import os
import numpy as np
import torch
from PIL import Image
import tempfile
import json
import sys
import unicodedata
import re
import uuid

# 多进程问题的优雅解决方案
def fix_multiprocessing_context():
    """修复多进程上下文问题"""
    try:
        import multiprocessing
        
        # 方法1: 设置启动方法为spawn（如果还没设置）
        try:
            if multiprocessing.get_start_method(allow_none=True) is None:
                multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # 如果已经设置过，忽略错误
            pass
        
        # 方法2: 修补set_start_method函数，避免重复设置错误
        original_set_start_method = multiprocessing.set_start_method
        def safe_set_start_method(*args, **kwargs):
            try:
                return original_set_start_method(*args, **kwargs)
            except RuntimeError as e:
                if "context has already been set" in str(e):
                    print("多进程上下文已设置，跳过重复设置")
                    return
                raise
        
        multiprocessing.set_start_method = safe_set_start_method
        
        return True
    except Exception as e:
        print(f"修复多进程上下文时出错: {e}")
        return False

def safe_import_blind_watermark():
    """安全导入blind_watermark库"""
    try:
        # 先修复多进程问题
        fix_multiprocessing_context()
        
        # 导入库
        from blind_watermark import WaterMark
        
        # 关闭版本提示
        try:
            import blind_watermark.bw_notes
            blind_watermark.bw_notes.close()
        except:
            pass
        
        # 测试创建实例
        test_bwm = WaterMark(password_img=1, password_wm=1)
        
        return WaterMark, True
        
    except Exception as e:
        print(f"导入 blind_watermark 失败: {e}")
        return None, False

# 全局变量，延迟初始化
_WATERMARK_CLASS = None
_WATERMARK_AVAILABLE = None

def get_watermark_class():
    """获取WaterMark类，使用延迟初始化"""
    global _WATERMARK_CLASS, _WATERMARK_AVAILABLE
    
    if _WATERMARK_AVAILABLE is None:
        _WATERMARK_CLASS, _WATERMARK_AVAILABLE = safe_import_blind_watermark()
        
        if _WATERMARK_AVAILABLE:
            print("✅ blind_watermark 库加载成功")
        else:
            print("❌ blind_watermark 库加载失败")
            print("请运行: pip install blind-watermark")
    
    return _WATERMARK_CLASS

def check_blind_watermark():
    """检查blind_watermark库是否可用"""
    global _WATERMARK_AVAILABLE
    
    if _WATERMARK_AVAILABLE is None:
        get_watermark_class()
    
    return _WATERMARK_AVAILABLE

class BlindWatermarkEmbed:
    """图片暗水印嵌入节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "watermark_text": ("STRING", {"default": "DaiMao Tools", "multiline": True}),
                "password_img": ("INT", {"default": 1, "min": 1, "max": 999999}),
                "password_wm": ("INT", {"default": 1, "min": 1, "max": 999999}),
            },
            "optional": {
                "watermark_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("嵌入水印的图片", "水印信息")
    FUNCTION = "embed_watermark"
    CATEGORY = "暗水印工具"
    DISPLAY_NAME = "图片暗水印嵌入"

    def embed_watermark(self, image, watermark_text, password_img, password_wm, watermark_image=None):
        if not check_blind_watermark():
            raise Exception("blind_watermark 库未安装或导入失败，请运行: pip install blind-watermark")
        
        try:
            # 获取WaterMark类
            WaterMark = get_watermark_class()
            if WaterMark is None:
                raise Exception("无法获取 WaterMark 类")
            
            # 保存输入图片到临时文件
            temp_input_path = self.save_temp_image(image)
            
            # 创建WaterMark实例
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)
            bwm.read_img(temp_input_path)
            
            # 判断水印类型并处理
            if watermark_image is not None:
                # 图片水印模式
                print("使用图片水印模式")
                temp_watermark_path = self.save_temp_image(watermark_image)
                print(f"水印图片已保存到: {temp_watermark_path}")
                
                # 读取图片水印（不需要mode参数）
                bwm.read_wm(temp_watermark_path)
                
                # 获取水印信息
                watermark_shape = bwm.wm_size
                watermark_type = "image"
                watermark_content = f"图片水印 {watermark_shape}"
                
                print(f"图片水印size: {watermark_shape}")
                
            else:
                # 文本水印模式
                print(f"使用文本水印模式: '{watermark_text}'")
                
                # 读取文本水印
                bwm.read_wm(watermark_text, mode='str')
                
                # 获取水印信息
                watermark_shape = len(bwm.wm_bit)
                watermark_type = "text"
                watermark_content = watermark_text
                
                print(f"文本水印bit长度: {watermark_shape}")
            
            # 嵌入水印
            output_path = temp_input_path.replace('.jpg', '_watermarked.jpg')
            bwm.embed(output_path)
            
            print(f"水印嵌入成功")
            
            # 读取输出图片
            output_image = self.load_image_as_tensor(output_path)
            
            # 创建水印信息
            watermark_info = {
                "type": watermark_type,
                "content": watermark_content,
                "shape_or_length": watermark_shape,
                "password_img": password_img,
                "password_wm": password_wm,
            }
            
            # 为文本水印添加额外信息
            if watermark_type == "text":
                watermark_info.update({
                    "text": watermark_text,
                    "length": watermark_shape,
                    "char_count": len(watermark_text),
                    "utf8_bytes": len(watermark_text.encode('utf-8'))
                })
            
            # 清理临时文件
            try:
                os.unlink(temp_input_path)
                os.unlink(output_path)
                if watermark_image is not None:
                    os.unlink(temp_watermark_path)
            except:
                pass
            
            return (output_image, watermark_info)
                
        except Exception as e:
            print(f"嵌入水印时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return (image, {})

    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图片"""
        if len(tensor.shape) == 4:
            tensor = tensor.squeeze(0)
        
        np_image = tensor.cpu().numpy()
        
        if np_image.max() <= 1.0:
            np_image = (np_image * 255).astype(np.uint8)
        else:
            np_image = np_image.astype(np.uint8)
        
        if len(np_image.shape) == 3:
            return Image.fromarray(np_image, 'RGB')
        else:
            return Image.fromarray(np_image, 'L')

    def pil_to_tensor(self, pil_image):
        """将PIL图片转换为tensor"""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        np_image = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_image).unsqueeze(0)
        
        return tensor

    def save_temp_image(self, image):
        """保存图片到临时文件"""
        pil_image = self.tensor_to_pil(image)
        
        # 使用更安全的临时文件创建方式
        temp_dir = tempfile.gettempdir()
        
        # 生成唯一文件名，使用.jpg格式（更兼容）
        temp_filename = f"watermark_temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # 确保是RGB模式（避免RGBA导致的问题）
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 保存为JPEG格式（更兼容OpenCV）
        pil_image.save(temp_path, 'JPEG', quality=95)
        
        print(f"临时图片已保存到: {temp_path}")
        return temp_path

    def load_image_as_tensor(self, image_path):
        """加载图片为tensor"""
        image = Image.open(image_path)
        return self.pil_to_tensor(image)

class BlindWatermarkExtractNode:
    """图片暗水印提取节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "password_img": ("INT", {"default": 1, "min": 1, "max": 999999}),
                "password_wm": ("INT", {"default": 1, "min": 1, "max": 999999}),
                "watermark_type": (["text", "image"], {"default": "text"}),
            },
            "optional": {
                "original_text": ("STRING", {"default": "", "multiline": True}),
                "watermark_length": ("INT", {"default": 64, "min": 1, "max": 10000}),
                "watermark_width": ("INT", {"default": 64, "min": 1, "max": 1000}),
                "watermark_height": ("INT", {"default": 64, "min": 1, "max": 1000}),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("提取的水印文本", "提取的水印图片")
    FUNCTION = "extract"
    CATEGORY = "暗水印工具"
    DISPLAY_NAME = "图片暗水印提取"

    def extract(self, image, password_img=1, password_wm=1, watermark_type="text", 
                original_text="", watermark_length=64, watermark_width=64, watermark_height=64):
        """提取水印"""
        if not check_blind_watermark():
            raise Exception("blind_watermark 库未安装或导入失败，请运行: pip install blind-watermark")
        
        try:
            # 获取WaterMark类
            WaterMark = get_watermark_class()
            if WaterMark is None:
                raise Exception("无法获取 WaterMark 类")
            
            # 保存图片到临时文件
            temp_path = self.save_temp_image(image)
            
            # 创建WaterMark实例
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)
            
            if watermark_type == "image":
                # 图片水印提取
                print(f"提取图片水印，尺寸: ({watermark_height}, {watermark_width})")
                
                # 使用shape提取图片水印
                wm_shape = (watermark_height, watermark_width)
                
                # 方法1: 尝试直接提取到内存
                try:
                    # 创建临时输出路径，确保有正确的扩展名
                    temp_dir = tempfile.gettempdir()
                    temp_output = os.path.join(temp_dir, f"extracted_wm_{uuid.uuid4().hex}.png")
                    
                    print(f"临时输出路径: {temp_output}")
                    
                    # 使用指定的输出路径进行提取
                    extracted_result = bwm.extract(temp_path, wm_shape=wm_shape, mode='img', out_wm_name=temp_output)
                    
                    print(f"图片水印提取结果类型: {type(extracted_result)}")
                    
                    # 检查是否生成了输出文件
                    if os.path.exists(temp_output):
                        print("从输出文件读取提取结果")
                        # 从文件读取
                        import cv2
                        extracted_img = cv2.imread(temp_output)
                        if extracted_img is not None:
                            # 转换BGR到RGB
                            extracted_img = cv2.cvtColor(extracted_img, cv2.COLOR_BGR2RGB)
                            extracted_result = extracted_img
                        
                        # 清理临时文件
                        try:
                            os.unlink(temp_output)
                        except:
                            pass
                    
                except Exception as e1:
                    print(f"方法1失败: {e1}")
                    
                    # 方法2: 尝试不指定输出文件名
                    try:
                        print("尝试方法2: 不指定输出文件名")
                        extracted_result = bwm.extract(temp_path, wm_shape=wm_shape, mode='img')
                        print(f"方法2成功，结果类型: {type(extracted_result)}")
                    except Exception as e2:
                        print(f"方法2也失败: {e2}")
                        
                        # 方法3: 使用文本模式作为备选
                        try:
                            print("尝试方法3: 使用文本模式提取")
                            text_result = bwm.extract(temp_path, wm_shape=watermark_height*watermark_width*3, mode='str')
                            print(f"文本模式提取结果: {len(text_result) if text_result else 0} 字符")
                            
                            # 创建一个占位符图片
                            extracted_result = np.random.randint(0, 255, (watermark_height, watermark_width, 3), dtype=np.uint8)
                            print("使用占位符图片")
                            
                        except Exception as e3:
                            print(f"所有方法都失败: {e3}")
                            extracted_result = None
                
                if isinstance(extracted_result, np.ndarray) and extracted_result is not None:
                    print(f"提取的图片shape: {extracted_result.shape}")
                    
                    # 将numpy数组转换为PIL图片，再转换为tensor
                    if len(extracted_result.shape) == 2:
                        # 灰度图
                        extracted_pil = Image.fromarray(extracted_result.astype(np.uint8), 'L')
                        # 转换为RGB
                        extracted_pil = extracted_pil.convert('RGB')
                    else:
                        # 彩色图
                        extracted_pil = Image.fromarray(extracted_result.astype(np.uint8), 'RGB')
                    
                    # 转换为tensor
                    extracted_tensor = self.pil_to_tensor(extracted_pil)
                    
                    # 清理临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
                    return ("", extracted_tensor)
                else:
                    print("图片水印提取失败")
                    # 返回空的图片tensor
                    empty_image = torch.zeros(1, watermark_height, watermark_width, 3)
                    return ("", empty_image)
                    
            else:
                # 文本水印提取
                # 计算实际使用的长度
                if original_text and original_text.strip():
                    actual_length = self.calculate_watermark_length(original_text)
                    print(f"根据原始文本 '{original_text}' 计算的bit长度: {actual_length}")
                else:
                    actual_length = watermark_length
                    print(f"使用手动输入的长度: {watermark_length}")
                
                print(f"开始提取文本水印，使用长度: {actual_length}")
                
                # 提取文本水印
                extracted_result = bwm.extract(temp_path, wm_shape=actual_length, mode='str')
                
                print(f"原始提取结果: {repr(extracted_result)}")
                
                # 清理提取结果
                cleaned_text = self.clean_extracted_text(extracted_result)
                
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                if cleaned_text:
                    print(f"文本水印提取成功: '{cleaned_text}'")
                    # 返回空的图片tensor
                    empty_image = torch.zeros(1, 64, 64, 3)
                    return (cleaned_text, empty_image)
                else:
                    print("文本水印提取失败或为空")
                    empty_image = torch.zeros(1, 64, 64, 3)
                    return ("", empty_image)
                
        except Exception as e:
            print(f"提取水印时发生错误: {e}")
            import traceback
            traceback.print_exc()
            empty_image = torch.zeros(1, 64, 64, 3)
            return ("", empty_image)

    def calculate_watermark_length(self, text):
        """根据文本内容计算水印的bit长度"""
        try:
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            utf8_bytes = len(text.encode('utf-8'))
            bit_length = utf8_bytes * 8
            
            print(f"文本分析: 原文本='{text}', 字符数={len(text)}, UTF-8字节数={utf8_bytes}, bit长度={bit_length}")
            
            return bit_length
            
        except Exception as e:
            print(f"计算水印长度时出错: {e}")
            return len(text) * 8

    def clean_extracted_text(self, text):
        """清理提取的文本，处理编码问题"""
        if not text:
            return ""
        
        try:
            # 确保文本是字符串格式
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # 移除控制字符，保留基本空白字符
            cleaned_chars = []
            for char in text:
                if (unicodedata.category(char)[0] not in ['C'] or 
                    char in [' ', '\t', '\n', '\r']):
                    cleaned_chars.append(char)
            
            cleaned_text = ''.join(cleaned_chars).strip()
            
            # 移除末尾的特殊字符
            while cleaned_text and cleaned_text[-1] in ['~', '\x00', '\xff']:
                cleaned_text = cleaned_text[:-1]
            
            return cleaned_text
            
        except Exception as e:
            print(f"清理文本时出错: {e}")
            return text.strip() if text else ""

    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图片"""
        if len(tensor.shape) == 4:
            tensor = tensor.squeeze(0)
        
        np_image = tensor.cpu().numpy()
        
        if np_image.max() <= 1.0:
            np_image = (np_image * 255).astype(np.uint8)
        else:
            np_image = np_image.astype(np.uint8)
        
        if len(np_image.shape) == 3:
            return Image.fromarray(np_image, 'RGB')
        else:
            return Image.fromarray(np_image, 'L')

    def pil_to_tensor(self, pil_image):
        """将PIL图片转换为tensor"""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        np_image = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_image).unsqueeze(0)
        
        return tensor

    def save_temp_image(self, image):
        """保存图片到临时文件"""
        pil_image = self.tensor_to_pil(image)
        
        # 使用更安全的临时文件创建方式
        temp_dir = tempfile.gettempdir()
        
        # 生成唯一文件名，使用.jpg格式（更兼容）
        temp_filename = f"watermark_temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # 确保是RGB模式（避免RGBA导致的问题）
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 保存为JPEG格式（更兼容OpenCV）
        pil_image.save(temp_path, 'JPEG', quality=95)
        
        print(f"临时图片已保存到: {temp_path}")
        return temp_path

# 为了兼容性，保留旧的类名
BlindWatermarkExtract = BlindWatermarkExtractNode

# 节点映射
NODE_CLASS_MAPPINGS = {
    "BlindWatermarkEmbed": BlindWatermarkEmbed,
    "BlindWatermarkExtract": BlindWatermarkExtractNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlindWatermarkEmbed": "图片暗水印嵌入",
    "BlindWatermarkExtract": "图片暗水印提取",
} 
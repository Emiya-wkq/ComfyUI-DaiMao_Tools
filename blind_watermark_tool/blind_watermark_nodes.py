# 移除文件开头的多进程处理，恢复简洁的导入
import os
import tempfile
import uuid
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import torch
import json
import sys
import unicodedata
import re

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
                "password": ("INT", {"default": 1, "min": 1, "max": 999999}),
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

    def embed_watermark(self, image, watermark_text, password, watermark_image=None):
        if not check_blind_watermark():
            raise Exception("blind_watermark 库未安装或导入失败，请运行: pip install blind-watermark")
        
        try:
            # 获取WaterMark类
            WaterMarkClass = get_watermark_class()
            if WaterMarkClass is None:
                raise Exception("无法获取 WaterMark 类")
            
            # 保存输入图片到临时文件
            temp_input_path = self.save_temp_image(image)
            
            # 创建WaterMark实例
            bwm = WaterMarkClass(password_img=password, password_wm=password)
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
                "password": password,
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
        # 直接定义支持的攻击类型
        attack_types = ["无攻击", "抗截图", "抗压缩", "抗格式转换"]
        
        return {
            "required": {
                "image": ("IMAGE",),
                "password": ("INT", {"default": 1, "min": 1, "max": 999999}),
                "watermark_type": (["text", "image"], {"default": "text"}),
                "attack_type": (attack_types, {"default": "无攻击"}),
            },
            "optional": {
                "original_text": ("STRING", {"default": "", "multiline": True}),
                "watermark_length": ("INT", {"default": 64, "min": 1, "max": 10000}),
                "watermark_width": ("INT", {"default": 64, "min": 1, "max": 1000}),
                "watermark_height": ("INT", {"default": 64, "min": 1, "max": 1000}),
                "original_image": ("IMAGE",),  # 新增：用于抗截图攻击的原始图片
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("提取的水印文本", "提取的水印图片")
    FUNCTION = "extract"
    CATEGORY = "暗水印工具"
    DISPLAY_NAME = "图片暗水印提取"

    def extract(self, image, password, watermark_type="text", attack_type="无攻击", 
                original_text="", watermark_length=64, watermark_width=64, watermark_height=64, original_image=None):
        """提取水印"""
        if not check_blind_watermark():
            raise Exception("blind_watermark 库未安装或导入失败，请运行: pip install blind-watermark")
        
        try:
            # 获取WaterMark类
            WaterMarkClass = get_watermark_class()
            if WaterMarkClass is None:
                raise Exception("无法获取 WaterMark 类")
            
            # 保存图片到临时文件
            temp_path = self.save_temp_image(image)
            
            # 根据攻击类型进行图片预处理
            processed_path = self.apply_attack_resistance(temp_path, attack_type, original_image)
            
            # 创建WaterMark实例
            bwm = WaterMarkClass(password_img=password, password_wm=password)
            
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
                    extracted_result = bwm.extract(processed_path, wm_shape=wm_shape, mode='img', out_wm_name=temp_output)
                    
                    print(f"图片水印提取结果类型: {type(extracted_result)}")
                    
                    # 检查是否生成了输出文件
                    if os.path.exists(temp_output):
                        print("从输出文件读取提取结果")
                        # 从文件读取
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
                        extracted_result = bwm.extract(processed_path, wm_shape=wm_shape, mode='img')
                        print(f"方法2成功，结果类型: {type(extracted_result)}")
                    except Exception as e2:
                        print(f"方法2也失败: {e2}")
                        
                        # 方法3: 使用文本模式作为备选
                        try:
                            print("尝试方法3: 使用文本模式提取")
                            text_result = bwm.extract(processed_path, wm_shape=watermark_height*watermark_width*3, mode='str')
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
                        os.unlink(processed_path)
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
                    # 使用与嵌入时一致的方法计算长度
                    temp_bwm = WaterMarkClass(password_img=password, password_wm=password)
                    temp_bwm.read_wm(original_text, mode='str')
                    actual_length = len(temp_bwm.wm_bit)
                    print(f"根据原始文本 '{original_text}' 使用嵌入算法计算的bit长度: {actual_length}")
                else:
                    actual_length = watermark_length
                    print(f"使用手动输入的长度: {watermark_length}")
                
                print(f"开始提取文本水印，使用长度: {actual_length}")
                
                # 提取文本水印
                extracted_result = bwm.extract(processed_path, wm_shape=actual_length, mode='str')
                
                print(f"原始提取结果: {repr(extracted_result)}")
                
                # 清理提取结果
                cleaned_text = self.clean_extracted_text(extracted_result)
                
                # 清理临时文件
                try:
                    os.unlink(processed_path)
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

    def apply_attack_resistance(self, image_path, attack_type, original_image=None):
        """根据攻击类型对图片进行预处理"""
        if attack_type == "无攻击":
            return image_path
        
        try:
            print(f"应用抗攻击处理: {attack_type}")
            
            if attack_type == "抗截图":
                return self._process_anti_screenshot(image_path, original_image)
            elif attack_type == "抗压缩":
                return self._process_anti_compression(image_path)
            elif attack_type == "抗格式转换":
                return self._process_anti_format_conversion(image_path)
            else:
                print(f"未知的攻击类型: {attack_type}")
                return image_path
                
        except Exception as e:
            print(f"抗攻击处理失败: {e}")
            return image_path
    
    def _process_anti_screenshot(self, image_path, original_image=None):
        """处理抗截图攻击 - 使用blind_watermark库的恢复方法"""
        try:
            from blind_watermark.recover import recover_crop, estimate_crop_parameters
            
            # 生成恢复后的图片路径
            temp_dir = tempfile.gettempdir()
            recovered_path = os.path.join(temp_dir, f"recovered_screenshot_{uuid.uuid4().hex}.png")
            
            if original_image is not None:
                # 方法1：有原始图片，使用estimate_crop_parameters精确估计
                print("检测到原始图片，使用精确参数估计...")
                
                try:
                    # 保存原始图片到临时文件
                    original_path = self.save_temp_image(original_image)
                    
                    # 使用estimate_crop_parameters估计攻击参数
                    print("正在估计截图攻击参数...")
                    (x1, y1, x2, y2), image_o_shape, score, scale_infer = estimate_crop_parameters(
                        original_file=original_path,
                        template_file=image_path,
                        scale=(0.3, 3.0),  # 扩大搜索范围
                        search_num=300     # 增加搜索次数提高精度
                    )
                    
                    print(f"估计的攻击参数: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                    print(f"估计的缩放比例: {scale_infer}, 匹配得分: {score}")
                    
                    # 应用恢复处理
                    recover_crop(template_file=image_path, 
                               output_file_name=recovered_path,
                               loc=(x1, y1, x2, y2), 
                               image_o_shape=image_o_shape)
                    
                    # 清理原始图片临时文件
                    try:
                        os.unlink(original_path)
                    except:
                        pass
                    
                    if os.path.exists(recovered_path):
                        print(f"基于原始图片的截图攻击恢复成功: {recovered_path}")
                        return recovered_path
                    else:
                        print("精确恢复失败，尝试多参数方法...")
                        
                except Exception as e:
                    print(f"精确参数估计失败: {e}")
                    print("回退到多参数尝试方法...")
            
            # 方法2：没有原始图片或精确估计失败，使用多参数尝试
            print("使用多参数尝试策略...")
            
            img = Image.open(image_path)
            w, h = img.size
            
            # 定义多组常见的截图攻击参数
            attack_params = [
                # 格式: (x1_ratio, y1_ratio, x2_ratio, y2_ratio, description)
                (0.0, 0.0, 1.0, 1.0, "无裁剪"),
                (0.05, 0.05, 0.95, 0.95, "轻微边缘裁剪"),
                (0.1, 0.1, 0.9, 0.9, "中等边缘裁剪"),
                (0.15, 0.15, 0.85, 0.85, "较大边缘裁剪"),
                (0.02, 0.02, 0.98, 0.98, "微小边缘裁剪"),
                (0.08, 0.08, 0.92, 0.92, "常见截图裁剪"),
                (0.0, 0.05, 1.0, 0.95, "上下边缘裁剪"),
                (0.05, 0.0, 0.95, 1.0, "左右边缘裁剪"),
                (0.03, 0.08, 0.97, 0.92, "不对称裁剪1"),
                (0.08, 0.03, 0.92, 0.97, "不对称裁剪2"),
            ]
            
            best_recovered_path = None
            best_score = -1
            
            for i, (x1_ratio, y1_ratio, x2_ratio, y2_ratio, desc) in enumerate(attack_params):
                try:
                    # 计算实际坐标
                    x1 = int(w * x1_ratio)
                    y1 = int(h * y1_ratio)
                    x2 = int(w * x2_ratio)
                    y2 = int(h * y2_ratio)
                    
                    print(f"尝试参数 {i+1}/{len(attack_params)}: {desc}")
                    print(f"  坐标: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                    
                    # 生成当前尝试的恢复路径
                    current_recovered_path = os.path.join(temp_dir, f"recovered_try_{i}_{uuid.uuid4().hex}.png")
                    
                    # 应用恢复处理
                    recover_crop(template_file=image_path, 
                               output_file_name=current_recovered_path,
                               loc=(x1, y1, x2, y2), 
                               image_o_shape=(h, w))
                    
                    if os.path.exists(current_recovered_path):
                        # 简单的质量评估：检查恢复后图片的尺寸和内容
                        recovered_img = Image.open(current_recovered_path)
                        
                        # 计算简单的质量分数（基于尺寸匹配度）
                        size_score = min(recovered_img.width / w, recovered_img.height / h)
                        
                        print(f"  恢复成功，质量分数: {size_score:.3f}")
                        
                        if size_score > best_score:
                            best_score = size_score
                            if best_recovered_path and os.path.exists(best_recovered_path):
                                try:
                                    os.unlink(best_recovered_path)
                                except:
                                    pass
                            best_recovered_path = current_recovered_path
                        else:
                            # 删除质量较差的恢复结果
                            try:
                                os.unlink(current_recovered_path)
                            except:
                                pass
                    else:
                        print(f"  恢复失败")
                        
                except Exception as e:
                    print(f"  参数尝试失败: {e}")
                    continue
            
            if best_recovered_path and os.path.exists(best_recovered_path):
                # 将最佳结果移动到最终路径
                if best_recovered_path != recovered_path:
                    try:
                        os.rename(best_recovered_path, recovered_path)
                    except:
                        # 如果重命名失败，复制文件
                        import shutil
                        shutil.copy2(best_recovered_path, recovered_path)
                        os.unlink(best_recovered_path)
                
                print(f"多参数尝试完成，最佳恢复结果: {recovered_path} (分数: {best_score:.3f})")
                return recovered_path
            else:
                print("所有参数尝试都失败，使用原图")
                return image_path
                
        except ImportError:
            print("无法导入blind_watermark.recover模块，使用原图")
            return image_path
        except Exception as e:
            print(f"截图攻击处理失败: {e}")
            import traceback
            traceback.print_exc()
            return image_path
    
    def _process_anti_compression(self, image_path):
        """处理抗压缩攻击"""
        try:
            # 对于压缩攻击，主要是质量损失，可以通过图像增强来部分恢复
            img = Image.open(image_path)
            
            # 轻微的锐化处理
            img = img.filter(ImageFilter.SHARPEN)
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # 保存处理后的图片
            temp_dir = tempfile.gettempdir()
            processed_path = os.path.join(temp_dir, f"anti_compression_{uuid.uuid4().hex}.jpg")
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(processed_path, 'JPEG', quality=95)
            
            print(f"抗压缩处理完成: {processed_path}")
            return processed_path
            
        except Exception as e:
            print(f"抗压缩处理失败: {e}")
            return image_path
    
    def _process_anti_format_conversion(self, image_path):
        """处理抗格式转换攻击"""
        try:
            # 对于格式转换攻击，主要是色彩空间和编码的变化
            img = Image.open(image_path)
            
            # 确保RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 色彩增强
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)
            
            # 保存处理后的图片
            temp_dir = tempfile.gettempdir()
            processed_path = os.path.join(temp_dir, f"anti_format_{uuid.uuid4().hex}.png")
            
            img.save(processed_path, 'PNG')
            
            print(f"抗格式转换处理完成: {processed_path}")
            return processed_path
            
        except Exception as e:
            print(f"抗格式转换处理失败: {e}")
            return image_path

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
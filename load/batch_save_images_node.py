import os
import torch
import numpy as np
from PIL import Image
import json
import re

class BatchSaveImagesNode:
    """批量储存图片节点，支持重命名功能"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"description": "要保存的图片列表"}),
                "output_directory": ("STRING", {"default": "./output", "multiline": False, "description": "输出目录路径"}),
                "file_names": ("STRING", {"default": "[]", "multiline": True, "description": "文件名称列表（JSON格式）"}),
                "file_extension": (["png", "jpg", "jpeg", "bmp", "tiff"], {"default": "png", "description": "输出文件格式"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "description": "JPEG质量（仅对jpg/jpeg有效）"}),
                "overwrite": ("BOOLEAN", {"default": False, "description": "是否覆盖已存在的文件"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("保存结果", "保存的文件列表")
    FUNCTION = "save_images"
    CATEGORY = "呆毛工具"
    DISPLAY_NAME = "批量储存图片"

    def save_images(self, images, output_directory, file_names, file_extension="png", quality=95, overwrite=False):
        """
        批量保存图片，支持重命名
        
        Args:
            images: 图片tensor列表
            output_directory: 输出目录路径
            file_names: 文件名称列表（JSON格式）
            file_extension: 输出文件格式
            quality: JPEG质量
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            tuple: (保存结果, 保存的文件列表)
        """
        try:
            # 检查输出目录
            if not output_directory or not output_directory.strip():
                return ("错误：输出目录路径为空", "[]")
            
            output_directory = output_directory.strip()
            
            # 创建输出目录（如果不存在）
            try:
                os.makedirs(output_directory, exist_ok=True)
                print(f"输出目录: {output_directory}")
            except Exception as e:
                return (f"创建输出目录失败: {e}", "[]")
            
            # 解析文件名称列表
            try:
                if file_names and file_names.strip():
                    names_list = json.loads(file_names)
                    if not isinstance(names_list, list):
                        names_list = []
                else:
                    names_list = []
            except json.JSONDecodeError as e:
                print(f"解析文件名称列表失败: {e}")
                names_list = []
            
            # 检查图片数量
            if len(images) == 0:
                return ("错误：没有图片需要保存", "[]")
            
            print(f"开始保存 {len(images)} 张图片到目录: {output_directory}")
            print(f"文件格式: {file_extension}")
            print(f"文件名称列表: {len(names_list)} 个名称")
            
            # 保存图片
            saved_files = []
            failed_files = []
            
            for i, image in enumerate(images):
                try:
                    # 生成文件名
                    if i < len(names_list) and names_list[i]:
                        # 使用提供的名称
                        filename = str(names_list[i])
                    else:
                        # 使用默认名称
                        filename = f"image_{i:04d}"
                    
                    # 清理文件名（移除非法字符）
                    filename = self.clean_filename(filename)
                    
                    # 添加文件扩展名
                    output_filename = f"{filename}.{file_extension}"
                    output_path = os.path.join(output_directory, output_filename)
                    
                    # 检查文件是否已存在
                    if os.path.exists(output_path) and not overwrite:
                        # 生成唯一文件名
                        base_name = filename
                        counter = 1
                        while os.path.exists(output_path):
                            output_filename = f"{base_name}_{counter:03d}.{file_extension}"
                            output_path = os.path.join(output_directory, output_filename)
                            counter += 1
                    
                    # 保存图片
                    success = self.save_single_image(image, output_path, file_extension, quality)
                    
                    if success:
                        saved_files.append(output_filename)
                        print(f"成功保存: {output_filename}")
                    else:
                        failed_files.append(f"图片_{i}")
                        
                except Exception as e:
                    print(f"保存图片 {i} 失败: {e}")
                    failed_files.append(f"图片_{i}")
            
            # 生成结果信息
            result_info = self.generate_save_result(output_directory, len(saved_files), len(failed_files), file_extension)
            saved_files_json = json.dumps(saved_files, ensure_ascii=False, indent=2)
            
            print(f"保存完成: 成功 {len(saved_files)} 张，失败 {len(failed_files)} 张")
            
            return (result_info, saved_files_json)
            
        except Exception as e:
            print(f"批量保存图片时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return (f"保存失败: {str(e)}", "[]")
    
    def clean_filename(self, filename):
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除或替换非法字符
        # Windows: < > : " | ? * \ /
        # Unix: / (根目录分隔符)
        illegal_chars = r'[<>:"|?*\\/]'
        cleaned = re.sub(illegal_chars, '_', filename)
        
        # 移除前后空格和点
        cleaned = cleaned.strip(' .')
        
        # 如果文件名为空，使用默认名称
        if not cleaned:
            cleaned = "unnamed"
        
        return cleaned
    
    def save_single_image(self, image_tensor, output_path, file_extension, quality):
        """
        保存单张图片
        
        Args:
            image_tensor: 图片tensor
            output_path: 输出路径
            file_extension: 文件格式
            quality: JPEG质量
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保tensor格式正确
            if len(image_tensor.shape) == 4:
                image_tensor = image_tensor.squeeze(0)
            
            # 转换为numpy数组
            np_image = image_tensor.cpu().numpy()
            
            # 检查图片通道数
            channels = np_image.shape[2] if len(np_image.shape) == 3 else 1
            
            # 确保像素值在0-1范围内
            if np_image.max() <= 1.0:
                np_image = (np_image * 255).astype(np.uint8)
            else:
                np_image = np_image.astype(np.uint8)
            
            # 根据通道数和格式选择合适的模式
            if channels == 4:
                # RGBA图片，保持透明通道
                if file_extension.lower() in ['jpg', 'jpeg']:
                    # JPEG不支持透明通道，需要转换为RGB
                    print(f"警告：JPEG格式不支持透明通道，图片 {os.path.basename(output_path)} 将丢失透明信息")
                    pil_image = Image.fromarray(np_image, 'RGBA')
                    # 创建白色背景
                    background = Image.new('RGB', pil_image.size, (255, 255, 255))
                    # 将RGBA图片合成到白色背景上
                    background.paste(pil_image, mask=pil_image.split()[-1])  # 使用alpha通道作为mask
                    pil_image = background
                else:
                    # PNG等格式支持透明通道
                    pil_image = Image.fromarray(np_image, 'RGBA')
            elif channels == 3:
                # RGB图片
                pil_image = Image.fromarray(np_image, 'RGB')
            elif channels == 1:
                # 灰度图片
                pil_image = Image.fromarray(np_image, 'L')
            else:
                # 其他情况，尝试自动处理
                pil_image = Image.fromarray(np_image)
            
            # 根据格式保存
            if file_extension.lower() in ['jpg', 'jpeg']:
                # 确保JPEG图片是RGB模式
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                pil_image.save(output_path, 'JPEG', quality=quality)
            else:
                # 其他格式保持原有模式
                pil_image.save(output_path, file_extension.upper())
            
            return True
            
        except Exception as e:
            print(f"保存单张图片失败 {output_path}: {e}")
            return False
    
    def generate_save_result(self, output_directory, success_count, failed_count, file_extension):
        """生成保存结果信息"""
        info = f"保存完成\n"
        info += f"输出目录: {output_directory}\n"
        info += f"文件格式: {file_extension}\n"
        info += f"成功保存: {success_count} 张\n"
        
        if failed_count > 0:
            info += f"保存失败: {failed_count} 张\n"
        
        info += f"总计处理: {success_count + failed_count} 张"
        
        return info 
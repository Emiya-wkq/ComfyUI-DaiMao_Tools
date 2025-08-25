import os
import torch
import numpy as np
from PIL import Image
import glob

class BatchLoadImagesNode:
    """批量加载图片节点，读取指定目录下的全部图片并按原尺寸输出"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": "", "multiline": False, "description": "要读取的图片目录路径"}),
                "file_extensions": ("STRING", {"default": "jpg,jpeg,png,bmp,tiff", "multiline": False, "description": "支持的图片文件扩展名，用逗号分隔"}),
                "recursive": ("BOOLEAN", {"default": False, "description": "是否递归搜索子目录"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("图片列表", "文件信息", "文件名称列表")
    FUNCTION = "load_images"
    CATEGORY = "呆毛工具"
    DISPLAY_NAME = "批量加载图片"

    def load_images(self, directory_path, file_extensions="jpg,jpeg,png,bmp,tiff", recursive=False):
        """
        读取指定目录下的全部图片
        
        Args:
            directory_path: 要读取的图片目录路径
            file_extensions: 支持的图片文件扩展名，用逗号分隔
            recursive: 是否递归搜索子目录
            
        Returns:
            tuple: (images_tensor, file_info) - 图片tensor列表和文件信息
        """
        try:
            # 检查目录路径是否为空
            if not directory_path or not directory_path.strip():
                print("目录路径为空")
                return (torch.zeros(0, 100, 100, 3), "目录路径为空")
            
            # 去除路径前后的空白字符
            directory_path = directory_path.strip()
            
            # 检查目录是否存在
            if not os.path.isdir(directory_path):
                print(f"目录不存在: {directory_path}")
                return (torch.zeros(0, 100, 100, 3), f"目录不存在: {directory_path}")
            
            print(f"正在搜索目录: {directory_path}")
            print(f"目录绝对路径: {os.path.abspath(directory_path)}")
            
            # 解析文件扩展名
            extensions = [ext.strip().lower() for ext in file_extensions.split(',') if ext.strip()]
            if not extensions:
                extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
            
            print(f"支持的图片格式: {extensions}")
            
            # 构建搜索模式
            search_patterns = []
            for ext in extensions:
                if ext.startswith('.'):
                    search_patterns.append(f"**/*{ext}")
                else:
                    search_patterns.append(f"**/*.{ext}")
            
            # 搜索图片文件
            image_files = []
            for ext in extensions:
                if recursive:
                    # 递归搜索
                    search_path = os.path.join(directory_path, f"**/*.{ext}")
                    files = glob.glob(search_path, recursive=True)
                    print(f"递归搜索 {ext}: {search_path} -> 找到 {len(files)} 个文件")
                else:
                    # 仅搜索当前目录
                    search_path = os.path.join(directory_path, f"*.{ext}")
                    files = glob.glob(search_path)
                    print(f"当前目录搜索 {ext}: {search_path} -> 找到 {len(files)} 个文件")
                
                image_files.extend(files)
            
            # 去重并排序
            image_files = sorted(list(set(image_files)), key=self.natural_sort_key)
            print(f"去重后总文件数: {len(image_files)}")
            
            # 显示排序后的文件列表（前10个）
            print("排序后的文件列表:")
            for i, file_path in enumerate(image_files[:10]):
                print(f"  {i+1:2d}. {os.path.basename(file_path)}")
            if len(image_files) > 10:
                print(f"  ... 还有 {len(image_files) - 10} 个文件")
            
            if not image_files:
                print(f"在目录 {directory_path} 中未找到支持的图片文件")
                # 列出目录中的所有文件，帮助调试
                try:
                    all_files = os.listdir(directory_path)
                    print(f"目录中的所有文件: {all_files[:20]}")  # 只显示前20个
                    if len(all_files) > 20:
                        print(f"... 还有 {len(all_files) - 20} 个文件")
                except Exception as e:
                    print(f"无法列出目录内容: {e}")
                return (torch.zeros(0, 100, 100, 3), f"未找到支持的图片文件，支持的格式: {', '.join(extensions)}")
            
            print(f"找到 {len(image_files)} 个图片文件")
            
            # 加载所有图片
            images = []
            loaded_count = 0
            failed_files = []
            max_width = 0
            max_height = 0
            image_info_list = []  # 存储图片信息和尺寸
            
            # 第一遍：加载所有图片并计算最大尺寸
            print("第一遍：加载图片并计算最大尺寸...")
            for file_path in image_files:
                try:
                    # 检查文件是否为图片
                    if not self.is_image_file(file_path, extensions):
                        continue
                    
                    # 加载图片
                    image = self.load_single_image(file_path)
                    if image is not None:
                        # 记录图片信息
                        img_height, img_width = image.shape[1], image.shape[2]
                        img_channels = image.shape[3] if len(image.shape) == 4 else 1
                        image_info = {
                            'tensor': image,
                            'path': file_path,
                            'original_size': (img_height, img_width),
                            'channels': img_channels
                        }
                        image_info_list.append(image_info)
                        
                        # 更新最大尺寸
                        max_height = max(max_height, img_height)
                        max_width = max(max_width, img_width)
                        
                        channel_info = f"({img_channels}通道)" if img_channels != 3 else ""
                        print(f"加载图片: {os.path.basename(file_path)} - 尺寸: {img_width}x{img_height} {channel_info}")
                    else:
                        failed_files.append(file_path)
                        
                except Exception as e:
                    print(f"加载图片失败 {file_path}: {e}")
                    failed_files.append(file_path)
            
            if not image_info_list:
                print("没有成功加载任何图片")
                return (torch.zeros(0, 100, 100, 3), "没有成功加载任何图片")
            
            print(f"计算得到最大尺寸: {max_width}x{max_height}")
            
            # 第二遍：创建统一尺寸的背景图片并居中放置
            print("第二遍：创建统一尺寸的背景图片...")
            for img_info in image_info_list:
                try:
                    # 创建背景图片
                    background = self.create_centered_image(img_info['tensor'], max_width, max_height)
                    if background is not None:
                        images.append(background)
                        loaded_count += 1
                        print(f"成功处理: {os.path.basename(img_info['path'])} - 从 {img_info['original_size'][1]}x{img_info['original_size'][0]} 调整到 {max_width}x{max_height}")
                    else:
                        failed_files.append(img_info['path'])
                        
                except Exception as e:
                    print(f"处理图片失败 {img_info['path']}: {e}")
                    failed_files.append(img_info['path'])
            
            if not images:
                print("没有成功处理任何图片")
                return (torch.zeros(0, 100, 100, 3), "没有成功处理任何图片")
            
            # 将所有图片合并为一个tensor
            try:
                images_tensor = torch.cat(images, dim=0)
                print(f"成功合并 {len(images)} 张图片，总尺寸: {images_tensor.shape}")
            except Exception as e:
                print(f"合并图片tensor失败: {e}")
                # 如果合并失败，返回第一张图片
                print("返回第一张图片作为备选方案")
                images_tensor = images[0]
            
            # 生成文件信息
            file_info = self.generate_file_info(directory_path, loaded_count, len(image_files), failed_files, extensions, (max_height, max_width))
            
            # 生成文件名称列表（JSON格式，便于后续节点使用）
            file_names = self.generate_file_names_list(image_info_list)
            
            return (images_tensor, file_info, file_names)
            
        except Exception as e:
            print(f"批量加载图片时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return (torch.zeros(0, 100, 100, 3), f"加载失败: {str(e)}")
    
    def is_image_file(self, file_path, extensions):
        """检查文件是否为支持的图片格式"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext.startswith('.'):
                file_ext = file_ext[1:]
            
            # 检查扩展名是否在支持列表中
            is_supported = file_ext in extensions
            
            # 调试信息
            if not is_supported:
                print(f"文件 {os.path.basename(file_path)} 扩展名 {file_ext} 不在支持列表中: {extensions}")
            
            return is_supported
        except Exception as e:
            print(f"检查文件扩展名时出错 {file_path}: {e}")
            return False
    
    def load_single_image(self, image_path):
        """
        加载单张图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            tensor: 图片tensor，格式为 (1, H, W, C)，如果加载失败返回None
        """
        try:
            # 使用PIL加载图片
            image = Image.open(image_path)
            
            # 检查图片模式并处理
            if image.mode == 'RGBA':
                # 保持RGBA模式，支持透明通道
                print(f"检测到RGBA图片: {os.path.basename(image_path)}")
            elif image.mode == 'LA':
                # 灰度+透明通道，转换为RGBA
                image = image.convert('RGBA')
                print(f"转换LA图片为RGBA: {os.path.basename(image_path)}")
            elif image.mode == 'P':
                # 调色板模式，转换为RGBA以保持透明信息
                image = image.convert('RGBA')
                print(f"转换P图片为RGBA: {os.path.basename(image_path)}")
            elif image.mode != 'RGB':
                # 其他模式转换为RGB
                image = image.convert('RGB')
            
            # 转换为numpy数组
            np_image = np.array(image).astype(np.float32) / 255.0
            
            # 转换为tensor并添加batch维度
            tensor = torch.from_numpy(np_image).unsqueeze(0)
            
            return tensor
            
        except Exception as e:
            print(f"加载单张图片失败 {image_path}: {e}")
            return None
    
    def natural_sort_key(self, file_path):
        """
        自然排序键函数，实现正确的数字排序
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: 排序键，支持数字和文本混合排序
        """
        import re
        
        # 提取文件名（不含路径）
        filename = os.path.basename(file_path)
        
        # 使用正则表达式分割文件名，将数字和文本分开
        # 例如: "image_10.jpg" -> ["image_", "10", ".jpg"]
        parts = re.split(r'(\d+)', filename)
        
        # 转换排序键
        sort_key = []
        for part in parts:
            if part.isdigit():
                # 数字部分转换为整数，确保正确的数字排序
                sort_key.append(int(part))
            else:
                # 文本部分保持原样，用于字母排序
                sort_key.append(part.lower())  # 忽略大小写
        
        return sort_key
    
    def create_centered_image(self, image_tensor, target_width, target_height):
        """
        创建一个统一尺寸的背景图片，并将输入图片居中放置
        
        Args:
            image_tensor: 输入图片tensor，格式为 (1, H, W, C)
            target_width: 目标宽度
            target_height: 目标高度
            
        Returns:
            tensor: 居中后的图片tensor，如果失败返回None
        """
        try:
            # 确保输入tensor是 (1, H, W, C) 格式
            if len(image_tensor.shape) == 4:
                image_tensor = image_tensor.squeeze(0)
            
            # 获取输入图片的尺寸和通道数
            input_height, input_width = image_tensor.shape[0], image_tensor.shape[1]
            channels = image_tensor.shape[2] if len(image_tensor.shape) == 3 else 1
            
            # 根据通道数创建背景
            if channels == 4:
                # RGBA图片，创建透明背景
                background = np.zeros((target_height, target_width, 4), dtype=np.float32)
                # 设置透明通道为0（完全透明）
                background[:, :, 3] = 0.0
            elif channels == 3:
                # RGB图片，创建黑色背景
                background = np.zeros((target_height, target_width, 3), dtype=np.float32)
            elif channels == 1:
                # 灰度图片，创建黑色背景
                background = np.zeros((target_height, target_width, 1), dtype=np.float32)
            else:
                # 其他情况，创建默认背景
                background = np.zeros((target_height, target_width, channels), dtype=np.float32)
            
            # 计算居中位置
            x_offset = (target_width - input_width) // 2
            y_offset = (target_height - input_height) // 2
            
            # 将输入图片复制到背景图片的居中位置
            background[y_offset:y_offset + input_height, x_offset:x_offset + input_width, :] = image_tensor.cpu().numpy()
            
            # 转换回tensor
            centered_tensor = torch.from_numpy(background).unsqueeze(0)
            
            return centered_tensor
            
        except Exception as e:
            print(f"创建居中图片失败: {e}")
            return None
    
    def generate_file_info(self, directory_path, loaded_count, total_found, failed_files, extensions, target_size):
        """生成文件信息字符串"""
        info = f"目录: {directory_path}\n"
        info += f"支持的格式: {', '.join(extensions)}\n"
        info += f"找到文件数: {total_found}\n"
        info += f"成功加载: {loaded_count}\n"
        
        if failed_files:
            info += f"加载失败: {len(failed_files)}\n"
            info += "失败文件:\n"
            for failed_file in failed_files[:10]:  # 只显示前10个失败文件
                info += f"  - {os.path.basename(failed_file)}\n"
            if len(failed_files) > 10:
                info += f"  ... 还有 {len(failed_files) - 10} 个文件加载失败\n"
        
        if target_size:
            info += f"目标尺寸: {target_size[0]}x{target_size[1]}\n"
        
        return info 
    
    def generate_file_names_list(self, image_info_list):
        """
        生成文件名称列表（JSON格式）
        
        Args:
            image_info_list: 图片信息列表
            
        Returns:
            str: JSON格式的文件名称列表
        """
        import json
        
        try:
            # 提取文件名称（不含路径和扩展名）
            file_names = []
            for img_info in image_info_list:
                # 获取文件名（不含扩展名）
                filename = os.path.splitext(os.path.basename(img_info['path']))[0]
                file_names.append(filename)
            
            # 返回JSON格式的字符串
            return json.dumps(file_names, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"生成文件名称列表失败: {e}")
            return "[]" 
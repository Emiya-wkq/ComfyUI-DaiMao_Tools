import os
import torch
import numpy as np
from PIL import Image

class FileExistsNode:
    """文件存在检查节点，判断指定路径的文件是否存在，并输出对应的图片"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "", "multiline": False, "description": "要检查的图片文件路径"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "IMAGE")
    RETURN_NAMES = ("文件存在", "图片")
    FUNCTION = "check_file_exists"
    CATEGORY = "呆毛工具"
    DISPLAY_NAME = "文件存在检查"

    def check_file_exists(self, file_path):
        """
        检查指定路径的文件是否存在，并返回对应的图片
        
        Args:
            file_path: 要检查的文件路径（字符串）
            
        Returns:
            tuple: (bool, tensor) - 文件存在状态和对应的图片tensor
        """
        try:
            # 检查文件路径是否为空
            if not file_path or not file_path.strip():
                return (False, self.create_black_image())
            
            # 去除路径前后的空白字符
            file_path = file_path.strip()
            
            # 检查文件是否存在
            exists = os.path.isfile(file_path)
            
            if exists:
                # 文件存在，加载图片
                try:
                    image = self.load_image(file_path)
                    return (True, image)
                except Exception as e:
                    print(f"加载图片失败: {e}")
                    return (False, self.create_black_image())
            else:
                # 文件不存在，返回黑色图片
                return (False, self.create_black_image())
            
        except Exception as e:
            print(f"文件存在检查出错: {e}")
            # 出错时返回False和黑色图片
            return (False, self.create_black_image())
    
    def load_image(self, image_path):
        """
        加载图片为tensor格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            tensor: 图片tensor，格式为 (1, H, W, 3)
        """
        # 使用PIL加载图片
        image = Image.open(image_path)
        
        # 确保是RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 转换为numpy数组
        np_image = np.array(image).astype(np.float32) / 255.0
        
        # 转换为tensor并添加batch维度
        tensor = torch.from_numpy(np_image).unsqueeze(0)
        
        return tensor
    
    def create_black_image(self, width=100, height=100):
        """
        创建黑色图片
        
        Args:
            width: 图片宽度
            height: 图片高度
            
        Returns:
            tensor: 黑色图片tensor，格式为 (1, H, W, 3)
        """
        # 创建100x100的黑色图片
        black_array = np.zeros((height, width, 3), dtype=np.float32)
        tensor = torch.from_numpy(black_array).unsqueeze(0)
        return tensor 
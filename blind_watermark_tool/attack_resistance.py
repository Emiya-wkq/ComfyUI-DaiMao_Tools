#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抗攻击处理模块
用于处理各种图片攻击的预处理策略
"""

import os
import tempfile
import uuid
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2


class AttackResistanceProcessor:
    """抗攻击处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.supported_attacks = ["无攻击", "抗截图", "抗压缩", "抗格式转换"]
    
    def get_supported_attacks(self):
        """获取支持的攻击类型列表"""
        return self.supported_attacks.copy()
    
    def process_image(self, image_path, attack_type):
        """
        根据攻击类型对图片进行预处理
        
        Args:
            image_path (str): 输入图片路径
            attack_type (str): 攻击类型
            
        Returns:
            str: 处理后的图片路径
        """
        if attack_type not in self.supported_attacks:
            raise ValueError(f"不支持的攻击类型: {attack_type}，支持的类型: {self.supported_attacks}")
        
        if attack_type == "无攻击":
            return image_path
        
        print(f"应用抗攻击策略: {attack_type}")
        
        # 加载图片
        img = Image.open(image_path)
        
        # 根据攻击类型选择处理方法
        if attack_type == "抗截图":
            img = self._process_anti_screenshot(img)
        elif attack_type == "抗压缩":
            img = self._process_anti_compression(img)
        elif attack_type == "抗格式转换":
            img = self._process_anti_format_conversion(img)
        
        # 保存处理后的图片
        processed_path = self._save_processed_image(img, attack_type)
        print(f"抗攻击处理完成，保存到: {processed_path}")
        
        return processed_path
    
    def _process_anti_screenshot(self, img):
        """
        抗截图攻击处理
        
        策略：增强对比度和锐化，补偿截图时的质量损失
        """
        print("应用抗截图处理：增强对比度和锐化")
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # 增强20%对比度
        
        # 锐化处理
        img = img.filter(ImageFilter.SHARPEN)
        
        # 轻微的高斯模糊去噪
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return img
    
    def _process_anti_compression(self, img):
        """
        抗压缩攻击处理
        
        策略：去噪和边缘增强，补偿压缩造成的细节损失
        """
        print("应用抗压缩处理：去噪和边缘增强")
        
        # 转换为numpy数组进行OpenCV处理
        img_array = np.array(img)
        
        # 双边滤波去噪（保持边缘）
        img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
        
        # 增强边缘
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img_array = cv2.filter2D(img_array, -1, kernel)
        
        # 转换回PIL
        img = Image.fromarray(img_array)
        
        # 增强亮度
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        
        return img
    
    def _process_anti_format_conversion(self, img):
        """
        抗格式转换攻击处理
        
        策略：标准化和色彩校正，补偿格式转换的色彩损失
        """
        print("应用抗格式转换处理：标准化和色彩校正")
        
        # 确保RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 色彩平衡
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)  # 轻微增强饱和度
        
        # 伽马校正
        img_array = np.array(img).astype(np.float32) / 255.0
        img_array = np.power(img_array, 0.9)  # 轻微的伽马校正
        img_array = (img_array * 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        
        # 轻微锐化
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        return img
    
    def _save_processed_image(self, img, attack_type):
        """
        保存处理后的图片
        
        Args:
            img (PIL.Image): 处理后的图片
            attack_type (str): 攻击类型
            
        Returns:
            str: 保存的文件路径
        """
        # 生成临时文件路径
        temp_dir = tempfile.gettempdir()
        safe_attack_type = attack_type.replace("抗", "anti_").replace("无攻击", "no_attack")
        processed_filename = f"processed_{safe_attack_type}_{uuid.uuid4().hex}.jpg"
        processed_path = os.path.join(temp_dir, processed_filename)
        
        # 确保是RGB模式并保存
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(processed_path, 'JPEG', quality=95)
        
        return processed_path
    
    def add_custom_attack_processor(self, attack_name, processor_func):
        """
        添加自定义攻击处理器
        
        Args:
            attack_name (str): 攻击类型名称
            processor_func (callable): 处理函数，接受PIL.Image参数，返回处理后的PIL.Image
        """
        if attack_name not in self.supported_attacks:
            self.supported_attacks.append(attack_name)
        
        # 动态添加处理方法
        method_name = f"_process_{attack_name.lower().replace('抗', 'anti_')}"
        setattr(self, method_name, lambda img: processor_func(img))
        
        print(f"已添加自定义攻击处理器: {attack_name}")


# 全局处理器实例
_attack_processor = None

def get_attack_processor():
    """获取全局攻击处理器实例"""
    global _attack_processor
    if _attack_processor is None:
        _attack_processor = AttackResistanceProcessor()
    return _attack_processor

def process_attack_resistance(image_path, attack_type):
    """
    便捷函数：处理抗攻击
    
    Args:
        image_path (str): 图片路径
        attack_type (str): 攻击类型
        
    Returns:
        str: 处理后的图片路径
    """
    processor = get_attack_processor()
    return processor.process_image(image_path, attack_type)

def get_supported_attack_types():
    """
    便捷函数：获取支持的攻击类型
    
    Returns:
        list: 支持的攻击类型列表
    """
    processor = get_attack_processor()
    return processor.get_supported_attacks()


# 示例：如何添加自定义攻击处理器
def example_add_custom_processor():
    """示例：添加自定义攻击处理器"""
    
    def anti_noise_processor(img):
        """自定义抗噪声处理器"""
        # 中值滤波去噪
        img_array = np.array(img)
        img_array = cv2.medianBlur(img_array, 3)
        return Image.fromarray(img_array)
    
    # 添加到处理器
    processor = get_attack_processor()
    processor.add_custom_attack_processor("抗噪声", anti_noise_processor)


if __name__ == "__main__":
    # 测试代码
    print("支持的攻击类型:", get_supported_attack_types())
    
    # 示例：添加自定义处理器
    example_add_custom_processor()
    print("添加自定义处理器后:", get_supported_attack_types()) 
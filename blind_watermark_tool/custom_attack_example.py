#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义抗攻击处理器示例
展示如何扩展抗攻击功能
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2
from attack_resistance import get_attack_processor


def add_anti_noise_processor():
    """添加抗噪声攻击处理器"""
    
    def anti_noise_processor(img):
        """
        抗噪声攻击处理
        
        策略：使用多种去噪技术组合
        """
        print("应用抗噪声处理：多重去噪")
        
        # 转换为numpy数组
        img_array = np.array(img)
        
        # 1. 中值滤波去椒盐噪声
        img_array = cv2.medianBlur(img_array, 3)
        
        # 2. 高斯滤波去高斯噪声
        img_array = cv2.GaussianBlur(img_array, (3, 3), 0.5)
        
        # 3. 双边滤波保持边缘
        img_array = cv2.bilateralFilter(img_array, 5, 50, 50)
        
        # 转换回PIL
        img = Image.fromarray(img_array)
        
        # 4. 轻微锐化恢复细节
        img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=2))
        
        return img
    
    # 添加到处理器
    processor = get_attack_processor()
    processor.add_custom_attack_processor("抗噪声", anti_noise_processor)
    print("✅ 已添加抗噪声处理器")


def add_anti_rotation_processor():
    """添加抗旋转攻击处理器"""
    
    def anti_rotation_processor(img):
        """
        抗旋转攻击处理
        
        策略：尝试检测和校正轻微旋转
        """
        print("应用抗旋转处理：旋转校正")
        
        # 转换为numpy数组
        img_array = np.array(img)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # 使用霍夫变换检测直线
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None and len(lines) > 0:
            # 计算主要角度
            angles = []
            for rho, theta in lines[:10]:  # 只考虑前10条线
                angle = theta * 180 / np.pi
                if angle > 90:
                    angle = angle - 180
                angles.append(angle)
            
            # 取中位数作为旋转角度
            if angles:
                rotation_angle = np.median(angles)
                
                # 如果角度较小，进行校正
                if abs(rotation_angle) < 5:  # 只校正小角度旋转
                    print(f"检测到旋转角度: {rotation_angle:.2f}°，进行校正")
                    
                    # 获取图片中心
                    h, w = img_array.shape[:2]
                    center = (w // 2, h // 2)
                    
                    # 创建旋转矩阵
                    M = cv2.getRotationMatrix2D(center, -rotation_angle, 1.0)
                    
                    # 应用旋转
                    img_array = cv2.warpAffine(img_array, M, (w, h), 
                                             flags=cv2.INTER_CUBIC,
                                             borderMode=cv2.BORDER_REFLECT)
        
        # 转换回PIL
        img = Image.fromarray(img_array)
        
        return img
    
    # 添加到处理器
    processor = get_attack_processor()
    processor.add_custom_attack_processor("抗旋转", anti_rotation_processor)
    print("✅ 已添加抗旋转处理器")


def add_anti_scaling_processor():
    """添加抗缩放攻击处理器"""
    
    def anti_scaling_processor(img):
        """
        抗缩放攻击处理
        
        策略：标准化图片尺寸和增强细节
        """
        print("应用抗缩放处理：尺寸标准化和细节增强")
        
        # 获取原始尺寸
        original_size = img.size
        
        # 如果图片太小，先放大
        if min(original_size) < 256:
            scale_factor = 256 / min(original_size)
            new_size = (int(original_size[0] * scale_factor), 
                       int(original_size[1] * scale_factor))
            img = img.resize(new_size, Image.LANCZOS)
            print(f"图片放大: {original_size} -> {new_size}")
        
        # 增强细节
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        return img
    
    # 添加到处理器
    processor = get_attack_processor()
    processor.add_custom_attack_processor("抗缩放", anti_scaling_processor)
    print("✅ 已添加抗缩放处理器")


def demo_custom_processors():
    """演示自定义处理器的使用"""
    print("=== 自定义抗攻击处理器演示 ===")
    
    # 添加自定义处理器
    add_anti_noise_processor()
    add_anti_rotation_processor()
    add_anti_scaling_processor()
    
    # 显示所有支持的攻击类型
    from attack_resistance import get_supported_attack_types
    print(f"\n当前支持的攻击类型: {get_supported_attack_types()}")
    
    print("\n现在您可以在水印提取节点中使用这些新的攻击类型！")


if __name__ == "__main__":
    demo_custom_processors() 
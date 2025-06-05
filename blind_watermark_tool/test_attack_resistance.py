#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试抗攻击水印功能
"""

import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import tempfile
import uuid

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blind_watermark_nodes import BlindWatermarkEmbed, BlindWatermarkExtractNode
from attack_resistance import get_supported_attack_types, get_attack_processor

def create_test_image(width=512, height=512):
    """创建测试图片"""
    # 创建一个彩色测试图片
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # 添加一些结构化内容
    img_array[100:150, 100:400] = [255, 0, 0]  # 红色矩形
    img_array[200:250, 150:350] = [0, 255, 0]  # 绿色矩形
    img_array[300:350, 200:300] = [0, 0, 255]  # 蓝色矩形
    
    # 转换为tensor格式 (1, H, W, 3)
    tensor = torch.from_numpy(img_array).float() / 255.0
    tensor = tensor.unsqueeze(0)  # 添加batch维度
    
    return tensor

def simulate_screenshot_attack(image_path):
    """模拟截图攻击"""
    img = Image.open(image_path)
    
    # 模拟截图的质量损失
    # 1. 轻微模糊
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    
    # 2. 对比度变化
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.9)
    
    # 3. 亮度变化
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)
    
    # 4. 添加轻微噪声
    img_array = np.array(img)
    noise = np.random.normal(0, 3, img_array.shape).astype(np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    # 保存攻击后的图片
    temp_dir = tempfile.gettempdir()
    attacked_filename = f"screenshot_attacked_{uuid.uuid4().hex}.jpg"
    attacked_path = os.path.join(temp_dir, attacked_filename)
    img.save(attacked_path, 'JPEG', quality=85)
    
    return attacked_path

def simulate_compression_attack(image_path):
    """模拟压缩攻击"""
    img = Image.open(image_path)
    
    # 保存为低质量JPEG
    temp_dir = tempfile.gettempdir()
    attacked_filename = f"compression_attacked_{uuid.uuid4().hex}.jpg"
    attacked_path = os.path.join(temp_dir, attacked_filename)
    img.save(attacked_path, 'JPEG', quality=50)  # 低质量压缩
    
    return attacked_path

def simulate_format_conversion_attack(image_path):
    """模拟格式转换攻击"""
    img = Image.open(image_path)
    
    # PNG -> BMP -> JPEG 多次格式转换
    temp_dir = tempfile.gettempdir()
    
    # 第一次转换：PNG
    png_path = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}.png")
    img.save(png_path, 'PNG')
    
    # 第二次转换：BMP
    img = Image.open(png_path)
    bmp_path = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}.bmp")
    img.save(bmp_path, 'BMP')
    
    # 最终转换：JPEG
    img = Image.open(bmp_path)
    attacked_filename = f"format_attacked_{uuid.uuid4().hex}.jpg"
    attacked_path = os.path.join(temp_dir, attacked_filename)
    img.save(attacked_path, 'JPEG', quality=90)
    
    # 清理临时文件
    try:
        os.remove(png_path)
        os.remove(bmp_path)
    except:
        pass
    
    return attacked_path

def test_attack_resistance():
    """测试抗攻击功能"""
    print("=== 测试抗攻击水印功能 ===")
    
    try:
        # 创建节点实例
        embed_node = BlindWatermarkEmbed()
        extract_node = BlindWatermarkExtractNode()
        
        # 创建测试图片
        print("1. 创建测试图片...")
        test_image = create_test_image()
        
        # 嵌入文本水印
        print("2. 嵌入文本水印...")
        watermark_text = "测试抗攻击水印"
        password = "test123"
        
        watermarked_image, watermark_info = embed_node.embed_watermark(
            test_image, watermark_text, None, password
        )
        
        print(f"水印信息: {watermark_info}")
        
        # 保存水印图片到临时文件
        temp_dir = tempfile.gettempdir()
        watermarked_filename = f"watermarked_{uuid.uuid4().hex}.jpg"
        watermarked_path = os.path.join(temp_dir, watermarked_filename)
        
        # 转换tensor为PIL并保存
        img_array = (watermarked_image.squeeze(0).numpy() * 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        img.save(watermarked_path, 'JPEG', quality=95)
        
        print(f"水印图片保存到: {watermarked_path}")
        
        # 测试不同攻击类型
        attack_types = [
            ("无攻击", watermarked_path),
            ("抗截图", simulate_screenshot_attack(watermarked_path)),
            ("抗压缩", simulate_compression_attack(watermarked_path)),
            ("抗格式转换", simulate_format_conversion_attack(watermarked_path))
        ]
        
        for attack_name, attacked_path in attack_types:
            print(f"\n3. 测试 {attack_name}...")
            print(f"攻击后图片路径: {attacked_path}")
            
            try:
                # 加载攻击后的图片
                attacked_img = Image.open(attacked_path)
                attacked_tensor = torch.from_numpy(np.array(attacked_img)).float() / 255.0
                attacked_tensor = attacked_tensor.unsqueeze(0)
                
                # 提取水印
                extracted_text, extracted_image = extract_node.extract(
                    attacked_tensor, 
                    password, 
                    attack_name,  # 使用对应的攻击类型
                    watermark_text,  # 提供原始文本用于长度计算
                    "text",
                    None, None
                )
                
                print(f"提取结果: {extracted_text}")
                
                # 验证结果
                if extracted_text and watermark_text in extracted_text:
                    print(f"✓ {attack_name} 测试成功！")
                else:
                    print(f"✗ {attack_name} 测试失败，提取结果不匹配")
                    
            except Exception as e:
                print(f"✗ {attack_name} 测试出错: {str(e)}")
            
            # 清理攻击后的临时文件
            try:
                if attacked_path != watermarked_path:
                    os.remove(attacked_path)
            except:
                pass
        
        # 清理水印图片
        try:
            os.remove(watermarked_path)
        except:
            pass
            
        print("\n=== 抗攻击测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import torch
    test_attack_resistance() 
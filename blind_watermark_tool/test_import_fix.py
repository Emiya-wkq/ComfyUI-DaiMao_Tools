#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入修复
"""

import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试导入是否正常"""
    print("=== 测试导入修复 ===")
    
    try:
        print("1. 测试导入 blind_watermark_nodes...")
        from blind_watermark_nodes import BlindWatermarkEmbed, BlindWatermarkExtractNode
        print("✅ 导入成功")
        
        print("\n2. 测试创建节点实例...")
        embed_node = BlindWatermarkEmbed()
        extract_node = BlindWatermarkExtractNode()
        print("✅ 节点实例创建成功")
        
        print("\n3. 测试获取INPUT_TYPES...")
        embed_input_types = BlindWatermarkEmbed.INPUT_TYPES()
        extract_input_types = BlindWatermarkExtractNode.INPUT_TYPES()
        print("✅ INPUT_TYPES获取成功")
        
        print(f"\n嵌入节点输入类型: {list(embed_input_types['required'].keys())}")
        print(f"提取节点输入类型: {list(extract_input_types['required'].keys())}")
        
        print("\n4. 测试抗攻击模块...")
        from attack_resistance import get_supported_attack_types
        attack_types = get_supported_attack_types()
        print(f"✅ 支持的攻击类型: {attack_types}")
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import()
    if success:
        print("\n🎉 导入修复成功！现在可以正常使用水印工具了。")
    else:
        print("\n💥 导入仍有问题，需要进一步调试。") 
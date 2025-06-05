#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化抗攻击功能
"""

import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_attack_resistance_module():
    """测试抗攻击模块"""
    print("=== 测试抗攻击模块 ===")
    
    try:
        # 导入模块
        from attack_resistance import (
            get_supported_attack_types, 
            get_attack_processor,
            process_attack_resistance
        )
        
        # 测试获取支持的攻击类型
        print("1. 测试获取支持的攻击类型...")
        attack_types = get_supported_attack_types()
        print(f"支持的攻击类型: {attack_types}")
        
        # 测试获取处理器实例
        print("\n2. 测试获取处理器实例...")
        processor = get_attack_processor()
        print(f"处理器类型: {type(processor)}")
        print(f"处理器支持的攻击类型: {processor.get_supported_attacks()}")
        
        # 测试添加自定义处理器
        print("\n3. 测试添加自定义处理器...")
        
        def test_custom_processor(img):
            """测试用的自定义处理器"""
            print("执行自定义处理...")
            return img
        
        processor.add_custom_attack_processor("测试攻击", test_custom_processor)
        print(f"添加后的攻击类型: {processor.get_supported_attacks()}")
        
        print("\n✅ 抗攻击模块测试成功！")
        
    except Exception as e:
        print(f"❌ 抗攻击模块测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_custom_processors():
    """测试自定义处理器示例"""
    print("\n=== 测试自定义处理器示例 ===")
    
    try:
        # 导入自定义处理器示例
        from custom_attack_example import demo_custom_processors
        
        # 运行演示
        demo_custom_processors()
        
        print("\n✅ 自定义处理器示例测试成功！")
        
    except Exception as e:
        print(f"❌ 自定义处理器示例测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_node_integration():
    """测试节点集成"""
    print("\n=== 测试节点集成 ===")
    
    try:
        # 导入节点
        from blind_watermark_nodes import BlindWatermarkExtractNode
        
        # 测试INPUT_TYPES是否正确获取攻击类型
        print("1. 测试提取节点的INPUT_TYPES...")
        input_types = BlindWatermarkExtractNode.INPUT_TYPES()
        attack_types = input_types["required"]["attack_type"][0]
        print(f"节点支持的攻击类型: {attack_types}")
        
        # 创建节点实例
        print("\n2. 测试创建节点实例...")
        extract_node = BlindWatermarkExtractNode()
        print(f"节点类型: {type(extract_node)}")
        
        print("\n✅ 节点集成测试成功！")
        
    except Exception as e:
        print(f"❌ 节点集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试模块化抗攻击功能...\n")
    
    # 运行所有测试
    test_attack_resistance_module()
    test_custom_processors()
    test_node_integration()
    
    print("\n=== 所有测试完成 ===")
    print("\n使用说明:")
    print("1. 抗攻击逻辑已提取到 attack_resistance.py 模块中")
    print("2. 可以通过 custom_attack_example.py 查看如何添加自定义处理器")
    print("3. 主节点文件 blind_watermark_nodes.py 现在使用模块化的抗攻击功能")
    print("4. 要添加新的攻击类型，只需修改 attack_resistance.py 或创建自定义处理器") 
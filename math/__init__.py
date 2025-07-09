# -*- coding: utf-8 -*-
"""
数学工具节点注册
"""

from .number_padding_node import NumberPaddingNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "NumberPaddingNode": NumberPaddingNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "NumberPaddingNode": "数字补零",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
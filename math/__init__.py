# -*- coding: utf-8 -*-
"""
数学工具节点注册
"""

from .number_padding_node import NumberPaddingNode
from .file_exists_node import FileExistsNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "NumberPaddingNode": NumberPaddingNode,
    "FileExistsNode": FileExistsNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "NumberPaddingNode": "数字补零",
    "FileExistsNode": "文件存在检查",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
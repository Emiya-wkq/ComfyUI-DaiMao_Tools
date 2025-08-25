# -*- coding: utf-8 -*-
"""
图片加载工具节点注册
"""

from .batch_load_images_node import BatchLoadImagesNode
from .batch_save_images_node import BatchSaveImagesNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "BatchLoadImagesNode": BatchLoadImagesNode,
    "BatchSaveImagesNode": BatchSaveImagesNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchLoadImagesNode": "批量加载图片",
    "BatchSaveImagesNode": "批量储存图片",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
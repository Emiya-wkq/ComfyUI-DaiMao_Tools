# -*- coding: utf-8 -*-
"""
Mask节点注册
"""

from .seam_mask import SeamMask
from .grid_mask import GridMask
from .bounding_box_mask import BoundingBoxMask

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "SeamMask": SeamMask,
    "GridMask": GridMask,
    "BoundingBoxMask": BoundingBoxMask,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "SeamMask": "接缝区域遮罩",
    "GridMask": "网格化遮罩", 
    "BoundingBoxMask": "最小矩形包裹",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
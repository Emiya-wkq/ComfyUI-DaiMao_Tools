import torch
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, generate_binary_structure

class SeamMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "width": ("INT", {
                    "default": 50,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display_name": "接缝宽度"
                }),
                "offset": ("INT", {
                    "default": 0,
                    "min": -50,
                    "max": 50,
                    "step": 1,
                    "display_name": "偏移量"
                }),
            }
        }

    RETURN_TYPES = ("MASK", "MASK")
    FUNCTION = "process"
    CATEGORY = "custom_nodes"
    DISPLAY_NAME = "接缝区域遮罩"

    def process(self, mask, width, offset):
        # 确保mask是二值化的
        mask = (mask > 0.5).float()
        
        # 确保mask是二维的
        if mask.dim() > 2:
            mask = mask.squeeze(0)  # 假设mask是在第一个维度上多余的

        # 生成结构元素
        structure = generate_binary_structure(2, 1)
        
        # 计算基本的扩展和收缩次数（宽度的一半）
        half_width = width // 2
        
        # 处理偏移量，确保其在合理范围内
        max_offset = half_width
        min_offset = -half_width
        offset = max(min(offset, max_offset), min_offset)
        
        # 计算外部扩展和内部收缩的迭代次数
        if offset > 0:
            # 偏移量为正，外部多扩展，内部少收缩
            outer_iterations = half_width + offset
            inner_iterations = half_width
        elif offset < 0:
            # 偏移量为负，内部多收缩，外部少扩展
            outer_iterations = half_width
            inner_iterations = half_width + abs(offset)
        else:
            # 偏移量为0，内外扩展相同
            outer_iterations = half_width
            inner_iterations = half_width

        # 扩展遮罩
        outer_dilated_mask = binary_dilation(mask.numpy(), structure=structure, iterations=outer_iterations)
        # 收缩遮罩
        inner_eroded_mask = binary_erosion(mask.numpy(), structure=structure, iterations=inner_iterations)

        # 计算扩展区域（外部扩展减去内部收缩）
        expanded_region = torch.from_numpy(outer_dilated_mask).float().to(mask.device) - torch.from_numpy(inner_eroded_mask).float().to(mask.device)
        
        # 返回接缝遮罩和原始遮罩，交换位置并更改名称
        return (expanded_region, mask)
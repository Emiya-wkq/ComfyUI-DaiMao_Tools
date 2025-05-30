import torch
import numpy as np

class GridMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "rows": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display_name": "行数"
                }),
                "cols": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display_name": "列数"
                }),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "process"
    CATEGORY = "custom_nodes"
    DISPLAY_NAME = "网格化遮罩"

    def process(self, mask, rows, cols):
        # 获取遮罩尺寸
        height, width = mask.shape[-2], mask.shape[-1]
        
        # 创建网格模式
        grid = np.indices((height, width))
        grid = (grid[0] // (height // rows) + grid[1] // (width // cols)) % 2
        grid_mask = torch.from_numpy(grid).float().to(mask.device)
        
        # 应用网格到原始遮罩
        final_mask = mask * grid_mask
        
        return (final_mask,) 
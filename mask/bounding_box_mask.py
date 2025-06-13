import torch
import numpy as np
import cv2

class BoundingBoxMask:
    """最小矩形包裹遮罩节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "padding": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display_name": "边界填充"
                }),
                "min_area": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 10000,
                    "step": 1,
                    "display_name": "最小区域面积"
                }),
            }
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("包裹矩形遮罩",)
    FUNCTION = "process"
    CATEGORY = "custom_nodes"
    DISPLAY_NAME = "最小矩形包裹"

    def process(self, mask, padding=0, min_area=100):
        """
        将遮罩部分进行最小矩形包裹
        
        Args:
            mask: 输入遮罩（单个或batch）
            padding: 边界填充像素数
            min_area: 最小区域面积，小于此面积的区域将被忽略
            
        Returns:
            包裹矩形遮罩（单个或batch）
        """
        # 首先检查输入是否为列表
        if isinstance(mask, list):
            # 处理mask列表
            results = []
            for i, single_mask in enumerate(mask):
                print(f"处理第 {i+1}/{len(mask)} 个遮罩...")
                result = self._process_single_mask(single_mask, padding, min_area)
                results.append(result)
            # 将结果合并为batch tensor
            batch_result = torch.stack(results, dim=0)
            return (batch_result,)
        # 然后检查输入是否为batch（多个mask）
        elif hasattr(mask, 'dim') and mask.dim() == 3 and mask.shape[0] > 1:
            # 处理batch中的多个mask
            batch_size = mask.shape[0]
            results = []
            for i in range(batch_size):
                print(f"处理第 {i+1}/{batch_size} 个遮罩...")
                single_mask = mask[i:i+1]  # 保持维度
                result = self._process_single_mask(single_mask, padding, min_area)
                results.append(result)
            # 将结果合并为batch tensor
            batch_result = torch.stack(results, dim=0)
            return (batch_result,)
        else:
            # 处理单个mask
            result = self._process_single_mask(mask, padding, min_area)
            return (result,)  # 单个结果包装在元组中
    
    def _process_single_mask(self, mask, padding=0, min_area=100):
        """
        处理单个遮罩
        
        Args:
            mask: 单个输入遮罩
            padding: 边界填充像素数
            min_area: 最小区域面积
            
        Returns:
            包裹矩形遮罩
        """
        # 确保mask是二值化的 - 白色区域（值>0.5）为前景
        binary_mask = (mask > 0.5).float()
        
        # 处理不同的维度情况
        if binary_mask.dim() == 3:
            # 如果是 (1, H, W) 格式，去掉第一个维度
            if binary_mask.shape[0] == 1:
                binary_mask = binary_mask.squeeze(0)
            else:
                # 如果是 (H, W, C) 格式，取第一个通道
                binary_mask = binary_mask[:, :, 0]
        elif binary_mask.dim() > 3:
            # 如果是更高维度，取第一个
            binary_mask = binary_mask.squeeze(0)
        
        # 确保是二维的
        if binary_mask.dim() != 2:
            print(f"警告：mask维度异常 {binary_mask.shape}，尝试修复...")
            binary_mask = binary_mask.squeeze()
        
        # 转换为numpy数组用于OpenCV处理
        mask_np = binary_mask.cpu().numpy().astype(np.uint8)
        
        # 确保是单通道图像
        if len(mask_np.shape) > 2:
            # 如果是多通道，取第一个通道或转换为灰度
            if mask_np.shape[2] == 3:
                # 如果是RGB，转换为灰度
                mask_np = cv2.cvtColor(mask_np, cv2.COLOR_RGB2GRAY)
            else:
                # 取第一个通道
                mask_np = mask_np[:, :, 0]
        
        # 确保是二值图像 - 白色区域为255，黑色区域为0
        mask_np = (mask_np > 0).astype(np.uint8) * 255
        
        print(f"处理mask形状: {mask_np.shape}, 值范围: [{mask_np.min()}, {mask_np.max()}]")
        
        # 查找轮廓 - 查找白色区域（前景）
        contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 创建输出遮罩
        output_mask = torch.zeros_like(binary_mask)
        
        if len(contours) > 0:
            # 过滤小区域
            valid_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= min_area:
                    valid_contours.append(contour)
            
            if len(valid_contours) > 0:
                # 合并所有有效轮廓
                combined_contour = np.vstack(valid_contours)
                
                # 计算最小外接矩形
                rect = cv2.minAreaRect(combined_contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                
                # 应用填充
                if padding > 0:
                    # 扩展矩形边界
                    height, width = mask_np.shape
                    box[:, 0] = np.clip(box[:, 0] + padding, 0, width - 1)
                    box[:, 1] = np.clip(box[:, 1] + padding, 0, height - 1)
                
                # 创建矩形遮罩 - 填充矩形区域为白色
                rect_mask = np.zeros_like(mask_np)
                cv2.fillPoly(rect_mask, [box], 255)
                
                # 转换为tensor - 确保输出是浮点数格式
                output_mask = torch.from_numpy(rect_mask).float().to(mask.device) / 255.0
                
                print(f"找到 {len(valid_contours)} 个有效区域，最小矩形尺寸: {rect[1]}")
                print(f"矩形坐标: {box}")
            else:
                print(f"没有找到面积大于 {min_area} 的有效区域")
        else:
            print("未找到任何轮廓")
        
        return output_mask 
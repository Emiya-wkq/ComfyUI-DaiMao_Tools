import os

class NumberPaddingNode:
    """数字补零节点，将整数补零到指定位数"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number": ("INT", {"default": 1, "min": 0, "max": 999999999}),
                "padding_digits": ("INT", {"default": 5, "min": 1, "max": 20, "description": "补零到几位数"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("补零结果",)
    FUNCTION = "pad_number"
    CATEGORY = "呆毛工具"
    DISPLAY_NAME = "数字补零"

    def pad_number(self, number, padding_digits):
        """
        将数字补零到指定位数
        
        Args:
            number: 输入的数字
            padding_digits: 补零到几位数
            
        Returns:
            str: 补零后的字符串
        """
        try:
            # 将数字转换为字符串并补零
            result = str(number).zfill(padding_digits)
            return (result,)
        except Exception as e:
            print(f"数字补零出错: {e}")
            # 出错时返回原数字的字符串形式
            return (str(number),) 
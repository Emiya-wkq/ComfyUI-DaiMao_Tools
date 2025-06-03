from .blind_watermark_nodes import BlindWatermarkEmbed, BlindWatermarkExtract

NODE_CLASS_MAPPINGS = {
    "BlindWatermarkEmbed": BlindWatermarkEmbed,
    "BlindWatermarkExtract": BlindWatermarkExtract,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlindWatermarkEmbed": "呆毛图片数字水印嵌入",
    "BlindWatermarkExtract": "呆毛图片数字水印提取",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
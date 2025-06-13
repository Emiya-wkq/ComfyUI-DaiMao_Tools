from .daimao_file_finder import NODE_CLASS_MAPPINGS as FINDER_NODE_MAPPINGS
from .daimao_file_finder import NODE_DISPLAY_NAME_MAPPINGS as FINDER_DISPLAY_MAPPINGS
from .daimao_file_deduplicator import NODE_CLASS_MAPPINGS as DEDUPLICATOR_NODE_MAPPINGS
from .daimao_file_deduplicator import NODE_DISPLAY_NAME_MAPPINGS as DEDUPLICATOR_DISPLAY_MAPPINGS
from .daimao_file_dedup import NODE_CLASS_MAPPINGS as DEDUP_NODE_MAPPINGS
from .daimao_file_dedup import NODE_DISPLAY_NAME_MAPPINGS as DEDUP_DISPLAY_MAPPINGS
from .daimao_file_deduplicator_with_symlink import DaiMaoFileDeduplicatorWithSymlink
from .anime_name_helper.anime_name_helper_node import AnimeNameHelper
from .blind_watermark_tool import NODE_CLASS_MAPPINGS as WATERMARK_NODE_MAPPINGS
from .blind_watermark_tool import NODE_DISPLAY_NAME_MAPPINGS as WATERMARK_DISPLAY_MAPPINGS
from .mask import NODE_CLASS_MAPPINGS as MASK_NODE_MAPPINGS
from .mask import NODE_DISPLAY_NAME_MAPPINGS as MASK_DISPLAY_MAPPINGS

# 合并节点映射
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(FINDER_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DEDUPLICATOR_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DEDUP_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(WATERMARK_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(MASK_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update({
    "anime_name_helper": AnimeNameHelper,
    "呆毛文件去重器(带符号链接)": DaiMaoFileDeduplicatorWithSymlink,
})

# 合并显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(FINDER_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DEDUPLICATOR_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DEDUP_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(WATERMARK_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(MASK_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update({
    "anime_name_helper": "呆毛动漫人物名称辅助器",
    "呆毛文件去重器(带符号链接)": "呆毛文件去重器(带符号链接)",
})

# 添加便于搜索的别名
NODE_CLASS_MAPPINGS.update({
    "DaiMaoFileDedup": NODE_CLASS_MAPPINGS["呆毛文件去重"],
    "FileDeduplication": NODE_CLASS_MAPPINGS["呆毛文件去重"],
    "DedupFiles": NODE_CLASS_MAPPINGS["呆毛文件去重"],
    "文件去重": NODE_CLASS_MAPPINGS["呆毛文件去重"],
    "文件查重": NODE_CLASS_MAPPINGS["呆毛文件查重"],
    
    "DaiMaoFileFinder": NODE_CLASS_MAPPINGS["呆毛文件查重"],
    "FileDuplicatesFinder": NODE_CLASS_MAPPINGS["呆毛文件查重"],
    "FindDuplicates": NODE_CLASS_MAPPINGS["呆毛文件查重"],
    "查找重复文件": NODE_CLASS_MAPPINGS["呆毛文件查重"],
    
    "DaiMaoDeduplicator": NODE_CLASS_MAPPINGS["呆毛文件去重器"],
    "FileDeduplicator": NODE_CLASS_MAPPINGS["呆毛文件去重器"],
    "RemoveDuplicates": NODE_CLASS_MAPPINGS["呆毛文件去重器"],
    "删除重复文件": NODE_CLASS_MAPPINGS["呆毛文件去重器"],
    
    "DaiMaoDeduplicatorWithSymlink": NODE_CLASS_MAPPINGS["呆毛文件去重器(带符号链接)"],
    "FileDeduplicatorWithSymlink": NODE_CLASS_MAPPINGS["呆毛文件去重器(带符号链接)"],
    "RemoveDuplicatesWithSymlink": NODE_CLASS_MAPPINGS["呆毛文件去重器(带符号链接)"],
    "删除重复文件(带符号链接)": NODE_CLASS_MAPPINGS["呆毛文件去重器(带符号链接)"],
    
    # Mask节点别名
    "BoundingBox": NODE_CLASS_MAPPINGS["BoundingBoxMask"],
    "MinRectMask": NODE_CLASS_MAPPINGS["BoundingBoxMask"],
    "最小矩形": NODE_CLASS_MAPPINGS["BoundingBoxMask"],
    "Seam": NODE_CLASS_MAPPINGS["SeamMask"],
    "接缝遮罩": NODE_CLASS_MAPPINGS["SeamMask"],
    "Grid": NODE_CLASS_MAPPINGS["GridMask"],
    "网格遮罩": NODE_CLASS_MAPPINGS["GridMask"],
})

# 同步更新显示名称
for key in NODE_CLASS_MAPPINGS:
    if key not in NODE_DISPLAY_NAME_MAPPINGS:
        if key in ["DaiMaoFileFinder", "FileDuplicatesFinder", "FindDuplicates", "查找重复文件", "文件查重"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件查重"
        elif key in ["DaiMaoDeduplicator", "FileDeduplicator", "RemoveDuplicates", "删除重复文件"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件去重器"
        elif key in ["DaiMaoDeduplicatorWithSymlink", "FileDeduplicatorWithSymlink", "RemoveDuplicatesWithSymlink", "删除重复文件(带符号链接)"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件去重器(带符号链接)"
        elif key in ["BoundingBox", "MinRectMask", "最小矩形"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "最小矩形包裹"
        elif key in ["Seam", "接缝遮罩"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "接缝区域遮罩"
        elif key in ["Grid", "网格遮罩"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "网格化遮罩"
        else:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件去重"

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
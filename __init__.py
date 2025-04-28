from .daimao_file_finder import NODE_CLASS_MAPPINGS as FINDER_NODE_MAPPINGS
from .daimao_file_finder import NODE_DISPLAY_NAME_MAPPINGS as FINDER_DISPLAY_MAPPINGS
from .daimao_file_deduplicator import NODE_CLASS_MAPPINGS as DEDUPLICATOR_NODE_MAPPINGS
from .daimao_file_deduplicator import NODE_DISPLAY_NAME_MAPPINGS as DEDUPLICATOR_DISPLAY_MAPPINGS
from .daimao_file_dedup import NODE_CLASS_MAPPINGS as DEDUP_NODE_MAPPINGS
from .daimao_file_dedup import NODE_DISPLAY_NAME_MAPPINGS as DEDUP_DISPLAY_MAPPINGS

# 合并节点映射
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(FINDER_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DEDUPLICATOR_NODE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DEDUP_NODE_MAPPINGS)

# 合并显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(FINDER_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DEDUPLICATOR_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DEDUP_DISPLAY_MAPPINGS)

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
})

# 同步更新显示名称
for key in NODE_CLASS_MAPPINGS:
    if key not in NODE_DISPLAY_NAME_MAPPINGS:
        if key in ["DaiMaoFileFinder", "FileDuplicatesFinder", "FindDuplicates", "查找重复文件", "文件查重"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件查重"
        elif key in ["DaiMaoDeduplicator", "FileDeduplicator", "RemoveDuplicates", "删除重复文件"]:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件去重器"
        else:
            NODE_DISPLAY_NAME_MAPPINGS[key] = "呆毛文件去重"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 
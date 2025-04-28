from .daimao_file_finder import DaiMaoFileDuplicatesFinder
import folder_paths
import os

class DaiMaoFileDeduplication:
    """呆毛文件去重节点（向后兼容版），只提供查重功能"""
    @classmethod
    def INPUT_TYPES(cls):
        # 获取ComfyUI的输入路径
        input_dir = folder_paths.get_input_directory()
        output_dir = folder_paths.get_output_directory()
        temp_dir = folder_paths.get_temp_directory()
        models_dir = folder_paths.get_folder_paths("checkpoints")[0] if folder_paths.get_folder_paths("checkpoints") else ""
        
        # 构建预设的目录列表
        preset_dirs = []
        for path in [input_dir, output_dir, temp_dir, models_dir]:
            if path and os.path.exists(path) and path not in preset_dirs:
                preset_dirs.append(path)
                # 尝试向上一级目录
                parent = os.path.dirname(path)
                if parent and os.path.exists(parent) and parent not in preset_dirs:
                    preset_dirs.append(parent)
        
        # 确保列表不为空
        if not preset_dirs:
            preset_dirs = [""]
            
        return {
            "required": {
                "directory_path": ("STRING", {"default": preset_dirs[0], "multiline": False}),
                "preset_dir": (preset_dirs, {"default": preset_dirs[0]}),
                "dedup_type": (["模型文件", "大文件", "全部文件"], {"default": "模型文件"}),
                "size_threshold_mb": ("FLOAT", {"default": 100.0, "min": 0.1, "max": 10000.0, "step": 0.1}),
                "use_preset_dir": (["是", "否"], {"default": "否"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("重复文件信息",)
    FUNCTION = "deduplicate_files"
    CATEGORY = "呆毛工具"
    
    @classmethod
    def IS_CHANGED(cls, browse_directory, **kwargs):
        """检测浏览按钮状态变化，用于触发文件夹选择器"""
        if browse_directory:
            return float("NaN")  # 返回非数字值，确保在点击按钮时Always更新
        return 0

    def __init__(self):
        self.finder = DaiMaoFileDuplicatesFinder()
    
    def deduplicate_files(self, directory_path, preset_dir, dedup_type, size_threshold_mb, use_preset_dir):
        """为了向后兼容，仍然提供完整的查重功能"""
        result, _ = self.finder.find_duplicate_files(directory_path, preset_dir, dedup_type, size_threshold_mb, use_preset_dir)
        return (result,)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "呆毛文件去重": DaiMaoFileDeduplication
}

# 显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "呆毛文件去重": "呆毛文件去重"
} 
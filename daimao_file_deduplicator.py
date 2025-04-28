import os
import json

class DaiMaoFileDeduplicator:
    """呆毛文件去重器节点，根据查重结果删除重复文件"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duplicate_data": ("STRING", {"default": "", "multiline": True, "input_optional": True}),
                "keep_strategy": (["保留第一个文件", "保留最近修改的文件", "保留最大的文件", "保留路径最短的文件"], {"default": "保留第一个文件"}),
                "dry_run": (["是", "否"], {"default": "是"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("删除结果",)
    FUNCTION = "deduplicate_files"
    CATEGORY = "呆毛工具"
    
    def deduplicate_files(self, duplicate_data, keep_strategy, dry_run):
        """根据查重结果和策略删除重复文件"""
        is_dry_run = dry_run == "是"
        
        if duplicate_data == "{}" or not duplicate_data:
            return ("没有重复文件数据，请先使用呆毛文件查重节点查找重复文件。",)
        
        try:
            data = json.loads(duplicate_data)
            if "groups" not in data or not data["groups"]:
                return ("没有找到重复文件组。",)
        except json.JSONDecodeError:
            return ("重复文件数据格式错误，无法解析JSON。",)
        
        total_deleted = 0
        total_freed_space = 0
        result = f"文件去重{'模拟' if is_dry_run else ''}执行结果：\n\n"
        
        for group in data["groups"]:
            result += f"处理组 {group['group_id']} (SHA256: {group['hash'][:10]}...):\n"
            files = group.get("files", [])
            
            if not files:
                result += "  • 此组没有文件信息\n\n"
                continue
                
            files_to_keep = []
            files_to_delete = []
            
            # 根据策略选择要保留的文件
            if keep_strategy == "保留第一个文件":
                files_to_keep = [files[0]]
                files_to_delete = files[1:]
            elif keep_strategy == "保留最近修改的文件":
                # 按修改时间排序，保留最新的
                sorted_files = sorted(files, key=lambda f: os.path.getmtime(f["path"]) if os.path.exists(f["path"]) else 0, reverse=True)
                files_to_keep = [sorted_files[0]]
                files_to_delete = sorted_files[1:]
            elif keep_strategy == "保留最大的文件":
                # 按文件大小排序，保留最大的
                if "size_bytes" in files[0]:
                    sorted_files = sorted(files, key=lambda f: f.get("size_bytes", 0), reverse=True)
                    files_to_keep = [sorted_files[0]]
                    files_to_delete = sorted_files[1:]
                else:
                    # 如果没有大小信息，手动获取
                    sized_files = []
                    for f in files:
                        try:
                            size = os.path.getsize(f["path"]) if os.path.exists(f["path"]) else 0
                            sized_files.append({"path": f["path"], "size": size})
                        except:
                            sized_files.append({"path": f["path"], "size": 0})
                    
                    sorted_files = sorted(sized_files, key=lambda f: f["size"], reverse=True)
                    files_to_keep = [sorted_files[0]]
                    files_to_delete = sorted_files[1:]
            elif keep_strategy == "保留路径最短的文件":
                # 按路径长度排序，保留最短的
                sorted_files = sorted(files, key=lambda f: len(f["path"]))
                files_to_keep = [sorted_files[0]]
                files_to_delete = sorted_files[1:]
            
            # 显示保留的文件
            keep_file = files_to_keep[0]["path"] if isinstance(files_to_keep[0], dict) else files_to_keep[0]
            keep_size = files_to_keep[0].get("size_mb", None) if isinstance(files_to_keep[0], dict) else None
            if keep_size:
                result += f"  • 保留: {keep_file} ({keep_size:.2f} MB)\n"
            else:
                result += f"  • 保留: {keep_file}\n"
            
            # 删除或模拟删除文件
            for file_info in files_to_delete:
                file_path = file_info["path"] if isinstance(file_info, dict) else file_info
                file_size = file_info.get("size_mb", 0) if isinstance(file_info, dict) else 0
                file_size_bytes = file_info.get("size_bytes", 0) if isinstance(file_info, dict) else 0
                
                if is_dry_run:
                    result += f"  • 将删除: {file_path}"
                    if file_size:
                        result += f" ({file_size:.2f} MB)"
                    result += "\n"
                    total_freed_space += file_size_bytes
                    total_deleted += 1
                else:
                    try:
                        if os.path.exists(file_path):
                            # 尝试获取文件大小（如果还没有）
                            if not file_size_bytes:
                                try:
                                    file_size_bytes = os.path.getsize(file_path)
                                    file_size = file_size_bytes / (1024 * 1024)
                                except:
                                    file_size_bytes = 0
                                    file_size = 0
                            
                            total_freed_space += file_size_bytes
                            os.remove(file_path)
                            result += f"  • 已删除: {file_path}"
                            if file_size:
                                result += f" ({file_size:.2f} MB)"
                            result += "\n"
                            total_deleted += 1
                        else:
                            result += f"  • 文件不存在，无法删除: {file_path}\n"
                    except Exception as e:
                        result += f"  • 删除失败: {file_path} - 错误: {str(e)}\n"
            
            result += "\n"
        
        # 总结
        if is_dry_run:
            result += f"模拟删除完成，将删除 {len(data['groups'])} 组中的 {total_deleted} 个文件，"
            result += f"预计释放空间: {total_freed_space / (1024 * 1024):.2f} MB ({total_freed_space / (1024 * 1024 * 1024):.2f} GB)\n"
            result += "注意：这只是模拟结果，没有实际删除文件。要执行实际删除，请将'dry_run'设置为'否'。"
        else:
            result += f"删除完成，共删除 {len(data['groups'])} 组中的 {total_deleted} 个文件，"
            result += f"释放空间: {total_freed_space / (1024 * 1024):.2f} MB ({total_freed_space / (1024 * 1024 * 1024):.2f} GB)"
        
        return (result,)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "呆毛文件去重器": DaiMaoFileDeduplicator
}

# 显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "呆毛文件去重器": "呆毛文件去重器"
} 
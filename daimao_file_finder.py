import os
import hashlib
import glob
import time
import json
from collections import defaultdict
import folder_paths

class DaiMaoFileDuplicatesFinder:
    """呆毛文件查重节点，查找重复文件并输出信息"""
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

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("重复文件信息", "重复文件JSON数据")
    FUNCTION = "find_duplicate_files"
    CATEGORY = "呆毛工具"
    
    @classmethod
    def IS_CHANGED(cls, browse_directory, **kwargs):
        """检测浏览按钮状态变化，用于触发文件夹选择器"""
        if browse_directory:
            return float("NaN")  # 返回非数字值，确保在点击按钮时Always更新
        return 0

    def get_model_files(self, directory):
        """获取目录下的模型文件"""
        model_extensions = [".ckpt", ".safetensors", ".pt", ".pth", ".bin"]
        model_files = []
        
        for ext in model_extensions:
            pattern = os.path.join(directory, f"**/*{ext}")
            model_files.extend(glob.glob(pattern, recursive=True))
            
        return model_files
    
    def get_large_files(self, directory, threshold_mb):
        """获取目录下大于指定阈值的文件"""
        threshold_bytes = threshold_mb * 1024 * 1024
        large_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) > threshold_bytes:
                        large_files.append(file_path)
                except (OSError, FileNotFoundError):
                    continue
                    
        return large_files
    
    def get_all_files(self, directory):
        """获取目录下的所有文件"""
        all_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                all_files.append(os.path.join(root, file))
                
        return all_files
    
    def calculate_sha256(self, file_path):
        """计算文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (OSError, FileNotFoundError):
            return None
    
    def find_duplicates(self, file_list):
        """找出重复文件，并显示进度"""
        hash_dict = defaultdict(list)
        total_files = len(file_list)
        processed = 0
        start_time = time.time()
        last_update = start_time
        update_interval = 1.0  # 每秒更新一次进度
        
        print(f"开始分析 {total_files} 个文件...")
        
        for file_path in file_list:
            file_hash = self.calculate_sha256(file_path)
            if file_hash:
                hash_dict[file_hash].append(file_path)
            
            processed += 1
            current_time = time.time()
            if current_time - last_update >= update_interval:
                elapsed = current_time - start_time
                files_per_second = processed / elapsed if elapsed > 0 else 0
                percent = (processed / total_files) * 100 if total_files > 0 else 0
                print(f"进度: {processed}/{total_files} ({percent:.1f}%) - {files_per_second:.1f} 文件/秒")
                last_update = current_time
        
        # 过滤掉没有重复的文件
        duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}
        
        print(f"分析完成，耗时 {time.time() - start_time:.1f} 秒，找到 {len(duplicates)} 组重复文件。")
        return duplicates
    
    def format_duplicate_result(self, duplicates):
        """将重复文件信息格式化为易读的字符串"""
        if not duplicates:
            return "没有找到重复文件。", json.dumps({})
        
        result = "找到以下重复文件组：\n\n"
        total_wasted_space = 0
        json_data = {"groups": []}
        
        for idx, (hash_val, paths) in enumerate(duplicates.items(), 1):
            # 以第一个文件作为参考，计算重复文件占用的额外空间
            if paths:
                try:
                    file_size = os.path.getsize(paths[0])
                    wasted_space = file_size * (len(paths) - 1)
                    total_wasted_space += wasted_space
                    
                    result += f"组 {idx} (SHA256: {hash_val[:10]}...): {len(paths)} 个文件，浪费空间: {wasted_space / (1024 * 1024):.2f} MB\n"
                    
                    group_data = {
                        "group_id": idx,
                        "hash": hash_val,
                        "file_count": len(paths),
                        "wasted_space_bytes": wasted_space,
                        "wasted_space_mb": wasted_space / (1024 * 1024),
                        "files": []
                    }
                    
                    for path in paths:
                        size_mb = os.path.getsize(path) / (1024 * 1024)
                        result += f"  • {path} ({size_mb:.2f} MB)\n"
                        group_data["files"].append({
                            "path": path,
                            "size_bytes": os.path.getsize(path),
                            "size_mb": size_mb
                        })
                    
                    json_data["groups"].append(group_data)
                    result += "\n"
                except (OSError, FileNotFoundError):
                    result += f"组 {idx} (SHA256: {hash_val[:10]}...): 无法获取文件大小\n"
                    
                    group_data = {
                        "group_id": idx,
                        "hash": hash_val,
                        "file_count": len(paths),
                        "error": "无法获取文件大小",
                        "files": [{"path": path} for path in paths]
                    }
                    
                    json_data["groups"].append(group_data)
                    
                    for path in paths:
                        result += f"  • {path}\n"
                    result += "\n"
        
        total_groups = len(duplicates)
        total_files = sum(len(paths) for paths in duplicates.values())
        
        result += f"总计找到 {total_groups} 组重复文件，共 {total_files} 个文件。\n"
        result += f"浪费的存储空间：{total_wasted_space / (1024 * 1024):.2f} MB ({total_wasted_space / (1024 * 1024 * 1024):.2f} GB)"
        
        json_data["summary"] = {
            "total_groups": total_groups,
            "total_duplicate_files": total_files,
            "total_wasted_space_bytes": total_wasted_space,
            "total_wasted_space_mb": total_wasted_space / (1024 * 1024),
            "total_wasted_space_gb": total_wasted_space / (1024 * 1024 * 1024)
        }
        
        return result, json.dumps(json_data)
    
    def find_duplicate_files(self, directory_path, preset_dir, dedup_type, size_threshold_mb, use_preset_dir):
        """执行文件查重操作"""
        # 处理目录选择
        if use_preset_dir == "是":
            directory_path = preset_dir
            print(f"使用预设目录: {directory_path}")
        
        print(f"开始执行呆毛文件查重：目录 '{directory_path}'，类型 '{dedup_type}'")
        
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return (f"错误：目录 '{directory_path}' 不存在或不是一个有效的目录。", "{}")
        
        # 根据选择的类型获取文件列表
        file_list = []
        if dedup_type == "模型文件":
            print(f"正在扫描模型文件...")
            file_list = self.get_model_files(directory_path)
        elif dedup_type == "大文件":
            print(f"正在扫描大于 {size_threshold_mb} MB 的文件...")
            file_list = self.get_large_files(directory_path, size_threshold_mb)
        else:  # 全部文件
            print(f"正在扫描所有文件...")
            file_list = self.get_all_files(directory_path)
        
        print(f"找到 {len(file_list)} 个文件符合条件")
        
        # 如果没有找到文件
        if not file_list:
            return (f"在目录 '{directory_path}' 中没有找到符合条件的文件。", "{}")
        
        # 查找重复文件
        duplicates = self.find_duplicates(file_list)
        
        # 格式化结果
        result, json_data = self.format_duplicate_result(duplicates)
        
        return (result, json_data)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "呆毛文件查重": DaiMaoFileDuplicatesFinder
}

# 显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "呆毛文件查重": "呆毛文件查重"
} 
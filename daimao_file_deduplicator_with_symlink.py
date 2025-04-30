import os
import json
import platform
import shutil
from pathlib import Path

class DaiMaoFileDeduplicatorWithSymlink:
    """呆毛文件去重器节点（带符号链接），根据查重结果删除重复文件并创建符号链接"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duplicate_data": ("STRING", {"default": "", "multiline": True, "input_optional": True}),
                "keep_strategy": (["保留第一个文件", "保留最近修改的文件", "保留最大的文件", "保留路径最短的文件"], {"default": "保留第一个文件"}),
                "link_type": (["软链接", "硬链接"], {"default": "软链接"}),
                "dry_run": (["是", "否"], {"default": "是"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("处理结果",)
    FUNCTION = "deduplicate_files_with_symlink"
    CATEGORY = "呆毛工具"
    
    def check_windows_permission(self):
        """检查Windows系统下的权限"""
        if platform.system() == "Windows":
            try:
                # 尝试创建一个测试符号链接
                test_target = os.path.abspath(__file__)
                test_link = test_target + ".test"
                try:
                    os.symlink(test_target, test_link)
                    os.remove(test_link)
                except OSError as e:
                    if e.winerror == 1314:  # 需要管理员权限
                        return False, "需要管理员权限才能创建符号链接。请以管理员身份运行ComfyUI。"
                    raise
            except Exception as e:
                return False, f"权限检查失败: {str(e)}"
        return True, None
    
    def is_file_linked(self, file_path, target_path=None):
        """检查文件是否已经是链接"""
        try:
            if os.path.islink(file_path):
                return True, "软链接"
            elif os.path.exists(file_path) and target_path and os.path.samefile(file_path, target_path):
                return True, "硬链接"
            return False, None
        except Exception:
            return False, None
    
    def create_link(self, target_path, link_path, link_type):
        """创建链接（软链接或硬链接），考虑不同操作系统的差异"""
        try:
            # 确保目标路径存在
            if not os.path.exists(target_path):
                return False, f"目标文件不存在: {target_path}"
            
            # 如果链接已存在，先删除
            if os.path.exists(link_path):
                if os.path.islink(link_path) or (link_type == "硬链接" and os.path.samefile(target_path, link_path)):
                    os.remove(link_path)
                else:
                    # 如果已存在的不是链接，先尝试删除
                    try:
                        os.remove(link_path)
                    except Exception as e:
                        return False, f"无法删除已存在的文件: {link_path} - 错误: {str(e)}"
            
            # 根据操作系统和链接类型创建链接
            if platform.system() == "Windows":
                # Windows需要管理员权限才能创建符号链接
                # 使用相对路径可以避免权限问题
                target_path = os.path.abspath(target_path)
                link_path = os.path.abspath(link_path)
                
                # 检查目标文件是否存在
                if not os.path.exists(target_path):
                    return False, f"目标文件不存在: {target_path}"
                
                # 检查目标文件是否是文件
                if not os.path.isfile(target_path):
                    return False, f"目标路径不是文件: {target_path}"
                
                # 检查目标文件是否可读
                if not os.access(target_path, os.R_OK):
                    return False, f"目标文件不可读: {target_path}"
                
                # 检查链接目录是否存在
                link_dir = os.path.dirname(link_path)
                if not os.path.exists(link_dir):
                    return False, f"链接目录不存在: {link_dir}"
                
                # 检查链接目录是否可写
                if not os.access(link_dir, os.W_OK):
                    return False, f"链接目录不可写: {link_dir}"
                
                try:
                    if link_type == "软链接":
                        # 尝试创建符号链接
                        os.symlink(target_path, link_path)
                        
                        # 验证符号链接是否创建成功
                        if not os.path.islink(link_path):
                            return False, f"符号链接创建失败: {link_path}"
                        
                        # 验证符号链接是否指向正确的目标
                        if os.path.realpath(link_path) != target_path:
                            return False, f"符号链接指向错误的目标: {link_path} -> {os.path.realpath(link_path)}"
                    else:
                        # 创建硬链接
                        os.link(target_path, link_path)
                        
                        # 验证硬链接是否创建成功
                        if not os.path.samefile(target_path, link_path):
                            return False, f"硬链接创建失败: {link_path}"
                    
                except OSError as e:
                    if e.winerror == 1314:  # 需要管理员权限
                        return False, f"创建链接需要管理员权限: {link_path}"
                    return False, f"创建链接失败: {str(e)}"
            else:
                # Linux/Unix系统
                if link_type == "软链接":
                    os.symlink(target_path, link_path)
                else:
                    os.link(target_path, link_path)
            
            return True, f"成功创建{link_type}: {link_path} -> {target_path}"
        except Exception as e:
            return False, f"创建{link_type}失败: {str(e)}"
    
    def deduplicate_files_with_symlink(self, duplicate_data, keep_strategy, link_type, dry_run):
        """根据查重结果和策略删除重复文件并创建链接"""
        is_dry_run = dry_run == "是"
        
        if duplicate_data == "{}" or not duplicate_data:
            return ("没有重复文件数据，请先使用呆毛文件查重节点查找重复文件。",)
        
        try:
            data = json.loads(duplicate_data)
            if "groups" not in data or not data["groups"]:
                return ("没有找到重复文件组。",)
        except json.JSONDecodeError:
            return ("重复文件数据格式错误，无法解析JSON。",)
        
        # 检查Windows权限
        if not is_dry_run:
            success, error = self.check_windows_permission()
            if not success:
                return (error,)
        
        total_deleted = 0
        total_freed_space = 0
        total_links = 0
        result = f"文件去重{'模拟' if is_dry_run else ''}执行结果：\n\n"
        
        # 用于跟踪已处理过的文件路径
        processed_paths = set()
        
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
            
            # 删除或模拟删除文件，并创建链接
            for file_info in files_to_delete:
                file_path = file_info["path"] if isinstance(file_info, dict) else file_info
                
                # 如果文件路径已经处理过，跳过
                if file_path in processed_paths:
                    continue
                
                # 检查文件是否已经是链接
                is_linked, link_type_found = self.is_file_linked(file_path, keep_file)
                if is_linked:
                    result += f"  • 跳过: {file_path} 已经是{link_type_found}\n"
                    processed_paths.add(file_path)
                    continue
                
                file_size = file_info.get("size_mb", 0) if isinstance(file_info, dict) else 0
                file_size_bytes = file_info.get("size_bytes", 0) if isinstance(file_info, dict) else 0
                
                if is_dry_run:
                    result += f"  • 将删除: {file_path}"
                    if file_size:
                        result += f" ({file_size:.2f} MB)"
                    result += "\n"
                    result += f"  • 将创建{link_type}: {file_path} -> {keep_file}\n"
                    total_freed_space += file_size_bytes
                    total_deleted += 1
                    total_links += 1
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
                            
                            # 创建临时文件路径
                            temp_path = file_path + ".temp"
                            
                            # 先创建链接到临时路径
                            success, message = self.create_link(keep_file, temp_path, link_type)
                            if success:
                                result += f"  • 已创建{link_type}: {message}\n"
                                total_links += 1
                                
                                # 删除原文件
                                try:
                                    os.remove(file_path)
                                    total_freed_space += file_size_bytes
                                    result += f"  • 已删除: {file_path}"
                                    if file_size:
                                        result += f" ({file_size:.2f} MB)"
                                    result += "\n"
                                    total_deleted += 1
                                    
                                    # 重命名临时文件为原文件名
                                    os.rename(temp_path, file_path)
                                    result += f"  • 已重命名{link_type}: {temp_path} -> {file_path}\n"
                                    
                                    # 将处理过的路径添加到集合中
                                    processed_paths.add(file_path)
                                except Exception as e:
                                    result += f"  • 处理失败: {file_path} - 错误: {str(e)}\n"
                                    # 如果失败，删除临时文件
                                    if os.path.exists(temp_path):
                                        try:
                                            os.remove(temp_path)
                                        except:
                                            pass
                            else:
                                result += f"  • 创建{link_type}失败: {message}\n"
                        else:
                            result += f"  • 文件不存在，无法处理: {file_path}\n"
                    except Exception as e:
                        result += f"  • 处理失败: {file_path} - 错误: {str(e)}\n"
            
            result += "\n"
        
        # 总结
        if is_dry_run:
            result += f"模拟处理完成，将处理 {len(data['groups'])} 组中的 {total_deleted} 个文件，"
            result += f"预计释放空间: {total_freed_space / (1024 * 1024):.2f} MB ({total_freed_space / (1024 * 1024 * 1024):.2f} GB)\n"
            result += f"将创建 {total_links} 个{link_type}\n"
            result += "注意：这只是模拟结果，没有实际执行。要执行实际处理，请将'dry_run'设置为'否'。"
        else:
            result += f"处理完成，共处理 {len(data['groups'])} 组中的 {total_deleted} 个文件，"
            result += f"释放空间: {total_freed_space / (1024 * 1024):.2f} MB ({total_freed_space / (1024 * 1024 * 1024):.2f} GB)\n"
            result += f"创建了 {total_links} 个{link_type}"
        
        return (result,) 
# ComfyUI-DaiMao_Tools (呆毛工具)

一个为ComfyUI提供实用工具的自定义节点集合。

## 项目结构优化

该项目采用模块化设计，将功能拆分为多个独立文件：

- `daimao_file_finder.py` - 文件查重节点
- `daimao_file_deduplicator.py` - 文件去重器节点（执行删除操作）
- `daimao_file_dedup.py` - 向后兼容的文件去重节点

## 功能节点

### 呆毛文件查重

这个节点可以帮助您找出指定目录下的重复文件，支持多种筛选方式：

- **模型文件**：专门查找AI模型相关的文件（.ckpt, .safetensors, .pt, .pth, .bin）
- **大文件**：查找超过指定大小阈值的文件
- **全部文件**：查找目录中的所有文件

所有文件通过SHA256哈希值进行比对，确保找到的是真正的重复文件。节点会计算重复文件占用的额外存储空间，输出人类可读的文本和机器可读的JSON数据。

> **搜索关键词**：您可以使用以下任何关键词在ComfyUI节点搜索框中找到此节点：
> - 呆毛文件查重
> - 查找重复文件
> - 文件查重
> - DaiMaoFileFinder
> - FileDuplicatesFinder
> - FindDuplicates

### 呆毛文件去重器

这个节点接收由"呆毛文件查重"节点提供的JSON数据，根据选择的策略删除重复文件：

- **保留第一个文件**：保留每组重复文件中的第一个文件，删除其余文件
- **保留最近修改的文件**：保留每组中最近修改过的文件
- **保留最大的文件**：保留每组中最大的文件
- **保留路径最短的文件**：保留每组中路径最短的文件

节点提供"模拟"模式，让您在实际删除前预览将会删除哪些文件。

> **搜索关键词**：您可以使用以下任何关键词在ComfyUI节点搜索框中找到此节点：
> - 呆毛文件去重器
> - 删除重复文件
> - DaiMaoDeduplicator
> - FileDeduplicator
> - RemoveDuplicates

### 呆毛文件去重

这是一个功能完整的节点（为保持向后兼容），综合了查重功能，但不提供删除功能。如果您只需要查找并查看重复文件信息，可以使用此节点。

> **搜索关键词**：您可以使用以下任何关键词在ComfyUI节点搜索框中找到此节点：
> - 呆毛文件去重
> - 文件去重
> - 文件查重
> - DaiMaoFileDedup
> - FileDeduplication
> - DedupFiles

## 安装

1. 将此仓库克隆到ComfyUI的`custom_nodes`目录：
   ```
   cd ComfyUI/custom_nodes
   git clone https://github.com/yourusername/ComfyUI-DaiMao_Tools.git
   ```

2. 重启ComfyUI

## 使用方法

### 目录选择功能

节点提供了两种设置查重目录的方式：

1. **手动输入路径**：在`directory_path`文本框中直接输入目录的完整路径
2. **使用预设目录**：
   - 下拉列表`preset_dir`中包含了ComfyUI中常用的目录（输入目录、输出目录、模型目录等）
   - 选择需要的预设目录，然后将`use_preset_dir`设置为"是"

预设目录功能让您无需手动输入路径，直接查找ComfyUI相关目录中的重复文件。

### 单节点模式（呆毛文件去重）

1. 从节点选择菜单中找到"呆毛工具"分类，或直接在搜索框中输入"文件去重"
2. 添加"呆毛文件去重"节点到工作流
3. 设置以下参数：
   - `directory_path`：要扫描的目录路径（手动输入）
   - `preset_dir`：选择一个预设目录
   - `use_preset_dir`：选择"是"使用预设目录，"否"使用手动输入的路径
   - `dedup_type`：选择"模型文件"、"大文件"或"全部文件"
   - `size_threshold_mb`：当选择"大文件"时，设置大小阈值（MB）
4. 运行工作流后，节点将输出重复文件的详细信息，包括文件路径和大小

### 分离节点模式（查重+去重）

1. 添加"呆毛文件查重"节点到工作流
2. 设置查重参数（与单节点模式相同）
3. 添加"呆毛文件去重器"节点
4. 将"呆毛文件查重"的"重复文件JSON数据"输出连接到"呆毛文件去重器"的"duplicate_data"输入
5. 在"呆毛文件去重器"上选择保留策略和是否为模拟运行
6. 运行工作流，先查找重复文件，然后根据策略删除文件

### 示例工作流

项目包含两个预配置的示例工作流：

1. `examples/file_dedup_workflow.json` - 单节点模式示例
2. `examples/file_dedup_with_separate_nodes.json` - 分离节点模式示例

导入步骤：
1. 在ComfyUI中点击右上角的"Load"按钮
2. 导航到`custom_nodes/ComfyUI-DaiMao_Tools/examples`目录
3. 选择需要的工作流文件
4. 根据需要修改参数
5. 点击"Queue Prompt"运行工作流

## 输出示例

### 呆毛文件查重节点输出

```
找到以下重复文件组：

组 1 (SHA256: 7a8b9c0d1e...): 2 个文件，浪费空间: 2048.55 MB
  • D:/models/model1.safetensors (2048.55 MB)
  • D:/models/backup/model1.safetensors (2048.55 MB)

组 2 (SHA256: 2e3f4a5b6c...): 3 个文件，浪费空间: 4097.10 MB
  • D:/models/model2.safetensors (2048.55 MB)
  • D:/models/old/model2.safetensors (2048.55 MB)
  • D:/models/test/model2.safetensors (2048.55 MB)

总计找到 2 组重复文件，共 5 个文件。
浪费的存储空间：6145.65 MB (6.00 GB)
```

### 呆毛文件去重器节点输出

```
文件去重模拟执行结果：

处理组 1 (SHA256: 7a8b9c0d1e...):
  • 保留: D:/models/model1.safetensors (2048.55 MB)
  • 将删除: D:/models/backup/model1.safetensors (2048.55 MB)

处理组 2 (SHA256: 2e3f4a5b6c...):
  • 保留: D:/models/model2.safetensors (2048.55 MB)
  • 将删除: D:/models/old/model2.safetensors (2048.55 MB)
  • 将删除: D:/models/test/model2.safetensors (2048.55 MB)

模拟删除完成，将删除 2 组中的 3 个文件，预计释放空间: 6145.65 MB (6.00 GB)
注意：这只是模拟结果，没有实际删除文件。要执行实际删除，请将'dry_run'设置为'否'。
```

## 注意事项

- 文件较多时，扫描过程可能需要一些时间，特别是"全部文件"模式
- 建议先使用"模型文件"或"大文件"模式减少扫描范围
- 计算SHA256哈希值需要读取完整文件内容，对于大文件可能比较耗时
- 在执行实际删除前，强烈建议先使用"模拟"模式（dry_run="是"）查看哪些文件将被删除
- 删除操作不可逆，请谨慎使用 
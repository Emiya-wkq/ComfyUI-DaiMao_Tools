# ComfyUI-DaiMao_Tools

一个专为ComfyUI设计的暗水印工具集合，支持文本和图片水印的嵌入与提取。

## 🌟 主要功能

### 📝 文本水印
- **智能长度计算**: 自动根据文本内容计算所需的bit长度
- **多语言支持**: 完美支持中文、英文及特殊字符
- **编码优化**: 智能处理UTF-8编码，避免乱码问题
- **长度兼容**: 支持手动指定长度或自动计算

### 🖼️ 图片水印
- **灵活尺寸**: 支持任意尺寸的水印图片
- **格式兼容**: 自动处理不同图片格式转换
- **质量保证**: 使用高质量JPEG格式确保兼容性

### 🔐 安全特性
- **双重密码**: 支持图片密码和水印密码
- **隐蔽性强**: 基于blind_watermark算法，肉眼不可见
- **抗攻击**: 对常见图片处理操作具有一定抗性

## 📦 安装要求

### 依赖库
```bash
pip install blind-watermark
pip install opencv-python
pip install pillow
pip install torch
pip install numpy
```

### ComfyUI集成
1. 将本项目克隆到ComfyUI的`custom_nodes`目录
2. 重启ComfyUI
3. 在节点列表中找到"暗水印工具"分类

## 🚀 使用指南

### 水印嵌入节点 (BlindWatermarkEmbed)

#### 输入参数
- **image**: 要嵌入水印的原始图片
- **watermark_text**: 要嵌入的文本水印（默认："DaiMao Tools"）
- **password_img**: 图片密码（1-999999）
- **password_wm**: 水印密码（1-999999）
- **watermark_image**: 可选的图片水印

#### 输出结果
- **嵌入水印的图片**: 包含隐藏水印的图片
- **水印信息**: JSON格式的水印详细信息

#### 使用示例

**文本水印嵌入:**
```
输入图片 → BlindWatermarkEmbed节点
├─ watermark_text: "版权所有 © 2024"
├─ password_img: 12345
├─ password_wm: 67890
└─ watermark_image: (留空)
```

**图片水印嵌入:**
```
输入图片 → BlindWatermarkEmbed节点
├─ watermark_text: (留空)
├─ password_img: 12345
├─ password_wm: 67890
└─ watermark_image: 水印图片
```

### 水印提取节点 (BlindWatermarkExtractNode)

#### 输入参数
- **image**: 包含水印的图片
- **password_img**: 图片密码（必须与嵌入时一致）
- **password_wm**: 水印密码（必须与嵌入时一致）
- **watermark_type**: 水印类型（"text"或"image"）
- **original_text**: 原始文本（用于自动计算长度）
- **watermark_length**: 手动指定的水印长度
- **watermark_width**: 图片水印宽度
- **watermark_height**: 图片水印高度

#### 输出结果
- **提取的水印文本**: 解码后的文本内容
- **提取的水印图片**: 提取的图片水印

#### 使用示例

**文本水印提取（自动长度）:**
```
含水印图片 → BlindWatermarkExtractNode
├─ password_img: 12345
├─ password_wm: 67890
├─ watermark_type: "text"
├─ original_text: "版权所有 © 2024"  # 自动计算长度
└─ watermark_length: (忽略)
```

**文本水印提取（手动长度）:**
```
含水印图片 → BlindWatermarkExtractNode
├─ password_img: 12345
├─ password_wm: 67890
├─ watermark_type: "text"
├─ original_text: (留空)
└─ watermark_length: 128  # 手动指定
```

**图片水印提取:**
```
含水印图片 → BlindWatermarkExtractNode
├─ password_img: 12345
├─ password_wm: 67890
├─ watermark_type: "image"
├─ watermark_width: 64
└─ watermark_height: 64
```

## 🔧 技术特性

### 多进程兼容
- 自动修复multiprocessing上下文问题
- 支持ComfyUI的多线程环境
- 优雅处理库导入冲突

### 文件格式优化
- 使用JPEG格式确保OpenCV兼容性
- 自动RGB模式转换
- 临时文件安全管理

### 错误处理
- 多重备选方案确保提取成功
- 详细的错误日志和调试信息
- 优雅的异常恢复机制

### 编码处理
- UTF-8编码自动检测和转换
- 控制字符过滤
- 多语言字符支持

## 📊 水印信息格式

嵌入成功后返回的水印信息包含：

**文本水印信息:**
```json
{
    "type": "text",
    "content": "版权所有 © 2024",
    "shape_or_length": 128,
    "password_img": 12345,
    "password_wm": 67890,
    "text": "版权所有 © 2024",
    "length": 128,
    "char_count": 12,
    "utf8_bytes": 16
}
```

**图片水印信息:**
```json
{
    "type": "image",
    "content": "图片水印 (64, 64)",
    "shape_or_length": [64, 64],
    "password_img": 12345,
    "password_wm": 67890
}
```

## ⚠️ 注意事项

### 密码管理
- 嵌入和提取时必须使用相同的密码组合
- 建议使用复杂密码提高安全性
- 妥善保管密码，丢失后无法恢复水印

### 长度计算
- 文本水印长度 = UTF-8字节数 × 8
- 建议优先使用原始文本自动计算长度
- 手动指定长度时需确保足够容纳文本内容

### 图片要求
- 载体图片建议尺寸大于256×256
- 水印图片尺寸应小于载体图片
- 支持RGB和灰度图片

### 性能优化
- 大图片处理可能需要较长时间
- 建议在高性能设备上处理大尺寸图片
- 临时文件会自动清理

## 🐛 故障排除

### 常见问题

**1. "blind_watermark 库未安装"**
```bash
pip install blind-watermark
```

**2. "OpenCV写入错误"**
- 已自动使用JPEG格式解决
- 确保有足够的磁盘空间

**3. "提取结果乱码"**
- 检查密码是否正确
- 使用原始文本自动计算长度
- 确认水印类型选择正确

**4. "多进程错误"**
- 已自动修复，重启ComfyUI即可

### 调试模式
设置环境变量启用详细日志：
```bash
export WATERMARK_DEBUG=1
```

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进本项目！

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**版本**: 2.0.0  
**更新日期**: 2024年12月  
**兼容性**: ComfyUI 最新版本

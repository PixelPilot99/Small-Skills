---
name: psd-processor
description: |
  处理Adobe Photoshop (PSD) 文件的技能。当用户需要将PSD文件导出为图片格式（JPG/PNG）或导出PSD的各个图层为单独图片时使用此技能。
  适用于批量处理PSD文件、提取图层、转换PSD为常见图片格式等任务。
  当用户提到"PSD"、"Photoshop"、"导出图层"、"导出PSD为图片"、"批量处理PSD"等关键词时，应考虑使用此技能。
compatibility:
  tools:
    - Bash
    - Read
    - Glob
  dependencies:
    - Python 3.6+
    - psd-tools (可通过 pip install psd-tools Pillow 安装)
---

# PSD 文件处理技能

此技能提供两种主要的PSD处理功能：
1. **批量导出PSD为图片** - 将PSD文件转换为JPG或PNG格式
2. **导出PSD图层** - 将PSD的各个图层导出为单独的图片文件

## 快速开始

根据用户需求选择以下功能之一：

### 1. 批量导出PSD为图片
当用户需要将整个PSD文件导出为JPG或PNG图片时使用此功能。

**常用指令示例：**
- "将这些PSD文件导出为PNG"
- "把PSD转换成JPG格式"
- "批量导出PSD文件"

### 2. 导出PSD图层
当用户需要提取PSD文件中的各个图层为单独图片时使用此功能。

**常用指令示例：**
- "导出这个PSD的所有图层"
- "把PSD的每个图层保存为单独图片"
- "提取PSD图层为PNG"

## 使用方法

### 依赖检查
在执行任何PSD处理前，首先检查系统是否已安装所需依赖：
```bash
python -c "import psd_tools, PIL" 2>/dev/null || echo "需要安装依赖：pip install psd-tools Pillow"
```

如果未安装，提示用户并帮助安装：
```bash
pip install psd-tools Pillow
```

### 功能选择流程

1. **分析用户请求**，确定需要哪种功能：
   - 如果用户提到"图层"、"每个图层"、"分别导出" → 使用图层导出功能
   - 如果用户提到"转换"、"导出为"、"保存为图片" → 使用批量导出功能
   - 如果不确定，询问用户具体需求

2. **收集必要参数**：
   - **输入目录/文件**：PSD文件所在位置
   - **输出目录**：图片保存位置（可选，有默认值）
   - **格式**：JPG或PNG（默认：JPG）
   - **其他选项**：质量、是否递归搜索等

3. **执行相应脚本**：
   - 批量导出：`python scripts/psd_export.py [参数]`
   - 图层导出：`python scripts/psd_export_layers.py [参数]`

## 详细功能说明

### 批量导出PSD为图片 (`scripts/psd_export.py`)
此脚本将目录中的PSD文件批量导出为JPG或PNG图片。

**命令行参数：**
```bash
# 基本用法
python scripts/psd_export.py --input /path/to/psd --output /path/to/output --format png

# 完整选项
python scripts/psd_export.py \
  --input /path/to/psd \
  --output /path/to/output \
  --format jpg \
  --quality 95 \
  --pattern "*.psd" \
  --no-recursive \
  --silent
```

**参数说明：**
- `--input, -i`: PSD文件所在目录（必需）
- `--output, -o`: 输出目录（可选，默认为输入目录下的jpg_output或png_output）
- `--format, -f`: 输出格式，jpg或png（默认：jpg）
- `--quality, -q`: JPG质量，1-100（默认：95，PNG忽略此参数）
- `--pattern`: 文件匹配模式（默认："*.psd"）
- `--no-recursive`: 不递归搜索子目录
- `--silent`: 静默模式，减少日志输出

### 导出PSD图层 (`scripts/psd_export_layers.py`)
此脚本将PSD文件的各个图层导出为单独的图片文件。

**命令行参数：**
```bash
# 基本用法
python scripts/psd_export_layers.py --input /path/to/psd --output /path/to/output --format png

# 完整选项
python scripts/psd_export_layers.py \
  --input /path/to/psd \
  --output /path/to/output \
  --format png \
  --quality 95 \
  --pattern "*.psd" \
  --no-hidden \
  --top-only \
  --no-recursive \
  --silent
```

**参数说明：**
- `--input, -i`: PSD文件所在目录（必需）
- `--output, -o`: 输出目录（可选，默认为输入目录下的layers_output）
- `--format, -f`: 输出格式，png、jpg或jpeg（默认：png）
- `--quality, -q`: JPG质量，1-100（默认：95）
- `--pattern`: 文件匹配模式（默认："*.psd"）
- `--no-hidden`: 不导出隐藏图层
- `--top-only`: 只导出顶层，不递归子图层
- `--no-recursive`: 输入目录不递归搜索
- `--silent`: 减少日志输出

## 交互模式

如果用户没有提供完整参数，脚本支持交互式输入。直接运行脚本而不带参数将进入交互模式：

```bash
# 交互式批量导出
python scripts/psd_export.py

# 交互式图层导出
python scripts/psd_export_layers.py
```

## 输出结构

### 批量导出输出结构
```
输出目录/
├── image1.jpg
├── subfolder/
│   └── image2.jpg
└── ...
```

### 图层导出输出结构
```
输出目录/
├── 文件名1/
│   ├── 001_图层1.png
│   ├── 002_图层2.png
│   └── ...
├── 文件名2/
│   ├── 001_背景.png
│   ├── 002_文字.png
│   └── ...
└── ...
```

## 最佳实践

1. **总是检查依赖**：在执行前确认psd-tools和Pillow已安装
2. **提供清晰反馈**：告诉用户正在执行的操作和预计输出位置
3. **处理错误**：如果脚本执行失败，提供有用的错误信息
4. **验证输入**：确认输入的PSD目录存在且包含PSD文件
5. **保持组织**：建议有意义的输出目录结构

## 示例对话

**用户**: "帮我把这个PSD文件导出为PNG"
**Claude**: "好的，我会帮您将PSD文件导出为PNG格式。首先让我检查一下所需的依赖..."
```bash
# 检查依赖
python -c "import psd_tools" 2>/dev/null || pip install psd-tools Pillow
# 执行导出
python scripts/psd_export.py --input /path/to/psd --format png
```

**用户**: "我需要导出这个PSD的所有图层"
**Claude**: "我将帮您导出PSD的所有图层为单独图片。使用PNG格式可以保留透明度..."
```bash
# 执行图层导出
python scripts/psd_export_layers.py --input /path/to/psd --format png
```

**用户**: "批量处理这个文件夹里的所有PSD文件，转换成JPG"
**Claude**: "我会递归处理这个文件夹中的所有PSD文件，将它们转换为JPG格式..."
```bash
python scripts/psd_export.py --input /path/to/folder --format jpg --quality 90
```

## 注意事项

1. **大文件处理**：大型PSD文件可能需要较多内存和处理时间
2. **透明度处理**：JPG格式不支持透明度，透明区域将转为白色背景
3. **图层命名**：图层名称中的特殊字符会被替换为下划线
4. **兼容性**：某些PSD特性可能不被psd-tools完全支持
5. **错误处理**：如果遇到损坏的PSD文件，脚本会跳过并继续处理其他文件
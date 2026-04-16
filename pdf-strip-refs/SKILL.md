---
name: pdf-strip-refs
description: 去除PDF文献中的参考文献部分，用于RAG预处理。基于pymupdf，可批量处理。
license: MIT
---

# PDF参考文献去除工具

## 概述

该技能提供去除PDF文档中参考文献部分的功能，适用于RAG（检索增强生成）预处理。通过识别“References”、“Bibliography”等标题，自动删除参考文献及后续页面，保留正文内容。

## 使用方法

### 命令行调用（在Claude Code中使用）

```bash
python scripts/pdf_strip_refs.py -i /path/to/pdf/directory -o /path/to/output/directory
```

### 交互式运行

```bash
python scripts/pdf_strip_refs.py
```

### 在Python代码中直接调用

```python
from scripts.pdf_strip_refs import strip_references, batch_strip

# 处理单个PDF
strip_references("input.pdf", "output.pdf")

# 批量处理
batch_strip("/path/to/input", "/path/to/output")
```

## 参数说明

- `-i, --input`: PDF文件所在目录（必需）
- `-o, --output`: 处理后PDF的输出目录（可选，默认为输入目录下的`no_refs`子目录）

## 检测的关键词

脚本会自动识别以下参考文献标题（不区分大小写）：

- References
- REFERENCES
- Bibliography
- BIBLIOGRAPHY
- 参考文献

## 输出说明

- 如果找到参考文献标题：截断该位置及之后的所有内容，生成新文件（文件名添加`_no_refs`后缀）
- 如果未找到参考文献标题：原样复制PDF文件
- 输出文件保存在指定输出目录中

## 依赖项

```bash
pip install pymupdf
```

## 示例

```bash
# 批量处理当前目录下的PDF文件
python scripts/pdf_strip_refs.py -i ./pdfs -o ./processed

# 交互式运行（会提示输入目录）
python scripts/pdf_strip_refs.py
```

## 注意事项

1. 仅支持PDF格式文件
2. 参考文献标题必须单独成行（作为一个文本块）
3. 使用pymupdf的redaction功能永久删除文本层内容
4. 处理后的PDF可能会丢失参考文献部分的文本，但保留原始格式
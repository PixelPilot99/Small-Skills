---
name: pdf-strip-refs
description: 去除PDF文献中的参考文献部分，用于RAG预处理。基于pymupdf，可批量处理。
license: MIT
---

# PDF参考文献去除工具

## 概述

去除PDF文档中的参考文献部分，适用于RAG预处理。通过识别”References”、”Bibliography”、”参考文献”等标题，自动删除参考文献及后续页面。

## 调用方式

### 单个文件（推荐）

直接用 `python -c` 导入函数处理，适用于单个或少量文件：

```bash
python -c “
import sys
sys.path.insert(0, r'<skill_dir>/scripts')
from pdf_strip_refs import strip_references
strip_references(r'input.pdf', r'output.pdf')
“
```

输出文件名约定：在原文件名后加 `_no_refs` 后缀（如 `paper_no_refs.pdf`）。

### 批量处理（目录级别）

当用户需要批量处理一个目录下的所有 PDF 时才用此方式：

```bash
python <skill_dir>/scripts/pdf_strip_refs.py -i /path/to/pdf/dir -o /path/to/output/dir
```

参数：
- `-i, --input`: PDF文件所在目录（必需）
- `-o, --output`: 输出目录（**调用时始终提供此参数**，避免回退到交互式输入导致 EOFError）

## 执行策略

**不要预先检查依赖。** 直接运行上述命令。只有当 `import fitz` 报 `ModuleNotFoundError` 时，才执行 `pip install pymupdf` 后重试。

## 检测关键词

以下标题会被识别为参考文献起始位置（完整匹配一个文本块，不区分大小写）：

- References / REFERENCES
- Bibliography / BIBLIOGRAPHY
- 参考文献

## 输出说明

- 找到参考文献：截断该位置及后续内容，输出 `_no_refs.pdf`
- 未找到：原样复制 PDF（不会丢失内容）
- 返回值 `True` = 已截断，`False` = 未找到参考文献

## 注意事项

1. 参考文献标题必须单独成行（作为一个文本块），不会被正文中的孤立单词误触发
2. 使用 pymupdf redaction 永久删除文本层内容，不可逆
3. 单文件场景请勿用 CLI 参数——CLI 要求输入目录，多余且不灵活
4. **`-o` 参数在 agent/CI 下必须提供。** 脚本中 `get_paths()` 在未提供 `-o` 时会回退到 `input()` 交互式输入，而非交互式环境（agent 调用、CI 流水线）中 `input()` 会抛出 `EOFError` 导致脚本崩溃。
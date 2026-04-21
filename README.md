# Small-Skills

> A collection of lightweight, independent Claude Code skills / 一组轻量级、独立运行的 Claude Code 技能合集

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview / 简介

This repository houses multiple standalone skills designed to extend Claude Code's capabilities. Each skill is self-contained in its own subdirectory and can be used independently.

本仓库包含多个独立的技能，旨在扩展 Claude Code 的功能。每个技能独立存放在各自的子目录中，可单独使用。

## Skills / 技能列表

| Skill | Description | 描述 |
|-------|-------------|------|
| `media-to-text` | Convert video/audio to text using speech recognition. Supports clipping and multiple formats. Requires `SKILL_ASR_API_KEY` environment variable. | 视频/音频转文字工具，基于语音识别。支持剪辑和多种音视频格式。需要配置 `SKILL_ASR_API_KEY` 环境变量。 |
| `pdf-strip-refs` | Remove references/bibliography section from PDF academic papers. Useful for RAG preprocessing. | 去除 PDF 学术论文中的参考文献部分，适用于 RAG 预处理场景。 |
| `psd-processor` | Batch export PSD files to image formats (JPG/PNG). Supports exporting individual layers. | 批量将 PSD 文件导出为图片格式（JPG/PNG），支持单独导出图层。 |

## Directory Structure / 目录结构

```
Small-Skills/
├── media-to-text/          # Video/audio to text skill
│   └── SKILL.md            # Skill definition
├── pdf-strip-refs/         # PDF reference stripper
│   └── SKILL.md            # Skill definition
├── psd-processor/          # PSD batch processor
│   └── SKILL.md            # Skill definition
├── CLAUDE.md               # Project-level instructions
└── README.md               # This file
```


## Configuration / 配置

### media-to-text

Set your ASR API key before using:

使用前请设置 ASR API 密钥：

```bash
export SKILL_ASR_API_KEY="your-api-key-here"
```

> **Note / 注意**: The platform endpoint can be modified in the skill code. API endpoint 地址可在技能代码中修改。

## License / 许可证

Each skill is licensed under the MIT License. Please refer to the `LICENSE` file within each skill's subdirectory for terms.

每个技能均采用 MIT 许可证授权，详情请参阅各技能子目录中的 `LICENSE` 文件。

---

*Star this repository if you find it useful! / 如果对你有帮助，请给我们点个 Star！*

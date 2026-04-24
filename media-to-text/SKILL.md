---
name: media-to-text
description: 将视频或音频文件转换为文本的工具。使用MoviePy提取音频，通过SiliconFlow ASR API进行语音识别。支持视频截取、多种音频格式。当用户需要将视频文件（如MP4）或音频文件（如MP3、WAV）转换为文本内容时使用此技能。适用于转录会议录音、视频字幕提取、语音笔记转文字等场景。注意：需要SKILL_ASR_API_KEY环境变量，切勿在对话中暴露API密钥内容。
compatibility: 需要Python环境及moviepy、requests库，需要设置SKILL_ASR_API_KEY环境变量。
---

# 媒体转文本工具

**⚠️ 安全重要提示**：本技能需要`SKILL_ASR_API_KEY`环境变量。请勿在任何日志、控制台输出或对话中显示此API密钥的实际内容。只能验证环境变量是否存在，不能显示其值。详情参见"安全提示"章节。

本技能提供将视频或音频文件转换为文本的功能。它包含两个主要组件：
1. **视频转音频**：使用MoviePy库从视频文件中提取音频并保存为MP3格式
2. **音频转文本**：通过SiliconFlow的ASR API将音频文件转录为文本

## 先决条件

### 1. Python依赖
确保已安装以下Python库：
```bash
pip install moviepy requests
```

### 2. API密钥
需要设置环境变量`SKILL_ASR_API_KEY`，包含SiliconFlow平台的API密钥：
```bash
# Windows
setx SKILL_ASR_API_KEY "your-api-key-here"

# Linux/macOS
export SKILL_ASR_API_KEY="your-api-key-here"
```

### 3. 文件权限
确保有读取输入文件和写入输出文件的权限。

## 使用方法

### 基本命令格式
```bash
# 视频文件转文本
python scripts/process_media.py -i 输入视频文件 -o 输出文本文件 [选项]

# 音频文件转文本
python scripts/process_media.py -i 输入音频文件 -o 输出文本文件
```

### 完整参数说明
| 参数 | 必选 | 说明 |
|------|------|------|
| `-i`, `--input` | 是 | 输入文件路径（支持.mp4, .mp3, .wav等格式） |
| `-o`, `--output` | 是 | 输出文本文件路径（.txt格式） |
| `--start` | 否 | 开始截取时间（支持秒数或HH:MM:SS格式） |
| `--end` | 否 | 结束截取时间（不能与--duration同时使用） |
| `--duration` | 否 | 持续时间（秒）（不能与--end同时使用） |
| `--keep-audio` | 否 | 保留中间生成的音频文件（默认不保留） |
| `--audio-output` | 否 | 指定中间音频文件路径（如不指定则自动生成临时文件） |

### 时间格式说明
- **秒数**：`90` 或 `90.5`
- **时间格式**：`HH:MM:SS` 或 `MM:SS` 或 `HH:MM:SS.mmm`
- 示例：`00:01:30` 表示1分30秒，`120.5` 表示120.5秒

## 工作流程

1. **检测输入文件类型**
   - 如果是视频文件（.mp4, .mov, .avi等），先使用`Movie_to_Sound.py`提取音频
   - 如果是音频文件（.mp3, .wav, .m4a等），直接进入下一步

2. **视频截取处理**（如果指定了时间参数）
   - 根据`--start`、`--end`或`--duration`参数截取指定时间段的音频

3. **语音识别**
   - 使用`Use_ASRmodel.py`调用SiliconFlow ASR API进行转录
   - API模型：FunAudioLLM/SenseVoiceSmall

4. **结果保存**
   - 将转录文本保存到指定的输出文件
   - 根据`--keep-audio`决定是否保留中间音频文件

## 示例

### 示例1：完整视频转文本
```bash
python scripts/process_media.py -i meeting.mp4 -o meeting_transcript.txt
```

### 示例2：截取视频片段转文本
```bash
# 从第30秒到第2分10秒
python scripts/process_media.py -i presentation.mp4 -o excerpt.txt --start 00:00:30 --end 00:02:10

# 从第10秒开始，持续60秒
python scripts/process_media.py -i lecture.mp4 -o part.txt --start 10 --duration 60

# 只从第1分20秒开始，到视频结束
python scripts/process_media.py -i interview.mp4 -o interview.txt --start 00:01:20
```

### 示例3：音频文件转文本
```bash
python scripts/process_media.py -i recording.mp3 -o transcript.txt
```

### 示例4：保留中间音频文件
```bash
python scripts/process_media.py -i video.mp4 -o output.txt --keep-audio --audio-output extracted_audio.mp3
```

## 脚本说明

### 1. Movie_to_Sound.py
视频转音频工具，基于MoviePy库。支持：
- 视频文件读取（支持多种格式）
- 时间截取（开始时间、结束时间、持续时间）
- 音频提取和保存为MP3格式
- 自动处理MoviePy 1.x和2.x版本差异

### 2. Use_ASRmodel.py
语音识别工具，使用SiliconFlow ASR API。功能：
- 音频文件上传和转录
- 错误处理和API响应验证
- 结果保存为UTF-8编码的文本文件

### 3. process_media.py（主脚本）
集成两个功能的统一入口脚本，提供：
- 文件类型自动检测
- 工作流程协调
- 参数解析和错误处理
- 临时文件管理

## 错误处理

### 自动诊断机制
出错时脚本会自动调用环境诊断，检查以下项目（无需提前手动检查）：
1. **moviepy库**（视频文件时需要）— 是否已安装
2. **requests库** — 是否已安装
3. **SKILL_ASR_API_KEY环境变量** — 是否已设置（仅检查是否存在，不显示密钥值）

### 常见错误及解决方法
1. **API密钥错误**：检查`SKILL_ASR_API_KEY`环境变量是否正确设置（脚本出错时会自动检测）
2. **文件不存在**：确认输入文件路径正确
3. **时间参数无效**：检查时间格式是否正确，确保开始时间小于结束时间
4. **依赖缺失**：确保已安装moviepy和requests库（脚本出错时会自动检测并给出安装命令）
5. **网络错误**：检查网络连接，确认能访问SiliconFlow API

### 错误代码
- `0`：成功
- `1`：输入文件不存在
- `2`：时间参数冲突（同时指定了--end和--duration）
- `3`：视频转音频失败
- `4`：音频文件未生成
- `5`：不支持的文件格式
- `6`：音频转文本失败
- `99`：未知错误

## 性能提示

1. **大文件处理**：对于长视频，考虑先截取关键片段以减少处理时间
2. **批量处理**：可以编写脚本批量处理多个文件
3. **音频质量**：确保音频清晰度以获得最佳转录效果
4. **网络连接**：API调用需要稳定的网络连接

## 注意事项

1. **API限制**：SiliconFlow API可能有调用频率和文件大小限制，请参考其官方文档
2. **隐私考虑**：音频文件会上传到云端处理，请勿上传敏感或机密内容
3. **临时文件**：默认会生成临时音频文件，处理完成后自动删除（除非使用`--keep-audio`）
4. **编码格式**：输出文本文件使用UTF-8编码，确保文本编辑器支持

## 安全提示

### API密钥保护
**重要**：`SKILL_ASR_API_KEY`是敏感凭据，请勿在日志、控制台输出或任何可公开访问的位置显示。

**安全检查方法**（不暴露密钥）：
```bash
# 检查环境变量是否设置（不显示值）
# Windows PowerShell
if ($env:SKILL_ASR_API_KEY) { echo "API密钥已设置" } else { echo "API密钥未设置" }

# Windows CMD
if defined SKILL_ASR_API_KEY (echo API密钥已设置) else (echo API密钥未设置)

# Linux/macOS
if [ -n "$SKILL_ASR_API_KEY" ]; then echo "API密钥已设置"; else echo "API密钥未设置"; fi

# Python检查
python -c "import os; print('API密钥已设置' if os.getenv('SKILL_ASR_API_KEY') else 'API密钥未设置')"
```

**错误做法**（会暴露密钥）：
```bash
# ❌ 危险：直接显示API密钥
echo $SKILL_ASR_API_KEY
echo %SKILL_ASR_API_KEY%
print(os.getenv('SKILL_ASR_API_KEY'))  # 在代码中直接打印
```

### 使用本技能时的安全指南
1. **不要要求Claude显示或验证API密钥的具体内容**，只需确认环境变量是否存在
2. **在调试时**，使用上述安全检查方法，避免密钥泄露
3. **在共享日志或截图时**，确保API密钥被遮盖或删除
4. **定期轮换密钥**，特别是如果怀疑密钥可能已泄露

### 技能内置保护
- 本技能的脚本只会检查`SKILL_ASR_API_KEY`是否存在，不会在日志中输出其内容
- API调用使用标准Authorization头，密钥在HTTPS请求中加密传输
- 临时文件处理完成后会自动清理，不保留敏感数据

## 扩展使用

### 集成到其他脚本
```python
from scripts.Movie_to_Sound import main as video_to_audio
from scripts.Use_ASRmodel import transcribe_audio
import subprocess

# 直接调用脚本
subprocess.run(["python", "scripts/process_media.py", "-i", "input.mp4", "-o", "output.txt"])
```

### 自定义ASR模型
如需使用其他ASR模型，可修改`Use_ASRmodel.py`中的`model`参数。

## 支持的文件格式

### 视频格式
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)
- FLV (.flv)
- 其他MoviePy支持的格式

### 音频格式
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- AAC (.aac)
- OGG (.ogg)
- 其他常见音频格式

## 更新日志

- v1.0：初始版本，集成视频转音频和语音识别功能
- v1.1：添加时间截取功能，支持多种时间格式
- v1.2：优化错误处理，添加临时文件管理
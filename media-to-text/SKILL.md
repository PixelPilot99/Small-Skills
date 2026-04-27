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

## 依赖说明

运行所需依赖（脚本出错时会自动诊断，无需提前手动检查）：

- **Python库**：`moviepy`, `requests`
- **环境变量**：`SKILL_ASR_API_KEY`（SiliconFlow API 密钥）
- **文件权限**：读取输入文件、写入输出文件

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
   - 视频文件（.mp4/.avi/.mov 等）→ `Movie_to_Sound.py` 提取音频
   - 音频文件（.mp3/.wav/.m4a 等）→ 直接使用

2. **时间截取**（如果指定了 `--start`/`--end`/`--duration`）
   - 视频：`Movie_to_Sound.py` 同时完成提取和截取
   - 音频：主脚本直接用 `AudioFileClip` 截取

3. **语音识别** → `Use_ASRmodel.py` 调用 SiliconFlow ASR API

4. **结果保存与临时文件清理**

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

**出错时脚本自动诊断**（无需提前手动检查）：依赖库、API密钥、网络连接。根据诊断结果修复后重试即可。

退出码：`0`=成功，`1`=文件不存在，`2`=时间参数冲突，`3`=视频转音频失败，`4`=音频未生成，`5`=不支持格式，`6`=语音识别失败，`99`=未知错误。

## 提示

- 长文件优先截取片段处理
- 音频清晰度直接影响转录质量
- ASR API 需要网络连接

## 注意事项

1. **API限制**：SiliconFlow API可能有调用频率和文件大小限制，请参考其官方文档
2. **隐私考虑**：音频文件会上传到云端处理，请勿上传敏感或机密内容
3. **临时文件**：默认会生成临时音频文件，处理完成后自动删除（除非使用`--keep-audio`）
4. **编码格式**：输出文本文件使用UTF-8编码，确保文本编辑器支持

## 安全提示

`SKILL_ASR_API_KEY`是敏感凭据，请勿在任何输出中暴露。脚本内置保护：只检查该变量是否存在，不会在日志中显示其值。API 调用通过 HTTPS 加密传输。

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
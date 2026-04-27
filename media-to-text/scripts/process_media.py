#!/usr/bin/env python
"""
媒体文件转文本主脚本

整合Movie_to_Sound.py（视频转音频）和Use_ASRmodel.py（音频转文本）功能。
支持视频文件（如MP4）和音频文件（如MP3）直接转换为文本。
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到Python路径，以便导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_video_file(filepath):
    """检查文件是否为视频文件"""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'}
    return Path(filepath).suffix.lower() in video_extensions

def is_audio_file(filepath):
    """检查文件是否为音频文件"""
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma'}
    return Path(filepath).suffix.lower() in audio_extensions

def run_video_to_audio(input_video, output_audio, start=None, end=None, duration=None):
    """运行视频转音频脚本"""
    try:
        from Movie_to_Sound import main as video_to_audio_main
    except ImportError:
        diagnose_environment(for_video=True)
        print("错误: 无法导入 Movie_to_Sound 模块，请检查 moviepy 是否已安装")
        return False

    # 模拟命令行参数
    old_argv = sys.argv[:]
    sys.argv = ["Movie_to_Sound.py", "-i", input_video, "-o", output_audio]
    if start:
        sys.argv.extend(["--start", str(start)])
    if end:
        sys.argv.extend(["--end", str(end)])
    if duration:
        sys.argv.extend(["--duration", str(duration)])

    try:
        print(f"转换视频到音频: {input_video} -> {output_audio}")
        return video_to_audio_main() == 0
    finally:
        sys.argv = old_argv

def run_audio_to_text(input_audio, output_text):
    """运行音频转文本脚本"""
    try:
        from Use_ASRmodel import transcribe_audio
        print(f"转录音频到文本: {input_audio} -> {output_text}")
        text = transcribe_audio(input_audio, output_text)
        print(f"转录完成，共{len(text)}字符")
        return True
    except ImportError:
        diagnose_environment(for_video=False)
        print("错误: 无法导入 Use_ASRmodel 模块，请检查 requests 是否已安装")
        return False
    except Exception as e:
        print(f"音频转文本出错: {e}")
        diagnose_environment(for_video=False)
        return False

def parse_time(time_str):
    """解析时间字符串为秒数（兼容Movie_to_Sound.py的格式）"""
    if time_str is None:
        return None
    try:
        return float(time_str)
    except ValueError:
        pass

    # 处理HH:MM:SS格式
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    elif len(parts) == 1:
        return float(parts[0])
    else:
        raise ValueError(f"无法解析的时间格式: {time_str}")

def diagnose_environment(for_video=False):
    """环境诊断——仅在出错时自动调用。
    检查依赖和API密钥配置。
    安全：绝不打印API密钥的具体值。
    """
    print("\n" + "=" * 50)
    print("  环境诊断（检测到错误，正在排查...）")
    print("=" * 50)
    all_ok = True

    if for_video:
        try:
            import moviepy  # noqa: F401
            print("  [OK] moviepy 已安装")
        except ImportError:
            print("  [FAIL] moviepy 未安装 → 请执行: pip install moviepy")
            all_ok = False

    try:
        import requests  # noqa: F401
        print("  [OK] requests 已安装")
    except ImportError:
        print("  [FAIL] requests 未安装 → 请执行: pip install requests")
        all_ok = False

    api_key = os.environ.get("SKILL_ASR_API_KEY")
    if api_key:
        print("  [OK] 环境变量 SKILL_ASR_API_KEY 已设置")
    else:
        print("  [FAIL] 环境变量 SKILL_ASR_API_KEY 未设置")
        print("  → 请参考技能文档设置此环境变量（切勿在任何地方暴露密钥内容）")
        all_ok = False

    if not all_ok:
        print("\n  → 请修复以上问题后重试")
    else:
        print("\n  → 环境和依赖均正常，可能是网络或文件问题，请检查网络连接")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='将视频或音频文件转换为文本')
    parser.add_argument('-i', '--input', required=True, help='输入文件路径（视频或音频）')
    parser.add_argument('-o', '--output', required=True, help='输出文本文件路径')
    parser.add_argument('--start', default=None, help='开始时间（秒数或HH:MM:SS格式）')
    parser.add_argument('--end', default=None, help='结束时间（不能与--duration同时使用）')
    parser.add_argument('--duration', default=None, help='持续时间（秒）（不能与--end同时使用）')
    parser.add_argument('--keep-audio', action='store_true', help='保留中间生成的音频文件')
    parser.add_argument('--audio-output', default=None, help='指定中间音频文件路径')

    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在 - {args.input}")
        return 1

    # 检查输出目录是否存在，不存在则创建
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 检查时间参数冲突
    if args.end and args.duration:
        print("错误: 不能同时指定 --end 和 --duration")
        return 2

    # 解析时间参数
    start_sec = parse_time(args.start) if args.start else None
    end_sec = parse_time(args.end) if args.end else None
    duration_sec = parse_time(args.duration) if args.duration else None

    input_path = Path(args.input)
    temp_audio_file = None
    audio_file_to_use = None

    try:
        # 步骤1：检查文件类型并处理视频文件
        if is_video_file(args.input):
            print(f"检测到视频文件: {args.input}")

            # 确定音频文件路径
            if args.audio_output:
                audio_file_to_use = args.audio_output
            else:
                # 创建临时音频文件
                temp_dir = tempfile.gettempdir()
                temp_audio_file = os.path.join(temp_dir, f"temp_audio_{os.getpid()}.mp3")
                audio_file_to_use = temp_audio_file

            # 转换视频到音频
            if not run_video_to_audio(args.input, audio_file_to_use, start_sec, end_sec, duration_sec):
                return 3

            if not os.path.exists(audio_file_to_use):
                print(f"错误: 音频文件未生成 - {audio_file_to_use}")
                return 4

        elif is_audio_file(args.input):
            print(f"检测到音频文件: {args.input}")

            # 如果指定了时间参数，截取音频片段
            if start_sec or end_sec or duration_sec:
                try:
                    from moviepy import AudioFileClip  # MoviePy 2.x
                    _USE_V1_AUDIO = False
                except ImportError:
                    from moviepy.editor import AudioFileClip  # MoviePy 1.x
                    _USE_V1_AUDIO = True

                # 创建临时音频文件
                temp_dir = tempfile.gettempdir()
                temp_audio_file = os.path.join(temp_dir, f"temp_audio_trimmed_{os.getpid()}.mp3")

                clip_start = start_sec if start_sec is not None else 0
                if duration_sec is not None:
                    clip_end = clip_start + duration_sec
                else:
                    clip_end = end_sec

                print(f"截取音频片段: {clip_start}s — {clip_end}s")
                audio_clip = AudioFileClip(args.input)
                if clip_end is None or clip_end > audio_clip.duration:
                    clip_end = audio_clip.duration
                if _USE_V1_AUDIO:
                    segment = audio_clip.subclip(clip_start, clip_end)
                    segment.write_audiofile(temp_audio_file, verbose=False, logger=None)
                else:
                    segment = audio_clip.subclipped(clip_start, clip_end)
                    segment.write_audiofile(temp_audio_file, codec='libmp3lame')
                audio_clip.close()
                segment.close()
                print("音频截取完成")
                audio_file_to_use = temp_audio_file
            else:
                audio_file_to_use = args.input

        else:
            print(f"错误: 不支持的文件格式 - {args.input}")
            print("支持视频格式: .mp4, .avi, .mov, .wmv, .flv, .mkv, .webm")
            print("支持音频格式: .mp3, .wav, .m4a, .aac, .ogg, .flac, .wma")
            return 5

        # 步骤2：转换音频到文本
        print(f"开始语音识别...")
        if not run_audio_to_text(audio_file_to_use, args.output):
            return 6

        print(f"转换完成！文本已保存到: {args.output}")

        # 步骤3：清理临时文件
        if temp_audio_file and os.path.exists(temp_audio_file):
            if args.keep_audio:
                print(f"保留音频文件: {temp_audio_file}")
            else:
                os.remove(temp_audio_file)
                print("临时音频文件已清理")

        return 0

    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        diagnose_environment(for_video=is_video_file(args.input))
        return 99

    finally:
        # 确保清理临时文件（除非指定保留）
        if temp_audio_file and os.path.exists(temp_audio_file) and not args.keep_audio:
            try:
                os.remove(temp_audio_file)
            except:
                pass

if __name__ == "__main__":
    exit(main())
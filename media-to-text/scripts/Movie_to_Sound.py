#!/usr/bin/env python
"""
视频转 MP3 工具 (基于 MoviePy)

用法示例:
    # 转换整个视频
    python video_to_mp3.py -i input.mp4 -o output.mp3

    # 从第30秒开始，到第2分10秒结束
    python video_to_mp3.py -i input.mp4 -o output.mp3 --start 00:00:30 --end 00:02:10

    # 从第10秒开始，持续60秒
    python video_to_mp3.py -i input.mp4 -o output.mp3 --start 10 --duration 60

    # 只从第1分20秒开始，直到视频末尾
    python video_to_mp3.py -i input.mp4 -o output.mp3 --start 00:01:20
"""

import argparse
import os

try:
    from moviepy.editor import VideoFileClip  # MoviePy 1.x
    MOVIEPY_V2 = False
except ImportError:
    from moviepy import VideoFileClip          # MoviePy 2.x
    MOVIEPY_V2 = True


def subclip(clip, start, end):
    """兼容两个版本的截取方法"""
    if MOVIEPY_V2:
        return clip.subclipped(start, end)
    else:
        return clip.subclip(start, end)


def parse_time(time_str):
    """将时间字符串转换为秒数 (支持 HH:MM:SS 或纯数字)"""
    if time_str is None:
        return None
    try:
        return float(time_str)
    except ValueError:
        pass
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


def main():
    parser = argparse.ArgumentParser(description='将视频文件转换为 MP3 音频')
    parser.add_argument('-i', '--input', required=True, help='输入视频文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出 MP3 文件路径')
    parser.add_argument('--start', default=None, help='开始时间 (例如 00:01:30 或 90.5)')
    parser.add_argument('--end', default=None, help='结束时间 (例如 00:02:00)')
    parser.add_argument('--duration', default=None, help='持续时间（秒）')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在 - {args.input}")
        return 1

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    start_sec = parse_time(args.start) if args.start else None
    end_sec = parse_time(args.end) if args.end else None
    duration_sec = parse_time(args.duration) if args.duration else None

    if args.end and args.duration:
        print("错误: 不能同时指定 --end 和 --duration")
        return 1

    clip = None
    try:
        print(f"正在加载视频: {args.input}")
        print(f"使用 MoviePy {'2.x' if MOVIEPY_V2 else '1.x'}")
        clip = VideoFileClip(args.input)

        if start_sec is not None or end_sec is not None or duration_sec is not None:
            if duration_sec is not None:
                start = start_sec if start_sec is not None else 0
                end = start + duration_sec
                if end > clip.duration:
                    end = clip.duration
                    print(f"警告: 持续时间超出视频长度，自动截取到视频末尾")
                clip = subclip(clip, start, end)
            else:
                start = start_sec if start_sec is not None else 0
                end = end_sec if end_sec is not None else clip.duration
                if start > clip.duration:
                    print(f"错误: 开始时间 ({start}秒) 大于视频长度 ({clip.duration}秒)")
                    return 1
                if end > clip.duration:
                    end = clip.duration
                    print(f"警告: 结束时间超出视频长度，自动截取到视频末尾")
                if start >= end:
                    print("错误: 开始时间不能大于等于结束时间")
                    return 1
                clip = subclip(clip, start, end)

        print(f"正在提取音频并保存为: {args.output}")
        if MOVIEPY_V2:
            clip.audio.write_audiofile(args.output)
        else:
            clip.audio.write_audiofile(args.output, verbose=False, logger=None)
        print("转换完成！")

    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return 1
    finally:
        if clip is not None:
            try:
                clip.close()
            except:
                pass

    return 0


if __name__ == "__main__":
    exit(main())

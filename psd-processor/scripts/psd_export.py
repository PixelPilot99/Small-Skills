#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psd_export_jpg.py
-----------------
将 PSD 批量导出为 JPG 或 PNG（仅使用 psd-tools，不使用 Pillow 读取 PSD 回退逻辑）。

使用方式：
  # 交互式（手动运行）
  python psd_export_jpg.py

  # 命令行参数（agent 调用 / 脚本集成）
  python psd_export_jpg.py -i /path/to/psd -o /path/to/output
  python psd_export_jpg.py -i /path/to/psd -o /path/to/output --format png
  python psd_export_jpg.py -i /path/to/psd -o /path/to/output --format jpg -q 92 --pattern "*.PSD" --no-recursive --silent

依赖：
  pip install psd-tools Pillow
"""

import os
import glob
import argparse


def export_one_psd(psd_path: str, out_path: str, out_format: str = "jpg", quality: int = 95) -> tuple[bool, str]:
    """
    导出单个 PSD -> JPG/PNG（仅 psd-tools）。
    返回: (是否成功, 错误信息)
    """
    try:
        from psd_tools import PSDImage

        fmt = out_format.lower()
        if fmt not in ("jpg", "jpeg", "png"):
            return False, f"不支持的导出格式: {out_format}"

        psd = PSDImage.open(psd_path)
        img = psd.composite()
        if img is None:
            return False, "psd.composite() 返回 None"

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        if fmt in ("jpg", "jpeg"):
            # JPEG 需要 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(out_path, "JPEG", quality=quality, optimize=True)
        else:
            # PNG 保留透明通道（若有）
            if img.mode not in ("RGBA", "RGB", "L", "LA", "P"):
                img = img.convert("RGBA")
            img.save(out_path, "PNG", optimize=True)

        return True, ""
    except Exception as e:
        return False, str(e)


def batch_export(
    input_dir: str,
    output_dir: str,
    out_format: str = "jpg",
    quality: int = 95,
    pattern: str = "*.psd",
    recursive: bool = True,
    verbose: bool = True
):
    """
    批量导出目录中的 PSD 文件为 JPG/PNG。
    """
    os.makedirs(output_dir, exist_ok=True)

    if recursive:
        search_pattern = os.path.join(input_dir, "**", pattern)
        psd_files = glob.glob(search_pattern, recursive=True)
    else:
        search_pattern = os.path.join(input_dir, pattern)
        psd_files = glob.glob(search_pattern)

    if not psd_files:
        print("没有在输入目录找到 PSD 文件")
        return

    fmt = out_format.lower()
    ext = ".png" if fmt == "png" else ".jpg"

    total = len(psd_files)
    success = 0
    failed = 0
    failed_files = []

    if verbose:
        print(f"找到 {total} 个 PSD 文件，开始导出为 {fmt.upper()}...")

    for idx, psd_path in enumerate(psd_files, 1):
        rel_path = os.path.relpath(psd_path, input_dir)
        rel_no_ext = os.path.splitext(rel_path)[0]
        out_path = os.path.join(output_dir, rel_no_ext + ext)

        ok, err = export_one_psd(psd_path, out_path, out_format=fmt, quality=quality)
        if ok:
            success += 1
            if verbose:
                print(f"[OK]    [{idx}/{total}] {rel_path} -> {os.path.relpath(out_path, output_dir)}")
        else:
            failed += 1
            failed_files.append((rel_path, err))
            print(f"[ERROR] [{idx}/{total}] {rel_path} 导出失败：{err}")

    print(f"\n完成：总计 {total}，成功 {success}，失败 {failed}")
    if failed_files:
        print("\n失败文件（最多展示前10个）：")
        for name, err in failed_files[:10]:
            print(f"  - {name}: {err}")


def get_args():
    """
    优先命令行参数；未传时进入交互输入。
    """
    parser = argparse.ArgumentParser(
        description="批量导出 PSD 到 JPG/PNG（仅 psd-tools）"
    )
    parser.add_argument("--input", "-i", default=None, help="PSD 输入目录")
    parser.add_argument("--output", "-o", default=None, help="输出目录")
    parser.add_argument("--format", "-f", default="jpg", choices=["jpg", "jpeg", "png"], help="导出格式：jpg/png，默认jpg")
    parser.add_argument("--quality", "-q", type=int, default=95, help="JPG 质量(1-100)，默认95（PNG忽略）")
    parser.add_argument("--pattern", default="*.psd", help='文件匹配模式，默认 "*.psd"')
    parser.add_argument("--no-recursive", action="store_true", help="仅扫描输入目录，不递归子目录")
    parser.add_argument("--silent", action="store_true", help="静默模式（减少日志）")
    args = parser.parse_args()

    input_dir = args.input or input("请输入 PSD 所在目录：").strip()
    output_dir = args.output or input("请输入输出目录（留空则在输入目录下创建导出目录）：").strip()

    export_format = (args.format or "").lower().strip()
    if not export_format:
        export_format = input("请选择导出格式（jpg/png，默认jpg）：").strip().lower() or "jpg"

    if export_format not in ("jpg", "jpeg", "png"):
        print(f"不支持的格式：{export_format}，将使用默认 jpg")
        export_format = "jpg"

    if not output_dir:
        suffix = "png_output" if export_format == "png" else "jpg_output"
        output_dir = os.path.join(input_dir, suffix)

    # 质量范围保护（仅 JPG 使用）
    quality = max(1, min(100, args.quality))

    return input_dir, output_dir, export_format, quality, args.pattern, (not args.no_recursive), (not args.silent)


def main():
    # 依赖可用性检查
    try:
        import psd_tools  # noqa: F401
    except Exception:
        print("缺少依赖：psd-tools")
        print("请先安装：pip install psd-tools Pillow")
        return

    input_dir, output_dir, export_format, quality, pattern, recursive, verbose = get_args()

    if not os.path.isdir(input_dir):
        print(f"输入目录不存在：{input_dir}")
        return

    batch_export(
        input_dir=input_dir,
        output_dir=output_dir,
        out_format=export_format,
        quality=quality,
        pattern=pattern,
        recursive=recursive,
        verbose=verbose
    )


if __name__ == "__main__":
    main()

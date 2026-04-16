#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psd_export_layers.py
--------------------
将 PSD 的图层分别导出为单独图片（PNG 或 JPG）。

使用方式：
  # 交互式
  python psd_export_layers.py

  # 命令行
  python psd_export_layers.py -i /path/to/psd -o /path/to/output --format png
  python psd_export_layers.py -i /path/to/psd -o /path/to/output --format jpg -q 92 --no-hidden --flat

依赖：
  pip install psd-tools Pillow
"""

import os
import re
import glob
import argparse
from typing import List, Tuple


def safe_name(name: str) -> str:
    """清理文件名非法字符"""
    name = name.strip() if name else "unnamed"
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:120] if len(name) > 120 else name


def iter_layers(psd, include_hidden=True, flat=True, prefix="") -> List[Tuple[object, str]]:
    """
    遍历图层，返回 [(layer, layer_path_name), ...]
    flat=True: 递归展开所有子层
    flat=False: 仅顶层
    """
    result = []

    def walk(parent, path_prefix=""):
        for layer in parent:
            # hidden 过滤
            if (not include_hidden) and (not layer.is_visible()):
                continue

            lname = safe_name(layer.name or "unnamed")
            full_name = f"{path_prefix}__{lname}" if path_prefix else lname

            # group 也可能有可渲染内容，但通常我们导出像素层即可
            # 为了简单：有像素内容就导；group 的内容靠子层导出
            if not layer.is_group():
                result.append((layer, full_name))

            if flat and layer.is_group():
                walk(layer, full_name)

    if flat:
        walk(psd, prefix)
    else:
        for layer in psd:
            if (not include_hidden) and (not layer.is_visible()):
                continue
            lname = safe_name(layer.name or "unnamed")
            if not layer.is_group():
                result.append((layer, lname))

    return result


def export_layer_image(layer, out_path: str, out_format: str = "png", quality: int = 95) -> Tuple[bool, str]:
    """导出单个图层"""
    try:
        img = layer.topil()
        if img is None:
            return False, "layer.topil() 返回 None"

        out_format = out_format.lower()
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        if out_format == "png":
            # 保留透明
            img.save(out_path, "PNG", optimize=True)
        elif out_format in ("jpg", "jpeg"):
            # JPG 不支持透明，转白底
            if img.mode in ("RGBA", "LA"):
                bg = img.convert("RGBA")
                from PIL import Image
                white = Image.new("RGB", bg.size, (255, 255, 255))
                white.paste(bg, mask=bg.split()[-1])
                img = white
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.save(out_path, "JPEG", quality=quality, optimize=True)
        else:
            return False, f"不支持格式: {out_format}"

        return True, ""
    except Exception as e:
        return False, str(e)


def process_one_psd(psd_path: str, output_dir: str, out_format="png", quality=95, include_hidden=True, flat=True, verbose=True):
    """处理单个 PSD，返回统计 dict"""
    from psd_tools import PSDImage

    psd_name = os.path.splitext(os.path.basename(psd_path))[0]
    psd_out_dir = os.path.join(output_dir, safe_name(psd_name))
    os.makedirs(psd_out_dir, exist_ok=True)

    psd = PSDImage.open(psd_path)
    layers = iter_layers(psd, include_hidden=include_hidden, flat=flat)

    stats = {
        "file": psd_path,
        "total_layers": len(layers),
        "success": 0,
        "failed": 0,
        "failed_layers": []
    }

    if verbose:
        print(f"\n处理: {os.path.basename(psd_path)}")
        print(f"图层数: {len(layers)}")

    for idx, (layer, lname) in enumerate(layers, 1):
        ext = "jpg" if out_format.lower() in ("jpg", "jpeg") else "png"
        out_name = f"{idx:03d}_{safe_name(lname)}.{ext}"
        out_path = os.path.join(psd_out_dir, out_name)

        ok, err = export_layer_image(layer, out_path, out_format=out_format, quality=quality)
        if ok:
            stats["success"] += 1
            if verbose:
                print(f"[OK]    {idx:03d} {layer.name}")
        else:
            stats["failed"] += 1
            stats["failed_layers"].append((layer.name, err))
            print(f"[ERROR] {idx:03d} {layer.name} -> {err}")

    return stats


def batch_process(input_dir: str, output_dir: str, pattern="*.psd", out_format="png", quality=95, include_hidden=True, flat=True, recursive=True, verbose=True):
    """批量处理目录"""
    os.makedirs(output_dir, exist_ok=True)

    if recursive:
        files = glob.glob(os.path.join(input_dir, "**", pattern), recursive=True)
    else:
        files = glob.glob(os.path.join(input_dir, pattern))

    if not files:
        print("没有找到 PSD 文件")
        return

    total_files = len(files)
    ok_files = 0
    fail_files = 0
    total_layers = 0
    total_success = 0
    total_failed = 0

    print(f"找到 {total_files} 个 PSD，开始导出图层...")

    for i, psd_path in enumerate(files, 1):
        print(f"\n=== [{i}/{total_files}] ===")
        try:
            s = process_one_psd(
                psd_path=psd_path,
                output_dir=output_dir,
                out_format=out_format,
                quality=quality,
                include_hidden=include_hidden,
                flat=flat,
                verbose=verbose
            )
            total_layers += s["total_layers"]
            total_success += s["success"]
            total_failed += s["failed"]
            ok_files += 1
        except Exception as e:
            fail_files += 1
            print(f"[FILE ERROR] {os.path.basename(psd_path)}: {e}")

    print("\n======== 完成 ========")
    print(f"PSD 文件总数: {total_files}")
    print(f"处理成功文件: {ok_files}")
    print(f"处理失败文件: {fail_files}")
    print(f"图层总数: {total_layers}")
    print(f"导出成功: {total_success}")
    print(f"导出失败: {total_failed}")


def get_args():
    parser = argparse.ArgumentParser(description="将 PSD 图层分别导出为 PNG/JPG")
    parser.add_argument("--input", "-i", default=None, help="PSD 输入目录")
    parser.add_argument("--output", "-o", default=None, help="输出目录")
    parser.add_argument("--format", "-f", default="png", choices=["png", "jpg", "jpeg"], help="导出格式")
    parser.add_argument("--quality", "-q", type=int, default=95, help="JPG质量(1-100)")
    parser.add_argument("--pattern", default="*.psd", help='文件匹配模式，默认 "*.psd"')
    parser.add_argument("--no-hidden", action="store_true", help="不导出隐藏图层")
    parser.add_argument("--top-only", action="store_true", help="只导出顶层，不递归子图层")
    parser.add_argument("--no-recursive", action="store_true", help="输入目录不递归")
    parser.add_argument("--silent", action="store_true", help="减少日志输出")
    args = parser.parse_args()

    input_dir = args.input or input("请输入 PSD 所在目录：").strip()
    output_dir = args.output or input("请输入输出目录（留空则在输入目录下创建 layers_output 子目录）：").strip()
    if not output_dir:
        output_dir = os.path.join(input_dir, "layers_output")

    quality = max(1, min(100, args.quality))
    include_hidden = not args.no_hidden
    flat = not args.top_only
    recursive = not args.no_recursive
    verbose = not args.silent

    return input_dir, output_dir, args.pattern, args.format, quality, include_hidden, flat, recursive, verbose


def main():
    try:
        import psd_tools  # noqa
        from PIL import Image  # noqa
    except Exception:
        print("缺少依赖，请安装：pip install psd-tools Pillow")
        return

    input_dir, output_dir, pattern, out_format, quality, include_hidden, flat, recursive, verbose = get_args()

    if not os.path.isdir(input_dir):
        print(f"输入目录不存在：{input_dir}")
        return

    batch_process(
        input_dir=input_dir,
        output_dir=output_dir,
        pattern=pattern,
        out_format=out_format,
        quality=quality,
        include_hidden=include_hidden,
        flat=flat,
        recursive=recursive,
        verbose=verbose
    )


if __name__ == "__main__":
    main()

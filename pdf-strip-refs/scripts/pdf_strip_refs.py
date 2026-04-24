"""
pdf_strip_refs.py
-----------------
去除 PDF 文献中的参考文献部分，用于 RAG 预处理。

使用方式：
  # 交互式（手动运行）
  python pdf_strip_refs.py

  # 命令行参数（agent 调用 / 脚本集成）
  python pdf_strip_refs.py -i /path/to/pdfs -o /path/to/output

依赖：
  pip install pymupdf
"""

import os
import glob
import argparse
import fitz  # pymupdf


REF_MARKERS = [
    "References",
    "REFERENCES",  
    "Bibliography",
    "BIBLIOGRAPHY",
    "参考文献",
]


def find_ref_position(page: fitz.Page):
    """
    在页面文字块中查找参考文献标题。
    只匹配"整个 block 就是关键词"的情况，避免误判正文中出现的单词。
    返回 (True, y坐标) 或 (False, None)。
    """
    blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
    for b in blocks:
        text = b[4].strip()
        if text in REF_MARKERS:
            return True, b[1]  # y0 坐标
    return False, None


def strip_references(in_pdf: str, out_pdf: str) -> bool:
    """
    处理单个 PDF：找到参考文献起始位置后，
    永久删除该位置以下的所有内容（含后续页），保存到 out_pdf。
    返回 True 表示做了截断，False 表示未找到参考文献标题。
    """
    doc = fitz.open(in_pdf)
    cut_page = len(doc)
    cut_y = None

    for i, page in enumerate(doc):
        found, y = find_ref_position(page)
        if found:
            cut_page = i
            cut_y = y
            break

    # 没找到参考文献标题，原样保存
    if cut_page == len(doc):
        doc.save(out_pdf)
        doc.close()
        return False

    # 1. 在 cut_page 页上 redact 掉 cut_y 以下的所有内容（永久从文本层删除）
    page = doc[cut_page]
    rect = fitz.Rect(0, cut_y, page.rect.width, page.rect.height)
    page.add_redact_annot(rect)
    page.apply_redactions()

    # 2. 删除 cut_page 之后的所有页（从后往前删，避免索引偏移）
    for i in range(len(doc) - 1, cut_page, -1):
        doc.delete_page(i)

    # 3. 如果 cut_page 这页 redact 后已无文字，也一并删掉
    if not doc[cut_page].get_text().strip():
        doc.delete_page(cut_page)

    doc.save(out_pdf)
    doc.close()
    return True


def batch_strip(input_dir: str, output_dir: str):
    """批量处理目录下所有 PDF。"""
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print("没有在输入目录找到 .pdf 文件")
        return

    ok = skipped = failed = 0
    for pdf_path in pdf_files:
        name = os.path.splitext(os.path.basename(pdf_path))[0]
        out_path = os.path.join(output_dir, name + "_no_refs.pdf")
        try:
            cut = strip_references(pdf_path, out_path)
            if cut:
                print(f"[OK]      {name}.pdf  →  {name}_no_refs.pdf")
                ok += 1
            else:
                print(f"[SKIP]    {name}.pdf  未找到参考文献标题，已原样复制")
                skipped += 1
        except Exception as e:
            print(f"[ERROR]   {name}.pdf  出错：{e}")
            failed += 1

    print(f"\n完成：{ok} 个截断，{skipped} 个未找到标题，{failed} 个出错")


def get_paths() -> tuple[str, str]:
    """
    优先读取命令行参数（供 agent / 脚本调用），
    未传参时退回到交互式 input()（供手动运行）。
    """
    parser = argparse.ArgumentParser(
        description="去除 PDF 参考文献，用于 RAG 预处理（基于 pymupdf）"
    )
    parser.add_argument("--input",  "-i", help="PDF 输入目录", default=None)
    parser.add_argument("--output", "-o", help="处理后的输出目录", default=None)
    args = parser.parse_args()

    if not args.input:
        raise ValueError("必须提供 -i/--input 参数（PDF 输入目录）")

    input_dir  = args.input.strip()
    output_dir = (args.output or os.path.join(input_dir, "no_refs")).strip()

    return input_dir, output_dir


if __name__ == "__main__":
    input_dir, output_dir = get_paths()
    batch_strip(input_dir, output_dir)

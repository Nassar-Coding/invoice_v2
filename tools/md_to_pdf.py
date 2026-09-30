"""Render a short Markdown document (headings, paragraphs, bullet lists, tables, bold/italic/code spans) to PDF with
PyMuPDF's Story (a pinned dependency; no other tool needed). Used for the report deliverables.

Usage::  python tools/md_to_pdf.py INPUT.md OUTPUT.pdf
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import pymupdf

CSS = """
body { font-family: sans-serif; font-size: 9.5pt; line-height: 1.3; }
h1 { font-size: 15pt; margin: 0 0 6pt 0; }
h2 { font-size: 11.5pt; margin: 9pt 0 3pt 0; }
h3 { font-size: 10pt; margin: 7pt 0 2pt 0; }
p { margin: 0 0 4pt 0; }
ul { margin: 0 0 4pt 0; }
li { margin: 0 0 1pt 0; }
table { border-collapse: collapse; margin: 2pt 0 6pt 0; }
th, td { border: 0.5pt solid #888; padding: 1.5pt 3pt; font-size: 8.5pt; vertical-align: top; }
th { background-color: #e8e8e8; }
code { font-family: monospace; font-size: 8.5pt; }
"""


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s


def to_html(md: str) -> str:
    out, para, lst, tbl = [], [], [], []

    def flush_text():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + "</ul>")
            lst.clear()

    def flush_table():
        rows = [r for r in tbl if not set(r.replace("|", "").strip()) <= set("-: ")]
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        if cells:
            h = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f"<table><tr>{h}</tr>{b}</table>")
        tbl.clear()

    for line in md.splitlines():
        s = line.rstrip()
        if s.lstrip().startswith("|"):
            flush_text()
            tbl.append(s)
            continue
        if tbl:
            flush_table()
        if not s.strip():
            flush_text()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            flush_text()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", s)
        if m:
            if para:
                out.append("<p>" + inline(" ".join(para)) + "</p>")
                para.clear()
            lst.append(m.group(1))
            continue
        if lst and s.startswith("  "):
            lst[-1] += " " + s.strip()
            continue
        if lst:
            flush_text()
        para.append(s.strip())
    flush_text()
    if tbl:
        flush_table()
    return "<body>" + "".join(out) + "</body>"


def render(md_path: Path, pdf_path: Path) -> int:
    story = pymupdf.Story(html=to_html(md_path.read_text()), user_css=CSS)
    writer = pymupdf.DocumentWriter(str(pdf_path))
    rect = pymupdf.paper_rect("a4")
    where = rect + (40, 40, -40, -40)
    pages = 0
    more = True
    while more:
        dev = writer.begin_page(rect)
        more, _filled = story.place(where)
        story.draw(dev)
        writer.end_page()
        pages += 1
    writer.close()
    # deterministic metadata (no creation timestamps) so the PDF regenerates byte-identically
    doc = pymupdf.open(str(pdf_path))
    doc.set_metadata({"title": md_path.stem.replace("_", " "), "author": "", "subject": "", "keywords": "",
                      "creator": "tools/md_to_pdf.py", "producer": "PyMuPDF", "creationDate": "", "modDate": ""})
    doc.save(str(pdf_path) + ".tmp", garbage=3, deflate=True, no_new_id=True)
    doc.close()
    Path(str(pdf_path) + ".tmp").replace(pdf_path)
    return pages


def main() -> int:
    n = render(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{sys.argv[2]}: {n} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

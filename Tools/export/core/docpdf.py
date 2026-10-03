"""Pass 6 (spec 6): pdf/Machine_Brigade_Design_<date>.pdf rendered from md/Machine_Brigade_Design_FULL_<date>.md.

No hand-written text: the PDF is the FULL.md through a small Markdown-to-HTML step (headings, paragraphs, lists, tables,
pictures, **bold**, `code`) and PyMuPDF's Story layout, with the repo's Barlow font (Vietnamese; Inter's contextual
hyphen glyphs extract as private-use characters, so a number could not be found in the text). Pictures are shrunk to
JPEG in memory (the copies in images/ stay as they are). Fixed metadata and no new file id: the same md gives the same
bytes. Without PyMuPDF (pip install pymupdf) the PDF is skipped and the run says so.
"""
from __future__ import annotations

import html
import io
import re
from pathlib import Path

from . import repo

FONTS = repo.ROOT / "Assets" / "MachineBrigade" / "Resources" / "Fonts"
PAGE_W, PAGE_H, MARGIN = 595, 842, 36  # A4 in points
PIC_W = 1100
ZWSP = chr(0x200B)  # zero-width space
CSS = """
@font-face {font-family: Barlow; src: url(Barlow-Regular.ttf);}
@font-face {font-family: Barlow; src: url(Barlow-SemiBold.ttf); font-weight: bold;}
@font-face {font-family: Mono; src: url(JetBrainsMono-Medium.ttf);}
body {font-family: Barlow; font-size: 9pt; line-height: 1.3;}
h1 {font-size: 17pt; margin: 0 0 6pt 0;}
h2 {font-size: 13pt; margin: 12pt 0 4pt 0; color: #1f3d3d;}
h3 {font-size: 11pt; margin: 9pt 0 3pt 0; color: #1f3d3d;}
h4 {font-size: 9.5pt; margin: 7pt 0 2pt 0;}
h5, h6 {font-size: 8.5pt; margin: 5pt 0 2pt 0;}
p {margin: 0 0 4pt 0;}
ul {margin: 0 0 4pt 12pt;}
li {margin: 0 0 1pt 0;}
code {font-family: Mono; font-size: 7.5pt;}
table {border-collapse: collapse; margin: 0 0 6pt 0; font-size: 6.2pt;}
th {font-weight: bold; text-align: left; padding: 1pt 2pt; border: 0.4pt solid #888888;}
td {padding: 1pt 2pt; border: 0.4pt solid #bbbbbb; vertical-align: top;}
.cap {font-size: 7.5pt; color: #444444;}
"""


def available() -> bool:
    try:
        import pymupdf  # noqa: F401
        return True
    except ImportError:
        return False


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    return s


def _breakable(s: str) -> str:
    """A zero-width space after '_', '/' and ';' so a long id or header wraps inside its cell: a table wider than the
    page would lose its right-hand columns."""
    return re.sub(r"([_/;])(?=[^<>]*(?:<|$))", lambda m: m.group(1) + ZWSP, s)


def md_to_html(text: str, pictures: dict) -> str:
    """pictures: {md picture path: (archive name, width pt, height pt)}."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("<!--"):
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
            i += 1
            continue
        m = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", line)
        if m:
            pic = pictures.get(m.group(2))
            if pic:
                out.append(f'<p><img src="{pic[0]}" width="{pic[1]}" height="{pic[2]}"/></p>')
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><tr>" + "".join(f"<th>{_breakable(_inline(h))}</th>" for h in head) + "</tr>"]
            t += ["<tr>" + "".join(f"<td>{_breakable(_inline(c))}</td>" for c in r) + "</tr>" for r in rows]
            out.append("".join(t) + "</table>")
            continue
        if line.startswith("- ") or line.startswith("  - "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  - ")):
                items.append(f"<li>{_inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if not line.strip():
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|!\[|\||- |<!--)", lines[i]):
            para.append(lines[i])
            i += 1
        cls = ' class="cap"' if para[0].startswith("*Hình:") else ""
        out.append(f"<p{cls}>{_inline(' '.join(para))}</p>")
    return "\n".join(out)


def _shrink(path: Path) -> tuple[bytes, int, int]:
    from PIL import Image
    im = Image.open(path)
    if im.width > PIC_W:
        im = im.resize((PIC_W, round(im.height * PIC_W / im.width)), Image.LANCZOS)
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bg.paste(im, mask=im.split()[3] if im.mode == "RGBA" else None)
    buf = io.BytesIO()
    bg.save(buf, "JPEG", quality=80, optimize=True)
    return buf.getvalue(), im.width, im.height


def render(md_path: Path, pdf_path: Path, date: str, commit: str) -> int:
    """Writes the PDF; returns its page count."""
    import pymupdf
    text = md_path.read_text("utf-8")
    archive = pymupdf.Archive()
    archive.add(str(FONTS))
    pictures = {}
    for rel in sorted(set(re.findall(r"^!\[.*?\]\((.+?)\)\s*$", text, flags=re.M))):
        src = (md_path.parent / rel).resolve()
        if not src.exists():
            continue
        data, w, h = _shrink(src)
        name = "pic_" + re.sub(r"[^A-Za-z0-9_.]", "_", rel.replace("../images/", "")) + ".jpg"
        archive.add(data, name)
        width = PAGE_W - 2 * MARGIN
        pictures[rel] = (name, width, round(h * width / w))
    body = md_to_html(text, pictures)
    story = pymupdf.Story(html=f"<html><body>{body}</body></html>", user_css=CSS, archive=archive)
    where = pymupdf.Rect(MARGIN, MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN)
    heads = []

    def rectfn(rect_num, filled):
        return pymupdf.Rect(0, 0, PAGE_W, PAGE_H), where, None

    def posfn(pos):
        if pos.heading and pos.heading <= 3 and (pos.open_close & 1) and pos.text:
            heads.append((pos.heading, re.sub(r"\s+", " ", pos.text).strip()[:120], pos.page_num))

    doc = story.write_with_links(rectfn, posfn)
    toc, last = [], 0
    for lvl, title, page in heads:
        lvl = min(lvl, last + 1) if toc else 1
        toc.append([lvl, title, page])
        last = lvl
    if toc:
        doc.set_toc(toc)
    stamp = "D:" + date.replace("-", "") + "000000Z"
    doc.set_metadata({"title": f"Machine Brigade — Tài liệu thiết kế {date}", "author": "Tools/export",
                      "subject": f"commit {commit}", "creator": "Tools/export/core/docpdf.py", "producer": "PyMuPDF",
                      "creationDate": stamp, "modDate": stamp, "keywords": "", "trapped": ""})
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    data = doc.tobytes(garbage=3, deflate=True, no_new_id=True)
    pages = doc.page_count
    doc.close()
    pdf_path.write_bytes(data)
    return pages

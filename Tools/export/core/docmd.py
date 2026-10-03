"""The design review's prose and pictures (Docs/Machine_Brigade_Design_Review.html, the build of Tools/docs/build_doc.py):
read_review turns its sections into blocks, apply_fixes corrects the text against the code (doc_parts.FIXES), and
picture_plan names the pictures the parts show. packdoc.py writes the md of the pack from them."""
from __future__ import annotations

import collections
import re
import shutil
from pathlib import Path

from . import doc_parts as DP
from . import repo
from .diff import load_export, number

MAX_ROWS, HEAD_ROWS, MAX_COLS, MAX_TEXT = 40, 15, 10, 60
SKIP_COLS = {"raw_json", "nguon"}
PIC_EXT = (".png", ".jpg", ".jpeg")
FX_PICS = ("impact_0.5s.png", "fire_0.2s.png")


def full_name(date: str) -> str:
    return f"Machine_Brigade_Design_FULL_{date}.md"


# ------------------------------------------------------------------------------------------------- the design review
def _inline(node) -> str:
    from bs4 import NavigableString, Tag
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    if node.name in ("img", "table", "style", "script"):
        return ""
    if node.name == "br":
        return " "
    inner = "".join(_inline(c) for c in node.children)
    if node.name in ("b", "strong") and inner.strip():
        return f"**{inner.strip()}** "
    if node.name == "code" and inner.strip():
        return f"`{inner.strip()}`"
    if node.name == "div":
        return inner + " "
    return inner


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\*\*\s+\*\*", " ", s)
    return re.sub(r"\s+([,.;:)])", r"\1", s)


def _text_table(t) -> list[str] | None:
    """A table of the review kept as text when under 30 % of its cells are numbers; a number table returns None (the
    sheets hold those numbers)."""
    rows = [[_clean(_inline(c)) for c in tr.find_all(["th", "td"])] for tr in t.find_all("tr")]
    rows = [r for r in rows if any(r)]
    cells = [c for r in rows[1:] for c in r if c]
    if not rows or not cells or len(rows) > 60:
        return None
    nums = sum(1 for c in cells if re.fullmatch(r"[-+−]?[\d.,%× ]+(?:\s*(?:m|s|CP|%|m/s))?", c))
    if nums / len(cells) >= 0.3:
        return None
    width = max(len(r) for r in rows)
    out = []
    for i, r in enumerate(rows):
        r = r + [""] * (width - len(r))
        out.append("| " + " | ".join(_cell(c, 200) for c in r) + " |")
        if i == 0:
            out.append("|" + "---|" * width)
    return out + [""]


def _picture_of(src: str) -> Path | None:
    """The review's picture (a cache name '<folder>_<stem>.jpg') back to its repo file, when the repo has it."""
    name = re.sub(r".*[/\\]", "", src)
    m = re.match(r"(r6|shots)_(.+)\.(?:jpg|png)$", name)
    if not m:
        return None
    p = repo.ROOT / "Docs" / "doc-images" / m.group(1) / f"{m.group(2)}.png"
    return p if p.exists() else None


def _blocks(node, out: list, stats: dict):
    """The review's HTML under one <h2> as Markdown blocks: ('h', level, text), ('p', text), ('li', text),
    ('table', lines), ('img', Path, caption)."""
    from bs4 import NavigableString, Tag
    for c in node.children:
        if isinstance(c, NavigableString):
            if c.strip():
                out.append(("p", _clean(str(c))))
            continue
        if not isinstance(c, Tag):
            continue
        cls = set(c.get("class") or [])
        if c.name == "h2":
            continue
        if c.name in ("h3", "h4"):
            out.append(("h", 3 if c.name == "h3" else 4, _clean(c.get_text(" "))))
        elif c.name == "table":
            t = _text_table(c)
            if t:
                out.append(("table", t))
            else:
                stats["number_tables"] += 1
        elif c.name == "img":
            p = _picture_of(c.get("src", ""))
            cap = c.find_next_sibling()
            caption = _clean(cap.get_text(" ")) if cap is not None and "caption" in (cap.get("class") or []) else ""
            if p:
                out.append(("img", p, caption or c.get("alt", "")))
            else:
                stats["pictures_outside"] += 1
        elif "caption" in cls:
            prev = c.find_previous_sibling()
            if prev is not None and prev.name == "img":
                continue  # printed with its picture (or dropped with it)
            out.append(("p", "*" + _clean(c.get_text(" ")) + "*"))
        elif "card" in cls:
            stats["cards"] += 1  # unit cards: the stats are in the sheets, the guide text comes from the strings
        elif "galcell" in cls:
            stats["pictures_outside"] += 1
        elif c.name in ("ul", "ol"):
            for li in c.find_all("li", recursive=False):
                t = _clean(_inline(li))
                if t:
                    out.append(("li", t))
        elif c.name == "p" or cls & {"note", "guide", "behav", "kicker"}:
            t = _clean(_inline(c))
            if t:
                out.append(("p", t))
        elif c.name in ("div", "span", "small", "section"):
            _blocks(c, out, stats)
        else:
            t = _clean(_inline(c))
            if t:
                out.append(("p", t))


def read_review(path: Path) -> tuple[dict, dict]:
    """{h2 title: [blocks]} of the design review, and counters."""
    stats = {"number_tables": 0, "pictures_outside": 0, "cards": 0, "missing": ""}
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        stats["missing"] = "beautifulsoup4 chưa cài: văn bản của tài liệu thiết kế không đọc được"
        return {}, stats
    if not path.exists():
        stats["missing"] = f"{path.name} không có"
        return {}, stats
    soup = BeautifulSoup(path.read_text("utf-8"), "html.parser")
    secs = {}
    for div in soup.find_all("div", class_="section"):
        if not div.h2:
            continue
        title = _clean(div.h2.get_text(" "))
        blocks: list = []
        _blocks(div, blocks, stats)
        secs.setdefault(title, []).extend(blocks)
    return secs, stats


def apply_fixes(text: str, counts: dict) -> str:
    for pat, repl, _why in DP.FIXES:
        n = len(re.findall(pat, text))
        counts[pat] = counts.get(pat, 0) + n
        if repl is not None and n:
            text = re.sub(pat, repl, text)
    return text


# ----------------------------------------------------------------------------------------------------------- tables
def _cell(v, limit=MAX_TEXT) -> str:
    s = str(v).replace("|", "/").replace("\r", " ").replace("\n", " ").strip()
    if number(s) is not None:
        return s
    return s if len(s) <= limit else s[:limit - 1].rstrip() + "…"


# ---------------------------------------------------------------------------------------------------------- pictures
FOLDER_CAPTIONS = {
    "before_after.png": "{m}: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)",
    "unity_scan.png": "{m}: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận)",
    "kit35_catalog.png": "bộ chi tiết kit35: 70 chi tiết dựng model (Tools/blender/mb_kit35.py; số đo ở 10_model_tai_san/Kit_chi_tiet)",
}


def export_name(src: Path) -> str:
    """The picture's file name under images/<file>/: its folder and name joined ('r6_flame.png', 'tier_T3_fire_0.2s.png')."""
    return "_".join(src.parts[-2:])


def folder_files(folder: Path) -> list[Path]:
    return [p for p in sorted(folder.rglob("*")) if p.suffix.lower() in PIC_EXT] if folder.is_dir() else []


def folder_caption(p: Path) -> str:
    t = FOLDER_CAPTIONS.get(p.name)
    return t.format(m=p.parent.name) if t else p.relative_to(repo.ROOT).as_posix()


def fx_found(root: Path | None) -> list[Path]:
    """The Unity effect shots section 20b prints: tier_T*/impact_0.5s.png and fire_0.2s.png of an --effect-shots folder."""
    found = []
    if root and root.is_dir():
        for d in sorted(root.glob("tier_T*")):
            found += [d / name for name in FX_PICS if (d / name).exists()]
    return found


_REVIEW: dict = {}


def picture_plan(fids: dict, effect_shots: Path | None = None) -> list[dict]:
    """Every picture the md of pass 6 shows, in the order Doc places them (one per images/<file>/<name>), without
    writing anything: {src, rel, part, title, caption, kind}; kind = review (the design review's picture), folder
    (doc_parts pictures), fx (the Unity effect shots of 20b). fids: {"10": "10_model_tai_san", ...}. The domain
    module 10 lists it in 10_model_tai_san/Anh_chup."""
    path = repo.ROOT / DP.DESIGN_HTML
    if path not in _REVIEW:
        _REVIEW[path] = read_review(path)[0]
    review = _REVIEW[path]
    seen, out = set(), []

    def add(src, part, caption, kind, skip_seen=False):
        rel = f"images/{fids.get(part['domain'], part['domain'])}/{export_name(src)}"
        if rel in seen and skip_seen:
            return
        out.append(dict(src=src, rel=rel, part=part["num"], title=part["title"], caption=caption, kind=kind,
                        first=rel not in seen))
        seen.add(rel)

    for part in DP.PARTS:
        for prefix in part.get("html", []):
            for t in (t for t in review if t.startswith(prefix)):
                for b in review[t]:
                    if b[0] == "img":
                        add(b[1], part, apply_fixes(b[2], {}), "review")
        for folder in part.get("pictures", []):
            for p in folder_files(repo.ROOT / folder):
                add(p, part, folder_caption(p), "folder", skip_seen=True)
        if part.get("fx"):
            for p in fx_found(effect_shots):
                add(p, part, f"{p.parent.name} {p.stem}", "fx")
    return out



"""Pass 6 (spec 6): md/<file>.md for files 01-12, md/Machine_Brigade_Design_FULL_<date>.md, images/<file>/.

Sources: the written csv/ (read back, so a table prints the very cell the csv and xlsx hold, and a later column or sheet
shows up by itself), the design review's prose (Docs/Machine_Brigade_Design_Review.html, the build of Tools/docs/build_doc.py;
its number tables are left out because the sheets replace them, its text tables are kept), the in-game guide strings
(10_model_tai_san/Dia_phuong_hoa guide.<id>), repo reports named in doc_parts.PARTS and the pictures of Docs/doc-images and
Docs/models/rebuild. The section list and the text fixes against the code are in doc_parts.py. No clock in any file: the
same data gives the same bytes. The PDF (docpdf.py) is rendered from FULL.md.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from . import doc_parts as DP
from . import repo
from .diff import load_export, number

MAX_ROWS, HEAD_ROWS, MAX_COLS, MAX_TEXT = 40, 15, 10, 60
SKIP_COLS = {"raw_json", "nguon"}
MARK = re.compile(r"^(CHUA_AP:prompt_[\w.]+|NEED_CODE_CHECK|NEED_SOURCE|KHONG_CO|KHONG_CHAY)$")
PIC_EXT = (".png", ".jpg", ".jpeg")
FX_PICS = ("impact_0.5s.png", "fire_0.2s.png")
SELF_CHECK_START, SELF_CHECK_END = "<!-- SELF_CHECK -->", "<!-- /SELF_CHECK -->"


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


def sheet_status(rows: list, header: list) -> tuple[str, str]:
    """('da' | 'mot_phan' | 'chua', the marker that says why)."""
    if not rows:
        return "chua", "sheet rỗng"
    marks = [v for r in rows for v in r if MARK.match(v or "")]
    marker_only = all(any(MARK.match(v or "") for v in r) for r in rows) and len(rows) <= 3 and all(
        r[0] in ("chua_ap", "") or any(MARK.match(v or "") for v in r[1:3]) for r in rows)
    first = next((m for m in marks if m.startswith("CHUA_AP")), marks[0] if marks else "")
    if marker_only:
        return ("mot_phan" if first == "NEED_CODE_CHECK" else "chua"), first
    if any(m.startswith("CHUA_AP") for m in marks):
        return "mot_phan", first
    return "da", ""


def _why(mark: str) -> str:
    if mark.startswith("CHUA_AP:prompt_"):
        return "chờ prompt " + mark.split("prompt_", 1)[1]
    return {"KHONG_CO": "không có trong mã và dữ liệu", "NEED_CODE_CHECK": "cần đọc mã (NEED_CODE_CHECK)",
            "sheet rỗng": "sheet rỗng"}.get(mark, mark)


def table_md(fid: str, sheet: str, header: list, rows: list, names: dict) -> list[str]:
    vi = names.get((fid, sheet), "")
    title = f"{fid}/{sheet}"
    if not rows:
        return [f"Sheet (rỗng): {title}{' — ' + vi if vi else ''}: 0 dòng.", ""]
    shown = rows if len(rows) <= MAX_ROWS else rows[:HEAD_ROWS]
    cols = [i for i, c in enumerate(header) if i == 0 or (c not in SKIP_COLS and not c.endswith(("_truoc", "_sau"))
                                                         and any(i < len(r) and r[i] != "" for r in shown))]
    rest = len(cols) - 1 - (MAX_COLS - 1) if len(cols) > MAX_COLS else 0
    cols = cols[:MAX_COLS]
    lines = [f"Sheet: {title}" + (f" — {vi}" if vi else "") + f" ({len(rows)} dòng, {len(header)} cột)", ""]
    lines.append("| " + " | ".join(header[i] for i in cols) + " |")
    lines.append("|" + "---|" * len(cols))
    for r in shown:
        lines.append("| " + " | ".join(_cell(r[i]) if i < len(r) else "" for i in cols) + " |")
    notes = []
    if len(rows) > MAX_ROWS:
        notes.append(f"{HEAD_ROWS} / {len(rows)} dòng đầu: xem sheet {title}")
    if rest:
        notes.append(f"in {len(cols)} / {len(header)} cột; {rest} cột khác (và raw_json, nguon): xem sheet")
    lines += [""] + ([("*" + "; ".join(notes) + ".*"), ""] if notes else [])
    return lines


# ---------------------------------------------------------------------------------------------------------- builder
class Doc:
    def __init__(self, out: Path, meta: dict, effect_shots: Path | None = None, review: Path | None = None):
        self.out, self.meta = out, meta
        self.books, _, _ = load_export(out)
        self.fids = {fid[:2]: fid for fid in self.books if re.match(r"\d\d_", fid) and not fid.startswith("00_")}
        self.names = {}
        for r in self._dicts("00_chi_muc", "Muc_luc_sheet"):
            self.names[(r.get("file", ""), r.get("sheet", ""))] = r.get("ten_viet", "")
        self.file_titles = {r.get("id", ""): r for r in self._dicts("00_chi_muc", "Muc_luc_file")}
        self.review_path = review or repo.ROOT / DP.DESIGN_HTML
        self.review, self.review_stats = read_review(self.review_path)
        self.effect_shots = effect_shots
        self.fix_counts: dict = {}
        self.used_html: set = set()
        self.used_sheets: set = set()
        self.pictures: list = []  # (images/<file>/<name>, source label)
        self.guide = {r["id"][6:]: r.get("vi", "") for r in self._dicts("10_model_tai_san", "Dia_phuong_hoa")
                      if r.get("id", "").startswith("guide.")}
        self.short = {r["id"][6:]: r.get("vi", "") for r in self._dicts("10_model_tai_san", "Dia_phuong_hoa")
                      if r.get("id", "").startswith("short.")}
        self.statuses: list = []  # (num, title, status text)

    def _dicts(self, fid, sheet):
        h, rows = self.books.get(fid, {}).get(sheet, ([], []))
        return [dict(zip(h, r)) for r in rows]

    def sheet(self, ref: str):
        num, name = ref.split("/", 1)
        fid = self.fids.get(num, num)
        return fid, name, self.books.get(fid, {}).get(name)

    # --------------------------------------------------------------------------------------------------- pictures
    def picture(self, src: Path, domain_fid: str, caption: str) -> list[str]:
        rel_src = src.relative_to(repo.ROOT).as_posix() if src.is_relative_to(repo.ROOT) else src.name
        parts = src.relative_to(repo.ROOT).parts if src.is_relative_to(repo.ROOT) else ("fx",) + src.parts[-2:]
        name = "_".join(p for p in parts[-2:])
        rel = f"images/{domain_fid}/{name}"
        dst = self.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copyfile(src, dst)
            self.pictures.append((rel, rel_src if src.is_relative_to(repo.ROOT) else "Builds/effect_shots/" + "/".join(parts[-2:])))
        unit = self.unit_note(src)
        return [f"![{_cell(caption, 120)}](../{rel})", "", f"*Hình: {caption.strip().rstrip('.') or name}. {unit}*", ""]

    def unit_note(self, src: Path) -> str:
        models = {r["id"]: r for r in self._dicts("10_model_tai_san", "Model")}
        mbt = models.get("main_battle_tank", {})
        ruler = ""
        if mbt.get("glb_x_m"):
            ruler = (f"thước so sánh: Tăng chủ lực (main_battle_tank) {mbt.get('glb_x_m')} × {mbt.get('glb_y_m')} × "
                     f"{mbt.get('glb_z_m')} m (glb x × y × z, 10_model_tai_san/Model)")
        model = models.get(src.parent.name)
        if "rebuild" in src.parts and model:
            return (f"Đơn vị: m; ảnh không có lưới mét; model {src.parent.name} {model.get('glb_x_m')} × "
                    f"{model.get('glb_y_m')} × {model.get('glb_z_m')} m (glb x × y × z); {ruler}.")
        if "fx" == src.parent.parent.name or (self.effect_shots and src.is_relative_to(self.effect_shots)):
            return f"Đơn vị: m (cảnh hiệu ứng trên nền phẳng, không lưới); {ruler}."
        return f"Đơn vị: ảnh chụp trong game, không có lưới mét; {ruler}." if ruler else "Đơn vị: ảnh chụp, không lưới."

    # ------------------------------------------------------------------------------------------------------- parts
    def part_status(self, part: dict) -> str:
        if part.get("status"):
            return part["status"]
        states = []
        for ref in part.get("sheets", []):
            fid, name, sh = self.sheet(ref)
            if sh is None:
                states.append(("chua", f"sheet {fid}/{name} chưa có", name))
                continue
            st, mark = sheet_status(sh[1], sh[0])
            states.append((st, mark, name))
        if not states or all(s[0] == "da" for s in states):
            return "Đã áp"
        whys = sorted({_why(m) for s, m, _ in states if s != "da"})
        sheets = ", ".join(n for s, _, n in states if s != "da")
        if all(s[0] == "chua" for s in states):
            return f"Chưa áp — {'; '.join(whys)} (sheet {sheets})"
        return f"Một phần — {'; '.join(whys)} (sheet {sheets})"

    def part_md(self, part: dict) -> list[str]:
        num, title = part["num"], part["title"]
        level = "##" if re.fullmatch(r"\d+|P\d", num) else "###"
        dom = self.fids.get(part["domain"], part["domain"])
        status = self.part_status(part)
        self.statuses.append((num, title, status))
        srcs = [f"{self.sheet(r)[0]}/{self.sheet(r)[1]}" for r in part.get("sheets", [])]
        srcs += [f"{self.sheet(r)[0]}/{self.sheet(r)[1]} (lời hướng dẫn: 10_model_tai_san/Dia_phuong_hoa guide.<id>)"
                 for r in part.get("guides", []) if r not in part.get("sheets", [])]
        prose = []
        if part.get("html"):
            prose.append(f"{DP.DESIGN_HTML} (Tools/docs/build_doc.py) §" + ", §".join(h.rstrip(".") for h in part["html"]))
        prose += part.get("docs", [])
        lines = [f"{level} {num}. {title}", "", f"Trạng thái: {status}", "",
                 "Nguồn dữ liệu: " + ("; ".join(srcs) if srcs else "(không có sheet; chỉ văn bản)")
                 + (". Văn bản: " + "; ".join(prose) if prose else "") + ".", ""]
        # prose of the review
        for prefix in part.get("html", []):
            hits = [t for t in self.review if t.startswith(prefix)]
            for t in hits:
                self.used_html.add(t)
                lines += self.blocks_md(self.review[t], dom, t if len(hits) > 1 or len(part["html"]) > 1 else "")
            if not hits:
                lines += [f"*(Mục \"{prefix}\" không có trong {DP.DESIGN_HTML}.)*", ""]
        for doc in part.get("docs", []):
            lines += self.doc_md(doc)
        if part.get("links"):
            lines += ["Báo cáo chi tiết trong repo: " + "; ".join(f"`{x}`" for x in part["links"]) + ".", ""]
        for folder in part.get("pictures", []):
            lines += self.folder_pictures(repo.ROOT / folder, dom)
        if part.get("fx"):
            lines += self.fx_md(dom)
        # tables
        for ref in part.get("sheets", []):
            fid, name, sh = self.sheet(ref)
            self.used_sheets.add((fid, name))
            if sh is None:
                lines += [f"Sheet (chưa có): {fid}/{name}.", ""]
                continue
            lines += table_md(fid, name, sh[0], sh[1], self.names)
        for ref in part.get("guides", []):
            lines += self.guides_md(ref)
        if part.get("index"):
            lines += self.index_md()
        return lines

    def blocks_md(self, blocks, dom: str, sub: str) -> list[str]:
        lines = [f"#### {sub}", ""] if sub else []
        # a heading whose content was only unit cards or number tables (left out) is left out too
        blocks = [b for i, b in enumerate(blocks) if b[0] != "h" or (
            i + 1 < len(blocks) and not (blocks[i + 1][0] == "h" and blocks[i + 1][1] <= b[1]))]
        for b in blocks:
            kind = b[0]
            if kind == "h":
                lines += [("#" * (b[1] + 1)) + " " + self.fix(b[2]), ""]
            elif kind == "p":
                lines += [self.fix(b[1]), ""]
            elif kind == "li":
                lines += ["- " + self.fix(b[1])]
                continue
            elif kind == "table":
                lines += [""] + [self.fix(x) for x in b[1]]
            elif kind == "img":
                lines += self.picture(b[1], dom, self.fix(b[2]))
            if lines and lines[-1] != "" and kind != "li":
                lines.append("")
        return _tidy(lines)

    def fix(self, s: str) -> str:
        return apply_fixes(s, self.fix_counts)

    def doc_md(self, rel: str) -> list[str]:
        p = repo.ROOT / rel
        if not p.exists():
            return [f"*(Báo cáo {rel} không có.)*", ""]
        lines = [f"#### Báo cáo `{rel}`", ""]
        for line in p.read_text("utf-8").splitlines():
            m = re.match(r"^(#+)\s+(.*)", line)
            lines.append(("#####" if len(m.group(1)) <= 1 else "######") + " " + m.group(2) if m else line)
        return _tidy(lines + [""])

    def folder_pictures(self, folder: Path, dom: str) -> list[str]:
        lines = []
        for p in sorted(folder.rglob("*")):
            if p.suffix.lower() in PIC_EXT and not (self.out / f"images/{dom}/{'_'.join(p.parts[-2:])}").exists():
                rel = p.relative_to(repo.ROOT).as_posix()
                cap = {"before_after.png": f"{p.parent.name}: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)",
                       "unity_scan.png": f"{p.parent.name}: ảnh quét trong Unity (ModelScan)"}.get(p.name, rel)
                lines += self.picture(p, dom, cap)
        return lines

    def fx_md(self, dom: str) -> list[str]:
        lines = ["#### Ảnh hiệu ứng theo bậc (Unity, EffectShots.FxBatch)", ""]
        root = self.effect_shots
        found = []
        if root and root.is_dir():
            for d in sorted(root.glob("tier_T*")):
                for name in FX_PICS:
                    if (d / name).exists():
                        found.append(d / name)
        if not found:
            lines += ["*Ảnh chờ (pending): ảnh hiệu ứng nằm ngoài repo (Builds/effect_shots của máy chạy Unity, "
                      "EffectShots.FxBatch). Chạy lại `python Tools/export/export.py --effect-shots <thư mục>` để chèn. "
                      "Đơn vị khi có ảnh: m, thước so sánh Tăng chủ lực (main_battle_tank).*", ""]
            return lines
        for p in found:
            lines += self.picture(p, dom, f"{p.parent.name} {p.stem}")
        return lines

    def guides_md(self, ref: str) -> list[str]:
        fid, name, sh = self.sheet(ref)
        if sh is None:
            return []
        ids = [r[0] for r in sh[1]]
        lines = [f"#### Lời hướng dẫn trong game theo đơn vị ({fid}/{name}; chuỗi guide.<id> của GuideText.cs)", ""]
        n = 0
        for i in ids:
            g = self.guide.get(i)
            if not g:
                continue
            n += 1
            g = re.sub(r"\[\[(.+?)\]\]", r"\1", g)
            parts = [x.strip() for x in g.splitlines() if x.strip()]
            head = self.short.get(i) or (parts[0] if parts else i)
            lines += [f"- **{_cell(head, 80)}** (`{i}`): " + " · ".join(_cell(x, 400) for x in parts[1:] or parts)]
        lines += ["", f"*{n} / {len(ids)} đơn vị có lời hướng dẫn.*", ""]
        return lines

    def index_md(self) -> list[str]:
        lines = ["#### Sửa chữ theo mã (spec 6)", "",
                 "| văn bản cũ (mẫu) | thay bằng | căn cứ trong mã / dữ liệu | số chỗ |", "|---|---|---|---|"]
        for pat, repl, why in DP.FIXES:
            lines.append(f"| {_cell(pat, 90)} | {_cell(repl or '(giữ: đúng với mã)', 120)} | {_cell(why, 160)} | "
                         f"{self.fix_counts.get(pat, 0)} chỗ |")
        if self.review_stats.get("missing"):
            lines += ["", f"Văn bản tài liệu thiết kế: {self.review_stats['missing']}."]
        lines += ["", f"Bản PDF cũ: {self.review_stats['number_tables']} bảng số bỏ (các sheet thay), "
                      f"{self.review_stats['cards']} thẻ đơn vị bỏ (chỉ số ở sheet, lời hướng dẫn từ chuỗi), "
                      f"{self.review_stats['pictures_outside']} ảnh ngoài repo bỏ.", ""]
        left = sorted(t for t in self.review if t not in self.used_html and t != "Mục lục")
        if left:
            lines += ["Mục của bản PDF cũ không dùng: " + "; ".join(left) + ".", ""]
        return lines

    # -------------------------------------------------------------------------------------------------- the files
    def build(self) -> dict:
        md = self.out / "md"
        if md.exists():
            shutil.rmtree(md)
        if (self.out / "images").exists():
            shutil.rmtree(self.out / "images")
        md.mkdir(parents=True)
        rendered = [(p, self.part_md(p)) for p in DP.PARTS if p.get("index") is None]
        index_part = next(p for p in DP.PARTS if p.get("index"))
        rendered.append((index_part, self.part_md(index_part)))  # last: it reports what the others used
        rendered.sort(key=lambda x: DP.PARTS.index(x[0]))
        files = {}
        for num, fid in sorted(self.fids.items()):
            parts = [(p, lines) for p, lines in rendered if p["domain"] == num]
            files[f"md/{fid}.md"] = self.domain_md(fid, parts)
        files[f"md/{full_name(self.meta['ngay'])}"] = self.full_md(rendered)
        for rel, lines in files.items():
            (self.out / rel).write_bytes(("\n".join(_tidy(lines)).rstrip() + "\n").encode("utf-8"))
        return {"md": sorted(files), "images": sorted(self.pictures), "chua_ap": self.chua_ap()}

    def chua_ap(self):
        return [(n, t, s) for n, t, s in self.statuses if s.startswith("Chưa áp")]

    def domain_md(self, fid: str, parts) -> list[str]:
        info = self.file_titles.get(fid, {})
        title = info.get("tieu_de") or fid
        lines = [f"# {fid} — {title}", "",
                 f"Bộ xuất dữ liệu Machine Brigade, commit {self.meta['commit']}, ngày {self.meta['ngay']}. Sinh bởi "
                 "`python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết "
                 f"kế (Tools/docs) và chuỗi trong game. Toàn văn: {full_name(self.meta['ngay'])}.", ""]
        if info.get("mo_ta"):
            lines += [info["mo_ta"], ""]
        lines += ["Mục trong file này: " + "; ".join(f"{p['num']}. {p['title']}" for p, _ in parts) + "." if parts
                  else "Mục: (không có mục riêng trong tài liệu thiết kế; chỉ bảng).", ""]
        for _, body in parts:
            lines += body
        rest = [s for s in sorted(self.books.get(fid, {})) if (fid, s) not in self.used_sheets and not s.startswith("input_")]
        if rest:
            lines += ["## Các sheet khác của file", "",
                      "Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).", ""]
            for s in rest:
                h, rows = self.books[fid][s]
                st, mark = sheet_status(rows, h)
                label = {"da": "Đã áp", "mot_phan": "Một phần — " + _why(mark), "chua": "Chưa áp — " + _why(mark)}[st]
                lines += [f"### {s}", "", f"Trạng thái: {label}", "", f"Nguồn dữ liệu: {fid}/{s}.", ""]
                lines += table_md(fid, s, h, rows, self.names)
        return lines

    def full_md(self, rendered) -> list[str]:
        d = self.meta["ngay"]
        lines = [f"# Machine Brigade — Tài liệu thiết kế toàn văn ({d})", "",
                 f"Commit {self.meta['commit']}. Sinh bởi `python Tools/export/export.py` (spec 6): ghép theo mục lục của "
                 "tài liệu thiết kế (mục 1–19) cùng các mục mới 3b, 3c, 10i, 15b, 16b, 20, 21 và phụ lục P1–P5. Bảng in đúng "
                 "ô của sheet (csv / xlsx cùng bộ xuất); bảng quá 40 dòng in 15 dòng đầu. PDF cùng ngày sinh từ chính file "
                 "này.", "",
                 SELF_CHECK_START, "## Tự kiểm (00_chi_muc/SELF_CHECK.md)", "",
                 "Chưa chạy: `python Tools/export/export.py check` chèn SELF_CHECK.md vào đây.", "", SELF_CHECK_END, "",
                 "## Mục lục", ""]
        for p, _ in rendered:
            ind = "" if re.fullmatch(r"\d+|P\d", p["num"]) else "  "
            lines.append(f"{ind}- {p['num']}. {p['title']} ({self.fids.get(p['domain'], p['domain'])})")
        lines.append("")
        for _, body in rendered:
            lines += body
        lines += ["## Mục \"Chưa áp\"", ""]
        ca = self.chua_ap()
        lines += [f"- {n}. {t}: {s}" for n, t, s in ca] if ca else ["(không có)"]
        lines += ["", "Mục \"Một phần\": " + "; ".join(f"{n}. {t}" for n, t, s in self.statuses if s.startswith("Một phần"))
                  + ".", ""]
        return lines


def _tidy(lines: list[str]) -> list[str]:
    out = []
    for x in lines:
        if x == "" and out and out[-1] == "":
            continue
        if x != "" and out and out[-1].startswith("- ") and not x.startswith("- "):
            out.append("")
        out.append(x)
    return out


def build(out: Path, meta: dict, effect_shots: Path | None = None) -> dict:
    return Doc(out, meta, effect_shots).build()


def insert_self_check(out: Path, date: str) -> Path | None:
    """check: put SELF_CHECK.md at the top of FULL.md (between the markers), its headings one level down."""
    full = out / "md" / full_name(date)
    sc = out / "00_chi_muc" / "SELF_CHECK.md"
    if not full.exists() or not sc.exists():
        return None
    body = []
    for line in sc.read_text("utf-8").splitlines():
        m = re.match(r"^(#+)\s+(.*)", line)
        body.append(("#" * min(6, len(m.group(1)) + 1)) + " " + m.group(2) if m else line)
    text = full.read_text("utf-8")
    a, b = text.index(SELF_CHECK_START), text.index(SELF_CHECK_END)
    text = text[:a] + SELF_CHECK_START + "\n" + "\n".join(body).rstrip() + "\n\n" + text[b:]
    text = text.replace("## Tự kiểm bộ xuất (spec 9)", "## Tự kiểm bộ xuất (spec 9; 00_chi_muc/SELF_CHECK.md)", 1)
    full.write_bytes(text.encode("utf-8"))
    return full

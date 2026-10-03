"""The md of the pack (addendum 5): one file per xlsx, only rules, explanations, design reasons, references to the real world
and the games, and small tables (20 rows at most; a bigger table is "xem sheet <name>"). No status line, no history, no
process word. Prose comes from the design review (docmd.read_review) cleaned sentence by sentence; every table prints the
cells of the sheet as the xlsx holds them (the 200-cell check compares them). Pictures go flat into images/ with the
file's id as a prefix, and only the ones an md shows are copied.
"""
from __future__ import annotations

import collections
import re
import shutil
from pathlib import Path

from . import doc_parts as DP
from . import docmd, repo
from .model import MARKER
from .pack import OLD_TO_NEW, PACK
from .write import csv_value

MAX_TABLE_ROWS, MAX_COLS, MAX_TEXT, REF_ROWS = 20, 10, 60, 15
SKIP_COLS = {"raw_json", "nguon"}
SKIP_PARTS = {"15b", "16b", "17", "P1", "P2", "P3", "P4", "P5"}
OLD_NUM = {fid[:2]: fid for olds in (v[1] for v in PACK.values()) for fid in olds}
# a sentence that tells how or when something was done, not what it is
BAD = re.compile(r"(?i)prompt|lượt\s*\d|manifest|nhật ký|apply_log|decisions|changelog|chua_ap|chưa áp|đã áp|"
                 r"sửa sau buổi|cân bằng đợt|play-?test|buổi chơi thử|fix l\d|p\d\d_apply|lịch sử đo|self_check|validator")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ỵ0-9*\[`(\"“])")
# a section title that tells when it was done, said by what it holds
TITLE_OVERRIDE = {"Cân bằng đợt 2": "Hệ số sát thương, pháo sáng và APS của xe",
                  "Hệ căn cứ (prompt 32) / The base system (prompt 32)": "Hệ căn cứ / The base system"}
TITLE_PROMPT = re.compile(r"\s*\((?:[^()]*\b[Pp]rompt\b[^()]*)\)")


def clean_title(t: str) -> str:
    t = TITLE_PROMPT.sub("", t)
    t = re.sub(r"^(?:[Pp]rompt \d+[a-z]?:\s*)", "", t)
    t = re.sub(r"^\d+[a-z]?\.\s+", "", t)
    t = re.sub(r"\b[Pp]rompt \d+[a-z]?:?\s*", "", t)
    return re.sub(r"\s{2,}", " ", t).strip(" :/")


def keep_text(s: str) -> str:
    """The sentences of s that are not about process; '' when none is left."""
    if not BAD.search(s):
        return s
    kept = [x for x in SENTENCE.split(s) if not BAD.search(x)]
    return " ".join(kept).strip()


class PackDoc:
    def __init__(self, ctx, meta: dict, out: Path):
        self.ctx, self.meta, self.out = ctx, meta, out
        self.books = ctx.books
        self.review, self.review_stats = docmd.read_review(repo.ROOT / DP.DESIGN_HTML)
        self.fix_counts: dict = {}
        self._tables: dict = {}
        self.pictures: dict[str, str] = {}  # images/<name> -> repo source
        self.used_sheets: set = set()

    # ------------------------------------------------------------------------------------------------------- data
    def sheet(self, ref: str):
        """'02/Xe' (old file number / old sheet name) -> (new file, new name, Sheet or None)."""
        num, name = ref.split("/", 1)
        q = self.ctx.sheet_map.get((OLD_NUM.get(num, num), name))
        if q is None:
            return None, name, None
        return q[0], q[1], self.books[q[0]].sheets.get(q[1])

    def data(self, s):
        key = id(s)
        if key not in self._tables:
            header, rows = s.table(values=True)
            self._tables[key] = (header, [[csv_value(v) for v in r] for r in rows])
        return self._tables[key]

    def dicts(self, fid: str, name: str):
        s = self.books.get(fid, None) and self.books[fid].sheets.get(name)
        if s is None:
            return []
        h, rows = self.data(s)
        return [dict(zip(h, r)) for r in rows]

    # ---------------------------------------------------------------------------------------------------- tables
    def table(self, fid: str, s) -> list[str]:
        header, rows = self.data(s)
        where = f"{fid}/{s.name}" + (" (bulk.zip)" if s.bulk else "")
        if not rows:
            return []
        title = s.title_vi
        if s.bulk or len(rows) > MAX_TABLE_ROWS:
            return [f"Sheet {where}{' — ' + title if title else ''}: {len(rows)} dòng, {len(header)} cột; bảng đầy đủ: xem "
                    f"{'bulk.zip' if s.bulk else 'sheet ' + s.name}.", ""]
        cols = [i for i, c in enumerate(header) if i == 0 or (c not in SKIP_COLS and not c.endswith(("_truoc", "_sau"))
                                                             and any(r[i] != "" for r in rows))]
        rest = len(cols) - MAX_COLS if len(cols) > MAX_COLS else 0
        cols = cols[:MAX_COLS]
        lines = [f"Sheet {where}{' — ' + title if title else ''} ({len(rows)} dòng, {len(header)} cột)", "",
                 "| " + " | ".join(header[i] for i in cols) + " |", "|" + "---|" * len(cols)]
        for r in rows:
            lines.append("| " + " | ".join(docmd._cell(r[i], 400 if i == 0 else MAX_TEXT) for i in cols) + " |")
        lines += [""]
        if rest:
            lines += [f"*In {len(cols)} / {len(header)} cột; {rest} cột khác: xem sheet.*", ""]
        return lines

    # -------------------------------------------------------------------------------------------------- pictures
    def picture(self, src: Path, fid: str, caption: str) -> list[str]:
        name = f"{fid}_{docmd.export_name(src)}"
        dst = self.out / "images" / name
        if name not in self.pictures:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            self.pictures[name] = src.relative_to(repo.ROOT).as_posix() if src.is_relative_to(repo.ROOT) else src.name
        return [f"![{docmd._cell(caption, 120)}](images/{name})", "", f"*Hình: {caption.strip().rstrip('.') or name}. "
                f"{self.unit_note()}*", ""]

    def unit_note(self) -> str:
        mbt = {r.get("id"): r for r in self.dicts("07_hinh_anh_am_thanh_model", "Model")}.get("main_battle_tank", {})
        if mbt.get("glb_x_m"):
            return (f"Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) "
                    f"{mbt.get('glb_x_m')} × {mbt.get('glb_y_m')} × {mbt.get('glb_z_m')} m (07_hinh_anh_am_thanh_model/Model).")
        return "Đơn vị: ảnh chụp, không lưới mét."

    # ----------------------------------------------------------------------------------------------------- prose
    def fix(self, s: str) -> str:
        return docmd.apply_fixes(s, self.fix_counts)

    def blocks_md(self, blocks, fid: str, sheets: list[str]) -> list[str]:
        lines = []
        blocks = [b for i, b in enumerate(blocks) if b[0] != "h" or (
            i + 1 < len(blocks) and not (blocks[i + 1][0] == "h" and blocks[i + 1][1] <= b[1]))]
        skip_level = None  # a heading about process drops what is under it, down to the next heading of its level
        for b in blocks:
            kind = b[0]
            if kind == "h":
                title = clean_title(self.fix(b[2]))
                if skip_level is not None and b[1] <= skip_level:
                    skip_level = None
                if BAD.search(title) or not title:
                    skip_level = b[1]
                    continue
                if skip_level is None:
                    lines += [("#" * b[1]) + " " + title, ""]
                continue
            if skip_level is not None:
                continue
            if kind == "p":
                t = keep_text(self.fix(b[1]))
                if t:
                    lines += [t, ""]
            elif kind == "li":
                t = keep_text(self.fix(b[1]))
                if t:
                    lines += ["- " + t]
                    continue
            elif kind == "table":
                body = [x for x in b[1] if x.startswith("|")][2:]
                if len(body) > MAX_TABLE_ROWS:
                    lines += [f"Bảng {len(body)} dòng: xem " + (("sheet " + ", ".join(sheets[:3])) if sheets else "các sheet của file")
                              + ".", ""]
                elif not BAD.search("\n".join(b[1])):
                    lines += [""] + [self.fix(x) for x in b[1]]
            elif kind == "img":
                lines += self.picture(b[1], fid, keep_text(self.fix(b[2])) or "Hình minh họa")
            if lines and lines[-1] != "" and kind != "li":
                lines.append("")
        return _tidy(lines)

    def part_md(self, part: dict, fid: str) -> list[str]:
        sheets = [self.sheet(r) for r in part.get("sheets", [])]
        sheets = [(f, n, s) for f, n, s in sheets if s is not None]
        names = [f"{n}" for _f, n, _s in sheets]
        lines = [f"## {part['title']}", ""]
        for prefix in part.get("html", []):
            for t in (t for t in self.review if t.startswith(prefix)):
                body = self.blocks_md(self.review[t], fid, names)
                if body:
                    sub = clean_title(TITLE_OVERRIDE.get(t, t))
                    if sub and sub != part["title"] and not BAD.search(sub):
                        lines += [f"### {sub}", ""]
                    lines += body
        for folder in part.get("pictures", []):
            if "kit_catalog" in folder or "doc-images" in folder:
                for p in docmd.folder_files(repo.ROOT / folder):
                    if f"{fid}_{docmd.export_name(p)}" not in self.pictures:
                        lines += self.picture(p, fid, docmd.folder_caption(p))
        big = []
        for f, n, s in sheets:
            self.used_sheets.add((f, n))
            if s.bulk or len(s.rows) > MAX_TABLE_ROWS:
                big.append(f"`{n}` ({len(s.rows)} dòng{', bulk.zip' if s.bulk else ''})")
            else:
                lines += self.table(f, s)
        if big:
            lines += ["Bảng đầy đủ: xem sheet " + ", ".join(big) + ".", ""]
        for rel in part.get("docs", []):
            if rel == "Docs/models/MODEL_STANDARD.md" and (repo.ROOT / rel).exists():
                lines += self.doc_md(rel)
        return _tidy(lines)

    def doc_md(self, rel: str) -> list[str]:
        """A rules document of the repo (the model standard), its process sentences left out."""
        out = []
        for line in (repo.ROOT / rel).read_text("utf-8").splitlines():
            m = re.match(r"^(#+)\s+(.*)", line)
            if m:
                title = clean_title(m.group(2))
                if title and not BAD.search(title):
                    out.append(("#" * min(6, len(m.group(1)) + 2)) + " " + title)
                continue
            t = keep_text(line) if line.strip() else ""
            out.append(t)
        return _tidy(out + [""])

    # ----------------------------------------------------------------------------------------------- reference
    def ref_md(self, fid: str) -> list[str]:
        """The subsection "Tham khảo ngoài đời và game": reliability counts, the first rows with a reference, the sources."""
        sheets = self.books[fid].sheets
        refs = [n for n, s in sheets.items() if n.endswith("_tham_chieu") and "loai_tham_chieu" in s.cols and not s.bulk]
        cmps = [n for n in sheets if n.endswith("_so_sanh_that")]
        if not refs and not cmps:
            return []
        nguon = {r.get("id", ""): r for r in self.dicts("08_tham_chieu", "Nguon_tham_chieu")}
        lines = ["## Tham khảo ngoài đời và game", "",
                 "Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi "
                 "NEED_SOURCE, không điền từ trí nhớ.", ""]
        used = set()
        for s in refs:
            rows = self.dicts(fid, s)
            tin = collections.Counter(r.get("do_tin_cay", "") for r in rows)
            loai = collections.Counter(r.get("loai_tham_chieu", "") for r in rows)
            lines += [f"### {s}", "",
                      f"{len(rows)} dòng. Độ tin cậy: " + ", ".join(f"{k} {tin[k]}" for k in
                                                                   ("da_kiem_chung", "uoc_dinh", "ban_dau_doan", "NEED_SOURCE"))
                      + ". Loại: " + ", ".join(f"{k} {v}" for k, v in sorted(loai.items()) if k) + ".", ""]
            shown = [r for r in rows if any(r.get(c) not in ("", "NEED_SOURCE", None)
                                            for c in ("ten_mau_that", "ten_game", "ten_phim_truyen", "hoc_thuyet_quan_su"))]
            for r in shown[:REF_ROWS]:
                bits = []
                for c, label in (("ten_mau_that", "mẫu thật"), ("hoc_thuyet_quan_su", "học thuyết"), ("ten_game", "game"),
                                 ("ten_phim_truyen", "phim / truyện"), ("diem_giong", "giống"),
                                 ("diem_khac_co_chu_dich", "khác có chủ đích")):
                    v = keep_text(r.get(c, ""))
                    if v and v != "NEED_SOURCE":
                        bits.append(f"{label}: {docmd._cell(v, 90)}")
                ids = [x for x in r.get("nguon_id", "").split(";") if x]
                used.update(ids)
                lines.append(f"- `{r.get('id', '')}` ({docmd._cell(r.get('ten_hien_thi', ''), 40)}): " + "; ".join(bits)
                             + f"; độ tin: {r.get('do_tin_cay', '')}; nguồn: {', '.join(ids) or 'không'}.")
            for r in shown[REF_ROWS:]:
                used.update(x for x in r.get("nguon_id", "").split(";") if x)
            if len(shown) > REF_ROWS:
                lines.append(f"- … {len(shown) - REF_ROWS} dòng có tham chiếu nữa: xem sheet {s}.")
            if not shown:
                lines.append("- Chưa dòng nào có tham chiếu trong repo.")
            lines.append("")
            self.used_sheets.add((fid, s))
        if used:
            lines += ["Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):", ""]
            for nid in sorted(used)[:30]:
                d = nguon.get(nid, {})
                url = d.get("url", "")
                lines.append(f"- `{nid}`: {docmd._cell(d.get('tieu_de', nid), 120)}" + (f" — <{url}>" if url else "")
                             + (f" (độ tin {d.get('do_tin_cay')})" if d.get("do_tin_cay") else ""))
            if len(used) > 30:
                lines.append(f"- … {len(used) - 30} nguồn nữa: xem sheet Nguon_tham_chieu của 08_tham_chieu.")
            lines.append("")
        for s in cmps:
            self.used_sheets.add((fid, s))
            lines += self.table(fid, sheets[s])
        return lines

    # ------------------------------------------------------------------------------------------------- the files
    def reference_file_md(self, fid: str) -> list[str]:
        """08_tham_chieu: what each sheet holds and how to read the reliability grades."""
        src = self.dicts(fid, "Nguon_tham_chieu")
        tin = collections.Counter(r.get("do_tin_cay", "") for r in src)
        loai = collections.Counter(r.get("loai", "") for r in src)
        lines = ["## Cách đọc", "",
                 "File này giữ nguồn ngoài đời, cơ chế lấy ý từ game khác và học thuyết quân sự mà các file 01–07 dẫn tới "
                 "(cột `nguon_id` của sheet `<tên>_tham_chieu`). Một dòng nguồn có `do_tin_cay`: `da_kiem_chung` (có tài liệu "
                 "hoặc số đo kiểm được), `uoc_dinh` (ước theo nguồn gần đúng), `ban_dau_doan` (đoán ban đầu, chưa có nguồn).", "",
                 f"Nguon_tham_chieu: {len(src)} nguồn; độ tin cậy: " + ", ".join(f"{k or '(trống)'} {v}" for k, v in sorted(tin.items()))
                 + ". Loại: " + ", ".join(f"{k or '(trống)'} {v}" for k, v in sorted(loai.items())) + ".", ""]
        return lines

    def sheet_list(self, fid: str) -> list[str]:
        lines = ["## Các sheet của file", "",
                 "Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản "
                 "chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.", ""]
        for name, s in self.books[fid].sheets.items():
            if name.startswith("input_"):
                continue
            where = " [bulk.zip]" if s.bulk else ""
            desc = docmd._cell(s.desc or "", 150)
            lines.append(f"- `{name}`{where} ({len(s.rows)} dòng): {s.title_vi}" + (f" — {desc}" if desc else ""))
        return lines + [""]

    def file_md(self, fid: str) -> list[str]:
        title, olds, desc = PACK[fid]
        lines = [f"# {fid} — {title}", "", desc + ".", "",
                 f"Gói cân bằng Machine Brigade, commit {self.meta['commit']}, ngày {self.meta['ngay']}. Số liệu đầy đủ ở "
                 f"{fid}.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa "
                 f"{MAX_TABLE_ROWS} dòng, bảng lớn: xem sheet).", ""]
        nums = [n for n, f in OLD_NUM.items() if f in olds]
        parts = [p for p in DP.PARTS if p["num"] not in SKIP_PARTS and p["domain"] in nums and self.part_belongs(p, fid)]
        for p in parts:
            lines += self.part_md(p, fid)
        if fid == "08_tham_chieu":
            lines += self.reference_file_md(fid)
        else:
            lines += self.ref_md(fid)
        lines += self.sheet_list(fid)
        return _tidy(lines)

    def part_belongs(self, part: dict, fid: str) -> bool:
        """A part goes to the file that holds most of its sheets (a reclassified sheet moves its part with it)."""
        refs = [self.sheet(r)[0] for r in part.get("sheets", [])]
        refs = [r for r in refs if r]
        if not refs:
            return OLD_TO_NEW.get(OLD_NUM.get(part["domain"])) == fid
        return collections.Counter(refs).most_common(1)[0][0] == fid

    def build(self) -> dict:
        if (self.out / "images").exists():
            shutil.rmtree(self.out / "images")
        texts = {}
        for fid in PACK:
            texts[fid] = "\n".join(_tidy(self.file_md(fid))).rstrip() + "\n"
        for fid, text in texts.items():
            (self.out / f"{fid}.md").write_bytes(text.encode("utf-8"))
        return {"md": sorted(f"{f}.md" for f in texts), "images": sorted(self.pictures)}


def _tidy(lines: list[str]) -> list[str]:
    out = []
    for x in lines:
        if x == "" and out and out[-1] == "":
            continue
        if x != "" and out and out[-1].startswith("- ") and not x.startswith("- "):
            out.append("")
        out.append(x)
    return out


def build(ctx, meta: dict, out: Path) -> dict:
    return PackDoc(ctx, meta, out).build()

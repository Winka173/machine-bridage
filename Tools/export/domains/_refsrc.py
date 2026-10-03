"""Pass 10 (spec 12.1, the "no web" branch): the repo's reference notes and the registry of the documents they cite.

Read only, and only repo data: Tools/docs/unit_refs.json, Tools/models/reference_real.json (exported by 10/Kich_thuoc_that),
the REAL and WARHEAD tables of Tools/balance/full_weapon_audit.py (read as literals, never run), Tools/docs/unit_sheet.json,
the reference columns of Docs/balance/Machine_Brigade_Can_bang.xlsx and Docs/ai/Machine_Brigade_AI_Research.xlsx (openpyxl),
the Tools/blender builders' docstrings and Tools/blender/specs/*.json, Docs/DECISIONS.md (searched by phrase, never read
whole into a sheet), Docs/ASSET_LICENSES.md and the audio credits already in 09/Am_thanh. No number or fact is filled from
memory: a document a note names becomes a Nguon_tham_chieu row (title as the note writes it, the URL only when the repo
gives one); a value no repo source gives is NEED_SOURCE.
"""
from __future__ import annotations

import ast
import re
import unicodedata

from core.repo import ROOT

UNIT_REFS = "Tools/docs/unit_refs.json"
REAL_SIZES = "Tools/models/reference_real.json"
UNIT_SHEET = "Tools/docs/unit_sheet.json"
AUDIT = "Tools/balance/full_weapon_audit.py"
REASONS = "Tools/balance/fix_weapon_reasons.json"
CAN_BANG = "Docs/balance/Machine_Brigade_Can_bang.xlsx"
AI_RESEARCH = "Docs/ai/Machine_Brigade_AI_Research.xlsx"
DECISIONS = "Docs/DECISIONS.md"
REF_DIMS = "Docs/models/reference_dimensions.md"
LICENSES = "Docs/ASSET_LICENSES.md"
SPECS = "Tools/blender/specs/"
BLENDER = "Tools/blender/"

# reliability of a document (spec 12.3): 1 official / manufacturer, 2 reputable secondary, 3 community (our own repo notes: 3)
LOAI_TIN = {"tai_lieu_quan_su_chinh_thuc": 1, "nha_san_xuat": 1, "nha_phat_hanh_game": 1, "wikipedia": 2, "bai_bao": 2,
            "sach": 2, "wiki_game": 3, "thu_vien_am_thanh": 2, "tai_lieu_repo": 3, "ban_ve": 2, "video": 3}
# films and series among unit_refs' "media" (the rest are games); a name list, not a fact about the works
FILM_WORDS = ("Star Wars", "The Expanse", "Battlestar Galactica", "Hunt for Red October")
EST = re.compile(r"(\best\.|\(est\b|\best\b\.?\s|ước đoán|ước lượng|uoc_dinh|\bapprox)", re.I)


def slug(text: str, n: int = 44) -> str:
    t = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D")).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_").lower()
    return t[:n].rstrip("_") or "x"


class Registry:
    """Nguon_tham_chieu rows: id -> dict(loai, tieu_de, tac_gia_to_chuc, nam, url, ngay_truy_cap, do_tin_cay, ghi_chu,
    duong_dan_repo, trich_tu). The same document cited twice is one row (same title -> same id)."""

    def __init__(self):
        self.rows: dict[str, dict] = {}
        self.by_title: dict[tuple, str] = {}

    def add(self, loai: str, tieu_de: str, url: str = "", duong_dan_repo: str = "", ngay_truy_cap: str = "",
            ghi_chu: str = "", trich_tu: str = "", tac_gia: str = "", nam="") -> str:
        key = (loai, tieu_de.strip().lower())
        if key in self.by_title:
            r = self.rows[self.by_title[key]]
            if trich_tu and trich_tu not in r["trich_tu"].split(";"):
                r["trich_tu"] = ";".join(sorted(set(filter(None, r["trich_tu"].split(";") + [trich_tu]))))
            if url and not r["url"]:
                r["url"] = url
            if ngay_truy_cap and not r["ngay_truy_cap"]:
                r["ngay_truy_cap"] = ngay_truy_cap
            return self.by_title[key]
        prefix = {"tai_lieu_repo": "R", "wikipedia": "W"}.get(loai, "D")
        rid = f"{prefix}_{slug(tieu_de)}"
        n = 2
        while rid in self.rows:
            rid = f"{prefix}_{slug(tieu_de)}_{n}"
            n += 1
        self.by_title[key] = rid
        self.rows[rid] = {"loai": loai, "tieu_de": tieu_de.strip(), "tac_gia_to_chuc": tac_gia, "nam": nam, "url": url,
                          "ngay_truy_cap": ngay_truy_cap, "do_tin_cay": LOAI_TIN.get(loai, 3), "ghi_chu": ghi_chu,
                          "duong_dan_repo": duong_dan_repo, "trich_tu": trich_tu}
        return rid

    def repo(self, path: str, title: str, note: str = "", url: str = "") -> str:
        """A repo document: id R_<file stem> (the path names it; the same path is one row)."""
        for rid, r in self.rows.items():
            if r["loai"] == "tai_lieu_repo" and r["duong_dan_repo"] == path:
                if note and not r["ghi_chu"]:
                    r["ghi_chu"] = note
                return rid
        stem = path.rstrip("/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        rid = f"R_{slug(stem, 40)}"
        n = 2
        while rid in self.rows:
            rid = f"R_{slug(stem, 40)}_{n}"
            n += 1
        self.by_title[("tai_lieu_repo", title.strip().lower())] = rid
        self.rows[rid] = {"loai": "tai_lieu_repo", "tieu_de": title.strip(), "tac_gia_to_chuc": "", "nam": "", "url": url,
                          "ngay_truy_cap": "", "do_tin_cay": LOAI_TIN["tai_lieu_repo"], "ghi_chu": note,
                          "duong_dan_repo": path, "trich_tu": ""}
        return rid

    # ------------------------------------------------------------------ citations inside a note
    def cite(self, text: str, carrier: str, accessed: str = "") -> tuple[list[str], bool]:
        """The documents a repo note names (Wikipedia 'X', US Army FM ..., a maker's specification, Army Recognition 'X',
        DECISIONS <id>, the balance sheet): (nguon ids, external document named). carrier: the repo source holding the note
        (its id is the caller's to add)."""
        text = text or ""
        ids = []
        for m in re.finditer(r"Wikipedia\s+'([^']+)'", text):
            ids.append(self.add("wikipedia", f"Wikipedia '{m.group(1)}'", ngay_truy_cap=accessed, trich_tu=carrier,
                                ghi_chu="bài Wikipedia (tiếng Anh) theo tên ghi trong nguồn repo; URL không ghi trong repo"))
        for m in re.finditer(r"(US Army (?:FM [\d.-]+|[A-Z0-9]+ fact file))", text):
            ids.append(self.add("tai_lieu_quan_su_chinh_thuc", m.group(1), ngay_truy_cap=accessed, trich_tu=carrier))
        for m in re.finditer(r"((?:Rheinmetall|Caterpillar|Toyota)\s[^:;,()]+?)(?=:|;|,|\(|$)", text):
            ids.append(self.add("nha_san_xuat", m.group(1).strip(), ngay_truy_cap=accessed, trich_tu=carrier))
        for m in re.finditer(r"Army Recognition\s+'([^']+)'", text):
            ids.append(self.add("bai_bao", f"Army Recognition '{m.group(1)}'", ngay_truy_cap=accessed, trich_tu=carrier))
        external = bool(ids)
        if re.search(r"DECISIONS\s+\d+\w*", text):
            ids.append(self.repo(DECISIONS, "Docs/DECISIONS.md (nhật ký quyết định)"))
        if re.search(r"the sheet", text):
            ids.append(self.repo(CAN_BANG, "Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx)"))
        return list(dict.fromkeys(ids)), external


def is_estimate(text: str) -> bool:
    return bool(EST.search(text or ""))


# ---------------------------------------------------------------------------------------------------------- readers
def audit_literals():
    """(REAL, WARHEAD, WARHEAD_NOTE) of full_weapon_audit.py, read as literals (the module is not imported)."""
    tree = ast.parse((ROOT / AUDIT).read_text("utf-8"))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", "") in ("REAL", "WARHEAD", "WARHEAD_NOTE", "SLOWER"):
                    out[t.id] = ast.literal_eval(node.value)
    return out.get("REAL", []), out.get("WARHEAD", {}), out.get("WARHEAD_NOTE", ""), out.get("SLOWER", 0.7)


def real_hit(real_table, name: str):
    name = (name or "").lower()
    if not name:
        return None
    return next((x for x in real_table if re.search(x[0], name)), None)


def xlsx_rows(path: str, sheet: str, header_row: int = 1) -> list[dict]:
    """A sheet of a repo workbook as dicts (header = row header_row); [] when the file or sheet is missing."""
    p = ROOT / path
    if not p.exists():
        return []
    import openpyxl
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    try:
        if sheet not in wb.sheetnames:
            return []
        rows = list(wb[sheet].iter_rows(values_only=True))
    finally:
        wb.close()
    if len(rows) < header_row:
        return []
    head = [str(h).strip() if h is not None else f"col{i}" for i, h in enumerate(rows[header_row - 1])]
    out = []
    for r in rows[header_row:]:
        if not any(v not in (None, "") for v in r):
            continue
        out.append({head[i]: (r[i] if i < len(r) else None) for i in range(len(head))})
    return out


def text(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s in ("—", "-", "–") else re.sub(r"\s+", " ", s)


def split_items(cell: str) -> list[tuple[str, str]]:
    """'Company of Heroes (quay mặt giáp), Steel Beasts' -> [('Company of Heroes', 'quay mặt giáp'), ('Steel Beasts', '')]
    (commas inside brackets kept; ';' also splits)."""
    cell = text(cell)
    if not cell:
        return []
    parts, depth, cur = [], 0, ""
    for ch in cell:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        cur += ch
    parts.append(cur)
    out = []
    for p in parts:
        p = p.strip().rstrip(".")
        if not p:
            continue
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", p)
        out.append((m.group(1).strip(), m.group(2).strip()) if m else (p, ""))
    return out


KNOWN_GAMES = ("Red Alert", "Command & Conquer", "C&C", "StarCraft", "Company of Heroes", "Supreme Commander", "Halo",
               "Warhammer", "Mass Effect", "Ace Combat", "World of Tanks", "War Thunder", "Battlefield", "Wargame", "WARNO")


def known_game(name: str) -> bool:
    return any(g.lower() in name.lower() for g in KNOWN_GAMES)


def game_like(name: str) -> bool:
    """A 'Tham khảo game' item that names a game (not a war, a real system or a phrase): starts with a capital or digit,
    and is not 'Chiến sự ...', '(thật) ...' or '... ngoài đời'."""
    n = name.strip()
    if not n or n[0] in "(-" or not (n[0].isupper() or n[0].isdigit()):
        return False
    low = n.lower()
    return not (low.startswith("chiến sự") or "ngoài đời" in low or "(thật)" in low)


def games_only(items):
    """(game items, other items) of split_items()."""
    g = [(a, b) for a, b in items if game_like(a)]
    o = [(a, b) for a, b in items if not game_like(a)]
    return g, o


def is_film(name: str) -> bool:
    return any(w.lower() in name.lower() for w in FILM_WORDS)


def decisions_lines() -> list[str]:
    p = ROOT / DECISIONS
    return p.read_text("utf-8").splitlines() if p.exists() else []


def decisions_find(lines: list[str], phrase: str):
    """(line number, '## section' heading, the line) of the first line holding phrase; None when absent."""
    sec = ""
    for i, ln in enumerate(lines, 1):
        if ln.startswith("## "):
            sec = ln[3:].strip()
        if phrase in ln:
            return i, sec, ln.strip()
    return None


def decisions_references(lines: list[str]) -> list[dict]:
    """Every '**References' passage of DECISIONS (its section, line, the paragraph up to a blank line, cut at 600)."""
    out, sec, sub = [], "", ""
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            sec = ln[3:].strip()
        elif ln.startswith("### "):
            sub = ln[4:].strip()
        m = re.search(r"\*\*References?(?: \([^)]*\))?[:.]?\*\*[:.]?|References:\s", ln)
        if m:
            para = [ln[m.start():]]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("#", "**", "|")) and len(" ".join(para)) < 900:
                para.append(lines[j].strip())
                j += 1
            body = re.sub(r"\*\*References?(?: \([^)]*\))?[:.]?\*\*[:.]?|References:\s*", "", " ".join(para)).strip()
            out.append({"dong": i + 1, "muc": sec, "muc_con": sub, "van_ban": body[:600]})
        i += 1
    return out


def builder_notes() -> list[dict]:
    """Bullets '  * <id>[ / <id>]: ...' of the module docstring of every Tools/blender/*.py whose docstring names its
    references: (file, ids, text cut at 500)."""
    out = []
    for p in sorted((ROOT / BLENDER).glob("*.py")):
        try:
            tree = ast.parse(p.read_text("utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        doc = ast.get_docstring(tree) or ""
        if "reference" not in doc.lower():
            continue
        cur = None
        for ln in doc.splitlines():
            m = re.match(r"^\s{0,4}\*\s+([a-z0-9_]+(?:\s*/\s*[a-z0-9_]+)*):\s*(.*)$", ln)
            if m:
                cur = {"file": f"{BLENDER}{p.name}", "ids": [x.strip() for x in m.group(1).split("/")], "text": m.group(2)}
                out.append(cur)
            elif cur and ln.startswith("    ") and ln.strip():
                cur["text"] += " " + ln.strip()
            else:
                cur = None
        for c in out:
            c["text"] = c["text"][:500]
    return out

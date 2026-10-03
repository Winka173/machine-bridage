"""Process words out of exported text (Docs/prompts/export_pack_vi.txt section 5): "prompt N", "lượt N", CHUA_AP:prompt_N.

A cell of a data column that names the prompt that wrote it ("... (prompt 34's trial table; ...)") keeps its words and
loses the process reference. Game text (dialogue, localisation, licences, tutorial strings) is never touched: it is the
game's own wording ("lượt" there means a turn or a pass).
"""
from __future__ import annotations

import re

# a parenthesis that opens with the process word, one level of nesting allowed
PAREN = re.compile(r"\s*\((?:[Pp]rompt|PROMPT|lượt|luot)\b(?:[^()]|\([^()]*\))*\)")
BARE_PROMPT = re.compile(r"\b[Pp]rompt \d+[a-z]?(?: [A-Z]\d?(?:\.\d+)?)?(?: and [A-Z]\d?)?(?:'s)?(?:, pass \d)?(?=\W|$)")
PROMPT_TOKEN = re.compile(r"CHUA_AP:prompt_[\w.]+|prompt_[\w.]+|xuat_luot\d+")
LUOT_N = re.compile(r"\(lượt \d+[^()]*\)|\blượt \d+(?=\s*[:;,.)]|$)")
SPACES = re.compile(r"[ \t]{2,}")
FAST = ("rompt", "ượt", "luot", "CHUA_AP")

# sheets whose cells are the game's own text
GAME_TEXT = {"Dia_phuong_hoa", "Dia_phuong_hoa_van_de", "Thoai", "Thoai_thong_ke_nhom", "Kich_ban_goc", "Nhiem_vu_radio",
             "Huong_dan", "Giay_phep_noi_dung", "Am_thanh_envelope", "Anh_the"}


def scrub_str(s: str) -> str:
    if not any(t in s for t in FAST):
        return s
    t = PAREN.sub("", s)
    t = LUOT_N.sub("", t)
    t = PROMPT_TOKEN.sub("", t)
    t = BARE_PROMPT.sub("", t)
    t = re.sub(r"\(\s*[,;:]?\s*\)", "", t)          # an emptied parenthesis
    t = re.sub(r"\s+([,.;:)])", r"\1", t)
    t = re.sub(r"([(])\s+", r"\1", t)
    t = re.sub(r"(?:[;,]\s*){2,}", "; ", t)
    t = re.sub(r"^\s*[;,:]\s*|\s*[;,:]\s*$", "", t)
    t = SPACES.sub(" ", t)
    return t.strip() if t != s else s


def scrub_obj(x):
    if isinstance(x, str):
        return scrub_str(x)
    if isinstance(x, list):
        return [scrub_obj(y) for y in x]
    if isinstance(x, dict):
        return {k: scrub_obj(v) for k, v in x.items()}
    return x

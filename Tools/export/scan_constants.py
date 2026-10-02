"""Hang_so_trong_ma (spec 5): every gameplay constant and hard-coded number in the game's C# (read only; changes no code).

    python Tools/export/scan_constants.py            # prints the counts by kind, domain and suggestion
    from scan_constants import scan, COLUMNS          # file 12 (d12) builds its sheet from scan(repo root)

Scanned: Assets/MachineBrigade/Scripts/Sim/** and Game/** (*.cs; Editor/ is tooling, left out). Comments and string
literals are blanked first, so a number in a comment, a text or a format string is never read.

Kinds (loai):
  const                 a const field                          static_readonly   a static readonly field (arrays too)
  mac_dinh_thuoc_tinh   a property's default (= x after { get; })   mac_dinh_doc_du_lieu   the default of a data read
                                                                  (.Float("key", x): used only when the data lacks the key)
  so_cung               a literal number in Sim/** and Game/Match/** code (0 and 1, array indexes and version
                        attributes left out). Rendering and UI files (Game/Hud, Effects, Rendering, Views, Audio, Input,
                        CameraControl) keep their declarations (domain 09 / 10 / 11, suggestion "khong") but not their
                        literals (layout numbers).
de_xuat_dua_ra_du_lieu (co / khong) is the scan's own suggestion, for the owner to review: "co" for a const / static
readonly / literal of the simulation (domains 01-08) in a damage, time, radius, threshold, chance, cap, rate or entity
limit context; "khong" for the view (09-11), the data reads' defaults (the data already carries the number), math
(epsilons, degrees, PI) and the rest.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

SCRIPTS = "Assets/MachineBrigade/Scripts"
SCAN_DIRS = ("Sim", "Game")
LITERAL_DIRS = ("Sim/", "Game/Match/")
VIEW_DIRS = {"Game/Hud/": "11", "Game/Effects/": "09", "Game/Audio/": "09", "Game/Rendering/": "10", "Game/Views/": "10",
             "Game/Input/": "11", "Game/CameraControl/": "11"}

COLUMNS = [
    ("tep", "", "file C# (đường dẫn trong repo)"),
    ("dong", "", "số dòng (1 = dòng đầu)"),
    ("ten", "", "tên hằng / thuộc tính / khóa dữ liệu; số cứng: hàm chứa nó"),
    ("gia_tri", "", "giá trị (số; biểu thức hoặc mảng: chữ, phần tử ngăn ';')"),
    ("ngu_canh", "", "dòng mã (cắt 160 ký tự)"),
    ("loai", "", "const / static_readonly / mac_dinh_thuoc_tinh / mac_dinh_doc_du_lieu / so_cung"),
    ("nhom", "", "sat_thuong / thoi_gian / ban_kinh / nguong / xac_suat / tran / tan_suat / gioi_han_thuc_the / khac"),
    ("linh_vuc", "", "file lĩnh vực liên quan 01-11"),
    ("de_xuat_dua_ra_du_lieu", "", "co / khong (đề xuất của bản quét, chủ dự án duyệt)"),
]

NUM = re.compile(r"(?<![\w.$])(-?)((?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)([fFdDmMuUlL]{0,2})(?![\w.])")
DECL_CONST = re.compile(r"\bconst\s+([\w.?<>\[\]]+)\s+(\w+)\s*=\s*([^;]+);", re.S)
DECL_STATIC = re.compile(r"\bstatic\s+readonly\s+([\w.?<>\[\],\s]+?)\s+(\w+)\s*=\s*([^;]+);", re.S)
DECL_PROP = re.compile(r"\bpublic\s+(?:static\s+)?(float|int|double|long)\??\s+(\w+)\s*\{[^{}]*\}\s*=\s*([^;]+);")
DATA_READ = re.compile(r"\.(Float|Int|Double)\(\s*\"(\w+)\"\s*,\s*(-?[\d.]+(?:[eE][+-]?\d+)?)[fFdD]?\s*\)")
MEMBER = re.compile(r"^\s*(?:\[[^\]]*\]\s*)*(?:(?:public|private|internal|protected|static|override|virtual|sealed|"
                    r"abstract|readonly|async|unsafe|partial|new|extern)\s+)+[\w.<>\[\],?() ]*?\b(\w+)\s*(?:\(|\{|=>|$)")
NUMERIC_TYPES = re.compile(r"\b(float|int|double|long|short|byte|uint|ulong|decimal)\b")

CATEGORY = [
    ("sat_thuong", r"damage|dmg|\bhp\b|health|hurt|heal|armou?r|pen(etration)?\b|blast|splash|kill"),
    ("thoi_gian", r"second|seconds|time|\bnow\b|cooldown|delay|duration|interval|timer|tick|wait|warn|reload|rearm|recharge|life"),
    ("ban_kinh", r"radius|range|distance|reach|metre|spacing|gap|width|length|height|altitude|leash|sight|vision|offset"),
    ("xac_suat", r"chance|random|probab|Next(Double|Float)?\(|roll|odds"),
    ("tran", r"\bcap\b|Cap\b|limit|ceiling|clamp"),
    ("tan_suat", r"rate|per ?second|\bhz\b|every|frequency|cadence|speed"),
    ("gioi_han_thuc_the", r"count|units|entities|pool|squad|wave|max\w*(count|units)|capacity|slots"),
    ("nguong", r"threshold|\bmin\b|\bmax\b|Min\w*|Max\w*|at least|above|below|share|ratio"),
]
GAMEPLAY = {"sat_thuong", "thoi_gian", "ban_kinh", "xac_suat", "tran", "tan_suat", "gioi_han_thuc_the", "nguong"}

DOMAIN_RULES = [  # (regex on the path under Assets/MachineBrigade/Scripts/, domain), first match wins
    (r"^Sim/(Combat|Strikes)/|Weapon|DamageTable|Armour|FirePower|SecondRounds|FixRules|Munition|Projectile|Ammo", "01"),
    (r"Boss|BigAttack|TierDefs|Naval|Escort|Catalog\.P(19|20|22)|^Sim/Bosses/", "03"),
    (r"Base(Rules|Sites|System|Loadout)|Tower|HqType|Fortress|Wall|Outpost", "04"),
    (r"^Sim/AI/|AiBehaviour|AiParams|AiModeProfile|Squads", "06"),
    (r"Campaign|Mission|Story|Narrative|Chapter|EventDefs|Dialog|Radio|FrontMap", "07"),
    (r"MapDefinition|^Sim/Navigation/|MapDressing|SpawnPoints|SeaRoute|Terrain|Transit", "08"),
    (r"^Sim/Economy/|MatchRules|OpeningRules|OpeningSquads|^Sim/Modes/|ModeSession|Showdown|Siege|Conquest|Weekly|Operations", "05"),
    (r"Gear|Commanders?\.cs|CommanderDefs|^Sim/(Entities|Abilities|Movement)/|Vehicle|Skill|Catalog|Definitions|Enums", "02"),
    (r"^Game/Match/(Player|Profile|Progression|Shop|Arsenal|Unlock|Rewards?|Coins|Chest)", "11"),
]


def _blank(text: str) -> str:
    """Comments and string / char literals replaced by spaces (newlines kept, so offsets and lines stay)."""
    out = list(text)
    i, n = 0, len(text)

    def wipe(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            wipe(i, j)
            i = j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            wipe(i, j)
            i = j
        elif c == '"' or (c in "@$" and i + 1 < n and text[i + 1] in '"@$'):
            j = i
            verbatim = False
            while j < n and text[j] in "@$":
                verbatim = verbatim or text[j] == "@"
                j += 1
            if j >= n or text[j] != '"':
                i += 1
                continue
            k = j + 1
            while k < n:
                if verbatim and text[k] == '"' and k + 1 < n and text[k + 1] == '"':
                    k += 2
                    continue
                if not verbatim and text[k] == "\\":
                    k += 2
                    continue
                if text[k] == '"' or (not verbatim and text[k] == "\n"):
                    break
                k += 1
            wipe(j + 1, min(k, n))
            i = k + 1
        elif c == "'":
            k = i + 1
            while k < n and k < i + 8 and text[k] != "'":
                k += 2 if text[k] == "\\" else 1
            wipe(i + 1, min(k, n))
            i = k + 1
        else:
            i += 1
    return "".join(out)


def _number(tok: str):
    t = tok.rstrip("fFdDmMuUlL")
    try:
        v = float(t)
    except ValueError:
        return None
    return int(v) if v.is_integer() and "." not in t and "e" not in t.lower() and abs(v) < 2 ** 53 else v


def _value(expr: str):
    expr = " ".join(expr.split())
    m = NUM.fullmatch(expr)
    if m:
        v = _number(m.group(2))
        return -v if m.group(1) else v
    nums = [(-1 if m.group(1) else 1) * _number(m.group(2)) for m in NUM.finditer(expr) if _number(m.group(2)) is not None]
    if expr.startswith(("{", "new")) and nums and re.fullmatch(r"[\w\[\]\s{}(),.\-+*/fFdD]*", expr):
        return ";".join(str(x) for x in nums)
    return expr[:160]


def _category(text: str) -> str:
    for cat, pat in CATEGORY:
        if re.search(pat, text, re.I):
            return cat
    return "khac"


def _domain(rel: str, text: str) -> str:
    for prefix, dom in VIEW_DIRS.items():
        if rel.startswith(f"{SCRIPTS}/{prefix}"):
            return dom
    sub = rel[len(SCRIPTS) + 1:]
    for pat, dom in DOMAIN_RULES:
        if re.search(pat, sub):
            return dom
    if re.search(r"weapon|damage|round|shell|missile", text, re.I):
        return "01"
    if re.search(r"boss", text, re.I):
        return "03"
    if re.search(r"tower|base|hq\b", text, re.I):
        return "04"
    return "05" if "/Sim/" in rel else "11"


def _mathy(v, ctx: str) -> bool:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if v != 0 and abs(v) < 1e-3:
            return True
        if abs(v) in (90, 180, 360, 1000, 255) and re.search(r"deg|rad|PI|angle|ms|colou?r|byte", ctx, re.I):
            return True
    return bool(re.search(r"\bMathF?\.PI\b|Deg2Rad|Rad2Deg|Epsilon", ctx))


def _suggest(kind: str, domain: str, cat: str, value, ctx: str) -> str:
    if domain in ("09", "10", "11") or kind == "mac_dinh_doc_du_lieu" or _mathy(value, ctx):
        return "khong"
    if kind in ("const", "static_readonly", "so_cung") and cat in GAMEPLAY:
        return "co"
    return "khong"


def scan(root: Path) -> list[dict]:
    """Every row of Hang_so_trong_ma, sorted by file, line and column (deterministic)."""
    base = root / SCRIPTS
    rows = []
    files = sorted(p for d in SCAN_DIRS for p in (base / d).rglob("*.cs"))
    for path in files:
        rel = path.relative_to(root).as_posix()
        raw = path.read_text("utf-8-sig")
        raw_lines = raw.splitlines()
        text = _blank(raw)
        lines = text.splitlines()
        starts = [0]
        for ln in text.split("\n"):
            starts.append(starts[-1] + len(ln) + 1)

        def line_of(off):
            lo, hi = 0, len(starts) - 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if starts[mid] <= off:
                    lo = mid
                else:
                    hi = mid - 1
            return lo + 1

        def context(ln):
            return " ".join(raw_lines[ln - 1].split())[:160] if 0 < ln <= len(raw_lines) else ""

        taken = set()  # (line, col) of literals inside declarations

        def add(kind, ln, col, name, value, ctx_text):
            dom = _domain(rel, name + " " + ctx_text)
            cat = _category(name + " " + ctx_text)
            rows.append({"id": f"{rel}:{ln}:{col}", "tep": rel, "dong": ln, "cot": col, "ten": name, "gia_tri": value,
                         "ngu_canh": ctx_text, "loai": kind, "nhom": cat, "linh_vuc": dom,
                         "de_xuat_dua_ra_du_lieu": _suggest(kind, dom, cat, value, name + " " + ctx_text)})

        for rx, kind, numeric_type in ((DECL_CONST, "const", True), (DECL_STATIC, "static_readonly", True),
                                       (DECL_PROP, "mac_dinh_thuoc_tinh", False)):
            for m in rx.finditer(text):
                typ, name, expr = m.group(1), m.group(2), m.group(3)
                if numeric_type and not NUMERIC_TYPES.search(typ):
                    continue
                if not NUM.search(expr):
                    continue
                if kind == "static_readonly" and not NUMERIC_TYPES.search(typ):
                    continue
                ln = line_of(m.start(2))
                end_ln = line_of(m.end())
                for k in range(ln, end_ln + 1):
                    taken.add(k)
                add(kind, ln, m.start(2) - starts[ln - 1] + 1, name, _value(expr), context(ln))
        for k, ln_text in enumerate(raw_lines, start=1):
            if k > len(lines) or ".Float(" not in lines[k - 1] and ".Int(" not in lines[k - 1] and ".Double(" not in lines[k - 1]:
                continue
            for m in DATA_READ.finditer(ln_text):
                add("mac_dinh_doc_du_lieu", k, m.start(2) + 1, m.group(2), _number(m.group(3)), context(k))
                taken.add((k, "data"))
        if not any(rel.startswith(f"{SCRIPTS}/{d}") for d in LITERAL_DIRS):
            continue
        member = ""
        enum_lines = set()
        for m in re.finditer(r"\benum\s+\w+[^{]*\{[^}]*\}", text):
            enum_lines.update(range(line_of(m.start()), line_of(m.end()) + 1))
        for k, ln_text in enumerate(lines, start=1):
            mm = MEMBER.match(ln_text)
            if mm and not re.match(r"^\s*(using|namespace|return|if|for|while|switch|case|var)\b", ln_text):
                member = mm.group(1)
            if k in taken or (k, "data") in taken or k in enum_lines:
                continue
            s = ln_text.strip()
            if not s or s.startswith(("[", "#", "using ")):
                continue
            for m in NUM.finditer(ln_text):
                v = _number(m.group(2))
                if v is None:
                    continue
                if m.group(1):
                    v = -v
                if v in (0, 1, -1):
                    continue
                before = ln_text[:m.start()].rstrip()
                if before.endswith("[") and re.search(r"\w\[$", before):
                    continue  # an index
                add("so_cung", k, m.start() + 1, member, v, context(k))
    rows.sort(key=lambda r: (r["tep"], r["dong"], r["cot"]))
    seen = set()
    out = []
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    rows = scan(root)
    print(f"Hang_so_trong_ma: {len(rows)} rows")
    for key in ("loai", "linh_vuc", "de_xuat_dua_ra_du_lieu", "nhom"):
        print(f"  {key}: {dict(sorted(collections.Counter(r[key] for r in rows).items()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

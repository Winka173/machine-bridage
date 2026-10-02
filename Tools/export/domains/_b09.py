"""09_hieu_ung_am_thanh, layer B (pass 5 part 2): Am_thanh_so_do (each clip's measured loudness, peak, low-end share, tail
and "keng" test from Docs/audio/metrics.json, Tools/sfx/analyze_sfx.py's report, as data; the keng verdict re-derived by
a live formula from the measured prominence / decay / width and the tool's thresholds), Am_thanh_so_do_bac (the per-size
table, which must rise steadily: louder, deeper, longer; the rise test live) and VFX_ngan_sach (the effects' concurrency
budget by tier from TierFx.cs FullCap / Weight / Busy / ShakeAt, the big smoke columns, the particle caps).

The audio numbers are not re-measured (owner rule 30/09); bao_cao_cu marks a clip changed after the report's commit."""
from __future__ import annotations

import json
import re

from core.formula import F, q, ref as R
from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _layer_b as LB

METRICS = "Docs/audio/metrics.json"
TOOL = "Tools/sfx/analyze_sfx.py"
AUDIO = "Assets/MachineBrigade/Resources/Audio"
TIERFX = LB.SCRIPTS + "Game/Effects/TierFx.cs"
SMOKE = LB.SCRIPTS + "Game/Effects/ImpactSmoke.cs"
EFFECTS = LB.SCRIPTS + "Game/Effects/"
CLIP_COLS = [("do_dai_s", "seconds", "s", "độ dài đo"), ("lufs", "lufs", "LUFS", "độ to tích hợp (ITU-R BS.1770-4)"),
             ("lufs_mmax", "lufs_mmax", "LUFS", "độ to 400 ms lớn nhất (M-max)"), ("dinh_db", "peak", "dBFS", "đỉnh mẫu"),
             ("dinh_that_db", "true_peak", "dBFS", "đỉnh thật (x4)"), ("duoi_150hz_pct", "sub150", "%", "tỷ lệ năng lượng dưới 150 Hz"),
             ("duoi_s", "tail", "s", "đuôi: từ đỉnh tới khi tụt 40 dB"), ("keng_noi_db", "keng_prominence", "dB",
                                                                            "độ nổi của đỉnh 2-6 kHz so với trung vị 1/3 octave"),
             ("keng_tat_s", "keng_decay", "s", "thời gian đỉnh tụt 20 dB"), ("keng_rong_hz", "keng_width", "Hz", "bề rộng -6 dB của đỉnh"),
             ("keng_tan_so_hz", "keng_hz", "Hz", "tần số đỉnh"), ("keng_bao_cao", "keng", "", "kết luận keng của bản đo")]


def _tool_consts(ctx):
    text = (ROOT / TOOL).read_text("utf-8") if (ROOT / TOOL).exists() else ""
    out = {}
    for k in ("KENG_PROMINENCE", "KENG_DECAY", "KENG_WIDTH"):
        m = re.search(rf"^{k} = ([\d.]+)", text, re.M)
        out[k] = float(m.group(1)) if m else None
        if m is None:
            ctx.issue(f"09 Am_thanh_so_do: {TOOL} {k} not found")
    return out


def _ternary(ctx, path: str, name: str):
    """A C# tier switch written as `Name(int tier) => tier >= 5 ? a : tier == 4 ? b : ... : default;`: a Python function."""
    g, line = LB.cs_find(ctx, path, rf"\b{name}\(int tier\) => ([^;]+);", what=f"TierFx.{name}")
    if g is None:
        return None, path
    expr = g[0]
    arms = re.findall(r"tier (>=|==|<=|>|<) (\d+) \? ([\w.]+?)f? :", expr)
    tail = expr.rsplit(":", 1)[-1].strip().rstrip("f")
    ops = {">=": lambda a, b: a >= b, "==": lambda a, b: a == b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,
           "<": lambda a, b: a < b}

    def val(s):
        return "" if s == "int.MaxValue" else float(s)

    def fn(t):
        for op, n, v in arms:
            if ops[op](t, int(n)):
                return val(v)
        return val(tail)
    return fn, f"{LB.short(path)}:{line}"


def build(ctx, book):
    at = book.sheets["Am_thanh"]
    m = json.loads((ROOT / METRICS).read_text("utf-8")) if (ROOT / METRICS).exists() else {}
    if not m:
        ctx.issue(f"09 Am_thanh_so_do: {METRICS} missing")
    k = _tool_consts(ctx)
    commits = LB.git_last_commit([AUDIO, METRICS])
    report_t = commits.get(METRICS, (0, ""))[0]

    # ------------------------------------------------------------------ Am_thanh_so_do
    sd = book.sheet("Am_thanh_so_do", "Âm thanh: số đo", "Mỗi clip trận (không gồm nhạc): LUFS, đỉnh dB, tỷ lệ năng lượng dưới 150 Hz, "
                    "đuôi, phát hiện 'keng' (Docs/audio/metrics.json của Tools/sfx/analyze_sfx.py); keng tính lại bằng công thức từ "
                    "số đo và ngưỡng của công cụ; keng ngoài nhóm kim loại giáp", layer="B")
    sd.col("id", fk=["09_hieu_ung_am_thanh/Am_thanh"], meaning="clip (Am_thanh.id)")
    for c, _key, unit, meaning in CLIP_COLS:
        sd.col(c, unit=unit, meaning=meaning, source_note=f"{METRICS} ({TOOL})")
    sd.col("bao_cao_cu", meaning="file clip đổi sau commit của báo cáo (git): số đo có thể cũ")
    T = {
        "keng": (f"=AND({{keng_noi_db}}>={k['KENG_PROMINENCE']},{{keng_tat_s}}>={k['KENG_DECAY']},{{keng_rong_hz}}<{k['KENG_WIDTH']})"),
        "keng_ngoai_giap": f"=AND({{keng}},{R('Am_thanh', 'nhom')}<>{q('armour_metal')})",
    }
    LB.declare(sd, "keng", T["keng"], f"{TOOL} keng(): độ nổi >= {k['KENG_PROMINENCE']} dB, tắt >= {k['KENG_DECAY']} s, rộng < {k['KENG_WIDTH']} Hz",
               game=False, meaning="keng tính lại từ số đo (số trong báo cáo đã làm tròn: xem keng_bao_cao)")
    LB.declare(sd, "keng_ngoai_giap", T["keng_ngoai_giap"], f"{TOOL} keng_outside_armour", game=False,
               meaning="keng ở clip ngoài nhóm armour_metal (bản kiểm --check báo lỗi)")
    for rel, x in sorted((m.get("clips") or {}).items()):
        rid = rel.rsplit(".", 1)[0]
        if rid not in at.rows:
            ctx.issue(f"09 Am_thanh_so_do: {rel} not in Am_thanh")
            continue
        r = sd.row(rid, f"{METRICS}: clips[\"{rel}\"]")
        for c, key, _u, _m in CLIP_COLS:
            r.set(c, x.get(key, ""))
        t = commits.get(f"{AUDIO}/{rel}", (0, ""))[0]
        r.set("bao_cao_cu", t > report_t)
        kg = (x.get("keng_prominence", 0) >= k["KENG_PROMINENCE"] and x.get("keng_decay", 0) >= k["KENG_DECAY"] and
              x.get("keng_width", 0) < k["KENG_WIDTH"])
        LB.put(r, "keng", T["keng"], kg, game=False)
        LB.put(r, "keng_ngoai_giap", T["keng_ngoai_giap"], kg and at.rows[rid].values.get("nhom") != "armour_metal", game=False)

    # ------------------------------------------------------------------ Am_thanh_so_do_bac
    sb = book.sheet("Am_thanh_so_do_bac", "Âm thanh: bảng theo bậc cỡ", "Mỗi bậc cỡ x vai (bắn / nổ): trung bình M-max, LUFS, tỷ lệ "
                    "dưới 150 Hz, đuôi của các bank hàng đó (metrics.json sizes); phải tăng đều từ <= 14,5 mm tới siêu vũ khí", layer="B")
    sb.col("bac_co", meaning="bậc cỡ s0-s4 / bomb / s406 / super")
    sb.col("vai", meaning="shot (bắn) / blast (nổ, trúng)", enum=["shot", "blast"])
    sb.col("ten", meaning="tên bậc (cỡ nòng)")
    for c, unit, meaning in (("lufs_mmax", "LUFS", "M-max trung bình"), ("lufs", "LUFS", "LUFS trung bình"),
                             ("duoi_150hz_pct", "%", "tỷ lệ dưới 150 Hz trung bình"), ("duoi_s", "s", "đuôi trung bình"),
                             ("bank", "", "bank của hàng (ngăn ';')"), ("bac_truoc", "", "hàng trước cùng vai (trống: đầu bảng)")):
        sb.col(c, unit=unit, meaning=meaning, source_note=f"{METRICS} sizes ({TOOL})")
    LB.declare(sb, "tang_deu", "=AND({lufs_mmax}>{lufs_mmax@<hàng trước>},{duoi_150hz_pct}>{duoi_150hz_pct@<hàng trước>},{duoi_s}>{duoi_s@<hàng trước>})",
               f"{TOOL} rises(): to hơn, trầm hơn, dài hơn hàng trước", game=False,
               meaning="tăng đều so với bậc trước cùng vai (trống: hàng đầu)")
    bad = set(m.get("not_rising") or [])
    for role in ("shot", "blast"):
        prev = None
        for i, row in enumerate(m.get("sizes") or []):
            v = row.get(role)
            if not v:
                continue
            rid = f"{role}/{row['size']}"
            r = sb.row(rid, f"{METRICS}: sizes[{i}].{role}")
            for c, val in (("bac_co", row["size"]), ("vai", role), ("ten", row.get("name", "")), ("lufs_mmax", v.get("lufs_mmax")),
                           ("lufs", v.get("lufs")), ("duoi_150hz_pct", v.get("sub150")), ("duoi_s", v.get("tail")),
                           ("bank", ";".join(v.get("banks") or [])), ("bac_truoc", prev[0] if prev else "")):
                r.set(c, val)
            if prev:
                pv = prev[1]
                ok = v["lufs_mmax"] > pv["lufs_mmax"] and v["sub150"] > pv["sub150"] and v["tail"] > pv["tail"]
                rep = not any(b.startswith(f"{role} ") and f"-> {row['size']} " in b for b in bad)
                if ok != rep:
                    ctx.issue(f"09 Am_thanh_so_do_bac {rid}: rise {ok} but the report says {rep}")
                t = (f"=AND({{lufs_mmax}}>{R('', 'lufs_mmax', prev[0])},{{duoi_150hz_pct}}>{R('', 'duoi_150hz_pct', prev[0])},"
                     f"{{duoi_s}}>{R('', 'duoi_s', prev[0])})")
                LB.put(r, "tang_deu", t, ok, game=False)
            else:
                LB.put(r, "tang_deu", f"={q('')}", "", game=False)
            prev = (rid, v)

    # ------------------------------------------------------------------ VFX_ngan_sach
    vn = book.sheet("VFX_ngan_sach", "VFX: ngân sách", "Ngân sách hiệu ứng: theo bậc T0-T5 (TierFx.cs: số vụ nổ chi tiết đầy đủ cùng lúc "
                    "FullCap, trọng số với trần WeightCap, thời gian tính là đang chạy Busy, rung camera ShakeAt), cột khói lớn tối đa "
                    "(ImpactSmoke.BigColumns, spec: 3), tổng hạt tối đa của các bộ phát có số cố định (VFX_ngan_sach_hat)", layer="B")
    vn.col("loai", meaning="bac (một bậc) / khoi_lon / hat_tong", enum=["bac", "khoi_lon", "hat_tong"])
    funcs = {}
    for c, name, unit, meaning in (("toan_chi_tiet_toi_da", "FullCap", "", "vụ nổ chi tiết đầy đủ cùng lúc tối đa (trống: không trần)"),
                                   ("trong_so", "Weight", "", "trọng số một vụ nổ chi tiết đầy đủ"),
                                   ("ban_s", "Busy", "s", "thời gian một vụ nổ tính là đang chạy"),
                                   ("rung_tai_no", "ShakeAt", "", "rung camera tại vụ nổ (bắn: x ShotShare)")):
        fn, cite = _ternary(ctx, TIERFX, name)
        funcs[c] = (fn, cite)
        vn.col(c, unit=unit, meaning=f"{meaning} (TierFx.{name}, port của biểu thức theo bậc)", source_note=f"C#: {cite}")
    for c, pat, meaning in (("tran_trong_so", r"public const float WeightCap = " + r"([\d.]+)f", "trần tổng trọng số (TierFx.WeightCap)"),
                            ("he_so_rung_khi_ban", r"public const float ShotShare = ([\d.]+)f", "phần rung khi bắn (TierFx.ShotShare)")):
        vn.col(c, meaning=meaning, source_note="C#: " + TIERFX)
    vn.col("gioi_han_ma", meaning="giới hạn trong mã (khói lớn: ImpactSmoke.BigColumns)", source_note="C#")
    vn.col("yeu_cau", meaning="yêu cầu của spec (khói lớn tối đa 3)")
    vn.col("nguon_ma", meaning="file:dòng")
    wc, cw = LB.cs_num(ctx, TIERFX, r"public const float WeightCap = ([\d.]+)f", what="TierFx.WeightCap")
    ss, cs_ = LB.cs_num(ctx, TIERFX, r"public const float ShotShare = ([\d.]+)f", what="TierFx.ShotShare")
    isn = lambda e: f"ISNUMBER({e})"  # noqa: E731
    VT = {
        "dong_thoi_theo_trong_so": f"=IF(AND({isn('{trong_so}')},{{trong_so}}>0),FLOOR({{tran_trong_so}}/{{trong_so}},1),{q('')})",
        "dong_thoi_toi_da": (f"=IF({isn('{toan_chi_tiet_toi_da}')},IF({isn('{dong_thoi_theo_trong_so}')},MIN({{toan_chi_tiet_toi_da}},"
                             f"{{dong_thoi_theo_trong_so}}),{{toan_chi_tiet_toi_da}}),{q('')})"),
        "rung_khi_ban": f"=IF({isn('{rung_tai_no}')},{{rung_tai_no}}*{{he_so_rung_khi_ban}},{q('')})",
        "dat": f"=IF(AND({isn('{gioi_han_ma}')},{isn('{yeu_cau}')}),{{gioi_han_ma}}<={{yeu_cau}},{q('')})",
    }
    for c, unit, meaning in (("dong_thoi_theo_trong_so", "", "vụ nổ cùng bậc cùng lúc theo trần trọng số (WeightCap / Weight)"),
                             ("dong_thoi_toi_da", "", "vụ nổ chi tiết đầy đủ cùng lúc tối đa: min(FullCap, WeightCap / Weight)"),
                             ("rung_khi_ban", "", "rung camera khi bắn (ShakeAt x ShotShare)"),
                             ("dat", "", "giới hạn trong mã <= yêu cầu")):
        LB.declare(vn, c, VT[c], f"{TIERFX} (FullCap, Weight, WeightCap, ShakeAt, ShotShare)", unit=unit, meaning=meaning, game=False)
    for t in range(6):
        x = vn.row(f"T{t}", "C#: " + "; ".join(sorted({cite for _f, cite in funcs.values()} | {cw, cs_})))
        x.set("loai", "bac")
        vals = {}
        for c, (fn, _cite) in funcs.items():
            vals[c] = fn(t) if fn else NEED_CODE_CHECK
            x.set(c, vals[c])
        x.set("tran_trong_so", wc)
        x.set("he_so_rung_khi_ban", ss)
        w = vals["trong_so"]
        by_w = float(int(wc // w)) if isinstance(w, float) and w > 0 and isinstance(wc, float) else ""
        fc = vals["toan_chi_tiet_toi_da"]
        mx = (min(fc, by_w) if by_w != "" else fc) if isinstance(fc, float) else ""
        sh = vals["rung_tai_no"] * ss if isinstance(vals["rung_tai_no"], float) and isinstance(ss, float) else ""
        for c, v in (("dong_thoi_theo_trong_so", by_w), ("dong_thoi_toi_da", mx), ("rung_khi_ban", sh), ("dat", "")):
            LB.put(x, c, VT[c], v, game=False)
    big, cb = LB.cs_num(ctx, SMOKE, r"public const int BigColumns = (\d+)", what="ImpactSmoke.BigColumns")
    x = vn.row("khoi_lon", f"C#: {cb}; spec 09 VFX_ngan_sach")
    x.set("loai", "khoi_lon")
    x.set("gioi_han_ma", big)
    x.set("yeu_cau", 3.0)
    x.set("nguon_ma", cb)
    for c in ("dong_thoi_theo_trong_so", "dong_thoi_toi_da", "rung_khi_ban"):
        LB.put(x, c, VT[c], "", game=False)
    LB.put(x, "dat", VT["dat"], big <= 3.0 if isinstance(big, float) else "", game=False)

    # ------------------------------------------------------------------ VFX_ngan_sach_hat (maxParticles literals)
    vh = book.sheet("VFX_ngan_sach_hat", "VFX: trần hạt mỗi bộ phát", "Mọi chỗ Game/Effects đặt maxParticles bằng một số cố định "
                    "(file:dòng); bộ phát đặt theo biến (max) không có số cố định", layer="B")
    vh.col("tep", meaning="file C#")
    vh.col("dong", meaning="dòng")
    vh.col("hat_toi_da", meaning="maxParticles (số cố định)", source_note="C#: Game/Effects")
    total = 0.0
    for p in sorted((ROOT / EFFECTS).glob("*.cs")):
        rel = p.relative_to(ROOT).as_posix()
        for i, ln in enumerate(p.read_text("utf-8-sig").splitlines(), start=1):
            mm = re.search(r"\.maxParticles = (\d+);", ln)
            if mm and not ln.strip().startswith("//"):
                r = vh.row(f"{LB.short(rel)}:{i}", f"{LB.short(rel)}:{i}")
                r.set("tep", LB.short(rel))
                r.set("dong", i)
                r.set("hat_toi_da", float(mm.group(1)))
                total += float(mm.group(1))
    x = vn.row("hat_tong", "VFX_ngan_sach_hat (tổng)")
    x.set("loai", "hat_tong")
    x.set("gioi_han_ma", F(f"=SUM({R('VFX_ngan_sach_hat', 'hat_toi_da', '*')})", expect=total, ref="python: tổng maxParticles cố định"))
    x.set("nguon_ma", "VFX_ngan_sach_hat")
    for c in ("dong_thoi_theo_trong_so", "dong_thoi_toi_da", "rung_khi_ban", "dat"):
        LB.put(x, c, VT[c], "", game=False)

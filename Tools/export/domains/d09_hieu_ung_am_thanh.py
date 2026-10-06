"""09_hieu_ung_am_thanh, layer A: every audio clip, the sound library banks (Tools/sfx/library.json), the clip envelopes,
the rapid-fire burst table, effects by tier (TierFx.Fire, EffectLife.Bands), hull fire looks, post-processing
(BattlefieldProfile.asset); code-only parts (wrecks, mixer) marked."""
from __future__ import annotations

import importlib
import json
import re
import struct
import sys

from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _b09
from . import _lane_c as C

FILE_ID = "09_hieu_ung_am_thanh"
TITLE = "Hiệu ứng và âm thanh"
DESC = "Clip âm thanh, bank thư viện, envelope, bảng loạt bắn nhanh, VFX theo bậc, lửa thân xe, hậu kỳ hình ảnh; xác vỡ / mixer (mã)"

AUDIO = "Assets/MachineBrigade/Resources/Audio/"
LIBRARY = "Tools/sfx/library.json"
ENVELOPES = AUDIO + "sfx/envelopes.txt"
PROFILE = "Assets/MachineBrigade/Settings/BattlefieldProfile.asset"
TIERFX = "Assets/MachineBrigade/Scripts/Game/Effects/TierFx.cs"
LIFE = "Assets/MachineBrigade/Scripts/Game/Effects/EffectLife.cs"
HULLFIRE = "Assets/MachineBrigade/Scripts/Game/Effects/HullFire.cs"
SOUNDLIB = "Assets/MachineBrigade/Scripts/Game/Audio/SoundLibrary.cs"
UNITY_META = {"_class", "_file_id", "m_ObjectHideFlags", "m_CorrespondingSourceObject", "m_PrefabInstance", "m_PrefabAsset",
              "m_GameObject", "m_Script", "m_EditorHideFlags", "m_EditorClassIdentifier"}


def _ogg_info(path) -> tuple[float | str, int | str, int | str]:
    """(length s, channels, sample rate) from the Ogg Vorbis headers and the last page's granule position."""
    try:
        data = path.read_bytes()
        i = data.find(b"\x01vorbis")
        if i < 0:
            return "", "", ""
        channels = data[i + 11]
        rate = struct.unpack_from("<I", data, i + 12)[0]
        last = data.rfind(b"OggS")
        granule = struct.unpack_from("<q", data, last + 6)[0]
        return (round(granule / rate, 3) if rate else ""), channels, rate
    except (OSError, struct.error, IndexError):
        return "", "", ""


LICENSE_STATES = ("ASSET_LICENSE_OK", "ASSET_LICENSE_MISSING")
SOURCE_STATES = ("ASSET_SOURCE_OK", "ASSET_SOURCE_MISSING")
REALISM_STATES = ("REALISM_REFERENCE_OK", "REALISM_REFERENCE_NEEDS_SOURCE", "NOT_APPLICABLE")


def _credits():
    """{file relative to Audio/: (length, author, source, licence)} from Audio/CREDITS.md and Music/MUSIC_CREDITS.md."""
    out = {}
    for rel, prefix in (("CREDITS.md", ""), ("Music/MUSIC_CREDITS.md", "Music/")):
        p = ROOT / AUDIO / rel
        if not p.exists():
            continue
        for _line, header, rows in C.md_tables(p.read_text("utf-8")):
            h = [x.lower() for x in header]
            if not h or h[0] != "file":
                continue
            for _ln, cells in rows:
                f = C.clean_md(cells[0])
                rec = dict(zip(h, (C.clean_md(c) for c in cells)))
                out[prefix + f] = (AUDIO + rel, rec)
    return out


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    lib = ctx.data(LIBRARY) if LIBRARY in ctx.sources else {}
    banks = lib.get("banks") or {}
    credits = _credits()

    # ------------------------------------------------------------------ Am_thanh (every clip)
    at = book.sheet("Am_thanh", "Âm thanh: clip", "Mỗi clip trong Resources/Audio một dòng: nhóm, bậc cỡ, đường dẫn, độ dài, "
                    "nén, nguồn, giấy phép (Audio/CREDITS.md, Music/MUSIC_CREDITS.md)")
    at.col("bank", meaning="thư mục bank (tên bank trong SoundLibrary)", fk=["09_hieu_ung_am_thanh/Am_thanh_bank"])
    for c, m in (("nhom", "nhóm (library.json banks.<bank>.group; thư mục gốc nếu không có trong thư viện)"),
                 ("bac_co", "bậc cỡ s0-s4 / bomb / s406 / super (library.json size)"),
                 ("duong_dan", "đường dẫn trong repo"), ("do_dai_s", "độ dài (granule cuối / tần số mẫu của Ogg Vorbis)"),
                 ("kenh", "số kênh"), ("tan_so_mau_hz", "tần số mẫu"), ("nen", "định dạng nén (đuôi file)"),
                 ("tac_gia", "tác giả / nhà phát hành (CREDITS)"), ("nguon_goc", "nguồn gốc (CREDITS; sfx: tổng hợp / trộn bởi Tools/sfx/build_sfx.py)"),
                 ("giay_phep", "giấy phép (CREDITS)")):
        at.col(c, unit="s" if c.endswith("_s") else "Hz" if c.endswith("_hz") else "", meaning=m)
    # MVA W1-B (spec part BJ): the asset's own legal / source status apart from the realism reference, so a legally sourced
    # clip is never held back because a real-sound comparison is not cited yet.
    for c, m, e in (("trang_thai_giay_phep", "assetLicenseStatus: giấy phép của chính tài sản", LICENSE_STATES),
                    ("trang_thai_nguon", "assetSourceStatus: nguồn của chính tài sản", SOURCE_STATES),
                    ("trang_thai_tham_chieu_that", "realismReferenceStatus: tham chiếu tiếng thật để so (không chặn tài sản)", REALISM_STATES)):
        at.col(c, meaning=m, enum=list(e))
    for sid in sorted(s for s, src in ctx.sources.items() if src.kind == "audio" and s.startswith(AUDIO)):
        relp = sid[len(AUDIO):]
        parts = relp.split("/")
        bank = parts[-2] if len(parts) >= 2 else ""
        rid = relp.rsplit(".", 1)[0]
        r = at.row(rid, sid)
        r.set("bank", bank if bank in banks else "")
        info = banks.get(bank) or {}
        r.set("nhom", info.get("group", parts[0] if len(parts) > 1 else ""))
        r.set("bac_co", info.get("size", ""))
        r.set("duong_dan", sid, sid, ("file",))
        length, ch, rate = _ogg_info(ctx.sources[sid].path) if sid.endswith(".ogg") else ("", "", "")
        r.set("do_dai_s", length)
        r.set("kenh", ch)
        r.set("tan_so_mau_hz", rate)
        r.set("nen", sid.rsplit(".", 1)[-1].lower())
        cred = credits.get(relp)
        if cred:
            rec = cred[1]
            r.set("tac_gia", rec.get("author / publisher", rec.get("title", "")))
            r.set("nguon_goc", rec.get("source", cred[0]))
            r.set("giay_phep", rec.get("licence", rec.get("license", "")))
        elif relp.startswith("sfx/"):
            r.set("nguon_goc", "tổng hợp / trộn bởi Tools/sfx/build_sfx.py (Audio/CREDITS.md)")
            r.set("giay_phep", "của dự án; lớp ghi âm theo Sonniss GDC (Audio/CREDITS.md)")
        elif relp.startswith("Music/"):
            r.set("nguon_goc", "nhạc gốc của dự án (Tools/music, Music/MUSIC_CREDITS.md)")
            r.set("giay_phep", "của dự án (Music/MUSIC_CREDITS.md)")
        lic, src = r.values.get("giay_phep"), r.values.get("nguon_goc")
        r.set("trang_thai_giay_phep", "ASSET_LICENSE_OK" if lic else "ASSET_LICENSE_MISSING")
        r.set("trang_thai_nguon", "ASSET_SOURCE_OK" if src else "ASSET_SOURCE_MISSING")
        # Music and UI have no real-world sound to match; combat sound has none cited in the repo yet.
        r.set("trang_thai_tham_chieu_that", "NOT_APPLICABLE" if relp.startswith(("Music/", "ui", "UI")) else "REALISM_REFERENCE_NEEDS_SOURCE")

    # ------------------------------------------------------------------ Am_thanh_bank (library.json)
    bk = book.sheet("Am_thanh_bank", "Âm thanh: bank", "Tools/sfx/library.json banks: nhóm, bậc cỡ, hàng, số biến thể")
    bk.col("so_clip", meaning="số clip trong thư mục bank (Am_thanh)")
    for r, _x, _p in C.keyed(bk, banks, LIBRARY, ("banks",)):
        r.set("so_clip", sum(1 for x in at.rows.values() if x.values.get("bank") == r.id))
    rest = {k: v for k, v in lib.items() if k != "banks"}
    if rest:
        kv = book.kv_sheet("Am_thanh_thu_vien", "Âm thanh: thư viện", "Tools/sfx/library.json: ghi chú (bậc cỡ theo cỡ nòng)")
        book.kv_rows(kv, rest, LIBRARY, (), "library")

    # ------------------------------------------------------------------ Am_thanh_envelope (envelopes.txt)
    ev = book.sheet("Am_thanh_envelope", "Âm thanh: envelope", "Audio/sfx/envelopes.txt: RMS mỗi 20 ms (50 Hz, x1000) của từng "
                    "clip cho compressor của Effects; dòng '#' là ghi chú")
    ev.col("clip", meaning="tên clip")
    ev.col("so_mau", meaning="số mẫu RMS")
    ev.col("rms_x1000", meaning="RMS x1000 mỗi 20 ms (ngăn ';')")
    if ENVELOPES in ctx.sources:
        for j, line in enumerate(ctx.data(ENVELOPES)):
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                r = ev.row(f"#{j + 1}", C.nguon(ENVELOPES, ("lines", j)))
                r.set("clip", "")
                r.set("rms_x1000", s, ENVELOPES, ("lines", j))
                continue
            name, *vals = s.split()
            r = ev.row(name, C.nguon(ENVELOPES, ("lines", j)))
            r.set("clip", name)
            r.set("so_mau", len(vals))
            r.set("rms_x1000", ";".join(vals), ENVELOPES, ("lines", j))

    # ------------------------------------------------------------------ Am_thanh_loat (SoundLibrary.Bursts)
    lo = book.sheet("Am_thanh_loat", "Âm thanh: loạt bắn nhanh", "SoundLibrary.Bursts: bank loạt, cỡ, nhịp (phát/s), số phát mỗi đoạn")
    sid, rows, lines = ctx.cs_table(SOUNDLIB, "Bursts")
    for i, item in enumerate(rows):
        r = lo.row(item[0] if isinstance(item, list) and item else i, f"{SOUNDLIB}:{lines[i] if i < len(lines) else ''} (Bursts[{i}])", raw=item)
        for j, name in enumerate(("bank", "co", "nhip_phat_s", "so_phat")):
            if isinstance(item, list) and j < len(item):
                r.set(name, item[j], sid, (i, j))

    # ------------------------------------------------------------------ VFX_bac (TierFx.Fire + EffectLife.Bands)
    vb = book.sheet("VFX_bac", "VFX theo bậc", "Bậc T0-T5: chớp đầu nòng, khói, vòng bụi, sóng nước, ánh sáng, giật (TierFx.Fire) "
                    "và thời gian cầu lửa, khói, hố (EffectLife.Bands); rung camera, hạt, LOD, đồng thời tối đa: hàm trong TierFx (mã)")
    vb.col("bac", meaning="bậc T0-T5")
    vb.col("rung_camera_dong_thoi", meaning="ShakeAt, FullCap, Weight, Busy: hàm theo bậc trong TierFx.cs; giá trị theo bậc ở VFX_ngan_sach (XEM_VFX_ngan_sach)")
    for path, array, prefix in ((TIERFX, "Fire", "ban_"), (LIFE, "Bands", "doi_")):
        sid, rows, lines = ctx.cs_table(path, array)
        for i, item in enumerate(rows):
            r = vb.rows.get(f"T{i}") or vb.row(f"T{i}", f"{TIERFX} (Fire), {LIFE} (Bands)")
            r.set("bac", i)
            if isinstance(item, dict):
                r.flatten(item, sid, (i,), prefix=prefix)
            else:
                C.cs_element_row(r, item, sid, (i,))
            r.set("rung_camera_dong_thoi", "XEM_VFX_ngan_sach")  # lane B pass 5: TierFx ShakeAt / FullCap / Weight / Busy ported there
    vc = book.sheet("VFX_chay_than_xe", "VFX: lửa thân xe", "HullFire.Looks: 3 mức lửa (thân, lưỡi lửa, khói, tàn, tia)")
    sid, rows, lines = ctx.cs_table(HULLFIRE, "Looks")
    for i, item in enumerate(rows):
        r = vc.row(i, f"{HULLFIRE}:{lines[i] if i < len(lines) else ''} (Looks[{i}])", raw=item)
        C.cs_element_row(r, item, sid, (i,))

    # ------------------------------------------------------------------ Hau_ky_hinh_anh (BattlefieldProfile.asset)
    hk = book.sheet("Hau_ky_hinh_anh", "Hậu kỳ hình ảnh", "Settings/BattlefieldProfile.asset: mỗi thiết lập của mỗi hiệu ứng "
                    "(Bloom, Tonemapping, Color Adjustments...) một dòng: ghi đè, giá trị; trường Unity nội bộ ở Khong_xuat")
    hk.col("hieu_ung", meaning="hiệu ứng (m_Name)")
    hk.col("thiet_lap", meaning="thiết lập")
    hk.col("ghi_de", meaning="m_OverrideState (1 = dùng giá trị này)")
    hk.col("gia_tri", meaning="m_Value")
    if PROFILE in ctx.sources:
        ctx.exclude(PROFILE, "docs[*].MonoBehaviour.components._items[*].*",
                    "VolumeProfile.components: id tài liệu Unity của các hiệu ứng (siêu dữ liệu; mỗi hiệu ứng là một dòng ở Hau_ky_hinh_anh)",
                    origin="domains/d09")
        for i, doc in enumerate((ctx.data(PROFILE) or {}).get("docs") or []):
            for cls, body in doc.items():
                if cls in UNITY_META or not isinstance(body, dict):
                    continue
                name = body.get("m_Name") or f"{cls}{i}"
                for k, v in body.items():
                    if k in UNITY_META or (k == "components" and isinstance(v, dict) and set(v) == {"_items"}):
                        continue
                    p = ("docs", i, cls, k)
                    r = hk.row(f"{name}.{k}" if name else f"{i}.{k}", C.nguon(PROFILE, p), raw=v)
                    r.set("hieu_ung", name)
                    r.set("thiet_lap", k)
                    if isinstance(v, dict) and v:
                        for kk, vv in v.items():
                            col = {"m_OverrideState": "ghi_de", "m_Value": "gia_tri"}.get(kk, kk)
                            if isinstance(vv, dict):
                                r.flatten(vv, PROFILE, p + (kk,), prefix=f"{col}_")
                            else:
                                r.set(col, vv, PROFILE, p + (kk,))
                    else:
                        r.set("gia_tri", "" if isinstance(v, dict) else v, PROFILE, p)

    # ------------------------------------------------------------------ code-only / later passes
    C.marker_sheet(book, "Xac_vo", "Xác vỡ", "Mỗi lớp xe: kiểu vỡ, biến thể, thời gian tồn tại, ảnh hưởng lối chơi (không: chỉ hình)",
                   NEED_CODE_CHECK, "Assets/MachineBrigade/Scripts/Game/Effects/WreckClasses.cs (2-3 biến thể mỗi lớp, chọn theo id; "
                   "DECISIONS 'Play-test 12 (lane B)'); không có bảng dữ liệu", "Assets/MachineBrigade/Scripts/Game/Effects/WreckClasses.cs")
    C.marker_sheet(book, "Am_thanh_mixer", "Âm thanh: mixer", "Nhóm, ưu tiên, số kênh tối đa, compressor / limiter, giảm theo khoảng cách",
                   NEED_CODE_CHECK, "AudioDirector.cs / EffectsLimiter.cs (hằng trong mã; Docs/audio/metrics.md)",
                   "Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.cs")
    _samples(book)
    _fx_shots(ctx, book)

    # ------------------------------------------------------------------ layer B (lane B, pass 5 part 2)
    _b09.build(ctx, book)


# ---------------------------------------------------------------------------------------------- Am_thanh_mau (Docs/audio)
SAMPLES = "Docs/audio/samples/"
MIX_ORDER = ("normal_battle", "boss_battle", "crowded_battle")
LOUD_BELOW = 6.0  # LU under the mix's loudest 400 ms: louder than this is a loud moment
LOUD_GAP = 2.0  # s between two marks
LOUD_MAX = 8  # marks a mix


def _analyzer():
    """Tools/sfx/analyze_sfx (BS.1770 K-weighting, soundfile, scipy) or None when those packages are missing."""
    path = str(ROOT / "Tools" / "sfx")
    if path not in sys.path:
        sys.path.insert(0, path)
    try:
        return importlib.import_module("analyze_sfx")
    except ImportError:
        return None


def _loud_moments(az, path):
    """(momentary max LUFS, [(centre s, 400 ms LUFS, sample peak dBFS, rank)]): the loudest 400 ms windows (100 ms
    hop, K-weighted mono mix as Tools/sfx/render_mix.py measures it) within LOUD_BELOW LU of the loudest, LOUD_GAP s
    apart, at most LOUD_MAX, in time order."""
    import numpy as np
    stereo, sr = az.sf.read(str(path), dtype="float64", always_2d=True)
    y = az.k_weight(stereo.mean(axis=1), sr)
    block, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < block:
        return "", []
    cs = np.concatenate([[0.0], np.cumsum(y * y)])
    starts = np.arange(0, len(y) - block + 1, hop)
    lk = -0.691 + 10 * np.log10(np.maximum((cs[starts + block] - cs[starts]) / block, 1e-20))
    top = float(lk.max())
    chosen = []
    for i in np.argsort(-lk, kind="stable"):
        if lk[i] < top - LOUD_BELOW or len(chosen) == LOUD_MAX:
            break
        if all(abs(int(starts[i]) - int(starts[j])) >= LOUD_GAP * sr for j in chosen):
            chosen.append(int(i))
    marks = []
    for rank, i in enumerate(chosen, 1):
        a = int(starts[i])
        peak = float(np.max(np.abs(stereo[a:a + block])))
        marks.append((round((a + block / 2) / sr, 1), round(float(lk[i]), 1),
                      round(20 * float(np.log10(peak)), 1) if peak > 0 else -120.0, rank))
    return round(top, 1), sorted(marks)


def _samples(book):
    """Am_thanh_mau: the three offline battle mixes of Tools/sfx/render_mix.py (Docs/audio/samples/*.ogg, mixes.json)
    and, in Am_thanh_mau_moc, their loud moments (computed from the .ogg here, the same K-weighting as analyze_sfx)."""
    sh = book.sheet("Am_thanh_mau", "Âm thanh: bản ghi mẫu", "Docs/audio/samples: 3 bản trộn trận mẫu (Tools/sfx/render_mix.py): "
                    "file, độ dài, số sự kiện / phát / cắt, limiter, compressor, độ to (mixes.json); mốc tiếng lớn ở "
                    "Am_thanh_mau_moc")
    for c, unit, m in (("tep", "", "file ghi âm (repo)"), ("do_dai_s", "s", "độ dài (Ogg granule cuối / tần số mẫu)"),
                       ("kenh", "", "số kênh"), ("tan_so_mau_hz", "Hz", "tần số mẫu"),
                       ("lufs_mmax_tinh", "LUFS", "400 ms to nhất tính lại từ file .ogg ở đây; mixes.json lufs_mmax đo trước khi nén Vorbis nên lệch 0.1-0.2 LU"),
                       ("so_moc", "", "số mốc tiếng lớn (Am_thanh_mau_moc)")):
        sh.col(c, unit=unit, meaning=m)
    mc = book.sheet("Am_thanh_mau_moc", "Âm thanh mẫu: mốc tiếng lớn", f"Mỗi bản trộn: các cửa sổ 400 ms to nhất (bước 100 ms, "
                    f"K-weighting BS.1770 của Tools/sfx/analyze_sfx.py trên kênh trộn mono) không dưới {LOUD_BELOW:g} LU so với "
                    f"cửa sổ to nhất, cách nhau >= {LOUD_GAP:g} s, tối đa {LOUD_MAX}; theo thời gian", parent=sh)
    for c, unit, m in (("thoi_diem_s", "s", "giữa cửa sổ 400 ms (giây từ đầu file)"), ("lufs_400ms", "LUFS", "độ to cửa sổ"),
                       ("duoi_to_nhat_lu", "LU", "dưới cửa sổ to nhất của bản trộn"),
                       ("dinh_dbfs", "dBFS", "đỉnh mẫu trong cửa sổ (2 kênh)"), ("hang", "", "thứ hạng độ to (1 = to nhất)")):
        mc.col(c, unit=unit, meaning=m)
    folder = ROOT / SAMPLES
    report = json.loads((folder / "mixes.json").read_text("utf-8")) if (folder / "mixes.json").exists() else {}
    names = [n for n in MIX_ORDER if (folder / f"{n}.ogg").exists() or n in report]
    names += sorted(p.stem for p in folder.glob("*.ogg") if p.stem not in names)
    az = _analyzer()
    for name in names:
        ogg = folder / f"{name}.ogg"
        r = sh.row(name, f"{SAMPLES}{name}.ogg; {SAMPLES}mixes.json[{name}]", raw=report.get(name))
        r.set("tep", f"{SAMPLES}{name}.ogg" if ogg.exists() else "")
        length, ch, rate = _ogg_info(ogg) if ogg.exists() else ("", "", "")
        r.set("do_dai_s", length)
        r.set("kenh", ch)
        r.set("tan_so_mau_hz", rate)
        for k, v in (report.get(name) or {}).items():
            r.set({"seconds": "do_dai_tron_s"}.get(k, k), v)
        if not ogg.exists():
            continue
        if az is None:
            m = mc.row(f"{name}/chua_tinh", f"{SAMPLES}{name}.ogg")
            m.set(mc.parent_col, name)
            m.set("thu_tu", 0)
            m.set("hang", "KHONG_CHAY")
            r.set("so_moc", "")
            book.ctx.issue("09/Am_thanh_mau_moc: soundfile / scipy missing (pip install soundfile scipy); loud moments "
                           "not computed", once=True)
            continue
        top, marks = _loud_moments(az, ogg)
        r.set("lufs_mmax_tinh", top)
        r.set("so_moc", len(marks))
        for j, (t, lufs, peak, rank) in enumerate(marks):
            m = mc.row(f"{name}/{j + 1}", f"{SAMPLES}{name}.ogg @ {t} s")
            m.set(mc.parent_col, name)
            m.set("thu_tu", j)
            m.set("thoi_diem_s", t)
            m.set("lufs_400ms", lufs)
            m.set("duoi_to_nhat_lu", round(top - lufs, 1))
            m.set("dinh_dbfs", peak)
            m.set("hang", rank)


# ------------------------------------------------------------------------------- VFX_vu_khi (EffectShots.FxBatch shots)
FX_OUT = "Builds/effect_shots/"  # EffectShots.FxBatch default -mbFxOut (the runner's, git-ignored)
FX_FROM_MM = 120.0  # EffectShots.FxCalibreFrom
FX_TOP = 5  # TierFx.Top
FX_FRAMES = [("fire", 0.0, "fire_0s.png"), ("fire", 0.2, "fire_0.2s.png"), ("fire", 1.0, "fire_1s.png"),
             ("impact", 0.0, "impact_0s.png"), ("impact", 0.5, "impact_0.5s.png"), ("impact", 2.0, "impact_2s.png"),
             ("impact", 10.0, "impact_10s.png"), ("impact", 30.0, "impact_30s.png")]
FX_SALVO = [("salvo", "", "salvo.png"), ("salvo_impact", 0.5, "salvo_impact.png")]


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fx_shots(ctx, book):
    """VFX_vu_khi: the subjects of EffectShots.FxBatch (the six tiers, every weapon >= 120 mm a unit carries) and, in
    VFX_vu_khi_anh, every frame's path relative to the project root on the Unity runner (Builds/effect_shots/<key>/...;
    Docs/doc-images/README.md: the review's fx/ folder is a copy of it). present / pending by --effect-shots DIR: with
    DIR, its index.json gives the subjects and each file is looked up there; without, the list follows FxJobs from the
    01 sheets (carrier = any unit in Vu_khi.mang_boi; FxJobs also needs the carrier's model, checked in Unity)."""
    sh = book.sheet("VFX_vu_khi", "VFX theo vũ khí", "EffectShots.FxBatch: mỗi bậc T0-T5 (vũ khí đại diện chọn lúc chụp) và mỗi vũ "
                    "khí >= 120 mm có đơn vị mang: bậc, cỡ, số nòng, thư mục ảnh, số ảnh có / chờ; ảnh trên lưới 1 m (vạch "
                    "5 m đậm), vòng lõi đỏ, vòng rìa cam, Tăng chủ lực đặt cạnh làm thước; từng ảnh ở VFX_vu_khi_anh")
    for c, m in (("loai", "bac: ảnh đại diện của bậc; vu_khi: vũ khí >= 120 mm"),
                 ("vu_khi", "id vũ khí (bậc: vũ khí FxJobs chọn, chỉ biết khi chạy với --effect-shots)"),
                 ("bac", "bậc hiệu ứng T0-T5 (TierFx.Of: min(5, bậc họ), không họ = 0)"),
                 ("co_mm", "cỡ nòng (01/Vu_khi.co_mm)"), ("so_nong", "số nòng (01/Vu_khi.so_nong)"),
                 ("loat", "có ảnh loạt salvo.png / salvo_impact.png (nhiều nòng)"),
                 ("don_vi_mang", "đơn vị mang khi chụp (index.json carrier; không có thì 01/Vu_khi.mang_boi)"),
                 ("thu_muc", "thư mục ảnh, tương đối với gốc dự án trên máy chạy Unity"),
                 ("so_anh", "số ảnh mong đợi"), ("so_anh_co", "số ảnh có trong --effect-shots"),
                 ("trang_thai", "present: đủ ảnh; partial: thiếu một phần; pending: chưa có ảnh (không có --effect-shots)")):
        sh.col(c, meaning=m, unit="mm" if c == "co_mm" else "")
    sh.col("vu_khi", fk=["01_vu_khi_dan/Vu_khi"])
    an = book.sheet("VFX_vu_khi_anh", "VFX theo vũ khí: ảnh", "Mỗi ảnh của mỗi chủ đề: khung (fire / impact / salvo), giây sau phát "
                    "bắn / lúc chạm, đường dẫn tương đối Builds/effect_shots/<key>/<ảnh>, present / pending", parent=sh)
    an.col("khung", meaning="fire: sau phát bắn; impact: sau lúc chạm; salvo / salvo_impact: loạt nhiều nòng")
    an.col("thoi_diem_s", unit="s", meaning="giây sau phát bắn / lúc chạm (EffectShots.FxFireMoments / FxImpactMoments)")
    an.col("duong_dan", meaning="đường dẫn tương đối với gốc dự án trên máy chạy Unity")
    an.col("trang_thai", meaning="present: file có trong --effect-shots; pending: chưa có")
    shots = getattr(ctx, "effect_shots", None)
    index = {}
    if shots and (shots / "index.json").exists():
        try:
            index = {j["key"]: j for j in json.loads((shots / "index.json").read_text("utf-8-sig")).get("jobs") or []}
        except (ValueError, KeyError, TypeError):
            index = {}
    vk = ctx.books.get("01_vu_khi_dan")
    weapons = vk.sheets["Vu_khi"].rows if vk and "Vu_khi" in vk.sheets else {}
    derived = vk.sheets["Vu_khi_suy_ra"].rows if vk and "Vu_khi_suy_ra" in vk.sheets else {}

    def tier_of(wid):
        t = _num(derived[wid].values.get("bac_so")) if wid in derived else None
        return max(0, min(FX_TOP, int(t))) if t is not None else ""

    subjects = []  # (key, kind, weapon id, tier, salvo (None: unknown), carrier)
    for t in range(FX_TOP + 1):
        j = index.get(f"tier_T{t}")
        subjects.append((f"tier_T{t}", "bac", j.get("weapon", "") if j else "", t,
                         (int(j.get("barrels") or 1) > 1) if j else None, j.get("carrier", "") if j else ""))
    if index:
        for key, j in sorted(index.items()):
            if not key.startswith("tier_T"):
                subjects.append((key, "vu_khi", j.get("weapon", key), j.get("tier", ""), int(j.get("barrels") or 1) > 1,
                                 j.get("carrier", "")))
    else:
        for wid in sorted(weapons, key=str):
            v = weapons[wid].values
            cal, dmg = _num(v.get("co_mm")), _num(v.get("sat_thuong_moi_phat"))
            if cal is None or cal < FX_FROM_MM or not v.get("mang_boi") or not (dmg and dmg > 0):
                continue
            subjects.append((wid, "vu_khi", wid, tier_of(wid), (_num(v.get("so_nong")) or 1) > 1, v.get("mang_boi", "")))
    for key, kind, wid, tier, salvo, carrier in subjects:
        w = weapons[wid].values if wid in weapons else {}
        r = sh.row(key, f"EffectShots.FxJobs ({'index.json' if key in index else '01_vu_khi_dan/Vu_khi'}); {FX_OUT}{key}/")
        r.set("loai", kind)
        r.set("vu_khi", wid)
        r.set("bac", tier)
        r.set("co_mm", w.get("co_mm", ""))
        r.set("so_nong", w.get("so_nong", ""))
        r.set("loat", "" if salvo is None else salvo)
        r.set("don_vi_mang", carrier)
        r.set("thu_muc", f"{FX_OUT}{key}/")
        frames = FX_FRAMES + (FX_SALVO if salvo else [])
        have = 0
        for i, (frame, at, name) in enumerate(frames):
            ok = bool(shots and (shots / key / name).exists())
            have += ok
            a = an.row(f"{key}/{name}", f"{FX_OUT}{key}/{name}")
            a.set(an.parent_col, key)
            a.set("thu_tu", i)
            a.set("khung", frame)
            a.set("thoi_diem_s", at)
            a.set("duong_dan", f"{FX_OUT}{key}/{name}")
            a.set("trang_thai", "present" if ok else "pending")
        r.set("so_anh", len(frames))
        r.set("so_anh_co", have)
        r.set("trang_thai", "present" if have == len(frames) else "partial" if have else "pending")

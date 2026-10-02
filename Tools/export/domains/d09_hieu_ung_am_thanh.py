"""09_hieu_ung_am_thanh, layer A: every audio clip, the sound library banks (Tools/sfx/library.json), the clip envelopes,
the rapid-fire burst table, effects by tier (TierFx.Fire, EffectLife.Bands), hull fire looks, post-processing
(BattlefieldProfile.asset); code-only parts (wrecks, mixer) marked."""
from __future__ import annotations

import re
import struct

from core.model import NEED_CODE_CHECK, chua_ap
from core.repo import ROOT

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
    vb.col("rung_camera_dong_thoi", meaning="ShakeAt, FullCap, Weight, Busy: hàm theo bậc trong TierFx.cs")
    for path, array, prefix in ((TIERFX, "Fire", "ban_"), (LIFE, "Bands", "doi_")):
        sid, rows, lines = ctx.cs_table(path, array)
        for i, item in enumerate(rows):
            r = vb.rows.get(f"T{i}") or vb.row(f"T{i}", f"{TIERFX} (Fire), {LIFE} (Bands)")
            r.set("bac", i)
            if isinstance(item, dict):
                r.flatten(item, sid, (i,), prefix=prefix)
            else:
                C.cs_element_row(r, item, sid, (i,))
            r.set("rung_camera_dong_thoi", NEED_CODE_CHECK)
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
    C.marker_sheet(book, "Am_thanh_mau", "Âm thanh: bản ghi mẫu", "3 file ghi âm thử và mốc thời gian các tiếng lớn",
                   chua_ap("xuat_luot6"), "Docs/audio (bản trộn mẫu của Tools/sfx/render_mix.py)", "Docs/audio")
    C.marker_sheet(book, "VFX_vu_khi", "VFX theo vũ khí", "Mỗi vũ khí >= 120 mm: bậc, ảnh lúc bắn / nổ, lưới mét, thước Tăng chủ lực",
                   chua_ap("xuat_luot6"), "ảnh chụp (lượt 6: images/09); bậc theo 01_vu_khi_dan/Vu_khi", "Tools/export (lượt 6)")

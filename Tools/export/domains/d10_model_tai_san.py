"""10_model_tai_san, layer A: every GLB model (nodes, materials, meshes, triangles, Part_ / Mount_ / Muzzle_ counts), the
model baseline (Tools/assets/baseline.json: per-model check, budgets, history), real reference sizes, card renders,
localisation (every HUD key in Vietnamese and English), asset licences."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from core import docmd
from core.model import NEED_CODE_CHECK, join_list
from core.repo import ROOT

from . import DOMAINS, _b10
from . import _lane_c as C

FILE_ID = "10_model_tai_san"
TITLE = "Model và tài sản"
DESC = "Model GLB (nút, vật liệu, mesh, tam giác, Part / Mount / Muzzle), chuẩn kiểm model, kích thước thật tham chiếu, " \
       "ảnh thẻ, địa phương hóa Việt / Anh, giấy phép tài sản"

MODELS = "Assets/MachineBrigade/Resources/Models/"
BASELINE = "Tools/assets/baseline.json"
REAL = "Tools/models/reference_real.json"
GOLD = "Tools/assets/gold_metrics.json"
NODE_MAP = "Tools/assets/runtime_node_map.json"
NODE_BASELINE = "Tools/assets/runtime_node_baseline.json"
WAIVERS = "Tools/assets/budget_waivers.json"
STATIC_MERGE = "Tools/assets/static_merge.json"
SPECS = "Tools/blender/specs/"
CARDS = "Assets/MachineBrigade/Resources/UI/Cards/manifest.json"
LICENSES = "Assets/MachineBrigade/Resources/Licenses/"
MODEL_FK = ["10_model_tai_san/Model"]
REBUILD = "Docs/models/rebuild/"
SCAN_OUT = "Builds/scan/"  # ModelScan.DefaultOut: the runner's 3-up sheets (git-ignored)
KIT = "Docs/models/kit_catalog/kit35_components.json"
FX_TIERS = 6  # TierFx.Top + 1


def _count(names, prefix):
    return sum(1 for n in names if n.startswith(prefix))


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    base = ctx.data(BASELINE) if BASELINE in ctx.sources else {}
    bmodels = base.get("models") or {}

    # ------------------------------------------------------------------ Model (+ nodes)
    md = book.sheet("Model", "Model", "Mỗi GLB một dòng (đọc bằng Tools/assets/glb_analyze.read_glb): tam giác, nút, vật liệu, "
                    "mesh, số Part_* / Mount_* / Muzzle_*, Mount_Flare / Mount_APS, kích thước (baseline)")
    for c, unit, m in (("loai", "", "loại (baseline category)"), ("lop_ngan_sach", "", "lớp ngân sách (baseline budgetClass)"),
                       ("tam_giac", "", "tổng tam giác (mọi primitive tam giác)"), ("so_nut", "", "số nút"),
                       ("so_part", "", "số nút Part_*"), ("so_mount", "", "số nút Mount_*"), ("so_muzzle", "", "số nút Muzzle_*"),
                       ("co_mount_flare", "", "có nút Mount_Flare*"), ("co_mount_aps", "", "có nút Mount_APS*"),
                       ("vat_lieu", "", "tên vật liệu (ngăn ';')"), ("mesh", "", "tên mesh (ngăn ';')"),
                       ("glb_x_m", "m", "kích thước x của GLB (baseline size[0])"),
                       ("glb_y_m", "m", "kích thước y của GLB (baseline size[1])"),
                       ("glb_z_m", "m", "kích thước z của GLB (baseline size[2])"), ("duong_dan", "", "file"),
                       ("tam_giac_lod", "", "tam giác LOD0 / 1 / 2 (Unity tạo LOD lúc nhập; xem 12/Validator lod1Share)"),
                       ("anh_3_goc", "", "ảnh 3 góc (ModelScan: play / side / rear, 3 x 512 px): Docs/models/rebuild/<model>/"
                                         "unity_scan.png khi repo có, không thì Builds/scan/<model>.png của máy chạy Unity"),
                       ("anh_3_goc_trang_thai", "", "present: file có trong repo; pending: chờ ModelScan.RenderBatch "
                                                    "(model không thuộc đơn vị nào thì ModelScan không chụp)")):
        md.col(c, unit=unit, meaning=m)
    nodes = book.sheet("Model_nut", "Model: nút", "nodes[].name: mọi nút của mọi GLB một dòng", parent=md)
    nodes.col("ten", meaning="tên nút")
    nodes.col("tien_to", meaning="Part / Mount / Muzzle / Point / khác")
    for sid in sorted(s for s, src in ctx.sources.items() if src.kind == "glb" and s.startswith(MODELS)):
        g = ctx.data(sid)
        stem = sid.rsplit("/", 1)[-1][:-4]
        r = md.row(stem, sid, raw={k: g[k] for k in ("triangles",)})
        b = bmodels.get(stem) or {}
        r.set("loai", b.get("category", ""))
        r.set("lop_ngan_sach", b.get("budgetClass", ""))
        r.set("tam_giac", g.get("triangles"), sid, ("triangles",))
        names = g.get("nodes") or []
        r.set("so_nut", len(names))
        r.set("so_part", _count(names, "Part_"))
        r.set("so_mount", _count(names, "Mount_"))
        r.set("so_muzzle", _count(names, "Muzzle_"))
        r.set("co_mount_flare", any(n.startswith("Mount_Flare") for n in names))
        r.set("co_mount_aps", any(n.startswith("Mount_APS") for n in names))
        for key, col in (("materials", "vat_lieu"), ("meshes", "mesh")):
            vals = g.get(key) or []
            r.set(col, join_list(vals))
            for i in range(len(vals)):
                r.mark(sid, (key, i, "name"), col)
        size = b.get("size") or []
        for i, col in enumerate(("glb_x_m", "glb_y_m", "glb_z_m")):  # not dai_m / rong_m: 02/Xe has those (game size)
            r.set(col, size[i] if i < len(size) else "")
        r.set("duong_dan", sid)
        r.set("tam_giac_lod", NEED_CODE_CHECK)
        scan = f"{REBUILD}{stem}/unity_scan.png"
        have = (ROOT / scan).exists()
        r.set("anh_3_goc", scan if have else f"{SCAN_OUT}{stem}.png")
        r.set("anh_3_goc_trang_thai", "present" if have else "pending")
        for i, n in enumerate(names):
            nr = nodes.row(f"{stem}/{i}", C.nguon(sid, ("nodes", i, "name")))
            nr.set(nodes.parent_col, stem)
            nr.set("thu_tu", i)
            nr.set("ten", n, sid, ("nodes", i, "name"))
            nr.set("tien_to", next((p for p in ("Part", "Mount", "Muzzle", "Point") if n.startswith(p + "_")), ""))

    # ------------------------------------------------------------------ baseline.json
    kc = book.sheet("Model_kiem_chuan", "Model: kiểm chuẩn (baseline)", "Tools/assets/baseline.json models: số liệu kiểm máy của "
                    "mỗi model (tam giác, đỉnh, renderer, bộ phận chạy, lỗi, cảnh báo, nút runtime, kích thước, hash)")
    kc.col("model", meaning="model", fk=MODEL_FK)
    for r, item, _p in C.keyed(kc, bmodels, BASELINE, ("models",), vectors={
            "boundsMin": ["x_m", "y_m", "z_m"], "boundsMax": ["x_m", "y_m", "z_m"], "size": ["x_m", "y_m", "z_m"],
            "center": ["x_m", "y_m", "z_m"]}):
        r.set("model", r.id if r.id in md.rows else "")
    ts = book.sheet("Model_tieu_chuan", "Model: tiêu chuẩn", "baseline.json budgets: ngân sách theo lớp x bậc (normal / hd): "
                    "tam giác, đỉnh, renderer, bộ phận chạy [mức, trần]; ngân sách là hướng dẫn, không phải trần cứng")
    ts.col("lop", meaning="lớp ngân sách")
    ts.col("bac", meaning="normal / hd")
    for cls, tiers in (base.get("budgets") or {}).items():
        for tier, rec in (tiers or {}).items():
            p = ("budgets", cls, tier)
            r = ts.row(f"{cls}/{tier}", C.nguon(BASELINE, p), raw=rec)
            r.set("lop", cls)
            r.set("bac", tier)
            r.flatten(rec, BASELINE, p, vectors={k: ["muc", "tran"] for k in rec})
    ls = book.sheet("Model_lich_su", "Model: lịch sử kiểm chuẩn", "baseline.json history[]: ngày, model, lý do, thay đổi")
    ls.col("models", meaning="model đổi (ngăn ';')")
    C.records(ls, base.get("history"), BASELINE, ("history",))
    kv = book.kv_sheet("Model_kiem_chuan_chung", "Model: kiểm chuẩn (chung)", "baseline.json: số model, ngày sinh")
    book.kv_rows(kv, {k: v for k, v in base.items() if k not in ("models", "budgets", "history")}, BASELINE, (), "baseline")

    # ------------------------------------------------------------------ MVA W1-B: runtime node contract and budget waivers
    for src, name, title, desc, group in (
            (NODE_MAP, "Model_ten_nut_on_dinh", "Model: tên nút runtime ổn định",
             "Tools/assets/runtime_node_map.json: mỗi model đã đổi tên nút có hậu tố Blender (.001) sang tên ngữ nghĩa ổn định "
             "(cũ -> mới, giữ thứ tự); frontier_kit áp lại sau mỗi lần xuất. Báo cáo: Docs/models/RUNTIME_NODES.md", "runtime_node_map"),
            (NODE_BASELINE, "Model_nut_ton_dong", "Model: lỗi nút runtime đã biết",
             "Tools/assets/runtime_node_baseline.json: lỗi cứng đã biết (model|luật|vị trí) và lý do; lỗi mới làm "
             "runtime_node_audit.py thất bại", "runtime_node_baseline"),
            (WAIVERS, "Model_ngan_sach_mien", "Model: miễn trừ ngân sách",
             "Tools/assets/budget_waivers.json: miễn trừ chính thức (ai, ngày, lý do, việc tiếp) cho lỗi ngân sách cứng và "
             "ghi chú duyệt cho mức mềm. Báo cáo: Docs/models/BUDGET_OUTLIERS.md", "budget_waivers"),
            (STATIC_MERGE, "Model_gop_luoi_tinh", "Model: gộp lưới tĩnh",
             "Tools/assets/static_merge.json: model có các lưới chi tiết tĩnh cùng vật liệu được gộp trong GLB "
             "(Tools/assets/glb_merge_static.py; hình trên màn hình giữ nguyên). Báo cáo: Docs/models/BUDGET_OUTLIERS.md",
             "static_merge")):
        if src in ctx.sources:
            kvw = book.kv_sheet(name, title, desc)
            book.kv_rows(kvw, ctx.data(src), src, (), group)

    # ------------------------------------------------------------------ reference sizes (Tools/models/reference_real.json)
    if REAL in ctx.sources:
        real = ctx.data(REAL)
        kt = book.sheet("Kich_thuoc_that", "Kích thước thật tham chiếu", "Tools/models/reference_real.json: mẫu thật, kích thước "
                        "dài / rộng / cao (m), nguồn, độ tin (conf); dùng ở 13 (lượt 10)")
        C.keyed(kt, real.get("units"), REAL, ("units",), vectors={"size": ["dai_m", "rong_m", "cao_m"]})
        rest = {k: v for k, v in real.items() if k != "units"}
        if rest:
            kv2 = book.kv_sheet("Kich_thuoc_that_chung", "Kích thước thật: ghi chú", "reference_real.json: khóa ngoài units")
            book.kv_rows(kv2, rest, REAL, (), "reference_real")

    # ------------------------------------------------------------------ prompt 35 model rebuild data (lane B, pass 5 part 2)
    # Tools/assets/gold_metrics.json (gold-set class means of the quality gate) and Tools/blender/specs/*.json (the rebuild
    # specs of the pilot models): every leaf one row of a key / value sheet (new sources after lane C's passes 3-4)
    if GOLD in ctx.sources:
        gm = book.kv_sheet("Model_chuan_vang", "Model: số đo bộ mẫu vàng", "Tools/assets/gold_metrics.json: trung bình theo lớp của "
                           "bộ model mẫu (quality_gate.compute_gold, prompt 35)")
        book.kv_rows(gm, ctx.data(GOLD), GOLD, (), "gold_metrics")
    specs = sorted(s for s in ctx.sources if s.startswith(SPECS) and s.endswith(".json"))
    if specs:
        ms = book.kv_sheet("Model_spec_dung", "Model: spec dựng lại", "Tools/blender/specs/<model>.json: spec dựng lại model (mẫu thật, "
                           "kích thước đích, bộ phận, vũ khí, ngân sách, vùng màu; prompt 35); id = <model>.<đường dẫn>")
        for sid in specs:
            stem = sid.rsplit("/", 1)[-1][:-5]
            book.kv_rows(ms, ctx.data(sid), sid, (), stem, prefix=(stem,))

    # ------------------------------------------------------------------ card renders (UI/Cards/manifest.json)
    if CARDS in ctx.sources:
        cards = ctx.data(CARDS)
        at = book.sheet("Anh_the", "Ảnh thẻ", "Resources/UI/Cards/manifest.json entries: ảnh thẻ render từ model (loại, model, nguồn, hash)")
        # Play-test 14 lane K: a boss with its own paint has its own picture key (its id), not always a model file.
        at.col("model", meaning="khóa ảnh: id model, hoặc id boss khi boss có sơn riêng")
        C.records(at, cards.get("entries"), CARDS, ("entries",))
        kv3 = book.kv_sheet("Anh_the_chung", "Ảnh thẻ: cài đặt render", "manifest.json: camera, cỡ ảnh, phiên bản")
        book.kv_rows(kv3, {k: v for k, v in cards.items() if k != "entries"}, CARDS, (), "cards")

    # ------------------------------------------------------------------ Dia_phuong_hoa (every HUD key)
    dp = book.sheet("Dia_phuong_hoa", "Địa phương hóa", "Mọi khóa chữ của các bảng C# [\"key\"] = (\"en\", \"vi\") một dòng")
    dp.col("bang", meaning="file C# chứa khóa")
    dp.col("tien_to", meaning="tiền tố khóa (phần trước dấu chấm đầu)")
    dp.col("en", meaning="tiếng Anh")
    dp.col("vi", meaning="tiếng Việt")
    dp.col("so_ky_tu_en", meaning="số ký tự tiếng Anh")
    dp.col("so_ky_tu_vi", meaning="số ký tự tiếng Việt")
    for sid in sorted(s for s, src in ctx.sources.items() if src.kind == "cs_strings"):
        for key, tv in (ctx.data(sid) or {}).items():
            rid = key if key not in dp.rows else f"{key}@{sid.rsplit('/', 1)[-1]}"
            r = dp.row(rid, f"{sid}: [\"{key}\"]")
            r.set("bang", sid.rsplit("/", 1)[-1])
            r.set("tien_to", key.split(".", 1)[0])
            r.set("en", tv.get("en", ""), sid, (key, "en"))
            r.set("vi", tv.get("vi", ""), sid, (key, "vi"))
            r.set("so_ky_tu_en", len(tv.get("en") or ""))
            r.set("so_ky_tu_vi", len(tv.get("vi") or ""))

    # ------------------------------------------------------------------ Giay_phep_tai_san (Resources/Licenses)
    gp = book.sheet("Giay_phep_tai_san", "Giấy phép tài sản", "Resources/Licenses/*.txt: mỗi file giấy phép một dòng "
                    "(phông chữ OFL); nội dung từng dòng ở Giay_phep_noi_dung; âm thanh: 09/Am_thanh.giay_phep")
    gp.col("tep", meaning="file")
    gp.col("tai_san", meaning="tài sản (tên phông chữ theo tên file)")
    gp.col("giay_phep", meaning="loại giấy phép (tiền tố tên file: OFL = SIL Open Font License)")
    gp.col("so_dong", meaning="số dòng không trống")
    nd = book.sheet("Giay_phep_noi_dung", "Giấy phép: nội dung", "mỗi dòng không trống của file giấy phép", parent=gp)
    nd.col("noi_dung", meaning="nguyên văn dòng")
    for sid in sorted(s for s in ctx.sources if s.startswith(LICENSES)):
        lines = ctx.data(sid) or []
        stem = sid.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        r = gp.row(stem, sid)
        r.set("tep", sid.rsplit("/", 1)[-1])
        r.set("tai_san", stem.split("-", 1)[-1])
        r.set("giay_phep", "SIL Open Font License" if stem.startswith("OFL") else stem.split("-", 1)[0])
        n = 0
        for j, line in enumerate(lines):
            if not line.strip():
                continue
            n += 1
            lr = nd.row(f"{stem}/{j + 1:04d}", C.nguon(sid, ("lines", j)))
            lr.set(nd.parent_col, stem)
            lr.set("thu_tu", j)
            lr.set("noi_dung", line, sid, ("lines", j))
        r.set("so_dong", n)

    # ------------------------------------------------------------------ later passes / code-only
    C.marker_sheet(book, "Xem_truoc", "Màn xem trước", "Mỗi đơn vị: miền đất / biển / ray / không, cảnh nền, hợp lệ",
                   NEED_CODE_CHECK, "Assets/MachineBrigade/Scripts/Editor/ModelPreview.cs và preview của menu (FiringRange; "
                   "DECISIONS 'Play-test 12 (lane B)'): không có bảng dữ liệu", "Assets/MachineBrigade/Scripts/Editor/ModelPreview.cs")
    _pictures(ctx, book, md)
    _kit(book)

    # ------------------------------------------------------------------ layer B (lane B, pass 5 part 2)
    _b10.build(ctx, book)


def _png_size(path) -> tuple:
    try:
        head = path.read_bytes()[:24]
        return struct.unpack(">II", head[16:24]) if head[1:4] == b"PNG" else ("", "")
    except (OSError, struct.error):
        return "", ""


def _pictures(ctx, book, md):
    """Anh_chup: every picture md/ of pass 6 shows (docmd.picture_plan: same order and names as the md), plus the
    Unity effect shots of section 20b still pending when no --effect-shots folder was given."""
    sh = book.sheet("Anh_chup", "Ảnh chụp", "Mọi ảnh md / PDF của lượt 6 dùng (docmd.picture_plan): ảnh trong export "
                    "images/<file>/<tên>, file gốc, mục, chú thích, cỡ px, thước đo; ảnh hiệu ứng Unity: present khi "
                    "chạy với --effect-shots <thư mục>, không thì pending")
    for c, m in (("nguon_anh", "file gốc: đường dẫn trong repo, hoặc Builds/effect_shots/<key>/<ảnh> của máy chạy Unity"),
                 ("loai", "review: ảnh của tài liệu thiết kế; thu_muc: ảnh thư mục doc_parts in kèm; fx: ảnh hiệu ứng Unity"),
                 ("muc", "mục tài liệu in ảnh (ngăn ';')"), ("tieu_de_muc", "tên mục đầu"), ("chu_thich", "chú thích"),
                 ("rong_px", "rộng (px)"), ("cao_px", "cao (px)"),
                 ("thuoc_do", "đơn vị và thước so sánh của ảnh (không ảnh nào có lưới mét trừ ảnh hiệu ứng)"),
                 ("trang_thai", "present: ảnh có, đã chép vào images/; pending: chờ ảnh Unity")):
        sh.col(c, meaning=m)
    fids = {n[1:3]: n[1:] for n in DOMAINS}
    shots = getattr(ctx, "effect_shots", None)
    mbt = md.rows.get("main_battle_tank")
    ruler = (f"thước: Tăng chủ lực main_battle_tank {mbt.values.get('glb_x_m')} × {mbt.values.get('glb_y_m')} × "
             f"{mbt.values.get('glb_z_m')} m (10/Model)") if mbt else ""

    def unit(src, kind):
        if kind == "fx":
            return "m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng chủ lực đặt cạnh làm thước"
        m = md.rows.get(src.parent.name) if REBUILD.rstrip("/") in src.as_posix() else None
        if m:
            return (f"m, không lưới; model {src.parent.name} {m.values.get('glb_x_m')} × {m.values.get('glb_y_m')} × "
                    f"{m.values.get('glb_z_m')} m (glb x × y × z); {ruler}")
        return f"ảnh chụp, không lưới mét; {ruler}" if ruler else "ảnh chụp, không lưới mét"

    for e in docmd.picture_plan(fids, shots):
        src = e["src"]
        if e["rel"] in sh.rows:
            r = sh.rows[e["rel"]]
            parts = str(r.values.get("muc", "")).split(";")
            if e["part"] not in parts:
                r.values["muc"] = ";".join(parts + [e["part"]])
            continue
        inside = src.is_relative_to(ROOT)
        label = src.relative_to(ROOT).as_posix() if inside else "Builds/effect_shots/" + "/".join(src.parts[-2:])
        r = sh.row(e["rel"], f"{label} (Tools/export/core/docmd.picture_plan)")
        r.set("nguon_anh", label)
        r.set("loai", {"folder": "thu_muc"}.get(e["kind"], e["kind"]))
        r.set("muc", e["part"])
        r.set("tieu_de_muc", e["title"])
        r.set("chu_thich", e["caption"])
        w, h = _png_size(src)
        r.set("rong_px", w)
        r.set("cao_px", h)
        r.set("thuoc_do", unit(src, e["kind"]))
        r.set("trang_thai", "present")
    part = next(p for p in docmd.DP.PARTS if p.get("fx"))
    for t in range(FX_TIERS):
        for name in docmd.FX_PICS:
            rel = f"images/{fids[part['domain']]}/tier_T{t}_{name}"
            if rel in sh.rows:
                continue
            label = f"Builds/effect_shots/tier_T{t}/{name}"
            r = sh.row(rel, f"{label} (EffectShots.FxBatch; 09/VFX_vu_khi_anh)")
            r.set("nguon_anh", label)
            r.set("loai", "fx")
            r.set("muc", part["num"])
            r.set("tieu_de_muc", part["title"])
            r.set("chu_thich", f"tier_T{t} {name[:-4]}")
            r.set("thuoc_do", unit(Path(label), "fx"))
            r.set("trang_thai", "pending")


def _kit(book):
    """Kit_chi_tiet: Docs/models/kit_catalog/kit35_components.json (the 70 Blender kit parts; picture kit35_catalog.png)."""
    p = ROOT / KIT
    if not p.exists():
        return
    sh = book.sheet("Kit_chi_tiet", "Bộ chi tiết kit35", "Docs/models/kit_catalog/kit35_components.json: 70 chi tiết của "
                    "Tools/blender/mb_kit35.py (tam giác, kích thước, lỗi kiểm); ảnh: kit35_catalog.png (Anh_chup)")
    sh.col("tam_giac", meaning="số tam giác")
    for c in ("x_m", "y_m", "z_m"):
        sh.col(c, unit="m", meaning=f"kích thước {c[0]} (size)")
    sh.col("loi", meaning="lỗi kiểm (fails, ngăn ';'; trống = đạt)")
    for i, rec in enumerate(json.loads(p.read_text("utf-8"))):
        r = sh.row(rec.get("component", i), f"{KIT}[{i}]", raw=rec)
        r.set("tam_giac", rec.get("triangles", ""))
        size = rec.get("size") or []
        for j, c in enumerate(("x_m", "y_m", "z_m")):
            r.set(c, size[j] if j < len(size) else "")
        r.set("loi", join_list(rec.get("fails") or []))

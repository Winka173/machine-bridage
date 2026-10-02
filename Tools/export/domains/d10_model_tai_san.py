"""10_model_tai_san, layer A: every GLB model (nodes, materials, meshes, triangles, Part_ / Mount_ / Muzzle_ counts), the
model baseline (Tools/assets/baseline.json: per-model check, budgets, history), real reference sizes, card renders,
localisation (every HUD key in Vietnamese and English), asset licences."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK, chua_ap, join_list

from . import _lane_c as C

FILE_ID = "10_model_tai_san"
TITLE = "Model và tài sản"
DESC = "Model GLB (nút, vật liệu, mesh, tam giác, Part / Mount / Muzzle), chuẩn kiểm model, kích thước thật tham chiếu, " \
       "ảnh thẻ, địa phương hóa Việt / Anh, giấy phép tài sản"

MODELS = "Assets/MachineBrigade/Resources/Models/"
BASELINE = "Tools/assets/baseline.json"
REAL = "Tools/models/reference_real.json"
CARDS = "Assets/MachineBrigade/Resources/UI/Cards/manifest.json"
LICENSES = "Assets/MachineBrigade/Resources/Licenses/"
MODEL_FK = ["10_model_tai_san/Model"]


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
                       ("dai_m", "m", "kích thước x (baseline size[0])"), ("cao_m", "m", "kích thước y (baseline size[1])"),
                       ("rong_m", "m", "kích thước z (baseline size[2])"), ("duong_dan", "", "file"),
                       ("tam_giac_lod", "", "tam giác LOD0 / 1 / 2 (Unity tạo LOD lúc nhập; xem 12/Validator lod1Share)"),
                       ("anh_3_goc", "", "ảnh 3 góc (lượt 6, images/10)")):
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
        for i, col in enumerate(("dai_m", "cao_m", "rong_m")):
            r.set(col, size[i] if i < len(size) else "")
        r.set("duong_dan", sid)
        r.set("tam_giac_lod", NEED_CODE_CHECK)
        r.set("anh_3_goc", chua_ap("xuat_luot6"))
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

    # ------------------------------------------------------------------ card renders (UI/Cards/manifest.json)
    if CARDS in ctx.sources:
        cards = ctx.data(CARDS)
        at = book.sheet("Anh_the", "Ảnh thẻ", "Resources/UI/Cards/manifest.json entries: ảnh thẻ render từ model (loại, model, nguồn, hash)")
        at.col("model", fk=MODEL_FK)
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
    C.marker_sheet(book, "Anh_chup", "Ảnh chụp", "Danh sách ảnh dùng trong tài liệu (images/<lĩnh vực>)", chua_ap("xuat_luot6"),
                   "lượt 6 (Markdown, PDF, ảnh): Docs/doc-images", "Docs/doc-images")

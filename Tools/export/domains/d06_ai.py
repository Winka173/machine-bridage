"""06_ai, layer A: tactics, AI profiles by mode, enemy generals, AI parameters (economy, params, world), unit roles,
squad states, tower and boss behaviour."""
from __future__ import annotations

from . import _b06
from . import _c06
from . import _p5_ai
from . import _mva_w1a
from . import _balance as B
from . import _lane_c as C

FILE_ID = "06_ai"
TITLE = "AI"
DESC = "Chiến thuật, hồ sơ AI theo chế độ, tướng địch, tham số AI, vai trò đơn vị, trạng thái đội, hành vi tháp / boss"

TACTIC_FK = ["06_ai/Chien_thuat"]


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    camp = ctx.data(C.CAMPAIGN)
    beh = d.get("aiBehaviour") or {}
    prof = d.get("aiModeProfiles") or {}

    # ------------------------------------------------------------------ Chien_thuat
    ct = book.sheet("Chien_thuat", "Chiến thuật", "aiBehaviour.tactics: 16 chiến thuật (tỷ lệ CP theo nhóm, ưu tiên, "
                    "khắc chế, mở khóa theo chương, commander, mô-đun ghi đè tham số)")
    ct.col("counters", meaning="chiến thuật nó khắc chế (ngăn ';')", fk=TACTIC_FK)
    ct.col("countered_by", meaning="chiến thuật khắc chế nó (ngăn ';')", fk=TACTIC_FK)
    ct.col("prefer", meaning="đơn vị ưu tiên (ngăn ';')", fk=C.UNIT_FK)
    ct.col("commanders", meaning="commander dùng chiến thuật (ngăn ';')", fk=["02_phuong_tien/Commander"])
    C.records(ct, beh.get("tactics"), B.BALANCE, ("aiBehaviour", "tactics"))

    # ------------------------------------------------------------------ AI_ho_so_che_do (+ the mode / goal map)
    hs = book.sheet("AI_ho_so_che_do", "Hồ sơ AI theo chế độ", "aiModeProfiles.profiles: controllers, chiến thuật cho phép, "
                    "chính sách mục tiêu, đứng yên, áp lực tiêu / tiến, hỗ trợ, leash, mặt nạ mục tiêu")
    hs.col("tactics", meaning="chiến thuật cho phép (ngăn ';'; '*' = mọi chiến thuật, nên không khai khóa ngoại)")
    po = book.sheet("AI_ho_so_pha", "Hồ sơ AI: ghi đè theo pha", "aiModeProfiles.profiles.<hồ sơ>.phaseOverrides[]", parent=hs)
    C.keyed(hs, prof.get("profiles"), B.BALANCE, ("aiModeProfiles", "profiles"), children={"phaseOverrides": C.child(po)})
    hm = book.sheet("AI_ho_so_anh_xa", "Hồ sơ AI: chế độ / mục tiêu -> hồ sơ",
                    "aiModeProfiles.modes (chế độ) và aiModeProfiles.goals (kiểu mục tiêu nhiệm vụ) -> hồ sơ")
    hm.col("loai", meaning="mode (chế độ) / goal (kiểu mục tiêu)", enum=["mode", "goal"])
    hm.col("khoa", meaning="tên chế độ hoặc kiểu mục tiêu")
    hm.col("ho_so", meaning="hồ sơ AI", fk=["06_ai/AI_ho_so_che_do"])
    for key, kind in (("modes", "mode"), ("goals", "goal")):
        for k, v in (prof.get(key) or {}).items():
            r = hm.row(f"{kind}.{k}", B.nguon(("aiModeProfiles", key, k)), raw=v)
            r.set("loai", kind)
            r.set("khoa", k)
            r.set("ho_so", v, B.BALANCE, ("aiModeProfiles", key, k))
    other = {k: v for k, v in prof.items() if k not in ("profiles", "modes", "goals")}
    if other:
        kv = book.kv_sheet("AI_ho_so_luat", "Hồ sơ AI: khóa khác", "aiModeProfiles: khóa ngoài profiles / modes / goals")
        book.kv_rows(kv, other, B.BALANCE, ("aiModeProfiles",), "aiModeProfiles")

    # ------------------------------------------------------------------ AI_tuong
    tg = book.sheet("AI_tuong", "Tướng địch", "Mỗi tướng một dòng: campaign.json generals (bộ bài, hỗ trợ, thế, phong cách), "
                    "balance.json generals (elite ưa thích, bài thêm), aiBehaviour.generals (chiến thuật ưa thích)")
    tg.col("chien_thuat_ua_thich", meaning="aiBehaviour.generals.<tướng>", fk=TACTIC_FK)
    tg.col("chien_dich_deck", meaning="bộ bài (campaign generals[].deck, ngăn ';')", fk=C.UNIT_FK)
    tg.col("chien_dich_supports", meaning="thẻ hỗ trợ (ngăn ';')", fk=C.SUPPORT_FK)
    tg.col("noi_tai", meaning="nội tại tướng: 02_phuong_tien/Commander (gen.<tướng>)")
    camp_gen = {g.get("id"): (i, g) for i, g in enumerate(camp.get("generals") or []) if isinstance(g, dict)}
    bal_gen = d.get("generals") or {}
    beh_gen = beh.get("generals") or {}
    for gid in sorted(set(camp_gen) | set(bal_gen) | set(beh_gen)):
        r = tg.row(gid, f"{C.CAMPAIGN}: generals / {B.BALANCE}: generals, aiBehaviour.generals")
        if gid in beh_gen:
            r.set("chien_thuat_ua_thich", beh_gen[gid], B.BALANCE, ("aiBehaviour", "generals", gid))
        if gid in camp_gen:
            i, g = camp_gen[gid]
            r.raw = g
            r.flatten(g, C.CAMPAIGN, ("generals", i), prefix="chien_dich_", skip=("id",))
            r.mark(C.CAMPAIGN, ("generals", i, "id"), "id")
        if isinstance(bal_gen.get(gid), dict):
            r.flatten(bal_gen[gid], B.BALANCE, ("generals", gid), prefix="can_bang_")
        r.set("noi_tai", f"gen.{gid}")

    # ------------------------------------------------------------------ AI_tham_so
    ts = book.sheet("AI_tham_so", "Tham số AI", "balance.json ai.economy / ai.params / ai.world: giá trị, khoảng cho phép, "
                    "chỉ số đo, lý do (prompt 28 L); danh sách bậc (escalation) một dòng mỗi bậc")
    ts.col("khoi", meaning="economy / params / world")
    ts.col("tham_so", meaning="tên tham số")
    ts.col("bac", meaning="bậc (danh sách nhiều bậc), trống nếu một giá trị")
    for block, params in (d.get("ai") or {}).items():
        if not isinstance(params, dict):
            r = ts.row(block, B.nguon(("ai", block)), raw=params)
            C.scalar_or_list(r, "value", params, B.BALANCE, ("ai", block))
            continue
        for k, rec in params.items():
            path = ("ai", block, k)
            items = rec if isinstance(rec, list) else [rec]
            for j, item in enumerate(items):
                p = path + ((j,) if isinstance(rec, list) else ())
                r = ts.row(f"{block}.{k}" + (f"/{j}" if isinstance(rec, list) else ""), B.nguon(p), raw=item)
                r.set("khoi", block)
                r.set("tham_so", k)
                r.set("bac", j if isinstance(rec, list) else "")
                if isinstance(item, dict):
                    r.flatten(item, B.BALANCE, p)
                else:
                    C.scalar_or_list(r, "value", item, B.BALANCE, p)

    # ------------------------------------------------------------------ roles, states, units, towers, bosses
    vt = book.sheet("AI_vai_tro", "Vai trò đơn vị", "aiBehaviour.roles: ngưỡng giao chiến, phản ứng khi bị áp đảo")
    C.keyed(vt, beh.get("roles"), B.BALANCE, ("aiBehaviour", "roles"))
    dv = book.sheet("AI_don_vi", "Vai trò của từng đơn vị", "aiBehaviour.units: đơn vị -> vai trò AI")
    dv.col("don_vi", meaning="đơn vị", fk=C.VEHICLE_FK)
    dv.col("vai_tro", meaning="vai trò AI", fk=["06_ai/AI_vai_tro"])
    for uid, role in (beh.get("units") or {}).items():
        r = dv.row(uid, B.nguon(("aiBehaviour", "units", uid)), raw=role)
        r.set("don_vi", uid)
        r.set("vai_tro", role, B.BALANCE, ("aiBehaviour", "units", uid))
    st = book.sheet("AI_trang_thai", "Trạng thái đội", "aiBehaviour.states: ưu tiên và thời gian cam kết mỗi trạng thái")
    C.keyed(st, beh.get("states"), B.BALANCE, ("aiBehaviour", "states"), units={"commit": "s"})
    th = book.sheet("AI_thap", "Hành vi tháp", "aiBehaviour.towers: cách chọn mục tiêu mặc định và các cách đổi được")
    th.col("thap", meaning="tháp", fk=["04_can_cu_thap/Thap"])
    for r, _item, _p in C.keyed(th, beh.get("towers"), B.BALANCE, ("aiBehaviour", "towers")):
        r.set("thap", r.id)
    bo = book.sheet("AI_boss", "Hành vi boss", "aiBehaviour.bosses: kiểu hành vi của boss (ngăn ';')")
    bo.col("boss", meaning="boss", fk=["03_boss/Boss"])
    bo.col("hanh_vi", meaning="kiểu hành vi (ngăn ';')")
    for bid, lst in (beh.get("bosses") or {}).items():
        r = bo.row(bid, B.nguon(("aiBehaviour", "bosses", bid)), raw=lst)
        r.set("boss", bid)
        C.scalar_or_list(r, "hanh_vi", lst, B.BALANCE, ("aiBehaviour", "bosses", bid))
    rest = {k: v for k, v in beh.items() if k not in ("tactics", "roles", "units", "states", "towers", "bosses", "generals")}
    if rest:
        kv = book.kv_sheet("AI_hanh_vi_khac", "Hành vi AI: khóa khác", "aiBehaviour: khóa chưa có sheet riêng")
        book.kv_rows(kv, rest, B.BALANCE, ("aiBehaviour",), "aiBehaviour")

    # ------------------------------------------------------------------ layer B (lane B, pass 5 part 2)
    _b06.build(ctx, book, d)

    # ------------------------------------------------------------------ layer C (AI book, 04/10): code-sourced sheets
    _c06.build(ctx, book)

    # ------------------------------------------------------------------ AI MASTER P5 (05/10): registry, doctrines, ladders, budget, health
    _p5_ai.build(ctx, book)

    # ------------------------------------------------------------------ map / visual / audio W1-A (06/10): AI consumers of GameplayTopology
    _mva_w1a.build_ai(ctx, book)

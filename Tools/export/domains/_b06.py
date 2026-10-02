"""06_ai, layer B (pass 5 part 2): AI_xung_dot (where a mode's AI profile overrides the enemy general's preferred tactic,
the precedence rule of Sim/AI/ConquestAi.P28.cs TickLayered + Sim/AI/Commander.cs AllowedTactic, every mode / mission
goal x general) and AI_xung_dot_do_kho (where the difficulty's tactic switching, AiSkill.For, is blocked by the profile).

The precedence (game): a tactic set before (the player's pick, a mission's) > the general's preference (only where the
profile has generalTactic, or the mode is Weekly / Operation) > balanced; then AllowedTactic: a profile with no tactics or
the flag noGeneralTactic plays balanced; an allowed tactic stays; else balanced if allowed; else the first allowed one."""
from __future__ import annotations

from core.formula import lookup, q, ref as R

from . import _layer_b as LB

CMD = LB.SCRIPTS + "Sim/AI/Commander.cs"
P28 = LB.SCRIPTS + "Sim/AI/ConquestAi.P28.cs"
BEH = LB.SCRIPTS + "Sim/Content/AiBehaviour.cs"
DIFFS = ["Easy", "Normal", "Hard", "VeryHard"]


def _general_tactic(gens: dict, gid: str) -> str:
    """Sim/Content/AiBehaviour.cs GeneralTactic(general): by id (without 'gen.'), else 'default', else balanced."""
    return gens.get(gid) or gens.get("default") or "balanced"


def _allowed(tactics: list, flags: list, known: set, tactic: str) -> str:
    """Sim/AI/Commander.cs AiCommander.AllowedTactic(world, tactic)."""
    if not tactics or "noGeneralTactic" in flags:
        return "balanced"
    if "*" in tactics or tactic in tactics:
        return tactic
    if "balanced" in tactics:
        return "balanced"
    for t in tactics:
        if t in known:
            return t
    return "balanced"


def _switching(ctx):
    """AiSkill.For(difficulty).Switching (Sim/AI/Commander.cs): Never unless the difficulty's block sets it."""
    out = {}
    text = LB.cs_text(CMD)
    i = text.find("public static AiSkill For")
    j = text.find("\n        }", i)
    body = text[i:j]
    line0 = text.count("\n", 0, i) + 1
    for d in DIFFS:
        key = "_ =>" if d == "Normal" else f"AiDifficulty.{d} =>"
        k = body.find(key)
        if k < 0:
            ctx.issue(f"06 AI_xung_dot_do_kho: AiSkill.For {d} not found")
            out[d] = ("NEED_CODE_CHECK", CMD)
            continue
        end = body.find("},", k)
        end = body.find("}", k) if end < 0 else end
        seg = body[k:end if d != "Normal" else body.find(";", k)]
        import re
        m = re.search(r"Switching = TacticSwitching\.(\w+)", seg)
        out[d] = (m.group(1) if m else "Never", f"{LB.short(CMD)}:{line0 + body.count(chr(10), 0, k)}")
    return out


def build(ctx, book, d):
    beh = d.get("aiBehaviour") or {}
    prof = (d.get("aiModeProfiles") or {}).get("profiles") or {}
    gens = beh.get("generals") or {}
    known = {t.get("id") for t in beh.get("tactics") or [] if isinstance(t, dict)}
    hm = book.sheets["AI_ho_so_anh_xa"]
    tg = book.sheets["AI_tuong"]
    hs = book.sheets["AI_ho_so_che_do"]

    # ------------------------------------------------------------------ AI_xung_dot
    xd = book.sheet("AI_xung_dot", "AI: xung đột ghi đè", "Mỗi chế độ / kiểu mục tiêu nhiệm vụ (AI_ho_so_anh_xa) x tướng (AI_tuong): "
                    "chiến thuật tướng ưa thích, hồ sơ có dùng nó không, chiến thuật vào trận theo luật ưu tiên của game "
                    "(ConquestAi.P28.cs TickLayered: tướng chỉ khi hồ sơ generalTactic hoặc chế độ Weekly / Operation; rồi "
                    "Commander.cs AllowedTactic), trạng thái ghi đè", layer="B")
    xd.col("id", meaning="<AI_ho_so_anh_xa.id>/<tướng>")
    xd.col("anh_xa", fk=["06_ai/AI_ho_so_anh_xa"], meaning="chế độ (mode.X) hoặc kiểu mục tiêu nhiệm vụ (goal.X)")
    xd.col("tuong", fk=["06_ai/AI_tuong"], meaning="tướng địch")
    ax = lambda col: R("AI_ho_so_anh_xa", col, "AX")  # noqa: E731
    hsl = lambda col: lookup("AI_ho_so_che_do", col, "{ho_so}")  # noqa: E731
    tactics = "{chien_thuat_cho_phep}"
    has = lambda t: f"ISNUMBER(FIND({q(';')}&{t}&{q(';')},{q(';')}&{tactics}&{q(';')}))"  # noqa: E731
    T = {
        "ho_so": f"={ax('ho_so')}",
        "chien_thuat_cho_phep": f"={hsl('tactics')}&{q('')}",
        "ho_so_dung_tuong": f"={hsl('general_tactic')}=TRUE",
        "co_khong_tuong": f"=ISNUMBER(FIND({q(';noGeneralTactic;')},{q(';')}&{hsl('flags')}&{q(';')}))",
        "ua_thich_tuong": (f"=IF({R('AI_tuong', 'chien_thuat_ua_thich', 'GEN')}&{q('')}<>{q('')},{R('AI_tuong', 'chien_thuat_ua_thich', 'GEN')},"
                           f"IF({R('AI_tuong', 'chien_thuat_ua_thich', 'default')}&{q('')}<>{q('')},{R('AI_tuong', 'chien_thuat_ua_thich', 'default')},"
                           f"{q('balanced')}))"),
        "dung_tuong": f"=OR({{ho_so_dung_tuong}},AND({ax('loai')}={q('mode')},OR({ax('khoa')}={q('Weekly')},{ax('khoa')}={q('Operation')})))",
        "yeu_cau": f"=IF({{dung_tuong}},{{ua_thich_tuong}},{q('balanced')})",
        "vao_tran": (f"=IF(OR({tactics}={q('')},{{co_khong_tuong}}),{q('balanced')},IF(OR({tactics}={q('*')},{has('{yeu_cau}')}),{{yeu_cau}},"
                     f"IF({has(q('balanced'))},{q('balanced')},LEFT({tactics},FIND({q(';')},{tactics}&{q(';')})-1))))"),
        "trang_thai": (f"=IF(OR({tactics}={q('')},{{co_khong_tuong}}),{q('KHONG_CHIEN_THUAT')},IF(NOT({{dung_tuong}}),"
                       f"IF({{ua_thich_tuong}}={q('balanced')},{q('GIU')},{q('CHE_DO_BO_QUA')}),IF({{vao_tran}}={{ua_thich_tuong}},"
                       f"{q('GIU')},{q('HO_SO_GHI_DE')})))"),
    }
    META = {
        "ho_so": ("hồ sơ AI của chế độ / kiểu mục tiêu", False, "AI_ho_so_anh_xa.ho_so"),
        "chien_thuat_cho_phep": ("chiến thuật hồ sơ cho phép (ngăn ';'; '*' mọi chiến thuật; trống: không có chiến thuật)", False,
                                 "AI_ho_so_che_do.tactics"),
        "ho_so_dung_tuong": ("hồ sơ có generalTactic", False, "AI_ho_so_che_do.general_tactic"),
        "co_khong_tuong": ("hồ sơ có cờ noGeneralTactic", False, "AI_ho_so_che_do.flags"),
        "ua_thich_tuong": ("chiến thuật tướng ưa thích (aiBehaviour.generals; không có: 'default', rồi balanced)", True,
                           "Sim/Content/AiBehaviour.cs GeneralTactic"),
        "dung_tuong": ("trận bắt đầu bằng chiến thuật của tướng (hồ sơ generalTactic, hoặc chế độ Weekly / Operation)", True,
                       "Sim/AI/ConquestAi.P28.cs TickLayered"),
        "yeu_cau": ("chiến thuật được xin lúc vào trận (chưa có chiến thuật chọn trước)", True, "Sim/AI/ConquestAi.P28.cs TickLayered"),
        "vao_tran": ("chiến thuật vào trận sau luật hồ sơ", True, "Sim/AI/Commander.cs AiCommander.AllowedTactic"),
        "trang_thai": ("GIU (tướng giữ chiến thuật) / CHE_DO_BO_QUA (chế độ không dùng ưa thích của tướng) / HO_SO_GHI_DE "
                       "(hồ sơ không cho, đổi sang balanced hoặc chiến thuật đầu) / KHONG_CHIEN_THUAT (hồ sơ không có chiến thuật)",
                       False, "python: luật ưu tiên (ConquestAi.P28.cs + Commander.cs)"),
    }
    for c, (m, game, ref_) in META.items():
        LB.declare(xd, c, T[c], ref_, meaning=m, game=game,
                   enum=["GIU", "CHE_DO_BO_QUA", "HO_SO_GHI_DE", "KHONG_CHIEN_THUAT"] if c == "trang_thai" else None)
    for ar in hm.sorted_rows():
        kind, key, pid = ar.values.get("loai"), ar.values.get("khoa"), ar.values.get("ho_so")
        p = prof.get(pid) or {}
        tl = list(p.get("tactics") or [])
        fl = list(p.get("flags") or [])
        for gr in tg.sorted_rows():
            gid = gr.id
            x = xd.row(f"{ar.id}/{gid}", f"{LB.short(P28)} TickLayered + {LB.short(CMD)} AllowedTactic ({ar.id}, {gid})")
            x.set("anh_xa", ar.id)
            x.set("tuong", gid)
            pref = _general_tactic(gens, gid)
            use = bool(p.get("generalTactic", False)) or (kind == "mode" and key in ("Weekly", "Operation"))
            ask = pref if use else "balanced"
            got = _allowed(tl, fl, known, ask)
            if not tl or "noGeneralTactic" in fl:
                st = "KHONG_CHIEN_THUAT"
            elif not use:
                st = "GIU" if pref == "balanced" else "CHE_DO_BO_QUA"
            else:
                st = "GIU" if got == pref else "HO_SO_GHI_DE"
            vals = {"ho_so": pid, "chien_thuat_cho_phep": ";".join(tl), "ho_so_dung_tuong": bool(p.get("generalTactic", False)),
                    "co_khong_tuong": "noGeneralTactic" in fl, "ua_thich_tuong": pref, "dung_tuong": use, "yeu_cau": ask,
                    "vao_tran": got, "trang_thai": st}
            for c, (_m, game, _r) in META.items():
                LB.put(x, c, T[c].replace("AX", str(ar.id)).replace("GEN", str(gid)), vals[c], game=game)

    # ------------------------------------------------------------------ AI_xung_dot_do_kho
    sw = _switching(ctx)
    xk = book.sheet("AI_xung_dot_do_kho", "AI: độ khó x hồ sơ", "Mỗi hồ sơ AI x độ khó: cách đổi chiến thuật giữa trận của độ khó "
                    "(AiSkill.For: Never / WhenLosing / Counter) và việc hồ sơ chặn nó (không chiến thuật, noGeneralTactic hoặc chỉ "
                    "một chiến thuật cho phép: RequestTactic bị từ chối); số ghi đè theo pha của hồ sơ", layer="B")
    xk.col("id", meaning="<hồ sơ>/<độ khó>")
    xk.col("ho_so", fk=["06_ai/AI_ho_so_che_do"], meaning="hồ sơ AI")
    xk.col("do_kho", fk=["05_che_do_kinh_te/Do_kho"], meaning="độ khó")
    xk.col("doi_chien_thuat_do_kho", meaning="AiSkill.For(độ khó).Switching (số trong mã)", source_note="C#: Sim/AI/Commander.cs AiSkill.For",
           enum=["Never", "WhenLosing", "Counter"])
    tac = lookup("AI_ho_so_che_do", "tactics", "{ho_so}") + "&" + q("")
    TK = {
        "so_chien_thuat_cho_phep": (f"=IF({tac}={q('*')},COUNTIFS({R('Chien_thuat', 'id', '*')},{q('*')}),IF({tac}={q('')},0,"
                                    f"LEN({tac})-LEN(SUBSTITUTE({tac},{q(';')},{q('')}))+1))"),
        "hieu_luc": (f"=IF(OR({{so_chien_thuat_cho_phep}}<=1,ISNUMBER(FIND({q(';noGeneralTactic;')},{q(';')}&"
                     f"{lookup('AI_ho_so_che_do', 'flags', '{ho_so}')}&{q(';')}))),{q('Never')},{{doi_chien_thuat_do_kho}})"),
        "trang_thai": (f"=IF({{doi_chien_thuat_do_kho}}={q('Never')},{q('KHONG_DOI')},IF({{hieu_luc}}={q('Never')},{q('HO_SO_CHAN')},"
                       f"{q('DO_KHO_CHO_DOI')}))"),
        "so_ghi_de_pha": f"=COUNTIFS({R('AI_ho_so_pha', 'ai_ho_so_che_do_id', '*')},{{ho_so}})",
    }
    TM = {
        "so_chien_thuat_cho_phep": ("số chiến thuật hồ sơ cho phép ('*': mọi chiến thuật của Chien_thuat)", False, "AI_ho_so_che_do.tactics", None),
        "hieu_luc": ("cách đổi chiến thuật có hiệu lực (Never khi hồ sơ không cho đổi)", True,
                     "Sim/AI/Commander.cs RequestTactic + AllowedTactic", ["Never", "WhenLosing", "Counter"]),
        "trang_thai": ("KHONG_DOI (độ khó không đổi) / HO_SO_CHAN (độ khó cho đổi, hồ sơ chặn) / DO_KHO_CHO_DOI", False,
                       "python: luật ưu tiên", ["KHONG_DOI", "HO_SO_CHAN", "DO_KHO_CHO_DOI"]),
        "so_ghi_de_pha": ("số ghi đè theo pha (phaseOverrides) của hồ sơ", False, "AI_ho_so_pha", None),
    }
    for c, (m, game, ref_, en) in TM.items():
        LB.declare(xk, c, TK[c], ref_, meaning=m, game=game, enum=en)
    n_tac = len(beh.get("tactics") or [])
    for hr in hs.sorted_rows():
        p = prof.get(hr.id) or {}
        tl = list(p.get("tactics") or [])
        fl = list(p.get("flags") or [])
        n = n_tac if "*" in tl else len(tl)
        for dname in DIFFS:
            s, cite = sw[dname]
            x = xk.row(f"{hr.id}/{dname}", f"{cite} (AiSkill.For {dname}); balance.json aiModeProfiles.profiles.{hr.id}")
            x.set("ho_so", hr.id)
            x.set("do_kho", dname)
            x.set("doi_chien_thuat_do_kho", s)
            eff = "Never" if n <= 1 or "noGeneralTactic" in fl else s
            st = "KHONG_DOI" if s == "Never" else "HO_SO_CHAN" if eff == "Never" else "DO_KHO_CHO_DOI"
            vals = {"so_chien_thuat_cho_phep": float(n), "hieu_luc": eff, "trang_thai": st,
                    "so_ghi_de_pha": float(len(p.get("phaseOverrides") or []))}
            for c, (_m, game, _r, _e) in TM.items():
                LB.put(x, c, TK[c], vals[c], game=game)

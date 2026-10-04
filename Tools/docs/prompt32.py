"""The design document's prompt 32 L8 section "Sổ tay đạn / Ammunition handbook", in Vietnamese and English, every number
read from balance.json (no number written by hand): the six damage types against ground, air and structures with their
examples, the penetration row and a worked example, the special marks, what stops which rounds, what to hit structures
with. The game's own handbook (Game/Hud/AmmoHandbook.cs, the Dossier's tab) is generated the same way from the same data;
HandbookP32Tests checks the game's strings against the data. build_doc.py calls ammo_handbook.

    python Tools/docs/prompt32.py > handbook.html   # the section alone (a quick look; the PDF is build_doc.py's)
"""
from __future__ import annotations

import html
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "balance"))
from p32_tower_prices import Model, front  # noqa: E402

TYPES = ["Kinetic", "ShapedCharge", "HighExplosive", "Fire", "Fragmentation", "Energy"]
KINDS = ["Ground", "Air", "Structure"]
NAMES = {
    "vi": {"Kinetic": "Động năng", "ShapedCharge": "Nổ lõm", "HighExplosive": "Nổ mạnh", "Fire": "Lửa", "Fragmentation": "Mảnh",
           "Energy": "Năng lượng", "Ground": "Mặt đất", "Air": "Máy bay", "Structure": "Công trình"},
    "en": {"Kinetic": "Kinetic", "ShapedCharge": "Shaped charge", "HighExplosive": "High explosive", "Fire": "Fire",
           "Fragmentation": "Fragmentation", "Energy": "Energy", "Ground": "Ground", "Air": "Air", "Structure": "Structures"},
}
STEPS = {
    "vi": ["Hơn từ 2 cấp", "Hơn 1 cấp", "Bằng cấp", "Thiếu 1 cấp", "Thiếu 2 cấp", "Thiếu 3 cấp", "Thiếu từ 4 cấp"],
    "en": ["2 levels or more above", "1 level above", "Level", "1 level under", "2 levels under", "3 levels under", "4 levels or more under"],
}
REACTIVE_CAP = 0.8  # HandbookFacts.ReactiveCap (the code reads it from there)
ROUND_HOLD, MIN_SWITCH = 2.0, 0.5  # WeaponDef.RoundHoldSeconds, MinSwitchSeconds
MAX_UNIT, MAX_BOSS = 4, 5  # ArmourLevels.MaxUnit, Max


def num(x, lang, digits=2):
    s = f"{x:.{digits}f}".rstrip("0").rstrip(".") if digits else f"{round(x):.0f}"
    return s.replace(".", ",") if lang == "vi" else s


def mult(x, lang):
    return "×" + num(x, lang)


def pct(x, lang):
    return num(x * 100, lang, 0) + "%"


def faces(v):
    a = v.get("armour", 0)
    if isinstance(a, list):
        return a + [a[-1]] * (4 - len(a))
    return [a, max(0, a - 1), max(0, a - 2), max(0, a - 2)]


class Handbook:
    def __init__(self):
        self.m = Model()
        self.d = self.m.d
        self.t = self.d["damageTable"]

    def card(self, v):
        return float(v.get("cp", 0) or 0) > 0 and not v.get("static") and not v.get("boss") and not v.get("elite") and not v.get("eliteOf") and not v.get("fort")

    def examples(self, fits, n=3):
        count = {}
        for v in self.m.V.values():
            if not self.card(v):
                continue
            for w in self.m.mounts(v):
                if float(w.get("damage", 0) or 0) > 0 and fits(w):
                    count[w["id"]] = count.get(w["id"], 0) + 1
        out, seen = [], set()
        for k in sorted(count, key=lambda k: (-count[k], k)):
            name = self.name(self.m.W[k])
            if name in seen:
                continue  # two weapon lines of the same real weapon read as one example
            seen.add(name)
            out.append(self.m.W[k])
        return out[:n]

    @staticmethod
    def name(w):
        return w.get("real") or w["id"]

    def type_of(self, w, kind):
        return self.m.type_of(w, kind)

    def effective(self, w, armour, kind="Ground"):
        roof = float(w.get("minRange", 0)) > 0 or w.get("projectile") in ("Bomb", "Drone")
        return self.m.armour_mult(w, armour, kind, roof) * self.type_of(w, kind)

    def section(self, lang, esc, table):
        N, t = NAMES[lang], self.t
        vi = lang == "vi"
        out = [f"<h3>{'Sổ tay đạn (tiếng Việt)' if vi else 'Ammunition handbook (English)'}</h3>"]
        # 1. Types.
        rows = [[esc(N[k])] + [mult(t[k][kind], lang) for kind in KINDS] for k in TYPES]
        out.append(table([("Loại" if vi else "Type")] + [N[k] for k in KINDS], rows, "dps"))
        for k in TYPES:
            best = max(KINDS, key=lambda kind: t[k][kind])
            worst = min(KINDS, key=lambda kind: t[k][kind])
            ex = ", ".join(esc(self.name(w)) for w in self.examples(lambda w, k=k: w.get("damageType", "Kinetic") == k)) or ("chưa có" if vi else "none yet")
            out.append(f"<p><b>{esc(N[k])}</b>: " + (f"mạnh với {N[best]} ({mult(t[k][best], lang)}), yếu với {N[worst]} ({mult(t[k][worst], lang)}). Ví dụ: {ex}."
                                                     if vi else f"strong against {N[best]} ({mult(t[k][best], lang)}), weak against {N[worst]} ({mult(t[k][worst], lang)}). For example: {ex}.") + "</p>")
        # 2. Penetration and the worked example.
        # Combat final 04/10: two tables, direct fire and top attack (a weapon reads one or the other, never both).
        def seven(row):
            row = list(row)
            if len(row) == 5:
                row = [row[0]] + row
            return row + [row[-1]] * (7 - len(row))
        pens, tops = seven(t["penetration"]), seven(t.get("topAttack") or t["penetration"])
        out.append(table(["Xuyên so với giáp mặt trúng" if vi else "Penetration against the face's armour", "Bắn thẳng" if vi else "Direct fire",
                          "Đánh nóc (giáp nóc)" if vi else "Top attack (roof)"],
                         [[STEPS[lang][i], mult(pens[i], lang), mult(tops[i], lang)] for i in range(7)], "dps"))
        out.append("<p>" + (f"Giáp có hướng: trước, hông, sau và nóc (xe tới cấp {MAX_UNIT}, boss tới cấp {MAX_BOSS}). Đạn bắn thẳng dùng cột bắn thẳng theo mặt trúng; "
                            f"đạn không đánh nóc mà rơi xuống nóc, và mọi phát lên máy bay, không có mức áp đảo ({mult(pens[1], lang)} là cao nhất). "
                            f"Vũ khí đánh nóc luôn trúng giáp nóc và chỉ dùng cột đánh nóc (không nhân hai bảng, không chặn ở {mult(pens[1], lang)})."
                            if vi else f"Armour has a direction: front, side, rear and roof (vehicles up to level {MAX_UNIT}, bosses up to {MAX_BOSS}). Direct fire reads the direct column "
                            f"against the face it strikes; a round that is not a top attack but comes down on the roof, and every hit on an aircraft, never overmatches "
                            f"({mult(pens[1], lang)} is the most). A top-attack weapon always strikes the roof and reads the top-attack column only (never both tables, no cap at {mult(pens[1], lang)}).") + "</p>")
        hb = self.d.get("handbook", {})
        shooter, target = self.m.V.get(hb.get("exampleShooter", "ifv")), self.m.V.get(hb.get("exampleTarget", "main_battle_tank"))
        if shooter and target and shooter.get("weapon") in self.m.W:
            w = self.m.W[shooter["weapon"]]
            f = faces(target)
            hp = float(target["hp"]) * float(self.d["toughness"]["vehicles"])
            fm, sm = self.effective(w, f[0]), self.effective(w, f[1])
            dmg = float(w.get("damage", 0))
            out.append("<p>" + (f"Ví dụ: một phát {esc(self.name(w))} của {esc(shooter['id'])} (xuyên {num(float(w.get('pen', 0)), lang)}, sát thương {num(dmg, lang, 0)}) lên {esc(target['id'])} (máu {num(hp, lang, 0)}): "
                                f"giáp trước cấp {f[0]}: {mult(fm, lang)}, {num(dmg * fm, lang, 0)}; giáp hông cấp {f[1]}: {mult(sm, lang)}, {num(dmg * sm, lang, 0)}."
                                if vi else f"Worked example: one shot of the {esc(shooter['id'])}'s {esc(self.name(w))} (penetration {num(float(w.get('pen', 0)), lang)}, {num(dmg, lang, 0)} damage) on a {esc(target['id'])} "
                                f"(health {num(hp, lang, 0)}): front armour {f[0]}: {mult(fm, lang)}, {num(dmg * fm, lang, 0)}; side armour {f[1]}: {mult(sm, lang)}, {num(dmg * sm, lang, 0)}.") + "</p>")
        # 3. Marks.
        def ex(fits, n=3):
            return ", ".join(esc(self.name(w)) for w in self.examples(fits, n)) or ("chưa có" if vi else "none yet")
        he_s, th = t["HighExplosive"]["Structure"], t.get("thermobaric", 2.0)
        marks = [
            ("Đánh nóc" if vi else "Top attack", ("Trúng giáp nóc, mặt mỏng nhất, theo bảng đánh nóc riêng. Ví dụ: " if vi else "Strikes the roof armour, the thinnest face, on its own top-attack table. For example: ") + ex(lambda w: w.get("topAttack"))),
            ("Nhiệt áp" if vi else "Thermobaric", (f"{mult(th, lang)} lên công trình thay cho {mult(he_s, lang)} của nổ mạnh (thay, không nhân thêm). Ví dụ: " if vi
                                                   else f"{mult(th, lang)} on structures instead of high explosive's {mult(he_s, lang)} (replaces, never adds). For example: ") + ex(lambda w: w.get("thermobaric"))),
            ("Dẫn đường" if vi else "Guided", ("Bám mục tiêu; APS / phòng thủ điểm bắn hạ được, pháo sáng đánh lừa loại nhắm máy bay. Ví dụ: " if vi
                                              else "Follows its target; APS and point defence can shoot it down, flares draw off those aimed at aircraft. For example: ") + ex(lambda w: w.get("projectile") in ("Missile", "Drone"))),
            ("Nổ trên không" if vi else "Airburst", (f"Đạn mảnh: {mult(t['Fragmentation']['Air'], lang)} lên máy bay. Ví dụ: " if vi else f"Fragmentation: {mult(t['Fragmentation']['Air'], lang)} against aircraft. For example: ")
             + ex(lambda w: w.get("damageType") == "Fragmentation" and w.get("targets", "Ground") in ("All", "Air"))),
            ("Đạn thay thế" if vi else "Second rounds", (f"Súng tự đổi khi mục tiêu hợp; giữ đạn ít nhất {num(ROUND_HOLD, lang)} s, đổi mất ít nhất {num(MIN_SWITCH, lang)} s." if vi
                                                         else f"The gun switches on its own when the target suits; a round stays in {num(ROUND_HOLD, lang)} s at least, a switch takes {num(MIN_SWITCH, lang)} s at least.")),
            ("Tầm tối thiểu" if vi else "Minimum range", ", ".join(f"{esc(self.name(w))} ({num(float(w['minRange']), lang, 0)} m)" for w in self.examples(lambda w: float(w.get("minRange", 0)) > 0))),
        ]
        out.append(table(["Dấu" if vi else "Mark", "Nghĩa" if vi else "Meaning"], [[esc(a), b] for a, b in marks], "dps"))
        # 4. Defences.
        cram = (self.m.V.get("c_ram", {}).get("aps") or {}).get("shells", 0)
        laser = (self.m.V.get("laser_ad_station", {}).get("aps") or {}).get("shells", 0)
        if vi:
            dfs = [("Giáp phản ứng nổ", f"Giảm tới {pct(REACTIVE_CAP, lang)} sát thương nổ lõm; đầu nổ kép xuyên qua."),
                   ("Lồng chắn", "Đỡ nổ lõm của rốc-két, tên lửa, drone; động năng và nhiệt áp đi qua."),
                   ("SELF_APS", "Chỉ tên lửa dẫn đường, drone, rốc-két bắn thẳng; không chặn đạn pháo xe tăng."),
                   ("POINT_DEFENSE (C-RAM, la-de, vòm)", f"Tên lửa, drone, rốc-két, một phần đạn pháo binh (C-RAM {pct(cram, lang)}, la-de {pct(laser, lang)}); không chặn đạn pháo xe tăng; mỗi viên một hệ (gần nhất)."),
                   ("Pháo sáng", "Đánh lừa tên lửa dẫn đường nhắm máy bay."), ("Khói", "Che mục tiêu, làm mù la-de phòng thủ điểm."),
                   ("Gây nhiễu", "Làm tản drone và hỏa lực dẫn đường gọi vào vùng nhiễu."), ("Khiên", "Vòm hấp thụ mọi đòn trừ năng lượng; khiên tháp chỉ đỡ đạn nhắm vào tháp.")]
        else:
            dfs = [("Reactive armour", f"Cuts shaped charges by up to {pct(REACTIVE_CAP, lang)}; a tandem warhead goes through."),
                   ("Cage", "Takes shaped charges on rockets, missiles, drones; kinetic and thermobaric go through."),
                   ("SELF_APS", "Guided missiles, drones, direct-fire rockets only; never a tank's shell."),
                   ("POINT_DEFENSE (C-RAM, lasers, dome)", f"Missiles, drones, rockets, a share of artillery shells (C-RAM {pct(cram, lang)}, laser {pct(laser, lang)}); never a tank's shell; one system per round (the nearest)."),
                   ("Flares", "Draw off guided missiles aimed at aircraft."), ("Smoke", "Hides what is in it, blinds point-defence lasers."),
                   ("Jamming", "Scatters drones and guided fire called into its bubble."), ("Shield", "A dome absorbs every hit but energy; a tower's shield only rounds aimed at the tower.")]
        out.append(table(["Hệ" if vi else "System", "Chặn" if vi else "Stops"], [[esc(a), esc(b)] for a, b in dfs], "dps"))
        # 5. Structures and walls.
        rows = [[("Nổ mạnh nhiệt áp" if vi else "Thermobaric high explosive"), mult(th, lang)]] + \
               [[esc(N[k]), mult(t[k]["Structure"], lang)] for k in sorted(TYPES, key=lambda k: -t[k]["Structure"])]
        out.append(table(["Đánh công trình bằng" if vi else "Against structures", "Hệ số" if vi else "Multiplier"], rows, "dps"))
        walls = self.d["base"].get("walls", {})
        out.append("<p>" + (f"Xe phá tường ({esc(', '.join(walls.get('breakers', [])))}) gây {mult(float(walls.get('breakerMultiplier', 1.5)), lang)} lên tường (không lên tháp hay nhà chính)."
                            if vi else f"Wall breakers ({esc(', '.join(walls.get('breakers', [])))}) do {mult(float(walls.get('breakerMultiplier', 1.5)), lang)} to walls (not to towers or the HQ).") + "</p>")
        return "".join(out)


def _table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table class='{cls}'><tr>{head}</tr>{body}</table>"


def ammo_handbook(game=None, h=None):
    esc = (h or {}).get("esc", html.escape)
    table = (h or {}).get("table", _table)
    book = Handbook()
    return ("<div class='section'><h2>Sổ tay đạn / Ammunition handbook</h2><p>Sinh từ dữ liệu (balance.json) như mục Sổ tay đạn trong "
            "Hồ sơ của game; chạm vào chip ĐÁNH NÓC, ĐẠN THAY THẾ, NỔ TRÊN KHÔNG, DẪN ĐƯỜNG, PHÁ CÔNG TRÌNH, PHÁ TƯỜNG trên trang chi tiết "
            "mở đúng mục. / Generated from the data, as the game's Dossier tab.</p>"
            + book.section("vi", esc, table) + book.section("en", esc, table) + "</div>")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(ammo_handbook())

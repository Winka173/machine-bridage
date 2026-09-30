"""Prompt 25: applies the owner's balance spreadsheet (Docs/balance/Machine_Brigade_Can_bang.xlsx) to the game data.

    python Tools/balance/import_xlsx.py --upto A2        # applies A1 (Cao, Trung, Thap), then A2
    python Tools/balance/import_xlsx.py --upto all       # every step this script knows
    python Tools/balance/import_xlsx.py --upto A2 --dry  # reports, writes nothing

The steps run in the task order of the sheet "Viec cho agent" (A1 Cao, A1 Trung, A1 Thap, A2, A3, A4, A5, B7, B8)
and each is re-runnable: running the same --upto twice changes nothing the second time. Every number comes from the
spreadsheet (read with openpyxl, data_only: the values the formulas computed); the script holds only the rules that
map a row onto the data, and the owner's decisions where the sheet offers a choice (DECISIONS 25A). balance.json is
edited in place, field by field on each entry's own line (jsonc_edit.py), never re-serialised.

Rows whose id is not in the data, and rows that belong to a later task (names D1, sizes B1, bosses C1/C2), go into
Docs/balance/apply-report.md with the reason; nothing is guessed.
"""
from __future__ import annotations

import argparse
import collections
import math
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import Doc, Entry, fmt, loads  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX = os.path.join(ROOT, "Docs", "balance", "Machine_Brigade_Can_bang.xlsx")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
REFS = os.path.join(ROOT, "Tools", "docs", "unit_refs.json")
REPORT = os.path.join(ROOT, "Docs", "balance", "apply-report.md")

STEPS = ["A1-Cao", "A1-Trung", "A1-Thap", "A1-review", "A2", "A3", "A4", "A5", "B7", "B8", "review"]
PRIORITY = {"A1-Cao": "Cao", "A1-Trung": "Trung", "A1-Thap": "Thấp"}

DEG_PER_RAD = 180.0 / math.pi


# ----------------------------------------------------------------------------------------------------------------
# Reading the spreadsheet


def sheet(wb, name):
    rows = list(wb[name].iter_rows(values_only=True))
    head = rows[0]
    return head, [r for r in rows[1:] if any(c is not None for c in r)]


def num(text) -> float:
    """A number as the sheet writes it: '1.500' (thousands), '6,5' (decimal comma), '~24.000'."""
    if isinstance(text, (int, float)):
        return float(text)
    s = str(text).strip().lstrip("~").strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    return float(s.replace(",", "."))


NUM = r"~?\d{1,3}(?:\.\d{3})+(?![\d,])|~?\d+(?:[.,]\d+)?"


def nums(text) -> list[float]:
    return [num(m) for m in re.findall(NUM, str(text or ""))]


# ----------------------------------------------------------------------------------------------------------------
# The game data, resolved (inherits, and from A3 the weapon families)


class Game:
    def __init__(self, doc: Doc):
        self.doc = doc
        self.refresh()

    def refresh(self):
        d = self.doc.data()
        self.data = d
        self.raw_weapons = {w["id"]: w for w in d["weapons"]}
        self.families = {f["id"]: f for f in d.get("weaponFamilies", [])}
        self.vehicles_raw = {v["id"]: v for v in d["vehicles"]}
        self.supports = {s["id"]: s for s in d["supports"]}
        self.toughness = d["toughness"]["vehicles"]
        self.strikes = d["firepower"]["strikes"]
        self.vehicle_blasts = d["firepower"]["vehicleBlasts"]
        self._w = {}
        self._v = {}

    def weapon(self, wid, family=True):
        key = (wid, family)
        if key in self._w:
            return self._w[key]
        w = dict(self.raw_weapons[wid])
        if "inherits" in w:
            base = dict(self.weapon(w["inherits"], family=False))
            base.update(w)
            w = base
        if family and w.get("weaponFamily") in self.families:
            for k, v in self.families[w["weaponFamily"]].items():
                if k not in ("id", "real"):
                    w[k] = v
        self._w[key] = w
        return w

    def parent_value(self, wid, key):
        """The value a weapon would take for key without its own line's field (inherited or default)."""
        w = self.raw_weapons[wid]
        if "inherits" in w:
            return self.weapon(w["inherits"], family=False).get(key)
        return None

    def vehicle(self, vid):
        if vid in self._v:
            return self._v[vid]
        v = dict(self.vehicles_raw[vid])
        if "inherits" in v:
            base = dict(self.vehicle(v["inherits"]))
            base.update(v)
            v = base
        self._v[vid] = v
        return v

    def is_boss(self, vid):
        v = self.vehicles_raw.get(vid) or {}
        return any(k in v for k in ("rank", "variantOf", "frame")) or v.get("boss") is True

    def mounts(self, vid):
        v = self.vehicle(vid)
        out = [v.get("weapon")]
        for m in v.get("secondary", []) or []:
            out.append(m.get("weapon"))
        return [m for m in out if m]

    def users(self, wid):
        return [vid for vid in self.vehicles_raw if wid in self.mounts(vid)]


def armour_faces(v) -> list[int]:
    a = v.get("armour", 0)
    if isinstance(a, list):
        return list(a)
    return [a, max(0, a - 1), max(0, a - 2), max(0, a - 2)]


def cadence(w):
    """(mode, rate, rounds, sustained DPS) of a weapon as the game fires it (WeaponDef.SustainedDps)."""
    cd = w.get("cooldown", 1.0)
    burst = w.get("burst", 1)
    bi = w.get("burstInterval", 0.1)
    clip = w.get("clip", 0)
    cr = w.get("clipReload", 0.0)
    if clip > 0:
        cycle = (clip - 1) * cd + cr
        n = clip
        mode, rate = "băng", 1 / cd
    elif burst > 1:
        cycle = cd + (burst - 1) * bi
        n = burst
        mode, rate = "loạt", 1 / bi if bi > 0 else 0
    else:
        cycle, n = cd, 1
        mode, rate = "từng phát", 1 / cd
    return mode, rate, n, w.get("damage", 0) * n / max(0.05, cycle)


def close(a, b, rel=1e-4):
    if a is None or b is None:
        return a is b
    if isinstance(a, (list, dict, str, bool)) or isinstance(b, (list, dict, str, bool)):
        return a == b
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


# ----------------------------------------------------------------------------------------------------------------
# The report


class Report:
    def __init__(self):
        self.rows = collections.defaultdict(list)  # step -> [(sheet, id, item, outcome, detail)]

    def add(self, step, sheet_name, id_, item, outcome, detail=""):
        self.rows[step].append((sheet_name, id_, item, outcome, detail))

    def section(self, step, title, intro=""):
        rows = self.rows.get(step, [])
        counts = collections.Counter((r[0], r[3]) for r in rows)
        sheets = sorted({r[0] for r in rows})
        out = [f"<!-- step:{step} -->", f"## {title}", ""]
        if intro:
            out += [intro, ""]
        out += ["| Sheet | Applied | Already so | Deferred | Skipped |", "|---|---|---|---|---|"]
        for s in sheets:
            out.append(f"| {s} | {counts[(s, 'applied')]} | {counts[(s, 'already')]} | {counts[(s, 'deferred')]} | {counts[(s, 'skipped')]} |")
        out += ["", "| Sheet | id | Item | Outcome | Detail |", "|---|---|---|---|---|"]
        for r in rows:
            detail = str(r[4]).replace("|", "/").replace("\n", " ")
            out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {detail} |")
        out += ["", f"<!-- /step:{step} -->", ""]
        return "\n".join(out)

    def write(self, sections):
        text = ""
        if os.path.exists(REPORT):
            with open(REPORT, encoding="utf-8") as f:
                text = f.read()
        if not text.startswith("# "):
            text = HEADER
        for step, body in sections:
            pat = re.compile(r"<!-- step:" + re.escape(step) + r" -->.*?<!-- /step:" + re.escape(step) + r" -->\n?", re.S)
            if pat.search(text):
                text = pat.sub(lambda _: body, text)
            else:
                text = text.rstrip("\n") + "\n\n" + body
        with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.rstrip("\n") + "\n")


HEADER = """# Balance spreadsheet: apply report (prompt 25)

What `Tools/balance/import_xlsx.py` applied from `Docs/balance/Machine_Brigade_Can_bang.xlsx`, sheet by sheet, and
what it left and why. Outcomes: **applied** (the data now holds the sheet's number), **already** (the data already
held it), **deferred** (the row belongs to a later task of the sheet "Việc cho agent": names D1, model sizes B1,
models B2, bosses C1, boss weapons C2), **skipped** (no id in the data, a contradiction, or a measurement that did not
confirm it). Decisions and their reasons: `Docs/DECISIONS.md`, section 25A. Each step's section is rewritten when the
script runs it again.
"""


# ----------------------------------------------------------------------------------------------------------------
# Writing weapons


FAMILY_KEYS = ("projectileSpeed", "splash", "projectileModel", "roundWeight")


class Writer:
    def __init__(self, doc: Doc, game: Game, step_index: int):
        self.doc = doc
        self.game = game
        self.step_index = step_index

    def at_least(self, step):
        return self.step_index >= STEPS.index(step)

    # Weapons ------------------------------------------------------------------------------------------------

    def weapon_field(self, wid, key, value):
        """Sets a weapon's field so its resolved value is <value>, on its own line; False when it already was."""
        g = self.game
        w = g.weapon(wid)
        if close(w.get(key), value):
            return False
        if self.at_least("A3") and key in FAMILY_KEYS and g.weapon(wid, family=False).get("weaponFamily"):
            return False  # the family holds it (A3, A5)
        self.doc.edit("weapons", wid, lambda e: e.set(key, value))
        g.refresh()
        return True

    def weapon_unset(self, wid, key, zero=0):
        """Makes a field inactive: removed from the weapon's own line, or set to zero over an inherited value."""
        g = self.game
        own = g.raw_weapons[wid]
        inherited = g.parent_value(wid, key)
        if key in own and not inherited:
            self.doc.edit("weapons", wid, lambda e: e.remove(key))
            g.refresh()
            return True
        if g.weapon(wid).get(key) and inherited:
            return self.weapon_field(wid, key, zero)
        return False

    # Vehicles -----------------------------------------------------------------------------------------------

    def vehicle_field(self, vid, key, value):
        if close(self.game.vehicle(vid).get(key), value):
            return False
        self.doc.edit("vehicles", vid, lambda e: e.set(key, value))
        self.game.refresh()
        return True

    def vehicle_sub(self, vid, key, sub, value):
        cur = (self.game.vehicle(vid).get(key) or {}).get(sub)
        if close(cur, value):
            return False
        if key not in self.game.vehicles_raw[vid]:
            merged = dict(self.game.vehicle(vid).get(key) or {})
            merged[sub] = value
            return self.vehicle_field(vid, key, merged)
        self.doc.edit("vehicles", vid, lambda e: e.set_sub(key, sub, value))
        self.game.refresh()
        return True

    def vehicle_load(self, vid, wid, n):
        """A carrier's stores of one weapon per full load: the weapon's own load when no other carrier uses it."""
        g = self.game
        users = [u for u in g.users(wid) if g.vehicle(u).get("flying")]
        cur = (g.vehicle(vid).get("loads") or {}).get(wid, g.weapon(wid).get("load", 0))
        if cur == n:
            return False
        if users == [vid] and not (g.vehicle(vid).get("loads") or {}).get(wid):
            return self.weapon_field(wid, "load", n)
        loads = dict(g.vehicle(vid).get("loads") or {})
        loads[wid] = n
        return self.vehicle_field(vid, "loads", loads)

    def remove_mount(self, vid, wid):
        v = self.game.vehicles_raw[vid]
        sec = v.get("secondary") or []
        if not any(m.get("weapon") == wid for m in sec):
            return False

        def fn(e: Entry):
            raw = e.raw("secondary")
            items = _array_items(raw)
            keep = [raw[s:t] for s, t in items if f'"weapon": "{wid}"' not in raw[s:t].replace('"weapon":"', '"weapon": "')]
            if len(keep) == len(items):
                return
            if not keep:
                e.set_raw("secondary", "[]")
                return
            # Keep the other mounts' text (and the line breaks between them) as they were.
            text = raw
            for s, t in reversed(items):
                piece = raw[s:t]
                if piece in keep:
                    continue
                j = s - 1
                while text[j] in " \t\r\n":
                    j -= 1
                if text[j] == ",":
                    text = text[:j] + text[t:]
                else:
                    k = t
                    while text[k] in " \t\r\n":
                        k += 1
                    if text[k] == ",":
                        k += 1
                        while text[k] in " \t":
                            k += 1
                    text = text[:s] + text[k:]
            e.set_raw("secondary", text)

        self.doc.edit("vehicles", vid, fn)
        self.game.refresh()
        return True

    def add_mount(self, vid, mount: dict):
        v = self.game.vehicle(vid)
        if any(m.get("weapon") == mount["weapon"] and m.get("slot") == mount.get("slot") for m in v.get("secondary") or []):
            return False

        def fn(e: Entry):
            raw = e.raw("secondary")
            piece = fmt(mount)
            if raw is None:
                e.set_raw("secondary", f"[ {piece} ]", after="weapon")
            elif raw.strip() == "[]":
                e.set_raw("secondary", f"[ {piece} ]")
            else:
                close_at = raw.rindex("]")
                body = raw[:close_at].rstrip()
                e.set_raw("secondary", body + f", {piece} " + raw[close_at:])

        self.doc.edit("vehicles", vid, fn)
        self.game.refresh()
        return True

    def swap_mount(self, vid, old, new):
        v = self.game.vehicles_raw[vid]
        if v.get("weapon") == old:
            return self.vehicle_field(vid, "weapon", new)
        if not any(m.get("weapon") == old for m in v.get("secondary") or []):
            return False

        def fn(e: Entry):
            raw = e.raw("secondary")
            e.set_raw("secondary", raw.replace(f'"weapon": "{old}"', f'"weapon": "{new}"'))

        self.doc.edit("vehicles", vid, fn)
        self.game.refresh()
        return True

    def new_weapon(self, after, line_fields: dict):
        wid = line_fields["id"]
        if wid in self.game.raw_weapons:
            changed = False
            for k, v in line_fields.items():
                if k != "id":
                    changed |= self.weapon_field(wid, k, v) if k not in ("inherits",) else False
            return changed
        self.doc.insert_after("weapons", after, fmt(line_fields))
        self.game.refresh()
        return True


def _array_items(raw):
    """(start, end) of each element of a JSON array's text."""
    from jsonc_edit import _skip, _value_end
    items = []
    i = 1
    while True:
        i = _skip(raw, i)
        if raw[i] == "]":
            return items
        if raw[i] == ",":
            i += 1
            continue
        j = _value_end(raw, i)
        items.append((i, j))
        i = j


# ----------------------------------------------------------------------------------------------------------------
# A2: a weapon row of "Vũ khí đề xuất"

# Column indices of "Vũ khí đề xuất".
W_ID, W_REAL, W_KIND, W_USERS, W_TYPE, W_FORM, W_SIZE = 0, 1, 2, 3, 4, 5, 6
W_PEN0, W_PEN, W_DMG0, W_DMG, W_MODE0, W_MODE, W_RATE0, W_RATE, W_N0, W_N, W_REST0, W_REST = range(7, 19)
W_RANGE0, W_RANGE, W_SPEED0, W_SPEED, W_FLIGHT, W_SPLASH0, W_SPLASH, W_DPS0, W_DPS = range(19, 28)


def weapon_targets(row):
    """What the game's fields must be for a row's proposal ('đề xuất' columns)."""
    t = {}
    if row[W_DMG] is not None:
        t["damage"] = float(row[W_DMG])
    if row[W_PEN] is not None:
        t["pen"] = int(row[W_PEN])
    if row[W_RANGE] is not None:
        t["range"] = float(row[W_RANGE])
    if row[W_SPEED] is not None:
        t["projectileSpeed"] = float(row[W_SPEED])
    if row[W_SPLASH] is not None:
        t["splash"] = float(row[W_SPLASH])
    return t


def cadence_targets(row, current_gap=None):
    """The sheet's cycle (n rounds at the rate, then the rest) as the game's fields; None when a cell is empty.

    The sheet times a cycle as n / rate + rest; the game as n - 1 gaps plus the magazine change (clip) or the
    cooldown after a salvo's last round (burst). The change (or cooldown) is written as rest + one gap, so the game's
    cycle, and its sustained DPS, are the sheet's exactly (DECISIONS 25A)."""
    mode, rate, n, rest = row[W_MODE], row[W_RATE], row[W_N], row[W_REST]
    if mode is None or rate in (None, 0) or n in (None, 0) or rest is None:
        return None
    gap = 1.0 / rate
    # The sheet rounds rates (2.22 a second for 0.45 s apart): a gap within 1.5 % of the game's stays the game's.
    if current_gap and abs(current_gap * rate - 1) <= 0.015:
        gap = current_gap
    if mode == "từng phát":
        return {"cooldown": round(gap, 4), "burst": 1, "clip": 0}
    if mode == "băng":
        return {"cooldown": round(gap, 4), "clip": int(n), "clipReload": round(rest + gap, 4), "burst": 1}
    if mode == "loạt":
        return {"burst": int(n), "burstInterval": round(gap, 4), "cooldown": round(rest + gap, 4), "clip": 0}
    raise ValueError(mode)


def sheet_dps(row):
    dmg, mode, rate, n, rest = row[W_DMG], row[W_MODE], row[W_RATE], row[W_N], row[W_REST]
    if None in (dmg, mode, rate, n, rest):
        return None
    return dmg * rate if mode == "từng phát" else dmg * n / (n / rate + rest)


def apply_weapon_row(wr: Writer, row, report: Report, step, sheet_name="Vũ khí đề xuất", why=""):
    """Applies one weapon's proposal; returns the list of fields written."""
    g = wr.game
    wid = row[W_ID]
    if wid not in g.raw_weapons:
        report.add(step, sheet_name, wid, "weapon", "skipped", "no such weapon id in balance.json")
        return []
    done = []
    for k, v in weapon_targets(row).items():
        if k == "splash" and v == 0 and not g.weapon(wid).get("splash"):
            continue
        if wr.weapon_field(wid, k, v):
            done.append(f"{k} {fmt(v)}")
    w = g.weapon(wid)
    mode, rate, n, dps = cadence(w)
    cad = cadence_targets(row, 1.0 / rate if mode == row[W_MODE] and rate else None)
    if cad is None:
        report.add(step, sheet_name, wid, "cadence", "skipped", "the sheet's mode, rate, rounds or rest cell is empty")
    else:
        want = sheet_dps(row)
        # Within 3 % of the sheet's sustained DPS in the same mode and rounds, the game's cadence stands (the sheet
        # rounds rates and times a cycle as n / rate + rest: DECISIONS 25A); the test allows 5 %.
        keep = mode == row[W_MODE] and n == int(row[W_N]) and want and abs(dps / want - 1) <= 0.03
        # A single shot's rate as the sheet shows it (two decimals: 0.12 a second for one every 8 s).
        if mode == row[W_MODE] == "từng phát" and round(rate, 2) == round(row[W_RATE], 2):
            keep = True
        if not keep:
            for k in ("burst", "burstInterval", "cooldown", "clip", "clipReload"):
                if k not in cad:
                    continue
                v = cad[k]
                if k == "clip" and v == 0:
                    if wr.weapon_unset(wid, "clip"):
                        done.append("clip removed")
                    wr.weapon_unset(wid, "clipReload")
                    continue
                if k == "burst" and v == 1:
                    if g.weapon(wid).get("burst", 1) != 1:
                        if wr.weapon_unset(wid, "burst", zero=1):
                            done.append("burst 1")
                        wr.weapon_unset(wid, "burstInterval", zero=0.1)
                    continue
                if wr.weapon_field(wid, k, v):
                    done.append(f"{k} {fmt(v)}")
    outcome = "applied" if done else "already"
    report.add(step, sheet_name, wid, "weapon", outcome, (", ".join(done) or "as the sheet") + (f" ({why})" if why else ""))
    return done


# ----------------------------------------------------------------------------------------------------------------
# A1: "Thay đổi chi tiết"

# The weapons an A1 weapon row is about, on the unit it names (checked against the unit's mounts). Their numbers
# come from the weapon's own row of "Vũ khí đề xuất", which carries the same proposal in columns.
A1_WEAPONS = {
    ("aa_turret", "Vũ khí và tham khảo"): ["tower_flak_30"],
    ("artillery", "Vũ khí: lựu pháo 155 mm"): ["howitzer"],
    ("attack_jet", "Vũ khí: FAB-250"): ["jet_bombs"],
    ("attack_jet", "Vũ khí: Kh-29L, R-60"): ["kh29", "r60"],
    ("fighter_jet", "Vũ khí: AIM-120, AIM-9X"): ["air_to_air", "wvr_aam"],
    ("iron_beam", "Vũ khí: laser 100 kW"): ["hel_beam"],
    ("missile_battery", "Vũ khí: Patriot PAC-2"): ["patriot"],
    ("rocket_turret.guided", "Vũ khí: GMLRS dẫn đường"): ["turret_gmlrs"],
    ("sam_launcher", "Vũ khí: 9M317 Buk"): ["buk_launcher"],
    ("scout_heli", "Vũ khí: Hydra 70"): ["scout_rockets"],
    ("swarm_carrier", "Vũ khí: thêm Rapid Dragon"): ["jassm"],
    ("wheeled_gun", "Vũ khí: 120 mm"): ["gun_105_wheeled"],
    ("zu23_technical", "Vũ khí: ZU-23-2"): ["zu23"],
    ("aa_vehicle", "Vũ khí: Stinger"): ["sam"],
    ("artillery_emplacement.mortar", "Vũ khí: cối 240 mm"): ["mortar_240_fixed"],
    ("attack_helicopter", "Vũ khí: Hellfire, Stinger ATAS"): ["hellfire_standoff", "stinger_atas"],
    ("attack_jet", "Vũ khí: GSh-30-2"): ["jet_cannon"],
    ("ballistic_launcher", "Vũ khí: Iskander"): ["ballistic_missile"],
    ("bmpt", "Vũ khí: 2A42 đôi"): ["twin_30_bmpt"],
    ("bmpt", "Vũ khí: Mk 19 40 mm"): ["agl_40"],
    ("c_ram", "Vũ khí: Phalanx 20 mm"): ["c_ram_gatling"],
    ("gun_turret.long", "Vũ khí: 120 mm L/55"): ["turret_gun_120_long"],
    ("gunship_heli", "Vũ khí: tên lửa chống tăng"): ["heli_atgm"],
    ("heavy_bomber", "Vũ khí: Kh-101"): ["air_cruise_missile"],
    ("heavy_bomber", "Vũ khí: FAB-500"): ["bomber_payload"],
    ("heavy_turret", "Vũ khí: 155 mm đôi"): ["gun_155_twin_fort"],
    ("ifv", "Vũ khí: 2A42 30 mm"): ["ifv_30"],
    ("ifv", "Vũ khí: TOW-2"): ["atgm"],
    ("leviathan", "Vũ khí: 460 mm"): ["leviathan_460"],
    ("long_sam", "Vũ khí: 48N6"): ["sam_48n6"],
    ("missile_battery.lrr", "Vũ khí"): ["sam_battery_lrr"],
    ("missile_battery.pac3", "Vũ khí: PAC-3"): ["sam_pac3"],
    ("stealth_bomber", "Vũ khí: JASSM"): ["jassm"],
    ("stealth_fighter", "Vũ khí và giá"): ["air_to_air"],
    ("wingman_drone", "Vũ khí: AIM-9"): ["aim9"],
    ("laser_tank", "Giá, tăng dần"): [],
    ("tank_destroyer", "Tầm, nhịp, giá"): ["gun_105_long"],
    ("vbied", "Máu, nổ lan"): ["detonator"],
    ("bmpt", "Vũ khí: 9M120 Ataka"): ["ataka"],
    ("flame_tank", "Vũ khí: súng phun lửa"): ["flamethrower"],
    ("heavy_aa", "Vũ khí: 2A38 30 mm đôi"): ["twin_30_flak"],
    ("heavy_rocket_artillery", "Vũ khí: Smerch 300 mm"): ["rockets_300mm"],
    ("hover_gunboat", "Vũ khí: AK-630 30 mm"): ["hover_ciws"],
    ("light_tank", "Vũ khí: 57 mm"): ["gun_57mm"],
    ("mortar_carrier", "Vũ khí: cối 120 mm"): ["mortar_120"],
    ("rocket_turret", "Vũ khí: Grad"): ["turret_rockets"],
    ("shahed_truck", "Vũ khí: Shahed-136"): ["shahed"],
    ("smoke_carrier", "Vũ khí: M2 12,7 mm"): [],
}

# Where a row offers a choice ("chọn một", "hoặc"), the option taken (DECISIONS 25A).
CHOICES = {
    ("aa_turret", "Vũ khí và tham khảo"): "the reference moves to the 2A38 (the weapon is kept); the anti-aircraft value "
                                          "falls through the tower flak's new rate (tower_flak_30's row)",
    ("gun_turret.long", "Vũ khí: 120 mm L/55"): "penetration +1 (the weapon row's 'xuyên đề xuất' 5), not a first-shot bonus",
    ("rocket_turret", "Vũ khí: Grad"): "+15 % damage (the weapon row's 66 a rocket), not the shorter reload",
}

# References (Tools/docs/unit_refs.json "real"), where the row names them.
A1_REFS = {
    "aa_turret": {"replace": {"Oerlikon GDF 35 mm (Skyguard)": "2K22 Tunguska (2A38 30 mm)"}},
    "aa_turret.sam": {"real": ["Mistral ATLAS", "RBS-70", "Starstreak LML"]},
    "heavy_tank": {"drop": ["T-14 Armata (bản 152 mm)"]},
    "morrigan": {"real": ["Su-57", "F-22 Raptor"], "media": ["Ace Combat"]},
}


def parse_armour(text, current):
    t = str(text)
    m = re.search(r"(\d)\s*/\s*(\d)\s*/\s*(\d)\s*/\s*(\d)", t)
    if m:
        return [int(x) for x in m.groups()]
    faces = list(current)
    found = False
    for i, word in enumerate(("trước", "hông", "sau", "nóc")):
        m = re.search(word + r"\s*(\d)(?:\s*→\s*(\d))?", t)
        if m:
            faces[i] = int(m.group(2) or m.group(1))
            found = True
    if found:
        return faces
    m = re.search(r"giáp\s*(\d)", t)
    if m:
        f = int(m.group(1))
        return [f, max(0, f - 1), max(0, f - 2), max(0, f - 2)]
    return None


def a1(wr: Writer, wb, report: Report, step, weapon_rows, unit_rows, refs):
    g = wr.game
    _, rows = sheet(wb, "Thay đổi chi tiết")
    prio = PRIORITY[step]
    sh = "Thay đổi chi tiết"
    for r in rows:
        id_, unit, cat, cur, prop, why, ref, p = r[:8]
        if p != prio:
            continue
        cat = str(cat)
        vid = id_
        item = cat

        def add(outcome, detail=""):
            report.add(step, sh, id_, item, outcome, detail)

        if vid not in g.vehicles_raw:
            add("skipped", "no such vehicle id in balance.json")
            continue
        boss = g.is_boss(vid)
        if cat.startswith("Tên"):
            add("deferred", "name: task D1 (sheet Tên đề xuất)")
            continue
        if cat.startswith("Kích thước"):
            add("deferred", "model size: task B1")
            continue
        if cat == "Dữ liệu vũ khí":
            add("deferred", "a boss's main weapon as data: task C2")
            continue
        if boss and not cat.startswith("Giáp") and (vid, cat) not in A1_WEAPONS:
            add("deferred", "boss health and weapons: task C1 (sheet Boss đề xuất)")
            continue

        done = []
        # Prices ------------------------------------------------------------------------------------------------
        if "giá" in cat.lower():
            m = re.search(r"(\d+)\s*CP", str(prop)) or re.search(r"giá\s*\d+\s*→\s*(\d+)", str(prop))
            if m:
                if wr.vehicle_field(vid, "cp", int(m.group(1))):
                    done.append(f"cp {m.group(1)}")
        # Health ------------------------------------------------------------------------------------------------
        if cat.startswith("Máu") or cat in ("Giáp, máu",):
            m = re.search(r"(" + NUM + r")\s*máu", str(prop)) or re.search(r"máu\s*(" + NUM + r")", str(prop)) \
                or re.fullmatch(r"\s*(" + NUM + r")\s*", str(prop))
            if m:
                hp = round(num(m.group(1)) / g.toughness)
                if wr.vehicle_field(vid, "hp", hp):
                    done.append(f"hp {hp} (the sheet's {fmt(num(m.group(1)))} over toughness {fmt(g.toughness)})")
        # Armour ------------------------------------------------------------------------------------------------
        if cat.startswith("Giáp"):
            faces = parse_armour(prop, armour_faces(g.vehicle(vid)))
            if faces is None:
                add("skipped", f"no armour levels in '{prop}'")
                continue
            if faces != armour_faces(g.vehicle(vid)):
                wr.vehicle_field(vid, "armour", faces)
                done.append(f"armour {faces}")
        # Speed -------------------------------------------------------------------------------------------------
        if cat.startswith("Tốc độ") and "xoay" not in cat:
            m = re.search(r"(" + NUM + r")\s*m/s", str(prop))
            if m:
                if wr.vehicle_field(vid, "speed", num(m.group(1))):
                    done.append(f"speed {fmt(num(m.group(1)))}")
        if "xoay" in cat:
            now = re.findall(r"\d+", str(cur))
            new = re.findall(r"\d+", str(prop))
            # The sheet shows turn rates in rad/s rounded (60 deg/s shows as 1); the data holds deg/s.
            for i, key in enumerate(("turnRate", "turretTurnRate")):
                if now[i] != new[i]:
                    deg = round(int(new[i]) * DEG_PER_RAD)
                    if wr.vehicle_field(vid, key, deg):
                        done.append(f"{key} {deg} ({new[i]} rad/s)")
        # Vision ------------------------------------------------------------------------------------------------
        if cat == "Tầm nhìn":
            m = re.search(r"(\d+)\s*m", str(prop))
            if wr.vehicle_field(vid, "vision", int(m.group(1))):
                done.append(f"vision {m.group(1)}")
        # Death blast -------------------------------------------------------------------------------------------
        if cat.startswith("Nổ khi bị phá"):
            m = re.search(r"(" + NUM + r")\s*m", str(prop))
            if wr.vehicle_sub(vid, "deathExplosion", "radius", num(m.group(1))):
                done.append(f"deathExplosion.radius {fmt(num(m.group(1)))}")
        # References --------------------------------------------------------------------------------------------
        if "tham khảo" in cat.lower():
            if vid in A1_REFS:
                if refs.apply(vid, A1_REFS[vid]):
                    done.append("reference (unit_refs.json)")
                elif not done:
                    done.append("")
            elif "model" in cat.lower():
                # "Đổi model sang M109A7 xích; giáp trước 1→2; tốc độ 7→6": the stats now, the model and its
                # reference with the model (task B2).
                m = re.search(r"tốc độ\s*[\d,]+\s*→\s*([\d,]+)", str(prop))
                if m and wr.vehicle_field(vid, "speed", num(m.group(1))):
                    done.append(f"speed {fmt(num(m.group(1)))}")
                m = re.search(r"giáp trước\s*\d\s*→\s*(\d)", str(prop))
                faces = armour_faces(g.vehicle(vid))
                if m and faces[0] != int(m.group(1)):
                    faces[0] = int(m.group(1))
                    wr.vehicle_field(vid, "armour", faces)
                    done.append(f"front armour {m.group(1)}")
                if done:
                    done.append("the model and its reference wait for the model (task B2)")
        # Behaviour ---------------------------------------------------------------------------------------------
        if cat == "Hành vi":
            if vid == "scout_jeep":
                share = nums(re.search(r"\d+%", str(prop)).group(0))[0] / 100.0
                if wr.vehicle_field(vid, "stillCamo", round(1 - share, 2)):
                    done.append(f"stillCamo {fmt(round(1 - share, 2))} (seen at {int(share * 100)} % of a spotter's sight when still)")
            elif vid == "mlrs":
                lo, hi = nums(re.search(r"\d+\s*[–-]\s*\d+\s*m", str(prop)).group(0))[:2]
                if wr.vehicle_field(vid, "scoot", {"shots": 1, "min": lo, "max": hi}):
                    done.append(f"scoot after every salvo, {fmt(lo)}-{fmt(hi)} m")
        # Weapons -----------------------------------------------------------------------------------------------
        key = (vid, cat)
        if key in A1_WEAPONS:
            mounts = g.mounts(vid)
            for wid in A1_WEAPONS[key]:
                if wid not in mounts and wid not in ("jassm", "heli_atgm"):
                    report.add(step, sh, id_, cat, "skipped", f"{wid} is not on {vid}")
                    continue
                if wid in weapon_rows:
                    got = apply_weapon_row(wr, weapon_rows[wid], report, step, "Vũ khí đề xuất", f"for {vid}: {cat}")
                    if got:
                        done.append(f"{wid}: {', '.join(got)}")
            done += a1_special(wr, key, prop, unit_rows, report, step)
        if key in CHOICES:
            done.append("choice: " + CHOICES[key])
        text = "; ".join(d for d in done if d)
        if done:
            add("applied" if text else "already", text or "the data already holds it")
        elif key in A1_WEAPONS or "tham khảo" in cat.lower() or cat == "Hành vi":
            detail = {
                "artillery": "model and reference follow the model change: task B2 (the armour and speed are its Trung rows)",
            }.get(vid, "")
            if cat == "Hành vi" and vid not in ("scout_jeep", "mlrs"):
                add("skipped", "no rule for this behaviour")
            elif detail and "model" in cat.lower():
                add("deferred", detail)
            else:
                add("already", ALREADY.get(key, "the data already holds it"))
        else:
            add("already", "the data already holds it")


def a1_special(wr: Writer, key, prop, unit_rows, report, step):
    """The loadout parts of A1 weapon rows: stores per load, mounts added or dropped (sheet Đơn vị – vũ khí)."""
    g = wr.game
    vid, cat = key
    done = []
    prop = str(prop)
    if key == ("attack_jet", "Vũ khí: FAB-250"):
        n = int(nums(re.search(r"(\d+)\s*quả", prop).group(1))[0])
        if wr.vehicle_load(vid, "jet_bombs", n):
            done.append(f"jet_bombs {n} a load")
    if key == ("scout_heli", "Vũ khí: Hydra 70"):
        n = int(nums(re.search(r"(\d+)\s*quả", prop).group(1))[0])
        if wr.vehicle_load(vid, "scout_rockets", n):
            done.append(f"scout_rockets {n} a load")
    if key == ("heavy_bomber", "Vũ khí: FAB-500"):
        n = int(nums(re.search(r"(\d+)\s*quả", prop).group(1))[0])
        if wr.vehicle_load(vid, "bomber_payload", n):
            done.append(f"bomber_payload {n} a sortie")
    if key == ("stealth_fighter", "Vũ khí và giá"):
        extra = int(nums(re.search(r"\+(\d+)\s*AIM-120", prop).group(1))[0])
        base = g.weapon("air_to_air").get("load", 0)
        if wr.vehicle_load(vid, "air_to_air", base + extra):
            done.append(f"air_to_air {base + extra} a load")
    if key == ("swarm_carrier", "Vũ khí: thêm Rapid Dragon"):
        done += loadout(wr, vid, unit_rows, report, step)
        n = int(nums(re.search(r"thêm\s*(\d+)\s*tên lửa", prop).group(1))[0])
        if wr.vehicle_load(vid, "jassm", n):
            done.append(f"jassm {n} a sortie")
    if key == ("iron_beam", "Vũ khí: laser 100 kW"):
        # "đánh chặn cả đạn cối và rốc-két pháo binh": rockets it already takes; mortar bombs at the C-RAM's share.
        share = g.vehicle("c_ram")["aps"]["shells"]
        if wr.vehicle_sub(vid, "aps", "shells", share):
            done.append(f"aps shells {fmt(share)} (the C-RAM's share of mortar bombs and shells)")
    if key == ("laser_tank", "Giá, tăng dần"):
        m = re.search(r"×\s*2\s*sau\s*(\d+)\s*s", prop)
        secs = float(m.group(1))
        ramp = dict(g.weapon("focus_laser").get("ramp") or {})
        if not close(ramp.get("seconds"), secs):
            wr.doc.edit("weapons", "focus_laser", lambda e: e.set_sub("ramp", "seconds", secs))
            g.refresh()
            done.append(f"focus_laser ramp to x2 in {fmt(secs)} s")
    if key == ("gunship_heli", "Vũ khí: tên lửa chống tăng"):
        done += loadout(wr, vid, unit_rows, report, step)
    if key == ("heavy_turret", "Vũ khí: 155 mm đôi"):
        # The armour-piercing 155 mm round, switched to by target like the heavy tank's gun (its "he").
        m = re.search(r"xuyên\s*(\d)\s*,\s*~?(\d+)\s*/\s*phát", prop)
        pen, dmg = int(m.group(1)), float(m.group(2))
        line = {"id": "gun_155_twin_ap", "inherits": "gun_155_twin_fort", "real": "M284 155 mm (twin) AP", "damageType": "Kinetic",
                "damage": dmg, "pen": pen, "splash": 0, "piercing": True, "he": "gun_155_twin_fort"}
        if wr.new_weapon("gun_155_twin_fort", line):
            done.append(f"gun_155_twin_ap (AP, pen {pen}, {fmt(dmg)} a round)")
        for vid2 in ("heavy_turret",):
            if wr.vehicle_field(vid2, "weapon", "gun_155_twin_ap"):
                done.append("heavy_turret fires gun_155_twin_ap, its HE round gun_155_twin_fort for structures and light armour")
    return done


# Rows the data already answers in another way (the report says how).
ALREADY = {
    ("smoke_carrier", "Vũ khí: M2 12,7 mm"): "it carries hmg_selfdef_15 (15 m, the engineer's) already; the sheet's 22 m is out of date",
}


def loadout(wr: Writer, vid, unit_rows, report, step):
    """A unit's rows of 'Đơn vị – vũ khí': mounts dropped (kept 0), added, or swapped (the change note)."""
    g = wr.game
    done = []
    sh = "Đơn vị – vũ khí"
    rows = [r for r in unit_rows if r[0] == vid]
    for r in rows:
        wid, keep, note = r[3], r[5], str(r[12] or "")
        if keep == 0:
            if wr.remove_mount(vid, wid):
                done.append(f"{wid} dropped")
                report.add(step, sh, vid, wid, "applied", "dropped (kept 0)")
            else:
                report.add(step, sh, vid, wid, "already", "not mounted")
        elif note.startswith("Vũ khí thêm"):
            slot = {"jassm": ("drone", "Free"), "hmg_roof": ("mg", "Free")}.get(wid)
            if wid in g.mounts(vid):
                report.add(step, sh, vid, wid, "already", "mounted")
            elif slot and wr.add_mount(vid, {"weapon": wid, "slot": slot[0], "aim": slot[1]}):
                done.append(f"{wid} added")
                report.add(step, sh, vid, wid, "applied", f"added on slot {slot[0]}")
            else:
                report.add(step, sh, vid, wid, "skipped", "no mount rule")
    # Swaps and new weapons named in a unit's change note.
    notes = {str(r[12] or "") for r in rows}
    for note in notes:
        if note.startswith("Đổi Hellfire → 9M120 Ataka"):
            m = re.search(r"9M120 Ataka\s*·\s*tốc độ\s*(\d+)\s*·\s*tầm\s*(\d+)", A1_TEXT.get(("gunship_heli", "Vũ khí: tên lửa chống tăng"), ""))
            rng = float(m.group(2)) if m else None
            hell = g.weapon("heli_atgm")
            line = {"id": "heli_ataka", "inherits": "ataka", "load": hell.get("load", 4), "burst": 1, "cooldown": hell["cooldown"],
                    "range": rng or hell["range"]}
            if wr.new_weapon("ataka", line):
                done.append("heli_ataka (9M120 Ataka at the Hellfire mount's rate and load)")
            if wr.swap_mount(vid, "heli_atgm", "heli_ataka"):
                done.append("heli_atgm -> heli_ataka")
            report.add(step, sh, vid, "heli_atgm", "applied" if done else "already", "Hellfire -> 9M120 Ataka")
        if note.startswith("Đổi Stinger → tên lửa 57E6"):
            m = re.search(r"1\s*×\s*(\d+),\s*Mảnh xuyên\s*(\d),\s*tầm\s*(\d+),\s*tốc độ\s*(\d+)", note)
            dmg, pen, rng, spd = float(m.group(1)), int(m.group(2)), float(m.group(3)), float(m.group(4))
            sam = g.weapon("sam")
            line = {"id": "missile_57e6", "real": "57E6 (Pantsir)", "family": "aa_missile", "size": SIZE_FOR["missile_57e6"], "pen": pen,
                    "projectileModel": sam.get("projectileModel"), "projectileScale": 0.85, "damageType": "Fragmentation",
                    "damage": dmg, "cooldown": sam["cooldown"], "range": rng, "projectileSpeed": spd, "splash": sam.get("splash", 2),
                    "impactTier": "Medium", "projectile": "Missile", "targets": "Air", "flareResist": g.weapon("buk_launcher").get("flareResist", 0.8)}
            ch = wr.new_weapon("sam", line)
            ch |= wr.swap_mount(vid, "sam", "missile_57e6")
            report.add(step, sh, vid, "sam", "applied" if ch else "already", "Stinger -> 57E6: " + note.split("—")[0].strip())
            if ch:
                done.append("missile_57e6")
        if note.startswith("Thêm tên lửa bắn qua nòng"):
            m = re.search(r"1 quả\s*×\s*(\d+),\s*xuyên\s*(\d),\s*mỗi\s*(\d+)\s*s,\s*tầm\s*(\d+)", note)
            dmg, pen, every, rng = float(m.group(1)), int(m.group(2)), float(m.group(3)), float(m.group(4))
            ref = g.weapon("kornet_twin")
            line = {"id": "gun_launched_atgm", "real": "gun-launched ATGM (9M117 class)", "family": "atgm", "size": SIZE_FOR["gun_launched_atgm"],
                    "pen": pen, "piercing": True, "projectileModel": ref.get("projectileModel"), "projectileScale": 0.7,
                    "damageType": "ShapedCharge", "damage": dmg, "cooldown": every, "range": rng, "projectileSpeed": ref["projectileSpeed"],
                    "impactTier": "Medium", "projectile": "Missile"}
            ch = wr.new_weapon("atgm", line)
            ch |= wr.add_mount(vid, {"weapon": "gun_launched_atgm", "slot": "main", "aim": "Turret"})
            report.add(step, sh, vid, "gun_launched_atgm", "applied" if ch else "already", note.split("—")[0].strip())
            if ch:
                done.append("gun_launched_atgm")
        if note.startswith("Thêm 1 AIM-120") or note.startswith("Hydra:") or note.startswith("FAB-250:"):
            pass  # the A1 rows carry these (stores per load)
    return done


# Sizes of the new weapons on prompt 13's calibre scale: damage per round rises with size within a family, so a new
# round's size sits where its damage falls between its family's neighbours (DECISIONS 25A).
SIZE_FOR = {"missile_57e6": 7, "gun_launched_atgm": 24}

A1_TEXT = {}


# ----------------------------------------------------------------------------------------------------------------
# References


class Refs:
    def __init__(self, path):
        self.doc = Doc(path)

    def apply(self, vid, rule):
        d = self.doc.data()
        cur = d.get(vid)
        if cur is None:
            line = {"real": rule.get("real", []), "media": rule.get("media", []), "note": ""}
            text = self.doc.text
            at = text.rstrip().rindex("}")
            prev = text[:at].rstrip()
            self.doc.text = prev + ",\n  " + fmt(vid) + ": " + fmt(line).replace("{ ", "{ ").rstrip() + "\n}\n"
            return True
        real = list(cur.get("real", []))
        if "replace" in rule:
            real = [rule["replace"].get(x, x) for x in real]
        if "drop" in rule:
            real = [x for x in real if x not in rule["drop"]]
        if "real" in rule:
            real = rule["real"]
        media = rule.get("media", cur.get("media", []))
        if real == cur.get("real") and media == cur.get("media"):
            return False
        # Edit the entry's own line.
        m = re.search(r'\n  ' + re.escape(fmt(vid)) + r': (\{.*\})', self.doc.text)
        e = Entry(m.group(1))
        e.set("real", real, after="real")
        e.set("media", media, after="real")
        self.doc.text = self.doc.text[:m.start(1)] + e.text + self.doc.text[m.end(1):]
        return True


# ----------------------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upto", default="all")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    last = len(STEPS) - 1 if args.upto == "all" else STEPS.index(args.upto)

    wb = openpyxl.load_workbook(XLSX, data_only=True)
    _, wrows = sheet(wb, "Vũ khí đề xuất")
    weapon_rows = {r[W_ID]: r for r in wrows if r[W_ID]}
    _, unit_rows = sheet(wb, "Đơn vị – vũ khí")
    _, trows = sheet(wb, "Thay đổi chi tiết")
    for r in trows:
        A1_TEXT[(r[0], str(r[2]))] = str(r[4])

    doc = Doc(BALANCE)
    game = Game(doc)
    refs = Refs(REFS)
    report = Report()
    sections = []
    import steps_more  # noqa: E402  (A2 onwards)

    for i in range(last + 1):
        step = STEPS[i]
        wr = Writer(doc, game, i)
        if step in PRIORITY:
            a1(wr, wb, report, step, weapon_rows, unit_rows, refs)
            sections.append((step, report.section(step, f"A1 {PRIORITY[step]}: sheet Thay đổi chi tiết")))
        else:
            title = steps_more.run(step, wr, wb, report, weapon_rows, unit_rows)
            if title:
                sections.append((step, report.section(step, title, steps_more.INTRO.get(step, ""))))

    if args.dry:
        for _, body in sections:
            print(body)
        return
    changed = doc.save()
    changed |= refs.doc.save()
    report.write(sections)
    print("balance.json changed" if changed else "no change to the data")


if __name__ == "__main__":
    main()

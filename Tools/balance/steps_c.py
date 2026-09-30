"""Prompt 25 importer, C1 and C2: the bosses (sheet "Boss đề xuất"; see import_xlsx.py and DECISIONS 25C).

C1, per boss row:
  * health: the sheet's "Máu đề xuất (gốc)" is what the boss has before the campaign's scale, after the bosses'
    toughness (balance.json "toughness.bosses") and a mini boss's rank share ("bossRanks.mini.hp"), as the sheet's
    "Máu hiện" column shows today's data; the data holds it over both, to the nearest 50;
  * weapons: the rule table WEAPONS below says which mounts a row's "Vũ khí thêm / đổi" adds or swaps (existing weapons
    by id; the new ones take the row's numbers); a mount goes on the part the row names, or on a part the boss's
    variants leave off, so a variant keeps its own loadout ("Giữ");
  * damage a second: "DPS thường mục tiêu (vs giáp 3)" is the boss's sustained fire against armour 3 on the sheet's
    own formula (a weapon's sustained damage x its type's factor on the ground x the penetration step against level 3,
    sheet "Hệ số"); the boss's ordinary weapons take "weaponDamage" so the whole comes to it (what the boss system
    fires, a ship's main battery, the cruise missiles, the supergun's shell, counts at its own numbers; the crusher is
    a contact weapon and is left out);
  * super weapons ("Siêu vũ khí đề xuất"): only the twelve main bosses have one, the big attack of prompt 18 with the
    row's numbers (SUPER below says which fields a row's words fill); a mini boss's big attack is taken away, and every
    big attack no boss (or duel) names any more leaves the data.
C2: the Gungnir's 80 cm gun and the Kronos's bucket wheel become weapons (its main weapon; a mount on the wheel), which
the supergun's shot and the crusher fire with their numbers.
Every run is a no-op the second time (counts are targets, entries are compared before they are written).
"""
from __future__ import annotations

import copy
import json
import re

import import_xlsx as X
from jsonc_edit import Entry, _skip, fmt, loads

SHEET = "Boss đề xuất"

INTRO = {
    "C1": ("Every row of \"Boss đề xuất\": health before the campaign's scale (the data holds it over the bosses' toughness "
           "0.85 and a mini boss's rank share 0.55, as the sheet's \"Máu hiện\" reads today's), the weapons added or "
           "swapped, the boss's ordinary damage a second against armour 3 (its weapons' `weaponDamage`), and the super "
           "weapons: only the twelve main bosses keep a big attack, with the row's numbers; a mini boss's is taken away. "
           "The boss rows of \"Thay đổi chi tiết\" and \"Kiểm tra từng mục\" that earlier steps left to C1 are listed "
           "with what answers them."),
    "C2": ("The Gungnir's 80 cm gun and the Kronos's bucket wheel as weapons (rows \"Dữ liệu vũ khí\"): the supergun's "
           "shot and the crusher fire them with their numbers, so the weapons tables and the Guide show them."),
}

# ----------------------------------------------------------------------------------------------------------------
# The sheet


def rows(wb):
    head, body = X.sheet(wb, SHEET)
    return {r[0]: dict(zip(head, r)) for r in body if r[0]}


def factors(wb):
    """The sheet's "Hệ số": damage type on the ground, and the penetration step against the armour level."""
    ws = wb["Hệ số"]
    types, pens = {}, {}
    names = {"Động năng": "Kinetic", "Nổ lõm": "ShapedCharge", "Nổ mạnh": "HighExplosive", "Lửa": "Fire",
             "Mảnh": "Fragmentation", "Năng lượng": "Energy"}
    for r in ws.iter_rows(values_only=True):
        if r[0] in names:
            types[names[r[0]]] = float(r[1])
        m = re.match(r"^(≥|≤)?\s*([+−-]?\d+)$", str(r[0] or "").strip())
        if m and r[1] is not None:
            pens[int(m.group(2).replace("−", "-").replace("+", ""))] = float(r[1])
    return types, pens


def pen_step(pens, diff):
    lo, hi = min(pens), max(pens)
    return pens[max(lo, min(hi, diff))]


# ----------------------------------------------------------------------------------------------------------------
# The bosses as the loader builds them (BossTemplates.Expand): library parts, dropped parts, variants


NOT_INHERITED = ("id", "rank", "variantOf", "variant", "phases", "radioSpawn", "bigAttack", "bigAttackScale", "damageScale",
                 "weaponDamage", "size", "dropParts", "tint", "mark", "variantName", "hiddenNodes")


def _merge(under, over):
    d = copy.deepcopy(under)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            m = dict(d[k])
            m.update(copy.deepcopy(v))
            d[k] = m
        else:
            d[k] = copy.deepcopy(v)
    return d


def _build(d, library):
    parts = d.get("parts") or []
    secondary = list(d.get("secondary") or [])
    for k, part in enumerate(parts):
        if not isinstance(part, dict) or "use" not in part:
            continue
        merged = _merge(library[part["use"]], part)
        merged.pop("use")
        if "weapon" in merged:
            if "mounts" not in merged:
                mount = {"weapon": merged["weapon"]}
                for key in ("slot", "aim", "arc", "model"):
                    if merged.get(key) is not None:
                        mount[key] = merged[key]
                mount.setdefault("slot", "gun")
                secondary.append(mount)
                merged["mounts"] = [len(secondary)]
            for key in ("weapon", "slot", "aim", "arc", "model"):
                merged.pop(key, None)
        parts[k] = merged
    if secondary:
        d["secondary"] = secondary
    return d


def _strip(d, keep):
    parts = d.get("parts") or []
    secondary = d.get("secondary") or []
    mounts = 1 + len(secondary)
    kept, kept_m, dropped_m = [], set(), set()
    for p in parts:
        stays = keep(p.get("id", ""))
        if stays:
            kept.append(p)
        for m in p.get("mounts", []) or []:
            (kept_m if stays else dropped_m).add(int(m))
    if len(kept) == len(parts):
        return
    gone = [m in dropped_m and m not in kept_m for m in range(mounts)]
    order = [m for m in range(mounts) if not gone[m]]
    if gone[0]:
        promoted = secondary[order[0] - 1]
        d["weapon"] = promoted["weapon"]
    remap = {m: k for k, m in enumerate(order)}
    d["secondary"] = [secondary[m - 1] for m in order[1:]]
    for p in kept:
        for key in ("mounts", "affects"):
            if key in p:
                p[key] = [remap[int(m)] for m in p[key] if int(m) in remap]
    crash = ((d.get("tiers") or {}).get("crash") or {})
    if crash and "guns" in crash:
        crash["guns"] = [remap[int(m)] for m in crash["guns"] if int(m) in remap]
    d["parts"] = kept


def expand(data):
    """Every boss (and variant) as the loader builds it, before its rank's scaling: {id: entry}."""
    library = data.get("bossParts", {})
    before = {}
    out = {}
    for pass_ in (0, 1):
        for v in data["vehicles"]:
            variant = isinstance(v.get("variantOf"), str)
            if variant != (pass_ == 1):
                continue
            if not variant and not (v.get("boss") is True or "frame" in v or "rank" in v):
                continue
            if variant:
                d = copy.deepcopy(before[v["variantOf"]])
                for k in NOT_INHERITED:
                    d.pop(k, None)
                rules = v.get("variant") or {}
                if "keep" in rules:
                    keep = set(rules["keep"])
                    _strip(d, lambda i: i in keep)
                if "drop" in rules:
                    drop = set(rules["drop"])
                    _strip(d, lambda i: i not in drop)
                for p in d.get("parts") or []:
                    if p.get("id") in (rules.get("tune") or {}):
                        p.update(rules["tune"][p["id"]])
                for k, val in v.items():
                    if k == "variant":
                        continue
                    if isinstance(val, dict) and isinstance(d.get(k), dict):
                        d[k] = _merge(d[k], val)
                    else:
                        d[k] = copy.deepcopy(val)
                d["boss"] = True
                d.setdefault("rank", "mini")
            else:
                d = _build(copy.deepcopy(v), library)
                if d.get("dropParts"):
                    drop = set(d["dropParts"])
                    _strip(d, lambda i: i not in drop)
            before[d["id"]] = copy.deepcopy(d)
            d.setdefault("rank", "main")
            out[d["id"]] = d
    return out


def mounts_of(b):
    return [b.get("weapon")] + [m.get("weapon") for m in b.get("secondary") or []]


def check(data, built):
    """The rules the loader and BossPartsTests hold a boss to: mounts on parts in range and on one part at most, every
    part doing something when it breaks, the crash guns, the big attack's parts. A list of problems (empty: fine)."""
    attacks = {a["id"]: a for a in data.get("bigAttacks", [])}
    problems = []
    for bid, b in built.items():
        n = len(mounts_of(b))
        seen = []
        big = attacks.get(b.get("bigAttack") or "")
        uses = set()
        if big:
            for s in _resolved(attacks, big)["strikes"]:
                uses |= set(s.get("parts", []))
        part_ids = {p.get("id") for p in b.get("parts") or []}
        for p in b.get("parts") or []:
            ms = [int(m) for m in p.get("mounts", []) or []]
            seen += ms
            if any(m < 0 or m >= n for m in ms):
                problems.append(f"{bid}.{p['id']}: mount out of range {ms} (of {n})")
            does = ms or p.get("skills") or p.get("stops") or p.get("speed", 1) < 1 or p.get("turn", 1) < 1 \
                or p.get("cadence", 1) > 1 or p.get("spread", 1) > 1 or p["id"] in uses
            if not does:
                problems.append(f"{bid}.{p['id']}: does nothing when it breaks")
        if len(seen) != len(set(seen)):
            problems.append(f"{bid}: a mount on two parts")
        for m in (((b.get("tiers") or {}).get("crash") or {}).get("guns") or []):
            if m <= 0 or m >= n:
                problems.append(f"{bid}: crash gun {m} out of range")
        for m in ((b.get("wake") or {}).get("mounts") or []):
            if m <= 0 or m >= n:
                problems.append(f"{bid}: wake mount {m} out of range")
        for p in uses:
            if p not in part_ids:
                problems.append(f"{bid}: its big attack's part '{p}' is not on it")
        if b.get("bigAttack") and not big:
            problems.append(f"{bid}: unknown big attack {b['bigAttack']}")
    return problems


def _resolved(attacks, a, depth=0):
    if "from" not in a:
        return a
    base = copy.deepcopy(_resolved(attacks, attacks[a["from"]], depth + 1))
    for k, v in a.items():
        if k == "from":
            continue
        if k == "strikes":
            for i, s in enumerate(v):
                if i < len(base["strikes"]):
                    base["strikes"][i] = _merge(base["strikes"][i], s)
                else:
                    base["strikes"].append(s)
            continue
        base[k] = v
    return base


# ----------------------------------------------------------------------------------------------------------------
# Damage a second against armour 3 (the sheet's formula)


def sustained(w):
    """FirePower.Sustained for a boss (no aircraft loads): a cycle's rounds over the cycle, a launcher's reload counted."""
    dmg = w.get("damage", 0)
    if dmg <= 0:
        return 0.0
    cd, burst, bi = w.get("cooldown", 1.0), w.get("burst", 1), w.get("burstInterval", 0.1)
    clip, cr = w.get("clip", 0), w.get("clipReload", 0.0)
    if clip > 0:
        cycle, n = (clip - 1) * cd + cr, clip
    else:
        cycle, n = cd + (burst - 1) * bi, burst
    cycle = max(0.05, cycle)
    per = dmg * max(1, n)
    ammo = w.get("ammo", 0)
    if ammo > 0:
        return per * ammo / (cycle * ammo + w.get("reload", 0.0))
    return per / cycle


def vs_armour3(w, types, pens):
    if w.get("targets", "Ground") == "Air":
        return 0.0
    return sustained(w) * types.get(w.get("damageType", "Kinetic"), 1.0) * pen_step(pens, int(w.get("pen", 0)) - 3)


def boss_dps(g, b, types, pens):
    """(what weaponDamage scales, what counts at its own numbers, what is left out) against armour 3, with the lines."""
    scaled = fixed = 0.0
    lines = []
    for wid in mounts_of(b):
        if not wid or wid not in g.raw_weapons:
            continue
        w = g.weapon(wid)
        v = vs_armour3(w, types, pens)
        if v <= 0:
            continue
        if w.get("melee") and w.get("laid"):
            lines.append(f"{wid} {v:.0f} (the crusher: left out)")
            continue
        if w.get("laid"):
            fixed += v
            lines.append(f"{wid} {v:.0f} (laid)")
        else:
            scaled += v
            lines.append(f"{wid} {v:.0f}")
    cruise = b.get("cruise")
    if cruise and b.get("naval") is not None:
        w = g.weapon(cruise["weapon"]) if cruise.get("weapon") in g.raw_weapons else {}
        dmg = cruise.get("damage", 520)
        every = cruise.get("every", 48)
        v = dmg / every * types.get("HighExplosive", 1) * pen_step(pens, int(w.get("pen", 3)) - 3)
        fixed += v
        lines.append(f"cruise {v:.0f}")
    return scaled, fixed, lines


# ----------------------------------------------------------------------------------------------------------------
# Editing helpers


def _vehicle_entry(doc, vid):
    return doc.entry("vehicles", vid)


def _own_secondary(e: Entry):
    raw = e.raw("secondary")
    return loads(raw) if raw else []


def set_nested(doc, vid, path, value):
    """Sets vehicles[vid].a.b.c = value (each level an object on the entry's own text)."""
    def fn(e: Entry):
        stack = [e]
        for key in path[:-1]:
            stack.append(stack[-1].sub(key))
        leaf = stack[-1]
        first = next(iter(leaf._keys()))[0]
        leaf.set(path[-1], value, after=first)
        for i in range(len(path) - 2, -1, -1):
            stack[i].set_raw(path[i], stack[i + 1].text)
    return doc.edit("vehicles", vid, fn)


def add_mounts(wr, vid, weapon, want, slot, aim="Free", parts=None):
    """Makes the boss's own "secondary" hold <want> mounts of <weapon> (added at the end); the added mounts go on
    <parts> in turn (their "mounts" lists), so a variant that leaves those parts off leaves the guns off too.
    Returns the mounts added."""
    doc = wr.doc
    e = _vehicle_entry(doc, vid)
    sec = _own_secondary(e)
    have = [i for i, m in enumerate(sec) if m.get("weapon") == weapon and m.get("slot") == slot]
    added = []
    for k in range(len(have), want):
        _guard_library_refs(doc, vid)
        _append_mount(doc, vid, {"weapon": weapon, "slot": slot, "aim": aim})
        added.append(k)
    # Which of those mounts are C1's, by order (the <want - base> last of them); the base count is what the boss had.
    e = _vehicle_entry(doc, vid)
    sec = _own_secondary(e)
    have = [i for i, m in enumerate(sec) if m.get("weapon") == weapon and m.get("slot") == slot]
    if parts:
        mine = have[-len(parts):]
        for part_id, idx in zip(parts, mine):
            _put_on_part(doc, vid, part_id, idx + 1)
    wr.game.refresh()
    return added


def _append_mount(doc, vid, mount):
    def fn(e: Entry):
        raw = e.raw("secondary")
        piece = fmt(mount)
        if raw is None:
            e.set_raw("secondary", f"[ {piece} ]", after="weapon")
        elif raw.strip() == "[]":
            e.set_raw("secondary", f"[ {piece} ]")
        else:
            close_at = raw.rindex("]")
            e.set_raw("secondary", raw[:close_at].rstrip() + f", {piece} " + raw[close_at:])
    doc.edit("vehicles", vid, fn)


def _guard_library_refs(doc, vid):
    """A mount added to the boss's own list moves its library parts' guns one on: no index written by hand may point
    at one of those (a crash gun, a woken mount, a part's list), or it would point at another gun after."""
    v = loads(doc.entry("vehicles", vid).text)
    own = len(v.get("secondary") or [])
    refs = []
    for p in v.get("parts") or []:
        refs += list(p.get("mounts", []) or []) + list(p.get("affects", []) or [])
    refs += (((v.get("tiers") or {}).get("crash") or {}).get("guns") or []) + ((v.get("wake") or {}).get("mounts") or [])
    bad = [m for m in refs if m > own]
    if bad:
        raise SystemExit(f"{vid}: mounts {bad} written by hand point past its own list ({own}): place the new mount by hand")


def _put_on_part(doc, vid, part_id, mount_index):
    def fn(e: Entry):
        raw = e.raw("parts")
        items = X._array_items(raw)
        for s, t in items:
            piece = Entry(raw[s:t])
            if piece.get("id") != part_id:
                continue
            ms = piece.get("mounts")
            if ms is not None and mount_index in ms:
                return
            if piece.has("use") and ms is None and "weapon" in (doc.data().get("bossParts", {}).get(piece.get("use"), {})):
                raise ValueError(f"{vid}.{part_id}: a library part with its own gun")
            piece.set("mounts", (ms or []) + [mount_index], after="id")
            e.set_raw("parts", raw[:s] + piece.text + raw[t:])
            return
        raise KeyError(f"{vid}: no part {part_id}")
    doc.edit("vehicles", vid, fn)


def shift_library_refs(before_n, after_n):
    """Mounts after the boss's own secondary (library parts' guns) move by the number added: never referenced by hand
    (check() fails loudly if one is)."""
    return after_n - before_n


def remove_entry(doc, section, id_):
    """Takes an entry out of a top-level array, with its own comment lines above it and its comma."""
    for i, s, e in doc._entries(section):
        if i != id_:
            continue
        t = doc.text
        line_start = t.rindex("\n", 0, s) + 1
        # The comment lines directly above it are its own.
        start = line_start
        while True:
            prev = t.rindex("\n", 0, start - 1) + 1 if start > 0 else 0
            line = t[prev:start]
            if line.strip().startswith("//"):
                start = prev
            else:
                break
        end = e
        j = _skip(t, end)
        if t[j] == ",":
            end = j + 1
        eol = t.find("\n", end)
        rest = t[end:eol]
        if rest.strip() == "":
            end = eol + 1
        doc.text = t[:start] + t[end:]
        _fix_trailing_comma(doc, section)
        return True
    return False


def _fix_trailing_comma(doc, section):
    s, e = doc._section(section)
    t = doc.text
    body = t[s:e + 1]
    fixed = re.sub(r",(\s*(//[^\n]*\n\s*)*)\]$", r"\1]", body)
    if fixed != body:
        doc.text = t[:s] + fixed + t[e + 1:]


def replace_entry(doc, section, id_, entry: dict, comment: str):
    """Writes an entry on its own line in place of <id_> (a new id may replace an old one), its comment above it (the
    old entry's own comment replaced; a shared header, "Prompt 20 H-J", is kept above it)."""
    text = fmt(entry)
    for i, s, e in doc._entries(section):
        if i != id_:
            continue
        t = doc.text
        line_start = t.rindex("\n", 0, s) + 1
        indent = t[line_start:s]
        start = line_start
        while True:
            prev = t.rindex("\n", 0, start - 1) + 1
            line = t[prev:start].strip()
            if line.startswith("//") and not line.startswith("// Prompt 20 H-J") and not line.startswith("// Prompt 18"):
                start = prev
            else:
                break
        new = f"{indent}// {comment}\n{indent}{text}"
        old = t[start:e]
        if old == new:
            return False
        doc.text = t[:start] + new + t[e:]
        return True
    raise KeyError(id_)


def attack_entry(doc, id_):
    e = doc.entry("bigAttacks", id_)
    return None if e is None else loads(e.text)


# ----------------------------------------------------------------------------------------------------------------
# C1: health


def round50(x):
    return int(round(x / 50.0)) * 50


def health(wr, sheet_rows, report, step):
    g = wr.game
    d = g.data
    tough = d["toughness"]["bosses"]
    mini_share = d["bossRanks"]["mini"].get("hp", 1.0)
    built = expand(d)
    for vid, r in sheet_rows.items():
        if vid not in g.vehicles_raw:
            report.add(step, SHEET, vid, "Máu", "skipped", "no such boss id in balance.json")
            continue
        want = X.num(r["Máu đề xuất (gốc)"])
        share = mini_share if built[vid]["rank"] == "mini" else 1.0
        hp = round50(want / (tough * share))
        cur = g.vehicles_raw[vid].get("hp")
        shown = cur * tough * share
        if X.close(cur, hp):
            report.add(step, SHEET, vid, "Máu", "already", f"hp {hp} ({want:.0f} shown)")
            continue
        wr.doc.edit("vehicles", vid, lambda e: e.set("hp", hp))
        g.refresh()
        report.add(step, SHEET, vid, "Máu", "applied",
                   f"hp {cur:g} -> {hp} (shown {shown:.0f} -> {hp * tough * share:.0f}: the sheet's {want:.0f} over toughness {tough:g}"
                   + (f" x the mini share {share:g}" if share != 1 else "") + ")")


# ----------------------------------------------------------------------------------------------------------------
# C1: weapons ("Vũ khí thêm / đổi")

# vid -> [(weapon, count wanted among the boss's own "secondary", slot, parts carrying the added mounts)], and a note
# of what the row asks. Existing weapons by id (the calibre and role the row names); "Giữ" rows and rows the data
# already answers are listed with the reason.
WEAPONS = {
    "armored_train": ([("boss_flak", 2, "mg", None)], "one more flak car: a second twin 35 mm on the train (no car of its own on the model yet)"),
    "ixion": ([("boss_hmg", 2, "mg", None)], "two NSV 12.7 mm on the hull"),
    "caspian": ([("zu23", 2, "mg", None)], "two ZU-23-2 twin 23 mm; the anti-ship missile of each pass is its cruise missile (below)"),
    "mega_gunship": ([("boss_hmg", 2, "mg", None)], "a door gun each side: NSV 12.7 mm"),
    "daedalus": ([("gun_57mm", 2, "gun", None)], "two 57 mm (the 2A91, the AU-220M's automatic gun) under the belly; its two point-defence lasers are in already"),
    "behemoth": ([("kornet_twin", 1, "missile", ["gun_120"])], "a twin Kornet launcher behind the main turret, on the 120 mm turret's part (the Mk.0 and Mk.II keep their own loadouts)"),
    "mobile_fortress": ([("twin_30_flak", 1, "mg", ["flak_r"])], "a twin 30 mm anti-drone turret (the 2A38), beside the right flak (Fenrir keeps its own)"),
    "command_airship": ([("twin_30_bmpt", 2, "gun", ["bomb_bay", "bomb_bay"])], "two twin 30 mm (2A42) under the belly, by the bomb bay (Argus keeps its own)"),
    "moloch": ([("zu23", 2, "mg", None)], "two ZU-23-2 on the roof"),
    "fortress_bastion": ([("boss_hmg", 2, "mg", ["turret_rl", "turret_rr"])], "two NSV 12.7 mm turrets on the sides, with the rear turrets (the Mk.0 keeps its own)"),
    "kronos": ([("gun_57mm", 2, "gun", None)], "two automatic 57 mm turrets (the 2A91)"),
    "leviathan": ([("sam_post", 1, "missile", ["radar"])], "a medium-range SAM (the 9M317 Buk), with the radar that guides it (Scylla keeps its own)"),
    "drone_mothership": ([("mothership_drones", 2, "missile", ["uav_bay"])], "a third Lancet bay, in the UAV bay (Locust keeps its own)"),
}
ALREADY = {
    "nuke_train": "its 152 mm gun car is in already (gun_car_152, prompt 20 F.3)",
    "landing_hovercraft": "its AK-630s are the gunboat's (hover_ciws, and ciws_aa inherits it): A2 set them",
    "bastion_mk0": "the 240 mm mortar (an ordinary weapon now its big attack is gone) and the two Bofors are its mounts",
    "behemoth_tempest": "the railgun stays its main gun (its big attack is gone)",
    "behemoth_inferno": "the flamethrowers stay its main weapons",
    "fenrir": "its two rocket boxes and its flak stay",
    "argus": "it spots for the artillery (its radar's aura) and keeps its guns",
    "supreme_command": "no strong weapon: its command aura makes its side hit harder (its antenna); two NSV",
}


def weapons(wr, sheet_rows, report, step):
    g = wr.game
    for vid, r in sheet_rows.items():
        words = str(r.get("Vũ khí thêm / đổi") or "")
        if vid in WEAPONS:
            plan, note = WEAPONS[vid]
            done = []
            for weapon, want, slot, parts in plan:
                if weapon not in g.raw_weapons:
                    raise KeyError(weapon)
                added = add_mounts(wr, vid, weapon, want, slot, parts=parts)
                if added:
                    done.append(f"+{len(added)} {weapon}" + (f" on {', '.join(parts)}" if parts else " on the hull"))
            report.add(step, SHEET, vid, "Vũ khí", "applied" if done else "already", (", ".join(done) + ": " if done else "") + note)
        elif vid in ALREADY:
            report.add(step, SHEET, vid, "Vũ khí", "already", ALREADY[vid])
        elif words.strip().startswith("Giữ") and vid not in ("landing_hovercraft",):
            report.add(step, SHEET, vid, "Vũ khí", "already", "Giữ: kept")
    icarus(wr, sheet_rows, report, step)
    scylla(wr, sheet_rows, report, step)
    typhon_caspian(wr, sheet_rows, report, step)


def icarus(wr, sheet_rows, report, step):
    """Icarus: the two 120 mm and two 35 mm flak go, two coilguns in their place (firing from the start); the phase-3
    wreck's turrets are four ordinary guns (two Bofors on the hull, the two crash turrets). Icarus Mk.0 keeps one of the
    two point-defence lasers instead of the satellite uplink (its rods are gone with its big attack)."""
    g = wr.game
    doc = wr.doc
    vid = "silver_bug"
    want = [{"weapon": "coilgun", "slot": "gun", "aim": "Free"}, {"weapon": "coilgun", "slot": "gun", "aim": "Free"},
            {"weapon": "autocannon_40", "slot": "gun", "aim": "Free"}, {"weapon": "autocannon_40", "slot": "gun", "aim": "Free"}]
    e = _vehicle_entry(doc, vid)
    done = []
    if _own_secondary(e) != want:
        doc.edit("vehicles", vid, lambda en: en.set_raw("secondary", "[ " + ", ".join(fmt(m) for m in want) + " ]"))
        done.append("2 coilguns in place of the 2 Rh-120 and the 2 Oerlikon 35 mm")
    guns = [3, 4, 5, 6]
    g.refresh()
    cur = (loads(_vehicle_entry(doc, vid).text).get("tiers") or {}).get("crash", {}).get("guns")
    if cur != guns:
        set_nested(doc, vid, ["tiers", "crash", "guns"], guns)
        done.append("the wreck's four ordinary turrets (two Bofors, the two crash turrets) wake in phase 3; the coilguns fire from the start")
    g.refresh()
    report.add(step, SHEET, vid, "Vũ khí", "applied" if done else "already",
               "; ".join(done) or "coilguns x2 (from the start), four ordinary turrets on the wreck (phase 3); the two point-defence lasers were in")
    # Icarus Mk.0: one point-defence laser.
    vid = "icarus_mk0"
    e = _vehicle_entry(doc, vid)
    rules = e.get("variant")
    done = []
    if "uplink" in rules.get("keep", []):
        rules["keep"] = [("pd_laser_l" if k == "uplink" else k) for k in rules["keep"]]
        tune = rules.get("tune", {})
        if "uplink" in tune:
            tune["pd_laser_l"] = tune.pop("uplink")
        doc.edit("vehicles", vid, lambda en: en.set("variant", rules))
        done.append("a point-defence laser (Icarus's left one) in place of the satellite uplink")
    # Its laser is its active protection: Icarus's, over the Mk.0's own size (a variant's resize leaves the APS as it is).
    parent = g.vehicles_raw["silver_bug"]["aps"]
    size = (_vehicle_entry(doc, vid).get("variant") or {}).get("size", 0.7)
    aps = dict(parent)
    aps["radius"] = round(parent["radius"] * size, 1)
    if _vehicle_entry(doc, vid).get("aps") != aps:
        doc.edit("vehicles", vid, lambda en: en.set("aps", aps, after="secondary"))
        done.append(f"active protection (the laser's): Icarus's at its size, {aps['radius']:g} m")
    g.refresh()
    report.add(step, SHEET, vid, "Vũ khí", "applied" if done else "already", "; ".join(done) or "one point-defence laser")


def _parse_ak130(words):
    m = re.search(r"AK-130[^(]*\((\d+)/phát\s*·\s*([\d,]+)\s*phát/s\s*loạt\s*(\d+)\s*·\s*nổ lan\s*([\d,]+)\s*m\s*·\s*tầm\s*(\d+)\)", words)
    dmg, rate, n, splash, rng = float(m.group(1)), X.num(m.group(2)), int(m.group(3)), X.num(m.group(4)), float(m.group(5))
    m2 = re.search(r"tên lửa chống hạm\s*\(1\s*×\s*(\d+)\s*mỗi\s*(\d+)\s*s\)", words)
    return dmg, rate, n, splash, rng, float(m2.group(1)), float(m2.group(2))


def scylla(wr, sheet_rows, report, step):
    """Scylla: the 460 mm goes for a twin AK-130 (the row's numbers, a burst on A2's rule: the sheet's cycle n / rate +
    rest, no rest given), which the combat system fires (its salvo mechanism, the 460's, goes); its anti-ship missile
    is its cruise missile at the row's numbers."""
    g = wr.game
    doc = wr.doc
    words = str(sheet_rows["scylla"]["Vũ khí thêm / đổi"])
    dmg, rate, n, splash, rng, ship_dmg, ship_every = _parse_ak130(words)
    gap = round(1.0 / rate, 4)
    line = {"id": "naval_130_twin", "inherits": "naval_100", "real": "AK-130 130 mm (twin)", "size": 130, "pen": 3,
            "damage": dmg, "burst": n, "burstInterval": gap, "cooldown": gap, "range": rng, "splash": splash, "impactTier": "Large"}
    done = []
    if "naval_130_twin" not in g.raw_weapons:
        doc.insert_after("weapons", "naval_100", fmt(line))
        g.refresh()
        done.append(f"naval_130_twin: {dmg:.0f} a round, bursts of {n} at {rate:g} a second, {splash:g} m blast, {rng:.0f} m")
    else:
        for k, v in line.items():
            if k in ("id", "inherits"):
                continue
            if wr.weapon_field("naval_130_twin", k, v):
                done.append(f"naval_130_twin {k} {fmt(v)}")
    e = _vehicle_entry(doc, "scylla")
    if e.get("weapon") != "naval_130_twin":
        doc.edit("vehicles", "scylla", lambda en: en.set("weapon", "naval_130_twin", after="radioSpawn"))
        done.append("its main gun the AK-130 (the 460 mm gone)")
    e = _vehicle_entry(doc, "scylla")
    if e.raw("salvo") != "null":
        doc.edit("vehicles", "scylla", lambda en: en.set_raw("salvo", "null"))
        done.append("no main-battery salvo (the 460's)")
    cruise = _vehicle_entry(doc, "scylla").get("cruise") or {}
    for k, v in (("every", ship_every), ("damage", ship_dmg)):
        if not X.close(cruise.get(k), v):
            set_nested(doc, "scylla", ["cruise", k], v)
            done.append(f"its anti-ship missile (cruise) {k} {fmt(v)}")
    g.refresh()
    report.add(step, SHEET, "scylla", "Vũ khí", "applied" if done else "already", "; ".join(done) or "AK-130 twin, anti-ship missiles, CIWS")


def typhon_caspian(wr, sheet_rows, report, step):
    """Typhon's short-range cruise missile fired as an ordinary weapon (surfaced: a submarine fires nothing under water)
    is its cruise missile at the row's numbers; Caspian's one anti-ship missile a pass is a cruise missile of its own,
    one a pass (its passes: in and out), at its old volley's missile (500, the launcher carrying it)."""
    g = wr.game
    doc = wr.doc
    words = str(sheet_rows["typhon"]["Vũ khí thêm / đổi"])
    m = re.search(r"1 quả\s*×\s*(\d+)\s*mỗi\s*(\d+)\s*s", words)
    dmg, every = float(m.group(1)), float(m.group(2))
    done = []
    cruise = _vehicle_entry(doc, "typhon").get("cruise") or {}
    for k, v in (("every", every), ("damage", dmg)):
        if not X.close(cruise.get(k), v):
            set_nested(doc, "typhon", ["cruise", k], v)
            done.append(f"cruise {k} {fmt(v)}")
    report.add(step, SHEET, "typhon", "Vũ khí", "applied" if done else "already",
               ("; ".join(done) + ": " if done else "") + f"its cruise missile, 1 x {dmg:.0f} every {every:.0f} s, fired only surfaced")
    # Caspian.
    e = _vehicle_entry(doc, "caspian")
    naval = e.get("naval") or {}
    pass_s = naval.get("passIn", 6) + naval.get("passOut", 20)
    old = attack_entry(doc, "caspian_antiship_volley")
    per = old["strikes"][0]["damage"] if old else (e.get("cruise") or {}).get("damage", 500)
    want = {"every": pass_s, "first": naval.get("passIn", 6), "phase": 0, "warn": 4, "damage": per,
            "radius": KALIBR_BLAST, "final": 0, "weapon": "leviathan_cruise", "warning": "leviathan_cruise_mark"}
    done = []
    if e.get("cruise") is None:
        doc.edit("vehicles", "caspian", lambda en: en.set("cruise", want, after="naval"))
        done.append(f"a cruise missile a pass: 1 x {per:.0f} every {pass_s:g} s")
    parts_raw = _vehicle_entry(doc, "caspian").raw("parts")
    for s, t in X._array_items(parts_raw):
        piece = Entry(parts_raw[s:t])
        if piece.get("id") == "launcher" and not piece.has("stops"):
            piece.set("stops", ["cruise"], after="radius")
            doc.edit("vehicles", "caspian", lambda en, p=parts_raw[:s] + piece.text + parts_raw[t:]: en.set_raw("parts", p))
            done.append("its launcher carries it (broken: no more)")
            break
    g.refresh()
    report.add(step, SHEET, "caspian", "tên lửa chống hạm", "applied" if done else "already", "; ".join(done) or "a cruise missile a pass")


# The Kalibr (leviathan_cruise, 500 kg): the round A5 left to C1 (a boss system's own); A5's rule, 10 m x (500 / 500)^(1/3).
KALIBR_BLAST = 10.0


def kalibr(wr, report, step):
    """The boss system's cruise missile takes A5's rule for its blast (the sheet gives no number): the weapon, every
    cruise missile that fires it, and its warning ring (the blast plus the 2 m it may fall off the mark)."""
    g = wr.game
    doc = wr.doc
    done = []
    if wr.weapon_field("leviathan_cruise", "splash", KALIBR_BLAST):
        done.append(f"leviathan_cruise {KALIBR_BLAST:g} m")
    for vid, v in g.vehicles_raw.items():
        c = v.get("cruise")
        if c and c.get("weapon", "leviathan_cruise") == "leviathan_cruise" and "radius" in c and not X.close(c["radius"], KALIBR_BLAST):
            set_nested(doc, vid, ["cruise", "radius"], KALIBR_BLAST)
            done.append(f"{vid}'s cruise {c['radius']:g} -> {KALIBR_BLAST:g} m")
    mark = next(s for s in g.data["supports"] if s["id"] == "leviathan_cruise_mark")
    for k, v in (("blast", KALIBR_BLAST), ("radius", KALIBR_BLAST + 2)):
        if not X.close(mark.get(k), v):
            doc.edit("supports", "leviathan_cruise_mark", lambda e, k=k, v=v: e.set(k, v))
            done.append(f"leviathan_cruise_mark {k} {v:g}")
    g.refresh()
    report.add(step, "Tổng quan", "leviathan_cruise", "blast", "applied" if done else "already",
               ("; ".join(done) + " " if done else "") + "(A5's rule for a 500 kg round: the round A5 left to C1)")


# ----------------------------------------------------------------------------------------------------------------
# C1: damage a second


def dps(wr, wb, sheet_rows, report, step, only_changed=False):
    g = wr.game
    types, pens = factors(wb)
    built = expand(g.data)
    for vid, r in sheet_rows.items():
        if vid not in built:
            continue
        target = float(r["DPS thường mục tiêu (vs giáp 3)"])
        scaled, fixed, lines = boss_dps(g, built[vid], types, pens)
        if scaled <= 0:
            report.add(step, SHEET, vid, "DPS", "skipped", "no ordinary weapon against the ground")
            continue
        k = round(max(0.1, (target - fixed)) / scaled, 3)
        cur = g.vehicles_raw[vid].get("weaponDamage", 1.0)
        detail = f"{scaled + fixed:.0f} -> {scaled * k + fixed:.0f} against armour 3 (target {target:.0f}; {', '.join(lines)})"
        if X.close(cur, k, 1e-3):
            if not only_changed:
                report.add(step, SHEET, vid, "DPS", "already", f"weaponDamage {k:g}: {detail}")
            continue
        wr.doc.edit("vehicles", vid, lambda e: e.set("weaponDamage", k, after="hp"))
        g.refresh()
        report.add(step, SHEET, vid, "DPS", "applied", f"weaponDamage {cur:g} -> {k:g}: {detail}")


# ----------------------------------------------------------------------------------------------------------------
# C1: super weapons


def _n(text, pattern, group=1):
    m = re.search(pattern, text)
    return X.num(m.group(group)) if m else None


def parse_super(text):
    """The row's numbers: rounds x damage, blast, cycle, warning, and the shape's own (strip, arc, flight, phase 3)."""
    t = str(text)
    p = {}
    m = re.search(r"(\d+)\s*(?:khoang|quả|phát)?\s*×\s*(\d{1,3}(?:\.\d{3})+|\d+)", t)
    if m:
        p["count"], p["damage"] = int(m.group(1)), X.num(m.group(2))
    p["radius"] = _n(t, r"nổ lan\s*([\d,]+)\s*m")
    p["cooldown"] = _n(t, r"mỗi\s*(\d+)\s*s")
    p["warn"] = _n(t, r"cảnh báo[^·0-9]*?([\d,]+)\s*s") or _n(t, r"trước\s*([\d,]+)\s*s")
    m = re.search(r"dải\s*(\d+)\s*×\s*(\d+)\s*m", t)
    if m:
        p["length"], p["width"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"cung\s*(\d+)°\s*×\s*(\d+)\s*m,\s*(\d{1,3}(?:\.\d{3})+|\d+)", t)
    if m:
        p["arc"], p["radius"], p["damage"] = float(m.group(1)), float(m.group(2)), X.num(m.group(3))
    p["flight"] = _n(t, r"(?:đồng hồ bay|bay chậm)\s*([\d,]+)\s*s")
    m = re.search(r"pha\s*(\d+):\s*(\d+)\s*thanh,\s*mỗi\s*(\d+)\s*s", t)
    if m:
        p["late"] = {"phase": int(m.group(1)) - 1, "cooldown": float(m.group(3)), "count": int(m.group(2))}
    p["drop"] = _n(t, r"thả\s*(\d+)\s*xe")
    p["rings"] = _n(t, r"vạch\s*(\d+)\s*vòng tròn")
    return {k: v for k, v in p.items() if v is not None}


def _num(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


# Each main boss's super weapon: its big attack's id (a new id where the attack is a new one), what the row's numbers
# set, and how it is stopped. A glide bomb that can be shot down flies as a missile (prompt 18's shape) with the
# missiles' health (Typhon's and the cruise volleys' 250).
SUPER = {
    "behemoth": ("behemoth_barrage", "behemoth_barrage"),
    "mobile_fortress": ("fortress_rocket_rain", "fortress_203_barrage"),
    "drone_mothership": ("carrier_heavy_bomb", "carrier_heavy_bomb"),
    "nuke_train": ("doomsday_missile", "doomsday_missile"),
    "silver_bug": ("bug_rod_rain", "bug_rod_rain"),
    "fortress_bastion": ("bastion_mortar_walk", "bastion_420_shell"),
    "command_airship": ("airship_carpet", "airship_carpet"),
    "leviathan": ("leviathan_volley", "leviathan_volley"),
    "moloch": ("moloch_factory_dump", "moloch_factory_dump"),
    "daedalus": ("daedalus_mass_drop", "daedalus_mass_drop"),
    "kronos": ("kronos_bucket_sweep", "kronos_bucket_sweep"),
    "typhon": ("typhon_underwater_launch", "typhon_underwater_launch"),
}
MISSILE_HP = 250


def super_entry(vid, old, p):
    """The super weapon's entry from the old one and the row's numbers."""
    a = copy.deepcopy(old)
    s = a["strikes"]
    for k in ("cooldown", "warn"):
        if k in p:
            a[k] = _num(p[k])
    if vid == "mobile_fortress":
        a = {"id": "fortress_203_barrage", "icon": "artillery", "warn": _num(p["warn"]), "cooldown": _num(p["cooldown"]), "aim": "group",
             "reach": old.get("reach", 70), "target": "mixed",
             "strikes": [{"shape": "circle", "parts": ["howitzer", "howitzer_2"], "perPart": p["count"] // 2, "damage": _num(p["damage"]),
                          "type": "HighExplosive", "pen": 4, "radius": _num(p["radius"]), "area": 14, "duration": 2.4, "weapon": "boss_howitzer"}]}
        return a
    if vid == "fortress_bastion":
        a = {"id": "bastion_420_shell", "icon": "mortar", "warn": _num(p["warn"]), "cooldown": _num(p["cooldown"]), "aim": "group",
             "reach": old.get("reach", 85), "target": "defences",
             "strikes": [{"shape": "circle", "parts": ["mortar"], "count": p["count"], "damage": _num(p["damage"]), "type": "HighExplosive",
                          "pen": 4, "structure": 2, "radius": _num(p["radius"]), "weapon": "boss_mortar"}]}
        return a
    if vid == "drone_mothership":
        st = s[0]
        st.update({"shape": "missile", "count": p["count"], "damage": _num(p["damage"]), "radius": _num(p["radius"]),
                   "hp": MISSILE_HP, "flight": _num(p["flight"]), "targets": 1})
        return a
    if vid == "leviathan":
        st = s[0]
        st["shape"] = "strip"
        for k in ("salvo", "area"):
            st.pop(k, None)
        st.update({"radius": _num(p["radius"]), "length": _num(p["length"]), "width": _num(p["width"]), "axis": "toward"})
        st["perPart"] = p["count"] // len(st["parts"])
        return a
    if vid == "moloch":
        drop = next(x for x in s if x["shape"] == "drop")
        drop["perPart"] = int(p["drop"]) // len(drop["parts"])
        circle = next(x for x in s if x["shape"] == "circle")
        circle.update({"count": p["count"], "damage": _num(p["damage"]), "radius": _num(p["radius"])})
        return a
    if vid == "kronos":
        s[0].update({"width": _num(p["arc"]), "radius": _num(p["radius"]), "damage": _num(p["damage"])})
        return a
    st = s[0]
    st.update({"count": p["count"], "damage": _num(p["damage"]), "radius": _num(p["radius"])})
    if "length" in p:
        st.update({"length": _num(p["length"]), "width": _num(p["width"])})
    if "flight" in p:
        st["flight"] = _num(p["flight"])
    if "late" in p:
        a["late"] = p["late"]
    if p.get("rings") == p.get("count"):
        st["rings"] = True  # "vạch 6 vòng tròn": each round's own ring drawn at the warning
    return a


def summary(vid, a, name):
    st = a["strikes"]
    bits = []
    for x in st:
        if x["shape"] == "drop":
            bits.append(f"{x['perPart'] * len(x['parts'])} vehicles landed")
        elif x["shape"] == "arc":
            bits.append(f"a {x['width']:g} deg x {x['radius']:g} m sweep of {x['damage']:g}")
        else:
            n = x.get("perPart", 0) * len(x.get("parts", [])) or x.get("count", 1)
            bits.append(f"{n} x {x['damage']:g}, {x['radius']:g} m blast" + (f" along a strip {x['length']:g} x {x['width']:g} m" if x["shape"] == "strip" else "")
                        + (f", {x['flight']:g} s in flight, shot down at {x['hp']:g}" if x["shape"] == "missile" and "hp" in x else ""))
    late = a.get("late")
    return (f"Prompt 25 C1: {name}'s super weapon, {' + '.join(bits)}, every {a['cooldown']:g} s, {a['warn']:g} s warning"
            + (f" (phase {late['phase'] + 1}: {late['count']} every {late['cooldown']:g} s)" if late else "") + " (sheet Boss đề xuất).")


def supers(wr, sheet_rows, report, step):
    g = wr.game
    doc = wr.doc
    for vid, (old_id, new_id) in SUPER.items():
        r = sheet_rows[vid]
        p = parse_super(r["Siêu vũ khí đề xuất"])
        base = attack_entry(doc, new_id) or attack_entry(doc, old_id)
        want = super_entry(vid, base, p)
        want["id"] = new_id
        name = str(r["Tên"]).split(" · ")[0]
        comment = summary(vid, want, name)
        present = doc.entry("bigAttacks", new_id) is not None
        changed = replace_entry(doc, "bigAttacks", new_id if present else old_id, want, comment)
        if g.vehicles_raw[vid].get("bigAttack") != new_id:
            doc.edit("vehicles", vid, lambda e: e.set("bigAttack", new_id))
            changed = True
        g.refresh()
        report.add(step, SHEET, vid, "Siêu vũ khí", "applied" if changed else "already",
                   (f"{old_id} -> {new_id}: " if old_id != new_id else f"{new_id}: ") + comment.split("super weapon, ", 1)[1])


def minis(wr, sheet_rows, report, step):
    """A mini boss keeps its ordinary weapons only: its big attack (and Morrigan's duel's) is taken away."""
    g = wr.game
    doc = wr.doc
    built = expand(g.data)
    for vid in sheet_rows:
        if built.get(vid, {}).get("rank") != "mini":
            continue
        raw = g.vehicles_raw[vid]
        done = []
        if "bigAttack" in raw:
            done.append(f"{raw['bigAttack']} taken away")
            doc.edit("vehicles", vid, lambda e: e.remove("bigAttack"))
        duel = raw.get("duel") or {}
        if "bigAttack" in duel:
            done.append(f"its duel's {duel['bigAttack']} too")
            def fn(e):
                d = e.sub("duel")
                d.remove("bigAttack")
                e.set_raw("duel", d.text)
            doc.edit("vehicles", vid, fn)
        g.refresh()
        report.add(step, SHEET, vid, "Siêu vũ khí", "applied" if done else "already",
                   ("; ".join(done) + ": " if done else "") + "a mini boss has no super weapon (only its ordinary weapons)")
    # Every big attack no boss and no duel names any more leaves the data.
    named = set()
    for v in g.data["vehicles"]:
        if v.get("bigAttack"):
            named.add(v["bigAttack"])
        if (v.get("duel") or {}).get("bigAttack"):
            named.add(v["duel"]["bigAttack"])
    attacks = {a["id"]: a for a in g.data["bigAttacks"]}
    needed = set(named)
    for a in list(named):
        while a in attacks and "from" in attacks[a]:
            a = attacks[a]["from"]
            needed.add(a)
    gone = [a for a in attacks if a not in needed]
    for a in gone:
        remove_entry(doc, "bigAttacks", a)
    g.refresh()
    if gone:
        report.add(step, SHEET, "bigAttacks", "entries", "applied", f"{len(gone)} big attacks no boss names any more removed: {', '.join(gone)}")


def header(wr):
    """The big-attack section's header says prompt 25's rule once."""
    doc = wr.doc
    line = ("  // Prompt 25 C1 (DECISIONS 25C): only the twelve main bosses have a big attack, their super weapon, with the numbers of\n"
            "  // the balance sheet's \"Boss đề xuất\" (written by Tools/balance/import_xlsx.py); a mini boss has its ordinary weapons only.\n"
            "  // \"late\": from a boss phase on (0 up), another cooldown and its first strike's rounds (Icarus on the ground).\n")
    old = "// Prompt 20 H-J: the new bosses' big attacks; a variant's is its main boss's scaled down (\"from\": its strikes merged by index)."
    doc.text = doc.text.replace(old, "// Prompt 20 H-J: the new bosses' big attacks.")
    if "Prompt 25 C1 (DECISIONS 25C): only the twelve" in doc.text:
        return
    at = doc.text.index('  "bigAttacks": [')
    doc.text = doc.text[:at] + line + doc.text[at:]


# ----------------------------------------------------------------------------------------------------------------
# C1: the rows of the other sheets that earlier steps left to C1


def earlier_rows(wb, sheet_rows, report, step):
    _, trows = X.sheet(wb, "Thay đổi chi tiết")
    for r in trows:
        vid, cat = r[0], str(r[2])
        # The rows A1 left to C1 (import_xlsx.a1: a boss's health and weapons; its armour and references were A1's).
        if vid in sheet_rows and not cat.startswith(("Tên", "Kích thước", "Dữ liệu vũ khí", "Giáp", "Tham khảo"))                 and (vid, cat) not in X.A1_WEAPONS:
            note = "by its Boss đề xuất row (exact numbers)"
            if "giáp" in cat.lower():
                note += "; the armour by its own Giáp row (A1 Thấp: a mini boss's front 4 at most)"
            report.add(step, "Thay đổi chi tiết", vid, cat, "applied", note)
    _, krows = X.sheet(wb, "Kiểm tra từng mục")
    for r in krows:
        vid, item, result, prop = r[0], str(r[2]), r[4], str(r[5] or "")
        if vid in ("daedalus", "bastion_mk0", "scylla") and item == "Máu" and result == "Đổi":
            want = X.num(sheet_rows[vid]["Máu đề xuất (gốc)"])
            note = f"Boss đề xuất's {want:.0f}"
            m = re.match(r"~?([\d.]+)", prop)
            if m and abs(X.num(m.group(1)) - want) > 1:
                note += f" (this row's {prop.split('·')[0].strip()}; Boss đề xuất gives the exact number, within the Boss sheet's range)"
            report.add(step, "Kiểm tra từng mục", vid, "Máu", "applied", note)


# ----------------------------------------------------------------------------------------------------------------


def c2(wr, wb, sheet_rows, report, step):
    pass


def run(step, wr, wb, report):
    sheet_rows = rows(wb)
    if step == "C1":
        health(wr, sheet_rows, report, step)
        weapons(wr, sheet_rows, report, step)
        kalibr(wr, report, step)
        supers(wr, sheet_rows, report, step)
        minis(wr, sheet_rows, report, step)
        header(wr)
        dps(wr, wb, sheet_rows, report, step)
        earlier_rows(wb, sheet_rows, report, step)
        problems = check(wr.game.data, expand(wr.game.data))
        if problems:
            raise SystemExit("C1 left the bosses inconsistent:\n  " + "\n  ".join(problems))
        return "C1: bosses (sheet Boss đề xuất): health, weapons, damage a second, super weapons"
    if step == "C2":
        c2(wr, wb, sheet_rows, report, step)
        dps(wr, wb, sheet_rows, report, step, only_changed=True)
        problems = check(wr.game.data, expand(wr.game.data))
        if problems:
            raise SystemExit("C2 left the bosses inconsistent:\n  " + "\n  ".join(problems))
        return "C2: the Gungnir's 80 cm gun and the Kronos's bucket wheel as weapons"
    return None

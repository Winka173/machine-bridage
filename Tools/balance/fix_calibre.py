"""Full fix prompt L2: the calibre and the warhead as separate fields (DECISIONS "Sửa lỗi tổng hợp L2").

    python Tools/balance/fix_calibre.py           # dry run: what each line gets, and the check
    python Tools/balance/fix_calibre.py --write   # save balance.json (a second run changes nothing)

The data's "size" held a gun's calibre in mm, a missile's, bomb's or drone's kg, a laser's kW and a railgun's MJ. Each
weapon line that carries its own "size" now also says what it means, in one of four display fields:
  caliberMm   guns, autocannons, howitzers, mortars, naval guns, grenade launchers, recoilless guns, rockets, the 800 mm gun
  warheadKg   missiles, bombs, drones (a bomb's class weight; a missile's warhead, `full_weapon_audit.WARHEAD` where the
              data's size is the whole missile's mass)
  powerKw     lasers
  energyMj    railguns and coilguns (Gungnir's EMRG: the data's 250, a scaled-up US Navy EMRG)
Flamethrowers and close-in tools (drill, blade, bucket wheel) have none. "size" itself stays: the Sim reads it for the
default penetration, the round's form and the flak's look, so nothing in a battle moves. The card reads only the four
display fields (WeaponInfo / UnitLines), never the digits of an id or a name.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import full_weapon_audit as W  # noqa: E402
import p34_families as F  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

FIELDS = ("caliberMm", "warheadKg", "powerKw", "energyMj")
SPECIAL = {"p26_gungnir_emrg": ("energyMj", 250)}


def wanted(w):
    """(field, value) a resolved line should carry, or (None, None)."""
    if w["id"] in SPECIAL:
        return SPECIAL[w["id"]]
    fam, size = w.get("family"), w.get("size")
    if not size:
        return None, None
    if fam in W.GUN_FAMS or fam == "rocket" or (fam == "special" and size >= 800):
        return "caliberMm", size
    if fam in W.WARHEAD_FAMS:
        return "warheadKg", W.WARHEAD.get(F.real_base(w).lower(), size)
    if fam == "laser":
        return "powerKw", size
    if fam == "railgun":
        return "energyMj", size
    return None, None


def plan(data):
    ws = F.Weapons(data)
    edits = {}
    for raw in data["weapons"]:
        wid = raw["id"]
        w = ws.resolve(wid)
        field, value = wanted(w)
        own = {k: raw[k] for k in FIELDS if k in raw}
        f = {}
        if field and ("size" in raw or wid in SPECIAL or raw.get("family")):
            if raw.get(field) != value:
                f[field] = value
        # an inherited display field of the wrong kind (the parent's) is cleared on the child
        for k in FIELDS:
            if k != field and w.get(k) and k not in own:
                f[k] = 0
        if f:
            edits[wid] = f
    return ws, edits


def check(data):
    """Every resolved weapon line carries the field its family means (and only that one), with the data's value."""
    ws = F.Weapons(data)
    problems = []
    for raw in data["weapons"]:
        w = ws.resolve(raw["id"])
        field, value = wanted(w)
        have = {k: w.get(k) for k in FIELDS if w.get(k)}
        if field and have.get(field) != value:
            problems.append(f"{raw['id']}: {field} {have.get(field)} (wanted {value})")
        extra = [k for k in have if k != field]
        if extra:
            problems.append(f"{raw['id']}: also {extra}")
    return problems


def main():
    doc = Doc(F.PATH)
    data = doc.data()
    changed = 0
    for _pass in range(3):   # a child's inherited field of the wrong kind shows once its parent has one
        ws, edits = plan(data)
        for wid, f in edits.items():
            def fn(e, f=f):
                for k, v in f.items():
                    e.set(k, v, after="size" if e.has("size") else F._after(e))
            if doc.edit("weapons", wid, fn):
                changed += 1
        data = doc.data()
    print(f"{changed} lines changed")
    problems = check(doc.data())
    for p in problems:
        print("CHECK:", p)
    print("check: OK" if not problems else f"check: {len(problems)} problems")
    if "--write" in sys.argv:
        doc.save()
        print("written")


if __name__ == "__main__":
    main()

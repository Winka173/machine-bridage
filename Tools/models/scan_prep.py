"""Fix pass 8 (Docs/prompts/fix_full_vi.txt "Lượt 8"; DECISIONS "Sửa lỗi tổng hợp L8 prep"): the model scan.

    python Tools/models/scan_prep.py                  # (b) static scores -> Docs/models/scan/static_scores.csv
    python Tools/models/scan_prep.py --refs           # Docs/models/reference_dimensions.md from reference_real.json
    python Tools/models/scan_prep.py --old            # (a) pre-prompt-27 GLBs -> <runner>/Builds/scan_old_models/
           [--repo C:/Users/Winka/Projects/MachineBrigade-runner] [--base 07444b1] [--dry-run]
    python Tools/models/scan_prep.py --index          # after the Unity scan: Docs/models/scan/visual_scores.md
           [--scan-dir <runner>/Builds/scan]

(a) --old: the models rebuilt in prompt 27 (git log of the prompt's model commits after --base, the BUILDERS of
    Tools/blender/mb_p27_*.py, the backticked ids of DECISIONS "## 27 wave ..." sections, Docs/models/PROGRESS.md's
    "**done" rows), plus the ones the prompt makes compulsory (sky_gunship, every tower, structure and HQ), kept when
    the file existed at --base and differs at HEAD. Each comes out of git at --base (`git show <base>:<path>`, then
    `git lfs smudge` on the LFS pointer) into <repo>/Builds/scan_old_models/<id>.glb, with old_models.tsv listing why.
    Normal tier only (the scan renders the normal file). Needs the LFS objects (fetched from the remote if missing).
(b) default: every model a vehicle def draws (vehicles, aircraft, ships, bosses, towers and their branch models,
    structures) and the HQs, scored against Docs/models/MODEL_STANDARD.md: LOD0 triangles vs the class budget,
    required parts by class (node names; Part_<role> or the kit's merged-material names, see the standard), Muzzle_* per
    barrel and Mount_* per free-aimed weapon, Mount_Flare (>= 2 when the def has flares), Mount_APS, boss part nodes,
    proportions (width/length, height/length) vs Tools/models/reference_real.json. When Builds/scan/<id>.json exists
    (the Unity scan), its LOD1 triangle share is added. Static grade: Tốt / Cần sửa / Kém (rules in the standard);
    the final grade adds the visual pass on the sheets (Docs/models/scan/README.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'Tools' / 'assets'))
sys.path.insert(0, str(ROOT / 'Tools' / 'balance'))
# MVA W1-B stable runtime names: a semantic tag (Mount_gun_02, Muzzle_mg_L, Mount_gun_aft) counts like a
# legacy '.NNN' suffix (naval models lane B, 06/10: the tagged mounts read as missing before).
from runtime_nodes import TAG as _TAG  # noqa: E402
TAG = '(?:' + _TAG + ')'
import glb_analyze  # noqa: E402
from jsonc_edit import loads as load_jsonc  # noqa: E402

MODELS_REL = 'Assets/MachineBrigade/Resources/Models'
MODELS = ROOT / MODELS_REL
BALANCE = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json'
REFERENCE = HERE / 'reference_real.json'
SCAN_DOCS = ROOT / 'Docs' / 'models' / 'scan'
SCORES = SCAN_DOCS / 'static_scores.csv'
REF_DOC = ROOT / 'Docs' / 'models' / 'reference_dimensions.md'
RUNNER = Path('C:/Users/Winka/Projects/MachineBrigade-runner')
BASE = '07444b1'
HQ = ('headquarters', 'command_hq')
OBSTACLE = re.compile(r'^(wall_|base_wall|blast_wall|barricade|razor|sandbag_wall|jersey)')
P27_COMMIT = re.compile(r'(?i)(prompt 27|\bwave \d)')

# LOD0 triangle budgets per class [min, max] (the prompt's numbers; MODEL_STANDARD.md section 1).
BUDGET = {
    'light': (3000, 5000), 'heavy': (4000, 7000), 'jet': (4000, 7000), 'helicopter': (4000, 7000),
    'air_other': (0, 7000), 'ship': (8000, 15000), 'boss': (10000, 20000), 'tower': (2000, 4000),
    'structure': (2000, 6000), 'hq': (2000, 6000), 'obstacle': (0, 6000),
}
HD_FACTOR = 2.4          # the _hd file (PC High) may carry this x the class maximum (BUDGETS.md median ratio)
PROPORTION_OFF, PROPORTION_FAR = 0.10, 0.25
OVER_POOR, UNDER_POOR = 1.5, 0.5
MISSING_POOR = 4
LOD1_BAND = (0.35, 0.65)  # "LOD1 ~50 %"


def role(pattern: str) -> re.Pattern:
    """A part role: a node name starting with one of the alternatives, then the end, '_', '.' or a digit."""
    return re.compile(rf'^(?:{pattern})(?:$|[._0-9])', re.I)


WEAPON_PART = 'Main_cannon|Barrels?|Guns?|Part_barrel|Tubes|Launchers?|Pods?|Rocket_tubes|Mortar_tube|Atgm_pod|Howitzer|MG|Coax|Missiles?|Turret|Mount_[a-z]+'
STOWAGE = 'Stowage|Tarp|Crates?|Jerrycans?|Bins?|Toolbox|Racks?|Straps|Ammo_boxes|Bags|Spare_wheel|Tow_cable'
ROLES = {
    'tracked': [
        ('hull', 'Hull|Part_hull|Body|Chassis'), ('turret', 'Turret|Part_turret|Casemate'),
        ('mantlet', 'Mantlet|Gun_mantlet|Elevation|Cradle|Part_mantlet'), ('barrel', WEAPON_PART),
        ('roadwheels', 'Wheels|Road_?wheels|Part_wheel|Bogies'), ('sprocket', 'Sprockets?|Drive_wheels?|Part_sprocket'),
        ('idler', 'Idlers?|Part_idler'), ('tracks', 'Tracks?|Track_links|Part_track|Treads?'),
        ('skirts', 'Skirts?|Side_skirts?|Part_skirt|Skirt_edge'), ('hatches', 'Hatch|Hatches|Cupola'),
        ('sight', 'Sight|Periscopes?|Optics?|Sensor'), ('roof_mg', 'MG|Roof_mg|Mount_mg|Part_mg|Rws|Hmg'),
        ('smoke', 'Smoke|Smoke_launchers|Smoke_brackets|Smoke_dischargers'), ('stowage', STOWAGE),
    ],
    'wheeled': [
        ('wheels', 'Wheels|Tyres|Part_wheel'), ('axles', 'Axles?|Undercarriage|Suspension|Part_axle|Hubs'),
        ('cab', 'Cab|Cabin|Hull|Body|Part_cab|Part_hull'),
        ('glass', 'Glass|Windows?|Windscreens?|Cab_glass|Lit_windows|Canopy|Visors?'),
        ('lights', 'Lamps|Lights?|Head_?lights?|Head_?lamps?|Tail_lamps|Tail_lights|Light_rims|Light_housing'),
        ('stowage', STOWAGE), ('weapon', WEAPON_PART),
    ],
    'ground': [('hull', 'Hull|Part_hull|Body|Chassis|Skirt'), ('weapon', WEAPON_PART)],
    'jet': [
        ('fuselage', 'Fuselage|Hull|Body|Part_fuselage'), ('canopy', 'Canopy|Cockpit|Glass|Windscreen'),
        ('wings', 'Wings?|Part_wing'),
        ('tail', 'Tail|Fins?|Tailplanes?|Stabilators?|Rudders?|Part_tail|Empennage|Vertical_tail|Horizontal_tail'),
        ('intakes', 'Intakes?|Intake_lips|Inlets?'), ('exhaust', 'Nozzles?|Exhausts?|Nozzle_petals|Exhaust_glow'),
        ('pylons', 'Pylons?|Hardpoints?|Racks?'),
        ('stores', 'Missiles?|Bombs|Pods?|Rockets?|Wingtip_missiles|Drop_tanks?|Stores|Guns?'),
        ('flares', 'Flares?|Mount_flare|Flare_dispensers?'),
    ],
    'helicopter': [
        ('fuselage', 'Fuselage|Hull|Body|Part_fuselage'), ('glass', 'Canopy|Glass|Windows?|Cockpit'),
        ('rotor_hub', 'Rotor_hub|Rotor_grips|Hub|Rotor_head|Rotor_mast'), ('blades', 'Rotor_blades|Blades|Rotor_tips'),
        ('tail_rotor', 'Tail_rotor'), ('gear', 'Undercarriage|Skids?|Gear|Tyres|Wheels|Landing_gear'),
        ('stub_wings', 'Wings?|Stub_wings?|Pylons?|Part_wing'),
        ('weapons', 'Guns?|Gun_turret|Missiles?|Pods?|Rockets?|Launchers?|Stinger_tubes|Minigun|Door_guns?'),
    ],
    'air_other': [('body', 'Fuselage|Hull|Body|Capsule|Canopy|Chute|Envelope|Part_[a-z]+')],
    'ship': [
        ('hull', 'Hull|Part_hull'),
        ('superstructure', 'Superstructure|Bridge|Deckhouse|Tiers?|Island|Cabin|Wheelhouse|Funnel'),
        ('mast', 'Masts?|Radar|Radar_mast|Antennas?'), ('turrets', 'Turret|Gun_house|Main_cannon|Barrels?|Guns?|Mount_gun'),
        ('ciws', 'CIWS|Phalanx|AK630|Gatling|Mount_ciws'), ('boats', 'Boats?|RHIB|Ribs?|Lifeboats?|Davits?|Launches?'),
        ('deck_details', 'Deck|Rails?|Railings?|Bollards|Hatches|Vents|Winch|Anchor|Life_rafts?|Capstan'),
    ],
    'tower': [
        ('base', 'Base|Plinth|Footing|Emplacement|Pad|Foundation|Slab|Tower_footing|Block|Floor|Basket_floor|Race'),
        ('walls', 'Sandbags?|Hesco|Walls?|Parapet|Barriers?|Blast_bags|Revetment|Berm|Coping|Buttresses|Side_plates|Fence'),
        ('roof', 'Roof|Roof_deck|Canopy|Cupola|Tower_deck|Deck|Turret|Dome|Shelter'),
        ('antenna', 'Antennas?|Masts?|Aerials?|Radar|Dish|Flag_pole'),
    ],
    'obstacle': [],
}
ROLES['structure'] = ROLES['tower']
ROLES['hq'] = ROLES['tower']
BOSS_ROLES = {
    'body': ('body', 'Hull|Fuselage|Body|Part_hull|Chassis|Deck|Envelope|Gondola|Block'),
    'weapons': ('weapons', WEAPON_PART),
    'ground': ('running_gear', 'Tracks?|Wheels|Tyres|Part_wheel|Bogies|Legs|Rail_wheels|Skirts?|Rollers'),
    'air': ('lift', 'Rotor|Wings?|Part_wing|Envelope|Propellers?|Engines?|Nozzles?|Fins?'),
    'ship': ('superstructure', 'Superstructure|Bridge|Deckhouse|Tiers?|Island|Funnel|Sail|Tower'),
}
TRACKED = role('Tracks?|Track_links|Part_track|Sprockets?|Treads?')
WHEELED = role('Tyres|Wheels|Part_wheel')
ROTOR = role('Rotor')
NO_MUZZLE = {'bomb', 'drone', 'blade'}
SLOT_ALIAS = {'rocket2': 'rocket'}


# --------------------------------------------------------------------------------------------------- data

def load_balance(root: Path = ROOT):
    return load_jsonc((root / BALANCE.relative_to(ROOT)).read_text(encoding='utf-8'))


class Defs:
    """balance.json vehicles with inheritance (inherits / variantOf), the weapons table and model ownership."""

    def __init__(self, balance):
        self.by_id = {v['id']: v for v in balance['vehicles']}
        self.weapons = {w['id']: w for w in balance.get('weapons', [])}

    def field(self, v, key, depth=0):
        if v is None:
            return None
        if key in v or depth > 8:
            return v.get(key)
        parent = self.by_id.get(v.get('variantOf') or v.get('inherits') or '')
        return self.field(parent, key, depth + 1) if parent else None

    def model_of(self, v):
        if v.get('model'):
            return v['model']
        parent = self.by_id.get(v.get('variantOf') or '')
        if parent:
            return self.field(parent, 'model') or parent['id']
        return v['id']

    def armed(self, wid, depth=0):
        """False for the 'none' weapon (unarmed towers and props): no damage or form None."""
        w = self.weapons.get(wid or '')
        if not wid or wid == 'none':
            return False
        if w is None or depth > 8:
            return True
        if w.get('form') == 'None' or w.get('damage') == 0:
            return False
        return self.armed(w.get('inherits'), depth + 1) if 'damage' not in w and w.get('inherits') else True

    def barrels(self, wid, depth=0):
        w = self.weapons.get(wid or '')
        if w is None or depth > 8:
            return 1
        if 'barrels' in w:
            try:
                return max(1, int(w['barrels']))
            except (TypeError, ValueError):
                return 1
        return self.barrels(w.get('inherits'), depth + 1)


def model_owners(defs: Defs, models_dir: Path):
    """{model: [def, ...]} for every shipped model a def draws (its own def first), the branch _a/_b files and the HQs."""
    owners: dict[str, list] = {}
    for v in defs.by_id.values():
        m = defs.model_of(v)
        if (models_dir / f'{m}.glb').exists():
            owners.setdefault(m, []).append(v)
    # Play-test 14 wave M4: a branch's art file is scored for the branch that draws it ("art"), so a branch that drops
    # or changes its parent's weapons (mg_bunker.flame keeps no port guns) is checked against its own mounts.
    for v in defs.by_id.values():
        art = v.get('art')
        if art and (models_dir / f'{art}.glb').exists():
            owners.setdefault(art, []).append(v)
    for m in list(owners):
        for letter in ('a', 'b'):
            branch = f'{m}_{letter}'
            if (models_dir / f'{branch}.glb').exists() and branch not in owners:
                owners[branch] = [v for v in owners[m] if defs.field(v, 'static')] or owners[m]
    for m in HQ:
        if (models_dir / f'{m}.glb').exists():
            owners.setdefault(m, [])
    for m, vs in owners.items():
        vs.sort(key=lambda v: (v['id'] != m, bool(v.get('variantOf')), v['id']))
    return dict(sorted(owners.items()))


def classify(defs: Defs, model: str, own, names) -> str:
    if model in HQ:
        return 'hq'
    if own is None:
        return 'structure'
    f = defs.field
    if f(own, 'boss'):
        return 'boss'
    if f(own, 'naval'):
        return 'ship'
    if f(own, 'flying'):
        if f(own, 'fixedWing'):
            return 'jet'
        return 'helicopter' if any(ROTOR.match(n) for n in names) else 'air_other'
    if f(own, 'static') or not f(own, 'speed'):
        if OBSTACLE.match(model) or f(own, 'wall') or f(own, 'obstacle') or f(own, 'passable'):
            return 'obstacle'
        return 'tower' if f(own, 'fort') or f(own, 'branchOf') else 'structure'
    if any(TRACKED.match(n) for n in names):
        return 'tracked'
    if any(WHEELED.match(n) for n in names):
        return 'wheeled'
    return 'ground'


def budget_class(defs: Defs, cls: str, own) -> str:
    if cls == 'tracked':
        return 'heavy'
    if cls in ('wheeled', 'ground'):
        return 'heavy' if own is not None and defs.field(own, 'class') in ('Tank', 'Heavy') else 'light'
    return cls


def boss_frame(defs: Defs, own) -> str:
    if defs.field(own, 'flying'):
        return 'air'
    if defs.field(own, 'naval'):
        return 'ship'
    return 'ground'


# --------------------------------------------------------------------------------------------------- checks

def count(names, pattern: str) -> int:
    rx = re.compile(pattern, re.I)
    return sum(1 for n in names if rx.match(n))


def weapon_checks(defs: Defs, own, cls: str, names):
    """(muzzles needed, muzzles found, missing list, mount issues, flare (have, need), aps (have, need))."""
    f = defs.field
    missing, mounts = [], []
    need_total = found_total = 0
    slots = []
    main = f(own, 'weapon') if defs.armed(f(own, 'weapon')) else None
    main_slot = SLOT_ALIAS.get(f(own, 'mainSlot') or 'main', f(own, 'mainSlot') or 'main')
    if main:
        slots.append((main_slot, f(own, 'mainAim') or 'Turret', defs.barrels(main), True))
    for s in f(own, 'secondary') or []:
        if isinstance(s, dict) and s.get('weapon') and defs.armed(s['weapon']):
            slots.append((s.get('slot') or 'mg', s.get('aim') or 'Free', defs.barrels(s['weapon']), False))
    if cls == 'boss':
        mw = f(own, 'mountWeapons')
        # Play-test 14 wave M7: a variant with its own "secondary" list has the main mount and those only (BossTemplates
        # never inherits mountWeapons; icarus_mk0's "secondary": [] leaves it its main laser), not its parent's table.
        if own.get('variantOf') and 'secondary' in own:
            mw = None
        need_total = len(mw) if isinstance(mw, dict) and mw else sum(b for _, _, b, _ in slots)
        # A variant boss (keep / drop) loses the mounts only its dropped parts carried (BossTemplates.Strip).
        need_total -= len(dropped_mounts(defs, own))
        found_total = count(names, r'^Muzzle_')
        if found_total < need_total:
            missing.append(f'muzzles {found_total}/{need_total}')
    else:
        per_slot: dict[str, list] = {}
        for slot, aim, barrels, is_main in slots:
            slot = SLOT_ALIAS.get(slot, slot)
            entry = per_slot.setdefault(slot, [0, 0, is_main])
            # A secondary on the main gun's slot (alternate rounds, the coax of a twin) fires from the same barrels.
            entry[0] = max(entry[0], barrels) if slot == main_slot and main else entry[0] + barrels
            if aim == 'Free' and not is_main:
                entry[1] += 1
            entry[2] = entry[2] or is_main
        for slot, (need, free, is_main) in per_slot.items():
            if slot in NO_MUZZLE:
                continue
            have = count(names, rf'^(Muzzle_{slot}{TAG}?(\.\d+)?$|Muzzle_b\d+_{slot}{TAG}?(\.\d+)?$|Launch_{slot})')
            need_total += need
            found_total += min(have, need)
            if have < need:
                missing.append(f'Muzzle_{slot} {have}/{need}' + (' (main)' if is_main else ''))
            if free:
                mhave = count(names, rf'^Mount_{slot}{TAG}?(\.\d+)?$')
                if mhave < free:
                    mounts.append(f'Mount_{slot} {mhave}/{free}')
        if main and cls not in ('jet', 'air_other') and f(own, 'turretTurnRate') and \
                (f(own, 'mainAim') or 'Turret') == 'Turret' and                 not count(names, rf'^(Turret(\.\d+)?$|Gun_turret|Mount_main|Mount_{main_slot}{TAG}?(\.\d+)?$)'):
            mounts.append('Turret (main mount)')
    flares = f(own, 'flareCharges') or 0
    flare = (count(names, r'^Mount_flare(\.\d+)?$'), 2 if flares else 0)
    aps = (count(names, r'^Mount_aps(\.\d+)?$'), 1 if f(own, 'aps') else 0)
    return need_total, found_total, missing, mounts, flare, aps


def dropped_mounts(defs: Defs, own):
    """Mount indices a variant boss's keep / drop list removes: those carried only by dropped parts."""
    parts = defs.field(own, 'parts') or []
    rules = own.get('variant') if isinstance(own.get('variant'), dict) and 'parts' not in own else {}
    if not rules.get('keep') and not rules.get('drop'):
        return set()
    stays = (lambda p: p.get('id') in rules['keep']) if rules.get('keep') else (lambda p: p.get('id') not in rules['drop'])
    kept, dropped = set(), set()
    for p in parts:
        (kept if stays(p) else dropped).update(p.get('mounts') or [])
    return dropped - kept


def boss_part_nodes(defs: Defs, own, names):
    parts = defs.field(own, 'parts') or []
    rules = own.get('variant') if isinstance(own.get('variant'), dict) and 'parts' not in own else {}
    if rules.get('keep'):
        parts = [p for p in parts if p.get('id') in rules['keep']]
    if rules.get('drop'):
        parts = [p for p in parts if p.get('id') not in rules['drop']]
    have = set(names)
    out = []
    for p in parts:
        node = p.get('node')
        # A trailing '*' is a prefix, as the runtime reads it (VehicleView.BossParts).
        if node and not any(alt in have if not alt.endswith('*') else any(n.startswith(alt[:-1]) for n in have)
                            for alt in node.split('|')):
            out.append(f"{p.get('id')}:{node.split('|')[0]}")
    return out


def reference_for(refs, model, owners):
    for v in owners:
        r = refs.get(v['id'])
        if r:
            return v['id'], r
    r = refs.get(model)
    return (model, r) if r else (None, None)


def proportion(have, real, judge='wh'):
    """[(label, error)] of width/length and height/length against the real ratios (error = have / real - 1)."""
    out = []
    if not real or not have or have[0] <= 0.01 or not real[0]:
        return out
    for i, label in ((1, 'w'), (2, 'h')):
        if label in judge and real[i] and have[i]:
            out.append((label, (have[i] / have[0]) / (real[i] / real[0]) - 1.0))
    return out


def lod_share(scan_dir: Path, model: str):
    path = scan_dir / f'{model}.json'
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    t0, t1 = data.get('triangles0') or 0, data.get('triangles1') or 0
    return round(t1 / t0, 3) if t0 > 0 and t1 > 0 else None


# --------------------------------------------------------------------------------------------------- (b) score

def score(scan_dir: Path, out: Path = SCORES, quiet=False):
    balance = load_balance()
    defs = Defs(balance)
    refs = json.loads(REFERENCE.read_text(encoding='utf-8'))['units']
    owners = model_owners(defs, MODELS)
    rows = []
    for model, vs in owners.items():
        own = vs[0] if vs else None
        rec = glb_analyze.analyze(MODELS / f'{model}.glb')
        names = rec['nodeNames']
        cls = classify(defs, model, own, names)
        bcls = budget_class(defs, cls, own)
        lo, hi = BUDGET[bcls]
        tris = rec['triangles']
        hd_path = MODELS / f'{model}_hd.glb'
        hd_tris = glb_analyze.analyze(hd_path)['triangles'] if hd_path.exists() else None
        reasons, poor = [], []
        if tris > hi:
            pct = tris / hi - 1
            reasons.append(f'triangles {tris} over {hi} (+{pct:.0%})')
            if tris > hi * OVER_POOR:
                poor.append('far over budget')
        elif tris < lo:
            reasons.append(f'triangles {tris} under {lo}')
            if tris < lo * UNDER_POOR:
                poor.append('far under budget')
        budget_status = 'over' if tris > hi else 'under' if tris < lo else 'ok'

        if cls == 'boss':
            frame = boss_frame(defs, own)
            role_list = [BOSS_ROLES['body'], BOSS_ROLES['weapons'], BOSS_ROLES[frame]]
        else:
            role_list = list(ROLES[cls])
            if cls == 'tracked' and own is not None and not defs.field(own, 'turretTurnRate'):
                role_list = [r for r in role_list if r[0] not in ('turret', 'mantlet')]
            if cls in ('wheeled', 'ground', 'tracked') and own is not None and not defs.armed(defs.field(own, 'weapon')):
                role_list = [r for r in role_list if r[0] not in ('weapon', 'barrel', 'roof_mg')]
        missing_parts = [name for name, pattern in role_list if not any(role(pattern).match(n) for n in names)]
        if missing_parts:
            reasons.append('missing parts: ' + ', '.join(missing_parts))
            if len(missing_parts) >= MISSING_POOR:
                poor.append(f'{len(missing_parts)} parts missing')

        need = found = 0
        mz_missing, mounts, flare, aps, part_nodes = [], [], (0, 0), (0, 0), []
        if own is not None and cls not in ('obstacle',):
            need, found, mz_missing, mounts, flare, aps = weapon_checks(defs, own, cls, names)
            if cls == 'boss':
                part_nodes = boss_part_nodes(defs, own, names)
        if mz_missing:
            reasons.append('muzzles: ' + ', '.join(mz_missing))
            if any('(main)' in m for m in mz_missing):
                poor.append('main muzzle missing')
        if mounts:
            reasons.append('mounts: ' + ', '.join(mounts))
        if flare[0] < flare[1]:
            reasons.append(f'Mount_Flare {flare[0]}/{flare[1]}')
        if aps[0] < aps[1]:
            reasons.append('Mount_APS missing')
        if part_nodes:
            reasons.append('boss part nodes missing: ' + ', '.join(part_nodes))

        ref_id, ref = reference_for(refs, model, vs)
        props = []
        if ref and ref.get('size') and ref.get('conf') in ('high', 'approx'):
            props = proportion(rec['size'], ref['size'], ref.get('judge', 'wh'))
        prop_flag = ''
        for label, err in props:
            if abs(err) > PROPORTION_OFF:
                prop_flag = 'far' if abs(err) > PROPORTION_FAR or prop_flag == 'far' else 'off'
        if prop_flag:
            reasons.append('proportions vs ' + ref['ref'] + ': ' +
                           ', '.join(f'{l}/L {e:+.0%}' for l, e in props if abs(e) > PROPORTION_OFF))
            if prop_flag == 'far' and ref.get('conf') == 'high':
                poor.append('proportions > 25 % off (high-confidence reference)')

        share = lod_share(scan_dir, model)
        if share is not None and not (LOD1_BAND[0] <= share <= LOD1_BAND[1]):
            reasons.append(f'LOD1 share {share:.0%}')
        grade = 'Kém' if poor else 'Cần sửa' if reasons else 'Tốt'
        rows.append({
            'model': model, 'class': cls, 'budgetClass': bcls,
            'units': ' '.join(v['id'] for v in vs[:4]) + (' ...' if len(vs) > 4 else ''),
            'triangles': tris, 'budgetMin': lo, 'budgetMax': hi, 'budgetStatus': budget_status,
            'overPct': f'{tris / hi - 1:+.0%}' if tris > hi else '',
            'hdTriangles': hd_tris if hd_tris is not None else '',
            'hdOver': 'yes' if hd_tris and hd_tris > hi * HD_FACTOR else '',
            'partsRequired': len(role_list), 'partsMissing': ' '.join(missing_parts),
            'muzzlesNeeded': need, 'muzzlesFound': found, 'muzzlesMissing': '; '.join(mz_missing),
            'mountsMissing': '; '.join(mounts), 'flareMounts': f'{flare[0]}/{flare[1]}' if flare[1] else '',
            'apsMount': f'{aps[0]}/{aps[1]}' if aps[1] else '', 'bossPartNodesMissing': ' '.join(part_nodes),
            'reference': f"{ref['ref']} ({ref_id})" if ref else '', 'refConf': ref.get('conf', '') if ref else '',
            'glbSize': 'x'.join(f'{x:.2f}' for x in rec['size']),
            'propW': next((f'{e:+.1%}' for l, e in props if l == 'w'), ''),
            'propH': next((f'{e:+.1%}' for l, e in props if l == 'h'), ''),
            'propFlag': prop_flag, 'lod1Share': share if share is not None else '',
            'staticGrade': grade, 'poorBecause': '; '.join(poor), 'reasons': ' | '.join(reasons),
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    if not quiet:
        summary(rows)
    return rows


def summary(rows):
    by = lambda key, value: [r for r in rows if r[key] == value]  # noqa: E731
    print(f'{len(rows)} models scored -> {SCORES.relative_to(ROOT)}')
    grades = {g: len(by('staticGrade', g)) for g in ('Tốt', 'Cần sửa', 'Kém')}
    print('static grades: ' + ', '.join(f'{g} {n}' for g, n in grades.items()))
    over = by('budgetStatus', 'over')
    print(f'over budget: {len(over)} (under: {len(by("budgetStatus", "under"))}); worst: ' +
          ', '.join(f"{r['model']} {r['overPct']}" for r in sorted(over, key=lambda r: -r['triangles'] / r['budgetMax'])[:8]))
    print(f"missing parts: {sum(1 for r in rows if r['partsMissing'])} models, "
          f"{sum(len(r['partsMissing'].split()) for r in rows)} parts")
    print(f"missing muzzles: {sum(1 for r in rows if r['muzzlesMissing'])} models; mounts: "
          f"{sum(1 for r in rows if r['mountsMissing'])}; Mount_Flare short: "
          f"{sum(1 for r in rows if r['flareMounts'] and r['flareMounts'].split('/')[0] < r['flareMounts'].split('/')[1])}; "
          f"Mount_APS missing: {sum(1 for r in rows if r['apsMount'] == '0/1')}; boss part nodes: "
          f"{sum(1 for r in rows if r['bossPartNodesMissing'])}")
    flags = [r for r in rows if r['propFlag']]
    print(f"proportion flags (> 10 %): {len(flags)} ({sum(1 for r in flags if r['propFlag'] == 'far')} > 25 %): " +
          ', '.join(r['model'] for r in flags))
    classes = {}
    for r in rows:
        classes[r['class']] = classes.get(r['class'], 0) + 1
    print('classes: ' + ', '.join(f'{k} {v}' for k, v in sorted(classes.items())))


# --------------------------------------------------------------------------------------------------- refs doc

def refs_doc():
    balance = load_balance()
    defs = Defs(balance)
    refs = json.loads(REFERENCE.read_text(encoding='utf-8'))['units']
    glb_cache = {}

    def glb_size(model):
        if model not in glb_cache:
            path = MODELS / f'{model}.glb'
            glb_cache[model] = glb_analyze.analyze(path)['size'] if path.exists() else None
        return glb_cache[model]

    fmt = lambda s: ' x '.join('-' if x is None else f'{x:g}' for x in s) if s else '-'  # noqa: E731
    lines = [
        '# Reference dimensions (fix pass 8)',
        '',
        'Generated by `python Tools/models/scan_prep.py --refs` from `Tools/models/reference_real.json` (edit the JSON, not',
        'this file). Real overall dimensions (length with the gun forward / rotors turning, width = overall width, wingspan',
        'or rotor diameter, height = overall), in balance.json `modelSize` order. The game draws aircraft and ships smaller',
        'than life on purpose, so the check is on **proportions**: width/length and height/length of the data\'s `modelSize`',
        '(or the GLB\'s built box when the def has none) against the real ratios, flagged **bold** above 10 % (MODEL_STANDARD',
        'rule 3.1). "scale" = drawn length / real length, for information. conf: high = published figure; approx = a figure',
        'is uncertain or comes from the base chassis; inspiration = fictional, shown and never flagged; none = no figure yet',
        '(to source). Variants (`variantOf`) and tower branches draw their frame\'s model and are left out.',
        '',
        '| unit | model | reference | real L x W x H (m) | conf | source | modelSize | GLB box | W/L | H/L | scale |',
        '|---|---|---|---|---|---|---|---|---:|---:|---:|',
    ]
    flagged = total = 0
    for v in sorted(defs.by_id.values(), key=lambda x: x['id']):
        if v.get('variantOf') or v.get('branchOf') or '.' in v['id'] or defs.field(v, 'static'):
            continue
        model = defs.model_of(v)
        ref = refs.get(v['id'])
        ms = v.get('modelSize')
        box = glb_size(model)
        have = ms or box
        cells_w = cells_h = scale = ''
        if ref and ref.get('size') and ref.get('conf') in ('high', 'approx') and have:
            total += 1
            judge = ref.get('judge', 'wh')
            errs = dict(proportion(have, ref['size'], judge))
            hit = False
            for key in ('w', 'h'):
                if key in errs:
                    text = f'{errs[key]:+.0%}'
                    if abs(errs[key]) > PROPORTION_OFF:
                        text, hit = f'**{text}**', True
                    if key == 'w':
                        cells_w = text
                    else:
                        cells_h = text
            flagged += hit
            scale = f'{have[0] / ref["size"][0]:.2f}'
        lines.append(f"| `{v['id']}` | {'=' if model == v['id'] else '`' + model + '`'} | "
                     f"{ref['ref'] if ref else '(none set)'} | {fmt(ref.get('size')) if ref else '-'} | "
                     f"{ref.get('conf', '') if ref else 'none'} | {ref.get('source', '') if ref else ''} | "
                     f"{fmt(ms) if ms else '-'} | {fmt([round(x, 2) for x in box]) if box else '-'} | "
                     f"{cells_w} | {cells_h} | {scale} |")
    lines += ['', f'{total} units compared, {flagged} flagged (> 10 % off in W/L or H/L).', '']
    REF_DOC.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{REF_DOC.relative_to(ROOT)}: {total} compared, {flagged} flagged')


# --------------------------------------------------------------------------------------------------- (a) old GLBs

def git(repo: Path, *args, data: bytes | None = None, binary=False):
    res = subprocess.run(['git', '-C', str(repo), *args], input=data, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {res.stderr.decode('utf-8', 'replace').strip()}")
    return res.stdout if binary else res.stdout.decode('utf-8', 'replace')


def stem(path: str) -> str:
    name = path.rsplit('/', 1)[-1]
    return name[:-4] if name.endswith('.glb') else name


def rebuilt_candidates(repo: Path, base: str):
    """{id: [sources]} for the scanned models prompt 27 rebuilt (plus the compulsory checks), before the git filter."""
    found: dict[str, list] = {}

    def add(model, why):
        model = model[:-3] if model.endswith('_hd') else model
        found.setdefault(model, [])
        if why not in found[model]:
            found[model].append(why)

    log = git(repo, 'log', '--format=%x01%s', '--name-only', f'{base}..HEAD', '--', f'{MODELS_REL}/*.glb')
    for block in log.split('\x01')[1:]:
        lines = [x for x in block.splitlines() if x.strip()]
        if lines and P27_COMMIT.search(lines[0]):
            for path in lines[1:]:
                if path.endswith('.glb'):
                    add(stem(path), 'git: ' + lines[0].split(':')[0][:40])
    for module in sorted((repo / 'Tools' / 'blender').glob('mb_p27_*.py')):
        text = module.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'^BUILDERS\s*=\s*\{(.*?)^\}', text, re.S | re.M)
        if m:
            for key in re.findall(r"^\s*['\"](\w+)['\"]\s*:", m.group(1), re.M):
                add(key, 'builder: ' + module.stem)
    decisions = (repo / 'Docs' / 'DECISIONS.md').read_text(encoding='utf-8', errors='replace')
    for sec in re.finditer(r'^## 27 wave[^\n]*\n(.*?)(?=^## )', decisions, re.S | re.M):
        title = sec.group(0).splitlines()[0][3:40]
        for word in set(re.findall(r'`([a-z0-9_]+)`', sec.group(1))):
            add(word, 'DECISIONS ' + title)
    progress = repo / 'Docs' / 'models' / 'PROGRESS.md'
    if progress.exists():
        for line in progress.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('|') and '**done' in line:
                for word in re.findall(r'`([a-z0-9_]+)`', line.split('|')[1]):
                    add(word, 'PROGRESS done')
    # The prompt's compulsory checks: sky_gunship, every tower, structure and HQ.
    add('sky_gunship', 'compulsory')
    defs = Defs(load_jsonc((repo / BALANCE.relative_to(ROOT)).read_text(encoding='utf-8')))
    scanned = model_owners(defs, repo / MODELS_REL)
    for model, vs in scanned.items():
        own = vs[0] if vs else None
        if classify(defs, model, own, []) in ('tower', 'structure', 'hq', 'obstacle'):
            add(model, 'compulsory: structure')
    # Only what the scan draws (vehicles, aircraft, ships, bosses, towers, structures, HQs): no munitions or scenery.
    return {m: why for m, why in found.items() if m in scanned}


def extract_old(repo: Path, base: str, dry_run=False):
    base_sha = git(repo, 'rev-parse', '--short', base).strip()
    candidates = rebuilt_candidates(repo, base)
    changed = {stem(p) for p in git(repo, 'diff', '--name-only', base, 'HEAD', '--', f'{MODELS_REL}/*.glb').split()}
    at_base = {stem(p) for p in git(repo, 'ls-tree', '-r', '--name-only', base, '--', MODELS_REL + '/').split()
               if p.endswith('.glb')}
    keep = sorted(m for m in candidates if m in changed and m in at_base)
    skipped_new = sorted(m for m in candidates if m not in at_base and (repo / MODELS_REL / f'{m}.glb').exists())
    print(f'{len(candidates)} candidates; {len(keep)} existed at {base_sha} and changed since; '
          f'{len(skipped_new)} are new since (no old copy)')
    out = repo / 'Builds' / 'scan_old_models'
    if dry_run:
        for m in keep:
            print(f"{m}\t{'; '.join(candidates[m])}")
        return keep
    out.mkdir(parents=True, exist_ok=True)
    written, failed = [], []
    for m in keep:
        path = f'{MODELS_REL}/{m}.glb'
        try:
            blob = git(repo, 'show', f'{base}:{path}', binary=True)
            if blob.startswith(b'version https://git-lfs'):
                blob = git(repo, 'lfs', 'smudge', path, data=blob, binary=True)
            if blob[:4] != b'glTF':
                raise RuntimeError('not a GLB after smudge (LFS object missing?)')
            (out / f'{m}.glb').write_bytes(blob)
            written.append(m)
        except RuntimeError as e:
            failed.append((m, str(e)))
    with (out / 'old_models.tsv').open('w', encoding='utf-8') as fh:
        fh.write(f'# models rebuilt in prompt 27, as they were at {base_sha} (scan_prep.py --old)\n')
        fh.write('id\tsources\n')
        for m in written:
            fh.write(f"{m}\t{'; '.join(candidates[m])}\n")
    print(f'wrote {len(written)} GLBs to {out}' + (f'; {len(failed)} failed:' if failed else ''))
    for m, why in failed:
        print(f'  {m}: {why}')
    return written


# --------------------------------------------------------------------------------------------------- index

def index(scan_dir: Path):
    rows = list(csv.DictReader(SCORES.open(encoding='utf-8')))
    lines = [
        '# Pass 8 visual scores',
        '',
        f'Generated by `scan_prep.py --index` from static_scores.csv and the sheets in `{scan_dir}`. The scoring pass',
        'fills "visual" (Tốt / Cần sửa / Kém + a concrete reason: silhouette, boxy turret/hull, missing bevels, materials,',
        'proportions, detail at the gameplay distance) and, where an old sheet exists, "old vs new" (better / same / worse;',
        'worse = restore the old GLB or rebuild). Final grade = the lower of static and visual.',
        '',
        '| model | class | static | static reasons | sheet | old sheet | visual | visual reason | old vs new | final |',
        '|---|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        new = scan_dir / f"{r['model']}.png"
        old = scan_dir / f"{r['model']}_old.png"
        lines.append(f"| `{r['model']}` | {r['class']} | {r['staticGrade']} | {r['reasons'][:160]} | "
                     f"{'yes' if new.exists() else 'MISSING'} | {'yes' if old.exists() else ''} |  |  |  |  |")
    out = SCAN_DOCS / 'visual_scores.md'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{out.relative_to(ROOT)}: {len(rows)} rows')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--old', action='store_true', help='(a) extract the pre-prompt-27 GLBs into <repo>/Builds/scan_old_models')
    ap.add_argument('--dry-run', action='store_true', help='with --old: list the ids and their sources, write nothing')
    ap.add_argument('--refs', action='store_true', help='write Docs/models/reference_dimensions.md')
    ap.add_argument('--index', action='store_true', help='write Docs/models/scan/visual_scores.md from the scores and sheets')
    ap.add_argument('--repo', type=Path, default=RUNNER, help='repository for --old (default: the runner tree)')
    ap.add_argument('--base', default=BASE, help='commit before prompt 27\'s first wave (default 07444b1)')
    ap.add_argument('--scan-dir', type=Path, default=None, help='the Unity scan output (default: <repo>/Builds/scan)')
    args = ap.parse_args()
    scan_dir = args.scan_dir or (args.repo / 'Builds' / 'scan' if args.repo.exists() else ROOT / 'Builds' / 'scan')
    if args.old:
        extract_old(args.repo, args.base, args.dry_run)
    elif args.refs:
        refs_doc()
    elif args.index:
        index(scan_dir)
    else:
        score(scan_dir)


if __name__ == '__main__':
    main()

"""Balance pack 2, section 5 and addendum item 1 (Docs/prompts/export_pack2_vi.txt): a minimum range for every boss weapon.

A boss's guns sit high and cannot depress onto a vehicle at its feet. This reads every boss as the loader builds it
(Tools/balance/p26_ab.expand, the port of BossTemplates.Expand), its weapons as the game resolves them, the boss's GLB
(Resources/Models, dequantised by Tools/assets/glb_analyze) and the barrel limits in balance.json "barrelLimits"
(addendum 1b: the Sim has none of its own), and works out per mount:

  direct fire   max(0, (muzzle height - target centre height) / tan(max depression)) + the barrel's reach along the aim
  level rack    sqrt(2 x range x drop) + reach (a rocket rack that cannot depress: launched level, falling under gravity
                at the game's ballistic speed v = sqrt(g x range), the speed that reaches the weapon's range at 45 deg)
  indirect      v^2 x sin(2 x elevation limit) / g with the same v (= range x sin(2 theta)), the shortest of the min / max
                elevation limits (a mortar fires at 45-85 deg only)
  missile       max(arming distance, lock distance)
  aircraft      the view's chin-gun limit (VehicleView.Elevate: -65 deg) from the boss's altitude; bombs none

Muzzle height (addendum 1a): the redrawn model's Muzzle_<slot> / Mount_<slot> node x draw scale (+ altitude for a flyer);
the part's data height (Boss_bo_phan: parts[].at = [x right, y forward, height] in the boss's frame, BossDefs.At / Height,
so the pack's at_z_m, not at_y_m, is the height; the root is the ground, a flyer adds its altitude) where the model has no
node for the mount, and is shown beside it as a check.

Distances are from the boss's centre to the target's near face, the way the weapon key groundMinReach is measured
(CombatSystem.InReach: a ground target with distance - target.Radius < GroundMinReach is not shot; aircraft are). A
direct-fire weapon gets groundMinReach, not minRange: minRange > 0 makes a weapon indirect (WeaponDef.Indirect: no line
of fire, artillery role for the AI, lobbed interception rules) and minReach would also stop it shooting aircraft. Proposed =
max(current, geometric) rounded half up to 1 m. Close-defence weapons (machine guns, flamers, small autocannon / CIWS,
melee) and air-only weapons are shown but not written (their mounts turn and depress; they cover the dead zone).

MB_FINAL F2 (owner's final bundle, 04/10): the values the game uses now come from balance.json "bossWeaponOverrides" (per boss
and weapon: groundMinReach / minRange / maxRange; a variant without a row of its own uses its parent's), not from the shared
weapon. tam_toi_thieu_ghi_m / tam_toi_da_ghi_m show them (ghi_de_tu_boss: the boss whose row is used); --apply, which wrote one
value per shared weapon, is retired.

    python Tools/export/boss_min_range.py            # writes the QA lists to Docs/export/current/_qa/
"""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BALANCE = ROOT / "Assets/MachineBrigade/Resources/Data/balance.json"
MODELS = ROOT / "Assets/MachineBrigade/Resources/Models"
QA = ROOT / "Docs/export/current/_qa"
G = 9.81
CLOSE = {"sung_may", "phun_lua", "phao_nho_ciws", "can_chien"}   # close defence: shown, never written
NAVAL_FRAMES = {"ship", "submarine"}
REFERENCE = "xe_tang"     # the proposal's target (barrelLimits.targetCentreHeightM)
MUZZLE_SLOTS = {"main", "coax", "mg", "missile", "rocket", "gun", "aam", "door_l", "door_r", "ramp", "agl_l", "agl_r", "mortar"}


class Limits:
    """balance.json "barrelLimits" (addendum 1b): class defaults, family overrides, class rules, reference heights."""

    def __init__(self, d: dict):
        bl = d.get("barrelLimits") or {}
        self.classes = bl.get("classes") or {}
        self.families = bl.get("families") or {}
        self.rules = bl.get("classRules") or {}
        self.heights = bl.get("targetCentreHeightM") or {}
        self.arming = float(bl.get("missileArmingM", 1))
        self.cap = float(bl.get("capShare", 0.8))
        self.cover = float(bl.get("coverShare", 0.9))
        self.large = float(bl.get("largeBandM", 8))
        self.negligible = float(bl.get("negligibleBandM", 2))

    def of(self, cls: str, w: dict, mount: dict) -> tuple[dict, str]:
        """(limits, source) of one mount: its own "barrel" over its weapon's over the family's over the class's."""
        out, src = dict(self.classes.get(cls) or {}), f"lop:{cls}"
        fam = (w.get("family") or "").lower()
        if fam in self.families:
            out.update(self.families[fam])
            src = f"ho:{fam}"
        for k, own in (("vu_khi", w.get("barrel")), ("be", mount.get("barrel"))):
            if isinstance(own, dict) and own:
                out.update(own)
                out["estimated"] = own.get("estimated", False)
                src = k
        return out, src


def _paths():
    for p in ("Tools/export", "Tools/balance", "Tools/assets"):
        if str(ROOT / p) not in sys.path:
            sys.path.insert(0, str(ROOT / p))


def half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------------------------------------------------- GLB
_glb_cache: dict = {}


def glb_info(model: str):
    """{nodes: {name: (x, y, z)} at scale 1, bbox_min, bbox_max} of Resources/Models/<model>.glb, or None."""
    if model in _glb_cache:
        return _glb_cache[model]
    _paths()
    import numpy as np
    from glb_analyze import accessor, read_glb, walk
    path = MODELS / f"{model}.glb"
    if not path.exists():
        _glb_cache[model] = None
        return None
    doc, binary = read_glb(path)
    nodes, parents, lo, hi = {}, {}, np.full(3, np.inf), np.full(3, -np.inf)
    for i, m, parent in walk(doc):
        node = doc["nodes"][i]
        name = node.get("name", f"node{i}")
        if name not in nodes:
            nodes[name] = tuple(float(v) for v in m[:3, 3])
            parents[name] = doc["nodes"][parent].get("name", f"node{parent}") if parent is not None else None
        if "mesh" in node:
            for prim in doc["meshes"][node["mesh"]].get("primitives", []):
                pos = accessor(doc, binary, prim["attributes"]["POSITION"]).astype(np.float64)
                w = pos @ m[:3, :3].T + m[:3, 3]
                lo, hi = np.minimum(lo, w.min(0)), np.maximum(hi, w.max(0))
    info = {"nodes": nodes, "parents": parents, "lo": tuple(float(v) for v in lo), "hi": tuple(float(v) for v in hi)}
    _glb_cache[model] = info
    return info


def draw_scale(rec: dict, info) -> float:
    """VehicleView.DrawScaleOf: modelSize[0] / model length when given, else the data's scale (bosses never shrink)."""
    size = rec.get("modelSize")
    if size and info:
        length = info["hi"][2] - info["lo"][2]
        if length > 0.01:
            return float(size[0]) / length
    s = float(rec.get("scale", 1.0) or 1.0)
    if rec.get("flying") and not rec.get("boss", True):
        s *= 0.85
    return s


def mount_node(info, slot: str, k: int):
    """VehicleView: the k-th mount of a slot is the k-th Muzzle_<slot> (name order), else the k-th Mount_<slot>."""
    if not info:
        return None, "khong_co_glb"
    names = info["nodes"]
    slot = slot.lower()

    def listed(prefix):
        # MVA W1-B: the runtime's canonical order (Tools/assets/runtime_nodes.py): plain, semantic tags, legacy .NNN.
        _paths()
        import runtime_nodes
        return runtime_nodes.groups(names).get((prefix.rstrip("_"), slot), [])

    if slot in MUZZLE_SLOTS:
        lst = listed("muzzle_")
        if lst:
            return lst[k % len(lst)], "muzzle"
    if slot.isalpha():
        lst = listed("mount_")
        if lst:
            return lst[k % len(lst)], "mount"
    for alt in ("Muzzle_main", "Turret"):
        if alt in names:
            return alt, "thay_the"
    return None, "hop_bao"


def pivot_of(info, node: str):
    """The yaw pivot a muzzle turns about: its nearest Mount_* / Turret* ancestor (None: fixed on the hull)."""
    p = info["parents"].get(node)
    while p:
        low = p.lower()
        if low.startswith("mount_") or low.startswith("turret"):
            return p
        p = info["parents"].get(p)
    return None


def resized(bid: str, built: dict, raw: dict, frames: dict) -> dict:
    """The boss after BossTemplates.Resize, which Tools/balance/p26_ab.expand leaves out: "size" multiplies the drawn scale,
    the hit radius and the parts' positions (a variant: its parent's size, then its variant.size, default 0.7; its tune
    positions are already in its parent's resized units; its own fields go on top unscaled). Frame defaults under it."""
    b = {**((frames.get(built[bid].get("frame")) or {}).get("defaults") or {}), **copy.deepcopy(built[bid])}
    r = raw.get(bid) or {}
    pid = r.get("variantOf")
    if isinstance(pid, str) and pid in built:
        p = {**((frames.get(built[pid].get("frame")) or {}).get("defaults") or {}), **built[pid]}
        ps = float((raw.get(pid) or {}).get("size") or 1.0)
        rules = r.get("variant") or {}
        vs = float(rules.get("size", 0.7))
        tune = rules.get("tune") or {}
        total = ps * vs
        if "scale" not in r:
            b["scale"] = float(p.get("scale", 1.0) or 1.0) * total
        if "radius" not in r and "radius" in p:
            b["radius"] = float(p["radius"]) * total
        if "parts" not in r:
            for part in b.get("parts") or []:
                at = part.get("at")
                if not isinstance(at, list):
                    continue
                own = isinstance((tune.get(part.get("id")) or {}).get("at"), list)
                part["at"] = [float(x) * (vs if own else total) for x in at]
        b["_size"] = total
        return b
    size = float(r.get("size") or 1.0)
    if abs(size - 1.0) >= 1e-4:
        b["scale"] = float(b.get("scale", 1.0) or 1.0) * size
        if "radius" in b:
            b["radius"] = float(b["radius"]) * size
        for part in b.get("parts") or []:
            if isinstance(part.get("at"), list):
                part["at"] = [float(x) * size for x in part["at"]]
    b["_size"] = size
    return b


def model_of(b: dict, data_vehicles: dict) -> str:
    """The model the view loads: the boss's own, else a variant's parent's (BossTemplates: model = parent id)."""
    if b.get("model"):
        return b["model"]
    parent = b.get("variantOf")
    while parent:
        pv = data_vehicles.get(parent) or {}
        if pv.get("model"):
            return pv["model"]
        if not pv.get("variantOf"):
            return parent
        parent = pv.get("variantOf")
    return b["id"]


# ---------------------------------------------------------------------------------------------------------- data
def load():
    _paths()
    from core.jsonc import strip
    import p26_ab
    d = json.loads(strip(BALANCE.read_text(encoding="utf-8")))
    built = p26_ab.expand(copy.deepcopy(d))
    return d, built, resolved_weapons(d)


def resolved_weapons(d: dict) -> dict:
    _paths()
    from domains import _balance as B

    class _Ctx:
        cache: dict = {}
        sources: dict = {}

        def data(self, _p):
            return d
    c = _Ctx()
    c.cache = {}
    return B.resolved_weapons(c)


def target_heights(lim: Limits) -> dict:
    """Reference target centre heights (m) by class, from barrelLimits.targetCentreHeightM (addendum 1c)."""
    return {k: float(v) for k, v in lim.heights.items()}


def weapon_class(w: dict, boss: dict, main_mount: bool, lim: Limits):
    """(class, group): group chinh (main barrels: guns, rockets, lobbed fire; they set the dead zone) / phong_thu_gan (close
    defence) / dan_dan (guided missiles, drones and bombs: they steer or fall onto the feet) / phong_khong (air only).
    Calibre thresholds: barrelLimits.classRules."""
    fam = (w.get("family") or "").lower()
    proj = w.get("projectile") or "Shell"
    cal = float(w.get("caliberMm") or 0)
    if fam == "melee":
        return "can_chien", "phong_thu_gan"
    if (w.get("targets") or "") == "Air":
        return "phong_khong", "phong_khong"
    if proj == "Bomb":
        return "bom", "dan_dan"
    if proj == "Drone":
        return "drone", "dan_dan"
    if proj == "Missile":
        return "ten_lua", "dan_dan"
    indirect = float(w.get("minRange") or 0) > 0 or bool(w.get("lofted"))
    if indirect:
        return "ban_cau", "chinh"
    if proj == "Rocket":
        return "be_rocket", "chinh"
    if fam == "mg":
        return "sung_may", "phong_thu_gan"
    if fam == "flame" or proj == "Flame":
        return "phun_lua", "phong_thu_gan"
    if fam == "autocannon" and cal <= float(lim.rules.get("smallAutocannonMaxMm", 40)):
        return "phao_nho_ciws", "phong_thu_gan"
    naval = boss.get("frame") in NAVAL_FRAMES
    below = float(lim.rules.get("navalSecondaryGunBelowMm" if naval else "secondaryGunBelowMm", 130 if naval else 100))
    if cal and not main_mount and cal < below:
        return "sung_phu", "chinh"           # a secondary gun (naval under 130 mm, others under 100 mm)
    return ("phao_ham" if naval else "phao_boss"), "chinh"


def geometric(cls: str, w: dict, boss: dict, h_m: float, r_m: float, h_t: float, lim: Limits, mount: dict):
    """(geometric minimum from the boss centre, from the muzzle, depression, min elevation, max elevation, formula, source,
    estimated) for one mount and target height."""
    rng = float(w.get("range") or 0)
    if cls in ("can_chien", "phong_khong", "bom"):
        return 0.0, 0.0, None, None, None, "khong_ap", "khong_ap", False
    if cls in ("ten_lua", "drone"):
        return lim.arming, lim.arming, None, None, None, "max(vu_trang, khoa)", "missileArmingM", True
    if boss.get("flying"):
        b, src = lim.of("may_bay", w, mount)
        dep = float(b.get("depressionDeg", 65))
        own = max(0.0, (h_m - h_t) / math.tan(math.radians(dep)))
        return own + r_m, own, dep, None, b.get("elevationMaxDeg"), "ban_thang_may_bay", src, bool(b.get("estimated"))
    b, src = lim.of(cls, w, mount)
    est = bool(b.get("estimated"))
    if cls == "ban_cau":
        lo, hi = float(b.get("elevationMinDeg", 5)), float(b.get("elevationMaxDeg", 70))
        frac = min(math.sin(math.radians(2 * lo)), math.sin(math.radians(2 * hi)))
        return rng * frac, rng * frac, None, lo, hi, "v2_sin2theta_g", src, est
    dep = float(b.get("depressionDeg", 0))
    if dep <= 0.0:
        own = math.sqrt(2.0 * rng * max(0.0, h_m - h_t))
        return own + r_m, own, 0.0, b.get("elevationMinDeg", 0.0), b.get("elevationMaxDeg"), "roi_tu_do_be_co_dinh", src, est
    own = max(0.0, (h_m - h_t) / math.tan(math.radians(dep)))
    return own + r_m, own, dep, b.get("elevationMinDeg"), b.get("elevationMaxDeg"), "ban_thang", src, est


def boss_override(d: dict, built: dict, bid: str, wid: str):
    """(row, boss id it comes from) of balance.json bossWeaponOverrides for this boss's weapon: its own row, else its nearest
    ancestor's (variantOf), whole; (None, "") when none (MB_FINAL F2, as Catalog.BossReach.cs reads it)."""
    table = d.get("bossWeaponOverrides") or {}
    b, depth = bid, 0
    while b and depth < 8:
        row = (table.get(b) or {}).get(wid)
        if row is not None:
            return row, b
        b, depth = (built.get(b) or {}).get("variantOf"), depth + 1
    return None, ""


def effective_reach(w: dict, row) -> tuple[float, float, float]:
    """(minRange, ground minimum to the near face, reach) the game uses for a weapon under an override row (WeaponDef.WithReach:
    minRange only on a weapon that has one, else folded into groundMinReach)."""
    cur_min = float(w.get("minRange") or 0)
    ground = max(float(w.get("minReach") or 0), float(w.get("groundMinReach") or 0))
    rng = float(w.get("range") or 0)
    if row:
        if "maxRange" in row:
            rng = float(row["maxRange"])
        if "groundMinReach" in row:
            ground = max(float(w.get("minReach") or 0), float(row["groundMinReach"]))
        if "minRange" in row:
            if cur_min > 0:
                cur_min = float(row["minRange"])
            else:
                ground = max(ground, float(row["minRange"]))
    return cur_min, ground, rng


def part_of(b: dict, k: int):
    """The part carrying mount k (parts[].mounts) and its data height (at[2], the boss frame's height), or (None, None)."""
    for p in b.get("parts") or []:
        if k in (p.get("mounts") or []):
            at = p.get("at") or []
            return p.get("id"), (float(at[2]) if len(at) > 2 else None)
    return None, None


def compute(d: dict, built: dict, wres: dict) -> dict:
    lim = Limits(d)
    heights = target_heights(lim)
    veh = {v["id"]: v for v in d.get("vehicles", [])}
    h_ref = heights[REFERENCE]
    rows, bosses = [], {}
    frames = d.get("bossFrames") or {}
    for bid in sorted(built):
        # BossTemplates puts the frame's defaults under the entry (flying, altitude); p26_ab.expand leaves them out
        b = resized(bid, built, veh, frames)
        model = model_of(b, veh)
        info = glb_info(model)
        s = draw_scale(b, info)
        alt = float(b.get("altitude") or 0) if b.get("flying") else 0.0
        top = (info["hi"][1] * s) if info else 0.0
        mounts = [{"weapon": b.get("weapon"), "slot": b.get("mainSlot", "main"), "aim": b.get("mainAim", "")}] + \
                 [m for m in b.get("secondary") or []]
        seen = collections.Counter()
        brows = []
        for k, mount in enumerate(mounts):
            wid, slot, aim = mount.get("weapon"), mount.get("slot", ""), mount.get("aim", "")
            w = wres.get(wid) or {}
            j = seen[slot]
            seen[slot] += 1
            part_id, part_h = part_of(b, k)
            h_part = part_h + alt if part_h is not None else None
            node, how = mount_node(info, slot or "main", j)
            if how in ("thay_the", "hop_bao") and h_part is not None:
                node, how = None, "bo_phan"
            pivot = None
            if node:
                x, y, z = info["nodes"][node]
                h_m, r_m = y * s + alt, math.hypot(x, z) * s
                pivot = pivot_of(info, node)
                if pivot:
                    px, _py, pz = info["nodes"][pivot]
                    r_aim, r_pivot = math.hypot(x - px, z - pz) * s, math.hypot(px, pz) * s
                elif aim == "Hull":
                    r_aim, r_pivot = abs(z) * s, 0.0   # the boss turns its body to aim: the forward reach counts
                else:
                    r_aim, r_pivot = 0.0, r_m          # fixed on the hull, aimed by the mount: no reach along the aim
            elif how == "bo_phan":
                h_m, r_m, r_aim, r_pivot = h_part, 0.0, 0.0, 0.0
            else:
                h_m, r_m, r_aim, r_pivot = (0.75 * top + alt), 0.0, 0.0, 0.0
            cls, group = weapon_class(w, b, k == 0, lim)
            geo, own, dep, emin, emax, formula, src, est = geometric(cls, w, b, h_m, r_aim, h_ref, lim, mount)
            geo_light = geometric(cls, w, b, h_m, r_aim, heights["xe_nhe"], lim, mount)[0]
            geo_heavy = geometric(cls, w, b, h_m, r_aim, heights["hang_nang"], lim, mount)[0]
            cur_min = float(w.get("minRange") or 0)
            cur_reach = max(float(w.get("minReach") or 0), float(w.get("groundMinReach") or 0))
            rng = float(w.get("range") or 0)
            field = "minRange" if cur_min > 0 else "groundMinReach"
            applies = cls not in CLOSE and group != "phong_khong" and cls != "bom"
            prop = half_up(max(cur_min, cur_reach, geo)) if applies else half_up(max(cur_min, cur_reach))
            capped = False
            # MinRange >= Range throws at load (WeaponDef) and a GroundMinReach past the range mutes the gun on the ground:
            # a proposal within 1 m of the range is cut to capShare of it and flagged for the owner.
            if applies and rng and prop >= rng - 1:
                prop, capped = max(half_up(max(cur_min, cur_reach)), int(math.floor(rng * lim.cap))), True
            arc = mount.get("arc") or []
            brows.append({
                "boss_id": bid, "chi_so_be": k, "vu_khi_id": wid or "", "bo_phan_id": part_id or "", "slot": slot, "aim": aim,
                "lop_vu_khi": cls, "nhom": group, "nut_glb": node or "", "cach_tim_nut": how, "model": model,
                "ti_le_ve": round(s, 4), "he_so_size": round(float(b.get("_size", 1.0)), 4), "do_cao_nong_m": round(h_m, 2),
                "do_cao_be_du_lieu_m": round(h_part, 2) if h_part is not None else "",
                "lech_glb_du_lieu_m": round(h_m - h_part, 2) if h_part is not None and how != "bo_phan" else "",
                "do_cao_boss_m": round(top + alt, 2),
                "khoang_cach_ngang_tu_tam_boss_den_nong_m": round(r_m, 2), "nut_be_xoay": pivot or "",
                "khoang_cach_ngang_tu_tam_boss_den_be_m": round(r_pivot, 2),
                "khoang_cach_ngang_theo_huong_ngam_m": round(r_aim, 2),
                "ban_kinh_than_boss_m": float(b.get("radius") or 0), "do_cao_bay_m": alt,
                "goc_ha_nong_toi_da_deg": dep if dep is not None else "",
                "goc_nang_toi_da_deg": emax if emax is not None else "",
                "goc_nang_toi_thieu_deg": emin if emin is not None else "",
                "goc_quay_ngang_deg": 2 * float(arc[1]) if len(arc) > 1 else (360 if aim in ("", "Free", "Turret") else ""),
                "nguon_goc_nong": src, "uoc_dinh": est,
                "tam_toi_thieu_m_hien_tai": cur_min if field == "minRange" else cur_reach,
                "tam_toi_thieu_m": cur_min, "tam_toi_thieu_mep_m": cur_reach, "tam_toi_da_m": rng,
                "toc_do_dau_nong_m_s": float(w.get("projectileSpeed") or 0),
                "toc_do_dan_dao_game_m_s": round(math.sqrt(G * rng), 2) if rng else "",
                "khoang_cach_vu_trang_m": lim.arming if cls in ("ten_lua", "drone") else "",
                "do_cao_tam_muc_tieu_m": h_ref, "cong_thuc": formula,
                "tam_toi_thieu_hinh_hoc_tu_nong_m": round(own, 2),
                "tam_toi_thieu_hinh_hoc_m": round(geo, 2), "tam_toi_thieu_hinh_hoc_xe_nhe_m": round(geo_light, 2),
                "tam_toi_thieu_hinh_hoc_hang_nang_m": round(geo_heavy, 2),
                "tam_toi_thieu_de_xuat_m": prop, "ap_dung": applies,
                "truong_ghi": field if applies else ("khong_ap:phong_thu_gan" if cls in CLOSE else "khong_ap"),
                "cat_theo_tam": capped,
            })
        bosses[bid] = {"bay": bool(b.get("flying")), "khung": b.get("frame", ""),
                       "ban_kinh_trong_m": 0.0 if b.get("flying") else float(b.get("radius") or 0)}
        rows.extend(brows)
    pl = plan(d, built, wres, rows)
    for r in rows:
        # MB_FINAL F2: what the game uses, the boss's override row over the shared weapon.
        row, src = boss_override(d, built, r["boss_id"], r["vu_khi_id"])
        mn, ground, rng = effective_reach(wres.get(r["vu_khi_id"]) or {}, row)
        r["ghi_de_tu_boss"] = src
        r["tam_toi_thieu_ghi_m"] = half_up(max(mn, ground))
        r["tam_toi_da_ghi_m"] = half_up(rng) if rng else 0
        r["ti_le_tam_toi_da_toi_thieu"] = round(rng / max(mn, ground), 2) if max(mn, ground) > 0 else ""
    for bid, summary in bosses.items():
        brows = [r for r in rows if r["boss_id"] == bid]
        summary.update(dead_zone(brows, summary["ban_kinh_trong_m"], lim))
        for r in brows:
            r.update({k: summary[k] for k in ("vung_chet_ban_kinh_m", "vu_khi_che_vung_chet",
                                              "phan_tram_vung_chet_duoc_phu", "co_che_vung_chet")})
    return {"rows": rows, "bosses": bosses, "heights": heights, "plan": pl, "limits": lim}


def dead_zone(brows: list, inner: float, lim: Limits) -> dict:
    """The boss's dead zone from the values the game will use (tam_toi_thieu_ghi_m), measured like GroundMinReach: the
    smallest minimum of its main barrels; the band from its body's edge (inner) out to it; the weapons that reach into
    it and the share of the band they reach; the nearest weapon when nothing does."""
    ground = [r for r in brows if r["nhom"] != "phong_khong" and r["tam_toi_da_ghi_m"]]
    main = [r for r in ground if r["nhom"] == "chinh"] or ground

    def val(r):
        return r["tam_toi_thieu_ghi_m"]
    dz = min((val(r) for r in main), default=0)
    band = dz - inner
    covers, best_lo = [], dz
    for r in ground:
        lo, hi = max(val(r), inner), min(dz, r["tam_toi_da_ghi_m"])
        if val(r) < dz and hi > lo:
            covers.append(r["vu_khi_id"])
            best_lo = min(best_lo, lo)
    share = 1.0 if band <= lim.negligible else max(0.0, (dz - best_lo) / band)
    rest = [r for r in ground if r not in main and r["tam_toi_da_ghi_m"] > inner] or \
        [r for r in ground if r["tam_toi_da_ghi_m"] > inner and val(r) > dz]
    nearest = min(rest, key=val, default=None)
    return {"vung_chet_ban_kinh_m": dz, "dai_chet_m": round(max(0.0, band), 2),
            "vu_khi_chinh_dat_vung_chet": ";".join(sorted({r["vu_khi_id"] for r in main if val(r) == dz})),
            "vu_khi_che_vung_chet": ";".join(sorted(set(covers))),
            "phan_tram_vung_chet_duoc_phu": round(100.0 * min(1.0, share), 1),
            "co_che_vung_chet": band <= lim.negligible or share >= lim.cover,
            "vu_khi_gan_nhat": nearest["vu_khi_id"] if nearest else "",
            "vu_khi_gan_nhat_tam_m": val(nearest) if nearest else "",
            "xem_lai_thoi_gian_ha": band >= lim.large,
            "co_vu_khi_chinh": any(r["nhom"] == "chinh" for r in ground)}


# ---------------------------------------------------------------------------------------------------------- plan
def plan(d: dict, built: dict, wres: dict, rows: list) -> dict:
    """{weapon id: (field, old, new)} so every boss weapon resolves to its proposed value and no other weapon changes.

    Only mounts with ap_dung (not close defence, not air-only, not bombs). A weapon on several mounts (or bosses) takes
    the smallest proposal, so no mount gets a minimum its own geometry does not give (the sheet shows the mounts it
    under-states: tam_toi_thieu_ghi_m < tam_toi_thieu_de_xuat_m); a weapon a non-boss unit also carries is left
    (reported); a weapon whose value would reach another weapon through inherits is pinned on that weapon at its old value."""
    raw = {w["id"]: w for w in d["weapons"]}
    boss_ids = set(built)
    carried = collections.defaultdict(set)
    for v in d["vehicles"]:
        if v["id"] in boss_ids:
            continue
        for wid in [v.get("weapon")] + [m.get("weapon") for m in v.get("secondary") or []]:
            if wid:
                carried[wid].add(v["id"])
    want, field_of, shared = {}, {}, {}
    for r in rows:
        wid = r["vu_khi_id"]
        if not wid or wid not in raw or not r["ap_dung"]:
            continue
        want[wid] = min(want.get(wid, math.inf), r["tam_toi_thieu_de_xuat_m"])
        field_of[wid] = r["truong_ghi"]
    edits = {}
    for wid, val in want.items():
        f = field_of[wid]
        old = float(wres[wid].get(f) or 0)
        if val > old:
            if carried.get(wid):
                shared[wid] = (f, old, val, sorted(carried[wid]))
                continue
            edits[(wid, f)] = val

    def resolve(wid, f, ed, depth=0):
        if (wid, f) in ed:
            return ed[(wid, f)]
        w = raw[wid]
        if f in w:
            return float(w[f] or 0)
        if "inherits" in w and w["inherits"] in raw and depth < 5:
            return resolve(w["inherits"], f, ed, depth + 1)
        return 0.0

    intended = {}
    for wid in raw:
        for f in ("minRange", "groundMinReach"):
            intended[(wid, f)] = edits.get((wid, f), float(wres.get(wid, {}).get(f) or 0))
    pins = {}
    for _ in range(6):
        changed = False
        for (wid, f), val in intended.items():
            if resolve(wid, f, {**edits, **pins}) != val and (wid, f) not in edits:
                pins[(wid, f)] = val
                changed = True
        if not changed:
            break
    effective = {}
    for wid in want:
        key = (wid, field_of[wid])
        effective[wid] = edits[key] if key in edits else \
            half_up(max(float(wres[wid].get(f) or 0) for f in ("minRange", "minReach", "groundMinReach")))
    return {"edits": edits, "pins": pins, "shared": shared, "effective": effective, "proposed": want}


def apply(result: dict) -> list[str]:
    _paths()
    from jsonc_edit import Doc
    doc = Doc(str(BALANCE))
    notes = []

    def number(v):
        return int(v) if float(v).is_integer() else v
    for (wid, f), val in sorted(result["plan"]["edits"].items()):
        doc.edit("weapons", wid, lambda e, f=f, val=val: e.set(f, number(val)), note=f"{wid}.{f} = {val}")
        notes.append(f"{wid}.{f} -> {number(val)}")
    for (wid, f), val in sorted(result["plan"]["pins"].items()):
        doc.edit("weapons", wid, lambda e, f=f, val=val: e.set(f, number(val)), note=f"{wid}.{f} pinned {val}")
        notes.append(f"{wid}.{f} pinned at {number(val)}")
    doc.save()
    return notes


# ---------------------------------------------------------------------------------------------------------- QA
def write_qa(result: dict, out: Path = QA) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = result["rows"]
    with open(out / "boss_tam_toi_thieu.csv", "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    lines = ["# Góc nòng ước định (uoc_dinh) của vũ khí boss", "",
             "Sim/** không có góc nâng / hạ nòng (chỉ VehicleView.Elevate, phần vẽ, kẹp súng máy bay -65..+5 deg): mọi giá trị "
             "dưới đây lấy từ balance.json barrelLimits (mặc định theo lớp, mục 5.2; estimated = uoc_dinh). Chủ dự án kiểm rồi "
             "ghi \"barrel\": {..} vào vũ khí / bệ, hoặc sửa barrelLimits, rồi chạy lại boss_min_range.py --apply.", "",
             "| boss | bệ | vũ khí | lớp | nguồn | góc hạ (deg) | góc nâng min (deg) | góc nâng max (deg) | công thức |",
             "|---|---|---|---|---|---|---|---|---|"]
    n = 0
    for r in rows:
        if r["uoc_dinh"]:
            n += 1
            lines.append(f"| {r['boss_id']} | {r['chi_so_be']} | {r['vu_khi_id']} | {r['lop_vu_khi']} | {r['nguon_goc_nong']} | "
                         f"{r['goc_ha_nong_toi_da_deg']} | {r['goc_nang_toi_thieu_deg']} | {r['goc_nang_toi_da_deg']} | {r['cong_thuc']} |")
    lines += ["", f"Tổng: {n} bệ có góc nòng ước định.", "",
              "Độ cao tâm mục tiêu tham chiếu (barrelLimits.targetCentreHeightM): "
              + ", ".join(f"{k} {v} m" for k, v in result["heights"].items()) + f"; đề xuất theo {REFERENCE}."]
    (out / "boss_goc_nong_uoc_dinh.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="retired (MB_FINAL F2: bossWeaponOverrides holds the values)")
    ap.add_argument("--qa", default=str(QA), help="folder for the QA lists")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    d, built, wres = load()
    result = compute(d, built, wres)
    write_qa(result, Path(args.qa))
    p = result["plan"]
    print(f"{len(result['rows'])} mounts on {len(result['bosses'])} bosses; {len(p['edits'])} weapon edits, "
          f"{len(p['pins'])} pins, {len(p['shared'])} shared weapons left")
    if args.apply:
        print("--apply is retired (MB_FINAL F2): boss minimum / maximum ranges live in balance.json bossWeaponOverrides.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

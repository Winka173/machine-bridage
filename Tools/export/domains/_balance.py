"""Shared reading of balance.json for the domain files: the raw records with their source paths, the game's merge rules
ported from C# (Catalog.Inherited, Catalog.WeaponFamilies, SecondRounds.StripRoundLinks), the classification of
vehicle entries into the sheets of 02 / 03 / 04, who carries which weapon, and the HUD names (read only)."""
from __future__ import annotations

import copy
import sys

from core.repo import ROOT

BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"
CAMPAIGN = "Assets/MachineBrigade/Resources/Data/campaign.json"
HUD = "Assets/MachineBrigade/Scripts/Game/Hud/"


def bal(ctx) -> dict:
    return ctx.data(BALANCE)


def nguon(path: tuple) -> str:
    from core import paths as P
    return f"{BALANCE}: {P.to_str(path)}"


# ---------------------------------------------------------------------- weapons
def weapon_entries(ctx):
    """[(weapon id, raw record, source path)]: balance weapons, then the second rounds (they are weapons too)."""
    key = "weapon_entries"
    if key not in ctx.cache:
        d = bal(ctx)
        out = [(w["id"], w, ("weapons", i)) for i, w in enumerate(d.get("weapons", []))]
        for i, w in enumerate((d.get("secondRounds") or {}).get("rounds", [])):
            out.append((w["id"], w, ("secondRounds", "rounds", i)))
        ctx.cache[key] = out
    return ctx.cache[key]


def weapon_families(ctx) -> dict:
    d = bal(ctx)
    fams = {}
    for f in d.get("weaponFamilies", []) + (d.get("secondRounds") or {}).get("families", []):
        fams[f["id"]] = f
    return fams


def resolved_weapons(ctx) -> dict:
    """{id: the record the game builds}: inherits (parent under child, the parent already finished), then the family's
    fields on top (all but id and real; weaponFamily "" keeps it out), then a second round loses its gun's he / air links."""
    key = "resolved_weapons"
    if key in ctx.cache:
        return ctx.cache[key]
    entries = {wid: w for wid, w, _ in weapon_entries(ctx)}
    fams = weapon_families(ctx)

    def finish(w):
        fam = w.get("weaponFamily")
        if isinstance(fam, str) and fam:
            if fam in fams:
                w = {**w, **{k: v for k, v in fams[fam].items() if k not in ("id", "real")}}
        if "roundOf" in w:
            w = {k: v for k, v in w.items() if k not in ("he", "air")}
        return w

    memo: dict = {}

    def resolve(wid, depth=0):
        if wid in memo:
            return memo[wid]
        w = entries[wid]
        if "inherits" not in w or depth > 4 or w["inherits"] not in entries:
            out = finish(dict(w))
        else:
            base = resolve(w["inherits"], depth + 1)
            out = finish({**base, **w})
        memo[wid] = out
        return out

    ctx.cache[key] = {wid: resolve(wid) for wid in entries}
    return ctx.cache[key]


# ---------------------------------------------------------------------- vehicles
def vehicle_entries(ctx):
    return [(v["id"], v, ("vehicles", i)) for i, v in enumerate(bal(ctx).get("vehicles", []))]


def resolved_vehicles(ctx) -> dict:
    """{id: record} after Catalog.Inherited(vehicles, model: true): the parent's fields under the child's; the parent's id
    as the model when neither names one."""
    key = "resolved_vehicles"
    if key in ctx.cache:
        return ctx.cache[key]
    entries = {vid: v for vid, v, _ in vehicle_entries(ctx)}
    memo: dict = {}

    def resolve(vid, depth=0):
        if vid in memo:
            return memo[vid]
        v = entries[vid]
        if "inherits" not in v or depth > 4 or v["inherits"] not in entries:
            out = dict(v)
        else:
            base = resolve(v["inherits"], depth + 1)
            out = {**base, **v}
            if "model" not in v and "model" not in base:
                out["model"] = v["inherits"]
        memo[vid] = out
        return out

    ctx.cache[key] = {vid: resolve(vid) for vid in entries}
    return ctx.cache[key]


def is_boss_entry(v: dict) -> bool:
    """What steps_c.expand / BossTemplates treat as a boss: boss true, a frame or a rank, or a variant of a boss."""
    return isinstance(v.get("variantOf"), str) or v.get("boss") is True or "frame" in v or "rank" in v


def classify(ctx, vid: str) -> str:
    """boss | wall | hq | utility | tower | elite | vehicle (the sheet a vehicles[] entry goes to)."""
    key = "classes"
    if key not in ctx.cache:
        d = bal(ctx)
        res = resolved_vehicles(ctx)
        hq_id = (d.get("base") or {}).get("hq", "headquarters")
        out = {}
        for i, v, _ in vehicle_entries(ctx):
            r = res[i]
            fort = r.get("fort") if isinstance(r.get("fort"), dict) else {}
            chain_hq = i == hq_id or i.startswith(hq_id + ".") or v.get("inherits") == hq_id
            if is_boss_entry(v):
                out[i] = "boss"
            elif r.get("wall") is True:
                out[i] = "wall"
            elif chain_hq or fort.get("kind") == "Hq":
                out[i] = "hq"
            elif fort.get("kind") == "Utility":
                out[i] = "utility"
            elif r.get("static") is True or "fort" in r or "towerRole" in r or "branchOf" in r:
                out[i] = "tower"
            elif "eliteOf" in v:
                out[i] = "elite"
            else:
                out[i] = "vehicle"
        ctx.cache[key] = out
    return ctx.cache[key][vid]


def boss_built(ctx) -> dict:
    """{boss id: the boss as the loader builds it} from Tools/balance/p26_ab.expand (the repo's port of
    BossTemplates.Expand with prompt 26's mountWeapons), before its rank's scaling."""
    key = "boss_built"
    if key not in ctx.cache:
        sys.path.insert(0, str(ROOT / "Tools" / "balance"))
        try:
            import p26_ab  # noqa: WPS433
        finally:
            sys.path.pop(0)
        ctx.cache[key] = p26_ab.expand(copy.deepcopy(bal(ctx)))
    return ctx.cache[key]


KIND_VI = {"vehicle": "xe", "elite": "xe", "tower": "thap", "wall": "cong_trinh", "hq": "cong_trinh",
           "utility": "cong_trinh", "boss": "boss"}


def weapon_users(ctx) -> dict:
    """{weapon id: [(owner kind, unit id, mount)]}: mount 0 = the main weapon, k = secondary[k-1]; 'other' = named
    elsewhere in the record (a skill, a drop, a burrow); bosses as built (their library parts' weapons included)."""
    key = "weapon_users"
    if key in ctx.cache:
        return ctx.cache[key]
    ids = set(resolved_weapons(ctx))
    out: dict = {}

    def add(wid, kind, unit, mount):
        if isinstance(wid, str) and wid in ids:
            lst = out.setdefault(wid, [])
            if (kind, unit, mount) not in lst:
                lst.append((kind, unit, mount))

    def strings(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k != "id":
                    yield from strings(v)
        elif isinstance(node, list):
            for v in node:
                yield from strings(v)
        elif isinstance(node, str):
            yield node

    res = resolved_vehicles(ctx)
    built = boss_built(ctx)
    for vid, _v, _ in vehicle_entries(ctx):
        kind = classify(ctx, vid)
        r = built.get(vid, res[vid]) if kind == "boss" else res[vid]
        mounts = [r.get("weapon")] + [m.get("weapon") for m in (r.get("secondary") or []) if isinstance(m, dict)]
        for k, wid in enumerate(mounts):
            add(wid, KIND_VI[kind], vid, k)
        for s in sorted(set(strings(r)) - set(mounts)):
            add(s, KIND_VI[kind], vid, "other")
    for pid, part in sorted((bal(ctx).get("bossParts") or {}).items()):
        add(part.get("weapon"), "boss_part", pid, "part")
    ctx.cache[key] = out
    return out


# ---------------------------------------------------------------------- names (read only: the tables are 10's)
def hud_strings(ctx) -> dict:
    """{key: {en, vi}} over every HUD text table (the first table naming a key wins, in file order)."""
    key = "hud_strings"
    if key not in ctx.cache:
        out: dict = {}
        for sid, s in ctx.sources.items():
            if s.kind == "cs_strings" and s.readable:
                for k, v in s.data.items():
                    out.setdefault(k, v)
        ctx.cache[key] = out
    return ctx.cache[key]


def name_of(ctx, *keys: str) -> tuple[str, str]:
    """(English, Vietnamese) of the first key found."""
    t = hud_strings(ctx)
    for k in keys:
        if k in t:
            return t[k]["en"], t[k]["vi"]
    return "", ""


# ---------------------------------------------------------------------- the earlier version (_truoc / _sau)
class _View:
    """balance.json (and the same caches) at a git ref, for the _truoc / _sau columns."""

    def __init__(self, data: dict):
        self._data = data
        self.cache: dict = {}
        self.sources: dict = {}

    def data(self, sid: str):
        return self._data[sid]


def base_view(ctx):
    """The reading of balance.json at ctx.base_ref, or None when there is no base."""
    if not ctx.base_ref:
        return None
    if "base_view" not in ctx.cache:
        from core import jsonc, repo
        raw = repo.show(ctx.base_ref, BALANCE)
        ctx.cache["base_view"] = _View({BALANCE: jsonc.loads(raw.decode("utf-8-sig"))}) if raw else None
    return ctx.cache["base_view"]


CHANGE_ENUM = ["giong", "doi", "moi"]


def declare_changes(sheet, cols: list[str]):
    sheet.col("so_voi_ban_goc", enum=CHANGE_ENUM,
              meaning="so với bản gốc (Phien_ban.ban_goc): giong / doi / moi (chưa có ở bản gốc)")
    for c in cols:
        sheet.col(f"{c}_truoc", meaning=f"{c} ở bản gốc (chỉ điền khi đổi)")
        sheet.col(f"{c}_sau", meaning=f"{c} bây giờ (chỉ điền khi đổi)")


def set_changes(row, cols: list[str], cur: dict, base: dict | None, has_base: bool):
    if not has_base:
        return
    if base is None:
        row.set("so_voi_ban_goc", "moi")
        return
    changed = False
    for c in cols:
        a, b = base.get(c), cur.get(c)
        if _differs(a, b):
            changed = True
            row.set(f"{c}_truoc", a)
            row.set(f"{c}_sau", b)
    row.set("so_voi_ban_goc", "doi" if changed else "giong")


def _differs(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(float(a) - float(b)) > 1e-9
    return a != b

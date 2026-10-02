"""Pass 9 check: applying an import manifest by real key paths (Tools/balance/p29_apply.py --manifest), on a TEMP COPY.

    python Tools/export/tests/test_manifest_apply.py

Copies balance.json, campaign.json and one map file into a temp tree, writes a manifest in the import format and checks:
  - --dry-run writes no data file;
  - only bundles with Trạng thái APPLY and only their APPLY rows are applied (DECIDE waits), per bundle;
  - a CONFLICT (expected_before off the data) and a type change write nothing of their bundle;
  - ALREADY_APPLIED; depends_on (BLOCKED, then OK in the same run once the dependency applied);
  - weapon damage, vehicle hp, a map value and a campaign value land at their id_path, the rest of each file is byte for
    byte the same (comments and layout kept), and a rerun reports APPLIED;
  - the CLI (--manifest --root --dry-run) runs; the real data files are never touched.
Exit code 0 = pass.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "Tools" / "balance"))

import manifest_apply  # noqa: E402
from jsonc_edit import loads  # noqa: E402

from core import paths as P  # noqa: E402
from core.reimport import id_path  # noqa: E402

DATA = "Assets/MachineBrigade/Resources/Data"
BAL, CAM = f"{DATA}/balance.json", f"{DATA}/campaign.json"


def real_hash() -> str:
    h = hashlib.sha256()
    for p in sorted((ROOT / DATA).rglob("*.json")):
        h.update(p.read_bytes())
    return h.hexdigest()


def first_number(node, path=()):
    """The first int leaf (not a bool) in the data, depth first."""
    if isinstance(node, dict):
        items = node.items()
    elif isinstance(node, list):
        items = enumerate(node)
    else:
        return path if isinstance(node, int) and not isinstance(node, bool) else None
    for k, v in items:
        hit = first_number(v, path + (k,))
        if hit is not None:
            return hit
    return None


def row(bundle, sid, data, path, new, status="APPLY", expected=None):
    cur = manifest_apply.get(data, path)
    return {"bundle_id": bundle, "entity_id": bundle, "field_path": P.to_str(path), "expected_before":
            cur if expected is None else expected, "new_value": new, "tolerance": 0, "status": status,
            "data_file": sid, "id_path": id_path(data, path)}


def bundle(bid, status="APPLY", depends=""):
    return {"bundle_id": bid, "Đối tượng": bid, "Trạng thái": status, "depends_on": depends}


def main() -> int:
    fails = []
    before_real = real_hash()
    work = Path(tempfile.mkdtemp(prefix="mb_manifest_apply_"))
    try:
        map_file = sorted((ROOT / DATA / "maps").glob("*.json"))[0]
        MAP = f"{DATA}/maps/{map_file.name}"
        for sid in (BAL, CAM, MAP):
            dst = work / sid
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / sid, dst)
        orig = {sid: (work / sid).read_text("utf-8") for sid in (BAL, CAM, MAP)}
        data = {sid: loads(t) for sid, t in orig.items()}
        bal = data[BAL]
        wi = next(i for i, w in enumerate(bal["weapons"]) if w["id"] == "gun_120mm")
        vi = next(i for i, v in enumerate(bal["vehicles"]) if v["id"] == "light_tank")
        dmg, hp = ("weapons", wi, "damage"), ("vehicles", vi, "hp")
        speed, cp = ("vehicles", vi, "speed"), ("vehicles", vi, "cp")
        mp, cpath = first_number(data[MAP]), first_number(data[CAM])
        g = manifest_apply.get
        man = {"sha256": "test", "rows": [
            row("XL-dmg", BAL, bal, dmg, g(bal, dmg) + 5),
            row("XL-hp", BAL, bal, hp, g(bal, hp) + 10, ),
            row("XL-hp", BAL, bal, speed, g(bal, speed) + 1, status="DECIDE"),  # waits: not APPLY
            row("XL-map", MAP, data[MAP], mp, g(data[MAP], mp) + 1),
            row("XL-cam", CAM, data[CAM], cpath, g(data[CAM], cpath) + 1),
            row("XL-decide", BAL, bal, cp, g(bal, cp) + 1, status="DECIDE"),
            row("XL-conflict", BAL, bal, cp, g(bal, cp) + 2, expected=g(bal, cp) + 100),
            row("XL-type", BAL, bal, cp, "seven"),
            row("XL-same", BAL, bal, speed, g(bal, speed)),
            row("XL-dep", BAL, bal, cp, g(bal, cp) + 3),
        ], "bundles": [bundle("XL-dmg"), bundle("XL-dep", depends="XL-dmg"), bundle("XL-hp"), bundle("XL-map"),
                       bundle("XL-cam"), bundle("XL-decide", status="DECIDE"), bundle("XL-conflict"), bundle("XL-type"),
                       bundle("XL-same"), bundle("XL-nodep", depends="XL-missing")]}
        man["rows"].append(row("XL-nodep", BAL, bal, cp, g(bal, cp) + 4))
        mpath = work / "manifest_import.json"
        mpath.write_text(json.dumps(man, ensure_ascii=False, indent=1), "utf-8")

        # dry run: nothing written
        out = manifest_apply.run(str(mpath), ["*"], True, str(work))
        if any((work / s).read_text("utf-8") != orig[s] for s in orig):
            fails.append("dry run wrote a data file")
        want = {"XL-dep": "OK", "XL-dmg": "OK", "XL-hp": "OK", "XL-map": "OK", "XL-cam": "OK",
                "XL-decide": "SKIPPED(DECIDE)", "XL-conflict": "CONFLICT", "XL-type": "CONFLICT",
                "XL-same": "ALREADY_APPLIED", "XL-nodep": "BLOCKED"}
        if out != want:
            fails.append(f"dry outcomes {out}")

        # real run on the copy
        out = manifest_apply.run(str(mpath), ["*"], False, str(work))
        if out != want:
            fails.append(f"apply outcomes {out}")
        after = {sid: (work / sid).read_text("utf-8") for sid in orig}
        new = {sid: loads(t) for sid, t in after.items()}
        expect = {BAL: [(dmg, g(bal, dmg) + 5), (hp, g(bal, hp) + 10), (cp, g(bal, cp) + 3)], MAP: [(mp, g(data[MAP], mp) + 1)],
                  CAM: [(cpath, g(data[CAM], cpath) + 1)]}
        for sid, changes in expect.items():
            want_data = json.loads(json.dumps(data[sid]))
            for path, v in changes:
                manifest_apply.set_in(want_data, path, v)
            if new[sid] != want_data:
                fails.append(f"{sid}: data is not the old data with only the planned leaves changed")
            a, b = orig[sid], after[sid]
            pre = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
            if pre is None:
                fails.append(f"{sid}: unchanged")
                continue
            # every changed byte sits inside the changed value texts: remove them and the files are equal
            lines_a, lines_b = a.splitlines(), b.splitlines()
            diff = [i for i, (x, y) in enumerate(zip(lines_a, lines_b)) if x != y]
            if len(lines_a) != len(lines_b) or len(diff) > len(changes):
                fails.append(f"{sid}: {len(diff)} lines changed for {len(changes)} values (or the line count moved)")
            if a.count("//") != b.count("//"):
                fails.append(f"{sid}: comments changed")
        print("apply:", out)
        state = json.loads((work / "manifest_import_apply_state.json").read_text("utf-8"))
        if state != sorted(["XL-cam", "XL-dmg", "XL-hp", "XL-map", "XL-same", "XL-dep"]):
            fails.append(f"state {state}")
        if new[BAL]["vehicles"][vi]["cp"] != bal["vehicles"][vi]["cp"] + 3:
            fails.append("XL-dep did not apply after XL-dmg (or another cp bundle wrote)")
        if new[BAL]["vehicles"][vi]["speed"] != bal["vehicles"][vi]["speed"]:
            fails.append("a DECIDE row was applied")

        # rerun: applied bundles stay applied, nothing changes
        out2 = manifest_apply.run(str(mpath), ["XL-dmg", "XL-hp"], False, str(work))
        if out2 != {"XL-dmg": "APPLIED", "XL-hp": "APPLIED"} or any((work / s).read_text("utf-8") != after[s] for s in orig):
            fails.append(f"rerun {out2}")

        # the CLI, dry, on the copy
        cli = subprocess.run([sys.executable, str(ROOT / "Tools" / "balance" / "p29_apply.py"), "--manifest", str(mpath),
                              "--root", str(work), "--dry-run"], capture_output=True, text=True)
        if cli.returncode != 0:
            fails.append(f"CLI failed: {cli.stderr[-300:]}")
        log = (work / "manifest_import_apply_log.md").read_text("utf-8")
        if log.count("## Run") != 4:
            fails.append("log: expected 4 runs")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if real_hash() != before_real:
        fails.append("THE REAL DATA CHANGED")
    print("PASS" if not fails else "FAIL: " + "; ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

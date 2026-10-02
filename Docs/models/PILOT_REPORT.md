# Prompt 35 pilot report (pass 3, lane A, 2026-10-03)

Three models rebuilt from scratch, each in its own new Blender script on the kit35 library, then STOP (prompt 35
section 6). Specs: `Tools/blender/specs/<id>.json`; gate: `Tools/assets/quality_gate.py`; gold: `GOLD_METRICS.md`;
the whole list: `REBUILD_LIST.md`. Decisions: Docs/DECISIONS.md "Prompt 35".

| # | model | why this one | script |
|---|---|---|---|
| 1 | `ixion` (boss) | the owner's pilot 1; its sheet still says "model tạm" | `Tools/blender/mb_p35_ixion.py` |
| 2 | `zu23_technical` (wheeled) | no starter-deck vehicle borrows geometry; the first player card of REBUILD_LIST group 2 (chapter 1, Kém, 39 % shared with rocket_technical) | `Tools/blender/mb_p35_zu23_technical.py` |
| 3 | `rocket_turret` (tower) | no common tower borrows another tower's geometry; the first tower a player builds (chapter 1), Kém | `Tools/blender/mb_p35_rocket_turret.py` |

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, and the
battle angle at the default zoom's 28.4 px per metre, x2):

- `Docs/models/rebuild/ixion/before_after.png`
- `Docs/models/rebuild/zu23_technical/before_after.png`
- `Docs/models/rebuild/rocket_turret/before_after.png`

**In-battle shots (the game's preview scene) are for the lead to render in Unity** (this lane runs no Unity):

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "ixion,zu23_technical,rocket_turret"
```

(the runner, as Docs/models/scan/README.md step 2; the old sheets of the three are the pass 8 scan's).

## Numbers

Soft score 0-100 against the gold mean of the class (Tốt >= 80). Before = the committed GLB at the start of prompt 35.

| model | triangles before -> after (class range) | size L x W x H (target) | hard gates | soft before -> after | grade |
|---|---|---|---|---|---|
| `ixion` | 17,324 -> 35,714 (10-20k) | 27.0 x 13.0 x 10.4 (26 x 12 x 10) | pass | 64.8 -> 79.7 | Cần sửa, NEEDS_HUMAN |
| `zu23_technical` | 1,996 -> 7,436 (3-5k) | 4.58 x 1.61 x 1.64 (4.39 x 1.5 x 1.56) | pass | 77.7 -> 93.9 | Tốt |
| `rocket_turret` | 4,410 -> 9,052 (2-4k) | 4.69 x 4.72 x 3.43 (4.7 x 4.7 x 3.4) | pass | 54.4 -> 79.6 | Cần sửa, NEEDS_HUMAN |

Over the class maximum is information only (owner rule 02/10); every pilot keeps its runtime nodes (validate_specs
--glb ok: every spec feature's node, every Mount / Muzzle), 0 zero-area triangles, COLOR_0 on every mesh, own
geometry (shared 3.2 % / 1.9 % / 3.8 %). Materials 17 / 11 / 16 (prompt 35 section 9 asks 4-6 at integration;
the old files had 11 / 9 / 8; glb_check's renderer caps pass: QUESTIONS.md 11).

Against the gold (class mean; pilot / gold):

| metric | ixion / boss gold | zu23_technical / wheeled gold | rocket_turret / tower gold |
|---|---|---|---|
| silhouette (boundary / hull) | 1.62 / 1.61 | 1.50 / 1.57 | 1.95 / 2.51 |
| edge density | 0.147 / 0.173 | 0.36 / 0.35 | 0.25 / 0.30 |
| brightness regions / 1000 px | 3.5 / 4.7 | 17.2 / 14.8 | 10.9 / 12.4 |
| own pieces per m2 | 0.86 / 2.16 | 1.44 / 0.62 | 0.52 / 0.95 |
| tier 2 / tier 3 pieces per m2 | 0.79 / 3.26 vs 1.78 / 10.08 | 1.05 / 2.79 vs 0.57 / 0.45 | 0.47 / 0.38 vs 1.35 / 0.68 |

The four V2 gold models on the same gate: main_battle_tank 93.5, fighter_jet 99.2, attack_helicopter 92.7,
silver_bug 79.4 (they fail hard gates on node names only: unnamed mantlet / idler, Mount_aam, flare count).

Rounds (section 7, at most 4): ixion 4 (blockout and tier 2; field fit; floodlights, ladder, AC, drums; ram
cylinders fixed), zu23_technical 3 (blockout; size and greenhouse lean; slopes), rocket_turret 4 (blockout;
height, dust, aiming posts, tools; camo net, crates, launcher fittings; irregular earth pad). Ixion and the rocket
turret end 0.3 / 0.4 under 80: both are short on detail density against gold sets that are themselves dense in small
repeated pieces (the boss gold is three trains with rails and sleepers; the tower gold seven towers with railings and
ladders). NEEDS_HUMAN: the owner's look decides (QUESTIONS.md 5).

## Time

| model | rounds | agent time (approx.) |
|---|---|---|
| ixion | 4 | 70 min (including the kit fixes it found) |
| zu23_technical | 3 | 25 min |
| rocket_turret | 4 | 35 min |

Kit35 (pass 1) and the gate, inventory and specs (passes 0-2) were one-off costs (about 3 hours). For the rest:
REBUILD_LIST has 129 P1 and 86 P2; at 25-45 minutes per model (bosses and ships ~60, trucks and towers ~25) that is
roughly 110-150 agent hours for P1 + P2, about 11 waves of 20, plus a spec per model (~5 min each).

## Kit components found missing (added during the pilot)

- `pintle_mg`: machine guns with indexed mounts (`Mount_mg`, `Mount_mg.001` ...); mb_parts27.mg_mount names one only.
- `rot_to` now keeps wall fittings upright (local Y up the wall): doors, lamps, panels on side walls were lying down.
- `panel` / `rivet_line` take rivet size and sides: a 26 m boss needs fewer, bigger, 4-sided rivets (6,440 -> 2,112
  triangles on Ixion with the same look).
- `sandbag_wall(round_both=False)`: towers seen from above do not need the bags' hidden bottom chamfers.
- To add before wave 1 (built inline in the pilots, worth a kit function): an irregular earthwork pad (rocket turret),
  a greenhouse with tumblehome (the technical's cab), a camouflage net on poles, aiming posts.

## Owner questions

`Docs/models/QUESTIONS.md`.

# Prompt 32 report: the base system

Passes 0-9 of prompt 32 (DECISIONS "Prompt 32 L0/L1/L2", "Prompt 32 L4/L5/L6/L8", "Prompt 32 L3 / L7 / L9"). Nothing was
simulated, played or profiled: every number below is the data's, a static script's, or a provisional choice marked as such.
NEED SIM marks what only a battle can tell.

## 1. Pass 0: the precheck (Docs/checks/p32_precheck.md)

| item | result |
|---|---|
| 1. Guard tower +10 % vs the Watch branch's +15 % within 30 m | replace: one inherited field, the best aura counts (no code fix) |
| 2. Units seen at the start | the maps' generic `units` (build_maps.py CONQUEST_UNITS / SURVIVAL_UNITS); L6 marks them `start` and the opening squads replace them |
| 3. Rebuilt towers in supply's army value; CP for destroying a tower | neither: a tower's `cp` is 0 (L2 also skips any fort explicitly) |
| 4. Catch-up today | sliding catch-up up to +50 % income with kill pay by the odds; the once-a-match underdog rule (+25 % and a free drop, Conquest) |
| 5. Forward drop at a strongpoint's outpost | exists (`BaseSystem.TryGetDropZone`), only where a mission marks outposts (MissionSession); HOLD: not switched on in Conquest, King of the Hill or Showdown (Showdown has no capture points, so no outposts) |
| 6. Thermobaric x2 and the structure multiplier | replaces (x2.0 instead of x1.5), never x3 |
| 7. Second rounds | first second round in data order that fits the target; hold 2 s, switch at least 0.5 s |
| 8. Prompt 29 appendix | done first (DECISIONS "Prompt 29 appendix") |

## 2. Rebuild prices (L2)

`Tools/balance/p32_tower_prices.py` (report `Docs/balance/p32_tower_prices.md`); the script's prices are applied (`rebuildCp`
on the 22 cards and their 38 branches); Brandt pays 0.8 of them (runtime price, rounded half up).

| group | script | provisional (the prompt's) |
|---|---|---|
| Small AA (aa_turret / .flak / .sam) | 6 / 6 / 5 | 6 |
| MG bunker (base / .twin / .flame) | 6 / 6 / 6 | 6 |
| Guard tower (base / .watch / .nest) | 5 / 5 / 5 | 4 |
| AT post (base / .long / .recoilless) | 4 / 4 / 3 | 3 |
| Small unarmed (EW, teeth, mines, lighting, decoys) | 3 | 3 |
| CP relay | 6 | 3 |
| Gun turret (base / .long / .auto 57 mm) | 11 / 11 / 11 | - / 6 / 7 |
| Medium AA (base / .heavy / .bofors) | 7 / 7 / 6 | 6 |
| Rocket battery (base / .cluster / .guided) | 11 / 10 / 9 | 6 |
| ATGM tower (base / .top / .multi) | 7 / 7 / 6 | 5 |
| C-RAM (base / .centurion / .dome) | 5 / 5 / 5 | 5 |
| Anti-drone (base / .laser / .net) | 5 / 5 / 5 | - / 7 / 5 |
| Troop shelter | 5 | 5 |
| Long-range SAM (base / .lrr / .pac3) | 13 / 12 / 9 | 12 / 11 / 9 |
| Heavy turret (base / .coastal / .bastion) | 18 / 18 / 18 | 10 / 11 / 17 |
| Drone hangar (base / .lancet / .swarm) | 12 / 14 / 14 | 9 |
| Artillery emplacement (base / .cb / .mortar) | 12 / 12 / 12 | 9 |
| Shield generator (base / .bulwark / .ward) | 10 / 10 / 10 | 9 |

The large gaps (gun turret, rocket battery, heavy turret, drone hangar, emplacement) come from the towers' effective health
(structures take 0.6 from kinetic and shaped charges, and their front armour cuts the reference rounds): NEED SIM.

## 3. Towers cut (REBALANCE_STATS, L2)

Small towers past equivalentCP 8, damage cut through `outgoingDamageMult` (health kept), (8 / eq)^2:

| tower | equivalentCP before | damage share after |
|---|---|---|
| mg_bunker | 14.1 | 0.3204 |
| mg_bunker.twin | 15.5 | 0.2672 |
| mg_bunker.flame | 19.3 | 0.1716 |
| aa_turret | 10.5 | 0.5762 |
| aa_turret.flak | 12.4 | 0.4139 |

Large cuts made on paper (the flame bunker to 17 % of its damage): the first thing to look at in play.

## 4. The steel fortress (heavy_turret.bastion)

Formula price 18 (raw 28.5, over the large band's 15); one roof MG fewer: still 18; health down to the base heavy turret's
2,800: still 18; reaching 13-15 would need health of about 1,200. Verdict: HOLD, not changed (the prompt's provisional 17
is also over 15); for the owner.

## 5. The three HQ types (L4, `Docs/balance/p32_hq_types.md`)

Defensive value a minute of the base under attack (CP), after the refit (`--apply`; one factor per level on each type's
tables, the provisional assumptions in DECISIONS):

| HQ level | target | Fortress (ground) | Fortress (anti-air) | Garrison | Shield |
|---|---|---|---|---|---|
| 1 | 4-5 | 4.5 | 4.4 | 4.5 | 4.5 |
| 2 | 5-6 | 5.6 | 5.5 | 5.5 | 5.5 |
| 3 | 6-7 | 6.5 | 6.3 | 6.6 | 6.5 |
| 4 | 7-8 | 7.6 | 7.4 | 7.7 | 7.5 |
| 5 | 8-9 | 8.5 | 8.5 | 8.5 | 8.5 |

With the prompt's own tables every type ran 1.5-4x over its band (Fortress ground 7.7-18.6, anti-air 13.7-32.8, Garrison
6.0-15.0, Shield 11.6-37.6). The refit is a large cut resting on assumptions (the gun busy half the minute, 1.5 vehicles a
barrage blast, a 2-minute attack, 12 interceptable rounds a minute): NEED SIM.

## 6. Walls (L3)

75 base maps, 280 lines (DECISIONS "Prompt 32 L3 / L7 / L9" lists the maps and why a line is NONE). Static: every line
intact keeps the anchors joined (checked by the planner on the 2 m grid, again in the game as it loads, and by
WallP32Tests); rubble only opens ground. The gate-or-breach AI choice: NEED SIM.

## 7. Showdown, the static check (L7, `Docs/checks/showdown_static.md`)

An army of the median ground card (main_battle_tank) against the HQ 5 reference base and its covering towers:

| army | no wall | HESCO | T-wall | gun wall |
|---|---|---|---|---|
| 40 CP | held | held | held | held |
| 80 CP | held | held | held | held |
| 120 CP | 2.5 min | 3.0 min | held | 3.2 min |
| 160 CP | 1.9 min | 2.2 min | 2.8 min | 2.2 min |

About 950 CP a side to spend in 12 minutes; the base falls to an army of 120-160 CP that has beaten the defender's army
first. Verdict: 12 minutes is a reasonable limit (the HQ lead and sudden death decide an even match). NEED SIM.

## 8. Overlaps and performance (L9)

`Docs/checks/base_overlap.md`: the prompt's pairs kept apart (radar module / neutral radar; repair bay / workshop / shield;
C-RAM / laser / shield under the stacking rule). Same job, reach and price: 9 pairs of a card and its own branch (the
branch differs by its role, by design) and 2 between cards, for the owner: `aa_turret.flak` / `heavy_flak_tower.bofors`
(fragmentation, 46 / 48 m, 6 CP: a small and a medium slot) and `aa_turret.sam` / `c_ram.dome` (air, 56 / 60 m, 5 CP: a
missile post and a dome interceptor, different mechanisms).

`Docs/checks/base_perf.md`: about 63 long-lived entities a side in Showdown at HQ 5 (about 126 a match; the prompt expected
75 / 150), walls without per-tick logic, the Garrison inside the caps, views pooled; NEED PROFILE: the Sim's projectile
allocations, NavGrid relabelling when several segments fall, the rubble slow with many areas, wall and tower draw calls.

## 9. Decisions taken alone (all in DECISIONS)

- L1: the Stinger post's own 56 m line; the 57 mm light-only prey; lasers stop no shells; the wire's existing slow; the
  shelter's 15 m; AI styles moved to the merged cards; folded and retired cards out of the shop.
- L2: the reference threats, the reach bands, the utility price formulas, the cut towers (section 3), the steel fortress
  on HOLD.
- L4: HqType.None for loadouts made in code; the Fortress gun's scale on its mount only; the refit's assumptions; the
  point-defence stacking rule (one system per round, the nearest).
- L5: the reference bases' contents; the campaign progress factor 1 until a mission runs Defend.
- L6: x1.16 applied to the modes' real starting CP (not the prompt's numbers); the commanders' ids for the sheet's names.
- L3: the line geometry (squares round the HQ, 12 x 2 m axis-aligned segments, the radii), the T-wall's narrower gate as an
  extra half-gate segment, the gun wall taking the last open small slot, rubble drawn as the segment's wreck, the 80 %
  breach margin and 40 m a threat unit in the AI's cost, NONE where a line does not fit.
- L7: a camp's gate is an opening, so "the main gate destroyed" reads as enemy ground vehicles through it into the base;
  the 22 eligible maps by the audit's GREEN bands (path and neutral deltas 10 % or less, no RED flag); the AI's objectives
  as the two HQs; ammo depots as the neutrals; the menu's map picker not filtered (an ineligible pick plays the first
  eligible map); sudden death's income x2 of the base income.
- L9: the static models of the Showdown check and the audits; the forward drop on HOLD (campaign outposts only, as found).

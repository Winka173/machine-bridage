# Play-test 14 boss redraw: reuse audit (04/10)

Owner (04/10, last block of Docs/prompts/playtest14_vi.txt): the turrets on the redrawn bosses look reused and do not
fit; "đừng reuse gì hết, tất cả boss khi vẽ lại đều vẽ lại từ đầu, súng railgun cũng vậy vẽ lại"; Icarus Mk.0's tower
looks like a watchtower; "scan các boss vừa vẽ lại tương tự".

Scanned: every play-test 14 boss builder (Tools/blender/mb_pt14_m1.py, mb_pt14_m2.py, mb_pt14_m3.py, mb_pt14_m7.py),
their imports and every call that makes a whole sub-assembly (a turret, gun mount, launcher, tower, mast, radar,
director, VLS, boat, aircraft) in a shared kit (mb_kit35 `K.*`, mb_p35_w5parts `W.*`), in another unit's builder, in an
older builder of the same boss, or in a helper the builder shares between bosses.
Not counted as reuse: geometry primitives (k.lathe / block / extrude / sharp_loft, W.poly_turret = a faceted loft,
K.section_loft / slab_loft, K.chamfer_box), surface kit (rivets, plates, soot, tone, portholes, doors, ladders,
railings, hatches, lamps, beacons, whips, crates, jerrycans) and the `K.engine_flame` / pivot helpers.

Fit: **ok** = built for this boss at its scale; **reused** = the same mesh code another boss also draws (they look
alike side by side); **old** = the boss's pre-play-test-14 model carried over, not redrawn.

## Sea bosses (mb_pt14_m3.py, its "shared naval kit")

| Boss | Sub-assembly (helper) | Also drawn on | Fit before R1 | R1 |
|---|---|---|---|---|
| leviathan | triple 406 mm turrets `triple_turret` (Part_gun .. .002) | kraken (406 mm, same house / bags / hoods) | reused: boxy generic house, reads as Kraken's | redrawn: `_lev_main_turret` |
| leviathan | triple 155 mm in wells `triple_turret(prefix='Sec')` | kraken (155 mm sponsons) | reused | redrawn: `_lev_sec_turret` (well kept, Leviathan-only) |
| leviathan | 127 mm `dp_mount` (Part_mg / .001) | kraken, scylla, nyx (stealth shield) | reused on four ships | redrawn: twin 5"/38-style `_lev_dp_twin` |
| leviathan | Phalanx `gatling` | kraken (x2), scylla (x4) | reused | redrawn: `_lev_ciws` |
| leviathan | triple 25 mm `aa_triple` (Mount_mg.002 - .009) | kraken (8) | reused | redrawn: Type 96 read with top magazines `_lev_aa25` |
| leviathan | twin-arm SAM `twin_arm_launcher` (Mount_missile) | kraken | reused | redrawn: single-arm Mk 13 read `_lev_sam` |
| leviathan | fire-control `director` (x2) | kraken | reused | redrawn: Mk 37 read `_lev_director` |
| leviathan | search radar `radar_array` (Radar) | kraken, scylla, hydra_sub | reused | redrawn: SPS-49 read `_lev_radar` |
| leviathan | VLS `K.vls` (Part_vls) | kraken, nyx; kit used by older ships | reused | redrawn: armoured box launchers `_lev_abl` |
| leviathan | Ka-27 `_helicopter` | kraken, nyx (scaled) | reused (decor) | kept (Kraken's goes in R2; Nyx's replaced) |
| leviathan | `searchlight`, `K.rhib`, `liferaft_rack`, `vent` | kraken / scylla / nyx | decor kit, small | kept |
| scylla | twin 130 mm `twin_turret` | (scylla only) | ok, but a W.poly_turret box | redrawn: AK-130 read `_sc_ak130` |
| scylla | 127 mm `dp_mount` (Part_mg) | leviathan, kraken, nyx | reused | redrawn: AK-100 read `_sc_ak100` |
| scylla | `gatling` x4 | leviathan, kraken | reused | redrawn: AK-630 read `_sc_ak630` |
| scylla | `radar_array` (Radar) | leviathan, kraken, hydra_sub | reused | redrawn: Top Pair back-to-back arrays `_sc_radar` |
| scylla | missile tubes (Part_vls), SAM lids, pyramid mast, fc dome | (scylla only) | ok | kept |
| nyx | railgun (Part_gun > Mount_gun, Rail_barrels) | (nyx only) | owner: replace by a gun turret | redrawn: AGS-style 155 mm stealth turret `_nx_ags` |
| nyx | 127 mm `dp_mount(shield='stealth')` (Part_mg / .001) | leviathan, kraken, scylla | reused | redrawn: Mk 110 stealth cupola read `_nx_cupola` |
| nyx | VLS `K.vls` (Part_vls + aft) | leviathan, kraken | reused | redrawn: peripheral VLS modules `_nx_pvls` |
| nyx | `_helicopter` (Ka-27 at 0.62) | leviathan, kraken | reused | redrawn: Fire Scout drone `_nx_drone` |
| kraken | 406 mm / 155 mm `triple_turret`, `dp_mount`, `aa_triple`, `gatling` x2, `twin_arm_launcher`, `director`, `radar_array`, `K.vls`, `_helicopter` | (after R1 Kraken is their only user) | reused (it drew the same kit as Leviathan) | **R2** |
| hydra_sub | twin 57 mm / 100 mm (in-file, W.poly_turret + K.gun_barrel) | - | ok | - |
| hydra_sub | mast radar `radar_array(w=.9)` | kraken (+ leviathan / scylla before R1) | reused (small) | **R2** |

## Air and space bosses (mb_pt14_m2.py, mb_pt14_m7.py)

| Boss | Sub-assembly | Also drawn on | Fit before R1 | R1 |
|---|---|---|---|---|
| icarus_mk0 | command tower `_mk_tower`: a four-leg lattice tower with a railed cabin on top | (a guard-tower silhouette) | owner: "looks exactly like a watchtower" | redrawn: low raked armoured citadel under construction `_mk_citadel` |
| icarus_mk0 | ventral laser `_main_laser(proto=True)`, PD `_pd_laser(proto=True)`, pod bay `_pod_bay`, engines `_sb_engines(proto=True)` (`bell` / `powerhead`) | silver_bug (same functions, variants) | reused (same pod bay, bells, PD tower) | redrawn: `_mk_laser`, `_mk_pd`, `_mk_pod_rig`, `_mk_engines` |
| silver_bug | coilguns `_coilgun`, beam directors `_beam_director`, twin 40 mm `_crash_turret`, PD `_pd_laser`, ventral laser `_main_laser`, pod bay | icarus_mk0 (PD, laser, bay, engines) | silver_bug-only after R1, but plain boxes | redrawn at higher fidelity: `_sb_coilgun`, `_sb_beam_turret`, `_sb_twin40`, `_sb_pd` |
| silver_bug_wreck | everything of silver_bug (built from it) | - | ok (it is the same ship crashed) | follows silver_bug |
| daedalus | turbolasers `_dd_turbolaser` (in-file) | - | ok | - |
| mega_gunship (Harpy) | door guns `K.pintle_mg` | kit pintle MG on many ground vehicles | reused (small) | **R2** |
| mega_gunship | gun pods, rocket pods, missiles, rotors (in-file) | - | ok | - |
| armored_train | the whole wave-8 train `W8.armored_train` (its turret, rocket, mortar, MG cars) + 3 new cars | - | old (pre-PT14 turrets; `K.pintle_mg` / `K.gun_barrel` kit) | **R2/R3** |
| nuke_train | the whole wave-12 train `NT.nuke_train` (gun, rocket, SAM, AA, ICBM cars) + 2 new cars | - | old | **R2/R3** |
| ixion | the P35 truck `IX.ixion` (its turret) + new RWS / Kornet / Grad (in-file) | - | old turret + ok new mounts | **R2/R3** |

## Ground bosses (mb_pt14_m1.py)

| Boss | Sub-assembly | Also drawn on | Fit before R3 | R3 (mb_pt14_r3.py) |
|---|---|---|---|---|
| fortress_bastion | mortar turret, twin 100 mm / Bofors sponsons, 155 mm ball, Kornets, ZU-23-2 | kit barrels / race / periscopes / hatches / smoke | kit barrel look | 2B8 read `bs_mortar_turret`, D-10 twins + Bofors L/60 `bs_sponson_house`, M284 slab brake `bs_bow_gun`, Kornet-EM `bs_kornet`, ZU-23-2 `bs_zu23`, own hatch / vision block / smoke box |
| bastion_mk0 | twin 100 mm sponsons, open mortar | kit barrels, periscopes, hatches; same layout as Bastion | kit barrel look | riveted 12-sided drums with slotted-brake early 100 mm `m0_sponson`, M1-240 banded tube with arc and handwheels `m0_mortar`, own hatch / vision slot |
| mobile_fortress | turret, roof gun, launchers, SAM, bow gun, flak cupolas, EMP radar | kit barrels / race / smoke / hatches; flak twin like Fenrir's | kit barrel look | 2A44 house `jt_main_turret`, B-4 roof gun `jt_roof_gun`, AK-230 cupolas `jt_flak`, Strela-10 SAM `jt_sam`, 2A46 bow gun `jt_bow_gun`, Smerch open bundles `jt_rockets`, orange-peel reflector `jt_radar`, own hatch / smoke |
| fenrir | twin 35 mm turret, 300 mm pods, radar | kit barrels / race; pods like Jotunn's | kit barrel look | Gepard read `fn_flak`, MLRS boxed pods `fn_rockets`, telescopic-mast planar array `fn_radar`, own hatch |
| behemoth_inferno | flame projectors, thermo gun, flak mount | kit barrels / race / periscopes / hatches / smoke | kit barrel look | M67-read projectors `in_turret_fittings`, Nona-read pepperpot gun `in_thermo`, ZPU-2 `in_zpu`, own oval hatch / vision block / smoke cluster (the Behemoth house stays: the boss is built from that design) |

## Left for R2+
Kraken (the whole weapon fit), hydra_sub's radar, Harpy's door guns, the two trains and Ixion (old turrets carried
over). The ground bosses' shared barrel kit is gone in R3.
over), and optionally per-boss barrel profiles on the ground bosses (K.gun_barrel).

## R2 (lane A, 04/10)
Done: Kraken (every sub-assembly above, plus its carrier deck), Hydra's mast radar, Harpy's aft window guns, both trains'
weapons (wave 8 / wave 12 weapon functions swapped while the old builder runs), Ixion's turret and cab guns, Typhon
redrawn whole (Tools/blender/mb_pt14_r2_naval.py, mb_pt14_r2_land.py; DECISIONS "Play-test 14 boss redraw R2 (lane A)").
Still kit level: K.gun_barrel on Hydra's own guns and on the ground bosses (lane B, R2 ground).

## R4 (lane models, 04/10)
hyperion redrawn whole (its own cruiser builder, mb_pt14_r4_cruiser); theia and coeus are new models with their own weapon
functions (nothing shared with hyperion but the hull-section primitives); hydra_sub's twin 57 mm and 100 mm and nyx's AGS and
cupolas redrawn bespoke (mb_pt14_r4_naval): Hydra's guns no longer use W.poly_turret / K.gun_barrel.

## R5 (lane sea, 04/10)
New weapons each drawn for one ship only in Tools/blender/mb_pt14_r5_sea.py (no kit sub-assembly, nothing from another
unit or boss): Scylla `sc_ak230`, `sc_2m7`, `sc_uran`; Nyx `nx_millennium`, `nx_vls`; Typhon `ty_stern57` (new code for the
third 57 mm, not `_ty_57` called again); Hydra `hy_twin57`, `hy_100`, `hy_launcher` (R4's `mb_pt14_r4_naval.hy_twin57` /
`hy_a190` are no longer called). DECISIONS "Play-test 14 sea bosses after R4 (lane sea)".
## After R4 (lane space, 04/10)
The space bosses' new weapons (Icarus / Mk.0 / Daedalus ventral guns, Hyperion's 155 mm, 127 mm and VLS, Theia's 35 mm and
pods, Coeus's 203 mm, 76 mm and Spike boxes) are each drawn by their own function in Tools/blender/mb_pt14_r5_space.py:
nothing shared between ships, no kit sub-assembly (only the primitives and K.bolt_ring / K.grille / K.lamp surface kit).

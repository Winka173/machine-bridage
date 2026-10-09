# Naval vehicle expansion — model contract (06/10 owner prompt, lane: data/AI/economy)

> **09/10 (naval FINAL spec):** ids renamed, models kept: `ciws_escort_ship` -> `ciws_escort_craft` (model
> `ciws_escort_ship`), `heavy_monitor` -> `naval_monitor` (model `heavy_monitor`), `missile_cruiser` -> `sea_cruiser.missile`
> (model `missile_cruiser`); `sea_cruiser.gun` uses `sea_cruiser`. Weapons now idle on a mount: frigate and missile_frigate
> `Mount_missile_02`, ew_corvette `Mount_missile` (Docs/naval/final/NAVAL_FINAL_REPORT.md).

Written for the model/VFX lanes that will replace the stand-in GLBs this data pass uses. Source of truth for the
gameplay numbers is `Assets/MachineBrigade/Resources/Data/balance.json` (canonical) and
`Docs/naval/PROMPT_owner_vi.md` (the owner prompt + spec); this file only adds the geometry/silhouette brief and the
exact runtime node names each ship's data expects, so a model lane can build a real GLB and swap the `"model"` field
without touching balance.json again.

Node names follow the stable semantic convention of `Docs/models/RUNTIME_NODES.md` (no Blender `.NNN` suffixes): a
weapon mount is `Mount_<slot>` (or `Muzzle_<slot>` for the actual barrel tip) where `<slot>` is the weapon's data
`"slot"` value (`gun`, `mg`, `missile`, `rocket`); a second weapon on the same slot wraps onto `Mount_<slot>_02`,
a third onto `_03`, etc. (the runtime node-resolution rule already used across the roster: "k wraps" in
RUNTIME_NODES.md). All 17 ships are **simple (non-`parts`) vehicles** like `missile_boat` / `hover_gunboat` /
`river_patrol_boat` / `river_gunboat` — a single hitbox, no independently-destructible turrets — so no `Part_*`
node names are required (that convention is reserved for the `sea_corvette`/`sea_cruiser`-style multi-turret hulls;
none of the new ships use it, by design, so every mount resolves even on a stand-in GLB that only has one node per
slot — the runtime wraps multiple same-slot weapons onto whatever nodes exist).

Wake: automatic and data-only (`Game/Views/WakeView.cs`) — any vehicle with a `"naval"` object gets the foam trail
and bow wave procedurally from its hull length/heading; no model node is needed. All 17 ships already carry a
`"naval"` object (role `Raider` for `torpedo_boat`, `Escort` with a station distance for the other 16) so the wake
is ready the moment a model lane ships a real hull — give the hull a clean, mostly-flat waterline near z=0 so the
trail sits correctly.

Death/wreck: reused as-is, no new nodes. These are simple vehicles (no `parts` array), so they use the generic
hull break-up + `deathExplosion` (already set per ship below) exactly like `missile_boat`/`hover_gunboat` — no
`wreck_*` part mesh is required unless a later pass wants a part-based wreck (optional upgrade, not required for
this contract).

Stand-ins currently in balance.json (lane 06/10): `missile_boat.glb` for `torpedo_boat`; `sea_corvette.glb` for the
corvette/frigate-tier hulls and the two support ships; `sea_cruiser.glb` for the destroyer-tier and capital hulls.
`modelSize` force-fits each stand-in to the target box below (same trick as the existing `river_patrol_boat` /
`hover_gunboat` stand-ins already in the file) — a real model only needs to replace the `"model"` id; mount
resolution does not depend on the box size.

## Light tier

### torpedo_boat
- Real-ish reference: fast torpedo attack craft (Nasty/Komar-class scale), game scale **18 x 4.2 x 3.2 m**.
- Silhouette: low, narrow, open-backed hull, a visible twin torpedo rack amidships/bow and a tiny MG tub aft —
  must read as "glass-cannon strike boat" at a glance, nothing else on deck.
- Nodes: `Mount_missile` (torpedo rack, `torpedo_naval`, slot `missile`), `Mount_mg` (`hmg_roof` self-defence MG).
- Stand-in: `missile_boat.glb`.

## Corvette tier

### ashm_corvette
- Reference: missile corvette (Tarantul/Molniya scale), **34 x 6.2 x 5.2 m**.
- Silhouette: forward deck dominated by an angled quad AShM canister bank (4 cells), a single light gun or CIWS
  mount aft.
- Nodes: `Mount_missile` (`ashm_corvette_salvo`, 4-round salvo), `Mount_mg` (`hover_ciws`).
- Stand-in: `sea_corvette.glb`.

### aa_corvette
- Reference: light air-defence corvette, **33 x 6.2 x 5.2 m**.
- Silhouette: a SAM octuple/quad rail forward in place of a gun turret, a CIWS mount, a visibly small deck gun (or
  bare MG tub) — must read as "the gun is an afterthought" next to `ashm_corvette`'s missile bank.
- Nodes: `Mount_missile` (`sam`), `Mount_mg` (`hover_ciws`), `Mount_mg_02` (`hmg_roof`).
- Stand-in: `sea_corvette.glb`.

### ciws_escort_ship (heavy-support tier, grouped here for hull family)
- Reference: small point-defence escort, **26 x 5.4 x 4.6 m** (smallest hull after torpedo_boat).
- Silhouette: 2-3 small CIWS domes/tubs spread fore/aft/beam, a token small gun forward, no missile cells at all —
  the whole point is "all defence turrets, no offence."
- Nodes: `Mount_gun` (`naval_76`), `Mount_mg` / `Mount_mg_02` / `Mount_mg_03` (3x `hover_ciws`).
- Stand-in: `sea_corvette.glb` (scaled down).

### ew_corvette (conditional unit — implemented; see Decision note below)
- Reference: light electronic-warfare support corvette, **32 x 6.0 x 5.1 m**.
- Silhouette: a visible jammer dome/mast in place of a second weapon mount, one weak deck gun, a small
  self-defence SAM rail — no radar dish, no new sensor geometry (owner constraint: no radar/vision/sonar system).
- Nodes: `Mount_gun` (`naval_76`), `Mount_missile` (`sam`, self-defence only).
- Stand-in: `sea_corvette.glb`.
- **Decision**: the generic jammer runtime (`Def.Jammer`, a pure radius/position aura in
  `Sim/Abilities/AbilitySystem.cs`) carries no movement-type or hull assumption, so it is directly reusable on a
  naval hull — this unit is **implemented**, not `BLOCKED_BY_EXISTING_RUNTIME`.

## Frigate tier

### frigate
- Reference: general-purpose frigate (Oliver Hazard Perry scale), **42 x 7.4 x 6.0 m**.
- Silhouette: single 100-127 mm forward gun, a small missile cell block (2 AShM) and a short SAM rail amidships,
  one CIWS aft — the "naval MBT," balanced not specialist.
- Nodes: `Mount_gun` (`naval_100`), `Mount_missile` (`frigate_ashm`), `Mount_missile_02` (`sam`), `Mount_mg`
  (`hover_ciws`).
- Stand-in: `sea_corvette.glb` (scaled up).

### missile_frigate
- Reference: missile frigate, **44 x 7.6 x 6.1 m**.
- Silhouette: a dominant 6-cell AShM bank forward/amidships, a modest 76-100 mm gun as an afterthought, one CIWS,
  a slim self-defence SAM rail.
- Nodes: `Mount_missile` (`missile_frigate_salvo`, 6-round), `Mount_gun` (`naval_76`), `Mount_mg` (`hover_ciws`),
  `Mount_missile_02` (`sam`, optional short-range layer).
- Stand-in: `sea_corvette.glb` (scaled up).

### aa_frigate
- Reference: air-defence frigate, **43 x 7.5 x 6.1 m**.
- Silhouette: medium/long SAM launcher forward (biggest visible system on the hull), CIWS amidships, a 76 mm gun
  aft only — no missile cells of the AShM kind at all.
- Nodes: `Mount_missile` (`sam_long`), `Mount_mg` (`hover_ciws`), `Mount_gun` (`naval_76`).
- Stand-in: `sea_corvette.glb` (scaled up).

## Destroyer tier

### destroyer
- Reference: general-purpose destroyer (Arleigh Burke scale, toned down), **52 x 8.6 x 7.0 m**.
- Silhouette: single 127 mm forward gun, VLS-style missile deck (AShM + medium SAM share the deck visually), two
  CIWS (fore/aft).
- Nodes: `Mount_gun` (`naval_127`), `Mount_missile` (`ashm_quad`), `Mount_missile_02` (`sam_long`), `Mount_mg` /
  `Mount_mg_02` (2x `hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled down).

### gun_destroyer
- Reference: gunnery/shore-bombardment destroyer, **53 x 8.6 x 7.0 m**.
- Silhouette: two 127 mm turrets fore+aft (no large missile deck — read as "all guns"), a short SAM rail, one
  CIWS.
- Nodes: `Mount_gun` (`naval_127`), `Mount_gun_02` (`naval_127`, second turret), `Mount_missile` (`sam`),
  `Mount_mg` (`hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled down).

### missile_destroyer
- Reference: heavy missile destroyer / arsenal ship, **54 x 8.8 x 7.1 m**.
- Silhouette: large 8-cell VLS deck dominating the silhouette, a secondary 100-127 mm gun, two CIWS, a short/medium
  SAM rail — the biggest missile deck in the destroyer tier.
- Nodes: `Mount_missile` (`missile_destroyer_salvo`, 8-round), `Mount_gun` (`naval_100`), `Mount_missile_02`
  (`sam`), `Mount_mg` / `Mount_mg_02` (2x `hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled down).

### aa_destroyer
- Reference: area air-defence destroyer (Aegis-scale), **53 x 8.7 x 7.0 m**.
- Silhouette: a large long-range SAM launcher (the dominant visual system), a secondary medium/short SAM rail, two
  CIWS, a 100-127 mm surface gun aft only.
- Nodes: `Mount_missile` (`sam_48n6`), `Mount_missile_02` (`sam_long`), `Mount_mg` / `Mount_mg_02` (2x
  `hover_ciws`), `Mount_gun` (`naval_127`).
- Stand-in: `sea_cruiser.glb` (scaled down).

## Heavy-support tier

### rocket_artillery_ship
- Reference: navalised rocket-artillery barge (GMLRS/Grad-afloat), **38 x 7.0 x 5.8 m**.
- Silhouette: a large angled rocket-pod battery amidships (the single dominant feature), a bare MG tub for
  self-defence — no main gun, no CIWS, no missile cells, reads as unarmoured/unarmed up close.
- Nodes: `Mount_rocket` (`mlrs_rockets`, navalised GMLRS reuse), `Mount_mg` (`hmg_roof`).
- Stand-in: `sea_corvette.glb`.

### heavy_monitor
- Reference: shore-bombardment monitor (wide, shallow-draft, slow), **46 x 10.0 x 7.6 m** — wider beam than its
  length would suggest for any other hull on this list; low silhouette, heavily armoured deck.
- Silhouette: one large 152-203 mm turret forward, light CIWS aft, no missile cells at all.
- Nodes: `Mount_gun` (`naval_203_monitor`), `Mount_mg` (`hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled down, beam widened in the real model).

## Capital tier

### battlecruiser
- Reference: fast battlecruiser (Kirov/Alaska scale), **68 x 11.0 x 8.6 m**.
- Silhouette: one twin 203-254 mm turret forward (both barrels from one mount — see barrels note below), a 4-cell
  AShM deck, a medium SAM rail, two CIWS.
- Nodes: `Mount_gun` (`naval_203_bc`, `barrels: 2` — model one twin-barrel turret, both barrels fire from this one
  node), `Mount_missile` (`ashm_quad`), `Mount_missile_02` (`sam_long`), `Mount_mg` / `Mount_mg_02` (2x
  `hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled up).

### battleship
- Reference: superheavy battleship (Iowa/Yamato scale), **82 x 13.0 x 10.2 m** — the largest buyable hull in the
  roster.
- Silhouette: **three** single-barrel heavy turrets (the data fires the same weapon from 3 separate mounts — model
  3 distinct turret positions, e.g. two forward superfiring + one aft, the classic battleship layout), a medium SAM
  rail, two CIWS.
- Nodes: `Mount_gun` (`naval_406_bs`, turret 1), `Mount_gun_02` (turret 2), `Mount_gun_03` (turret 3),
  `Mount_missile` (`sam_long`), `Mount_mg` / `Mount_mg_02` (2x `hover_ciws`).
- Stand-in: `sea_cruiser.glb` (scaled up).

### missile_cruiser
- Reference: missile cruiser / area-denial ship, **58 x 9.4 x 7.6 m**.
- Silhouette: large 8-cell VLS deck (the dominant feature, similar visual language to `missile_destroyer` but
  bigger), a single 127-130 mm gun aft, a medium/long SAM rail, two CIWS.
- Nodes: `Mount_missile` (`missile_cruiser_salvo`, 8-round), `Mount_gun` (`naval_127`), `Mount_missile_02`
  (`sam_long`), `Mount_mg` / `Mount_mg_02` (2x `hover_ciws`).
- Stand-in: `sea_cruiser.glb`.

## Summary table (length x beam x height, stand-in, node count)

| id | size (L x B x H, m) | stand-in GLB | mount nodes |
| --- | --- | --- | --- |
| torpedo_boat | 18 x 4.2 x 3.2 | missile_boat | Mount_missile, Mount_mg |
| ashm_corvette | 34 x 6.2 x 5.2 | sea_corvette | Mount_missile, Mount_mg |
| aa_corvette | 33 x 6.2 x 5.2 | sea_corvette | Mount_missile, Mount_mg, Mount_mg_02 |
| ciws_escort_ship | 26 x 5.4 x 4.6 | sea_corvette | Mount_gun, Mount_mg, Mount_mg_02, Mount_mg_03 |
| ew_corvette | 32 x 6.0 x 5.1 | sea_corvette | Mount_gun, Mount_missile |
| frigate | 42 x 7.4 x 6.0 | sea_corvette | Mount_gun, Mount_missile, Mount_missile_02, Mount_mg |
| missile_frigate | 44 x 7.6 x 6.1 | sea_corvette | Mount_missile, Mount_gun, Mount_mg, Mount_missile_02 |
| aa_frigate | 43 x 7.5 x 6.1 | sea_corvette | Mount_missile, Mount_mg, Mount_gun |
| destroyer | 52 x 8.6 x 7.0 | sea_cruiser | Mount_gun, Mount_missile, Mount_missile_02, Mount_mg, Mount_mg_02 |
| gun_destroyer | 53 x 8.6 x 7.0 | sea_cruiser | Mount_gun, Mount_gun_02, Mount_missile, Mount_mg |
| missile_destroyer | 54 x 8.8 x 7.1 | sea_cruiser | Mount_missile, Mount_gun, Mount_missile_02, Mount_mg, Mount_mg_02 |
| aa_destroyer | 53 x 8.7 x 7.0 | sea_cruiser | Mount_missile, Mount_missile_02, Mount_mg, Mount_mg_02, Mount_gun |
| rocket_artillery_ship | 38 x 7.0 x 5.8 | sea_corvette | Mount_rocket, Mount_mg |
| heavy_monitor | 46 x 10.0 x 7.6 | sea_cruiser | Mount_gun, Mount_mg |
| battlecruiser | 68 x 11.0 x 8.6 | sea_cruiser | Mount_gun, Mount_missile, Mount_missile_02, Mount_mg, Mount_mg_02 |
| battleship | 82 x 13.0 x 10.2 | sea_cruiser | Mount_gun, Mount_gun_02, Mount_gun_03, Mount_missile, Mount_mg, Mount_mg_02 |
| missile_cruiser | 58 x 9.4 x 7.6 | sea_cruiser | Mount_missile, Mount_gun, Mount_missile_02, Mount_mg, Mount_mg_02 |

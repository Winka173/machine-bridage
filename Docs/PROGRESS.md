# Progress

Short record of what each milestone delivered and what is still missing. Newest first.

## 2026-09-26: Combat sandbox (Phase 1 and the start of Phase 2)

A playable test battle on the Ashfield sandbox map. It runs on the Android emulator (functional check only; no phone measurements yet).

### Done

- **Simulation** (`Scripts/Sim`, no engine references):
  - 20 Hz fixed step.
  - Stable entity ids.
  - Commands validated on submit: Move, Attack, Attack-move, Stop and Retreat.
  - Team vision.
  - Grid navigation: A* with corner-safe line-of-sight smoothing, formation slots, and stuck detection.
  - Turret aiming, projectiles with travel time, the damage table and splash.
  - Delayed explosions, with chain reactions that terminate.
  - Destroyed buildings unblock the grid.
- **Data:** `Resources/Data/balance.json` (4 weapons, 4 vehicles, 7 props) and `maps/ashfield_sandbox.json`. Both accept `//` comments. Load errors name the offending field.
- **Sandbox mode and placeholder AI:**
  - Starting forces for both sides.
  - Escalating enemy waves every 30 s.
  - A reinforcement call (+2 vehicles, 12 s cooldown).
  - Enemy groups attack-move towards the nearest player vehicle.
- **Voxel art generated in code:**
  - Jeep, light tank, main battle tank and artillery, in team colours.
  - Two house sizes, wall, fuel tank, barrel, ammo crate and tree.
  - A greedy mesher, pre-split debris chunks and rubble.
- **Effects:**
  - Five explosion tiers built from particle layers: flash, fireball, smoke, sparks, debris, shockwave and a light.
  - Muzzle flashes.
  - Tracers timed to the simulation, with arcing artillery shells.
  - Scorch decals in a ring buffer.
  - Burning wrecks, and turrets blown off by cook-offs.
  - Physics debris from destroyed props.
  - Camera shake, and brief slow motion on huge blasts.
  - All pooled, with Eco and High budgets.
- **Controls:**
  - Tap to select, move or attack; tapping a barrel or building attacks it.
  - Double-tap selects all vehicles of that type.
  - Long-press and drag box-selects.
  - One-finger pan and pinch zoom.
  - HUD buttons: All, Stop, Retreat, Attack-move, Reinforce and Restart.
  - Mouse wheel and right-drag in the editor.
- **Rendering:** three hand-written URP shaders (VoxelLit, Unlit, Particle). Vertex colours are linearised for the Linear colour space.
- **Tests:** 38 EditMode tests. They cover content parsing, navigation, commands (including R04 retreat), combat (T01 single damage, T05 chain termination, death explosions, building unblocking), determinism and the voxel mesher.

### Known limitations

- Vehicles drive through wrecks and each other's wrecks. The plan's "large wrecks block" rule is not implemented yet.
- Shots pass through buildings; there is no line-of-fire check.
- Explosions read small at the default zoom. Fireball size, lifetime and bloom need tuning.
- The pace is very lethal: most of the starting force is lost in under a minute. TTK and HP need tuning.
- The deck/CP economy, helicopters, fog-of-war visuals, Conquest tickets and the real AI are not started. These are Phase 3 onwards.
- HUD text is English only and uses the built-in font. Be Vietnam Pro and the localisation tables come with the menus.
- There are no haptics yet: `Handheld.Vibrate` is too long and a short Android vibration plugin is needed.
- The emulator runs on the desktop GPU, so its FPS says nothing about phone performance.

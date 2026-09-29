# Adding a boss (prompt 20 E)

Bosses are data in `Assets/MachineBrigade/Resources/Data/balance.json`, built by `Sim/Content/BossTemplates.cs` before the
catalog parses them. A new boss needs code only when it needs a mechanism the library does not have yet.

## 1. A main boss

Add a vehicle entry with `"boss": true` and:

| Field | What it gives |
|---|---|
| `"frame"` | Its body frame from `bossFrames`: `tracked`, `wheeled`, `hovercraft`, `train`, `ship`, `submarine`, `aircraft`, `spacecraft`. The frame's `defaults` go under the entry (a `spacecraft` brings altitude-tier heights and marks, a `submarine` its dive rules, a `ship` a flagship's `naval` role). The catalog checks the rules: a spacecraft has `tiers`, a ship or submarine `naval`, a submarine a sea `burrow`. |
| `"rank"` | `main` or `mini` (`bossRanks`): a mini's health share (0.55), weapon damage (0.8), big-attack damage (0.7) and cooldown (x1.3), 2 phases instead of 3, at most 3 escorts, the small "Mini boss" bar, the short camera look and the shared track. Rank stats apply to the entry's own `hp`: write the value before the rank. |
| `"general"` | Its general (`brandt`, `varga`, `orlov`, `kessler`, `sen`, `hung`, `quaden`, `aurel`). With no `escorts` table of its own it gets its general's `escortTemplates` entry (a ship sails with its `fleet` instead). |
| `"size"` | A resize of the model, hull, hit radius, part positions and radii, attachments, landing ramp and death blast together (prompt 20 F.1: x1.3-1.5 for a main boss). |
| `"parts"` | Its parts. `{ "use": "<library id>", "id": ..., "at": [x, y, height], "node": ... }` takes a `bossParts` entry; a library part with a `weapon` adds its own mount. Keep the parts at 50-70 % of the body in all (5-15 % each; 7 % or more with ten parts or fewer), each doing something when it breaks. |
| `"bigAttack"` | An entry of `bigAttacks`: strikes of the library's shapes (circle, strip, line, sweep, swarm, missile, drop, buff, quake, rods, arc, charge; a circle with `seats` and `units` lands troops). `parts` carry a strike; `cut` is what is left once one of them breaks (0: it stops). |
| Mechanisms | `factory` (a workshop), `crush` (crushes what is in front), `route` (a battlefield route it follows), `spotAura` (its side's artillery tighter), `wake` (mounts woken by a phase), and the older `burrow`, `landing`, `bombard`, `pods`, `tiers`, `fireTrail`, `guards`, `naval`/`salvo`/`cruise`/`craft`/`fleet`. |
| `"phases"` | Optional: with none (and no tiers) it gets its rank's. |
| `"radioSpawn"` | Its arrival line, `radio.<general>.<boss>`. |

## 2. A mini boss made from a main boss (a variant)

```json
{ "id": "bastion_mk0", "variantOf": "fortress_bastion", "general": "brandt", "bigAttack": "bastion_mk0_mortar",
  "radioSpawn": "radio.brandt.bastion_mk0", "speed": 1.1,
  "variant": { "size": 0.7, "keep": ["mortar", "turret_fl", "turret_fr"], "tint": [0.8, 0.86, 0.72], "mark": "mk0", "name": "mk0",
               "tune": { "mortar": { "hp": 0.15 } } } }
```

It takes its main boss's built data and model, keeps only the listed parts (their mounts renumbered; the dropped weapons'
model nodes hidden), shrinks by `size`, wears `tint`, and is a mini boss. `name` is the naming rule: `mk0` for the prototype
met before the main boss, `mk2` for the upgrade after; a variant with another role gets a name of its own. Its fields on
top replace its parent's (an object such as `tiers` or `naval` is merged one level deep; `null` removes a field). Phases,
radio line and big attack are never inherited. Its big attack is usually its main boss's scaled down:
`{ "id": "bastion_mk0_mortar", "from": "bastion_mortar_walk", "strikes": [ { "count": 3 } ] }`.

## 3. Words, model, lists

- Text keys (in `Game/Hud/BossText.cs`): `unit.<id>` ("Name · subtitle"), `short.<id>`, `note.<id>`, `guide.<id>` (the
  Guide card: rank line, how it fights, strong / weak, tip), `guide.parts.tip.<id>`, `part.<kind>` for a new part kind,
  its radio lines, and for its big attack `bigattack.<id>`, `.cancelled`, `radio.bigattack.<id>`,
  `guide.bigattack.<id>.how/.dodge/.stop`.
- Model: a builder in `Tools/blender` (see `mb_p20_bosses.py`), with `Part_*`/`Mount_*`/`Muzzle_*` nodes named as the parts'
  `node`s. A variant needs none.
- Lists: `BossRushRules.Kinds` (Boss Rush), `BossPartsTests.Expected` (its part count), campaign stages by `def`.
- The card render and In-action clip are made by the lead's graphics run (`CardRenders`); list them in `ASSET_DEBT.md`.

## 4. The Sandbox's calls (prompt 21)

`BossSystem`: `JumpPhase`, `TriggerBig`, `SetBigOff`, `Break`, `Restore`, `ForceTier`, `SetEscorts(on)`, `SwapRank` (main to
its mini version and back).

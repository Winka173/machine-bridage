# Full model rebuild: execution plan

Date: 2026-10-06. Source of truth: `lead/integration` (`b67747c0`). Scope: every gameplay vehicle, boss, armed tower, HQ/building, fortification and gameplay obstacle. Decorative scenery and munitions are inventoried separately; they are included only where the owner confirms “everything” means those too. No game data or runtime code changes are authorized by this plan.

## Goal

Replace the current procedural GLB art with a coherent, visibly stronger art set while preserving all runtime contracts and the shipped game behavior. Treat a model as complete only after its geometry, references, Blender output, Unity import, game pivots, damage parts, presentation and performance budgets have been reviewed.

## Source and current baseline

- Use the lead working copy, not the owner's Unity tree or the older `feature/visual-overhaul` checkout. Lead is `lead/integration` at `b67747c0`; the visual-overhaul checkout was an ancestor 18 commits behind at the last comparison.
- Existing pipeline: `Tools/blender/build_assets.py` registers procedural builders; `mb_kit27.py`/`mb_kit35.py` provide shared geometry; `Tools/blender/specs/*.json` describe references, dimensions, runtime features, mounts, breakable parts, team zones and budgets. Exported models live in `Assets/MachineBrigade/Resources/Models/*.glb`.
- Baseline inventory: 473 GLBs, 273 Blender scripts, 220 spec JSON files, 246 existing per-model rebuild folders. The previous campaign rebuilt 218 of 230 scored models, raising the mean score of rebuilt models from 69.8 to 88.3 and hard-gate passes from 38 to 218. This is a substantial baseline, so “from scratch” means original new geometry for every selected final model, not rerunning the existing builders and not blindly replacing already-good art.
- Existing static tools: `validate_specs.py --glb <ids>`, `glb_check.py --compare`, `quality_gate.py --ids ...`, and `runtime_node_audit.py`. Unity model/card previews are required for visual/runtime confidence but are not run in this kickoff because repo rules prohibit Unity runs without an explicit brief.

## Batch 0: representative vertical slice

| Category | Model | Why it is a useful pilot |
|---|---|---|
| Vehicle | `main_battle_tank` | Recognizable tracked combat vehicle; owner-approved V2 quality anchor; validates tracks, turret, cannon, secondary mounts and team colour. Rebuild must beat the approved version before replacement. |
| Boss | `ixion` | Large multi-part boss with wheel/tyre breakage and layered armor; spec already captures boss parts and detailed features. |
| Tower | `rocket_turret` | Common armed static defense with turning launcher and crew MG; validates a tower silhouette, terrain contact, reload details and pivots. |
| Building/HQ | `headquarters` | Multi-mass structure with turret, twin flak positions, breakable/runtime parts and faction treatment; validates static geometry plus armed-building contracts. |

Each model gets its own isolated builder/spec update and before/after evidence. `main_battle_tank` currently has no `Tools/blender/specs/main_battle_tank.json`, unlike the other three; create its spec and capture the approved-model runtime contract before building. Models are not switched in-game until all gates pass. If a rebuild does not visibly improve the approved source or introduces a contract regression, retain the existing GLB and refine the candidate.

## Quality bar

1. **Readability first:** the type and role read at the battle view and generated LODs; card close-ups are a bonus, not the only quality proof.
2. **Correct shape:** source-backed dimensions and proportions, strong primary silhouette, plausible major masses and weapons, intentional asymmetry, meaningful secondary forms.
3. **Designed detail:** layered large/medium/small detail with clean material zones, bevels and wear. No random greeble noise, overlapping coplanar surfaces, fake detail hidden below the ground, or details that alias away at gameplay scale.
4. **Cohesive faction language:** retain Machine Brigade's clean hard-surface style, distinct Accord field-built and Hegemon modular/concrete cues, and no real national insignia. Use restrained team-colour zones which remain readable on both sides.
5. **Performance with intent:** use the existing class/tier budgets as review signals; minimize separate moving nodes and material slots while retaining clear wear/damage parts. Do not degrade hero silhouettes just to hit a soft budget. Record and justify any intentional growth.
6. **Own geometry:** every independently named model must be a deliberate design. Shared kit primitives and family components are allowed; copying another model and stretching/recolouring it is not.

## Runtime compatibility gates

- Keep IDs, paths, orientation, origin, scale/bounds, team-colour conventions and card/render assumptions stable unless a mismatch is documented and separately approved.
- Preserve exact data-driven names/counts for `Turret`, `Elevation`, `Mount_*`, `Muzzle_*`, flare and APS pivots; one muzzle per data barrel; rotor/propeller articulation; boss `Part_*` breakables and deployable nodes.
- Keep part pivots and parent transforms at expected positions/orientations, not merely nodes with the right names.
- Preserve `COLOR_0`, material names/zones, glTF compatibility, non-zero-area geometry, bounds and mobile-load budgets.
- No edits to `balance.json`, gameplay tunables, card/model pointers, runtime C# or scene composition as part of art-only model work.

## Per-model workflow

1. Capture current GLB, builder, spec, def/data requirements, baseline stats, card and battle-camera preview. Record any already-known findings.
2. Write/revise the model spec first: real reference or fictional design brief, dimension confidence, silhouette, feature-to-node map, materials, team zones, breakables, mounts/muzzles and complexity targets.
3. Build a new, model-specific procedural script using shared kit helpers. Keep generation deterministic and builders individually filterable.
4. Run only the relevant static checks: spec/GLB contract, GLB analyzer/check, runtime-node audit, quality gate, plus Python syntax/build checks. Review every changed node/mesh/material and compare stats against the accepted baseline.
5. Render Blender multi-angle/contact sheets, then Unity card and battle-camera/LOD previews. Inspect visually at normal play scale and both team colors.
6. Correct failures and repeat gates. Do not accept lower quality because a numeric score is high; compare to the previous approved model and the category art bar.
7. Keep rollback trivial: separate commits per model/family; no batch overwrites. Rebuild only named IDs and inspect `git status` before staging.

## Known baseline findings from kickoff

- `glb_check.py --compare`: no changes against the committed GLB baseline.
- `quality_gate.py --ids ixion,main_battle_tank,rocket_turret,headquarters`: all four pass existing hard checks; soft scores are 90.9, 82.4, 84.0, 96.3 respectively. These are baseline scores to beat, not proof of in-game import/runtime correctness.
- The all-spec data-only validator reports some unrelated missing weapon spec entries. The selected-ID GLB check found legacy mismatches for Ixion and HQ: Ixion has stale feature/part nodes, and HQ has stale repeated-mount node names. `main_battle_tank` and `rocket_turret` pass. These selected specs must be triaged against balance and the actual intended runtime contract; do not paper over them with data/gameplay changes.
- `runtime_node_audit.py`: 0 new hard findings, 4 known hard findings, 6 soft findings. Preserve this baseline distinction and require no new hard findings.
- No Unity build, preview, test, sim, sweep, or measurement was run.

## Rollout after Batch 0

After the four-model review, lock the procedural kit/material palette and the accepted complexity/performance range. Re-inventory against current source and run in waves by family: common tracked/wheeled vehicles; aircraft; naval units; bosses by frame; towers/branches; HQ/structures/fortifications; obstacles and scenery if included. Rebuild family variants together where they share an approved design language, but keep every gameplay ID and runtime contract explicit. Integrate only after category-level visual and runtime review.

## Decisions still needed before broad rollout

- Whether “all models” includes decorative biome/map scenery, ammunition/projectiles, wreck/debris props and archived/non-gameplay GLBs, or means all gameplay vehicles, bosses, towers and buildings with their required variants.
- Unity previews/ModelScan and permitted in-game functional checks are needed for the final acceptance gate. Current repository guidance forbids running Unity/tests without explicit authorization; get that authorization before those checks.
- Any desired changes to factions, palette, realism level or a model whose real proportions are intentionally stylized should be recorded before its spec is frozen.

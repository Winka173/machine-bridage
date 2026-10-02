# Prompts 29 appendix, 31 and 32, done locally (2026-10-02)

The cloud session ran out of capacity; the owner: "bạn làm luôn". Two lanes, one agent each, merged by the lead (who
compiles in Unity, runs CatalogCheck after data changes and renders cards). No tests, sims or measures run (the
owner's rule): the prompts' "write automated tests" means write them. Unity NUnit limits: see CLOUD_HANDOFF "Local
merge notes".

| lane | worktree | order |
|---|---|---|
| A | `MachineBrigade-art` | prompt 29 appendix -> prompt 32 L0, L1, L2 -> (after lane B's 31 L3 is merged) 32 L3 -> L4 -> L5 -> L6 -> L7 -> L8 -> L9 |
| B | `MachineBrigade-art2` | prompt 31 L0, L1, L2 -> L3 (prebuilt NavGrid states for events) -> L4 -> L5 -> L6 (report; the lead builds the PDF) |

Coordination: prompt 31 L3 creates the prebuilt NavGrid state mechanism (Sim, `Scripts/Sim/Navigation`); prompt 32 L3
(walls) must reuse it, so lane A does 32 L3 only after 31 L3 is merged. Both lanes append DECISIONS sections
(`## Prompt 31 <pass> (lead pass, <date>)`, `## Prompt 32 <pass> ...`, `## Prompt 29 appendix ...`); do not edit the other
lane's files. Data changes (balance.json, campaign.json) are allowed by these prompts; list the changed keys so the
lead runs CatalogCheck. UI is written blind (no compile in the agent); the lead compiles after each merge.

## Prompts 33 and 34, three lanes (owner 2026-10-02: "tăng agent lên 3")

| lane | worktree | after its current work |
|---|---|---|
| C | `MachineBrigade-art3` | prompt 34 L0, L1, L2 (families, boss weapon table and DPS-keeping script, data), L3 (warnings), L4 (multi-barrel; Blender muzzles), then L5-L7 (effects, sound, wrecks), L8 (previews; uses prompt 33 assets if merged, else temporary scenes), L9 |
| A | `MachineBrigade-art` | prompt 32 L4/L5/L6/L8 -> 32 L3 and L7 after 31 L3 -> prompt 33 L0-L3, L6 (map zones, edges, tags, dressing) |
| B | `MachineBrigade-art2` | prompt 31 L3-L6 -> prompt 33 L4, L5 (sea route graph, rail splines and crossings: Sim navigation like 31 L3) -> 33 L7 |
Prompt 34 L8 and prompt 33 share the preview/biome assets: lane C uses temporary scenes if 33 is not merged and records it.

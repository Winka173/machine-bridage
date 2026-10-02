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

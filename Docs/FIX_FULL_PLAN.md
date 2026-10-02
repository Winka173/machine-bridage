# The full fix prompt (Docs/prompts/fix_full_vi.txt), three lanes (2026-10-02)

Owner: "tôi thấy có rất nhiều vấn đề, sửa ngay". Its rules are the base: prompts 28-34 already ran here (see
Docs/checks/fix_precheck.md once written); where they overlap, this prompt wins and DECISIONS "Sửa lỗi tổng hợp" says so.
No Unity, tests or sims in the agents; the lead merges, compiles, runs CatalogCheck, renders cards/previews.

| lane | worktree | passes |
|---|---|---|
| A (weapons) | MachineBrigade-art | L0 precheck, L1 full weapon audit, L2 caliberMm / warheadKg and card display, L3 rates, families, boss DPS make-up (redo prompt 34's boss table where it kept the wrong p26_* DPS), then L9 items 1-5 |
| B (munitions, rings, effects) | MachineBrigade-art2 | L4 munition behaviour and flares (incl. Mount_Flare on models, the delayed-damage bug), L5 warning rings, L6 effects lifetimes, then L9 item 6 |
| C (audio) | MachineBrigade-art3 | L7 audio diagnosis and rebuild, metrics, then L9 item 8 |
| lead + one lane later | | L8 model standard and scan (the lead renders the sheets with ModelPreview; an agent scores and fixes 15), L9 item 7, L10 PDF and report |

Data file overlap: lane A owns `weapons` in balance.json; lane B keeps its data in its own blocks (warning rules,
flare counts) and touches weapons only through lane A's merge; lane C touches no balance data.

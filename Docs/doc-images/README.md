# Design review pictures

The design review PDF's screenshots and render pages (`shots/`, `r6/`), recovered on 2026-10-01 from the 264-page PDF
of 30/09 after the original image folder was lost. Build with an image folder holding these two folders plus a copy
of `Docs/ui-screens` as `ui/`:

    python Tools/docs/build_doc.py <game.json> <imgdir> <out.pdf>

`game.json` comes from the ExportGameDoc fixture (MB_EXPORT=<path>, run with -testFilter ExportGameDoc).

Full fix L10 (sections 10j and 21 A-E, `Tools/docs/fix_full.py`) also reads, when present (a missing picture is a grey
"shot pending" box naming the file):

- `fx/` = a copy of `Builds/effect_shots` (`MachineBrigade.Editor.EffectShots.FxBatch`): `fx/index.json` and
  `fx/<key>/fire_0s.png`, `fire_0.2s.png`, `fire_1s.png`, `impact_0s.png`, `impact_0.5s.png`, `impact_2s.png`,
  `impact_10s.png`, `impact_30s.png`, plus `salvo.png` and `salvo_impact.png` for a multi-barrel gun; `<key>` is
  `tier_T0` ... `tier_T5` or a weapon id.
- `scan/` = a copy of the runner's `Builds/scan` (ModelScan: `<model>.png`, `<model>_old.png`).
- `scan_after/` = a copy of the runner's `Builds/scan_after` (ModelScan after the L8 rebuilds).

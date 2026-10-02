# Pass 8 model scan: how to run it (lead)

Standard: `Docs/models/MODEL_STANDARD.md`. Real sizes: `Docs/models/reference_dimensions.md`. Decisions: DECISIONS
"Sửa lỗi tổng hợp L8 prep". Static scores (already committed): `static_scores.csv` (230 models).

## Commands, in order

0. Mirror the worktree into the runner as usual (`C:\Users\Winka\Projects\MachineBrigade-runner`); no Unity open on it.

1. The old GLBs (before prompt 27's first wave, 07444b1) into the runner's `Builds/scan_old_models/`:

   ```
   python Tools/models/scan_prep.py --old --repo C:/Users/Winka/Projects/MachineBrigade-runner --dry-run   # list only
   python Tools/models/scan_prep.py --old --repo C:/Users/Winka/Projects/MachineBrigade-runner
   ```

   About 180 models (every scanned model prompt 27 rebuilt, plus sky_gunship and every tower, structure and HQ, kept
   when the file existed at 07444b1 and changed since; ~48 are new since and have no old copy). Uses `git show` +
   `git lfs smudge` (fetches LFS objects from the remote if the runner lacks them). Writes `old_models.tsv` (why each).

2. The Unity scan, one batch run in the runner (with graphics, no `-nographics`):

   ```
   cd /c/Users/Winka/Projects/MachineBrigade-runner
   env -u ELECTRON_RUN_AS_NODE "/c/Program Files/Unity/Hub/Editor/6000.6.3f1/Editor/Unity.exe" -batchmode -force-d3d11 \
     -force-device-index 1 -quit -projectPath . -executeMethod MachineBrigade.Editor.ModelScan.RenderBatch \
     -logFile Builds/scan.log
   ```

   Options: `-mbScan "id,id"` (only these), `-mbScanOut <dir>` (default `Builds/scan`), `-mbScanOld <dir>` (default
   `Builds/scan_old_models`), `-mbScanNoOld`, `-mbScanZoom 9` (the closest zoom instead of the default 19).
   Expected 8-15 min (~230 sheets + ~180 old). Check the log ends with `[ModelScan] wrote N sheets`, that
   `Builds/scan/index.json` has an empty `missing` list, and that `Assets/ScanOld` is gone (it is git-ignored anyway).
   Output: `<id>.png` (1536 x 512: play / side / rear) and `<id>.json`; `<id>_old.png/.json` for the old ones.

3. The scoring pass (an agent, from the worktree; it reads the sheets in the runner):

   ```
   python Tools/models/scan_prep.py --scan-dir C:/Users/Winka/Projects/MachineBrigade-runner/Builds/scan          # rescore with the LOD1 shares
   python Tools/models/scan_prep.py --index --scan-dir C:/Users/Winka/Projects/MachineBrigade-runner/Builds/scan  # visual_scores.md
   ```

   Then the agent opens each sheet (and its `_old` sheet), fills `visual_scores.md` (visual grade + concrete reason,
   old vs new, final grade per MODEL_STANDARD section 4), restores the old GLB or rebuilds where the new one scores
   lower (sky_gunship, every structure, tower and HQ first), and rebuilds at most 15 Kém models (worse-than-old first,
   starter-deck vehicles, common towers, early bosses) with before / after sheets (`-mbScan "<ids>"`). For the PDF's
   section E, copy the sheets it uses into `Docs/doc-images/` (PNG is LFS-tracked).

## Static score (2026-10-02, before the scan)

230 models: Tốt 24, Cần sửa 104, Kém 102. Over budget 57 (worst: heavy_turret_b +199 %, drone_hangar_b +144 %,
heavy_turret_a +142 %, heavy_turret +138 %, headquarters +136 %), under the minimum 92 (mostly trucks under 3,000 and
jets under 4,000). Missing named parts: 146 models, 409 parts (mantlet, idler, glass, tail surfaces are the common
ones; a part modelled inside a merged node is cleared by the visual pass). Muzzles short on 23 models, mounts on 14,
Mount_Flare short on all 16 flare units (lane B adds them), Mount_APS missing on 18, boss part nodes on 3. Proportions
off by more than 10 % on 42 models (23 by more than 25 %, mostly ships, bosses and aircraft drawn shortened).

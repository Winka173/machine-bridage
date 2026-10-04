# Applying MB_FINAL_2026_10_04 (owner 04/10: this bundle wins over everything)

Files: BAO_CAO_FINAL.md, VIEC_CHO_AGENT_FINAL.md (agent rules), Manifest_FINAL.json (226 changes), Machine_Brigade_FINAL_Recheck.xlsx.
Rule: per manifest row check expected_before; equal -> apply new_value; different -> CONFLICT row in
Docs/balance/final/CONFLICTS.md with our current value, and apply the bundle's derivation formula to the current
entity (owner: "data mà bên đó chưa cung cấp thì sửa theo công thức bên đó"). Never invent numbers. Every value ->
Docs/export/CHANGES.md section "MB_FINAL". Keep vision/stealth/radar/reveal data.

Split (3 lanes, opus):
- F1 data: all non-boss-override rows (vehicles hp/modelSize/rank/aps/towerRangeAura, weapons damage/cooldown/
  splash/edge, bigAttacks, aiBehaviour Laser.overwhelmed Smoke->Shift, matchRules catchUp/timeLimit texts) + the
  bundle formulas for entities the bundle does not know (Theia, Coeus, pt14_* weapons, new sea/space weapons:
  boss HP by chapter TTK, heavy-gun fire-rate -30 % / damage per shot up, aircraft HP bands).
- F2 boss range: new data layer bossWeaponOverrides[boss][weapon] {groundMinReach, minRange, maxRange} in the Sim,
  apply the 108 rows; weapons since replaced (nyx boss_railgun -> nyx_ags_155, hyperion coilguns -> 155 twins,
  new ventral guns/missiles) get the bundle's rule (min from barrel geometry, max ~3.2x min, cap 300 m;
  close-defence min ~0).
- F3 code: 10 campaign fixedDeck MAKE_LATER -> READY with their specialRules implemented; Survival 10 waves ~60 s;
  weekly mutator rule (seed year*100+ISO week, 2 distinct, excludes, one pressure + one rule-change); VFX tier map
  from calibre/warhead (incl. Scylla/Nyx Kalibr -> Large T4, lead decision).
Lead decisions on open questions: player Buk/Patriot speeds keep (bundle has no row); stealth jet / light-vehicle
gate cap / rigid trains / waking-barrel clip: no change now; uncovered dead zones: solved by F2.
After merge: ExportGameDoc + pack rebuild + export checks; tests and replay hashes wait for the owner's word.

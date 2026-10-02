# Cau_hoi_chu_du_an (prompt 35)

Questions for the owner from passes 0-3 (lane A, 2026-10-03). Nothing here was changed in data; each line says what
was done meanwhile.

1. **Ixion's size and tyres.** modelSize 26 m is x1.26 of the BelAZ-75710 (prompt 35 asks bosses x1.3-1.5); the real
   truck has eight tyres, the sheet and the parts data six. Kept 26 m and six tyres. Enlarge (modelSize) or add tyres
   (parts data)?
2. **ZU-23 barrels.** The ZU-23-2 fires two barrels; `zu23` has no `barrels` in balance.json (1 muzzle). The model has
   two barrels and one `Muzzle_main`. Set `barrels: 2`?
3. **Tower faction style.** A tower draws one model for both sides. The rocket turret was built in the Accord style
   (field-built: earth, timber, sandbags), since the player builds it from chapter 1. A Hegemon (cast concrete,
   modular) twin needs a second model id per tower (data). Wanted?
4. **Tower branches.** rocket_turret_a / _b still use their old builder, so the upgraded tower looks unlike the new
   base. Rebuild branches together with their base in wave 1 (proposed)?
5. **Two pilots just under 80 after four rounds** (Ixion 79.7, rocket turret 79.6, NEEDS_HUMAN). Both pass every hard
   gate; the soft score is pulled down by the gold's detail density (the boss gold is three trains; the tower gold
   is dense in railings and ladders). Options: accept them on your look at the sheets; or let each boss frame
   (ground, rail, air, sea) have its own gold.
6. **Triangles.** The pilots are over their class maximum (Ixion 35.7k / 20k, technical 7.4k / 5k, rocket turret
   9.1k / 4k). Kept (your rule of 02/10). Is that fine on phones for units seen in numbers (technicals, towers), or
   should waves stay under 1.5 x the maximum?
7. **mara_behemoth** draws `behemoth` by data (prompt 31's). Give it a model id of its own?
8. **The V2 gold models fail the new hard gates on names only** (no node named mantlet / idler on the MBT, no
   Mount_aam on the Su-27, Apache's rocket muzzles and flare count by the old counting). Rename in the waves, or let
   the gate accept merged nodes as MODEL_STANDARD section 4 does for the visual pass?
9. **Builds are not byte-identical** (any builder, e.g. aa_gun_tower): the glTF exporter writes one index accessor in a
   different order run to run; positions, normals and colours are identical. Fix the exporter order (pipeline work)?
10. **Ixion's "(model tạm)" note** is in the balance spreadsheet's shape cell (unit_sheet.json is generated from it),
    so the inventory still lists Ixion as a stand-in. Remove the note in the spreadsheet?
11. **Materials per model.** Section 9 asks for 4-6 materials per model; the kit's material separation (MODEL_STANDARD
    rule 3: paint, steel, rubber, glass, lamps, markings) and the colour-zone gate (boss >= 6) give the pilots 11-17
    (the old files 8-11). The runtime merges meshes per material and glb_check's draw-call caps pass. Keep the
    separation, or merge to 6 at integration (fewer colours, cheaper draws)?

# C05: flare baseline (prompt 29, read only)

The sheet "Pháo sáng" column "Hồi chiêu hiện tại" against the data: a vehicle's flares are its `Flares` skill
(`skills[]`), whose cooldown is shared (heli_flares 20 s, jet_flares 16 s, bomber_flares 11 s).

All 23 rows match: attack_helicopter 20, gunship_heli 20 (heli_flares); fighter_jet, interceptor_jet, stealth_fighter,
attack_jet 16 (jet_flares); swarm_carrier, glide_bomber, stealth_bomber, heavy_bomber, sky_gunship 11 (bomber_flares);
the other 12 have no flare skill ("—"). No B2-FLR bundle is in conflict on its baseline. The charges are 0 everywhere
(no charge system yet: S06).

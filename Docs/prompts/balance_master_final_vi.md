# 06/10 owner prompt (verbatim)

tiếp tục nhưng làm cái này trước @Machine_Brigade_BALANCE_MASTER_UPDATE_FINAL.md
implement the attached file:

Treat it as the single source of truth for this balance pass.

IMPORTANT:
- Current XLSX/MD exports may be stale.
- Change canonical/runtime source first, then regenerate exports.
- Preserve previously locked combat rules.
- DO NOT change boss armour.

Execution order:

1. Apply the FINAL projectile-speed values in the master.
2. Audit full inheritance/runtime pipeline for missile, rocket, mortar, howitzer and MLRS families.
3. Preserve boss-specific intentional exceptions:
   - boss/ship `sam_post` = 80 m/s
   - Nemesis `sam_battery` = 95 m/s
   - boss Grad/rockets = 65 m/s
4. Apply bomb and aircraft buffs.
5. Apply conservative ground-vehicle buffs.
6. Apply tower/building durability and damage changes.
7. Apply main/mini boss HP rules plus Nyx/Scylla output changes.
8. Apply fire-support pass:
   - 120 mm mortar / AMOS damage +10%
   - 240 mm mortar splash 9 -> 10, damage unchanged
   - howitzer coverage ~+10%, raw damage unchanged
   - MLRS coverage +8–10%, raw damage unchanged
   - cluster coverage +10%
   - TOS unchanged
   - artillery_barrage support ~+10% total strike value
9. Audit structure repair throughput and fire-support resupply.
10. Run the full regression matrix in the master.
11. Regenerate all relevant generated files/docs/reports.
12. Return a detailed old->new implementation report.

Do NOT auto-change:
- boss armour;
- Titan stats;
- wall HP;
- TOS combat stats;
- Nemesis damage;
- SAM/AAM damage unless fixing a concrete bug;
- direct tank/AP/APFSDS projectile speed;
- cruise missile outside the ~65–70 m/s target band.

Mandatory pipeline audit:

canonical source -> family inheritance -> variant override -> runtime effective value -> generated export

Mandatory mismatch candidates:
apkws_rocket, anti_ship_missile, Kornet variants, Buk/Patriot/S-400 player families, boss sam_post, Nemesis sam_battery, boss Grad/rocket family, guided artillery

Mandatory final report:
- all changed IDs; exact old->new values; runtime-effective projectile speeds; min/half/max flight times; legal max-geared projectile speeds; APS/CIWS/flare/jammer regression; AI lead/intercept regression; bomb/aircraft results; ground/tower/structure durability results; boss TTK/pressure results; fire-support effectiveness results; support-card artillery barrage separated from scripted enemy barrage; repair/resupply audit; generated-file list; stale-value scan; explicit confirmation that boss armour was unchanged.

Use the attached master file for every exact value and rule.

(Attached spec copied to Docs/prompts/balance_master_final_spec.md.)

# Machine Brigade — Full Game QA / Balance Test Guide

## 0. Purpose

This is the master regression guide for testing units, weapons, structures, bosses, AI, economy, equipment, maps and game-state systems.

Core rule:
Every entity must be tested for:
1. what it is supposed to beat;
2. what it is supposed to be even against;
3. what it is supposed to lose to;
4. survivability under incidental pressure;
5. CP/value efficiency;
6. AI correctness;
7. interaction with maps, formation, logistics and equipment;
8. presentation/readability;
9. deterministic/regression stability.

Never judge an entity from one duel alone.

## 1. Universal test conditions

For every important balance test record:
- build/commit;
- canonical data version;
- random seed;
- map;
- spawn positions;
- distance;
- facing;
- terrain;
- unit IDs and quantities;
- gear loadout;
- CP value;
- AI/manual control;
- time to first shot;
- TTK;
- survivors;
- damage by source;
- ammo consumed;
- reload/rearm downtime;
- target switches;
- pathing failures;
- warnings/errors.

Run important stochastic tests with enough seeds to expose variance. Prefer deterministic seeds for regression.

### Gear states

Use:
- Naked: no equipment bonuses.
- Realistic: representative legal player build.
- Max legal: all relevant legal bonuses at BuildCap.

Show effective and wasted/overcap values where applicable.

## 2. Reference target ladder

Use stable reference opponents for cross-patch comparison.

Ground:
- Very light: scout/technical.
- Light: `armored_car`.
- Light-medium: `ifv` / `light_tank`.
- Medium-heavy: `main_battle_tank`.
- Heavy: `heavy_tank`.
- Superheavy: `titan_tank` or equivalent.
- Specialist Armour4/5 test: heavy/superheavy and boss part, not random light targets.

Air:
- Light: recon drone / scout heli.
- Medium: attack heli / strike drone / fighter.
- Heavy: attack jet / bomber / gunship according to role.

Naval:
- Light: patrol/hover/missile boat.
- Medium: corvette/frigate.
- Heavy: destroyer/cruiser.
- Capital: battlecruiser/battleship when implemented.

Structures:
- Small combat tower.
- Medium combat tower.
- Large combat tower.
- Utility structure.
- HQ/strategic objective.

Boss:
- representative mini boss.
- representative main boss.
- special mechanic boss such as Earth Borer.
- naval boss where relevant.

## 3. Ground vehicle suite

For every ground combat vehicle test:

### Role matchup
- one lighter target;
- one equal-tier target;
- one heavier target;
- intended prey;
- intended counter;
- structure/tower if the role supports it.

### Facing
For direct ground weapons:
- front;
- side;
- rear;
- roof only through valid top-attack mechanics.

Use the locked penetration tables. Preserve fractional Pen/Armour interpolation.

### Survivability
Test against:
- MG/autocannon incidental fire;
- same-tier main gun;
- higher-tier main gun;
- edge splash;
- direct explosive hit;
- small boss secondary;
- heavy boss direct attack.

Cheap units may survive incidental/edge pressure, but should not survive major heavy boss direct attacks by design.

### Group scaling
Run:
- 1v1;
- 3-unit squad;
- 5-unit squad;
- larger formation where spam risk exists.

Check focus fire, overkill and collision.

### Expected role failures
Examples:
- TD should suffer against fast light swarm at close range.
- artillery should fail if flanked.
- scout should lose frontal combat.
- SAM vehicle should be weak against direct ground attack.
- breacher should not become best tank killer.

## 4. Aircraft suite

Test the entire sortie, not just weapon DPS.

Record:
- ingress time;
- time inside AA envelope;
- payload delivered;
- damage delivered;
- survival;
- egress;
- rearm time;
- second-sortie availability.

Matchups:
- recon drone vs cheap AA;
- scout heli vs AA vehicle;
- attack heli vs AA vehicle / SHORAD;
- strike drone vs AA gun / SAM;
- fighter vs fighter/AAM;
- attack jet vs SHORAD/SAM;
- bomber vs medium/large towers;
- gunship vs layered AA.

Check:
- flare/jammer;
- AAM/SAM flight time;
- missile guidance;
- overshoot/circling;
- AA target selection;
- air cap;
- rearm downtime.

## 5. Naval suite

For each ship:
- test lighter/equal/heavier hull;
- test intended specialist target;
- test its counter;
- test shore structure if allowed;
- test aircraft/missile defence if relevant.

Measure:
- broadside/orientation effects if any;
- time to preferred range;
- turn/path reliability;
- salvo readability;
- missile interception;
- overkill;
- target selection;
- CP efficiency.

Naval formation:
- 3 ships;
- 5 ships;
- mixed escort group;
- narrow lane/choke;
- wreck obstruction.

No reverse/turn-radius violations for units configured with ship navigation constraints.

## 6. Tower and structure suite

Test:
- cheap swarm;
- mid assault;
- heavy assault;
- artillery;
- bomber/air attack;
- specialist siege/breacher;
- repair support;
- rebuild economy.

For combat towers record:
- primary weapon DPS;
- target selection;
- uptime;
- time under focus fire;
- rebuild CP and rebuild time;
- repaired EHP;
- stacked tower interaction.

AA/SAM towers:
- test every air class;
- do not judge by ground DPS.

Utility structures:
- measure utility delivered over time, not weapon DPS.

## 7. Weapon/projectile suite

### Direct cannon / kinetic
Test Armour 0–5:
- front;
- side;
- rear;
- overpenetration at Pen differences +3/+4/+5.

### Shaped charge / ATGM
Test:
- normal armour;
- top attack with roof armour only;
- reactive armour;
- tandem interaction if implemented;
- APS;
- min range;
- moving target;
- guidance after speed changes.

### SAM/AAM
Test:
- light/medium/heavy aircraft;
- flare/jammer;
- minimum range;
- launch-to-impact time;
- overshoot;
- interception;
- fragmentation splash cap.

### Mortar/howitzer
Test:
- min range;
- max practical range;
- actual arc;
- moving target;
- single target;
- cluster;
- counterbattery;
- splash footprint.

### MLRS
Test:
- coverage;
- salvo spacing;
- cluster coverage where applicable;
- moving concentration;
- reload/resupply;
- overkill.

### Cruise
Test:
- warning;
- visible travel;
- interception;
- 10/11/12/14/16 m footprint according to weapon class;
- VFX/warning marker agreement.

### Ballistic
Test:
- speed target;
- visible flight;
- splash 14 m for locked tactical ballistic case;
- warning;
- impact scale;
- interception if allowed.

### Energy/laser
Test:
- ramp;
- tracking break;
- Energy bypass shield rule;
- effective sustained DPS.

## 8. Fire-support suite

Every fire-support platform:
- single target;
- dense group;
- tower/structure;
- moving target;
- counterbattery target;
- minimum range;
- resupply cycle;
- shoot-and-scoot.

Keep dedicated locked fire-support changes:
- 120 mm mortar +10% damage.
- AMOS +10% damage.
- 240 mm mortar damage KEEP, splash 10 m.
- howitzer raw damage KEEP, coverage +10%.
- standard MLRS damage KEEP, coverage +8–10%.
- cluster MLRS bomblet damage KEEP, coverage +10%.
- TOS/thermobaric combat stats KEEP.

## 9. Boss suite

Never test only boss TTK.

Use at least:
- light army;
- balanced army;
- heavy army;
- anti-boss specialist army;
- air-heavy army;
- artillery-heavy army where map permits.

Record:
- survivors;
- lost CP;
- boss TTK;
- phase durations;
- damage by boss source;
- number hit by each big attack;
- telegraph reaction success;
- weakpoint/component lifetime;
- escort contribution;
- APS/CIWS interaction.

### Earth Borer controlled test
Always support:
A. fixed exact roster;
B. fixed CP budget;
C. fixed count/role mix.

Record burrow:
- warning;
- units inside impact radius;
- spacing;
- escape vectors;
- damage;
- stun;
- path reservation conflicts.

Do not nerf the boss from one composition regression.

## 10. AI suite

Every armed unit must satisfy the no-idle-armed-unit invariant when a valid combat action exists.

Test:
- target feasibility;
- target value;
- role priority;
- overkill reservation;
- stickiness;
- firing-lane blockage;
- reposition;
- min-range handling;
- threat-specific formation;
- objective-aware targeting;
- ammo-aware behavior;
- counterbattery;
- shoot-and-scoot;
- interception;
- pursuit discipline;
- opportunity fire.

Failure examples:
- TD chases scouts while a heavy target is valid.
- artillery drives into minimum range.
- five heavy weapons overkill a 5% HP light target.
- AI stacks a formation inside a boss AoE warning.
- AA ignores a high-value air threat to shoot ground.

No morale, panic or retreat-by-health.

## 11. Formation/pathing/traffic suite

Test:
- solo;
- 3;
- 5;
- 8+ units;
- mixed-size formation.

Terrain:
- open field;
- road;
- bridge;
- choke;
- urban corner;
- ridge/slope;
- shoreline/sea lane;
- wreck-filled lane.

Record:
- stuck time;
- queue length;
- reservation failures;
- collision loops;
- U-turns;
- formation compression;
- time to regain formation;
- firing-lane obstruction.

## 12. Terrain/map suite

Verify:
- LOS;
- projectile obstruction;
- firing position;
- min-range geometry;
- shoreline attack eligibility;
- spawn safety;
- objective access;
- route diversity;
- choke behavior;
- no terrain semantic hidden buffs unless explicitly designed.

## 13. Economy/CP suite

Measure:
- HP/CP;
- effective DPS/CP;
- useful lifetime/CP;
- objective pressure/CP;
- specialist value/CP;
- repair/supply dependence;
- rearm downtime;
- vehicle/air cap opportunity cost;
- kill refund;
- rebuild CP/time for towers.

Run both:
- fixed roster;
- fixed CP budget.

This catches cases where raising cheap-unit CP reduces army body count enough to make actual performance worse.

## 14. Equipment suite

Test:
- naked;
- realistic;
- max legal BuildCap.

Verify:
- final caps after all sources;
- overcap is wasted;
- UI/debug reports effective and wasted values;
- VeteranCrew does not bypass BuildCap;
- ProjectileSpeed gear stays within +4/+6/+8/+10 and BuildCap 30%;
- no illegal stacking.

## 15. Repair/resupply/shield suite

Repair:
- percent max HP/s vs flat HP/s;
- mobile vs static;
- stacked repair;
- repair under fire.

Resupply:
- magazine depletion;
- full reload cycle;
- artillery/MLRS throughput;
- no infinite-fire bug.

Shield:
- normal damage;
- Energy bypass;
- recharge;
- multiple simultaneous attackers;
- shield-body destruction order.

## 16. Objective/mode suite

Test each unit in:
- capture;
- defend;
- escort;
- breach;
- hold;
- hunt;
- survival/waves;
- boss encounter.

A duel-balanced unit can still be useless in an objective mode.

## 17. Scripted/free/event unit suite

For CP=0 or scripted units:
- do not evaluate them as normal purchasable economy units;
- verify encounter strength;
- verify spawn safety;
- verify canonical balance changes do not accidentally overpower campaign scripts.

Examples include event/support units such as CP=0 transports/support entities.

## 18. Presentation/telegraph suite

For every dangerous attack verify:
- prelaunch cue;
- projectile visible;
- trail readable;
- impact VFX matches damage footprint;
- warning circle is not smaller than gameplay area;
- audio cue survives busy combat mix;
- no fog-of-war information leak.

Boss missile reporting:
PreLaunchWarning / ProjectileTravel / TotalReactionWindow.

## 19. Death/wreck suite

Test:
- death explosion;
- chain deaths;
- wreck collision;
- bridge/choke blocking;
- naval sinking;
- line-of-fire obstruction;
- cleanup time;
- low graphics still show collision-relevant wreck lifetime.

## 20. Save/load/pause/time-scale suite

Save during:
- reload;
- missile flight;
- aircraft rearm;
- repair;
- shield recharge;
- boss phase;
- Earth Borer burrow;
- artillery salvo.

After load verify:
- timers preserved;
- targets valid;
- no duplicated projectile/unit;
- no cooldown reset exploit.

Test pause and supported time scales.

## 21. Performance/stress suite

Stress combinations:
- 50–100 ground units;
- missile saturation;
- MLRS salvos;
- drone swarms;
- tower networks;
- boss + escorts;
- naval fleet + aircraft.

Record:
- simulation step;
- AI update time;
- pathfinding cost;
- projectile count;
- reservation count;
- memory growth;
- long-session degradation.

## 22. Determinism suite

For deterministic subsystems:
- same setup + same seed should reproduce equivalent results.

For variable systems:
- report distribution across seeds;
- never use a single run as final evidence.

## 23. UI/stat integrity suite

UI must show effective runtime values, not stale raw/export numbers.

Check:
- HP;
- CP;
- damage;
- Pen;
- reload;
- range;
- splash;
- projectile speed;
- capped equipment values;
- overcap/wasted amount.

## 24. Campaign regression suite

For every canonical unit change:
- search campaign usage;
- fixed decks;
- scripted waves;
- militia;
- allied reinforcements;
- boss escorts.

Run affected mission smoke tests before export regeneration.

## 25. Cross-system trigger matrix

When changing:

Projectile speed →
- guidance;
- APS/CIWS;
- warning/travel;
- AI lead;
- VFX trail.

HP/CP →
- fixed roster;
- fixed CP budget;
- campaign waves;
- boss survival.

Weapon damage/Pen →
- intended prey;
- intended counter;
- CP efficiency;
- boss parts;
- tower/structure matchup.

AI →
- combat activity;
- formation;
- targeting;
- objective behavior;
- performance.

Map topology →
- pathing;
- firing lanes;
- objective access;
- naval lanes;
- choke traffic.

## 26. Final release gate

A balance/content change is ready only when:
- canonical/runtime source is updated first;
- relevant unit-role tests pass;
- counter matchups still exist;
- AI uses the content correctly;
- no new HARD_FAIL validator appears;
- campaign regression passes;
- performance does not materially regress;
- exports/docs are regenerated after implementation;
- stale-value scan is clean;
- final report lists exact IDs and old → new effective values.

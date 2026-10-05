# MACHINE BRIGADE — MAP / VISUAL / VFX / AUDIO / MODEL MASTER SPEC
## Canonical improvement and validation specification for `06_ban_do` and `07_hinh_anh_am_thanh_model`

**Status:** MASTER REVIEW SPEC  
**Date:** 2026-10-04  
**Scope:** map data, tactical topology, naval routes, terrain/weather semantics, visual readability, VFX, model contracts, LOD/render budgets, audio event design, mixing, spatial audio, accessibility, QA and automation.  
**Source basis:** current Machine Brigade export package (`06_ban_do.xlsx/.md`, `07_hinh_anh_am_thanh_model.xlsx/.md`, `00_index.xlsx`) plus external research listed in Part Z.  
**Does not rebalance:** weapon damage, armour, boss HP, economy, AI tactics except where the map/presentation layer must expose metadata to those systems.

---

# 0. FINAL GOAL

The current repository already has unusually strong raw data:
- 100 map variants with geometry and sub-sheets;
- map audit metrics including path lengths, lane counts, chokepoints, sightline P95, artillery coverage and nav connectivity;
- SeaRouteGraph nodes and segments;
- tens of thousands of terrain-zone rects;
- weather visibility modifiers;
- 453 model records with validation data;
- VFX tiers and budgets;
- audio banks, loudness/peak metrics, sample battle mixes, envelopes and licensing information.

The remaining problem is **not lack of content**.

The main work is to turn existing content into four reliable systems:

1. **GameplayTopology** — semantic tactical information generated from map geometry and used by AI/pathing/mode logic.
2. **Combat Readability** — every important weapon/threat/state communicates its meaning consistently through visual/audio channels.
3. **Runtime Asset Contracts** — stable model nodes, budget discipline, LOD, destruction states and renderer/material rules.
4. **Audio Priority & Spatial Mix** — important cues always survive crowded battles while distant/background sounds virtualize gracefully.

The player should feel:
- maps are tactically legible;
- vehicles fit through routes they are sent through;
- ships turn like ships;
- dangerous attacks are readable before impact;
- large weapons feel large;
- audio remains intelligible in a 48v48 battle;
- visual/audio quality does not collapse performance.

---

# PART A — CURRENT REPOSITORY FINDINGS

## A1. Map data foundation

`06_ban_do` already exposes:
- map boundary/bounds;
- roads;
- rails and crossings;
- walls/gates;
- entry gates;
- bases and base slots;
- objectives/outposts;
- neutrals;
- terrain tags;
- map props/decor;
- landmarks;
- SeaRouteGraph nodes/segments;
- fortress layout;
- biome rules;
- weather;
- static map audit.

`Ban_do_do_tinh` already measures or imports:
- spawn/objective distance;
- route asymmetry;
- independent lanes;
- mandatory/optional chokepoints;
- sightline P95;
- artillery coverage;
- deployment/drop areas;
- defence-layer spacing;
- nav connectivity;
- map validation warnings.

Do not replace this system. Extend it.

## A2. Known map warnings

Some map variants currently carry warnings such as:
- `YELLOW sightline`
- `YELLOW exits`

These are not automatically bugs.

They require classification:
- `UNINTENTIONAL`
- `INTENTIONAL_ACCEPTED`
- `NEEDS_PLAYTEST`

No accepted warning should remain context-free.

## A3. Sea route foundation

The export contains:
- SeaRouteGraph nodes;
- SeaRouteGraph segments;
- shore, pier and naval route metadata.

This is adequate for a real naval movement layer, but route curvature and ship-size compatibility need to become first-class validation data.

## A4. Weather foundation

Current weather includes visibility scaling for:
- Clear
- Fog
- Night
- Overcast
- Rain
- Sandstorm
- Snow
- Storm

Keep those gameplay values unless explicitly rebalanced elsewhere.

This spec adds **presentation/acoustic metadata**, not new accuracy or damage penalties.

## A5. Model validation foundation

The model system already checks:
- dimensions;
- renderer count;
- triangle/vertex counts;
- runtime nodes;
- mesh topology warnings;
- material usage;
- moving parts;
- category budgets;
- mount/muzzle/part naming conventions.

This is a strong foundation.

## A6. Concrete model issues already visible

Examples worth fixing:

### `attack_jet`
Runtime gameplay nodes include Blender-generated suffix names such as:
- `Muzzle_missile.001`
- `Muzzle_rocket.001`

This should be replaced by stable semantic names.

### `cp_relay`
Renderer count exceeds the normal structure budget.

### `armored_bulldozer`
Normal model exceeds the listed ground normal triangle budget and slightly exceeds the vertex hard cap under the current audit.

These are examples, not the complete warning list.

## A7. VFX foundation

Current VFX data already defines:
- T0–T5 tiers;
- muzzle flash;
- lights;
- dust rings;
- pressure/wave effects;
- smoke/lifetime;
- camera shake thresholds;
- global concurrency/particle budgets;
- per-weapon VFX capture/reference data.

Do not replace tiering.

Add semantic clarity rules on top.

## A8. Audio foundation

The current system already contains:
- audio clips and banks;
- burst banks;
- per-clip loudness/peak/frequency metrics;
- size-tier aggregates;
- RMS envelopes;
- sample battle mixes;
- mixer groups;
- licensing/source records.

Current sample mixes show that crowded battles generate far more events than can or should be physically played at once.

Therefore:
> audio prioritization is not optional.

---

# PART B — RESEARCH PRINCIPLES ADOPTED

External research is used as design guidance, not as a reason to overwrite repo-specific gameplay.

## B1. Gameplay readability outranks spectacle

Adopt:
> Visual impact should broadly correspond to gameplay impact.

High-threat attacks can be visually/audio prominent.
Routine MG fire must not look or sound like a superweapon.

This follows the clarity hierarchy used in competitive game VFX design.

## B2. Hit/threat shape must communicate gameplay truth

Telegraphs and decals must represent:
- actual danger area;
- actual direction;
- actual timing;
- actual travel path when relevant.

Do not draw a huge circle for a tiny actual threat or vice versa.

## B3. Important information should survive clutter

In dense battles:
- critical warning cues stay;
- low-value ambient/repetitive sounds can virtualize/drop;
- noncritical particles can simplify;
- key hitboxes/telegraphs cannot disappear.

## B4. Multiple sensory channels

Any cue where missing it can cause serious gameplay loss should have at least:
- visual + audio

Optional:
- haptic

Do not rely only on:
- color;
- sound;
- controller rumble.

## B5. Stable runtime asset identifiers

Gameplay code should never rely on DCC-generated suffixes such as `.001`.

Names used by runtime contracts must be explicit, semantic and validated.

## B6. Measure performance, do not optimize blindly

Renderer count, state changes, particle overdraw, spatial-audio calculations and path/topology preprocessing should be measured with representative combat scenes.

---

# PART C — GAMEPLAY TOPOLOGY MASTER LAYER

Create a generated/cacheable layer:

```csharp
sealed class GameplayTopology
{
    GroundTopology Ground;
    NavalTopology Naval;
    AmphibiousTopology Amphibious;

    IReadOnlyList<TacticalChoke> Chokes;
    IReadOnlyList<TacticalLane> Lanes;
    IReadOnlyList<TacticalPosition> Positions;
    IReadOnlyList<StagingArea> StagingAreas;
    IReadOnlyList<SpawnClearZone> SpawnClearZones;
    IReadOnlyList<ShoreFireRegion> ShoreFireRegions;
}
```

This is generated from canonical map data.

Do not hand-author all tactical points unless necessary.

---

# PART D — CONNECTED COMPONENTS / DOMAIN ACCESS

For each map generate separate connected components:

```text
GroundComponent[]
NavalComponent[]
AmphibiousComponent[]
```

Every:
- spawn;
- objective;
- base;
- fortress layer;
- shoreline firing zone;
- naval lane;
- boss route

must resolve to relevant components.

## D1. Vehicle-size accessibility classes

Connectivity is not binary.

Generate passability for:

```text
Light
Medium
Heavy
SuperHeavy
Boss
```

A route that a jeep can use may not be valid for:
- Titan-class tanks;
- mobile fortress;
- boss-sized chassis.

For each critical path, validate:

```text
minClearWidth
minTurnSpace
maxSlope if slope mechanics exist
obstacle clearance
gate width
bridge width
```

---

# PART E — CHOKEPOINT SEMANTICS

Each tactical choke gets:

```csharp
struct TacticalChoke
{
    Bounds Area;
    float UsableWidthM;
    int MaxLightSideBySide;
    int MaxMediumSideBySide;
    int MaxHeavySideBySide;

    float EstimatedThroughput;
    bool OppositeTrafficAllowed;

    Bounds QueueAreaA;
    Bounds QueueAreaB;

    ChokeType Type;
}
```

Choke types:
- gate;
- bridge;
- street canyon;
- wall breach;
- river crossing;
- rail crossing;
- pier/harbor throat;
- natural terrain gap.

## E1. Capacity rule

Do not hardcode only one universal width threshold.

Derive:
```text
maxSideBySide =
floor(usableWidth / (vehicleWidth + separationMargin))
```

Use class median width for audit.

## E2. Queue safety

Queue areas should:
- not overlap spawn clear zones;
- not block objective capture area;
- not be in known impassable terrain;
- not force units into min-range traps.

---

# PART F — TRAFFIC LANES

Generate tactical lanes with:

```text
laneWidth
directionality
vehicleClassSupport
expectedTravelSpeed
chokeDependency
objectiveCoverage
trafficCapacity
parkingForbidden
```

Mark:
- major transit route;
- minor route;
- flank route;
- service/support route;
- boss corridor.

Fire-support parking should be strongly discouraged on a major transit lane.

---

# PART G — SPAWN / ENTRY FAIRNESS

Current entry-gate data is valuable but needs explicit anti-camp audit.

For every team spawn/entry:

```text
enemyDirectLOSAtSpawn
enemyDirectLOSAtExit
enemyArtilleryCoverageAtSpawn
spawnToFirstCoverM
spawnExitWidthM
alternateExitCount
spawnQueueCapacity
enemyRushETA
friendlyObjectiveETA
```

## G1. Required checks

A normal competitive map should not allow:
- direct long-range fire into the entire spawn exit at match start;
- a single blocked vehicle to seal the only exit;
- a spawn exit narrower than the intended largest normal vehicle;
- artillery coverage of all exits with zero response route unless explicitly asymmetric.

Intentional asymmetry must be documented.

---

# PART H — OBJECTIVE APPROACH TOPOLOGY

For each objective compute:
- primary approach;
- secondary approach;
- flank approaches;
- shortest approach;
- safest approach;
- heavy-vehicle-compatible approach;
- artillery-support region;
- defender fallback region.

This directly supports:
- Assault;
- Conquest;
- Escort;
- Siege;
- Hold;
- AI attack-package staging.

---

# PART I — STAGING / RALLY AREAS

Generate candidate staging areas.

Requirements:
- enough area for squad footprint;
- outside choke itself;
- reachable;
- not inside spawn clear zone;
- not inside immediate direct-fire threat if avoidable;
- not inside objective capture circle unless intended;
- route continues forward cleanly.

Suggested metadata:

```text
capacityLight
capacityHeavy
coverScore
threatExposure
distanceToObjective
lanesAvailable
```

---

# PART J — FIRING POSITIONS

Generate role-aware tactical positions.

## J1. Direct-fire position

Score:
```text
LOS quality
effective range band
cover/hull-down value
escape route
friendly lane obstruction
threat exposure
```

## J2. Artillery pocket

Score:
```text
objective coverage
approach coverage
min-range safety
direct-fire protection
counterbattery exposure
AA coverage potential
exit options
traffic conflict
```

## J3. Recon observation

Score:
```text
LOS area
objective visibility
approach visibility
risk
escape route
```

## J4. Hull-down candidate

Only when terrain geometry genuinely creates hull masking while preserving weapon LOS.

Do not label arbitrary ridges as hull-down.

---

# PART K — SHORELINE ENGAGEMENT TOPOLOGY

Critical for naval maps and procurement AI.

Create `ShoreFireRegion`:

```text
groundComponentId
shorelineSegment
minDistanceToNavalLane
maxDistanceToNavalLane
elevation
LOSQuality
coverScore
maxUsefulWeaponRange
```

The purpose is to answer:

> Can a ground unit physically occupy a reachable point from which its weapon can affect a naval target?

Do not confuse:
- "cannot enter water"
with
- "cannot influence water."

---

# PART L — NAVAL ROUTE MASTER RULES

Existing SeaRouteGraph becomes a true kinematic route network.

Every node/segment should expose or derive:

```text
width
depthClass if relevant
curveRadiusM
entryHeading
exitHeading
maxRecommendedShipLength
maxRecommendedShipRadius
passingAllowed
passingBay
bossSafe
broadsideRoomLeft
broadsideRoomRight
shoreThreatExposure
```

---

# PART M — NAVAL CURVATURE VALIDATION

For each ship class derive minimum practical turning radius from movement data.

Approximation:

```text
Rmin ≈ speed / angularSpeedRad
```

Use safety margin.

Audit every boss route:

```text
routeCurveRadius >= shipRmin * safetyFactor
```

Suggested initial safety factor:
`1.10–1.25`

Do not force a ship controller to solve impossible geometry.

## M1. Hairpin detection

Flag:
- sudden heading changes;
- node spacing too short for turn;
- route segment that causes bow to collide with shore/wall during legal turn.

## M2. Broadside space

At likely combat segments ensure enough lateral water for:
- route adherence;
- safe heading correction;
- broadside offset.

---

# PART N — NAVAL PASSING / TRAFFIC

Create:
- passing bays;
- no-overtake zones;
- one-way conflict zones;
- boss-priority corridors.

A large boss should not be forced into:
- reverse;
- three-point turn;
- collision jitter.

---

# PART O — WALL / GATE / BREACH METADATA

For every destructible wall/gate compute:

```text
blockedRouteIds
pathCostReductionOnDestroy
heavyAccessGained
objectiveAccessGained
alternateRouteExists
defensiveTowerCoverage
```

This enables:
- Breacher AI;
- Siege target priority;
- player-facing tactical UI if ever desired.

---

# PART P — TERRAIN SEMANTICS

The repo already has dense terrain tagging.

Map tags into semantic fields:

```csharp
struct TerrainSemantics
{
    float MovementCost;
    float Traction;
    float Concealment;
    float VisualCover;
    float DirectFireCover;
    float ArtilleryExposure;
    float MineSuitability;
    float HullDownPotential;
    float LargeVehiclePenalty;
}
```

Do not automatically turn these into combat buffs.

They are primarily:
- pathing;
- AI positioning;
- presentation;
- optional detection/visibility hooks if already supported.

---

# PART Q — WEATHER PRESENTATION LAYER

Keep current visibility multipliers.

Add non-balance presentation metadata:

```text
FogDensity
AmbientLight
Cloudiness
RainIntensity
SnowIntensity
WindStrength
WindDirection
LightningIntensity
DustIntensity
ContrailVisibility
MuzzleFlashVisibility
AmbientAudioProfile
ReverbProfile
LowpassEnvironmentAmount
```

## Q1. Weather readability

Weather must not erase critical telegraphs.

Examples:
- red danger decal cannot vanish in snow/desert;
- projectile trail must remain readable in fog;
- night muzzle flash can be brighter but must not become photosensitive strobe spam.

---

# PART R — MAP VISUAL LANGUAGE

Each biome should have:
- terrain palette;
- silhouette palette;
- navigation landmark language;
- objective readability;
- edge/boundary language;
- traversable/non-traversable distinction.

Important:
> Players should read routeability from the environment without memorizing hidden collision.

Examples:
- passable gap visually open;
- impassable rubble looks substantial;
- shallow/usable shore visually differs from cliff shore;
- destructible wall differs from permanent boundary.

---

# PART S — LANDMARKS / ORIENTATION

Landmarks are not only decoration.

Ensure every large map has:
- at least 3 strong macro landmarks;
- distinct silhouettes;
- different compass quadrants;
- visibility from multiple route contexts.

Avoid:
- four identical towers serving as "landmarks";
- landmark clutter that looks like objectives.

---

# PART T — MAP READABILITY QA

Test every map at:
- gameplay camera normal zoom;
- maximum tactical zoom;
- combat with smoke;
- weather variants;
- color-vision simulation;
- low graphics preset.

Validate:
- objective readable;
- team ownership readable;
- threat decal readable;
- road/gate/breach readable;
- shallow/deep/non-navigable water distinguishable if relevant.

---

# PART U — MAP AUDIT WARNING GOVERNANCE

Every map warning record gets:

```text
warningId
severity
metric
value
threshold
status
owner
acceptedReason
lastReviewedVersion
```

Status:
```text
OPEN
FIXED
ACCEPTED_INTENTIONAL
PLAYTEST_REQUIRED
```

Never leave perpetual `YELLOW` with no explanation.

---

# PART V — MAP AUTOMATION / GENERATED OUTPUT

Recommended generated artifacts:

```text
GameplayTopology.json
MapConnectivity.json
TacticalPositions.json
NavalRouteAudit.json
SpawnFairnessAudit.json
MapWarningRegistry.json
```

These are generated, not hand-authored authoritative data.

Canonical map JSON remains authoritative geometry.

---

# PART W — MODEL RUNTIME CONTRACTS

Gameplay-dependent model nodes require a hard schema.

## W1. Stable naming

Forbidden:
```text
Muzzle_main.001
Mount_gun.002
Part_radar.001
```

Required:
```text
Muzzle_main_L
Muzzle_main_R
Mount_ciws_fore
Mount_ciws_aft
Part_radar
```

Suffix may exist internally for non-runtime cosmetic nodes, but runtime lookup must not depend on it.

## W2. Validator hard fail

Hard fail if:
- required muzzle missing;
- required mount missing;
- required boss part missing;
- duplicate runtime semantic ID;
- gameplay runtime node uses DCC suffix;
- node exists but transform hierarchy makes aiming impossible.

---

# PART X — MODEL AIM / PIVOT CONTRACT

Every aimed weapon must declare:

```text
aimMode = Free | Hull | FixedArc
pivotNode
muzzleNodes[]
yawMin
yawMax
pitchMin
pitchMax
```

Model and gameplay data must agree.

For freely rotating turret:
- pivot orientation must be correct;
- muzzle follows pivot;
- hull does not need to rotate to aim inside arc.

For hull-fixed weapon:
- mark `HullAim`.

This is essential for the new boss/naval AI.

---

# PART Y — MODEL PART / DAMAGE STATE CONTRACT

Important breakable boss/vehicle parts should expose:

```text
Part_* node
damageStateSupport
destroyedVariant or hide/break rule
VFX attachment points
```

Suggested states:
- Healthy
- Damaged
- Critical
- Destroyed

Not every cosmetic prop needs four meshes.

Use shader/material/VFX states where cheaper.

---

# PART Z — MODEL PERFORMANCE BUDGETS

Keep existing per-category budgets.

Add enforcement policy:

## Z1. Hard cap
Must fail unless explicit owner exception.

## Z2. Soft budget
Warning requiring review.

## Z3. Renderer/material priority

Renderer count deserves high attention because draw/render-state work can be CPU-sensitive.

Prefer:
- shared materials;
- renderer merging for tiny static sub-parts;
- instancing for repeated props;
- category-appropriate batching;
- no unnecessary unique material instances.

Do not merge everything blindly:
- preserve culling granularity;
- preserve moving parts;
- preserve destructible parts.

---

# PART AA — LOD POLICY

Every common/high-frequency model category should have appropriate LOD behavior.

Recommended:

## Vehicles
- LOD0: current normal/HD where applicable
- LOD1: 50–70% triangle cost
- LOD2: 20–35%
- distant impostor/simplified only if required by scale

## Large boss
Preserve silhouette and weapon mounts longer.

## Small props
Aggressive LOD or instancing.

## Foliage
Use distance-based simplification; avoid expensive alpha overdraw when filling screen.

LOD switching must not:
- remove visible weapon barrel too early;
- alter collision;
- change gameplay silhouette in a misleading way.

---

# PART AB — MODEL OUTLIER FIX STRATEGY

## `attack_jet`
Priority:
1. rename stable runtime muzzle nodes;
2. reduce renderer count if possible without breaking mounts/parts.

## `cp_relay`
Reduce renderer count by merging:
- repeated small static details;
- same-material props;
- noninteractive micro meshes.

## `armored_bulldozer`
Trim:
- invisible/internal faces;
- overly dense small details;
- duplicate geometry.

Preserve:
- blade silhouette;
- tracks/wheels;
- breacher identity;
- runtime mount/part nodes.

---

# PART AC — VFX CLARITY HIERARCHY

Adopt a presentation hierarchy:

```text
P0 Lethal / superweapon / must-react
P1 High threat / strong CC-like battlefield denial
P2 Heavy weapon / major damage
P3 Normal weapon
P4 Minor support / MG / cosmetic
```

Visual attention should roughly follow this.

Do not let:
- routine tracer
outshine:
- incoming boss superweapon.

---

# PART AD — VFX SHAPE LANGUAGE

Create consistent visual grammar.

## Direct kinetic
- sharp impact;
- sparks/debris;
- directional streak;
- minimal lingering cloud compared with HE.

## Shaped charge
- concentrated flash;
- directional jet impression;
- localized hot impact.

## HE
- broad blast;
- dust/smoke volume;
- clear radial impact.

## Fragmentation
- lighter broad burst;
- visible fragment/spark impression;
- anti-air/drone readability.

## Fire
- sustained flame;
- persistent burning state.

## Energy
- distinct coherent beam/arc/pulse language;
- must not be confused with conventional tracer.

Do not depend on color alone.

---

# PART AE — TOP ATTACK READABILITY

Top Attack is now mechanically meaningful and needs its own communication.

Differentiate:
- direct ATGM;
- top-attack ATGM;
- loitering drone;
- guided bomb;
- unguided bomb.

Top-attack options:
- climb then dive trajectory;
- vertical approach marker;
- ground shadow/indicator;
- short unique warning;
- overhead impact direction.

Never show a top-attack warning for ordinary direct fire.

---

# PART AF — THREAT TELEGRAPH CONTRACT

Every high-threat attack defines:

```text
TelegraphLeadTime
TelegraphShape
ActualDangerShape
AudioCue
OptionalHapticPattern
CancelBehavior
ImpactCue
```

Telegraph must match:
- hitbox;
- travel time;
- timing.

If attack is cancelled:
- visual/audio telegraph must cancel/fade correctly.

---

# PART AG — TELEGRAPH PRIORITY / OCCLUSION

Critical danger indicators render above:
- smoke;
- decals;
- cosmetic debris

within reasonable rules.

Do not allow a cosmetic explosion cloud to hide the next lethal danger decal.

Optional:
- subtle outline/ground projection for high priority cues.

---

# PART AH — BOSS PRESENTATION

Boss combat must communicate:
- current phase;
- dangerous active weapon;
- broken parts;
- exposed weakpoints;
- shield/APS/radar state if gameplay-relevant;
- superweapon charge.

Avoid permanent excessive glow that makes active-state glow meaningless.

---

# PART AI — WEAPON SCALE PRESENTATION

Maintain and strengthen T0–T5 concept.

For larger tiers increase some combination of:
- muzzle flash;
- pressure;
- dust displacement;
- smoke volume;
- debris scale;
- screen-space presence;
- audio low-frequency/body;
- tail duration.

Do not simply increase every dimension linearly.

A T5 explosion should feel larger, but must still preserve visibility of other critical cues.

---

# PART AJ — PARTICLE / OVERDRAW BUDGET

Particle effects can become fill-rate heavy when smoke/dust fills large portions of screen.

Add metrics:
- average overdraw;
- peak screen coverage;
- concurrent transparent emitters;
- particle count;
- lifetime.

LOD/simplify:
- distant smoke;
- overlapping dust;
- repeated low-priority impacts.

Critical telegraphs should not be first to simplify.

---

# PART AK — CAMERA SHAKE

Camera shake is presentation, not information.

Provide:
- master camera shake intensity;
- option 0–100%;
- reduced motion preset.

Rules:
- T0/T1 little or none;
- T3+ scaled;
- repeated impacts accumulate with clamp, not additive unbounded shake;
- boss barrage cannot cause continuous nausea.

Camera shake may support a cue but must never be the only cue.

---

# PART AL — PHOTOSENSITIVITY

Audit:
- repeated muzzle flashes;
- lightning;
- energy weapons;
- boss phase effects;
- UI warning flashes.

Mitigations:
- clamp flash frequency;
- avoid large high-contrast full-screen flashes;
- reduce saturated red rapid flashing;
- provide reduced-flash/reduced-effects accessibility setting.

Gameplay information must remain intact under reduced-effects mode.

---

# PART AM — COLOR / CONTRAST ACCESSIBILITY

Critical information cannot rely only on:
- red vs green;
- subtle hue differences.

Use combinations:
- color;
- shape;
- icon;
- outline;
- motion;
- label;
- audio.

Support configurable team/threat colors if UI system permits.

Telegraphs must remain visible across:
- snow;
- desert;
- volcanic;
- urban;
- night/fog.

---

# PART AN — VISUAL LOW-PRESET CONTRACT

Low graphics must never remove:
- danger telegraph;
- projectile needed to dodge;
- objective marker;
- team identification;
- boss weakpoint state.

Low preset may reduce:
- particle count;
- smoke detail;
- reflections;
- debris;
- secondary sparks;
- ambient dust.

---

# PART AO — DESTRUCTION / WRECK VISUAL CONTRACT

Wreck visual state and nav/collision state must be synchronized.

State sequence example:

```text
Alive
DestroyedAnimating
BlockingWreck
PassableRubble
Removed
```

Each state defines:
- collider;
- nav obstacle;
- visual mesh;
- fire/smoke;
- salvage if applicable.

Never:
- invisible wreck still blocking;
- visible solid wreck with AI driving through it unless intentionally passable.

---

# PART AP — AUDIO EVENT PRIORITY

Define gameplay priority.

Suggested:

```text
P0 critical UI / lethal warning / boss superweapon
P1 incoming missile / incoming artillery / critical HQ alarm
P2 own heavy weapon / nearby heavy hostile weapon
P3 nearby normal weapons / impacts
P4 distant normal combat / engines
P5 ambience / repetitive MG tails / cosmetic
```

Exact implementation may use numeric priority.

Distance may modify priority, but P0 should not disappear because a nearby MG consumed all voices.

---

# PART AQ — AUDIO VOICE MANAGEMENT

Use:
- playback limits;
- priority;
- virtualization;
- distance-based priority;
- cooldown;
- aggregation.

Low-value distant sounds:
- virtualize or kill.

Important finite cue:
- must survive.

For looping engines/ambience:
- virtual voice can continue timeline and return smoothly.

---

# PART AR — AUDIO CLUSTERING / AGGREGATION

In a dense 48v48 battle do not play every MG shot individually.

Aggregate by:
- spatial cell;
- weapon family;
- time window;
- distance.

Example:
```text
12 distant MG emitters
→ 1–3 distant battle-cluster voices
```

Keep individually:
- player-owned selected unit;
- nearby threatening heavy weapon;
- critical incoming projectile.

---

# PART AS — AUDIO MIX BUSES

Recommended separate control groups:

```text
Master
Music
UI
Voice/Radio
CriticalWarnings
PlayerWeapons
CombatSFX
Engines
Ambience
```

At minimum, user-facing controls should distinguish:
- Music
- Voice
- gameplay-critical SFX
- ambient/background

Do not force critical warning cues to share the same user slider as purely decorative ambience if avoidable.

---

# PART AT — SIDECHAIN / DUCKING

Short duck events may be used for:
- boss superweapon warning;
- incoming lethal artillery;
- critical HQ warning;
- important radio line.

Duck mainly:
- music;
- ambience;
- low-priority distant combat.

Do not heavily duck:
- other simultaneous critical warnings.

Suggested envelope:
- fast attack: 0.15–0.30 s
- release: 0.5–1.5 s

Tune by listening tests.

---

# PART AU — HDR / ENVELOPE-AWARE MIX

The project already has RMS/envelope analysis.

Use it to ensure:
- transient impact can temporarily dominate;
- long explosion tail stops dominating the mix after its meaningful transient;
- boss warning can cut through without permanently crushing everything else.

Envelope-aware dynamic range control is preferred to crude constant ducking.

---

# PART AV — DISTANCE SOUND LAYERS

Large weapons can use layered behavior:

```text
NearTransient
Body
FarReport
EnvironmentTail
```

At far distance:
- reduce high frequencies;
- soften transient;
- keep recognizable body/tail.

Do not make a 155 mm cannon simply become the same sound at -30 dB.

---

# PART AW — SPATIAL AUDIO

For important sources use:
- position;
- distance attenuation;
- orientation/cone where relevant.

Directional sources:
- siren;
- engine exhaust;
- naval horn;
- rocket exhaust;
- loudspeaker.

Avoid expensive full spatial treatment for every tiny distant emitter.

---

# PART AX — OBSTRUCTION / OCCLUSION / DIFFRACTION

Urban/fortress maps benefit from acoustic obstruction.

Important nearby emitter:
- wall/building between listener and source
→ volume attenuation + low-pass / diffraction-style change.

Performance rules:
- update at reduced frequency;
- distance cap;
- prioritize high-value nearby sources;
- static acoustic zones can use precomputed/room metadata.

Do not raycast every emitter every frame.

---

# PART AY — ENVIRONMENT REVERB

Map/biome areas can define acoustic environments:
- open desert;
- forest;
- street canyon;
- fortress interior/courtyard;
- harbor;
- snowfield.

Use broad zones.
Do not create hundreds of micro reverb volumes.

---

# PART AZ — WEAPON AUDIO IDENTITY

Every major family should be recognizable:

```text
MG
Autocannon
Tank cannon
Heavy cannon
Mortar
Howitzer
MLRS
ATGM launch
SAM launch
Railgun
Energy weapon
Drone motor
Helicopter rotor
Jet pass
Naval gun
Boss superweapon
```

Variation within family:
- size tier;
- environment;
- distance.

Identity must survive mixing.

---

# PART BA — INCOMING / OUTGOING AUDIO

Separate:

## Artillery
- outgoing thump/launch
- incoming whistle/approach
- impact

## Missile
- launch
- motor/flyby
- incoming/lock/approach
- intercept/impact

## Bomb
- release/fall
- warning where gameplay permits
- impact

The player should often perceive:
> danger is coming
before:
> damage already happened.

---

# PART BB — TOP ATTACK AUDIO

Top-attack weapon may have:
- launch signature;
- overhead approach signature;
- dive/terminal cue;
- impact signature.

Direct ATGM should not use the same terminal warning pattern if gameplay response differs.

---

# PART BC — BOSS AUDIO STATE

Boss audio layers:
- idle/movement;
- phase transition;
- weapon charge;
- superweapon warning;
- part damaged;
- part destroyed;
- shield/APS/radar state if relevant;
- death.

Do not stack all layers at full volume.

Use priority and state ownership.

---

# PART BD — VEHICLE MOVEMENT AUDIO

Movement sound should expose:
- vehicle size;
- surface;
- speed;
- damage/component state where useful.

Families:
- tracked;
- wheeled;
- hover/amphibious if present;
- naval;
- helicopter;
- jet;
- rail.

Avoid restarting engine loops on every AI micro-order.

---

# PART BE — WEATHER AUDIO

Weather metadata can drive:
- rain bed;
- wind;
- storm gust;
- distant thunder;
- sandstorm noise;
- snow/wind dampening.

Critical warning cues remain intelligible.

Weather should not force players to increase master volume to hear threats.

---

# PART BF — AMBIENCE

Biome ambience should:
- establish location;
- fill quiet gaps;
- reduce during heavy combat via mix priority/ducking;
- not mask tactical information.

Examples:
- harbor machinery/gulls/water;
- desert wind;
- jungle insects/birds;
- urban distant hum;
- volcanic wind/rumble.

Do not use overly repetitive one-shot loops.

---

# PART BG — RADIO / VOICE

Radio information should have hierarchy:
- objective update;
- boss warning;
- unit acknowledgement;
- flavor chatter.

Critical line:
- higher priority;
- interrupt lower flavor chatter if necessary.

Provide subtitles for meaningful spoken information.

---

# PART BH — CAPTIONS / NON-SPEECH CUES

If accessibility scope permits, support captions for critical non-speech events:

Examples:
- `[Incoming artillery]`
- `[Missile lock]`
- `[Boss superweapon charging]`

Optional direction indicator where UI architecture supports it.

Do not caption every MG shot.

---

# PART BI — HAPTICS

Optional haptics can reinforce:
- own heavy gun;
- nearby explosion;
- missile warning;
- boss superweapon.

Must have:
- enable/disable;
- intensity control.

Never convey unique required information only through haptics.

---

# PART BJ — AUDIO REALISM REFERENCE VS LICENSE STATUS

Current `NEED_SOURCE` entries can mean missing realism reference, not missing legal permission.

Separate fields:

```text
assetLicenseStatus
assetSourceStatus
realismReferenceStatus
```

Example:
- `ASSET_LICENSE_OK`
- `REALISM_REFERENCE_NEEDS_SOURCE`

Do not block a legally sourced asset because a realism comparison citation is missing.

---

# PART BK — AUDIO QUALITY GATES

Every combat clip should be checked for:
- LUFS range;
- peak/headroom;
- low-frequency ratio;
- metallic ringing/keng;
- clipping;
- excessive DC;
- tail duration;
- mono/stereo appropriateness.

Current metric system should remain authoritative.

Add:
- event priority;
- max instances;
- virtualization policy;
- attenuation preset;
- occlusion class.

---

# PART BL — CROSS-SYSTEM THREAT CUE TABLE

Create a canonical table:

```text
ThreatType
VisualTelegraph
AudioCue
OptionalHaptic
Priority
MinLeadTime
CanBeOccludedVisually
CanBeVirtualizedAudio
```

Critical examples:
- artillery incoming;
- missile lock;
- top attack;
- bomb;
- boss superweapon;
- mine detected;
- EMP;
- thermobaric;
- nuke/superheavy strike.

P0 audio warning:
`CanBeVirtualizedAudio = false` during active warning.

---

# PART BM — DAMAGE TYPE READABILITY

Do not require players to identify damage type perfectly by VFX, but make families distinguishable.

Kinetic:
- sharp/hard impact.

ShapedCharge:
- concentrated high-energy impact.

HE:
- broad blast.

Fragmentation:
- broad light fragment burst.

Fire:
- persistent flame.

Energy:
- coherent electric/energy visual/audio language.

This supports learning without turning the game into color-coded arcade effects.

---

# PART BN — PROJECTILE READABILITY

Projectile/tracer scale should reflect:
- weapon tier;
- projectile speed;
- gameplay need.

Very fast kinetic:
- brief readable tracer/muzzle connection, not giant glowing orb.

Slow missile:
- persistent visible motor/trail.

Drone:
- silhouette + motor sound.

Bomb:
- fall/shadow/marker where needed.

---

# PART BO — FOG / WEATHER / SMOKE INTERACTION

Presentation must respect actual gameplay visibility.

Do not:
- reveal hidden unit through persistent VFX/audio if game rules say it is unknown;
- play exact positional loop from a hidden unit beyond intel rules unless intentional acoustic detection is a mechanic.

If combat sound can reveal approximate direction:
- explicitly define it as gameplay rule;
- use uncertainty, not perfect tracking.

---

# PART BP — MAP / AUDIO ACOUSTIC METADATA

Generate simplified acoustic zones from map semantics:

```text
Open
UrbanStreet
Fortress
Forest
Harbor
Tunnel/Interior if present
```

Fields:
```text
reverbPreset
occlusionMaterialClass
ambientProfile
farReportTail
```

Do not require high-poly acoustic geometry.

---

# PART BQ — UI / WORLD ICON READABILITY

Objective/team/threat icons:
- outline;
- scale rules;
- contrast floor;
- do not rely only on red/green;
- retain visibility over bright snow and dark night.

Critical offscreen threat:
- directional edge cue where gameplay appropriate.

---

# PART BR — COLOR-BLIND / LOW-VISION TESTING

At minimum simulate:
- protanopia;
- deuteranopia;
- tritanopia;
- low contrast.

Test:
- team colors;
- objective ownership;
- danger telegraphs;
- boss weakpoint states;
- repair/support indicators.

Simulation does not replace human user testing where possible.

---

# PART BS — REDUCED EFFECTS ACCESSIBILITY MODE

Optional setting:

```text
Reduced Flash
Reduced Camera Shake
Reduced Screen Distortion
Reduced Cosmetic Particles
```

Must preserve:
- exact danger shape;
- timing;
- important projectile;
- impact confirmation.

---

# PART BT — PERFORMANCE TEST SCENES

Create repeatable scenes:

## Map
- 48v48 in urban choke;
- 48v48 open desert;
- naval boss + escorts;
- fortress siege;
- weather storm;
- maximum wreck density.

## Visual
Measure:
- CPU render thread;
- batches/state changes;
- GPU frame;
- transparent overdraw;
- VFX particle concurrency.

## Audio
Measure:
- event count;
- physical voices;
- virtual voices;
- dropped voices;
- priority distribution;
- spatial-audio CPU;
- occlusion query count.

---

# PART BU — RENDER QUALITY GATES

Do not accept a visual improvement if:
- combat readability decreases;
- low preset loses key cue;
- frame budget materially regresses outside agreed budget.

Track:
```text
renderers visible
batches
triangles
vertices
transparent pixels/overdraw
particle emitters
shadow casters
```

---

# PART BV — AUDIO LOAD GATES

In `crowded_battle` style stress test:
- P0/P1 cues must always play;
- no warning misses;
- background cluster sounds may virtualize;
- voice count stays bounded;
- mix remains intelligible.

Add automated test:
inject P0 warning during peak combat event storm and assert audible/played state.

---

# PART BW — MAP TOPOLOGY LOAD GATES

On map load validate:
- all objectives map to components;
- all spawns map to components;
- all naval nodes connected as expected;
- no impossible boss route curvature;
- all declared gates have clearance;
- no generated tactical point outside playable bounds;
- no FireSupportAnchor inside forbidden transit zone.

---

# PART BX — ART / MODEL BUILD GATES

Build fails or warns according to severity:

Hard:
- missing runtime muzzle/mount/part;
- runtime suffix used;
- nonfinite mesh data;
- invalid bound;
- gameplay node duplicate.

Soft:
- renderer budget exceeded;
- triangle budget exceeded;
- open edges if acceptable asset type;
- visual metric deviation.

Owner exceptions must be recorded.

---

# PART BY — REFERENCE IMAGE / CARD RENDER CONSISTENCY

Card renders should:
- use consistent camera/perspective;
- preserve silhouette;
- show faction/vehicle identity;
- not hide main weapon;
- use neutral enough background for readability.

If actual model changes structurally:
- regenerate card;
- update hash/manifests.

---

# PART BZ — SCREENSHOT / GOLDEN TESTS

Maintain golden captures for:
- each VFX tier;
- top attack;
- artillery warning;
- boss superweapon;
- objective marker in each biome;
- main boss damage states;
- representative normal/HD models.

Compare:
- missing effect;
- gross scale mismatch;
- unreadable telegraph.

Do not require pixel-perfect comparison for procedural particles.

---

# PART CA — MAP PLAYTEST METRICS

Record by map/mode:
- first-contact time;
- objective arrival time;
- lane usage share;
- choke queue time;
- spawn-exit block events;
- average LOS engagement distance;
- artillery firing-position distribution;
- naval route collision events;
- heavy-unit inaccessible-route attempts.

Use telemetry to validate topology assumptions.

---

# PART CB — VISUAL READABILITY PLAYTEST METRICS

Questions:
- Can player identify incoming artillery before impact?
- Can player distinguish top-attack from direct missile?
- Can player tell boss part is destroyed?
- Can player locate objective through smoke?
- Are T4/T5 effects overwhelming smaller but important warnings?

Record miss rate.

---

# PART CC — AUDIO PLAYTEST METRICS

Test with:
- headphones;
- stereo speakers;
- low volume;
- noisy room;
- music high;
- music low.

Questions:
- incoming warning detected?
- direction understandable?
- boss cue distinct?
- weapon family recognizable?
- speech intelligible?
- combat tiring after long session?

---

# PART CD — MAP ISSUE PRIORITY

## P0
1. Generate GameplayTopology.
2. Choke width/capacity.
3. Vehicle-size route compatibility.
4. ShoreFireRegion generation.
5. Naval curve/turn-radius validation.
6. Spawn clear-zone/anti-camp validation.
7. Warning registry.

## P1
8. Staging areas.
9. Firing pockets/hull-down candidates.
10. Terrain semantics.
11. tactical objective approach metadata.
12. acoustic zone metadata.

## P2
13. richer landmark/readability audit.
14. weather presentation metadata.
15. telemetry feedback.

---

# PART CE — VISUAL / MODEL ISSUE PRIORITY

## P0
1. Stable runtime node names.
2. Boss/mount/pivot contract validation.
3. Threat telegraph consistency.
4. Wreck visual/nav sync.
5. Critical low-preset cue preservation.

## P1
6. Model renderer outlier cleanup.
7. normal model hard-cap cleanup.
8. boss part damage states.
9. Top Attack visual language.
10. color/contrast QA.

## P2
11. LOD polish.
12. biome identity polish.
13. card/golden capture consistency.

---

# PART CF — AUDIO ISSUE PRIORITY

## P0
1. Gameplay priority/voice management.
2. P0/P1 warning survivability.
3. incoming/outgoing distinction.
4. critical cue visual counterpart.
5. licensing-vs-realism-source status separation.

## P1
6. sidechain/HDR/envelope behavior.
7. distance layers.
8. obstruction/occlusion.
9. weapon-family identity.
10. captions for critical warnings if UI scope supports.

## P2
11. biome ambience expansion.
12. environment reverb polish.
13. optional haptic profiles.

---

# PART CG — SPECIFIC CURRENT FIXES TO INCLUDE

At minimum audit and fix or formally waive:

```text
attack_jet:
    runtime DCC suffix muzzle nodes
    renderer budget warning

cp_relay:
    renderer budget warning

armored_bulldozer:
    normal triangle budget warning
    normal vertex hard-cap warning
```

Do not assume these are the only outliers.
Run the full model validator and create an outlier report.

---

# PART CH — DO NOT DO

Do not:
- redesign all maps because of YELLOW warnings;
- make all maps symmetrical;
- remove intentional long sightlines automatically;
- add random terrain combat buffs;
- make weather change weapon accuracy without a balance decision;
- make every projectile neon;
- encode damage types only by color;
- hide lethal telegraphs on low graphics;
- use `.001` runtime node identifiers;
- solve renderer count by merging movable/destructible parts incorrectly;
- play every audio event physically;
- duck the entire mix for every explosion;
- raycast occlusion for every emitter every frame;
- use audio to reveal hidden enemy exact location unless gameplay explicitly allows it;
- make camera shake mandatory information;
- use haptic-only warning;
- let ambience mask gameplay warnings.

---

# PART CI — ACCEPTANCE TESTS

## Map
- [ ] 100% objectives/spawns resolve to topology components.
- [ ] all heavy/boss routes validated by size.
- [ ] all boss naval routes pass curvature audit.
- [ ] all critical chokes have width/capacity.
- [ ] no normal spawn has unexplained full-exit direct-fire exposure.
- [ ] shore-fire feasibility works.
- [ ] map warnings all have state/owner/reason.

## Model
- [ ] no runtime gameplay node depends on `.001` suffix.
- [ ] all free turrets have stable pivots.
- [ ] every barrel has expected muzzle.
- [ ] boss part nodes exist.
- [ ] hard-cap model violations fixed or explicitly waived.
- [ ] renderer outliers audited.

## VFX
- [ ] T0–T5 hierarchy readable.
- [ ] lethal telegraphs match actual hit area/timing.
- [ ] top attack visually distinct.
- [ ] low preset preserves critical cues.
- [ ] reduced-flash setting preserves gameplay truth.
- [ ] boss parts have readable destruction state.

## Audio
- [ ] P0/P1 warnings never lost in crowded stress mix.
- [ ] artillery/missile/bomb incoming cues distinct where applicable.
- [ ] distance attenuation does not erase identity.
- [ ] occlusion works on high-value nearby emitters.
- [ ] user has separate core volume controls.
- [ ] meaningful spoken warnings have subtitles/captions.
- [ ] asset license status is distinct from realism-reference status.

## Cross-system
- [ ] wreck visual/collision/nav states synchronized.
- [ ] fog does not leak hidden exact enemy data through presentation.
- [ ] weather does not make critical cue unreadable.
- [ ] map topology feeds AI without duplicate geometry inference.
- [ ] boss hull/turret model contract supports AI behavior.

---

# PART CJ — AUTOMATED VALIDATORS TO ADD/EXTEND

Recommended:

```text
Tools/audit/map_topology_audit.py
Tools/audit/naval_route_audit.py
Tools/audit/spawn_fairness_audit.py
Tools/audit/tactical_position_audit.py

Tools/assets/runtime_node_audit.py
Tools/assets/model_budget_audit.py

Tools/vfx/telegraph_audit.py
Tools/vfx/readability_capture.py

Tools/sfx/priority_stress_test.py
Tools/sfx/spatial_audio_audit.py
Tools/sfx/critical_warning_mix_test.py
```

Reuse existing tools where equivalent code already exists.

Do not create duplicate tooling if current validators can be extended.

---

# PART CK — GENERATED DOCUMENTATION

After canonical changes regenerate/update as applicable:

```text
06_ban_do.xlsx
06_ban_do.md
07_hinh_anh_am_thanh_model.xlsx
07_hinh_anh_am_thanh_model.md
00_index.xlsx
README.md
CHANGES.md

Docs/checks/map_audit.csv
Docs/maps/validation outputs
Docs/models/BUDGETS.md
model baseline/gold metrics
audio metrics
audio sample mixes
VFX capture sheets
AI-readable map topology exports
```

If AI master consumes new topology fields, update/regenerate:
```text
09_ai.xlsx
09_ai.md
```

Do not manually edit generated output as authority.

---

# PART CL — IMPLEMENTATION PHASES

## Phase 1 — correctness and contracts
- runtime model node names;
- GameplayTopology;
- route-size validation;
- naval curvature;
- critical telegraph definitions;
- audio priority classes;
- wreck state synchronization.

## Phase 2 — tactical map semantics
- chokes/capacity;
- staging;
- FireSupportAnchor candidates;
- shoreline firing regions;
- terrain semantics;
- spawn fairness.

## Phase 3 — readability
- top attack;
- boss part states;
- damage/weapon family VFX grammar;
- low preset;
- accessibility contrast/flash controls.

## Phase 4 — audio depth
- virtualization;
- distance layers;
- obstruction;
- acoustic zones;
- mix duck/HDR;
- captions.

## Phase 5 — performance polish
- renderer/material cleanup;
- LOD;
- particle overdraw;
- stress scene profiling;
- accepted-warning cleanup.

---

# PART CM — FINAL DESIGN DECISIONS

Final recommendations:

1. **Do not redesign the 06 map system.** Add a generated semantic topology layer.
2. **Do not rebalance weather from this task.** Expand presentation metadata only.
3. **Do not make all YELLOW warnings failures.** Add acceptance governance.
4. **Make ship route geometry obey real movement constraints.**
5. **Make model runtime node naming a hard gameplay contract.**
6. **Preserve current VFX tier system but enforce gameplay clarity hierarchy.**
7. **Add dedicated Top Attack presentation.**
8. **Make boss-part damage visually readable.**
9. **Make critical warnings multi-channel.**
10. **Use priority + virtualization for crowded audio.**
11. **Use distance/occlusion to create depth rather than raw volume scaling only.**
12. **Never allow low graphics/performance optimization to delete critical combat information.**
13. **Synchronize wreck presentation with navigation/collision state.**
14. **Treat accessibility as a combat-readability QA requirement, not a cosmetic afterthought.**

---

# PART CN — RESEARCH REFERENCES

These references informed the recommendations. Repo data remains authoritative for Machine Brigade-specific values.

## Visual clarity / VFX
**R1 — Riot Games: “Clarity in League”**
- gameplay-impact hierarchy;
- attention proportional to importance;
- direction/readability;
- map/background readability;
- avoid excessive visual noise.

**R2 — Riot Games: “League’s VFX Style Guide”**
- clarity first;
- minimize clutter;
- gameplay/value/color/shape/timing framework.

**R3 — Riot Games: “Behind the Scenes of VFX Updates”**
- correct inaccurate/missing hitbox communication before thematic polish;
- reduce visual noise;
- brightness/power should match gameplay.

**R4 — Riot Games VFX update articles/patch notes**
- actual hitbox indicators;
- width/range lines;
- simplifying noisy decals.

## Audio systems
**R5 — Audiokinetic Wwise: Virtual Voices**
- inaudible/over-limit sounds can move to virtual voices to reduce processing while retaining state where appropriate.

**R6 — Audiokinetic Wwise: Attenuation**
- distance, obstruction, occlusion, diffraction/transmission can drive volume/filters.

**R7 — Audiokinetic Wwise: Spatial Audio Rooms/Portals**
- diffraction, transmission and obstruction concepts;
- reduced update frequency is a legitimate performance tradeoff.

**R8 — Audiokinetic Wwise HDR / amplitude envelopes**
- transient importance can drive mix without long tails permanently dominating.

**R9 — Audiokinetic Wwise priority/playback limits**
- priority and max-instance behavior support bounded crowded mixes.

## Rendering / assets
**R10 — Unity Manual: Optimizing Draw Calls**
- render-state changes/draw calls are significant;
- shared materials, SRP batching/instancing/batching choices should be profiled;
- do not optimize only polygon count.

**R11 — Unity Manual: Occlusion Culling**
- hidden geometry should not consume unnecessary render work where the scene structure benefits from occlusion.

**R12 — NVIDIA GPU Gems: high-speed/off-screen particle rendering**
- transparent particle overdraw can become a major fill-rate bottleneck.

## Multi-agent / pathing
**R13 — ORCA / RVO2 research (UNC/GAMMA)**
- reciprocal collision avoidance supports smooth local multi-agent motion;
- relevant to traffic layer, not a replacement for strategic topology.

## Accessibility / combat cues
**R14 — Xbox Accessibility Guideline 103**
- important visual/audio information should be represented via more than one sensory channel;
- avoid relying only on color.

**R15 — Xbox Accessibility Guideline 102**
- contrast matters for non-text gameplay cues as well as UI.

**R16 — Xbox Accessibility Guideline 104/105**
- captions for meaningful audio;
- separate controls for music, speech and important/background audio.

**R17 — Xbox Accessibility Guideline 110**
- haptics are optional reinforcement and should be configurable, never the only information channel.

**R18 — Xbox Accessibility Guideline 118**
- reduce large/rapid high-contrast flashes and support safer visual presentation.

## Competitive map examples
**R19 — StarCraft II competitive map conventions / official map descriptions**
- rush distance, line-of-sight blockers, destructible route modifiers and watch/control positions are meaningful map characteristics.
- Used only as a conceptual reference; Machine Brigade’s audit metrics remain authoritative.

---

# PART CO — FINAL RECHECK CHECKLIST

Before declaring this task complete:

## Internal consistency
- [ ] no recommendation requires changing combat balance values;
- [ ] no recommendation contradicts AI master no-reverse naval rule;
- [ ] no new weather accuracy/damage modifier introduced;
- [ ] no hidden-info audio leak;
- [ ] no critical cue relies on one sensory channel.

## Map integration
- [ ] generated topology derived from canonical map geometry;
- [ ] AI uses topology rather than duplicate ad-hoc geometry analysis;
- [ ] ship route audit uses actual boss/ship dimensions and turn rates;
- [ ] warnings are governed, not blindly fixed.

## Visual/model
- [ ] runtime node schema stable;
- [ ] renderer/LOD optimization preserves moving/destructible parts;
- [ ] VFX clarity outranks spectacle;
- [ ] critical effects survive low preset.

## Audio
- [ ] crowded-event prioritization explicit;
- [ ] critical warnings cannot virtualize/drop during active warning;
- [ ] distance/spatial behavior bounded for CPU;
- [ ] ducking is brief and priority-aware;
- [ ] sample mixes regenerated after changes.

## Accessibility
- [ ] color-independent critical telegraphs;
- [ ] configurable camera shake;
- [ ] reduced-flash path;
- [ ] key audio has visual counterpart;
- [ ] subtitles/captions cover critical speech/warnings if implemented.

## Performance
- [ ] 48v48 urban stress;
- [ ] 48v48 open stress;
- [ ] naval boss stress;
- [ ] siege VFX stress;
- [ ] storm/weather stress;
- [ ] wreck-heavy stress.

---

# PART CP — FINAL IMPLEMENTATION REPORT FORMAT

Coding/asset AI should return:

1. canonical files changed;
2. generated files regenerated;
3. maps with topology changes;
4. map warnings fixed/accepted/playtest-required;
5. naval routes adjusted;
6. model runtime nodes renamed;
7. model budget outliers fixed/waived;
8. VFX clarity changes;
9. Top Attack telegraph implementation;
10. boss part visual-state implementation;
11. audio priority table;
12. voice/virtualization policy;
13. distance/occlusion implementation;
14. accessibility settings added;
15. performance before/after;
16. 48v48 stress results;
17. audio warning-miss count;
18. stale data scan;
19. screenshots/audio sample outputs regenerated;
20. known remaining issues.

Final confirmations:

```text
Map geometry remains canonical.
GameplayTopology is generated.
Naval routes are turn-radius validated.
Critical chokes have capacity metadata.
Vehicle-size route compatibility exists.
Shore-fire feasibility exists.
Runtime model gameplay nodes use stable semantic names.
Critical telegraphs match gameplay.
Top Attack has distinct readable presentation.
Critical warnings survive crowded audio.
Wreck visual and nav states are synchronized.
Low graphics preserves gameplay-critical cues.
Accessibility cues do not rely on color/audio/haptics alone.
```

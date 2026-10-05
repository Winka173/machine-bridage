dùng @Machine_Brigade_MAP_VISUAL_AUDIO_MASTER_SPEC.md  

Hãy dùng file đính kèm:

`Machine_Brigade_MAP_VISUAL_AUDIO_MASTER_SPEC.md`

làm **spec chính thức mới nhất** cho toàn bộ hệ:

- bản đồ;
- topology gameplay;
- naval routes;
- terrain/weather presentation;
- model/runtime nodes;
- LOD/render budget;
- VFX;
- combat readability;
- audio;
- spatial audio;
- accessibility;
- QA/performance.

File này là master spec cho phạm vi trên.

Không dùng các prompt cũ về bản đồ/hình ảnh/âm thanh nếu có xung đột.

# 1. MỤC TIÊU

Audit toàn bộ implementation hiện tại liên quan tới:

- `06_ban_do`
- `07_hinh_anh_am_thanh_model`
- map runtime
- pathing/nav
- naval lanes
- model loading
- weapon mount/muzzle nodes
- boss part nodes
- VFX
- audio playback/mixer
- accessibility presentation
- map/model/audio validators

Sau đó implement theo file master.

Ưu tiên:

1. correctness;
2. gameplay readability;
3. AI integration;
4. performance;
5. presentation polish.

Không ưu tiên cosmetic polish trước các lỗi ảnh hưởng gameplay.

---

# 2. KHÔNG REBALANCE COMBAT

Task này KHÔNG được tự thay:

- weapon damage;
- penetration;
- armour;
- HP;
- boss HP;
- boss armour;
- reload;
- projectile speed;
- range;
- economy;
- AI tactic balance.

Weather cũng KHÔNG tự thêm:
- accuracy penalty;
- damage modifier;
- projectile penalty

nếu không có yêu cầu riêng.

Task này chủ yếu bổ sung:
- metadata;
- topology;
- validation;
- readability;
- presentation;
- performance.

---

# 3. MAP GEOMETRY VẪN LÀ CANONICAL

Không thay toàn bộ map design.

Canonical map JSON/geometry hiện tại vẫn là nguồn gốc.

Tạo/generated semantic layer từ map:

```text
GameplayTopology
GroundComponents
NavalComponents
AmphibiousComponents
TacticalChokes
TacticalLanes
StagingAreas
FiringPositions
FireSupportAnchors
ShoreFireRegions
SpawnClearZones
```

Không hand-author duplicate geometry nếu có thể generate.

---

# 4. GAMEPLAY TOPOLOGY — BẮT BUỘC

Implement `GameplayTopology`.

Ít nhất phải có:

```text
GroundComponent[]
NavalComponent[]
AmphibiousComponent[]
```

Mọi:
- spawn;
- objective;
- base;
- fortress;
- shoreline;
- naval lane;
- boss route

phải resolve được sang component phù hợp.

Topology này phải dùng được bởi AI master sau này.

Không để AI tự suy lại geometry theo logic riêng ở nhiều chỗ.

---

# 5. VEHICLE-SIZE ROUTE VALIDATION

Route connectivity không còn binary.

Phải support:

```text
Light
Medium
Heavy
SuperHeavy
Boss
```

Audit:

- gate width;
- bridge width;
- road width;
- turn clearance;
- obstacle clearance;
- choke clearance.

Nếu Light đi được nhưng SuperHeavy không đi được:
- topology phải phản ánh đúng.

Không cho pathfinder gửi large vehicle vào route technically connected nhưng thực tế không đủ không gian.

---

# 6. CHOKEPOINT CAPACITY

Mỗi choke phải có:

```text
usableWidthM
maxLightSideBySide
maxMediumSideBySide
maxHeavySideBySide
estimatedThroughput
oppositeTrafficAllowed
queueAreaA
queueAreaB
type
```

Các loại:

- gate;
- bridge;
- street;
- breach;
- terrain gap;
- harbor throat;
- rail crossing.

Capacity tính từ actual width và footprint.

Không chỉ dùng boolean `isChoke`.

---

# 7. TRAFFIC / TRANSIT LANES

Generate lane semantics:

```text
laneWidth
vehicleClassSupport
expectedTravelSpeed
trafficCapacity
chokeDependency
parkingForbidden
```

Mark:
- main transit;
- secondary;
- flank;
- support/service;
- boss corridor.

Fire-support unit không nên chọn firing position trên main transit lane.

---

# 8. SPAWN / ENTRY FAIRNESS

Audit tất cả spawn/entry:

```text
enemyDirectLOSAtSpawn
enemyDirectLOSAtExit
enemyArtilleryCoverageAtSpawn
spawnToFirstCoverM
spawnExitWidthM
alternateExitCount
spawnQueueCapacity
enemyRushETA
```

Flag trường hợp:
- toàn bộ exit bị direct fire ngay đầu trận;
- chỉ có 1 exit quá hẹp;
- một vehicle có thể chặn toàn spawn;
- không có alternate route;
- artillery có thể cover toàn bộ spawn từ vị trí bình thường.

Intentional asymmetry:
- không auto-fix;
- phải ghi accepted reason.

---

# 9. SHORE FIRE REGIONS

Tạo:

```text
ShoreFireRegion
```

Fields:

```text
groundComponentId
shorelineSegment
minDistanceToNavalLane
maxDistanceToNavalLane
elevation
LOSQuality
coverScore
```

Mục tiêu:

phân biệt:

```text
ground unit cannot enter water
```

với:

```text
ground unit cannot influence naval target
```

AI phải biết tank/coastal gun nào thực sự bắn tới naval lane.

---

# 10. NAVAL ROUTE VALIDATION

SeaRouteGraph hiện có phải trở thành route network có kinematic constraints.

Mỗi node/segment nên expose/derive:

```text
width
curveRadiusM
entryHeading
exitHeading
maxRecommendedShipLength
passingAllowed
passingBay
bossSafe
broadsideRoomLeft
broadsideRoomRight
```

---

# 11. NAVAL TURN RADIUS

Dùng actual ship/boss movement data.

Approx:

```text
Rmin = speed / angularSpeedRad
```

Route phải pass:

```text
curveRadius >= Rmin * safetyFactor
```

Dùng safety khoảng:

```text
1.10–1.25
```

hoặc equivalent đã xác minh bằng simulation.

Flag:

- hairpin;
- node spacing quá gần;
- 90° turn impossible;
- hull collision với shore trong legal turn.

Không ép AI controller giải geometry bất khả thi.

---

# 12. BOSS NAVAL LANE

Boss route phải có:

```text
bossSafe
passing zones
no-overtake areas
broadside space
shore clearance
turn clearance
```

Không tạo tình huống boss phải:
- reverse;
- three-point turn;
- giật trái/phải để qua node.

---

# 13. WALL / BREACH METADATA

Mỗi wall/gate phá được cần derived metadata:

```text
blockedRouteIds
pathCostReductionOnDestroy
heavyAccessGained
objectiveAccessGained
alternateRouteExists
defensiveTowerCoverage
```

Dữ liệu này phục vụ:
- Breacher AI;
- Siege AI;
- route planning.

---

# 14. TACTICAL POSITIONS

Generate candidate positions:

## DirectFirePosition
Score:
- LOS;
- effective range;
- cover;
- hull-down;
- escape;
- friendly blocking;
- threat.

## ArtilleryPocket
Score:
- objective coverage;
- min-range safety;
- counterbattery risk;
- AA support;
- escape route;
- traffic conflict.

## ReconObservation
Score:
- area observed;
- approach coverage;
- risk;
- escape.

## HullDownPosition
Chỉ generate nếu geometry thật sự che hull và vẫn cho weapon LOS.

Không giả lập hull-down từ ridge arbitrary.

---

# 15. STAGING / RALLY AREAS

Generate staging areas đủ cho squad.

Không đặt:
- trong choke;
- trong spawn clear zone;
- trong objective capture circle trừ khi intended;
- trên major transit lane.

Metadata:

```text
capacityLight
capacityHeavy
coverScore
threatExposure
distanceToObjective
availableLanes
```

---

# 16. TERRAIN SEMANTICS

Map terrain tags hiện tại sang:

```text
MovementCost
Traction
Concealment
VisualCover
DirectFireCover
ArtilleryExposure
MineSuitability
HullDownPotential
LargeVehiclePenalty
```

Đây chủ yếu là semantic/pathing/AI metadata.

Không tự biến thành damage/accuracy buffs.

---

# 17. WEATHER

Giữ visibility multiplier hiện tại.

Chỉ thêm presentation metadata:

```text
FogDensity
AmbientLight
Cloudiness
RainIntensity
SnowIntensity
WindStrength
LightningIntensity
DustIntensity
ContrailVisibility
MuzzleFlashVisibility
AmbientAudioProfile
ReverbProfile
```

Critical cue phải vẫn đọc được trong:
- Fog;
- Night;
- Snow;
- Sandstorm;
- Storm.

---

# 18. MAP READABILITY

Routeability phải đọc được bằng hình ảnh.

Phải phân biệt rõ:

- passable opening;
- impassable obstacle;
- destructible wall;
- permanent boundary;
- usable shore;
- cliff shore;
- objective;
- gate;
- route.

Không phụ thuộc hidden collider knowledge.

---

# 19. LANDMARKS

Large map cần strong macro landmarks.

Audit:
- distinct silhouette;
- không giống nhau quá mức;
- không bị nhầm với objective;
- hỗ trợ orientation.

Không cần thêm landmark nếu map hiện tại đã đủ.

Chỉ flag map không có orientation anchors.

---

# 20. MAP WARNING GOVERNANCE

Các warning kiểu:

```text
YELLOW sightline
YELLOW exits
```

không auto-fix.

Mỗi warning phải có:

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

Không để warning tồn tại mãi không có context.

---

# 21. MODEL RUNTIME NODE CONTRACT

Gameplay runtime node phải dùng semantic stable name.

CẤM:

```text
Muzzle_main.001
Muzzle_missile.002
Part_radar.001
```

Dùng:

```text
Muzzle_main_L
Muzzle_main_R
Muzzle_missile_L
Muzzle_missile_R
Part_radar
```

Validator hard fail nếu gameplay lookup còn dùng Blender/DCC suffix.

---

# 22. AIM / PIVOT MODEL CONTRACT

Mỗi aimed weapon phải có:

```text
aimMode = Free | Hull | FixedArc
pivotNode
muzzleNodes[]
yawMin
yawMax
pitchMin
pitchMax
```

Model và weapon data phải match.

Free turret:
- pivot đúng;
- muzzle child đúng;
- hull không cần quay trong arc.

Hull-fixed:
- explicit `HullAim`.

Đặc biệt quan trọng cho boss/naval AI master.

---

# 23. BOSS PART NODES

Mỗi breakable boss part gameplay-relevant:

```text
Part_*
```

phải tồn tại.

Expose:
- node;
- attachment points;
- destroyed state;
- VFX point nếu cần.

Không để AI/gameplay tham chiếu node không ổn định.

---

# 24. MODEL DAMAGE STATES

Các part quan trọng nên hỗ trợ:

```text
Healthy
Damaged
Critical
Destroyed
```

Không bắt buộc 4 mesh.

Có thể dùng:
- material;
- emissive;
- smoke;
- sparks;
- hide/broken submesh.

Mục tiêu là readability.

---

# 25. MODEL PERFORMANCE

Giữ budget hiện tại làm authority.

Phân biệt:

```text
hard cap
soft budget
owner exception
```

Renderer/material count cần được xem trọng, không chỉ triangle.

Không merge mesh mù quáng nếu làm hỏng:
- moving parts;
- destructible parts;
- culling;
- mount rotation.

---

# 26. CURRENT MODEL ISSUES

Audit và fix hoặc formally waive ít nhất:

## attack_jet
- runtime suffix muzzle nodes;
- renderer warning.

## cp_relay
- renderer count warning.

## armored_bulldozer
- triangle budget warning;
- vertex hard-cap warning.

Không giả định chỉ có 3 model này.

Chạy toàn bộ validator và report tất cả outlier.

---

# 27. LOD

Audit tất cả high-frequency categories.

Suggested:

Vehicles:
- LOD0
- LOD1 ~50–70% triangle
- LOD2 ~20–35%

Boss:
- giữ silhouette/mount detail lâu hơn.

Small props:
- aggressive LOD/instancing.

Foliage:
- kiểm soát alpha overdraw.

Không để LOD:
- xóa barrel quá sớm;
- thay gameplay silhouette;
- ảnh hưởng collider;
- làm weapon biến mất khi vẫn gameplay-active.

---

# 28. VFX CLARITY HIERARCHY

Presentation priority:

```text
P0 lethal/superweapon
P1 high threat
P2 heavy weapon
P3 normal weapon
P4 minor/cosmetic
```

Attention phải tỷ lệ tương đối với gameplay impact.

Không để:
- MG tracer
nổi hơn:
- incoming superweapon.

---

# 29. DAMAGE TYPE VISUAL LANGUAGE

Kinetic:
- sharp directional impact.

ShapedCharge:
- concentrated hot impact / jet language.

HE:
- broad blast.

Fragmentation:
- broad fragment/spark burst.

Fire:
- persistent flame.

Energy:
- coherent energy/beam/arc/pulse language.

Không chỉ dùng màu.

---

# 30. TOP ATTACK PRESENTATION

Phải phân biệt:

- direct ATGM;
- top-attack ATGM;
- drone;
- guided bomb;
- normal bomb.

Có thể dùng:

```text
climb/diving trajectory
overhead marker
ground shadow
terminal warning
vertical impact cue
```

Không dùng top-attack warning cho direct weapon.

---

# 31. THREAT TELEGRAPH CONTRACT

Mỗi high-threat attack phải có:

```text
TelegraphLeadTime
TelegraphShape
ActualDangerShape
AudioCue
OptionalHaptic
ImpactCue
CancelBehavior
```

Telegraph phải khớp:
- actual hit area;
- timing;
- direction.

Nếu attack cancel:
- cue cũng cancel/fade.

---

# 32. BOSS PRESENTATION

Boss phải đọc được:

- phase;
- charging superweapon;
- active dangerous mount;
- broken parts;
- exposed weakpoint;
- shield/APS/radar state nếu gameplay-relevant.

Không glow mọi thứ liên tục làm active state mất ý nghĩa.

---

# 33. VFX SCALE

Giữ T0–T5.

Large weapon tăng có chọn lọc:
- flash;
- pressure;
- dust;
- smoke;
- debris;
- light;
- audio body;
- tail duration.

Không scale mọi parameter linearly.

---

# 34. PARTICLE / OVERDRAW

Đo:

```text
particle count
transparent emitter count
screen coverage
overdraw
lifetime
```

Distant/noncritical effect:
- simplify;
- aggregate;
- shorten.

Critical telegraph:
- không phải thứ đầu tiên bị cắt.

---

# 35. CAMERA SHAKE

Phải có:
- intensity slider;
- reduced motion option.

Rules:
- clamp cumulative shake;
- T0/T1 nhẹ hoặc không;
- barrage không tạo continuous nausea.

Camera shake không được là cue duy nhất.

---

# 36. PHOTOSENSITIVITY

Audit:
- muzzle flashes;
- lightning;
- Energy;
- boss effects;
- warning flashing.

Thêm:
- Reduced Flash;
- Reduced Effects;
- Reduced Camera Shake.

Không dùng full-screen high-contrast rapid flashes nếu tránh được.

---

# 37. COLOR / CONTRAST

Critical cue không phụ thuộc duy nhất:
- red/green;
- hue.

Use:
- shape;
- outline;
- motion;
- icon;
- audio;
- text nếu cần.

Test:
- snow;
- desert;
- volcanic;
- night;
- fog.

---

# 38. LOW GRAPHICS CONTRACT

Low preset không được loại:

- danger telegraph;
- important projectile;
- objective marker;
- boss weakpoint state;
- team ID.

Có thể giảm:
- secondary particles;
- debris;
- ambient smoke;
- distortion;
- reflections.

---

# 39. WRECK STATE SYNC

Define:

```text
Alive
DestroyedAnimating
BlockingWreck
PassableRubble
Removed
```

Mỗi state có:
- collider;
- nav state;
- visual;
- smoke/fire.

Không:
- invisible but blocking;
- visibly solid but AI passes through unexpectedly.

---

# 40. AUDIO PRIORITY CLASSES

Suggested:

```text
P0 critical UI / lethal warning / boss superweapon
P1 incoming artillery/missile / HQ alarm
P2 own heavy weapon / nearby hostile heavy weapon
P3 nearby normal combat
P4 distant combat / engines
P5 ambience / low-value repetitive sounds
```

P0/P1 phải sống sót khi battle crowded.

---

# 41. VOICE MANAGEMENT

Implement:

- max instances;
- priority;
- virtualization;
- cooldown;
- distance weighting;
- aggregation.

Low-value distant sound:
- virtualize/kill.

Loop:
- virtual timeline có thể tiếp tục nếu engine hỗ trợ.

Không play mọi event physically.

---

# 42. AUDIO AGGREGATION

Distant cluster:

```text
many MG shots
→ few battle-cluster voices
```

Aggregate theo:
- spatial cell;
- family;
- time window;
- distance.

Không aggregate:
- selected player unit;
- close heavy threat;
- critical incoming cue.

---

# 43. AUDIO MIX BUSES

Recommended groups:

```text
Master
Music
UI
VoiceRadio
CriticalWarnings
PlayerWeapons
CombatSFX
Engines
Ambience
```

Nếu architecture hạn chế, ít nhất:
- Music
- Voice
- SFX
- Ambience

Critical warning không nên bị control chung với ambience nếu có thể tránh.

---

# 44. DUCKING

Short sidechain cho:
- boss superweapon;
- incoming artillery;
- critical HQ warning;
- important radio line.

Duck:
- music;
- ambience;
- distant combat.

Không duck P0/P1 khác.

Suggested:
- attack 0.15–0.30 s
- release 0.5–1.5 s

Tune bằng actual mixes.

---

# 45. HDR / ENVELOPE MIXING

Repo đã có envelope/RMS metrics.

Dùng để:
- transient temporarily dominate;
- explosion tail không giữ toàn mix quá lâu;
- boss warning cut through.

Không chỉ constant volume reduction.

---

# 46. DISTANCE AUDIO

Large weapon nên có cảm giác khác theo range.

Concept:

```text
NearTransient
Body
FarReport
EnvironmentTail
```

Ở xa:
- high-frequency giảm;
- transient mềm hơn;
- identity vẫn giữ.

---

# 47. SPATIAL AUDIO

Use positional attenuation cho important emitters.

Directional source:
- siren;
- exhaust;
- naval horn;
- rocket;
- loudspeaker.

Không cần expensive treatment cho mọi tiny distant sound.

---

# 48. OBSTRUCTION / OCCLUSION

Nearby important emitter bị:
- wall;
- building;
- fortress

che:
- reduce volume;
- low-pass/filter;
- optional diffraction.

Performance:
- reduced update rate;
- range cap;
- important emitters only.

Không raycast every sound every frame.

---

# 49. ACOUSTIC ZONES

Map semantic zones:

```text
Open
UrbanStreet
Fortress
Forest
Harbor
Interior/Tunnel if applicable
```

Use:
- reverb preset;
- obstruction material;
- ambient profile;
- far-tail style.

Không tạo quá nhiều micro-volumes.

---

# 50. WEAPON AUDIO IDENTITY

Distinct family identity:

- MG
- Autocannon
- Tank cannon
- Heavy cannon
- Mortar
- Howitzer
- MLRS
- ATGM
- SAM
- Railgun
- Energy
- Drone
- Helicopter
- Jet
- Naval gun
- Boss superweapon

Identity phải tồn tại cả khi nghe xa.

---

# 51. INCOMING / OUTGOING

Artillery:
- outgoing
- incoming
- impact

Missile:
- launch
- motor/flyby
- terminal warning/approach
- impact/intercept

Bomb:
- fall
- warning nếu mechanics cho phép
- impact

Player cần nghe danger trước khi ăn hit khi gameplay cho phép.

---

# 52. TOP ATTACK AUDIO

Top-attack terminal cue khác direct missile nếu người chơi cần phản ứng khác.

Không lạm dụng warning khiến battle noisy.

Priority dựa trên actual threat.

---

# 53. BOSS AUDIO STATES

Boss audio:
- movement;
- phase;
- charge;
- superweapon warning;
- part damage;
- part destroyed;
- shield/APS/radar state;
- death.

State manager phải tránh stack tất cả cùng full volume.

---

# 54. VEHICLE MOVEMENT AUDIO

Families:
- tracked;
- wheeled;
- naval;
- helicopter;
- jet;
- rail.

Drive parameters:
- speed;
- surface;
- damage/component state nếu useful.

Không restart loop vì AI issue micro-order mới.

---

# 55. WEATHER AUDIO

Rain/wind/snow/storm/sandstorm có ambient bed.

Critical warning phải vẫn clear.

Weather mix không được buộc user tăng volume mới nghe được threat.

---

# 56. CAPTIONS / ACCESSIBILITY

Meaningful spoken warning:
- subtitle.

Nếu scope cho phép:
critical non-speech captions:
- `[Incoming artillery]`
- `[Missile warning]`
- `[Boss superweapon charging]`

Không caption every gunshot.

---

# 57. HAPTICS

Optional only.

Có:
- enable;
- intensity.

Không dùng haptic làm unique required cue.

---

# 58. LICENSE VS REALISM SOURCE

Tách:

```text
assetLicenseStatus
assetSourceStatus
realismReferenceStatus
```

Nếu file audio legally sourced nhưng “real-world realism reference” còn `NEED_SOURCE`:

không coi đó là license blocker.

---

# 59. AUDIO QUALITY GATES

Giữ current metrics:

- LUFS;
- peak;
- low frequency;
- ringing;
- tail;
- clipping.

Thêm:

```text
priority
maxInstances
virtualizationPolicy
attenuationPreset
occlusionClass
```

---

# 60. CROSS-SYSTEM THREAT TABLE

Tạo canonical table:

```text
ThreatType
VisualTelegraph
AudioCue
HapticOptional
Priority
MinLeadTime
CanVisualOcclude
CanAudioVirtualize
```

P0 active warning:

```text
CanAudioVirtualize = false
```

---

# 61. FOG / AUDIO INFORMATION FAIRNESS

Không để presentation leak hidden exact enemy position.

Nếu hidden unit bắn và game cho phép player nghe:
- direction/approximation có thể hợp lệ.

Nhưng không:
- exact tracking loop;
- exact position icon;
- persistent sound revealing precise hidden movement

nếu gameplay không định nghĩa acoustic detection.

---

# 62. PERFORMANCE STRESS SCENES

Create repeatable:

- 48v48 urban choke;
- 48v48 open desert;
- naval boss + escorts;
- siege;
- storm;
- wreck-heavy.

Record:

## Render
```text
CPU render
GPU
draw calls/batches
renderers
transparent overdraw
particles
```

## Audio
```text
events
physical voices
virtual voices
dropped voices
priority distribution
occlusion queries
CPU
```

## Map
```text
route failures
blocked spawn
choke queue time
boss route corrections
```

---

# 63. CRITICAL AUDIO STRESS TEST

During maximum crowded battle:
inject:
- boss superweapon warning;
- artillery incoming;
- missile warning.

Assert:
- event plays;
- not dropped;
- intelligible.

Target:

```text
critical warning miss count = 0
```

---

# 64. MAP TELEMETRY

Log:

```text
laneUsageShare
chokeQueueSeconds
spawnBlockEvents
firstContactTime
objectiveETA
heavyRouteFailure
artilleryPositionUsage
navalCollisionEvents
bossRouteReplanCount
```

Use this to verify topology.

---

# 65. VISUAL READABILITY TEST

Ask:

- incoming artillery readable?
- top attack distinguishable?
- boss part destroyed obvious?
- objective visible through combat clutter?
- T5 effect hides next warning?
- low preset still fair?

Record miss rate.

---

# 66. AUDIO PLAYTEST

Test:
- headphones;
- stereo speaker;
- low master volume;
- high music;
- long battle session.

Check:
- warning recognition;
- direction;
- boss cue;
- weapon identity;
- voice intelligibility;
- fatigue.

---

# 67. AUTOMATED TOOLS

Extend existing tools where possible.

Suggested responsibilities:

```text
map_topology_audit
naval_route_audit
spawn_fairness_audit
tactical_position_audit

runtime_node_audit
model_budget_audit

telegraph_audit
readability_capture

priority_stress_test
critical_warning_mix_test
spatial_audio_audit
```

Không tạo duplicate script nếu validator hiện tại đã làm được.

---

# 68. IMPLEMENTATION PRIORITY

## P0 — correctness
1. stable runtime nodes
2. GameplayTopology
3. route-size validation
4. naval turn-radius audit
5. critical telegraph contract
6. audio priority
7. wreck/nav sync
8. spawn fairness

## P1 — gameplay semantics
1. chokes/capacity
2. ShoreFireRegions
3. staging
4. firing pockets
5. terrain semantics
6. Top Attack readability
7. boss part damage state
8. P0/P1 audio stress guarantee

## P2 — depth
1. obstruction
2. distance layers
3. acoustic zones
4. LOD/render cleanup
5. accessibility
6. weather presentation
7. telemetry tuning

---

# 69. SPECIFIC CURRENT FIXES

At minimum:

```text
attack_jet:
    fix runtime suffix nodes
    audit renderer count

cp_relay:
    audit/fix renderer count

armored_bulldozer:
    audit/fix or waive triangle/vertex issue
```

Do full scan, not only these.

---

# 70. DO NOT DO

Không:

- make every map symmetric;
- auto-fix every YELLOW;
- redesign map geometry without evidence;
- add weather accuracy penalties;
- add random terrain damage buffs;
- make every projectile neon;
- encode damage type only by color;
- remove critical cue in low preset;
- use `.001` runtime names;
- merge moving/destructible parts incorrectly;
- play every audio event;
- raycast audio every frame;
- allow ambience to mask warnings;
- reveal hidden exact enemy state via sound;
- use camera shake as required information.

---

# 71. GENERATED OUTPUTS

After canonical changes regenerate/update if applicable:

```text
06_ban_do.xlsx
06_ban_do.md

07_hinh_anh_am_thanh_model.xlsx
07_hinh_anh_am_thanh_model.md

00_index.xlsx
README.md
CHANGES.md
```

Also regenerate:
- map audit;
- topology exports;
- naval audit;
- spawn audit;
- model baseline/gold metrics;
- VFX captures;
- audio metrics;
- sample battle mixes;
- manifests/hashes.

If new topology is consumed by AI:

```text
09_ai.xlsx
09_ai.md
```

must also update.

Không manually patch generated output if generator exists.

---

# 72. REQUIRED FINAL REPORT

Return:

1. files changed;
2. canonical source changed;
3. generated outputs;
4. maps changed;
5. topology added;
6. chokes generated;
7. route-size failures;
8. naval route fixes;
9. spawn fairness issues;
10. warning registry;
11. model node renames;
12. model budget outliers;
13. VFX changes;
14. Top Attack presentation;
15. boss part states;
16. audio priority table;
17. voice virtualization policy;
18. occlusion/distance implementation;
19. accessibility changes;
20. render performance before/after;
21. audio stress results;
22. map stress results;
23. warning-miss count;
24. remaining issues.

---

# 73. FINAL NON-NEGOTIABLE CONFIRMATIONS

Final report must explicitly confirm:

```text
Map geometry remains canonical.

GameplayTopology is generated from canonical map data.

Vehicle-size route compatibility exists.

Critical chokepoints have capacity metadata.

Spawn fairness validation exists.

Shore-fire feasibility exists.

Boss/naval routes are validated against turn radius.

Runtime gameplay model nodes use stable semantic names.

No gameplay runtime lookup depends on Blender .001 suffix.

Free turrets/mounts have valid pivots.

Critical telegraphs match actual gameplay danger.

Top Attack has distinct readable presentation.

Critical visual cues survive Low graphics mode.

Critical audio warnings survive crowded combat.

P0/P1 warning miss count is reported.

Audio uses bounded voice management / priority / virtualization.

Presentation does not reveal hidden exact enemy state.

Wreck visual, collision and nav states are synchronized.

Accessibility does not rely only on color, audio or haptics.

Weather combat-balance values were not changed by this task.

Boss HP/armour were not changed by this task.
```

Use `Machine_Brigade_MAP_VISUAL_AUDIO_MASTER_SPEC.md` as the detailed source of truth for every implementation detail not repeated above.

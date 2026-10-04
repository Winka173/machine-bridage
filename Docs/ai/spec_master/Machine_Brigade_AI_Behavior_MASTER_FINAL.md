
# MACHINE BRIGADE — AI BEHAVIOR MASTER SPEC
## Canonical AI architecture, combat doctrine, mode doctrine, boss/naval behavior, pathing, traffic, procurement, squad coordination, targeting, support, watchdogs, debug, tests and performance

**Status:** FINAL MASTER SPEC  
**Supersedes:** all previous AI behavior prompts/spec files (including V1/V2).  
**Scope:** all runtime AI behavior for player-side auto-AI, enemy AI, bosses, squads, ground/naval/air units, towers/support, procurement, pathing, targeting and tactical coordination.  
**Do not combine old AI prompts with this file.** If an older prompt conflicts, this file wins.

---

# MASTER RULES

1. AI must be **smart because it plans and coordinates**, not because it cheats.
2. AI must respect fog/intel. Unknown is not safe, but hidden enemy state is not available.
3. No morale system.
4. No retreat-by-health.
5. Boss armour/HP and combat-balance values are outside this AI task.
6. Hard feasibility filters run **before** scoring.
7. Commander chooses WHAT/WHERE, Squad chooses HOW AS GROUP, Tactical chooses LOCAL ACTION, Steering chooses SAFE MOTION.
8. Every armed unit that is idle must have a valid explainable reason.
9. Every important decision must be debuggable through DecisionLog/reason codes.
10. Generated AI docs/data must be regenerated from canonical source; never patch generated output as authority.

---

# PART A — EXISTING FOUNDATION TO PRESERVE

The current repository already contains useful foundations and they must be integrated rather than discarded:

- AiCommander strategic intent.
- Squad state/action layer.
- TacticalAi unit-level combat behavior.
- WorldModel / fog / threat representation.
- DecisionLog.
- mode profiles.
- tactic profiles.
- AI role mapping.
- tower modes.
- artillery standoff concepts.
- firing-spot booking.
- aircraft resupply.
- boss phase data.
- target masks.
- anti-stuck fallback.
- current difficulty framework.

The new architecture extends these systems and may refactor them, but must not silently remove working behavior.

---
# 0. Mục tiêu

Tài liệu này thay thế cách vá từng bug AI bằng một kiến trúc thống nhất.

Các lỗi cần giải quyết:

1. Boss, đặc biệt boss biển, di chuyển và quay thân không tự nhiên.
2. Boss tàu có thể đi lùi hoặc quay đầu chỉ để nhìn mục tiêu.
3. AI mua đơn vị không thể tác động tới trận đánh, ví dụ boss biển mua xe mặt đất ở map mà xe không thể bắn tới.
4. Nhiều xe bị dồn cục, đụng nhau, kẹt cổng, kẹt xác xe và deadlock đối đầu.
5. Anti-stuck kích hoạt quá muộn và có thể ra lệnh “đi tới địch gần nhất” làm tình trạng tệ hơn.
6. AI mua quân theo điểm từng card nhưng quản lý **cơ cấu toàn quân** chưa đủ chặt.
7. Quân mới mua không được gắn vào squad/rally hợp lý.
8. Squad quá yếu vẫn tồn tại, squad quá lớn gây tắc đường.
9. Target selection đôi khi chọn mục tiêu technically có điểm cao nhưng không có firing solution.
10. Các lớp strategic/tactical có thể đưa ra quyết định hợp lệ riêng lẻ nhưng xung đột khi ghép lại.
11. AI chưa đánh giá đủ:
    - map domain;
    - reachability;
    - weapon reach;
    - travel time;
    - congestion;
    - objective timing;
    - overkill;
    - friendly traffic.
12. Debug/telemetry chưa đủ để xác định vì sao một đơn vị mua sai hoặc kẹt.

Mục tiêu cuối:

> AI phải trông như đang **lập kế hoạch**, không phải chỉ phản ứng từng xe.

---

# 1. Những gì hệ hiện tại đã có và nên GIỮ

Không viết lại tất cả từ đầu.

Hệ hiện tại đã có nền kiến trúc tốt:

- `AiCommander`: chiến lược và ý định.
- `SquadLayer`: đội, task, state, formation.
- `TacticalAi`: điều khiển đơn vị.
- `WorldModel`: threat/intel grid.
- `DecisionLog`: giữ lý do và cảnh báo churning.
- 7 squad states:
  - Travel
  - Approach
  - Combat
  - Overwatch
  - Flank
  - Hold
  - Regroup
- 9 squad actions:
  - Attack
  - Hold
  - FlankLeft
  - FlankRight
  - Overwatch
  - Reposition
  - Support
  - Join
  - Regroup
- mode profile.
- tactic profile.
- role mapping.
- unit mapping.
- anti-stuck.
- firing spot booking cho artillery.
- target priorities.
- fog/intel model.

**Không bỏ các hệ này.**

Thay vào đó thêm các lớp còn thiếu:

```text
MapTopology / DomainGraph
        ↓
EngagementFeasibility
        ↓
ForcePlanner / ProcurementDirector
        ↓
AiCommander
        ↓
SquadManager
        ↓
Formation + SharedPath
        ↓
TrafficCoordinator
        ↓
TacticalAi
        ↓
Vehicle / Naval / Aircraft Steering
```

---

# 2. Nguyên tắc thiết kế bắt buộc

## 2.1. Filter trước, score sau

Một lựa chọn **không thể thực hiện** không được phép thắng chỉ vì score cao.

Sai:

```text
score(tank) = 140
score(gunboat) = 120
=> mua tank
```

trong khi tank không có đường tới bất kỳ mục tiêu nào.

Đúng:

```text
tank:
    feasible = false
    => REMOVE

gunboat:
    feasible = true
    => score = 120

=> mua gunboat
```

Áp dụng cùng nguyên tắc cho:

- mua quân;
- chọn mục tiêu;
- chọn firing position;
- chọn flank route;
- chọn squad task;
- chọn support power.

---

## 2.2. Strategic AI không điều khiển từng bánh xe

Commander chọn:

- mục tiêu nào;
- bao nhiêu lực lượng;
- hướng nào;
- khi nào đánh.

Squad chọn:

- tập hợp ở đâu;
- đi tuyến nào;
- formation nào;
- engage hay hold.

Tactical AI chọn:

- mục tiêu cụ thể;
- firing spot;
- local avoidance;
- aim / fire / short reposition.

Steering chọn:

- velocity;
- steering angle;
- collision avoidance.

Không để Commander liên tục ghi đè TacticalAi.

---

## 2.3. Không gian phải là dữ liệu hạng nhất

Mỗi quyết định phải biết:

- mobility domain;
- connected component;
- chokepoint;
- lane width;
- water depth nếu có;
- bridge/gate;
- objective reachability;
- firing reachability;
- danger/threat;
- congestion.

---

## 2.4. Không retreat-by-health

Giữ design hiện tại:

- không morale;
- không tự rút lui chỉ vì HP thấp.

Có thể disengage vì:

- local force ratio bất lợi;
- objective không còn hợp lệ;
- path bị cắt;
- cần regroup;
- commander đổi nhiệm vụ;
- unit không còn firing solution.

HP chỉ được dùng để:
- ưu tiên sửa chữa/support;
- target vulnerability;
- survivability estimate.

Không dùng:

```text
if hp < X:
    retreat
```

làm luật chung.

---

# 3. Kiến trúc tick

Không chạy tất cả AI ở cùng tần số.

## 3.1. Steering tick

```text
10 Hz
```

Phụ trách:

- collision avoidance;
- formation following;
- hull steering;
- velocity obstacle;
- obstacle feeler;
- ship heading.

Có thể giảm xuống 5 Hz trên low-end nếu interpolation render mượt.

---

## 3.2. Tactical tick

```text
4 Hz
```

Mỗi 0.25 s:

- target validity;
- firing solution;
- local reposition;
- standoff;
- jam detection;
- support nearby.

Không đổi strategic task ở đây.

---

## 3.3. Squad tick

```text
2 Hz
```

Mỗi 0.5 s:

- cohesion;
- merge/split;
- formation;
- route progress;
- local power ratio;
- objective state.

---

## 3.4. Commander tick

```text
1 Hz
```

- intent;
- objectives;
- role deficits;
- counter needs;
- attack window;
- reserve allocation.

---

## 3.5. Procurement tick

```text
0.5 Hz
```

Mỗi 2 s hoặc event-trigger:

- CP changed enough;
- unit died;
- enemy composition changed;
- objective phase changed;
- domain accessibility changed.

Không cần đánh giá toàn bộ deck mỗi frame.

---

## 3.6. World Model

Giữ world-model update riêng và stagger theo team.

Không update toàn bộ expensive influence maps cùng một frame cho mọi AI.

---

# 4. MapTopology — lớp còn thiếu quan trọng nhất

Tạo:

```csharp
enum MobilityDomain
{
    Ground,
    Naval,
    Amphibious,
    Air,
    Static
}
```

Mỗi map khi load tạo:

```csharp
sealed class MapTopology
{
    DomainGraph Ground;
    DomainGraph Naval;
    DomainGraph Amphibious;

    IReadOnlyList<ChokePoint> Chokes;
    IReadOnlyList<TrafficLane> MainLanes;
    IReadOnlyList<Region> Regions;
    IReadOnlyList<ObjectiveRegion> Objectives;
}
```

---

# 5. Connected components

Với từng mobility domain, flood-fill/navmesh partition thành component:

```text
GroundComponent 0
GroundComponent 1
...
NavalComponent 0
...
```

Mỗi spawn và objective biết component ID.

Ví dụ:

```text
enemy naval boss: NavalComponent 2
player land objective: GroundComponent 0
```

Ground vehicle không thể tác động sang NavalComponent 2 nếu:

- không có shoreline firing position;
- weapon range không tới;
- không có transport/amphibious connection.

Đây là cơ sở để chặn bug mua quân vô dụng.

---

# 6. EngagementFeasibility

Tạo service:

```csharp
public interface IEngagementFeasibility
{
    InfluenceResult EvaluateUnit(
        UnitDef unit,
        Team side,
        StrategicIntent intent,
        WorldModel world);
}
```

Kết quả:

```csharp
readonly struct InfluenceResult
{
    public bool CanDeploy;
    public bool CanReachObjective;
    public bool CanReachEnemy;
    public bool CanFireFromReachableRegion;
    public float Coverage;          // 0..1
    public float TravelSeconds;
    public float UsefulTargetShare; // 0..1
    public string Reason;
}
```

---

# 7. "Có thể bắn tới" khác "có thể đi tới"

Đây là điểm bắt buộc cho map biển.

Ví dụ pháo bờ:

- ground unit không thể đi xuống biển;
- nhưng có thể đứng trên bờ và range 120 m bắn boss tàu.

Vậy:

```text
CanReachEnemy = false
CanFireFromReachableRegion = true
=> unit vẫn hữu ích
```

Ngược lại MBT range 40 m, bờ cách lane tàu 100 m:

```text
CanReachEnemy = false
CanFireFromReachableRegion = false
=> hard reject
```

---

# 8. Reachable firing region

Cho mỗi target region:

1. lấy các cell reachable của unit;
2. expand target shape theo weapon max range;
3. subtract minimum range;
4. intersect hai vùng.

Nếu intersection rỗng:

```text
no firing solution
```

Pseudo:

```csharp
bool HasReachableFiringPosition(
    NavRegion reachable,
    Region target,
    WeaponEnvelope weapon)
{
    var fireBand = target
        .ExpandedBy(weapon.MaxRange)
        .Minus(target.ExpandedBy(weapon.MinRange));

    return reachable.Intersects(fireBand);
}
```

Cache theo:

```text
(unit mobility class, weapon envelope, target region)
```

không tính lại từng frame.

---

# 9. AI mua quân — thay score đơn bằng ProcurementDirector

Tạo lớp mới:

```csharp
sealed class ProcurementDirector
```

Pipeline:

```text
Available cards
    ↓
Hard legality filter
    ↓
Map/domain feasibility filter
    ↓
Role deficit
    ↓
Enemy counter need
    ↓
Objective fit
    ↓
Army composition
    ↓
Travel/time fit
    ↓
Cost efficiency
    ↓
Diversity penalty
    ↓
Final score
```

---

# 10. Hard filter mua quân

Card bị loại hoàn toàn nếu:

```text
!available
CP < price
unit cap exceeded
spawn unavailable
deployment impossible
zero useful targets AND no utility role
cannot influence current/next objective
```

Đặc biệt:

```csharp
if (!influence.CanReachObjective &&
    !influence.CanReachEnemy &&
    !influence.CanFireFromReachableRegion &&
    !IsStrategicUtility(unit))
{
    reject("no-map-influence");
}
```

---

# 11. Naval boss / naval map purchase rule

Khi strategic anchor là naval boss:

Không dùng:

```text
if boss is naval:
    only buy naval
```

vì có thể map vẫn có bờ và objective đất.

Dùng:

```text
buy if unit can influence boss battle or an active objective
```

Ground unit hợp lệ nếu:

- có shoreline firing solution;
- bảo vệ được coastal battery;
- chiếm/giữ objective đất;
- bảo vệ spawn/factory;
- tham gia secondary mission.

Ground unit bị reject nếu:

- mọi reachable GroundComponent đều nằm ngoài range mọi enemy/objective;
- không có nhiệm vụ utility.

---

# 12. Procurement score chuẩn

Sau hard filter:

```text
FinalScore =
    0.22 * RoleDeficit
  + 0.18 * CounterNeed
  + 0.15 * ObjectiveFit
  + 0.12 * MapInfluence
  + 0.10 * TimingFit
  + 0.08 * SurvivabilityFit
  + 0.06 * SupportSynergy
  + 0.05 * CostEfficiency
  + 0.04 * TacticPreference
  - RedundancyPenalty
  - CongestionPenalty
  - LongTravelPenalty
```

Tất cả input normalize 0..1.

---

# 13. Role deficit

Không mua theo unit ID trước.

Lập role budget:

```text
Frontline
AntiTank
AntiAir
Artillery
Recon
Engineer
ElectronicWarfare
Drone
FastFlank
Siege
NavalScreen
NavalStrike
AirCover
```

Mỗi tactic đặt desired share.

Ví dụ Balanced:

```text
Frontline       0.28
AntiTank        0.15
AntiAir         0.12
Artillery       0.10
Recon           0.07
Engineer        0.06
FastFlank       0.08
Electronic      0.04
Flexible        0.10
```

Không bắt buộc tổng role map trực tiếp 1:1 vì unit có thể có nhiều role.

---

# 14. Enemy counter need

Dựa trên **observed/remembered intel**, không cheat fog.

Ví dụ:

```text
enemy air threat high
=> AntiAir deficit increases

enemy Armour4/5 high
=> AntiTank increases

enemy artillery high
=> counterbattery / fast flank increases

enemy drones high
=> AA/fragmentation/drone counter increases
```

Decay counter need khi intel stale.

---

# 15. Không overreact theo 1 contact

Dùng smoothed composition:

```text
ObservedShareEMA =
    lerp(old, current, 0.20)
```

Không đổi build vì vừa thấy 1 aircraft.

Mismatch event chỉ kích khi:

```text
confidence >= threshold
AND duration >= 4 s
```

---

# 16. Purchase batch

Không mua một card rồi đánh giá lại lập tức nếu đang cần squad mới.

Tạo `PurchasePlan` tối đa 3–5 card:

```csharp
sealed record PurchasePlan(
    IReadOnlyList<CardId> Cards,
    string Purpose,
    float ExpectedPower,
    int CpCost);
```

Ví dụ:

```text
Purpose: "shore denial"
- long_sam
- tank_destroyer
- recon_drone
```

Kế hoạch có thể bị hủy khi điều kiện thay đổi.

---

# 17. Không mua vượt khả năng điều khiển

Thêm congestion-aware penalty.

Nếu team đã có:

- quá nhiều unit bán kính lớn;
- quá nhiều artillery cần parking;
- chokepoint map rất hẹp;

thì giảm score thêm heavy unit.

Ví dụ:

```text
CongestionPenalty =
    DensityPressure
  * UnitFootprintFactor
  * ChokeDependency
```

Đây là cách tránh 20 heavy tank cùng lao qua một cổng.

---

# 18. Reserve CP

Commander giữ CP nếu:

- sắp đủ tiền mua counter quan trọng;
- expected boss phase trong vài giây;
- current force composition đã đủ nhưng reinforcement chưa cần;
- aircraft cap đầy;
- ground cap gần đầy.

Không giữ tiền vô hạn.

Max bank vẫn theo economy/mode data hiện tại.

---

# 19. Squad lifecycle

Tạo lifecycle rõ:

```text
Forming
Rallying
Ready
Committed
Reorganizing
Dissolving
```

Đây là lifecycle nội bộ, không thay 7 tactical states hiện tại.

---

# 20. Squad size

Default:

```text
desired = 5–7 combat units
min viable = 3
max = 9
```

Exception:

- artillery battery: 2–4 + escort
- air group: theo aircraft logic
- naval boss escort: 3–6
- swarm/drone: own rules

Không tạo squad 15–20 ground vehicles.

---

# 21. Merge squad

Merge khi:

```text
strength < 45% desired
AND compatible tasks
AND distance < 35 m
AND no immediate combat
```

Không merge nếu:

- một squad đang flank opposite side;
- một squad là reserve;
- khác mobility domain;
- merge làm vượt max size.

---

# 22. Split squad

Split khi:

```text
members > max
OR path bottleneck width too small
OR two objectives require simultaneous presence
```

Choke split:

```text
if requiredFormationWidth > 0.75 * chokeWidth
    split movement packets
```

Hai packet đi cách nhau 2–4 s.

---

# 23. Reinforcement

Quân mới không chạy thẳng tới squad leader.

Chọn `RendezvousPoint`:

- sau tuyến squad;
- reachable;
- không nằm trong threat cao;
- không nằm ở doorway;
- không chắn main traffic route.

Squad nhận reinforcement khi reinforcement vào bán kính:

```text
12–20 m
```

---

# 24. Reserve

Commander nên luôn cố giữ:

```text
15–25% combat power
```

làm reserve trong mode cho phép.

Reserve dùng để:

- vá flank;
- chặn breakthrough;
- thay squad mất sức mạnh;
- phản ứng air drop;
- giữ HQ.

Không cần reserve trong scripted wave/boss-only encounter nếu mode profile không phù hợp.

---

# 25. Cohesion

Không yêu cầu mọi unit dính sát formation slot.

Cohesion score:

```text
C =
  0.45 * memberDistanceScore
+ 0.30 * roleCoverageScore
+ 0.25 * routeProgressScore
```

Regroup nếu:

```text
C < 0.55
```

trong > 2 s và không trong immediate survival situation.

---

# 26. Formation

Giữ 5 formation hiện tại nhưng formalize slot assignment:

## Travel
- column/loose column
- ưu tiên narrow width

## Spread
- tăng lateral separation
- chống splash

## Hold
- frontline arc
- support behind

## Flank
- wedge/echelon
- fast unit outer side

## Regroup
- compact but non-overlapping

---

# 27. Role placement trong formation

Thứ tự:

```text
Front:
    heavy / durable / breacher

Middle:
    main gun / generalist / AT

Rear:
    artillery / SAM / EW / repair

Outer:
    recon / fast flank

Never front:
    artillery
    ammo carrier
    fragile radar
```

---

# 28. Shared squad path

Không cho mỗi unit A* độc lập tới cùng điểm.

Squad tạo:

```text
SharedPath / FlowCorridor
```

rồi unit theo formation offset.

Có thể triển khai hai cấp:

```text
Global:
    region graph / A*

Local:
    flow field / corridor steering
```

Lợi ích:

- ít CPU hơn;
- ít unit chọn hai đường khác nhau;
- giảm giao cắt;
- formation tự nhiên hơn.

---

# 29. Flow field / corridor

Đối với lệnh group tới cùng objective:

1. build integration field/corridor một lần;
2. unit đọc hướng local;
3. local steering thêm separation/avoidance.

Không bắt buộc rewrite toàn engine thành full flow-field ngay.

Phase 1 có thể:

```text
shared waypoint corridor + local avoidance
```

Phase 2:

```text
flow field tiles
```

---

# 30. TrafficCoordinator

Tạo subsystem mới:

```csharp
sealed class TrafficCoordinator
```

Nó quản lý:

- gate;
- choke;
- bridge;
- spawn exit;
- narrow road;
- boss corridor;
- firing parking.

---

# 31. Reservation

Mỗi choke có reservation token:

```csharp
sealed class PassageReservation
{
    SquadId Owner;
    float EnterTime;
    float ExpireTime;
    TravelDirection Direction;
    int Priority;
}
```

Squad cùng hướng có thể batch.

Hai hướng ngược nhau luân phiên.

---

# 32. Right-of-way priority

Đề xuất:

```text
100 boss / scripted convoy
90  unit đang ở giữa choke
80  heavy / super-heavy
70  squad main effort
60  artillery reposition
50  normal combat
40  reinforcement
30  scout
```

Không đổi liên tục mỗi frame.

Priority giữ ít nhất 2 s để tránh cả hai bên cùng nhường rồi cùng đi.

---

# 33. Boss corridor

Boss lớn luôn reserve corridor theo:

```text
boss radius + 2.5 m
```

Friendly unit tránh corridor nếu boss cách < 25–35 m.

Không để jeep đứng trước mũi boss khiến boss quay hoặc dừng.

---

# 34. Local collision avoidance

Không chỉ dùng repulsion force đơn giản.

Dùng reciprocal velocity obstacle kiểu ORCA/RVO hoặc approximation deterministic.

Input neighbor:

```text
position
velocity
radius
priority
desiredVelocity
```

Output:

```text
safeVelocity
```

---

# 35. Deterministic ORCA-lite

Nếu full ORCA khó integrate, dùng ORCA-lite:

1. predict position sau `timeHorizon = 1.5 s`;
2. nếu circles overlap:
   - tính lateral avoidance vector;
   - unit priority thấp chịu 70–100% tránh;
   - unit priority cao chịu 0–30%;
3. clamp acceleration;
4. giữ preferred forward velocity.

Pseudo:

```csharp
Vector2 Avoid(Unit self, Unit other)
{
    var relPos = other.Pos - self.Pos;
    var relVel = self.Vel - other.Vel;

    if (!WillOverlap(relPos, relVel, self.R + other.R, 1.5f))
        return Vector2.Zero;

    var side = DeterministicPassingSide(self.Id, other.Id, relPos);

    float responsibility =
        AvoidanceResponsibility(self.Priority, other.Priority);

    return side * responsibility;
}
```

---

# 36. Deterministic passing side

Không random left/right mỗi tick.

```text
pairKey = hash(min(idA,idB), max(idA,idB))
```

Pair chọn một passing side cố định cho tới khi tách > 2× avoidance radius.

Ngăn wobble:

```text
left-right-left-right
```

---

# 37. Jam detector mới

Anti-stuck hiện tại không nên chờ tới 10–12 s mới phản ứng.

Theo dõi:

```text
distanceProgress
pathProgress
desiredSpeed
actualSpeed
neighborDensity
blockingEntity
```

---

# 38. Jam stages

## Stage 0 — normal

Không có vấn đề.

## Stage 1 — soft jam

Điều kiện:

```text
move order active
actual speed < 25% desired
for >= 1.5 s
```

Hành động:

- increase separation;
- temporarily loosen formation;
- side-step.

---

## Stage 2 — local replan

Sau:

```text
3 s
```

- chọn local waypoint lệch 3–6 m;
- tránh occupied cells;
- không đổi strategic target.

---

## Stage 3 — yield / priority resolution

Sau:

```text
5 s
```

Nếu blocker friendly:

- TrafficCoordinator chọn một bên nhường;
- loser dừng/side-step;
- winner giữ đường.

---

## Stage 4 — corridor replan

Sau:

```text
8 s
```

- squad recompute corridor;
- tăng congestion cost cell;
- tránh choke hiện tại nếu alternative cost < 1.5×.

---

## Stage 5 — emergency unjam

Sau:

```text
12 s
```

Ground vehicle:
- formation break;
- short reverse **chỉ nếu vehicle cho phép reverse**;
- hoặc pivot + alternate local target.

Naval:
- **không reverse**;
- widen turn / alternate waypoint.

Không teleport unit trong normal gameplay.

Nếu game hiện có emergency relocation, chỉ giữ như fail-safe debug cuối cùng và log `SEVERE_UNSTUCK`.

---

# 39. Wreck-aware navigation

Wreck hiện là obstacle trong một khoảng thời gian.

Bắt buộc:

```text
on WreckSpawn:
    dirty local nav cells immediately

on WreckRemoved:
    dirty again
```

Không đợi periodic full nav rebuild.

Wreck có congestion cost cao trước khi thành hard block nếu animation đang chìm/đổ.

---

# 40. Spawn exit

Mỗi spawn có:

```text
ExitBox
ClearZone
RallyRing
```

AI không được chọn firing spot/rally point trong ExitBox.

Nếu exit blocked > 2 s:

- unit ngoài exit nhường trước;
- newly spawned unit được high traffic priority trong 3 s.

---

# 41. Artillery parking

Giữ reservation firing spot hiện có nhưng mở rộng:

- một artillery spot có occupancy lease;
- expire nếu unit rời > 5 m;
- artillery mới không chọn spot trong 1.5× friendly splash spacing.

Không đỗ pháo trên main route.

---

# 42. Target selection — hard feasibility

Trước mọi target score:

```text
Targetable?
Within weapon target mask?
Has line/arc solution?
Reachable firing solution?
Not inside min range trap without escape?
```

Nếu fail:

```text
score = -infinity
```

---

# 43. Weapon-target utility

Mỗi candidate:

```text
Utility =
    ExpectedDamagePerSecond
  * HitProbability
  * TargetValue
  * RangeAccess
  * AngleAccess
  * TimeOnTarget
```

Không chỉ “closest” hay “strongest”.

---

# 44. Overkill control

Nếu nhiều weapon nhắm cùng mục tiêu:

```text
CommittedDamage =
sum(projectiles_in_flight expected damage)
```

Nếu:

```text
CommittedDamage > targetEffectiveHp * 1.15
```

unit chưa bắn chọn target khác nếu có.

Ngoại lệ:

- boss part focus;
- Executioner/kill objective;
- target cực nguy hiểm cần chắc chắn hạ.

---

# 45. Target stickiness

Tránh đổi target liên tục.

Bonus:

```text
current target:
    +15% score
```

trong:

```text
1.5 s
```

sau khi acquire.

Break ngay nếu:

- invalid;
- unreachable;
- target leaves weapon domain;
- commander focus target override.

---

# 46. Threat vs opportunity

Score target:

```text
TargetScore =
    ThreatToSelf          * 0.20
  + ThreatToObjective     * 0.22
  + WeaponSuitability     * 0.18
  + KillOpportunity       * 0.12
  + StrategicValue        * 0.12
  + FocusFire             * 0.08
  + DistanceEfficiency    * 0.08
```

Role modifier áp sau.

---

# 47. Không chase mục tiêu unreachable

Nếu target rời connected firing-access region:

```text
drop target
```

Không để tank đi vòng toàn map vì một helicopter hoặc ship.

---

# 48. Boss architecture

Boss không nên chỉ là “unit lớn với TacticalAi”.

Tạo:

```text
BossBrain
    ├── BossMissionController
    ├── BossMovementController
    ├── BossWeaponDirector
    ├── BossPhaseController
    ├── BossEscortCoordinator
    └── BossTargetDirector
```

---

# 49. Boss mission anchor

Mỗi boss luôn có một `MissionAnchor`:

- route node;
- arena center;
- target structure;
- naval lane;
- escort objective.

Boss movement ưu tiên anchor hơn target.

Không:

```text
hull turns toward current target
```

trừ boss melee/direct frontal weapon được design như vậy.

---

# 50. Hull và turret phải tách

Đây là fix lớn cho boss tàu.

```text
Hull:
    follows route / movement plan

Turret:
    tracks combat target
```

Boss không quay thân chỉ vì turret đổi mục tiêu.

Hull target chỉ đổi khi:

- route requires;
- broadside controller yêu cầu;
- collision;
- phase movement;
- escape scripted.

---

# 51. Naval Boss Controller

Tạo riêng:

```csharp
sealed class NavalBossMovementController
```

Không dùng generic ground vehicle steering.

---

# 52. Naval reverse

Final rule:

```text
naval boss allowReverse = false
```

Trong combat bình thường.

Không được:

- đi lùi để giữ range;
- đi lùi vì target phía sau;
- đổi forward thành reverse vì local avoidance.

Nếu đường trước bị chặn:

- giảm ga;
- tăng turn;
- chọn alternate lane;
- orbit;
- stop ngắn.

Không reverse.

---

# 53. Minimum turn radius

Từ data:

```text
Rmin = speed / angularSpeedRad
```

Ví dụ:

```text
speed = 2.6 m/s
turnRate = 8 deg/s
angular = 0.1396 rad/s

Rmin ≈ 18.6 m
```

Path planner không được tạo góc cua nhỏ hơn Rmin.

Dùng:

```text
planningRadius = max(collisionRadius, Rmin * 1.1)
```

---

# 54. Naval look-ahead steering

Không steer thẳng waypoint gần nhất.

Dùng look-ahead:

```text
lookAhead =
clamp(
    speed * 6,
    length * 1.5,
    length * 4.0)
```

Chọn point trên lane spline phía trước.

Giảm wobble.

---

# 55. Heading hysteresis

Không đổi desired heading vì target dịch 2–3 độ.

```text
heading deadband = 5°
```

Broadside state:

```text
enter broadside at desired ±8°
leave only outside ±15°
```

Tạo hysteresis.

---

# 56. Broadside controller

Không phải boss tàu nào cũng luôn quay 90°.

Tính từ mount arcs.

```text
BroadsideValue(angle) =
sum(
    weaponDps
    * CanBearAtHullAngle(angle)
    * targetSuitability
)
```

Sample candidate hull offsets:

```text
-80 -60 -40 -20 0 +20 +40 +60 +80
```

Chọn góc có:

- nhiều effective DPS;
- không phá route;
- không cần turn quá lớn;
- giữ safe lane.

---

# 57. Broadside preference smoothing

```text
DesiredHullAngle =
lerp(previousDesired, bestCandidate, 0.15)
```

Không snap.

---

# 58. Target phía sau tàu

Nếu turret bắn được:

```text
hull continues route
turret rotates
```

Nếu turret không bắn được:

- đợi natural turn;
- target director chọn target khác;
- không quay 180° ngay.

Chỉ quay cả tàu nếu target là mission-critical và expected value vượt threshold.

---

# 59. Naval spacing

Friendly ship desired separation:

```text
max(
    radiusA + radiusB + 4 m,
    0.5 * max(lengthA,lengthB)
)
```

Boss ship separation lớn hơn:

```text
+ 8–15 m
```

---

# 60. Ship collision prediction

Predict CPA — Closest Point of Approach.

```text
tCPA =
-clamp(dot(relPos, relVel) / |relVel|², 0, horizon)
```

Nếu predicted distance < safe separation:

- early turn;
- speed reduction.

Không chờ hull overlap mới tránh.

Horizon:

```text
6–10 s
```

cho tàu lớn.

---

# 61. Naval lane

Map naval routes phải là spline/corridor có width.

Mỗi point biết:

```text
centre
tangent
width
depth
next
branch
```

Boss không target arbitrary XY trong nước nếu lane exists.

---

# 62. Naval escape / phase

Các field hiện có như:

```text
naval_escape_phase
naval_escape_speed_m_s
naval_lanes
naval_role
```

phải được BossMissionController sử dụng trực tiếp.

Phase change tạo new route goal.

Không để TacticalAi override route bằng enemy target.

---

# 63. Ground boss

Boss ground lớn cũng dùng kinematic-aware controller.

Tracked boss:

- có reverse nếu design cho phép;
- nhưng không reverse liên tục theo target;
- hull follows mission / lane;
- turret independent.

Mobile fortress phải reserve traffic corridor.

---

# 64. Flying boss

Air boss:

- dùng orbit/attack lane;
- không hover-turn 180 liên tục nếu frame/model là fixed-wing;
- separate craft type:
  - rotor/hover
  - fixed-wing
  - airship.

Không dùng cùng steering law.

---

# 65. Boss target director

Boss target score thêm:

```text
ThreatToBossPart
ThreatToEscort
ThreatToMission
CanWeaponBear
TimeToAim
Overkill
TargetPersistence
```

Boss không quay thân vì target score cao nếu weapon bearing không yêu cầu hull turn.

---

# 66. Boss escorts

EscortCoordinator giữ role:

```text
screen
AA
repair
EW
spot
strike
```

Escort anchor vào boss nhưng không đứng ngay hull collision radius.

Rings:

```text
inner forbidden: bossRadius + 4 m
screen ring:      +10–18 m
support ring:     +18–30 m
```

---

# 67. Boss purchase / factory spawn

Nếu boss/factory sinh unit:

Dùng cùng `EngagementFeasibility`.

Không spawn ground escort chỉ vì danh sách factory chứa ground unit nếu map region không dùng được.

Nếu scripted story bắt buộc spawn:
- spawn được;
- nhưng phải có explicit mission role / reachable objective.

---

# 68. Squad power estimate

Không dùng chỉ HP hoặc số unit.

```text
CombatPower =
    ExpectedDpsAgainstLocalMix
  * SurvivabilitySeconds
  * Availability
  * RangeFactor
  * MobilityAccess
```

Normalize.

---

# 69. Local engagement odds

```text
Odds = friendlyCombatPower / max(enemyCombatPower, epsilon)
```

Tactic modifies threshold.

Ví dụ:

```text
balanced:      1.10
blitz:         0.90
attrition:     1.40
breakthrough:  1.00 on main effort
```

Không hardcode trong code; lấy tactic data.

---

# 70. Objective urgency

Attack threshold giảm khi:

- time near end;
- objective bleed severe;
- HQ threatened;
- boss phase requires pressure.

```text
EffectiveThreshold =
BaseThreshold * lerp(1.0, 0.75, Urgency)
```

Không thấp hơn tactic-specific minimum.

---

# 71. Army management theo objective

Commander không chia unit theo khoảng cách đơn thuần.

Mỗi objective tạo demand:

```text
ObjectiveDemand
{
    RequiredPower;
    RequiredAA;
    RequiredAT;
    RequiredRecon;
    RequiredEngineer;
    Deadline;
}
```

Assignment giải bài toán deficit.

---

# 72. Assignment utility

```text
AssignmentScore =
    RoleFit
  + DistanceFit
  + CurrentTaskCompatibility
  + DomainAccess
  - ReassignmentCost
```

Không đổi squad liên tục.

---

# 73. Task commitment

Giữ commit windows hiện có.

Reassignment chỉ break commit khi:

```text
emergency severity >= High
OR task invalid
OR phase changed
```

Ngăn churning.

---

# 74. Join action

`Join` phải có rendezvous.

Không:

```text
chase moving squad centroid forever
```

Dự đoán intercept point:

```text
futureSquadPos =
squadPos + squadVelocity * clamp(travelTime, 0, 6)
```

---

# 75. Regroup

Regroup point:

- reachable by all squad members;
- behind current combat line;
- not in splash threat;
- not choke;
- not main traffic route.

---

# 76. Flank route

Flank route score:

```text
PathCost
+ ThreatCost
+ CongestionCost
+ ExposureCost
```

Không chọn flank nếu route width quá nhỏ cho squad.

---

# 77. Artillery

Artillery:

- giữ ngoài min range;
- dùng booked firing spot;
- không theo frontline vào choke;
- reposition nếu target unavailable;
- counterbattery khi world model confidence đủ cao.

---

# 78. AA

AA không chase aircraft vô hạn.

AA leash theo:

- protected squad;
- boss;
- objective.

Nếu aircraft đi xa:

```text
return to cover anchor
```

---

# 79. Recon

Recon priority:

- unknown cells near strategic route;
- suspected artillery;
- flank path validation;
- boss spot requirement.

Không lao vào strongest visible target.

---

# 80. Engineer/repair

Engineer không đứng trước frontline.

Repair target score:

```text
strategicValue
* repairNeed
/ travelRisk
```

Không dùng “HP thấp nhất” duy nhất.

Không retreat-by-health; chỉ repair prioritization.

---

# 81. EW

Jammer đứng sao cho bubble cover:

- main effort;
- boss;
- artillery.

Không chạy tới enemy chỉ để jam nếu sẽ rời friendly support.

---

# 82. Aircraft

Giữ hệ resupply hiện tại nhưng thêm:

- sortie grouping;
- avoid sending aircraft one-by-one;
- target package.
- strike group waits max 2–4 s cho wingman nếu profile cho phép.

Air superiority:
- fighter first;
- strike follows window.

---

# 83. Target accessibility cache

Cache:

```text
CanUnitClassInfluenceRegion
```

Invalidate khi:

- gate opens/closes;
- bridge destroyed;
- hardpoint built;
- wreck blocks narrow path;
- scripted terrain changes.

---

# 84. Dynamic obstacle cost

Không mọi obstacle là infinite ngay lập tức.

Cost categories:

```text
StaticWall          INF
ClosedGate          INF or gated
FriendlyUnit        dynamic soft
EnemyUnit           tactical
Wreck               high / hard
ReservedFiringSpot  high
BossCorridor        very high
TrafficLane         low movement cost, high parking cost
```

---

# 85. Choke queue

Unit không dồn tới cùng cửa.

Tạo queue positions trước choke:

```text
Q1, Q2, Q3...
```

Squad packet đợi ở queue ring.

---

# 86. Formation through choke

Trước choke:

```text
formation -> TravelColumn
```

Sau choke:

```text
restore requested formation
```

Không cố giữ Spread qua cửa hẹp.

---

# 87. Minimum separation

Dynamic:

```text
base =
radiusA + radiusB + 0.5

splash threat:
base *= 1.3–1.8

travel column:
base *= 0.85
```

Không cho overlap collider.

---

# 88. Target firing arc

Weapon mount phải expose:

```text
yaw min/max
pitch min/max
hull-dependent
```

Target score = 0 nếu weapon không thể bear trong acceptable aim time.

---

# 89. Aim-time penalty

```text
AimPenalty =
exp(-AimSeconds / 4)
```

Boss không ưu tiên mục tiêu cần quay turret/hull rất lâu nếu có mục tiêu gần cùng giá trị.

---

# 90. Fire while moving

Nếu unit `fires_while_moving`:

- không stop chỉ để bắn trừ accuracy reason.

Nếu không:
- tactical controller chọn firing stop;
- traffic coordinator không cho stop trên choke.

---

# 91. Movement reservation vs firing reservation

Tách:

```text
TransitReservation
FiringReservation
HoldReservation
```

Firing spot không được reserve trên transit route.

---

# 92. Difficulty

Không làm VeryHard bằng cách cheat hidden info.

Difficulty thay:

- reaction latency;
- target focus;
- formation discipline;
- counter confidence threshold;
- purchase planning horizon;
- jam response speed;
- attack timing.

Không tăng omniscience.

---

# 93. Suggested difficulty values

## Easy
```text
reaction 1.3x slower
focus coordination 0.6
counter confidence 0.80
procurement lookahead 1 purchase
```

## Normal
```text
baseline
confidence 0.70
lookahead 2–3 purchases
```

## Hard
```text
reaction 0.85x
focus 0.9
confidence 0.60
lookahead 3–4 purchases
```

## VeryHard
```text
reaction 0.70x
focus 1.0
confidence 0.55
lookahead 4–5 purchases
```

Không thay raw unit stats trong AI behavior layer.

---

# 94. DecisionLog mở rộng

Mỗi purchase log:

```text
BUY tank_destroyer score=0.83
+ role deficit +0.22
+ heavy enemy +0.18
+ objective fit +0.13
+ map influence +0.12
- travel -0.04
runner-up sam_launcher=0.75
```

Rejected card:

```text
REJECT main_battle_tank:
no reachable firing region against active naval objective
```

Đây là log cực quan trọng để tìm bug.

---

# 95. Movement debug

Unit debug panel:

```text
DesiredVelocity
SafeVelocity
FormationSlot
SharedPathId
TrafficPriority
JamStage
BlockerId
LocalTarget
StrategicTask
```

---

# 96. Naval debug

Boss ship debug:

```text
LaneId
RouteProgress
DesiredHullHeading
ActualHeading
BroadsideCandidate
TurnRadius
TargetId
HullTargetReason
TurretTargets[]
CPA threat
```

---

# 97. Squad debug

```text
Task
State
Action
Cohesion
Power
EnemyPower
AttackThreshold
Formation
Route
Reservation
MemberCount
RoleDeficits
```

---

# 98. Performance budget

Không scan mọi unit với mọi unit.

Dùng spatial hash:

```text
cell = 8–12 m
```

cho neighbor query.

Local avoidance chỉ xét:

```text
nearest 8–12 relevant neighbors
```

Boss có radius query lớn hơn.

---

# 99. Determinism

Tất cả tie-break:

```text
stable ID
fixed hash
fixed-point or deterministic float order
```

Không `Random()` trong steering quyết định trái/phải mỗi frame.

---

# 100. C# — feasibility skeleton

```csharp
public readonly record struct InfluenceResult(
    bool CanDeploy,
    bool CanReachObjective,
    bool CanReachEnemy,
    bool CanFireFromReachableRegion,
    float Coverage,
    float TravelSeconds,
    float UsefulTargetShare,
    string Reason)
{
    public bool Useful =>
        CanDeploy &&
        (CanReachObjective ||
         CanReachEnemy ||
         CanFireFromReachableRegion ||
         UsefulTargetShare > 0f);
}

public sealed class EngagementFeasibility
{
    private readonly MapTopology topology;
    private readonly WeaponEnvelopeCache envelopes;

    public InfluenceResult Evaluate(
        UnitDef unit,
        StrategicIntent intent,
        WorldModel world,
        Team side)
    {
        var domain = topology.For(unit.MobilityDomain);

        if (!domain.CanDeploy(side, unit))
            return new(false, false, false, false, 0, float.PositiveInfinity, 0,
                "deployment-unreachable");

        var reachable = domain.ReachableFromSpawn(side, unit);

        bool objective = intent.PrimaryObjective is not null &&
            reachable.Intersects(intent.PrimaryObjective.Region);

        bool enemy = world.KnownEnemyRegions
            .Any(r => reachable.Intersects(r.Region));

        bool fire = HasAnyReachableFiringRegion(
            unit, reachable, world, intent);

        float targetShare = ComputeUsefulTargetShare(unit, world);
        float coverage = ComputeCoverage(unit, reachable, intent, world);
        float travel = EstimateTravelSeconds(unit, reachable, intent);

        string reason = fire ? "reachable-fire"
            : objective ? "reachable-objective"
            : enemy ? "reachable-enemy"
            : "no-map-influence";

        return new(true, objective, enemy, fire,
            coverage, travel, targetShare, reason);
    }
}
```

---

# 101. C# — procurement skeleton

```csharp
public CardChoice? ChooseCard(
    AiCommander commander,
    IReadOnlyList<CardDef> cards,
    ProcurementContext ctx)
{
    CardChoice? best = null;

    foreach (var card in cards)
    {
        if (!BasicLegal(card, ctx))
            continue;

        var influence = feasibility.Evaluate(
            card.Unit, ctx.Intent, ctx.World, ctx.Team);

        if (!influence.Useful &&
            !IsStrategicUtility(card.Unit, ctx))
        {
            log.Reject(card.Id, "no-map-influence");
            continue;
        }

        float score =
            0.22f * RoleDeficit(card, ctx) +
            0.18f * CounterNeed(card, ctx) +
            0.15f * ObjectiveFit(card, ctx) +
            0.12f * influence.Coverage +
            0.10f * TimingFit(card, ctx) +
            0.08f * SurvivabilityFit(card, ctx) +
            0.06f * SupportSynergy(card, ctx) +
            0.05f * CostEfficiency(card, ctx) +
            0.04f * TacticPreference(card, ctx);

        score -= RedundancyPenalty(card, ctx);
        score -= CongestionPenalty(card, ctx);
        score -= LongTravelPenalty(influence, ctx);

        best = CardChoice.Better(best, card, score);
    }

    return best;
}
```

---

# 102. C# — jam detector

```csharp
public enum JamStage
{
    None,
    Soft,
    LocalReplan,
    Yield,
    CorridorReplan,
    Emergency
}

public sealed class JamTracker
{
    public JamStage Stage { get; private set; }
    public float LowProgressSeconds { get; private set; }

    public void Tick(Unit u, float dt)
    {
        if (!u.HasMoveIntent || u.CanEngageCurrentTarget)
        {
            Reset();
            return;
        }

        float desired = MathF.Max(0.1f, u.DesiredSpeed);
        bool low =
            u.ActualSpeed < desired * 0.25f &&
            u.PathProgressPerSecond < 0.25f;

        LowProgressSeconds = low
            ? LowProgressSeconds + dt
            : MathF.Max(0, LowProgressSeconds - dt * 2);

        Stage =
            LowProgressSeconds >= 12 ? JamStage.Emergency :
            LowProgressSeconds >= 8  ? JamStage.CorridorReplan :
            LowProgressSeconds >= 5  ? JamStage.Yield :
            LowProgressSeconds >= 3  ? JamStage.LocalReplan :
            LowProgressSeconds >= 1.5f ? JamStage.Soft :
            JamStage.None;
    }

    public void Reset()
    {
        Stage = JamStage.None;
        LowProgressSeconds = 0;
    }
}
```

---

# 103. C# — naval steering

```csharp
public sealed class NavalBossMovementController
{
    public Vector2 ComputeDesiredVelocity(
        Boss boss,
        NavalLane lane,
        NavalContext ctx)
    {
        float omega =
            MathF.Max(0.01f,
                boss.TurnRateDegPerSec * MathF.PI / 180f);

        float minTurnRadius =
            boss.SpeedMps / omega;

        float lookAhead =
            Math.Clamp(
                boss.SpeedMps * 6f,
                boss.LengthM * 1.5f,
                boss.LengthM * 4f);

        Vector2 lanePoint =
            lane.PointAhead(boss.RouteProgress, lookAhead);

        Vector2 laneHeading =
            Vector2.Normalize(lanePoint - boss.Position);

        float broadsideOffset =
            ctx.Broadside.ChooseOffset(
                boss,
                ctx.Targets,
                minTurnRadius);

        Vector2 preferred =
            Rotate(laneHeading, broadsideOffset);

        preferred =
            ApplyHeadingDeadband(
                boss.Forward,
                preferred,
                5f);

        preferred =
            ctx.CollisionAvoidance.SolveNaval(
                boss,
                preferred,
                horizonSeconds: 8f);

        // IMPORTANT: naval boss cannot reverse.
        if (Vector2.Dot(preferred, boss.Forward) < 0f)
            preferred = PerpendicularForwardChoice(
                boss.Forward, preferred);

        return preferred * boss.SpeedMps;
    }
}
```

---

# 104. C# — broadside scoring

```csharp
float ScoreHullOffset(
    Boss boss,
    Target target,
    float offsetDeg)
{
    float dps = 0f;

    foreach (var mount in boss.Mounts)
    {
        if (!mount.Enabled)
            continue;

        if (!mount.Weapon.CanTarget(target))
            continue;

        if (!mount.CanBearAtHullOffset(
                target.Position,
                boss.Position,
                boss.HeadingDeg + offsetDeg))
            continue;

        dps += mount.Weapon.ExpectedDps(target);
    }

    float turnCost =
        MathF.Abs(offsetDeg) / MathF.Max(1f, boss.TurnRateDegPerSec);

    float routePenalty =
        RouteDeviationPenalty(boss, offsetDeg);

    return dps
        - turnCost * 0.08f
        - routePenalty;
}
```

---

# 105. C# — target hard-filter

```csharp
bool IsCandidate(
    Unit self,
    Weapon weapon,
    Entity target,
    TacticalContext ctx)
{
    if (!target.Alive)
        return false;

    if (!weapon.TargetMask.Allows(target))
        return false;

    if (!ctx.Visibility.CanLegallyKnow(target))
        return false;

    if (!weapon.CanBear(self, target))
        return false;

    if (!ctx.FiringAccess.HasSolution(
            self, weapon, target))
        return false;

    return true;
}
```

---

# 106. C# — target score with overkill

```csharp
float ScoreTarget(
    Unit self,
    Weapon weapon,
    Entity target,
    TacticalContext ctx)
{
    float committed =
        ctx.Projectiles.ExpectedIncomingDamage(target);

    if (committed > target.EffectiveHp * 1.15f &&
        !ctx.FocusFire.IsForced(target))
        return -1000f;

    float score =
        0.20f * ThreatToSelf(target, self) +
        0.22f * ThreatToObjective(target, ctx) +
        0.18f * WeaponSuitability(weapon, target) +
        0.12f * KillOpportunity(target, committed) +
        0.12f * StrategicValue(target, ctx) +
        0.08f * FocusValue(target, ctx) +
        0.08f * DistanceEfficiency(self, weapon, target);

    if (self.CurrentTarget == target)
        score *= 1.15f;

    return score;
}
```

---

# 107. Tunables đề xuất mới

Thêm dưới `ai`:

```json
{
  "navigation": {
    "steeringHz": 10,
    "tacticalHz": 4,
    "squadHz": 2,
    "commanderHz": 1,

    "jamSoftS": 1.5,
    "jamReplanS": 3.0,
    "jamYieldS": 5.0,
    "jamCorridorS": 8.0,
    "jamEmergencyS": 12.0,

    "avoidanceHorizonGroundS": 1.5,
    "avoidanceHorizonNavalS": 8.0,

    "chokeBatchGapS": 2.5,
    "spawnPriorityS": 3.0
  },

  "squads": {
    "desiredSize": 6,
    "minViable": 3,
    "maxSize": 9,
    "mergeStrengthShare": 0.45,
    "mergeDistanceM": 35,
    "regroupCohesion": 0.55,
    "reinforcementJoinM": 16,
    "reservePowerShare": 0.20
  },

  "targeting": {
    "targetStickSeconds": 1.5,
    "targetStickBonus": 0.15,
    "overkillShare": 1.15
  },

  "naval": {
    "allowBossReverse": false,
    "headingDeadbandDeg": 5,
    "broadsideEnterDeg": 8,
    "broadsideLeaveDeg": 15,
    "turnRadiusSafety": 1.10
  },

  "procurement": {
    "intelEma": 0.20,
    "mismatchConfirmSeconds": 4,
    "maxPlanCards": 5
  }
}
```

Tên key cuối cùng map theo convention repo hiện tại.

---

# 108. Những giá trị hiện tại nên thay/retire

Anti-stuck kiểu:

```text
đứng lâu → tự đi về enemy gần nhất
```

không nên là primary solution nữa.

Giữ chỉ như fallback cuối sau:

```text
soft avoid
local replan
yield
corridor replan
```

Nếu `StaleIdle = 12 s` còn tồn tại:
- giữ làm severe fail-safe;
- không phải lần phản ứng đầu tiên.

---

# 109. AI mua quân — test bắt buộc

## Test A — naval boss inaccessible ground

Map:
- enemy boss ở biển;
- shoreline > max range MBT;
- không objective đất.

Expected:

```text
main_battle_tank REJECT no-map-influence
heavy_tank REJECT
naval/air/coastal-capable units eligible
```

---

## Test B — coastal gun can reach ship

Ground gun:
- reachable firing hill;
- range đủ tới naval lane.

Expected:

```text
eligible
```

---

## Test C — secondary land objective

Boss ở biển nhưng map có capture point đất.

Expected:
- ground unit có thể mua nếu phục vụ land objective;
- không hard ban ground vì boss naval.

---

# 110. Naval boss tests

## Heading

Target chuyển từ trái sang phải boss.

Expected:
- turret đổi mục tiêu;
- hull không flip 180°.

## Target behind

Expected:
- ship không reverse;
- tiếp tục lane;
- turret/mount phù hợp xử lý hoặc đổi target.

## Turn radius

Planner không tạo waypoint khiến curvature nhỏ hơn `Rmin`.

## Collision

Hai ship hội tụ:
- giảm tốc/turn trước nhiều giây;
- không overlap rồi giật.

---

# 111. Congestion tests

## 20 vehicles same objective

Expected:
- squad split;
- shared corridor;
- choke batching;
- không 20 A* path độc lập dồn đúng một cell.

## Two squads opposite gate

Expected:
- one direction granted;
- loser waits/yields;
- không cả hai inch forward/back forever.

## Heavy + scout

Expected:
- scout yields;
- heavy giữ đường.

## Wreck in choke

Expected:
- nav dirty ngay;
- squad replan;
- không đứng 10 s mới nhận ra.

---

# 112. Squad tests

## Reinforcement

New unit:
- tới rendezvous;
- join;
- không chase moving centroid vô hạn.

## Understrength squad

<45% desired:
- merge compatible squad.

## Oversized squad

>9:
- split.

## Narrow route

formation auto Travel/column.

---

# 113. Targeting tests

- unreachable target filtered.
- target behind wall filtered nếu không indirect.
- target outside mount bearing filtered.
- minimum range respected.
- overkill spreads fire.
- current-target stickiness giảm churning.
- boss part focus override vẫn hoạt động.

---

# 114. Performance tests

Các test tối thiểu:

```text
32 ground vs 32 ground
48 vs 48 Siege
boss + escorts + 32 units
multiple wrecks in choke
4 simultaneous squads
```

Metrics:

```text
AI total ms/frame
steering ms
path rebuild ms
procurement ms
jam count
severe unjam count
average blocked seconds
orders/unit/min
target switches/min
squad action switches/min
```

---

# 115. Quality gates

Không merge nếu:

```text
SevereUnstuck > 1 per 10 unit-minutes
```

trong normal open map.

Không merge nếu:

```text
naval reverse event > 0
```

cho naval boss.

Không merge nếu AI mua:

```text
unit with MapInfluence == 0
```

trừ explicit scripted mission unit.

Không merge nếu:

```text
squad action switches > current churn warning
```

mà không có objective/phase event.

---

# 116. Regression — giữ các behavior tốt hiện có

Phải giữ:

- threat grid/intel;
- fog-respecting AI;
- tactic switching;
- squad state commitment;
- mode profiles;
- tower modes;
- artillery standoff;
- firing spot booking;
- aircraft resupply;
- boss phase data;
- escort roles;
- target masks;
- anti-snipe/mode rules.

Không rewrite làm mất các behavior này.

---

# 117. Migration plan

## Phase 1 — high impact, low risk

Implement:

1. EngagementFeasibility.
2. hard filter mua quân.
3. target hard feasibility.
4. naval reverse=false.
5. hull/turret separation.
6. jam stages.
7. DecisionLog reasons.

Đây là phase nên làm đầu tiên.

---

## Phase 2 — traffic

1. shared squad corridor;
2. TrafficCoordinator;
3. choke reservations;
4. deterministic passing;
5. wreck nav dirty;
6. spawn clear zones.

---

## Phase 3 — squad lifecycle

1. forming/rallying;
2. merge/split;
3. rendezvous;
4. reserve;
5. role placement.

---

## Phase 4 — advanced naval

1. turn radius;
2. lane spline;
3. broadside scoring;
4. CPA collision prediction;
5. heading hysteresis.

---

## Phase 5 — optimization

1. flow-field tiles if necessary;
2. cache reachability;
3. profiler;
4. stagger updates.

---

# 118. Source/research rationale

Các nguyên tắc trong tài liệu lấy cảm hứng từ nhiều hướng đã chứng minh hiệu quả trong RTS/multi-agent navigation:

## OpenRA / modular RTS AI
Điểm dùng:
- production theo cơ cấu thay vì first available;
- squad gathering;
- reserve/defense;
- local tactical logic;
- native real-time modules tách khỏi high-level intent.

## StarCraft AI research
Điểm dùng:
- modular architecture;
- macro actions;
- rally trước attack;
- attack timing;
- route selection;
- influence maps;
- hierarchical decision layers.

## Supreme Commander / Game AI Pro flow fields
Điểm dùng:
- shared path/flow-field cho nhiều unit;
- tránh mỗi unit tính một đường độc lập;
- steering/local avoidance tách khỏi global path.

## ORCA / reciprocal collision avoidance
Điểm dùng:
- velocity-based collision prediction;
- hai agent chia trách nhiệm tránh;
- smooth multi-agent avoidance.

Không cần copy implementation nguyên xi.
Mục tiêu là áp các pattern phù hợp với kiến trúc Machine Brigade hiện tại.

---

# 119. Những điều KHÔNG nên làm

Không:

1. cho AI cheat fog để “thông minh hơn”;
2. teleport unit như normal anti-stuck;
3. random passing side mỗi frame;
4. để ship reverse;
5. để boss hull aim target nếu turret đủ arc;
6. mua unit rồi mới phát hiện map không dùng được;
7. cho mọi unit pathfind tới enemy individually;
8. formation cứng trong choke;
9. dùng HP threshold làm retreat system;
10. tăng raw enemy stats để che AI xấu;
11. update strategic decision ở 10 Hz;
12. cho AI đổi target/action không hysteresis;
13. cho support vehicle đứng frontline vì nó gần objective hơn.

---

# 120. Recheck checklist trước khi merge

## Architecture
- [ ] Commander không micro steer.
- [ ] Squad không direct fire weapon.
- [ ] Tactical không đổi strategic objective.
- [ ] steering không chọn target.

## Purchase
- [ ] no-map-influence rejected.
- [ ] naval map test pass.
- [ ] secondary objective test pass.
- [ ] role deficit applied.
- [ ] observed intel only.

## Navigation
- [ ] shared route.
- [ ] choke reservation.
- [ ] deterministic passing.
- [ ] wreck invalidation.
- [ ] spawn exit clear.

## Jam
- [ ] 1.5 s soft reaction.
- [ ] 3 s local replan.
- [ ] 5 s yield.
- [ ] 8 s corridor.
- [ ] 12 s emergency.
- [ ] no teleport normal path.

## Naval
- [ ] reverse impossible.
- [ ] minimum turn radius.
- [ ] hull/turret separation.
- [ ] broadside hysteresis.
- [ ] CPA avoidance.
- [ ] lane follow.

## Squads
- [ ] 3–9 normal squad size.
- [ ] merge.
- [ ] split.
- [ ] reinforcement rendezvous.
- [ ] reserve.
- [ ] formation roles.

## Target
- [ ] firing solution filter.
- [ ] arc.
- [ ] min range.
- [ ] overkill.
- [ ] target stick.
- [ ] unreachable target drop.

## Performance
- [ ] 48v48 acceptable.
- [ ] boss + escort acceptable.
- [ ] spatial queries bounded.
- [ ] caches invalidate correctly.

## Logs
- [ ] purchase reject reason.
- [ ] movement jam reason.
- [ ] target reject reason.
- [ ] squad choice reason.
- [ ] boss hull reason.

---

# 121. Final implementation report format

Code AI phải trả cuối task:

1. files changed;
2. new classes/services;
3. old behavior → new behavior;
4. all new tunables;
5. purchase feasibility tests;
6. naval boss tests;
7. congestion tests;
8. squad tests;
9. target tests;
10. performance measurements;
11. severe-unstuck count;
12. AI decision-log examples;
13. remaining known issues;
14. generated docs/data regenerated.

Nếu canonical AI data/docs thay đổi, regenerate:
- `09_ai.xlsx`
- `09_ai.md`
- `04_che_do_kinh_te_ai.xlsx/.md` nếu AI mode/economy docs mirror dữ liệu
- `02_boss.xlsx/.md` nếu boss behavior fields/docs thay đổi
- `06_ban_do.xlsx/.md` nếu thêm topology/lane metadata
- `00_index.xlsx`
- `README.md`
- `CHANGES.md`
- AI-readable exports / JSON / CSV / schemas nếu có

Không patch generated file thủ công nếu generator tồn tại.

---

# 122. Final decision

Kiến trúc cuối nên là:

```text
WORLD / MAP TOPOLOGY
        ↓
INTEL + THREAT MODEL
        ↓
STRATEGIC INTENT
        ↓
FORCE / PROCUREMENT PLAN
        ↓
SQUAD ASSIGNMENT
        ↓
SHARED ROUTE + TRAFFIC
        ↓
TACTICAL TARGET / POSITION
        ↓
LOCAL STEERING
```

Boss:

```text
BOSS MISSION
   ↓
HULL MOVEMENT ──────── separate ──────── WEAPON TARGETS
   ↓                                         ↓
NAVAL / GROUND KINEMATICS                TURRET AIM
   ↓                                         ↓
TRAFFIC / COLLISION                     FIRE CONTROL
```

Điểm thay đổi quan trọng nhất:

> **Không để “target” trực tiếp lái cả thân boss.**

> **Không để “unit score” thắng nếu unit không thể tác động tới map.**

> **Không đợi 10–12 giây mới bắt đầu xử lý congestion.**

> **Không cho từng xe tự giải quyết một vấn đề đội hình mà squad/traffic layer phải giải quyết.**

Đây là nền đủ mạnh để cải thiện các bug hiện tại mà vẫn giữ hệ AI theo tactic/profile đã xây sẵn.


---

# 123. ADVANCED BEHAVIOR PACK — mở rộng từ RTS / tactical AI khác

Phần này bổ sung behavior nâng cao lên toàn bộ spec trước. Mọi rule an toàn/feasibility/navigation ở phần trước vẫn ưu tiên cao hơn.

Nguyên tắc bắt buộc:
- không cheat fog;
- không morale;
- không retreat-by-health;
- không random quyết định chiến thuật chỉ để “trông khác”;
- behavior phải deterministic và explainable;
- AI khó hơn bằng planning/coordination tốt hơn, không bằng omniscience.

Nguồn cảm hứng chính:
- OpenRA: squad manager, production share/limit, opportunity fire, persistent targeting, range margin, stance.
- Total War battle AI: phối hợp mũi flank với main force và bố trí vai trò trong đội hình.
- Killzone 3 hierarchical AI: strategic graph, influence map có temporal smoothing, regroup marker, route diversification.
- Days Gone squad coordination: squad là AI entity riêng, role assignment và “confidence” cấp nhóm.
- Gears Tactics: planned world state, cooperative goals, combo action, interrupt/replan.
- StarCraft/BWAPI bot ecosystem: blackboard/FSM, combat forecast, kiting, fog-respecting state, macro/micro separation.
- Influence-map / cluster research: local tactical clustering và hierarchical coordination.

Không copy nguyên implementation của game khác; chỉ dùng pattern phù hợp với Machine Brigade.

# 124. Tactical Frontline Model

Tạo một lớp `FrontlineModel` thay vì chỉ nhìn từng enemy contact.

```csharp
sealed class FrontlineModel
{
    public IReadOnlyList<FrontSegment> Segments;
}

readonly record struct FrontSegment(
    Vector2 Centre,
    Vector2 Normal,
    float FriendlyPressure,
    float EnemyPressure,
    float Stability,
    float Width,
    float Confidence);
```

Frontline suy ra từ:
- friendly combat influence;
- enemy visible/remembered influence;
- objective;
- recent combat;
- chokepoint/terrain.

Không dùng hidden enemy positions.

Lợi ích:
- biết đâu là front, flank, rear;
- artillery/repair/AA/EW biết đứng sau tuyến;
- reserve biết chỗ nào đang sắp vỡ;
- flank route không chỉ là “đường dài hơn”.

# 125. Tactical Confidence — không phải morale

Đây là giá trị cơ học cấp squad, không liên quan tinh thần.

```text
TacticalConfidence =
    0.35 * LocalForceRatio
  + 0.20 * RoleCoverage
  + 0.15 * SupportCoverage
  + 0.10 * PositionalAdvantage
  + 0.10 * ObjectiveUrgency
  + 0.10 * IntelConfidence
```

Clamp `0..1`.

Dùng để:
- có nên commit một squad mới;
- có nên flank;
- có nên hold/regroup;
- có release reserve;
- giữ standoff/aggressive posture.

Không dùng:
```text
hp < x => retreat
```

Gợi ý:
- `>=0.70`: aggressive opportunity
- `0.45–0.70`: normal
- `0.30–0.45`: cautious/hold/regroup
- `<0.30`: không commit thêm nếu chưa có emergency objective

# 126. Dynamic Frontage

Mỗi đoạn front có usable width.

```text
RequiredFrontage =
sum(unitWidth + desiredSeparation)
```

Nếu vượt usable width:
1. mở route khác;
2. giữ reserve;
3. stagger wave;
4. gọi artillery/air;
5. không tiếp tục nhét quân qua cùng choke.

Đây là rule rất quan trọng để ngăn “AI có 30 xe nhưng chỉ 5 xe thật sự chiến đấu”.

# 127. Route Diversity

Strategic path cost thêm:

```text
PathCost =
    Distance
  + Threat
  + Congestion * 0.8
  + FriendlyRouteOccupancy * 0.5
  + RecentLosses * 0.7
  + UnknownRisk
```

Mục tiêu:
- 2 squad có thể chọn 2 corridor khác nhau;
- route vừa thất bại không được dùng lại ngay vô thức;
- vẫn chọn cùng route nếu rõ ràng tốt nhất.

# 128. Temporal Influence Memory

Threat không biến mất ngay khi enemy ra khỏi vision.

Suggested half-life:
- mobile unit: `8–12 s`
- artillery suspected: `15–25 s`
- tower/static: `30–60 s` hoặc tới khi recon xác nhận vắng

`ConfirmedAbsent` vẫn giảm memory nhanh.

# 129. Recent-Death Danger Memory

Mỗi friendly death tạo danger signal cục bộ:

```text
DeathInfluence =
    StrategicValue
  * exp(-age / halfLife)
```

Dùng để:
- tăng scout demand;
- tăng artillery/SEAD;
- tránh lặp lại đúng kill zone.

Không dùng để tạo morale/panic.

# 130. Unknown != Safe

Map cell `Unknown` có uncertainty cost.

Tactic modifier:
- blitz: thấp;
- balanced: trung bình;
- attrition: cao;
- recon/ambush: cao.

Điều này làm scout thật sự có giá trị.

# 131. Scout Before Commit

Nếu main force sắp vào vùng unknown cao:
- giao recon task trong `2–6 s`;
- dùng recon drone/scout jeep/heli/radar;
- main force stage ngoài danger band.

Timeout hết mà objective urgent:
- vẫn commit với uncertainty hiện có.

Không chờ vô hạn.

# 132. Probe-and-Exploit

Gửi lực lượng nhỏ `8–15%` power kiểm tra lane.

Nếu resistance thấp:
- tạo `ExploitWindow`;
- main force đổi trọng tâm.

Nếu AT/ambush cao:
- tạo threat event;
- dùng artillery/flank/SEAD.

Nếu route blocked:
- không gửi army chính vào đó.

Probe không phải suicide; phải có route về hoặc standoff role.

# 133. Feint

Chỉ Hard/VeryHard hoặc commander/tactic phù hợp.

Feint phải có tactical utility riêng:
- contest secondary point;
- force spotting;
- threaten flank;
- pin turret arc.

AI chỉ coi feint thành công khi **quan sát được** enemy redeploy.

Không đọc hidden reaction.

# 134. Fix-and-Flank

Hai squad:
- `Fix`: giữ enemy occupied ở front;
- `Flank`: đi route khác đánh side/rear/support.

Điều kiện:
- enemy cluster stable;
- có ít nhất 2 access routes;
- friendly power đủ.

Fix squad không được suicide; nó chỉ giữ pressure trong engagement envelope.

# 135. Synchronized Attack ETA

Tính:
- ETA main;
- ETA flank;
- ETA artillery prep;
- ETA air cover;
- ETA reserve.

Main force đến sớm thì **stage/overwatch**, không lao vào trước.

Suggested tolerance:
- ground main/flank: `±3 s`
- air/ground: `±4 s`
- artillery impact: `1–3 s` trước ground contact

# 136. AttackPackage

```csharp
sealed class AttackPackage
{
    SquadId Main;
    SquadId? Fix;
    SquadId? Flank;
    SquadId? Reserve;
    FireMissionId? ArtilleryPrep;
    AirMissionId? AirCover;
    ObjectiveId Target;
    float ExecuteAt;
}
```

Commander lập package, squad thực thi.

# 137. Staging Areas

Attack package chọn staging area:
- reachable;
- đủ rộng;
- ngoài direct-fire threat nếu biết;
- không choke;
- không block spawn;
- gần route split.

Mỗi squad nhận sub-zone riêng, không cùng exact coordinate.

# 138. Planned Action Reservation Board

Tạo bảng “đồng đội đang định làm gì”.

```csharp
sealed class PlannedActionBoard
{
    // target -> planned damage
    // area -> planned smoke/artillery
    // target -> repair reserved
    // objective -> committed power
    // choke -> movement reservation
}
```

Đây là layer rất quan trọng để AI phối hợp thay vì chỉ phản ứng trạng thái hiện tại.

# 139. Planned Damage / Anti-Overkill

Trước khi bắn:
- reserve expected damage.

Nếu:

```text
plannedIncomingDamage >
targetEffectiveHp * 1.15
```

unit chưa fire chọn target khác nếu không có forced focus.

Release reservation khi:
- shot cancelled;
- target invalid;
- timeout.

# 140. Repair Reservation

Không để 4–5 engineer chạy vào cùng một tank.

```text
RepairNeed
RepairReserved
```

Chỉ assign thêm repair khi còn deficit.

# 141. AA Coverage Reservation

AA có coverage assignment:
- BossCover
- MainForceCover
- ArtilleryCover
- ObjectiveCover

Không mọi AA chase cùng một aircraft.

# 142. Smoke Deconfliction

Smoke mission có:
- area;
- start;
- end;
- purpose.

Purpose:
- crossing;
- break laser LOS;
- cover repair;
- assault objective.

Không bắn 4 smoke cùng một spot.

# 143. Fire Mission Scheduler

Artillery missions:
- Prep
- Suppress
- CounterBattery
- AreaDenial
- Finish

Scheduler tránh:
- toàn bộ artillery bắn 1 weak target;
- barrage liên tục vào vị trí remembered đã stale.

# 144. Counter-Battery

Enemy artillery shot tạo estimated origin:
- confidence;
- error radius;
- timestamp.

Nhiều shot cùng vùng => confidence tăng.

Không magic reveal.

Nếu unseen:
- chỉ area-fire nếu weapon cho phép;
- spread theo error radius.

# 145. Shoot-and-Scoot

Artillery/MLRS/missile truck:
- sau `2–4 salvo`;
- hoặc khi bị counterbattery threat;
- reposition `12–30 m`.

Không scoot vào:
- choke;
- frontline;
- firing reservation khác.

# 146. Predictive Interception

Fast unit/AA/fighter không chase current position.

Tính intercept:

```text
|targetPos + targetVel*t - selfPos| = selfSpeed*t
```

Clamp horizon.

Target hidden:
- extrapolation uncertainty tăng theo thời gian.

# 147. Cutoff Instead of Chase

Nếu có route confidence:
- fast squad đi tới choke/exit dự đoán thay vì chạy sau target.

Chỉ dùng khi cutoff ETA tốt hơn direct pursuit.

# 148. Pursuit Discipline

Squad task có:
- max pursuit distance;
- max pursuit seconds;
- objective leash.

Nếu target không còn mission-relevant:
- drop pursuit;
- trở lại task.

AA đặc biệt không chase aircraft qua nửa map.

# 149. Internal Unit Stances

Dùng 4 stance kiểu:
- HoldFire
- ReturnFire
- Defend
- AttackAnything

Mapping:
- ambush/recon => HoldFire/ReturnFire
- fragile support => Defend
- assault => AttackAnything

# 150. Opportunity Fire

Đang move:
- turret có thể bắn target trong arc/range;
- hull route không đổi;
- chỉ break formation nếu threat vượt threshold.

Đặc biệt boss ship:
- turret opportunity fire;
- hull không steer theo opportunity target.

# 151. Range Margin

Không cố đứng đúng max/min range gây oscillation.

```text
preferredMax = maxRange - margin
preferredMin = minRange + margin
```

Gợi ý:
- direct gun: 3–6%
- artillery: 5–10%
- ATGM: ~5%
- AA missile: 5–8%

# 152. Short-Horizon Combat Forecast

Tạo simulator nhẹ 4–8 s.

Input:
- DPS by target class;
- armour/penetration;
- range uptime;
- AoE density;
- support;
- local threat.

Output:
- expected friendly loss;
- expected enemy loss;
- power after horizon;
- breakthrough chance.

Không simulate full projectile physics.

# 153. Forecast Usage

Dùng để:
- frontal vs flank;
- wait artillery vs attack now;
- release reserve;
- support need.

Không dùng làm health-retreat rule.

# 154. Counterfactual Shallow Planning

Commander đánh giá 2–4 plan:

```text
A: attack now
B: wait artillery
C: flank
D: split/hold
```

```text
PlanUtility =
    ObjectiveGain
  + EnemyLossValue
  - FriendlyLossValue
  - DelayCost
  - CongestionCost
  - UncertaintyRisk
```

Depth 1–2, không deep search.

# 155. Abort Attack Package

Abort trước contact nếu:
- route invalidated;
- primary squad mất trước khi tới;
- flank blocked;
- objective thay đổi;
- enemy estimate tăng mạnh;
- support mission fail.

Không abort chỉ vì một unit mất HP.

# 156. Opportunity / Exploit Windows

WorldModel tạo opportunity:
- enemy AA destroyed;
- boss APS/shield/radar part destroyed;
- artillery exposed;
- defenders redeploy;
- gate opens;
- enemy main force ở xa.

Opportunity có:
- location;
- confidence;
- expiry;
- required roles.

# 157. Same-Match Adaptation

Không machine learning persistent.

Track EMA trong trận:
- route success;
- unit class utilization;
- target-type kill efficiency;
- support effectiveness.

Reset mỗi match.

# 158. Anti-Repetition

Plan vừa fail nhận penalty `25–50%`, decay `30–60 s`.

Không random vô lý; chỉ giảm score của phương án vừa chứng minh tệ.

# 159. Formation Morphing

Formation chuyển dần:
- Spread -> Travel: outer unit converge;
- Travel -> Hold: front line peel ra;
- Hold -> Flank: fast unit dịch outer side.

Không snap exact slot.

# 160. Stable Slot Assignment

Giữ slot cũ nếu còn hợp lệ.
Slot mới assign nearest compatible role.

Mục tiêu:
- giảm xe cắt ngang nhau;
- giảm wobble.

# 161. Travel Column Ordering

Trong cột:
- giữ thứ tự longitudinal ổn định;
- heavy không swap qua lại với scout;
- chỉ reorder khi split/regroup/member mất.

# 162. Splash-Aware Spacing

Nếu enemy splash threat cao:
- tăng separation;
- giảm packet size.

Nếu enemy direct AT high:
- không spread vô ích; ưu tiên cover/flank.

# 163. Area-Denial Memory

Mine/fire/thermobaric danger tạo temporary cost.

Mine risk đến từ:
- observed explosion;
- spotted mine layer;
- detected mine.

AI không tự “biết” mine chưa thấy.

# 164. Mine-Clearing Task

Critical route bị mine risk cao:
- engineer/breacher đi trước;
- main force giữ ngoài trigger band;
- alternate route được evaluate song song.

# 165. Screen Behavior

Recon/light units tạo screen trước main force:
- spot;
- kiểm tra ambush;
- detect threat;
- không trade trực diện với heavy enemy.

Khi heavy threat lộ:
- screen chuyển về support band.
Không liên quan HP threshold.

# 166. Escort Sectors

Escort quanh boss/convoy chia sector:
- FrontScreen
- LeftScreen
- RightScreen
- RearGuard
- AAUmbrella
- RepairTrail

Không cả escort pack chạy vào cùng target.

# 167. Threat Handoff

Threat đi từ left sang right:
- escort left handoff cho right nếu right ETA tốt hơn;
- left quay lại sector.

# 168. Support Chain

Repair/EW/AA/ammo không stack cùng centroid.

Position theo coverage:
- repair phía sau;
- ammo farther rear;
- AA offset;
- EW tối ưu bubble.

# 169. Coverage Optimizer

Sample candidate spots:

```text
CoverageScore =
    FriendlyValueCovered
  - Exposure
  - Congestion
  - RedundantCoverage
```

Dùng cho:
- AA;
- EW;
- repair aura;
- radar.

# 170. Reserve Logic

Reserve default 15–25% combat power.

Release ưu tiên:
1. HQ/boss critical threat
2. breakthrough
3. primary objective collapse
4. high-value exploit
5. secondary objective

Không release reserve vào fight đã thắng rõ.

# 171. Economy of Force

Secondary objective chỉ nhận đủ lực lượng để:
- delay;
- screen;
- contest.

Không chia 50/50 nếu primary decisive.

# 172. Objective Sunk-Cost Reset

Nếu:

```text
ExpectedRecoveryCost >
ObjectiveFutureValue
```

Commander ngừng gửi reinforcement mới.

Đơn vị đang ở đó nhận task mới theo strategic state; không phải health retreat.

# 173. Threat-Specific Posture

Enemy artillery:
- spread/move/counterbattery.

Enemy AT:
- avoid frontal heavy exposure;
- use artillery/light flank.

Enemy air:
- remain in AA umbrella.

Enemy splash:
- packet split.

Enemy stealth:
- recon density tăng.

# 174. SEAD Package

Air strike có thể yêu cầu:

```text
EW/SEAD
→ SAM suppression
→ strike ingress
→ egress
```

Nếu suppression fail:
- delay hoặc reroute strike.

# 175. Aircraft Risk Routing

Build `AirRiskMap`.

Aircraft route:
- ingress low risk;
- attack;
- egress route nếu có.

Không repeated pass qua strongest SAM bubble nếu không cần.

# 176. CAP Patrol Zones

Fighter assign patrol zone:
- boss;
- main force;
- objective;
- expected approach corridor.

Không chase mọi aircraft tới map edge.

# 177. Air Target Handoff

Estimate TTK.
Không 6 fighter cùng chase 1 weak target.
Assign 1–2 attackers tùy target.

# 178. Bomber Package

Bomber chờ:
- valuable target;
- acceptable route;
- blast deconfliction;
- SEAD window nếu cần.

Không gửi expensive bomber vào trivial target nếu không urgent.

# 179. Boss Weakpoint Utility

Boss part score theo:
- disabled DPS;
- disabled APS/shield/radar;
- phase utility;
- kill progress.

AI được biết function của part vì đó là game rule, không hidden intel.

# 180. Boss Telegraph Reaction

AI phản ứng với warning mà player cũng thấy:
- big attack;
- salvo;
- bomb stick;
- burrow;
- superweapon.

Difficulty chỉ thay reaction delay/quality.

# 181. Escape Sector Reservation

Khi telegraph AoE:
- generate 3–5 safe sectors;
- distribute squad;
- không cả squad chạy cùng một điểm.

# 182. Tactical Interrupt/Replan

Plan re-evaluate khi:
- target chết;
- route blocked;
- new lethal warning;
- support lost;
- objective version changed.

Không replan vì thay đổi nhỏ.

# 183. Plan Validity Dependencies

AttackPackage lưu:
- route version;
- objective version;
- target-cluster version;
- support availability.

Chỉ invalidate khi dependency quan trọng đổi.

# 184. Commitment Windows

Suggested:
- turret target: 1–1.5 s
- firing spot: 2–3 s
- squad route: 4–6 s
- attack package: 6–12 s
- tactic: existing large cooldown

Emergency safety có thể break.

# 185. Unit State Anomaly Detection

Mỗi issued command có expected state.

Ví dụ:
- Move order => phải acceleration trong 0.5 s.
- Attack order => aim/reposition progress phải có.
- Join => distance to rendezvous giảm.

Nếu không:
- log anomaly;
- local recovery;
- không spam cùng command mỗi tick.

# 186. Command Deduplication

Nếu desired order equivalent current:
- không issue lại.

Giảm:
- path reset;
- animation jitter;
- CPU;
- churning.

# 187. Intent Ownership

Order tagged:
- ScriptCritical
- Emergency
- BossPhaseSafety
- Tactical
- Squad
- Commander
- Idle

Arbiter ưu tiên safety nhưng không cho lower layer thay strategic intent vô lý.

# 188. Predictive Congestion

Không chỉ đo density hiện tại.

Tính lượng unit **sắp tới choke trong 5 s**.

Nếu overloaded:
- delay package;
- split packet;
- choose alternate route.

# 189. Choke Throughput

Approx:

```text
throughput =
usableWidth / avgUnitWidth
* avgSpeed
```

ETA route phải tính queue delay.

# 190. Deadlock Wait-For Graph

Nếu:
- A waits B
- B waits C
- C waits A

=> cycle.

Lowest priority yields/local replan.

Naval:
- low-priority ship slows/turns aside;
- boss không reverse.

# 191. Threat-Aware Spawn Choice

Nhiều spawn/entry:
```text
SpawnScore =
    ObjectiveETA
  - Threat
  - Congestion
  + SupportProximity
```

# 192. Reinforcement Batching

Units spawn trong 3–6 s:
- có thể rally thành packet;
- tránh feed one-by-one.

# 193. Attrition Efficiency

Track:

```text
TradeRatio =
EnemyCPValueLost / FriendlyCPValueLost
```

EMA.

Dùng để đổi:
- lane;
- support;
- composition;
- tactic.

Không dùng health retreat.

# 194. Weapon Utilization Metric

Per unit class/squad:

```text
Utilization =
effectiveFiringTime / combatTime
```

Nếu artillery utilization thấp:
- reposition.

Nếu MBT utilization thấp trên naval map:
- same-match procurement giảm score mua thêm.

# 195. Range-Band Occupancy

Track:
- under min range;
- effective band;
- beyond max.

Giúp phát hiện:
- bad pathing;
- bad purchase;
- bad target selection.

# 196. Same-Match Procurement Feedback

Nếu unit class:
- CombatTime >= 20 s
- Utilization < 0.15

=> reduce purchase score current match, min modifier ~0.55.

Log:
`low-realized-utilization`.

# 197. Counter Saturation

Không over-buy AA/AT sau khi deficit đã giải quyết.

RoleDeficit phải tính **existing useful coverage**, không chỉ enemy threat.

# 198. Soft Composition Floors

Nếu threat class có thể xuất hiện:
- giữ small floor recon;
- AA;
- AT.

Không hard nếu deck/map không hỗ trợ.

# 199. Focus-Fire Coordinator

Chỉ focus mạnh khi:
- high threat;
- boss part;
- near kill;
- strategic unit.

Otherwise spread fire để giảm overkill.

# 200. Target Handoff by Suitability

Ví dụ:
- autocannon đang bắn Armour5;
- AT gun vừa có solution.

=> AT nhận Armour5, autocannon chuyển light/drone.

Handoff có short lock window để tránh churn.

# 201. Multi-Weapon Platform Director

Không force mọi mount cùng target.

Ví dụ:
- main gun -> heavy ground
- MG -> light/air opportunity
- AA mount -> air
- CIWS -> missile
- rocket -> cluster/structure

Hull chỉ xét mount cần hull bearing.

Đặc biệt quan trọng cho boss.

# 202. Boss Active-DPS Bearing

Measure:

```text
ActiveDpsFraction =
DPS currently bearing / total relevant DPS
```

Movement/broadside controller cố giữ mức tốt khi route cho phép, ví dụ target `>=0.65`, nhưng không hard-lock.

# 203. Boss Fire Cadence Director

Không phải mọi heavy weapon fire cùng frame.

WeaponDirector stagger:
- main gun;
- rockets;
- missiles;
- secondary.

Ngoại lệ:
- data explicit salvo/superattack => giữ synchronized.

Mục tiêu:
- pressure đều;
- dễ đọc;
- giảm self-overkill.

# 204. Pressure Budget

Boss/AI có thể theo dõi số dangerous actions đang active.

Nếu đã có:
- bomb warning;
- missile volley;
- artillery strike;

thì non-critical ability khác có thể delay rất ngắn.

Đây là pacing/readability, không nerf damage.

# 205. Ambush Discipline

Ambush:
- HoldFire;
- spread positions;
- synchronized opening volley.

Trigger:
- enemy vào 55–70% effective range;
- ambush bị phát hiện;
- high-value target đi qua.

Opening volley dùng anti-overkill reservation.

# 206. Bait Resistance without Cheating

AI không biết trap hidden.

Nhưng nếu:
- repeated cheap target xuất hiện cùng route;
- AI chase rồi chịu losses;

thì:
- recent-loss memory tăng;
- pursuit leash giảm;
- scout task tăng.

Emergent anti-bait.

# 207. Deadline-Aware Objective Assignment

Nếu capture còn `X s`, squad ETA > X:
- không gửi slow squad vô ích;
- dùng fast unit/fire support/next objective.

# 208. Time-to-Value Procurement

```text
TimeToValue =
delivery/build
+ rally
+ travel
+ time to firing region
```

Late game:
- fast useful unit có thể score hơn slow efficient unit.

# 209. Capability Replacement

Unit chết:
- tăng deficit **role/capability**;
- không blindly mua đúng same ID.

# 210. Objective Ownership Prediction

Estimate future capture bằng:
- capture rates;
- current units;
- reinforcement ETA.

Có thể rotate một phần squad sớm khi objective gần secure.

# 211. Defense in Depth

Defense profile precomputes 2–3 hold lines.

Khi forward objective mất:
- assign Hold task tới next line.

Không retreat-by-health; trigger là strategic objective state.

# 212. Counterattack Window

Nếu enemy assault vừa mất nhiều local power:
- WorldModel tạo short `CounterattackOpportunity`;
- reserve/main có thể push trước khi enemy regroup.

# 213. Anti-Artillery Dispersion Timing

Khi warning:
- spread ngay.

Sau impact:
- không regroup quá sớm nếu threat window vẫn active.

# 214. Within-Encounter Pattern Learning

Nếu boss attack pattern repeated và được telegraph:
- AI có thể cải thiện escape sector choice sau lần đầu.

Không đọc hidden random future.

# 215. Tactical Communication Cues

Khi synchronized attack:
- optional radio cue;
- leader gesture;
- boss escort animation.

Không gameplay bonus.
Làm AI thông minh dễ nhìn thấy đối với player.

# 216. Advanced Difficulty Gating

Easy:
- no feint;
- 1 forecast plan;
- đơn giản route diversity.

Normal:
- synchronized attacks;
- fix/flank rõ;
- counterbattery basic;
- 2 forecast plans.

Hard:
- probe;
- conditional feint;
- same-match adaptation;
- SEAD package;
- 3 plans.

VeryHard:
- full pack;
- vẫn fog-respecting;
- không instant reaction;
- không hidden info.

# 217. Deterministic Human-Like Stagger

Để tránh robot-sync:
- 150–400 ms deterministic stagger giữa actions tương đương.

```text
delay = hash(unitId,eventId) % allowedWindow
```

Không nondeterministic random.

# 218. Advanced Tunables

```json
{
  "advanced": {
    "frontlineUpdateS": 1.0,
    "mobileInfluenceHalfLifeS": 10.0,
    "staticInfluenceHalfLifeS": 45.0,
    "deathMemoryHalfLifeS": 18.0,

    "scoutBeforeCommitMaxWaitS": 5.0,
    "probePowerShare": 0.12,

    "syncGroundToleranceS": 3.0,
    "syncAirToleranceS": 4.0,
    "artilleryPrepLeadS": 2.0,

    "repeatPlanPenalty": 0.35,
    "repeatPlanPenaltyHalfLifeS": 45.0,

    "combatForecastSeconds": 6.0,
    "combatForecastCacheS": 0.75,

    "plannedOverkillShare": 1.15,

    "artilleryScootMinSalvos": 2,
    "artilleryScootMaxSalvos": 4,
    "artilleryScootMinM": 12.0,
    "artilleryScootMaxM": 30.0,

    "reserveDefaultShare": 0.20,

    "sameMatchLowUtilizationThreshold": 0.15,
    "sameMatchLowUtilizationSeconds": 20.0
  }
}
```

Tên key cuối map theo convention repo.

# 219. Code skeleton — TacticalConfidence

```csharp
float TacticalConfidence(Squad squad, TacticalContext ctx)
{
    float localRatio = NormalizeForceRatio(
        ctx.Power.FriendlyAround(squad),
        ctx.Power.EnemyAround(squad));

    float roleCoverage =
        ctx.Roles.Coverage(squad);

    float support =
        ctx.Support.Coverage(squad);

    float position =
        ctx.Frontline.PositionalAdvantage(squad);

    float urgency =
        ctx.Objective.Urgency01(squad.Task);

    float intel =
        ctx.World.IntelConfidence01(squad.Task.Region);

    return Math.Clamp(
        0.35f * localRatio +
        0.20f * roleCoverage +
        0.15f * support +
        0.10f * position +
        0.10f * urgency +
        0.10f * intel,
        0f, 1f);
}
```

# 220. Code skeleton — synchronized attack

```csharp
AttackPackage BuildAttackPackage(
    StrategicIntent intent,
    IReadOnlyList<Squad> squads,
    AiContext ctx)
{
    var main =
        SelectMainEffort(squads, intent, ctx);

    var flank =
        SelectBestFlank(main, squads, intent, ctx);

    var reserve =
        SelectReserve(squads, main, flank, ctx);

    float mainEta =
        ctx.Paths.EstimateEta(main, intent.Target);

    float flankEta =
        flank == null
            ? 0f
            : ctx.Paths.EstimateEta(
                flank, intent.Target);

    float supportEta =
        ctx.FireSupport.EstimatePrepEta(
            intent.Target);

    float executeAt =
        ctx.Time.Now +
        MathF.Max(
            mainEta,
            MathF.Max(flankEta, supportEta));

    return new AttackPackage(
        Main: main.Id,
        Fix: null,
        Flank: flank?.Id,
        Reserve: reserve?.Id,
        ArtilleryPrep:
            ctx.FireSupport.CurrentPrepMission,
        AirCover:
            ctx.Air.CurrentCoverMission,
        Target: intent.Target.Id,
        ExecuteAt: executeAt);
}
```

# 221. Code skeleton — planned action board

```csharp
public sealed class PlannedActionBoard
{
    private readonly Dictionary<EntityId, float>
        plannedDamage = new();

    private readonly Dictionary<EntityId, float>
        repairReserved = new();

    public float PlannedDamage(EntityId target) =>
        plannedDamage.GetValueOrDefault(target);

    public void ReserveDamage(
        EntityId target,
        float expected)
    {
        plannedDamage[target] =
            PlannedDamage(target) + expected;
    }

    public void ReleaseDamage(
        EntityId target,
        float expected)
    {
        plannedDamage[target] =
            MathF.Max(
                0f,
                PlannedDamage(target) - expected);
    }
}
```

# 222. Code skeleton — simplified combat forecast

```csharp
public CombatForecast Forecast(
    Squad friendly,
    EnemyCluster enemy,
    float horizonS)
{
    float fdps =
        EffectiveDps(friendly, enemy);

    float edps =
        EffectiveDps(enemy, friendly);

    float fEh =
        EffectiveHealth(friendly);

    float eEh =
        EffectiveHealth(enemy);

    float enemyLoss =
        MathF.Min(eEh, fdps * horizonS);

    float friendlyLoss =
        MathF.Min(fEh, edps * horizonS);

    return new CombatForecast(
        FriendlyLoss: friendlyLoss,
        EnemyLoss: enemyLoss,
        FriendlyPowerAfter:
            MathF.Max(0, fEh - friendlyLoss) /
            MathF.Max(1, fEh),
        EnemyPowerAfter:
            MathF.Max(0, eEh - enemyLoss) /
            MathF.Max(1, eEh));
}
```

Production version cần tính:
- target mix;
- armour/penetration;
- range uptime;
- AoE;
- support;
- known cover/threat.

# 223. Code skeleton — pursuit discipline

```csharp
bool ShouldContinuePursuit(
    Squad squad,
    Entity target,
    SquadTask task,
    AiContext ctx)
{
    if (!target.Alive)
        return false;

    if (ctx.Time.Now - squad.PursuitStart >
        task.MaxPursuitSeconds)
        return false;

    if (Distance(
            target.Position,
            task.Anchor) >
        task.MaxPursuitDistance)
        return false;

    if (ctx.Objective.Urgency01(task) > 0.75f &&
        !TargetDirectlyThreatensObjective(
            target, task))
        return false;

    return true;
}
```

# 224. Advanced Tests

## Sync flank
Main ETA 8 s, flank 12 s:
- main stages ~4 s;
- contact delta <= 3 s.

## Route diversity
2 equal squads / 2 equal corridors:
- occupancy penalty khiến chúng tách route.

## Death memory
Một squad vừa chết tại choke:
- squad sau scout/alternate;
- không lặp blind push ngay.

## Opportunity fire
Turreted unit travel:
- turret bắn;
- hull route không đổi.

## Forecast
Frontal bad, flank good:
- flank plan thắng.

## Counterbattery
Nhiều enemy artillery shot từ cùng vùng:
- confidence tăng;
- counterbattery mission;
- own artillery scoot nếu threat phù hợp.

## Utilization
Ground unit theoretically legal nhưng thực tế không bắn được naval target:
- sau 20 s utilization thấp;
- purchase modifier giảm.

## Pursuit
Defending squad chase target:
- hết leash thì return objective.

## Reserve
Primary line collapse:
- reserve release.
Secondary easy fight:
- reserve vẫn giữ.

# 225. Advanced Metrics

Log:
```text
syncArrivalDeltaMean/P95
probeCount/probeSuccess
feintCount
fixFlankCount
routeDiversityEntropy
routeRepeatAfterFailure
plannedOverkillPrevented
duplicateRepairPrevented
counterBatteryMissions
artilleryScoots
pursuitAbortCount
unitClassUtilization
reserveUsefulReleaseRate
objectiveMissedDeadlineOrders
attackPackagesCreated/aborted
```

# 226. Conflict Rules

- feasibility hard filter luôn thắng tactic preference;
- traffic/collision safety thắng local formation;
- HoldFire thắng opportunity fire;
- objective emergency thắng feint/probe;
- short match timer có thể bỏ scout-before-commit;
- boss naval no-reverse luôn thắng local avoidance;
- explicit scripted boss salvo thắng cadence staggering;
- public telegraph reaction được phép; hidden future không được phép.

# 227. Behaviors được chốt thêm

ACCEPT:
1. Tactical Frontline.
2. Tactical Confidence không-morale.
3. Temporal influence memory.
4. Route diversity.
5. Recent death memory.
6. Scout-before-commit.
7. Probe-and-exploit.
8. Conditional feint.
9. Fix-and-flank.
10. Synchronized ETA attacks.
11. AttackPackage.
12. PlannedActionBoard.
13. Repair/AA/smoke deconfliction.
14. Counterbattery.
15. Shoot-and-scoot.
16. Predictive interception.
17. Cutoff.
18. Pursuit discipline.
19. Stances/opportunity fire.
20. Range margin.
21. Combat forecast.
22. Shallow counterfactual planning.
23. Attack abort on invalid assumptions.
24. Same-match adaptation.
25. Formation morphing.
26. Stable formation slots.
27. Mine/area-denial memory.
28. Screen behavior.
29. Sectorized escort.
30. Coverage optimizer.
31. Reserve release logic.
32. Economy of force.
33. SEAD package.
34. Aircraft risk routing.
35. CAP zones.
36. Boss weakpoint utility.
37. Boss telegraph response.
38. Tactical interrupt/replan.
39. Predictive congestion.
40. Deadlock graph.
41. Time-to-value buying.
42. Capability replacement.
43. Early objective rotation.
44. Counterattack windows.
45. Deterministic communication cues.

NOT ACCEPT:
- morale/panic;
- retreat-by-health;
- omniscient counter-building;
- deep RL runtime controller;
- deep MCTS per tick;
- permanent cross-match adaptation;
- random deception;
- perfect artillery origin;
- normal teleport anti-stuck.

# 228. Research / rationale

## OpenRA
Các AI module tách squad và production; squad manager phân ground/naval/air types, còn production có relative build shares, unit limits và cash thresholds. Attack behavior cũng tách opportunity fire, persistent targeting và range margin. Pattern áp dụng: capability-based production, stance, target persistence và range band.

## Total War
Battle AI có thay đổi để lực lượng flank cố gắng tấn công cùng thời điểm với main force; formation cũng đặt cavalry/flanking element ra flank. Pattern áp dụng: ETA synchronization và role-based formation.

## Killzone 3
Hierarchical squad AI dùng strategic graph + influence map; influence có spatial/temporal smoothing, recent deaths và route penalty khi friendly squads đã chọn đường đó. Pattern áp dụng: temporal memory, safe regroup, route diversity.

## Days Gone
Squad là một AI entity riêng, phân role cho members và dùng group-level confidence để quyết định posture. Pattern áp dụng: TacticalConfidence và frontline-aware coordination; không dùng morale hay HP-retreat.

## Gears Tactics
AI tạo planned world state, cooperative goals, combo actions và interrupt/replan khi execution không còn khớp plan. Pattern áp dụng: PlannedActionBoard, attack package, reservation và dependency-based replanning.

## StarCraft / BWAPI bot ecosystem
Fog-respecting state, blackboard/FSM, squad grouping và short combat simulation cho thấy giá trị của macro/micro separation và local forecast. Pattern áp dụng: anomaly detection, forecast, role/capability assignment và same-match feedback.

# 229. Recheck Advanced Pack

Đã kiểm lại các conflict chính:

- không thêm morale;
- không retreat-by-health;
- không thay boss armour/HP;
- không thay economy formula;
- không thay weapon stats;
- naval boss vẫn no reverse;
- hull/turret tách riêng;
- advanced behavior vẫn qua map/domain feasibility;
- no-map-influence vẫn hard reject;
- fog memory chỉ từ seen/remembered data;
- counterbattery chỉ từ observed fire;
- feint không đọc hidden reaction;
- forecast shallow + cached, không gây deep-search CPU explosion;
- route diversity không override route duy nhất hợp lệ;
- opportunity fire không steer boss hull;
- synchronized attack dùng staging để không tạo congestion mới.

# 230. Final Architecture v2

```text
MAP TOPOLOGY / DOMAIN GRAPH
        ↓
FOG-RESPECTING WORLD MODEL
        ↓
TEMPORAL INFLUENCE + FRONTLINE
        ↓
THREAT / OPPORTUNITY / DEADLINE MODEL
        ↓
PROCUREMENT + FORCE PLANNER
        ↓
SHALLOW COUNTERFACTUAL PLAN SCORING
        ↓
ATTACK PACKAGE / RESERVE / OBJECTIVES
        ↓
SQUAD ROLE / STAGING / SHARED ROUTE
        ↓
PLANNED ACTION RESERVATION
        ↓
TARGET / SUPPORT / FIRE-MISSION COORDINATION
        ↓
TACTICAL LOCAL DECISION
        ↓
TRAFFIC / COLLISION / STEERING
```

Boss:

```text
MISSION / PHASE
      ↓
BOSS PLAN
  ↙        ↘
HULL       WEAPON DIRECTOR
 ↓              ↓
LANE        TARGET HANDOFF
 ↓              ↓
TURN         MOUNT ARC
 ↓              ↓
CPA          FIRE CADENCE
```

# 231. Final Design Principle v2

AI nên cho cảm giác:
- biết mục tiêu;
- biết quân nào thực sự hữu ích trên map;
- biết đợi đồng đội;
- biết chia lane;
- biết không feed từng xe;
- biết scout trước khi lao vào vùng mù;
- biết đổi đường sau một kill zone;
- biết phối hợp pháo + main + flank;
- biết giữ reserve;
- biết không chase mục tiêu vô nghĩa;
- biết tàu phải lái như tàu;
- biết boss hull khác turret;
- biết tự đánh giá cùng loại unit đang “có tác dụng thật” hay không;
- và giải thích được mọi quyết định quan trọng trong log.

Đây là behavior target cuối cùng khuyến nghị cho Machine Brigade AI.

---

# PART B — COMBAT ROLE DOCTRINE (MANDATORY)

This layer is required to eliminate the bug where a vehicle has a valid role but still chooses poor targets or idles.

Each combat unit resolves:

```text
RoleDoctrine
+ MissionDoctrine
+ ModeDoctrine
+ WeaponSuitability
+ LocalThreat
= TacticalCombatIntent
```

Target selection is therefore not a single global priority table.

## B1. Generic target score

```text
TargetScore =
    BaseTargetValue
  × RolePreference
  × MissionPreference
  × ModePreference
  × WeaponSuitability
  × ThreatUrgency
  × FiringSolutionQuality
  × TargetPersistence
  × ObjectiveRelevance
  - OverkillPenalty
  - AimTurnPenalty
  - ExposurePenalty
```

Any infeasible target is removed before this formula.

## B2. Breacher / wall-breaker doctrine

Applies to:
- armored bulldozer;
- engineer breach vehicles;
- demolition line vehicles;
- any explicit Breacher role.

Priority:

1. blocking wall section whose destruction reduces route cost;
2. destructible gate/obstacle blocking the mission corridor;
3. tower directly defending the breach point;
4. structure preventing objective access;
5. enemy combat unit posing immediate lethal/self-defence threat;
6. other valid targets.

Critical rule:

> A Breacher must not abandon a mission-blocking wall to shoot a random nearby light unit unless that unit is an immediate survival blocker.

Walls are not globally high priority. Only `BlockingStructure` / `BreachObjective` structures get the hard bonus.

Suggested breach utility:

```text
BreachUtility =
    PathCostReduction
  + FriendlyUnitsUnblocked
  + ObjectiveAccessValue
  + ChokeRelief
  - BreachTime
  - ThreatAtBreach
```

## B3. Siege / anti-structure doctrine

Priority:

1. tower currently damaging the assault/objective;
2. shield/radar/SAM/heavy defensive tower;
3. blocking wall/gate on main effort;
4. mission/HQ structure if objective requires;
5. static artillery/support structure;
6. heavy ground target;
7. light targets only when no valuable structure remains or in self-defence.

Siege platforms should not waste long reload shots on scouts while useful structures are available.

## B4. Tank destroyer / Rail doctrine

Priority:

1. Armour5;
2. Armour4;
3. heavy/super-heavy;
4. boss combat part / heavy boss target if weapon is suitable;
5. MBT;
6. medium target;
7. light target only if no better heavy target or the light target is immediately critical.

This preserves the purpose of Pen5 and Kinetic Overpenetration.

## B5. MBT / Heavy doctrine

Priority:

1. immediate threat to self/squad;
2. enemy heavy / MBT;
3. enemy TD/AT threatening own heavies;
4. objective defender;
5. structure if mission requires;
6. light/recon/support.

Do not chase support far outside formation leash.

## B6. IFV / autocannon / light combat doctrine

Priority:

1. light vehicle;
2. recon;
3. drone / low-altitude air when weapon permits;
4. fragile support;
5. medium combat vehicle;
6. heavy only when no suitable target exists or for self-defence.

## B7. AA / SAM doctrine

Priority:

1. aircraft attacking protected asset;
2. bomber / strike aircraft;
3. attack helicopter/gunship;
4. fighter;
5. drone if compatible;
6. no ground chase unless platform has a valid separate ground weapon.

SAM must preserve coverage anchor and pursuit leash.

## B8. Artillery / mortar / MLRS doctrine

Priority:

1. counter-battery target;
2. tower / defensive cluster;
3. dense enemy cluster;
4. static heavy target;
5. objective defenders;
6. isolated light target only if urgent or no better target.

Heavy salvo weapons use a minimum target-value threshold.

## B9. Recon doctrine

Primary jobs:
1. scout unknown/high-risk routes;
2. expose artillery/SAM/boss weakpoints;
3. validate flank corridors;
4. provide objective vision;
5. combat only via opportunity fire/self-defence.

Recon must not abandon scouting to chase kills.

## B10. Engineer / repair / support doctrine

Repair:
- high-value repair demand;
- boss/critical escort if assigned;
- frontline heavy;
- important support.

Combat engineer/breacher:
- structure/path task outranks random combat.

Support units should optimize coverage, not chase enemy contact.

## B11. Bomber / strike doctrine

Priority:
1. high-value structure;
2. artillery;
3. SAM/radar when SEAD-capable;
4. heavy cluster;
5. objective cluster;
6. single light target only if strategically urgent.

## B12. Fighter doctrine

Priority:
1. bomber;
2. strike aircraft;
3. fighter threatening own strike package;
4. gunship/helicopter;
5. drone.

No ground attack unless the aircraft/weapon explicitly supports it.

## B13. Loitering/drone doctrine

Anti-armour:
- heavy armour;
- TD/artillery;
- expensive support;
- tower.

Lancet-like anti-artillery:
- artillery;
- SAM/radar;
- parked support;
- tower;
- heavy target.

Never "nearest valid target" as the only rule.

---

# PART C — COMBAT ACTIVITY WATCHDOG (MANDATORY)

Movement anti-stuck is not enough. Add a separate combat watchdog.

Each armed unit tracks:

```text
lastTargetAcquireTime
lastAimProgressTime
lastFireTime
lastDamageAttemptTime
hasValidTarget
hasFiringSolution
weaponReady
blockedByArc
blockedByLOS
blockedByMinRange
blockedByFriendly
blockedByMovementState
explicitHoldReason
```

## C1. Combat anomaly

If:

```text
hasValidTarget
AND hasFiringSolution
AND weaponReady
AND not explicit HoldFire
AND no fire beyond expected aim/reload window
```

for roughly `1.5–2.5 s` beyond the weapon's expected readiness:

=> `COMBAT_ANOMALY`.

Recovery sequence:

1. validate target entity;
2. recompute mount arc;
3. clear stale aim/attack state;
4. recompute LOS/firing lane;
5. attempt local firing-position correction;
6. switch target if current target is invalid/stale;
7. if still unresolved, escalate to Squad/Tactical recovery;
8. log exact reason.

## C2. No-idle-armed-unit invariant

An armed unit that is:
- not moving;
- not firing;
- not reloading;
- not repairing/resupplying;
- not holding an explicit ambush/defence order;
- not disabled;
- not waiting for a valid known reason;

for more than the configured threshold must have a reason code.

Valid examples:

```text
HOLD_FIRE_AMBUSH
RELOADING
NO_REACHABLE_TARGET
WAITING_MIN_RANGE
BLOCKED_BY_FRIEND
WAITING_FORMATION
OBJECTIVE_HOLD
NO_VALID_WEAPON_TARGET
DISABLED_MAIN_WEAPON
WAITING_FIRE_MISSION
```

No reason code => state-machine bug.

---

# PART D — TERRAIN / COVER / FIRING POSITION INTELLIGENCE

The AI must understand good and bad positions, not just path distance.

## D1. Position score

```text
PositionScore =
    WeaponUptime
  + CoverValue
  + HullDownValue
  + Elevation/Observation
  + EscapeRoute
  + FriendlySupportCoverage
  - EnemyThreat
  - SplashDensityRisk
  - Congestion
  - FriendlyFireLaneBlocking
  - CounterBatteryRisk
```

Weights depend on role.

## D2. Hull-down

For TD/MBT/heavy where terrain allows:
- prefer positions exposing turret/weapon while hull is masked;
- only when weapon arc and LOS remain valid;
- do not obsessively path to hull-down if objective timing is critical.

## D3. Ridge / high ground

Recon and long-range direct-fire units gain score for:
- long LOS;
- observation;
- clear firing lane.

Artillery does not need visual high ground unless its weapon/spotting model benefits.

## D4. Dead ground / protected firing pockets

Mortar/MLRS/artillery prefer:
- lower direct enemy LOS;
- enough sky/arc clearance;
- valid range;
- multiple exit routes;
- nearby AA support.

## D5. Cover reservation

High-quality firing positions may be reservable:
- TD/sniper-like vehicle spots;
- artillery pockets;
- hull-down points.

Avoid 4 units selecting the same exact point.

---

# PART E — FRIENDLY FIRING-LANE / BLOCKED-SHOT HANDLING

A common idle bug is "valid target but friendly vehicle blocks the shot."

## E1. FiringLane check

Before committing:

```text
LOS to target
mount arc
friendly collider intersection
splash/friendly-fire risk if applicable
```

## E2. Resolution

If blocked by friendly:
1. wait briefly if blocker is moving through;
2. choose a small lateral sidestep;
3. switch to an alternate equivalent formation slot;
4. choose another target;
5. only move the blocker if Squad layer can do so safely.

Do not let both units oscillate.

## E3. Boss multi-mount lanes

Each boss mount resolves its own lane.
One blocked turret does not stop the entire boss from attacking.

---

# PART F — DAMAGE / COMPONENT-STATE ROLE ADAPTATION

This is NOT retreat-by-health.

AI changes behavior when capability changes.

Examples:

## F1. Main gun disabled
MBT:
- cease "main battle" aggressive doctrine;
- use secondary/self-defence;
- become screen/support/objective body if useful.

## F2. Engine crippled
- adjust route/formation slot;
- do not assign long flank mission;
- prefer hold/support if still combat-capable.

## F3. Radar destroyed
AA/radar platform:
- lose radar-derived target ability/coverage;
- hand off coverage responsibility.

## F4. APS/shield lost
- survivability estimate changes;
- formation may place unit less aggressively.
- no health-retreat trigger.

## F5. Boss mount/part destroyed
Broadside logic recomputes effective-DPS bearing.
If left battery is destroyed, the boss should no longer keep presenting that useless side.

---

# PART G — THREAT-SPECIFIC FORMATION SWITCHING

Existing formations remain, but triggers are formalized.

```text
Enemy splash/artillery high -> Spread
Narrow choke/bridge/gate   -> Travel
Static objective defence   -> Hold
Validated flank opening    -> Flank
Low cohesion               -> Regroup
```

Use hysteresis:
- do not switch back immediately;
- minimum commitment window;
- emergency can override.

---

# PART H — OBJECTIVE-AWARE TARGET PRIORITY

`ThreatToObjective` gets mode-aware weighting.

Examples:

Conquest:
- unit actively capturing a critical point gets high priority.

Escort:
- unit currently damaging convoy outranks a distant heavy that is not relevant.

Defend:
- breacher threatening the gate/wall rises sharply.

BossRush:
- dangerous exposed boss part outranks generic hull.

Siege:
- defensive tower covering the breach outranks unrelated vehicle.

This modifies role priority; it does not replace weapon suitability.

---

# PART I — MODE COMBAT DOCTRINE (MANDATORY)

Mode profile must change **positioning and role behavior**, not only tactic preference.

Every mode defines:

```text
FrontlinePolicy
FireSupportPolicy
SupportPolicy
PursuitPolicy
ReservePolicy
RepositionTriggers
ObjectiveTargetWeights
```

## I1. Assault / Breakthrough

Formation:
- heavy/MBT/breacher front;
- IFV/TD second line;
- mortar support;
- MLRS/heavy launcher deeper;
- AA between frontline and fire-support layer;
- repair/ammo/EW behind line 2.

Fire support:
- Mortar anchor at roughly 55–75% of usable weapon range behind target/front context.
- Artillery: 65–85%.
- MLRS: 75–90%.
- very-long-range/ballistic: 85–95% or fixed pocket if map-wide coverage.

Artillery sequence:
1. defensive tower;
2. breach cluster;
3. counterbattery;
4. assault support.

Do not follow squad centroid meter-by-meter.

Reposition only when:
- utilization drops;
- frontline moved materially;
- range band lost;
- counterbattery threat;
- route/mission changed.

## I2. Defend / Hold

Do not move launchers to meet enemy.

Mortar:
- behind first defence line;
- at least one fallback firing position.

MLRS:
- deeper than mortar;
- separated from HQ/tower cluster.

TD:
- hull-down/crossfire.

Mine layer:
- pre-place mines on approaches;
- no suicidal mid-combat mine runs.

AA:
- protect HQ/artillery/support;
- no long chase.

Defence can fall back by strategic line/objective state, never by health threshold.

## I3. Capture / Conquest / Hill

Capture body:
- MBT/light/IFV/appropriate durable units.

Fire support:
- stays outside capture circle unless necessary;
- chooses support anchor that covers current objective and approach lanes;
- ideally also covers likely next objective.

Reserve:
- fast unit response package.

Reposition fire support only when new objective is no longer covered or threat demands it.

## I4. Escort

Use convoy-relative sectors:
- front screen;
- left/right screen;
- AA umbrella;
- rear guard;
- repair/support trail;
- fire-support leapfrog.

Mortar:
- behind convoy but in range of expected front.

MLRS:
- firing pocket to firing pocket;
- not physically glued to convoy.

Escort leash always wins against random pursuit.

## I5. Siege

Most sophisticated artillery doctrine:

1. recon/spot;
2. counterbattery;
3. radar/SAM/tower suppression;
4. breach wall/gate;
5. defensive cluster suppression;
6. main assault.

Mortar closest support layer.
MLRS farther.
Heavy artillery deepest.

Shoot-and-scoot after configured salvos when counterbattery risk exists.

## I6. Survival

No chase.

Prepare 2–3 firing positions.
Rotate by wave direction.
Keep escape/reload lane.

AA covers survival anchor/base.
Fast units intercept and return.

## I7. BossRush

Target:
1. lethal telegraph avoidance;
2. dangerous boss part;
3. exposed/disabled-value boss part;
4. escorts/adds;
5. hull.

Artillery/launcher predicts boss firing region rather than following physically.
Never stand in telegraph danger simply to maintain DPS.

## I8. Deathmatch

No capture anchor.
Fire support uses friendly combat centroid/frontline as a moving **logical** anchor, not exact centroid following.

Reposition when:
- utilization falls;
- frontline moves beyond useful range band;
- firing pocket compromised.

Avoid gifting expensive units.

## I9. Hunt

Scout/fast units locate/intercept.
Artillery predicts likely area and uses intel.
Do not make launchers directly chase mobile targets.

## I10. Recon

Recon remains main task.
Heavy support only engages high-value spotted targets.
Avoid revealing artillery/strike platform unnecessarily if mission rewards stealth/observation.

## I11. Operation / phased campaign

At each phase transition rebuild:
- objective anchor;
- fire-support anchor;
- reserve location;
- AA coverage;
- procurement role deficits;
- pursuit leash;
- target priorities.

Do not carry stale doctrine from a previous phase.

## I12. Showdown / escalating duel

Early:
- defensive support pocket;
- preserve expensive units.

Mid:
- balanced support / objective pressure.

Final/sudden death:
- reduce reserve;
- move fire-support forward only enough to maintain value;
- increase time-to-value weighting.

## I13. Shootdown / air-objective modes

AA coverage and survival become primary.
Ground combat units defend AA/support.
Do not chase unrelated ground targets unless they threaten the AA mission.

## I14. Fixed deck / scripted modes

Respect scenario restrictions first.
Apply doctrine only inside permitted unit/task set.

## I15. Mode inheritance

Do not hardcode identical copies.
Use:

```text
base RoleDoctrine
+ ModeDoctrine override
+ mission phase override
```

Mode profiles remain data-driven.

## I16. Endless

Inherits Defend doctrine but changes long-horizon behavior:

- rotate firing positions to avoid permanent counterbattery exposure;
- keep repair/support logistics sustainable;
- do not spend all reserve on an early wave unless HQ/base emergency;
- procurement should react to observed wave composition EMA;
- clear obsolete mines/reservations/anchors between major wave-direction changes if the engine supports it;
- fire-support anchors may cycle among prepared pockets rather than remain permanently fixed.

No match-end deadline pressure; prioritize sustainable utilization and traffic health.

## I17. Weekly

Inherits Siege doctrine, but progress can persist across attempts.

AI must:
- value already-breached defensive layers correctly;
- not waste breacher effort on a layer already permanently cleared;
- rebuild the current attempt's fire-support plan from current fortress state;
- prioritize remaining high-value defensive systems;
- use time-to-value because each attempt has a practical combat window;
- preserve valid stage/layer state supplied by the mode instead of assuming a fresh fortress.

## I18. Campaign Hold / Protect / Outpost / Relieve

These mission-goal profiles inherit Defend/Hold principles but use the mission object as the protected anchor.

- `Hold`: maintain contest/control area, fire support outside the objective body.
- `Protect`: ThreatToProtectedAsset is the dominant target modifier.
- `Outpost`: defend the outpost while preserving useful firing arcs and rebuild/support access.
- `Relieve`: fast/main force reaches the threatened friendly position; artillery anchors behind the relief corridor rather than staying at original spawn.

## I19. Evacuate

Inherits Escort but the destination and survival of evac entities dominate.

- screen ahead;
- rear guard against pursuers;
- AA coverage on convoy/evac group;
- no random pursuit away from evacuation corridor;
- fire support leapfrogs to cover the next convoy segment.

## I20. Intercept

Time/deadline dominates.

- use fast suitable units;
- predictive interception/cutoff;
- do not assign slow units whose ETA misses the intercept window;
- artillery targets predicted choke/route only with sufficient intel confidence;
- pursuit ends when intercept mission becomes impossible or target leaves mission relevance.

## I21. Recon mission goal

ReconQuiet / no-strike star conditions, if active, must be visible to doctrine.

- HoldFire where appropriate;
- avoid unnecessary artillery/air strikes;
- prioritize observation and safe extraction;
- only break quiet posture for explicit survival/mission necessity.

## I22. ShootDown

- preserve AA/SAM;
- maintain overlapping coverage rather than chase aircraft;
- air target handoff prevents overcommit;
- ground enemies only become primary when they directly threaten AA/objective assets.

## I23. Destroy

Destroy mission identifies the mission structure/target as the strategic target.

- siege/bomber/strike receive high MissionPreference;
- escort/AA/support protect the strike package;
- avoid wasting heavy strike ordnance on unrelated targets before the mission target is accessible.

## I24. Duel

- preserve high-value units according to current mode rules;
- focus combat power rather than over-dispersing;
- fire support follows the combat front;
- no objective-capture logic unless the scenario explicitly adds one.

## I25. Boss mission goal

Same principles as BossRush but for a single campaign boss:
- telegraph survival;
- dangerous boss parts;
- adds/escorts threatening the force;
- hull afterward;
- star/mastery constraints may modify optional behavior but never violate survival/fog fairness.

## I26. Profile completeness rule

At load/validation time:

```text
for every aiModeProfiles.profiles row:
    assert a ModeDoctrine exists
    OR an explicit inherits/fallback doctrine exists
```

No profile is allowed to silently fall back to generic "move toward nearest enemy" behavior.

For every campaign goal mapping:

```text
aiModeProfiles.goals -> profile -> doctrine
```

must resolve successfully.

If a new mode/profile is added later without doctrine:
- development build warning/error;
- production falls back to `BalancedObjectiveDoctrine`, not raw nearest-enemy behavior.

---

# PART J — FIRE SUPPORT ANCHORS

Artillery does not follow squad centroid.

Each support group receives a `FireSupportAnchor`.

Anchor score:

```text
AnchorScore =
    ObjectiveCoverage
  + EnemyApproachCoverage
  + FriendlyFrontCoverage
  + AAProtection
  + EscapeRoute
  + CounterBatterySafety
  - Threat
  - Congestion
  - MinRangeViolation
  - Spawn/TrafficBlocking
```

Reposition triggers:
- objective/frontline moved outside effective range band;
- utilization below threshold;
- target access lost;
- counterbattery;
- terrain state changes;
- mode phase changes.

---

# PART K — AI HEALTH MONITOR (MANDATORY SYSTEM WATCHDOG)

Create an aggregate monitor above individual watchdogs.

Track:

```text
armedIdleWithoutReason
squadsNoDamageSeconds
blockedUnits
severeUnstuckEvents
ordersPerUnitPerMinute
targetSwitchesPerMinute
squadActionSwitchesPerMinute
noMapInfluencePurchases
lowUtilizationUnitClasses
stalledObjectiveAssignments
combatAnomalies
deadlockCycles
navalReverseAttempts
```

## K1. Recovery actions

If systemic threshold trips:

### Too many idle armed units
- force target/firing-solution audit;
- refresh combat state;
- log top reasons.

### Squad no useful damage for 10–20 s
- recompute firing anchor;
- re-evaluate route;
- re-evaluate mission fit.

### High blocked-unit ratio
- activate TrafficCoordinator congestion escalation;
- split/re-route packets.

### Repeated low-utilization purchases
- same-match purchase modifier.

### Excessive churn
- increase commitment/hysteresis temporarily.

### Naval reverse attempt
- hard assertion/error in debug;
- controller must choose turn/slow/alternate lane.

The Health Monitor must never cheat or issue magical state changes. It only triggers valid re-evaluation/recovery.

---

# PART L — AMMO / RELOAD-AWARE TACTICS

If a weapon uses meaningful magazine/reload cycles:

- do not begin an exposed charge with an empty/near-empty magazine unless objective emergency;
- use long reload windows for short reposition;
- artillery may scoot during reload;
- support weapons avoid exposing themselves while unable to fire;
- do not cancel reload repeatedly due target churn.

This makes magazine/reload gear meaningful to AI behavior.

---

# PART M — ANTI-CHEESE / SAME-MATCH ADAPTATION

Allowed adaptation uses only observed match data.

Examples:
- player repeatedly baits chase through same choke;
- player camps with artillery;
- air-heavy composition;
- repeated fixed-route ambush;
- repeated tower-defense pattern.

Responses:
- reduce pursuit leash;
- increase recon;
- alternate route;
- increase counterbattery/SEAD;
- adjust procurement role deficit;
- use smoke/support.

No hidden-state knowledge and no cross-match learning unless separately designed.

---

# PART N — TOWER AI COORDINATION

Keep existing tower modes, but add coordination:

- avoid overkill where multiple towers target one weak unit;
- SAM/AA towers prioritize aircraft threatening protected zone;
- AT tower values heavy targets;
- drone hangar/artillery-capable towers value enemy artillery/support;
- shield/PD systems prioritize relevant interceptable threats;
- tower target mode may be overridden by critical objective threat.

Static towers do not path, but still use PlannedActionBoard for deconfliction.

---

# PART O — FULL DEBUG / REASON CODE SET

Minimum reason namespaces:

```text
PURCHASE_*
TARGET_*
POSITION_*
ROUTE_*
TRAFFIC_*
JAM_*
COMBAT_IDLE_*
FORMATION_*
MODE_*
BOSS_*
NAVAL_*
SUPPORT_*
AIR_*
ARTILLERY_*
OBJECTIVE_*
WATCHDOG_*
```

Every rejection should be explainable.

Examples:

```text
PURCHASE_NO_MAP_INFLUENCE
PURCHASE_ROLE_SATURATED
TARGET_NO_FIRING_SOLUTION
TARGET_WRONG_WEAPON_DOMAIN
POSITION_FRIENDLY_BLOCK
JAM_CHOKE_QUEUE
COMBAT_IDLE_STALE_AIM
MODE_DEFEND_NO_CHASE
BOSS_HULL_ROUTE_OWNS_HEADING
NAVAL_REVERSE_FORBIDDEN
ARTILLERY_COUNTERBATTERY_SCOOT
WATCHDOG_SQUAD_ZERO_UTILIZATION
```

---

# PART P — PERFORMANCE / UPDATE BUDGET

Suggested update classes:

```text
Steering/avoidance:  10 Hz
Tactical combat:      4 Hz
Squad:                2 Hz
Commander:            1 Hz
Procurement:          0.5 Hz
Heavy forecast:       event-driven + cached
Frontline/influence:  staggered
```

Use:
- spatial hash/grid;
- bounded nearest-neighbour queries;
- cache map/domain feasibility;
- sparse reservation maps;
- shallow forecast only;
- no per-frame deep search.

---

# PART Q — IMPLEMENTATION ORDER

## P0 Correctness
1. combat activity watchdog;
2. no-idle-armed-unit invariant;
3. target hard feasibility;
4. breach/structure targeting;
5. no-map-influence procurement;
6. naval no-reverse;
7. hull/turret separation;
8. staged anti-stuck.

## P1 Movement / traffic
1. shared corridor;
2. TrafficCoordinator;
3. deterministic passing;
4. choke queue/reservation;
5. wreck nav invalidation;
6. spawn clear zones;
7. predictive congestion/deadlock cycle.

## P2 Role/mode intelligence
1. CombatRoleDoctrine;
2. ModeCombatDoctrine;
3. FireSupportAnchor;
4. terrain/cover;
5. friendly firing-lane handling;
6. component-state adaptation;
7. formation switching.

## P3 Coordination
1. frontline;
2. planned action reservations;
3. synchronized attacks;
4. reserve;
5. route diversity;
6. counterbattery;
7. pursuit discipline.

## P4 Advanced planning
1. short combat forecast;
2. shallow counterfactual plans;
3. probe/feint/fix-flank;
4. same-match adaptation;
5. SEAD/air packages;
6. advanced boss cadence/weakpoint logic.

## P5 Monitoring/optimization
1. AI Health Monitor;
2. performance profiling;
3. tuning and regression sweeps.

---

# PART R — REQUIRED REGRESSION MATRIX

## R1. "Standing still but not attacking"
Cases:
- valid target + clear LOS;
- valid target but friendly blocks;
- target inside min range;
- target outside mount arc;
- stale target entity;
- weapon reloaded but aim state stuck;
- unit in formation waiting incorrectly.

Expected:
- explicit reason or automatic recovery;
- never indefinite silent idle.

## R2. Breacher
- random jeep beside blocking wall;
- wall must remain priority unless jeep is immediate self-defence threat.

## R3. Siege
- tower + scout both visible;
- structure priority wins if weapon and mission support it.

## R4. Fire support by mode
Test mortar/MLRS in:
- Assault
- Defend
- Conquest
- Escort
- Siege
- Survival
- BossRush
- Deathmatch
- Hunt
- Operation phase transition
- Showdown

Verify:
- correct anchor;
- correct pursuit;
- correct reposition trigger.

## R5. Component damage
- boss loses left broadside;
- broadside preference must recompute.
- MBT loses main gun;
- role changes without health-retreat.

## R6. Friendly firing lane
Two tanks line up:
- rear tank sidesteps/chooses alternate slot instead of silently idling.

## R7. Cover
TD has open-ground position vs hull-down position with equivalent mission timing:
- hull-down preferred.

## R8. Health monitor
Inject artificial stalled squad:
- monitor detects;
- triggers valid re-evaluation;
- logs cause.

---

# PART S — ACCEPTANCE GATES

Task is not complete unless all are true:

```text
naval boss reverse events = 0
no-map-influence purchases = 0 except explicit scripted exception
armed idle without reason = 0
combat anomaly recovery verified
breacher blocking-wall priority verified
mode-aware fire-support anchors verified
boss hull/turret separation verified
traffic deadlock recovery verified
fog fairness tests pass
48v48 performance acceptable
```

Target severe unstuck:

```text
<= 1 per 10 unit-minutes
```

on normal open maps.

---

# PART T — RESEARCH-DERIVED DESIGN RATIONALE

External research is guidance, not authority over repo behavior.

## OpenRA / modular RTS patterns
Useful ideas:
- production composition rather than first-available purchase;
- squad-level grouping;
- stances/opportunity fire;
- persistent target behavior;
- range margin.

## Total War battle AI
Useful pattern:
- synchronize flanking force arrival with main force;
- role-aware formation placement.

## Killzone 3 hierarchical multiplayer bots
Useful patterns:
- squad as an AI agent;
- plan continuation/invalidity conditions;
- tactical position/path queries;
- hierarchical planning.

## Days Gone squad coordination
Useful patterns:
- dynamically created squads;
- friendly/enemy spatial analysis;
- group-level confidence/posture.
Machine Brigade explicitly does **not** import morale/panic; only the spatial/group-confidence pattern.

## Gears Tactics
Useful pattern:
- layered planning;
- planned world state;
- committed actions represented before later agents choose;
- interrupt/replan only when continuation conditions fail.

## StarCraft/BWAPI bot ecosystem
Useful patterns:
- fog-respecting non-cheating AI;
- short-horizon combat simulation;
- macro/micro separation;
- pathfinding/kiting utilities.

---

# PART U — FINAL MASTER ARCHITECTURE

```text
MAP TOPOLOGY / DOMAIN GRAPH
        ↓
FOG-RESPECTING WORLD MODEL
        ↓
TEMPORAL THREAT / FRONTLINE / OBJECTIVE MODEL
        ↓
MODE DOCTRINE + ROLE DOCTRINE
        ↓
PROCUREMENT / FORCE PLANNER
        ↓
SHALLOW PLAN / ATTACK PACKAGE
        ↓
SQUAD ASSIGNMENT / RESERVE / STAGING
        ↓
SHARED ROUTE / TRAFFIC / FORMATION
        ↓
PLANNED ACTION BOARD
        ↓
TARGET / SUPPORT / FIRE-SUPPORT COORDINATION
        ↓
TACTICAL COMBAT + COMBAT WATCHDOG
        ↓
FIRING POSITION / COVER / FIRING-LANE
        ↓
LOCAL STEERING / COLLISION AVOIDANCE
        ↓
AI HEALTH MONITOR / DEBUG / RECOVERY
```

Boss/naval:

```text
MISSION / PHASE
      ↓
BOSS MISSION CONTROLLER
   ↙         ↘
HULL          WEAPON DIRECTOR
 ↓                 ↓
ROUTE/LANE     TARGET/MOUNT ASSIGNMENT
 ↓                 ↓
TURN RADIUS     ARC / FIRING LANE
 ↓                 ↓
CPA/TRAFFIC     FIRE CADENCE
```

Core principle:

> Hull decides where the platform goes and how the body turns.  
> Turrets/mounts decide what they shoot.  
> Only hull-dependent weapons may request body alignment, and that request is arbitrated by the movement/mission controller.

---

# PART V — FINAL IMPLEMENTATION REPORT REQUIRED

Coding AI must report:

1. changed files;
2. new classes/services;
3. old behavior -> new behavior;
4. tunables;
5. behaviors fully implemented;
6. scaffolded/not-yet-implemented behavior + reason;
7. combat-idle tests;
8. role-doctrine tests;
9. mode-doctrine tests;
10. procurement tests;
11. naval/boss tests;
12. traffic tests;
13. squad tests;
14. targeting tests;
15. cover/firing-lane tests;
16. component-state tests;
17. Health Monitor tests;
18. performance results;
19. severe-unstuck count;
20. DecisionLog examples;
21. generated outputs regenerated;
22. stale old-value/spec scan result.

Regenerate relevant canonical/generated artifacts if the repo contains them:

- `09_ai.xlsx`
- `09_ai.md`
- `04_che_do_kinh_te_ai.xlsx/.md`
- `02_boss.xlsx/.md`
- `06_ban_do.xlsx/.md`
- `00_index.xlsx`
- `README.md`
- `CHANGES.md`
- AI JSON/CSV/schema/agent-readable docs
- AI regression/performance reports

Do not manually patch generated outputs when a generator exists.

---

# PART W — FINAL NON-NEGOTIABLE CONFIRMATIONS

Final report must explicitly confirm:

```text
No morale system.
No retreat-by-health.
AI remains fog-respecting.
Naval boss reverse is disabled.
Boss hull target and turret target are independent.
Target does not directly steer boss hull.
No-map-influence purchase is rejected before scoring.
Armed unit idle without reason is treated as a bug.
CombatActivityWatchdog is active.
Breacher prioritizes mission-blocking walls/gates.
Siege prioritizes defensive structures when appropriate.
ModeCombatDoctrine changes mortar/MLRS/artillery positioning by mode.
Artillery follows FireSupportAnchor, not squad centroid.
Friendly blocked-shot handling exists.
Terrain/cover firing-position scoring exists.
Component-state adaptation exists.
AI Health Monitor exists.
Boss armour/HP are unchanged by this AI task.
```

This document is the single source of truth for AI behavior implementation.

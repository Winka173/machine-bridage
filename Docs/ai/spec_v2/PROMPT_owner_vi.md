Hãy dùng file đính kèm:

@Machine_Brigade_AI_Behavior_Full_Spec_v2.md  

làm **spec AI behavior chính thức mới nhất** cho Machine Brigade.

Mục tiêu của task này là:

1. audit toàn bộ AI runtime hiện tại;
2. map từng behavior trong spec vào code/data hiện có;
3. implement các thay đổi theo thứ tự ưu tiên;
4. giữ lại các hệ đang tốt, không rewrite mù quáng;
5. regenerate toàn bộ docs/data liên quan;
6. chạy regression/performance tests;
7. báo cáo rõ phần nào đã implement hoàn toàn, phần nào chỉ scaffold nếu architecture hiện tại chưa hỗ trợ.

Không hỏi lại tôi về các giá trị trong spec. Các giá trị trong file là quyết định final, trừ khi phần dưới đây ghi override.

# 1. FILE SPEC CÓ THẨM QUYỀN

File đính kèm:

`Machine_Brigade_AI_Behavior_Full_Spec_v2.md`

là nguồn yêu cầu chính cho task AI này.

Nếu code/data hiện tại dùng identifier khác:
- map theo semantics;
- không tạo duplicate system chỉ để khớp tên trong spec;
- ưu tiên integrate vào architecture hiện có.

Nếu spec nói giữ behavior hiện tại:
- không xóa;
- chỉ refactor nếu cần để hỗ trợ behavior mới.

---

# 2. CÁC BUG BẮT BUỘC PHẢI FIX

Ít nhất phải xử lý tận gốc:

## Boss / naval AI
- boss biển quay đầu theo target không tự nhiên;
- boss biển có thể đi lùi;
- hull movement và turret targeting đang bị coupling;
- boss/naval unit avoidance quá giống ground vehicle;
- route/broadside/turn radius chưa đủ tự nhiên.

Final:
- naval boss `allowReverse = false`;
- hull follow mission/lane;
- turret/mount target độc lập;
- target không trực tiếp steer hull;
- path respect minimum turn radius;
- broadside dùng weapon arcs / effective DPS;
- predictive collision/CPA;
- heading hysteresis;
- lane following;
- boss corridor reservation.

## AI mua quân
Không được tiếp tục mua unit không thể tác động tới trận.

Ví dụ:
- boss biển ngoài tầm ground vehicle;
- map không có land objective hữu ích;
- tank không thể reach hoặc fire tới bất kỳ active target;
=> hard reject.

Implement:
- `MapTopology`
- mobility domain
- connected components
- `EngagementFeasibility`
- reachable firing region
- `no-map-influence` rejection
- role deficit
- counter need
- objective fit
- timing/time-to-value
- congestion penalty
- same-match utilization feedback

Không hard-ban ground unit chỉ vì boss naval:
- ground unit vẫn hợp lệ nếu bắn từ bờ được;
- hoặc có land objective/support role.

## Traffic / stuck
Không chờ 10–12 s mới bắt đầu xử lý.

Implement staged anti-stuck:

- 1.5 s → soft avoidance
- 3 s → local replan
- 5 s → yield / right-of-way
- 8 s → corridor replan
- 12 s → emergency fallback

Thêm:
- deterministic passing side
- TrafficCoordinator
- choke reservation
- queue
- shared squad route
- predictive congestion
- wait-for/deadlock detection
- wreck nav invalidation
- spawn clear zone
- boss corridor

Không teleport trong normal recovery.

## Squad / army management
Implement:
- squad lifecycle
- 3–9 normal squad size
- merge understrength squads
- split oversized/choke-incompatible squads
- reinforcement rendezvous
- stable formation slots
- role-based formation
- reserve 15–25%
- shared corridor/path
- pursuit leash
- staging area
- synchronized attack package

---

# 3. GIỮ ARCHITECTURE 3 LỚP

Giữ separation:

```text
Commander
    → WHAT / WHERE

Squad
    → HOW AS GROUP

Tactical
    → LOCAL TARGET / POSITION

Steering / Traffic
    → SAFE VELOCITY / COLLISION
```

Không để:
- Commander micro steering;
- Tactical đổi strategic objective;
- Steering chọn target;
- target selector steer boss hull.

---

# 4. HARD FILTER TRƯỚC SCORE

Rule chung:

> lựa chọn không khả thi phải bị loại trước khi chấm điểm.

Áp cho:
- procurement;
- target selection;
- firing position;
- squad assignment;
- flank route;
- support mission.

Ví dụ:

```text
if no reachable deployment
OR no objective reach
OR no enemy reach
OR no reachable firing position
AND no strategic utility
=> reject
```

Không cho score cao cứu một option bất khả thi.

---

# 5. ADVANCED BEHAVIOR — IMPLEMENT THEO FILE

File V2 có full details.

Các behavior mới ưu tiên implement:

## Strategic / squad intelligence
- Tactical Frontline Model
- Tactical Confidence, nhưng KHÔNG morale
- temporal influence memory
- recent death danger memory
- route diversity
- unknown-risk reasoning
- scout-before-commit
- probe-and-exploit
- conditional feint
- fix-and-flank
- synchronized ETA attacks
- staging areas
- AttackPackage
- reserve release
- economy of force
- objective sunk-cost reset
- counterattack windows

## Coordination
- PlannedActionBoard
- planned damage reservation
- repair reservation
- AA coverage reservation
- smoke deconfliction
- target handoff
- weapon suitability handoff
- multi-weapon platform director

## Fire support
- fire mission scheduler
- counterbattery from observed fire only
- shoot-and-scoot
- artillery parking/reservations
- artillery prep synchronized with attack

## Air
- predictive interception
- CAP patrol zone
- air risk routing
- SEAD package
- strike ingress/egress
- bomber package
- air target handoff

## Boss
- boss target director
- weakpoint utility
- escort sectors
- escort threat handoff
- boss telegraph reaction
- escape-sector reservation
- active-DPS bearing
- fire cadence director
- pressure pacing

## Planning
- short-horizon combat forecast
- shallow counterfactual plan scoring
- attack abort on invalid dependency
- plan validity hash/version
- same-match adaptation
- anti-repetition penalty

---

# 6. KHÔNG IMPLEMENT CÁC BEHAVIOR BỊ LOẠI

Không thêm:

- morale;
- panic;
- retreat-by-health;
- omniscient counter-building;
- perfect hidden artillery origin;
- deep RL runtime controller;
- deep MCTS mỗi tick;
- persistent learning cross-match;
- random feint không có tactical utility;
- teleport anti-stuck như normal behavior.

---

# 7. FOG / INTEL FAIRNESS

AI phải respect fog/intel.

Được phép biết:
- game rules;
- own unit data;
- known map topology;
- boss public phase rules;
- visible telegraphs.

Không được biết:
- hidden current enemy position;
- hidden future random result;
- artillery exact location nếu chưa quan sát đủ;
- hidden player redeploy chỉ để đánh giá feint.

Threat memory phải decay từ observed intel.

---

# 8. TICK / PERFORMANCE

Dùng staggered frequencies theo spec.

Target baseline:

```text
steering ~10 Hz
tactical ~4 Hz
squad ~2 Hz
commander ~1 Hz
procurement ~0.5 Hz
```

Không bắt buộc tên/tick chính xác nếu architecture khác, nhưng phải giữ nguyên nguyên tắc:

- steering nhanh;
- tactical vừa;
- strategic chậm;
- expensive planning cached/staggered.

Combat forecast:
- shallow;
- cached;
- chỉ 2–4 candidate plans;
- không full projectile simulation.

Phải benchmark:
- 32v32
- 48v48
- boss + escorts + army
- multiple wrecks/chokes
- multiple simultaneous squads

---

# 9. DECISION LOG / DEBUG

Mở rộng DecisionLog.

Procurement phải log cả:

```text
BUY ...
```

và:

```text
REJECT ... reason=no-map-influence
```

Movement debug cần:
- desired velocity
- safe velocity
- blocker
- jam stage
- traffic priority
- route/corridor ID
- formation slot

Naval boss debug:
- lane
- route progress
- desired heading
- actual heading
- turn radius
- broadside candidate
- target
- hull reason
- mount targets
- CPA threat

Squad debug:
- task
- state
- action
- cohesion
- combat power
- enemy power
- formation
- reserve/attack-package state

---

# 10. DETERMINISM

Không dùng random nondeterministic cho:
- passing side
- tie-break
- action staggering
- route choice tie.

Dùng:
- stable ID;
- stable hash;
- deterministic iteration order.

Cosmetic stagger 150–400 ms có thể dùng hash deterministic.

---

# 11. TESTS BẮT BUỘC

Phải thêm automated/regression tests cho ít nhất:

## Procurement
- naval boss unreachable by MBT => reject
- coastal gun can reach ship => eligible
- secondary land objective => ground unit can still be eligible
- same-match low utilization reduces future purchase score

## Naval
- target changes side => turret turns, hull does not flip
- target behind => no reverse
- minimum turn radius respected
- collision predicted before overlap
- broadside stays route-constrained

## Traffic
- 20 vehicles same objective
- two squads opposite one gate
- heavy + scout right-of-way
- wreck blocking choke
- spawn exit congestion
- deadlock cycle

## Squad
- merge
- split
- rally/rendezvous
- reserve
- formation through choke
- synchronized main/flank ETA

## Targeting
- unreachable target rejected
- mount arc
- minimum range
- target stickiness
- anti-overkill
- handoff by weapon suitability

## Advanced
- death-memory avoids immediate repeated blind push
- scout-before-commit
- fix-and-flank
- counterbattery confidence
- shoot-and-scoot
- pursuit leash
- objective deadline
- counterattack opportunity
- boss telegraph escape sectors

---

# 12. QUALITY GATES

Do not consider task complete if:

```text
naval boss reverse event > 0
```

hoặc AI mua:

```text
MapInfluence == 0
```

trừ scripted explicit exception.

Target quality goals:

```text
SevereUnstuck <= 1 / 10 unit-minutes
```

trên normal open map.

Không để:
- squad action churn vượt warning liên tục;
- target switch spam;
- same move order reissued every tick.

---

# 13. PRESERVE CURRENT GOOD SYSTEMS

Không làm mất:
- threat/intel grid
- tactic switching
- mode profiles
- commander profiles
- squad commit windows
- tower modes
- artillery standoff
- firing spot booking
- aircraft resupply
- boss phase data
- escort roles
- target masks
- current difficulty framework
- current DecisionLog reasons

Integrate, không thay trắng.

---

# 14. SOURCE OF TRUTH / GENERATED FILES

Sửa canonical source/code trước.

Sau đó regenerate/update nếu relevant:

- `09_ai.xlsx`
- `09_ai.md`
- `04_che_do_kinh_te_ai.xlsx`
- `04_che_do_kinh_te_ai.md`
- `02_boss.xlsx`
- `02_boss.md`
- `06_ban_do.xlsx`
- `06_ban_do.md`
- `00_index.xlsx`
- `README.md`
- `CHANGES.md`
- AI JSON/CSV exports
- schemas
- agent-readable AI docs
- tunables documentation
- test reports

Không manually patch generated file nếu generator tồn tại.

---

# 15. EQUIPMENT CORRECTION — OVERRIDE PROMPT CŨ

Nếu task/codebase hiện đang đồng thời áp prompt cân bằng trang bị trước đó, dùng các correction dưới đây thay thế phần tương ứng.

## 15.1. Global BuildCap

KEEP:

> BuildCap tính trên tổng tất cả nguồn.

Tức:

```text
base gear
+ substats
+ traits
+ modules
+ sets
+ commander/other valid modifiers
→ sum
→ final cap
```

Không cho `VeteranCrew` bypass cap.

Nếu build đã chạm cap:
- phần bonus cùng stat của VeteranCrew bị wasted.

Nếu UI/tooltips hỗ trợ:
- hiển thị effective bonus;
- hiển thị lượng bị overcap/wasted.

---

# 16. VeteranCrew

KEEP module values hiện tại:

- Epic `0.08`
- Legendary `0.12`

Không đổi chỉ vì có cap.

Không bypass cap.

---

# 17. hair_trigger — TARGET EFFECTIVE VALUE

Override giá trị trước.

Final effective FireRate target:

- Common/Uncommon: theo availability hiện tại
- Rare: **8%**
- Epic: **10%**
- Legendary: **11%**

Mục tiêu:
- Legendary còn đúng 4% headroom tới FireRate cap 15%;
- Legendary FireRate substat +4% có thể chạm cap mà không bị phí.

Giữ penalty Spread theo version cân bằng gần nhất trừ khi cần minor mapping để khớp rarity.

Quan trọng:
- chỉnh RAW values theo formula runtime thực tế để **effective output** đúng bảng trên;
- không chỉ sửa spreadsheet display.

---

# 18. overtuned_engine — TARGET EFFECTIVE VALUE

Final effective Speed:

- Rare: **8%**
- Epic: **10%**
- Legendary: **12%**

Speed cap vẫn 15%.

Legendary phải còn ~3% headroom cho substat/set/other valid source.

Giữ Health penalty theo version gần nhất:
- Rare `-3%`
- Epic `-4%`
- Legendary `-5%`

hoặc equivalent raw values nếu runtime scaling làm effective khác.

---

# 19. monolith_plate

Audit runtime effect trước.

Nó hiện dùng special mechanism:
- `implicitStat = Count`
- `MainScale = 1.8`
- `NoSubs = true`

Không đoán sửa `Count`.

Final target:

> Legendary effective Health bonus = **24%**

Không để:
- `25.2% → clamp 25%`

Mục tiêu:
- tránh vượt cap vì scaling/rounding;
- còn 1% headroom cho nguồn global khác;
- `NoSubs=true` vẫn giữ.

Nếu formula không trực tiếp expose Health:
- chỉnh đúng raw/MainScale/derived input tối thiểu để resulting effective Health = 24%;
- report formula cụ thể.

---

# 20. ammo_handling — OVERRIDE QUAN TRỌNG

Prompt trước nói `MainScale=1.25` nhưng runtime thực tế cho MagazineReload chỉ khoảng:

`3.75% → 17.5%`

Vì vậy:

> KHÔNG khóa `MainScale=1.25`.

Final target effective values mới:

| Rarity | Magazine | Effective MagazineReload |
|---|---:|---:|
| Common | 8% | 10% |
| Uncommon | 12% | 15% |
| Rare | 16% | 20% |
| Epic | 20% | 25% |
| Legendary | 24% | 30% |

MagazineReload cap vẫn:
`30%`

Magazine cap vẫn:
`40%`

Coding task:
1. xác định exact runtime formula của `MainScale`/implicit stat;
2. giải ngược raw values/scale;
3. làm cho **effective runtime output** đúng bảng trên;
4. test actual resulting stat sau formula;
5. update docs/tooltips theo effective value.

Không chấp nhận:
- spreadsheet ghi 30% nhưng runtime chỉ ra 17.5%.

Effective runtime result là nguồn kiểm tra cuối.

---

# 21. EQUIPMENT TESTS BỔ SUNG

Test:

## VeteranCrew
- build chưa cap → bonus có tác dụng
- build đã cap → effective stat không vượt cap
- overcap amount được report nếu UI/debug hỗ trợ

## hair_trigger
- Rare effective = 8%
- Epic = 10%
- Legendary = 11%
- Legendary + FireRate substat 4% = exactly 15% effective

## overtuned_engine
- 8/10/12% effective
- không tự chạm Speed cap

## monolith_plate
- Legendary effective Health = 24%
- không 25.2%
- không clamp artifact

## ammo_handling
Actual runtime effective:
- Magazine = 8/12/16/20/24%
- MagazineReload = 10/15/20/25/30%

Test giá trị cuối sau toàn pipeline, không chỉ raw catalog.

---

# 22. IMPLEMENTATION PRIORITY

Nếu task quá lớn, thứ tự triển khai bắt buộc:

## Priority 0 — correctness bugs
1. no-map-influence procurement filter
2. naval boss no reverse
3. hull/turret decoupling
4. staged anti-stuck
5. target feasibility
6. global BuildCap corrections
7. ammo_handling actual effective values

## Priority 1 — traffic / squad
1. TrafficCoordinator
2. shared paths
3. choke reservation
4. merge/split
5. reinforcement rendezvous
6. reserve

## Priority 2 — intelligent coordination
1. frontline
2. route diversity
3. synchronized attack
4. AttackPackage
5. PlannedActionBoard
6. counterbattery
7. pursuit discipline

## Priority 3 — advanced intelligence
1. combat forecast
2. probe/feint
3. shallow plan comparison
4. same-match utilization adaptation
5. advanced air/SEAD
6. advanced boss coordination

Không bỏ Priority 0 để làm behavior đẹp trước.

---

# 23. FINAL REPORT FORMAT

Cuối task trả report:

## A. AI implementation
1. files modified;
2. new classes/services;
3. old behavior → new behavior;
4. new tunables;
5. behaviors fully implemented;
6. behaviors scaffolded/not implemented + reason;
7. procurement tests;
8. naval tests;
9. traffic tests;
10. squad tests;
11. targeting tests;
12. advanced behavior tests;
13. performance results;
14. severe-unstuck count;
15. representative DecisionLog output.

## B. Equipment correction
16. VeteranCrew cap behavior;
17. hair_trigger old → new effective;
18. overtuned_engine old → new effective;
19. monolith_plate effective Health result;
20. ammo_handling raw formula + resulting effective table;
21. all cap tests.

## C. Generated outputs
22. docs regenerated;
23. exports regenerated;
24. grep/scan for stale old values;
25. any remaining warnings.

---

# 24. FINAL NON-NEGOTIABLE CONFIRMATIONS

Report phải xác nhận rõ:

```text
naval boss reverse = disabled

boss hull target != turret target

no-map-influence units are rejected before purchase scoring

anti-stuck begins before 10–12 s

global BuildCap applies to the sum of all valid gear sources

VeteranCrew does not bypass BuildCap

hair_trigger Legendary effective FireRate = 11%

overtuned_engine Legendary effective Speed = 12%

monolith_plate Legendary effective Health = 24%

ammo_handling effective MagazineReload =
10 / 15 / 20 / 25 / 30%

boss armour unchanged

boss HP unchanged

no retreat-by-health

no morale system

AI remains fog-respecting
```

Dùng file V2 đính kèm làm spec chi tiết đầy đủ cho tất cả behavior còn lại.

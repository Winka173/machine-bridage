# 10_model_tai_san — Model và tài sản

Bộ xuất dữ liệu Machine Brigade, commit 5d195554, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Model GLB (nút, vật liệu, mesh, tam giác, Part / Mount / Muzzle), chuẩn kiểm model, kích thước thật tham chiếu, ảnh thẻ, địa phương hóa Việt / Anh, giấy phép tài sản

Mục trong file này: 19. Hình ảnh; 21. Model.

## 19. Hình ảnh

Trạng thái: Một phần — chờ prompt xuat_luot6 (sheet Anh_chup)

Nguồn dữ liệu: 10_model_tai_san/Anh_the; 10_model_tai_san/Anh_chup. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §19. Hình ảnh, §20. Thư viện hình ảnh.

#### 19. Hình ảnh

![Mô hình đạn: tên lửa chống tăng và phòng không vác vai.](../images/10_model_tai_san/r6_munitions_1.png)

*Hình: Mô hình đạn: tên lửa chống tăng và phòng không vác vai. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Tên lửa không đối không, phòng không, không đối đất.](../images/10_model_tai_san/r6_munitions_2.png)

*Hình: Tên lửa không đối không, phòng không, không đối đất. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Rocket.](../images/10_model_tai_san/r6_munitions_3.png)

*Hình: Rocket. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Bom và drone.](../images/10_model_tai_san/r6_munitions_4.png)

*Hình: Bom và drone. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Đạn pháo, đạn cối, đạn xuyên, đạn railgun.](../images/10_model_tai_san/r6_munitions_5.png)

*Hình: Đạn pháo, đạn cối, đạn xuyên, đạn railgun. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre.](../images/10_model_tai_san/r6_new_models.png)

*Hình: Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen.](../images/10_model_tai_san/r6_flame.png)

*Hình: Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Railgun: nạp năng lượng, tia sáng lưu lại.](../images/10_model_tai_san/r6_railgun.png)

*Hình: Railgun: nạp năng lượng, tia sáng lưu lại. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích.](../images/10_model_tai_san/r6_boss_death.png)

*Hình: Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra.](../images/10_model_tai_san/r6_muzzle_audit.png)

*Hình: Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

#### 20. Thư viện hình ảnh

Ảnh render từ mô hình 3D của game (cùng ảnh dùng cho thẻ), ảnh chụp trong trận, các bảng hiệu ứng và bản đồ nhiệt.

![Docs/doc-images/r6/supports.png](../images/10_model_tai_san/r6_supports.png)

*Hình: Docs/doc-images/r6/supports.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/battle1.png](../images/10_model_tai_san/shots_battle1.png)

*Hình: Docs/doc-images/shots/battle1.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/battle2.png](../images/10_model_tai_san/shots_battle2.png)

*Hình: Docs/doc-images/shots/battle2.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/boss.png](../images/10_model_tai_san/shots_boss.png)

*Hình: Docs/doc-images/shots/boss.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/defend.png](../images/10_model_tai_san/shots_defend.png)

*Hình: Docs/doc-images/shots/defend.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/edge.png](../images/10_model_tai_san/shots_edge.png)

*Hình: Docs/doc-images/shots/edge.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/hd.png](../images/10_model_tai_san/shots_hd.png)

*Hình: Docs/doc-images/shots/hd.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/hunt.png](../images/10_model_tai_san/shots_hunt.png)

*Hình: Docs/doc-images/shots/hunt.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/siege.png](../images/10_model_tai_san/shots_siege.png)

*Hình: Docs/doc-images/shots/siege.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 10_model_tai_san/Anh_the — Ảnh thẻ (241 dòng, 7 cột)

| id | model | hash | kind | source |
|---|---|---|---|---|
| aa_57mm_vehicle | aa_57mm_vehicle | v2:bee71d1a6cc830be5788b6e1f0413408c5def34f | vehicle | Models/aa_57mm_vehicle |
| aa_gun_tower | aa_gun_tower | v2:1025a648efa86c1a0f59d2dc0ae2a29a4aad7e0a | tower | Models/aa_gun_tower |
| aa_gun_vehicle | aa_gun_vehicle | v2:eabe9ddd7406a58560f750dfcff157f149cc737f | vehicle | Models/aa_gun_vehicle |
| aa_turret | aa_turret | v2:8e6d00e266ceabf8144865cadf4698469e56c52d | tower | Models/aa_turret |
| aa_turret.flak | aa_turret_a | v2:88bfa5196b539f88f3b14802e198760b04a3ef74 | tower | Models/aa_turret_a |
| aa_turret.sam | aa_turret_b | v2:7e53712ff36be3f744fd6f2b6aada66cf57615d1 | tower | Models/aa_turret_b |
| aa_vehicle | aa_vehicle | v2:1289d1f47da30d893895ed85aecd655e3cfd9e3a | vehicle | Models/aa_vehicle_hd |
| aerial_tanker | aerial_tanker | v2:ec43c999483b9d865ae4076d882d2a2b72d2f367 | vehicle | Models/aerial_tanker |
| airborne_light_tank | airborne_light_tank | v2:1a7e46957def37e7b3fb34242a576a3bcd2145c2 | vehicle | Models/airborne_light_tank |
| airborne_vehicle | airborne_vehicle | v2:ea40410f88ec13e047b1f3f76f4daab0374f2f8e | vehicle | Models/airborne_vehicle |
| airfield | helipad | v2:8632041388de13a52d29dd466a586f52537c2c7f | tower | Models/helipad |
| airfield.hangar | helipad_a | v2:50d7f6fdbd14fc77ec64f4f7af9c3edcec4ffaef | tower | Models/helipad_a |
| airfield.service | helipad_b | v2:2d958e133edb19b63ebf5fdf1b49ead6a07c2014 | tower | Models/helipad_b |
| ammo_carrier | ammo_carrier | v2:c50fe4b2c580acfcb7a71103f48365d7b686c387 | vehicle | Models/ammo_carrier |
| ammo_depot | ammo_dump | v2:9d916519cf62f2a2b36cafdfde3845217891da6d | tower | Models/ammo_dump |

*15 / 241 dòng đầu: xem sheet 10_model_tai_san/Anh_the.*

Sheet: 10_model_tai_san/Anh_chup — Ảnh chụp (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot6 | lượt 6 (Markdown, PDF, ảnh): Docs/doc-images |

## 21. Model

Trạng thái: Một phần — chờ prompt xuat_luot6; cần đọc mã (NEED_CODE_CHECK) (sheet Model, Xem_truoc)

Nguồn dữ liệu: 10_model_tai_san/Model; 10_model_tai_san/Model_tieu_chuan; 10_model_tai_san/Model_kiem_chuan; 10_model_tai_san/Kich_thuoc_that; 10_model_tai_san/Giay_phep_tai_san; 10_model_tai_san/Xem_truoc. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10h. Prompt 27; Docs/models/MODEL_STANDARD.md.

Prompt 27 thay các model mượn tạm (stand-in) bằng model riêng và đặt một mức chất lượng chung cho mọi model. Quy trình: **STEP0_AUDIT** kiểm kê mọi model và thẻ; **BASELINE** chạy bộ kiểm tra GLB (`Tools/assets/glb_check.py`: tỉ lệ so với `modelSize`, tam giác diện tích 0, màu đỉnh COLOR_0, nút bộ phận boss) và ghi mốc; **EXPERIMENT_1** thử bộ dựng V2 trên bốn model (xe tăng chủ lực, máy bay tiêm kích, silver_bug, trực thăng tấn công) và được chủ dự án duyệt; **BUDGETS** đặt trần số tam giác, renderer và bộ phận động theo loại; **art-bible** ghi luật tạo hình, bảng màu và công thức V2. Mỗi model một commit: dựng lại, kiểm tĩnh, render thẻ, xem trước trong Unity, chấp nhận mốc mới kèm lý do. Không chạy test, mô phỏng hay đo hiệu năng cho đến khi chủ dự án cho phép.

**Đợt 1** (42 model có tên riêng; đợt 1a: 2, đợt 1b: 8, đợt 1c: 32): Ixion và Gungnir, tám boss lô D (Kraken, Monster, Garuda, Hyperion, Stymphalos, Nyx, Cerberus, Hydra) và 32 đơn vị lô B; mọi lớp màu sơn tạm đã bỏ, không số liệu nào đổi. **Đợt 2** sửa 18 model validator đánh dấu (sai tỉ lệ, tam giác diện tích 0, thiếu nút bộ phận boss, vượt trần ngân sách) theo nguyên tắc thay đổi nhỏ nhất.

#### Báo cáo `Docs/models/MODEL_STANDARD.md`

##### Model standard (fix pass 8)

Source: Docs/prompts/fix_full_vi.txt "Lượt 8" item 1 (owner, 2026-10-02); DECISIONS "Sửa lỗi tổng hợp L8 prep".
Where this file and Docs/models/BUDGETS.md disagree, this file decides how a model is **scored**. L9 item 7 is
`python Tools/balance/fix_validate.py 7` (budget information only, the parts and LOD1 against the pass 8 scores); the
prompt 27 caps in `Tools/assets/glb_check.py` stay an error gate for draw calls, while their triangle and vertex caps
only warn (the owner's rule of 02/10).
Checked statically by `python Tools/models/scan_prep.py` (Docs/models/scan/static_scores.csv) and visually on the
sheets that `MachineBrigade.Editor.ModelScan.RenderBatch` draws (Docs/models/scan/README.md).

###### 1. Triangle budgets

LOD0 = the normal GLB (every platform loads it; phones only load this one). The `_hd` twin (the PC High tiers) may
carry up to 2.4 x the class maximum (BUDGETS.md's median `_hd` / normal ratio). The scorer reports it but does not
grade on it.

**Owner rule (02/10): a model over its budget is kept.** Budgets are a guide, not a cap; the scorer reports
over-budget as information only and never grades a model down or cuts it for that (DECISIONS "Owner: over-budget
models are fine").

| class (scorer) | what | LOD0 triangles |
|---|---|---|
| light | wheeled and other light vehicles (trucks, cars, APCs on wheels) | 3,000-5,000 |
| heavy | tanks, tracked and heavy vehicles (tracked, or class Tank / Heavy) | 4,000-7,000 |
| jet, helicopter | aircraft and helicopters | 4,000-7,000 |
| air_other | drop pods, parachute loads | at most 7,000 |
| ship | ships (`naval`) | 8,000-15,000 |
| boss | bosses (every frame) | 10,000-20,000 |
| tower | towers (defs with `fort`, their branch `_a` / `_b` models) | 2,000-4,000 |
| structure, hq | other static structures; the HQs (`headquarters`, `command_hq`) | 2,000-6,000 |
| obstacle | walls, dragon's teeth, minefields (`wall`, `obstacle`, `passable`) | at most 6,000 |

- Below the minimum is a fault too (too little detail to read), not only above the maximum.
- **LOD1 ~50 %** of LOD0: the game builds it at run time (`ModelLibrary.Lod`, `MeshSimplifier`, half a pixel of

  error at the 128 px switch). ModelScan writes `triangles0` / `triangles1` per model; accepted band 35-65 %.
- **LOD2 ~20 %**: the impostor (`ImpostorAtlas`, below 24 px) takes this level for every vehicle. A model drawn large

  enough that its impostor is never used (bosses, ships) needs no mesh LOD2; if one is ever added, about 20 % of LOD0.

###### 2. Minimum parts per class

A part is a named node. A role is met by a `Part_<role>` node **or** by the kit's merged-material node of that
part (the names in the table). Note: `Part_*` nodes are runtime parts (damage, boss parts): ModelLibrary keeps each as
a mesh of its own, so one draw and one shadow draw each. Do **not** add a `Part_*` node per wheel or per blade to pass
this list; "every road wheel", "every blade", "every barrel" are geometry rules, checked on the sheet (each wheel its
own disc with a hub, each blade its own blade). Roles marked (w) only apply when the def is armed; (t) only with a
turret (`turretTurnRate`).

| class | roles (accepted node names, start of the name) |
|---|---|
| tracked | hull (Hull, Body, Chassis); turret (t) (Turret, Casemate); mantlet (t) (Mantlet, Gun_mantlet, Elevation, Cradle); barrels (w) (Main_cannon, Barrel, Gun, Tubes, Launcher, Pod, Missiles, Mount_*); every road wheel (Wheels, Roadwheels, Bogies); drive sprocket (Sprockets); idler (Idlers); tracks with links / tread (Tracks, Track_links, Treads); side skirts (Skirts, Skirt_edge); hatches (Hatch, Hatches, Cupola); sights (Sight, Periscope, Optics, Sensor); roof MG (w) (MG, Mount_mg, Rws, Hmg); smoke dischargers (Smoke, Smoke_launchers, Smoke_brackets); stowage (Stowage, Tarp, Crates, Jerrycans, Bins, Racks, Straps, Ammo_boxes, Bags) |
| wheeled | every wheel (Wheels, Tyres); axles (Axles, Undercarriage, Suspension, Hubs); cab (Cab, Cabin, Hull, Body); glass (Glass, Windows, Windscreen, Lit_windows, Canopy, Visors); lights (Lamps, Lights, Headlights, Tail_lamps, Light_rims); stowage (as above); weapon (w) |
| jet | fuselage; cockpit glass (Canopy, Cockpit, Glass); wings with the reference's sweep and taper (Wing, Part_wing); horizontal and vertical tail (Tail, Fins, Tailplane, Stabilator, Rudder); intakes (Intake, Intake_lips, Inlet); exhausts (Nozzle, Exhaust); pylons (Pylons, Hardpoints, Racks); stores on them (Missiles, Bombs, Pods, Rockets, Drop_tanks); flare dispensers (Flares, Mount_flare) |
| helicopter | fuselage; glass (Canopy, Glass, Windows); rotor hub (Rotor_hub, Rotor_grips, Hub); every blade (Rotor_blades, Blades); tail rotor (Tail_rotor); landing gear (Undercarriage, Skids, Gear, Tyres); stub wings (Wing, Stub_wing, Pylons); weapons (Gun, Gun_turret, Missiles, Pods, Rockets, Launchers) |
| ship | hull with bow flare (Hull); superstructure tiers (Superstructure, Bridge, Deckhouse, Tier, Island, Funnel); radar mast (Mast, Radar, Antenna); every turret and barrel (Turret, Gun_house, Main_cannon, Barrel); CIWS (CIWS, Phalanx, AK630, Gatling, Mount_ciws); boats (Boat, RHIB, Lifeboat, Davit); deck details (Deck, Rails, Bollards, Hatches, Vents, Winch, Anchor) |
| tower, structure, hq | base (Base, Plinth, Footing, Emplacement, Pad, Foundation, Slab, Block, Race); sandbags / walls (Sandbags, Hesco, Wall, Parapet, Barriers, Blast_bags, Revetment, Berm, Coping); roof (Roof, Roof_deck, Canopy, Cupola, Tower_deck, Deck, Turret, Dome, Shelter); antennas (Antenna, Mast, Aerial, Radar, Dish, Flag_pole); faction detail differs (Accord: practical, field-built - sandbags, timber, nets; Hegemon: prefabricated - cast concrete, modular panels) - visual check |
| boss | body (Hull, Fuselage, Body, Chassis, Deck, Envelope, Gondola); weapons; by frame: running gear (ground: Tracks, Wheels, Bogies, Legs, Rail_wheels), lift (air: Rotor, Wing, Envelope, Propeller, Engine), superstructure (naval); and every `parts[].node` of its def present |
| obstacle | none (budget and look only) |

###### 3. General rules

1. **Proportions within 10 %** of the real reference: width/length and height/length against
   `Docs/models/reference_dimensions.md` (data: `Tools/models/reference_real.json`). Absolute size is free (the game
   draws aircraft and ships smaller on purpose; the view fits the length to `modelSize`). Fictional designs
   (conf "inspiration") are not judged.
2. **No single-box turret or hull**: at least two stacked or angled volumes, sloped glacis / cheeks; large bevels on
   every big edge (the kit's chamfers), no 90-degree slab edge on a hull or turret read from 28 px per metre.
3. **Materials and detail colours separated**: hull paint, steel, rubber, glass, lamps, markings in their own
   materials (the kit's names), so the team colour and wear read.
4. **Mounts and muzzles**: a `Muzzle_<slot>` per barrel of every weapon (the weapon's `barrels`; a secondary on the
   main gun's slot shares its barrels); a `Mount_<slot>` per freely aimed (`aim: Free`) secondary; the main weapon on a
   `Turret` (or `Mount_<mainSlot>`) when the def turns a turret; `Mount_Flare` x 2 or more when the def has
   `flareCharges`; `Mount_APS` when it has `aps`. Bosses: as many `Muzzle_*` as `mountWeapons`, every part node.
5. **Readable silhouette at the normal camera distance**: the battle camera's default zoom (orthographic size 19 on
   a 1080 px screen = 28.4 px per metre, pitch 52). The ModelScan sheet shows exactly that; the type must be named from
   the left cell alone.

###### 4. Grades

- **Kém** (poor): triangles over 1.5 x the class maximum or under half the minimum; 4 or more required parts missing;

  the main weapon's muzzle missing; proportions more than 25 % off a high-confidence reference; or the visual pass
  finds the silhouette unreadable / a box model.
- **Cần sửa** (needs fixing): any other fault above (over or under budget, 1-3 parts, a secondary muzzle or mount,

  Mount_Flare / Mount_APS, boss part node, proportions 10-25 %, LOD1 outside 35-65 %), or a visual fault.
- **Tốt** (good): nothing found, statically and on the sheet.
- Final grade = the lower of the static and the visual grade, with one exception: a "missing part" that the sheet

  shows modelled inside a merged node (an idler inside `Wheels`, a mantlet inside `Turret_body`) is cleared by the
  visual pass, which says so in its reason (the static check only sees node names). Old vs new (models rebuilt in prompt 27): the lower
  scoring version loses; when the new one scores lower, restore the old GLB or rebuild it to pass.

###### 5. How the scorer assigns a class

Own def = the def whose id is the model, else the first def drawing it. HQ ids -> hq; `boss` -> boss; `naval` -> ship;
`flying` -> jet (`fixedWing`), helicopter (has a `Rotor*` node) or air_other; static or speed 0 -> obstacle (`wall`,
`obstacle`, `passable` or a wall / teeth / minefield id), tower (`fort` or `branchOf`; the `_a` / `_b` files) or
structure; otherwise tracked (Tracks / Sprockets nodes), wheeled (Tyres / Wheels nodes) or ground.

![ixion: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/ixion_before_after.png)

*Hình: ixion: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model ixion 27.02 × 13.03 × 10.372 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![ixion: ảnh quét trong Unity (ModelScan)](../images/10_model_tai_san/ixion_unity_scan.png)

*Hình: ixion: ảnh quét trong Unity (ModelScan). Đơn vị: m; ảnh không có lưới mét; model ixion 27.02 × 13.03 × 10.372 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![rocket_turret: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/rocket_turret_before_after.png)

*Hình: rocket_turret: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model rocket_turret 4.685 × 4.717 × 3.434 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![rocket_turret: ảnh quét trong Unity (ModelScan)](../images/10_model_tai_san/rocket_turret_unity_scan.png)

*Hình: rocket_turret: ảnh quét trong Unity (ModelScan). Đơn vị: m; ảnh không có lưới mét; model rocket_turret 4.685 × 4.717 × 3.434 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![zu23_technical: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/zu23_technical_before_after.png)

*Hình: zu23_technical: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model zu23_technical 4.582 × 1.61 × 1.64 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![zu23_technical: ảnh quét trong Unity (ModelScan)](../images/10_model_tai_san/zu23_technical_unity_scan.png)

*Hình: zu23_technical: ảnh quét trong Unity (ModelScan). Đơn vị: m; ảnh không có lưới mét; model zu23_technical 4.582 × 1.61 × 1.64 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 10_model_tai_san/Model — Model (518 dòng, 20 cột)

| id | loai | lop_ngan_sach | tam_giac | so_nut | so_part | so_mount | so_muzzle | co_mount_flare | co_mount_aps |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | ground | ground | 6028 | 38 | 0 | 0 | 2 | FALSE | FALSE |
| aa_gun_tower | structure | tower | 1724 | 12 | 0 | 0 | 2 | FALSE | FALSE |
| aa_gun_vehicle | ground | ground | 3556 | 26 | 0 | 0 | 2 | FALSE | FALSE |
| aa_turret | structure | tower | 6306 | 34 | 0 | 0 | 4 | FALSE | FALSE |
| aa_turret_a | structure | tower | 6670 | 33 | 0 | 0 | 5 | FALSE | FALSE |
| aa_turret_b | structure | tower | 2610 | 33 | 0 | 0 | 5 | FALSE | FALSE |
| aa_vehicle | ground | ground | 4964 | 36 | 0 | 0 | 4 | FALSE | FALSE |
| aa_vehicle_hd | ground | ground | 12556 | 42 | 0 | 0 | 4 | FALSE | FALSE |
| adobe_house | prop | prop | 1660 | 19 | 0 | 0 | 0 | FALSE | FALSE |
| adobe_large | prop | prop | 3946 | 28 | 0 | 0 | 0 | FALSE | FALSE |
| aerial_tanker | air | jet | 4164 | 33 | 1 | 6 | 1 | TRUE | FALSE |
| aim9 | unlisted |  | 238 | 10 | 0 | 0 | 0 | FALSE | FALSE |
| aim120 | munition | munition | 222 | 8 | 0 | 0 | 0 | FALSE | FALSE |
| airborne_light_tank | ground | ground | 5550 | 34 | 0 | 0 | 3 | FALSE | FALSE |
| airborne_light_tank_chute | air | jet | 3514 | 23 | 0 | 0 | 3 | FALSE | FALSE |

*15 / 518 dòng đầu: xem sheet 10_model_tai_san/Model; in 10 / 20 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Model_tieu_chuan — Model: tiêu chuẩn (14 dòng, 13 cột)

| id | lop | bac | moving_parts_muc | moving_parts_tran | renderers_muc | renderers_tran | triangles_muc | triangles_tran | vertices_muc |
|---|---|---|---|---|---|---|---|---|---|
| boss_l/normal | boss_l | normal | 41 | 52 | 240 | 299 | 56000 | 70000 | 72000 |
| boss_m/normal | boss_m | normal | 25 | 31 | 178 | 222 | 44000 | 55000 | 56000 |
| boss_s/normal | boss_s | normal | 22 | 28 | 130 | 162 | 36000 | 45000 | 43000 |
| ground/hd | ground | hd | 8 | 10 | 83 | 103 | 18800 | 23300 | 27300 |
| ground/normal | ground | normal | 8 | 10 | 61 | 76 | 7800 | 9700 | 10100 |
| helicopter/hd | helicopter | hd | 5 | 6 | 61 | 76 | 15900 | 20000 | 22500 |
| helicopter/normal | helicopter | normal | 5 | 6 | 45 | 56 | 6600 | 8300 | 8300 |
| jet/hd | jet | hd | 6 | 7 | 49 | 60 | 12300 | 15400 | 19200 |
| jet/normal | jet | normal | 6 | 7 | 36 | 44 | 5100 | 6400 | 7100 |
| munition/normal | munition | normal | 2 | 3 | 14 | 17 | 500 | 1600 | 600 |
| prop/normal | prop | normal | 2 | 3 | 46 | 58 | 6900 | 8600 | 9900 |
| scenery/normal | scenery | normal | 2 | 3 | 12 | 14 | 3700 | 4600 | 9700 |
| structure/normal | structure | normal | 2 | 3 | 39 | 48 | 7900 | 9900 | 9800 |
| tower/normal | tower | normal | 8 | 9 | 144 | 180 | 14700 | 18400 | 20100 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Model_kiem_chuan — Model: kiểm chuẩn (baseline) (518 dòng, 72 cột)

| id | model | animations | bounds_max_x_m | bounds_max_y_m | bounds_max_z_m | bounds_min_x_m | bounds_min_y_m | bounds_min_z_m | budget_class |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | aa_57mm_vehicle | 0 | 1.295 | 2.63 | 2.75 | -1.295 | -0.0376 | -2.9901 | ground |
| aa_gun_tower | aa_gun_tower | 0 | 2.85 | 3.1969 | 3.0366 | -2.85 | -0.01 | -2.85 | tower |
| aa_gun_vehicle | aa_gun_vehicle | 0 | 1.31 | 2.945 | 2.9257 | -1.31 | -0.0386 | -2.715 | ground |
| aa_turret | aa_turret | 0 | 2.25 | 3.1849 | 3.188 | -2.25 | -0.02 | -2.25 | tower |
| aa_turret_a | aa_turret_a | 0 | 2.25 | 3.2617 | 3.188 | -2.25 | -0.02 | -2.25 | tower |
| aa_turret_b | aa_turret_b | 0 | 2.25 | 2.7398 | 2.25 | -2.25 | -0.02 | -2.25 | tower |
| aa_vehicle | aa_vehicle | 0 | 1.54 | 2.8703 | 3.54 | -1.54 | -0.01 | -2.945 | ground |
| aa_vehicle_hd | aa_vehicle_hd | 0 | 1.545 | 2.8703 | 3.54 | -1.545 | -0.01 | -2.945 | ground |
| adobe_house | adobe_house | 0 | 3.53 | 5.0 | 3.6937 | -3.74 | -0.04 | -3.54 | prop |
| adobe_large | adobe_large | 0 | 6.04 | 9.76 | 4.785 | -5.73 | 0.0 | -4.54 | prop |
| aerial_tanker | aerial_tanker | 0 | 11.31 | 5.7 | 9.9 | -11.31 | 0.02 | -10.0754 | jet |
| aim9 | aim9 | 0 | 0.1434 | 0.1434 | 1.1 | -0.1434 | -0.1434 | -1.1 |  |
| aim120 | aim120 | 0 | 0.1177 | 0.1177 | 1.3 | -0.1177 | -0.1177 | -1.3 | munition |
| airborne_light_tank | airborne_light_tank | 0 | 1.31 | 1.8 | 3.25 | -1.31 | -0.047 | -3.2001 | ground |
| airborne_light_tank_chute | airborne_light_tank_chute | 0 | 4.5018 | 11.0 | 4.5 | -4.5018 | -0.047 | -4.5 | jet |

*15 / 518 dòng đầu: xem sheet 10_model_tai_san/Model_kiem_chuan; in 10 / 72 cột; 52 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Kich_thuoc_that — Kích thước thật tham chiếu (105 dòng, 11 cột)

| id | conf | ref | size_cao_m | size_dai_m | size_rong_m | source |
|---|---|---|---|---|---|---|
| aa_vehicle | approx | Flakpanzer Gepard 1A2 | 3.29 | 7.68 | 3.71 | Wikipedia 'Flakpanzer Gepard' (radar stowed) |
| aerial_tanker | approx | B-52H (same frame as the heavy bomber) | 12.4 | 48.5 | 56.4 | Wikipedia 'Boeing B-52 Stratofortress' |
| ammo_carrier | approx | M977 / M985 HEMTT | 2.84 | 10.17 | 2.44 | Wikipedia 'Heavy Expanded Mobility Tactical Truck' |
| amphib_light_vehicle | approx | M2A3 Bradley (same frame as the IFV) | 2.98 | 6.55 | 3.6 | Wikipedia 'M2 Bradley' |
| armored_bulldozer | approx | Caterpillar D9R (IDF kit) | 4.0 | 8.1 | 4.3 | Caterpillar D9R specifications (blade and ripper) |
| armored_car | approx | Pandur I 6x6 | 1.82 | 5.7 | 2.5 | Wikipedia 'Steyr Pandur' (height to the hull roof) |
| armored_train | inspiration | BP-35 armoured train |  |  |  | a train set |
| artillery | high | M109A6 Paladin | 3.24 | 9.12 | 3.15 | Wikipedia 'M109 howitzer' |
| attack_helicopter | approx | AH-64D Apache Longbow | 3.87 | 17.73 | 14.63 | Wikipedia 'Boeing AH-64 Apache' (length with rotors; height… |
| attack_jet | high | Su-25 Frogfoot | 4.8 | 15.53 | 14.36 | Wikipedia 'Sukhoi Su-25' |
| ballistic_launcher | approx | 9P78-1 Iskander-M TEL (MZKT-7930) |  | 13.07 | 3.07 | Wikipedia '9K720 Iskander' (height not reliable) |
| behemoth | inspiration | Object 279 (four tracks, flat hull), a giant | 2.47 | 10.24 | 3.4 | Wikipedia 'Object 279' (hull 7.77 m); the boss is a fiction… |
| behemoth_inferno | inspiration | Object 279 with a TOS-1A pack |  |  |  | fictional |
| behemoth_tempest | inspiration | Object 279 with a railgun |  |  |  | fictional |
| bmpt | none | BMPT Terminator |  |  |  | no reliable overall figure found yet |

*15 / 105 dòng đầu: xem sheet 10_model_tai_san/Kich_thuoc_that.*

Sheet: 10_model_tai_san/Giay_phep_tai_san — Giấy phép tài sản (5 dòng, 7 cột)

| id | tep | tai_san | giay_phep | so_dong |
|---|---|---|---|---|
| OFL-Barlow | OFL-Barlow.txt | Barlow | SIL Open Font License | 75 |
| OFL-BarlowCondensed | OFL-BarlowCondensed.txt | BarlowCondensed | SIL Open Font License | 75 |
| OFL-BeVietnamPro | OFL-BeVietnamPro.txt | BeVietnamPro | SIL Open Font License | 75 |
| OFL-Inter | OFL-Inter.txt | Inter | SIL Open Font License | 75 |
| OFL-JetBrainsMono | OFL-JetBrainsMono.txt | JetBrainsMono | SIL Open Font License | 74 |

Sheet: 10_model_tai_san/Xem_truoc — Màn xem trước (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | Assets/MachineBrigade/Scripts/Editor/ModelPreview.cs và pre… |

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Anh_the_chung

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Anh_the_chung.

Sheet: 10_model_tai_san/Anh_the_chung — Ảnh thẻ: cài đặt render (3 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|
| camera | camera |  | orthographic 3/4, pitch 26, yaw -142 (the front to the righ… |
| size | size | 512 |  |
| version | version | 2 |  |

### Dia_phuong_hoa

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Dia_phuong_hoa.

Sheet: 10_model_tai_san/Dia_phuong_hoa — Địa phương hóa (6535 dòng, 9 cột)

| id | bang | tien_to | en | vi | so_ky_tu_en | so_ky_tu_vi |
|---|---|---|---|---|---|---|
| act.1 | CampaignText.cs | act | Act I · Landfall | Hồi I · Landfall | 16 | 16 |
| act.2 | CampaignText.cs | act | Act II · Counteroffensive | Hồi II · Counteroffensive | 25 | 25 |
| act.3 | CampaignText.cs | act | Act III · Betrayal | Hồi III · Betrayal | 18 | 18 |
| act.4 | CampaignText.cs | act | Act IV · Silver Sky | Hồi IV · Silver Sky | 19 | 19 |
| ad.body | Strings.cs | ad | Test ad: a real ad network is connected before release. | Quảng cáo thử nghiệm: mạng quảng cáo thật sẽ được gắn trước… | 55 | 74 |
| ad.claim | Strings.cs | ad | Claim double coins | Nhận gấp đôi xu | 18 | 15 |
| ad.close | Strings.cs | ad | Close | Đóng | 5 | 4 |
| ad.title | Strings.cs | ad | ADVERTISEMENT | QUẢNG CÁO | 13 | 9 |
| aihint.airInbound | TacticText.cs | aihint | Enemy aircraft inbound. | Máy bay địch đang tới. | 23 | 22 |
| aihint.bigAttack | TacticText.cs | aihint | A big attack is coming down: clear the ring. | Đòn lớn sắp rơi: rời khỏi vòng cảnh báo. | 44 | 40 |
| aihint.enemyArtillery | TacticText.cs | aihint | Enemy artillery just showed itself. | Pháo địch vừa lộ vị trí. | 35 | 24 |
| aihint.losingPoint | TacticText.cs | aihint | A point is under pressure. | Một cứ điểm đang bị ép. | 26 | 23 |
| aihint.needAntiAir | TacticText.cs | aihint | Short of anti-air against their aircraft. | Thiếu phòng không trước máy bay địch. | 41 | 37 |
| aihint.needAntiTank | TacticText.cs | aihint | Short of anti-tank against their armour. | Thiếu chống tăng trước xe tăng địch. | 40 | 36 |
| aihint.opportunity | TacticText.cs | aihint | A valuable target is in sight. | Có mục tiêu giá trị trong tầm nhìn. | 30 | 35 |

*15 / 6535 dòng đầu: xem sheet 10_model_tai_san/Dia_phuong_hoa.*

### Dia_phuong_hoa_thong_ke

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Dia_phuong_hoa_thong_ke.

Sheet: 10_model_tai_san/Dia_phuong_hoa_thong_ke — Địa phương hóa: thống kê (15 dòng, 9 cột)

| id | so_khoa | thieu_en | thieu_vi | khai_hai_lan | ten_rieng_bi_dich | khong_thay_trong_ma |
|---|---|---|---|---|---|---|
| BaseText.cs | 133.0 | 0.0 | 0.0 | 0.0 | 0.0 | 12.0 |
| BigAttackText.cs | 108.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| BossText.cs | 313.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| CampaignText.cs | 1690.0 | 0.0 | 0.0 | 0.0 | 25.0 | 8.0 |
| CommanderText.cs | 174.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| DialogueText.cs | 18.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| EventText.cs | 157.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| GuideText.cs | 209.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| NameText.cs | 12.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| OrbitalText.cs | 36.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| SandboxText.cs | 251.0 | 0.0 | 0.0 | 0.0 | 0.0 | 16.0 |
| StoryText.cs | 325.0 | 0.0 | 0.0 | 0.0 | 3.0 | 0.0 |
| Strings.cs | 2729.0 | 0.0 | 0.0 | 0.0 | 6.0 | 128.0 |
| TacticText.cs | 209.0 | 0.0 | 0.0 | 0.0 | 0.0 | 65.0 |
| UnitText.cs | 171.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5.0 |

### Dia_phuong_hoa_van_de

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Dia_phuong_hoa_van_de.

Sheet: 10_model_tai_san/Dia_phuong_hoa_van_de — Địa phương hóa: khóa có vấn đề (271 dòng, 9 cột)

| id | bang | khong_thay_trong_ma | thieu_en | thieu_vi | khai_hai_lan |
|---|---|---|---|---|---|
| armor.air | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| armor.heavy | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| armor.light | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| armor.structure | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| army.balanced | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| army.noAir | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| army.noArmour | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| army.noArtillery | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.bonusStrike | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.bonusVehicle | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.cards | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.cardsNote | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.gear | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.gearNote | Strings.cs | TRUE | FALSE | FALSE | FALSE |
| arsenal.needPrints | Strings.cs | TRUE | FALSE | FALSE | FALSE |

*15 / 271 dòng đầu: xem sheet 10_model_tai_san/Dia_phuong_hoa_van_de.*

### Giay_phep_noi_dung

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Giay_phep_noi_dung.

Sheet: 10_model_tai_san/Giay_phep_noi_dung — Giấy phép: nội dung (374 dòng, 6 cột)

| id | giay_phep_tai_san_id | thu_tu | noi_dung |
|---|---|---|---|
| OFL-Barlow/0001 | OFL-Barlow | 0 | Copyright 2017 The Barlow Project Authors (https://github.c… |
| OFL-Barlow/0003 | OFL-Barlow | 2 | This Font Software is licensed under the SIL Open Font Lice… |
| OFL-Barlow/0004 | OFL-Barlow | 3 | This license is copied below, and is also available with a… |
| OFL-Barlow/0005 | OFL-Barlow | 4 | http://scripts.sil.org/OFL |
| OFL-Barlow/0008 | OFL-Barlow | 7 | ----------------------------------------------------------- |
| OFL-Barlow/0009 | OFL-Barlow | 8 | SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007 |
| OFL-Barlow/0010 | OFL-Barlow | 9 | ----------------------------------------------------------- |
| OFL-Barlow/0012 | OFL-Barlow | 11 | PREAMBLE |
| OFL-Barlow/0013 | OFL-Barlow | 12 | The goals of the Open Font License (OFL) are to stimulate w… |
| OFL-Barlow/0014 | OFL-Barlow | 13 | development of collaborative font projects, to support the… |
| OFL-Barlow/0015 | OFL-Barlow | 14 | efforts of academic and linguistic communities, and to prov… |
| OFL-Barlow/0016 | OFL-Barlow | 15 | open framework in which fonts may be shared and improved in… |
| OFL-Barlow/0017 | OFL-Barlow | 16 | with others. |
| OFL-Barlow/0019 | OFL-Barlow | 18 | The OFL allows the licensed fonts to be used, studied, modi… |
| OFL-Barlow/0020 | OFL-Barlow | 19 | redistributed freely as long as they are not sold by themse… |

*15 / 374 dòng đầu: xem sheet 10_model_tai_san/Giay_phep_noi_dung.*

### Kich_thuoc_that_chung

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Kich_thuoc_that_chung.

Sheet: 10_model_tai_san/Kich_thuoc_that_chung — Kích thước thật: ghi chú (1 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| _about | _about | Fix pass 8 (DECISIONS 'Sửa lỗi tổng hợp L8 prep'): the real… |

### Model_cham_diem

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_cham_diem.

Sheet: 10_model_tai_san/Model_cham_diem — Model: chấm điểm (230 dòng, 47 cột)

| id | lop | lop_ngan_sach | tam_giac_bao_cao | ngan_sach_duoi | ngan_sach_tren | ngan_sach_bao_cao | so_phan_bat_buoc | phan_thieu | muzzle_can |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | tracked | heavy | 6028.0 | 4000.0 | 7000.0 | ok | 14.0 | mantlet;idler;roof_mg;stowage | 1.0 |
| aa_gun_tower | tower | tower | 1724.0 | 2000.0 | 4000.0 | under | 4.0 |  | 1.0 |
| aa_gun_vehicle | tracked | heavy | 3556.0 | 4000.0 | 7000.0 | under | 14.0 | mantlet;idler;skirts;sight;roof_mg;smoke;stowage | 1.0 |
| aa_turret | tower | tower | 6306.0 | 2000.0 | 4000.0 | over | 4.0 |  | 2.0 |
| aa_turret_a | tower | tower | 6670.0 | 2000.0 | 4000.0 | over | 4.0 |  | 2.0 |
| aa_turret_b | tower | tower | 2610.0 | 2000.0 | 4000.0 | ok | 4.0 |  | 2.0 |
| aa_vehicle | tracked | heavy | 4964.0 | 4000.0 | 7000.0 | ok | 14.0 | mantlet;idler;sight;roof_mg;smoke;stowage | 2.0 |
| aerial_tanker | jet | jet | 4164.0 | 4000.0 | 7000.0 | ok | 9.0 | tail;exhaust;pylons;stores | 0.0 |
| airborne_light_tank | tracked | heavy | 5550.0 | 4000.0 | 7000.0 | ok | 14.0 | mantlet;idler;roof_mg;stowage | 1.0 |
| airborne_light_tank_chute | air_other | air_other | 3514.0 | 0.0 | 7000.0 | ok | 1.0 |  | 0.0 |
| airborne_vehicle | tracked | heavy | 3260.0 | 4000.0 | 7000.0 | under | 14.0 | mantlet;idler;skirts;sight;roof_mg;smoke;stowage | 2.0 |
| airborne_vehicle_chute | air_other | air_other | 3262.0 | 0.0 | 7000.0 | ok | 1.0 |  | 0.0 |
| ammo_carrier | wheeled | light | 3388.0 | 3000.0 | 5000.0 | ok | 7.0 | axles | 1.0 |
| ammo_dump | tower | tower | 5276.0 | 2000.0 | 4000.0 | over | 4.0 | base;roof | 0.0 |
| amphib_light_vehicle | tracked | heavy | 4606.0 | 4000.0 | 7000.0 | ok | 14.0 | mantlet;idler;skirts;roof_mg;smoke;stowage | 1.0 |

*15 / 230 dòng đầu: xem sheet 10_model_tai_san/Model_cham_diem; in 10 / 47 cột; 33 cột khác (và raw_json, nguon): xem sheet.*

### Model_chuan_vang

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_chuan_vang.

Sheet: 10_model_tai_san/Model_chuan_vang — Model: số đo bộ mẫu vàng (147 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|
| about | about |  | prompt 35 section 5.3: class means of the gold set (quality… |
| classes.air_other.asym_raw | asym_raw | 0.0003 |  |
| classes.air_other.count | count | 3 |  |
| classes.air_other.edges | edges | 0.1015 |  |
| classes.air_other.parts_m2 | parts_m2 | 0.2285 |  |
| classes.air_other.regions | regions | 2.1849 |  |
| classes.air_other.silhouette | silhouette | 2.7935 |  |
| classes.air_other.sloped_dirs | sloped_dirs | 11.0 |  |
| classes.air_other.tier2_m2 | tier2_m2 | 0.2875 |  |
| classes.air_other.tier3_m2 | tier3_m2 | 0.1769 |  |
| classes.air_other.zones | zones | 7.0 |  |
| classes.boss.asym_raw | asym_raw | 0.0208 |  |
| classes.boss.count | count | 33 |  |
| classes.boss.edges | edges | 0.1728 |  |
| classes.boss.parts_m2 | parts_m2 | 2.1627 |  |

*15 / 147 dòng đầu: xem sheet 10_model_tai_san/Model_chuan_vang.*

### Model_kiem_chuan_chung

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_kiem_chuan_chung.

Sheet: 10_model_tai_san/Model_kiem_chuan_chung — Model: kiểm chuẩn (chung) (3 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|
| count | count | 518 |  |
| generated | generated |  | 2026-10-03 |
| tool | tool |  | Tools/assets/glb_check.py |

### Model_lich_su

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_lich_su.

Sheet: 10_model_tai_san/Model_lich_su — Model: lịch sử kiểm chuẩn (91 dòng, 7 cột)

| id | models | changes | date | reason |
|---|---|---|---|---|
| 0 | main_battle_tank;main_battle_tank_hd;fighter_jet;fighter_je… | FLAG attack_helicopter: triangles 3,482 -> 4,362 (+25.3%);… | 2026-10-02 | Prompt 27 experiment 1 (DECISIONS '27 experiment 1'): V2 =… |
| 1 | ixion;rail_supergun;rail_tractor | FLAG ixion: triangles 21,628 -> 17,324 (-19.9%); vertices 2… | 2026-10-02 | P27 wave 1a: Ixion rebuilt as the BelAZ-75710 mine truck (o… |
| 2 | ixion | ixion: vertices 22,036 -> 22,038 (+0.0%); fileBytes 1,079,8… | 2026-10-02 | P27 wave 1a: Ixion's turret enlarged 1.35x after the first… |
| 3 | nyx | FLAG nyx: triangles 3,550 -> 3,526 (-0.7%); vertices 3,681… | 2026-10-02 | P27 wave 1b: Nyx's own Zumwalt-style model (helo deck mater… |
| 4 | hydra_sub | hydra_sub: new (7268 triangles) | 2026-10-02 | prompt 27 wave 1b: Hydra's own model (small VLS submarine,… |
| 5 | hydra_sub | hydra_sub: bytes only | 2026-10-02 | prompt 27 wave 1b: Hydra's launch-tube lids seated on the c… |
| 6 | cerberus |  | 2026-10-02 | prompt 27 wave 1b: Cerberus's own model (three coupled big-… |
| 7 | stymphalos;stymphalos_drone | stymphalos: new (4186 triangles);stymphalos_drone: new (502… | 2026-10-02 | prompt 27 wave 1b: Stymphalos's own model (eight delta jet… |
| 8 | garuda | garuda: new (2840 triangles) | 2026-10-02 | prompt 27 wave 1b: Garuda's own model (B-2 / B-21 flying wi… |
| 9 | hyperion | hyperion: new (7914 triangles) | 2026-10-02 | prompt 27 wave 1b: Hyperion's own model (hexagonal mirror r… |
| 10 | kraken | kraken: new (10796 triangles) | 2026-10-02 | prompt 27 wave 1b: Kraken's own model (Kuznetsov / Nimitz-s… |
| 11 | aa_57mm_vehicle;mine_rocket_truck;prop_attack_plane;light_a… | aa_57mm_vehicle: new (5468 triangles);combat_wreck_car: new… | 2026-10-02 | prompt 27 wave 1c pass A (1/2): own models for eight batch… |
| 12 | manpads_tower;river_patrol_boat;river_gunboat;coastal_ashm_… | airborne_light_tank: new (5550 triangles);airborne_light_ta… | 2026-10-02 | prompt 27 wave 1c pass A (2/2): own models for the other ei… |
| 13 | aa_57mm_vehicle;mine_rocket_truck;prop_attack_plane;light_a… | FLAG aa_57mm_vehicle: triangles 5,468 -> 6,028 (+10.2%); ve… | 2026-10-02 | prompt 27 wave 1c pass A: card-luminance pass (lighter Team… |
| 14 | twin_rotor_gunship;ground_drone_carrier;mobile_repair_vehic… | aerial_tanker: new (3220 triangles);bridging_vehicle: new (… | 2026-10-02 | prompt 27 wave 1c pass B: own models for the last 16 prompt… |

*15 / 91 dòng đầu: xem sheet 10_model_tai_san/Model_lich_su.*

### Model_nut

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_nut.

Sheet: 10_model_tai_san/Model_nut — Model: nút (13363 dòng, 7 cột)

| id | model_id | thu_tu | ten | tien_to |
|---|---|---|---|---|
| aa_57mm_vehicle/0 | aa_57mm_vehicle | 0 | Hatch_fittings.001 |  |
| aa_57mm_vehicle/1 | aa_57mm_vehicle | 1 | Hatches.001 |  |
| aa_57mm_vehicle/2 | aa_57mm_vehicle | 2 | Main_cannon |  |
| aa_57mm_vehicle/3 | aa_57mm_vehicle | 3 | Muzzle_brake | Muzzle |
| aa_57mm_vehicle/4 | aa_57mm_vehicle | 4 | Muzzle_main | Muzzle |
| aa_57mm_vehicle/5 | aa_57mm_vehicle | 5 | Radar_back |  |
| aa_57mm_vehicle/6 | aa_57mm_vehicle | 6 | Radar_mast |  |
| aa_57mm_vehicle/7 | aa_57mm_vehicle | 7 | Radar_panel |  |
| aa_57mm_vehicle/8 | aa_57mm_vehicle | 8 | Radar |  |
| aa_57mm_vehicle/9 | aa_57mm_vehicle | 9 | Sight_drum |  |
| aa_57mm_vehicle/10 | aa_57mm_vehicle | 10 | Sight_glass |  |
| aa_57mm_vehicle/11 | aa_57mm_vehicle | 11 | Smoke |  |
| aa_57mm_vehicle/12 | aa_57mm_vehicle | 12 | Smoke_brackets |  |
| aa_57mm_vehicle/13 | aa_57mm_vehicle | 13 | Turret_armor |  |
| aa_57mm_vehicle/14 | aa_57mm_vehicle | 14 | Turret_body |  |

*15 / 13363 dòng đầu: xem sheet 10_model_tai_san/Model_nut.*

### Model_spec_dung

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Model_spec_dung.

Sheet: 10_model_tai_san/Model_spec_dung — Model: spec dựng lại (173 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|
| ixion.aps | aps | FALSE |  |
| ixion.boss.how_to_fight | how_to_fight |  | unit_sheet description: armour front 4, side 3, rear and ro… |
| ixion.boss.scale_note | scale_note |  | modelSize is x1.26 of the real length (prompt 35 asks x1.3-… |
| ixion.boss.weak_points_visible | weak_points_visible |  | the four rear tyres (armour 1) stand bare behind the body:… |
| ixion.breakable[0].node | node |  | Part_wheel |
| ixion.breakable[0].part | part |  | wheel_l |
| ixion.breakable[1].node | node |  | Part_wheel.001 |
| ixion.breakable[1].part | part |  | wheel_r |
| ixion.breakable[2].node | node |  | Part_tyre |
| ixion.breakable[2].part | part |  | rear_l1 |
| ixion.breakable[3].node | node |  | Part_tyre.001 |
| ixion.breakable[3].part | part |  | rear_r1 |
| ixion.breakable[4].node | node |  | Part_tyre.002 |
| ixion.breakable[4].part | part |  | rear_l2 |
| ixion.breakable[5].node | node |  | Part_tyre.003 |

*15 / 173 dòng đầu: xem sheet 10_model_tai_san/Model_spec_dung.*

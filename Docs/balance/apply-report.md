# Balance spreadsheet: apply report

<!-- import_names:begin -->
## Tên đề xuất

Applied by `Tools/balance/import_names.py` (prompt 25 D1, DECISIONS 25D1): 63 rows applied, 1 skipped. A row applies its full name, its short name and its English name to `unit.<id>` and `short.<id>`, the head of `guide.<id>`, and every text that named the unit by its old name.

| id | full name (vi) | short (vi) | English | English short | before |
|---|---|---|---|---|---|
| `hover_gunboat` | Xuồng đệm khí hộ tống | Xuồng hộ tống | Escort hovercraft | Hovercraft | Xuồng cao tốc đệm khí / Hover gunboat |
| `armored_car` | Xe bọc thép bánh lốp | Bánh lốp | Armoured car | Armoured car | Xe bọc thép / Armored car |
| `ifv` | Xe chiến đấu bộ binh | Xe bộ binh | Infantry fighting vehicle | IFV | Xe chiến đấu bộ binh / Infantry fighting vehicle |
| `supply_truck` | Xe tải tiếp tế | Tiếp tế | Supply truck | Supply truck | Xe tiếp tế / Supply truck |
| `engineer_vehicle` | Xe công binh | Công binh | Engineering vehicle | Engineer | Xe công binh / Engineer vehicle |
| `smoke_carrier` | Xe thả khói | Xe khói | Smoke carrier | Smoke carrier | Xe tạo khói / Smoke generator carrier |
| `ammo_carrier` | Xe tiếp đạn | Tiếp đạn | Ammo carrier | Ammo carrier | Xe tiếp đạn / Ammunition carrier |
| `counter_battery_radar` | Xe radar phản pháo | Radar phản pháo | Counter-battery radar | CB radar | Radar phản pháo / Counter-battery radar |
| `ew_jammer` | Xe gây nhiễu điện tử | Gây nhiễu | EW jammer | Jammer | Xe tác chiến điện tử / EW jammer |
| `mine_layer` | Xe rải mìn | Rải mìn | Minelayer | Minelayer | Xe rải mìn / Mine layer |
| `command_vehicle` | Xe chỉ huy | Chỉ huy | Command vehicle | Command | Xe chỉ huy / Command vehicle |
| `shield_carrier` | Xe phát khiên | Phát khiên | Shield carrier | Shield carrier | Xe phát khiên / Shield carrier |
| `scout_jeep` | Xe trinh sát hạng nhẹ | Trinh sát | Scout jeep | Scout | Xe trinh sát / Scout jeep |
| `vbied` | Xe bom bọc thép | Xe bom | Armoured car bomb | Car bomb | Xe bom tự sát bọc thép / Armoured car bomb |
| `light_tank` | Tăng nhẹ lội nước | Tăng nhẹ | Amphibious light tank | Light tank | Tăng hạng nhẹ / Light tank |
| `flame_tank` | Tăng phun lửa | Phun lửa | Flame tank | Flame tank | Tăng phun lửa / Flame tank |
| `turtle_tank` | Tăng mái che | Tăng rùa | Turtle tank | Turtle tank | Xe tăng rùa / Turtle tank |
| `bmpt` | Xe hỗ trợ tăng | Hỗ trợ tăng | Tank support vehicle | Tank support | BMPT Terminator / BMPT Terminator |
| `rocket_technical` | Bán tải rốc-két | Bán tải rốc-két | Rocket technical | Rocket pickup | Bán tải rốc-két / Rocket technical |
| `mortar_carrier` | Xe cối tự hành | Xe cối | Mortar carrier | Mortar | Xe súng cối / Mortar carrier |
| `artillery` | Lựu pháo tự hành | Lựu pháo | SP howitzer | SP howitzer | Pháo tự hành / Artillery |
| `mlrs` | Pháo phản lực dẫn đường | Phản lực | Guided MLRS | Guided MLRS | Pháo phản lực / Rocket launcher |
| `shahed_truck` | Xe phóng drone cảm tử tầm xa | Drone cảm tử | Long-range drone launcher | Kamikaze drones | Xe phóng Shahed / Shahed launcher truck |
| `thermobaric_launcher` | Pháo phản lực nhiệt áp | Nhiệt áp | Thermobaric launcher | Thermobaric | Pháo phản lực nhiệt áp / Thermobaric launcher |
| `ballistic_launcher` | Xe phóng tên lửa chiến thuật | TL chiến thuật | Tactical ballistic launcher | Ballistic | Xe phóng tên lửa đạn đạo / Ballistic missile launcher |
| `heavy_rocket_artillery` | Pháo phản lực hạng nặng | Phản lực nặng | Heavy MLRS | Heavy MLRS | Pháo phản lực hạng nặng / Heavy rocket artillery |
| `siege_tank` | Pháo cối công thành | Công thành | Siege mortar | Siege mortar | Tăng công thành / Siege tank |
| `zu23_technical` | Bán tải cao xạ | Cao xạ bán tải | Flak technical | Flak technical | Bán tải ZU-23 / ZU-23 technical |
| `aa_vehicle` | Pháo cao xạ tự hành | Cao xạ | Self-propelled AA gun | AA gun | Xe phòng không / Anti-air |
| `sam_launcher` | Xe tên lửa phòng không tầm trung | PK tầm trung | Medium-range SAM | Medium SAM | Tên lửa phòng không / SAM launcher |
| `heavy_aa` | Xe phòng không pháo – tên lửa | PK hỗn hợp | Gun–missile AA | Gun–missile AA | Pháo tên lửa phòng không / Gun-missile air defence |
| `iron_beam` | Xe la-de phòng không | La-de PK | Laser AA | Laser AA | La-de phòng không / Iron Beam laser |
| `long_sam` | Xe tên lửa phòng không tầm xa | PK tầm xa | Long-range SAM | Long-range SAM | Tên lửa phòng không tầm xa / Long-range SAM |
| `scout_heli` | Trực thăng trinh sát vũ trang | TT trinh sát | Armed scout helicopter | Scout heli | Trực thăng trinh sát / Scout helicopter |
| `recon_drone` | UAV trinh sát | UAV trinh sát | Recon UAV | Recon UAV | UAV trinh sát / Recon drone |
| `wingman_drone` | Drone hộ vệ | Drone hộ vệ | Wingman drone | Wingman | Drone hộ vệ / Loyal wingman |
| `strike_drone` | UAV tấn công | UAV tấn công | Strike UAV | Strike UAV | UAV tấn công / Strike drone |
| `swarm_carrier` | Máy bay mẹ thả drone | Máy bay mẹ | Drone mothership aircraft | Mothership | Máy bay mẹ thả drone / Drone mothership |
| `attack_helicopter` | Trực thăng tấn công | TT tấn công | Attack helicopter | Attack heli | Trực thăng tấn công / Attack helicopter |
| `fighter_jet` | Tiêm kích | Tiêm kích | Fighter | Fighter | Tiêm kích / Fighter jet |
| `stealth_fighter` | Tiêm kích tàng hình | TK tàng hình | Stealth fighter | Stealth fighter | Tiêm kích tàng hình / Stealth fighter |
| `gunship_heli` | Trực thăng vũ trang bọc giáp | TT vũ trang | Armoured gunship helicopter | Gunship heli | Trực thăng hạng nặng / Heavy gunship |
| `attack_jet` | Máy bay cường kích | Cường kích | Attack jet | Attack jet | Máy bay cường kích / Attack jet |
| `stealth_bomber` | Oanh tạc cơ tàng hình | OTC tàng hình | Stealth bomber | Stealth bomber | Máy bay ném bom tàng hình / Stealth bomber |
| `heavy_bomber` | Oanh tạc cơ chiến lược | Oanh tạc cơ | Strategic bomber | Bomber | Oanh tạc cơ hạng nặng / Heavy bomber |
| `sky_gunship` | Pháo hạm bay | Pháo hạm | Airborne gunship | Gunship | Pháo hạm AC-130 / AC-130 Gunship |
| `bunker_vehicle` | Xe công sự triển khai | Công sự | Deployable bunker | Bunker | Xe công sự / Bunker vehicle |
| `armored_bulldozer` | Xe ủi bọc thép | Xe ủi | Armoured bulldozer | Bulldozer | Xe ủi bọc thép / Armoured bulldozer |
| `main_battle_tank` | Tăng chủ lực | Tăng chủ lực | Main battle tank | Battle tank | Tăng chủ lực / Main battle tank |
| `twin_tank` | Tăng hai nòng | Hai nòng | Twin-gun tank | Twin-gun tank | Tăng hai nòng / Twin-barrel tank |
| `heavy_tank` | Tăng hạng nặng | Tăng nặng | Heavy tank | Heavy tank | Tăng hạng nặng / Heavy tank |
| `titan_tank` | Siêu tăng | Siêu tăng | Super-heavy tank | Super tank | Siêu tăng Titan / Titan super tank |
| `fpv_carrier` | Xe phóng drone FPV | Drone FPV | FPV drone carrier | FPV drones | Xe phóng drone FPV / FPV drone carrier |
| `lancet_truck` | Xe phóng đạn lảng vảng | Đạn lảng vảng | Loitering munition truck | Loiter munition | Xe phóng Lancet / Loitering munition truck |
| `wheeled_gun` | Pháo xung kích bánh lốp | Pháo xung kích | Wheeled tank destroyer | Wheeled gun | Pháo bánh lốp diệt tăng / Wheeled tank hunter |
| `tank_destroyer` | Pháo chống tăng tự hành | Chống tăng | Tank destroyer | Tank destroyer | Pháo chống tăng / Tank destroyer |
| `railgun_truck` | Xe pháo điện từ | Pháo điện từ | Railgun truck | Railgun | Xe súng điện từ / Railgun truck |
| `laser_tank` | Xe la-de diệt tăng | La-de diệt tăng | Laser tank destroyer | Laser tank | Xe la-de tập trung / Focused-laser tank |
| `c_ram` | Trạm đánh chặn C-RAM | C-RAM | C-RAM interceptor | C-RAM | Trạm C-RAM / C-RAM |
| `drone_hangar` | Nhà chứa drone | Nhà chứa drone | Drone hangar | Drone hangar | Nhà chứa drone / Drone hangar |
| `heavy_turret` | Tháp pháo hạng nặng | Pháo hạng nặng | Heavy gun turret | Heavy gun | Pháo đài hạng nặng / Heavy fortress |
| `missile_battery` | Trạm tên lửa phòng không tầm xa | Trạm PK tầm xa | Long-range SAM site | SAM site | Tên lửa Patriot tầm xa / Patriot battery |
| `bulwark_post` | Ụ súng dã chiến | Ụ súng | Field gun post | Gun post | Ụ súng tạm / Fallback post |

Changed from the sheet:

- `ballistic_launcher` short name "TL chiến thuật": "Tên lửa chiến thuật" is 19 letters, over the 15 of one card line; "TL" is the short names' abbreviation of "tên lửa".
- `wheeled_gun` short name "Pháo xung kích": "Bánh lốp diệt tăng" is 18 letters; the first words of the full name instead.
- `missile_battery` short name "Trạm PK tầm xa": "PK tầm xa" is the long-range SAM vehicle's short name too; the tower keeps the "Trạm" of its full name.
- English names in sentence case and British spelling (the glossary): "Armored Car" is "Armoured car". English short names are the script's (the sheet has none).

Skipped:

- `spawn_bastion` (Tháp căn cứ): the sheet proposes no name ("kiểm tra còn dùng không"): the bastion is only the fallback of ModeSupport.Build when the catalogue has no HQ, which the shipped content always has; its old name stays until the base system drops it.

<!-- import_names:end -->

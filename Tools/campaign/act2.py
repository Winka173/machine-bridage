"""Act II, The Counterattack: chapters 4-6 (Ironport, Rust Yard; Emberridge, Jungle Pass; Hollow Dam, Whiteout and Ashfield reversed).

A reversed mission ("reversed": True) is written as the player sees it (the player's camp south-west);
build_campaign.py turns it round onto the battlefield."""

from campaign_kit import T, add_mission, ring, say, scripted, units, waves

KESSLER = ['wheeled_gun', 'ifv', 'main_battle_tank', 'heavy_tank', 'sam_launcher', 'fpv_carrier', 'mine_layer', 'mlrs']
SEN = ['strike_drone', 'fpv_carrier', 'lancet_truck', 'recon_drone', 'ew_jammer', 'ifv', 'main_battle_tank', 'aa_vehicle']
VARGA_LATE = ['main_battle_tank', 'heavy_tank', 'twin_tank', 'tank_destroyer', 'fpv_carrier', 'flame_tank', 'ifv', 'mlrs']


def m(mid, chapter, map_, goal, weather, **kw):
    d = {'id': mid, 'chapter': chapter, 'map': map_, 'goal': goal, 'weather': weather}
    d.update(kw)
    return d


def choice_income(label_en, label_vi, general_en, general_vi):
    return ((label_en, label_vi), (f'{general_en} earns 30 % less for the rest of the battle.', f'{general_vi} kiếm được ít hơn 30 % trong suốt phần còn lại của trận.'))


def choice_strikes(label_en, label_vi, every):
    return ((label_en, label_vi), (f'Free airstrikes about every {every} s for the rest of the battle.', f'Không kích miễn phí khoảng mỗi {every} giây trong suốt phần còn lại của trận.'))


WEAKEN = [{'at': 'end', 'kind': 'Income', 'team': 1, 'amount': 0.7}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.enemyWeakened'}]


def strikes(every, support='airstrike'):
    return [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': support, 'every': every}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.alliedStrikes'}]


# ================================================================================ CHAPTER 4: STEEL HARBOUR

add_mission(m('c4m01', 4, 'rustyard', 'Capture', 'Overcast', points=['west', 'town', 'east'], enemyOwns=['town'], general='kessler', reinforcements=2,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.9, enemyDeck=KESSLER,
              playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor', unlocks=['command_vehicle'], starTime=600, starLosses=10),
            ('The Rust Yard', 'Rust Yard'),
            ('Kessler\'s marshalling yard feeds the port. Take the foundry, the yard and the scrapyard, and his trains have nowhere to be put together.',
             'Bãi dồn toa của Kessler nuôi cả bến cảng. Chiếm xưởng đúc, bãi dồn toa và bãi phế liệu, các đoàn tàu của hắn sẽ không còn chỗ lắp ráp.'),
            (('The timetable', 'Thời gian biểu'),
             ('A Rust Yard timetable, pinned in the signal box: 212 trains a week, each to the minute. Handwritten at the bottom: "Delays will be explained to the Admiral in person."',
              'Một bảng giờ tàu ở Rust Yard, ghim trong trạm tín hiệu: 212 chuyến mỗi tuần, chính xác tới từng phút. Viết tay ở dưới: "Chuyến nào trễ sẽ phải giải trình trực tiếp với Đô đốc."')),
            [say('kessler', 'Start', 'You are four minutes behind schedule, Colonel.', 'Ngươi đang trễ bốn phút so với lịch, đại tá.'),
             say('khai', 'Start', 'Then we will make up the time.', 'Vậy thì ta sẽ bù lại số phút đó.')])

add_mission(m('c4m02', 4, 'ironport', 'Capture', 'Rain', legacy='m10', points=['west', 'town', 'east'], outposts=['town'], enemyOwns=['west', 'town', 'east'],
              timeLimit=1000, general='kessler', reinforcements=3,
              enemyAi='commander', enemyStance='Defend', difficulty='Hard', enemyCp=15, enemyIncome=0.7,
              enemyDeck=['main_battle_tank', 'heavy_tank', 'tank_destroyer', 'aa_vehicle', 'sam_launcher', 'mlrs', 'attack_helicopter', 'artillery'],
              playerCp=26, playerIncome=1.85, playerCap=36, unlocks=['attack_jet'], starTime=600, starLosses=12),
            ('Storm the Factories', 'Đánh chiếm khu nhà máy'),
            ('Kessler holds the docks, the factories and the rail yard of Ironport. Take all three in the rain, and set up an outpost in the factories.',
             'Kessler giữ bến tàu, khu nhà máy và bãi đường sắt của Ironport. Chiếm cả ba dưới mưa, và lập tiền đồn trong khu nhà máy.'),
            (('Made in Ironport', 'Sản xuất tại Ironport'),
             ('Every Behemoth hull left Ironport by sea. Mara recognised the factory\'s crane from the other side: she used to sign for the plates it lifted.',
              'Mọi thân tàu Behemoth đều rời Ironport bằng đường biển. Mara nhận ra cây cần cẩu của nhà máy, từ phía bên kia: cô từng ký nhận những tấm thép nó nâng.')),
            [say('linh', 'Start', 'Three objectives, all dug in. Take the factories first and build there.', 'Ba cứ điểm, cứ điểm nào cũng cố thủ. Chiếm khu nhà máy trước rồi dựng tiền đồn ở đó.')])

add_mission(m('c4m03', 4, 'ironport', 'Escort', 'Fog', legacy='m11', convoyCount=5, convoyNeeded=3, timeLimit=1100, reinforcements=2,
              convoy=scripted('supply_truck', (-105, -105), route=[(-33.75, -33.75), (-33.75, 33.75), (0, 33.75), (0, 106.8), (-56.25, 106.8)], heading=45),
              units=units(0, ['main_battle_tank', 'main_battle_tank', 'aa_vehicle', 'armored_car'], (-88, -92), 7),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['armored_car', 'rocket_technical', 'light_tank', 'attack_helicopter', 'flame_tank'], first=20, interval=26, size=3, grow=0.6, max_size=7, max_alive=18,
                          spawns=[(60, 93), (93, 15), (-96, 60)]),
              unlocks=['wheeled_gun'], starTime=300, starLosses=8, challenge={'kind': 'Kills', 'value': 25}),
            ('Dockside Convoy', 'Đoàn xe bến cảng'),
            ('Engineers and explosives for the docks, five trucks through the fogbound port. Three must reach the quay.',
             'Công binh và thuốc nổ cho bến tàu, năm xe tải xuyên qua bến cảng chìm trong sương. Phải tới được cầu tàu ba xe.'),
            (('Fog horn', 'Còi sương'),
             ('The port\'s fog horn sounds every ninety seconds. The drivers timed their dashes between the blasts, so the enemy could not hear the engines.',
              'Còi sương của bến cảng rú lên mỗi chín mươi giây. Cánh tài xế canh giờ lao xe vào giữa hai tiếng còi để địch không nghe thấy tiếng máy.')),
            [say('khai', 'Start', 'Fog is cover. Use it, and stay with the trucks.', 'Sương mù là chỗ ẩn nấp. Tận dụng nó, và bám sát đoàn xe.')])

add_mission(m('c4m04', 4, 'rustyard', 'Recon', 'Fog', legacy='m19', points=['west', 'town', 'east'], timeLimit=900, speaker='linh', general='kessler', reinforcements=2,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=16, enemyIncome=0.9,
              enemyDeck=['light_tank', 'ifv', 'main_battle_tank', 'aa_vehicle', 'tank_destroyer', 'mortar_carrier'],
              playerCp=24, playerIncome=1.35, playerCap=36, unlocks=['logistics_station'], starTime=420, starLosses=10, challenge={'kind': 'NoAircraft'}),
            ('Eyes on the Yard', 'Mắt nhìn Bãi Sắt'),
            ('Nadia needs to know where Juggernaut is being put together. Get a vehicle onto each of the three objectives and look, before Kessler digs in.',
             'Nadia cần biết Juggernaut đang được lắp ráp ở đâu. Đưa xe tới từng cứ điểm trong ba cứ điểm để quan sát, trước khi Kessler kịp cố thủ.'),
            (('Wagon numbers', 'Số hiệu toa'),
             ('Nadia copied the numbers off every wagon in the yard. Eleven of them came up twice in Kessler\'s own lists: Juggernaut, hiding in plain sight.',
              'Nadia chép lại số hiệu của mọi toa tàu trong bãi. Mười một số xuất hiện hai lần trong chính danh sách của Kessler: Juggernaut, trốn ngay trước mắt.')),
            [say('linh', 'Start', 'Three looks. Count the wagons if you can.', 'Ba lần quan sát. Đếm được toa tàu thì càng tốt.')])

add_mission(m('c4m05', 4, 'ironport', 'Intercept', 'Night', legacy='m12', timeLimit=1200, general='kessler', reinforcements=3,
              boss=scripted('armored_train', (128, 106.8), heading=270, route=[(75, 106.8), (0, 106.8), (-75, 106.8), (-138.75, 106.8)], health=1.6),
              units=[{'def': 'main_battle_tank', 'team': 0, 'x': -93.75, 'z': 56.25, 'heading': 45}, {'def': 'light_tank', 'team': 0, 'x': -82.5, 'z': 63.75, 'heading': 45},
                     {'def': 'tank_destroyer', 'team': 0, 'x': -101.25, 'z': 71.25, 'heading': 45}, {'def': 'tank_destroyer', 'team': 0, 'x': -71.25, 'z': 82.5, 'heading': 45},
                     {'def': 'mlrs', 'team': 0, 'x': -112.5, 'z': 41.25, 'heading': 45}, {'def': 'heavy_tank', 'team': 0, 'x': -56.25, 'z': 86.25, 'heading': 90},
                     {'def': 'heavy_tank', 'team': 0, 'x': -45, 'z': 93.75, 'heading': 90}],
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.85,
              enemyDeck=['main_battle_tank', 'heavy_tank', 'aa_vehicle', 'sam_launcher', 'gunship_heli', 'attack_jet'],
              playerCp=28, playerIncome=1.4, playerCap=36, unlocks=['thermobaric_launcher', 'field_tower'], starTime=480, starLosses=8, challenge={'kind': 'NoStrikes'}),
            ('The Steel Train', 'Juggernaut'),
            ('Kessler\'s armoured train is running for the docks with a cargo Nadia does not like the sound of. Destroy it before it arrives.',
             'Đoàn tàu bọc thép của Kessler đang lao về bến tàu với một chuyến hàng mà Nadia nghe tên đã thấy không ổn. Phá hủy nó trước khi nó tới nơi.'),
            (('The cargo', 'Chuyến hàng'),
             ('The train\'s manifest, recovered from the wreck: forty tons of "laboratory equipment" addressed to "Project Icarus, Skyhold". The first time anyone read those two letters.',
              'Bản kê hàng của đoàn tàu, tìm thấy trong xác tàu: bốn mươi tấn "thiết bị phòng thí nghiệm" gửi tới "Dự án Icarus, Skyhold". Lần đầu tiên có người đọc thấy hai chữ cái đó.')),
            [say('kessler', 'Start', 'The train leaves on time, Colonel. It always does.', 'Tàu chạy đúng giờ, đại tá. Xưa nay vẫn thế.'),
             say('khai', 'Boss', 'Everything on the train. Now.', 'Dồn hết vào đoàn tàu. Ngay.'),
             say('kessler', 'Win', 'Cancel the timetable.', 'Hủy lịch trình.')])

add_mission(m('c11m05', 11, 'rustyard', 'Boss', 'Clear', timeLimit=1200, general='kessler', reinforcements=3,
              boss=scripted('rail_supergun', (140, 11.25), heading=270, name='rail_supergun'),
              units=units(0, ['main_battle_tank', 'tank_destroyer', 'heavy_tank', 'wheeled_gun'], (-70, -40), 8),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=12, enemyIncome=0.85, enemyDeck=KESSLER,
              playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor', starTime=540, starLosses=10),
            ('The Gungnir', 'Gungnir'),
            ('Kessler has a gun too big for any road, parked on the rails at the edge of the Rust Yard. Every twenty seconds it drops a shell on us, and the ground warns us three seconds before. Fight through its guard and destroy it.',
             'Kessler có một khẩu pháo quá to cho mọi con đường, đậu trên đường ray ở rìa Rust Yard. Cứ hai mươi giây nó lại nã một phát vào ta, và mặt đất báo trước ba giây. Đánh xuyên qua đội canh gác và phá hủy nó.'),
            (('Forty kilometres', 'Bốn mươi cây số'),
             ('The supergun\'s range card says forty kilometres. Its crew manual says: "Do not fire within forty kilometres of the Admiral." He was never that far from it.',
              'Bảng tầm bắn của siêu pháo ghi bốn mươi cây số. Sổ tay kíp pháo ghi: "Không được bắn khi Đô đốc ở trong vòng bốn mươi cây số." Ông ta chưa từng rời xa nó tới thế.')),
            [say('linh', 'Start', 'The supergun is on the east rails. Watch the ground: where it cracks red, a shell lands three seconds later.', 'Siêu pháo nằm trên đường ray phía đông. Để ý mặt đất: chỗ nào nứt đỏ, ba giây sau đạn rơi xuống đó.'),
             say('mai', 'BossHalf', 'Take out its targeting station and its shells go wide.', 'Phá trạm chỉ thị mục tiêu của nó là đạn sẽ rơi lệch.')])

add_mission(m('c4m07', 4, 'ironport', 'Protect', 'Overcast', reversed=True, targets=['factory', 'office_block'], protectNeeded=1, targetHealth=14, surviveSeconds=420,
              general='kessler', reinforcements=2,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.85, enemyDeck=KESSLER,
              playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['ifv', 'main_battle_tank', 'mine_layer', 'wheeled_gun', 'attack_helicopter'], first=90, interval=65, size=2, grow=0.3, max_size=4, max_alive=10),
              starTime=0, starLosses=10, challenge={'kind': 'NoAircraft'}),
            ('Kessler Strikes Back', 'Kessler phản đòn'),
            ('We hold the factory district now, and the workers are back at their benches. Kessler is coming from the south to burn it rather than lose it. '
             'Keep at least one building standing for seven minutes.',
             'Giờ ta giữ khu nhà máy, và công nhân đã quay lại bàn máy. Kessler đang kéo tới từ phía nam để đốt trụi nó chứ không chịu mất. '
             'Giữ ít nhất một tòa nhà đứng vững trong bảy phút.'),
            (('The foreman', 'Ông đốc công'),
             ('The factory\'s foreman stayed at his post through the whole attack. Asked why, he said: "Somebody has to switch the furnaces off properly. Hegemon never did."',
              'Ông đốc công bám trụ ở vị trí suốt trận tấn công. Hỏi vì sao, ông bảo: "Phải có người tắt lò cho đúng cách. Bọn Hegemon chẳng bao giờ làm."')),
            [say('khai', 'Start', 'The factories are the objective. Everything else is noise.', 'Khu nhà máy là mục tiêu. Mọi thứ khác chỉ là tiếng ồn.')])

add_mission(m('c4m08', 4, 'rustyard', 'Hunt', 'Night', general='kessler', timeLimit=1500, targetHealth=1.5, reinforcements=2,
              hunt=[scripted('mine_layer', (60, 70), route=[(90, 60), (40, 80), (60, 40)]),
                    scripted('mine_layer', (-20, 90), route=[(-50, 100), (0, 70), (-30, 60)]),
                    scripted('mine_layer', (80, -10), route=[(90, -30), (60, 10), (90, 25)])],
              units=units(1, ['main_battle_tank', 'sam_launcher'], (60, 70), 7) + units(1, ['wheeled_gun', 'ifv'], (-20, 90), 6) + units(1, ['heavy_tank', 'aa_vehicle'], (80, -10), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.9, enemyDeck=KESSLER,
              playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor', starTime=660, starLosses=10, challenge={'kind': 'Kills', 'value': 25}),
            ('Minelayers', 'Tàu rải mìn trên cạn'),
            ('Every night Kessler\'s minelayers seed the roads to the port. Nadia has marked three of them. Hunt them before they finish their round.',
             'Đêm nào các xe rải mìn của Kessler cũng gieo mìn khắp những con đường vào cảng. Nadia đã đánh dấu ba chiếc. Săn chúng trước khi chúng xong một vòng.'),
            (('Kessler\'s mines', 'Mìn của Kessler'),
             ('Kessler\'s mines are numbered, dated and logged. His engineers could tell us the exact place of every one. They did, for a hot meal each.',
              'Mìn của Kessler được đánh số, ghi ngày và vào sổ. Công binh của hắn có thể chỉ cho ta chính xác vị trí từng quả. Và họ đã chỉ, đổi lấy mỗi người một bữa ăn nóng.')),
            [say('linh', 'Start', 'Three marked vehicles, moving slowly. Where they have been, drive carefully.', 'Ba xe được đánh dấu, đi chậm. Đường chúng đã qua, lái cẩn thận.')])

add_mission(m('c4m09', 4, 'ironport', 'Duel', 'Storm', targetHealth=0.3, general='kessler', enemyBase='Target', enemyHq=2, replay=True, reinforcements=1, timeLimit=1800,
              units=units(0, ['artillery', 'artillery', 'mlrs'], (-86, -86), 6), enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=11, enemyIncome=0.34,
              playerCp=30, playerIncome=2.3, playerCap=40, playerBase='Anchor', starTime=900, starLosses=14),
            ('The Admiral\'s Quarters', 'Tổng hành dinh của Đô đốc'),
            ('Kessler\'s headquarters stands behind the container stacks at the north end of the port, a little of every defence and mines everywhere. '
             'Break it in the storm and level his HQ.',
             'Sở chỉ huy của Kessler nằm sau những dãy container ở đầu bắc bến cảng, phòng thủ thứ gì cũng có một ít và mìn ở khắp nơi. '
             'Phá nó giữa cơn bão và san phẳng sở chỉ huy.'),
            (('The logbook', 'Cuốn sổ nhật ký'),
             ('Kessler\'s logbook, last entry before the storm: "Weather: unacceptable. Enemy: unacceptable. Morale: acceptable." He took the logbook with him when he ran.',
              'Sổ nhật ký của Kessler, dòng cuối trước cơn bão: "Thời tiết: không chấp nhận được. Quân địch: không chấp nhận được. Tinh thần: chấp nhận được." Hắn mang theo cuốn sổ khi tháo chạy.')),
            [say('kessler', 'Start', 'Every road here is mined. I checked.', 'Mọi con đường ở đây đều có mìn. Ta đã kiểm tra rồi.'),
             say('kessler', 'Win', 'Evacuate the quarters. By sea.', 'Sơ tán tổng hành dinh. Bằng đường biển.')])

add_mission(m('c4m10', 4, 'ironport', 'Capture', 'Clear', operation=True, general='kessler', reinforcements=3,
              playArea={'minX': -146, 'minZ': -146, 'maxX': 146, 'maxZ': 146},
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=16, enemyIncome=0.95, enemyDeck=KESSLER,
              playerCp=30, playerIncome=1.7, playerCap=42, playerBase='Anchor',
              waves=waves(['ifv', 'main_battle_tank', 'wheeled_gun', 'attack_helicopter', 'heavy_tank'], first=90, interval=65, size=2, grow=0.3, max_size=5, max_alive=12),
              unlocks=['laser_tank', 'cp_relay'],
              stages=[
                  {'stage': 'yard', 'goal': 'Capture', 'points': ['east'], 'enemyOwns': ['west', 'town', 'east'], 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c4m10.s1'}],
                   'choices': [{'key': 'crane', 'next': 'crane'}, {'key': 'signal', 'next': 'signal'}]},
                  {'stage': 'crane', 'goal': 'Destroy', 'targets': ['fuel_tank', 'rail_tanker'], 'targetX': 45, 'targetZ': -85, 'targetRadius': 30, 'targetHealth': 2, 'cp': 6, 'next': 'factories',
                   'events': WEAKEN},
                  {'stage': 'signal', 'goal': 'Survive', 'points': ['east'], 'surviveSeconds': 150, 'cp': 6, 'next': 'factories', 'events': strikes(55)},
                  {'stage': 'factories', 'goal': 'Capture', 'points': ['town', 'west'], 'enemyOwns': ['town', 'west'], 'cp': 10,
                   'events': [{'at': 'start', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'wheeled_gun', 'sam_launcher']}]},
                  {'stage': 'works', 'goal': 'Survive', 'points': ['town'], 'surviveSeconds': 240, 'cp': 8,
                   'events': [{'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'mine_layer']}]},
                  {'stage': 'tempest', 'goal': 'Boss', 'boss': scripted('behemoth_tempest', (-56, 100), heading=180, health=1.8), 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.kessler.c4m10.s4'}]},
                  {'stage': 'quay', 'goal': 'Survive', 'points': ['west'], 'surviveSeconds': 540,
                   'events': [{'at': '20', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'fpv_carrier', 'mlrs']},
                              {'at': '200', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'wheeled_gun', 'sam_launcher']}]},
              ],
              starTime=1380, starLosses=18),
            ('Take the Port', 'Chiếm bến cảng'),
            ('The whole port, in one day: the rail yard, then the factories and the docks. On the quay, Nadia\'s intercepts say, Tempest is waiting with its railgun. '
             'Take everything, destroy Tempest, and hold the quay against Kessler\'s last counterattack.',
             'Cả bến cảng, trong một ngày: bãi đường sắt, rồi khu nhà máy và bến tàu. Trên cầu tàu, theo các bản chặn thu của Nadia, Tempest đang chờ với khẩu súng điện từ. '
             'Chiếm tất cả, tiêu diệt Tempest, rồi giữ cầu tàu trước đợt phản công cuối cùng của Kessler.'),
            (('Tempest', 'Tempest'),
             ('Kessler shipped Tempest to the docks so it could sail if the port fell. It never sailed. Its railgun now points at the sea, in the brigade\'s museum yard.',
              'Kessler đưa Tempest ra bến để nó kịp xuống tàu nếu cảng thất thủ. Nó chưa bao giờ xuống tàu. Giờ khẩu súng điện từ của nó chĩa ra biển, trong sân bảo tàng của lữ đoàn.')),
            [say('khai', 'Start', 'The port, Brigade. All of it, by tonight.', 'Bến cảng, Lữ đoàn. Toàn bộ, trước đêm nay.'),
             say('khai', 'Win', 'Ironport is free. Kessler\'s timetable is ours now.', 'Ironport tự do rồi. Thời gian biểu của Kessler giờ thuộc về ta.')],
            stages_text={'yard': ('The Rail Yard', 'Bãi đường sắt'), 'crane': ('Burn the Fuel Wagons', 'Đốt các toa nhiên liệu'), 'signal': ('Hold the Signal Box', 'Giữ trạm tín hiệu'),
                         'factories': ('The Factories and the Docks', 'Khu nhà máy và bến tàu'), 'works': ('Hold the Factories', 'Giữ khu nhà máy'),
                         'tempest': ('Tempest', 'Tempest'), 'quay': ('Hold the Quay', 'Giữ cầu tàu')},
            choices_text={'crane': choice_income('Burn the fuel wagons', 'Đốt các toa nhiên liệu', 'Kessler', 'Kessler'),
                          'signal': choice_strikes('Hold the signal box (150 s)', 'Giữ trạm tín hiệu (150 giây)', 55)})
T('radio.khai.c4m10.s1', 'The rail yard first: it is the key to the rest.', 'Bãi đường sắt trước: nó là chìa khóa cho phần còn lại.')
T('radio.kessler.c4m10.s4', 'Tempest, clear the docks. On schedule.', 'Tempest, dọn sạch bến tàu. Đúng lịch.')

# Prompt 16: the chapter's epilogue. The port lost, Kessler puts to sea on Leviathan and shells the coast from the
# bay; sink it before it gets away. After the operation (its tenth mission), so the chapter's shape holds: an
# epilogue mission is a main mission the chapter's count and "the tenth is the operation" rule leave out.
LEVIATHAN_START = (42.4, -127.3)   # the far lane (w 120) at u -60, in the coast's frame
add_mission(m('c4m11', 4, 'lighthousebay', 'Boss', 'Overcast', epilogue=True, replay=True, timeLimit=1500, general='kessler', reinforcements=3,
              boss=scripted('leviathan', LEVIATHAN_START, heading=45, name='leviathan'),
              units=units(0, ['artillery', 'mlrs', 'main_battle_tank', 'aa_vehicle', 'tank_destroyer', 'ifv'], (-86, -86), 7),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=10, enemyIncome=0.7, enemyDeck=KESSLER,
              playerCp=30, playerIncome=1.6, playerCap=38, playerBase='Anchor', unlocks=['heavy_turret.coastal'],
              starTime=960, starLosses=12, challenge={'kind': 'Kills', 'value': 20}),
            ('Leviathan', 'Leviathan'),
            ('Ironport is ours, but Kessler got out by sea. He is aboard Leviathan, his battleship, off Beacon Bay, and he means to shell the '
             'coast until we give the port back. Take the lighthouse to see his fleet, man the old coastal batteries, and sink it before it runs for open sea.',
             'Ironport đã về tay ta, nhưng Kessler thoát được bằng đường biển. Hắn đang ở trên Leviathan, chiến hạm của hắn, ngoài khơi Beacon Bay, '
             'và định nã pháo vào bờ cho tới khi ta trả lại bến cảng. Chiếm ngọn hải đăng để thấy hạm đội của hắn, dùng các trận địa pháo bờ biển cũ, '
             'và đánh chìm nó trước khi nó chạy ra khơi.'),
            (('The timetable', 'Thời gian biểu'),
             ('Divers brought up Leviathan\'s bridge clock a month later. It had stopped at 16:42, the minute the second magazine went. '
              'Kessler\'s last order in the log, in his own hand: "Record the time."',
              'Một tháng sau, thợ lặn vớt được chiếc đồng hồ trên cầu chỉ huy của Leviathan. Nó dừng ở 16 giờ 42, đúng phút kho đạn thứ hai phát nổ. '
              'Mệnh lệnh cuối cùng trong sổ, chữ của chính Kessler: "Ghi lại thời gian."')),
            [say('linh', 'Start', 'Leviathan is on the far lane. We cannot see its fleet from the beach: the lighthouse can.',
                 'Leviathan đang ở tuyến xa. Từ bãi biển ta không thấy hạm đội của nó: ngọn hải đăng thì thấy.'),
             say('mai', 'Start', 'Its sides will stop anything we have. Its deck will not: artillery and bombs.',
                 'Hông tàu chặn được mọi thứ ta có. Boong thì không: pháo binh và bom.', at=20),
             say('khai', 'BossHalf', 'It is coming in close. Tanks on the pier heads, now.', 'Nó đang áp sát. Đưa xe tăng ra đầu cầu tàu, ngay.'),
             say('khai', 'Win', 'Kessler\'s timetable ends here.', 'Thời gian biểu của Kessler kết thúc ở đây.')])

add_mission(m('c4s1', 4, 'rustyard', 'Escort', 'Rain', side=True, after='c4m03', speaker='linh', convoyCount=4, convoyNeeded=3, timeLimit=1000, reinforcements=1,
              convoy=scripted('supply_truck', (-100, -100), route=[(-82.5, -82.5), (-82.5, -60), (-40, -33.75), (20, -33.75), (63.75, -60), (63.75, -86.25)], heading=45),
              units=units(0, ['main_battle_tank', 'heavy_aa', 'wheeled_gun'], (-90, -88), 6),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['ifv', 'wheeled_gun', 'light_tank', 'attack_helicopter'], first=20, interval=30, size=2, grow=0.45, max_size=6, max_alive=13,
                          spawns=[(80, 60), (100, 0), (20, 100)]),
              rarePrints=30, starTime=360, starLosses=6),
            ('The Prisoners\' Train', 'Chuyến tàu tù binh'),
            ('Nadia has found where Kessler keeps the Accord prisoners: a siding at the scrapyard. Four trucks to bring them out; three must make it.',
             'Nadia đã tìm ra nơi Kessler giam giữ tù binh Accord: một đường tránh ở bãi phế liệu. Bốn xe tải để đưa họ ra; phải thoát được ba xe.'),
            (('Names', 'Những cái tên'),
             ('Eighty-four prisoners came out of the siding. Nadia read every name over the radio that night, so their families would hear.',
              'Tám mươi tư tù binh được đưa ra khỏi đường tránh. Đêm đó Nadia đọc từng cái tên trên sóng phát thanh, để gia đình họ được nghe.')),
            [say('linh', 'Start', 'The prisoners are at the scrapyard. Bring them home.', 'Tù binh đang ở bãi phế liệu. Đưa họ về nhà.')])

add_mission(m('c4s2', 4, 'ironport', 'Hunt', 'Clear', side=True, reversed=True, after='c4m07', speaker='linh', timeLimit=1300, targetHealth=1.8, reinforcements=1,
              hunt=[scripted('command_vehicle', (60, 60), route=[(80, 40), (40, 80), (70, 90)]),
                    scripted('command_vehicle', (-30, 90), route=[(-60, 100), (0, 80), (-20, 60)])],
              units=units(1, ['main_battle_tank', 'aa_vehicle', 'ifv'], (60, 60), 7) + units(1, ['wheeled_gun', 'sam_launcher'], (-30, 90), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.85, enemyDeck=KESSLER,
              playerCp=26, playerIncome=1.4, playerCap=36, playerBase='Anchor', towerGear='Epic', starTime=480, starLosses=8),
            ('Harbour Masters', 'Những viên cảng vụ'),
            ('Two of Kessler\'s harbour masters are still running the smuggling routes from command cars. Nadia has marked them. Bring them in, the hard way.',
             'Hai viên cảng vụ của Kessler vẫn đang điều hành các tuyến buôn lậu từ xe chỉ huy. Nadia đã đánh dấu họ. Bắt họ về, bằng cách khó.'),
            (('The smugglers\' ledger', 'Sổ sách buôn lậu'),
             ('The harbour masters\' ledger listed every buyer of Hegemon weapons on the coast. One name had been crossed out and written again in ink: Thorne.',
              'Sổ sách của các viên cảng vụ ghi tên mọi kẻ mua vũ khí Hegemon trên Meridian Coast. Một cái tên bị gạch đi rồi viết lại bằng mực: Thorne.')),
            [say('linh', 'Start', 'Two command cars, marked. They talk a lot; that is how I found them.', 'Hai xe chỉ huy, đã đánh dấu. Chúng nói nhiều lắm; tôi tìm ra chúng là nhờ thế.')])

# ================================================================================ CHAPTER 5: JUNGLE FIRE

add_mission(m('c5m01', 5, 'junglepass', 'Capture', 'Rain', legacy='m14', points=['west', 'town', 'east'], outposts=['west'], enemyOwns=['town', 'east'], timeLimit=1100,
              general='sen', reinforcements=3,
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.9,
              enemyDeck=['light_tank', 'ifv', 'main_battle_tank', 'flame_tank', 'attack_helicopter', 'tank_destroyer', 'strike_drone'],
              waves=waves(['ifv', 'main_battle_tank', 'elite_mbt', 'attack_helicopter'], first=80, interval=70, size=2, grow=0.3, max_size=4, max_alive=10),
              playerCp=24, playerIncome=1.35, playerCap=36, unlocks=['strike_drone'], starTime=600, starLosses=14, challenge={'kind': 'NoAircraft'}),
            ('Temple of Ash', 'Đền Tro'),
            ('Venn\'s outer guard holds the temple ford and the east village of the Jungle Pass. Take the whole pass in the rain.',
             'Lực lượng canh gác vòng ngoài của Venn giữ bến đền cổ và làng phía đông Jungle Pass. Chiếm trọn con đèo dưới mưa.'),
            (('The temple', 'Ngôi đền'),
             ('The temple in the pass is eight hundred years old. Venn\'s engineers used its courtyard to test drones, and left the carvings alone. Nadia noticed that.',
              'Ngôi đền trên đèo đã tám trăm năm tuổi. Kỹ sư của Venn dùng sân đền để thử drone, nhưng không đụng tới những bức chạm khắc. Nadia để ý điều đó.')),
            [say('sen', 'Start', 'The swarm does not hate you, Colonel. It does not anything.', 'Bầy drone không ghét các anh, đại tá. Nó chẳng có cảm xúc gì cả.'),
             say('linh', 'Start', 'That was Dr Venn, on an open channel. She wanted us to hear.', 'Đó là tiến sĩ Venn, trên kênh mở. Bà ấy muốn ta nghe thấy.')])

add_mission(m('c5m02', 5, 'emberridge', 'Hunt', 'Night', general='sen', timeLimit=1100, targetHealth=2.5, reinforcements=2,
              hunt=[scripted('fpv_carrier', (60, 60), route=[(80, 80), (40, 50), (70, 30)]),
                    scripted('lancet_truck', (-20, 90), route=[(-50, 90), (0, 70), (-30, 60)]),
                    scripted('fpv_carrier', (90, -10), route=[(110, -40), (80, 10), (110, 20)])],
              units=units(1, ['main_battle_tank', 'aa_vehicle'], (60, 60), 6) + units(1, ['ifv', 'ew_jammer'], (-20, 90), 6) + units(1, ['main_battle_tank', 'aa_vehicle'], (90, -10), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.9, enemyDeck=SEN,
              playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor', unlocks=['fpv_carrier'], starTime=660, starLosses=10, challenge={'kind': 'Kills', 'value': 25}),
            ('Swarm Trucks', 'Xe bầy đàn'),
            ('Three of Venn\'s launch trucks send drone swarms over the lava fields every night. Nadia has marked them. Hunt them in the glow of the lava.',
             'Ba xe phóng của Venn đêm nào cũng tung bầy drone qua đồng dung nham. Nadia đã đánh dấu chúng. Săn chúng dưới ánh sáng của dung nham.'),
            (('Drone serials', 'Số hiệu drone'),
             ('Every one of Venn\'s drones carries a serial number and a single word stamped under the wing: "Sorry." Nobody in Hegemon ever turned one over.',
              'Mỗi chiếc drone của Venn đều mang một số hiệu và một chữ duy nhất đóng dưới cánh: "Xin lỗi." Chưa ai bên Hegemon từng lật một chiếc lên mà xem.')),
            [say('linh', 'Start', 'Three launch trucks. Kill the trucks and the swarms stop coming.', 'Ba xe phóng. Diệt được xe là bầy drone thôi kéo tới.')])

add_mission(m('c5m03', 5, 'junglepass', 'Escort', 'Fog', convoyCount=5, convoyNeeded=3, timeLimit=1100, reinforcements=2,
              convoy=scripted('supply_truck', (-100, -100), route=[(-82.2, -71.6), (-50.4, -50.4), (-77, -13), (-82, 34), (-75, 63)], heading=45),
              units=units(0, ['main_battle_tank', 'heavy_aa', 'ifv', 'heavy_tank'], (-88, -90), 6),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['ifv', 'light_tank', 'strike_drone', 'armored_car', 'fpv_carrier'], first=35, interval=32, size=2, grow=0.35, max_size=5, max_alive=12,
                          spawns=[(60, 80), (95, 20), (20, 110)]),
              starTime=360, starLosses=8, challenge={'kind': 'Kills', 'value': 22}),
            ('River Road', 'Đường ven sông'),
            ('Bridging gear for the engineers, up the river road through the jungle fog to the west village. Three of five trucks must arrive; Venn\'s drones will be looking for them.',
             'Thiết bị bắc cầu cho công binh, ngược đường ven sông qua sương rừng tới làng phía tây. Năm xe phải tới được ba; drone của Venn sẽ săn lùng chúng.'),
            (('The bridges', 'Những cây cầu'),
             ('The engineers built four bridges over the river in two days. The villagers named the last one after the brigade. The brigade named it after the villagers.',
              'Công binh bắc bốn cây cầu qua sông trong hai ngày. Dân làng đặt tên cây cầu cuối theo tên lữ đoàn. Lữ đoàn lại đặt tên nó theo tên dân làng.')),
            [say('khai', 'Start', 'Eyes up. The fog does not hide you from drones.', 'Nhìn lên trời. Sương mù không che được các anh khỏi drone đâu.')])

add_mission(m('c5m04', 5, 'emberridge', 'Outpost', 'Clear', points=['town'], holdSeconds=180, speaker='mai', general='sen', reinforcements=2, timeLimit=1100,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=13, enemyIncome=0.85, enemyDeck=SEN,
              playerCp=28, playerIncome=1.5, playerCap=38, playerBase='Anchor',
              waves=waves(['strike_drone', 'ifv', 'main_battle_tank', 'fpv_carrier'], first=70, interval=55, size=2, grow=0.3, max_size=4, max_alive=12),
              unlocks=['twin_tank', 'airfield'], starTime=600, starLosses=10),
            ('The Geothermal Plant', 'Nhà máy địa nhiệt'),
            ('Mara wants the geothermal plant in the middle of Emberridge: free power for a forward base. Take it, set up an outpost, keep it three minutes.',
             'Mara muốn lấy nhà máy địa nhiệt giữa Emberridge: điện miễn phí cho một căn cứ tiền phương. Chiếm nó, lập tiền đồn, giữ ba phút.'),
            (('Free power', 'Điện miễn phí'),
             ('Mara\'s note on the plant: "Output 40 MW. Enough for the base, the airfield and the coffee machine. In that order. No, reverse that order."',
              'Ghi chú của Mara về nhà máy: "Công suất 40 MW. Đủ cho căn cứ, sân bay và máy pha cà phê. Theo thứ tự đó. À không, đảo ngược thứ tự đó."')),
            [say('mai', 'Start', 'Forty megawatts under our feet. Give me the plant.', 'Bốn mươi megawatt ngay dưới chân. Cho tôi nhà máy đó.'),
             say('sen', 'At', 'You are sitting on a volcano, Engineer. I would not get comfortable.', 'Cô đang ngồi trên núi lửa đấy, kỹ sư. Tôi mà là cô thì không ngồi yên đâu.', at=120)])

add_mission(m('c5m05', 5, 'junglepass', 'Boss', 'Storm', general='sen', timeLimit=1200, reinforcements=3,
              boss=scripted('fortress_hive', (84, 84), heading=225, route=[(60, 60), (20, 30), (-20, 10), (30, -20)], health=1.1),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=13, enemyIncome=0.85, enemyDeck=SEN,
              playerCp=28, playerIncome=1.5, playerCap=38, playerBase='Anchor', hqLevel=3, unlocks=['long_sam'], starTime=780, starLosses=12, challenge={'kind': 'NoAircraft'}),
            ('The Hive', 'Hive'),
            ('Venn\'s drone fortress is crawling down the pass in the storm, swarms rising from its racks. It has no main gun and fears no aircraft. Break it with tanks and artillery.',
             'Pháo đài drone của Venn đang bò xuống con đèo trong cơn bão, bầy drone bốc lên từ các giàn phóng. Nó không có pháo chính và chẳng sợ máy bay nào. Đập vỡ nó bằng xe tăng và pháo binh.'),
            (('Rescue system', 'Hệ thống cứu hộ'),
             ('The Hive\'s original design document, found in its wreck: "Autonomous swarm for search and rescue in disaster zones." The word "rescue" had been crossed out, by someone else.',
              'Tài liệu thiết kế gốc của Hive, tìm thấy trong xác nó: "Bầy drone tự hành phục vụ tìm kiếm cứu nạn ở vùng thảm họa." Chữ "cứu nạn" đã bị gạch đi, bởi một người khác.')),
            [say('sen', 'Start', 'Seven hundred drones in the air. Count them if you like.', 'Bảy trăm drone đang trên trời. Các anh cứ đếm nếu thích.'),
             say('khai', 'Boss', 'Ground guns on it. Keep the aircraft home.', 'Pháo mặt đất dồn vào nó. Máy bay ở nhà.'),
             say('sen', 'Win', 'Enough. Stand the swarm down.', 'Đủ rồi. Cho bầy drone hạ cánh.')])

add_mission(m('c5m06', 5, 'emberridge', 'Destroy', 'Night', variant='siege', legacy='m13', targets=['command_hq'], targetHealth=0.8, timeLimit=1500, replay=True,
              general='sen', reinforcements=3,
              enemyAi='commander', enemyStance='Defend', difficulty='Easy', enemyCp=10, enemyIncome=0.9,
              enemyDeck=['main_battle_tank', 'heavy_tank', 'aa_vehicle', 'mortar_carrier', 'tank_destroyer', 'strike_drone'],
              waves=waves(['main_battle_tank', 'ifv', 'attack_helicopter', 'elite_mbt'], first=90, interval=75, size=2, grow=0.3, max_size=3, max_alive=10),
              playerCp=32, playerIncome=2.8, playerCap=48, starTime=780, starLosses=16),
            ('Molten Gate', 'Cổng Dung Nham'),
            ('The drone works are inside a fortress at the north end of the ridge. Break through the walls at night and level the command HQ.',
             'Xưởng drone nằm trong một pháo đài ở đầu bắc sườn núi. Phá tường trong đêm và san phẳng sở chỉ huy.'),
            (('The works', 'Xưởng máy'),
             ('Inside the drone works: 4,000 drones in crates, and one office with a camp bed. Venn had not been home in eight months.',
              'Bên trong xưởng drone: 4.000 chiếc drone còn trong thùng, và một văn phòng kê một chiếc giường gấp. Venn đã tám tháng không về nhà.')),
            [say('khai', 'Start', 'Walls first, then the HQ. The guns do the talking.', 'Tường trước, rồi tới sở chỉ huy. Để pháo nói chuyện.')])

add_mission(m('c5m07', 5, 'junglepass', 'ShootDown', 'Clear', killsNeeded=14, timeLimit=1200, general='sen',
              enemyAi='waves', difficulty='Normal', playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['strike_drone', 'strike_drone', 'attack_helicopter', 'recon_drone', 'ifv', 'main_battle_tank'], first=30, interval=42, size=3, grow=0.4, max_size=7, max_alive=14),
              starTime=600, starLosses=10),
            ('Clear the Canopy', 'Quét sạch tán rừng'),
            ('Venn\'s strike drones own the sky over the pass. Bring fourteen of them down, and the jungle belongs to the brigade again.',
             'Drone tấn công của Venn làm chủ bầu trời trên đèo. Bắn rơi mười bốn chiếc, và rừng lại thuộc về lữ đoàn.'),
            (('Birds', 'Chim chóc'),
             ('After the drones were gone, the birds came back to the pass within a week. Hawk claims they were waiting for him.',
              'Lũ drone biến mất được một tuần thì chim chóc quay về đèo. Hawk khẳng định chúng đợi anh.')),
            [say('dieuhau', 'Start', 'Drones, lots of them. Keep the anti-air moving under the trees.', 'Drone, nhiều lắm. Cho phòng không di chuyển liên tục dưới tán cây.')])

add_mission(m('c5m08', 5, 'emberridge', 'Protect', 'Overcast', reversed=True, targets=['storage_tank'], protectNeeded=1, targetHealth=14, surviveSeconds=420,
              general='sen', reinforcements=2,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.85, enemyDeck=SEN,
              playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['strike_drone', 'fpv_carrier', 'ifv', 'main_battle_tank'], first=90, interval=65, size=2, grow=0.3, max_size=4, max_alive=10),
              starTime=0, starLosses=10, challenge={'kind': 'NoAircraft'}),
            ('Keep the Lights On', 'Giữ đèn sáng'),
            ('The geothermal plant\'s steam tanks power the whole brigade now. Venn\'s drones are coming for them from the south. Keep at least one standing for seven minutes.',
             'Các bồn hơi của nhà máy địa nhiệt giờ cấp điện cho cả lữ đoàn. Drone của Venn đang lao tới từ phía nam. Giữ ít nhất một bồn đứng vững trong bảy phút.'),
            (('A message', 'Một bức điện'),
             ('Intercepted, from Venn to Aurel: "The plant is a civilian power source. I will not strike it." Aurel\'s reply: "Then someone else will." Someone else did.',
              'Chặn thu được, Venn gửi Aurel: "Nhà máy là nguồn điện dân sự. Tôi sẽ không đánh nó." Aurel trả lời: "Vậy sẽ có người khác đánh." Và đã có người khác đánh.')),
            [say('linh', 'Start', 'These drones are not Venn\'s launch codes. Aurel is running them himself.', 'Những drone này không dùng mã phóng của Venn. Aurel đang tự điều khiển chúng.')])

add_mission(m('c5m09', 5, 'junglepass', 'Duel', 'Night', targetHealth=0.4, general='sen', enemyBase='Target', enemyHq=2, replay=True, reinforcements=3, timeLimit=1500,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=11, enemyIncome=0.56,
              playerCp=30, playerIncome=2.3, playerCap=40, playerBase='Anchor', unlocks=['fighter_jet', 'wingman_drone'], starTime=900, starLosses=14),
            ('The Hangars of the Pass', 'Những nhà chứa trên đèo'),
            ('Venn\'s field headquarters is ringed with drone hangars and jammers. Break it at night and level her HQ. Nadia thinks she may not fight to the end.',
             'Sở chỉ huy dã chiến của Venn được bao quanh bởi những nhà chứa drone và xe gây nhiễu. Phá nó trong đêm và san phẳng sở chỉ huy. Nadia nghĩ bà ấy có thể sẽ không đánh tới cùng.'),
            (('An open channel', 'Một kênh mở'),
             ('Venn\'s last message before her HQ fell, on an open channel: "Colonel, if we meet, I would like to talk. Not about drones." Kade did not answer. He kept the recording.',
              'Bức điện cuối của Venn trước khi sở chỉ huy thất thủ, trên kênh mở: "Đại tá, nếu ta gặp nhau, tôi muốn nói chuyện. Không phải về drone." Kade không trả lời. Ông giữ lại bản ghi âm.')),
            [say('sen', 'Start', 'I designed this to save people. Remember that when it kills you.', 'Tôi thiết kế thứ này để cứu người. Hãy nhớ điều đó khi nó giết các anh.'),
             say('sen', 'Win', 'Enough.', 'Đủ rồi.')])

add_mission(m('c5m10', 5, 'emberridge', 'Capture', 'Storm', legacy='m15', operation=True, general='sen', reinforcements=3,
              playArea={'minX': -146, 'minZ': -146, 'maxX': 146, 'maxZ': 146},
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.95, enemyDeck=SEN,
              playerCp=30, playerIncome=1.7, playerCap=42, playerBase='Anchor',
              waves=waves(['strike_drone', 'fpv_carrier', 'ifv', 'main_battle_tank', 'attack_helicopter'], first=90, interval=65, size=2, grow=0.3, max_size=5, max_alive=12),
              unlocks=['drone_hangar'],
              stages=[
                  {'stage': 'causeways', 'goal': 'Capture', 'points': ['west', 'east'], 'enemyOwns': ['west', 'town', 'east'], 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c5m10.s1'}],
                   'choices': [{'key': 'fuel', 'next': 'fuel'}, {'key': 'relay', 'next': 'relay'}]},
                  {'stage': 'fuel', 'goal': 'Destroy', 'targets': ['storage_tank'], 'targetX': 36, 'targetZ': 20, 'targetRadius': 36, 'targetHealth': 2, 'cp': 6, 'next': 'plant',
                   'events': WEAKEN},
                  {'stage': 'relay', 'goal': 'Survive', 'points': ['town'], 'enemyOwns': [], 'surviveSeconds': 120, 'cp': 6, 'next': 'plant', 'events': strikes(55)},
                  {'stage': 'plant', 'goal': 'Survive', 'points': ['town'], 'surviveSeconds': 300, 'cp': 8,
                   'events': [{'at': '40', 'kind': 'Reinforce', 'team': 1, 'units': ['ifv', 'main_battle_tank', 'fpv_carrier']}]},
                  {'stage': 'swarm', 'goal': 'Survive', 'surviveSeconds': 480, 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.sen.c5m10.s3'},
                              {'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['strike_drone', 'strike_drone', 'fpv_carrier', 'ifv']},
                              {'at': '110', 'kind': 'Reinforce', 'team': 1, 'units': ['strike_drone', 'lancet_truck', 'main_battle_tank', 'ew_jammer']}]},
                  {'stage': 'mothership', 'goal': 'Boss', 'boss': scripted('drone_mothership', (84, 84), heading=225, health=1.6),
                   'events': [{'at': 'end', 'kind': 'Radio', 'key': 'radio.sen.c5m10.end'}]},
              ],
              starTime=1380, starLosses=18),
            ('The Mothership', 'Tàu mẹ'),
            ('The Hive\'s mothership is over Emberridge, feeding swarms to every Hegemon unit in the jungle. Take the causeways, choose your next blow, '
             'survive the swarm it throws at you, then bring the mothership down.',
             'Tàu mẹ của Hive đang lơ lửng trên Emberridge, tiếp bầy drone cho mọi đơn vị Hegemon trong rừng. Chiếm các đường đắp, chọn đòn kế tiếp, '
             'trụ vững trước bầy drone nó tung ra, rồi bắn rơi tàu mẹ.'),
            (('Venn', 'Venn'),
             ('Dr Venn walked out of the burning works with her hands up and a hard drive in each. "Icarus," she said. "You need to see this. Now."',
              'Tiến sĩ Venn bước ra khỏi xưởng đang cháy, hai tay giơ cao, mỗi tay cầm một ổ cứng. "Icarus," bà nói. "Các anh cần xem cái này. Ngay bây giờ."')),
            [say('khai', 'Start', 'The mothership falls today. Everything else is on the way to it.', 'Hôm nay tàu mẹ phải rơi. Mọi thứ khác chỉ là đường tới nó.'),
             say('khai', 'Win', 'Venn is surrendering, Colonel? ...Bring her in. Carefully.', 'Venn ra hàng à? ...Đưa bà ấy về. Cẩn thận.')],
            stages_text={'causeways': ('The Causeways', 'Các đường đắp'), 'fuel': ('Burn the Drone Fuel', 'Đốt nhiên liệu drone'), 'relay': ('Hold the Relay', 'Giữ trạm tiếp sóng'),
                         'plant': ('Hold the Geothermal Plant', 'Giữ nhà máy địa nhiệt'), 'swarm': ('The Swarm', 'Bầy drone'), 'mothership': ('The Mothership', 'Tàu mẹ')},
            choices_text={'fuel': choice_income('Burn the drone fuel', 'Đốt nhiên liệu drone', 'Venn\'s army', 'Quân của Venn'),
                          'relay': choice_strikes('Hold the relay (120 s)', 'Giữ trạm tiếp sóng (120 giây)', 55)})
T('radio.khai.c5m10.s1', 'The causeways first. They are the only roads over the lava.', 'Các đường đắp trước. Đó là những con đường duy nhất vượt qua dung nham.')
T('radio.sen.c5m10.s3', 'Aurel has taken the swarm from me. I cannot stop it. Survive it.', 'Aurel đã lấy bầy drone khỏi tay tôi. Tôi không dừng nó được. Hãy trụ vững.')
T('radio.sen.c5m10.end', 'Colonel. This is Venn. I am coming out. Do not shoot.', 'Đại tá. Venn đây. Tôi đang đi ra. Đừng bắn.')

add_mission(m('c5s1', 5, 'junglepass', 'Recon', 'Overcast', side=True, after='c5m03', speaker='linh', points=['west', 'town', 'east'], timeLimit=900, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.85, enemyDeck=SEN,
              playerCp=26, playerIncome=1.4, playerCap=36, rarePrints=34, starTime=420, starLosses=8),
            ('Venn\'s Laboratory', 'Phòng thí nghiệm của Venn'),
            ('Somewhere in the pass Venn keeps a laboratory off Hegemon\'s books. Nadia wants to find it first. Look at all three objectives.',
             'Đâu đó trên đèo, Venn có một phòng thí nghiệm không có trong sổ sách của Hegemon. Nadia muốn tìm ra nó trước. Quan sát cả ba cứ điểm.'),
            (('The second lab', 'Phòng thí nghiệm thứ hai'),
             ('In Venn\'s hidden lab: rescue drones, painted orange, with medical kits in their bays. Hundreds of them, never armed. She had been building the Hive she wanted.',
              'Trong phòng thí nghiệm bí mật của Venn: drone cứu hộ, sơn màu cam, trong khoang chứa túi cứu thương. Hàng trăm chiếc, chưa bao giờ gắn vũ khí. Bà vẫn đang chế tạo Hive mà bà mong muốn.')),
            [say('linh', 'Start', 'Look for anything painted orange.', 'Tìm bất cứ thứ gì sơn màu cam.')])

add_mission(m('c5s2', 5, 'emberridge', 'Relieve', 'Fog', targetHealth=3.0, side=True, after='c5m07', speaker='linh', reinforcements=2, timeLimit=1000,
              ally={'x': -60, 'z': -20, 'hq': 'headquarters', 'structures': units(0, ['mg_bunker', 'gun_turret', 'aa_turret'], (-60, -20), 14),
                    'units': units(0, ['ifv', 'light_tank'], (-66, -26), 4)},
              hunt=[scripted(d, p) for d, p in zip(['main_battle_tank', 'fpv_carrier', 'ifv', 'strike_drone', 'mortar_carrier', 'main_battle_tank'], ring((-60, -20), 40, 6, 0.4))],
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.75, enemyDeck=SEN,
              playerCp=28, playerIncome=1.5, playerCap=36, playerBase='Anchor',
              waves=waves(['strike_drone', 'ifv', 'fpv_carrier'], first=70, interval=60, size=2, grow=0.3, max_size=4, max_alive=12, spawns=[(40, 60), (80, 20)]),
              towerGear='Epic', starTime=480, starLosses=8),
            ('The Charcoal Burners', 'Làng đốt than'),
            ('The charcoal burners of the ridge have held out against Hegemon for two years in a fortified camp. Now they are ringed. Break the ring; the besiegers are marked.',
             'Dân đốt than trên sườn núi đã cầm cự với Hegemon suốt hai năm trong một trại có rào lũy. Giờ họ bị vây kín. Phá vòng vây; quân vây được đánh dấu.'),
            (('Charcoal', 'Than củi'),
             ('The burners paid the brigade in charcoal. Mara used it in the base forge for a month and said it was the best she had ever worked with.',
              'Dân đốt than trả công lữ đoàn bằng than củi. Mara dùng nó trong lò rèn của căn cứ suốt một tháng và bảo đó là loại than tốt nhất cô từng dùng.')),
            [say('linh', 'Start', 'They held for two years. Their HQ cannot hold much longer.', 'Họ giữ được hai năm. Sở chỉ huy của họ không trụ được lâu nữa đâu.')])

# ================================================================================ CHAPTER 6: COUNTERSTRIKE

add_mission(m('c6m01', 6, 'ashfield', 'Protect', 'Storm', variant='siege', reversed=True, targets=['command_hq'], protectNeeded=1, targetHealth=2.5, surviveSeconds=480,
              general='varga', replay=True, reinforcements=3,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=14, enemyIncome=1.0, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.5, playerCap=40,
              waves=waves(['main_battle_tank', 'heavy_tank', 'ifv', 'mlrs', 'flame_tank'], first=60, interval=55, size=3, grow=0.4, max_size=6, max_alive=16,
                          spawns=[(20, 60), (60, 20), (40, 40)]),
              starTime=0, starLosses=16),
            ('Ashfield Under Fire', 'Ashfield rực lửa'),
            ('Hegemon strikes back where we first won. Varga is throwing his armour at the Ashfield fortress, ours now, towers and all. '
             'Keep its command HQ standing for eight minutes.',
             'Hegemon phản đòn đúng nơi ta giành chiến thắng đầu tiên. Varga đang tung thiết giáp vào pháo đài Ashfield, giờ là của ta, cả tháp lẫn tường. '
             'Giữ sở chỉ huy của nó đứng vững trong tám phút.'),
            (('The kilns again', 'Lại là lò nung'),
             ('The fortress\'s old kilns held again, this time for us. Mara had reinforced them with the Bastion\'s own plates. "Recycling," she called it.',
              'Những lò nung cũ của pháo đài lại trụ vững, lần này là cho ta. Mara đã gia cố chúng bằng chính những tấm giáp của Bastion. Cô gọi đó là "tái chế".')),
            [say('varga', 'Start', 'You took my fortress. I have come to collect it.', 'Ngươi lấy pháo đài của ta. Ta tới lấy lại đây.'),
             say('khai', 'Start', 'It was never yours. Hold the walls.', 'Nó chưa bao giờ là của ngươi. Giữ tường thành.')])

add_mission(m('c6m02', 6, 'whiteout', 'Evacuate', 'Snow', reversed=True, convoyCount=8, convoyNeeded=5, convoyInterval=18, timeLimit=900, general='varga', reinforcements=2,
              convoy=scripted('supply_truck', (0, 0), route=[(-33, -33), (-53, -53), (-84.8, -74.2), (-108, -100)], heading=225),
              units=units(0, ['main_battle_tank', 'heavy_aa', 'tank_destroyer', 'ifv'], (-6, -6), 8),
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=12, enemyIncome=0.9, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.5, playerCap=38, playerBase='Anchor',
              waves=waves(['main_battle_tank', 'ifv', 'flame_tank', 'mortar_carrier'], first=50, interval=50, size=2, grow=0.35, max_size=5, max_alive=12,
                          spawns=[(80, 60), (40, 100), (100, 10)]),
              unlocks=['armored_bulldozer', 'c_ram', 'bunker_vehicle'], starTime=600, starLosses=10),
            ('Evacuate Whiteout', 'Sơ tán Whiteout Pass'),
            ('Varga\'s counterstrike is pouring over the pass. The villagers at the frozen lake have to get out: six trucks, one every few seconds, down the road to our camp. '
             'Hold the lake until the last one leaves, then cover the road. Four must get through.',
             'Đợt phản công của Varga đang tràn qua đèo. Dân làng ở hồ băng phải rời đi: sáu xe tải, cứ vài giây một chiếc, theo đường về trại của ta. '
             'Giữ hồ cho tới khi xe cuối cùng rời đi, rồi yểm trợ con đường. Phải thoát được bốn xe.'),
            (('The last truck', 'Chiếc xe cuối cùng'),
             ('The last truck out of Whiteout carried the church bell of the village in the valley. The priest would not leave without it. Nobody argued.',
              'Chiếc xe cuối cùng rời Whiteout Pass chở theo quả chuông nhà thờ của ngôi làng dưới thung lũng. Cha xứ không chịu đi nếu không có nó. Chẳng ai cãi.')),
            [say('khai', 'Start', 'Nobody is left behind. Hold the lake.', 'Không bỏ lại ai. Giữ hồ băng.'),
             say('linh', 'At', 'Half the trucks are out. Varga is pushing harder.', 'Một nửa số xe đã thoát. Varga đang dồn ép mạnh hơn.', at=80)])

add_mission(m('c6m03', 6, 'ashfield', 'Escort', 'Clear', reversed=True, convoyCount=1, convoyNeeded=1, timeLimit=1100, speaker='mai', general='varga', reinforcements=3,
              convoy=scripted('behemoth', (-100, -100), route=[(-78.75, -78.75), (-31.9, -31.9), (0, 0), (31.9, 31.9), (78.75, 78.75)], heading=45, health=4.0),
              units=units(0, ['main_battle_tank', 'tank_destroyer', 'heavy_aa', 'ifv'], (-88, -80), 7),
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=12, enemyIncome=0.9, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.5, playerCap=38, playerBase='Anchor',
              waves=waves(['tank_destroyer', 'fpv_carrier', 'main_battle_tank', 'attack_helicopter'], first=40, interval=45, size=2, grow=0.35, max_size=5, max_alive=12,
                          spawns=[(60, 90), (90, 60), (100, 100)]),
              unlocks=['ew_tower', 'shield_carrier'], starTime=660, starLosses=10, challenge={'kind': 'Kills', 'value': 25}),
            ('Our Behemoth', 'Behemoth của ta'),
            ('Mara has done it: the Behemoth from the Ashfield yard runs, and it is ours. Escort it from the fortress across Ashfield to the front. '
             'Varga will do anything to stop his own machine.',
             'Mara đã làm được: chiếc Behemoth trong sân pháo đài Ashfield đã chạy, và nó là của ta. Hộ tống nó từ Jötunn qua Ashfield ra tiền tuyến. '
             'Varga sẽ làm mọi cách để chặn chính cỗ máy của hắn.'),
            (('Mara\'s Behemoth', 'Behemoth của Mara'),
             ('Mara named the captured Behemoth "Matilda" (the Old Lady). Its crew painted a flower on the rear plates, over the weld she had never told anyone about.',
              'Mara đặt tên chiếc Behemoth bắt được là "Matilda". Kíp lái vẽ một bông hoa lên tấm giáp sau, đè lên đường hàn cô chưa từng kể với ai.')),
            [say('mai', 'Start', 'She runs, Colonel. Slowly, loudly, but she runs. Keep her in one piece.', 'Nó chạy rồi, đại tá. Chậm, ồn, nhưng chạy được. Giữ cho nó nguyên vẹn.'),
             say('varga', 'Start', 'That is MY machine! Burn it!', 'Đó là cỗ máy của TA! Đốt nó đi!'),
             say('mai', 'Win', 'She made it. I may cry. Do not tell anyone.', 'Nó tới nơi rồi. Chắc tôi khóc mất. Đừng kể với ai nhé.')])

add_mission(m('c6m04', 6, 'hydrodam', 'Capture', 'Rain', points=['west', 'town', 'east'], enemyOwns=['west'], general='varga', reinforcements=3,
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=15, enemyIncome=0.95, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.55, playerCap=38, playerBase='Anchor', unlocks=['scout_heli'], starTime=660, starLosses=12),
            ('The Dam Valley', 'Thung lũng con đập'),
            ('Varga is making for the Hollow Dam that lights half the coast. Get there first: the power station, the road bridge and the ford.',
             'Varga đang nhắm tới Hollow Dam, nơi thắp sáng nửa Meridian Coast. Tới đó trước hắn: trạm phát điện, cầu đường bộ và bến lội.'),
            (('Half the coast', 'Nửa Meridian Coast'),
             ('The Hollow Dam\'s turbines light every town from Greenvale to Ironport. When Hegemon took the coast, the dam was the only thing its engineers asked to keep running.',
              'Tua-bin của Hollow Dam thắp sáng mọi thị trấn từ Greenvale tới Ironport. Khi Hegemon chiếm Meridian Coast, con đập là thứ duy nhất các kỹ sư của chúng xin được giữ cho chạy.')),
            [say('linh', 'Start', 'Varga\'s scouts are at the power station already.', 'Trinh sát của Varga đã tới trạm phát điện rồi.')])

add_mission(m('c10m08', 10, 'whiteout', 'Boss', 'Night', reversed=True, general='varga', timeLimit=1200, reinforcements=3,
              boss=scripted('sky_fortress', (84, 84), heading=225, route=[(50, 50), (-30, 40), (-40, -30), (30, -40)], health=3.5),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=13, enemyIncome=0.9,
              enemyDeck=['main_battle_tank', 'heavy_tank', 'ifv', 'aa_vehicle', 'mlrs', 'tank_destroyer'],
              playerCp=30, playerIncome=1.55, playerCap=40, playerBase='Anchor', starTime=780, starLosses=12),
            ('Spectre', 'Bóng ma Spectre'),
            ('Something is circling high over the pass at night, and every time it passes, a tank burns. Spectre: a gunship that never comes low. '
             'Only anti-air and fighters can reach it. Bring it down.',
             'Có thứ gì đó bay vòng trên cao trên đèo trong đêm, và mỗi lần nó lướt qua là một chiếc xe tăng bốc cháy. Spectre: pháo hạm bay không bao giờ hạ thấp. '
             'Chỉ phòng không và tiêm kích với tới nó. Bắn rơi nó.'),
            (('The ghost', 'Bóng ma'),
             ('Spectre\'s crew called themselves "the Ghosts" and never landed at the same base twice. They landed once more, in pieces, on the frozen lake.',
              'Kíp lái Spectre tự gọi mình là "những Bóng Ma" và không bao giờ hạ cánh hai lần ở cùng một căn cứ. Chúng đã hạ cánh thêm một lần nữa, thành từng mảnh, trên hồ băng.')),
            [say('dieuhau', 'Start', 'It flies above my ceiling at night. The SAMs will have to do this one.', 'Ban đêm nó bay cao hơn trần bay của tôi. Lần này phải nhờ tên lửa phòng không rồi.'),
             say('dieuhau', 'Win', 'The ghost is down. Sleep well tonight, everyone.', 'Bóng ma rơi rồi. Đêm nay mọi người ngủ ngon nhé.')])

add_mission(m('c6m06', 6, 'hydrodam', 'Hold', 'Fog', points=['town'], holdSeconds=240, general='varga', reinforcements=3,
              units=units(0, ['main_battle_tank', 'heavy_tank', 'tank_destroyer', 'heavy_aa', 'mlrs'], (-6, -8), 8),
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.9, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.4, playerCap=42, playerBase='Anchor',
              waves=waves(['main_battle_tank', 'ifv', 'flame_tank', 'mortar_carrier', 'twin_tank'], first=40, interval=45, size=2, grow=0.35, max_size=5, max_alive=12),
              unlocks=['lancet_truck'], starTime=0, starLosses=12),
            ('Hold the Bridge', 'Giữ cây cầu'),
            ('The road bridge below the dam is the only way across for heavy armour. Hold it in the fog for four minutes. The bridge must not fall into Varga\'s hands.',
             'Cây cầu đường bộ dưới chân đập là lối duy nhất cho thiết giáp hạng nặng vượt sông. Giữ nó trong sương mù bốn phút. Không được để cây cầu rơi vào tay Varga.'),
            (('The bridge', 'Cây cầu'),
             ('The bridge was built in 1962 and rated for thirty tons. The brigade ran sixty-ton tanks across it all day. Mara does not want to talk about it.',
              'Cây cầu xây năm 1962, thiết kế chịu tải ba mươi tấn. Lữ đoàn cho xe tăng sáu mươi tấn chạy qua cả ngày. Mara không muốn nhắc tới chuyện đó.')),
            [say('khai', 'Start', 'The bridge, four minutes. Nobody crosses.', 'Cây cầu, bốn phút. Không ai được qua.')])

add_mission(m('c6m07', 6, 'ashfield', 'Relieve', 'Overcast', targetHealth=3.0, reversed=True, reinforcements=3, timeLimit=1000, general='varga',
              ally={'x': 0, 'z': 0, 'hq': 'headquarters', 'structures': units(0, ['mg_bunker', 'gun_turret', 'aa_turret', 'guard_tower'], (0, 0), 15),
                    'units': units(0, ['ifv', 'main_battle_tank'], (-6, -6), 4)},
              hunt=[scripted(d, p) for d, p in zip(['heavy_tank', 'tank_destroyer', 'main_battle_tank', 'mlrs', 'ifv', 'flame_tank', 'main_battle_tank'], ring((0, 0), 40, 7, 0.2))],
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.85, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.5, playerCap=38, playerBase='Anchor',
              waves=waves(['main_battle_tank', 'ifv', 'mortar_carrier', 'tank_destroyer'], first=70, interval=60, size=2, grow=0.3, max_size=4, max_alive=12, spawns=[(60, 80), (80, 30)]),
              starTime=540, starLosses=10),
            ('The Town Garrison', 'Đồn thị trấn'),
            ('Varga has ringed Ashfield town, where the Accord militia keep their HQ. Break the ring before it falls; the besiegers are marked.',
             'Varga đã vây kín thị trấn Ashfield, nơi dân quân Accord đặt sở chỉ huy. Phá vòng vây trước khi nó thất thủ; quân vây được đánh dấu.'),
            (('Bricks', 'Gạch'),
             ('The militia had rebuilt the town square with bricks from the old kilns. Varga\'s guns knocked half of it down. They started rebuilding before the smoke cleared.',
              'Dân quân đã xây lại quảng trường bằng gạch từ những lò nung cũ. Pháo của Varga bắn sập một nửa. Khói chưa tan, họ đã bắt đầu xây lại.')),
            [say('khai', 'Start', 'Break the ring. Their HQ first, everything else second.', 'Phá vòng vây. Sở chỉ huy của họ trước tiên, mọi thứ khác tính sau.')])

add_mission(m('c8m05', 8, 'hydrodam', 'Intercept', 'Night', timeLimit=1200, general='varga', reinforcements=3,
              boss=scripted('earth_borer', (100, 60), heading=270, route=[(60, 40), (20, 50), (-20, 60), (-40, 64)], fallback='behemoth', fallbackHealth=1.4, name='earth_borer'),
              units=units(0, ['heavy_tank', 'tank_destroyer', 'fpv_carrier', 'main_battle_tank'], (-50, 20), 8),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=13, enemyIncome=0.9, enemyDeck=VARGA_LATE,
              playerCp=30, playerIncome=1.5, playerCap=40, playerBase='Anchor', starTime=600, starLosses=10, challenge={'kind': 'NoStrikes'}),
            ('Tartarus', 'Tartarus'),
            ('Varga\'s tunnelling machine is grinding under the valley towards the power station. If it gets there, the dam loses its heart. Stop it on the way.',
             'Cỗ máy khoan của Varga đang nghiến xuyên dưới thung lũng hướng về trạm phát điện. Nó mà tới nơi, con đập mất trái tim. Chặn nó giữa đường.'),
            (('The earthworm', 'Con giun đất'),
             ('Tartarus was built to dig mines. Varga fitted it with guns and a battering head. Its original crew, miners from Red Rock, refused to drive it. He found another crew.',
              'Tartarus được chế tạo để đào mỏ. Varga gắn thêm pháo và một đầu húc. Kíp lái cũ, thợ mỏ ở Red Rock, từ chối lái nó. Hắn tìm kíp khác.')),
            [say('linh', 'Start', 'Seismic contact under the valley, moving west. That is Tartarus.', 'Tín hiệu địa chấn dưới thung lũng, đang di chuyển về phía tây. Đó là Tartarus.'),
             say('mai', 'Boss', 'Hit it when it surfaces. The drill head is armour; the back is not.', 'Đánh nó khi nó trồi lên. Đầu khoan là giáp; phía sau thì không.')])

add_mission(m('c6m09', 6, 'whiteout', 'Duel', 'Fog', targetHealth=0.3, reversed=True, general='varga', enemyBase='Target', enemyHq=2, replay=True, reinforcements=1, timeLimit=1800,
              units=units(0, ['artillery', 'artillery', 'mlrs'], (-86, -86), 6), enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=11, enemyIncome=0.35,
              playerCp=30, playerIncome=2.35, playerCap=40, playerBase='Anchor', starTime=900, starLosses=14),
            ('Varga\'s Winter Camp', 'Trại mùa đông của Varga'),
            ('Varga has made his winter camp in the south of the pass, in our old positions, and dug in every anti-tank gun he has. Level his HQ, and his counterstrike has no head.',
             'Varga dựng trại mùa đông ở phía nam đèo, ngay trên các vị trí cũ của ta, và đào sẵn mọi khẩu pháo chống tăng hắn có. San phẳng sở chỉ huy, đợt phản công của hắn sẽ mất đầu.'),
            (('Two tanks for one', 'Hai đổi một'),
             ('Varga\'s supply officer, captured at the camp: "He said he would build two tanks for every one you burned. He stopped saying it in November."',
              'Sĩ quan hậu cần của Varga, bị bắt tại trại: "Ông ấy nói cứ ta mất một chiếc là ông ấy đóng hai. Ông ấy thôi nói câu đó từ tháng Mười Một."')),
            [say('varga', 'Start', 'Every tank you burn, I build two.', 'Ngươi đốt một chiếc, ta đóng hai chiếc.'),
             say('varga', 'Win', 'Fall back to the dam. Moloch will finish this.', 'Rút về con đập. Moloch sẽ kết thúc chuyện này.')])

add_mission(m('c6m10', 6, 'hydrodam', 'Hold', 'Storm', operation=True, replay=True, general='varga', reinforcements=3,
              playArea={'minX': -146, 'minZ': -146, 'maxX': 146, 'maxZ': 146},
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=15, enemyIncome=1.0, enemyDeck=VARGA_LATE,
              playerCp=30, playerIncome=1.7, playerCap=44, playerBase='Defend', towerGear='Epic',
              waves=waves(['main_battle_tank', 'heavy_tank', 'ifv', 'twin_tank', 'mlrs', 'flame_tank'], first=60, interval=55, size=3, grow=0.4, max_size=6, max_alive=16),
              ally={'x': -100, 'z': -60, 'heading': 45},
              stages=[
                  {'stage': 'crest', 'goal': 'Survive', 'points': ['town'], 'surviveSeconds': 240, 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c6m10.s1'}],
                   'choices': [{'key': 'spillway', 'next': 'spillway'}, {'key': 'station', 'next': 'station'}]},
                  {'stage': 'spillway', 'goal': 'Destroy', 'targets': ['fuel_bladder', 'barn', 'cottage'], 'targetX': 60, 'targetZ': -100, 'targetRadius': 45, 'targetHealth': 2, 'cp': 6,
                   'next': 'monster', 'events': WEAKEN},
                  {'stage': 'station', 'goal': 'Survive', 'points': ['west'], 'surviveSeconds': 150, 'cp': 6, 'next': 'monster', 'events': strikes(55)},
                  {'stage': 'monster', 'goal': 'Boss', 'boss': scripted('behemoth', (90, 90), heading=225, route=[(50, 40), (10, 10), (-20, -20)], health=3.0, name='frost_monster'), 'cp': 10,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.varga.c6m10.s3'}]},
                  {'stage': 'relief', 'goal': 'Survive', 'surviveSeconds': 360,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.hung.c6m10.s4'},
                              {'at': '40', 'kind': 'AllyReinforce', 'units': ['main_battle_tank', 'main_battle_tank', 'ifv', 'aa_vehicle']},
                              {'at': '60', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'twin_tank', 'mlrs', 'flame_tank']},
                              {'at': '120', 'kind': 'AllyReinforce', 'units': ['heavy_tank', 'tank_destroyer', 'mlrs', 'heavy_aa']}]},
              ],
              starTime=1440, starLosses=20),
            ('Defend the Dam', 'Bảo vệ con đập'),
            ('Varga\'s last card is Moloch, a Behemoth bigger than any before, and it is coming for the dam. The brigade must hold the crest, choose its blow, '
             'kill the monster, and hold until General Thorne\'s relief army arrives. The base here must not fall.',
             'Lá bài cuối của Varga là Moloch, chiếc Behemoth lớn hơn mọi chiếc trước đó, và nó đang tiến về con đập. Lữ đoàn phải giữ mặt đập, chọn đòn đánh, '
             'hạ con quái vật, và trụ cho tới khi đạo quân cứu viện của tướng Thorne tới nơi. Căn cứ ở đây không được thất thủ.'),
            (('Relief', 'Cứu viện'),
             ('General Thorne\'s first words on arrival, broadcast to his whole army: "The Northern Army has saved the dam." Colonel Kade\'s staff heard it too. Nobody said anything.',
              'Câu đầu tiên của tướng Thorne khi tới nơi, phát cho toàn quân của ông: "Tập đoàn quân Phương Bắc đã cứu con đập." Ban tham mưu của đại tá Kade cũng nghe thấy. Không ai nói gì.')),
            [say('khai', 'Start', 'The dam, the base, the monster. In that order. Hold.', 'Con đập, căn cứ, con quái vật. Theo đúng thứ tự đó. Trụ vững.'),
             say('khai', 'Win', 'The dam holds. Act two is done, Brigade.', 'Con đập trụ vững. Hồi thứ hai khép lại rồi, Lữ đoàn.')],
            stages_text={'crest': ('Hold the Crest', 'Giữ mặt đập'), 'spillway': ('Burn Varga\'s Depot', 'Đốt kho của Varga'), 'station': ('Hold the Power Station', 'Giữ trạm phát điện'),
                         'monster': ('Moloch', 'Moloch'), 'relief': ('Until Relief Arrives', 'Chờ cứu viện')},
            choices_text={'spillway': choice_income('Burn Varga\'s depot at the ford', 'Đốt kho của Varga ở bến lội', 'Varga', 'Varga'),
                          'station': choice_strikes('Hold the power station (150 s)', 'Giữ trạm phát điện (150 giây)', 55)})
T('radio.khai.c6m10.s1', 'The crest first. Whoever holds the dam holds the valley.', 'Mặt đập trước. Ai giữ con đập thì giữ cả thung lũng.')
T('radio.varga.c6m10.s3', 'Meet my masterpiece, Colonel.', 'Chào kiệt tác của ta đi, đại tá.')
T('radio.hung.c6m10.s4', 'Kade! Thorne here, the Northern Army is on the road. Hold on, we are coming.', 'Kade! Thorne đây, Tập đoàn quân Phương Bắc đang trên đường. Cố lên, chúng tôi đang tới.')

add_mission(m('c6s1', 6, 'ashfield', 'ShootDown', 'Night', side=True, reversed=True, after='c6m03', speaker='dieuhau', killsNeeded=14, timeLimit=1200,
              enemyAi='waves', difficulty='Normal', playerCp=28, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['attack_helicopter', 'gunship_heli', 'attack_jet', 'strike_drone', 'main_battle_tank'], first=30, interval=42, size=3, grow=0.4, max_size=6, max_alive=14),
              rarePrints=40, starTime=600, starLosses=10),
            ('Night Raiders', 'Không kích đêm'),
            ('Varga\'s night raiders are bombing the Ashfield fortress. Hawk wants fourteen of them down before dawn.',
             'Máy bay đột kích đêm của Varga đang ném bom pháo đài Ashfield. Hawk muốn bắn rơi mười bốn chiếc trước bình minh.'),
            (('Dawn', 'Bình minh'),
             ('At dawn Hawk counted the wrecks from the air, then landed and counted them again on foot. Fourteen, both times. He bought the anti-air crews breakfast.',
              'Lúc bình minh, Hawk đếm xác máy bay từ trên không, rồi hạ cánh đi bộ đếm lại. Cả hai lần đều mười bốn. Anh khao các kíp phòng không bữa sáng.')),
            [say('dieuhau', 'Start', 'They come in low from the north. Let them.', 'Chúng bay thấp tới từ phía bắc. Cứ để chúng tới.')])

add_mission(m('c6s2', 6, 'hydrodam', 'Recon', 'Clear', side=True, after='c6m06', speaker='linh', points=['west', 'town', 'east'], timeLimit=900, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.9, enemyDeck=VARGA_LATE,
              playerCp=28, playerIncome=1.45, playerCap=36, towerGear='Epic', starTime=420, starLosses=8, challenge={'kind': 'NoAircraft'}),
            ('Survey the Dam', 'Khảo sát con đập'),
            ('Mara needs to know whether the dam will hold a siege. Get a vehicle onto the power station, the bridge and the ford, and let her engineers look.',
             'Mara cần biết con đập có chịu nổi một trận vây hãm hay không. Đưa xe tới trạm phát điện, cây cầu và bến lội để công binh của cô quan sát.'),
            (('Cracks', 'Vết nứt'),
             ('The engineers found three cracks in the dam, all old, all repaired by Hegemon\'s own crews. "They cared about this dam," Mara said. "That makes two of us."',
              'Công binh tìm thấy ba vết nứt trên thân đập, đều cũ, đều đã được chính người của Hegemon sửa. "Họ quý con đập này," Mara nói. "Vậy là có hai bên cùng quý nó."')),
            [say('linh', 'Start', 'Three looks for the engineers. Quickly, Varga is not far.', 'Ba lần quan sát cho công binh. Nhanh lên, Varga không ở xa đâu.')])

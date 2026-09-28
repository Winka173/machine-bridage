"""Act I, The Landing: chapters 1-3 (Bãi Đổ Bộ, Greenvale, Ashfield; Dunebreak, Red Rock; Frostpeak, Whiteout)."""

from campaign_kit import (CAMP, ENEMY_CAMP, add_mission, area, pt, radio, ring, say, scripted, toward, turn, units, waves)

# Enemy forces of the act, by who commands them.
GARRISON = ['scout_jeep', 'armored_car', 'light_tank', 'rocket_technical', 'ifv']
GARRISON_HEAVY = ['armored_car', 'light_tank', 'ifv', 'main_battle_tank', 'mortar_carrier', 'rocket_technical']
VARGA = ['light_tank', 'main_battle_tank', 'ifv', 'tank_destroyer', 'flame_tank', 'heavy_tank']
VARGA_EARLY = ['armored_car', 'light_tank', 'main_battle_tank', 'ifv', 'tank_destroyer', 'mortar_carrier']
ORLOV = ['main_battle_tank', 'ifv', 'mlrs', 'artillery', 'mortar_carrier', 'sam_launcher', 'aa_vehicle', 'attack_helicopter']


def m(mid, chapter, map_, goal, weather, **kw):
    d = {'id': mid, 'chapter': chapter, 'map': map_, 'goal': goal, 'weather': weather}
    d.update(kw)
    return d


# ================================================================================ CHAPTER 1: COAST OF FIRE

add_mission(m('c1m01', 1, 'landingbeach', 'Capture', 'Clear', points=['east', 'town'], reinforcements=0,
              enemyAi='commander', enemyStance='Defend', difficulty='Easy', enemyCp=8, enemyIncome=0.45,
              enemyDeck=['scout_jeep', 'armored_car'], playerCp=22, playerIncome=1.3,
              tips=[{'at': 2, 'key': 'tip.auto'}, {'at': 9, 'key': 'tip.deploy'}, {'at': 16, 'key': 'tip.points'},
                    {'at': 24, 'key': 'tip.strike'}, {'at': 33, 'key': 'tip.select'}, {'at': 43, 'key': 'tip.counters'},
                    {'at': 54, 'key': 'tip.items'}],
              unlocks=['rocket_technical'], starTime=300, starLosses=4, challenge={'kind': 'Kills', 'value': 8}),
            ('Landfall', 'Đổ bộ'),
            ('The landing craft are on the sand. Take the beach and the draw above it before Hegemon\'s garrison wakes up. '
             'Your army fights on its own: you choose where it goes, what it brings and when the guns fire.',
             'Xuồng đổ bộ đã chạm cát. Chiếm bãi biển và con dốc phía trên trước khi đồn Hegemon kịp tỉnh ngủ. '
             'Quân ta tự chiến đấu: bạn chọn nơi đánh, mang theo gì và lúc nào pháo khai hỏa.'),
            (('The first boot on the sand', 'Dấu giày đầu tiên trên cát'),
             ('Brigade log, day one: 212 vehicles ashore by 06:40. Losses light. The coastal guns fired late and badly; somebody in Hegemon did not believe we would come.',
              'Nhật ký lữ đoàn, ngày thứ nhất: 212 xe lên bờ trước 06:40. Thiệt hại nhẹ. Pháo bờ biển bắn muộn và bắn tồi; có kẻ nào đó bên Hegemon đã không tin chúng ta dám tới.')),
            [say('khai', 'Start', 'Brigade, this is Khải. Off the sand and up the draw. Nobody stops on the beach.',
                 'Lữ đoàn, Khải đây. Rời bãi cát, lên dốc. Không ai được dừng lại trên bãi biển.'),
             say('dieuhau', 'Capture', 'Diều Hâu overhead. Beach exit is ours, I can see the whole bay from here!',
                 'Diều Hâu trên đầu các anh đây. Cửa ra bãi biển là của ta rồi, từ đây tôi thấy cả vịnh!', arg='east'),
             say('khai', 'Win', 'Beachhead secured. Now we find somewhere to build.', 'Đầu cầu đã an toàn. Giờ tìm chỗ dựng căn cứ.')])

add_mission(m('c1m02', 1, 'landingbeach', 'Destroy', 'Overcast', targets=['radar_station'], targetHealth=3, timeLimit=900, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Easy', enemyCp=10, enemyIncome=0.7,
              enemyDeck=GARRISON, playerCp=20, playerIncome=1.3,
              unlocks=['mortar_carrier'], starTime=420, challenge={'kind': 'NoStrikes'}),
            ('Blind the Coast', 'Bịt mắt bờ biển'),
            ('A radar on the bluffs is calling Hegemon\'s guns onto every landing craft still in the bay. '
             'Knock it down, and the boats behind us can come in unseen.',
             'Trạm radar trên vách đá đang gọi pháo Hegemon bắn vào từng chiếc xuồng còn trong vịnh. '
             'Hạ nó xuống, các đợt đổ bộ sau sẽ vào bờ mà không bị phát hiện.'),
            (('A coastal radar\'s last report', 'Bản tin cuối của trạm radar'),
             ('Recovered from the radar\'s log: "Contacts multiplying. Request confirmation from Director\'s office. Request confirmation. Request—" Nobody confirmed.',
              'Trích từ sổ trực của trạm radar: "Mục tiêu tăng lên liên tục. Đề nghị văn phòng Giám đốc xác nhận. Đề nghị xác nhận. Đề nghị—" Không ai xác nhận cả.')),
            [say('linh', 'Start', 'The radar is on the bluffs. Its crew changes shift every hour; we will not get a better window.',
                 'Radar nằm trên vách đá. Kíp trực đổi ca mỗi giờ; ta sẽ không có cơ hội nào tốt hơn đâu.'),
             say('khai', 'Win', 'Radar down. Tell the boats they can come in.', 'Radar đã sập. Báo các xuồng vào bờ được rồi.')])

add_mission(m('c1m03', 1, 'greenvale', 'Capture', 'Clear', legacy='m00', points=['west', 'town', 'east'], reinforcements=0,
              enemyAi='commander', enemyStance='Defend', difficulty='Easy', enemyCp=9, enemyIncome=0.55,
              enemyDeck=['scout_jeep', 'armored_car', 'light_tank'], playerCp=22, playerIncome=1.3,
              unlocks=['repair_drop'], starTime=360, starLosses=5),
            ('The Crossroads', 'Ngã tư Lũng Xanh'),
            ('Greenvale\'s crossroads village and its two farms command every road inland. A handful of scouts hold them. '
             'Take all three and the brigade has room to breathe.',
             'Làng ngã tư ở Lũng Xanh cùng hai trang trại kiểm soát mọi con đường vào nội địa. Chỉ vài xe trinh sát canh giữ. '
             'Chiếm cả ba, lữ đoàn sẽ có đất mà thở.'),
            (('Greenvale\'s farmers', 'Nông dân Lũng Xanh'),
             ('The farmers of Greenvale kept planting for two years under the Protectorate. When our tanks came up the road, an old man offered Colonel Khải a bag of rice and asked if we were staying.',
              'Nông dân Lũng Xanh vẫn cày cấy suốt hai năm dưới thời "Bảo hộ". Khi xe tăng ta lên đường làng, một cụ già đưa đại tá Khải một bao gạo và hỏi quân mình có ở lại không.')),
            [say('khai', 'Start', 'Three objectives, light resistance. Show me what the brigade can do.', 'Ba cứ điểm, địch kháng cự yếu. Cho tôi xem lữ đoàn làm được gì.'),
             say('linh', 'Capture', 'The crossroads is ours. Every road inland runs through here now.', 'Ngã tư là của ta. Giờ mọi con đường vào nội địa đều đi qua đây.', arg='town')])

add_mission(m('c1m04', 1, 'greenvale', 'Outpost', 'Overcast', points=['town'], holdSeconds=150, speaker='mai', reinforcements=1, timeLimit=1000,
              enemyAi='both', enemyStance='Attack', difficulty='Easy', enemyCp=8, enemyIncome=0.6,
              enemyDeck=GARRISON, playerCp=24, playerIncome=1.4,
              waves=waves(['armored_car', 'light_tank', 'rocket_technical'], first=60, interval=55, size=2, grow=0.3, max_size=4, max_alive=10,
                          spawns=[(90, 60), (60, 95), (100, 20)]),
              hqLevel=1, unlocks=['rocket_turret', 'repair_bay'], starTime=480, starLosses=6),
            ('First Outpost', 'Tiền đồn đầu tiên'),
            ('Mai wants the crossroads for a base. Take it, set up an outpost there, and keep it standing while her crews fly the towers in. '
             'Once it holds, the brigade has its first HQ on the coast.',
             'Mai muốn lấy ngã tư làm căn cứ. Chiếm nó, lập tiền đồn ở đó và giữ vững trong lúc đội của cô thả tháp xuống. '
             'Trụ được rồi, lữ đoàn sẽ có sở chỉ huy đầu tiên trên dải duyên hải.'),
            (('Mai\'s shopping list', 'Danh sách mua sắm của Mai'),
             ('Pinned to the first HQ\'s door: "Generators (4). Welding rods (all of them). Coffee (more than that). Do not touch the blue crates. — M."',
              'Dán trên cửa sở chỉ huy đầu tiên: "Máy phát điện (4). Que hàn (tất cả chỗ có). Cà phê (nhiều hơn thế). Không được đụng vào thùng màu xanh. — M."')),
            [say('mai', 'Start', 'Give me that crossroads and a few minutes of quiet, Colonel, and I will give you a base.',
                 'Cho tôi cái ngã tư đó và vài phút yên tĩnh, đại tá, tôi sẽ trả lại ông một căn cứ.'),
             say('mai', 'Capture', 'Ground is ours. Towers coming down, keep them off my crews!', 'Đất là của ta rồi. Tháp đang thả xuống, đừng để chúng đụng vào người của tôi!', arg='town'),
             say('mai', 'Win', 'It holds. Welcome to your new HQ, Colonel. The coffee is terrible.', 'Trụ được rồi. Chào mừng tới sở chỉ huy mới, đại tá. Cà phê dở tệ.')])

add_mission(m('c1m05', 1, 'landingbeach', 'Boss', 'Night', timeLimit=1140, reinforcements=2,
              boss=scripted('landing_hovercraft', pt('landingbeach', 'east'), route=[pt('landingbeach', 'east'), (20, -45), (0, 0), (45, -30)],
                            heading=315, fallback='mobile_fortress', fallbackHealth=0.5, name='hovercraft'),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.8,
              enemyDeck=GARRISON_HEAVY, playerCp=24, playerIncome=1.4, playerBase='Anchor',
              unlocks=['tank_destroyer'], starTime=600, starLosses=8),
            ('Iron Tide', 'Thủy triều thép'),
            ('Hegemon is landing behind us: a hovercraft is coming up the beach at night with a company of armour aboard. '
             'Destroy it before it can unload, or the beachhead is cut off.',
             'Hegemon đang đổ bộ sau lưng ta: một tàu đệm khí chở cả đại đội thiết giáp đang lao lên bãi biển trong đêm. '
             'Tiêu diệt nó trước khi nó kịp dỡ quân, nếu không đầu cầu sẽ bị cắt đứt.'),
            (('Counter-landing', 'Phản đổ bộ'),
             ('Hegemon order, captured: "Retake the beach by morning. Use the hovercraft. Do not use the word \'counterattack\' in reports to the Director."',
              'Mệnh lệnh Hegemon thu được: "Chiếm lại bãi biển trước sáng mai. Dùng tàu đệm khí. Không dùng từ \'phản công\' trong báo cáo gửi Giám đốc."')),
            [say('dieuhau', 'Start', 'Something big on the water, Colonel. Bigger than a boat, faster than a tank.',
                 'Có thứ gì to lắm trên mặt nước, đại tá. To hơn xuồng, nhanh hơn xe tăng.'),
             say('khai', 'Boss', 'There it is. Hit it before it reaches the draw.', 'Nó đây rồi. Đánh nó trước khi nó lên tới con dốc.'),
             say('khai', 'Win', 'The tide goes out for them tonight.', 'Đêm nay thủy triều rút về phía chúng.')])

add_mission(m('c1m06', 1, 'greenvale', 'Escort', 'Rain', convoyCount=5, convoyNeeded=3, reinforcements=1, timeLimit=1000,
              convoy=scripted('supply_truck', (-100, -100), route=[(-78.75, -78.75), (-78.75, 0), (0, 0), (0, 86.25), (-60, 86.25)], heading=45),
              units=units(0, ['light_tank', 'ifv', 'main_battle_tank'], (-90, -88), 5),
              enemyAi='waves', difficulty='Easy',
              waves=waves(['armored_car', 'rocket_technical', 'light_tank', 'ifv'], first=15, interval=28, size=2, grow=0.4, max_size=5, max_alive=11,
                          spawns=[(20, 110), (95, 40), (60, 90), (-10, 60)]),
              playerBase='Anchor', unlocks=['zu23_technical'], starTime=300, starLosses=5, challenge={'kind': 'Kills', 'value': 15}),
            ('Supply Line', 'Đường tiếp tế'),
            ('Fuel and shells for the forward units, five trucks in the rain. Get at least three to the west farm. '
             'The trucks wait for an escort; they will not drive into an ambush alone.',
             'Nhiên liệu và đạn cho các đơn vị tiền phương, năm xe tải dưới mưa. Đưa ít nhất ba xe tới trang trại phía tây. '
             'Xe tải sẽ chờ hộ tống; chúng không tự lao vào ổ phục kích đâu.'),
            (('Rain', 'Mưa'),
             ('Driver\'s note found in a cab: "Rain for three days. The mud is on our side for once: their raiders bog down before they reach us."',
              'Mẩu giấy của tài xế tìm thấy trong ca-bin: "Mưa ba ngày rồi. Lần này bùn đứng về phía ta: bọn đột kích sa lầy trước khi tới được chỗ mình."')),
            [say('khai', 'Start', 'The convoy moves when you move. Stay with it.', 'Đoàn xe đi khi các anh đi. Bám sát nó.'),
             say('linh', 'At', 'Raiders on the north road. They are after the trucks, not you.', 'Quân đột kích trên đường phía bắc. Chúng nhắm vào xe tải, không phải các anh.', at=60)])

add_mission(m('c1m07', 1, 'greenvale', 'Protect', 'Storm', legacy='m22', targets=['silo', 'water_tower'], protectNeeded=1, targetHealth=8, surviveSeconds=420,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=8, enemyIncome=0.7,
              enemyDeck=GARRISON_HEAVY, playerCp=24, playerIncome=1.35, playerCap=34,
              waves=waves(['light_tank', 'ifv', 'rocket_technical', 'main_battle_tank'], first=100, interval=70, size=2, grow=0.3, max_size=4, max_alive=10),
              playerBase='Anchor', starTime=0, starLosses=10, challenge={'kind': 'NoAircraft'}),
            ('Harvest Guard', 'Giữ mùa gặt'),
            ('Hegemon wants the grain silos and the water tower at Greenvale\'s south end burned, so the valley starves and blames us. '
             'Keep at least one standing through the storm.',
             'Hegemon muốn đốt các silo lúa và tháp nước ở phía nam Lũng Xanh, để thung lũng đói và đổ lỗi cho ta. '
             'Giữ ít nhất một công trình đứng vững qua cơn bão.'),
            (('Scorched earth', 'Tiêu thổ'),
             ('Hegemon field order: "Deny the valley\'s food to the enemy." Linh underlined "the enemy" twice. The valley\'s food feeds the valley.',
              'Lệnh dã chiến của Hegemon: "Không để lương thực của thung lũng rơi vào tay địch." Linh gạch chân chữ "địch" hai lần. Lương thực của thung lũng là để nuôi chính thung lũng.')),
            [say('khai', 'Start', 'Silos and water tower. Nothing else matters today.', 'Silo và tháp nước. Hôm nay không có gì quan trọng hơn.'),
             say('mai', 'At', 'Storm is getting worse. So is their aim, lucky for us.', 'Bão càng lúc càng to. Bắn của chúng cũng càng tệ, may cho mình.', at=200)])

add_mission(m('c1m08', 1, 'ashfield', 'Capture', 'Clear', legacy='m01', points=['west', 'town', 'east'], reinforcements=1,
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.8,
              enemyDeck=GARRISON_HEAVY, playerCp=22, playerIncome=1.3, playerBase='Anchor',
              starTime=480, starLosses=6, challenge={'kind': 'NoStrikes'}),
            ('Ashfield Road', 'Đường vào Ashfield'),
            ('Ashfield\'s town and its two fuel depots lie in front of the fortress. Take all three, and the fortress is cut off from the road.',
             'Thị trấn Ashfield cùng hai kho nhiên liệu nằm ngay trước pháo đài. Chiếm cả ba, pháo đài sẽ bị cắt khỏi đường cái.'),
            (('Ashfield', 'Ashfield'),
             ('Before the Night of Steel, Ashfield made bricks. The fortress on the hill was a brickworks; Hegemon kept the kilns and put guns in them.',
              'Trước Đêm Thép, Ashfield làm gạch. Pháo đài trên đồi vốn là lò gạch; Hegemon giữ lại các lò nung rồi đặt pháo vào trong đó.')),
            [say('khai', 'Start', 'The fortress watches this road. Take the town and the depots, and it watches nothing.',
                 'Pháo đài canh con đường này. Chiếm thị trấn và các kho, nó sẽ chẳng còn gì để canh.'),
             say('linh', 'Lost', 'They have retaken a depot. They want that fuel badly.', 'Chúng chiếm lại một kho rồi. Chúng thèm chỗ nhiên liệu đó lắm.')])

add_mission(m('c1m09', 1, 'ashfield', 'Escort', 'Overcast', legacy='m02', convoyCount=5, convoyNeeded=3, reinforcements=1, timeLimit=1000,
              convoy=scripted('supply_truck', (-105, -105), route=[(-78.75, -78.75), (0, -78.75), (78.75, -78.75), (78.75, 0), (31.8, 0), (7.5, 0)], heading=45),
              units=units(0, ['light_tank', 'light_tank', 'ifv'], (-90, -90), 6),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['scout_jeep', 'armored_car', 'rocket_technical', 'light_tank', 'mortar_carrier'], first=12, interval=26, size=2, grow=0.45, max_size=5, max_alive=11,
                          spawns=[(15, -108), (93, -45), (93, 30), (45, 45), (-45, 21)]),
              playerBase='Anchor', starTime=300, starLosses=5, challenge={'kind': 'Kills', 'value': 18}),
            ('Ammunition for the Siege', 'Đạn cho trận vây thành'),
            ('The guns for the fortress need shells. Bring the ammunition trucks round the east road into Ashfield town; three of five must get there.',
             'Pháo đánh pháo đài cần đạn. Đưa đoàn xe chở đạn vòng đường phía đông vào thị trấn Ashfield; năm xe phải tới được ba.'),
            (('Shell count', 'Đếm đạn'),
             ('Artillery officer\'s estimate for the fortress: "Four thousand rounds, or one engineer who knows where the kilns are weakest." Mai volunteered. Khai ordered the rounds.',
              'Ước tính của sĩ quan pháo binh cho pháo đài: "Bốn nghìn quả đạn, hoặc một kỹ sư biết lò nung nào yếu nhất." Mai xung phong. Khải vẫn cho chở đạn.')),
            [say('khai', 'Start', 'No shells, no siege. Keep the trucks moving.', 'Không có đạn thì không vây được. Giữ cho đoàn xe chạy.')])

# The chapter's big operation: the Ashfield fortress, and the Bastion inside it.
C1_WAVES = waves(['light_tank', 'main_battle_tank', 'ifv', 'mortar_carrier', 'rocket_technical'], first=70, interval=60, size=2, grow=0.3, max_size=5, max_alive=12,
                 spawns=[(100, 60), (60, 100), (80, 80)])
add_mission(m('c1m10', 1, 'ashfield', 'Destroy', 'Fog', variant='siege', operation=True, reinforcements=2,
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=12, enemyIncome=0.85,
              enemyDeck=GARRISON_HEAVY, playerCp=30, playerIncome=2.0, playerCap=42, playerBase='Anchor', enemyHq=2,
              stages=[
                  {'stage': 'depot', 'goal': 'Destroy', 'targets': ['fuel_tank'], 'targetX': 56.25, 'targetZ': -97, 'targetRadius': 25, 'targetHealth': 2, 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c1m10.s1'}],
                   'choices': [{'key': 'dump', 'next': 'dump'}, {'key': 'radar', 'next': 'radar'}]},
                  {'stage': 'dump', 'goal': 'Destroy', 'targets': ['ammo_dump'], 'targetHealth': 2, 'cp': 6, 'next': 'bastion',
                   'events': [{'at': 'end', 'kind': 'Income', 'team': 1, 'amount': 0.7}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.enemyWeakened'}]},
                  {'stage': 'radar', 'goal': 'Destroy', 'targets': ['radar_station'], 'targetHealth': 2, 'cp': 6, 'next': 'bastion',
                   'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'airstrike', 'every': 55}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.alliedStrikes'}]},
                  {'stage': 'bastion', 'goal': 'Boss', 'boss': scripted('fortress_bastion', (92, 92), heading=225, health=0.55), 'cp': 10,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.mai.c1m10.s3'}]},
                  {'stage': 'counter', 'goal': 'Survive', 'surviveSeconds': 240, 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c1m10.s4'},
                              {'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'mortar_carrier', 'light_tank']},
                              {'at': '140', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'rocket_technical', 'ifv']}]},
                  {'stage': 'hq', 'goal': 'Destroy', 'targets': ['command_hq'], 'targetHealth': 0.8,
                   'events': [{'at': 'start', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'mortar_carrier']}]},
              ],
              waves=C1_WAVES, starTime=1320, starLosses=16),
            ('The Ashfield Fortress', 'Pháo đài Ashfield'),
            ('The old brickworks on the hill is Hegemon\'s strongest point on the coast, and the Bastion walks its yard. '
             'Burn the fuel depot outside, choose how to soften the walls, bring the Bastion down and level the command HQ.',
             'Lò gạch cũ trên đồi là điểm mạnh nhất của Hegemon trên dải duyên hải, và Bastion đi tuần trong sân của nó. '
             'Đốt kho nhiên liệu bên ngoài, chọn cách làm yếu tường thành, hạ gục Bastion và san phẳng sở chỉ huy.'),
            (('The Bastion\'s crew', 'Kíp lái Bastion'),
             ('Taken from the Bastion\'s crew after the fall: all eleven were contract engineers, not soldiers. The oldest had helped Mai weld her first Behemoth hull.',
              'Khai thác từ kíp lái Bastion sau khi pháo đài thất thủ: cả mười một người đều là kỹ sư hợp đồng, không phải lính. Người lớn tuổi nhất từng giúp Mai hàn vỏ chiếc Behemoth đầu tiên của cô.')),
            [say('khai', 'Start', 'This is what we landed for. The fortress falls today.', 'Ta đổ bộ là vì hôm nay. Pháo đài phải thất thủ.'),
             say('khai', 'Win', 'Ashfield is ours. Chapter one of a long book, Brigade.', 'Ashfield là của ta. Chương đầu của một cuốn sách dài, Lữ đoàn ạ.')],
            stages_text={'depot': ('Burn the Fuel Depot', 'Đốt kho nhiên liệu'), 'dump': ('Blow the Ammunition Dumps', 'Cho nổ kho đạn'),
                         'radar': ('Knock Out the Radar', 'Phá trạm radar'), 'bastion': ('The Bastion', 'Bastion'), 'counter': ('The Garrison Strikes Back', 'Quân đồn trú phản kích'),
                         'hq': ('Level the HQ', 'San phẳng sở chỉ huy')},
            choices_text={'dump': (('Blow the ammunition dumps', 'Cho nổ kho đạn'), ('The garrison earns 30 % less for the rest of the battle.', 'Quân địch kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')),
                          'radar': (('Knock out the radar', 'Phá trạm radar'), ('Diều Hâu can reach the fortress: a free airstrike about every minute.', 'Diều Hâu bay tới được pháo đài: một đợt không kích miễn phí khoảng mỗi phút.'))})
# Stage lines of the operation.
from campaign_kit import T
T('radio.khai.c1m10.s1', 'Fuel depot first. Light it up and their tanks go hungry.', 'Kho nhiên liệu trước. Đốt nó đi, xe tăng của chúng sẽ đói.')
T('radio.khai.c1m10.s4', 'The garrison is coming back out of the kilns. Hold where you stand.', 'Quân đồn trú đang tràn ra từ các lò nung. Giữ nguyên vị trí.')
T('radio.mai.c1m10.s3', 'That is the Bastion. Early model: thin rear plates. Hit it from behind!', 'Đó là Bastion. Mẫu đời đầu: giáp sau mỏng. Đánh từ phía sau!')

add_mission(m('c1s1', 1, 'greenvale', 'Recon', 'Fog', side=True, after='c1m03', speaker='linh', points=['west', 'town', 'east'], timeLimit=840, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Easy', enemyCp=10, enemyIncome=0.7,
              enemyDeck=GARRISON, playerCp=22, playerIncome=1.3, rarePrints=18, starTime=360, starLosses=5),
            ('Tracks in the Fog', 'Dấu xích trong sương'),
            ('Linh has heard engines in the fog round Greenvale\'s farms. Get a vehicle onto each of the three objectives and look before whatever is out there digs in.',
             'Linh nghe thấy tiếng động cơ trong sương quanh các trang trại Lũng Xanh. Đưa một xe tới từng cứ điểm trong ba cứ điểm để xem trước khi thứ gì ngoài đó kịp cố thủ.'),
            (('Linh\'s first report', 'Báo cáo đầu tiên của Linh'),
             ('"Engines: three types. Diesel, heavy. Not Hegemon standard. Suggest someone else is selling them tanks." The note was filed, and forgotten, until chapter eight.',
              '"Tiếng động cơ: ba loại. Diesel, hạng nặng. Không phải loại tiêu chuẩn của Hegemon. Đề nghị điều tra ai đang bán xe tăng cho chúng." Báo cáo được lưu lại, rồi bị quên, cho tới chương tám.')),
            [say('linh', 'Start', 'Three farms, three looks. Nobody fights unless they must.', 'Ba trang trại, ba lần nhìn. Không ai đánh nhau trừ khi bắt buộc.')])

add_mission(m('c1s2', 1, 'landingbeach', 'Hunt', 'Rain', side=True, after='c1m07', speaker='linh', timeLimit=900, targetHealth=2,
              hunt=[scripted('mortar_carrier', (-40, 70), route=[(-60, 90), (-30, 60), (-50, 50)]),
                    scripted('mortar_carrier', (20, 50), route=[(10, 70), (40, 40), (20, 30)]),
                    scripted('mlrs', (60, 20), route=[(80, 40), (50, 0), (70, -10)])],
              units=units(1, ['light_tank', 'ifv', 'armored_car'], (-35, 65), 7) + units(1, ['light_tank', 'rocket_technical'], (55, 25), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=10, enemyIncome=0.75,
              enemyDeck=GARRISON_HEAVY, playerCp=24, playerIncome=1.35, playerBase='Anchor', towerGear='Rare', starTime=480, starLosses=6),
            ('Mortars on the Bluffs', 'Cối trên vách đá'),
            ('Mortar teams on the bluffs are shelling the beach every night. Linh has marked three of them. Hunt them down in the rain.',
             'Các khẩu đội cối trên vách đá đêm nào cũng nã vào bãi biển. Linh đã đánh dấu ba khẩu. Săn lùng chúng dưới mưa.'),
            (('The mortar crews', 'Kíp cối'),
             ('The mortar crews kept a tally on a door: 41 shells on the first night, 12 on the fifth. They were running out, and so was their nerve.',
              'Kíp cối ghi số đạn lên một cánh cửa: 41 quả đêm đầu, 12 quả đêm thứ năm. Chúng đang cạn đạn, và cạn cả gan.')),
            [say('linh', 'Start', 'Three marked targets. They move between shots; so should we.', 'Ba mục tiêu được đánh dấu. Chúng di chuyển giữa các loạt bắn; ta cũng nên thế.')])

# ================================================================================ CHAPTER 2: BLACK GOLD

add_mission(m('c2m01', 2, 'dunebreak', 'Survive', 'Clear', legacy='m04', surviveSeconds=300, points=['east'], general='varga',
              enemyAi='waves', difficulty='Normal', playerCp=20, playerIncome=1.3,
              waves=waves(['rocket_technical', 'armored_car', 'light_tank', 'mortar_carrier', 'ifv'], first=18, interval=30, size=3, grow=0.6, max_size=8, max_alive=16,
                          spawns=[(93, -15), (75, 33), (27, -114)]),
              playerBase='Anchor', unlocks=['mlrs'], starTime=0, starLosses=8, challenge={'kind': 'NoAircraft'}),
            ('Oil and Sand', 'Dầu và cát'),
            ('The brigade has reached Dunebreak\'s oil field. Hegemon wants it back before we can blow the wells. Hold out at the field for five minutes.',
             'Lữ đoàn đã tới mỏ dầu Dunebreak. Hegemon muốn giành lại trước khi ta kịp phá giếng. Trụ vững ở mỏ dầu trong năm phút.'),
            (('Black gold', 'Vàng đen'),
             ('Hegemon\'s machines burn 40,000 barrels a day. Dunebreak and Red Rock pump 38,000. Varga has been complaining about the other two thousand for a year.',
              'Máy móc của Hegemon đốt 40.000 thùng dầu mỗi ngày. Dunebreak và Hẻm Đá Đỏ bơm được 38.000. Varga đã cằn nhằn về hai nghìn thùng còn thiếu suốt một năm nay.')),
            [say('khai', 'Start', 'Five minutes. Dig in round the pumps and let them come.', 'Năm phút. Bám quanh các giàn bơm và để chúng tới.'),
             say('varga', 'At', 'Who is burning my oil? Find them. Crush them.', 'Kẻ nào đang đốt dầu của ta? Tìm ra. Nghiền nát.', at=90)])

add_mission(m('c2m02', 2, 'redrock', 'Capture', 'Clear', points=['west', 'town', 'east'], enemyOwns=['town'], general='varga', reinforcements=2,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=13, enemyIncome=0.85,
              enemyDeck=VARGA_EARLY, playerCp=24, playerIncome=1.4, playerBase='Anchor',
              unlocks=['sam_launcher'], starTime=540, starLosses=8),
            ('The Wells of Red Rock', 'Giếng dầu Hẻm Đá Đỏ'),
            ('Red Rock\'s wellhead, oasis and caravan stop feed the pipeline to Dunebreak. Varga\'s tanks hold the oasis. Take all three.',
             'Đầu giếng, ốc đảo và trạm dừng đoàn lạc đà ở Hẻm Đá Đỏ cấp dầu cho đường ống tới Dunebreak. Xe tăng của Varga giữ ốc đảo. Chiếm cả ba.'),
            (('Varga\'s memo', 'Bản ghi nhớ của Varga'),
             ('Memo from General Varga to Director Aurel: "I need the Red Rock wells, two more Behemoths and nobody from accounting in my headquarters." Aurel approved one of the three.',
              'Ghi nhớ của tướng Varga gửi giám đốc Aurel: "Tôi cần giếng dầu Hẻm Đá Đỏ, thêm hai chiếc Behemoth và không có ai của phòng kế toán trong sở chỉ huy của tôi." Aurel duyệt một trong ba đề nghị.')),
            [say('linh', 'Start', 'Varga\'s own tanks at the oasis. He is here, Colonel. In person.', 'Xe tăng của chính Varga ở ốc đảo. Hắn ở đây, đại tá. Đích thân.'),
             say('varga', 'Capture', 'Take the sand if you like. The sand does not care.', 'Lấy cát nếu thích. Cát chẳng quan tâm đâu.', arg='town')])

add_mission(m('c2m03', 2, 'redrock', 'Escort', 'Night', convoyCount=5, convoyNeeded=3, reinforcements=1, timeLimit=1000,
              convoy=scripted('supply_truck', (-100, -100), route=[(-78, -65), (-34, -45), (-20, -20), (0, 0), (-30, 40), (-56.25, 86.25)], heading=45),
              units=units(0, ['main_battle_tank', 'ifv', 'aa_vehicle'], (-88, -92), 6),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['armored_car', 'rocket_technical', 'light_tank', 'tank_destroyer', 'mortar_carrier'], first=20, interval=28, size=2, grow=0.5, max_size=6, max_alive=13,
                          spawns=[(60, 80), (90, 20), (20, 110), (-60, 110)]),
              unlocks=['flame_tank'], starTime=360, starLosses=6, challenge={'kind': 'Kills', 'value': 18}),
            ('Night Caravan', 'Đoàn xe đêm'),
            ('Fuel trucks for the brigade, through the canyon at night, past the oasis to the wellhead. Three of five must get through.',
             'Xe bồn nhiên liệu cho lữ đoàn, băng qua hẻm núi trong đêm, qua ốc đảo tới đầu giếng. Năm xe phải qua được ba.'),
            (('The caravan road', 'Đường đoàn lạc đà'),
             ('The canyon road was a caravan route for five hundred years. The drivers still leave a stone at the oasis for luck. Ours did too.',
              'Con đường qua hẻm núi là tuyến đoàn lạc đà suốt năm trăm năm. Cánh tài xế vẫn đặt một hòn đá ở ốc đảo để cầu may. Tài xế của ta cũng thế.')),
            [say('khai', 'Start', 'Lights off, engines low. Bring them through.', 'Tắt đèn, hạ ga. Đưa họ qua.')])

add_mission(m('c2m04', 2, 'dunebreak', 'Destroy', 'Overcast', targets=['pipeline'], targetHealth=2.5, timeLimit=900, general='varga', reinforcements=2,
              units=units(1, ['main_battle_tank', 'tank_destroyer'], (0, 30), 6) + units(1, ['light_tank', 'ifv'], (100, -50), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.85,
              enemyDeck=VARGA_EARLY, playerCp=24, playerIncome=1.4,
              unlocks=['airstrike'], starTime=480, starLosses=8, challenge={'kind': 'NoStrikes'}),
            ('Cut the Pipeline', 'Cắt đường ống'),
            ('Five pipeline stations carry Red Rock\'s oil into the refinery. Blow every one of them. A raid, no base: in fast, out faster.',
             'Năm trạm đường ống dẫn dầu từ Hẻm Đá Đỏ vào nhà máy lọc dầu. Cho nổ tung tất cả. Một trận đột kích, không căn cứ: vào nhanh, ra nhanh hơn.'),
            (('Pressure', 'Áp suất'),
             ('Refinery log after the raid: "Pressure zero on all lines. General Varga informed. General Varga has broken the telephone."',
              'Sổ nhật ký nhà máy sau trận đột kích: "Áp suất bằng không trên mọi tuyến. Đã báo tướng Varga. Tướng Varga đã đập vỡ điện thoại."')),
            [say('khai', 'Start', 'Five stations. Every one burns.', 'Năm trạm. Trạm nào cũng phải cháy.'),
             say('varga', 'At', 'My pipeline! You will pay by the barrel.', 'Đường ống của ta! Ngươi sẽ trả giá theo từng thùng.', at=150)])

add_mission(m('c2m05', 2, 'dunebreak', 'Boss', 'Sandstorm', legacy='m06', timeLimit=1200, general='varga', reinforcements=3,
              boss=scripted('behemoth', (75, 75), heading=225, health=1.8),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=11, enemyIncome=0.85,
              enemyDeck=VARGA_EARLY, playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              unlocks=['heavy_tank'], starTime=720, starLosses=10),
            ('Behemoth', 'Behemoth'),
            ('A land battleship crawls out of the sandstorm: Varga\'s Behemoth, the machine Mai helped build. '
             'Its main gun kills a tank a shot. Mai says the rear plates are thin. Bring it down.',
             'Một chiến hạm mặt đất bò ra từ bão cát: Behemoth của Varga, cỗ máy chính Mai từng góp tay chế tạo. '
             'Pháo chính của nó mỗi phát hạ một xe tăng. Mai nói giáp sau mỏng. Hạ gục nó.'),
            (('Hull number one', 'Thân tàu số một'),
             ('Mai, quietly, after the battle: "I welded the rear plates on that one. I used the thin ones because the thick ones were late. I never told anyone."',
              'Mai, khẽ nói sau trận: "Tôi đã hàn các tấm giáp sau của chiếc đó. Tôi dùng loại mỏng vì loại dày về trễ. Tôi chưa bao giờ nói với ai."')),
            [say('varga', 'Start', 'Colonel Khải. Meet the Behemoth. It does not negotiate either.', 'Đại tá Khải. Chào Behemoth đi. Nó cũng không biết thương lượng đâu.'),
             say('mai', 'Boss', 'Rear plates, Colonel. I know, because I put them there.', 'Giáp sau, đại tá. Tôi biết, vì chính tôi lắp chúng.'),
             say('mai', 'BossHalf', 'It is slowing. The engine block is exposed!', 'Nó chậm lại rồi. Khối động cơ lộ ra rồi!'),
             say('varga', 'Win', 'Retreat. Save the machines. The men can walk.', 'Rút. Giữ lấy máy móc. Người thì đi bộ cũng được.')])

add_mission(m('c2m06', 2, 'redrock', 'Hunt', 'Sandstorm', legacy='m17', timeLimit=1100, targetHealth=2.5, general='varga', reinforcements=2,
              hunt=[scripted('elite_mlrs', (90, 45), route=[(60, 82.5), (22.5, 60), (52.5, 22.5), (90, 45)]),
                    scripted('elite_grad', (-15, 105), heading=180, route=[(-60, 120), (-37.5, 75), (-15, 105)]),
                    scripted('sam_launcher', (105, 0), route=[(82.5, -37.5), (120, -45), (105, 0)])],
              units=[{'def': 'tank_destroyer', 'team': 1, 'x': 75, 'z': 52.5, 'heading': 225}, {'def': 'aa_vehicle', 'team': 1, 'x': 82.5, 'z': 63, 'heading': 225},
                     {'def': 'main_battle_tank', 'team': 1, 'x': -7.5, 'z': 90, 'heading': 200}, {'def': 'tank_destroyer', 'team': 1, 'x': -27, 'z': 99, 'heading': 200},
                     {'def': 'heavy_tank', 'team': 1, 'x': 93, 'z': -12, 'heading': 225}, {'def': 'main_battle_tank', 'team': 1, 'x': 108, 'z': -21, 'heading': 225}],
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.85,
              enemyDeck=['main_battle_tank', 'aa_vehicle', 'tank_destroyer', 'ifv', 'heavy_tank', 'mortar_carrier'],
              playerCp=26, playerIncome=1.4, playerCap=36, playerBase='Anchor',
              unlocks=['atgm_tower', 'ammo_depot'], starTime=660, starLosses=12, challenge={'kind': 'Kills', 'value': 25}),
            ('Scorpion Hunt', 'Săn bọ cạp'),
            ('Three of Varga\'s rocket and missile batteries hide among the mesas, marked in red. Find them in the sandstorm and knock them out.',
             'Ba dàn pháo phản lực và tên lửa của Varga ẩn giữa các khối đá, đánh dấu màu đỏ. Tìm ra chúng trong bão cát và tiêu diệt.'),
            (('Scorpions', 'Bọ cạp'),
             ('Varga\'s batteries call themselves the Scorpions and paint a tail on every launcher. After this afternoon, there were no more tails to paint.',
              'Các khẩu đội của Varga tự gọi mình là Bọ Cạp và vẽ một cái đuôi lên mỗi bệ phóng. Sau buổi chiều hôm đó, chẳng còn cái đuôi nào để vẽ nữa.')),
            [say('linh', 'Start', 'Three batteries, marked. They move; we move faster.', 'Ba khẩu đội, đã đánh dấu. Chúng di chuyển; ta di chuyển nhanh hơn.')])

add_mission(m('c2m07', 2, 'redrock', 'Relieve', 'Night', targetHealth=3.0, reinforcements=2, timeLimit=1000,
              ally={'x': 0, 'z': 0, 'hq': 'headquarters', 'structures': units(0, ['mg_bunker', 'gun_turret', 'guard_tower'], (0, 0), 14),
                    'units': units(0, ['ifv', 'light_tank'], (-6, -6), 4)},
              hunt=[scripted(d, p) for d, p in zip(['main_battle_tank', 'tank_destroyer', 'light_tank', 'mortar_carrier', 'ifv', 'main_battle_tank'],
                                                   ring((0, 0), 38, 6, 0.3))],
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.75,
              enemyDeck=VARGA_EARLY, playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['light_tank', 'ifv', 'mortar_carrier', 'tank_destroyer'], first=70, interval=60, size=2, grow=0.3, max_size=4, max_alive=12,
                          spawns=[(60, 80), (80, 30)]),
              starTime=480, starLosses=8),
            ('The Oasis Garrison', 'Đồn ốc đảo'),
            ('A company of Red Rock militia has declared for the Alliance and is holding the oasis. Varga\'s tanks have it ringed. '
             'Break the ring before their HQ falls. The ring vehicles are marked.',
             'Một đại đội dân quân Hẻm Đá Đỏ đã tuyên bố đứng về phía Liên minh và đang giữ ốc đảo. Xe tăng của Varga vây kín họ. '
             'Phá vòng vây trước khi sở chỉ huy của họ thất thủ. Các xe vây được đánh dấu.'),
            (('Militia', 'Dân quân'),
             ('The militia captain\'s first words to Khai: "We have been waiting two years. You are late." His second: "Thank you."',
              'Câu đầu tiên của đại đội trưởng dân quân với Khải: "Chúng tôi chờ hai năm rồi. Các anh tới muộn." Câu thứ hai: "Cảm ơn."')),
            [say('khai', 'Start', 'They held for two years. We can hold for them tonight.', 'Họ giữ được hai năm. Đêm nay ta giữ cho họ.'),
             say('linh', 'At', 'The garrison\'s HQ is taking fire. Hurry.', 'Sở chỉ huy của đồn đang trúng đạn. Nhanh lên.', at=120)])

add_mission(m('c2m08', 2, 'dunebreak', 'Hold', 'Night', points=['town'], holdSeconds=240, general='varga', reinforcements=2,
              units=units(0, ['main_battle_tank', 'main_battle_tank', 'ifv', 'aa_vehicle', 'tank_destroyer'], (-8, -8), 8),
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.8,
              enemyDeck=VARGA, playerCp=24, playerIncome=1.3, playerCap=40, playerBase='Anchor',
              waves=waves(['light_tank', 'main_battle_tank', 'ifv', 'mortar_carrier', 'flame_tank'], first=40, interval=48, size=2, grow=0.35, max_size=5, max_alive=12),
              starTime=0, starLosses=10),
            ('Hold the Refinery', 'Giữ nhà máy lọc dầu'),
            ('We have a foot inside the refinery. Varga is throwing his reserve at it. Hold the refinery yard for four minutes.',
             'Ta đã đặt được một chân vào nhà máy lọc dầu. Varga đang tung lực lượng dự bị vào đó. Giữ sân nhà máy trong bốn phút.'),
            (('Night shift', 'Ca đêm'),
             ('The refinery\'s night shift hid in the cooling towers through the whole battle. In the morning they asked who was paying their wages now.',
              'Ca đêm của nhà máy trốn trong tháp làm mát suốt trận đánh. Sáng ra họ hỏi giờ ai sẽ trả lương cho họ.')),
            [say('khai', 'Start', 'Four minutes in the yard. Do not chase them out.', 'Bốn phút trong sân. Đừng đuổi theo chúng ra ngoài.'),
             say('varga', 'At', 'Burn them out of my refinery!', 'Đốt chúng ra khỏi nhà máy của ta!', at=100)])

add_mission(m('c2m09', 2, 'redrock', 'Duel', 'Sandstorm', targetHealth=0.4, general='varga', enemyBase='Target', enemyHq=3, replay=True, reinforcements=3, timeLimit=1500,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=10, enemyIncome=0.54,
              playerCp=26, playerIncome=1.9, playerCap=38, playerBase='Anchor', starTime=780, starLosses=12),
            ('Varga\'s Camp', 'Trại của Varga'),
            ('Varga has dug his headquarters into the far end of the canyon: anti-tank guns, his favourite tanks, and his temper. '
             'Level his HQ. He will run; let him know we are coming.',
             'Varga đã đào sở chỉ huy vào cuối hẻm núi: pháo chống tăng, những chiếc xe tăng hắn ưng ý nhất, và cái tính nóng của hắn. '
             'San phẳng sở chỉ huy. Hắn sẽ chạy; để hắn biết ta đang tới.'),
            (('The napkin', 'Tờ giấy ăn'),
             ('Found in Varga\'s abandoned tent: a napkin with the first sketch of the Behemoth, dated eleven years ago. On the back, a shopping list. Linh framed it.',
              'Tìm thấy trong lều bỏ lại của Varga: một tờ giấy ăn với bản phác thảo đầu tiên của Behemoth, đề ngày mười một năm trước. Mặt sau là danh sách đồ cần mua. Linh đóng khung nó lại.')),
            [say('varga', 'Start', 'Steel does not negotiate, Colonel.', 'Thép không biết thương lượng, đại tá ạ.'),
             say('khai', 'Start', 'Neither do I.', 'Tôi cũng thế.'),
             say('varga', 'Win', 'Retreat. Save the machines.', 'Rút. Giữ lấy máy móc.')])

add_mission(m('c2m10', 2, 'dunebreak', 'Capture', 'Overcast', legacy='m05', operation=True, general='varga', reinforcements=3,
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.9,
              enemyDeck=VARGA, playerCp=28, playerIncome=1.6, playerCap=40, playerBase='Anchor',
              waves=waves(['light_tank', 'main_battle_tank', 'ifv', 'flame_tank', 'tank_destroyer'], first=80, interval=60, size=2, grow=0.3, max_size=5, max_alive=12),
              stages=[
                  {'stage': 'fields', 'goal': 'Capture', 'points': ['east', 'west'], 'enemyOwns': ['east', 'west'], 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c2m10.s1'}],
                   'choices': [{'key': 'tanks', 'next': 'tanks'}, {'key': 'oasis', 'next': 'oasis'}]},
                  {'stage': 'tanks', 'goal': 'Destroy', 'targets': ['fuel_tank'], 'targetX': 65, 'targetZ': 29, 'targetRadius': 20, 'targetHealth': 2, 'cp': 6, 'next': 'wells',
                   'events': [{'at': 'end', 'kind': 'Income', 'team': 1, 'amount': 0.7}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.enemyWeakened'}]},
                  {'stage': 'oasis', 'goal': 'Survive', 'points': ['west'], 'surviveSeconds': 90, 'cp': 6, 'next': 'wells',
                   'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'airstrike', 'every': 55}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.alliedStrikes'}]},
                  {'stage': 'wells', 'goal': 'Destroy', 'targets': ['oil_pump'], 'targetX': 56, 'targetZ': -86, 'targetRadius': 40, 'targetHealth': 2, 'cp': 6},
                  {'stage': 'refinery', 'goal': 'Destroy', 'targets': ['refinery_tower', 'storage_tank'], 'targetX': 0, 'targetZ': 0, 'targetRadius': 40, 'targetHealth': 2, 'cp': 10,
                   'events': [{'at': 'start', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'tank_destroyer', 'flame_tank']}]},
                  {'stage': 'yard', 'goal': 'Survive', 'points': ['town'], 'surviveSeconds': 240, 'cp': 8,
                   'events': [{'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'flame_tank']}]},
                  {'stage': 'inferno', 'goal': 'Boss', 'boss': scripted('behemoth_inferno', (30, 30), heading=225, health=1.4), 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.varga.c2m10.s5'}]},
                  {'stage': 'counter', 'goal': 'Survive', 'surviveSeconds': 480,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.varga.c2m10.s6'},
                              {'at': '40', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'tank_destroyer', 'ifv', 'mlrs']},
                              {'at': '200', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'flame_tank', 'heavy_tank']}]},
              ],
              towerGear=None, starTime=1320, starLosses=16),
            ('Refinery Raid', 'Đột kích nhà máy lọc dầu'),
            ('The operation Varga fears: take the oil field and the oasis, choose what to hit next, then blow the refinery\'s towers and tanks. '
             'Linh says something is parked inside the refinery, and it runs on fire.',
             'Chiến dịch mà Varga sợ nhất: chiếm mỏ dầu và ốc đảo, chọn mục tiêu kế tiếp, rồi cho nổ tháp và bồn chứa của nhà máy. '
             'Linh nói có thứ gì đó đang đỗ bên trong nhà máy, và nó chạy bằng lửa.'),
            (('Inferno', 'Inferno'),
             ('Workshop order for the Inferno: "Two flame projectors, one thermobaric box, cooling for the crew (optional)." The cooling was never fitted.',
              'Phiếu đặt hàng xưởng cho Inferno: "Hai súng phun lửa lớn, một hộp rocket nhiệt áp, hệ làm mát cho kíp lái (tùy chọn)." Hệ làm mát chưa bao giờ được lắp.')),
            [say('khai', 'Start', 'The refinery burns today, Brigade. Everything inside it too.', 'Hôm nay nhà máy lọc dầu phải cháy, Lữ đoàn. Cả những gì bên trong nó.'),
             say('khai', 'Win', 'Varga is running out of fuel, and out of monsters.', 'Varga đang cạn dầu, và cạn cả quái vật.')],
            stages_text={'fields': ('The Oil Field and the Oasis', 'Mỏ dầu và ốc đảo'), 'tanks': ('Burn the Fuel Tanks', 'Đốt bồn nhiên liệu'),
                         'oasis': ('Hold the Oasis Radio', 'Giữ đài phát ốc đảo'), 'wells': ('Blow the Wellheads', 'Phá các đầu giếng'),
                         'refinery': ('Blow the Refinery', 'Cho nổ nhà máy'), 'yard': ('Hold the Refinery Yard', 'Giữ sân nhà máy'), 'inferno': ('Inferno', 'Inferno'),
                         'counter': ('Varga\'s Counterattack', 'Varga phản kích')},
            choices_text={'tanks': (('Burn the fuel tanks', 'Đốt bồn nhiên liệu'), ('Varga\'s army earns 30 % less for the rest of the battle.', 'Quân Varga kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')),
                          'oasis': (('Hold the oasis radio', 'Giữ đài phát ốc đảo'), ('Hold it 90 s: Diều Hâu\'s airstrikes, free, about every minute.', 'Giữ 90 giây: không kích miễn phí của Diều Hâu, khoảng mỗi phút một lượt.'))})
T('radio.khai.c2m10.s1', 'Oil field and oasis first. Then we choose.', 'Mỏ dầu và ốc đảo trước. Rồi ta sẽ chọn.')
T('radio.varga.c2m10.s6', 'Every tank I have left, to the refinery. Now!', 'Toàn bộ xe tăng còn lại, tới nhà máy lọc dầu. Ngay!')
T('radio.varga.c2m10.s5', 'You want fire, Colonel? Here is fire.', 'Muốn lửa hả, đại tá? Lửa đây.')

add_mission(m('c2s1', 2, 'dunebreak', 'Recon', 'Night', side=True, after='c2m03', speaker='linh', points=['west', 'town', 'east'], timeLimit=840, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=12, enemyIncome=0.8,
              enemyDeck=VARGA_EARLY, playerCp=24, playerIncome=1.4, rarePrints=22, starTime=420, starLosses=6, challenge={'kind': 'NoAircraft'}),
            ('Minefield Maps', 'Bản đồ bãi mìn'),
            ('Linh needs eyes on the oasis, the refinery and the oil field at night: Varga has been laying mines, and she wants to know where. Look, do not linger.',
             'Linh cần người tới xem ốc đảo, nhà máy và mỏ dầu trong đêm: Varga đang cho rải mìn, và cô muốn biết ở đâu. Nhìn rồi đi, đừng nấn ná.'),
            (('The mine map', 'Tấm bản đồ mìn'),
             ('The map Linh drew that night had 340 marks on it. The engineers cleared 338. Nobody found the other two, and nobody drives that way.',
              'Tấm bản đồ Linh vẽ đêm đó có 340 dấu. Công binh gỡ được 338. Không ai tìm ra hai quả còn lại, và không ai lái xe đi đường đó.')),
            [say('linh', 'Start', 'Three looks. Their mines are the target, not their tanks.', 'Ba lần nhìn. Mìn của chúng là mục tiêu, không phải xe tăng.')])

add_mission(m('c2s2', 2, 'redrock', 'ShootDown', 'Clear', side=True, after='c2m07', speaker='dieuhau', killsNeeded=10, timeLimit=1100,
              enemyAi='waves', difficulty='Normal', playerCp=24, playerIncome=1.4, playerCap=34,
              waves=waves(['attack_helicopter', 'attack_helicopter', 'scout_heli', 'armored_car', 'light_tank'], first=30, interval=40, size=2, grow=0.35, max_size=5, max_alive=12),
              towerGear='Rare', starTime=540, starLosses=8),
            ('Varga\'s Gunships', 'Trực thăng của Varga'),
            ('Varga has called in helicopters to hunt our convoys over Red Rock. Diều Hâu wants ten of them down before sunset. Bring your anti-air.',
             'Varga gọi trực thăng tới săn đoàn xe của ta trên Hẻm Đá Đỏ. Diều Hâu muốn bắn rơi mười chiếc trước khi mặt trời lặn. Mang phòng không theo.'),
            (('Diều Hâu\'s score', 'Bảng điểm của Diều Hâu'),
             ('Chalked on the hangar wall: "Diều Hâu 10, Varga 0." Underneath, in smaller letters: "Anti-air crews 9 of those."',
              'Viết phấn trên tường nhà chứa máy bay: "Diều Hâu 10, Varga 0." Bên dưới, chữ nhỏ hơn: "Trong đó 9 chiếc là của pháo thủ phòng không."')),
            [say('dieuhau', 'Start', 'Helicopters, low and slow. My favourite kind.', 'Trực thăng, bay thấp và chậm. Loại tôi khoái nhất.')])

# ================================================================================ CHAPTER 3: THE LONG WINTER

add_mission(m('c3m01', 3, 'whiteout', 'Capture', 'Snow', points=['west', 'town', 'east'], general='orlov', reinforcements=2,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.85,
              enemyDeck=ORLOV, playerCp=24, playerIncome=1.4, playerBase='Anchor',
              unlocks=['heavy_aa'], starTime=540, starLosses=8),
            ('Into the Pass', 'Vào đèo'),
            ('The Whiteout pass is the only road north. Orlov\'s outposts hold its signal post, the frozen lake and the sawmill. Take all three in the snow.',
             'Đèo Bão Tuyết là con đường duy nhất lên phía bắc. Tiền đồn của Orlov giữ trạm tín hiệu, hồ băng và xưởng cưa. Chiếm cả ba trong tuyết.'),
            (('Orlov', 'Orlov'),
             ('Orlov\'s personnel file: "Excellent. Cold. Has requested that his batteries be positioned further from the front. Again."',
              'Hồ sơ nhân sự của Orlov: "Xuất sắc. Lạnh lùng. Lại đề nghị bố trí các khẩu đội của mình xa tiền tuyến hơn nữa."')),
            [say('orlov', 'Start', 'Welcome to the highlands, Colonel. You are a coordinate now.', 'Chào mừng tới cao nguyên, đại tá. Giờ ngươi chỉ là một tọa độ.'),
             say('khai', 'Start', 'Keep moving. Coordinates that move are harder to hit.', 'Cứ di chuyển. Tọa độ biết chạy thì khó bắn trúng hơn.')])

add_mission(m('c3m02', 3, 'frostpeak', 'Destroy', 'Snow', legacy='m07', targets=['radar_station'], timeLimit=840, targetHealth=5, general='orlov', reinforcements=2,
              units=[{'def': 'heavy_tank', 'team': 1, 'x': -56.25, 'z': 93.75, 'heading': 225}, {'def': 'sam_launcher', 'team': 1, 'x': -75, 'z': 116.25, 'heading': 225},
                     {'def': 'aa_vehicle', 'team': 1, 'x': -37.5, 'z': 112.5, 'heading': 225}, {'def': 'main_battle_tank', 'team': 1, 'x': -41.25, 'z': 97.5, 'heading': 225},
                     {'def': 'mortar_carrier', 'team': 1, 'x': -60, 'z': 128, 'heading': 225}],
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.9,
              enemyDeck=ORLOV,
              waves=waves(['scout_heli', 'attack_helicopter', 'armored_car'], first=60, interval=55, size=2, grow=0.4, max_size=5, max_alive=16),
              playerCp=24, playerIncome=1.4, playerBase='Anchor',
              unlocks=['attack_helicopter'], starTime=480, starLosses=8, challenge={'kind': 'NoStrikes'}),
            ('Blind the Radar', 'Làm mù radar'),
            ('The first station of Orlov\'s radar line stands on the western heights. While it sees, his guns hit anything we move. Destroy it.',
             'Trạm đầu tiên trên tuyến radar của Orlov đứng trên cao điểm phía tây. Chừng nào nó còn nhìn thấy, pháo của hắn còn bắn trúng mọi thứ ta di chuyển. Phá hủy nó.'),
            (('The radar line', 'Tuyến radar'),
             ('Seven stations from the coast to the mountains, each seeing eighty kilometres. With one gone, Orlov\'s map has a hole the size of a brigade.',
              'Bảy trạm từ bờ biển tới núi, mỗi trạm nhìn xa tám mươi cây số. Mất một trạm, tấm bản đồ của Orlov thủng một lỗ to bằng cả lữ đoàn.')),
            [say('linh', 'Start', 'Heavy tank and SAMs round the radar. Orlov guards his eyes.', 'Xe tăng hạng nặng và tên lửa phòng không quanh radar. Orlov canh mắt của hắn kỹ lắm.')])

add_mission(m('c3m03', 3, 'frostpeak', 'Hold', 'Fog', legacy='m08', points=['town'], holdSeconds=210, general='orlov', reinforcements=2,
              units=units(0, ['main_battle_tank', 'main_battle_tank', 'aa_vehicle', 'light_tank', 'tank_destroyer', 'heavy_tank', 'mlrs'], (0, 0), 12),
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=9, enemyIncome=0.85,
              enemyDeck=['light_tank', 'ifv', 'main_battle_tank', 'heavy_tank', 'mortar_carrier', 'flame_tank', 'attack_helicopter'],
              playerCp=24, playerIncome=1.2, playerCap=40, playerBase='Anchor',
              waves=waves(['light_tank', 'main_battle_tank', 'ifv', 'mortar_carrier', 'attack_helicopter', 'flame_tank'], first=45, interval=50, size=2, grow=0.3, max_size=4, max_alive=10),
              unlocks=['uav_scan'], starTime=0, starLosses=10),
            ('Village in the Fog', 'Ngôi làng trong sương'),
            ('The village in the valley is the only shelter for kilometres. Orlov wants it back, and the fog hides his guns. Hold it for three and a half minutes.',
             'Ngôi làng dưới thung lũng là chỗ trú duy nhất trong vòng nhiều cây số. Orlov muốn lấy lại, và sương mù che pháo của hắn. Giữ làng trong ba phút rưỡi.'),
            (('The church bell', 'Tiếng chuông nhà thờ'),
             ('The village priest rang the church bell every time Orlov\'s guns fired, so the brigade knew when to duck. He rang it 212 times.',
              'Cha xứ trong làng kéo chuông nhà thờ mỗi lần pháo Orlov khai hỏa, để lữ đoàn biết mà nằm xuống. Ông kéo 212 lần.')),
            [say('khai', 'Start', 'We hold the village. They come to us, in the fog.', 'Ta giữ ngôi làng. Chúng sẽ tới chỗ ta, trong sương.')])

add_mission(m('c3m04', 3, 'whiteout', 'Outpost', 'Night', points=['town'], holdSeconds=180, speaker='mai', general='orlov', reinforcements=2, timeLimit=1100,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=12, enemyIncome=0.85,
              enemyDeck=ORLOV, playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              waves=waves(['light_tank', 'ifv', 'mortar_carrier', 'main_battle_tank'], first=70, interval=55, size=2, grow=0.3, max_size=4, max_alive=12),
              unlocks=['dragons_teeth', 'radar_station'], starTime=600, starLosses=8),
            ('Base on the Ice', 'Căn cứ trên băng'),
            ('Mai wants a forward base on the frozen lake, in the middle of the pass. Take the lake, set up an outpost and keep it three minutes. At night. On ice.',
             'Mai muốn dựng căn cứ tiền phương trên hồ băng, giữa đèo. Chiếm hồ, lập tiền đồn và giữ nó ba phút. Ban đêm. Trên băng.'),
            (('Ice thickness', 'Độ dày của băng'),
             ('Mai measured the ice herself: ninety centimetres. "Enough for a tower, not for a Behemoth," she wrote. "Good. That is the point."',
              'Mai tự tay đo băng: chín mươi phân. "Đủ cho một cái tháp, không đủ cho một chiếc Behemoth," cô ghi. "Tốt. Chính là thế."')),
            [say('mai', 'Start', 'The ice holds towers. I checked. Mostly.', 'Băng chịu được tháp. Tôi kiểm tra rồi. Gần như chắc chắn.'),
             say('orlov', 'At', 'A base on a lake. How poetic. How flammable.', 'Căn cứ trên mặt hồ. Thật nên thơ. Thật dễ cháy.', at=120)])

add_mission(m('c3m05', 3, 'whiteout', 'Boss', 'Clear', legacy='m03', general='orlov', timeLimit=1140, reinforcements=2,
              boss=scripted('mega_gunship', (84, 84), heading=225, route=[(60, 60), (-20, 60), (-40, -10), (30, -30)], health=1.6),
              enemyAi='commander', enemyStance='Attack', difficulty='Normal', enemyCp=12, enemyIncome=0.85,
              enemyDeck=['light_tank', 'main_battle_tank', 'ifv', 'mortar_carrier', 'aa_vehicle', 'attack_helicopter'],
              playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              hqLevel=2, unlocks=['atgm_carrier'], starTime=660, starLosses=10, challenge={'kind': 'NoStrikes'}),
            ('Iron Bird', 'Chim Sắt'),
            ('Orlov\'s Iron Bird has come down from the clouds over the pass: a gunship the size of a ship, with rockets, flares and an escort. '
             'This is what the anti-air was for. Bring it down.',
             'Chim Sắt của Orlov đã sà xuống khỏi mây trên đèo: một pháo hạm bay to như con tàu, có rocket, pháo sáng mồi bẫy và đội hộ tống. '
             'Phòng không là để dành cho lúc này. Bắn rơi nó.'),
            (('Iron Bird', 'Chim Sắt'),
             ('Iron Bird\'s crew manual, page one: "The aircraft cannot be shot down by ground fire." Page two was missing. So, now, is Iron Bird.',
              'Sổ tay kíp lái Chim Sắt, trang một: "Máy bay không thể bị hỏa lực mặt đất bắn hạ." Trang hai bị mất. Giờ thì Chim Sắt cũng mất.')),
            [say('dieuhau', 'Start', 'Big bird, big target. Keep the launchers moving under it.', 'Chim to, bia to. Cho các bệ phóng di chuyển liên tục dưới nó.'),
             say('orlov', 'Boss', 'Look up, Colonel. The coordinate has arrived.', 'Nhìn lên đi, đại tá. Tọa độ đã tới.'),
             say('dieuhau', 'Win', 'Iron Bird is down! Somebody owes me a drink.', 'Chim Sắt rơi rồi! Có ai đó nợ tôi một chầu đấy.')])

add_mission(m('c3m06', 3, 'frostpeak', 'Hunt', 'Night', general='orlov', timeLimit=1100, targetHealth=2.5, reinforcements=2,
              hunt=[scripted('mlrs', (60, 70), route=[(80, 90), (40, 60), (70, 40)]),
                    scripted('artillery', (-20, 100), route=[(-40, 120), (0, 90), (-30, 80)]),
                    scripted('mlrs', (100, 20), route=[(110, -10), (90, 40), (120, 30)])],
              units=units(1, ['main_battle_tank', 'aa_vehicle', 'tank_destroyer'], (60, 70), 7) + units(1, ['ifv', 'sam_launcher'], (-20, 100), 6) +
              units(1, ['heavy_tank', 'mortar_carrier'], (100, 20), 6),
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=14, enemyIncome=0.9,
              enemyDeck=ORLOV, playerCp=26, playerIncome=1.45, playerCap=36, playerBase='Anchor',
              unlocks=['artillery_emplacement'], starTime=660, starLosses=10, challenge={'kind': 'Kills', 'value': 25}),
            ('Orlov\'s Guns', 'Pháo của Orlov'),
            ('Linh has fixed three of Orlov\'s batteries by their muzzle flashes, marked in red. They move after every salvo. Hunt them in the dark.',
             'Linh đã định vị được ba khẩu đội của Orlov qua ánh chớp đầu nòng, đánh dấu màu đỏ. Chúng di chuyển sau mỗi loạt bắn. Săn chúng trong bóng tối.'),
            (('Muzzle flash', 'Chớp đầu nòng'),
             ('Linh\'s method, in her own words: "Count the seconds from the flash to the bang. Multiply. Draw a circle. Send Diều Hâu into the circle."',
              'Phương pháp của Linh, theo lời cô: "Đếm số giây từ lúc chớp sáng tới tiếng nổ. Nhân lên. Vẽ một vòng tròn. Cho Diều Hâu bay vào vòng tròn đó."')),
            [say('linh', 'Start', 'Three batteries. They shoot, they move, they shoot. Be quicker than the second shot.', 'Ba khẩu đội. Chúng bắn, chúng chạy, chúng lại bắn. Phải nhanh hơn loạt thứ hai.'),
             say('orlov', 'At', 'You found my guns. Remarkable. Also irrelevant.', 'Ngươi tìm ra pháo của ta. Đáng nể. Nhưng cũng chẳng để làm gì.', at=150)])

add_mission(m('c3m07', 3, 'whiteout', 'Protect', 'Fog', targets=['log_cabin', 'barn'], protectNeeded=1, targetHealth=22, surviveSeconds=390, general='orlov', reinforcements=2,
              enemyAi='both', enemyStance='Attack', difficulty='Normal', enemyCp=10, enemyIncome=0.8,
              enemyDeck=ORLOV, playerCp=26, playerIncome=1.4, playerCap=36, playerBase='Anchor',
              waves=waves(['light_tank', 'ifv', 'mortar_carrier', 'main_battle_tank', 'attack_helicopter'], first=90, interval=65, size=2, grow=0.3, max_size=4, max_alive=10),
              starTime=0, starLosses=10, challenge={'kind': 'NoAircraft'}),
            ('Cabins in the Snow', 'Những căn nhà gỗ trong tuyết'),
            ('The families of the pass have taken shelter in the cabins and the barn on the south side. Orlov is shelling everything that still has a roof. '
             'Keep at least one standing for seven minutes.',
             'Các gia đình trên đèo đã trú trong những căn nhà gỗ và nhà kho phía nam. Orlov đang nã pháo vào mọi thứ còn mái che. '
             'Giữ ít nhất một căn đứng vững trong bảy phút.'),
            (('Fifty-one', 'Năm mươi mốt người'),
             ('Fifty-one people spent the night in the barn. In the morning a girl asked Diều Hâu if the loud planes were his. He said yes, and that they were on her side.',
              'Năm mươi mốt người qua đêm trong nhà kho. Sáng ra, một cô bé hỏi Diều Hâu có phải mấy chiếc máy bay ầm ĩ kia là của chú không. Anh bảo phải, và chúng đứng về phía cháu.')),
            [say('khai', 'Start', 'Civilians in the cabins. They are the objective.', 'Dân thường trong các căn nhà gỗ. Họ chính là mục tiêu.')])

add_mission(m('c3m08', 3, 'whiteout', 'Boss', 'Snow', legacy='m18', general='varga', timeLimit=1200, reinforcements=3,
              boss=scripted('behemoth', (84, 84), heading=225, health=2.2, name='frozen_behemoth'),
              enemyAi='commander', enemyStance='Attack', difficulty='Hard', enemyCp=13, enemyIncome=0.85,
              enemyDeck=['main_battle_tank', 'heavy_tank', 'aa_vehicle', 'tank_destroyer', 'mlrs', 'ifv'],
              playerCp=26, playerIncome=1.45, playerCap=36, starTime=780, starLosses=12, challenge={'kind': 'NoStrikes'}),
            ('Frozen Behemoth', 'Behemoth Băng Giá'),
            ('The Behemoth from Dunebreak is back: Varga had it dragged north, repaired and heated for the snow, and lent it to Orlov. '
             'Heavier than before. Stop it for good.',
             'Chiếc Behemoth ở Dunebreak đã quay lại: Varga cho kéo nó lên phía bắc, sửa chữa, lắp hệ sưởi cho tuyết, rồi cho Orlov mượn. '
             'Nặng hơn trước. Chặn đứng nó vĩnh viễn.'),
            (('A loan', 'Khoản cho mượn'),
             ('Varga to Orlov: "Return it with a full tank." Orlov to Varga, a week later: "Returned in several pieces. Tank empty."',
              'Varga gửi Orlov: "Trả lại nhớ đổ đầy bình." Orlov gửi Varga, một tuần sau: "Đã trả, thành nhiều mảnh. Bình rỗng."')),
            [say('mai', 'Start', 'They patched it. Badly. The rear plates are still mine.', 'Chúng vá lại nó rồi. Vá ẩu. Giáp sau vẫn là của tôi.'),
             say('varga', 'Boss', 'I fixed her, Colonel. I always fix her.', 'Ta đã sửa lại nó, đại tá. Ta luôn sửa được nó.')])

add_mission(m('c3m09', 3, 'frostpeak', 'Duel', 'Clear', targetHealth=0.4, general='orlov', enemyBase='Target', enemyHq=2, replay=True, reinforcements=3, timeLimit=1500,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=10, enemyIncome=0.56,
              playerCp=28, playerIncome=2.25, playerCap=38, playerBase='Anchor', starTime=840, starLosses=12),
            ('Orlov\'s Gun Line', 'Trận địa pháo của Orlov'),
            ('Orlov\'s headquarters sits behind a wall of artillery emplacements, where he can see the whole valley. Break through and level it. He will not wait for you.',
             'Sở chỉ huy của Orlov nằm sau một bức tường ụ pháo, nơi hắn nhìn thấy cả thung lũng. Chọc thủng và san phẳng nó. Hắn sẽ không chờ ta đâu.'),
            (('Orlov\'s notebook', 'Sổ tay của Orlov'),
             ('Every page of Orlov\'s notebook is numbers: ranges, times, weights of shell. On the last page, one word, underlined: "Why?" Nobody knows what he was asking.',
              'Trang nào trong sổ tay của Orlov cũng toàn con số: tầm bắn, thời gian, trọng lượng đạn. Ở trang cuối có một chữ, gạch chân: "Tại sao?" Không ai biết hắn đã tự hỏi điều gì.')),
            [say('orlov', 'Start', 'Fire mission. Grid one-seven. All batteries.', 'Nhiệm vụ bắn. Ô lưới một-bảy. Toàn bộ khẩu đội.'),
             say('orlov', 'Win', 'Recalculating. Withdraw the batteries to the next line.', 'Tính lại. Rút các khẩu đội về tuyến sau.')])

add_mission(m('c3m10', 3, 'frostpeak', 'Destroy', 'Overcast', variant='siege', legacy='m09', operation=True, general='orlov', reinforcements=3,
              enemyAi='both', enemyStance='Defend', difficulty='Normal', enemyCp=15, enemyIncome=0.95,
              enemyDeck=ORLOV, playerCp=30, playerIncome=2.0, playerCap=42, playerBase='Anchor', enemyHq=3,
              waves=waves(['main_battle_tank', 'ifv', 'mlrs', 'attack_helicopter', 'heavy_tank'], first=80, interval=60, size=2, grow=0.3, max_size=5, max_alive=12,
                          spawns=[(100, 60), (60, 100)]),
              stages=[
                  {'stage': 'radar', 'goal': 'Destroy', 'targets': ['radar_station'], 'targetX': -56.25, 'targetZ': 116, 'targetRadius': 20, 'targetHealth': 3, 'cp': 8,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.khai.c3m10.s1'}],
                   'choices': [{'key': 'depots', 'next': 'depots'}, {'key': 'radars', 'next': 'radars'}]},
                  {'stage': 'depots', 'goal': 'Destroy', 'targets': ['fuel_depot'], 'targetHealth': 2, 'cp': 6, 'next': 'fortress',
                   'events': [{'at': 'end', 'kind': 'Income', 'team': 1, 'amount': 0.7}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.enemyWeakened'}]},
                  {'stage': 'radars', 'goal': 'Destroy', 'targets': ['radar_station'], 'targetX': 79, 'targetZ': 79, 'targetRadius': 46, 'targetHealth': 2, 'cp': 6, 'next': 'fortress',
                   'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'airstrike', 'every': 50}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.alliedStrikes'}]},
                  {'stage': 'fortress', 'goal': 'Boss', 'boss': scripted('mobile_fortress', (90, 90), heading=225, health=1.3), 'cp': 10,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.orlov.c3m10.s4'}]},
                  {'stage': 'gate', 'goal': 'Survive', 'surviveSeconds': 300,
                   'events': [{'at': 'start', 'kind': 'Radio', 'key': 'radio.orlov.c3m10.s5'},
                              {'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'mlrs', 'sam_launcher', 'main_battle_tank']},
                              {'at': '190', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'artillery', 'ifv']}]},
              ],
              starTime=1380, starLosses=16),
            ('The Frostpeak Line', 'Tuyến Frostpeak'),
            ('The last station of the radar line, the fortress behind it, and the Ice Fortress guarding its gate. '
             'Blind the hill radar, choose your second blow, destroy the Ice Fortress, and hold its gate against Orlov\'s counterattack.',
             'Trạm cuối của tuyến radar, pháo đài phía sau nó, và Pháo Đài Băng canh cổng. '
             'Làm mù radar trên đồi, chọn đòn thứ hai, tiêu diệt Pháo Đài Băng, rồi giữ cổng trước đợt phản kích của Orlov.'),
            (('Spring', 'Mùa xuân'),
             ('The day the Frostpeak line fell, the thaw began. The engineers swear the two are not connected. The villagers do not believe the engineers.',
              'Ngày tuyến Frostpeak sụp đổ, băng bắt đầu tan. Công binh thề rằng hai chuyện chẳng liên quan gì nhau. Dân làng không tin công binh.')),
            [say('khai', 'Start', 'The line breaks today, or the winter wins. Move.', 'Hôm nay tuyến phải vỡ, không thì mùa đông thắng. Tiến lên.'),
             say('khai', 'Win', 'The highlands are open. Act one is done, Brigade.', 'Cao nguyên đã mở. Hồi thứ nhất khép lại rồi, Lữ đoàn.')],
            stages_text={'radar': ('Blind the Hill Radar', 'Làm mù radar trên đồi'), 'depots': ('Blow the Fuel Depots', 'Cho nổ kho nhiên liệu'),
                         'radars': ('The Fortress Radars', 'Radar của pháo đài'), 'fortress': ('The Ice Fortress', 'Pháo Đài Băng'), 'gate': ('Hold the Gate', 'Giữ cổng')},
            choices_text={'depots': (('Blow the fuel depots', 'Cho nổ kho nhiên liệu'), ('Orlov\'s army earns 30 % less for the rest of the battle.', 'Quân Orlov kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')),
                          'radars': (('Destroy the fortress radars', 'Phá radar của pháo đài'), ('Free airstrikes about every 50 s for the rest of the battle.', 'Không kích miễn phí khoảng mỗi 50 giây trong suốt phần còn lại của trận.'))})
T('radio.khai.c3m10.s1', 'The hill radar first. Without it, his guns fire blind.', 'Radar trên đồi trước. Mất nó, pháo của hắn bắn mù.')
T('radio.orlov.c3m10.s5', 'All batteries, the gate. Bury them in it.', 'Toàn bộ khẩu đội, nhắm cổng. Chôn chúng ở đó.')
T('radio.orlov.c3m10.s4', 'The Ice Fortress will hold the gate. It always has.', 'Pháo Đài Băng sẽ giữ cổng. Xưa nay vẫn thế.')

add_mission(m('c3s1', 3, 'frostpeak', 'Recon', 'Fog', side=True, after='c3m03', speaker='linh', points=['west', 'town', 'east'], timeLimit=840, reinforcements=1,
              enemyAi='commander', enemyStance='Defend', difficulty='Normal', enemyCp=13, enemyIncome=0.85,
              enemyDeck=ORLOV, playerCp=24, playerIncome=1.4, rarePrints=26, starTime=420, starLosses=6),
            ('Where the Guns Are', 'Pháo nằm ở đâu'),
            ('Before the big push, Linh wants every gun position round Frostpeak on her map. Put a vehicle on the radar hill, the village and the lumber camp, in the fog.',
             'Trước trận đánh lớn, Linh muốn mọi trận địa pháo quanh Frostpeak có mặt trên bản đồ của cô. Đưa xe tới đồi radar, ngôi làng và trại gỗ, trong sương mù.'),
            (('Paper map', 'Bản đồ giấy'),
             ('Linh keeps her maps on paper. "Hegemon reads our radio," she says. "Hegemon does not read my handwriting. Nobody does."',
              'Linh giữ bản đồ trên giấy. "Hegemon đọc được sóng vô tuyến của ta," cô nói. "Hegemon không đọc được chữ tôi. Chẳng ai đọc được."')),
            [say('linh', 'Start', 'Look and leave. The fog helps both sides.', 'Nhìn rồi rút. Sương mù giúp cả hai bên đấy.')])

add_mission(m('c3s2', 3, 'whiteout', 'Escort', 'Night', side=True, after='c3m07', speaker='linh', convoyCount=5, convoyNeeded=3, reinforcements=1, timeLimit=1000,
              convoy=scripted('supply_truck', (-100, -100), route=[(-84.8, -74.2), (-53, -53), (-33, -33), (0, 0), (-40, 40), (-71.25, 71.25)], heading=45),
              units=units(0, ['main_battle_tank', 'heavy_aa', 'ifv'], (-90, -90), 6),
              enemyAi='waves', difficulty='Normal',
              waves=waves(['light_tank', 'ifv', 'mortar_carrier', 'attack_helicopter', 'main_battle_tank'], first=20, interval=30, size=2, grow=0.45, max_size=6, max_alive=13,
                          spawns=[(80, 60), (40, 100), (100, 10)]),
              towerGear='Rare', starTime=360, starLosses=6, challenge={'kind': 'Kills', 'value': 18}),
            ('Medical Convoy', 'Đoàn xe cứu thương'),
            ('Medicine and doctors for the signal post, where the wounded from the pass are waiting. Five trucks at night; three must get there.',
             'Thuốc men và bác sĩ cho trạm tín hiệu, nơi thương binh trên đèo đang chờ. Năm xe trong đêm; phải tới được ba xe.'),
            (('The doctor', 'Bác sĩ'),
             ('The convoy\'s doctor had worked for Hegemon\'s medical corps until the Night of Steel. Nobody asked her why she changed sides. She did not wait to be asked.',
              'Bác sĩ trong đoàn xe từng làm cho quân y Hegemon cho tới Đêm Thép. Không ai hỏi vì sao cô đổi phe. Cô cũng chẳng đợi ai hỏi.')),
            [say('linh', 'Start', 'The wounded cannot wait for daylight. Neither can we.', 'Thương binh không đợi được tới sáng. Ta cũng thế.')])

"""Prompt 22, pass 1, Act II: chapters 4-6 and interlude II (The Queen's Choice). See act5.py for the tools."""

import copy

import campaign_kit as kit
from campaign_kit import mission, retext, say
from act1 import VARGA_EARLY
from act2 import KESSLER, SEN, VARGA_LATE
from act4 import LY_HAN, stage
from act5 import WEAKEN, clone, mark, rewrite, stage_says, texts

# ====================================================================== chapter 4: Iron Harbor (Kessler)

# The port operation is a set piece now; the chapter ends on Leviathan (its main boss) off Beacon Bay.
d = mission('c4m10')
d.pop('operation', None)
d['replay'] = True
mark(d, set_piece=True)

d = rewrite('c4m06', brief=('Kessler has run for the sea. His command destroyer Scylla is blocking Beacon Bay in the fog while his fleet gets out. Sink it.',
                            'Kessler đã chạy ra biển. Tàu khu trục chỉ huy Scylla của ông ta đang chặn Beacon Bay trong sương cho hạm đội rút đi. Đánh chìm nó.'))

# c4m11: Leviathan, the chapter's operation: the lighthouse, the old coastal batteries, the fishing village, the flagship.
d = mission('c4m11')
for k in ('epilogue', 'timeLimit', 'replay'):
    d.pop(k, None)
leviathan = d.pop('boss')
d.update(goal='Capture', operation=True)
d['stages'] = [
    {'stage': 'lighthouse', 'goal': 'Capture', 'points': ['east'], 'enemyOwns': ['west', 'town', 'east'], 'cp': 8,
     'choices': [{'key': 'battery', 'next': 'battery'}, {'key': 'strikes', 'next': 'strikes'}]},
    {'stage': 'battery', 'goal': 'Capture', 'points': ['west'], 'enemyOwns': ['west'], 'cp': 8, 'next': 'village',
     'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'artillery_barrage', 'every': 50}]},
    {'stage': 'strikes', 'goal': 'Survive', 'points': ['east'], 'surviveSeconds': 150, 'cp': 8, 'next': 'village',
     'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'airstrike', 'every': 55}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.alliedStrikes'}]},
    {'stage': 'village', 'goal': 'Capture', 'points': ['town'], 'enemyOwns': ['town'], 'cp': 8,
     'events': [{'at': 'start', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'ifv', 'wheeled_gun']}]},
    {'stage': 'leviathan', 'goal': 'Boss', 'boss': leviathan, 'cp': 0},
]
retext('mission.c4m11.brief', 'Kessler is aboard Leviathan off Beacon Bay with what is left of his fleet, shelling the coast. Take the lighthouse to see his ships, '
       'choose your guns, take the fishing village, then sink the flagship from the shore.',
       'Kessler đang ở trên Leviathan ngoài khơi Beacon Bay cùng phần còn lại của hạm đội, nã pháo vào bờ biển. Chiếm ngọn hải đăng để thấy tàu của ông ta, '
       'chọn hỏa lực, chiếm làng chài, rồi đánh chìm soái hạm từ trên bờ.')
for key, text in {'lighthouse': ('The Lighthouse', 'Ngọn hải đăng'), 'battery': ('The Old Batteries', 'Trận địa pháo cũ'), 'strikes': ('Air Cover', 'Yểm trợ trên không'),
                  'village': ('The Fishing Village', 'Làng chài'), 'leviathan': ('Leviathan', 'Leviathan')}.items():
    retext(f'stage.c4m11.{key}', *text)
retext('choice.c4m11.battery', 'Man the coastal batteries', 'Chiếm trận địa pháo bờ biển')
retext('choice.c4m11.battery.info', 'The old coastal guns fire on the enemy every minute for the rest of the battle.', 'Pháo bờ biển cũ nã vào quân địch mỗi phút trong suốt phần còn lại của trận.')
retext('choice.c4m11.strikes', 'Call the air wing', 'Gọi không quân')
retext('choice.c4m11.strikes.info', 'Air strikes on call, every minute, for the rest of the battle.', 'Không kích theo yêu cầu, mỗi phút một lượt, trong suốt phần còn lại của trận.')
stage_says(d, 'lighthouse', 'khai', 's1', 'The lighthouse first. From up there we see his whole fleet.', 'Ngọn hải đăng trước. Từ trên đó ta thấy cả hạm đội của hắn.')
stage_says(d, 'battery', 'mai', 's2', 'The old guns still turn. Give me a minute and they fire.', 'Pháo cũ vẫn xoay được. Cho tôi một phút là chúng bắn.', at='end')
stage_says(d, 'leviathan', 'kessler', 's4', 'Leviathan, all turrets. Clear the shore.', 'Leviathan, toàn bộ tháp pháo. Dọn sạch bờ biển.')
rewrite('c4m11', lines=[say('kessler', 'Win', 'Abandon ship. Record the loss, and the time.', 'Bỏ tàu. Ghi lại khoản lỗ, và cả giờ giấc.')])

d = clone('c4m02', 'c4m12', 4, flip=True, weather='Rain', playerBase='Anchor', general='kessler', enemyDeck=KESSLER, speaker='adler')
texts(d, ('Flag\'s Strongpoints', 'Các cứ điểm của Flag'),
      ('Captain Adler wants the three strongpoints along the harbour wall, and he wants his flag on each by noon. Take them from the landward side, in the rain.',
       'Đại úy Adler muốn ba cứ điểm dọc tường cảng, và muốn cờ của anh cắm trên từng cái trước trưa. Chiếm chúng từ phía đất liền, trong mưa.'),
      (('Four flags', 'Bốn lá cờ'),
       ('Adler planted a flag on each strongpoint and a fourth on the harbour master\'s office, which nobody had asked him to take.',
        'Adler cắm một lá cờ lên từng cứ điểm, và lá thứ tư lên văn phòng trưởng cảng, nơi chẳng ai bảo anh chiếm.')),
      [say('adler', 'Start', 'Three forts, three flags. I brought four, just in case.', 'Ba pháo đài, ba lá cờ. Tôi mang bốn lá, phòng khi cần.'),
       say('adler', 'Win', 'Flags up! All three, and one spare for the office.', 'Cờ đã cắm! Cả ba, thêm một lá cho văn phòng.')])

d = clone('c4s2', 'c4m16', 4, flip=True, weather='Overcast', playerBase='None', general='kessler', enemyDeck=KESSLER, speaker='linh')
texts(d, ('The Cargo Manifests', 'Bản kê hàng'),
      ('Two of Kessler\'s command cars are carrying the port\'s manifests out of Ironport, and Nadia wants to know what he has been shipping. Stop both before they reach the gate.',
       'Hai xe chỉ huy của Kessler đang chở bản kê hàng của bến cảng ra khỏi Ironport, và Nadia muốn biết ông ta đã chở những gì. Chặn cả hai trước khi chúng ra tới cổng.'),
      (('Heavy cargo', 'Hàng nặng'),
       ('The manifests listed Behemoth hulls by the dozen, shipped from Varga\'s works to wherever Hegemon was losing. One line was underlined twice: "Tempest. Quay 4. Do not unload."',
        'Bản kê ghi hàng chục vỏ Behemoth, chở từ xưởng của Varga tới bất cứ nơi nào Hegemon đang thua. Một dòng được gạch chân hai lần: "Tempest. Cầu tàu 4. Không dỡ hàng."')),
      [say('linh', 'Start', 'Two cars, marked. I want their paperwork, not their drivers.', 'Hai xe, đã đánh dấu. Tôi cần giấy tờ của chúng, không cần tài xế.'),
       say('linh', 'Win', 'Varga\'s Behemoths, by the shipload. One called Tempest is still on the quay.', 'Behemoth của Varga, từng chuyến tàu một. Một chiếc tên Tempest vẫn nằm trên cầu tàu.')])

d = clone('c3m03', 'c4m13', 4, map_='rustyard', weather='Rain', general='kessler', enemyDeck=KESSLER)
texts(d, ('The Empty Flank', 'Sườn bỏ trống'),
      ('Thorne\'s column was to cover our left while we hold the foundry crossing. It has not arrived. Hold the crossing alone for three and a half minutes.',
       'Cánh quân của Thorne lẽ ra phải che sườn trái trong lúc ta giữ ngả qua xưởng đúc. Nó chưa tới. Một mình giữ ngả qua trong ba phút rưỡi.'),
      (('Where was Thorne?', 'Thorne ở đâu?'),
       ('Thorne\'s column arrived an hour after the fighting, apologised, and blamed a broken bridge. Nadia went to look at the bridge the next morning. It was fine.',
        'Cánh quân của Thorne tới một giờ sau khi trận đánh kết thúc, xin lỗi, và đổ cho một cây cầu gãy. Sáng hôm sau Nadia tới xem cây cầu. Nó vẫn nguyên vẹn.')),
      [say('linh', 'Start', 'Thorne\'s column is not on our left. It is not anywhere.', 'Cánh quân của Thorne không có ở sườn trái. Không có ở đâu cả.'),
       say('linh', 'Win', 'I have a question for General Thorne. Nobody will want to hear it.', 'Tôi có một câu hỏi cho tướng Thorne. Sẽ chẳng ai muốn nghe đâu.')])

d = clone('c2m01', 'c4m14', 4, map_='rustyard', weather='Clear', playerBase='None', general='kessler', enemyDeck=KESSLER)
d['waves'].pop('spawns', None)
d['waves']['roster'] = ['wheeled_gun', 'ifv', 'main_battle_tank', 'mine_layer', 'mlrs']
texts(d, ('Kessler Runs for the Sea', 'Kessler chạy ra biển'),
      ('Kessler is putting his staff on the last ships at the rail pier, and his rearguard is holding the Rust Yard to buy him time. We cannot stop the ships today. '
       'Survive the rearguard for five minutes and the yard is ours.',
       'Kessler đang đưa bộ tham mưu lên những con tàu cuối cùng ở cầu tàu đường sắt, và quân đoạn hậu giữ Rust Yard để câu giờ cho ông ta. Hôm nay ta không chặn được những con tàu. '
       'Trụ vững trước quân đoạn hậu năm phút là bãi ray thuộc về ta.'),
      (('Courtesy', 'Phép lịch sự'),
       ('Kessler\'s ship left the pier at eighteen hundred exactly. He radioed the time to the brigade, as a courtesy.',
        'Tàu của Kessler rời cầu tàu đúng mười tám giờ. Ông ta còn báo giờ cho lữ đoàn qua bộ đàm, như một phép lịch sự.')),
      [say('kessler', 'Start', 'My ship leaves at eighteen hundred, Colonel. Do not be late.', 'Tàu của ta rời bến lúc mười tám giờ, đại tá. Đừng tới trễ.'),
       say('khai', 'Win', 'He is at sea. Let him go. We meet his fleet at Beacon Bay.', 'Hắn ra biển rồi. Cứ để hắn đi. Ta sẽ gặp hạm đội của hắn ở Beacon Bay.')])

d = clone('c3m03', 'c4m15', 4, map_='lighthousebay', weather='Night', playerBase='None', general='kessler', enemyDeck=KESSLER)
texts(d, ('Night at the Fishing Village', 'Đêm ở làng chài'),
      ('Kessler\'s landing parties are coming ashore at Beacon Bay. Hold the fishing village through the night while our guns come up the coast road.',
       'Các toán đổ bộ của Kessler đang lên bờ ở Beacon Bay. Giữ làng chài suốt đêm trong lúc pháo của ta tiến lên theo đường ven biển.'),
      (('Lanterns', 'Đèn lồng'),
       ('The fishermen hung their lanterns along the harbour wall all night, so the landing craft could not see the beach. None came ashore at the village.',
        'Ngư dân treo đèn lồng dọc tường cảng suốt đêm để xuồng đổ bộ không nhìn rõ bãi biển. Không chiếc nào cập được bờ ở làng.')),
      [say('khai', 'Start', 'Hold the village till dawn. The guns are on their way.', 'Giữ làng tới sáng. Pháo đang trên đường tới.'),
       say('mai', 'Win', 'The guns are up. From here we can reach the bay.', 'Pháo đã vào vị trí. Từ đây ta với tới được cả vịnh.')])

# ====================================================================== chapter 5: Burning Canopy (Venn)

mark(mission('c5m06'), set_piece=True)
retext('radio.khai.c5m10.2', 'Venn is coming out? …Bring her in. Carefully.', 'Venn đang đi ra à? …Đưa bà ấy về. Cẩn thận.')
rewrite('c5m09', lines=[say('linh', 'Win', 'Venn\'s traffic has one Accord call sign in it: Titan. That is Thorne\'s.',
                            'Liên lạc của Venn có đúng một mật danh của Accord: Titan. Đó là của Thorne.')])
rewrite('c5s1', name=('Venn\'s Notebooks', 'Sổ ghi chép của Venn'),
        brief=('Venn kept field stations in the pass, off Hegemon\'s books. Nadia wants eyes on all three before anyone clears them out.',
               'Venn có các trạm thực địa trong đèo, không ghi trong sổ sách của Hegemon. Nadia muốn tận mắt thấy cả ba trước khi có người dọn sạch chúng.'),
        fragment=(('Margins', 'Ghi chú bên lề'),
                  ('The notebooks were full of rescue drills: how many drones it takes to find one child under a collapsed school. '
                   'In the margins, in red, in someone else\'s hand: "Increase payload."',
                   'Các cuốn sổ đầy những bài tập cứu hộ: cần bao nhiêu drone để tìm một đứa trẻ dưới ngôi trường sập. '
                   'Bên lề, bằng mực đỏ, nét chữ của người khác: "Tăng tải trọng."')))

d = clone('c5s1', 'c5m11', 5, map_='emberridge', weather='Fog', general='sen', enemyDeck=SEN, speaker='linh')
texts(d, ('The Laboratory Signal', 'Tín hiệu phòng thí nghiệm'),
      ('Nadia has traced a signal to a laboratory in the ridge that Hegemon\'s own maps leave out. Put a vehicle on each of the three marked buildings. Venn may be inside.',
       'Nadia lần theo một tín hiệu tới một phòng thí nghiệm trên sườn núi mà chính bản đồ của Hegemon bỏ sót. Đưa xe tới từng tòa nhà đã đánh dấu. Có thể Venn đang ở trong.'),
      (('Her voice', 'Giọng của bà'),
       ('Venn spoke once on the open channel, calmly, as if to a colleague: the swarms were made to find people under rubble. Then she asked us to leave the building standing. We did.',
        'Venn lên kênh mở đúng một lần, điềm tĩnh như nói với đồng nghiệp: bầy drone được làm ra để tìm người dưới đống đổ nát. Rồi bà xin ta để tòa nhà đứng nguyên. Ta làm theo.')),
      [say('linh', 'Start', 'The signal comes from here. Look, and do not shoot the building.', 'Tín hiệu phát ra từ đây. Nhìn thôi, đừng bắn vào tòa nhà.'),
       say('sen', None, 'Dr Venn here. I built the swarm to find people under rubble.', 'Tiến sĩ Venn đây. Tôi làm ra bầy drone để tìm người dưới đống đổ nát.', at=45),
       say('linh', 'Win', 'She could have jammed us. She didn\'t.', 'Bà ấy có thể gây nhiễu ta. Nhưng bà ấy không làm.')])

d = clone('c5m01', 'c5m12', 5, flip=True, playerBase='Anchor', general='sen', enemyDeck=SEN)
texts(d, ('Around the Back', 'Vòng ra phía sau'),
      ('Venn\'s outer guard watches the pass from the south. Come round through the north villages and take the whole pass from behind, in the rain.',
       'Quân canh vòng ngoài của Venn nhìn về đèo từ phía nam. Vòng qua các làng phía bắc và chiếm cả đèo từ phía sau, trong mưa.'),
      (('The long way', 'Đường vòng'),
       ('The engineers cut a road through the jungle in two nights. The villagers called it the brigade\'s road, and still do.',
        'Công binh mở một con đường xuyên rừng trong hai đêm. Dân làng gọi nó là đường của lữ đoàn, tới giờ vẫn gọi thế.')),
      [say('khai', 'Start', 'The long way round. They will be looking the wrong way.', 'Đi đường vòng. Chúng sẽ nhìn nhầm hướng.'),
       say('linh', 'Win', 'The pass is ours from both ends now.', 'Giờ ta giữ đèo từ cả hai đầu.')])

d = clone('c3m03', 'c5m13', 5, map_='junglepass', weather='Night', playerBase='None', general='sen', enemyDeck=SEN)
texts(d, ('The Temple at Night', 'Ngôi đền trong đêm'),
      ('The temple ford is the only crossing the swarm cannot see through the canopy. Hold it through the night.',
       'Bến lội qua ngôi đền là ngả qua duy nhất bầy drone không nhìn thấu được qua tán rừng. Giữ nó suốt đêm.'),
      (('The swarm turned back', 'Bầy drone quay đầu'),
       ('At two in the morning the swarm came down the river like a second river. At three it turned back. Nobody knew why until Venn told us, much later: she had called it off.',
        'Hai giờ sáng, bầy drone tràn xuống theo dòng sông như một dòng sông thứ hai. Ba giờ, nó quay đầu. Không ai hiểu vì sao, cho tới rất lâu sau Venn mới kể: chính bà đã gọi nó về.')),
      [say('khai', 'Start', 'Hold the ford till morning. The canopy hides us; keep it that way.', 'Giữ bến lội tới sáng. Tán rừng che cho ta; cứ giữ như thế.'),
       say('mai', 'Win', 'Morning. And we are all still here.', 'Sáng rồi. Và tất cả ta vẫn còn đây.')])

# ====================================================================== chapter 6: Counterstrike (Varga; Brandt on our side)

d = mark(mission('c6m03'), set_piece=True)
rewrite('c6m03', fragment=(('Matilda', 'Matilda'),
                           ('Mara named the captured Behemoth "Matilda". Its crew painted a flower on the rear plates, over the weld she had never told anyone about.',
                            'Mara đặt tên chiếc Behemoth bắt được là "Matilda". Kíp lái vẽ một bông hoa lên tấm giáp sau, đè lên đường hàn cô chưa từng kể với ai.')))
retext('radio.hung.c6m10.s4', 'Kade! Thorne here. We are on the road. Hold on a little longer.', 'Kade! Thorne đây. Chúng tôi đang trên đường. Cố thêm chút nữa.')
retext('radio.khai.c6m10.2', 'The dam holds. The counterstrike is broken, Brigade.', 'Con đập trụ vững. Cuộc tổng phản công đã vỡ, Lữ đoàn.')
rewrite('c6m10', lines=[say('linh', 'Win', 'Thorne\'s army is here. Late, again.', 'Quân của Thorne tới rồi. Lại muộn.')])

d = clone('c1m07', 'c6m11', 6, general='varga', enemyDeck=VARGA_LATE, legacy='m22')
d['waves']['roster'] = ['main_battle_tank', 'ifv', 'flame_tank', 'tank_destroyer']
texts(d, ('Harvest Guard', 'Canh mùa gặt'),
      ('Varga\'s counterstrike has reached Greenvale, and Aurel wants its grain silos and water tower burned so the valley starves this winter. Keep at least one standing through the storm.',
       'Cuộc tổng phản công của Varga đã tới Greenvale, và Aurel muốn đốt các si-lô thóc cùng tháp nước để cả thung lũng chết đói mùa đông này. Giữ ít nhất một công trình đứng vững qua cơn bão.'),
      (('Bread', 'Bánh mì'),
       ('The mill ran all night on the brigade\'s generators. In the morning the village baked bread for the whole front line.',
        'Cối xay chạy suốt đêm bằng máy phát của lữ đoàn. Sáng ra, cả làng nướng bánh mì cho toàn tuyến đầu.')),
      [say('khai', 'Start', 'Keep the silos standing. Greenvale fed us once.', 'Giữ các si-lô đứng vững. Greenvale từng nuôi ta.'),
       say('varga', None, 'Aurel\'s orders, not mine, Colonel. I am sorry for the bread.', 'Lệnh của Aurel, không phải của tôi, đại tá. Tôi tiếc cho chỗ bánh mì.', at=60)])

d = clone('c1s2', 'c6m12', 6, general='varga', enemyDeck=VARGA_LATE, speaker='linh')
texts(d, ('Spotters on the Bluffs', 'Trinh sát trên vách đá'),
      ('Varga\'s spotters are on the Stormbeach bluffs, calling in the landing Charybdis is about to make. Nadia has marked three teams. Hunt them in the rain.',
       'Trinh sát của Varga đang nấp trên vách đá Stormbeach, chỉ điểm cho cuộc đổ bộ Charybdis sắp tiến hành. Nadia đã đánh dấu ba tổ. Săn chúng trong mưa.'),
      (('The same bluffs', 'Những vách đá cũ'),
       ('The spotters had dug in exactly where Brandt\'s mortars had been on the first day. Brandt told us where to look.',
        'Trinh sát đã đào công sự đúng chỗ các khẩu cối của Brandt từng đặt vào ngày đầu tiên. Brandt chỉ cho ta chỗ cần tìm.')),
      [say('linh', 'Start', 'Three spotter teams, marked. Without them Charybdis lands blind.', 'Ba tổ trinh sát, đã đánh dấu. Không có chúng, Charybdis sẽ đổ bộ mù.'),
       say('brandt', None, 'Look under the third rock shelf. That is where I would sit.', 'Tìm dưới gờ đá thứ ba. Là tôi thì tôi sẽ ngồi ở đó.', at=25)])

d = clone('c1m04', 'c6m13', 6, map_='ashfield', weather='Rain', playerBase='Anchor', general='varga', enemyDeck=VARGA_LATE, speaker='brandt')
d['waves']['roster'] = ['main_battle_tank', 'ifv', 'tank_destroyer', 'flame_tank']
texts(d, ('Brandt\'s Line', 'Phòng tuyến của Brandt'),
      ('Major Brandt has come over to us, and he knows exactly where Varga will hit Ashfield. Take the town square, set up an outpost and hold it while his engineers raise the walls.',
       'Thiếu tá Brandt đã về phe ta, và ông biết chính xác Varga sẽ đánh vào Ashfield ở đâu. Chiếm quảng trường thị trấn, lập tiền đồn và giữ nó trong lúc công binh của ông dựng tường.'),
      (('Walls', 'Tường thành'),
       ('Brandt built the new line in two days and named every bunker after a man of his old garrison. He said they would have liked to be useful.',
        'Brandt dựng phòng tuyến mới trong hai ngày và đặt tên mỗi boong-ke theo một người lính trong đạo quân đồn trú cũ. Ông nói họ hẳn sẽ muốn được làm việc có ích.')),
      [say('brandt', 'Start', 'Varga comes by the east road. He always does. Walls there.', 'Varga sẽ tới theo đường phía đông. Lúc nào cũng vậy. Dựng tường ở đó.'),
       say('khai', 'Win', 'Good walls, Major.', 'Tường tốt đấy, thiếu tá.'),
       say('brandt', 'Win', 'The only kind I build, Colonel.', 'Tôi chỉ xây loại đó thôi, đại tá.')])

# The ceasefire at the Hollow Dam: Varga's guns silent until noon, Aurel's drones not; the only time Varga and Kade speak.
d = clone('c7m08', 'c6m14', 6, map_='hydrodam', weather='Clear', general='varga', enemyAi='waves', enemyDeck=SEN, speaker='khai')
d['convoy'] = dict(d['convoy'], x=0, z=0, heading=225, route=[-30, 0, -52, -12, -80, -60, -108, -104])
d['waves'] = dict(d['waves'], roster=['strike_drone', 'fpv_carrier', 'recon_drone'])
d['waves'].pop('spawns', None)
mark(d, set_piece=True)
texts(d, ('The Ceasefire', 'Ngừng bắn'),
      ('The Hollow Dam is cracking. For one morning Varga and Kade have agreed to hold their fire so the villages below can get out. '
       'Aurel\'s drones have agreed to nothing. Get the families over the bridge and down the road.',
       'Hollow Dam đang nứt. Trong đúng một buổi sáng, Varga và Kade đồng ý ngừng bắn để các làng bên dưới kịp chạy. '
       'Bầy drone của Aurel thì chẳng đồng ý gì cả. Đưa các gia đình qua cầu và xuống đường.'),
      (('Two old soldiers', 'Hai người lính già'),
       ('Varga and Kade spoke for four minutes on an open channel. Nobody wrote down what they said. Kade came off the radio and said only: "He is a soldier. That makes it worse."',
        'Varga và Kade nói chuyện bốn phút trên kênh mở. Không ai ghi lại họ đã nói gì. Kade rời bộ đàm và chỉ nói: "Ông ấy là một người lính. Thế mới khổ."')),
      [say('varga', 'Start', 'Colonel Kade. Varga. My guns are silent until noon. You have my word.', 'Đại tá Kade. Varga đây. Pháo của tôi im tới trưa. Tôi hứa danh dự.'),
       say('khai', None, 'Understood, General. Thank you.', 'Rõ, thưa tướng quân. Cảm ơn ông.', at=8),
       say('linh', None, 'Drones inbound. Not Varga\'s: Aurel\'s security net.', 'Drone đang tới. Không phải của Varga: mạng an ninh của Aurel.', at=45),
       say('varga', 'Win', 'Noon, Colonel. It was an honour. Now we are enemies again.', 'Tới trưa rồi, đại tá. Thật vinh dự. Giờ ta lại là kẻ thù.')])

d = clone('c6m04', 'c6m15', 6, weather='Overcast', playerBase='None', general='varga', enemyDeck=VARGA_LATE, speaker='linh')
texts(d, ('The Spillway Road', 'Đường tràn'),
      ('Varga\'s armour holds the spillway road below the dam: the power station, the bridge and the ford. Thorne promised to take the ford from the north. Take all three; do not wait for him.',
       'Thiết giáp của Varga giữ con đường tràn dưới chân đập: trạm phát điện, cây cầu và bến lội. Thorne hứa sẽ đánh bến lội từ phía bắc. Chiếm cả ba; đừng chờ ông ta.'),
      (('Radio silence', 'Im lặng vô tuyến'),
       ('Thorne\'s army kept radio silence for six hours that day. In that time Nadia logged one message from his headquarters, on a band the Accord does not use.',
        'Hôm đó quân của Thorne im lặng vô tuyến suốt sáu giờ. Trong khoảng ấy Nadia ghi được một bức điện từ sở chỉ huy của ông ta, trên một băng tần Accord không dùng.')),
      [say('linh', 'Start', 'Thorne\'s army went quiet an hour ago. Completely quiet.', 'Quân của Thorne im bặt từ một giờ trước. Im hoàn toàn.'),
       say('linh', 'Win', 'Colonel, one message from Thorne\'s HQ, on a Hegemon band. I am logging it.', 'Đại tá, một bức điện từ sở chỉ huy của Thorne, trên băng tần của Hegemon. Tôi ghi lại rồi.')])

d = clone('c1m03', 'c6m16', 6, flip=True, weather='Fog', playerBase='Anchor', general='varga', enemyDeck=VARGA_LATE, difficulty='Normal')
texts(d, ('Greenvale Again', 'Lại Greenvale'),
      ('Varga\'s armour has retaken the Greenvale crossroads, the village and the farm we took in the first days. Take them back from the other side, in the fog.',
       'Thiết giáp của Varga đã chiếm lại ngã tư Greenvale, ngôi làng và trang trại ta giành được những ngày đầu. Chiếm lại chúng từ phía bên kia, trong sương.'),
      (('Old tracks', 'Vết xích cũ'),
       ('The brigade\'s first tracks were still in the Greenvale mud, under Varga\'s.',
        'Những vết xích đầu tiên của lữ đoàn vẫn còn trên bùn Greenvale, bên dưới vết xích của Varga.')),
      [say('khai', 'Start', 'We took this valley once. We take it again.', 'Ta đã chiếm thung lũng này một lần. Giờ chiếm lại.'),
       say('varga', 'Win', 'You fight for every field, Colonel. I respect that.', 'Ông giành giật từng cánh đồng, đại tá. Tôi tôn trọng điều đó.')])

# ====================================================================== interlude II: The Queen's Choice (Venn's escort)

d = clone('c5m01', 'i2m01', 14, map_='swamp', weather='Fog', general='aurel', enemyDeck=SEN, speaker='mendez')
texts(d, ('Into Mirewood', 'Vào Mirewood'),
      ('Captain Mendez wants to be through Mirewood by dusk. Take the two villages and the sunken temple on the causeways, fast, in the fog.',
       'Đại úy Mendez muốn qua khỏi Mirewood trước chạng vạng. Chiếm hai ngôi làng và ngôi đền chìm trên các đường đắp, thật nhanh, trong sương.'),
      (('Passenger', 'Hành khách'),
       ('Venn rode in the second truck with a laptop on her knees and did not speak all day. Mendez said she was the best passenger she had ever had.',
        'Venn ngồi trên xe thứ hai với chiếc máy tính trên đùi và không nói một lời suốt cả ngày. Mendez bảo đó là hành khách tốt nhất cô từng chở.')),
      [say('mendez', 'Start', 'Three stops, no waiting. Dr Venn, keep your head down.', 'Ba điểm dừng, không chờ ai. Tiến sĩ Venn, cúi đầu xuống.'),
       say('sen', 'Win', 'Captain, you drive like someone is chasing you.', 'Đại úy, cô lái xe như thể có ai đang đuổi theo.'),
       say('mendez', 'Win', 'Someone is, Doctor.', 'Có người đuổi thật đấy, tiến sĩ.')])

d = clone('c12m05', 'i2m02', 14, flip=True, map_='swamp', weather='Rain', playerBase='Anchor', general='aurel', enemyDeck=SEN, speaker='mendez')
d['boss'].update(fallbackHealth=0.5)
texts(d, ('The First Locust', 'Chiếc Locust thứ nhất'),
      ('A Locust has found the convoy: a small drone carrier from Venn\'s own programme, hunting her by her radio signature. Bring it down before its swarm reaches the trucks.',
       'Một chiếc Locust đã tìm ra đoàn xe: một tàu mang drone cỡ nhỏ trong chính chương trình của Venn, săn bà theo dấu hiệu vô tuyến. Bắn hạ nó trước khi bầy drone tới được đoàn xe.'),
      (('Signature', 'Dấu hiệu'),
       ('Venn rebuilt her own radio in a swamp, in the rain, in forty minutes, so the second Locust would have to find her the hard way.',
        'Venn lắp lại chiếc bộ đàm của mình giữa đầm lầy, trong mưa, mất bốn mươi phút, để chiếc Locust thứ hai phải vất vả mới tìm ra bà.')),
      [say('sen', 'Boss', 'That is my Locust. It is looking for me. Aim for the hangar doors.', 'Đó là chiếc Locust của tôi. Nó đang tìm tôi. Nhắm vào cửa khoang chứa.'),
       say('mendez', 'Win', 'One down. Doctor, how many of those did you build?', 'Một chiếc rồi. Tiến sĩ, bà đã làm bao nhiêu chiếc như thế?'),
       say('sen', 'Win', 'Two.', 'Hai.')])

d = clone('c3m03', 'i2m03', 14, map_='borderbridge', weather='Overcast', enemyDeck=LY_HAN, speaker='mendez')
d.pop('general', None)
texts(d, ('The Great Bridge', 'Cây cầu lớn'),
      ('An Accord militia that wants Venn tried and hanged has reached the Border Crossing first, and it will not stand aside. Hold the great bridge until the convoy is over.',
       'Một toán dân quân Accord muốn đem Venn ra xử treo cổ đã tới Border Crossing trước, và chúng không chịu tránh đường. Giữ cây cầu lớn cho tới khi đoàn xe qua hết.'),
      (('Warrant', 'Lệnh bắt'),
       ('The militia carried a warrant for Venn signed by nobody the Accord had ever heard of. Kade kept it, framed, in his office.',
        'Toán dân quân mang theo lệnh bắt Venn do một người Accord chưa từng nghe tên ký. Kade giữ lại nó, đóng khung, trong văn phòng.')),
      [say('mendez', 'Start', 'Accord colours on the bridge, and their guns point at us.', 'Cờ Accord trên cầu, và súng của họ chĩa vào ta.'),
       say('khai', None, 'Hold the bridge. Nobody takes our passenger.', 'Giữ cầu. Không ai được bắt hành khách của ta.', at=10),
       say('sen', 'Win', 'They were right to hate me. Thank you for not letting them.', 'Họ ghét tôi là phải. Cảm ơn vì đã không để họ làm vậy.')])

d = clone('c12m05', 'i2m04', 14, flip=True, map_='borderbridge', weather='Night', playerBase='None', general='aurel', enemyDeck=SEN, speaker='mendez')
d['boss'].update(fallbackHealth=0.6)
texts(d, ('The Second Locust', 'Chiếc Locust thứ hai'),
      ('The second Locust has found the crossing. It is the last thing between Venn and the far bank. Bring it down and get her over.',
       'Chiếc Locust thứ hai đã tìm ra ngả qua. Nó là thứ cuối cùng chắn giữa Venn và bờ bên kia. Bắn hạ nó và đưa bà qua.'),
      (('The far bank', 'Bờ bên kia'),
       ('On the far bank Venn was offered a flight to anywhere she liked. She asked where the brigade was going next, and got back in the truck.',
        'Tới bờ bên kia, Venn được mời bay tới bất cứ đâu bà muốn. Bà hỏi lữ đoàn sẽ đi đâu tiếp, rồi leo trở lại lên xe.')),
      [say('sen', 'Boss', 'Its left rack jams after every third launch. I never fixed it.', 'Giàn phóng trái của nó kẹt sau mỗi lần phóng thứ ba. Tôi chưa bao giờ sửa.'),
       say('sen', 'Win', 'I will stay with the brigade, Colonel. If you will have me.', 'Tôi sẽ ở lại với lữ đoàn, đại tá. Nếu ông chịu nhận tôi.'),
       say('khai', 'Win', 'Welcome aboard, Doctor.', 'Chào mừng bà, tiến sĩ.')])

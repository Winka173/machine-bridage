"""Prompt 22, pass 1, Act III: chapters 7-9 and interlude III (Hawk and Raven). See act5.py for the tools."""

import campaign_kit as kit
from campaign_kit import mission, retext, say
from act3 import AIR_WAVES, AUREL_CITY, QUADEN
from act4 import LY_HAN, boss, stage
from act5 import ally, clone, mark, rewrite, stage_says, texts

OLD_QUARTER = ('map:veyra_old_quarter',)

# ====================================================================== chapter 7: Veyra (Thorne's betrayal)

# Aurel speaks on the radio for the first time in chapter 11 (C.4): his earlier lines go to others.
rewrite('c7m01', drop=('radio.aurel.c7m01.1',),
        lines=[say('linh', 'Start', 'Aurel\'s guard holds the park, the plaza and the car park. Street by street.', 'Cận vệ của Aurel giữ công viên, quảng trường và bãi đỗ xe. Từng con phố một.')])
rewrite('c7m09', drop=('radio.aurel.c7m09.1',),
        brief=('Hegemon\'s propaganda station speaks to the whole country every night from the radar dome by the palace. Tonight it will not. Destroy it.',
               'Đài tuyên truyền của Hegemon phát cho cả nước mỗi đêm từ mái vòm radar cạnh cung điện. Đêm nay thì không. Phá hủy nó.'),
        lines=[say('linh', 'Start', 'The dome carries every Hegemon broadcast in the country. Bring it down.', 'Mái vòm đó phát mọi chương trình của Hegemon trong cả nước. Hạ nó xuống.')])
mark(mission('c7m08'), set_piece=True)

# c7m05: Juggernaut comes back on the city's freight line (Nemesis is the chapter's end, C.4).
d = mission('c7m05')
d['boss'].update({'def': 'armored_train', 'name': 'armored_train'})
rewrite('c7m05', keep=False, name=('Juggernaut in the Streets', 'Juggernaut giữa phố'),
        brief=('Kessler\'s armoured train, Juggernaut, has been patched up and put on Metro City\'s freight line to carry Aurel\'s guard into the centre. '
               'When it reaches the depot it has a minute to unload its guns on us. Stop it first.',
               'Đoàn tàu bọc thép Juggernaut của Kessler đã được vá lại và đưa lên tuyến hàng hóa của Metro City để chở cận vệ của Aurel vào trung tâm. '
               'Tới kho ga, nó có một phút để dỡ pháo nã vào ta. Chặn nó trước.'),
        fragment=(('Second life', 'Kiếp thứ hai'),
                  ('Juggernaut\'s new plates were Metro City tram rails, welded on in a hurry. The trams ran again a month later, on new rails.',
                   'Các tấm giáp mới của Juggernaut là đường ray xe điện của Metro City, hàn vội vào. Một tháng sau xe điện chạy lại, trên đường ray mới.')),
        lines=[say('linh', 'Start', 'Juggernaut again, on the city freight line. Someone patched it up.', 'Lại là Juggernaut, trên tuyến hàng hóa trong thành phố. Có người đã vá nó lại.'),
               say('khai', 'Boss', 'Stop it before the depot. Everything on the train.', 'Chặn nó trước kho ga. Dồn hết vào đoàn tàu.'),
               say('khai', 'Win', 'Derailed twice. Kessler will send us the bill.', 'Hai lần trật bánh. Kessler sẽ gửi hóa đơn cho ta.')])

# c7m10: the liberation of Veyra; Thorne turns in the middle of it (prompt 5's ally who changes sides), Atlas covers his escape,
# and Nemesis is stopped at the edge of the centre.
d = mission('c7m10')
retext('mission.c7m10.name', 'Liberate Veyra', 'Giải phóng Veyra')
retext('mission.c7m10.brief', 'Veyra, with General Thorne\'s army and his base beside us. Take the bridgeheads, choose your blow, storm the palace and the square, '
       'and stop whatever Aurel sends last. Nadia has one more thing to say before we go: watch General Thorne.',
       'Veyra, với đạo quân và căn cứ của tướng Thorne bên cạnh. Chiếm các đầu cầu, chọn đòn đánh, đánh chiếm cung điện và quảng trường, '
       'rồi chặn thứ cuối cùng Aurel tung ra. Nadia còn một điều muốn nói trước khi xuất phát: hãy để mắt tới tướng Thorne.')
retext('mission.c7m10.fragment', 'Thorne\'s price, found in Aurel\'s safe: the Meridian Coast to govern once Icarus flew. Aurel had signed it. '
       'Nadia read it twice and put it in the file marked "Thorne", which was thicker than anyone had known.',
       'Cái giá của Thorne, tìm thấy trong két sắt của Aurel: quyền cai quản Meridian Coast khi Icarus cất cánh. Aurel đã ký. '
       'Nadia đọc hai lần rồi cất nó vào tập hồ sơ đề "Thorne", dày hơn mọi người vẫn tưởng.')
retext('radio.khai.c7m10.1', 'Veyra, Brigade. Together with Thorne\'s army.', 'Veyra, Lữ đoàn. Cùng đạo quân của Thorne.')
retext('radio.khai.c7m10.2', 'Veyra is free. Thorne got out with a third of the army. We will find him.', 'Veyra đã tự do. Thorne thoát được cùng một phần ba đạo quân. Ta sẽ tìm ra ông ta.')
retext('radio.hung.c7m10.s1', 'My army takes the left. Kade, take the right, and we meet at the palace.', 'Quân của tôi đánh cánh trái. Kade, cánh phải, ta gặp nhau ở cung điện.')
retext('radio.hung.c7m10.s4', 'Have you seen what they are about to launch, Kade? I have.', 'Anh đã thấy thứ họ sắp phóng lên chưa, Kade? Tôi thì thấy rồi.')
stage_says(d, 'palace', 'dahl', 's3', 'Longshot here. Guns on the palace approaches, on your call.', 'Longshot đây. Pháo đã căn vào các ngả tới cung điện, chờ lệnh anh.')
# Nadia sees the guns turn first.
s = stage(d, 'betrayal')
s['events'].insert(0, {'at': 'start', 'kind': 'Radio', 'key': retext('radio.linh.c7m10.s6', 'Thorne\'s guns are turning. On us! Off the square, now!',
                                                                      'Pháo của Thorne đang quay. Vào ta! Rời quảng trường, ngay!')})
d['stages'].append({'stage': 'nemesis', 'goal': 'Intercept', 'launchSeconds': 60, 'cp': 0,
                    'boss': {'def': 'nuke_train', 'name': 'nuke_train', 'x': 140, 'z': 0, 'heading': 270, 'route': [100, 0, 64, 0, 36, 0]},
                    'events': [{'at': 'start', 'kind': 'Radio', 'key': retext('radio.linh.c7m10.s7', 'Nemesis, on the east road. Stop it before the centre!', 'Nemesis, trên đường phía đông. Chặn nó trước khi tới trung tâm!')},
                               {'at': '6', 'kind': 'Radio', 'key': retext('radio.dahl.c7m10.s7', 'Longshot. Every gun on the east road. Firing.', 'Longshot. Toàn bộ pháo vào đường phía đông. Khai hỏa.')}]})
retext('stage.c7m10.nemesis', 'Nemesis', 'Nemesis')

d = clone('c7s2', 'c7m11', 7, general='aurel', enemyDeck=AUREL_CITY)
texts(d, ('Storm over Veyra', 'Bão trên Veyra'),
      ('Aurel\'s guard helicopters are hunting the resistance over the rooftops of Veyra in the storm. Bring fourteen of them down.',
       'Trực thăng của đội cận vệ Aurel đang săn quân kháng chiến trên các mái nhà Veyra giữa cơn bão. Bắn hạ mười bốn chiếc.'),
      (('Rooftops', 'Mái nhà'),
       ('The resistance had painted arrows on the rooftops for our gunners, pointing at Aurel\'s helicopter pads. Some of the arrows are still there.',
        'Quân kháng chiến sơn những mũi tên trên mái nhà cho pháo thủ của ta, chỉ về các bãi đáp trực thăng của Aurel. Vài mũi tên tới giờ vẫn còn.')),
      [say('dieuhau', 'Start', 'Fourteen birds over the roofs. Keep the launchers moving.', 'Mười bốn con chim trên mái nhà. Cho bệ phóng di chuyển liên tục.'),
       say('khai', 'Win', 'The sky over Veyra is ours.', 'Bầu trời Veyra là của ta.')])

d = clone('c7m01', 'c7m16', 7, flip=True, weather='Overcast', playerBase='None', general='aurel', enemyDeck=AUREL_CITY, speaker='linh')
d['ally'] = ally((-96, -80), ['main_battle_tank', 'heavy_tank', 'ifv', 'aa_vehicle', 'mlrs'], later=[(200, ['main_battle_tank', 'bmpt'])])
texts(d, ('Thorne\'s Wing', 'Cánh quân của Thorne'),
      ('General Thorne\'s army has joined us in Metro City. His wing takes the northern streets with ours: the park, the plaza and the car park, from the east side. '
       'Nadia has asked to ride with his staff.',
       'Đạo quân của tướng Thorne đã tới Metro City cùng ta. Cánh quân của ông đánh các phố phía bắc cùng quân ta: công viên, quảng trường và bãi đỗ xe, từ phía đông. '
       'Nadia xin được đi cùng bộ tham mưu của ông.'),
      (('Nadia\'s notes', 'Ghi chép của Nadia'),
       ('Nadia\'s notes from the day: Thorne\'s staff carry two radios each. His orders arrive before his officers ask for them. He looks at the sky more than at the map.',
        'Ghi chép của Nadia hôm đó: mỗi sĩ quan tham mưu của Thorne mang hai bộ đàm. Mệnh lệnh của ông tới trước cả khi cấp dưới xin. Ông nhìn lên trời nhiều hơn nhìn bản đồ.')),
      [say('hung', 'Start', 'Welcome to the city, Kade. My men will take the north side.', 'Chào mừng tới thành phố, Kade. Người của tôi sẽ đánh phía bắc.'),
       say('linh', None, 'Colonel, a word: watch Thorne. I mean it.', 'Đại tá, một lời thôi: hãy để mắt tới Thorne. Tôi nói thật đấy.', at=60),
       say('khai', 'Win', 'Noted, Nadia. He is on our side.', 'Ghi nhận, Nadia. Ông ấy đứng về phía ta.')])

d = mark(clone('c7m01', 'c7m12', 7, map_='veyra_old_quarter', weather='Night', playerBase='None', general='aurel', enemyDeck=AUREL_CITY), awaits=OLD_QUARTER)
texts(d, ('The Old Quarter Gate', 'Cổng Old Quarter'),
      ('The Old Quarter of Veyra is a maze of narrow streets round three squares, and Aurel\'s guard holds all three. Take them at night, street by street.',
       'Old Quarter của Veyra là một mê cung phố hẹp quanh ba quảng trường, và cận vệ của Aurel giữ cả ba. Chiếm chúng trong đêm, từng con phố một.'),
      (('Old streets', 'Phố cổ'),
       ('The Old Quarter\'s streets were built for carts. The brigade\'s tanks took the corners with a hand\'s breadth to spare, and took a few corners off.',
        'Phố của Old Quarter được xây cho xe ngựa. Xe tăng của lữ đoàn ôm cua chỉ còn cách tường một gang tay, và gạt mất vài góc tường.')),
      [say('khai', 'Start', 'Narrow streets. Keep the tanks together and the carriers close.', 'Phố hẹp. Giữ xe tăng đi cùng nhau và xe chở quân sát bên.'),
       say('linh', 'Win', 'Three squares, three districts free. The people are coming out.', 'Ba quảng trường, ba quận được giải phóng. Người dân đang ra đường.')])

d = clone('c2m05', 'c7m13', 7, map_='veyra_old_quarter', weather='Clear', general='aurel', enemyDeck=AUREL_CITY, speaker='mai')
d['boss'].pop('fleeAt', None)
d['boss']['health'] = 1.4
mark(d, awaits=OLD_QUARTER)
texts(d, ('Inferno in the Old Quarter', 'Inferno giữa Old Quarter'),
      ('Aurel\'s guard has an Inferno of its own, a second one from Varga\'s works, and it is burning the Old Quarter one street at a time. Stop it.',
       'Cận vệ của Aurel có một chiếc Inferno riêng, chiếc thứ hai từ xưởng của Varga, và nó đang đốt Old Quarter từng con phố một. Chặn nó lại.'),
      (('A second Inferno', 'Inferno thứ hai'),
       ('This Inferno had a different serial number and the same cooling line. Mara looked at the wreck for a long time and said Varga would never have used it on a city.',
        'Chiếc Inferno này mang số hiệu khác nhưng cùng một đường ống làm mát. Mara nhìn xác nó rất lâu rồi nói Varga sẽ không bao giờ dùng nó đánh vào một thành phố.')),
      [say('mai', 'Boss', 'Same design, same weak cooling line. Hit it behind the turret.', 'Cùng thiết kế, cùng đường ống làm mát yếu. Đánh vào phía sau tháp pháo.'),
       say('khai', 'Win', 'That is the last fire in the Old Quarter.', 'Đó là đám cháy cuối cùng ở Old Quarter.')])

d = clone('c7m06', 'c7m14', 7, map_='veyra_old_quarter', weather='Fog', general='aurel', enemyDeck=AUREL_CITY, speaker='dahl')
d['units'] = kit.units(0, ['artillery', 'artillery', 'mlrs', 'heavy_tank', 'heavy_aa', 'main_battle_tank'], (-4, -8), radius=8.0)
mark(d, awaits=OLD_QUARTER)
texts(d, ('Longshot\'s Guns', 'Pháo của Longshot'),
      ('Major Dahl has brought the brigade\'s guns into the Old Quarter\'s main square, and Aurel\'s guard wants them out. Hold the square for four minutes while Longshot ranges every bridge into the centre.',
       'Thiếu tá Dahl đã đưa pháo của lữ đoàn vào quảng trường chính của Old Quarter, và cận vệ của Aurel muốn đuổi chúng ra. Giữ quảng trường bốn phút trong lúc Longshot căn pháo vào mọi cây cầu dẫn vào trung tâm.'),
      (('Ranging shots', 'Phát bắn thử'),
       ('Dahl fired one ranging shot at each bridge into the centre and wrote the numbers on the square\'s fountain in chalk. The rain washed them off. He did not need them any more.',
        'Dahl bắn thử một phát vào mỗi cây cầu dẫn vào trung tâm rồi ghi số liệu bằng phấn lên đài phun nước của quảng trường. Mưa xóa sạch. Ông chẳng cần tới chúng nữa.')),
      [say('dahl', 'Start', 'Four minutes, and I will have every bridge in Veyra on the map.', 'Bốn phút, là tôi có mọi cây cầu ở Veyra trên bản đồ.'),
       say('dahl', 'Win', 'Ranged. Every bridge, to the metre.', 'Đã căn xong. Mọi cây cầu, chính xác tới từng mét.')])

d = mark(clone('c7s1', 'c7m15', 7, map_='veyra_old_quarter', weather='Rain', general='aurel', enemyDeck=AUREL_CITY, speaker='linh'), awaits=OLD_QUARTER)
texts(d, ('Narrow Streets', 'Phố hẹp'),
      ('Nadia wants to see the Old Quarter\'s three squares before the heavy fighting: who holds them, and whose flags fly over them. Get a vehicle into each, in the rain.',
       'Nadia muốn tận mắt thấy ba quảng trường của Old Quarter trước trận đánh lớn: ai đang giữ chúng, và cờ của ai bay trên đó. Đưa xe vào từng quảng trường, trong mưa.'),
      (('A guest', 'Một vị khách'),
       ('In the second square Nadia found Thorne\'s staff already there, and a Hegemon officer walking out of their command post. She photographed him. Nobody asked her for the photograph.',
        'Ở quảng trường thứ hai, Nadia thấy bộ tham mưu của Thorne đã có mặt, và một sĩ quan Hegemon bước ra từ sở chỉ huy của họ. Cô chụp ảnh hắn. Không ai hỏi cô tấm ảnh đó.')),
      [say('linh', 'Start', 'Three squares. I want to know who is really in each.', 'Ba quảng trường. Tôi muốn biết thật sự ai đang ở từng nơi.'),
       say('linh', 'Win', 'Thorne\'s staff had a guest from Hegemon. I have a photograph.', 'Bộ tham mưu của Thorne có một vị khách từ Hegemon. Tôi có ảnh.'),
       say('khai', 'Win', 'File it, Nadia. We have a city to take.', 'Cất vào hồ sơ đi, Nadia. Ta còn cả một thành phố phải chiếm.')])

d = clone('c7m01', 'c7m17', 7, flip=True, map_='capital', weather='Night', playerBase='None', general='aurel', enemyDeck=AUREL_CITY, speaker='dahl')
texts(d, ('The Bridges at Night', 'Những cây cầu trong đêm'),
      ('The centre of Veyra sits on its island behind three bridgeheads. Take the gardens, the palace square and the station from the far bank, at night, behind Dahl\'s shells.',
       'Trung tâm Veyra nằm trên hòn đảo sau ba đầu cầu. Chiếm khu vườn, quảng trường cung điện và nhà ga từ bờ bên kia, trong đêm, theo sau làn đạn của Dahl.'),
      (('Night crossing', 'Vượt cầu trong đêm'),
       ('The brigade crossed the east bridge with its lights off and Dahl\'s shells walking ahead of it, fifty metres at a time.',
        'Lữ đoàn vượt cây cầu phía đông với đèn tắt, và làn đạn của Dahl đi trước từng năm mươi mét một.')),
      [say('dahl', 'Start', 'Longshot here. I walk the shells ahead of you. Stay behind them.', 'Longshot đây. Tôi dẫn làn đạn đi trước. Bám sau nó.'),
       say('khai', 'Win', 'We are on the island. Hold what we have.', 'Ta đã lên đảo. Giữ chắc những gì đã chiếm.')])

d = clone('c2m01', 'c7m18', 7, map_='capital', weather='Fog', playerBase='None', general='aurel', enemyDeck=AUREL_CITY, speaker='dahl')
d['waves'].pop('spawns', None)
d['waves']['roster'] = ['main_battle_tank', 'bmpt', 'ifv', 'heavy_tank', 'gunship_heli']
texts(d, ('The River Line', 'Tuyến sông'),
      ('Aurel\'s guard is throwing everything it has at our river line before the last battle. Survive for five minutes; Dahl\'s guns will do the rest.',
       'Cận vệ của Aurel đang dồn mọi thứ vào tuyến sông của ta trước trận đánh cuối. Trụ vững năm phút; pháo của Dahl sẽ lo phần còn lại.'),
      (('Five minutes', 'Năm phút'),
       ('For five minutes the river line held under everything Aurel had. Thorne\'s army, a kilometre away, did not fire a shot. Nadia wrote down the time.',
        'Suốt năm phút, tuyến sông trụ vững trước mọi thứ Aurel có. Quân của Thorne, cách đó một cây số, không bắn một phát nào. Nadia ghi lại giờ giấc.')),
      [say('dahl', None, 'Longshot. Barrage on the far bank in ten. Heads down.', 'Longshot. Mười giây nữa pháo kích bờ bên kia. Cúi đầu xuống.', at=30),
       say('linh', 'Win', 'Thorne\'s army sat it out. Every minute of it.', 'Quân của Thorne ngồi yên. Suốt từng phút một.')])

# ====================================================================== chapter 8: Underworld (Thorne in Deepcut Mine)

mark(mission('c8m05'), set_piece=True)

d = clone('c4m02', 'c8m11', 8, map_='openpit', weather='Overcast', playerBase='Anchor', general='hung', enemyDeck=LY_HAN, speaker='varro')
d['ally'] = ally((-96, -80), ['scout_jeep', 'rocket_technical', 'armored_car', 'zu23_technical', 'rocket_technical', 'scout_jeep', 'armored_car'],
                 later=[(150, ['rocket_technical', 'armored_car', 'scout_jeep']), (330, ['zu23_technical', 'rocket_technical', 'armored_car'])])
texts(d, ('Tide Comes In', 'Thủy triều dâng'),
      ('Captain Varro\'s miners know every road into Deepcut Mine, and they have brought everything that still runs. Take the crusher plant, the pit floor and the ore loadout with them.',
       'Thợ mỏ của đại úy Varro thuộc mọi con đường vào Deepcut Mine, và họ mang theo mọi thứ còn chạy được. Cùng họ chiếm nhà máy nghiền, đáy hố và bãi xuất quặng.'),
      (('Everyone', 'Tất cả mọi người'),
       ('Varro\'s militia was two hundred miners in forty trucks and one bulldozer with a machine gun welded to its blade. Thorne\'s men had not expected the bulldozer.',
        'Dân quân của Varro là hai trăm thợ mỏ trên bốn mươi chiếc xe tải và một chiếc máy ủi có khẩu súng máy hàn trên lưỡi ủi. Người của Thorne không ngờ tới chiếc máy ủi.')),
      [say('varro', 'Start', 'Tide here. Every truck in the valley is with you, Colonel.', 'Tide đây. Mọi chiếc xe tải trong thung lũng đều theo ông, đại tá.'),
       say('varro', 'Win', 'Nobody holds a mine against the people who dug it.', 'Không ai giữ nổi khu mỏ trước chính những người đã đào ra nó.')])

d = clone('c1s1', 'c8m12', 8, map_='openpit', weather='Sandstorm', general='hung', enemyDeck=LY_HAN, speaker='quist')
texts(d, ('Magpie\'s Salvage', 'Chiến lợi phẩm của Magpie'),
      ('Sergeant Major Quist has found three depots in the pit that Thorne left in a hurry. Get a vehicle to each before his men come back for them. She will do the carrying.',
       'Thượng sĩ Quist đã tìm ra ba kho trong hố mỏ mà Thorne bỏ lại vội vàng. Đưa xe tới từng kho trước khi người của ông ta quay lại. Việc khuân vác để cô lo.'),
      (('Pockets', 'Túi áo'),
       ('Quist came back with two engines, a crate of shells, a Hegemon officer\'s coffee machine and a map of the pit\'s deepest bunker. She kept the coffee machine.',
        'Quist trở về với hai động cơ, một thùng đạn, chiếc máy pha cà phê của một sĩ quan Hegemon và tấm bản đồ boong-ke sâu nhất dưới hố. Cô giữ lại chiếc máy pha cà phê.')),
      [say('quist', 'Start', 'Three depots, all unguarded. My favourite kind.', 'Ba kho, không ai canh. Đúng loại tôi thích nhất.'),
       say('quist', 'Win', 'Engines, shells, and a map of Thorne\'s bunker. And a coffee machine.', 'Động cơ, đạn, và bản đồ boong-ke của Thorne. Thêm cái máy pha cà phê.'),
       say('mai', 'Win', 'A fortress under the pit. He is waiting for Icarus.', 'Một pháo đài dưới đáy mỏ. Ông ta đang chờ Icarus.')])

# ====================================================================== chapter 9: Rough Water (Thorne and Kessler's remnants)

mark(mission('c9m05'), set_piece=True)
d = rewrite('c9m10', keep=False, name=('Typhon Rising', 'Typhon trồi lên'),
            fragment=(('The last message', 'Tin nhắn cuối cùng'),
                      ('The last message from Typhon came four minutes after it sank, sent from a buoy: the coordinates of Project Icarus\'s launch site, and one line for Kade. '
                       '"Don\'t let me have been right." Divers searched the wreck for a week. They did not find Thorne.',
                       'Tin nhắn cuối từ Typhon tới bốn phút sau khi tàu chìm, gửi đi từ một chiếc phao: tọa độ bãi phóng của Dự án Icarus, và một câu cho Kade. '
                       '"Đừng để tôi đã đúng." Thợ lặn tìm trong xác tàu suốt một tuần. Họ không tìm thấy Thorne.')),
            lines=[say('khai', 'Start', 'This ends at sea, Brigade.', 'Chuyện này kết thúc trên biển, Lữ đoàn.'),
                   say('linh', 'Win', 'Typhon is down. A message came from it as it sank.', 'Typhon đã chìm. Có một tin nhắn phát ra từ nó lúc chìm.'),
                   say('hung', 'Win', 'Coordinates follow: Icarus launches from there. Don\'t let me have been right.', 'Tọa độ kèm theo: Icarus phóng từ đó. Đừng để tôi đã đúng.')])

d = clone('c1s1', 'c9m11', 9, map_='lighthousebay', weather='Clear', general='hung', enemyDeck=LY_HAN, speaker='sen')
texts(d, ('Signals under Beacon Bay', 'Tín hiệu dưới Beacon Bay'),
      ('Dr Venn has heard something under Beacon Bay: a submarine talking to the sky on a band nobody uses. Get a vehicle to the fort, the village and the lighthouse, so she can listen from all three.',
       'Tiến sĩ Venn nghe thấy một thứ dưới Beacon Bay: một tàu ngầm liên lạc với bầu trời trên một băng tần không ai dùng. Đưa xe tới pháo đài, làng chài và ngọn hải đăng để bà nghe từ cả ba nơi.'),
      (('Three ears', 'Ba đôi tai'),
       ('From the three posts Venn fixed the submarine to within a kilometre. Then she heard it answer something in orbit.',
        'Từ ba điểm nghe, Venn xác định được tàu ngầm trong phạm vi một cây số. Rồi bà nghe thấy nó trả lời một thứ gì đó trên quỹ đạo.')),
      [say('sen', 'Start', 'I need three ears on the water. The fort, the village, the lighthouse.', 'Tôi cần ba đôi tai trên mặt nước. Pháo đài, làng chài, ngọn hải đăng.'),
       say('sen', 'Win', 'A submarine, talking to a satellite. It is called Typhon.', 'Một tàu ngầm đang liên lạc với vệ tinh. Nó tên là Typhon.')])

d = clone('c1m03', 'c9m12', 9, map_='coralisles', weather='Clear', playerBase='Anchor', general='hung', enemyDeck=LY_HAN, difficulty='Normal')
texts(d, ('The Coral Keys', 'Coral Keys'),
      ('Thorne\'s sailors have taken the Coral Keys: two islands and the lighthouse between them. Take all three, and Venn can put her listening buoys in the channel.',
       'Thủy thủ của Thorne đã chiếm Coral Keys: hai hòn đảo và ngọn hải đăng ở giữa. Chiếm cả ba là Venn có thể thả phao nghe xuống eo biển.'),
      (('Buoys', 'Phao'),
       ('The buoys were fishing floats with Venn\'s microphones taped inside. The fishermen asked for them back after the war, microphones and all.',
        'Những chiếc phao là phao đánh cá có micrô của Venn dán bên trong. Sau chiến tranh, ngư dân xin lại chúng, cả micrô lẫn phao.')),
      [say('khai', 'Start', 'Two islands and a lighthouse. Take them, and the doctor gets her ears.', 'Hai hòn đảo và một ngọn hải đăng. Chiếm được là tiến sĩ có tai nghe.'),
       say('sen', 'Win', 'Buoys going in. Now we wait for it to speak.', 'Đang thả phao. Giờ chờ nó lên tiếng.')])

d = clone('c3m03', 'c9m13', 9, map_='coralisles', weather='Storm', playerBase='None', general='hung', enemyDeck=LY_HAN, speaker='sen')
texts(d, ('The Listening Buoys', 'Những chiếc phao nghe'),
      ('Thorne knows what the buoys are for. Hold the lighthouse through the storm while Venn records every word Typhon sends.',
       'Thorne biết những chiếc phao để làm gì. Giữ ngọn hải đăng qua cơn bão trong lúc Venn ghi lại từng chữ Typhon gửi đi.'),
      (('Decoded', 'Giải mã'),
       ('By morning Venn had the submarine\'s call sign, its patrol line and the name of the man giving it orders. She handed the page to Nadia without a word.',
        'Tới sáng, Venn có mật danh của tàu ngầm, tuyến tuần tra của nó và tên người ra lệnh cho nó. Bà đưa trang giấy cho Nadia mà không nói một lời.')),
      [say('sen', 'Start', 'Keep them off the lighthouse. Typhon is talking, and I am listening.', 'Giữ chúng tránh xa ngọn hải đăng. Typhon đang nói, và tôi đang nghe.'),
       say('linh', 'Win', 'The man giving Typhon its orders: Thorne.', 'Người ra lệnh cho Typhon: Thorne.')])

d = clone('c2m01', 'c9m14', 9, map_='lighthousebay', weather='Storm', general='hung', enemyDeck=LY_HAN)
d['waves'].pop('spawns', None)
d['waves']['roster'] = ['main_battle_tank', 'ifv', 'heavy_tank', 'mlrs', 'tank_destroyer']
texts(d, ('Hold the Headland', 'Giữ mũi đất'),
      ('Kessler\'s last ships and Thorne\'s sailors are landing on the Beacon Bay headland to cover Typhon\'s run. Survive their landing for five minutes.',
       'Những con tàu cuối cùng của Kessler và thủy thủ của Thorne đang đổ bộ lên mũi đất Beacon Bay để yểm hộ Typhon. Trụ vững trước cuộc đổ bộ năm phút.'),
      (('Kessler\'s men', 'Người của Kessler'),
       ('The prisoners from the headland still wore Kessler\'s badges under Thorne\'s ribbon. Asked who they served, most of them said "the timetable".',
        'Tù binh trên mũi đất vẫn đeo phù hiệu của Kessler dưới dải băng của Thorne. Hỏi phục vụ ai, phần lớn trả lời "thời gian biểu".')),
      [say('khai', 'Start', 'Five minutes on the headland. Let them come to us.', 'Năm phút trên mũi đất. Để chúng tự tìm tới ta.'),
       say('hung', 'Win', 'Hold them, then. It will not matter much longer.', 'Cứ giữ đi. Chẳng còn quan trọng bao lâu nữa đâu.')])

# ====================================================================== interlude III: Hawk and Raven (the rescue behind the lines)

d = clone('c3s1', 'i3m01', 15, flip=True, weather='Night', playerBase='Anchor', general='quaden', enemyDeck=QUADEN, speaker='reyn')
texts(d, ('Hawk Down', 'Hawk bị bắn rơi'),
      ('Hawk went down behind the lines somewhere on the Frostpeak heights, and his beacon comes and goes. Colonel Reyn\'s column will search the radar hill, the village and the lumber camp, at night, from the enemy\'s side.',
       'Hawk bị bắn rơi sau chiến tuyến, đâu đó trên các điểm cao Frostpeak, và đèn hiệu của anh lúc có lúc không. Đoàn quân của đại tá Reyn sẽ lục soát đồi radar, ngôi làng và trại gỗ, trong đêm, từ phía quân địch.'),
      (('The beacon', 'Đèn hiệu'),
       ('Hawk\'s beacon stopped and started all night: he switched it on only when he heard our engines. Reyn called it the smartest thing a pilot had ever done.',
        'Đèn hiệu của Hawk tắt rồi bật suốt đêm: anh chỉ bật nó khi nghe tiếng động cơ của ta. Reyn gọi đó là điều khôn ngoan nhất một phi công từng làm.')),
      [say('reyn', 'Start', 'Crown\'s column, moving. We bring our pilot home.', 'Đoàn quân của Crown, xuất phát. Ta đưa phi công của mình về nhà.'),
       say('quaden', None, 'Your little Hawk fell well, Colonel. I will finish it myself.', 'Con chim ưng non của ông rơi đẹp lắm, đại tá. Ta sẽ tự tay kết thúc.', at=40),
       say('reyn', 'Win', 'Crash site found. He walked away from it. Follow the tracks.', 'Đã tìm thấy chỗ máy bay rơi. Cậu ấy đã tự đi khỏi đó. Lần theo dấu chân.')])

d = clone('c12m05', 'i3m02', 15, map_='junglepass', weather='Fog', playerBase='None', general='quaden', enemyDeck=QUADEN, speaker='reyn')
boss(d, 'morrigan', fallback='sky_fortress', health=0.5, name='morrigan', fleeAt=0.5)
mark(d, awaits=('boss:morrigan',))
texts(d, ('Morrigan', 'Morrigan'),
      ('Raven is hunting the rescue column himself, in Morrigan: fast, hard to see, and armed for our anti-air. Keep the launchers moving, watch for its strike, and drive it off.',
       'Raven đang tự mình săn đoàn cứu hộ, bằng Morrigan: nhanh, khó thấy, và mang vũ khí nhắm vào phòng không của ta. Cho bệ phóng di chuyển liên tục, để ý đòn tấn công của nó, và đuổi nó đi.'),
      (('A black shape', 'Một bóng đen'),
       ('Morrigan never came close enough to photograph. The only picture the brigade has is a black shape against the canopy, and Hawk says it does not do it justice.',
        'Morrigan chưa bao giờ bay đủ gần để chụp ảnh. Tấm hình duy nhất lữ đoàn có là một bóng đen trên nền tán rừng, và Hawk nói nó chẳng lột tả được gì.')),
      [say('quaden', 'Boss', 'Morrigan, weapons free. Hawk, I know you are listening.', 'Morrigan, tự do khai hỏa. Hawk, ta biết ngươi đang nghe.'),
       say('dieuhau', 'Boss', 'I\'m listening, Raven. Next time I\'ll be flying.', 'Tôi đang nghe đây, Raven. Lần sau tôi sẽ ở trên trời.'),
       say('khai', 'Win', 'It broke off. Keep moving before it comes back.', 'Nó bỏ đi rồi. Đi tiếp trước khi nó quay lại.')])

d = clone('c2m07', 'i3m03', 15, flip=True, map_='junglepass', weather='Night', general='quaden', enemyDeck=QUADEN, speaker='reyn')
texts(d, ('Crown\'s Column', 'Đoàn quân của Crown'),
      ('Hawk has reached a village in Jungle Pass, and Raven\'s ground troops have it ringed. Colonel Reyn\'s heavy column will break the ring. The ring vehicles are marked.',
       'Hawk đã tới được một ngôi làng ở Jungle Pass, và quân mặt đất của Raven vây kín nó. Đoàn thiết giáp hạng nặng của đại tá Reyn sẽ phá vòng vây. Các xe trong vòng vây đã được đánh dấu.'),
      (('Found', 'Tìm thấy'),
       ('Hawk was sitting on the village well with a cup of the headman\'s tea when Reyn\'s first tank came round the corner. "You took your time," he said. Reyn did not smile. Much.',
        'Hawk đang ngồi trên thành giếng làng với chén trà của trưởng làng khi chiếc xe tăng đầu tiên của Reyn rẽ qua góc phố. "Ông tới chậm đấy," anh nói. Reyn không cười. Gần như không.')),
      [say('reyn', 'Start', 'Crown here. Break the ring, and mind the village.', 'Crown đây. Phá vòng vây, và cẩn thận với ngôi làng.'),
       say('dieuhau', 'Win', 'About time, Colonel! I was starting to like the tea.', 'Cũng tới lúc rồi, đại tá! Tôi bắt đầu thích trà ở đây rồi đấy.'),
       say('reyn', 'Win', 'Lieutenant. Get in the tank.', 'Trung úy. Lên xe.')])

d = clone('c2m01', 'i3m04', 15, flip=True, map_='frostpeak', weather='Fog', playerBase='None', general='quaden', enemyDeck=QUADEN, speaker='dieuhau')
d['waves'].pop('spawns', None)
d['waves']['roster'] = list(AIR_WAVES)
texts(d, ('The Long Way Home', 'Đường về nhà'),
      ('The column has Hawk and is running for our lines over the Frostpeak heights, with everything Raven has left on its tail. Survive for five minutes until the pickup.',
       'Đoàn quân đã có Hawk và đang chạy về phòng tuyến của ta qua các điểm cao Frostpeak, với mọi thứ Raven còn lại bám đuôi. Trụ vững năm phút cho tới khi được đón.'),
      (('A debt', 'Món nợ'),
       ('On the flight home Hawk asked the pilot to go past Skyhold, low, so he could see where Raven lived. The pilot said no. Hawk said that next time he would not be asking.',
        'Trên chuyến bay về, Hawk xin phi công bay thấp qua Skyhold để anh nhìn xem Raven ở đâu. Phi công từ chối. Hawk nói lần sau anh sẽ không xin phép nữa.')),
      [say('dieuhau', 'Start', 'Five minutes. Then I\'m back in a cockpit, and he\'s mine.', 'Năm phút. Rồi tôi sẽ trở lại buồng lái, và hắn là của tôi.'),
       say('quaden', 'Win', 'Run home, little Hawk. I will be waiting at Skyhold.', 'Chạy về nhà đi, chim ưng non. Ta sẽ chờ ở Skyhold.')])

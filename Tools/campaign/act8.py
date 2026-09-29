"""Prompt 22, pass 1, Act IV: chapters 10-12, and the order every chapter's main missions are played in (ORDER).
See act5.py for the tools."""

import copy

from campaign_kit import mission, retext, say
from act2 import KESSLER
from act3 import AUREL, QUADEN
from act4 import boss, stage
from act5 import SOURCES, clone, mark, rewrite, stage_says, texts

# ====================================================================== chapter 10: War in the Sky (Raven)

mark(mission('c10m05'), set_piece=True)
rewrite('c10m05', drop=('radio.aurel.c10m05.2',),
        lines=[say('quaden', 'Boss', 'Look at it, Colonel. That is the future. It is not yours.', 'Nhìn nó đi, đại tá. Đó là tương lai. Không phải của ông.'),
               say('sen', 'Win', 'That was a test flight. Of something much bigger.', 'Đó chỉ là một chuyến bay thử. Cho một thứ lớn hơn nhiều.')])
rewrite('c10m10', lines=[say('dieuhau', 'Win', 'That one was for you, old friend.', 'Phát đó là cho cậu, bạn cũ.')])
rewrite('c10s2', keep=False, name=('Argus', 'Argus'),
        brief=('Argus, Raven\'s armoured recon airship, is spotting for Hegemon\'s guns over the Frostpeak heights. Nadia wants the three posts it watches checked, and the airship down if it comes close.',
               'Argus, khí cầu trinh sát bọc giáp của Raven, đang chỉ điểm cho pháo Hegemon trên các điểm cao Frostpeak. Nadia muốn kiểm tra ba điểm nó đang theo dõi, và bắn hạ khí cầu nếu nó tới gần.'),
        fragment=(('Spotter', 'Kẻ chỉ điểm'),
                  ('With Argus gone, the enemy guns round Skyhold fired by the map for a week. The map was old.',
                   'Mất Argus, pháo địch quanh Skyhold phải bắn theo bản đồ suốt một tuần. Tấm bản đồ ấy đã cũ.')),
        lines=[say('linh', 'Start', 'Three posts under Argus. Look, and shoot it if it comes low.', 'Ba điểm dưới tầm mắt Argus. Nhìn thôi, và bắn nó nếu nó hạ thấp.'),
               say('dieuhau', 'Boss', 'Argus, Raven\'s recon airship. It is spotting for his guns.', 'Argus, khí cầu trinh sát của Raven. Nó đang chỉ điểm cho pháo của hắn.')])

d = clone('c11m06', 'c10m11', 10, weather='Clear', playerBase='None', general='quaden', enemyDeck=QUADEN, speaker='okoye')
texts(d, ('Vault\'s Airstrip', 'Sân bay dã chiến của Vault'),
      ('Captain Okoye has a forward airstrip for the air campaign, a stretch of road on the Frostpeak heights, and a hundred transport flights to land on it. Hold it while they come in.',
       'Đại úy Okoye có một sân bay dã chiến cho chiến dịch trên không, một đoạn đường trên các điểm cao Frostpeak, và một trăm chuyến bay vận tải cần hạ cánh ở đó. Giữ nó trong lúc chúng hạ cánh.'),
      (('Stock', 'Hàng dự trữ'),
       ('Okoye stocked the airstrip for a campaign twice as long as the one we fought. When it ended she had enough fuel left over to light Veyra for a winter.',
        'Okoye tích trữ cho sân bay đủ dùng một chiến dịch dài gấp đôi trận ta đã đánh. Khi mọi chuyện kết thúc, cô còn thừa đủ nhiên liệu để thắp sáng Veyra cả một mùa đông.')),
      [say('okoye', 'Start', 'Every flight that lands is a week of war we can afford. Hold the strip.', 'Mỗi chuyến bay hạ cánh là thêm một tuần chiến tranh ta gánh nổi. Giữ đường băng.'),
       say('okoye', 'Win', 'Hundredth flight down. The reserve is full, and the reserve\'s reserve.', 'Chuyến thứ một trăm đã hạ cánh. Dự trữ đã đầy, cả dự trữ của dự trữ.')])

# c10m12: the duel over Skyhold. Prompt 22 E.3 gives Morrigan a mode of its own for it (the player flies only aircraft)
# and F.1 fixes Hawk as its commander; both come later, the mission awaits them.
d = clone('c10m05', 'c10m12', 10, flip=True, playerBase='None', general='quaden', enemyDeck=QUADEN, speaker='dieuhau', commander='dieuhau')
boss(d, 'morrigan', fallback='sky_fortress', health=0.6, name='morrigan')
mark(d, set_piece=True, awaits=('boss:morrigan', 'mode:air_duel'))
texts(d, ('Hawk and Raven', 'Hawk và Raven'),
      ('Raven has sent word through the Skyhold tower: him and Hawk, over the runway, at noon. Hawk has already said yes. Keep the rest of Raven\'s wing off him and bring Morrigan down.',
       'Raven gửi lời qua tháp điều khiển Skyhold: hắn và Hawk, trên đường băng, giữa trưa. Hawk đã nhận lời. Giữ phần còn lại của phi đội Raven tránh xa anh và hạ Morrigan.'),
      (('Noon', 'Giữa trưa'),
       ('The duel lasted six minutes. Morrigan broke off trailing smoke, and Hawk flew home in a jet with forty holes in it. He asked for it to be repaired, not replaced.',
        'Trận tay đôi kéo dài sáu phút. Morrigan bỏ chạy, kéo theo một vệt khói, và Hawk bay về trên chiếc phản lực thủng bốn mươi lỗ. Anh xin sửa nó, chứ không thay chiếc mới.')),
      [say('quaden', 'Start', 'Noon, little Hawk. Just you and me.', 'Giữa trưa, chim ưng non. Chỉ ngươi và ta.'),
       say('dieuhau', None, 'This one is for my wingman, Raven.', 'Trận này là cho đồng đội của tôi, Raven.', at=6),
       say('dieuhau', 'Win', 'He ran! Raven ran!', 'Hắn chạy rồi! Raven chạy rồi!'),
       say('khai', 'Win', 'Good flying, Lieutenant. Finish it at Skyhold.', 'Bay giỏi lắm, trung úy. Kết thúc nó ở Skyhold.')])

d = clone('c3m01', 'c10m13', 10, flip=True, weather='Clear', playerBase='None', general='quaden', enemyDeck=QUADEN)
texts(d, ('The Passes at Dawn', 'Các con đèo lúc bình minh'),
      ('Spectre hunts the passes at night. By day we can take them: the signal post, the frozen lake and the sawmill, from the north side, before Raven\'s wing is up.',
       'Spectre săn trên các con đèo trong đêm. Ban ngày thì ta chiếm được chúng: trạm tín hiệu, hồ băng và xưởng cưa, từ phía bắc, trước khi phi đội của Raven cất cánh.'),
      (('First light', 'Tia sáng đầu tiên'),
       ('The brigade took the last outpost as the sun came over the pass, and Spectre\'s contrail turned for home above it.',
        'Lữ đoàn chiếm tiền đồn cuối cùng đúng lúc mặt trời nhô qua đèo, và vệt khói của Spectre quay đầu về căn cứ ngay phía trên.')),
      [say('khai', 'Start', 'Dawn. The gunship is going home. We go up the pass.', 'Bình minh. Pháo hạm bay đang về căn cứ. Ta tiến lên đèo.'),
       say('dieuhau', 'Win', 'The passes are ours. Spectre will have to come to us tonight.', 'Các con đèo là của ta. Đêm nay Spectre sẽ phải tự tìm tới ta.')])

d = clone('c7m01', 'c10m14', 10, flip=True, map_='skyhold', weather='Overcast', playerBase='Anchor', general='quaden', enemyDeck=QUADEN, speaker='linh')
texts(d, ('The Refuelling Hour', 'Giờ tiếp nhiên liệu'),
      ('Nadia has Raven\'s schedule: for one hour every afternoon his wing is on the ground refuelling. In that hour, take both aprons and the runway from the far side.',
       'Nadia có lịch trình của Raven: mỗi chiều có một giờ phi đội của hắn nằm dưới đất tiếp nhiên liệu. Trong giờ đó, chiếm cả hai sân đỗ và đường băng từ phía bên kia.'),
      (('Schedule', 'Lịch trình'),
       ('Raven changed his schedule the next day. It cost him a day of flying to do it.',
        'Hôm sau Raven đổi lịch trình. Việc đó làm hắn mất một ngày bay.')),
      [say('linh', 'Start', 'One hour, Colonel. His wing is on the ground until four.', 'Một giờ thôi, đại tá. Phi đội của hắn nằm dưới đất tới bốn giờ.'),
       say('quaden', 'Win', 'A cheap trick, Colonel. I will remember it.', 'Một mánh rẻ tiền, đại tá. Ta sẽ nhớ.')])

# ====================================================================== chapter 11: Skygate (Aurel on the radio; Orlov's last battle)

mark(mission('c11m05'), set_piece=True)
rewrite('c11m01', lines=[say('aurel', None, 'Director Aurel. For the record: our first satellite reached orbit this morning.',
                             'Giám đốc Aurel. Xin thông báo: vệ tinh đầu tiên của chúng tôi đã lên quỹ đạo sáng nay.', at=10)])
retext('mission.c11m05.brief', 'Orlov is waiting at the Skygate Array\'s railhead in the Rust Yard with Gungnir, the biggest gun he ever had. This is his last battle. Silence the gun.',
       'Orlov đang chờ ở đầu mối đường sắt của Skygate Array trong Rust Yard cùng Gungnir, khẩu pháo lớn nhất ông ta từng có. Đây là trận cuối của ông ta. Bắt khẩu pháo câm họng.')
rewrite('c11m10', lines=[say('khai', 'Win', 'The Skygate is down. Next stop, Helion.', 'Skygate đã sụp. Điểm dừng tiếp theo: Helion.')])
mission('c11s1')['towerGear'] = 'Legendary'  # chapter 12's side mission paid the campaign's legendary tower piece

d = clone('c11s2', 'c11m11', 11, general='aurel', enemyDeck=AUREL, speaker='mai')
texts(d, ('The Engineers\' Convoy', 'Đoàn xe công binh'),
      ('Mara\'s engineers need to reach the wreck of the Skygate\'s western pad before Aurel\'s men clear it. Take them through the Rust Yard in the fog.',
       'Công binh của Mara cần tới xác bệ phóng phía tây của Skygate trước khi người của Aurel dọn sạch. Đưa họ qua Rust Yard trong sương.'),
      (('Salvage', 'Thu hồi'),
       ('From the wreck Mara took one thing: a guidance computer. "For later," she said. It was the first part of a surprise.',
        'Từ đống đổ nát Mara lấy đúng một thứ: một máy tính dẫn đường. "Để dành," cô nói. Đó là phần đầu tiên của một bất ngờ.')),
      [say('mai', 'Start', 'Get my engineers there in one piece. I need what is in that wreck.', 'Đưa công binh của tôi tới nơi nguyên vẹn. Tôi cần thứ nằm trong đống đổ nát đó.'),
       say('mai', 'Win', 'Got it. A guidance computer, nearly intact. Don\'t ask what for.', 'Có rồi. Một máy tính dẫn đường, gần như nguyên vẹn. Đừng hỏi để làm gì.')])

# ====================================================================== chapter 12: Helion (Aurel, Varga, Kessler)

# The reversed Salt Flats round the launch complex (C.4): the Locust's road and the reactor fuel's.
d = mission('c12m05')
d['map'] = 'saltflat'
retext('mission.c12m05.brief', 'Aurel took Venn\'s drone programme when she left, and kept building. A Locust carrier covers the Salt Flats road to Helion. Bring it down.',
       'Aurel chiếm lấy chương trình drone của Venn khi bà bỏ đi, và vẫn đóng tiếp. Một tàu Locust đang che chắn con đường qua Salt Flats tới Helion. Bắn hạ nó.')
d = mission('c12m07')
d.update(map='saltflat', weather='Night')
retext('mission.c12m07.brief', 'Icarus\'s reactor fuel is crossing the Salt Flats at night in three guarded trucks. Nadia has marked them. Stop every one.',
       'Nhiên liệu lò phản ứng của Icarus đang băng qua Salt Flats trong đêm trên ba xe tải có hộ tống. Nadia đã đánh dấu chúng. Chặn từng chiếc một.')

# c12m02: Kessler's last stand is at sea (his Scylla, C.4), in Beacon Bay north of Helion; he bargains to the last.
d = mission('c12m02')
d['map'] = 'lighthousebay'
d['boss'] = copy.deepcopy(mission('c4m06')['boss'])
d['boss'].update(fallbackHealth=0.6)
d['enemyDeck'] = KESSLER
mark(d, set_piece=True)
rewrite('c12m02', keep=False, name=('Kessler\'s Last Ship', 'Con tàu cuối cùng của Kessler'),
        brief=('Kessler has gathered his last ships in Beacon Bay, north of Helion, to cover the launch from the sea, with Scylla at their head. Level his shore HQ and sink the destroyer.',
               'Kessler gom những con tàu cuối cùng về Beacon Bay, phía bắc Helion, để yểm hộ cuộc phóng từ biển, với Scylla dẫn đầu. San phẳng sở chỉ huy trên bờ của ông ta và đánh chìm tàu khu trục.'),
        fragment=(('The ledger', 'Sổ cái'),
                  ('Kessler was taken off Scylla\'s deck with his ledger under his arm. The last page balanced.',
                   'Kessler bị bắt trên boong Scylla với cuốn sổ cái kẹp dưới nách. Trang cuối cùng vẫn cân.')),
        lines=[say('kessler', 'Start', 'Colonel, let us be sensible. Every ship I have left, for safe passage.', 'Đại tá, ta hãy thực tế. Mọi con tàu ta còn lại, đổi lấy một lối thoát an toàn.'),
               say('khai', None, 'No sale, Admiral.', 'Không mua, đô đốc.', at=6),
               say('kessler', 'Boss', 'Name your price, then. Everyone has one.', 'Vậy ra giá đi. Ai cũng có giá cả.'),
               say('kessler', 'Win', 'Then record the time, Colonel. The ledger is closed.', 'Vậy thì ghi lại giờ giấc, đại tá. Sổ cái đã khép.')])

# c12m10: Varga falls like a soldier; Mara's Behemoth fights beside the brigade (prompt 22 E.4: P22-content builds the unit, the
# stage awaits it); Aurel launches, a tungsten rod falls from orbit, Icarus falls after it, and Aurel fights on in the wreck.
d = mission('c12m10')
mark(d, awaits=('ally:mara_behemoth',))
stage_says(d, 'command', 'mai', 's4b', 'Matilda is in the fight, Colonel. Behemoth against Behemoth.', 'Matilda đã vào trận, đại tá. Behemoth đấu Behemoth.', replace=False)
stage_says(d, 'command', 'varga', 's4e', 'Well fought, Colonel. Look after my machines.', 'Đánh hay lắm, đại tá. Hãy chăm sóc những cỗ máy của tôi.', at='end', replace=False)
stage_says(d, 'bug', 'linh', 's6b', 'Impact warning! A tungsten rod, falling from orbit. Scatter!', 'Cảnh báo va chạm! Một thanh vonfram đang rơi từ quỹ đạo. Tản ra!', replace=False)
rewrite('c12m10', lines=[say('aurel', 'Win', 'They still don\'t understand.', 'Họ vẫn chưa hiểu.')])

# ====================================================================== the order of play

# Each chapter's main missions in the order they are played (its side missions follow). A mission not listed is an error.
ORDER = {
    1: ['c1m01', 'c1m02', 'c1m03', 'c1m04', 'c1m05', 'c1m06', 'c1m08', 'c1m09', 'c1m10'],
    2: ['c2m01', 'c2m02', 'c2m03', 'c2m04', 'c2m05', 'c2m06', 'c2m07', 'c2m08', 'c2m09', 'c2m10', 'c2m11'],
    3: ['c3m01', 'c3m02', 'c3m11', 'c3m03', 'c3m04', 'c3m05', 'c3m06', 'c3m12', 'c3m07', 'c3m08', 'c3m09', 'c3m10'],
    13: ['i1m01', 'i1m02', 'i1m03', 'i1m04'],
    4: ['c4m01', 'c4m02', 'c4m03', 'c4m04', 'c4m05', 'c4m12', 'c4m07', 'c4m16', 'c4m08', 'c4m13', 'c4m09', 'c4m10', 'c4m14', 'c4m06', 'c4m15', 'c4m11'],
    5: ['c5m01', 'c5m02', 'c5m03', 'c5m04', 'c5m08', 'c5m12', 'c5m05', 'c5m06', 'c5m11', 'c5m07', 'c5m13', 'c5m09', 'c5m10'],
    6: ['c6m01', 'c6m13', 'c6m02', 'c6m16', 'c6m11', 'c6m03', 'c6m05', 'c6m12', 'c6m08', 'c6m07', 'c6m04', 'c6m06', 'c6m09', 'c6m15', 'c6m14', 'c6m10'],
    14: ['i2m01', 'i2m02', 'i2m03', 'i2m04'],
    7: ['c7m01', 'c7m03', 'c7m16', 'c7m04', 'c7m05', 'c7m07', 'c7m12', 'c7m15', 'c7m13', 'c7m14', 'c7m02', 'c7m17', 'c7m06', 'c7m11', 'c7m09', 'c7m18',
        'c7m08', 'c7m10'],
    8: ['c8m01', 'c8m02', 'c8m03', 'c8m11', 'c8m04', 'c8m05', 'c8m06', 'c8m12', 'c8m07', 'c8m08', 'c8m09', 'c8m10'],
    9: ['c9m01', 'c9m02', 'c9m03', 'c9m04', 'c9m05', 'c9m11', 'c9m06', 'c9m12', 'c9m13', 'c9m07', 'c9m08', 'c9m14', 'c9m09', 'c9m10'],
    15: ['i3m01', 'i3m02', 'i3m03', 'i3m04'],
    10: ['c10m01', 'c10m02', 'c10m11', 'c10m03', 'c10m04', 'c10m05', 'c10m06', 'c10m13', 'c10m08', 'c10m14', 'c10m07', 'c10m12', 'c10m09', 'c10m10'],
    11: ['c11m01', 'c11m02', 'c11m03', 'c11m04', 'c11m05', 'c11m06', 'c11m07', 'c11m11', 'c11m08', 'c11m09', 'c11m10'],
    12: ['c12m01', 'c12m05', 'c12m03', 'c12m02', 'c12m04', 'c12m07', 'c12m06', 'c12m08', 'c12m09', 'c12m10'],
}

import campaign_kit as _kit  # noqa: E402
_listed = [mid for ids in ORDER.values() for mid in ids]
_main = [m['id'] for m in _kit.MISSIONS if not m.get('side')]
if sorted(_listed) != sorted(_main) or len(set(_listed)) != len(_listed):
    raise SystemExit(f'act8.ORDER: missing {sorted(set(_main) - set(_listed))}, unknown {sorted(set(_listed) - set(_main))}')
for _c, _ids in ORDER.items():
    for _mid in _ids:
        if mission(_mid)['chapter'] != _c:
            raise SystemExit(f'act8.ORDER: {_mid} is not in chapter {_c}')

# ====================================================================== prompt 22 A: the last words that named the old story

retext('bossfile.daedalus', 'The ship that brings Aurel\'s troops down from orbit, pod by pod, onto the Skygate Array.',
       'Con tàu đưa quân của Aurel từ quỹ đạo xuống Skygate Array, từng khoang một.')
retext('mission.c11m01.brief', 'Aurel\'s Skygate Array is fed by the rail yard. Take its crossings at night, from the far side.',
       'Skygate Array của Aurel được tiếp tế qua bãi ray. Chiếm các ngả giao cắt trong đêm, từ phía bên kia.')
retext('mission.c11m10.name', 'The Skygate Array', 'Skygate Array')
retext('mission.c1m03.fragment', 'The farmers of Greenvale kept planting for two years under Hegemon. When our tanks came up the road, an old man offered Colonel Kade a bag of rice and asked if we were staying.',
       'Nông dân Greenvale vẫn cày cấy suốt hai năm dưới thời Hegemon. Khi xe tăng ta lên đường làng, một cụ già đưa đại tá Kade một bao gạo và hỏi quân mình có ở lại không.')
retext('mission.c1m08.fragment', 'Before Hegemon came, Ashfield made bricks. The fortress on the hill was a brickworks; Hegemon kept the kilns and put guns in them.',
       'Trước khi Hegemon tới, Ashfield làm gạch. Pháo đài trên đồi vốn là lò gạch; Hegemon giữ lại các lò nung rồi đặt pháo vào trong đó.')
retext('mission.c3m08.fragment', "The convoy's doctor had worked for Hegemon's medical corps until the occupation. Nobody asked her why she changed sides. She did not wait to be asked.",
       'Bác sĩ trong đoàn xe từng làm cho quân y Hegemon cho tới ngày chiếm đóng. Không ai hỏi vì sao cô đổi phe. Cô cũng chẳng đợi ai hỏi.')
retext('mission.c6m10.fragment', 'General Thorne\'s first words on arrival, broadcast to his whole army: "My army has saved the dam." Colonel Kade\'s staff heard it too. Nobody said anything.',
       'Câu đầu tiên của tướng Thorne khi tới nơi, phát cho toàn quân của ông: "Quân của tôi đã cứu con đập." Ban tham mưu của đại tá Kade cũng nghe thấy. Không ai nói gì.')
retext('mission.c7m09.fragment', 'The station\'s last broadcast was cut off mid-sentence: "Stability will always—" Nadia has the tape. She plays it when anyone needs cheering up.',
       'Buổi phát sóng cuối cùng của đài bị cắt ngang giữa câu: "Sự ổn định sẽ mãi mãi—" Nadia giữ cuộn băng. Cô bật nó mỗi khi có ai cần vui lên.')

# Prompt 22 C.7: a radio line fits in one or two lines on a phone (100 characters at most).
retext('radio.sen.c12m10.s6', 'That is 01, complete. It climbs past most of your reach. Do not let it level out.',
       'Đó là chiếc 01, hoàn chỉnh. Nó sẽ vượt tầm với của phần lớn các anh. Đừng để nó bay ổn định.')
retext('radio.linh.c11m05.1', 'Gungnir is on the east rails. Where the ground cracks red, a shell lands three seconds later.',
       'Gungnir nằm trên đường ray phía đông. Chỗ nào mặt đất nứt đỏ, ba giây sau đạn rơi xuống đó.')
# The old chapter and act names, as the words of a mission.
retext('mission.c12m10.name', 'Icarus Falls', 'Icarus rơi')
retext('mission.c2m01.fragment.title', 'Crude', 'Dầu thô')

# ====================================================================== prompt 22 D (pass 2): where its choices will be made
# The mission after which each choice of D.5 comes (the flag it sets is the choice's id); the chapter-end comics (D.8) hang
# off each chapter's "comic" key in campaign.json. Nothing reads them yet.
mission('c4m14')['storyChoice'] = 'c4.pursuit'   # chase Kessler out to sea at once, or stay and save the civilian ships
mission('c8m09')['storyChoice'] = 'c8.miners'    # free the miners Thorne holds (help in chapter 9), or strike at Kronos (more coins)
mission('c11m09')['storyChoice'] = 'c11.radar'   # the Skygate radars first (less enemy sight in chapter 12), or straight to Helion

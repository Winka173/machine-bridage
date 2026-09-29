"""Prompt 22, pass 1: the campaign in chapters of 9 to 18 missions and three interludes (B), and the story's
beats (C). This file holds the tools the four prompt 22 files share and Act I: chapters 1-3 and
interlude I (Blueprints). act6.py is Act II, act7.py Act III, act8.py Act IV and the order of play.

How a new mission is made (prompt 4's map reuse): a mission already written on the same battlefield (or
one whose goal names only the map's points, on another) is copied with its set-up changed: the side it
is played from, the weather, the player's base, the play area. Every two missions on one map still
differ in at least two of those and the goal; no two in a row are the same (build_campaign.check).

Ids: a chapter's new missions go on from its last id (c4m12...), and act8.ORDER says where each is
played; an interlude's are i1m01-i3m04, chapter 13-15. A mission that moved takes its stars along
(story.MOVES22). Words: every text here is new or marked fresh, in both languages.
"""

import copy

import campaign_kit as kit
from campaign_kit import T, add_mission, mission, retext, say, scripted
from act1 import ORLOV, VARGA, VARGA_EARLY
from act4 import PACE, pace, boss, stage

# Prompt 21 localised by hand, in CampaignText.cs, the words prompt 20 marked fresh (act4.py): they keep those words now.
# Only what story.py and these files write again is fresh.
for _key in set(kit.FRESH) - getattr(kit, 'STORY_FRESH', set()):
    kit.FRESH.discard(_key)

# ====================================================================== the ground

# The standard frame on the battlefields the campaign did not use yet, and on the two P22-content builds (part E;
# its maps are in the same frame as every map, so a mission that names only points works there; DECISIONS 22A).
kit.POINTS.update({
    'saltflat': {'west': (-56.0, 88.0), 'town': (0, 0), 'east': (56.0, -88.0)},
    'borderbridge': {'west': (-60.0, 84.0), 'town': (0, 0), 'east': (60.0, -84.0)},
    'swamp': {'west': (-62.0, 86.0), 'town': (0, 0), 'east': (62.0, -86.0)},
    'coralisles': {'west': (-62.0, 86.0), 'town': (0, 0), 'east': (62.0, -86.0)},
    'lighthousebay': {'west': (-73.54, 73.54), 'town': (-14.14, 14.14), 'east': (26.87, -26.87)},
    'foundry': {'west': (-60.0, 84.0), 'town': (0, 0), 'east': (60.0, -84.0)},
    'veyra_old_quarter': {'west': (-60.0, 84.0), 'town': (0, 0), 'east': (60.0, -84.0)},
})
kit.WEATHER.update({
    'saltflat': {'Clear', 'Sandstorm', 'Night'},
    'borderbridge': {'Clear', 'Overcast', 'Rain', 'Fog', 'Storm', 'Night'},
    'swamp': {'Fog', 'Rain', 'Overcast', 'Storm', 'Clear', 'Night'},
    'coralisles': {'Clear', 'Storm', 'Overcast', 'Night'},
    # The two new maps (part E): an old factory's halls and yards, and the capital's old streets (like the capital).
    'foundry': {'Clear', 'Overcast', 'Rain', 'Fog', 'Night'},
    'veyra_old_quarter': {'Night', 'Clear', 'Rain', 'Overcast', 'Fog', 'Storm'},
})

# The pace of the chapters act4.py had none for (their neighbours' numbers), and of the interludes (the chapter before).
PACE.update({
    2: dict(enemyCp=10, enemyIncome=0.8, playerCp=26, playerIncome=1.45, playerCap=36),
    5: dict(enemyCp=13, enemyIncome=0.9, playerCp=28, playerIncome=1.5, playerCap=38),
    7: dict(enemyCp=14, enemyIncome=0.9, playerCp=30, playerIncome=1.55, playerCap=40),
    10: dict(enemyCp=15, enemyIncome=0.95, playerCp=32, playerIncome=1.6, playerCap=42),
    12: dict(enemyCp=17, enemyIncome=1.0, playerCp=32, playerIncome=1.7, playerCap=44),
    13: dict(enemyCp=12, enemyIncome=0.85, playerCp=26, playerIncome=1.45, playerCap=36),
    14: dict(enemyCp=13, enemyIncome=0.9, playerCp=30, playerIncome=1.55, playerCap=40),
    15: dict(enemyCp=15, enemyIncome=0.95, playerCp=30, playerIncome=1.6, playerCap=40),
})

# ====================================================================== the tools

DROP = ('radio', 'tips', 'legacy', 'unlocks', 'hqLevel', 'rarePrints', 'towerGear', 'replay', 'epilogue', 'side', 'after',
        'challenge', 'speaker', 'setPiece', 'awaits')

# The missions that leave their chapter (they come back under a new id, story.MOVES22) or the campaign.
RETIRED = {'c1m07', 'c1s2', 'c7s2', 'c11s2', 'c12s1', 'c12s2'}
SOURCES = {mid: copy.deepcopy(mission(mid)) for mid in RETIRED}
kit.MISSIONS[:] = [m for m in kit.MISSIONS if m['id'] not in RETIRED]
for _key in list(kit.TEXTS):
    if any(f'.{mid}.' in _key + '.' for mid in RETIRED):
        del kit.TEXTS[_key]
        kit.FRESH.discard(_key)


def source(mid):
    return SOURCES[mid] if mid in SOURCES else mission(mid)


def clone(src, new, chapter, flip=False, map_=None, **over):
    """A copy of mission <src> as <new> in <chapter>: its battlefield and set-up, none of its rewards or words.
    <flip> plays it from the other side; <map_> moves it to another battlefield (its goal must name only points)."""
    d = copy.deepcopy(source(src))
    for k in DROP:
        d.pop(k, None)
    if flip:
        d['reversed'] = not d.get('reversed', False)
    d['id'] = new
    d['chapter'] = chapter
    if map_:
        d['map'] = map_
    for s in d.get('stages', []):
        s['events'] = [e for e in s.get('events', []) if not (e['kind'] == 'Radio' and f'.{src}.' in e['key'])]
    d.update(over)
    if not d.get('reversed'):
        d.pop('reversed', None)
    if chapter in PACE:
        pace(d, chapter)
    return d


def mark(d, set_piece=False, awaits=None):
    if set_piece:
        d['setPiece'] = True
    if awaits:
        d['awaits'] = list(awaits)
    return d


def rewrite(mid, name=None, brief=None, fragment=None, lines=None, drop=(), keep=True):
    """Prompt 22's words for a mission already written: <lines> are added (keep) or replace the mission's own."""
    d = mission(mid)
    if name:
        retext(f'mission.{mid}.name', *name)
    if brief:
        retext(f'mission.{mid}.brief', *brief)
    if fragment:
        retext(f'mission.{mid}.fragment.title', *fragment[0])
        retext(f'mission.{mid}.fragment', *fragment[1])
    rad = d.get('radio', [])
    if not keep:
        rad = [r for r in rad if f'.{mid}.' not in r['key']]
    rad = [r for r in rad if r['key'] not in drop]
    for i, line in enumerate(lines or []):
        key = retext(f'radio.{line.speaker}.{mid}.q{i + 1}', line.en, line.vi)
        rad.append(kit.radio(line.on, key, line.arg, line.at))
    if rad:
        d['radio'] = rad
    return d


def stage_says(d, stage_key, speaker, key, en, vi, at='start', replace=True):
    """A stage's own line (the one it had at that moment goes when <replace>)."""
    s = stage(d, stage_key)
    if replace:
        s['events'] = [e for e in s.get('events', []) if not (e['kind'] == 'Radio' and e.get('at') == at and f".{d['id']}." in e['key'])]
    s['events'].append({'at': at, 'kind': 'Radio', 'key': retext(f"radio.{speaker}.{d['id']}.{key}", en, vi)})


def texts(d, name, brief, fragment, lines, stages_text=None, choices_text=None):
    # Fresh: these words are the sources', build after build (CampaignText.cs keeps a key's words otherwise).
    return add_mission(d, name, brief, fragment, lines, stages_text=stages_text, choices_text=choices_text, fresh=True)


def ally(site, defs, heading=45, later=None):
    """An allied column (prompt 5's ally, no base of its own): units round <site> (the player's frame), more flown in later."""
    a = {'x': site[0], 'z': site[1], 'heading': heading, 'units': kit.units(0, defs, site, radius=7.0, heading=heading)}
    if later:
        a['reinforcements'] = [{'at': at, 'units': list(units)} for at, units in later]
    return a


WEAKEN = [{'at': 'end', 'kind': 'Income', 'team': 1, 'amount': 0.7}, {'at': 'end', 'kind': 'Radio', 'key': 'radio.enemyWeakened'}]

# ====================================================================== chapter 1: Coast of Fire (Brandt)

mark(mission('c1m01'), set_piece=True)
rewrite('c1m03', name=('The Fishing Village', 'Làng chài'),
        brief=('The fishing village at the river mouth, the crossroads above it and the farm beyond command every road inland. '
               'A handful of Brandt\'s scouts hold them. Take all three and the brigade has room to breathe.',
               'Làng chài ở cửa sông, ngã tư phía trên và trang trại phía xa khống chế mọi con đường vào đất liền. '
               'Chỉ một nhúm lính trinh sát của Brandt giữ chúng. Chiếm cả ba là lữ đoàn có chỗ thở.'),
        lines=[say('khai', 'Win', 'The village is ours. The boats can go back out.', 'Làng chài là của ta. Thuyền lại ra khơi được rồi.')])

d = rewrite('c1m10', fragment=(('Brandt\'s terms', 'Điều kiện của Brandt'),
                               ('Brandt surrendered in full uniform and asked for one thing: that his men be counted, not shot. Nadia counted his files instead. '
                                'One name was on nearly every page: General Viktor Varga.',
                                'Brandt đầu hàng trong quân phục chỉnh tề và chỉ xin một điều: người của ông ta được điểm danh, không bị bắn. Nadia thì điểm danh hồ sơ của ông ta. '
                                'Một cái tên có mặt gần như trên mọi trang: tướng Viktor Varga.')),
            lines=[say('brandt', 'Win', 'Enough. The walls are yours, Colonel. My men walk out alive.', 'Đủ rồi. Tường thành là của ông, đại tá. Người của tôi được đi ra an toàn.'),
                   say('linh', 'Win', 'His files say Varga, Varga, Varga. Every order comes from him.', 'Hồ sơ của ông ta toàn Varga, Varga, Varga. Mọi mệnh lệnh đều từ ông ta.')])

# ====================================================================== chapter 2: Black Gold (Varga; Thorne's first battle with us)

rewrite('c2m01', drop=('radio.varga.c2m01.2',),
        lines=[say('varga', None, 'General Varga, to the brigade. Welcome to my desert. Let us fight like soldiers.',
                   'Tướng Varga gửi lữ đoàn. Chào mừng tới sa mạc của tôi. Ta hãy đánh nhau như những người lính.', at=15)])

# Inferno guards the refinery road and falls back into the refinery hurt (the raid finishes it); Mara knows its design.
d = mission('c2m05')
d['boss']['fleeAt'] = 0.5
rewrite('c2m05', keep=False,
        brief=('Varga has sent Inferno out into the sandstorm to guard the refinery road: a Behemoth rebuilt round flame projectors. '
               'Keep out of its reach and drive it back.',
               'Varga tung Inferno ra giữa bão cát để canh con đường tới nhà máy lọc dầu: một chiếc Behemoth dựng lại quanh các súng phun lửa. '
               'Tránh xa tầm với của nó và đẩy nó lùi lại.'),
        lines=[say('varga', 'Start', 'You want fire, Colonel? Here is fire.', 'Muốn lửa hả, đại tá? Lửa đây.'),
               say('mai', 'Boss', 'That cooling line on its back. I drew that.', 'Đường ống làm mát trên lưng nó. Tôi đã vẽ nó.'),
               say('khai', 'Win', 'It ran for the refinery. We will find it there.', 'Nó chạy về nhà máy lọc dầu. Ta sẽ tìm nó ở đó.')])

# The refinery raid: a set piece of stages now, not the operation; Inferno burns inside the refinery.
d = mission('c2m10')
d.pop('operation', None)
d['replay'] = True
mark(d, set_piece=True)
boss(stage(d, 'inferno'), 'behemoth_inferno', health=1.2)
stage(d, 'inferno')['boss']['name'] = 'behemoth_inferno'
retext('stage.c2m10.inferno', 'Inferno', 'Inferno')
stage_says(d, 'inferno', 'varga', 's5', 'Inferno, burn it all. The refinery too.', 'Inferno, đốt hết đi. Cả nhà máy nữa.')
retext('mission.c2m10.name', 'Refinery Raid', 'Đột kích nhà máy lọc dầu')
retext('mission.c2m10.brief', 'The raid Varga fears: take the oil field and the oasis, choose what to hit next, then blow the refinery\'s towers and tanks, with Inferno inside them.',
       'Trận đột kích mà Varga sợ nhất: chiếm mỏ dầu và ốc đảo, chọn mục tiêu kế tiếp, rồi cho nổ tháp và bồn chứa của nhà máy, cùng Inferno bên trong.')
retext('mission.c2m10.fragment.title', 'The refinery', 'Nhà máy lọc dầu')
retext('mission.c2m10.fragment', 'The refinery burned for four days, and Inferno with it. When the fire died down Mara went in alone and came out with a cooling pipe she had drawn years before.',
       'Nhà máy lọc dầu cháy suốt bốn ngày, cùng Inferno bên trong. Khi lửa tàn, Mara một mình đi vào và mang ra một đoạn ống làm mát cô từng vẽ nhiều năm trước.')
retext('radio.khai.c2m10.2', 'The refinery is gone. Varga\'s big one has pulled back into Red Rock.', 'Nhà máy lọc dầu mất rồi. Con quái vật lớn của Varga đã rút vào Red Rock.')

# c2m11: the operation for Red Rock, the Behemoth at the end of it, General Thorne's army on our flank for the first time.
d = clone('c2m10', 'c2m11', 2, map_='redrock', weather='Sandstorm', operation=True, replay=True, general='varga', enemyDeck=VARGA)
d['playArea'] = {'minX': -146, 'minZ': -146, 'maxX': 146, 'maxZ': 146}
d['ally'] = ally((-96, -80), ['main_battle_tank', 'main_battle_tank', 'ifv', 'aa_vehicle', 'mlrs'], later=[(240, ['heavy_tank', 'ifv', 'tank_destroyer'])])
d['stages'] = [
    {'stage': 'wells', 'goal': 'Capture', 'points': ['west'], 'enemyOwns': ['west', 'town', 'east'], 'cp': 8,
     'choices': [{'key': 'pumps', 'next': 'pumps'}, {'key': 'guns', 'next': 'guns'}]},
    {'stage': 'pumps', 'goal': 'Destroy', 'targets': ['oil_pump'], 'targetX': -56, 'targetZ': 92, 'targetRadius': 30, 'targetHealth': 2, 'cp': 6,
     'next': 'oasis', 'events': copy.deepcopy(WEAKEN)},
    {'stage': 'guns', 'goal': 'Survive', 'points': ['west'], 'surviveSeconds': 150, 'cp': 6, 'next': 'oasis',
     'events': [{'at': 'end', 'kind': 'Strike', 'team': 0, 'support': 'artillery_barrage', 'every': 55}]},
    {'stage': 'oasis', 'goal': 'Capture', 'points': ['town'], 'enemyOwns': ['town'], 'cp': 8,
     'events': [{'at': 'start', 'kind': 'Reinforce', 'team': 1, 'units': ['heavy_tank', 'tank_destroyer', 'ifv']}]},
    {'stage': 'caravan', 'goal': 'Survive', 'points': ['town'], 'surviveSeconds': 180, 'cp': 6,
     'events': [{'at': '30', 'kind': 'Reinforce', 'team': 1, 'units': ['main_battle_tank', 'flame_tank', 'ifv']}]},
    {'stage': 'behemoth', 'goal': 'Boss', 'boss': {'def': 'behemoth', 'name': 'behemoth', 'x': 84, 'z': 84, 'heading': 225, 'health': 1.8}, 'cp': 0},
]
texts(d, ('Behemoth at Red Rock', 'Behemoth ở Red Rock'),
      ('The operation for Red Rock, with General Thorne\'s army on our flank for the first time. Take the wellhead, choose your blow, '
       'take the oasis and hold it, then bring down the Behemoth itself.',
       'Chiến dịch giành Red Rock, lần đầu tiên có đạo quân của tướng Thorne ở bên sườn. Chiếm giếng dầu, chọn đòn đánh, '
       'chiếm và giữ ốc đảo, rồi hạ chính Behemoth.'),
      (('The first drawing', 'Bản vẽ đầu tiên'),
       ('That night Mara told Kade everything: the Behemoth programme, the prototype with her name on it, the day she understood what it was for. '
        'Kade listened, then asked one question: "Can you stop the next one?" She said yes.',
        'Đêm đó Mara kể với Kade tất cả: chương trình Behemoth, bản nguyên mẫu mang tên cô, cái ngày cô hiểu nó được làm ra để làm gì. '
        'Kade lắng nghe, rồi hỏi đúng một câu: "Cô chặn được chiếc tiếp theo không?" Cô trả lời có.')),
      [say('khai', 'Start', 'Red Rock, Brigade. The Behemoth is in there, and this time we have company.', 'Red Rock, Lữ đoàn. Behemoth ở trong đó, và lần này ta có bạn đồng hành.'),
       say('hung', None, 'Thorne\'s army, on your left. Good hunting, Colonel Kade.', 'Quân của Thorne, bên cánh trái anh. Chúc săn tốt, đại tá Kade.', at=12),
       say('mai', 'Win', 'You asked where I learned to build those, Colonel. Tonight I will tell you.', 'Ông từng hỏi tôi học chế tạo chúng ở đâu, đại tá. Tối nay tôi sẽ kể.')],
      stages_text={'wells': ('The Wellhead', 'Giếng dầu'), 'pumps': ('Blow the Pumps', 'Phá các giàn bơm'), 'guns': ('Thorne\'s Guns', 'Pháo của Thorne'),
                   'oasis': ('Take the Oasis', 'Chiếm ốc đảo'), 'caravan': ('Hold the Oasis', 'Giữ ốc đảo'), 'behemoth': ('Behemoth', 'Behemoth')},
      choices_text={'pumps': (('Blow the pumps', 'Phá các giàn bơm'), ('Varga\'s army earns 30 % less for the rest of the battle.', 'Quân Varga kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')),
                    'guns': (('Call Thorne\'s guns', 'Gọi pháo của Thorne'), ('Thorne\'s artillery fires on the enemy every minute for the rest of the battle.',
                                                                            'Pháo binh của Thorne nã vào quân địch mỗi phút trong suốt phần còn lại của trận.'))})
stage_says(d, 'wells', 'khai', 's1', 'The wellhead first. Then we choose.', 'Giếng dầu trước. Rồi ta sẽ chọn.')
stage_says(d, 'guns', 'hung', 's2', 'Thorne here. My guns are yours, Kade. Tell me where.', 'Thorne đây. Pháo của tôi là của anh, Kade. Chỉ chỗ đi.', at='end')
stage_says(d, 'behemoth', 'varga', 's5', 'My Behemoth, Colonel. Look at it closely.', 'Behemoth của tôi đây, đại tá. Nhìn cho kỹ.')

# ====================================================================== chapter 3: The Long Winter (Orlov; Raven's first flight)

rewrite('c3m05', brief=('The Harpy has been hunting our supply columns over the pass, and an ace in a black-marked jet flies with it. '
                        'Bring the gunship down. This is what the anti-air was for.',
                        'Harpy vẫn săn các đoàn tiếp tế của ta trên đèo, và một phi công át chủ bài lái chiếc phản lực mang phù hiệu đen bay cùng nó. '
                        'Bắn rơi pháo hạm bay. Phòng không có là để cho lúc này.'),
        lines=[say('quaden', 'Boss', 'The Harpy hunts, I watch. Hello again, little Hawk.', 'Harpy đi săn, ta ngồi xem. Chào lại nhé, chim ưng non.'),
               say('dieuhau', 'Boss', 'Black bird on a red disc. That\'s Raven. He\'s here.', 'Chim đen trên nền tròn đỏ. Là Raven. Hắn ở đây.')])
mark(mission('c3m05'), set_piece=True)
retext('radio.khai.c3m10.2', 'The highlands are open. Rest while you can, Brigade.', 'Cao nguyên đã mở. Nghỉ được lúc nào thì nghỉ, Lữ đoàn.')
rewrite('c3m10', lines=[say('orlov', 'Win', 'Withdraw. Winter always comes back, Colonel.', 'Rút lui. Mùa đông luôn quay lại, đại tá.')])

# Fenrir: the side mission's chase moves into the Whiteout Pass blizzard (the frozen Behemoth Mk.II of chapter 6 goes to fog).
d = mission('c3s2')
d.update(map='whiteout', weather='Snow', reversed=True)
mission('c6m05')['weather'] = 'Fog'
retext('mission.c3s2.brief', 'Nadia has found Orlov\'s winter vanguard in the Whiteout Pass blizzard: Fenrir, a heavy hunter that marks targets for his guns. Chase it down before the storm lifts.',
       'Nadia phát hiện xe tiên phong mùa đông của Orlov giữa bão tuyết Whiteout Pass: Fenrir, một thợ săn hạng nặng đánh dấu mục tiêu cho pháo của ông ta. Đuổi theo và hạ nó trước khi bão tan.')

d = clone('c3m01', 'c3m11', 3, map_='frostpeak', weather='Snow', playerBase='None', general='orlov', enemyDeck=ORLOV)
texts(d, ('The Radar Road', 'Đường radar'),
      ('The road to Orlov\'s radar line runs through three frozen hamlets on the Frostpeak slopes. Take all three in the snow; his spotters are in every one.',
       'Con đường tới tuyến radar của Orlov chạy qua ba xóm nhỏ đóng băng trên sườn Frostpeak. Chiếm cả ba trong tuyết; người chỉ điểm của ông ta nấp ở từng xóm.'),
      (('Spotters', 'Người chỉ điểm'),
       ('Each hamlet had a radio in its church tower, tuned to one of Orlov\'s batteries. Nadia kept all three.',
        'Mỗi xóm có một chiếc bộ đàm trên tháp nhà thờ, dò đúng tần số một khẩu đội của Orlov. Nadia giữ lại cả ba.')),
      [say('linh', 'Start', 'A spotter in every hamlet. Take them and his guns go deaf.', 'Mỗi xóm đều có người chỉ điểm. Chiếm xong là pháo của ông ta điếc.'),
       say('orlov', 'Win', 'Three spotters lost. I have thirty more, Colonel.', 'Mất ba người chỉ điểm. Ta còn ba mươi người nữa, đại tá.')])

d = clone('c2m01', 'c3m12', 3, map_='frostpeak', weather='Overcast', playerBase='None', general='orlov', enemyDeck=ORLOV)
d['waves'].pop('spawns', None)
d['waves']['roster'] = ['mortar_carrier', 'mlrs', 'ifv', 'main_battle_tank', 'artillery']
texts(d, ('Under the Guns', 'Dưới làn pháo'),
      ('Orlov knows where we are. For five minutes every gun on his line will fire at one valley, ours, and his screen will come in behind the shells. Survive it.',
       'Orlov biết ta đang ở đâu. Trong năm phút, mọi khẩu pháo trên tuyến của ông ta sẽ nã vào một thung lũng, thung lũng của ta, và quân yểm hộ sẽ tràn vào sau làn đạn. Trụ vững.'),
      (('Craters', 'Hố đạn'),
       ('Afterwards the engineers counted four hundred craters in the valley. Orlov had missed by eleven metres on average. He would not like that number.',
        'Sau đó công binh đếm được bốn trăm hố đạn trong thung lũng. Trung bình Orlov bắn trượt mười một mét. Ông ta sẽ không thích con số ấy.')),
      [say('khai', 'Start', 'Five minutes under his guns. Keep moving, keep alive.', 'Năm phút dưới làn pháo của hắn. Cứ di chuyển, cứ sống sót.'),
       say('orlov', None, 'Adjust fire. Two hundred metres east.', 'Chỉnh bắn. Lệch đông hai trăm mét.', at=70)])

# ====================================================================== interlude I: Blueprints (Mara's past; the Foundry)

FOUNDRY = ('map:foundry',)
d = mark(clone('c1m03', 'i1m01', 13, map_='foundry', weather='Night', playerBase='None', general='varga', enemyDeck=VARGA_EARLY,
               speaker='mai', difficulty='Normal'), awaits=FOUNDRY)
texts(d, ('The Foundry Gates', 'Cổng Foundry'),
      ('The Foundry has three ways in: the loading gate, the rail shed and the smelter. Take all three at night, quietly, before the guard knows we are here.',
       'Foundry có ba lối vào: cổng bốc dỡ, nhà ga đường ray và xưởng luyện. Chiếm cả ba trong đêm, thật lặng lẽ, trước khi lính gác biết ta đã tới.'),
      (('Home', 'Chốn cũ'),
       ('Mara walked through the gate she had used every morning for six years. The badge reader still knew her name.',
        'Mara đi qua cánh cổng cô từng đi mỗi sáng suốt sáu năm. Máy đọc thẻ vẫn còn nhận ra tên cô.')),
      [say('mai', 'Start', 'Left at the smelter, second door. I could walk this in my sleep.', 'Rẽ trái ở xưởng luyện, cửa thứ hai. Tôi có thể đi đường này cả trong mơ.'),
       say('khai', 'Win', 'The gates are ours. Mara, lead the way.', 'Các cổng là của ta. Mara, dẫn đường đi.')])

d = mark(clone('c1s1', 'i1m02', 13, map_='foundry', weather='Fog', general='varga', enemyDeck=VARGA_EARLY, speaker='brenn', difficulty='Normal'), awaits=FOUNDRY)
texts(d, ('The Ledger', 'Sổ cái'),
      ('Major Brenn knows how Hegemon files things: in triplicate. The Behemoth drawings are split between three archive rooms. Put a vehicle in each and he will do the rest.',
       'Thiếu tá Brenn biết Hegemon lưu hồ sơ thế nào: ba bản một. Bản vẽ Behemoth bị chia ra ba phòng lưu trữ. Đưa xe tới từng phòng, phần còn lại để ông lo.'),
      (('Signed for', 'Đã ký nhận'),
       ('Brenn logged every drawing he carried out: four hundred and twelve sheets, one coffee stain, and a signature on page one he asked Mara to explain. It was hers.',
        'Brenn ghi sổ từng bản vẽ ông mang ra: bốn trăm mười hai tờ, một vết cà phê, và một chữ ký ở trang đầu mà ông nhờ Mara giải thích. Đó là chữ ký của cô.')),
      [say('brenn', 'Start', 'Three rooms, three copies. Hegemon never threw anything away.', 'Ba phòng, ba bản. Hegemon chưa bao giờ vứt bỏ thứ gì.'),
       say('brenn', 'Win', 'Four hundred and twelve sheets. Sign here, Engineer.', 'Bốn trăm mười hai tờ. Ký vào đây, kỹ sư.')])

d = clone('c1m05', 'i1m03', 13, map_='foundry', weather='Overcast', general='varga', enemyDeck=VARGA, difficulty='Normal', speaker='mai')
boss(d,'behemoth_mk0', fallback='behemoth', health=0.9, name='behemoth_mk0')
mark(d, set_piece=True, awaits=FOUNDRY + ('boss:behemoth_mk0',))
texts(d, ('Behemoth Mk.0', 'Behemoth Mk.0'),
      ('The alarm has woken the Foundry\'s oldest guard: Behemoth Mk.0, the prototype Mara designed before she knew better. '
       'It is slow and old, and it knows every corner of these halls. Stop it.',
       'Tiếng báo động đã đánh thức lính gác lâu năm nhất của Foundry: Behemoth Mk.0, bản nguyên mẫu Mara thiết kế khi cô chưa hiểu chuyện. '
       'Nó chậm và cũ, nhưng thuộc từng góc của các xưởng này. Chặn nó lại.'),
      (('Her first', 'Chiếc đầu tiên'),
       ('On the Mk.0\'s rear plate, under the paint, Mara found her own initials, welded on her first day at the Foundry. She was twenty-three. She did not know yet what it was for.',
        'Trên tấm giáp sau của chiếc Mk.0, dưới lớp sơn, Mara tìm thấy chữ viết tắt tên mình, hàn vào ngày đầu tiên cô tới Foundry. Khi ấy cô hai mươi ba tuổi. Cô chưa biết nó được làm ra để làm gì.')),
      [say('varga', 'Start', 'Engineer Lind. You came back for your firstborn?', 'Kỹ sư Lind. Cô quay về vì đứa con đầu lòng à?'),
       say('mai', 'Boss', 'That is my prototype. Hit the left track: I never fixed the tensioner.', 'Đó là bản nguyên mẫu của tôi. Đánh vào xích trái: tôi chưa bao giờ sửa bộ căng xích.'),
       say('mai', 'Win', 'Rest now. I am sorry I built you.', 'Nghỉ đi. Xin lỗi vì tôi đã tạo ra mày.')])

d = mark(clone('c3m03', 'i1m04', 13, map_='foundry', weather='Rain', general='varga', enemyDeck=VARGA, speaker='brenn'), awaits=FOUNDRY)
texts(d, ('Out of the Foundry', 'Rời Foundry'),
      ('We have the drawings; Hegemon wants them back before they reach the trucks. Hold the loading yard until the convoy is loaded.',
       'Ta đã có bản vẽ; Hegemon muốn lấy lại trước khi chúng lên xe. Giữ bãi bốc dỡ cho tới khi đoàn xe chất hàng xong.'),
      (('Paperwork', 'Giấy tờ'),
       ('The convoy left with forty crates of drawings and one of spare parts. Brenn had put the spare parts on the list himself.',
        'Đoàn xe rời đi với bốn mươi thùng bản vẽ và một thùng phụ tùng. Chính Brenn đã tự ghi thùng phụ tùng vào danh sách.')),
      [say('brenn', 'Start', 'Four minutes to load. Nobody touches the crates marked blue.', 'Bốn phút để chất hàng. Không ai được đụng vào các thùng đánh dấu xanh.'),
       say('khai', 'Win', 'The convoy is out. Mara, are you all right?', 'Đoàn xe ra rồi. Mara, cô ổn chứ?'),
       say('mai', 'Win', 'I will be. Let\'s go home.', 'Rồi sẽ ổn. Ta về thôi.')])

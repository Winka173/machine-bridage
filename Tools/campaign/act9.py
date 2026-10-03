"""Prompt 22, pass 2 (section D): the story's choices and the missions each option leads to, the clues about Thorne on
Nadia's radio in chapters 4-6, and the cards the story itself hands out (story loot). See act5.py for the tools.

Choices (D.5): the mission that offers one carries "storyChoice" (pass 1). Each option is one new mission, right after
it in the order of play, marked "branch" (the choice) and "option"; only the chosen one is played, then the story goes
on as before. A branch mission is a copy of one on its battlefield with its set-up changed (prompt 4's rule, checked by
build_campaign), unlocks no card (the route never hangs on a choice) and is paid from the mission before it, like a
side mission (build_campaign.pay_base); the economy's tune leaves the branches out, so no other mission's pay moves.
What an option does later (reinforcements in chapter 9, a blinder enemy in chapter 12) is the Game layer's
(Narrative.cs); its words are here and in Tools/campaign/narrative.py.

Story loot (D.6): four cards move to the mission of the story beat that gives them, and a card of the same chapter
pair moves back the other way, so every chapter still opens four to seven cards and no mission's count changes.
"""

import json

import campaign_kit as kit
from campaign_kit import mission, retext, say
from act4 import FLIP_SAFE
from act5 import clone, texts
import act8

# ====================================================================== D.6: story loot, one-for-one swaps

SWAPS = [
    # Tempest's rail gun (chapter 4's port) and the laser tank (chapter 11's rail yard) change places.
    ('railgun_truck', 'c11m01', 'c4m10'), ('laser_tank', 'c4m10', 'c11m01'),
    # Venn brings the drone mothership over (chapter 5's operation); the drone hangar goes to chapter 12.
    ('swarm_carrier', 'c12m04', 'c5m10'), ('drone_hangar', 'c5m10', 'c12m04'),
    # The jammer goes to chapter 9's listening war (play-test 14 deleted the deployable bunker, the Lancet truck and the
    # wingman drone, whose swaps stood here).
    ('ew_jammer', 'c10m04', 'c9m01'),
]

for card, frm, to in SWAPS:
    a, b = mission(frm), mission(to)
    if card not in a.get('unlocks', []):
        raise SystemExit(f'story loot: {card} is not unlocked by {frm}')
    a['unlocks'] = [u for u in a['unlocks'] if u != card]
    if not a['unlocks']:
        del a['unlocks']
    b['unlocks'] = b.get('unlocks', []) + [card]

# ====================================================================== D.2: Nadia's clues about Thorne (chapters 4-6)

CLUES = [
    ('c4m08', say('linh', 'Win', 'Thorne\'s column is "delayed by fuel" again. Third time. I\'m writing it down.',
                  'Đoàn xe của Thorne lại "chậm vì thiếu xăng". Lần thứ ba rồi. Tôi ghi lại đây.')),
    ('c5m07', say('linh', 'Win', 'Hegemon moved before our orders went out. Someone reads them early.',
                  'Hegemon di chuyển trước khi lệnh của ta được phát đi. Có người đọc lệnh sớm.')),
    ('c6m09', say('linh', 'Win', 'Thorne\'s HQ went quiet for an hour. So did Varga\'s guns. The same hour.',
                  'Sở chỉ huy của Thorne im lặng một tiếng. Pháo của Varga cũng vậy. Cùng một tiếng.')),
]

for mid, line in CLUES:
    d = mission(mid)
    key = retext(f'radio.{line.speaker}.{mid}.d1', line.en, line.vi)
    d['radio'] = d.get('radio', []) + [kit.radio(line.on, key)]

# ====================================================================== D.5: the choices' missions


def _signature(m):
    return {
        'direction': bool(m.get('reversed')),
        'weather': m['weather'],
        'goal': m['goal'],
        'area': json.dumps(m.get('playArea'), sort_keys=True),
        'base': (m.get('variant', 'conquest'), m.get('playerBase', 'None'), m.get('enemyBase', 'None')),
    }


def _differ(a, b):
    sa, sb = _signature(a), _signature(b)
    return sum(1 for k in sa if sa[k] != sb[k])


def free_setup(d):
    """A set-up for <d> that differs from every other mission on its battlefield in two ways at least: the weather
    first, then the player's base, then the side it is played from (only for a goal that can be turned round)."""
    others = [m for m in kit.MISSIONS if m['map'] == d['map'] and m['id'] != d['id']]
    rev = bool(d.get('reversed'))
    directions = [rev, not rev] if d['goal'] in FLIP_SAFE else [rev]
    bases = [d.get('playerBase', 'None')] + [b for b in ('None', 'Anchor') if b != d.get('playerBase', 'None')]
    weathers = [w for w in sorted(kit.WEATHER[d['map']]) if w != d['weather']] + [d['weather']]
    for direction in directions:
        for base in bases:
            for weather in weathers:
                c = dict(d, weather=weather, playerBase=base)
                if direction:
                    c['reversed'] = True
                else:
                    c.pop('reversed', None)
                if all(_differ(c, o) >= 2 for o in others):
                    d.clear()
                    d.update(c)
                    return d
    raise SystemExit(f"act9: no free set-up for {d['id']} on {d['map']}")


# (choice, option, new id, source, speaker, name, brief, fragment, lines, extra data)
BRANCHES = [
    ('c4.pursuit', 'sea', 'c4m17', 'c4m16', 'khai',
     ('Last Boats', 'Những chuyến tàu cuối'),
     ('Kessler\'s staff are racing for the last boats with his codebooks and his charts of the coast. Catch both staff cars '
      'on the quays before they sail, and he goes to sea blind.',
      'Bộ tham mưu của Kessler đang lao ra những chuyến tàu cuối cùng, mang theo sổ mật mã và hải đồ của cả dải bờ biển. Chặn '
      'cả hai xe tham mưu trên cầu tàu trước khi tàu nhổ neo, và hắn sẽ ra khơi như kẻ mù.'),
     (('The charts', 'Bộ hải đồ'),
      ('Kessler\'s charts came off the quay wet and complete: every minefield, every buoy, every hidden fuel dump on the coast. '
       'He got away by sea. His maps did not.',
       'Hải đồ của Kessler được vớt lên từ cầu tàu, ướt sũng nhưng còn nguyên: mọi bãi mìn, mọi phao tiêu, mọi kho nhiên liệu giấu '
       'dọc bờ biển. Hắn thoát ra biển. Bản đồ của hắn thì không.')),
     [say('kessler', 'Start', 'Chasing me, Colonel? The harbour burns behind you.', 'Đuổi theo ta à, đại tá? Bến cảng đang cháy sau lưng ngươi đấy.'),
      say('khai', 'Win', 'He sails without his charts. Now we know every fuel dump on this coast.',
          'Hắn ra khơi mà không có hải đồ. Giờ ta biết mọi kho nhiên liệu trên bờ biển này.')],
     {}),
    ('c4.pursuit', 'harbour', 'c4m18', 'c4m07', 'linh',
     ('Harbour Lights', 'Đèn bến cảng'),
     ('Three ferries full of families are still tied up in Iron Harbor, and Kessler\'s rearguard is shelling the quays to cover '
      'his escape. Hold the terminal and the fish market until the ferries are out.',
      'Ba chiếc phà chở đầy các gia đình vẫn còn neo ở Iron Harbor, và đội đoạn hậu của Kessler đang pháo kích cầu tàu để yểm '
      'hộ hắn chạy. Giữ nhà ga và chợ cá cho tới khi phà ra được khơi.'),
     (('The ferries', 'Những chuyến phà'),
      ('Eleven hundred people left Iron Harbor that night. The ferry captains sent the brigade a crate of spare parts they had '
       'hidden from Hegemon for two years, "for whoever stays".',
       'Một nghìn một trăm người rời Iron Harbor đêm ấy. Các thuyền trưởng phà gửi lữ đoàn một thùng phụ tùng họ giấu Hegemon suốt '
       'hai năm, "cho những ai ở lại".')),
     [say('linh', 'Start', 'Kessler is getting away. The ferries are not. Your call was the right one.',
          'Kessler đang thoát. Mấy chiếc phà thì không. Ông chọn đúng rồi.'),
      say('khai', 'Win', 'All three ferries clear. Kessler can wait.', 'Cả ba chiếc phà đã ra khơi. Kessler để sau.')],
     # Held, not protected: Iron Harbor has two missions that protect its buildings already.
     {'rarePrints': 3, 'goal': 'Hold', 'points': ['town'], 'holdSeconds': 300,
      '_drop': ('targets', 'protectNeeded', 'targetHealth', 'surviveSeconds')}),
    ('c8.miners', 'rescue', 'c8m13', 'c8m11', 'varro',
     ('The Miners of Deepcut', 'Thợ mỏ Deepcut'),
     ('Thorne is holding three hundred miners in the pit\'s camps to dig for Kronos. Varro\'s militia knows the tunnels. Take '
      'the three camps and every miner walks out.',
      'Thorne đang giữ ba trăm thợ mỏ trong các lán trại dưới hố để đào đường cho Kronos. Dân quân của Varro thuộc từng đường hầm. '
      'Chiếm cả ba lán trại và mọi người thợ mỏ sẽ được ra ngoài.'),
     (('Three hundred', 'Ba trăm người'),
      ('The miners came out blinking into the sun. Most went home. Sixty of them stayed, took rifles and trucks, and asked where '
       'the brigade was going next.',
       'Những người thợ mỏ bước ra, nheo mắt dưới nắng. Phần lớn về nhà. Sáu mươi người ở lại, cầm súng, lái xe tải và hỏi lữ đoàn '
       'sẽ đi đâu tiếp.')),
     [say('varro', 'Start', 'My brother is in the east camp. Get him out, Colonel, and my people follow you anywhere.',
          'Em trai tôi ở lán phía đông. Đưa nó ra, đại tá, và người của tôi sẽ theo ông tới bất cứ đâu.'),
      say('varro', 'Win', 'Every camp open. Sixty of them want to fight. I said yes.',
          'Mọi lán trại đã mở. Sáu mươi người muốn chiến đấu. Tôi đồng ý rồi.')],
     {}),
    ('c8.miners', 'direct', 'c8m14', 'c8m02', 'khai',
     ('Straight at Kronos', 'Đánh thẳng vào Kronos'),
     ('Kronos draws its power from one line down the pit, and Thorne\'s paymaster sits beside the switchgear with a year of '
      'wages. Hold the ramp while the sappers cut the line. The pay chest comes with it.',
      'Kronos lấy điện từ một đường dây duy nhất dẫn xuống hố, và viên quản lương của Thorne ngồi ngay cạnh tủ điện với lương của '
      'cả một năm. Giữ con dốc trong lúc công binh cắt đường dây. Hòm lương đi kèm luôn.'),
     (('The pay chest', 'Hòm lương'),
      ('A year of Thorne\'s payroll, in the Accord\'s own notes: the money the government sent him to fight Hegemon. Nadia '
       'counted it twice and said nothing for a long time.',
       'Lương cả năm của quân Thorne, bằng chính tiền của Accord: số tiền chính phủ gửi ông ta để đánh Hegemon. Nadia đếm hai lần '
       'rồi im lặng rất lâu.')),
     [say('hung', 'Start', 'You came for the machine, not the miners. We are more alike than you think.',
          'Anh tới vì cỗ máy, không phải vì thợ mỏ. Ta giống nhau hơn anh tưởng đấy.'),
      say('khai', 'Win', 'Line cut. Kronos runs on its batteries now, and we have Thorne\'s money.',
          'Đã cắt đường dây. Kronos giờ chạy bằng ắc quy, còn ta giữ tiền của Thorne.')],
     {}),
    ('c11.radar', 'radar', 'c11m12', 'c11m07', 'linh',
     ('Blind the Array', 'Làm mù Skygate'),
     ('The Skygate Array\'s radar runs on the fuel tanks at the foot of its masts. Burn them and Hegemon fights the last '
      'battle half blind, from Helion\'s pads to the salt.',
      'Radar của Skygate Array chạy bằng các bồn nhiên liệu dưới chân cột ăng-ten. Đốt chúng đi và Hegemon sẽ đánh trận cuối trong '
      'cảnh nửa mù, từ bãi phóng Helion tới sa mạc muối.'),
     (('Dark masts', 'Cột ăng-ten tắt'),
      ('The Array\'s dishes kept turning for an hour after the tanks burned, sweeping nothing. Helion\'s operators were '
       'told to look out of the window.',
       'Các chảo radar của Skygate vẫn quay thêm một tiếng sau khi bồn nhiên liệu cháy, quét vào khoảng không. Người trực ở Helion '
       'được lệnh nhìn qua cửa sổ.')),
     [say('aurel', 'Start', 'You would put out my eyes? I have others, in orbit.',
          'Ông muốn móc mắt tôi ư? Tôi còn những con mắt khác, trên quỹ đạo.'),
      say('linh', 'Win', 'The Array is dark. At Helion they will be looking through fog.',
          'Skygate đã tắt. Ở Helion chúng sẽ phải nhìn qua sương mù.')],
     {}),
    ('c11.radar', 'launch', 'c11m13', 'c11m04', 'khai',
     ('The Short Road', 'Đường tắt'),
     ('The service road runs straight to the launch pads. Take it fast, look at every pad and get out before the Array turns '
      'its guns round. No time for anything else.',
      'Đường công vụ chạy thẳng tới các bệ phóng. Đi thật nhanh, xem từng bệ phóng rồi rút trước khi Skygate quay pháo lại. Không '
      'có thời gian cho việc gì khác.'),
     (('Pad count', 'Đếm bệ phóng'),
      ('Four pads, three empty, one with a shape under a tarpaulin the size of a cathedral. The recon footage paid for itself: '
       'the Accord bought the brigade new stores on the strength of it.',
       'Bốn bệ phóng, ba bệ trống, một bệ có thứ gì đó phủ bạt to bằng cả một nhà thờ. Đoạn phim trinh sát đáng đồng tiền: Accord '
       'cấp cho lữ đoàn kho tiếp tế mới nhờ nó.')),
     [say('khai', 'Start', 'In, look, out. Nobody stops to fight.', 'Vào, nhìn, rút. Không ai dừng lại đánh.'),
      say('linh', 'Win', 'Four pads, one full. We are a day ahead of them now.', 'Bốn bệ phóng, một bệ có hàng. Giờ ta đi trước chúng một ngày.')],
     {'rarePrints': 3, 'timeLimit': 600, 'starTime': 300}),
]

# How each option pays against the mission before it (build_campaign.pay_base): coins, blueprints.
PAY = {'sea': (1.6, 1.0), 'harbour': (1.0, 1.0), 'rescue': (1.0, 1.0), 'direct': (2.0, 1.0), 'radar': (1.0, 1.0), 'launch': (1.5, 1.0)}

for choice, option, new, src, speaker, name, brief, fragment, lines, extra in BRANCHES:
    at = next(m for m in kit.MISSIONS if m.get('storyChoice') == choice)
    d = clone(src, new, at['chapter'])
    d['speaker'] = speaker
    d['branch'] = choice
    d['option'] = option
    d['_pay'] = PAY[option]
    for k in extra.get('_drop', ()):
        d.pop(k, None)
    d.update({k: v for k, v in extra.items() if k != '_drop'})
    free_setup(d)
    texts(d, name, brief, fragment, lines)
    order = act8.ORDER[at['chapter']]
    after = order.index(at['id'])
    # The options in the order they are offered, right after the mission that offers them.
    while order[after + 1:after + 2] and mission(order[after + 1]).get('branch') == choice:
        after += 1
    order.insert(after + 1, new)

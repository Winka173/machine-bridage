"""Prompt 20, pass 1: the twelve chapters in four acts.

The nine-chapter campaign's missions keep their words and data in act1.py, act2.py and act3.py under
their new ids (chapter 7 became 10, 8 became 7, 9 became 12; a few single missions moved: see
story.MOVES). This file lays them out for the new story:

  - the boss slots of every chapter (story.CHAPTER_BOSSES): a mission fights a slot's boss by its id;
    one pass 2 has not built yet is fought as the "fallback" stand-in until its def exists;
  - the unlock route and the HQ levels over twelve chapters (UNLOCKS, HQ_LEVELS);
  - the new missions of chapters 8 (Underground), 9 (Rough Seas) and 11 (The Orbital Gate), and the
    single missions that replace the ones that moved (c1m05, c3s2, c4m06): each is an existing mission
    of the same battlefield written again (clone), so its positions stay right for that map;
  - short new words where a mission's boss or place in the story changed (retext / rewrite).

Words here are short on purpose: prompt 22 rewrites the story and its names.
"""

import copy
import re

import campaign_kit as kit
from campaign_kit import T, add_mission, mission, retext, say, scripted
from act1 import ORLOV
from act2 import KESSLER
from act3 import AUREL, QUADEN

LY_HAN = ['main_battle_tank', 'heavy_tank', 'titan_tank', 'bmpt', 'ifv', 'aa_vehicle', 'mlrs', 'tank_destroyer']

# Goals whose mission can be flipped (played from the other side): what they name is a map point, a unit
# written from the player's corner, or the centre. Destroy, Protect, Escort, Intercept and Boss missions
# name props and roads fixed on the map, so a copy of one keeps its side.
FLIP_SAFE = {'Capture', 'Hold', 'Survive', 'Duel', 'Hunt', 'Recon', 'ShootDown', 'Relieve'}
DROP = ('radio', 'tips', 'legacy', 'unlocks', 'hqLevel', 'rarePrints', 'towerGear', 'replay', 'epilogue', 'side', 'after', 'challenge')

# The chapter's pace for the new missions (the neighbours' numbers: chapters 7 and 10 on either side).
PACE = {
    1: dict(enemyCp=8, enemyIncome=0.7, playerCp=24, playerIncome=1.4, playerCap=36),
    3: dict(enemyCp=12, enemyIncome=0.85, playerCp=26, playerIncome=1.45, playerCap=36),
    4: dict(enemyCp=12, enemyIncome=0.85, playerCp=28, playerIncome=1.5, playerCap=38),
    6: dict(enemyCp=13, enemyIncome=0.9, playerCp=30, playerIncome=1.55, playerCap=40),
    8: dict(enemyCp=14, enemyIncome=0.9, playerCp=30, playerIncome=1.55, playerCap=40),
    9: dict(enemyCp=15, enemyIncome=0.95, playerCp=30, playerIncome=1.6, playerCap=40),
    11: dict(enemyCp=16, enemyIncome=1.0, playerCp=32, playerIncome=1.65, playerCap=42),
}


def chapter_of(mid):
    return int(re.match(r'c(\d+)', mid).group(1))


def pace(d, chapter, at_least=True):
    for k, v in PACE[chapter].items():
        if k in d or k.startswith('player'):
            d[k] = max(d.get(k, 0), v) if at_least else v


def clone(src, new, flip=False, **over):
    """A copy of mission <src> as <new>: its battlefield and set-up, none of its rewards or words."""
    d = copy.deepcopy(mission(src))
    for k in DROP:
        d.pop(k, None)
    if flip:
        if d['goal'] not in FLIP_SAFE or d.get('operation'):
            raise SystemExit(f'{new}: {src} ({d["goal"]}) cannot be flipped')
        d['reversed'] = not d.get('reversed', False)
    d['id'] = new
    d['chapter'] = chapter_of(new)
    for s in d.get('stages', []):
        # The source's own stage lines stay with it; the shared ones (strikes, weakened supply) come along.
        s['events'] = [e for e in s.get('events', []) if not (e['kind'] == 'Radio' and f'.{src}.' in e['key'])]
    d.update(over)
    if not d.get('reversed'):
        d.pop('reversed', None)
    if d['chapter'] in PACE:
        pace(d, d['chapter'])
    return d


def boss(d_or_stage, slot, fallback=None, health=None, name=None, **extra):
    """Puts a boss slot on a mission or a stage: the slot's def (the boss's id), the stand-in it is fought as until then."""
    b = d_or_stage.setdefault('boss', {})
    old = b.get('def')
    b['def'] = slot
    b['name'] = name or slot
    if fallback and fallback != slot:
        b['fallback'] = fallback
        b['fallbackHealth'] = health if health is not None else b.get('health', b.get('fallbackHealth', 1.0))
        b.pop('health', None)
    elif health is not None:
        b['health'] = health
    b.update(extra)
    return old


def stage(d, key):
    return next(s for s in d['stages'] if s['stage'] == key)


def copy_stage_texts(src, new, titles=None):
    """An operation's stage titles and choices, from the operation it was written from (new titles where given)."""
    titles = titles or {}
    for key in list(kit.TEXTS):
        for kind in ('stage', 'choice'):
            prefix = f'{kind}.{src}.'
            if key.startswith(prefix) and not (kind == 'stage' and key[len(prefix):] in titles):
                T(f'{kind}.{new}.' + key[len(prefix):], *kit.TEXTS[key])
    for k, text in (titles or {}).items():
        T(f'stage.{new}.{k}', *text)


def new(d, name, brief, fragment, lines, stages=None):
    """Registers a written-again mission with its own words."""
    return add_mission(d, name, brief, fragment, lines)


def rewrite(mid, name=None, brief=None, fragment=None, lines=None):
    """New words for a mission already written (its old radio lines are dropped when new ones are given)."""
    d = mission(mid)
    if name:
        retext(f'mission.{mid}.name', *name)
    if brief:
        retext(f'mission.{mid}.brief', *brief)
    if fragment:
        retext(f'mission.{mid}.fragment.title', *fragment[0])
        retext(f'mission.{mid}.fragment', *fragment[1])
    if lines is not None:
        d['radio'] = [r for r in d.get('radio', []) if f'.{mid}.' not in r['key']]
        for i, line in enumerate(lines):
            key = retext(f'radio.{line.speaker}.{mid}.p{i + 1}', line.en, line.vi)
            d['radio'].append(kit.radio(line.on, key, line.arg, line.at))
    return d


def stage_line(d, stage_key, speaker, key, en, vi, at='start'):
    """A stage's own line, replacing the one it had at that moment."""
    s = stage(d, stage_key)
    s['events'] = [e for e in s.get('events', []) if not (e['kind'] == 'Radio' and e.get('at') == at and f".{d['id']}." in e['key'])]
    s['events'].append({'at': at, 'kind': 'Radio', 'key': retext(f"radio.{speaker}.{d['id']}.{key}", en, vi)})


def side(d, after, rare=None, gear=None):
    d['side'] = True
    d['after'] = after
    if rare:
        d['rarePrints'] = rare
    if gear:
        d['towerGear'] = gear
    return d


# ====================================================================== the missions that moved

# c3m08: the Whiteout night escort, a side mission before, is chapter 3's eighth main mission now.
for k in ('side', 'after', 'rarePrints', 'towerGear'):
    mission('c3m08').pop(k, None)

# c6m05: the frozen Behemoth of the Whiteout (old c3m08) is Varga's Behemoth Mk.II.
boss(mission('c6m05'), 'behemoth_mk2', fallback='behemoth', health=2.2)
mission('c6m05')['difficulty'] = 'Normal'
rewrite('c6m05', name=('Behemoth Mk.II', 'Behemoth Mk.II'),
        brief=('Varga has rebuilt the Behemoth we burned at Dunebreak: heavier, heated for the snow, and coming down the Whiteout pass. Stop Behemoth Mk.II before it reaches our lines.',
               'Varga đã dựng lại chiếc Behemoth ta đốt ở Dunebreak: nặng hơn, lắp hệ sưởi cho tuyết, và đang xuống Đèo Bão Tuyết. Chặn Behemoth Mk.II trước khi nó tới phòng tuyến của ta.'))

# c6m08: the landing hovercraft (old c1m05) is Charybdis, landing Varga's counterstrike on our beach.
d = mission('c6m08')
d['boss']['name'] = 'landing_hovercraft'
d['difficulty'] = 'Normal'
pace(d, 6)
rewrite('c6m08', name=('Charybdis', 'Charybdis'),
        brief=('Varga\'s counterstrike comes by sea: Charybdis, a landing hovercraft, is bringing a company of armour onto the beach where we landed. Sink it before it unloads.',
               'Đợt tổng phản công của Varga tới từ biển: Charybdis, một tàu đệm khí đổ bộ, đang chở cả một đại đội thiết giáp lên chính bãi biển ta đã đổ bộ. Đánh chìm nó trước khi nó dỡ quân.'),
        fragment=(('The same sand', 'Cùng một bãi cát'),
                  ('The brigade fought on the beach where it had landed months before. Some of the old tracks were still in the sand.',
                   'Lữ đoàn đánh trên chính bãi biển nơi mình đổ bộ mấy tháng trước. Vài vết xích cũ vẫn còn trên cát.')),
        lines=[say('linh', 'Start', 'Charybdis, on the water. It is coming for our beach.', 'Charybdis, trên mặt nước. Nó đang nhắm vào bãi biển của ta.'),
               say('khai', 'Win', 'The beach stays ours.', 'Bãi biển vẫn là của ta.')])

# c8m05: the Earth Worm (old c6m08) is Tartarus, sent under the dam by Lý Hàn.
d = mission('c8m05')
d['general'] = 'hung'
d['enemyDeck'] = LY_HAN
rewrite('c8m05', name=('Tartarus', 'Tartarus'),
        brief=('Lý Hàn has sent Tartarus, Varga\'s old tunnelling machine, under the Hydro Dam towards the power station. Stop it before it gets there.',
               'Lý Hàn đã tung Tartarus, cỗ máy khoan cũ của Varga, luồn dưới Đập Thủy Điện về phía trạm phát điện. Chặn nó trước khi nó tới nơi.'),
        lines=[say('hung', 'Start', 'You will not see it coming, Khải.', 'Các người sẽ không thấy nó tới đâu, Khải.'),
               say('mai', 'Win', 'Tartarus is stuck in its own tunnel.', 'Tartarus kẹt luôn trong đường hầm của nó.')])

# c10m08: Spectre (old c6m05) flies for Wolff over the Whiteout now.
d = mission('c10m08')
d['general'] = 'quaden'
d['enemyDeck'] = QUADEN
rewrite('c10m08', name=('Spectre', 'Spectre'),
        brief=('Wolff\'s gunship aircraft circles high over the Whiteout pass, shelling our convoys to Skyhold. Bring Spectre down with everything that reaches the sky.',
               'Máy bay pháo của Wolff bay vòng trên cao quanh Đèo Bão Tuyết, nã vào các đoàn xe của ta tới Skyhold. Bắn rơi Spectre bằng mọi thứ với tới được bầu trời.'),
        lines=[say('dieuhau', 'Start', 'Spectre is up there. Keep the launchers busy.', 'Spectre đang ở trên đó. Cho các bệ phóng làm việc liên tục.')])

# c11m05: the rail supergun (old c4m06) is Gungnir, Orlov's last battle, at the orbital gate's rail yard.
d = mission('c11m05')
d['general'] = 'orlov'
d['enemyDeck'] = ORLOV
pace(d, 11)
rewrite('c11m05', name=('Gungnir', 'Gungnir'),
        brief=('Orlov guards the orbital gate with Gungnir, the biggest gun he ever had, on the rails of the Rust Yard. This is his last battle. Silence the gun.',
               'Orlov canh giữ cửa ngõ quỹ đạo bằng Gungnir, khẩu pháo lớn nhất hắn từng có, trên đường ray của Bãi Sắt Gỉ. Đây là trận cuối của hắn. Bắt khẩu pháo câm họng.'),
        fragment=(('The last coordinate', 'Tọa độ cuối cùng'),
                  ('Orlov gave himself up by radio, reading out his own position like a fire mission. Then he asked for tea.',
                   'Orlov ra hàng qua bộ đàm, đọc tọa độ của chính mình như một nhiệm vụ bắn. Rồi hắn xin một ấm trà.')),
        lines=[say('orlov', 'Start', 'Gungnir has your grid, Colonel. Fire mission.', 'Gungnir có tọa độ của ngươi rồi, đại tá. Nhiệm vụ bắn.'),
               say('orlov', 'Win', 'Recalculating... no. Cease fire. It is over.', 'Tính lại... không. Ngừng bắn. Hết rồi.')])

# ====================================================================== boss slots on missions that stayed

# Chapter 2: Inferno is the fifth mission's mini boss, the Behemoth the operation's main boss.
d = mission('c2m05')
boss(d, 'behemoth_inferno', health=1.6)
rewrite('c2m05', name=('Inferno', 'Inferno'),
        brief=('Varga has sent Inferno ahead into the sandstorm: a Behemoth rebuilt round flame projectors. Keep out of its reach and burn it first.',
               'Varga tung Inferno đi trước vào bão cát: một chiếc Behemoth dựng lại quanh các súng phun lửa. Tránh xa tầm với của nó và hạ nó trước.'),
        fragment=(('Cooling (optional)', 'Làm mát (tùy chọn)'),
                  ('Workshop order for the Inferno: "Two flame projectors, one thermobaric box, cooling for the crew (optional)." The cooling was never fitted.',
                   'Phiếu đặt hàng xưởng cho Inferno: "Hai súng phun lửa lớn, một hộp rocket nhiệt áp, hệ làm mát cho kíp lái (tùy chọn)." Hệ làm mát chưa bao giờ được lắp.')),
        lines=[say('varga', 'Start', 'You want fire, Colonel? Here is fire.', 'Muốn lửa hả, đại tá? Lửa đây.'),
               say('khai', 'Win', 'One of Varga\'s monsters down. The big one is still in the refinery.', 'Một con quái vật của Varga đã gục. Con lớn nhất vẫn còn trong nhà máy lọc dầu.')])
d = mission('c2m10')
boss(stage(d, 'inferno'), 'behemoth', health=1.8)
retext('stage.c2m10.inferno', 'Behemoth', 'Behemoth')
stage_line(d, 'inferno', 'varga', 's5', 'My Behemoth, Colonel. Look at it closely.', 'Behemoth của ta đây, đại tá. Nhìn cho kỹ.')
retext('mission.c2m10.brief', 'The operation Varga fears: take the oil field and the oasis, choose what to hit next, then blow the refinery\'s towers and tanks. The Behemoth is parked inside it.',
       'Chiến dịch mà Varga sợ nhất: chiếm mỏ dầu và ốc đảo, chọn mục tiêu kế tiếp, rồi cho nổ tháp và bồn chứa của nhà máy. Behemoth đang đỗ bên trong nó.')
retext('mission.c2m10.fragment.title', 'The napkin\'s monster', 'Con quái vật trên tờ giấy ăn')
retext('mission.c2m10.fragment', 'Varga\'s Behemoth burned in its own refinery. Mai walked round the wreck twice and said nothing.',
       'Behemoth của Varga cháy ngay trong nhà máy lọc dầu của hắn. Mai đi quanh xác nó hai vòng và không nói gì.')

# Chapter 5: Locust, a small drone carrier, over the burning ridge.
d = mission('c5m08')
boss(d, 'locust', fallback='drone_mothership', health=0.4, x=84, z=84, heading=225, route=[60, 60, 20, 30, -10, 10])
d['radio'].append(kit.radio('Boss', retext('radio.linh.c5m08.p1', 'Locust: one of Sen\'s small drone carriers. Shoot it down.', 'Locust: một tàu mang drone cỡ nhỏ của Sen. Bắn hạ nó.')))

# Chapter 6: Moloch, the mobile factory, is the operation's main boss (the Behemoth Mk.II moved to c6m05).
d = mission('c6m10')
boss(stage(d, 'monster'), 'moloch', fallback='mobile_fortress', health=1.8)
retext('stage.c6m10.monster', 'Moloch', 'Moloch')
stage_line(d, 'monster', 'varga', 's3', 'Moloch builds faster than you can burn, Colonel.', 'Moloch đóng xe nhanh hơn ngươi đốt, đại tá.')
retext('mission.c6m10.brief', 'Varga\'s last card is Moloch, a factory on tracks that builds tanks as it rolls, and it is coming for the dam. Hold the crest until Lý Hàn\'s army arrives.',
       'Quân bài cuối của Varga là Moloch, một nhà máy bánh xích vừa lăn vừa đóng xe tăng, và nó đang tiến về con đập. Giữ đỉnh đập cho tới khi quân của Lý Hàn tới.')

# Chapter 7: Nemesis (the missile train) stays the fifth mission; Atlas covers Lý Hàn's escape after the betrayal.
d = mission('c7m10')
s = stage(d, 'strikeback')
boss(s, 'supreme_command', health=0.8, x=60, z=60, heading=225, route=[70, 70, 100, 90], fleeAt=0.5)
s['events'].append({'at': 'start', 'kind': 'Radio', 'key': retext('radio.hung.c7m10.atlas', 'Atlas, cover me. We are leaving the city.', 'Atlas, yểm trợ ta. Ta rời thành phố.')})

# Chapter 10: the Icarus seen over Skyhold is the unfinished prototype; Argus watches the side mission.
boss(mission('c10m05'), 'icarus_mk0', fallback='silver_bug', health=4.4)
retext('mission.c10m05.name', 'Icarus Mk.0', 'Icarus Mk.0')
d = mission('c10s2')
boss(d, 'argus', fallback='command_airship', health=0.45, x=84, z=84, heading=225, route=[50, 70, 10, 50, -30, 60])
d.setdefault('radio', []).append(kit.radio('Boss', retext('radio.dieuhau.c10s2.p1', "Argus, Quạ Đen's recon airship. It is watching us.", 'Argus, khí cầu trinh sát của Quạ Đen. Nó đang theo dõi ta.')))

# Chapter 12: Kessler's last fight brings Tempest; Locust flies for Aurel; the Behemoth Mk.II is Varga's last.
d = mission('c12m02')
boss(d, 'behemoth_tempest', health=0.6, x=84, z=84, heading=225, route=[50, 50, 10, 20])
d['radio'].append(kit.radio('Boss', retext('radio.kessler.c12m02.p1', 'Tempest, on schedule. As always.', 'Tempest, đúng lịch. Như mọi khi.')))
for mid, name, brief, line in [
    ('c12m04', ('Aurel\'s Guard', 'Cận vệ của Aurel'),
     ('Aurel\'s own guard holds the northern pads of the launch site. Level their HQ.', 'Đội cận vệ riêng của Aurel giữ các bệ phóng phía bắc. San phẳng sở chỉ huy của chúng.'),
     say('aurel', 'Start', 'My guard costs more than your brigade, Colonel.', 'Đội cận vệ của tôi đắt hơn cả lữ đoàn của ông, đại tá.')),
    ('c12m06', ('The Last Airfield', 'Sân bay cuối cùng'),
     ('The last Hegemon airfield covers the launch pad. Wolff is gone; Aurel flies its jets himself, by remote. Level the HQ.', 'Sân bay cuối cùng của Hegemon che chắn bệ phóng. Wolff đã không còn; Aurel tự điều khiển máy bay từ xa. San phẳng sở chỉ huy.'),
     say('aurel', 'Start', 'Pilots are an expense. Drones are an investment.', 'Phi công là chi phí. Drone là khoản đầu tư.')),
]:
    mission(mid)['general'] = 'aurel'
    mission(mid)['enemyDeck'] = AUREL
    rewrite(mid, name=name, brief=brief, lines=[line])
d = mission('c12m05')
boss(d, 'locust', fallback='drone_mothership', health=0.7)
rewrite('c12m05', name=('Locust', 'Locust'),
        brief=('Aurel took Sen\'s drone programme when she left, and kept building. A Locust carrier is covering the desert road to the launch site. Bring it down.',
               'Aurel chiếm lấy chương trình drone của Sen khi bà bỏ đi, và vẫn đóng tiếp. Một tàu Locust đang che chắn con đường sa mạc tới bãi phóng. Bắn hạ nó.'),
        fragment=(('Sen\'s drones', 'Bầy drone của Sen'),
                  ('Sen looked at the wreck for a long time. "I built the first one to find people under rubble," she said.',
                   'Sen nhìn xác nó rất lâu. "Chiếc đầu tiên tôi làm ra là để tìm người dưới đống đổ nát," bà nói.')),
        lines=[say('sen', 'Boss', 'That is my design. Aim for the hangar doors.', 'Đó là thiết kế của tôi. Nhắm vào cửa khoang chứa.')])
d = mission('c12m10')
boss(stage(d, 'command'), 'behemoth_mk2', fallback='behemoth', health=1.6)
retext('stage.c12m10.command', 'Varga\'s Last Stand', 'Trận cuối của Varga')
stage_line(d, 'command', 'varga', 's4', 'One more Behemoth, Colonel. The last one.', 'Thêm một chiếc Behemoth nữa, đại tá. Chiếc cuối cùng.')

# ====================================================================== new missions: the ones that replace the movers

# c1m05: Bastion Mk.0, Brandt's prototype fortress, in the Greenvale fields.
add_mission({'id': 'c1m05', 'chapter': 1, 'map': 'greenvale', 'goal': 'Boss', 'weather': 'Night', 'timeLimit': 1140, 'reinforcements': 2,
             'boss': scripted('bastion_mk0', (84, 84), heading=225, route=[(55, 55), (20, 25), (-15, -5)], fallback='fortress_bastion', fallbackHealth=0.55, name='bastion_mk0'),
             'enemyAi': 'commander', 'enemyStance': 'Attack', 'difficulty': 'Normal', 'enemyCp': 10, 'enemyIncome': 0.8,
             'enemyDeck': ['armored_car', 'light_tank', 'ifv', 'main_battle_tank', 'mortar_carrier', 'rocket_technical'],
             'playerCp': 24, 'playerIncome': 1.4, 'playerBase': 'Anchor', 'starTime': 600, 'starLosses': 8},
            ('Bastion Mk.0', 'Bastion Mk.0'),
            ('Brandt has sent his prototype fortress across the Greenvale fields at night to crush our new camp. It is slow and thin-skinned. Stop it.',
             'Brandt tung pháo đài nguyên mẫu băng qua cánh đồng Lũng Xanh trong đêm để nghiền nát trại mới của ta. Nó chậm và giáp mỏng. Chặn nó lại.'),
            (('The prototype', 'Bản nguyên mẫu'),
             ('Stencilled on the wreck: "Bastion Mk.0, garrison use only". Brandt had kept the real one for Ashfield.',
              'Trên xác nó có dòng chữ sơn: "Bastion Mk.0, chỉ dùng cho đồn trú". Brandt giữ chiếc thật cho Ashfield.')),
            [say('linh', 'Start', 'Large contact moving on the camp. Brandt\'s prototype.', 'Mục tiêu cỡ lớn đang tiến về trại. Bản nguyên mẫu của Brandt.'),
             say('khai', 'Win', 'If that was the prototype, the Bastion will be worse.', 'Nếu đó mới là bản nguyên mẫu, Bastion sẽ còn tệ hơn.')])

# c3s2: Fenrir, Orlov's winter vanguard, in the Frostpeak snow (no camp: a hunt across the heights).
d = side({'id': 'c3s2', 'chapter': 3, 'map': 'frostpeak', 'goal': 'Boss', 'weather': 'Snow', 'general': 'orlov', 'timeLimit': 1080, 'reinforcements': 2,
          'boss': scripted('fenrir', (84, 84), heading=225, route=[(55, 60), (15, 30), (-20, 10)], fallback='behemoth', fallbackHealth=1.2, name='fenrir'),
          'enemyAi': 'commander', 'enemyStance': 'Defend', 'difficulty': 'Normal', 'enemyCp': 12, 'enemyIncome': 0.85, 'enemyDeck': ORLOV,
          'playerCp': 26, 'playerIncome': 1.45, 'playerCap': 36, 'starTime': 660, 'starLosses': 10}, 'c3m07', gear='Rare')
add_mission(d, ('Fenrir', 'Fenrir'),
            ("Linh has found Orlov's winter vanguard in the Frostpeak snow: Fenrir, a heavy hunter that marks targets for his guns. Hunt it down.",
             'Linh phát hiện xe tiên phong mùa đông của Orlov trong tuyết Frostpeak: Fenrir, một thợ săn hạng nặng đánh dấu mục tiêu cho pháo của hắn. Săn nó.'),
            (('Blind guns', 'Pháo mù'),
             ("With Fenrir gone, Orlov's batteries fired at the old coordinates for an hour. There was nobody there.",
              'Mất Fenrir, các khẩu đội của Orlov bắn vào tọa độ cũ suốt một giờ. Ở đó chẳng còn ai.')),
            [say('linh', 'Start', "Fenrir is in the snow. It sees for Orlov's guns.", 'Fenrir ở trong tuyết. Nó là mắt cho pháo của Orlov.')])

# c4m06: Scylla, Kessler's command destroyer, at Lighthouse Bay (Leviathan's water, in fog, without our camp).
d = clone('c4m11', 'c4m06', weather='Fog', playerBase='None', starTime=720)
boss(d, 'scylla', fallback='leviathan', health=0.5, name='scylla')
pace(d, 4, at_least=False)
add_mission(d, ('Scylla', 'Scylla'),
            ('Kessler\'s command destroyer, Scylla, is escorting his ships out of Lighthouse Bay in the fog. Sink it before the convoy gets away.',
             'Tàu khu trục chỉ huy của Kessler, Scylla, đang hộ tống tàu của hắn rời Vịnh Hải Đăng trong sương. Đánh chìm nó trước khi đoàn tàu thoát được.'),
            (('Cargo', 'Hàng hóa'),
             ('The ships Scylla was guarding carried Behemoth parts from Varga\'s works. Kessler ships everything, for everyone.',
              'Những con tàu Scylla hộ tống chở linh kiện Behemoth từ xưởng của Varga. Kessler chở mọi thứ, cho mọi người.')),
            [say('kessler', 'Start', 'Scylla leaves on time, Colonel.', 'Scylla rời bến đúng giờ, đại tá.')])

# ====================================================================== chapter 8: Underground (Lý Hàn, the mines)
# Its battlefields stand in for the open-pit mine (openpit) until part M builds it: c8m02, c8m07 and c8m10 move there.

H8 = dict(general='hung', enemyDeck=LY_HAN)
d = clone('c2m02', 'c8m01', flip=True, weather='Night', **H8)
new(d, ('Into the Mines', 'Vào khu mỏ'),
    ('Lý Hàn\'s trail leads north into the mining country. Take the canyon crossings from the other side, at night.',
     'Dấu vết của Lý Hàn dẫn lên vùng mỏ phía bắc. Chiếm các ngả qua hẻm núi từ phía bên kia, trong đêm.'),
    (('The trail', 'Dấu vết'), ('Lý Hàn\'s staff cars left the capital in the rain. By morning their tracks were in the red canyons.',
                                  'Xe tham mưu của Lý Hàn rời thủ đô trong mưa. Tới sáng, vết bánh đã in trên các hẻm núi đỏ.')),
    [say('khai', 'Start', 'He ran north. We follow.', 'Hắn chạy lên phía bắc. Ta đuổi theo.')])

d = clone('c2m01', 'c8m02', flip=True, weather='Night', **H8)
new(d, ('The Ore Depot', 'Kho quặng'),
    ('We hold the ore depot on the dunes. Lý Hàn wants it back tonight. Keep the brigade alive until morning.',
     'Ta đang giữ kho quặng trên đồi cát. Lý Hàn muốn lấy lại nó ngay đêm nay. Giữ cho lữ đoàn trụ vững tới sáng.'),
    (('Ore', 'Quặng'), ("Hegemon had paid for the depot's ore in advance, for ten years. Nobody would collect it now.",
                          'Hegemon đã trả tiền quặng của kho trước cho mười năm. Giờ chẳng còn ai tới lấy.')),
    [say('mai', 'Start', 'No ore, no new tanks for him. Hold it.', 'Không có quặng, hắn hết xe tăng mới. Giữ lấy nó.')])

d = clone('c2m06', 'c8m03', flip=True, weather='Clear', **H8)
new(d, ('Battery Hunt', 'Săn khẩu đội'),
    ('Lý Hàn\'s rocket batteries shell the mine road from the mesas. Linh has marked them. Hunt them down.',
     'Các khẩu đội rocket của Lý Hàn nã vào đường mỏ từ trên các khối đá. Linh đã đánh dấu chúng. Săn chúng.'),
    (('Old habits', 'Thói quen cũ'), ('Lý Hàn\'s gunners had trained with ours. They still used our old call signs.',
                                        'Pháo thủ của Lý Hàn từng huấn luyện cùng người của ta. Họ vẫn dùng mật danh cũ của ta.')),
    [say('linh', 'Start', 'Three batteries, marked. They know our tricks.', 'Ba khẩu đội, đã đánh dấu. Chúng biết các mẹo của ta.')])

d = clone('c2m07', 'c8m04', flip=True, weather='Sandstorm', **H8)
new(d, ('The Mine Town', 'Thị trấn mỏ'),
    ('The miners of the canyon town have risen against Lý Hàn, and his tanks have them ringed. Break the ring in the sandstorm.',
     'Thợ mỏ ở thị trấn hẻm núi đã nổi dậy chống Lý Hàn, và xe tăng của hắn vây kín họ. Phá vòng vây trong bão cát.'),
    (('Spare parts', 'Phụ tùng'), ('The miners paid the brigade in spare parts. Half of them fitted the Behemoth Mai keeps "for the museum".',
                                     'Thợ mỏ trả ơn lữ đoàn bằng phụ tùng. Một nửa lắp vừa chiếc Behemoth Mai giữ lại "cho bảo tàng".')),
    [say('khai', 'Start', 'They rose for us. We go for them.', 'Họ đứng lên vì ta. Ta tới vì họ.')])

d = clone('c6m06', 'c8m06', weather='Night', playerBase='None', **H8)
new(d, ('The Tunnel Mouth', 'Miệng hầm'),
    ('The mine tunnels come out under the dam. Hold the crossing at night while Lý Hàn tries to break through.',
     'Các đường hầm mỏ thông ra dưới con đập. Giữ ngả qua trong đêm khi Lý Hàn tìm cách chọc thủng.'),
    (('Echoes', 'Tiếng vọng'), ('All night the tunnels echoed with engines. Nobody could tell whose.',
                                  'Suốt đêm các đường hầm vọng tiếng động cơ. Không ai phân biệt được là của ai.')),
    [say('hung', 'Start', 'The mountain is mine, Khải. Every tunnel.', 'Ngọn núi là của ta, Khải. Mọi đường hầm.')])

d = clone('c2m05', 'c8m07', weather='Clear', playerBase='Defend', **H8)
boss(d, 'ixion', fallback='behemoth', health=1.1)
new(d, ('Ixion', 'Ixion'),
    ('A haul truck with wheels taller than a tank is coming across the dunes at full speed: Ixion. Stop it before it rams our columns.',
     'Một xe chở quặng có bánh cao hơn xe tăng đang lao qua đồi cát hết tốc lực: Ixion. Chặn nó trước khi nó húc vào đội hình của ta.'),
    (('Wheels', 'Bánh xe'), ('One of Ixion\'s wheels rolled on alone for two kilometres after the truck died.',
                               'Một bánh của Ixion còn tự lăn thêm hai cây số sau khi chiếc xe đã chết máy.')),
    [say('linh', 'Boss', 'Ixion. Break a wheel and it loses its line.', 'Ixion. Phá một bánh là nó mất hướng.')])

d = clone('c6s2', 'c8m08', weather='Storm', playerBase='Anchor', **H8)
new(d, ('Eyes on the Pit', 'Mắt nhìn hố mỏ'),
    ('Before we go into the deepest pit, Linh wants to see it. Get a vehicle onto each marked spot in the storm.',
     'Trước khi vào hố mỏ sâu nhất, Linh muốn tận mắt thấy nó. Đưa xe tới từng điểm đánh dấu trong cơn bão.'),
    (('The pit', 'Hố mỏ'), ('The photographs showed a machine the size of a building at the bottom of the pit. Its bucket wheel was turning.',
                              'Các tấm ảnh cho thấy một cỗ máy to bằng tòa nhà dưới đáy hố. Bánh gầu của nó đang quay.')),
    [say('linh', 'Start', 'Look, do not linger.', 'Nhìn thôi, đừng nán lại.')])

d = clone('c2m09', 'c8m09', flip=True, weather='Night', **H8)
new(d, ('Lý Hàn\'s Camp', 'Trại của Lý Hàn'),
    ('Lý Hàn has dug his headquarters into the end of the canyon. Level it. He will run again; make him run faster.',
     'Lý Hàn đã đào sở chỉ huy vào cuối hẻm núi. San phẳng nó. Hắn sẽ lại chạy; bắt hắn chạy nhanh hơn.'),
    (('Medals', 'Huân chương'), ('In the abandoned camp: Lý Hàn\'s medals from the liberation war, in a box, polished.',
                                   'Trong trại bỏ hoang: những tấm huân chương thời chiến tranh giải phóng của Lý Hàn, trong một chiếc hộp, được đánh bóng.')),
    [say('hung', 'Start', 'I earned this country before you were a colonel.', 'Ta đã giành lấy đất nước này khi ngươi còn chưa là đại tá.')])

d = clone('c2m10', 'c8m10', weather='Clear', playerBase='None', operation=True, **H8)
boss(stage(d, 'inferno'), 'kronos', fallback='mobile_fortress', health=1.3)
copy_stage_texts('c2m10', 'c8m10', {'inferno': ('Kronos', 'Kronos')})
stage(d, 'inferno')['events'].append({'at': 'start', 'kind': 'Radio', 'key': T('radio.hung.c8m10.s5', 'Wake up, Kronos. Dig them a grave.', 'Thức dậy đi, Kronos. Đào cho chúng một nấm mồ.')})
new(d, ('The Deepest Pit', 'Hố sâu nhất'),
    ('The operation into Lý Hàn\'s mine: take the pit\'s rim, choose what to hit next, blow the works, then face what waits at the bottom: Kronos.',
     'Chiến dịch vào khu mỏ của Lý Hàn: chiếm miệng hố, chọn mục tiêu kế tiếp, phá các xưởng, rồi đối mặt với thứ đang chờ dưới đáy: Kronos.'),
    (('Buried', 'Chôn vùi'), ('Kronos went down into its own pit. Lý Hàn was already on a boat.',
                                'Kronos sụp xuống chính hố mỏ của nó. Lý Hàn thì đã ở trên một con tàu.')),
    [say('khai', 'Start', 'Into the pit, Brigade.', 'Xuống hố, Lữ đoàn.'),
     say('linh', 'Win', 'Lý Hàn has reached the coast. He is heading for Kessler\'s old ships.', 'Lý Hàn đã tới bờ biển. Hắn đang tìm tới những con tàu cũ của Kessler.')])

d = side(clone('c2s1', 'c8s1', flip=True, weather='Clear', **H8), 'c8m03', rare=34)
new(d, ('Survey Maps', 'Bản đồ khảo sát'),
    ('Linh wants the mine\'s survey maps from three buildings on the dunes. Look, do not linger.', 'Linh muốn lấy bản đồ khảo sát của khu mỏ từ ba tòa nhà trên đồi cát. Nhìn thôi, đừng nán lại.'),
    (('Surveys', 'Khảo sát'), ('The maps showed every tunnel Lý Hàn could use. Linh drew the rest.', 'Bản đồ cho thấy mọi đường hầm Lý Hàn có thể dùng. Linh vẽ nốt phần còn lại.')),
    [say('linh', 'Start', 'Three buildings. Quick in, quick out.', 'Ba tòa nhà. Vào nhanh, ra nhanh.')])

d = side(clone('c2s2', 'c8s2', flip=True, weather='Night', **H8), 'c8m07', gear='Epic')
new(d, ('Night Flights', 'Chuyến bay đêm'),
    ('Lý Hàn is flying his gold out of the mines at night. Shoot down his transports.', 'Lý Hàn đang chở vàng ra khỏi khu mỏ trong đêm. Bắn hạ các máy bay vận tải của hắn.'),
    (('Gold', 'Vàng'), ('The crates were not gold. They were Hegemon contracts, signed.', 'Các thùng hàng không phải vàng. Đó là những bản hợp đồng Hegemon, đã ký.')),
    [say('dieuhau', 'Start', 'Night hunting. My favourite.', 'Săn đêm. Món tôi thích nhất.')])

# ====================================================================== chapter 9: Rough Seas (Lý Hàn and Kessler's remnants)

H9 = dict(general='hung', enemyDeck=LY_HAN)
d = clone('c4m02', 'c9m01', weather='Storm', playerBase='Anchor', **H9)
new(d, ('The Harbour Again', 'Lại bến cảng'),
    ('Lý Hàn has taken Ironport with what is left of Kessler\'s men. Take the docks back in the storm.',
     'Lý Hàn đã chiếm Ironport cùng tàn quân của Kessler. Chiếm lại cầu tàu trong cơn bão.'),
    (('Old uniforms', 'Quân phục cũ'), ('Kessler\'s sailors still wore his badges, with Lý Hàn\'s ribbon pinned over them.',
                                          'Thủy thủ của Kessler vẫn đeo phù hiệu của hắn, với dải băng của Lý Hàn ghim đè lên.')),
    [say('khai', 'Start', 'The port again. This time we keep it.', 'Lại bến cảng. Lần này ta giữ nó.')])

d = clone('c1m01', 'c9m02', flip=True, weather='Rain', **H9)
new(d, ('Back to the Beach', 'Trở lại bãi biển'),
    ('Lý Hàn is landing troops on the beach where our war began. Take the beach from the other side, in the rain.',
     'Lý Hàn đang đổ quân lên chính bãi biển nơi cuộc chiến của ta bắt đầu. Chiếm bãi biển từ phía bên kia, trong mưa.'),
    (('Full circle', 'Một vòng tròn'), ('The same dunes, the same rain. This time the brigade came from inland.',
                                          'Cùng những đụn cát, cùng cơn mưa. Lần này lữ đoàn tiến từ đất liền ra.')),
    [say('khai', 'Start', 'We know this beach. Better than he does.', 'Ta biết bãi biển này. Rõ hơn hắn.')])

d = clone('c4m03', 'c9m03', weather='Night', playerBase='Anchor', **H9)
new(d, ('Night Convoy', 'Đoàn xe đêm'),
    ('Take the supply convoy through the harbour roads at night. Lý Hàn\'s patrols are waiting.',
     'Đưa đoàn xe tiếp tế qua các con đường bến cảng trong đêm. Lính tuần của Lý Hàn đang chờ.'),
    (('Lights off', 'Tắt đèn'), ('The drivers went through the harbour with their lights off. One of them sang all the way.',
                                   'Các tài xế đi qua bến cảng với đèn tắt. Một người hát suốt dọc đường.')),
    [say('linh', 'Start', 'Patrols on the harbour road. Keep moving.', 'Lính tuần trên đường bến cảng. Cứ đi tiếp.')])

d = clone('c1m02', 'c9m04', weather='Storm', playerBase='Anchor', **H9)
new(d, ('The Coastal Guns', 'Pháo bờ biển'),
    ('Lý Hàn has put guns back on the beach. Destroy them before his ships come in.',
     'Lý Hàn đã đặt lại pháo trên bãi biển. Phá chúng trước khi tàu của hắn cập bờ.'),
    (('Rust', 'Gỉ sét'), ('Some of the guns were the ones we silenced on the first day, repaired.', 'Vài khẩu pháo chính là những khẩu ta bắt câm họng ngày đầu tiên, đã được sửa lại.')),
    [say('mai', 'Start', 'Same guns. Same weak mounts.', 'Vẫn những khẩu pháo đó. Vẫn những bệ yếu đó.')])

d = clone('c6m08', 'c9m05', weather='Fog', playerBase='None', **H9)
boss(d, 'caspian', fallback='landing_hovercraft', health=1.0)
new(d, ('Caspian', 'Caspian'),
    ('Out of the fog comes Caspian, a ground-effect ship that skims the waves and lands troops. Bring it down before it reaches the beach.',
     'Từ trong sương lao ra Caspian, một con tàu bay sát mặt sóng và đổ quân. Hạ nó trước khi nó tới bãi biển.'),
    (('Wings', 'Cánh'), ('Caspian\'s wing floated for a week. Children from the village swam out to sit on it.',
                           'Cánh của Caspian nổi trên mặt nước suốt một tuần. Trẻ con trong làng bơi ra ngồi lên nó.')),
    [say('linh', 'Boss', 'Caspian, low over the water. Fast.', 'Caspian, bay thấp trên mặt nước. Rất nhanh.')])

d = clone('c4m09', 'c9m06', flip=True, weather='Fog', **H9)
new(d, ('Lý Hàn\'s Harbour HQ', 'Sở chỉ huy bến cảng'),
    ('Lý Hàn has set up his headquarters on the far docks. Level it and cut him off from the sea.',
     'Lý Hàn đặt sở chỉ huy ở cầu tàu phía xa. San phẳng nó và cắt đường ra biển của hắn.'),
    (('Charts', 'Hải đồ'), ('Lý Hàn\'s charts showed one route out: past the lighthouse, where the submarine waited.',
                              'Hải đồ của Lý Hàn chỉ một đường thoát: qua ngọn hải đăng, nơi tàu ngầm đang chờ.')),
    [say('hung', 'Start', 'The sea does not belong to you, Khải.', 'Biển không thuộc về ngươi, Khải.')])

d = clone('c4m07', 'c9m07', weather='Night', playerBase='None', **H9)
new(d, ('The Lighthouse Keepers', 'Người giữ hải đăng'),
    ('Our spotters in the port buildings guide our guns. Keep one of them standing through Lý Hàn\'s night attack.',
     'Các trạm quan sát của ta trong khu bến cảng dẫn đường cho pháo. Giữ ít nhất một trạm đứng vững qua trận tấn công đêm của Lý Hàn.'),
    (('Lamps', 'Ngọn đèn'), ('The spotters kept one lamp lit all night, on purpose. It drew the fire away from the rest.',
                               'Các trạm quan sát cố ý để một ngọn đèn sáng suốt đêm. Nó hút hỏa lực khỏi những trạm còn lại.')),
    [say('khai', 'Start', 'Keep one standing. That is all we need.', 'Giữ một trạm đứng vững. Ta chỉ cần thế.')])

d = clone('c4m06', 'c9m08', weather='Rain', playerBase='Defend', general='hung')
boss(d, 'scylla', fallback='leviathan', health=0.6, name='scylla')
new(d, ('Scylla Again', 'Lại là Scylla'),
    ('Scylla is back in service under Lý Hàn\'s flag, guarding the bay in the rain. Sink it for good this time.',
     'Scylla trở lại hoạt động dưới cờ của Lý Hàn, canh vịnh trong mưa. Lần này đánh chìm hẳn nó.'),
    (('Patched', 'Vá víu'), ('Scylla\'s new plates were welded over the old holes. Some of the welds were ours.',
                               'Các tấm giáp mới của Scylla được hàn đè lên những lỗ thủng cũ. Vài đường hàn là của người bên ta.')),
    [say('hung', 'Start', 'Kessler\'s ship. My sailors.', 'Tàu của Kessler. Thủy thủ của ta.')])

d = clone('c1s2', 'c9m09', flip=True, weather='Clear', **H9)
new(d, ('Beach Hunt', 'Săn trên bãi biển'),
    ('Lý Hàn\'s mortar teams are shelling the beach road. Hunt the marked ones.', 'Các tổ súng cối của Lý Hàn đang nã vào đường bờ biển. Săn những tổ đã đánh dấu.'),
    (('Tea', 'Trà'), ('One of the mortar crews surrendered with their tea still hot. They offered it round.',
                        'Một tổ súng cối ra hàng khi ấm trà vẫn còn nóng. Họ mời mọi người cùng uống.')),
    [say('linh', 'Start', 'Mortar teams, marked. Move fast.', 'Các tổ súng cối, đã đánh dấu. Di chuyển nhanh.')])

d = clone('c4m10', 'c9m10', weather='Fog', playerBase='None', operation=True, **H9)
boss(stage(d, 'tempest'), 'typhon', fallback='behemoth_tempest', health=1.8)
copy_stage_texts('c4m10', 'c9m10', {'tempest': ('Typhon', 'Typhon')})
stage(d, 'tempest')['events'].append({'at': 'start', 'kind': 'Radio', 'key': T('radio.hung.c9m10.s4', 'Typhon, surface. Fire everything.', 'Typhon, nổi lên. Bắn tất cả.')})
new(d, ('Rough Seas', 'Biển động'),
    ('The operation for the coast: take the harbour, choose what to hit, clear the works, then stop Typhon, the missile submarine that is Lý Hàn\'s last card.',
     'Chiến dịch giành bờ biển: chiếm bến cảng, chọn mục tiêu, dọn sạch các xưởng, rồi chặn Typhon, chiếc tàu ngầm tên lửa là quân bài cuối của Lý Hàn.'),
    (('The general', 'Viên tướng'), ('Lý Hàn was taken on the bridge of his flagship, in full uniform. He asked to see Khải. Khải did not go.',
                                       'Lý Hàn bị bắt trên đài chỉ huy soái hạm, quân phục chỉnh tề. Hắn xin gặp Khải. Khải không tới.')),
    [say('khai', 'Start', 'This ends at sea, Brigade.', 'Chuyện này kết thúc trên biển, Lữ đoàn.'),
     say('hung', 'Win', 'Enough. Tell Khải I surrender.', 'Đủ rồi. Nói với Khải ta đầu hàng.'),
     say('linh', 'Win', 'His papers mention one thing again and again: Project Icarus.', 'Giấy tờ của hắn cứ nhắc mãi một thứ: Dự án Icarus.')])

d = side(clone('c4s2', 'c9s1', flip=True, weather='Fog', **H9), 'c9m03', gear='Epic')
new(d, ('The Last Minelayers', 'Những tàu rải mìn cuối cùng'),
    ('Kessler\'s old minelayers are working for Lý Hàn now. Hunt the marked ones before they close the harbour.',
     'Những xe rải mìn cũ của Kessler giờ làm việc cho Lý Hàn. Săn những chiếc đã đánh dấu trước khi chúng phong tỏa bến cảng.'),
    (('Timetables', 'Thời gian biểu'), ('The minelayers still worked to Kessler\'s timetable. That made them easy to find.',
                                          'Các xe rải mìn vẫn chạy theo thời gian biểu của Kessler. Nhờ thế mà dễ tìm.')),
    [say('linh', 'Start', 'They run on schedule. We will be early.', 'Chúng chạy đúng giờ. Ta sẽ tới sớm.')])

d = side(clone('c1m01', 'c9s2', weather='Fog', playerBase='Anchor', **H9), 'c9m07', rare=40)
new(d, ('The Radio Hut', 'Trạm vô tuyến'),
    ('Lý Hàn\'s radio posts on the beach talk to his ships. Take them in the fog.', 'Các trạm vô tuyến của Lý Hàn trên bãi biển liên lạc với tàu của hắn. Chiếm chúng trong sương.'),
    (('Frequencies', 'Tần số'), ('Linh kept the posts\' codebook. It opened every door of the next battle.',
                                   'Linh giữ lại cuốn mật mã của các trạm. Nó mở mọi cánh cửa cho trận đánh sau.')),
    [say('linh', 'Start', 'I want their radios intact.', 'Tôi cần radio của chúng còn nguyên.')])

# ====================================================================== chapter 11: The Orbital Gate (Aurel; Orlov's last battle)
# Its battlefields stand in for the orbital gate (orbitalgate) until part M builds it: c11m04, c11m07 and c11m10 move there.

A11 = dict(general='aurel', enemyDeck=AUREL)
d = clone('c4m01', 'c11m01', flip=True, weather='Night', **A11)
new(d, ('The Gate\'s Rail Yard', 'Bãi ray của cửa ngõ'),
    ('Aurel\'s orbital gate is fed by the rail yard. Take its crossings at night, from the far side.',
     'Cửa ngõ quỹ đạo của Aurel được tiếp tế qua bãi ray. Chiếm các ngả giao cắt trong đêm, từ phía bên kia.'),
    (('Freight', 'Hàng hóa'), ('The wagons were full of rocket fuel, stamped "Project Icarus".', 'Các toa đầy nhiên liệu tên lửa, đóng dấu "Dự án Icarus".')),
    [say('khai', 'Start', 'The gate first. Then the launch site.', 'Cửa ngõ trước. Rồi tới bãi phóng.')])

d = clone('c10m02', 'c11m02', flip=True, weather='Rain', **A11)
new(d, ('Eyes on the Gate', 'Mắt nhìn cửa ngõ'),
    ('Linh wants to see the gate\'s radar stations before we strike them. Get a vehicle onto each, in the rain.',
     'Linh muốn tận mắt thấy các trạm radar của cửa ngõ trước khi ta đánh. Đưa xe tới từng trạm, trong mưa.'),
    (('Guidance', 'Dẫn đường'), ('The radars were not watching for us. They were watching the sky, for Daedalus.',
                                   'Các radar không canh chừng ta. Chúng canh bầu trời, chờ Daedalus.')),
    [say('linh', 'Start', 'Every station. I need all of them.', 'Mọi trạm. Tôi cần tất cả.')])

d = clone('c3m02', 'c11m03', weather='Night', playerBase='None', **A11)
new(d, ('Blind the Gate', 'Làm mù cửa ngõ'),
    ('Destroy the radar dishes that guide Aurel\'s ships down from orbit.', 'Phá các chảo radar dẫn đường cho tàu của Aurel từ quỹ đạo xuống.'),
    (('Silence', 'Im lặng'), ('When the dishes fell, the sky went quiet. Then the first pod came down, off course.',
                                'Khi các chảo radar đổ, bầu trời im bặt. Rồi khoang đổ bộ đầu tiên rơi xuống, lệch hướng.')),
    [say('khai', 'Start', 'Blind it, and his ships land where we want.', 'Làm mù nó, tàu của hắn sẽ đáp đúng chỗ ta muốn.')])

d = clone('c4m04', 'c11m04', flip=True, weather='Clear', **A11)
new(d, ('The Side Pads', 'Bệ phóng phụ'),
    ('Aurel has side pads hidden round the rail yard. Find them before he fuels them.', 'Aurel giấu các bệ phóng phụ quanh bãi ray. Tìm ra chúng trước khi hắn nạp nhiên liệu.'),
    (('Countdown', 'Đếm ngược'), ('One pad already had a countdown clock running. Mai stopped it with a spanner.',
                                    'Một bệ đã có đồng hồ đếm ngược đang chạy. Mai dừng nó bằng một chiếc cờ lê.')),
    [say('mai', 'Start', 'Find the pads. I will bring the spanners.', 'Tìm các bệ phóng. Tôi sẽ mang cờ lê.')])

d = clone('c3m03', 'c11m06', flip=True, weather='Overcast', **A11)
new(d, ('Hold the Ridge', 'Giữ sườn núi'),
    ('Aurel wants the ridge above the gate back. Hold it until the guns are in place.', 'Aurel muốn lấy lại sườn núi phía trên cửa ngõ. Giữ nó cho tới khi pháo vào vị trí.'),
    (('High ground', 'Điểm cao'), ('From the ridge the brigade could see the launch site\'s lights on the horizon, far to the south.',
                                     'Từ sườn núi, lữ đoàn nhìn thấy ánh đèn của bãi phóng trên đường chân trời, tít phía nam.')),
    [say('khai', 'Start', 'Hold the high ground.', 'Giữ điểm cao.')])

d = clone('c10m04', 'c11m07', weather='Clear', playerBase='Defend', **A11)
boss(d, 'locust', fallback='drone_mothership', health=0.5, x=84, z=84, heading=225, route=[50, 60, 0, 30, -40, 50])
new(d, ('Locust over the Gate', 'Locust trên cửa ngõ'),
    ('A Locust drone carrier covers the gate\'s hangars. Burn the parked aircraft and bring the carrier down.',
     'Một tàu mang drone Locust che chắn các nhà chứa của cửa ngõ. Đốt máy bay đang đỗ và bắn hạ tàu mang drone.'),
    (('Sen\'s work', 'Công trình của Sen'), ('Sen recognised the carrier from its sound. "Version four," she said. "I never finished version four."',
                                               'Sen nhận ra tàu mang drone qua tiếng động cơ. "Phiên bản bốn," bà nói. "Tôi chưa bao giờ làm xong phiên bản bốn."')),
    [say('sen', 'Boss', 'Locust. Aurel finished my design.', 'Locust. Aurel đã làm nốt thiết kế của tôi.')])

d = clone('c3m09', 'c11m09', flip=True, weather='Fog', **A11)
new(d, ('The Gatekeeper', 'Người gác cổng'),
    ('Aurel\'s gate commander has dug in on the far side of the pass. Level the HQ.', 'Viên chỉ huy cửa ngõ của Aurel cố thủ ở phía bên kia đèo. San phẳng sở chỉ huy.'),
    (('Orders', 'Mệnh lệnh'), ('The commander\'s last order from Aurel: "Hold until the launch. Then you are free to go."',
                                 'Mệnh lệnh cuối Aurel gửi viên chỉ huy: "Giữ cho tới khi phóng. Sau đó anh được tự do."')),
    [say('aurel', 'Start', 'The gate is closed, Colonel. Permanently.', 'Cửa ngõ đã đóng, đại tá. Vĩnh viễn.')])

d = clone('c3m10', 'c11m10', weather='Clear', playerBase='None', operation=True, **A11)
boss(stage(d, 'fortress'), 'daedalus', fallback='silver_bug', health=2.0)
copy_stage_texts('c3m10', 'c11m10', {'fortress': ('Daedalus', 'Daedalus')})
stage(d, 'fortress')['events'].append({'at': 'start', 'kind': 'Radio', 'key': T('radio.aurel.c11m10.s4', 'Daedalus, bring them down on the gate.', 'Daedalus, thả chúng xuống cửa ngõ.')})
new(d, ('The Orbital Gate', 'Cửa ngõ quỹ đạo'),
    ('The operation for the gate: blind its radars, choose what to hit, break the defences, then bring down Daedalus as it lands Aurel\'s troops from orbit.',
     'Chiến dịch giành cửa ngõ: làm mù radar, chọn mục tiêu, phá tuyến phòng thủ, rồi hạ Daedalus khi nó đổ quân của Aurel từ quỹ đạo xuống.'),
    (('Falling', 'Rơi'), ('Daedalus came down on the gate it was built to use. Only the launch site was left.',
                            'Daedalus rơi xuống chính cửa ngõ nó được làm ra để dùng. Chỉ còn lại bãi phóng.')),
    [say('khai', 'Start', 'The gate, Brigade. The last door before the launch site.', 'Cửa ngõ, Lữ đoàn. Cánh cửa cuối cùng trước bãi phóng.')])

d = side(clone('c10s1', 'c11s1', flip=True, weather='Night', **A11), 'c11m03', rare=48)
new(d, ('Fuel Trucks', 'Xe nhiên liệu'),
    ('Aurel\'s fuel trucks are running to the pads at night. Hunt the marked ones.', 'Các xe nhiên liệu của Aurel đang chạy tới bệ phóng trong đêm. Săn những chiếc đã đánh dấu.'),
    (('Fuel', 'Nhiên liệu'), ('Every truck stopped was an hour more before Icarus could fly.', 'Mỗi xe bị chặn là thêm một giờ trước khi Icarus cất cánh được.')),
    [say('linh', 'Start', 'Fuel trucks, marked. Every one counts.', 'Xe nhiên liệu, đã đánh dấu. Chiếc nào cũng quan trọng.')])

d = side(clone('c4s1', 'c11s2', weather='Fog', playerBase='Anchor', **A11), 'c11m07', gear='Epic')
new(d, ('The Engineers\' Convoy', 'Đoàn xe công binh'),
    ('Mai\'s engineers need to reach the gate\'s wreckage before Aurel\'s men clear it. Take them through in the fog.',
     'Công binh của Mai cần tới đống đổ nát của cửa ngõ trước khi người của Aurel dọn sạch. Đưa họ qua trong sương.'),
    (('Salvage', 'Thu hồi'), ('From the wreckage Mai took one thing: a guidance computer. "For the museum," she said.',
                                'Từ đống đổ nát Mai lấy đúng một thứ: một máy tính dẫn đường. "Cho bảo tàng," cô nói.')),
    [say('mai', 'Start', 'Get my engineers there in one piece.', 'Đưa công binh của tôi tới nơi nguyên vẹn.')])

# The three new operations' stages and choices came with their sources' words; these named the wrong general.
retext('stage.c8m10.counter', 'Lý Hàn\'s Counterattack', 'Lý Hàn phản kích')
retext('choice.c8m10.tanks.info', 'Lý Hàn\'s army earns 30 % less for the rest of the battle.', 'Quân Lý Hàn kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')
retext('choice.c9m10.crane.info', 'Lý Hàn earns 30 % less for the rest of the battle.', 'Lý Hàn kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')
retext('choice.c11m10.depots.info', 'Aurel\'s army earns 30 % less for the rest of the battle.', 'Quân Aurel kiếm được ít hơn 30 % trong suốt phần còn lại của trận.')

# ====================================================================== the unlock route and the HQ levels (D.1, D.2)
# Four to six cards a chapter, towers and buildings among them; the five modules stay in acts I and II.
# The old route's cards in chapters 7-12 spread onto the new chapters 8, 9 and 11.

UNLOCKS = {
    'c1m01': ['rocket_technical'], 'c1m02': ['mortar_carrier'], 'c1m03': ['repair_drop'], 'c1m04': ['rocket_turret', 'repair_bay'],
    'c1m05': ['tank_destroyer'], 'c1m06': ['zu23_technical'],
    'c2m01': ['mlrs'], 'c2m02': ['sam_launcher'], 'c2m03': ['flame_tank'], 'c2m04': ['airstrike'], 'c2m05': ['heavy_tank'],
    'c2m06': ['atgm_tower', 'ammo_depot'],
    'c3m01': ['heavy_aa'], 'c3m02': ['attack_helicopter'], 'c3m03': ['uav_scan', 'ammo_carrier'], 'c3m04': ['dragons_teeth', 'radar_station'],
    'c3m05': ['recon_drone'],
    'c4m01': ['command_vehicle'], 'c4m02': ['attack_jet'], 'c4m03': ['wheeled_gun'], 'c4m04': ['logistics_station'], 'c4m05': ['field_tower'],
    'c4m10': ['laser_tank'], 'c4m11': ['heavy_turret.coastal'],
    'c5m01': ['strike_drone'], 'c5m02': ['fpv_carrier'], 'c5m04': ['twin_tank', 'airfield'], 'c5m05': ['long_sam'], 'c5m09': ['fighter_jet'],
    'c5m10': ['drone_hangar'],
    'c6m02': ['armored_bulldozer', 'c_ram'], 'c6m03': ['ew_tower', 'shield_carrier'], 'c6m04': ['scout_heli'], 'c6m06': ['lancet_truck'],
    'c7m01': ['vbied'], 'c7m02': ['turtle_tank'], 'c7m03': ['bmpt'], 'c7m04': ['smoke_carrier'],
    'c8m01': ['shahed_truck'], 'c8m02': ['counter_battery_radar'], 'c8m03': ['thermobaric_launcher'], 'c8m04': ['bunker_vehicle'],
    'c9m01': ['wingman_drone'], 'c9m02': ['remote_mines'], 'c9m03': ['iron_beam'], 'c9m04': ['artillery_emplacement'],
    'c10m01': ['sead_strike'], 'c10m02': ['heavy_rocket_artillery'], 'c10m04': ['ew_jammer'], 'c10m05': ['gunship_heli'],
    'c11m01': ['railgun_truck'], 'c11m02': ['stealth_fighter'], 'c11m03': ['cp_relay'], 'c11m04': ['heavy_turret'],
    'c12m02': ['cruise_missile'], 'c12m03': ['shield_tower'], 'c12m04': ['swarm_carrier'], 'c12m06': ['mine_layer'],
}
HQ_LEVELS = {'c1m04': 1, 'c3m05': 2, 'c6m04': 3, 'c9m05': 4, 'c11m04': 5}

for m in kit.MISSIONS:
    m.pop('unlocks', None)
    m.pop('hqLevel', None)
for mid, cards in UNLOCKS.items():
    mission(mid)['unlocks'] = list(cards)
for mid, level in HQ_LEVELS.items():
    mission(mid)['hqLevel'] = level

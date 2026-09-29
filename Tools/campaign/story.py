"""The story around the missions: who is who, the chapters, the boss files, the timeline and the
radio chatter every mission can fall back on. The missions themselves are in act1.py, act2.py
and act3.py."""

from campaign_kit import T

# ------------------------------------------------------------------------------------------ the campaign

T('campaign.story.title', 'Machine Brigade: The Lam Hai Front', 'Lữ Đoàn Cơ Giới: Mặt Trận Lam Hải')
T('campaign.story.prologue',
  'Two years ago, in one night, the private military corporation Hegemon seized the Lam Hai coast it had been paid to guard. '
  'Its director, Aurel, turned the ports, the oil fields and the highlands into a laboratory for weapons no army should own. '
  'The Coastal Alliance has rebuilt one brigade strong enough to go back: the 7th Mechanised, the Machine Brigade.',
  'Hai năm trước, chỉ trong một đêm, tập đoàn quân sự tư nhân Hegemon đã chiếm luôn dải duyên hải Lam Hải mà nó được thuê để canh giữ. '
  'Giám đốc Aurel biến bến cảng, mỏ dầu và vùng cao nguyên thành phòng thí nghiệm cho những thứ vũ khí không quân đội nào nên có. '
  'Liên minh Duyên hải đã dựng lại được một lữ đoàn đủ mạnh để quay về: Lữ đoàn Cơ giới 7, mà lính gọi là Lữ Đoàn Máy.')

# Prompt 20: four acts of three chapters.
ACTS = {
    1: ('Act I · The Landing', 'Hồi I · Đổ bộ'),
    2: ('Act II · The Counterattack', 'Hồi II · Phản công'),
    3: ('Act III · Betrayal', 'Hồi III · Phản bội'),
    4: ('Act IV · Silver Sky', 'Hồi IV · Bầu trời bạc'),
}
for n, (en, vi) in ACTS.items():
    T(f'act.{n}', en, vi, fresh=n >= 3)

# number, act, title, maps, general, opening card (3-4 sentences), timeline line once it is done
CHAPTERS = [
    (1, 1, ('Coast of Fire', 'Bờ biển lửa'), ['landingbeach', 'greenvale', 'ashfield'], None,
     ('Dawn over Bãi Đổ Bộ. The landing craft ground on the sand under Hegemon\'s coastal guns, and the 7th Mechanised Brigade rolls ashore to open the first front in two years. '
      'Colonel Trần Khải has one order: get off the beach, find ground to build on, and take the Ashfield fortress before the enemy wakes up. '
      'Behind its walls waits the Bastion, an old walking fortress, still more than enough to stop a brigade that hesitates.',
      'Bình minh trên Bãi Đổ Bộ. Xuồng đổ bộ tì mũi lên cát dưới làn pháo bờ biển của Hegemon, và Lữ đoàn Cơ giới 7 lăn bánh lên bờ, mở mặt trận đầu tiên sau hai năm. '
      'Đại tá Trần Khải chỉ có một mệnh lệnh: rời bãi biển, tìm chỗ đứng chân, rồi chiếm pháo đài Ashfield trước khi địch kịp tỉnh. '
      'Sau những bức tường ấy là Bastion, một pháo đài biết đi đã cũ, nhưng vẫn thừa sức chặn một lữ đoàn biết chùn tay.'),
     ('The brigade lands at Bãi Đổ Bộ, sets up its first base in Greenvale and storms the Ashfield fortress, bringing down the Bastion.',
      'Lữ đoàn đổ bộ ở Bãi Đổ Bộ, dựng căn cứ đầu tiên ở Lũng Xanh rồi đánh chiếm pháo đài Ashfield, hạ gục Bastion.')),
    (2, 1, ('Black Gold', 'Vàng đen'), ['dunebreak', 'redrock'], 'varga',
     ('Every Hegemon engine runs on the oil of Dunebreak and Red Rock. Cut it, and the machines starve. '
      'The enemy knows it too: General Varga, the man who built the Behemoth, has come south in person to guard his fuel. '
      'Ahead lie the pipelines, the wells, the refinery, and whatever monster Varga has parked inside it.',
      'Mọi cỗ máy của Hegemon đều chạy bằng dầu của Dunebreak và Hẻm Đá Đỏ. Cắt nguồn dầu, lũ máy sẽ chết đói. '
      'Địch cũng biết điều đó: tướng Varga, cha đẻ của Behemoth, đích thân xuống phía nam giữ kho nhiên liệu. '
      'Phía trước là đường ống, giếng dầu, nhà máy lọc dầu, và con quái vật nào đó Varga đang giấu bên trong.'),
     ('Varga shows himself at Dunebreak; his Behemoth falls in a sandstorm, and the refinery burns with the Inferno inside it.',
      'Varga lộ mặt ở Dunebreak; Behemoth của hắn gục trong bão cát, còn nhà máy lọc dầu bốc cháy cùng Inferno bên trong.')),
    (3, 1, ('The Long Winter', 'Mùa đông dài'), ['frostpeak', 'whiteout'], 'orlov',
     ('Winter comes early to the highlands. Across Frostpeak and the Whiteout pass, Colonel Orlov has built a radar line that sees every convoy, and guns that answer within a minute. '
      'His Harpy, a gunship the size of a ship, hunts anything that moves on the snow. '
      'The brigade has anti-air now. It will need every launcher to break the line and reach Jötunn behind it.',
      'Mùa đông về sớm trên cao nguyên. Dọc Frostpeak và Đèo Bão Tuyết, đại tá Orlov dựng một tuyến radar thấy được mọi đoàn xe, cùng những khẩu pháo khai hỏa chưa tới một phút sau. '
      'Harpy của hắn, một pháo hạm bay to như con tàu, săn mọi thứ nhúc nhích trên tuyết. '
      'Lữ đoàn giờ đã có phòng không. Sẽ cần đến từng bệ phóng để phá tuyến radar và tới được Jötunn phía sau.'),
     ('The brigade blinds Orlov\'s radar line, brings Harpy down in the snow and breaks through at Frostpeak, past Jötunn.',
      'Lữ đoàn làm mù tuyến radar của Orlov, bắn rơi Harpy trên tuyết và chọc thủng Frostpeak, vượt qua Jötunn.')),
    (4, 2, ('Steel Harbour', 'Cảng thép'), ['ironport', 'rustyard', 'lighthousebay'], 'kessler',
     ('Everything Hegemon builds leaves through Ironport. Admiral Kessler runs its cranes, its rails and its armoured trains to a timetable nobody has ever seen broken. '
      'The Alliance goes over to the attack: take the Rust Yard, cut the rail lines, and seize the port itself. '
      'On the docks, Linh\'s intercepts keep mentioning one word: Tempest.',
      'Mọi thứ Hegemon chế tạo đều đi qua Ironport. Đô đốc Kessler điều hành cần cẩu, đường ray và những đoàn tàu bọc thép theo một thời gian biểu chưa ai thấy trễ bao giờ. '
      'Liên minh chuyển sang phản công: chiếm Bãi Sắt Gỉ, cắt đường ray, rồi đánh chiếm chính bến cảng. '
      'Trên cầu tàu, các bản chặn thu của Linh cứ nhắc mãi một cái tên: Tempest.'),
     ('Kessler\'s timetable breaks: Juggernaut is derailed, Gungnir silenced, and the port taken from Tempest on its own docks.',
      'Thời gian biểu của Kessler đổ vỡ: Juggernaut bị lật, Gungnir câm họng, bến cảng bị chiếm từ tay Tempest ngay trên cầu tàu.')),
    (5, 2, ('Jungle Fire', 'Lửa rừng'), ['emberridge', 'junglepass'], 'sen',
     ('Under the volcanoes of Ember Ridge and the canopy of the Jungle Pass, Dr Sen builds drones by the thousand. '
      'Her masterpiece, the Hive, can blacken the sky over a whole division; its mothership carries the swarm wherever Hegemon points it. '
      'Burn the drone works and the sky clears. But Linh has noticed something odd: Sen\'s own messages are getting shorter, and angrier.',
      'Dưới chân núi lửa Sườn Dung Nham và tán rừng Đèo Rừng Rậm, tiến sĩ Sen chế tạo drone theo từng nghìn chiếc. '
      'Kiệt tác của bà, Hive, có thể che đen bầu trời trên cả một sư đoàn; tàu mẹ của nó chở bầy drone tới bất cứ đâu Hegemon chỉ tay. '
      'Đốt xưởng drone thì bầu trời sẽ sạch. Nhưng Linh để ý một điều lạ: các bức điện của chính Sen cứ ngắn dần, và gay gắt dần.'),
     ('The Hive and its mothership fall over Ember Ridge. Dr Sen walks out of the burning drone works and gives herself up, with the Icarus files.',
      'Hive và tàu mẹ của nó rơi trên Sườn Dung Nham. Tiến sĩ Sen bước ra khỏi xưởng drone đang cháy và ra hàng, mang theo hồ sơ Icarus.')),
    (6, 2, ('Counterstrike', 'Tổng phản công'), ['hydrodam', 'whiteout', 'ashfield', 'landingbeach'], 'varga',
     ('Hegemon strikes back. Varga throws everything left at the ground the brigade took in the first act: Ashfield, the Whiteout pass, and the Hydro Dam that lights half the coast. '
      'Engineer Mai has done the impossible and got a captured Behemoth running for our side. '
      'Varga has done something worse: his new Behemoth, Moloch, is heading for the dam, and General Lý Hàn\'s relief army is days away.',
      'Hegemon phản đòn. Varga ném tất cả những gì còn lại vào những vùng đất lữ đoàn đã chiếm ở hồi đầu: Ashfield, Đèo Bão Tuyết, và Đập Thủy Điện thắp sáng nửa dải duyên hải. '
      'Kỹ sư Mai đã làm được điều không tưởng: cho một chiếc Behemoth bắt được chạy về phía ta. '
      'Varga làm được điều tệ hơn: Behemoth mới của hắn, Moloch, đang tiến về con đập, trong khi đạo quân cứu viện của tướng Lý Hàn còn cách nhiều ngày đường.'),
     ('The counterstrike breaks on the Hydro Dam: Moloch goes into the gorge and General Lý Hàn\'s army arrives in time.',
      'Đợt tổng phản công vỡ tan trước Đập Thủy Điện: Moloch lao xuống hẻm sông, và đạo quân của tướng Lý Hàn tới kịp.')),
    (7, 3, ('The Capital', 'Thủ đô'), ['metrocity', 'capital'], 'aurel',
     ('The road runs through Metro City to Lam Thành, the capital. General Lý Hàn brings his Northern Army to join the liberation, with a base of his own and his own plans for the city. '
      'Under the streets, Nemesis, Hegemon\'s missile train, is moving.',
      'Con đường chạy qua Thành Phố Metro tới Lam Thành, thủ đô. Tướng Lý Hàn kéo Tập đoàn quân Phương Bắc tới cùng giải phóng, với căn cứ riêng và những toan tính riêng cho thành phố. '
      'Dưới lòng phố, Nemesis, đoàn tàu tên lửa của Hegemon, đang lăn bánh.'),
     ('The capital is freed, but Lý Hàn turns on the brigade in the middle of the battle. His base falls; he escapes north to the mines.',
      'Thủ đô được giải phóng, nhưng Lý Hàn trở mặt với lữ đoàn ngay giữa trận. Căn cứ của hắn thất thủ; hắn trốn lên các khu mỏ phía bắc.')),
    (8, 3, ('Underground', 'Lòng đất'), ['openpit', 'redrock', 'hydrodam', 'dunebreak'], 'hung',
     ('Lý Hàn has run north to the open-pit mines where Hegemon digs the metal for its machines. He holds the pits with his own army and the diggers Aurel left behind. '
      'Somewhere in the deepest pit, Kronos is waking up.',
      'Lý Hàn đã chạy lên các mỏ lộ thiên phía bắc, nơi Hegemon đào kim loại cho những cỗ máy của nó. Hắn giữ các hố mỏ bằng quân riêng và những cỗ máy đào Aurel để lại. '
      'Đâu đó dưới hố sâu nhất, Kronos đang thức giấc.'),
     ('The brigade follows Lý Hàn into the mines; Tartarus and Ixion fall, and Kronos is buried in its own pit. Lý Hàn escapes again, to the sea.',
      'Lữ đoàn đuổi theo Lý Hàn vào khu mỏ; Tartarus và Ixion gục ngã, Kronos bị chôn vùi trong chính hố mỏ của nó. Lý Hàn lại trốn thoát, ra biển.')),
    (9, 3, ('Rough Seas', 'Biển động'), ['ironport', 'lighthousebay', 'landingbeach'], 'hung',
     ('Lý Hàn has found what is left of Kessler\'s fleet and made it his own. From the harbours of the coast he means to hold the sea, with Scylla back in service '
      'and a missile submarine, Typhon, somewhere under the waves. This is where he has to be stopped.',
      'Lý Hàn đã tìm thấy tàn quân hạm đội của Kessler và biến nó thành của mình. Từ các bến cảng dọc bờ biển, hắn định giữ lấy biển, với Scylla trở lại hoạt động '
      'và một tàu ngầm tên lửa, Typhon, ẩn đâu đó dưới sóng. Đây là nơi phải chặn hắn lại.'),
     ('Typhon goes down off the coast and Lý Hàn is taken on his own flagship. Act III ends; in his papers Linh finds two words: Project Icarus.',
      'Typhon chìm ngoài khơi và Lý Hàn bị bắt ngay trên soái hạm của hắn. Hồi III khép lại; trong giấy tờ của hắn, Linh tìm thấy hai chữ: Dự án Icarus.')),
    (10, 4, ('War in the Air', 'Chiến tranh trên không'), ['skyhold', 'frostpeak', 'whiteout'], 'quaden',
     ('Project Icarus is real: Aurel\'s orbital spacecraft, built to hang over the coast. Between the brigade and the sky stands Kasimir Wolff, call sign Raven, '
      'Hegemon\'s best pilot and Hawk\'s old wingman. Take Skyhold, the air base he flies from, and the sky belongs to the Alliance.',
      'Dự án Icarus có thật: phi thuyền quỹ đạo của Aurel, được chế tạo để treo trên bầu trời duyên hải. Giữa lữ đoàn và bầu trời là Kasimir Wolff, biệt danh Raven, '
      'phi công giỏi nhất của Hegemon và là đồng đội bay cũ của Diều Hâu. Chiếm Skyhold, căn cứ nơi hắn cất cánh, là bầu trời thuộc về Liên minh.'),
     ('Icarus shows itself and runs; Wolff is shot down, and Skyhold falls with Roc, his command airship.',
      'Icarus lộ diện rồi bỏ chạy; Wolff bị bắn rơi, Skyhold thất thủ cùng Roc, khí cầu chỉ huy của hắn.')),
    (11, 4, ('The Orbital Gate', 'Cửa ngõ quỹ đạo'), ['orbitalgate', 'frostpeak', 'rustyard', 'skyhold'], 'aurel',
     ('Before Icarus can fly, Aurel needs the orbital gate: the radar stations and side pads that guide his ships up and down. '
      'Orlov guards it with Gungnir, his last and biggest gun. Above it all waits Daedalus, the ship that brings Aurel\'s troops down from orbit.',
      'Trước khi Icarus cất cánh, Aurel cần cửa ngõ quỹ đạo: các trạm radar và bệ phóng phụ dẫn đường cho tàu của hắn lên xuống. '
      'Orlov canh giữ nó bằng Gungnir, khẩu pháo cuối cùng và lớn nhất của hắn. Phía trên tất cả là Daedalus, con tàu đưa quân của Aurel từ quỹ đạo xuống.'),
     ('Orlov\'s Gungnir is silenced and Daedalus falls on the gate it guarded. Only the launch site is left.',
      'Gungnir của Orlov câm họng và Daedalus rơi xuống chính cửa ngõ nó canh giữ. Chỉ còn lại bãi phóng.')),
    (12, 4, ('The Launch Site', 'Bãi phóng'), ['launchsite', 'dunebreak'], 'aurel',
     ('Everything Hegemon has left is at the launch site in the southern desert: Varga and Kessler for one last fight, Sen\'s drones in Aurel\'s hands, and Icarus itself on its pad. '
      'At the end of the road Aurel waits, ready to go to orbit and leave the war behind.',
      'Tất cả những gì Hegemon còn lại đều dồn về bãi phóng giữa sa mạc phía nam: Varga và Kessler cho trận cuối, bầy drone của Sen giờ trong tay Aurel, và chính Icarus trên bệ phóng. '
      'Ở cuối con đường, Aurel đang chờ, sẵn sàng bay lên quỹ đạo và bỏ lại cuộc chiến phía sau.'),
     ('Icarus turns back from orbit and crashes in the desert. Hegemon is finished, and the Lam Hai coast is free.',
      'Icarus quay lại từ quỹ đạo và rơi xuống sa mạc. Hegemon sụp đổ, dải duyên hải Lam Hải được tự do.')),
]

for n, act, title, maps, general, card, done in CHAPTERS:
    # Prompt 20: chapters 7-12 (and chapter 4's opening, for Tempest) are new words; 1-6 keep CampaignText's.
    T(f'chapter.{n}.title', *title, fresh=n >= 7)
    T(f'chapter.{n}.summary', *card, fresh=n >= 7)
    T(f'timeline.{n}', *done, fresh=n >= 7)

T('chapter.4.summary',
  'Everything Hegemon builds leaves through Ironport. Admiral Kessler runs its cranes, its rails and its armoured trains to a timetable nobody has ever seen broken. '
  'The Alliance goes over to the attack: take the Rust Yard, cut the rail lines, and seize the port itself. '
  'On the docks, Linh\'s intercepts keep mentioning Tempest: one of Varga\'s Behemoths, waiting for Kessler\'s next ship.',
  'Mọi thứ Hegemon chế tạo đều đi qua Ironport. Đô đốc Kessler điều hành cần cẩu, đường ray và những đoàn tàu bọc thép theo một thời gian biểu chưa ai thấy trễ bao giờ. '
  'Liên minh chuyển sang phản công: chiếm Bãi Sắt Gỉ, cắt đường ray, rồi đánh chiếm chính bến cảng. '
  'Trên cầu tàu, các bản chặn thu của Linh cứ nhắc mãi tới Tempest: một chiếc Behemoth của Varga đang chờ chuyến tàu tiếp theo của Kessler.', fresh=True)

# Prompt 20 A-B: each chapter's boss slots, the main boss and its mini bosses (a slot is the boss's id; one
# pass 2 has not built yet is fought as the stand-in its missions name as "fallback").
CHAPTER_BOSSES = {
    1: ('fortress_bastion', ['bastion_mk0']),
    2: ('behemoth', ['behemoth_inferno']),
    3: ('mobile_fortress', ['mega_gunship', 'fenrir']),
    4: ('leviathan', ['behemoth_tempest', 'armored_train', 'scylla']),
    5: ('drone_mothership', ['locust', 'fortress_hive']),
    6: ('moloch', ['landing_hovercraft', 'behemoth_mk2']),
    7: ('nuke_train', ['supreme_command']),
    8: ('kronos', ['ixion', 'earth_borer']),
    9: ('typhon', ['caspian', 'scylla']),
    10: ('command_airship', ['sky_fortress', 'icarus_mk0', 'argus']),
    11: ('daedalus', ['rail_supergun', 'locust']),
    12: ('silver_bug', ['behemoth_mk2', 'behemoth_tempest', 'locust']),
}

# Prompt 20 B.3: where the missions of the nine-chapter campaign went (a save's stars follow the same map).
MOVES = {}
for _n in range(1, 11):
    MOVES[f'c7m{_n:02d}'] = f'c10m{_n:02d}'
    MOVES[f'c8m{_n:02d}'] = f'c7m{_n:02d}'
    MOVES[f'c9m{_n:02d}'] = f'c12m{_n:02d}'
for _s in (1, 2):
    MOVES[f'c7s{_s}'] = f'c10s{_s}'
    MOVES[f'c8s{_s}'] = f'c7s{_s}'
    MOVES[f'c9s{_s}'] = f'c12s{_s}'
MOVES.update({'c1m05': 'c6m08', 'c6m08': 'c8m05', 'c4m06': 'c11m05', 'c3m08': 'c6m05', 'c3s2': 'c3m08',
              'c6m05': 'c10m08', 'c7m08': 'c11m08'})
# The old chapters' opening cards seen (and 10, the old epilogue's mark, now 100).
CHAPTERS_SEEN = {7: 10, 8: 7, 9: 12, 10: 100}
# The HQ levels the nine-chapter campaign opened, by its old mission ids (a save keeps the level it had).
OLD_HQ = {'c1m04': 1, 'c3m05': 2, 'c5m05': 3, 'c7m05': 4, 'c9m03': 5}

T('timeline.0', 'Two years ago: the Night of Steel. Hegemon seizes the Lam Hai coast; Director Aurel declares the "Protectorate".',
  'Hai năm trước: Đêm Thép. Hegemon chiếm dải duyên hải Lam Hải; giám đốc Aurel tuyên bố thành lập "Chính quyền Bảo hộ".')

T('campaign.epilogue.title', 'Epilogue: Clear Sky', 'Vĩ thanh: Bầu trời trong')
T('campaign.epilogue',
  'The wreck of Icarus burned on its pad for three days. Aurel was found in the command bunker beneath it, still giving orders to a network that no longer answered. '
  'Colonel Khải sent the brigade home in stages, the way it had come. Engineer Mai kept one Behemoth, "for the museum", and nobody believed her. '
  'Diều Hâu flies the coast every morning now, and the sky stays empty. The Operations room stays open, for whoever wants to fight the great battles again, at the hardest tier.',
  'Xác Icarus cháy trên bệ phóng suốt ba ngày. Người ta tìm thấy Aurel trong hầm chỉ huy bên dưới, vẫn đang ra lệnh cho một mạng lưới không còn ai trả lời. '
  'Đại tá Khải cho lữ đoàn về từng đợt, như lúc đã đến. Kỹ sư Mai giữ lại một chiếc Behemoth, "để cho bảo tàng", mà chẳng ai tin cả. '
  'Giờ sáng nào Diều Hâu cũng bay dọc bờ biển, và bầu trời vẫn trống trơn. Phòng Chiến dịch vẫn mở cửa, cho ai muốn đánh lại những trận lớn, ở cấp độ khó nhất.')

# ------------------------------------------------------------------------------------------ the people

# id, name, role, bio; side: ours / hegemon
CHARACTERS = [
    ('khai', 'ours', ('Colonel Trần Khải', 'Đại tá Trần Khải'), ('Commander, 7th Mechanised Brigade', 'Chỉ huy Lữ đoàn Cơ giới 7'),
     ('Fifty-two, calm, practical, never heard to raise his voice on the radio. Khải lost his home town on the Night of Steel and does not talk about it. '
      'He plans battles like a mechanic fixes an engine: find what is broken, fix that, move on.',
      'Năm mươi hai tuổi, điềm tĩnh, thực tế, chưa ai nghe ông lớn tiếng trên sóng bộ đàm. Khải mất quê nhà trong Đêm Thép và không bao giờ nhắc tới. '
      'Ông lên kế hoạch trận đánh như thợ máy sửa động cơ: tìm chỗ hỏng, sửa chỗ đó, rồi đi tiếp.')),
    ('mai', 'ours', ('Engineer Mai', 'Kỹ sư Mai'), ('Chief engineer; runs the base', 'Kỹ sư trưởng, phụ trách căn cứ'),
     ('Mai keeps the brigade\'s base running and signs off every HQ upgrade. For three years she welded Behemoth hulls for Hegemon as a contract engineer, until she understood what they were for and walked out. '
      'She knows every weak seam in Varga\'s machines, and she has not forgiven herself for any of them.',
      'Mai giữ cho căn cứ của lữ đoàn vận hành và là người ký duyệt mọi lần nâng cấp sở chỉ huy. Suốt ba năm, cô hàn vỏ Behemoth cho Hegemon theo hợp đồng, cho đến khi hiểu chúng được làm ra để làm gì và bỏ đi. '
      'Cô biết từng đường hàn yếu trên những cỗ máy của Varga, và chưa tha thứ cho mình vì bất cứ đường nào.')),
    ('dieuhau', 'ours', ('Diều Hâu', 'Diều Hâu'), ('Pilot; leads the air wing', 'Phi công, chỉ huy phi đội'),
     ('Captain Lê Phong, call sign Diều Hâu (Hawk), flies everything the brigade owns that leaves the ground. Loud, cheerful, better than he admits. '
      'He trained at the same school as Quạ Đen, and they were wingmen, once.',
      'Đại úy Lê Phong, tên gọi Diều Hâu, lái mọi thứ biết cất cánh của lữ đoàn. Ồn ào, vui tính, và giỏi hơn những gì anh chịu nhận. '
      'Anh học cùng trường bay với Quạ Đen, và đã từng là đồng đội bay kèm của hắn.')),
    ('linh', 'ours', ('Lieutenant Linh', 'Trung úy Linh'), ('Intelligence officer', 'Sĩ quan tình báo'),
     ('Linh reads Hegemon\'s mail. Intercepts, captured drives, a burnt notebook: she turns them into targets, and into the side jobs nobody else has time for. '
      'Precise, patient, and the only one who can make Colonel Khải laugh.',
      'Linh đọc thư của Hegemon. Bản chặn thu, ổ cứng thu được, một cuốn sổ cháy dở: cô biến tất cả thành mục tiêu, và thành những nhiệm vụ phụ không ai có thời gian làm. '
      'Chính xác, kiên nhẫn, và là người duy nhất làm được đại tá Khải bật cười.')),
    ('hung', 'ours', ('General Lý Hàn', 'Tướng Lý Hàn'), ('Commander, Alliance Northern Army', 'Tư lệnh Tập đoàn quân Phương Bắc của Liên minh'),
     ('Lý Hàn commands the Alliance\'s largest army and never lets anyone forget it. Brave, generous with his men, hungry for the one thing a liberator can take: the city he frees. '
      'He fights beside the brigade in the great operations, with a base of his own.',
      'Lý Hàn chỉ huy đạo quân lớn nhất của Liên minh và không bao giờ để ai quên điều đó. Dũng cảm, hào phóng với lính của mình, và thèm khát đúng một thứ mà người giải phóng có thể lấy: thành phố ông giải phóng. '
      'Ông sát cánh cùng lữ đoàn trong các chiến dịch lớn, với căn cứ riêng.')),
    ('brandt', 'hegemon', ('Major Brandt', 'Thiếu tá Brandt'), ('Hegemon coastal garrison · boss names: fortresses', 'Đồn trú duyên hải của Hegemon · tên boss: pháo đài'),
     ('Brandt commands the garrison that was meant to keep the Alliance off the beach. A careful officer who trusts concrete more than men, '
      'he names his fortresses as if they were old friends: Bastion first of all.',
      'Brandt chỉ huy đạo quân đồn trú có nhiệm vụ chặn Liên minh ngoài bãi biển. Một sĩ quan cẩn trọng, tin bê tông hơn tin người, '
      'hắn đặt tên cho các pháo đài như gọi bạn cũ: trước hết là Bastion.')),
    ('varga', 'hegemon', ('General Varga', 'Tướng Varga'), ('Hegemon armour; father of the Behemoth', 'Thiết giáp Hegemon; cha đẻ của Behemoth'),
     ('Varga believes weight wins wars. He designed the Behemoth on a napkin and spent a nation\'s budget building it. '
      'Brave, stubborn, loyal to his machines more than to Aurel. His armies are all tanks and tank killers; his bases bristle with anti-tank guns.',
      'Varga tin rằng sức nặng thắng được chiến tranh. Hắn vẽ Behemoth trên một tờ giấy ăn rồi tiêu ngân sách của cả một quốc gia để chế tạo nó. '
      'Gan lì, cứng đầu, trung thành với những cỗ máy của mình hơn là với Aurel. Quân của hắn toàn xe tăng và xe diệt tăng; căn cứ của hắn dựng đầy pháo chống tăng.')),
    ('orlov', 'hegemon', ('Colonel Orlov', 'Đại tá Orlov'), ('Hegemon artillery', 'Pháo binh Hegemon'),
     ('Orlov has never seen the face of a man he killed, and prefers it that way. He fights from thirty kilometres off, with radar, rockets and patience. '
      'His bases are gun lines; his armies screen his batteries and wait for the shells to do the work.',
      'Orlov chưa từng nhìn mặt người nào hắn giết, và hắn muốn thế. Hắn đánh từ cách xa ba mươi cây số, bằng radar, rocket và sự kiên nhẫn. '
      'Căn cứ của hắn là những trận địa pháo; quân của hắn che chắn cho các khẩu đội và chờ đạn pháo làm nốt phần việc.')),
    ('kessler', 'hegemon', ('Admiral Kessler', 'Đô đốc Kessler'), ('Hegemon logistics, ports and trains', 'Hậu cần, bến cảng và đường sắt của Hegemon'),
     ('Kessler has never lost a shipment, a train or an argument about a timetable. He runs Hegemon\'s ports and rail lines, and armours both. '
      'His armies are balanced to the gram, his bases a little of everything, and he mines anything he cannot hold.',
      'Kessler chưa từng để thất lạc một chuyến hàng, một đoàn tàu hay thua một cuộc cãi về thời gian biểu. Hắn điều hành bến cảng và đường sắt của Hegemon, và bọc thép cả hai. '
      'Quân của hắn cân bằng đến từng gam, căn cứ của hắn thứ gì cũng có một ít, và hắn rải mìn bất cứ chỗ nào không giữ nổi.')),
    ('sen', 'hegemon', ('Dr Sen', 'Tiến sĩ Sen'), ('Hegemon drones; creator of the Hive', 'Drone của Hegemon; người tạo ra Hive'),
     ('Sen builds swarms the way other people knit. The Hive was meant to be a rescue system for disaster zones; Hegemon armed it before she finished her coffee. '
      'She fights with drones, jammers and hangars full of both, and she has begun to wonder who she is working for.',
      'Sen tạo ra bầy drone như người khác đan len. Hive vốn được thiết kế làm hệ thống cứu hộ cho vùng thảm họa; Hegemon vũ trang cho nó trước khi bà kịp uống xong ly cà phê. '
      'Bà đánh bằng drone, xe gây nhiễu và những nhà chứa đầy cả hai thứ, và bà bắt đầu tự hỏi mình đang làm việc cho ai.')),
    ('quaden', 'hegemon', ('Quạ Đen', 'Quạ Đen'), ('Hegemon air force ace', 'Át chủ bài không quân Hegemon'),
     ('Nobody uses his real name. Raven commands Hegemon\'s air wing from Skyhold and has more kills than the rest of it together. '
      'He flies gunships, jets and drones in one screaming wave, and his bases are ringed with missiles. He and Diều Hâu have unfinished business.',
      'Không ai gọi tên thật của hắn. Quạ Đen chỉ huy lực lượng không quân Hegemon từ Skyhold và có số lần hạ địch nhiều hơn cả phần còn lại cộng lại. '
      'Hắn tung trực thăng, phản lực và drone thành một đợt gào thét, và căn cứ của hắn vây kín tên lửa. Giữa hắn và Diều Hâu còn một món nợ chưa trả.')),
    ('aurel', 'hegemon', ('Director Aurel', 'Giám đốc Aurel'), ('Head of Hegemon; Project Icarus', 'Người đứng đầu Hegemon; Dự án Icarus'),
     ('Aurel talks about war the way accountants talk about quarterly results. He took the coast because the contract allowed it, and he built Icarus because nobody could stop him. '
      'He commands the best of everything, and he plans to never be in range of any of it.',
      'Aurel nói về chiến tranh như kế toán nói về báo cáo quý. Hắn chiếm dải duyên hải vì hợp đồng cho phép, và chế tạo Icarus vì chẳng ai ngăn nổi. '
      'Hắn chỉ huy những thứ tốt nhất của mọi loại, và định sẽ không bao giờ đứng trong tầm bắn của thứ nào.')),
]

for cid, side, name, role, bio in CHARACTERS:
    T(f'char.{cid}.name', *name)
    T(f'char.{cid}.role', *role)
    T(f'char.{cid}.bio', *bio)

T('char.hq.name', 'Brigade HQ', 'Sở chỉ huy Lữ đoàn')
T('char.hq.role', 'Radio', 'Bộ đàm')

# The generals as the AI plays them: signature deck, fire support habits, base style, and their lines.
GENERALS = [
    ('varga', ['light_tank', 'main_battle_tank', 'heavy_tank', 'tank_destroyer', 'ifv', 'flame_tank', 'twin_tank', 'fpv_carrier'],
     ['artillery_barrage', 'airstrike', 'smoke_screen'], 'varga', 'Attack',
     [('Steel does not negotiate, Colonel.', 'Thép không biết thương lượng, đại tá ạ.'),
      ('Every tank you burn, I build two.', 'Ngươi đốt một chiếc, ta đóng hai chiếc.'),
      ('Come closer. My guns are lonely.', 'Lại gần đây. Pháo của ta đang buồn lắm.')],
     ('Retreat. Save the machines. The men can walk.', 'Rút. Giữ lấy máy móc. Người thì đi bộ cũng được.')),
    ('orlov', ['mlrs', 'artillery', 'mortar_carrier', 'heavy_rocket_artillery', 'sam_launcher', 'main_battle_tank', 'aa_vehicle', 'counter_battery_radar'],
     ['artillery_barrage', 'cruise_missile', 'uav_scan'], 'orlov', 'Defend',
     [('You are a coordinate, nothing more.', 'Ngươi chỉ là một tọa độ, không hơn.'),
      ('Fire mission. Grid one-seven. All batteries.', 'Nhiệm vụ bắn. Ô lưới một-bảy. Toàn bộ khẩu đội.'),
      ('Patience, Colonel. The snow is on my side.', 'Kiên nhẫn đi, đại tá. Tuyết đứng về phía ta.')],
     ('Recalculating. Withdraw the batteries to the next line.', 'Tính lại. Rút các khẩu đội về tuyến sau.')),
    ('kessler', ['wheeled_gun', 'ifv', 'main_battle_tank', 'heavy_tank', 'sam_launcher', 'fpv_carrier', 'mine_layer', 'mlrs'],
     ['remote_mines', 'artillery_barrage', 'smoke_screen'], 'kessler', 'Defend',
     [('You are four minutes behind schedule, Colonel.', 'Ngươi đang trễ bốn phút so với lịch, đại tá.'),
      ('Every road here is mined. I checked.', 'Mọi con đường ở đây đều có mìn. Ta đã kiểm tra rồi.'),
      ('The next train leaves on time. With or without you under it.', 'Chuyến tàu sau sẽ chạy đúng giờ. Dù có ngươi nằm dưới bánh hay không.')],
     ('Cancel the timetable. Evacuate the port by sea.', 'Hủy lịch trình. Sơ tán bến cảng bằng đường biển.')),
    ('sen', ['strike_drone', 'fpv_carrier', 'lancet_truck', 'recon_drone', 'ew_jammer', 'ifv', 'main_battle_tank', 'aa_vehicle'],
     ['uav_scan', 'sead_strike', 'repair_drop'], 'sen', 'Attack',
     [('The swarm does not hate you. It does not anything.', 'Bầy drone không ghét các anh. Nó chẳng có cảm xúc gì cả.'),
      ('Seven hundred drones in the air. Count them if you like.', 'Bảy trăm drone đang trên trời. Các anh cứ đếm nếu thích.'),
      ('I designed this to save people. Remember that when it kills you.', 'Tôi thiết kế thứ này để cứu người. Hãy nhớ điều đó khi nó giết các anh.')],
     ('Enough. Stand the swarm down.', 'Đủ rồi. Cho bầy drone hạ cánh.')),
    ('quaden', ['attack_helicopter', 'gunship_heli', 'attack_jet', 'fighter_jet', 'strike_drone', 'aa_vehicle', 'main_battle_tank', 'sam_launcher'],
     ['airstrike', 'sead_strike', 'napalm_strike'], 'quaden', 'Attack',
     [('Diều Hâu! Still flying that museum piece?', 'Diều Hâu! Vẫn lái cái đồ cổ đó à?'),
      ('Look up, Colonel. That is where you lose.', 'Nhìn lên đi, đại tá. Ông sẽ thua ở trên đó.'),
      ('The sky is mine. You can keep the mud.', 'Bầu trời là của ta. Bùn đất thì cứ giữ lấy.')],
     ('Eject, eject! ...Not like this.', 'Nhảy dù, nhảy dù! ...Không phải thế này chứ.')),
    ('hung', ['main_battle_tank', 'heavy_tank', 'titan_tank', 'bmpt', 'ifv', 'aa_vehicle', 'mlrs', 'tank_destroyer'],
     ['artillery_barrage', 'airstrike', 'cruise_missile'], 'aurel', 'Attack',
     [('I liberated this country once. I can take it back from you.', 'Ta đã giải phóng đất nước này một lần. Ta lấy lại nó từ tay các người được.'),
      ('Titans do not kneel, Colonel.', 'Titan không biết quỳ, đại tá ạ.'),
      ('Aurel paid well. You only ever gave orders.', 'Aurel trả hậu hĩnh. Còn các người chỉ biết ra lệnh.')],
     ('Enough. Tell Khải... tell him I surrender.', 'Đủ rồi. Nói với Khải... nói rằng ta đầu hàng.')),
    ('aurel', ['heavy_tank', 'bmpt', 'railgun_truck', 'attack_helicopter', 'long_sam', 'heavy_rocket_artillery', 'titan_tank', 'fighter_jet'],
     ['cruise_missile', 'airstrike', 'napalm_strike', 'sead_strike'], 'aurel', 'Attack',
     [('Your brigade is a rounding error on my balance sheet.', 'Lữ đoàn của ông chỉ là sai số làm tròn trên bảng cân đối của tôi.'),
      ('Everyone has a price, Colonel. General Lý Hàn had his.', 'Ai cũng có giá, đại tá. Tướng Lý Hàn cũng có giá của ông ta.'),
      ('Icarus is not a weapon. It is a contract nobody can refuse.', 'Icarus không phải vũ khí. Nó là một bản hợp đồng không ai từ chối nổi.')],
     ('This was not in the forecast.', 'Chuyện này không có trong dự báo.')),
]

for gid, deck, supports, style, stance, taunts, defeat in GENERALS:
    for i, (en, vi) in enumerate(taunts):
        T(f'radio.{gid}.taunt.{i + 1}', en, vi)
    T(f'radio.{gid}.defeat', *defeat)

# ------------------------------------------------------------------------------------------ the boss files

# key, name, file text
BOSS_FILES = [
    ('fortress_bastion', ('Bastion', 'Bastion'),
     ('Hegemon\'s first walking fortress: four autocannon turrets, a heavy mortar and a crew that patches it under fire. The one at Ashfield is an early model, slower and thinner than the ones that came after.',
      'Pháo đài biết đi đầu tiên của Hegemon: bốn tháp pháo tự động, một khẩu cối hạng nặng và kíp lái biết tự vá giáp dưới làn đạn. Chiếc ở Ashfield là mẫu đời đầu, chậm hơn và mỏng hơn những chiếc về sau.')),
    ('hovercraft', ('Charybdis', 'Charybdis'),
     ('A Hegemon assault hovercraft that carries a company of armour up the beach at sixty knots and covers the landing with its own guns. Hit it before it unloads.',
      'Tàu đệm khí đổ bộ của Hegemon, chở cả một đại đội thiết giáp lên bãi biển với tốc độ sáu mươi hải lý và tự yểm trợ cuộc đổ bộ bằng pháo của mình. Phải đánh nó trước khi nó kịp dỡ quân.')),
    ('behemoth', ('Behemoth', 'Behemoth'),
     ('Varga\'s land battleship: a main gun that kills a tank a shot, escorts that follow it into battle and a hull that shrugs off most of what the brigade fires. Mai says the rear plates are its weakness.',
      'Chiến hạm mặt đất của Varga: pháo chính mỗi phát hạ một xe tăng, đội hộ tống bám theo vào trận và lớp vỏ chịu được gần hết hỏa lực của lữ đoàn. Mai nói các tấm giáp phía sau là điểm yếu của nó.')),
    ('behemoth_inferno', ('Inferno', 'Inferno'),
     ('A Behemoth rebuilt round two flame projectors and a thermobaric rocket box. It sets the ground itself on fire. Stay out of its reach and keep hitting it.',
      'Một chiếc Behemoth dựng lại quanh hai súng phun lửa lớn và một hộp rocket nhiệt áp. Nó đốt cháy cả mặt đất. Tránh xa tầm với của nó và cứ thế mà nện.')),
    ('mega_gunship', ('Harpy', 'Harpy'),
     ('Orlov\'s gunship, as big as a ship and as slow: rocket pods, flares and an escort of helicopters. Only anti-air and fighters reach it. Bring every launcher you have.',
      'Pháo hạm bay của Orlov, to như con tàu và chậm như vậy: ổ rocket, pháo sáng mồi bẫy và một tốp trực thăng hộ tống. Chỉ phòng không và tiêm kích với tới nó. Mang theo mọi bệ phóng có được.')),
    ('frozen_behemoth', ('Behemoth Mk.II', 'Behemoth Mk.II'),
     ('The Behemoth from Dunebreak, dragged north, repaired and heated for the winter. Heavier than before, and angrier.',
      'Chiếc Behemoth ở Dunebreak, bị kéo lên phía bắc, sửa lại và lắp hệ sưởi cho mùa đông. Nặng hơn trước, và hung hãn hơn.')),
    ('mobile_fortress', ('Jötunn', 'Jötunn'),
     ('The anchor of Orlov\'s Frostpeak line: a mobile fortress with a howitzer, an escort and an EMP that stuns everything round it.',
      'Mỏ neo của tuyến Frostpeak: một pháo đài di động với lựu pháo, đội hộ tống và xung EMP làm tê liệt mọi thứ xung quanh.')),
    ('armored_train', ('Juggernaut', 'Juggernaut'),
     ('Kessler\'s armoured train: artillery wagons and armour that runs on time. It smokes itself when hit and patches itself on the move. Stop it before it reaches the docks.',
      'Đoàn tàu bọc thép của Kessler: toa pháo và toa giáp chạy đúng giờ. Bị bắn là nó tự thả khói, vừa chạy vừa tự vá. Phải chặn nó trước khi tới bến cảng.')),
    ('rail_supergun', ('Gungnir', 'Gungnir'),
     ('A gun too big for any road, pushed along the rails by two tractors. Kessler uses it to shell the port from forty kilometres off.',
      'Một khẩu pháo quá to cho mọi con đường, được hai đầu kéo đẩy dọc đường ray. Kessler dùng nó nã vào bến cảng từ cách bốn mươi cây số.')),
    ('behemoth_tempest', ('Tempest', 'Tempest'),
     ('A Behemoth built round a railgun that charges, glows and punches through everything in a line. Two coilguns and a shield. Spread out and close in.',
      'Một chiếc Behemoth dựng quanh khẩu súng điện từ: nạp điện, phát sáng rồi xuyên thủng mọi thứ trên một đường thẳng. Hai pháo điện từ và một tấm khiên. Dàn quân ra và áp sát.')),
    ('fortress_hive', ('The Hive', 'Hive'),
     ('Sen\'s drone fortress: no main gun, just racks that launch swarm after swarm, a SAM battery and flak. Deadly to aircraft; tanks and artillery break it.',
      'Pháo đài drone của Sen: không có pháo chính, chỉ có các giàn phóng hết bầy này tới bầy khác, một dàn tên lửa phòng không và pháo cao xạ. Cực nguy hiểm với máy bay; xe tăng và pháo binh mới hạ được nó.')),
    ('drone_mothership', ('Matriarch', 'Matriarch'),
     ('The Hive\'s flying carrier: it launches drones from its belly, fires flares and raises a shield when hurt. Only what shoots at the sky can finish it.',
      'Tàu sân bay biết bay của Hive: phóng drone từ bụng, bắn pháo sáng mồi bẫy và dựng khiên khi bị thương. Chỉ những gì bắn được lên trời mới kết liễu được nó.')),
    ('sky_fortress', ('Spectre', 'Bóng Ma Spectre'),
     ('A gunship that circles high over its prey with a 105 mm and two 40 mm guns down its side. It never comes low. Anti-air and fighters, or nothing.',
      'Pháo hạm bay vòng trên cao quanh con mồi với khẩu 105 mm và hai khẩu 40 mm dọc sườn. Nó không bao giờ hạ thấp. Hoặc phòng không và tiêm kích, hoặc chẳng gì cả.')),
    ('earth_borer', ('Tartarus', 'Tartarus'),
     ('Varga\'s tunnelling machine, Tartarus ("the earthworm"): it grinds under walls and dams and comes up where nobody is looking. Kill it before it reaches the power station.',
      'Cỗ máy khoan của Varga, tên là Tartarus: nó nghiến xuyên dưới tường thành và thân đập rồi trồi lên đúng chỗ không ai canh. Phải tiêu diệt nó trước khi nó tới trạm phát điện.')),
    ('frost_monster', ('Moloch', 'Moloch'),
     ('Varga\'s answer to losing the first Behemoth: a bigger one, armoured for the winter, with twice the escort. He calls it his masterpiece.',
      'Câu trả lời của Varga sau khi mất chiếc Behemoth đầu tiên: một chiếc lớn hơn, bọc giáp cho mùa đông, đội hộ tống gấp đôi. Hắn gọi nó là kiệt tác của đời mình.')),
    ('silver_bug', ('Icarus', 'Icarus'),
     ("Aurel's orbital warship: a dagger of a hull, a stepped superstructure under its command tower and a bank of engines across the stern, meant to strike from orbit and put Aurel beyond anyone's reach. The first one seen runs when it is hurt badly enough. The one on the launch pad is complete.",
      'Chiến hạm quỹ đạo của Aurel: thân tàu hình mũi dao, thượng tầng bậc thang dưới tháp chỉ huy và cả một dãy động cơ ở đuôi, được chế tạo để tấn công từ quỹ đạo và đưa Aurel ra ngoài tầm với của mọi người. Chiếc đầu tiên xuất hiện sẽ bỏ chạy khi bị thương đủ nặng. Chiếc trên bệ phóng đã hoàn chỉnh.')),
    ('silver_bug_complete', ('Icarus', 'Icarus'),
     ('Icarus 01, the first and only finished Icarus: a reactor that could keep it in orbit for a year, a main engine built to outrun anything that flies, and the warhead from Nemesis. It never reached orbit.',
      'Icarus 01, chiếc Icarus đầu tiên và duy nhất được hoàn thiện: lò phản ứng đủ sức giữ nó trên quỹ đạo suốt một năm, động cơ chính đủ sức bỏ xa mọi thứ biết bay, và đầu đạn lấy từ Nemesis. Nó chưa bao giờ tới được quỹ đạo.')),
    ('command_airship', ('Roc', 'Roc'),
     ('Quạ Đen\'s flying headquarters over Skyhold: radar, missiles and a hangar for drones. It directs every Hegemon aircraft on the coast.',
      'Sở chỉ huy bay của Quạ Đen trên Skyhold: radar, tên lửa và một khoang chứa drone. Nó điều khiển mọi máy bay Hegemon trên dải duyên hải.')),
    ('nuke_train', ('Nemesis', 'Nemesis'),
     ('A missile train crossing Metro City to its launch site. When it gets there, the countdown starts. Do not let it get there.',
      'Một đoàn tàu tên lửa đang băng qua Thành Phố Metro tới bãi phóng. Tới nơi là đếm ngược bắt đầu. Đừng để nó tới nơi.')),
    ('leviathan', ('Leviathan', 'Leviathan'),
     ('Kessler\'s flagship: the biggest battleship ever laid down, three triple 460 mm turrets, a pagoda tower over a forest of guns, launch cells by the funnel '
      'and a well deck for landing craft. Its sides stop tank shells; its deck does not. It never fights where it cannot leave.',
      'Soái hạm của Kessler: thiết giáp hạm lớn nhất từng được đóng, ba tháp pháo ba nòng 460 mm, tháp chỉ huy kiểu chùa trên cả một rừng súng, ống phóng cạnh ống khói '
      'và khoang chở tàu đổ bộ. Hông tàu chặn được đạn xe tăng; boong thì không. Nó không bao giờ đánh ở nơi nó không rút được.')),
    ('sea_corvette', ('Escort Corvette', 'Tàu hộ vệ'),
     ('Leviathan\'s escorts: a 76 mm gun and a CIWS that covers the flagship too. Sink them first and the flagship\'s sky opens.',
      'Tàu hộ vệ của Leviathan: pháo 76 mm và CIWS che chắn luôn cả tàu chính. Đánh chìm chúng trước thì bầu trời trên tàu chính mở ra.')),
    ('sea_cruiser', ('Missile Cruiser', 'Tuần dương hạm tên lửa'),
     ('Kessler\'s old flagship, the first Leviathan, now a missile cruiser in its fleet: two twin 203 mm turrets and two CIWS, keeping station between the battleship and the shore.',
      'Soái hạm cũ của Kessler, chiếc Leviathan đầu tiên, nay là tuần dương hạm tên lửa trong hạm đội: hai tháp pháo nòng đôi 203 mm và hai CIWS, giữ vị trí giữa thiết giáp hạm và bờ biển.')),
    ('missile_boat', ('Missile Boat', 'Xuồng tên lửa cao tốc'),
     ('Fast, thin boats that dash in to the pier heads with a salvo of rockets and are gone before the smoke clears.',
      'Những chiếc xuồng nhanh, vỏ mỏng, lao vào đầu cầu tàu bắn một loạt rốc-két rồi biến mất trước khi khói tan.')),
    ('landing_craft', ('Landing Craft', 'Tàu đổ bộ'),
     ('Leviathan\'s well deck carries three of them, each with two tanks for the beach.',
      'Khoang đổ bộ của Leviathan chở ba chiếc, mỗi chiếc hai xe tăng cho bãi biển.')),
    ('supreme_command', ('Atlas', 'Atlas'),
     ('Aurel\'s personal command vehicle, Atlas: the heaviest armour Hegemon ever built, around a communications suite that runs the whole launch site.',
      'Xe chỉ huy riêng của Aurel, Atlas: lớp giáp nặng nhất Hegemon từng đúc, bao quanh hệ thống liên lạc điều hành toàn bộ bãi phóng.')),
]

# Prompt 20: the boss slots pass 2 builds (fought as stand-ins until then). Short, in the tables, for prompt 22.
BOSS_FILES += [
    ('landing_hovercraft', ('Charybdis · Landing hovercraft', 'Charybdis · Tàu đệm khí đổ bộ'),
     ('A Hegemon assault hovercraft that carries a company of armour up the beach at sixty knots and covers the landing with its own guns. Hit it before it unloads.',
      'Tàu đệm khí đổ bộ của Hegemon, chở cả một đại đội thiết giáp lên bãi biển với tốc độ sáu mươi hải lý và tự yểm trợ cuộc đổ bộ bằng pháo của mình. Phải đánh nó trước khi nó kịp dỡ quân.')),
    ('bastion_mk0', ('Bastion Mk.0 · Prototype fortress', 'Bastion Mk.0 · Pháo đài nguyên mẫu'),
     ('Brandt\'s first walking fortress, a prototype of the Bastion: fewer guns, thinner plates, the same stubborn crew.',
      'Pháo đài biết đi đầu tiên của Brandt, bản nguyên mẫu của Bastion: ít pháo hơn, giáp mỏng hơn, vẫn kíp lái lì lợm ấy.')),
    ('fenrir', ('Fenrir · Vanguard', 'Fenrir · Xe tiên phong'),
     ('Orlov\'s winter vanguard: a heavy hunter that runs ahead of his gun lines through the snow and marks targets for them.',
      'Xe tiên phong mùa đông của Orlov: một thợ săn hạng nặng chạy trước các trận địa pháo qua tuyết và đánh dấu mục tiêu cho chúng.')),
    ('scylla', ('Scylla · Destroyer', 'Scylla · Tàu khu trục'),
     ('Kessler\'s command destroyer: fast, well armed, and always first into the harbour.',
      'Tàu khu trục chỉ huy của Kessler: nhanh, nhiều vũ khí, và luôn là chiếc đầu tiên vào cảng.')),
    ('locust', ('Locust · Drone carrier', 'Locust · Tàu con drone'),
     ('A small carrier from Sen\'s drone programme. Aurel kept building them after she left.',
      'Một tàu mang drone cỡ nhỏ trong chương trình drone của Sen. Aurel vẫn cho đóng tiếp sau khi bà bỏ đi.')),
    ('behemoth_mk2', ('Behemoth Mk.II · Upgraded Behemoth', 'Behemoth Mk.II · Behemoth nâng cấp'),
     ('Varga\'s Behemoth rebuilt after its first defeat: heavier, heated for the winter, and angrier.',
      'Chiếc Behemoth của Varga dựng lại sau lần bại trận đầu tiên: nặng hơn, lắp hệ sưởi cho mùa đông, và hung hãn hơn.')),
    ('moloch', ('Moloch · Mobile factory', 'Moloch · Nhà máy di động'),
     ('Varga\'s mobile factory: it builds tanks as it rolls and sends them out of its doors into battle.',
      'Nhà máy di động của Varga: vừa lăn bánh vừa đóng xe tăng, rồi tung chúng ra trận qua các cửa thả.')),
    ('kronos', ('Kronos · Mining excavator', 'Kronos · Máy xúc mỏ'),
     ('A bucket-wheel excavator the size of a building, armoured by Lý Hàn and pointed at the brigade.',
      'Một máy xúc bánh gầu to bằng cả tòa nhà, được Lý Hàn bọc thép và chĩa thẳng vào lữ đoàn.')),
    ('ixion', ('Ixion · Giant wheeled vehicle', 'Ixion · Xe bánh khổng lồ'),
     ('A war machine on two spiked wheels taller than a house, a roller of spikes across its front, built from mine machinery to batter through walls.',
      'Một cỗ máy chiến tranh trên hai bánh gai cao hơn nhà, phía trước là trục lăn đầy gai, đóng từ máy móc hầm mỏ để phá tường.')),
    ('typhon', ('Typhon · Missile submarine', 'Typhon · Tàu ngầm tên lửa'),
     ('Kessler\'s missile submarine, now Lý Hàn\'s: it surfaces, fires a salvo and dives again.',
      'Tàu ngầm tên lửa của Kessler, giờ trong tay Lý Hàn: nổi lên, phóng một loạt rồi lại lặn.')),
    ('caspian', ('Caspian · Ekranoplan', 'Caspian · Ekranoplan'),
     ('A ground-effect ship that skims the waves at the speed of an aircraft and lands troops on any beach.',
      'Một con tàu bay sát mặt sóng với tốc độ của máy bay và đổ quân lên bất cứ bãi biển nào.')),
    ('argus', ('Argus · Recon airship', 'Argus · Khí cầu trinh sát'),
     ('Wolff\'s armoured recon airship: it sees everything and tells his jets where to go.',
      'Khí cầu trinh sát bọc giáp của Wolff: thấy hết mọi thứ và chỉ đường cho máy bay của hắn.')),
    ('icarus_mk0', ('Icarus Mk.0 · Prototype spacecraft', 'Icarus Mk.0 · Phi thuyền nguyên mẫu'),
     ('The unfinished first Icarus, flown over Skyhold as a field test. Hurt it badly enough and it runs.',
      'Chiếc Icarus đầu tiên chưa hoàn thiện, bay trên Skyhold như một cuộc thử nghiệm thực địa. Đánh nó đủ đau, nó sẽ bỏ chạy.')),
    ('daedalus', ('Daedalus · Orbital lander', 'Daedalus · Tàu đổ bộ quỹ đạo'),
     ('The ship that brings Aurel\'s troops down from orbit, pod by pod, onto the orbital gate.',
      'Con tàu đưa quân của Aurel từ quỹ đạo xuống cửa ngõ quỹ đạo, từng khoang một.')),
]

for key, name, text in BOSS_FILES:
    T(f'boss.{key}', *name)
    T(f'bossfile.{key}', *text)

# ------------------------------------------------------------------------------------------ radio everyone can fall back on

GENERIC = {
    'capture': [('khai', 'Objective taken. Dig in.', 'Đã chiếm cứ điểm. Bám trụ.'),
                ('khai', 'Good. That one is ours now.', 'Tốt. Chỗ đó là của ta rồi.'),
                ('khai', 'Point secured. Keep moving.', 'Cứ điểm đã an toàn. Tiếp tục tiến.')],
    'lost': [('khai', 'We have lost a point. Take it back.', 'Ta mất một cứ điểm. Chiếm lại ngay.'),
             ('linh', 'Enemy flag on one of our objectives.', 'Cờ địch đã cắm trên một cứ điểm của ta.')],
    'boss': [('linh', 'Large contact. That is the boss: focus fire.', 'Mục tiêu cỡ lớn. Đó là trùm: tập trung hỏa lực.'),
             ('khai', 'There it is. Everything on it.', 'Nó đây rồi. Dồn hết vào nó.')],
    'bossHalf': [('khai', 'It is burning. Keep hitting it.', 'Nó đang cháy. Tiếp tục nện.'),
                 ('mai', 'Half its plates are gone. Aim for the seams!', 'Nửa lớp giáp của nó bay rồi. Nhắm vào đường hàn!')],
    'hqHalf': [('mai', 'HQ at half strength! I can\'t patch it that fast!', 'Sở chỉ huy còn một nửa! Tôi vá không kịp đâu!'),
               ('khai', 'They are on the HQ. Bring the army home.', 'Chúng đang đánh vào sở chỉ huy. Kéo quân về.')],
    'reinforce': [('linh', 'Enemy reinforcements dropping at their camp.', 'Viện binh địch đang nhảy dù xuống trại của chúng.'),
                  ('linh', 'More of them coming in by air.', 'Thêm quân địch đang được thả xuống.')],
    'win': [('khai', 'Well done, Brigade. Rest while you can.', 'Làm tốt lắm, Lữ đoàn. Nghỉ được lúc nào thì nghỉ.'),
            ('khai', 'That is how it is done.', 'Đánh là phải thế.')],
    'lose': [('khai', 'Pull back. We regroup and go again.', 'Rút về. Tập hợp lại rồi đánh tiếp.')],
    'stage': [('khai', 'Next objective. Move.', 'Mục tiêu tiếp theo. Di chuyển.')],
}

for trigger, lines in GENERIC.items():
    for i, (speaker, en, vi) in enumerate(lines):
        T(f'radio.{speaker}.gen.{trigger}.{i + 1}', en, vi)

# Lines the operations and the Sim send by key.
T('radio.betrayal', 'The allied commander has turned on us: their units are firing on ours!', 'Chỉ huy đồng minh đã trở mặt: quân của họ đang bắn vào ta!')
T('radio.bossFled', 'It is breaking off! Let it go, we have what we came for.', 'Nó đang tháo chạy! Để nó đi, ta đạt được mục tiêu rồi.')
T('radio.alliedStrikes', 'Hawk here: the air corridor is open. Strikes on call, every minute.', 'Hawk đây: hành lang bay đã mở. Không kích theo yêu cầu, mỗi phút một lượt.')
T('radio.enemyWeakened', 'Their supply is burning. They will feel that for the rest of the day.', 'Kho tiếp tế của chúng đang cháy. Cả ngày hôm nay chúng sẽ thấm đòn.')

# Speakers' names on the radio panel.
SPEAKERS = ['khai', 'mai', 'dieuhau', 'linh', 'hung', 'brandt', 'varga', 'orlov', 'kessler', 'sen', 'quaden', 'aurel', 'hq']

# ------------------------------------------------------------------------------------------ the campaign's screens

UI = {
    'campaign.dossier': ('Dossier', 'Hồ sơ'),
    'campaign.chapterKicker': ('{0} · Chapter {1}', '{0} · Chương {1}'),
    'campaign.missionKicker': ('Chapter {0} · Mission {1} · {2}', 'Chương {0} · Nhiệm vụ {1} · {2}'),
    'campaign.side': ('Side mission', 'Nhiệm vụ phụ'),
    'campaign.operation': ('Operation', 'Chiến dịch lớn'),
    'campaign.continue': ('Continue', 'Tiếp tục'),
    'campaign.deploy': ('Deploy', 'Xuất kích'),
    'campaign.back': ('Back', 'Quay lại'),
    'campaign.opponent': ('Opposing commander: {0}', 'Chỉ huy đối phương: {0}'),
    'campaign.noMap': ('Battlefield in the next update', 'Chiến trường có ở bản cập nhật tới'),
    'campaign.rewardFirst': ('Reward: {0} xu · {1} blueprints', 'Thưởng: {0} xu · {1} bản thiết kế'),
    'campaign.rewardReplay': ('Replay reward: {0} xu · {1} blueprints', 'Thưởng chơi lại: {0} xu · {1} bản thiết kế'),
    'campaign.hqLevel': ('Opens HQ level {0}', 'Mở cấp sở chỉ huy {0}'),
    'campaign.rareReward': ('{0} rare blueprints', '{0} bản thiết kế hiếm'),
    'campaign.gearReward': ('A tower piece: {0}', 'Một trang bị tháp: {0}'),
    'campaign.progressChapter': ('{0}/10', '{0}/10'),
    'campaign.epilogueGo': ('To the Operations room', 'Tới phòng Chiến dịch'),
    'campaign.sideAfter': ('Opens after mission {0}', 'Mở sau nhiệm vụ {0}'),
    # Prompt 20 C: an act switched off, and the last chapter switched on when it is not the last of the story.
    'campaign.comingSoon': ('Coming soon', 'Sắp ra mắt'),
    'campaign.comingSoonNote': ('This chapter comes in a later update.', 'Chương này sẽ có trong bản cập nhật sau.'),
    'campaign.tbc.title': ('To be continued', 'Còn tiếp'),
    'campaign.tbc': ('The war is not over. Hegemon still holds the rest of the coast, and the brigade is getting ready for what comes next. '
                     'The next chapters come in a later update; until then the Operations room is open.',
                     'Cuộc chiến chưa kết thúc. Hegemon vẫn giữ phần còn lại của dải duyên hải, và lữ đoàn đang chuẩn bị cho những gì sắp tới. '
                     'Các chương tiếp theo sẽ có trong bản cập nhật sau; từ giờ tới đó, phòng Chiến dịch vẫn mở cửa.'),
    'dossier.people': ('People', 'Nhân vật'),
    'dossier.bosses': ('Boss files', 'Hồ sơ trùm'),
    'dossier.timeline': ('Timeline', 'Dòng thời gian'),
    'dossier.files': ('Story files', 'Tư liệu'),
    'dossier.locked': ('Not met yet.', 'Chưa gặp mặt.'),
    'dossier.lockedBoss': ('Beat it to open its file.', 'Hạ gục nó để mở hồ sơ.'),
    'dossier.lockedChapter': ('Not yet written.', 'Chưa được viết nên.'),
    'dossier.before': ('Before the landing', 'Trước cuộc đổ bộ'),
    'dossier.chapterFiles': ('Chapter {0}', 'Chương {0}'),
    'dossier.empty': ('Every mission won adds a file here.', 'Mỗi nhiệm vụ giành thắng lợi sẽ thêm một tư liệu vào đây.'),
    'goal.outpost': ('Set up an outpost', 'Lập tiền đồn'),
    'goal.relieve': ('Break the siege', 'Giải vây'),
    'goal.evacuate': ('Evacuate', 'Sơ tán'),
    'goal.duel': ('Destroy the general\'s HQ', 'Phá sở chỉ huy của tướng địch'),
    'result.prints': ('Blueprints', 'Bản thiết kế'),
    'result.fragment': ('New in the dossier: {0}', 'Hồ sơ mới: {0}'),
    'result.hqLevel': ('HQ level {0} open', 'Đã mở cấp sở chỉ huy {0}'),
    'result.towerPiece': ('Tower piece', 'Trang bị tháp'),
    'camp.levelLocked': ('Opens in the campaign: mission {0}', 'Mở trong chiến dịch: nhiệm vụ {0}'),
    # The four battlefields built for the story (their names also come with the maps branch).
}
for key, (en, vi) in UI.items():
    T(key, en, vi)

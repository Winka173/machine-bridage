"""The story around the missions: who is who, the chapters and interludes, the boss files, the timeline and
the radio chatter every mission can fall back on. The missions themselves are in act1.py-act3.py, laid out
by act4.py (prompt 20) and act5.py-act8.py (prompt 22)."""

from campaign_kit import T

# ------------------------------------------------------------------------------------------ the campaign

# Prompt 22 C.1: the setting. Every proper name is the spec's (A), the same in both languages.
T('campaign.story.title', 'Machine Brigade: The Meridian Front', 'Machine Brigade: Mặt trận Meridian', fresh=True)
T('campaign.story.prologue',
  'The near future. The Meridian Coast is rich in oil and ore. When its government collapsed, a mining consortium hired Hegemon, '
  'the largest private military company in the world, to "keep things stable". Within two years Hegemon was an army of occupation, '
  'and the coast its weapons range. The free provinces formed the Meridian Accord. Its strongest force is the 7th Mechanized Brigade, '
  'the Machine Brigade: vehicles only, dropped where they are needed, fast. You are its field commander.',
  'Tương lai gần. Meridian Coast giàu dầu mỏ và khoáng sản. Khi chính quyền trong vùng sụp đổ, một tập đoàn khai khoáng thuê Hegemon, '
  'tập đoàn quân sự tư nhân lớn nhất thế giới, để "giữ ổn định". Chỉ trong hai năm, Hegemon thành đội quân chiếm đóng, và cả vùng thành bãi thử vũ khí của nó. '
  'Các tỉnh còn lại lập ra Meridian Accord. Lực lượng mạnh nhất của Accord là 7th Mechanized Brigade, Machine Brigade: '
  'chỉ có phương tiện, thả dù xuống đúng nơi cần, đánh bằng tốc độ. Bạn là chỉ huy chiến trường của lữ đoàn.', fresh=True)

# Prompt 22 C.3: the flash-forward before the first mission (MenuScreen.ShowFlashForward).
T('campaign.flash.kicker', 'Helion Launch Complex · Three years later', 'Helion Launch Complex · Ba năm sau', fresh=True)
T('campaign.flash.title', 'The Last Sky', 'Bầu trời cuối cùng', fresh=True)
T('campaign.flash',
  'The sky over Helion burns white. Something falls out of orbit: a tungsten rod the length of a train, faster than sound, '
  'faster than anything the brigade can shoot at. On an open channel, a calm voice: "They still don\'t understand." '
  'Three years earlier. Stormbeach.',
  'Bầu trời trên Helion cháy trắng. Một thứ rơi xuống từ quỹ đạo: thanh vonfram dài bằng cả đoàn tàu, nhanh hơn âm thanh, '
  'nhanh hơn mọi thứ lữ đoàn có thể bắn hạ. Trên kênh mở, một giọng nói điềm tĩnh: "Họ vẫn chưa hiểu." '
  'Ba năm trước. Stormbeach.', fresh=True)

# Prompt 20: four acts of three chapters; prompt 22: the names of the acts, each with the interlude after it.
ACTS = {
    1: ('Act I · Landfall', 'Hồi I · Landfall'),
    2: ('Act II · Counteroffensive', 'Hồi II · Counteroffensive'),
    3: ('Act III · Betrayal', 'Hồi III · Betrayal'),
    4: ('Act IV · Silver Sky', 'Hồi IV · Silver Sky'),
}
for n, (en, vi) in ACTS.items():
    T(f'act.{n}', en, vi, fresh=True)

# Prompt 22 B: twelve chapters and three interludes, in the order they are played. An interlude is numbered after the
# twelve (13-15) so no chapter's mission ids move, and goes with the act before it.
# number, act, interlude, title, maps, general (the card's portrait), opening card (3-4 sentences), timeline line once done
CHAPTERS = [
    (1, 1, 0, ('Coast of Fire', 'Coast of Fire'), ['landingbeach', 'greenvale', 'ashfield'], 'brandt',
     ('Dawn over Stormbeach. The landing craft ground on the sand under Hegemon\'s coastal guns, and the 7th Mechanized Brigade rolls ashore to open the first front in two years. '
      'Colonel Kade has one order: get off the beach, take the fishing village, find ground to build on in Greenvale, then take the Ashfield fortress. '
      'Major Brandt holds this coast, and he trusts his walls more than any man alive.',
      'Bình minh trên Stormbeach. Xuồng đổ bộ tì mũi lên cát dưới làn pháo bờ biển của Hegemon, và 7th Mechanized Brigade lăn bánh lên bờ, mở mặt trận đầu tiên sau hai năm. '
      'Đại tá Kade chỉ có một mệnh lệnh: rời bãi biển, chiếm làng chài, tìm chỗ đứng chân ở Greenvale, rồi đánh chiếm pháo đài Ashfield. '
      'Thiếu tá Brandt giữ bờ biển này, và ông ta tin tường thành của mình hơn tin bất kỳ ai.'),
     ('The brigade lands at Stormbeach, builds its first base in Greenvale and storms the Ashfield fortress. The Bastion falls and Major Brandt surrenders. '
      'His files name one man again and again: General Varga.',
      'Lữ đoàn đổ bộ ở Stormbeach, dựng căn cứ đầu tiên ở Greenvale rồi đánh chiếm pháo đài Ashfield. Bastion gục ngã và thiếu tá Brandt đầu hàng. '
      'Hồ sơ của ông ta nhắc đi nhắc lại một cái tên: tướng Varga.')),
    (2, 1, 0, ('Black Gold', 'Black Gold'), ['dunebreak', 'redrock'], 'varga',
     ('Every Hegemon engine runs on the oil of Dunebreak and Red Rock. Cut it, and the machines starve. '
      'General Varga, the man who built the Behemoth, has come south in person to guard his fuel, and he greets the brigade on the radio like one soldier to another. '
      'For the first time, General Thorne\'s army of the Accord will fight at our side.',
      'Mọi cỗ máy của Hegemon đều chạy bằng dầu của Dunebreak và Red Rock. Cắt nguồn dầu, lũ máy sẽ chết đói. '
      'Tướng Varga, cha đẻ của Behemoth, đích thân xuống phía nam giữ kho nhiên liệu, và ông chào lữ đoàn qua bộ đàm như một người lính chào một người lính. '
      'Lần đầu tiên, đạo quân Accord của tướng Thorne sẽ sát cánh cùng ta.'),
     ('Varga shows himself at Dunebreak. The refinery burns with the Inferno inside it, and at Red Rock, with Thorne\'s army beside us, the Behemoth falls. '
      'That night Mara tells Kade where she learned to build it.',
      'Varga lộ diện ở Dunebreak. Nhà máy lọc dầu bốc cháy cùng Inferno bên trong, và ở Red Rock, với đạo quân của Thorne bên cạnh, Behemoth gục ngã. '
      'Đêm đó Mara kể với Kade nơi cô đã học cách chế tạo nó.')),
    (3, 1, 0, ('The Long Winter', 'The Long Winter'), ['whiteout', 'frostpeak'], 'orlov',
     ('Winter comes early to the highlands. Across Frostpeak, Colonel Orlov has built a radar line that sees every convoy, and guns nobody sees that answer within a minute. '
      'Now something new hunts our supply columns from the clouds: the Harpy, and the ace who flies with it. Hawk has seen that insignia before.',
      'Mùa đông về sớm trên cao nguyên. Dọc Frostpeak, đại tá Orlov dựng một tuyến radar thấy được mọi đoàn xe, cùng những khẩu pháo không ai nhìn thấy, khai hỏa chưa tới một phút sau. '
      'Giờ có thêm thứ mới săn các đoàn tiếp tế của ta từ trên mây: Harpy, và viên phi công át chủ bài bay cùng nó. Hawk đã từng thấy phù hiệu ấy.'),
     ('The brigade blinds Orlov\'s radar line, brings the Harpy down and breaks Jötunn at the gate of Frostpeak. Orlov pulls his guns back north. '
      'His last words on the radio: "Winter always comes back."',
      'Lữ đoàn làm mù tuyến radar của Orlov, bắn rơi Harpy và hạ Jötunn trước cổng Frostpeak. Orlov rút pháo về phía bắc. '
      'Câu cuối của ông ta trên bộ đàm: "Mùa đông luôn quay lại."')),
    (13, 1, 1, ('Blueprints', 'Blueprints'), ['foundry'], 'varga',
     ('Mara has asked for one week and one convoy. Somewhere in the Foundry, the old Hegemon factory where the first Behemoth was built, are the blueprints of every Behemoth since, '
      'and she knows exactly which drawer. So does the machine that still guards its halls: Behemoth Mk.0, the prototype she designed herself. '
      'Major Brenn, the brigade\'s quartermaster, is coming to carry the paperwork.',
      'Mara xin đúng một tuần và một đoàn xe. Đâu đó trong Foundry, nhà máy cũ của Hegemon nơi chiếc Behemoth đầu tiên ra đời, là bản thiết kế của mọi chiếc Behemoth về sau, '
      'và cô biết chính xác nó nằm trong ngăn kéo nào. Cỗ máy vẫn canh giữ các xưởng cũng biết: Behemoth Mk.0, bản nguyên mẫu do chính cô thiết kế. '
      'Thiếu tá Brenn, quân nhu trưởng của lữ đoàn, đi cùng để khuân giấy tờ.'),
     ('At the Foundry Mara faces the Behemoth Mk.0 she drew as a young engineer, and brings its blueprints home. Major Brenn signs for every page.',
      'Ở Foundry, Mara đối mặt với chiếc Behemoth Mk.0 cô từng vẽ khi còn là một kỹ sư trẻ, và mang bản thiết kế của nó về. Thiếu tá Brenn ký nhận từng trang.')),
    (4, 2, 0, ('Iron Harbor', 'Iron Harbor'), ['rustyard', 'ironport', 'lighthousebay'], 'kessler',
     ('Everything Hegemon builds leaves through Ironport. Admiral Kessler runs its cranes, its rails and its armoured trains like a ledger that has never shown a loss. '
      'The Accord goes over to the attack: take the Rust Yard, cut the rail lines, seize the port. '
      'Nadia\'s intercepts keep mentioning cargo too heavy for any ship: Varga\'s Behemoths, and one called Tempest.',
      'Mọi thứ Hegemon chế tạo đều đi qua Ironport. Đô đốc Kessler điều hành cần cẩu, đường ray và những đoàn tàu bọc thép như một cuốn sổ cái chưa từng ghi lỗ. '
      'Accord chuyển sang phản công: chiếm Rust Yard, cắt đường ray, đánh chiếm bến cảng. '
      'Các bản chặn thu của Nadia cứ nhắc mãi tới những chuyến hàng nặng quá sức mọi con tàu: các chiếc Behemoth của Varga, và một chiếc tên Tempest.'),
     ('Juggernaut is derailed, Tempest dies on its own quay and the port is ours. Kessler runs to sea, and off Beacon Bay the brigade mans the old coastal batteries and sinks Leviathan. '
      'Kessler lives; his fleet does not. One of Thorne\'s columns was not where it had promised to be.',
      'Juggernaut bị lật, Tempest gục ngay trên cầu tàu của nó và bến cảng về tay ta. Kessler chạy ra biển, và ngoài khơi Beacon Bay, lữ đoàn chiếm các trận địa pháo bờ biển cũ rồi đánh chìm Leviathan. '
      'Kessler sống sót; hạm đội của ông ta thì không. Một cánh quân của Thorne đã không có mặt ở nơi đã hứa.')),
    (5, 2, 0, ('Burning Canopy', 'Burning Canopy'), ['junglepass', 'emberridge'], 'sen',
     ('Under the volcanoes of Emberridge and the canopy of Jungle Pass, Dr Elara Venn builds drones by the thousand. '
      'She designed her swarms to find survivors under rubble; Aurel made them into weapons. Burn the drone works and the sky clears. '
      'Nadia has been listening to Venn\'s own signals, and they do not sound like a woman who wants to win.',
      'Dưới chân núi lửa Emberridge và tán rừng Jungle Pass, tiến sĩ Elara Venn chế tạo drone theo từng nghìn chiếc. '
      'Bà thiết kế bầy drone để tìm người sống sót dưới đống đổ nát; Aurel biến chúng thành vũ khí. Đốt xưởng drone thì bầu trời sẽ sạch. '
      'Nadia vẫn nghe lén tín hiệu của chính Venn, và chúng không giống lời của một người muốn thắng.'),
     ('Locust, the Hive and at last the Matriarch fall over the burning canopy. Dr Venn walks out of her drone works alone, gives herself up with a drive marked "Icarus", '
      'and goes to work for the Accord.',
      'Locust, Hive rồi Matriarch lần lượt rơi trên tán rừng đang cháy. Tiến sĩ Venn một mình bước ra khỏi xưởng drone, ra hàng cùng một ổ đĩa đề "Icarus", '
      'và bắt đầu làm việc cho Accord.')),
    (6, 2, 0, ('Counterstrike', 'Counterstrike'), ['ashfield', 'whiteout', 'greenvale', 'landingbeach', 'hydrodam'], 'varga',
     ('Hegemon strikes back. Varga throws everything he has left at the ground the brigade took in the first act: Ashfield, Whiteout Pass and the Hollow Dam that lights half the coast. '
      'Charybdis is coming for the beach where we landed. Help comes from a man nobody expected: Major Brandt has changed sides, and he knows every wall Varga wants back. '
      'And Mara has a captured Behemoth running for us.',
      'Hegemon phản đòn. Varga ném tất cả những gì còn lại vào những vùng đất lữ đoàn đã chiếm ở hồi đầu: Ashfield, Whiteout Pass và Hollow Dam thắp sáng nửa Meridian Coast. '
      'Charybdis đang nhắm vào chính bãi biển ta đã đổ bộ. Ta có người giúp mà không ai ngờ tới: thiếu tá Brandt đã đổi phe, và ông thuộc từng bức tường Varga muốn đòi lại. '
      'Còn Mara đã cho một chiếc Behemoth bắt được chạy về phía ta.'),
     ('Varga\'s counterstrike breaks on the Hollow Dam. Before it, for one morning, Varga and Kade held their fire so the valley could get out; it was the only time the two men spoke. '
      'Moloch goes into the gorge. Thorne\'s army arrives late, again.',
      'Cuộc tổng phản công của Varga vỡ tan trước Hollow Dam. Trước đó, trong đúng một buổi sáng, Varga và Kade ngừng bắn để dân trong thung lũng kịp chạy; đó là lần duy nhất hai người nói chuyện với nhau. '
      'Moloch lao xuống hẻm sông. Quân của Thorne lại tới muộn.')),
    (14, 2, 2, ('The Queen\'s Choice', 'The Queen\'s Choice'), ['swamp', 'borderbridge'], None,
     ('Everyone wants Dr Venn. Hegemon wants her back or dead, and a faction inside the Accord wants her tried and hanged for every drone she ever built. '
      'The brigade will take her through Mirewood and over the Border Crossing to safety. Captain Kaia Mendez leads the escort, fast. '
      'Behind them two Locusts are already hunting: Venn\'s own design.',
      'Ai cũng muốn có tiến sĩ Venn. Hegemon muốn bắt bà về hoặc giết bà, còn một phe cực đoan trong Accord muốn đem bà ra xử treo cổ vì mọi chiếc drone bà từng tạo ra. '
      'Lữ đoàn sẽ đưa bà qua Mirewood và Border Crossing tới nơi an toàn. Đại úy Kaia Mendez dẫn đoàn hộ tống, và dẫn thật nhanh. '
      'Phía sau, hai chiếc Locust đã lên đường săn lùng: thiết kế của chính Venn.'),
     ('The brigade takes Dr Venn through Mirewood and over the Border Crossing with two Locusts on her trail. On the far bank she makes her choice: she stays with the brigade.',
      'Lữ đoàn đưa tiến sĩ Venn qua Mirewood và Border Crossing với hai chiếc Locust bám theo. Tới bờ bên kia, bà đưa ra lựa chọn của mình: bà ở lại với lữ đoàn.')),
    (7, 3, 0, ('Veyra', 'Veyra'), ['metrocity', 'veyra_old_quarter', 'capital'], 'hung',
     ('The road to Veyra, the capital, runs through Metro City and the narrow streets of the Old Quarter, district by district. '
      'General Thorne brings the Accord\'s largest army to share the liberation, with a base of his own beside ours. Major Dahl has the brigade\'s guns ranged on every bridge. '
      'Nadia has said it three times now: watch Thorne. Nobody listens.',
      'Con đường tới Veyra, thủ đô, chạy qua Metro City và những con phố hẹp của Old Quarter, từng quận một. '
      'Tướng Thorne kéo đạo quân lớn nhất của Accord tới cùng giải phóng, với căn cứ riêng đặt ngay cạnh căn cứ của ta. Thiếu tá Dahl đã căn pháo của lữ đoàn vào từng cây cầu. '
      'Nadia đã nói tới lần thứ ba: hãy để mắt tới Thorne. Không ai nghe.'),
     ('Veyra is free. In the middle of the last battle Thorne\'s base turned its guns on the brigade; Nadia saw it first and saved half of us. '
      'We fought back through Atlas and stopped Nemesis at the edge of the centre. Thorne escaped with a third of the Accord\'s army.',
      'Veyra được giải phóng. Giữa trận cuối, căn cứ của Thorne quay pháo vào lữ đoàn; Nadia là người thấy đầu tiên và cứu được một nửa quân ta. '
      'Ta đánh ngược lại qua Atlas và chặn Nemesis ngay rìa trung tâm. Thorne trốn thoát cùng một phần ba đạo quân của Accord.')),
    (8, 3, 0, ('Underworld', 'Underworld'), ['redrock', 'openpit', 'hydrodam', 'dunebreak'], 'hung',
     ('Thorne has run north to Deepcut Mine, where Hegemon digs the metal for its machines, and he is not hiding. He is digging in: tunnels, bunkers, a fortress under the pit, '
      'as if he only has to hold on until something arrives from the sky. Captain Varro\'s people know every road in the mining country. '
      'Sergeant Major Quist knows what is worth taking home.',
      'Thorne đã chạy lên Deepcut Mine ở phía bắc, nơi Hegemon đào kim loại cho những cỗ máy của nó, và ông ta không trốn. Ông ta đang cố thủ: đường hầm, boong-ke, cả một pháo đài dưới đáy mỏ, '
      'như thể chỉ cần cầm cự cho tới khi một thứ gì đó tới từ trên trời. Người của đại úy Varro thuộc mọi con đường trong vùng mỏ. '
      'Thượng sĩ Quist thì biết thứ gì đáng mang về.'),
     ('The brigade follows Thorne into Deepcut Mine. Tartarus and Ixion fall, and Kronos is stopped short of our base. Thorne escapes again, to the sea.',
      'Lữ đoàn đuổi theo Thorne vào Deepcut Mine. Tartarus và Ixion gục ngã, còn Kronos bị chặn lại trước khi tới căn cứ của ta. Thorne lại trốn thoát, ra biển.')),
    (9, 3, 0, ('Rough Water', 'Rough Water'), ['ironport', 'landingbeach', 'lighthousebay', 'coralisles'], 'hung',
     ('Thorne has found what is left of Kessler\'s fleet and made it his own. Caspian skims the coast, Scylla is back in service, '
      'and somewhere under Beacon Bay and the Coral Keys a submarine is talking to the sky. Dr Venn is listening to it. This is where Thorne has to be stopped.',
      'Thorne đã tìm thấy tàn quân hạm đội của Kessler và biến nó thành của mình. Caspian lướt dọc bờ biển, Scylla trở lại hoạt động, '
      'và đâu đó dưới Beacon Bay và Coral Keys, một tàu ngầm đang liên lạc với bầu trời. Tiến sĩ Venn đang nghe nó. Đây là nơi phải chặn Thorne lại.'),
     ('Typhon surfaced in the middle of the bay with Thorne on its bridge, and went down. His last message came after it sank: the coordinates of Project Icarus\'s launch site, '
      'and one line. "Don\'t let me have been right." Nobody found his body.',
      'Typhon nổi lên giữa vịnh với Thorne trên đài chỉ huy, rồi chìm. Tin nhắn cuối của ông ta tới sau khi tàu đã chìm: tọa độ bãi phóng của Dự án Icarus, '
      'và một câu: "Đừng để tôi đã đúng." Không ai tìm thấy thi thể ông ta.')),
    (15, 3, 3, ('Hawk and Raven', 'Hawk and Raven'), ['frostpeak', 'junglepass'], 'quaden',
     ('Hawk went down behind the lines last night, somewhere between the Frostpeak heights and Jungle Pass, and his beacon is still talking. '
      'So is Raven\'s radio: he wants to finish the job himself, in Morrigan, his own fighter. Colonel Reyn\'s elite column is going in to bring Hawk home.',
      'Đêm qua Hawk bị bắn rơi sau chiến tuyến, đâu đó giữa các điểm cao Frostpeak và Jungle Pass, và đèn hiệu của anh vẫn đang phát. '
      'Bộ đàm của Raven cũng vậy: hắn muốn tự tay kết thúc, bằng Morrigan, chiếc tiêm kích riêng của hắn. Đội quân tinh nhuệ của đại tá Reyn đang tiến vào để đưa Hawk về.'),
     ('Colonel Reyn\'s column finds Hawk and brings him out through Frostpeak and Jungle Pass, with Morrigan overhead. Raven lets him go, this time.',
      'Đội quân của đại tá Reyn tìm thấy Hawk và đưa anh ra qua Frostpeak và Jungle Pass, với Morrigan trên đầu. Raven để anh đi, lần này.')),
    (10, 4, 0, ('War in the Sky', 'War in the Sky'), ['frostpeak', 'skyhold', 'whiteout'], 'quaden',
     ('Thorne\'s coordinates point past Skyhold, and Raven has thrown Hegemon\'s whole air force into the sky over it. Spectre circles the passes at night; Argus spots for the guns. '
      'And over Skyhold something descends that is not an aircraft. Captain Okoye has fuel and shells for a long air campaign. Hawk has a debt to settle.',
      'Tọa độ của Thorne chỉ về phía sau Skyhold, và Raven đã tung toàn bộ không quân Hegemon lên bầu trời nơi đó. Spectre bay vòng trên các con đèo trong đêm; Argus chỉ điểm cho pháo binh. '
      'Và trên Skyhold, có một thứ hạ xuống mà không phải máy bay. Đại úy Okoye đã chuẩn bị đủ nhiên liệu và đạn cho một chiến dịch trên không kéo dài. Hawk thì có một món nợ cần đòi.'),
     ('Icarus Mk.0 shows itself over Skyhold and runs: a test, Venn says, of something much bigger. Hawk beats Raven in the air, and in the storming of Skyhold he fires the last shot.',
      'Icarus Mk.0 lộ diện trên Skyhold rồi bỏ chạy: một bản thử nghiệm, Venn nói, cho một thứ lớn hơn nhiều. Hawk hạ Raven trên không, và trong trận đánh chiếm Skyhold, anh bắn phát cuối cùng.')),
    (11, 4, 0, ('Skygate', 'Skygate'), ['rustyard', 'skyhold', 'frostpeak', 'orbitalgate'], 'aurel',
     ('For the first time, Director Aurel speaks on the radio, and he has only one thing to say: the first satellite is in orbit. '
      'Before Icarus can fly he needs the Skygate Array, the radars and pads that guide his ships up and down, and Orlov is waiting there with Gungnir for his last battle. '
      'Above it all, Daedalus is landing troops.',
      'Lần đầu tiên, giám đốc Aurel lên bộ đàm, và ông ta chỉ nói một điều: vệ tinh đầu tiên đã lên quỹ đạo. '
      'Trước khi Icarus cất cánh, ông ta cần Skygate Array, các trạm radar và bệ phóng dẫn đường cho tàu lên xuống, và Orlov đang chờ ở đó cùng Gungnir cho trận cuối của mình. '
      'Phía trên tất cả, Daedalus đang đổ quân.'),
     ('Orlov fights his last battle with Gungnir and gives himself up by radio. Venn finds her drone programme in Aurel\'s hands. Daedalus falls on the Skygate Array, and the road to Helion is open.',
      'Orlov đánh trận cuối cùng với Gungnir rồi ra hàng qua bộ đàm. Venn phát hiện chương trình drone của mình đã nằm trong tay Aurel. Daedalus rơi xuống Skygate Array, và con đường tới Helion mở ra.')),
    (12, 4, 0, ('Helion', 'Helion'), ['launchsite', 'saltflat', 'dunebreak', 'lighthousebay'], 'aurel',
     ('Everything Hegemon has left is at the Helion Launch Complex: Varga with his last Behemoth, Kessler with his last ship, Venn\'s drones in Aurel\'s hands, and Icarus itself on its pad. '
      'Mara has one surprise of her own, repaired and repainted. At the end of the road Aurel waits, ready to take the sky and keep it.',
      'Tất cả những gì Hegemon còn lại đều dồn về Helion Launch Complex: Varga với chiếc Behemoth cuối cùng, Kessler với con tàu cuối cùng, bầy drone của Venn trong tay Aurel, và chính Icarus trên bệ phóng. '
      'Mara cũng có một bất ngờ của riêng mình, đã sửa lại và sơn lại. Ở cuối con đường, Aurel đang chờ, sẵn sàng chiếm lấy bầu trời và giữ lấy nó.'),
     ('Varga falls like a soldier; Kessler bargains to the last. Aurel launches Icarus and a tungsten rod falls from orbit, but Icarus falls after it, as its name promised. '
      'Aurel fights to the end in the wreck. The Meridian Coast is free.',
      'Varga ngã xuống như một người lính; Kessler mặc cả tới phút cuối. Aurel phóng Icarus và một thanh vonfram rơi từ quỹ đạo, nhưng rồi Icarus rơi theo, đúng như cái tên của nó. '
      'Aurel chiến đấu tới cùng trong xác phi thuyền. Meridian Coast được giải phóng.')),
]

ORDER = [c[0] for c in CHAPTERS]
ACT_OF = {c[0]: c[1] for c in CHAPTERS}
INTERLUDES = {c[0] for c in CHAPTERS if c[2]}

for n, act, interlude, title, maps, general, card, done in CHAPTERS:
    T(f'chapter.{n}.title', *title, fresh=True)
    T(f'chapter.{n}.summary', *card, fresh=True)
    T(f'timeline.{n}', *done, fresh=True)

# Prompt 20 A-B: each chapter's boss slots, the main boss and its mini bosses (a slot is the boss's id; one not built
# yet is fought as the stand-in its missions name as "fallback"). Prompt 22: an interlude has no main boss; chapter 7
# brings back Inferno and Juggernaut in the city streets; Behemoth Mk.0 (interlude I) and Morrigan (interlude III,
# chapter 10) come from part E (P22-content builds them; until then they are fought as their fallbacks).
CHAPTER_BOSSES = {
    1: ('fortress_bastion', ['bastion_mk0']),
    2: ('behemoth', ['behemoth_inferno']),
    3: ('mobile_fortress', ['mega_gunship', 'fenrir']),
    13: (None, ['behemoth_mk0']),
    4: ('leviathan', ['behemoth_tempest', 'armored_train', 'scylla']),
    5: ('drone_mothership', ['locust', 'fortress_hive']),
    6: ('moloch', ['landing_hovercraft', 'behemoth_mk2']),
    14: (None, ['locust']),
    7: ('nuke_train', ['supreme_command', 'behemoth_inferno', 'armored_train']),
    8: ('kronos', ['ixion', 'earth_borer']),
    9: ('typhon', ['caspian', 'scylla']),
    15: (None, ['morrigan']),
    10: ('command_airship', ['sky_fortress', 'icarus_mk0', 'argus', 'morrigan']),
    11: ('daedalus', ['rail_supergun', 'locust']),
    12: ('silver_bug', ['behemoth_mk2', 'scylla', 'locust']),
}

# Prompt 22 B: main missions of each chapter (9-18; the owner's note of 30/09: a chapter runs from 9 to 18 missions by the
# story's pace) and side missions, the spec's starting counts with chapter 1 raised from 8 to 9 (DECISIONS 22A).
COUNTS = {1: (9, 1), 2: (11, 2), 3: (12, 2), 13: (4, 0), 4: (16, 2), 5: (13, 2), 6: (16, 2), 14: (4, 0),
          7: (18, 1), 8: (12, 2), 9: (14, 2), 15: (4, 0), 10: (14, 2), 11: (11, 1), 12: (10, 0)}

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

# Prompt 22 B: where a mission of the twelve chapters of ten went (campaign version 3 to 4; PlayerProfile.MigrateCampaign).
# Every other mission keeps its id; c12s1 and c12s2 are gone (chapter 12 has no side mission), their stars with them.
MOVES22 = {'c1m07': 'c6m11', 'c1s2': 'c6m12', 'c7s2': 'c7m11', 'c11s2': 'c11m11'}

T('timeline.0', 'Two years before the landing: the government of the Meridian Coast collapses. A mining consortium hires Hegemon to keep order, and Hegemon keeps the coast.',
  'Hai năm trước cuộc đổ bộ: chính quyền Meridian Coast sụp đổ. Một tập đoàn khai khoáng thuê Hegemon giữ trật tự, và Hegemon giữ luôn cả vùng.', fresh=True)

# Prompt 22 C.5: the ending.
T('campaign.epilogue.title', 'Epilogue: Clear Sky', 'Vĩ thanh: Bầu trời trong')
T('campaign.epilogue',
  'Icarus fell out of the sky, as its name had always promised, and Aurel went down fighting in its wreck. Without him Hegemon came apart in a month. '
  'After three years, the Meridian Coast was free. Colonel Kade was offered a seat in the new government and turned it down; his place, he said, was with the brigade. '
  'Mara and Dr Venn spent the spring taking apart the machines they had helped to build. Hawk flew one last patrol over Skyhold and came back grinning. '
  'On the night the brigade stood down, Nadia was still at the orbital tracking screen. A few points of light up there had no explanation. '
  'Project Icarus had never been only one ship.',
  'Icarus rơi khỏi bầu trời, đúng như cái tên của nó vẫn báo trước, và Aurel chiến đấu tới cùng trong xác phi thuyền. Không còn Aurel, Hegemon tan rã chỉ trong một tháng. '
  'Sau ba năm, Meridian Coast được giải phóng. Đại tá Kade được mời vào chính phủ mới và từ chối; chỗ của ông, ông nói, là ở lữ đoàn. '
  'Mara và tiến sĩ Venn dành cả mùa xuân tháo dỡ những cỗ máy họ từng góp tay tạo ra. Hawk bay lượt tuần tra cuối cùng qua Skyhold và trở về cười toe. '
  'Đêm lữ đoàn giải ngũ, Nadia vẫn ngồi trước màn hình theo dõi quỹ đạo. Trên đó còn vài chấm sáng chưa ai giải thích được. '
  'Dự án Icarus chưa bao giờ chỉ có một phi thuyền.', fresh=True)

# ------------------------------------------------------------------------------------------ the people

# Prompt 22 C.2: who is who and what drives them. id (kept from before), side, name, role, bio.
CHARACTERS = [
    ('khai', 'ours', ('Colonel Marcus Kade', 'Đại tá Marcus Kade'), ('Commander, 7th Mechanized Brigade · call sign Iron', 'Chỉ huy 7th Mechanized Brigade · biệt danh Iron'),
     ('Kade commands the brigade in the field and on the radio. Calm, practical, never heard to raise his voice. '
      'He trusts the brigade more than any politician, and he plans a battle the way a mechanic fixes an engine: find what is broken, fix that, move on.',
      'Kade chỉ huy lữ đoàn ngoài chiến trường và trên sóng bộ đàm. Điềm tĩnh, thực dụng, chưa ai nghe ông lớn tiếng. '
      'Ông tin lữ đoàn hơn tin bất kỳ chính trị gia nào, và lên kế hoạch trận đánh như thợ máy sửa động cơ: tìm chỗ hỏng, sửa chỗ đó, rồi đi tiếp.')),
    ('mai', 'ours', ('Engineer Mara Lind', 'Kỹ sư Mara Lind'), ('Chief engineer; runs the base', 'Kỹ sư trưởng, phụ trách căn cứ'),
     ('Mara keeps the base running and signs off every HQ upgrade. Before the war she was an engineer on Hegemon\'s Behemoth programme; the first prototype was hers. '
      'When she saw what they were for she walked out, and she has not forgiven herself since. She knows every weak seam in Varga\'s machines.',
      'Mara giữ cho căn cứ vận hành và ký duyệt mọi lần nâng cấp sở chỉ huy. Trước chiến tranh, cô là kỹ sư trong chương trình Behemoth của Hegemon; bản nguyên mẫu đầu tiên là của cô. '
      'Khi thấy chúng được làm ra để làm gì, cô bỏ đi, và từ đó chưa tha thứ cho mình. Cô biết từng đường hàn yếu trên những cỗ máy của Varga.')),
    ('dieuhau', 'ours', ('Lieutenant Jonah Reyes', 'Trung úy Jonah Reyes'), ('Leads the air wing · call sign Hawk', 'Chỉ huy không quân · biệt danh Hawk'),
     ('Jonah Reyes, call sign Hawk, flies everything the brigade owns that leaves the ground. Young, loud, reckless, and better than he admits. '
      'Raven shot down his old wingman over this coast, and Hawk has been waiting to meet him ever since.',
      'Jonah Reyes, biệt danh Hawk, lái mọi thứ biết cất cánh của lữ đoàn. Trẻ, ồn ào, liều lĩnh, và giỏi hơn những gì anh chịu nhận. '
      'Raven đã bắn hạ đồng đội bay cũ của anh trên vùng biển này, và từ đó Hawk vẫn chờ ngày gặp lại hắn.')),
    ('linh', 'ours', ('Captain Nadia Kerr', 'Đại úy Nadia Kerr'), ('Intelligence officer', 'Sĩ quan tình báo'),
     ('Nadia reads Hegemon\'s mail. Intercepts, captured drives, a burnt notebook: she turns them into targets, into the side jobs nobody else has time for, '
      'and into questions nobody wants to hear. Precise, patient, and the only one who can make Kade laugh.',
      'Nadia đọc thư của Hegemon. Bản chặn thu, ổ cứng thu được, một cuốn sổ cháy dở: cô biến tất cả thành mục tiêu, thành những nhiệm vụ phụ không ai có thời gian làm, '
      'và thành những câu hỏi không ai muốn nghe. Chính xác, kiên nhẫn, và là người duy nhất làm được Kade bật cười.')),
    ('hung', 'ours', ('General Roland Thorne', 'Tướng Roland Thorne'), ('Commander of the Accord\'s largest army · call sign Titan', 'Tư lệnh đạo quân lớn nhất của Accord · biệt danh Titan'),
     ('Thorne commands the Accord\'s largest allied army and has won more battles than anyone on our side. Brave, generous with his men, and tired in a way nobody can explain. '
      'He fights beside the brigade in the great operations, with a base of his own. Nadia does not trust him.',
      'Thorne chỉ huy đạo quân đồng minh lớn nhất của Accord và thắng nhiều trận hơn bất kỳ ai bên ta. Dũng cảm, hào phóng với lính của mình, và mệt mỏi theo một cách không ai giải thích được. '
      'Ông sát cánh cùng lữ đoàn trong các chiến dịch lớn, với căn cứ riêng. Nadia không tin ông.')),
    ('brandt', 'hegemon', ('Major Brandt', 'Thiếu tá Brandt'), ('Hegemon west coast garrison · call sign Bulwark', 'Đồn trú bờ biển phía tây của Hegemon · biệt danh Bulwark'),
     ('Brandt held the west coast for Hegemon with more concrete than men. He believes in walls absolutely, and he names his fortresses like old friends: the Bastion first of all. '
      'He surrendered at Ashfield rather than waste his garrison, and he has been thinking about walls ever since.',
      'Brandt giữ bờ biển phía tây cho Hegemon bằng bê tông nhiều hơn bằng người. Ông ta tin tuyệt đối vào tường thành, và đặt tên cho các pháo đài như gọi bạn cũ: trước hết là Bastion. '
      'Ông ta đầu hàng ở Ashfield để khỏi phí mạng quân đồn trú, và từ đó vẫn suy nghĩ về những bức tường.')),
    ('varga', 'hegemon', ('General Viktor Varga', 'Tướng Viktor Varga'), ('Hegemon armour; father of the Behemoth · call sign Anvil', 'Thiết giáp Hegemon; cha đẻ của Behemoth · biệt danh Anvil'),
     ('Varga is old, proud and honourable, and he loves his machines the way other men love their children. He built the Behemoth and has never lost his faith in weight. '
      'He respects a good opponent, and he has decided that the brigade\'s commander is one.',
      'Varga già, kiêu hãnh và trọng danh dự, và ông yêu những cỗ máy của mình như người ta yêu con. Ông chế tạo Behemoth và chưa bao giờ hết tin vào sức nặng. '
      'Ông tôn trọng một đối thủ xứng tầm, và ông đã quyết định chỉ huy của lữ đoàn là một người như thế.')),
    ('orlov', 'hegemon', ('Colonel Ilya Orlov', 'Đại tá Ilya Orlov'), ('Hegemon artillery · call sign Winter', 'Pháo binh Hegemon · biệt danh Winter'),
     ('Orlov has never seen the face of a man he killed, and prefers it that way. Cold, patient and exact, he likes to win from a distance his enemy cannot see. '
      'His bases are gun lines; his armies screen his batteries and wait for the shells to do the work.',
      'Orlov chưa từng nhìn mặt người nào ông ta giết, và ông ta muốn thế. Lạnh lùng, kiên nhẫn, chính xác, ông ta thích thắng từ khoảng cách đối thủ không nhìn thấy mình. '
      'Căn cứ của ông ta là những trận địa pháo; quân của ông ta che chắn cho các khẩu đội và chờ đạn pháo làm nốt phần việc.')),
    ('kessler', 'hegemon', ('Admiral Magnus Kessler', 'Đô đốc Magnus Kessler'), ('Hegemon logistics and navy · call sign Maelstrom', 'Hậu cần và hải quân Hegemon · biệt danh Maelstrom'),
     ('Kessler runs Hegemon\'s ports, trains and ships, and he runs the war like a balance sheet: every shell a cost, every city an asset. '
      'He has never lost a shipment or an argument about a timetable. His armies are balanced to the gram, and he mines anything he cannot hold.',
      'Kessler điều hành bến cảng, đường sắt và tàu chiến của Hegemon, và ông ta điều hành chiến tranh như một bảng cân đối: mỗi viên đạn là một khoản chi, mỗi thành phố là một tài sản. '
      'Ông ta chưa từng để thất lạc một chuyến hàng hay thua một cuộc cãi về thời gian biểu. Quân của ông ta cân bằng đến từng gam, và ông ta rải mìn bất cứ chỗ nào không giữ nổi.')),
    ('sen', 'hegemon', ('Dr Elara Venn', 'Tiến sĩ Elara Venn'), ('Hegemon drones; creator of the Hive · call sign Queen', 'Drone của Hegemon; người tạo ra Hive · biệt danh Queen'),
     ('Venn builds swarms the way other people knit. She designed the Hive as a rescue system for disaster zones, to find the living under rubble; Aurel armed it before she had finished her coffee. '
      'She fights with drones, jammers and hangars full of both, and she has begun to wonder who she is working for.',
      'Venn tạo ra bầy drone như người khác đan len. Bà thiết kế Hive làm hệ thống cứu hộ cho vùng thảm họa, để tìm người còn sống dưới đống đổ nát; Aurel vũ trang cho nó trước khi bà kịp uống xong ly cà phê. '
      'Bà đánh bằng drone, xe gây nhiễu và những nhà chứa đầy cả hai thứ, và bà bắt đầu tự hỏi mình đang làm việc cho ai.')),
    ('quaden', 'hegemon', ('Kasimir Wolff', 'Kasimir Wolff'), ('Hegemon air ace · call sign Raven', 'Át chủ bài không quân Hegemon · biệt danh Raven'),
     ('Kasimir Wolff, call sign Raven, commands Hegemon\'s air wing from Skyhold and has more kills than the rest of it together. Arrogant, brilliant, bored by anyone slower than him. '
      'He flies Morrigan, a fighter built for him alone. One of his kills was Hawk\'s wingman.',
      'Kasimir Wolff, biệt danh Raven, chỉ huy không quân Hegemon từ Skyhold và có số lần hạ địch nhiều hơn cả phần còn lại cộng lại. Kiêu ngạo, tài giỏi, chán ngán bất kỳ ai chậm hơn mình. '
      'Hắn lái Morrigan, chiếc tiêm kích làm riêng cho hắn. Một trong những người hắn bắn hạ là đồng đội bay của Hawk.')),
    ('aurel', 'hegemon', ('Director Lucien Aurel', 'Giám đốc Lucien Aurel'), ('Head of Hegemon; Project Icarus · call sign Sol', 'Người đứng đầu Hegemon; Dự án Icarus · biệt danh Sol'),
     ('Aurel runs Project Icarus, an orbital weapon that can strike anywhere on the ground. He believes that whoever holds the sky holds the world, '
      'and he talks about war the way accountants talk about quarterly results. He plans never to be in range of anything.',
      'Aurel điều hành Dự án Icarus, một vũ khí quỹ đạo có thể tấn công bất kỳ điểm nào trên mặt đất. Ông ta tin rằng ai kiểm soát bầu trời sẽ kiểm soát thế giới, '
      'và nói về chiến tranh như kế toán nói về báo cáo quý. Ông ta định sẽ không bao giờ đứng trong tầm bắn của bất cứ thứ gì.')),
    # Prompt 22 C.4: the officers who join the brigade on the way (the commanders of prompt 22 F, pass 3).
    ('brenn', 'ours', ('Major Otto Brenn', 'Thiếu tá Otto Brenn'), ('Quartermaster · call sign Ledger', 'Quân nhu trưởng · biệt danh Ledger'),
     ('Brenn has counted every shell, tyre and ration the brigade ever used, and can tell you which ones it wasted. Dry, exact and quietly funny. '
      'He helped Mara bring the Behemoth files out of the Foundry, and made her sign for them.',
      'Brenn đã đếm từng viên đạn, từng chiếc lốp, từng suất ăn lữ đoàn từng dùng, và nói được chiếc nào bị lãng phí. Khô khan, chính xác, hài hước theo kiểu lặng lẽ. '
      'Ông giúp Mara mang hồ sơ Behemoth ra khỏi Foundry, và bắt cô ký nhận.')),
    ('adler', 'ours', ('Captain Tomas Adler', 'Đại úy Tomas Adler'), ('Strongpoint assault · call sign Flag', 'Đánh chiếm cứ điểm · biệt danh Flag'),
     ('Adler has planted the brigade\'s flag on more objectives than anyone, and keeps a spare in his hatch. Eager, loud on the radio, first through any gate. '
      'He led the capture of the harbour strongpoints at Ironport.',
      'Adler đã cắm cờ lữ đoàn trên nhiều cứ điểm hơn bất kỳ ai, và luôn giữ một lá cờ dự phòng trong nắp xe. Hăng hái, ồn ào trên bộ đàm, luôn là người đầu tiên qua mọi cánh cổng. '
      'Anh dẫn đợt đánh chiếm các cứ điểm ven cảng ở Ironport.')),
    ('mendez', 'ours', ('Captain Kaia Mendez', 'Đại úy Kaia Mendez'), ('Fast columns · call sign Rush', 'Đoàn xe cơ động · biệt danh Rush'),
     ('Mendez believes the safest place in a war is somewhere else, quickly. Her column moves before the order is finished. '
      'She led Dr Venn\'s escort across Mirewood and never once stopped.',
      'Mendez tin rằng nơi an toàn nhất trong chiến tranh là một nơi khác, tới thật nhanh. Đoàn xe của cô xuất phát trước khi mệnh lệnh kịp nói hết. '
      'Cô dẫn đoàn hộ tống tiến sĩ Venn qua Mirewood mà không dừng lại lần nào.')),
    ('dahl', 'ours', ('Major Piet Dahl', 'Thiếu tá Piet Dahl'), ('Brigade artillery · call sign Longshot', 'Pháo binh lữ đoàn · biệt danh Longshot'),
     ('Dahl measures everything in metres and seconds, his patience included. He commanded the brigade\'s guns in the battle for Veyra '
      'and never fired a round he could not account for.',
      'Dahl đo mọi thứ bằng mét và giây, kể cả sự kiên nhẫn của mình. Ông chỉ huy pháo binh lữ đoàn trong trận Veyra '
      'và chưa từng bắn một viên đạn nào mà không giải thích được.')),
    ('varro', 'ours', ('Captain Ines Varro', 'Đại úy Ines Varro'), ('Local militia · call sign Tide', 'Dân quân địa phương · biệt danh Tide'),
     ('Varro grew up in the mining country and knows everyone in it. Her militia is cheap, numerous and everywhere, like a tide coming in. She joined the brigade at Deepcut Mine.',
      'Varro lớn lên ở vùng mỏ và quen tất cả mọi người ở đó. Dân quân của cô rẻ, đông và có mặt khắp nơi, như thủy triều dâng. Cô gia nhập lữ đoàn ở Deepcut Mine.')),
    ('quist', 'ours', ('Sergeant Major Lena Quist', 'Thượng sĩ Lena Quist'), ('Salvage · call sign Magpie', 'Thu hồi chiến lợi phẩm · biệt danh Magpie'),
     ('Quist cannot pass a wreck without taking something shiny off it, and half the brigade\'s spare parts came out of her pockets. She joined at Deepcut Mine and emptied it.',
      'Quist không thể đi qua một cái xác xe mà không gỡ lấy thứ gì đó sáng bóng, và một nửa phụ tùng dự phòng của lữ đoàn đến từ túi của cô. Cô gia nhập ở Deepcut Mine và vét sạch nó.')),
    ('reyn', 'ours', ('Colonel August Reyn', 'Đại tá August Reyn'), ('Elite forces · call sign Crown', 'Lực lượng tinh nhuệ · biệt danh Crown'),
     ('Reyn commands the Accord\'s elite heavy column: the best crews, the heaviest machines, and a very high opinion of both. Formal and proud. He led the rescue that brought Hawk home.',
      'Reyn chỉ huy đoàn thiết giáp tinh nhuệ của Accord: kíp lái giỏi nhất, cỗ máy nặng nhất, và một đánh giá rất cao về cả hai. Nghiêm trang và kiêu hãnh. Ông dẫn cuộc giải cứu đưa Hawk về nhà.')),
    ('okoye', 'ours', ('Captain Selma Okoye', 'Đại úy Selma Okoye'), ('Logistics · call sign Vault', 'Hậu cần · biệt danh Vault'),
     ('Okoye keeps a reserve of everything, the reserve included. Patient, unhurried, impossible to surprise. She ran the supply of the long air campaign over Skyhold.',
      'Okoye luôn giữ dự trữ của mọi thứ, kể cả dự trữ của dự trữ. Kiên nhẫn, thong thả, không gì làm cô bất ngờ được. Cô lo tiếp tế cho chiến dịch trên không kéo dài quanh Skyhold.')),
]

for cid, side, name, role, bio in CHARACTERS:
    T(f'char.{cid}.name', *name, fresh=True)
    T(f'char.{cid}.role', *role, fresh=True)
    T(f'char.{cid}.bio', *bio, fresh=True)

T('char.hq.name', 'Brigade HQ', 'Sở chỉ huy Lữ đoàn')
T('char.hq.role', 'Radio', 'Bộ đàm')

# The generals as the AI plays them: signature deck, fire support habits, base style, and their lines (prompt 22 C.7:
# each in his or her own voice; the lines that changed are fresh).
GENERALS = [
    ('varga', ['light_tank', 'main_battle_tank', 'heavy_tank', 'tank_destroyer', 'ifv', 'flame_tank', 'twin_tank', 'fpv_carrier'],
     ['artillery_barrage', 'airstrike', 'repair_drop'], 'varga', 'Attack',
     [('Welcome to the desert, Colonel. From one soldier to another.', 'Chào mừng tới sa mạc, đại tá. Từ một người lính tới một người lính.'),
      ('Every tank you burn, I build two.', 'Ông đốt một chiếc, tôi đóng hai chiếc.'),
      ('Come closer. My guns are lonely.', 'Lại gần đây. Pháo của tôi đang buồn lắm.')],
     ('Retreat. Save the machines. The men can walk.', 'Rút. Giữ lấy máy móc. Người thì đi bộ cũng được.')),
    ('orlov', ['mlrs', 'artillery', 'mortar_carrier', 'heavy_rocket_artillery', 'sam_launcher', 'main_battle_tank', 'aa_vehicle', 'command_vehicle'],
     ['artillery_barrage', 'cruise_missile', 'airstrike'], 'orlov', 'Defend',
     [('You are a coordinate, nothing more.', 'Ngươi chỉ là một tọa độ, không hơn.'),
      ('Fire mission. Grid one-seven. All batteries.', 'Nhiệm vụ bắn. Ô lưới một-bảy. Toàn bộ khẩu đội.'),
      ('Patience, Colonel. The snow is on my side.', 'Kiên nhẫn đi, đại tá. Tuyết đứng về phía ta.')],
     ('Recalculating. Withdraw the batteries to the next line.', 'Tính lại. Rút các khẩu đội về tuyến sau.')),
    ('kessler', ['wheeled_gun', 'ifv', 'main_battle_tank', 'heavy_tank', 'sam_launcher', 'fpv_carrier', 'mine_layer', 'mlrs'],
     ['remote_mines', 'artillery_barrage', 'repair_drop'], 'kessler', 'Defend',
     [('You are four minutes behind schedule, Colonel.', 'Ngươi đang trễ bốn phút so với lịch, đại tá.'),
      ('Every road here is mined. I checked.', 'Mọi con đường ở đây đều có mìn. Ta đã kiểm tra rồi.'),
      ('You cost more than you are worth, Colonel. I have the figures.', 'Ngươi tốn kém hơn giá trị của ngươi, đại tá. Ta có số liệu đây.')],
     ('Cancel the timetable. Evacuate the port by sea.', 'Hủy lịch trình. Sơ tán bến cảng bằng đường biển.')),
    ('sen', ['strike_drone', 'fpv_carrier', 'recon_drone', 'ew_jammer', 'ifv', 'main_battle_tank', 'aa_vehicle'],
     ['airstrike', 'cruise_missile', 'repair_drop'], 'sen', 'Attack',
     [('The swarm does not hate you. It does not feel anything.', 'Bầy drone không ghét các anh. Nó chẳng có cảm xúc gì cả.'),
      ('I built them to find people under rubble.', 'Tôi làm ra chúng để tìm người dưới đống đổ nát.'),
      ('I designed this to save people. Remember that when it kills you.', 'Tôi thiết kế thứ này để cứu người. Hãy nhớ điều đó khi nó giết các anh.')],
     ('Enough. Stand the swarm down.', 'Đủ rồi. Cho bầy drone hạ cánh.')),
    ('quaden', ['attack_helicopter', 'attack_jet', 'fighter_jet', 'strike_drone', 'aa_vehicle', 'main_battle_tank', 'sam_launcher'],
     ['airstrike', 'cruise_missile', 'napalm_strike'], 'quaden', 'Attack',
     [('Hawk! Still flying that museum piece?', 'Hawk! Vẫn lái cái đồ cổ đó à?'),
      ('Look up, Colonel. That is where you lose.', 'Nhìn lên đi, đại tá. Ông sẽ thua ở trên đó.'),
      ('The sky is mine. You can keep the mud.', 'Bầu trời là của ta. Bùn đất thì cứ giữ lấy.')],
     ('Eject, eject! …Not like this.', 'Nhảy dù, nhảy dù! …Không phải thế này chứ.')),
    ('hung', ['main_battle_tank', 'heavy_tank', 'titan_tank', 'ifv', 'aa_vehicle', 'mlrs', 'tank_destroyer'],
     ['artillery_barrage', 'airstrike', 'cruise_missile'], 'aurel', 'Attack',
     [('You fight well, Kade. It changes nothing.', 'Anh đánh giỏi lắm, Kade. Nhưng chẳng thay đổi được gì.'),
      ('Titans do not kneel, Colonel.', 'Titan không biết quỳ, đại tá ạ.'),
      ('Look up one night. Then tell me I was wrong.', 'Một đêm nào đó hãy nhìn lên trời. Rồi hãy nói tôi sai.')],
     ('Pull back. The sky will finish this for me.', 'Rút lui. Bầu trời sẽ kết thúc chuyện này thay tôi.')),
    ('aurel', ['heavy_tank', 'ifv', 'railgun_truck', 'attack_helicopter', 'long_sam', 'heavy_rocket_artillery', 'titan_tank', 'fighter_jet'],
     ['cruise_missile', 'airstrike', 'napalm_strike'], 'aurel', 'Attack',
     [('Your brigade is a rounding error on my balance sheet.', 'Lữ đoàn của ông chỉ là sai số làm tròn trên bảng cân đối của tôi.'),
      ('Whoever holds the sky holds the world, Colonel.', 'Ai giữ bầu trời thì giữ cả thế giới, đại tá.'),
      ('Icarus is not a weapon. It is a contract nobody can refuse.', 'Icarus không phải vũ khí. Nó là một bản hợp đồng không ai từ chối nổi.')],
     ('This was not in the forecast.', 'Chuyện này không có trong dự báo.')),
]

# The lines prompt 22 changed (the others keep their hand-localised words in CampaignText.cs).
_FRESH_GENERAL = {('varga', 1), ('varga', 2), ('varga', 3), ('kessler', 3), ('sen', 1), ('sen', 2), ('hung', 1), ('hung', 3), ('hung', 'defeat'), ('aurel', 2)}
for gid, deck, supports, style, stance, taunts, defeat in GENERALS:
    for i, (en, vi) in enumerate(taunts):
        T(f'radio.{gid}.taunt.{i + 1}', en, vi, fresh=(gid, i + 1) in _FRESH_GENERAL)
    T(f'radio.{gid}.defeat', *defeat, fresh=(gid, 'defeat') in _FRESH_GENERAL)

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
     ('Varga\'s land battleship: a main gun that kills a tank a shot, escorts that follow it into battle and a hull that shrugs off most of what the brigade fires. Mara says the rear plates are its weakness.',
      'Chiến hạm mặt đất của Varga: pháo chính mỗi phát hạ một xe tăng, đội hộ tống bám theo vào trận và lớp vỏ chịu được gần hết hỏa lực của lữ đoàn. Mara nói các tấm giáp phía sau là điểm yếu của nó.')),
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
     ('Venn\'s drone fortress: no main gun, just racks that launch swarm after swarm, a SAM battery and flak. Deadly to aircraft; tanks and artillery break it.',
      'Pháo đài drone của Venn: không có pháo chính, chỉ có các giàn phóng hết bầy này tới bầy khác, một dàn tên lửa phòng không và pháo cao xạ. Cực nguy hiểm với máy bay; xe tăng và pháo binh mới hạ được nó.')),
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
     ('Raven\'s flying headquarters over Skyhold: radar, missiles and a hangar for drones. It directs every Hegemon aircraft on the coast.',
      'Sở chỉ huy bay của Raven trên Skyhold: radar, tên lửa và một khoang chứa drone. Nó điều khiển mọi máy bay Hegemon trên Meridian Coast.')),
    ('nuke_train', ('Nemesis', 'Nemesis'),
     ('A missile train crossing Metro City to its launch site. When it gets there, the countdown starts. Do not let it get there.',
      'Một đoàn tàu tên lửa đang băng qua Metro City tới bãi phóng. Tới nơi là đếm ngược bắt đầu. Đừng để nó tới nơi.')),
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
     ('A small carrier from Venn\'s drone programme. Aurel kept building them after she left.',
      'Một tàu mang drone cỡ nhỏ trong chương trình drone của Venn. Aurel vẫn cho đóng tiếp sau khi bà bỏ đi.')),
    ('behemoth_mk2', ('Behemoth Mk.II · Upgraded Behemoth', 'Behemoth Mk.II · Behemoth nâng cấp'),
     ('Varga\'s Behemoth rebuilt after its first defeat: heavier, heated for the winter, and angrier.',
      'Chiếc Behemoth của Varga dựng lại sau lần bại trận đầu tiên: nặng hơn, lắp hệ sưởi cho mùa đông, và hung hãn hơn.')),
    ('moloch', ('Moloch · Mobile factory', 'Moloch · Nhà máy di động'),
     ('Varga\'s mobile factory: it builds tanks as it rolls and sends them out of its doors into battle.',
      'Nhà máy di động của Varga: vừa lăn bánh vừa đóng xe tăng, rồi tung chúng ra trận qua các cửa thả.')),
    ('kronos', ('Kronos · Mining excavator', 'Kronos · Máy xúc mỏ'),
     ('A bucket-wheel excavator the size of a building, armoured by Thorne and pointed at the brigade.',
      'Một máy xúc bánh gầu to bằng cả tòa nhà, được Thorne bọc thép và chĩa thẳng vào lữ đoàn.')),
    ('ixion', ('Ixion · Giant wheeled vehicle', 'Ixion · Xe bánh khổng lồ'),
     ('A war machine on two spiked wheels taller than a house, a roller of spikes across its front, built from mine machinery to batter through walls.',
      'Một cỗ máy chiến tranh trên hai bánh gai cao hơn nhà, phía trước là trục lăn đầy gai, đóng từ máy móc hầm mỏ để phá tường.')),
    ('typhon', ('Typhon · Missile submarine', 'Typhon · Tàu ngầm tên lửa'),
     ('Kessler\'s missile submarine, now Thorne\'s: it surfaces, fires a salvo and dives again.',
      'Tàu ngầm tên lửa của Kessler, giờ trong tay Thorne: nổi lên, phóng một loạt rồi lại lặn.')),
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

# Prompt 22 E: the two new mini bosses (P22-content builds their defs; the campaign fights them as their fallbacks until then).
BOSS_FILES += [
    ('behemoth_mk0', ('Behemoth Mk.0 · Prototype Behemoth', 'Behemoth Mk.0 · Behemoth nguyên mẫu'),
     ('The first Behemoth ever built, drawn by a young engineer called Mara Lind and finished by Varga. Slower, thinner and older than its sons, '
      'and still guarding the Foundry where it was born.',
      'Chiếc Behemoth đầu tiên từng được chế tạo, do một kỹ sư trẻ tên Mara Lind vẽ và Varga hoàn thiện. Chậm hơn, mỏng hơn và già hơn những đứa con của nó, '
      'và vẫn canh giữ Foundry nơi nó ra đời.')),
    ('morrigan', ('Morrigan · Raven\'s Fighter', 'Morrigan · Tiêm kích của Raven'),
     ('Wolff\'s own fighter, built for him alone: fast, hard to see on radar, with air-to-air missiles and guided bombs. '
      'Its big attack is a salvo of both at our aircraft and anti-air vehicles. Watch for the warning, and break it.',
      'Chiếc tiêm kích riêng của Wolff, làm cho một mình hắn: nhanh, khó thấy trên radar, mang tên lửa không đối không và bom dẫn đường. '
      'Đòn lớn của nó là một loạt cả hai thứ nhắm vào máy bay và xe phòng không của ta. Để ý cảnh báo, và ngắt nó.')),
]

for key, name, text in BOSS_FILES:
    T(f'boss.{key}', *name, fresh=key in ('behemoth_mk0', 'morrigan'))
    T(f'bossfile.{key}', *text, fresh=key in ('behemoth_mk0', 'morrigan'))

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
# radio.betrayal lives in Strings.cs (prompt 21 moved it there; the Sim sends it by key).
T('radio.bossFled', 'It is breaking off! Let it go, we have what we came for.', 'Nó đang tháo chạy! Để nó đi, ta đạt được mục tiêu rồi.')
T('radio.alliedStrikes', 'Hawk here: the air corridor is open. Strikes on call, every minute.', 'Hawk đây: hành lang bay đã mở. Không kích theo yêu cầu, mỗi phút một lượt.')
T('radio.enemyWeakened', 'Their supply is burning. They will feel that for the rest of the day.', 'Kho tiếp tế của chúng đang cháy. Cả ngày hôm nay chúng sẽ thấm đòn.')

# Speakers' names on the radio panel.
SPEAKERS = ['khai', 'mai', 'dieuhau', 'linh', 'hung', 'brandt', 'varga', 'orlov', 'kessler', 'sen', 'quaden', 'aurel', 'hq',
            'brenn', 'adler', 'mendez', 'dahl', 'varro', 'quist', 'reyn', 'okoye']

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
                     'Cuộc chiến chưa kết thúc. Hegemon vẫn giữ phần còn lại của Meridian Coast, và lữ đoàn đang chuẩn bị cho những gì sắp tới. '
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

# Prompt 22 B: an interlude on the screens ("Interlude II", "II-3"); a chapter's name is filled in, so the kickers take it whole.
UI22 = {
    'campaign.chapterName': ('Chapter {chapter}', 'Chương {chapter}'),
    'campaign.interludeName': ('Interlude {interlude}', 'Chương xen kẽ {interlude}'),
    'campaign.chapterKicker': ('{act} · {chapter}', '{act} · {chapter}'),
    'campaign.missionKicker': ('{chapter} · Mission {mission} · {map}', '{chapter} · Nhiệm vụ {mission} · {map}'),
}
for key, (en, vi) in UI22.items():
    T(key, en, vi, fresh=True)

# Prompt 22: the keys this file marks fresh (act5.py tells them from the ones prompt 20 marked, which prompt 21 localised by hand).
import campaign_kit as _kit  # noqa: E402
_kit.STORY_FRESH = set(_kit.FRESH)

"""Prompt 22 D: the words and the data of the story's mechanics, outside the missions (DECISIONS 22D).

    python Tools/campaign/narrative.py

Writes Scripts/Game/Hud/StoryText.cs (the texts, English and Vietnamese) and Scripts/Game/Match/Narrative.Data.cs
(what the Game layer needs to know about them): the intel files and where each is recovered (D.7, the clues about
Thorne among them, D.2), the comic panels after every chapter and interlude (D.8), the characters' arcs and their
payoff missions (D.3), the story loot's reasons (D.6), the story choices' words (D.5; their missions are act9.py's),
the reactive radio of every enemy general (D.4) and the front map's and dossier's labels (D.1).

A radio line is at most 100 characters in both languages, like the campaign's (Prompt22StoryTests). The texts follow
prompt 21: both languages, named placeholders, proper names as they are (NameText.Kept).
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
TEXT_CS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts', 'Game', 'Hud', 'StoryText.cs')
DATA_CS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Scripts', 'Game', 'Match', 'Narrative.Data.cs')

TEXTS = {}


def T(key, en, vi):
    if key in TEXTS:
        raise SystemExit(f'narrative: {key} twice')
    TEXTS[key] = (en, vi)


# ====================================================================== D.7: intel files (D.2: the clues about Thorne)
# (id, chapter, source: 'side' (win the side mission) or 'stars' (win the mission with three stars), mission, author,
#  a clue about Thorne, title, from, text)
INTEL = [
    ('c1.letter', 1, 'side', 'c1s1', 'hq', False, ('A letter home', 'Thư gửi về nhà'),
     ('A Hegemon private, Stormbeach', 'Một binh nhì Hegemon, Stormbeach'),
     ('Mum, they told us the coast would be quiet work: guard a port, count the ships. Now there are tanks coming out of the '
      'sea and nobody tells us anything. Keep my room as it is.',
      'Mẹ ơi, người ta bảo bờ biển này là việc nhàn: gác cảng, đếm tàu. Giờ thì xe tăng từ dưới biển bò lên mà chẳng ai nói gì '
      'với tụi con cả. Mẹ cứ để phòng con như cũ nhé.')),
    ('c1.inspection', 1, 'stars', 'c1m05', 'brandt', False, ('Inspection report', 'Biên bản kiểm tra'),
     ('Major Brandt, Ashfield', 'Thiếu tá Brandt, Ashfield'),
     ('Bastion Mk.0: plates thinner than drawn, the second gun never fitted. Crew morale good. Request for the missing parts '
      'sent to General Varga for the fourth time. I expect no answer.',
      'Bastion Mk.0: giáp mỏng hơn bản vẽ, khẩu pháo thứ hai chưa bao giờ được lắp. Tinh thần kíp lái tốt. Đã gửi tướng Varga '
      'xin phụ tùng còn thiếu lần thứ tư. Tôi không mong có hồi âm.')),
    ('c2.order', 2, 'side', 'c2s1', 'varga', False, ('Order of the day', 'Nhật lệnh'),
     ('General Viktor Varga, Dunebreak', 'Tướng Viktor Varga, Dunebreak'),
     ('To the Desert Group: the enemy fights for his home. Respect that, and beat him anyway. No well is to be poisoned. Any man '
      'who does will answer to me, not to the Director.',
      'Gửi Cụm Sa mạc: kẻ địch chiến đấu vì nhà cửa của họ. Hãy tôn trọng điều đó, và vẫn phải đánh bại họ. Cấm đầu độc giếng '
      'nước. Kẻ nào làm vậy sẽ phải trả lời trước ta, không phải trước Giám đốc.')),
    ('c2.drawings', 2, 'side', 'c2s2', 'mai', False, ('Mara\'s diary: the first drawings', 'Nhật ký của Mara: những bản vẽ đầu tiên'),
     ('Engineer Mara Lind', 'Kỹ sư Mara Lind'),
     ('I drew the Behemoth to end a war quickly. That was the pitch, and I believed it. Seven years later it ends nothing, and '
      'I am the one who knows where its rear plates are thin.',
      'Tôi vẽ Behemoth để kết thúc chiến tranh cho nhanh. Người ta chào hàng như thế, và tôi đã tin. Bảy năm sau nó chẳng kết '
      'thúc được gì, còn tôi là người biết giáp sau của nó mỏng ở đâu.')),
    ('c3.tables', 3, 'side', 'c3s1', 'orlov', False, ('Firing tables', 'Bảng bắn'),
     ('Colonel Ilya Orlov, Frostpeak', 'Đại tá Ilya Orlov, Frostpeak'),
     ('Guns 1 to 9 registered on every road out of the pass. Fire only on the radar\'s word. Never twice from the same pit. '
      'Patience is cheaper than shells.',
      'Pháo 1 đến 9 đã ngắm sẵn mọi con đường ra khỏi đèo. Chỉ bắn theo lệnh của radar. Không bao giờ bắn hai lần từ cùng một '
      'hố. Kiên nhẫn rẻ hơn đạn pháo.')),
    ('c3.snow', 3, 'side', 'c3s2', 'hq', False, ('A letter from the pass', 'Thư từ con đèo'),
     ('A Hegemon gunner, Whiteout Pass', 'Một pháo thủ Hegemon, Whiteout Pass'),
     ('The Colonel says the cold is on our side. The cold is on nobody\'s side. Fenrir went out into the storm this morning and '
      'the snow closed behind it like a door.',
      'Đại tá bảo cái lạnh đứng về phía ta. Cái lạnh chẳng đứng về phía ai cả. Sáng nay Fenrir lao vào bão tuyết và tuyết khép '
      'lại sau nó như một cánh cửa.')),
    ('i1.ledger', 13, 'stars', 'i1m02', 'brenn', False, ('Brenn\'s ledger', 'Sổ cái của Brenn'),
     ('Major Otto Brenn', 'Thiếu tá Otto Brenn'),
     ('Page 212: one Behemoth, prototype, its cost carried over from a cancelled contract, signed M. L. The quartermaster '
      'underlined the initials twice and closed the book.',
      'Trang 212: một Behemoth nguyên mẫu, chi phí chuyển từ một hợp đồng đã hủy, ký tên M. L. Người quản lý hậu cần gạch dưới '
      'chữ ký tắt hai lần rồi gấp sổ lại.')),
    ('i1.initials', 13, 'stars', 'i1m03', 'mai', False, ('Mara\'s diary: initials', 'Nhật ký của Mara: chữ ký tắt'),
     ('Engineer Mara Lind', 'Kỹ sư Mara Lind'),
     ('They left my initials on the hull. Maybe it was spite, maybe pride. I scratched them off with a screwdriver while Kade '
      'pretended not to watch.',
      'Họ để nguyên chữ ký tắt của tôi trên thân xe. Có thể vì hằn học, có thể vì tự hào. Tôi cạo nó đi bằng tua vít trong lúc '
      'Kade giả vờ không nhìn.')),
    ('c4.prisoner', 4, 'side', 'c4s1', 'hq', False, ('A note from the train', 'Mẩu giấy trên tàu'),
     ('A prisoner, Rust Yard', 'Một tù nhân, Rust Yard'),
     ('If you find this, we are in the third wagon. They feed us once a day and count us twice. Tell my sister I did not sign '
      'anything.',
      'Nếu ai thấy mẩu giấy này, chúng tôi ở toa thứ ba. Chúng cho ăn một lần một ngày và điểm danh hai lần. Nhắn em gái tôi '
      'là tôi không ký gì cả.')),
    ('c4.balance', 4, 'side', 'c4s2', 'kessler', False, ('The balance sheet', 'Bảng cân đối'),
     ('Admiral Magnus Kessler, Iron Harbor', 'Đô đốc Magnus Kessler, Iron Harbor'),
     ('Harbour losses this quarter within tolerance. Recommend we stop repairing the docks and let the Accord inherit the cost. '
      'A port is an asset until it is a liability.',
      'Tổn thất cảng quý này trong mức cho phép. Đề nghị ngừng sửa bến và để Accord gánh chi phí. Một hải cảng là tài sản cho '
      'tới khi nó thành gánh nặng.')),
    ('c4.flank', 4, 'stars', 'c4m13', 'linh', True, ('Movement order, Thorne\'s column', 'Lệnh hành quân, đoàn xe của Thorne'),
     ('Intercepted by Captain Nadia Kerr', 'Đại úy Nadia Kerr chặn được'),
     ('Column to move at 06:00 and cover the brigade\'s left. Overwritten at 05:40 by Thorne\'s own HQ: hold in place, fuel '
      'shortage. The fuel depot\'s log shows full tanks.',
      'Đoàn xe xuất phát lúc 06:00 để che sườn trái của lữ đoàn. Lúc 05:40 bị chính sở chỉ huy của Thorne ghi đè: giữ nguyên vị '
      'trí, thiếu nhiên liệu. Sổ kho xăng ghi các bồn vẫn đầy.')),
    ('c5.notebook', 5, 'side', 'c5s1', 'sen', False, ('Venn\'s notes: the swarm', 'Ghi chép của Venn: bầy drone'),
     ('Dr Elara Venn', 'Tiến sĩ Elara Venn'),
     ('A swarm can search a collapsed building in four minutes. I built it for earthquakes. The board asked how many warheads '
      'it could carry. I should have left then.',
      'Một bầy drone có thể lục soát một tòa nhà sập trong bốn phút. Tôi làm ra nó cho những trận động đất. Hội đồng hỏi nó mang '
      'được bao nhiêu đầu đạn. Lẽ ra tôi phải đi ngay lúc đó.')),
    ('c5.village', 5, 'side', 'c5s2', 'hq', False, ('A letter from the canopy', 'Thư từ rừng sâu'),
     ('The charcoal burners, Jungle Pass', 'Những người đốt than, Jungle Pass'),
     ('The drones fly over us every night and never fire. We think they are counting us. The children have started waving '
      'at them.',
      'Đêm nào drone cũng bay qua đầu mà không bắn. Chúng tôi nghĩ chúng đang đếm người. Bọn trẻ bắt đầu vẫy tay chào chúng.')),
    ('c5.titan', 5, 'stars', 'c5m09', 'linh', True, ('Signal log: Titan', 'Nhật ký tín hiệu: Titan'),
     ('Captain Nadia Kerr', 'Đại úy Nadia Kerr'),
     ('Venn\'s hangars logged six calls from a station signing as Titan, the Accord\'s call sign for General Thorne. The calls '
      'came on our frequencies, at hours our own logs show as silent.',
      'Nhà chứa của Venn ghi lại sáu cuộc gọi từ một trạm ký tên Titan, mật danh của Accord dành cho tướng Thorne. Các cuộc gọi '
      'đến trên tần số của ta, vào những giờ sổ trực của ta ghi là im lặng.')),
    ('c6.raiders', 6, 'side', 'c6s1', 'hq', False, ('A letter from the dam', 'Thư từ con đập'),
     ('A Hegemon driver, Hollow Dam', 'Một lính lái xe Hegemon, Hollow Dam'),
     ('General Varga came down to the vehicle park himself and asked our names. Twenty years in, and nobody from the top ever '
      'did that. We will hold this dam for him.',
      'Tướng Varga đích thân xuống bãi xe và hỏi tên từng người. Hai mươi năm quân ngũ, chưa ai ở trên làm vậy. Tụi tôi sẽ giữ '
      'con đập này vì ông ấy.')),
    ('c6.board', 6, 'side', 'c6s2', 'aurel', False, ('Report to the board', 'Báo cáo gửi hội đồng'),
     ('Director Lucien Aurel', 'Giám đốc Lucien Aurel'),
     ('The Varga counterstrike buys Project Icarus four months. The general believes he is winning a war. He is buying time '
      'for the only weapon that matters.',
      'Cuộc phản công của Varga mua cho Dự án Icarus bốn tháng. Vị tướng tin rằng ông ta đang thắng một cuộc chiến. Thực ra ông '
      'ta chỉ đang câu giờ cho thứ vũ khí duy nhất đáng kể.')),
    ('c6.band', 6, 'stars', 'c6m15', 'linh', True, ('Signal log: Hollow Dam', 'Nhật ký tín hiệu: Hollow Dam'),
     ('Captain Nadia Kerr', 'Đại úy Nadia Kerr'),
     ('For one hour on the night before the dam, Thorne\'s HQ transmitter worked on a Hegemon band. In the same hour Varga\'s '
      'guns fell silent. I have told no one yet. I want to be wrong.',
      'Trong một tiếng đêm trước trận đập, máy phát của sở chỉ huy Thorne chạy trên băng tần của Hegemon. Đúng tiếng ấy pháo '
      'của Varga im bặt. Tôi chưa nói với ai. Tôi muốn mình sai.')),
    ('i2.escort', 14, 'stars', 'i2m02', 'mendez', False, ('Escort log', 'Nhật ký hộ tống'),
     ('Captain Kaia Mendez', 'Đại úy Kaia Mendez'),
     ('Package asleep in the third truck, arms round a hard drive. Asked twice whether we would hand her to the Accord\'s '
      'courts. I said I drive, I do not judge.',
      'Người cần hộ tống ngủ ở thùng xe thứ ba, ôm khư khư một ổ cứng. Hỏi hai lần liệu chúng tôi có giao cô ấy cho tòa án của '
      'Accord không. Tôi bảo tôi chỉ lái xe, không phán xử.')),
    ('i2.stay', 14, 'stars', 'i2m04', 'sen', False, ('Venn\'s notes: why I stayed', 'Ghi chép của Venn: vì sao tôi ở lại'),
     ('Dr Elara Venn', 'Tiến sĩ Elara Venn'),
     ('They could have left me at the border with a car and papers. Instead the brigade\'s engineer asked me to help her take '
      'my machines apart. Nobody had ever asked me to take anything apart.',
      'Họ có thể để tôi lại ở biên giới với một chiếc xe và giấy tờ. Thay vào đó, kỹ sư của lữ đoàn nhờ tôi giúp tháo dỡ những '
      'cỗ máy của chính tôi. Chưa ai từng nhờ tôi tháo dỡ thứ gì.')),
    ('c7.letters', 7, 'side', 'c7s1', 'hq', False, ('Letters from Veyra', 'Những lá thư từ Veyra'),
     ('The post office, Veyra', 'Bưu điện Veyra'),
     ('Two years of letters that were never delivered, sorted by street. The brigade\'s drivers took them round in the '
      'evenings. Some doors had no one left to open them.',
      'Thư từ suốt hai năm chưa từng được phát, xếp theo từng con phố. Lính lái xe của lữ đoàn đi phát vào mỗi buổi tối. Có '
      'những cánh cửa không còn ai để mở.')),
    ('c7.turn', 7, 'stars', 'c7m10', 'linh', False, ('Nadia\'s report: the turn', 'Báo cáo của Nadia: cú phản bội'),
     ('Captain Nadia Kerr', 'Đại úy Nadia Kerr'),
     ('At 14:02 Thorne\'s base turned its guns inward. I had the file for six weeks: the column, Titan, the dam. I should have '
      'sent it after the second clue. I will not wait again.',
      'Lúc 14:02 căn cứ của Thorne quay nòng pháo vào trong. Tôi đã giữ hồ sơ suốt sáu tuần: đoàn xe, Titan, con đập. Lẽ ra tôi '
      'phải gửi nó sau manh mối thứ hai. Tôi sẽ không chờ nữa.')),
    ('c8.fortress', 8, 'side', 'c8s1', 'mai', False, ('Mara\'s diary: the fortress below', 'Nhật ký của Mara: pháo đài dưới lòng đất'),
     ('Engineer Mara Lind', 'Kỹ sư Mara Lind'),
     ('The survey maps show tunnels cut for something wide and heavy, and bunkers facing up, not out. This is not a mine. It '
      'is a shelter, for when the sky starts falling.',
      'Bản đồ khảo sát cho thấy đường hầm được đào cho một thứ vừa rộng vừa nặng, và những hầm ngầm hướng lên trời chứ không '
      'hướng ra ngoài. Đây không phải mỏ. Đây là chỗ trú ẩn, cho lúc bầu trời bắt đầu sụp xuống.')),
    ('c8.letter', 8, 'side', 'c8s2', 'hung', False, ('Thorne\'s letter', 'Thư của Thorne'),
     ('General Roland Thorne, to Director Aurel', 'Tướng Roland Thorne, gửi Giám đốc Aurel'),
     ('You promised me the coast when Icarus flies. I have kept my part: the Accord\'s best army is out of your way. Keep '
      'yours, or I will find out what your satellites cost to shoot down.',
      'Ông đã hứa trao dải bờ biển cho tôi khi Icarus cất cánh. Tôi đã làm xong phần mình: đạo quân giỏi nhất của Accord đã '
      'tránh khỏi đường ông. Hãy giữ lời, không thì tôi sẽ tìm hiểu bắn hạ vệ tinh của ông tốn bao nhiêu.')),
    ('c9.timetable', 9, 'side', 'c9s1', 'kessler', False, ('The last timetable', 'Thời gian biểu cuối cùng'),
     ('Admiral Magnus Kessler', 'Đô đốc Magnus Kessler'),
     ('Minelayers to sail at 02:00, 02:20 and 02:40. Crews to be paid on return. Note: there may be no return. Pay them '
      'anyway; it is good for the others to see.',
      'Tàu rải mìn xuất phát lúc 02:00, 02:20 và 02:40. Trả lương thủy thủ khi quay về. Ghi chú: có thể sẽ không ai quay về. Cứ '
      'trả lương, để những người khác thấy.')),
    ('c9.buoy', 9, 'side', 'c9s2', 'linh', False, ('The second line', 'Dòng thứ hai'),
     ('Captain Nadia Kerr', 'Đại úy Nadia Kerr'),
     ('I ran the buoy\'s message through Thorne\'s old codebooks. Under the coordinates there is a second line, addressed to '
      'nobody: "Still here." The buoy has not answered since.',
      'Tôi giải tin nhắn từ cái phao bằng sổ mật mã cũ của Thorne. Dưới dòng tọa độ còn một dòng thứ hai, không gửi cho ai: '
      '"Vẫn ở đây." Từ đó cái phao không trả lời nữa.')),
    ('i3.log', 15, 'stars', 'i3m01', 'dieuhau', False, ('Hawk\'s flight log', 'Nhật ký bay của Hawk'),
     ('Lieutenant Jonah Reyes', 'Trung úy Jonah Reyes'),
     ('Hit at nine thousand feet, left engine gone. Saw the black fighter turn for a second pass and not come. He wanted me '
      'alive, to hunt. His mistake.',
      'Trúng đạn ở độ cao chín nghìn bộ, động cơ trái hỏng. Thấy chiếc tiêm kích đen quay lại lượt thứ hai rồi không tới. Hắn '
      'muốn tôi sống, để săn. Sai lầm của hắn.')),
    ('i3.crown', 15, 'stars', 'i3m03', 'reyn', False, ('Column orders', 'Lệnh hành quân của đoàn'),
     ('Colonel August Reyn', 'Đại tá August Reyn'),
     ('Crown to all: we bring the pilot home. Nothing else on this road is worth a vehicle. If the ring does not break, we '
      'make it break.',
      'Crown gửi toàn đoàn: ta đưa phi công về nhà. Trên con đường này không có gì khác đáng một chiếc xe. Nếu vòng vây không '
      'vỡ, ta làm cho nó vỡ.')),
    ('c10.home', 10, 'side', 'c10s1', 'quaden', False, ('Raven\'s letter home', 'Thư Raven gửi về nhà'),
     ('Kasimir Wolff', 'Kasimir Wolff'),
     ('The Accord boy is good. Better than his friend was. I will enjoy this one. Tell Father the new fighter turns like a '
      'thought.',
      'Thằng nhóc của Accord khá lắm. Giỏi hơn bạn nó ngày trước. Lần này ta sẽ vui đây. Nói với cha là chiếc tiêm kích mới quay '
      'nhanh như ý nghĩ.')),
    ('c10.test', 10, 'side', 'c10s2', 'aurel', False, ('Report: Icarus Mk.0', 'Báo cáo: Icarus Mk.0'),
     ('Director Lucien Aurel', 'Giám đốc Lucien Aurel'),
     ('Mk.0 flight test complete. Losses to ground fire acceptable. Icarus 01 is ready; 02 and 03 follow on the next launch '
      'windows. The brigade need not know there is more than one.',
      'Hoàn tất bay thử Mk.0. Tổn thất do hỏa lực mặt đất chấp nhận được. Icarus 01 đã sẵn sàng; 02 và 03 sẽ theo ở các khung '
      'phóng kế tiếp. Lữ đoàn không cần biết có nhiều hơn một chiếc.')),
    ('c11.memo', 11, 'side', 'c11s1', 'aurel', False, ('Memo to the board', 'Bản ghi nhớ gửi hội đồng'),
     ('Director Lucien Aurel', 'Giám đốc Lucien Aurel'),
     ('The Skygate Array will be defended to the last contract. After Helion there will be no more contracts, only customers.',
      'Skygate Array sẽ được bảo vệ tới bản hợp đồng cuối cùng. Sau Helion sẽ không còn hợp đồng nào nữa, chỉ còn khách hàng.')),
    ('c11.orlov', 11, 'stars', 'c11m05', 'orlov', False, ('Orlov\'s last letter', 'Lá thư cuối của Orlov'),
     ('Colonel Ilya Orlov', 'Đại tá Ilya Orlov'),
     ('I have lost the war and my gun on the same day. I find I mind the gun more. Winter always comes back, but not for me.',
      'Ta mất cả cuộc chiến lẫn khẩu pháo trong cùng một ngày. Hóa ra ta tiếc khẩu pháo hơn. Mùa đông luôn quay lại, nhưng không '
      'phải cho ta.')),
    ('c12.bargain', 12, 'stars', 'c12m02', 'kessler', False, ('Kessler\'s bargain', 'Cuộc mặc cả của Kessler'),
     ('Admiral Magnus Kessler', 'Đô đốc Magnus Kessler'),
     ('Terms: every ship and missile I have left, for my sailors\' lives. Mine you may keep. I have always known what I am '
      'worth.',
      'Điều kiện: mọi con tàu và tên lửa ta còn lại, đổi lấy mạng sống của thủy thủ. Mạng ta thì cứ giữ lấy. Ta luôn biết mình '
      'đáng giá bao nhiêu.')),
    ('c12.last', 12, 'stars', 'c12m09', 'hq', False, ('The last letter', 'Lá thư cuối'),
     ('A Hegemon private, Dunebreak', 'Một binh nhì Hegemon, Dunebreak'),
     ('They say it ends at Helion, one way or the other. If the sky lights up, don\'t look at it. Put the kettle on. I\'m '
      'coming home.',
      'Người ta bảo mọi chuyện sẽ kết thúc ở Helion, bằng cách này hay cách khác. Nếu bầu trời sáng rực, mẹ đừng nhìn. Mẹ cứ đun '
      'nước đi. Con sắp về rồi.')),
]

for iid, _, _, _, _, _, title, frm, text in INTEL:
    T(f'intel.{iid}.title', *title)
    T(f'intel.{iid}.from', *frm)
    T(f'intel.{iid}.text', *text)

# ====================================================================== D.8: comic panels (placeholders from renders)
# chapter -> [(battlefield art (the first that exists), a render in the panel or None, speaker, line)]
COMICS = {
    1: [('landingbeach', None, 'khai', ('Stormbeach. Three years of occupation, and we came in with the tide.',
                                         'Stormbeach. Ba năm bị chiếm đóng, và ta đổ bộ theo con nước.')),
        ('greenvale', None, 'mai', ('A field base in a day. Don\'t ask me how. Ask me for more steel.',
                                     'Một căn cứ dã chiến trong một ngày. Đừng hỏi tôi làm thế nào. Cứ xin thêm thép cho tôi.')),
        ('ashfield', 'fortress_bastion', 'brandt', ('The Bastion held for a week. You broke it in a morning, Colonel.',
                                                     'Bastion trụ được một tuần. Ông phá nó trong một buổi sáng, đại tá.')),
        ('ashfield', None, 'linh', ('Brandt\'s files. One name on every page: Varga.', 'Hồ sơ của Brandt. Một cái tên trên mọi trang: Varga.'))],
    2: [('dunebreak', None, 'varga', ('A soldier\'s greeting, Colonel. Then a soldier\'s war.',
                                       'Một lời chào của người lính, đại tá. Rồi một cuộc chiến của người lính.')),
        ('redrock', 'behemoth', 'mai', ('I drew that machine. I know where it bleeds.', 'Tôi đã vẽ cỗ máy đó. Tôi biết nó chảy máu ở đâu.')),
        ('redrock', None, 'hung', ('Thorne\'s army on your left. Together nobody stops us, Kade.',
                                    'Quân của Thorne bên cánh trái anh. Cùng nhau thì không ai cản nổi ta, Kade.'))],
    3: [('whiteout', None, 'dieuhau', ('That mark on the Harpy\'s tail. Raven. He shot down my wingman.',
                                        'Dấu hiệu trên đuôi Harpy. Raven. Hắn đã bắn hạ bạn bay của tôi.')),
        ('frostpeak', 'mobile_fortress', 'orlov', ('Winter always comes back, Colonel.', 'Mùa đông luôn quay lại, đại tá.')),
        ('frostpeak', None, 'khai', ('The pass is open. Next stop, the sea.', 'Con đèo đã mở. Điểm dừng tiếp theo: biển.'))],
    13: [('foundry|rustyard', None, 'brenn', ('Every bolt Hegemon ever bought is written down in here.',
                                               'Mọi con bu lông Hegemon từng mua đều được ghi trong này.')),
         ('foundry|rustyard', 'behemoth', 'mai', ('M. L. My initials. On the first one they ever built.',
                                                   'M. L. Chữ ký tắt của tôi. Trên chiếc đầu tiên họ từng chế tạo.')),
         ('foundry|rustyard', None, 'khai', ('We take the drawings. They build no more of these here.',
                                              'Ta mang bản vẽ đi. Ở đây chúng sẽ không chế tạo thêm chiếc nào nữa.'))],
    4: [('ironport', 'behemoth_tempest', 'adler', ('The port is ours. Tempest\'s gun came out of the water in one piece.',
                                                    'Cảng là của ta. Khẩu pháo của Tempest được vớt lên còn nguyên.')),
        ('lighthousebay', 'leviathan', 'kessler', ('A fleet is a line in a ledger, Colonel. You have closed mine.',
                                                    'Hạm đội chỉ là một dòng trong sổ sách, đại tá. Ngươi vừa khóa sổ của ta.')),
        ('rustyard', None, 'linh', ('Thorne\'s column never came. Again. I\'m starting a file.',
                                     'Đoàn xe của Thorne lại không tới. Lại nữa. Tôi bắt đầu lập hồ sơ.'))],
    5: [('junglepass', None, 'sen', ('I built the swarm to find people under rubble.', 'Tôi tạo ra bầy drone để tìm người dưới đống đổ nát.')),
        ('emberridge', 'drone_mothership', 'khai', ('Matriarch is down. The woman who built her is walking towards us.',
                                                     'Matriarch đã rơi. Người tạo ra nó đang bước về phía ta.')),
        ('emberridge', None, 'sen', ('Here is the Icarus drive. Stop him before he finishes it.',
                                      'Đây là bộ đẩy của Icarus. Hãy chặn ông ta trước khi ông ta hoàn thành nó.'))],
    6: [('hydrodam', None, 'varga', ('One hour of ceasefire, Colonel. For the wounded. Then we are enemies again.',
                                      'Một giờ ngừng bắn, đại tá. Cho những người bị thương. Rồi ta lại là kẻ thù.')),
        ('hydrodam', 'moloch', 'brandt', ('Moloch\'s factory floor, still warm. My walls held, Colonel.',
                                           'Sàn xưởng của Moloch vẫn còn ấm. Tường của tôi đã trụ vững, đại tá.')),
        ('hydrodam', None, 'linh', ('Thorne was late again. I can\'t call it luck any more.',
                                     'Thorne lại tới muộn. Tôi không thể gọi đó là may rủi được nữa.'))],
    14: [('swamp', None, 'mendez', ('Keep your head down, Doctor. Mirewood bites.', 'Cúi đầu xuống, tiến sĩ. Mirewood cắn người đấy.')),
         ('borderbridge', None, 'sen', ('The border is right there. I could just drive across.',
                                         'Biên giới ở ngay đó. Tôi có thể lái xe qua là xong.')),
         ('borderbridge', None, 'sen', ('No. I stay. I built these machines. I\'ll help take them apart.',
                                         'Không. Tôi ở lại. Tôi đã tạo ra những cỗ máy này. Tôi sẽ giúp tháo dỡ chúng.'))],
    7: [('metrocity', None, 'khai', ('Veyra. The capital. The whole Accord is watching.', 'Veyra. Thủ đô. Cả Accord đang dõi theo.')),
        ('capital', 'behemoth_mk2', 'linh', ('Thorne\'s base just turned its guns on us. I saw it first.',
                                                 'Căn cứ của Thorne vừa quay pháo vào ta. Tôi thấy trước tiên.')),
        ('capital', None, 'hung', ('Have you seen what they are about to launch, Kade? I have.',
                                    'Anh đã thấy thứ họ sắp phóng lên chưa, Kade? Tôi thì thấy rồi.')),
        ('capital', 'nuke_train', 'khai', ('Veyra is free. A third of the army walked out with him.',
                                            'Veyra đã tự do. Một phần ba quân đội đã theo hắn bỏ đi.'))],
    8: [('openpit', None, 'varro', ('The miners know every tunnel. Thorne only knows the maps.',
                                     'Thợ mỏ thuộc từng đường hầm. Thorne chỉ biết bản đồ.')),
        ('openpit', 'earth_borer', 'mai', ('Something is tunnelling down here, waiting for the sky to fall.', 'Có thứ gì đó đang đào hầm dưới này, chờ bầu trời sụp xuống.')),
        ('openpit', None, 'khai', ('Tartarus stopped short of our base. Thorne is running for the sea.',
                                    'Tartarus dừng lại ngay trước căn cứ của ta. Thorne đang chạy ra biển.'))],
    9: [('coralisles', None, 'sen', ('His buoys are listening. So now am I.', 'Phao của hắn đang nghe lén. Giờ tôi cũng vậy.')),
        ('lighthousebay', 'typhon', 'hung', ('Don\'t let me have been right.', 'Đừng để tôi đã đúng.')),
        ('lighthousebay', None, 'linh', ('No body in the wreck. Just a message, four minutes later.',
                                          'Không có xác người trong xác tàu. Chỉ có một tin nhắn, bốn phút sau.'))],
    15: [('frostpeak', None, 'dieuhau', ('Down behind the lines. Raven is circling. Waiting.',
                                          'Rơi sau phòng tuyến địch. Raven đang lượn vòng. Chờ đợi.')),
         ('junglepass', None, 'reyn', ('Crown\'s column. We came for our pilot.', 'Đoàn xe Crown. Chúng tôi tới đón phi công của mình.')),
         ('frostpeak', None, 'dieuhau', ('Home. Give me a jet. This isn\'t over.', 'Về nhà rồi. Cho tôi một chiếc máy bay. Chuyện này chưa xong đâu.'))],
    10: [('skyhold', None, 'quaden', ('Just you and me, Hawk. No ground fire, no excuses.',
                                       'Chỉ còn ta với ngươi, Hawk. Không hỏa lực mặt đất, không viện cớ.')),
         ('skyhold', 'command_airship', 'dieuhau', ('That one was for you, old friend.', 'Phát đó là cho cậu, bạn cũ.')),
         ('skyhold', None, 'khai', ('Skyhold is ours. The sky is next.', 'Skyhold là của ta. Tiếp theo là bầu trời.'))],
    11: [('rustyard', None, 'aurel', ('For the record: our first satellite reached orbit this morning.',
                                       'Xin thông báo: vệ tinh đầu tiên của chúng tôi đã lên quỹ đạo sáng nay.')),
         ('orbitalgate', 'daedalus', 'mai', ('Their guidance computer. With this I can tell where Icarus will be.',
                                              'Máy tính dẫn đường của chúng. Có nó, tôi biết Icarus sẽ ở đâu.')),
         ('orbitalgate', None, 'khai', ('The Array has fallen. Helion is all that\'s left.', 'Skygate đã thất thủ. Chỉ còn lại Helion.'))],
    12: [('launchsite', None, 'varga', ('Like soldiers, Colonel. To the end.', 'Như những người lính, đại tá. Tới cùng.')),
         ('launchsite', 'behemoth', 'mai', ('Matilda, forward. One last time.', 'Matilda, tiến lên. Lần cuối cùng.')),
         ('launchsite', 'silver_bug', 'aurel', ('They still don\'t understand.', 'Họ vẫn chưa hiểu.')),
         ('launchsite', None, 'khai', ('It\'s over. Three years. Take us home.', 'Kết thúc rồi. Ba năm. Đưa chúng ta về nhà.'))],
}

for chapter, panels in COMICS.items():
    for i, (_, _, _, line) in enumerate(panels):
        T(f'comic.{chapter}.{i + 1}', *line)

# ====================================================================== D.3: arcs and their payoff missions
# character -> (title, [(mission, payoff, line)])
ARCS = {
    'mai': (('Mara\'s story', 'Câu chuyện của Mara'), [
        ('c1m04', False, ('Builds the brigade\'s first field base in a day.', 'Dựng căn cứ dã chiến đầu tiên của lữ đoàn trong một ngày.')),
        ('c2m05', False, ('Knows Inferno\'s cooling line: she drew it.', 'Nhận ra đường ống làm mát của Inferno: chính bà đã vẽ nó.')),
        ('c2m11', False, ('Tells Kade she designed Hegemon\'s first Behemoth.', 'Kể với Kade rằng bà đã thiết kế chiếc Behemoth đầu tiên của Hegemon.')),
        ('i1m03', False, ('Finds her initials on Behemoth Mk.0.', 'Tìm thấy chữ ký tắt của mình trên Behemoth Mk.0.')),
        ('c6m03', False, ('Restarts a captured Behemoth: Matilda.', 'Khởi động lại một chiếc Behemoth bắt được: Matilda.')),
        ('c11m11', False, ('Takes the guidance computer that tracks Icarus.', 'Lấy được máy tính dẫn đường theo dõi Icarus.')),
        ('c12m10', True, ('Her Behemoth fights beside the brigade at Helion.', 'Chiếc Behemoth của bà chiến đấu cùng lữ đoàn ở Helion.'))]),
    'dieuhau': (('Hawk\'s story', 'Câu chuyện của Hawk'), [
        ('c3m05', False, ('Knows Raven\'s mark: Raven shot down his wingman.', 'Nhận ra dấu hiệu của Raven: kẻ đã bắn hạ bạn bay của anh.')),
        ('i3m01', False, ('Shot down behind the lines.', 'Bị bắn rơi sau phòng tuyến địch.')),
        ('i3m04', False, ('Brought home over Frostpeak.', 'Được đưa về nhà qua Frostpeak.')),
        ('c10m12', True, ('The duel with Raven over Skyhold.', 'Trận đấu tay đôi với Raven trên bầu trời Skyhold.')),
        ('c10m10', False, ('The last shot at Roc: "That one was for you, old friend."', 'Phát bắn cuối vào Roc: "Phát đó là cho cậu, bạn cũ."'))]),
    'linh': (('Nadia\'s story', 'Câu chuyện của Nadia'), [
        ('c1m10', False, ('Counts Brandt\'s files and finds Varga.', 'Đếm hồ sơ của Brandt và tìm ra Varga.')),
        ('c4m13', False, ('Notices that Thorne\'s column never came.', 'Để ý rằng đoàn xe của Thorne không bao giờ tới.')),
        ('c5m09', False, ('Hears "Titan" in Venn\'s traffic.', 'Nghe thấy "Titan" trong liên lạc của Venn.')),
        ('c6m15', False, ('Finds Thorne\'s HQ on a Hegemon band.', 'Phát hiện sở chỉ huy của Thorne trên băng tần Hegemon.')),
        ('c7m10', True, ('Sees Thorne\'s base turn before anyone else.', 'Thấy căn cứ của Thorne trở giáo trước tất cả mọi người.'))]),
    'khai': (('Kade\'s story', 'Câu chuyện của Kade'), [
        ('c1m01', False, ('Leads the landing at Stormbeach.', 'Chỉ huy cuộc đổ bộ ở Stormbeach.')),
        ('c6m14', False, ('Talks with Varga during the ceasefire.', 'Nói chuyện với Varga trong giờ ngừng bắn.')),
        ('c7m10', False, ('Frees Veyra and loses a third of the army to Thorne.', 'Giải phóng Veyra và mất một phần ba quân đội vào tay Thorne.')),
        ('c12m10', True, ('Brings Icarus down, then turns down a seat in the government.', 'Hạ Icarus, rồi từ chối một ghế trong chính phủ.'))]),
    'varga': (('Varga\'s story', 'Câu chuyện của Varga'), [
        ('c2m01', False, ('Greets the brigade like a soldier.', 'Chào lữ đoàn như một người lính.')),
        ('c2m11', False, ('Sends the Behemoth at Red Rock.', 'Tung Behemoth vào trận ở Red Rock.')),
        ('c6m14', True, ('The ceasefire: his only talk with Kade.', 'Cuộc ngừng bắn: lần duy nhất ông nói chuyện với Kade.')),
        ('c12m10', True, ('Falls like a soldier at Helion.', 'Ngã xuống như một người lính ở Helion.'))]),
}

for who, (title, beats) in ARCS.items():
    T(f'arc.{who}.title', *title)
    for mid, _, line in beats:
        T(f'arc.{who}.{mid}', *line)

# ====================================================================== D.6: story loot (act9.SWAPS moves the cards)
LOOT = [
    ('railgun_truck', 'c4m10', ('Tempest\'s rail gun came out of the wreck whole; Mara built a truck round it.',
                                'Pháo điện từ của Tempest được vớt lên nguyên vẹn; Mara dựng cả một chiếc xe quanh nó.')),
    ('swarm_carrier', 'c5m10', ('Venn came over with the plans for her drone mothership, and the Accord built it.',
                                'Venn mang theo bản vẽ máy bay mẹ thả drone của bà khi đào ngũ, và Accord đã chế tạo nó.')),
    ('cruise_missile', 'c12m02', ('Kessler\'s last bargain: his cruise missiles, for his sailors\' lives.',
                                  'Cuộc mặc cả cuối cùng của Kessler: tên lửa hành trình của hắn, đổi lấy mạng sống thủy thủ.')),
]
for card, _, line in LOOT:
    T(f'loot.{card}', *line)

# ====================================================================== D.5: the choices' words (their missions: act9.py)
CHOICES = [
    ('c4.pursuit', 'linh', ('Kessler Runs', 'Kessler bỏ chạy'),
     ('Kessler is racing for the sea with his staff and his charts of the coast. Three ferries full of families are still tied '
      'up under his rearguard\'s guns. There is time for one of them, Colonel.',
      'Kessler đang lao ra biển cùng bộ tham mưu và hải đồ của cả dải bờ biển. Ba chiếc phà đầy các gia đình vẫn còn neo dưới '
      'họng pháo của đội đoạn hậu. Chỉ kịp lo một việc thôi, đại tá.'),
     [('sea', ('Chase Kessler', 'Đuổi theo Kessler'),
       ('Last Boats: catch his staff cars on the quays. Pays more coins.',
        'Những chuyến tàu cuối: chặn xe tham mưu trên cầu tàu. Nhận nhiều xu hơn.')),
      ('harbour', ('Save the ferries', 'Cứu những chuyến phà'),
       ('Harbour Lights: hold the terminal until the ferries are out. Pays rare blueprints.',
        'Đèn bến cảng: giữ nhà ga cho tới khi phà ra khơi. Nhận bản thiết kế hiếm.'))]),
    ('c8.miners', 'varro', ('The Miners', 'Những người thợ mỏ'),
     ('Thorne is holding three hundred miners in the pit\'s camps. Or we go straight for Tartarus\'s power line while his '
      'paymaster sits beside it. We can\'t do both before Tartarus moves.',
      'Thorne đang giữ ba trăm thợ mỏ trong các lán trại dưới hố. Hoặc ta đánh thẳng vào đường điện của Tartarus trong lúc viên '
      'quản lương của hắn còn ngồi cạnh đó. Không kịp làm cả hai trước khi Tartarus di chuyển.'),
     [('rescue', ('Free the miners', 'Giải cứu thợ mỏ'),
       ('The Miners of Deepcut: sixty of them join the brigade, +{cp} CP at the start of every chapter 9 battle.',
        'Thợ mỏ Deepcut: sáu mươi người gia nhập lữ đoàn, +{cp} CP khi bắt đầu mỗi trận của chương 9.')),
      ('direct', ('Strike Tartarus', 'Đánh thẳng Tartarus'),
       ('Straight at Tartarus: cut its power and take Thorne\'s pay chest. Pays twice the coins.',
        'Đánh thẳng vào Tartarus: cắt điện và lấy hòm lương của Thorne. Nhận gấp đôi xu.'))]),
    ('c11.radar', 'linh', ('The Array', 'Skygate Array'),
     ('The Skygate Array sees everything from here to Helion. Burn its radar first and Hegemon fights the last battle half '
      'blind. Or take the service road straight to the pads, fast, and be a day ahead.',
      'Skygate Array nhìn thấy mọi thứ từ đây tới Helion. Đốt radar của nó trước và Hegemon sẽ đánh trận cuối trong cảnh nửa '
      'mù. Hoặc đi đường công vụ thẳng tới các bệ phóng, thật nhanh, và đi trước chúng một ngày.'),
     [('radar', ('Blind the radar', 'Làm mù radar'),
       ('Blind the Array: the enemy sees {share}% less in every chapter 12 battle.',
        'Làm mù Skygate: địch nhìn kém đi {share}% trong mọi trận của chương 12.')),
      ('launch', ('Go straight in', 'Đi thẳng vào'),
       ('The Short Road: a fast look at the pads. Pays more coins and rare blueprints.',
        'Đường tắt: trinh sát nhanh các bệ phóng. Nhận thêm xu và bản thiết kế hiếm.'))]),
]
for cid, _, title, body, options in CHOICES:
    T(f'storychoice.{cid}.title', *title)
    T(f'storychoice.{cid}.body', *body)
    for opt, label, info in options:
        T(f'storychoice.{cid}.{opt}', *label)
        T(f'storychoice.{cid}.{opt}.info', *info)

T('storyeffect.c8.miners.rescue', 'Deepcut\'s miners fight with you: +{cp} CP at the start.', 'Thợ mỏ Deepcut chiến đấu cùng ta: +{cp} CP khi bắt đầu.')
T('storyeffect.c11.radar.radar', 'The Skygate Array is dark: the enemy sees {share}% less.', 'Skygate Array đã tắt: địch nhìn kém đi {share}%.')

# ====================================================================== D.4: reactive radio, two lines a moment a general
SITUATIONS = ['fast', 'losses', 'air', 'drones', 'artillery', 'interrupt']
REACT = {
    'brandt': [
        [('Faster than my drills allowed for. Noted, Colonel.', 'Nhanh hơn mọi bài tập của tôi tính tới. Ghi nhận, đại tá.'),
         ('My walls were built for a siege, not a sprint.', 'Tường của tôi xây để chống vây hãm, không phải để chạy nước rút.')],
        [('Your wrecks are piling up at my wall. Walls are patient.', 'Xác xe của ông chất đống dưới chân tường tôi. Tường thì kiên nhẫn lắm.'),
         ('Count your losses, Colonel. I count mine every night.', 'Đếm tổn thất đi, đại tá. Tôi thì đêm nào cũng đếm của mình.')],
        [('Aircraft over my walls. Gunners, look up.', 'Máy bay trên đầu tường thành. Pháo thủ, nhìn lên.'),
         ('You fly over walls you cannot break. Clever.', 'Ông bay qua những bức tường ông không phá nổi. Khôn đấy.')],
        [('Drones in the trenches. Nets up, all of you.', 'Drone trong chiến hào. Tất cả giăng lưới lên.'),
         ('Little machines, big noise. My men have seen worse.', 'Máy nhỏ, tiếng to. Người của tôi từng gặp chuyện tệ hơn.')],
        [('Shells on my walls all day. At least you respect them.', 'Đạn pháo dội vào tường tôi suốt ngày. Ít ra ông cũng nể chúng.'),
         ('Your guns are good. My concrete is better.', 'Pháo của ông tốt. Bê tông của tôi tốt hơn.')],
        [('You broke the shot before it fired. I trained that crew myself.', 'Ông phá phát bắn trước khi nó kịp nổ. Kíp đó do chính tôi huấn luyện.'),
         ('Stopped cold. Reload and try again.', 'Bị chặn đứng. Nạp đạn lại và thử lần nữa.')],
    ],
    'varga': [
        [('Quick work, Colonel. I would have liked a longer fight.', 'Nhanh gọn đấy, đại tá. Ta đã mong một trận dài hơn.'),
         ('You move like my old regiment did. That is a compliment.', 'Ông cơ động như trung đoàn cũ của ta. Đó là lời khen.')],
        [('You are spending men, Colonel. Steel is cheaper.', 'Ông đang tiêu hao người đấy, đại tá. Thép rẻ hơn.'),
         ('Pull your wounded back. I will not fire on them.', 'Rút thương binh của ông về đi. Ta sẽ không bắn vào họ.')],
        [('Planes over the desert. The sand eats engines, Colonel.', 'Máy bay trên sa mạc. Cát ăn động cơ đấy, đại tá.'),
         ('You fight from the sky now. My guns look up too.', 'Giờ ông đánh từ trên trời. Pháo của ta cũng biết ngẩng lên.')],
        [('Drones. Venn\'s toys. I prefer an honest tank.', 'Drone. Đồ chơi của Venn. Ta thích một chiếc xe tăng đàng hoàng hơn.'),
         ('A swarm of little machines. War is getting smaller.', 'Một bầy máy nhỏ. Chiến tranh đang nhỏ lại.')],
        [('Your guns are patient. So am I.', 'Pháo của ông kiên nhẫn. Ta cũng vậy.'),
         ('Shells from far away. Come closer, Colonel.', 'Đạn pháo từ xa. Lại gần hơn đi, đại tá.')],
        [('You broke its stroke. Mara taught you well.', 'Ông bẻ gãy đòn của nó. Mara dạy ông giỏi đấy.'),
         ('Stopped before the shot. The old ways still work.', 'Chặn được trước phát bắn. Cách cũ vẫn hiệu quả.')],
    ],
    'orlov': [
        [('Too fast. My guns never finished ranging.', 'Quá nhanh. Pháo của ta chưa kịp chỉnh tầm.'),
         ('You ran through my winter. It will remember.', 'Ngươi chạy xuyên qua mùa đông của ta. Nó sẽ nhớ.')],
        [('The snow is full of your wrecks. Patience wins.', 'Tuyết đầy xác xe của ngươi. Kiên nhẫn sẽ thắng.'),
         ('Every loss is a lesson. You learn slowly.', 'Mỗi tổn thất là một bài học. Ngươi học chậm quá.')],
        [('Aircraft in my sky. The radar sees them all.', 'Máy bay trên trời của ta. Radar thấy hết.'),
         ('Fly, then. The cold brings down more than guns do.', 'Cứ bay đi. Cái lạnh hạ được nhiều hơn pháo.')],
        [('Small drones freeze, Colonel. Wait for it.', 'Drone nhỏ sẽ đóng băng, đại tá. Cứ chờ xem.'),
         ('Drones in a blizzard. Brave, or foolish.', 'Drone giữa bão tuyết. Dũng cảm, hoặc ngu ngốc.')],
        [('A gunner\'s war. At last, someone who understands.', 'Một cuộc chiến của pháo thủ. Cuối cùng cũng có người hiểu.'),
         ('Counter-battery, all guns. Find his pits.', 'Phản pháo, tất cả các khẩu. Tìm hố pháo của hắn.')],
        [('Fire mission cancelled. Recalculate.', 'Hủy nhiệm vụ bắn. Tính lại.'),
         ('You broke my shot. Nobody breaks my shot.', 'Ngươi phá phát bắn của ta. Chưa ai làm được thế.')],
    ],
    'kessler': [
        [('Quick. Expensive for me. Noted in the ledger.', 'Nhanh. Tốn kém cho ta. Đã ghi vào sổ.'),
         ('You finish early. Time is money, and you are taking mine.', 'Ngươi xong sớm. Thời gian là tiền bạc, và ngươi đang lấy của ta.')],
        [('Your losses are mounting. Can you afford this war?', 'Tổn thất của ngươi đang tăng. Ngươi có kham nổi cuộc chiến này không?'),
         ('A poor exchange rate, Colonel. Poor indeed.', 'Tỷ giá tệ đấy, đại tá. Tệ thật.')],
        [('Aircraft cost more than ships. I checked.', 'Máy bay đắt hơn tàu. Ta đã kiểm tra rồi.'),
         ('Planes over my harbour. Anti-air, earn your pay.', 'Máy bay trên cảng của ta. Phòng không, làm cho xứng đồng lương.')],
        [('Drones: cheap, and plenty of them. I approve.', 'Drone: rẻ, và nhiều. Ta tán thành.'),
         ('A swarm. Venn would send you an invoice for that.', 'Một bầy drone. Venn sẽ gửi hóa đơn cho ngươi đấy.')],
        [('Shelling my docks. Who pays to rebuild them, Colonel?', 'Pháo kích bến cảng của ta. Ai trả tiền xây lại, đại tá?'),
         ('Guns from far off. Safe, and slow. Like a bank.', 'Pháo từ xa. An toàn, và chậm. Như ngân hàng.')],
        [('The salvo is lost. Write it off.', 'Mất loạt đạn rồi. Xóa sổ đi.'),
         ('You broke my broadside. That will cost you.', 'Ngươi phá loạt pháo mạn của ta. Chuyện đó sẽ đắt cho ngươi.')],
    ],
    'sen': [
        [('Faster than my models predicted. Interesting.', 'Nhanh hơn mô hình của tôi dự đoán. Thú vị.'),
         ('You adapt faster than the swarm does. That worries me.', 'Ông thích nghi nhanh hơn bầy drone. Điều đó làm tôi lo.')],
        [('You are losing a lot of machines. Pull back, please.', 'Ông đang mất nhiều xe lắm. Rút lui đi, làm ơn.'),
         ('The swarm counts your losses. I wish it would not.', 'Bầy drone đang đếm tổn thất của ông. Tôi mong nó đừng đếm.')],
        [('Aircraft. The swarm routes around them.', 'Máy bay. Bầy drone đổi hướng tránh chúng.'),
         ('You bring planes to a drone fight. Bold.', 'Ông mang máy bay tới trận đánh drone. Táo bạo đấy.')],
        [('You use drones too. Now we are having a conversation.', 'Ông cũng dùng drone. Giờ ta mới thực sự nói chuyện.'),
         ('Your drones are clumsy. Mine were built to be gentle.', 'Drone của ông vụng về quá. Drone của tôi được tạo ra để nhẹ nhàng.')],
        [('Artillery. Blunt, but the swarm cannot dodge it.', 'Pháo binh. Thô, nhưng bầy drone không né được.'),
         ('Shells through the canopy. The forest is burning, Colonel.', 'Đạn pháo xuyên tán rừng. Khu rừng đang cháy, đại tá.')],
        [('You stopped the launch. Good. I mean... noted.', 'Ông chặn được đợt phóng. Tốt. Ý tôi là... ghi nhận.'),
         ('The swarm lost its signal. You found the weak link.', 'Bầy drone mất tín hiệu. Ông tìm ra mắt xích yếu rồi.')],
    ],
    'hung': [
        [('Fast, Kade. You always were, when it mattered.', 'Nhanh đấy, Kade. Anh luôn nhanh, khi cần.'),
         ('Quick work. You would have made a fine general of mine.', 'Gọn gàng. Anh mà theo tôi thì sẽ là một vị tướng giỏi.')],
        [('You\'re bleeding, Kade. Is the Accord worth it?', 'Anh đang mất máu đấy, Kade. Accord có đáng không?'),
         ('Your losses, not mine. For once.', 'Tổn thất của anh, không phải của tôi. Lần này thôi.')],
        [('Planes. Icarus will own that sky soon. Enjoy it.', 'Máy bay. Chẳng bao lâu nữa Icarus sẽ làm chủ bầu trời đó. Tận hưởng đi.'),
         ('Air cover. I taught you that, Kade.', 'Yểm trợ trên không. Tôi dạy anh chiêu đó đấy, Kade.')],
        [('Venn\'s drones on my lines. So she chose you.', 'Drone của Venn trên phòng tuyến của tôi. Vậy là cô ấy chọn anh.'),
         ('Drones everywhere. You fight like Hegemon now.', 'Drone khắp nơi. Giờ anh đánh như Hegemon rồi đấy.')],
        [('Artillery. Still the careful one, Kade.', 'Pháo binh. Vẫn cẩn thận như xưa, Kade.'),
         ('Dahl\'s guns. I signed his promotion, you know.', 'Pháo của Dahl. Anh biết không, chính tôi ký lệnh thăng chức cho cậu ta.')],
        [('You broke it in time. Of course you did.', 'Anh phá được nó kịp lúc. Tất nhiên rồi.'),
         ('Stopped. You always find the weak point, Kade.', 'Bị chặn rồi. Anh luôn tìm ra điểm yếu, Kade.')],
    ],
    'quaden': [
        [('Quick, Colonel. Too quick to be fun.', 'Nhanh đấy, đại tá. Nhanh quá thì mất vui.'),
         ('Over already? I barely warmed up the engines.', 'Xong rồi à? Ta còn chưa kịp làm nóng động cơ.')],
        [('Burning wrecks everywhere. Beautiful from up here.', 'Xác xe cháy khắp nơi. Nhìn từ trên này đẹp lắm.'),
         ('Your losses make good target practice.', 'Tổn thất của ông là bài tập bắn tốt đấy.')],
        [('More planes for me to shoot. Thank you, Colonel.', 'Thêm máy bay cho ta bắn. Cảm ơn, đại tá.'),
         ('Your pilots are brave. Bravery burns nicely.', 'Phi công của ông dũng cảm. Lòng dũng cảm cháy đẹp lắm.')],
        [('Drones? I do not dogfight toasters.', 'Drone à? Ta không không chiến với lò nướng bánh.'),
         ('A sky full of drones. Clutter.', 'Bầu trời đầy drone. Toàn rác.')],
        [('Guns on the ground. How very old-fashioned.', 'Pháo dưới đất. Thật là cổ lỗ.'),
         ('Shells can\'t climb, Colonel. I can.', 'Đạn pháo không leo lên được, đại tá. Ta thì được.')],
        [('You broke my attack run? Lucky.', 'Ông phá được đợt tấn công của ta ư? May mắn thôi.'),
         ('Missed my window. It will not happen twice.', 'Lỡ thời cơ rồi. Chuyện đó không lặp lại lần hai đâu.')],
    ],
    'aurel': [
        [('Efficient, Colonel. The sky rewards efficiency.', 'Hiệu quả đấy, đại tá. Bầu trời thưởng cho sự hiệu quả.'),
         ('You win quickly. You will lose quickly too.', 'Ông thắng nhanh. Ông cũng sẽ thua nhanh thôi.')],
        [('Your losses are the ground\'s losses. The sky loses nothing.', 'Tổn thất của ông là tổn thất của mặt đất. Bầu trời chẳng mất gì.'),
         ('Count them, Colonel. From orbit they are very small.', 'Đếm đi, đại tá. Nhìn từ quỹ đạo, chúng nhỏ xíu.')],
        [('You reach for the sky. It is already taken.', 'Ông với tay lên trời. Nhưng nó đã có chủ.'),
         ('Aircraft. How quaint, beneath a satellite.', 'Máy bay. Thật cổ kính, dưới một vệ tinh.')],
        [('Venn\'s work, turned against me. She will regret it.', 'Công trình của Venn, quay lại chống tôi. Cô ta sẽ hối hận.'),
         ('Drones. Small ideas. I prefer large ones.', 'Drone. Những ý tưởng nhỏ. Tôi thích ý tưởng lớn hơn.')],
        [('Guns. You fight with the last century\'s tools.', 'Pháo. Ông chiến đấu bằng công cụ của thế kỷ trước.'),
         ('Your shells fall. Mine will fall from much higher.', 'Đạn của ông rơi xuống. Đạn của tôi sẽ rơi từ cao hơn nhiều.')],
        [('A delay. Only a delay.', 'Một sự trì hoãn. Chỉ là trì hoãn thôi.'),
         ('You interrupted the strike. The next will not ask.', 'Ông ngắt được đòn đánh. Đòn tiếp theo sẽ không hỏi ý ông đâu.')],
    ],
}
for general, rows in REACT.items():
    if len(rows) != len(SITUATIONS):
        raise SystemExit(f'narrative: {general} has {len(rows)} moments')
    for situation, lines in zip(SITUATIONS, rows):
        for i, (en, vi) in enumerate(lines):
            if len(en) > 100 or len(vi) > 100:
                raise SystemExit(f'narrative: radio.{general}.react.{situation}.{i + 1} is long')
            T(f'radio.{general}.react.{situation}.{i + 1}', en, vi)

# ====================================================================== D.1 and the dossier: labels
UI = {
    'frontmap.caption': ('The front · {won} of {total} missions won', 'Mặt trận · đã thắng {won}/{total} nhiệm vụ'),
    'frontmap.ours': ('Liberated', 'Đã giải phóng'),
    'frontmap.enemy': ('Hegemon', 'Hegemon'),
    'frontmap.betrayed': ('Thorne\'s army', 'Quân của Thorne'),
    'frontmap.front': ('Front line', 'Chiến tuyến'),
    'frontmap.flag': ('Base taken', 'Căn cứ đã chiếm'),
    'campaign.choose': ('Choose', 'Chọn'),
    'campaign.choiceTag': ('A choice', 'Lựa chọn'),
    'campaign.notTaken': ('Not taken', 'Không chọn'),
    'campaign.notTakenNote': ('You chose the other way here.', 'Bạn đã chọn hướng còn lại ở đây.'),
    'campaign.choiceKicker': ('{chapter} · a choice', '{chapter} · lựa chọn'),
    'campaign.storyLoot': ('Story reward', 'Phần thưởng cốt truyện'),
    'dossier.intel': ('Intel', 'Tình báo'),
    'dossier.intelCount': ('{found} of {total} files recovered. Reading them is up to you.',
                           'Đã thu {found}/{total} tài liệu. Đọc hay không là tùy bạn.'),
    'dossier.intelLocked': ('Classified file', 'Tài liệu mật'),
    'dossier.intelStars': ('Win {mission} with three stars to recover it.', 'Thắng {mission} với ba sao để thu được.'),
    'dossier.intelSide': ('Win the side mission {mission} to recover it.', 'Thắng nhiệm vụ phụ {mission} để thu được.'),
    'dossier.choices': ('Your choices', 'Các lựa chọn của bạn'),
    'dossier.choiceNone': ('No choice made yet.', 'Chưa có lựa chọn nào.'),
    'dossier.arc': ('Story so far', 'Câu chuyện tới giờ'),
    'dossier.payoff': ('Payoff', 'Đền đáp'),
    'dossier.comic': ('Replay the panels', 'Xem lại tranh'),
    'comic.kicker': ('{chapter} · after the battle', '{chapter} · sau trận đánh'),
    'comic.next': ('Next', 'Tiếp'),
    'comic.done': ('Continue', 'Tiếp tục'),
    'comic.skip': ('Skip', 'Bỏ qua'),
    'result.intel': ('Intel file recovered: {title}', 'Thu được tài liệu tình báo: {title}'),
}
for k, (en, vi) in UI.items():
    T(k, en, vi)


# ====================================================================== writing

def cs(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def write():
    lines = ['// Generated by Tools/campaign/narrative.py: edit the script, not this file.',
             'using System.Collections.Generic;', '',
             'namespace MachineBrigade.Game.Hud', '{',
             '    /// <summary>',
             '    /// Prompt 22 D: the texts of the story\'s mechanics (the intel files, the comic panels, the arcs, the story loot, the',
             '    /// choices, the generals\' reactive radio, the front map\'s and the dossier\'s labels), English and Vietnamese.',
             '    /// </summary>',
             '    public static class StoryText', '    {',
             '        public static readonly Dictionary<string, (string en, string vi)> Table = new()', '        {']
    for key in sorted(TEXTS):
        en, vi = TEXTS[key]
        lines.append(f'            [{cs(key)}] = ({cs(en)}, {cs(vi)}),')
    lines += ['        };', '    }', '}', '']
    open(TEXT_CS, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines))

    d = ['// Generated by Tools/campaign/narrative.py: edit the script, not this file.',
         'namespace MachineBrigade.Game.Match', '{',
         '    public static partial class Narrative', '    {',
         '        /// <summary>D.7: every intel file, in the order of play (texts: intel.&lt;id&gt;.title, .from, .text).</summary>',
         '        public static readonly IntelFile[] Intel =', '        {']
    for iid, chapter, kind, mid, author, clue, _, _, _ in INTEL:
        d.append(f'            new({cs(iid)}, {chapter}, {"true" if kind == "stars" else "false"}, {cs(mid)}, {cs(author)}, {"true" if clue else "false"}),')
    d += ['        };', '',
          '        /// <summary>D.8: the comic panels after each chapter and interlude (texts: comic.&lt;chapter&gt;.&lt;n&gt;).</summary>',
          '        public static readonly ComicPanel[] Comics =', '        {']
    for chapter, panels in COMICS.items():
        for i, (art, render, speaker, _) in enumerate(panels):
            d.append(f'            new({chapter}, {i + 1}, {cs(art)}, {cs(render) if render else "null"}, {cs(speaker)}),')
    d += ['        };', '',
          '        /// <summary>D.3: the characters\' arcs, beat by beat (texts: arc.&lt;who&gt;.title, arc.&lt;who&gt;.&lt;mission&gt;).</summary>',
          '        public static readonly ArcBeat[] Arcs =', '        {']
    for who, (_, beats) in ARCS.items():
        for mid, payoff, _ in beats:
            d.append(f'            new({cs(who)}, {cs(mid)}, {"true" if payoff else "false"}),')
    d += ['        };', '',
          '        /// <summary>D.6: the cards the story hands out, and the mission of the beat that does (text: loot.&lt;card&gt;).</summary>',
          '        public static readonly (string card, string mission)[] Loot =', '        {']
    for card, mid, _ in LOOT:
        d.append(f'            ({cs(card)}, {cs(mid)}),')
    d += ['        };', '',
          '        /// <summary>D.5: each story choice, who puts it to the player, and its options in order (texts: storychoice.*).</summary>',
          '        public static readonly (string id, string speaker, string[] options)[] Choices =', '        {']
    for cid, speaker, _, _, options in CHOICES:
        d.append(f'            ({cs(cid)}, {cs(speaker)}, new[] {{ {", ".join(cs(o[0]) for o in options)} }}),')
    d += ['        };', '',
          '        /// <summary>D.4: the moments a general answers (texts: radio.&lt;general&gt;.react.&lt;moment&gt;.&lt;n&gt;), and the generals who do.</summary>',
          '        public static readonly string[] ReactGenerals = { ' + ', '.join(cs(g) for g in REACT) + ' };', '',
          f'        public const int ReactLines = 2;',
          '    }', '}', '']
    open(DATA_CS, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(d))
    print(f'{len(TEXTS)} texts, {len(INTEL)} intel files, {sum(len(p) for p in COMICS.values())} comic panels, '
          f'{sum(len(b) for _, b in ARCS.values())} arc beats, {len(LOOT)} story loot, {len(REACT) * len(SITUATIONS) * 2} reactive lines')


if __name__ == '__main__':
    write()

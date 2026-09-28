"""The design document's sections for the 2026-09 programme (prompts 1-10): the story campaign,
multi-stage missions, the Operations mode, bases and towers, Siege and Defend, and what is left
to measure. build_doc.py calls these with the exported game (game.json) and its helpers."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GOAL_VI_EXTRA = {'Outpost': 'Lập tiền đồn', 'Relieve': 'Giải vây', 'Evacuate': 'Di tản', 'Duel': 'Đấu tướng'}
SIZE_VI = {'Small': 'Nhỏ', 'Medium': 'Vừa', 'Large': 'Lớn'}
STYLE_VI = {'tank': 'Thiết giáp', 'armour': 'Thiết giáp', 'artillery': 'Pháo binh', 'drones': 'Drone', 'drone': 'Drone', 'air': 'Phòng không',
            'antiair': 'Phòng không', 'logistics': 'Hậu cần', 'navy': 'Hậu cần', 'all': 'Tổng hợp', 'default': 'Mặc định'}
STANCE_VI = {'Attack': 'Tấn công', 'Defend': 'Phòng thủ'}
EVENT_VI = {'Reinforce': 'chi viện địch', 'AllyReinforce': 'chi viện ta', 'Expand': 'mở rộng vùng chơi', 'Betrayal': 'đồng minh phản bội',
            'Radio': 'radio', 'Cp': 'thưởng CP', 'Strike': 'không kích', 'Income': 'thu nhập'}


def campaign(game, h):
    """Section: the story campaign (prompt 4): setting, characters, chapters, missions, rewards."""
    esc, table, img = h['esc'], h['table'], h['img']
    goal_vi = dict(h['GOAL_VI'], **GOAL_VI_EXTRA)
    out = ["<div class='section'><h2>3. Chiến dịch</h2>"
           "<p><b>Bối cảnh:</b> tương lai gần, một vùng duyên hải hư cấu. Tập đoàn quân sự tư nhân <b>Hegemon</b> chiếm vùng này và chạy các chương trình "
           "vũ khí thử nghiệm: Behemoth, Tổ Ong và dự án Bọ Bạc. Người chơi chỉ huy <b>Lữ đoàn Cơ giới 7</b> (Machine Brigade) của Liên minh Duyên hải.</p>"
           f"<p><b>Cấu trúc:</b> {len(game['chapters'])} chương trong 3 hồi, {len(game['campaign'])} nhiệm vụ "
           f"({sum(1 for m in game['campaign'] if not m['side'])} chính, {sum(1 for m in game['campaign'] if m['side'])} phụ). Mỗi chương có 10 nhiệm vụ chính "
           "và 2 nhiệm vụ phụ; nhiệm vụ 5 là boss giữa chương, nhiệm vụ 10 là chiến dịch lớn nhiều giai đoạn (15–25 phút, riêng trận cuối game tới 30 phút). "
           "Không hai nhiệm vụ nào trên cùng một bản đồ có cùng cấu hình: mỗi lần quay lại đổi ít nhất 2 yếu tố (hướng xuất phát, vị trí căn cứ, thời tiết/đêm, "
           "vùng chơi, loại mục tiêu, phe giữ căn cứ). Trình tạo dữ liệu (Tools/campaign) tự kiểm tra luật này và luật không nhiệm vụ nào đòi thẻ chưa mở.</p>"]
    # Characters
    rows = [[f"<b>{esc(c['name'])}</b>", esc(c['role']), esc(c['bio'])] for c in game['characters'] if c['name']]
    out.append("<h3>Nhân vật</h3>" + table(['Nhân vật', 'Vai trò', 'Tiểu sử'], rows))
    # Generals as AI configurations
    rows = [[f"<b>{esc(g['name'] or g['id'])}</b>", esc(STYLE_VI.get(g['style'], g['style'])), esc(STANCE_VI.get(g['stance'], g['stance'])), esc(', '.join(g['deck'])), esc(', '.join(g['supports'])),
             esc(', '.join(g['elitesPrefer']))] for g in game['generals']]
    out.append("<h3>Tướng địch là cấu hình AI</h3><p>Mỗi tướng có bộ bài, thói quen gọi hỏa lực, kiểu căn cứ, ưu tiên xe tinh nhuệ, chân dung, câu khiêu khích và câu khi thua.</p>"
               + table(['Tướng', 'Kiểu căn cứ', 'Thế trận', 'Bộ bài đặc trưng', 'Hỏa lực', 'Ưu tiên tinh nhuệ'], rows))
    # Chapters
    rows = [[f"{c['number']}", f"Hồi {c['act']}", f"<b>{esc(c['title'])}</b><br><span class='muted'>{esc(c['summary'])}</span>", esc(', '.join(c['maps'])),
             esc(c['general']), c['missions']] for c in game['chapters']]
    out.append("<h3>Các chương</h3>" + table(['#', 'Hồi', 'Chương', 'Bản đồ', 'Tướng', 'Nhiệm vụ'], rows))
    if game['timeline']:
        out.append("<h3>Dòng thời gian</h3><ol>" + ''.join(f"<li>{esc(t)}</li>" for t in game['timeline']) + "</ol>")
    # Missions by chapter
    for c in game['chapters']:
        ms = [m for m in game['campaign'] if m['chapter'] == c['number']]
        rows = []
        for m in ms:
            tag = ' <span class="chip">chiến dịch lớn</span>' if m['operation'] else ' <span class="chip">phụ</span>' if m['side'] else ''
            stages = ''
            if m['stages']:
                stages = ('<br><span class="muted">Giai đoạn: ' + ' → '.join(esc(s['title'] or s['goalName']) for s in m['stages'])
                          + (' · lựa chọn: ' + esc(' / '.join(x for s in m['stages'] for x in s['choices'])) if any(s['choices'] for s in m['stages']) else '')
                          + '</span>')
            rows.append([m['id'], f"<b>{esc(m['name'])}</b>{tag}<br><span class='muted'>{esc(m['brief'])}</span>{stages}", esc(m.get('mapName', m['map'])),
                         goal_vi.get(m['goal'], m['goal']) + (f"<br><span class='muted'>{esc(m['boss'])}</span>" if m['boss'] else ''),
                         esc(m['general']), f"{m['coins']} xu" + (f" · HQ {m['hqLevel']}" if m['hqLevel'] else ''), esc(', '.join(m['unlocks']))])
        out.append(f"<h3>Chương {c['number']}: {esc(c['title'])}</h3>" + table(['#', 'Nhiệm vụ', 'Bản đồ', 'Mục tiêu', 'Tướng', 'Thưởng', 'Mở khóa'], rows))
    out.append("<h3>Kể chuyện</h3><ul>"
               "<li>Briefing dạng thẻ có chân dung người giao nhiệm vụ.</li>"
               "<li>Radio trong trận: chân dung nhỏ và một dòng, kích hoạt theo sự kiện (chiếm điểm, boss xuất hiện, sở chỉ huy dưới 50% máu...), bỏ qua được.</li>"
               "<li>Camera lia trong trận khi boss, chi viện hoặc tướng địch xuất hiện; không có cutscene.</li>"
               "<li>Màn chuyển chương có tóm tắt 3–4 câu; phần kết (epilogue) sau chương 9 và mở cấp Huyền thoại của chế độ Tác chiến.</li>"
               "<li>Mục Hồ sơ trong menu: tiểu sử nhân vật, hồ sơ boss, dòng thời gian, các mẩu truyện mỗi nhiệm vụ trao.</li></ul>"
               "<h3>Phần thưởng và kinh tế chiến dịch</h3><p>Mỗi chương mở 5–7 thẻ (xe, tháp, thẻ hỗ trợ), một cấp sở chỉ huy ở các chương 1/3/5/7/9 và một "
               "mô-đun tiện ích (chương 1–5; các chương sau trao một món đồ tháp). Mỗi nhiệm vụ trả bản thiết kế, xu và một mẩu truyện; nhiệm vụ phụ trả bản thiết kế hiếm "
               "hoặc đồ tháp. Boss bay chỉ xuất hiện khi người chơi đã có ít nhất hai thẻ phòng không mặt đất. Người chơi chỉ đánh chiến dịch đưa bộ bài chính "
               "(8 thẻ + 6 tháp) lên hạng 7,0 khi bắt đầu hồi III và 8,1 ở cuối chiến dịch.</p>"
               + img(ROOT / 'Docs' / 'art' / 'campaign_economy.png', '') + "<div class='caption'>Đường cong hạng của bộ bài chính theo tiến độ chiến dịch.</div></div>")
    return '\n'.join(out)


def multistage(game, h):
    """Section: the multi-stage mission framework (prompt 5)."""
    esc, table = h['esc'], h['table']
    ops = [m for m in game['campaign'] if m['operation']]
    rows = [[m['id'], f"<b>{esc(m['name'])}</b>", ' → '.join(esc(s['title'] or s['goalName']) for s in m['stages']),
             esc(', '.join(sorted({EVENT_VI.get(e, e) for s in m['stages'] for e in s['events']}))),
             esc(' / '.join(x for s in m['stages'] for x in s['choices'])), 'có' if m['ally'] else ''] for m in ops]
    return ("<div class='section'><h2>4. Nhiệm vụ nhiều giai đoạn</h2>"
            "<p>Chiến dịch lớn chạy nhiều giai đoạn trong cùng một trận. Mỗi giai đoạn là một nhiệm vụ riêng (mục tiêu, điều kiện thắng, quân, boss) đặt trên dữ liệu "
            "của nhiệm vụ mẹ. Xong một giai đoạn thì trả thưởng CP, chạy sự kiện cuối giai đoạn, lưu điểm lưu và sang giai đoạn tiếp theo hoặc một lựa chọn. "
            "Thua một giai đoạn là thua nhiệm vụ.</p><ul>"
            "<li><b>Sự kiện</b> ở đầu, cuối hoặc sau một số giây: chi viện địch, chi viện ta, mở rộng vùng chơi, đồng minh phản bội, radio, thưởng CP, không kích, thu nhập.</li>"
            "<li><b>Lựa chọn nhánh:</b> mỗi chiến dịch lớn có ít nhất một giai đoạn chọn giữa hai mục tiêu có hệ quả khác nhau (ví dụ phá kho đạn: thu nhập địch ×0,7; "
            "hoặc chiếm đài radio: không kích miễn phí mỗi 50–55 giây). Trận vẫn chạy trong lúc chọn; sau 15 giây tự lấy phương án đầu.</li>"
            "<li><b>Điểm lưu bằng phát lại:</b> mô phỏng xác định, nên thay vì chụp toàn bộ trạng thái, game ghi lệnh của người chơi (kèm bước mô phỏng) và các công tắc "
            "(thế trận, tự mua, yểm trợ, cứ điểm ưu tiên, nhánh đã chọn). Khôi phục = dựng lại trận cùng seed và phát lại nhật ký sau màn chờ; dấu vân tay trạng thái "
            "(vị trí, máu, CP của mọi xe) phải trùng. Bài kiểm tra xác nhận trận khôi phục và trận chơi liền mạch giống hệt, kể cả qua một lựa chọn và một lần phản bội.</li>"
            "<li><b>Chỉ huy đồng minh:</b> căn cứ riêng (sở chỉ huy, tháp) và quân riêng, do AI chiến thuật riêng điều khiển, cùng mục tiêu với người chơi, "
            "thả quân ở bãi riêng. Xe đồng minh không tính vào quân số, phí duy trì và giới hạn của người chơi. Sự kiện phản bội chuyển toàn bộ xe và công trình của "
            "đồng minh sang phe địch ngay trong trận (chương 8).</li>"
            "<li><b>Vùng chơi mở rộng:</b> chiến dịch lớn bắt đầu trên một phần bản đồ; phe người chơi không đi ra ngoài biên (đường đứt nét vàng), camera cũng dừng "
            "ở biên và mở theo khi vùng chơi mở rộng. Lưới dẫn đường và làn giao thông đã phủ toàn bản đồ.</li>"
            "<li><b>Địch đông:</b> trần xe địch 48 ở Công thành, Phòng thủ, Vô tận và chiến dịch lớn (32 ở chế độ thường); quân đông là bầy xe rẻ. "
            "Tìm đường tối đa 6 lượt mỗi bước mô phỏng (còn lại xếp hàng), hai chỉ huy AI nghĩ ở các bước khác nhau. Đo trên máy bàn quy đổi ×6 cho điện thoại yếu: "
            "48 xe địch có thời gian bước trung bình 4,4 ms, p99 15,3 ms (ngân sách 8/16 ms).</li>"
            "<li><b>Boss nhiều pha:</b> thanh máu có vạch pha; tới vạch boss dừng lại, biến hình vài giây (không nhận sát thương, camera lia tới, tướng lên radio) rồi "
            "đánh tiếp mạnh hơn (sát thương, tốc độ, giáp, kỹ năng, mô hình mới).</li></ul>"
            "<h3>Các chiến dịch lớn cuối chương</h3>"
            + table(['#', 'Chiến dịch', 'Giai đoạn', 'Sự kiện', 'Lựa chọn', 'Đồng minh'], rows) + "</div>")


def operations(game, h):
    """Section: the Operations mode (prompt 6)."""
    esc, table = h['esc'], h['table']
    o = game['operations']
    tiers = [[f"<b>{esc(t['name'])}</b>", f"×{t['enemy']:g}", f"×{t['playerIncome']:g}", 'có' if t['supports'] else 'không', f"×{t['score']:g}"] for t in o['tiers']]
    s = o['scoring']
    muts = [[f"<b>{esc(m['name'])}</b>", esc(m['info']), f"+{m['score'] * 100:g}%"] for m in o['mutators']]
    rot = [[i + 1, esc(r['operation']), esc(r['a']), esc(r['b'])] for i, r in enumerate(o['rotation'])]
    return ("<div class='section'><h2>5. Tác chiến</h2>"
            "<p>Menu gồm 5 mục: Trang chủ, Chiến dịch, <b>Tác chiến</b>, Quân đội, Cửa hàng; Giao tranh (Giữ cứ điểm, Vua đồi, Tử chiến, Công phá, Công thành, Phòng thủ) "
            "và Thử thách (Sinh tồn, Vô tận) chọn ở ô chọn chế độ. Tác chiến gom: chơi lại các chiến dịch lớn và các trận nổi bật của cốt truyện (công thành, phòng thủ, "
            f"đấu tướng) sau khi đã thắng trong chiến dịch ({len(o['replayable'])} trận), chiến dịch của tuần, Pháo đài tuần, Săn trùm và thử thách hằng ngày.</p>"
            "<h3>Cấp độ</h3>" + table(['Cấp', 'CP và thu nhập địch', 'Thu nhập ta', 'Hỏa lực', 'Hệ số điểm'], tiers)
            + "<p>Huyền thoại mở sau khi thắng chiến dịch lớn cuối cùng. "
            f"<b>Điểm</b> một trận thắng: {s['win']:g} + tối đa {s['time']:g} theo thời gian dưới {s['par'] / 60:g} phút + tối đa {s['losses']:g} theo tổn thất "
            f"({s['lossesAtZero']:g} xe mất thì bằng 0) + tối đa {s['hq']:g} theo máu sở chỉ huy; nhân hệ số cấp cộng phần của mỗi mutator. Thua: 0 điểm. "
            "Kỷ lục (điểm cao nhất, thắng nhanh nhất) lưu riêng cho từng trận và từng cấp.</p>"
            f"<p><b>Thưởng tuần gộp chung một sổ:</b> thắng lần đầu trong tuần Pháo đài tuần {o['weekly']['fortress']} xu, chiến dịch của tuần {o['weekly']['operation']} xu.</p>"
            f"<h3>Mutator ({len(muts)})</h3>" + table(['Mutator', 'Tác dụng', 'Điểm'], muts)
            + "<h3>Vòng xoay 26 tuần</h3><p>Mỗi tuần một chiến dịch và hai mutator, chọn theo số tuần (ISO, UTC) nên mọi người cùng một tuần; các cặp loại trừ nhau "
            "không bao giờ đi cùng, mỗi mutator đều xuất hiện trong nửa năm, không cặp nào lặp lại.</p>"
            + table(['Tuần', 'Chiến dịch', 'Mutator 1', 'Mutator 2'], rot) + "</div>")


def bases(game, h):
    """Section: bases and towers (prompts 1, 3 and the sized slots)."""
    esc, table, guide = h['esc'], h['table'], h['guide_html']
    b = game['base']
    levels = [[f"HQ {l['level']}", l['small'], l['medium'], l['large'], l['utility']] for l in b['levels']]
    towers = sorted(b['towers'], key=lambda t: ['Small', 'Medium', 'Large'].index(t['size']) if t['size'] in ('Small', 'Medium', 'Large') else 3)
    rows = [[f"<b>{esc(t['name'])}</b>", SIZE_VI.get(t['size'], t['size']), h['num'](t['hp']), f"{t['rebuildCp']} CP · {t['rebuildSeconds']:g} s",
             '<br>'.join(f"<b>{esc(x['name'])}</b>: {esc(x['info'])}" for x in t['branches']), guide(t['guide'])] for t in towers]
    mods = [[f"<b>{esc(m['name'])}</b>", guide(m['guide'])] for m in b['modules']]
    return ("<div class='section'><h2>6. Căn cứ và tháp</h2>"
            "<p>Căn cứ là một loadout chọn trước trận như bộ bài: sở chỉ huy (HQ) cấp 1–5 và các ô tháp theo cỡ <b>nhỏ / vừa / lớn</b> trên bản đồ căn cứ của từng map. "
            "Tháp cỡ nào vào ô cỡ đó hoặc ô to hơn; ô tiện ích nhận mô-đun. Tháp bị phá được thả dù lại trong trận (trả CP, có hồi chiêu; tháp nhỏ rẻ và nhanh hơn). "
            "Mỗi cứ điểm có tiền đồn 1 ô nhỏ + 1 ô vừa. Vai trò căn cứ theo chế độ: chỗ dựa (sở chỉ huy không bị phá) hoặc mục tiêu.</p>"
            + table(['Cấp', 'Ô nhỏ', 'Ô vừa', 'Ô lớn', 'Ô tiện ích'], levels)
            + "<p><b>Vai trò tháp nhỏ:</b> tháp canh thấy tàng hình và tăng 10% tầm cho tháp gần; tháp phòng không nhỏ +25% sát thương lên drone và trực thăng. "
            "<b>Điểm yếu tháp pháo:</b> xoay chậm, nạp lâu, súng đồng trục không bắn máy bay. <b>AI</b> đọc căn cứ địch và mua quân khắc chế. "
            "<b>Thẻ tháp</b> lên hạng như xe; từ hạng 7 chọn 1 trong 2 nhánh (đổi nhánh 800 xu). <b>Trang bị tháp:</b> 3 ô (Vũ khí, Kết cấu, Hệ thống) dùng chung cho mọi "
            "tháp cùng loại trong căn cứ.</p>"
            f"<h3>Thẻ tháp ({len(rows)})</h3>" + table(['Tháp', 'Cỡ', 'Máu', 'Dựng lại', 'Nhánh (hạng 7)', 'Hướng dẫn'], rows)
            + f"<h3>Mô-đun tiện ích ({len(mods)})</h3>" + table(['Mô-đun', 'Tác dụng'], mods)
            + "<h3>Đo cân bằng căn cứ</h3><p>Căn cứ mặc định (pháo đài hạng nặng + ụ pháo; tháp pháo, giàn rocket, tháp ATGM; mỗi loại 2 tháp canh, phòng không, súng máy) "
            "đạt 1,86 trước quân hỗn hợp, cao hơn mọi căn cứ chỉ một loại tháp (tốt nhất 1,79); không căn cứ một loại nào mạnh nhất trước mọi loại quân. Tỷ lệ chọn tháp "
            "nhỏ trong ô nhỏ (tối ưu tham lam): tháp canh 32%, phòng không 22%, súng máy 19%, răng rồng 11%, EW 10%, bãi mìn 7% → bãi mìn được tăng lên 8 quả, "
            "rải lại mỗi 45 giây. Quân pháo binh đứng ngoài tầm tháp thắng mọi căn cứ nếu căn cứ đứng một mình: câu trả lời là quân và phản pháo.</p></div>")


def siege(game, h):
    """Section: Siege and Defend (prompt 5, items 6-7)."""
    return ("<div class='section'><h2>7. Công thành và Phòng thủ</h2><ul>"
            "<li><b>Pháo đài chiếm 45% chiến trường</b> ở góc đông bắc: tuyến ngoài (trạm radar), tường chữ L có cổng chính đóng và cửa phụ mở, thành trong có sở chỉ huy. "
            "Tháp đặt trên ô có cỡ theo roster tháp mới, lấy từ loadout của phe giữ (AI theo độ khó và tướng); vòng trong mạnh hơn.</li>"
            "<li><b>Set-piece:</b> tường sập có hoạt cảnh rồi thành đống gạch đi qua được; cổng thép bị phá đổ vào trong; máy phát khiên giữ vòm khiên che thành trong, "
            "phá máy cuối cùng thì vòm tắt kèm chớp sáng; siêu pháo bắn theo đồng hồ đếm ngược vào cụm quân đông nhất (phá nó là mục tiêu phụ: 25 CP, 100 xu); "
            "đèn pha quét và còi báo động ban đêm; chi viện địch đến bằng tàu hỏa trên đường ray hoặc máy bay vận tải hạ cánh trên đường băng, báo trước 10 giây.</li>"
            "<li><b>Phòng thủ:</b> ba tuyến ngoài, giữa, trong và sở chỉ huy là trận chốt cuối. Mất một tuyến thì tháp ở đó nổ và người chơi được thưởng CP rút lui "
            "(24 rồi 32 CP); tuyến trong có tháp mạnh hơn. Căn cứ dùng đúng loadout của người chơi. Đợt địch kế tiếp hiện trước bằng icon và số lượng (đợt được lên "
            "kế hoạch trước nên đúng y như thứ đổ bộ); đợt là bầy xe rẻ lớn dần, trần 48 xe cùng lúc.</li>"
            "<li><b>Đầm Lầy và Quần Đảo San Hô</b> giữ pháo đài kiểu cũ ở góc: tường mới sẽ cắt mọi đường đắp của hai bản đồ này.</li>"
            "<li><b>Đo (độ khó Thường, 5 seed):</b> Công thành thắng 5/5 (9,7–17,8 phút); Phòng thủ giữ 3/5 trên 5 bản đồ và 5/5 ở bài kiểm tra kết thúc trận; "
            "Vô tận: sở chỉ huy rơi ở phút 10,3–11,7.</li></ul></div>")


def boss_rules(game, h):
    """Prompt 9: the rules every boss's parts follow, the effects at the breaks, the part order."""
    rules = [
        '<b>Máu bộ phận</b> là một phần máu thân (đọc trực tiếp, nên tăng theo cấp chiến dịch, độ khó và bản mạnh của nhiệm vụ): mỗi bộ phận 8–15%; '
        'boss từ 5 súng trở lên có tổng 50–70%, boss chỉ có 3–4 thứ phá được có tổng 35–47%.',
        '<b>Máu thân</b> giảm còn ×0,76 đến ×0,90 (1,125 / (1 + 0,7 × tổng phần bộ phận)) để trận dài hơn khoảng 12% (ước tính theo mô hình, đo ở phase kiểm tra).',
        '<b>Vỡ một bộ phận:</b> súng trên đó im cả trận; kỹ năng dừng khi mọi bộ phận mang nó đều vỡ; cơ chế dừng (phát bắn của siêu pháo, đào hầm của Giun Đất, '
        'đổ quân của tàu đệm khí, hào quang của Tổng Tư Lệnh); áp dụng phạt tốc độ, quay, nhịp bắn, độ tản; thân mất thêm 30% máu của bộ phận đó.',
        '<b>Chỉ phát trúng trực tiếp</b> làm hại bộ phận; nổ lan, lửa và hỏa lực hỗ trợ rơi vào thân. Đạn trúng bộ phận nhô ra ngoài thân (quạt, đầu máy, đầu kéo) nay tính là trúng.',
        '<b>Tự sửa:</b> Tàu Thép và Bastion một lần mỗi trận hồi bộ phận đã vỡ có phát bắn mặt đất nặng nhất lên 50%.',
        '<b>Nhắm bắn:</b> mỗi xe nhắm bộ phận nguy hiểm nhất với nó trong tầm (phòng không nhắm bộ phận bắn máy bay, diệt tăng nhắm bộ phận dày nhất); 2 trên 5 phát vẫn vào thân.',
        '<b>Lệnh bắn bộ phận:</b> chạm vào biểu tượng bộ phận dưới thanh máu boss hoặc chạm thẳng vào bộ phận trên mô hình: mọi xe trong tầm dồn hỏa lực vào đó tới khi vỡ; chạm lại để hủy.',
        '<b>Săn trùm</b> thưởng 2 CP cho mỗi bộ phận vỡ.',
    ]
    fx = [
        'Dưới 50% máu bộ phận bốc khói và tóe lửa điện, dưới 25% bắt cháy.',
        'Lúc vỡ: súng và kho đạn nổ lớn (có mảnh văng ở đồ họa Cao), bộ phận năng lượng lóe sáng với vòng xanh và tia điện, động cơ bùng cầu lửa; '
        'bộ phận biến mất, thay bằng mảnh xác.',
        'Sau khi vỡ, lửa và cột khói đen ở lại tới hết trận; thân boss cháy thêm ở 66% và 33% máu; boss bay hoặc chạy nhanh kéo vệt khói từ động cơ vỡ.',
        'Tối đa 8 điểm lửa mỗi boss (5 ở đồ họa Thấp, khói và tia lửa giảm một nửa). Khi boss chết mọi đám cháy bùng lên, xác cháy 25–35 giây.',
        'Chỉ là hình ảnh: mô phỏng không thấy khói, tầm nhìn qua boss đang cháy không đổi.',
    ]
    return ("<p>Mọi boss có bộ phận theo cùng một bộ luật (phase 9); boss cuối chương còn có thanh máu nhiều pha.</p><ul>"
            + ''.join(f"<li>{r}</li>" for r in rules) + "</ul><h4>Lửa và khói ở chỗ vỡ</h4><ul>"
            + ''.join(f"<li>{h['esc'](f)}</li>" for f in fx) + "</ul>")


def boss_parts(v, h):
    """The parts table under one boss's card."""
    parts = v.get('parts') or []
    if not parts:
        return ''
    groups = {}
    for p in parts:
        key = (p.get('name') or p['kind'], p.get('effects', ''), round(p['hp'], 3))
        groups[key] = groups.get(key, 0) + 1
    rows = [[h['esc'](name) + (f" ×{n}" if n > 1 else ''), f"{share * 100:g}%" + (f" (×{n}: {share * n * 100:g}%)" if n > 1 else ''), h['esc'](effects)]
            for (name, effects, share), n in groups.items()]
    total = sum(p['hp'] for p in parts)
    notes = [f"Tổng {total * 100:.0f}% máu thân trong {len(parts)} bộ phận"]
    if v.get('partLock'):
        notes.append('thân không nhận sát thương tới khi vỡ ' + h['esc'](v['partLock']))
    if v.get('partPatch'):
        notes.append('tự sửa một bộ phận một lần mỗi trận')
    if v.get('phases'):
        notes.append('pha ở ' + ', '.join(f'{x * 100:g}%' for x in v['phases']))
    tip = ''
    if v.get('partTip'):
        text = re.sub(r'^\s*(Mẹo|Tip)\s*:\s*', '', v['partTip'])
        tip = "<p class='muted'><b>Mẹo:</b> " + re.sub(r'\[\[(.*?)\]\]', r'<b>\1</b>', h['esc'](text)) + "</p>"
    return (h['table'](['Bộ phận', 'Máu (phần thân)', 'Khi vỡ'], rows)
            + f"<p class='muted'>{'; '.join(notes)}.</p>" + tip)


def feedback(game, h):
    """The fixes after the owner's play test (2026-09-28, DECISIONS 11A-11D)."""
    e = h['esc']
    missiles = [('Tên lửa chống tăng (TOW, Ataka...)', '36 → 24', '0,94 → 1,42 s ở 34 m'), ('Kornet', '38 → 25', '1,32 → 2,0 s ở 50 m'),
                ('Hellfire và cùng lớp', '45 → 30', '0,76 → 1,13 s ở 34 m'), ('Vikhr (Ka-52)', '50 → 34', '1,1 → 1,62 s ở 55 m'),
                ('Maverick, Kh-29', '50 → 32', '0,8 → 1,25 s ở 40 m'), ('Phòng không tầm ngắn (SAM, Stinger, Igla-V)', '60 → 40', '0,73 → 1,1 s ở 44 m'),
                ('Phòng không tầm xa', '72 → 46', '1,39 → 2,17 s ở 100 m'), ('48N6', '95 → 62', '1,0 → 1,53 s'),
                ('Không đối không (AIM-9, R-60...)', '74 → 48', '0,81 → 1,25 s ở 60 m'), ('Tên lửa hành trình, JASSM', '30 → 20', '3,7 → 5,5 s ở 110 m'),
                ('Rocket bắn thẳng (6 loại)', '75 → 60', '0,45 → 0,57 s ở 34 m')]
    rhythm = [('Pháo máy bay cường kích', 'loạt 10 viên, hồi 3,57 s', 'luồng 20 viên/s, băng 70, thay 1 s', '101 → 100'),
              ('Gatling GAU (A-10)', 'loạt 14 viên', 'luồng 25 viên/s, băng 90, thay 1 s', '190 → 190'),
              ('Pháo tiêm kích', 'loạt 8 viên', 'luồng 20 viên/s, băng 70, thay 1 s', '54 → 54,5'),
              ('GSh-30K', 'loạt 6 viên', 'luồng 12,5 viên/s, băng 30, thay 1,2 s', '73,8 → 73,7'),
              ('Pháo 25 mm máy bay pháo', 'súng máy', 'luồng 16,7 viên/s, băng 50, thay 1,2 s', '45 → 45'),
              ('Pháo tự động 25 mm (xe bọc thép)', 'loạt 3, hồi 1,29 s', 'luồng 5 viên/s, băng 12, thay 1,6 s', '44 → 46,5'),
              ('Pháo tự động 30 mm (IFV)', 'loạt 3', 'luồng 5 viên/s, băng 10, thay 1,8 s', '52,8 → 59,7'),
              ('Pháo đôi 30 mm (BMPT)', 'loạt 4', 'luồng 6,7 viên/s, băng 16, thay 1,6 s', '74 → 84,5'),
              ('Súng máy', 'hồi 0,16–0,22 s', 'hồi 0,1–0,13 s, viên nhẹ hơn', 'gần như giữ nguyên')]
    clips = [('Xe gây nhiễu', 'tên lửa của địch bắn vào xe tăng bên cạnh bị mất khóa, bay lệch; vòng tím nhấp nháy'),
             ('Iron Beam', 'đốt rơi rocket và tên lửa bắn vào xe nó bảo vệ; bắn cả trực thăng'),
             ('Xe công binh', 'sửa hai xe tăng bị thương'), ('Xe đặc công', 'gia cố tháp canh bị hỏng'),
             ('Xe chỉ huy', 'xe tăng trong vùng hào quang bắn nhanh hơn; vòng vàng'),
             ('Radar phản pháo', 'cối địch bắn là bị lộ (chấm đỏ), cối ta bắn trả'),
             ('Xe ủi bọc thép', 'ủi phẳng một hàng răng rồng'),
             ('Máy bay, trực thăng', 'xe phòng không địch bắn, pháo sáng kéo tên lửa đi'),
             ('IFV, xe thả khói', 'địch áp sát thì thả màn khói'), ('Drone trinh sát', 'đánh dấu mọi mục tiêu thấy được'),
             ('EMP, vòm khiên', 'EMP làm im xe tăng đang bắn; vòm khiên đỡ đạn cho xe bên trong')]
    return ("<div class='section'><h2>16b. Sửa sau buổi chơi thử (28/9)</h2>"
            "<p>Chủ dự án chơi thử bản phase 1-9 và báo 16 lỗi; bốn nhóm sửa song song, mỗi nhóm có bài kiểm tra riêng và chạy thử chế độ Play (0 lỗi).</p>"
            "<h3>Nòng súng và đường đạn</h3><ul>"
            "<li><b>Đạn ra lệch nòng:</b> nguyên nhân là hiệu ứng bắn được đặt khi xe còn ở tư thế của khung hình trước (lệch tới 2,4 m ở trực thăng, 4,7 m ở máy bay). "
            "Giờ đạn, chớp lửa và vệt khói xuất phát từ đầu nòng đúng như được vẽ trong khung hình đó, ở mọi hướng thân, tháp pháo, góc nâng và tư thế bay: đo được 0,000 m trên 400 phát.</li>"
            "<li><b>Đạn pháo, cối:</b> bay trên một đường cong duy nhất ra khỏi nòng theo hướng nòng; đạn, vệt khói và điểm bắt đầu khớp nhau suốt đường bay.</li>"
            "<li><b>Kích thước:</b> tên lửa chống tăng và vác vai ×1,1; rocket ×1,15; không đối đất, phòng không, không đối không, hành trình ×1,2; drone ×2.</li></ul>"
            "<h3>Vũ khí</h3><ul>"
            "<li><b>Mục tiêu:</b> xe chuyên phòng không (và tháp phòng không) giữ vũ khí chính bắn máy bay và ngóc nòng lên theo máy bay; xe khác chỉ bắn máy bay bằng súng máy. "
            "Đổi sang chỉ bắn mặt đất: pháo 25 mm (xe bọc thép, tổ súng của tháp canh), pháo 30 mm (IFV, APC tinh nhuệ), pháo đôi BMPT, Vikhr của Ka-52, tên lửa của boss.</li>"
            "<li><b>Nhịp bắn:</b> cơ chế băng đạn mới (bắn liên tục theo mục tiêu rồi thay băng), DPS giữ như cũ.</li></ul>"
            + h['table'](['Tên lửa', 'Tốc độ (m/s)', 'Thời gian bay'], [[e(a), b, c] for a, b, c in missiles])
            + h['table'](['Vũ khí', 'Trước', 'Sau', 'DPS'], [[e(a), e(b), e(c), e(d)] for a, b, c, d in rhythm])
            + "<p class='muted'>Máy bay cường kích bắn một luồng 1–1,4 giây mỗi lượt bổ nhào (trước 0,45–0,55 s); muốn đủ 3–4 giây mỗi lượt cần tầm pháo xa hơn hoặc bổ nhào chậm hơn: chờ chủ dự án quyết.</p>"
            "<h3>Vụ nổ, lửa, laser</h3><ul>"
            "<li><b>Nổ đạn tăng:</b> công thức riêng (chớp sáng, cầu lửa và cầu lửa thứ hai, tia lửa, khói đen, bụi, mảnh kim loại); tăng nhẹ ×1,3, tăng chủ lực và diệt tăng ×1,4, tăng nặng và siêu nặng ×1,5.</li>"
            "<li><b>Bom:</b> GBU-12, bom chùm, napalm ×1,3; ném bom rải thảm ×1,45; FAB-500, JDAM, Mk 84 ×1,5. Tên lửa hành trình và MOAB: vòng sóng xung kích bằng đúng bán kính sát thương (18 m và 27 m).</li>"
            "<li><b>Giữ chất lượng khi phóng to:</b> thêm nhiều hạt hơn thay vì phóng to từng hạt (khung ảnh 128 px), chớp sáng không còn bị mặt đất cắt; đồ họa Thấp giữ 40% phần hạt thêm.</li>"
            "<li><b>Xe phun lửa:</b> luồng lửa cam dày loang dần, cầu lửa napalm phồng khi bay và bốc lên ở mục tiêu, lửa đứng thẳng, hơi nóng, than hồng, khói đen dày hơn.</li>"
            "<li><b>Iron Beam:</b> tia la-de liên tục có lõi trắng, quầng đỏ cam, nạp năng lượng 0,22 s, điểm cháy trắng, tia lửa và giọt kim loại nóng chảy, lưu sáng 0,28 s.</li></ul>"
            "<h3>Menu, âm thanh, clip Xem bắn</h3><ul>"
            "<li><b>Giật lúc mở game:</b> màn chờ chưa hiện ở lần mở đầu tiên nên người chơi thấy quá trình dựng (khung đầu 3,2 giây). Giờ màn chờ che từ khung đầu, âm thanh nạp trước; "
            "5 giây đầu sau màn chờ không khung nào quá 33 ms (đo trên editor).</li>"
            "<li><b>Nhạc:</b> một trình phát nhạc cho cả phiên, chuyển bài có crossfade 2 giây; menu không còn tiếng súng nổ của trận nền (chỉ gió nhẹ); clip Xem bắn nhỏ tiếng hơn và hạ nhạc.</li>"
            "<li><b>Clip Xem bắn thể hiện kỹ năng đặc biệt:</b></li></ul>"
            + h['table'](['Phương tiện', 'Clip cho thấy'], [[e(a), e(b)] for a, b in clips])
            + "</div>")


def testing(game, h):
    """Section: tests and what the testing phase still has to measure."""
    items = [
        'Quét 5 seed toàn chiến dịch sau khi gộp mọi nhánh (21 nhiệm vụ trên 8 bản đồ mới chưa đo; các chiến dịch lớn giữ trong 15–25 phút).',
        'Tác chiến: mọi tuần của vòng xoay thắng được qua 5 seed ở cấp Thường.',
        'Công thành, Phòng thủ (mục tiêu ≥ 4/5), Vô tận, Pháo đài tuần ở các độ khó và 7 bản đồ còn lại.',
        'Xe tinh nhuệ theo ngân sách: tỷ lệ sức mạnh 1,8–2,2 lần; chiến dịch và Săn trùm sau khi đổi sang ngân sách.',
        'Trang bị: độ chênh giữa các nhóm vũ khí (mục tiêu ≤ 1,5 lần), Nạp kép trên pháo tự động và giàn rocket, đầu đạn chùm lên công trình, cầu tuyết sau trần hoàn CP.',
        'Boss: thời gian hạ trong +15% sau khi có bộ phận; mọi trận boss và Săn trùm thắng được.',
        'Hiệu năng: ngân sách tick đo lại trên máy yên tĩnh và điện thoại yếu thật; FPS trận boss nặng nhất ở mức đồ họa Thấp; đảo và đầm lầy (2.500 vật thể).',
        'Sau buổi chơi thử: khả năng thắng chiến dịch và trận boss khi súng chính xe thường không còn bắn máy bay; thời gian hạ tăng của máy bay cường kích và A-10 với nhịp bắn mới; '
        'tỷ lệ trúng của tên lửa chậm hơn khi có pháo sáng và APS; FPS khi nhiều tên lửa hành trình hoặc ném bom rải thảm cùng lúc ở đồ họa Thấp; khung hình những giây đầu trên điện thoại thật.',
        'Giao diện: FPS của HUD mới ở đồ họa Thấp; vùng an toàn trên máy tai thỏ và đục lỗ thật; toàn bộ bài kiểm tra EditMode.',
    ]
    return ("<div class='section'><h2>17. Kiểm thử và phép đo còn lại</h2>"
            "<p>Bài kiểm tra tự động chạy trong Unity (EditMode): mô phỏng xác định, nên mỗi luật có bài riêng (điểm lưu phát lại khớp tuyệt đối, phản bội không làm lỗi AI, "
            "trần xe, vùng chơi, mutator, bộ phận boss...). Các phép đo dài (5 seed, phòng thí nghiệm trang bị) dồn vào một phase kiểm tra riêng:</p><ul>"
            + ''.join(f"<li>{h['esc'](i)}</li>" for i in items) + "</ul></div>")

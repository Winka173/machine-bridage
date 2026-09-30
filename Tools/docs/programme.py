"""The design document's sections for the 2026-09 programme (prompts 1-10): the story campaign,
multi-stage missions, the Operations mode, bases and towers, Siege and Defend, and what is left
to measure. build_doc.py calls these with the exported game (game.json) and its helpers."""
import math
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
           "vũ khí thử nghiệm: Behemoth, bầy drone và Dự án Icarus. Người chơi chỉ huy <b>Lữ đoàn Cơ giới 7</b> (Machine Brigade) của Liên minh Duyên hải.</p>"
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
    armour = {(p.get('name') or p['kind'], p.get('effects', ''), round(p['hp'], 3)): p.get('armour', '') for p in parts}
    rows = [[h['esc'](name) + (f" ×{n}" if n > 1 else ''), f"{share * 100:g}%" + (f" (×{n}: {share * n * 100:g}%)" if n > 1 else ''),
             str(armour.get((name, effects, share), '')), h['esc'](effects)]
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
    a = v.get('armour') or {}
    notes.insert(0, 'giáp thân ' + ' / '.join(f"{k} {a.get(key, 0)}" for key, k in (('front', 'trước'), ('side', 'hông'), ('rear', 'sau'), ('top', 'nóc'))))
    return (h['table'](['Bộ phận', 'Máu (phần thân)', 'Giáp', 'Khi vỡ'], rows)
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


def combat_value(game, h):
    """Combat value measured in the sim (prompt 13 A): damage dealt with the time not firing counted."""
    e = h['esc']
    runs = sorted((ROOT / 'Docs' / 'balance').glob('combat_value_*_summary.tsv'), key=lambda p: p.stat().st_mtime)
    if not runs:
        return ''
    # The balance pass after prompt 18 names its final measure (a fresh checkout gives every file the same time).
    latest = ROOT / 'Docs' / 'balance' / 'combat_value_p18_after_summary.tsv'
    path = latest if latest.exists() else runs[-1]
    lines = path.read_text(encoding='utf-8').splitlines()
    head = lines[0].split('\t')
    units = {v['id']: v for group in ('vehicles', 'towers', 'elites') for v in game.get(group, [])}
    names = {i: v['name'] for i, v in units.items()}
    def num(x):
        try:
            return f"{float(x):.0f}"
        except ValueError:
            return ''
    def pct(x):
        try:
            return f"{float(x) * 100:.0f}%"
        except ValueError:
            return ''
    rows = []
    for line in lines[1:]:
        c = dict(zip(head, line.split('\t')))
        v = units.get(c['id'])
        if v is None:
            continue   # a card merged or dropped since the measure
        front = (v.get('armour') or {}).get('front', 0)
        rows.append([f"<b>{e(names[c['id']])}</b>", e(c.get('class', '')), str(v['cost']), str(front),
                     num(c.get('light')), num(c.get('tanks')), num(c.get('fort')), num(c.get('air')),
                     num(c.get('tanks+AA')), pct(c.get('onTarget')), num(c.get('survival')),
                     num(c.get('dpsLight')), num(c.get('dpsHeavy')), num(c.get('dpsAir'))])
    return ("<div class='section'><h2>9b. Giá trị thực chiến</h2>"
            "<p>DPS lý thuyết (phần 9) đã sửa để tính đủ loạt bắn, băng đạn, thời gian thay băng, nạp của bệ phóng và số bom/tên lửa mỗi lần đầy đạn. "
            "Giá trị thực chiến đo trong mô phỏng: mỗi xe hạng 1, không trang bị, đánh các nhóm mục tiêu chuẩn (cụm xe nhẹ, cụm xe tăng, công sự có tháp, máy bay) "
            "trong khoảng 90 giây từ lúc tiếp đất, có và không có phòng không đối phương; tính cả thời gian không bắn (di chuyển, xoay tháp, nạp đạn, bay vòng, bị pháo sáng "
            "và APS chặn). Giá trị = sát thương thực × hệ số sống sót / CP. Mọi quyết định cân bằng của prompt 13 dựa trên bảng này.</p>"
            + f"<p class='muted'>Số đo: <code>{e(path.name)}</code>; chỉ các thẻ còn trong roster, CP theo dữ liệu hiện tại.</p>"
            + h['table'](['Xe', 'Lớp', 'CP', 'Giáp trước', 'Giá trị: xe nhẹ', 'xe tăng', 'công sự', 'máy bay', 'xe tăng + PK', 'Thời gian bắn', 'Sống (s)',
                          'DPS thật: nhẹ', 'nặng', 'bay'], rows, 'dps') + "</div>")


def ammo_system(game, h):
    """Stores and rearming on the field (prompt 13 C, D, F)."""
    items = [
        '<b>Lượng đạn:</b> bom, tên lửa và rốc-két của máy bay và trực thăng có số lượng khi đầy đạn (ghi ở mục "Đạn và nạp đạn" trên mỗi thẻ); pháo máy bay và súng máy không giới hạn, chỉ thay băng.',
        '<b>Hồi dần trên chiến trường:</b> từng quả hồi theo thời gian, không cần căn cứ. Đang tấn công hoặc trong tầm phòng không/tiêm kích địch: một nửa tốc độ; ra khỏi vùng nguy hiểm liên tục 3 giây: đủ tốc độ.',
        '<b>Vòng chờ gần:</b> một vòng bay ngay sau tuyến quân ta gần nhất, ngoài tầm phòng không đã biết, cách chỗ giao tranh khoảng 2–3 giây bay; tính lại liên tục theo chiến tuyến. Không đơn vị nào bay về căn cứ hay ra ngoài bản đồ để nạp.',
        '<b>Rút đúng lúc:</b> hết đạn giữa lượt thì làm xong lượt (bổ nhào, lượt ném bom, vòng bay) rồi mới ra vòng chờ, bay theo đường thật, vẫn bị bắn được; chỉ huy AI cho ra sớm khi đạn dưới 20% và đang có quãng lặng.',
        '<b>Nạp nhanh hơn:</b> Bãi đáp ×2 (và hồi 3% máu/giây), sở chỉ huy ×1,5 (1% máu/giây), trực thăng cạnh Xe tiếp đạn ×2. Chỉ ghé khi nhanh hơn vòng chờ hoặc cần hồi máu.',
        '<b>Máy bay ném bom:</b> chỉ vào lượt mới khi có ít nhất 2/3 tải bom; ưu tiên cụm quân và công trình, không thả gần quân ta, nghỉ trước khi ném lại cùng khu vực. Oanh tạc cơ 9 quả, máy bay tàng hình 2, Su-25 16 rốc-két, không kích bất ngờ 10, bom chùm 30 quả con.',
        '<b>Xe tiếp đạn (mới, 4 CP):</b> điểm nạp tiền phương: trực thăng đứng cạnh hồi đạn nhanh gấp đôi, bệ phóng và xe tên lửa quanh nó nạp nhanh gấp ba. Xe công binh chỉ còn sửa chữa (3 CP).',
        '<b>Bãi đáp:</b> nhánh hạng 7: Nhà chứa (+1 trần máy bay) hoặc Phục vụ nhanh. AI địch đặt Bãi đáp trong căn cứ; phá Bãi đáp pháo đài trong Công thành được 12 CP.',
        '<b>Icon trên chiến trường:</b> cạnh thanh máu: sắp hết (vàng), hết (đỏ nhấp nháy), đang ra vòng chờ, đang hồi (vòng tiến độ mờ khi hồi chậm, sáng khi hồi đủ), lóe sáng khi đầy. Địch chỉ hiện hết đạn và đang ra vòng chờ. Bản đồ nhỏ hiện vòng chờ của ta.',
    ]
    return ("<div class='section'><h2>12b. Hệ đạn và hồi đạn</h2><ul>" + ''.join(f"<li>{i}</li>" for i in items) + "</ul></div>")


def modes_and_ai(game, h):
    """Mode results and AI difficulty (prompt 13 H, I)."""
    modes = [('Giữ cứ điểm', '7/12', '7,4', '55–65%, 6–10 phút'), ('Tử chiến (điểm theo giá CP, ngưỡng 480)', '2/6 (8/12 ở seed khác)', '8,5', '6–9 phút'),
             ('Vua đồi (ngưỡng 170)', '8/12', '7,4', '55–65%, 6–9 phút'), ('Công phá', '8/12', '4,7', '60–70%'),
             ('Công thành', '6/6', '10,7 (9,2–14)', '60–75%, 10–15 phút'), ('Phòng thủ', 'giữ HQ 6/6, mất tuyến ngoài mọi trận (phút 4–6)', '', 'mất tuyến ngoài 50–70%, giữ HQ ~4/5'),
             ('Vô tận', '', '15,1', '12–15 phút'), ('Sinh tồn', '', '12,0', '8–12 phút'), ('Săn trùm', '4/4', '18,7', '15–25 phút'),
             ('Pháo đài tuần', 'chưa thắng được từ giai đoạn 1–3', '', 'giai đoạn cuối vẫn là thử thách')]
    ai = [('Dễ', 'chọn gần như ngẫu nhiên trong bộ bài, không khắc chế; thu nhập ×0,8', '98%'),
          ('Thường', 'khắc chế cơ bản theo quân địch đang thấy; ×1', '73%'),
          ('Khó', 'khắc chế, giữ tỷ lệ đội hình, để dành CP cho xe lớn, phối hợp hỗ trợ với đợt tấn công, săn máy bay đang hồi đạn; ×1,2', '60%'),
          ('Cực khó (mới)', 'như Khó, biết trước bộ bài người chơi, dồn CP cho đợt tấn công phối hợp, đánh điểm yếu nhất, phản ứng nhanh hơn; ×1,4; tinh nhuệ 30%; thưởng ×1,8; không nhìn xuyên sương mù', '29%')]
    e = h['esc']
    return ("<div class='section'><h2>2b. Cân bằng chế độ và độ khó</h2>"
            "<p>Đo bằng bộ bài mẫu 8 thẻ, độ khó Thường, chỉ huy tự động của người chơi (2 seed trên 2–3 bản đồ mỗi chế độ; đo đủ 5 seed ở phase kiểm tra). "
            "Bên đang thua quá xa sau phút 4 (quân trên sân chênh từ 1,6 lần) được +25% thu nhập và một lần thả tiếp viện miễn phí; ở Phòng thủ và Vô tận, "
            "nếu người chơi áp đảo quá thì địch được thêm một đợt công phá. Đợt địch ở Phòng thủ và Vô tận mạnh theo <b>Sức mạnh căn cứ</b> (cùng con số hiện ở màn Căn cứ), có xe ủi, "
            "pháo công thành và pháo tầm xa bắn từ ngoài tầm tháp.</p>"
            + h['table'](['Chế độ', 'Người chơi thắng', 'Thời lượng trung vị (phút)', 'Mục tiêu'], [[e(a), e(b), e(c), e(d)] for a, b, c, d in modes])
            + "<h3>AI mua quân theo độ khó</h3><p>Logic mua quân xác định (deterministic): một hàm chấm điểm (khắc chế quân địch đang thấy, vai trò còn thiếu, giá trị thực chiến theo giá) "
            "dùng ở mức khác nhau cho mỗi độ khó. Tên độ khó thống nhất: chiến dịch và Tác chiến đổi Anh hùng → Khó, Thép → Cực khó (kỷ lục lưu theo số nên giữ nguyên).</p>"
            + h['table'](['Độ khó', 'Cách AI chơi', 'Người chơi thắng (48 trận)'], [[e(a), e(b), c] for a, b, c in ai]) + "</div>")


def late_programme(game, h, imgdir):
    """Section 7b: prompts 16-18, read from balance.json."""
    import json as _json
    from pathlib import Path
    e, img, table = h['esc'], h['img'], h['table']
    imgdir = Path(imgdir)
    text = (ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json').read_text(encoding='utf-8')
    data = _json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    names = {v['id']: v.get('name', v['id']) for v in game['vehicles'] + game.get('bosses', []) + game.get('elites', [])}
    name = lambda i: names.get(i, i)
    dtype = {'Kinetic': 'Động năng', 'ShapedCharge': 'Nổ lõm', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa',
             'Fragmentation': 'Mảnh', 'Energy': 'Năng lượng'}
    shape = {'circle': 'vùng tròn', 'strip': 'dải', 'line': 'đường thẳng', 'sweep': 'đường quét', 'missile': 'tên lửa bắn hạ được',
             'swarm': 'bầy drone', 'drop': 'thả quân', 'quake': 'rung chấn', 'buff': 'tăng lực phe mình'}
    role = {'guard': 'bảo vệ', 'repair': 'sửa boss', 'jam': 'gây nhiễu tên lửa ta', 'cover': 'phòng không che boss',
            'spot': 'đánh dấu quân ta', 'smoke': 'thả khói', 'raid': 'đột kích'}
    cards = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Cards'
    out = ["<div class='section'><h2>7b. Biển, hộ tống, bản đồ dài, roster mới và đòn lớn (prompt 16–18)</h2>"]

    # 16 A-D: the sea.
    out.append("<h3>Lighthouse Bay và hải chiến (prompt 16 A–D)</h3><ul>"
               "<li><b>Lighthouse Bay:</b> bờ biển đá, 2 vịnh có bãi và cầu tàu, hải đăng trên mũi đất (giữ nó thì thấy hạm đội), "
               "2 trận địa pháo bờ biển chiếm được (chỉ bắn tàu), làng chài và pháo đài cũ. Biển chiếm 36% map, 3 tuyến biển. "
               "Có bản Giữ cứ điểm, Sinh tồn, Công thành và bản dài.</li>"
               "<li><b>Tàu chạy trên tuyến biển:</b> xe tăng chỉ bắn tới tuyến gần từ đầu cầu tàu và mũi đất; xe săn tăng tầm trung (38–42 m) bắn được từ sườn đá.</li>"
               "<li><b>Leviathan (Kessler):</b> 9 bộ phận, giáp hông cấp 4, boong cấp 2; 3 pha: loạt pháo có cảnh báo, tên lửa hành trình, đổ tăng, "
               "trực thăng và gọi jet; pha 3 chạy ra biển theo đồng hồ, thoát được thì thua nhiệm vụ. Chết thì nghiêng, gãy đôi và chìm.</li>"
               "<li><b>Hạm đội:</b> 2 tàu hộ vệ (CIWS che Leviathan), 3 xuồng tên lửa đánh đầu cầu tàu, tàu đổ bộ.</li>"
               "<li><b>Chiến dịch và chế độ:</b> nhiệm vụ 4-11 \"Leviathan\" cuối chương 4 (mở nhánh Pháo bờ biển tầm xa của Pháo đài hạng nặng); "
               "Săn trùm tự chuyển sang Lighthouse Bay cho Leviathan rồi quay lại, mang theo quân, CP và đồng hồ; Tác chiến có mutator Bão biển và Hạm đội.</li></ul>")
    pics = [(imgdir / 'maps' / 'lighthousebay.png', 'Lighthouse Bay (Giữ cứ điểm).'),
            (imgdir / 'maps' / 'lighthousebay_siege.png', 'Lighthouse Bay, bản Công thành.'),
            (cards / 'leviathan.png', 'Leviathan.')]
    out.append(''.join(f"{img(p, 'shot')}<div class='caption'>{e(c)}</div>" for p, c in pics if p.exists()))

    # 16 E-F: escorts.
    rules = data.get('escortRules', {})
    cap = rules.get('cap', {})
    out.append("<h3>Hộ tống cho mọi boss (prompt 16 E–F)</h3><p>Mỗi boss mang một nhóm đi cùng và thêm một nhóm ở mỗi lần đổi pha; "
               f"số hộ tống còn sống tối đa theo độ khó: {e(', '.join(f'{k} {v}' for k, v in cap.items()))} (Săn trùm ít hơn). "
               "Mỗi nhóm có một xe phụ trợ (sửa boss, gây nhiễu tên lửa ta, phòng không che boss, đánh dấu quân ta) nên người chơi phải chọn đánh boss hay hộ tống trước. "
               f"Hộ tống không rời boss quá {rules.get('leash', 28)} m, hạ được thì thưởng CP, có dấu cam, và thanh máu boss đếm số hộ tống.</p>")

    def units(block):
        if not block:
            return []
        if isinstance(block, dict):
            block = block.get('units', [])
        if block and isinstance(block[0], list):
            block = [u for g in block for u in g]
        return block

    def fmt(block):
        rows = units(block)
        return ', '.join(e(name(u['unit'])) + (' ★' if u.get('elite') else '') + (f" ({role.get(u['role'], u['role'])})" if u.get('role') and u['role'] != 'guard' else '')
                         + (f" ×{u['count']}" if u.get('count', 1) > 1 else '') for u in rows)

    rows = []
    for x in data.get('escorts', []):
        phase = x.get('phases') or x.get('phase')
        if isinstance(phase, list) and phase and isinstance(phase[0], dict) and 'units' in phase[0]:
            phase_txt = ' / '.join(fmt(p) for p in phase)
        else:
            phase_txt = fmt(phase)
        rows.append([e(name(x['boss'])), fmt(x.get('arrive')), phase_txt])
    out.append(table(['Boss', 'Đi cùng', 'Khi đổi pha'], rows))

    # 17 A-B: long maps.
    out.append("<h3>Bản đồ dài và căn cứ nhiều lớp (prompt 17 A–B)</h3><ul>"
               "<li>Công thành, Phòng thủ, Vô tận và Pháo đài tuần chơi trên bản dài: 300 m ngang, 480 m dọc theo hướng tấn công (đủ cho 20 map có bản công thành, "
               "cộng Lighthouse Bay); các chế độ khác giữ map 300 × 300 m.</li>"
               "<li>Căn cứ nhiều lớp: vùng đệm (răng rồng, hào, dây thép gai, 1–4 ụ bắn), trạm tiền tiêu và 8 cứ điểm, tường ngoài có cổng chính và 2 cửa phụ, sân trong, thành trong, rồi HQ. "
               "Quân phòng thủ thả xuống trong thành; quân tấn công thả dù xa dần lên sau mỗi vòng tường bị phá.</li>"
               "<li>Ô theo cấp HQ từ 4/1/0/1 (nhỏ/vừa/lớn/tiện ích) tới 8/5/3/4; nhãn ô mới: cổng ngoài, tường ngoài, sân trong, tường trong. "
               "Một loadout dùng cho cả trại và căn cứ dài: căn cứ dài chưa chỉnh thì mượn tháp của trại.</li>"
               "<li>Camera nhìn về phía tây trên map dài (zoom mặc định 21, xa nhất 50); bản đồ nhỏ giữ hình chữ nhật.</li>"
               "<li>Tìm đường: 150 × 240 ô, 1,9 MB; một đường hết chiều dài mất 5–6 ms trên máy bàn, khoảng 35 ms trên điện thoại (đo lại ở phase kiểm tra).</li></ul>")
    pics = [(imgdir / 'maps' / 'ashfield_long.png', 'Ashfield, bản dài (Công thành).'),
            (imgdir / 'maps' / 'ashfield_long_bases.png', 'Ashfield bản dài: các ô công sự theo cỡ.'),
            (imgdir / 'maps' / 'swamp_long.png', 'Đầm lầy, bản dài.'), (imgdir / 'maps' / 'lighthousebay_long.png', 'Lighthouse Bay, bản dài.')]
    out.append(''.join(f"{img(p, 'shot')}<div class='caption'>{e(c)}</div>" for p, c in pics if p.exists()))

    # 17 C-D: roster.
    out.append("<h3>Đơn vị mới và rà soát roster (prompt 17 C–D)</h3><ul>"
               "<li><b>Mới:</b> tiêm kích tàng hình (14 CP), drone yểm trợ (6 CP, bay theo máy bay có người lái và hút tên lửa bắn vào chúng), xe tăng laser (10 CP, tia mạnh dần ×0,3 → ×2 trong 6 giây), "
               "xe mang khiên (7 CP) và tháp khiên (ô lớn), xe lô cốt (6 CP, đứng yên 3 giây thì đào hầm: giáp trước dày hơn, tầm +30%), "
               "máy bay mẹ thả 8 drone FPV (8 CP), tháp tiếp sóng CP (ô nhỏ, tối đa 2 mỗi căn cứ). Giá đo bằng bộ đo giá trị thực chiến.</li>"
               "<li><b>Gộp:</b> A-10 vào Cường kích (model Su-25, cả hai bộ vũ khí và 2 Kh-29, 15 CP); Ka-52 vào Trực thăng tấn công (giữ Hellfire tầm 55 m và Stinger, 11 CP); "
               "xe ATGM vào xe phóng drone FPV; công binh phá mìn vào Công binh; ụ súng vào tháp pháo. Model cũ giữ làm mẫu phụ.</li>"
               "<li><b>Tăng hai nòng và tăng hạng nặng:</b> tăng hai nòng bắn 2 phát 120 mm một lượt, nạp 7 giây, hạ xe tăng nhanh nhất (37,9 s); "
               "tăng hạng nặng đổi sang đạn nổ khi bắn công trình và xe nhẹ, 12 CP, sống dai và phá công trình tốt nhất theo CP.</li>"
               "<li><b>Save:</b> giữ hạng cao hơn, hoàn xu và bản thiết kế của thẻ hạng thấp; Ka-52 đã mua được hoàn 3.500 xu; ụ súng trong loadout thành tháp pháo.</li></ul>")

    # 18: big attacks.
    br = data.get('bigAttackRules', {})
    diff = br.get('difficulty', {})
    out.append("<h3>Đòn lớn của mọi boss (prompt 18)</h3><p>Mỗi boss có một đòn lớn lấy từ cùng một hệ dữ liệu (mẫu hình dạng + tham số). "
               f"Đòn đầu tiên khoảng {br.get('first', 30)} giây sau khi boss xuất hiện; luôn có cảnh báo trên mặt đất; phá bộ phận mang đòn trong lúc cảnh báo thì đòn yếu đi hoặc bị hủy; "
               "quân ta biết né khỏi vùng cảnh báo. Theo độ khó: "
               + e('; '.join(f"{k} sát thương ×{v.get('damage', 1)}, hồi ×{v.get('cooldown', 1)}" + (f", cảnh báo +{v['warn']} s" if v.get('warn') else '') for k, v in diff.items()))
               + ".</p>")
    owner = {v['bigAttack']: v['id'] for v in data['vehicles'] if v.get('bigAttack')}
    rows = []
    for a in data.get('bigAttacks', []):
        parts, strikes = set(), []
        for s in a['strikes']:
            parts |= set(s.get('parts', []))
            bits = [shape.get(s.get('shape'), s.get('shape', ''))]
            if s.get('count', 1) > 1:
                bits.append(f"{s['count']} phát")
            if s.get('damage'):
                bits.append(f"{s['damage']:g} {dtype.get(s.get('type'), s.get('type', ''))}" + (f", xuyên {s['pen']}" if 'pen' in s else ''))
            if s.get('radius'):
                bits.append(f"bán kính {s['radius']:g} m")
            if s.get('length'):
                bits.append(f"dài {s['length']:g} m")
            if s.get('hp'):
                bits.append(f"{s['hp']:g} máu, bắn hạ được")
            if s.get('stun'):
                bits.append(f"choáng {s['stun']:g} s")
            if s.get('units'):
                bits.append(f"{len(s['units']) if isinstance(s['units'], list) else s['units']} xe")
            strikes.append(', '.join(bits))
        rows.append([e(name(owner.get(a['id'], ''))), e(a['id']), e('; '.join(strikes)), f"{a.get('warn', '')} s", f"{a.get('cooldown', '')} s",
                     e(', '.join(sorted(parts)) or '—')])
    out.append(table(['Boss', 'Đòn', 'Gồm', 'Cảnh báo', 'Hồi', 'Bộ phận ngắt'], rows))
    out.append("<p>Bộ phận mới: bệ dựng tên lửa của Doomsday Train, khoang bom của Hive Carrier và của Khí cầu chỉ huy. "
               "Prompt 19: đòn của Icarus là mưa thanh tungsten từ vệ tinh (thay cho tia laser quét); từ prompt 20 mini boss dùng đòn lớn thu nhỏ (sát thương ×0,7, hồi chiêu ×1,3).</p>")
    out.append('</div>')
    return ''.join(out)


def props_and_rounds(game, h, sizes, weapons, owners):
    """Map props and every round model, with their sizes."""
    e, table = h['esc'], h['table']

    def box(model, scale=1.0):
        s = sizes.get(model or '')
        return f"{s[2] * scale:.2f} × {s[0] * scale:.2f} × {s[1] * scale:.2f}" if s else '—'

    prop_rows = []
    for p in game.get('props', []):
        raw = p.get('raw', {})
        sc = raw.get('Scale', 1) or 1
        prop_rows.append([e(p.get('name') or p['id']), f"<code>{e(p['id'])}</code>", e(str(raw.get('Kind', '') or '')), str(raw.get('MaxHp', '') or '—'),
                          f"{raw.get('Width', 0) or 0:.1f} × {raw.get('Depth', 0) or 0:.1f}", 'có' if raw.get('BlocksMovement') else '—',
                          'có' if raw.get('BlocksFire') else '—', 'có' if raw.get('Crushable') else '—', 'bất tử' if raw.get('Indestructible') else '—',
                          box(p['id'], sc)])
    round_rows = []
    seen = set()
    for wid in sorted(weapons):
        w = weapons[wid]
        raw = w.get('raw', {})
        model = raw.get('ProjectileModel') or ''
        scale = raw.get('ProjectileScale', 1) or 1
        if not model or (model, scale) in seen:
            continue
        seen.add((model, scale))
        round_rows.append([f"<code>{e(model)}</code>", f"{scale:g}", box(model, scale), f"<code>{e(wid)}</code>", e(w.get('real') or ''),
                           f"{(raw.get('Size', 0) or 0):g}"])
    out = ""
    if prop_rows:
        out += f"<h3>Công trình và vật thể trên bản đồ ({len(prop_rows)})</h3>" + table(
            ['Tên', 'Id', 'Loại', 'Máu', 'Rộng × sâu (m)', 'Chặn xe', 'Chặn đạn', 'Bị nghiền', 'Bất tử', 'Model: dài × rộng × cao (m)'], prop_rows, 'dps')
    if round_rows:
        out += f"<h3>Kích thước đạn ({len(round_rows)} model)</h3><p class='muted'>Kích thước model đạn nhân tỷ lệ của vũ khí (projectileScale).</p>" + table(
            ['Model đạn', 'Tỷ lệ', 'Dài × rộng × cao (m)', 'Vũ khí', 'Tên thật', 'Cỡ (mm)'], round_rows, 'dps')
    return out


def boss_summary(game, h):
    """Section 10d: the bosses side by side."""
    import json as _json
    e, table = h['esc'], h['table']
    text = (ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json').read_text(encoding='utf-8')
    data = _json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    big = {v['id']: v.get('bigAttack') for v in data['vehicles'] if v.get('bigAttack')}
    attacks = {a['id']: a for a in data.get('bigAttacks', [])}
    escorts = {x['boss']: x for x in data.get('escorts', [])}

    def escort_count(x):
        n = 0
        for part in (x.get('arrive'), x.get('phase'), x.get('phases')):
            if not part:
                continue
            groups = part if isinstance(part, list) and part and isinstance(part[0], dict) and 'units' in part[0] else [part]
            for g in groups:
                units = g.get('units', []) if isinstance(g, dict) else g
                n += sum(u.get('count', 1) for u in units if isinstance(u, dict))
        return n

    gen_names = {x['id']: x.get('name', x['id']) for x in game.get('generals', []) + game.get('characters', [])}
    gen_names = {**{k: v for k, v in game.get('bossGenerals', {}).items() if v}, **gen_names}
    rows = []
    for v in sorted(game.get('bosses', []), key=lambda v: (str(v.get('raw', {}).get('Rank', '')), -float(v.get('hp', 0) or 0))):
        raw = v.get('raw', {})
        a = v.get('armour') or {}
        parts = v.get('parts') or []
        d = v.get('dpsVs', {})
        att = attacks.get(big.get(v['id'], '') or '', {})
        strike = (att.get('strikes') or [{}])[0]
        big_txt = (f"{att.get('id', '')}: {strike.get('count', 1)} × {strike.get('damage', 0):g}, hồi {att.get('cooldown', '')} s" if att else '—')
        rows.append([e(v['name']), 'mini' if raw.get('MiniBoss') else 'chủ lực', e(gen_names.get(str(raw.get('General', '') or ''), str(raw.get('General', '') or '—'))),
                     f"{float(v.get('hp', 0) or 0):,.0f}".replace(',', '.'),
                     f"{a.get('front', 0)}/{a.get('side', 0)}/{a.get('rear', 0)}/{a.get('top', 0)}",
                     f"{len(parts)} ({sum(p.get('hp', 0) for p in parts) * 100:.0f}%)",
                     f"{float(d.get('Light', 0)):.0f}", f"{float(d.get('Heavy', 0)):.0f}", f"{float(d.get('Air', 0)):.0f}", f"{float(d.get('Structure', 0)):.0f}",
                     *unit_reach(v)[:3], e(big_txt), str(escort_count(escorts[v['id']])) if v['id'] in escorts else '—'])
    return ("<div class='section'><h2>10d. Tổng hợp boss</h2>"
            "<p>Mọi boss và mini boss cạnh nhau, đọc từ dữ liệu hiện tại: máu thân (trước hệ số độ khó), giáp trước/hông/sau/nóc, số bộ phận và phần máu của chúng, "
            "DPS duy trì lên xe nhẹ, xe nặng, máy bay và công trình (trước giáp), đòn lớn đầu tiên và số hộ tống trong mọi đợt.</p>"
            + table(['Boss', 'Cấp', 'Tướng', 'Máu', 'Giáp T/H/S/N', 'Bộ phận', 'DPS nhẹ', 'DPS nặng', 'DPS bay', 'DPS công trình', 'Tầm xa nhất', 'Tầm mặt đất', 'Tầm máy bay', 'Đòn lớn', 'Hộ tống'], rows, 'dps')
            + "</div>")


KIND_VI = {'EnemyWave': 'viện quân địch', 'AllyWave': 'tiếp viện Accord', 'Barrage': 'pháo kích dồn', 'AirRaid': 'không kích địch',
           'CounterBattery': 'phản pháo', 'AllyAirStrike': 'Hawk không kích', 'AllyArtillery': 'pháo Accord yểm trợ', 'GeneralField': 'tướng địch ra trận',
           'SideObjective': 'mục tiêu phụ', 'NeutralConvoy': 'đoàn tiếp tế trung lập', 'LootDrop': 'kho thả dù', 'SupplyRaid': 'địch cướp tiếp tế',
           'SupplyDrop': 'thả dù tiếp tế', 'IntelReveal': 'Nadia báo vị trí', 'Blackout': 'bão nhiễu điện tử', 'MiniBoss': 'mini boss giữa trận',
           'PlanChange': 'đổi kế hoạch', 'WeatherShift': 'đổi thời tiết / ngày đêm', 'Ceasefire': 'đồng hồ ngừng bắn', 'OrbitalStrike': 'vệ tinh bắn thử'}


def mission_events(game, h):
    """Section 7c (prompt 23): the mission events, the reinforcement rules by difficulty and the in-battle dialogue."""
    import json as _json
    import collections
    e, table = h['esc'], h['table']
    text = (ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'campaign.json').read_text(encoding='utf-8-sig')
    camp = _json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    lib = camp.get('eventLibrary', {})
    rules, events = lib.get('rules', {}), lib.get('events', [])
    diff_vi = {'Easy': 'Dễ', 'Normal': 'Thường', 'Hard': 'Khó', 'VeryHard': 'Cực khó'}
    drows = []
    for k, d in rules.get('difficulty', {}).items():
        dirs = d.get('directions', [])
        drows.append([diff_vi.get(k, k), f"{dirs[0]}–{dirs[-1]}" if dirs else '—', f"{d.get('warning', 0):g} s", f"{d.get('ally', 0) * 100:.0f}%",
                      f"×{d.get('waveScale', 1):g}", 'có' if d.get('elites') else '—',
                      'không giới hạn' if d.get('allyWaves', -1) < 0 else f"{d['allyWaves']} đợt", str(d.get('escorts', ''))])
    gen_names = {x['id']: x.get('name', x['id']) for x in game.get('generals', []) + game.get('characters', [])}
    gen_names = {**{k: v for k, v in game.get('bossGenerals', {}).items() if v}, **gen_names}
    names = {v['id']: v.get('short') or v['name'] for v in game.get('vehicles', []) + game.get('elites', []) + game.get('bosses', [])}
    grows = [[e(gen_names.get(g, g)), e(', '.join(names.get(u, u) for u in x.get('roster', []))), e(', '.join(x.get('delivery', []))),
              e(names.get(x.get('elite', ''), x.get('elite', '') or '—')), str(x.get('lastChapter', '—'))]
             for g, x in rules.get('generals', {}).items()]
    words = {'at': lambda v: f"lúc {v:g} s", 'progress': lambda v: f"tiến độ {v * 100:.0f}%", 'bossHp': lambda v: f"máu boss {v * 100:.0f}%",
             'delay': lambda v: f"trễ {v:g} s", 'repeat': lambda v: f"lặp mỗi {v:g} s"}

    def trig(t):
        out = []
        for k, v in (t or {}).items():
            if isinstance(v, (int, float)) and k in words:
                out.append(words[k](v))
            elif isinstance(v, (int, float, str)):
                out.append(f"{k} {v}")
            else:
                out.append(k)
        return ', '.join(out) or '—'

    erows = [[f"<code>{e(x['id'])}</code>", e(KIND_VI.get(x['kind'], x['kind'])), e(trig(x.get('trigger'))),
              e(', '.join(f"{k} {v}" for k, v in (x.get('params') or {}).items() if not isinstance(v, (dict, list)))[:90] or '—')] for x in events]
    lib_kind = {x['id']: x['kind'] for x in events}
    by_chapter = collections.OrderedDict()
    for m in camp.get('missions', []):
        b = by_chapter.setdefault(m.get('chapter'), {'missions': 0, 'events': 0, 'kinds': collections.Counter(), 'general': 0})
        b['missions'] += 1
        refs = []

        def walk(o):
            # A mission's own events and each stage's (an operation's stages carry their own).
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'missionEvents' and isinstance(v, list):
                        refs.extend(v)
                    else:
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(m)
        for ref in refs:
            k = lib_kind.get(ref if isinstance(ref, str) else ref.get('id', ''), '')
            b['events'] += 1
            b['kinds'][k] += 1
            b['general'] += k == 'GeneralField'
    chapters = {c.get('number'): c for c in game.get('chapters', [])}
    crows = []
    for ch, b in by_chapter.items():
        c = chapters.get(ch, {})
        top = ', '.join(f"{KIND_VI.get(k, k)} ×{n}" for k, n in b['kinds'].most_common(5) if k)
        crows.append([str(ch), e(str(c.get('title') or c.get('id') or '')), str(b['missions']), str(b['events']), str(b['general']), e(top)])
    total = sum(b['events'] for b in by_chapter.values())
    caps = rules.get('caps', {})
    sight = rules.get('weatherSight', {})
    return ("<div class='section'><h2>7c. Sự kiện trong nhiệm vụ và thoại trong trận (prompt 23)</h2>"
            f"<p>Mỗi nhiệm vụ ghép từ thư viện sự kiện dạng dữ liệu ({len(events)} sự kiện, {len(set(x['kind'] for x in events))} loại); cả chiến dịch có {total} sự kiện. "
            "Sự kiện kích hoạt theo thời gian, tiến độ nhiệm vụ, máu boss, số quân trên sân hoặc sau một sự kiện khác; chạy theo seed và vào chuỗi lệnh của trận "
            "nên replay và checkpoint khôi phục đúng. Mọi sự kiện lớn được báo trước bằng thông báo ở mép trên, một câu thoại và mũi tên hướng trên bản đồ nhỏ; "
            f"quân địch không bao giờ xuất hiện trong vòng {rules.get('nearSight', 45)} m quanh quân người chơi. Viện quân có trần riêng ngoài trần quân thường: "
            f"{caps.get('enemy', '—')} xe địch, {caps.get('ally', '—')} xe Accord. Tướng địch rút lui khi còn {rules.get('retreatAt', 0.3) * 100:.0f}% máu, trừ ở trận cuối của mình; "
            f"từ chương {rules.get('miniFrom', 4)} tướng ra trận bằng mini boss thay vì xe tinh nhuệ. Các con số là điểm khởi đầu, chờ đợt mô phỏng 5 seed.</p>"
            "<h3>Viện quân theo độ khó</h3>"
            + table(['Độ khó', 'Số hướng', 'Cảnh báo', 'Tiếp viện ta (so với một đợt địch)', 'Cỡ đợt địch', 'Có tinh nhuệ', 'Số đợt tiếp viện ta', 'Hộ tống tướng'], drows)
            + "<h3>Viện quân theo tướng</h3>" + table(['Tướng', 'Thành phần', 'Cách tới', 'Xe tinh nhuệ', 'Chương cuối'], grows)
            + f"<h3>Thư viện sự kiện ({len(events)})</h3>" + table(['Id', 'Loại', 'Kích hoạt', 'Tham số'], erows, 'dps')
            + "<h3>Sự kiện theo chương</h3>" + table(['Chương', 'Tên', 'Số màn', 'Số sự kiện', 'Tướng ra trận', 'Loại dùng nhiều nhất'], crows, 'dps')
            + "<h3>Tầm nhìn theo thời tiết</h3>" + table(['Thời tiết', 'Hệ số tầm nhìn'], [[e(k), f"×{v:g}"] for k, v in sight.items()])
            + "<h3>Thoại trong trận</h3><p>Mọi lời nhân vật trong trận là một dòng chữ kiểu phụ đề ngay trên khay thẻ: tên người nói in đậm, màu theo phe (ta xanh nhạt, "
            "địch đỏ đậm), rồi câu thoại; nền chỉ là một dải tối mờ, rộng tối đa nửa màn hình, tối đa 2 dòng, không chân dung, không lồng tiếng. Một câu một lúc, "
            "theo mức ưu tiên: cốt truyện, cảnh báo, sự kiện, phản ứng. Câu cốt truyện và cảnh báo xếp hàng (cảnh báo quá 12 s thì bỏ); câu sự kiện và phản ứng "
            "hiện ngay hoặc bỏ, cách nhau tối thiểu 9 s (20 s cho câu phản ứng khi có boss trên sân). Mỗi câu hiện 3–6 s theo độ dài, mờ dần 0,25 s, không bao giờ "
            "dừng trận. Nhật ký 20 câu gần nhất mở từ menu tạm dừng. Cài đặt: Đầy đủ / Chỉ quan trọng / Tắt (câu cốt truyện luôn hiện). Sáu khoảnh khắc cốt truyện "
            "làm trận chậm 0,5 lần trong khi 2–3 câu liên tiếp chạy: Hollow Dam, Venn mất bầy drone, Thorne phản bội, Thorne trên Typhon, Varga ngã xuống, Icarus rơi.</p>"
            + "</div>")


def commanders(game, h):
    """Section 12c (prompt 22 F): the player's commanders and the enemy generals' passives, as the game words them."""
    e, table = h['esc'], h['table']
    fam = {'Combat': 'chiến đấu', 'Economy': 'kinh tế', 'General': 'tướng địch'}
    cs = game.get('commanders', [])
    mine = [[f"<b>{e(c['name'])}</b><br><span class='muted'>{e(c.get('call', ''))}</span>", fam.get(c['family'], c['family']), e(c.get('role', '')),
             e(c.get('style', '')), e(c.get('strength', '')), e(c.get('weakness', '')), e(c.get('unlock', ''))]
            for c in cs if c['family'] != 'General']
    gens = [[f"<b>{e(c['name'])}</b>", e(c.get('strength', '')), e(c.get('weakness', ''))] for c in cs if c['family'] == 'General']
    return ("<div class='section'><h2>12c. Commander</h2>"
            "<p>Người chơi chọn một commander trước trận; nội tại của nó áp cho cả phe, trong mọi chế độ. Mỗi màn gắn với một tướng địch "
            "thì địch mang nội tại của tướng đó. Commander mở dần theo chương. Không còn chọn học thuyết riêng: lợi thế của năm học thuyết cũ "
            "đã gộp vào commander hợp lối chơi (Crown: thiết giáp, Hawk: không quân, Longshot: pháo binh, Rush: chớp nhoáng, Ledger: hậu cần), "
            "chỗ trùng loại thưởng thì gộp thành một con số, không cộng dồn; bảng dưới là số mới.</p>"
            f"<h3>Commander của người chơi ({len(mine)})</h3>"
            + table(['Commander', 'Nhóm', 'Vai trò', 'Hợp lối chơi', 'Điểm mạnh', 'Điểm yếu', 'Mở khóa'], mine)
            + f"<h3>Nội tại của tướng địch ({len(gens)})</h3>" + table(['Tướng', 'Điểm mạnh', 'Điểm yếu'], gens)
            + "</div>")


def price_list(game, h, unlock_text):
    """Section 12b (play-test 8): every price in one place: cards, base towers, supports and items."""
    e, table = h['esc'], h['table']
    eco = game.get('economy', {})
    money = lambda n: f"{n:,}".replace(',', '.')
    route_vi = {'Starter': 'có sẵn', 'Premium': 'cao cấp', 'Campaign': 'chiến dịch'}
    cards = [[e(v['name']), e(v.get('class', '')), f"{v['cost']}", route_vi.get(v.get('route'), v.get('route', '')), money(v.get('coins', 0))]
             for v in sorted(game.get('vehicles', []), key=lambda v: (v['cost'], v['name']))]
    names = {t['id']: t['name'] for t in game.get('towers', [])}
    size_vi = {'Small': 'nhỏ', 'Medium': 'vừa', 'Large': 'lớn', 'Utility': 'tiện ích'}
    towers = []
    for t in game.get('base', {}).get('towers', []):
        v = next((x for x in game.get('towers', []) if x['id'] == t['id']), {})
        towers.append([e(t.get('name') or names.get(t['id'], t['id'])), size_vi.get(t.get('size'), t.get('size', '')), f"{t.get('rebuildCp', 0)}",
                       f"{t.get('rebuildSeconds', 0):g}", route_vi.get(v.get('route'), v.get('route', '') or '—'), money(v.get('coins', 0)) if v else '—',
                       e(', '.join(b['name'] for b in t.get('branches', [])) or '—')])
    sups = [[e(s['name']), e(s['kind']), f"{s['cost']}", route_vi.get(s.get('route'), s.get('route', '')), money(s.get('coins', 0))]
            for s in game.get('supports', []) if s['cost'] and not s.get('consumable') and not s.get('eventOnly')]
    items = [[e(s['name']), e(s['kind']), money(s.get('coins', 0)), f"{eco.get('itemPack', 2)}", money(round(s.get('coins', 0) / max(1, eco.get('itemPack', 2))))]
             for s in game.get('supports', []) if s.get('consumable')]
    return ("<div class='section'><h2>12b. Bảng giá</h2>"
            "<p>Mọi giá trong game ở một chỗ. <b>CP</b> là điểm chỉ huy trả mỗi lần gọi trong trận. <b>Xu</b> là tiền duy nhất ngoài trận: mua thẻ cao cấp, "
            "mua sớm thẻ chiến dịch trước khi thắng màn mở khóa, mua vật phẩm. Thẻ có sẵn không cần mua. Giá lên hạng thẻ, hòm và gói xu ở phần kinh tế.</p>"
            f"<h3>Thẻ xe ({len(cards)})</h3>" + table(['Thẻ', 'Lớp', 'CP mỗi lần gọi', 'Cách có', 'Giá mua (xu)'], cards, 'dps')
            + f"<h3>Tháp căn cứ ({len(towers)})</h3><p class='muted'>Tháp không tốn CP khi đặt vào căn cứ: nó chiếm một ô theo cỡ. Bị phá trong trận thì xây lại bằng CP sau một thời gian chờ.</p>"
            + table(['Tháp', 'Ô', 'Xây lại (CP)', 'Chờ xây lại (s)', 'Cách có', 'Giá mua (xu)', 'Nhánh'], towers, 'dps')
            + f"<h3>Thẻ hỗ trợ ({len(sups)})</h3>" + table(['Hỗ trợ', 'Loại', 'CP mỗi lần gọi', 'Cách có', 'Giá mua (xu)'], sups, 'dps')
            + f"<h3>Vật phẩm dùng một lần ({len(items)})</h3>" + table(['Vật phẩm', 'Loại', 'Giá một gói (xu)', 'Số cái mỗi gói', 'Xu mỗi cái'], items, 'dps')
            + "</div>")


def blast_radii(game, h):
    """Section 10c: every blast radius in the game."""
    import json as _json
    e, table = h['esc'], h['table']
    ordnance = {'Bomb', 'GuidedBomb', 'Cluster', 'HeavyBomb', 'CarBomb', 'Napalm', 'Atgm', 'Sam', 'Cruise', 'Ballistic', 'RocketSmall', 'RocketBig',
                'HeShell', 'MortarBomb', 'SuperShell', 'Airburst', 'Grenade', 'Fpv', 'Shahed', 'Lancet', 'Rail', 'Dart', 'DoubleDart'}
    dtype = {'Kinetic': 'Động năng', 'ShapedCharge': 'Nổ lõm', 'HighExplosive': 'Nổ mạnh', 'Fire': 'Lửa', 'Fragmentation': 'Mảnh', 'Energy': 'Năng lượng'}
    weapons, owners = {}, {}
    for group in ('vehicles', 'elites', 'bosses', 'towers', 'itemVehicles'):
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                weapons.setdefault(w['id'], w)
                owners.setdefault(w['id'], []).append(v.get('short') or v['name'])
    rows = []
    for wid, w in weapons.items():
        raw = w.get('raw', {})
        form = str(raw.get('Form', w.get('form', '')))
        splash = float(w.get('splash', 0) or raw.get('SplashRadius', 0) or 0)
        if form not in ordnance and splash <= 0:
            continue
        rows.append((splash, [f"<code>{e(wid)}</code>", e(w.get('real') or ''), e(form), e(', '.join(sorted(set(owners[wid])))[:50]),
                              f"{round(splash, 1):g}" if splash > 0 else 'trúng trực tiếp', f"{float(w.get('damage', 0) or 0):g}", e(dtype.get(w.get('type'), w.get('type', ''))),
                              str(w.get('pen', '')), 'có' if raw.get('Thermobaric') else '—', 'có' if raw.get('Splashes') else '—', 'có' if raw.get('Cluster') else '—']))
    rows.sort(key=lambda r: -r[0])
    sup_rows = []
    for s in sorted(game.get('supports', []), key=lambda s: -(s.get('radius') or 0)):
        if not s.get('radius') and not s.get('damage'):
            continue
        sup_rows.append([e(s.get('name') or s['id']), f"<code>{e(s['id'])}</code>", f"{s.get('count', 1) or 1}", f"{float(s.get('damage', 0) or 0):g}",
                         f"{round(float(s.get('radius', 0) or 0), 1):g}", e(dtype.get(s.get('type'), s.get('type', '') or '')), f"{s.get('cost', '')}", f"{s.get('cooldown', '')}"])
    text = (ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json').read_text(encoding='utf-8')
    data = _json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    owner = {v.get('bigAttack'): v['id'] for v in data['vehicles'] if v.get('bigAttack')}
    names = {v['id']: v.get('name', v['id']) for v in game.get('bosses', []) + game.get('vehicles', [])}
    big_rows = []
    for a in data.get('bigAttacks', []):
        for st in a.get('strikes', []):
            r = st.get('radius') or st.get('area') or 0
            big_rows.append([e(names.get(owner.get(a['id'], ''), owner.get(a['id'], ''))), f"<code>{e(a['id'])}</code>", e(st.get('shape', '')), f"{st.get('count', 1)}",
                             f"{st.get('damage', 0):g}" if st.get('damage') else '—', f"{r:g}" if r else '—',
                             f"{st.get('length'):g} × {st.get('width', 0):g}" if st.get('length') else '—', e(dtype.get(st.get('type'), st.get('type', '') or ''))])
    death_rows = []
    for group, label in (('vehicles', 'xe'), ('elites', 'tinh nhuệ'), ('bosses', 'boss'), ('towers', 'tháp')):
        for v in game.get(group, []):
            if v.get('death'):
                death_rows.append((float(v.get('deathRadius', 0) or 0), [e(v['name']), label, f"{float(v['death']):g}", f"{round(float(v.get('deathRadius', 0) or 0), 1):g}"]))
    death_rows.sort(key=lambda r: -r[0])
    return ("<div class='section'><h2>10c. Tầm nổ</h2>"
            "<p>Bán kính nổ lan (m) của mọi bom, tên lửa, rốc-két, đạn pháo và drone; của các thẻ hỗ trợ hỏa lực; của đòn lớn của boss; và của vụ nổ khi xe, tháp, boss bị phá. "
            "\"Trúng trực tiếp\" là quả chỉ gây sát thương cho mục tiêu nó trúng. Sát thương là mỗi phát, trước giáp.</p>"
            f"<h3>Bom, tên lửa, rốc-két, đạn pháo, drone ({len(rows)})</h3>"
            + table(['Vũ khí', 'Tên thật', 'Dạng', 'Trên', 'Bán kính nổ (m)', 'Sát thương', 'Loại', 'Xuyên', 'Nhiệt áp', 'Nổ lan', 'Chùm'], [r for _, r in rows], 'dps')
            + f"<h3>Hỗ trợ hỏa lực ({len(sup_rows)})</h3>"
            + table(['Thẻ', 'Id', 'Số quả', 'Sát thương mỗi quả', 'Bán kính (m)', 'Loại', 'CP', 'Hồi (s)'], sup_rows, 'dps')
            + f"<h3>Đòn lớn của boss ({len(big_rows)} đợt)</h3>"
            + table(['Boss', 'Đòn', 'Dạng', 'Số phát', 'Sát thương', 'Bán kính (m)', 'Dải dài × rộng (m)', 'Loại'], big_rows, 'dps')
            + f"<h3>Vụ nổ khi bị phá ({len(death_rows)})</h3>"
            + table(['Đơn vị', 'Loại', 'Sát thương', 'Bán kính (m)'], [r for _, r in death_rows], 'dps')
            + "</div>")


def unit_reach(v):
    """A unit's reach: its longest weapon, its longest against ground and against air, and its shortest minimum range."""
    ws = [w for w in v.get('weapons', []) if (w.get('damage') or 0) > 0]
    far = max((float(w.get('range', 0) or 0) for w in ws), default=0)
    ground = max((float(w.get('range', 0) or 0) for w in ws if w.get('targets') in ('Ground', 'All')), default=0)
    air = max((float(w.get('range', 0) or 0) for w in ws if w.get('targets') in ('Air', 'All')), default=0)
    mins = [float(w.get('minRange', 0) or 0) for w in ws if (w.get('minRange') or 0) > 0]
    fmt = lambda x: f"{x:g}" if x else '—'
    return fmt(round(far, 1)), fmt(round(ground, 1)), fmt(round(air, 1)), fmt(round(min(mins), 1)) if mins else '—'


def rates_and_ballistics(game, h):
    """Section 10b: every weapon's rate of fire, magazine and reload, and its ballistics; every unit's movement and size."""
    e, table = h['esc'], h['table']
    tgt = {'Ground': 'mặt đất', 'Air': 'trên không', 'All': 'tất cả'}

    def f(x, n=2):
        if x in (None, '', 0, 0.0):
            return '—'
        if not isinstance(x, float):
            return str(x)
        t = f"{x:.{n}f}"
        return t.rstrip('0').rstrip('.') if '.' in t else t

    weapons, owners = {}, {}
    for group in ('vehicles', 'elites', 'bosses', 'towers', 'itemVehicles'):
        for v in game.get(group, []):
            for w in v.get('weapons', []):
                weapons.setdefault(w['id'], w)
                owners.setdefault(w['id'], []).append(v.get('short') or v['name'])
    rate_rows, ball_rows = [], []
    for wid in sorted(weapons):
        w = weapons[wid]
        raw = w.get('raw', {})
        cd = raw.get('Cooldown', w.get('cooldown') or 0) or 0
        burst = raw.get('Burst', w.get('burst', 1)) or 1
        gap = raw.get('BurstInterval', 0) or 0
        clip = raw.get('Clip', w.get('clip', 0)) or 0
        clip_reload = raw.get('ClipReload', w.get('clipReload', 0)) or 0
        ammo = raw.get('Ammo', 0) or 0
        reload = raw.get('Reload', 0) or 0
        dmg = w.get('damage', 0) or 0
        # Rounds a second while it fires: inside a burst its gap, else its cooldown.
        rate = (1 / gap) if burst > 1 and gap > 0 else ((1 / cd) if cd > 0 else 0)
        stream = (clip / rate) if clip and rate else ((burst * gap) if burst > 1 and gap > 0 else 0)
        rest = clip_reload if clip else (cd if burst > 1 else 0)
        burst_dps = dmg * rate
        cycle = f"băng {clip}" if clip else (f"loạt {burst}" if burst > 1 else "từng phát")
        launcher = f"{ammo} lượt, nạp {f(reload, 1)} s" if ammo else '—'
        per_cycle, cycle_s = raw.get('RoundsPerCycle', 0) or 0, raw.get('CycleSeconds', 0) or 0
        avg = (per_cycle / cycle_s) if per_cycle and cycle_s else 0
        rate_rows.append([f"<code>{e(wid)}</code>", e(w.get('real') or ''), e(', '.join(sorted(set(owners[wid])))[:60]),
                          f(rate, 2), f(rate * 60, 0) if rate else '—', f(avg, 2), e(cycle), f(stream, 2), f(rest, 2), e(launcher),
                          f(float(dmg), 1), f(burst_dps, 0), f(float(w.get('dps', 0)), 0)])
        speed = w.get('speed') or raw.get('ProjectileSpeed', 0) or 0
        rng = w.get('range', 0) or 0
        flight = (rng / speed) if speed else 0
        tags = [t for t, on in (('dẫn đường', raw.get('Guided')), ('bắn cầu vồng', raw.get('Indirect')), ('tia', raw.get('Beam')),
                                ('cận chiến', raw.get('Melee')), ('xuyên qua', raw.get('Pierce')), ('chùm', raw.get('Cluster')),
                                ('chỉ đánh chặn', raw.get('InterceptOnly')), ('đánh nóc', raw.get('TopAttack'))) if on]
        ball_rows.append([f"<code>{e(wid)}</code>", f(raw.get('Size', 0), 1), e(str(raw.get('Family', ''))), e(str(raw.get('Form', w.get('form', '')))),
                          f(float(speed), 0), f(flight, 2), f(float(rng), 0), f(float(w.get('minRange', 0) or 0), 0),
                          f(float(w.get('splash', 0) or 0), 1), e(tgt.get(w.get('targets'), w.get('targets', ''))), e(str(raw.get('Ceiling', '') or '—')),
                          str(w.get('pen', '')), f(raw.get('FlareResist', 0), 2), e(', '.join(tags) or '—')])
    sizes = game.get('modelSizes', {})

    def drawn(model, scale, fit=0):
        s = sizes.get(model or '')
        if not s:
            return '—'
        # Prompt 25 B1: a vehicle with a modelSize has its model's length fitted to it (VehicleView.DrawScaleOf).
        k = fit / s[2] if fit and s[2] else (scale or 1)
        return f"{s[2] * k:.1f} × {s[0] * k:.1f} × {s[1] * k:.1f}"

    def deg(rad):
        # Prompt 25 C.4: VehicleDef keeps turn rates in radians a second (balance.json gives degrees); shown in degrees.
        return float(rad) * 180 / math.pi if rad else 0

    move_rows = []
    for group, label in (('vehicles', 'xe'), ('itemVehicles', 'vật phẩm'), ('elites', 'tinh nhuệ'), ('bosses', 'boss'), ('towers', 'tháp')):
        for v in game.get(group, []):
            raw = v.get('raw', {})
            scale = raw.get('Scale', 1) or 1
            if v.get('flying') and not raw.get('Boss'):
                scale *= 0.85   # aircraft are drawn 15 % smaller (DECISIONS 21H)
            move_rows.append([e(v['name']), label, f(float(v.get('speed', 0) or 0), 1), f(deg(raw.get('TurnRate', 0)), 0), f(deg(raw.get('TurretTurnRate', 0)), 0),
                              f(raw.get('Length', 0), 1), f(raw.get('Width', 0), 1), f(raw.get('HullRadius', 0), 1), f(float(v.get('vision', 0) or 0), 0),
                              f(raw.get('Standoff', 0), 0), f(raw.get('RearmTime', 0), 1), 'có' if raw.get('Stealth') else '—',
                              f(raw.get('MaxPerSide', 0), 0), *unit_reach(v), drawn(v.get('model'), scale, raw.get('ModelLength', 0) or 0)])
    return ("<div class='section'><h2>10b. Nhịp bắn, nạp đạn, đường đạn và di chuyển</h2>"
            "<p>Đọc thẳng từ dữ liệu game. <b>Viên/s</b> là nhịp khi đang bắn (trong một loạt, hoặc giữa hai phát). <b>Xả</b> là thời gian hết một băng hay một loạt. "
            "<b>Nghỉ/nạp</b> là thời gian thay băng hay nghỉ giữa hai loạt. <b>Bệ phóng</b> là số lượt bắn trước khi phải nạp lại cả bệ. "
            "<b>TB viên/s</b> tính cả thời gian nghỉ và nạp. <b>DPS khi xả</b> là sát thương mỗi giây trong lúc bắn, trước giáp; <b>DPS duy trì</b> tính cả thời gian nạp (prompt 13). "
            "<b>Xoay thân / tháp</b> tính bằng độ mỗi giây, như balance.json (mã giữ radian mỗi giây; bản trước in số radian dưới nhãn °/s, prompt 25 C.4).</p>"
            f"<h3>Nhịp bắn và nạp đạn ({len(rate_rows)} vũ khí)</h3>"
            + table(['Vũ khí', 'Tên thật', 'Trên', 'Viên/s', 'Viên/phút', 'TB viên/s cả chu kỳ', 'Loạt / băng', 'Xả (s)', 'Nghỉ/nạp (s)', 'Bệ phóng', 'Sát thương/phát', 'DPS khi xả', 'DPS duy trì'], rate_rows, 'dps')
            + f"<h3>Đường đạn</h3>"
            + table(['Vũ khí', 'Cỡ (mm)', 'Họ', 'Dạng', 'Tốc độ đạn (m/s)', 'Bay hết tầm (s)', 'Tầm (m)', 'Tối thiểu', 'Nổ lan (m)', 'Mục tiêu', 'Trần bắn', 'Xuyên', 'Kháng pháo sáng', 'Dấu'], ball_rows, 'dps')
            + f"<h3>Di chuyển, tầm bắn và kích thước ({len(move_rows)} đơn vị)</h3>"
            + table(['Đơn vị', 'Loại', 'Tốc độ (m/s)', 'Xoay thân (°/s)', 'Xoay tháp (°/s)', 'Dài (m)', 'Rộng (m)', 'Bán kính thân', 'Tầm nhìn', 'Đứng cách', 'Nạp đạn ở căn cứ (s)', 'Tàng hình', 'Tối đa mỗi phe', 'Tầm xa nhất (m)', 'Tầm mặt đất', 'Tầm bắn máy bay', 'Tầm tối thiểu', 'Model vẽ: dài × rộng × cao (m)'], move_rows, 'dps')
            + props_and_rounds(game, h, sizes, weapons, owners)
            + "</div>")


def gallery(game, h, imgdir):
    """Section 20: the picture library."""
    from pathlib import Path
    e, img = h['esc'], h['img']
    imgdir = Path(imgdir)
    cards = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Cards'

    def grid(items, cols=4):
        cells = []
        for name, path in items:
            tag = img(path, 'gal')
            if tag:
                cells.append(f"<div class='galcell'>{tag}<div class='galcap'>{e(name)}</div></div>")
        return f"<div class='grid{cols}'>" + ''.join(cells) + "</div>" if cells else ''

    # A card's picture is named after its model (Resources/UI/Cards/manifest.json maps the card id to it).
    try:
        import json as _json
        manifest = {x['id']: x['model'] for x in _json.loads((cards / 'manifest.json').read_text(encoding='utf-8'))['entries']}
    except (OSError, ValueError, KeyError):
        manifest = {}

    def renders(units):
        seen, out = set(), []
        for v in units:
            model = manifest.get(v['id']) or v.get('model') or v['id']
            path = cards / (model + '.png')
            if not path.exists():
                path = cards / (v['id'] + '.png')
            if path.exists() and (v['name'], str(path)) not in seen:
                seen.add((v['name'], str(path)))
                out.append((v['name'], path))
        return out

    branch = {b['id'] for t in game['base']['towers'] for b in t['branches']}
    towers = [t for t in game['towers'] if t['id'] not in branch]
    modules = [dict(m, model=m.get('model') or m['id']) for m in game['base']['modules']]
    out = ["<div class='section'><h2>20. Thư viện hình ảnh</h2>"
           "<p>Ảnh render từ mô hình 3D của game (cùng ảnh dùng cho thẻ), ảnh chụp trong trận, các bảng hiệu ứng và bản đồ nhiệt.</p>"]
    battle = sorted((imgdir / 'ui').glob('battle3d-*.png'))
    if battle:
        out.append("<h3>Trong trận (3D và HUD)</h3>" + ''.join(f"{img(p, 'shot')}<div class='caption'>{e(p.stem.replace('battle3d-', ''))}</div>" for p in battle))
    out.append("<h3>Phương tiện</h3>" + grid(renders(game['vehicles'])))
    out.append("<h3>Xe tinh nhuệ</h3>" + grid(renders(game.get('elites', []))))
    out.append("<h3>Boss</h3>" + grid(renders(game['bosses']), 3))
    out.append("<h3>Tháp canh và công sự</h3>" + grid(renders(towers)))
    out.append("<h3>Công trình tiện ích</h3>" + grid(renders(modules)))
    base = [p for p in [imgdir / 'ui' / 'basemaps-sheet.png', imgdir / 'ui' / 'screen-army-base-ranges-vi-16x9.png',
                        imgdir / 'ui' / 'screen-army-base-picked-vi-16x9.png', imgdir / 'ui' / 'kit-tower-icons.png'] if p.exists()]
    if base:
        out.append("<h3>Căn cứ</h3>" + ''.join(f"{img(p, 'shot')}<div class='caption'>{e(p.stem)}</div>" for p in base))
    fx = imgdir / 'fx'
    sheets = [('impacts_12c.png', 'Nổ đạn tăng, bom, tên lửa hành trình và MOAB (trước / sau 12C, 0,04–3,2 s).'),
              ('impacts_11a.png', 'Nổ trước và sau đợt 11A.'), ('supports.png', 'Hỗ trợ hỏa lực: đạn rơi và lúc chạm đất của từng thẻ.'),
              ('flames.png', 'Xe phun lửa: trước (trên) và sau (dưới).'), ('lasers.png', 'La-de Iron Beam và tia laser của Icarus (trước prompt 19).'),
              ('missiles_1.png', 'Tên lửa phòng không: lửa đuôi và vệt khói.'), ('missiles_2.png', 'Tên lửa chống tăng.'),
              ('missiles_3.png', 'Tên lửa trực thăng và drone.'), ('missiles_4.png', 'Tên lửa máy bay.'), ('missiles_5.png', 'Rốc-két và tên lửa đạn đạo.'),
              ('flashes_1.png', 'Chớp lửa đầu nòng ở 4 hướng (quả cầu xanh: đầu nòng thật).'), ('flashes_2.png', 'Chớp lửa: boss, máy bay, tháp.'),
              ('air_hold.png', 'Tiêm kích dừng xả rồi bay vòng.')]
    fx_tags = ''.join(f"{img(fx / n, 'shot')}<div class='caption'>{e(c)}</div>" for n, c in sheets if (fx / n).exists())
    shields = ROOT / 'Docs' / 'art' / 'shields'
    for n, c in (('shields.png', 'Khiên lưới lục giác: ta xanh, địch đỏ cam, gợn sóng khi trúng, sụp vỡ.'),
                 ('in-game-siege-dome-down.png', 'Vòm khiên pháo đài trong Công thành.'), ('in-game-defend-low-dome-down.png', 'Vòm khiên ở đồ họa Thấp.')):
        tag = img(shields / n, 'shot')
        if tag:
            fx_tags += f"{tag}<div class='caption'>{e(c)}</div>"
    if fx_tags:
        out.append("<h3>Hiệu ứng</h3>" + fx_tags)
    art = ROOT / 'Docs' / 'art'
    art_tags = ''.join(f"{img(art / n, 'shot')}<div class='caption'>{e(c)}</div>" for n, c in
                       (('vehicles-hero.png', 'Mô hình phương tiện.'), ('vehicles2-hero.png', 'Mô hình phương tiện (2).'), ('air-hero.png', 'Mô hình máy bay và trực thăng.'),
                        ('props-game.png', 'Vật thể trên bản đồ.'), ('terrain-game.png', 'Địa hình.'), ('terrain-props-game.png', 'Địa hình và vật thể.')) if (art / n).exists())
    if art_tags:
        out.append("<h3>Mô hình và địa hình</h3>" + art_tags)
    stuck = ROOT / 'Docs' / 'stuck-report'
    pairs = []
    for m in ('ashfield', 'rustyard', 'capital', 'swamp'):
        for when, label in (('before', 'trước'), ('after', 'sau')):
            p = stuck / when / f'heatmap_{m}.png'
            if p.exists():
                pairs.append((f"{m} · {label}", p))
    if pairs:
        out.append("<h3>Bản đồ nhiệt xe kẹt (Công thành, trước và sau prompt 12)</h3>" + grid(pairs, 2))
        top = stuck / 'after' / 'top10.png'
        if top.exists():
            out.append(f"{img(top, 'shot')}<div class='caption'>10 điểm kẹt nhiều nhất còn lại.</div>")
    out.append('</div>')
    return ''.join(out)


def testing(game, h):
    """Section: tests and what the testing phase still has to measure."""
    items = [
        'Quét 5 seed toàn chiến dịch sau khi gộp mọi nhánh (21 nhiệm vụ trên 8 bản đồ mới chưa đo; các chiến dịch lớn giữ trong 15–25 phút).',
        'Tác chiến: mọi tuần của vòng xoay thắng được qua 5 seed ở cấp Thường.',
        'Công thành, Phòng thủ (mục tiêu ≥ 4/5), Vô tận, Pháo đài tuần ở các độ khó và 7 bản đồ còn lại.',
        'Xe tinh nhuệ theo ngân sách: tỷ lệ sức mạnh 1,8–2,2 lần; chiến dịch và Săn trùm sau khi đổi sang ngân sách.',
        'Trang bị: độ chênh giữa các nhóm vũ khí (mục tiêu ≤ 1,5 lần), Nạp kép trên pháo tự động và giàn rocket, đầu đạn chùm lên công trình, cầu tuyết sau trần hoàn CP.',
        'Đã chạy trong đợt cân bằng sau prompt 18 (DECISIONS 19B, số liệu trong Docs/balance, tables_p18.md): quét 5 seed toàn chiến dịch trước/sau, '
        'bộ phát hiện xe kẹt trên 21 bản đồ × 4 chế độ × 5 seed (420 trận), ngân sách tick, mọi chế độ ở 4 độ khó × 5 seed; còn lại ở đây là phần chưa đạt.',
        'Boss: thời gian hạ trong +15% sau khi có bộ phận; mọi trận boss và Săn trùm thắng được (Săn trùm chạm trần 30 phút ở cả 10 trận đo, sau prompt 18).',
        'Hiệu năng: ngân sách tick đo lại trên máy yên tĩnh và điện thoại yếu thật; FPS trận boss nặng nhất ở mức đồ họa Thấp; đảo và đầm lầy (2.500 vật thể).',
        'Sau buổi chơi thử: khả năng thắng chiến dịch và trận boss khi súng chính xe thường không còn bắn máy bay; thời gian hạ tăng của máy bay cường kích và A-10 với nhịp bắn mới; '
        'tỷ lệ trúng của tên lửa chậm hơn khi có pháo sáng và APS; FPS khi nhiều tên lửa hành trình hoặc ném bom rải thảm cùng lúc ở đồ họa Thấp; khung hình những giây đầu trên điện thoại thật.',
        'Giao diện: FPS của HUD mới ở đồ họa Thấp; vùng an toàn trên máy tai thỏ và đục lỗ thật; toàn bộ bài kiểm tra EditMode.',
        'Cân bằng (prompt 13): đủ 5 seed mọi chế độ với người chơi thật, nhất là Công thành, Phòng thủ, Pháo đài tuần và Tử chiến; khoảng cách Thường và Khó; Vô tận/Phòng thủ với căn cứ mạnh yếu khác nhau; thời gian từng boss; mọi mutator Tác chiến; toàn bộ chiến dịch nhiều seed; lượt bay ra vòng chờ dài nhất của oanh tạc cơ (4,5 giây, trên mục tiêu 3 giây).',
        'Xe kẹt (prompt 12): chạy công cụ phát hiện xe kẹt đủ 20 bản đồ mọi chế độ, 5 seed, mọi loadout, bật và tắt lưới an toàn; TickBudgetTests đầy đủ; trận Đầm Lầy và Quần Đảo San Hô.',
    ]
    return ("<div class='section'><h2>17. Kiểm thử và phép đo còn lại</h2>"
            "<p>Bài kiểm tra tự động chạy trong Unity (EditMode): mô phỏng xác định, nên mỗi luật có bài riêng (điểm lưu phát lại khớp tuyệt đối, phản bội không làm lỗi AI, "
            "trần xe, vùng chơi, mutator, bộ phận boss...). Các phép đo dài (5 seed, phòng thí nghiệm trang bị) dồn vào một phase kiểm tra riêng:</p><ul>"
            + ''.join(f"<li>{h['esc'](i)}</li>" for i in items) + "</ul></div>")

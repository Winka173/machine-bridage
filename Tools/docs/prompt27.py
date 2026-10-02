"""The design document's prompt 27 section (the model pipeline and wave 1) and the CHANGELOG's Unreleased headings.

Counts and headings are read from Docs/models/PROGRESS.md and Docs/CHANGELOG.md so the section follows the notes.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(*parts):
    p = ROOT.joinpath(*parts)
    return p.read_text(encoding='utf-8') if p.exists() else ''


def section(game, h):
    e = h['esc']
    progress = _read('Docs', 'models', 'PROGRESS.md')
    waves = {}
    cur = None
    for line in progress.splitlines():
        m = re.match(r'### Wave (\w+)', line)
        if m:
            cur = m.group(1)
            waves[cur] = 0
        elif cur and line.startswith('| `') and '**committed**' in line:
            waves[cur] += 1
    total = sum(waves.values())
    changelog = _read('Docs', 'CHANGELOG.md')
    unreleased = changelog.split('\n## ')[1] if '\n## ' in changelog else ''
    heads = [re.sub(r'\s*\(DECISIONS[^)]*\)', '', l[4:]).strip() for l in unreleased.splitlines() if l.startswith('### ')]
    rows = ''.join(f"<li>{e(t)}</li>" for t in heads)
    wave_txt = ', '.join(f"đợt {k}: {v}" for k, v in waves.items() if v)
    return ("<div class='section'><h2>10h. Prompt 27: quy trình dựng model và đợt 1</h2>"
            "<p>Prompt 27 thay các model mượn tạm (stand-in) bằng model riêng và đặt một mức chất lượng chung cho mọi model. Quy trình: "
            "<b>STEP0_AUDIT</b> kiểm kê mọi model và thẻ; <b>BASELINE</b> chạy bộ kiểm tra GLB (<code>Tools/assets/glb_check.py</code>: tỉ lệ so với "
            "<code>modelSize</code>, tam giác diện tích 0, màu đỉnh COLOR_0, nút bộ phận boss) và ghi mốc; <b>EXPERIMENT_1</b> thử bộ dựng V2 trên bốn model "
            "(xe tăng chủ lực, máy bay tiêm kích, silver_bug, trực thăng tấn công) và được chủ dự án duyệt; <b>BUDGETS</b> đặt trần số tam giác, renderer và "
            "bộ phận động theo loại; <b>art-bible</b> ghi luật tạo hình, bảng màu và công thức V2. Mỗi model một commit: dựng lại, kiểm tĩnh, render thẻ, "
            "xem trước trong Unity, chấp nhận mốc mới kèm lý do. Không chạy test, mô phỏng hay đo hiệu năng cho đến khi chủ dự án cho phép.</p>"
            f"<p><b>Đợt 1</b> ({total} model có tên riêng; {e(wave_txt)}): Ixion và Gungnir, tám boss lô D (Kraken, Monster, Garuda, Hyperion, Stymphalos, "
            "Nyx, Cerberus, Hydra) và 32 đơn vị lô B; mọi lớp màu sơn tạm đã bỏ, không số liệu nào đổi. <b>Đợt 2</b> sửa 18 model validator đánh dấu "
            "(sai tỉ lệ, tam giác diện tích 0, thiếu nút bộ phận boss, vượt trần ngân sách) theo nguyên tắc thay đổi nhỏ nhất.</p>"
            + (f"<h3>Chưa phát hành (CHANGELOG)</h3><ul>{rows}</ul>" if rows else '')
            + "</div>")

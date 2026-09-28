"""The stuck report (prompt 12): heatmaps of where vehicles got stuck on each battlefield, close-ups
of the ten worst spots, and the tables by cause, mode and battlefield, from the CSV files the batch
runs write (Assets/.../Tests/EditMode/StuckBatch.cs, StuckWatch in the sim).

    python Tools/maps/stuck_report.py <label> [<label to compare with>]

Reads Docs/stuck-report/data/<label>/stuck-*.csv and summary-*.csv, writes
Docs/stuck-report/<label>/: heatmap_<map>.png (every mode on that battlefield; the fortress, the
camps, their hardpoints and the gates drawn as plot_map.py draws them, the stuck spots as a heat
layer weighted by the seconds stuck and as dots coloured by cause), top10.png (the ten spots with
the most seconds stuck, each a close-up with its causes and vehicles), and summary.md (the tables;
with a second label, before against after).
"""
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_map  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'maps'
REPORT = ROOT / 'Docs' / 'stuck-report'

CAUSE_COLOURS = {
    'Embedded': '#ff00ff', 'NoPath': '#ff2020', 'GoalUnreachable': '#ff8000', 'StalePath': '#ffe000', 'OffRoute': '#c0ff40',
    'GateWait': '#00e0ff', 'YieldWait': '#4080ff', 'BlockedByFriend': '#2040ff', 'BlockedByDefence': '#a040ff',
    'BlockedByEnemy': '#ffffff', 'BlockedByObstacle': '#806040', 'PathQueued': '#a0a0a0', 'Unknown': '#000000',
}
THRESHOLD = 10.0   # the spec's line: stuck longer than about ten seconds


def load(label):
    folder = REPORT / 'data' / label
    rows = []
    for f in sorted(folder.glob('stuck-*.csv')):
        with f.open(encoding='utf-8') as fh:
            rows.extend(csv.DictReader(fh))
    for r in rows:
        for k in ('seconds', 'x', 'y', 'goal_x', 'goal_y', 'start_s'):
            r[k] = float(r[k])
        r['rescues'] = int(r['rescues'])
    battles = []
    for f in sorted(folder.glob('summary-*.csv')):
        with f.open(encoding='utf-8') as fh:
            battles.extend(csv.DictReader(fh))
    return rows, battles


def map_json(map_id, mode):
    name = f'{map_id}_siege.json'
    text = re.sub(r'^\s*//.*$', '', (DATA / name).read_text(encoding='utf-8'), flags=re.M)
    return json.loads(text)


def heatmap(map_id, rows, out):
    m = map_json(map_id, 'Siege')
    half = m['size'] / 2
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_map.draw_map(ax, m, half)
    plot_map.draw_bases(ax, m, labels=False)
    plot_map.draw_fortress(ax, m, half)
    if rows:
        xs = np.array([r['x'] for r in rows])
        ys = np.array([r['y'] for r in rows])
        ws = np.array([r['seconds'] for r in rows])
        bins = int(m['size'] // 6)
        h, xe, ye = np.histogram2d(xs, ys, bins=bins, range=[[-half, half], [-half, half]], weights=ws)
        h = np.ma.masked_where(h <= 0, h)
        ax.imshow(h.T, origin='lower', extent=[-half, half, -half, half], cmap='inferno', alpha=0.75, zorder=20,
                  interpolation='gaussian')
        for r in rows:
            ax.plot([r['x']], [r['y']], marker='o', markersize=3 + min(8, r['seconds'] / 3), color=CAUSE_COLOURS.get(r['cause'], '#000'),
                    markeredgecolor='black', markeredgewidth=0.5, zorder=21)
    for t in ax.texts:
        t.set_clip_on(True)
    over = sum(1 for r in rows if r['seconds'] >= THRESHOLD)
    ax.set_title(f'{map_id}: {len(rows)} stuck (8 s+), {over} over {THRESHOLD:.0f} s, {sum(r["seconds"] for r in rows):.0f} s in all')
    handles = [plt.Line2D([], [], marker='o', linestyle='', color=c, markeredgecolor='black', label=k)
               for k, c in CAUSE_COLOURS.items() if any(r['cause'] == k for r in rows)]
    if handles:
        ax.legend(handles=handles, loc='lower right', fontsize=7, framealpha=0.85).set_zorder(30)
    fig.savefig(out, dpi=80, bbox_inches='tight')
    plt.close(fig)


def spots(rows, cell=14.0):
    """Stuck records grouped into spots (a 14 m square per battlefield), worst first by seconds stuck."""
    groups = defaultdict(list)
    for r in rows:
        groups[(r['map'], math.floor(r['x'] / cell), math.floor(r['y'] / cell))].append(r)
    ranked = sorted(groups.items(), key=lambda kv: -sum(r['seconds'] for r in kv[1]))
    return ranked


def top10(rows, out):
    ranked = spots(rows)[:10]
    if not ranked:
        return []
    fig, axes = plt.subplots(2, 5, figsize=(30, 13))
    lines = []
    for ax, ((map_id, _, _), group) in zip(axes.flat, ranked):
        m = map_json(map_id, 'Siege')
        half = m['size'] / 2
        plot_map.draw_map(ax, m, half)
        plot_map.draw_bases(ax, m, labels=True)
        plot_map.draw_fortress(ax, m, half)
        cx = sum(r['x'] for r in group) / len(group)
        cy = sum(r['y'] for r in group) / len(group)
        span = 22
        ax.set_xlim(cx - span, cx + span)
        ax.set_ylim(cy - span, cy + span)
        for r in group:
            colour = CAUSE_COLOURS.get(r['cause'], '#000')
            ax.plot([r['x']], [r['y']], marker='o', markersize=6 + min(10, r['seconds'] / 2), color=colour, markeredgecolor='black', zorder=21)
            ax.annotate('', xy=(max(cx - span, min(cx + span, r['goal_x'])), max(cy - span, min(cy + span, r['goal_y']))),
                        xytext=(r['x'], r['y']), arrowprops=dict(arrowstyle='->', color=colour, lw=1.2), zorder=22)
        causes = Counter(r['cause'] for r in group)
        defs = Counter(r['def'] for r in group)
        seconds = sum(r['seconds'] for r in group)
        title = (f'{map_id} ({cx:.0f}, {cy:.0f}): {len(group)} stuck, {seconds:.0f} s\n'
                 + ', '.join(f'{k} {n}' for k, n in causes.most_common(3)) + '\n'
                 + ', '.join(f'{k} {n}' for k, n in defs.most_common(3)))
        ax.set_title(title, fontsize=9)
        for t in ax.texts:
            t.set_clip_on(True)
        lines.append((map_id, cx, cy, len(group), seconds, causes, defs, group))
    for ax in list(axes.flat)[len(ranked):]:
        ax.axis('off')
    fig.subplots_adjust(hspace=0.35, wspace=0.2)
    fig.savefig(out, dpi=70, bbox_inches='tight')
    plt.close(fig)
    return lines


def table(counter, total_label='total'):
    keys = sorted(counter, key=lambda k: -counter[k])
    return keys


def summary(label, rows, battles, other=None):
    out = []
    out.append(f'# Stuck report: {label}\n')
    over = [r for r in rows if r['seconds'] >= THRESHOLD]
    rescues = sum(int(b['rescues']) for b in battles)
    out.append(f'- Battles: {len(battles)}; stuck episodes of 8 s or more: {len(rows)}; over {THRESHOLD:.0f} s: {len(over)}; '
               f'safety-net activations: {rescues}.')
    if battles:
        sim = sum(float(b['minutes']) for b in battles)
        out.append(f'- Simulated: {sim:.0f} min of battle ({sum(float(b["wall_s"]) for b in battles):.0f} s to run).')
    if other is not None:
        orows, obattles = other
        oover = [r for r in orows if r['seconds'] >= THRESHOLD]
        out.append(f'- Against `{other_label}`: {len(orows)} episodes of 8 s+ ({len(oover)} over {THRESHOLD:.0f} s), '
                   f'{sum(int(b["rescues"]) for b in obattles)} activations.')
    out.append('')
    out.append(f'## By cause (8 s+ / over {THRESHOLD:.0f} s)\n')
    out.append('| cause | 8 s+ | over 10 s | seconds | ' + ('before 8 s+ | before over 10 s |' if other else '') )
    out.append('|---|---|---|---|' + ('---|---|' if other else ''))
    c8 = Counter(r['cause'] for r in rows)
    c10 = Counter(r['cause'] for r in over)
    secs = Counter()
    for r in rows:
        secs[r['cause']] += r['seconds']
    oc8 = Counter(r['cause'] for r in other[0]) if other else Counter()
    oc10 = Counter(r['cause'] for r in other[0] if r['seconds'] >= THRESHOLD) if other else Counter()
    for k in sorted(set(c8) | set(oc8), key=lambda k: -(c8[k] + oc8[k])):
        out.append(f'| {k} | {c8[k]} | {c10[k]} | {secs[k]:.0f} |' + (f' {oc8[k]} | {oc10[k]} |' if other else ''))
    out.append('')
    for key, name in (('mode', 'mode'), ('area', 'place'), ('def', 'vehicle'), ('map', 'battlefield'), ('config', 'loadout')):
        out.append(f'## By {name} (8 s+ / over 10 s)\n')
        out.append(f'| {name} | 8 s+ | over 10 s |' + (' before 8 s+ | before over 10 s |' if other else ''))
        out.append('|---|---|---|' + ('---|---|' if other else ''))
        a = Counter(r[key] for r in rows)
        b = Counter(r[key] for r in over)
        oa = Counter(r[key] for r in other[0]) if other else Counter()
        ob = Counter(r[key] for r in other[0] if r['seconds'] >= THRESHOLD) if other else Counter()
        for k in sorted(set(a) | set(oa), key=lambda k: -(a[k] + oa[k]))[:25]:
            out.append(f'| {k} | {a[k]} | {b[k]} |' + (f' {oa[k]} | {ob[k]} |' if other else ''))
        out.append('')
    out.append('## Battles\n')
    out.append('| mode | map | seed | loadout | minutes | result | 8 s+ | over 10 s | worst s | rescues |')
    out.append('|---|---|---|---|---|---|---|---|---|---|')
    for b in battles:
        out.append(f"| {b['mode']} | {b['map']} | {b['seed']} | {b['config']} | {b['minutes']} | {b['result']} | {b['stuck8']} | "
                   f"{b['stuck10']} | {b['worst_s']} | {b['rescues']} |")
    out.append('')
    return '\n'.join(out)


if __name__ == '__main__':
    label = sys.argv[1]
    other_label = sys.argv[2] if len(sys.argv) > 2 else None
    rows, battles = load(label)
    other = load(other_label) if other_label else None
    folder = REPORT / label
    folder.mkdir(parents=True, exist_ok=True)
    by_map = defaultdict(list)
    for r in rows:
        by_map[r['map']].append(r)
    maps = sorted({b['map'] for b in battles} | set(by_map))
    for map_id in maps:
        heatmap(map_id, by_map.get(map_id, []), folder / f'heatmap_{map_id}.png')
    lines = top10(rows, folder / 'top10.png')
    text = summary(label, rows, battles, other)
    text += '\n## The ten worst spots (top10.png)\n\n'
    for i, (map_id, cx, cy, n, seconds, causes, defs, group) in enumerate(lines, 1):
        worst = max(group, key=lambda r: r['seconds'])
        text += (f"{i}. **{map_id} ({cx:.0f}, {cy:.0f})**: {n} stuck, {seconds:.0f} s; "
                 + ', '.join(f'{k} {c}' for k, c in causes.most_common()) + f"; worst: {worst['def']} #{worst['vehicle']} "
                 f"({worst['mode']} seed {worst['seed']} {worst['config']}, from {worst['start_s']:.0f} s for {worst['seconds']:.0f} s, "
                 f"{worst['cause']}: {worst['detail']}; near {worst['nearby'][:160]})\n")
    (folder / 'summary.md').write_text(text, encoding='utf-8')
    print(text[:3000])

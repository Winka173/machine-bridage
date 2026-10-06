"""MVA W2-B (spec parts AM, BR, CE #10): static colour / contrast QA of the danger telegraphs against every map theme's ground.

    python Tools/vfx/contrast_audit.py        # writes Docs/mapvisaudio/CONTRAST_AUDIT.md; exit 0 (a review list, never a gate)

Reads the colours where the game keeps them (no copies to drift): each telegraph's `static readonly Color X = new(r, g, b, a)`
in Game/Effects (escape rings, stick rectangles, big-attack zones, top-attack marks, hazard rings) and each theme's ground
palette (`new TerrainTheme("#..", ...)` in Game/Views/MapTheme.cs). For every cue edge over every ground swatch it composites
the edge (HDR clamped to 1, as the bloom-free Low tier shows it) over the ground at its alpha, then measures how far apart the
two are as seen: the CIELAB colour difference (Delta E 1976, which counts hue as well as lightness: a red ring on sand differs
in hue where its luminance contrast is nil) and, for reference, the WCAG luminance ratio, under four conditions: day, night (ground x 0.35), fog (ground half-way to the fog grey) and snow glare (ground x 1.1),
and again through protanopia, deuteranopia and tritanopia (Machado et al. 2009, severity 1). The rings also differ by shape,
motion and sound (spec part AM: never colour alone), so the report is a review list: Delta E under 20 is REVIEW.
Simulation does not replace testing with people (spec part BR).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EFFECTS = ROOT / 'Assets/MachineBrigade/Scripts/Game/Effects'
THEMES = ROOT / 'Assets/MachineBrigade/Scripts/Game/Views/MapTheme.cs'
OUT = ROOT / 'Docs/mapvisaudio/CONTRAST_AUDIT.md'
CUES = {
    'EscapeWarnings.cs': ('EdgeColour', 'CoreColour'),
    'StickWarnings.cs': ('EdgeColour', 'NextColour'),
    'BigAttackZones.cs': ('Edge',),
    'TopAttackMarks.cs': ('Edge',),
    'HazardCues.cs': ('MineEdge', 'EmpEdge'),
}
CVD = {
    'protan': ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    'deutan': ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    'tritan': ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
REVIEW = 20.0


def lab(rgb):
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))) ** 0.5
COLOR = re.compile(r'static readonly Color (\w+) = new\(([^)]*)\)')
THEME = re.compile(r'new TerrainTheme\(([^)]*)\);\s*return new MapTheme\s*\{\s*Id = "(\w+)"', re.S)


def floats(text):
    return [float(x.strip().rstrip('f')) for x in text.split(',') if x.strip()]


def hex_rgb(h):
    h = h.strip().strip('"').lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb(c):
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(rgb):
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def simulate(rgb, kind):
    if kind is None:
        return rgb
    v = [lin(c) for c in rgb]
    m = CVD[kind]
    return tuple(srgb(sum(m[i][j] * v[j] for j in range(3))) for i in range(3))


def over(edge, ground):
    r, g, b, a = edge
    a = min(1.0, max(0.0, a))
    top = (min(1.0, r), min(1.0, g), min(1.0, b))
    return tuple(top[i] * a + ground[i] * (1 - a) for i in range(3))


CONDITIONS = {
    'day': lambda g: g,
    'night': lambda g: tuple(c * 0.35 for c in g),
    'fog': lambda g: tuple(c * 0.5 + 0.62 * 0.5 for c in g),
    'glare': lambda g: tuple(min(1.0, c * 1.1) for c in g),
}


def main():
    cues = {}
    for name, wanted in CUES.items():
        text = (EFFECTS / name).read_text(encoding='utf-8')
        for colour, values in COLOR.findall(text):
            if colour in wanted:
                v = floats(values)
                cues[f'{name[:-3]}.{colour}'] = (v + [1.0])[:4]
    themes = {tid: [hex_rgb(h) for h in args.split(',')] for args, tid in THEME.findall(THEMES.read_text(encoding='utf-8'))}
    # The temperate theme takes TerrainPainter's Riverlands palette.
    river = re.search(r'Riverlands => new\(([^)]*)\)', (THEMES.parent / 'TerrainPainter.cs').read_text(encoding='utf-8'))
    if river:
        themes['temperate'] = [hex_rgb(h) for h in river.group(1).split(',')]
    rows, worst = [], {}
    for cue, edge in sorted(cues.items()):
        for theme, swatches in sorted(themes.items()):
            low = None
            for cond, shade in CONDITIONS.items():
                for kind in (None, 'protan', 'deutan', 'tritan'):
                    for ground in swatches:
                        g = shade(ground)
                        seen_edge, seen_ground = simulate(over(edge, g), kind), simulate(g, kind)
                        d = delta_e(seen_edge, seen_ground)
                        if low is None or d < low[0]:
                            low = (d, cond, kind or 'normal', ratio(seen_edge, seen_ground))
            rows.append((cue, theme, low))
            if cue not in worst or low[0] < worst[cue][0]:
                worst[cue] = (low[0], theme, low[1], low[2], low[3])
    review = [r for r in rows if r[2][0] < REVIEW]
    lines = ['# Danger telegraph contrast audit (MVA W2-B)', '',
             'Generated by `python Tools/vfx/contrast_audit.py` (spec parts AM, BR, CE #10). Do not edit by hand. The rings also',
             'differ by shape, motion and sound, so this is a review list, never a gate; simulation does not replace testing with',
             'people. Worst case per cue over every theme ground swatch, day / night / fog / snow glare, normal and protan /',
             f'deutan / tritan vision: CIELAB Delta E (hue and lightness; REVIEW under {REVIEW:g}) and the WCAG luminance ratio there.', '',
             f'- Cues: {len(cues)}; themes: {len(themes)}; pairs under Delta E {REVIEW:g}: {len(review)}.', '',
             '| cue | worst Delta E | luminance ratio | theme | condition | vision |', '| --- | --- | --- | --- | --- | --- |']
    for cue, (d, theme, cond, kind, lum) in sorted(worst.items()):
        lines.append(f'| {cue} | {d:.1f}{" REVIEW" if d < REVIEW else ""} | {lum:.2f} | {theme} | {cond} | {kind} |')
    if review:
        lines += ['', '## Pairs to review', '', '| cue | theme | Delta E | luminance ratio | condition | vision |',
                  '| --- | --- | --- | --- | --- | --- |']
        for cue, theme, (d, cond, kind, lum) in review:
            lines.append(f'| {cue} | {theme} | {d:.1f} | {lum:.2f} | {cond} | {kind} |')
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'CONTRAST: {len(cues)} cues x {len(themes)} themes, {len(review)} pairs to review -> {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

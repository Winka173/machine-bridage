"""Resolves the usual art-merge conflicts: builder registrations in build_assets.py (import lines and
**mb_x.BUILDERS, both sides kept) and Docs/art/models.json (union of entries, sorted). Run from the repo root."""
import json
import re
import subprocess

p = 'Tools/blender/build_assets.py'
s = open(p, encoding='utf-8').read()
HUNK = re.compile(r'<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n', re.S)


def resolve(m):
    ours, theirs = m.group(1), m.group(2)
    if 'import ' in ours or 'import ' in theirs:
        # Import lines: keep both sides, sorted.
        lines = sorted(set(line for line in (ours + theirs).splitlines() if line.strip()))
        return '\n'.join(lines) + '\n'
    tokens = []
    for part in (ours, theirs):
        for t in re.findall(r'\*\*mb_\w+\.BUILDERS', part):
            if t not in tokens:
                tokens.append(t)
    return '            ' + ', '.join(tokens) + '}\n'


if '<<<<<<<' in s:
    s = HUNK.sub(resolve, s)
    open(p, 'w', encoding='utf-8').write(s)
    print('build_assets resolved')

try:
    ours = json.loads(subprocess.check_output(['git', 'show', ':2:Docs/art/models.json']).decode('utf-8'))
    theirs = json.loads(subprocess.check_output(['git', 'show', ':3:Docs/art/models.json']).decode('utf-8'))
    merged = dict(ours)
    for k, v in theirs.items():
        merged.setdefault(k, v)
    open('Docs/art/models.json', 'w', encoding='utf-8').write(json.dumps(dict(sorted(merged.items())), indent=2) + '\n')
    print('models.json:', len(merged), 'entries')
except subprocess.CalledProcessError:
    print('models.json: no conflict')

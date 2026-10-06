"""MVA W1-B (spec part W / X / BX): the runtime node contract, shared by the audit, the export hook and the tools.

Gameplay looks a model's nodes up by name (Scripts/Game/Rendering/RuntimeNodes.cs is the C# twin of this file):

  indexed   Muzzle_<slot>, Mount_<slot>, Part_<name>: the k-th mount of a slot in the data is the k-th node of the slot in
            canonical order (VehicleView), a boss part names its node in the data (balance.json parts[].node).
  set       Turret, Engine_flame, Rotor*, Propeller*, Radar*, Deploy_*: every node of the name is used alike, order free.

Stable names (W1): a runtime node may carry a semantic tag, never a Blender duplicate suffix (".001"):

  <Kind>_<slot>[_<tag>[_<tag>]]     tag = L | C | R (side) | fore | mid | aft (along the hull) | 01..99 (an index)

e.g. Muzzle_missile_L / Muzzle_missile_R, Mount_gun_fore / Mount_gun_aft, Mount_mg_01 .. Mount_mg_04. Tags are
case-sensitive (Part_aa_l / Muzzle_door_l are older lower-case names, not tags). A tagged Mount_Flare_* is never a weapon
mount (AGENT_RULES: flare points).

Canonical order inside a slot: the plain name first, then by tag (fore < mid < aft, L < C < R, 01 < 02 ...), then a legacy
".NNN" suffix by number. For legacy names alone this is exactly the old ordinal order (Muzzle_mg, Muzzle_mg.001, ...), so
old GLBs resolve as before until they are renamed.

Renaming (order-preserving, `propose`): the plain name stays (the slot's first node); each ".NNN" gets a tag that keeps the
canonical order (a pair's second by where it is: Muzzle_rocket + Muzzle_rocket_R; three or more by index: Mount_mg,
Mount_mg_02, Mount_mg_03).
`rename_file(path, mapping)` rewrites the GLB's JSON chunk only (the binary chunk is untouched).
"""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / 'Assets/MachineBrigade/Resources/Models'
MAP_FILE = Path(__file__).with_name('runtime_node_map.json')

MUZZLE_SLOTS = ('main', 'coax', 'mg', 'missile', 'rocket', 'gun', 'aam', 'door_l', 'door_r', 'ramp', 'agl_l', 'agl_r', 'mortar')
TAG = r'(?-i:(?:_(?:L|R|C|fore|mid|aft|\d{2})){1,2})'
SUFFIX = r'(\.\d+)?'
PATTERNS = {
    'muzzle': re.compile(r'^Muzzle_(' + '|'.join(MUZZLE_SLOTS) + r')(' + TAG + r')?' + SUFFIX + r'$', re.I),
    # Mount_Flare_L / _R are flare points, not weapon pivots; a bare legacy Mount_Flare still parses as before.
    'mount': re.compile(r'^Mount_(?!flare_)([a-z]+)(' + TAG + r')?' + SUFFIX + r'$', re.I),
    'part': re.compile(r'^Part_([a-z]+)(' + TAG + r')?' + SUFFIX + r'$', re.I),
}
SET_PATTERNS = {
    'turret': re.compile(r'^Turret(\.\d+)?$'),
    'engine_flame': re.compile(r'^Engine_flame(' + TAG + r')?(\.\d+)?$'),
    'rotor': re.compile(r'^Rotor(_rear|_front|_\d+)?(\.\d+)?$'),
    'propeller': re.compile(r'^Propeller(_\d+)?(\.\d+)?$'),
    'radar': re.compile(r'^Radar(_search|_\d+)?(\.\d+)?$'),
    'deploy': re.compile(r'^Deploy_[a-z]+(_[lr])?(\.\d+)?$', re.I),
}
POSITION = {'fore': 0, 'mid': 1, 'aft': 2}
SIDE = {'L': 0, 'C': 1, 'R': 2}
LEGACY = re.compile(r'\.\d+$')


def parse(name: str):
    """(kind, slot, tags tuple, legacy suffix number or None) of an indexed runtime node, else None."""
    for kind, pattern in PATTERNS.items():
        m = pattern.match(name)
        if m:
            tags = tuple(t for t in (m.group(2) or '').split('_') if t)
            suffix = int(m.group(3)[1:]) if m.group(3) else None
            return kind, m.group(1).lower(), tags, suffix
    return None


def tag_key(tags) -> tuple:
    out = []
    for t in tags:
        if t in POSITION:
            out.append((0, POSITION[t]))
        elif t in SIDE:
            out.append((1, SIDE[t]))
        else:
            out.append((2, int(t)))
    return tuple(out)


def order_key(name: str) -> tuple:
    """Canonical order inside a slot (see the module doc); the C# twin is RuntimeNodes.Compare."""
    p = parse(name)
    if p is None:
        return ((9, 0),), 1 << 30, name
    _, _, tags, suffix = p
    return tag_key(tags), -1 if suffix is None else suffix, name


def groups(names):
    """{(kind, slot): [names in canonical order]} of the indexed runtime nodes among `names`."""
    out: dict = {}
    for n in names:
        p = parse(n)
        if p:
            out.setdefault((p[0], p[1]), []).append(n)
    for k in out:
        out[k].sort(key=order_key)
    return out


# ------------------------------------------------------------------------------------------------------------- GLB I/O

def read_doc(path: Path):
    """(json doc, binary chunk bytes or None) of a GLB."""
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67:
        raise ValueError(f'{path}: not a GLB')
    jlen, jtype = struct.unpack_from('<II', data, 12)
    doc = json.loads(data[20:20 + jlen])
    rest = data[20 + jlen:]
    return doc, rest


def write_doc(path: Path, doc, rest: bytes):
    raw = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    raw += b' ' * ((4 - len(raw) % 4) % 4)
    total = 12 + 8 + len(raw) + len(rest)
    Path(path).write_bytes(struct.pack('<III', 0x46546C67, 2, total) + struct.pack('<II', len(raw), 0x4E4F534A) + raw + rest)


def _local(node):
    import numpy as np
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=float).reshape(4, 4).T
    t = node.get('translation', [0, 0, 0])
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    s = node.get('scale', [1, 1, 1])
    r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    m = np.eye(4)
    m[:3, :3] = r * np.array(s, dtype=float)
    m[:3, 3] = t
    return m


def world_matrices(doc):
    """{node index: 4x4 world matrix} and {child: parent} in glTF space (+Y up, +Z forward, +X the model's left: glTFast negates X)."""
    nodes = doc.get('nodes', [])
    parent = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
    cache = {}

    def world(i):
        if i not in cache:
            m = _local(nodes[i])
            cache[i] = world(parent[i]) @ m if i in parent else m
        return cache[i]

    for i in range(len(nodes)):
        world(i)
    return cache, parent


# ------------------------------------------------------------------------------------------------------------- rename

def propose(doc) -> dict:
    """{old name: new name} for every indexed group that carries a legacy suffix, keeping its canonical order.

    The plain name (Muzzle_rocket) stays: it is the slot's first node, and every exact lookup of it keeps working. The
    suffixed ones get a tag: with a plain first any tag keeps the order, so a pair's second is named by where it is (_R /
    _L by side, _aft / _fore along the hull), three or more by index (_02, _03 ...: the plain one is the first). A group
    with no plain name: a mirrored pair whose first is on the left is _L / _R, whose first is ahead _fore / _aft, else
    _01 .. _NN."""
    nodes = doc.get('nodes', [])
    names = [n.get('name', '') for n in nodes]
    index = {}
    for i, n in enumerate(names):
        index.setdefault(n, i)
    mats, _ = world_matrices(doc)
    mapping = {}
    for (kind, slot), members in groups(names).items():
        parsed = [parse(n) for n in members]
        if not any(p[3] is not None for p in parsed):
            continue
        if any(p[2] for p in parsed) or len(set(members)) != len(members):
            continue  # tagged and suffixed at once, or duplicate names: the audit reports it, no automatic name
        base = LEGACY.sub('', members[0])
        pos = [mats[index[n]][:3, 3] for n in members]
        plain = parsed[0][3] is None
        tags = None
        if len(members) == 2:
            (x0, _, z0), (x1, _, z1) = pos[0], pos[1]
            side = 'L' if x1 > x0 else 'R'  # glTF +X is the model's left (glTFast flips X into Unity's)
            if abs(x0 - x1) > 0.1 and (plain or (x0 > 0.05 and x1 < -0.05)):
                tags = [None, side] if plain else ['L', 'R']
            elif abs(z0 - z1) > 0.3 and (plain or z0 > z1):
                tags = [None, 'aft' if z1 < z0 else 'fore'] if plain else ['fore', 'aft']
        if tags is None:
            tags = [None if (plain and k == 0) else f'{k + 1:02d}' for k in range(len(members))]
        for old, tag in zip(members, tags):
            if tag is not None:
                mapping[old] = f'{base}_{tag}'
    # A muzzle on a renamed mount takes its mount's tag (Mount_mg_R carries Muzzle_mg_R) when that keeps the order.
    _, parent = world_matrices(doc)
    for (kind, slot), members in groups(names).items():
        if kind != 'muzzle' or not any(m in mapping for m in members):
            continue
        tags = []
        for n in members:
            i, tag = index[n], False
            while i in parent:
                i = parent[i]
                p = parse(mapping.get(names[i], names[i]))
                if p and p[0] == 'mount' and p[1] == slot:
                    tag = '_'.join(p[2]) or None
                    break
            tags.append(tag)
        if False in tags or tags[0] is not None and parse(members[0])[3] is None:
            continue
        keys = [tag_key(t.split('_')) if t else () for t in tags]
        if any(t is None for t in tags[1:]) or any(a >= b for a, b in zip(keys, keys[1:])):
            continue
        base = re.sub(TAG + r'$', '', LEGACY.sub('', members[0]))
        for old, tag in zip(members, tags):
            if tag is not None:
                mapping[old] = f'{base}_{tag}'
            else:
                mapping.pop(old, None)
    return mapping


def load_map() -> dict:
    if not MAP_FILE.exists():
        return {}
    return json.loads(MAP_FILE.read_text(encoding='utf-8')).get('models', {})


def save_map(models: dict):
    body = {'about': 'MVA W1-B: legacy Blender-suffixed runtime node names renamed to stable semantic names, per model '
                     '(old -> new, order-preserving). Tools/assets/runtime_nodes.py; frontier_kit.export_collection re-applies '
                     'it after every export, so a rebuilt model keeps its stable names.',
            'models': dict(sorted(models.items()))}
    MAP_FILE.write_text(json.dumps(body, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def rename_file(path: Path, mapping: dict) -> list[str]:
    """Renames the nodes of a GLB by `mapping`; returns the old names it renamed (missing ones are skipped)."""
    doc, rest = read_doc(path)
    done = []
    for node in doc.get('nodes', []):
        new = mapping.get(node.get('name'))
        if new:
            done.append(node['name'])
            node['name'] = new
    if done:
        write_doc(path, doc, rest)
    return done


def apply_export_map(path) -> list[str]:
    """frontier_kit.export_collection's hook: a model listed in runtime_node_map.json gets its stable names again."""
    path = Path(path)
    stem = path.stem
    mapping = load_map().get(stem)
    return rename_file(path, mapping) if mapping else []

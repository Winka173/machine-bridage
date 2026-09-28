"""Machine Brigade phase 8 models: a combat bulldozer, the boss roster's new showpieces and the generic broken
pieces that replace a boss part once it is destroyed. Built with frontier_kit and the helpers of mb_vehicles,
mb_bosses, mb_siege and mb_air.

  * armored_bulldozer: armoured combat bulldozer (IDF D9R lineage), 7.9 x 4.3 m, 4 m: high-drive tracks (the
    sprocket raised over the rear idler, so each belt is a triangle), a narrow armoured engine hood, a
    tall armoured cab with thick bullet-proof windows behind slat armour, a single-shank ripper at the rear
    and a big semi-U blade on push arms and lift rams. The blade and its push arms hang from the `Blade`
    empty at the push arms' trunnions (0, -0.7, 0.58): pitching it about local X raises the blade. A remote
    heavy machine gun on the cab roof turns on `Mount_mg` (`Muzzle_mg` at its flash hider).
  * rail_supergun: super-heavy railway gun (Schwerer Gustav / K5 lineage) on its own double-track bed (see
    the rail_supergun docstring for the rig and the boss parts).
  * rail_tractor, targeting_station: the gun's two armoured shunting locomotives and its fire-control post,
    separate models.
  * earth_borer, command_airship, landing_hovercraft, supreme_command: bosses; see each builder's docstring.
  * wreck_barrel, wreck_turret, wreck_launcher, wreck_stump, wreck_engine: charred broken pieces the game
    swaps in for a destroyed boss part.

Boss parts: every part of a boss that can be destroyed on its own (engines, hangars, radar, fans, ramp, drill,
antennas, guns) is an empty `Part_<kind>` (`Part_engine`, `Part_engine.001` ...) holding all of that part's
meshes and pivots, so the game can hide it or swap a wreck piece in at its origin. A weapon's part is named
after its data slot (`Part_mg` holds `Mount_mg`, `Part_gun.001` holds `Mount_gun.001`, `Part_main` the gun
`Turret`). Each Part_ empty sits where a wreck piece belongs: a gun's on its mount ring, an engine's at the
nacelle's middle, a radar's and an antenna farm's at their foot. The game still has to treat `Part_*` as
separate rigid groups (ModelLibrary.MergeRigidParts merges every mesh that is not under a moving pivot).

Rig (ModelLibrary.cs, VehicleView.cs): `Turret` yaws; its children named main_cannon*, muzzle_brake* ...
elevate on a pivot the game puts at the back of their bounds, Main_cannon* / Muzzle_brake* also recoil.
`Mount_<slot>` pivots turn on their own, `Radar` spins about Z and `Propeller`, `Propeller_2` ... about
Y (the model's front-back axis): the earth borer's drill head spins on a `Propeller`. A slot's k-th mount in
the data takes the k-th `Muzzle_<slot>` in name order. Every muzzle empty sits at the bore end of its
barrel, on the bore axis, under the pivot that moves that barrel; at rest every bore points along -Y.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front and +X the vehicle's left,
origin on the ground at the footprint centre (the airship: at its hull centre; the wreck pieces: at the
point where they attach). Touching parts overlap or stand at least 1 cm apart, never face to face.
Suffixed pivots are authored as `Mount_gun__001` (frontier_kit refuses runtime names with a dot) and
renamed when the asset finishes (mb_phase2._suffixed), under build_assets.py and under this module's main.

Headless: blender --background --python Tools/blender/build_assets.py -- armored_bulldozer
     or:  blender --background --python Tools/blender/mb_phase8.py -- [--out DIR] [names...]
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from frontier_kit import chamfered  # noqa: E402
from mb_air import _prop_blade, _revolve  # noqa: E402
from mb_bosses import _headlamp, _hull2d, _plate_bolts, _railing, _sec6, track_shoes, track_unit  # noqa: E402
from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_siege import bag_arc, bag_run, flag, flood_head, generator, lattice, loop_rail  # noqa: E402
from mb_support import _beacon, _lpda, _ram, _telescopic_mast, _whip  # noqa: E402
from mb_themes import ladder  # noqa: E402
from mb_town import fbox  # noqa: E402
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _cable, _dish, _frame, _glacis, _hatch, _headlight,  # noqa: E402
                         _jerrycans, _periscopes, _perimeter, _slats, _stowage_bin, _taillight, _wheel)
from mb_vehicles2 import _axis  # noqa: E402

TAU = math.tau
BACKWARD = (-R90, 0, 0)   # cylinder axis along Y, local +Z -> +Y


# ----------------------------------------------------------------------------- shared helpers
def _v(p, dx=0.0, dy=0.0, dz=0.0):
    return (p[0] + dx, p[1] + dy, p[2] + dz)


def _rel(p, o):
    """World point p relative to the pivot origin o."""
    return (p[0] - o[0], p[1] - o[1], p[2] - o[2])


def pv(a, name, loc, parent=None):
    """a.pivot for a name that may carry a Blender suffix (Part_engine.001); returns the kit key."""
    return a.pivot(dotted(name), loc, dotted(parent) if parent else None)


def _slot_names(mount):
    """'Mount_gun.001' -> ('Mount_gun__001', 'Muzzle_gun__001', 'gun_001'): pivot keys and a mesh prefix."""
    return dotted(mount), dotted(mount.replace('Mount_', 'Muzzle_')), mount[6:].replace('.', '_')


def _muzzle_ring(part, bore, at, r, depth=.12, seg=12):
    """Muzzle ring round a dark recessed bore at the front of a barrel along -Y whose tip is at `at`."""
    base = _v(at, dy=depth)
    part.lathe([(r, -.03), (r, depth), (r * .62, depth), (r * .62, .02)], loc=base, rot=FORWARD, seg=seg)
    bore.cyl(r * .6, .02, loc=_v(base, dy=-.05), rot=FORWARD, seg=seg, bevel=0)


def rws(a, mount, loc, parent=None, length=1.05, ammo=1, body='Armor'):
    """Remote weapon station (Samson / Protector lineage) on its own yaw pivot `mount` (Mount_mg or
    Mount_mg.001) at loc, relative to `parent`: a socket ring on the parent, a turntable, an armoured cradle
    with the heavy machine gun (receiver, perforated jacket, 7.6 cm barrel, dark flash hider), the sensor head
    with two glass eyes on the left, an ammunition box on side `ammo` and a smoke bank. The muzzle
    (Muzzle_mg ...) sits at the hider's face. Returns the pivot key."""
    key, mkey, tag = _slot_names(mount)
    pk = dotted(parent) if parent else None
    a.part(f'RWS_socket_{tag}', 'Steel', pk).cyl(.3, .08, loc=_v(loc, dz=.03), seg=14, bevel=.01, bseg=1)
    m = a.pivot(key, loc, pk)
    steel = a.part(f'RWS_steel_{tag}', 'Steel', m)
    arm = a.part(f'RWS_body_{tag}', body, m)
    dark = a.part(f'RWS_dark_{tag}', 'Undercarriage', m)
    steel.cyl(.27, .08, loc=(0, 0, .08), seg=14, bevel=.01, bseg=1)                        # turntable
    arm.box((.46, .5, .16), loc=(0, .05, .2), bevel=.03, seg=1)                             # base
    for s in (-1, 1):
        arm.box((.06, .42, .34), loc=(s * .2, .02, .42), bevel=.015, seg=1)                 # cradle arms
    zb = .46
    steel.box((.2, .62, .2), loc=(0, .02, zb), bevel=.02, seg=1)                            # receiver
    steel.cyl(.058, .34, loc=(0, -.44, zb), rot=FORWARD, seg=10, bevel=0)                   # jacket
    dark.cyl(.064, .04, loc=(0, -.36, zb), rot=FORWARD, seg=10, bevel=0)
    dark.cyl(.064, .04, loc=(0, -.52, zb), rot=FORWARD, seg=10, bevel=0)
    tip = -.29 - length
    steel.cyl(.038, length - .3, loc=(0, (-.6 + tip + .12) / 2, zb), rot=FORWARD, seg=8, bevel=0)
    dark.cyl(.052, .14, loc=(0, tip + .07, zb), rot=FORWARD, seg=8, bevel=0)               # flash hider
    head = a.part(f'RWS_sensor_{tag}', body, m)
    head.box((.24, .34, .3), loc=(.36, -.02, .52), bevel=.03, seg=1)                        # sensor head
    glass = a.part(f'RWS_glass_{tag}', 'Glass', m)
    glass.box((.08, .02, .08), loc=(.31, -.195, .58), bevel=0)
    glass.box((.08, .02, .08), loc=(.41, -.195, .48), bevel=0)
    a.part(f'RWS_ammo_{tag}', 'Crate', m).box((.2, .36, .26), loc=(-ammo * .34, .08, .44), bevel=.02, seg=1)
    for k in range(3):
        steel.cyl(.035, .12, loc=(-ammo * .3 + k * .07 * -ammo, .3, .32), rot=(-.5, 0, 0), seg=6, bevel=0)
    a.pivot(mkey, (0, tip, zb), m)
    return m


def autocannon(a, mount, loc, parent=None, length=3.0, r=.075, body='Team', size=(1.3, 1.5, .62)):
    """Compact faceted gun turret (Bofors 57 / 40 mm naval lineage) on its own yaw pivot `mount` at loc
    (relative to `parent`): a ring on the parent, a squat stealthy house `size` (width, depth, height) with
    sloped faces, a cylindrical mantlet, one long autocannon barrel with cooling rings and a slotted muzzle
    brake round a dark bore, a sight and a vent. The muzzle sits at the brake's face. Returns the pivot key."""
    key, mkey, tag = _slot_names(mount)
    pk = dotted(parent) if parent else None
    w, d, h = size
    a.part(f'Gun_ring_{tag}', 'Armor', pk).cyl(w * .5, .1, loc=_v(loc, dz=.03), seg=18, bevel=.02, bseg=1)
    m = a.pivot(key, loc, pk)
    house = a.part(f'Gun_house_{tag}', body, m)
    arm = a.part(f'Gun_armor_{tag}', 'Armor', m)
    steel = a.part(f'Gun_steel_{tag}', 'Steel', m)
    dark = a.part(f'Gun_dark_{tag}', 'Undercarriage', m)
    bottom = [(-w / 2 + .12, -d / 2), (w / 2 - .12, -d / 2), (w / 2, -d / 2 + .3), (w / 2, d / 2 - .1),
              (w / 2 - .1, d / 2), (-w / 2 + .1, d / 2), (-w / 2, d / 2 - .1), (-w / 2, -d / 2 + .3)]
    top = [(x * .78, y * .8 + .06) for x, y in bottom]
    house.loft([[(x, y, .06) for x, y in bottom], [(x, y, h) for x, y in top]], bevel=.04, seg=1)
    zb = h * .52
    arm.cyl(.2, .34, loc=(0, -d / 2 + .06, zb), rot=FORWARD, seg=14, bevel=.02, bseg=1)       # mantlet
    front = -d / 2 - .1
    steel.cyl(r * 1.35, .5, loc=(0, front - .2, zb), rot=FORWARD, seg=12, bevel=0)            # barrel root
    tip = front - length
    steel.cyl(r, length - .75, loc=(0, (front - .4 + tip + .35) / 2, zb), rot=FORWARD, seg=12, bevel=0)
    for f in (.3, .55):
        dark.cyl(r * 1.25, .06, loc=(0, front - length * f, zb), rot=FORWARD, seg=12, bevel=0)
    brake = a.part(f'Gun_brake_{tag}', 'Undercarriage', m)
    brake.cyl(r * 1.45, .36, loc=(0, tip + .18, zb), rot=FORWARD, seg=12, bevel=.01, bseg=1)
    for dy in (.1, .22):
        brake.box((r * 3.2, .05, r * 1.3), loc=(0, tip + dy, zb), bevel=0)
    a.part(f'Gun_bore_{tag}', 'Charred', m).cyl(r * .75, .02, loc=(0, tip + .005, zb), rot=FORWARD, seg=10, bevel=0)
    arm.box((.2, .26, .18), loc=(w * .3, -d * .15, h + .06), bevel=.02, seg=1)                # sight
    a.part(f'Gun_glass_{tag}', 'Glass', m).box((.14, .02, .08), loc=(w * .3, -d * .15 - .135, h + .07), bevel=0)
    arm.cyl(.1, .1, loc=(-w * .22, d * .15, h + .02), seg=8, bevel=0)                          # vent
    a.pivot(mkey, (0, tip, zb), m)
    return m


def _roller_track(a, x, s, idle_f, idle_r, drive, width, pitch=.24, rollers=7, roller_r=.17):
    """High-drive crawler track (Caterpillar D9 lineage) centred at x on side s: the belt runs round a front
    idler, a rear idler (both (y, z, r) touching the ground) and the drive sprocket raised above them, so it
    is a triangle from the side. Grousers on the exposed runs, bottom rollers and a rock guard, idler discs
    and a toothed sprocket on the outer face."""
    circles = [idle_f, idle_r, drive]
    outline = _hull2d([(cy + r * math.cos(k * TAU / 22), cz + r * math.sin(k * TAU / 22))
                       for cy, cz, r in circles for k in range(22)])
    a.part('Tracks', 'Undercarriage').prism(outline, width, loc=(x, 0, 0), axis='X', bevel=.03, seg=1)
    track_shoes(a.part('Track_shoes', 'Armor'), x, 0, outline, width + .05, pitch, zmin=.1, size=(.12, .08))
    face = x + s * (width / 2)
    disc, hub = a.part('Idlers', 'Steel'), a.part('Hubs', 'Undercarriage')
    for cy, cz, r in (idle_f, idle_r):
        disc.cyl(r * .78, .08, loc=(face + s * .02, cy, cz), rot=ACROSS, seg=16, bevel=.015, bseg=1)
        hub.cyl(r * .3, .1, loc=(face + s * .05, cy, cz), rot=ACROSS, seg=8, bevel=0)
    cy, cz, r = drive
    teeth = a.part('Sprockets', 'Steel')
    teeth.cyl(r * .82, .1, loc=(face + s * .02, cy, cz), rot=ACROSS, seg=18, bevel=.015, bseg=1)
    for k in range(13):
        u = k * TAU / 13
        teeth.box((.12, .14, .12), loc=(face + s * .02, cy + math.cos(u) * r * .86, cz + math.sin(u) * r * .86),
                  rot=(u, 0, 0), bevel=0)
    hub.cyl(r * .42, .12, loc=(face + s * .06, cy, cz), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    a.part('Sprocket_bolts', 'Armor').bolts(
        [(face + s * .12, cy + math.cos(k * TAU / 8) * r * .3, cz + math.sin(k * TAU / 8) * r * .3) for k in range(8)],
        r=.03, h=.04, rot=ACROSS, bevel=0)
    rolls = a.part('Rollers', 'Steel')
    y0, y1 = idle_f[0] + idle_f[2] + .1, idle_r[0] - idle_r[2] - .1
    for i in range(rollers):
        y = y0 + i * (y1 - y0) / (rollers - 1)
        rolls.cyl(roller_r, .07, loc=(face + s * .02, y, roller_r + .02), rot=ACROSS, seg=10, bevel=0)
    guard = a.part('Rock_guards', 'Armor')
    guard.box((.06, y1 - y0 + .3, .2), loc=(face + s * .08, (y0 + y1) / 2, .42), bevel=.015, seg=1)
    for i in range(4):
        y = y0 + (i + .5) * (y1 - y0) / 4
        guard.box((.07, .1, .32), loc=(face + s * .09, y, .3), bevel=0)
    return outline


# ----------------------------------------------------------------------------- armored_bulldozer
def armored_bulldozer(a):
    """Armoured combat bulldozer (IDF D9R lineage), 7.9 x 4.3 m, cab roof 3.85 m. High-drive tracks: each belt
    is a triangle round two idlers on the ground and a sprocket raised at the rear, with grousers, rollers
    and rock guards. A narrow armoured engine hood at the front between the tracks (armoured radiator
    louvres, an exhaust stack and a pre-cleaner, headlights in cages), decks over the tracks, and a tall
    armoured cab over the rear half: Team walls with bolted appliqué, small thick bullet-proof windows in
    deep frames, slat armour round the lower walls and the hood sides, work lamps, a beacon and whips. On the
    roof a remote heavy machine gun turns on `Mount_mg` (`Muzzle_mg`). Rear: a fuel tank, a tow hitch and a
    single-shank ripper on its frame and rams. Front: a semi-U blade (Team moldboard, steel cutting edge and
    end bits, a ribbed box back) on push arms outside the tracks, all on the `Blade` empty at the push
    arms' trunnions; the two lift rams and the tilt brace stay on the body."""
    _suffixed(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    team = a.part('Hull', 'Team')
    tx, tw = 1.12, .62                                            # track centre, belt width
    for s in (-1, 1):
        _roller_track(a, s * tx, s, (-1.95, .43, .44), (1.45, .43, .44), (1.02, 1.6, .6), tw)
    # Main frame between the tracks and the trunnion bosses on the roller frames.
    dark.box((1.56, 4.6, .6), loc=(0, -.1, .85), bevel=.04, seg=1)
    for s in (-1, 1):
        steel.cyl(.16, .22, loc=(s * (tx + tw / 2 + .06), -.7, .58), rot=ACROSS, seg=12, bevel=0)
    # Engine hood: narrow and tall, sloped top, armoured louvres at the front.
    hood = [(-.78, -2.55, .55), (.78, -2.55, .55), (.78, -.2, .55), (-.78, -.2, .55)]
    top = [(-.66, -2.45, 2.32), (.66, -2.45, 2.32), (.7, -.2, 2.42), (-.7, -.2, 2.42)]
    team.loft([hood, top], bevel=.05, seg=1)
    armor.box((1.5, .14, 1.35), loc=(0, -2.58, 1.45), bevel=.03, seg=1)                     # radiator guard frame
    for k in range(7):
        armor.box((1.36, .2, .06), loc=(0, -2.66, .92 + k * .18), rot=(-.5, 0, 0), bevel=0)  # louvres
    dark.box((1.3, .04, 1.2), loc=(0, -2.62, 1.45), bevel=0)
    for s in (-1, 1):
        _headlight(a, s * .56, -2.62, 2.28, guard=True)
        # Hood side armour: plates with bolts, slats standing off them over the tracks.
        armor.box((.06, 2.1, .7), loc=(s * .8, -1.35, 1.92), bevel=.015, seg=1)
        _plate_bolts(steel, s * .835, (-2.25, -1.35, -.45), 2.16, r=.03, h=.03)
        _slats(a, _frame((s * 1.02, -1.25, 1.95), (0, 0, R90)), 1.8, .72, 4)
        for y in (-2.05, -.45):
            steel.box((.26, .05, .05), loc=(s * .9, y, 2.2), bevel=0)                         # slat brackets
            steel.box((.26, .05, .05), loc=(s * .9, y, 1.66), bevel=0)
    a.part('Deck_grille', 'Undercarriage').grille(1.0, .9, loc=(0, -1.55, 2.4), rot=(-R90 + .04, 0, 0), slats=5,
                                                  depth=.06, thickness=.04)
    steel.cyl(.1, .9, loc=(-.4, -.75, 2.85), seg=10, bevel=0)                                  # exhaust stack
    a.part('Soot', 'Charred').cyl(.115, .06, loc=(-.4, -.75, 3.3), seg=10, bevel=0)
    armor.cyl(.2, .5, loc=(.4, -.85, 2.65), seg=12, bevel=.03, bseg=1)                         # pre-cleaner
    armor.cyl(.24, .08, loc=(.4, -.85, 2.93), seg=12, bevel=.02, bseg=1)
    # Decks over the tracks beside the cab, the fuel tank at the rear.
    for s in (-1, 1):
        armor.box((.8, 2.9, .08), loc=(s * 1.13, .6, 2.3), bevel=.015, seg=1)                 # y -0.85 .. 2.05
        a.part('Deck_tread', 'Undercarriage').box((.5, 2.4, .02), loc=(s * 1.13, .6, 2.345), bevel=0)
        for y in (-.7, 1.9):
            steel.box((.06, .06, .5), loc=(s * 1.45, y, 2.1), bevel=0)                         # deck stays
    armor.box((1.5, .7, 1.5), loc=(0, 2.35, 1.4), bevel=.05, seg=1)                            # fuel tank
    team.box((1.56, 2.15, 1.25), loc=(0, .87, 1.72), bevel=.04, seg=1)                          # transmission bay
    steel.cyl(.08, .06, loc=(.5, 2.35, 2.17), seg=8, bevel=0)                                  # filler cap
    for x in (-.45, .45):
        a.part('Tank_straps', 'Undercarriage').box((.1, .74, 1.54), loc=(x, 2.35, 1.4), bevel=0)
    a.part('Tank_label', 'Hazard').box((.5, .02, .22), loc=(0, 2.705, 1.75), bevel=0)
    # Cab: tall Team box on the rear half with thick bullet-proof windows and appliqué plates.
    cy0, cy1, cz0, cz1, cw = -.3, 1.9, 2.3, 3.82, 1.2
    team.box((2 * cw, cy1 - cy0, cz1 - cz0), loc=(0, (cy0 + cy1) / 2, (cz0 + cz1) / 2), bevel=.05, seg=1,
             taper=(.93, .94))
    team.box((2 * cw - .14, cy1 - cy0 - .12, .1), loc=(0, (cy0 + cy1) / 2, cz1 + .03), bevel=.03, seg=1)   # roof plate
    armor.box((2 * cw - .3, .1, .06), loc=(0, cy0 + .2, cz1 + .1), bevel=0)                    # roof rain lip
    glass, frame = a.part('Windows', 'Glass'), a.part('Window_frames', 'Armor')
    # Walls lean in (taper .93 / .94), so frames follow their faces.
    lean_x = math.atan2(cw * .07, cz1 - cz0)
    lean_y = math.atan2((cy1 - cy0) * .03, cz1 - cz0)
    zw = 3.2
    for x in (-.5, .5):                                                                         # front pair
        fy = cy0 + (cy1 - cy0) * .03 * (zw - cz0) / (cz1 - cz0)
        frame.box((.78, .16, .58), loc=(x, fy - .02, zw), rot=(-lean_y, 0, 0), bevel=.02, seg=1)
        glass.box((.56, .06, .38), loc=(x, fy - .09, zw + .01), rot=(-lean_y, 0, 0), bevel=0)
        frame.box((.84, .26, .05), loc=(x, fy - .1, zw + .31), rot=(-lean_y, 0, 0), bevel=.01, seg=1)  # brow
    for s in (-1, 1):
        fx = cw - cw * .07 * (zw - cz0) / (cz1 - cz0)
        for y in (.15, 1.25):                                                                    # side pairs
            frame.box((.16, .72, .52), loc=(s * (fx + .02), y, zw), rot=(0, -s * lean_x, 0), bevel=.02, seg=1)
            glass.box((.06, .5, .34), loc=(s * (fx + .09), y, zw + .01), rot=(0, -s * lean_x, 0), bevel=0)
        # Appliqué plates below the windows and slat armour standing off them.
        armor.box((.06, 1.9, .5), loc=(s * (cw + .01), .8, 2.62), bevel=.015, seg=1)
        _plate_bolts(steel, s * (cw + .045), (0, .8, 1.6), 2.78, r=.028, h=.03)
        _slats(a, _frame((s * (cw + .22), .8, 2.66), (0, 0, R90)), 2.1, .56, 4)
        for y in (-.1, 1.7):
            steel.box((.24, .05, .05), loc=(s * (cw + .11), y, 2.86), bevel=0)
        # Work lamps on the roof corners, grab rails up the rear corners.
        a.part('Lamp_boxes', 'Armor').box((.2, .16, .14), loc=(s * .92, cy0 + .15, cz1 + .14), bevel=.02, seg=1)
        a.part('Lamps', 'Lamp').box((.14, .03, .09), loc=(s * .92, cy0 + .065, cz1 + .14), bevel=0)
        steel.tube([(s * (cw - .1), cy1 + .06, 2.5), (s * (cw - .1), cy1 + .1, 2.6), (s * (cw - .12), cy1 + .1, 3.6),
                    (s * (cw - .14), cy1 + .04, 3.7)], .022, seg=5)
    frame.box((1.5, .16, .5), loc=(0, cy1 + .02, 3.15), bevel=.02, seg=1)                      # rear window
    glass.box((1.26, .06, .32), loc=(0, cy1 + .09, 3.16), bevel=0)
    armor.box((2.1, .08, .5), loc=(0, cy0 - .02, 2.6), bevel=.015, seg=1)                      # front appliqué
    _slats(a, _frame((0, cy0 - .26, 2.72), (0, 0, 0)), 2.3, .56, 3)
    for x in (-.95, .95):
        steel.box((.05, .26, .05), loc=(x, cy0 - .14, 2.9), bevel=0)
    # Roof: the remote weapon station, a hatch, a beacon and whips.
    rws(a, 'Mount_mg', (0, .35, cz1 + .08), length=1.05)
    armor.box((.7, .6, .08), loc=(0, 1.45, cz1 + .1), bevel=.02, seg=1)                        # roof hatch
    steel.box((.3, .05, .05), loc=(0, 1.2, cz1 + .16), bevel=0)
    _beacon(a, -.85, 1.6, cz1 + .08)
    _whip(a, .95, 1.72, cz1 + .08, 1.6)
    _whip(a, -.95, 1.72, cz1 + .08, 1.2)
    # Ripper: frame hinged under the fuel tank, rams from the tank sides, one big shank with a tooth.
    rip = a.part('Ripper', 'Armor')
    for s in (-1, 1):
        rip.limb((s * .55, 2.55, .75), (s * .45, 3.55, .95), .18, .26, bevel=.03)
        _ram(a, (s * .62, 2.72, 1.85), (s * .48, 3.5, 1.12), .08)
    rip.box((1.2, .34, .36), loc=(0, 3.6, 1.0), bevel=.04, seg=1)                               # beam
    shank = [(3.48, 1.2), (3.76, 1.2), (3.78, .62), (3.64, .26), (3.4, .06), (3.5, .42)]
    rip.prism(shank, .16, loc=(0, 0, 0), axis='X', bevel=.02)
    steel.prism([(3.6, .22), (3.48, .1), (3.3, .03), (3.34, .1), (3.5, .3)], .2, axis='X', bevel=0)  # tooth
    steel.box((.36, .3, .2), loc=(0, 2.72, .62), bevel=.02, seg=1)                             # tow hitch
    for s in (-1, 1):
        _taillight(a, s * .6, 2.71, 1.95)

    # Blade assembly on `Blade` at the push-arm trunnions.
    o = (0, -.7, .58)
    b = a.pivot('Blade', o)
    mold = a.part('Blade_moldboard', 'Team', b)
    edge = a.part('Blade_edge', 'Steel', b)
    back = a.part('Blade_back', 'Armor', b)
    front = [(-3.88, .02), (-3.76, .3), (-3.67, .6), (-3.62, .9), (-3.63, 1.2), (-3.68, 1.5), (-3.77, 1.75),
             (-3.9, 1.95)]
    prof = [(y - o[1], z - o[2]) for y, z in front + [(y + .12, z) for y, z in reversed(front)]]
    mid = 1.6
    mold.prism(prof, 2 * mid + .02, loc=(0, 0, 0), axis='X', bevel=.02, seg=1)
    lip = [(y - o[1], z - o[2]) for y, z in front[:2] + [(y + .13, z) for y, z in reversed(front[:2])]]
    edge.prism([(y - .012, z) for y, z in lip], 2 * mid + .04, axis='X', bevel=0)
    wing = .58
    hinge_y = -3.62 + .12 - o[1]
    for s in (-1, 1):
        yaw = -s * .42
        m = _frame((s * mid, hinge_y, 0), (0, 0, yaw))
        wprof = [(y - hinge_y, z) for y, z in prof]
        mold.prism(wprof, wing, loc=m @ Vector((s * wing / 2, 0, 0)), rot=(0, 0, yaw), axis='X', bevel=.02, seg=1)
        wlip = [(y - hinge_y - .012, z) for y, z in lip]
        edge.prism(wlip, wing + .02, loc=m @ Vector((s * wing / 2, 0, 0)), rot=(0, 0, yaw), axis='X', bevel=0)
        # End bit (side plate) closing the wing.
        eb = m @ Vector((s * (wing + .02), -.18, .95 - o[2]))
        edge.box((.05, .46, 1.9), loc=eb, rot=(0, 0, yaw), bevel=.01, seg=1)
    # Box-section back with vertical ribs and the push-arm and ram brackets.
    back.box((3.1, .22, 1.6), loc=(0, -3.36 - o[1], 1.0 - o[2]), bevel=.03, seg=1)
    for x in (-1.45, -.75, 0, .75, 1.45):
        back.box((.08, .3, 1.7), loc=(x, -3.3 - o[1], 1.0 - o[2]), bevel=0)
    for s in (-1, 1):
        back.box((.24, .3, .3), loc=(s * .95, -3.18 - o[1], 1.55 - o[2]), bevel=.02, seg=1)     # ram brackets
        # Push arms outside the tracks: trunnion -> blade back.
        arm_x = s * (tx + tw / 2 + .23)
        back.limb((arm_x, 0, 0), (arm_x, -3.1 - o[1], .55 - o[2]), .18, .3, bevel=.03)
        back.limb((arm_x, -3.1 - o[1], .55 - o[2]), (s * 1.5, -3.3 - o[1], .7 - o[2]), .18, .26, bevel=.02)
        a.part('Blade_pins', 'Steel', b).cyl(.1, .3, loc=(arm_x, 0, 0), rot=ACROSS, seg=10, bevel=0)  # trunnion pin
    # Lift rams from the hood sides to the blade back, a tilt brace on the right.
    for s in (-1, 1):
        steel.box((.3, .3, .3), loc=(s * .82, -2.3, 2.1), bevel=.02, seg=1)                    # ram trunnions
        _ram(a, (s * .95, -2.3, 2.1), (s * .95, -3.25, 1.58), .1)
    _ram(a, _rel((-1.66, -1.3, .62), o), _rel((-1.3, -3.28, 1.45), o), .07, parent=b)           # tilt brace


# ----------------------------------------------------------------------------- railway helpers
TREAD = .7525        # wheel tread / rail head centre either side of a track's centre line (1.435 m gauge)
RAIL_TOP = .36       # the supergun's rail heads, on its own ballasted track bed


def _track_bed(a, xs, y0, y1, pitch=.66):
    """Ballasted standard-gauge track for each track centre x in xs, from y0 to y1: a ballast bank with
    sloped shoulders, timber sleepers every `pitch` metres and two rails (steel head, dark foot) whose heads
    top out at RAIL_TOP."""
    bal, sleeper = a.part('Ballast', 'Concrete'), a.part('Sleepers', 'Wood')
    rail, foot = a.part('Rails', 'Steel'), a.part('Rail_feet', 'Undercarriage')
    L, yc = y1 - y0, (y0 + y1) / 2
    n = int(L / pitch)
    for x in xs:
        bal.prism([(x - 1.95, -.05), (x + 1.95, -.05), (x + 1.45, .15), (x - 1.45, .15)], L, loc=(0, yc, 0),
                  axis='Y', bevel=.03, seg=1)
        for k in range(n):
            sleeper.box((2.6, .24, .14), loc=(x, y0 + (k + .5) * L / n, .19), bevel=.01, seg=1)
        for s in (-1, 1):
            rail.box((.07, L, .1), loc=(x + s * TREAD, yc, .31), bevel=.01, seg=1)
            foot.box((.15, L, .03), loc=(x + s * TREAD, yc, .265), bevel=0)


def _rail_bogie(a, x0, y, axles, pitch, r, z0=0.0, frame_len=None):
    """Railway bogie centred at (x0, y) with its wheel treads on rail heads at height z0: axles, wheels on the
    1.435 m gauge (treads at x0 +- 0.7525), hubs, axle boxes, side frames with springs and a bolster."""
    wheel, under, steel = a.part('Wheels', 'Steel'), a.part('Bogies', 'Undercarriage'), a.part('Bogie_steel', 'Steel')
    frame_len = frame_len or (axles - 1) * pitch + 2 * r + .3
    zc = z0 + r
    for i in range(axles):
        ay = y + (i - (axles - 1) / 2) * pitch
        steel.cyl(.08, 1.9, loc=(x0, ay, zc), rot=ACROSS, seg=8, bevel=0)                        # axle
        for s in (-1, 1):
            wheel.cyl(r, .13, loc=(x0 + s * TREAD, ay, zc), rot=ACROSS, seg=12, bevel=0)
            under.cyl(r * .42, .16, loc=(x0 + s * (TREAD + .05), ay, zc), rot=ACROSS, seg=6, bevel=0)  # hub
            under.box((.22, .3, .3), loc=(x0 + s * .98, ay, zc), bevel=0)                         # axle box
    for s in (-1, 1):
        under.box((.14, frame_len, .42), loc=(x0 + s * 1.1, y, zc + .12), bevel=.03, seg=1)      # side frame
        for k in range(axles - 1):
            steel.cyl(.08, .3, loc=(x0 + s * 1.1, y + (k + .5 - (axles - 1) / 2) * pitch, zc + .48), seg=8, bevel=0)
    under.box((2.1, .5, .26), loc=(x0, y, zc + .5), bevel=.03, seg=1)                             # bolster


def _headstock(a, x0, face, end, z0=0.0, width=2.9):
    """Hazard-striped headstock across a track at the carriage end `face` (end -1 front, +1 rear), buffers
    reaching out 0.38 m and a coupler; rails at height z0."""
    zb = z0 + 1.06
    c = face - end * .1
    a.part('Headstocks', 'SafetyStripe').box((width, .2, .5), loc=(x0, c, zb), bevel=.02, seg=1)
    bars = a.part('Headstock_bars', 'Charred')
    n = int(width / .4)
    for k in range(n):
        bars.box((.13, .02, .56), loc=(x0 - (n - 1) * .2 + k * .4, face + end * .005, zb), rot=(0, .6, 0), bevel=0)
    steel = a.part('Buffers', 'Steel')
    for s in (-1, 1):
        steel.cyl(.1, .34, loc=(x0 + s * .85, face + end * .15, zb), rot=FORWARD, seg=8, bevel=0)
        steel.cyl(.22, .06, loc=(x0 + s * .85, face + end * .345, zb), rot=FORWARD, seg=12, bevel=.015, bseg=1)
    a.part('Couplers', 'Armor').box((.26, .3, .2), loc=(x0, face + end * .12, zb - .05), bevel=.03, seg=1)


def _genset(a, parent, loc, size=(2.6, 1.4, 1.45)):
    """Diesel generator set on a skid along X at loc (its base centre, relative to `parent`): a housing with
    Team service doors on both long sides, a radiator grille at +X, louvres, an exhaust stack with a rain
    cap, a control panel, lifting eyes and a hazard stripe along the skid."""
    x, y, z = loc
    w, d, h = size
    a.part('Genset_skid', 'Undercarriage', parent).box((w + .2, d + .1, .16), loc=(x, y, z + .08), bevel=.02, seg=1)
    a.part('Genset_stripe', 'Hazard', parent).box((w + .22, .02, .06), loc=(x, y - d / 2 - .05, z + .1), bevel=0)
    body = a.part('Genset_body', 'Armor', parent)
    body.box((w, d, h - .16), loc=(x, y, z + .16 + (h - .16) / 2), bevel=.04, seg=1)
    doors = a.part('Genset_doors', 'Team', parent)
    for sy in (-1, 1):
        for dx in (-.55, .25):
            doors.box((.72, .04, h - .5), loc=(x + dx * w / 2, y + sy * (d / 2 + .005), z + .16 + (h - .16) / 2),
                      bevel=.01, seg=1)
    a.part('Genset_grille', 'Undercarriage', parent).grille(d - .3, h - .5, loc=(x + w / 2 + .02, y, z + .2 + h / 2),
                                                            rot=(0, 0, R90), slats=5, depth=.05, thickness=.04)
    steel = a.part('Genset_steel', 'Steel', parent)
    steel.cyl(.09, .7, loc=(x - w * .3, y + d * .2, z + h + .3), seg=8, bevel=0)                  # exhaust stack
    steel.cyl(.13, .05, loc=(x - w * .3, y + d * .2, z + h + .66), seg=8, bevel=0)                # rain cap
    for dx in (-w * .38, w * .38):
        steel.tube([(x + dx - .08, y, z + h - .02), (x + dx - .08, y, z + h + .08), (x + dx + .08, y, z + h + .08),
                    (x + dx + .08, y, z + h - .02)], .02, seg=4)
    a.part('Genset_panel', 'Glass', parent).box((.3, .03, .2), loc=(x - w * .38, y - d / 2 - .01, z + h * .7), bevel=0)


# ----------------------------------------------------------------------------- rail_supergun
SG_TRACKS = (2.5, -2.5)          # track centres (left, right)
SG_BOGIES = (-9.75, -3.25, 3.25, 9.75)
SG_END = 13.2                    # headstock faces at y = +-SG_END
SG_DECK = 3.56                   # top of the lower carriage's deck


def rail_supergun(a):
    """Super-heavy railway gun (Schwerer Gustav / K5 lineage), 52 x 7.8 m, muzzle 15.9 m up at rest: it stands on
    two parallel standard-gauge tracks of its own ballasted bed (rail heads 0.36 m up, 30 m long). The
    lower carriage: per track four four-axle bogies under two span bolsters and a Team box girder, cross
    girders, a deck with hazard-striped headstocks, buffers, walkways, railings and ladders at the ends. On
    a slewing ring amidships the upper carriage (`Turret`, it traverses): a base, two tall Team side walls
    carrying the trunnion bosses, a raised breech platform, a rear loading platform with a crew cabin and
    shells on a trolley. The 41.9 m, 80 cm gun rests at 10 degrees: a Team jacket with steel hoops over the
    rear third, a tapering chase with a muzzle swell (`Muzzle_main` at the bore), a sliding-block breech,
    the cradle with recoil cylinders on top, two toothed elevating arcs hanging under the trunnion and a
    queen-post truss over the barrel against droop (the Paris gun's). Every elevating part is named
    Main_cannon*, and the arcs put the game's elevation pivot within 0.3 m of the trunnion.

    Boss parts: `Part_main` (the whole upper carriage and gun, holding `Turret`) on the slewing ring;
    `Part_gun` / `Part_gun.001`: 40 mm guns on pedestals at the front corners of the deck (left, right; on
    `Mount_gun` / `Mount_gun.001` with `Muzzle_gun` / `Muzzle_gun.001`); `Part_generator`: the diesel
    generator set on the rear deck; `Part_crane`: the ammunition jib crane on the loading platform (under
    the Turret, it turns with it)."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, team = a.part('Chassis', 'Undercarriage'), a.part('Hull', 'Team')
    rt = RAIL_TOP
    _track_bed(a, SG_TRACKS, -15.0, 15.0)
    for x in SG_TRACKS:
        for y in SG_BOGIES:
            _rail_bogie(a, x, y, 4, 1.25, .5, z0=rt)
        for yc in (-6.5, 6.5):
            dark.box((2.0, 11.6, .5), loc=(x, yc, rt + 1.35), bevel=.03, seg=1)                  # span bolsters
            for yb in (yc - 3.25, yc + 3.25):
                steel.cyl(.42, .16, loc=(x, yb, rt + 1.08), seg=12, bevel=0)                      # centre pivots
        team.box((1.7, 2 * SG_END - .3, 1.5), loc=(x, 0, rt + 2.35), bevel=.05, seg=1)            # main girder
        s = 1 if x > 0 else -1
        for y in (-11.5, -8.0, -4.8, -1.6, 1.6, 4.8, 8.0, 11.5):                                  # girder ribs
            armor.box((.08, .22, 1.3), loc=(x + s * .87, y, rt + 2.35), bevel=0)
        _plate_bolts(steel, x + s * .9, [y + dy for y in (-9.75, -3.25, 3.25, 9.75) for dy in (-.8, .8)], rt + 3.0,
                     r=.04, h=.04)
        for end, face in ((-1, -SG_END), (1, SG_END)):
            _headstock(a, x, face, end, rt)
    for y in (-12.0, -8.0, -1.8, 1.8, 8.0, 12.0):
        dark.box((3.4, .5, 1.2), loc=(0, y, 2.8), bevel=.02, seg=1)                               # cross girders
    armor.box((7.0, 2 * SG_END - .2, .14), loc=(0, 0, SG_DECK - .07), bevel=.03, seg=1)          # deck
    tread = a.part('Deck_tread', 'Undercarriage')
    for s in (-1, 1):
        tread.box((.8, 2 * SG_END - 1.0, .02), loc=(s * 3.0, 0, SG_DECK + .005), bevel=0)
    for yc in (-10.6, 10.6):                                                                       # Team deck plates
        if yc > 0:
            team.box((1.6, 4.2, .04), loc=(2.4, yc, SG_DECK), bevel=0)
            team.box((1.6, 4.2, .04), loc=(-2.4, yc, SG_DECK), bevel=0)
        else:
            team.box((1.8, 3.8, .04), loc=(0, yc - .2, SG_DECK), bevel=0)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):                          # railings only beyond the upper carriage's sweep
        _railing(rail, [(s * 3.42, -8.4, SG_DECK), (s * 3.42, -12.9, SG_DECK)], every=1.5)
        _railing(rail, [(s * 3.42, 8.4, SG_DECK), (s * 3.42, 12.9, SG_DECK)], every=1.5)
        for end in (-1, 1):
            ladder(a.part('Ladders', 'Steel'), (s * 3.62, end * 12.5, rt), SG_DECK + .9, 0, width=.44, step=.34,
                   rung=.03)
    steel.cyl(2.9, .16, loc=(0, 0, SG_DECK + .06), seg=32, bevel=.02, bseg=1)                     # slewing ring
    for k in range(16):
        u = k * TAU / 16
        steel.box((.2, .3, .12), loc=(math.cos(u) * 3.05, math.sin(u) * 3.05, SG_DECK + .04), rot=(0, 0, u), bevel=0)
    # Boss parts on the lower carriage: the two 40 mm guns, the generator set.
    for name, x in (('Part_gun', 2.6), ('Part_gun.001', -2.6)):
        pg = pv(a, name, (x, -11.3, SG_DECK))
        tag = name[5:].replace('.', '_')
        a.part(f'Pedestal_{tag}', 'Armor', pg).cyl(.8, .8, loc=(0, 0, .4), seg=18, bevel=.04, bseg=1)
        a.part(f'Pedestal_band_{tag}', 'SafetyStripe', pg).cyl(.82, .12, loc=(0, 0, .62), seg=18, bevel=0)
        autocannon(a, name.replace('Part_', 'Mount_'), (0, 0, .8), parent=name, length=2.4, r=.065, size=(1.1, 1.3, .6))
    pgen = pv(a, 'Part_generator', (0, 11.2, SG_DECK))
    _genset(a, pgen, (0, 0, 0))

    # Upper carriage on `Turret`, inside Part_main.
    pm = pv(a, 'Part_main', (0, 0, SG_DECK))
    t = a.pivot('Turret', (0, 0, .14), pm)
    tarm, tsteel = a.part('Turret_armor', 'Armor', t), a.part('Turret_steel', 'Steel', t)
    tteam, tdark = a.part('Turret_walls', 'Team', t), a.part('Turret_dark', 'Undercarriage', t)
    tarm.box((6.2, 13.5, .6), loc=(0, .25, .3), bevel=.05, seg=1)                                 # base y -6.5 .. 7
    tsteel.cyl(2.75, .12, loc=(0, 0, .02), seg=32, bevel=0)
    wall = [(-6.2, .55), (6.9, .55), (6.9, 3.4), (4.6, 5.5), (3.0, 6.7), (-.8, 6.7), (-2.8, 5.0), (-6.2, 2.2)]
    T = Vector((0, 1.0, 5.2))                                                                      # trunnion
    for s in (-1, 1):
        tteam.prism(wall, .9, loc=(s * 2.05, 0, 0), axis='X', bevel=.06, seg=1)
        for y, h in ((-5.0, 1.9), (-3.0, 3.3), (4.2, 3.9), (6.2, 2.6)):                           # ribs
            tarm.box((.1, .26, h), loc=(s * 2.53, y, .55 + h / 2), bevel=0)
        tsteel.cyl(1.05, .22, loc=(s * 2.6, T.y, T.z), rot=ACROSS, seg=20, bevel=.03, bseg=1)       # trunnion boss
        tarm.cyl(.55, .3, loc=(s * 2.68, T.y, T.z), rot=ACROSS, seg=14, bevel=.03, bseg=1)
        _plate_bolts(tsteel, s * 2.72, (T.y - .8, T.y + .8), T.z - .8, r=.05, h=.05)
        tarm.box((.1, 3.6, .14), loc=(s * 2.53, 1.1, 6.62), bevel=0)                               # coping
        ladder(a.part('Turret_ladders', 'Steel', t), (s * 2.62, -5.3, .6), 2.9, 0, width=.44, step=.34, rung=.03)
        # Elevation gearboxes (the arcs of the cradle mesh with their pinions).
        tdark.box((.46, 1.0, 1.4), loc=(s * 1.4, .45, 1.3), bevel=.03, seg=1)
    # Breech platform between the walls, the rear loading platform on struts, its railings.
    tarm.box((3.1, 2.7, .25), loc=(0, 5.55, 2.72), bevel=.02, seg=1)
    for x in (-1.2, 1.2):
        tsteel.box((.14, .14, 2.1), loc=(x, 5.0, 1.6), bevel=0)
        tsteel.box((.14, .14, 2.1), loc=(x, 6.6, 1.6), bevel=0)
    tarm.box((6.2, 3.8, .3), loc=(0, 8.8, 1.75), bevel=.03, seg=1)                                # y 6.9 .. 10.7
    for x in (-2.7, -.9, .9, 2.7):
        tsteel.limb((x, 6.7, .55), (x, 9.8, 1.62), .16, .16, bevel=0)                              # struts
    trail = a.part('Turret_rails', 'Steel', t)
    _railing(trail, [(-3.0, 7.0, 1.9), (-3.0, 10.6, 1.9), (3.0, 10.6, 1.9), (3.0, 7.0, 1.9)], every=1.3)
    ladder(a.part('Turret_ladders', 'Steel', t), (0, 6.95, 1.9), 2.95, 0, width=.5, step=.3, rung=.03)  # to the breech
    # Crew cabin on the left of the loading platform.
    cab = a.part('Cabin', 'Team', t)
    cab.box((1.9, 2.3, 2.0), loc=(2.0, 9.25, 2.9), bevel=.05, seg=1)
    tarm.box((2.1, 2.5, .12), loc=(2.0, 9.25, 3.95), bevel=.02, seg=1)
    cglass = a.part('Cabin_glass', 'Glass', t)
    for y in (8.7, 9.8):
        cglass.box((.04, .7, .5), loc=(2.96, y, 3.2), bevel=0)
    cglass.box((1.2, .04, .5), loc=(2.0, 8.09, 3.2), bevel=0)
    fbox(tarm, '-x', (1.05, 9.3, 2.85), (.8, .05, 1.7), out=.02, bevel=.01)                         # door
    _antenna(a, t, 2.7, 10.2, 4.0, 2.2)
    # Shells and charge cases on a trolley (Gilded brass cases, used sparingly).
    trol = a.part('Trolley', 'Undercarriage', t)
    trol.box((1.0, 4.2, .2), loc=(-.4, 8.8, 2.1), bevel=.02, seg=1)
    for y in (7.2, 10.4):
        for x in (-.8, 0.0):
            a.part('Trolley_wheels', 'Steel', t).cyl(.14, .08, loc=(x, y, 2.0), rot=ACROSS, seg=8, bevel=0)
    shell = a.part('Shell', 'Steel', t)
    shell.lathe([(.38, 0), (.38, 2.1), (.3, 2.8), (.12, 3.25), (0, 3.35)], loc=(-.4, 10.55, 2.6), rot=FORWARD, seg=14)
    a.part('Shell_bands', 'Hazard', t).cyl(.395, .16, loc=(-.4, 10.1, 2.6), rot=FORWARD, seg=14, bevel=0)
    a.part('Charges', 'Gilded', t).cyl(.34, 1.3, loc=(-.4, 7.9, 2.55), rot=FORWARD, seg=12, bevel=.02, bseg=1)
    # Ammunition jib crane (Part_crane) on the loading platform's right rear corner.
    pc = pv(a, 'Part_crane', (-2.3, 10.0, 1.9), 'Turret')
    crane = a.part('Crane', 'Hazard', pc)
    csteel = a.part('Crane_steel', 'Steel', pc)
    csteel.cyl(.36, .2, loc=(0, 0, .1), seg=14, bevel=.02, bseg=1)
    crane.cyl(.2, 3.4, loc=(0, 0, 1.9), seg=12, bevel=.02, bseg=1)                                   # post
    crane.limb((0, 0, 3.4), (1.7, -2.6, 3.4), .26, .34, bevel=.03)                                    # jib
    crane.limb((0, 0, 2.2), (.9, -1.4, 3.25), .14, .14, bevel=0)                                     # brace
    csteel.box((.4, .5, .3), loc=(-.1, .3, 3.4), bevel=.02, seg=1)                                   # winch
    csteel.tube([(1.62, -2.48, 3.22), (1.62, -2.48, 1.55)], .025, seg=4)                             # hook cable
    csteel.box((.2, .16, .26), loc=(1.62, -2.48, 1.45), bevel=0)                                      # hook block
    csteel.tube([(1.52, -2.48, 1.32), (1.2, -2.48, .98), (2.04, -2.48, .98), (1.72, -2.48, 1.32)], .02, seg=4)  # sling

    # The gun: every elevating part is a Main_cannon* child of the Turret.
    p = math.radians(10)
    at = _axis(T, p)
    crot, brot = (R90 - p, 0, 0), (-p, 0, 0)
    tube = a.part('Main_cannon', 'Armor', t)
    tube.lathe([(1.02, 0), (1.02, 15.3), (.93, 15.8), (.64, 38.0), (0, 38.0)], loc=tuple(at(.6)), rot=crot,
               seg=24)                                                                               # s .6 .. 38.6
    a.part('Muzzle_brake', 'Armor', t).lathe([(.64, 0), (.74, .12), (.74, .85), (.42, .85), (.42, .3), (0, .3)],
                                            loc=tuple(at(38.55)), rot=crot, seg=24)                 # swell, to 39.4
    a.part('Main_cannon_bore', 'Charred', t).cyl(.415, .02, loc=tuple(at(38.87)), rot=crot, seg=16, bevel=0)
    a.part('Main_cannon_jacket', 'Team', t).cyl(1.1, 15.0, loc=tuple(at(8.1)), rot=crot, seg=24, bevel=.03, bseg=1)
    hoops = a.part('Main_cannon_hoops', 'Steel', t)
    for sv in (1.2, 5.0, 9.0, 13.0, 15.45):
        hoops.cyl(1.17, .3, loc=tuple(at(sv)), rot=crot, seg=24, bevel=.01, bseg=1)
    for sv in (23.0, 31.0):
        r = .93 - (sv - 16.4) * (.29 / 22)
        hoops.cyl(r + .06, .25, loc=tuple(at(sv)), rot=crot, seg=20, bevel=0)
    breech = a.part('Main_cannon_breech', 'Armor', t)
    breech.box((2.5, 3.1, 2.5), loc=tuple(at(-.95)), rot=brot, bevel=.08, seg=1)                     # s -2.5 .. .6
    bsteel = a.part('Main_cannon_block', 'Steel', t)
    bsteel.box((3.1, .7, .8), loc=tuple(at(-1.9, .1)), rot=brot, bevel=.03, seg=1)                   # sliding block
    bsteel.box((.5, .3, .5), loc=tuple(at(-2.6, .4, .6)), rot=brot, bevel=.02, seg=1)                # firing gear
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((2.8, 10.0, .3), loc=tuple(at(5.0, -1.35)), rot=brot, bevel=.03, seg=1)                # bottom plate
    for sd in (-1.4, 1.4):
        cradle.box((.3, 10.0, 2.3), loc=tuple(at(5.0, -.25, sd)), rot=brot, bevel=.03, seg=1)        # side plates
    recoil = a.part('Main_cannon_recoil', 'Steel', t)
    for sd in (-.62, .62):
        recoil.cyl(.32, 8.6, loc=tuple(at(4.6, 1.4, sd)), rot=crot, seg=14, bevel=.02, bseg=1)
    recoil.box((2.1, .5, .5), loc=tuple(at(8.9, 1.3)), rot=brot, bevel=.03, seg=1)                   # front yoke
    recoil.cyl(.4, 3.3, loc=tuple(T), rot=ACROSS, seg=16, bevel=.02, bseg=1)                          # trunnion pin
    # Toothed elevating arcs under the trunnion (radius 2.9), one inside each wall.
    arc = a.part('Main_cannon_arcs', 'Steel', t)
    down = -Vector((0, math.sin(p), math.cos(p)))
    fwd = Vector((0, -math.cos(p), math.sin(p)))
    R = 2.9
    for sd in (-1.4, 1.4):
        pts = []
        for k in range(12):
            ph = math.radians(55) * k / 11
            pts.append(T + (down * math.cos(ph) + fwd * math.sin(ph)) * R)
        for q0, q1 in zip(pts, pts[1:]):
            arc.limb((sd, q0.y, q0.z), (sd, q1.y, q1.z), .2, .3, bevel=0)
        for q in (pts[0], pts[5], pts[11]):                                                         # spokes
            arc.limb((sd, T.y, T.z), (sd, q.y, q.z), .16, .16, bevel=0)
    for sd in (-1.4, 1.4):                                                                         # pinions
        q = T + down * (R + .38)
        tsteel.cyl(.32, .3, loc=(sd, q.y, q.z), rot=ACROSS, seg=12, bevel=0)
    # Queen-post truss over the barrel.
    truss = a.part('Main_cannon_truss', 'Steel', t)
    tops = []
    for sv, h in ((12.0, 3.3), (25.0, 2.7)):
        truss.limb(tuple(at(sv, 1.0)), tuple(at(sv, h)), .22, .22, bevel=.02)
        truss.cyl(1.08 if sv < 16 else .88, .3, loc=tuple(at(sv)), rot=crot, seg=20, bevel=0)      # clamp ring
        tops.append(at(sv, h))
    truss.limb(tuple(tops[0]), tuple(tops[1]), .16, .16, bevel=0)
    truss.tube([tuple(at(2.0, 1.12)), tuple(tops[0])], .06, seg=6)
    truss.tube([tuple(tops[1]), tuple(at(35.0, .7))], .06, seg=6)
    a.pivot('Muzzle_main', tuple(at(39.4)), t)


# ----------------------------------------------------------------------------- rail_tractor
RT_AXLES = (-3.0, -1.4, .2)      # three coupled axles; the jackshaft behind them


def _hood_ring(y, w, z0, zs, wt, zt):
    """Hood cross-section at y: flat sides to zs, chamfered to a roof of half-width wt at zt."""
    return [(-w, y, z0), (w, y, z0), (w, y, zs), (wt, y, zt), (-wt, y, zt), (-w, y, zs)]


def rail_tractor(a):
    """Armoured diesel shunting locomotive (Wehrmacht V 36 / D 311 "Panzerlok" lineage), one of the supergun's two
    tractors: 10.9 m over the buffers, 3.1 m wide, cab roof 3.9 m, wheels on the rail heads at z = 0 (on the
    supergun's own bed its rails top out at 0.36 m). A centre cab between a long front hood and a short rear
    hood, all in chamfered Team armour: the front hood with an armoured radiator grille and louvres, a
    headlamp, side louvres and access doors, an exhaust stack with a spark arrestor; the cab with vision slits
    behind visors, side doors and steps, a roof lamp, horn and whip; the rear hood with the fuel filler and
    tool boxes. Running boards with handrails and a hazard-striped headstock with buffers at each end. Below:
    three coupled axles in an outside frame with red side rods and cranks and a jackshaft with its big
    crank disc (the V 36's drive), sand boxes and brake gear. No weapon, no pivots."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, team = a.part('Chassis', 'Undercarriage'), a.part('Hull', 'Team')
    red = a.part('Rods', 'BarrelRed')
    r = .55
    for y in RT_AXLES:
        steel.cyl(.09, 1.98, loc=(0, y, r), rot=ACROSS, seg=8, bevel=0)                            # axle
        for s in (-1, 1):
            a.part('Wheels', 'Steel').cyl(r, .13, loc=(s * TREAD, y, r), rot=ACROSS, seg=16, bevel=.012, bseg=1)
            red.cyl(r * .78, .15, loc=(s * TREAD, y, r), rot=ACROSS, seg=14, bevel=0)             # wheel centres
            dark.box((.14, .32, .34), loc=(s * .92, y, r), bevel=.02, seg=1)                       # axle boxes
    jy = 2.1                                                                                       # jackshaft
    steel.cyl(.12, 2.2, loc=(0, jy, .72), rot=ACROSS, seg=10, bevel=0)
    for s in (-1, 1):
        # Quartered cranks: the left pins stand up, the right ones forward.
        off = Vector((0, 0, .26)) if s > 0 else Vector((0, -.26, 0))
        pins = []
        for y in RT_AXLES:
            c = Vector((s * 1.02, y, r))
            red.limb(tuple(c), tuple(c + off), .06, .16, bevel=0)                                  # crank arms
            pins.append(c + off)
            steel.cyl(.05, .1, loc=tuple(Vector((s * 1.06, 0, 0)) + Vector((0, (c + off).y, (c + off).z))), rot=ACROSS,
                      seg=6, bevel=0)
        red.box((.06, pins[-1].y - pins[0].y + .24, .12), loc=(s * 1.09, (pins[0].y + pins[-1].y) / 2, pins[0].z),
                bevel=.01, seg=1)                                                                  # coupling rod
        jc = Vector((s * 1.02, jy, .72))
        red.cyl(.4, .08, loc=tuple(jc), rot=ACROSS, seg=16, bevel=.01, bseg=1)                     # jackshaft disc
        jp = jc + off * 1.15
        red.limb((s * 1.15, pins[-1].y, pins[-1].z), (s * 1.15, jp.y, jp.z), .07, .14, bevel=0)    # connecting rod
        armor.box((.08, 7.6, .62), loc=(s * .92, -.3, .98), bevel=.015, seg=1)                     # outside frame
        _plate_bolts(steel, s * .97, (-3.8, -2.2, -.6, 1.0, 2.8), 1.18, r=.03, h=.03)
        for y in (-3.8, -.6):
            dark.box((.3, .4, .25), loc=(s * 1.2, y, 1.075), bevel=.02, seg=1)                     # sand boxes
        dark.box((.06, .2, .5), loc=(s * .85, -2.2, .55), rot=(.2, 0, 0), bevel=0)                 # brake hangers
    armor.box((3.0, 10.3, .12), loc=(0, 0, 1.26), bevel=.02, seg=1)                                # running boards
    for s in (-1, 1):
        armor.box((.05, 10.1, .2), loc=(s * 1.5, 0, 1.16), bevel=0)                                 # valances
    for end in (-1, 1):
        _headstock(a, 0, end * 5.3, end, 0.0, width=2.9)
        for s in (-1, 1):
            steel.box((.32, .24, .04), loc=(s * 1.28, end * 4.95, .82), bevel=0)                    # end steps
            steel.box((.04, .04, .5), loc=(s * 1.42, end * 4.95, 1.02), bevel=0)
    # Long front hood.
    hood = [_hood_ring(-4.8, .92, 1.32, 2.45, .6, 2.95), _hood_ring(-1.25, .95, 1.32, 2.5, .62, 3.0)]
    team.loft(hood, bevel=.05, seg=1)
    armor.box((1.7, .16, 1.2), loc=(0, -4.84, 1.98), bevel=.03, seg=1)                            # grille frame
    for k in range(6):
        armor.box((1.56, .16, .05), loc=(0, -4.95, 1.5 + k * .19), rot=(-.55, 0, 0), bevel=0)      # louvres
    dark.box((1.5, .04, 1.1), loc=(0, -4.9, 1.98), bevel=0)
    _headlamp(a, (0, -4.86, 2.75), r=.16)
    for s in (-1, 1):
        for end in (-1, 1):                                          # marker lamps: white ahead, red behind
            armor.box((.22, .16, .22), loc=(s * 1.2, end * 5.07, 1.43), bevel=.02, seg=1)
            a.part('Lamps' if end < 0 else 'Tail_lamps', 'Lamp' if end < 0 else 'LavaGlow').box(
                (.14, .04, .12), loc=(s * 1.2, end * 5.155, 1.45), bevel=0)
        a.part('Hood_louvres', 'Undercarriage').grille(1.2, .45, loc=(s * .955, -3.6, 2.0), rot=(0, 0, s * R90),
                                                        slats=4, depth=.05, thickness=.035)
        fbox(armor, '+x' if s > 0 else '-x', (s * .93, -2.2, 1.9), (.9, .05, .8), out=.02, bevel=.01)   # doors
        steel.box((.04, .14, .04), loc=(s * .99, -1.9, 1.9), bevel=0)
    steel.cyl(.14, .7, loc=(0, -2.1, 3.3), seg=10, bevel=0)                                        # exhaust stack
    a.part('Soot', 'Charred').cyl(.2, .22, loc=(0, -2.1, 3.7), seg=10, bevel=.02, bseg=1)          # spark arrestor
    armor.box((1.0, .9, .08), loc=(0, -3.6, 2.99), bevel=.02, seg=1)                               # roof hatch
    # Centre cab with sloped armour.
    cab = [_hood_ring(-1.3, 1.42, 1.32, 3.3, 1.0, 3.95), _hood_ring(1.3, 1.42, 1.32, 3.3, 1.0, 3.95)]
    team.loft(cab, bevel=.06, seg=1)
    glass, visor = a.part('Vision_slits', 'Glass'), a.part('Visors', 'Armor')
    for end in (-1, 1):
        for x in (-.6, .6):
            glass.box((.5, .04, .16), loc=(x, end * 1.31, 3.35), bevel=0)
            visor.box((.62, .18, .04), loc=(x, end * 1.36, 3.46), bevel=0)
    for s in (-1, 1):
        fbox(armor, '+x' if s > 0 else '-x', (s * 1.42, 0, 2.2), (.8, .05, 1.6), out=.02, bevel=.01)   # doors
        glass.box((.04, .4, .14), loc=(s * 1.44, 0, 3.2), bevel=0)
        for k in range(2):
            steel.box((.3, .5, .04), loc=(s * 1.35, 0, .82 + k * .25), bevel=0)                     # steps
        steel.tube([(s * 1.47, -.5, 1.4), (s * 1.47, -.5, 2.8)], .02, seg=4)                        # grab rails
        steel.tube([(s * 1.47, .5, 1.4), (s * 1.47, .5, 2.8)], .02, seg=4)
    armor.box((2.2, 2.9, .1), loc=(0, 0, 3.98), bevel=.03, seg=1)                                  # cab roof
    a.part('Roof_lamp', 'Lamp').cyl(.12, .05, loc=(.5, -1.5, 4.12), rot=FORWARD, seg=10, bevel=0)
    armor.cyl(.16, .2, loc=(.5, -1.42, 4.12), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    armor.box((.1, .5, .14), loc=(.5, -1.2, 4.06), bevel=0)
    steel.cyl(.05, .3, r2=.09, loc=(-.5, -1.25, 4.15), rot=FORWARD, seg=8, bevel=0)                # horn
    _whip(a, -.8, 1.1, 4.03, 1.4)
    # Short rear hood.
    team.loft([_hood_ring(1.25, .9, 1.32, 2.2, .58, 2.7), _hood_ring(4.8, .88, 1.32, 2.15, .56, 2.62)], bevel=.05, seg=1)
    steel.cyl(.12, .1, loc=(.4, 3.4, 2.72), seg=8, bevel=0)                                        # fuel filler
    for s in (-1, 1):
        _stowage_bin(a, (s * 1.15, 3.3, 1.32), (.4, 1.2, .5), latch_side=s)
    a.part('Lamps', 'Lamp').box((.3, .04, .14), loc=(0, 4.82, 2.45), bevel=0)
    # Handrails along both hoods.
    rail = a.part('Handrails', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-4.7, -1.45), (1.45, 4.7)):
            rail.tube([(s * 1.42, y0, 2.3), (s * 1.42, y1, 2.3)], .02, seg=4)
            for y in (y0, (y0 + y1) / 2, y1):
                rail.box((.03, .03, 1.0), loc=(s * 1.42, y, 1.82), bevel=0)


# ----------------------------------------------------------------------------- targeting_station
def targeting_station(a):
    """The supergun's fire-control post (Wurzburg-Riese radar and a coast-artillery rangefinder post lineage),
    8 x 6.5 m on a concrete pad, mast 10.3 m: a hardened Team cabin with lit vision slits under visors, a
    door and steps, an air vent and a stereoscopic rangefinder on the roof (a 4 m tube with end windows on a
    pedestal, a ladder up to it); sandbag walls along the front; a generator set and a cable reel.

    Boss parts: `Part_radar` holds the fire-control radar: a pedestal and, spinning on `Radar`, a turntable,
    a yoke and a 3.4 m parabolic dish tilted up 25 degrees with its feed horn on four struts and the receiver
    box behind; `Part_antenna` holds the guyed lattice mast with its dipole head, a link dish, a floodlight
    and the obstruction light."""
    _suffixed(a)
    rng = random.Random(88)
    a.part('Pad', 'Concrete').prism(chamfered(8.0, 6.5, .5), .3, loc=(0, 0, .1), axis='Z', bevel=.04, seg=1)  # z -.05 .. .25
    z0 = .25
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    # Cabin.
    cx, cy, cw, cd, ch = -1.6, .2, 3.4, 2.8, 2.6
    a.part('Cabin', 'Team').box((cw, cd, ch), loc=(cx, cy, z0 + ch / 2), bevel=.06, seg=1)
    a.part('Cabin_roof', 'Team').box((cw + .3, cd + .3, .14), loc=(cx, cy, z0 + ch + .05), bevel=.03, seg=1)  # roof slab
    armor.box((cw + .34, .12, .1), loc=(cx, cy - cd / 2 - .1, z0 + ch + .1), bevel=0)             # drip edge
    lit, visor = a.part('Lit_slits', 'Lamp'), a.part('Visors', 'Armor')
    for x in (-2.6, -1.6, -.6):
        fbox(lit, '-y', (x, cy - cd / 2, z0 + 1.75), (.6, .05, .16), out=.015)
        fbox(visor, '-y', (x, cy - cd / 2, z0 + 1.92), (.8, .3, .05), out=.14)
    for y in (-.4, .8):
        fbox(lit, '-x', (cx - cw / 2, y, z0 + 1.75), (.5, .05, .16), out=.015)
        fbox(visor, '-x', (cx - cw / 2, y, z0 + 1.92), (.7, .3, .05), out=.14)
    fbox(armor, '+x', (cx + cw / 2, cy + .3, z0 + 1.05), (.9, .06, 2.0), out=.025, bevel=.015)      # door
    fbox(steel, '+x', (cx + cw / 2, cy - .02, z0 + 1.0), (.05, .06, .2), out=.06)
    armor.box((.5, 1.2, .08), loc=(cx + cw / 2 + .22, cy + .3, z0 + 2.25), bevel=.02, seg=1)        # door canopy
    a.part('Vent', 'Undercarriage').grille(.8, .5, loc=(cx, cy + cd / 2 + .02, z0 + 2.1), rot=(0, 0, math.pi), slats=4,
                                           depth=.05, thickness=.035)
    ladder(a.part('Ladder', 'Steel'), (cx - .9, cy + cd / 2 + .12, z0), z0 + ch + .9, 0, width=.44, step=.32, rung=.03)
    # Stereoscopic rangefinder on the roof.
    rz = z0 + ch + .12
    armor.cyl(.3, .5, loc=(cx, cy - .3, rz + .25), seg=12, bevel=.03, bseg=1)                      # pedestal
    armor.box((.7, .6, .45), loc=(cx, cy - .3, rz + .7), bevel=.04, seg=1)                          # eyepiece box
    rf = a.part('Rangefinder', 'Team')
    rf.cyl(.17, 3.4, loc=(cx, cy - .3, rz + .8), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    for s in (-1, 1):
        armor.box((.3, .4, .4), loc=(cx + s * 1.75, cy - .3, rz + .8), bevel=.03, seg=1)            # end heads
        a.part('Rangefinder_glass', 'Glass').box((.2, .04, .2), loc=(cx + s * 1.75, cy - .52, rz + .8), bevel=0)
    # Sandbags along the front edge, a generator set and a cable reel.
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(2):
        bag_run(bags, rng, (-3.8, -2.85), (0.2, -2.85), z0 + .13 + course * .24, half=course % 2 == 1)
    generator(a, (1.6, 2.55, z0), yaw=0, size=(2.0, 1.0, 1.2))
    reel = a.part('Cable_reel', 'Rubber')
    reel.cyl(.3, .5, loc=(-.2, 2.5, z0 + .38), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    for dx in (-.28, .28):
        steel.cyl(.4, .04, loc=(-.2 + dx, 2.5, z0 + .38), rot=ACROSS, seg=14, bevel=0)
    a.part('Cables', 'Rubber').tube([(-.2, 2.2, z0 + .1), (-.3, 1.7, z0 + .04), (-.1, 1.62, z0 + .6)], .04, seg=5)

    # Part_radar: pedestal and the dish spinning on `Radar`.
    rx, ry = 2.45, -.25
    pr = pv(a, 'Part_radar', (rx, ry, z0))
    pbody = a.part('Radar_pedestal', 'Armor', pr)
    pbody.cyl(.7, .3, loc=(0, 0, .15), seg=16, bevel=.03, bseg=1)
    pbody.cyl(.36, 1.1, loc=(0, 0, .8), seg=14, bevel=.03, bseg=1)
    a.part('Radar_ring', 'Steel', pr).cyl(.46, .08, loc=(0, 0, 1.38), seg=16, bevel=0)
    rr = pv(a, 'Radar', (0, 0, 1.42), 'Part_radar')
    rsteel, rarm = a.part('Radar_steel', 'Steel', rr), a.part('Radar_yoke', 'Armor', rr)
    rsteel.cyl(.44, .1, loc=(0, 0, .05), seg=16, bevel=.01, bseg=1)
    rarm.box((.9, .6, .5), loc=(0, .15, .35), bevel=.04, seg=1)
    for s in (-1, 1):
        rarm.limb((s * .38, .1, .5), (s * .5, .1, 1.35), .14, .2, bevel=.02)                          # yoke arms
    tilt = math.radians(25)
    dc = Vector((0, .05, 1.45))                                                                         # dish back
    _dish(a.part('Radar_dish', 'Medical', rr), tuple(dc), 1.7, 1.7, depth=.55, seg=18, tilt=tilt)
    rsteel.cyl(.06, 1.1, loc=(0, .05, 1.45), rot=ACROSS, seg=8, bevel=0)                             # elevation axis
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    focus = dc + axis * 1.45
    ring = []
    for k in range(4):
        u = math.pi / 4 + k * R90
        side = Vector((math.cos(u), 0, 0)) * 1.3
        up = Vector((0, math.sin(tilt), math.cos(tilt))) * math.sin(u) * 1.3
        ring.append(dc + axis * .5 + side + up)
    for q in ring:
        rsteel.limb(tuple(q), tuple(focus), .04, .04, bevel=0)                                        # feed struts
    rarm.cyl(.13, .3, loc=tuple(focus), rot=(R90 - tilt, 0, 0), seg=10, bevel=.02, bseg=1)             # feed horn
    rarm.box((.7, .5, .6), loc=tuple(dc - axis * .45 + Vector((0, 0, -.1))), rot=(-tilt, 0, 0), bevel=.03, seg=1)
    a.part('Radar_cable', 'Undercarriage', rr).tube([(.2, .4, .5), (.25, .55, .9), (.2, .45, 1.2)], .035, seg=5)

    # Part_antenna: guyed lattice mast behind the cabin.
    mx, my = -3.0, 2.45
    pa = pv(a, 'Part_antenna', (mx, my, z0))
    a.part('Mast_footing', 'Concrete', pa).box((1.1, 1.1, .2), loc=(0, 0, .08), bevel=.02, seg=1)
    lattice(a.part('Mast', 'Steel', pa), 0, 0, .15, 9.4, .42, .2, 6, leg=.13, brace=.035)
    head = a.part('Mast_head', 'Armor', pa)
    head.box((.5, .5, .3), loc=(0, 0, 9.5), bevel=.02, seg=1)
    dip = a.part('Dipoles', 'Steel', pa)
    dip.cyl(.04, 1.0, loc=(0, 0, 10.1), seg=6, bevel=0)
    for z in (9.8, 10.2):
        dip.cyl(.025, 1.6, loc=(0, 0, z), rot=ACROSS, seg=5, bevel=0)
        dip.cyl(.025, 1.6, loc=(0, 0, z), rot=(R90, 0, 0), seg=5, bevel=0)
    a.part('Obstruction_light', 'LavaGlow', pa).sphere(.08, loc=(0, 0, 10.65), seg=8, rings=5)
    _dish(a.part('Link_dish', 'Medical', pa), (.25, -.3, 8.2), .45, .45, depth=.16, seg=12, tilt=.1)
    head.box((.2, .3, .2), loc=(.2, -.12, 8.2), bevel=0)
    flood_head(a, (.3, -.35, 6.2), yaw=.5, tilt=.6, size=(.5, .26, .36), parent=pa)
    guys = a.part('Guy_wires', 'Steel', pa)
    for gx, gy in ((-.85, -.7), (.85, -.7), (-.7, .55), (.85, .6)):
        guys.tube([(0, 0, 8.0), (gx, gy, .1)], .012, seg=4)
        a.part('Guy_anchors', 'Steel', pa).box((.14, .14, .12), loc=(gx, gy, .06), bevel=0)


# ----------------------------------------------------------------------------- earth_borer
EB_ZC = 3.3                      # body axis height
EB_SEGMENTS = ((-5.8, -1.6), (-.9, 4.1), (4.8, 9.8))


def _profile_r(profile, z):
    """Radius of a (radius, z) lathe profile at z (linear between its points)."""
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(1e-6, z1 - z0)
    return profile[-1][0]


def _axial_plates(part, y0, y1, R, angles, width, t=.08, zc=EB_ZC):
    """Armour plates laid along a body of revolution about Y (radius R, axis at height zc) from y0 to y1, one at
    each angle (radians from the top, positive towards +X)."""
    for u in angles:
        loc = (math.sin(u) * (R + t / 2 - .02), (y0 + y1) / 2, zc + math.cos(u) * (R + t / 2 - .02))
        part.box((width, y1 - y0, t), loc=loc, rot=(0, u, 0), bevel=.02, seg=1)


def earth_borer(a):
    """"Earth Worm" boring machine (Soviet "Battle Mole" / tunnel-boring machine lineage), 22.9 x 5.3 m, 6.2 m: a
    long armoured body of three segments joined by ribbed rubber bellows, each segment a barrel of revolution
    under longitudinal Team armour plates with dark end bands, riding on its own pair of short track units
    under fenders. Big spoil pipes run along both flanks from the shield to the tail, clamped at every
    segment. At the front a shield collar with headlamps, the driver's vision blocks and hatch behind it,
    and the huge drill head: a stepped cone with three steel spiral flights studded with carbide teeth, a
    gauge ring of cutters round its base and a pilot bit. At the rear a tapered tail cap with the spoil
    conveyor chute and tail lights.

    Rig: the drill head spins on `Propeller` (the game spins Propeller* about the model's front-back axis,
    which is the drill's axis) at the drill base (0, -6.8, 3.3). Boss parts: `Part_drill` (the drill head
    and its spinner, origin at the drill base on the axis); `Part_gun` / `Part_gun.001`: 57 mm turrets on
    barbettes on the left front and right rear shoulders of the middle segment (`Mount_gun` / `Muzzle_gun`,
    `Mount_gun.001` / `Muzzle_gun.001`); `Part_engine`: the raised engine deck on the rear segment with its
    grilles, fans and four exhaust stacks."""
    _suffixed(a)
    zc = EB_ZC
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    team, dark = a.part('Hull', 'Team'), a.part('Chassis', 'Undercarriage')
    rubber = a.part('Bellows', 'Rubber')
    body = a.part('Body', 'Armor')
    bands = a.part('Bands', 'Undercarriage')
    # Segments, bellows and plates.
    for i, (y0, y1) in enumerate(EB_SEGMENTS):
        L = y1 - y0
        if i == 0:
            prof = [(2.45, 0), (2.4, .6), (2.27, 1.4), (2.24, 3.0), (2.1, L)]
        else:
            prof = [(2.1, 0), (2.22, .3), (2.25, L / 2), (2.22, L - .3), (2.1, L)]
        body.lathe(prof, loc=(0, y0, zc), rot=BACKWARD, seg=28)
        R = 2.25
        p0, p1 = (y0 + 1.4, y0 + 3.1) if i == 0 else (y0 + .45, y1 - .35)          # where the barrel is 2.25 m
        _axial_plates(team, p0, p1, R, [math.radians(d) for d in (-60, -40, -20, 0, 20, 40, 60)], .72)
        _axial_plates(armor, p0, p1, R, [math.radians(d) for d in (-112, -80, 80, 112)], .72)
        for yb in (y0 + .22, y1 - .15):
            _revolve(bands, [(_profile_r(prof, yb - y0) - .02, -.12), (_profile_r(prof, yb - y0) + .1, -.1),
                             (_profile_r(prof, yb - y0) + .1, .1), (_profile_r(prof, yb - y0) - .02, .12)],
                     (0, yb, zc), BACKWARD, 28)
        if i < 2:
            j0 = y1 - .1
            j1 = EB_SEGMENTS[i + 1][0] + .1
            n = 5
            pts = []
            for k in range(2 * n + 1):
                pts.append((2.08 if k % 2 else 1.92, (j1 - j0) * k / (2 * n)))
            rubber.lathe(pts, loc=(0, j0, zc), rot=BACKWARD, seg=24)
        # Track units under each segment, fenders over them.
        yc = (y0 + y1) / 2
        for s in (-1, 1):
            track_unit(a, s * 1.55, yc, L - .6, .85, 1.35, .42, .36, .6, .3, 5, s, pitch=.32, sprocket=-1)
            armor.box((1.25, L - .4, .1), loc=(s * 1.55, yc, 1.45), bevel=.02, seg=1)
            dark.box((.3, L - 1.0, .5), loc=(s * .95, yc, 1.3), bevel=.02, seg=1)                   # track frames
    # Spoil pipes along both flanks, clamped at every segment.
    pipe = a.part('Spoil_pipes', 'Armor')
    for s in (-1, 1):
        pipe.cyl(.32, 15.6, loc=(s * 2.45, 2.0, zc - .2), rot=BACKWARD, seg=14, bevel=.02, bseg=1)   # y -5.8 .. 9.8
        for y in (-4.6, -2.6, .5, 2.6, 6.0, 8.4):
            steel.cyl(.38, .2, loc=(s * 2.45, y, zc - .2), rot=BACKWARD, seg=14, bevel=0)
            dark.box((.3, .16, .3), loc=(s * 2.24, y, zc - .2), bevel=0)
        pipe.limb((s * 2.45, -5.8, zc - .2), (s * 2.2, -6.3, zc + .6), .5, .5, bevel=.03)            # intakes
    # Shield collar at the front, lamps, vision blocks and hatches on the front segment.
    armor.lathe([(2.35, 0), (2.7, .12), (2.7, 1.05), (2.45, 1.3)], loc=(0, -6.95, zc), rot=BACKWARD, seg=32)
    for k in range(12):
        u = k * TAU / 12 + TAU / 24
        steel.box((.24, .5, .16), loc=(math.sin(u) * 2.72, -6.4, zc + math.cos(u) * 2.72), rot=(0, u, 0), bevel=0)
    for s in (-1, 1):
        _headlamp(a, (s * 1.4, -6.2, zc + 2.45), r=.16)
        _headlamp(a, (s * 2.62, -6.2, zc + .9), r=.14, hood=False)
    _periscopes(a, [(x, -4.9, zc + 2.3, 0) for x in (-.4, 0, .4)])
    armor.box((1.4, .5, .18), loc=(0, -4.75, zc + 2.3), bevel=.03, seg=1)                          # vision block hood
    _hatch(a, .8, -3.6, zc + 2.31, .32)
    _hatch(a, -.8, -3.4, zc + 2.31, .3)
    _antenna(a, None, -1.4, -2.6, zc + 1.7, 1.2)
    # Tail cap, conveyor chute, tail lights, whips.
    body.lathe([(2.1, 0), (2.02, .3), (1.6, .8), (1.1, 1.0), (0, 1.02)], loc=(0, 9.8, zc), rot=BACKWARD, seg=28)
    chute = a.part('Conveyor', 'Hazard')
    chute.limb((0, 10.3, zc + .9), (0, 11.5, zc - .4), .9, .3, bevel=.03)
    for s in (-1, 1):
        steel.limb((s * .5, 10.2, zc + 1.0), (s * .5, 11.4, zc - .3), .1, .45, bevel=0)             # chute sides
        a.part('Tail_lamps', 'LavaGlow').box((.2, .05, .14), loc=(s * 1.2, 10.55, zc + 1.2), rot=(-.9, 0, 0), bevel=0)
    _whip(a, 1.1, 9.4, zc + 1.88, 1.6)
    _whip(a, -1.1, 9.4, zc + 1.88, 1.3)

    # Part_drill: the drill head spinning on `Propeller` at its base.
    pd = pv(a, 'Part_drill', (0, -6.8, zc))
    pr = a.pivot('Propeller', (0, 0, 0), pd)
    prof = [(2.55, -.3), (2.55, .35), (2.3, .6), (1.8, 1.6), (1.2, 2.8), (.62, 3.9), (.3, 4.4), (0, 4.75)]
    a.part('Drill_cone', 'Armor', pr).lathe(prof, rot=FORWARD, seg=28)
    _revolve(a.part('Drill_ring', 'SafetyStripe', pr), [(2.5, -.12), (2.74, -.12), (2.74, .3), (2.5, .3)], (0, 0, 0),
             FORWARD, 32)
    cut = a.part('Drill_cutters', 'Steel', pr)
    for k in range(18):
        u = k * TAU / 18
        cut.box((.22, .3, .22), loc=(math.cos(u) * 2.78, -.12, math.sin(u) * 2.78), rot=(0, -u, 0), bevel=0)
    flights = a.part('Drill_flights', 'Steel', pr)
    teeth = a.part('Drill_teeth', 'Charred', pr)
    for f in range(3):
        pts = []
        for k in range(34):
            z = .65 + (4.2 - .65) * k / 33
            ang = f * TAU / 3 + 1.15 * TAU * k / 33
            rr = _profile_r(prof, z) + .1
            pts.append((math.cos(ang) * rr, -z, math.sin(ang) * rr))
        flights.tube(pts, .13, seg=6)
        for k in range(2, 34, 4):
            x, y, z = pts[k]
            n = Vector((x, 0, z)).normalized()
            teeth.box((.2, .2, .2), loc=(x + n.x * .14, y, z + n.z * .14), rot=(0, math.atan2(x, z), 0), bevel=0)
    a.part('Drill_tip', 'Steel', pr).lathe([(.34, 4.3), (.24, 4.7), (0, 5.05)], rot=FORWARD, seg=12)

    # Part_gun / Part_gun.001: 57 mm turrets on barbettes on the middle segment's shoulders.
    for name, x, y in (('Part_gun', 1.3, -.2), ('Part_gun.001', -1.3, 3.2)):
        pg = pv(a, name, (x, y, zc + 2.33))
        tag = name[5:].replace('.', '_')
        a.part(f'Barbette_{tag}', 'Armor', pg).cyl(.72, 1.5, loc=(0, 0, -.75), seg=18, bevel=.03, bseg=1)
        a.part(f'Barbette_band_{tag}', 'SafetyStripe', pg).cyl(.74, .1, loc=(0, 0, -.12), seg=18, bevel=0)
        autocannon(a, name.replace('Part_', 'Mount_'), (0, 0, 0), parent=name, length=1.6, r=.07, size=(1.1, 1.2, .58))

    # Part_engine: raised engine deck on the rear segment.
    pe = pv(a, 'Part_engine', (0, 7.3, zc + 1.6))
    deck = a.part('Engine_deck', 'Team', pe)
    deck.box((2.6, 4.2, .85), loc=(0, 0, .425), bevel=.05, seg=1, taper=(.96, .98))
    grille = a.part('Engine_grilles', 'Undercarriage', pe)
    for y in (-1.2, .1):
        grille.grille(1.9, 1.0, loc=(0, y, .87), rot=(-R90, 0, 0), slats=6, depth=.06, thickness=.04)
    for x in (-.55, .55):
        a.part('Engine_fans', 'Rubber', pe).cyl(.42, .04, loc=(x, 1.35, .86), seg=14, bevel=0)
        a.part('Engine_fan_guards', 'Steel', pe).cyl(.46, .05, loc=(x, 1.35, .9), seg=14, bevel=0)
    es = a.part('Engine_stacks', 'Steel', pe)
    soot = a.part('Engine_soot', 'Charred', pe)
    for x in (-1.0, 1.0):
        for y in (1.2, 1.8):
            es.cyl(.13, 1.3, loc=(x, y, 1.3), seg=10, bevel=0)
            soot.cyl(.15, .12, loc=(x, y, 1.97), seg=10, bevel=0)
    a.part('Engine_armor', 'Armor', pe).box((2.8, .3, .5), loc=(0, -2.0, .55), bevel=.03, seg=1)   # front bulkhead


# ----------------------------------------------------------------------------- command_airship
CA_ENV_X, CA_ENV_Z = 7.8, 2.0            # envelope axes (x = +-7.8), 45 m long
CA_DECK, CA_KEEL = 2.2, -2.2             # the spine hull's deck and keel
CA_ENVELOPE = [(0, 0), (1.3, .6), (2.4, 1.8), (3.3, 3.8), (3.8, 6.5), (4.0, 10.0), (4.0, 28.0), (3.7, 33.0),
               (3.0, 37.5), (2.0, 41.0), (1.0, 43.6), (0, 45.0)]           # (radius, distance from the nose)


def _env_radius(y):
    """Envelope radius at y (the nose at y = -22.5)."""
    d = y + 22.5
    for (r0, d0), (r1, d1) in zip(CA_ENVELOPE, CA_ENVELOPE[1:]):
        if d0 <= d <= d1:
            return r0 + (r1 - r0) * (d - d0) / max(1e-6, d1 - d0)
    return 0.0


def _ca_drone(body, rotors, x, y, z):
    """Quad-rotor strike drone hanging nose-forward in a hangar at (x, y, z): an X frame, four motor pods with
    rotor discs and a warhead slung under the body."""
    body.box((.36, .56, .18), loc=(x, y, z), bevel=.03, seg=1)
    body.cyl(.09, .36, loc=(x, y - .12, z - .16), rot=FORWARD, seg=8, bevel=0)                     # warhead
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = x + sx * .42, y + sy * .42
            body.limb((x, y, z), (px, py, z + .02), .06, .05, bevel=0)
            rotors.cyl(.24, .02, loc=(px, py, z + .1), seg=10, bevel=0)


def _ca_plate(part, cx, y0, y1, a0, a1, out=.07, inn=.03, na=6):
    """Curved armour plate on the envelope whose axis runs along Y at (cx, CA_ENV_Z), from y0 to y1 and angles
    a0..a1 about the axis (0 = top, positive towards +X), standing `out` proud of the skin."""
    ys = [y0] + [d - 22.5 for _, d in CA_ENVELOPE if y0 + .05 < d - 22.5 < y1 - .05] + [y1]
    loops = []
    for y in ys:
        r = _env_radius(y)
        ang = [a0 + (a1 - a0) * i / (na - 1) for i in range(na)]
        outer = [(cx + (r + out) * math.sin(u), y, CA_ENV_Z + (r + out) * math.cos(u)) for u in ang]
        inner = [(cx + (r - inn) * math.sin(u), y, CA_ENV_Z + (r - inn) * math.cos(u)) for u in reversed(ang)]
        loops.append(outer + inner)
    part.loft(loops, bevel=.015, seg=1)


def _ca_nacelle(a, name, prop, x, y, z, k=1.18):
    """Engine nacelle `name` (a Part_engine empty at the nacelle's middle) on an outrigger from the envelope at
    (x, y, z), `k` times the base size: a streamlined Team pod with armour bands, a chin radiator, exhaust
    stubs, the pylon and a brace to the envelope, and a four-blade tractor propeller on `prop` at its nose
    (spins about Y)."""
    s = 1 if x > 0 else -1
    tag = name[5:].replace('.', '_')
    pe = pv(a, name, (x, y, z))
    a.part(f'Nacelle_{tag}', 'Team', pe).lathe([(r * k, zz * k) for r, zz in ((0, -2.55), (.45, -2.45), (.8, -2.0),
                                                (.95, -1.0), (.95, .8), (.7, 1.9), (.35, 2.5), (0, 2.65))],
                                               rot=BACKWARD, seg=16)
    band = a.part(f'Nacelle_bands_{tag}', 'Armor', pe)
    for yy in (-1.6, .2):
        _revolve(band, [(.93 * k, -.12), (1.0 * k, -.1), (1.0 * k, .1), (.93 * k, .12)], (0, yy * k, 0), BACKWARD, 16)
    band.box((.7 * k, 1.4 * k, .4 * k), loc=(0, -.9 * k, -.9 * k), bevel=.05, seg=1, taper=(.85, .9))  # radiator
    a.part(f'Nacelle_grille_{tag}', 'Undercarriage', pe).box((.56 * k, .05, .26 * k), loc=(0, -1.62 * k, -.92 * k),
                                                             bevel=0)
    steel = a.part(f'Nacelle_steel_{tag}', 'Steel', pe)
    for j in range(3):
        steel.cyl(.08, .3, loc=(s * .92 * k, (-.4 + j * .45) * k, .2 * k), rot=(0, s * R90, 0), seg=6, bevel=0)
    r = _env_radius(y)
    pyl = a.part(f'Pylon_{tag}', 'Armor', pe)
    pyl.limb((s * (CA_ENV_X + r * .96) - x, .2, CA_ENV_Z - z + .2), (0, .2, .7 * k), .5, 1.8, bevel=.04)
    low = CA_ENV_X + math.sqrt(max(.01, r * r - 1.6 ** 2)) * .98
    pyl.limb((s * low - x, .4, CA_ENV_Z - 1.6 - z), (0, .4, -.62 * k), .16, .16, bevel=0)             # brace
    pr = a.pivot(prop, (0, -2.72 * k, 0), pe)
    a.part(f'{prop}_hub', 'Steel', pr).lathe([(.4, .3), (.4, 0), (.26, -.35), (0, -.6)], rot=BACKWARD, seg=10)
    bl = a.part(f'{prop}_blades', 'Armor', pr)
    for j in range(4):
        _prop_blade(bl, math.pi / 4 + j * R90, .3, 1.95, .48, .26, .1, .035, .75, .3)


def _ca_hangar(a, name, muzzle, x):
    """Drone hangar bay `name` under the spine keel beside the centre line at x: an armoured box with hazard
    sills, both bottom doors hinged open, three drones on a rail and `muzzle` just below the opening."""
    tag = name[5:].replace('.', '_')
    yc, L, w, h, top = 3.0, 9.6, 2.3, 1.9, 1.5            # the walls rise into the hull up to its bilge knuckle
    ph = pv(a, name, (x, yc, CA_KEEL))
    box = a.part(f'Hangar_{tag}', 'Armor', ph)
    for s in (-1, 1):
        box.box((.12, L, h + top), loc=(s * (w / 2), 0, (top - h) / 2), bevel=.02, seg=1)
    for e in (-1, 1):
        box.box((w + .12, .12, h + top), loc=(0, e * L / 2, (top - h) / 2), bevel=.02, seg=1)
    a.part(f'Hangar_roof_{tag}', 'Undercarriage', ph).box((w, L, .06), loc=(0, 0, -.1), bevel=0)
    sill = a.part(f'Hangar_sills_{tag}', 'SafetyStripe', ph)
    for s in (-1, 1):
        sill.box((.16, L + .14, .12), loc=(s * w / 2, 0, -h + .1), bevel=0)
    for e in (-1, 1):
        sill.box((w + .16, .16, .12), loc=(0, e * L / 2, -h + .1), bevel=0)
    doors = a.part(f'Hangar_doors_{tag}', 'Team', ph)
    for s in (-1, 1):
        c = Vector((s * w / 2, 0, -h + .05)) + Vector((s * math.sin(.3), 0, -math.cos(.3))) * .6
        doors.box((.06, L - .2, 1.2), loc=tuple(c), rot=(0, -s * .3, 0), bevel=.01, seg=1)
    a.part(f'Hangar_rail_{tag}', 'Steel', ph).box((.12, L - .6, .1), loc=(0, 0, -.2), bevel=0)
    body, rotors = a.part(f'Drones_{tag}', 'Armor', ph), a.part(f'Drone_rotors_{tag}', 'Charred', ph)
    for k in range(3):
        _ca_drone(body, rotors, 0, -3.0 + k * 3.0, -.62)
        a.part(f'Drone_lights_{tag}', 'TeamGlow', ph).box((.1, .04, .05), loc=(0, -3.0 + k * 3.0 - .29, -.6), bevel=0)
        a.part(f'Hangar_rail_{tag}', 'Steel', ph).box((.05, .05, .36), loc=(0, -3.0 + k * 3.0, -.36), bevel=0)
    # Launch trapeze lowered through the opening with the next drone on it; the muzzle at the cradle's front.
    zl = -h - .15
    cradle = a.part(f'Launch_cradle_{tag}', 'Steel', ph)
    cradle.box((.3, 1.2, .1), loc=(0, -.9, zl), bevel=0)
    for yy in (-1.3, -.5):
        cradle.box((.06, .06, 1.5), loc=(0, yy, zl + .75), bevel=0)
    _ca_drone(body, rotors, 0, -.9, zl - .22)
    a.pivot(dotted(muzzle), (0, -1.5, zl), ph)


def command_airship(a):
    """Armoured command airship ("Sky Admiral"), 45.9 x 31.4 m, 17 m tall: a flying battleship. A dark armoured
    spine hull with a raked prow runs between two Team gas envelopes (belted with armour plates and bands)
    and carries the command: a three-tier bridge tower amidships with a glazed, lit command deck, bridge
    wings, searchlights and a radar mast on top; a gun turret on the bow deck and one on the stern deck; a
    command flag; railings and antennas. Girders tie the envelopes to the spine, a biplane-style tailplane
    joins their tails over the stern, each envelope has an upper and a lower fin. Four engine nacelles on
    outriggers from the envelopes' outer flanks turn tractor propellers; two drone hangar bays hang under the
    keel with their doors open. Origin at the spine hull's centre (it flies).

    Boss parts (and pivots): `Part_engine` (front left), `Part_engine.001` (front right), `Part_engine.002`
    (rear left), `Part_engine.003` (rear right), each with its `Propeller` / `Propeller_2` / `Propeller_3` /
    `Propeller_4`; `Part_hangar` (left bay, `Muzzle_door_l`) and `Part_hangar.001` (right bay,
    `Muzzle_door_r`); `Part_radar` (the mast and the spinning `Radar` array); `Part_gun` (bow turret,
    `Mount_gun` / `Muzzle_gun`) and `Part_gun.001` (stern turret, `Mount_gun.001` / `Muzzle_gun.001`)."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    team, dark = a.part('Envelopes', 'Team'), a.part('Undercarriage', 'Undercarriage')
    glow = a.part('Nav_lights', 'TeamGlow')
    # Envelopes with armour belts, bands, nose caps and a dark keel strip.
    for s in (-1, 1):
        ex = s * CA_ENV_X
        team.lathe([(r, d) for r, d in CA_ENVELOPE], loc=(ex, -22.5, CA_ENV_Z), rot=BACKWARD, seg=32)
        armor.lathe([(0, 0), (1.3, .6), (2.1, 1.5), (2.0, 1.62), (0, 1.62)], loc=(ex, -22.55, CA_ENV_Z), rot=BACKWARD,
                    seg=24)                                                                           # nose cap
        for y in (-16.0, -11.5, -7.0, -2.5, 2.0, 6.5, 11.0):
            r = _env_radius(y)
            _revolve(armor, [(r - .02, -.16), (r + .08, -.13), (r + .08, .13), (r - .02, .16)], (ex, y, CA_ENV_Z),
                     BACKWARD, 32)
        bands = (-16.0, -11.5, -7.0, -2.5, 2.0, 6.5, 11.0)
        for y0, y1 in zip(bands, bands[1:]):                                   # curved plates between the bands
            _ca_plate(armor, ex, y0 + .2, y1 - .2, -.32, .32)
            _ca_plate(armor, ex, y0 + .2, y1 - .2, s * .95, s * 1.62)
        dark.box((.5, 30.0, .1), loc=(ex, -2.0, CA_ENV_Z - 4.02), bevel=.02, seg=1)                     # keel strip
        glow.sphere(.14, loc=(ex, 22.55, CA_ENV_Z), seg=8, rings=5)                                    # tail light
        # Upper and lower fins.
        for up in (1, -1):
            fin = [(18.0, 0), (22.0, 0), (22.4, up * 3.6), (20.6, up * 3.8)]
            team.prism([(yy, CA_ENV_Z + up * (_env_radius(yy) - .3) + zz) for yy, zz in fin], .22, loc=(ex, 0, 0),
                       axis='X', bevel=.03, seg=1)
            armor.prism([(21.9, CA_ENV_Z + up * 1.4), (22.75, CA_ENV_Z + up * 1.4), (23.0, CA_ENV_Z + up * 3.6),
                         (22.35, CA_ENV_Z + up * 3.65)], .16, loc=(ex, 0, 0), axis='X', bevel=.02, seg=1)  # rudder
    # Tailplane joining both tails over the stern, with elevators; outboard stubs.
    tp = [(-12.4, 18.6), (12.4, 18.6), (12.4, 21.4), (-12.4, 21.4)]
    team.prism([(x, y) for x, y in tp], .26, loc=(0, 0, 3.0), axis='Z', bevel=.04, seg=1)
    armor.prism([(-12.2, 21.35), (12.2, 21.35), (12.2, 22.3), (-12.2, 22.3)], .16, loc=(0, 0, 3.0), axis='Z',
                bevel=.02, seg=1)
    for s in (-1, 1):
        glow.box((.1, .5, .12), loc=(s * 12.45, 20.0, 3.0), bevel=0)
    # Spine hull: raked prow, straight hull, tapering stern.
    def sec(y, k=1.0, top=CA_DECK):
        w, wb = 2.6 * k, 1.2 * k
        return [(-wb, y, CA_KEEL * (.6 + .4 * k)), (wb, y, CA_KEEL * (.6 + .4 * k)), (w, y, -.6), (w, y, top),
                (-w, y, top), (-w, y, -.6)]
    hull = a.part('Spine', 'Armor')
    hull.loft([sec(-21.8, .12, CA_DECK + .6), sec(-20.0, .5, CA_DECK + .35), sec(-17.5, .92), sec(-15.5, 1.0),
               sec(15.0, 1.0), sec(17.5, .7, CA_DECK - .2), sec(18.6, .35, CA_DECK - .5)], bevel=.06, seg=2)
    deck = a.part('Deck', 'Undercarriage')
    deck.box((4.9, 32.0, .04), loc=(0, -.5, CA_DECK + .02), bevel=0)
    stripe = a.part('Deck_lines', 'Hazard')
    for s in (-1, 1):
        stripe.box((.1, 32.0, .02), loc=(s * 2.2, -.5, CA_DECK + .045), bevel=0)
    _plate_bolts(steel, 2.63, [y for y in range(-14, 15, 2)], .8, r=.05, h=.05)
    _plate_bolts(steel, -2.63, [y for y in range(-14, 15, 2)], .8, r=.05, h=.05)
    for s in (-1, 1):
        armor.box((.1, 29.0, .7), loc=(s * 2.62, 0, 1.2), bevel=.02, seg=1)                              # side belt
        a.part('Portholes', 'Lamp').bolts([(s * 2.68, y, 0.0) for y in (-13, -11, -9, 9, 11, 13)], r=.12, h=.04,
                                          rot=(0, R90, 0), seg=8, bevel=0)
        # Girders to the envelopes, with diagonal braces.
        for y in (-14.0, -3.0, 8.0, 15.0):
            r = _env_radius(y)
            inner = CA_ENV_X - math.sqrt(max(.01, r * r - (1.6 - CA_ENV_Z) ** 2))
            x0, x1 = 2.45, inner + .45
            armor.box((x1 - x0, .5, .6), loc=(s * (x0 + x1) / 2, y, 1.6), bevel=.03, seg=1)
            low = CA_ENV_X - math.sqrt(max(.01, r * r - (.9 - CA_ENV_Z) ** 2))
            steel.limb((s * 2.5, y, -.4), (s * (low + .3), y, .9), .2, .2, bevel=0)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        _railing(rail, [(s * 2.48, -16.5, CA_DECK), (s * 2.48, -8.0, CA_DECK)], h=.8, every=1.6)
        _railing(rail, [(s * 2.48, 0.0, CA_DECK), (s * 2.48, 15.0, CA_DECK)], h=.8, every=1.6)
    for s in (-1, 1):                                                                                      # prow stars
        a.part('Emblem', 'Gilded').cyl(.34, .08, loc=(s * 1.7, -19.2, 1.2), rot=(0, R90, -s * .41), seg=5, bevel=0)
    # Bridge tower amidships: three tiers, the glazed command deck, bridge wings, searchlights.
    br = a.part('Bridge', 'Armor')
    br.box((4.2, 6.0, 1.6), loc=(0, -4.0, CA_DECK + .8), bevel=.06, seg=1, taper=(.95, .95))
    br.box((3.6, 4.8, 1.5), loc=(0, -3.8, CA_DECK + 2.3), bevel=.06, seg=1, taper=(.95, .95))
    a.part('Bridge_band', 'Team').box((3.7, 4.9, .3), loc=(0, -3.8, CA_DECK + 1.8), bevel=.02, seg=1)
    cd = a.part('Command_deck', 'Armor')
    cd.box((3.2, 3.6, 1.3), loc=(0, -3.6, CA_DECK + 3.7), bevel=.05, seg=1, taper=(.92, .92))
    lit = a.part('Command_windows', 'Lamp')
    for x in (-1.0, 0, 1.0):
        lit.box((.8, .06, .5), loc=(x, -5.43, CA_DECK + 3.75), rot=(-.1, 0, 0), bevel=0)
    for s in (-1, 1):
        lit.box((.06, 2.6, .5), loc=(s * 1.62, -3.6, CA_DECK + 3.75), rot=(0, s * .1, 0), bevel=0)
        armor.box((1.2, 1.0, .12), loc=(s * 2.2, -5.2, CA_DECK + 3.2), bevel=.02, seg=1)                  # bridge wings
        steel.box((.06, .9, .7), loc=(s * 2.75, -5.2, CA_DECK + 3.55), bevel=0)
        flood_head(a, (s * 2.3, -5.5, CA_DECK + 3.55), yaw=s * .3, tilt=.25, size=(.46, .26, .34))
    armor.box((3.5, 3.9, .12), loc=(0, -3.6, CA_DECK + 4.4), bevel=.03, seg=1)                             # roof
    for x, y, h in ((-1.5, -1.9, 2.0), (1.5, -1.9, 1.6)):
        _antenna(a, None, x, y, CA_DECK + 4.46, h)
    # Command flag on a staff at the stern.
    flag(a, 0, 16.0, CA_DECK - .3, 4.2, w=2.4, h=1.4, phase=.6, yaw=R90)

    # Part_radar: mast and the spinning bedspring array on the bridge roof.
    prd = pv(a, 'Part_radar', (0, -3.2, CA_DECK + 4.46))
    mast = a.part('Radar_mast', 'Steel', prd)
    lattice(mast, 0, 0, 0, 1.6, .5, .3, 2, leg=.13, brace=.035)
    a.part('Radar_platform', 'Armor', prd).box((1.1, 1.1, .14), loc=(0, 0, 1.65), bevel=.02, seg=1)
    rp = pv(a, 'Radar', (0, 0, 1.72), 'Part_radar')
    a.part('Radar_turntable', 'Steel', rp).cyl(.36, .12, loc=(0, 0, .06), seg=14, bevel=.01, bseg=1)
    a.part('Radar_post', 'Armor', rp).box((.3, .3, .8), loc=(0, 0, .5), bevel=.02, seg=1)
    arr = a.part('Radar_array', 'Armor', rp)
    arr.box((4.0, .16, 1.5), loc=(0, -.1, 1.55), rot=(-.18, 0, 0), bevel=.03, seg=1)
    grid = a.part('Radar_grid', 'Medical', rp)
    for k in range(9):
        grid.box((.04, .06, 1.4), loc=(-1.8 + k * .45, -.21, 1.56), rot=(-.18, 0, 0), bevel=0)
    for k in range(4):
        grid.box((3.9, .06, .04), loc=(0, -.2 - (k - 1.5) * .06, 1.0 + k * .37), rot=(-.18, 0, 0), bevel=0)
    a.part('Radar_iff', 'Undercarriage', rp).box((3.2, .12, .2), loc=(0, -.02, 2.42), bevel=0)

    # Part_gun (bow) and Part_gun.001 (stern): 57 mm turrets on barbettes on the centre line.
    for name, y in (('Part_gun', -13.2), ('Part_gun.001', 10.2)):
        pg = pv(a, name, (0, y, CA_DECK + .8))
        tag = name[5:].replace('.', '_')
        a.part(f'Barbette_{tag}', 'Armor', pg).cyl(.95, .9, loc=(0, 0, -.44), seg=20, bevel=.04, bseg=1)
        a.part(f'Barbette_band_{tag}', 'SafetyStripe', pg).cyl(.97, .12, loc=(0, 0, -.2), seg=20, bevel=0)
        autocannon(a, name.replace('Part_', 'Mount_'), (0, 0, 0), parent=name, length=2.4, r=.08, size=(1.4, 1.5, .64))

    # Engines and hangars.
    for name, prop, x, y in (('Part_engine', 'Propeller', 14.3, -9.0), ('Part_engine.001', 'Propeller_2', -14.3, -9.0),
                             ('Part_engine.002', 'Propeller_3', 14.3, 8.0),
                             ('Part_engine.003', 'Propeller_4', -14.3, 8.0)):
        _ca_nacelle(a, name, prop, x, y, 1.0)
    _ca_hangar(a, 'Part_hangar', 'Muzzle_door_l', 1.3)
    _ca_hangar(a, 'Part_hangar.001', 'Muzzle_door_r', -1.3)
    dark.box((.4, 10.0, .3), loc=(0, 3.0, CA_KEEL - .1), bevel=0)                                      # keel between bays


# ----------------------------------------------------------------------------- landing_hovercraft
def ciws(a, mount, loc, parent=None, length=1.7):
    """Six-barrel 30 mm close-in weapon system (AK-630 lineage) on its own yaw pivot `mount` at loc (relative to
    `parent`): a ring on the parent, a squat Team drum with a domed roof, the cradle, a slim barrel cluster
    (one bundle, so every round leaves from its axis) in a cooling shroud with a muzzle clamp, and a sensor
    box on the roof. The muzzle sits at the cluster's tip. Returns the pivot key."""
    key, mkey, tag = _slot_names(mount)
    pk = dotted(parent) if parent else None
    a.part(f'CIWS_ring_{tag}', 'Armor', pk).cyl(.82, .12, loc=_v(loc, dz=.04), seg=18, bevel=.02, bseg=1)
    m = a.pivot(key, loc, pk)
    body = a.part(f'CIWS_body_{tag}', 'Team', m)
    body.cyl(.74, .62, loc=(0, .05, .36), seg=18, bevel=.04, bseg=1)
    body.sphere((.74, .74, .34), loc=(0, .05, .66), seg=18, rings=6, cut=0)
    arm = a.part(f'CIWS_armor_{tag}', 'Armor', m)
    zb = .62
    arm.box((.56, .7, .52), loc=(0, -.62, zb), bevel=.04, seg=1)                                   # cradle
    arm.cyl(.2, .5, loc=(0, -1.1, zb), rot=FORWARD, seg=12, bevel=.02, bseg=1)                     # shroud
    tip = -.97 - length
    a.part(f'CIWS_barrels_{tag}', 'Steel', m).cyl(.13, -1.2 - tip, loc=(0, (-1.2 + tip) / 2, zb), rot=FORWARD, seg=12,
                                                 bevel=0)
    dark = a.part(f'CIWS_dark_{tag}', 'Undercarriage', m)
    dark.cyl(.16, .1, loc=(0, tip + .45, zb), rot=FORWARD, seg=12, bevel=0)                        # muzzle clamp
    dark.cyl(.15, .12, loc=(0, tip + .06, zb), rot=FORWARD, seg=12, bevel=0)
    a.part(f'CIWS_bores_{tag}', 'Charred', m).cyl(.1, .02, loc=(0, tip + .005, zb), rot=FORWARD, seg=10, bevel=0)
    arm.box((.3, .3, .22), loc=(.3, .2, 1.02), bevel=.03, seg=1)                                     # sensor
    a.part(f'CIWS_glass_{tag}', 'Glass', m).box((.18, .02, .1), loc=(.3, .045, 1.03), bevel=0)
    a.pivot(mkey, (0, tip, zb), m)
    return m


def _rounded_rect(hx, hy, r, n=6):
    """Counter-clockwise outline of a rectangle (half sizes hx, hy) with corner radius r, n points per corner."""
    pts = []
    for cx, cy, a0 in ((hx - r, -hy + r, -R90), (hx - r, hy - r, 0.0), (-hx + r, hy - r, R90), (-hx + r, -hy + r, math.pi)):
        for k in range(n):
            u = a0 + R90 * k / (n - 1)
            pts.append((cx + r * math.cos(u), cy + r * math.sin(u)))
    return pts


def landing_hovercraft(a):
    """Air-cushion landing craft (LCAC / Zubr lineage), 28.3 x 16 m, 9.2 m to the mast top: a buoyancy hull
    riding on a black bag skirt with fingers round its foot; an open cargo deck the full length between two
    Team side structures (hazard lines and chevrons, tie-down rings, a raised stern ramp); on the side
    structures the turbine intakes and exhausts, life-raft canisters along their outer walls, handrails, and
    on the right front the raised control cabin with a mast (radar dome, nav lights). Navigation lights at the
    corners.

    Boss parts: `Part_fan` (left) and `Part_fan.001` (right): the twin shrouded pusher propellers at the stern
    on pylons, each with its `Propeller` / `Propeller_2`, stators and twin rudders, origin at the duct's
    middle; `Part_ramp`: the lowered bow ramp, hinged at the deck's bow sill, with `Muzzle_ramp` at its foot
    where vehicles drive off; `Part_gun` (left front) and `Part_gun.001` (right, behind the cabin): six-barrel
    CIWS on `Mount_gun` / `Mount_gun.001` (`Muzzle_gun`, `Muzzle_gun.001`)."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    team, dark = a.part('Side_structures', 'Team'), a.part('Undercarriage', 'Undercarriage')
    # Skirt: a bag round the hull bulging out, fingers along its foot.
    skirt = a.part('Skirt', 'Rubber')
    rings = [(7.25, 12.85, 2.9, .02), (7.7, 13.3, 3.3, .35), (7.95, 13.55, 3.5, 1.05), (7.55, 13.15, 3.1, 1.7),
             (6.75, 12.35, 2.4, 1.95)]
    skirt.loft([[(x, y, z) for x, y in _rounded_rect(hx, hy, r, 6)] for hx, hy, r, z in rings], bevel=0)
    fingers = a.part('Skirt_fingers', 'Charred')
    outline = _rounded_rect(7.5, 13.1, 3.2, 6)
    per = 0.0
    segs = []
    for p, q in zip(outline, outline[1:] + outline[:1]):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        segs.append((p, q, L, per))
        per += L
    n = int(per / .75)
    for k in range(n):
        d = (k + .5) * per / n
        p, q, L, s0 = next(sg for sg in segs if sg[3] <= d < sg[3] + sg[2])
        t = (d - s0) / L
        x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        fingers.box((.5, .14, .42), loc=(x, y, .22), rot=(0, 0, ang), bevel=0)
    # Hull, cargo deck and its markings.
    hull = a.part('Hull', 'Armor')
    hull.box((13.8, 25.0, 1.0), loc=(0, 0, 1.5), bevel=.08, seg=1)                                     # z 1 .. 2
    deck = a.part('Cargo_deck', 'Undercarriage')
    deck.box((7.4, 25.0, .06), loc=(0, 0, 2.02), bevel=0)
    mark = a.part('Deck_markings', 'Hazard')
    for s in (-1, 1):
        mark.box((.14, 24.0, .02), loc=(s * 3.35, 0, 2.06), bevel=0)
    for k in range(3):                                                                                  # chevrons
        for s in (-1, 1):
            mark.box((1.6, .2, .02), loc=(s * .7, -10.0 + k * 1.2, 2.06), rot=(0, 0, s * .5), bevel=0)
    rings_ = a.part('Tie_downs', 'Steel')
    for x in (-2.4, -.8, .8, 2.4):
        for y in (-8.0, -4.0, 0.0, 4.0, 8.0):
            rings_.cyl(.08, .04, loc=(x, y, 2.06), seg=6, bevel=0)
    # Side structures.
    for s in (-1, 1):
        team.box((3.0, 20.5, 2.3), loc=(s * 5.3, -.25, 3.15), bevel=.07, seg=1, taper=(.96, .98))     # z 2 .. 4.3
        armor.prism([(-11.6, 2.0), (-11.6, 2.6), (-10.6, 4.25), (-10.3, 4.25), (-10.3, 2.0)], 3.0, loc=(s * 5.3, 0, 0),
                    axis='X', bevel=.05, seg=1)                                                          # sloped bows
        grille = a.part('Intakes', 'Undercarriage')
        for y in (-.8, 2.2, 5.2):
            armor.box((2.0, 2.2, .4), loc=(s * 5.3, y, 4.45), bevel=.04, seg=1)
            grille.grille(1.7, 1.8, loc=(s * 5.3, y, 4.66), rot=(-R90, 0, 0), slats=6, depth=.05, thickness=.04)
        for y in (7.2, 8.4):                                                                             # exhausts
            dark.box((1.2, .9, .3), loc=(s * 5.1, y, 4.42), rot=(.4, 0, 0), bevel=.02, seg=1)
            a.part('Soot', 'Charred').box((1.0, .05, .22), loc=(s * 5.1, y + .42, 4.56), rot=(.4, 0, 0), bevel=0)
        # Life-raft canisters in racks along the outer wall.
        raft = a.part('Life_rafts', 'Medical')
        for y in (-7.0, -5.4, -3.8, 3.8, 5.4):
            raft.cyl(.3, 1.2, loc=(s * 7.05, y, 3.55), rot=FORWARD, seg=10, bevel=.03, bseg=1)
            steel.box((.1, .08, .7), loc=(s * 6.84, y, 3.4), bevel=0)
        # Handrails round the side-structure roofs, nav lights at the corners.
        _railing(a.part('Railings', 'Steel'), [(s * 6.7, -1.2, 4.3), (s * 6.7, 9.6, 4.3)], h=.8, every=1.8)
        a.part('Nav_green' if s < 0 else 'Nav_red', 'SignalGreen' if s < 0 else 'LavaGlow').box(
            (.12, .24, .14), loc=(s * 6.85, -9.8, 4.2), bevel=0)
        a.part('Stern_lights', 'Lamp').box((.2, .06, .14), loc=(s * 6.0, 10.02, 3.9), bevel=0)
    # Rub rail round the hull, crew doors and hatches on the inner walls, bollards on the roofs.
    rub = a.part('Rub_rail', 'Armor')
    for s in (-1, 1):
        rub.box((.14, 25.2, .16), loc=(s * 6.95, 0, 1.92), bevel=.02, seg=1)
        for y in (-5.0, 3.0):
            fbox(armor, '-x' if s > 0 else '+x', (s * 3.8, y, 3.0), (.9, .06, 1.8), out=.02, bevel=.012)
            fbox(steel, '-x' if s > 0 else '+x', (s * 3.8, y + .3, 3.0), (.06, .06, .2), out=.06)
        for y in (8.9,):
            steel.cyl(.12, .3, loc=(s * 6.2, y, 4.45), seg=8, bevel=0)
            steel.cyl(.18, .05, loc=(s * 6.2, y, 4.62), seg=8, bevel=0)
    for e in (-1, 1):
        rub.box((13.6, .14, .16), loc=(0, e * 12.55, 1.92), bevel=.02, seg=1)
    # Stern ramp (raised) with hazard edges, bow sill.
    armor.box((6.8, .2, 2.0), loc=(0, 12.45, 3.0), rot=(-.12, 0, 0), bevel=.03, seg=1)
    for s in (-1, 1):
        a.part('Ramp_edges', 'SafetyStripe').box((.14, .24, 2.0), loc=(s * 3.35, 12.46, 3.0), rot=(-.12, 0, 0), bevel=0)
    armor.box((7.4, .5, .4), loc=(0, -12.35, 2.15), bevel=.03, seg=1)                                 # bow sill
    # Control cabin on the right front with its mast.
    cab = a.part('Cabin', 'Team')
    cab.box((2.8, 2.8, 1.5), loc=(-5.3, -8.8, 5.05), bevel=.06, seg=1, taper=(.94, .94))
    glass = a.part('Cabin_glass', 'Glass')
    glass.box((2.2, .06, .5), loc=(-5.3, -10.18, 5.2), rot=(.12, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.06, 1.8, .45), loc=(-5.3 + s * 1.36, -8.8, 5.2), rot=(0, s * -.06, 0), bevel=0)
    armor.box((3.0, 3.0, .12), loc=(-5.3, -8.8, 5.85), bevel=.03, seg=1)
    steel.cyl(.1, 2.4, loc=(-5.3, -8.6, 7.1), seg=8, bevel=0)                                           # mast
    steel.box((1.4, .1, .1), loc=(-5.3, -8.6, 7.6), bevel=0)
    a.part('Radar_dome', 'Medical').sphere(.42, loc=(-5.3, -8.6, 8.55), seg=14, rings=8)
    a.part('Mast_lights', 'Lamp').sphere(.07, loc=(-5.3, -8.6, 9.0), seg=6, rings=4)
    for s in (-1, 1):
        a.part('Mast_lights', 'Lamp').sphere(.06, loc=(-5.3 + s * .7, -8.6, 7.66), seg=6, rings=4)
    _antenna(a, None, -4.2, -7.6, 5.9, 1.4)

    # Part_ramp: the lowered bow ramp from the sill to the ground.
    hinge = Vector((0, -12.5, 2.3))
    foot = Vector((0, -15.6, .05))
    pr = pv(a, 'Part_ramp', tuple(hinge))
    d = (foot - hinge)
    Lr = d.length
    tilt = math.atan2(-d.z, -d.y)                                                                        # down-slope
    ramp = a.part('Ramp', 'Armor', pr)
    mid = d / 2
    ramp.box((6.8, Lr, .2), loc=tuple(mid), rot=(tilt, 0, 0), bevel=.03, seg=1)
    ribs = a.part('Ramp_ribs', 'Undercarriage', pr)
    for k in range(9):
        c = d * ((k + .5) / 9) + Vector((0, 0, .1 / math.cos(tilt)))
        ribs.box((6.2, .1, .06), loc=tuple(c), rot=(tilt, 0, 0), bevel=0)
    edge = a.part('Ramp_edges_bow', 'SafetyStripe', pr)
    for s in (-1, 1):
        edge.box((.2, Lr, .5), loc=tuple(mid + Vector((s * 3.3, 0, .2))), rot=(tilt, 0, 0), bevel=.02, seg=1)
    steel_r = a.part('Ramp_steel', 'Steel', pr)
    steel_r.cyl(.14, 7.0, loc=(0, 0, 0), rot=ACROSS, seg=10, bevel=0)                                    # hinge pin
    steel_r.box((6.8, .2, .08), loc=tuple(d + Vector((0, .05, .05))), bevel=0)                           # toe plate
    a.pivot('Muzzle_ramp', tuple(d + Vector((0, -.06, .05))), pr)

    # Part_fan / Part_fan.001: the shrouded pusher propellers on pylons at the stern.
    for name, prop, x in (('Part_fan', 'Propeller', 5.3), ('Part_fan.001', 'Propeller_2', -5.3)):
        tag = name[5:].replace('.', '_')
        pf = pv(a, name, (x, 10.9, 6.55))
        _revolve(a.part(f'Duct_{tag}', 'Team', pf), [(2.02, -.8), (2.32, -.7), (2.32, .7), (2.02, .8)], (0, 0, 0),
                 BACKWARD, 28)
        _revolve(a.part(f'Duct_band_{tag}', 'Hazard', pf), [(2.3, -.1), (2.36, -.1), (2.36, .1), (2.3, .1)],
                 (0, -.3, 0), BACKWARD, 28)
        fa = a.part(f'Fan_armor_{tag}', 'Armor', pf)
        fa.box((.9, 1.5, 1.2), loc=(0, 0, -2.6), bevel=.04, seg=1)                                        # pylon
        fa.box((.3, .8, .6), loc=(0, .9, -2.1), bevel=.02, seg=1)
        st = a.part(f'Fan_stators_{tag}', 'Steel', pf)
        for k in range(4):
            u = math.pi / 4 + k * R90
            st.box((1.9, .1, .08), loc=(math.cos(u) * 1.05, .55, math.sin(u) * 1.05), rot=(0, -u, 0), bevel=0)
        st.cyl(.36, .9, loc=(0, .45, 0), rot=BACKWARD, seg=12, bevel=.03, bseg=1)                          # gearbox
        for dx in (-.8, .8):
            fa.box((.12, 1.0, 3.4), loc=(dx, 1.5, 0), bevel=.02, seg=1)                                    # rudders
        fa.box((2.0, .14, .14), loc=(0, 1.2, 1.75), bevel=0)
        fa.box((2.0, .14, .14), loc=(0, 1.2, -1.75), bevel=0)
        pp = a.pivot(prop, (0, -.1, 0), pf)
        a.part(f'{prop}_hub', 'Steel', pp).lathe([(.3, .3), (.3, 0), (.18, -.25), (0, -.4)], rot=BACKWARD, seg=10)
        bl = a.part(f'{prop}_blades', 'Armor', pp)
        for k in range(5):
            _prop_blade(bl, k * TAU / 5, .28, 1.95, .5, .34, .09, .03, .8, .35)

    # Part_gun (left front) / Part_gun.001 (right, behind the cabin): CIWS on the side-structure roofs.
    for name, x, y in (('Part_gun', 5.3, -6.4), ('Part_gun.001', -5.3, -3.0)):
        pv(a, name, (x, y, 4.3))
        ciws(a, name.replace('Part_', 'Mount_'), (0, 0, 0), parent=name)


# ----------------------------------------------------------------------------- supreme_command
SC_AXLES = (-4.6, -2.9, 2.5, 4.2)


def supreme_command(a):
    """"Supreme Commander" super-heavy command vehicle (MZKT-7930 chassis / armoured mobile headquarters lineage),
    14.4 x 4.2 m, 5.6 m roof, 11.2 m to the mast head: four axles of 1.9 m tyres in two pairs, a wide faceted
    armoured cab with three thick windscreens, a VIP light bar with blue escort lights, a bull bar, headlights,
    a gilded star on the nose and two Team pennants on staffs at the front corners; behind it the two-deck
    armoured command citadel: a Team lower module with bolted plates, a side door and ladders, and on it the
    war room with a lit window band under armoured louvres all round; a generator at the rear with its
    exhaust, a rear door and steps. Deliberately light armament: two small remote machine guns.

    Boss parts: `Part_antenna` (origin at the mast foot on the rear roof) holds the command antenna farm: the
    raised telescopic mast with a log-periodic array and a crossed-dipole head, the SATCOM radome on the war
    room, two link dishes and four whips; `Part_mg` / `Part_mg.001`: remote machine guns on the war room's front
    corners (left, right) on `Mount_mg` / `Mount_mg.001` with `Muzzle_mg` / `Muzzle_mg.001`."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, team = a.part('Chassis', 'Undercarriage'), a.part('Citadel', 'Team')
    for y in SC_AXLES:
        for s in (-1, 1):
            _wheel(a, s * 1.62, y, .95, .7, seg=18)
            dark.box((.5, .36, .36), loc=(s * 1.1, y, .95), bevel=.03, seg=1)                          # hub carriers
        dark.box((2.0, .3, .26), loc=(0, y, .95), bevel=.02, seg=1)                                     # axles
    dark.box((1.4, 13.6, .6), loc=(0, 0, 1.3), bevel=.04, seg=1)                                         # frame
    for s in (-1, 1):
        for y0, y1 in ((-5.75, -1.75), (1.35, 5.35)):                                                   # mudguards
            armor.box((.9, y1 - y0, .08), loc=(s * 1.62, (y0 + y1) / 2, 2.0), bevel=.02, seg=1)
            armor.box((.9, .08, .5), loc=(s * 1.62, y0 - .02, 1.78), rot=(-.4, 0, 0), bevel=0)
            armor.box((.9, .08, .5), loc=(s * 1.62, y1 + .02, 1.78), rot=(.4, 0, 0), bevel=0)
        team.box((.12, 2.9, .95), loc=(s * 1.98, -.2, 1.5), bevel=.02, seg=1)                            # skirts
        _plate_bolts(steel, s * 2.05, (-1.3, -.2, .9), 1.8, r=.03, h=.03)
    # Cab: faceted, raked front with three armoured windscreens.
    cab = a.part('Cab', 'Armor')
    prof = [(-7.15, 2.0), (-7.35, 2.55), (-6.45, 3.78), (-4.2, 3.95), (-4.2, 2.0)]
    cab.prism(prof, 4.16, axis='X', bevel=.06, seg=1)
    team.box((4.2, 1.1, .5), loc=(0, -4.75, 3.72), bevel=.03, seg=1)                                     # cab roof band
    G0, G1 = (-7.35, 2.55), (-6.45, 3.78)
    wr = _glacis(G0, G1, 0, 0)[2]
    glass, frame = a.part('Windscreens', 'Glass'), a.part('Screen_frames', 'Armor')
    for x in (-1.3, 0, 1.3):
        gy, gz, _ = _glacis(G0, G1, .55, .02)
        frame.box((1.2, .9, .08), loc=(x, gy, gz), rot=(wr, 0, 0), bevel=.02, seg=1)
        gy, gz, _ = _glacis(G0, G1, .55, .065)
        glass.box((1.0, .7, .04), loc=(x, gy, gz), rot=(wr, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.05, 1.2, .5), loc=(s * 2.09, -5.4, 3.2), bevel=0)                                    # side windows
        frame.box((.06, 1.4, .1), loc=(s * 2.1, -5.4, 3.5), bevel=0)
        _headlight(a, s * 1.55, -7.3, 2.35, guard=True)
        steel.limb((s * 2.08, -6.0, 3.2), (s * 2.4, -6.2, 3.3), .05, .05, bevel=0)
        armor.box((.1, .22, .34), loc=(s * 2.44, -6.2, 3.2), bevel=.02, seg=1)                           # mirrors
        flag(a, s * 1.9, -6.95, 3.3, 1.7, w=.7, h=.45, phase=s * .7, yaw=R90)                            # pennants
    steel.box((4.0, .16, .5), loc=(0, -7.5, 1.55), bevel=.03, seg=1)                                     # bull bar
    for x in (-1.4, -.5, .5, 1.4):
        steel.box((.1, .12, .8), loc=(x, -7.46, 1.9), bevel=0)
    sy, sz, _ = _glacis(G0, G1, .1, .03)
    a.part('Emblem', 'Gilded').cyl(.3, .06, loc=(0, sy, sz), rot=(wr, 0, 0), seg=5, bevel=0)             # nose star
    # VIP light bar on the cab roof.
    armor.box((2.6, .3, .14), loc=(0, -5.9, 3.93), bevel=.02, seg=1)
    for x in (-1.1, -.7, .7, 1.1):
        a.part('Escort_lights', 'Energy').box((.28, .24, .1), loc=(x, -5.9, 4.03), bevel=0)
    a.part('Light_bar_lamps', 'Lamp').box((.5, .24, .1), loc=(0, -5.9, 4.03), bevel=0)
    for s in (-1, 1):
        _whip(a, s * 1.9, -4.5, 3.95, 1.6)
    # Citadel: the lower module with plates, door, ladders; the war room with its window band.
    team.box((4.1, 11.1, 2.1), loc=(0, 1.25, 3.05), bevel=.07, seg=1)                                    # y -4.3 .. 6.8
    for s in (-1, 1):
        for y0, y1 in ((-3.9, -1.5), (-1.3, 1.3), (1.5, 3.9), (4.1, 6.4)):
            armor.box((.06, y1 - y0, .7), loc=(s * 2.06, (y0 + y1) / 2, 2.55), bevel=.012, seg=1)
            _plate_bolts(steel, s * 2.1, (y0 + .15, y1 - .15), 2.8, r=.03, h=.03)
        _periscopes(a, [(s * 2.04, y, 3.55, s * R90) for y in (-2.6, .1, 2.8)])
    fbox(armor, '-x', (-2.05, 5.2, 2.9), (.9, .06, 1.7), out=.02, bevel=.012)                            # side door
    for k in range(3):
        steel.box((.5, .8, .05), loc=(-2.3, 5.2, .7 + k * .45), bevel=0)                                 # door steps
    ladder(a.part('Ladders', 'Steel'), (-1.4, 6.95, .7), 4.3, 0, width=.44, step=.34, rung=.03)
    wr_ = a.part('War_room', 'Team')
    wr_.box((3.5, 6.6, 1.4), loc=(0, -.1, 4.8), bevel=.06, seg=1, taper=(.95, .96))                     # y -3.4 .. 3.2
    lit, louv = a.part('War_room_windows', 'Lamp'), a.part('Louvres', 'Armor')
    for s in (-1, 1):
        for y in (-2.4, -.8, .8, 2.4):
            lit.box((.05, 1.2, .38), loc=(s * 1.72, y, 4.8), bevel=0)
            for dz in (-.1, .1):
                louv.box((.1, 1.3, .05), loc=(s * 1.76, y, 4.8 + dz), rot=(0, s * .5, 0), bevel=0)
    for x in (-1.0, 0, 1.0):
        lit.box((.8, .05, .38), loc=(x, -3.35, 4.8), bevel=0)
        louv.box((.9, .1, .05), loc=(x, -3.4, 4.9), rot=(-.5, 0, 0), bevel=0)
    team.box((3.4, 6.4, .1), loc=(0, -.1, 5.52), bevel=.03, seg=1)                                      # war room roof
    armor.box((3.44, .12, .14), loc=(0, -3.28, 5.55), bevel=0)                                          # roof brow
    # Command tent rolled along the left upper edge, air-conditioning units on the right.
    for y in (-2.6, 0, 2.6):
        steel.box((.2, .06, .3), loc=(2.12, y, 3.75), bevel=0)
    a.part('Tent_roll', 'Canvas').cyl(.2, 6.2, loc=(2.2, 0, 3.85), rot=FORWARD, seg=10, bevel=.04, bseg=1)
    for y in (-2.8, 2.8):
        a.part('Tent_straps', 'Charred').cyl(.215, .1, loc=(2.2, y * .8, 3.85), rot=FORWARD, seg=10, bevel=0)
    for y in (-1.6, 1.6):
        a.part('Aircon', 'Fuel').box((.36, 1.0, .7), loc=(-2.2, y, 3.55), bevel=.03, seg=1)
        a.part('Aircon_grilles', 'Undercarriage').grille(.8, .5, loc=(-2.39, y, 3.55), rot=(0, 0, -R90), slats=4,
                                                          depth=.04, thickness=.03)
    _hatch(a, 0, -1.2, 5.55, .34)
    for s in (-1, 1):
        a.part('Gilt_stripes', 'Gilded').box((.03, 6.0, .05), loc=(s * 1.74, -.1, 5.15), bevel=0)
    # Rear: generator with exhaust, rear door, tail lights.
    gen = a.part('Generator', 'Armor')
    gen.box((1.8, 1.0, 1.1), loc=(.9, 6.4, 4.65), bevel=.04, seg=1)
    a.part('Generator_grille', 'Undercarriage').grille(.9, .6, loc=(.9, 6.92, 4.65), rot=(0, 0, math.pi), slats=4,
                                                        depth=.05, thickness=.035)
    steel.cyl(.08, .8, loc=(1.6, 6.2, 5.5), seg=8, bevel=0)
    fbox(armor, '+y', (-.2, 6.8, 2.9), (1.2, .06, 1.7), out=.02, bevel=.012)                             # rear door
    for s in (-1, 1):
        _taillight(a, s * 1.8, 6.82, 2.3)
        steel.box((.14, .2, .14), loc=(s * .9, 6.95, 1.55), bevel=.02, seg=1)                            # tow eyes

    # Part_mg / Part_mg.001: remote machine guns on the war room's front corners.
    for name, x in (('Part_mg', 1.15), ('Part_mg.001', -1.15)):
        pv(a, name, (x, -2.75, 5.57))
        rws(a, name.replace('Part_', 'Mount_'), (0, 0, 0), parent=name, length=.85, ammo=-1 if x > 0 else 1)

    # Part_antenna: the command antenna farm, origin at the mast foot on the rear roof.
    pa = pv(a, 'Part_antenna', (-.6, 4.9, 4.1))
    top = _telescopic_mast(a, 0, 0, 0, ((.16, 2.0), (.13, 1.9), (.1, 1.8)), parent=pa)
    _lpda(a, 0, 0, top + .1, parent=pa, length=1.8, elements=8)
    dip = a.part('Dipoles', 'Steel', pa)
    dip.cyl(.035, .9, loc=(0, 0, top + .6), seg=6, bevel=0)
    for u in (0, R90):
        dip.cyl(.02, 1.4, loc=(0, 0, top + .9), rot=(R90, 0, u), seg=5, bevel=0)
    a.part('Mast_beacon', 'LavaGlow', pa).sphere(.07, loc=(0, 0, top + 1.1), seg=8, rings=5)
    for gx, gy in ((-1.25, -1.1), (1.25, -1.1), (-1.25, 1.0), (.45, .95)):                            # mast guys
        a.part('Guys', 'Steel', pa).tube([(0, 0, top - 1.8), (gx, gy, .02)], .01, seg=4)
    rad = a.part('Satcom', 'Medical', pa)
    rad.cyl(.95, .14, loc=(.6, -3.6, 1.5), seg=18, bevel=.02, bseg=1)
    rad.sphere((.9, .9, .72), loc=(.6, -3.6, 1.56), seg=18, rings=8, cut=0)
    for dx, dy, h in ((-.5, .9, .5), (2.5, -1.2, .5)):
        a.part('Dish_posts', 'Steel', pa).cyl(.06, h, loc=(dx, dy, h / 2), seg=8, bevel=0)
        _dish(a.part('Link_dishes', 'Medical', pa), (dx, dy + .05, h + .25), .38, .38, depth=.14, seg=12, tilt=.5)
    for x, y, h in ((-1.3, 1.8, 2.4), (2.55, 1.85, 2.1), (-1.3, -.6, 1.8), (2.4, -.6, 1.5)):
        _whip(a, x, y, 0, h, parent=pa)


BUILDERS = {
    'armored_bulldozer': (armored_bulldozer, dict(ao_distance=.7, grime_height=.6)),
    'rail_supergun': (rail_supergun, dict(ao_distance=1.4, grime_height=.8)),
    'rail_tractor': (rail_tractor, dict(ao_distance=.8, grime_height=.7)),
    'targeting_station': (targeting_station, dict(ao_distance=.9, grime_height=.6)),
    'earth_borer': (earth_borer, dict(ao_distance=1.0, grime_height=.8)),
    'command_airship': (command_airship, dict(ao_distance=1.3, ground=False)),
    'landing_hovercraft': (landing_hovercraft, dict(ao_distance=1.0, grime_height=.8)),
    'supreme_command': (supreme_command, dict(ao_distance=.9, grime_height=.8)),
}


if __name__ == '__main__':
    import mb_round6
    mb_round6.main(BUILDERS)

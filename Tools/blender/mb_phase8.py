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
from mb_bosses import _hull2d, _plate_bolts, _railing, _sec6, track_shoes, track_unit  # noqa: E402
from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_siege import bag_arc, bag_run, flag, flood_head, generator, lattice, loop_rail  # noqa: E402
from mb_support import _beacon, _lpda, _ram, _whip  # noqa: E402
from mb_themes import ladder  # noqa: E402
from mb_town import fbox  # noqa: E402
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _cable, _dish, _frame, _glacis, _headlight,  # noqa: E402
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
    a.part(f'RWS_socket_{tag}', 'Steel', parent).cyl(.3, .08, loc=_v(loc, dz=.03), seg=14, bevel=.01, bseg=1)
    m = a.pivot(key, loc, dotted(parent) if parent else None)
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
    w, d, h = size
    a.part(f'Gun_ring_{tag}', 'Armor', parent).cyl(w * .5, .1, loc=_v(loc, dz=.03), seg=18, bevel=.02, bseg=1)
    m = a.pivot(key, loc, dotted(parent) if parent else None)
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


BUILDERS = {
    'armored_bulldozer': (armored_bulldozer, dict(ao_distance=.7, grime_height=.6)),
}


if __name__ == '__main__':
    import mb_round6
    mb_round6.main(BUILDERS)

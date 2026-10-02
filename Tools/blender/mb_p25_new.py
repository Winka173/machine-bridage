"""Machine Brigade prompt 25 F2 batch A (DECISIONS 25F2-A): models for the balance sheet's new units and structures.

Drawn low-effort on purpose (prompt 27 remakes every model): the right size (the data's "modelSize": 0.8 x real on the
ground, 0.4 x real in the air), a silhouette that carries the one or two features the sheet's shape note names, the
pivots and muzzles the game looks up (Turret, Muzzle_<slot>, Mount_mg / Muzzle_mg, Point_exhaust, Point_fire) and the
side's colour (Team) on the roof and both sides. Nothing thinner than 0.1 m; parts overlap or stand 1 cm apart. The looks
are post-1945 (the heavy flak gun and the balloon are drawn so prompt 26's KS-19 and aerostat can keep them).

Conventions are mb_vehicles': metres, +Z up, Blender -Y is the front, origin on the ground at the centre (an aircraft's
at its centre).

Headless: blender --background --python Tools/blender/build_assets.py -- heavy_flak_tower
"""
import math

import mb_vehicles as mv
from mb_vehicles import ACROSS, FORWARD, R90


# ------------------------------------------------------------------------------------------------ shared pieces

def _stripes(a, length, width, z, parent=None, y=0.0):
    """The side's colour: a roof band and a band down each side."""
    team = a.part('Team_bands', 'Team', parent)
    team.box((width * .5, length * .5, .03), loc=(0, y, z + .015), bevel=0)
    for s in (-1, 1):
        team.box((.03, length * .55, .22), loc=(s * (width / 2 + .005), y, z - .25), bevel=0)


def _wheels(a, xs, ys, r, width=.34):
    for x in xs:
        for y in ys:
            mv._wheel(a, x, y, r, width, seg=12)


def _truck(a, length, width, cab, axles, r=.45, bed_h=1.25, cab_h=2.0, armoured=True):
    """A wheeled chassis: a cab of `cab` metres at the front, a flat bed behind; returns the bed's top."""
    body = a.part('Hull', 'Team' if armoured else 'Armor')
    chassis = a.part('Chassis', 'Undercarriage')
    chassis.box((width * .8, length * .95, .3), loc=(0, 0, r + .05), bevel=0)
    y0 = -length / 2
    body.box((width, cab, cab_h - r), loc=(0, y0 + cab / 2, r + (cab_h - r) / 2), bevel=.08, seg=1, taper=(1, .85))
    a.part('Glass', 'Glass').box((width * .8, .05, .35), loc=(0, y0 - .01, cab_h - .45), bevel=0)
    body.box((width, length - cab - .05, bed_h - r), loc=(0, y0 + cab + (length - cab) / 2, r + (bed_h - r) / 2), bevel=.05, seg=1)
    step = (length - 1.2) / max(1, axles - 1)
    _wheels(a, (-(width / 2 - .1), width / 2 - .1), [y0 + .8 + step * k for k in range(axles)], r)
    a.pivot('Point_exhaust', (width / 2 - .2, y0 + cab, cab_h))
    a.pivot('Point_fire', (0, 0, bed_h + .2))
    return bed_h


def _tracked(a, length, width, height, wheels=6, glacis=.6):
    """A tracked hull with its tracks; returns the hull's top."""
    mv.tracks(a, width / 2 - .25, length, .7, .26, wheels, .42, belt_width=.46, wheel_seg=10, lean=True)
    hull = a.part('Hull', 'Team')
    y0, y1 = -length / 2, length / 2
    hull.prism([(y0, .55), (y0 + .05, .8), (y0 + glacis, height), (y1 - .1, height), (y1, height - .2), (y1, .55)], width - .5, bevel=.05)
    a.pivot('Point_exhaust', (width / 2 - .45, y1 - .3, height))
    a.pivot('Point_fire', (0, 0, height + .2))
    return height


def _sandbags(a, radius, height, gap=None, seg=16, name='Sandbags'):
    """A ring of sandbags (a horseshoe open at the rear when gap is given, in radians)."""
    bags = a.part(name, 'Sandbag')
    n = seg
    for k in range(n):
        ang = k * math.tau / n
        if gap and abs(math.atan2(math.sin(ang - R90), math.cos(ang - R90))) < gap / 2:
            continue
        x, y = radius * math.cos(ang), radius * math.sin(ang)
        bags.box((.7, radius * math.tau / n + .05, height), loc=(x, y, height / 2), rot=(0, 0, ang), bevel=.1, seg=1)


def _pad(a, w, d, h=.2, mat='Concrete'):
    a.part('Pad', mat).box((w, d, h), loc=(0, 0, h / 2), bevel=.04, seg=1)
    return h


def _launcher_box(a, parent, loc, size, cells, pitch, mat='Armor', face='Undercarriage'):
    """A missile box tilted up by pitch with `cells` round tube mouths on its front face; returns the front centre."""
    w, d, h = size
    # Rotating about X by -pitch raises the front (-Y) face; the front face's up is (0, sin, cos).
    a.part('Launcher', mat, parent).box(size, loc=loc, rot=(-pitch, 0, 0), bevel=.04, seg=1)
    c, s = math.cos(pitch), math.sin(pitch)
    front = (loc[0], loc[1] - (d / 2 + .02) * c, loc[2] + (d / 2 + .02) * s)
    _tube_faces(a, parent, front, pitch, [((i - (cells[0] - 1) / 2) * w / cells[0], (j - (cells[1] - 1) / 2) * h / cells[1])
                                           for i in range(cells[0]) for j in range(cells[1])],
                min(w / cells[0], h / cells[1]) * .36, face)
    return front


def _tube_faces(a, parent, front, pitch, offsets, r, mat='Undercarriage'):
    """Round tube mouths on a launcher face centred at `front`, facing forward and `pitch` up; offsets are (across, up)."""
    c, s = math.cos(pitch), math.sin(pitch)
    tubes = a.part('Tubes', mat, parent)
    for x, u in offsets:
        tubes.cyl(r, .04, loc=(front[0] + x, front[1] + u * s, front[2] + u * c), rot=(R90 - pitch, 0, 0), seg=8, bevel=0)


def _gun(a, parent, start, length, r, pitch=0.0, style='collar', x=0.0, slot='main'):
    """A barrel forward from `start` (y, z) under `parent`, with its muzzle pivot."""
    muzzle = mv._barrel(a, parent, start[0], length, r, start[1], pitch=pitch, style=style, x=x,
                        brake=(r * 3.2, r * 3.4, r * 3.2), seg=10)
    a.pivot(f'Muzzle_{slot}', muzzle, parent)


# ------------------------------------------------------------------------------------------------ towers and structures

def heavy_flak_tower(a):
    """A heavy towed AA gun of the KS-19 kind in a round emplacement: cruciform outriggers, a box shield, a long barrel
    raised 28 degrees; 7.0 x 6.0 x 3.4 m (wave 2: was 40 degrees and 4.2 m, 4.9 m tall)."""
    _pad(a, 6.4, 6.4, .15)
    _sandbags(a, 3.0, .9, gap=.9)
    mount = a.part('Mount', 'Armor')
    for ang in (0, R90):
        mount.box((.35, 5.2, .25), loc=(0, 0, .3), rot=(0, 0, ang), bevel=.04, seg=1)
    t = a.pivot('Turret', (0, 0, .45))
    a.part('Carriage', 'Team', t).box((1.6, 2.2, .9), loc=(0, .2, .5), bevel=.08, seg=1)
    a.part('Shield', 'Armor', t).box((1.9, .1, 1.1), loc=(0, -.9, 1.25), rot=(.2, 0, 0), bevel=.03, seg=1)
    a.part('Recoil', 'Steel', t).box((.5, 1.8, .45), loc=(0, .1, 1.2), rot=(-.49, 0, 0), bevel=.04, seg=1)
    _gun(a, t, (-.2, 1.35), 3.6, .12, pitch=math.radians(28), style='baffle')
    a.part('Ready_rounds', 'Crate').box((.9, .6, .5), loc=(2.1, 1.4, .4), bevel=.04, seg=1)
    _stripes(a, 2.0, 1.6, 1.0, t, y=.2)


def at_gun_emplacement(a):
    """A towed 100 mm anti-tank gun (MT-12 / 2A45 look) behind a horseshoe of sandbags open at the rear: a very long
    barrel with a muzzle brake, a flat shield, split trails; 5.8 x 4.2 x 2.0 m."""
    _sandbags(a, 2.0, .8, gap=1.4, seg=14)
    t = a.pivot('Turret', (0, .3, 0))
    a.part('Shield', 'Team', t).box((1.9, .1, 1.4), loc=(0, -.45, 1.1), rot=(.12, 0, 0), bevel=.03, seg=1, taper=(.8, 1))
    a.part('Cradle', 'Armor', t).box((.45, 1.3, .4), loc=(0, .1, .85), bevel=.04, seg=1)
    trails = a.part('Trails', 'Armor', t)
    for s in (-1, 1):
        trails.limb((s * .2, .5, .5), (s * 1.0, 1.8, .12), .18, .18)
        mv._wheel(a, s * .85, .1, .32, .2)
    _gun(a, t, (-.55, .88), 3.2, .075, style='baffle')


def blast_wall(a):
    """A line of Hesco gabions: two cells deep at the bottom, one on top, five long; 4.8 x 1.9 x 2.4 m."""
    fill = a.part('Gabions', 'Sandbag')
    frame = a.part('Frames', 'Steel')
    for i in range(5):
        x = (i - 2) * .95
        for y in (-.47, .47):
            fill.box((.92, .92, 1.15), loc=(x, y, .58), bevel=.05, seg=1)
        fill.box((.92, .92, 1.15), loc=(x, 0, 1.78), bevel=.05, seg=1)
        for z in (1.17, 2.37):
            frame.box((.95, .95 if z > 2 else 1.9, .03), loc=(x, 0, z), bevel=0)
    a.part('Team_bands', 'Team').box((4.7, .95, .03), loc=(0, 0, 2.4), bevel=0)


def inflatable_decoy(a):
    """An inflatable gun turret: soft pillowy hull and turret, a fat barrel, seam bands, tethers and a blower box;
    5.0 x 4.6 x 2.6 m."""
    skin = a.part('Skin', 'Team')
    fabric = a.part('Fabric', 'Canvas')
    fabric.sphere((2.2, 2.2, .9), loc=(0, 0, .6), seg=14, rings=8, cut=-.6)
    skin.sphere((1.3, 1.4, .8), loc=(0, .2, 1.5), seg=14, rings=8)
    skin.cyl(.28, 2.4, loc=(0, -1.9, 1.6), rot=FORWARD, seg=12, bevel=.1)
    seams = a.part('Seams', 'Undercarriage')
    seams.cyl(1.32, .06, loc=(0, .2, 1.5), seg=14, bevel=0)
    for y in (-2.4, -1.4):
        seams.cyl(.3, .06, loc=(0, y, 1.6), rot=FORWARD, seg=12, bevel=0)
    pegs = a.part('Tethers', 'Rubber')
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        pegs.limb((sx * 1.6, sy * 1.6, .7), (sx * 2.3, sy * 2.2, 0), .1, .1)
    a.part('Blower', 'Armor').box((.6, .5, .5), loc=(2.2, -1.2, .25), bevel=.05, seg=1)


def fire_control_centre(a):
    """A fire-direction centre: two joined shelters, a lattice mast with an antenna head, a dish, a generator and a
    net awning; 6.0 x 6.0 x 5.5 m."""
    _pad(a, 5.8, 5.8, .12)
    body = a.part('Shelters', 'Team')
    body.box((2.4, 4.2, 2.3), loc=(-1.3, 0, 1.27), bevel=.06, seg=1)
    body.box((2.0, 3.0, 2.0), loc=(1.2, .5, 1.12), bevel=.06, seg=1)
    mast = a.part('Mast', 'Steel')
    for s in (-1, 1):
        mast.box((.12, .12, 5.0), loc=(-1.3 + s * .25, -1.5, 2.6), bevel=0)
    for z in (1.5, 2.8, 4.1):
        mast.box((.62, .12, .12), loc=(-1.3, -1.5, z), bevel=0)
    a.pivot('Radar', (-1.3, -1.5, 5.2))
    a.part('Antenna_head', 'Armor', 'Radar').box((1.2, .3, .5), loc=(0, 0, 0), bevel=.05, seg=1)
    mv._dish(a.part('Dish', 'Medical'), (1.6, -1.6, 1.0), .6, .6, tilt=.6)
    a.part('Generator', 'Armor').box((1.0, 1.3, .9), loc=(1.8, -1.8, .57), bevel=.05, seg=1)
    a.part('Awning', 'Canvas').box((2.0, 2.2, .05), loc=(1.2, 2.4, 2.1), rot=(.2, 0, 0), bevel=0)


def searchlight(a):
    """A 150 cm defence searchlight drum on a turntable trailer with outriggers and a generator, sandbags round it;
    3.6 x 3.0 x 2.8 m."""
    _sandbags(a, 1.6, .6, seg=12)
    base = a.part('Trailer', 'Armor')
    base.box((1.6, 2.2, .4), loc=(0, .3, .45), bevel=.05, seg=1)
    for s in (-1, 1):
        base.limb((s * .7, 0, .5), (s * 1.5, -.9, .05), .12, .12)
    a.part('Generator', 'Armor').box((.9, .8, .7), loc=(0, 1.2, 1.0), bevel=.05, seg=1)
    t = a.pivot('Turret', (0, -.1, .7))
    a.part('Yoke', 'Team', t).box((1.7, .4, 1.1), loc=(0, 0, .55), bevel=.05, seg=1)
    a.part('Drum', 'Team', t).cyl(.7, 1.0, loc=(0, 0, 1.5), rot=(R90 - .35, 0, 0), seg=16, bevel=.05)
    a.part('Lens', 'Lamp', t).cyl(.62, .05, loc=(0, -.47, 1.67), rot=(R90 - .35, 0, 0), seg=16, bevel=0)
    a.pivot('Muzzle_main', (0, -.55, 1.7), t)


def barrage_balloon(a):
    """A winch trailer with a cable drum and a modern streamlined tethered aerostat 12 m up, three tail fins; the
    cable 0.12 m thick; 9.0 x 4.0 x 16 m."""
    a.part('Winch', 'Armor').box((2.4, 3.0, .9), loc=(0, 0, .55), bevel=.06, seg=1)
    a.part('Drum', 'Steel').cyl(.5, 1.6, loc=(0, 0, 1.3), rot=ACROSS, seg=12, bevel=.03)
    _wheels(a, (-1.2, 1.2), (-.8, .8), .35, .25)
    a.part('Cable', 'Steel').cyl(.06, 11.0, loc=(0, 0, 7.0), seg=6, bevel=0)
    env = a.part('Envelope', 'Medical')
    env.sphere((1.9, 4.5, 1.9), loc=(0, 0, 14.0), seg=18, rings=10)
    fins = a.part('Fins', 'Team')
    for ang in (0, 2.094, 4.189):
        x, z = math.sin(ang) * 1.3, math.cos(ang) * 1.3
        fins.box((.08, 1.6, 1.3), loc=(x, 3.9, 14.0 + z), rot=(0, ang, 0), bevel=.02, seg=1)
    a.part('Team_bands', 'Team').cyl(1.92, .4, loc=(0, -1.0, 14.0), rot=FORWARD, seg=18, bevel=0)


def visual_jammer(a):
    """An electronic camouflage station: an equipment container, a lattice mast with flat emitter panels, aerosol
    drums and a generator; 6.0 x 5.0 x 6.5 m."""
    _pad(a, 4.8, 5.8, .12)
    a.part('Container', 'Team').box((2.3, 5.0, 2.4), loc=(-1.2, 0, 1.32), bevel=.06, seg=1)
    mast = a.part('Mast', 'Steel')
    for s in (-1, 1):
        mast.box((.12, .12, 5.4), loc=(1.3 + s * .25, 0, 2.8), bevel=0)
    for z in (1.6, 3.2):
        mast.box((.62, .12, .12), loc=(1.3, 0, z), bevel=0)
    panels = a.part('Emitters', 'Armor')
    for k, ang in enumerate((0, 2.1, 4.2)):
        panels.box((.9, .1, 1.2), loc=(1.3 + math.sin(ang) * .45, math.cos(ang) * .45, 5.6), rot=(0, 0, ang), bevel=.02, seg=1)
    drums = a.part('Drums', 'Fuel')
    for y in (-1.6, -.9):
        drums.cyl(.35, 1.0, loc=(1.6, y, .62), seg=12, bevel=.03)
    a.part('Generator', 'Armor').box((1.0, 1.1, .9), loc=(1.6, 1.7, .57), bevel=.05, seg=1)


def troop_shelter(a):
    """A half-buried concrete bunker under an earth berm, an entrance ramp at the rear with a blast door, two vents;
    6.0 x 5.0 x 2.2 m."""
    a.part('Berm', 'Dirt').prism([(-3.0, 0), (-2.0, 1.6), (2.0, 1.6), (3.0, 0)], 5.0, axis='X', bevel=.1, seg=1)
    a.part('Roof', 'Concrete').box((4.2, 4.0, .4), loc=(0, 0, 1.75), bevel=.08, seg=1)
    a.part('Door', 'Armor').box((1.4, .12, 1.2), loc=(0, 2.51, .8), bevel=.03, seg=1)
    a.part('Ramp', 'Concrete').box((1.8, 1.0, .1), loc=(0, 3.0, .15), rot=(-.25, 0, 0), bevel=0)
    vents = a.part('Vents', 'Steel')
    for x in (-1.2, 1.2):
        vents.cyl(.14, .5, loc=(x, -.8, 2.15), seg=8, bevel=0)
    a.part('Team_bands', 'Team').box((2.0, 3.8, .03), loc=(0, 0, 1.97), bevel=0)
    _sandbags(a, 2.8, .5, gap=1.0, seg=14)


def flare_tower(a):
    """An illumination launcher: a steel platform 3 m up with a multi-tube flare mortar on a turntable, ammunition
    boxes, a solid ladder; 3.6 x 3.6 x 5.0 m."""
    legs = a.part('Legs', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            legs.box((.16, .16, 3.0), loc=(sx * 1.2, sy * 1.2, 1.5), bevel=0)
    a.part('Deck', 'Armor').box((3.0, 3.0, .2), loc=(0, 0, 3.1), bevel=.04, seg=1)
    a.part('Ladder', 'Steel').box((.5, .12, 3.0), loc=(0, 1.6, 1.5), rot=(.1, 0, 0), bevel=0)
    t = a.pivot('Turret', (0, 0, 3.2))
    a.part('Base', 'Team', t).cyl(.7, .3, loc=(0, 0, .15), seg=12, bevel=.03)
    front = _launcher_box(a, t, (0, 0, .75), (.9, .8, .7), (3, 2), math.radians(55), mat='Team')
    a.pivot('Muzzle_main', front, t)
    a.part('Ammo', 'Crate').box((.8, .5, .4), loc=(.9, .9, 3.4), bevel=.04, seg=1)


def laser_ad_station(a):
    """A fixed high-energy laser site: a container, a big domed laser turret with a round aperture, a flat radar panel
    on a short mast, a cooling unit; 6.0 x 4.0 x 4.6 m."""
    _pad(a, 3.9, 5.8, .12)
    a.part('Container', 'Team').box((2.4, 5.2, 2.3), loc=(0, .3, 1.27), bevel=.06, seg=1)
    t = a.pivot('Turret', (0, -1.0, 2.42))
    a.part('Dome', 'Medical', t).sphere((.95, .95, .95), loc=(0, 0, .5), seg=16, rings=8, cut=-.4)
    a.part('Aperture', 'Energy', t).cyl(.35, .1, loc=(0, -.9, .75), rot=FORWARD, seg=12, bevel=0)
    a.pivot('Muzzle_main', (0, -.98, .75), t)
    a.part('Radar_mast', 'Steel').box((.15, .15, 1.2), loc=(.8, 2.3, 3.0), bevel=0)
    a.part('Radar_panel', 'Armor').box((1.1, .12, .9), loc=(.8, 2.3, 3.9), rot=(-.25, 0, 0), bevel=.03, seg=1)
    a.part('Cooler', 'Steel').box((1.0, 1.0, .8), loc=(-.9, 2.4, 2.8), bevel=.04, seg=1)


def aa_gun_tower(a):
    """A single Bofors 40 mm L/70 on a turntable with a small shield and a fire-control dish on a post, in a sandbag ring
    with clip racks; 5.5 x 5.5 x 3.2 m."""
    _pad(a, 5.2, 5.2, .15)
    _sandbags(a, 2.5, .8, seg=16)
    t = a.pivot('Turret', (0, 0, .2))
    a.part('Turntable', 'Armor', t).cyl(1.0, .3, loc=(0, 0, .15), seg=14, bevel=.03)
    a.part('Mount', 'Team', t).box((1.3, 1.5, 1.0), loc=(0, .1, .8), bevel=.06, seg=1)
    a.part('Shield', 'Armor', t).box((1.4, .08, .7), loc=(0, -.7, 1.1), rot=(.2, 0, 0), bevel=.02, seg=1)
    _gun(a, t, (-.6, 1.25), 2.7, .07, pitch=math.radians(35), style='flash')
    a.part('Radar_post', 'Steel').box((.14, .14, 1.8), loc=(1.8, 1.6, .9), bevel=0)
    mv._dish(a.part('Radar_dish', 'Medical'), (1.8, 1.6, 2.0), .45, .45, tilt=.4)
    a.part('Clips', 'Crate').box((.8, .4, .5), loc=(-1.8, 1.2, .4), bevel=.04, seg=1)


# ------------------------------------------------------------------------------------------------ ground vehicles

def aa_gun_vehicle(a):
    """A tracked 40 mm SPAAG (CV90 AA look): an IFV hull, a turret with one long 40 mm gun and a search radar at the
    turret's rear; 5.9 x 2.5 x 2.7 m."""
    top = _tracked(a, 5.3, 2.5, 1.55)
    t = a.pivot('Turret', (0, .3, top))
    a.part('Turret_body', 'Team', t).box((1.7, 2.0, .7), loc=(0, 0, .35), bevel=.08, seg=1, taper=(.85, .9))
    _gun(a, t, (-1.0, .45), 2.2, .07, pitch=math.radians(20), style='flash')
    a.pivot('Radar', (0, .9, .95), t)
    a.part('Radar_panel', 'Armor', 'Radar').box((1.0, .1, .45), loc=(0, 0, .1), bevel=.02, seg=1)
    _stripes(a, 3.5, 2.0, top)


def shorad_vehicle(a):
    """An Avenger: a HMMWV-type 4x4 with a small turret in the bed, a four-tube Stinger pod either side and a sensor
    box, and its roof machine gun; 3.8 x 1.8 x 2.2 m."""
    body = a.part('Hull', 'Team')
    body.box((1.8, 1.5, .55), loc=(0, -1.1, .85), bevel=.08, seg=1, taper=(.95, .9))
    body.box((1.8, 1.6, .9), loc=(0, .5, 1.0), bevel=.06, seg=1)
    a.part('Glass', 'Glass').box((1.5, .05, .35), loc=(0, -.36, 1.3), bevel=0)
    _wheels(a, (-.78, .78), (-1.2, 1.1), .38, .3)
    t = a.pivot('Turret', (0, .6, 1.45))
    a.part('Turret_body', 'Armor', t).box((.7, .7, .6), loc=(0, 0, .3), bevel=.05, seg=1)
    front = None
    for s in (-1, 1):
        front = _launcher_box(a, t, (s * .6, 0, .45), (.4, .9, .4), (2, 2), math.radians(10), mat='Team')
    a.pivot('Muzzle_missile', (0, front[1], front[2]), t)
    mv._roof_mg(a, None, (.55, -.4, 1.5), length=.6, shield=False)
    a.pivot('Point_exhaust', (.8, 1.2, .8))
    a.pivot('Point_fire', (0, 0, 1.6))


def microwave_vehicle(a):
    """A 6x6 armoured truck carrying a high-power microwave emitter: a big flat square panel on a turret, generator
    boxes behind the cab; 5.8 x 2.1 x 2.9 m."""
    top = _truck(a, 5.8, 2.1, 1.8, 3, r=.45, bed_h=1.2)
    a.part('Generators', 'Armor').box((1.8, 1.2, .7), loc=(0, .5, top + .35), bevel=.05, seg=1)
    t = a.pivot('Turret', (0, 1.8, top))
    a.part('Pedestal', 'Armor', t).cyl(.35, .5, loc=(0, 0, .25), seg=10, bevel=.03)
    a.part('Emitter', 'Team', t).box((1.8, .25, 1.4), loc=(0, -.15, 1.2), rot=(-.15, 0, 0), bevel=.05, seg=1)
    a.part('Emitter_face', 'Undercarriage', t).box((1.6, .05, 1.2), loc=(0, -.3, 1.2), rot=(-.15, 0, 0), bevel=0)
    a.pivot('Muzzle_main', (0, -.35, 1.2), t)
    _stripes(a, 2.0, 2.1, 2.0, y=-2.0)


def nlos_atgm_vehicle(a):
    """A 6x6 armoured truck with a raised four-cell Spike NLOS box launcher and a mast sensor, a roof machine gun;
    6.0 x 2.1 x 2.6 m."""
    top = _truck(a, 6.0, 2.1, 1.9, 3, r=.45, bed_h=1.2)
    t = a.pivot('Turret', (0, 1.4, top))
    front = _launcher_box(a, t, (0, 0, .7), (1.6, 1.8, .9), (2, 2), math.radians(30), mat='Team')
    a.pivot('Muzzle_missile', front, t)
    a.part('Sensor_mast', 'Steel').box((.12, .12, .9), loc=(-.7, -1.6, 2.4), bevel=0)
    a.part('Sensor', 'Glass').box((.3, .3, .25), loc=(-.7, -1.6, 2.9), bevel=.03, seg=1)
    mv._roof_mg(a, None, (.5, -2.3, 2.0), length=.6, shield=False)
    _stripes(a, 1.6, 2.1, 2.0, y=-2.0)


def radar_atgm_vehicle(a):
    """Khrizantema-S: a tracked BMP-3-type hull, twin launch rails on arms raised from the front and a big
    millimetre-wave radar box at the rear-centre; 5.8 x 2.5 x 2.3 m."""
    top = _tracked(a, 5.6, 2.5, 1.45, glacis=1.0)
    t = a.pivot('Turret', (0, -.8, top))
    rails = a.part('Rails', 'Team', t)
    for x in (-.45, .45):
        rails.box((.25, 2.2, .25), loc=(x, -.4, .5), rot=(.3, 0, 0), bevel=.03, seg=1)
    a.part('Missiles', 'Armor', t).cyl(.1, 1.8, loc=(0, -.5, .72), rot=(R90 - .3, 0, 0), seg=8, bevel=0)
    a.pivot('Muzzle_missile', (0, -1.55, .85), t)
    a.pivot('Radar', (0, 1.4, top + .1))
    a.part('Radar_box', 'Medical', 'Radar').box((1.2, .9, .8), loc=(0, 0, .45), bevel=.08, seg=1)
    _stripes(a, 3.0, 2.0, top)


def recoilless_jeep(a):
    """An open 4x4 jeep (M151 look) with a 106 mm recoilless rifle on a pedestal in the back, its long barrel reaching
    over the bonnet; 3.5 x 1.4 x 1.6 m."""
    body = a.part('Body', 'Team')
    a.part('Chassis', 'Undercarriage').box((1.2, 3.0, .22), loc=(0, 0, .45), bevel=0)
    body.box((1.4, 1.2, .35), loc=(0, -.9, .75), bevel=.05, seg=1)
    body.box((1.4, 1.7, .5), loc=(0, .55, .8), bevel=.05, seg=1)
    _wheels(a, (-.62, .62), (-1.05, .95), .33, .26)
    t = a.pivot('Turret', (0, .6, 1.05))
    a.part('Pedestal', 'Steel', t).cyl(.1, .35, loc=(0, 0, .18), seg=8, bevel=0)
    _gun(a, t, (1.2, .4), 3.0, .075, style='collar')
    a.part('Breech', 'Steel', t).cyl(.12, .5, loc=(0, 1.35, .4), rot=FORWARD, seg=10, bevel=.02)
    a.pivot('Point_exhaust', (.5, 1.4, .5))
    a.pivot('Point_fire', (0, 0, 1.2))


def _airborne_body(a, lift=0.0):
    top = _tracked(a, 4.8, 2.5, 1.3 + lift, wheels=5, glacis=.9)
    t = a.pivot('Turret', (0, .2, top))
    a.part('Turret_body', 'Team', t).box((1.5, 1.7, .55), loc=(0, 0, .28), bevel=.08, seg=1, taper=(.85, .85))
    _gun(a, t, (-.85, .35), 1.9, .09, style='collar')
    mv._coax(a, t, .35, -.85, .35, length=.9, housing=.3)
    _stripes(a, 2.8, 2.0, top)
    return top


def airborne_vehicle(a):
    """A light airborne IFV (BMD-4 look): a low short tracked hull on five road wheels, a BMP-3-style turret with a
    short 100 mm gun and a 30 mm cannon beside it; 5.0 x 2.5 x 2.0 m."""
    _airborne_body(a)


def airborne_vehicle_chute(a):
    """The airborne vehicle on its drop pallet under three large canopies 8-10 m up; 9 x 9 x 11 m, origin at the
    vehicle's bottom centre (the game draws it falling)."""
    _airborne_body(a)
    a.part('Pallet', 'Wood').box((2.8, 5.2, .2), loc=(0, 0, -.12), bevel=.02, seg=1)
    canopy = a.part('Canopies', 'Canvas')
    risers = a.part('Risers', 'Undercarriage')
    for k in range(3):
        ang = k * math.tau / 3
        x, y = math.cos(ang) * 2.4, math.sin(ang) * 2.4
        canopy.sphere((2.5, 2.5, 1.3), loc=(x, y, 9.0), seg=12, rings=6, cut=0)
        risers.limb((x * .1, y * .1, 1.8), (x, y, 9.0), .1, .1)


def wheeled_howitzer(a):
    """A CAESAR 6x6 truck-mounted 155 mm howitzer: a cab in front, the long 52-calibre barrel lying back over the cab in
    travel, a turntable mount and a big firing spade at the rear; 8.0 x 2.1 x 3.0 m."""
    top = _truck(a, 7.4, 2.1, 1.8, 3, r=.45, bed_h=1.2, armoured=False)
    t = a.pivot('Turret', (0, 2.3, top))
    a.part('Mount', 'Team', t).box((1.6, 1.6, .7), loc=(0, 0, .35), bevel=.06, seg=1)
    _gun(a, t, (-.4, .9), 5.6, .09, pitch=math.radians(4), style='baffle')
    a.part('Spade', 'Armor').box((2.0, .2, 1.0), loc=(0, 3.75, .6), rot=(.3, 0, 0), bevel=.03, seg=1)
    _stripes(a, 1.7, 2.1, 2.0, y=-2.8)


def sp_mortar(a):
    """An 8x8 armoured vehicle (Patria AMV look) with a boxy twin-barrel 120 mm mortar turret (AMOS look) and a roof
    machine gun; 6.3 x 2.3 x 2.5 m."""
    hull = a.part('Hull', 'Team')
    hull.prism([(-3.1, .6), (-3.1, 1.05), (-2.3, 1.75), (3.1, 1.75), (3.1, .6)], 2.3, axis='X', bevel=.06)
    _wheels(a, (-1.0, 1.0), (-2.3, -1.05, .45, 1.7), .45, .32)
    t = a.pivot('Turret', (0, .5, 1.75))
    a.part('Turret_body', 'Armor', t).box((1.9, 2.0, .7), loc=(0, 0, .35), bevel=.07, seg=1, taper=(.9, .9))
    for x in (-.3, .3):
        mv._barrel(a, t, -.9, 1.4, .1, .45, pitch=math.radians(12), style='collar', x=x, suffix='' if x < 0 else '_2',
                   brake=(.26, .2, .26), seg=10)
    a.pivot('Muzzle_main', (0, -2.35, .75), t)
    mv._roof_mg(a, t, (.7, .6, .7), length=.6, shield=False)
    a.pivot('Point_exhaust', (1.0, 2.6, 1.4))
    a.pivot('Point_fire', (0, 0, 1.9))
    _stripes(a, 3.0, 2.0, 1.75, y=-1.4)


def radar_scout(a):
    """A 4x4 armoured scout car (Fennek look): low with a wedge nose, a telescopic mast about 3 m above the roof with a
    sensor head, a roof 12.7 mm gun; 4.6 x 2.0 x 4.0 m."""
    hull = a.part('Hull', 'Team')
    hull.prism([(-2.3, .55), (-2.3, .8), (-1.3, 1.45), (2.2, 1.45), (2.3, 1.2), (2.3, .55)], 2.0, axis='X', bevel=.06)
    _wheels(a, (-.9, .9), (-1.4, 1.35), .45, .32)
    a.part('Mast', 'Steel').box((.14, .14, 2.4), loc=(0, .8, 2.65), bevel=0)
    a.part('Sensor_head', 'Armor').box((.5, .4, .45), loc=(0, .8, 4.0), bevel=.05, seg=1)
    t = a.pivot('Turret', (0, -.3, 1.45))
    a.part('Ring', 'Armor', t).cyl(.35, .12, loc=(0, 0, .06), seg=10, bevel=.02)
    gun = a.part('MG', 'Steel', t)
    gun.box((.14, .4, .16), loc=(0, 0, .3), bevel=.02, seg=1)
    gun.cyl(.04, .8, loc=(0, -.55, .3), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -.95, .3), t)
    a.pivot('Point_exhaust', (.8, 2.2, 1.0))
    a.pivot('Point_fire', (0, 0, 1.6))
    _stripes(a, 2.6, 2.0, 1.45, y=.3)


def fibre_fpv_carrier(a):
    """A 4x4 armoured pickup with an open bed holding an FPV launch rack and two big fibre-optic cable spools;
    4.6 x 1.9 x 2.0 m."""
    body = a.part('Hull', 'Team')
    body.box((1.9, 2.0, 1.15), loc=(0, -1.2, 1.05), bevel=.07, seg=1, taper=(.95, .85))
    a.part('Bed', 'Armor').shell([(-.9, -.2), (.9, -.2), (.9, 2.3), (-.9, 2.3)], .45, .08, loc=(0, 0, .8), floor=.06)
    a.part('Glass', 'Glass').box((1.6, .05, .35), loc=(0, -2.21, 1.3), bevel=0)
    _wheels(a, (-.82, .82), (-1.5, 1.4), .42, .3)
    t = a.pivot('Turret', (0, 1.2, .95))
    rack = a.part('Rack', 'Steel', t)
    rack.box((1.2, .9, .12), loc=(0, 0, .3), rot=(.25, 0, 0), bevel=.02, seg=1)
    drones = a.part('Drones', 'Undercarriage', t)
    for x in (-.35, .35):
        drones.box((.45, .45, .12), loc=(x, 0, .42), rot=(.25, 0, 0), bevel=.03, seg=1)
    a.pivot('Muzzle_main', (0, -.4, .6), t)
    spools = a.part('Spools', 'Hazard')
    for x in (-.55, .55):
        spools.cyl(.3, .35, loc=(x, 1.95, 1.2), rot=ACROSS, seg=12, bevel=.03)
    a.pivot('Point_exhaust', (.7, 2.3, .7))
    a.pivot('Point_fire', (0, 0, 1.6))


def interceptor_drone_vehicle(a):
    """A 4x4 tactical truck (JLTV look) with a hexagonal multi-tube box launcher for interceptor drones and a small
    radar panel; 5.0 x 2.0 x 2.4 m."""
    body = a.part('Hull', 'Team')
    body.box((2.0, 2.1, 1.2), loc=(0, -1.35, 1.1), bevel=.08, seg=1, taper=(.95, .85))
    a.part('Bed', 'Armor').box((2.0, 2.6, .6), loc=(0, 1.1, .85), bevel=.05, seg=1)
    a.part('Glass', 'Glass').box((1.7, .05, .35), loc=(0, -2.41, 1.35), bevel=0)
    _wheels(a, (-.86, .86), (-1.6, 1.55), .45, .32)
    t = a.pivot('Turret', (0, 1.2, 1.15))
    pitch = .5
    a.part('Launcher', 'Team', t).cyl(.6, 1.6, loc=(0, 0, .75), rot=(R90 - pitch, 0, 0), seg=6, bevel=.04)
    front = (0, -.82 * math.cos(pitch), .75 + .82 * math.sin(pitch))
    _tube_faces(a, t, front, pitch, [(0, 0)] + [(math.cos(k * math.tau / 6) * .35, math.sin(k * math.tau / 6) * .35) for k in range(6)], .12)
    a.pivot('Muzzle_main', front, t)
    a.part('Radar_panel', 'Armor').box((.7, .1, .5), loc=(.7, -.3, 1.95), bevel=.02, seg=1)
    a.pivot('Point_exhaust', (.8, 2.4, .8))
    a.pivot('Point_fire', (0, 0, 1.7))


# ------------------------------------------------------------------------------------------------ aircraft (0.4 x real)

def _jet(a, length, span, fuselage_r, tail=2, nose=1.6, intake=.0, wing_y=.1, wing_sweep=.35, tail_cant=.35, dark=False):
    """A fighter-shaped airframe: a lofted fuselage, swept wings, tailplanes, one or two fins; returns the half span."""
    skin = 'Armor' if dark else 'Team'
    body = a.part('Fuselage', skin)
    half = length / 2
    body.cyl(fuselage_r, length - nose, loc=(0, nose / 2, 0), rot=FORWARD, seg=10, bevel=.04)
    body.cyl(fuselage_r, nose, loc=(0, -half + nose / 2, 0), rot=FORWARD, seg=10, r2=fuselage_r * .2, bevel=.02)
    a.part('Canopy', 'Glass').sphere((fuselage_r * .6, nose * .45, fuselage_r * .5), loc=(0, -half + nose * 1.1, fuselage_r * .65), seg=10, rings=6)
    wings = a.part('Wings', skin)
    root = length * .38
    wings.prism([(0, -root / 2 + wing_y), (span / 2, root * .1 + wing_y + wing_sweep * span / 2), (span / 2, root * .32 + wing_y + wing_sweep * span / 2),
                 (0, root / 2 + wing_y)], .1, axis='Z', bevel=.02, seg=1)
    wings.prism([(0, -root / 2 + wing_y), (-span / 2, root * .1 + wing_y + wing_sweep * span / 2), (-span / 2, root * .32 + wing_y + wing_sweep * span / 2),
                 (0, root / 2 + wing_y)], .1, axis='Z', bevel=.02, seg=1)
    tails = a.part('Tails', skin)
    for s in (-1, 1):
        tails.prism([(0, half - .9), (s * span * .2, half - .2), (s * span * .2, half + .05), (0, half + .05)], .08, axis='Z', bevel=.01, seg=1)
    fins = a.part('Fins', 'Team')
    for k in range(tail):
        x = 0 if tail == 1 else (k - .5) * fuselage_r * 1.4
        fins.box((.08, 1.0, length * .1), loc=(x, half - .5, fuselage_r + length * .05), rot=(-.3, (k - .5) * 2 * tail_cant if tail > 1 else 0, 0), bevel=.01, seg=1, taper=(1, .5))
    return span / 2


def glide_bomber(a):
    """A Su-34 look: a Flanker planform with a broad flat nose and side-by-side cockpit, twin tails, two big glide bombs
    with UMPK wings under the wings; 9.3 x 5.9 x 2.4 m."""
    _jet(a, 9.3, 5.9, .42, nose=2.0, wing_y=.4)
    a.part('Nose_flat', 'Team').box((.9, 1.4, .3), loc=(0, -3.6, .05), bevel=.08, seg=1, taper=(.8, .9))
    for s in (-1, 1):
        a.part('Nacelles', 'Armor').cyl(.32, 3.5, loc=(s * .55, 1.2, -.15), rot=FORWARD, seg=10, bevel=.03)
    bombs = a.part('Bombs', 'Armor')
    kits = a.part('Bomb_wings', 'Steel')
    for s in (-1, 1):
        bombs.cyl(.16, 1.3, loc=(s * 1.6, .3, -.4), rot=FORWARD, seg=10, bevel=.03)
        kits.box((1.2, .25, .04), loc=(s * 1.6, .2, -.25), bevel=0)
    a.pivot('Muzzle_missile', (0, .3, -.5))


def recon_jet(a):
    """An SR-71 look: a very long chined fuselage, a slender delta wing, two big engine nacelles at mid-wing with
    inward-canted tails; dark gunmetal, the side's colour only in accents; 13.1 x 6.8 x 2.2 m."""
    body = a.part('Fuselage', 'Armor')
    body.cyl(.35, 9.0, loc=(0, .8, 0), rot=FORWARD, seg=10, bevel=.03)
    body.cyl(.35, 3.2, loc=(0, -5.2, 0), rot=FORWARD, seg=10, r2=.05, bevel=.02)
    body.prism([(0, -6.2), (.75, -2.0), (.8, 3.0), (-.8, 3.0), (-.75, -2.0)], .12, axis='Z', bevel=.02, seg=1)  # chines
    wing = a.part('Wings', 'Armor')
    wing.prism([(0, -1.5), (3.4, 4.8), (3.4, 5.6), (-3.4, 5.6), (-3.4, 4.8)], .12, axis='Z', bevel=.02, seg=1)
    for s in (-1, 1):
        a.part('Nacelles', 'Armor').cyl(.42, 5.2, loc=(s * 1.8, 3.2, 0), rot=FORWARD, seg=10, bevel=.03)
        a.part('Spikes', 'Steel').cyl(.25, .8, loc=(s * 1.8, .25, 0), rot=FORWARD, seg=8, r2=.02, bevel=0)
        a.part('Fins', 'Team').box((.08, 1.3, 1.1), loc=(s * 1.6, 5.0, .7), rot=(-.25, -s * .3, 0), bevel=.01, seg=1, taper=(1, .5))
    a.part('Canopy', 'Glass').sphere((.22, .6, .2), loc=(0, -3.4, .3), seg=8, rings=5)
    a.pivot('Muzzle_main', (0, -6.5, 0))


def interceptor_jet(a):
    """A MiG-31 look: big boxy intakes, a long straight fuselage, twin tails, four long R-37 missiles under the
    fuselage; 9.1 x 5.4 x 2.5 m."""
    _jet(a, 9.1, 5.4, .38, nose=1.8, wing_y=.6, wing_sweep=.25, tail_cant=.1)
    intakes = a.part('Intakes', 'Armor')
    for s in (-1, 1):
        intakes.box((.55, 3.2, .6), loc=(s * .6, 0, 0), bevel=.05, seg=1)
    missiles = a.part('Missiles', 'Medical')
    for x in (-.35, .35):
        for y in (-.6, 1.0):
            missiles.cyl(.08, 1.5, loc=(x, y, -.45), rot=FORWARD, seg=8, bevel=.02)
    # The def is 9.1 x 5.4 x 2.5 m (balance.json modelSize); the model stood 1.87 m (DECISIONS 27 wave 2 pass B): tall
    # twin outboard fins on the tailplanes, as on the MiG-31, bring it to 2.1 m.
    fins = a.part('Fins', 'Team')
    for s in (-1, 1):
        fins.box((.08, 1.3, 1.6), loc=(s * 1.08, 9.1 / 2 - .75, .8), rot=(-.25, s * .1, 0), bevel=.01, seg=1, taper=(1, .5))
    a.pivot('Muzzle_missile', (0, -.2, -.55))


# name: (builder, Asset options).
BUILDERS = {
    'heavy_flak_tower': (heavy_flak_tower, dict(ao_distance=.6, ao_strength=.7, grime_height=.4)),
    'at_gun_emplacement': (at_gun_emplacement, dict(ao_distance=.5, grime_height=.4)),
    'blast_wall': (blast_wall, dict(ao_distance=.5, grime_height=.6)),
    'inflatable_decoy': (inflatable_decoy, dict(ao_distance=.5, grime_height=.3)),
    'fire_control_centre': (fire_control_centre, dict(ao_distance=.6, grime_height=.4)),
    'searchlight': (searchlight, dict(ao_distance=.4, grime_height=.3)),
    'barrage_balloon': (barrage_balloon, dict(ao_distance=.6, grime_height=.3)),
    'visual_jammer': (visual_jammer, dict(ao_distance=.6, ao_strength=.7, grime_height=.4)),
    'troop_shelter': (troop_shelter, dict(ao_distance=.6, grime_height=.5)),
    'flare_tower': (flare_tower, dict(ao_distance=.5, grime_height=.3)),
    'laser_ad_station': (laser_ad_station, dict(ao_distance=.6, ao_strength=.7, grime_height=.4)),
    'aa_gun_tower': (aa_gun_tower, dict(ao_distance=.5, grime_height=.4)),
    'aa_gun_vehicle': (aa_gun_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'shorad_vehicle': (shorad_vehicle, dict(ao_distance=.4, grime_height=.4)),
    'microwave_vehicle': (microwave_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'nlos_atgm_vehicle': (nlos_atgm_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'radar_atgm_vehicle': (radar_atgm_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'recoilless_jeep': (recoilless_jeep, dict(ao_distance=.3, grime_height=.3)),
    'airborne_vehicle': (airborne_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'airborne_vehicle_chute': (airborne_vehicle_chute, dict(ao_distance=.5, ground=False)),
    'wheeled_howitzer': (wheeled_howitzer, dict(ao_distance=.5, grime_height=.5)),
    'sp_mortar': (sp_mortar, dict(ao_distance=.5, grime_height=.5)),
    'radar_scout': (radar_scout, dict(ao_distance=.4, grime_height=.4)),
    'fibre_fpv_carrier': (fibre_fpv_carrier, dict(ao_distance=.4, grime_height=.4)),
    'interceptor_drone_vehicle': (interceptor_drone_vehicle, dict(ao_distance=.4, grime_height=.4)),
    'glide_bomber': (glide_bomber, dict(ao_distance=.35, ground=False)),
    'recon_jet': (recon_jet, dict(ao_distance=.35, ground=False)),
    'interceptor_jet': (interceptor_jet, dict(ao_distance=.35, ground=False)),
}

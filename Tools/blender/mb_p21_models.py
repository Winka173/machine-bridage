"""Machine Brigade play-test 4 (DECISIONS 19R): the bunker vehicle redrawn with a real dug-in mode, and
redraws of the vehicles that read too alike at the default zoom.

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z). Team / TeamGlow parts are
recoloured per army at runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * bunker_vehicle: a self-entrenching fighting vehicle (Strv 103 dozer blade, engineer-vehicle hull) with a
    low wide turret, 105 mm L7 (`Main_cannon`, `Muzzle_main`) and a coaxial MG (`Muzzle_mg`). Every part that
    moves when it digs in is a `Deploy_*` pivot (the runtime keeps them apart from the merged hull and animates
    them in VehicleView.Deploy):
      - `Deploy_blade`: the dozer blade on its push arms, hinged on the hull sides; digging in lowers it
        (Unity localEulerAngles.x + 6): its edge bites into the scrape.
      - `Deploy_plate_l` / `Deploy_plate_r`: armoured side plates, hinged along the sponson edges and stowed
        standing up beside the turret; they fold out and down over the spoil bank (Unity z +95 / -95).
      - `Deploy_spade_l` / `Deploy_spade_r`: rear earth spades, stowed up, swung back and down (Unity x -125).
      - `Deploy_riser`: the turret's telescopic mount; `Turret` rides on it. It rises 0.75 m once dug in.
      - `Deploy_berm`: the spoil bank and sandbags round the scrape, exported at 1 % scale (so a card, an
        impostor or a moving vehicle never shows it); the view grows it as the hull sinks 0.8 m into the scrape.
    Dug in, the hull top is 0.9 m above the ground inside a 0.3-0.5 m bank and the turret sits on 0.8 m of
    exposed mount: the silhouette is lower than on the move (the side plates no longer stand up) and only the turret shows above
    the bank.

Look-alike redraws (the card renders side by side at the default zoom's size):
  * light_tank (was a small copy of main_battle_tank's layout): an amphibious light tank on the PT-76 / ZBD-05
    pattern with an unmanned 57 mm module (AU-220M lineage) set well forward, a boat bow with a trim vane
    folded on the glacis, twin water-jet housings at the stern and a tall panoramic sight mast. Same pivots
    (`Turret`, `Muzzle_main`, `Muzzle_coax`) as before; its _hd variant is the same builder with detail=True.
  * titan_tank (read as heavy_tank's twin): a land battleship. The twin-140 mm main turret moves 1 m forward and
    a superfiring rear turret (`Mount_mg`, free yaw) carries the heavy machine gun on a raised plinth, so it is
    the only tank with two turrets.
  * laser_tank (tank_destroyer's hull with a fat barrel): the tube gives way to a beam director, a ball head
    on a yoke with a short telescope and a round window (`Main_cannon*`, `Muzzle_main` at the window), and a power and cooling
    module (generator, radiator banks) fills the rear deck.
  * shield_carrier (command_vehicle's twin 8x8): the emitter stands on a tall lattice mast with a glowing halo
    ring, capacitor drums line the roof, so it reads as the one tall vehicle among the 8x8s.
"""
import math

import mb_detail as hd
import mb_p17_temp
import mb_vehicles2
from mb_air import ACROSS, FORWARD, R90
from mb_siege import lattice
from mb_vehicles import (_access_panel, _antenna, _barrel, _cable, _coax, _eyes, _filler, _flank, _glacis,
                         _glacis_bolts, _grille_frame, _hatch, _headlight, _jerrycans, _periscopes, _phone, _pick,
                         _pintle, _shackle, _shovel, _skirt, _smoke, _sponson_section, _stowage_bin, _taillight,
                         _vent, tracks)

# Deployed pose, shared with VehicleView.Deploy (model units; the vehicle is drawn at its def's scale). Play-test 5
# (DECISIONS 20V, mb_pt5_models.py) dug it in deeper: hull-down, the turret lifted less, the side plates leaning out 20 degrees.
SINK, LIFT, BERM_REST = 1.25, .55, .01


def _bunker_berm(a):
    """The spoil bank round the scrape: side banks, a high front bank the blade pushed up, a low rear
    one between the spades, lumps of earth and a course of sandbags on the front and the corners."""
    p = a.pivot('Deploy_berm', (0, 0, 0))
    dirt = a.part('Berm_dirt', 'Dirt', p)
    bags = a.part('Berm_bags', 'Sandbag', p)
    for s in (-1, 1):
        # Side bank: steep inside against the hull, a long slope outwards (x, z).
        dirt.prism([(s * 1.95, -.01), (s * 1.95, .28), (s * 2.3, .3), (s * 3.25, -.01)], 6.4, loc=(0, -.3, 0),
                   axis='Y', bevel=.08, seg=1)
        # Corner banks joining the sides to the front and the rear.
        dirt.box((1.4, 1.3, .5), loc=(s * 2.4, -4.2, .2), rot=(0, 0, s * .35), bevel=.2, seg=1, taper=(.6, .6))
        dirt.box((1.3, 1.1, .45), loc=(s * 2.3, 3.55, .18), rot=(0, 0, -s * .3), bevel=.2, seg=1, taper=(.6, .6))
    # Front bank (y, z): the blade's spoil, heaped just ahead of the blade.
    dirt.prism([(-4.45, -.01), (-4.45, .42), (-4.8, .5), (-5.9, -.01)], 4.4, axis='X', bevel=.1, seg=1)
    # Rear bank, low, split by the spades.
    for x in (-1.45, 0, 1.45):
        dirt.box((.95 if x else .7, 1.0, .5), loc=(x, 4.25, .2), bevel=.2, seg=1, taper=(.7, .6))
    for k, (x, y, z, r) in enumerate([(-2.9, -2.0, .12, .32), (2.95, 1.2, .1, .3), (-1.3, -5.5, .12, .35),
                                      (1.6, -5.35, .14, .4), (3.1, -3.3, .12, .28), (-3.0, 2.6, .1, .3)]):
        dirt.ico(r, loc=(x, y, z), sub=1, jitter=.25, seed=k * 1.7)
    # Sandbags: two courses on the front bank's crest, one on each front corner.
    for row, (z, n) in enumerate(((.57, 7), (.73, 6))):
        for i in range(n):
            x = (i - (n - 1) / 2) * .56
            bags.box((.52, .3, .17), loc=(x, -4.85 - row * .04, z), rot=(0, 0, .05 * ((i % 3) - 1)), bevel=.07, seg=1)
    for s in (-1, 1):
        for i in range(3):
            bags.box((.5, .3, .16), loc=(s * (2.2 + i * .05), -3.45 - i * .5, .45 - i * .03),
                     rot=(0, 0, s * (.9 + .1 * i)), bevel=.07, seg=1)


def bunker_vehicle(a):
    """Deployable bunker vehicle, 8.0 x 3.6 m on the move: a heavy tracked engineer hull with a dozer blade
    under the nose, tall armoured side plates beside a low wide turret on a telescopic mount, and rear earth
    spades. Dug in (see the module notes) it becomes a pillbox in a spoil bank."""
    tracks(a, 1.38, 7.0, .9, .3, 7, .5, belt_width=.6, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.5, 1.08, 1.7, 1.02, 1.8, 1.4)
    hull.loft([_sponson_section(-3.75, .62, 1.08, 1.12, 1.0, 1.72, 1.2), _sponson_section(-2.6, *body),
               _sponson_section(3.3, *body), _sponson_section(3.55, .6, 1.08, 1.62, .98, 1.75, 1.34)], bevel=.05, seg=2)
    for s in (-1, 1):
        _taillight(a, s * 1.5, 3.55, 1.25)
        _headlight(a, s * 1.2, -3.2, 1.28)
        _hatch(a, s * .6, -2.3, 1.7, .26)
        steel.cyl(.09, .32, loc=(s * .9, 3.62, 1.35), rot=FORWARD, seg=10, bevel=.015, bseg=1)   # exhausts
        # Push-arm brackets for the blade on the hull sides.
        armor.box((.18, .5, .36), loc=(s * 1.62, -2.55, .86), bevel=.03, seg=1)
    gy, gz, grot = _glacis((-3.75, 1.12), (-2.6, 1.7), .5, .02)
    for xx in (-.9, -.45, 0, .45, .9):                                                    # spare track links
        deck.box((.36, .26, .05), loc=(xx, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    _periscopes(a, [(dx, -2.62, 1.7, 0) for dx in (-.2, 0, .2)])
    deck.grille(1.6, 1.0, loc=(0, 2.55, 1.71), rot=(-R90, 0, 0), slats=7, depth=.08, thickness=.04)
    # The mount's well in the roof: a thick collar round the telescopic column.
    steel.cyl(.78, .09, loc=(0, -.3, 1.705), seg=24, bevel=.03)
    armor.cyl(.66, .06, loc=(0, -.3, 1.765), seg=24, bevel=.02)

    # Side plates, hinged along the sponson edges, standing up beside the turret on the move.
    for s, name in ((1, 'Deploy_plate_l'), (-1, 'Deploy_plate_r')):
        for y in (-2.1, -.2, 1.7):
            steel.box((.16, .34, .16), loc=(s * 1.8, y, 1.12), bevel=.02, seg=1)                  # hinge lugs
        p = a.pivot(name, (s * 1.86, 0, 1.14))
        a.part(f'{name}_slab', 'Team', p).box((.1, 5.3, 1.02), loc=(s * .06, -.2, .53), bevel=.03, seg=1,
                                             taper=(1, .96))
        ribs = a.part(f'{name}_ribs', 'Armor', p)
        for y in (-2.3, -1.1, .1, 1.3, 2.3):
            ribs.box((.07, .12, .9), loc=(s * .14, y - .2, .5), bevel=0)
        ribs.box((.07, 5.0, .1), loc=(s * .14, -.2, .98), bevel=0)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, 5.1, loc=(0, -.2, 0), rot=FORWARD, seg=10, bevel=0)

    # Dozer blade on two push arms under the nose, raised clear of the ground on the move.
    p = a.pivot('Deploy_blade', (0, -2.55, .86))
    arms = a.part('Deploy_blade_arms', 'Steel', p)
    for s in (-1, 1):
        arms.limb((s * 1.62, 0, 0), (s * 1.62, -1.75, -.18), .14, .16, bevel=.02, seg=1)
        arms.limb((s * 1.0, -.4, -.35), (s * 1.3, -1.7, .05), .1, .1, bevel=0, seg=1)          # rams
    blade = a.part('Deploy_blade_plate', 'Armor', p)
    # Curved moldboard (y, z), 3.7 m wide, its cutting edge 0.35 m above the ground on the move.
    board = [(-1.72, -.52), (-1.95, -.5), (-2.02, -.25), (-2.04, .05), (-1.98, .35), (-1.86, .52), (-1.76, .5),
             (-1.84, .3), (-1.88, .05), (-1.86, -.22), (-1.74, -.42)]
    blade.prism(board, 3.7, axis='X', bevel=.02, seg=1)
    edge = a.part('Deploy_blade_edge', 'Steel', p)
    edge.box((3.66, .1, .09), loc=(0, -1.99, -.54), bevel=.01, seg=1)
    for xx in (-1.2, -.4, .4, 1.2):
        a.part('Deploy_blade_ribs', 'Armor', p).box((.1, .14, .8), loc=(xx, -1.72, -.02), bevel=0)

    # Rear earth spades, stowed standing up behind the tail plate; each pivot is its hinge axis (X).
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        x = s * .8
        for dx in (-.38, .38):
            armor.box((.16, .2, .22), loc=(x + dx, 3.6, .72), bevel=.02, seg=1)             # hinge lugs
        p = a.pivot(name, (x, 3.66, .72))
        a.part(f'{name}_blade', 'Armor', p).box((.9, .08, 1.15), loc=(0, .1, .62), bevel=.02, seg=1)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .56, rot=ACROSS, seg=10, bevel=0)
        ribs = a.part(f'{name}_ribs', 'Armor', p)
        for dx in (-.3, .3):
            ribs.box((.06, .1, .9), loc=(dx, .17, .55), bevel=0)
        teeth = a.part(f'{name}_teeth', 'Steel', p)
        for dx in (-.33, -.11, .11, .33):
            teeth.box((.14, .06, .16), loc=(dx, .1, 1.24), bevel=0, taper=(.4, 1))

    # The telescopic mount: two column stages under the turret, hidden in the hull on the move.
    r = a.pivot('Deploy_riser', (0, -.3, 1.72))
    column = a.part('Deploy_riser_column', 'Steel', r)
    column.cyl(.6, .9, loc=(0, 0, -.43), seg=20, bevel=.02)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.63, .08, loc=(0, 0, -.22), seg=20, bevel=0)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.63, .08, loc=(0, 0, -.6), seg=20, bevel=0)

    t = a.pivot('Turret', (0, 0, .04), r)
    outline = [(-.8, -1.35), (.8, -1.35), (1.4, -.8), (1.45, .9), (1.1, 1.45), (-1.1, 1.45), (-1.45, .9),
               (-1.4, -.8)]
    a.part('Turret_body', 'Team', t).prism(outline, .62, loc=(0, 0, .31), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((.9, .42, .54), loc=(0, -1.42, .34), bevel=.035, taper=(.9, .9))                # mantlet
    tarm.box((2.0, .4, .36), loc=(0, 1.45, .3), bevel=.03, seg=1)                          # bustle bin
    for s in (-1, 1):                                                                     # cheek blocks
        tarm.box((.5, .8, .4), loc=(s * 1.02, -.9, .3), rot=(0, 0, -s * .55), bevel=.03, seg=1, taper=(.9, .85))
    tsteel.box((.22, .26, .22), loc=(.7, -.6, .72), bevel=.03)                             # sight
    a.part('Sight', 'Glass', t).box((.16, .04, .1), loc=(.7, -.74, .74), bevel=.01, seg=1)
    _hatch(a, -.55, .3, .62, .3, parent=t)
    tarm.cyl(.24, .12, loc=(-.55, .3, .66), seg=14, bevel=.02, bseg=1)                      # cupola ring
    for s in (-1, 1):
        _smoke(a, tsteel, 1.0, -.7, .66, s, count=3, gap=.08, r=.045, depth=.16)
    _antenna(a, t, .95, 1.0, .62, 1.2)
    tip = _barrel(a, t, start_y=-1.6, length=4.0, radius=.075, height=.36, brake=(.24, .3, .22),
                  sleeve=(.4, .5, .12), seg=12, style='collar', bands=(.2, .7, .85))
    a.pivot('Muzzle_main', tip, t)
    mg = a.part('MG_port', 'Steel', t)
    mg.box((.12, .3, .12), loc=(.55, -1.4, .3), bevel=.02, seg=1)
    mg.cyl(.025, .4, loc=(.55, -1.75, .3), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.036, .08, loc=(.55, -1.94, .3), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (.55, -1.99, .3), t)

    _bunker_berm(a)
    # Exported at 1 %: hidden on the move, in the cards and in the impostor atlas (the view grows it).
    a.pivots['Deploy_berm'].scale = (BERM_REST,) * 3


# ----------------------------------------------------------------------------- look-alike redraws
def light_tank(a, detail=False):
    """Amphibious light tank, 4.9 x 2.7 m: a boat-bowed hull with a trim vane folded on the glacis, stern
    water-jet housings, four-panel skirts and fender stowage, and an unmanned 57 mm gun module set well
    forward (a faceted flat turret, ammunition bustle, panoramic sight mast, a long thin gun with a big
    pepperpot brake and a coaxial MG)."""
    hd.mark(a, detail)
    tracks(a, 1.02, 4.4, .72, .25, 5, .42, belt_width=.5, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    # Boat bow: a long shallow lower glacis under a short upper one.
    front, brow = (-2.3, .82), (-1.55, 1.12)
    hull.prism([(-1.9, .5), (-2.45, .72), front, brow, (1.95, 1.12), (2.25, .92), (2.25, .5)], 1.62, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.3, -2.05, 1.95, .6, 1.0, 4, thick=.1)
        _headlight(a, s * .55, -2.3, .72)
        steel.box((.14, .16, .1), loc=(s * .22, -2.46, .64), bevel=.02, seg=1)             # tow hooks
        _taillight(a, s * .64, 2.25, .8)
        # Water-jet housing with its round outlet and a steering flap.
        armor.box((.42, .3, .38), loc=(s * .45, 2.39, .7), bevel=.04, seg=1)
        steel.cyl(.13, .06, loc=(s * .45, 2.56, .7), rot=FORWARD, seg=12, bevel=0)
        a.part('Jet_flaps', 'Undercarriage').box((.3, .04, .3), loc=(s * .45, 2.61, .7), bevel=.01, seg=1)
    # Trim vane folded flat on the glacis: a wide ribbed board on two hinges.
    gy, gz, grot = _glacis(front, brow, .5, .045)
    a.part('Trim_vane', 'Team').box((1.9, .64, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.015, seg=1)
    vane_ribs = a.part('Trim_vane_ribs', 'Armor')
    for dx in (-.7, -.23, .23, .7):
        vane_ribs.box((.06, .6, .04), loc=(dx, gy, gz + .03), rot=(grot, 0, 0), bevel=0)
    for dx in (-.8, .8):
        steel.cyl(.035, .16, loc=(dx, gy - .3, gz - .02), rot=ACROSS, seg=8, bevel=0)
    # Fender stowage: bin and tools on the left, jerrycans and the tow cable on the right.
    _stowage_bin(a, (-1.03, 1.3, .85), (.36, .9, .26), latch_side=0)
    _shovel(a, (-1.1, -.95, .875), length=1.0)
    _pick(a, (-1.04, .1, .875), length=.85)
    _jerrycans(a, (1.03, 1.4, .85), 3)
    _cable(a, [(1.0, -1.85, .89), (1.0, -.4, .89), (.98, .7, .89), (.92, 1.02, .89)])
    # Driver's hatch and vision blocks just behind the vane, left of the turret's nose.
    _hatch(a, -.5, -1.45, 1.11, .22)
    _periscopes(a, [(-.5 + dx, -1.64, 1.1, 0) for dx in (-.14, 0, .14)])
    # Engine deck: framed grille and a rear stowage box.
    deck.grille(1.0, .6, loc=(0, 1.35, 1.13), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
    _grille_frame(a, 0, 1.35, 1.11, 1.0, .6)
    _stowage_bin(a, (0, 1.82, 1.11), (1.1, .2, .17), latch_side=0)
    steel.cyl(.72, .14, loc=(0, -.45, 1.17), seg=24, bevel=.03)

    t = a.pivot('Turret', (0, -.45, 1.24))
    module = a.part('Turret_body', 'Team', t)
    outline = [(-.82, .72), (.82, .72), (.96, .2), (.86, -.52), (.46, -.84), (-.46, -.84), (-.86, -.52), (-.96, .2)]
    module.prism(outline, .42, loc=(0, 0, .21), axis='Z', bevel=.04, taper=.8)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.5, .52, .36), loc=(0, .96, .2), bevel=.04, taper=(.92, .85))                # ammunition bustle
    tarm.box((.36, .3, .34), loc=(0, -.86, .22), bevel=.04)                                  # gun cradle
    # Panoramic sight on a mast (rear left) and the gunner's sight box (front right).
    tsteel.cyl(.06, .5, loc=(-.55, .35, .66), seg=10, bevel=0)
    tsteel.box((.26, .26, .2), loc=(-.55, .35, .98), bevel=.04, seg=1)
    sight = a.part('Sight', 'Glass', t)
    sight.box((.18, .03, .1), loc=(-.55, .215, .99), bevel=.008, seg=1)
    tsteel.box((.3, .34, .22), loc=(.52, -.42, .5), bevel=.035, seg=1)
    sight.box((.2, .03, .12), loc=(.52, -.595, .51), bevel=.008, seg=1)
    tsteel.box((.12, .12, .08), loc=(.2, .45, .44), bevel=.02, seg=1)                         # laser warner
    for s in (-1, 1):
        _smoke(a, tsteel, .78, -.45, .3, s, count=3)
    _hatch(a, .35, .3, .42, .16, parent=t, seg=10)                                           # maintenance hatch
    _antenna(a, t, .7, .85, .38, .9)
    tip = _barrel(a, t, start_y=-.95, length=2.9, radius=.055, height=.22, brake=(.22, .36, .22),
                  sleeve=(.12, .45, .09), style='baffle', bands=(.4, .75))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .26, -.86, .22, length=.36, housing=.3)
    if detail:
        for u in (.1, .9):
            _glacis_bolts(a, front, brow, u, -.62, .62, 7)
        for s in (-1, 1):
            _shackle(a, s * .22, -2.48, .59)
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * .81, -1.3, 1.03), (s * .81, 1.75, 1.03), 8,
                         rot=hd.side_rot(s), r=.016, h=.022)
            _filler(a, s * .66, .72, 1.12)
        _eyes(a, [(s * .62, y, 1.12, 0) for s in (-1, 1) for y in (-1.42, 1.9)])
        _access_panel(a, 0, .78, 1.12, .7, .24, nx=4, ny=2)
        _pintle(a, 0, 2.25, .55)
        _phone(a, .9, 2.25, .62)
        _eyes(a, [(-.62, .55, .42, 0), (.62, .55, .42, 0), (.7, -.35, .42, -.6)], parent=t, size=.08)
        for dx in (-.1, .1):
            for dz in (-.1, .1):
                hd.bolt(a.part('Turret_bolts', 'Steel', t), (dx, -1.015, .22 + dz), hd.FRONT, r=.014, h=.02)
        _vent(a, -.1, .3, .42, parent=t, r=.08)
        hd.bolt_line(a.part('Turret_bolts', 'Steel', t), (-.62, 1.225, .22), (.62, 1.225, .22), 6, rot=hd.BACK,
                     r=.014, h=.02)


def titan_tank(a):
    """Titan: the super tank (mb_vehicles2) turned land battleship. Its twin-140 mm turret moves 1 m forward;
    a superfiring rear turret on a raised plinth, the heavy machine gun's free mount (`Mount_mg`), stands over
    the engine deck in place of the main turret's remote weapon station."""
    mb_vehicles2.titan_tank(a)
    a.pivots['Turret'].location.y = -.55
    steel = a.part('Steel', 'Steel')
    hull = a.part('Hull', 'Team')
    # The turret ring's new place (the old ring's rear shows under the plinth's skirt).
    steel.cyl(1.35, .1, loc=(0, -.55, 1.915), seg=16, bevel=.02, bseg=1)
    # Raised plinth over the engine deck, with louvres on its flanks.
    # It starts behind the main turret's sweep (2.8 m round its pivot), so the turret turns clear of it.
    hull.prism([(-1.2, 2.35), (1.2, 2.35), (1.35, 2.7), (1.35, 3.95), (1.05, 4.3), (-1.05, 4.3), (-1.35, 3.95),
                (-1.35, 2.7)], .5, loc=(0, 0, 2.15), axis='Z', bevel=.05, taper=.9)
    for s in (-1, 1):
        for k in range(4):
            a.part('Louvres', 'Undercarriage').box((.04, .26, .22), loc=(s * 1.29, 2.75 + k * .36, 2.12), bevel=0)
    steel.cyl(.8, .08, loc=(0, 3.3, 2.43), seg=18, bevel=.02, bseg=1)                      # rear ring
    m = a.pivots['Mount_mg']
    m.parent = None
    m.location = (0, 3.3, 2.66)
    # The rear turret round the remote gun: a faceted shell, a mantlet and a sight, all on Mount_mg.
    shell = a.part('Rear_turret', 'Team', 'Mount_mg')
    shell.prism([(-.45, -.75), (.45, -.75), (.78, -.3), (.78, .55), (.5, .8), (-.5, .8), (-.78, .55), (-.78, -.3)],
                .46, loc=(0, 0, -.1), axis='Z', bevel=.04, taper=.85)
    rear = a.part('Rear_turret_armor', 'Armor', 'Mount_mg')
    rear.box((.5, .2, .3), loc=(0, -.8, -.05), bevel=.03, seg=1)
    rear.box((.3, .22, .18), loc=(-.45, .1, .22), bevel=.03, seg=1)


def laser_tank(a):
    """Laser tank: tank_destroyer's sponson hull and running gear under a low turret whose weapon is a beam
    director, a ball head on a yoke with a short telescope (every `Main_cannon*` part elevates with it),
    and a power and cooling module on the rear deck: a generator box, two radiator banks with fans and
    conduits to the turret."""
    tracks(a, 1.22, 6.2, .8, .28, 7, .45, belt_width=.56, wheel_seg=12, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    body = (.46, .96, 1.36, .95, 1.52, 1.16)
    hull.loft([_sponson_section(-3.5, .62, .96, 1.1, .9, 1.4, 1.24), _sponson_section(-2.1, *body),
               _sponson_section(3.25, *body), _sponson_section(3.5, .56, .96, 1.28, .92, 1.48, 1.14)], bevel=.05, seg=2)
    x, z, lean = _flank((1.52, 1.04), (1.16, 1.36), .5, .02)
    for s in (-1, 1):
        for y in (-1.4, .2):                                                              # bolt-on plates
            armor.box((.06, 1.3, .3), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.015, seg=1)
        _headlight(a, s * .75, -3.5, .86)
        _taillight(a, s * 1.05, 3.5, 1.12)
        _hatch(a, s * .55, -1.85, 1.35, .26)
        _periscopes(a, [(s * .55 + dx, -2.2, 1.35, 0) for dx in (-.12, .12)])
    steel.cyl(.95, .09, loc=(0, -.6, 1.375), seg=24, bevel=.03)                            # turret ring
    # Power and cooling module over the engine deck: generator, two radiator banks with fans.
    armor.box((2.0, 1.1, .55), loc=(0, 2.55, 1.63), bevel=.05, seg=1, taper=(.95, .92))
    deck.grille(1.7, .8, loc=(0, 2.55, 1.915), rot=(-R90, 0, 0), slats=8, depth=.06, thickness=.03)
    for s in (-1, 1):
        armor.box((.5, 1.7, .42), loc=(s * .95, 1.0, 1.57), bevel=.04, seg=1)
        for y in (.55, 1.45):
            steel.cyl(.2, .05, loc=(s * .95, y, 1.8), seg=16, bevel=0)                         # fan rings
            deck.cyl(.17, .04, loc=(s * .95, y, 1.81), seg=16, bevel=0)
        steel.cyl(.09, .45, loc=(s * .55, 3.55, 1.0), rot=FORWARD, seg=10, bevel=.015, bseg=1)   # exhausts
    conduits = a.part('Conduits', 'Undercarriage')
    for s in (-1, 1):
        conduits.tube([(s * .4, 2.0, 1.75), (s * .35, .9, 1.9), (s * .3, -.1, 1.55)], .06, seg=6)

    t = a.pivot('Turret', (0, -.6, 1.43))
    outline = [(-.6, -.9), (.6, -.9), (.95, -.5), (.95, .7), (.7, .95), (-.7, .95), (-.95, .7), (-.95, -.5)]
    a.part('Turret_body', 'Team', t).prism(outline, .4, loc=(0, 0, .2), axis='Z', bevel=.04, taper=.86)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):                                                                      # yoke arms
        tarm.box((.16, .6, .95), loc=(s * .78, -.1, .75), bevel=.03, seg=1, taper=(1, .8))
    tsteel.box((.2, .24, .2), loc=(-.62, .62, .5), bevel=.02, seg=1)                      # tracking sensor
    a.part('Sight', 'Glass', t).box((.14, .04, .1), loc=(-.62, .49, .52), bevel=.01, seg=1)
    _antenna(a, t, .7, .7, .4, 1.0)
    # The beam director: ball head, aperture hood and window, cooling ribs round the ball.
    zc = 1.0
    # The ball and its telescope elevate; the trunnion pins stay in the yoke.
    a.part('Main_cannon_head', 'Armor', t).sphere(.6, loc=(0, -.1, zc), seg=20, rings=12)
    a.part('Main_cannon', 'Team', t).cyl(.22, 1.5, loc=(0, -1.25, zc), rot=FORWARD, seg=16, bevel=.02)
    a.part('Director_trunnions', 'Steel', t).cyl(.13, 1.42, loc=(0, -.1, zc), rot=ACROSS, seg=12, bevel=0)
    ribs = a.part('Main_cannon_ribs', 'Steel', t)
    for k in (-1, 0, 1):
        ribs.torus(.6 * math.cos(k * .45) + .005, .03, loc=(0, -.1 + .6 * math.sin(k * .45), zc), rot=(R90, 0, 0),
                   seg=20, ring=5)
    for y in (-.9, -1.45):
        ribs.cyl(.25, .06, loc=(0, y, zc), rot=FORWARD, seg=16, bevel=0)
    y0 = -1.95
    a.part('Main_cannon_hood', 'Team', t).lathe([(.2, -.08), (.29, 0), (.29, .2), (.26, .23), (.23, .23),
                                                 (.23, .1)], loc=(0, y0, zc), rot=FORWARD, seg=16)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.22, .03, loc=(0, y0 - .08, zc), rot=FORWARD, seg=16, bevel=0)
    a.pivot('Muzzle_main', (0, y0 - .25, zc), t)
    # Coaxial MG on the turret face (fixed: it does not elevate with the director).
    mg = a.part('MG_port', 'Steel', t)
    mg.box((.12, .3, .12), loc=(.45, -.95, .22), bevel=.02, seg=1)
    mg.cyl(.025, .4, loc=(.45, -1.3, .22), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.036, .08, loc=(.45, -1.49, .22), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (.45, -1.54, .22), t)


def shield_carrier(a):
    """Shield carrier: the prompt-17 8x8 (mb_p17_temp) with its emitter on a tall lattice mast (5.6 m), a
    glowing halo ring below the dish and capacitor drums along the roof, so it stands out among the 8x8s."""
    mb_p17_temp.shield_carrier(a)
    a.pivots['Emitter'].location = (0, 2.0, 5.3)
    steel = a.part('Steel', 'Steel')
    lattice(steel, 0, 2.0, 2.5, 5.26, .4, .16, 5, leg=.1, brace=.03)
    steel.cyl(.22, .08, loc=(0, 2.0, 5.28), seg=12, bevel=0)
    a.part('Halo', 'TeamGlow').torus(.95, .05, loc=(0, 2.0, 4.6), seg=28, ring=6)
    for k in range(4):
        u = k * math.tau / 4 + math.pi / 4
        steel.limb((.2 * math.cos(u), 2.0 + .2 * math.sin(u), 4.6), (.93 * math.cos(u), 2.0 + .93 * math.sin(u), 4.6),
                   .04, .04, bevel=0)
    drums = a.part('Capacitors', 'Armor')
    caps = a.part('Capacitor_caps', 'TeamGlow')
    for s in (-1, 1):
        for y in (.3, 3.2):
            drums.cyl(.26, .5, loc=(s * .75, y, 2.26), seg=14, bevel=.03)
            caps.cyl(.2, .03, loc=(s * .75, y, 2.52), seg=14, bevel=0)


BUILDERS = {
    'bunker_vehicle': (bunker_vehicle, dict(ao_distance=.7, grime_height=.6)),
    'light_tank': (light_tank, dict(ao_distance=.55, grime_height=.5)),
    'titan_tank': (titan_tank, dict(ao_distance=.65, grime_height=.6)),
    'laser_tank': (laser_tank, dict(ao_distance=.6, grime_height=.55)),
    'shield_carrier': (shield_carrier, dict(ao_distance=.6, grime_height=.55)),
}

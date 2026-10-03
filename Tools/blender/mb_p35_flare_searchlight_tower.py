"""Prompt 35 wave 11 (lane C): the flare and searchlight tower rebuilt from scratch (spec: Tools/blender/specs/flare_searchlight_tower.json).

A field illumination post (the def's illum_flare weapon, modelSize 3.6 x 3.6 x 5.0 m; the Soviet 60 cm searchlight
and the 2B? flare mortar packs of border posts as the reference): four splayed steel legs on concrete footings with
X bracing and a ladder, the chequer-plate deck at 3.4 m with a steel parapet and a kick rail, a lean-to shelter over
the rear of the deck; on the turntable (`Turret`) the yoke with the 60 cm searchlight drum (glowing lens, louvred
door, cooling fins, handles) and on top of the drum the six-tube flare pack raised 35 degrees (`Muzzle_main` at its
mouths); the beacon, a whip on the mast with the team pennant, flare boxes on the deck, the cable down a leg to the
generator box at the foot, sandbags round two footings.

Runtime nodes kept where they were: `Turret` (0, 0, 3.62), `Muzzle_main` (0, -.64, 4.55); old mesh names kept
(`Launcher_body`, `Launcher_bands`, `Tubes`, `Beacon`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
DECK = 3.4
FOOT, TOP = 1.55, .98        # the legs' half spread at the ground and under the deck


def _legs(a):
    base = a.part('Base', 'Concrete')
    legs = a.part('Legs', 'Steel')
    br = a.part('Braces', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.extrude(base, [(-.24, -.24), (.24, -.24), (.24, .24), (-.24, .24)], .3,
                      loc=(sx * FOOT, sy * FOOT, .15), axis='Z', chamfer=.04, corner=.04, taper=(.8, .8))
            legs.limb((sx * FOOT, sy * FOOT, .28), (sx * TOP, sy * TOP, DECK - .08), .1, .1, bevel=0)
            K.rivet_line(a.part('Kit_bolts', 'Steel'), (sx * FOOT, sy * (FOOT - .14), .3),
                         (sx * FOOT, sy * (FOOT + .14), .3), (0, 0, 1), pitch=.28, r=.026, h=.03)

    def leg(sx, sy, z):
        f = (z - .28) / (DECK - .36)
        h = FOOT + (TOP - FOOT) * f
        return (sx * h, sy * h, z)
    for z0, z1 in ((.5, 1.95), (1.95, 3.3)):
        for sx, sy, tx, ty in ((-1, -1, 1, -1), (-1, 1, 1, 1), (-1, -1, -1, 1), (1, -1, 1, 1)):
            br.limb(leg(sx, sy, z0), leg(tx, ty, z1), .05, .03, bevel=0)
            br.limb(leg(tx, ty, z0), leg(sx, sy, z1), .05, .03, bevel=0)
        for sx, sy, tx, ty in ((-1, -1, 1, -1), (-1, 1, 1, 1), (-1, -1, -1, 1), (1, -1, 1, 1)):
            br.limb(leg(sx, sy, z1), leg(tx, ty, z1), .07, .05, bevel=0)
    # The ladder up the rear face to a hatch in the deck.
    K.ladder(a.part('Ladders', 'Steel'), (.0, FOOT - .05, .3), (.0, TOP + .08, DECK), width=.42, step=.3)
    # Sandbags round two footings, the generator box and the cable up a leg.
    for sx, sy in ((1, -1), (-1, 1)):
        x, y = sx * FOOT, sy * FOOT
        K.sandbag_run(a, [(x + sx * .05, y - sy * .4, 0), (x - sx * .42, y - sy * .4, 0)], courses=2,
                      bag=(.42, .24, .13), seed=sx + 3, lean=True)
    gen = a.part('Generator', 'Team')
    k.block(gen, (.7, .45, .5), loc=(-.9, -.1, .27), chamfer=.04)
    k.extrude(gen, [(-.25, 0), (.25, 0), (.18, .1), (-.18, .1)], .7, loc=(-.9, -.1, .52), axis='X', chamfer=.01)
    K.grille(a, (-.9, -.33, .3), .5, .25, facing=(0, -1, 0), slats=5)
    K.exhaust(a, (-1.1, .0, .62), r=.03, length=.28, direction=(0, 0, 1), muffler=False)
    a.part('Kit_cables', 'Rubber').tube([(-.6, -.1, .3), (-.2, .3, .05), (TOP + .3, TOP + .3, .4),
                                         (TOP + .1, TOP + .1, DECK - .2)], .022, seg=4)


def _deck(a):
    deck = a.part('Tower_deck', 'Steel')
    W = TOP + .32
    k.block(deck, (2 * W, 2 * W, .1), loc=(0, 0, DECK - .1), chamfer=.02)
    pl = a.part('Deck_plate', 'MetalSheet')
    for i in range(5):
        for j in range(5):
            if (i + j) % 2:
                pl.box((.3, .06, .012), loc=(-.8 + i * .4, -.8 + j * .4, DECK + .006), rot=(0, 0, .785), bevel=0)
    # Parapet: steel plates on three sides, a rail with a gap at the ladder.
    par = a.part('Parapet', 'Armor')
    hgt = .75
    for sx, sy, rot, ln in ((0, -1, 0, 2 * W), (-1, 0, R90, 2 * W), (1, 0, R90, 2 * W)):
        loc = (sx * (W - .03), sy * (W - .03), DECK + hgt / 2)
        k.block(par, (ln, .05, hgt), loc=(loc[0], loc[1], DECK + hgt / 2), rot=(0, 0, rot), chamfer=.015)
    for s in (-1, 1):
        k.block(par, (W - .3, .05, hgt), loc=(s * (W + .3) / 2, W - .03, DECK + hgt / 2), chamfer=.015)
    # Stiffeners on the parapet's outer faces.
    st = a.part('Parapet_ribs', 'Armor')
    for i in range(5):
        x = -W + .2 + i * (2 * W - .4) / 4
        st.box((.05, .04, hgt - .1), loc=(x, -W - .02, DECK + hgt / 2), bevel=0)
        st.box((.04, .05, hgt - .1), loc=(-W - .02, x, DECK + hgt / 2), bevel=0)
        st.box((.04, .05, hgt - .1), loc=(W + .02, x, DECK + hgt / 2), bevel=0)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        rail.limb((s * .15, W, DECK + hgt), (s * .15, W, DECK + hgt + .2), .04, .04, bevel=0)
    # The lean-to shelter over the rear half: two posts, a sloped roof, a canvas side.
    roof = a.part('Roof', 'Corrugated')
    posts = a.part('Shelter_posts', 'Steel')
    for s in (-1, 1):
        posts.limb((s * (W - .08), W - .08, DECK), (s * (W - .08), W - .08, DECK + 1.25), .06, .06, bevel=0)
        posts.limb((s * (W - .08), .1, DECK + hgt), (s * (W - .08), .1, DECK + 1.45), .05, .05, bevel=0)
    k.extrude(roof, [(.0, 1.5), (W + .15, 1.28), (W + .15, 1.32), (0, 1.54)], 2 * W + .2, loc=(0, 0, DECK),
              axis='X', chamfer=0)
    a.part('Canvas_side', 'Canvas').box((.02, W - .1, .45), loc=(-W + .03, (W + .1) / 2, DECK + hgt + .25),
                                        bevel=0)
    # Mast with a whip and the pennant on the shelter's corner.
    mast = a.part('Masts', 'Steel')
    mx, my = W - .08, W - .08
    mast.cyl(.03, .3, loc=(mx, my, DECK + 1.42), seg=6, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (mx, my, DECK + 1.56), h=.3, r=.02, lean=.08)
    a.part('Pennant', 'Team').mesh([(mx, my, DECK + 1.56), (mx, my - .35, DECK + 1.5), (mx, my, DECK + 1.42),
                                    (mx + .01, my, DECK + 1.56), (mx + .01, my - .35, DECK + 1.5),
                                    (mx + .01, my, DECK + 1.42)], [(0, 1, 2), (5, 4, 3)])
    K.beacon(a, (-(W - .2), W - .25, DECK + 1.42), r=.08)
    a.part('Beacon', 'Lamp').cyl(.04, .04, loc=(-(W - .2), W - .25, DECK + 1.7), seg=6, bevel=0)
    # Flare boxes on the deck.
    cr = a.part('Ammo_boxes', 'Crate')
    for i, (x, y) in enumerate(((.6, .55), (.6, .2), (-.65, .4))):
        k.block(cr, (.42, .26, .22), loc=(x, y, DECK + .11), rot=(0, 0, .1 * i), chamfer=.015)
        a.part('Kit_handles', 'Steel').box((.03, .2, .02), loc=(x + .22, y, DECK + .12), bevel=0)
    K.periscope(a, (-.7, -W + .1, DECK + hgt), facing=(0, -1, 0), size=(.12, .1, .1))


def _light(a):
    """The turntable, the yoke, the searchlight drum, the six-tube flare pack on top."""
    t = a.pivot('Turret', (0, 0, 3.62))
    k.lathe(a.part('Turntable', 'Steel', t), [(.42, -.22), (.42, -.14), (.36, -.1), (.2, -.02), (.2, .02)],
            seg=12, worn=(1,))
    yoke = a.part('Yoke', 'Team', t)
    for s in (-1, 1):
        k.extrude(yoke, [(-.14, 0), (.14, 0), (.1, .42), (-.1, .42)], .05, loc=(s * .37, 0, 0), axis='X',
                  chamfer=.01)
    yoke.box((.8, .22, .06), loc=(0, 0, .02), bevel=0)
    zc = .32
    drum = a.part('Armor', 'Team', t)
    k.lathe(drum, [(.0, -.4), (.17, -.39), (.28, -.33), (.3, .17), (.32, .23), (.32, .28), (.27, .28)],
            loc=(0, 0, zc), rot=K.FORWARD, seg=14, worn=(3, 5))
    a.part('Lamps', 'Lamp', t).cyl(.27, .02, loc=(0, -.28, zc), rot=K.FORWARD, seg=14, bevel=0)
    door = a.part('Louvres', 'Steel', t)
    for i in range(5):
        door.box((.5, .015, .025), loc=(0, -.295, zc - .2 + i * .1), bevel=0)
    fins = a.part('Cooling_fins', 'Steel', t)
    for i in range(6):
        k.ring(fins, [(.3, 0), (.35, 0), (.35, .02), (.3, .02)], loc=(0, .1 - i * .05, zc), rot=K.FORWARD,
               seg=12)
    for s in (-1, 1):
        a.part('Trunnions', 'Steel', t).cyl(.06, .1, loc=(s * .34, 0, zc), rot=(0, R90, 0), seg=8, bevel=0)
        K.handle(a.part('Kit_handles', 'Steel', t), (s * .22, .3, zc + .15), (s * .22, .3, zc - .15), (0, 1, 0), h=.07)
    # The flare pack: six tubes in two rows, raised 35 degrees, on a bracket over the drum.
    pitch = math.radians(35)
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    base = (0, -.15, .62)
    lb = a.part('Launcher_body', 'Armor', t)
    a.part('Launcher_bracket', 'Steel', t).limb((0, .02, zc + .28), (0, -.1, .58), .14, .14, bevel=0)
    Lt = .6
    tubes = a.part('Tubes', 'Steel', t)
    for row in range(2):
        for col in range(3):
            x = (col - 1) * .13
            off = (row - .5) * .13
            p = (x, base[1] + math.sin(pitch) * off, base[2] + math.cos(pitch) * off)
            k.lathe(tubes, [(.055, 0), (.055, Lt), (.045, Lt), (.045, .05)], loc=p, rot=rot, seg=8,
                    caps=(True, False))
    k.block(lb, (.46, .32, .16), loc=(0, base[1] + .02, base[2] - .02), rot=(-pitch, 0, 0), chamfer=.02)
    bands = a.part('Launcher_bands', 'Team', t)
    for f in (.2, .45):
        c = (0, base[1] + d[1] * f * Lt * 1.0, base[2] + d[2] * f * Lt)
        bands.box((.44, .3, .04), loc=c, rot=(-pitch, 0, 0), bevel=0)
    tip = (0, base[1] + d[1] * Lt, base[2] + d[2] * Lt)
    a.pivot('Muzzle_main', (0, -.64, .93), t)
    K.soot(a, (0, -.64, 4.55), radius=.3, k=.3)
    del tip


def flare_searchlight_tower(a, detail=False):
    """The flare and searchlight tower: see the module docstring."""
    _legs(a)
    _deck(a)
    _light(a)
    K.dust(a, (0, 0, 0), radius=2.2, k=.15)
    k.clean(a)


BUILDERS = {
    'flare_searchlight_tower': (flare_searchlight_tower, dict(ao_distance=.5, grime_height=.4)),
}

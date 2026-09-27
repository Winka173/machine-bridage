"""Machine Brigade secondary weapons: the shared kit that gives single-weapon models their second,
visible weapon (called from mb_vehicles, mb_vehicles2, mb_elites, mb_support and mb_siege; the aircraft
build their stores with mb_air's kit).

Freely aimed weapons stand on a `Mount_<slot>` empty that the game yaws on its own (about local Z
only); its child `Muzzle_<slot>` sits at the barrel tip, and at rest the barrel points along -Y. Every
part under a mount is authored relative to it, in metres with +Z up. The socket that the mount turns
in stays on the parent (it bakes occlusion onto the roof it stands on; parts under a mount move, so
they receive occlusion but never cast it).

Readability at the RTS camera: machine-gun barrels are at least 7 cm across (7.4 cm here, with a
10 cm flash hider) and grenade-launcher barrels at least 12 cm (13.6 cm jackets); a cradle, an
ammunition can and a small shield make each read as a weapon from above.

Part names start with HMG, AGL or ATGM: never with a runtime pattern (Main_cannon, Muzzle, Mount_,
Tubes, Pod, Launcher, Barrel ...; see frontier_kit.RIG / RUNTIME and ModelLibrary.cs), so nothing
here recoils, elevates with a main gun or is mistaken for a pivot. Touching parts overlap or stand
at least 1 cm apart, never face to face.
"""
import math

R90 = math.pi / 2
TAU = math.tau
FORWARD = (R90, 0, 0)   # cylinder axis along Y (local +Z -> -Y)
ACROSS = (0, R90, 0)    # cylinder axis along X


def _v(p, dx=0.0, dy=0.0, dz=0.0):
    return (p[0] + dx, p[1] + dy, p[2] + dz)


def muzzle_lip(part, bore, at, r, depth=.1, seg=12):
    """Muzzle ring at the front of a barrel lying along -Y whose tip is at `at`: a lip `depth` long
    around a dark recessed bore, so the opening reads (and darkens in the baked AO) from above."""
    base = _v(at, dy=depth)                             # lathe origin; local +Z runs to -Y
    part.lathe([(r, -.03), (r, depth), (r * .6, depth), (r * .6, .02)], loc=base, rot=FORWARD, seg=seg)
    bore.cyl(r * .58, .02, loc=_v(base, dy=-.045), rot=FORWARD, seg=seg, bevel=0)


def hmg(a, loc, parent=None, post=.16, length=.9, shield=True, ammo=1, socket=True):
    """Pintle heavy machine gun (M2 / DShK lineage) on its own `Mount_mg` yaw pivot at loc (the foot of
    the pintle on the roof, relative to `parent`): a socket, the pintle post, a cradle, the receiver
    with its feed cover, rear plate and spade grips, a perforated barrel jacket, a 7.4 cm barrel and a
    dark flash hider, an ammunition can on side `ammo` (+1 right, -1 left) with its belt chute, and a
    small gun shield with side wings on two struts. `Muzzle_mg` sits at the hider's face, the
    barrel's tip `length` ahead of the receiver. Returns the pivot name."""
    if socket:
        a.part('HMG_socket', 'Armor', parent).cyl(.085, .08, loc=_v(loc, dz=.03), seg=10, bevel=0)
    m = a.pivot('Mount_mg', loc, parent)
    steel = a.part('HMG', 'Steel', m)
    cradle = a.part('HMG_cradle', 'Armor', m)
    zc = post + .13                                                        # receiver centre height
    zb = zc + .01                                                          # bore axis
    steel.cyl(.042, post - .04, loc=(0, 0, .05 + (post - .04) / 2), seg=8, bevel=0)      # pintle
    cradle.box((.2, .3, .05), loc=(0, .02, post + .02), bevel=0)                           # cradle base
    for s in (-1, 1):
        cradle.box((.03, .24, .15), loc=(s * .1, .02, post + .1), bevel=0)                 # cheeks
    steel.cyl(.028, .25, loc=(0, .06, zc - .02), rot=ACROSS, seg=6, bevel=0)             # trunnion pin
    steel.box((.15, .44, .15), loc=(0, .03, zc), bevel=.02, seg=1)                       # receiver
    cradle.box((.12, .22, .03), loc=(0, -.02, zc + .085), bevel=0)                         # feed cover
    steel.box((.12, .03, .1), loc=(0, .26, zc - .01), bevel=0)                           # rear plate
    for s in (-1, 1):
        steel.box((.03, .03, .13), loc=(s * .035, .29, zc - .02), rot=(.25, 0, 0), bevel=0)   # spade grips
    front = -.19
    tip = front - length
    steel.cyl(.05, .26, loc=(0, front - .11, zb), rot=FORWARD, seg=10, bevel=0)          # barrel jacket
    steel.cyl(.037, length - .32, loc=(0, (front - .22 + tip + .1) / 2, zb), rot=FORWARD, seg=8, bevel=0)
    a.part('HMG_hider', 'Undercarriage', m).cyl(.05, .12, loc=(0, tip + .06, zb), rot=FORWARD, seg=8, bevel=0)
    can = a.part('HMG_ammo', 'Crate', m)
    can.box((.13, .26, .18), loc=(ammo * .17, .04, zc - .04), bevel=.015, seg=1)
    cradle.box((.1, .09, .02), loc=(ammo * .125, 0, zc + .06), rot=(0, ammo * .5, 0), bevel=0)   # belt chute
    if shield:
        guard = a.part('HMG_shield', 'Armor', m)
        guard.box((.5, .035, .3), loc=(0, -.3, zc + .07), rot=(-.12, 0, 0), bevel=.012, seg=1, taper=(.84, 1))
        for s in (-1, 1):
            guard.box((.16, .03, .26), loc=(s * .3, -.25, zc + .06), rot=(-.1, 0, s * .55), bevel=0)
            steel.box((.03, .18, .03), loc=(s * .12, -.2, zc - .05), bevel=0)             # shield struts
    a.pivot('Muzzle_mg', (0, tip, zb), m)
    return m


def agl(a, loc, parent=None, post=.3, shield=.34, ammo=-1, socket=True, sight='top'):
    """40 mm automatic grenade launcher (Mk 19 / AGS lineage) on its own `Mount_gun` yaw pivot at loc (the
    foot of the pedestal, relative to `parent`): a socket, the pedestal, a cradle with cheeks, the boxy
    receiver with a steel top cover, a rear plate and spade grips, a stubby 13.6 cm barrel jacket with
    two cooling bands and a muzzle ring around a dark bore, a big ammunition can on side `ammo` (-1
    left, the usual feed side) with its chute, a ranging sight with a glass eye (on the cover,
    sight='top', or low on the side opposite the can, 'side') and a small shield `shield` tall with
    side wings (0: none). `Muzzle_gun` sits at the muzzle face. Returns the pivot name."""
    if socket:
        a.part('AGL_socket', 'Armor', parent).cyl(.1, .08, loc=_v(loc, dz=.03), seg=10, bevel=0)
    m = a.pivot('Mount_gun', loc, parent)
    body = a.part('AGL', 'Armor', m)
    steel = a.part('AGL_steel', 'Steel', m)
    dark = a.part('AGL_bands', 'Undercarriage', m)
    zc = post + .2                                                         # receiver centre height
    zb = zc - .02                                                          # bore axis
    steel.cyl(.05, post - .04, loc=(0, 0, .05 + (post - .04) / 2), seg=8, bevel=0)       # pedestal
    body.box((.3, .36, .06), loc=(0, .02, post + .02), bevel=0)                            # cradle base
    for s in (-1, 1):
        body.box((.035, .3, .2), loc=(s * .155, .02, post + .13), bevel=0)                 # cradle cheeks
    steel.cyl(.03, .38, loc=(0, .05, zc - .04), rot=ACROSS, seg=6, bevel=0)              # trunnion pin
    body.box((.24, .56, .2), loc=(0, .05, zc), bevel=.025, seg=1)                          # receiver
    steel.box((.2, .3, .035), loc=(0, 0, zc + .11), bevel=0)                             # top cover
    for s in (-1, 1):
        steel.box((.035, .035, .14), loc=(s * .07, .37, zc - .02), rot=(.25, 0, 0), bevel=0)  # spade grips
    steel.box((.2, .03, .12), loc=(0, .335, zc - .01), bevel=0)                          # rear plate
    steel.box((.12, .02, .02), loc=(0, .37, zc + .035), bevel=0)                         # trigger bar
    front = -.23
    steel.cyl(.068, .36, loc=(0, front - .16, zb), rot=FORWARD, seg=10, bevel=0)         # barrel jacket
    for y in (front - .1, front - .22):
        dark.cyl(.077, .035, loc=(0, y, zb), rot=FORWARD, seg=10, bevel=0)                # cooling bands
    tip = front - .41
    muzzle_lip(steel, a.part('AGL_bore', 'Undercarriage', m), (0, tip, zb), .076, depth=.1, seg=10)
    can = a.part('AGL_ammo', 'Crate', m)
    can.box((.2, .32, .26), loc=(ammo * .26, .06, zc - .06), bevel=.02, seg=1)
    steel.box((.07, .16, .025), loc=(ammo * .26, .06, zc + .08), bevel=0)                # can handle
    dark.box((.12, .14, .03), loc=(ammo * .15, 0, zc + .07), rot=(0, ammo * .35, 0), bevel=0)   # feed chute
    if sight:
        sx, sy, sz = (-ammo * .05, -.04, zc + .16) if sight == 'top' else (-ammo * .165, -.075, zc + .04)
        a.part('AGL_sight', 'Armor', m).box((.08, .14, .1), loc=(sx, sy, sz), bevel=0)
        a.part('AGL_sight_glass', 'Glass', m).box((.06, .02, .06), loc=(sx, sy - .075, sz + .005), bevel=0)
    if shield:
        h = shield
        zs = zc - .11 + h / 2                                              # bottom edge 11 cm under the bore
        guard = a.part('AGL_shield', 'Armor', m)
        guard.box((.56, .035, h), loc=(0, -.29, zs), rot=(-.1, 0, 0), bevel=.012, seg=1, taper=(.85, 1))
        for s in (-1, 1):
            guard.box((.18, .03, h - .04), loc=(s * .33, -.24, zs - .01), rot=(-.1, 0, s * .55), bevel=0)
            steel.box((.03, .14, .03), loc=(s * .155, -.2, zc - .08), bevel=0)            # shield struts
    a.pivot('Muzzle_gun', (0, tip, zb), m)
    return m


def atgm_tripod(a, loc, parent=None, height=.62, length=1.2, spread=.5):
    """Tripod anti-tank missile launcher (Kornet / TOW lineage) standing on loc (relative to `parent`):
    three steel legs splayed `spread` out (one back, two forward) with foot pads and a head hub; on
    `Mount_missile` at the head a cradle, a thermal sight unit with a glass eye on the left, the missile
    canister (a fat olive tube with a dark rear ring, a yellow band and a muzzle ring around a dark
    bore) and rear grips. `Muzzle_missile` sits at the canister's front face. Returns the pivot name."""
    x, y, z = loc
    legs = a.part('ATGM_tripod', 'Steel', parent)
    for k in range(3):
        ang = R90 + k * TAU / 3                                            # one leg back, two forward
        c, s = math.cos(ang), math.sin(ang)
        legs.limb((x + c * spread, y + s * spread, z + .01), (x + c * .05, y + s * .05, z + height - .06), .04, .04,
                  bevel=0)
        legs.box((.1, .1, .03), loc=(x + c * spread, y + s * spread, z + .005), rot=(0, 0, ang), bevel=0)  # feet
    legs.cyl(.07, .12, loc=(x, y, z + height - .05), seg=8, bevel=0)                    # head hub
    m = a.pivot('Mount_missile', (x, y, z + height), parent)
    cradle = a.part('ATGM_cradle', 'Steel', m)
    zt = .24                                                               # canister axis
    cradle.box((.18, .26, .05), loc=(0, .02, .03), bevel=0)
    for s in (-1, 1):
        cradle.box((.03, .22, .2), loc=(s * .105, .02, .13), bevel=0)
    tube = a.part('ATGM_tube', 'Crate', m)
    y0 = -.1                                                               # canister centre
    tube.cyl(.085, length, loc=(0, y0, zt), rot=FORWARD, seg=12, bevel=0)
    rings = a.part('ATGM_rings', 'Armor', m)
    rings.cyl(.097, .06, loc=(0, y0 + length / 2 - .02, zt), rot=FORWARD, seg=12, bevel=0)
    a.part('ATGM_band', 'Hazard', m).cyl(.098, .05, loc=(0, y0 - length * .22, zt), rot=FORWARD, seg=12, bevel=0)
    tip = y0 - length / 2 - .04
    muzzle_lip(rings, a.part('ATGM_bore', 'Undercarriage', m), (0, tip, zt), .1, depth=.08, seg=12)
    sight = a.part('ATGM_sight', 'Armor', m)
    sight.box((.16, .3, .2), loc=(-.2, .08, zt + .03), bevel=.02, seg=1)
    sight.box((.2, .08, .04), loc=(-.1, .12, zt - .02), bevel=0)                          # sight bracket
    a.part('ATGM_sight_glass', 'Glass', m).box((.12, .02, .1), loc=(-.2, -.075, zt + .05), bevel=0)
    for s in (-1, 1):
        cradle.box((.03, .03, .14), loc=(s * .06, .44, zt - .1), rot=(.3, 0, 0), bevel=0)   # grips
    a.pivot('Muzzle_missile', (0, tip, zt), m)
    return m

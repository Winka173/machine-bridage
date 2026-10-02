"""Prompt 33 L6: biome dressing on the V2 kit (DECISIONS "Prompt 33 L1 / L6").

Decoration only: the view draws these with GPU instancing round and on the battlefield (Surroundings.Dressing.cs,
Resources/Data/map_dressing.json); they have no collider, never block a route or a line of sight and never reach the
simulation. Eight biomes, four or five objects each, all `dress_<biome>_<thing>` (glb_check.py's scenery class). Lean
by design: they are drawn by the hundred, so one to three parts (one instanced draw per part and cell) and a few
hundred triangles at most; the `_far` objects are the HLOD stand-ins drawn in the outer half of the ring (tens of
triangles). Existing kit materials only.

    blender --background --python Tools/blender/build_assets.py -- dress_
"""
import math
import random

import mb_kit27 as k

R90 = math.pi / 2


def _blobs(part, items, sub=2, jitter=.22):
    for i, (x, y, z, r) in enumerate(items):
        part.ico(r, loc=(x, y, z), sub=sub, jitter=jitter, seed=i * 1.7 + x)


def _log(part, a, b, r, seg=7):
    """A lying cylinder from a to b (ground points, z = r)."""
    (x0, y0), (x1, y1) = a, b
    length = math.hypot(x1 - x0, y1 - y0)
    yaw = math.atan2(y1 - y0, x1 - x0)
    part.cyl(r, length, loc=((x0 + x1) / 2, (y0 + y1) / 2, r), rot=(0, R90, yaw), seg=seg, bevel=0)


def _blades(part, n, radius, height, seed, lean=.35, w=.06):
    """A tuft of thin three-sided blades (grass, reeds)."""
    rng = random.Random(seed)
    for i in range(n):
        ang = rng.uniform(0, math.tau)
        rr = rng.uniform(0, radius)
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        h = height * rng.uniform(.6, 1.1)
        tilt = rng.uniform(.1, lean)
        part.cyl(w, h, loc=(x + math.cos(ang) * h * tilt * .5, y + math.sin(ang) * h * tilt * .5, h / 2),
                 rot=(math.sin(ang) * -tilt, math.cos(ang) * tilt, 0), seg=3, r2=.004, bevel=0)


# ============================================================================= temperate
def temperate_shrub(a):
    """Flowering hedge shrub (1.6 x 1.2 m, 1.1 m): two leafy clumps and a light crown."""
    leaves = a.part('Leaves', 'Foliage', flat=True)
    _blobs(leaves, ((-.35, 0, .42, (.62, .55, .48)), (.3, .1, .38, (.55, .5, .42))))
    a.part('Crown', 'FoliageLight', flat=True).ico((.42, .38, .3), loc=(0, .05, .78), sub=2, jitter=.25, seed=3.3)


def temperate_haybales(a):
    """Three round hay bales left in a meadow (1.5 m across)."""
    hay = a.part('Bales', 'Sandbag')
    for x, y, yaw in ((-.9, -.3, .2), (.85, -.2, -.4), (0, .9, 1.1)):
        hay.cyl(.75, 1.2, loc=(x, y, .75), rot=(0, R90, yaw), seg=10, bevel=0)


def temperate_stump(a):
    """A sawn stump and the fallen trunk beside it, a grass tuft at its foot."""
    wood = a.part('Wood', 'Bark')
    wood.cyl(.32, .5, loc=(0, 0, .25), seg=8, r2=.28, bevel=0)
    _log(wood, (.4, -.3), (2.6, .4), .24)
    a.part('Grass', 'Grass').ico((.3, .3, .16), loc=(-.3, .3, .06), sub=0, jitter=.2, seed=1.1)


def temperate_wildflowers(a):
    """A patch of meadow flowers and grass (2 m), knee high."""
    _blades(a.part('Grass', 'FoliageLight'), 9, .9, .55, 33, w=.05)
    heads = a.part('Flowers', 'PlasterOchre', flat=True)
    rng = random.Random(7)
    for _ in range(6):
        ang, rr = rng.uniform(0, math.tau), rng.uniform(.1, .8)
        heads.ico(.08, loc=(rr * math.cos(ang), rr * math.sin(ang), .5), sub=0)


def temperate_tree_far(a):
    """HLOD stand-in for the broadleaf woods in the far ring: one trunk, one faceted crown (about 7 m)."""
    a.part('Trunk', 'Bark').cyl(.22, 2.6, loc=(0, 0, 1.3), seg=5, r2=.16, bevel=0)
    a.part('Crown', 'Foliage', flat=True).ico((2.1, 2.0, 2.6), loc=(0, 0, 4.4), sub=0, jitter=.12, seed=2.0)


# ============================================================================= desert
def desert_scrub(a):
    """Grey-green saltbush (1.4 m) on a sand hummock."""
    _blobs(a.part('Bush', 'FoliageDark', flat=True), ((-.25, 0, .35, (.5, .45, .35)), (.28, .12, .3, (.42, .4, .3)),
                                                      (0, -.25, .28, (.35, .32, .26))), sub=0)
    a.part('Hummock', 'Sandstone', flat=True).ico((.9, .8, .18), loc=(0, 0, 0), sub=0, jitter=.1, seed=4.0)


def desert_hoodoo(a):
    """Sandstone hoodoo (4.5 m): a weathered pillar with a dark cap rock."""
    stone = a.part('Pillar', 'Sandstone', flat=True)
    for i, (z, r) in enumerate(((.6, (1.1, .95, .8)), (1.8, (.75, .7, .75)), (2.9, (.55, .5, .7)))):
        stone.ico(r, loc=(.05 * i, -.04 * i, z), sub=2, jitter=.28, seed=i + 5.1)
    a.part('Cap', 'SandstoneDark', flat=True).ico((.95, .85, .35), loc=(.1, -.05, 3.75), sub=2, jitter=.3, seed=9.2)


def desert_barrel_cacti(a):
    """A cluster of three ribbed barrel cacti (to 0.9 m)."""
    body = a.part('Cacti', 'Foliage')
    for x, y, h, r in ((0, 0, .9, .32), (.55, .2, .6, .24), (-.35, .45, .45, .2)):
        k.lathe(body, [(r * .7, 0), (r, h * .2), (r, h * .7), (r * .6, h * .95), (.02, h)], loc=(x, y, 0), seg=8)
    a.part('Blooms', 'BarrelRed', flat=True).ico(.07, loc=(0, 0, .92), sub=0)


def desert_bones(a):
    """Bleached remains of a dead tree half buried in sand: two limbs and a root plate."""
    wood = a.part('Wood', 'BarkWhite')
    wood.limb((0, 0, 0), (1.9, .3, .55), .2, .18, bevel=0)
    wood.limb((1.1, .15, .3), (1.6, -.6, 1.1), .1, .1, bevel=0)
    a.part('Sand', 'Sandstone', flat=True).ico((.7, .6, .2), loc=(0, 0, 0), sub=0, jitter=.15, seed=2.2)


def desert_far(a):
    """HLOD stand-in for the far desert: a low sandstone outcrop and a scrub clump."""
    a.part('Rock', 'SandstoneDark', flat=True).ico((2.4, 1.9, 1.3), loc=(0, 0, .5), sub=0, jitter=.2, seed=1.3)
    a.part('Scrub', 'FoliageDark', flat=True).ico((.9, .8, .6), loc=(2.0, .9, .3), sub=0, jitter=.2, seed=6.1)


# ============================================================================= snow
def snow_drift(a):
    """A wind-sculpted snow drift (4 x 2 m, 0.9 m)."""
    a.part('Drift', 'Snow', flat=True).ico((2.1, 1.1, .9), loc=(0, 0, 0), sub=2, jitter=.18, seed=2.4)


def snow_ice_rock(a):
    """A frost-shattered boulder with snow lying on top."""
    a.part('Rock', 'Rock', flat=True).ico((1.0, .85, .7), loc=(0, 0, .45), sub=2, jitter=.3, seed=3.7)
    a.part('Cap', 'SnowCap', flat=True).ico((.85, .7, .25), loc=(.05, 0, 1.02), sub=0, jitter=.2, seed=1.9)


def snow_log(a):
    """A fallen pine trunk under a crust of snow, a broken stub at one end."""
    _log(a.part('Log', 'LogWood'), (-1.8, 0), (1.8, .3), .26)
    a.part('Snow', 'Snow').box((3.5, .4, .14), loc=(0, .15, .54), rot=(0, 0, .083), bevel=0)
    a.part('Stub', 'LogWood').cyl(.18, .5, loc=(1.6, .5, .25), seg=6, bevel=0)


def snow_pine_far(a):
    """HLOD stand-in for the far snow forest: two snowy tiers on a short trunk (about 8 m)."""
    a.part('Trunk', 'Bark').cyl(.2, 1.4, loc=(0, 0, .7), seg=5, bevel=0)
    tiers = a.part('Tiers', 'FoliageDark', flat=True)
    tiers.cyl(2.0, 3.8, loc=(0, 0, 3.0), seg=6, r2=.6, bevel=0)
    tiers.cyl(1.3, 3.2, loc=(0, 0, 5.8), seg=6, r2=.01, bevel=0)
    a.part('Snow', 'SnowCap', flat=True).cyl(1.05, .9, loc=(0, 0, 5.0), seg=6, r2=.55, bevel=0)


# ============================================================================= harbour / industrial
def harbor_pallets(a):
    """Stacked shipping pallets and crates on the quay (2.6 x 1.4 m)."""
    wood = a.part('Pallets', 'Wood')
    for i in range(3):
        wood.box((1.2, 1.0, .14), loc=(-.65, 0, .07 + i * .16), rot=(0, 0, .05 * i), bevel=0)
    crate = a.part('Crates', 'Crate')
    crate.box((1.1, 1.0, .9), loc=(.65, 0, .45), bevel=0)
    crate.box((.8, .7, .6), loc=(-.6, .05, .78), rot=(0, 0, .3), bevel=0)


def harbor_drums(a):
    """A cluster of oil drums, one lying on its side."""
    drums = a.part('Drums', 'BarrelRed')
    for x, y in ((0, 0), (.62, .1), (.25, .58)):
        k.lathe(drums, [(.27, 0), (.29, .04), (.29, .84), (.27, .88)], loc=(x, y, 0), seg=8)
    a.part('Rusted', 'Rust').cyl(.29, .88, loc=(-.5, -.55, .29), rot=(0, R90, .4), seg=8, bevel=0)


def harbor_pipes(a):
    """Spare pipe sections stacked on two timber sleepers (5 m)."""
    a.part('Sleepers', 'Wood').box((.25, 1.8, .2), loc=(-1.6, 0, .1), bevel=0).box((.25, 1.8, .2), loc=(1.6, 0, .1), bevel=0)
    pipes = a.part('Pipes', 'Pipe')
    for y, z in ((-.5, .5), (0, .5), (.5, .5), (-.25, .93)):
        pipes.cyl(.25, 5.0, loc=(0, y, z), rot=(0, R90, 0), seg=8, bevel=0)


def harbor_bollards(a):
    """A short run of quay bollards with a slack mooring rope (4 m)."""
    iron = a.part('Bollards', 'Undercarriage')
    for x in (-1.8, 0, 1.8):
        k.lathe(iron, [(.22, 0), (.18, .3), (.16, .5), (.26, .58), (.24, .64), (.01, .66)], loc=(x, 0, 0), seg=8)
    a.part('Rope', 'Canvas').tube([(-1.8, 0, .45), (-.9, .1, .15), (0, 0, .45)], .04, seg=4, caps=False)


def harbor_shed_far(a):
    """HLOD stand-in for the far docks and works: a long shed with a pitched roof (16 x 9 m)."""
    a.part('Walls', 'Concrete').box((16, 9, 5), loc=(0, 0, 2.5), bevel=0)
    a.part('Roof', 'Corrugated').prism([(-4.7, 5), (4.7, 5), (0, 7.2)], 16.4, axis='X', bevel=0)


# ============================================================================= jungle
def jungle_palm_small(a):
    """Young oil palm (3.5 m): a curved trunk and a crown of drooping fronds."""
    a.part('Trunk', 'Bark').tube([(0, 0, 0), (.15, 0, 1.4), (.42, .05, 2.8)], .14, seg=6, caps=False)
    fronds = a.part('Fronds', 'Foliage')
    top = (.42, .05, 2.85)
    for i in range(6):
        ang = i * math.tau / 6 + .3
        tip = (top[0] + math.cos(ang) * 1.7, top[1] + math.sin(ang) * 1.7, top[2] - .7)
        mid = (top[0] + math.cos(ang) * .9, top[1] + math.sin(ang) * .9, top[2] + .15)
        fronds.tube([top, mid, tip], .16, seg=3, caps=False)


def jungle_banana(a):
    """Wild banana clump (2.4 m): three stems with broad paddle leaves."""
    stems = a.part('Stems', 'FoliageLight')
    leaves = a.part('Leaves', 'Foliage')
    for i, (x, y, h) in enumerate(((0, 0, 1.6), (.4, .25, 1.2), (-.3, .35, 1.0))):
        stems.cyl(.1, h, loc=(x, y, h / 2), seg=5, bevel=0)
        for j in range(2):
            ang = i * 2.1 + j * math.pi + .4
            leaves.box((1.3, .42, .03), loc=(x + math.cos(ang) * .6, y + math.sin(ang) * .6, h + .1),
                       rot=(0, -.45, ang), bevel=0)


def jungle_fern(a):
    """Tree fern crown at knee height (2 m across): eight arching fronds round a stub."""
    a.part('Stub', 'Bark').cyl(.14, .5, loc=(0, 0, .25), seg=5, bevel=0)
    fronds = a.part('Fronds', 'FoliageDark')
    for i in range(8):
        ang = i * math.tau / 8
        fronds.tube([(0, 0, .5), (math.cos(ang) * .55, math.sin(ang) * .55, .8), (math.cos(ang) * 1.0, math.sin(ang) * 1.0, .35)],
                    .12, seg=3, caps=False)


def jungle_vine_rock(a):
    """A mossy boulder overgrown with creepers."""
    a.part('Rock', 'Rock', flat=True).ico((1.1, .9, .8), loc=(0, 0, .5), sub=2, jitter=.3, seed=4.4)
    _blobs(a.part('Moss', 'Foliage', flat=True), ((.2, .1, 1.05, (.7, .55, .25)), (-.6, -.3, .55, (.35, .4, .35))), sub=0)


def jungle_tree_far(a):
    """HLOD stand-in for the far rainforest: a tall emergent trunk and two layered crowns (about 12 m)."""
    a.part('Trunk', 'Bark').cyl(.3, 7.5, loc=(0, 0, 3.75), seg=5, r2=.2, bevel=0)
    crown = a.part('Crown', 'FoliageDark', flat=True)
    crown.ico((3.0, 2.8, 1.5), loc=(0, 0, 8.2), sub=0, jitter=.15, seed=1.4)
    crown.ico((2.2, 2.0, 1.2), loc=(.6, -.3, 9.6), sub=0, jitter=.15, seed=3.8)


# ============================================================================= volcanic
def volcanic_cinder_cone(a):
    """A small spatter cone (3 m across) with a dull glow in its throat."""
    k.lathe(a.part('Cone', 'Charred'), [(1.6, 0), (1.2, .5), (.55, 1.05), (.4, 1.0), (.3, .7)], seg=9)
    a.part('Glow', 'LavaGlow').cyl(.32, .05, loc=(0, 0, .72), seg=7, bevel=0)


def volcanic_ash_rocks(a):
    """Obsidian blocks half sunk in ash."""
    stone = a.part('Obsidian', 'Obsidian', flat=True)
    stone.ico((.8, .6, .55), loc=(0, 0, .3), sub=2, jitter=.35, seed=5.5)
    stone.ico((.45, .4, .35), loc=(.9, .4, .15), sub=0, jitter=.3, seed=2.5)
    a.part('Ash', 'Charred', flat=True).ico((1.5, 1.2, .16), loc=(.3, .1, 0), sub=0, jitter=.15, seed=7.1)


def volcanic_snag(a):
    """A burnt-out tree snag (5 m), two stubs of branches."""
    wood = a.part('Snag', 'Charred')
    wood.cyl(.26, 4.8, loc=(0, 0, 2.4), seg=6, r2=.08, bevel=0)
    wood.limb((0, 0, 2.6), (1.0, .3, 3.5), .12, .12, bevel=0)
    wood.limb((0, 0, 3.4), (-.7, -.2, 4.0), .09, .09, bevel=0)


def volcanic_far(a):
    """HLOD stand-in for the far lava fields: a basalt hump with a glowing seam."""
    a.part('Basalt', 'Obsidian', flat=True).ico((2.6, 2.0, 1.1), loc=(0, 0, .3), sub=0, jitter=.2, seed=3.1)
    a.part('Seam', 'LavaGlow').box((2.2, .18, .08), loc=(0, 0, 1.05), rot=(0, 0, .5), bevel=0)


# ============================================================================= urban
def urban_rubble(a):
    """A heap of broken concrete slabs and bricks with bent rebar (3 m)."""
    slab = a.part('Slabs', 'Concrete', flat=True)
    rng = random.Random(41)
    for i in range(4):
        slab.box((rng.uniform(.8, 1.4), rng.uniform(.6, 1.0), .18), loc=(rng.uniform(-.8, .8), rng.uniform(-.6, .6), .15 + i * .12),
                 rot=(rng.uniform(-.4, .4), rng.uniform(-.4, .4), rng.uniform(0, 3)), bevel=0)
    a.part('Bricks', 'Brick', flat=True).ico((.9, .7, .35), loc=(.3, -.3, .1), sub=0, jitter=.3, seed=2.8)
    a.part('Rebar', 'Rust').tube([(-.4, .2, .4), (-.2, .3, 1.1), (.2, .1, 1.3)], .025, seg=3, caps=False)


def urban_planter(a):
    """A concrete street planter with a clipped shrub (1.6 x 1.6 m)."""
    a.part('Planter', 'Concrete').box((1.6, 1.6, .55), loc=(0, 0, .275), bevel=0)
    a.part('Shrub', 'Foliage', flat=True).ico((.7, .7, .55), loc=(0, 0, .95), sub=2, jitter=.2, seed=1.6)


def urban_billboard(a):
    """A roadside billboard on two steel legs (6 m wide, 6 m tall)."""
    legs = a.part('Legs', 'Steel')
    for x in (-1.8, 1.8):
        legs.box((.22, .22, 3.6), loc=(x, 0, 1.8), bevel=0)
    a.part('Board', 'PlasterBlue').box((6.0, .2, 2.6), loc=(0, 0, 4.8), bevel=0)
    a.part('Frame', 'Undercarriage').box((6.2, .25, .14), loc=(0, 0, 3.45), bevel=0)


def urban_kiosk(a):
    """A shuttered street kiosk (2.4 x 1.8 m) with an awning."""
    a.part('Body', 'PlasterOchre').box((2.4, 1.8, 2.4), loc=(0, 0, 1.2), bevel=0)
    a.part('Shutter', 'MetalSheet').box((2.0, .05, 1.3), loc=(0, -.92, 1.15), bevel=0)
    a.part('Awning', 'WoodRed').prism([(-.95, 2.6), (.95, 2.6), (.95, 2.45), (-1.25, 2.2)], 2.6, axis='X', bevel=0)


def urban_block_far(a):
    """HLOD stand-in for the far city: a mid-rise block with a lit window band and a roof plant box (20 x 16 m)."""
    a.part('Block', 'Concrete').box((20, 16, 18), loc=(0, 0, 9), bevel=0)
    a.part('Windows', 'Lamp').box((20.1, 16.1, 1.2), loc=(0, 0, 12), bevel=0)
    a.part('Plant', 'MetalSheet').box((6, 5, 2), loc=(3, 2, 19), bevel=0)


# ============================================================================= coast
def coast_dune_grass(a):
    """Marram grass on a sand hummock (1.8 m)."""
    _blades(a.part('Grass', 'FoliageLight'), 11, .7, .9, 12, lean=.45, w=.05)
    a.part('Sand', 'Sandstone', flat=True).ico((.95, .85, .2), loc=(0, 0, 0), sub=0, jitter=.12, seed=3.3)


def coast_driftwood(a):
    """Two bleached driftwood logs washed up crossways (3.5 m)."""
    wood = a.part('Driftwood', 'BarkWhite')
    _log(wood, (-1.7, -.2), (1.6, .4), .2, seg=6)
    _log(wood, (-.4, -1.0), (.5, 1.1), .14, seg=6)


def coast_rowboat(a):
    """A small wooden rowboat drawn up on the beach, tilted on its keel (4 m)."""
    hull = a.part('Hull', 'WoodRed')
    hull.shell([(-2.0, 0), (-1.4, -.7), (1.2, -.75), (2.0, 0), (1.2, .75), (-1.4, .7)], .6, .06, loc=(0, 0, .08),
               rot=(.18, 0, 0), taper=.8, floor=.06, bevel=0)
    a.part('Thwart', 'Wood').box((.25, 1.3, .06), loc=(.1, 0, .5), rot=(.18, 0, 0), bevel=0)


def coast_buoy(a):
    """A red channel buoy riding the swell (1.2 m across, 2.2 m)."""
    k.lathe(a.part('Buoy', 'ContainerRed'), [(.01, -.4), (.6, -.2), (.6, .3), (.25, .5), (.18, 1.8), (.01, 1.85)], seg=8)
    a.part('Band', 'SafetyStripe').cyl(.62, .15, loc=(0, 0, .1), seg=8, bevel=0)


def coast_island_far(a):
    """A distant wooded islet for the sea horizon (40 x 25 m)."""
    a.part('Rock', 'Rock', flat=True).ico((20, 13, 6), loc=(0, 0, -1.5), sub=2, jitter=.25, seed=5.9)
    a.part('Woods', 'FoliageDark', flat=True).ico((13, 8, 5), loc=(-3, 1, 3.5), sub=2, jitter=.3, seed=2.6)


def _gen(fn, ao=.8):
    def run(a):
        fn(a)
        k.clean(a)
    return run, dict(ao_distance=.8, grime_height=.3, ao_strength=ao)


BUILDERS = {
    'dress_temperate_shrub': _gen(temperate_shrub),
    'dress_temperate_haybales': _gen(temperate_haybales),
    'dress_temperate_stump': _gen(temperate_stump),
    'dress_temperate_wildflowers': _gen(temperate_wildflowers, .6),
    'dress_temperate_tree_far': _gen(temperate_tree_far, .5),
    'dress_desert_scrub': _gen(desert_scrub),
    'dress_desert_hoodoo': _gen(desert_hoodoo),
    'dress_desert_barrel_cacti': _gen(desert_barrel_cacti),
    'dress_desert_bones': _gen(desert_bones),
    'dress_desert_far': _gen(desert_far, .5),
    'dress_snow_drift': _gen(snow_drift, .5),
    'dress_snow_ice_rock': _gen(snow_ice_rock),
    'dress_snow_log': _gen(snow_log),
    'dress_snow_pine_far': _gen(snow_pine_far, .5),
    'dress_harbor_pallets': _gen(harbor_pallets),
    'dress_harbor_drums': _gen(harbor_drums),
    'dress_harbor_pipes': _gen(harbor_pipes),
    'dress_harbor_bollards': _gen(harbor_bollards),
    'dress_harbor_shed_far': _gen(harbor_shed_far, .5),
    'dress_jungle_palm_small': _gen(jungle_palm_small),
    'dress_jungle_banana': _gen(jungle_banana),
    'dress_jungle_fern': _gen(jungle_fern),
    'dress_jungle_vine_rock': _gen(jungle_vine_rock),
    'dress_jungle_tree_far': _gen(jungle_tree_far, .5),
    'dress_volcanic_cinder_cone': _gen(volcanic_cinder_cone),
    'dress_volcanic_ash_rocks': _gen(volcanic_ash_rocks),
    'dress_volcanic_snag': _gen(volcanic_snag),
    'dress_volcanic_far': _gen(volcanic_far, .5),
    'dress_urban_rubble': _gen(urban_rubble),
    'dress_urban_planter': _gen(urban_planter),
    'dress_urban_billboard': _gen(urban_billboard),
    'dress_urban_kiosk': _gen(urban_kiosk),
    'dress_urban_block_far': _gen(urban_block_far, .5),
    'dress_coast_dune_grass': _gen(coast_dune_grass, .6),
    'dress_coast_driftwood': _gen(coast_driftwood),
    'dress_coast_rowboat': _gen(coast_rowboat),
    'dress_coast_buoy': _gen(coast_buoy),
    'dress_coast_island_far': _gen(coast_island_far, .5),
}

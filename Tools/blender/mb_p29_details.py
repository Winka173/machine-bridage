"""Prompt 29 5.5: small details for the round-2 self-defence systems, built from the V2 kit (mb_kit27 / mb_parts27).

Written in a cloud session without Blender: not built, not validated. The local session calls these from each model's
builder (the wave builders mb_p27_*.py, or the model's own builder for older models), places them on the hull, rebuilds
with build_assets.py, validates and renders the cards. Parts keep the Part_* / Mount_* naming and the Armor / Team /
TeamGlow materials; every part sits at least 1 cm off the faces it rests on (CLAUDE.md: coplanar faces z-fight).

- Flares (D6): a row of dispenser tubes on the rear fuselage or tail boom, mouths pointing down and out to both sides;
  a big aircraft gets two rows (the "angel wings" burst comes from the effect, see FLARE_EFFECT).
- APS (D7): a small sensor block and two launcher cassettes on the turret roof; interception draws a short beam and a
  small burst (APS_EFFECT, the game's existing intercept event).
"""
import mb_kit27 as k

# The models that change (manifest bundles B2-FLR-* with charges > 0, B2-APS-*), with how many tube rows / cassettes.
FLARE_MODELS = {
    "scout_heli": 1, "heavy_lift_helicopter": 2, "light_attack_heli": 1, "prop_attack_plane": 1, "aerial_tanker": 2,
    "attack_helicopter": 1, "fighter_jet": 1, "interceptor_jet": 1, "stealth_fighter": 1, "swarm_carrier": 2,
    "twin_rotor_gunship": 2, "gunship_heli": 1, "glide_bomber": 2, "attack_jet": 1, "heavy_bomber": 2, "sky_gunship": 2,
}
APS_MODELS = {"next_gen_tank": 2, "titan_tank": 2, "main_battle_tank": 0}  # 0: Trophy retrofit, drawn only when fitted (gear art)
FLARE_EFFECT = "flare_burst: 2 x 4 bright points fanning down and out, big aircraft both rows at once (angel wings)"
APS_EFFECT = "aps_intercept: a 0.1 s tracer from the cassette to the round, a small flash at the meeting point"


def flare_tubes(a, parent, x, y, z, s, count=4, gap=.06, r=.03, depth=.12, seg=8):
    """One row of flare dispenser tubes on side s (+1 right, -1 left) at (x, y, z), pointing down and out. The nodes are
    `Flares` / `Flares_glow`, deliberately not `Part_*`: the runtime reads `Part_<letters>` as a separate part."""
    part = a.part('Flares', 'Armor', parent)
    k.block(part, (r * 2.6, (count - 1) * gap + r * 3, .04), loc=(s * x, y + (count - 1) * gap / 2, z + r * 1.2), chamfer=0)
    h = depth / 2
    for i in range(count):
        k.lathe(part, [(r, -h), (r * 1.08, h), (r * .7, h), (r * .7, h - .03), (0, h - .03)],
                loc=(s * x, y + i * gap, z), rot=(2.4, 0, s * .5), seg=seg, worn=(1,))
    glow = a.part('Flares_glow', 'TeamGlow', parent)
    for i in range(count):
        k.lathe(glow, [(r * .6, 0), (0, .002)], loc=(s * x, y + i * gap, z - h + .012), rot=(2.4, 0, s * .5), seg=min(seg, 6))


def aps_cluster(a, parent, x, y, z, cassettes=2):
    """A sensor block with two radar panels and launcher cassettes on a turret roof at (x, y, z)."""
    part = a.part('Part_aps', 'Armor', parent)
    k.block(part, (.32, .22, .14), loc=(x, y, z + .08), chamfer=.02)
    team = a.part('Part_aps_panels', 'Team', parent)
    for s in (-1, 1):
        k.block(team, (.012, .18, .1), loc=(x + s * .172, y, z + .09), chamfer=0)
    for i in range(cassettes):
        s = -1 if i % 2 == 0 else 1
        k.block(part, (.16, .26, .1), loc=(x + s * .32, y - .05, z + .06), rot=(.35, 0, 0), chamfer=.015)

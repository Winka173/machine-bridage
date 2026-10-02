"""Prompt 27 wave 8, lane A (DECISIONS "27 wave 8a1 ..."): the remaining munitions, props and unlisted units, merged last
in build_assets.all_builders() so these builders win. Plan: Docs/models/WAVE8_PLAN.md.

Pass 8a1 (first half of the generated "not found by the static scan" row; aim120 and aim9 keep their old files: their
COLOR_0 is already at the ceiling and any added part lowers the mean): apfsds, atgm_ataka, atgm_kornet,
atgm_tow, bomb_fab, bomb_mk84, buk, debris_concrete/leaves/metal/plaster/roof/wood, flak_round, gbu12, gbu39, gmlrs, grad,
grad_cluster, griffin.

Method: the current builders (mb_munitions, mb_props) unchanged in silhouette and nodes, plus a few small real-world details
(hanger lugs, guide studs, arming vanes) and a lighter ambient-occlusion bake (`ao_strength`) so the round
reads brighter at 40 px. Names of existing parts are reused, so no runtime node changes.
"""
import mb_munitions as mu
import mb_props as pr

LEN = {'aim120': 2.6, 'aim9': 2.2, 'atgm_ataka': 1.5, 'atgm_kornet': 1.3, 'atgm_tow': 1.3, 'bomb_fab': 1.8,
       'bomb_mk84': 2.7, 'buk': 3.6, 'gbu12': 2.2, 'gmlrs': 2.8, 'grad': 2.2, 'grad_cluster': 2.2, 'griffin': 1.0}
RADIUS = {'aim120': .07, 'aim9': .055, 'atgm_ataka': .058, 'atgm_kornet': .08, 'atgm_tow': .066, 'bomb_fab': .15,
          'bomb_mk84': .27, 'buk': .13, 'gbu12': .11, 'gmlrs': .081, 'grad': .052, 'grad_cluster': .052, 'griffin': .064}


def _lugs(name, ts, size=(.04, .07, .04)):
    def add(m, r):
        for t in ts:
            m.box('Lugs', mu.LIGHT_GREY, size, m.at(r + .008, t))
    return add


def _studs(ts):
    """Guide studs: small steel pins on the underside (they ride the launch rail)."""
    def add(m, r):
        for t in ts:
            m.box('Studs', mu.LIGHT_GREY, (.02, .04, .03), m.at(r + .004, t, 3.14159))
    return add


def _vane(m, r):
    """Arming vane: a short two-blade propeller on the fuze tip."""
    m.box('Arming_vane', mu.STEEL, (1.4 * r, .012, .03), m.at(0, .04))


DETAIL = {
    'atgm_ataka': _studs((.55, 1.0)),
    'atgm_kornet': _studs((.55, 1.0)),
    'atgm_tow': _studs((.60, 1.0)),
    'griffin': _studs((.40, .72)),
    'gmlrs': _studs((1.0, 1.9)),
    'grad': _studs((.9,)),
    'grad_cluster': _studs((.9,)),
    'buk': _lugs('buk', (1.6, 2.7), (.06, .12, .06)),
    'gbu12': _lugs('gbu12', (.90, 1.30), (.04, .07, .04)),
    'bomb_fab': _vane,
    'bomb_mk84': _vane,
}


def _wrap(name, fn):
    detail = DETAIL.get(name)

    def build(a):
        fn(a)
        if detail:
            m = mu.Round(a, LEN[name])
            detail(m, RADIUS[name])
    return build


LOW_AO = ('buk', 'gmlrs')  # near the top of the tone range: the lugs' own vertices need a lighter bake
NAMES = ('apfsds', 'atgm_ataka', 'atgm_kornet', 'atgm_tow', 'bomb_fab', 'bomb_mk84', 'buk', 'flak_round',
         'gbu12', 'gbu39', 'gmlrs', 'grad', 'grad_cluster', 'griffin')
BUILDERS = {n: (_wrap(n, mu.BUILDERS[n][0]), dict(mu.BUILDERS[n][1], ao_strength=0 if n in LOW_AO else .5)) for n in NAMES}


def _debris(kind):
    fn, options = pr.BUILDERS[f'debris_{kind}']

    return fn, dict(options, ao_strength=.8)


BUILDERS.update({f'debris_{k}': _debris(k) for k in ('concrete', 'leaves', 'metal', 'plaster', 'roof', 'wood')})

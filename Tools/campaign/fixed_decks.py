"""Prompt 31 L1/L2 (DECISIONS "Prompt 31 L0/L1/L2"): the missions whose deck the game hands out (sheet "Màn bộ bài game").

A fixed deck is exactly eight buyable vehicle cards and two support cards; placed allies take no card slot. Its cards fight
at the main deck's rank curve for that point of the campaign (Campaign.ExpectedRank in the game, plus the deck's
rankBonus), with no equipment. A card the player has not unlocked by then is a loaned card: usable in that mission only,
never unlocked by it, labelled "Loaned for this mission" / "Mượn trong nhiệm vụ này". At most two loaned cards a mission
(LOAN_EXCEPTIONS); the sheet's other locked cards are replaced by an unlocked card of the same role (REPLACED, logged in
DECISIONS). A fixed deck never changes the mission's objective (p31_objectives_baseline.json, the objectives before
prompt 31; check() compares them). The AI keeps the mission type's profile; the special rules ride on it as flags.

campaign.json "fixedDeck": {"vehicleIds": [8], "supportIds": [2], "placedAllies": [], "loanedCards": [],
"specialRules": [], "status": "MAKE_FIRST", "rankBonus": n, "prepSeconds": s} (the last two only when set).
"""

import json
import os

import campaign_kit as kit

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = json.load(open(os.path.join(HERE, 'p31_objectives_baseline.json'), encoding='utf-8'))

# The objective fields check() compares with the baseline (what wins or loses the mission).
OBJECTIVE_KEYS = ('goal', 'points', 'enemyOwns', 'holdSeconds', 'targets', 'protectNeeded', 'killsNeeded', 'surviveSeconds',
                  'timeLimit', 'convoyCount', 'convoyNeeded', 'launchSeconds')

VEHICLE_SLOTS, SUPPORT_SLOTS, MAX_LOANED = 8, 2, 2

# c1m01 is the first battle: a new player owns four vehicle cards, so eight cards need four loaned (DECISIONS).
LOAN_EXCEPTIONS = {'c1m01': 4}

# The special rules a fixed deck may name, and how each is met (the game shows Strings "fixeddeck.rule.<id>"). A rule is
# listed only when the game does what it says; the sheet's rules not met yet are in PENDING.
RULES = {
    'noBaseStart': 'no camp: playerBase None',
    'beachLanding': 'deliveries land at the rally point on the beach: no outposts, no command vehicle in the deck',
    'coastalGuns': 'the enemy_barrage event repeats, each salvo warned (event.barrage.warn)',
    'raidNoBase': 'no camp: playerBase None',
    'warnedAirWaves': 'the air_wave event warns of the direction (C.3 warning seconds, minimap mark)',
    'nightGuns': 'Night; the counter-battery radar shows a gun that fired (StatusKind.Reveal); the hunted guns move on their routes',
    'trainPrep': 'MissionMode holds the boss on its route for prepSeconds',
    'seaFogLighthouse': 'lighthousebay in Fog; whoever holds the lighthouse sees the sea (Naval.Rules.LighthouseOwner)',
    'airCap6': 'the aircraft cap is 6 in every battle',
    'patchworkDeck': 'the deck itself (cheap cards, many of them)',
    'ciwsSaturate': "Scylla's ciws_fore part shoots missiles down (CombatSystem.PointDefence); mass them or break it",
    'morriganDecoys': "Morrigan's big attack goes for anti-air (BigAttackDefs); the decoy paradrop draws fire",
    'eliteRank': 'the cards fight one rank above the curve (rankBonus 1)',
    'timedRecon': 'Recon against the time limit; the test_rod event is Skygate turning its gun',
}

# The sheet's rules not in effect yet, and why (the report and DECISIONS list them).
PENDING = {
    'c2m04': 'extraction point after the last station, win with 3 vehicles there: would change the objective (Destroy), dropped',
    'c4m05': 'mines on the rails slow the train: mines damage it, no slow yet',
    'c5m07': 'the canopy hides ground vehicles from drones: no canopy cover in the Sim yet',
    'c7m11': 'city blackout (prompt 31 L3 event, not built yet: the mission runs without it); the storm cutting radar range',
    'i3m02': 'Morrigan prefers anti-air that stands still: its big attack picks anti-air, moving or not',
}

# The fixed decks in effect (prompt 31 L2: the 13 MAKE FIRST missions), each with the sheet's cards it replaced.
DECKS = {
    'c1m01': dict(
        vehicles=['amphib_light_vehicle', 'light_tank', 'armored_car', 'rocket_technical', 'mortar_carrier', 'ifv', 'main_battle_tank', 'scout_jeep'],
        supports=['smoke_screen', 'artillery_barrage'],
        loaned=['amphib_light_vehicle', 'light_tank', 'rocket_technical', 'mortar_carrier'],
        replaced={'zu23_technical': 'ifv', 'engineer_vehicle': 'main_battle_tank'},
        rules=['noBaseStart', 'beachLanding', 'coastalGuns'],
        events=[{'id': 'enemy_barrage', 'trigger': {'at': 90, 'every': 80, 'times': 4}, 'params': {'salvos': 2, 'radius': 16}}]),
    'c2m04': dict(
        vehicles=['armored_car', 'scout_jeep', 'vbied', 'rocket_technical', 'ifv', 'light_tank', 'zu23_technical', 'demolition_line_vehicle'],
        supports=['smoke_screen', 'repair_drop'],
        loaned=['vbied', 'demolition_line_vehicle'],
        replaced={'recoilless_jeep': 'ifv'},
        rules=['raidNoBase']),
    'c2s2': dict(
        vehicles=['zu23_technical', 'aa_vehicle', 'shorad_vehicle', 'aa_gun_vehicle', 'armored_car', 'ifv', 'engineer_vehicle', 'ammo_carrier'],
        supports=['smoke_screen', 'repair_drop'],
        loaned=['shorad_vehicle', 'aa_gun_vehicle'],
        replaced={'mobile_repair_vehicle': 'ammo_carrier', 'uav_scan': 'smoke_screen'},
        rules=['warnedAirWaves']),
    'c3m06': dict(
        vehicles=['scout_jeep', 'radar_scout', 'counter_battery_radar', 'mortar_carrier', 'artillery', 'attack_helicopter', 'recon_drone', 'armored_car'],
        supports=['instant_counter_battery', 'uav_scan'],
        loaned=['radar_scout', 'instant_counter_battery'],
        replaced={'wheeled_howitzer': 'mortar_carrier', 'scout_heli': 'attack_helicopter', 'illum_flare_strike': 'uav_scan'},
        rules=['nightGuns']),
}


def apply():
    """Writes each deck into its mission (campaign_kit.MISSIONS), and the events its rules need."""
    for mid, d in DECKS.items():
        m = kit.mission(mid)
        deck = {'vehicleIds': list(d['vehicles']), 'supportIds': list(d['supports']), 'placedAllies': list(d.get('allies', [])),
                'loanedCards': list(d['loaned']), 'specialRules': list(d['rules']), 'status': 'MAKE_FIRST'}
        if d.get('rankBonus'):
            deck['rankBonus'] = d['rankBonus']
        if d.get('prepSeconds'):
            deck['prepSeconds'] = d['prepSeconds']
        m['fixedDeck'] = deck
        if d.get('events'):
            m['missionEvents'] = list(m.get('missionEvents', [])) + list(d['events'])


apply()


def objectives(m):
    """The fields that win or lose a mission, as the baseline file holds them."""
    o = {k: m[k] for k in OBJECTIVE_KEYS if k in m}
    if m.get('boss'):
        o['boss'] = m['boss']['def']
    if m.get('hunt'):
        o['hunt'] = [h['def'] for h in m['hunt']]
    if m.get('convoy'):
        o['convoy'] = m['convoy']['def']
    if m.get('stages'):
        o['stages'] = [s.get('goal') for s in m['stages']]
    return o


def check_mission(m, owned, defs, fail):
    """
    Prompt 31 L1: the campaign rule "no mission asks for a card not unlocked" with its one exception, the loaned card.
    <owned> is what the player has before this mission (its own reward is not owned in it); <defs> every id balance.json
    defines.
    """
    deck = m.get('fixedDeck')
    if not deck:
        return
    mid = m['id']
    vehicles, supports, loaned = deck['vehicleIds'], deck['supportIds'], deck['loanedCards']
    if len(vehicles) != VEHICLE_SLOTS or len(set(vehicles)) != VEHICLE_SLOTS:
        fail(f'{mid}: a fixed deck has {VEHICLE_SLOTS} different vehicle cards ({vehicles})')
    if len(supports) != SUPPORT_SLOTS or len(set(supports)) != SUPPORT_SLOTS:
        fail(f'{mid}: a fixed deck has {SUPPORT_SLOTS} different support cards ({supports})')
    for card in vehicles + supports:
        if card not in defs:
            fail(f'{mid}: fixed deck card {card} is not in balance.json')
        if card not in owned and card not in loaned:
            fail(f'{mid}: {card} is not unlocked by then and not loaned')
    for card in loaned:
        if card not in vehicles + supports:
            fail(f'{mid}: loaned card {card} is not in the deck')
        if card in owned:
            fail(f'{mid}: {card} is unlocked by then, not loaned')
    if len(loaned) > LOAN_EXCEPTIONS.get(mid, MAX_LOANED):
        fail(f'{mid}: {len(loaned)} loaned cards (at most {LOAN_EXCEPTIONS.get(mid, MAX_LOANED)})')
    for rule in deck['specialRules']:
        if rule not in RULES:
            fail(f'{mid}: special rule {rule} is not one the game knows')
    rules = set(deck['specialRules'])
    if rules & {'noBaseStart', 'raidNoBase'} and m.get('playerBase', 'None') != 'None':
        fail(f'{mid}: a raid with no camp has playerBase None')
    if 'beachLanding' in rules and (m.get('outposts') or 'command_vehicle' in vehicles):
        fail(f'{mid}: deliveries land on the beach only: no outposts and no command vehicle')
    if 'trainPrep' in rules and not (deck.get('prepSeconds', 0) > 0 and m.get('boss', {}).get('route')):
        fail(f'{mid}: the train waits only with prepSeconds and a boss route')
    if 'eliteRank' in rules and deck.get('rankBonus', 0) < 1:
        fail(f'{mid}: elite armour wants a rank bonus')
    if mid not in BASELINE:
        fail(f'{mid}: no objective baseline from before prompt 31')
    elif objectives(m) != BASELINE[mid]:
        fail(f'{mid}: the objective changed ({objectives(m)} against {BASELINE[mid]} before prompt 31)')

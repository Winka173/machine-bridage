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
    'cityBlackout': 'the city_blackout event (prompt 31 L3): night falls and the towers on the grid shut down, both sides',
    'behemothOurs': "the escorted Behemoth is Mara's, a placed ally (convoy): the escort's loss rule; it holds on the order Defend",
    'hawkWingman': "Hawk's fighter is a placed ally under the allied AI and the general order; MissionMode loses the mission if it falls",
    'maraBehemoth': "Mara's repainted Behemoth (mara_behemoth) is a placed ally under the allied AI and the general order",
    'factoryAlarm': 'the factory_alarm event (prompt 31 L3): spotted, the mill gate shuts and the garrison comes',
}

# The rules that are a mission event (prompt 31 L3): the event must be in the mission.
RULE_EVENTS = {'cityBlackout': 'city_blackout', 'factoryAlarm': 'factory_alarm', 'droneCanopy': 'drone_swarm', 'ceasefireFaction': 'ceasefire'}

# The sheet's rules not in effect yet, and why (the report and DECISIONS list them).
PENDING = {
    'c2m04': 'extraction point after the last station, win with 3 vehicles there: would change the objective (Destroy), dropped',
    'c4m05': 'mines on the rails slow the train: mines damage it, no slow yet',
    'c5m07': 'the canopy hides ground vehicles from drones: no canopy cover in the Sim yet',
    'c7m11': 'the storm cutting radar range (no Sim rule yet); the city blackout is in since prompt 31 L3',
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
    'c4m05': dict(
        vehicles=['engineer_vehicle', 'vbied', 'mine_layer', 'tank_destroyer', 'artillery', 'wheeled_gun', 'towed_at_gun', 'scout_jeep'],
        supports=['remote_mines', 'artillery_barrage'],
        loaned=['towed_at_gun', 'remote_mines'],
        replaced={'demolition_line_vehicle': 'vbied', 'nlos_atgm_vehicle': 'artillery'},
        rules=['trainPrep'], prepSeconds=60),
    'c4m06': dict(
        vehicles=['river_patrol_boat', 'river_gunboat', 'ifv', 'railgun_truck', 'light_tank', 'attack_helicopter', 'scout_heli', 'aa_vehicle'],
        supports=['artillery_barrage', 'smoke_screen'],
        loaned=['river_patrol_boat', 'river_gunboat'],
        replaced={'amphib_light_vehicle': 'ifv', 'coastal_ashm_vehicle': 'railgun_truck', 'prop_attack_plane': 'scout_heli',
                  'guided_shell_strike': 'artillery_barrage'},
        rules=['seaFogLighthouse']),
    'c5m07': dict(
        vehicles=['fighter_jet', 'scout_heli', 'attack_helicopter', 'strike_drone', 'sam_launcher', 'ew_jammer', 'iron_beam', 'aa_vehicle'],
        supports=['drone_intercept_strike', 'uav_scan'],
        loaned=['iron_beam', 'drone_intercept_strike'],
        replaced={'light_attack_heli': 'scout_heli', 'wingman_drone': 'strike_drone', 'interceptor_drone_vehicle': 'sam_launcher',
                  'microwave_vehicle': 'ew_jammer', 'shorad_vehicle': 'aa_vehicle', 'jam_storm': 'uav_scan'},
        rules=['airCap6']),
    'c7m11': dict(
        vehicles=['aa_57mm_vehicle', 'heavy_aa', 'iron_beam', 'sam_launcher', 'zu23_technical', 'shorad_vehicle', 'recon_drone', 'ifv'],
        supports=['uav_scan', 'airstrike'],
        loaned=['aa_57mm_vehicle', 'shorad_vehicle'],
        replaced={'radar_support_vehicle': 'recon_drone', 'illum_flare_strike': 'uav_scan', 'sead_strike': 'airstrike'},
        rules=['airCap6', 'cityBlackout']),
    'c8m11': dict(
        vehicles=['combat_wreck_car', 'armored_bulldozer', 'rocket_technical', 'zu23_technical', 'recoilless_jeep', 'mortar_carrier', 'engineer_vehicle', 'vbied'],
        supports=['artillery_barrage', 'smoke_screen'],
        loaned=['combat_wreck_car', 'recoilless_jeep'],
        replaced={'demolition_line_vehicle': 'engineer_vehicle', 'reinforcements': 'artillery_barrage'},
        rules=['patchworkDeck']),
    'c9m08': dict(
        vehicles=['coastal_ashm_vehicle', 'ground_cruise_missile_vehicle', 'attack_helicopter', 'attack_jet', 'recon_drone', 'mlrs', 'sam_launcher', 'iron_beam'],
        supports=['airstrike', 'smoke_screen'],
        loaned=['coastal_ashm_vehicle', 'ground_cruise_missile_vehicle'],
        replaced={'stealth_naval_strike': 'attack_jet', 'river_gunboat': 'mlrs', 'cruise_missile': 'airstrike', 'chaff_strike': 'smoke_screen'},
        rules=['ciwsSaturate']),
    'i3m02': dict(
        vehicles=['long_sam', 'sam_launcher', 'aa_vehicle', 'recon_drone', 'aa_57mm_vehicle', 'iron_beam', 'heavy_aa', 'engineer_vehicle'],
        supports=['decoy_paradrop', 'smoke_screen'],
        loaned=['aa_57mm_vehicle', 'decoy_paradrop'],
        replaced={'shorad_vehicle': 'aa_vehicle', 'radar_support_vehicle': 'recon_drone', 'interceptor_drone_vehicle': 'heavy_aa',
                  'mobile_repair_vehicle': 'engineer_vehicle', 'chaff_strike': 'smoke_screen'},
        rules=['morriganDecoys']),
    'i3m03': dict(
        vehicles=['heavy_tank', 'next_gen_tank', 'main_battle_tank', 'bmpt', 'twin_tank', 'heavy_aa', 'mobile_repair_vehicle', 'ammo_carrier'],
        supports=['repair_drop', 'artillery_barrage'],
        loaned=['next_gen_tank', 'mobile_repair_vehicle'],
        replaced={},
        rules=['eliteRank'], rankBonus=1),
    'c11m13': dict(
        vehicles=['recon_jet', 'scout_heli', 'armored_car', 'scout_jeep', 'smoke_carrier', 'ew_jammer', 'gps_jammer_vehicle', 'light_tank'],
        supports=['smoke_screen', 'sead_strike'],
        loaned=['recon_jet', 'gps_jammer_vehicle'],
        replaced={'airborne_vehicle': 'light_tank', 'decoy_paradrop': 'sead_strike'},
        rules=['timedRecon']),
    # Prompt 31 L4 (MAKE LATER), c6m03 first: the placed-ally trial. Mara's Behemoth is the Escort's own convoy (the objective
    # kept: it must reach the end of its route), so the placed ally is that convoy unit: shown on the deck page, lost if it
    # falls (the escort's rule), halting while the player's general order is Defend.
    'c6m03': dict(
        vehicles=['mobile_repair_vehicle', 'ammo_carrier', 'engineer_vehicle', 'aa_vehicle', 'ifv', 'smoke_carrier', 'tank_destroyer', 'scout_jeep'],
        supports=['repair_drop', 'smoke_screen'],
        loaned=['mobile_repair_vehicle'],
        replaced={},
        allies=[{'def': 'behemoth', 'x': -100, 'z': -100, 'heading': 45, 'name': 'behemoth_mara', 'convoy': True, 'lossIfDestroyed': True}],
        rules=['behemothOurs'], status='MAKE_LATER'),
    # c10m12 (Hawk and Raven): Hawk's own fighter as a placed ally (the allied AI, the general order), lost if it falls; the
    # Boss objective (Morrigan) kept. The sheet's five locked vehicle cards and one support: loaned the wingman drone (Hawk's
    # wingman) and the chaff (the duel's defence); radar_support_vehicle -> recon_drone (the owned spotter), aa_57mm_vehicle ->
    # heavy_aa (owned gun anti-air), aerial_tanker -> stealth_fighter (no tanker owned; a second fighter keeps the air side),
    # shorad_vehicle -> aa_vehicle.
    'c10m12': dict(
        vehicles=['fighter_jet', 'wingman_drone', 'sam_launcher', 'recon_drone', 'heavy_aa', 'iron_beam', 'stealth_fighter', 'aa_vehicle'],
        supports=['chaff_strike', 'sead_strike'],
        loaned=['wingman_drone', 'chaff_strike'],
        replaced={'radar_support_vehicle': 'recon_drone', 'aa_57mm_vehicle': 'heavy_aa', 'aerial_tanker': 'stealth_fighter',
                  'shorad_vehicle': 'aa_vehicle'},
        allies=[{'def': 'fighter_jet', 'x': -92, 'z': -92, 'heading': 45, 'name': 'hawk_jet', 'lossIfDestroyed': True}],
        rules=['hawkWingman'], status='MAKE_LATER'),
    # c12m03 (the last Behemoth works): Mara's Behemoth, repainted, fights beside the brigade (placed ally, allied AI, the
    # general order: Attack at Varga's HQ, Defend by our camp); the Duel objective kept; not lost if it falls (the sheet asks
    # nothing harder than c6m03). Only the mobile repair vehicle is locked: loaned.
    'c12m03': dict(
        vehicles=['main_battle_tank', 'bmpt', 'tank_destroyer', 'mobile_repair_vehicle', 'ammo_carrier', 'mlrs', 'sam_launcher', 'engineer_vehicle'],
        supports=['repair_drop', 'artillery_barrage'],
        loaned=['mobile_repair_vehicle'],
        replaced={},
        allies=[{'def': 'mara_behemoth', 'fallback': 'behemoth', 'x': -96, 'z': -88, 'heading': 45, 'name': 'behemoth_mara_repainted'}],
        rules=['maraBehemoth'], status='MAKE_LATER'),
    # i1m01 (interlude I, the Foundry): infiltration with the pass 3 factory alarm. The sheet's three locked cards: loaned the
    # radar scout (see first) and the EW jammer (stay unseen); recoilless_jeep -> rocket_technical (the owned light anti-tank).
    'i1m01': dict(
        vehicles=['scout_jeep', 'radar_scout', 'armored_car', 'rocket_technical', 'light_tank', 'smoke_carrier', 'ew_jammer', 'engineer_vehicle'],
        supports=['smoke_screen', 'uav_scan'],
        loaned=['radar_scout', 'ew_jammer'],
        replaced={'recoilless_jeep': 'rocket_technical'},
        rules=['factoryAlarm'], status='MAKE_LATER'),
}


def apply():
    """Writes each deck into its mission (campaign_kit.MISSIONS), and the events its rules need."""
    for mid, d in DECKS.items():
        m = kit.mission(mid)
        deck = {'vehicleIds': list(d['vehicles']), 'supportIds': list(d['supports']), 'placedAllies': list(d.get('allies', [])),
                'loanedCards': list(d['loaned']), 'specialRules': list(d['rules']), 'status': d.get('status', 'MAKE_FIRST')}
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
    # Prompt 31 L3/L4: a rule that is an event wants the event in the mission.
    played = {(r if isinstance(r, str) else r.get('id')) for r in m.get('missionEvents', [])}
    for rule_id, event_id in RULE_EVENTS.items():
        if rule_id in rules and event_id not in played:
            fail(f'{mid}: the rule {rule_id} wants the {event_id} event')
    if 'eliteRank' in rules and deck.get('rankBonus', 0) < 1:
        fail(f'{mid}: elite armour wants a rank bonus')
    # Prompt 31 L4: placed allies: a unit the catalog has (or its fallback), the convoy one the mission's own convoy.
    for a in deck.get('placedAllies', []):
        if a['def'] not in defs and a.get('fallback') not in defs:
            fail(f"{mid}: placed ally {a['def']} is not in balance.json")
        if a.get('convoy') and m.get('convoy', {}).get('def') != a['def']:
            fail(f"{mid}: placed ally {a['def']} is the convoy, but the mission's convoy is {m.get('convoy', {}).get('def')}")
    if mid not in BASELINE:
        fail(f'{mid}: no objective baseline from before prompt 31')
    elif objectives(m) != BASELINE[mid]:
        fail(f'{mid}: the objective changed ({objectives(m)} against {BASELINE[mid]} before prompt 31)')

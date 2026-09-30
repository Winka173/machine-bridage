"""Prompt 25 D2 (DECISIONS 25D2): the unlock route of the balance spreadsheet.

Tools/balance/import_unlocks.py reads the sheet "Phương tiện" (column "Mở khóa đề xuất") into unlocks_sheet.json, here:
where each vehicle card opens (a starter, a chapter, an interlude) and which cards are story loot. This file moves the
cards of the route (act4.UNLOCKS, act9's story loot) to the sheet's chapters:

  1. A card already opened in the sheet's chapter keeps its mission. Story loot keeps its story beat (act9.SWAPS put it
     there; the sheet names the same chapters).
  2. A card moved to another chapter takes a main mission of that chapter (not a side mission, not an option of a story
     choice, not the operation): in the order of play, the first that unlocks the fewest things once the cards leaving the
     chapter are gone. The cards moving into one chapter are placed in the order they opened before: the former starters
     first, then by their old mission, then the cards that had no mission (the premium vehicles and the two below) by CP.
  3. Cards the sheet does not cover stay where they are (supports, towers, modules, tower branches). Two towers had lost
     their mission in prompt 20's route and could not be had at all: they get one here (ORPHANS).

The prompt 20 act switches then work as before: a chapter switched off hands its cards to the nearest chapter on
(Campaign.All in the game, build_campaign.cut for the economy).
"""

import json
import os

import campaign_kit as kit
import act8
import story

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = json.load(open(os.path.join(HERE, 'unlocks_sheet.json'), encoding='utf-8'))

# The supports and towers a new player owns (Progression.StarterSupports / StarterTowers: no row of the sheet).
STARTER_REST = ['artillery_barrage', 'smoke_screen', 'guard_tower', 'mg_bunker', 'aa_turret', 'gun_turret']
STARTER_VEHICLES = list(SHEET['starters'])
STARTERS = STARTER_VEHICLES + STARTER_REST

# Towers no mission opened (prompt 20's route dropped them; prompt 4 had the minefield in chapter 1 and the Patriot in
# chapter 3). The minefield goes back to chapter 1, where the first base is built; the long-range SAM site goes to chapter 8,
# the chapter of the long-range SAM vehicle, which the sheet leaves with three cards (chapter 3 opens eight already).
ORPHANS = {'minefield': 1, 'missile_battery': 8}

# Progression.StarterVehicles before prompt 25 D2 (a former starter that moves into a chapter opens first there).
OLD_STARTERS = ['scout_jeep', 'armored_car', 'ifv', 'light_tank', 'main_battle_tank', 'aa_vehicle', 'artillery']
CP = {}  # filled from balance.json for the order of the cards with no old mission


def _cp():
    import re
    text = open(os.path.join(HERE, '..', '..', 'Assets', 'MachineBrigade', 'Resources', 'Data', 'balance.json'), encoding='utf-8').read()
    for vid, cp in re.findall(r'\{\s*"id":\s*"([a-z0-9_]+)"[^\n]*?"cp":\s*(\d+)', text):
        CP.setdefault(vid, int(cp))


def _play_order():
    """Every main mission id in the order of play (chapters in story order, each in act8.ORDER)."""
    return [mid for c in story.ORDER for mid in act8.ORDER[c]]


def _apply():
    _cp()
    order = _play_order()
    at = {mid: i for i, mid in enumerate(order)}
    by_id = {m['id']: m for m in kit.MISSIONS}
    where = {}
    for m in kit.MISSIONS:
        for u in m.get('unlocks', []):
            where[u] = m['id']
    wanted = dict(SHEET['chapters'])
    wanted.update({k: v for k, v in ORPHANS.items() if k not in where})
    loot = set(SHEET['loot'])
    moving = []
    for card, chapter in wanted.items():
        mid = where.get(card)
        if card in loot:
            if mid is None or by_id[mid]['chapter'] != chapter:
                raise SystemExit(f'act11: story loot {card} is not on its beat in chapter {chapter} ({mid})')
            continue
        if mid is not None and by_id[mid]['chapter'] == chapter:
            continue
        if mid is not None:
            m = by_id[mid]
            m['unlocks'] = [u for u in m['unlocks'] if u != card]
            if not m['unlocks']:
                del m['unlocks']
        # The order it opened in before: a former starter first, then its old mission, then the rest by CP.
        rank = (0, 0) if card in OLD_STARTERS else (1, at[mid]) if mid is not None else (2, CP.get(card, 99))
        moving.append((chapter, rank, card))
    for chapter, _, card in sorted(moving):
        slots = [by_id[mid] for mid in act8.ORDER[chapter]]
        slots = [m for m in slots if not m.get('side') and not m.get('branch') and not m.get('operation')]
        if not slots:
            raise SystemExit(f'act11: no mission of chapter {chapter} can open {card}')
        target = min(slots, key=lambda m: (len(m.get('unlocks', [])), at[m['id']]))
        target['unlocks'] = target.get('unlocks', []) + [card]
    for card in STARTER_VEHICLES:
        if card in where:
            raise SystemExit(f'act11: the starter {card} is still opened by {where[card]}')


_apply()

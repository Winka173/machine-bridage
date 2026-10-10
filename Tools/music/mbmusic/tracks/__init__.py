"""Track registry: name -> builder returning a :class:`mbmusic.score.Song`."""

from __future__ import annotations

import importlib

TRACKS = {
    "menu": "menu",
    "battle_1": "battle_1",
    "battle_2": "battle_2",
    "battle_3": "battle_3",
    "boss": "boss",
    "siege": "siege",
    "battle_4": "battle_4",
    "battle_5": "battle_5",
    "battle_6": "battle_6",
    "battle_7": "battle_7",
    "battle_8": "battle_8",
    "naval": "naval",
    "boss_air": "boss_air",
    "boss_naval": "boss_naval",
    "boss_land": "boss_land",
    "boss_train": "boss_train",
    "boss_orbital": "boss_orbital",
    "boss_final": "boss_final",
    "boss_mini": "boss_mini",
    "victory": "stingers:victory",
    "defeat": "stingers:defeat",
}


def build(name: str):
    spec = TRACKS[name]
    mod_name, _, fn = spec.partition(":")
    mod = importlib.import_module(f"{__name__}.{mod_name}")
    return getattr(mod, fn or "build")()

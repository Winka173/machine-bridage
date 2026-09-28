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
    "victory": "stingers:victory",
    "defeat": "stingers:defeat",
}


def build(name: str):
    spec = TRACKS[name]
    mod_name, _, fn = spec.partition(":")
    mod = importlib.import_module(f"{__name__}.{mod_name}")
    return getattr(mod, fn or "build")()

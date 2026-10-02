"""Prompt 29 S08 (R10): measurements carry a stamp of what they measured.

A measure writes `<file>.stamp.json` beside its output (Tests/EditMode/MeasureStamp.cs): the sha256 of balance.json and
campaign.json, the build commit and the rules version. The design document shows a measured table in the main body only
when its stamp matches the current data and rules; anything else (no stamp, or another hash) goes to the appendix
"Lịch sử đo" with the stamp it was measured under.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
RULES = 'p29'  # bump when the balance rules change (MeasureStamp.Rules in C# too)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ''


def current() -> dict:
    return {'balance': sha(DATA / 'balance.json'), 'campaign': sha(DATA / 'campaign.json'), 'rules': RULES}


def stamp_of(path) -> dict | None:
    if path is None:
        return None
    p = Path(str(path) + '.stamp.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def matches(path) -> bool:
    """The measure at <path> was taken on today's data and rules (the build commit is informative, not compared)."""
    s = stamp_of(path)
    if not s:
        return False
    now = current()
    return all(s.get(k) == now[k] for k in ('balance', 'campaign', 'rules'))


def describe(path) -> str:
    s = stamp_of(path)
    if not s:
        return 'không có dấu hash (đo trước prompt 29)'
    return f"balance {s.get('balance', '')[:8]}, campaign {s.get('campaign', '')[:8]}, commit {s.get('commit', '')[:8]}, luật {s.get('rules', '')}"

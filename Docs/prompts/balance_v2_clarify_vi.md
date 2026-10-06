# 06/10 owner final clarifications for balance v2 (verbatim)

Final clarifications:

1. `recoilless_106`
- The prompt's `damage 220 KEEP` was stale.
- Canonical/newer balance already changed it from 220 damage / 6.6667 s cooldown to 314 damage / 9.524 s cooldown to preserve approximately the same raw DPS.
- Final:
  - damage = **314 KEEP**
  - cooldown = **current 9.524 s KEEP**
  - Pen **3 -> 4**
- Do not revert damage to 220.

2. `sam_48n6`
- Final splash = **6 m**.
- The ×1.25 suggestion is capped by the stated 5–6 m fragmentation footprint.
- Do not use 7.2 m.
- Speed remains the latest approved value.
- Damage/Pen KEEP.

3. Boss anti-ship missiles
Increase the two undersized boss anti-ship footprints:
- `pt14_hp_nsm`: splash **-> 8 m**
- `scylla_kh35`: splash **-> 8 m**

Keep their damage, Pen, cooldown and other combat stats unchanged unless another explicit instruction already changes them.

Update impact VFX and warning/damage-radius presentation where derived so the visual footprint matches gameplay.

Do not globally force every boss anti-ship missile to 8 m; these are explicit corrections for these two currently undersized weapons. Continue the broader boss missile audit separately.

4. Railgun
- Pen **4 -> 5**
- damage KEEP
- reload/cooldown KEEP
- do not pre-nerf cadence.
Only increase reload later if post-patch Armour4/5 TTK regression proves Pen 5 makes the railgun overtuned.

These clarifications override conflicting older prompt values.

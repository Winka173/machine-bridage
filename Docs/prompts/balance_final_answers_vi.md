# 06/10 owner answers to the balance master final open decisions (verbatim)

1. Keep `coastal_battery`, `bunker_shelter_tower`, `wheeled_gun`, `blast_wall`, and `bulwark_post` unchanged in this pass. Do not infer additional buffs from class/name.

2. Aircraft cluster-bomb rule is N/A because no aircraft currently carries one. Do NOT automatically apply it to `cluster_strike`.

For `airstrike`: apply the conventional bomb ×1.25 only if the support ultimately uses the same canonical conventional bomb payload. Apply the buff once at the canonical weapon/payload layer; do not double-buff again at the support layer.

Keep `cluster_strike` unchanged for now and balance it separately only if support-value regression shows it is weak.

3. Do NOT add per-ID exceptions for the 25 projectile validator flags and do NOT raise projectile speeds to satisfy the old validator.

Refactor validator classification to:
- HARD_FAIL
- YELLOW_FEEL
- PASS_INTENTIONAL_SHORT_RANGE

Add reason codes:
- `CANONICAL_SHORT_RANGE`
- `INHERITANCE_MISMATCH`
- `TOO_FAST_FOR_CLASS`
- `TOO_SLOW_FOR_CLASS`
- `INTENTIONAL_BOSS_OVERRIDE`

Primary validation should use typical/max-range flight time. Half-range is secondary warning data, not an unconditional fail.

Use approximate hard-fast thresholds:
- ATGM/tactical ground missile: hard fail only if <0.25 s at half range AND <0.45 s at max/typical range.
- Short AAM/MANPADS: hard fail <0.18 s typical.
- Medium/long SAM/AAM: hard fail <0.22 s typical.
- Rocket artillery: hard fail <0.45 s max.
- Mortar/howitzer: hard fail <0.60 s actual-arc max.
- Heavy 240 mm mortar: hard fail <0.75 s actual-arc max; target band can extend to ~2.2 s.

Canonical speeds from the master remain authoritative. A projectile that has the correct canonical speed but is fast only because the game's engagement distance is short should become `PASS_INTENTIONAL_SHORT_RANGE` or `YELLOW_FEEL`, not force a speed increase.

Regenerate the validator report and list all remaining HARD_FAIL entries separately. There should be no stale `NHANH_QUA/CHAM_QUA` flag without a class-aware reason.

4. When should the pack be rebuilt (Unity ExportGameDoc, then export.py)?: after each large task and dont have any task pending, do last

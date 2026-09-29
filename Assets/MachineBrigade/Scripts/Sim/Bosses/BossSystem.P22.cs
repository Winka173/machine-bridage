#nullable enable
using System;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 22 E (DECISIONS 22E): a boss's duel mode (<see cref="Content.DuelDef"/>), for a mission where the player
    /// has aircraft only. <see cref="Duel"/> puts a boss into it: its escorts go home, its big attack is the duel's, and
    /// it goes dark now and then: it holds its fire and flares for a few seconds, so its stealth hides it beyond close
    /// range again (it is seen close up, or for a moment after it fires, as every stealth aircraft).
    /// </summary>
    internal sealed partial class BossSystem
    {
        /// <summary>Puts a boss into its duel mode; false when it has none (or is not alive).</summary>
        public bool Duel(Vehicle v)
        {
            if (v.Def.Duel is not { } duel || !v.IsAlive || v.InDuel) return false;
            v.InDuel = true;
            v.DuelMark = 0;
            v.DuelNextDark = duel.VanishEvery > 0f ? _world.Time + duel.VanishEvery : double.PositiveInfinity;
            if (!duel.Escorts) SetEscorts(v, false);
            if (duel.BigAttack != null)
            {
                var next = v.BigAttack?.Next ?? _world.Time;
                JoinBig(v, duel.BigAttack);
                if (v.BigAttack != null) v.BigAttack.Next = next;
            }
            _world.Emit(SimEvent.RadioMessage((v.Def.RadioSpawn ?? "radio.boss") + ".duel", v.Team));
            return true;
        }

        /// <summary>A duelling boss's dark spells: into one at each health mark and on its clock, out of it when it ends.</summary>
        private void StepDuels(double now)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.InDuel || v.Def.Duel is not { } duel) continue;
                if (!v.IsAlive)
                {
                    v.InDuel = false;
                    continue;
                }
                if (v.DuelDark)
                {
                    if (now < v.DuelDarkUntil) continue;
                    v.DuelDark = false;
                    v.HoldFire = false;
                    continue;
                }
                var share = v.Hp / MathF.Max(1f, v.MaxHp);
                var mark = v.DuelMark < duel.VanishAt.Length && share <= duel.VanishAt[v.DuelMark];
                // Never while its big attack is under way (it keeps its fire for that).
                if (!(mark || now >= v.DuelNextDark) || v.BigAttack is { Stage: not BigStage.Ready }) continue;
                if (mark) v.DuelMark++;
                v.DuelNextDark = duel.VanishEvery > 0f ? now + duel.VanishSeconds + duel.VanishEvery : double.PositiveInfinity;
                v.DuelDark = true;
                v.DuelDarkUntil = now + duel.VanishSeconds;
                v.HoldFire = true;
                v.FlaresUntil = Math.Max(v.FlaresUntil, now + 1.5);
                _world.Emit(SimEvent.RadioMessage((v.Def.RadioSpawn ?? "radio.boss") + ".dark", v.Team));
            }
        }
    }
}

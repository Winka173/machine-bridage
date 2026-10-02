using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 34 L3: warnings by escape time. A boss's T4+ round (<see cref="WeaponDef.WarnSeconds"/>) shows its edge and its
    /// core on its fall point for its whole warning (the Sim keeps it in the air at least that long); a T5 salvo's shells
    /// (Leviathan's 406 mm, marked by their own strike warning) get the core ring inside the warning's edge ring. View only.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private readonly EscapeWarnings _escape;

        /// <summary>The round a fired event carried: its second round, else the mount's own weapon as the boss carries it (its edge).</summary>
        private WeaponDef FiredRound(SimEvent e, VehicleView shooter, WeaponDef fallback)
        {
            if (e.Round != null && _catalog.Weapons.TryGetValue(e.Round, out var round)) return round;
            var mounts = shooter.Sim.Def.Mounts;
            return e.Mount >= 0 && e.Mount < mounts.Count ? mounts[e.Mount].Weapon : fallback;
        }

        /// <summary>
        /// A boss's round fired: true when it is a T4+ round that warns by escape time (its rings are drawn), false to let the
        /// older 0.8 s ring (prompt 26 B.4) decide.
        /// </summary>
        private bool EscapeRing(SimEvent e, VehicleView shooter, WeaponDef weapon, float now)
        {
            var round = FiredRound(e, shooter, weapon);
            var warn = round.WarnSeconds;
            if (warn <= 0f || round.Guided || round.Laid) return false;
            var flight = Mathf.Max(0.05f, e.Value);
            var start = now + Mathf.Max(0f, flight - warn);
            _escape.Add(Ground(e.Target, 0.13f), round.SplashRadius, round.WarnRadius, start, now + flight);
            return true;
        }

        /// <summary>A strike warning of an event barrage with a core inside its ring (the 406 mm salvo's shell): the core's ring too.</summary>
        private void StrikeCore(SimEvent e, float now)
        {
            if (e.DefId == null || !_catalog.TryGetSupport(e.DefId, out var support) || !support.EventOnly || support.IsLine) return;
            if (support.BlastRadius <= 0f || support.BlastRadius >= support.Radius - 0.25f) return;
            _escape.Add(Ground(e.Position, 0.13f), support.BlastRadius, support.Radius, now, now + Mathf.Max(0.2f, e.Value));
        }
    }
}

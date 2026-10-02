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

        /// <summary>Prompt 34 L4: rounds of each shooter's mount already drawn in this batch (a simultaneous volley's barrels).</summary>
        private readonly System.Collections.Generic.Dictionary<(MachineBrigade.Sim.Core.EntityId, int), int> _volley = new();

        /// <summary>
        /// Prompt 34 L4: how late this round of a simultaneous volley is drawn: 0 for the first barrel, then
        /// <see cref="WeaponDef.BarrelGap"/> a barrel (all fired in one tick, drawn one after another on their own muzzles).
        /// </summary>
        private float BarrelStagger(SimEvent e, VehicleView shooter)
        {
            if (e.Kind != SimEventKind.WeaponFired || e.DefId == null || !_catalog.Weapons.TryGetValue(e.DefId, out var gun)) return 0f;
            var round = FiredRound(e, shooter, gun);
            if (!round.Simultaneous || round.Barrels < 2) return 0f;
            var key = (e.Entity, e.Mount);
            var k = _volley.TryGetValue(key, out var seen) ? seen + 1 : 0;
            _volley[key] = k;
            return (k % round.Barrels) * WeaponDef.BarrelGap;
        }

        /// <summary>Prompt 34 L4: a volley's later barrel, drawn <paramref name="late"/> s after the Sim fired it (its shell flies that much less).</summary>
        private void LaterShot(SimEvent e, VehicleView shooter, ViewRegistry views, float at, float late)
        {
            Later(at, () =>
            {
                if (shooter == null || shooter.Root == null) return;
                _weapons.TravelCut = late;
                _weapons.Fired(e, shooter, views, Time.time);
                _weapons.TravelCut = 0f;
            });
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

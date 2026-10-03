#nullable enable
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Play-test 14 (Docs/fixes/playtest14_plan.md): the base aura buildings. While one stands, every unit of its side in its
    /// reach, anywhere on the map, gets its lifts: the airfield aircraft's damage and speed, the repair bay ground vehicles'
    /// damage and health, the defence command centre structures' range and health. One building of a kind counts (the
    /// strongest of the side's, never the sum). Health keeps its share of the maximum as the maximum changes, so a unit
    /// neither heals nor dies when a building rises or falls.
    /// </summary>
    internal sealed partial class FieldWorksSystem
    {
        private readonly List<Vehicle> _auras = new();

        /// <summary>The side's strongest building of each reach this step (team, reach).</summary>
        private readonly Dictionary<(int team, BaseAuraReach reach), BaseAuraDef> _auraBest = new();

        /// <summary>Some unit carried a lift last step: one more pass sets them back to 1 when the last building falls.</summary>
        private bool _aurasOn;

        private void ApplyBaseAuras()
        {
            if (_auras.Count == 0 && !_aurasOn) return;
            _auraBest.Clear();
            foreach (var a in _auras)
            {
                var aura = a.Def.BaseAura!;
                var key = (a.Team, aura.Reach);
                if (!_auraBest.TryGetValue(key, out var held) || aura.Weight > held.Weight) _auraBest[key] = aura;
            }
            _aurasOn = _auraBest.Count > 0;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive) continue;
                BaseAuraDef? lift = null;
                if (_aurasOn && ReachOf(v.Def) is { } reach) _auraBest.TryGetValue((v.Team, reach), out lift);
                v.AuraDamage = 1f + (lift?.Damage ?? 0f);
                v.AuraSpeed = 1f + (lift?.Speed ?? 0f);
                SetAuraHp(v, 1f + (lift?.Hp ?? 0f));
                SetAuraRange(v, 1f + (lift?.Range ?? 0f));
            }
        }

        /// <summary>Which aura reaches a unit (null: none; bosses never).</summary>
        internal static BaseAuraReach? ReachOf(VehicleDef def)
        {
            if (def.Boss) return null;
            if (def.Static) return def.Fort != null ? BaseAuraReach.Structures : null;
            if (def.Flying) return def.Drone ? null : BaseAuraReach.Aircraft;
            return def.Naval != null ? null : BaseAuraReach.Ground;
        }

        private static void SetAuraHp(Vehicle v, float scale)
        {
            if (v.AuraHp == scale) return;
            var max = v.MaxHp;
            var share = max > 0f ? v.Hp / max : 1f;
            v.AuraHp = scale;
            v.Hp = share * v.MaxHp;
        }

        private static void SetAuraRange(Vehicle v, float scale)
        {
            if (v.AuraRange == scale) return;
            if (v.AuraBaseRange == null)
            {
                v.AuraBaseRange = new float[v.Arms.Length];
                for (var i = 0; i < v.Arms.Length; i++) v.AuraBaseRange[i] = v.Arms[i].Range;
            }
            v.AuraRange = scale;
            for (var i = 0; i < v.Arms.Length && i < v.AuraBaseRange.Length; i++)
            {
                var w = v.Arms[i];
                v.Arms[i] = w.Tuned(v.AuraBaseRange[i] * scale, w.Cooldown, w.ProjectileSpeed, w.SplashRadius, w.Spread, w.BurstInterval, w.Targets,
                    w.Ammo, w.Reload, w.Cluster);
            }
        }
    }
}

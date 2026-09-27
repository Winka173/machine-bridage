using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// A vehicle's numbers for its detail screen: health, damage (a shot, and a second's worth),
    /// rate of fire, range, speed and sight, each as it comes and as the player's rank and
    /// equipment make it, with the roster's best for scaling the bars (as World of Tanks Blitz
    /// and War Robots show them: a bar against the best, the upgrade in green on top).
    /// </summary>
    public static class UnitStats
    {
        public readonly struct Stat
        {
            public Stat(string key, float value, float boosted, float best, string format, bool lowerIsBetter = false)
            {
                Key = key;
                Value = value;
                Boosted = boosted;
                Best = best;
                Format = format;
                LowerIsBetter = lowerIsBetter;
            }

            /// <summary>String key of its name (stat.detail.*).</summary>
            public string Key { get; }

            public float Value { get; }
            public float Boosted { get; }

            /// <summary>The roster's best, for the bar's full length.</summary>
            public float Best { get; }

            public string Format { get; }
            public bool LowerIsBetter { get; }
        }

        private static Dictionary<string, float> _best;
        private static Catalog _bestFor;

        /// <summary>Damage of one trigger pull of the main weapon (the whole salvo).</summary>
        public static float Volley(WeaponDef w) => w.Damage * Mathf.Max(1, w.Burst);

        /// <summary>The main weapon's damage a second (salvos over their cooldown).</summary>
        public static float Dps(WeaponDef w) => Volley(w) / Mathf.Max(0.1f, w.Cooldown + (w.Burst - 1) * w.BurstInterval);

        public static List<Stat> For(Catalog catalog, VehicleDef def, VehicleBoost boost)
        {
            var best = Best(catalog);
            var w = def.Weapon;
            return new List<Stat>
            {
                new("stat.detail.hp", def.MaxHp, def.MaxHp * boost.Hp, best["hp"], "N0"),
                new("stat.detail.volley", Volley(w), Volley(w) * boost.Damage, best["volley"], "N0"),
                new("stat.detail.dps", Dps(w), Dps(w) * boost.Damage * boost.FireRate, best["dps"], "N0"),
                new("stat.detail.range", w.Range, w.Range * (1f + boost.Stat(StatId.Range)), best["range"], "0"),
                new("stat.detail.speed", def.Speed, def.Speed * boost.Speed, best["speed"], "0.0"),
                new("stat.detail.vision", def.VisionRange, def.VisionRange * (1f + boost.Stat(StatId.Vision)), best["vision"], "0"),
            };
        }

        /// <summary>The roster's best of each (bosses and fixed defences left out), worked out once per catalog.</summary>
        private static Dictionary<string, float> Best(Catalog catalog)
        {
            if (_best != null && _bestFor == catalog) return _best;
            _bestFor = catalog;
            _best = new Dictionary<string, float> { ["hp"] = 1f, ["volley"] = 1f, ["dps"] = 1f, ["range"] = 1f, ["speed"] = 1f, ["vision"] = 1f };
            foreach (var d in catalog.Vehicles.Values)
            {
                if (d.Boss || d.Static || d.CpCost <= 0) continue;
                _best["hp"] = Mathf.Max(_best["hp"], d.MaxHp);
                _best["volley"] = Mathf.Max(_best["volley"], Volley(d.Weapon));
                _best["dps"] = Mathf.Max(_best["dps"], Dps(d.Weapon));
                _best["range"] = Mathf.Max(_best["range"], d.Weapon.Range);
                _best["speed"] = Mathf.Max(_best["speed"], d.Speed);
                _best["vision"] = Mathf.Max(_best["vision"], d.VisionRange);
            }
            return _best;
        }
    }
}

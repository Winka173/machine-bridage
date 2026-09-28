using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Game.Match
{
    /// <summary>What a base can do (prompt 14 E1, the Base screen's cover strip, like the deck's role cover).</summary>
    public enum CoverRole
    {
        /// <summary>Guns, cannon, flame or blast against light vehicles.</summary>
        AntiLight,

        /// <summary>Armour-piercing guns or missiles against tanks.</summary>
        AntiTank,

        /// <summary>Anti-aircraft guns or missiles.</summary>
        AntiAir,

        /// <summary>Shoots down incoming rockets and missiles (C-RAM's active protection).</summary>
        Intercept,

        /// <summary>Sees stealthy and hidden units (the guard tower).</summary>
        Stealth,

        /// <summary>Repairs or rearms what stands near it (the repair bay, the ammunition depot).</summary>
        Support,
    }

    /// <summary>The roles of towers and modules, their reach, and a camp's cover, from their data (prompt 14 B7, D1, E1).</summary>
    public static class BaseRoles
    {
        public static readonly CoverRole[] All = (CoverRole[])Enum.GetValues(typeof(CoverRole));

        /// <summary>The roles one structure fills.</summary>
        public static HashSet<CoverRole> Of(VehicleDef def)
        {
            var roles = new HashSet<CoverRole>();
            foreach (var m in def.Mounts)
            {
                var w = m.Weapon;
                if (w == null || w.Damage <= 0f) continue;
                if (w.CanTarget(true) && (w.DamageType == DamageType.Flak || w.Targets == TargetLayers.Air || w.Targets == (TargetLayers.Air | TargetLayers.Ground)))
                    roles.Add(CoverRole.AntiAir);
                if (!w.CanTarget(false)) continue;
                if (w.DamageType == DamageType.ArmorPiercing) roles.Add(CoverRole.AntiTank);
                else roles.Add(CoverRole.AntiLight);
            }
            if (def.Aps != null) roles.Add(CoverRole.Intercept);
            if (def.RevealStealth) roles.Add(CoverRole.Stealth);
            if (def.RepairAura != null || def.RearmAura != null) roles.Add(CoverRole.Support);
            return roles;
        }

        /// <summary>The roles a loadout covers with what stands in its open slots (branches counted as themselves).</summary>
        public static HashSet<CoverRole> Cover(Catalog catalog, BaseLoadout loadout)
        {
            var cover = new HashSet<CoverRole>();
            var fitted = loadout.Fitted(catalog);
            foreach (var id in fitted.Towers)
                if (catalog.Vehicles.TryGetValue(fitted.DefFor(id), out var def)) cover.UnionWith(Of(def));
            foreach (var id in fitted.Utilities)
                if (!string.IsNullOrEmpty(id) && catalog.Vehicles.TryGetValue(id, out var def)) cover.UnionWith(Of(def));
            return cover;
        }

        /// <summary>A structure's reach in metres: against the ground and against aircraft (0: cannot), and its shortest range (artillery).</summary>
        public static (float ground, float air, float min) Reach(VehicleDef def)
        {
            float ground = 0f, air = 0f, min = 0f;
            foreach (var m in def.Mounts)
            {
                var w = m.Weapon;
                if (w == null || w.Damage <= 0f) continue;
                if (w.CanTarget(false))
                {
                    ground = MathF.Max(ground, w.Range);
                    if (w.MinRange > 0f) min = min <= 0f ? w.MinRange : MathF.Min(min, w.MinRange);
                }
                if (w.CanTarget(true)) air = MathF.Max(air, w.Range);
            }
            return (ground, air, min);
        }

        /// <summary>The best of a stat among the loadout towers of one size (the Base panel's bars: a tower against its size).</summary>
        public static (float hp, float dps, float range) BestOfSize(Catalog catalog, SlotSize size)
        {
            float hp = 1f, dps = 1f, range = 1f;
            foreach (var id in TowerCards.All(catalog))
            {
                var def = catalog.Vehicles[id];
                if (def.Fort.Size != size) continue;
                hp = MathF.Max(hp, def.MaxHp);
                dps = MathF.Max(dps, UnitStats.Dps(def.Weapon));
                range = MathF.Max(range, Reach(def).ground > 0f ? Reach(def).ground : Reach(def).air);
            }
            return (hp, dps, range);
        }

        /// <summary>How many of a camp's open slots of each size hold something, and how many are open (the counter line).</summary>
        public static (int filled, int open)[] Counts(BaseSiteDef site, BaseRules rules, BaseLoadout loadout)
        {
            var counts = new (int filled, int open)[4];
            var towers = BasePlan.ToAssignment(site, loadout);
            foreach (var slot in BaseLayout.Camp(site, rules, loadout.HqLevel))
            {
                if (!slot.Open) continue;
                var k = slot.Def.Kind == HardpointKind.Utility ? 3 : (int)slot.Def.Class;
                counts[k].open++;
                if (towers[slot.Hardpoint] != null) counts[k].filled++;
            }
            return counts;
        }
    }
}

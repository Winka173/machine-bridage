#nullable enable
using System;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Prompt 13 H.7: how strong a side's base is, one number for the Base screen ("Sức mạnh căn cứ")
    /// and for scaling the Defend and Endless waves. A base is its HQ, its towers and its utility
    /// modules, each worth its fighting value in CP (<see cref="VehicleDef.Power"/>: an HQ 14, a
    /// large tower 11, a medium 7, a light 4, a module 1) times what its card's rank and equipment
    /// make of it: the geometric mean of its toughness (health over damage taken) and its firepower
    /// (damage times rate of fire). A tower branch counts as its tower. <see cref="Score"/> puts it on
    /// a scale where 100 is a mid-level base: the enemy's Normal base at HQ level 3 (1 large, 3
    /// medium, 5 small, 2 modules), rank 1 and no equipment.
    /// </summary>
    public static class BaseStrength
    {
        /// <summary>A structure's worth: its fighting value times its upgrades' quality.</summary>
        public static float Of(VehicleDef def, VehicleBoost boost) => def.Power * Quality(boost);

        /// <summary>What rank and equipment make of a structure: √(toughness × firepower), 1 with none.</summary>
        public static float Quality(VehicleBoost b)
        {
            var toughness = b.Hp / MathF.Max(0.05f, b.DamageTaken);
            var firepower = b.Damage * b.FireRate;
            return MathF.Sqrt(MathF.Max(0f, toughness * firepower));
        }

        /// <summary>
        /// A loadout's power in CP (what stands in the base, as its HQ level fits it): the HQ, every
        /// tower (a branch chosen for it counted as that branch's structure) and module, each with its
        /// upgrades from <paramref name="boosts"/> (null: none).
        /// </summary>
        public static float Power(Catalog catalog, BaseLoadout loadout, Func<VehicleDef, VehicleBoost>? boosts = null)
        {
            var fitted = loadout.Fitted(catalog);
            var total = 0f;
            void Add(string? id)
            {
                if (string.IsNullOrEmpty(id) || !catalog.Vehicles.TryGetValue(id!, out var def)) return;
                total += Of(def, boosts?.Invoke(def) ?? VehicleBoost.None);
            }
            Add(catalog.Base.HqId);
            foreach (var id in fitted.Towers) Add(fitted.DefFor(id));
            foreach (var id in fitted.Utilities) Add(id);
            // Prompt 17 B.6: a layered base's forward strongpoints repeat its towers (as the fortress raises them).
            if (fitted.Layered)
                foreach (var size in new[] { SlotSize.Small, SlotSize.Medium })
                    for (var k = 0; k < catalog.Base.ForwardSlots(size); k++)
                        Add(fitted.TowerForFortress(size, k) is { } id ? fitted.DefFor(id) : null);
            return total;
        }

        /// <summary>A loadout on the 100 scale (100: the Normal enemy base at HQ level 3, no upgrades).</summary>
        public static float Score(Catalog catalog, BaseLoadout loadout, Func<VehicleDef, VehicleBoost>? boosts = null) =>
            100f * Power(catalog, loadout, boosts) / Reference(catalog);

        /// <summary>
        /// A side's base on the same scale, from what stands on the field now (the HQ, towers and modules
        /// alive, with the upgrades they entered with): a mode's reading of the base it faces.
        /// </summary>
        public static float Score(SimWorld world, int team)
        {
            var total = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.Def.Fort == null) continue;
                total += v.Def.Power * MathF.Sqrt(MathF.Max(0f, v.BoostHp / MathF.Max(0.05f, v.DamageTaken) * v.DamageBoost * v.FireGear));
            }
            return 100f * total / Reference(world.Catalog);
        }

        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Catalog, object> References = new();

        /// <summary>The 100 mark's power in CP: the Normal enemy base at HQ level 3 with no upgrades.</summary>
        public static float Reference(Catalog catalog)
        {
            return (float)References.GetValue(catalog, c => MathF.Max(1f, Power(c, BaseLoadout.ForAi(c, "Normal", "default", 1, 3))));
        }

        /// <summary>
        /// Prompt 32 L5: ReferenceBasePower, the power in CP of an HQ level's reference base (balance.json
        /// "base.reference"; a level without one: the AI's Normal base at that level). The Defend and Endless waves are
        /// sized by it, never by the player's own base.
        /// </summary>
        public static float ReferencePower(Catalog catalog, int level)
        {
            level = Math.Clamp(level, 1, catalog.Base.MaxLevel);
            foreach (var r in catalog.Base.Reference)
                if (r.HqLevel == level) return Power(catalog, r);
            return Power(catalog, BaseLoadout.ForAi(catalog, "Normal", "default", 1, level));
        }

        /// <summary>Prompt 32 L5: an HQ level's reference base on the 100 scale (the waves' measure).</summary>
        public static float ReferenceScore(Catalog catalog, int level) => 100f * ReferencePower(catalog, level) / Reference(catalog);

        /// <summary>
        /// How much bigger the Defend and Endless waves come against a base of this score: the score's
        /// share of the 100 mark to the power 0.75, between 0.75 and 2.5 (a base twice the mark faces
        /// waves 1.7 times the size; a bare HQ about three quarters).
        /// </summary>
        public static float WaveScale(float score) => Math.Clamp(MathF.Pow(MathF.Max(0.01f, score / 100f), 0.75f), 0.75f, 2.5f);
    }
}

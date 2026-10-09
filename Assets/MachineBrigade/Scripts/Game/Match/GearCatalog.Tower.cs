using System.Collections.Generic;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Tower equipment's catalogue: 14 base types over the three tower slots (Weapon, Structure,
    /// Systems), the traits each tower slot rolls (the five tower lines and five vehicle traits that
    /// work on a fixed defence), which sub-stats roll on a tower slot, and the tower caps. Every
    /// base type and trait says what a tower must have for it to do anything (<see cref="TowerNeed"/>;
    /// a base type's comes from its stat lines, see <see cref="TowerFit"/>). Numbers are at the top
    /// level, as for vehicles.
    /// </summary>
    public static partial class GearCatalog
    {
        private const BranchMask NoBranch = BranchMask.None;

        public static readonly BaseTypeDef[] TowerBases =
        {
            // Weapon: main stat +damage (the ammunition hoist: +rate of fire).
            new("fortress_barrel", GearSlot.TowerWeapon, NoBranch, StatId.Range, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FortressBarrelTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FortressBarrelTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FortressBarrelTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FortressBarrelTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FortressBarrelTop5)),
            // Prompt 15 C.9: a level of penetration at the top.
            new("sabot_rounds", GearSlot.TowerWeapon, NoBranch, StatId.Penetration, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.SabotRoundsTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.SabotRoundsTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.SabotRoundsTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.SabotRoundsTop4, 1f)),
            new("flak_proximity_fuze", GearSlot.TowerWeapon, NoBranch, StatId.DamageVsAir, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FlakProximityFuzeTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FlakProximityFuzeTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FlakProximityFuzeTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FlakProximityFuzeTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.FlakProximityFuzeTop5)),
            new("airburst_shells", GearSlot.TowerWeapon, NoBranch, StatId.Splash, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AirburstShellsTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AirburstShellsTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AirburstShellsTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AirburstShellsTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AirburstShellsTop5)),
            // Gear balance 04/10: ProjectileSpeed 0.08/0.12/0.16/0.20/0.25 -> 0.06/0.09/0.12/0.15/0.18 (main FireRate unchanged).
            new("ammo_hoist", GearSlot.TowerWeapon, NoBranch, StatId.ProjectileSpeed, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHoistTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHoistTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHoistTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHoistTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHoistTop5)) { Main = StatId.FireRate },

            // Structure: main stat +health (screens: less damage taken; the engineer bay: repairs out of combat).
            new("reinforced_concrete", GearSlot.TowerStructure, NoBranch, StatId.ResistHighExplosive, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("composite_casemate", GearSlot.TowerStructure, NoBranch, StatId.ResistShapedCharge, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),
            new("blast_walls", GearSlot.TowerStructure, NoBranch, StatId.ResistIndirect, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BlastWallsTop1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BlastWallsTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BlastWallsTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BlastWallsTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BlastWallsTop5)) { Plating = true },
            new("slat_screens", GearSlot.TowerStructure, NoBranch, StatId.ResistRocket, V(0.06f, 0.09f, 0.13f, 0.17f, 0.22f)) { Plating = true },
            new("engineer_bay", GearSlot.TowerStructure, NoBranch, StatId.RegenDelay, V(1f, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.EngineerBayTop2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.EngineerBayTop3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.EngineerBayTop4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.EngineerBayTop5)) { Main = StatId.Regen },
            // Gear balance 04/10 (new): energy damage cut after it has gone past any shield (energy still bypasses shields).
            new("grounding_mesh", GearSlot.TowerStructure, NoBranch, StatId.ResistEnergy, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f)),

            // Systems: main stat +vision (traverse motors: turret turn rate; ammunition handling: magazine reload).
            new("search_radar", GearSlot.TowerSystems, NoBranch, StatId.SpreadLong, V(0.08f, 0.12f, 0.16f, 0.2f, 0.25f)),
            new("traverse_motors", GearSlot.TowerSystems, NoBranch, StatId.Spread, V(0.04f, 0.06f, 0.09f, 0.12f, 0.15f))
                { Main = StatId.TurretRate, MainScale = global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.TraverseMotorsMainScale },
            // Gear balance 04/10: Magazine 0.10-0.30 -> 0.08-0.24. Gear targets 04/10 (owner): effective magazine reload
            // 10 / 15 / 20 / 25 / 30 %: no MainScale (was 1.25: 3.75-17.5 %), the main line 0.03-0.14 plus a second implicit.
            new("ammo_handling", GearSlot.TowerSystems, NoBranch, StatId.Magazine, V(0.08f, 0.12f, 0.16f, 0.2f, 0.24f))
                { Main = StatId.MagazineReload, Implicit2 = StatId.MagazineReload, Top2 = V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHandlingTop2N1, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHandlingTop2N2, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHandlingTop2N3, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHandlingTop2N4, global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.AmmoHandlingTop2N5) },
        };

        /// <summary>
        /// The traits tower pieces roll, Epic / Legendary. The brief's numbers are the Legendary
        /// ones (Fire Link +15 %, Counter-Battery 6 s); the one-a-battle, below-half-health and
        /// immunity rules are fixed. Vehicle traits in these pools keep their vehicle numbers.
        /// </summary>
        public static readonly TraitDef[] TowerTraits =
        {
            // Weapon
            new(TraitId.TowerFireLink, GearSlot.TowerWeapon, NoBranch, V(0.1f, 3f), V(0.15f, 3f)) { Need = TowerNeed.Armed },
            new(TraitId.Executioner, GearSlot.TowerWeapon, NoBranch, V(0.4f), V(0.6f)) { Need = TowerNeed.Armed },
            new(TraitId.OpeningSalvo, GearSlot.TowerWeapon, NoBranch, V(0.5f), V(0.8f)) { Need = TowerNeed.Armed },
            // Structure
            new(TraitId.TowerModular, GearSlot.TowerStructure, NoBranch, V(0.5f), V(1f)),
            // Play-test 14 lane I: hidden (the player's smoke gear waits; see TraitDef.Hidden).
            new(TraitId.TowerSmokeLaunchers, GearSlot.TowerStructure, NoBranch, V(10f, 12f), V(14f, 16f)) { Hidden = true },
            new(TraitId.AegisBarrier, GearSlot.TowerStructure, NoBranch, V(0.1f, 20f), V(0.15f, 16f)),
            new(TraitId.AblativeLayer, GearSlot.TowerStructure, NoBranch, V(0.2f), V(0.3f)),
            // Systems
            new(TraitId.TowerCounterBattery, GearSlot.TowerSystems, NoBranch, V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.TowerCounterBatteryEpic1), V(global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.TowerCounterBatteryLegendary1)),
            new(TraitId.TowerBackupGenerator, GearSlot.TowerSystems, NoBranch, V(0.5f), V(1f)) { Need = TowerNeed.Armed },
            new(TraitId.LaserDesignator, GearSlot.TowerSystems, NoBranch, V(0.08f, 4f), V(0.12f, 6f)) { Need = TowerNeed.Armed },
        };

        /// <summary>Which tower slots each sub-stat rolls on (values as on vehicles, from <see cref="Subs"/>); a stat not listed never rolls on a tower.</summary>
        private static readonly Dictionary<StatId, GearSlot[]> TowerSubSlots = new()
        {
            [StatId.DamageVsLight] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.DamageVsHeavy] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.DamageVsAir] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.FireRate] = new[] { GearSlot.TowerWeapon },
            [StatId.Damage] = new[] { GearSlot.TowerSystems },
            [StatId.Range] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.Spread] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.ProjectileSpeed] = new[] { GearSlot.TowerWeapon },
            [StatId.Magazine] = new[] { GearSlot.TowerWeapon },
            [StatId.MagazineReload] = new[] { GearSlot.TowerWeapon, GearSlot.TowerSystems },
            [StatId.Health] = new[] { GearSlot.TowerStructure, GearSlot.TowerSystems },
            [StatId.ResistKinetic] = new[] { GearSlot.TowerStructure },
            [StatId.ResistShapedCharge] = new[] { GearSlot.TowerStructure },
            [StatId.ResistHighExplosive] = new[] { GearSlot.TowerStructure },
            [StatId.ResistFire] = new[] { GearSlot.TowerStructure },
            [StatId.ResistFragmentation] = new[] { GearSlot.TowerStructure },
            [StatId.TurretRate] = new[] { GearSlot.TowerSystems },
            [StatId.Regen] = new[] { GearSlot.TowerStructure },
        };

        /// <summary>
        /// What a tower type's three pieces may add to each stat: the vehicle caps, but range stops
        /// at +10 % (a base's reach is what attackers plan round) and regeneration at 1 % a second
        /// (a fixed target must still be crackable by siege fire).
        /// </summary>
        public static readonly float[] TowerStatCap = BuildTowerCaps();

        private static float[] BuildTowerCaps()
        {
            // Built from scratch, not from StatCap: static fields in the parts of a partial class
            // initialise in no set order.
            var caps = BuildCaps();
            caps[(int)StatId.Range] = global::MachineBrigade.Sim.Content.SimTunables.Bases.GearCatalog.BuildTowerCapsCaps;
            caps[(int)StatId.Regen] = 0.01f;
            return caps;
        }

        /// <summary>Whether a sub-stat rolls on this slot (a vehicle slot's own list, or the tower table).</summary>
        public static bool RollsOn(SubDef sub, GearSlot slot) =>
            Gear.IsTower(slot) ? TowerSubSlots.TryGetValue(sub.Stat, out var slots) && System.Array.IndexOf(slots, slot) >= 0 : sub.RollsOn(slot);

        public static IEnumerable<BaseTypeDef> TowerBasesFor(GearSlot slot)
        {
            foreach (var b in TowerBases)
                if (b.Slot == slot && !b.Hidden) yield return b;
        }

        public static IEnumerable<TraitDef> TowerTraitsFor(GearSlot slot)
        {
            foreach (var t in TowerTraits)
                if (t.Slot == slot && !t.Hidden) yield return t;
        }

        /// <summary>A trait as a piece of this slot carries it: a tower slot's own entry (its numbers and needs), else the vehicle one.</summary>
        public static TraitDef TraitFor(GearSlot slot, string key)
        {
            var id = GearKeys.ParseTrait(key);
            if (Gear.IsTower(slot))
                foreach (var t in TowerTraits)
                    if (t.Id == id && t.Slot == slot) return t;
            return Trait(id);
        }
    }
}

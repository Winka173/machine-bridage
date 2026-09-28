using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// What a tower must have for a piece of tower equipment, a stat line or a trait to do anything.
    /// The weapon needs include <see cref="Armed"/>, so a need is met exactly when all its bits are
    /// among a tower's (<see cref="TowerFit.Within"/>).
    /// </summary>
    [Flags]
    public enum TowerNeed
    {
        /// <summary>Works on any tower (health, resistances, vision, the Modular re-drop, smoke).</summary>
        None = 0,

        /// <summary>A weapon that does damage (damage, rate of fire, range, accuracy, traverse).</summary>
        Armed = 1,

        /// <summary>A weapon made for ground targets (damage against light, heavy and structures).</summary>
        HitsGround = 2 | Armed,

        /// <summary>A weapon made for aircraft (damage against aircraft, a proximity fuze).</summary>
        HitsAir = 4 | Armed,

        /// <summary>A weapon with a magazine that runs dry and reloads (magazine size and reload).</summary>
        Magazine = 8 | Armed,

        /// <summary>Something that drives (speed, turning, capturing): never a tower.</summary>
        Mobile = 16,
    }

    /// <summary>
    /// Which tower types a piece of tower equipment works for, read from the data: a tower's
    /// weapons say what it has (<see cref="Of(VehicleDef)"/>), a stat line what it needs
    /// (<see cref="Need(StatId)"/>), a base type what its main and implicit lines need, a trait
    /// what its catalogue entry says. A piece's sub-stats and trait are only ever rolled within its
    /// base type's need, so every line of a piece works on every tower it fits. This is the data
    /// the equipment fit matrix reads (<see cref="Matrix"/>).
    /// </summary>
    public static class TowerFit
    {
        /// <summary>Whether everything <paramref name="need"/> asks for is in <paramref name="has"/>.</summary>
        public static bool Within(TowerNeed need, TowerNeed has) => (need & ~has) == 0;

        /// <summary>
        /// What a tower (or branch) def has. Its main weapon counts for what it can target; a
        /// secondary only for what it is made for (a coaxial machine gun that can also shoot at
        /// aircraft does not make a gun tower an anti-air one; a SAM box on the roof does).
        /// Weapons that do no damage do not count: an obstacle has nothing.
        /// </summary>
        public static TowerNeed Of(VehicleDef def)
        {
            var has = TowerNeed.None;
            if (def == null) return has;
            for (var i = 0; i < def.Mounts.Count; i++)
            {
                var w = def.Mounts[i].Weapon;
                if (w == null || w.Damage <= 0f) continue;
                has |= TowerNeed.Armed;
                var main = i == 0;
                if (w.CanTarget(false) && (main || !w.CanTarget(true))) has |= TowerNeed.HitsGround;
                if (w.CanTarget(true) && (main || w.DamageType == DamageType.Flak || w.Targets == TargetLayers.Air)) has |= TowerNeed.HitsAir;
                if (w.Ammo > 0) has |= TowerNeed.Magazine;
            }
            return has;
        }

        /// <summary>What a tower needs for this stat line to change anything.</summary>
        public static TowerNeed Need(StatId stat) => stat switch
        {
            StatId.Damage or StatId.FireRate or StatId.Range or StatId.Spread or StatId.ProjectileSpeed or StatId.TurretRate or StatId.SpreadLong
                or StatId.Splash or StatId.SecondaryFireRate or StatId.SalvoInterval or StatId.BurnDamage => TowerNeed.Armed,
            StatId.DamageVsLight or StatId.DamageVsHeavy or StatId.DamageVsStructure => TowerNeed.HitsGround,
            StatId.DamageVsAir => TowerNeed.HitsAir,
            StatId.Magazine or StatId.MagazineReload => TowerNeed.Magazine,
            StatId.Speed or StatId.TurnRate or StatId.CaptureRate or StatId.TransitSpeed or StatId.SpreadMoving or StatId.SummonPower => TowerNeed.Mobile,
            _ => TowerNeed.None,
        };

        /// <summary>What a base type's main and implicit lines need (its drawback, if any, does not count).</summary>
        public static TowerNeed Need(BaseTypeDef b)
        {
            if (b == null) return TowerNeed.None;
            var need = Need(Gear.MainStatOf(b));
            if (b.Implicit != StatId.Count) need |= Need(b.Implicit);
            return need;
        }

        /// <summary>What a trait in a tower pool needs.</summary>
        public static TowerNeed Need(TraitDef t) => t?.Need ?? TowerNeed.None;

        /// <summary>What a piece needs: all its lines together (a vehicle piece is never a tower's: <see cref="TowerNeed.Mobile"/>).</summary>
        public static TowerNeed Need(GearItem item)
        {
            if (item == null || !Gear.IsTower(item.Slot)) return TowerNeed.Mobile;
            var b = Gear.BaseOf(item);
            var need = b != null ? Need(b) : Need(Gear.MainStat(item));
            if (item.subs != null)
                foreach (var sub in item.subs)
                    need |= Need(sub.Stat);
            if (item.rarity >= (int)Rarity.Epic && !string.IsNullOrEmpty(item.trait)) need |= Need(GearCatalog.TraitFor(item.Slot, item.trait));
            return need;
        }

        /// <summary>Whether a piece works for this tower type (a tower card or branch def).</summary>
        public static bool Fits(GearItem item, VehicleDef tower) =>
            item != null && Gear.IsTower(item.Slot) && IsTowerCard(tower) && Within(Need(item), Of(tower));

        public static bool Fits(TowerNeed need, VehicleDef tower) => IsTowerCard(tower) && Within(need, Of(tower));

        /// <summary>A tower of a base loadout (or one of its branches): what tower equipment is for.</summary>
        public static bool IsTowerCard(VehicleDef def) => def != null && def.Fort is { Kind: FortKind.Tower } && TowerCards.IsLoadoutTower(def.CardId);

        /// <summary>The tower cards (not branches) a piece works for, in catalogue order.</summary>
        public static List<string> TowersFor(GearItem item, Catalog catalog)
        {
            var list = new List<string>();
            foreach (var id in TowerCards.All(catalog))
                if (Fits(item, catalog.Vehicles[id]))
                    list.Add(id);
            return list;
        }

        /// <summary>One row of the fit matrix: a tower card (or branch), what it has, and the base types and traits of each tower slot that work for it.</summary>
        public sealed class Row
        {
            public string Tower;
            public TowerNeed Has;
            public readonly List<string> Bases = new();
            public readonly List<string> Traits = new();
        }

        /// <summary>
        /// The fit matrix: for every tower card and branch def, the tower base types and traits that
        /// work for it (a base type's own lines, a trait's catalogue need).
        /// </summary>
        public static List<Row> Matrix(Catalog catalog)
        {
            var rows = new List<Row>();
            foreach (var def in catalog.Vehicles.Values)
            {
                if (!IsTowerCard(def)) continue;
                var row = new Row { Tower = def.Id, Has = Of(def) };
                foreach (var b in GearCatalog.TowerBases)
                    if (Within(Need(b), row.Has))
                        row.Bases.Add(b.Id);
                foreach (var t in GearCatalog.TowerTraits)
                    if (Within(t.Need, row.Has) && !row.Traits.Contains(t.Key))
                        row.Traits.Add(t.Key);
                rows.Add(row);
            }
            return rows;
        }

        // ------------------------------------------------------------------ the game's catalogue

        private static Catalog _catalog;
        private static readonly Dictionary<string, TowerNeed> HasById = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _catalog = null;
            HasById.Clear();
        }

        /// <summary>The game's catalogue, read once (menus ask about fits often).</summary>
        internal static Catalog GameCatalog => _catalog ??= GameContent.LoadCatalog();

        /// <summary>What a def of the game's catalogue has (cached); None for an unknown id.</summary>
        public static TowerNeed Of(string defId)
        {
            if (string.IsNullOrEmpty(defId)) return TowerNeed.None;
            if (HasById.TryGetValue(defId, out var has)) return has;
            has = GameCatalog.Vehicles.TryGetValue(defId, out var def) ? Of(def) : TowerNeed.None;
            HasById[defId] = has;
            return has;
        }
    }
}

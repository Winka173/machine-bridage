#nullable enable
using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 22 F: each side's commander (or enemy general) for the battle. Set before the forces are placed: a unit
    /// takes its commander's lines as it enters (through the loadout's caps, <see cref="CommanderRules.Merge"/>), the
    /// side's economy its prices and income, and the abilities, sight and damage read the side-wide numbers here.
    /// </summary>
    public sealed partial class SimWorld
    {
        private readonly CommanderDef?[] _commanders = new CommanderDef?[3];
        private readonly float[] _stealthSight = { 1f, 1f, 1f };
        private float[] _statCaps = CommanderRules.DefaultCaps;
        private float[] _towerCaps = CommanderRules.DefaultCaps;

        /// <summary>Capture points are fought over in this battle (set by the point rules as they run; Flag's weakness is for a battle without them).</summary>
        public bool PointsInPlay { get; internal set; }

        /// <summary>A side's commander (null: none).</summary>
        public CommanderDef? CommanderOf(int team) => team >= 0 && team < _commanders.Length ? _commanders[team] : null;

        /// <summary>The loadout caps a commander's lines count towards: a vehicle's and a tower's (the Game's gear tables).</summary>
        public void SetStatCaps(float[]? vehicles, float[]? towers)
        {
            _statCaps = vehicles ?? CommanderRules.DefaultCaps;
            _towerCaps = towers ?? _statCaps;
        }

        /// <summary>Gives a side its commander for the battle (null: none). Call it before the side's forces are placed.</summary>
        public void SetCommander(int team, CommanderDef? commander)
        {
            if (team < 0 || team >= _commanders.Length) return;
            _commanders[team] = commander;
            _stealthSight[team] = commander?.StealthSight ?? 1f;
            if (Economy.TryGet(team, out var economy)) ApplyCommander(economy);
        }

        /// <summary>The side's commander in its economy: prices by card, income and the bank.</summary>
        private void ApplyCommander(TeamEconomy economy)
        {
            var c = CommanderOf(economy.Team);
            economy.Commander = c;
            economy.PriceScales.Clear();
            if (c == null || c.Prices.Count == 0) return;
            foreach (var def in Catalog.Vehicles.Values)
            {
                var scale = CommanderRules.PriceScale(c, def);
                if (scale != 1f) economy.PriceScales[def.Id] = scale;
            }
            foreach (var s in Catalog.Supports.Values)
            {
                var scale = CommanderRules.PriceScale(c, s);
                if (scale != 1f) economy.PriceScales[s.Id] = scale;
            }
        }

        /// <summary>A unit's boost with its side's commander on top (the unit's own boost when no line reaches it).</summary>
        private VehicleBoost? CommanderBoost(int team, VehicleDef def, VehicleBoost? boost)
        {
            if (CommanderOf(team) is not { } c || !Touches(c, def)) return boost;
            return CommanderRules.Merge(boost ?? VehicleBoost.None, c, def, def.Static ? _towerCaps : _statCaps);
        }

        private static bool Touches(CommanderDef c, VehicleDef def)
        {
            foreach (var l in c.Lines)
                if (CommanderRules.Reaches(l.Reach, def)) return true;
            return false;
        }

        /// <summary>How much farther a side sees stealthy, camouflaged and hidden enemies (1: as usual).</summary>
        internal float StealthSightOf(int team) => team >= 0 && team < _stealthSight.Length ? _stealthSight[team] : 1f;

        /// <summary>A side's engineers and repair bays: their repair rate multiplier.</summary>
        internal float RepairScaleOf(int team) => CommanderOf(team)?.Repair ?? 1f;

        /// <summary>How fast a vehicle rearms under its commander (an aircraft under Hawk: 15 % faster).</summary>
        internal float RearmScaleOf(Vehicle v) => v.Flying && CommanderOf(v.Team) is { } c ? c.AirRearm : 1f;

        /// <summary>A guided round a jammer caught: a side's drones shrug off a share of it (Dr. Venn's).</summary>
        internal bool ShrugsJam(Vehicle shooter, WeaponDef weapon)
        {
            if (CommanderOf(shooter.Team) is not { JamResist: > 0f } c) return false;
            if (!shooter.Def.Drone && weapon.Projectile != ProjectileKind.Drone) return false;
            return Random.NextDouble() < c.JamResist;
        }

        /// <summary>
        /// A hit's damage multiplier from the attacking side's commander: more from a unit under half health (Titan's),
        /// more on an enemy the side has marked or revealed (Captain Kerr's).
        /// </summary>
        internal float CommanderOutgoing(Vehicle? attacker, int team, IDamageable target)
        {
            if (CommanderOf(team) is not { } c) return 1f;
            var f = 1f;
            if (c.LowHpDamage != 1f && attacker != null && attacker.Team == team && attacker.Hp < attacker.MaxHp * 0.5f && CommanderRules.Fields(attacker.Def))
                f *= c.LowHpDamage;
            if (c.ExposedTaken != 1f && target is Vehicle v && v.Team != team && _combat.Marked(v, team)) f *= c.ExposedTaken;
            return f;
        }

        /// <summary>Aircraft a side's commander adds to its air cap.</summary>
        internal int CommanderAirCap(int team) => CommanderOf(team)?.AirCap ?? 0;
    }
}

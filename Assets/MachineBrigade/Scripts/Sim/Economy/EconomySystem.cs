#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Economy
{
    /// <summary>
    /// One side's Command Points and deck (game plan section 2). CP regenerate over time, up to a
    /// bank cap; kills refund a quarter of the victim's cost. There is no hard army cap: an army
    /// bigger than its supply (<see cref="ArmyCap"/>) costs upkeep, which slows the income, so
    /// a side can always buy but a huge army starves its own reinforcements. Only a vehicle
    /// count far above any real army stops purchases, to keep phones fast.
    /// </summary>
    public sealed class TeamEconomy
    {
        internal readonly Dictionary<string, double> ReadyAt = new();

        public TeamEconomy(int team, float startCp = 12f, float income = 1f, float bank = 30f, int armyCap = 24,
            IReadOnlyList<string>? vehicles = null, IReadOnlyList<string>? supports = null)
        {
            Team = team;
            Cp = startCp;
            _income = income;
            Bank = bank;
            _armyCap = armyCap;
            Vehicles = vehicles ?? Array.Empty<string>();
            Supports = supports ?? Array.Empty<string>();
        }

        public int Team { get; }
        public float Cp { get; internal set; }

        /// <summary>CP per second before objective bonuses.</summary>
        public float Income => _income * (Doctrine?.Income ?? 1f) * IncomeScale;

        /// <summary>The catalog's economy pace: scales the income and objective bonuses (1: as the mode set them).</summary>
        public float IncomeScale { get; internal set; } = 1f;

        /// <summary>The catalog's scale for the supply line (1: as the mode set it).</summary>
        public float SupplyScale { get; internal set; } = 1f;

        private readonly float _income;
        private readonly int _armyCap;

        /// <summary>The commander's doctrine for this battle, or none.</summary>
        public Content.Doctrine? Doctrine { get; set; }

        /// <summary>Extra CP per second, set by the game mode (for example per held objective).</summary>
        public float Bonus { get; set; }

        public float Bank { get; }

        /// <summary>Supply: the army value the side keeps up at full income; above it, upkeep sets in.</summary>
        public int ArmyCap => (int)MathF.Round((_armyCap + (Doctrine?.ArmyCap ?? 0)) * SupplyScale);

        /// <summary>Vehicles one side may have on the field (and on the way) at once: a safety limit for performance.</summary>
        public const int MaxVehicles = 32;

        /// <summary>
        /// Aircraft one side may have up at once (and on the way), like the air slots of Wargame
        /// and World in Conflict: air power is a scarce, dear asset, not a swarm.
        /// </summary>
        public const int MaxAircraft = 6;

        /// <summary>
        /// Army value kept up at full income: half again the mode's old army cap, so a normal
        /// army never pays upkeep and only a swarm does.
        /// </summary>
        public int Supply => ArmyCap * 3 / 2;

        /// <summary>
        /// Share of the income left after upkeep: full up to the supply, then falling steadily
        /// (half at twice the supply) to a floor of a quarter.
        /// </summary>
        public float Upkeep => UpkeepFor(ArmyCp, Supply);

        public static float UpkeepFor(int armyCp, int supply)
        {
            if (supply <= 0 || armyCp <= supply) return 1f;
            return MathF.Max(0.25f, 1f - 0.5f * (armyCp - supply) / supply);
        }

        /// <summary>CP per second actually earned now: income and bonuses after upkeep.</summary>
        public float Earning => (Income + Bonus * IncomeScale) * Upkeep;

        /// <summary>Vehicles on the field plus deliveries on the way.</summary>
        public int VehicleCount { get; internal set; }

        /// <summary>Vehicle cards in the deck (empty: any vehicle).</summary>
        public IReadOnlyList<string> Vehicles { get; }

        /// <summary>Support cards in the deck (empty: any support).</summary>
        public IReadOnlyList<string> Supports { get; }

        /// <summary>CP value of this side's army on the field plus deliveries on the way.</summary>
        public int ArmyCp { get; internal set; }

        /// <summary>Chance that a delivered vehicle arrives as its elite version (enemy difficulty).</summary>
        public float EliteChance { get; set; }

        /// <summary>Single-use items this side carries into the match (bought with coins), by support id.</summary>
        public Dictionary<string, int> Items { get; } = new();

        public int ItemCount(string supportId) => Items.TryGetValue(supportId, out var n) ? n : 0;

        public float CooldownLeft(string supportId, double now) =>
            ReadyAt.TryGetValue(supportId, out var ready) ? (float)Math.Max(0.0, ready - now) : 0f;
    }

    /// <summary>Command Point income, purchases, deliveries and kill rewards for every side that has an economy.</summary>
    internal sealed class EconomySystem
    {
        /// <summary>Seconds between buying a vehicle and it arriving at the drop zone.</summary>
        public const float DeliverySeconds = 2.5f;

        /// <summary>How far past the drop zone a delivered vehicle drives, so the zone stays clear.</summary>
        private const float RollIn = 12f;

        private const float KillReward = 0.25f;

        private readonly SimWorld _world;
        private readonly Dictionary<int, TeamEconomy> _teams = new();
        private readonly List<(int team, string defId, double due)> _pending = new();
        private readonly List<EntityId> _single = new(1);
        private int _deliveries;

        public EconomySystem(SimWorld world) => _world = world;

        public void Enable(TeamEconomy economy) => _teams[economy.Team] = economy;

        public bool TryGet(int team, out TeamEconomy economy) => _teams.TryGetValue(team, out economy!);

        public CommandResult Deploy(int team, string? defId)
        {
            if (!_teams.TryGetValue(team, out var economy)) return CommandResult.Rejected(CommandError.NotAvailable);
            if (defId == null || !_world.Catalog.Vehicles.TryGetValue(defId, out var def))
                return CommandResult.Rejected(CommandError.UnknownCard);
            if (economy.Vehicles.Count > 0 && !Contains(economy.Vehicles, defId)) return CommandResult.Rejected(CommandError.UnknownCard);
            if (!_world.TryGetRally(team, out var zone)) return CommandResult.Rejected(CommandError.NoRallyPoint);
            if (economy.Cp < def.CpCost) return CommandResult.Rejected(CommandError.NotEnoughCp);
            if (VehicleCount(team) >= TeamEconomy.MaxVehicles) return CommandResult.Rejected(CommandError.ArmyAtCapacity);
            if (def.Flying && AircraftCount(team) >= TeamEconomy.MaxAircraft) return CommandResult.Rejected(CommandError.AirAtCapacity);

            // Charged exactly once, when accepted (T03).
            economy.Cp -= def.CpCost;
            _pending.Add((team, defId, _world.Time + DeliverySeconds));
            economy.ArmyCp = ArmyCp(team);
            economy.VehicleCount = VehicleCount(team);
            _world.Emit(SimEvent.DeploymentQueued(team, defId, zone, DeliverySeconds));
            return CommandResult.Ok;
        }

        /// <summary>Spends CP for a strike; the caller has already validated everything else.</summary>
        public bool TrySpend(int team, int cost)
        {
            if (!_teams.TryGetValue(team, out var economy)) return true; // modes without an economy call strikes freely
            if (economy.Cp < cost) return false;
            economy.Cp -= cost;
            return true;
        }

        public void Step(float dt)
        {
            foreach (var economy in _teams.Values)
            {
                economy.ArmyCp = ArmyCp(economy.Team);
                economy.VehicleCount = VehicleCount(economy.Team);
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + economy.Earning * dt);
            }

            for (var i = _pending.Count - 1; i >= 0; i--)
            {
                var (team, defId, due) = _pending[i];
                if (due > _world.Time) continue;
                _pending.RemoveAt(i);
                Deliver(team, defId);
            }
        }

        /// <summary>
        /// Pays the side that dealt the last damage (recently), even if the shooter died with its
        /// shell still in the air, and for strike kills.
        /// </summary>
        public void OnVehicleDestroyed(Vehicle victim)
        {
            var team = victim.LastAttackerTeam;
            if (team < 0 || team == victim.Team || _world.Time - victim.LastHitTime > 10.0) return;
            if (_teams.TryGetValue(team, out var economy))
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + victim.Def.ArmyCost * KillReward);
        }

        private void Deliver(int team, string defId)
        {
            if (!_world.TryGetRally(team, out var zone)) return;
            // Deliveries fan out around the zone so consecutive ones do not stack.
            var index = _deliveries++;
            var angle = index * 2.39996f;
            var offset = new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (2f + (index % 5) * 1.5f);
            var inward = Vector2.Normalize(-zone == Vector2.Zero ? Vector2.UnitY : -zone);
            // Veteran crews: some deliveries turn up as the refurbished elite version.
            if (_teams.TryGetValue(team, out var economy) && economy.EliteChance > 0f &&
                _world.Catalog.EliteVariant(defId) is { } elite && _world.Random.NextDouble() < economy.EliteChance)
                defId = elite;
            var vehicle = _world.SpawnVehicle(defId, team, zone + offset, SimMath.HeadingOf(inward));
            _single.Clear();
            _single.Add(vehicle.Id);
            _world.Submit(new Command(CommandType.Move, team, _single, _world.ClampToMap(vehicle.Position + inward * RollIn)));
        }

        private int ArmyCp(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team) total += v.Def.ArmyCost;
            foreach (var (pendingTeam, defId, _) in _pending)
                if (pendingTeam == team) total += _world.Catalog.Vehicle(defId).CpCost;
            return total;
        }

        /// <summary>Aircraft a side has up, plus those on the way.</summary>
        public int AircraftCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Flying && !v.Def.Boss && !v.Scripted) total++;
            foreach (var (pendingTeam, id, _) in _pending)
                if (pendingTeam == team && _world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Flying) total++;
            return total;
        }

        private int VehicleCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Scripted) total++;
            foreach (var (pendingTeam, _, _) in _pending)
                if (pendingTeam == team) total++;
            return total;
        }

        private static bool Contains(IReadOnlyList<string> list, string id)
        {
            foreach (var item in list)
                if (item == id) return true;
            return false;
        }
    }
}

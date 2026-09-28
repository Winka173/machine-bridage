#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
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
    /// In the quick modes (<see cref="SimWorld.CatchUp"/>) the side that is losing the war of
    /// armies is reinforced faster and paid more for its kills, so one side cannot simply roll
    /// the other over (see <see cref="EconomySystem"/>).
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

        /// <summary>
        /// The underdog's reinforcement boost: 1 while the armies are close, up to
        /// 1 + <see cref="EconomySystem.MaxCatchUp"/> for a side whose army has been shot to pieces.
        /// </summary>
        public float CatchUp { get; internal set; } = 1f;

        /// <summary>CP per second actually earned now: income and bonuses after upkeep, and the underdog's boost.</summary>
        public float Earning => (Income + Bonus * IncomeScale) * Upkeep * CatchUp;

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

        /// <summary>CP off a card's price for this side (its rank: see the game's CardRanks.CallCut), by card id.</summary>
        public Dictionary<string, int> Discounts { get; } = new();

        /// <summary>Scales this side's income (the campaign enemy keeping pace with a discounted deck).</summary>
        public void ScaleIncome(float factor) => IncomeScale *= factor;

        /// <summary>What calling this card costs this side: its price less its rank's cut, never below 1.</summary>
        public int CostOf(string id, int price) => Discounts.TryGetValue(id, out var cut) ? Math.Max(1, price - cut) : price;

        public float CooldownLeft(string supportId, double now) =>
            ReadyAt.TryGetValue(supportId, out var ready) ? (float)Math.Max(0.0, ready - now) : 0f;
    }

    /// <summary>
    /// Command Point income, purchases, deliveries and kill rewards for every side that has an economy.
    /// <para>
    /// Catch-up (the quick modes only; campaign missions are balanced by hand): a snowball is the
    /// bigger army winning every fight, taking the points and earning more for it. Like the
    /// reinforcement points of World in Conflict and the bounties of Dota, two gentle levers
    /// work against it. The side whose army is under three quarters of the other's is
    /// reinforced faster, up to half again at a fifth or less; and a kill pays by the odds: the
    /// underdog knocking out a unit of the bigger army earns up to half as much again, the
    /// bigger army picking off the last of the smaller one earns as little as half. Neither
    /// changes a close fight; together with the home zones' repair and invulnerable bastions
    /// they give a beaten side the time and means to come back.
    /// </para>
    /// </summary>
    internal sealed class EconomySystem
    {
        /// <summary>The underdog's biggest reinforcement boost (0.5: half again the income).</summary>
        public const float MaxCatchUp = 0.5f;

        /// <summary>The underdog's boost starts once its army falls under this share of the other's.</summary>
        private const float CatchUpBelow = 0.75f;

        /// <summary>Armies too small to judge (the opening, a wiped board) change nothing.</summary>
        private const int CatchUpMinimumArmy = 14;

        /// <summary>Seconds for the boost to settle to a change in the odds (no flicker as units die and arrive).</summary>
        private const float CatchUpSettle = 4f;

        /// <summary>
        /// Seconds between buying a vehicle and it arriving: long enough for the transport to fly
        /// over and the vehicle to come down under its parachute onto its landing point (the drop
        /// is drawn by the game; aircraft fly in from the map's edge instead).
        /// </summary>
        public const float DeliverySeconds = 3.5f;

        /// <summary>How far past the drop zone a delivered vehicle drives, so the zone stays clear.</summary>
        private const float RollIn = 12f;

        private const float KillReward = 0.25f;

        private readonly SimWorld _world;
        private readonly Dictionary<int, TeamEconomy> _teams = new();
        private readonly List<(int team, string defId, double due, Vector2 landing)> _pending = new();
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
            // A ranked card costs less to call (the army's value, upkeep and refunds keep its full price).
            var price = economy.CostOf(defId, def.CpCost);
            if (economy.Cp < price) return CommandResult.Rejected(CommandError.NotEnoughCp);
            if (VehicleCount(team) >= TeamEconomy.MaxVehicles) return CommandResult.Rejected(CommandError.ArmyAtCapacity);
            if (def.Flying && AircraftCount(team) >= TeamEconomy.MaxAircraft) return CommandResult.Rejected(CommandError.AirAtCapacity);

            // Charged exactly once, when accepted (T03).
            economy.Cp -= price;
            if (def.Flying) _world.CountAircraft(team);
            // Veteran crews: some deliveries turn up as the refurbished elite version. Decided now,
            // with the landing point, so the drop the game draws is the vehicle that lands.
            if (economy.EliteChance > 0f && _world.Catalog.EliteVariant(defId) is { } elite && _world.Random.NextDouble() < economy.EliteChance)
                defId = elite;
            // Deliveries fan out around the zone so consecutive ones do not stack.
            var index = _deliveries++;
            var angle = index * 2.39996f;
            var landing = zone + new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (2f + (index % 5) * 1.5f);
            _pending.Add((team, defId, _world.Time + DeliverySeconds, landing));
            economy.ArmyCp = ArmyCp(team);
            economy.VehicleCount = VehicleCount(team);
            _world.Emit(SimEvent.DeploymentQueued(team, defId, landing, Inward(zone), DeliverySeconds));
            return CommandResult.Ok;
        }

        /// <summary>
        /// A delivery nobody pays for (a mission enemy's reinforcements): it comes the way a bought
        /// vehicle does, dropped by parachute near <paramref name="near"/> (aircraft fly in over the
        /// edge), and needs no economy for the side.
        /// </summary>
        public void Airlift(int team, string defId, Vector2 near)
        {
            if (!_world.Catalog.Vehicles.ContainsKey(defId)) return;
            var index = _deliveries++;
            var angle = index * 2.39996f;
            var landing = _world.ClampToMap(near + new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (3f + (index % 5) * 2f));
            _pending.Add((team, defId, _world.Time + DeliverySeconds, landing));
            _world.Emit(SimEvent.DeploymentQueued(team, defId, landing, Inward(near), DeliverySeconds));
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
            }
            foreach (var economy in _teams.Values)
            {
                var target = _world.CatchUp && TryGetRival(economy.Team, out var rival) ? CatchUpFor(economy.ArmyCp, rival.ArmyCp) : 1f;
                economy.CatchUp += (target - economy.CatchUp) * MathF.Min(1f, dt / CatchUpSettle);
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + economy.Earning * dt);
            }

            for (var i = _pending.Count - 1; i >= 0; i--)
            {
                var (team, defId, due, landing) = _pending[i];
                if (due > _world.Time) continue;
                _pending.RemoveAt(i);
                Deliver(team, defId, landing);
            }
        }

        /// <summary>
        /// Pays the side that dealt the last damage (recently), even if the shooter died with its
        /// shell still in the air, and for strike kills.
        /// </summary>
        public void OnVehicleDestroyed(Vehicle victim, Vehicle? killer = null)
        {
            // Quartermaster's four-piece: part of its own cost comes back when it falls.
            if (victim.Gear != null && victim.Gear.Has(TraitId.SetSalvageRights) && _teams.TryGetValue(victim.Team, out var own))
                own.Cp = MathF.Min(own.Bank, own.Cp + victim.Def.CpCost * victim.Gear.Trait(TraitId.SetSalvageRights).B);
            var team = victim.LastAttackerTeam;
            if (team < 0 || team == victim.Team || _world.Time - victim.LastHitTime > 10.0) return;
            if (_teams.TryGetValue(team, out var economy))
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + victim.Def.ArmyCost * KillReward * Bounty(economy, victim) * KillerBonus(killer, team));
        }

        /// <summary>A killer's equipment that pays more for its kills (War Profiteer, Quartermaster's four-piece).</summary>
        private static float KillerBonus(Vehicle? killer, int team)
        {
            if (killer == null || killer.Team != team) return 1f;
            var bonus = 1f;
            if (killer.Special == SpecialModule.WarProfiteer) bonus += killer.SpecialPower;
            if (killer.Gear != null && killer.Gear.Has(TraitId.SetSalvageRights)) bonus += killer.Gear.Trait(TraitId.SetSalvageRights).A;
            return bonus;
        }

        /// <summary>
        /// The underdog's income boost for an army of <paramref name="own"/> CP against
        /// <paramref name="rival"/>: none down to three quarters of the rival's, then rising to
        /// <see cref="MaxCatchUp"/> at a fifth.
        /// </summary>
        public static float CatchUpFor(int own, int rival)
        {
            if (rival < CatchUpMinimumArmy) return 1f;
            var odds = own / (float)rival;
            return 1f + MaxCatchUp * Math.Clamp((CatchUpBelow - odds) / (CatchUpBelow - 0.2f), 0f, 1f);
        }

        /// <summary>
        /// A kill's pay by the odds (catch-up only): the square root of the victim side's army over
        /// the killer's, from half to half as much again.
        /// </summary>
        private float Bounty(TeamEconomy killer, Vehicle victim)
        {
            if (!_world.CatchUp || !_teams.TryGetValue(victim.Team, out var loser)) return 1f;
            // The victim still counts: it was part of the army the killer was up against.
            var theirs = MathF.Max(CatchUpMinimumArmy, loser.ArmyCp + victim.Def.ArmyCost);
            var ours = MathF.Max(CatchUpMinimumArmy, killer.ArmyCp);
            return Math.Clamp(MathF.Sqrt(theirs / ours), 0.5f, 1.5f);
        }

        /// <summary>The one other side with an economy (the catch-up compares two armies).</summary>
        private bool TryGetRival(int team, out TeamEconomy rival)
        {
            rival = null!;
            if (_teams.Count != 2) return false;
            foreach (var economy in _teams.Values)
                if (economy.Team != team) rival = economy;
            return rival != null;
        }

        /// <summary>From a team's zone towards the middle of the map.</summary>
        private static Vector2 Inward(Vector2 zone) => zone.LengthSquared() > 0.01f ? Vector2.Normalize(-zone) : Vector2.UnitY;

        private void Deliver(int team, string defId, Vector2 landing)
        {
            if (!_world.TryGetRally(team, out var zone)) return;
            var inward = Inward(zone);
            var at = landing;
            // Aircraft fly in over the map's edge behind the zone instead of appearing on it.
            if (_world.Catalog.Vehicle(defId).Flying) at = EdgeBehind(zone, inward);
            var vehicle = _world.SpawnVehicle(defId, team, at, SimMath.HeadingOf(inward));
            _single.Clear();
            _single.Add(vehicle.Id);
            _world.Submit(new Command(CommandType.Move, team, _single, _world.ClampToMap(landing + inward * RollIn)));
        }

        /// <summary>The map's edge straight behind a zone (looking in from it), just inside the square.</summary>
        private Vector2 EdgeBehind(Vector2 zone, Vector2 inward)
        {
            var limit = _world.Map.HalfSize - 2f;
            var p = zone;
            for (var step = 0; step < 40 && MathF.Abs(p.X - inward.X * 4f) <= limit && MathF.Abs(p.Y - inward.Y * 4f) <= limit; step++)
                p -= inward * 4f;
            return p;
        }

        private int ArmyCp(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team) total += v.Def.ArmyCost;
            foreach (var (pendingTeam, defId, _, _) in _pending)
                if (pendingTeam == team) total += _world.Catalog.Vehicle(defId).CpCost;
            return total;
        }

        /// <summary>Aircraft a side has up, plus those on the way.</summary>
        public int AircraftCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Flying && !v.Def.Boss && !v.Scripted) total++;
            foreach (var (pendingTeam, id, _, _) in _pending)
                if (pendingTeam == team && _world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Flying) total++;
            return total;
        }

        private int VehicleCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Scripted) total++;
            foreach (var (pendingTeam, _, _, _) in _pending)
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

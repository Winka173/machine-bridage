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

        public TeamEconomy(int team, float startCp = 12f, float income = 1f, float bank = 30f, int armyCap = 0,
            IReadOnlyList<string>? vehicles = null, IReadOnlyList<string>? supports = null)
        {
            Team = team;
            Cp = startCp;
            _income = income;
            _bank = bank;
            _armyCap = armyCap;
            Vehicles = vehicles ?? Array.Empty<string>();
            Supports = supports ?? Array.Empty<string>();
        }

        public int Team { get; }
        public float Cp { get; internal set; }

        /// <summary>CP per second before objective bonuses.</summary>
        public float Income => _income * IncomeScale;

        /// <summary>The catalog's economy pace: scales the income and objective bonuses (1: as the mode set them).</summary>
        public float IncomeScale { get; internal set; } = 1f;

        /// <summary>Prompt 20 N: support cooldowns are multiplied by this (a Boss Hunt support).</summary>
        public float StrikeScale { get; internal set; } = 1f;

        /// <summary>The catalog's scale for the supply line (1: as the mode set it).</summary>
        public float SupplyScale { get; internal set; } = 1f;

        private readonly float _income;
        /// <summary>The mode's supply before scale (0 until the world fills it in from the catalog).</summary>
        private int _armyCap;

        /// <summary>Extra supply from the side's base (a logistics station) or anything else that adds to it.</summary>
        public int SupplyBonus { get; set; }

        internal int BaseArmyCap
        {
            get => _armyCap;
            set => _armyCap = value;
        }

        /// <summary>Prompt 22 F: the side's commander (or enemy general), or none (SimWorld.SetCommander).</summary>
        public CommanderDef? Commander { get; internal set; }

        /// <summary>Prompt 22 F: the commander's price change by card id (absent: the card's own price).</summary>
        internal Dictionary<string, float> PriceScales { get; } = new();

        /// <summary>Prompt 22 F: the commander's income multiplier now (its flat rate, a battle without points, a full purse, the opening).</summary>
        public float CommanderIncome { get; internal set; } = 1f;

        /// <summary>Extra CP per second, set by the game mode (for example per held objective).</summary>
        public float Bonus { get; set; }

        private float _bank;

        /// <summary>The bank before the commander's bonus (prompt 29 E1 moves it by mode).</summary>
        internal float BaseBank
        {
            get => _bank;
            set => _bank = value;
        }

        /// <summary>The most CP the side can hold (a commander may raise it: Vault's 30 to 45).</summary>
        public float Bank => _bank + (Commander?.BankBonus ?? 0f);

        /// <summary>Supply: the army value the side keeps up at full income; above it, upkeep sets in.</summary>
        public int ArmyCap => (int)MathF.Round((_armyCap + SupplyBonus) * SupplyScale * (Commander?.Supply ?? 1f));

        /// <summary>Vehicles one side may have on the field (and on the way) at once: a safety limit for performance.</summary>
        public const int MaxVehicles = 32;

        /// <summary>
        /// Most vehicles this side may have in the field or on the way (balance.json
        /// economy.vehicleCap: 32, the enemy's 48 in Siege, Defend, Endless and the big operations).
        /// </summary>
        public int VehicleCap { get; set; } = MaxVehicles;

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
        public float Earning => (Income + (Bonus * (Commander?.PointIncome ?? 1f) + Relay) * IncomeScale) * Upkeep * CatchUp * CommanderIncome;

        /// <summary>Prompt 17 C: CP per second its base's CP relays pay now (before the economy's pace, upkeep and the underdog's boost).</summary>
        public float Relay { get; internal set; }

        /// <summary>Vehicles on the field plus deliveries on the way.</summary>
        public int VehicleCount { get; internal set; }

        /// <summary>Vehicle cards in the deck (empty: any vehicle).</summary>
        public IReadOnlyList<string> Vehicles { get; }

        /// <summary>Support cards in the deck (empty: any support).</summary>
        public IReadOnlyList<string> Supports { get; }

        /// <summary>CP value of this side's army on the field plus deliveries on the way.</summary>
        public int ArmyCp { get; internal set; }

        /// <summary>Single-use items this side carries into the match (bought with coins), by support id.</summary>
        public Dictionary<string, int> Items { get; } = new();

        public int ItemCount(string supportId) => Items.TryGetValue(supportId, out var n) ? n : 0;

        /// <summary>CP off a card's price for this side (its rank: see the game's CardRanks.CallCut), by card id.</summary>
        public Dictionary<string, int> Discounts { get; } = new();

        /// <summary>Scales this side's income (the campaign enemy keeping pace with a discounted deck).</summary>
        public void ScaleIncome(float factor) => IncomeScale *= factor;

        /// <summary>What calling this card costs this side, to the whole CP (shown on the cards): see <see cref="PriceOf"/>.</summary>
        public int CostOf(string id, int price) => PriceScales.Count == 0 ? (Discounts.TryGetValue(id, out var cut) ? Math.Max(1, price - cut) : price)
            : Math.Max(1, SimMath.RoundHalfUp(PriceOf(id, price)));

        /// <summary>Prompt 29 S04 (R7): what calling the card costs this side now (rank discount, commander); never used to
        /// classify a card, pay a bounty or count supply (those use <see cref="VehicleDef.BaseCp"/>).</summary>
        public float RuntimeCallCost(string id, int baseCp) => PriceOf(id, baseCp);

        /// <summary>
        /// What calling this card costs this side: its price times the commander's change (prompt 22 F; CP are fractional,
        /// so a 15 % cut on a 3 CP card is worth its 0.45 CP), less its rank's cut, never below 1.
        /// </summary>
        public float PriceOf(string id, int price)
        {
            var scaled = PriceScales.TryGetValue(id, out var scale) ? price * scale : price;
            return Discounts.TryGetValue(id, out var cut) ? MathF.Max(1f, scaled - cut) : MathF.Max(MathF.Min(1f, price), scaled);
        }

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
    internal sealed partial class EconomySystem
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

        /// <summary>
        /// A side whose ground deliveries come in by the fortress's line (a train, or an aircraft
        /// onto a runway) instead of by parachute: when the next one gets in, where the vehicles get
        /// off and the way along the platform they line up (null for the side: the usual drop).
        /// </summary>
        internal Func<int, (double due, Vector2 at, Vector2 along)?>? Route { get; set; }

        /// <summary>A routed delivery's landing and time, or false for the usual parachute drop.</summary>
        private bool Routed(int team, VehicleDef def, int index, out double due, out Vector2 landing)
        {
            due = 0;
            landing = default;
            if (def.Flying || Route?.Invoke(team) is not { } route) return false;
            // Off the train (or out of the aircraft) one behind another along the platform.
            var k = index % 6;
            landing = route.at + route.along * ((k % 2 == 0 ? 1f : -1f) * (2f + (k / 2) * 5f));
            due = MathF.Max((float)(_world.Time + 1.0), (float)route.due);
            return true;
        }

        public void Enable(TeamEconomy economy) => _teams[economy.Team] = economy;

        public bool TryGet(int team, out TeamEconomy economy) => _teams.TryGetValue(team, out economy!);

        public CommandResult Deploy(int team, string? defId)
        {
            if (!_teams.TryGetValue(team, out var economy)) return CommandResult.Rejected(CommandError.NotAvailable);
            if (defId == null || !_world.Catalog.Vehicles.TryGetValue(defId, out var def))
                return CommandResult.Rejected(CommandError.UnknownCard);
            if (economy.Vehicles.Count > 0 && !Contains(economy.Vehicles, defId)) return CommandResult.Rejected(CommandError.UnknownCard);
            // The drop zone: round the HQ, or a forward one (an outpost, a command vehicle).
            if (!_world.Bases.TryGetDropZone(team, out var zone)) return CommandResult.Rejected(CommandError.NoRallyPoint);
            // A ranked card costs less to call (the army's value, upkeep and refunds keep its full price).
            var price = economy.PriceOf(defId, def.CpCost);
            if (economy.Cp < price) return CommandResult.Rejected(CommandError.NotEnoughCp);
            if (VehicleCount(team) >= economy.VehicleCap) return CommandResult.Rejected(CommandError.ArmyAtCapacity);
            if (def.MaxPerSide > 0 && Fielded(team, defId) >= def.MaxPerSide) return CommandResult.Rejected(CommandError.UnitLimit);
            // Prompt 17 C: a loyal wingman is outside the aircraft cap (its own limit of four holds).
            if (def.Flying && !def.AirCapFree && AircraftCount(team) >= AircraftCap(team)) return CommandResult.Rejected(CommandError.AirAtCapacity);

            // Charged exactly once, when accepted (T03).
            economy.Cp -= price;
            if (def.Flying) _world.CountAircraft(team);
            // Veteran crews: a delivery turns up as the refurbished elite version while the side's
            // elite budget has room (prompt 8 H), for the elite's dearer price. Decided now, with the
            // landing point, so the drop the game draws is the vehicle that lands.
            defId = Promote(team, economy, def);
            // Deliveries fan out around the zone so consecutive ones do not stack.
            var index = _deliveries++;
            if (Routed(team, def, index, out var due, out var routed))
            {
                _pending.Add((team, defId, due, routed));
                economy.ArmyCp = ArmyCp(team);
                economy.VehicleCount = VehicleCount(team);
                _world.Emit(SimEvent.DeploymentRouted(team, defId, routed, Inward(zone), (float)(due - _world.Time)));
                return CommandResult.Ok;
            }
            var angle = index * 2.39996f;
            var landing = zone + new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (2f + (index % 5) * 1.5f);
            // Prompt 22 F: Rush's drops come down faster.
            // Prompt 29 S04: the card's own drop time (by its base price class, data), then the commander's change.
            var delivery = def.DropDelay * (economy.Commander?.Delivery ?? 1f);
            _pending.Add((team, defId, _world.Time + delivery, landing));
            economy.ArmyCp = ArmyCp(team);
            economy.VehicleCount = VehicleCount(team);
            _world.Emit(SimEvent.DeploymentQueued(team, defId, landing, Inward(zone), delivery));
            return CommandResult.Ok;
        }

        /// <summary>How many of a vehicle a side has in the field or on its way.</summary>
        internal int Fielded(int team, string defId)
        {
            var n = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Ally && v.Def.Id == defId) n++;
            foreach (var p in _pending)
                if (p.Item1 == team && p.Item2 == defId && !_allyLandings.Contains(p.Item4)) n++;
            return n;
        }

        /// <summary>
        /// A delivery nobody pays for (a mission enemy's reinforcements): it comes the way a bought
        /// vehicle does, dropped by parachute near <paramref name="near"/> (aircraft fly in over the
        /// edge), and needs no economy for the side.
        /// </summary>
        public void Airlift(int team, string defId, Vector2 near, bool ally = false)
        {
            if (!_world.Catalog.Vehicles.TryGetValue(defId, out var def)) return;
            var index = _deliveries++;
            if (!ally && Routed(team, def, index, out var due, out var routed))
            {
                _pending.Add((team, defId, due, routed));
                _world.Emit(SimEvent.DeploymentRouted(team, defId, routed, Inward(near), (float)(due - _world.Time)));
                return;
            }
            var angle = index * 2.39996f;
            var landing = _world.ClampToMap(near + new Vector2(MathF.Sin(angle), MathF.Cos(angle)) * (3f + (index % 5) * 2f));
            _pending.Add((team, defId, _world.Time + def.DropDelay, landing));
            if (ally) _allyLandings.Add(landing);
            _world.Emit(SimEvent.DeploymentQueued(team, defId, landing, Inward(near), def.DropDelay));
        }

        /// <summary>Spends CP for a strike; the caller has already validated everything else.</summary>
        public bool TrySpend(int team, int cost) => TrySpend(team, (float)cost);

        /// <summary>Spends a fractional price (a commander's cut on a support).</summary>
        public bool TrySpend(int team, float cost)
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
            StepUnderdog();
            StepRelays();
            foreach (var economy in _teams.Values)
            {
                // Prompt 13 H.12: a mode with the once-a-match help for the side behind gives its income
                // boost only to the side that got it; the others keep the old sliding boost.
                var target = Underdog != null ? (UnderdogTeam == economy.Team ? Underdog.Income : 1f)
                    : _world.CatchUp && TryGetRival(economy.Team, out var rival) ? CatchUpFor(economy.ArmyCp, rival.ArmyCp, _world.CatchUpMax) : 1f;
                economy.CatchUp += (target - economy.CatchUp) * MathF.Min(1f, dt / CatchUpSettle);
                economy.CommanderIncome = CommanderIncome(economy);
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + economy.Earning * dt);
            }

            for (var i = _pending.Count - 1; i >= 0; i--)
            {
                var (team, defId, due, landing) = _pending[i];
                if (due > _world.Time) continue;
                _pending.RemoveAt(i);
                var delivered = Deliver(team, defId, landing);
                // The ally's reinforcements belong to the ally's commander.
                if (delivered != null && _allyLandings.Remove(landing)) delivered.Ally = true;
            }
        }

        /// <summary>
        /// Pays the side that dealt the last damage (recently), even if the shooter died with its
        /// shell still in the air, and for strike kills.
        /// </summary>
        public void OnVehicleDestroyed(Vehicle victim, Vehicle? killer = null)
        {
            // Quartermaster's four-piece: part of its own cost comes back when it falls.
            if (victim.Gear != null && victim.Gear.Has(TraitId.SetSalvageRights) && _teams.TryGetValue(victim.Team, out var own) && own.Commander?.LossRefund != false)
                own.Cp = MathF.Min(own.Bank, own.Cp + victim.Def.ArmyCost * MathF.Min(LossRefundCap, victim.Gear.Trait(TraitId.SetSalvageRights).B));
            var team = victim.LastAttackerTeam;
            var paid = 0f;
            // Prompt 32 L4: a garrison squad pays nobody.
            if (team >= 0 && team != victim.Team && victim.Def.Fort == null && !victim.Garrison && _world.Time - victim.LastHitTime <= 10.0 && _teams.TryGetValue(team, out var economy))
            {
                paid = KillShare(Bounty(economy, victim), KillerBonus(killer, team), economy.Commander?.KillRefund ?? KillReward);
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + victim.Def.ArmyCost * paid);
            }
            else team = -1;
            PayLoot(victim, team, paid);
        }

        /// <summary>
        /// The tower-branch rework (DECISIONS 19T): an enemy vehicle destroyed within a loot depot's reach pays the depot's
        /// side its share of the victim's price (the nearest depot only), the kill's own refund and this together never
        /// past <see cref="KillRefundCap"/>.
        /// </summary>
        private void PayLoot(Vehicle victim, int paidTeam, float paid)
        {
            if (victim.Def.Static || victim.Def.ArmyCost <= 0) return;
            Vehicle? depot = null;
            var best = float.MaxValue;
            foreach (var v in _world.VehicleList)
            {
                if (v.Def.Loot is not { } loot || !v.IsAlive || v.Team == victim.Team || v.Team < 0 || v.Stunned) continue;
                var d2 = System.Numerics.Vector2.DistanceSquared(v.Position, victim.Position);
                if (d2 > loot.Radius * loot.Radius || d2 >= best) continue;
                depot = v;
                best = d2;
            }
            if (depot == null || !_teams.TryGetValue(depot.Team, out var own)) return;
            var room = KillRefundCap - (paidTeam == depot.Team ? paid : 0f);
            var share = MathF.Min(depot.Def.Loot!.Share, MathF.Max(0f, room));
            if (share <= 0f) return;
            own.Cp = MathF.Min(own.Bank, own.Cp + victim.Def.ArmyCost * share);
            LootPaid?.Invoke(depot, victim, victim.Def.ArmyCost * share);
        }

        /// <summary>Tests and the HUD: a loot depot paid its side (the depot, the victim, the CP).</summary>
        internal Action<Vehicle, Vehicle, float>? LootPaid;

        /// <summary>The most a kill may refund, as a share of the victim's price, whatever pays it (prompt 8 I.6).</summary>
        internal const float KillRefundCap = 0.45f;

        /// <summary>The most one's own loss may refund (Quartermaster's four pieces), as a share of its price.</summary>
        internal const float LossRefundCap = 0.15f;

        /// <summary>A kill's refund as a share of the victim's price: the base quarter, the odds, the killer's equipment, capped.</summary>
        internal static float KillShare(float bounty, float killerBonus, float reward = KillReward) => MathF.Min(KillRefundCap, reward * bounty * killerBonus);

        /// <summary>
        /// Prompt 22 F: the commander's income multiplier now: its flat rate (Ledger's), a battle without capture points
        /// (Flag's), a full purse and the opening seconds (Vault's).
        /// </summary>
        internal float CommanderIncome(TeamEconomy economy)
        {
            if (economy.Commander is not { } c) return 1f;
            var f = c.Income;
            if (c.NoPointsIncome != 1f && !_world.PointsInPlay) f *= c.NoPointsIncome;
            if (c.RichIncome != 1f && economy.Cp >= c.RichAt) f *= c.RichIncome;
            if (c.EarlyIncome != 1f && _world.Time < c.EarlySeconds) f *= c.EarlyIncome;
            return f;
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
        public static float CatchUpFor(int own, int rival, float max = MaxCatchUp)
        {
            if (rival < CatchUpMinimumArmy) return 1f;
            var odds = own / (float)rival;
            return 1f + max * Math.Clamp((CatchUpBelow - odds) / (CatchUpBelow - 0.2f), 0f, 1f);
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

        private readonly List<Vector2> _allyLandings = new();

        private Vehicle? Deliver(int team, string defId, Vector2 landing)
        {
            if (!_world.TryGetRally(team, out var zone)) return null;
            var inward = Inward(zone);
            var at = landing;
            // Aircraft fly in over the map's edge behind the zone instead of appearing on it.
            if (_world.Catalog.Vehicle(defId).Flying) at = EdgeBehind(zone, inward);
            var vehicle = _world.SpawnVehicle(defId, team, at, SimMath.HeadingOf(inward));
            _single.Clear();
            _single.Add(vehicle.Id);
            _world.Submit(new Command(CommandType.Move, team, _single, _world.ClampToMap(landing + inward * RollIn)));
            return vehicle;
        }

        /// <summary>The map's edge straight behind a zone (looking in from it), just inside the square.</summary>
        private Vector2 EdgeBehind(Vector2 zone, Vector2 inward)
        {
            var map = _world.Map;
            var p = zone;
            for (var step = 0; step < 40 && map.EdgeDistance(p - inward * 4f) >= 2f; step++)
                p -= inward * 4f;
            return p;
        }

        private int ArmyCp(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                // Prompt 23 C.4: a mission event's reinforcements are outside the army (they have a cap of their own).
                // Prompt 32 L4: a Garrison HQ's squads count against the cap, never in the army supply reads.
                if (v.IsAlive && v.Team == team && !v.Ally && !v.Reinforcement && !v.Garrison) total += v.Def.ArmyCost;
            foreach (var (pendingTeam, defId, _, landing) in _pending)
                if (pendingTeam == team && !_allyLandings.Contains(landing)) total += _world.Catalog.Vehicle(defId).CpCost;
            return total;
        }

        /// <summary>
        /// The most aircraft a side may have up (and on the way): <see cref="TeamEconomy.MaxAircraft"/>, and
        /// one more for each landing pad of its that took the hangar branch (prompt 13 F.1).
        /// </summary>
        public int AircraftCap(int team)
        {
            var cap = TeamEconomy.MaxAircraft + _world.CommanderAirCap(team);
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Def.Utility is { AirCap: > 0 } u) cap += u.AirCap;
            return cap;
        }

        /// <summary>Aircraft a side has up, plus those on the way.</summary>
        public int AircraftCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Flying && !v.Def.Boss && !v.Scripted && !v.Def.AirCapFree) total++;
            foreach (var (pendingTeam, id, _, _) in _pending)
                if (pendingTeam == team && _world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Flying && !def.AirCapFree) total++;
            return total;
        }

        internal int VehicleCount(int team)
        {
            var total = 0;
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Scripted && !v.Ally && !v.Reinforcement) total++;
            foreach (var (pendingTeam, _, _, landing) in _pending)
                if (pendingTeam == team && !_allyLandings.Contains(landing)) total++;
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

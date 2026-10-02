#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Numerics;
using System.Text;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>What a Sandbox control does to the running battle (prompt 21 C, D).</summary>
    public enum SandboxOpKind
    {
        /// <summary>The units drive to <see cref="SandboxOp.Point"/>.</summary>
        Move,

        /// <summary>The units hold where they are (no AI moves them) until released.</summary>
        Hold,

        Release,

        /// <summary>The units hold their fire (<see cref="SandboxOp.Value"/> 1) or fire again (0).</summary>
        HoldFire,

        /// <summary>The units fire at <see cref="SandboxOp.Target"/>.</summary>
        FireAt,

        /// <summary>The units cannot be hurt (1) or can again (0).</summary>
        Immortal,

        /// <summary>A whole side cannot be hurt (1) or can again (0): <see cref="SandboxOp.Team"/>.</summary>
        SideImmortal,

        /// <summary>A side's CP unlimited (<see cref="SandboxOp.Value"/> &lt; 0) or set to Value.</summary>
        SideCp,

        /// <summary>A side's fire-support cooldowns on (1) or off (0).</summary>
        Cooldowns,

        /// <summary>A side's fire support <see cref="SandboxOp.Text"/> called on <see cref="SandboxOp.Point"/>.</summary>
        Strike,

        /// <summary>Boss tools (D): phase <see cref="SandboxOp.Value"/> (0-based).</summary>
        BossPhase,

        /// <summary>The big attack now.</summary>
        BossBig,

        /// <summary>The big attack off (1) or on (0).</summary>
        BossBigOff,

        /// <summary>Part <see cref="SandboxOp.Value"/> broken.</summary>
        BossBreak,

        /// <summary>Part <see cref="SandboxOp.Value"/> whole again.</summary>
        BossRestore,

        /// <summary>The altitude tier: 1 low, 2 high.</summary>
        BossTier,

        /// <summary>Escorts on (1) or off (0).</summary>
        BossEscorts,

        /// <summary>Swapped for its main or mini version.</summary>
        BossSwap,

        /// <summary>The bosses' difficulty key <see cref="SandboxOp.Text"/> (escorts, big attacks).</summary>
        Difficulty,
    }

    /// <summary>One Sandbox control, as the journal keeps it: units by entity id (the same ids in every replay of the scenario).</summary>
    public sealed class SandboxOp
    {
        public SandboxOpKind Kind;
        public int[] Units = Array.Empty<int>();
        public int Team;
        public Vector2 Point;
        public int Target;
        public int Value;
        public string Text = "";

        public static SandboxOp For(SandboxOpKind kind, IEnumerable<int> units, int value = 0) => new() { Kind = kind, Units = new List<int>(units).ToArray(), Value = value };

        public static SandboxOp Boss(SandboxOpKind kind, int boss, int value = 0) => new() { Kind = kind, Units = new[] { boss }, Value = value };

        public static SandboxOp Side(SandboxOpKind kind, int team, int value = 0) => new() { Kind = kind, Team = team, Value = value };
    }

    /// <summary>
    /// A Sandbox battle (prompt 21 C): the scenario's units placed as it says (heading, rank, equipment, elite,
    /// health, ammunition, a boss's phase, parts, escorts and tier), both sides' bases, economies and AI, and the
    /// controls fed in through a journal. Every control goes through <see cref="Queue"/> and takes effect at the
    /// start of the next step, stamped with that step: replaying the scenario with the same seed and journal
    /// (<see cref="Replay"/>) gives the same battle, step for step (C.7).
    /// </summary>
    public sealed class SandboxBattle : IGameMode
    {
        /// <summary>A side with nothing left for this long has lost (a bought unit on its way has time to land).</summary>
        public const double WipeGrace = 2.0;

        private readonly List<(long tick, SandboxOp op)> _journal = new();
        private readonly List<SandboxOp> _pending = new();
        private readonly List<(long tick, SandboxOp op)> _script = new();
        private int _scriptAt;
        private readonly HashSet<int> _held = new();
        private readonly HashSet<int> _immortal = new();
        private readonly bool[] _sideImmortal = new bool[2];
        private readonly bool[] _unlimited = new bool[2];
        private readonly bool[] _cooldowns = { true, true };
        private readonly bool[] _had = new bool[2];
        private readonly double[] _wipedSince = { -1, -1 };
        private readonly ConquestAi?[] _commanders = new ConquestAi?[2];
        private readonly TacticalAi?[] _fighters = new TacticalAi?[2];
        private readonly List<(int id, int phase)> _phaseTargets = new();
        private readonly List<(int id, AltitudeTier tier)> _tierTargets = new();
        private readonly List<int> _spawned = new();
        private readonly HashSet<int> _fixed = new();

        public SandboxBattle(SandboxScenario scenario, Func<SandboxUnit, VehicleDef, VehicleBoost?>? boost = null)
        {
            Scenario = scenario.Clone();
            Boost = boost;
        }

        /// <summary>The scenario as it started (a copy: editing the original does not change a running battle).</summary>
        public SandboxScenario Scenario { get; private set; }

        /// <summary>A unit's rank and equipment as a boost (the game's gear rules); null: every unit as the data has it.</summary>
        public Func<SandboxUnit, VehicleDef, VehicleBoost?>? Boost { get; }

        /// <summary>A side's saved base plan (the player's, B.7); null: the AI's base for its level stands in.</summary>
        public Func<int, BaseLoadout?>? PlayerBase { get; set; }

        /// <summary>Set by the internal build: the full AI writes its buying scores (E.6).</summary>
        public bool TraceBuying { get; set; }

        public MatchResult? Result { get; private set; }

        /// <summary>When the result came (seconds of battle).</summary>
        public double EndedAt { get; private set; } = -1;

        public SandboxStats Stats { get; } = new();

        public StuckWatch? Stuck { get; private set; }

        /// <summary>The entity id of each scenario unit, in scenario order.</summary>
        public IReadOnlyList<int> Spawned => _spawned;

        public IReadOnlyList<(long tick, SandboxOp op)> Journal => _journal;

        public ConquestAi? Commander(int team) => team is 0 or 1 ? _commanders[team] : null;

        public bool Held(int id) => _held.Contains(id);

        public bool IsImmortal(int id) => _immortal.Contains(id);

        public bool SideImmortal(int team) => team is 0 or 1 && _sideImmortal[team];

        public bool Unlimited(int team) => team is 0 or 1 && _unlimited[team];

        public bool CooldownsOn(int team) => team is not (0 or 1) || _cooldowns[team];

        // ================================================================== set-up

        public void Setup(SimWorld world)
        {
            var s = Scenario;
            var catalog = world.Catalog;
            world.ModeTag = "Sandbox";
            world.FogOfWar = s.Fog;
            world.EscortSettings = EscortSettings.For(catalog.EscortRules, s.Difficulty);
            world.BigAttackSettings = BigAttackSettings.For(catalog.BigAttackRules, s.Difficulty);
            for (var team = 0; team < 2; team++)
            {
                var side = s.Sides[team];
                var deck = side.Deck.Count > 0 ? new List<string>(side.Deck) : FieldDeck(catalog, s, team);
                deck.RemoveAll(id => !catalog.Vehicles.ContainsKey(id));
                var supports = new List<string>(side.Supports);
                supports.RemoveAll(id => !catalog.TryGetSupport(id, out _));
                _unlimited[team] = side.Cp < 0f;
                var start = _unlimited[team] ? UnlimitedCp : side.Cp;
                var economy = new TeamEconomy(team, start, income: _unlimited[team] ? 0f : side.Income, bank: _unlimited[team] ? UnlimitedCp : MathF.Max(30f, side.Cp),
                    vehicles: deck, supports: supports) { VehicleCap = SandboxRules.VehicleCap };
                world.EnableEconomy(economy);
                _cooldowns[team] = side.Cooldowns;
                _sideImmortal[team] = side.Immortal;
                // Prompt 22 F.1: each side's commander, before anything of it is placed.
                world.SetCommander(team, Commanders.Get(side.Commander));
            }
            // Bases (B.7): a side's HQ and towers where the map has a camp for it.
            var bases = new BaseSetup();
            var any = false;
            for (var team = 0; team < 2; team++)
            {
                var side = s.Sides[team];
                if (side.Base == SandboxBase.None || world.Map.BaseOf(team) == null) continue;
                var loadout = side.Base == SandboxBase.Player ? PlayerBase?.Invoke(team) : null;
                loadout ??= BaseLoadout.ForAi(catalog, side.BaseLevel, "default", s.Seed + 5 * team);
                bases.Set(team, loadout, BaseRole.Anchor);
                any = true;
            }
            if (any) BaseDefences.Build(world, bases, 0, 1);
            foreach (var v in world.Vehicles) _fixed.Add(v.Id.Value);

            foreach (var u in s.Units) _spawned.Add(Place(world, u)?.Id.Value ?? 0);

            for (var team = 0; team < 2; team++)
            {
                var seed = s.Seed + 11 * (team + 1);
                switch (s.Sides[team].Ai)
                {
                    case SandboxAi.Full:
                        _commanders[team] = new ConquestAi(null, team, 1 - team, AiDifficulty.Hard, seed)
                        {
                            AutoDeploy = true, AutoStrike = true, BuyScores = TraceBuying ? new Dictionary<string, float>() : null,
                            Tactic = string.IsNullOrEmpty(s.Sides[team].Tactic) ? null : s.Sides[team].Tactic,
                        };
                        break;
                    case SandboxAi.Combat:
                        _fighters[team] = new TacticalAi(team, 1 - team, seed);
                        break;
                }
            }
            Stuck = new StuckWatch(world.Map.Id, "Sandbox", s.Seed);
            Stats.Attach(world);
            ApplyGuards(world);
        }

        /// <summary>
        /// While the battle is being set up (it does not step): the scenario's units taken off the field and placed
        /// again from <paramref name="scenario"/> (the editor's change mirrored). The ids taken off are returned for
        /// the views. A set-up battle is never run: running it rebuilds the whole battle from the scenario.
        /// </summary>
        public List<int> Rebuild(SimWorld world, SandboxScenario scenario)
        {
            // Everything but the bases goes: the units and whatever they brought with them (a boss's guards).
            var removed = new List<int>();
            foreach (var v in new List<Vehicle>(world.Vehicles))
            {
                if (_fixed.Contains(v.Id.Value)) continue;
                world.RemoveQuietly(v);
                removed.Add(v.Id.Value);
            }
            _spawned.Clear();
            _immortal.Clear();
            _phaseTargets.Clear();
            _tierTargets.Clear();
            Scenario = scenario.Clone();
            world.FogOfWar = Scenario.Fog;
            foreach (var u in Scenario.Units) _spawned.Add(Place(world, u)?.Id.Value ?? 0);
            world.ClearEvents();
            return removed;
        }

        /// <summary>CP that never runs out (topped up every step).</summary>
        public const float UnlimitedCp = 999f;

        /// <summary>The full AI's deck when the scenario names none: the kinds of the side's placed units it could buy.</summary>
        private static List<string> FieldDeck(Catalog catalog, SandboxScenario s, int team)
        {
            var list = new List<string>();
            foreach (var u in s.Units)
                if (u.Team == team && catalog.Vehicles.TryGetValue(u.Def, out var def) && def.Card && def.CpCost > 0 && !def.Boss && !def.Static &&
                    !list.Contains(def.CardId))
                    list.Add(def.CardId);
            return list;
        }

        private Vehicle? Place(SimWorld world, SandboxUnit u)
        {
            var catalog = world.Catalog;
            var id = u.Elite && catalog.EliteVariant(u.Def) is { } elite ? elite : u.Def;
            if (!catalog.Vehicles.TryGetValue(id, out var def)) return null;
            var v = world.SpawnBoosted(id, u.Team, u.Position, SimMath.DegToRad(u.Heading), Boost?.Invoke(u, def));
            v.Hp = MathF.Max(1f, v.MaxHp * Math.Clamp(u.Hp, 1, 100) / 100f);
            if (u.Ammo < 100) SetAmmo(v, u.Ammo);
            if (u.Immortal) _immortal.Add(v.Id.Value);
            if (u.Boss is { } boss && def.Boss)
            {
                if (boss.BigOff) world.Bosses.SetBigOff(v, true);
                foreach (var part in boss.Broken)
                    if (part >= 0 && part < v.PartCount && !v.IsPartBroken(part)) world.Bosses.Break(v, part);
                if (boss.NoEscorts) world.Bosses.SetEscorts(v, false);
                if (boss.Phase > 0) _phaseTargets.Add((v.Id.Value, boss.Phase));
            }
            var tier = TierOf(u.Tier);
            if (tier != AltitudeTier.None && def.Tiers != null)
            {
                world.Bosses.JumpPhase(v, 0);
                _tierTargets.Add((v.Id.Value, tier));
            }
            return v;
        }

        public static AltitudeTier TierOf(string? name) => name switch { "low" => AltitudeTier.Low, "high" => AltitudeTier.High, _ => AltitudeTier.None };

        /// <summary>Every finite magazine to <paramref name="percent"/> of full (B.6).</summary>
        internal static void SetAmmo(Vehicle v, int percent)
        {
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var full = v.Weapons[i].Load > 0 ? v.Weapons[i].Load : v.Arms[i].Ammo > 0 ? v.Arms[i].Ammo : -1;
                if (full <= 0) continue;
                v.Weapons[i].Ammo = (int)MathF.Round(full * Math.Clamp(percent, 0, 100) / 100f);
            }
        }

        // ================================================================== the controls and the journal

        /// <summary>A control from the screen: it takes effect at the start of the next step and is written in the journal.</summary>
        public void Queue(SandboxOp op) => _pending.Add(op);

        /// <summary>Controls written earlier (a replay, a test): each is fed in at the step it was given at.</summary>
        public void Replay(IEnumerable<(long tick, SandboxOp op)> journal)
        {
            _script.AddRange(journal);
            _script.Sort((a, b) => a.tick.CompareTo(b.tick));
        }

        public void Tick(SimWorld world, float dt)
        {
            while (_scriptAt < _script.Count && _script[_scriptAt].tick <= world.Tick) Apply(world, _script[_scriptAt++].op);
            foreach (var op in _pending) Apply(world, op);
            _pending.Clear();
            Stuck?.Observe(world);
            Stats.Step(world);
            ApplyGuards(world);
            foreach (var c in _commanders) c?.Tick(world, dt);
            foreach (var f in _fighters) f?.Tick(world, dt);
            ReleaseHeld(world);
            Judge(world);
        }

        /// <summary>The result-free part of a step: what the switches keep true (CP, cooldowns, immortality, pending phases and tiers).</summary>
        private void ApplyGuards(SimWorld world)
        {
            for (var team = 0; team < 2; team++)
            {
                if (!world.TryGetEconomy(team, out var e)) continue;
                if (_unlimited[team]) e.Cp = UnlimitedCp;
                if (!_cooldowns[team]) e.ReadyAt.Clear();
            }
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive) continue;
                var guard = _immortal.Contains(v.Id.Value) || (v.Team is 0 or 1 && _sideImmortal[v.Team]);
                if (guard) v.Invulnerable = true;
                else if (_guarded.Contains(v.Id.Value)) v.Invulnerable = false;
                if (guard) _guarded.Add(v.Id.Value);
                else _guarded.Remove(v.Id.Value);
            }
            for (var i = _phaseTargets.Count - 1; i >= 0; i--)
            {
                var (id, phase) = _phaseTargets[i];
                if (!world.TryGetVehicle(new EntityId(id), out var v) || !v.IsAlive) _phaseTargets.RemoveAt(i);
                else if (v.Def.Tiers != null ? v.TierPhase >= phase : v.Phase >= phase) _phaseTargets.RemoveAt(i);
                else if (!v.Transforming) world.Bosses.JumpPhase(v, phase);
            }
            for (var i = _tierTargets.Count - 1; i >= 0; i--)
            {
                var (id, tier) = _tierTargets[i];
                if (!world.TryGetVehicle(new EntityId(id), out var v) || !v.IsAlive) _tierTargets.RemoveAt(i);
                else if (v.LeftOrbit && world.Bosses.ForceTier(v, tier)) _tierTargets.RemoveAt(i);
            }
        }

        private readonly HashSet<int> _guarded = new();

        /// <summary>Held units drop whatever an AI told them this step (they still turn and shoot).</summary>
        private void ReleaseHeld(SimWorld world)
        {
            foreach (var id in _held)
                if (world.TryGetVehicle(new EntityId(id), out var v) && v.IsAlive && v.Order.Kind != OrderKind.Idle && v.Order.Kind != OrderKind.Attack)
                {
                    v.SetOrder(Order.Idle);
                    v.ClearPath();
                }
        }

        private void Apply(SimWorld world, SandboxOp op)
        {
            _journal.Add((world.Tick, op));
            switch (op.Kind)
            {
                case SandboxOpKind.Move:
                    Issue(world, op, CommandType.Move);
                    foreach (var id in op.Units) _held.Remove(id);
                    break;
                case SandboxOpKind.FireAt:
                    Issue(world, op, CommandType.Attack);
                    break;
                case SandboxOpKind.Hold:
                    Issue(world, op, CommandType.Stop);
                    foreach (var id in op.Units) _held.Add(id);
                    break;
                case SandboxOpKind.Release:
                    foreach (var id in op.Units)
                    {
                        _held.Remove(id);
                        if (world.TryGetVehicle(new EntityId(id), out var v)) v.ManualOrder = false;
                    }
                    break;
                case SandboxOpKind.HoldFire:
                    foreach (var v in Units(world, op)) world.HoldFire(v, op.Value != 0);
                    break;
                case SandboxOpKind.Immortal:
                    foreach (var id in op.Units)
                        if (op.Value != 0) _immortal.Add(id);
                        else _immortal.Remove(id);
                    break;
                case SandboxOpKind.SideImmortal:
                    if (op.Team is 0 or 1) _sideImmortal[op.Team] = op.Value != 0;
                    break;
                case SandboxOpKind.SideCp:
                    if (op.Team is 0 or 1 && world.TryGetEconomy(op.Team, out var e))
                    {
                        _unlimited[op.Team] = op.Value < 0;
                        e.Cp = op.Value < 0 ? UnlimitedCp : Math.Min(op.Value, (int)e.Bank);
                    }
                    break;
                case SandboxOpKind.Cooldowns:
                    if (op.Team is 0 or 1) _cooldowns[op.Team] = op.Value != 0;
                    break;
                case SandboxOpKind.Strike:
                    world.Submit(Command.Strike(op.Team, op.Text, op.Point));
                    break;
                case SandboxOpKind.Difficulty:
                    world.EscortSettings = EscortSettings.For(world.Catalog.EscortRules, op.Text);
                    world.BigAttackSettings = BigAttackSettings.For(world.Catalog.BigAttackRules, op.Text);
                    break;
                default:
                    foreach (var v in Units(world, op)) BossTool(world, v, op);
                    break;
            }
        }

        /// <summary>The last boss a swap made (the screen's selection follows it).</summary>
        public int LastSwapped { get; private set; }

        private void BossTool(SimWorld world, Vehicle v, SandboxOp op)
        {
            if (!v.Def.Boss) return;
            var bosses = world.Bosses;
            switch (op.Kind)
            {
                case SandboxOpKind.BossPhase:
                    _phaseTargets.RemoveAll(t => t.id == v.Id.Value);
                    _phaseTargets.Add((v.Id.Value, op.Value));
                    // A step now, the rest as each transformation ends (see ApplyGuards).
                    bosses.JumpPhase(v, op.Value);
                    break;
                case SandboxOpKind.BossBig:
                    bosses.TriggerBig(v);
                    break;
                case SandboxOpKind.BossBigOff:
                    bosses.SetBigOff(v, op.Value != 0);
                    break;
                case SandboxOpKind.BossBreak:
                    if (op.Value >= 0 && op.Value < v.PartCount && !v.IsPartBroken(op.Value)) bosses.Break(v, op.Value);
                    break;
                case SandboxOpKind.BossRestore:
                    bosses.Restore(v, op.Value);
                    break;
                case SandboxOpKind.BossTier:
                    var tier = op.Value == 1 ? AltitudeTier.Low : AltitudeTier.High;
                    if (!bosses.ForceTier(v, tier))
                    {
                        // Still in its opening orbit: out of it on the next step, then to the tier.
                        bosses.JumpPhase(v, 0);
                        _tierTargets.RemoveAll(t => t.id == v.Id.Value);
                        _tierTargets.Add((v.Id.Value, tier));
                    }
                    break;
                case SandboxOpKind.BossEscorts:
                    bosses.SetEscorts(v, op.Value != 0);
                    break;
                case SandboxOpKind.BossSwap:
                    if (bosses.SwapRank(v) is { } swapped)
                    {
                        LastSwapped = swapped.Id.Value;
                        if (_immortal.Remove(v.Id.Value)) _immortal.Add(swapped.Id.Value);
                    }
                    break;
            }
        }

        private IEnumerable<Vehicle> Units(SimWorld world, SandboxOp op)
        {
            foreach (var id in op.Units)
                if (world.TryGetVehicle(new EntityId(id), out var v) && v.IsAlive) yield return v;
        }

        private void Issue(SimWorld world, SandboxOp op, CommandType type)
        {
            // Units of either side take orders in the Sandbox: one command a side.
            for (var team = 0; team < 2; team++)
            {
                var ids = new List<EntityId>();
                foreach (var v in Units(world, op))
                    if (v.Team == team) ids.Add(v.Id);
                if (ids.Count == 0) continue;
                world.Submit(new Command(type, team, ids, op.Point, new EntityId(op.Target), manual: true));
            }
        }

        // ================================================================== the result

        private void Judge(SimWorld world)
        {
            if (Result != null) return;
            var now = world.Time;
            var alive = new int[2];
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team is 0 or 1) alive[v.Team]++;
            for (var team = 0; team < 2; team++)
            {
                if (alive[team] > 0) _had[team] = true;
                _wipedSince[team] = alive[team] == 0 && _had[team] ? (_wipedSince[team] < 0 ? now : _wipedSince[team]) : -1;
            }
            var wiped0 = _wipedSince[0] >= 0 && now - _wipedSince[0] >= WipeGrace;
            var wiped1 = _wipedSince[1] >= 0 && now - _wipedSince[1] >= WipeGrace;
            int? winner = wiped0 && wiped1 ? -1 : wiped0 ? 1 : wiped1 ? 0 : null;
            if (winner == null && Scenario.Limit > 0f && now >= Scenario.Limit)
            {
                var share0 = HealthShare(world, 0);
                var share1 = HealthShare(world, 1);
                winner = MathF.Abs(share0 - share1) < 1e-4f ? -1 : share0 > share1 ? 0 : 1;
            }
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            EndedAt = now;
            Stats.Step(world);
            Stats.Frozen = true;
        }

        /// <summary>A side's health left as a share of its units' full health (placed units and whatever joined).</summary>
        public static float HealthShare(SimWorld world, int team)
        {
            var (hp, max) = (0f, 0f);
            foreach (var v in world.VehicleList)
            {
                if (v.Team != team) continue;
                max += v.MaxHp;
                if (v.IsAlive) hp += v.Hp;
            }
            return max > 0f ? hp / max : 0f;
        }

        // ================================================================== replays (F.6)

        /// <summary>The scenario and its journal as one text: attach it to a bug report to play the battle again.</summary>
        public string ReplayJson() => ReplayJson(Scenario, _journal);

        public static string ReplayJson(SandboxScenario scenario, IReadOnlyList<(long tick, SandboxOp op)> journal)
        {
            var inv = CultureInfo.InvariantCulture;
            var b = new StringBuilder("{\"replay\":1,\"scenario\":").Append(scenario.ToJson()).Append(",\"ops\":[");
            for (var i = 0; i < journal.Count; i++)
            {
                var (tick, op) = journal[i];
                if (i > 0) b.Append(',');
                b.Append("{\"t\":").Append(tick.ToString(inv)).Append(",\"k\":\"").Append(op.Kind).Append("\",\"u\":[");
                for (var k = 0; k < op.Units.Length; k++) b.Append(k > 0 ? "," : "").Append(op.Units[k].ToString(inv));
                b.Append("],\"team\":").Append(op.Team.ToString(inv)).Append(",\"x\":").Append(op.Point.X.ToString("R", inv)).Append(",\"y\":")
                    .Append(op.Point.Y.ToString("R", inv)).Append(",\"target\":").Append(op.Target.ToString(inv)).Append(",\"v\":").Append(op.Value.ToString(inv))
                    .Append(",\"s\":\"").Append(op.Text.Replace("\\", "\\\\").Replace("\"", "\\\"")).Append("\"}");
            }
            return b.Append("]}").ToString();
        }

        /// <summary>Reads <see cref="ReplayJson()"/> back: the scenario and its journal.</summary>
        public static (SandboxScenario scenario, List<(long tick, SandboxOp op)> journal) ReadReplay(string json)
        {
            var o = new JsonObject(MiniJson.Parse(json), "replay");
            var scenario = SandboxScenario.FromObject(o.Raw.TryGetValue("scenario", out var inner) ? inner : null);
            var journal = new List<(long, SandboxOp)>();
            foreach (var e in o.Array("ops"))
            {
                var op = new SandboxOp
                {
                    Kind = e.Enum<SandboxOpKind>("k"), Team = e.Int("team", 0), Point = new Vector2(e.Float("x", 0f), e.Float("y", 0f)),
                    Target = e.Int("target", 0), Value = e.Int("v", 0), Text = e.Raw.TryGetValue("s", out var text) && text is string str ? str : "",
                };
                var units = new List<int>();
                if (e.IsArray("u"))
                    foreach (var f in e.FloatArray("u")) units.Add((int)f);
                op.Units = units.ToArray();
                journal.Add((e.Int("t", 0), op));
            }
            return (scenario, journal);
        }
    }
}

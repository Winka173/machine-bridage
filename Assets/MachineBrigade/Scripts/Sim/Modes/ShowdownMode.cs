#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Prompt 32 L7: Showdown's numbers (balance.json "matchRules.modes.showdown", schema of prompt 30).</summary>
    public sealed class ShowdownRules
    {
        /// <summary>12 minutes; then the HQ health lead decides, or sudden death.</summary>
        public float TimeLimit { get; set; } = 720f;

        /// <summary>Until a side's outer defence is breached, its HQ takes this share from artillery, missiles and aircraft fired from beyond <see cref="AntiSnipeRange"/>.</summary>
        public float AntiSnipeShare { get; set; } = 0.25f;

        public float AntiSnipeRange { get; set; } = 60f;

        /// <summary>Minute 6: income x <see cref="EscalationIncome"/> for both sides; the CP relays stop paying.</summary>
        public float EscalationAt { get; set; } = 360f;

        public float EscalationIncome { get; set; } = 1.5f;

        /// <summary>Minute 10: no tower is flown back in (a paid drop still lands).</summary>
        public float RebuildCutoff { get; set; } = 600f;

        /// <summary>At the limit, a lead of this share of the HQ's health (5 points) wins at once.</summary>
        public float OvertimeLead { get; set; } = 0.05f;

        /// <summary>Sudden death: seconds, and its income (x the base income).</summary>
        public float SuddenDeath { get; set; } = 90f;

        public float SuddenDeathIncome { get; set; } = 2f;

        /// <summary>Catch-up: income only, up to +25 %; no free reinforcement.</summary>
        public float CatchUpMax { get; set; } = 0.25f;

        /// <summary>How far round an HQ an enemy ground vehicle counts as inside the base (a line-less base's outer defence).</summary>
        public float BaseRadius { get; set; } = 46f;

        public SideSetup Player { get; set; } = new() { StartCp = 18f, Income = 1.35f };
        public SideSetup Enemy { get; set; } = new() { StartCp = 18f, Income = 1.35f };

        /// <summary>Each side's full base (towers, walls, HQ type); both HQs can fall.</summary>
        public BaseSetup? Bases { get; set; }

        public string? RulesId { get; set; } = "showdown";

        public void Apply(SimWorld world)
        {
            if (RulesId == null || world.Catalog.MatchRules.For(RulesId) is not { } r) return;
            TimeLimit = r.Get("timeLimit", TimeLimit);
            AntiSnipeShare = r.Get("antiSnipeShare", AntiSnipeShare);
            AntiSnipeRange = r.Get("antiSnipeRange", AntiSnipeRange);
            EscalationAt = r.Get("escalationAt", EscalationAt);
            EscalationIncome = r.Get("escalationIncome", EscalationIncome);
            RebuildCutoff = r.Get("rebuildCutoff", RebuildCutoff);
            OvertimeLead = r.Get("overtimeLead", OvertimeLead);
            SuddenDeath = r.Get("suddenDeath", SuddenDeath);
            SuddenDeathIncome = r.Get("suddenDeathIncome", SuddenDeathIncome);
            CatchUpMax = r.Get("catchUpMax", CatchUpMax);
            BaseRadius = r.Get("baseRadius", BaseRadius);
        }
    }

    /// <summary>Where a Showdown match stands.</summary>
    public enum ShowdownPhase
    {
        Regulation,
        SuddenDeath,
        Over,
    }

    /// <summary>
    /// Prompt 32 L7 (DECISIONS "Prompt 32 L3 / L7 / L9"): Showdown (Đối công). Two full bases on a symmetric 300 x 300
    /// battlefield; destroying the enemy HQ wins, losing one's own loses. Anti-snipe: until a side's outer defence is breached
    /// (an enemy ground vehicle into its base past the gate, or a rubble segment of its outer line that opens a route, by
    /// the NavGrid), its HQ takes a quarter from artillery, missiles and aircraft fired from beyond 60 m. Minute 6: income
    /// x1.5 both sides, the CP relays stop; minute 10: no tower flown back in. At 12 minutes a lead of 5 HQ health points or
    /// more wins; under 5, 90 s of sudden death (no anti-snipe, no rebuilding, income x2, the HQ skills' cooldowns kept): an
    /// HQ destroyed wins, else the side that did more damage to the enemy HQ in those 90 s; level, a draw. Catch-up is income
    /// only (+25 % at most), no free reinforcement. The AI reads the two HQs as its objectives (defend its own when
    /// threatened, attack the other's through the walls by the gate or breach rule).
    /// </summary>
    public sealed class ShowdownMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly ShowdownRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly EntityId[] _hq = new EntityId[2];
        private readonly bool[] _breached = new bool[2];
        private readonly float[] _sdDamage = new float[2];
        private double _nextLook;
        private bool _escalated;
        private double _suddenUntil = double.NaN;

        public ShowdownMode(ShowdownRules? rules = null) => _rules = rules ?? new ShowdownRules();

        public MatchResult? Result { get; private set; }

        public ShowdownPhase Phase { get; private set; } = ShowdownPhase.Regulation;

        /// <summary>The AI's objectives: each side's HQ as a point it holds (never captured: the HQ has to fall).</summary>
        public IReadOnlyList<ObjectiveState> Points => _points;

        public ShowdownRules Rules => _rules;

        /// <summary>Whether a side's outer defence is breached (its HQ takes full damage from afar from then on).</summary>
        public bool Breached(int team) => team is 0 or 1 && _breached[team];

        /// <summary>The damage a side did to the enemy HQ in sudden death.</summary>
        public float SuddenDeathDamage(int team) => team is 0 or 1 ? _sdDamage[team] : 0f;

        public float SecondsLeft(SimWorld world) => Phase == ShowdownPhase.SuddenDeath
            ? MathF.Max(0f, (float)(_suddenUntil - world.Time))
            : MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        /// <summary>A side's HQ health share (0 once it has fallen).</summary>
        public float HqShare(SimWorld world, int team) =>
            team is 0 or 1 && world.TryGetVehicle(_hq[team], out var hq) && hq.IsAlive ? hq.Hp / MathF.Max(1f, hq.MaxHp) : 0f;

        public void Setup(SimWorld world)
        {
            _rules.Apply(world);
            world.CatchUp = true;
            world.CatchUpIncomeOnly = true;
            world.CatchUpMax = _rules.CatchUpMax;
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(_rules.Enemy.Build(EnemyTeam));
            foreach (var unit in world.MapUnits) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            var bases = _rules.Bases ?? new BaseSetup().Set(PlayerTeam, BaseLoadout.HqOnly(), BaseRole.Target).Set(EnemyTeam, BaseLoadout.HqOnly(), BaseRole.Target);
            BaseDefences.Build(world, bases, PlayerTeam, EnemyTeam);
            world.Bases.RebuildUntil = _rules.RebuildCutoff;
            for (var team = 0; team <= 1; team++)
            {
                var b = world.Bases.Of(team);
                _hq[team] = b?.Hq ?? EntityId.None;
                var at = b?.HqPosition ?? (world.TryGetRally(team, out var r) ? r : Vector2.Zero);
                _points.Add(new ObjectiveState(new CapturePointDef("hq" + team, "hq", at, 18f)) { Owner = team, Progress = team == PlayerTeam ? 1f : -1f });
            }
            world.HqDamageRule = HqDamage;
        }

        /// <summary>The anti-snipe and the sudden-death count, on what an HQ takes (DamageSystem, after every other rule).</summary>
        internal float HqDamage(Vehicle hq, HitInfo hit, float damage)
        {
            var team = hq.Id == _hq[0] ? 0 : hq.Id == _hq[1] ? 1 : -1;
            if (team < 0 || Phase == ShowdownPhase.Over) return damage;
            if (Phase == ShowdownPhase.Regulation && !_breached[team] && FromAfar(hq, hit)) damage *= _rules.AntiSnipeShare;
            if (Phase == ShowdownPhase.SuddenDeath && hit.Team is 0 or 1 && hit.Team != team) _sdDamage[hit.Team] += MathF.Min(damage, hq.Hp);
            return damage;
        }

        /// <summary>Artillery (an indirect weapon, a called strike), a missile or rocket, or an aircraft, fired from beyond the range.</summary>
        private bool FromAfar(Vehicle hq, in HitInfo hit)
        {
            var weapon = hit.Weapon;
            var kind = hit.Attacker is { Flying: true } || hit.Kind == HitKind.Strike || hit.Indirect ||
                       (weapon != null && (weapon.Indirect || weapon.Projectile is ProjectileKind.Missile or ProjectileKind.Rocket or ProjectileKind.Drone));
            if (!kind) return false;
            // A called strike has no shooter: it comes from afar by definition.
            if (hit.Attacker == null) return true;
            return Vector2.Distance(hit.Attacker.Position, hq.Position) > _rules.AntiSnipeRange;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            var now = world.Time;
            // An HQ down ends it (both on the same step: a draw).
            var down0 = HqDown(world, PlayerTeam);
            var down1 = HqDown(world, EnemyTeam);
            if (down0 || down1)
            {
                End(world, down0 && down1 ? -1 : down0 ? EnemyTeam : PlayerTeam);
                return;
            }
            if (now >= _nextLook)
            {
                _nextLook = now + 0.5;
                for (var team = 0; team <= 1; team++)
                    if (!_breached[team] && (world.Walls.RubbleRoute(team) || EnemyInside(world, team))) _breached[team] = true;
            }
            if (!_escalated && now >= _rules.EscalationAt)
            {
                _escalated = true;
                Income(world, _rules.EscalationIncome);
                world.RelaysOff = true;
            }
            if (Phase == ShowdownPhase.Regulation && now >= _rules.TimeLimit)
            {
                var lead = HqShare(world, PlayerTeam) - HqShare(world, EnemyTeam);
                if (MathF.Abs(lead) >= _rules.OvertimeLead - 1e-5f)
                {
                    End(world, lead > 0f ? PlayerTeam : EnemyTeam);
                    return;
                }
                Phase = ShowdownPhase.SuddenDeath;
                _suddenUntil = now + _rules.SuddenDeath;
                Income(world, _rules.SuddenDeathIncome / (_escalated ? _rules.EscalationIncome : 1f));
                return;
            }
            if (Phase == ShowdownPhase.SuddenDeath && now >= _suddenUntil)
            {
                var a = _sdDamage[PlayerTeam];
                var b = _sdDamage[EnemyTeam];
                End(world, MathF.Abs(a - b) < 0.5f ? -1 : a > b ? PlayerTeam : EnemyTeam);
            }
        }

        private void End(SimWorld world, int winner)
        {
            Phase = ShowdownPhase.Over;
            Result = new MatchResult(winner);
            world.IsOver = true;
        }

        private bool HqDown(SimWorld world, int team) =>
            _hq[team].IsValid && (!world.TryGetVehicle(_hq[team], out var hq) || !hq.IsAlive);

        private static void Income(SimWorld world, float factor)
        {
            for (var team = 0; team <= 1; team++)
                if (world.Economy.TryGet(team, out var e)) e.ScaleIncome(factor);
        }

        /// <summary>
        /// An enemy ground vehicle inside the side's base: behind its outer wall line when it has one (through the gate:
        /// the camp's gate is an opening, never a gate entity to destroy), else within the base radius of its HQ.
        /// </summary>
        private bool EnemyInside(SimWorld world, int team)
        {
            WallLine? outer = null;
            foreach (var l in world.Walls.LinesOf(team))
                if (outer == null || l.Def.Radius > outer.Def.Radius) outer = l;
            var hq = world.Bases.Of(team)?.HqPosition ?? Vector2.Zero;
            var r2 = _rules.BaseRadius * _rules.BaseRadius;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team == team || v.Team < 0 || v.Team > 1 || v.Flying || v.Def.Static) continue;
                if (outer != null ? outer.Inside(v.Position) : Vector2.DistanceSquared(v.Position, hq) <= r2) return true;
            }
            return false;
        }
    }
}

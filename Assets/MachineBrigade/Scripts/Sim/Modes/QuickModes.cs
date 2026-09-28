#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    public sealed class DeathmatchRules
    {
        /// <summary>Vehicles to destroy to win outright.</summary>
        public int KillTarget { get; set; } = 100;

        /// <summary>Seconds; when time runs out the side with more kills wins.</summary>
        public float TimeLimit { get; set; } = 12 * 60f;

        public SideSetup Player { get; set; } = new() { StartCp = 18f, Income = 1.35f };
        public SideSetup Enemy { get; set; } = new() { StartCp = 18f, Income = 1.35f };

        /// <summary>Each side's base loadout and role; null: a bare HQ each.</summary>
        public BaseSetup? Bases { get; set; }
    }

    /// <summary>
    /// Deathmatch (tử chiến): no objectives, just destruction. Command Points flow faster, and
    /// the first side to destroy the target number of enemy vehicles wins; at the time limit the
    /// side with more kills does.
    /// </summary>
    public sealed class DeathmatchMode : IGameMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly DeathmatchRules _rules;
        private readonly KillLedger _ledger = new();

        public DeathmatchMode(DeathmatchRules? rules = null) => _rules = rules ?? new DeathmatchRules();

        public MatchResult? Result { get; private set; }

        public int KillTarget => _rules.KillTarget;

        public int Kills(int team) => _ledger.Kills(team);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            world.CatchUp = true;
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(_rules.Enemy.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            BaseDefences.Build(world, _rules.Bases, PlayerTeam, EnemyTeam);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            var ours = Kills(PlayerTeam);
            var theirs = Kills(EnemyTeam);
            var winner = ours >= _rules.KillTarget ? PlayerTeam : theirs >= _rules.KillTarget ? EnemyTeam : (int?)null;
            if (winner == null && world.Time >= _rules.TimeLimit) winner = ours == theirs ? -1 : ours > theirs ? PlayerTeam : EnemyTeam;
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            world.IsOver = true;
        }
    }

    public sealed class KingOfTheHillRules
    {
        /// <summary>Score to win; the sole holder of the hill scores <see cref="ScorePerSecond"/>.</summary>
        public float ScoreTarget { get; set; } = 100f;

        public float ScorePerSecond { get; set; } = 0.75f;
        public float CaptureSeconds { get; set; } = 8f;

        /// <summary>Seconds; at the limit the higher score wins.</summary>
        public float TimeLimit { get; set; } = 15 * 60f;

        /// <summary>Id of the map objective that becomes the hill.</summary>
        public string Hill { get; set; } = "town";

        public SideSetup Player { get; set; } = new() { StartCp = 16f, Income = 1.2f };
        public SideSetup Enemy { get; set; } = new() { StartCp = 16f, Income = 1.2f };

        /// <summary>Each side's base loadout and role; null: a bare HQ each.</summary>
        public BaseSetup? Bases { get; set; }
    }

    /// <summary>
    /// King of the Hill (vua đồi): one objective in the middle of the map. Holding it alone builds
    /// score; the first side to the target wins. Everything converges on one spot, so it is the
    /// most explosive mode.
    /// </summary>
    public sealed class KingOfTheHillMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly KingOfTheHillRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly float[] _score = new float[2];

        public KingOfTheHillMode(KingOfTheHillRules? rules = null) => _rules = rules ?? new KingOfTheHillRules();

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        public float ScoreTarget => _rules.ScoreTarget;

        public int Score(int team) => (int)MathF.Floor(_score[team]);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            CapturePointDef? hill = null;
            foreach (var def in world.Map.Points)
                if (def.Id == _rules.Hill) hill = def;
            hill ??= world.Map.Points.Count > 0 ? world.Map.Points[0] : null;
            if (hill != null) _points.Add(new ObjectiveState(hill.Value));
            world.CatchUp = true;
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(_rules.Enemy.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            BaseDefences.Build(world, _rules.Bases, PlayerTeam, EnemyTeam);
            _outposts = new Outposts(world, _points, neutral: true);
        }

        private Outposts? _outposts;

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null || _points.Count == 0) return;
            var hill = _points[0];
            PointCapture.Tick(world, hill, dt, _rules.CaptureSeconds);
            _outposts?.Tick(world);
            if (hill.Owner is PlayerTeam or EnemyTeam && !hill.Contested) _score[hill.Owner] += _rules.ScorePerSecond * dt;
            // The holder also earns a little more, so a strong hold snowballs a bit.
            if (world.TryGetEconomy(PlayerTeam, out var e0)) e0.Bonus = hill.Owner == PlayerTeam ? 0.35f : 0f;
            if (world.TryGetEconomy(EnemyTeam, out var e1)) e1.Bonus = hill.Owner == EnemyTeam ? 0.35f : 0f;

            int? winner = _score[PlayerTeam] >= _rules.ScoreTarget ? PlayerTeam : _score[EnemyTeam] >= _rules.ScoreTarget ? EnemyTeam : null;
            if (winner == null && world.Time >= _rules.TimeLimit)
                winner = Score(PlayerTeam) == Score(EnemyTeam) ? -1 : Score(PlayerTeam) > Score(EnemyTeam) ? PlayerTeam : EnemyTeam;
            if (winner == null) return;
            Result = new MatchResult(winner.Value);
            world.IsOver = true;
        }
    }

    public sealed class AssaultRules
    {
        /// <summary>The attacker's time bank at the start, what each sector taken adds, and its cap.</summary>
        public float StartSeconds { get; set; } = 300f;

        public float SectorBonus { get; set; } = 240f;
        public float MaxBank { get; set; } = 480f;

        /// <summary>Extra time while the attacker is still fighting on a live point when the clock runs out.</summary>
        public float Overtime { get; set; } = 60f;

        public float CaptureSeconds { get; set; } = 12f;

        /// <summary>CP the attacker gets for each sector taken.</summary>
        public float SectorCp { get; set; } = 12f;

        /// <summary>Fixed defences dug in round each sector (bunkers, towers, guns, flak).</summary>
        public bool Defences { get; set; } = true;

        /// <summary>The attacker (the player) buys faster; the defender starts dug in with more CP.</summary>
        public SideSetup Attacker { get; set; } = new() { StartCp = 20f, Income = 1.45f };

        public SideSetup Defender { get; set; } = new() { StartCp = 26f, Income = 1.05f };

        /// <summary>The Defend mode: the enemy attacks and the player holds the sectors.</summary>
        public bool PlayerDefends { get; set; }

        /// <summary>
        /// Each side's base loadout and role. The attacker's camp is an Anchor; the defender's base
        /// is the target: destroying its HQ wins as well as taking the last sector. Null: bare HQs.
        /// </summary>
        public BaseSetup? Bases { get; set; }
    }

    /// <summary>
    /// Assault (công phá), as Battlefield's Breakthrough and Rush: the defender holds three
    /// sectors laid one behind the other along the way to its camp (A; B, two points side by
    /// side; C, well short of the camp). Only the front sector can be captured; once every point
    /// in it is the attacker's, the sector locks, its fixed defences blow up, the next one goes
    /// live, the attacker's drop zone moves up behind it, and the clock and the attacker's CP get
    /// a boost. The attacker wins by taking C; the defender by running the clock out (with
    /// overtime while a live point is still being fought over).
    /// </summary>
    public sealed class AssaultMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        /// <summary>The side taking the sectors and the side holding them (the player attacks unless the rules say it defends).</summary>
        public int Attacker => _rules.PlayerDefends ? EnemyTeam : PlayerTeam;

        public int Defender => _rules.PlayerDefends ? PlayerTeam : EnemyTeam;

        private readonly AssaultRules _rules;
        private readonly List<ObjectiveState> _points = new();
        private readonly List<List<ObjectiveState>> _sectors = new();
        private readonly List<List<EntityId>> _defences = new();
        private Outposts? _outposts;
        private double _deadline;
        private double _overtimeUntil = double.NegativeInfinity;
        private Vector2 _axis = Vector2.UnitX;

        public AssaultMode(AssaultRules? rules = null) => _rules = rules ?? new AssaultRules();

        public IReadOnlyList<ObjectiveState> Points => _points;

        public MatchResult? Result { get; private set; }

        /// <summary>The live sector, from 0; equal to <see cref="SectorCount"/> once all are taken.</summary>
        public int Sector { get; private set; }

        public int SectorCount => _sectors.Count;

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, (float)(_deadline - world.Time));

        public bool InOvertime(SimWorld world) => world.Time < _overtimeUntil && world.Time >= _deadline;

        public int Taken => PointCapture.Held(_points, Attacker);

        /// <summary>The points of one sector (0 = A).</summary>
        public IReadOnlyList<ObjectiveState> SectorPoints(int sector) => _sectors[sector];

        public void Setup(SimWorld world)
        {
            world.CatchUp = true;
            world.EnableEconomy(_rules.Attacker.Build(Attacker));
            world.EnableEconomy(_rules.Defender.Build(Defender));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            BuildSectors(world);
            _deadline = _rules.StartSeconds;
            if (_rules.Defences) Fortify(world);
            var bases = _rules.Bases ?? new BaseSetup().Set(Attacker, null, BaseRole.Anchor).Set(Defender, null, BaseRole.Target);
            BaseDefences.Build(world, bases, Attacker, Defender);
            _outposts = new Outposts(world, _points, built: true);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            if (Sector < _sectors.Count)
            {
                foreach (var point in _sectors[Sector]) PointCapture.Tick(world, point, dt, _rules.CaptureSeconds);
                var taken = true;
                foreach (var point in _sectors[Sector]) taken &= point.Owner == Attacker;
                if (taken) Advance(world);
            }
            _outposts?.Tick(world);
            if (world.TryGetEconomy(Attacker, out var e0)) e0.Bonus = 0.25f * Sector;

            // The defending HQ destroyed: the attack has won, whatever the sectors.
            if (Sector >= _sectors.Count || world.Bases.Of(Defender)?.HqFallen == true) Result = new MatchResult(Attacker);
            else if (world.Time >= _deadline)
            {
                // Overtime: the attack goes on while it is still pushing on a live point.
                var fighting = false;
                foreach (var point in _sectors[Sector])
                    fighting |= point.Contested || (point.Owner != Attacker && point.Progress * (Defender == Attacker ? 1f : -1f) < 0.999f && Pushing(world, point));
                if (fighting && _overtimeUntil < _deadline) _overtimeUntil = world.Time + _rules.Overtime;
                if (!fighting || world.Time >= _overtimeUntil) Result = new MatchResult(Defender);
            }
            if (Result != null) world.IsOver = true;
        }

        private bool Pushing(SimWorld world, ObjectiveState point)
        {
            var r = point.Def.Radius;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Attacker && !v.Flying && Vector2.DistanceSquared(v.Position, point.Def.Position) < r * r) return true;
            return false;
        }

        /// <summary>A sector fell: lock it, blow its defences, open the next, move the attacker up.</summary>
        private void Advance(SimWorld world)
        {
            var fallen = _sectors[Sector];
            foreach (var point in fallen) point.Locked = true;
            foreach (var id in _defences[Sector])
                if (world.TryGetVehicle(id, out var gun) && gun.IsAlive) world.Damage.Apply(gun, 1e7f, DamageType.HighExplosive);
            var centre = Centre(fallen);
            Sector++;
            var remaining = MathF.Max(0f, (float)(_deadline - world.Time));
            _deadline = world.Time + MathF.Min(_rules.MaxBank, remaining + _rules.SectorBonus);
            _overtimeUntil = double.NegativeInfinity;
            if (world.TryGetEconomy(Attacker, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + _rules.SectorCp);
            if (Sector < _sectors.Count)
            {
                foreach (var point in _sectors[Sector]) point.Locked = false;
                world.SetRally(Attacker, Open(world, centre - _axis * 14f, 10f));
            }
            var side = _rules.PlayerDefends ? "defend." : "assault.";
            var key = side + (Sector >= _sectors.Count ? "done" : Sector == 1 ? "sectorB" : "sectorC");
            world.Emit(SimEvent.Stage(Sector + 1, centre, key));
        }

        /// <summary>
        /// Three sectors along the line from the attacker's camp to the defender's: A a bit over
        /// a third of the way, B (two points either side of the line) past the middle, C at
        /// least 52 m short of the defender's camp. Each point sits on the most open ground near
        /// its spot.
        /// </summary>
        private void BuildSectors(SimWorld world)
        {
            world.TryGetRally(Attacker, out var from);
            world.TryGetRally(Defender, out var to);
            var length = Vector2.Distance(from, to);
            _axis = length > 1f ? (to - from) / length : Vector2.UnitX;
            var across = new Vector2(-_axis.Y, _axis.X);
            var cSpot = to - _axis * MathF.Max(52f, length * 0.26f);
            var layout = new[]
            {
                new[] { ("a", "sector_a", from + _axis * (length * 0.36f)) },
                new[] { ("b1", "sector_b", from + _axis * (length * 0.56f) + across * 24f), ("b2", "sector_b", from + _axis * (length * 0.56f) - across * 24f) },
                new[] { ("c", "sector_c", cSpot) },
            };
            for (var s = 0; s < layout.Length; s++)
            {
                var sector = new List<ObjectiveState>();
                foreach (var (id, name, spot) in layout[s])
                {
                    var point = new ObjectiveState(new CapturePointDef(id, name, Open(world, spot, 14f), s == 2 ? 13f : 12f));
                    PointCapture.Own(point, Defender);
                    point.Locked = s > 0;
                    sector.Add(point);
                    _points.Add(point);
                }
                _sectors.Add(sector);
                _defences.Add(new List<EntityId>());
            }
        }

        /// <summary>Each sector's fixed defences, dug in on the defender's side of its points, facing the attack.</summary>
        private void Fortify(SimWorld world)
        {
            var kinds = new[]
            {
                new[] { "mg_bunker", "guard_tower" },
                new[] { "gun_turret", "aa_turret" },
                new[] { "rocket_turret", "gun_turret", "aa_turret" },
            };
            var across = new Vector2(-_axis.Y, _axis.X);
            var heading = SimMath.HeadingOf(-_axis);
            for (var s = 0; s < _sectors.Count; s++)
            {
                var sector = _sectors[s];
                for (var i = 0; i < kinds[s].Length; i++)
                {
                    if (!world.Catalog.Vehicles.ContainsKey(kinds[s][i])) continue;
                    var point = sector[i % sector.Count];
                    var side = (i % 2 == 0 ? 1f : -1f) * (sector.Count > 1 ? 6f : 9f);
                    var spot = point.Def.Position + _axis * (point.Def.Radius + 4f) + across * side;
                    var gun = world.SpawnVehicle(kinds[s][i], Defender, Open(world, spot, 6f), heading);
                    world.AnchorDefence(gun);
                    _defences[s].Add(gun.Id);
                }
            }
        }

        /// <summary>The most open walkable spot within <paramref name="search"/> of <paramref name="spot"/>.</summary>
        private static Vector2 Open(SimWorld world, Vector2 spot, float search)
        {
            var best = spot;
            var bestScore = -1;
            for (var dx = -search; dx <= search; dx += 2f)
                for (var dy = -search; dy <= search; dy += 2f)
                {
                    var at = spot + new Vector2(dx, dy);
                    if (!world.Map.Contains(at) || !world.Grid.IsWalkable(at)) continue;
                    var open = 0;
                    for (var ox = -6f; ox <= 6f; ox += 3f)
                        for (var oy = -6f; oy <= 6f; oy += 3f)
                            if (world.Grid.IsWalkable(at + new Vector2(ox, oy))) open++;
                    // Prefer open ground, then staying near the spot.
                    var score = open * 100 - (int)(dx * dx + dy * dy);
                    if (score <= bestScore) continue;
                    bestScore = score;
                    best = at;
                }
            return best;
        }

        private static Vector2 Centre(List<ObjectiveState> points)
        {
            var sum = Vector2.Zero;
            foreach (var p in points) sum += p.Def.Position;
            return sum / Math.Max(1, points.Count);
        }
    }
}

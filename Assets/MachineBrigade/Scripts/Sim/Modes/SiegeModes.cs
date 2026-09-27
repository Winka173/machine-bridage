#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    public sealed class SiegeRules
    {
        /// <summary>Seconds to bring down the command HQ.</summary>
        public float TimeLimit { get; set; } = 15 * 60f;

        /// <summary>Prop that has to fall.</summary>
        public string Target { get; set; } = "command_hq";

        /// <summary>The HQ is this many times tougher than the building's catalogue health (a fortress core).</summary>
        public float Hardening { get; set; } = 4f;

        public SideSetup Attacker { get; set; } = new() { StartCp = 26f, Income = 1.5f, ArmyCap = 34 };
        public SideSetup Defender { get; set; } = new() { StartCp = 20f, Income = 1f };
    }

    /// <summary>
    /// Siege (công thành): the enemy holds a fortress of walls, gun turrets, AA, bunkers and guard
    /// towers around a command HQ. The player's army has to break in and level the HQ before the
    /// clock runs out; the defender sends out its own tanks from inside the walls.
    /// </summary>
    public sealed class SiegeMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly SiegeRules _rules;
        private readonly KillLedger _ledger = new();
        private readonly List<EntityId> _targets = new();
        private readonly List<EntityId> _defences = new();
        private double _wipedSince = -1;

        public SiegeMode(SiegeRules? rules = null) => _rules = rules ?? new SiegeRules();

        public MatchResult? Result { get; private set; }
        public IReadOnlyList<ObjectiveState> Points => Array.Empty<ObjectiveState>();

        public int Kills => _ledger.Kills(PlayerTeam);
        public int Losses => _ledger.Losses(PlayerTeam);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        /// <summary>The fortress centre (the HQ), for the defender to rally round.</summary>
        public Vector2? Fortress { get; private set; }

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Attacker.Build(PlayerTeam));
            world.EnableEconomy(_rules.Defender.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            foreach (var prop in world.Props)
                if (prop.IsAlive && prop.Def.Id == _rules.Target)
                {
                    _targets.Add(prop.Id);
                    if (_rules.Hardening > 1f) prop.Harden(_rules.Hardening);
                    Fortress ??= prop.Position;
                }
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == EnemyTeam && v.Def.Static) _defences.Add(v.Id);
            if (Fortress == null && world.TryGetRally(EnemyTeam, out var rally)) Fortress = rally;
        }

        /// <summary>Share of the HQ destroyed (0-1); without an HQ, of the fixed defences.</summary>
        public float Progress(SimWorld world)
        {
            if (_targets.Count > 0)
            {
                float hp = 0f, max = 0f;
                foreach (var id in _targets)
                    if (world.TryGetProp(id, out var p))
                    {
                        hp += MathF.Max(0f, p.Hp);
                        max += p.MaxHp;
                    }
                return max > 0f ? 1f - hp / max : 1f;
            }
            // Destroyed vehicles leave the world's list, so count against the ones there at the start.
            var standing = 0;
            foreach (var id in _defences)
                if (world.TryGetVehicle(id, out var v) && v.IsAlive) standing++;
            return _defences.Count > 0 ? 1f - standing / (float)_defences.Count : 0f;
        }

        /// <summary>What the attacking army should knock down now: the HQ.</summary>
        public EntityId Target(SimWorld world)
        {
            foreach (var id in _targets)
                if (world.TryGetProp(id, out var p) && p.IsAlive) return id;
            return EntityId.None;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            if (Progress(world) >= 0.999f)
            {
                Finish(world, PlayerTeam);
                return;
            }
            if (world.Time >= _rules.TimeLimit)
            {
                Finish(world, EnemyTeam);
                return;
            }
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            if (_wipedSince >= 0 && world.Time - _wipedSince > 12.0) Finish(world, EnemyTeam);
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }
    }

    public sealed class BossRushRules
    {
        /// <summary>The bosses, fought one after another.</summary>
        public IReadOnlyList<string> Bosses { get; set; } = new[] { "behemoth", "mega_gunship", "mobile_fortress", "drone_mothership" };

        /// <summary>Elite escorts that come with each boss, by boss.</summary>
        public IReadOnlyDictionary<string, string[]> Escorts { get; set; } = new Dictionary<string, string[]>
        {
            ["behemoth"] = new[] { "elite_mbt", "elite_mbt" },
            ["mega_gunship"] = new[] { "elite_attack_helicopter", "elite_attack_helicopter" },
            ["mobile_fortress"] = new[] { "elite_heavy_tank", "elite_aa", "elite_mlrs" },
            ["drone_mothership"] = new[] { "elite_aa", "elite_apc", "elite_tank_destroyer" },
        };

        /// <summary>Seconds between one boss falling and the next arriving.</summary>
        public float Breather { get; set; } = 20f;

        public float TimeLimit { get; set; } = 22 * 60f;

        /// <summary>CP handed out when a boss falls.</summary>
        public float Bounty { get; set; } = 15f;

        public SideSetup Player { get; set; } = new() { StartCp = 30f, Income = 1.5f, ArmyCap = 36 };
    }

    /// <summary>
    /// Boss Rush: the campaign's bosses one after another, each with an elite escort, on an open
    /// field. Every boss that falls pays a CP bounty and buys a short breather.
    /// </summary>
    public sealed class BossRushMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly BossRushRules _rules;
        private readonly KillLedger _ledger = new();
        private double _nextBossAt;
        private double _wipedSince = -1;

        public BossRushMode(BossRushRules? rules = null) => _rules = rules ?? new BossRushRules();

        public MatchResult? Result { get; private set; }
        public IReadOnlyList<ObjectiveState> Points => Array.Empty<ObjectiveState>();

        /// <summary>Bosses destroyed so far.</summary>
        public int Defeated { get; private set; }

        public int Total => _rules.Bosses.Count;

        /// <summary>The boss on the field (none during a breather).</summary>
        public EntityId Boss { get; private set; }

        public int Kills => _ledger.Kills(PlayerTeam);
        public int Losses => _ledger.Losses(PlayerTeam);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(new SideSetup { StartCp = 0f, Income = 0.01f }.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            _ledger.Ignore = v => v.Def.Boss;
            _nextBossAt = 10.0;
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            if (Boss.IsValid && (!world.TryGetVehicle(Boss, out var boss) || !boss.IsAlive))
            {
                Boss = EntityId.None;
                Defeated++;
                if (world.TryGetEconomy(PlayerTeam, out var ours)) ours.Cp = MathF.Min(ours.Bank, ours.Cp + _rules.Bounty);
                if (Defeated >= Total)
                {
                    Finish(world, PlayerTeam);
                    return;
                }
                _nextBossAt = world.Time + _rules.Breather;
            }
            if (!Boss.IsValid && world.Time >= _nextBossAt && Defeated < Total) Spawn(world);
            if (world.Time >= _rules.TimeLimit)
            {
                Finish(world, EnemyTeam);
                return;
            }
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            if (_wipedSince >= 0 && world.Time - _wipedSince > 12.0) Finish(world, EnemyTeam);
        }

        private void Spawn(SimWorld world)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            var id = _rules.Bosses[Defeated];
            var home = world.TryGetRally(PlayerTeam, out var h) ? h : Vector2.Zero;
            var heading = SimMath.HeadingOf(home - rally);
            Boss = world.SpawnVehicle(id, EnemyTeam, rally, heading).Id;
            if (!_rules.Escorts.TryGetValue(id, out var escorts)) return;
            for (var i = 0; i < escorts.Length; i++)
            {
                var angle = heading + (i - (escorts.Length - 1) * 0.5f) * 0.7f;
                world.SpawnVehicle(escorts[i], EnemyTeam, world.ClampToMap(rally + SimMath.Forward(angle) * 14f), heading);
            }
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }
    }
}

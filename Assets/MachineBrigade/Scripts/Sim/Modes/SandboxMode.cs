#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>
    /// Endless test battle: the map's starting forces, escalating enemy waves, and a
    /// reinforcement call for the player. It exists to tune combat and explosions before the
    /// real modes (Conquest first) arrive.
    /// </summary>
    public sealed class SandboxMode : IGameMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private const float FirstWaveDelay = 20f;
        private const float WaveInterval = 30f;
        private const int MaxEnemies = 14;
        public const float ReinforceCooldownSeconds = 12f;

        private static readonly string[] WaveRoster =
        {
            "light_tank", "scout_jeep", "armored_car", "apc", "rocket_technical", "main_battle_tank", "attack_helicopter", "tank_destroyer",
            "flame_tank", "scout_heli", "mortar_carrier", "artillery", "aa_vehicle", "mlrs", "gunship_heli", "heavy_tank", "attack_jet",
        };
        private static readonly string[] ReinforceRoster = { "main_battle_tank", "light_tank", "aa_vehicle", "artillery", "scout_jeep" };

        private float _waveTimer = FirstWaveDelay;
        private int _reinforcements;

        public int Wave { get; private set; }

        public float SecondsToNextWave => MathF.Max(0f, _waveTimer);

        public float ReinforceCooldown { get; private set; }

        public MatchResult? Result => null;

        public void Setup(SimWorld world)
        {
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
        }

        public void Tick(SimWorld world, float dt)
        {
            ReinforceCooldown = MathF.Max(0f, ReinforceCooldown - dt);
            _waveTimer -= dt;
            if (_waveTimer > 0f) return;
            _waveTimer = WaveInterval;
            if (world.CountAlive(EnemyTeam) < MaxEnemies) SpawnWave(world);
        }

        /// <summary>Calls two vehicles to the player's rally point. Returns false while on cooldown.</summary>
        public bool TryReinforce(SimWorld world)
        {
            if (ReinforceCooldown > 0f || world.IsOver || !world.TryGetRally(PlayerTeam, out var rally)) return false;
            for (var i = 0; i < 2; i++)
            {
                var def = ReinforceRoster[_reinforcements++ % ReinforceRoster.Length];
                world.SpawnVehicle(def, PlayerTeam, rally + Offset(i, 2, 7f), SimMath.DegToRad(45f));
            }
            ReinforceCooldown = ReinforceCooldownSeconds;
            return true;
        }

        private void SpawnWave(SimWorld world)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            Wave++;
            var count = Math.Min(2 + Wave, 6);
            for (var i = 0; i < count; i++)
            {
                var def = WaveRoster[(Wave + i) % WaveRoster.Length];
                world.SpawnVehicle(def, EnemyTeam, rally + Offset(i, count, 9f), SimMath.DegToRad(225f));
            }
        }

        private static Vector2 Offset(int index, int count, float radius)
        {
            var angle = index * SimMath.Tau / Math.Max(1, count);
            return new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * radius;
        }
    }
}

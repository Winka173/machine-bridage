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

        /// <summary>Enemies alive at once: 14, one and a half more each wave, up to 48 (prompt 13 H.9).</summary>
        private int MaxEnemies => Math.Min(48, 14 + Wave * 3 / 2);
        public const float ReinforceCooldownSeconds = 12f;

        private static readonly string[] WaveRoster =
        {
            "light_tank", "scout_jeep", "armored_car", "ifv", "rocket_technical", "main_battle_tank", "attack_helicopter", "tank_destroyer",
            "flame_tank", "scout_heli", "mortar_carrier", "artillery", "aa_vehicle", "mlrs", "gunship_heli", "heavy_tank", "attack_jet",
        };
        private static readonly string[] ReinforceRoster = { "main_battle_tank", "light_tank", "aa_vehicle", "artillery", "scout_jeep" };

        private float _waveTimer = FirstWaveDelay;
        private int _reinforcements;

        public int Wave { get; private set; }

        /// <summary>Scales wave size and pace (difficulty): 0.75 easy, 1 normal, 1.35 hard.</summary>
        public float Intensity { get; set; } = 1f;

        /// <summary>
        /// Prompt 13 H.9: the waves by the player's deck (its cards' rank and equipment: 1 for rank 1 with
        /// nothing; a deck 20 % tougher and harder-hitting 1.2).
        /// </summary>
        public float DeckScale { get; set; } = 1f;

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
            _waveTimer = WaveInterval / MathF.Max(0.5f, Intensity);
            // Prompt 13 H.9: the waves keep coming (heavier, more of them elite) while the field is full; only
            // the room left under the ceiling is filled. They stopped altogether before, and a deck that held
            // the line stood for ever.
            SpawnWave(world, MaxEnemies - world.CountAlive(EnemyTeam));
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

        private void SpawnWave(SimWorld world, int room)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            Wave++;
            // Prompt 13 H.9: waves that keep growing (they stopped at six before, and a deck outgrew them for
            // ever), by the difficulty and the deck, with no ceiling but the enemies alive at once; the heavier
            // cards come in as the waves go on, and from wave 8 more and more of them (all by wave 24) as their
            // elite versions, so a line that holds is worn down in the end.
            var count = Math.Min(room, Math.Max(1, (int)MathF.Round((3f + 0.9f * (Wave - 1)) * Intensity * DeckScale)));
            var reach = Math.Clamp(4 + Wave, 4, WaveRoster.Length);
            var elite = MathF.Min(1f, (Wave - 7) * 0.06f);
            for (var i = 0; i < count; i++)
            {
                var def = WaveRoster[(Wave * 3 + i) % reach];
                if (elite > 0f && (Wave + i) % 10 < elite * 10f && world.Catalog.EliteVariant(def) is { } better) def = better;
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

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
    public sealed class SandboxMode : IGameMode, IEndlessMode
    {
        // ------------------------------------------------------------------------------------------------ prompt 30 L5

        /// <summary>
        /// Survival's finite part (sheet "Luật trận", "Vô hạn"): 10 waves, a mini boss with wave 5 and a main boss with wave 10;
        /// won once wave 10 is spawned and every enemy is down. 0: the old waves without end (no win).
        /// </summary>
        public int FiniteWaves { get; set; } = EndlessRules.SurvivalWaves;

        /// <summary>The main bosses Survival draws from (land bosses), and their mini versions (the mini-boss mutator's).</summary>
        public static readonly string[] MainBosses = { "behemoth", "mobile_fortress", "mega_gunship", "drone_mothership" };

        private MatchResult? _result;
        private int _finiteWaves, _lastFiniteSize;

        public MatchResult? Result => _result;

        public bool CanContinue => FiniteWaves > 0 && !InEndless && _result is { WinningTeam: PlayerTeam };

        public bool InEndless { get; private set; }

        public int EndlessSteps => InEndless ? Math.Max(0, Wave - _finiteWaves) : 0;

        public void ContinueEndless(SimWorld world)
        {
            if (!CanContinue) return;
            _result = null;
            InEndless = true;
            _finiteWaves = Wave;
            _waveTimer = WaveInterval / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.ContinueEndlessIntensityFloor, Intensity);
        }

        /// <summary>Survival's own loss (sheet: the army wiped out, or the drop zone taken) is the session's; this is the win.</summary>
        private void CheckWin(SimWorld world)
        {
            if (FiniteWaves <= 0 || InEndless || _result != null || Wave < FiniteWaves || world.CountAlive(EnemyTeam) > 0) return;
            _result = new MatchResult(PlayerTeam);
            world.IsOver = true;
        }

        /// <summary>The boss a wave brings: a main boss every 10 waves, a mini boss every 5 (the main one's mini version).</summary>
        private void SpawnBoss(SimWorld world, Vector2 rally)
        {
            var kind = EndlessRules.BossOfWave(Wave);
            if (kind == 0) return;
            var main = MainBosses[(Wave / EndlessRules.MiniBossEvery) % MainBosses.Length];
            if (!world.Catalog.Vehicles.TryGetValue(main, out var def)) return;
            var id = kind == 2 ? main : def.MiniVariant;
            if (id == null || !world.Catalog.Vehicles.ContainsKey(id)) return;
            world.SpawnVehicle(id, EnemyTeam, rally, SimMath.DegToRad(225f));
        }

        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private static float FirstWaveDelay => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.FirstWaveDelay;
        private static float WaveInterval => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.WaveInterval;

        /// <summary>
        /// MB_FINAL F3 (owner's final bundle, VIEC_CHO_AGENT_FINAL section 3): Survival's ten waves come one a minute whatever the
        /// difficulty (the difficulty sizes the waves), so wave 10 is sent at 20 + 9 x 60 = 560 s and the run, its clearing
        /// included, takes about 10 minutes. The waves past the tenth (Continue, endless) keep the old cadence.
        /// </summary>
        private static float SurvivalWaveInterval => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SurvivalWaveInterval;

        /// <summary>Seconds to the next wave: a minute in Survival's ten, else the old interval by the intensity.</summary>
        private float NextWaveIn => FiniteWaves > 0 && !InEndless ? SurvivalWaveInterval : WaveInterval / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.NextWaveInIntensityFloor, Intensity);

        /// <summary>Enemies alive at once: 14, one and a half more each wave, up to 48 (prompt 13 H.9).</summary>
        private int MaxEnemies => Math.Min(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.MaxEnemiesWaveCap, global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.MaxEnemiesWaveAdd + Wave * global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.MaxEnemiesWaveScale / global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.MaxEnemiesWaveDivisor);
        public static float ReinforceCooldownSeconds => global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.ReinforceCooldownSeconds;

        private static readonly string[] WaveRoster =
        {
            "light_tank", "scout_jeep", "armored_car", "ifv", "rocket_technical", "main_battle_tank", "attack_helicopter", "tank_destroyer",
            "flame_tank", "scout_heli", "mortar_carrier", "artillery", "aa_vehicle", "mlrs", "heavy_tank", "attack_jet",
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


        public void Setup(SimWorld world)
        {
            // Mini bosses carry no superweapon in Survival (the mini-boss rule).
            world.MiniBossesNoBigAttacks = true;
            foreach (var unit in world.MapUnits) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (_result != null) return;
            CheckWin(world);
            ReinforceCooldown = MathF.Max(0f, ReinforceCooldown - dt);
            // The finite part's last wave sent: the rest is clearing the field.
            if (FiniteWaves > 0 && !InEndless && Wave >= FiniteWaves) return;
            _waveTimer -= dt;
            if (_waveTimer > 0f) return;
            _waveTimer = NextWaveIn;
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
                world.SpawnVehicle(def, PlayerTeam, rally + Offset(i, global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.TryReinforceCount, global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.TryReinforceRadius), SimMath.DegToRad(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.TryReinforceDegrees));
            }
            ReinforceCooldown = ReinforceCooldownSeconds;
            return true;
        }

        private void SpawnWave(SimWorld world, int room)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            Wave++;
            if (InEndless)
            {
                // Stats only: the enemy +4 % a wave, the player +2 % (to +30 %); never more than the finite part's last wave.
                var k = EndlessSteps;
                world.SetTeamStats(EnemyTeam, EndlessRules.EnemyScale(k), EndlessRules.EnemyScale(k));
                world.SetTeamStats(PlayerTeam, EndlessRules.PlayerScale(k), EndlessRules.PlayerScale(k));
            }
            if (FiniteWaves > 0) SpawnBoss(world, rally);
            // Prompt 13 H.9: waves that keep growing (they stopped at six before, and a deck outgrew them for
            // ever), by the difficulty and the deck, with no ceiling but the enemies alive at once; the heavier
            // cards come in as the waves go on, and from wave 8 more and more of them (all by wave 24) as their
            // elite versions, so a line that holds is worn down in the end.
            var count = Math.Min(room, Math.Max(1, (int)MathF.Round((global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveAdd + global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveScale * (Wave - 1)) * Intensity * DeckScale)));
            if (InEndless) count = Math.Min(count, _lastFiniteSize);
            else if (FiniteWaves > 0 && Wave == FiniteWaves) _lastFiniteSize = count;
            var reach = Math.Clamp(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveAdd2 + Wave, global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveMin, WaveRoster.Length);
            var elite = MathF.Min(1f, (Wave - global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveSub) * global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveScale2);
            for (var i = 0; i < count; i++)
            {
                var def = WaveRoster[(Wave * global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveScale3 + i) % reach];
                if (elite > 0f && (Wave + i) % global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveWaveMod < elite * global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveEliteScale && world.Catalog.EliteVariant(def) is { } better) def = better;
                world.SpawnVehicle(def, EnemyTeam, rally + Offset(i, count, global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveRadius), SimMath.DegToRad(global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxMode.SpawnWaveDegrees));
            }
        }

        private static Vector2 Offset(int index, int count, float radius)
        {
            var angle = index * SimMath.Tau / Math.Max(1, count);
            return new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * radius;
        }
    }
}

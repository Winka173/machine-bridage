using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>A finished battle as the result screen shows it.</summary>
    internal sealed class MatchOutcome
    {
        /// <summary>1 victory, 0 draw, -1 defeat.</summary>
        public int Result { get; set; }

        public string Subtitle { get; set; }
        public List<(string label, string value)> Rows { get; } = new();
        public MatchReward Reward { get; set; }
    }

    /// <summary>
    /// One game mode as the match runs it: the simulation mode, the commander AIs of both sides,
    /// what the HUD shows, and how the battle ends and pays out. <see cref="MatchRunner"/> stays
    /// the same for every mode.
    /// </summary>
    internal abstract class ModeSession
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        protected readonly List<ConquestAi> Commanders = new();
        protected TacticalAi Waves;

        public IGameMode Mode { get; protected set; }

        /// <summary>The player's own commander (the army fights on its own); null on the menu.</summary>
        public ConquestAi PlayerAi { get; protected set; }

        public virtual IObjectiveMode Objectives => Mode as IObjectiveMode;

        public virtual HudSpec Hud => new() { Mode = HudMode.Score };

        public abstract string Kicker { get; }
        public virtual string Title => Strings.Get("mission.title");
        public abstract string Subtitle { get; }
        public abstract string StartToast { get; }

        public AiDifficulty Difficulty { get; protected set; } = AiDifficulty.Normal;

        public void TickAi(SimWorld world, float dt)
        {
            foreach (var c in Commanders) c.Tick(world, dt);
            Waves?.Tick(world, dt);
        }

        /// <summary>Fills the top bar; called every frame.</summary>
        public abstract void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps);

        /// <summary>The ending, once the battle is over; null while it runs.</summary>
        public abstract MatchOutcome Outcome(SimWorld world, int kills, int losses);

        protected ConquestAi AddPlayerCommander(IObjectiveMode objectives, int seed)
        {
            PlayerAi = new ConquestAi(objectives, PlayerTeam, EnemyTeam, AiDifficulty.Hard, seed + 2)
            {
                AutoDeploy = MatchSettings.AutoDeploy,
                AutoStrike = MatchSettings.AutoStrike,
            };
            Commanders.Add(PlayerAi);
            return PlayerAi;
        }

        protected ConquestAi AddEnemyCommander(IObjectiveMode objectives, int seed, CommanderStance stance = CommanderStance.Attack)
        {
            var ai = new ConquestAi(objectives, EnemyTeam, PlayerTeam, Difficulty, seed) { Stance = stance };
            Commanders.Add(ai);
            return ai;
        }

        protected static void FillPoints(IObjectiveMode mode, List<PointInfo> scratch)
        {
            scratch.Clear();
            if (mode == null) return;
            foreach (var p in mode.Points) scratch.Add(new PointInfo(p.Def.Id, p.Owner, p.Progress, p.Contested));
        }

        protected static string Clock(double seconds)
        {
            var s = (int)System.Math.Max(0.0, seconds);
            return $"{s / 60}:{s % 60:00}";
        }

        /// <summary>The standard rows every quick battle shows.</summary>
        protected static void AddRows(MatchOutcome outcome, SimWorld world, int kills, int losses)
        {
            outcome.Rows.Add((Strings.Get("result.kills"), kills.ToString()));
            outcome.Rows.Add((Strings.Get("result.losses"), losses.ToString()));
            outcome.Rows.Add((Strings.Get("result.time"), Clock(world.Time)));
        }

        protected static int OutcomeOf(MatchResult result) => result.IsDraw ? 0 : result.WinningTeam == PlayerTeam ? 1 : -1;

        /// <summary>The enemy's cards in a quick battle: what the player has unlocked, everything on Hard.</summary>
        protected static (string[] vehicles, string[] supports) EnemyDeck(AiDifficulty difficulty, Catalog catalog)
        {
            var vehicles = new List<string>();
            foreach (var id in MatchSettings.AllVehicles)
                if (catalog.Vehicles.ContainsKey(id) && !Progression.IsPremium(id) &&
                    (difficulty == AiDifficulty.Hard || PlayerProfile.IsUnlocked(id))) vehicles.Add(id);
            var supports = new List<string>();
            foreach (var id in MatchSettings.AllSupports)
                if (catalog.TryGetSupport(id, out _) && !Progression.IsPremium(id) &&
                    (difficulty == AiDifficulty.Hard || PlayerProfile.IsUnlocked(id))) supports.Add(id);
            return (vehicles.ToArray(), supports.ToArray());
        }

        protected static SideSetup PlayerSide(float cp, float income) => new()
        {
            StartCp = cp, Income = income, Vehicles = MatchSettings.DeckVehicles.ToArray(), Supports = MatchSettings.DeckSupports.ToArray(),
        };

        protected static SideSetup EnemySide(float cp, float income, AiDifficulty difficulty, Catalog catalog)
        {
            var (vehicles, supports) = EnemyDeck(difficulty, catalog);
            return new SideSetup { StartCp = cp, Income = income, Vehicles = vehicles, Supports = supports };
        }

        /// <summary>The session for the chosen mode (or the menu's AI-versus-AI battle).</summary>
        public static ModeSession Create(GameModeKind kind, bool menu, SimWorld world, int seed)
        {
            ModeSession session = menu ? new MenuSession() : kind switch
            {
                GameModeKind.Survival => new SurvivalSession(),
                GameModeKind.Deathmatch => new DeathmatchSession(),
                GameModeKind.KingOfTheHill => new HillSession(),
                GameModeKind.Assault => new AssaultSession(),
                GameModeKind.Campaign => new MissionSession(Campaign.Get(MatchSettings.Mission) ?? Campaign.All[0]),
                _ => new ConquestSession(),
            };
            if (!menu && kind != GameModeKind.Campaign) session.Difficulty = MatchSettings.Difficulty;
            session.Build(world, seed);
            return session;
        }

        protected abstract void Build(SimWorld world, int seed);

        /// <summary>Which map file the mode plays on (objectives or the open sandbox version).</summary>
        public static string MapFile(GameModeKind kind, string mapId) =>
            mapId + (kind is GameModeKind.Survival ? "_sandbox" : "_conquest");
    }

    /// <summary>The main menu's backdrop: two AI commanders fight a Conquest battle with everything.</summary>
    internal sealed class MenuSession : ModeSession
    {
        public override HudSpec Hud => new() { Mode = HudMode.Menu };
        public override string Kicker => "";
        public override string Subtitle => "";
        public override string StartToast => "";

        protected override void Build(SimWorld world, int seed)
        {
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            Mode = mode;
            mode.Setup(world);
            AddEnemyCommander(mode, seed);
            Commanders.Add(new ConquestAi(mode, PlayerTeam, EnemyTeam, AiDifficulty.Normal, seed + 1));
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps) { }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses) => null;
    }

    internal sealed class ConquestSession : ModeSession
    {
        private ConquestMode _mode;

        public override string Kicker => Strings.Get("mission.conquest.kicker");
        public override string Subtitle => Strings.Get("mission.conquest.sub");
        public override string StartToast => Strings.Get("toast.conquestStart");

        protected override void Build(SimWorld world, int seed)
        {
            var (vehicles, supports) = EnemyDeck(Difficulty, world.Catalog);
            _mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.DeckVehicles.ToArray(), PlayerSupports = MatchSettings.DeckSupports.ToArray(),
                EnemyVehicles = vehicles, EnemySupports = supports,
            });
            Mode = _mode;
            _mode.Setup(world);
            AddEnemyCommander(_mode, seed);
            AddPlayerCommander(_mode, seed);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            hud.SetScore(_mode.Tickets(PlayerTeam), _mode.Tickets(EnemyTeam), _mode.MaxTickets, scratch);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("stat.tickets"), $"{_mode.Tickets(PlayerTeam)} : {_mode.Tickets(EnemyTeam)}"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    internal sealed class DeathmatchSession : ModeSession
    {
        private DeathmatchMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Score, ScoreLabel = "stat.kills" };
        public override string Kicker => Strings.Get("mode.deathmatch.kicker");
        public override string Subtitle => Strings.Format("mode.deathmatch.sub", _mode.KillTarget);
        public override string StartToast => Strings.Format("mode.deathmatch.toast", _mode.KillTarget);

        protected override void Build(SimWorld world, int seed)
        {
            _mode = new DeathmatchMode(new DeathmatchRules
            {
                Player = PlayerSide(18f, 1.35f), Enemy = EnemySide(18f, 1.35f, Difficulty, world.Catalog),
            });
            Mode = _mode;
            _mode.Setup(world);
            AddEnemyCommander(null, seed);
            AddPlayerCommander(null, seed);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            hud.SetScore(_mode.Kills(PlayerTeam), _mode.Kills(EnemyTeam), _mode.KillTarget, scratch);
            hud.SetTimer(_mode.SecondsLeft(world));
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    internal sealed class HillSession : ModeSession
    {
        private KingOfTheHillMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Score, ScoreLabel = "stat.score" };
        public override string Kicker => Strings.Get("mode.hill.kicker");
        public override string Subtitle => Strings.Get("mode.hill.sub");
        public override string StartToast => Strings.Get("mode.hill.toast");

        protected override void Build(SimWorld world, int seed)
        {
            _mode = new KingOfTheHillMode(new KingOfTheHillRules
            {
                Player = PlayerSide(16f, 1.2f), Enemy = EnemySide(16f, 1.2f, Difficulty, world.Catalog),
            });
            Mode = _mode;
            _mode.Setup(world);
            AddEnemyCommander(_mode, seed);
            AddPlayerCommander(_mode, seed);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            hud.SetScore(_mode.Score(PlayerTeam), _mode.Score(EnemyTeam), (int)_mode.ScoreTarget, scratch);
            hud.SetTimer(_mode.SecondsLeft(world));
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("stat.score"), $"{_mode.Score(PlayerTeam)} : {_mode.Score(EnemyTeam)}"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    internal sealed class AssaultSession : ModeSession
    {
        private AssaultMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Score, ScoreLabel = "stat.taken" };
        public override string Kicker => Strings.Get("mode.assault.kicker");
        public override string Subtitle => Strings.Get("mode.assault.sub");
        public override string StartToast => Strings.Get("mode.assault.toast");

        protected override void Build(SimWorld world, int seed)
        {
            _mode = new AssaultMode(new AssaultRules
            {
                Attacker = PlayerSide(20f, 1.45f), Defender = EnemySide(26f, 1.05f, Difficulty, world.Catalog),
            });
            Mode = _mode;
            _mode.Setup(world);
            AddEnemyCommander(_mode, seed, CommanderStance.Defend);
            AddPlayerCommander(_mode, seed);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            var count = _mode.Points.Count;
            hud.SetScore(_mode.Taken, count - _mode.Taken, count, scratch);
            hud.SetTimer(_mode.SecondsLeft(world));
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("stat.taken"), $"{_mode.Taken} / {_mode.Points.Count}"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    internal sealed class SurvivalSession : ModeSession
    {
        private SandboxMode _mode;
        private double _wipedSince = -1, _overrunSince = -1;
        private bool _over;

        public override HudSpec Hud => new() { Mode = HudMode.Waves, HintKey = "hint.autoSurvival" };
        public override string Kicker => Strings.Get("mission.survival.kicker");
        public override string Subtitle => Strings.Get("mission.sub");
        public override string StartToast => Strings.Get("toast.start");

        public SandboxMode Survival => _mode;

        protected override void Build(SimWorld world, int seed)
        {
            _mode = new SandboxMode
            {
                Intensity = Difficulty switch { AiDifficulty.Easy => 0.75f, AiDifficulty.Hard => 1.35f, _ => 1f },
            };
            Mode = _mode;
            _mode.Setup(world);
            world.EnableEconomy(new Sim.Economy.TeamEconomy(PlayerTeam, 16f, income: 0.8f,
                vehicles: MatchSettings.DeckVehicles.ToArray(), supports: MatchSettings.DeckSupports.ToArray()));
            Waves = new TacticalAi(EnemyTeam, PlayerTeam, seed);
            // The commander holds a line a third of the way towards the enemy.
            world.TryGetRally(PlayerTeam, out var home);
            world.TryGetRally(EnemyTeam, out var threat);
            AddPlayerCommander(null, seed).DefendPoint = Vector2.Lerp(home, threat, 0.33f);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps) =>
            hud.SetStats(world.CountAlive(PlayerTeam), world.CountAlive(EnemyTeam), _mode.Wave, _mode.SecondsToNextWave, fps);

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_over || world.Time <= 5.0 || !Lost(world)) return null;
            _over = true;
            world.IsOver = true;
            var outcome = new MatchOutcome { Result = -1, Subtitle = Strings.Get("result.over") };
            outcome.Rows.Add((Strings.Get("result.waves"), _mode.Wave.ToString()));
            outcome.Rows.Add((Strings.Get("result.kills"), kills.ToString()));
            outcome.Rows.Add((Strings.Get("result.time"), Clock(world.Time)));
            outcome.Reward = Rewards.Survival(Difficulty, _mode.Wave, kills);
            return outcome;
        }

        /// <summary>
        /// Survival ends when the army has been wiped out for a while (nothing alive or on the
        /// way), or the enemy has held the base unopposed. Command Points always trickle in, so
        /// "cannot afford anything right now" alone would make the ending a matter of luck.
        /// </summary>
        private bool Lost(SimWorld world)
        {
            var now = world.Time;
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0;
            _wipedSince = wiped ? (_wipedSince < 0 ? now : _wipedSince) : -1;
            world.TryGetRally(PlayerTeam, out var home);
            var attackers = 0;
            var defenders = 0;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Flying) continue;
                var distance = Vector2.Distance(v.Position, home);
                if (v.Team == EnemyTeam && distance < 18f) attackers++;
                else if (v.Team == PlayerTeam && distance < 26f) defenders++;
            }
            var overrun = attackers > 0 && defenders == 0;
            _overrunSince = overrun ? (_overrunSince < 0 ? now : _overrunSince) : -1;
            return (_wipedSince >= 0 && now - _wipedSince > 10.0) || (_overrunSince >= 0 && now - _overrunSince > 15.0);
        }
    }

    /// <summary>A campaign mission: its goal, the enemy it describes, and stars and unlocks at the end.</summary>
    internal sealed class MissionSession : ModeSession
    {
        private readonly MissionDef _def;
        private MissionMode _mode;

        public MissionSession(MissionDef def) => _def = def;

        public MissionDef Def => _def;
        public MissionMode Mission => _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Format("campaign.kicker", Campaign.IndexOf(_def.Id) + 1);
        public override string Title => Strings.Get("mission." + _def.Id + ".name");
        public override string Subtitle => Strings.Get("goal." + _def.Goal.ToString().ToLowerInvariant());
        public override string StartToast => Strings.Get("mission." + _def.Id + ".brief");

        protected override void Build(SimWorld world, int seed)
        {
            Difficulty = System.Enum.TryParse<AiDifficulty>(_def.Difficulty, out var d) ? d : AiDifficulty.Normal;
            var commander = _def.EnemyAi is "commander" or "both";
            SideSetup enemy = null;
            if (commander)
            {
                var deck = new List<string>();
                foreach (var id in _def.EnemyDeck)
                    if (world.Catalog.Vehicles.ContainsKey(id)) deck.Add(id);
                var supports = new List<string>();
                foreach (var id in MatchSettings.AllSupports)
                    if (world.Catalog.TryGetSupport(id, out _) && !Progression.IsPremium(id) && id != "cruise_missile") supports.Add(id);
                enemy = new SideSetup
                {
                    StartCp = _def.EnemyCp, Income = _def.EnemyIncome,
                    Vehicles = deck.Count > 0 ? deck.ToArray() : EnemyDeck(Difficulty, world.Catalog).vehicles, Supports = supports.ToArray(),
                };
            }
            var playerSide = PlayerSide(_def.PlayerCp, _def.PlayerIncome);
            playerSide.ArmyCap = _def.PlayerCap;
            _mode = new MissionMode(_def, playerSide, enemy);
            Mode = _mode;
            _mode.Setup(world);

            if (commander)
            {
                var stance = _def.EnemyStance == "Defend" ? CommanderStance.Defend : CommanderStance.Attack;
                AddEnemyCommander(_mode, seed, stance).Goal = w => _mode.EnemyGoal(w);
            }
            else if (_def.EnemyAi == "waves")
            {
                world.TryGetRally(PlayerTeam, out var home);
                Waves = new TacticalAi(EnemyTeam, PlayerTeam, seed) { Objective = w => _mode.EnemyGoal(w) ?? home };
            }
            var player = AddPlayerCommander(_mode, seed);
            player.Goal = w => _mode.PlayerGoal(w);
            player.Demolish = w => _mode.PlayerDemolish(w);
            // Holding a point: fight whatever comes at it, but never wander off and leave it open.
            if (_def.Goal == MissionGoal.Hold) player.Leash = 32f;
            if (_def.Goal == MissionGoal.Survive)
            {
                foreach (var p in world.Map.Points)
                    if (_def.Points.Count > 0 && p.Id == _def.Points[0]) player.DefendPoint = p.Position;
                if (player.DefendPoint == null && world.TryGetRally(PlayerTeam, out var home) && world.TryGetRally(EnemyTeam, out var threat))
                    player.DefendPoint = Vector2.Lerp(home, threat, 0.33f);
            }
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            var (done, needed) = _mode.Count(world);
            var detail = _def.Goal switch
            {
                MissionGoal.Hold or MissionGoal.Survive => $"{Clock(done)} / {Clock(needed)}",
                MissionGoal.Boss or MissionGoal.Intercept => $"{UnityEngine.Mathf.RoundToInt(_mode.Progress(world) * 100f)}%",
                _ => $"{done} / {needed}",
            };
            hud.SetMission(Strings.Get("goal." + _def.Goal.ToString().ToLowerInvariant()), detail, _mode.Progress(world),
                _mode.SecondsLeft(world), scratch);
            if (world.TryGetVehicle(_mode.Boss, out var boss) && boss.IsAlive)
                hud.SetBoss(Strings.Card(boss.Def.Id), boss.Hp / boss.MaxHp);
            else hud.SetBoss(null, 0f);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var won = result.WinningTeam == PlayerTeam;
            var outcome = new MatchOutcome { Result = won ? 1 : -1, Subtitle = Title };
            outcome.Rows.Add((Strings.Get("result.kills"), _mode.Kills.ToString()));
            outcome.Rows.Add((Strings.Get("result.losses"), _mode.Losses.ToString()));
            outcome.Rows.Add((Strings.Get("result.time"), Clock(world.Time)));
            outcome.Reward = Rewards.Mission(_def, won, (float)world.Time, _mode.Losses);
            return outcome;
        }
    }
}

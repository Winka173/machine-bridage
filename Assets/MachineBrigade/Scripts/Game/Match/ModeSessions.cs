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
            Events?.Tick(world, dt);
        }

        /// <summary>Supply drops and bomber raids (every mode but the scripted campaign).</summary>
        protected BattleEvents Events;

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

        /// <summary>
        /// Both sides' bases for a mode (balance.json "base.roles" for what they are for): the
        /// player's own loadout, and the enemy's drawn for its difficulty (a commander personality
        /// names its style later). Assault's defender is the target; everywhere else an Anchor.
        /// </summary>
        protected BaseSetup Bases(SimWorld world, GameModeKind kind, int seed, int attacker = PlayerTeam, bool menu = false)
        {
            var rules = world.Catalog.Base;
            var role = rules.RoleFor(kind.ToString());
            var setup = new BaseSetup();
            var enemyLoadout = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed);
            var playerLoadout = menu ? BaseLoadout.ForAi(world.Catalog, "Normal", "default", seed + 5) : PlayerProfile.BaseLoadout;
            if (role == BaseRole.Target)
            {
                // The side attacking holds its camp; the side attacked has the base to lose.
                var defender = 1 - attacker;
                setup.Set(attacker, attacker == PlayerTeam ? playerLoadout : enemyLoadout, BaseRole.Anchor);
                setup.Set(defender, defender == PlayerTeam ? playerLoadout : enemyLoadout, BaseRole.Target);
                return setup;
            }
            var each = role == BaseRole.None ? BaseRole.None : BaseRole.Anchor;
            return setup.Set(PlayerTeam, playerLoadout, each).Set(EnemyTeam, enemyLoadout, each);
        }

        /// <summary>The enemy commander's base style (balance.json "base.ai.styles"); commanders with personalities choose their own.</summary>
        protected string EnemyStyle { get; set; } = "default";

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
                GameModeKind.Defend => new DefendSession(endless: false),
                GameModeKind.Endless => new DefendSession(endless: true),
                GameModeKind.Weekly => new WeeklySession(),
                GameModeKind.Siege => new SiegeSession(),
                GameModeKind.BossRush => new BossRushSession(),
                GameModeKind.Campaign => new MissionSession(Campaign.Get(MatchSettings.Mission) ?? Campaign.All[0]),
                _ => new ConquestSession(),
            };
            if (!menu && kind != GameModeKind.Campaign) session.Difficulty = MatchSettings.Difficulty;
            session.Build(world, seed);
            // Supply drops everywhere; no bomber raids in Boss Rush (they hit the army massed round the boss).
            if (menu || kind != GameModeKind.Campaign) session.Events = new BattleEvents(seed, raids: kind != GameModeKind.BossRush);
            // Elite crews turn up more often the harder the enemy (and now and then in the menu battle).
            var elite = menu ? 0.15f : session.Difficulty switch { AiDifficulty.Hard => 0.25f, AiDifficulty.Normal => 0.1f, _ => 0f };
            if (world.TryGetEconomy(EnemyTeam, out var enemy)) enemy.EliteChance = elite;
            if (menu && world.TryGetEconomy(PlayerTeam, out var ours)) ours.EliteChance = elite;
            // Doctrines: the player's choice; a hard enemy picks one of its own.
            if (!menu && Progression.DoctrineOwned(MatchSettings.Doctrine))
                world.SetDoctrine(PlayerTeam, MachineBrigade.Sim.Content.Doctrine.Get(MatchSettings.Doctrine));
            if (session.Difficulty == AiDifficulty.Hard || menu)
            {
                var all = MachineBrigade.Sim.Content.Doctrine.All;
                world.SetDoctrine(EnemyTeam, all[new System.Random(seed).Next(all.Count)]);
            }
            return session;
        }

        protected abstract void Build(SimWorld world, int seed);

        /// <summary>Which map file the mode plays on (objectives or the open sandbox version).</summary>
        public static string MapFile(GameModeKind kind, string mapId) => kind switch
        {
            // Every battlefield has a fortified version; fall back to Conquest's if one is missing.
            GameModeKind.Siege or GameModeKind.Defend or GameModeKind.Endless =>
                UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + mapId + "_siege") != null ? mapId + "_siege" : mapId + "_conquest",
            GameModeKind.BossRush => mapId + "_sandbox",
            GameModeKind.Weekly => WeeklyFortress.MapId + "_siege",
            _ => LegacyMapFile(kind, mapId),
        };

        private static string LegacyMapFile(GameModeKind kind, string mapId) =>
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
                Bases = Bases(world, GameModeKind.Conquest, seed, menu: true),
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
                Bases = Bases(world, GameModeKind.Conquest, seed),
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
                Bases = Bases(world, GameModeKind.Deathmatch, seed),
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
                Bases = Bases(world, GameModeKind.KingOfTheHill, seed),
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
            // The time bank: harder assaults start with less on the clock.
            var start = Difficulty switch { AiDifficulty.Hard => 270f, AiDifficulty.Easy => 360f, _ => 300f };
            _mode = new AssaultMode(new AssaultRules
            {
                StartSeconds = start, Attacker = PlayerSide(20f, 1.45f), Defender = EnemySide(26f, 1.05f, Difficulty, world.Catalog),
                Bases = Bases(world, GameModeKind.Assault, seed),
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
            outcome.Rows.Add((Strings.Get("stat.taken"), Strings.Format("mode.assault.sector", UnityEngine.Mathf.Min(_mode.Sector + 1, _mode.SectorCount), _mode.SectorCount)));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    /// <summary>
    /// Defend (phòng thủ): the enemy's Breakthrough, three sectors the player holds one behind the
    /// other with dug-in guns; the enemy's clock grows with every sector it takes. Hold until it runs out.
    /// </summary>
    /// <summary>
    /// Defend: the player's own base. The siege map's fortress (walls, gates, guard towers, gun
    /// turrets, relay stations, shield generators and the command HQ in the keep) is the
    /// player's, garrison included, and the enemy lays siege to it in three stages, as the player
    /// does in Siege: the outer line, the shield generators, then the HQ. The player holds until
    /// the attacker's clock runs out, with enemy waves flown in on top of what it buys. Endless:
    /// no clock, the waves grow and turn elite until the HQ falls, and the best wave is kept.
    /// </summary>
    internal sealed class DefendSession : ModeSession
    {
        private const string BestKey = "mb.endless.best";

        private readonly bool _endless;
        private SiegeMode _mode;

        public DefendSession(bool endless) => _endless = endless;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get(_endless ? "mode.endless.kicker" : "mode.defend.kicker");
        public override string Subtitle => Strings.Get(_endless ? "mode.endless.sub" : "mode.defend.sub");
        public override string StartToast => Strings.Get(_endless ? "mode.endless.toast" : "mode.defend.toast");

        /// <summary>The furthest wave held in Endless.</summary>
        public static int BestWave => UnityEngine.PlayerPrefs.GetInt(BestKey, 0);

        protected override void Build(SimWorld world, int seed)
        {
            var hard = Difficulty == AiDifficulty.Hard;
            var easy = Difficulty == AiDifficulty.Easy;
            var defender = PlayerSide(24f, 1.2f);
            defender.ArmyCap = 36;
            var attacker = EnemySide(26f, hard ? 1.6f : easy ? 1.15f : 1.35f, Difficulty, world.Catalog);
            attacker.ArmyCap = 40;
            _mode = new SiegeMode(new SiegeRules
            {
                PlayerDefends = true, Endless = _endless,
                // The clock the enemy has to break in: longer the harder it is.
                StartSeconds = hard ? 540f : easy ? 420f : 480f, StageBonus = new[] { 60f, 90f }, MaxBank = 900f,
                WaveSeconds = _endless ? 55f : 75f, StageCp = 12f,
                Attacker = attacker, Defender = defender,
                AttackerBase = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed),
            });
            Mode = _mode;
            _mode.Setup(world);
            var enemy = AddEnemyCommander(_mode, seed, CommanderStance.Attack);
            enemy.Goal = w => w.TryGetProp(_mode.Target(w), out var objective) ? objective.Position : _mode.Fortress;
            enemy.Demolish = w => _mode.Target(w);
            enemy.Plunder = _ => _mode.BountyTargets;
            enemy.RoleMix = ConquestAi.SiegeMix;
            // The player's commander stands on whatever the enemy is going for.
            var player = AddPlayerCommander(_mode, seed);
            player.Stance = CommanderStance.Defend;
            player.Goal = w => w.TryGetProp(_mode.Target(w), out var objective) ? objective.Position : _mode.Fortress;
            player.Leash = 40f;
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            var integrity = 1f - _mode.Progress(world);
            var goal = Strings.Format("mode.siege.stage", UnityEngine.Mathf.Min(3, _mode.Stage),
                Strings.Get(_mode.Stage switch { 1 => "base.goal1", 2 => "base.goal2", _ => "base.goal3" }));
            var detail = Strings.Format("base.waveOf", _mode.Wave) + "  ·  " + $"{UnityEngine.Mathf.RoundToInt(integrity * 100f)}%";
            hud.SetMission(goal, detail, integrity, _endless ? -1f : _mode.SecondsLeft(world), scratch);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("result.waves"), _mode.Wave.ToString()));
            if (_endless)
            {
                var best = BestWave;
                if (_mode.Wave > best) UnityEngine.PlayerPrefs.SetInt(BestKey, _mode.Wave);
                outcome.Subtitle = Strings.Format(_mode.Wave > best ? "endless.record" : "endless.reached", _mode.Wave);
                outcome.Rows.Add((Strings.Get("endless.best"), UnityEngine.Mathf.Max(best, _mode.Wave).ToString()));
                outcome.Reward = Rewards.Survival(Difficulty, _mode.Wave, kills);
                return outcome;
            }
            outcome.Rows.Add((Strings.Get("base.integrity"), $"{UnityEngine.Mathf.RoundToInt((1f - _mode.Progress(world)) * 100f)}%"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            if (outcome.Result > 0) outcome.Reward.Coins += 120;
            return outcome;
        }
    }

    /// <summary>
    /// The weekly fortress (see <see cref="WeeklyFortress"/>): a siege that starts at the stage an
    /// earlier attack this week reached, and pays its weekly reward on the first win of the week.
    /// </summary>
    internal sealed class WeeklySession : ModeSession
    {
        private SiegeMode _mode;
        private int _week, _startStage;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get("mode.weekly.kicker");
        public override string Subtitle => Strings.Format("mode.weekly.sub", _week % 100, Strings.Get("map." + WeeklyFortress.MapId));
        public override string StartToast => Strings.Format("mode.weekly.toast", _startStage, WeeklyFortress.Reward);

        protected override void Build(SimWorld world, int seed)
        {
            _week = WeeklyFortress.Week;
            _startStage = PlayerProfile.WeeklyStage(_week);
            var attacker = PlayerSide(26f, 1.5f);
            attacker.ArmyCap = 34;
            _mode = new SiegeMode(new SiegeRules
            {
                StartSeconds = 300f, StartStage = _startStage,
                Attacker = attacker, Defender = EnemySide(22f, 1.15f, Difficulty, world.Catalog),
            });
            Mode = _mode;
            _mode.Setup(world);
            var defender = AddEnemyCommander(_mode, seed, CommanderStance.Defend);
            defender.DefendPoint = _mode.Fortress;
            var player = AddPlayerCommander(_mode, seed);
            player.Goal = w => w.TryGetProp(_mode.Target(w), out var hq) ? hq.Position : _mode.Fortress;
            player.Demolish = w => _mode.Target(w);
            player.Plunder = _ => _mode.BountyTargets;
            player.RoleMix = ConquestAi.SiegeMix;
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            var progress = _mode.Progress(world);
            var goal = Strings.Format("mode.siege.stage", UnityEngine.Mathf.Min(3, _mode.Stage),
                Strings.Get(_mode.Stage switch { 1 => "siege.goal1", 2 => "siege.goal2", _ => "siege.goal3" }));
            hud.SetMission(goal, $"{UnityEngine.Mathf.RoundToInt(progress * 100f)}%", progress, _mode.SecondsLeft(world), scratch);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("mode.siege.goal"), $"{UnityEngine.Mathf.RoundToInt(_mode.Progress(world) * 100f)}%"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            // The rings broken stay broken for the rest of the week; the first win of the week pays.
            if (PlayerProfile.RecordWeekly(_week, UnityEngine.Mathf.Min(3, _mode.Stage), outcome.Result > 0))
            {
                outcome.Reward.Coins += WeeklyFortress.Reward;
                outcome.Rows.Add((Strings.Get("mode.weekly"), Strings.Format("weekly.reward", WeeklyFortress.Reward)));
            }
            return outcome;
        }
    }

    internal sealed class SiegeSession : ModeSession
    {
        /// <summary>Coins at the end for each fortress building knocked down.</summary>
        public const int SiegeBountyCoins = 12;

        private SiegeMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get("mode.siege.kicker");
        public override string Subtitle => Strings.Get("mode.siege.sub");
        public override string StartToast => Strings.Get("mode.siege.toast");

        protected override void Build(SimWorld world, int seed)
        {
            // The attacker has the bigger purse (a siege needs numbers); the fortress has its guns.
            var attacker = PlayerSide(34f, 1.8f);
            attacker.ArmyCap = 40;
            attacker.Bank = 40f;
            // The time bank: harder sieges start with less on the clock.
            var start = Difficulty switch { AiDifficulty.Hard => 270f, AiDifficulty.Easy => 360f, _ => 300f };
            _mode = new SiegeMode(new SiegeRules
            {
                StartSeconds = start, Attacker = attacker, Defender = EnemySide(20f, Difficulty == AiDifficulty.Hard ? 1.05f : 0.85f, Difficulty, world.Catalog),
                AttackerBase = PlayerProfile.BaseLoadout,
            });
            Mode = _mode;
            _mode.Setup(world);
            var defender = AddEnemyCommander(_mode, seed, CommanderStance.Defend);
            defender.DefendPoint = _mode.Fortress;
            var player = AddPlayerCommander(_mode, seed);
            player.Goal = w => w.TryGetProp(_mode.Target(w), out var hq) ? hq.Position : _mode.Fortress;
            player.Demolish = w => _mode.Target(w);
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            var progress = _mode.Progress(world);
            var goal = Strings.Format("mode.siege.stage", UnityEngine.Mathf.Min(3, _mode.Stage),
                Strings.Get(_mode.Stage switch { 1 => "siege.goal1", 2 => "siege.goal2", _ => "siege.goal3" }));
            hud.SetMission(goal, $"{UnityEngine.Mathf.RoundToInt(progress * 100f)}%", progress, _mode.SecondsLeft(world), scratch);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("mode.siege.goal"), $"{UnityEngine.Mathf.RoundToInt(_mode.Progress(world) * 100f)}%"));
            outcome.Rows.Add((Strings.Get("stat.razed"), _mode.BuildingsRazed.ToString()));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            // Levelling a fortress pays extra, and every building knocked down on the way.
            if (outcome.Result > 0) outcome.Reward.Coins += 150;
            outcome.Reward.Coins += _mode.BuildingsRazed * SiegeBountyCoins;
            return outcome;
        }
    }

    internal sealed class BossRushSession : ModeSession
    {
        private BossRushMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get("mode.bossrush.kicker");
        public override string Subtitle => Strings.Get("mode.bossrush.sub");
        public override string StartToast => Strings.Get("mode.bossrush.toast");

        protected override void Build(SimWorld world, int seed)
        {
            // A bigger opening purse and income than the old 30 CP and 1.6: playtests found the rush too hard to win.
            // Round 6: 1.8 -> 2.0 (Hard 1.55 -> 1.75), a 45 CP bank so the start and bounties are not clipped.
            var player = PlayerSide(40f, Difficulty == AiDifficulty.Hard ? 1.75f : 2f);
            player.ArmyCap = 36;
            player.Bank = 45f;
            // One boss of each kind, which variant drawn by the battle's seed.
            // The bounty comes as the boss loses health (8 CP at 75, 50 and 25 %) and 12 on the kill.
            _mode = new BossRushMode(new BossRushRules { Player = player, Bounty = 12f, StepBounty = 8f, Bosses = BossRushRules.Roster(seed) });
            Mode = _mode;
            _mode.Setup(world);
            world.TryGetRally(PlayerTeam, out var home);
            // The bosses and their escorts come for the player's army.
            Waves = new TacticalAi(EnemyTeam, PlayerTeam, seed) { Objective = w => PlayerCentre(w) ?? home };
            AddPlayerCommander(_mode, seed).Goal = w => w.TryGetVehicle(_mode.Boss, out var b) && b.IsAlive ? b.Position : null;
        }

        private static Vector2? PlayerCentre(SimWorld world)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.Vehicles)
                if (v.IsAlive && v.Team == PlayerTeam && !v.Flying)
                {
                    sum += v.Position;
                    n++;
                }
            return n > 0 ? sum / n : null;
        }

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            hud.SetMission(Strings.Get("mode.bossrush.goal"), $"{_mode.Defeated} / {_mode.Total}", _mode.Defeated / (float)_mode.Total,
                _mode.SecondsLeft(world), scratch);
            if (world.TryGetVehicle(_mode.Boss, out var boss) && boss.IsAlive) hud.SetBoss(Strings.Card(boss.Def.Id), boss.Hp / boss.MaxHp);
            else hud.SetBoss(null, 0f);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Kicker };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("mode.bossrush.goal"), $"{_mode.Defeated} / {_mode.Total}"));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            // Every boss brought down pays, win or lose.
            outcome.Reward.Coins += 120 * _mode.Defeated;
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
            world.EnableEconomy(new Sim.Economy.TeamEconomy(PlayerTeam, 16f, income: 0.9f,
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
            // Heroic and Iron: the enemy comes stronger; Iron also leaves the player poorer and without fire support.
            _tier = System.Math.Clamp(MatchSettings.MissionTier, 0, 2);
            if (_tier > 0 && enemy != null)
            {
                enemy.StartCp *= 1.3f;
                enemy.Income *= 1.25f;
            }
            if (_tier == 2)
            {
                playerSide.Income *= 0.8f;
                playerSide.Supports = System.Array.Empty<string>();
            }
            _mode = new MissionMode(_tier > 0 ? _def.Harder(1.3f) : _def, playerSide, enemy);
            Mode = _mode;
            _mode.Setup(world);
            // Bases in a mission: a camp for either side if the mission gives one, and outposts on marked points.
            if (_def.PlayerBase != BaseRole.None || _def.EnemyBase != BaseRole.None)
                BaseDefences.Build(world, new BaseSetup()
                    .Set(PlayerTeam, PlayerProfile.BaseLoadout, _def.PlayerBase)
                    .Set(EnemyTeam, BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed), _def.EnemyBase), PlayerTeam, EnemyTeam);
            if (_def.Outposts.Count > 0)
            {
                world.Bases.Ensure(PlayerTeam, PlayerProfile.BaseLoadout);
                world.Bases.Ensure(EnemyTeam, BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed));
                foreach (var id in _def.Outposts) world.Bases.OutpostPoints.Add(id);
                world.Bases.PointOwner = id =>
                {
                    foreach (var p in _mode.Points)
                        if (p.Def.Id == id) return p.Owner;
                    return -1;
                };
            }

            if (commander)
            {
                var stance = _def.EnemyStance == "Defend" ? CommanderStance.Defend : CommanderStance.Attack;
                var enemyAi = AddEnemyCommander(_mode, seed, stance);
                enemyAi.Goal = w => _mode.EnemyGoal(w);
                // Protect: the enemy comes to knock the player's buildings down.
                if (_def.Goal == MissionGoal.Protect) enemyAi.Demolish = w => _mode.EnemyDemolish(w);
            }
            else if (_def.EnemyAi == "waves")
            {
                world.TryGetRally(PlayerTeam, out var home);
                Waves = new TacticalAi(EnemyTeam, PlayerTeam, seed) { Objective = w => _mode.EnemyGoal(w) ?? home };
                if (_def.Goal == MissionGoal.Protect) Waves.Demolish = w => _mode.EnemyDemolish(w);
            }
            var player = AddPlayerCommander(_mode, seed);
            if (_tier == 2) player.AutoStrike = false;
            player.Goal = w => _mode.PlayerGoal(w);
            player.Demolish = w => _mode.PlayerDemolish(w);
            // A demolition inside a fortress is a siege: guns to break it from outside its reach.
            if (_def.Goal == MissionGoal.Destroy && _def.Variant == "siege") player.RoleMix = ConquestAi.SiegeMix;
            // Holding a point: fight whatever comes at it, but never wander off and leave it open.
            if (_def.Goal == MissionGoal.Hold) player.Leash = 32f;
            if (_def.Goal is MissionGoal.Survive or MissionGoal.ShootDown)
            {
                foreach (var p in world.Map.Points)
                    if (_def.Points.Count > 0 && p.Id == _def.Points[0]) player.DefendPoint = p.Position;
                if (player.DefendPoint == null && world.TryGetRally(PlayerTeam, out var home) && world.TryGetRally(EnemyTeam, out var threat))
                    player.DefendPoint = Vector2.Lerp(home, threat, 0.33f);
            }
        }

        private int _nextTip;
        private int _tier;

        /// <summary>Whether the mission's own third-star challenge was met.</summary>
        private bool ChallengeMet(SimWorld world) => _def.Challenge switch
        {
            "NoStrikes" => world.StrikesCalled(PlayerTeam) == 0,
            "NoAircraft" => world.AircraftBought(PlayerTeam) == 0,
            "Kills" => _mode.Kills >= _def.ChallengeValue,
            _ => true,
        };

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            // Mission hints (the tutorial), each once, when their moment comes.
            while (_nextTip < _def.Tips.Count && world.Time >= _def.Tips[_nextTip].at)
                hud.Toast(Strings.Get(_def.Tips[_nextTip++].key), seconds: 6f);
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            var (done, needed) = _mode.Count(world);
            var detail = _def.Goal switch
            {
                MissionGoal.Hold or MissionGoal.Survive or MissionGoal.Protect => $"{Clock(done)} / {Clock(needed)}",
                MissionGoal.Intercept when _mode.LaunchIn(world) >= 0f => Strings.Format("mission.launchIn", Clock(_mode.LaunchIn(world))),
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
            outcome.Reward = Rewards.Mission(_def, won, (float)world.Time, _mode.Losses, ChallengeMet(world), _tier);
            if (_tier > 0) outcome.Rows.Add((Strings.Get("tier.label"), Strings.Get("tier." + _tier)));
            return outcome;
        }
    }
}

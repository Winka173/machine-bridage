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

        /// <summary>The result's title: the mission's name, or the mode's (never both: not "Operation 02 / Conquest").</summary>
        public string Subtitle { get; set; }

        /// <summary>A line under the title (an endless run's record); null for none.</summary>
        public string Note { get; set; }

        public List<(string label, string value)> Rows { get; } = new();

        /// <summary>After a defeat: one or two things to change, from how the battle went (filled by the runner).</summary>
        public List<string> Hints { get; } = new();
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

        /// <summary>The allied commander of a multi-stage mission (its own units only; null when there is none).</summary>
        protected TacticalAi AllyAi;

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

        /// <summary>The key the enemy's elite budget goes by (prompt 8 H): Easy, Normal, Hard, or a mission tier's Heroic and Iron.</summary>
        public virtual string EliteDifficulty => Difficulty.ToString();

        /// <summary>The enemy's general (a campaign mission's), whose favoured cards become elites first; null for none.</summary>
        public virtual string EnemyGeneral => null;

        /// <summary>The elite budget's key for a difficulty and a mission tier (0 as written, 1 Heroic, 2 Iron).</summary>
        public static string EliteKey(string difficulty, int tier) => tier switch { 1 => "Heroic", 2 => "Iron", _ => difficulty ?? "Normal" };

        /// <summary>A side's elite budget from the catalog's rules for a difficulty key, and its general.</summary>
        public static void SetElites(SimWorld world, int team, string key, string general)
        {
            var rules = world.Catalog.Elites;
            var budget = world.Elites(team);
            budget.Share = rules.BudgetFor(key);
            budget.Cap = rules.CapFor(key);
            budget.General = general != null && world.Catalog.Generals.TryGetValue(general, out var g) ? g : null;
        }

        public void TickAi(SimWorld world, float dt)
        {
            foreach (var c in Commanders) c.Tick(world, dt);
            Waves?.Tick(world, dt);
            AllyAi?.Tick(world, dt);
            Events?.Tick(world, dt);
        }

        /// <summary>Supply drops and bomber raids (every mode but the scripted campaign).</summary>
        protected BattleEvents Events;

        /// <summary>The weather turned to night or back (the fortress modes sound their sirens at night).</summary>
        public virtual void SetNight(bool night) { }

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
            var ai = new ConquestAi(objectives, EnemyTeam, PlayerTeam, Difficulty, seed)
            {
                Stance = stance,
                // Very Hard knows the player's deck from the start (never where anything is).
                KnownDeck = Difficulty == AiDifficulty.VeryHard ? MatchSettings.DeckVehicles : null,
            };
            Commanders.Add(ai);
            return ai;
        }

        /// <summary>A boss's bar: its name, health, and for a multi-phase boss the marks and the phase it is in.</summary>
        protected static void ShowBoss(BattleHud hud, MachineBrigade.Sim.Entities.Vehicle boss, string name = null, SimWorld world = null)
        {
            name ??= Strings.Card(boss.Def.Id);
            var phases = boss.Def.Phases;
            // Prompt 9: the parts are icons under the bar now; the name only says when the hull is shut.
            if (boss.BodyLocked) name += "  ·  " + Strings.Get("boss.locked");
            var focused = world != null && world.TryGetPartFocus(PlayerTeam, out var focusBoss, out var focusPart) && focusBoss == boss.Id ? focusPart : -1;
            hud.SetBossParts(boss, focused);
            hud.SetBossHp(boss.Hp, boss.MaxHp);
            // Prompt 16: a ship running for the edge shows how long until it gets away.
            if (boss.Escaping && boss.EscapeSeconds >= 0f)
                name += "  ·  " + Strings.Format("boss.escaping", $"{(int)boss.EscapeSeconds / 60}:{(int)boss.EscapeSeconds % 60:00}");
            hud.SetBossEscorts(world != null ? world.EscortsAlive(boss.Id) : 0);
            hud.SetBossRank(boss.Def.RankDef);
            hud.SetBossBigAttack(boss);
            // Prompt 19 B.5: a tiered boss's altitude and countdown, and its phase marks on the bar.
            hud.SetBossTier(boss, world?.Time ?? 0.0);
            if (phases.Count == 0 && boss.Def.Tiers is { Marks: { Count: > 0 } tierMarks })
            {
                hud.SetBoss(name, boss.Hp / boss.MaxHp, boss.TierPhase, new List<float>(tierMarks), false);
                return;
            }
            if (phases.Count == 0)
            {
                hud.SetBoss(name, boss.Hp / boss.MaxHp);
                return;
            }
            var marks = new List<float>(phases.Count);
            foreach (var p in phases) marks.Add(p.At);
            hud.SetBoss(name, boss.Hp / boss.MaxHp, boss.Phase, marks, boss.Transforming);
        }

        /// <summary>A multi-part boss's parts on its bar: "  ·  engine 3/4 · drone bay 2/2 · radar 1/1 · hull shielded" (prompt 9 draws them as icons).</summary>
        internal static string PartsLine(MachineBrigade.Sim.Entities.Vehicle boss)
        {
            if (!boss.HasParts) return "";
            var kinds = new List<string>();
            var alive = new Dictionary<string, int>();
            var total = new Dictionary<string, int>();
            for (var i = 0; i < boss.Def.Parts.Count; i++)
            {
                var kind = boss.Def.Parts[i].Kind;
                if (!total.ContainsKey(kind))
                {
                    kinds.Add(kind);
                    total[kind] = 0;
                    alive[kind] = 0;
                }
                total[kind]++;
                if (!boss.IsPartBroken(i)) alive[kind]++;
            }
            var bits = new List<string>();
            foreach (var kind in kinds) bits.Add(Strings.Format("boss.parts", Strings.Get("part." + kind), alive[kind], total[kind]));
            if (boss.BodyLocked) bits.Add(Strings.Get("boss.locked"));
            return "  ·  " + string.Join(" · ", bits);
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

        /// <summary>A score that says whose is whose: "Us 0 · Enemy 331".</summary>
        protected static string Sides(int us, int enemy) => Strings.Format("result.sides", us, enemy);

        protected static int OutcomeOf(MatchResult result) => result.IsDraw ? 0 : result.WinningTeam == PlayerTeam ? 1 : -1;

        /// <summary>
        /// The enemy's cards in a quick battle (prompt 13 I.2): a deck drawn from what the player has
        /// unlocked (everything on Hard and Very Hard) by <see cref="ConquestAi.PickDeck"/>: eight on Easy
        /// and Normal, ten on Hard, twelve on Very Hard (built against the player's deck).
        /// </summary>
        protected static (string[] vehicles, string[] supports) EnemyDeck(AiDifficulty difficulty, Catalog catalog, int seed = 1)
        {
            var pool = new List<string>();
            foreach (var id in MatchSettings.AllVehicles)
                if (catalog.Vehicles.ContainsKey(id) && !Progression.IsPremium(id) &&
                    (difficulty >= AiDifficulty.Hard || PlayerProfile.IsUnlocked(id))) pool.Add(id);
            var vehicles = ConquestAi.PickDeck(catalog, pool, difficulty, seed, difficulty == AiDifficulty.VeryHard ? MatchSettings.DeckVehicles : null);
            var supports = new List<string>();
            foreach (var id in MatchSettings.AllSupports)
                if (catalog.TryGetSupport(id, out _) && !Progression.IsPremium(id) &&
                    (difficulty >= AiDifficulty.Hard || PlayerProfile.IsUnlocked(id))) supports.Add(id);
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
            var enemyLoadout = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed, against: MatchSettings.DeckVehicles);
            var playerLoadout = menu ? BaseLoadout.ForAi(world.Catalog, "Normal", "default", seed + 5) : PlayerProfile.BaseLoadoutOn(world.Map, PlayerTeam);
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

        protected static SideSetup EnemySide(float cp, float income, AiDifficulty difficulty, Catalog catalog, int seed = 1)
        {
            var (vehicles, supports) = EnemyDeck(difficulty, catalog, seed);
            return new SideSetup { StartCp = cp, Income = income, Vehicles = vehicles, Supports = supports };
        }

        /// <summary>The session for the chosen mode (or the menu's AI-versus-AI battle).</summary>
        /// <param name="mission">A campaign mission to play (tests, a replay); null: the one chosen on the menu.</param>
        public static ModeSession Create(GameModeKind kind, bool menu, SimWorld world, int seed, MissionDef mission = null)
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
                GameModeKind.Sandbox => new SandboxSession(),
                GameModeKind.Campaign => new MissionSession(mission ?? Campaign.Get(MatchSettings.Mission) ?? Campaign.All[0]),
                _ => new ConquestSession(),
            };
            if (!menu && kind != GameModeKind.Campaign) session.Difficulty = MatchSettings.Difficulty;
            world.ModeTag = menu ? "Menu" : kind.ToString();
            session.Build(world, seed);
            // Prompt 21: the Sandbox sets up its own sides, bosses and weather; no difficulty, events, elites or doctrines.
            if (!menu && kind == GameModeKind.Sandbox) return session;
            // Prompt 13 I.1: the enemy's income by difficulty (Easy x0.8, Normal x1, Hard x1.2, Very Hard x1.4).
            if (!menu && kind != GameModeKind.Campaign && world.TryGetEconomy(EnemyTeam, out var enemyEconomy))
                enemyEconomy.ScaleIncome(BuyProfile.For(session.Difficulty).Income);
            // Supply drops everywhere; no bomber raids in Boss Rush (they hit the army massed round the boss).
            if (menu || kind != GameModeKind.Campaign) session.Events = new BattleEvents(seed, raids: kind != GameModeKind.BossRush);
            // Elites (prompt 8 H): a share of the enemy's spending by difficulty, not a chance per
            // delivery (both sides in the menu battle).
            SetElites(world, EnemyTeam, menu ? "Normal" : session.EliteDifficulty, menu ? null : session.EnemyGeneral);
            if (menu) SetElites(world, PlayerTeam, "Normal", null);
            // Boss escorts (prompt 16 F): how many alive at once by difficulty, fewer in Boss Rush.
            if (!menu) world.EscortSettings = MachineBrigade.Sim.Content.EscortSettings.For(world.Catalog.EscortRules, session.EliteDifficulty,
                bossRush: kind == GameModeKind.BossRush);
            // Prompt 18: every boss's big attack, wherever it appears, scaled by difficulty.
            if (!menu) world.BigAttackSettings = MachineBrigade.Sim.Content.BigAttackSettings.For(world.Catalog.BigAttackRules, session.EliteDifficulty);
            // Doctrines: the player's choice; a hard enemy picks one of its own.
            if (!menu && Progression.DoctrineOwned(MatchSettings.Doctrine))
                world.SetDoctrine(PlayerTeam, MachineBrigade.Sim.Content.Doctrine.Get(MatchSettings.Doctrine));
            if (session.Difficulty >= AiDifficulty.Hard || menu)
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
            // Prompt 17 A.2: the long battlefield (300 x 480 m, the layered base) where the map has one; else its fortified
            // 300 m version; else Conquest's.
            GameModeKind.Siege or GameModeKind.Defend or GameModeKind.Endless => Fortified(mapId),
            // Prompt 16: part way through, the rush may be at sea (Lighthouse Bay) for its ship.
            GameModeKind.BossRush => (BossRushSession.Pending?.Map ?? mapId) + "_sandbox",
            GameModeKind.Weekly => Fortified(WeeklyFortress.MapId),
            _ => LegacyMapFile(kind, mapId),
        };

        private static string Fortified(string mapId) =>
            UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + mapId + "_long") != null ? mapId + "_long"
            : UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + mapId + "_siege") != null ? mapId + "_siege" : mapId + "_conquest";

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
                Bases = Bases(world, GameModeKind.Conquest, seed, menu: true), UnderdogAfter = 0f,
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
            var (vehicles, supports) = EnemyDeck(Difficulty, world.Catalog, seed);
            _mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.DeckVehicles.ToArray(), PlayerSupports = MatchSettings.DeckSupports.ToArray(),
                EnemyVehicles = vehicles, EnemySupports = supports,
                Bases = Bases(world, GameModeKind.Conquest, seed),
                // Prompt 13 H.1: a slower bleed (0.6 -> 0.5 a second) and less CP a point (0.3 -> 0.15), so the side
                // ahead snowballs less and a battle runs 6-10 minutes.
                Bleed = 0.5f, PointIncome = 0.15f,
            });
            Mode = _mode;
            _mode.Setup(world);
            // Prompt 13 H.1: the enemy's commander earns 18 % more here: it takes and holds points worse than a
            // player does (the measured side won five battles in six without it).
            if (world.TryGetEconomy(EnemyTeam, out var enemy)) enemy.ScaleIncome(1.18f);
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
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.conquest") };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("stat.score"), Sides(_mode.Tickets(PlayerTeam), _mode.Tickets(EnemyTeam))));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            return outcome;
        }
    }

    internal sealed class DeathmatchSession : ModeSession
    {
        private DeathmatchMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Score, ScoreLabel = "stat.score" };
        public override string Kicker => Strings.Get("mode.deathmatch.kicker");
        public override string Subtitle => Strings.Format("mode.deathmatch.sub", _mode.ScoreTarget);
        public override string StartToast => Strings.Format("mode.deathmatch.toast", _mode.ScoreTarget);

        protected override void Build(SimWorld world, int seed)
        {
            _mode = new DeathmatchMode(new DeathmatchRules
            {
                // Prompt 13 H.2: the enemy 1.35 -> 1.2 income (a straight fight: it won every measured battle).
                Player = PlayerSide(18f, 1.35f), Enemy = EnemySide(18f, 1.2f, Difficulty, world.Catalog, seed),
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
            hud.SetScore(_mode.Score(PlayerTeam), _mode.Score(EnemyTeam), _mode.ScoreTarget, scratch);
            hud.SetTimer(_mode.SecondsLeft(world));
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.deathmatch") };
            outcome.Rows.Add((Strings.Get("stat.score"), Sides(_mode.Score(PlayerTeam), _mode.Score(EnemyTeam))));
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
                // Prompt 13 H.3: the enemy 1.2 -> 1.1 income (it won two battles in three).
                Player = PlayerSide(16f, 1.2f), Enemy = EnemySide(16f, 1.1f, Difficulty, world.Catalog, seed),
                Bases = Bases(world, GameModeKind.KingOfTheHill, seed),
                ScoreTarget = 170f,
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
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.hill") };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("stat.score"), Sides(_mode.Score(PlayerTeam), _mode.Score(EnemyTeam))));
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
            var start = Difficulty switch { AiDifficulty.VeryHard => 255f, AiDifficulty.Hard => 270f, AiDifficulty.Easy => 360f, _ => 300f };
            _mode = new AssaultMode(new AssaultRules
            {
                // Prompt 13 H.4: the defender 26 -> 32 CP and 1.05 -> 1.3 income, 12 -> 8 CP a sector for the attacker.
                StartSeconds = start, Attacker = PlayerSide(20f, 1.45f), Defender = EnemySide(32f, 1.3f, Difficulty, world.Catalog, seed), SectorCp = 8f,
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
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.assault") };
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

        /// <summary>
        /// What the enemy's waves are made of: a swarm of cheap, fast vehicles that grows wave on
        /// wave (armoured cars, technicals, drone trucks, light tanks, car bombs, jeeps), with a
        /// heavy vehicle every few waves.
        /// </summary>
        public static readonly string[] Swarm =
            { "armored_car", "rocket_technical", "light_tank", "fpv_carrier", "zu23_technical", "armored_car", "vbied", "scout_jeep" };

        public static readonly string[] Heavy = { "main_battle_tank", "mlrs", "heavy_tank", "attack_helicopter", "artillery" };

        /// <summary>Prompt 13 H.7: siege breakers in the waves (bulldozers, siege guns, long guns that outrange the towers).</summary>
        public static readonly string[] Breachers = { "armored_bulldozer", "siege_tank", "heavy_rocket_artillery", "artillery" };

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
            var hard = Difficulty >= AiDifficulty.Hard;
            var easy = Difficulty == AiDifficulty.Easy;
            var defender = PlayerSide(30f, 1.35f);
            defender.ArmyCap = 38;
            // The difficulty's income multiplier (ModeSession.Create) sets Easy, Hard and Very Hard apart.
            var attacker = EnemySide(22f, 1.1f, Difficulty, world.Catalog, seed);
            attacker.ArmyCap = 40;
            _mode = new SiegeMode(new SiegeRules
            {
                PlayerDefends = true, Endless = _endless,
                // The clock the enemy has to break in: longer the harder it is.
                StartSeconds = hard ? 540f : easy ? 420f : 480f, StageBonus = new[] { 60f, 90f }, MaxBank = 900f,
                WaveSeconds = _endless ? 55f : 70f, StageCp = 12f, Hardening = 4.5f, LineHardening = 2f, RetreatCp = new[] { 24f, 32f },
                // The player's inner lines are the strong ones.
                // Prompt 13 H.7: Defend's outer line 1 -> 1.45 and the inner ones 1.4 / 1.8 -> 1.25 / 1.4 (the outer line
                // always fell and the HQ never did); Endless 1.2 / 1.3 / 1.5.
                // The balance pass after prompt 18 (D.2): the outer line fell in every battle (15 of 15 at 3-5 minutes, the HQ
                // always held): outer 1.45 -> 2.0 as tough and 1.15 -> 1.3 as hard-hitting, the first waves smaller; the inner as they were.
                LineHealth = _endless ? new[] { 1.2f, 1.3f, 1.5f } : new[] { 2.0f, 1.25f, 1.4f },
                LineDamage = _endless ? new[] { 1.05f, 1.15f, 1.25f } : new[] { 1.3f, 1.1f, 1.2f },
                // Swarms that grow in numbers, not heavier (up to the ceiling of attackers alive).
                WaveRoster = Available(world, Swarm), WaveHeavy = Available(world, Heavy),
                WaveStart = _endless ? (hard ? 6 : easy ? 4 : 5) : hard ? 4 : easy ? 2 : 3, WaveGrowth = _endless ? 1.2f : hard ? 2.0f : 1.8f, WaveCompound = _endless ? 0.06f : 0f, WaveMax = 36, HeavyEvery = 3,
                EliteFrom = _endless ? 6 : 99, WaveSeed = seed,
                // Prompt 13 H.7-H.8: the waves by the base they face, drawn against it, with siege breakers.
                ScaleToBase = true, CounterBase = true, BreachWave = true, WaveBreachers = Available(world, Breachers), BreachFrom = 2, BreachEvery = 3,
                // The player's fortress: exactly their own base loadout in its lines' hardpoints (on a long battlefield
                // the plan laid on its layered base, prompt 17 B.5).
                FortressLoadout = world.Map.Fortress is { Layered: true } ? PlayerProfile.BaseLoadoutOnLayered(world.Map) : PlayerProfile.BaseLoadout,
                Attacker = attacker, Defender = defender,
            });
            Mode = _mode;
            _mode.Setup(world);
            var enemy = AddEnemyCommander(_mode, seed, CommanderStance.Attack);
            // The enemy blows in the player's gates on its way to each line's objectives.
            enemy.Goal = w => _mode.AttackGoal(w);
            enemy.Demolish = w => _mode.AttackTarget(w);
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
            var goal = Strings.Format("base.line", UnityEngine.Mathf.Min(3, _mode.Stage),
                Strings.Get(_mode.Stage switch { 1 => "base.goal1", 2 => "base.goal2", _ => "base.goal3" }));
            var detail = Strings.Format("base.waveOf", _mode.Wave) + "  ·  " + $"{UnityEngine.Mathf.RoundToInt(integrity * 100f)}%";
            hud.SetMission(goal, detail, integrity, _endless ? -1f : _mode.SecondsLeft(world), scratch);
            hud.SetWavePreview(_mode.NextWave, _mode.SecondsToWave(world), _mode.Wave + 1, _mode.Held);
            hud.SetSuperGun(_mode.SuperGunCountdown(world), _mode.SuperGunDown, ours: true);
        }

        public override void SetNight(bool night) => _mode.Night = night;

        /// <summary>The ids of a roster the catalogue has.</summary>
        private static string[] Available(SimWorld world, string[] roster) => System.Array.FindAll(roster, world.Catalog.Vehicles.ContainsKey);

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get(_endless ? "mode.endless" : "mode.defend") };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("result.waves"), _mode.Wave.ToString()));
            if (_endless)
            {
                var best = BestWave;
                if (_mode.Wave > best) UnityEngine.PlayerPrefs.SetInt(BestKey, _mode.Wave);
                outcome.Note = Strings.Format(_mode.Wave > best ? "endless.record" : "endless.reached", _mode.Wave);
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

        /// <summary>Tests: the stage to start at instead of this week's (null: the saved one).</summary>
        internal static int? TestStage;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get("mode.weekly.kicker");
        public override string Subtitle => Strings.Format("mode.weekly.sub", _week % 100, Strings.Get("map." + WeeklyFortress.MapId));
        public override string StartToast => Strings.Format("mode.weekly.toast", _startStage, WeeklyFortress.Reward);

        protected override void Build(SimWorld world, int seed)
        {
            _week = WeeklyFortress.Week;
            _startStage = TestStage ?? PlayerProfile.WeeklyStage(_week);
            var attacker = PlayerSide(26f, 1.5f);
            attacker.ArmyCap = 34;
            _mode = new SiegeMode(new SiegeRules
            {
                StartSeconds = 300f, StartStage = _startStage,
                Attacker = attacker, Defender = EnemySide(22f, 1.15f, Difficulty, world.Catalog, seed),
                // Prompt 17 B.7: on a long battlefield the same layered plan (the long table's towers).
                FortressLoadout = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, _week, layered: world.Map.Fortress is { Layered: true },
                    against: MatchSettings.DeckVehicles),
            });
            Mode = _mode;
            _mode.Setup(world);
            var defender = AddEnemyCommander(_mode, seed, CommanderStance.Defend);
            defender.DefendPoint = _mode.Fortress;
            var player = AddPlayerCommander(_mode, seed);
            player.Goal = w => _mode.AttackGoal(w);
            player.Demolish = w => _mode.AttackTarget(w);
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
            hud.SetSuperGun(_mode.SuperGunCountdown(world), _mode.SuperGunDown, ours: false);
        }

        public override void SetNight(bool night) => _mode.Night = night;

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.weekly") };
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

        /// <summary>Coins at the end for destroying the fortress's super-gun (the side objective).</summary>
        public const int SuperGunCoins = 100;

        private SiegeMode _mode;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get("mode.siege.kicker");
        public override string Subtitle => Strings.Get("mode.siege.sub");
        public override string StartToast => Strings.Get("mode.siege.toast");

        protected override void Build(SimWorld world, int seed)
        {
            // The attacker has the bigger purse (a siege needs numbers); the fortress has its guns.
            var attacker = PlayerSide(38f, 2.4f);
            attacker.ArmyCap = 44;
            attacker.Bank = 40f;
            // The fortress holds its ground with its towers and a modest garrison (its reinforcements come by its line).
            // Its income is one base (0.6) times the difficulty's multiplier (ModeSession.Create; prompt 13 I.1).
            var hard = Difficulty >= AiDifficulty.Hard;
            // Prompt 13 H.5: the garrison 12 -> 16 CP (Hard 18 -> 22) and 0.6 -> 0.8 income.
            // The balance pass after prompt 18 (D.1): 16 -> 20 CP on Normal and Easy (the measured side won 13 sieges of 15).
            var defender = EnemySide(hard ? 24f : 20f, 0.8f, Difficulty, world.Catalog, seed);
            defender.ArmyCap = hard ? 34 : 26;
            // The time bank: harder sieges start with less on the clock.
            var start = Difficulty switch { AiDifficulty.VeryHard => 400f, AiDifficulty.Hard => 420f, AiDifficulty.Easy => 540f, _ => 480f };
            _mode = new SiegeMode(new SiegeRules
            {
                // Prompt 13 H.5: 300 s more a ring broken (360 before), towers 1.2 -> 1.75 as tough, the inner rings
                // more so, and Normal mans 90 % of the hardpoints.
                StartSeconds = start, StageBonus = new[] { 300f, 300f }, MaxBank = 900f, SuperGunFirst = 150f, SuperGunSeconds = 90f,
                // The balance pass after prompt 18 (D.1): towers 1.75 -> 2.1 as tough, the inner rings hit harder.
                Hardening = 2.1f, LineHealth = new[] { 1.1f, 1.25f, 1.4f }, LineDamage = new[] { 1.05f, 1.15f, 1.25f },
                // An easier fortress leaves some of its outer hardpoints empty.
                Manning = Difficulty switch { >= AiDifficulty.Normal => 1f, _ => 0.6f },
                Attacker = attacker, Defender = defender,
                AttackerBase = PlayerProfile.BaseLoadoutOn(world.Map, PlayerTeam),
                // The fortress's towers: the enemy's base loadout for this difficulty, over every ring.
                // (Prompt 17 B.7: a long battlefield's layered base takes the long table's towers.)
                FortressLoadout = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed, layered: world.Map.Fortress is { Layered: true },
                    against: MatchSettings.DeckVehicles),
            });
            Mode = _mode;
            _mode.Setup(world);
            var garrison = AddEnemyCommander(_mode, seed, CommanderStance.Defend);
            garrison.DefendPoint = _mode.Fortress;
            var player = AddPlayerCommander(_mode, seed);
            // The army blows in a gate when the objective is behind walls nobody has broken yet,
            // brings the guns a siege needs, and shoots up the fortress's buildings for their bounties.
            player.Goal = w => _mode.AttackGoal(w);
            player.Demolish = w => _mode.AttackTarget(w);
            player.Plunder = _ => _mode.BountyTargets;
            player.RoleMix = ConquestAi.SiegeMix;
        }

        public override void SetNight(bool night) => _mode.Night = night;

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            hud.SetStats(0, 0, 0, 0f, fps);
            scratch.Clear();
            var progress = _mode.Progress(world);
            var goal = Strings.Format("mode.siege.stage", UnityEngine.Mathf.Min(3, _mode.Stage),
                Strings.Get(_mode.GateToBreak(world).IsValid ? "siege.goalGate"
                    : _mode.Stage switch { 1 => "siege.goal1", 2 => "siege.goal2", _ => "siege.goal3" }));
            hud.SetMission(goal, $"{UnityEngine.Mathf.RoundToInt(progress * 100f)}%", progress, _mode.SecondsLeft(world), scratch);
            hud.SetSuperGun(_mode.SuperGunCountdown(world), _mode.SuperGunDown, ours: false);
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get("mode.siege") };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("mode.siege.goal"), $"{UnityEngine.Mathf.RoundToInt(_mode.Progress(world) * 100f)}%"));
            outcome.Rows.Add((Strings.Get("stat.razed"), _mode.BuildingsRazed.ToString()));
            if (_mode.SuperGunDown) outcome.Rows.Add((Strings.Get("stat.superGun"), Strings.Format("result.superGun", SuperGunCoins)));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            // Levelling a fortress pays extra, and every building knocked down on the way, and its super-gun.
            if (outcome.Result > 0) outcome.Reward.Coins += 150;
            outcome.Reward.Coins += _mode.BuildingsRazed * SiegeBountyCoins;
            if (_mode.SuperGunDown) outcome.Reward.Coins += SuperGunCoins;
            return outcome;
        }
    }

    internal sealed class BossRushSession : ModeSession
    {
        private BossRushMode _mode;

        /// <summary>Prompt 16: the battlefield the rush fights its sea boss on.</summary>
        public const string SeaMap = "lighthousebay";

        /// <summary>The rush carried over from the last battlefield or a checkpoint (set before the scene is rebuilt, taken up by the next session).</summary>
        internal static BossRushCarry Pending;

        /// <summary>Prompt 20 N: the next Boss Hunt is the full one (every boss in story order), else the week's.</summary>
        internal static bool Full;

        private readonly bool _full = Full;
        private int _week;
        private IReadOnlyList<string> _roster;
        private int _checkpointsSaved;
        private MatchOutcome _outcome;

        /// <summary>Where the rush must go before its next boss, or null.</summary>
        public BossRushCarry SwitchTo => _mode?.SwitchTo;

        /// <summary>This run is the full hunt.</summary>
        public bool IsFull => _full;

        private string Key => _full ? BossHunts.FullKey : BossHunts.WeeklyKey;

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Get(_full ? "hunt.full.kicker" : "mode.bossrush.kicker");
        public override string Subtitle => Strings.Get(_full ? "hunt.full.sub" : "mode.bossrush.sub");
        public override string StartToast => Strings.Get("mode.bossrush.toast");

        protected override void Build(SimWorld world, int seed)
        {
            // A bigger opening purse and income than the old 30 CP and 1.6: playtests found the rush too hard to win.
            // Round 6: 1.8 -> 2.0 (Hard 1.55 -> 1.75), a 45 CP bank so the start and bounties are not clipped.
            var player = PlayerSide(40f, Difficulty switch { AiDifficulty.VeryHard => 1.6f, AiDifficulty.Hard => 1.75f, _ => 2f });
            player.ArmyCap = 36;
            player.Bank = 45f;
            // Prompt 20 N: the week's hunt (3 main and 7 mini bosses drawn by the week, stronger down the run, 45 minutes)
            // or the full hunt (every boss in story order, no clock); a 20 s rest that repairs 30 % of the army, a support
            // after each main boss, checkpoints. The bounty comes as the boss loses health (8 CP at 75, 50 and 25 %) and 12 on the kill.
            _week = WeeklyFortress.Week;
            _roster = _full ? BossHunts.Full : BossHunts.Weekly(_week);
            _mode = new BossRushMode(new BossRushRules
            {
                Player = player, Bounty = 12f, StepBounty = 8f, Bosses = _roster,
                SeaMap = SeaMap, HomeMap = MatchSettings.CurrentMap.Id, Resume = Pending,
                Checkpoints = _full ? HuntCheckpoints.EveryBoss : HuntCheckpoints.MainBosses, Supports = true,
                Seed = _full ? BossHunts.FullSeed : _week, Ramp = !_full, RestRepair = 0.3f, Breather = 20f,
                TimeLimit = _full ? float.MaxValue : BossHunts.WeeklyMinutes * 60f,
            });
            Pending = null;
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
            var detail = $"{_mode.Defeated} / {_mode.Total}";
            // The full hunt has no clock: its total time (the leaderboard's) instead.
            if (_full) detail += "  ·  " + Clock(_mode.TotalSeconds(world));
            hud.SetMission(Strings.Get("mode.bossrush.goal"), detail, _mode.Defeated / (float)_mode.Total, _full ? -1f : _mode.SecondsLeft(world), scratch);
            if (world.TryGetVehicle(_mode.Boss, out var boss) && boss.IsAlive) ShowBoss(hud, boss, world: world);
            else hud.SetBoss(null, 0f);
            // Prompt 20 N/O.4: the rest between bosses, the support pick after a main boss, the checkpoint kept.
            var rest = _mode.RestLeft(world);
            hud.SetHuntRest(rest >= 0f ? Strings.Format("hunt.restTitle", UnityEngine.Mathf.RoundToInt(_mode.RestRepairShare * 100f)) : null, rest,
                _mode.Next is { } next ? Strings.Format("hunt.next", Strings.Card(next)) : null, HeldLine());
            ShowSupportPick(hud, world, rest);
            if (KeepCheckpoint()) hud.Toast(Strings.Get("hunt.checkpointToast"));
        }

        /// <summary>Saves the run's newest checkpoint once (each frame, and before a switch of battlefield); true when one was saved.</summary>
        public bool KeepCheckpoint()
        {
            if (_mode == null || _mode.CheckpointsTaken == _checkpointsSaved || _mode.Checkpoint is not { } checkpoint) return false;
            _checkpointsSaved = _mode.CheckpointsTaken;
            PlayerProfile.SaveHuntCheckpoint(Key, _week, _roster, checkpoint);
            return true;
        }

        private string HeldLine()
        {
            if (_mode.Held.Count == 0) return null;
            var names = new List<string>();
            foreach (var id in _mode.Held) names.Add(Strings.Get("hunt.support." + id));
            return Strings.Format("hunt.held", string.Join(", ", names));
        }

        /// <summary>The pick of one of three supports while an offer is open; the first is taken when the rest ends.</summary>
        private void ShowSupportPick(BattleHud hud, SimWorld world, float rest)
        {
            if (_mode.Offer is not { } offer)
            {
                if (hud.SupportPickShown) hud.HideSupportPick();
                return;
            }
            if (!hud.SupportPickShown)
            {
                var options = new List<(string, string, string)>();
                foreach (var id in offer)
                    options.Add((HuntSupports.Get(id)?.Icon ?? "star", Strings.Get("hunt.support." + id), Strings.Get("hunt.support." + id + ".info")));
                hud.ShowSupportPick(Strings.Get("hunt.pickTitle"), options, index =>
                {
                    if (index < offer.Count) Choose(world, offer[index]);
                    hud.HideSupportPick();
                });
            }
            hud.SetSupportPickTime(UnityEngine.Mathf.Max(0f, rest));
        }

        /// <summary>A support picked (recorded with the player's other inputs).</summary>
        public void Choose(SimWorld world, string id)
        {
            if (_mode.Offer == null) return;
            MatchJournal.Record(world, "support", id);
            _mode.Choose(world, id);
        }

        /// <summary>A lost run's way back: its last checkpoint, as saved (with what this sitting paid), or null.</summary>
        public BossRushCarry ResumeFrom() => _roster == null ? null : PlayerProfile.HuntCheckpoint(Key, _week, _roster);

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (_outcome != null) return _outcome;
            if (_mode.Result is not { } result) return null;
            var outcome = new MatchOutcome { Result = OutcomeOf(result), Subtitle = Strings.Get(_full ? "hunt.full" : "mode.bossrush") };
            AddRows(outcome, world, kills, losses);
            outcome.Rows.Add((Strings.Get("mode.bossrush.goal"), $"{_mode.Defeated} / {_mode.Total}"));
            var total = _mode.TotalSeconds(world);
            outcome.Rows.Add((Strings.Get("hunt.time"), Clock(total)));
            outcome.Reward = Rewards.Quick(Difficulty, outcome.Result, kills, (float)world.Time / 60f);
            // Every boss brought down pays, win or lose; those paid in an earlier sitting of the run are not paid again.
            outcome.Reward.Coins += 120 * System.Math.Max(0, _mode.Defeated - _mode.PaidBefore);
            if (outcome.Result > 0)
            {
                PlayerProfile.ClearHuntCheckpoint(Key);
                if (_full)
                {
                    if (PlayerProfile.RecordFullHunt((float)total)) outcome.Rows.Add((Strings.Get("hunt.newBest"), Clock(total)));
                    if (PlayerProfile.ClaimFullHunt())
                    {
                        outcome.Reward.Coins += BossHunts.FullReward;
                        PlayerProfile.AddCrate(CrateKind.Legendary);
                        outcome.Rows.Add((Strings.Get("hunt.firstClear"), Strings.Format("hunt.full.reward", Kit.Count(BossHunts.FullReward))));
                    }
                }
                else if (PlayerProfile.ClaimWeekly(_week, "hunt"))
                {
                    outcome.Reward.Coins += BossHunts.WeeklyReward;
                    outcome.Rows.Add((Strings.Get("hunt.firstClear"), $"+{Kit.Count(BossHunts.WeeklyReward)}"));
                }
            }
            else PlayerProfile.HuntPaidUpTo(Key, _mode.Defeated);
            return _outcome = outcome;
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
                Intensity = Difficulty switch { AiDifficulty.Easy => 0.75f, AiDifficulty.Hard => 1.35f, AiDifficulty.VeryHard => 1.6f, _ => 1f },
                // Prompt 13 H.9: the waves by the deck's strength (its cards' rank and equipment).
                DeckScale = EnemyScaling.Power(System.Linq.Enumerable.Select(System.Linq.Enumerable.Where(MatchSettings.DeckVehicles, world.Catalog.Vehicles.ContainsKey),
                    id => PlayerProfile.BoostFor(world.Catalog.Vehicles[id]))) / 100f,
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
            var outcome = new MatchOutcome { Result = -1, Subtitle = Strings.Get("mode.survival"), Note = Strings.Get("result.over") };
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
            // Prompt 13 H.9: overrun when the enemy holds the rally two to one (not only when nobody is left
            // there: new vehicles come in at the rally, and a beaten army could feed them in for ever).
            var overrun = attackers > 0 && (defenders == 0 || attackers >= 4 && attackers >= defenders * 2);
            _overrunSince = overrun ? (_overrunSince < 0 ? now : _overrunSince) : -1;
            return (_wipedSince >= 0 && now - _wipedSince > 10.0) || (_overrunSince >= 0 && now - _overrunSince > 15.0);
        }
    }

    /// <summary>A campaign mission: its goal, the enemy it describes, and stars and unlocks at the end.</summary>
    internal sealed class MissionSession : ModeSession
    {
        private readonly MissionDef _def;
        private MissionMode _single;
        private OperationMode _op;
        private ConquestAi _enemyAi;

        public MissionSession(MissionDef def) => _def = def;

        public MissionDef Def => _def;

        /// <summary>The mission being played: the whole of a one-goal mission, the current stage of a staged one.</summary>
        public MissionMode Mission => _mode;

        /// <summary>The stages of a multi-stage mission (or one with an ally); null otherwise.</summary>
        public OperationMode Operation => _op;

        private MissionMode _mode => _op != null ? _op.Current : _single;

        private int Kills => _op != null ? _op.Kills : _single.Kills;
        private int Losses => _op != null ? _op.Losses : _single.Losses;

        /// <summary>A stage's name (its own text, else "Stage n").</summary>
        public string StageTitle(string stageId, int number)
        {
            var key = "stage." + _def.Id + "." + stageId;
            var text = Strings.Get(key);
            return text != key ? text : Strings.Format("stage.kicker", number);
        }

        public override HudSpec Hud => new() { Mode = HudMode.Mission };
        public override string Kicker => Strings.Format("campaign.kicker", Campaign.Label(_def));
        public override string Title => Strings.Get("mission." + _def.Id + ".name");
        public override string Subtitle => Strings.Get("goal." + _def.Goal.ToString().ToLowerInvariant());
        public override string StartToast => Strings.Get("mission." + _def.Id + ".brief");

        public override string EliteDifficulty => EliteKey(_def.Difficulty, _tier);
        public override string EnemyGeneral => GeneralOf(_def);

        /// <summary>The mission's enemy general (its AI configuration, portrait and lines), or null.</summary>
        internal static string GeneralOf(MissionDef def) => def?.General;

        protected override void Build(SimWorld world, int seed)
        {
            Difficulty = System.Enum.TryParse<AiDifficulty>(_def.Difficulty, out var d) ? d : AiDifficulty.Normal;
            var commander = _def.EnemyAi is "commander" or "both";
            // The general in command: their deck when the mission names none, their fire support,
            // their base's style.
            var general = Campaign.General(_def.General);
            EnemyStyle = _def.EnemyStyle ?? general?.Style ?? "default";
            SideSetup enemy = null;
            if (commander)
            {
                var deck = new List<string>();
                foreach (var id in _def.EnemyDeck.Count > 0 ? _def.EnemyDeck : general?.Deck ?? (IReadOnlyList<string>)System.Array.Empty<string>())
                    if (world.Catalog.Vehicles.ContainsKey(id)) deck.Add(id);
                // A general's own cards join a mission's deck (Varga's armoured bulldozer).
                if (deck.Count > 0 && _def.General is { } generalId && world.Catalog.Generals.TryGetValue(generalId, out var g))
                    foreach (var id in g.Deck)
                        if (!deck.Contains(id) && world.Catalog.Vehicles.ContainsKey(id)) deck.Add(id);
                var supports = new List<string>();
                var habits = _def.EnemySupports.Count > 0 ? _def.EnemySupports : general?.Supports;
                if (habits is { Count: > 0 })
                {
                    foreach (var id in habits)
                        if (world.Catalog.TryGetSupport(id, out _)) supports.Add(id);
                }
                else
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
            // An Operations battle: its tier (Legend too) and its mutators (null: a campaign mission).
            _run = MatchSettings.Run != null && MatchSettings.Run.Mission == _def.Id ? MatchSettings.Run : null;
            // Heroic and Iron (and Legend): the enemy comes stronger; Iron and Legend also leave the
            // player poorer and without fire support (operations.json "tiers").
            _tier = System.Math.Clamp(MatchSettings.MissionTier, 0, _run != null && Operations.LegendOpen ? Operations.Legend : 2);
            var tier = Operations.Tier(_tier);
            if (_tier > 0 && enemy != null)
            {
                enemy.StartCp *= tier.Enemy;
                enemy.Income *= 1f + (tier.Enemy - 1f) * 0.8333f;
            }
            playerSide.Income *= tier.PlayerIncome;
            if (!tier.Supports) playerSide.Supports = System.Array.Empty<string>();
            var def = _tier > 0 ? _def.Harder(tier.Enemy) : _def;
            if (_run != null && _run.Mutators.Count > 0)
            {
                var owned = new List<string>();
                foreach (var id in MatchSettings.AllVehicles)
                    if (PlayerProfile.IsUnlocked(id) && !Progression.IsPremium(id)) owned.Add(id);
                Mutators.Apply(playerSide, enemy, _run.Mutators, world.Catalog, owned);
                def = Mutators.Apply(def, _run.Mutators, world.Catalog);
                world.SetMutators(PlayerTeam, Mutators.Strength(_run.Mutators, PlayerTeam));
                world.SetMutators(EnemyTeam, Mutators.Strength(_run.Mutators, EnemyTeam));
                Mutators.ApplySea(world.SeaRules, _run.Mutators);
                foreach (var m in _run.Mutators)
                    if (m.Raids) Events = new BattleEvents(seed, raids: true);
            }
            // Stages, or an allied commander: the operation runs them (each stage a mission of its own).
            if (def.Stages.Count > 0 || def.Ally != null)
            {
                _op = new OperationMode(def, playerSide, enemy);
                Mode = _op;
            }
            else
            {
                _single = new MissionMode(def, playerSide, enemy);
                Mode = _single;
            }
            Mode.Setup(world);
            // Bases in a mission: a camp for either side if the mission gives one, and outposts on marked points.
            var enemyBase = BaseLoadout.ForAi(world.Catalog, Difficulty.ToString(), EnemyStyle, seed, _def.EnemyHq > 0 ? _def.EnemyHq : null, against: MatchSettings.DeckVehicles);
            if (_def.PlayerBase != BaseRole.None || _def.EnemyBase != BaseRole.None)
                BaseDefences.Build(world, new BaseSetup()
                    .Set(PlayerTeam, MutatedBase(PlayerProfile.BaseLoadoutOn(world.Map, PlayerTeam)), _def.PlayerBase)
                    .Set(EnemyTeam, enemyBase, _def.EnemyBase), PlayerTeam, EnemyTeam);
            // A duel's HQ is as tough as the mission says (its towers are the general's full base).
            if (_def.Goal == MissionGoal.Duel && System.Math.Abs(_def.TargetHealth - 1f) > 1e-3f)
                MissionMode.HardenHq(world, EnemyTeam, _def.TargetHealth);
            // Outposts: the marked points, and a point to set one up on (the mission's or a stage's goal).
            var outposts = new List<string>(_def.Outposts);
            void AddSite(MissionDef m)
            {
                if (m.Goal == MissionGoal.Outpost && m.Points.Count > 0 && !outposts.Contains(m.Points[0])) outposts.Add(m.Points[0]);
            }
            AddSite(_def);
            foreach (var s in _def.Stages) AddSite(s.Mission);
            if (outposts.Count > 0)
            {
                world.Bases.Ensure(PlayerTeam, PlayerProfile.BaseLoadoutOn(world.Map, PlayerTeam));
                world.Bases.Ensure(EnemyTeam, enemyBase);
                foreach (var id in outposts) world.Bases.OutpostPoints.Add(id);
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
                _enemyAi = AddEnemyCommander(Objectives, seed, stance);
                _enemyAi.Goal = w => _mode.EnemyGoal(w);
            }
            else if (_def.EnemyAi == "waves")
            {
                world.TryGetRally(PlayerTeam, out var home);
                Waves = new TacticalAi(EnemyTeam, PlayerTeam, seed) { Objective = w => _mode.EnemyGoal(w) ?? home };
            }
            var player = AddPlayerCommander(Objectives, seed);
            if (_tier == 2) player.AutoStrike = false;
            player.Goal = w => _mode.PlayerGoal(w);
            player.Demolish = w => _mode.PlayerDemolish(w);
            // The allied commander goes where the player's goal is, with its own units only.
            if (def.Ally != null)
                AllyAi = new TacticalAi(PlayerTeam, EnemyTeam, seed + 11)
                {
                    Allies = true,
                    Objective = w => _mode.PlayerGoal(w) ?? (w.TryGetRally(EnemyTeam, out var camp) ? camp : null),
                };
            Configure(world);
            // Extra mini boss (prompt 20 N.3): one more from the enemy's camp, of the mission's boss rank and chapter.
            if (_run != null && _run.Mutators.Exists(m => m.ExtraBoss) && world.TryGetRally(EnemyTeam, out var lair) &&
                ExtraBossFor(def, world.Catalog) is { } bossId)
                world.SpawnVehicle(bossId, EnemyTeam, lair, 0f);
            // Each stage sets the commanders for its own goal, in the step it begins.
            if (_op != null) _op.StageChanged += _ => Configure(world);
        }

        private OperationRun _run;

        /// <summary>
        /// Prompt 20 N.3: the Operations mutator's extra boss: a mini boss of the mission's boss (a second one when it is a
        /// mini, its mini version when it is a main boss with one), else the chapter's first mini boss (its general's), else
        /// the mission's boss itself; null when none exists.
        /// </summary>
        internal static string ExtraBossFor(MissionDef def, Catalog catalog)
        {
            var id = def.Boss?.Def;
            if (id == null)
                foreach (var s in def.Stages)
                    if (s.Mission.Boss != null)
                    {
                        id = s.Mission.Boss.Def;
                        break;
                    }
            if (id != null && catalog.Vehicles.TryGetValue(id, out var boss))
            {
                if (boss.MiniBoss) return id;
                if (boss.MiniVariant != null && catalog.Vehicles.ContainsKey(boss.MiniVariant)) return boss.MiniVariant;
            }
            if (Campaign.Chapter(def.Chapter) is { } chapter)
                foreach (var mini in chapter.Minis)
                    if (catalog.Vehicles.ContainsKey(mini)) return mini;
            return id != null && catalog.Vehicles.ContainsKey(id) ? id : null;
        }

        /// <summary>The player's base under the run's mutators: no towers (empty base), no repair bay (no repair).</summary>
        private BaseLoadout MutatedBase(BaseLoadout loadout)
        {
            if (_run == null) return loadout;
            var b = loadout;
            foreach (var m in _run.Mutators)
            {
                if (!m.EmptyBase && !m.NoRepair) continue;
                if (b == loadout) b = loadout.Clone();
                if (m.EmptyBase)
                {
                    b.Small.Clear();
                    b.Medium.Clear();
                    b.Large.Clear();
                }
                if (m.NoRepair) b.Utilities.Remove("repair_bay");
            }
            return b;
        }

        /// <summary>The commanders set for the goal of the mission (or of the stage now being played).</summary>
        private void Configure(SimWorld world)
        {
            var def = _mode.Def;
            var player = PlayerAi;
            // A demolition inside a fortress is a siege: guns to break it from outside its reach. (Not a
            // duel: there the general's army must be beaten in the field first, and the siege mix lost it.)
            player.RoleMix = def.Goal == MissionGoal.Destroy && def.Variant == "siege" ? ConquestAi.SiegeMix : null;
            // Holding a point (or an outpost on one): fight whatever comes at it, but never wander off and leave it open.
            player.Leash = def.Goal is MissionGoal.Hold or MissionGoal.Outpost ? 32f : null;
            player.DefendPoint = null;
            if (def.Goal is MissionGoal.Survive or MissionGoal.ShootDown)
            {
                foreach (var p in world.Map.Points)
                    if (def.Points.Count > 0 && p.Id == def.Points[0]) player.DefendPoint = p.Position;
                if (player.DefendPoint == null && world.TryGetRally(PlayerTeam, out var home) && world.TryGetRally(EnemyTeam, out var threat))
                    player.DefendPoint = Vector2.Lerp(home, threat, 0.33f);
            }
            // Protect: the enemy comes to knock the player's buildings down.
            System.Func<SimWorld, MachineBrigade.Sim.Core.EntityId> demolish = def.Goal == MissionGoal.Protect ? w => _mode.EnemyDemolish(w) : null;
            if (_enemyAi != null) _enemyAi.Demolish = demolish;
            if (Waves != null) Waves.Demolish = demolish;
        }

        /// <summary>The player picks a branch at a stage's end (the choice dialog), written in the journal for a replay.</summary>
        public void Choose(SimWorld world, string key)
        {
            if (_op?.PendingChoice == null) return;
            MatchJournal.Record(world, "choose", key);
            _op.Choose(world, key);
        }

        private int _nextTip;
        private int _tier;

        /// <summary>Whether the mission's own third-star challenge was met.</summary>
        private bool ChallengeMet(SimWorld world) => _def.Challenge switch
        {
            "NoStrikes" => world.StrikesCalled(PlayerTeam) == 0,
            "NoAircraft" => world.AircraftBought(PlayerTeam) == 0,
            "Kills" => Kills >= _def.ChallengeValue,
            _ => true,
        };

        public override void UpdateHud(BattleHud hud, SimWorld world, List<PointInfo> scratch, float fps)
        {
            // Mission hints (the tutorial), each once, when their moment comes.
            while (_nextTip < _def.Tips.Count && world.Time >= _def.Tips[_nextTip].at)
                hud.Toast(Strings.Get(_def.Tips[_nextTip++].key), seconds: 6f);
            hud.SetStats(0, 0, 0, 0f, fps);
            FillPoints(_mode, scratch);
            ShowChoice(hud, world);
            var goal = _mode.Def.Goal;
            var (done, needed) = _mode.Count(world);
            var detail = goal switch
            {
                MissionGoal.Hold or MissionGoal.Survive or MissionGoal.Protect => $"{Clock(done)} / {Clock(needed)}",
                MissionGoal.Intercept when _mode.LaunchIn(world) >= 0f => Strings.Format("mission.launchIn", Clock(_mode.LaunchIn(world))),
                MissionGoal.Boss or MissionGoal.Intercept => $"{UnityEngine.Mathf.RoundToInt(_mode.Progress(world) * 100f)}%",
                _ => $"{done} / {needed}",
            };
            var goalText = Strings.Get("goal." + goal.ToString().ToLowerInvariant());
            if (_op != null && _op.StageCount > 1) goalText = Strings.Format("stage.goal", _op.Path.Count, goalText);
            hud.SetMission(goalText, detail, _mode.Progress(world), _mode.SecondsLeft(world), scratch);
            if (world.TryGetVehicle(_mode.Boss, out var boss) && boss.IsAlive && !_mode.BossFled)
                ShowBoss(hud, boss, BossName(_mode.Def, boss.Def.Id), world);
            else hud.SetBoss(null, 0f);
        }

        /// <summary>
        /// An Operations battle's ending: its score (time, losses, the HQ's health; the tier's and
        /// the mutators' multipliers), the record, the mutators, and the week's reward on this
        /// week's operation (the one weekly ledger shared with the weekly fortress).
        /// </summary>
        private void OperationRows(MatchOutcome outcome, SimWorld world, bool won)
        {
            var hq = 1f;
            if (world.Bases.Of(PlayerTeam) is { } home && world.TryGetVehicle(home.Hq, out var hqVehicle))
                hq = hqVehicle.IsAlive ? hqVehicle.Hp / hqVehicle.MaxHp : 0f;
            var score = Operations.Data.Scoring.Score(won, world.Time, Losses, hq, Operations.Tier(_tier), _run.Mutators);
            var best = PlayerProfile.BestScore(_def.Id, _tier);
            var record = PlayerProfile.RecordOperation(_def.Id, _tier, score, (float)world.Time);
            outcome.Subtitle = Strings.Format("ops.resultTitle", Title, Strings.Get("tier." + _tier));
            outcome.Rows.Insert(0, (Strings.Get("ops.score"), score.ToString("N0")));
            outcome.Rows.Insert(1, (Strings.Get("ops.best"), record ? Strings.Get("ops.newRecord") : best.ToString("N0")));
            if (_run.Mutators.Count > 0)
            {
                var names = new List<string>();
                foreach (var m in _run.Mutators) names.Add(Strings.Get("mutator." + m.Id));
                outcome.Rows.Add((Strings.Get("ops.mutators"), string.Join(" · ", names)));
            }
            if (!won || !_run.Weekly || !PlayerProfile.ClaimWeekly(WeeklyFortress.Week, "operation") || outcome.Reward == null) return;
            outcome.Reward.Coins += Operations.Data.WeeklyOperationReward;
            outcome.Rows.Add((Strings.Get("ops.weekly"), Strings.Format("weekly.reward", Operations.Data.WeeklyOperationReward)));
        }

        /// <summary>A boss's name in this mission: its own ("the Frost Monster") or its def's.</summary>
        internal static string BossName(MissionDef def, string defId) =>
            def.Boss?.Name is { } name && Strings.Has("boss." + name) ? Strings.Get("boss." + name) : Strings.Card(defId);

        /// <summary>The choice dialog while a stage waits on the player's pick; the first option goes ahead by itself.</summary>
        private void ShowChoice(BattleHud hud, SimWorld world)
        {
            if (_op?.PendingChoice is not { } stage)
            {
                if (hud.ChoiceShown) hud.HideChoice();
                return;
            }
            if (!hud.ChoiceShown)
            {
                var options = new List<(string, string)>();
                foreach (var c in stage.Choices)
                {
                    var key = "choice." + _def.Id + "." + c.Key;
                    var info = Strings.Get(key + ".info");
                    options.Add((Strings.Get(key), info != key + ".info" ? info : null));
                }
                hud.ShowChoice(Strings.Get("choice.title"), options, index =>
                {
                    Choose(world, stage.Choices[index].Key);
                    hud.HideChoice();
                });
            }
            hud.SetChoiceTime(_op.ChoiceLeft(world));
        }

        public override MatchOutcome Outcome(SimWorld world, int kills, int losses)
        {
            if (Mode.Result is not { } result) return null;
            var won = result.WinningTeam == PlayerTeam;
            var outcome = new MatchOutcome { Result = won ? 1 : -1, Subtitle = Title };
            outcome.Rows.Add((Strings.Get("result.kills"), Kills.ToString()));
            outcome.Rows.Add((Strings.Get("result.losses"), Losses.ToString()));
            outcome.Rows.Add((Strings.Get("result.time"), Clock(world.Time)));
            if (_op != null && _op.StageCount > 1)
                outcome.Rows.Add((Strings.Get("result.stages"), won ? _op.Path.Count.ToString() : UnityEngine.Mathf.Max(0, _op.Path.Count - 1).ToString()));
            outcome.Reward = Rewards.Mission(_def, won, (float)world.Time, Losses, ChallengeMet(world), System.Math.Min(_tier, 2));
            if (_run != null) OperationRows(outcome, world, won);
            if (_tier > 0) outcome.Rows.Add((Strings.Get("tier.label"), Strings.Get("tier." + _tier)));
            return outcome;
        }
    }
}

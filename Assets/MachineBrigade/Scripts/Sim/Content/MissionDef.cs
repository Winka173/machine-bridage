#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What wins a campaign mission.</summary>
    public enum MissionGoal
    {
        /// <summary>Own every listed objective at the same time.</summary>
        Capture,

        /// <summary>Keep one objective for a number of seconds while the enemy attacks it.</summary>
        Hold,

        /// <summary>Destroy every prop of the listed kinds.</summary>
        Destroy,

        /// <summary>Bring enough convoy trucks along their route to its end.</summary>
        Escort,

        /// <summary>Stay alive until the clock runs out.</summary>
        Survive,

        /// <summary>Destroy the boss.</summary>
        Boss,

        /// <summary>Destroy the boss before it reaches the end of its route.</summary>
        Intercept,

        /// <summary>Hunt down marked high-value vehicles (a battery, a commander) that patrol with their guard.</summary>
        Hunt,

        /// <summary>Scout every listed objective: bring a vehicle onto each for a few seconds.</summary>
        Recon,

        /// <summary>Keep enough of the listed buildings on the player's side standing until the clock runs out.</summary>
        Protect,

        /// <summary>Shoot down enough enemy aircraft.</summary>
        ShootDown,

        /// <summary>
        /// Set up an outpost: take the first listed objective, set it up as an outpost (its towers
        /// flown in) and keep it for <see cref="MissionDef.HoldSeconds"/> once it stands.
        /// </summary>
        Outpost,

        /// <summary>
        /// Break the siege of an allied base: destroy every marked besieger before the ally's HQ
        /// (see <see cref="AllyDef.Hq"/>) falls.
        /// </summary>
        Relieve,

        /// <summary>
        /// Evacuation: the convoy's trucks leave its start one after another (the army holds the
        /// site until the last has left, then brings them out); enough must reach the route's end.
        /// </summary>
        Evacuate,

        /// <summary>A duel with a general: level the enemy base's HQ (the base must be a Target).</summary>
        Duel,
    }

    /// <summary>What sets a radio line off during a mission (the Game layer shows it; the battle is not changed).</summary>
    public enum RadioTrigger
    {
        /// <summary>As the mission starts.</summary>
        Start,

        /// <summary><see cref="RadioLineDef.Seconds"/> into the mission.</summary>
        Time,

        /// <summary>The player takes an objective (<see cref="RadioLineDef.Arg"/>: its id, or any).</summary>
        Capture,

        /// <summary>The enemy takes one of the player's objectives.</summary>
        Lost,

        /// <summary>The boss comes onto the field.</summary>
        Boss,

        /// <summary>The boss is down to half its health.</summary>
        BossHalf,

        /// <summary>The player's HQ is down to half its health.</summary>
        HqHalf,

        /// <summary>A stage begins (<see cref="RadioLineDef.Arg"/>: its id).</summary>
        Stage,

        /// <summary>The enemy calls in reinforcements.</summary>
        Reinforce,

        /// <summary>The mission is won.</summary>
        Win,

        /// <summary>The mission is lost.</summary>
        Lose,

        // Prompt 30 L2: the triggers of the sheet "Điểm kích hoạt" (keys in StoryScript.TriggerKeys).

        /// <summary>A stage ends (phase_end).</summary>
        PhaseEnd,

        /// <summary>The goal passes a mark (Arg: "1/3", "1/2", "2/3" or "last").</summary>
        ObjectiveProgress,

        /// <summary>The boss changes phase (Arg: the new phase's number).</summary>
        BossPhase,

        /// <summary>A part of the boss that matters breaks (Arg: the part id, or any).</summary>
        BossPart,

        /// <summary>The boss passes a health mark (Arg: "75", "50" or "25"); skipped within 10 s of a phase change.</summary>
        BossHp,

        /// <summary>The first warning of a superweapon in the battle: the line that says how to get clear.</summary>
        Superweapon,

        /// <summary>The enemy general changes tactic and a scout sees it.</summary>
        TacticChange,

        /// <summary>The first loss of a vehicle of base CP 15 or more (at most twice a mission).</summary>
        ExpensiveLost,

        /// <summary>A kind of enemy vehicle seen for the first time (Arg: its id).</summary>
        FirstSeen,

        /// <summary>About to lose: one convoy truck left, the protected building nearly down, the HQ critical.</summary>
        Critical,

        /// <summary>The player clearly holds the battle (once).</summary>
        Momentum,

        /// <summary>An ally arrives.</summary>
        AllyArrives,

        /// <summary>An ally is late (before chapter 7 only).</summary>
        AllyLate,

        /// <summary>A neutral site is taken (Arg: its kind).</summary>
        NeutralCaptured,

        /// <summary>A mission event begins (Arg: its kind).</summary>
        EventTriggered,

        /// <summary>90 s with no progress on the goal and no P0-P2 line (at most once).</summary>
        ObjectiveStall,

        /// <summary>60 s left on a timed mission.</summary>
        Timer60,
    }

    /// <summary>One radio line of a mission: when it plays and its text key ("radio.&lt;speaker&gt;.&lt;line&gt;").</summary>
    public sealed class RadioLineDef
    {
        public RadioTrigger On { get; set; }
        public double Seconds { get; set; }
        public string? Arg { get; set; }
        public string Key { get; set; } = "";
    }

    /// <summary>Enemy vehicles arriving on a schedule.</summary>
    public sealed class WaveDef
    {
        public float First { get; set; } = 30f;
        public float Interval { get; set; } = 40f;
        public int Size { get; set; } = 3;

        /// <summary>Extra vehicles per wave after the first.</summary>
        public float Grow { get; set; } = 0.5f;

        public int MaxSize { get; set; } = 8;

        /// <summary>No new wave while this many enemies are already alive.</summary>
        public int MaxAlive { get; set; } = 18;

        public IReadOnlyList<string> Roster { get; set; } = Array.Empty<string>();

        /// <summary>Where waves appear; empty: the enemy camp.</summary>
        public IReadOnlyList<Vector2> Spawns { get; set; } = Array.Empty<Vector2>();
    }

    public sealed class ScriptedUnitDef
    {
        public string Def { get; set; } = "";
        public Vector2 Position { get; set; }
        public float Heading { get; set; }

        /// <summary>Waypoints it drives along (convoys, the armoured train); empty: the AI commands it.</summary>
        public IReadOnlyList<Vector2> Route { get; set; } = Array.Empty<Vector2>();

        /// <summary>Its health against its def's (a weakened Bastion, a boss in its complete form).</summary>
        public float Health { get; set; } = 1f;

        /// <summary>A boss that flees (the fight is won) once its health falls to this share (0: it fights to the end).</summary>
        public float FleeAt { get; set; }

        /// <summary>The name it goes by in this mission (a text key "boss.&lt;name&gt;"; null: its def's).</summary>
        public string? Name { get; set; }

        /// <summary>
        /// The def to field while <see cref="Def"/> is not in the catalog yet (a boss still being
        /// modelled), at <see cref="FallbackHealth"/>; null: none.
        /// </summary>
        public string? Fallback { get; set; }

        public float FallbackHealth { get; set; } = 1f;

        /// <summary>The def fielded in this catalog, and its health share.</summary>
        public (string def, float health) Resolve(Catalog catalog) =>
            Fallback != null && !catalog.Vehicles.ContainsKey(Def) ? (Fallback, FallbackHealth) : (Def, Health);
    }

    /// <summary>One campaign mission, read from campaign.json.</summary>
    /// <summary>
    /// A stage of a multi-stage mission (see Modes.OperationMode): its goal is a mission of its own
    /// (the stage's fields laid over the mission's), what it pays on completion, what happens at its
    /// start, end and on its clock, where it leads (the next stage, or a choice of two).
    /// </summary>
    public sealed class StageDef
    {
        public string Id { get; set; } = "";
        public MissionDef Mission { get; set; } = null!;

        /// <summary>CP paid to the player when the stage is done.</summary>
        public int Cp { get; set; }

        public IReadOnlyList<StageEventDef> Events { get; set; } = Array.Empty<StageEventDef>();

        /// <summary>The stage that follows (null: the next in the list).</summary>
        public string? Next { get; set; }

        /// <summary>A branching point: the player picks one (the first after a while if nobody does).</summary>
        public IReadOnlyList<StageChoiceDef> Choices { get; set; } = Array.Empty<StageChoiceDef>();

        /// <summary>A checkpoint is kept at its end.</summary>
        public bool Checkpoint { get; set; } = true;
    }

    /// <summary>When a stage event happens.</summary>
    public enum StageMoment
    {
        Start,
        End,

        /// <summary><see cref="StageEventDef.Seconds"/> into the stage.</summary>
        Time,
    }

    /// <summary>What a stage event does.</summary>
    public enum StageEventKind
    {
        /// <summary>Units flown in for a side (Team) near Position (default: its drop zone).</summary>
        Reinforce,

        /// <summary>Units flown in for the ally near its site.</summary>
        AllyReinforce,

        /// <summary>The battlefield grows into its outer area (Expansion: the map's expansion id).</summary>
        Expand,

        /// <summary>The ally changes sides: its units and structures join the enemy.</summary>
        Betrayal,

        /// <summary>A radio message (Key: the text).</summary>
        Radio,

        /// <summary>CP for a side.</summary>
        Cp,

        /// <summary>
        /// Fire support for a side (Team) at no cost: Support at Position, else on the other side's
        /// biggest group; with <see cref="StageEventDef.Every"/> it comes again on that interval for
        /// the rest of the mission (allied air strikes opened by a choice).
        /// </summary>
        Strike,

        /// <summary>A side's income is scaled by Amount from now on (the enemy weakened by a blown depot).</summary>
        Income,
    }

    public sealed class StageEventDef
    {
        public StageMoment At { get; set; }
        public double Seconds { get; set; }
        public StageEventKind Kind { get; set; }
        public int Team { get; set; } = 1;
        public IReadOnlyList<string> Units { get; set; } = Array.Empty<string>();
        public Vector2? Position { get; set; }
        public string? Key { get; set; }

        /// <summary>Expand: the play area from now on.</summary>
        public PlayArea? Area { get; set; }

        public float Amount { get; set; }

        /// <summary>Strike: the support called.</summary>
        public string? Support { get; set; }

        /// <summary>Strike: seconds between repeats (0: once).</summary>
        public double Every { get; set; }
    }

    /// <summary>
    /// The part of the map the player's side may go into (a multi-stage mission opens the rest as
    /// it goes): a rectangle, in metres.
    /// </summary>
    public readonly struct PlayArea
    {
        public PlayArea(Vector2 min, Vector2 max)
        {
            Min = Vector2.Min(min, max);
            Max = Vector2.Max(min, max);
        }

        public Vector2 Min { get; }
        public Vector2 Max { get; }

        public bool Contains(Vector2 p) => p.X >= Min.X && p.X <= Max.X && p.Y >= Min.Y && p.Y <= Max.Y;

        public Vector2 Clamp(Vector2 p) => Vector2.Clamp(p, Min, Max);

        internal static PlayArea? Read(JsonObject o, string key)
        {
            if (!o.Has(key)) return null;
            var a = o.Object(key);
            return new PlayArea(new Vector2(a.Float("minX"), a.Float("minZ")), new Vector2(a.Float("maxX"), a.Float("maxZ")));
        }
    }

    public sealed class StageChoiceDef
    {
        public string Key { get; set; } = "";
        public string Next { get; set; } = "";
    }

    /// <summary>
    /// An allied commander (a multi-stage mission): its own camp (Site) and units on the player's
    /// side, commanded by its own AI; reinforcements flown in on a schedule; it may change sides.
    /// </summary>
    public sealed class AllyDef
    {
        public Vector2 Site { get; set; }
        public float Heading { get; set; }
        public IReadOnlyList<UnitPlacement> Units { get; set; } = Array.Empty<UnitPlacement>();
        public IReadOnlyList<(double at, IReadOnlyList<string> units)> Reinforcements { get; set; } = Array.Empty<(double, IReadOnlyList<string>)>();

        /// <summary>The ally's own HQ at its site (the defector's base when it changes sides).</summary>
        public string? Hq { get; set; }

        /// <summary>The ally's towers and other structures round its site (they change sides with it).</summary>
        public IReadOnlyList<UnitPlacement> Structures { get; set; } = Array.Empty<UnitPlacement>();
    }

    public sealed class MissionDef
    {
        public string Id { get; set; } = "";

        /// <summary>The stages of a multi-stage mission, in order (empty: a mission of one goal).</summary>
        public IReadOnlyList<StageDef> Stages { get; set; } = Array.Empty<StageDef>();

        /// <summary>The allied commander, if the mission has one.</summary>
        public AllyDef? Ally { get; set; }

        /// <summary>Most enemy vehicles on the field at once (0: the usual cap). Large battles raise it.</summary>
        public int EnemyCap { get; set; }

        /// <summary>Where the player's side may go at the start (null: the whole map).</summary>
        public PlayArea? PlayArea { get; set; }

        /// <summary>
        /// Prompt 22 E: a duel (chapter 10's Hawk and Raven): the mission's boss flies in its duel mode (BossSystem.Duel), and
        /// the player's deck is its aircraft only (<see cref="PlayerDeck"/> "air").
        /// </summary>
        public bool Duel { get; set; }

        /// <summary>Prompt 22 E: what the player's deck is cut to for this mission: "air" (its aircraft only), or null (the deck as it is).</summary>
        public string? PlayerDeck { get; set; }

        /// <summary>Prompt 31 L1: the deck the game hands out (campaign.json "fixedDeck"); null: the player's own.</summary>
        public FixedDeckDef? FixedDeck { get; set; }

        /// <summary>Prompt 31 L3: the mission's prebuilt ground states (campaign.json "navStates"), built as the battle loads.</summary>
        public IReadOnlyList<Navigation.NavSiteDef> NavSites { get; set; } = Array.Empty<Navigation.NavSiteDef>();

        /// <summary>A chapter's big operation: the Operations mode offers it again once won.</summary>
        public bool Operation { get; set; }

        /// <summary>A notable story battle (a siege, a defence, a duel with a general) the Operations mode offers again once won.</summary>
        public bool Replay { get; set; }

        /// <summary>
        /// Prompt 22 D.5: the story choice offered once this mission is won (its id, "c4.pursuit"), or null. The
        /// choice's options are the missions that name it as their <see cref="Branch"/>.
        /// </summary>
        public string? StoryChoice { get; set; }

        /// <summary>Prompt 22 D.5: a mission of one option of a story choice (the choice's id; null: on every path).</summary>
        public string? Branch { get; set; }

        /// <summary>Prompt 22 D.5: which option of <see cref="Branch"/> this mission is ("sea", "harbour").</summary>
        public string? Option { get; set; }

        public string Map { get; set; } = "ashfield";

        /// <summary>Which version of the map: "conquest" (objectives) or "sandbox".</summary>
        public string Variant { get; set; } = "conquest";

        public string Weather { get; set; } = "Clear";
        public MissionGoal Goal { get; set; }

        /// <summary>Capture: the objectives to own; Hold: the first one is held.</summary>
        public IReadOnlyList<string> Points { get; set; } = Array.Empty<string>();

        /// <summary>Objectives the enemy owns when the mission starts.</summary>
        public IReadOnlyList<string> EnemyOwns { get; set; } = Array.Empty<string>();

        public float HoldSeconds { get; set; } = 180f;

        /// <summary>Destroy: the kinds of building to knock down. Protect: the kinds to keep standing (those on the player's side).</summary>
        public IReadOnlyList<string> Targets { get; set; } = Array.Empty<string>();

        /// <summary>Protect: the mission is lost when fewer than this many are left standing.</summary>
        public int ProtectNeeded { get; set; } = 1;

        /// <summary>Hunt: the marked vehicles, each on its patrol route (driven round and round).</summary>
        public IReadOnlyList<ScriptedUnitDef> Hunt { get; set; } = Array.Empty<ScriptedUnitDef>();

        /// <summary>ShootDown: enemy aircraft to bring down.</summary>
        public int KillsNeeded { get; set; } = 10;
        public float SurviveSeconds { get; set; } = 300f;

        /// <summary>Seconds before the mission is lost (0: no limit).</summary>
        public float TimeLimit { get; set; }

        /// <summary>
        /// Intercept: once the boss reaches the end of its route it prepares to launch, and the
        /// mission is lost after this many seconds (0: lost the moment it arrives).
        /// </summary>
        public float LaunchSeconds { get; set; }

        public ScriptedUnitDef? Boss { get; set; }

        /// <summary>Convoy trucks, spawned one after another along the route.</summary>
        public ScriptedUnitDef? Convoy { get; set; }

        public int ConvoyCount { get; set; } = 4;
        public int ConvoyNeeded { get; set; } = 2;

        /// <summary>"commander" (an enemy that buys and fights for objectives), "waves", "both" or "none".</summary>
        public string EnemyAi { get; set; } = "commander";

        public string EnemyStance { get; set; } = "Attack";
        public string Difficulty { get; set; } = "Normal";
        public float EnemyCp { get; set; } = 14f;
        public float EnemyIncome { get; set; } = 1f;
        public IReadOnlyList<string> EnemyDeck { get; set; } = Array.Empty<string>();
        public WaveDef? Waves { get; set; }

        /// <summary>
        /// How many times the enemy calls for help when it is losing (see <see cref="Modes.MissionMode"/>),
        /// and how many vehicles come the first time (one more each time after).
        /// </summary>
        public int Reinforcements { get; set; } = 3;

        public int ReinforceSize { get; set; } = 3;

        public float PlayerCp { get; set; } = 16f;
        public float PlayerIncome { get; set; } = 1f;

        /// <summary>
        /// The player's army cap. Above Conquest's 24: the enemy brings waves on top of its own
        /// commander, and units placed at the start count against the cap too.
        /// </summary>
        public int PlayerCap { get; set; } = 30;

        /// <summary>Demolition targets are this many times tougher than the same building elsewhere.</summary>
        public float TargetHealth { get; set; } = 1f;

        /// <summary>Extra units on the map when the mission starts (on top of the map's own).</summary>
        public IReadOnlyList<UnitPlacement> Units { get; set; } = Array.Empty<UnitPlacement>();

        public int RewardCoins { get; set; } = 200;
        public int RewardXp { get; set; } = 150;
        public IReadOnlyList<string> Unlocks { get; set; } = Array.Empty<string>();

        /// <summary>Hints shown during the mission: (seconds in, localisation key). The tutorial talks the player through.</summary>
        public IReadOnlyList<(float at, string key)> Tips { get; set; } = Array.Empty<(float, string)>();

        /// <summary>An optional mission (the tutorial): the next one does not wait for it.</summary>
        public bool Optional { get; set; }

        /// <summary>A chapter's epilogue (prompt 16: Leviathan after chapter 4's operation): a main mission after the operation.</summary>
        public bool Epilogue { get; set; }

        /// <summary>Second star: won within this many seconds (0: always).</summary>
        public float StarTime { get; set; }

        /// <summary>Third star: won losing at most this many vehicles (negative: always).</summary>
        public int StarLosses { get; set; } = -1;

        /// <summary>Capture points the player can set up as outposts once taken (hardpoints for towers, a second drop zone).</summary>
        public IReadOnlyList<string> Outposts { get; set; } = Array.Empty<string>();

        /// <summary>The player's base in this mission (None: no camp, the default), and the enemy's.</summary>
        public BaseRole PlayerBase { get; set; } = BaseRole.None;
        public BaseRole EnemyBase { get; set; } = BaseRole.None;

        /// <summary>
        /// The mission's own third star, instead of the losses rule: "NoStrikes" (no fire support
        /// called), "NoAircraft" (no aircraft bought), "Kills" (at least <see cref="ChallengeValue"/>
        /// enemy vehicles destroyed); null keeps <see cref="StarLosses"/>.
        /// </summary>
        public string? Challenge { get; set; }

        public int ChallengeValue { get; set; }

        // ------------------------------------------------------------------ the story campaign

        /// <summary>The campaign chapter (1-9; 0 outside the chapters).</summary>
        public int Chapter { get; set; }

        /// <summary>A side mission: optional, opened by <see cref="After"/>, paying rare blueprints or tower equipment.</summary>
        public bool Side { get; set; }

        /// <summary>A side mission: the main mission whose first win opens it.</summary>
        public string? After { get; set; }

        /// <summary>The sides swap camps: the player starts from the enemy's usual corner (a return to a map taken earlier).</summary>
        public bool Reversed { get; set; }

        /// <summary>The enemy general in command (balance of the enemy's deck, fire support and base; their portrait and lines).</summary>
        public string? General { get; set; }

        /// <summary>
        /// Prompt 22 F: the commander the story sets for this mission (chapter 10's duel is Hawk's); null: the player
        /// picks one. campaign.json "commander".
        /// </summary>
        public string? Commander { get; set; }

        /// <summary>Who gives the briefing (a portrait id): the colonel, unless the mission says otherwise.</summary>
        public string Speaker { get; set; } = "khai";

        /// <summary>The fire support the enemy commander calls (empty: every support that is not premium).</summary>
        public IReadOnlyList<string> EnemySupports { get; set; } = Array.Empty<string>();

        /// <summary>The enemy base's style (balance.json base.ai.styles; null: the general's, else "default").</summary>
        public string? EnemyStyle { get; set; }

        /// <summary>The enemy base's HQ level (0: by difficulty).</summary>
        public int EnemyHq { get; set; }

        /// <summary>Seconds between two convoy trucks leaving (an evacuation spaces them out more).</summary>
        public float ConvoyInterval { get; set; } = 4f;

        /// <summary>Radio lines this mission plays, by what sets them off.</summary>
        public IReadOnlyList<RadioLineDef> Radio { get; set; } = Array.Empty<RadioLineDef>();

        /// <summary>The HQ level the first win opens (0: none).</summary>
        public int HqLevel { get; set; }

        /// <summary>Blueprints the first win pays for the cards of the player's main deck (a third on a replay).</summary>
        public int Prints { get; set; }

        /// <summary>Universal blueprints the first win pays (side missions: rare blueprints).</summary>
        public int RarePrints { get; set; }

        /// <summary>A piece of tower equipment of this rarity the first win pays (side missions; null: none).</summary>
        public string? TowerGear { get; set; }

        /// <summary>The mission of the old campaign this one grew out of (its stars move here with a saved game).</summary>
        public string? Legacy { get; set; }


        /// <summary>Destroy and Protect: only the buildings within <see cref="TargetRadius"/> of this spot count (null: all of them).</summary>
        public Vector2? TargetNear { get; set; }

        public float TargetRadius { get; set; } = 40f;

        /// <summary>
        /// Prompt 23 A: the events this mission (or stage) plays, resolved from the library (campaign.json "missionEvents":
        /// library ids, or objects naming one with overrides). A staged mission's own run over the whole operation; a
        /// stage's own over that stage.
        /// </summary>
        public IReadOnlyList<MissionEventDef> Events { get; set; } = Array.Empty<MissionEventDef>();

        /// <summary>The library's rules the events read (the C.3 table, the generals, the caps).</summary>
        public EventRules EventRules { get; set; } = EventRules.Default;

        /// <summary>
        /// A harder copy of the mission (the Heroic and Iron tiers): the enemy starts with more
        /// CP, earns more and sends bigger waves. The mission itself is left as it is.
        /// </summary>
        public MissionDef Harder(float enemy)
        {
            var copy = (MissionDef)MemberwiseClone();
            if (Stages.Count > 0)
            {
                var stages = new List<StageDef>();
                foreach (var s in Stages)
                    stages.Add(new StageDef
                    {
                        Id = s.Id, Mission = s.Mission.Harder(enemy), Cp = s.Cp, Events = s.Events, Next = s.Next,
                        Choices = s.Choices, Checkpoint = s.Checkpoint,
                    });
                copy.Stages = stages;
            }
            copy.EnemyCp = EnemyCp * enemy;
            copy.EnemyIncome = EnemyIncome * (1f + (enemy - 1f) * 0.8f);
            copy.Reinforcements = Reinforcements + 1;
            copy.ReinforceSize = (int)Math.Ceiling(ReinforceSize * enemy);
            if (Waves != null)
                copy.Waves = new WaveDef
                {
                    First = Waves.First, Interval = Waves.Interval, Size = (int)Math.Ceiling(Waves.Size * enemy), Grow = Waves.Grow * enemy,
                    MaxSize = (int)Math.Ceiling(Waves.MaxSize * enemy), MaxAlive = (int)Math.Ceiling(Waves.MaxAlive * enemy),
                    // The waves stay what they were (they were lost here: a harder tier's waves never came).
                    Roster = Waves.Roster, Spawns = Waves.Spawns,
                };
            return copy;
        }

        public static IReadOnlyList<MissionDef> ListFromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            // Prompt 23 A: the event library first; the missions' events are resolved against it.
            var library = root.Has("eventLibrary") ? EventLibrary.Parse(root.Object("eventLibrary")) : new EventLibrary();
            var missions = new List<MissionDef>();
            foreach (var m in root.Array("missions")) missions.Add(Parse(m, library));
            return missions;
        }

        private static MissionDef Parse(JsonObject m, EventLibrary library)
        {
            var def = new MissionDef
            {
                Id = m.String("id"),
                Map = m.String("map"),
                Variant = m.Has("variant") ? m.String("variant") : "conquest",
                Weather = m.Has("weather") ? m.String("weather") : "Clear",
                Goal = m.Enum<MissionGoal>("goal"),
                Points = Strings(m, "points"),
                EnemyOwns = Strings(m, "enemyOwns"),
                HoldSeconds = m.Float("holdSeconds", 180f),
                Targets = Strings(m, "targets"),
                ProtectNeeded = m.Int("protectNeeded", 1),
                KillsNeeded = m.Int("killsNeeded", 10),
                SurviveSeconds = m.Float("surviveSeconds", 300f),
                TimeLimit = m.Float("timeLimit", 0f),
                ConvoyCount = m.Int("convoyCount", 4),
                ConvoyNeeded = m.Int("convoyNeeded", 2),
                LaunchSeconds = m.Float("launchSeconds", 0f),
                EnemyAi = m.Has("enemyAi") ? m.String("enemyAi") : "commander",
                EnemyStance = m.Has("enemyStance") ? m.String("enemyStance") : "Attack",
                Difficulty = m.Has("difficulty") ? m.String("difficulty") : "Normal",
                EnemyCp = m.Float("enemyCp", 14f),
                EnemyIncome = m.Float("enemyIncome", 1f),
                EnemyDeck = Strings(m, "enemyDeck"),
                Reinforcements = m.Int("reinforcements", 3),
                ReinforceSize = m.Int("reinforceSize", 3),
                PlayerCp = m.Float("playerCp", 16f),
                PlayerIncome = m.Float("playerIncome", 1f),
                PlayerCap = (int)m.Float("playerCap", 30f),
                TargetHealth = m.Float("targetHealth", 1f),
                RewardCoins = m.Int("coins", 200),
                RewardXp = m.Int("xp", 150),
                Unlocks = Strings(m, "unlocks"),
                Tips = ParseTips(m),
                Optional = m.Bool("optional", false),
                Epilogue = m.Bool("epilogue", false),
                StarTime = m.Float("starTime", 0f),
                StarLosses = m.Int("starLosses", -1),
                Outposts = Strings(m, "outposts"),
                PlayerBase = m.Enum("playerBase", BaseRole.None),
                EnemyBase = m.Enum("enemyBase", BaseRole.None),
                Chapter = m.Int("chapter", 0),
                Side = m.Bool("side", false),
                After = m.Has("after") ? m.String("after") : null,
                Reversed = m.Bool("reversed", false),
                General = m.Has("general") ? m.String("general") : null,
                Commander = m.Has("commander") ? m.String("commander") : null,
                Speaker = m.Has("speaker") ? m.String("speaker") : "khai",
                EnemySupports = Strings(m, "enemySupports"),
                EnemyStyle = m.Has("enemyStyle") ? m.String("enemyStyle") : null,
                EnemyHq = m.Int("enemyHq", 0),
                ConvoyInterval = m.Float("convoyInterval", 4f),
                HqLevel = m.Int("hqLevel", 0),
                Prints = m.Int("prints", 0),
                RarePrints = m.Int("rarePrints", 0),
                TowerGear = m.Has("towerGear") ? m.String("towerGear") : null,
                Radio = ParseRadio(m),
                Legacy = m.Has("legacy") ? m.String("legacy") : null,
                Operation = m.Bool("operation", false),
                Duel = m.Bool("duel", false),
                PlayerDeck = m.Has("playerDeck") ? m.String("playerDeck") : m.Bool("duel", false) ? "air" : null,
                Replay = m.Bool("replay", false),
                StoryChoice = m.Has("storyChoice") ? m.String("storyChoice") : null,
                Branch = m.Has("branch") ? m.String("branch") : null,
                Option = m.Has("option") ? m.String("option") : null,
                TargetNear = m.Has("targetX") ? new Vector2(m.Float("targetX"), m.Float("targetZ")) : null,
                TargetRadius = m.Float("targetRadius", 40f),
            };
            def.EventRules = library.Rules;
            // A plan change's new goal is the mission's fields with the plan's on top (what it fights is the plan's own).
            if (m.Has("missionEvents"))
                def.Events = library.Resolve(m, "missionEvents", plan => Parse(Bare(m).Under(plan), library));
            if (m.Has("fixedDeck")) def.FixedDeck = FixedDeckDef.Parse(m.Object("fixedDeck"));
            if (m.Has("navStates")) def.NavSites = NavSiteDefs.Parse(m, "navStates");
            if (m.Has("challenge"))
            {
                var c = m.Object("challenge");
                def.Challenge = c.String("kind");
                def.ChallengeValue = c.Int("value", 0);
            }
            if (m.Has("boss")) def.Boss = Scripted(m.Object("boss"));
            if (m.Has("hunt"))
            {
                var hunt = new List<ScriptedUnitDef>();
                foreach (var h in m.Array("hunt")) hunt.Add(Scripted(h));
                def.Hunt = hunt;
            }
            if (m.Has("convoy")) def.Convoy = Scripted(m.Object("convoy"));
            if (m.Has("waves"))
            {
                var w = m.Object("waves");
                def.Waves = new WaveDef
                {
                    First = w.Float("first", 30f),
                    Interval = w.Float("interval", 40f),
                    Size = w.Int("size", 3),
                    Grow = w.Float("grow", 0.5f),
                    MaxSize = w.Int("maxSize", 8),
                    MaxAlive = w.Int("maxAlive", 18),
                    Roster = Strings(w, "roster"),
                    Spawns = w.Has("spawns") ? Points2(w.FloatArray("spawns")) : Array.Empty<Vector2>(),
                };
            }
            if (m.Has("units")) def.Units = Placements(m, "units");
            def.EnemyCap = m.Int("enemyCap", 0);
            def.PlayArea = Content.PlayArea.Read(m, "playArea");
            if (m.Has("ally"))
            {
                var a = m.Object("ally");
                var reinforcements = new List<(double, IReadOnlyList<string>)>();
                foreach (var r in a.Array("reinforcements")) reinforcements.Add((r.Float("at"), Strings(r, "units")));
                def.Ally = new AllyDef
                {
                    Site = new Vector2(a.Float("x"), a.Float("z")), Heading = SimMath.DegToRad(a.Float("heading", 0f)),
                    Units = a.Has("units") ? Placements(a, "units") : Array.Empty<UnitPlacement>(),
                    Reinforcements = reinforcements, Hq = a.Has("hq") ? a.String("hq") : null,
                    Structures = a.Has("structures") ? Placements(a, "structures") : Array.Empty<UnitPlacement>(),
                };
            }
            // Stages: each is a mission of its own, its fields laid over the mission's ("stage" names it).
            // What a stage fights (its units, boss, hunted vehicles, convoy, waves) is its own; the
            // mission's units are placed once, at the start.
            if (m.Has("stages"))
            {
                var parent = Bare(m).With("tips", null).With("ally", null).With("radio", null);
                var stages = new List<StageDef>();
                foreach (var s in m.Array("stages"))
                {
                    var stage = new StageDef
                    {
                        Id = s.Has("stage") ? s.String("stage") : "s" + (stages.Count + 1),
                        Mission = Parse(parent.Under(s), library),
                        Cp = s.Int("cp", 0),
                        Next = s.Has("next") ? s.String("next") : null,
                        Checkpoint = s.Bool("checkpoint", true),
                    };
                    var events = new List<StageEventDef>();
                    foreach (var e in s.Array("events"))
                    {
                        var at = e.Has("at") ? e.String("at") : "start";
                        var timed = double.TryParse(at, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var seconds);
                        events.Add(new StageEventDef
                        {
                            At = timed ? StageMoment.Time : (StageMoment)Enum.Parse(typeof(StageMoment), at, true),
                            Seconds = timed ? seconds : 0.0,
                            Kind = e.Enum<StageEventKind>("kind"),
                            Team = e.Int("team", 1),
                            Units = Strings(e, "units"),
                            Position = e.Has("x") ? new Vector2(e.Float("x"), e.Float("z")) : null,
                            Key = e.Has("key") ? e.String("key") : null,
                            Area = Content.PlayArea.Read(e, "area"),
                            Amount = e.Float("amount", 0f),
                            Support = e.Has("support") ? e.String("support") : null,
                            Every = e.Float("every", 0f),
                        });
                    }
                    stage.Events = events;
                    var choices = new List<StageChoiceDef>();
                    foreach (var c in s.Array("choices")) choices.Add(new StageChoiceDef { Key = c.String("key"), Next = c.String("next") });
                    stage.Choices = choices;
                    stages.Add(stage);
                }
                def.Stages = stages;
            }
            return def;
        }

        /// <summary>A mission's fields without what it fights and its events (a stage's or a new plan's base).</summary>
        private static JsonObject Bare(JsonObject m) =>
            m.With("stages", null).With("units", null).With("boss", null).With("hunt", null).With("convoy", null).With("waves", null)
                .With("missionEvents", null);

        private static IReadOnlyList<UnitPlacement> Placements(JsonObject m, string key)
        {
            var units = new List<UnitPlacement>();
            foreach (var u in m.Array(key))
                units.Add(new UnitPlacement(u.String("def"), u.Int("team", 0), new Vector2(u.Float("x"), u.Float("z")),
                    SimMath.DegToRad(u.Float("heading", 0f))));
            return units;
        }

        private static ScriptedUnitDef Scripted(JsonObject o) => new()
        {
            Def = o.String("def"),
            Position = new Vector2(o.Float("x"), o.Float("z")),
            Heading = SimMath.DegToRad(o.Float("heading", 0f)),
            Route = o.Has("route") ? Points2(o.FloatArray("route")) : Array.Empty<Vector2>(),
            Health = o.Float("health", 1f),
            FleeAt = o.Float("fleeAt", 0f),
            Name = o.Has("name") ? o.String("name") : null,
            Fallback = o.Has("fallback") ? o.String("fallback") : null,
            FallbackHealth = o.Float("fallbackHealth", o.Float("health", 1f)),
        };

        /// <summary>Radio lines: "on" a trigger (start, capture, boss...) or "at" a number of seconds.</summary>
        private static IReadOnlyList<RadioLineDef> ParseRadio(JsonObject m)
        {
            if (!m.Has("radio")) return Array.Empty<RadioLineDef>();
            var lines = new List<RadioLineDef>();
            foreach (var r in m.Array("radio"))
                lines.Add(new RadioLineDef
                {
                    On = r.Has("at") ? RadioTrigger.Time : r.Enum<RadioTrigger>("on"),
                    Seconds = r.Float("at", 0f),
                    Arg = r.Has("arg") ? r.String("arg") : null,
                    Key = r.String("key"),
                });
            return lines;
        }

        private static IReadOnlyList<(float, string)> ParseTips(JsonObject m)
        {
            if (!m.Has("tips")) return Array.Empty<(float, string)>();
            var tips = new List<(float, string)>();
            foreach (var t in m.Array("tips")) tips.Add((t.Float("at"), t.String("key")));
            return tips;
        }

        private static IReadOnlyList<string> Strings(JsonObject o, string key)
        {
            if (!o.Has(key)) return Array.Empty<string>();
            var list = new List<string>();
            foreach (var s in o.StringArray(key)) list.Add(s);
            return list;
        }

        private static IReadOnlyList<Vector2> Points2(IReadOnlyList<float> flat)
        {
            var list = new List<Vector2>();
            for (var i = 0; i + 1 < flat.Count; i += 2) list.Add(new Vector2(flat[i], flat[i + 1]));
            return list;
        }
    }
}

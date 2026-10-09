#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 23 A: what a mission event does (the library's "kind").</summary>
    public enum MissionEventKind
    {
        /// <summary>C.1: enemy reinforcements from several directions, made up by the mission's general.</summary>
        EnemyWave,

        /// <summary>C.2: Meridian Accord reinforcements under the allied AI (never cards), a share of an enemy wave's strength.</summary>
        AllyWave,

        /// <summary>D.1: enemy guns walking a warned barrage over one zone (the player's biggest group).</summary>
        Barrage,

        /// <summary>D.1: the surprise bomber raid of the quick modes, called by the enemy on the player's biggest group.</summary>
        AirRaid,

        /// <summary>D.1: counter-battery fire on a player's gun that stands firing too long in one place.</summary>
        CounterBattery,

        /// <summary>D.1: Hawk calls an allied air strike.</summary>
        AllyAirStrike,

        /// <summary>D.1: Accord artillery fires in support on the script's cue.</summary>
        AllyArtillery,

        /// <summary>D.2: the mission's general takes the field in an elite or a mini boss of their own, with escorts and their passive.</summary>
        GeneralField,

        /// <summary>D.3: a timed side objective (intercept a convoy, rescue one, protect one); optional, never lost for.</summary>
        SideObjective,

        /// <summary>D.4: a neutral supply convoy crosses the map; the side that knocks a truck out gets CP.</summary>
        NeutralConvoy,

        /// <summary>D.4: a loot crate parachuted into the middle: the side that holds it gets CP or a repair.</summary>
        LootDrop,

        /// <summary>D.4: an enemy group goes for the player's CP supply station or depot.</summary>
        SupplyRaid,

        /// <summary>D.5: an allied supply drop: repair and rearm for the player's units in a zone.</summary>
        SupplyDrop,

        /// <summary>D.6: Nadia reports: a zone with enemies in it is revealed for a few seconds.</summary>
        IntelReveal,

        /// <summary>D.6: an electronic-warfare storm: the player's minimap and radar go dark for a while, with a countdown.</summary>
        Blackout,

        /// <summary>D.7: a mini boss comes in at a stage of the mission (prompt 20's rules).</summary>
        MiniBoss,

        /// <summary>D.8: Kade changes the plan: a new objective (a stage of an operation, or a new goal for a mission of one).</summary>
        PlanChange,

        /// <summary>D.9: the weather or the time of day turns over 20-30 s (the existing weather and night factors).</summary>
        WeatherShift,

        /// <summary>
        /// E.1 (chapter 6, the Hollow Dam): a ceasefire on a clock. The general's sworn column holds its fire and no weapon of
        /// ours picks it on its own; the side that fires first loses its reward; when the clock runs out both fight again.
        /// </summary>
        Ceasefire,

        /// <summary>
        /// E.1 (chapter 11, Skygate): the satellite test-fires one small tungsten rod on the player's biggest group, warned as
        /// prompt 18's big attacks are (a notice and a line, then a ring on the ground), kinetic from above.
        /// </summary>
        OrbitalStrike,

        /// <summary>
        /// Prompt 31 L3: the ground changes (a factory gate shuts, and later a shoal, a bridge, a crane): a prebuilt ground state
        /// of the mission ("navSite", "navState") comes in at a tick boundary after an 8-12 s warning with the place on the
        /// minimap. Never traps a vehicle and always leaves a way round (NavStates' load-time check).
        /// </summary>
        GroundChange,

        /// <summary>Prompt 31 L3: the wind turns and the sandstorm rolls over one half of the map: sight falls there (the other half may clear).</summary>
        SandstormTurn,

        /// <summary>Prompt 31 L3: the city's power fails: the street lights go out (night falls) and the towers on the grid shut down, both sides'.</summary>
        CityBlackout,

        /// <summary>Prompt 31 L3: the warning before an ally turns (chapter 7, Thorne): his columns are marked on the minimap 8-12 s ahead.</summary>
        BetrayalWarning,

        /// <summary>Prompt 31 L3: Daedalus drops pods that stand up as new enemy structures on prebuilt ground (its "sites").</summary>
        OrbitalPods,

        /// <summary>
        /// Prompt 31 L5: a frozen lake's ice (a circle, "x", "z", "radius") cracks under a vehicle that breaks ice (its weight
        /// class, never its CP) once it has been on it "seconds" (10): slowed by "slow" for "slowFor" seconds, again and again.
        /// </summary>
        IceCrack,

        /// <summary>
        /// Prompt 31 L5: a forest fire driven by the wind over the prebuilt strips of its site ("navSite": each state after the
        /// initial one a burning strip, the last one empty, burnt out), one strip every "every" seconds: the strip burning is
        /// closed ground, vehicles caught on it burn ("dps" for "burn" seconds) and are put out of it, its smoke drifts downwind.
        /// </summary>
        ForestFire,
    }

    /// <summary>The C.3 difficulty an event plays at: the mission's own, one step up per tier (Heroic, Iron).</summary>
    public enum EventLevel
    {
        Easy,
        Normal,
        Hard,
        VeryHard,
    }

    /// <summary>
    /// Prompt 23 H.3: how much a line or notice matters, for the in-battle text system (lower is more important). A low
    /// line is dropped when a higher one is showing; Story and Warning lines queue.
    /// </summary>
    public enum LinePriority
    {
        Story = 0,
        Warning = 1,
        Event = 2,
        Reaction = 3,
    }

    /// <summary>
    /// When an event happens (A.1). Every condition given must hold (a time and a progress mark both); <see cref="Delay"/>
    /// seconds later it starts (its warning first, when it has one). <see cref="Every"/> repeats it up to <see cref="Times"/>.
    /// </summary>
    public sealed class EventTrigger
    {
        /// <summary>Seconds into the mission (a stage's own events: into the stage).</summary>
        public double? At { get; set; }

        /// <summary>The mission's progress has reached this share (0 to 1).</summary>
        public float? Progress { get; set; }

        /// <summary>The mission's boss is down to this share of its health.</summary>
        public float? BossHealth { get; set; }

        /// <summary>The enemy has fewer (Below) or more (Above) vehicles than this on the field (towers and bosses not counted).</summary>
        public int? EnemyBelow { get; set; }

        public int? EnemyAbove { get; set; }

        /// <summary>The player's side has fewer (Below) or more (Above) vehicles than this on the field.</summary>
        public int? PlayerBelow { get; set; }

        public int? PlayerAbove { get; set; }

        /// <summary>Another event of the mission (its instance id) has happened.</summary>
        public string? After { get; set; }

        /// <summary>The enemy's army is worth this many times the player side's (combat value): the player is being overwhelmed.</summary>
        public float? Outnumbered { get; set; }

        /// <summary>Prompt 31 L3: the enemy has seen one of the player's vehicles (an infiltration found out).</summary>
        public bool Spotted { get; set; }

        /// <summary>
        /// Prompt 31 L5: a prop of this definition standing within 8 m of (<see cref="PropX"/>, <see cref="PropZ"/>) has been
        /// destroyed (the neutral crane brought down); data "propDown": {"def", "x", "z"}. Never holds where no such prop stands.
        /// </summary>
        public string? PropDown { get; set; }

        public float PropX { get; set; }
        public float PropZ { get; set; }

        /// <summary>Seconds between the conditions holding and the event starting.</summary>
        public double Delay { get; set; }

        /// <summary>Seconds between repeats (0: once).</summary>
        public double Every { get; set; }

        public int Times { get; set; } = 1;

        internal static EventTrigger Parse(JsonObject o) => new()
        {
            At = o.Has("at") ? o.Float("at") : null,
            Progress = o.Has("progress") ? o.Float("progress") : null,
            BossHealth = o.Has("bossHealth") ? o.Float("bossHealth") : null,
            EnemyBelow = o.Has("enemyBelow") ? o.Int("enemyBelow", 0) : null,
            EnemyAbove = o.Has("enemyAbove") ? o.Int("enemyAbove", 0) : null,
            PlayerBelow = o.Has("playerBelow") ? o.Int("playerBelow", 0) : null,
            PlayerAbove = o.Has("playerAbove") ? o.Int("playerAbove", 0) : null,
            After = o.Has("after") ? o.String("after") : null,
            Outnumbered = o.Has("outnumbered") ? o.Float("outnumbered") : null,
            Spotted = o.Bool("spotted", false),
            PropDown = o.Has("propDown") ? o.Object("propDown").String("def") : null,
            PropX = o.Has("propDown") ? o.Object("propDown").Float("x", 0f) : 0f,
            PropZ = o.Has("propDown") ? o.Object("propDown").Float("z", 0f) : 0f,
            Delay = o.Float("delay", 0f),
            Every = o.Float("every", 0f),
            Times = o.Int("times", o.Has("every") ? global::MachineBrigade.Sim.Content.SimTunables.Ai.EventTrigger.ParseHasTrue : 1),
        };
    }

    /// <summary>What an event pays (A.1): CP and repairs in the battle, coins, blueprints and an intel file after it.</summary>
    public sealed class EventReward
    {
        public int Cp { get; set; }

        /// <summary>Share of their health the player's vehicles in the zone get back.</summary>
        public float Repair { get; set; }

        public int Coins { get; set; }

        /// <summary>Universal blueprints.</summary>
        public int Prints { get; set; }

        /// <summary>Prompt 22 D.7's intel file (its id), or null.</summary>
        public string? Intel { get; set; }

        /// <summary>A rescued convoy joins the allied reinforcements.</summary>
        public bool Join { get; set; }

        internal static EventReward Parse(JsonObject o) => new()
        {
            Cp = o.Int("cp", 0), Repair = o.Float("repair", 0f), Coins = o.Int("coins", 0), Prints = o.Int("prints", 0),
            Intel = o.Has("intel") ? o.String("intel") : null, Join = o.Bool("join", false),
        };
    }

    /// <summary>
    /// One event of the library (A.1), or one placed in a mission (its <see cref="Instance"/> id, the mission's overrides laid
    /// over the library's entry). Its notices and lines default to the kind's text keys ("event.&lt;kind&gt;.&lt;moment&gt;",
    /// "radio.&lt;speaker&gt;.ev.&lt;kind&gt;.&lt;moment&gt;"); the moments are warn, start, done, fail, retreat and end.
    /// </summary>
    public sealed class MissionEventDef
    {
        public string Id { get; set; } = "";

        /// <summary>Its id in the mission (unique there; what another event's "after" names).</summary>
        public string Instance { get; set; } = "";

        public MissionEventKind Kind { get; set; }
        public EventTrigger Trigger { get; set; } = new();

        /// <summary>Seconds of warning before it happens; null: the kind's rule (the C.3 table's for a big event, none for a small one).</summary>
        public float? Lead { get; set; }

        /// <summary>Who speaks its lines (a portrait id: khai, linh, dieuhau ...); null: the kind's usual voice.</summary>
        public string? Speaker { get; set; }

        /// <summary>Its lines' priority when it is story (0); null: warning lines 1, the rest 2.</summary>
        public LinePriority? Priority { get; set; }

        public EventReward? Reward { get; set; }

        /// <summary>Text keys by moment, over the defaults.</summary>
        public Dictionary<string, string> Notices { get; } = new();

        public Dictionary<string, string> Lines { get; } = new();

        /// <summary>PlanChange in a mission of one goal: the new goal (the mission's fields with the plan's on top).</summary>
        public MissionDef? Plan { get; set; }

        /// <summary>PlanChange in an operation: the stage it moves on to.</summary>
        public string? Stage { get; set; }

        internal JsonObject Params;
        private bool _hasParams;

        public bool Has(string key) => _hasParams && Params.Has(key);

        public float Number(string key, float fallback)
        {
            if (!Has(key)) return fallback;
            return Params.Float(key, fallback);
        }

        public int Whole(string key, int fallback) => Has(key) ? (int)MathF.Round(Params.Float(key, fallback)) : fallback;

        public bool Flag(string key, bool fallback) => Has(key) ? Params.Bool(key, fallback) : fallback;

        public string? Word(string key) => Has(key) && Params.IsString(key) ? Params.String(key) : null;

        public IReadOnlyList<string> Words(string key)
        {
            if (!Has(key)) return Array.Empty<string>();
            return Params.IsString(key) ? new[] { Params.String(key) } : Params.StringArray(key);
        }

        internal void SetParams(JsonObject p)
        {
            Params = p;
            _hasParams = true;
        }

        /// <summary>The kind's name in its text keys ("enemyWave").</summary>
        public string KindKey => char.ToLowerInvariant(Kind.ToString()[0]) + Kind.ToString().Substring(1);

        internal static MissionEventDef Parse(JsonObject o)
        {
            var e = new MissionEventDef
            {
                Id = o.String("id"),
                Kind = o.Enum<MissionEventKind>("kind"),
                Trigger = o.Has("trigger") ? EventTrigger.Parse(o.Object("trigger")) : new EventTrigger { At = 0 },
                Lead = o.Has("lead") ? o.Float("lead") : null,
                Speaker = o.Has("speaker") ? o.String("speaker") : null,
                Priority = o.Has("priority") ? (LinePriority)Math.Clamp(o.Int("priority", 2), 0, 3) : null,
                Reward = o.Has("reward") ? EventReward.Parse(o.Object("reward")) : null,
                Stage = o.Has("stage") ? o.String("stage") : null,
            };
            e.Instance = o.Has("as") ? o.String("as") : e.Id;
            if (o.Has("params")) e.SetParams(o.Object("params"));
            if (o.Has("notices"))
            {
                var n = o.Object("notices");
                foreach (var k in n.Keys) e.Notices[k] = n.String(k);
            }
            if (o.Has("lines"))
            {
                var n = o.Object("lines");
                foreach (var k in n.Keys) e.Lines[k] = n.String(k);
            }
            return e;
        }
    }

    /// <summary>One row of the C.3 table: how a difficulty plays the reinforcement rules.</summary>
    public sealed class EventDifficulty
    {
        /// <summary>How many directions an enemy wave comes from.</summary>
        public int MinDirections { get; set; } = 2;

        public int MaxDirections { get; set; } = 2;

        /// <summary>Seconds of warning before a big event.</summary>
        public float Warning { get; set; } = 10f;

        /// <summary>An allied wave's strength against an enemy wave's (combat value).</summary>
        public float AllyShare { get; set; } = 0.5f;

        /// <summary>Enemy waves' size against the event's own.</summary>
        public float WaveScale { get; set; } = 1f;

        /// <summary>Enemy waves bring elites (a share of their vehicles as the elite versions).</summary>
        public bool Elites { get; set; }

        /// <summary>Most allied waves a mission (-1: no limit).</summary>
        public int AllyWaves { get; set; } = -1;

        /// <summary>Escorts beside a general on the field.</summary>
        public int Escorts { get; set; } = 3;

        /// <summary>The step added to the act for the general's elite-or-mini-boss rule (D.2).</summary>
        public int Step { get; set; } = 1;

        internal static EventDifficulty Parse(JsonObject o, EventDifficulty d)
        {
            if (o.Has("directions"))
            {
                var dirs = o.FloatArray("directions");
                d.MinDirections = (int)dirs[0];
                d.MaxDirections = (int)dirs[dirs.Count - 1];
            }
            d.Warning = o.Float("warning", d.Warning);
            d.AllyShare = o.Float("ally", d.AllyShare);
            d.WaveScale = o.Float("waveScale", d.WaveScale);
            d.Elites = o.Bool("elites", d.Elites);
            d.AllyWaves = o.Int("allyWaves", d.AllyWaves);
            d.Escorts = o.Int("escorts", d.Escorts);
            d.Step = o.Int("step", d.Step);
            return d;
        }
    }

    /// <summary>
    /// How a general's forces come as events (C.1, D.2): the wave roster (Varga's tanks, Orlov's guns, Kessler's landings
    /// and trains, Venn's drones, Wolff's aircraft, Thorne's turned Accord columns, Aurel's drop pods and drones), how they
    /// arrive, the card whose elite the general drives, and the chapter of the general's last battle (no retreat there).
    /// </summary>
    public sealed class GeneralEventDef
    {
        public string Id { get; set; } = "";
        public IReadOnlyList<string> Roster { get; set; } = Array.Empty<string>();

        /// <summary>How the waves come, in order of preference: edge, rail, sea, landing, air, pods.</summary>
        public IReadOnlyList<string> Delivery { get; set; } = new[] { "edge" };

        /// <summary>The card whose elite version the general takes the field in.</summary>
        public string Elite { get; set; } = "main_battle_tank";

        /// <summary>Mini bosses of the general's own, preferred in this order (empty: every mini boss of the general's in the catalog).</summary>
        public IReadOnlyList<string> Minis { get; set; } = Array.Empty<string>();

        /// <summary>The chapter of the general's last battle (its operation): the general fights to the end there.</summary>
        public int LastChapter { get; set; } = 12;

        internal static GeneralEventDef Parse(string id, JsonObject o) => new()
        {
            Id = id,
            Roster = o.Has("roster") ? o.StringArray("roster") : Array.Empty<string>(),
            Delivery = o.Has("delivery") ? o.StringArray("delivery") : new[] { "edge" },
            Elite = o.Has("elite") ? o.String("elite") : "main_battle_tank",
            Minis = o.Has("minis") ? o.StringArray("minis") : Array.Empty<string>(),
            LastChapter = o.Int("lastChapter", 12),
        };
    }

    /// <summary>
    /// The rules every event reads (campaign.json "eventLibrary"): the C.3 table, the generals, the rosters, the reinforcement
    /// caps, how close a spawn may come to the player's units, and the weather's sight. Every number is a starting point for
    /// the testing phase's sweeps (DECISIONS 23A).
    /// </summary>
    public sealed class EventRules
    {
        public Dictionary<EventLevel, EventDifficulty> Levels { get; } = new()
        {
            [EventLevel.Easy] = new EventDifficulty { MinDirections = 1, MaxDirections = 2, Warning = 15f, AllyShare = 0.7f, WaveScale = 0.7f, Escorts = 2, Step = 0 },
            [EventLevel.Normal] = new EventDifficulty { MinDirections = 2, MaxDirections = 2, Warning = 10f, AllyShare = 0.5f, WaveScale = 1f, Escorts = 3, Step = 1 },
            [EventLevel.Hard] = new EventDifficulty { MinDirections = 2, MaxDirections = 3, Warning = 8f, AllyShare = 0.3f, WaveScale = 1.15f, Escorts = 4, Step = 2 },
            [EventLevel.VeryHard] = new EventDifficulty
            {
                MinDirections = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsMinDirections3, MaxDirections = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsMaxDirections3, Warning = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsWarning4, AllyShare = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsAllyShare4, WaveScale = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsWaveScale4, Elites = true, AllyWaves = 1, Escorts = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsEscorts4, Step = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.LevelsStep2,
            },
        };

        /// <summary>The generals (the built-in rows are campaign.json's starting points; its library's rows replace them).</summary>
        public Dictionary<string, GeneralEventDef> Generals { get; } = new()
        {
            // Prompt 23 E.2: Brandt holds chapter 1's coast (his last battle as the enemy is its operation).
            ["brandt"] = G("brandt", 1, "main_battle_tank", new[] { "edge" }, "armored_car", "ifv", "main_battle_tank", "wheeled_gun", "light_tank"),
            ["varga"] = G("varga", 12, "heavy_tank", new[] { "edge" }, "light_tank", "main_battle_tank", "heavy_tank", "tank_destroyer", "twin_tank"),
            ["orlov"] = G("orlov", 11, "mlrs", new[] { "edge" }, "mlrs", "artillery", "mortar_carrier", "heavy_rocket_artillery", "aa_vehicle"),
            ["kessler"] = G("kessler", 12, "main_battle_tank", new[] { "sea", "rail", "landing", "edge" }, "ifv", "wheeled_gun", "main_battle_tank", "mine_layer", "sam_launcher"),
            ["sen"] = G("sen", 5, "fpv_carrier", new[] { "edge", "air" }, "strike_drone", "fpv_carrier", "recon_drone", "ew_jammer"),
            ["quaden"] = new GeneralEventDef
            {
                Id = "quaden", LastChapter = global::MachineBrigade.Sim.Content.SimTunables.Ai.EventRules.GeneralsLastChapter, Elite = "attack_jet", Delivery = new[] { "edge" }, Minis = new[] { "mega_gunship" },
                Roster = new[] { "attack_helicopter", "attack_jet", "strike_drone" },
            },
            ["hung"] = G("hung", 9, "heavy_tank", new[] { "edge", "landing" }, "main_battle_tank", "heavy_tank", "ifv", "aa_vehicle"),
            ["aurel"] = G("aurel", 12, "heavy_tank", new[] { "pods", "air", "edge" }, "strike_drone", "fpv_carrier", "heavy_tank", "ifv", "railgun_truck"),
        };

        private static GeneralEventDef G(string id, int last, string elite, string[] delivery, params string[] roster) =>
            new() { Id = id, LastChapter = last, Elite = elite, Delivery = delivery, Roster = roster };

        /// <summary>A mission without a general sends these.</summary>
        public IReadOnlyList<string> GenericRoster { get; set; } = new[] { "armored_car", "ifv", "light_tank", "main_battle_tank", "aa_vehicle", "mlrs" };

        /// <summary>The Meridian Accord's reinforcements.</summary>
        public IReadOnlyList<string> AccordRoster { get; set; } = new[] { "main_battle_tank", "ifv", "armored_car", "aa_vehicle", "tank_destroyer", "light_tank" };

        /// <summary>C.4: most reinforcement vehicles alive at once, by side (outside the army caps).</summary>
        public int EnemyCap { get; set; } = 16;

        public int AllyCap { get; set; } = 10;

        /// <summary>B.3: no reinforcement appears within this many metres of a player's vehicle.</summary>
        public float NearSight { get; set; } = 45f;

        /// <summary>D.2: the general takes the field in a mini boss once act + the difficulty's step reaches this.</summary>
        public int MiniFrom { get; set; } = 4;

        /// <summary>D.2: a general the story needs later breaks off at this share of their health.</summary>
        public float RetreatAt { get; set; } = 0.3f;

        /// <summary>D.9: how far units see in each weather (only a change mid-battle moves it: the mission's own weather is 1).</summary>
        public Dictionary<string, float> WeatherSight { get; } = new()
        {
            ["Clear"] = 1f, ["Overcast"] = 1f, ["Rain"] = 0.9f, ["Storm"] = 0.8f, ["Snow"] = 0.85f, ["Fog"] = 0.7f, ["Sandstorm"] = 0.75f, ["Night"] = 0.75f,
        };

        public EventDifficulty Of(EventLevel level) => Levels.TryGetValue(level, out var d) ? d : Levels[EventLevel.Normal];

        /// <summary>The built-in rules: the starting points campaign.json's library also carries.</summary>
        public static EventRules Default { get; } = new();

        internal static EventRules Parse(JsonObject o)
        {
            var r = new EventRules();
            if (o.Has("difficulty"))
            {
                var d = o.Object("difficulty");
                foreach (var key in d.Keys)
                    if (Enum.TryParse<EventLevel>(key, true, out var level)) EventDifficulty.Parse(d.Object(key), r.Of(level));
            }
            if (o.Has("generals"))
            {
                var g = o.Object("generals");
                foreach (var key in g.Keys) r.Generals[key] = GeneralEventDef.Parse(key, g.Object(key));
            }
            if (o.Has("genericRoster")) r.GenericRoster = o.StringArray("genericRoster");
            if (o.Has("accordRoster")) r.AccordRoster = o.StringArray("accordRoster");
            if (o.Has("caps"))
            {
                var c = o.Object("caps");
                r.EnemyCap = c.Int("enemy", r.EnemyCap);
                r.AllyCap = c.Int("ally", r.AllyCap);
            }
            r.NearSight = o.Float("nearSight", r.NearSight);
            r.MiniFrom = o.Int("miniFrom", r.MiniFrom);
            r.RetreatAt = o.Float("retreatAt", r.RetreatAt);
            if (o.Has("weatherSight"))
            {
                var w = o.Object("weatherSight");
                foreach (var key in w.Keys) r.WeatherSight[key] = w.Float(key);
            }
            return r;
        }
    }

    /// <summary>
    /// Prompt 23 A: the library of mission events (campaign.json "eventLibrary"): the rules and the events by id. A mission
    /// names the ones it plays ("missionEvents": ["id", {"id": ..., "as": ..., overrides}]), resolved as it is read.
    /// </summary>
    public sealed class EventLibrary
    {
        public EventRules Rules { get; private set; } = EventRules.Default;

        private readonly Dictionary<string, JsonObject> _entries = new();
        private readonly List<string> _order = new();

        public IReadOnlyList<string> Ids => _order;

        /// <summary>Each entry as the library writes it (the checks read every one).</summary>
        public MissionEventDef Get(string id) =>
            _entries.TryGetValue(id, out var o) ? MissionEventDef.Parse(o) : throw new FormatException($"eventLibrary: no event {id}.");

        public static EventLibrary FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            return root.Has("eventLibrary") ? Parse(root.Object("eventLibrary")) : new EventLibrary();
        }

        internal static EventLibrary Parse(JsonObject o)
        {
            var lib = new EventLibrary();
            if (o.Has("rules")) lib.Rules = EventRules.Parse(o.Object("rules"));
            foreach (var e in o.Array("events"))
            {
                var id = e.String("id");
                e.Enum<MissionEventKind>("kind");
                if (lib._entries.ContainsKey(id)) throw new FormatException($"{e.Path}: event {id} twice.");
                lib._entries[id] = e;
                lib._order.Add(id);
            }
            return lib;
        }

        /// <summary>
        /// A mission's events: each reference resolved (its overrides over the library's entry, the trigger and params
        /// merged field by field), instance ids made unique, a plan change's new goal parsed from the mission's fields.
        /// </summary>
        internal IReadOnlyList<MissionEventDef> Resolve(JsonObject mission, string key, Func<JsonObject, MissionDef> plan)
        {
            var list = new List<MissionEventDef>();
            var seen = new HashSet<string>();
            var i = 0;
            foreach (var entry in ArrayOf(mission, key))
            {
                JsonObject o;
                if (entry.value is string id)
                {
                    if (!_entries.TryGetValue(id, out o)) throw new FormatException($"{mission.Path}.{key}[{i}]: no event {id} in the library.");
                }
                else
                {
                    var over = new JsonObject(entry.value, $"{mission.Path}.{key}[{i}]");
                    var id2 = over.String("id");
                    if (!_entries.TryGetValue(id2, out var baseEntry)) throw new FormatException($"{over.Path}: no event {id2} in the library.");
                    o = baseEntry.Under(over);
                    foreach (var part in new[] { "trigger", "params", "notices", "lines", "reward" })
                        if (baseEntry.Has(part) && over.Has(part)) o = o.With(part, baseEntry.Object(part).Under(over.Object(part)).Raw);
                }
                var e = MissionEventDef.Parse(o);
                var name = e.Instance;
                for (var n = 2; !seen.Add(e.Instance); n++) e.Instance = name + "#" + n;
                if (e.Kind == MissionEventKind.PlanChange && o.Has("plan")) e.Plan = plan(o.Object("plan"));
                list.Add(e);
                i++;
            }
            return list;
        }

        private static IEnumerable<(object? value, int index)> ArrayOf(JsonObject o, string key)
        {
            if (!o.Has(key) || o.Raw[key] is not List<object?> items) yield break;
            for (var i = 0; i < items.Count; i++) yield return (items[i], i);
        }
    }

    /// <summary>The C.3 level a mission's events play at.</summary>
    public static class EventLevels
    {
        /// <summary>The mission's difficulty ("Easy", "Normal", "Hard", "VeryHard"), one step up for each tier (1 Heroic, 2 Iron).</summary>
        public static EventLevel From(string? difficulty, int tier = 0)
        {
            var baseLevel = Enum.TryParse<EventLevel>(difficulty ?? "Normal", true, out var l) ? l : EventLevel.Normal;
            return (EventLevel)Math.Clamp((int)baseLevel + Math.Max(0, tier), 0, global::MachineBrigade.Sim.Content.SimTunables.Ai.EventLevels.FromBaseLevelMax);
        }
    }
}

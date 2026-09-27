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
    }

    /// <summary>One campaign mission, read from campaign.json.</summary>
    public sealed class MissionDef
    {
        public string Id { get; set; } = "";
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
        public IReadOnlyList<string> Targets { get; set; } = Array.Empty<string>();
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

        /// <summary>Second star: won within this many seconds (0: always).</summary>
        public float StarTime { get; set; }

        /// <summary>Third star: won losing at most this many vehicles (negative: always).</summary>
        public int StarLosses { get; set; } = -1;

        /// <summary>
        /// The mission's own third star, instead of the losses rule: "NoStrikes" (no fire support
        /// called), "NoAircraft" (no aircraft bought), "Kills" (at least <see cref="ChallengeValue"/>
        /// enemy vehicles destroyed); null keeps <see cref="StarLosses"/>.
        /// </summary>
        public string? Challenge { get; set; }

        public int ChallengeValue { get; set; }

        /// <summary>
        /// A harder copy of the mission (the Heroic and Iron tiers): the enemy starts with more
        /// CP, earns more and sends bigger waves. The mission itself is left as it is.
        /// </summary>
        public MissionDef Harder(float enemy)
        {
            var copy = (MissionDef)MemberwiseClone();
            copy.EnemyCp = EnemyCp * enemy;
            copy.EnemyIncome = EnemyIncome * (1f + (enemy - 1f) * 0.8f);
            copy.Reinforcements = Reinforcements + 1;
            copy.ReinforceSize = (int)Math.Ceiling(ReinforceSize * enemy);
            if (Waves != null)
                copy.Waves = new WaveDef
                {
                    First = Waves.First, Interval = Waves.Interval, Size = (int)Math.Ceiling(Waves.Size * enemy), Grow = Waves.Grow * enemy,
                    MaxSize = (int)Math.Ceiling(Waves.MaxSize * enemy), MaxAlive = (int)Math.Ceiling(Waves.MaxAlive * enemy),
                };
            return copy;
        }

        public static IReadOnlyList<MissionDef> ListFromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "campaign");
            var missions = new List<MissionDef>();
            foreach (var m in root.Array("missions")) missions.Add(Parse(m));
            return missions;
        }

        private static MissionDef Parse(JsonObject m)
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
                StarTime = m.Float("starTime", 0f),
                StarLosses = m.Int("starLosses", -1),
            };
            if (m.Has("challenge"))
            {
                var c = m.Object("challenge");
                def.Challenge = c.String("kind");
                def.ChallengeValue = c.Int("value", 0);
            }
            if (m.Has("boss")) def.Boss = Scripted(m.Object("boss"));
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
            if (m.Has("units"))
            {
                var units = new List<UnitPlacement>();
                foreach (var u in m.Array("units"))
                    units.Add(new UnitPlacement(u.String("def"), u.Int("team", 0), new Vector2(u.Float("x"), u.Float("z")),
                        SimMath.DegToRad(u.Float("heading", 0f))));
                def.Units = units;
            }
            return def;
        }

        private static ScriptedUnitDef Scripted(JsonObject o) => new()
        {
            Def = o.String("def"),
            Position = new Vector2(o.Float("x"), o.Float("z")),
            Heading = SimMath.DegToRad(o.Float("heading", 0f)),
            Route = o.Has("route") ? Points2(o.FloatArray("route")) : Array.Empty<Vector2>(),
        };

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

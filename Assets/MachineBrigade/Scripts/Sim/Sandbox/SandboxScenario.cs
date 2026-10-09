#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Text;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>How a Sandbox side is commanded (prompt 21 C.2).</summary>
    public enum SandboxAi
    {
        /// <summary>The commander AI: buys from its deck, calls fire support, gives orders.</summary>
        Full,

        /// <summary>The fighting AI only: it commands what is on the field and buys nothing.</summary>
        Combat,

        /// <summary>No AI: every unit stays where it was put (it still shoots what comes into reach).</summary>
        Idle,
    }

    /// <summary>A placed unit's equipment (prompt 21 B.6).</summary>
    public enum SandboxGear
    {
        None,

        /// <summary>A fixed, sensible set for its branch (the same on every device).</summary>
        Suggested,

        /// <summary>The player's own loadout for its branch (differs from player to player).</summary>
        Player,
    }

    /// <summary>A boss's state as the scenario starts (prompt 21 F.1).</summary>
    public sealed class SandboxBossState
    {
        /// <summary>The phase it starts in (0 the first).</summary>
        public int Phase;

        /// <summary>Its big attack switched off.</summary>
        public bool BigOff;

        /// <summary>Its escorts sent home (none come).</summary>
        public bool NoEscorts;

        /// <summary>Indices of its parts that start broken.</summary>
        public List<int> Broken = new();

        public SandboxBossState Clone() => new() { Phase = Phase, BigOff = BigOff, NoEscorts = NoEscorts, Broken = new List<int>(Broken) };

        public bool IsDefault => Phase == 0 && !BigOff && !NoEscorts && Broken.Count == 0;
    }

    /// <summary>One placed unit (prompt 21 B.4-B.6).</summary>
    public sealed class SandboxUnit
    {
        public string Def = "";
        public int Team;
        public float X, Y;

        /// <summary>Degrees, the game's convention: 0 north (+Y), clockwise.</summary>
        public float Heading;

        public int Rank = 1;
        public SandboxGear Gear;
        public bool Elite;

        /// <summary>Health and ammunition at the start, in per cent (1-100 and 0-100).</summary>
        public int Hp = global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxUnit.Hp, Ammo = global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxUnit.Ammo;

        /// <summary>An altitude-tier boss's starting tier ("low", "high"; empty: its own opening).</summary>
        public string Tier = "";

        public bool Immortal;
        public SandboxBossState? Boss;

        public System.Numerics.Vector2 Position
        {
            get => new(X, Y);
            set
            {
                X = SandboxRules.Round(value.X);
                Y = SandboxRules.Round(value.Y);
            }
        }

        public SandboxUnit Clone() => new()
        {
            Def = Def, Team = Team, X = X, Y = Y, Heading = Heading, Rank = Rank, Gear = Gear, Elite = Elite, Hp = Hp, Ammo = Ammo,
            Tier = Tier, Immortal = Immortal, Boss = Boss?.Clone(),
        };
    }

    /// <summary>A side's HQ and towers (prompt 21 B.7): none, the AI's for a difficulty, or the player's saved plan.</summary>
    public enum SandboxBase
    {
        None,
        Ai,
        Player,
    }

    /// <summary>One side's settings (prompt 21 B.7, C.2, C.4, C.5).</summary>
    public sealed class SandboxSide
    {
        public SandboxAi Ai = SandboxAi.Combat;

        /// <summary>CP at the start; negative: unlimited (topped up every step).</summary>
        public float Cp = -1f;

        /// <summary>CP a second when not unlimited.</summary>
        public float Income = 1f;

        /// <summary>Fire-support cooldowns (off: a support is ready again at once).</summary>
        public bool Cooldowns = true;

        public bool Immortal;

        /// <summary>The cards the full AI buys and calls (empty: the kinds already on the field).</summary>
        public List<string> Deck = new();

        public List<string> Supports = new();

        public SandboxBase Base = SandboxBase.None;

        /// <summary>The AI base's difficulty (Easy, Normal, Hard).</summary>
        public string BaseLevel = "Normal";

        /// <summary>Prompt 22 F.1: the side's commander or general ("kade", "gen.varga"; empty: none).</summary>
        public string Commander = "";

        /// <summary>Prompt 28 H.13: the side's tactic for the full AI (empty: its general's preference).</summary>
        public string Tactic = "";

        public SandboxSide Clone() => new()
        {
            Ai = Ai, Cp = Cp, Income = Income, Cooldowns = Cooldowns, Immortal = Immortal, Deck = new List<string>(Deck),
            Supports = new List<string>(Supports), Base = Base, BaseLevel = BaseLevel, Commander = Commander, Tactic = Tactic,
        };
    }

    /// <summary>A pass condition that turns a scenario into an automatic test (prompt 21 F.2).</summary>
    public sealed class SandboxCheck
    {
        /// <summary>"win" (side <see cref="Team"/> wins within <see cref="Seconds"/>), "noStuck", "survive" (the side still has units at the end).</summary>
        public string Kind = "win";

        public int Team;
        public float Seconds = global::MachineBrigade.Sim.Content.SimTunables.Modes.SandboxCheck.Seconds;

        public SandboxCheck Clone() => new() { Kind = Kind, Team = Team, Seconds = Seconds };
    }

    /// <summary>
    /// A Sandbox battle as the player set it up (prompt 21 F.1): the map, the weather, the units (kind, side, place,
    /// heading, rank, equipment, elite, health, ammunition), both sides' bases and AI, the bosses' state and the seed.
    /// Saved as JSON with a format version (<see cref="Version"/>); files of every earlier version still open
    /// (<see cref="FromJson"/> upgrades them), and it shares as a short text code (<see cref="ToCode"/>).
    /// </summary>
    public sealed class SandboxScenario
    {
        /// <summary>
        /// The format written now. 1: map, seed and units only (kind, side, place, heading in radians); 2: headings
        /// in degrees, and everything else (rank, equipment, health, ammunition, bosses, bases, AI, weather, checks).
        /// </summary>
        public const int Version = 2;

        public const string Format = "machine-brigade-sandbox";

        /// <summary>The share code's prefix: the format and its version ("MBS2.").</summary>
        public const string CodePrefix = "MBS";

        public string Name = "";

        /// <summary>A map file id ("ashfield_conquest") or <see cref="SandboxMaps.FlatId"/>.</summary>
        public string Map = SandboxMaps.FlatId;

        public int Seed = 1;

        /// <summary>A weather name (the game's WeatherKind: Clear, Rain, Storm, Snow, Fog, Sandstorm, Overcast).</summary>
        public string Weather = "Clear";

        public bool Night;
        public bool Fog = true;

        /// <summary>The bosses' difficulty key (Easy, Normal, Hard, Heroic, Iron): their escorts and big attacks (prompt 21 D.6).</summary>
        public string Difficulty = "Normal";

        /// <summary>Seconds after which the battle is called (0: never).</summary>
        public float Limit;

        public SandboxSide[] Sides = { new(), new() { Ai = SandboxAi.Combat } };
        public List<SandboxUnit> Units = new();
        public List<SandboxCheck> Checks = new();

        /// <summary>The version the file was written in (read back; <see cref="Version"/> for a new one).</summary>
        public int LoadedVersion { get; private set; } = Version;

        public SandboxScenario Clone()
        {
            var c = new SandboxScenario
            {
                Name = Name, Map = Map, Seed = Seed, Weather = Weather, Night = Night, Fog = Fog, Difficulty = Difficulty, Limit = Limit,
                Sides = new[] { Sides[0].Clone(), Sides[1].Clone() }, LoadedVersion = LoadedVersion,
            };
            foreach (var u in Units) c.Units.Add(u.Clone());
            foreach (var k in Checks) c.Checks.Add(k.Clone());
            return c;
        }

        // ================================================================== writing

        private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        private static string F(float v) => v.ToString("R", Inv);

        private static string Q(string s)
        {
            var b = new StringBuilder("\"");
            foreach (var ch in s ?? "")
            {
                switch (ch)
                {
                    case '"': b.Append("\\\""); break;
                    case '\\': b.Append("\\\\"); break;
                    case '\n': b.Append("\\n"); break;
                    case '\r': b.Append("\\r"); break;
                    case '\t': b.Append("\\t"); break;
                    default:
                        if (ch < 0x20) b.Append("\\u").Append(((int)ch).ToString("x4", Inv));
                        else b.Append(ch);
                        break;
                }
            }
            return b.Append('"').ToString();
        }

        private static string B(bool v) => v ? "true" : "false";

        private static string List(IEnumerable<string> ids)
        {
            var b = new StringBuilder("[");
            var first = true;
            foreach (var id in ids)
            {
                if (!first) b.Append(',');
                b.Append(Q(id));
                first = false;
            }
            return b.Append(']').ToString();
        }

        /// <summary>The scenario as JSON, always the same text for the same scenario (keys in a fixed order).</summary>
        public string ToJson()
        {
            var b = new StringBuilder();
            b.Append("{\"format\":").Append(Q(Format)).Append(",\"version\":").Append(Version);
            b.Append(",\"name\":").Append(Q(Name)).Append(",\"map\":").Append(Q(Map)).Append(",\"seed\":").Append(Seed.ToString(Inv));
            b.Append(",\"weather\":").Append(Q(Weather)).Append(",\"night\":").Append(B(Night)).Append(",\"fog\":").Append(B(Fog));
            b.Append(",\"difficulty\":").Append(Q(Difficulty)).Append(",\"limit\":").Append(F(Limit));
            b.Append(",\"sides\":[");
            for (var i = 0; i < 2; i++)
            {
                var s = Sides[i];
                if (i > 0) b.Append(',');
                b.Append("{\"ai\":").Append(Q(s.Ai.ToString())).Append(",\"cp\":").Append(F(s.Cp)).Append(",\"income\":").Append(F(s.Income));
                b.Append(",\"cooldowns\":").Append(B(s.Cooldowns)).Append(",\"immortal\":").Append(B(s.Immortal));
                b.Append(",\"deck\":").Append(List(s.Deck)).Append(",\"supports\":").Append(List(s.Supports));
                b.Append(",\"base\":").Append(Q(s.Base.ToString())).Append(",\"baseLevel\":").Append(Q(s.BaseLevel));
                if (!string.IsNullOrEmpty(s.Commander)) b.Append(",\"commander\":").Append(Q(s.Commander));
                if (!string.IsNullOrEmpty(s.Tactic)) b.Append(",\"tactic\":").Append(Q(s.Tactic));
                b.Append('}');
            }
            b.Append("],\"units\":[");
            for (var i = 0; i < Units.Count; i++)
            {
                var u = Units[i];
                if (i > 0) b.Append(',');
                b.Append("{\"def\":").Append(Q(u.Def)).Append(",\"team\":").Append(u.Team.ToString(Inv));
                b.Append(",\"x\":").Append(F(u.X)).Append(",\"y\":").Append(F(u.Y)).Append(",\"heading\":").Append(F(u.Heading));
                if (u.Rank != 1) b.Append(",\"rank\":").Append(u.Rank.ToString(Inv));
                if (u.Gear != SandboxGear.None) b.Append(",\"gear\":").Append(Q(u.Gear.ToString()));
                if (u.Elite) b.Append(",\"elite\":true");
                if (u.Hp != 100) b.Append(",\"hp\":").Append(u.Hp.ToString(Inv));
                if (u.Ammo != 100) b.Append(",\"ammo\":").Append(u.Ammo.ToString(Inv));
                if (!string.IsNullOrEmpty(u.Tier)) b.Append(",\"tier\":").Append(Q(u.Tier));
                if (u.Immortal) b.Append(",\"immortal\":true");
                if (u.Boss is { IsDefault: false } boss)
                {
                    b.Append(",\"boss\":{\"phase\":").Append(boss.Phase.ToString(Inv)).Append(",\"bigOff\":").Append(B(boss.BigOff));
                    b.Append(",\"noEscorts\":").Append(B(boss.NoEscorts)).Append(",\"broken\":[");
                    for (var k = 0; k < boss.Broken.Count; k++) b.Append(k > 0 ? "," : "").Append(boss.Broken[k].ToString(Inv));
                    b.Append("]}");
                }
                b.Append('}');
            }
            b.Append("],\"checks\":[");
            for (var i = 0; i < Checks.Count; i++)
            {
                var c = Checks[i];
                if (i > 0) b.Append(',');
                b.Append("{\"kind\":").Append(Q(c.Kind)).Append(",\"team\":").Append(c.Team.ToString(Inv)).Append(",\"seconds\":").Append(F(c.Seconds)).Append('}');
            }
            return b.Append("]}").ToString();
        }

        // ================================================================== reading

        /// <summary>
        /// Reads a scenario of any version up to <see cref="Version"/> (older ones are upgraded; missing fields take
        /// their defaults). Throws <see cref="FormatException"/> on text that is not a scenario or is from a newer game.
        /// </summary>
        public static SandboxScenario FromJson(string json)
        {
            if (string.IsNullOrWhiteSpace(json)) throw new FormatException("Empty scenario.");
            object? parsed;
            try
            {
                parsed = MiniJson.Parse(json);
            }
            catch (Exception e)
            {
                throw new FormatException("Not a scenario: " + e.Message);
            }
            return FromObject(parsed);
        }

        /// <summary>A scenario from its parsed JSON (a replay file carries one inside it).</summary>
        internal static SandboxScenario FromObject(object? parsed)
        {
            if (parsed is not Dictionary<string, object?>) throw new FormatException("Not a scenario.");
            var o = new JsonObject(parsed, "scenario");
            var version = o.Int("version", 1);
            if (version > Version) throw new FormatException($"Scenario version {version} is newer than this game's ({Version}).");
            if (version < 1) throw new FormatException($"Unknown scenario version {version}.");
            var s = new SandboxScenario { LoadedVersion = version };
            s.Name = Str(o, "name", "");
            s.Map = Str(o, "map", SandboxMaps.FlatId);
            s.Seed = o.Int("seed", 1);
            if (version >= 2)
            {
                s.Weather = Str(o, "weather", "Clear");
                s.Night = o.Bool("night", false);
                s.Fog = o.Bool("fog", true);
                s.Difficulty = Str(o, "difficulty", "Normal");
                s.Limit = o.Float("limit", 0f);
                if (o.IsArray("sides"))
                {
                    var i = 0;
                    foreach (var so in o.Array("sides"))
                    {
                        if (i > 1) break;
                        var side = s.Sides[i++];
                        side.Ai = so.Enum("ai", SandboxAi.Combat);
                        side.Cp = so.Float("cp", -1f);
                        side.Income = so.Float("income", 1f);
                        side.Cooldowns = so.Bool("cooldowns", true);
                        side.Immortal = so.Bool("immortal", false);
                        if (so.IsArray("deck")) side.Deck.AddRange(so.StringArray("deck"));
                        if (so.IsArray("supports")) side.Supports.AddRange(so.StringArray("supports"));
                        side.Base = so.Enum("base", SandboxBase.None);
                        side.BaseLevel = Str(so, "baseLevel", "Normal");
                        side.Tactic = Str(so, "tactic", "");
                        side.Commander = Str(so, "commander", "");
                    }
                }
                if (o.IsArray("checks"))
                    foreach (var co in o.Array("checks"))
                        s.Checks.Add(new SandboxCheck { Kind = Str(co, "kind", "win"), Team = co.Int("team", 0), Seconds = co.Float("seconds", 60f) });
            }
            if (o.IsArray("units"))
                foreach (var uo in o.Array("units"))
                {
                    var u = new SandboxUnit
                    {
                        Def = Str(uo, "def", ""),
                        Team = Math.Clamp(uo.Int("team", 0), 0, 1),
                        X = uo.Float("x", 0f),
                        Y = uo.Float("y", 0f),
                    };
                    // Version 1 kept the heading in radians under "h".
                    u.Heading = version >= 2 ? uo.Float("heading", 0f) : SandboxRules.Normalise(uo.Float("h", 0f) * 180f / MathF.PI);
                    if (version >= 2)
                    {
                        u.Rank = Math.Max(1, uo.Int("rank", 1));
                        u.Gear = uo.Enum("gear", SandboxGear.None);
                        u.Elite = uo.Bool("elite", false);
                        u.Hp = Math.Clamp(uo.Int("hp", 100), 1, 100);
                        u.Ammo = Math.Clamp(uo.Int("ammo", 100), 0, 100);
                        u.Tier = Str(uo, "tier", "");
                        u.Immortal = uo.Bool("immortal", false);
                        if (uo.Has("boss"))
                        {
                            var bo = uo.Object("boss");
                            var boss = new SandboxBossState { Phase = bo.Int("phase", 0), BigOff = bo.Bool("bigOff", false), NoEscorts = bo.Bool("noEscorts", false) };
                            if (bo.IsArray("broken"))
                                foreach (var f in bo.FloatArray("broken")) boss.Broken.Add((int)f);
                            u.Boss = boss;
                        }
                    }
                    if (u.Def.Length > 0) s.Units.Add(u);
                }
            return s;
        }

        private static string Str(JsonObject o, string key, string fallback) => o.Raw.TryGetValue(key, out var v) && v is string text ? text : fallback;

        // ================================================================== share codes (F.7)

        /// <summary>The scenario as a text code to paste: "MBS2." and the JSON deflated in URL-safe base 64.</summary>
        public string ToCode()
        {
            var raw = Encoding.UTF8.GetBytes(ToJson());
            using var packed = new MemoryStream();
            using (var deflate = new DeflateStream(packed, CompressionLevel.Optimal, leaveOpen: true)) deflate.Write(raw, 0, raw.Length);
            var text = Convert.ToBase64String(packed.ToArray()).TrimEnd('=').Replace('+', '-').Replace('/', '_');
            return CodePrefix + Version.ToString(Inv) + "." + text;
        }

        /// <summary>Reads a share code (of any version up to this one); throws <see cref="FormatException"/> on a bad one.</summary>
        public static SandboxScenario FromCode(string code)
        {
            code = (code ?? "").Trim();
            var dot = code.IndexOf('.');
            if (!code.StartsWith(CodePrefix, StringComparison.Ordinal) || dot < 0) throw new FormatException("Not a scenario code.");
            var text = code.Substring(dot + 1).Replace('-', '+').Replace('_', '/');
            text = text.PadRight(text.Length + (4 - text.Length % 4) % 4, '=');
            byte[] packed;
            try
            {
                packed = Convert.FromBase64String(text);
            }
            catch (FormatException)
            {
                throw new FormatException("Not a scenario code.");
            }
            using var input = new MemoryStream(packed);
            using var deflate = new DeflateStream(input, CompressionMode.Decompress);
            using var output = new MemoryStream();
            try
            {
                deflate.CopyTo(output);
            }
            catch (Exception e) when (e is InvalidDataException or IOException)
            {
                throw new FormatException("Not a scenario code.");
            }
            return FromJson(Encoding.UTF8.GetString(output.ToArray()));
        }
    }
}

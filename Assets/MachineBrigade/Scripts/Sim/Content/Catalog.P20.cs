#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Prompt 20 E.5: a boss's rank. None: not a boss.</summary>
    public enum BossRank
    {
        None,
        Main,
        Mini,
    }

    /// <summary>Prompt 20 E.1: how a boss's body frame moves.</summary>
    public enum BossMove
    {
        Tracked,
        Wheeled,
        Rail,
        Ship,
        Submarine,
        Aircraft,
        Spacecraft,
    }

    /// <summary>
    /// A boss body frame (balance.json "bossFrames"): how it moves and which altitude rules it keeps. Ground
    /// frames are ordinary ground targets; an aircraft the ordinary air rules; a spacecraft has altitude tiers
    /// (prompt 19); a ship and a submarine sail the sea lanes, a submarine diving out of reach (its tier
    /// Orbit's rule under water: nothing reaches it).
    /// </summary>
    public sealed class BossFrameDef
    {
        public BossFrameDef(string id) => Id = Guard.Id(id);

        public string Id { get; }
        public BossMove Move { get; internal set; }

        public bool Ground => Move is BossMove.Tracked or BossMove.Wheeled or BossMove.Rail;
        public bool Sea => Move is BossMove.Ship or BossMove.Submarine;
    }

    /// <summary>A boss rank's rules for the show (balance.json "bossRanks"); its stats are applied to the data by <see cref="BossTemplates"/>.</summary>
    public sealed class BossRankDef
    {
        public BossRankDef(string id) => Id = Guard.Id(id);

        public string Id { get; }
        public BossRank Rank { get; internal set; }

        /// <summary>Its bar's label ("Boss", "Mini boss"): a text key.</summary>
        public string Label => "boss.rank." + Id;

        /// <summary>Seconds the camera pans to it as it arrives (a long introduction, a short look).</summary>
        public float Intro { get; internal set; } = 3.5f;

        /// <summary>The music track while it is on the field (a main boss may name its own).</summary>
        public string Music { get; internal set; } = "boss";

        /// <summary>Its rewards as a share of a main boss's.</summary>
        public float Reward { get; internal set; } = 1f;

        /// <summary>Its escorts alive at once at most, each wave cut to it (0: the rules' cap).</summary>
        public int EscortCap { get; internal set; }

        /// <summary>A small bar (a mini boss's).</summary>
        public bool Compact { get; internal set; }

        /// <summary>Play-test 6 (DECISIONS 21G): its weapons cycle this much faster (cooldowns, magazines and clips; 1: as the data).</summary>
        public float FireRate { get; internal set; } = 1f;

        /// <summary>Play-test 6: its hits on aircraft x this (a boss's air defence is fuzed and radar-laid).</summary>
        public float AirDamage { get; internal set; } = 1f;

        /// <summary>Play-test 6: the share it takes of a called strike's or a bomb's damage.</summary>
        public float StrikeTaken { get; internal set; } = 1f;

        /// <summary>
        /// Play-test 6: strikes and bombs take at most this share of its health in <see cref="StrikeWindow"/> seconds
        /// (0: no cap); past it only <see cref="StrikeOver"/> of their damage gets through. One bomber's load or one
        /// barrage no longer wipes it.
        /// </summary>
        public float StrikeCap { get; internal set; }

        public float StrikeWindow { get; internal set; } = 10f;

        public float StrikeOver { get; internal set; } = 0.2f;
    }

    /// <summary>
    /// Prompt 20 H.1: a workshop that builds vehicles inside the boss (Moloch): every <see cref="Every"/> seconds
    /// <see cref="Min"/> to <see cref="Max"/> of its phase's <see cref="Units"/> drive out of its standing doors,
    /// one more each <see cref="Grow"/> seconds, never more than <see cref="Cap"/> of them alive (apart from
    /// its escorts). Every door broken, it builds no more.
    /// </summary>
    public sealed class FactoryDef
    {
        public float First { get; internal set; } = 12f;
        public float Every { get; internal set; } = 20f;
        public int Min { get; internal set; } = 1;
        public int Max { get; internal set; } = 2;
        public float Grow { get; internal set; } = 60f;
        public int Cap { get; internal set; } = 6;

        /// <summary>The vehicles it builds, by phase (the last list holds after).</summary>
        public IReadOnlyList<IReadOnlyList<string>> Units { get; internal set; } = Array.Empty<IReadOnlyList<string>>();

        /// <summary>The parts its vehicles drive out of (each standing one sends its share).</summary>
        public IReadOnlyList<string> Doors { get; internal set; } = Array.Empty<string>();

        public IReadOnlyList<string> UnitsFor(int phase) => Units.Count == 0 ? Array.Empty<string>() : Units[Math.Clamp(phase, 0, Units.Count - 1)];
    }

    /// <summary>
    /// Prompt 20 J: a boss that crushes what is in front of it as it goes (Kronos's bucket wheel, Ixion's
    /// wheels): <see cref="Dps"/> a second to every other-side ground vehicle, tower and wall within
    /// <see cref="Reach"/> m past the front of its hull, less by <see cref="ArmourCut"/> for each armour level
    /// of the face it meets (Ixion rolls over light vehicles and grinds on heavy ones); walls and towers take
    /// <see cref="Structure"/> times as much; with <see cref="Hq"/> an HQ it reaches is flattened outright.
    /// </summary>
    public sealed class CrushDef
    {
        public float Dps { get; internal set; } = 600f;
        public float Reach { get; internal set; } = 3f;
        public float ArmourCut { get; internal set; }
        public float Structure { get; internal set; } = 1f;
        public bool Hq { get; internal set; }

        /// <summary>Only while it moves faster than this (m/s): a wheel's weight, not a standing hull.</summary>
        public float MinSpeed { get; internal set; } = 0.2f;

        /// <summary>From this phase (0 up) it throws debris round itself (-1: never): every <see cref="DebrisEvery"/> s three blasts of <see cref="DebrisDamage"/> within <see cref="DebrisRadius"/> m.</summary>
        public int DebrisPhase { get; internal set; } = -1;

        public float DebrisEvery { get; internal set; } = 4f;
        public float DebrisRadius { get; internal set; } = 16f;
        public float DebrisDamage { get; internal set; } = 120f;

        /// <summary>
        /// Prompt 25 C2 (DECISIONS 25C): the weapon it is (Kronos's bucket wheel, a mount on its wheel, so the weapons
        /// tables and the Guide show it): with no "dps" or "reach" of its own, its damage a second and its reach are the
        /// weapon's (damage over cooldown, range). Null: the crusher's own numbers (Ixion's wheels).
        /// </summary>
        public string? Weapon { get; internal set; }
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 20 E.5: main boss, mini boss, or none.</summary>
        public BossRank Rank { get; internal set; }

        public BossRankDef? RankDef { get; internal set; }

        public bool MiniBoss => Rank == BossRank.Mini;

        internal string? FrameId { get; set; }

        /// <summary>Prompt 20 E.1: its body frame, or null.</summary>
        public BossFrameDef? Frame { get; internal set; }

        /// <summary>Prompt 20 E.5: the main boss it is a variant of, or null.</summary>
        public string? VariantOf { get; internal set; }

        /// <summary>Its variant's naming rule: "mk0" (the prototype, met before the main boss), "mk2" (the upgrade, after), or null (a name of its own).</summary>
        public string? VariantName { get; internal set; }

        /// <summary>The mini boss made from it (its first variant), or null: the Sandbox's switch between the two.</summary>
        public string? MiniVariant { get; internal set; }

        /// <summary>A variant's colour: its hull multiplied by it (null: the model's own).</summary>
        public Vector3? Tint { get; internal set; }

        /// <summary>A variant's mark painted on it ("mk0", "mk2", "ice" ...), or null.</summary>
        public string? Mark { get; internal set; }

        /// <summary>Model nodes of the parts it was built without (a mini boss's dropped weapons): hidden from the start.</summary>
        public IReadOnlyList<string> HiddenNodes { get; internal set; } = Array.Empty<string>();

        /// <summary>Its own music track (a main boss's), or null: its rank's.</summary>
        public string? Music { get; internal set; }

        public FactoryDef? Factory { get; internal set; }
        public CrushDef? Crush { get; internal set; }

        /// <summary>A named route of the battlefield it follows when the mode gives it none (the open-pit mine's "haul").</summary>
        public string? RouteName { get; internal set; }

        /// <summary>Prompt 20 I.7 (Argus): while it lives, its side's artillery scatters this share as widely (1: no effect).</summary>
        public float SpotAura { get; internal set; } = 1f;

        /// <summary>Prompt 20 J.4: mounts silent until phase <see cref="WakePhase"/> (Typhon's deck gun, surfaced for good).</summary>
        public int WakePhase { get; internal set; } = -1;

        public IReadOnlyList<int> WakeMounts { get; internal set; } = Array.Empty<int>();

        /// <summary>
        /// Prompt 26 B.2: a close-guard ring (data "guard"): while <see cref="GuardRingDef.Count"/> or more ground vehicles stand
        /// within <see cref="GuardRingDef.Radius"/> m of its hull it blasts the ground round its body every <see cref="GuardRingDef.Every"/> s.
        /// </summary>
        public GuardRingDef? GuardRing { get; internal set; }
    }

    /// <summary>Prompt 26 B.2: a main boss's close guard (the ring of blasts round its body when a crowd comes in close).</summary>
    public sealed class GuardRingDef
    {
        /// <summary>How near a vehicle must be (from the boss's hull) to count.</summary>
        public float Radius { get; internal set; } = 15f;

        /// <summary>How many vehicles make a crowd.</summary>
        public int Count { get; internal set; } = 4;

        /// <summary>Seconds between rings while the crowd stays.</summary>
        public float Every { get; internal set; } = 5f;

        /// <summary>The blast's damage before the boss's own scale; its core reaches <see cref="Pad"/> m past the hull, the edge twice that (at most 20 m).</summary>
        public float Damage { get; internal set; }

        public float Pad { get; internal set; } = 6f;
    }

    /// <summary>Prompt 20 (DECISIONS 19E): frames, ranks, variants and the new boss mechanisms.</summary>
    public sealed partial class Catalog
    {
        public IReadOnlyDictionary<string, BossFrameDef> BossFrames { get; internal set; } = new Dictionary<string, BossFrameDef>();
        public IReadOnlyDictionary<string, BossRankDef> BossRanks { get; internal set; } = new Dictionary<string, BossRankDef>();

        private static void ParseP20(JsonObject v, VehicleDef def)
        {
            if (v.Has("frame")) def.FrameId = v.String("frame");
            if (def.Boss) def.Rank = v.Enum("rank", BossRank.Main);
            if (v.Has("variantOf")) def.VariantOf = v.String("variantOf");
            if (v.Has("variantName")) def.VariantName = v.String("variantName");
            if (v.Has("tint"))
            {
                var t = v.FloatArray("tint");
                def.Tint = new Vector3(t.Count > 0 ? t[0] : 1f, t.Count > 1 ? t[1] : 1f, t.Count > 2 ? t[2] : 1f);
            }
            if (v.Has("mark")) def.Mark = v.String("mark");
            if (v.Has("hiddenNodes")) def.HiddenNodes = v.StringArray("hiddenNodes");
            if (v.Has("music")) def.Music = v.String("music");
            if (v.Has("route")) def.RouteName = v.String("route");
            def.SpotAura = Math.Clamp(v.Float("spotAura", 1f), 0.1f, 1f);
            if (v.Has("factory"))
            {
                var f = v.Object("factory");
                // "units": one list of vehicle ids a phase.
                var units = new List<IReadOnlyList<string>>();
                if (f.Raw.TryGetValue("units", out var u) && u is List<object?> lists)
                    foreach (var o in lists)
                    {
                        if (o is not List<object?> list) throw new FormatException($"{f.Path}.units: a list of lists of vehicle ids.");
                        var ids = new List<string>();
                        foreach (var id in list) ids.Add(id as string ?? throw new FormatException($"{f.Path}.units: a list of lists of vehicle ids."));
                        units.Add(ids);
                    }
                def.Factory = new FactoryDef
                {
                    First = MathF.Max(0f, f.Float("first", 12f)), Every = MathF.Max(1f, f.Float("every", 20f)), Min = Math.Max(1, f.Int("min", 1)),
                    Max = Math.Max(1, f.Int("max", 2)), Grow = MathF.Max(1f, f.Float("grow", 60f)), Cap = Math.Max(1, f.Int("cap", 6)),
                    Units = units, Doors = f.Has("doors") ? f.StringArray("doors") : Array.Empty<string>(),
                };
            }
            if (v.Has("crush"))
            {
                var c = v.Object("crush");
                def.Crush = new CrushDef
                {
                    Dps = MathF.Max(0f, c.Float("dps", 600f)), Reach = MathF.Max(0.5f, c.Float("reach", 3f)), ArmourCut = Math.Clamp(c.Float("armourCut", 0f), 0f, 0.25f),
                    Structure = MathF.Max(0f, c.Float("structure", 1f)), Hq = c.Bool("hq", false), MinSpeed = MathF.Max(0f, c.Float("minSpeed", 0.2f)),
                    DebrisPhase = c.Int("debrisPhase", -1), DebrisEvery = MathF.Max(1f, c.Float("debrisEvery", 4f)),
                    DebrisRadius = MathF.Max(2f, c.Float("debrisRadius", 16f)), DebrisDamage = MathF.Max(0f, c.Float("debrisDamage", 120f)),
                    Weapon = c.Has("weapon") ? c.String("weapon") : null,
                };
                // Prompt 25 C2: the weapon's numbers where the crusher gives none (filled in once the weapons are read).
                if (def.Crush.Weapon != null && !c.Has("dps")) def.Crush.Dps = -1f;
                if (def.Crush.Weapon != null && !c.Has("reach")) def.Crush.Reach = -1f;
            }
            if (v.Has("guard"))
            {
                var g = v.Object("guard");
                def.GuardRing = new GuardRingDef
                {
                    Radius = MathF.Max(1f, g.Float("radius", 15f)), Count = Math.Max(1, g.Int("count", 4)), Every = MathF.Max(1f, g.Float("every", 5f)),
                    Damage = MathF.Max(0f, g.Float("damage", 0f)), Pad = MathF.Max(1f, g.Float("pad", 6f)),
                };
            }
            if (v.Has("wake"))
            {
                var w = v.Object("wake");
                def.WakePhase = w.Int("phase", 1);
                var mounts = new List<int>();
                foreach (var m in w.FloatArray("mounts")) mounts.Add((int)m);
                def.WakeMounts = mounts;
            }
        }

        /// <summary>The frame and rank tables, every boss's frame, rank and variant link, the new mechanisms checked.</summary>
        private void FinishP20(JsonObject root)
        {
            var frames = new Dictionary<string, BossFrameDef>();
            if (root.Has("bossFrames"))
            {
                var o = root.Object("bossFrames");
                foreach (var key in o.Keys) frames[key] = new BossFrameDef(key) { Move = o.Object(key).Enum("move", BossMove.Tracked) };
            }
            BossFrames = frames;
            var ranks = new Dictionary<string, BossRankDef>();
            if (root.Has("bossRanks"))
            {
                var o = root.Object("bossRanks");
                foreach (var key in o.Keys)
                {
                    var r = o.Object(key);
                    ranks[key] = new BossRankDef(key)
                    {
                        Rank = Enum.TryParse<BossRank>(key, true, out var rank) ? rank : throw new FormatException($"balance.bossRanks: unknown rank '{key}'."),
                        Intro = MathF.Max(0f, r.Float("intro", 3.5f)), Music = r.Has("music") ? r.String("music") : "boss",
                        Reward = MathF.Max(0f, r.Float("reward", 1f)), EscortCap = Math.Max(0, r.Int("escortCap", 0)), Compact = r.Bool("compact", false),
                        FireRate = Math.Clamp(r.Float("fireRate", 1f), 0.25f, 4f), AirDamage = Math.Clamp(r.Float("airDamage", 1f), 0f, 5f),
                        StrikeTaken = Math.Clamp(r.Float("strikeTaken", 1f), 0f, 1f), StrikeCap = Math.Clamp(r.Float("strikeCap", 0f), 0f, 1f),
                        StrikeWindow = MathF.Max(1f, r.Float("strikeWindow", 10f)), StrikeOver = Math.Clamp(r.Float("strikeOver", 0.2f), 0f, 1f),
                    };
                }
            }
            BossRanks = ranks;
            foreach (var def in _vehicles.Values)
            {
                if (def.FrameId != null)
                {
                    if (!frames.TryGetValue(def.FrameId, out var frame)) throw new FormatException($"{def.Id}.frame: unknown body frame '{def.FrameId}'.");
                    def.Frame = frame;
                    if (frame.Move == BossMove.Spacecraft && def.Tiers == null) throw new FormatException($"{def.Id}: a spacecraft frame needs its altitude tiers.");
                    if (frame.Sea && def.Naval == null) throw new FormatException($"{def.Id}: a {frame.Id} frame sails the sea lanes (\"naval\").");
                    if (frame.Move == BossMove.Submarine && def.Burrow is not { Sea: true }) throw new FormatException($"{def.Id}: a submarine frame dives (\"burrow\" with \"sea\").");
                    if ((frame.Move is BossMove.Aircraft or BossMove.Spacecraft) != def.Flying) throw new FormatException($"{def.Id}: a {frame.Id} frame {(def.Flying ? "does not fly" : "flies")}.");
                }
                if (def.Boss)
                {
                    var key = def.Rank == BossRank.Mini ? "mini" : "main";
                    if (ranks.TryGetValue(key, out var rank)) def.RankDef = rank;
                }
                if (def.VariantOf != null)
                {
                    if (!_vehicles.TryGetValue(def.VariantOf, out var main) || !main.Boss) throw new FormatException($"{def.Id}.variantOf: '{def.VariantOf}' is no boss.");
                    main.MiniVariant ??= def.Id;
                }
                foreach (var m in def.WakeMounts)
                    if (m <= 0 || m >= def.Mounts.Count) throw new FormatException($"{def.Id}.wake.mounts: no secondary mount {m}.");
                if (def.Factory is { } factory)
                {
                    foreach (var list in factory.Units)
                        foreach (var id in list)
                            if (!_vehicles.ContainsKey(id)) throw new FormatException($"{def.Id}.factory.units: unknown vehicle '{id}'.");
                    foreach (var door in factory.Doors)
                        if (def.PartIndex(door) < 0) throw new FormatException($"{def.Id}.factory.doors: no part '{door}'.");
                }
            }
        }
    }
}

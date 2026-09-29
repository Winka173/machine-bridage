#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What an escort does for its boss (prompt 16 F): fights, or helps it.</summary>
    public enum EscortRole
    {
        /// <summary>Fights the units attacking the boss, never chasing past the leash.</summary>
        Guard,

        /// <summary>Repairs the boss while close to it (an engineer).</summary>
        Repair,

        /// <summary>Scrambles guided weapons round it (its def's jammer).</summary>
        Jam,

        /// <summary>Anti-air cover over the boss (a SAM, flak, fighters).</summary>
        Cover,

        /// <summary>Marks the enemies it sees: the boss's side hits them harder and the boss's guns more tightly.</summary>
        Spot,

        /// <summary>Smoke round the boss (its def's smoke skill).</summary>
        Smoke,

        /// <summary>A guard that dashes farther out at a target and comes back (a missile boat's run at the shore).</summary>
        Raid,
    }

    /// <summary>How a wave comes in.</summary>
    public enum EscortDrop
    {
        /// <summary>Beside the boss, in formation.</summary>
        Beside,

        /// <summary>Air-dropped round the boss after a warning (the transport and parachutes are drawn from the drop support).</summary>
        Para,

        /// <summary>From the map edge behind the boss, driving or flying in.</summary>
        Edge,

        /// <summary>Set down at its offset in the boss's frame (<see cref="EscortUnitDef.At"/>), like a boss's guards.</summary>
        Place,
    }

    /// <summary>Where an escort keeps station round its boss.</summary>
    public enum EscortSlot
    {
        /// <summary>Guards and raiders on the flanks, helpers behind.</summary>
        Auto,

        /// <summary>Beside the boss, along its heading (running parallel to a train's rails).</summary>
        Flank,

        /// <summary>Behind the boss, away from the enemy.</summary>
        Rear,

        /// <summary>Between the boss and the enemy.</summary>
        Screen,

        /// <summary>Ahead of the boss, along its heading.</summary>
        Front,
    }

    /// <summary>What sets off a boss's next escort wave after its arrival.</summary>
    public enum EscortTrigger
    {
        /// <summary>Each phase change: the boss's own phase marks, else the table's marks.</summary>
        Phase,

        /// <summary>Each time a boring boss breaks out of the ground (the Earth Worm).</summary>
        Surface,
    }

    /// <summary>One vehicle of an escort wave.</summary>
    public sealed class EscortUnitDef
    {
        public EscortUnitDef(string unit, EscortRole role)
        {
            Unit = Guard.Id(unit);
            Role = role;
        }

        /// <summary>The vehicle def (a base card goes out as its elite when the side's elite budget has room).</summary>
        public string Unit { get; }

        public EscortRole Role { get; }

        /// <summary>Always its elite version (a boss's signature elite).</summary>
        public bool Elite { get; internal set; }

        public EscortSlot Slot { get; internal set; }

        /// <summary>Its offset in the boss's frame (X right, Y forward), for <see cref="EscortDrop.Place"/>; null: the formation's.</summary>
        public Vector2? At { get; internal set; }

        /// <summary>It helps the boss rather than only fighting (every wave has at least one).</summary>
        public bool Helper => Role is not (EscortRole.Guard or EscortRole.Raid);
    }

    /// <summary>A group of escorts that comes in together: with the boss, or at a phase change.</summary>
    public sealed class EscortWaveDef
    {
        public IReadOnlyList<EscortUnitDef> Units { get; internal set; } = Array.Empty<EscortUnitDef>();

        public EscortDrop Drop { get; internal set; }

        /// <summary>The event support whose warning, transport and parachutes are drawn for a <see cref="EscortDrop.Para"/> drop.</summary>
        public string? Support { get; internal set; }

        /// <summary>The boss stops this long as the wave comes in (the Iron Train at a station); 0: it keeps going.</summary>
        public float Halt { get; internal set; }

        /// <summary>Only replaces what the boss has lost of this wave's vehicles (the Tempest's jammers).</summary>
        public bool Refill { get; internal set; }

        /// <summary>A radio line as the wave comes in (a text key), or null.</summary>
        public string? Radio { get; internal set; }
    }

    /// <summary>
    /// A boss's escorts (prompt 16 F, balance.json "escorts"): the wave that comes in with it, the waves at
    /// each phase change, and the leash they keep. The same for every boss, Leviathan's fleet included.
    /// </summary>
    public sealed class EscortDef
    {
        public EscortDef(string boss) => Boss = Guard.Id(boss);

        public string Boss { get; }

        /// <summary>The wave that arrives with the boss (null: none, the Earth Worm).</summary>
        public EscortWaveDef? Arrive { get; internal set; }

        /// <summary>The waves at the phase changes: the n-th change brings the n-th (the last repeats).</summary>
        public IReadOnlyList<EscortWaveDef> Phases { get; internal set; } = Array.Empty<EscortWaveDef>();

        /// <summary>Phase changes by health share, highest first, for a boss with no phases of its own (empty: the rules' default).</summary>
        public IReadOnlyList<float> Marks { get; internal set; } = Array.Empty<float>();

        public EscortTrigger On { get; internal set; }

        /// <summary>How far from the boss its escorts may go (0: the rules').</summary>
        public float Leash { get; internal set; }

        /// <summary>At most this many alive at once (0: the rules' cap by difficulty).</summary>
        public int Cap { get; internal set; }

        /// <summary>The wave for the <paramref name="n"/>-th phase change (0 up), or null.</summary>
        public EscortWaveDef? PhaseWave(int n) => Phases.Count == 0 ? null : Phases[Math.Min(n, Phases.Count - 1)];
    }

    /// <summary>The escort rules every boss shares (balance.json "escortRules").</summary>
    public sealed class EscortRules
    {
        internal Dictionary<string, int> Caps { get; } = new();

        /// <summary>How many escorts of a boss may be alive at once at a difficulty (Easy 4 ... Iron 6).</summary>
        public int CapFor(string? difficulty) =>
            difficulty != null && Caps.TryGetValue(difficulty, out var cap) ? cap : Caps.TryGetValue("Normal", out var normal) ? normal : 5;

        /// <summary>Boss Rush: this many fewer alive (at least <see cref="BossRushMin"/>), so a fight does not drag.</summary>
        public int BossRushCut { get; internal set; } = 2;

        public int BossRushMin { get; internal set; } = 3;

        /// <summary>Boss Rush: the share of each wave's guards that come (the helpers always do).</summary>
        public float BossRushGuards { get; internal set; } = 0.5f;

        public float Leash { get; internal set; } = 28f;

        /// <summary>CP for the side that destroys an escort (a helper pays <see cref="HelperBounty"/>).</summary>
        public float Bounty { get; internal set; } = 3f;

        public float HelperBounty { get; internal set; } = 4f;

        /// <summary>A repairing escort mends this share of the boss's full health a second.</summary>
        public float Repair { get; internal set; } = 0.003f;

        /// <summary>How far past the boss's hull a repairing escort reaches.</summary>
        public float RepairReach { get; internal set; } = 12f;

        /// <summary>A spotter's mark: the boss's side deals this much more to the marked.</summary>
        public float SpotBonus { get; internal set; } = 0.15f;

        /// <summary>A boss's guns scatter this much as widely at a marked target.</summary>
        public float SpotSpread { get; internal set; } = 0.6f;

        /// <summary>Phase marks for a boss with no phases of its own and none in its table.</summary>
        public IReadOnlyList<float> Marks { get; internal set; } = new[] { 0.5f };

        /// <summary>Seconds from a para drop's warning to the vehicles landing.</summary>
        public float DropWarn { get; internal set; } = 3f;
    }

    /// <summary>
    /// One battle's escort settings (the mode sets them; null on the world: no escorts, as in the bare
    /// test battles): the cap alive by difficulty, and Boss Rush's smaller waves.
    /// </summary>
    public sealed class EscortSettings
    {
        public int Cap { get; set; } = 5;

        /// <summary>The share of each wave's guards that come (the helpers always come).</summary>
        public float Guards { get; set; } = 1f;

        /// <summary>Guards always go out as their elite (Boss Rush's elite escorts).</summary>
        public bool EliteGuards { get; set; }

        /// <summary>The settings for a difficulty key (Easy .. VeryHard, Heroic, Iron), Boss Rush's or not.</summary>
        public static EscortSettings For(EscortRules rules, string? difficulty, bool bossRush = false)
        {
            var cap = rules.CapFor(difficulty);
            return bossRush
                ? new EscortSettings { Cap = Math.Max(rules.BossRushMin, cap - rules.BossRushCut), Guards = rules.BossRushGuards, EliteGuards = true }
                : new EscortSettings { Cap = cap };
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>Every boss's escort table, by boss id (prompt 16 F).</summary>
        public IReadOnlyDictionary<string, EscortDef> Escorts { get; internal set; } = new Dictionary<string, EscortDef>();

        public EscortRules EscortRules { get; internal set; } = new();

        /// <summary>balance.json "escortRules" and "escorts", checked against the vehicles and supports.</summary>
        private void ParseEscorts(JsonObject root)
        {
            if (root.Has("escortRules"))
            {
                var r = root.Object("escortRules");
                var rules = new EscortRules
                {
                    BossRushCut = r.Int("bossRushCut", 2), BossRushMin = r.Int("bossRushMin", 3),
                    BossRushGuards = Math.Clamp(r.Float("bossRushGuards", 0.5f), 0f, 1f), Leash = r.Float("leash", 28f),
                    Bounty = r.Float("bounty", 3f), HelperBounty = r.Float("helperBounty", 4f), Repair = r.Float("repair", 0.003f),
                    RepairReach = r.Float("repairReach", 12f), SpotBonus = r.Float("spotBonus", 0.15f),
                    SpotSpread = Math.Clamp(r.Float("spotSpread", 0.6f), 0.1f, 1f), DropWarn = r.Float("dropWarn", 3f),
                };
                if (r.Has("marks")) rules.Marks = Sorted(r.FloatArray("marks"));
                if (r.Has("cap"))
                {
                    var caps = r.Object("cap");
                    foreach (var key in caps.Keys) rules.Caps[key] = Math.Max(1, caps.Int(key, 5));
                }
                EscortRules = rules;
            }
            var escorts = new Dictionary<string, EscortDef>();
            // Prompt 20 E.4: the tables built on the generals' templates, and a boss with none given its general's.
            var bosses = new List<VehicleDef>();
            foreach (var v in _vehicles.Values)
                if (v.Boss) bosses.Add(v);
            foreach (var e in BossTemplates.Escorts(root, bosses))
            {
                var boss = e.String("boss");
                if (!_vehicles.TryGetValue(boss, out var bossDef) || !bossDef.Boss) throw new FormatException($"balance.escorts: '{boss}' is not a boss.");
                var def = new EscortDef(boss)
                {
                    Leash = e.Float("leash", 0f), Cap = e.Int("cap", 0), On = e.Enum("on", EscortTrigger.Phase),
                    Marks = e.Has("marks") ? Sorted(e.FloatArray("marks")) : Array.Empty<float>(),
                };
                if (e.Has("arrive")) def.Arrive = Wave(e, "arrive", boss);
                var phases = new List<EscortWaveDef>();
                if (e.Has("phase")) phases.Add(Wave(e, "phase", boss));
                foreach (var p in e.Array("phases")) phases.Add(Wave(p, null, boss));
                def.Phases = phases;
                // Prompt 20 G.4: a mini boss brings two or three (its rank's cap, each wave cut to it).
                if (bossDef.RankDef is { EscortCap: > 0 } rank)
                {
                    if (def.Cap == 0 || def.Cap > rank.EscortCap) def.Cap = rank.EscortCap;
                    if (def.Arrive != null) Cut(def.Arrive, rank.EscortCap);
                    foreach (var w in def.Phases) Cut(w, Math.Max(1, rank.EscortCap - 1));
                }
                escorts[boss] = def;
            }
            Escorts = escorts;
        }

        /// <summary>A wave cut to its first <paramref name="n"/> vehicles, a helper kept when there is one.</summary>
        private static void Cut(EscortWaveDef wave, int n)
        {
            if (wave.Units.Count <= n) return;
            var list = new List<EscortUnitDef>();
            for (var i = 0; i < n; i++) list.Add(wave.Units[i]);
            if (!list.Exists(u => u.Helper))
                foreach (var u in wave.Units)
                    if (u.Helper)
                    {
                        list[n - 1] = u;
                        break;
                    }
            wave.Units = list;
        }

        private static IReadOnlyList<float> Sorted(IReadOnlyList<float> marks)
        {
            var list = new List<float>(marks);
            list.Sort((a, b) => b.CompareTo(a));
            return list;
        }

        /// <summary>A wave: an array of units, or an object with "units", "drop", "support", "halt", "refill", "radio".</summary>
        private EscortWaveDef Wave(JsonObject owner, string? key, string boss)
        {
            // A list of units, or an object with them (JsonObject is a struct: a flag says which).
            var listed = key != null && owner.IsArray(key);
            var o = key == null ? owner : listed ? owner : owner.Object(key);
            var units = new List<EscortUnitDef>();
            foreach (var u in listed ? owner.Array(key!) : o.Array("units"))
            {
                var id = u.String("unit");
                if (!_vehicles.TryGetValue(id, out var vehicle)) throw new FormatException($"balance.escorts.{boss}: unknown vehicle '{id}'.");
                var role = u.Enum("role", EscortRole.Guard);
                if (role == EscortRole.Jam && vehicle.Jammer <= 0f) throw new FormatException($"balance.escorts.{boss}: '{id}' has no jammer to jam with.");
                var unit = Wrap(u, () => new EscortUnitDef(id, role));
                unit.Elite = u.Bool("elite", false);
                unit.Slot = u.Enum("slot", EscortSlot.Auto);
                if (u.Has("at"))
                {
                    var at = u.FloatArray("at");
                    unit.At = new Vector2(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f);
                }
                var count = Math.Max(1, u.Int("count", 1));
                for (var k = 0; k < count; k++) units.Add(unit);
            }
            var wave = new EscortWaveDef { Units = units };
            if (listed) return wave;
            wave.Drop = o.Enum("drop", EscortDrop.Beside);
            wave.Halt = MathF.Max(0f, o.Float("halt", 0f));
            wave.Refill = o.Bool("refill", false);
            if (o.Has("radio")) wave.Radio = o.String("radio");
            if (o.Has("support"))
            {
                wave.Support = o.String("support");
                if (!_supports.ContainsKey(wave.Support)) throw new FormatException($"balance.escorts.{boss}: unknown support '{wave.Support}'.");
            }
            return wave;
        }
    }
}

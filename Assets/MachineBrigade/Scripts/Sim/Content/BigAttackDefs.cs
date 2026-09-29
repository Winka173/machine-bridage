#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 18 (DECISIONS 17A): the shapes a big attack's strike takes, a shared library (prompt 20 E.3 adds to
    /// it): shells or bombs over a circle, a strip or walking down a line; a piercing line; a beam sweeping a line;
    /// a drone swarm; missiles that can be shot down in flight; a landing party; a boost to the boss's side; the
    /// Earth Worm's quake (its dive, run by the burrow).
    /// </summary>
    public enum BigShape
    {
        Circle,
        Strip,
        Line,
        Sweep,
        Swarm,
        Missile,
        Drop,
        Buff,
        Quake,

        /// <summary>Prompt 19 F: rods from orbit, one on each of the other side's densest groups (the heaviest armour first), each its own ring.</summary>
        Rods,

        /// <summary>Prompt 20 J.1: a swing round the boss's front (Kronos's bucket wheel): everything within "radius" m and "width" degrees of its heading.</summary>
        Arc,

        /// <summary>Prompt 20 J.2: the boss itself charges down a warned line (Ixion): "length" m in "duration" s, everything within "width" hit once and stunned.</summary>
        Charge,
    }

    /// <summary>Where a big attack is laid: the enemy's biggest group (towers count), the biggest group standing still, the HQ (else the biggest group), the base's HQ and towers, or round the boss.</summary>
    public enum BigAim
    {
        Group,
        Still,
        Hq,
        Base,
        Self,
    }

    /// <summary>How a strip or a line lies: along the boss's heading (a train's rails, an airship's course), from the boss towards the aim, or across that.</summary>
    public enum BigAxis
    {
        Heading,
        Toward,
        Across,
    }

    /// <summary>Ground left burning after a strike: seconds, damage a second, radius.</summary>
    public sealed class BigFireDef
    {
        public float Seconds { get; internal set; } = 8f;
        public float Dps { get; internal set; } = 30f;
        public float Radius { get; internal set; } = 8f;
    }

    /// <summary>
    /// One strike of a big attack: a shape template and its numbers. Its parts carry it: with every one of them
    /// broken the strike is lost (cancelled if they break during the warning, gone until a self-repair puts one
    /// back); with <see cref="PerPart"/> each standing part brings that many rounds. Damage is before armour, on
    /// the calibre scale, and scales with the boss (campaign, difficulty).
    /// </summary>
    public sealed class BigStrikeDef
    {
        public BigShape Shape { get; internal set; }

        /// <summary>Ids of the boss's parts that carry it (empty: the boss itself).</summary>
        public IReadOnlyList<string> Parts { get; internal set; } = Array.Empty<string>();

        /// <summary>Rounds each standing part brings (0: <see cref="Count"/> in all while any stands).</summary>
        public int PerPart { get; internal set; }

        public int Count { get; internal set; } = 1;

        /// <summary>Rounds that land together (a pair of shells, a 40 mm burst of three).</summary>
        public int Salvo { get; internal set; } = 1;

        public float Damage { get; internal set; }
        public DamageType Type { get; internal set; } = DamageType.HighExplosive;

        /// <summary>Penetration level (a blast's fragments pierce as level 1 at most against vehicles, prompt 15 B.1).</summary>
        public int Pen { get; internal set; } = 1;

        /// <summary>It comes down on the roof (a drone, a bomb): blasts always do.</summary>
        public bool Top { get; internal set; }

        public bool Thermo { get; internal set; }

        /// <summary>Damage to structures (towers, gates, buildings) is multiplied by this.</summary>
        public float Structure { get; internal set; } = 1f;

        /// <summary>Each blast's radius (a line's and a sweep's half-width is <see cref="Width"/>).</summary>
        public float Radius { get; internal set; } = 5f;

        /// <summary>The share of the damage left at a blast's rim.</summary>
        public float Falloff { get; internal set; } = 0.25f;

        /// <summary>A circle's rounds fall within this radius of the aim (0: on it).</summary>
        public float Area { get; internal set; }

        /// <summary>A single round's scatter round the aim.</summary>
        public float Scatter { get; internal set; }

        public float Length { get; internal set; }
        public float Width { get; internal set; }
        public BigAxis Axis { get; internal set; } = BigAxis.Toward;

        /// <summary>Seconds the rounds take to land after it fires (a sweep's run).</summary>
        public float Duration { get; internal set; }

        /// <summary>A walking barrage: each round this long after the one before, in order down the line.</summary>
        public float Interval { get; internal set; }

        /// <summary>Continuous fire: a salvo this often for <see cref="Duration"/>.</summary>
        public float Every { get; internal set; }

        /// <summary>A piercing line: each unit beyond the first takes this share less than the one before.</summary>
        public float ChainCut { get; internal set; }

        /// <summary>A missile's or drone's health in flight (anti-air, C-RAM, point-defence lasers and APS shoot it down).</summary>
        public float Hp { get; internal set; }

        /// <summary>A drone's speed (m/s); a missile flies <see cref="Flight"/> seconds.</summary>
        public float Speed { get; internal set; } = 26f;

        public float Flight { get; internal set; } = 8f;

        /// <summary>A swarm's or a volley's distinct targets at most.</summary>
        public int Targets { get; internal set; } = 4;

        /// <summary>The weapon whose look it takes (its round, its flash); null: the part's own first mount.</summary>
        public string? Weapon { get; internal set; }

        /// <summary>A support whose aircraft flies over as it lands (the look only).</summary>
        public string? Pass { get; internal set; }

        public BigFireDef? Fire { get; internal set; }

        /// <summary>Seconds it stuns the ground vehicles it hits (the quake).</summary>
        public float Stun { get; internal set; }

        /// <summary>Round the boss: each part covers its own half (its side of the hull).</summary>
        public bool Sectors { get; internal set; }

        /// <summary>A landing party's vehicles, at most <see cref="Max"/> of them alive at once, set down at <see cref="At"/> (the boss's frame).</summary>
        public IReadOnlyList<string> Units { get; internal set; } = Array.Empty<string>();

        public int Max { get; internal set; } = 6;
        public Vector2 At { get; internal set; }

        /// <summary>
        /// Prompt 20 E.3: rounds lost once any part carrying it is broken: the share left (Daedalus's six pods fall as three
        /// with a bay gone; 0: a broken part stops it outright, Ixion's wheel); negative: the ordinary rule (every part).
        /// </summary>
        public float Cut { get; internal set; } = -1f;

        /// <summary>Prompt 20 E.3 (spawning troops): each round of a circle sets down this many of <see cref="Units"/> where it lands (Daedalus's pods).</summary>
        public int Seats { get; internal set; }

        /// <summary>A boost to the boss's side within <see cref="Reach"/>: damage and fire rate shares, for <see cref="Seconds"/>.</summary>
        public float Reach { get; internal set; }

        public float FireRate { get; internal set; }
        public float Seconds { get; internal set; }

        /// <summary>Its rounds at full strength (every part standing).</summary>
        public int FullCount => PerPart > 0 ? PerPart * Math.Max(1, Parts.Count) : Every > 0f ? (int)MathF.Floor(Duration / Every + 1e-3f) * Math.Max(1, Salvo) : Count;

        /// <summary>Its damage before armour at full strength (every round landing on one target), for the guide and the combat value.</summary>
        public float FullDamage => Shape is BigShape.Drop or BigShape.Buff ? 0f : Damage * (Shape is BigShape.Arc or BigShape.Charge ? 1 : FullCount);

        /// <summary>It hurts where it lands (not a landing party, not a boost): units dodge it.</summary>
        public bool Harmful => Shape is not (BigShape.Drop or BigShape.Buff or BigShape.Swarm);
    }

    /// <summary>
    /// A big attack (prompt 18): data in balance.json "bigAttacks", one per boss by its "bigAttack" id, so a boss can
    /// swap its attack for another entry (prompt 19 F) and a mini boss can scale one (prompt 20 G). Damage, cooldown
    /// and warning are separate scalable fields (<see cref="BigAttackScale"/>). Its name and lines are text keys
    /// derived from the id ("bigattack.&lt;id&gt;" and so on): nothing to show is in the data.
    /// </summary>
    public sealed class BigAttackDef
    {
        public BigAttackDef(string id) => Id = Guard.Id(id);

        public string Id { get; }

        /// <summary>The HUD icon on the boss bar.</summary>
        public string Icon { get; internal set; } = "bolt";

        /// <summary>Seconds of warning before it lands (the zones shown, the parts charging).</summary>
        public float Warn { get; internal set; } = 3.5f;

        /// <summary>Seconds from one attack's start to the next.</summary>
        public float Cooldown { get; internal set; } = 60f;

        /// <summary>Seconds after the boss appears for the first one; null: the rules' (about 30).</summary>
        public float? First { get; internal set; }

        public BigAim Aim { get; internal set; } = BigAim.Group;

        /// <summary>How far from the boss it reaches (0: the whole map).</summary>
        public float Reach { get; internal set; }

        /// <summary>Who it is meant for (a guide key: "light", "heavy", "base" ...).</summary>
        public string Target { get; internal set; } = "mixed";

        /// <summary>Seconds an EMP on the boss adds to its charge (0: none).</summary>
        public float EmpDelay { get; internal set; }

        /// <summary>The boss takes this many times the damage from the warning to the end (flying low and slow, bomb doors open).</summary>
        public float Exposed { get; internal set; } = 1f;

        /// <summary>A share of the boss's full health taken while it fires makes it break off (0: never).</summary>
        public float AbortDamage { get; internal set; }

        /// <summary>A part that aims it (the supergun's fire control): broken, a single round falls within <see cref="BlindScatter"/> m.</summary>
        public string? Spotter { get; internal set; }

        public float BlindScatter { get; internal set; }

        /// <summary>Boss mechanisms held while it charges (the supergun's ordinary shots, the Leviathan's single cruise missiles).</summary>
        public IReadOnlyList<string> Hold { get; internal set; } = Array.Empty<string>();

        /// <summary>The boss stops for the warning (a bomber over its target).</summary>
        public bool Halt { get; internal set; }

        /// <summary>Prompt 20 J.4: a diving boss comes up to launch (Typhon): only the parts carrying it show above the water until it fires.</summary>
        public bool Surface { get; internal set; }

        public IReadOnlyList<BigStrikeDef> Strikes { get; internal set; } = Array.Empty<BigStrikeDef>();

        /// <summary>Its name's text key.</summary>
        public string NameKey => "bigattack." + Id;

        /// <summary>The radio line as it begins (the boss's general where it has one).</summary>
        public string RadioKey => "radio.bigattack." + Id;

        /// <summary>The short notice when the player cancels it.</summary>
        public string CancelledKey => "bigattack." + Id + ".cancelled";

        /// <summary>The guide's lines: how it works, how to get out of it, how to stop it.</summary>
        public string GuideKey(string line) => "guide.bigattack." + Id + "." + line;

        /// <summary>A part of the boss carries it.</summary>
        public bool UsesPart(string partId)
        {
            foreach (var s in Strikes)
                foreach (var p in s.Parts)
                    if (p == partId) return true;
            return false;
        }

        /// <summary>Its damage before armour at full strength, all strikes.</summary>
        public float FullDamage
        {
            get
            {
                var sum = 0f;
                foreach (var s in Strikes) sum += s.FullDamage;
                return sum;
            }
        }

        /// <summary>Its damage a second over its cooldown on paper (the combat value, prompt 13 A).</summary>
        public float Sustained => FullDamage / MathF.Max(1f, Cooldown);
    }

    /// <summary>A big attack's scaling (a difficulty, a mini boss): damage and cooldown multipliers and seconds added to the warning.</summary>
    public readonly struct BigAttackScale
    {
        public BigAttackScale(float damage, float cooldown, float warn)
        {
            Damage = damage;
            Cooldown = cooldown;
            Warn = warn;
        }

        public float Damage { get; }
        public float Cooldown { get; }
        public float Warn { get; }

        public static BigAttackScale One => new(1f, 1f, 0f);

        public BigAttackScale Then(BigAttackScale other) => new(Damage * other.Damage, Cooldown * other.Cooldown, Warn + other.Warn);
    }

    /// <summary>balance.json "bigAttackRules".</summary>
    public sealed class BigAttackRules
    {
        /// <summary>Seconds after a boss appears for its first big attack.</summary>
        public float First { get; internal set; } = 30f;

        /// <summary>What one interceptor (APS, C-RAM, point-defence laser) takes off a missile or drone in flight.</summary>
        public float Intercept { get; internal set; } = 150f;

        /// <summary>The share of an anti-air gun's paper damage a second that hits a missile or drone in its reach.</summary>
        public float AaHit { get; internal set; } = 0.5f;

        /// <summary>Metres past a warning's edge a unit dodging it goes to.</summary>
        public float Dodge { get; internal set; } = 3f;

        public Dictionary<string, BigAttackScale> Difficulty { get; } = new();

        public BigAttackScale For(string? difficulty) =>
            difficulty != null && Difficulty.TryGetValue(difficulty, out var s) ? s : Difficulty.TryGetValue("Normal", out var n) ? n : BigAttackScale.One;
    }

    /// <summary>One battle's big-attack settings (the modes set them by difficulty; null on the world: no big attacks, as in the bare test battles).</summary>
    public sealed class BigAttackSettings
    {
        public BigAttackScale Scale { get; set; } = BigAttackScale.One;

        /// <summary>Prompt 19 E.6: the battle's difficulty key (the drone seizure is only at the hardest).</summary>
        public string? Difficulty { get; set; }

        public static BigAttackSettings For(BigAttackRules rules, string? difficulty) => new() { Scale = rules.For(difficulty), Difficulty = difficulty };
    }

    public sealed partial class Catalog
    {
        /// <summary>The big-attack library by id (prompt 18).</summary>
        public IReadOnlyDictionary<string, BigAttackDef> BigAttacks { get; internal set; } = new Dictionary<string, BigAttackDef>();

        public BigAttackRules BigAttackRules { get; internal set; } = new();

        /// <summary>balance.json "bigAttackRules" and "bigAttacks", and every boss's "bigAttack" checked against them.</summary>
        private void ParseBigAttacks(JsonObject root)
        {
            var rules = new BigAttackRules();
            if (root.Has("bigAttackRules"))
            {
                var r = root.Object("bigAttackRules");
                rules.First = MathF.Max(0f, r.Float("first", 30f));
                rules.Intercept = MathF.Max(0f, r.Float("intercept", 150f));
                rules.AaHit = Math.Clamp(r.Float("aaHit", 0.5f), 0f, 1f);
                rules.Dodge = MathF.Max(0f, r.Float("dodge", 3f));
                if (r.Has("difficulty"))
                {
                    var d = r.Object("difficulty");
                    foreach (var key in d.Keys)
                    {
                        var o = d.Object(key);
                        rules.Difficulty[key] = new BigAttackScale(MathF.Max(0f, o.Float("damage", 1f)), MathF.Max(0.1f, o.Float("cooldown", 1f)), o.Float("warn", 0f));
                    }
                }
            }
            BigAttackRules = rules;
            var attacks = new Dictionary<string, BigAttackDef>();
            foreach (var a in BossTemplates.BigAttacks(root))
            {
                var def = Wrap(a, () => new BigAttackDef(a.String("id")));
                if (attacks.ContainsKey(def.Id)) throw new FormatException($"balance.bigAttacks: '{def.Id}' twice.");
                def.Icon = a.Has("icon") ? a.String("icon") : def.Icon;
                def.Warn = MathF.Max(0.5f, a.Float("warn", 3.5f));
                def.Cooldown = MathF.Max(def.Warn + 1f, a.Float("cooldown", 60f));
                if (a.Has("first")) def.First = MathF.Max(0f, a.Float("first", 30f));
                def.Aim = a.Enum("aim", BigAim.Group);
                def.Reach = MathF.Max(0f, a.Float("reach", 0f));
                if (a.Has("target")) def.Target = a.String("target");
                def.EmpDelay = MathF.Max(0f, a.Float("empDelay", 0f));
                def.Exposed = MathF.Max(1f, a.Float("exposed", 1f));
                def.AbortDamage = Math.Clamp(a.Float("abortDamage", 0f), 0f, 1f);
                if (a.Has("spotter")) def.Spotter = a.String("spotter");
                def.BlindScatter = MathF.Max(0f, a.Float("blindScatter", 0f));
                if (a.Has("hold")) def.Hold = a.StringArray("hold");
                def.Halt = a.Bool("halt", false);
                def.Surface = a.Bool("surface", false);
                var strikes = new List<BigStrikeDef>();
                foreach (var s in a.Array("strikes")) strikes.Add(Wrap(s, () => ParseStrike(s)));
                if (strikes.Count == 0) throw new FormatException($"balance.bigAttacks.{def.Id}: no strikes.");
                def.Strikes = strikes;
                attacks[def.Id] = def;
            }
            BigAttacks = attacks;
            foreach (var v in _vehicles.Values)
            {
                if (v.BigAttackId == null) continue;
                if (!attacks.TryGetValue(v.BigAttackId, out var attack)) throw new FormatException($"{v.Id}.bigAttack: unknown big attack '{v.BigAttackId}'.");
                foreach (var s in attack.Strikes)
                {
                    foreach (var p in s.Parts)
                        if (v.PartIndex(p) < 0) throw new FormatException($"{v.Id}.bigAttack {attack.Id}: the boss has no part '{p}'.");
                    if (s.Weapon != null && !_weapons.ContainsKey(s.Weapon)) throw new FormatException($"balance.bigAttacks.{attack.Id}: unknown weapon '{s.Weapon}'.");
                    if (s.Pass != null && !_supports.ContainsKey(s.Pass)) throw new FormatException($"balance.bigAttacks.{attack.Id}: unknown support '{s.Pass}'.");
                    foreach (var u in s.Units)
                        if (!_vehicles.ContainsKey(u)) throw new FormatException($"balance.bigAttacks.{attack.Id}: unknown vehicle '{u}'.");
                    if (s.Shape == BigShape.Quake && v.Burrow == null) throw new FormatException($"{v.Id}.bigAttack {attack.Id}: a quake needs a boring boss.");
                }
                if (attack.Spotter != null && v.PartIndex(attack.Spotter) < 0) throw new FormatException($"{v.Id}.bigAttack {attack.Id}: no spotter part '{attack.Spotter}'.");
                v.BigAttack = attack;
            }
        }

        private static BigStrikeDef ParseStrike(JsonObject s)
        {
            var strike = new BigStrikeDef
            {
                Shape = s.Enum<BigShape>("shape"),
                Parts = s.Has("parts") ? s.StringArray("parts") : Array.Empty<string>(),
                PerPart = Math.Max(0, s.Int("perPart", 0)),
                Count = Math.Max(1, s.Int("count", 1)),
                Salvo = Math.Max(1, s.Int("salvo", 1)),
                Damage = MathF.Max(0f, s.Float("damage", 0f)),
                Type = s.Enum("type", DamageType.HighExplosive),
                Pen = Math.Clamp(s.Int("pen", 1), 0, ArmourLevels.Max),
                Top = s.Bool("top", false),
                Thermo = s.Bool("thermo", false),
                Structure = MathF.Max(0f, s.Float("structure", 1f)),
                Radius = MathF.Max(0.5f, s.Float("radius", 5f)),
                Falloff = Math.Clamp(s.Float("falloff", 0.25f), 0f, 1f),
                Area = MathF.Max(0f, s.Float("area", 0f)),
                Scatter = MathF.Max(0f, s.Float("scatter", 0f)),
                Length = MathF.Max(0f, s.Float("length", 0f)),
                Width = MathF.Max(0f, s.Float("width", 0f)),
                Axis = s.Enum("axis", BigAxis.Toward),
                Duration = MathF.Max(0f, s.Float("duration", 0f)),
                Interval = MathF.Max(0f, s.Float("interval", 0f)),
                Every = MathF.Max(0f, s.Float("every", 0f)),
                ChainCut = Math.Clamp(s.Float("chainCut", 0f), 0f, 1f),
                Hp = MathF.Max(0f, s.Float("hp", 0f)),
                Speed = MathF.Max(1f, s.Float("speed", 26f)),
                Flight = MathF.Max(0.5f, s.Float("flight", 8f)),
                Targets = Math.Max(1, s.Int("targets", 4)),
                Weapon = s.Has("weapon") ? s.String("weapon") : null,
                Pass = s.Has("pass") ? s.String("pass") : null,
                Stun = MathF.Max(0f, s.Float("stun", 0f)),
                Sectors = s.Bool("sectors", false),
                Units = s.Has("units") ? s.StringArray("units") : Array.Empty<string>(),
                Max = Math.Max(1, s.Int("max", 6)),
                Reach = MathF.Max(0f, s.Float("reach", 0f)),
                FireRate = MathF.Max(0f, s.Float("fireRate", 0f)),
                Seconds = MathF.Max(0f, s.Float("seconds", 0f)),
                Cut = s.Has("cut") ? Math.Clamp(s.Float("cut", 0.5f), 0f, 1f) : -1f,
                Seats = Math.Max(0, s.Int("seats", 0)),
            };
            if (s.Has("at"))
            {
                var at = s.FloatArray("at");
                strike.At = new Vector2(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f);
            }
            if (s.Has("fire"))
            {
                var f = s.Object("fire");
                strike.Fire = new BigFireDef
                {
                    Seconds = MathF.Max(0.5f, f.Float("seconds", 8f)), Dps = MathF.Max(0f, f.Float("dps", 30f)), Radius = MathF.Max(0.5f, f.Float("radius", 8f)),
                };
            }
            if (strike.Shape == BigShape.Drop && strike.Units.Count == 0) throw new FormatException($"{s.Path}: a landing party needs units.");
            if (strike.Shape is BigShape.Line or BigShape.Sweep or BigShape.Strip && strike.Length <= 0f) throw new FormatException($"{s.Path}: a {strike.Shape} needs a length.");
            if (strike.Shape == BigShape.Charge && (strike.Length <= 0f || strike.Duration <= 0f)) throw new FormatException($"{s.Path}: a charge needs a length and a duration.");
            if (strike.Shape == BigShape.Arc && strike.Width <= 0f) throw new FormatException($"{s.Path}: an arc needs its width in degrees.");
            if (strike.Seats > 0 && strike.Units.Count == 0) throw new FormatException($"{s.Path}: seats need units.");
            return strike;
        }
    }
}

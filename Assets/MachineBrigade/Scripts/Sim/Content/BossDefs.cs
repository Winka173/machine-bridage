#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// One part of a multi-part boss (an engine, a hangar, a radar, a gun): its own health, where it
    /// sits on the model, and the weapon mounts and skills it carries. Only rounds that strike the part
    /// hurt it (a blast lands on the body); once it breaks, its mounts fall silent, its skills stop and
    /// its penalties apply to the boss. Data: a boss's "parts" list in balance.json.
    /// </summary>
    public sealed class BossPartDef
    {
        public BossPartDef(string id, string kind, float hp)
        {
            Id = Guard.Id(id);
            Kind = string.IsNullOrWhiteSpace(kind) ? "part" : kind;
            Hp = hp > 0f && hp < 10f ? hp : throw new ArgumentException($"Boss part '{id}': hp is a share of the body's health (0 to 10).");
        }

        public string Id { get; }

        /// <summary>What it is (engine, hangar, radar, gun, drill, fan, ramp, antenna, tractor, station): what a lock counts and what the view shows.</summary>
        public string Kind { get; }

        /// <summary>Its health as a share of the body's full health (so campaign scaling and difficulty scale it with the boss).</summary>
        public float Hp { get; }

        /// <summary>
        /// Prompt 15 A.5: its own armour level, the same all round (data "armour"; -1 until set: the boss's
        /// front). A gun mantlet is thick, a radar or an antenna thin.
        /// </summary>
        public int Armour { get; internal set; } = -1;

        /// <summary>Its armour level on <paramref name="boss"/>: its own, else the boss's front.</summary>
        public int ArmourOn(VehicleDef boss) => Armour >= 0 ? Armour : boss.Armour.Front;

        /// <summary>The model node it is (Part_engine.001): the view hides it and puts a wreck piece in at its origin.</summary>
        public string? Node { get; internal set; }

        /// <summary>The broken piece the view puts in its place (wreck_engine); null hides it and leaves a charred stump.</summary>
        public string? Wreck { get; internal set; }

        /// <summary>Where it sits in the boss's frame, in metres: X to the right, Y forward, Height up (rounds fly to it, effects start there).</summary>
        public Vector2 At { get; internal set; }

        public float Height { get; internal set; }

        /// <summary>How close to its centre a round must land to strike it.</summary>
        public float Radius { get; internal set; } = 2f;

        /// <summary>Indices of the boss's weapon mounts it carries (0 the main weapon): they never fire once it breaks.</summary>
        public IReadOnlyList<int> Mounts { get; internal set; } = Array.Empty<int>();

        /// <summary>Ids of the boss's skills it drives: they are never used once it breaks.</summary>
        public IReadOnlyList<string> Skills { get; internal set; } = Array.Empty<string>();

        /// <summary>The boss's speed is multiplied by this once it breaks (an engine: 0.85).</summary>
        public float Speed { get; internal set; } = 1f;

        /// <summary>The spread of <see cref="Affects"/> is multiplied by this once it breaks (a fire-control radar: 3).</summary>
        public float Spread { get; internal set; } = 1f;

        /// <summary>Share of the guided rounds of <see cref="Affects"/> that lose lock once it breaks.</summary>
        public float Fail { get; internal set; }

        /// <summary>The mounts its <see cref="Spread"/> and <see cref="Fail"/> touch (empty: every mount).</summary>
        public IReadOnlyList<int> Affects { get; internal set; } = Array.Empty<int>();

        /// <summary>Share of its own full health the body loses when it breaks (prompt 9: 0.3; the airship's parts 0).</summary>
        public float BreakDamage { get; internal set; } = 0.3f;

        /// <summary>
        /// Boss mechanisms it drives, stopped once it breaks (see <see cref="Mechanisms"/>): "bombard"
        /// (the supergun's shot), "spotter" (the shot's fire control: it falls wide), "burrow" (the
        /// Earth Worm's dives), "landing" (the hovercraft's troops), "aura" (the Supreme Commander's
        /// command aura); prompt 16: "aps" (its protection system: the interceptors shrink with each part
        /// carrying it broken, and stop with the last), "jammer" (its jamming aura) and "trail" (the
        /// Inferno's fire trail), each stopped once every part carrying it is broken; the ships' "cruise" (the
        /// launch cells), "craft" (the well deck's landing craft) and "radar" (fire control: salvos and cruise
        /// missiles fall wide, the CIWS misses now and then).
        /// </summary>
        public IReadOnlyList<string> Stops { get; internal set; } = Array.Empty<string>();

        /// <summary>The boss turns (hull and turret) this many times as fast once it breaks (a tail rotor: 0.5).</summary>
        public float Turn { get; internal set; } = 1f;

        /// <summary>Its mechanisms' intervals (the bombard, the landings) are this many times as long once it breaks (a tractor: 1.3).</summary>
        public float Cadence { get; internal set; } = 1f;

        /// <summary>A radio line when it breaks (an important part: a main gun, a shield generator, a drone bay, a locomotive).</summary>
        public string? Radio { get; internal set; }

        /// <summary>How it breaks in the view: "blast" (guns and ammunition: a big blast and debris), "energy" (a flash and arcs), "engine" (fire and a smoke trail).</summary>
        public string Fx { get; internal set; } = "blast";

        /// <summary>The attached model it is (an index into the boss's "attach": the supergun's tractors), or -1.</summary>
        public int Attachment { get; internal set; } = -1;

        /// <summary>The mechanism names <see cref="Stops"/> may hold.</summary>
        public static readonly string[] Mechanisms =
        {
            "bombard", "spotter", "burrow", "landing", "aura", "aps", "jammer", "trail", "cruise", "craft", "radar", "thrust", "pods",
            // Prompt 20: Moloch's workshop doors (each standing one builds), a crusher (Kronos's bucket wheel), Argus's fire direction.
            "factory", "crush", "spotaura",
        };

        /// <summary>The view's default <see cref="Fx"/> for a kind of part.</summary>
        public static string FxFor(string kind) => kind switch
        {
            "engine" or "fan" or "rotor" or "locomotive" or "tractor" => "engine",
            "shield" or "laser" or "coilgun" or "railgun" or "emp" => "energy",
            _ => "blast",
        };
    }

    /// <summary>The body takes no damage until <see cref="Count"/> parts of <see cref="Kind"/> have broken (the command airship's engines).</summary>
    public sealed class PartLockDef
    {
        public PartLockDef(string kind, int count)
        {
            Kind = Guard.Id(kind);
            Count = count >= 1 ? count : throw new ArgumentException("partLock: count must be at least 1.");
        }

        public string Kind { get; }
        public int Count { get; }
    }

    /// <summary>
    /// A boring boss (the Earth Worm): it fights on the surface for <see cref="Surface"/> seconds, dives
    /// (<see cref="Dive"/> s), bores underground (untouchable, unseen) at <see cref="Speed"/> m/s to
    /// under the enemy's biggest group of ground vehicles, cracks the ground there for
    /// <see cref="Warn"/> s and breaks out: a quake of <see cref="Damage"/> that stuns ground
    /// vehicles within <see cref="Radius"/> m for <see cref="Stun"/> s. For <see cref="Exposed"/> s
    /// after it surfaces it takes <see cref="ExposedTaken"/> times the damage.
    /// </summary>
    public sealed class BurrowDef
    {
        public float Surface { get; internal set; } = 20f;
        public float Dive { get; internal set; } = 2f;
        public float Speed { get; internal set; } = 14f;
        public float Warn { get; internal set; } = 2f;
        public float Radius { get; internal set; } = 15f;
        public float Stun { get; internal set; } = 3f;
        public float Damage { get; internal set; } = 300f;
        public float Exposed { get; internal set; } = 6f;
        public float ExposedTaken { get; internal set; } = 1.5f;

        /// <summary>Its first dive waits this long after it arrives.</summary>
        public float First { get; internal set; } = 12f;

        /// <summary>
        /// Prompt 20 J.4: a submarine (Typhon) dives on the sea instead: it goes under on its schedule (not for a
        /// group), stays down at least <see cref="Under"/> s while it runs to another point of its lane, and the
        /// water boils (the warning) before it surfaces there; no quake unless it has <see cref="Damage"/>.
        /// </summary>
        public bool Sea { get; internal set; }

        public float Under { get; internal set; }

        /// <summary>A phase's surface and submerged seconds (the last holds after; empty: <see cref="Surface"/>, <see cref="Under"/>).</summary>
        public IReadOnlyList<float> SurfaceByPhase { get; internal set; } = Array.Empty<float>();

        public IReadOnlyList<float> UnderByPhase { get; internal set; } = Array.Empty<float>();

        /// <summary>From this phase (0 up) it no longer dives (-1: never).</summary>
        public int StopPhase { get; internal set; } = -1;

        public float SurfaceIn(int phase) => SurfaceByPhase.Count == 0 ? Surface : SurfaceByPhase[Math.Clamp(phase, 0, SurfaceByPhase.Count - 1)];

        public float UnderIn(int phase) => UnderByPhase.Count == 0 ? Under : UnderByPhase[Math.Clamp(phase, 0, UnderByPhase.Count - 1)];
    }

    /// <summary>
    /// A landing craft boss: every <see cref="Every"/> seconds it stops for <see cref="Stop"/> s, lowers
    /// its ramp and lands <see cref="Min"/> to <see cref="Max"/> vehicles drawn from <see cref="Units"/>,
    /// at most <see cref="Landings"/> times.
    /// </summary>
    public sealed class LandingDef
    {
        public float Every { get; internal set; } = 40f;
        public float Stop { get; internal set; } = 6f;
        public int Min { get; internal set; } = 3;
        public int Max { get; internal set; } = 4;
        public int Landings { get; internal set; } = 4;
        public float First { get; internal set; } = 20f;
        public IReadOnlyList<string> Units { get; internal set; } = Array.Empty<string>();

        /// <summary>Where they drive off, in the boss's frame (X right, Y forward).</summary>
        public Vector2 Ramp { get; internal set; } = new(0f, 10f);
    }

    /// <summary>
    /// A super-heavy gun's shot (the rail supergun): every <see cref="Every"/> seconds one shell at the
    /// enemy's biggest group of ground vehicles anywhere on the map, its landing marked
    /// <see cref="Warn"/> seconds ahead: a blast of <see cref="Damage"/> over <see cref="Radius"/> m,
    /// landing within <see cref="Scatter"/> m of the mark (times <see cref="BlindScatter"/> once its
    /// <see cref="Spotter"/> is gone).
    /// </summary>
    public sealed class BombardDef
    {
        public float Every { get; internal set; } = 20f;
        public float Warn { get; internal set; } = 3f;
        public float Damage { get; internal set; } = 1400f;
        public float Radius { get; internal set; } = 14f;
        public float Scatter { get; internal set; } = 3f;
        public float BlindScatter { get; internal set; } = 2.5f;
        public float First { get; internal set; } = 10f;

        /// <summary>
        /// Prompt 26 D.2 (Gungnir's electromagnetic shot): the slug goes through at most this many enemy ground vehicles on the line
        /// from the gun to the aim (the nearest first, each takes <see cref="PierceDamage"/>), and the blast lands on the last one hit;
        /// 0: a plain shell on the aim.
        /// </summary>
        public int PierceMax { get; internal set; }

        /// <summary>The damage the slug does to each vehicle it goes through (see <see cref="PierceMax"/>).</summary>
        public float PierceDamage { get; internal set; }

        /// <summary>The fire-control post that aims it (a guard's def id), or null.</summary>
        public string? Spotter { get; internal set; }

        /// <summary>
        /// The weapon drawn firing (its muzzle flash and the shell's flight). Prompt 25 C2 (DECISIONS 25C): it is the
        /// boss's gun (the supergun's main weapon, laid by this shot): with no "damage", "radius" or "every" of the
        /// bombard's own, the shell's damage, blast and cycle are the weapon's (damage, splash, cooldown).
        /// </summary>
        public string? Weapon { get; internal set; }

        /// <summary>The fire support whose warning marks the landing (an event-only support).</summary>
        public string? Warning { get; internal set; }
    }

    /// <summary>
    /// A fire trail (prompt 16 E, the Inferno): every <see cref="Every"/> metres it drives it leaves a patch
    /// of burning fuel <see cref="Radius"/> m across that sets enemy ground vehicles in it on fire
    /// (<see cref="Dps"/> a second, the Burn status). A patch is lit for <see cref="Seconds"/> and burns
    /// <see cref="GroundBurn"/> of that, the ground fires' time since the view cut it by a fifth (12A).
    /// </summary>
    public sealed class FireTrailDef
    {
        /// <summary>The share of its lit time a ground fire burns (DECISIONS 12A: a fifth shorter).</summary>
        public const float GroundBurn = 0.8f;

        public float Every { get; internal set; } = 4f;
        public float Seconds { get; internal set; } = 10f;
        public float Radius { get; internal set; } = 3.5f;
        public float Dps { get; internal set; } = 18f;

        /// <summary>How long a patch burns in the battle.</summary>
        public float Burns => Seconds * GroundBurn;
    }

    /// <summary>An emplacement a boss arrives with (the supergun's guns and walls), at an offset in its frame (X right, Y forward).</summary>
    public sealed class GuardDef
    {
        public GuardDef(string def, Vector2 at, float heading)
        {
            Def = Guard.Id(def);
            At = at;
            Heading = heading;
        }

        public string Def { get; }
        public Vector2 At { get; }

        /// <summary>Heading in degrees relative to the boss's.</summary>
        public float Heading { get; }
    }

    /// <summary>An extra model drawn fixed to a vehicle (the supergun's coupled tractors): view only, in the model's frame (X right, Y forward, Z up).</summary>
    public sealed class AttachmentDef
    {
        public AttachmentDef(string model, Vector3 at, float heading)
        {
            Model = Guard.Id(model);
            At = at;
            Heading = heading;
        }

        public string Model { get; }
        public Vector3 At { get; }
        public float Heading { get; }
    }

    /// <summary>
    /// Shoot-and-scoot (the SP howitzer): after <see cref="Shots"/> rounds from one spot it moves
    /// <see cref="Min"/> to <see cref="Max"/> metres to a new one, still in reach of its target, before
    /// it fires again.
    /// </summary>
    public sealed class ScootDef
    {
        public int Shots { get; internal set; } = 3;
        public float Min { get; internal set; } = 15f;
        public float Max { get; internal set; } = 20f;
    }
}

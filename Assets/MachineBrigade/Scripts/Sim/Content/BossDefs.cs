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

        /// <summary>Share of its full health the body loses when it breaks (0: none).</summary>
        public float BreakDamage { get; internal set; }
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

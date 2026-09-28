#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// A boss's runtime state for prompt 8's mechanisms: its parts (health, broken or not, what they
    /// switch off when they break), boring underground, landing troops, and its guards. General: any
    /// vehicle whose def has parts gets them (prompt 9 gives every boss its own).
    /// </summary>
    public sealed partial class Vehicle
    {
        /// <summary>Each part's health now (empty: no parts).</summary>
        internal float[] PartHp = Array.Empty<float>();

        /// <summary>Each part's full health.</summary>
        internal float[] PartMax = Array.Empty<float>();

        internal bool[] PartBroken = Array.Empty<bool>();

        /// <summary>Weapon mounts that no longer fire (their part broke).</summary>
        internal bool[] MountOff = Array.Empty<bool>();

        /// <summary>Skills that are no longer used (their part broke).</summary>
        internal bool[] SkillOff = Array.Empty<bool>();

        /// <summary>Speed from broken parts (engines).</summary>
        internal float PartSpeed = 1f;

        /// <summary>Spread multiplier and share of guided rounds that lose lock, per mount (a broken fire-control radar).</summary>
        internal float[] MountSpread = Array.Empty<float>();
        internal float[] MountFail = Array.Empty<float>();

        public bool HasParts => PartHp.Length > 0;

        public int PartCount => PartHp.Length;

        public float PartHealth(int i) => i >= 0 && i < PartHp.Length ? PartHp[i] : 0f;

        public float PartFullHealth(int i) => i >= 0 && i < PartMax.Length ? PartMax[i] : 0f;

        public bool IsPartBroken(int i) => i >= 0 && i < PartBroken.Length && PartBroken[i];

        /// <summary>Whether mount <paramref name="index"/> still fires (its part, if any, stands).</summary>
        public bool MountWorks(int index) => index < 0 || index >= MountOff.Length || !MountOff[index];

        /// <summary>Where part <paramref name="i"/> is now, on the ground plane.</summary>
        public Vector2 PartPosition(int i)
        {
            if (i < 0 || i >= Def.Parts.Count) return Position;
            var at = Def.Parts[i].At * Def.Scale;
            // At: X to the right, Y forward, in the boss's frame.
            var forward = SimMath.Forward(Heading);
            var right = new Vector2(forward.Y, -forward.X);
            return Position + forward * at.Y + right * at.X;
        }

        /// <summary>The body takes no damage now: too few parts of the lock's kind are broken (the airship's engines).</summary>
        public bool BodyLocked
        {
            get
            {
                var lockDef = Def.PartLock;
                if (lockDef == null || PartHp.Length == 0) return false;
                var broken = 0;
                for (var i = 0; i < Def.Parts.Count; i++)
                    if (PartBroken[i] && Def.Parts[i].Kind == lockDef.Kind) broken++;
                return broken < lockDef.Count;
            }
        }

        /// <summary>Gives it its parts at full health (called once it has its health, boosts and all).</summary>
        internal void InitParts()
        {
            var parts = Def.Parts;
            MountOff = new bool[Def.Mounts.Count];
            MountSpread = new float[Def.Mounts.Count];
            MountFail = new float[Def.Mounts.Count];
            for (var i = 0; i < MountSpread.Length; i++) MountSpread[i] = 1f;
            SkillOff = new bool[Def.Skills.Count];
            if (parts.Count == 0) return;
            PartHp = new float[parts.Count];
            PartMax = new float[parts.Count];
            PartBroken = new bool[parts.Count];
            for (var i = 0; i < parts.Count; i++) PartMax[i] = PartHp[i] = MaxHp * parts[i].Hp;
        }

        // ------------------------------------------------------------ boring underground (the Earth Worm)

        /// <summary>What a boring boss is doing.</summary>
        public enum BurrowState
        {
            Surface,
            Diving,
            Under,
            Cracking,
        }

        internal BurrowState Burrow;

        /// <summary>What a boring boss is doing now (for the view).</summary>
        public BurrowState BurrowStage => Burrow;
        internal double BurrowNext;
        internal Vector2 BurrowGoal;

        /// <summary>Just broke out: it takes more damage until then.</summary>
        internal double ExposedUntil = double.NegativeInfinity;

        /// <summary>Underground: out of sight and reach, it drives no route.</summary>
        public bool Burrowed => Burrow is BurrowState.Under or BurrowState.Cracking;

        /// <summary>Where the ground is cracking (the Earth Worm is about to break out), while it is.</summary>
        public Vector2? Cracking => Burrow == BurrowState.Cracking ? BurrowGoal : null;

        // ------------------------------------------------------------ landing troops (the hovercraft)

        internal double LandingNext;
        internal double LandingUntil = double.NegativeInfinity;
        internal int Landings;

        /// <summary>Stopped with its ramp down, landing troops.</summary>
        public bool Landing { get; internal set; }

        // ------------------------------------------------------------ the supergun's shot

        internal double BombardNext;
    }
}

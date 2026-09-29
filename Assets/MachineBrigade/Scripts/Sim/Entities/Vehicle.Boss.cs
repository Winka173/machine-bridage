#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>
    /// A boss's runtime state for prompt 8's mechanisms: its parts (health, broken or not, patched or
    /// not, what they switch off when they break), boring underground, landing troops, and its
    /// guards. General: any vehicle whose def has parts gets them (prompt 9 gives every boss its own).
    /// </summary>
    public sealed partial class Vehicle
    {
        /// <summary>Play-test 6 (DECISIONS 21G): a boss's rank cycles its weapons faster (1 for anything else).</summary>
        internal float RankFire => Def.RankDef?.FireRate ?? 1f;

        /// <summary>Play-test 6: when the boss's strike window began and what strikes and bombs took from it since (its rank's cap).</summary>
        internal double StrikeWindowAt = double.NegativeInfinity;

        internal float StrikeWindowTaken;

        /// <summary>Play-test 6: a standoff helicopter's target and when it began firing on it from its ring (infinity: not yet).</summary>
        internal EntityId StandoffTarget;

        internal double StandoffSince = double.PositiveInfinity;

        /// <summary>
        /// Each part's health as a share of its full health (empty: no parts). Its full health is a
        /// share of the body's full health, so a boss made tougher after it spawned (a campaign's
        /// scaling, a mission's stronger form) has tougher parts too.
        /// </summary>
        internal float[] PartFrac = Array.Empty<float>();

        internal bool[] PartBroken = Array.Empty<bool>();

        /// <summary>Parts a self-repair has put back (each at most once).</summary>
        internal bool[] PartPatched = Array.Empty<bool>();

        /// <summary>Turning from broken parts (a tail rotor), already folded into <see cref="TurnFactor"/> and <see cref="TurretFactor"/>.</summary>
        internal float PartTurn = 1f;

        /// <summary>The bombard's and the landings' intervals from broken parts (the supergun's tractors).</summary>
        internal float PartCadence = 1f;

        /// <summary>Mechanisms a broken part has stopped (see <see cref="BossPartDef.Stops"/>).</summary>
        internal bool BombardOff, SpotterOff, BurrowOff, LandingOff, AuraOff;

        /// <summary>Weapon mounts that no longer fire (their part broke).</summary>
        internal bool[] MountOff = Array.Empty<bool>();

        /// <summary>Skills that are no longer used (their part broke).</summary>
        internal bool[] SkillOff = Array.Empty<bool>();

        /// <summary>Speed from broken parts (engines).</summary>
        internal float PartSpeed = 1f;

        /// <summary>Spread multiplier and share of guided rounds that lose lock, per mount (a broken fire-control radar).</summary>
        internal float[] MountSpread = Array.Empty<float>();
        internal float[] MountFail = Array.Empty<float>();

        public bool HasParts => PartFrac.Length > 0;

        public int PartCount => PartFrac.Length;

        /// <summary>Part <paramref name="i"/>'s full health: its share of the body's full health.</summary>
        public float PartFullHealth(int i) => i >= 0 && i < PartFrac.Length ? MaxHp * Def.Parts[i].Hp : 0f;

        public float PartHealth(int i) => i >= 0 && i < PartFrac.Length ? PartFrac[i] * PartFullHealth(i) : 0f;

        /// <summary>Part <paramref name="i"/>'s health as a share of its full health (0 broken).</summary>
        public float PartShare(int i) => i >= 0 && i < PartFrac.Length ? PartFrac[i] : 0f;

        public bool IsPartBroken(int i) => i >= 0 && i < PartBroken.Length && PartBroken[i];

        /// <summary>A self-repair has put part <paramref name="i"/> back once.</summary>
        public bool IsPartPatched(int i) => i >= 0 && i < PartPatched.Length && PartPatched[i];

        /// <summary>How many of its parts are broken now.</summary>
        public int BrokenParts
        {
            get
            {
                var n = 0;
                foreach (var b in PartBroken) if (b) n++;
                return n;
            }
        }

        /// <summary>Whether mount <paramref name="index"/> still fires (its part, if any, stands).</summary>
        public bool MountWorks(int index) => SiegeModeFires(index) && (index < 0 || index >= MountOff.Length || (!MountOff[index] && !(index < MountHeld.Length && MountHeld[index]) &&
            // Prompt 19 E.5: guns that wake only once it has crashed.
            !(index < MountDormant.Length && MountDormant[index])));

        /// <summary>
        /// Play-test 5 (DECISIONS 20W): a siege tank's main weapon fires only sieged and its tank-mode gun only on its
        /// tracks (neither while it sieges or packs up); every other mount, and every other vehicle, as before.
        /// </summary>
        private bool SiegeModeFires(int index)
        {
            if (Def.Deploy is not { Siege: true } dep) return true;
            if (index == 0) return Deploy == DeployState.Deployed;
            return index != dep.TankMount || Deploy == DeployState.Mobile;
        }

        /// <summary>Prompt 18: mounts holding their fire while the big attack they carry charges and fires.</summary>
        internal bool[] MountHeld = Array.Empty<bool>();

        /// <summary>Prompt 18: its big attack as it runs, or null (no big attack).</summary>
        public BigAttackState? BigAttack { get; internal set; }

        /// <summary>Prompt 18: it takes this many times the damage while its big attack exposes it (1: not).</summary>
        internal float BigTaken = 1f;

        /// <summary>Prompt 18: the Earth Worm's next dive is its big attack's quake.</summary>
        internal bool BigQuake;

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
                // Prompt 20: a submarine up for a launch shows only its doors.
                if (BodyShut && PartFrac.Length > 0) return true;
                var lockDef = Def.PartLock;
                if (lockDef == null || PartFrac.Length == 0) return false;
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
            MountHeld = new bool[Def.Mounts.Count];
            MountDormant = new bool[Def.Mounts.Count];
            if (Def.Tiers?.Crash is { } crash)
                foreach (var m in crash.Guns)
                    if (m > 0 && m < MountDormant.Length) MountDormant[m] = true;
            // Prompt 20 J.4: mounts that wake with a later phase.
            foreach (var m in Def.WakeMounts)
                if (m > 0 && m < MountDormant.Length) MountDormant[m] = true;
            for (var i = 0; i < MountSpread.Length; i++) MountSpread[i] = 1f;
            SkillOff = new bool[Def.Skills.Count];
            if (parts.Count == 0) return;
            PartFrac = new float[parts.Count];
            PartBroken = new bool[parts.Count];
            PartPatched = new bool[parts.Count];
            for (var i = 0; i < parts.Count; i++) PartFrac[i] = 1f;
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

        // ------------------------------------------------------------ prompt 16: extra boss weapons and escorts

        /// <summary>Its protection system's interceptors stopped (every part carrying "aps" broken).</summary>
        internal bool ApsOff;

        /// <summary>Its jamming aura stopped (every part carrying "jammer" broken).</summary>
        internal bool JammerOff;

        /// <summary>Its fire trail stopped (the part carrying "trail" broken).</summary>
        internal bool TrailOff;

        /// <summary>Interceptors it can hold now: the def's, cut in proportion to the "aps" parts broken.</summary>
        internal int ApsMax = int.MaxValue;

        /// <summary>Where it last dropped a patch of burning fuel (its fire trail).</summary>
        internal Vector2 TrailFrom;

        /// <summary>The boss it escorts (prompt 16 F), or none: the commander AI leaves escorts alone.</summary>
        public EntityId EscortOf { get; internal set; }

        /// <summary>What it does for its boss while it escorts one.</summary>
        public EscortRole EscortRole { get; internal set; }

        public bool IsEscort => EscortOf.IsValid;
    }
}

#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>Timed effects any vehicle can carry (see <see cref="Combat.StatusSystem"/>).</summary>
    internal enum StatusKind
    {
        /// <summary>On fire: Value hit points a second as Fire damage; Team and Source are who lit it; Flag marks a Firestorm fire.</summary>
        Burn,

        /// <summary>Slowed: Value is the share of speed lost.</summary>
        Slow,

        /// <summary>Shredded: takes Value more damage per stack (Stacks) from everyone.</summary>
        Shred,

        /// <summary>Marked by Team: that side deals Value more damage to it, and its artillery reaches Extra farther.</summary>
        Mark,

        /// <summary>An absorbing barrier with Value hit points left.</summary>
        Barrier,

        /// <summary>A rally horn nearby: deals Value more damage.</summary>
        Rally,

        /// <summary>An ammunition carrier nearby: reloads Value faster, on the move too.</summary>
        Rearm,

        /// <summary>Guided rounds aimed at it lose lock (an EW jammer nearby).</summary>
        Jam,

        /// <summary>Just cleansed by damage control: new burns, slows, shreds and stuns do not take.</summary>
        Cleansed,

        /// <summary>Revealed by counter-battery radar to the teams in Stacks (a mask); their artillery deals Value more to it.</summary>
        Reveal,
        Count,
    }

    /// <summary>
    /// The last two fixed defences of one side that hit a vehicle, and when (Fire Link: a tower
    /// hits harder while another friendly tower has hit the same target within a few seconds).
    /// </summary>
    internal struct TowerFireMark
    {
        public EntityId Last, Previous;
        public double LastAt, PreviousAt;

        /// <summary>Whether a fixed defence other than <paramref name="self"/> hit it at or after <paramref name="since"/>.</summary>
        public bool ByOther(EntityId self, double since) =>
            (Last.IsValid && Last != self && LastAt >= since) || (Previous.IsValid && Previous != self && PreviousAt >= since);

        public void Note(EntityId tower, double now)
        {
            if (Last == tower)
            {
                LastAt = now;
                return;
            }
            Previous = Last;
            PreviousAt = LastAt;
            Last = tower;
            LastAt = now;
        }
    }

    internal struct Status
    {
        public float Value;
        public double Until;
        public int Stacks;
        public int Team;
        public EntityId Source;
        public float Extra;
        public bool Flag;

        public bool Active(double now) => Until > now;
    }

    /// <summary>
    /// What a vehicle's equipment gives it beyond the plain multipliers: its stat lines, its
    /// traits with their numbers, and the counters and timers the traits run on. Only vehicles
    /// with equipment have one.
    /// </summary>
    internal sealed class GearState
    {
        public readonly float[] Stats = new float[(int)StatId.Count];
        private readonly GearTrait[] _traits = new GearTrait[(int)TraitId.Count];
        private readonly bool[] _has = new bool[(int)TraitId.Count];

        /// <summary>When each trait may fire again (cooldown traits), by trait.</summary>
        public readonly double[] Ready = new double[(int)TraitId.Count];

        /// <summary>When the special module may fire again.</summary>
        public double ModuleReady;

        public bool Any { get; private set; }

        public bool Has(TraitId id) => _has[(int)id];

        public GearTrait Trait(TraitId id) => _traits[(int)id];

        public float Stat(StatId id) => Stats[(int)id];

        public void Add(GearTrait t)
        {
            if (t.Id <= TraitId.None || t.Id >= TraitId.Count) return;
            _traits[(int)t.Id] = t;
            _has[(int)t.Id] = true;
            Any = true;
        }

        public double SpawnedAt;

        /// <summary>The last proc word shown over it (at most one every two seconds).</summary>
        public double LastProcAt = double.NegativeInfinity;

        // ----------------------------------------------------------------- offence
        /// <summary>Trigger pulls of the main weapon (every-Nth-shot traits).</summary>
        public int Shots;

        /// <summary>What the main weapon last fired at (Opening Salvo).</summary>
        public EntityId LastTarget;

        /// <summary>Consecutive direct hits on one target (Momentum Gun).</summary>
        public EntityId StreakTarget;
        public int Streak;

        /// <summary>Shoot-and-Scoot: when it last got the bonus (once per stop), and the speed burst after firing.</summary>
        public double ScootShotAt = double.NegativeInfinity;
        public double ScootUntil = double.NegativeInfinity;

        /// <summary>Kestrel four-piece: the burst of speed after each shot.</summary>
        public double HitRunUntil = double.NegativeInfinity;

        /// <summary>Kill Reload: faster fire until then.</summary>
        public double KillFireUntil = double.NegativeInfinity;

        /// <summary>Ghillie Mode: hidden now, and whether the next shot is the first from hiding.</summary>
        public bool Hidden;
        public bool FromHiding;

        // ----------------------------------------------------------------- defence
        public int Blocks;
        public double BlockAt;
        public int GlacisHits;
        public float Ablative;
        public bool UnbreakableUsed;
        public readonly int[] Adapt = new int[5];
        public readonly double[] AdaptUntil = new double[5];
        public int CrownStacks;

        /// <summary>Siege Anchor: dug in, and until when it is still pulling the anchor up.</summary>
        public bool Anchored;
        public double UnanchorUntil = double.NegativeInfinity;

        public bool AfterburnerUsed, DomeUsed, SecondSmokeUsed, GhostNetUsed;

        /// <summary>A tower's smoke launchers have fired (once a life, below half health).</summary>
        public bool TowerSmokeUsed;

        /// <summary>Decoy Launcher: a decoy draws guided and indirect rounds until then, at this spot.</summary>
        public double DecoyUntil = double.NegativeInfinity;
        public Vector2 DecoyAt;

        /// <summary>Drone Escort and Swarm: the drone it launches (a copy of a catalog drone, sized to this vehicle).</summary>
        public WeaponDef? Drone;

        /// <summary>A trait's own counter (Stormfront: salvos fired).</summary>
        public int Salvos;

        /// <summary>Transit Gearbox: no enemy in sight (checked twice a second).</summary>
        public bool Calm;
    }
}

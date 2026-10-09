#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>A ship's state at sea (prompt 16): where it is heading, its dash, its landing, its run for the edge.</summary>
    public sealed partial class Vehicle
    {
        /// <summary>Which way along the coast it is going: +1 (towards +u) or -1.</summary>
        internal int NavalDir = 1;

        /// <summary>Naval tune 09/10: a standoff ship cornered at its lane's end breaking out past its enemy (the way, +1 / -1), or 0.</summary>
        internal int NavalBreak;

        /// <summary>Where it is steering to, in the coast's frame (u along, w out).</summary>
        internal Vector2 NavalGoal;

        /// <summary>The flagship an escort or a raider keeps with (its fleet's), or none.</summary>
        internal EntityId Flagship;

        /// <summary>
        /// DECISIONS 20Y: an escort's station beside its flagship in the coast's frame (u along its line from its
        /// middle, w from its lane, negative towards the shore), when <see cref="OnStation"/>.
        /// </summary>
        internal Vector2 StationAt;
        internal bool OnStation;

        /// <summary>A raider: in (dashing to the shore), holding there, or out on its lane; when that ends.</summary>
        internal int DashStage;
        internal double DashUntil;

        /// <summary>A landing craft: its beach, what it carries, whether it has landed them.</summary>
        internal int LandingIndex = -1;
        internal string[] Cargo = System.Array.Empty<string>();
        internal bool Unloaded;
        internal double UnloadAt = double.PositiveInfinity;

        /// <summary>The flagship's salvos, cruise missiles and craft: when they are next due, how many launched.</summary>
        internal double SalvoNext, CruiseNext, CraftNext;
        internal int CraftLaunched;
        internal float SweepU;
        internal bool SweepSet;
        internal int NavalPhaseSeen = -1;

        /// <summary>
        /// Play-test 14: a salvo being laid. Each standing main turret's order (its part, its mount, its aim point); the
        /// turrets traverse onto them at the turret rate and the salvo goes once all are on (or the lay ran too long).
        /// </summary>
        internal readonly System.Collections.Generic.List<(int part, int mount, Vector2 aim)> LayOrders = new();
        internal bool Laying, LayPreview;
        internal double LayFrom;
        internal Vector2 SalvoAim;

        /// <summary>Mechanisms its broken parts have stopped (prompt 16): cruise missiles, landing craft, fire-control radar (its CIWS is part 2's "aps").</summary>
        internal bool CruiseOff, CraftOff, RadarOff;

        /// <summary>The share of interceptions its point defence misses (a broken radar).</summary>
        internal float ApsMiss;

        /// <summary>Running for the edge (the flagship's last phase).</summary>
        public bool Escaping { get; internal set; }

        /// <summary>It got away over the edge: out of the fight (untouchable, silent, not drawn).</summary>
        public bool Escaped { get; internal set; }

        /// <summary>When its run's clock is out (set as the run begins; NaN before).</summary>
        internal double EscapeDeadline = double.NaN;

        /// <summary>Seconds until it gets away (while <see cref="Escaping"/>; -1 otherwise): the clock, or longer if it was slowed.</summary>
        public float EscapeSeconds { get; internal set; } = -1f;

        /// <summary>The flagship's lane, in the coast's frame, as the view and the HUD see it.</summary>
        public string? NavalLane { get; internal set; }

        // ------------------------------------------------------------------ prompt 33 L4: the sea routes

        /// <summary>A big ship's lane segment on the sea routes and the next one it sails into (both reserved); -1: none.</summary>
        internal int SeaSegment = -1, SeaNextSegment = -1;

        /// <summary>This step's speed cap (m/s) from the minimum gap to a big ship in its way; infinity: none.</summary>
        internal float SeaCap = float.PositiveInfinity;

        /// <summary>Ticks it has been held up (stopped by the gap rule) in a row.</summary>
        internal int SeaWait;

        /// <summary>The holding node it is pulling into (-1: none), the ship it gave way to, and the tick it began.</summary>
        internal int SeaHold = -1;
        internal EntityId SeaHoldFor;
        internal long SeaHoldSince;

        /// <summary>The lane a flagship's escort slots were resolved for; an escort on its way round astern to a slot on the other side.</summary>
        internal string? SlotLane;
        internal bool SlotVia;

        /// <summary>Holding in a passing bay (the view and the tests).</summary>
        public bool SeaHolding => SeaHold >= 0;
    }
}

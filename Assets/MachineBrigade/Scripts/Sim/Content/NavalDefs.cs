#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>What a ship does at sea (prompt 16 B, C).</summary>
    public enum NavalRole
    {
        /// <summary>The flagship (Leviathan): patrols its phase's lane, and in its last phase runs for the edge.</summary>
        Flagship,

        /// <summary>An escort (a corvette): keeps station on the flagship along its lane, screens it in the last phase.</summary>
        Escort,

        /// <summary>A fast attack boat: waits out on its lane, dashes in to the shore, fires and runs back out.</summary>
        Raider,

        /// <summary>A landing craft: runs up on a beach, lands its vehicles and backs off to its ship.</summary>
        Lander,
    }

    /// <summary>
    /// A ship (data "naval", prompt 16): it moves only on the sea, in the coast's frame (<see cref="SeaDef"/>),
    /// never on the ground's grid; the naval system steers it. <see cref="Lanes"/> is its lane by boss
    /// phase (the last one holds after); an escort keeps <see cref="Station"/> metres along the lane from
    /// its flagship; a raider dashes in to <see cref="DashW"/> (in the coast's frame) every
    /// <see cref="DashEvery"/> seconds and holds there <see cref="DashHold"/> seconds.
    /// </summary>
    public sealed class NavalDef
    {
        public NavalRole Role { get; internal set; } = NavalRole.Flagship;

        public IReadOnlyList<string> Lanes { get; internal set; } = new[] { "far" };

        /// <summary>The flagship's phase from which it runs for the edge (-1: never).</summary>
        public int EscapePhase { get; internal set; } = -1;

        /// <summary>Its speed while it runs, as a share of its own.</summary>
        public float EscapeSpeed { get; internal set; } = 0.6f;

        /// <summary>The least length of sea it has to cover to get away (it turns about if the nearer end is closer).</summary>
        public float EscapeRun { get; internal set; } = 150f;

        public float Station { get; internal set; }

        public float DashW { get; internal set; } = 48f;
        public float DashEvery { get; internal set; } = 26f;
        public float DashHold { get; internal set; } = 7f;

        /// <summary>How far to the side of its line it may drift before it steers back (metres).</summary>
        public float Slack { get; internal set; } = 2f;

        /// <summary>
        /// Prompt 20 J.5: a skimmer's passes (Caspian): <see cref="PassIn"/> s fast along the near lane (in reach of the
        /// shore), then <see cref="PassOut"/> s out on the far one, over and over (0: an ordinary patrol).
        /// </summary>
        public float PassIn { get; internal set; }

        public float PassOut { get; internal set; }

        /// <summary>The lane for boss phase <paramref name="phase"/>.</summary>
        public string LaneFor(int phase) => Lanes.Count == 0 ? "far" : Lanes[Math.Clamp(phase, 0, Lanes.Count - 1)];
    }

    /// <summary>
    /// A ship's main battery firing on the shore (data "salvo"): every <see cref="Every"/> seconds each
    /// standing main-gun part (kind "maingun") lays <see cref="Shells"/> shells along the coast round a
    /// point on the shore, marked <see cref="Warn"/> seconds ahead. The point sweeps along the coast
    /// <see cref="Sweep"/> metres a salvo the way the ship is going; a group of enemy ground vehicles in
    /// reach near the shore draws it instead (from the second phase on, the biggest group in reach).
    /// </summary>
    public sealed class SalvoDef
    {
        public float Every { get; internal set; } = 10f;
        public float First { get; internal set; } = 8f;
        public float Warn { get; internal set; } = 2.6f;
        public int Shells { get; internal set; } = 3;
        public float Damage { get; internal set; } = 300f;
        public float Radius { get; internal set; } = 7f;

        /// <summary>The length of shore a salvo's shells fall along.</summary>
        public float Spread { get; internal set; } = 16f;

        /// <summary>How far from the ship the shells reach.</summary>
        public float Range { get; internal set; } = 150f;

        public float Sweep { get; internal set; } = 18f;

        /// <summary>The spread and scatter once its fire-control radar (a part of kind "radar") is broken.</summary>
        public float BlindScatter { get; internal set; } = 2.2f;

        public string? Weapon { get; internal set; }
        public string? Warning { get; internal set; }
    }

    /// <summary>
    /// Cruise missiles from a ship's launch cells (data "cruise", a part of kind "vls"): from phase
    /// <see cref="Phase"/> one every <see cref="Every"/> seconds at the enemy's biggest group of ground
    /// vehicles anywhere, marked <see cref="Warn"/> seconds ahead; when the last phase begins,
    /// <see cref="Final"/> at once at the enemy's base (its HQ and towers).
    /// </summary>
    public sealed class CruiseDef
    {
        public float Every { get; internal set; } = 48f;
        public float First { get; internal set; } = 18f;
        public int Phase { get; internal set; } = 1;
        public float Warn { get; internal set; } = 4.5f;
        public float Damage { get; internal set; } = 520f;
        public float Radius { get; internal set; } = 16f;
        public int Final { get; internal set; } = 4;
        public string? Weapon { get; internal set; }
        public string? Warning { get; internal set; }
    }

    /// <summary>
    /// Landing craft from a ship's well deck (data "craft", a part of kind "welldeck"): from phase
    /// <see cref="Phase"/>, every <see cref="Every"/> seconds, a <see cref="Unit"/> carrying
    /// <see cref="Per"/> vehicles drawn in turn from <see cref="Carries"/> to a beach, at most
    /// <see cref="Max"/> times.
    /// </summary>
    public sealed class CraftDef
    {
        public string Unit { get; internal set; } = "landing_craft";
        public IReadOnlyList<string> Carries { get; internal set; } = Array.Empty<string>();
        public int Per { get; internal set; } = 2;
        public float Every { get; internal set; } = 42f;
        public float First { get; internal set; } = 6f;
        public int Phase { get; internal set; } = 1;
        public int Max { get; internal set; } = 3;
    }

    /// <summary>A ship of the flagship's fleet (data "fleet"): its def, how many, its station along the lane.</summary>
    public sealed class FleetShipDef
    {
        public string Unit { get; internal set; } = "";
        public int Count { get; internal set; } = 1;
        public float Station { get; internal set; }

        /// <summary>
        /// DECISIONS 20Y: an escort's station abeam of its flagship (data "abeam", metres, negative towards the shore),
        /// <see cref="Station"/> then being its place along the flagship's line from its middle; the k-th ship of the
        /// entry keeps a row further in (NaN: the old station along the lane, ahead or astern).
        /// </summary>
        public float Abeam { get; internal set; } = float.NaN;

        /// <summary>Whether its ships keep station abeam (<see cref="Abeam"/>).</summary>
        public bool Beside => !float.IsNaN(Abeam);
    }

    /// <summary>Aircraft that fly in from over the sea when a phase begins (data "air": the phase and the units).</summary>
    public sealed class AirWaveDef
    {
        public int Phase { get; internal set; } = 1;
        public IReadOnlyList<string> Units { get; internal set; } = Array.Empty<string>();
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 16: a ship (it moves on the sea only), or null.</summary>
        public NavalDef? Naval { get; internal set; }

        public SalvoDef? Salvo { get; internal set; }
        public CruiseDef? Cruise { get; internal set; }
        public CraftDef? Craft { get; internal set; }
        public IReadOnlyList<FleetShipDef> Fleet { get; internal set; } = Array.Empty<FleetShipDef>();
        public IReadOnlyList<AirWaveDef> AirWaves { get; internal set; } = Array.Empty<AirWaveDef>();

        /// <summary>
        /// Prompt 16: a coastal battery's gun fires on ships only (data "navalOnly" on the vehicle): its
        /// 155 mm reach out to sea would otherwise shell the whole coast.
        /// </summary>
        public bool NavalOnly { get; internal set; }

        /// <summary>The boss system lays its turret itself (the supergun's shot, a ship's salvos): the combat system leaves it be.</summary>
        internal bool LaysOwnTurret => Bombard != null || Salvo != null;
    }
}

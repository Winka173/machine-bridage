#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 17 C: a shield dome round a vehicle or tower (the shield carrier, the shield generator). Every
    /// hit but energy on a unit of its side inside <see cref="Radius"/> is taken by the dome until its
    /// <see cref="Hp"/> is spent; it is back at full <see cref="Recharge"/> seconds after the last hit it
    /// took (or after it broke). A unit under two domes is covered by one at a time (they never add up), and
    /// a shot fired from inside the dome passes (it is a bubble, not a wall round each unit).
    /// </summary>
    public sealed class DomeDef
    {
        public DomeDef(float radius, float hp, float recharge)
        {
            Radius = radius > 0f ? radius : throw new ArgumentException("A dome's radius must be positive.");
            Hp = hp > 0f ? hp : throw new ArgumentException("A dome's hp must be positive.");
            Recharge = Math.Max(1f, recharge);
        }

        public float Radius { get; }
        public float Hp { get; }
        public float Recharge { get; }
    }

    /// <summary>
    /// Prompt 17 C: a vehicle that digs in where it stands (the bunker vehicle): <see cref="Seconds"/> to deploy
    /// and as long to pack up, neither firing nor moving meanwhile and keeping its moving armour; dug in, its
    /// front is <see cref="FrontUp"/> levels thicker (at most 4), its guns reach <see cref="Range"/> times as
    /// far and its turret turns all round; moving, the turret keeps within <see cref="Arc"/> degrees of the nose.
    /// </summary>
    public sealed class DeployDef
    {
        public float Seconds { get; internal set; } = 3f;
        public int FrontUp { get; internal set; } = 2;
        public float Range { get; internal set; } = 1.3f;

        /// <summary>Half the turret's traverse while mobile, in radians.</summary>
        public float Arc { get; internal set; } = MathF.PI / 4f;

        /// <summary>
        /// Play-test 5 (DECISIONS 20W): a siege tank's two modes (StarCraft 2's). The main weapon (mount 0) fires only
        /// sieged; mount <see cref="TankMount"/> (its tank-mode gun) only on its tracks, the turret laid by it. It sieges
        /// with an enemy between the main weapon's minimum and full reach, or on guard, and packs up to move or when
        /// enemies close inside that minimum with nothing further to shell.
        /// </summary>
        public bool Siege { get; internal set; }

        /// <summary>The mount that fires in tank mode (a <see cref="Siege"/> vehicle).</summary>
        public int TankMount { get; internal set; } = 1;
    }

    /// <summary>
    /// Prompt 17 C: a loyal wingman drone. It flies on the wing of the nearest manned aircraft of its side within
    /// <see cref="Follow"/> metres (patrols the front with none); an enemy anti-air missile aimed at an aircraft it
    /// escorts, with the wingman within <see cref="Decoy"/> metres of it, turns onto the wingman at
    /// <see cref="Pull"/>.
    /// </summary>
    public sealed class WingmanDef
    {
        public float Follow { get; internal set; } = 120f;
        public float Decoy { get; internal set; } = 25f;
        public float Pull { get; internal set; } = 0.4f;
    }

    /// <summary>
    /// Prompt 17 C: a CP relay (a base's small tower): its side earns <see cref="Income"/> CP a second more, a
    /// second relay <see cref="Second"/>, a third nothing; nothing while it has been hit in the last
    /// <see cref="Quiet"/> seconds. Two to a base, never on an outpost.
    /// </summary>
    public sealed class RelayDef
    {
        public float Income { get; internal set; } = 0.1f;
        public float Second { get; internal set; } = 0.06f;
        public float Quiet { get; internal set; } = 5f;

        /// <summary>Relays a base may hold (the Base screen, the loadout and the AI's pick all keep to it).</summary>
        public static int MaxPerBase => global::MachineBrigade.Sim.Content.SimTunables.Vehicles.RelayDef.MaxPerBase;
    }

    public sealed partial class VehicleDef
    {
        /// <summary>Prompt 17 C: its shield dome (null: none).</summary>
        public DomeDef? Dome { get; internal set; }

        /// <summary>Prompt 17 C: it digs in when it stands (null: it does not).</summary>
        public DeployDef? Deploy { get; internal set; }

        /// <summary>Prompt 17 C: a loyal wingman drone's escort rules (null: not a wingman).</summary>
        public WingmanDef? Wingman { get; internal set; }

        /// <summary>Prompt 17 C: a CP relay's pay (null: not a relay).</summary>
        public RelayDef? Relay { get; internal set; }

        /// <summary>Prompt 17 C: not counted in its side's aircraft cap (the wingman; its own <see cref="MaxPerSide"/> holds).</summary>
        public bool AirCapFree { get; internal set; }

        /// <summary>
        /// Prompt 17 C: with no aircraft to fight it goes for the enemy's air defences (the stealth fighter's bombs):
        /// it engages them on its own and its free bomb mount picks them first.
        /// </summary>
        public bool Sead { get; internal set; }

        /// <summary>
        /// Prompt 17 D: the models of the cards merged into this one (the A-10 in the attack jet, the Ka-52 in the attack
        /// helicopter, the sapper in the engineer), kept in the model library for a later camouflage; never drawn now.
        /// </summary>
        public IReadOnlyList<string> AltModels { get; internal set; } = System.Array.Empty<string>();

        /// <summary>Whether it is a manned aircraft a wingman may escort (not a drone, a wingman or a boss).</summary>
        public bool Manned => Flying && !Drone && Wingman == null && !Boss && !Static;
    }
}

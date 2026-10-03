#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Commands
{
    public enum CommandType
    {
        Move,
        Attack,
        AttackMove,
        Stop,
        Retreat,

        /// <summary>Buys a vehicle (DefId) that arrives at the team's drop zone after a short delivery.</summary>
        Deploy,

        /// <summary>Calls fire support (DefId) on Point; airstrikes fly from Point towards Point2.</summary>
        Strike,

        /// <summary>Flies a tower into the base hardpoint at Point (a destroyed one back in; an outpost's with DefId).</summary>
        CallTower,

        /// <summary>Sets the captured point DefId up as an outpost.</summary>
        Outpost,

        /// <summary>
        /// Prompt 9: the side's units in reach aim at part DefId of boss Target until it breaks or the
        /// order is cancelled (DefId null or empty); Units may be empty.
        /// </summary>
        FocusPart,

        /// <summary>Prompt 13 C.4: sends aircraft with stores to rearm now (they finish what they are doing first).</summary>
        Rearm,

        /// <summary>Prompt 25 F2 batch A: buys an airborne vehicle (DefId) dropped by parachute on Point, where the side sees.</summary>
        Paradrop,

        /// <summary>
        /// Prompt 32 L4: the side's HQ skill (its one button): a Fortress's barrage on Point, a Garrison's alarm, a Shield's
        /// emergency dome (Point unused).
        /// </summary>
        HqSkill,

        /// <summary>Play-test 14: where the side's hangars send the units they turn out (Point).</summary>
        HangarRally,
    }

    /// <summary>
    /// A request from the player, the AI or a game mode. Every source goes through
    /// <see cref="SimWorld.Submit"/>, so all of them obey the same validation.
    /// </summary>
    public sealed class Command
    {
        public Command(CommandType type, int team, IReadOnlyList<EntityId> units, Vector2 point = default,
            EntityId target = default, string? defId = null, Vector2 point2 = default, bool manual = false)
        {
            Manual = manual;
            Type = type;
            Team = team;
            Units = units ?? throw new ArgumentNullException(nameof(units));
            Point = point;
            Target = target;
            DefId = defId;
            Point2 = point2;
        }

        /// <summary>Every unit of <paramref name="team"/> in reach aims at <paramref name="partId"/> of the boss (null cancels).</summary>
        public static Command FocusPart(int team, EntityId boss, string? partId) =>
            new(CommandType.FocusPart, team, Array.Empty<EntityId>(), target: boss, defId: partId);

        public static Command Deploy(int team, string vehicleId) =>
            new(CommandType.Deploy, team, Array.Empty<EntityId>(), defId: vehicleId);

        /// <summary>Prompt 25 F2 batch A: an airborne vehicle dropped by parachute on <paramref name="point"/>.</summary>
        public static Command Paradrop(int team, string vehicleId, Vector2 point) =>
            new(CommandType.Paradrop, team, Array.Empty<EntityId>(), point, defId: vehicleId);

        /// <summary>Prompt 32 L4: the HQ's skill (a Fortress aims it at <paramref name="point"/>).</summary>
        public static Command HqSkill(int team, Vector2 point = default) =>
            new(CommandType.HqSkill, team, Array.Empty<EntityId>(), point);

        /// <summary>Play-test 14: a call the player fills (<see cref="Content.SupportDef.CallMaxCp"/>): the support and the units chosen.</summary>
        public static Command Call(int team, string supportId, Vector2 point, IReadOnlyList<string> units) =>
            new(CommandType.Strike, team, Array.Empty<EntityId>(), point, defId: supportId, point2: point) { Calls = units };

        /// <summary>Play-test 14: the units a filled call drops (null: the support's own).</summary>
        public IReadOnlyList<string>? Calls { get; private set; }

        /// <summary>Play-test 14: the hangars' rally point.</summary>
        public static Command HangarRally(int team, Vector2 point) =>
            new(CommandType.HangarRally, team, Array.Empty<EntityId>(), point);

        public static Command Strike(int team, string supportId, Vector2 point, Vector2 towards = default) =>
            new(CommandType.Strike, team, Array.Empty<EntityId>(), point, defId: supportId, point2: towards);

        /// <summary>Vehicle or support definition for Deploy and Strike.</summary>
        public string? DefId { get; }

        /// <summary>Second point: the direction an airstrike flies in.</summary>
        public Vector2 Point2 { get; }

        /// <summary>
        /// Given by the player's own hand: the commander AI leaves these vehicles alone until a
        /// while after they finish the order.
        /// </summary>
        public bool Manual { get; }

        public CommandType Type { get; }
        public int Team { get; }
        public IReadOnlyList<EntityId> Units { get; }
        public Vector2 Point { get; }
        public EntityId Target { get; }
    }

    /// <summary>Why a command was refused. The HUD turns these into localised text.</summary>
    public enum CommandError
    {
        None,
        MatchOver,
        NoUnits,
        InvalidPoint,
        OutOfBounds,
        InvalidTarget,
        TargetNotVisible,
        NoRallyPoint,
        UnknownCard,
        NotEnoughCp,
        ArmyAtCapacity,

        /// <summary>The side already has its full share of aircraft up (see TeamEconomy.MaxAircraft).</summary>
        AirAtCapacity,
        OnCooldown,
        NotAvailable,

        /// <summary>The side already has as many of this vehicle as it may field (a command vehicle: one).</summary>
        UnitLimit,

        /// <summary>Prompt 25 F2 batch A: a parachute drop only where the side sees, and never into an enemy base.</summary>
        DropNotSeen,

        /// <summary>Prompt 32 L2: no tower is flown back in while an enemy stands within 20 m of its slot.</summary>
        EnemyNear,
    }

    public readonly struct CommandResult
    {
        private CommandResult(CommandError error) => Error = error;

        public static CommandResult Ok => default;

        public CommandError Error { get; }

        public bool Accepted => Error == CommandError.None;

        public static CommandResult Rejected(CommandError error) => new CommandResult(error);
    }
}

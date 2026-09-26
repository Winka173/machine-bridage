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

        public static Command Deploy(int team, string vehicleId) =>
            new(CommandType.Deploy, team, Array.Empty<EntityId>(), defId: vehicleId);

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
        OnCooldown,
        NotAvailable,
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

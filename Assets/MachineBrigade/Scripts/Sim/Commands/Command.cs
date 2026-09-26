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
    }

    /// <summary>
    /// A request from the player, the AI or a game mode. Every source goes through
    /// <see cref="SimWorld.Submit"/>, so all of them obey the same validation.
    /// </summary>
    public sealed class Command
    {
        public Command(CommandType type, int team, IReadOnlyList<EntityId> units, Vector2 point = default,
            EntityId target = default)
        {
            Type = type;
            Team = team;
            Units = units ?? throw new ArgumentNullException(nameof(units));
            Point = point;
            Target = target;
        }

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

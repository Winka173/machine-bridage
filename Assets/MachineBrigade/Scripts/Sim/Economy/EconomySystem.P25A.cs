#nullable enable
using MachineBrigade.Sim.Commands;

namespace MachineBrigade.Sim.Economy
{
    /// <summary>Prompt 25 F2 batch A (DECISIONS 25F2-A): the airborne vehicle's parachute drop, a paid delivery onto a chosen point.</summary>
    internal sealed partial class EconomySystem
    {
        /// <summary>
        /// Buys an airborne vehicle and drops it on <paramref name="point"/>: anywhere its side sees (a unit's sight or a scan,
        /// not through smoke) except an enemy base. The card's price and limits are a delivery's (<see cref="Deploy"/>); the
        /// stand-in falls for the drop's seconds, a low-altitude target for anti-air, and lands the vehicle with the health it kept.
        /// </summary>
        public CommandResult Paradrop(int team, string? defId, System.Numerics.Vector2 point)
        {
            if (!_teams.TryGetValue(team, out var economy)) return CommandResult.Rejected(CommandError.NotAvailable);
            if (defId == null || !_world.Catalog.Vehicles.TryGetValue(defId, out var def) || def.Paradrop is not { } drop)
                return CommandResult.Rejected(CommandError.UnknownCard);
            if (economy.Vehicles.Count > 0 && !Contains(economy.Vehicles, defId)) return CommandResult.Rejected(CommandError.UnknownCard);
            if (!_world.Map.Contains(point)) return CommandResult.Rejected(CommandError.OutOfBounds);
            if (!_world.Works.SeenBy(team, point) || _world.Works.NearEnemyBase(team, point, drop.BaseKeepOut))
                return CommandResult.Rejected(CommandError.DropNotSeen);
            var price = economy.PriceOf(defId, def.CpCost);
            if (economy.Cp < price) return CommandResult.Rejected(CommandError.NotEnoughCp);
            if (VehicleCount(team) + _world.Works.DropsOf(team) >= economy.VehicleCap) return CommandResult.Rejected(CommandError.ArmyAtCapacity);
            if (def.MaxPerSide > 0 && Fielded(team, defId) >= def.MaxPerSide) return CommandResult.Rejected(CommandError.UnitLimit);
            economy.Cp -= price;
            _world.Works.StartDrop(team, defId, point, drop);
            economy.ArmyCp = ArmyCp(team);
            economy.VehicleCount = VehicleCount(team);
            // No delivery event: the falling stand-in is the drop the game draws (its own model under its canopies).
            return CommandResult.Ok;
        }
    }
}

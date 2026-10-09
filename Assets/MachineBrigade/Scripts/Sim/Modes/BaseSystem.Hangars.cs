#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Play-test 14: one hangar's turn-out in the battle (see <see cref="HangarDef"/>).</summary>
    public sealed class HangarState
    {
        /// <summary>The unit it turns out (one of its def's units).</summary>
        public string Unit { get; internal set; } = "";

        /// <summary>Match time of the next unit.</summary>
        public double NextAt { get; internal set; }

        /// <summary>Its units in the field (pruned as they fall).</summary>
        internal readonly List<EntityId> Out = new();
    }

    public sealed partial class TeamBase
    {
        /// <summary>Play-test 14: where the side's hangars send their units (null: they stay by their hangar).</summary>
        public Vector2? HangarRally { get; internal set; }

        /// <summary>Play-test 14: each standing hangar's turn-out, by the hangar's id.</summary>
        internal readonly Dictionary<EntityId, HangarState> Hangars = new();
    }

    public sealed partial class BaseSystem
    {
        /// <summary>
        /// Play-test 14: the side's hangars. Each standing hangar turns out one unit a cycle (free: no CP, no army supply,
        /// no kill bounty, like the Garrison's squads) while fewer than its def's count of its own are alive (session 5: its
        /// budget over the unit's CP, <see cref="HangarDef.AliveOf"/>) and the side's
        /// vehicle cap has room; the units hold the hangar rally point, or the hangar's side facing the enemy's camp.
        /// </summary>
        private void StepHangars(TeamBase b)
        {
            var now = _world.Time;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team != b.Team || v.Def.Hangar is not { } hangar || hangar.Units.Count == 0) continue;
                if (!b.Hangars.TryGetValue(v.Id, out var s))
                {
                    s = new HangarState { Unit = HangarUnit(b, v.Def), NextAt = now + hangar.Every };
                    b.Hangars[v.Id] = s;
                }
                s.Out.RemoveAll(id => !_world.TryGetVehicle(id, out var u) || !u.IsAlive);
                if (now < s.NextAt) continue;
                s.NextAt = now + hangar.Every;
                // Play-test 14 session 5: as many alive as its budget buys of the picked unit (a light tank 1, a jeep 2).
                if (string.IsNullOrEmpty(s.Unit) || !_world.Catalog.Vehicles.TryGetValue(s.Unit, out var unitDef) || s.Out.Count >= hangar.AliveOf(unitDef)) continue;
                if (_world.TryGetEconomy(b.Team, out var economy) && _world.Economy.VehicleCount(b.Team) >= economy.VehicleCap) continue;
                var post = HangarPost(b, v);
                var dir = post - v.Position;
                var heading = SimMath.HeadingOf(dir.LengthSquared() > 0.01f ? dir : Vector2.UnitX);
                var at = _world.ClampToMap(v.Position + (dir.LengthSquared() > 0.01f ? Vector2.Normalize(dir) : Vector2.UnitX) * (v.Def.Radius + global::MachineBrigade.Sim.Content.SimTunables.Bases.BaseSystem.StepHangarsRadiusAdd));
                var unit = _world.SpawnVehicle(s.Unit, b.Team, at, heading);
                unit.Garrison = true;
                unit.GuardPoint = post;
                unit.PostRadius = hangar.Post;
                _world.PathTo(unit, post);
                s.Out.Add(unit.Id);
            }
        }

        /// <summary>The unit a hangar turns out: the loadout's choice for its def if the def allows it, else its first unit.</summary>
        private static string HangarUnit(TeamBase b, VehicleDef def)
        {
            var units = def.Hangar!.Units;
            var root = def.Id.Split('.')[0];
            if (b.Loadout.HangarUnits.TryGetValue(root, out var chosen) && ContainsUnit(units, chosen)) return chosen;
            return units[0];
        }

        private static bool ContainsUnit(IReadOnlyList<string> units, string id)
        {
            foreach (var u in units)
                if (u == id) return true;
            return false;
        }

        /// <summary>Where a hangar's units hold: the side's rally point, else 15 m out from the hangar towards the enemy's camp.</summary>
        private Vector2 HangarPost(TeamBase b, Vehicle hangar)
        {
            if (b.HangarRally is { } rally) return rally;
            Vector2? enemy = null;
            foreach (var other in _bases.Values)
                if (other.Team != b.Team && other.Hq.IsValid)
                {
                    enemy = other.HqPosition;
                    break;
                }
            var toward = enemy ?? Vector2.Zero;
            var d = toward - hangar.Position;
            return _world.ClampToMap(d.LengthSquared() > 0.01f ? hangar.Position + Vector2.Normalize(d) * (hangar.Def.Radius + global::MachineBrigade.Sim.Content.SimTunables.Bases.BaseSystem.HangarPostRadiusAdd) : hangar.Position);
        }

        /// <summary>Play-test 14: the side's hangar rally point; every hangar unit in the field heads there at once.</summary>
        internal CommandResult SetHangarRally(Command command)
        {
            if (!_bases.TryGetValue(command.Team, out var b)) return CommandResult.Rejected(CommandError.NoUnits);
            var at = _world.ClampToMap(command.Point);
            b.HangarRally = at;
            foreach (var s in b.Hangars.Values)
                foreach (var id in s.Out)
                {
                    if (!_world.TryGetVehicle(id, out var u) || !u.IsAlive) continue;
                    u.GuardPoint = at;
                    u.ClearPath();
                    _world.PathTo(u, at);
                }
            return CommandResult.Ok;
        }
    }
}

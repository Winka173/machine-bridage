#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Play-test 12 (DECISIONS "Play-test 12 (lane B)"): the menu's "In action" preview has no sea, so the naval system
    /// never steps there and a flagship's main battery (laid: only <see cref="Salvo"/> fires it) and its launch cells
    /// never fired: the owner watched the Leviathan and its main guns stayed silent. The preview calls these instead.
    /// Each standing main turret fires its salvo at an enemy of its own inside its arc (the nearest one no other turret
    /// took), the cells a cruise missile at the farthest enemy. Same events and blasts as a battle; only the range's world
    /// calls them, so a battle is unchanged.
    /// </summary>
    internal sealed partial class NavalSystem
    {
        private readonly List<EntityId> _previewTaken = new();

        /// <summary>
        /// Previews: one salvo from each standing main turret, each at its own enemy in its arc and reach. Play-test 14: the
        /// first call lays the turrets (they traverse in <see cref="TrainLaid"/>); a later one fires once they are on, so the
        /// caller calls it again while <see cref="Vehicle.Laying"/>. True when it fired.
        /// </summary>
        internal bool PreviewSalvo(Vehicle v)
        {
            if (!v.IsAlive || v.Def.Salvo is not { } salvo) return false;
            var parts = v.Def.Parts;
            if (!v.Laying)
            {
                _previewTaken.Clear();
                v.LayOrders.Clear();
                for (var i = 0; i < parts.Count; i++)
                {
                    if (parts[i].Kind != "maingun" || v.IsPartBroken(i) || parts[i].Mounts.Count == 0) continue;
                    var m = parts[i].Mounts[0];
                    var foe = PreviewFoe(v, m, v.PartPosition(i), salvo.Range);
                    if (foe == null) continue;
                    _previewTaken.Add(foe.Id);
                    v.LayOrders.Add((i, m, foe.Position));
                }
                if (v.LayOrders.Count == 0) return false;
                v.Laying = true;
                v.LayPreview = true;
                v.LayFrom = _world.Time;
                return false;
            }
            if (!v.LayPreview || !LaidOn(v, _world.Time)) return false;
            v.Laying = false;
            var warning = salvo.Warning != null && _world.Catalog.TryGetSupport(salvo.Warning, out var w) ? w : null;
            var gun = salvo.Weapon != null && _world.Catalog.Weapons.TryGetValue(salvo.Weapon, out var g) ? g : null;
            var together = gun is { Simultaneous: true };
            var fired = false;
            var turret = -1;
            foreach (var (i, m, aim) in v.LayOrders)
            {
                if (v.IsPartBroken(i)) continue;
                turret++;
                var from = v.PartPosition(i);
                Lay(v, m, SimMath.HeadingOf(aim - v.Position));
                // The turret's shells a few metres apart across the line of fire, as a battle's ripple lies along the shore.
                var line = aim - from;
                var across = line.LengthSquared() > 1e-4f ? Vector2.Normalize(new Vector2(line.Y, -line.X)) : new Vector2(1f, 0f);
                for (var s = 0; s < salvo.Shells; s++)
                {
                    var along = salvo.Shells > 1 ? (s - (salvo.Shells - 1) * 0.5f) * 2.5f : 0f;
                    var angle = (float)_world.Random.NextDouble() * SimMath.Tau;
                    var reach = global::MachineBrigade.Sim.Content.SimTunables.Bosses.NavalSystem.PreviewSalvoSqrtScale * MathF.Sqrt((float)_world.Random.NextDouble());
                    var at = _world.ClampToMap(aim + across * along + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * reach);
                    // Play-test 14 (lane G): as a battle's salvo (FireSalvo), an unwarned turret's shells fly at the gun's own shell
                    // speed; the warned time (3.7 s whatever the distance) had them crawl onto a target beside the ship.
                    var flight = warning == null && gun != null && gun.ProjectileSpeed > 1f ? Vector2.Distance(from, at) / gun.ProjectileSpeed : salvo.Warn;
                    if (warning != null) _world.Emit(SimEvent.StrikeWarning(v.Team, warning, at, at, salvo.Warn));
                    _world.Damage.Queue(at, salvo.Blast(ExplosionTier.Huge), flight + global::MachineBrigade.Sim.Content.SimTunables.Bosses.NavalSystem.PreviewSalvoScale * (together ? turret : s), v.Team, v,
                        HitKind.Strike, v.Id);
                    if (gun != null) _world.Emit(SimEvent.Fired(v, m, from, at, flight, EntityId.None));
                }
                fired = true;
            }
            if (fired) v.LastFiredAt = _world.Time;
            return fired;
        }

        /// <summary>Previews: a cruise missile from the launch cells at the farthest enemy on the ground or the water.</summary>
        internal bool PreviewCruise(Vehicle v)
        {
            if (!v.IsAlive || v.Def.Cruise is not { } cruise || v.CruiseOff) return false;
            Vehicle? far = null;
            var best = -1f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying) continue;
                var d = Vector2.DistanceSquared(e.Position, v.Position);
                if (d <= best) continue;
                best = d;
                far = e;
            }
            if (far == null) return false;
            Cruise(v, cruise, far.Position);
            return true;
        }

        /// <summary>The enemy a main turret takes: in its arc and reach, one no other turret took first, the nearest to it.</summary>
        private Vehicle? PreviewFoe(Vehicle v, int mount, Vector2 from, float range)
        {
            Vehicle? pick = null, spare = null;
            float pickD = float.MaxValue, spareD = float.MaxValue;
            var arc = mount >= 0 && mount < v.Def.Mounts.Count ? v.Def.Mounts[mount] : null;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Flying) continue;
                if (range > 0f && Vector2.Distance(e.Position, v.Position) > range) continue;
                if (arc != null && arc.ArcHalf > 0f &&
                    MathF.Abs(SimMath.WrapAngle(SimMath.HeadingOf(e.Position - v.Position) - (v.Heading + arc.ArcCentre))) > arc.ArcHalf) continue;
                var d = Vector2.DistanceSquared(e.Position, from);
                if (_previewTaken.Contains(e.Id))
                {
                    if (d < spareD)
                    {
                        spareD = d;
                        spare = e;
                    }
                    continue;
                }
                if (d >= pickD) continue;
                pickD = d;
                pick = e;
            }
            return pick ?? spare;
        }
    }
}

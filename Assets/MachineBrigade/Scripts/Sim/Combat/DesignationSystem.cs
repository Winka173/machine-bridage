#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Scout Target Designation (10/10): a scout (a vehicle whose def has <c>designationRange</c> above 0: scout_jeep 35 m,
    /// recon_drone 55 m, scout_heli 45 m) marks one enemy at a time. A marked enemy takes extra DIRECT damage from the
    /// scout's side (+10 %, a boss +5 %), never stacked, never for the scouts that hold the mark themselves.
    ///
    /// State: <see cref="Vehicle.DesignationSlots"/> on the target (one slot per scout) and <see cref="Vehicle.DesignationTarget"/>
    /// and <see cref="Vehicle.DesignationNextTick"/> on the scout. All timing is in sim ticks (SimWorld.Tick, 20 a second:
    /// 100 ticks a mark, 40 ticks a re-pick); no float time, no random, no dictionary order; the scan is the world's vehicle
    /// list in order, one scan per scout per 40 ticks (staggered by entity id), and nothing allocates after the first mark.
    ///
    /// Where the bonus goes in the damage pipeline (DamageSystem.Apply), in order: armour/penetration/face/damage-type table
    /// (HitMultiplier) -> smoke -> equipment Outgoing -> commander Outgoing -> THIS (one factor on the direct component) ->
    /// weapon bonuses -> boss air bonus -> HitVehicle (cover, domes, shield, barrier, parts, phases). So it never changes the
    /// penetration table or the armour face, is not seen by crits/statuses a second time, and cover/domes/shields still
    /// absorb the boosted amount. Only HitKind.Direct (and Pierce, a railgun slug) is boosted; Splash, Strike, Mine, Burn
    /// (DOT), Redirect and a hit with no attacker (script, environment, self) are not (unless the data flags say so).
    /// </summary>
    internal sealed class DesignationSystem
    {
        internal const int SlotCount = 4;

        private readonly SimWorld _world;
        private readonly List<Vehicle> _marked = new();

        public DesignationSystem(SimWorld world) => _world = world;

        /// <summary>The targets that carry a live mark now (the HUD draws one reticle on each).</summary>
        public IReadOnlyList<Vehicle> Marked => _marked;

        private static long Ticks(float seconds) => Math.Max(1L, (long)MathF.Round(seconds * 20f));

        /// <summary>Every tick: scouts that are due re-pick and refresh; lapsed marks leave the HUD list.</summary>
        public void Step()
        {
            var list = _world.VehicleList;
            var tick = _world.Tick;
            var interval = Ticks(SimTunables.Vehicles.ScoutDesignation.RetargetSeconds);
            for (var i = 0; i < list.Count; i++)
            {
                var scout = list[i];
                if (scout.Def.DesignationRange <= 0f || !scout.IsAlive) continue;
                if (scout.DesignationNextTick == 0L)
                {
                    scout.DesignationNextTick = tick + scout.Id.Value % interval;
                    continue;
                }
                if (tick < scout.DesignationNextTick) continue;
                scout.DesignationNextTick = tick + interval;
                Refresh(scout, tick);
            }
            for (var i = _marked.Count - 1; i >= 0; i--)
            {
                var t = _marked[i];
                if (t.IsAlive && HasLive(t, tick)) continue;
                _marked[i] = _marked[_marked.Count - 1];
                _marked.RemoveAt(_marked.Count - 1);
            }
        }

        private void Refresh(Vehicle scout, long tick)
        {
            var range = scout.Def.DesignationRange;
            Vehicle? best = null, held = null;
            var bestScore = 0f;
            var heldScore = 0f;
            var list = _world.VehicleList;
            for (var i = 0; i < list.Count; i++)
            {
                var other = list[i];
                if (!Eligible(scout, other, range, out var distance)) continue;
                var score = PickScore(scout, other, distance, range);
                if (other.Id == scout.DesignationTarget)
                {
                    held = other;
                    heldScore = score;
                }
                if (score <= bestScore) continue;
                best = other;
                bestScore = score;
            }
            // Keep the current target unless a clearly more dangerous one is in range (no flip-flopping).
            if (held != null && best != held && bestScore < heldScore * SimTunables.Vehicles.ScoutDesignation.SwitchMargin) best = held;
            var previous = scout.DesignationTarget;
            if (previous.IsValid && (best == null || best.Id != previous) && _world.TryGetVehicle(previous, out var old)) Release(old, scout);
            if (best == null || !Place(best, scout, tick))
            {
                scout.DesignationTarget = default;
                return;
            }
            scout.DesignationTarget = best.Id;
        }

        private bool Eligible(Vehicle scout, Vehicle other, float range, out float distance)
        {
            distance = 0f;
            if (!other.IsAlive || other.Team == scout.Team || other.Team < 0 || scout.Stunned) return false;
            if (other.Invulnerable || other.Def.Untargetable || other.Truce || other.Sworn || other.Def.Obstacle || other.Def.Wall) return false;
            if (_world.Ceasefire(scout.Team, other.Team) || !other.IsVisibleTo(scout.Team)) return false;
            distance = Vector2.Distance(scout.Position, other.Position);
            return distance <= range;
        }

        /// <summary>The scout's pick order: danger to its side first, then long-range fire, the guns that threaten an aircraft scout, heavy/elite, support, the rest.</summary>
        private float PickScore(Vehicle scout, Vehicle other, float distance, float range)
        {
            var w = SimTunables.Vehicles.ScoutDesignation.WeightOther;
            var cls = other.Def.Class;
            if (cls == UnitClass.Support) w = MathF.Max(w, SimTunables.Vehicles.ScoutDesignation.WeightSupport);
            if (other.Def.Boss || other.Def.Elite || cls is UnitClass.Heavy or UnitClass.Tank or UnitClass.TankHunter)
                w = MathF.Max(w, SimTunables.Vehicles.ScoutDesignation.WeightHeavy);
            if (cls == UnitClass.Artillery || other.Def.Weapon.MinRange > 0f) w = MathF.Max(w, SimTunables.Vehicles.ScoutDesignation.WeightArtillery);
            if (scout.Flying && (cls == UnitClass.AntiAir || other.Def.Weapon.CanTarget(true))) w = MathF.Max(w, SimTunables.Vehicles.ScoutDesignation.WeightAirDefence);
            if (other.Target.IsValid && _world.TryGetVehicle(other.Target, out var aimed) && aimed.IsAlive && aimed.Team == scout.Team)
                w = MathF.Max(w, SimTunables.Vehicles.ScoutDesignation.WeightThreat);
            return w * (1f - SimTunables.Vehicles.ScoutDesignation.RangeFalloff * Math.Clamp(distance / MathF.Max(1f, range), 0f, 1f));
        }

        /// <summary>Holds (or refreshes) the scout's slot on the target; false when every slot is held by another live scout.</summary>
        private bool Place(Vehicle target, Vehicle scout, long tick)
        {
            var slots = target.DesignationSlots ??= new DesignationSlot[SlotCount];
            var free = -1;
            for (var i = 0; i < slots.Length; i++)
            {
                if (ReferenceEquals(slots[i].Owner, scout))
                {
                    free = i;
                    break;
                }
                if (free < 0 && !Live(slots[i], tick)) free = i;
            }
            if (free < 0) return false;
            slots[free] = new DesignationSlot { Owner = scout, Team = scout.Team, UntilTick = tick + Ticks(SimTunables.Vehicles.ScoutDesignation.MarkSeconds) };
            if (!_marked.Contains(target)) _marked.Add(target);
            return true;
        }

        /// <summary>The scout hands its mark back (it switched target): only its own slot is cleared.</summary>
        private static void Release(Vehicle target, Vehicle scout)
        {
            var slots = target.DesignationSlots;
            if (slots == null) return;
            for (var i = 0; i < slots.Length; i++)
                if (ReferenceEquals(slots[i].Owner, scout)) slots[i] = default;
        }

        private static bool Live(in DesignationSlot s, long tick) =>
            s.Owner != null && s.UntilTick > tick && s.Owner.IsAlive && s.Owner.Team == s.Team;

        private static bool HasLive(Vehicle target, long tick)
        {
            var slots = target.DesignationSlots;
            if (slots == null) return false;
            for (var i = 0; i < slots.Length; i++)
                if (Live(slots[i], tick)) return true;
            return false;
        }

        /// <summary>Whether <paramref name="team"/> has a live mark on <paramref name="target"/> (AI priority, HUD, tests).</summary>
        public bool IsMarkedFor(Vehicle target, int team)
        {
            var slots = target.DesignationSlots;
            if (slots == null || !target.IsAlive) return false;
            var tick = _world.Tick;
            for (var i = 0; i < slots.Length; i++)
                if (slots[i].Team == team && Live(slots[i], tick)) return true;
            return false;
        }

        /// <summary>The marked-target factor in the allies' existing target score (1 when not marked by the shooter's side).</summary>
        public float PriorityFor(Vehicle shooter, Vehicle target) =>
            target.DesignationSlots != null && IsMarkedFor(target, shooter.Team) ? SimTunables.Vehicles.ScoutDesignation.MarkedPriorityMultiplier : 1f;

        /// <summary>
        /// The damage factor for one hit (see the class summary for its place in the pipeline). 1 when the target carries no
        /// mark, the hit has no attacker (script, environment, self), is friendly fire, is not of an enabled damage group,
        /// or the only marks are the attacker's own.
        /// </summary>
        public float Multiplier(Vehicle target, in HitInfo hit)
        {
            var slots = target.DesignationSlots;
            if (slots == null) return 1f;
            var attacker = hit.Attacker;
            if (attacker == null || hit.Team < 0 || hit.Team == target.Team || !Applies(hit.Kind)) return 1f;
            var tick = _world.Tick;
            var count = 0;
            for (var i = 0; i < slots.Length; i++)
            {
                if (slots[i].Team != hit.Team || !Live(slots[i], tick)) continue;
                if (!SimTunables.Vehicles.ScoutDesignation.ApplyToSelf && ReferenceEquals(slots[i].Owner, attacker)) continue;
                count++;
            }
            if (count == 0) return 1f;
            var bonus = target.Def.Boss ? SimTunables.Vehicles.ScoutDesignation.BossDamageBonus : SimTunables.Vehicles.ScoutDesignation.DamageBonus;
            return 1f + bonus * (SimTunables.Vehicles.ScoutDesignation.Stacking ? count : 1);
        }

        private static bool Applies(HitKind kind) => kind switch
        {
            HitKind.Direct or HitKind.Pierce => SimTunables.Vehicles.ScoutDesignation.AffectsDirect,
            HitKind.Splash => SimTunables.Vehicles.ScoutDesignation.AffectsSplash,
            HitKind.Burn => SimTunables.Vehicles.ScoutDesignation.AffectsDamageOverTime,
            _ => false,
        };
    }
}

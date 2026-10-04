#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>A wreck still on the field: its hull's capsule (spine ends and radius), whether it is afloat, when it is gone.</summary>
    public readonly struct WreckSpot
    {
        public readonly EntityId Id;
        public readonly Vector2 Position, A, B;
        public readonly float Radius;
        public readonly bool Naval;
        public readonly double Until;

        public WreckSpot(EntityId id, Vector2 position, Vector2 a, Vector2 b, float radius, bool naval, double until)
        {
            Id = id;
            Position = position;
            A = a;
            B = b;
            Radius = radius;
            Naval = naval;
            Until = until;
        }

        /// <summary>Half the capsule's length plus its radius: nothing further from its centre touches it.</summary>
        public float Bound => Vector2.Distance(A, Position) + Radius;
    }

    /// <summary>
    /// Play-test 14 (lane J, DECISIONS "Play-test 14 wreck collision (lane J)"): a destroyed ground vehicle's burning hulk
    /// and a ship going down stay solid until they are gone (the hulk has sunk into the ground, the ship under the water):
    /// drivers steer round them (MovementSystem.Drive, NavalSystem.Sail), are pushed out of them (MovementSystem.Separate)
    /// and routes planned after getting stuck pay them as a wall (UnitCostField). How long each lasts is data
    /// (vehicles.wreckRules in tunables.json); the view's hulk sinks on the same clock (WreckManager). Ground wrecks block
    /// ground vehicles only, sinking ships ships only. Aircraft, fixed defences (their ruin opens the ground as before),
    /// walls, drop pods and anything underground leave none. Kept in the order they died, so it is deterministic.
    /// </summary>
    public sealed class WreckField
    {
        private readonly List<WreckSpot> _list = new();
        private int _naval;

        /// <summary>The wrecks on the field now, oldest first.</summary>
        public IReadOnlyList<WreckSpot> List => _list;

        public int Count => _list.Count;

        /// <summary>Ground wrecks on the field now (none: the drivers' checks are skipped).</summary>
        public int GroundCount => _list.Count - _naval;

        /// <summary>Sinking ships on the field now.</summary>
        public int NavalCount => _naval;

        /// <summary>
        /// How long a vehicle's wreck stays solid, s: a ship until it has gone under, a boss's hulk its 90 s, any other hulk
        /// 30-45 s, the spread fixed by its id (so the view sinks it on the same clock without asking the Sim).
        /// </summary>
        public static double Life(VehicleDef def, EntityId id)
        {
            if (def.Naval != null) return SimTunables.Vehicles.WreckRules.ShipSeconds;
            if (def.Boss) return SimTunables.Vehicles.WreckRules.BossSeconds;
            return SimTunables.Vehicles.WreckRules.GroundSeconds + SimTunables.Vehicles.WreckRules.GroundSpread * Spread(id);
        }

        /// <summary>A fixed fraction 0-1 per id (the golden ratio's steps), for the spread of hulks' lives.</summary>
        public static float Spread(EntityId id)
        {
            var x = id.Value * 0.6180339887;
            return (float)(x - Math.Floor(x));
        }

        /// <summary>Whether a destroyed vehicle leaves a solid wreck at all (see the class summary).</summary>
        public static bool Leaves(Vehicle v) =>
            !v.Flying && !v.Def.Static && !v.Def.Wall && !v.IsPod && !v.Burrowed && !v.Escaped && v.Def.Width > 0f;

        /// <summary>A vehicle has just been destroyed: its hull stays where it stopped until its wreck is gone.</summary>
        internal void Add(Vehicle v, double now)
        {
            if (!Leaves(v)) return;
            var half = SimMath.Forward(v.Heading) * v.Def.HullHalf;
            var naval = v.Def.Naval != null;
            _list.Add(new WreckSpot(v.Id, v.Position, v.Position - half, v.Position + half, v.Def.HullRadius, naval, now + Life(v.Def, v.Id)));
            if (naval) _naval++;
        }

        /// <summary>Wrecks whose time is up are gone (once a step, after the dead are removed).</summary>
        internal void Expire(double now)
        {
            for (var i = _list.Count - 1; i >= 0; i--)
            {
                if (_list[i].Until > now) continue;
                if (_list[i].Naval) _naval--;
                _list.RemoveAt(i);
            }
        }

        /// <summary>Whether a disc of <paramref name="radius"/> at <paramref name="p"/> touches a wreck of that kind (ground or afloat).</summary>
        public bool Blocks(Vector2 p, float radius, bool naval)
        {
            foreach (var w in _list)
            {
                if (w.Naval != naval) continue;
                var reach = w.Bound + radius;
                if (Vector2.DistanceSquared(w.Position, p) >= reach * reach) continue;
                MovementSystem.ClosestPoints(p, p, w.A, w.B, out _, out var c);
                if (Vector2.DistanceSquared(p, c) < Square(w.Radius + radius)) return true;
            }
            return false;
        }

        /// <summary>
        /// The nearest wreck of that kind whose hull lies across the probe from <paramref name="front"/> to
        /// <paramref name="probe"/> (a hull's half <paramref name="width"/> either side of it), ahead of <paramref name="from"/>.
        /// </summary>
        internal bool Ahead(Vector2 from, Vector2 front, Vector2 probe, float width, bool naval, out WreckSpot hit)
        {
            hit = default;
            var found = false;
            var nearest = float.MaxValue;
            var forward = probe - from;
            var mid = (front + probe) * 0.5f;
            var span = Vector2.Distance(front, probe) * 0.5f + width;
            foreach (var w in _list)
            {
                if (w.Naval != naval) continue;
                var reach = span + w.Bound;
                if (Vector2.DistanceSquared(w.Position, mid) >= reach * reach) continue;
                var ahead = Vector2.Dot(w.Position - from, forward);
                if (ahead <= 0f || ahead >= nearest) continue;
                MovementSystem.ClosestPoints(front, probe, w.A, w.B, out var c1, out var c2);
                if (Vector2.DistanceSquared(c1, c2) >= Square(width + w.Radius)) continue;
                hit = w;
                nearest = ahead;
                found = true;
            }
            return found;
        }

        /// <summary>
        /// How far (and which way) a hull's capsule <paramref name="a0"/>-<paramref name="a1"/> of <paramref name="radius"/>
        /// sinks into the wrecks of that kind: the sum of the ways out of each, zero when it touches none.
        /// </summary>
        internal Vector2 Overlap(Vector2 centre, Vector2 a0, Vector2 a1, float radius, bool naval)
        {
            var push = Vector2.Zero;
            var bound = Vector2.Distance(a0, centre) + radius;
            foreach (var w in _list)
            {
                if (w.Naval != naval) continue;
                var reach = bound + w.Bound;
                if (Vector2.DistanceSquared(w.Position, centre) >= reach * reach) continue;
                MovementSystem.ClosestPoints(a0, a1, w.A, w.B, out var ca, out var cw);
                var delta = ca - cw;
                var minimum = radius + w.Radius;
                var d2 = delta.LengthSquared();
                if (d2 >= minimum * minimum) continue;
                if (d2 < 1e-6f)
                {
                    // Dead centre on its spine: out the way from the wreck's middle (else a fixed way by its id).
                    var away = centre - w.Position;
                    delta = away.LengthSquared() > 1e-6f ? away : SimMath.Forward((w.Id.Value * 2.39996f) % SimMath.Tau);
                    d2 = delta.LengthSquared();
                    push += delta / MathF.Sqrt(d2) * minimum;
                    continue;
                }
                var d = MathF.Sqrt(d2);
                push += delta / d * (minimum - d);
            }
            return push;
        }

        /// <summary>Folds the wrecks into the state's fingerprint (a checkpoint's replay must bring them back the same).</summary>
        internal void Mix(Action<long> mix)
        {
            mix(_list.Count);
            foreach (var w in _list)
            {
                mix(w.Id.Value);
                mix((long)Math.Round(w.Until * 20.0));
            }
        }

        private static float Square(float x) => x * x;
    }
}

using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Missiles, rockets and bombs drawn as real models. Each flies for its simulated travel time,
    /// with a burning motor and a smoke trail; guided missiles bend towards their target's current
    /// position every frame, so what the player sees lands where the simulation scores the hit.
    /// A missile or rocket with a <see cref="Plume"/> burns a flame cone and leaves a lingering
    /// smoke trail from its tail (<see cref="MotorPlumes"/>); a boosted one leaves the rail slowly,
    /// speeds up hard and then cruises (<see cref="Progress"/>).
    /// </summary>
    internal sealed class ProjectilePool
    {
        private const float TrailSpacing = 0.55f;

        /// <summary>The bomb-run fix, pass 3: a falling bomb's trail puffs, this far apart (m) and lasting this long (s).</summary>
        internal const float StreakSpacing = 0.8f, StreakLife = 0.6f;

        /// <summary>A boosted munition's speed as it leaves the rail, as a share of its cruise speed.</summary>
        internal const float RailSpeed = 0.2f;

        private sealed class Shot
        {
            public Transform Transform;
            public MeshFilter Filter;
            public MeshRenderer Renderer;
            public Vector3 From, To;

            /// <summary>The middle point of a bent path (see <see cref="Launch"/>'s control), used when Bent.</summary>
            public Vector3 Mid;
            public bool Bent;
            public Func<Vector3?> Homing;

            /// <summary>Fix prompt L4: the vehicle a guided round goes for (none for the rest), for the Sim's diversions.</summary>
            public EntityId Target;
            public float Start, Duration, Arc, Trail, PuffT, PuffStep, Wobble, Boost;
            public bool Flame, Active;

            /// <summary>The motor's flame (metres at cruise) and smoke puff size, and when it burns out (share of the flight); 0 length for none.</summary>
            public float PlumeLength, PlumeWidth, PlumeSmoke, Burn;

            /// <summary>Metres between the motor's smoke puffs on High.</summary>
            public float PuffSpacing;

            /// <summary>The model's tail along its length (local metres; negative: behind the pivot).</summary>
            public float Tail;

            /// <summary>The bomb-run fix, pass 3: a falling bomb's thin trail (puff size; 0: none) and its puffs' spacing along the path.</summary>
            public float Streak, StreakStep;

            /// <summary>
            /// Test feedback 19P: a guided round that will miss (the sim's Offset): from <see cref="JamAt"/> of its
            /// flight on it bends off onto its target plus <see cref="Wide"/>, where the sim lands it; a jammed one
            /// (<see cref="Tumble"/>) corkscrews and rolls as it goes, with a crackle as it loses its lock.
            /// </summary>
            public Vector3 Wide;
            public float JamAt;
            public bool Tumble, JamShown;

            /// <summary>An FPV quadcopter: flown level and nose-down with its rotors, buzzing about its line (see FlyAsDrone).</summary>
            public bool Drone;
            public Vector3 Spread;
            public float Phase;
            public Transform Rotors;
        }

        private readonly List<Shot> _shots = new();
        private int _next;
        private float _last = float.NaN;
        private Shot _launched;

        /// <summary>A jammed round lost its lock here, flying this way (the crackle of the jamming is drawn there).</summary>
        public Action<Vector3, Vector3> Jammed;

        /// <summary>The soft-disc material the drones' rotor blur is drawn with (none: no blur).</summary>
        public Material RotorMaterial { get; set; }

        private static Mesh _rotorDiscs;

        /// <summary>Play-test 12: the owning EffectsDirector's shot clock (none: the times given are used as they are).</summary>
        internal ShotClock Clock { get; set; }

        public ProjectilePool(Transform parent, int capacity)
        {
            var root = new GameObject("Projectiles").transform;
            root.SetParent(parent, false);
            _root = root;
            for (var i = 0; i < capacity; i++) _shots.Add(NewShot());
        }

        private readonly Transform _root;

        /// <summary>
        /// Play-test 6 (DECISIONS 21F): the most shots in flight at once. With every slot busy the pool grows (it
        /// used to take the next slot anyway, so a missile in mid-flight jumped back to a launcher as another round:
        /// the jerking missiles of a busy fight, worse since the slower missiles and rockets of 19R and 20W).
        /// </summary>
        internal const int MostShots = 512;

        /// <summary>Shots made so far (tests).</summary>
        internal int Capacity => _shots.Count;

        private Shot NewShot()
        {
            var go = new GameObject("Projectile");
            go.transform.SetParent(_root, false);
            var shot = new Shot
            {
                Transform = go.transform,
                Filter = go.AddComponent<MeshFilter>(),
                Renderer = go.AddComponent<MeshRenderer>(),
            };
            shot.Renderer.shadowCastingMode = ShadowCastingMode.Off;
            shot.Renderer.receiveShadows = false;
            go.SetActive(false);
            return shot;
        }

        /// <param name="homing">Current aim point of a guided missile, or null once its target is gone.</param>
        /// <param name="arc">Peak height of the flight path above the straight line.</param>
        /// <param name="trail">Smoke puff size; 0 for none.</param>
        /// <param name="boost">
        /// 0: flies at one speed. Up to 1: leaves the rail slowly, speeds up hard over the first
        /// <see cref="BoostShare"/> of the flight and then cruises (a missile's launch, boost and
        /// sustainer), arriving on time.
        /// </param>
        /// <param name="scale">How big the model is drawn.</param>
        /// <param name="control">
        /// A lobbed round's path through this point instead of the plain arc (a quadratic curve
        /// from <paramref name="from"/> to <paramref name="to"/>): set along the barrel, the round
        /// leaves down its barrel and bends onto where it lands, its trail on the same curve.
        /// </param>
        /// <param name="streak">
        /// The bomb-run fix, pass 3: a falling bomb's thin trail (no motor): small pale puffs along its path, this big, every
        /// <see cref="StreakSpacing"/> m, gone in <see cref="StreakLife"/> s. 0: none.
        /// </param>
        /// <param name="plume">
        /// The motor's flame and smoke, in lengths of the model as drawn: with one, the flame cone
        /// burns from the model's tail and the smoke trail leaves the tip of the flame (in place of
        /// <paramref name="trail"/>'s puffs); without one, the old small motor puff where there is a trail.
        /// </param>
        public void Launch(ChunkModel model, Vector3 from, Vector3 to, float duration, float arc, float trail, float now,
            Func<Vector3?> homing = null, float wobble = 0f, float delay = 0f, float boost = 0f, float scale = 1f, Vector3? control = null,
            Plume plume = default, float streak = 0f)
        {
            // A free slot if there is one, so a missile in flight does not teleport.
            var shot = _shots[_next];
            for (var k = 0; k < _shots.Count && shot.Active; k++)
            {
                _next = (_next + 1) % _shots.Count;
                shot = _shots[_next];
            }
            if (shot.Active && _shots.Count < MostShots)
            {
                // Every slot is busy: a new one, rather than take a round out of the air.
                shot = NewShot();
                _shots.Insert(_next, shot);
            }
            _next = (_next + 1) % _shots.Count;
            shot.Filter.sharedMesh = model.Mesh;
            shot.Renderer.sharedMaterials = model.Materials;
            shot.From = from;
            shot.To = to;
            shot.Homing = homing;
            shot.Bent = control.HasValue;
            shot.Mid = control ?? Vector3.zero;
            // Fix prompt L4: on the shot clock, so it lands on the Sim tick its damage does (ShotClock).
            shot.Start = ShotClock.Map(Clock, now) + delay;
            shot.Duration = Mathf.Max(0.05f, duration);
            shot.Arc = arc;
            shot.Trail = trail;
            shot.Wobble = wobble;
            shot.Boost = Mathf.Clamp01(boost);
            shot.Transform.localScale = Vector3.one * scale;
            var bounds = model.Mesh != null ? model.Mesh.bounds : new Bounds(Vector3.zero, Vector3.one);
            shot.Tail = bounds.min.z;
            var drawn = bounds.size.z * scale;
            shot.PlumeLength = plume.Burns ? plume.Length * drawn : 0f;
            shot.PlumeWidth = plume.Width * drawn;
            shot.PlumeSmoke = plume.Smoke * shot.PlumeWidth;
            shot.Burn = plume.Burns ? plume.Burn : 0f;
            shot.Flame = plume.Burns || trail > 0f;
            shot.PuffT = 0f;
            shot.PuffSpacing = Mathf.Max(0.15f, shot.PlumeSmoke * plume.Puffs);
            shot.PuffStep = TrailSpacing / Mathf.Max(1f, Vector3.Distance(from, to) + arc);
            shot.Streak = Mathf.Max(0f, streak);
            shot.StreakStep = StreakSpacing / Mathf.Max(1f, Vector3.Distance(from, to) + arc);
            shot.Wide = Vector3.zero;
            shot.JamAt = 0f;
            shot.Tumble = shot.JamShown = shot.Drone = false;
            shot.Target = default;
            shot.Spread = Vector3.zero;
            shot.Phase = UnityEngine.Random.value * 100f;
            if (shot.Rotors != null) shot.Rotors.gameObject.SetActive(false);
            shot.Active = true;
            shot.Transform.gameObject.SetActive(delay <= 0f);
            _launched = shot;
            Place(shot, 0f);
        }

        /// <summary>Fix prompt L4: the round just launched goes for <paramref name="target"/> (a guided round), so the Sim can divert it in flight.</summary>
        public void Tag(EntityId target)
        {
            if (_launched != null) _launched.Target = target;
        }

        /// <summary>
        /// Fix prompt L4: the Sim took a guided round off <paramref name="target"/> in flight (a flare, lost sight, out of
        /// reach, SimEventKind.RoundDiverted): of the rounds going for it, the one due nearest <paramref name="remaining"/> s
        /// from <paramref name="now"/> turns onto <paramref name="to"/> (it eases round within a few frames, HomingRate) and
        /// arrives there on time, where its burst is drawn. False when none was drawn (off screen when fired).
        /// </summary>
        public bool Divert(EntityId target, Vector3 to, float remaining, float now)
        {
            now = ShotClock.Map(Clock, now);
            Shot best = null;
            var bestGap = float.MaxValue;
            foreach (var shot in _shots)
            {
                if (!shot.Active || !shot.Target.IsValid || shot.Target != target) continue;
                var gap = Mathf.Abs(shot.Start + shot.Duration - now - remaining);
                if (gap >= bestGap) continue;
                bestGap = gap;
                best = shot;
            }
            if (best == null || bestGap > 0.35f) return false;
            best.Homing = () => to;
            best.Wide = Vector3.zero;
            best.JamAt = 0f;
            best.Target = default;
            return true;
        }

        /// <summary>
        /// The round just launched will not reach its target: it bends off from <paramref name="at"/> of its flight
        /// onto the target plus <paramref name="wide"/>; <paramref name="tumble"/> for a jammed one (see <see cref="Shot.Wide"/>).
        /// </summary>
        public void Veer(Vector3 wide, float at, bool tumble)
        {
            if (_launched == null) return;
            _launched.Wide = wide;
            _launched.JamAt = Mathf.Clamp(at, 0.05f, 0.9f);
            _launched.Tumble = tumble;
        }

        /// <summary>
        /// Test feedback 19P: the round just launched is an FPV quadcopter: it flies level with its nose a little down
        /// and its rotors blurred, weaving and bobbing with small corrections about a line of its own
        /// (<paramref name="spread"/>: how far out from the swarm's middle, most at mid-flight), then tips over into its dive.
        /// </summary>
        public void FlyAsDrone(Vector3 spread)
        {
            if (_launched == null) return;
            var shot = _launched;
            shot.Drone = true;
            shot.Spread = spread;
            Place(shot, 0f);
            if (RotorMaterial == null) return;
            if (shot.Rotors == null)
            {
                _rotorDiscs ??= RotorDiscs();
                var go = new GameObject("Rotors");
                go.transform.SetParent(shot.Transform, false);
                go.layer = shot.Transform.gameObject.layer;
                go.AddComponent<MeshFilter>().sharedMesh = _rotorDiscs;
                var renderer = go.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = RotorMaterial;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                shot.Rotors = go.transform;
            }
            shot.Rotors.gameObject.SetActive(true);
        }

        /// <summary>Four soft discs where the quadcopter's props turn (the fpv_drone model: props 0.16 m out on each diagonal).</summary>
        private static Mesh RotorDiscs()
        {
            var colour = Primitives.Linear(new Color(0.42f, 0.44f, 0.46f, 0.5f));
            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var colours = new List<Color>();
            var triangles = new List<int>();
            foreach (var (x, z) in new[] { (1f, 1f), (-1f, 1f), (-1f, -1f), (1f, -1f) })
            {
                var c = new Vector3(x * 0.16f, 0.056f, z * 0.16f);
                var b = vertices.Count;
                const float r = 0.15f;
                vertices.Add(c + new Vector3(-r, 0f, -r));
                vertices.Add(c + new Vector3(r, 0f, -r));
                vertices.Add(c + new Vector3(r, 0f, r));
                vertices.Add(c + new Vector3(-r, 0f, r));
                uvs.Add(new Vector2(0f, 0f));
                uvs.Add(new Vector2(1f, 0f));
                uvs.Add(new Vector2(1f, 1f));
                uvs.Add(new Vector2(0f, 1f));
                for (var k = 0; k < 4; k++) colours.Add(colour);
                // Both faces: seen from above in level flight, from the side as it tips over into the dive.
                triangles.AddRange(new[] { b, b + 2, b + 1, b, b + 3, b + 2, b, b + 1, b + 2, b, b + 2, b + 3 });
            }
            var mesh = new Mesh { name = "RotorDiscs" };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetColors(colours);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>How far a missing round has bent off onto its landing point (0 before it lost its lock, 1 at the end).</summary>
        private static float Veering(Shot shot, float t)
        {
            if (shot.JamAt <= 0f || t <= shot.JamAt) return 0f;
            var u = Mathf.Clamp01((t - shot.JamAt) / (1f - shot.JamAt));
            return u * u * (3f - 2f * u);
        }

        public void Tick(float now, Emitters emitters)
        {
            now = ShotClock.Map(Clock, now);
            // A clock that went back (a new battle): start over.
            if (!float.IsNaN(_last) && now < _last - 0.5f) _last = float.NaN;
            // The shot clock stands still while the Sim does (the Sandbox paused): the rounds hold where they are, no motor smoke piles up.
            var still = !float.IsNaN(_last) && now <= _last;
            var dt = float.IsNaN(_last) || now <= _last ? 1f / 30f : Mathf.Min(0.1f, now - _last);
            _last = now;
            var plumes = emitters.Plumes;
            plumes.Frame();
            foreach (var shot in _shots)
            {
                if (!shot.Active || now < shot.Start) continue;
                if (!shot.Transform.gameObject.activeSelf) shot.Transform.gameObject.SetActive(true);
                var t = (now - shot.Start) / shot.Duration;
                if (t >= 1f)
                {
                    shot.Active = false;
                    shot.Transform.gameObject.SetActive(false);
                    continue;
                }
                if (shot.Homing != null)
                {
                    var aim = shot.Homing();
                    // Play-test 6 (DECISIONS 21F): eased by the frame's time, not a fixed share a frame (the same line at 30 or 144 fps).
                    if (aim.HasValue) shot.To = Vector3.Lerp(shot.To, aim.Value + shot.Wide * Veering(shot, t), 1f - Mathf.Exp(-HomingRate * dt));
                }
                if (shot.JamAt > 0f && !shot.JamShown && t >= shot.JamAt)
                {
                    shot.JamShown = true;
                    if (shot.Tumble) Jammed?.Invoke(shot.Transform.position, shot.Transform.forward);
                }
                Place(shot, t);
                if (still) continue;
                if (shot.Rotors != null && shot.Drone)
                    shot.Rotors.localScale = Vector3.one * (0.92f + 0.16f * Mathf.PerlinNoise(now * 23f, shot.Phase));
                var forward = shot.Transform.forward;
                if (shot.PlumeLength > 0f)
                {
                    if (t > shot.Burn) continue;
                    var nozzle = shot.Transform.TransformPoint(new Vector3(0f, 0f, shot.Tail));
                    var speed = SpeedAt(shot.Boost, t);
                    // The flame flies with the missile, so its cone stays on the tail.
                    var velocity = (PositionAt(shot, Mathf.Min(1f, t + dt / shot.Duration)) - shot.Transform.position) / dt;
                    if (velocity.sqrMagnitude < 0.25f) velocity = forward * 0.5f;
                    plumes.Burn(nozzle, forward, velocity, shot.PlumeLength, shot.PlumeWidth, speed, dt);
                    // The smoke leaves the tip of the flame: puffs only where the flame has passed.
                    var path = Mathf.Max(1f, Vector3.Distance(shot.From, shot.To) + shot.Arc);
                    var behind = (shot.PlumeLength * 0.7f - shot.Tail * shot.Transform.localScale.z) / path;
                    var step = shot.PuffSpacing * plumes.SmokeSpacing / path;
                    while (shot.PuffT + step <= t - behind)
                    {
                        shot.PuffT += step;
                        plumes.Smoke(PositionAt(shot, shot.PuffT), -forward, shot.PlumeSmoke);
                    }
                    continue;
                }
                if (shot.Streak > 0f)
                {
                    // A falling bomb's trail: pale puffs left along its path, no motor.
                    while (shot.PuffT + shot.StreakStep <= t)
                    {
                        shot.PuffT += shot.StreakStep;
                        emitters.Contrail(PositionAt(shot, shot.PuffT), shot.Streak, StreakLife);
                    }
                    continue;
                }
                if (shot.Trail <= 0f) continue;
                while (shot.PuffT + shot.PuffStep <= t)
                {
                    shot.PuffT += shot.PuffStep;
                    emitters.Trail(PositionAt(shot, shot.PuffT), shot.Trail);
                }
                emitters.Motor(shot.Transform.position - forward * 0.6f, forward, shot.Trail);
            }
        }

        /// <summary>How fast a guided round's aim point follows its target (1/s; the old 0.35 a frame at 30 fps).</summary>
        private const float HomingRate = 13f;

        /// <summary>Share of the flight the boost takes, at full boost.</summary>
        internal const float BoostShare = 0.35f;

        /// <summary>
        /// How far along its path a munition is at <paramref name="t"/> (share of its flight time).
        /// Boosted: it leaves the rail at <see cref="RailSpeed"/> of its cruise speed, speeds up
        /// evenly to cruise over the first <c>boost x BoostShare</c> of the flight, then cruises,
        /// arriving at the end of its flight (the simulation's travel time).
        /// </summary>
        internal static float Progress(float boost, float t)
        {
            var tb = Mathf.Clamp01(boost) * BoostShare;
            if (tb <= 0f) return t;
            var cruise = 1f / (1f - tb * (1f - RailSpeed) * 0.5f);
            if (t >= tb) return cruise * (tb * (1f + RailSpeed) * 0.5f + (t - tb));
            return cruise * (RailSpeed * t + (1f - RailSpeed) * t * t / (2f * tb));
        }

        /// <summary>A boosted munition's speed at <paramref name="t"/> as a share of its cruise speed (1 when not boosted).</summary>
        internal static float SpeedAt(float boost, float t)
        {
            var tb = Mathf.Clamp01(boost) * BoostShare;
            return tb <= 0f || t >= tb ? 1f : RailSpeed + (1f - RailSpeed) * t / tb;
        }

        private static Vector3 PositionAt(Shot shot, float t)
        {
            t = Progress(shot.Boost, t);
            var p = shot.Bent
                ? Vector3.Lerp(Vector3.Lerp(shot.From, shot.Mid, t), Vector3.Lerp(shot.Mid, shot.To, t), t)
                : Vector3.Lerp(shot.From, shot.To, t) + Vector3.up * (shot.Arc * 4f * t * (1f - t));
            var side = Vector3.Cross(Vector3.up, (shot.To - shot.From).normalized);
            if (shot.Drone)
            {
                // A quadcopter weaves and bobs about its own line out from the swarm's, correcting all the way,
                // steadier off the rack and settling onto the target at the end.
                var raw = Mathf.Clamp01(t);
                p += shot.Spread * Mathf.Pow(Mathf.Sin(raw * Mathf.PI), 0.8f);
                var settle = Mathf.Clamp01(raw * 6f) * Mathf.Clamp01((1f - raw) * 4f);
                var ph = shot.Phase;
                p += side * ((Mathf.Sin(raw * 13f + ph) * 0.5f + Mathf.Sin(raw * 31f + ph * 1.7f) * 0.2f) * settle)
                     + Vector3.up * (Mathf.Sin(raw * 17f + ph * 0.6f) * 0.35f * settle);
            }
            else if (shot.Wobble > 0f)
            {
                // Unguided rockets corkscrew a little as they leave the tube.
                p += side * (Mathf.Sin(t * 19f + shot.Start * 7f) * shot.Wobble * (1f - t));
            }
            if (shot.Tumble && t > shot.JamAt)
            {
                // A jammed missile corkscrews off its line, widest halfway to where it comes down.
                var u = Mathf.Clamp01((t - shot.JamAt) / (1f - shot.JamAt));
                var turn = u * 24f + shot.Phase;
                p += (side * Mathf.Cos(turn) + Vector3.up * Mathf.Sin(turn)) * (Mathf.Sin(u * Mathf.PI) * 2.2f);
            }
            return p;
        }

        private static void Place(Shot shot, float t)
        {
            var here = PositionAt(shot, t);
            var ahead = PositionAt(shot, Mathf.Min(1f, t + 0.02f));
            shot.Transform.position = here;
            var direction = ahead - here;
            if (direction.sqrMagnitude < 1e-6f) direction = shot.To - shot.From;
            // Models point their nose along -Z after import (Blender -Y front arrives as Unity +Z), so look along +Z.
            if (direction.sqrMagnitude <= 1e-6f) return;
            if (shot.Drone)
            {
                // Level along its heading with the nose a little down (how a quadcopter flies forward), banking in
                // its weaves; in the last stretch it tips over and dives nose first onto the target.
                var flat = new Vector3(direction.x, 0f, direction.z);
                var yaw = flat.sqrMagnitude > 1e-6f ? Quaternion.LookRotation(flat) : Quaternion.Euler(0f, shot.Transform.eulerAngles.y, 0f);
                var dive = Mathf.Clamp01((t - 0.74f) / 0.18f);
                var slope = -Mathf.Atan2(direction.y, Mathf.Max(1e-4f, flat.magnitude)) * Mathf.Rad2Deg;
                var pitch = Mathf.Lerp(14f, Mathf.Clamp(slope, 14f, 80f), dive);
                var roll = (Mathf.Sin(t * 13f + shot.Phase) * 16f + Mathf.Sin(t * 37f + shot.Phase) * 5f) * (1f - dive);
                shot.Transform.rotation = yaw * Quaternion.Euler(pitch, 0f, roll);
                return;
            }
            var look = Quaternion.LookRotation(direction);
            if (shot.Tumble && t > shot.JamAt)
            {
                // Rolling over and over, the nose wandering.
                var u = (t - shot.JamAt) / Mathf.Max(0.05f, 1f - shot.JamAt);
                look *= Quaternion.Euler(Mathf.Sin(u * 17f + shot.Phase) * 28f, Mathf.Cos(u * 13f + shot.Phase) * 22f, u * 900f);
            }
            shot.Transform.rotation = look;
        }
    }
}

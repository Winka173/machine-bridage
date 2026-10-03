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

            /// <summary>
            /// Play-test 13 follow-up (lane A): a flight-profile path (<see cref="FlyLoft"/>, <see cref="FlyBallistic"/>): a
            /// cubic curve from <see cref="From"/> through <c>From + Out</c> (the climb out of the tube or barrel) and
            /// <c>To + up x Rise - ahead x Back x ground</c> (the dive or fall, kept on the live aim point) to <see cref="To"/>.
            /// <see cref="Level"/>: paced evenly over the ground (a ballistic round), else evenly along its length (a missile).
            /// </summary>
            public bool Curve, Level;
            public Vector3 Out;
            public float Rise, Back;

            /// <summary>The curve's running length at <see cref="CurveSteps"/> even steps of its parameter, for the aim point <see cref="LutTo"/>.</summary>
            public float[] Lut;
            public Vector3 LutTo;
            public bool LutValid;

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
            shot.Curve = shot.Level = shot.LutValid = false;
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
        /// Play-test 13 follow-up (lane A), FlightProfile.Loft: the round just launched (a tube- or box-launched missile: top
        /// attack, VLS, coastal box, SAM box) climbs out along <paramref name="launch"/> (a steep climb, see
        /// WeaponEffects.LoftLaunch), arcs over at about <paramref name="peak"/> m above the line (the Sim's ArcShare x ground
        /// distance) and dives steeply onto its target (<see cref="LoftDive"/>). It still lands on its aim point at the end of
        /// its flight (the ShotClock rule): only the shape of the path changes.
        /// </summary>
        public void FlyLoft(Vector3 launch, float peak)
        {
            if (_launched == null) return;
            Curve(_launched, launch, peak, false);
        }

        /// <summary>
        /// Play-test 13 follow-up (lane A), FlightProfile.Ballistic: the round just launched (an artillery shell or rocket, a
        /// ballistic missile) flies a high arc peaking <paramref name="peak"/> m above the line (the Sim's ArcShare x ground
        /// distance), at an even pace over the ground like a real ballistic round (fast off the barrel, slow over the top,
        /// plunging at the end). It leaves along <paramref name="launch"/> (the raised barrel, tubes or erector; zero: the
        /// plain parabola's angle) and comes down at least as steeply as it went up. It lands on its aim point on time.
        /// </summary>
        public void FlyBallistic(Vector3 launch, float peak)
        {
            if (_launched == null) return;
            Curve(_launched, launch, peak, true);
        }

        /// <summary>A lofted round's dive: its last inner control point sits this share of the ground distance short of the target (a 55-60 degree dive).</summary>
        internal const float LoftDive = 0.18f;

        /// <summary>Even steps of a profile curve's length table (enough for a smooth pace; rebuilt once a frame for a homing round).</summary>
        internal const int CurveSteps = 16;

        private static void Curve(Shot shot, Vector3 launch, float peak, bool level)
        {
            var flat = new Vector3(shot.To.x - shot.From.x, 0f, shot.To.z - shot.From.z);
            var ground = flat.magnitude;
            var ahead = ground > 1e-3f ? flat / ground : new Vector3(shot.Transform.forward.x, 0f, shot.Transform.forward.z);
            if (ahead.sqrMagnitude < 1e-6f) ahead = Vector3.forward;
            ahead.Normalize();
            var (rise, sideways, back, along) = CurveShape(launch, ahead, ground, peak, level);
            shot.Curve = true;
            shot.Level = level;
            shot.Bent = false;
            shot.Rise = rise;
            shot.Out = Vector3.up * rise + along * sideways;
            shot.Back = ground > 1e-3f ? back / ground : 0f;
            shot.LutValid = false;
            // Its smoke and streak puffs keep their spacing along the longer path.
            var length = CurveLength(shot);
            shot.Arc = Mathf.Max(0f, length - Vector3.Distance(shot.From, shot.To));
            shot.PuffStep = TrailSpacing / Mathf.Max(1f, length);
            shot.StreakStep = StreakSpacing / Mathf.Max(1f, length);
            Place(shot, 0f);
        }

        /// <summary>
        /// A profile curve's shape: the height of both inner control points (<c>peak / 0.75</c>: a cubic whose inner points
        /// stand level peaks at three quarters of their height), how far out over the ground the first one stands and which
        /// way (along the launch's heading, else straight at the target; the launch's angle sets the distance), and how far
        /// short of the target the second one stands (the fall's or dive's steepness). A ballistic round's first point stands
        /// 0.15-0.6 of the ground distance out (a third with a third back is the plain parabola, paced exactly like the Sim's
        /// round height), its second one as far back up to a third (a low barrel's round comes down steeper than it went up,
        /// as a real shell does); the two never cross, so the ground run only goes forward. A lofted one's first point stands
        /// 0.04-0.4 out (0.04: near straight up out of a VLS cell), its second <see cref="LoftDive"/> back.
        /// </summary>
        internal static (float rise, float sideways, float back, Vector3 along) CurveShape(Vector3 launch, Vector3 ahead, float ground, float peak, bool level)
        {
            var rise = Mathf.Max(peak, 0.6f) / 0.75f;
            var along = ahead;
            var sideways = ground / 3f;
            if (launch.sqrMagnitude > 1e-4f)
            {
                var dir = launch.normalized;
                var heading = new Vector3(dir.x, 0f, dir.z);
                var outward = heading.magnitude;
                // A launch that points back or far off the target's way (a launcher not laid yet) is not followed.
                if (outward > 0.05f && Vector3.Dot(heading / outward, ahead) > 0.5f) along = heading / outward;
                if (dir.y > 0.02f) sideways = rise * outward / dir.y;
            }
            // A lofted round always leans a little toward its target (a VLS cell's too), so its heading is never undefined.
            if (!level) return (rise, Mathf.Clamp(sideways, ground * 0.04f, ground * 0.4f), ground * LoftDive, along);
            sideways = Mathf.Clamp(sideways, ground * 0.15f, ground * 0.6f);
            return (rise, sideways, Mathf.Min(sideways, ground / 3f), along);
        }

        /// <summary>A point on a cubic curve.</summary>
        internal static Vector3 Cubic(Vector3 a, Vector3 b, Vector3 c, Vector3 d, float u)
        {
            var v = 1f - u;
            return v * v * v * a + 3f * v * v * u * b + 3f * v * u * u * c + u * u * u * d;
        }

        /// <summary>The curve's two inner control points for the shot's live aim point.</summary>
        private static void Controls(Shot shot, out Vector3 b, out Vector3 c)
        {
            var flat = new Vector3(shot.To.x - shot.From.x, 0f, shot.To.z - shot.From.z);
            var ground = flat.magnitude;
            b = shot.From + shot.Out;
            c = shot.To + Vector3.up * shot.Rise - (ground > 1e-3f ? flat / ground : Vector3.zero) * (shot.Back * ground);
        }

        private static float CurveLength(Shot shot)
        {
            Controls(shot, out var b, out var c);
            var length = 0f;
            var last = shot.From;
            for (var i = 1; i <= CurveSteps; i++)
            {
                var q = Cubic(shot.From, b, c, shot.To, i / (float)CurveSteps);
                length += Vector3.Distance(last, q);
                last = q;
            }
            return length;
        }

        /// <summary>
        /// Where a profile round is at <paramref name="s"/> of its way (after the boost's pacing): the curve's parameter that
        /// covers that share of its length (a lofted missile) or of its ground run (a ballistic round), from a small length
        /// table rebuilt when the aim point moves.
        /// </summary>
        private static Vector3 CurveAt(Shot shot, float s)
        {
            Controls(shot, out var b, out var c);
            var lut = shot.Lut ??= new float[CurveSteps + 1];
            if (!shot.LutValid || (shot.To - shot.LutTo).sqrMagnitude > 1e-4f)
            {
                lut[0] = 0f;
                var last = shot.From;
                for (var i = 1; i <= CurveSteps; i++)
                {
                    var q = Cubic(shot.From, b, c, shot.To, i / (float)CurveSteps);
                    var step = q - last;
                    if (shot.Level) step.y = 0f;
                    lut[i] = lut[i - 1] + step.magnitude;
                    last = q;
                }
                shot.LutTo = shot.To;
                shot.LutValid = true;
            }
            return Cubic(shot.From, b, c, shot.To, CurveParameter(lut, Mathf.Clamp01(s)));
        }

        /// <summary>The curve's parameter that covers <paramref name="s"/> of a running-length table (linear between its steps).</summary>
        internal static float CurveParameter(float[] lut, float s)
        {
            var steps = lut.Length - 1;
            var total = lut[steps];
            if (total <= 1e-4f) return s;
            var want = s * total;
            var k = 1;
            while (k < steps && lut[k] < want) k++;
            var span = lut[k] - lut[k - 1];
            return (k - 1 + (span > 1e-6f ? Mathf.Clamp01((want - lut[k - 1]) / span) : 0f)) / steps;
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
                    // Play-test 14 ("vệt khói bị cắt gần mục tiêu"): the smoke left the flame's tip, a flame's length behind the
                    // missile, so the last stretch to the target never got its puffs: they are laid now, up to the impact.
                    if (!still) FinishTrail(shot, plumes, emitters);
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

        /// <summary>Play-test 14: the rest of a motor's smoke trail, from its last puff to the impact point, as the round lands.</summary>
        private void FinishTrail(Shot shot, MotorPlumes plumes, Emitters emitters)
        {
            var back = -shot.Transform.forward;
            if (shot.PlumeLength > 0f && shot.PlumeSmoke > 0f)
            {
                var path = Mathf.Max(1f, Vector3.Distance(shot.From, shot.To) + shot.Arc);
                var step = shot.PuffSpacing * plumes.SmokeSpacing / path;
                if (step <= 0f) return;
                while (shot.PuffT + step <= 1f)
                {
                    shot.PuffT += step;
                    plumes.Smoke(PositionAt(shot, shot.PuffT), back, shot.PlumeSmoke);
                }
                return;
            }
            if (shot.Streak > 0f || shot.Trail <= 0f || shot.PuffStep <= 0f) return;
            while (shot.PuffT + shot.PuffStep <= 1f)
            {
                shot.PuffT += shot.PuffStep;
                emitters.Trail(PositionAt(shot, shot.PuffT), shot.Trail);
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
            var p = shot.Curve ? CurveAt(shot, t)
                : shot.Bent ? Vector3.Lerp(Vector3.Lerp(shot.From, shot.Mid, t), Vector3.Lerp(shot.Mid, shot.To, t), t)
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

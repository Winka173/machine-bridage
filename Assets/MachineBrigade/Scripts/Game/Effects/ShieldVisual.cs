using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// One shield as the player sees it, in the look every shield shares (prompt 11C, Shield.shader):
    /// a skin of hexagonal tiles, bright at its rim and nearly clear in the middle, blue for our
    /// side and red-orange for the enemy's. The owner places it (a dome stands on the ground, its
    /// base at the transform's origin, scaled to its radius and height; a bubble is centred on the
    /// transform and scaled to its three radii), says whose it is and, every frame, how much it
    /// flickers, then calls <see cref="Tick"/>. Hits ripple it; it comes up, fades out or shatters.
    /// Visual only: the simulation decides where shields stand and what they stop.
    /// </summary>
    /// <remarks>
    /// One shared material per variant (full, and the Low graphics one); each shield's own state
    /// lives in a <see cref="MaterialPropertyBlock"/>, so a shield needs no clean-up beyond its
    /// GameObject (a vehicle view is simply destroyed). Meshes are built once per size and kept.
    /// Nothing is allocated per frame.
    /// </remarks>
    public sealed class ShieldVisual
    {
        public enum Shape
        {
            /// <summary>A hemisphere standing on the ground (the fortress, the item, an objective).</summary>
            Dome,

            /// <summary>A whole sphere round a vehicle.</summary>
            Bubble,
        }

        private const int RippleSlots = 4;
        private const float RippleLife = 0.8f;
        private const float RiseSeconds = 0.4f;
        private const float FadeSeconds = 0.3f;

        /// <summary>How long a shield takes to shatter and be gone.</summary>
        public const float CollapseSeconds = 0.9f;

        /// <summary>The angle between neighbouring tiles of the coarsest mesh (an icosahedron's edge, 63.4 degrees).</summary>
        private const float IcosahedronEdge = 1.1071f;

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly int IntensityId = Shader.PropertyToID("_Intensity");
        private static readonly int NowId = Shader.PropertyToID("_Now");
        private static readonly int PowerId = Shader.PropertyToID("_Power");
        private static readonly int FlickerId = Shader.PropertyToID("_Flicker");
        private static readonly int CollapseId = Shader.PropertyToID("_Collapse");
        private static readonly int HitId = Shader.PropertyToID("_Hit");
        private static readonly int CellId = Shader.PropertyToID("_Cell");
        private static readonly int ReachId = Shader.PropertyToID("_Reach");
        private static readonly int LineId = Shader.PropertyToID("_Line");
        private static readonly int GroundId = Shader.PropertyToID("_Ground");

        private static readonly int[] RippleIds =
        {
            Shader.PropertyToID("_Ripple0"), Shader.PropertyToID("_Ripple1"), Shader.PropertyToID("_Ripple2"), Shader.PropertyToID("_Ripple3"),
        };

        private static readonly Vector4 NoRipple = new(0f, 1f, 0f, -100f);

        /// <summary>
        /// Forces the Low graphics variant on or off (editor shots); null follows the graphics
        /// tier in force. Read when a shield is made (changing graphics rebuilds the battle).
        /// </summary>
        public static bool? LiteOverride { get; set; }

        private static bool LiteNow => LiteOverride ?? Match.MatchSettings.Tier == Match.GraphicsQuality.Low;

        private static Material _full, _lite;
        private static readonly Dictionary<(int level, bool dome), Mesh> Meshes = new();

        private readonly MeshRenderer _renderer;
        private readonly MaterialPropertyBlock _block = new();
        private readonly Vector4[] _ripples = new Vector4[RippleSlots];
        private readonly Shape _shape;
        private float _raisedAt = -100f, _loweredAt = -1f, _collapseAt = -1f, _hitAt = -100f, _hitAmount;
        private float _intensity = 1f;
        private float _rise = RiseSeconds;
        private bool _shown;

        /// <param name="radius">Its size in metres across the ground (a dome's radius, a bubble's widest), for its tiles and ripples.</param>
        public ShieldVisual(string name, Transform parent, Shape shape, float radius)
        {
            _shape = shape;
            var lite = LiteNow;
            var level = Level(shape, radius, lite);
            var go = new GameObject(name);
            Transform = go.transform;
            Transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = MeshFor(level, shape == Shape.Dome);
            _renderer = go.AddComponent<MeshRenderer>();
            _renderer.sharedMaterial = MaterialFor(lite);
            _renderer.shadowCastingMode = ShadowCastingMode.Off;
            _renderer.receiveShadows = false;
            _renderer.lightProbeUsage = LightProbeUsage.Off;
            _renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            _renderer.motionVectorGenerationMode = MotionVectorGenerationMode.ForceNoMotion;
            for (var i = 0; i < RippleSlots; i++) _ripples[i] = NoRipple;
            // Tiles about five metres across on a dome, a metre or two on a bubble; a ripple runs
            // a fifth of a big dome's width, or right round a bubble.
            var cell = Mathf.Max(0.3f, radius * IcosahedronEdge / (1 << level));
            _block.SetFloat(CellId, cell);
            _block.SetFloat(ReachId, shape == Shape.Dome ? Mathf.Clamp(radius * 0.35f, cell * 3f, 22f) : radius * 1.2f);
            _block.SetFloat(LineId, shape == Shape.Dome ? 0.07f : 0.1f);
            _block.SetFloat(GroundId, shape == Shape.Dome ? 1f : 0f);
            SetSide(false);
            go.SetActive(false);
        }

        public Transform Transform { get; }

        /// <summary>Drawn: standing, coming up, fading out or shattering.</summary>
        public bool Shown => _shown;

        /// <summary>Up and not on its way down.</summary>
        public bool Standing => _shown && _collapseAt < 0f && _loweredAt < 0f;

        /// <summary>0 steady to 1 failing: the owner sets it every frame (a damaged generator, a shield running out).</summary>
        public float Flicker { get; set; }

        /// <summary>Brightness relative to the usual (a gear barrier's bubble is fainter).</summary>
        public float Intensity
        {
            get => _intensity;
            set
            {
                _intensity = value;
                _block.SetFloat(IntensityId, BaseIntensity * value);
            }
        }

        private float BaseIntensity => _shape == Shape.Dome ? 2.2f : 2f;

        /// <summary>Ours clear blue, the enemy's red-orange (orange in the colour-blind palette, against the same blue).</summary>
        public static Color SideColour(bool ours) => TeamColors.Palette == 1
            ? ours ? new Color(0.22f, 0.56f, 1f) : new Color(1f, 0.56f, 0.08f)
            : ours ? new Color(0.24f, 0.66f, 1f) : new Color(1f, 0.2f, 0.05f);

        public void SetSide(bool ours)
        {
            // Linear, set as a vector: no colour-space conversion to second-guess.
            _block.SetVector(ColorId, SideColour(ours).linear);
            _block.SetFloat(IntensityId, BaseIntensity * _intensity);
        }

        /// <summary>Comes up (fading in over <paramref name="seconds"/>; 0: at once).</summary>
        public void Raise(float now, float seconds = RiseSeconds)
        {
            if (Standing) return;
            // Coming back while it fades: from where it is.
            _raisedAt = now;
            _rise = Mathf.Max(0.001f, seconds);
            _loweredAt = -1f;
            _collapseAt = -1f;
            for (var i = 0; i < RippleSlots; i++) _ripples[i] = NoRipple;
            _hitAmount = 0f;
            _shown = true;
            if (!Transform.gameObject.activeSelf) Transform.gameObject.SetActive(true);
        }

        /// <summary>Fades out quietly (no longer needed: a dome over it has taken over).</summary>
        public void Lower(float now)
        {
            if (!Standing) return;
            _loweredAt = now;
        }

        /// <summary>Gives way: a flare, then its tiles break one by one and fly off (<see cref="CollapseSeconds"/>).</summary>
        public void Collapse(float now)
        {
            if (!_shown || _collapseAt >= 0f) return;
            _collapseAt = now;
            _loweredAt = -1f;
        }

        /// <summary>Gone at once.</summary>
        public void Hide()
        {
            _shown = false;
            _collapseAt = -1f;
            _loweredAt = -1f;
            if (Transform != null && Transform.gameObject.activeSelf) Transform.gameObject.SetActive(false);
        }

        /// <summary>
        /// A round struck it at <paramref name="world"/> (or landed inside): a ripple from that
        /// point of its skin. A dome takes the point straight above; a bubble the point towards
        /// <paramref name="towardsCamera"/> from it, so the ripple is on the side the player sees.
        /// </summary>
        public void Hit(Vector3 world, float now, Vector3 towardsCamera = default, float strength = 1f)
        {
            if (!Standing) return;
            var local = Transform.InverseTransformPoint(world);
            Vector3 skin;
            if (_shape == Shape.Dome)
            {
                var across = Mathf.Sqrt(local.x * local.x + local.z * local.z);
                // Far outside: it never touched the dome.
                if (across > 1.25f) return;
                skin = across < 0.97f
                    ? new Vector3(local.x, Mathf.Sqrt(1f - across * across), local.z)
                    : new Vector3(local.x / across * 0.97f, 0.24f, local.z / across * 0.97f);
            }
            else
            {
                var bias = towardsCamera.sqrMagnitude > 0f ? Transform.InverseTransformDirection(towardsCamera).normalized * 0.9f : Vector3.zero;
                var towards = local + bias;
                skin = towards.sqrMagnitude < 1e-4f ? Vector3.up : towards.normalized;
            }
            _hitAmount = Mathf.Max(_hitAmount * Mathf.Clamp01(1f - (now - _hitAt) / 0.35f), 0.55f * strength);
            _hitAt = now;
            // A burst of rounds on one spot: one ripple, not four restarting each other.
            var oldest = 0;
            for (var i = 0; i < RippleSlots; i++)
            {
                var r = _ripples[i];
                if (now - r.w < 0.12f && (new Vector3(r.x, r.y, r.z) - skin).sqrMagnitude < 0.09f) return;
                if (r.w < _ripples[oldest].w) oldest = i;
            }
            _ripples[oldest] = new Vector4(skin.x, skin.y, skin.z, now);
        }

        /// <summary>Draws this frame's state; false once it is hidden (a shatter or a fade finished).</summary>
        public bool Tick(float now)
        {
            if (!_shown) return false;
            float power, collapse = 0f;
            if (_collapseAt >= 0f)
            {
                collapse = (now - _collapseAt) / CollapseSeconds;
                if (collapse >= 1f)
                {
                    Hide();
                    return false;
                }
                power = 1f;
            }
            else if (_loweredAt >= 0f)
            {
                power = 1f - (now - _loweredAt) / FadeSeconds;
                if (power <= 0f)
                {
                    Hide();
                    return false;
                }
            }
            else
            {
                var t = Mathf.Clamp01((now - _raisedAt) / _rise);
                // Up with a brief overshoot, as it charges.
                power = t * t * (3f - 2f * t) * (1f + 0.35f * Mathf.Sin(t * Mathf.PI));
            }
            _block.SetFloat(NowId, now);
            _block.SetFloat(PowerId, power);
            _block.SetFloat(CollapseId, _collapseAt >= 0f ? Mathf.Max(1e-4f, collapse) : 0f);
            _block.SetFloat(FlickerId, _collapseAt >= 0f ? 0f : Mathf.Clamp01(Flicker));
            _block.SetFloat(HitId, Mathf.Max(0f, _hitAmount * (1f - (now - _hitAt) / 0.35f)));
            for (var i = 0; i < RippleSlots; i++)
            {
                // Ripples live in the shield's own space, so they ride with a moving vehicle.
                var r = _ripples[i];
                _block.SetVector(RippleIds[i], now - r.w > RippleLife ? NoRipple : r);
            }
            _renderer.SetPropertyBlock(_block);
            return true;
        }

        /// <summary>Builds the meshes a shield of this shape and size will use now (not the first time one appears mid-battle).</summary>
        public static void Prepare(Shape shape, float radius)
        {
            var lite = LiteNow;
            MeshFor(Level(shape, radius, lite), shape == Shape.Dome);
            MaterialFor(lite);
        }

        // ------------------------------------------------------------------ material and meshes

        /// <summary>
        /// How finely the sphere is tiled: tiles about five metres across on a dome, a metre or
        /// two on a bubble. Low graphics draws no lattice, so a dome there takes one level fewer
        /// (its tiles only show as it shatters).
        /// </summary>
        private static int Level(Shape shape, float radius, bool lite)
        {
            if (shape == Shape.Bubble) return 2;
            var level = Mathf.Clamp(Mathf.RoundToInt(Mathf.Log(Mathf.Max(1f, radius * IcosahedronEdge / 5f), 2f)), 2, 4);
            return lite ? Mathf.Max(2, level - 1) : level;
        }

        private static Material MaterialFor(bool lite)
        {
            var material = lite ? _lite : _full;
            if (material != null) return material;
            var shader = Shader.Find("MachineBrigade/Shield");
            if (shader == null) throw new InvalidOperationException("Shader 'MachineBrigade/Shield' is missing; it must live in Resources/Shaders.");
            material = new Material(shader) { name = lite ? "Shield (Low)" : "Shield" };
            if (lite) material.EnableKeyword("_SHIELD_LITE");
            if (lite) _lite = material;
            else _full = material;
            return material;
        }

        private static Mesh MeshFor(int level, bool dome)
        {
            if (Meshes.TryGetValue((level, dome), out var mesh) && mesh != null) return mesh;
            mesh = BuildTiles(level, dome);
            Meshes[(level, dome)] = mesh;
            return mesh;
        }

        /// <summary>
        /// The tiles: the dual of a geodesic sphere (an icosahedron with a vertex at each pole,
        /// split <paramref name="level"/> times), so hexagons with twelve pentagons among them.
        /// Each tile is a fan of triangles from its centre to its corners (the middles of the
        /// sphere's triangles round it); every vertex carries the tile's centre, its random value
        /// and 0 (centre) or 1 (edge), which the shader turns into the lattice lines. A dome keeps
        /// the tiles that reach above the ground.
        /// </summary>
        private static Mesh BuildTiles(int level, bool dome)
        {
            var points = new List<Vector3>();
            var faces = new List<int>();
            var lat = Mathf.Atan(0.5f);
            points.Add(Vector3.up);
            for (var i = 0; i < 5; i++)
            {
                var a = i * 72f * Mathf.Deg2Rad;
                points.Add(new Vector3(Mathf.Cos(a) * Mathf.Cos(lat), Mathf.Sin(lat), Mathf.Sin(a) * Mathf.Cos(lat)));
            }
            for (var i = 0; i < 5; i++)
            {
                var a = (i * 72f + 36f) * Mathf.Deg2Rad;
                points.Add(new Vector3(Mathf.Cos(a) * Mathf.Cos(lat), -Mathf.Sin(lat), Mathf.Sin(a) * Mathf.Cos(lat)));
            }
            points.Add(Vector3.down);
            for (var i = 0; i < 5; i++)
            {
                int u0 = 1 + i, u1 = 1 + (i + 1) % 5, l0 = 6 + i, l1 = 6 + (i + 1) % 5;
                faces.AddRange(new[] { 0, u0, u1, u0, l0, u1, u1, l0, l1, 11, l0, l1 });
            }
            for (var s = 0; s < level; s++)
            {
                var split = new List<int>(faces.Count * 4);
                var middles = new Dictionary<long, int>();
                int Middle(int a, int b)
                {
                    var key = a < b ? ((long)a << 32) | (uint)b : ((long)b << 32) | (uint)a;
                    if (middles.TryGetValue(key, out var m)) return m;
                    points.Add(((points[a] + points[b]) * 0.5f).normalized);
                    middles[key] = points.Count - 1;
                    return points.Count - 1;
                }
                for (var f = 0; f < faces.Count; f += 3)
                {
                    int a = faces[f], b = faces[f + 1], c = faces[f + 2];
                    int ab = Middle(a, b), bc = Middle(b, c), ca = Middle(c, a);
                    split.AddRange(new[] { a, ab, ca, b, bc, ab, c, ca, bc, ab, bc, ca });
                }
                faces = split;
            }

            var corners = new Vector3[faces.Count / 3];
            var around = new List<int>[points.Count];
            for (var f = 0; f < corners.Length; f++)
            {
                corners[f] = (points[faces[f * 3]] + points[faces[f * 3 + 1]] + points[faces[f * 3 + 2]]).normalized;
                for (var k = 0; k < 3; k++) (around[faces[f * 3 + k]] ??= new List<int>(6)).Add(f);
            }

            var vertices = new List<Vector3>();
            var normals = new List<Vector3>();
            var tiles = new List<Vector4>();
            var centres = new List<Vector3>();
            var triangles = new List<int>();
            var random = new System.Random(20260929 + level);
            var order = new List<(float angle, int face)>(6);
            for (var p = 0; p < points.Count; p++)
            {
                var centre = points[p];
                var seed = (float)random.NextDouble();
                // Tiles wholly underground are left out of a dome (its cut is at the ground, in the shader).
                if (dome && centre.y < -0.2f) continue;
                var t1 = Vector3.Cross(centre, Mathf.Abs(centre.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
                var t2 = Vector3.Cross(centre, t1);
                order.Clear();
                foreach (var f in around[p])
                {
                    var d = corners[f] - centre;
                    order.Add((Mathf.Atan2(Vector3.Dot(d, t2), Vector3.Dot(d, t1)), f));
                }
                order.Sort((x, y) => x.angle.CompareTo(y.angle));
                var first = vertices.Count;
                vertices.Add(centre);
                normals.Add(centre);
                tiles.Add(new Vector4(0f, seed, 0f, 0f));
                centres.Add(centre);
                foreach (var (_, f) in order)
                {
                    vertices.Add(corners[f]);
                    normals.Add(corners[f]);
                    tiles.Add(new Vector4(1f, seed, 0f, 0f));
                    centres.Add(centre);
                }
                var n = order.Count;
                // Outward-facing (clockwise seen from outside, Unity's front face).
                var outward = Vector3.Dot(Vector3.Cross(corners[order[0].face] - centre, corners[order[1 % n].face] - centre), centre) > 0f;
                for (var k = 0; k < n; k++)
                {
                    var b = first + 1 + k;
                    var c = first + 1 + (k + 1) % n;
                    triangles.Add(first);
                    triangles.Add(outward ? b : c);
                    triangles.Add(outward ? c : b);
                }
            }

            var mesh = new Mesh { name = dome ? $"Shield Dome {level}" : $"Shield Bubble {level}" };
            if (vertices.Count > 65000) mesh.indexFormat = IndexFormat.UInt32;
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetUVs(0, tiles);
            mesh.SetUVs(1, centres);
            mesh.SetTriangles(triangles, 0);
            // Room for the shatter, whose tiles fly out a little past the skin.
            mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 2.6f);
            mesh.UploadMeshData(true);
            return mesh;
        }
    }
}

using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Reinforcements come by air instead of popping up at the drop zone: a transport flies over,
    /// the vehicle drops out of its belly and comes down under a parachute onto the exact spot
    /// where it lands in the battle, as the simulation hands it over. The chute then collapses
    /// beside it and a puff of dust goes up. Purely a picture: the delivery itself (its time and
    /// landing point) is the simulation's. Aircraft fly in from the map's edge on their own.
    /// </summary>
    internal sealed class AirDrops
    {
        private sealed class Drop
        {
            public GameObject Vehicle;
            public Transform Chute;
            public Vector3 Landing;
            public float Heading, Scale, Release, Land, Collapsed;
            public bool Down;
        }

        /// <summary>
        /// A transport's flight: in from the nearest map edge to over the drop (<see cref="Over"/>, at
        /// <see cref="OverAt"/>), a climbing U-turn of <see cref="TurnRadius"/>, and out by the same edge.
        /// </summary>
        private sealed class Plane
        {
            public GameObject Root;
            public Vector3 Entry, Over, Inward, Side;
            public float Start, OverAt, TurnEnd, ExitEnd, ApproachSpeed, ExitLength;
            public int Team;
        }

        /// <summary>The transport's height and speed over the drop.</summary>
        private const float PlaneAltitude = 44f;
        private const float PlaneSpeed = 70f;

        /// <summary>How far past the map's edge a transport appears and is removed (out of the battle's view).</summary>
        private const float EdgeMargin = 45f;

        /// <summary>The radius of the transport's turn home after the drop.</summary>
        private const float TurnRadius = 32f;

        /// <summary>The fastest a transport may come in, when the delivery leaves it little time to reach the drop.</summary>
        private const float MaxApproachSpeed = 160f;

        /// <summary>The vehicle leaves the transport this long before it lands (the rest of the delivery the plane is on its way).</summary>
        private const float Descent = 2.3f;

        /// <summary>
        /// The airlifter: the gunship's airframe without its guns (play-test 5, DECISIONS 20V: a transport with a
        /// gunship's battery out of its side read as the gunship), drawn at the gunship's scale.
        /// </summary>
        internal const string TransportModel = "transport_plane", TransportScale = "sky_gunship";

        private readonly Catalog _catalog;
        private readonly ModelLibrary _models;
        private readonly Emitters _emitters;
        private readonly Transform _root;
        private readonly Mesh _canopy;
        private readonly Mesh _cord;
        private readonly Material _cloth;
        private readonly List<Drop> _drops = new();
        private readonly List<Plane> _planes = new();
        private readonly bool _hasTransport;

        /// <summary>Half the map's side (the map is square, centred on the origin): where transports come in and leave.</summary>
        public float HalfSize
        {
            get => HalfX;
            set
            {
                HalfX = HalfZ = value;
                Centre = Vector3.zero;
            }
        }

        /// <summary>The map's middle and half extents (a long battlefield's, prompt 17).</summary>
        public Vector3 Centre { get; set; }

        public float HalfX { get; set; } = 150f;
        public float HalfZ { get; set; } = 150f;

        public AirDrops(Catalog catalog, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials, Emitters emitters, Transform parent)
        {
            _catalog = catalog;
            _models = models;
            _emitters = emitters;
            _root = new GameObject("Air Drops").transform;
            _root.SetParent(parent, false);
            _canopy = Dome(16, 5);
            _cord = meshes.Box;
            _cloth = materials.ForModel("Canvas", -1);
            _hasTransport = models.Has(TransportModel);
        }

        /// <summary>A bought vehicle is on its way: fly it in.</summary>
        public void Queue(SimEvent e, float now)
        {
            // A fortress's reinforcements coming in by its rail line or runway get off the train or aircraft (FortressView), no parachute.
            if (e.ByLine || e.DefId == null || !_catalog.Vehicles.TryGetValue(e.DefId, out var def) || def.Flying) return;
            var landing = new Vector3(e.Position.X, 0f, e.Position.Y);
            var inward = new Vector3(e.Target.X, 0f, e.Target.Y);
            if (inward.sqrMagnitude < 0.01f) inward = Vector3.forward;
            inward.Normalize();
            var land = now + e.Value;
            var release = land - Mathf.Min(Descent, e.Value * 0.8f);

            // One transport serves every drop of its side released within a second of each other.
            var flight = FlightFor(e.Team, landing, release, now);

            var model = _models.Spawn(Match.BranchArt.Model(def, _models), e.Team, _root, castShadows: false);
            // Drawn as it will be on the ground: its model fitted to its modelSize (prompt 25 B1), else the data's scale.
            var scale = MachineBrigade.Game.Views.VehicleView.DrawScaleOf(def, model.Root);
            var drop = new Drop
            {
                Vehicle = model.Root, Landing = landing, Heading = Mathf.Atan2(inward.x, inward.z) * Mathf.Rad2Deg, Scale = scale,
                Release = release, Land = land,
            };
            model.Root.transform.localScale = Vector3.one * scale;
            model.Root.SetActive(false);
            drop.Chute = BuildChute(model.Root.transform, def);
            _drops.Add(drop);
        }

        private Plane FlightFor(int team, Vector3 landing, float release, float now)
        {
            if (!_hasTransport) return null;
            foreach (var p in _planes)
                if (p.Team == team && Mathf.Abs(p.OverAt - release) < 1f) return p;
            var plane = Route(HalfX, HalfZ, landing - Centre, release, now);
            plane.Entry += Centre;
            plane.Over += Centre;
            plane.Team = team;
            plane.Root = _models.Spawn(TransportModel, team, _root, castShadows: false).Root;
            if (_catalog.Vehicles.TryGetValue(TransportScale, out var transport)) plane.Root.transform.localScale = Vector3.one * MachineBrigade.Game.Views.VehicleView.DrawScaleOf(transport, plane.Root);
            plane.Root.transform.SetPositionAndRotation(plane.Entry, Quaternion.LookRotation(plane.Inward));
            _planes.Add(plane);
            return plane;
        }

        /// <summary>
        /// The transport's route for a drop at <paramref name="landing"/> released at <paramref name="release"/>:
        /// the shortest way over the map, in from the edge nearest the drop and square to it, over the drop,
        /// a climbing U-turn and out by the same edge.
        /// </summary>
        private static Plane Route(float halfSize, Vector3 landing, float release, float now) => Route(halfSize, halfSize, landing, release, now);

        /// <summary>The run in to <paramref name="landing"/> (relative to the map's middle) over the nearest edge of a halfX by halfZ map.</summary>
        private static Plane Route(float halfX, float halfZ, Vector3 landing, float release, float now)
        {
            var toEdgeX = halfX - Mathf.Abs(landing.x);
            var toEdgeZ = halfZ - Mathf.Abs(landing.z);
            var inward = toEdgeX < toEdgeZ ? new Vector3(landing.x >= 0f ? -1f : 1f, 0f, 0f) : new Vector3(0f, 0f, landing.z >= 0f ? -1f : 1f);
            var outside = Mathf.Max(0f, Mathf.Min(toEdgeX, toEdgeZ)) + EdgeMargin;
            var over = landing + Vector3.up * PlaneAltitude;
            // It turns home towards the middle of the edge, so it does not run along it.
            var side = Vector3.Cross(Vector3.up, inward);
            if (Vector3.Dot(side, -new Vector3(landing.x, 0f, landing.z)) < 0f) side = -side;
            // It must be over the drop when the vehicle leaves; when the delivery is short it comes in faster.
            var speed = Mathf.Clamp(outside / Mathf.Max(0.3f, release - now), PlaneSpeed, MaxApproachSpeed);
            var plane = new Plane
            {
                Entry = over - inward * outside, Over = over, Inward = inward, Side = side, ApproachSpeed = speed, OverAt = release,
                Start = release - outside / speed, ExitLength = outside,
            };
            plane.TurnEnd = release + Mathf.PI * TurnRadius / PlaneSpeed;
            plane.ExitEnd = plane.TurnEnd + outside / PlaneSpeed;
            return plane;
        }

        /// <summary>For tests: the transport's positions from <paramref name="now"/> to its removal, every <paramref name="step"/> seconds.</summary>
        internal static List<Vector3> SampleRoute(float halfSize, Vector3 landing, float release, float now, float step)
        {
            var plane = Route(halfSize, landing, release, now);
            var points = new List<Vector3>();
            for (var t = Mathf.Max(now, plane.Start); t <= plane.ExitEnd; t += step) points.Add(Pose(plane, t).at);
            points.Add(Pose(plane, plane.ExitEnd).at);
            return points;
        }

        /// <summary>Where the transport is at <paramref name="now"/>, which way it flies and how far it banks.</summary>
        private static (Vector3 at, Vector3 heading, float bank) Pose(Plane p, float now)
        {
            if (now <= p.OverAt)
            {
                // The run in, level, over the drop at OverAt.
                var k = Mathf.Clamp01(1f - (p.OverAt - now) * p.ApproachSpeed / Mathf.Max(0.01f, (p.Over - p.Entry).magnitude));
                return (Vector3.Lerp(p.Entry, p.Over, k), p.Inward, 0f);
            }
            if (now <= p.TurnEnd)
            {
                // A half circle towards Side, climbing, banked into the turn.
                var theta = Mathf.PI * (now - p.OverAt) / Mathf.Max(0.01f, p.TurnEnd - p.OverAt);
                var centre = p.Over + p.Side * TurnRadius;
                var at = centre - p.Side * (TurnRadius * Mathf.Cos(theta)) + p.Inward * (TurnRadius * Mathf.Sin(theta));
                var heading = p.Side * Mathf.Sin(theta) + p.Inward * Mathf.Cos(theta);
                var bank = 35f * Mathf.Sin(Mathf.Min(1f, theta / (Mathf.PI * 0.2f)) * Mathf.PI * 0.5f) * Mathf.Min(1f, (Mathf.PI - theta) / (Mathf.PI * 0.2f));
                return (at + Vector3.up * (14f * theta / Mathf.PI), heading, bank);
            }
            // Home the way it came, still climbing, until it is past the edge.
            var s = Mathf.Clamp01((now - p.TurnEnd) / Mathf.Max(0.01f, p.ExitEnd - p.TurnEnd));
            var start = p.Over + p.Side * (2f * TurnRadius) + Vector3.up * 14f;
            return (start - p.Inward * (p.ExitLength * s) + Vector3.up * (10f * s), -p.Inward, 0f);
        }

        public void Tick(float now)
        {
            for (var i = _planes.Count - 1; i >= 0; i--)
            {
                var p = _planes[i];
                if (now >= p.ExitEnd)
                {
                    Object.Destroy(p.Root);
                    _planes.RemoveAt(i);
                    continue;
                }
                var (at, heading, bank) = Pose(p, now);
                // Banked into the turn: a right turn (Side to the right of the run in) rolls right.
                var rightTurn = Vector3.Dot(Vector3.Cross(p.Inward, p.Side), Vector3.up) > 0f;
                var roll = rightTurn ? -bank : bank;
                p.Root.transform.SetPositionAndRotation(at, Quaternion.LookRotation(heading) * Quaternion.Euler(0f, 0f, roll));
            }

            for (var i = _drops.Count - 1; i >= 0; i--)
            {
                var d = _drops[i];
                if (now < d.Release) continue;
                var t = d.Vehicle.transform;
                if (!d.Down)
                {
                    if (!d.Vehicle.activeSelf) d.Vehicle.SetActive(true);
                    var s = Mathf.Clamp01((now - d.Release) / Mathf.Max(0.1f, d.Land - d.Release));
                    // Falls out of the plane, the chute opens and brakes it: fast at first, soft at the end.
                    var height = (PlaneAltitude - 4f) * Mathf.Pow(1f - s, 1.7f);
                    var sway = Mathf.Sin(now * 2.1f + i) * 5f * (1f - s);
                    t.SetPositionAndRotation(d.Landing + Vector3.up * height, Quaternion.Euler(sway, d.Heading, sway * 0.6f));
                    // The canopy blossoms open in the first moments.
                    var open = Mathf.Clamp01((now - d.Release) / 0.45f);
                    d.Chute.localScale = new Vector3(open, Mathf.Lerp(0.3f, 1f, open), open);
                    if (s >= 1f)
                    {
                        d.Down = true;
                        d.Collapsed = now;
                        t.SetPositionAndRotation(d.Landing, Quaternion.Euler(0f, d.Heading, 0f));
                        _emitters.Dust(d.Landing, 1.4f + d.Scale);
                        // The real vehicle takes over from here; the chute stays a moment.
                        d.Chute.SetParent(_root, true);
                        foreach (Transform child in t) child.gameObject.SetActive(false);
                    }
                    continue;
                }
                // Landed: the chute sags down and drifts off to one side, then is gone.
                var c = Mathf.Clamp01((now - d.Collapsed) / 1.2f);
                d.Chute.localScale = new Vector3(1f + c * 0.4f, Mathf.Lerp(1f, 0.05f, c), 1f + c * 0.4f);
                d.Chute.position = new Vector3(d.Landing.x, Mathf.Lerp(d.Chute.position.y, 0.2f, c), d.Landing.z) + new Vector3(c * 2.5f, 0f, c * 1.5f);
                if (c < 1f) continue;
                Object.Destroy(d.Chute.gameObject);
                Object.Destroy(d.Vehicle);
                _drops.RemoveAt(i);
            }
        }

        /// <summary>A canopy over the vehicle on four cords, sized to it.</summary>
        private Transform BuildChute(Transform vehicle, VehicleDef def)
        {
            var chute = new GameObject("Parachute").transform;
            chute.SetParent(vehicle, false);
            // About 1.3 vehicle lengths across: big enough to read as a cargo chute, not a tent over the battle.
            var size = Mathf.Max(def.Length, def.Width) * 0.65f + 0.8f;
            // Play-test 6: the canopy rides over the model's own top and the cords meet it there (a field tower is
            // taller than the 5 m the canopy hung at, so the canopy sat through the middle of it).
            var modelTop = ModelTop(vehicle);
            var canopy = new GameObject("Canopy", typeof(MeshFilter), typeof(MeshRenderer));
            canopy.transform.SetParent(chute, false);
            canopy.transform.localPosition = new Vector3(0f, Mathf.Max(5f, modelTop + 2f) + size * 0.4f, 0f);
            canopy.transform.localScale = new Vector3(size, size * 0.5f, size);
            canopy.GetComponent<MeshFilter>().sharedMesh = _canopy;
            var renderer = canopy.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = _cloth;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            for (var k = 0; k < 4; k++)
            {
                var corner = new Vector3(k % 2 == 0 ? -1f : 1f, 0f, k < 2 ? -1f : 1f);
                var bottom = new Vector3(corner.x * def.Width * 0.35f, Mathf.Max(1.6f, modelTop - 0.2f), corner.z * def.Length * 0.35f);
                var top = canopy.transform.localPosition + new Vector3(corner.x * size * 0.42f, 0f, corner.z * size * 0.42f);
                var cord = new GameObject("Cord", typeof(MeshFilter), typeof(MeshRenderer));
                cord.transform.SetParent(chute, false);
                cord.transform.localPosition = (top + bottom) * 0.5f;
                cord.transform.localRotation = Quaternion.FromToRotation(Vector3.up, top - bottom);
                cord.transform.localScale = new Vector3(0.06f, (top - bottom).magnitude, 0.06f);
                cord.GetComponent<MeshFilter>().sharedMesh = _cord;
                var cordRenderer = cord.GetComponent<MeshRenderer>();
                cordRenderer.sharedMaterial = _cloth;
                cordRenderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            }
            return chute;
        }

        /// <summary>The highest point of a model's meshes in its root's own (unscaled) space; 0 when it has none.</summary>
        internal static float ModelTop(Transform root)
        {
            var top = 0f;
            var toRoot = root.worldToLocalMatrix;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                var b = filter.sharedMesh.bounds;
                var m = toRoot * filter.transform.localToWorldMatrix;
                for (var c = 0; c < 8; c++)
                {
                    var corner = b.center + Vector3.Scale(b.extents, new Vector3((c & 1) == 0 ? -1f : 1f, (c & 2) == 0 ? -1f : 1f, (c & 4) == 0 ? -1f : 1f));
                    top = Mathf.Max(top, m.MultiplyPoint3x4(corner).y);
                }
            }
            return top;
        }

        /// <summary>A unit dome (radius 1, height 1) open at the bottom, its outside facing out (seen from above).</summary>
        private static Mesh Dome(int segments, int rings)
        {
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            for (var r = 0; r <= rings; r++)
            {
                var polar = r / (float)rings * Mathf.PI * 0.5f;
                for (var s = 0; s <= segments; s++)
                {
                    var azimuth = s / (float)segments * Mathf.PI * 2f;
                    // Scalloped rim, like the panels of a real canopy.
                    var scallop = r == rings ? 0.94f + 0.06f * Mathf.Cos(azimuth * segments * 0.5f) : 1f;
                    vertices.Add(new Vector3(Mathf.Sin(polar) * Mathf.Cos(azimuth) * scallop, Mathf.Cos(polar), Mathf.Sin(polar) * Mathf.Sin(azimuth) * scallop));
                }
            }
            for (var r = 0; r < rings; r++)
                for (var s = 0; s < segments; s++)
                {
                    var a = r * (segments + 1) + s;
                    var b = a + segments + 1;
                    triangles.AddRange(new[] { a, a + 1, b, a + 1, b + 1, b });
                }
            var mesh = new Mesh { name = "Canopy" };
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}

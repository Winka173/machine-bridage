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

        private sealed class Plane
        {
            public GameObject Root;
            public Vector3 From, To;
            public float Start, End;
            public int Team;
        }

        /// <summary>The transport's height and speed over the drop.</summary>
        private const float PlaneAltitude = 44f;
        private const float PlaneSpeed = 70f;

        /// <summary>The vehicle leaves the transport this long before it lands (the rest of the delivery the plane is on its way).</summary>
        private const float Descent = 2.3f;

        private const string TransportModel = "sky_gunship";

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
            var flight = FlightFor(e.Team, landing, inward, release);

            var model = _models.Spawn(def.Model, e.Team, _root, castShadows: false);
            var drop = new Drop
            {
                Vehicle = model.Root, Landing = landing, Heading = Mathf.Atan2(inward.x, inward.z) * Mathf.Rad2Deg, Scale = def.Scale,
                Release = release, Land = land,
            };
            model.Root.transform.localScale = Vector3.one * def.Scale;
            model.Root.SetActive(false);
            drop.Chute = BuildChute(model.Root.transform, def);
            _drops.Add(drop);
            if (flight != null) flight.End = Mathf.Max(flight.End, release + 2.5f);
        }

        private Plane FlightFor(int team, Vector3 landing, Vector3 inward, float release)
        {
            if (!_hasTransport) return null;
            foreach (var p in _planes)
                if (p.Team == team && Mathf.Abs(Overhead(p) - release) < 1f) return p;
            // It flies in along the line into the battlefield and passes over the landing point as the vehicle drops.
            var over = landing + Vector3.up * PlaneAltitude;
            var from = over - inward * PlaneSpeed * 1.6f;
            var to = over + inward * PlaneSpeed * 2.2f;
            var plane = new Plane { Root = _models.Spawn(TransportModel, team, _root, castShadows: false).Root, From = from, To = to, Team = team };
            if (_catalog.Vehicles.TryGetValue(TransportModel, out var transport)) plane.Root.transform.localScale = Vector3.one * transport.Scale;
            plane.Start = release - 1.6f;
            plane.End = release + 2.2f;
            plane.Root.transform.SetPositionAndRotation(from, Quaternion.LookRotation(inward));
            _planes.Add(plane);
            return plane;
        }

        private static float Overhead(Plane p) => p.Start + 1.6f;

        public void Tick(float now)
        {
            for (var i = _planes.Count - 1; i >= 0; i--)
            {
                var p = _planes[i];
                var total = (p.To - p.From).magnitude / PlaneSpeed;
                var k = (now - p.Start) / total;
                if (k >= 1f && now > p.End)
                {
                    Object.Destroy(p.Root);
                    _planes.RemoveAt(i);
                    continue;
                }
                // Climbing away gently once past.
                var at = Vector3.LerpUnclamped(p.From, p.To, k) + Vector3.up * Mathf.Max(0f, k - 0.45f) * 14f;
                p.Root.transform.position = at;
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
            var canopy = new GameObject("Canopy", typeof(MeshFilter), typeof(MeshRenderer));
            canopy.transform.SetParent(chute, false);
            canopy.transform.localPosition = new Vector3(0f, 5f + size * 0.4f, 0f);
            canopy.transform.localScale = new Vector3(size, size * 0.5f, size);
            canopy.GetComponent<MeshFilter>().sharedMesh = _canopy;
            var renderer = canopy.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = _cloth;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            for (var k = 0; k < 4; k++)
            {
                var corner = new Vector3(k % 2 == 0 ? -1f : 1f, 0f, k < 2 ? -1f : 1f);
                var bottom = new Vector3(corner.x * def.Width * 0.35f, 1.6f, corner.z * def.Length * 0.35f);
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

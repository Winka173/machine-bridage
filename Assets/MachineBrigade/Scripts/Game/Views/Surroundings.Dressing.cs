using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;
using NVector2 = System.Numerics.Vector2;
using Random = System.Random;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 33 L6: the biome's DECORATION layer (map_dressing.json): its own objects scattered by zone at the
    /// biome's target density (instances per hectare: a light scatter of small clutter on the play area, dense in the
    /// edge band, lighter in the ring, HLOD stand-ins in the ring's far half, buoys at sea and islets on the horizon),
    /// and visual-only relief past the edge (low hills, berms, ditches, dry stream beds). Everything here is drawn
    /// with GPU instancing from the map's fixed seed: no GameObject, no collider, nothing the simulation, its routes or
    /// its vision ever see. The GAMEPLAY layer (cover, blockers) is only ever the map files' props, through the map
    /// audit; plain wrecks stay visual (none are added here).
    /// </summary>
    public sealed partial class Surroundings
    {
        private enum ReliefKind
        {
            Hill,
            Berm,
            Ditch,
            DryBed,
        }

        /// <summary>One relief feature: a dome round <see cref="A"/>, or a ridge / channel along A-B.</summary>
        private readonly struct Relief
        {
            public Relief(ReliefKind kind, Vector2 a, Vector2 b, float radius, float height)
            {
                Kind = kind;
                A = a;
                B = b;
                Radius = radius;
                Height = height;
            }

            public ReliefKind Kind { get; }
            public Vector2 A { get; }
            public Vector2 B { get; }

            /// <summary>Dome radius, ridge half-width, or channel half-width.</summary>
            public float Radius { get; }

            /// <summary>Dome or ridge height; for a channel, its banks' height.</summary>
            public float Height { get; }
        }

        private readonly List<Relief> _relief = new();

        /// <summary>Width of a channel's raised bank, beside its painted bed.</summary>
        private const float BankWidth = 3.5f;

        /// <summary>Play-area dressing keeps this far from any prop, a rally, a capture circle and a road's edge.</summary>
        private const float PropClearance = 2.5f, RallyClearance = 22f, PointClearance = 4f, RoadClearance = 1.5f;

        private readonly Dictionary<string, bool> _hasModel = new();

        /// <summary>Instances in one hectare (m²).</summary>
        private const float Hectare = 10000f;

        private List<string> Usable(ModelLibrary models, string[] set)
        {
            var list = new List<string>();
            if (set == null) return list;
            foreach (var id in set)
            {
                if (string.IsNullOrEmpty(id)) continue;
                if (!_hasModel.TryGetValue(id, out var has)) _hasModel[id] = has = models.Has(id);
                if (has) list.Add(id);
            }
            return list;
        }

        private float DressDensity => _density * (_dress != null && _dress.density > 0f ? _dress.density : 1f);

        // ------------------------------------------------------------------------------------------ relief

        /// <summary>
        /// Lays the map's relief (counts from its entry, else its biome's), all past the edge: hills in the ring, berms
        /// along the edge in the band, ditches across band and ring, dry beds running out from the band. Off the sea, the
        /// river and the city.
        /// </summary>
        private void BuildRelief()
        {
            _relief.Clear();
            if (_biome == null && _dress == null) return;
            int Count(int own, int biome) => _dress != null ? own : biome;
            var rng = new Random(_seed + 101);
            var band = _zones.EdgeBand;
            var ring = Mathf.Min(_zones.RingX, _zones.RingZ);
            var peaks = Mathf.Clamp(_theme.Peaks, 0.6f, 1.4f);
            var hills = Count(_dress?.hills ?? 0, _biome?.hills ?? 0);
            var berms = Count(_dress?.berms ?? 0, _biome?.berms ?? 0);
            var ditches = Count(_dress?.ditches ?? 0, _biome?.ditches ?? 0);
            var beds = Count(_dress?.dryBeds ?? 0, _biome?.dryBeds ?? 0);
            for (int i = 0, tries = 0; i < hills && tries < hills * 20; tries++)
            {
                if (!ReliefPoint(rng, band + 8f, band + ring * 0.75f, out var p)) continue;
                var radius = 12f + (float)rng.NextDouble() * 14f;
                _relief.Add(new Relief(ReliefKind.Hill, p, p, radius, (1.8f + (float)rng.NextDouble() * 2.7f) * peaks));
                i++;
            }
            for (int i = 0, tries = 0; i < berms && tries < berms * 20; tries++)
            {
                if (!ReliefPoint(rng, 3f, Mathf.Max(4f, band - 1.5f), out var p)) continue;
                var along = EdgeTangent(p);
                var half = 12f + (float)rng.NextDouble() * 13f;
                _relief.Add(new Relief(ReliefKind.Berm, p - along * half, p + along * half, 3f + (float)rng.NextDouble(),
                    0.8f + (float)rng.NextDouble() * 0.7f));
                i++;
            }
            for (int i = 0, tries = 0; i < ditches && tries < ditches * 20; tries++)
            {
                if (!ReliefPoint(rng, band * 0.5f, band + 30f, out var p)) continue;
                var along = Rotate(EdgeTangent(p), ((float)rng.NextDouble() - 0.5f) * 50f);
                var half = 10f + (float)rng.NextDouble() * 10f;
                _relief.Add(new Relief(ReliefKind.Ditch, p - along * half, p + along * half, 1.2f + (float)rng.NextDouble() * 0.6f,
                    0.5f + (float)rng.NextDouble() * 0.3f));
                i++;
            }
            for (int i = 0, tries = 0; i < beds && tries < beds * 20; tries++)
            {
                if (!ReliefPoint(rng, band, band + 10f, out var p)) continue;
                // A meander of three reaches running out from the band towards the horizon.
                var heading = EdgeNormal(p);
                var width = 3f + (float)rng.NextDouble() * 2f;
                var bank = 0.4f + (float)rng.NextDouble() * 0.3f;
                for (var reach = 0; reach < 3; reach++)
                {
                    heading = Rotate(heading, ((float)rng.NextDouble() - 0.5f) * 60f);
                    var next = p + heading * (25f + (float)rng.NextDouble() * 20f);
                    _relief.Add(new Relief(ReliefKind.DryBed, p, next, width, bank));
                    p = next;
                }
                i++;
            }
        }

        private bool ReliefPoint(Random rng, float from, float to, out Vector2 p)
        {
            p = DressPoint(rng, to);
            var beyond = Beyond(p);
            if (beyond < from || beyond >= to) return false;
            return !InSea(p, 12f) && !NearRiver(p, 10f) && !(InCity(p) && beyond >= 16f);
        }

        /// <summary>Along the map edge nearest <paramref name="p"/> (a z side runs along x).</summary>
        private Vector2 EdgeTangent(Vector2 p) =>
            Mathf.Abs(p.x - _centre.x) - _halfX > Mathf.Abs(p.y - _centre.y) - _halfZ ? Vector2.up : Vector2.right;

        /// <summary>Out of the map, across the edge nearest <paramref name="p"/>.</summary>
        private Vector2 EdgeNormal(Vector2 p) =>
            Mathf.Abs(p.x - _centre.x) - _halfX > Mathf.Abs(p.y - _centre.y) - _halfZ
                ? new Vector2(Mathf.Sign(p.x - _centre.x), 0f)
                : new Vector2(0f, Mathf.Sign(p.y - _centre.y));

        private static Vector2 Rotate(Vector2 v, float degrees)
        {
            var r = degrees * Mathf.Deg2Rad;
            float c = Mathf.Cos(r), s = Mathf.Sin(r);
            return new Vector2(v.x * c - v.y * s, v.x * s + v.y * c);
        }

        private static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var t = ab.sqrMagnitude > 1e-6f ? Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude) : 0f;
            return Vector2.Distance(p, a + ab * t);
        }

        /// <summary>
        /// The relief's height at a ground point: 0 on the map and within 1.5 m of its edge (it rises over the next few
        /// metres), on the sea and by the river. Channels stay at ground level with raised banks (their beds are painted).
        /// </summary>
        private float ReliefHeight(Vector2 p)
        {
            if (_relief.Count == 0) return 0f;
            var beyond = Beyond(p);
            if (beyond < 1.5f || InSea(p, 4f) || NearRiver(p, 2f)) return 0f;
            var fade = Edge(1.5f, 5f, beyond);
            var height = 0f;
            foreach (var r in _relief)
            {
                float h;
                switch (r.Kind)
                {
                    case ReliefKind.Hill:
                    {
                        var t = 1f - Vector2.Distance(p, r.A) / r.Radius;
                        h = t > 0f ? r.Height * t * t * (3f - 2f * t) : 0f;
                        break;
                    }
                    case ReliefKind.Berm:
                    {
                        var t = 1f - SegmentDistance(p, r.A, r.B) / r.Radius;
                        h = t > 0f ? r.Height * t * t * (3f - 2f * t) : 0f;
                        break;
                    }
                    default:
                    {
                        var d = SegmentDistance(p, r.A, r.B) - r.Radius;
                        var t = 1f - Mathf.Abs(d - BankWidth * 0.5f) / (BankWidth * 0.5f);
                        h = d > 0f && t > 0f ? r.Height * t * t * (3f - 2f * t) : 0f;
                        break;
                    }
                }
                height = Mathf.Max(height, h);
            }
            return height * fade;
        }

        /// <summary>The painted beds of the ditches (dark, damp earth) and dry beds (sand and gravel) on the outer ground.</summary>
        private Color PaintRelief(Vector2 p, Color colour, TerrainTheme palette)
        {
            if (_relief.Count == 0 || Beyond(p) < 1f) return colour;
            foreach (var r in _relief)
            {
                if (r.Kind is ReliefKind.Hill or ReliefKind.Berm) continue;
                var d = SegmentDistance(p, r.A, r.B);
                if (d > r.Radius + 1f) continue;
                var bed = r.Kind == ReliefKind.Ditch ? palette.Dirt * 0.72f : Color.Lerp(palette.Sand, palette.Stone, 0.35f);
                bed.a = 1f;
                colour = Color.Lerp(colour, bed, 1f - Edge(r.Radius - 0.8f, r.Radius + 1f, d));
            }
            return colour;
        }

        // ------------------------------------------------------------------------------------------ dressing

        /// <summary>A point in the rectangle grown <paramref name="reach"/> m past the edge (kept inside the ring's far edge).</summary>
        private Vector2 DressPoint(Random rng, float reach)
        {
            var x = _halfX + Mathf.Min(reach, _zones.EdgeBand + _zones.RingX);
            var z = _halfZ + Mathf.Min(reach, _zones.EdgeBand + _zones.RingZ);
            return _centre + new Vector2((float)(rng.NextDouble() * 2 - 1) * x, (float)(rng.NextDouble() * 2 - 1) * z);
        }

        /// <summary>The biome's decoration, zone by zone, at its target densities (see the class summary).</summary>
        private void ScatterDressing(ModelLibrary models, SimWorld world, List<Rect> fields)
        {
            if (_biome == null) return;
            var rng = new Random(_seed + 202);
            var band = _zones.EdgeBand;
            var hlod = _zones.HlodStart;
            var outer = band + Mathf.Max(_zones.RingX, _zones.RingZ);
            var density = DressDensity;
            DressZone(models, rng, Usable(models, _biome.bandSet), _biome.band * density, 0.6f, band, fields, 0.75f, 1.25f, true);
            DressZone(models, rng, Usable(models, _biome.ringSet), _biome.ring * density, band, hlod, fields, 0.8f, 1.4f, false);
            DressZone(models, rng, Usable(models, _biome.farSet), _biome.far * density, hlod, outer + 1f, fields, 0.9f, 1.5f, false);
            DressSea(models, rng, Usable(models, _biome.seaSet), Usable(models, _biome.horizonSet));
            DressPlay(models, world, rng, Usable(models, _biome.playSet), _biome.play * density);
        }

        private void DressZone(ModelLibrary models, Random rng, List<string> set, float perHectare, float from, float to,
            List<Rect> fields, float minScale, float maxScale, bool edge)
        {
            if (set.Count == 0 || perHectare <= 0f) return;
            var target = Mathf.RoundToInt(perHectare * (_zones.AreaWithin(to) - _zones.AreaWithin(from)) / Hectare);
            var placed = 0;
            for (var attempt = 0; attempt < target * 12 + 200 && placed < target; attempt++)
            {
                var p = DressPoint(rng, to);
                var beyond = Beyond(p);
                if (beyond < from || beyond >= to) continue;
                if (InSea(p, 1f) || NearRiver(p, 2f) || InField(p, fields)) continue;
                // The city's blocks fill the ring round an urban map; dressing keeps to the strip before them.
                if (InCity(p) && beyond >= 16f) continue;
                var height = Height(p);
                if (height > TreeLine) continue;
                var model = set[rng.Next(set.Count)];
                var scale = minScale + (float)rng.NextDouble() * (maxScale - minScale);
                // The band sits right by the fight: its pieces cast shadows like the tree line there (by cell, as the rest).
                Add(models, model, p, (float)rng.NextDouble() * 360f, scale, height - 0.05f, shadowless: !edge);
                placed++;
            }
            DressingPlaced += placed;
        }

        /// <summary>Buoys on the sea in the band and ring, islets on the horizon beyond the ring (harbour and coast maps).</summary>
        private void DressSea(ModelLibrary models, Random rng, List<string> buoys, List<string> islets)
        {
            // With edges data the sea side is dressed by DressSeaEdges (prompt 33 L2 view); its buoys stay on the sea.
            if (_theme.Water != ThemeWater.Sea && !(HasEdges && _edges.HasSea)) return;
            if (HasEdges)
            {
                DressEdgeBuoys(models, rng, buoys);
                return;
            }
            var reachX = Mathf.Min(Extent, _zones.OuterX);
            var count = Mathf.RoundToInt(6f * DressDensity * reachX / 300f);
            for (var i = 0; i < count && buoys.Count > 0; i++)
            {
                var p = new Vector2(_centre.x + (float)(rng.NextDouble() * 2 - 1) * reachX * 0.9f,
                    SeaShore + 12f + (float)rng.NextDouble() * Mathf.Max(10f, _centre.y + _zones.OuterZ - SeaShore - 20f));
                Add(models, buoys[rng.Next(buoys.Count)], p, (float)rng.NextDouble() * 360f, 0.9f + (float)rng.NextDouble() * 0.3f,
                    -0.15f, shadowless: true);
                DressingPlaced++;
            }
            for (var i = 0; i < 4 && islets.Count > 0; i++)
            {
                var p = new Vector2(_centre.x + (float)(rng.NextDouble() * 2 - 1) * Extent * 1.3f,
                    _centre.y + _zones.OuterZ + 40f + (float)rng.NextDouble() * Extent * 0.6f);
                Add(models, islets[rng.Next(islets.Count)], p, (float)rng.NextDouble() * 360f, 1.2f + (float)rng.NextDouble() * 1.6f,
                    -0.6f, shadowless: true);
                DressingPlaced++;
            }
        }

        /// <summary>
        /// Small clutter on the play area (all under a metre or two, never cover-sized): clear of every prop (gameplay or
        /// not), both rallies, the capture circles, the roads and the outline's bays. Decoration only: units drive
        /// through it, shots and sight lines ignore it.
        /// </summary>
        private void DressPlay(ModelLibrary models, SimWorld world, Random rng, List<string> set, float perHectare)
        {
            if (set.Count == 0 || perHectare <= 0f) return;
            var map = world.Map;
            var target = Mathf.RoundToInt(perHectare * map.Width * map.Length / Hectare);
            float halfX = _halfX - 4f, halfZ = _halfZ - 4f;
            var placed = 0;
            for (var attempt = 0; attempt < target * 15 + 100 && placed < target; attempt++)
            {
                var p = _centre + new Vector2((float)(rng.NextDouble() * 2 - 1) * halfX, (float)(rng.NextDouble() * 2 - 1) * halfZ);
                if (_field.HasOutline && _field.Distance(p) > -3f) continue;
                if (!PlayClear(world, p) || InLandmark(p, 1f)) continue;
                var model = set[rng.Next(set.Count)];
                Add(models, model, p, (float)rng.NextDouble() * 360f, 0.55f + (float)rng.NextDouble() * 0.35f, 0f, shadowless: true);
                placed++;
            }
            DressingPlaced += placed;
        }

        private static bool PlayClear(SimWorld world, Vector2 p)
        {
            var at = new NVector2(p.x, p.y);
            foreach (var prop in world.Props)
                if (prop.Contains(at, PropClearance)) return false;
            foreach (var team in world.Map.Teams)
                if (NVector2.Distance(team.Rally, at) < RallyClearance) return false;
            foreach (var point in world.Map.Points)
                if (NVector2.Distance(point.Position, at) < point.Radius + PointClearance) return false;
            // Nor on a rail's band (prompt 33 L2 view: the track is drawn along the whole line).
            foreach (var rail in world.Map.Rails)
            {
                var along = rail.Project(at, out _);
                if (NVector2.Distance(rail.At(along), at) < MachineBrigade.Sim.Navigation.RailSpline.BandHalf + 0.5f) return false;
            }
            foreach (var road in world.Map.Roads)
                for (var i = 0; i + 1 < road.Points.Count; i++)
                {
                    var a = new Vector2(road.Points[i].X, road.Points[i].Y);
                    var b = new Vector2(road.Points[i + 1].X, road.Points[i + 1].Y);
                    if (SegmentDistance(p, a, b) < road.Width * 0.5f + RoadClearance) return false;
                }
            return true;
        }

        /// <summary>Biome dressing instances placed (all zones), for the perf probe and the scenery log.</summary>
        public int DressingPlaced { get; private set; }
    }
}

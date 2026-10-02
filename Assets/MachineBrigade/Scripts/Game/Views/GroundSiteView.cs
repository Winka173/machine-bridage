using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 31 L3 / L5 (lead UI pass 2026-10-02, DECISIONS "UI polish after prompts 28-34"): a 3D look for the ground a
    /// mission's prebuilt site closes, driven by the state in force of each NavGrid site (<c>world.NavStates.Sites</c>): the
    /// water over a flooded ford or a dam's rising flood, the broken deck of a fallen bridge, a crane's lattice boom lying
    /// across the quay, the rubble that seals a mine adit, a lava cut with its dark crust, a gate shut across a lane, and a
    /// forest fire's strips (the strip burning in flames and smoke, the strips it has passed charred). The look of a site
    /// comes from its id (the data's site names: "shoal", "flood", "east_bridge", "crane", "adits", "lava", "fire",
    /// "mill_gate"); the walls' and level crossings' sites (prompt 32 / 33) and Daedalus's pod sites draw themselves and are
    /// left out. Each block is drawn at its own size (without the route clearance). Shared surface materials only (no
    /// MaterialPropertyBlock, nothing tinted). View only: it reads the sim and never writes to it.
    /// </summary>
    internal sealed class GroundSiteView
    {
        private enum Look
        {
            None,
            Water,
            Bridge,
            Crane,
            Rubble,
            Lava,
            Fire,
            Gate,
        }

        private sealed class SiteLook
        {
            public Look Look;
            public int Shown = -2;
            public GameObject Root;
            public readonly List<(Vector2 centre, Vector2 size)> Burning = new();
            public float FireDue, SmokeDue;
        }

        /// <summary>Flames a second on a burning strip, per 100 m² of it (capped), and smoke billows a second.</summary>
        private const float FireRate = 9f, FireCap = 60f, SmokeRate = 2.5f, SmokeCap = 14f;

        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly EffectsDirector _effects;
        private readonly Transform _root;
        private readonly Dictionary<string, SiteLook> _sites = new();

        public GroundSiteView(MeshLibrary meshes, MaterialLibrary materials, EffectsDirector effects, Transform parent)
        {
            _meshes = meshes;
            _materials = materials;
            _effects = effects;
            _root = new GameObject("Ground Sites").transform;
            _root.SetParent(parent, false);
        }

        /// <summary>The look a site's id asks for (none: it is not one of the closed-ground events' sites).</summary>
        private static Look LookOf(string id)
        {
            if (string.IsNullOrEmpty(id)) return Look.None;
            var s = id.ToLowerInvariant();
            if (s.StartsWith("wall.") || s.StartsWith("rail_") || s.StartsWith("pod_")) return Look.None;
            if (s.Contains("flood") || s.Contains("shoal") || s.Contains("ford") || s.Contains("water")) return Look.Water;
            if (s.Contains("bridge")) return Look.Bridge;
            if (s.Contains("crane") || s.Contains("boom")) return Look.Crane;
            if (s.Contains("adit") || s.Contains("mine") || s.Contains("tunnel") || s.Contains("cave") || s.Contains("rubble") || s.Contains("rockfall"))
                return Look.Rubble;
            if (s.Contains("lava")) return Look.Lava;
            if (s.Contains("fire")) return Look.Fire;
            if (s.Contains("gate")) return Look.Gate;
            return Look.None;
        }

        public void Render(SimWorld world, float time, float dt)
        {
            // Never world.NavStates: it would make the holder, which then steps and locks (the view must not change the sim).
            var sites = world.NavSitesIfAny;
            for (var i = 0; i < sites.Count; i++)
            {
                var site = sites[i];
                if (!_sites.TryGetValue(site.Id, out var look))
                {
                    look = new SiteLook { Look = LookOf(site.Id) };
                    _sites[site.Id] = look;
                }
                if (look.Look == Look.None) continue;
                if (look.Shown != site.Active)
                {
                    var first = look.Shown == -2;
                    Build(site, look, first);
                    look.Shown = site.Active;
                }
                if (look.Burning.Count > 0 && dt > 0f) Feed(look, dt);
            }
        }

        // ------------------------------------------------------------------ building a state's look

        private void Build(NavSite site, SiteLook look, bool first)
        {
            if (look.Root != null) Object.Destroy(look.Root);
            look.Root = null;
            look.Burning.Clear();
            var def = site.Def;
            var state = def.States[site.Active];
            var go = new GameObject("Site " + site.Id + " " + state.Name);
            go.transform.SetParent(_root, false);
            look.Root = go;
            var random = new System.Random(Hash(site.Id) ^ (site.Active * 7919));
            if (look.Look == Look.Fire)
            {
                // The strips the fire has passed are charred; the one in force burns.
                for (var k = 0; k < site.Active; k++)
                    foreach (var b in def.States[k].Blocks)
                        Slab(go.transform, b, "Charred", 0.03f, 0.06f);
                foreach (var b in state.Blocks)
                {
                    Slab(go.transform, b, "Charred", 0.035f, 0.07f);
                    look.Burning.Add((Centre(b), new Vector2(b.Width, b.Depth)));
                }
                return;
            }
            foreach (var b in state.Blocks)
            {
                switch (look.Look)
                {
                    case Look.Water:
                        Water(go.transform, b);
                        break;
                    case Look.Bridge:
                        Bridge(go.transform, b, random);
                        break;
                    case Look.Crane:
                        Crane(go.transform, b, random);
                        break;
                    case Look.Rubble:
                        Rubble(go.transform, b, random);
                        break;
                    case Look.Lava:
                        Lava(go.transform, b, random);
                        look.Burning.Add((Centre(b), new Vector2(b.Width, b.Depth) * 0.6f));
                        break;
                    case Look.Gate:
                        Gate(go.transform, b);
                        break;
                }
                // Ground that has just come in (not as the battle loads) throws up dust along it.
                if (!first && look.Look is Look.Bridge or Look.Crane or Look.Rubble or Look.Gate) Dust(b, random);
            }
        }

        private static Vector2 Centre(NavBlock b) => new(b.Center.X, b.Center.Y);

        /// <summary>The block's long axis (x or z) and its length and breadth.</summary>
        private static (bool alongX, float length, float breadth) Axis(NavBlock b) =>
            b.Width >= b.Depth ? (true, b.Width, b.Depth) : (false, b.Depth, b.Width);

        private static Vector3 Along(bool alongX, float a, float y, float across) => alongX ? new Vector3(a, y, across) : new Vector3(across, y, a);

        private static Vector3 Size(bool alongX, float length, float height, float breadth) =>
            alongX ? new Vector3(length, height, breadth) : new Vector3(breadth, height, length);

        private Transform Group(Transform parent, NavBlock b, string name)
        {
            var g = new GameObject(name).transform;
            g.SetParent(parent, false);
            g.localPosition = new Vector3(b.Center.X, 0f, b.Center.Y);
            return g;
        }

        private void Box(Transform parent, Material material, Vector3 position, Vector3 size, Quaternion rotation, bool shadows = true)
        {
            var piece = new GameObject("piece");
            piece.transform.SetParent(parent, false);
            piece.transform.localPosition = position;
            piece.transform.localRotation = rotation;
            piece.transform.localScale = size;
            piece.AddComponent<MeshFilter>().sharedMesh = _meshes.Box;
            var renderer = piece.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = shadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
        }

        private Material Surface(string name) => _materials.ForModel(name, 0);

        /// <summary>A thin slab over the whole block (charred ground, a water sheet).</summary>
        private void Slab(Transform parent, NavBlock b, string surface, float y, float thickness)
        {
            var g = Group(parent, b, "slab");
            Box(g, Surface(surface), new Vector3(0f, y, 0f), new Vector3(b.Width, thickness, b.Depth), Quaternion.identity, false);
        }

        /// <summary>A flooded ford or a dam's flood: a water sheet just over the ground, a darker band of silt at its edge.</summary>
        private void Water(Transform parent, NavBlock b)
        {
            var g = Group(parent, b, "water");
            Box(g, Surface("Dirt"), new Vector3(0f, 0.02f, 0f), new Vector3(b.Width + 1.2f, 0.04f, b.Depth + 1.2f), Quaternion.identity, false);
            Box(g, _materials.Water, new Vector3(0f, 0.09f, 0f), new Vector3(b.Width, 0.1f, b.Depth), Quaternion.identity, false);
        }

        /// <summary>A fallen bridge: two broken deck spans pitched down into the gap, rebar out of their ends, slabs in the middle.</summary>
        private void Bridge(Transform parent, NavBlock b, System.Random random)
        {
            var (alongX, length, breadth) = Axis(b);
            var g = Group(parent, b, "bridge");
            var concrete = Surface("Concrete");
            var asphalt = Surface("Asphalt");
            var rust = Surface("Rust");
            var span = length * 0.5f - 1.5f;
            for (var side = -1; side <= 1; side += 2)
            {
                // Each span hinges at its far end (still on its pier) and drops its broken end into the gap.
                var pitch = 9f + (float)random.NextDouble() * 5f;
                var centre = side * (length * 0.5f - span * 0.5f);
                var drop = Mathf.Sin(pitch * Mathf.Deg2Rad) * span * 0.5f;
                var tilt = alongX ? Quaternion.Euler(0f, 0f, side * pitch) : Quaternion.Euler(-side * pitch, 0f, 0f);
                var at = Along(alongX, centre, 0.5f - drop * 0.6f, 0f);
                Box(g, concrete, at, Size(alongX, span, 0.9f, breadth), tilt);
                Box(g, asphalt, at + tilt * Vector3.up * 0.48f, Size(alongX, span * 0.98f, 0.08f, breadth * 0.86f), tilt, false);
                // Rebar out of the broken end.
                var end = side * (length * 0.5f - span) + side * 0.2f;
                for (var r = 0; r < 4; r++)
                {
                    var across = (r - 1.5f) * breadth * 0.22f;
                    var bend = Quaternion.Euler((float)random.NextDouble() * 30f - 15f, (float)random.NextDouble() * 40f - 20f, (float)random.NextDouble() * 30f - 15f);
                    Box(g, rust, Along(alongX, end, 0.2f, across), Size(alongX, 1.6f, 0.08f, 0.08f), tilt * bend, false);
                }
            }
            // Slabs and chunks fallen into the middle.
            for (var i = 0; i < 6; i++)
            {
                var a = ((float)random.NextDouble() - 0.5f) * 3f;
                var across = ((float)random.NextDouble() - 0.5f) * breadth * 0.8f;
                var s = 0.8f + (float)random.NextDouble() * 1.6f;
                Box(g, concrete, Along(alongX, a, s * 0.2f, across), new Vector3(s, s * 0.5f, s * 0.8f),
                    Quaternion.Euler((float)random.NextDouble() * 40f - 20f, (float)random.NextDouble() * 360f, (float)random.NextDouble() * 40f - 20f));
            }
        }

        /// <summary>A crane's lattice boom lying across the block: four chords, braces every 2.5 m, the hook block at its tip.</summary>
        private void Crane(Transform parent, NavBlock b, System.Random random)
        {
            var (alongX, length, breadth) = Axis(b);
            var g = Group(parent, b, "crane boom");
            g.localRotation = Quaternion.Euler(0f, (float)random.NextDouble() * 4f - 2f, 0f);
            var yellow = Surface("CraneYellow");
            var steel = Surface("Steel");
            var section = Mathf.Clamp(breadth * 0.45f, 1f, 1.8f);
            var half = section * 0.5f;
            var roll = alongX ? Quaternion.Euler(4f, 0f, 0f) : Quaternion.Euler(0f, 0f, 4f);
            for (var c = 0; c < 4; c++)
            {
                var across = c % 2 == 0 ? -half : half;
                var y = c < 2 ? 0.2f : 0.2f + section;
                Box(g, yellow, roll * Along(alongX, 0f, y, across), Size(alongX, length, 0.22f, 0.22f), roll);
            }
            var braces = Mathf.Max(2, Mathf.FloorToInt(length / 2.5f));
            for (var i = 0; i <= braces; i++)
            {
                var a = -length * 0.5f + length * i / braces;
                for (var side = -1; side <= 1; side += 2)
                    Box(g, yellow, roll * Along(alongX, a, 0.2f + half, side * half), new Vector3(0.12f, section, 0.12f),
                        roll * (alongX ? Quaternion.Euler(0f, 0f, i % 2 == 0 ? 35f : -35f) : Quaternion.Euler(i % 2 == 0 ? 35f : -35f, 0f, 0f)), false);
                Box(g, yellow, roll * Along(alongX, a, 0.2f + section, 0f), Size(alongX, 0.12f, 0.12f, section), roll, false);
            }
            // The tip's sheave and hook block at one end, the boom's foot torn off its pin at the other.
            var tip = random.Next(2) == 0 ? -1f : 1f;
            Box(g, steel, Along(alongX, tip * (length * 0.5f + 0.4f), 0.9f, 0f), new Vector3(1.4f, 1.6f, 1.4f), Quaternion.Euler(0f, 20f, 8f));
            Box(g, Surface("Hazard"), Along(alongX, tip * (length * 0.5f - 1.2f), 0.6f, half + 0.6f), new Vector3(0.9f, 1.1f, 0.6f), Quaternion.Euler(0f, 35f, 0f));
            Box(g, steel, Along(alongX, -tip * (length * 0.5f), 0.5f, 0f), Size(alongX, 0.6f, 1f, section + 0.6f), Quaternion.Euler(0f, 0f, 12f));
        }

        /// <summary>A sealed adit: a heap of rock and broken timber over the block, biggest in the middle.</summary>
        private void Rubble(Transform parent, NavBlock b, System.Random random)
        {
            var (alongX, length, breadth) = Axis(b);
            var g = Group(parent, b, "rubble");
            var rock = Surface("Rock");
            var dark = Surface("SandstoneDark");
            var wood = Surface("Wood");
            var count = Mathf.Clamp(Mathf.RoundToInt(length * breadth / 4f), 8, 28);
            for (var i = 0; i < count; i++)
            {
                var a = ((float)random.NextDouble() - 0.5f) * length;
                var across = ((float)random.NextDouble() - 0.5f) * breadth;
                // Higher towards the middle of the heap.
                var centre = 1f - Mathf.Abs(a) / (length * 0.5f + 0.01f);
                var s = 0.8f + (float)random.NextDouble() * 1.4f + centre * 1.4f;
                Box(g, i % 3 == 0 ? dark : rock, Along(alongX, a, s * 0.3f + centre * 0.6f, across), new Vector3(s, s * 0.7f, s * 0.9f),
                    Quaternion.Euler((float)random.NextDouble() * 50f - 25f, (float)random.NextDouble() * 360f, (float)random.NextDouble() * 50f - 25f));
            }
            for (var i = 0; i < 3; i++)
                Box(g, wood, Along(alongX, ((float)random.NextDouble() - 0.5f) * length * 0.6f, 1.2f, ((float)random.NextDouble() - 0.5f) * breadth * 0.5f),
                    new Vector3(0.3f, 0.3f, 3.2f), Quaternion.Euler(20f + (float)random.NextDouble() * 30f, (float)random.NextDouble() * 360f, 0f));
        }

        /// <summary>A lava cut: a glowing flow over the block under plates of dark crust, flames and smoke off it (<see cref="Feed"/>).</summary>
        private void Lava(Transform parent, NavBlock b, System.Random random)
        {
            var g = Group(parent, b, "lava");
            Box(g, Surface("Obsidian"), new Vector3(0f, 0.03f, 0f), new Vector3(b.Width + 1.6f, 0.06f, b.Depth + 1.6f), Quaternion.identity, false);
            Box(g, Surface("LavaGlow"), new Vector3(0f, 0.08f, 0f), new Vector3(b.Width, 0.1f, b.Depth), Quaternion.identity, false);
            var crust = Surface("Obsidian");
            var plates = Mathf.Clamp(Mathf.RoundToInt(b.Width * b.Depth / 10f), 5, 24);
            for (var i = 0; i < plates; i++)
            {
                var x = ((float)random.NextDouble() - 0.5f) * b.Width * 0.9f;
                var z = ((float)random.NextDouble() - 0.5f) * b.Depth * 0.9f;
                var s = 0.8f + (float)random.NextDouble() * 1.8f;
                Box(g, crust, new Vector3(x, 0.16f, z), new Vector3(s, 0.12f, s * (0.5f + (float)random.NextDouble() * 0.6f)),
                    Quaternion.Euler(0f, (float)random.NextDouble() * 360f, (float)random.NextDouble() * 8f - 4f), false);
            }
        }

        /// <summary>A gate shut across the lane: a steel leaf between two concrete posts, a hazard bar along its top.</summary>
        private void Gate(Transform parent, NavBlock b)
        {
            var (alongX, length, breadth) = Axis(b);
            var g = Group(parent, b, "gate");
            var thick = Mathf.Clamp(breadth * 0.4f, 0.3f, 0.8f);
            Box(g, Surface("MetalSheet"), Along(alongX, 0f, 1.6f, 0f), Size(alongX, length - 1.2f, 3.2f, thick), Quaternion.identity);
            Box(g, Surface("SafetyStripe"), Along(alongX, 0f, 3.3f, 0f), Size(alongX, length - 1.2f, 0.25f, thick + 0.06f), Quaternion.identity, false);
            for (var side = -1; side <= 1; side += 2)
                Box(g, Surface("Concrete"), Along(alongX, side * (length * 0.5f - 0.4f), 1.9f, 0f), new Vector3(0.9f, 3.8f, 0.9f), Quaternion.identity);
        }

        private void Dust(NavBlock b, System.Random random)
        {
            var (alongX, length, breadth) = Axis(b);
            var puffs = Mathf.Clamp(Mathf.RoundToInt(length / 3f), 4, 14);
            for (var i = 0; i < puffs; i++)
            {
                var a = ((float)random.NextDouble() - 0.5f) * length;
                var across = ((float)random.NextDouble() - 0.5f) * breadth;
                var local = Along(alongX, a, 0.6f, across);
                _effects?.GroundDust(new Vector3(b.Center.X, 0f, b.Center.Y) + local, 2.2f);
            }
        }

        // ------------------------------------------------------------------ flames and smoke

        /// <summary>The burning strips' and lava's flames and smoke, at a steady rate by their area (capped).</summary>
        private void Feed(SiteLook look, float dt)
        {
            if (_effects == null) return;
            var lava = look.Look == Look.Lava;
            foreach (var (centre, size) in look.Burning)
            {
                var area = size.x * size.y / 100f;
                var fire = Mathf.Min(FireCap, FireRate * area) * (lava ? 0.35f : 1f);
                var smoke = Mathf.Min(SmokeCap, SmokeRate * area) * (lava ? 0.5f : 1f);
                look.FireDue += fire * dt;
                look.SmokeDue += smoke * dt;
                while (look.FireDue >= 1f)
                {
                    look.FireDue -= 1f;
                    var p = new Vector3(centre.x + (Random.value - 0.5f) * size.x, 0.3f, centre.y + (Random.value - 0.5f) * size.y);
                    _effects.GroundFire(p, lava ? Random.Range(0.8f, 1.4f) : Random.Range(2.2f, 3.6f));
                }
                while (look.SmokeDue >= 1f)
                {
                    look.SmokeDue -= 1f;
                    var p = new Vector3(centre.x + (Random.value - 0.5f) * size.x, 2.2f, centre.y + (Random.value - 0.5f) * size.y);
                    _effects.GroundSmoke(p, lava ? Random.Range(2f, 3f) : Random.Range(3.5f, 5.5f), lava ? 0.55f : 0.15f);
                }
            }
        }

        /// <summary>A stable hash of a site's id (string.GetHashCode may change between runs).</summary>
        private static int Hash(string s)
        {
            unchecked
            {
                var h = (int)2166136261;
                foreach (var c in s) h = (h ^ c) * 16777619;
                return h;
            }
        }
    }
}

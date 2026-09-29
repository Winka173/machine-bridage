using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using UnityEngine.UIElements;
using SimVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Views
{
    /// <summary>The Sandbox's overlays (prompt 21 E), each switched on and off on its own.</summary>
    public enum SandboxLayer
    {
        Range,
        Hits,
        Dps,
        Ammo,
        Zones,

        /// <summary>Internal build only (E.6).</summary>
        Hull,
        Route,
        Stuck,
        Buy,
    }

    /// <summary>
    /// Draws the Sandbox's overlays (prompt 21 E) from the simulation's own numbers: the metre grid of the flat test
    /// range, rings round the selection, the selected units' maximum and minimum range, floating hit numbers with
    /// ✓ ~ ✕ and the face struck, each unit's real DPS and combat value, magazines and reloads, big-attack zones and
    /// shield domes, and (internal build only) hit boxes, routes, stuck vehicles and the AI's buying scores. Lines are
    /// flat quads on the ground in a few meshes rebuilt a few times a second; words are pooled labels on the
    /// screen's own layer.
    /// </summary>
    internal sealed class SandboxOverlays
    {
        private const float Width = 0.35f, Lift = 0.09f;

        private readonly SandboxController _owner;
        private readonly SimWorld _world;
        private readonly ViewRegistry _views;
        private readonly RtsCamera _camera;
        private readonly Transform _root;
        private readonly Dictionary<Material, (MeshFilter filter, Mesh mesh, List<Vector3> v, List<int> t)> _layers = new();
        private readonly Material _ring, _max, _min, _hull, _route, _zone, _dome, _grid;
        private readonly List<Label> _pool = new();
        private readonly List<(Label label, Vector3 at, float born)> _floating = new();
        private int _used;
        private float _rebuildIn;
        private int _hitsSeen;

        public SandboxOverlays(SandboxController owner, SimWorld world, ViewRegistry views, RtsCamera camera, MaterialLibrary materials, Transform parent)
        {
            _owner = owner;
            _world = world;
            _views = views;
            _camera = camera;
            _root = new GameObject("Sandbox Overlays").transform;
            _root.SetParent(parent, false);
            _ring = materials.SelectionRing;
            _max = materials.MarkScout;
            _min = materials.MarkAttack;
            _hull = materials.MarkDefend;
            _route = materials.MoveMarker;
            _zone = materials.StrikeWarning;
            _dome = materials.BarAlly;
            _grid = materials.BoundaryLine;
            if (SandboxMaps.IsFlat(world.Map.Id)) BuildGrid();
            On[SandboxLayer.Range] = true;
            On[SandboxLayer.Hits] = true;
        }

        /// <summary>Which overlays are on.</summary>
        public Dictionary<SandboxLayer, bool> On { get; } = new();

        public bool IsOn(SandboxLayer layer) => On.TryGetValue(layer, out var on) && on && (!Internal(layer) || SandboxSession.Internal);

        public static bool Internal(SandboxLayer layer) => layer >= SandboxLayer.Hull;

        /// <summary>The screen's layer the words go on.</summary>
        public VisualElement Labels { get; set; }

        /// <summary>Where a drag that turns the selection is now (a line from the unit to it).</summary>
        public SimVector2? DragTo { get; set; }

        // ------------------------------------------------------------------ the grid (B.1)

        private void BuildGrid()
        {
            var m = _world.Map;
            var filter = Layer(_grid).filter;
            var v = new List<Vector3>();
            var t = new List<int>();
            for (var x = Mathf.Ceil(m.Min.X / SandboxMaps.GridStep) * SandboxMaps.GridStep; x <= m.Max.X; x += SandboxMaps.GridStep)
            {
                var w = Mathf.Abs(x % SandboxMaps.GridMajor) < 0.01f ? 0.3f : 0.1f;
                Quad(v, t, new Vector2(x, m.Min.Y), new Vector2(x, m.Max.Y), w, 0.03f);
            }
            for (var y = Mathf.Ceil(m.Min.Y / SandboxMaps.GridStep) * SandboxMaps.GridStep; y <= m.Max.Y; y += SandboxMaps.GridStep)
            {
                var w = Mathf.Abs(y % SandboxMaps.GridMajor) < 0.01f ? 0.3f : 0.1f;
                Quad(v, t, new Vector2(m.Min.X, y), new Vector2(m.Max.X, y), w, 0.03f);
            }
            var mesh = new Mesh { name = "Sandbox Grid", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.SetVertices(v);
            mesh.SetTriangles(t, 0);
            mesh.RecalculateBounds();
            filter.sharedMesh = mesh;
            _layers.Remove(_grid);
        }

        // ------------------------------------------------------------------ every frame

        public void Tick(float dt)
        {
            _rebuildIn -= dt;
            if (_rebuildIn <= 0f)
            {
                _rebuildIn = 0.1f;
                Lines();
            }
            Words(dt);
        }

        private (MeshFilter filter, Mesh mesh, List<Vector3> v, List<int> t) Layer(Material material)
        {
            if (_layers.TryGetValue(material, out var layer)) return layer;
            var go = new GameObject("Overlay " + material.name);
            go.transform.SetParent(_root, false);
            var filter = go.AddComponent<MeshFilter>();
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            var mesh = new Mesh { name = "Sandbox Overlay", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.MarkDynamic();
            filter.sharedMesh = mesh;
            layer = (filter, mesh, new List<Vector3>(), new List<int>());
            _layers[material] = layer;
            return layer;
        }

        private static void Quad(List<Vector3> v, List<int> t, Vector2 a, Vector2 b, float width, float lift = Lift)
        {
            var d = b - a;
            if (d.sqrMagnitude < 1e-6f) return;
            var side = new Vector2(-d.y, d.x).normalized * (width * 0.5f);
            var n = v.Count;
            v.Add(new Vector3(a.x - side.x, lift, a.y - side.y));
            v.Add(new Vector3(a.x + side.x, lift, a.y + side.y));
            v.Add(new Vector3(b.x + side.x, lift, b.y + side.y));
            v.Add(new Vector3(b.x - side.x, lift, b.y - side.y));
            t.Add(n);
            t.Add(n + 1);
            t.Add(n + 2);
            t.Add(n);
            t.Add(n + 2);
            t.Add(n + 3);
        }

        private void Circle(Material m, SimVector2 c, float r, float width = Width)
        {
            if (r <= 0.1f) return;
            var (_, _, v, t) = Layer(m);
            var segments = Mathf.Clamp((int)(r * 1.5f), 24, 128);
            for (var i = 0; i < segments; i++)
            {
                var a0 = i * Mathf.PI * 2f / segments;
                var a1 = (i + 1) * Mathf.PI * 2f / segments;
                Quad(v, t, new Vector2(c.X + Mathf.Cos(a0) * r, c.Y + Mathf.Sin(a0) * r), new Vector2(c.X + Mathf.Cos(a1) * r, c.Y + Mathf.Sin(a1) * r), width);
            }
        }

        private void Line(Material m, SimVector2 a, SimVector2 b, float width = Width)
        {
            var (_, _, v, t) = Layer(m);
            Quad(v, t, new Vector2(a.X, a.Y), new Vector2(b.X, b.Y), width);
        }

        private void Lines()
        {
            foreach (var layer in _layers.Values)
            {
                layer.v.Clear();
                layer.t.Clear();
            }
            foreach (var v in _owner.SelectedVehicles())
            {
                Circle(_ring, v.Position, v.Def.HullBound + 1.2f, 0.25f);
                // The heading: a short line out of its nose.
                Line(_ring, v.Position, v.Position + Sim.Core.SimMath.Forward(v.Heading) * (v.Def.HullBound + 4f), 0.25f);
                if (IsOn(SandboxLayer.Range))
                {
                    var (max, min) = SandboxProbe.Reach(v);
                    Circle(_max, v.Position, max);
                    Circle(_min, v.Position, min);
                }
            }
            if (DragTo is { } to)
                foreach (var v in _owner.SelectedVehicles())
                    Line(_ring, v.Position, to, 0.3f);
            if (IsOn(SandboxLayer.Zones) || IsOn(SandboxLayer.Hull) || IsOn(SandboxLayer.Route))
                foreach (var v in _world.Vehicles)
                {
                    if (!v.IsAlive) continue;
                    if (IsOn(SandboxLayer.Zones))
                    {
                        foreach (var z in SandboxProbe.BigZones(v))
                        {
                            if (z.Rect)
                            {
                                var across = new SimVector2(z.Axis.Y, -z.Axis.X) * z.HalfWidth;
                                var along = z.Axis * z.HalfLength;
                                var c = z.Centre;
                                Line(_zone, c - along - across, c + along - across);
                                Line(_zone, c + along - across, c + along + across);
                                Line(_zone, c + along + across, c - along + across);
                                Line(_zone, c - along + across, c - along - across);
                            }
                            else Circle(_zone, z.Centre, z.Radius);
                        }
                        Circle(_dome, v.Position, SandboxProbe.Dome(v));
                        if (v.Def.Wards is { } ward) Circle(_dome, v.Position, ward.Radius, 0.2f);
                    }
                    if (IsOn(SandboxLayer.Hull))
                    {
                        var (half, radius) = SandboxProbe.Hull(v);
                        var fwd = Sim.Core.SimMath.Forward(v.Heading) * half;
                        var right = new SimVector2(fwd.Y, -fwd.X);
                        var side = right.LengthSquared() > 1e-6f ? SimVector2.Normalize(right) * radius : new SimVector2(radius, 0f);
                        Line(_hull, v.Position - fwd - side, v.Position + fwd - side, 0.15f);
                        Line(_hull, v.Position - fwd + side, v.Position + fwd + side, 0.15f);
                        Circle(_hull, v.Position + fwd, radius, 0.15f);
                        Circle(_hull, v.Position - fwd, radius, 0.15f);
                    }
                    if (IsOn(SandboxLayer.Route))
                    {
                        var route = SandboxProbe.Route(v);
                        var from = v.Position;
                        foreach (var p in route)
                        {
                            Line(_route, from, p, 0.2f);
                            from = p;
                        }
                    }
                }
            foreach (var layer in _layers.Values)
            {
                layer.mesh.Clear();
                layer.mesh.SetVertices(layer.v);
                layer.mesh.SetTriangles(layer.t, 0);
                layer.mesh.RecalculateBounds();
            }
        }

        // ------------------------------------------------------------------ words

        private Label Take(string classes)
        {
            Label l;
            if (_used < _pool.Count) l = _pool[_used];
            else
            {
                l = new Label { pickingMode = PickingMode.Ignore };
                _pool.Add(l);
                Labels?.Add(l);
            }
            _used++;
            l.ClearClassList();
            l.AddToClassList("sb-word");
            foreach (var c in classes.Split(' '))
                if (c.Length > 0) l.AddToClassList(c);
            l.style.display = DisplayStyle.Flex;
            return l;
        }

        private bool Place(Label l, Vector3 world)
        {
            var panel = Labels?.panel;
            if (panel == null || _camera.Camera == null) return false;
            var sp = _camera.Camera.WorldToScreenPoint(world);
            if (sp.z <= 0f)
            {
                l.style.display = DisplayStyle.None;
                return false;
            }
            var p = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(sp.x, Screen.height - sp.y));
            l.style.left = p.x;
            l.style.top = p.y;
            return true;
        }

        private void Words(float dt)
        {
            _used = 0;
            var now = Time.unscaledTime;
            // E.2: a number for each new hit, rising for a second.
            if (IsOn(SandboxLayer.Hits))
            {
                var hits = _owner.Battle.Stats.Hits;
                if (hits != _hitsSeen)
                {
                    var fresh = hits - _hitsSeen;
                    _hitsSeen = hits;
                    var recent = new List<HitReport>(_owner.Battle.Stats.Recent);
                    for (var i = System.Math.Max(0, recent.Count - fresh); i < recent.Count; i++)
                    {
                        var h = recent[i];
                        if (_floating.Count > 48)
                        {
                            _floating[0].label.RemoveFromHierarchy();
                            _floating.RemoveAt(0);
                        }
                        var mark = h.Verdict switch { MatchVerdict.Good => "✓", MatchVerdict.Poor => "~", _ => "✕" };
                        var text = SandboxText.Format("sandbox.hit", ("damage", SandboxText.Number(h.Dealt)), ("mark", mark),
                            ("face", Strings.Get("armour.face." + (int)h.Face)));
                        var label = new Label(text) { pickingMode = PickingMode.Ignore };
                        label.AddToClassList("sb-word");
                        label.AddToClassList("sb-hit");
                        label.AddToClassList(h.Verdict == MatchVerdict.Good ? "sb-hit--good" : h.Verdict == MatchVerdict.Poor ? "sb-hit--poor" : "sb-hit--none");
                        Labels?.Add(label);
                        _floating.Add((label, new Vector3(h.At.X, 2.5f, h.At.Y), now));
                    }
                }
            }
            else _hitsSeen = _owner.Battle.Stats.Hits;
            for (var i = _floating.Count - 1; i >= 0; i--)
            {
                var (label, at, born) = _floating[i];
                var age = now - born;
                if (age > 1.2f || !IsOn(SandboxLayer.Hits))
                {
                    label.RemoveFromHierarchy();
                    _floating.RemoveAt(i);
                    continue;
                }
                Place(label, at + Vector3.up * (age * 2.5f));
                label.style.opacity = 1f - age / 1.2f;
            }
            // E.3, E.4, E.6: over the units (the selection, or everyone when nothing is selected, at most 40).
            var dps = IsOn(SandboxLayer.Dps);
            var ammo = IsOn(SandboxLayer.Ammo);
            var stuck = IsOn(SandboxLayer.Stuck) ? SandboxProbe.Stuck(_owner.Battle.Stuck) : null;
            if (dps || ammo || stuck != null)
            {
                var shown = 0;
                IEnumerable<Vehicle> who = _owner.Selected.Count > 0 ? _owner.SelectedVehicles() : _world.Vehicles;
                foreach (var v in who)
                {
                    if (!v.IsAlive || shown++ >= 40) continue;
                    var lines = new List<string>();
                    if (dps)
                        lines.Add(SandboxText.Format("sandbox.dps.line", ("dps", SandboxText.Number(_owner.Battle.Stats.Dps(v.Id.Value), 1)),
                            ("value", SandboxText.Number(v.Def.CombatValue, 2))));
                    if (ammo)
                        foreach (var w in SandboxProbe.Weapons(v))
                        {
                            var line = w.Ammo < 0 || w.Full == 0 ? Strings.Get("sandbox.ammo.unlimited")
                                : SandboxText.Format("sandbox.ammo.line", ("ammo", w.Ammo), ("full", w.Full));
                            if (w.ReloadLeft > 0f) line += " · " + SandboxText.Format("sandbox.ammo.reload", ("seconds", SandboxText.Number(w.ReloadLeft, 1)));
                            lines.Add(line);
                        }
                    if (stuck != null && stuck.Contains(v.Id.Value)) lines.Add(Strings.Get("sandbox.stuck"));
                    if (lines.Count == 0) continue;
                    var label = Take(stuck != null && stuck.Contains(v.Id.Value) ? "sb-tag sb-tag--stuck" : "sb-tag");
                    label.text = string.Join("\n", lines);
                    Place(label, new Vector3(v.Position.X, v.Def.Flying ? v.Def.Altitude + 3f : 4f, v.Position.Y));
                }
            }
            for (var i = _used; i < _pool.Count; i++) _pool[i].style.display = DisplayStyle.None;
        }
    }
}

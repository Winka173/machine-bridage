using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Markers over a mission's targets, so the goal reads on the battlefield and not only in the
    /// objective panel: a red diamond with crosshair ticks over what to destroy (a demolition
    /// target, a hunted vehicle), a blue one over a building to keep standing, and an amber one
    /// over a spot to scout, filling as the look is taken. Each floats over its target, bobbing
    /// a little, facing the camera, built from quads so it needs no texture.
    /// </summary>
    internal sealed class MissionMarkers : IDisposable
    {
        private const float Size = 2.6f;

        private sealed class Marker
        {
            public Transform Root;
            public Transform Fill;
            public GameObject[] Ticks;
            public Renderer[] Coloured;
            public MissionMarkKind Kind = (MissionMarkKind)(-1);
        }

        private readonly MeshLibrary _meshes;
        private readonly MaterialLibrary _materials;
        private readonly Transform _root;
        private readonly List<Marker> _pool = new();
        private readonly Dictionary<EntityId, float> _tops = new();

        public MissionMarkers(MeshLibrary meshes, MaterialLibrary materials, Transform parent)
        {
            _meshes = meshes;
            _materials = materials;
            _root = new GameObject("Mission Markers").transform;
            _root.SetParent(parent, false);
        }

        public void Render(IReadOnlyList<MissionMark> marks, ViewRegistry views, MapView map, Quaternion cameraRotation, float time)
        {
            var shown = 0;
            for (var i = 0; i < marks.Count; i++)
            {
                var mark = marks[i];
                Vector3 at;
                if (mark.Prop) at = new Vector3(mark.Position.X, Top(mark.Entity, map) + 3.2f, mark.Position.Y);
                else if (mark.Entity.IsValid && views.TryGet(mark.Entity, out var view))
                    at = view.Position + Vector3.up * (view.ModelBounds.max.y * view.Def.Scale + 4.4f);
                else at = new Vector3(mark.Position.X, 5f, mark.Position.Y);
                var marker = Take(shown++);
                Dress(marker, mark.Kind);
                marker.Root.position = at + Vector3.up * (0.3f * Mathf.Sin(time * 2.2f + i * 1.3f));
                marker.Root.rotation = cameraRotation;
                if (mark.Kind == MissionMarkKind.Scout)
                {
                    // The look fills the diamond from the middle out.
                    var fill = Mathf.Lerp(0.18f, 0.62f, Mathf.Clamp01(mark.Progress));
                    marker.Fill.localScale = new Vector3(fill, fill, 1f);
                }
                else
                {
                    // A slow pulse so a target catches the eye.
                    var pulse = 0.62f * (1f + 0.07f * Mathf.Sin(time * 5f + i));
                    marker.Fill.localScale = new Vector3(pulse, pulse, 1f);
                }
            }
            for (var i = shown; i < _pool.Count; i++)
                if (_pool[i].Root.gameObject.activeSelf) _pool[i].Root.gameObject.SetActive(false);
        }

        /// <summary>The height of a building's top, measured once from its drawn model.</summary>
        private float Top(EntityId id, MapView map)
        {
            if (_tops.TryGetValue(id, out var top)) return top;
            top = 6f;
            if (map.TryGetProp(id, out var prop) && prop.GameObject != null)
            {
                var found = false;
                foreach (var r in prop.GameObject.GetComponentsInChildren<Renderer>())
                {
                    top = found ? Mathf.Max(top, r.bounds.max.y) : r.bounds.max.y;
                    found = true;
                }
            }
            _tops[id] = top;
            return top;
        }

        private Marker Take(int index)
        {
            if (index < _pool.Count)
            {
                var m = _pool[index];
                if (!m.Root.gameObject.activeSelf) m.Root.gameObject.SetActive(true);
                return m;
            }
            var marker = new Marker { Root = new GameObject("Marker").transform };
            marker.Root.SetParent(_root, false);
            marker.Root.localScale = Vector3.one * Size;
            var back = VehicleView.CreateMesh("Back", marker.Root, _meshes.Quad, _materials.BarBack, false);
            back.localRotation = Quaternion.Euler(0f, 0f, 45f);
            var rim = VehicleView.CreateMesh("Rim", marker.Root, _meshes.Quad, _materials.MarkAttack, false);
            rim.localScale = new Vector3(0.8f, 0.8f, 1f);
            rim.localRotation = Quaternion.Euler(0f, 0f, 45f);
            rim.localPosition = new Vector3(0f, 0f, -0.01f);
            var hollow = VehicleView.CreateMesh("Hollow", marker.Root, _meshes.Quad, _materials.BarBack, false);
            hollow.localScale = new Vector3(0.66f, 0.66f, 1f);
            hollow.localRotation = Quaternion.Euler(0f, 0f, 45f);
            hollow.localPosition = new Vector3(0f, 0f, -0.02f);
            marker.Fill = VehicleView.CreateMesh("Fill", marker.Root, _meshes.Quad, _materials.MarkAttack, false);
            marker.Fill.localRotation = Quaternion.Euler(0f, 0f, 45f);
            marker.Fill.localPosition = new Vector3(0f, 0f, -0.03f);
            // A pin down towards the target.
            var pin = VehicleView.CreateMesh("Pin", marker.Root, _meshes.Quad, _materials.MarkAttack, false);
            pin.localScale = new Vector3(0.07f, 0.55f, 1f);
            pin.localPosition = new Vector3(0f, -0.95f, 0f);
            // Crosshair ticks round an attack marker.
            marker.Ticks = new GameObject[4];
            for (var k = 0; k < 4; k++)
            {
                var tick = VehicleView.CreateMesh("Tick", marker.Root, _meshes.Quad, _materials.MarkAttack, false);
                var angle = k * 90f;
                var dir = Quaternion.Euler(0f, 0f, angle) * Vector3.up;
                tick.localPosition = dir * 0.86f;
                tick.localRotation = Quaternion.Euler(0f, 0f, angle);
                tick.localScale = new Vector3(0.09f, 0.3f, 1f);
                marker.Ticks[k] = tick.gameObject;
            }
            marker.Coloured = new Renderer[] { rim.GetComponent<Renderer>(), marker.Fill.GetComponent<Renderer>(), pin.GetComponent<Renderer>() };
            _pool.Add(marker);
            return marker;
        }

        private void Dress(Marker marker, MissionMarkKind kind)
        {
            if (marker.Kind == kind) return;
            marker.Kind = kind;
            var material = kind switch
            {
                MissionMarkKind.Defend => _materials.MarkDefend,
                MissionMarkKind.Scout => _materials.MarkScout,
                _ => _materials.MarkAttack,
            };
            foreach (var r in marker.Coloured) r.sharedMaterial = material;
            foreach (var tick in marker.Ticks)
            {
                tick.GetComponent<Renderer>().sharedMaterial = material;
                tick.SetActive(kind == MissionMarkKind.Attack);
            }
        }

        public void Dispose()
        {
            if (_root != null) UnityEngine.Object.Destroy(_root.gameObject);
        }
    }
}

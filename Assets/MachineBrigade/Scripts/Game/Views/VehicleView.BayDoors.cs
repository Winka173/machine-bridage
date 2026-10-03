using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): a bomber's bay doors swing open for its stick. Only the
    /// models with hinge pivots open (Part_bay_door_L / _R, prompt 35 wave 10: heavy_bomber and command_airship); the
    /// other bombers' doors are merged into their hull (Bay_doors meshes, no hinge) and stay as they are. The doors open
    /// over the stick's data bay-open time (stick.bayOpen), stay open while <see cref="OpenBay"/> holds them and close the
    /// same way after. Which way each door swings is worked out once from its own mesh: about the hull's long axis, its
    /// free edge going down. View only.
    /// </summary>
    public sealed partial class VehicleView
    {
        /// <summary>How far a door swings open (degrees about its hinge).</summary>
        internal const float BayDoorAngle = 80f;

        private readonly List<(Transform door, Quaternion rest, Vector3 axis, float sign)> _bayDoors = new();
        private float _bayOpenUntil = -10f;
        private float _bayOpenness;

        /// <summary>The mount that lays the stick (-1: none) and its stick.</summary>
        internal int BayMount { get; private set; } = -1;

        internal StickDef BayStick { get; private set; }

        /// <summary>The model has bay doors on hinges (and a weapon that lays a stick).</summary>
        internal bool HasBayDoors => _bayDoors.Count > 0 && BayStick != null;

        /// <summary>When this unit's last stick began (render clock; the view's own, for a boss bay's doors to open before the next).</summary>
        internal float LastStickAt { get; set; } = -100f;

        /// <summary>How open the doors are now (0 shut, 1 open; tests and tools).</summary>
        internal float BayOpenness => _bayOpenness;

        private void InitBayDoors()
        {
            if (_model?.Root == null) return;
            for (var i = 0; i < Sim.Def.Mounts.Count; i++)
            {
                var stick = Sim.Arm(i).Stick;
                if (stick == null || stick.Mode != StickMode.Stick) continue;
                BayMount = i;
                BayStick = stick;
                break;
            }
            if (BayStick == null) return;
            var along = Root != null ? Root.forward : _model.Root.transform.forward;
            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
            {
                if (!ModelLibrary.BayDoorPattern.IsMatch(t.name)) continue;
                var renderers = t.GetComponentsInChildren<Renderer>(true);
                if (renderers.Length == 0) continue;
                var bounds = renderers[0].bounds;
                for (var r = 1; r < renderers.Length; r++) bounds.Encapsulate(renderers[r].bounds);
                // The door hangs inboard of its hinge: its free edge must go down as it opens.
                var hang = bounds.center - t.position;
                var axis = t.InverseTransformDirection(along);
                if (hang.sqrMagnitude < 1e-6f || axis.sqrMagnitude < 1e-6f) continue;
                axis.Normalize();
                var local = t.InverseTransformVector(hang);
                var turned = t.TransformVector(Quaternion.AngleAxis(10f, axis) * local);
                var sign = turned.y < hang.y ? 1f : -1f;
                _bayDoors.Add((t, t.localRotation, axis, sign));
            }
        }

        /// <summary>Opens the bay doors (they swing over the stick's bay-open time) and keeps them open <paramref name="hold"/> s from now.</summary>
        internal void OpenBay(float hold)
        {
            if (_bayDoors.Count == 0) return;
            _bayOpenUntil = Mathf.Max(_bayOpenUntil, Time.time + Mathf.Max(0f, hold));
        }

        private void AnimateBayDoors()
        {
            if (_bayDoors.Count == 0) return;
            var open = Time.time < _bayOpenUntil && Sim.IsAlive && !_wreck;
            var seconds = Mathf.Max(0.2f, BayStick != null && BayStick.BayOpen > 0f ? BayStick.BayOpen : 1f);
            var target = open ? 1f : 0f;
            if (Mathf.Approximately(_bayOpenness, target)) return;
            _bayOpenness = Mathf.MoveTowards(_bayOpenness, target, Time.deltaTime / seconds);
            var eased = _bayOpenness * _bayOpenness * (3f - 2f * _bayOpenness);
            foreach (var (door, rest, axis, sign) in _bayDoors)
                if (door != null) door.localRotation = rest * Quaternion.AngleAxis(sign * BayDoorAngle * eased, axis);
        }
    }
}

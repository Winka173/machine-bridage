using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Conquest objectives on the battlefield: a marking on the ground in the owner's colour
    /// (a solid rim, a slowly turning dashed ring, a soft tint) with the capture progress
    /// sweeping round it in the capturing side's colour, pulsing while contested, and a flag
    /// that changes colour when the point changes hands.
    /// </summary>
    public sealed class ObjectiveView
    {
        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly Color Neutral = new(0.8f, 0.8f, 0.74f);
        private static readonly Color Contest = new(1.5f, 1.1f, 0.4f);

        private sealed class Marker
        {
            public ObjectiveState State;
            public GroundMark Mark;
            public Renderer Flag;
            public Transform FlagTransform;
        }

        private readonly List<Marker> _markers = new();
        private readonly MaterialPropertyBlock _block = new();
        private readonly Transform _root;

        public ObjectiveView(ConquestMode mode, MeshLibrary meshes, MaterialLibrary materials, Transform parent)
        {
            _root = new GameObject("Objectives").transform;
            _root.SetParent(parent, false);
            foreach (var point in mode.Points)
            {
                var at = new Vector3(point.Def.Position.X, 0f, point.Def.Position.Y);
                var mark = new GroundMark($"Objective {point.Def.Id}", _root, meshes, materials, GroundMark.Style.Objective);
                mark.Transform.position = at + Vector3.up * 0.09f;
                mark.Transform.localScale = Vector3.one * point.Def.Radius;

                var pole = VehicleView.CreateMesh("Pole", _root, meshes.Box, materials.ForModel("Steel", -1), true);
                pole.position = at + Vector3.up * 3.5f;
                pole.localScale = new Vector3(0.14f, 7f, 0.14f);
                var flag = VehicleView.CreateMesh("Flag", _root, meshes.Box, materials.Objective, false);
                flag.position = at + new Vector3(0.9f, 6.2f, 0f);
                flag.localScale = new Vector3(1.8f, 1.1f, 0.05f);

                _markers.Add(new Marker
                {
                    State = point,
                    Mark = mark,
                    Flag = flag.GetComponent<Renderer>(),
                    FlagTransform = flag,
                });
            }
        }

        public void Render(float time)
        {
            foreach (var m in _markers)
            {
                var s = m.State;
                var owner = s.Owner == 0 ? TeamColors.Ui(0) * 1.15f : s.Owner == 1 ? TeamColors.Ui(1) * 1.15f : Neutral;
                Tint(m.Flag, owner);

                // The arc shows how far the capture has got, in the colour of the side taking it;
                // it hides once the point is fully held.
                var amount = Mathf.Abs(s.Progress);
                var capturing = s.Progress > 0f ? TeamColors.Ui(0) : TeamColors.Ui(1);
                var rim = s.Contested ? Color.Lerp(owner, Contest, 0.5f) : owner;
                rim.a = 1f;
                m.Mark.Set(rim, capturing, amount < 0.999f ? amount : 0f, s.Contested ? 1f : 0f);

                // The flag flutters about its pole.
                var sway = Mathf.Sin(time * 3f + s.Def.Position.X) * 8f;
                var pole = m.FlagTransform.position - m.FlagTransform.rotation * new Vector3(0.9f, 0f, 0f);
                m.FlagTransform.rotation = Quaternion.Euler(0f, sway, 0f);
                m.FlagTransform.position = pole + m.FlagTransform.rotation * new Vector3(0.9f, 0f, 0f);
            }
        }

        private void Tint(Renderer renderer, Color colour)
        {
            _block.SetColor(ColorId, colour);
            renderer.SetPropertyBlock(_block);
        }
    }
}

using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 23 F.4: a Meridian Accord unit on our side (the allied AI's, not the player's) reads apart from the player's
    /// own: its health bar is the Accord's sky blue (teal in the colour-blind palette) instead of our green, and the Accord's
    /// sign stands left of where the bar is, shown whether the bar is or not: a thick ring with its meridian through it, on
    /// a dark square (the "accord" icon's shape). Built from quads and one ring mesh like the other marks, so it batches.
    /// <para>
    /// Which units: the simulation's allied-unit tag (<see cref="MachineBrigade.Sim.Entities.Vehicle.Ally"/>: the allied
    /// commander's units, Mara's Behemoth, and the event system's Accord reinforcements when it gives them to the allied AI),
    /// or the view-side flag <see cref="AccordMarked"/> the runner sets for reinforcements that stay ordinary units of ours
    /// (<c>MatchRunner.MarkAccord</c>). A unit that changes sides is rebuilt, so the mark follows it.
    /// </para>
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _accordMark;
        private MeshRenderer _barFillRenderer;
        private Material _barAccord, _barUsual;
        private bool _accordShown;

        /// <summary>The runner's view-side Accord flag (F.4), for reinforcements the simulation does not tag as allied.</summary>
        public bool AccordMarked { get; set; }

        /// <summary>This is one of the Meridian Accord's units on our side, not the player's own.</summary>
        public bool Accord => _ours && (Sim.Ally || AccordMarked);

        /// <summary>The Accord's sign is up (the checks).</summary>
        internal bool AccordMarkShown => _accordShown;

        /// <summary>The material the health bar fills with now (the checks).</summary>
        internal Material BarFillMaterial => _barFillRenderer.sharedMaterial;

        private void BuildAccordMark(MeshLibrary meshes, MaterialLibrary materials)
        {
            _barAccord = materials.BarAccord;
            _barFillRenderer = _barFill.GetComponent<MeshRenderer>();
            _accordMark = new GameObject("AccordMark").transform;
            _accordMark.SetParent(Root, false);
            var back = CreateMesh("Back", _accordMark, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(0.9f, 0.9f, 1f);
            // The ring lies on the ground: stood up to face the camera like the quads (its face from +Y to -Z).
            var ring = CreateMesh("Ring", _accordMark, meshes.BadgeRing, materials.AccordMark, false);
            ring.localScale = Vector3.one * 0.34f;
            ring.localRotation = Quaternion.Euler(-90f, 0f, 0f);
            ring.localPosition = new Vector3(0f, 0f, -0.01f);
            var meridian = CreateMesh("Meridian", _accordMark, meshes.Quad, materials.AccordMark, false);
            meridian.localScale = new Vector3(0.09f, 0.72f, 1f);
            meridian.localPosition = new Vector3(0f, 0f, -0.02f);
            _accordMark.gameObject.SetActive(false);
        }

        private void RenderAccordMark(Quaternion cameraRotation)
        {
            var on = Sim.IsAlive && Accord;
            if (on != _accordShown)
            {
                _accordShown = on;
                _accordMark.gameObject.SetActive(on);
                if (on)
                {
                    _barUsual = _barFillRenderer.sharedMaterial;
                    _barFillRenderer.sharedMaterial = _barAccord;
                }
                else if (_barUsual != null) _barFillRenderer.sharedMaterial = _barUsual;
            }
            if (!on) return;
            _accordMark.rotation = cameraRotation;
            _accordMark.position = _bar.parent.TransformPoint(_bar.localPosition) + cameraRotation * new Vector3(-(BarWidth * 0.5f + 0.62f), 0f, 0f);
        }

        /// <summary>F.5: where a name label stands over this vehicle, just above its health bar (world space).</summary>
        public Vector3 LabelPoint => _bar.parent.TransformPoint(_bar.localPosition) + Vector3.up * 0.8f;
    }
}

using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 25 G (DECISIONS 25G): a gun changing rounds flashes a small glyph over the unit's health bar for a moment:
    /// two rounds side by side with a two-way arrow between them on a dark diamond (the "ammoswap" icon's shape, in the
    /// orange of the bar's other marks). Built from quads like the repair wrench, so it batches; the bar shows while it does.
    /// </summary>
    public sealed partial class VehicleView
    {
        private Transform _roundMark;
        private float _roundUntil = -1f;

        /// <summary>Seconds the glyph stays up after a change of rounds begins.</summary>
        internal const float RoundMarkSeconds = 1.2f;

        /// <summary>A gun of this unit has just started changing rounds (the sim's RoundSwitched).</summary>
        public void ShowRoundSwitch() => _roundUntil = Time.time + RoundMarkSeconds;

        /// <summary>The glyph is up now (the bar shows for it).</summary>
        internal bool RoundMarkWanted => Time.time < _roundUntil;

        private void BuildRoundMark(MeshLibrary meshes, MaterialLibrary materials)
        {
            _roundMark = new GameObject("RoundMark").transform;
            _roundMark.SetParent(_bar, false);
            _roundMark.localPosition = new Vector3(0.95f, 0.72f, 0f);
            var back = CreateMesh("Back", _roundMark, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(0.86f, 0.86f, 1f);
            back.localRotation = Quaternion.Euler(0f, 0f, 45f);
            foreach (var x in new[] { -0.17f, 0.17f })
            {
                var body = CreateMesh("Round", _roundMark, meshes.Quad, materials.EscortMark, false);
                body.localScale = new Vector3(0.11f, 0.26f, 1f);
                body.localPosition = new Vector3(x, -0.05f, -0.01f);
                var tip = CreateMesh("Tip", _roundMark, meshes.Quad, materials.EscortMark, false);
                tip.localScale = new Vector3(0.078f, 0.078f, 1f);
                tip.localRotation = Quaternion.Euler(0f, 0f, 45f);
                tip.localPosition = new Vector3(x, 0.08f, -0.01f);
            }
            var shaft = CreateMesh("Arrow", _roundMark, meshes.Quad, materials.EscortMark, false);
            shaft.localScale = new Vector3(0.14f, 0.04f, 1f);
            shaft.localPosition = new Vector3(0f, -0.02f, -0.01f);
            foreach (var x in new[] { -0.075f, 0.075f })
            {
                var head = CreateMesh("ArrowHead", _roundMark, meshes.Quad, materials.EscortMark, false);
                head.localScale = new Vector3(0.07f, 0.07f, 1f);
                head.localRotation = Quaternion.Euler(0f, 0f, 45f);
                head.localPosition = new Vector3(x, -0.02f, -0.01f);
            }
            _roundMark.gameObject.SetActive(false);
        }

        /// <summary>Shows the glyph while it is wanted, with a small pulse so it catches the eye.</summary>
        private void RenderRoundMark()
        {
            if (_roundMark == null) return;
            var on = RoundMarkWanted;
            if (_roundMark.gameObject.activeSelf != on) _roundMark.gameObject.SetActive(on);
            if (on) _roundMark.localScale = Vector3.one * (1f + 0.12f * Mathf.Sin(Time.time * 9f));
        }
    }
}

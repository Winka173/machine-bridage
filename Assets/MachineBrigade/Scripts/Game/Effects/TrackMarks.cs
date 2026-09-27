using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Track marks: dark prints lying flat on the ground behind moving vehicles, fading over half
    /// a minute. One shared particle system (flat quads, each turned to its vehicle's heading), so a
    /// whole battle's tracks cost one draw call.
    /// </summary>
    internal sealed class TrackMarks
    {
        private const float Life = 30f;
        private readonly ParticleSystem _marks;

        public TrackMarks(MaterialLibrary materials, Transform parent)
        {
            _marks = PB.Create(parent, "Track Marks", materials.Tread, ParticleSystemRenderMode.HorizontalBillboard);
            var main = _marks.main;
            main.loop = true;
            main.maxParticles = 4000;
            main.startSize3D = true;
            main.startLifetime = Life;
            main.startSpeed = 0f;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            var emission = _marks.emission;
            emission.enabled = false;
            var shape = _marks.shape;
            shape.enabled = false;
            // Fresh prints are darkest; they fade into the ground over their last two thirds.
            var fade = new Gradient();
            fade.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0.9f, 0.3f), new GradientAlphaKey(0f, 1f) });
            PB.Colors(_marks, fade);
            var renderer = _marks.GetComponent<ParticleSystemRenderer>();
            renderer.maxParticleSize = 5f;
            renderer.sortMode = ParticleSystemSortMode.None;
            _marks.Play();
        }

        /// <summary>One print at <paramref name="at"/> (on the ground), turned to <paramref name="heading"/> degrees.</summary>
        public void Print(Vector3 at, float heading, float width)
        {
            _marks.Emit(new ParticleSystem.EmitParams
            {
                position = new Vector3(at.x, 0.035f, at.z),
                startSize3D = new Vector3(width, 0.95f, 1f),
                rotation = heading,
                startColor = new Color(0.12f, 0.1f, 0.08f, 0.42f),
                startLifetime = Life,
                velocity = Vector3.zero,
                applyShapeToPosition = false,
            }, 1);
        }

        public void Clear() => _marks.Clear();
    }
}

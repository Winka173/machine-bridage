using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Play-test 13: decoy flare materials. A magnesium/Teflon/Viton flare burns at over 2000 C: a small blinding white
    /// point (a sharp, peaked core, far over 1 for the bloom) inside a faint warm-white halo of light around it.
    /// </summary>
    public sealed partial class MaterialLibrary
    {
        private Material _flareCore, _flareGlow;

        /// <summary>The burning pellet: additive, a steep dot (bright centre, quick falloff), HDR so the bloom flares it.</summary>
        public Material FlareCore => _flareCore != null ? _flareCore : _flareCore = Particle(Find("MachineBrigade/Particle"), "FlareCore", additive: true,
            intensity: 7f, shape: 0f, softness: 2.4f, depthPull: 3f);

        /// <summary>The light around it: additive, wide and faint.</summary>
        public Material FlareGlow => _flareGlow != null ? _flareGlow : _flareGlow = Particle(Find("MachineBrigade/Particle"), "FlareGlow", additive: true,
            intensity: 1.4f, shape: 0f, softness: 1.8f, depthPull: 3f);
    }
}

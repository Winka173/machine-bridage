using System;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Materials for the flipbook sheets in Resources/Textures/Fx, rendered from Mantaflow fire and
    /// smoke simulations (see Flipbook.shader for the channel layout). They are shared by every
    /// match and built once: a few textures and materials, never destroyed.
    /// </summary>
    internal sealed class FxMaterials
    {
        /// <summary>Frames across (and down) every sheet.</summary>
        public const int Tiles = 8;

        private static FxMaterials _shared;

        private FxMaterials()
        {
            var shader = Shader.Find("MachineBrigade/Flipbook");
            if (shader == null) throw new InvalidOperationException("Shader 'MachineBrigade/Flipbook' is missing; it must live in Resources/Shaders.");
            var fire = Sheet("fx_fire");
            var blast = Sheet("fx_blast");
            var smoke = Sheet("fx_smoke");
            var scorch = Sheet("fx_scorch");

            // A burning wreck, crater or building: orange flames with a dark sooty fringe.
            Flames = Make(shader, "Flames", fire, 3010, depthPull: 9f);
            Flames.SetFloat("_FireIntensity", 3.2f);
            Flames.SetFloat("_FireOpacity", 0.5f);
            Flames.SetFloat("_SmokeShadow", 0.25f);
            Flames.SetFloat("_SmokeLight", 0.75f);

            // Napalm and thermobaric fuel: redder, denser, with heavy black smoke.
            Napalm = Make(shader, "Napalm", fire, 3010, depthPull: 9f);
            Napalm.SetColor("_FireDeep", new Color(0.6f, 0.04f, 0.0f));
            Napalm.SetColor("_FireMid", new Color(1f, 0.3f, 0.02f));
            Napalm.SetColor("_FireHot", new Color(1f, 0.72f, 0.3f));
            Napalm.SetFloat("_FireIntensity", 3.6f);
            Napalm.SetFloat("_HeatScale", 1.15f);
            Napalm.SetFloat("_FireOpacity", 0.6f);
            Napalm.SetFloat("_Density", 1.35f);
            Napalm.SetFloat("_SmokeShadow", 0.18f);
            Napalm.SetFloat("_SmokeLight", 0.55f);

            // Explosion fireballs rolling up into smoke.
            Blast = Make(shader, "Blast", blast, 3010, depthPull: 10f);
            Blast.SetFloat("_FireIntensity", 3.8f);
            Blast.SetFloat("_HeatScale", 1.1f);
            Blast.SetFloat("_FireOpacity", 0.55f);
            Blast.SetFloat("_SmokeShadow", 0.3f);
            Blast.SetFloat("_SmokeLight", 1f);

            // The biggest blasts (strikes, ammunition, fuel) burn hotter and whiter.
            HotBlast = Make(shader, "HotBlast", blast, 3010, depthPull: 12f);
            HotBlast.SetColor("_FireMid", new Color(1f, 0.46f, 0.1f));
            HotBlast.SetColor("_FireHot", new Color(1f, 0.93f, 0.75f));
            HotBlast.SetFloat("_FireIntensity", 4.6f);
            HotBlast.SetFloat("_HeatScale", 1.3f);
            HotBlast.SetFloat("_FireOpacity", 0.6f);
            HotBlast.SetFloat("_SmokeShadow", 0.3f);
            HotBlast.SetFloat("_SmokeLight", 1f);

            // Billowing smoke; its darkness comes from the particle colour.
            Smoke = Make(shader, "Smoke", smoke, 3000, depthPull: 8f);
            Smoke.SetFloat("_FireIntensity", 0f);
            Smoke.SetFloat("_SmokeShadow", 0.42f);
            Smoke.SetFloat("_SmokeLight", 1.2f);
            Smoke.SetFloat("_GroundFade", 1.6f);

            // Dust and earth thrown up by a blast: softer shading, thinner.
            Dust = Make(shader, "Dust", smoke, 3000, depthPull: 6f);
            Dust.SetFloat("_FireIntensity", 0f);
            Dust.SetFloat("_SmokeShadow", 0.62f);
            Dust.SetFloat("_SmokeLight", 1.12f);
            Dust.SetFloat("_Density", 0.85f);
            Dust.SetFloat("_GroundFade", 1.2f);

            // Scorch marks: four variants in a 2x2 sheet, one material each so they instance.
            Scorch = new Material[4];
            for (var i = 0; i < Scorch.Length; i++)
            {
                var m = Make(shader, "Scorch" + i, scorch, 2950, depthPull: 0f, blend: false);
                m.SetFloat("_FireIntensity", 0f);
                m.SetFloat("_SmokeShadow", 0.55f);
                m.SetFloat("_SmokeLight", 1.7f);
                m.SetTextureScale("_MainTex", new Vector2(0.5f, 0.5f));
                m.SetTextureOffset("_MainTex", new Vector2(i % 2 * 0.5f, i / 2 * 0.5f));
                m.enableInstancing = true;
                Scorch[i] = m;
            }
        }

        /// <summary>The shared set; rebuilt if something unloaded it.</summary>
        public static FxMaterials Shared => _shared != null && _shared.Flames != null ? _shared : _shared = new FxMaterials();

        public Material Flames { get; }
        public Material Napalm { get; }
        public Material Blast { get; }
        public Material HotBlast { get; }
        public Material Smoke { get; }
        public Material Dust { get; }
        public Material[] Scorch { get; }

        private static Texture2D Sheet(string name)
        {
            var texture = Resources.Load<Texture2D>("Textures/Fx/" + name);
            if (texture == null) throw new InvalidOperationException($"Flipbook sheet 'Resources/Textures/Fx/{name}' is missing.");
            return texture;
        }

        private static Material Make(Shader shader, string name, Texture texture, int queue, float depthPull, bool blend = true)
        {
            var m = new Material(shader) { name = name, renderQueue = queue, hideFlags = HideFlags.DontSave };
            m.SetTexture("_MainTex", texture);
            m.SetFloat("_DepthPull", depthPull);
            if (blend) m.EnableKeyword("_FLIPBOOK_BLEND");
            return m;
        }
    }
}

using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Materials for the flipbook sheets in Resources/Textures/Fx, rendered from Mantaflow fire and
    /// smoke simulations (see Flipbook.shader for the channel layout). They are shared by every
    /// match and built once: a few textures and materials, never destroyed.
    /// </summary>
    /// <summary>
    /// The fixed draw order of the blended effects, back to front. Most effects emit into a few
    /// systems shared by the whole map, whose bounds span the battlefield, so Unity's sort by
    /// distance between two of them is arbitrary and flips as blasts come and go elsewhere: a
    /// blast's smoke popping over a smoke screen, then under it. One queue per layer keeps the
    /// order steady. Additive light (flashes, sparks, glow) comes last, at 3010, and shows through
    /// everything.
    /// </summary>
    internal static class FxQueue
    {
        /// <summary>Soft haze (tread dust, shell trails, flak puffs; MaterialLibrary.Smoke).</summary>
        public const int Haze = 3000;

        /// <summary>Dust and earth thrown up by blasts.</summary>
        public const int Dust = 3001;

        /// <summary>Smoke: blasts', fires', burning hulls'.</summary>
        public const int Smoke = 3002;

        /// <summary>Flames and napalm.</summary>
        public const int Flames = 3003;

        /// <summary>Fireballs.</summary>
        public const int Fireball = 3004;

        /// <summary>
        /// Smoke screens, over every blast and fire inside or behind them (see
        /// <see cref="BlastLayers.Route"/> for the ones in front).
        /// </summary>
        public const int Screen = 3005;

        /// <summary>Added to a layer's queue for its twin drawn in front of the smoke screens (3006 to 3009).</summary>
        public const int FrontOffset = Screen + 1 - Dust;
    }

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
            Flames = Make(shader, "Flames", fire, FxQueue.Flames, depthPull: 9f);
            Flames.SetFloat("_FireIntensity", 3.2f);
            Flames.SetFloat("_FireOpacity", 0.5f);
            Flames.SetFloat("_SmokeShadow", 0.25f);
            Flames.SetFloat("_SmokeLight", 0.75f);

            // Napalm and thermobaric fuel: redder, denser, with heavy black smoke.
            Napalm = Make(shader, "Napalm", fire, FxQueue.Flames, depthPull: 9f);
            Napalm.SetColor("_FireDeep", new Color(0.6f, 0.04f, 0.0f));
            Napalm.SetColor("_FireMid", new Color(1f, 0.3f, 0.02f));
            Napalm.SetColor("_FireHot", new Color(1f, 0.72f, 0.3f));
            Napalm.SetFloat("_FireIntensity", 3.6f);
            Napalm.SetFloat("_HeatScale", 1.15f);
            Napalm.SetFloat("_FireOpacity", 0.6f);
            Napalm.SetFloat("_Density", 1.35f);
            Napalm.SetFloat("_SmokeShadow", 0.18f);
            Napalm.SetFloat("_SmokeLight", 0.55f);

            // A flamethrower's rolling balls of burning fuel: the blast sheet's fire, napalm-red and
            // hot for longer, rolling up into black smoke.
            FlameBall = Make(shader, "FlameBall", blast, FxQueue.Flames, depthPull: 9f);
            FlameBall.SetColor("_FireDeep", new Color(0.6f, 0.05f, 0f));
            FlameBall.SetColor("_FireMid", new Color(1f, 0.34f, 0.03f));
            FlameBall.SetColor("_FireHot", new Color(1f, 0.8f, 0.4f));
            FlameBall.SetFloat("_FireIntensity", 3.8f);
            FlameBall.SetFloat("_HeatScale", 1.6f);
            FlameBall.SetFloat("_FireOpacity", 0.6f);
            FlameBall.SetFloat("_Density", 1.25f);
            FlameBall.SetFloat("_SmokeShadow", 0.16f);
            FlameBall.SetFloat("_SmokeLight", 0.5f);

            // Explosion fireballs rolling up into smoke.
            Blast = Make(shader, "Blast", blast, FxQueue.Fireball, depthPull: 10f);
            Blast.SetFloat("_FireIntensity", 3.8f);
            Blast.SetFloat("_HeatScale", 1.1f);
            Blast.SetFloat("_FireOpacity", 0.55f);
            Blast.SetFloat("_SmokeShadow", 0.3f);
            Blast.SetFloat("_SmokeLight", 1f);

            // The biggest blasts (strikes, ammunition, fuel) burn hotter and whiter.
            HotBlast = Make(shader, "HotBlast", blast, FxQueue.Fireball, depthPull: 12f);
            HotBlast.SetColor("_FireMid", new Color(1f, 0.46f, 0.1f));
            HotBlast.SetColor("_FireHot", new Color(1f, 0.93f, 0.75f));
            HotBlast.SetFloat("_FireIntensity", 4.6f);
            HotBlast.SetFloat("_HeatScale", 1.3f);
            HotBlast.SetFloat("_FireOpacity", 0.6f);
            HotBlast.SetFloat("_SmokeShadow", 0.3f);
            HotBlast.SetFloat("_SmokeLight", 1f);

            // Billowing smoke; its darkness comes from the particle colour.
            Smoke = Make(shader, "Smoke", smoke, FxQueue.Smoke, depthPull: 8f);
            Smoke.SetFloat("_FireIntensity", 0f);
            Smoke.SetFloat("_SmokeShadow", 0.42f);
            Smoke.SetFloat("_SmokeLight", 1.2f);
            Smoke.SetFloat("_GroundFade", 1.6f);

            // Dust and earth thrown up by a blast: softer shading, thinner.
            Dust = Make(shader, "Dust", smoke, FxQueue.Dust, depthPull: 6f);
            Dust.SetFloat("_FireIntensity", 0f);
            Dust.SetFloat("_SmokeShadow", 0.62f);
            Dust.SetFloat("_SmokeLight", 1.12f);
            Dust.SetFloat("_Density", 0.85f);
            Dust.SetFloat("_GroundFade", 1.2f);

            // A smoke screen: thick, pale and softly lit, drawn over whatever burns inside it.
            ScreenSmoke = Make(shader, "ScreenSmoke", smoke, FxQueue.Screen, depthPull: 8f);
            ScreenSmoke.SetFloat("_FireIntensity", 0f);
            ScreenSmoke.SetFloat("_SmokeShadow", 0.6f);
            ScreenSmoke.SetFloat("_SmokeLight", 1.25f);
            ScreenSmoke.SetFloat("_Density", 1.2f);
            ScreenSmoke.SetFloat("_GroundFade", 1.6f);

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
        public Material FlameBall { get; }
        public Material Blast { get; }
        public Material HotBlast { get; }
        public Material Smoke { get; }
        public Material Dust { get; }
        public Material ScreenSmoke { get; }
        public Material[] Scorch { get; }

        private readonly Dictionary<Material, Material> _front = new();

        /// <summary>The same material drawn after the smoke screens (for blasts in front of them).</summary>
        public Material InFront(Material material)
        {
            if (_front.TryGetValue(material, out var front) && front != null) return front;
            front = new Material(material) { name = material.name + " (front)", hideFlags = HideFlags.DontSave };
            front.renderQueue = material.renderQueue + FxQueue.FrontOffset;
            return _front[material] = front;
        }

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

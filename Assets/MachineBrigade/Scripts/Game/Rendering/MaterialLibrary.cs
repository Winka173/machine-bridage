using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Every material the match uses, created once from the three project shaders
    /// (kept in Resources/Shaders so builds include them) and destroyed with the match.
    /// </summary>
    public sealed class MaterialLibrary : IDisposable
    {
        private readonly List<Material> _owned = new();

        public MaterialLibrary()
        {
            var voxel = Find("MachineBrigade/VoxelLit");
            var unlit = Find("MachineBrigade/Unlit");
            var particle = Find("MachineBrigade/Particle");

            Voxel = Make(voxel, "Voxel");
            Ground = Make(voxel, "Ground");
            Wreck = Make(voxel, "Wreck");
            Wreck.SetColor("_Tint", new Color(0.2f, 0.18f, 0.17f));

            SelectionRing = Unlit(unlit, "Selection", new Color(0.45f, 1.4f, 0.5f));
            MoveMarker = Unlit(unlit, "MoveMarker", new Color(0.6f, 2f, 0.7f));
            AttackMarker = Unlit(unlit, "AttackMarker", new Color(2f, 0.5f, 0.4f));
            BarBack = Unlit(unlit, "BarBack", new Color(0.06f, 0.06f, 0.06f));
            BarAlly = Unlit(unlit, "BarAlly", TeamColors.Ui(0));
            BarEnemy = Unlit(unlit, "BarEnemy", TeamColors.Ui(1));
            Tracer = Unlit(unlit, "Tracer", new Color(7f, 5f, 1.8f)); // HDR so bloom makes it glow

            Fire = Particle(particle, "Fire", additive: true, intensity: 2.6f, shape: 0f, softness: 1.4f);
            Sparks = Particle(particle, "Sparks", additive: true, intensity: 4f, shape: 0f, softness: 0.6f);
            Smoke = Particle(particle, "Smoke", additive: false, intensity: 1f, shape: 0f, softness: 1.2f);
            Shockwave = Particle(particle, "Shockwave", additive: true, intensity: 1.6f, shape: 1f, softness: 1f);
            Scorch = Particle(particle, "Scorch", additive: false, intensity: 1f, shape: 0f, softness: 0.8f);
        }

        public Material Voxel { get; }
        public Material Ground { get; }
        public Material Wreck { get; }
        public Material SelectionRing { get; }
        public Material MoveMarker { get; }
        public Material AttackMarker { get; }
        public Material BarBack { get; }
        public Material BarAlly { get; }
        public Material BarEnemy { get; }
        public Material Tracer { get; }
        public Material Fire { get; }
        public Material Sparks { get; }
        public Material Smoke { get; }
        public Material Shockwave { get; }
        public Material Scorch { get; }

        public void Dispose()
        {
            foreach (var m in _owned)
                if (m != null) Object.Destroy(m);
            _owned.Clear();
        }

        private static Shader Find(string name)
        {
            var shader = Shader.Find(name);
            if (shader == null) throw new InvalidOperationException($"Shader '{name}' is missing; it must live in Resources/Shaders.");
            return shader;
        }

        private Material Make(Shader shader, string name)
        {
            var m = new Material(shader) { name = name };
            _owned.Add(m);
            return m;
        }

        private Material Unlit(Shader shader, string name, Color color)
        {
            var m = Make(shader, name);
            m.SetColor("_Color", color);
            return m;
        }

        private Material Particle(Shader shader, string name, bool additive, float intensity, float shape, float softness)
        {
            var m = Make(shader, name);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", additive ? (float)BlendMode.One : (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_Intensity", intensity);
            m.SetFloat("_Shape", shape);
            m.SetFloat("_Softness", softness);
            m.renderQueue = additive ? 3010 : 3000;
            return m;
        }
    }
}

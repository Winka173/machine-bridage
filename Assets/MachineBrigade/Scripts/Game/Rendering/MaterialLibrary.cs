using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Every material the match uses. Model materials are looked up by the names the Blender kit
    /// gives them (Team, Armor, Steel, ...) and rebuilt on the project's Lit shader with the kit's
    /// colour, metallic, roughness and emission, so the GLB files only need to carry names.
    /// </summary>
    public sealed class MaterialLibrary : IDisposable
    {
        /// <summary>Kit surface definitions: sRGB base colour, metallic, roughness, emission strength.</summary>
        private static readonly Dictionary<string, (string color, float metallic, float roughness, float emission)> Kit = new()
        {
            ["Armor"] = ("#59605f", 0.55f, 0.46f, 0f),
            ["Steel"] = ("#c4c8c4", 0.95f, 0.28f, 0f),
            ["Undercarriage"] = ("#23282a", 0.35f, 0.72f, 0f),
            ["Glass"] = ("#12303a", 0.2f, 0.06f, 0.35f),
            ["Alloy"] = ("#ff9b36", 0.1f, 0.35f, 2.4f),
            ["Lamp"] = ("#ffe7b8", 0f, 0.3f, 3.2f),
            ["Concrete"] = ("#8d8a7e", 0f, 0.9f, 0f),
            ["Hazard"] = ("#e2b64a", 0.15f, 0.5f, 0f),
            ["Rock"] = ("#a29d92", 0f, 0.92f, 0f),
            ["Bark"] = ("#6e5a44", 0f, 0.9f, 0f),
            ["Foliage"] = ("#56733f", 0f, 0.85f, 0f),
            ["FoliageLight"] = ("#86995a", 0f, 0.8f, 0f),
            ["Crate"] = ("#737a5c", 0.2f, 0.6f, 0f),
            ["Rubber"] = ("#2a2d2f", 0f, 0.88f, 0f),
            ["Plaster"] = ("#ddd2b8", 0f, 0.92f, 0f),
            ["Roof"] = ("#b25a40", 0f, 0.78f, 0f),
            ["Wood"] = ("#86633f", 0f, 0.86f, 0f),
            ["BarrelRed"] = ("#c2402a", 0.35f, 0.48f, 0f),
            ["Fuel"] = ("#e4e2d8", 0.45f, 0.42f, 0f),
            ["Canvas"] = ("#8a8764", 0f, 0.9f, 0f),
        };

        private readonly List<Material> _owned = new();
        private readonly Dictionary<string, Material> _surfaces = new();
        private readonly Dictionary<(string, int), Material> _team = new();
        private readonly Shader _lit;

        public MaterialLibrary()
        {
            _lit = Find("MachineBrigade/Lit");
            var unlit = Find("MachineBrigade/Unlit");
            var particle = Find("MachineBrigade/Particle");

            Ground = Surface("Ground", Color.white, 0f, 0.95f, 0f);
            Fallback = Surface("Fallback", new Color(0.6f, 0.6f, 0.6f), 0f, 0.8f, 0f);
            foreach (var entry in Kit)
                _surfaces[entry.Key] = Surface(entry.Key, Hex(entry.Value.color), entry.Value.metallic, entry.Value.roughness,
                    entry.Value.emission);
            foreach (var name in new[] { "Foliage", "FoliageLight" }) _surfaces[name].SetFloat("_Wind", 1f);

            SelectionRing = Unlit(unlit, "Selection", new Color(0.55f, 1.6f, 1.1f));
            MoveMarker = Unlit(unlit, "MoveMarker", new Color(0.7f, 2f, 1.3f));
            BarBack = Unlit(unlit, "BarBack", new Color(0.04f, 0.06f, 0.06f));
            BarAlly = Unlit(unlit, "BarAlly", TeamColors.Ui(0));
            BarEnemy = Unlit(unlit, "BarEnemy", TeamColors.Ui(1));
            Tracer = Unlit(unlit, "Tracer", new Color(7f, 5f, 1.8f)); // HDR so bloom makes it glow

            Fire = Particle(particle, "Fire", additive: true, intensity: 2.6f, shape: 0f, softness: 1.4f);
            Sparks = Particle(particle, "Sparks", additive: true, intensity: 4f, shape: 0f, softness: 0.6f);
            Smoke = Particle(particle, "Smoke", additive: false, intensity: 1f, shape: 0f, softness: 1.2f);
            Shockwave = Particle(particle, "Shockwave", additive: true, intensity: 1.6f, shape: 1f, softness: 1f);
            Scorch = Particle(particle, "Scorch", additive: false, intensity: 1f, shape: 0f, softness: 0.8f);
        }

        public Material Ground { get; }
        public Material Fallback { get; }
        public Material SelectionRing { get; }
        public Material MoveMarker { get; }
        public Material BarBack { get; }
        public Material BarAlly { get; }
        public Material BarEnemy { get; }
        public Material Tracer { get; }
        public Material Fire { get; }
        public Material Sparks { get; }
        public Material Smoke { get; }
        public Material Shockwave { get; }
        public Material Scorch { get; }

        /// <summary>
        /// The runtime material for a model material name. Team and TeamGlow are painted in the
        /// army's colour; unknown names fall back to neutral grey rather than failing.
        /// </summary>
        public Material ForModel(string materialName, int team)
        {
            var name = BaseName(materialName);
            if (name == "Team" || name == "TeamGlow") return TeamMaterial(name, team);
            return _surfaces.TryGetValue(name, out var material) ? material : Fallback;
        }

        public void Dispose()
        {
            foreach (var m in _owned)
                if (m != null) Object.Destroy(m);
            _owned.Clear();
            _surfaces.Clear();
            _team.Clear();
        }

        private Material TeamMaterial(string name, int team)
        {
            if (_team.TryGetValue((name, team), out var cached)) return cached;
            var colour = (Color)TeamColors.Main(team);
            var material = name == "TeamGlow"
                ? Surface($"TeamGlow{team}", colour, 0f, 0.3f, 0f, colour * 3f)
                : Surface($"Team{team}", colour, 0.25f, 0.42f, 0f);
            _team[(name, team)] = material;
            return material;
        }

        /// <summary>Blender/glTF may add ".001" or " (Instance)" suffixes; the kit name is the first word.</summary>
        private static string BaseName(string name)
        {
            if (string.IsNullOrEmpty(name)) return string.Empty;
            var end = name.IndexOfAny(new[] { '.', ' ', '(' });
            return end > 0 ? name.Substring(0, end) : name;
        }

        private Material Surface(string name, Color color, float metallic, float roughness, float emission,
            Color? emissionColor = null)
        {
            var m = new Material(_lit) { name = name, enableInstancing = true };
            m.SetColor("_BaseColor", color);
            m.SetFloat("_Metallic", metallic);
            m.SetFloat("_Roughness", roughness);
            m.SetColor("_EmissionColor", emissionColor ?? (emission > 0f ? color * emission : Color.black));
            _owned.Add(m);
            return m;
        }

        private static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.magenta;

        private static Shader Find(string name)
        {
            var shader = Shader.Find(name);
            if (shader == null) throw new InvalidOperationException($"Shader '{name}' is missing; it must live in Resources/Shaders.");
            return shader;
        }

        private Material Unlit(Shader shader, string name, Color color)
        {
            var m = new Material(shader) { name = name };
            m.SetColor("_Color", color);
            _owned.Add(m);
            return m;
        }

        private Material Particle(Shader shader, string name, bool additive, float intensity, float shape, float softness)
        {
            var m = new Material(shader) { name = name };
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", additive ? (float)BlendMode.One : (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_Intensity", intensity);
            m.SetFloat("_Shape", shape);
            m.SetFloat("_Softness", softness);
            m.renderQueue = additive ? 3010 : 3000;
            _owned.Add(m);
            return m;
        }
    }
}

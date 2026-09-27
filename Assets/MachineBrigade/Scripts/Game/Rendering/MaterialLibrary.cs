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
            ["Steel"] = ("#c4c8c4", 0.85f, 0.42f, 0f),
            ["Undercarriage"] = ("#23282a", 0.35f, 0.72f, 0f),
            ["Glass"] = ("#12303a", 0.1f, 0.3f, 0.35f),
            ["Alloy"] = ("#ff9b36", 0.1f, 0.35f, 2.4f),
            ["Lamp"] = ("#ffe7b8", 0f, 0.3f, 3.2f),
            ["Concrete"] = ("#8d8a7e", 0f, 0.9f, 0f),
            ["Hazard"] = ("#e2b64a", 0.15f, 0.5f, 0f),
            ["Rock"] = ("#8d958c", 0f, 0.92f, 0f),
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
            ["Snow"] = ("#e8eef0", 0f, 0.85f, 0f),
            ["Dirt"] = ("#7a6448", 0f, 0.95f, 0f),
            ["Sandbag"] = ("#a8956a", 0f, 0.95f, 0f),
            ["Grass"] = ("#5f7a45", 0f, 0.9f, 0f),
            // Town kit.
            ["PlasterWhite"] = ("#ece8dc", 0f, 0.92f, 0f),
            ["PlasterBlue"] = ("#a9bfc7", 0f, 0.92f, 0f),
            ["PlasterOchre"] = ("#dfb56c", 0f, 0.92f, 0f),
            ["Brick"] = ("#a8553d", 0f, 0.9f, 0f),
            ["RoofSlate"] = ("#5b636c", 0f, 0.74f, 0f),
            ["RoofGreen"] = ("#5e8a72", 0.2f, 0.62f, 0f),
            ["MetalSheet"] = ("#a9b0b1", 0.55f, 0.5f, 0f),
            ["WoodRed"] = ("#9c3f2f", 0f, 0.85f, 0f),
            ["Charred"] = ("#302b28", 0f, 0.95f, 0f),
            ["FoliageDark"] = ("#3e5b35", 0f, 0.85f, 0f),
            ["BarkWhite"] = ("#e4dfd2", 0f, 0.85f, 0f),
            // Civilian paint; models use CarRed and the map swaps in the others.
            ["CarRed"] = ("#c8382c", 0.35f, 0.38f, 0f),
            ["CarBlue"] = ("#3b6a9e", 0.35f, 0.38f, 0f),
            ["CarWhite"] = ("#e6e6e0", 0.35f, 0.38f, 0f),
            ["CarYellow"] = ("#e0b53a", 0.35f, 0.38f, 0f),
            ["CarGreen"] = ("#4f7a54", 0.35f, 0.38f, 0f),
            ["CarGrey"] = ("#6c7176", 0.4f, 0.4f, 0f),
            // Desert and snow maps.
            ["Adobe"] = ("#d8ad7e", 0f, 0.95f, 0f),
            ["AdobeTrim"] = ("#a9774f", 0f, 0.93f, 0f),
            ["Sandstone"] = ("#d99d66", 0f, 0.92f, 0f),
            ["SandstoneDark"] = ("#a8603b", 0f, 0.93f, 0f),
            ["SnowCap"] = ("#f4f8fb", 0f, 0.78f, 0f),
            ["LogWood"] = ("#7a5334", 0f, 0.88f, 0f),
            ["Rust"] = ("#8f4e2c", 0.35f, 0.74f, 0f),
            ["Pipe"] = ("#9ba49c", 0.55f, 0.45f, 0f),
            // Harbour map; containers use ContainerRed and the map swaps in the others.
            ["ContainerRed"] = ("#b8432f", 0.3f, 0.55f, 0f),
            ["ContainerBlue"] = ("#2f6496", 0.3f, 0.55f, 0f),
            ["ContainerGreen"] = ("#3f7a4e", 0.3f, 0.55f, 0f),
            ["ContainerOrange"] = ("#d9782c", 0.3f, 0.55f, 0f),
            ["ContainerGrey"] = ("#8a9095", 0.3f, 0.55f, 0f),
            ["Corrugated"] = ("#8a9496", 0.5f, 0.58f, 0f),
            ["CraneYellow"] = ("#f5b41e", 0.25f, 0.5f, 0f),
            ["Asphalt"] = ("#4a4a48", 0f, 0.95f, 0f),
            ["SafetyStripe"] = ("#f7d21c", 0.05f, 0.5f, 0f),
            ["RailBrown"] = ("#7a3f2c", 0.3f, 0.6f, 0f),
            // Premium trims (the Titan).
            ["Gilded"] = ("#f5c75a", 0.9f, 0.28f, 0f),
            // Elite enemy units: dark armour and red sensor glow.
            ["EliteBlack"] = ("#1c1e24", 0.35f, 0.5f, 0f),
            ["Medical"] = ("#e9ece6", 0.1f, 0.4f, 0f),
            // Volcanic, jungle, airbase and city maps.
            ["LavaGlow"] = ("#ff4a12", 0f, 0.45f, 2.2f),
            ["SignalGreen"] = ("#3cf08c", 0f, 0.3f, 2.4f),
            ["Obsidian"] = ("#1e1c26", 0.3f, 0.16f, 0f),
            ["EliteGlow"] = ("#ff2a1f", 0f, 0.3f, 2.4f),
        };

        private readonly List<Material> _owned = new();
        private readonly Dictionary<string, Material> _surfaces = new();
        private readonly Dictionary<(string, int), Material> _team = new();
        private readonly Shader _lit;
        private readonly Texture2D _noise;

        public MaterialLibrary()
        {
            _lit = Find("MachineBrigade/Lit");
            var unlit = Find("MachineBrigade/Unlit");
            var particle = Find("MachineBrigade/Particle");
            _noise = NoiseTexture(64, 8);
            Shader.SetGlobalTexture("_MbNoise", _noise);

            Ground = Surface("Ground", Color.white, 0f, 0.95f, 0f);
            Skirt = Surface("Skirt", Hex("#424634"), 0f, 0.95f, 0f);
            Pebble = Surface("Pebble", Hex("#626957"), 0f, 0.9f, 0f);
            GrassTuft = Surface("GrassTuft", Hex("#515f40"), 0f, 0.85f, 0f);
            GrassTuft.SetFloat("_Wind", 0.6f);
            Water = Surface("Water", Hex("#2f6f78"), 0.1f, 0.08f, 0f);
            OuterGround = Surface("OuterGround", Color.white, 0f, 0.95f, 0f);
            Terrain = Surface("Terrain", Color.white, 0f, 0.92f, 0f);
            Fallback = Surface("Fallback", new Color(0.6f, 0.6f, 0.6f), 0f, 0.8f, 0f);
            foreach (var entry in Kit)
                _surfaces[entry.Key] = Surface(entry.Key, Hex(entry.Value.color), entry.Value.metallic, entry.Value.roughness,
                    entry.Value.emission);
            foreach (var name in new[] { "Foliage", "FoliageLight", "FoliageDark" }) _surfaces[name].SetFloat("_Wind", 1f);
            CarPaints = new[] { _surfaces["CarRed"], _surfaces["CarBlue"], _surfaces["CarWhite"], _surfaces["CarYellow"],
                _surfaces["CarGreen"], _surfaces["CarGrey"] };
            ContainerPaints = new[] { _surfaces["ContainerRed"], _surfaces["ContainerBlue"], _surfaces["ContainerGreen"],
                _surfaces["ContainerOrange"], _surfaces["ContainerGrey"] };

            SelectionRing = Unlit(unlit, "Selection", new Color(0.55f, 1.6f, 1.1f));
            MoveMarker = Unlit(unlit, "MoveMarker", new Color(0.7f, 2f, 1.3f));
            BarBack = Unlit(unlit, "BarBack", new Color(0.04f, 0.06f, 0.06f));
            BarAlly = Unlit(unlit, "BarAlly", TeamColors.Ui(0));
            BarTrail = Unlit(unlit, "BarTrail", new Color(1f, 0.86f, 0.45f));
            BarNeutral = Unlit(unlit, "BarNeutral", new Color(0.92f, 0.9f, 0.82f));
            BarEnemy = Unlit(unlit, "BarEnemy", TeamColors.Ui(1));
            BarElite = Unlit(unlit, "BarElite", new Color(1f, 0.78f, 0.25f));
            AmmoReload = Unlit(unlit, "AmmoReload", new Color(1f, 0.7f, 0.22f));
            AmmoEmpty = Unlit(unlit, "AmmoEmpty", new Color(1f, 0.26f, 0.18f));
            AmmoSpent = Unlit(unlit, "AmmoSpent", new Color(0.22f, 0.24f, 0.24f));
            RepairMark = Unlit(unlit, "RepairMark", new Color(0.5f, 1.45f, 0.62f));
            NavRed = Unlit(unlit, "NavRed", new Color(3.2f, 0.25f, 0.18f));
            NavGreen = Unlit(unlit, "NavGreen", new Color(0.25f, 3f, 0.6f));
            NavWhite = Unlit(unlit, "NavWhite", new Color(4f, 4f, 3.8f));
            Tracer = Unlit(unlit, "Tracer", new Color(7f, 5f, 1.8f)); // HDR so bloom makes it glow
            StrikeWarning = Unlit(unlit, "StrikeWarning", new Color(2.6f, 0.35f, 0.2f));
            Objective = Unlit(unlit, "Objective", new Color(0.9f, 0.9f, 0.85f));
            GroundMark = new Material(Find("MachineBrigade/GroundMark")) { name = "GroundMark", enableInstancing = true };
            _owned.Add(GroundMark);

            Fire = Particle(particle, "Fire", additive: true, intensity: 2f, shape: 3f, softness: 1.4f, depthPull: 9f);
            Sparks = Particle(particle, "Sparks", additive: true, intensity: 4f, shape: 0f, softness: 0.6f, depthPull: 3f);
            Smoke = Particle(particle, "Smoke", additive: false, intensity: 1f, shape: 4f, softness: 1.2f, depthPull: 8f);
            SoftSmoke = Particle(particle, "SoftSmoke", additive: false, intensity: 1f, shape: 0f, softness: 1.6f, depthPull: 4f);
            Shockwave = Particle(particle, "Shockwave", additive: true, intensity: 1.6f, shape: 1f, softness: 1f);
            // Light cast on the ground by blasts: a wide soft pool, drawn over the ground and under the smoke.
            Glow = Particle(particle, "Glow", additive: true, intensity: 1.35f, shape: 0f, softness: 1.8f);
            Glow.renderQueue = 2960;
            // The first instant of a blast: a round white-hot flash (a flame-shaped one read as a ghostly streak).
            Flash = Particle(particle, "Flash", additive: true, intensity: 2.6f, shape: 0f, softness: 1.3f, depthPull: 6f);
            Scorch = Particle(particle, "Scorch", additive: false, intensity: 1f, shape: 0f, softness: 0.8f);
            // Track marks: soft-edged dark oblongs on the ground, under every effect.
            Tread = Particle(particle, "Tread", additive: false, intensity: 1f, shape: 2f, softness: 0.55f);
            Tread.renderQueue = 2951;
            // Scorch marks lie on the ground: under strike warnings, rings, smoke and dust.
            Scorch.renderQueue = 2950;
            Scorch.enableInstancing = true;
            Rain = Particle(particle, "Rain", additive: false, intensity: 1.1f, shape: 0f, softness: 0.4f);
            Splash = Particle(particle, "Splash", additive: false, intensity: 1f, shape: 1f, softness: 0.8f);
        }

        /// <summary>Body colours for civilian cars and trucks; index 0 is the models' own CarRed.</summary>
        public Material[] CarPaints { get; }

        /// <summary>Shipping container colours; index 0 is the models' own ContainerRed.</summary>
        public Material[] ContainerPaints { get; }

        public Material Ground { get; }
        public Material Skirt { get; }
        public Material Pebble { get; }
        public Material GrassTuft { get; }
        public Material Water { get; }
        public Material OuterGround { get; }

        /// <summary>The mountain range; its colours come from a palette texture indexed by UV.</summary>
        public Material Terrain { get; }
        public Material Fallback { get; }
        public Material SelectionRing { get; }
        public Material MoveMarker { get; }

        /// <summary>Red telegraph circles and lines for incoming strikes.</summary>
        public Material StrikeWarning { get; }

        /// <summary>Ground markings (objectives, telegraphs, selection); see <see cref="Rendering.GroundMark"/>.</summary>
        public Material GroundMark { get; }

        /// <summary>Capture point flags; tinted per owner with a property block.</summary>
        public Material Objective { get; }
        public Material BarBack { get; }
        public Material BarAlly { get; }

        /// <summary>Track marks on the ground (see TrackMarks).</summary>
        public Material Tread { get; }

        /// <summary>Health just lost, shown behind the bar before it catches up.</summary>
        public Material BarTrail { get; }

        /// <summary>A neutral watchtower's health.</summary>
        public Material BarNeutral { get; }
        public Material BarEnemy { get; }

        /// <summary>Gold health bar of elite enemy units.</summary>
        public Material BarElite { get; }

        /// <summary>The overhead ammunition gauge: rounds coming back (amber), empty and waiting (red), spent (grey).</summary>
        public Material AmmoReload { get; }
        public Material AmmoEmpty { get; }
        public Material AmmoSpent { get; }

        /// <summary>The green wrench over something being repaired (a sapper at a tower).</summary>
        public Material RepairMark { get; }

        /// <summary>Aircraft navigation lights: red on the left wingtip, green on the right, white strobes.</summary>
        public Material NavRed { get; }
        public Material NavGreen { get; }
        public Material NavWhite { get; }
        public Material Tracer { get; }
        public Material Fire { get; }
        public Material Sparks { get; }

        /// <summary>Plain soft puffs for smoke trails, which read as smooth ribbons.</summary>
        public Material SoftSmoke { get; }

        /// <summary>Falling rain streaks (stretched billboards).</summary>
        public Material Rain { get; }

        /// <summary>Rings where raindrops hit the ground.</summary>
        public Material Splash { get; }
        public Material Smoke { get; }
        public Material Shockwave { get; }

        /// <summary>Soft additive pool of light on the ground, standing in for a real point light.</summary>
        public Material Glow { get; }

        /// <summary>Round white-hot flash at the heart of a blast.</summary>
        public Material Flash { get; }
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

        /// <summary>
        /// Paints the player's army (team 0): base colour, pattern (0 plain, 1 blotches, 2
        /// stripes, 3 digital) with its two other colours and scale, and the finish.
        /// </summary>
        public void ApplySkin(Color baseColour, Color second, Color third, int pattern, float scale, float metallic, float roughness)
        {
            var team = TeamMaterial("Team", 0);
            team.SetColor("_BaseColor", baseColour);
            team.SetColor("_CamoColorB", second);
            team.SetColor("_CamoColorC", third);
            team.SetFloat("_CamoMode", pattern);
            team.SetFloat("_CamoScale", scale);
            team.SetFloat("_Metallic", metallic);
            team.SetFloat("_Roughness", roughness);
        }

        public void Dispose()
        {
            foreach (var m in _owned)
            {
                if (m == null) continue;
                if (Application.isPlaying) Object.Destroy(m);
                else Object.DestroyImmediate(m);
            }
            _owned.Clear();
            if (_noise != null)
            {
                if (Application.isPlaying) Object.Destroy(_noise);
                else Object.DestroyImmediate(_noise);
            }
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
            var m = new Material(_lit) { name = name, enableInstancing = !Match.DebugFlags.Has("-mb-no-instancing") };
            m.SetColor("_BaseColor", color);
            m.SetFloat("_Metallic", metallic);
            m.SetFloat("_Roughness", roughness);
            m.SetColor("_EmissionColor", emissionColor ?? (emission > 0f ? color * emission : Color.black));
            _owned.Add(m);
            return m;
        }

        /// <summary>
        /// Tileable two-octave value noise (the particle shader's former per-pixel Fbm), with
        /// <paramref name="cells"/> lattice cells across the texture for the first octave.
        /// </summary>
        private static Texture2D NoiseTexture(int size, int cells)
        {
            var random = new System.Random(4242);
            float[] Lattice(int n)
            {
                var values = new float[n * n];
                for (var i = 0; i < values.Length; i++) values[i] = (float)random.NextDouble();
                return values;
            }

            float Sample(float[] lattice, int n, float x, float y)
            {
                var ix = Mathf.FloorToInt(x);
                var iy = Mathf.FloorToInt(y);
                var fx = x - ix;
                var fy = y - iy;
                fx = fx * fx * (3f - 2f * fx);
                fy = fy * fy * (3f - 2f * fy);
                float At(int cx, int cy) => lattice[(cy % n + n) % n * n + (cx % n + n) % n];
                return Mathf.Lerp(Mathf.Lerp(At(ix, iy), At(ix + 1, iy), fx), Mathf.Lerp(At(ix, iy + 1), At(ix + 1, iy + 1), fx), fy);
            }

            var first = Lattice(cells);
            var second = Lattice(cells * 2);
            var pixels = new Color32[size * size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var u = (x + 0.5f) / size * cells;
                var v = (y + 0.5f) / size * cells;
                var n = Sample(first, cells, u, v) * 0.6f + Sample(second, cells * 2, u * 2f, v * 2f) * 0.4f;
                var b = (byte)Mathf.Clamp(Mathf.RoundToInt(n * 255f), 0, 255);
                pixels[y * size + x] = new Color32(b, b, b, 255);
            }
            var texture = new Texture2D(size, size, TextureFormat.RGBA32, false, true)
            {
                name = "Particle Noise",
                wrapMode = TextureWrapMode.Repeat,
                filterMode = FilterMode.Bilinear,
            };
            texture.SetPixels32(pixels);
            texture.Apply(false, true);
            return texture;
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
            // Instanced: tracers and health bars are many copies of one mesh.
            var m = new Material(shader) { name = name, enableInstancing = true };
            m.SetColor("_Color", color);
            _owned.Add(m);
            return m;
        }

        private Material Particle(Shader shader, string name, bool additive, float intensity, float shape, float softness,
            float depthPull = 0f)
        {
            var m = new Material(shader) { name = name };
            m.SetFloat("_DepthPull", depthPull);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", additive ? (float)BlendMode.One : (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_Intensity", intensity);
            m.SetFloat("_Shape", shape);
            m.SetFloat("_Softness", softness);
            m.renderQueue = additive ? 3010 : Effects.FxQueue.Haze;
            _owned.Add(m);
            return m;
        }
    }
}

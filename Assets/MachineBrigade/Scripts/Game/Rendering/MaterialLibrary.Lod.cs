using System.Collections.Generic;
using UnityEngine;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The far detail level's surfaces. A vehicle's simplified model is one mesh per moving part
    /// drawn with one material per army: each vertex names its kit surface by an index into a
    /// small palette texture (colour, metallic, roughness, emission of every kit material), so a
    /// tank that takes about twenty draws up close takes four or five far away and still wears
    /// exactly the same colours. The army's own paint (and its camouflage) comes from the
    /// material, as on the full model.
    /// </summary>
    public sealed partial class MaterialLibrary
    {
        /// <summary>Palette columns: every kit surface, the two army entries and the fallback grey.</summary>
        public const int PaletteSize = 128;

        private const int TeamPaint = 0;
        private const int TeamGlowEntry = 1;
        private const int FallbackEntry = 2;
        private static readonly int PaletteId = Shader.PropertyToID("_MbPalette");
        private static readonly int VertexSurfaceId = Shader.PropertyToID("_VertexSurface");

        private Texture2D _palette;
        private readonly Dictionary<string, int> _paletteColumns = new();
        private readonly Dictionary<int, Material> _lodSurfaces = new();

        /// <summary>
        /// The palette: row 0 holds (base colour, metallic) and row 1 (emission, roughness), linear.
        /// An army entry has a metallic of -1 (paint) or -2 (glow) and takes its colour from the
        /// material. Built on first use, from the kit materials as they are then (a map's grass tint included).
        /// </summary>
        public Texture2D Palette
        {
            get
            {
                if (_palette == null) BuildPalette();
                return _palette;
            }
        }

        /// <summary>The palette column (texture U) of a model material name, for a far-detail vertex.</summary>
        public float PaletteU(string materialName)
        {
            if (_palette == null) BuildPalette();
            var name = BaseName(materialName);
            var column = name == "Team" ? TeamPaint : name == "TeamGlow" ? TeamGlowEntry
                : _paletteColumns.TryGetValue(name, out var c) ? c : FallbackEntry;
            return (column + 0.5f) / PaletteSize;
        }

        /// <summary>Whether a model material glows (lamps, energy coils, sensor eyes): its far-detail vertices keep the glow.</summary>
        public bool Emissive(string materialName)
        {
            var name = BaseName(materialName);
            return name == "TeamGlow" || (Kit.TryGetValue(name, out var kit) && kit.emission > 0f);
        }

        /// <summary>The far-detail material of an army: its paint, camouflage and finish, the palette for the rest.</summary>
        public Material LodSurface(int team)
        {
            if (_lodSurfaces.TryGetValue(team, out var cached)) return cached;
            var material = new Material(_lit) { name = $"LodSurface{team}", enableInstancing = !Match.DebugFlags.Has("-mb-no-instancing") };
            material.SetFloat(VertexSurfaceId, 1f);
            material.SetTexture(PaletteId, Palette);
            _owned.Add(material);
            _lodSurfaces[team] = material;
            SyncLodSurface(team);
            return material;
        }

        /// <summary>Copies the army's paint (colour, camouflage, finish) and its glow onto its far-detail material.</summary>
        private void SyncLodSurface(int team)
        {
            if (!_lodSurfaces.TryGetValue(team, out var material)) return;
            var paint = TeamMaterial("Team", team);
            var glow = TeamMaterial("TeamGlow", team);
            foreach (var name in new[] { "_BaseColor", "_CamoColorB", "_CamoColorC" }) material.SetColor(name, paint.GetColor(name));
            foreach (var name in new[] { "_CamoMode", "_CamoScale", "_Metallic", "_Roughness" }) material.SetFloat(name, paint.GetFloat(name));
            material.SetColor("_EmissionColor", glow.GetColor("_EmissionColor"));
        }

        private void BuildPalette()
        {
            var format = SystemInfo.SupportsTextureFormat(TextureFormat.RGBAHalf) ? TextureFormat.RGBAHalf : TextureFormat.RGBAFloat;
            _palette = new Texture2D(PaletteSize, 2, format, false, true)
            {
                name = "LOD Palette",
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp,
            };
            var pixels = new Color[PaletteSize * 2];
            void Put(int column, Color base_, float metallic, Color emission, float roughness)
            {
                pixels[column] = new Color(base_.r, base_.g, base_.b, metallic);
                pixels[PaletteSize + column] = new Color(emission.r, emission.g, emission.b, roughness);
            }
            // Material colours reach the shader converted to linear (HDR emission included); so do these.
            void PutMaterial(int column, Material m) =>
                Put(column, m.GetColor("_BaseColor").linear, m.GetFloat("_Metallic"), m.GetColor("_EmissionColor").linear, m.GetFloat("_Roughness"));
            Put(TeamPaint, Color.black, -1f, Color.black, 0.5f);
            Put(TeamGlowEntry, Color.black, -2f, Color.black, 0.3f);
            PutMaterial(FallbackEntry, Fallback);
            var next = FallbackEntry + 1;
            foreach (var name in Kit.Keys)
            {
                if (next >= PaletteSize)
                {
                    Debug.LogWarning($"[MaterialLibrary] The LOD palette is full; '{name}' draws as the fallback far away.");
                    break;
                }
                PutMaterial(next, _surfaces[name]);
                _paletteColumns[name] = next++;
            }
            _palette.SetPixels(pixels);
            _palette.Apply(false, false);
            Shader.SetGlobalTexture(PaletteId, _palette);
        }

        private void DisposeLod()
        {
            if (_palette != null)
            {
                if (Application.isPlaying) Object.Destroy(_palette);
                else Object.DestroyImmediate(_palette);
            }
            _palette = null;
            _paletteColumns.Clear();
            _lodSurfaces.Clear();
        }
    }
}

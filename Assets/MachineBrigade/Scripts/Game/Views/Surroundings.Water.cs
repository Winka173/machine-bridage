using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Play-test 13 ("biển nhìn không thực xíu nào"): the surroundings' water on the water shader. The edge sea knows its
    /// coast through a small shore-distance texture (4 m cells over the decorated square: 0 on the coast, 1 at 32 m out), so
    /// it is shallow and foaming at the beach and deep offshore; the map's own water inside the rectangle counts as sea (the
    /// sea runs on into the map without a false shore at the map's edge). Rivers and canals are calm (no swell).
    /// </summary>
    public sealed partial class Surroundings
    {
        /// <summary>Metres out from the coast at which the shore texture reads 1 (open sea).</summary>
        private const float ShoreReach = 32f;

        private Texture2D _shoreTexture;
        private Material _edgeWater;
        private Material _calmWater;

        /// <summary>The water for rivers and canals: the theme's water, calm.</summary>
        private Material CalmWater(MaterialLibrary materials)
        {
            if (_calmWater != null) return _calmWater;
            _calmWater = new Material(materials.Water) { name = "River Water" };
            _calmWater.SetFloat("_Calm", 1f);
            // A frozen river is ice: no ripples, no foam, a duller sheen.
            if (_theme.Water == ThemeWater.FrozenRiver)
            {
                _calmWater.SetFloat("_WaveStrength", 0.08f);
                _calmWater.SetFloat("_FoamAmount", 0f);
            }
            return _calmWater;
        }

        /// <summary>The edge sea's water: the theme's water reading its coast from the shore texture.</summary>
        private Material EdgeWater(MaterialLibrary materials, SimWorld world)
        {
            if (_edgeWater != null) return _edgeWater;
            _edgeWater = new Material(materials.Water) { name = "Edge Sea Water" };
            _shoreTexture = ShoreTexture(world);
            if (_shoreTexture == null) return _edgeWater;
            var size = Extent * 2f;
            _edgeWater.SetTexture("_ShoreTex", _shoreTexture);
            _edgeWater.SetVector("_ShoreRect", new Vector4(_centre.x - Extent, _centre.y - Extent, 1f / size, 1f / size));
            _edgeWater.SetFloat("_UseShoreTex", 1f);
            return _edgeWater;
        }

        /// <summary>Distance to land over the decorated square (water: the edge sea and the map's own water tiles).</summary>
        private Texture2D ShoreTexture(SimWorld world)
        {
            const float cell = SeaCell;
            var n = Mathf.CeilToInt(Extent * 2f / cell);
            if (n <= 1) return null;
            var water = new bool[n * n];
            for (var z = 0; z < n; z++)
            for (var x = 0; x < n; x++)
                water[z * n + x] = EdgeSeaAt(SeaCellCentre(x, z));
            // The map's own water (the sea and rivers drawn by MapView) is water too, so no shore is drawn at the map's edge.
            if (world != null)
                foreach (var prop in world.Props)
                {
                    var id = prop.Def.Id;
                    if (id != "river_water" && id != "river_ford") continue;
                    var x0 = Mathf.FloorToInt((prop.Position.X - prop.Width * 0.5f - 1f - (_centre.x - Extent)) / cell);
                    var x1 = Mathf.FloorToInt((prop.Position.X + prop.Width * 0.5f + 1f - (_centre.x - Extent)) / cell);
                    var z0 = Mathf.FloorToInt((prop.Position.Y - prop.Depth * 0.5f - 1f - (_centre.y - Extent)) / cell);
                    var z1 = Mathf.FloorToInt((prop.Position.Y + prop.Depth * 0.5f + 1f - (_centre.y - Extent)) / cell);
                    for (var z = Mathf.Max(0, z0); z <= Mathf.Min(n - 1, z1); z++)
                    for (var x = Mathf.Max(0, x0); x <= Mathf.Min(n - 1, x1); x++)
                        water[z * n + x] = true;
                }

            // Two-pass chamfer distance from the land (4 m straight, 5.66 m diagonal), in metres.
            var d = new float[n * n];
            for (var i = 0; i < d.Length; i++) d[i] = water[i] ? float.MaxValue : 0f;
            const float straight = cell, diagonal = cell * 1.41421f;
            for (var z = 0; z < n; z++)
            for (var x = 0; x < n; x++)
            {
                var i = z * n + x;
                var v = d[i];
                if (x > 0) v = Mathf.Min(v, d[i - 1] + straight);
                if (z > 0) v = Mathf.Min(v, d[i - n] + straight);
                if (x > 0 && z > 0) v = Mathf.Min(v, d[i - n - 1] + diagonal);
                if (x + 1 < n && z > 0) v = Mathf.Min(v, d[i - n + 1] + diagonal);
                d[i] = v;
            }
            for (var z = n - 1; z >= 0; z--)
            for (var x = n - 1; x >= 0; x--)
            {
                var i = z * n + x;
                var v = d[i];
                if (x + 1 < n) v = Mathf.Min(v, d[i + 1] + straight);
                if (z + 1 < n) v = Mathf.Min(v, d[i + n] + straight);
                if (x + 1 < n && z + 1 < n) v = Mathf.Min(v, d[i + n + 1] + diagonal);
                if (x > 0 && z + 1 < n) v = Mathf.Min(v, d[i + n - 1] + diagonal);
                d[i] = v;
            }

            var pixels = new byte[n * n];
            for (var i = 0; i < pixels.Length; i++)
                // A water cell's centre is half a cell from the coast at least; the coast itself (between cells) reads 0.
                pixels[i] = (byte)Mathf.RoundToInt(Mathf.Clamp01(water[i] ? (d[i] - cell * 0.5f) / ShoreReach : 0f) * 255f);
            var texture = new Texture2D(n, n, TextureFormat.R8, false, true)
            {
                name = "Shore Distance",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear,
            };
            texture.SetPixelData(pixels, 0);
            texture.Apply(false, true);
            return texture;
        }

        private void DisposeWater()
        {
            if (_shoreTexture != null) Object.Destroy(_shoreTexture);
            if (_edgeWater != null) Object.Destroy(_edgeWater);
            if (_calmWater != null) Object.Destroy(_calmWater);
        }
    }
}

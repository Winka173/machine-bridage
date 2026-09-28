using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// The battlefields' pictures (Resources/UI/Maps/&lt;map&gt;.png, drawn from the map data by
    /// Tools/maps/map_thumbs.py): the map dropdown's thumbnails, the chapter cards, the mission
    /// detail and the briefing card.
    /// </summary>
    public static class MapArt
    {
        private static readonly Dictionary<string, Texture2D> Loaded = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => Loaded.Clear();

        public static Texture2D For(string mapId)
        {
            if (string.IsNullOrEmpty(mapId)) return null;
            if (Loaded.TryGetValue(mapId, out var tex) && tex != null) return tex;
            tex = Resources.Load<Texture2D>("UI/Maps/" + mapId);
            Loaded[mapId] = tex;
            return tex;
        }
    }

    /// <summary>The shop's pictures (Resources/UI/Shop): the crates (renders of the crate models) and the coin packs.</summary>
    public static class ShopArt
    {
        private static readonly Dictionary<string, Texture2D> Loaded = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics() => Loaded.Clear();

        public static Texture2D Crate(CrateKind kind) => Load("crate_" + kind.ToString().ToLowerInvariant());

        /// <summary>The coin pack's picture by its place in the store (a bigger pile for a bigger pack).</summary>
        public static Texture2D CoinPack(int index) => Load("coins_" + Mathf.Clamp(index + 1, 1, 6));

        private static Texture2D Load(string name)
        {
            if (Loaded.TryGetValue(name, out var tex) && tex != null) return tex;
            tex = Resources.Load<Texture2D>("UI/Shop/" + name);
            Loaded[name] = tex;
            return tex;
        }
    }

    /// <summary>
    /// A camouflage's colours in bands (the shop's paint tiles). The colours are the product's own
    /// data, not the interface's, so they are painted here rather than set as styles.
    /// </summary>
    public sealed class KitPaintSample : VisualElement
    {
        private readonly Color[] _colours;

        public KitPaintSample(IReadOnlyList<Color> colours, bool metallic)
        {
            _colours = new Color[colours.Count];
            for (var i = 0; i < colours.Count; i++) _colours[i] = colours[i];
            AddToClassList("fc-paint");
            EnableInClassList("fc-paint--metal", metallic);
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Paint;
        }

        private void Paint(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width <= 0f || _colours.Length == 0) return;
            var p = context.painter2D;
            // Diagonal bands, like a camouflage net's strips.
            var band = r.width / (_colours.Length + 1f);
            for (var i = -1; i <= _colours.Length + 1; i++)
            {
                var x = r.xMin + i * band;
                p.fillColor = _colours[(i % _colours.Length + _colours.Length) % _colours.Length];
                p.BeginPath();
                p.MoveTo(new Vector2(Mathf.Clamp(x, r.xMin, r.xMax), r.yMin));
                p.LineTo(new Vector2(Mathf.Clamp(x + band, r.xMin, r.xMax), r.yMin));
                p.LineTo(new Vector2(Mathf.Clamp(x + band - r.height * 0.5f, r.xMin, r.xMax), r.yMax));
                p.LineTo(new Vector2(Mathf.Clamp(x - r.height * 0.5f, r.xMin, r.xMax), r.yMax));
                p.ClosePath();
                p.Fill();
            }
        }
    }
}

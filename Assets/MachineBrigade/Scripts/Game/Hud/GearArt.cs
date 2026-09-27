using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// How equipment looks in the menus: the piece's rendered picture (Tools/blender/mb_gear_icons.py)
    /// on a frame that says its rarity at a glance: grey, green, blue, purple or gold, darker at the
    /// edges and glowing at the heart, a brighter border, a shine across the legendary ones, and one
    /// to five pips along the bottom.
    /// </summary>
    internal static class GearArt
    {
        // Grey, green, blue, purple and orange: legendary is orange, not gold, so it never reads as
        // the coin's yellow or the battle button's amber.
        public static readonly Color[] Colors =
        {
            new(0.6f, 0.655f, 0.69f), new(0.3f, 0.78f, 0.39f), new(0.243f, 0.557f, 1f), new(0.643f, 0.361f, 1f), new(1f, 0.541f, 0.122f),
        };

        private static readonly Dictionary<int, Texture2D> Frames = new();
        private static readonly Dictionary<string, Texture2D> Pictures = new();

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); textures die with the scene.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            Frames.Clear();
            Pictures.Clear();
        }

        public static string PictureName(GearItem item) =>
            item.Slot == GearSlot.Special ? item.Module.ToString().ToLowerInvariant() : item.Slot.ToString().ToLowerInvariant();

        /// <summary>A tile for a piece: frame, picture, level and pips. <paramref name="size"/> in panel pixels.</summary>
        public static VisualElement Tile(GearItem item, float size, bool showLevel = true)
        {
            var tile = new VisualElement { pickingMode = PickingMode.Ignore };
            tile.AddToClassList("gear-art");
            tile.style.width = tile.style.height = size;
            tile.style.backgroundImage = Background.FromTexture2D(Frame(item.rarity));
            var picture = new VisualElement { pickingMode = PickingMode.Ignore };
            picture.AddToClassList("gear-art-picture");
            if (Picture(PictureName(item)) is { } tex) picture.style.backgroundImage = Background.FromTexture2D(tex);
            tile.Add(picture);
            var pips = new VisualElement { pickingMode = PickingMode.Ignore };
            pips.AddToClassList("gear-art-pips");
            for (var i = 0; i <= item.rarity; i++)
            {
                var pip = new VisualElement { pickingMode = PickingMode.Ignore };
                pip.AddToClassList("gear-art-pip");
                pip.style.backgroundColor = Colors[item.rarity];
                pips.Add(pip);
            }
            tile.Add(pips);
            if (showLevel)
            {
                var level = new Label(Strings.Format("gear.level", item.level)) { pickingMode = PickingMode.Ignore };
                level.AddToClassList("gear-art-level");
                tile.Add(level);
            }
            return tile;
        }

        /// <summary>An empty slot's tile: a dim frame with the slot's picture ghosted.</summary>
        public static VisualElement Empty(GearSlot slot, float size)
        {
            var tile = new VisualElement { pickingMode = PickingMode.Ignore };
            tile.AddToClassList("gear-art");
            tile.AddToClassList("empty");
            tile.style.width = tile.style.height = size;
            var picture = new VisualElement { pickingMode = PickingMode.Ignore };
            picture.AddToClassList("gear-art-picture");
            var name = slot == GearSlot.Special ? "reactivearmor" : slot.ToString().ToLowerInvariant();
            if (Picture(name) is { } tex) picture.style.backgroundImage = Background.FromTexture2D(tex);
            tile.Add(picture);
            return tile;
        }

        public static Texture2D Picture(string name)
        {
            if (Pictures.TryGetValue(name, out var tex) && tex != null) return tex;
            tex = Resources.Load<Texture2D>("UI/Gear/gear_" + name);
            Pictures[name] = tex;
            return tex;
        }

        /// <summary>The rarity frame, drawn once per rarity: a radial glow in its colour, a border, and for legendary a diagonal shine.</summary>
        public static Texture2D Frame(int rarity)
        {
            if (Frames.TryGetValue(rarity, out var cached) && cached != null) return cached;
            const int n = 128;
            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { name = "Rarity Frame " + rarity, wrapMode = TextureWrapMode.Clamp };
            var colour = Colors[rarity];
            var dark = new Color(0.07f, 0.085f, 0.095f);
            var pixels = new Color[n * n];
            const float corner = 14f;
            for (var y = 0; y < n; y++)
            for (var x = 0; x < n; x++)
            {
                // Rounded square: distance outside the rounded corner, for a soft edge.
                var dx = Mathf.Max(corner - x, x - (n - 1 - corner), 0f);
                var dy = Mathf.Max(corner - y, y - (n - 1 - corner), 0f);
                var outside = Mathf.Sqrt(dx * dx + dy * dy) - corner;
                var alpha = Mathf.Clamp01(0.5f - outside);
                if (alpha <= 0f)
                {
                    pixels[y * n + x] = Color.clear;
                    continue;
                }
                var u = (x - n * 0.5f) / (n * 0.5f);
                var v = (y - n * 0.42f) / (n * 0.5f);
                var glow = Mathf.Clamp01(1f - Mathf.Sqrt(u * u + v * v) * 0.95f);
                // Filled with the rarity's colour, lit from the top, brightest behind the picture: a
                // full-colour tile reads across a room (Archero's and Survivor.io's do).
                var lit = Mathf.Lerp(0.2f, 0.62f, Mathf.Pow(y / (n - 1f), 1.3f)) + glow * glow * 0.26f;
                var c = dark * 0.45f + colour * lit;
                // A darker band along the bottom, under the pips and the level.
                if (y < 14) c = Color.Lerp(c, dark, 0.45f);
                // Border: 3 px of the colour, a lighter inner line.
                var edge = -outside;
                if (edge < 3.5f) c = Color.Lerp(c, colour, 0.95f);
                else if (edge < 5f) c = Color.Lerp(c, Color.Lerp(colour, Color.white, 0.4f), 0.35f);
                // Legendary: a diagonal shine; epic: a brighter heart.
                if (rarity >= 4)
                {
                    var band = Mathf.Abs((x + y) - n * 1.15f);
                    c += new Color(1f, 0.95f, 0.8f) * Mathf.Clamp01(1f - band / 10f) * 0.22f;
                }
                else if (rarity == 3) c += colour * glow * glow * glow * 0.18f;
                c.a = alpha;
                pixels[y * n + x] = c;
            }
            tex.SetPixels(pixels);
            tex.Apply(false, true);
            Frames[rarity] = tex;
            return tex;
        }
    }
}

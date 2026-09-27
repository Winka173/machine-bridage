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
            Own.Clear();
            NoPicture.Clear();
        }

        /// <summary>
        /// The picture a piece falls back to when its base type has none of its own yet
        /// (Resources/UI/Gear/gear_&lt;name&gt;): its slot's, plating base types the old plating's,
        /// Optics the crew helmet with its goggles, new modules the reactive armour's.
        /// </summary>
        public static string PictureName(GearItem item)
        {
            if (item.Slot == GearSlot.Special)
                return item.Module is SpecialModule.ReactiveArmor or SpecialModule.AutoRepair or SpecialModule.VeteranCrew or SpecialModule.SmokeDischarger
                    ? item.Module.ToString().ToLowerInvariant()
                    : "reactivearmor";
            return SlotPicture(item.Slot, Gear.BaseOf(item)?.Plating == true);
        }

        private static string SlotPicture(GearSlot slot, bool plating = false) => slot switch
        {
            GearSlot.Special => "reactivearmor",
            GearSlot.Optics => "veterancrew",
            GearSlot.Armor when plating => "plating",
            _ => slot.ToString().ToLowerInvariant(),
        };

        private static readonly Dictionary<string, Texture2D> Own = new();
        private static readonly HashSet<string> NoPicture = new();

        /// <summary>A piece's own picture (Resources/UI/Gear/&lt;base type id&gt;), else its fallback (a missing one is looked for once).</summary>
        public static Texture2D PictureFor(GearItem item)
        {
            var id = item.baseType;
            if (!string.IsNullOrEmpty(id) && !NoPicture.Contains(id))
            {
                if (!Own.TryGetValue(id, out var tex) || tex == null)
                {
                    tex = Resources.Load<Texture2D>("UI/Gear/" + id);
                    if (tex == null) NoPicture.Add(id);
                    else Own[id] = tex;
                }
                if (tex != null) return tex;
            }
            return Picture(PictureName(item));
        }

        /// <summary>A tile for a piece: frame, picture, level and pips. <paramref name="size"/> in panel pixels.</summary>
        public static VisualElement Tile(GearItem item, float size, bool showLevel = true)
        {
            var tile = new VisualElement { pickingMode = PickingMode.Ignore };
            tile.AddToClassList("gear-art");
            tile.style.width = tile.style.height = size;
            tile.style.backgroundImage = Background.FromTexture2D(Frame(item.rarity));
            var picture = new VisualElement { pickingMode = PickingMode.Ignore };
            picture.AddToClassList("gear-art-picture");
            if (PictureFor(item) is { } tex) picture.style.backgroundImage = Background.FromTexture2D(tex);
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
            var name = SlotPicture(slot);
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

        /// <summary>
        /// The rarity frame, drawn once per rarity: graphite tinted by the rarity, a glow in its
        /// colour behind the picture, a hairline border and a bar of the colour along the bottom
        /// (the menus' flat style: square corners, the colour where it tells), and for legendary a
        /// diagonal shine.
        /// </summary>
        public static Texture2D Frame(int rarity)
        {
            if (Frames.TryGetValue(rarity, out var cached) && cached != null) return cached;
            const int n = 128;
            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { name = "Rarity Frame " + rarity, wrapMode = TextureWrapMode.Clamp };
            var colour = Colors[rarity];
            var dark = new Color(0.07f, 0.085f, 0.095f);
            var pixels = new Color[n * n];
            const float corner = 3f;
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
                // Graphite tinted by the rarity, lit from the top, a glow of the colour behind the
                // picture: the rarity still reads across a room without a full-colour tile.
                var lit = Mathf.Lerp(0.1f, 0.3f, Mathf.Pow(y / (n - 1f), 1.3f)) + glow * glow * 0.34f;
                var c = dark * 0.85f + colour * lit;
                // A darker band along the bottom, under the pips and the level, on a bar of the colour.
                if (y < 16) c = Color.Lerp(c, dark, 0.55f);
                if (y < 5) c = colour;
                // Border: a 2 px line of the colour.
                var edge = -outside;
                if (edge < 2.5f) c = Color.Lerp(c, colour, 0.85f);
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

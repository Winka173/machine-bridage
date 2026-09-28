using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Reads the design tokens of Resources/UI/Tokens.uss (for the UI checks and the render and
    /// screenshot tools) and the WCAG contrast arithmetic the checks and the preview use.
    /// </summary>
    public static class KitTokens
    {
        /// <summary>The theme file, relative to the project folder.</summary>
        public const string AssetPath = "Assets/MachineBrigade/Resources/UI/Tokens.uss";

        private static readonly Regex Declaration = new(@"--(fc-[a-z0-9-]+)\s*:\s*([^;]+);");

        /// <summary>The text of a stylesheet block: everything between the braces after <paramref name="selector"/>.</summary>
        public static string Block(string uss, string selector)
        {
            var start = uss.IndexOf(selector + " {", System.StringComparison.Ordinal);
            if (start < 0) return "";
            var open = uss.IndexOf('{', start);
            var close = uss.IndexOf('}', open);
            return close > open ? uss.Substring(open + 1, close - open - 1) : "";
        }

        /// <summary>The --fc-* declarations of a block, name (without the dashes) to raw value.</summary>
        public static Dictionary<string, string> Declarations(string block)
        {
            var map = new Dictionary<string, string>();
            foreach (System.Text.RegularExpressions.Match m in Declaration.Matches(StripComments(block))) map[m.Groups[1].Value] = m.Groups[2].Value.Trim();
            return map;
        }

        public static string StripComments(string css) => Regex.Replace(css, @"/\*.*?\*/", "", RegexOptions.Singleline);

        /// <summary>A #rrggbb or rgba(r, g, b, a) value.</summary>
        public static bool TryColour(string value, out Color colour)
        {
            colour = default;
            value = value.Trim();
            if (value.StartsWith("#")) return ColorUtility.TryParseHtmlString(value, out colour);
            var m = Regex.Match(value, @"^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$");
            if (!m.Success) return false;
            float F(int i) => float.Parse(m.Groups[i].Value, CultureInfo.InvariantCulture);
            colour = new Color(F(1) / 255f, F(2) / 255f, F(3) / 255f, m.Groups[4].Success ? F(4) : 1f);
            return true;
        }

        /// <summary>A pixel size ("21px").</summary>
        public static bool TryPixels(string value, out float px)
        {
            px = 0f;
            var m = Regex.Match(value.Trim(), @"^(-?[\d.]+)px$");
            return m.Success && float.TryParse(m.Groups[1].Value, NumberStyles.Float, CultureInfo.InvariantCulture, out px);
        }

        /// <summary>WCAG relative luminance of an sRGB colour.</summary>
        public static float Luminance(Color c)
        {
            static float Channel(float v) => v <= 0.04045f ? v / 12.92f : Mathf.Pow((v + 0.055f) / 1.055f, 2.4f);
            return 0.2126f * Channel(c.r) + 0.7152f * Channel(c.g) + 0.0722f * Channel(c.b);
        }

        public static float Contrast(Color a, Color b)
        {
            var la = Luminance(a);
            var lb = Luminance(b);
            return (Mathf.Max(la, lb) + 0.05f) / (Mathf.Min(la, lb) + 0.05f);
        }

        /// <summary>A translucent colour over a backdrop (alpha blending in sRGB, as the UI draws it).</summary>
        public static Color Over(Color top, Color backdrop)
        {
            var a = top.a;
            return new Color(top.r * a + backdrop.r * (1f - a), top.g * a + backdrop.g * (1f - a), top.b * a + backdrop.b * (1f - a), 1f);
        }

        /// <summary>The contrast a text needs: 4.5:1, or 3:1 from 24 px at the 1400 px reference (26.7 panel px) up.</summary>
        public static float RequiredContrast(float panelPx) => panelPx >= 24f * Kit.PanelPxPerReferencePx - 0.01f ? 3f : 4.5f;
    }

    /// <summary>A colour swatch for the kit preview: it paints the colour of a token it reads from the stylesheet (no colour in code).</summary>
    public sealed class KitSwatch : VisualElement
    {
        private readonly CustomStyleProperty<Color> _token, _against;
        private Color _colour, _backdrop;
        private readonly Label _ratio;

        public KitSwatch(string token, string against = "fc-panel-raised", Label ratio = null)
        {
            _token = new CustomStyleProperty<Color>("--" + token);
            _against = new CustomStyleProperty<Color>("--" + against);
            _ratio = ratio;
            AddToClassList("fc-swatch__colour");
            generateVisualContent += Paint;
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                e.customStyle.TryGetValue(_token, out _colour);
                e.customStyle.TryGetValue(_against, out _backdrop);
                if (_ratio != null)
                    _ratio.text = KitTokens.Contrast(KitTokens.Over(_colour, _backdrop), _backdrop).ToString("0.0", CultureInfo.InvariantCulture) + ":1";
                MarkDirtyRepaint();
            });
        }

        private void Paint(MeshGenerationContext context)
        {
            var r = contentRect;
            if (r.width <= 0f || r.height <= 0f) return;
            var p = context.painter2D;
            p.fillColor = _colour;
            p.BeginPath();
            p.MoveTo(r.min);
            p.LineTo(new Vector2(r.xMax, r.yMin));
            p.LineTo(r.max);
            p.LineTo(new Vector2(r.xMin, r.yMax));
            p.ClosePath();
            p.Fill();
        }
    }
}

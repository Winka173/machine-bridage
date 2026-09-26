using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
using RegexMatch = System.Text.RegularExpressions.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Stroke icons on a 24-unit grid (the 3d_astra set, Lucide style, plus a few of our own),
    /// drawn as vectors with Painter2D so they stay crisp at any screen density.
    /// </summary>
    public static class Icons
    {
        private static readonly Dictionary<string, string> Svg = new()
        {
            ["logo"] = "<path d=\"M12 2 22 20H2Z\"/><path d=\"m12 9 5 9H7Z\"/>",
            ["people"] = "<circle cx=\"9\" cy=\"7\" r=\"3\"/><path d=\"M3 21v-4a6 6 0 0 1 12 0v4M16 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3\"/>",
            ["shield"] = "<path d=\"m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6Z\"/><path d=\"m8 11 3 3 5-6\"/>",
            ["crosshair"] = "<circle cx=\"12\" cy=\"12\" r=\"7\"/><path d=\"M12 1v6m0 10v6M1 12h6m10 0h6\"/><circle cx=\"12\" cy=\"12\" r=\"1\"/>",
            ["tank"] = "<rect x=\"3\" y=\"13\" width=\"18\" height=\"7\" rx=\"3\"/><path d=\"M7 13V8h8v5M15 9h7M7 17h1m3 0h1m3 0h1\"/>",
            ["bolt"] = "<path d=\"m14 2-9 12h7l-2 8 9-12h-7Z\"/>",
            ["move"] = "<path d=\"M12 2v20M2 12h20M8 6l4-4 4 4M8 18l4 4 4-4M6 8l-4 4 4 4m12-8 4 4-4 4\"/>",
            ["stop"] = "<rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>",
            ["pause"] = "<path d=\"M8 4v16M16 4v16\"/>",
            ["play"] = "<path d=\"m7 3 14 9-14 9Z\"/>",
            ["help"] = "<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M9 8a3 3 0 1 1 4 3c-1 1-1 1-1 3m0 3v1\"/>",
            ["arrow"] = "<path d=\"M4 12h16m-6-6 6 6-6 6\"/>",
            ["close"] = "<path d=\"m5 5 14 14M5 19 19 5\"/>",
            ["flag"] = "<path d=\"M5 22V3h14l-3 5 3 5H5\"/>",
            ["check"] = "<path d=\"m5 12 4 4L19 6\"/>",
            ["expand"] = "<path d=\"M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5\"/>",
            ["info"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 11v6M12 7.5v.5\"/>",
            ["attack"] = "<path d=\"M20 4 9 15M20 4h-5M20 4v5M7 13l4 4M4 20l4-4\"/>",
            // Machine Brigade additions in the same style.
            ["plus"] = "<path d=\"M12 5v14M5 12h14\"/>",
            ["minus"] = "<path d=\"M5 12h14\"/>",
            ["restart"] = "<path d=\"M3 12a9 9 0 1 0 3-6.7L3 8\"/><path d=\"M3 3v5h5\"/>",
            ["retreat"] = "<path d=\"M9 14 4 9l5-5\"/><path d=\"M4 9h11a5 5 0 0 1 0 10h-3\"/>",
            ["reinforce"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 8v8M8 12h8\"/>",
            ["jeep"] = "<path d=\"M3 15v-3l2-4h7l3 4h5l1 3Z\"/><circle cx=\"7\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/>",
            ["artillery"] = "<rect x=\"3\" y=\"14\" width=\"14\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-4h6v4M13 11l8-5\"/>",
            ["apc"] = "<path d=\"M3 15v-4l3-3h10l4 4v3Z\"/><circle cx=\"6.5\" cy=\"17\" r=\"1.8\"/><circle cx=\"11.5\" cy=\"17\" r=\"1.8\"/><circle cx=\"16.5\" cy=\"17\" r=\"1.8\"/><path d=\"M11 8V6h6\"/>",
            ["helicopter"] = "<path d=\"M3 5h18M12 5v3\"/><path d=\"M5 12a3 3 0 0 1 3-3h7l3 3v2a2 2 0 0 1-2 2H8a3 3 0 0 1-3-3Z\"/><path d=\"M18 12h4M8 16v3m6-3v3M6 19h10\"/>",
            ["aa"] = "<rect x=\"3\" y=\"14\" width=\"16\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-3h8v3M10 11l4-7M13 11l4-6\"/>",
            ["mlrs"] = "<path d=\"M2 16v-4h4l2-3h3v7M11 16h10v-3H11ZM12 13l8-6 1 2-8 4\"/><circle cx=\"5\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/>",
            ["lighttank"] = "<rect x=\"3\" y=\"14\" width=\"15\" height=\"6\" rx=\"3\"/><path d=\"M7 14v-3h6v3M13 12h5\"/>",
            ["armoredcar"] = "<path d=\"M3 15v-3l3-3h10l4 3v3Z\"/><circle cx=\"6\" cy=\"17\" r=\"1.6\"/><circle cx=\"11\" cy=\"17\" r=\"1.6\"/><circle cx=\"16\" cy=\"17\" r=\"1.6\"/><path d=\"M10 9V7h4v2M14 8h6\"/>",
            ["destroyer"] = "<rect x=\"3\" y=\"14\" width=\"14\" height=\"6\" rx=\"3\"/><path d=\"M6 14v-3h7v3M13 12h9\"/>",
            ["heavytank"] = "<rect x=\"2\" y=\"13\" width=\"18\" height=\"7\" rx=\"3.5\"/><path d=\"M6 13V9h9v4M15 10.5h7M9 9V7h3\"/>",
            ["sam"] = "<rect x=\"3\" y=\"15\" width=\"15\" height=\"5\" rx=\"2.5\"/><path d=\"M8 15v-2h6v2M9 13l6-8 2 1-5 7M12 13l6-6 1 2-4 4\"/>",
            ["mortar"] = "<path d=\"M3 15v-4l3-3h10l4 4v3Z\"/><circle cx=\"7\" cy=\"17\" r=\"1.8\"/><circle cx=\"15\" cy=\"17\" r=\"1.8\"/><path d=\"M11 8l5-6 1.5 1-4.5 6\"/>",
            ["technical"] = "<path d=\"M2 16v-3h8V9h5l3 4h3v3Z\"/><circle cx=\"6\" cy=\"17\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/><path d=\"M3 12l6-4M4 13.5l6-4\"/>",
            ["gunship"] = "<path d=\"M2 5h20M12 5v3\"/><path d=\"M3 12a3 3 0 0 1 3-3h9l4 3v2a2 2 0 0 1-2 2H6a3 3 0 0 1-3-3Z\"/><path d=\"M19 12h3M6 16v3M15 16v3M4 19h13M8 12h6\"/>",
            ["scoutheli"] = "<path d=\"M5 6h14M12 6v3\"/><circle cx=\"10\" cy=\"13\" r=\"4\"/><path d=\"M14 13h7M19 11v4M8 17l-1 3M12 17l1 3\"/>",
            ["jet"] = "<path d=\"M12 2c1 0 1.5 2 1.5 4v12h-3V6c0-2 .5-4 1.5-4Z\"/><path d=\"M2 11h20v2H2ZM7 20h10M9 17h6\"/>",
            ["drone"] = "<path d=\"M2 10h20M12 6v12M9 18h6M10 20l2-2 2 2\"/><circle cx=\"12\" cy=\"5\" r=\"1.5\"/>",
            ["snow"] = "<path d=\"M12 2v20M4 7l16 10M20 7 4 17M9 4l3 2 3-2M9 20l3-2 3 2\"/>",
            ["wind"] = "<path d=\"M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h8\"/>",
            ["fog"] = "<path d=\"M4 9h16M2 13h20M5 17h14M7 21h10\"/><path d=\"M7 9a5 5 0 0 1 10 0\"/>",
            ["moon"] = "<path d=\"M20 14A8 8 0 1 1 10 4a6 6 0 0 0 10 10Z\"/>",
            ["pine"] = "<path d=\"M12 2 6 10h3l-4 6h14l-4-6h3ZM12 16v6\"/>",
            ["dune"] = "<path d=\"M2 19c4-6 8-6 11-2s6 3 9-1M6 9a3 3 0 1 0 0-.1\"/><path d=\"M16 4v6M13 7h6\"/>",
            ["anchor"] = "<path d=\"M12 7v14M5 13a7 7 0 0 0 14 0M3 13h4M17 13h4\"/><circle cx=\"12\" cy=\"5\" r=\"2\"/>",
            ["flame"] = "<path d=\"M12 22a7 7 0 0 0 7-7c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-3 3-5 5-5 8a7 7 0 0 0 7 7Z\"/>",
            ["barrage"] = "<path d=\"M6 3v6M12 2v7M18 3v6\"/><path d=\"M4 21a8 5 0 0 1 16 0\"/><path d=\"m9 13 3 3 3-3\"/>",
            ["airstrike"] = "<path d=\"M12 2l2 7 7 3v2l-7-1-1 6 3 2v1l-4-1-4 1v-1l3-2-1-6-7 1v-2l7-3Z\"/>",
            ["missile"] = "<path d=\"M4 20 15 9M15 9l4-6 2 2-6 4M9 15l-4 1 3 3 1-4M13 11l-3-4M13 11l4 3\"/>",
            ["smoke"] = "<path d=\"M4 17a4 4 0 0 1 2-7 5 5 0 0 1 9-2 4 4 0 0 1 5 5 3 3 0 0 1-1 6H7a3 3 0 0 1-3-2Z\"/>",
            ["repair"] = "<path d=\"M15 3a5 5 0 0 0-5 6L3 16l5 5 7-7a5 5 0 0 0 6-5l-3 3-3-1-1-3Z\"/>",
            ["settings"] = "<circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2\"/>",
            ["deck"] = "<rect x=\"3\" y=\"6\" width=\"12\" height=\"15\" rx=\"2\"/><path d=\"M8 3h11a2 2 0 0 1 2 2v13\"/>",
            ["trophy"] = "<path d=\"M7 4h10v5a5 5 0 0 1-10 0ZM7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4M12 14v4M8 21h8\"/>",
            ["home"] = "<path d=\"M3 11 12 3l9 8M5 9v12h14V9\"/>",
            ["cp"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M15 9a4 4 0 1 0 0 6\"/>",
            ["globe"] = "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18\"/>",
            ["volume"] = "<path d=\"M4 9h4l5-4v14l-5-4H4ZM16 9a4 4 0 0 1 0 6M19 6a8 8 0 0 1 0 12\"/>",
            ["sun"] = "<circle cx=\"12\" cy=\"12\" r=\"4\"/><path d=\"M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5\"/>",
            ["cloud"] = "<path d=\"M6 18a4 4 0 0 1 0-8 6 6 0 0 1 11-1 4 4 0 0 1 1 9Z\"/>",
            ["rain"] = "<path d=\"M5 14a4 4 0 0 1 2-7 5 5 0 0 1 9-1 4 4 0 0 1 3 8M8 17l-1 3M12 17l-1 3M16 17l-1 3\"/>",
            ["storm"] = "<path d=\"M5 13a4 4 0 0 1 2-7 5 5 0 0 1 9-1 4 4 0 0 1 3 8M13 13l-3 5h4l-3 5\"/>",
            ["dice"] = "<rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"3\"/><circle cx=\"9\" cy=\"9\" r=\"1\"/><circle cx=\"15\" cy=\"15\" r=\"1\"/><circle cx=\"15\" cy=\"9\" r=\"1\"/><circle cx=\"9\" cy=\"15\" r=\"1\"/>",
            ["skull"] = "<path d=\"M12 3a8 8 0 0 0-5 14v3h10v-3a8 8 0 0 0-5-14Z\"/><circle cx=\"9\" cy=\"11\" r=\"1.5\"/><circle cx=\"15\" cy=\"11\" r=\"1.5\"/><path d=\"M10 20v-2M14 20v-2\"/>",
        };

        private static readonly Dictionary<string, List<Shape>> Parsed = new();

        public static bool Exists(string name) => Svg.ContainsKey(name);

        internal static IReadOnlyList<Shape> Get(string name)
        {
            if (Parsed.TryGetValue(name, out var shapes)) return shapes;
            shapes = SvgParser.Parse(Svg.TryGetValue(name, out var svg) ? svg : Svg["logo"]);
            Parsed[name] = shapes;
            return shapes;
        }

        /// <summary>One drawing step in 24-unit icon space.</summary>
        internal readonly struct Op
        {
            public Op(char kind, Vector2 a, Vector2 b = default, Vector2 c = default, float radius = 0f, float start = 0f,
                float end = 0f)
            {
                Kind = kind;
                A = a;
                B = b;
                C = c;
                Radius = radius;
                Start = start;
                End = end;
            }

            /// <summary>M move, L line, C cubic, Q quadratic, A arc (A = centre), Z close.</summary>
            public char Kind { get; }
            public Vector2 A { get; }
            public Vector2 B { get; }
            public Vector2 C { get; }
            public float Radius { get; }
            public float Start { get; }
            public float End { get; }
        }

        internal sealed class Shape
        {
            public readonly List<Op> Ops = new();
        }

        /// <summary>Parses the SVG subset the icons use: path (all commands), circle and rect.</summary>
        private static class SvgParser
        {
            private static readonly Regex Element = new(@"<(path|circle|rect)\s([^>]*)/>");
            private static readonly Regex Attribute = new(@"([a-z]+)=""([^""]*)""");
            private static readonly Regex Token = new(@"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?");

            public static List<Shape> Parse(string svg)
            {
                var shapes = new List<Shape>();
                foreach (RegexMatch element in Element.Matches(svg))
                {
                    var attributes = new Dictionary<string, string>();
                    foreach (RegexMatch a in Attribute.Matches(element.Groups[2].Value)) attributes[a.Groups[1].Value] = a.Groups[2].Value;
                    var shape = new Shape();
                    switch (element.Groups[1].Value)
                    {
                        case "path":
                            PathData(attributes["d"], shape);
                            break;
                        case "circle":
                            var centre = new Vector2(F(attributes["cx"]), F(attributes["cy"]));
                            var r = F(attributes["r"]);
                            shape.Ops.Add(new Op('M', centre + new Vector2(r, 0f)));
                            shape.Ops.Add(new Op('A', centre, radius: r, start: 0f, end: Mathf.PI * 2f));
                            break;
                        case "rect":
                            Rect(F(attributes["x"]), F(attributes["y"]), F(attributes["width"]), F(attributes["height"]),
                                attributes.TryGetValue("rx", out var rx) ? F(rx) : 0f, shape);
                            break;
                    }
                    shapes.Add(shape);
                }
                return shapes;
            }

            private static void Rect(float x, float y, float w, float h, float r, Shape s)
            {
                r = Mathf.Min(r, w / 2f, h / 2f);
                s.Ops.Add(new Op('M', new Vector2(x + r, y)));
                s.Ops.Add(new Op('L', new Vector2(x + w - r, y)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + w - r, y + r), radius: r, start: -Mathf.PI / 2f, end: 0f));
                s.Ops.Add(new Op('L', new Vector2(x + w, y + h - r)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + w - r, y + h - r), radius: r, start: 0f, end: Mathf.PI / 2f));
                s.Ops.Add(new Op('L', new Vector2(x + r, y + h)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + r, y + h - r), radius: r, start: Mathf.PI / 2f, end: Mathf.PI));
                s.Ops.Add(new Op('L', new Vector2(x, y + r)));
                if (r > 0f) s.Ops.Add(new Op('A', new Vector2(x + r, y + r), radius: r, start: Mathf.PI, end: Mathf.PI * 1.5f));
                s.Ops.Add(new Op('Z', default));
            }

            private static void PathData(string d, Shape s)
            {
                var tokens = new List<string>();
                foreach (RegexMatch t in Token.Matches(d)) tokens.Add(t.Value);
                var i = 0;
                var command = 'M';
                Vector2 current = default, start = default, lastControl = default;
                var lastKind = ' ';
                while (i < tokens.Count)
                {
                    if (char.IsLetter(tokens[i][0])) command = tokens[i++][0];
                    var relative = char.IsLower(command);
                    var offset = relative ? current : Vector2.zero;
                    switch (char.ToUpperInvariant(command))
                    {
                        case 'M':
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            start = current;
                            s.Ops.Add(new Op('M', current));
                            command = relative ? 'l' : 'L'; // extra pairs after a move are lines
                            break;
                        case 'L':
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'H':
                            current = new Vector2((relative ? current.x : 0f) + F(tokens[i++]), current.y);
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'V':
                            current = new Vector2(current.x, (relative ? current.y : 0f) + F(tokens[i++]));
                            s.Ops.Add(new Op('L', current));
                            break;
                        case 'C':
                        {
                            var c1 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            var c2 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('C', c1, c2, current));
                            lastControl = c2;
                            break;
                        }
                        case 'S':
                        {
                            var c1 = lastKind is 'C' or 'S' ? current * 2f - lastControl : current;
                            var c2 = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('C', c1, c2, current));
                            lastControl = c2;
                            break;
                        }
                        case 'Q':
                        {
                            var c = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            current = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            s.Ops.Add(new Op('Q', c, current));
                            lastControl = c;
                            break;
                        }
                        case 'A':
                        {
                            var rx = F(tokens[i++]);
                            i += 2; // ry (icons use circular arcs) and x-axis rotation
                            var large = F(tokens[i++]) != 0f;
                            var sweep = F(tokens[i++]) != 0f;
                            var end = offset + new Vector2(F(tokens[i++]), F(tokens[i++]));
                            AddArc(s, current, end, rx, large, sweep);
                            current = end;
                            break;
                        }
                        case 'Z':
                            s.Ops.Add(new Op('Z', default));
                            current = start;
                            break;
                        default:
                            i++; // unknown command: skip a token rather than loop forever
                            break;
                    }
                    lastKind = char.ToUpperInvariant(command);
                }
            }

            /// <summary>SVG endpoint arc to centre form (circular arcs, no rotation).</summary>
            private static void AddArc(Shape s, Vector2 p1, Vector2 p2, float r, bool large, bool sweep)
            {
                var half = (p1 - p2) * 0.5f;
                var lambda = half.sqrMagnitude / (r * r);
                if (lambda > 1f) r *= Mathf.Sqrt(lambda);
                var sign = large != sweep ? 1f : -1f;
                var numerator = r * r * r * r - r * r * half.y * half.y - r * r * half.x * half.x;
                var denominator = r * r * half.y * half.y + r * r * half.x * half.x;
                var coefficient = sign * Mathf.Sqrt(Mathf.Max(0f, numerator / Mathf.Max(denominator, 1e-6f)));
                var centrePrime = new Vector2(coefficient * half.y, -coefficient * half.x);
                var centre = centrePrime + (p1 + p2) * 0.5f;
                var a0 = Mathf.Atan2(half.y - centrePrime.y, half.x - centrePrime.x);
                var a1 = Mathf.Atan2(-half.y - centrePrime.y, -half.x - centrePrime.x);
                var delta = a1 - a0;
                if (!sweep && delta > 0f) delta -= Mathf.PI * 2f;
                if (sweep && delta < 0f) delta += Mathf.PI * 2f;
                s.Ops.Add(new Op('A', centre, radius: r, start: a0, end: a0 + delta));
            }

            private static float F(string s) => float.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture);
        }
    }

    /// <summary>A vector icon that takes its colour from <see cref="Tint"/>.</summary>
    public sealed class IconElement : VisualElement
    {
        private static readonly CustomStyleProperty<Color> IconColor = new("--icon-color");

        private string _name;
        private Color _tint = Color.white;
        private Color _styleColor = Color.white;
        private bool _explicitTint, _hasStyleColor;

        public IconElement(string name, float strokeWidth = 1.7f)
        {
            _name = name;
            StrokeWidth = strokeWidth;
            pickingMode = PickingMode.Ignore;
            AddToClassList("icon");
            generateVisualContent += Draw;
            // Unless given a colour in code, an icon follows the stylesheet's --icon-color, so a
            // selected (amber) button can turn its icon dark.
            RegisterCallback<CustomStyleResolvedEvent>(OnStyleResolved);
        }

        private void OnStyleResolved(CustomStyleResolvedEvent e)
        {
            if (!e.customStyle.TryGetValue(IconColor, out var colour) || (_hasStyleColor && colour == _styleColor)) return;
            _styleColor = colour;
            _hasStyleColor = true;
            if (!_explicitTint) MarkDirtyRepaint();
        }

        public float StrokeWidth { get; }

        public string Name
        {
            get => _name;
            set
            {
                if (_name == value) return;
                _name = value;
                MarkDirtyRepaint();
            }
        }

        public Color Tint
        {
            get => _tint;
            set
            {
                if (_explicitTint && _tint == value) return;
                _tint = value;
                _explicitTint = true;
                MarkDirtyRepaint();
            }
        }

        private void Draw(MeshGenerationContext context)
        {
            var rect = contentRect;
            var scale = Mathf.Min(rect.width, rect.height) / 24f;
            if (scale <= 0f) return;
            var origin = rect.position + (rect.size - Vector2.one * 24f * scale) * 0.5f;
            var p = context.painter2D;
            p.strokeColor = _explicitTint || !_hasStyleColor ? _tint : _styleColor;
            p.lineWidth = StrokeWidth * scale;
            p.lineCap = LineCap.Round;
            p.lineJoin = LineJoin.Round;
            foreach (var shape in Icons.Get(_name))
            {
                p.BeginPath();
                foreach (var op in shape.Ops)
                {
                    switch (op.Kind)
                    {
                        case 'M': p.MoveTo(origin + op.A * scale); break;
                        case 'L': p.LineTo(origin + op.A * scale); break;
                        case 'C': p.BezierCurveTo(origin + op.A * scale, origin + op.B * scale, origin + op.C * scale); break;
                        case 'Q': p.QuadraticCurveTo(origin + op.A * scale, origin + op.B * scale); break;
                        case 'A':
                            p.Arc(origin + op.A * scale, op.Radius * scale, Angle.Radians(op.Start), Angle.Radians(op.End),
                                op.End >= op.Start ? ArcDirection.Clockwise : ArcDirection.CounterClockwise);
                            break;
                        case 'Z': p.ClosePath(); break;
                    }
                }
                p.Stroke();
            }
        }
    }
}

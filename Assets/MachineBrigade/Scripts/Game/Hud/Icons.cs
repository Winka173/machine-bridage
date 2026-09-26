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
        private string _name;
        private Color _tint = Color.white;

        public IconElement(string name, float strokeWidth = 1.7f)
        {
            _name = name;
            StrokeWidth = strokeWidth;
            pickingMode = PickingMode.Ignore;
            AddToClassList("icon");
            generateVisualContent += Draw;
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
                if (_tint == value) return;
                _tint = value;
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
            p.strokeColor = _tint;
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

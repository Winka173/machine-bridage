using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Re-reads the words of a screen built in the other language (prompt 21 L: the language changed in a paused
    /// battle). The battle keeps running under the pause, so its HUD is not rebuilt: each text and tooltip that is a
    /// table text of the old language (as it is, in capitals or highlighted) becomes the same text in the new one,
    /// and a filled text ("Wave 3 incoming") is matched against its old template and filled again, its numbers
    /// written the new language's way. The texts the HUD refreshes itself follow on their next update.
    /// </summary>
    public static class Relabel
    {
        private sealed class Template
        {
            public string Key;
            public Regex Pattern;
            public string[] Names;
            public string Anchor;
        }

        private sealed class Index
        {
            public readonly Dictionary<string, (string key, bool caps, bool rich)> Exact = new();
            public readonly List<Template> Templates = new();
        }

        private static readonly Dictionary<bool, Index> Indexes = new();
        private static readonly Regex Named = new(@"\{([A-Za-z][A-Za-z0-9_]*)(?::[^{}|]*)?(\|[^{}|]*\|[^{}|]*)?\}");
        private static readonly Regex NumberToken = new(@"(?<![\p{L}])[-+−]?\d[\d.,]*\d|\d");
        private static readonly string[] Separators = { "  ·  ", " · ", "\n", ": " };

        /// <summary>Every text and tooltip under <paramref name="root"/>, from the old language to the current one.</summary>
        public static int Apply(VisualElement root, bool fromVietnamese)
        {
            if (root == null || fromVietnamese == Strings.Vietnamese) return 0;
            var index = IndexFor(fromVietnamese);
            var changed = 0;
            root.Query<VisualElement>().ForEach(e =>
            {
                if (e is TextElement t && !string.IsNullOrEmpty(t.text))
                {
                    var n = Translate(t.text, index, fromVietnamese);
                    if (n != null && n != t.text) { t.text = n; changed++; }
                }
                if (!string.IsNullOrEmpty(e.tooltip))
                {
                    var n = Translate(e.tooltip, index, fromVietnamese);
                    if (n != null && n != e.tooltip) { e.tooltip = n; changed++; }
                }
            });
            return changed;
        }

        /// <summary>One text from the old language to the current one, or null when it is not a table text.</summary>
        public static string Translate(string text, bool fromVietnamese) =>
            fromVietnamese == Strings.Vietnamese ? text : Translate(text, IndexFor(fromVietnamese), fromVietnamese);

        private static string Translate(string text, Index index, bool fromVietnamese)
        {
            if (index.Exact.TryGetValue(text, out var hit)) return Present(hit.key, hit.caps, hit.rich);
            foreach (var t in index.Templates)
            {
                if (t.Anchor.Length > 0 && text.IndexOf(t.Anchor, StringComparison.OrdinalIgnoreCase) < 0) continue;
                var m = t.Pattern.Match(text);
                if (!m.Success) continue;
                var args = new (string name, object value)[t.Names.Length];
                for (var i = 0; i < t.Names.Length; i++)
                {
                    var value = m.Groups["p" + i].Value;
                    args[i] = (t.Names[i], TranslateValue(value, index, fromVietnamese));
                }
                var filled = Strings.Format(t.Key, args);
                // A text shown in capitals stays in capitals.
                return text == text.ToUpperInvariant() && text != text.ToLowerInvariant() ? Kit.Caps(filled) : filled;
            }
            // A text put together from table texts ("Tank · rank 3", "Title\nLine").
            foreach (var sep in Separators)
            {
                if (text.IndexOf(sep, StringComparison.Ordinal) < 0) continue;
                var parts = text.Split(new[] { sep }, StringSplitOptions.None);
                var any = false;
                for (var i = 0; i < parts.Length; i++)
                {
                    var n = Translate(parts[i], index, fromVietnamese);
                    if (n != null) { parts[i] = n; any = true; }
                    else parts[i] = SwapNumbers(parts[i], fromVietnamese);
                }
                if (any) return string.Join(sep, parts);
            }
            return null;
        }

        private static string TranslateValue(string value, Index index, bool fromVietnamese)
        {
            if (index.Exact.TryGetValue(value, out var hit)) return Present(hit.key, hit.caps, hit.rich);
            return SwapNumbers(value, fromVietnamese);
        }

        /// <summary>Numbers of the old language's format in the new one's (184.172 ↔ 184,172; 0,75 ↔ 0.75).</summary>
        private static string SwapNumbers(string text, bool fromVietnamese) =>
            NumberToken.Replace(text, m =>
            {
                var sb = new StringBuilder(m.Value.Length);
                foreach (var c in m.Value) sb.Append(c == '.' ? ',' : c == ',' ? '.' : c);
                return sb.ToString();
            });

        private static string Present(string key, bool caps, bool rich)
        {
            var text = Strings.Get(key);
            if (rich) text = Strings.Highlight(text);
            return caps ? Kit.Caps(text) : text;
        }

        private static Index IndexFor(bool vietnamese)
        {
            if (Indexes.TryGetValue(vietnamese, out var index)) return index;
            index = new Index();
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = vietnamese;
                foreach (var key in Strings.Keys.Distinct())
                {
                    var text = Strings.Get(key);
                    if (string.IsNullOrWhiteSpace(text)) continue;
                    if (Named.IsMatch(text))
                    {
                        var t = MakeTemplate(key, text);
                        if (t != null) index.Templates.Add(t);
                        continue;
                    }
                    index.Exact.TryAdd(text, (key, false, false));
                    index.Exact.TryAdd(Kit.Caps(text), (key, true, false));
                    if (text.Contains("[[")) index.Exact.TryAdd(Strings.Highlight(text), (key, false, true));
                }
                // The most specific templates first: the longest fixed text wins.
                index.Templates.Sort((a, b) => b.Anchor.Length.CompareTo(a.Anchor.Length));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            Indexes[vietnamese] = index;
            return index;
        }

        private static Template MakeTemplate(string key, string text)
        {
            var pattern = new StringBuilder("^");
            var names = new List<string>();
            var anchor = "";
            var last = 0;
            foreach (System.Text.RegularExpressions.Match m in Named.Matches(text))
            {
                var literal = text.Substring(last, m.Index - last);
                if (literal.Length > anchor.Length) anchor = literal;
                pattern.Append(Regex.Escape(literal));
                var name = m.Groups[1].Value;
                var repeated = names.Contains(name);
                var group = repeated ? ".+?" : "(?<p" + names.Count + ">.+?)";
                if (m.Groups[2].Success)
                {
                    // A plural ("{count|# tank|# tanks}"): either form, its "#" the number.
                    var forms = m.Groups[2].Value.Substring(1).Split('|');
                    var number = repeated ? @"[-+−]?\d[\d.,]*" : "(?<p" + names.Count + @">[-+−]?\d[\d.,]*)";
                    pattern.Append("(?:").Append(Regex.Escape(forms[0]).Replace(@"\#", number)).Append('|')
                        .Append(Regex.Escape(forms[1]).Replace(@"\#", number)).Append(')');
                    var word = forms[1].Replace("#", "").Trim();
                    if (word.Length > anchor.Length) anchor = word;
                }
                else pattern.Append(group);
                if (!repeated) names.Add(name);
                last = m.Index + m.Length;
            }
            var tail = text.Substring(last);
            if (tail.Length > anchor.Length) anchor = tail;
            pattern.Append(Regex.Escape(tail)).Append('$');
            // A text that is only placeholders ("{value}") would match anything.
            if (anchor.Trim().Length < 2) return null;
            return new Template { Key = key, Pattern = new Regex(pattern.ToString(), RegexOptions.Singleline | RegexOptions.IgnoreCase | RegexOptions.CultureInvariant), Names = names.ToArray(), Anchor = anchor };
        }
    }
}

using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>One registered key of SimTunables: the Entry, the field it reads, the field's default.</summary>
internal sealed class TunableKey
{
    public string Key = "";
    public string Unit = "";
    public string Kind = "scalar"; // scalar | flag | floatArray | intArray
    public string Path = "";        // Weapons.CombatSystem.AxisRatio
    public string File = "";        // where the Entry is
    public FieldInfo? Field;
}

internal sealed class FieldInfo
{
    public string Path = "";
    public string Type = "";
    public string? InitText;
    public TypedValue? Default;           // scalar default (literal / negated literal, or the C# default for no initializer)
    public List<TypedValue>? ArrayDefault; // array default
    public string Doc = "";
    public string File = "";
    public int Line;
    public ExpressionSyntax? Init;
}

/// <summary>Reads the SimTunables registry (all SimTunables*.cs) and tunables.json.</summary>
internal sealed class Registry
{
    public readonly Dictionary<string, TunableKey> Keys = new(StringComparer.Ordinal);
    public readonly Dictionary<string, FieldInfo> Fields = new(StringComparer.Ordinal); // by path
    public readonly Dictionary<string, JsonElement> Json = new(StringComparer.Ordinal);  // key -> the value element
    public readonly List<string> Problems = new();

    public static bool IsTunablesFile(string rel) =>
        rel.StartsWith(Repo.ContentDir + "/SimTunables", StringComparison.Ordinal) && rel.EndsWith(".cs");

    public static Registry Load(SourceSet s)
    {
        var r = new Registry();
        foreach (var (rel, text) in s.Files.Where(f => IsTunablesFile(f.Key)))
        {
            var root = CSharpSyntaxTree.ParseText(text, Compiler.SimParse, rel).GetRoot();
            r.ReadFields(root, rel);
            r.ReadEntries(root, rel);
        }
        foreach (var k in r.Keys.Values)
        {
            if (r.Fields.TryGetValue(k.Path, out var f)) k.Field = f;
            else r.Problems.Add($"{k.Key}: no field {k.Path}");
        }
        if (s.TunablesJson != null) r.ReadJson(s.TunablesJson);
        return r;
    }

    private void ReadFields(SyntaxNode root, string rel)
    {
        foreach (var fd in root.DescendantNodes().OfType<FieldDeclarationSyntax>())
        {
            var classes = fd.Ancestors().OfType<ClassDeclarationSyntax>().Select(c => c.Identifier.Text).Reverse().ToList();
            if (classes.Count < 2 || classes[0] != "SimTunables") continue;
            if (!fd.Modifiers.Any(SyntaxKind.StaticKeyword) || fd.Modifiers.Any(SyntaxKind.ReadOnlyKeyword) || fd.Modifiers.Any(SyntaxKind.PrivateKeyword)) continue;
            var doc = DocSummary(fd);
            var type = fd.Declaration.Type.ToString();
            foreach (var v in fd.Declaration.Variables)
            {
                var path = string.Join('.', classes.Skip(1).Append(v.Identifier.Text));
                var fi = new FieldInfo
                {
                    Path = path, Type = type, Init = v.Initializer?.Value, InitText = v.Initializer?.Value.ToString(), Doc = doc,
                    File = rel, Line = Syn.Line(v),
                };
                if (type.EndsWith("[]") && v.Initializer?.Value is InitializerExpressionSyntax or ArrayCreationExpressionSyntax)
                {
                    var init = v.Initializer.Value is ArrayCreationExpressionSyntax ac ? ac.Initializer : (InitializerExpressionSyntax)v.Initializer.Value;
                    fi.ArrayDefault = init?.Expressions.Select(e => TypedValue.FromExpression(e)).Where(x => x != null).Select(x => x!.Value).ToList();
                }
                else if (v.Initializer == null)
                    fi.Default = type switch
                    {
                        "bool" => new TypedValue("bool", false), "float" => new TypedValue("float", 0f), "int" => new TypedValue("int", 0),
                        "double" => new TypedValue("double", 0.0), _ => null,
                    };
                else fi.Default = TypedValue.FromExpression(v.Initializer.Value);
                Fields[path] = fi;
            }
        }
    }

    public static string DocSummary(SyntaxNode n)
    {
        var doc = n.GetLeadingTrivia().FirstOrDefault(t => t.IsKind(SyntaxKind.SingleLineDocumentationCommentTrivia));
        if (doc == default) return "";
        var s = string.Join(' ', doc.ToFullString().Split('\n').Select(l => l.Trim().TrimStart('/').Trim()));
        var m = Regex.Match(s, "<summary>(.*?)</summary>", RegexOptions.Singleline);
        return (m.Success ? m.Groups[1].Value : s).Trim();
    }

    private void ReadEntries(SyntaxNode root, string rel)
    {
        foreach (var e in root.DescendantNodes().OfType<ExpressionSyntax>())
        {
            ArgumentListSyntax? args;
            string kind;
            switch (e)
            {
                case ObjectCreationExpressionSyntax oc when oc.Type.ToString() == "Entry": args = oc.ArgumentList; kind = "scalar"; break;
                case ImplicitObjectCreationExpressionSyntax io when io.Parent?.Parent is InitializerExpressionSyntax: args = io.ArgumentList; kind = "scalar"; break;
                case InvocationExpressionSyntax inv when inv.Expression.ToString() is "Entry.FloatArray" or "Entry.IntArray":
                    args = inv.ArgumentList; kind = inv.Expression.ToString() == "Entry.FloatArray" ? "floatArray" : "intArray"; break;
                default: continue;
            }
            if (args == null || args.Arguments.Count < 4) continue;
            if (args.Arguments[0].Expression is not LiteralExpressionSyntax { Token.Value: string key }) continue;
            var unit = args.Arguments[1].Expression is LiteralExpressionSyntax { Token.Value: string u } ? u : "";
            if (args.Arguments.Any(a => a.NameColon?.Name.Identifier.Text == "flag")) kind = "flag";
            var getter = args.Arguments[2].Expression as ParenthesizedLambdaExpressionSyntax;
            var body = getter?.ExpressionBody;
            if (body is ConditionalExpressionSyntax ce) body = ce.Condition;
            var path = body?.ToString().Replace(" ", "") ?? "";
            if (Keys.ContainsKey(key)) { Problems.Add($"{key}: registered twice"); continue; }
            Keys[key] = new TunableKey { Key = key, Unit = unit, Kind = kind, Path = path, File = rel };
        }
    }

    private void ReadJson(string text)
    {
        using var doc = JsonDocument.Parse(text, new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
        foreach (var domain in doc.RootElement.EnumerateObject())
        {
            if (domain.Value.ValueKind != JsonValueKind.Object) continue;
            foreach (var owner in domain.Value.EnumerateObject())
            {
                if (owner.Value.ValueKind != JsonValueKind.Object) { Problems.Add($"json {domain.Name}.{owner.Name}: not an object"); continue; }
                foreach (var name in owner.Value.EnumerateObject())
                {
                    var v = name.Value;
                    if (v.ValueKind == JsonValueKind.Object && v.TryGetProperty("value", out var inner)) v = inner;
                    Json[$"{domain.Name}.{owner.Name}.{name.Name}"] = v.Clone();
                }
            }
        }
    }

    /// <summary>(b): the field default equals the JSON value (as SimTunables.Apply casts it). Null when equal.</summary>
    public string? CompareJson(TunableKey k)
    {
        if (!Json.TryGetValue(k.Key, out var j)) return "missing in tunables.json";
        var f = k.Field;
        if (f == null) return "no field";
        if (f.ArrayDefault != null)
        {
            if (j.ValueKind != JsonValueKind.Array) return "json is not an array";
            var arr = j.EnumerateArray().Select(x => x.GetDouble()).ToList();
            if (arr.Count != f.ArrayDefault.Count) return $"array length {arr.Count} vs {f.ArrayDefault.Count}";
            for (var i = 0; i < arr.Count; i++)
                if (!f.ArrayDefault[i].EqualsJson(arr[i])) return $"element {i}: json {arr[i]} vs default {f.ArrayDefault[i]}";
            return null;
        }
        if (f.Default == null) return $"default is not a literal ({f.InitText})";
        if (j.ValueKind is JsonValueKind.True or JsonValueKind.False)
            return f.Default.Value.Type == "bool" && (bool)f.Default.Value.Value == (j.ValueKind == JsonValueKind.True) ? null : $"json {j} vs default {f.Default}";
        if (j.ValueKind != JsonValueKind.Number) return "json value is not a number";
        var d = j.GetDouble();
        if (!f.Default.Value.EqualsJson(d)) return $"json {j.GetRawText()} vs default {f.Default}";
        if (f.Default.Value.Type is "int" or "long" or "uint" && j.GetRawText().Contains('.')) return null; // 4.0 for an int: same value, lane B style
        return null;
    }
}

/// <summary>Text edits on tunables.json that keep its comments and layout (JSONC).</summary>
internal sealed class JsoncDoc
{
    public sealed class Node
    {
        public string Key = "";
        public int KeyStart, ValueStart, ValueEnd; // ValueEnd exclusive
        public bool IsObject;
        public int Close;                          // index of '}' for an object
        public readonly List<Node> Children = new();
    }

    public string Text;
    public Node Root = null!;
    private int _i;

    public JsoncDoc(string text)
    {
        Text = text;
        Reparse();
    }

    public void Reparse()
    {
        _i = 0;
        Skip();
        Root = new Node { ValueStart = _i };
        ParseValue(Root);
    }

    private void Skip()
    {
        while (_i < Text.Length)
        {
            if (char.IsWhiteSpace(Text[_i])) _i++;
            else if (Text[_i] == '/' && _i + 1 < Text.Length && Text[_i + 1] == '/') { while (_i < Text.Length && Text[_i] != '\n') _i++; }
            else if (Text[_i] == '/' && _i + 1 < Text.Length && Text[_i + 1] == '*') { _i = Text.IndexOf("*/", _i + 2, StringComparison.Ordinal) + 2; }
            else break;
        }
    }

    private string ReadString()
    {
        var sb = new StringBuilder();
        _i++; // opening quote
        while (Text[_i] != '"')
        {
            if (Text[_i] == '\\') { sb.Append(Text[_i + 1]); _i += 2; continue; }
            sb.Append(Text[_i++]);
        }
        _i++;
        return sb.ToString();
    }

    private void ParseValue(Node n)
    {
        n.ValueStart = _i;
        var c = Text[_i];
        if (c == '{')
        {
            n.IsObject = true;
            _i++;
            Skip();
            while (Text[_i] != '}')
            {
                var child = new Node { KeyStart = _i, Key = ReadString() };
                Skip();
                if (Text[_i] != ':') throw new FormatException("tunables.json: ':' expected at " + _i);
                _i++;
                Skip();
                ParseValue(child);
                n.Children.Add(child);
                Skip();
                if (Text[_i] == ',') { _i++; Skip(); }
            }
            n.Close = _i;
            _i++;
        }
        else if (c == '[')
        {
            _i++;
            Skip();
            while (Text[_i] != ']')
            {
                ParseValue(new Node());
                Skip();
                if (Text[_i] == ',') { _i++; Skip(); }
            }
            _i++;
        }
        else if (c == '"') ReadString();
        else
        {
            while (_i < Text.Length && !",}] \t\r\n/".Contains(Text[_i])) _i++;
        }
        n.ValueEnd = _i;
    }

    private string IndentOf(int pos)
    {
        var lineStart = Text.LastIndexOf('\n', Math.Max(0, pos - 1)) + 1;
        var k = lineStart;
        while (k < Text.Length && (Text[k] == ' ' || Text[k] == '\t')) k++;
        return Text[lineStart..k];
    }

    private string Nl => Text.Contains("\r\n") ? "\r\n" : "\n";

    public bool Has(string key) => Find(key.Split('.')) != null;

    private Node? Find(string[] parts)
    {
        var n = Root;
        foreach (var p in parts)
        {
            n = n.Children.FirstOrDefault(c => c.Key == p);
            if (n == null) return null;
        }
        return n;
    }

    /// <summary>Adds domain.owner.name = entryJson (one line), creating the owner / domain objects as needed.</summary>
    public void Add(string key, string entryJson)
    {
        var parts = key.Split('.');
        if (parts.Length != 3) throw new ArgumentException("key must be domain.owner.name: " + key);
        if (Find(parts) != null) throw new InvalidOperationException("tunables.json already has " + key);
        var nl = Nl;
        var domain = Find(parts[..1]);
        var owner = domain == null ? null : Find(parts[..2]);
        string insert;
        Node parent;
        if (owner != null)
        {
            parent = owner;
            var ind = owner.Children.Count > 0 ? IndentOf(owner.Children[0].KeyStart) : IndentOf(owner.KeyStart) + "  ";
            insert = $"\"{parts[2]}\": {entryJson}";
            InsertMember(parent, ind, insert, nl);
        }
        else if (domain != null)
        {
            parent = domain;
            var ind = domain.Children.Count > 0 ? IndentOf(domain.Children[0].KeyStart) : IndentOf(domain.KeyStart) + "  ";
            insert = $"\"{parts[1]}\": {{{nl}{ind}  \"{parts[2]}\": {entryJson}{nl}{ind}}}";
            InsertMember(parent, ind, insert, nl);
        }
        else
        {
            parent = Root;
            var ind = Root.Children.Count > 0 ? IndentOf(Root.Children[0].KeyStart) : "  ";
            insert = $"\"{parts[0]}\": {{{nl}{ind}  \"{parts[1]}\": {{{nl}{ind}    \"{parts[2]}\": {entryJson}{nl}{ind}  }}{nl}{ind}}}";
            InsertMember(parent, ind, insert, nl);
        }
        Reparse();
    }

    private void InsertMember(Node parent, string indent, string member, string nl)
    {
        if (parent.Children.Count == 0)
        {
            var closeIndent = IndentOf(parent.Close);
            Text = Text[..(parent.ValueStart + 1)] + nl + indent + member + nl + closeIndent + Text[parent.Close..];
            return;
        }
        var last = parent.Children[^1];
        Text = Text[..last.ValueEnd] + "," + nl + indent + member + Text[last.ValueEnd..];
    }
}

/// <summary>
/// The generated files SimTunables.Pack2.&lt;Domain&gt;.cs: the pack-2 fields (domain → owner → name) and their Entry array,
/// regenerated from what they already hold plus the new keys.
/// </summary>
internal static class Pack2Files
{
    public static readonly string[] Domains = { "weapons", "vehicles", "bosses", "bases", "modes", "ai", "campaign", "maps" };

    public sealed class Field
    {
        public string Key = "", Unit = "", Kind = "", Was = "", Note = "", Type = "", Literal = "";
        public string Owner => Syn.Pascal(Key.Split('.')[1]);
        public string Name => Syn.Pascal(Key.Split('.')[2]);
        public string Path => Syn.KeyToPath(Key);
    }

    /// <summary>"Pack2" (pass 1 files) or "Pass2" (pack 2 pass 2, 09/10: SimTunables.Pass2.&lt;Domain&gt;.cs, arrays Pass2&lt;Domain&gt;).</summary>
    public static string Prefix = "Pack2";

    public static string FileOf(string domain) => $"{Repo.ContentDir}/SimTunables.{Prefix}.{Syn.Pascal(domain)}.cs";

    private static readonly Regex DocRx = new(@"^(\S+) \(([^;]*); ([^,]*), was (.*?)\)\.(?: (.*))?$");

    public static List<Field> Read(string domain)
    {
        var list = new List<Field>();
        var rel = FileOf(domain);
        if (!File.Exists(Repo.Abs(rel))) return list;
        var root = CSharpSyntaxTree.ParseText(Repo.ReadText(rel), Compiler.SimParse).GetRoot();
        foreach (var fd in root.DescendantNodes().OfType<FieldDeclarationSyntax>())
        {
            if (fd.Declaration.Type.ToString() == "Entry[]") continue;
            var doc = Registry.DocSummary(fd);
            var m = DocRx.Match(doc);
            if (!m.Success) throw new FormatException($"{rel}: unreadable summary '{doc}'");
            var v = fd.Declaration.Variables[0];
            list.Add(new Field
            {
                Key = m.Groups[1].Value, Unit = m.Groups[2].Value, Kind = m.Groups[3].Value, Was = m.Groups[4].Value, Note = m.Groups[5].Value,
                Type = fd.Declaration.Type.ToString(), Literal = v.Initializer!.Value.ToString(),
            });
        }
        return list;
    }

    public static string Generate(string domain, List<Field> fields)
    {
        var D = Syn.Pascal(domain);
        var sb = new StringBuilder();
        if (Prefix == "Pass2")
        {
            sb.Append("// Generated by Tools/export/literal_to_tunable.py (mbconst move), balance pack 2 pass 2 (09/10). Each field is a\n");
            sb.Append("// literal that was in the code (\"was\": where); the defaults equal those literals (a negative literal keeps its sign).\n");
            sb.Append("// Edit Resources/Data/tunables.json, not this file.\n");
        }
        else
        {
            sb.Append("// Generated by Tools/export/mbconst (move), balance pack 2. Each field is a literal that was in the code (\"was\":\n");
            sb.Append("// where); the defaults equal those literals. Edit Resources/Data/tunables.json, not this file.\n");
        }
        sb.Append("#nullable enable\n\nnamespace MachineBrigade.Sim.Content\n{\n    public static partial class SimTunables\n    {\n");
        sb.Append($"        public static partial class {D}\n        {{\n");
        var owners = fields.GroupBy(f => f.Owner).OrderBy(g => g.Key, StringComparer.Ordinal).ToList();
        for (var oi = 0; oi < owners.Count; oi++)
        {
            sb.Append($"            public static partial class {owners[oi].Key}\n            {{\n");
            foreach (var f in owners[oi])
            {
                var note = f.Note == "" ? "" : " " + Esc(f.Note);
                sb.Append($"                /// <summary>{f.Key} ({f.Unit}; {f.Kind}, was {Esc(f.Was)}).{note}</summary>\n");
                sb.Append($"                public static {f.Type} {f.Name} = {f.Literal};\n");
            }
            sb.Append("            }\n");
            if (oi < owners.Count - 1) sb.Append('\n');
        }
        sb.Append("        }\n\n");
        sb.Append($"        private static readonly Entry[] {Prefix}{D} =\n        {{\n");
        foreach (var f in fields.OrderBy(f => f.Owner, StringComparer.Ordinal))
        {
            var tv = new TypedValue(f.Type, 0);
            sb.Append($"            new Entry(\"{f.Key}\", \"{f.Unit}\", () => {f.Path}, {tv.SetterCast(f.Path)}),\n");
        }
        sb.Append("        };\n    }\n}\n");
        return sb.ToString();
    }

    /// <summary>Writes the domain file (and its Unity .meta with a fresh guid when the file is new).</summary>
    public static void Write(string domain, List<Field> fields)
    {
        var rel = FileOf(domain);
        var meta = Repo.Abs(rel + ".meta");
        Repo.WriteText(rel, Generate(domain, fields));
        if (!File.Exists(meta)) File.WriteAllText(meta, "fileFormatVersion: 2\nguid: " + Guid.NewGuid().ToString("N") + "\n");
    }

    private static string Esc(string s) => s.Replace("<", "&lt;").Replace(">", "&gt;").Replace("\n", " ");
}

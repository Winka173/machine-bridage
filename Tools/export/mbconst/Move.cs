using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>
/// literal_to_tunable (§2.1): for each row (file, line, literal, key, ...) replace the literal with a SimTunables field
/// read, add the field (default = the literal, same type and suffix) to SimTunables.Pack2.&lt;Domain&gt;.cs and the key to
/// tunables.json (value = the literal). Rows the tool cannot do safely are refused with the reason (left for a manual edit).
/// </summary>
internal static class Move
{
    public sealed class Row
    {
        public string File = "", Literal = "", Key = "", Unit = "", Kind = "", LinhVuc = "", Mode = "", Note = "";
        public int Line, Occurrence, Col;
        public int CsvLine;
    }

    private sealed class Plan
    {
        public Row Row = null!;
        public TypedValue Value;
        public int Start, Length;   // span replaced in the file
        public string Replacement = "";
        public string How = "";      // inline | const_to_property | static_to_property | local_const | static_init_inline
        public bool Signed;          // pass 2: "-lit" replaced whole, the key holds the negative value
        public List<(int Start, int Length, string Text)> Extra = new(); // pass 2: further edits of the same move (param_default_nullable)
    }

    /// <summary>Pass 2 (09/10): also replace literals inside static field initializers (tables, expressions), read once at type init.</summary>
    public static bool StaticInit;
    /// <summary>Pass 2 (09/10): a negated literal "-x" is replaced whole and its key holds -x (the data shows the value the code uses).</summary>
    public static bool SignedInline;
    /// <summary>
    /// Pass 2 (09/10): a parameter default "T x = lit" becomes "T? x = null" and every read of x in the body "(x ?? field)":
    /// a call without the argument reads the field (= lit), a call with it reads its value; named arguments keep working.
    /// </summary>
    public static bool ParamDefaults;

    public static int Run(string[] args)
    {
        string? csv = null;
        var dry = false;
        for (var i = 0; i < args.Length; i++)
        {
            if (args[i] == "--csv") csv = args[++i];
            else if (args[i] == "--dry-run") dry = true;
            else if (args[i] == "--repo") Repo.Root = args[++i];
            else if (args[i] == "--static-init") StaticInit = true;
            else if (args[i] == "--signed") SignedInline = true;
            else if (args[i] == "--param-defaults") ParamDefaults = true;
            else if (args[i] == "--fileset") Pack2Files.Prefix = args[++i] switch { "pass2" => "Pass2", _ => "Pack2" };
            else csv ??= args[i];
        }
        if (csv == null) { Console.Error.WriteLine("usage: mbconst move --csv <moves.csv> [--dry-run]"); return 2; }
        var rows = ReadCsv(csv);
        var wt = SourceSet.FromWorktree();
        var reg = Registry.Load(wt);
        var errors = new List<string>();
        var plans = new List<Plan>();
        var trees = new Dictionary<string, SyntaxTree>();

        var manual = rows.Where(r => r.Mode.StartsWith("manual")).ToList();
        foreach (var m in manual) Console.WriteLine($"skip (manual) csv:{m.CsvLine} {m.File}:{m.Line} {m.Literal}: {m.Mode}");
        foreach (var row in rows.Where(r => !r.Mode.StartsWith("manual")))
        {
            var rel = Repo.Rel(row.File);
            if (!wt.Files.TryGetValue(rel, out var text)) { errors.Add($"csv:{row.CsvLine} {row.File}: no such C# file"); continue; }
            if (Registry.IsTunablesFile(rel)) { errors.Add($"csv:{row.CsvLine}: {rel} is a SimTunables file"); continue; }
            if (!trees.TryGetValue(rel, out var tree))
                trees[rel] = tree = CSharpSyntaxTree.ParseText(text, rel.Contains("/Sim/") ? Compiler.SimParse : Compiler.GameParse, rel);
            var err = PlanRow(row, rel, tree, trees, wt, out var plan);
            if (err != null) { errors.Add($"csv:{row.CsvLine} {Repo.Short(rel)}:{row.Line} {row.Literal} -> {row.Key}: {err}"); continue; }
            plans.Add(plan!);
        }

        // rule (c): one key, one literal; an existing key keeps its default
        var newFields = new Dictionary<string, Pack2Files.Field>(StringComparer.Ordinal);
        foreach (var g in plans.GroupBy(p => p.Row.Key))
        {
            var values = g.Select(p => p.Value).Distinct().ToList();
            if (values.Count > 1) { errors.Add($"{g.Key}: two different literals ({string.Join(", ", values)}) -> two keys needed"); continue; }
            var v = values[0];
            if (reg.Keys.TryGetValue(g.Key, out var existing))
            {
                var d = existing.Field?.Default;
                if (d == null || !d.Value.SameAs(v)) errors.Add($"{g.Key}: exists with default {d?.ToString() ?? existing.Field?.InitText} (literal {v})");
                continue; // reuse: only the call sites change
            }
            var parts = g.Key.Split('.');
            if (parts.Length != 3 || !Pack2Files.Domains.Contains(parts[0])) { errors.Add($"{g.Key}: key must be <domain>.<owner>.<name>, domain one of {string.Join('/', Pack2Files.Domains)}"); continue; }
            if (parts.Any(p => p.Length == 0 || !SyntaxFacts.IsValidIdentifier(Syn.Pascal(p)))) { errors.Add($"{g.Key}: not an identifier path"); continue; }
            if (reg.Fields.ContainsKey(Syn.KeyToPath(g.Key))) { errors.Add($"{g.Key}: field {Syn.KeyToPath(g.Key)} exists under another key"); continue; }
            newFields[g.Key] = new Pack2Files.Field
            {
                Key = g.Key, Unit = Pick(g.Select(p => p.Row.Unit), "x"), Kind = Pick(g.Select(p => p.Row.Kind), "khac"),
                Note = Pick(g.Select(p => p.Row.Note), ""), Type = v.Type, Literal = LiteralText(g.First()),
                Was = string.Join(", ", g.Select(p => $"{Repo.Short(Repo.Rel(p.Row.File))}:{p.Row.Line}").Distinct()),
            };
        }

        if (errors.Count > 0)
        {
            Console.Error.WriteLine($"move: {errors.Count} row(s) refused (nothing written):");
            foreach (var e in errors) Console.Error.WriteLine("  " + e);
            return 1;
        }

        // the code edits, from the end of each file
        foreach (var g in plans.GroupBy(p => Repo.Rel(p.Row.File)))
        {
            var text = wt.Files[g.Key];
            var spans = g.OrderByDescending(p => p.Start).ToList();
            var edits = g.SelectMany(p => p.Extra.Select(e => (e.Start, e.Length, e.Text, p.Row.Line)).Prepend((p.Start, p.Length, p.Replacement, p.Row.Line)))
                .OrderByDescending(e => e.Item1).ToList();
            for (var i = 1; i < edits.Count; i++)
                if (edits[i].Item1 + edits[i].Item2 > edits[i - 1].Item1) throw new InvalidOperationException($"{g.Key}: overlapping edits at {edits[i].Item4}");
            var sb = new StringBuilder(text);
            foreach (var e in edits) sb.Remove(e.Item1, e.Item2).Insert(e.Item1, e.Item3);
            Console.WriteLine($"{Repo.Short(g.Key)}: {spans.Count} literal(s) -> SimTunables ({string.Join(", ", spans.Select(s => s.How).Distinct())})");
            if (!dry) Repo.WriteText(g.Key, sb.ToString());
        }

        // the generated fields and tunables.json
        var json = new JsoncDoc(wt.TunablesJson ?? throw new InvalidOperationException("no tunables.json"));
        foreach (var dg in newFields.Values.GroupBy(f => f.Key.Split('.')[0]))
        {
            var all = Pack2Files.Read(dg.Key);
            all.AddRange(dg);
            if (!dry) Pack2Files.Write(dg.Key, all);
            foreach (var f in dg)
            {
                var row = plans.First(p => p.Row.Key == f.Key);
                var code = Path.GetFileNameWithoutExtension(Repo.Short(Repo.Rel(row.Row.File))).Split('.')[0];
                var entry = $"{{ \"value\": {row.Value.JsonText()}, \"unit\": \"{f.Unit}\", \"kind\": \"{f.Kind}\", \"linh_vuc\": \"{Pick(new[] { row.Row.LinhVuc }, DomainNumber(f.Key))}\", \"code\": \"{code} ({(Pack2Files.Prefix == "Pass2" ? "pack 2 pass 2" : "pack 2")}, was {f.Was.Split(',')[0]})\" }}";
                json.Add(f.Key, entry);
            }
            Console.WriteLine($"SimTunables.{Pack2Files.Prefix}.{Syn.Pascal(dg.Key)}.cs: +{dg.Count()} field(s)");
        }
        if (!dry && newFields.Count > 0) Repo.WriteText(Repo.TunablesJson, json.Text);
        Console.WriteLine($"move: {plans.Count} literal(s), {newFields.Count} new key(s){(dry ? " (dry run, nothing written)" : "")}. Next: mbconst check --base HEAD");
        return 0;
    }

    private static string Pick(IEnumerable<string> xs, string fallback) => xs.FirstOrDefault(x => !string.IsNullOrWhiteSpace(x)) ?? fallback;

    public static string DomainNumber(string key) => key.Split('.')[0] switch
    {
        "weapons" => "01", "vehicles" => "02", "bosses" => "03", "bases" => "04", "modes" => "05", "ai" => "06", "campaign" => "07", "maps" => "08", _ => "",
    };

    /// <summary>The field initializer: the literal token exactly as written (suffix kept; a minus sign stays in the code).</summary>
    private static string LiteralText(Plan p) => (p.Signed ? "-" : "") + p.Row.Literal.TrimStart('-');

    private static string? PlanRow(Row row, string rel, SyntaxTree tree, Dictionary<string, SyntaxTree> trees, SourceSet wt, out Plan? plan)
    {
        plan = null;
        var text = tree.GetText();
        if (row.Line < 1 || row.Line > text.Lines.Count) return "line out of range";
        var span = text.Lines[row.Line - 1].Span;
        var root = tree.GetRoot();
        var lit = row.Literal.TrimStart('-');
        var tokens = root.DescendantTokens(span).Where(t => t.IsKind(SyntaxKind.NumericLiteralToken) && t.Text == lit && span.Contains(t.Span)).ToList();
        if (tokens.Count == 0) return "literal not found on that line";
        SyntaxToken tok;
        if (row.Col > 0)
        {
            // pass 2: the column (1-based, of the literal token itself) names the token exactly
            var atCol = tokens.Where(t => t.GetLocation().GetLineSpan().StartLinePosition.Character + 1 == row.Col).ToList();
            if (atCol.Count != 1) return $"no {lit} token at column {row.Col}";
            tok = atCol[0];
        }
        else
        {
            if (tokens.Count > 1 && row.Occurrence == 0) return $"literal appears {tokens.Count} times on the line: give the occurrence column";
            var occ = row.Occurrence == 0 ? 1 : row.Occurrence;
            if (occ > tokens.Count) return "occurrence out of range";
            tok = tokens[occ - 1];
        }
        var litNode = (LiteralExpressionSyntax)tok.Parent!;
        var tv = TypedValue.FromToken(tok)!.Value;
        if (tv.Type is "decimal" or "ulong") return $"type {tv.Type} has no SimTunables entry type";
        var chain = Syn.Qualifier + Syn.KeyToPath(row.Key);

        var cc = Syn.ConstantContext(litNode);
        if (cc == "parameter default" && ParamDefaults) return PlanParamDefault(row, tv, tok, litNode, chain, out plan);
        if (cc != null) return $"constant context ({cc}): manual";

        // implicit constant narrowing (byte b = 3) would no longer compile
        if (tv.Type == "int" && litNode.Parent is EqualsValueClauseSyntax { Parent: VariableDeclaratorSyntax { Parent: VariableDeclarationSyntax vd } }
            && vd.Type.ToString() is "byte" or "sbyte" or "short" or "ushort" or "char" or "uint" or "ulong")
            return $"int literal narrowed to {vd.Type}: manual";

        // where the literal sits
        var field = litNode.Ancestors().TakeWhile(a => a is not AnonymousFunctionExpressionSyntax).OfType<FieldDeclarationSyntax>().FirstOrDefault();
        var local = litNode.Ancestors().TakeWhile(a => a is not AnonymousFunctionExpressionSyntax).OfType<LocalDeclarationStatementSyntax>().FirstOrDefault();
        var prop = litNode.Ancestors().TakeWhile(a => a is not AnonymousFunctionExpressionSyntax and not AccessorDeclarationSyntax and not ArrowExpressionClauseSyntax)
            .OfType<PropertyDeclarationSyntax>().FirstOrDefault();
        var negated = litNode.Parent is PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression };
        var whole = negated ? (ExpressionSyntax)litNode.Parent! : litNode;

        if (field != null && (field.Modifiers.Any(SyntaxKind.ConstKeyword) || field.Modifiers.Any(SyntaxKind.StaticKeyword)))
        {
            var isConst = field.Modifiers.Any(SyntaxKind.ConstKeyword);
            if (field.Declaration.Variables.Count != 1) return "field declares several variables: manual";
            var v = field.Declaration.Variables[0];
            if (v.Initializer?.Value != whole)
            {
                if (!isConst && StaticInit && field.Modifiers.Any(SyntaxKind.ReadOnlyKeyword))
                    return PlanInline(row, tv, tok, litNode, negated, chain, "static_init_inline", out plan);
                return (isConst ? "const" : "static") + " field initializer is an expression, not the literal alone: manual" +
                       (field.Declaration.Type is ArrayTypeSyntax ? " (array table)" : "");
            }
            var name = v.Identifier.Text;
            if (isConst)
            {
                var use = ConstantUse(name, trees.Values.Concat(OtherTrees(wt, trees)));
                if (use != null) return $"const {name} is used in a constant context ({use}): manual";
            }
            else if (Assigned(name, trees.Values.Concat(OtherTrees(wt, trees)))) return $"static field {name} is assigned somewhere: manual";
            var mods = field.Modifiers.Where(m => !m.IsKind(SyntaxKind.ConstKeyword) && !m.IsKind(SyntaxKind.ReadOnlyKeyword)).Select(m => m.Text).ToList();
            if (!mods.Contains("static")) mods.Add("static");
            var minus = negated ? "-" : "";
            var decl = $"{string.Join(' ', mods)} {field.Declaration.Type} {name} => {minus}{chain};";
            var start = field.Modifiers.Count > 0 ? field.Modifiers[0].SpanStart : field.Declaration.SpanStart;
            plan = new Plan { Row = row, Value = tv, Start = start, Length = field.Span.End - start, Replacement = decl, How = isConst ? "const_to_property" : "static_to_property" };
            return null;
        }
        if (prop != null && prop.Initializer != null && prop.Initializer.Value.Span.Contains(litNode.Span) && prop.Modifiers.Any(SyntaxKind.StaticKeyword))
            return "static property initializer (runs before the data loads): manual";
        if (field != null && field.Declaration.Type is ArrayTypeSyntax && field.Modifiers.Any(SyntaxKind.StaticKeyword))
        {
            if (StaticInit && field.Modifiers.Any(SyntaxKind.ReadOnlyKeyword)) return PlanInline(row, tv, tok, litNode, negated, chain, "static_init_inline", out plan);
            return "static array table: manual (FloatArray / IntArray entry)";
        }
        if (local != null && local.IsConst)
        {
            if (local.Declaration.Variables.Count != 1) return "const local declares several variables: manual";
            var v = local.Declaration.Variables[0];
            if (v.Initializer?.Value != whole) return "const local initializer is an expression: manual";
            var body = local.Ancestors().FirstOrDefault(a => a is BaseMethodDeclarationSyntax or AccessorDeclarationSyntax or LocalFunctionStatementSyntax or PropertyDeclarationSyntax) ?? root;
            var use = ConstantUse(v.Identifier.Text, new[] { body.SyntaxTree }, body);
            if (use != null) return $"const local {v.Identifier.Text} is used in a constant context ({use}): manual";
            var minus = negated ? "-" : "";
            var constTok = local.Modifiers.First(m => m.IsKind(SyntaxKind.ConstKeyword));
            // "const float r = 10f;" -> "float r = <chain>;": one edit over the statement
            var newText = local.ToString().Remove(constTok.SpanStart - local.SpanStart, constTok.Span.Length + 1);
            var initStart = newText.LastIndexOf('=');
            newText = newText[..(initStart + 1)] + " " + minus + chain + ";";
            plan = new Plan { Row = row, Value = tv, Start = local.SpanStart, Length = local.Span.Length, Replacement = newText, How = "local_const" };
            return null;
        }
        if (field != null && !field.Modifiers.Any(SyntaxKind.StaticKeyword) && litNode.Ancestors().Any(a => a is TypeDeclarationSyntax { } td && td.Modifiers.Any(SyntaxKind.StaticKeyword)))
            return "field of a static class: manual";
        if (litNode.Ancestors().Any(a => a is InterpolationAlignmentClauseSyntax or InterpolationFormatClauseSyntax)) return "string format alignment: manual";
        return PlanInline(row, tv, tok, litNode, negated, chain, "inline", out plan);
    }

    /// <summary>"T x = lit" -> "T? x = null" and each read of x in the body -> "(x ?? field)" (see <see cref="ParamDefaults"/>).</summary>
    private static string? PlanParamDefault(Row row, TypedValue tv, SyntaxToken tok, LiteralExpressionSyntax litNode, string chain, out Plan? plan)
    {
        plan = null;
        var negated = litNode.Parent is PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression };
        var whole = negated ? (ExpressionSyntax)litNode.Parent! : litNode;
        if (whole.Parent is not EqualsValueClauseSyntax { Parent: ParameterSyntax par } || par.Type is not PredefinedTypeSyntax pt)
            return "parameter default: not 'T x = literal' with a built-in T: manual";
        if (pt.Keyword.Kind() is not (SyntaxKind.FloatKeyword or SyntaxKind.IntKeyword or SyntaxKind.DoubleKeyword or SyntaxKind.LongKeyword))
            return $"parameter default of type {pt}: manual";
        if (par.Modifiers.Count > 0) return "parameter default with a modifier (ref / in / out / params / this): manual";
        if (par.Parent?.Parent is not BaseMethodDeclarationSyntax member) return "parameter default outside a method / constructor: manual";
        var body = (SyntaxNode?)member.Body ?? member.ExpressionBody;
        if (body == null) return "parameter default of a member without a body: manual";
        var name = par.Identifier.Text;
        var type = member.Parent as TypeDeclarationSyntax;
        var memberName = member switch { MethodDeclarationSyntax m => m.Identifier.Text, ConstructorDeclarationSyntax c => c.Identifier.Text, _ => "" };
        if (memberName == "") return "parameter default of an operator / destructor: manual";
        var count = member.ParameterList.Parameters.Count;
        if (type != null && type.Members.OfType<BaseMethodDeclarationSyntax>().Count(m => m != member && m.ParameterList.Parameters.Count == count
                && (m switch { MethodDeclarationSyntax mm => mm.Identifier.Text, ConstructorDeclarationSyntax cc => cc.Identifier.Text, _ => "" }) == memberName) > 0)
            return "an overload with as many parameters exists (T -> T? could change overload resolution): manual";
        var uses = body.DescendantNodes().OfType<IdentifierNameSyntax>().Where(i => i.Identifier.Text == name).ToList();
        var edits = new List<(int, int, string)>();
        foreach (var id in uses)
        {
            if (id.Parent is MemberAccessExpressionSyntax ma && ma.Name == id) continue; // other.x
            if (id.Parent is NameColonSyntax or NameEqualsSyntax) continue;
            if (id.Ancestors().OfType<InvocationExpressionSyntax>().Any(inv => inv.Expression is IdentifierNameSyntax { Identifier.Text: "nameof" })) continue;
            if (id.Ancestors().Any(a => a is AnonymousFunctionExpressionSyntax af && af.ChildNodes().OfType<ParameterSyntax>().Any(pp => pp.Identifier.Text == name)
                                        || a is ParenthesizedLambdaExpressionSyntax pl && pl.ParameterList.Parameters.Any(pp => pp.Identifier.Text == name)
                                        || a is LocalFunctionStatementSyntax lf && lf.ParameterList.Parameters.Any(pp => pp.Identifier.Text == name)))
                return $"parameter {name} is shadowed in the body: manual";
            if (id.Parent is AssignmentExpressionSyntax asg && asg.Left == id || id.Parent is PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.PreIncrementExpression or (int)SyntaxKind.PreDecrementExpression }
                || id.Parent is PostfixUnaryExpressionSyntax || id.Parent is ArgumentSyntax a2 && !a2.RefKindKeyword.IsKind(SyntaxKind.None))
                return $"parameter {name} is assigned or passed by reference in the body: manual";
            edits.Add((id.SpanStart, id.Span.Length, $"({name} ?? {chain})"));
        }
        var value = negated ? TypedValue.FromToken(tok, negate: true)!.Value : tv;
        // the parameter: "T x = lit" -> "T? x = null"
        edits.Add((par.Type.Span.End, 0, "?"));
        plan = new Plan
        {
            Row = row, Value = value, Start = whole.SpanStart, Length = whole.Span.Length, Replacement = "null", How = "param_default_nullable",
            Signed = negated, Extra = edits,
        };
        return null;
    }

    /// <summary>The literal token (or, with --signed, the whole "-lit") replaced by the field read.</summary>
    private static string? PlanInline(Row row, TypedValue tv, SyntaxToken tok, LiteralExpressionSyntax litNode, bool negated, string chain, string how, out Plan? plan)
    {
        if (negated && SignedInline)
        {
            var neg = (PrefixUnaryExpressionSyntax)litNode.Parent!;
            var nv = TypedValue.FromToken(tok, negate: true)!.Value;
            plan = new Plan { Row = row, Value = nv, Start = neg.SpanStart, Length = neg.Span.End - neg.SpanStart, Replacement = chain, How = how, Signed = true };
            return null;
        }
        plan = new Plan { Row = row, Value = tv, Start = tok.SpanStart, Length = tok.Span.Length, Replacement = chain, How = how };
        return null;
    }

    private static IEnumerable<SyntaxTree> OtherTrees(SourceSet wt, Dictionary<string, SyntaxTree> parsed)
    {
        foreach (var (rel, text) in wt.Files)
            if (!parsed.ContainsKey(rel) && (rel.Contains("/Sim/") || rel.Contains("/Game/")))
                yield return CSharpSyntaxTree.ParseText(text, rel.Contains("/Sim/") ? Compiler.SimParse : Compiler.GameParse, rel);
    }

    /// <summary>Is this name used where C# needs a constant (case label, pattern, attribute, parameter default, const initializer)?</summary>
    public static string? ConstantUse(string name, IEnumerable<SyntaxTree> trees, SyntaxNode? within = null)
    {
        foreach (var t in trees)
        {
            var root = within ?? t.GetRoot();
            if (!root.ToString().Contains(name, StringComparison.Ordinal)) continue;
            foreach (var id in root.DescendantNodes().OfType<IdentifierNameSyntax>().Where(i => i.Identifier.Text == name))
            {
                var cc = Syn.ConstantContext(id);
                if (cc != null) return $"{cc} at {Repo.Short(t.FilePath)}:{Syn.Line(id)}";
                var constDecl = id.Ancestors().FirstOrDefault(a => a is FieldDeclarationSyntax f && f.Modifiers.Any(SyntaxKind.ConstKeyword)
                                                                    || a is LocalDeclarationStatementSyntax l && l.IsConst);
                if (constDecl != null) return $"const initializer at {Repo.Short(t.FilePath)}:{Syn.Line(id)}";
            }
        }
        return null;
    }

    private static bool Assigned(string name, IEnumerable<SyntaxTree> trees)
    {
        foreach (var t in trees)
        {
            var root = t.GetRoot();
            if (!root.ToString().Contains(name, StringComparison.Ordinal)) continue;
            foreach (var id in root.DescendantNodes().OfType<IdentifierNameSyntax>().Where(i => i.Identifier.Text == name))
            {
                SyntaxNode n = id.Parent is MemberAccessExpressionSyntax ma && ma.Name == id ? ma : id;
                if (n.Parent is AssignmentExpressionSyntax a && a.Left == n) return true;
                if (n.Parent is PrefixUnaryExpressionSyntax or PostfixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.PostIncrementExpression or (int)SyntaxKind.PostDecrementExpression }
                    && n.Parent.Kind() is SyntaxKind.PreIncrementExpression or SyntaxKind.PreDecrementExpression or SyntaxKind.PostIncrementExpression or SyntaxKind.PostDecrementExpression) return true;
                if (n.Parent is ArgumentSyntax arg && !arg.RefKindKeyword.IsKind(SyntaxKind.None) && !arg.RefKindKeyword.IsKind(SyntaxKind.InKeyword)) return true;
            }
        }
        return false;
    }

    public static List<Row> ReadCsv(string path)
    {
        var lines = File.ReadAllLines(path).ToList();
        if (lines.Count == 0) return new List<Row>();
        var head = Csv.Split(lines[0]).Select(h => h.Trim().ToLowerInvariant()).ToList();
        int Col(string n) => head.IndexOf(n);
        var rows = new List<Row>();
        for (var i = 1; i < lines.Count; i++)
        {
            if (string.IsNullOrWhiteSpace(lines[i]) || lines[i].StartsWith('#')) continue;
            var c = Csv.Split(lines[i]);
            string Get(string n) => Col(n) >= 0 && Col(n) < c.Count ? c[Col(n)].Trim() : "";
            rows.Add(new Row
            {
                File = Get("file"), Line = int.Parse(Get("line")), Literal = Get("literal"), Key = Get("key"), Unit = Get("unit"), Kind = Get("kind"),
                LinhVuc = Get("linh_vuc"), Occurrence = int.TryParse(Get("occurrence"), out var o) ? o : 0,
                Col = int.TryParse(Get("col"), out var cl) ? cl : 0, Mode = Get("mode"), Note = Get("note"), CsvLine = i + 1,
            });
        }
        return rows;
    }
}

internal static class Csv
{
    public static List<string> Split(string line)
    {
        var res = new List<string>();
        var sb = new StringBuilder();
        var q = false;
        for (var i = 0; i < line.Length; i++)
        {
            var ch = line[i];
            if (q)
            {
                if (ch == '"' && i + 1 < line.Length && line[i + 1] == '"') { sb.Append('"'); i++; }
                else if (ch == '"') q = false;
                else sb.Append(ch);
            }
            else if (ch == '"') q = true;
            else if (ch == ',') { res.Add(sb.ToString()); sb.Clear(); }
            else sb.Append(ch);
        }
        res.Add(sb.ToString());
        return res;
    }

    public static string Cell(object? o)
    {
        var s = o?.ToString() ?? "";
        return s.IndexOfAny(new[] { ',', '"', '\n', '\r' }) >= 0 ? "\"" + s.Replace("\"", "\"\"").Replace("\r", " ").Replace("\n", " ") + "\"" : s;
    }

    public static string Row(params object?[] cells) => string.Join(',', cells.Select(Cell));
}

using System.IO.Compression;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

internal static partial class Scan
{
    // ------------------------------------------------------------------------------------------------ classification

    private static Dictionary<string, HashSet<Graph.Member>> Readers(Compiler.Pair c, Graph g)
    {
        var map = new Dictionary<string, HashSet<Graph.Member>>(StringComparer.Ordinal);
        var gate = new object();
        Parallel.ForEach(c.Trees, kv =>
        {
            var model = c.Model(kv.Key)!;
            var local = new List<(string, Graph.Member)>();
            foreach (var id in kv.Value.GetRoot().DescendantNodes().OfType<IdentifierNameSyntax>())
            {
                SyntaxNode n = id.Parent is MemberAccessExpressionSyntax ma && ma.Name == id ? ma : id;
                if (n.Parent is MemberBindingExpressionSyntax) n = n.Parent;
                if (n.Parent is AssignmentExpressionSyntax a && a.Left == n && a.IsKind(SyntaxKind.SimpleAssignmentExpression)) continue; // a write
                ISymbol? s;
                try { s = model.GetSymbolInfo(id).Symbol; } catch { continue; }
                if (s is not (IFieldSymbol or IPropertySymbol)) continue;
                var owner = g.Owner(id, model);
                if (owner == null) continue;
                local.Add((Graph.Key(Graph.Norm(s)), owner));
            }
            lock (gate)
                foreach (var (s, o) in local)
                {
                    if (!map.TryGetValue(s, out var set)) map[s] = set = new HashSet<Graph.Member>();
                    set.Add(o);
                }
        });
        return map;
    }

    private static readonly Regex DataRead = new(@"^(Float|Int|Number|Double|Bool|Str|String|Long|Opt\w*|Get\w*|Read\w*|TryGet\w*)$", RegexOptions.Compiled);
    private static readonly Regex LogCall = new(@"^(Log\w*|Debug\w*|Note|Record|Trace|Journal\w*|Append)$", RegexOptions.Compiled);
    private static readonly Regex FormatCall = new(@"^(ToString|Format|Concat|Join|PadLeft|PadRight|AppendFormat)$", RegexOptions.Compiled);
    private static readonly Regex CapacityType = new(@"^(List|Dictionary|HashSet|Queue|Stack|StringBuilder|SortedSet|SortedDictionary|PriorityQueue)\b", RegexOptions.Compiled);
    private static readonly Regex AngleCtx = new(@"Deg|Rad|Angle|Pi\b|PI\b|Atan|Heading|Bearing|Yaw", RegexOptions.Compiled);

    private static void Classify(Compiler.Pair c, Graph g, List<Lit> lits)
    {
        var readers = Readers(c, g);
        foreach (var l in lits)
        {
            var (cls, reason) = ClassifyOne(c, g, readers, l);
            l.Class = cls;
            l.Reason = reason;
            var hay = l.LineText + " " + l.CtxName + " " + l.Member;
            l.Group = Category.FirstOrDefault(k => k.rx.IsMatch(hay)).group ?? "khac";
        }
    }

    private static (string, string) ClassifyOne(Compiler.Pair c, Graph g, Dictionary<string, HashSet<Graph.Member>> readers, Lit l)
    {
        var f = l.File;
        var node = l.Node;
        var abs = Math.Abs(l.Value);
        if (!l.Reachable)
        {
            if (ViewDirs.Any(f.StartsWith) || f.StartsWith("Editor/")) return ("visual", "not reachable from the simulation (view / UI / FX / audio / input code)");
            if (f.StartsWith("Game/")) return ("visual", "Game code not reachable from the simulation's entry points (menus, profile, shop, presentation)");
            if (f.Contains("BalancePackFacts") || f.Contains("HandbookFacts")) return ("infrastructure", "export / handbook facts (read by the doc export, not by the simulation)");
            return ("infrastructure", "Sim code not reachable from the simulation's entry points (helpers the view or the export call)");
        }
        switch (l.Context)
        {
            case "attribute": return ("infrastructure", "attribute argument");
            case "enum_value": return ("index", "enum value (an identifier, not a quantity)");
            case "case_label": return ("index", "switch case label (an identifier)");
            case "bitwise": return ("infrastructure", "bit operation (flags / hashing)");
            case "format": return ("visual", "text formatting");
        }
        if (l.Text.StartsWith("0x") || l.Text.StartsWith("0X")) return ("infrastructure", "hex constant (hash / bit mask)");
        var model = c.Model(Repo.Scripts + "/" + f)!;
        // the invocation the literal is an argument of
        var arg = node.Ancestors().TakeWhile(a => a is not StatementSyntax and not MemberDeclarationSyntax).OfType<ArgumentSyntax>().FirstOrDefault();
        var call = arg?.Parent?.Parent;
        var callName = call switch
        {
            InvocationExpressionSyntax inv => LastName(inv.Expression),
            ObjectCreationExpressionSyntax oc => oc.Type is GenericNameSyntax gn ? gn.Identifier.Text : oc.Type.ToString(),
            _ => "",
        };
        if (call is InvocationExpressionSyntax inv2 && DataRead.IsMatch(callName) && inv2.ArgumentList.Arguments.FirstOrDefault()?.Expression is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression })
            return ("already_data", $"default of a data read .{callName}(\"key\", x): used only when the data lacks the key");
        if (call is InvocationExpressionSyntax && FormatCall.IsMatch(callName)) return ("visual", $"text formatting ({callName})");
        if (call is InvocationExpressionSyntax && LogCall.IsMatch(callName) && !callName.StartsWith("Get")) return ("infrastructure", $"log / journal ({callName})");
        if (call is ObjectCreationExpressionSyntax && CapacityType.IsMatch(callName)) return ("infrastructure", "collection capacity");
        if (l.Context == "array_size") return ("infrastructure", "array size (buffer)");
        if (InfraMember.IsMatch(l.Member) || InfraMember.IsMatch(l.Owner) && !l.Owner.EndsWith("System")) return ("infrastructure", $"{Regex.Match(l.Member + " " + l.Owner, InfraMember.ToString()).Value} code (hash / save / parse / text / log / export)");
        if (Regex.IsMatch(l.Owner, "Rng|Random|Prng|Xorshift|Pcg")) return ("infrastructure", "random number generator internals");
        if (l.Context == "index" || node.Parent is BracketedArgumentListSyntax || node.Ancestors().OfType<BracketedArgumentListSyntax>().Any(b => b.Parent is ElementAccessExpressionSyntax && b.Span.Contains(node.Span) && abs <= 1))
            return ("index", "array / list index");
        var forStmt = node.Ancestors().OfType<ForStatementSyntax>().FirstOrDefault(fs => fs.Declaration?.Span.Contains(node.Span) == true || fs.Incrementors.Any(i => i.Span.Contains(node.Span)) || fs.Condition?.Span.Contains(node.Span) == true);
        if (forStmt != null && abs <= 1) return ("index", "loop start / step");
        if (abs > 0 && abs <= 1e-3 && l.Context is "compare" or "math_max" or "math_min" or "add" or "math_clamp" or "subtract" or "equals" or "arg:MathF.Max" or "arg:Math.Max")
            return ("infrastructure", "numerical tolerance (epsilon)");
        if (abs > 0 && abs < 1e-4) return ("infrastructure", "numerical tolerance (epsilon)");
        var around = l.CtxName + " " + l.LineText;
        if (abs is 180 or 360 or 57.29578 or 57.2958 or 0.0174533 or 0.01745329 or 3.14159 or 3.1415927 or 6.2831855 or 6.28318 && AngleCtx.IsMatch(around))
            return ("infrastructure", "angle unit conversion / wrap");
        if (abs is 1000 or 60 or 3600 && Regex.IsMatch(around, "Ms|Milli|Minute|Hour|PerMin|ToSeconds|seconds", RegexOptions.IgnoreCase) && l.Context is "multiply" or "divide" or "divide_num")
            return ("infrastructure", "unit conversion (ms / minutes / hours)");
        if (abs == 100 && Regex.IsMatch(around, "Percent|Pct|%", RegexOptions.IgnoreCase)) return ("infrastructure", "percent conversion");
        var named = l.Context is "const_field" or "static_field" or "field_init" or "property_init" or "param_default" or "object_init" or "const_local" || l.Context.StartsWith("ctor_arg");
        if (abs is 0 or 1)
        {
            if (named && GameplayName.IsMatch(l.CtxName)) return ("gameplay", $"0/1 as the value of a named setting ({l.CtxName})");
            return ("index", "0 / 1 / -1 (identity, start value; whitelist §3.5)");
        }
        if (abs is 2 or 0.5 && l.Context is "divide" or "multiply")
        {
            var bin = node.Ancestors().OfType<BinaryExpressionSyntax>().FirstOrDefault();
            var other = bin == null ? null : Unwrap(bin.Left).Span.Contains(node.Span) ? bin.Right : bin.Left;
            if (other is ParenthesizedExpressionSyntax { Expression: BinaryExpressionSyntax { RawKind: (int)SyntaxKind.AddExpression } })
                return ("infrastructure", "midpoint / average ((a + b) / 2)");
        }
        // presentation-named values
        if (VisualName.IsMatch(l.CtxName) || VisualName.IsMatch(l.Member) && !GameplayName.IsMatch(l.CtxName))
            return ("visual", $"presentation value ({(VisualName.IsMatch(l.CtxName) ? l.CtxName : l.Member)})");
        // a value written into a field / property: who reads it?
        if (l.Context is "field_init" or "property_init" or "assign" or "object_init" or "static_field" or "const_field" or "compound_assign")
        {
            ISymbol? target = null;
            var p = node.Parent;
            while (p is ParenthesizedExpressionSyntax or CastExpressionSyntax or PrefixUnaryExpressionSyntax) p = p.Parent;
            if (p is EqualsValueClauseSyntax { Parent: VariableDeclaratorSyntax vd }) target = model.GetDeclaredSymbol(vd);
            else if (p is EqualsValueClauseSyntax { Parent: PropertyDeclarationSyntax pd }) target = model.GetDeclaredSymbol(pd);
            else if (p is AssignmentExpressionSyntax asg) target = model.GetSymbolInfo(asg.Left).Symbol;
            if (target is IFieldSymbol or IPropertySymbol)
            {
                target = Graph.Norm(target);
                var rs = readers.GetValueOrDefault(Graph.Key(target));
                if (rs == null || rs.Count == 0) return ("infrastructure", $"written to {target.Name}, which nothing reads");
                if (rs.All(r => !r.Reachable)) return ("visual", $"written to {target.Name}, read only outside the simulation ({rs.First().Symbol.ContainingType?.Name}.{rs.First().Symbol.Name})");
            }
        }
        var why = l.M?.RootReason != null ? "root " + l.M.RootReason : $"reachable (depth {l.M?.Depth})";
        return ("gameplay", $"{l.Context} in {l.Owner}.{l.Member}; {why}");
    }

    // ------------------------------------------------------------------------------------------------ lanes, keys, move modes

    internal static readonly string[] Lanes = { "weapons", "vehicles", "boss", "bases", "modes_campaign", "ai_rest" };

    private static string LaneOf(string f)
    {
        // pass 2 (09/10): the AI's own files are the AI domain, whatever their names say (Commander, Conquest, Boss...)
        if (f.StartsWith("Sim/AI/")) return "ai_rest";
        if (Regex.IsMatch(f, @"^Sim/Bosses/|Boss|BigAttack|BigStrike|Escort|TierDefs|HuntPower")) return "boss";
        if (Regex.IsMatch(f, @"^Sim/(Combat|Strikes)/|Weapon|Munition|Projectile|Armour|DamageTable|Missile|Bomb|Flare|Countermeasure|Cluster|Ammo|FirePower|SecondRounds|FixRules")) return "weapons";
        if (Regex.IsMatch(f, @"Base(Rules|Sites|System|Loadout|Plan|Roles|Strength)|Tower|HqType|Fortress|Wall|Outpost|Garrison|SimWorld\.Walls")) return "bases";
        if (Regex.IsMatch(f, @"^Sim/(Modes|Economy|Events|Sandbox)/|ModeSession|MatchRunner\.(Ending|MissionEvents|GroundEvents|Elites|EventHud)|Campaign|Mission|Narrative|Operation|Endless|Siege|Conquest|Weekly|Showdown|SimWorld\.(MatchEnd|Events|Storm|Sandbox)|Daily|Reward")) return "modes_campaign";
        if (Regex.IsMatch(f, @"^Sim/(Movement|Entities|Abilities)/|Vehicle|Gear|Supply|Rail|Aircraft|Commander|SimWorld\.(Rails|Commanders|NavStates|Intel)|Catalog|Definitions")) return "vehicles";
        return "ai_rest";
    }

    private static string DomainOf(string lane, string f) => lane switch
    {
        "weapons" => "weapons", "vehicles" => "vehicles", "boss" => "bosses", "bases" => "bases",
        "modes_campaign" => Regex.IsMatch(f, "Campaign|Mission|Narrative|Operation|Chapter|Story|FrontMap") ? "campaign" : "modes",
        _ => Regex.IsMatch(f, "Navigation|Map|Terrain|Spawn|SeaRoute|Lane|EntryGate|UnitCost") ? "maps" : "ai",
    };

    private static string UnitOf(Lit l)
    {
        var n = l.CtxName + " " + l.Member;
        if (Regex.IsMatch(n, "Ticks?\\b|Tick[A-Z]")) return "ticks";
        if (Regex.IsMatch(n, "Second|Time|Delay|Cooldown|Interval|Duration|Wait|Reload|Recharge|Life|Until")) return "s";
        if (Regex.IsMatch(n, "Speed|Velocity")) return "m/s";
        if (Regex.IsMatch(n, "Radius|Range|Reach|Distance|Metre|Gap|Spacing|Width|Length|Height|Altitude|Offset|Leash")) return "m";
        if (Regex.IsMatch(n, "Chance|Share|Odds|Prob|Fraction|Ratio")) return "share";
        if (Regex.IsMatch(n, "Deg|Angle|Arc|Cone")) return "deg";
        if (Regex.IsMatch(n, "Cp\\b|Cp[A-Z]|Cost|Price")) return "CP";
        if (Regex.IsMatch(n, "Count|Max[A-Z]|Cap\\b|Limit|Slots|Waves?")) return "count";
        return l.Group switch { "ban_kinh" => "m", "thoi_gian" => "s", "xac_suat" => "share", "tran" or "gioi_han_thuc_the" => "count", _ => "x" };
    }

    private static string Ident(string s)
    {
        s = Regex.Replace(s, "^(m_|_)+", "");
        s = Regex.Replace(s, "[^A-Za-z0-9]", "");
        if (s.Length == 0) return "";
        if (char.IsDigit(s[0])) s = "n" + s;
        return s;
    }

    private static void AssignLanes(List<Lit> lits, Registry reg, Compiler.Pair? c = null)
    {
        var constUses = ConstantContextNames(lits);
        var assigned = AssignedNames(lits);
        var used = new Dictionary<string, (TypedValue v, string baseName)>(StringComparer.Ordinal);
        foreach (var k in reg.Keys.Values) used[k.Key] = (k.Field?.Default ?? new TypedValue("?", 0), "");
        var fieldPaths = new HashSet<string>(reg.Fields.Keys, StringComparer.Ordinal);
        // pass 2 (09/10): the gameplay literals first (their keys as before), then the simulation's other literals, so a
        // literal the pass-2 policy moves against the scan's class (Tools/export/literal_to_tunable.py FORCE_MOVE) has a key too
        var order = lits.Where(l => l.Class == "gameplay").OrderBy(l => l.File, StringComparer.Ordinal).ThenBy(l => l.Line)
            .Concat(lits.Where(l => l.Class != "gameplay" && (l.File.StartsWith("Sim/") || l.File.StartsWith("Game/Match/")))
                .OrderBy(l => l.File, StringComparer.Ordinal).ThenBy(l => l.Line));
        foreach (var l in order)
        {
            l.Lane = LaneOf(l.File);
            l.Domain = DomainOf(l.Lane, l.File);
            l.Unit = UnitOf(l);
            l.Mode = MoveMode(l, constUses, assigned);
            var owner = Syn.Camel(Ident(l.Owner));
            if (owner == "") owner = "misc";
            var named = l.Context is "const_field" or "static_field" or "property_init" or "field_init";
            var ctx = Ident(l.CtxName);
            var baseName = named && ctx != "" ? Syn.Camel(ctx) : Syn.Camel(Ident(l.Member) + Syn.Pascal(ctx));
            if (baseName == "" || baseName == Syn.Camel(Ident(l.Member)) && ctx == "") baseName = Syn.Camel(Ident(l.Member)) + Syn.Pascal(l.Group == "khac" ? "value" : l.Group.Split('_')[0]);
            if (baseName == "" ) baseName = "value";
            if (baseName.Length > 48) baseName = baseName[..48];
            // pass 2 (09/10): a literal in a data table gets its row id and path (TableNames), and is never merged with another
            var inStaticInit = l.Node.Ancestors().OfType<FieldDeclarationSyntax>().FirstOrDefault() is { } sf && sf.Modifiers.Any(SyntaxKind.StaticKeyword) && !sf.Modifiers.Any(SyntaxKind.ConstKeyword)
                               && !(sf.Declaration.Variables.Count == 1 && sf.Declaration.Variables[0].Initializer?.Value == (l.Negated ? (ExpressionSyntax)l.Node.Parent! : l.Node));
            if (c != null && (l.Context is "table" or "tuple" || inStaticInit) && TableNames.Of(l.Node, c.Model(Repo.Scripts + "/" + l.File)) is { } tableName)
            {
                baseName = tableName;
                named = true;
            }
            if (Syn.Pascal(baseName) == Syn.Pascal(owner)) baseName += "Value";
            var tv = TypedValue.FromToken(l.Node.Token, l.Negated)!.Value; // pass 2: signed (a negated literal is its own value)
            string key;
            for (var n = 1; ; n++)
            {
                key = $"{l.Domain}.{owner}.{baseName}{(n == 1 ? "" : n.ToString())}";
                if (!used.TryGetValue(key, out var u) && !fieldPaths.Contains(Syn.KeyToPath(key))) { used[key] = (tv, baseName); break; }
                if (u.baseName == baseName && u.v.SameAs(tv) && !named) break; // same name, same value: one setting used twice
            }
            l.Key = key;
        }
    }

    private static Dictionary<string, List<string>> ConstantContextNames(List<Lit> lits)
    {
        var map = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        foreach (var tree in lits.Select(l => l.Node.SyntaxTree).Distinct())
            foreach (var id in tree.GetRoot().DescendantNodes().OfType<IdentifierNameSyntax>())
            {
                var cc = Syn.ConstantContext(id);
                if (cc == null)
                {
                    var constDecl = id.Ancestors().FirstOrDefault(a => a is FieldDeclarationSyntax fd && fd.Modifiers.Any(SyntaxKind.ConstKeyword) || a is LocalDeclarationStatementSyntax ld && ld.IsConst);
                    if (constDecl != null) cc = "const initializer";
                }
                if (cc == null) continue;
                if (!map.TryGetValue(id.Identifier.Text, out var list)) map[id.Identifier.Text] = list = new List<string>();
                list.Add($"{cc} at {Repo.Short(tree.FilePath)}:{Syn.Line(id)}");
            }
        return map;
    }

    private static HashSet<string> AssignedNames(List<Lit> lits)
    {
        var set = new HashSet<string>(StringComparer.Ordinal);
        foreach (var tree in lits.Select(l => l.Node.SyntaxTree).Distinct())
            foreach (var a in tree.GetRoot().DescendantNodes().OfType<AssignmentExpressionSyntax>())
                if (LastName(a.Left) is { Length: > 0 } n && a.Left is IdentifierNameSyntax or MemberAccessExpressionSyntax) set.Add(n);
        return set;
    }

    /// <summary>What the move tool will do with this literal (the same rules as Move.PlanRow), or manual:&lt;why&gt;.</summary>
    private static string MoveMode(Lit l, Dictionary<string, List<string>> constUses, HashSet<string> assigned)
    {
        var node = l.Node;
        var cc = Syn.ConstantContext(node);
        if (cc != null) return "manual:" + cc;
        if (l.Type is "decimal" or "ulong") return "manual:type " + l.Type;
        if (l.Type == "int" && node.Parent is EqualsValueClauseSyntax { Parent: VariableDeclaratorSyntax { Parent: VariableDeclarationSyntax vd } } && vd.Type.ToString() is "byte" or "sbyte" or "short" or "ushort" or "char" or "uint" or "ulong")
            return "manual:int narrowed to " + vd.Type;
        var whole = l.Negated ? (ExpressionSyntax)node.Parent! : node;
        var field = node.Ancestors().TakeWhile(a => a is not AnonymousFunctionExpressionSyntax).OfType<FieldDeclarationSyntax>().FirstOrDefault();
        if (field != null && (field.Modifiers.Any(SyntaxKind.ConstKeyword) || field.Modifiers.Any(SyntaxKind.StaticKeyword)))
        {
            var isConst = field.Modifiers.Any(SyntaxKind.ConstKeyword);
            if (field.Declaration.Type is ArrayTypeSyntax || field.Declaration.Variables.Any(v => v.Initializer?.Value is InitializerExpressionSyntax or ArrayCreationExpressionSyntax))
                return "manual:static array table (FloatArray / IntArray entry)";
            if (field.Declaration.Variables.Count != 1) return "manual:field declares several variables (split first)";
            var v = field.Declaration.Variables[0];
            if (v.Initializer?.Value != whole) return $"manual:{(isConst ? "const" : "static")} initializer is an expression";
            if (isConst && constUses.TryGetValue(v.Identifier.Text, out var uses)) return "manual:const used in a constant context (" + uses[0] + ")";
            if (!isConst && assigned.Contains(v.Identifier.Text)) return "manual:static field assigned somewhere";
            return isConst ? "const_to_property" : "static_to_property";
        }
        var prop = node.Ancestors().OfType<PropertyDeclarationSyntax>().FirstOrDefault();
        if (prop?.Initializer != null && prop.Initializer.Span.Contains(node.Span) && prop.Modifiers.Any(SyntaxKind.StaticKeyword)) return "manual:static property initializer";
        var local = node.Ancestors().TakeWhile(a => a is not AnonymousFunctionExpressionSyntax).OfType<LocalDeclarationStatementSyntax>().FirstOrDefault();
        if (local is { IsConst: true })
        {
            if (local.Declaration.Variables.Count != 1) return "manual:const local declares several variables";
            if (local.Declaration.Variables[0].Initializer?.Value != whole) return "manual:const local initializer is an expression";
            var name = local.Declaration.Variables[0].Identifier.Text;
            var body = local.Ancestors().FirstOrDefault(a => a is BaseMethodDeclarationSyntax or AccessorDeclarationSyntax or LocalFunctionStatementSyntax or PropertyDeclarationSyntax);
            if (body != null && body.DescendantNodes().OfType<IdentifierNameSyntax>().Any(i => i.Identifier.Text == name && (Syn.ConstantContext(i) != null || i.Ancestors().Any(a => a is LocalDeclarationStatementSyntax { IsConst: true } ld && ld != local))))
                return "manual:const local used in a constant context";
            return "local_const";
        }
        if (node.Ancestors().Any(a => a is InterpolationAlignmentClauseSyntax or InterpolationFormatClauseSyntax)) return "manual:format alignment";
        return "inline";
    }

    // ------------------------------------------------------------------------------------------------ writers

    private static void WriteCandidates(string dir, List<Lit> lits)
    {
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("id", "file", "line", "col", "literal", "type", "class", "reason", "group", "context", "name_hint", "owner", "member", "reachable", "depth", "found_by", "lifecycle", "system", "lane", "domain", "key", "unit", "mode", "line_text"));
        foreach (var l in lits)
            sb.AppendLine(Csv.Row(l.Id, l.File, l.Line, l.Col, (l.Negated ? "-" : "") + l.Text, l.Type, l.Class, l.Reason, l.Group, l.Context, l.CtxName, l.Owner, l.Member, l.Reachable ? 1 : 0,
                l.M?.Depth ?? -1, string.Concat(l.FoundBy), l.Lifecycle, l.System, l.Lane, l.Domain, l.Key, l.Unit, l.Mode, l.LineText));
        File.WriteAllText(Path.Combine(dir, "candidates.csv"), sb.ToString(), new UTF8Encoding(true));
    }

    private static void WriteTables(string dir, List<Table> tables)
    {
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("file", "line", "kind", "owner", "member", "reachable", "literals", "gameplay", "sample"));
        foreach (var t in tables)
            sb.AppendLine(Csv.Row(t.File, t.Line, t.Kind, t.Owner, t.Member, t.Reachable ? 1 : 0, t.Count, t.Lits.Count(l => l.Class == "gameplay"), t.Sample));
        File.WriteAllText(Path.Combine(dir, "scan_b_tables.csv"), sb.ToString(), new UTF8Encoding(true));
    }

    private static void WriteIds(string dir, string listDir, List<IdCheck> ids)
    {
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("file", "line", "kind", "literal", "receiver", "owner", "member", "reachable", "data_hit", "proposed_flag", "line_text"));
        foreach (var i in ids.OrderBy(i => i.File, StringComparer.Ordinal).ThenBy(i => i.Line))
            sb.AppendLine(Csv.Row(i.File, i.Line, i.Kind, i.Literal, i.Receiver, i.Owner, i.Member, i.Reachable ? 1 : 0, i.DataHit, i.Flag, i.LineText));
        File.WriteAllText(Path.Combine(dir, "scan_c_id_checks.csv"), sb.ToString(), new UTF8Encoding(true));
        var sb2 = new StringBuilder();
        sb2.AppendLine(Csv.Row("file", "line", "kind", "literal", "receiver", "member", "lane", "data_hit", "proposed_flag"));
        foreach (var i in ids.Where(i => i.Reachable).OrderBy(i => LaneOf(i.File)).ThenBy(i => i.File, StringComparer.Ordinal).ThenBy(i => i.Line))
            sb2.AppendLine(Csv.Row(i.File, i.Line, i.Kind, i.Literal, i.Receiver, i.Member, LaneOf(i.File), i.DataHit, i.Flag));
        File.WriteAllText(Path.Combine(listDir, "id_hardcodes.csv"), sb2.ToString(), new UTF8Encoding(false));
    }

    private static void WriteAssets(string dir, List<AssetValue> assets)
    {
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("asset", "script", "field", "value", "decision"));
        foreach (var a in assets) sb.AppendLine(Csv.Row(a.Asset, a.Script, a.Field, a.Value, a.Decision));
        File.WriteAllText(Path.Combine(dir, "scan_d_assets.csv"), sb.ToString(), new UTF8Encoding(true));
    }

    private static void WriteLifecycle(string dir, Life life, List<Lit> lits)
    {
        var steps = Steps.Select(s => s.step).ToList();
        var ents = Entities.Select(e => e.entity).Append("chung").ToList();
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row(new object[] { "entity" }.Concat(steps).ToArray()));
        foreach (var e in ents) sb.AppendLine(Csv.Row(new object[] { e }.Concat(steps.Select(s => (object)life.Matrix.GetValueOrDefault((e, s)))).ToArray()));
        File.WriteAllText(Path.Combine(dir, "scan_e_lifecycle_matrix.csv"), sb.ToString(), new UTF8Encoding(true));
    }

    private static void WriteSystems(string dir, List<SysItem> items)
    {
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("class", "file", "line", "member", "what", "value", "decision"));
        foreach (var i in items)
        {
            var d = i.Decision != "" ? i.Decision : i.Lit!.Class switch
            {
                "gameplay" => "ra_du_lieu (pass 2, lane " + i.Lit.Lane + ")",
                "already_data" => "da_trong_du_lieu (" + i.Lit.Reason + ")",
                _ => "hinh_anh_ha_tang: " + i.Lit.Class + " (" + i.Lit.Reason + ")",
            };
            sb.AppendLine(Csv.Row(i.Class, i.File, i.Line, i.Member, i.What, i.Value, d));
        }
        File.WriteAllText(Path.Combine(dir, "scan_f_systems.csv"), sb.ToString(), new UTF8Encoding(true));
    }

    private static List<Lit> Sample(string dir, List<Lit> lits, int seed)
    {
        var pool = lits.Where(l => l.Class is "visual" or "infrastructure").OrderBy(l => l.Id).ToList();
        var rnd = new Random(seed);
        var pick = pool.OrderBy(_ => rnd.Next()).Take(150).OrderBy(l => l.Id).ToList();
        var sb = new StringBuilder();
        sb.AppendLine(Csv.Row("id", "file", "line", "literal", "class", "reason", "member", "line_text", "verdict", "note"));
        foreach (var l in pick) sb.AppendLine(Csv.Row(l.Id, l.File, l.Line, l.Text, l.Class, l.Reason, l.Owner + "." + l.Member, l.LineText, "", ""));
        File.WriteAllText(Path.Combine(dir, "sample150.csv"), sb.ToString(), new UTF8Encoding(true));
        return pick;
    }

    // ------------------------------------------------------------------------------------------------ cross-checks (§3.3)

    internal sealed class KeyRef
    {
        public string Key = "";
        public int Refs, ReachableRefs;
        public string Example = "";
    }

    private static List<KeyRef> KeyReferences(Compiler.Pair c, Graph g, Registry reg)
    {
        var list = new List<KeyRef>();
        foreach (var k in reg.Keys.Values)
        {
            var parts = k.Path.Split('.');
            var type = c.Sim.GetTypeByMetadataName("MachineBrigade.Sim.Content.SimTunables+" + string.Join('+', parts[..^1]));
            var field = type?.GetMembers(parts[^1]).FirstOrDefault();
            var r = new KeyRef { Key = k.Key };
            if (field != null && g.Get(field) is { } m)
            {
                var users = m.In.Where(u => !Registry.IsTunablesFile(u.File)).ToList();
                // a wrapper property of the old name counts through its own users
                var reachable = users.Any(u => u.Reachable);
                r.Refs = users.Count;
                r.ReachableRefs = users.Count(u => u.Reachable);
                r.Example = users.Select(u => Repo.Short(u.File) + " " + u.Symbol.Name).FirstOrDefault() ?? "";
                _ = reachable;
            }
            list.Add(r);
        }
        return list;
    }

    internal sealed class Cross
    {
        public readonly List<string> Lines = new();
        public readonly List<(string item, int lits, int keys)> Section4 = new();
        public readonly List<string> UnreadJson = new();
        public readonly List<string> KeysNotInPack = new();
    }

    private static readonly (string item, string rx)[] Section4 =
    {
        ("4.1 bom và ném bom", "Bomb|Bomblet|Napalm|Cluster|Carpet|Stick|Release|Drop(?!ped)|BigStrike|Glide"),
        ("4.2 tên lửa", "Missile|Rocket|Guid|Seeker|Homing|Lock|Arming|Cruise|Loiter|TopAttack|Sam\\b"),
        ("4.3 pháo sáng và APS", "Flare|Aps|Trophy|Intercept|PointDefen|Ciws|Decoy"),
        ("4.4 đạn pháo / cối / rốc-két / bắn thẳng", "Shell|Mortar|Artillery|Ballistic|Arc|Lead|Spread|Accuracy|Reload|Magazine|Burst|Salvo|Barrel|Muzzle|Penetrat|Falloff"),
        ("4.5 phát hiện và tầm nhìn", "Vision|Sight|Detect|Spot|Reveal|Stealth|Fog|Smoke|Radar|Uav|Intel|Visible|CounterBattery"),
        ("4.6 di chuyển và địa hình", "Speed|Accel|Turn|Steer|Terrain|Road|Rough|Forest|Water|Push|Stuck|Avoid|Separation|Traffic|Path|Nav"),
        ("4.7 chọn mục tiêu và AI đơn vị", "Target|Priority|Threat|Score|Retarget|Commit|Engage|Weight"),
        ("4.8 triển khai và kinh tế", "Deploy|Drop|Opening|ArmyCap|Supply|Income|Cp\\b|Cp[A-Z]|Refund|Bounty|Reward|CatchUp|Upkeep|Difficulty|Mutator|Start"),
        ("4.9 boss", "Boss|BigAttack|Phase|Escort|Summon|Charge|Ram|Weak|Part"),
        ("4.10 tháp, căn cứ, tường", "Tower|Turret|Base|Hq|Wall|Gate|Garrison|Shield|Aura|Rebuild|Fortress|Outpost"),
        ("4.11 chế độ và chiến dịch", "Mode|Score|Bleed|Overtime|Wave|Endless|Siege|Conquest|Mission|Campaign|Event|Trigger|Reinforce|Warning"),
        ("4.12 máy bay / tàu / ray", "Air|Jet|Plane|Heli|Hover|Orbit|Loiter|Sortie|Naval|Ship|Rail|Train"),
        ("4.13 hư hại và hồi", "Death|Wreck|Burn|Fire(?!Rate)|Chain|Repair|Heal|Rearm|Resupply"),
        ("4.14 thời gian toàn cục", "Tick|TimeStep|Dt\\b|Interval|Every"),
    };

    private static Cross CrossCheck(List<Lit> lits, Registry reg, List<KeyRef> keyRefs, SourceSet src)
    {
        var x = new Cross();
        var game = lits.Where(l => l.Class == "gameplay").ToList();
        foreach (var (item, rx) in Section4)
        {
            var r = new Regex(rx);
            var n = game.Count(l => r.IsMatch(l.Owner + " " + l.Member + " " + l.CtxName + " " + l.File));
            var k = reg.Keys.Keys.Count(key => r.IsMatch(Syn.KeyToPath(key)));
            x.Section4.Add((item, n, k));
        }
        // JSON property names no C# string literal names (data the code may not read)
        var strings = new HashSet<string>(StringComparer.Ordinal);
        foreach (var (rel, text) in src.Files)
            foreach (Match m in Regex.Matches(text, "\"([A-Za-z_][A-Za-z0-9_]*)\"")) strings.Add(m.Groups[1].Value);
        var dataDir = Repo.Abs("Assets/MachineBrigade/Resources/Data");
        var props = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var f in Directory.EnumerateFiles(dataDir, "*.json", SearchOption.AllDirectories))
        {
            if (f.EndsWith("tunables.json")) continue;
            try
            {
                using var doc = JsonDocument.Parse(File.ReadAllText(f), new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
                CollectProps(doc.RootElement, Path.GetFileName(f), props, 0);
            }
            catch { }
        }
        foreach (var (p, where) in props.OrderBy(k => k.Key, StringComparer.Ordinal))
            if (!strings.Contains(p) && !Regex.IsMatch(p, "^(_|//|note|notes|comment|comments|source|sources|ref|why|desc|description)$", RegexOptions.IgnoreCase)) x.UnreadJson.Add($"{p} ({where})");
        // every tunables key in the pack (the domain xlsx files' text)
        var packText = new StringBuilder();
        foreach (var xl in Directory.EnumerateFiles(Repo.Abs("Docs/export/current"), "*.xlsx"))
        {
            try
            {
                using var z = ZipFile.OpenRead(xl);
                foreach (var e in z.Entries.Where(e => e.FullName.EndsWith(".xml") && (e.FullName.Contains("sharedStrings") || e.FullName.Contains("worksheets/"))))
                {
                    using var r = new StreamReader(e.Open());
                    packText.Append(r.ReadToEnd());
                }
            }
            catch { }
        }
        var pt = packText.ToString();
        foreach (var k in reg.Keys.Keys)
        {
            var name = k.Split('.')[2];
            if (!pt.Contains(k) && !pt.Contains(">" + name + "<")) x.KeysNotInPack.Add(k);
        }
        return x;
    }

    private static void CollectProps(JsonElement e, string file, Dictionary<string, string> props, int depth)
    {
        if (depth > 12) return;
        if (e.ValueKind == JsonValueKind.Object)
            foreach (var p in e.EnumerateObject())
            {
                props.TryAdd(p.Name, file);
                CollectProps(p.Value, file, props, depth + 1);
            }
        else if (e.ValueKind == JsonValueKind.Array)
            foreach (var a in e.EnumerateArray().Take(400)) CollectProps(a, file, props, depth + 1);
    }

    // ------------------------------------------------------------------------------------------------ move lists for pass 2

    private static void WriteLists(string dir, List<Lit> lits)
    {
        foreach (var lane in Lanes)
        {
            var sb = new StringBuilder();
            sb.AppendLine("file,line,literal,key,unit,kind,linh_vuc,occurrence,mode,note,context");
            foreach (var l in lits.Where(l => l.Class == "gameplay" && l.Lane == lane).OrderBy(l => l.File, StringComparer.Ordinal).ThenBy(l => l.Line).ThenBy(l => l.Occurrence))
                sb.AppendLine(Csv.Row(l.File, l.Line, l.Text, l.Key, l.Unit, l.Group, Move.DomainNumber(l.Key), l.Occurrence, l.Mode, "", $"{l.Context}: {l.LineText}"));
            File.WriteAllText(Path.Combine(dir, $"moves_{lane}.csv"), sb.ToString(), new UTF8Encoding(false));
        }
    }
}

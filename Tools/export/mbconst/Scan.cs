using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>
/// Pass 1 (§3): the call-graph reachability from the simulation's entry points, the six independent scans (a-f), the
/// cross-checks, the candidate list with its classification, and the per-domain move lists for pass 2.
/// </summary>
internal static partial class Scan
{
    internal sealed class Lit
    {
        public int Id;
        public string File = "", Text = "", Type = "", Member = "", Owner = "", LineText = "", Context = "", CtxName = "";
        public int Line, Col, Pos, Occurrence;
        public double Value;
        public bool Reachable, Negated;
        public Graph.Member? M;
        public string Class = "", Reason = "", Group = "", Domain = "", Lane = "", Mode = "", Key = "", Unit = "";
        public readonly SortedSet<char> FoundBy = new();
        public string Lifecycle = "";
        public string System = "";
        public LiteralExpressionSyntax Node = null!;
    }

    private static readonly string[] ViewDirs = { "Game/Hud/", "Game/Effects/", "Game/Audio/", "Game/Rendering/", "Game/Views/", "Game/Input/", "Game/CameraControl/" };

    private static readonly (string group, Regex rx)[] Category =
    {
        ("sat_thuong", new Regex(@"damage|dmg|\bhp\b|health|hurt|heal|armou?r|pen(etration)?\b|blast|splash|kill", RegexOptions.IgnoreCase)),
        ("thoi_gian", new Regex(@"second|seconds|time|\bnow\b|cooldown|delay|duration|interval|timer|tick|wait|warn|reload|rearm|recharge|life", RegexOptions.IgnoreCase)),
        ("ban_kinh", new Regex(@"radius|range|distance|reach|metre|spacing|gap|width|length|height|altitude|leash|sight|vision|offset", RegexOptions.IgnoreCase)),
        ("xac_suat", new Regex(@"chance|random|probab|Next(Double|Float)?\(|roll|odds", RegexOptions.IgnoreCase)),
        ("tran", new Regex(@"\bcap\b|Cap\b|limit|ceiling|clamp", RegexOptions.None)),
        ("tan_suat", new Regex(@"rate|per ?second|\bhz\b|every|frequency|cadence|speed", RegexOptions.IgnoreCase)),
        ("gioi_han_thuc_the", new Regex(@"count|units|entities|pool|squad|wave|max\w*(count|units)|capacity|slots", RegexOptions.IgnoreCase)),
        ("nguong", new Regex(@"threshold|\bmin\b|\bmax\b|Min\w*|Max\w*|at least|above|below|share|ratio", RegexOptions.None)),
    };

    private static readonly Regex GameplayName = new(@"Chance|Rate|Radius|Range|Reach|Damage|Seconds|Cooldown|Delay|Mult|Scale|Share|Cap|Max|Min|Speed|Health|Hp|Armou?r|Cost|Cp|Bounty|Reward|Time|Ticks|Distance|Count|Limit|Factor|Bonus|Penalty|Odds|Weight|Priority|Threshold|Interval|Duration", RegexOptions.Compiled);
    private static readonly Regex VisualName = new(@"(Fx|Vfx|Effect|Visual|Anim|Sound|Audio|Sfx|Colou?r|Hud|\bUi\b|Camera|Shake|Flash|Icon|Sprite|Draw|Render|Blink|Pulse|Glow|Banner|Toast|Label|Tooltip|Font|Pixel|Screen|Haptic|Vibrat|Text\b|Display|Marker|Gizmo|Debug)", RegexOptions.Compiled);
    private static readonly Regex InfraMember = new(@"(Hash|Fnv|Mix|Checksum|Serializ|Deserializ|Save|Load(?!out)|Migrat|Version|Parse|ToString|Format|Describe|Log\b|Logger|Journal|Debug|Dump|Export|Handbook|Facts)", RegexOptions.Compiled);
    private static readonly Regex VerbCommand = new(@"^(Deploy|Spawn|Add|Queue|Enqueue|Issue|Order|Command|Set|Apply|Start|Begin|Trigger|Damage|Kill|Remove|Place|Build|Call|Launch|Fire|Give|Grant|Award|Use|Activate|Cast|Buy|Spend|Pay|Reinforce|Drop|Summon|Retreat|Move|Attack)", RegexOptions.Compiled);

    public static int Run(string[] args)
    {
        string outDir = Repo.Abs("Docs/export/current/_qa/pass1"), listDir = Repo.Abs("Tools/export/pack2");
        var seed = 20261003;
        string? debug = null;
        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--out": outDir = args[++i]; break;
                case "--lists": listDir = args[++i]; break;
                case "--seed": seed = int.Parse(args[++i]); break;
                case "--why": debug = args[++i]; break;
                case "--repo": Repo.Root = args[++i]; break;
            }
        }
        Directory.CreateDirectory(outDir);
        Directory.CreateDirectory(listDir);
        var t0 = DateTime.Now;
        var src = SourceSet.FromWorktree();
        var c = Compiler.Build(src);
        var errors = Compiler.Diagnostics(c).Count(d => d.Severity == DiagnosticSeverity.Error);
        Console.WriteLine($"compiled ({errors} errors) {(DateTime.Now - t0).TotalSeconds:F0}s");
        var g = new Graph(c);
        g.Build();
        var roots = Roots(g).ToList();
        g.Blocked = m => ViewDirs.Any(Repo.Short(m.File).StartsWith) || Repo.Short(m.File).StartsWith("Editor/");
        g.Reach(roots);
        File.WriteAllLines(Path.Combine(outDir, "view_boundary.txt"), g.Boundary.Select(b => $"{b.from.Id} [{Repo.Short(b.from.File)}] -> {b.to.Id} [{Repo.Short(b.to.File)}]").Distinct());
        Console.WriteLine($"graph: {g.Members.Count} members, {g.Members.Values.Count(m => m.Reachable)} reachable from {roots.Count} roots {(DateTime.Now - t0).TotalSeconds:F0}s");

        if (debug != null)
        {
            foreach (var m in g.Members.Values.Where(m => m.Id.Contains(debug)).Take(40))
                Console.WriteLine($"{(m.Reachable ? "R" : "-")} {m.Id} [{Repo.Short(m.File)}] in: {string.Join(", ", m.In.Take(6).Select(x => (x.Reachable ? "R " : "- ") + x.Id))} OUT: {string.Join(", ", m.Out.Take(12).Select(x => x.Id))}");
            return 0;
        }
        var reg = Registry.Load(src);
        var lits = ScanA(c, g);
        var tables = ScanB(c, g, lits);
        var ids = ScanC(c, g);
        var assets = ScanD(c, g);
        var life = ScanE(g, lits);
        var systems = ScanF(c, g, lits);
        Classify(c, g, lits);
        AssignLanes(lits, reg);
        Console.WriteLine($"scans done: {lits.Count} literals {(DateTime.Now - t0).TotalSeconds:F0}s");

        WriteCandidates(outDir, lits);
        WriteTables(outDir, tables);
        WriteIds(outDir, listDir, ids);
        WriteAssets(outDir, assets);
        WriteLifecycle(outDir, life, lits);
        WriteSystems(outDir, systems);
        var sample = Sample(outDir, lits, seed);
        var keyRefs = KeyReferences(c, g, reg);
        var cross = CrossCheck(lits, reg, keyRefs, src);
        WriteLists(listDir, lits);
        WriteSummary(outDir, g, roots, lits, tables, ids, assets, life, systems, sample, cross, keyRefs, reg);
        WriteChuaNhacToi(Path.Combine(outDir, ".."), lits);
        Console.WriteLine($"pass 1 written to {outDir} and {listDir} ({(DateTime.Now - t0).TotalSeconds:F0}s)");
        return 0;
    }

    // ------------------------------------------------------------------------------------------------ roots (§3.1)

    private static IEnumerable<(Graph.Member, string)> Roots(Graph g)
    {
        foreach (var m in g.Members.Values)
        {
            var file = Repo.Short(m.File);
            var type = m.Symbol.ContainingType?.Name ?? "";
            var name = m.Symbol.Name;
            var sim = file.StartsWith("Sim/");
            var match = file.StartsWith("Game/Match/");
            if (sim && type == "SimWorld" && (name == "Step" || m.Symbol is IMethodSymbol { MethodKind: MethodKind.Constructor }))
                yield return (m, "SimWorld.Step / constructor");
            else if (sim && type == "SimWorld" && m.Symbol.DeclaredAccessibility is Accessibility.Public or Accessibility.Internal && m.Symbol is IMethodSymbol)
                yield return (m, "SimWorld public surface (commands)");
            else if (sim && Regex.IsMatch(type, "(System|Director|Ai|Mode|Session)$") && name is "Update" or "Tick" or "Step" or "Run" or "Think")
                yield return (m, "*System.Update / Tick");
            else if (sim && type == "SideSetup")
                yield return (m, "SideSetup");
            else if (sim && file.StartsWith("Sim/Modes/") && m.Symbol is IMethodSymbol { MethodKind: MethodKind.Constructor })
                yield return (m, "mode constructor");
            else if (match && (type is "GameContent" or "ModeSessions" || type.EndsWith("Session") || file.EndsWith("ModeSessions.cs")))
                yield return (m, "match setup (sessions, catalog load)");
            else if (match && m.Symbol is IMethodSymbol && m.Out.Any(t => Repo.Short(t.File).StartsWith("Sim/") && t.Symbol is IMethodSymbol && VerbCommand.IsMatch(t.Symbol.Name)))
                yield return (m, "Game/Match code issuing a sim command");
        }
    }

    // ------------------------------------------------------------------------------------------------ (a) literals

    private static List<Lit> ScanA(Compiler.Pair c, Graph g)
    {
        var list = new List<Lit>();
        foreach (var (rel, tree) in c.Trees.OrderBy(k => k.Key, StringComparer.Ordinal))
        {
            var shortPath = Repo.Short(rel);
            if (!shortPath.StartsWith("Sim/") && !shortPath.StartsWith("Game/")) continue;
            if (Registry.IsTunablesFile(rel)) continue;
            var model = c.Model(rel)!;
            var text = tree.GetText();
            var perLine = new Dictionary<(int, string), int>();
            foreach (var lit in tree.GetRoot().DescendantNodes().OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression)))
            {
                var line = Syn.Line(lit);
                var key = (line, lit.Token.Text);
                perLine[key] = perLine.GetValueOrDefault(key) + 1;
                var owner = g.Owner(lit, model);
                var tv = TypedValue.FromToken(lit.Token)!.Value;
                var l = new Lit
                {
                    Id = list.Count + 1, File = shortPath, Line = line, Col = lit.GetLocation().GetLineSpan().StartLinePosition.Character + 1, Pos = lit.SpanStart,
                    Text = lit.Token.Text, Type = tv.Type, Value = tv.AsDouble, M = owner, Reachable = owner?.Reachable ?? false,
                    Member = owner?.Symbol.Name ?? "", Owner = owner?.Symbol.ContainingType?.Name ?? TypeName(lit),
                    LineText = Snip(text.Lines[line - 1].ToString()), Occurrence = perLine[key], Node = lit,
                    Negated = lit.Parent is PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression },
                };
                l.Context = ContextOf(lit, model, out l.CtxName);
                l.FoundBy.Add('a');
                list.Add(l);
            }
        }
        return list;
    }

    private static string TypeName(SyntaxNode n) => n.Ancestors().OfType<BaseTypeDeclarationSyntax>().FirstOrDefault()?.Identifier.Text ?? "";

    private static string Snip(string s)
    {
        s = Regex.Replace(s, @"\s+", " ").Trim();
        return s.Length > 160 ? s[..160] : s;
    }

    /// <summary>The syntactic context of a literal (a short tag) and a name that says what it is (for the key).</summary>
    private static string ContextOf(LiteralExpressionSyntax lit, SemanticModel model, out string name)
    {
        name = "";
        SyntaxNode node = lit.Parent is PrefixUnaryExpressionSyntax pu ? pu : lit;
        var p = node.Parent;
        while (p is ParenthesizedExpressionSyntax or CastExpressionSyntax) { node = p; p = p.Parent; }
        switch (p)
        {
            case EqualsValueClauseSyntax { Parent: VariableDeclaratorSyntax vd }:
                name = vd.Identifier.Text;
                var fd = vd.Parent?.Parent;
                return fd is FieldDeclarationSyntax f ? (f.Modifiers.Any(SyntaxKind.ConstKeyword) ? "const_field" : f.Modifiers.Any(SyntaxKind.StaticKeyword) ? "static_field" : "field_init")
                    : fd is LocalDeclarationStatementSyntax l ? (l.IsConst ? "const_local" : "local_init") : "declarator";
            case EqualsValueClauseSyntax { Parent: PropertyDeclarationSyntax prop }:
                name = prop.Identifier.Text;
                return "property_init";
            case EqualsValueClauseSyntax { Parent: ParameterSyntax par }:
                name = par.Identifier.Text;
                return "param_default";
            case EqualsValueClauseSyntax { Parent: EnumMemberDeclarationSyntax em }:
                name = em.Identifier.Text;
                return "enum_value";
            case ArrowExpressionClauseSyntax arrow:
                name = arrow.Parent switch { PropertyDeclarationSyntax pp => pp.Identifier.Text, MethodDeclarationSyntax mm => mm.Identifier.Text, _ => "" };
                return "expression_body";
            case ReturnStatementSyntax:
                name = (lit.Ancestors().OfType<MethodDeclarationSyntax>().FirstOrDefault()?.Identifier.Text ?? "") ;
                return "return";
            case AssignmentExpressionSyntax asg when asg.Right == node:
                name = LastName(asg.Left);
                return asg.Parent is InitializerExpressionSyntax ? "object_init" : asg.IsKind(SyntaxKind.SimpleAssignmentExpression) ? "assign" : "compound_assign";
            case ArgumentSyntax { Parent: TupleExpressionSyntax } targ:
                name = targ.NameColon?.Name.Identifier.Text ?? "";
                return "tuple";
            case ArgumentSyntax arg:
            {
                var inv = arg.Parent?.Parent;
                var sym = inv != null ? model.GetSymbolInfo(inv).Symbol as IMethodSymbol : null;
                var argList = (BaseArgumentListSyntax)arg.Parent!;
                var idx = argList.Arguments.IndexOf(arg);
                var pname = arg.NameColon?.Name.Identifier.Text ?? (sym != null && idx < sym.Parameters.Length ? sym.Parameters[idx].Name : "");
                var mname = sym?.Name ?? (inv is InvocationExpressionSyntax ie ? LastName(ie.Expression) : "");
                var recv = sym?.ContainingType?.Name ?? "";
                if (recv is "Math" or "MathF" or "Mathf" or "Vector2" or "Vector3" && mname is "Min" or "Max" or "Clamp" or "Lerp" or "Pow" or "Round" or "Atan2")
                {
                    var other = argList.Arguments.Where(a => a != arg).Select(a => LastName(a.Expression)).FirstOrDefault(s => s != "") ?? "";
                    var suffix = mname switch
                    {
                        "Min" => "Cap", "Max" => "Floor", "Clamp" => idx == 1 ? "Min" : idx == 2 ? "Max" : "", "Lerp" => "Lerp", "Pow" => "Exponent", "Round" => "Digits", _ => "",
                    };
                    name = other + suffix;
                    return "math_" + mname.ToLowerInvariant();
                }
                name = pname;
                if (inv is ObjectCreationExpressionSyntax or ImplicitObjectCreationExpressionSyntax) return "ctor_arg:" + (sym?.ContainingType?.Name ?? "");
                if (inv is ElementAccessExpressionSyntax) return "index";
                return "arg:" + recv + "." + mname;
            }
            case BinaryExpressionSyntax bin:
            {
                var other = bin.Left == node ? bin.Right : bin.Left;
                var on = LastName(other);
                var k = bin.Kind();
                switch (k)
                {
                    case SyntaxKind.LessThanExpression or SyntaxKind.LessThanOrEqualExpression:
                        name = on + (bin.Right == node ? "Max" : "Min");
                        return "compare";
                    case SyntaxKind.GreaterThanExpression or SyntaxKind.GreaterThanOrEqualExpression:
                        name = on + (bin.Right == node ? "Min" : "Max");
                        return "compare";
                    case SyntaxKind.EqualsExpression or SyntaxKind.NotEqualsExpression:
                        name = on + "Is";
                        return "equals";
                    case SyntaxKind.MultiplyExpression: name = on + "Scale"; return "multiply";
                    case SyntaxKind.DivideExpression: name = on + "Divisor"; return bin.Right == node ? "divide" : "divide_num";
                    case SyntaxKind.AddExpression: name = on + "Add"; return "add";
                    case SyntaxKind.SubtractExpression: name = on + "Sub"; return "subtract";
                    case SyntaxKind.ModuloExpression: name = on + "Mod"; return "modulo";
                    case SyntaxKind.LeftShiftExpression or SyntaxKind.RightShiftExpression or SyntaxKind.BitwiseAndExpression or SyntaxKind.BitwiseOrExpression or SyntaxKind.ExclusiveOrExpression:
                        return "bitwise";
                    case SyntaxKind.CoalesceExpression: name = on + "Default"; return "coalesce";
                    default: return "binary";
                }
            }
            case ConditionalExpressionSyntax ce:
                name = LastName(ce.Condition) + (ce.WhenTrue == node ? "True" : "False");
                return "conditional";
            case InitializerExpressionSyntax:
                return "table";
            case BracketedArgumentListSyntax:
                return "index";
            case ArrayRankSpecifierSyntax:
                return "array_size";
            case CaseSwitchLabelSyntax:
                return "case_label";
            case ConstantPatternSyntax or RelationalPatternSyntax:
                return p is RelationalPatternSyntax ? "relational_pattern" : "case_label";
            case SwitchExpressionArmSyntax arm:
                name = LastName(((SwitchExpressionSyntax)arm.Parent!).GoverningExpression) + "Value";
                return "switch_arm";
            case AttributeArgumentSyntax:
                return "attribute";
            case InterpolationSyntax or InterpolationAlignmentClauseSyntax:
                return "format";
            case PostfixUnaryExpressionSyntax or PrefixUnaryExpressionSyntax:
                return "unary";
            case ForStatementSyntax:
                return "loop";
            default:
                return p?.Kind().ToString() ?? "";
        }
    }

    private static string LastName(SyntaxNode e) => e switch
    {
        IdentifierNameSyntax id => id.Identifier.Text,
        MemberAccessExpressionSyntax ma => ma.Name.Identifier.Text,
        InvocationExpressionSyntax inv => LastName(inv.Expression),
        ElementAccessExpressionSyntax ea => LastName(ea.Expression),
        ParenthesizedExpressionSyntax pe => LastName(pe.Expression),
        CastExpressionSyntax cast => LastName(cast.Expression),
        BinaryExpressionSyntax b => LastName(b.Left) is { Length: > 0 } s ? s : LastName(b.Right),
        PrefixUnaryExpressionSyntax u => LastName(u.Operand),
        ConditionalAccessExpressionSyntax ca => LastName(ca.WhenNotNull),
        MemberBindingExpressionSyntax mb => mb.Name.Identifier.Text,
        GenericNameSyntax gn => gn.Identifier.Text,
        _ => "",
    };
}

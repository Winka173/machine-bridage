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
    // ------------------------------------------------------------------------------------------------ (b) hidden tables

    internal sealed class Table
    {
        public string File = "", Kind = "", Owner = "", Member = "", Sample = "";
        public int Line, Count, Gameplay;
        public bool Reachable;
        public List<Lit> Lits = new();
    }

    private static List<Table> ScanB(Compiler.Pair c, Graph g, List<Lit> lits)
    {
        var byPos = lits.ToDictionary(l => (l.File, l.Pos));
        var tables = new List<Table>();
        foreach (var (rel, tree) in c.Trees)
        {
            var sp = Repo.Short(rel);
            if (Registry.IsTunablesFile(rel)) continue;
            var model = c.Model(rel)!;
            foreach (var n in tree.GetRoot().DescendantNodes())
            {
                string? kind = null;
                IEnumerable<LiteralExpressionSyntax> inner = Array.Empty<LiteralExpressionSyntax>();
                switch (n)
                {
                    case InitializerExpressionSyntax ie when ie.IsKind(SyntaxKind.ArrayInitializerExpression) || ie.IsKind(SyntaxKind.CollectionInitializerExpression):
                    {
                        var direct = ie.Expressions.SelectMany(e => e is InitializerExpressionSyntax sub ? sub.Expressions : new SeparatedSyntaxList<ExpressionSyntax>().Add(e))
                            .Select(Unwrap).OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression)).ToList();
                        if (direct.Count < 2) continue;
                        var creation = ie.Parent?.ToString() ?? "";
                        kind = creation.Contains("Dictionary") ? "dictionary" : ie.IsKind(SyntaxKind.CollectionInitializerExpression) ? "collection" : "array";
                        inner = direct;
                        break;
                    }
                    case SwitchStatementSyntax ss:
                    {
                        var rets = ss.Sections.SelectMany(s => s.Statements.OfType<ReturnStatementSyntax>()).Select(r => r.Expression).Where(e => e != null)
                            .Select(e => Unwrap(e!)).OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression)).ToList();
                        if (rets.Count < 2) continue;
                        kind = "switch";
                        inner = rets;
                        break;
                    }
                    case SwitchExpressionSyntax se:
                    {
                        var arms = se.Arms.Select(a => Unwrap(a.Expression)).OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression)).ToList();
                        if (arms.Count < 2) continue;
                        kind = "switch_expression";
                        inner = arms;
                        break;
                    }
                    case ObjectCreationExpressionSyntax oc when oc.Type.ToString() is "Keyframe" or "AnimationCurve":
                        kind = "curve";
                        inner = oc.DescendantNodes().OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression));
                        break;
                    case EnumDeclarationSyntax ed when ed.Members.Any(m => m.EqualsValue != null):
                        kind = "enum";
                        inner = ed.DescendantNodes().OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression));
                        break;
                    case ConditionalExpressionSyntax ce when ce.WhenFalse is ConditionalExpressionSyntax:
                    {
                        if (ce.Parent is ConditionalExpressionSyntax) continue; // the outermost chain only
                        var vals = new List<LiteralExpressionSyntax>();
                        for (ExpressionSyntax e = ce; e is ConditionalExpressionSyntax cc; e = cc.WhenFalse)
                        {
                            if (Unwrap(cc.WhenTrue) is LiteralExpressionSyntax lt && lt.IsKind(SyntaxKind.NumericLiteralExpression)) vals.Add(lt);
                            if (cc.WhenFalse is not ConditionalExpressionSyntax && Unwrap(cc.WhenFalse) is LiteralExpressionSyntax lf && lf.IsKind(SyntaxKind.NumericLiteralExpression)) vals.Add(lf);
                        }
                        if (vals.Count < 3) continue;
                        kind = "ternary_chain";
                        inner = vals;
                        break;
                    }
                    case LiteralExpressionSyntax sl when sl.IsKind(SyntaxKind.StringLiteralExpression) && Regex.IsMatch(sl.Token.ValueText, @"\{\d+:[^}]*\d") :
                        tables.Add(new Table { File = sp, Kind = "format_string", Line = Syn.Line(sl), Owner = TypeName(sl), Count = 0, Sample = Snip(sl.ToString()) });
                        continue;
                    default: continue;
                }
                var t = new Table { File = sp, Kind = kind!, Line = Syn.Line(n), Owner = TypeName(n), Sample = Snip(n.ToString()) };
                var owner = g.Owner(n, model);
                t.Member = owner?.Symbol.Name ?? "";
                t.Reachable = owner?.Reachable ?? false;
                foreach (var l in inner)
                    if (byPos.TryGetValue((sp, l.SpanStart), out var lit)) { lit.FoundBy.Add('b'); t.Lits.Add(lit); }
                t.Count = t.Lits.Count;
                tables.Add(t);
            }
        }
        return tables;
    }

    private static ExpressionSyntax Unwrap(ExpressionSyntax e) => e switch
    {
        ParenthesizedExpressionSyntax p => Unwrap(p.Expression),
        PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression } u => u.Operand,
        CastExpressionSyntax c => Unwrap(c.Expression),
        _ => e,
    };

    // ------------------------------------------------------------------------------------------------ (c) hard-coded by ID / name

    internal sealed class IdCheck
    {
        public string File = "", Kind = "", Literal = "", Receiver = "", Owner = "", Member = "", LineText = "", DataHit = "", Flag = "";
        public int Line;
        public bool Reachable;
    }

    private static readonly Regex NotAnId = new(@"^(Data/|Resources/|Models/|[A-Za-z]+\.[a-z]{2,4}$)|[ {}]|^$");

    private static List<IdCheck> ScanC(Compiler.Pair c, Graph g)
    {
        var dataIds = DataIds();
        var list = new List<IdCheck>();
        foreach (var (rel, tree) in c.Trees)
        {
            var sp = Repo.Short(rel);
            if (!sp.StartsWith("Sim/") && !sp.StartsWith("Game/Match/")) continue;
            if (Registry.IsTunablesFile(rel)) continue;
            var model = c.Model(rel)!;
            var text = tree.GetText();
            foreach (var n in tree.GetRoot().DescendantNodes())
            {
                var found = new List<(string kind, string lit, ExpressionSyntax recv)>();
                switch (n)
                {
                    case BinaryExpressionSyntax b when b.IsKind(SyntaxKind.EqualsExpression) || b.IsKind(SyntaxKind.NotEqualsExpression):
                    {
                        var (sl, other) = b.Right is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } r ? (r, b.Left)
                            : b.Left is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } l ? (l, b.Right) : (null, null);
                        if (sl == null || other == null) break;
                        if (model.GetTypeInfo(other).Type?.SpecialType != SpecialType.System_String) break;
                        found.Add(("==", sl.Token.ValueText, other));
                        break;
                    }
                    case SwitchStatementSyntax ss when model.GetTypeInfo(ss.Expression).Type?.SpecialType == SpecialType.System_String:
                        foreach (var lab in ss.Sections.SelectMany(s => s.Labels).OfType<CaseSwitchLabelSyntax>())
                            if (lab.Value is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } sv) found.Add(("switch", sv.Token.ValueText, ss.Expression));
                        break;
                    case SwitchExpressionSyntax se when model.GetTypeInfo(se.GoverningExpression).Type?.SpecialType == SpecialType.System_String:
                        foreach (var arm in se.Arms)
                            foreach (var cp in arm.Pattern.DescendantNodesAndSelf().OfType<ConstantPatternSyntax>())
                                if (cp.Expression is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } sv2) found.Add(("switch", sv2.Token.ValueText, se.GoverningExpression));
                        break;
                    case IsPatternExpressionSyntax ip when model.GetTypeInfo(ip.Expression).Type?.SpecialType == SpecialType.System_String:
                        foreach (var cp in ip.Pattern.DescendantNodesAndSelf().OfType<ConstantPatternSyntax>())
                            if (cp.Expression is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } sv3) found.Add(("is", sv3.Token.ValueText, ip.Expression));
                        break;
                    case InvocationExpressionSyntax inv when inv.Expression is MemberAccessExpressionSyntax ma
                                                             && ma.Name.Identifier.Text is "StartsWith" or "EndsWith" or "Contains" or "Equals" or "IndexOf"
                                                             && inv.ArgumentList.Arguments.Count >= 1
                                                             && inv.ArgumentList.Arguments[0].Expression is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } a0:
                    {
                        var rt = model.GetTypeInfo(ma.Expression).Type;
                        if (rt?.SpecialType == SpecialType.System_String) found.Add((ma.Name.Identifier.Text, a0.Token.ValueText, ma.Expression));
                        else if (rt is INamedTypeSymbol nt && nt.TypeArguments.Length == 1 && nt.TypeArguments[0].SpecialType == SpecialType.System_String && ma.Name.Identifier.Text == "Contains")
                            found.Add(("set.Contains", a0.Token.ValueText, ma.Expression));
                        break;
                    }
                }
                foreach (var (kind, lit, recv) in found)
                {
                    if (NotAnId.IsMatch(lit) || lit.Length < 2) continue;
                    var owner = g.Owner(n, model);
                    var line = Syn.Line(n);
                    var member = owner?.Symbol.Name ?? "";
                    var hit = dataIds.TryGetValue(lit, out var h) ? h : dataIds.Where(kv => kind is "StartsWith" or "EndsWith" or "Contains" && (kind == "StartsWith" ? kv.Key.StartsWith(lit) : kind == "EndsWith" ? kv.Key.EndsWith(lit) : kv.Key.Contains(lit)))
                        .Select(kv => kv.Value.Split(':')[0] + ":" + kv.Value.Split(':')[1]).Distinct().Take(2).Aggregate("", (s, x) => s == "" ? x + " (prefix match)" : s);
                    list.Add(new IdCheck
                    {
                        File = sp, Line = line, Kind = kind, Literal = lit, Receiver = Snip(recv.ToString()), Owner = owner?.Symbol.ContainingType?.Name ?? TypeName(n),
                        Member = member, LineText = Snip(text.Lines[line - 1].ToString()), Reachable = owner?.Reachable ?? false, DataHit = hit,
                        Flag = ProposeFlag(kind, lit, member, recv.ToString(), hit),
                    });
                }
            }
        }
        return list;
    }

    private static string Snake(string s) => Regex.Replace(Regex.Replace(s, "([a-z0-9])([A-Z])", "$1_$2"), "[^A-Za-z0-9]+", "_").Trim('_').ToLowerInvariant();

    private static string ProposeFlag(string kind, string lit, string member, string recv, string hit)
    {
        var target = hit == "" ? "?" : hit.Split(' ')[0];
        var role = member switch
        {
            "" => "special_" + Snake(lit),
            _ when member.StartsWith("Is") || member.StartsWith("Has") || member.StartsWith("Can") => Snake(member),
            _ => Snake(member) + "_" + Snake(lit),
        };
        if (kind is "StartsWith" or "EndsWith" or "Contains") return $"tag \"{Snake(lit)}\" on every {target} whose id {kind.ToLowerInvariant()} \"{lit}\"; code reads def.Tags.Contains(\"{Snake(lit)}\")";
        if (recv.Contains("Kind") || recv.Contains("Mode") || recv.Contains("Type")) return $"enum / data value instead of the string \"{lit}\" ({recv}): a data field \"{Snake(member)}\" on the {target}";
        return $"flag \"{role}\" = true on {target} id \"{lit}\"; code reads def.Flags.Contains(\"{role}\")";
    }

    /// <summary>Every "id" in Resources/Data/**/*.json: id -> "file:block".</summary>
    private static Dictionary<string, string> DataIds()
    {
        var map = new Dictionary<string, string>(StringComparer.Ordinal);
        var dir = Repo.Abs("Assets/MachineBrigade/Resources/Data");
        if (!Directory.Exists(dir)) return map;
        foreach (var f in Directory.EnumerateFiles(dir, "*.json", SearchOption.AllDirectories))
        {
            try
            {
                using var doc = JsonDocument.Parse(File.ReadAllText(f), new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
                Walk(doc.RootElement, Path.GetFileName(f), "", map);
            }
            catch { /* not JSON */ }
        }
        return map;
    }

    private static void Walk(JsonElement e, string file, string block, Dictionary<string, string> map)
    {
        if (e.ValueKind == JsonValueKind.Object)
        {
            if (e.TryGetProperty("id", out var id) && id.ValueKind == JsonValueKind.String) map.TryAdd(id.GetString()!, $"{file}:{block}");
            foreach (var p in e.EnumerateObject()) Walk(p.Value, file, block == "" ? p.Name : block, map);
        }
        else if (e.ValueKind == JsonValueKind.Array)
            foreach (var x in e.EnumerateArray()) Walk(x, file, block, map);
    }

    // ------------------------------------------------------------------------------------------------ (d) Unity assets

    internal sealed class AssetValue
    {
        public string Asset = "", Script = "", Field = "", Value = "", Decision = "";
    }

    private static List<AssetValue> ScanD(Compiler.Pair c, Graph g)
    {
        var res = new List<AssetValue>();
        var guidToScript = new Dictionary<string, string>();
        foreach (var meta in Directory.EnumerateFiles(Repo.Abs(Repo.Scripts), "*.cs.meta", SearchOption.AllDirectories))
        {
            var rel = Repo.Short(Repo.Rel(meta[..^5]));
            if (!rel.StartsWith("Sim/") && !rel.StartsWith("Game/Match/")) continue;
            var m = Regex.Match(File.ReadAllText(meta), @"guid: ([0-9a-f]{32})");
            if (m.Success) guidToScript[m.Groups[1].Value] = rel;
        }
        var assetsRoot = Repo.Abs("Assets");
        foreach (var f in Directory.EnumerateFiles(assetsRoot, "*.*", SearchOption.AllDirectories).Where(p => p.EndsWith(".unity") || p.EndsWith(".prefab") || p.EndsWith(".asset")))
        {
            string text;
            try
            {
                if (new FileInfo(f).Length > 60_000_000) continue;
                text = File.ReadAllText(f);
            }
            catch { continue; }
            if (!text.StartsWith("%YAML")) continue;
            foreach (Match m in Regex.Matches(text, @"m_Script: \{fileID: 11500000, guid: ([0-9a-f]{32})"))
            {
                if (!guidToScript.TryGetValue(m.Groups[1].Value, out var script)) continue;
                var end = text.IndexOf("--- !u!", m.Index, StringComparison.Ordinal);
                var block = text[m.Index..(end < 0 ? text.Length : end)];
                var cls = Path.GetFileNameWithoutExtension(script).Split('.')[0];
                foreach (Match fm in Regex.Matches(block, @"^  (\w+): (-?[0-9.]+(?:e-?\d+)?)\s*$", RegexOptions.Multiline))
                {
                    var field = fm.Groups[1].Value;
                    if (field.StartsWith("m_")) continue;
                    var mem = g.Members.Values.FirstOrDefault(x => x.Symbol.ContainingType?.Name == cls && x.Symbol.Name == field);
                    res.Add(new AssetValue
                    {
                        Asset = Repo.Rel(f), Script = script, Field = field, Value = fm.Groups[2].Value,
                        Decision = mem == null ? "no such field in code (stale serialisation): ignore" : mem.Reachable ? "gameplay: read by the simulation -> data" : "visual: field not reachable from the simulation",
                    });
                }
                if (res.All(r => r.Script != script || r.Asset != Repo.Rel(f)))
                    res.Add(new AssetValue { Asset = Repo.Rel(f), Script = script, Field = "(no numeric field)", Decision = "none" });
            }
        }
        // Unity components the simulation could read (colliders, NavMeshAgent, Animator)
        foreach (var (rel, tree) in c.Trees.Where(t => Repo.Short(t.Key).StartsWith("Game/Match/") || Repo.Short(t.Key).StartsWith("Sim/")))
        {
            var model = c.Model(rel)!;
            foreach (var id in tree.GetRoot().DescendantNodes().OfType<IdentifierNameSyntax>().Where(i => i.Identifier.Text is "NavMeshAgent" or "Collider" or "BoxCollider" or "SphereCollider" or "Animator" or "Rigidbody" or "Physics"))
            {
                var owner = g.Owner(id, model);
                res.Add(new AssetValue
                {
                    Asset = Repo.Short(rel) + ":" + Syn.Line(id), Script = id.Identifier.Text, Field = owner?.Symbol.Name ?? "", Value = "",
                    Decision = owner?.Reachable == true ? "CHECK: Unity component used by code reachable from the simulation" : "visual: Unity component in presentation code",
                });
            }
        }
        return res;
    }

    // ------------------------------------------------------------------------------------------------ (e) entity lifecycle

    private static readonly (string step, Regex rx)[] Steps =
    {
        ("1_trien_khai", new Regex(@"Deploy|Spawn|Drop|Place|Queue|Card|Opening|Reinforce|Garrison|Summon|Build(?!ing)", RegexOptions.Compiled)),
        ("2_di_chuyen", new Regex(@"Move|Movement|Path|Steer|Nav|Traffic|Speed|Turn|Avoid|Push|Stuck|Formation|Hover|Orbit|Rail|Lane|Leash|Approach|Ram", RegexOptions.Compiled)),
        ("3_phat_hien", new Regex(@"Vision|Sight|Detect|Spot|Visible|Reveal|Fog|Stealth|Radar|Intel|Contact|Scout|Smoke|Conceal", RegexOptions.Compiled)),
        ("4_chon_muc_tieu", new Regex(@"Target|Pick|Choose|Score|Priority|Threat|Select|Acquire|Engage", RegexOptions.Compiled)),
        ("5_ban", new Regex(@"Fire|Shoot|Launch|Salvo|Burst|Reload|Volley|Aim|Weapon|Cooldown|Rearm|Magazine|Ammo|Barrel", RegexOptions.Compiled)),
        ("6_dan_bay", new Regex(@"Projectile|Missile|Munition|Flight|Shell|Rocket|Ballistic|Bomb|Drone|Guid|Flare|Aps|Intercept|Jam|Arc|Lob", RegexOptions.Compiled)),
        ("7_trung", new Regex(@"Hit|Impact|Splash|Blast|Explode|Detonat|Fuse|Miss|Scatter|Accuracy", RegexOptions.Compiled)),
        ("8_sat_thuong", new Regex(@"Damage|Armou?r|Penetrat|Health|\bHp|Burn|Status|Shield|Repair|Heal|Stun|Fragment", RegexOptions.Compiled)),
        ("9_chet_xac", new Regex(@"Death|Die|Kill|Destroy|Wreck|Corpse|Dead|Debris", RegexOptions.Compiled)),
        ("10_hoan_cp_xay_lai", new Regex(@"Refund|Rebuild|Bounty|Reward|Income|Supply|Economy|Cp\b|Upkeep|Respawn", RegexOptions.Compiled)),
    };

    private static readonly (string entity, Regex rx)[] Entities =
    {
        ("may_bay", new Regex(@"Air(?!borne)|Jet|Plane|Bomber|Fighter|Aircraft|Sortie|Dogfight", RegexOptions.Compiled)),
        ("truc_thang", new Regex(@"Heli|Rotor|Hover", RegexOptions.Compiled)),
        ("tau", new Regex(@"Naval|Ship|Sea|Boat|Carrier|Deck", RegexOptions.Compiled)),
        ("drone", new Regex(@"Drone|Uav|Swarm|Loiter", RegexOptions.Compiled)),
        ("ten_lua", new Regex(@"Missile|Rocket|Sam\b|Guided|Seeker", RegexOptions.Compiled)),
        ("bom", new Regex(@"Bomb|Cluster|Napalm|Bomblet", RegexOptions.Compiled)),
        ("dan_phao", new Regex(@"Shell|Artillery|Mortar|Howitzer|Ballistic|Battery", RegexOptions.Compiled)),
        ("boss", new Regex(@"Boss|BigAttack|BigStrike|Escort|Titan|Phase", RegexOptions.Compiled)),
        ("thap", new Regex(@"Tower|Turret", RegexOptions.Compiled)),
        ("tuong", new Regex(@"Wall|Gate|Barrier", RegexOptions.Compiled)),
        ("nha_chinh", new Regex(@"\bHq|Hq[A-Z]|Base(?!line)|Headquarter|Fortress", RegexOptions.Compiled)),
        ("quan_don_tru", new Regex(@"Garrison", RegexOptions.Compiled)),
        ("dong_minh", new Regex(@"Ally|Allied|Neutral|Friendly", RegexOptions.Compiled)),
        ("the_ho_tro", new Regex(@"Support|Strike|Card|Ability|Skill|Commander", RegexOptions.Compiled)),
        ("xe_mat_dat", new Regex(@"Vehicle|Tank|Ground|Unit|Convoy|Truck", RegexOptions.Compiled)),
    };

    internal sealed class Life
    {
        public readonly Dictionary<(string entity, string step), int> Matrix = new();
    }

    private static Life ScanE(Graph g, List<Lit> lits)
    {
        var life = new Life();
        var reach = g.Members.Values.Where(m => m.Reachable).ToList();
        var stepSets = new Dictionary<string, HashSet<Graph.Member>>();
        foreach (var (step, rx) in Steps)
        {
            var seeds = reach.Where(m => rx.IsMatch(m.Symbol.Name)).ToList();
            stepSets[step] = Graph.Within(seeds, 2);
        }
        foreach (var l in lits.Where(l => l.Reachable && l.M != null))
        {
            var steps = Steps.Where(s => stepSets[s.step].Contains(l.M!) || s.rx.IsMatch(l.CtxName)).Select(s => s.step).ToList();
            var hay = l.File + " " + l.Owner + " " + l.Member + " " + l.CtxName;
            var ents = Entities.Where(e => e.rx.IsMatch(hay)).Select(e => e.entity).Take(2).ToList();
            if (ents.Count == 0) ents.Add("chung");
            if (steps.Count == 0) continue;
            l.FoundBy.Add('e');
            l.Lifecycle = string.Join("|", ents) + ":" + string.Join("|", steps);
            foreach (var e in ents)
                foreach (var s in steps)
                    life.Matrix[(e, s)] = life.Matrix.GetValueOrDefault((e, s)) + 1;
        }
        return life;
    }

    // ------------------------------------------------------------------------------------------------ (f) per system class

    internal sealed class SysItem
    {
        public string Class = "", File = "", Member = "", What = "", Value = "", Decision = "";
        public int Line;
        public Lit? Lit;
    }

    private static readonly Regex SystemClass = new(@"(System|Director|Mode|Session|Ai)$", RegexOptions.Compiled);

    private static List<SysItem> ScanF(Compiler.Pair c, Graph g, List<Lit> lits)
    {
        var items = new List<SysItem>();
        var byPos = lits.ToDictionary(l => (l.File, l.Pos));
        foreach (var (rel, tree) in c.Trees)
        {
            var sp = Repo.Short(rel);
            if (!sp.StartsWith("Sim/") && !sp.StartsWith("Game/Match/")) continue;
            foreach (var cls in tree.GetRoot().DescendantNodes().OfType<ClassDeclarationSyntax>().Where(k => SystemClass.IsMatch(k.Identifier.Text)))
            {
                foreach (var lit in cls.DescendantNodes().OfType<LiteralExpressionSyntax>().Where(l => l.IsKind(SyntaxKind.NumericLiteralExpression)))
                {
                    if (lit.Ancestors().OfType<ClassDeclarationSyntax>().First() != cls) continue; // nested classes report themselves
                    if (!byPos.TryGetValue((sp, lit.SpanStart), out var l)) continue;
                    l.FoundBy.Add('f');
                    l.System = cls.Identifier.Text;
                    var what = l.Context is "const_field" or "static_field" or "field_init" or "property_init" ? "field" : l.Context == "param_default" ? "parameter default" : "literal";
                    items.Add(new SysItem { Class = cls.Identifier.Text, File = sp, Line = l.Line, Member = l.Member, What = what, Value = l.Text, Lit = l });
                }
                // members already in data: fields / properties whose value reads SimTunables or the catalog
                foreach (var m in cls.Members)
                {
                    var init = m switch
                    {
                        PropertyDeclarationSyntax p => (SyntaxNode?)p.ExpressionBody ?? p.Initializer,
                        FieldDeclarationSyntax f => f.Declaration.Variables.FirstOrDefault()?.Initializer,
                        _ => null,
                    };
                    if (init == null || !init.ToString().Contains("SimTunables")) continue;
                    items.Add(new SysItem
                    {
                        Class = cls.Identifier.Text, File = sp, Line = Syn.Line(m), Member = m is PropertyDeclarationSyntax pp ? pp.Identifier.Text : ((FieldDeclarationSyntax)m).Declaration.Variables[0].Identifier.Text,
                        What = "field", Value = Snip(init.ToString()), Decision = "da_trong_du_lieu (tunables.json)",
                    });
                }
            }
        }
        return items;
    }
}

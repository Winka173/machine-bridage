using System.Diagnostics;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;

namespace MbConst;

/// <summary>
/// The equivalence checker (§2.2): for one or more (base, head) pairs, proves that the C# changes are only literal →
/// SimTunables swaps (a), that every key's default, JSON value and original literal agree (b), that no key took two
/// literals (c), that the code compiles with no new warnings (d) and that no expression changed type (e).
/// </summary>
internal static class Check
{
    private sealed class Site
    {
        public string File = "", Path = "", How = "", OldSnippet = "";
        public List<TypedValue>? Array;
        public string? Cast;
        public int OldLine, NewLine, OldPos, NewPos;
        public TypedValue Literal;
        public string LiteralText = "";
        public string PairName = "";
    }

    private sealed class PairResult
    {
        public string Name = "", Base = "", Head = "";
        public int FilesChanged, HunksTotal, HunksLiteralOnly;
        public readonly List<string> NonLiteral = new();
        public readonly List<string> Rewrites = new();
        public readonly HashSet<string> NewKeys = new();
        public readonly List<(string file, int line, TypedValue val, string text)> DeletedLiterals = new();
        public readonly List<string> ReconstructFail = new();
        public readonly List<Site> Sites = new();
        public readonly List<string> TypeChanges = new();
        public readonly List<string> FoldingNotes = new();
        public readonly List<string> Errors = new();
        public readonly List<string> NewWarnings = new();
        public int OldWarnings, HeadWarnings;
        public bool Compiled;
        public string? Label;
    }

    private static readonly HashSet<string> ConversionWarnings = new() { "CS0652", "CS0675", "CS1718", "CS0464", "CS0458", "CS0472", "CS0665", "CS0221", "CS0220", "CS0162", "CS0429" };

    public static int Run(string[] args)
    {
        var pairs = new List<(string b, string h, string? label)>();
        string? basev = null, head = "WORKTREE", outPath = null, registryRev = null;
        var compile = true;
        var dotnet = false;
        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--base": basev = args[++i]; break;
                case "--head": head = args[++i]; break;
                case "--pair":
                {
                    var parts = args[++i].Split('=', 2);
                    var bh = parts[0].Split(':');
                    pairs.Add((bh[0], bh.Length > 1 ? bh[1] : "WORKTREE", parts.Length > 1 ? parts[1] : null));
                    break;
                }
                case "--out": outPath = args[++i]; break;
                case "--registry": registryRev = args[++i]; break;
                case "--no-compile": compile = false; break;
                case "--dotnet": dotnet = true; break;
                case "--repo": Repo.Root = args[++i]; break;
                case "--unity": Compiler.UnityEditor = args[++i]; break;
                case "--script-assemblies": Compiler.ScriptAssemblies = args[++i]; break;
            }
        }
        if (basev != null) pairs.Add((basev, head!, null));
        if (pairs.Count == 0) { Console.Error.WriteLine("usage: mbconst check --base <rev> [--head <rev>|WORKTREE] | --pair <base>:<head>[=label] ... [--out file] [--no-compile] [--dotnet]"); return 2; }
        outPath ??= Repo.Abs("Docs/export/current/_qa/equivalence.md");

        var results = new List<PairResult>();
        var bases = new List<SourceSet>();
        SourceSet? last = null;
        foreach (var (b, h, label) in pairs)
        {
            Console.WriteLine($"check {b} -> {h} ...");
            var oldS = SourceSet.Load(b);
            var newS = SourceSet.Load(h);
            bases.Add(oldS);
            last = newS;
            results.Add(CheckPair(oldS, newS, compile, label));
        }
        var finalReg = Registry.Load(registryRev == null ? SourceSet.FromWorktree() : SourceSet.Load(registryRev));
        var md = Report(results, finalReg, bases, last!, dotnet ? DotnetBuild() : null, out var pass);
        Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
        File.WriteAllText(outPath, md);
        Console.WriteLine($"{(pass ? "PASS" : "FAIL")}: {outPath}");
        return pass ? 0 : 1;
    }

    // ------------------------------------------------------------------------------------------------ one pair

    private static PairResult CheckPair(SourceSet oldS, SourceSet newS, bool compile, string? label)
    {
        var r = new PairResult { Name = $"{oldS.Name} → {newS.Name}", Base = oldS.Name, Head = newS.Name, Label = label };
        var changed = oldS.Files.Keys.Union(newS.Files.Keys)
            .Where(f => !Registry.IsTunablesFile(f))
            .Where(f => !oldS.Files.TryGetValue(f, out var o) || !newS.Files.TryGetValue(f, out var n) || Norm(o) != Norm(n))
            .OrderBy(f => f, StringComparer.Ordinal).ToList();
        r.FilesChanged = changed.Count;
        var regOld = Registry.Load(oldS);
        foreach (var k in Registry.Load(newS).Keys.Keys) if (!regOld.Keys.ContainsKey(k)) r.NewKeys.Add(k);
        Compiler.Pair? oldC = null, newC = null;
        if (compile)
        {
            oldC = Compiler.Build(oldS);
            newC = Compiler.Build(newS);
        }
        foreach (var f in changed)
        {
            if (!oldS.Files.ContainsKey(f)) { r.NonLiteral.Add($"{Repo.Short(f)}: new file"); continue; }
            if (!newS.Files.ContainsKey(f)) { r.NonLiteral.Add($"{Repo.Short(f)}: file deleted"); continue; }
            var parse = f.Contains("/Sim/") ? Compiler.SimParse : Compiler.GameParse;
            var oldT = oldC?.Trees.GetValueOrDefault(f) ?? CSharpSyntaxTree.ParseText(oldS.Files[f], parse, f);
            var newT = newC?.Trees.GetValueOrDefault(f) ?? CSharpSyntaxTree.ParseText(newS.Files[f], parse, f);
            _newModel = newC?.Model(f);
            // pass 2: "T x = lit" -> "T? x = null" + "(x ?? field)" is undone first; the rest of the proof runs on the undone text
            var undone = UndoNullableDefaults(f, oldT, newT, r, out var mapBack);
            var n0 = r.Sites.Count;
            CompareFile(f, oldT, undone ?? newT, r);
            if (undone != null)
                for (var si = n0; si < r.Sites.Count; si++)
                {
                    var st = r.Sites[si];
                    if (st.How == "param_default_nullable") continue;
                    st.NewPos = mapBack(st.NewPos);
                    st.NewLine = newT.GetText().Lines.GetLineFromPosition(st.NewPos).LineNumber + 1;
                }
            _newModel = null;
        }
        foreach (var s in r.Sites) s.PairName = r.Name;
        if (compile)
        {
            TypeCheck(r, oldC!, newC!);
            var oldD = Compiler.Diagnostics(oldC!);
            var newD = Compiler.Diagnostics(newC!);
            r.Compiled = true;
            r.Errors.AddRange(newD.Where(d => d.Severity == DiagnosticSeverity.Error).Select(Fmt));
            var oldW = oldD.Where(d => d.Severity == DiagnosticSeverity.Warning).Select(WKey).GroupBy(x => x).ToDictionary(g => g.Key, g => g.Count());
            r.OldWarnings = oldW.Values.Sum();
            var newWs = newD.Where(d => d.Severity == DiagnosticSeverity.Warning).ToList();
            r.HeadWarnings = newWs.Count;
            foreach (var g in newWs.GroupBy(WKey))
            {
                var extra = g.Count() - oldW.GetValueOrDefault(g.Key);
                foreach (var d in g.Take(Math.Max(0, extra))) r.NewWarnings.Add((ConversionWarnings.Contains(d.Id) ? "**conversion/constant** " : "") + Fmt(d));
            }
        }
        return r;
    }

    private static string Norm(string s) => s.Replace("\r\n", "\n");

    /// <summary>
    /// Pack 2 pass 2 (09/10): the move tool's parameter-default rewrite. Old: "T x = D"; new: "T? x = null" and every read of
    /// x in the member's body "(x ?? SimTunables.F)". Undoing it (the type back to T, null back to D, each "(x ?? F)" back to
    /// x) must give the old member exactly (the rest of the check proves that on the undone text, rebuilt tree included);
    /// every read of x must be wrapped (a bare x would now be a T?); F's default must be D (a site for checks b, c, e).
    /// </summary>
    private static SyntaxTree? UndoNullableDefaults(string f, SyntaxTree oldT, SyntaxTree newT, PairResult r, out Func<int, int> mapBack)
    {
        mapBack = p => p;
        var oldRoot = oldT.GetRoot();
        var newRoot = newT.GetRoot();
        var edits = new List<(int start, int len, string text)>();
        var found = new List<Site>();
        var notes = new List<string>();
        foreach (var member in newRoot.DescendantNodes().OfType<BaseMethodDeclarationSyntax>())
        {
            foreach (var par in member.ParameterList.Parameters)
            {
                if (par.Type is not NullableTypeSyntax { ElementType: PredefinedTypeSyntax et } nt
                    || par.Default?.Value is not LiteralExpressionSyntax { RawKind: (int)SyntaxKind.NullLiteralExpression } nul)
                    continue;
                var old = Counterpart(oldRoot, member);
                var op = old?.ParameterList.Parameters.FirstOrDefault(q => q.Identifier.Text == par.Identifier.Text);
                if (op?.Default == null || op.Type?.ToString() != et.ToString()) continue;
                var d = TypedValue.FromExpression(op.Default.Value);
                if (d == null) continue;
                var name = par.Identifier.Text;
                var body = (SyntaxNode?)member.Body ?? member.ExpressionBody;
                if (body == null) continue;
                var wraps = body.DescendantNodes().OfType<ParenthesizedExpressionSyntax>()
                    .Where(pe => pe.Expression is BinaryExpressionSyntax { RawKind: (int)SyntaxKind.CoalesceExpression } be
                                 && be.Left is IdentifierNameSyntax lid && lid.Identifier.Text == name && Syn.TunablePath(be.Right) != null).ToList();
                var wrapped = new HashSet<SyntaxNode>(wraps.Select(w => (SyntaxNode)((BinaryExpressionSyntax)w.Expression).Left));
                var bare = body.DescendantNodes().OfType<IdentifierNameSyntax>().Where(i => i.Identifier.Text == name && !wrapped.Contains(i)
                        && !(i.Parent is MemberAccessExpressionSyntax ma && ma.Name == i) && i.Parent is not NameColonSyntax and not NameEqualsSyntax
                        && !i.Ancestors().OfType<InvocationExpressionSyntax>().Any(inv => inv.Expression is IdentifierNameSyntax { Identifier.Text: "nameof" }))
                    .ToList();
                if (bare.Count > 0 || wraps.Count == 0) continue;
                edits.Add((nt.SpanStart, nt.Span.Length, et.ToString()));
                edits.Add((nul.SpanStart, nul.Span.Length, op.Default.Value.ToString()));
                foreach (var w in wraps)
                {
                    var chain = ((BinaryExpressionSyntax)w.Expression).Right;
                    edits.Add((w.SpanStart, w.Span.Length, name));
                    found.Add(new Site
                    {
                        File = f, Path = Syn.TunablePath(chain)!, How = "param_default_nullable", OldLine = Syn.Line(op), NewLine = Syn.Line(chain),
                        OldPos = op.Default.Value.SpanStart, NewPos = chain.SpanStart, Literal = d.Value, LiteralText = op.Default.Value.ToString(),
                        OldSnippet = op.ToString(),
                    });
                }
                notes.Add($"{Repo.Short(f)}:{Syn.Line(par)} default parameter -> nullable + (x ?? field) (pass 2 pattern): {name} = {op.Default.Value}, {wraps.Count} read(s) wrapped, none bare");
            }
        }
        if (edits.Count == 0) return null;
        edits.Sort((a, b) => a.start.CompareTo(b.start));
        var text = newT.GetText().ToString();
        var sb = new StringBuilder();
        var at = 0;
        var map = new List<(int primeStart, int primeEnd, int newStart, int newEnd)>();
        foreach (var e in edits)
        {
            if (e.start < at) return null; // overlapping: the plain diff reports the change
            sb.Append(text, at, e.start - at);
            var ps = sb.Length;
            sb.Append(e.text);
            map.Add((ps, sb.Length, e.start, e.start + e.len));
            at = e.start + e.len;
        }
        sb.Append(text, at, text.Length - at);
        mapBack = q =>
        {
            var delta = 0;
            foreach (var m in map)
            {
                if (q < m.primeStart) break;
                if (q < m.primeEnd) return m.newStart;
                delta = m.newEnd - m.primeEnd;
            }
            return q + delta;
        };
        r.Sites.AddRange(found);
        r.Rewrites.AddRange(notes);
        return CSharpSyntaxTree.ParseText(sb.ToString(), (CSharpParseOptions)newT.Options, f);
    }

    private static BaseMethodDeclarationSyntax? Counterpart(SyntaxNode oldRoot, BaseMethodDeclarationSyntax member)
    {
        static string Name(BaseMethodDeclarationSyntax m) => m switch { MethodDeclarationSyntax mm => mm.Identifier.Text, ConstructorDeclarationSyntax => ".ctor", _ => "" };
        static string Owner(SyntaxNode m) => (m.Parent as BaseTypeDeclarationSyntax)?.Identifier.Text ?? "";
        var names = member.ParameterList.Parameters.Select(p => p.Identifier.Text).ToList();
        return oldRoot.DescendantNodes().OfType<BaseMethodDeclarationSyntax>().FirstOrDefault(m => Name(m) == Name(member) && Owner(m) == Owner(member)
            && m.ParameterList.Parameters.Select(p => p.Identifier.Text).SequenceEqual(names));
    }

    private static string WKey(Diagnostic d) => d.Id + "|" + Repo.Short(d.Location.SourceTree?.FilePath ?? "") + "|" + Regex.Replace(d.GetMessage(), @"\d+", "#");

    private static string Fmt(Diagnostic d)
    {
        var p = d.Location.GetLineSpan();
        return $"{Repo.Short(p.Path)}:{p.StartLinePosition.Line + 1} {d.Id} {d.GetMessage()}";
    }

    private sealed record Hunk(int OldStart, int OldCount, int NewStart, int NewCount);

    /// <summary>Line hunks between the two texts (Myers-free: LCS on lines with the common prefix and suffix cut off).</summary>
    private static List<Hunk> Hunks(SourceText a, SourceText b)
    {
        var al = a.Lines.Select(l => a.ToString(l.Span).TrimEnd()).ToArray();
        var bl = b.Lines.Select(l => b.ToString(l.Span).TrimEnd()).ToArray();
        var ops = Lcs.Diff(al, bl, (x, y) => x == y);
        var hunks = new List<Hunk>();
        int i = 0, j = 0, k = 0;
        while (k < ops.Count)
        {
            if (ops[k] == Lcs.Op.Equal) { i++; j++; k++; continue; }
            int si = i, sj = j;
            while (k < ops.Count && ops[k] != Lcs.Op.Equal)
            {
                if (ops[k] == Lcs.Op.Delete) i++; else j++;
                k++;
            }
            hunks.Add(new Hunk(si, i - si, sj, j - sj));
        }
        return hunks;
    }

    private static TextSpan LinesSpan(SourceText t, int start, int count)
    {
        if (count == 0)
        {
            var pos = start < t.Lines.Count ? t.Lines[start].Start : t.Length;
            return new TextSpan(pos, 0);
        }
        return TextSpan.FromBounds(t.Lines[start].Start, t.Lines[start + count - 1].End);
    }

    private static void CompareFile(string f, SyntaxTree oldT, SyntaxTree newT, PairResult r)
    {
        var oldText = oldT.GetText();
        var newText = newT.GetText();
        var oldRoot = oldT.GetRoot();
        var newRoot = newT.GetRoot();
        var replacements = new List<(int start, int len, string oldText)>();
        var fileOk = true;
        foreach (var h in Hunks(oldText, newText))
        {
            r.HunksTotal++;
            var os = LinesSpan(oldText, h.OldStart, h.OldCount);
            var ns = LinesSpan(newText, h.NewStart, h.NewCount);
            var ot = oldRoot.DescendantTokens(os).Where(t => os.Contains(t.Span) && t.Span.Length > 0).ToList();
            var nt = newRoot.DescendantTokens(ns).Where(t => ns.Contains(t.Span) && t.Span.Length > 0).ToList();
            var sites = new List<Site>();
            var reps = new List<(int, int, string)>();
            var bad = new List<string>();
            // member rewrites (const / static readonly field -> expression-bodied property reading SimTunables or the same expression)
            var oldMembers = MembersIn(oldRoot, os);
            var newMembers = MembersIn(newRoot, ns);
            var skipOld = new HashSet<SyntaxToken>();
            var skipNew = new HashSet<SyntaxToken>();
            foreach (var om in oldMembers.OfType<FieldDeclarationSyntax>())
                MemberRewrite(f, om, newMembers, sites, reps, bad, skipOld, skipNew, r);
            var a = ot.Where(t => !skipOld.Contains(t)).ToList();
            var b = nt.Where(t => !skipNew.Contains(t)).ToList();
            var badBlocks = new List<(List<SyntaxToken> del, List<SyntaxToken> ins)>();
            if ((long)a.Count * b.Count > 6_000_000) bad.Add($"hunk too large to align ({a.Count} x {b.Count} tokens)");
            else
            {
                var ops = Lcs.Diff(a, b, (x, y) => x.RawKind == y.RawKind && x.ValueText == y.ValueText);
                int i = 0, j = 0, k = 0;
                while (k < ops.Count)
                {
                    if (ops[k] == Lcs.Op.Equal) { i++; j++; k++; continue; }
                    var del = new List<SyntaxToken>();
                    var ins = new List<SyntaxToken>();
                    while (k < ops.Count && ops[k] != Lcs.Op.Equal)
                    {
                        if (ops[k] == Lcs.Op.Delete) del.Add(a[i++]); else ins.Add(b[j++]);
                        k++;
                    }
                    var before = bad.Count;
                    ClassifyBlock(f, del, ins, j < b.Count ? b[j].SpanStart : -1, newRoot, sites, reps, bad);
                    if (bad.Count > before) badBlocks.Add((del, ins));
                }
            }
            // lane B's manual pattern: "T x = D" parameter -> "T? xOrDefault = null" + "var x = xOrDefault ?? D;"
            if (badBlocks.Count > 0 && badBlocks.Count == bad.Count && DefaultParamPattern(oldRoot, newRoot, badBlocks, out var what))
            {
                bad.Clear();
                r.Rewrites.Add($"{Repo.Short(f)}:{h.NewStart + 1} {what}");
                fileOk = false; // the rebuilt-tree proof cannot undo this pattern; the pattern check stands for it
            }
            if (bad.Count == 0) { r.HunksLiteralOnly++; r.Sites.AddRange(sites); replacements.AddRange(reps); }
            else
            {
                fileOk = false;
                var oldLine = h.OldCount > 0 ? Snip(oldText.ToString(os)) : "(none)";
                var newLine = h.NewCount > 0 ? Snip(newText.ToString(ns)) : "(none)";
                r.NonLiteral.Add($"{Repo.Short(f)}:{h.NewStart + 1} ({string.Join("; ", bad.Distinct().Take(2))}) old `{oldLine}` new `{newLine}`");
                r.Sites.AddRange(sites); // the literal swaps in a mixed hunk still count for (b), (c), (e)
                foreach (var t in ot.Where(t => t.IsKind(SyntaxKind.NumericLiteralToken) || t.IsKind(SyntaxKind.TrueKeyword) || t.IsKind(SyntaxKind.FalseKeyword)))
                    r.DeletedLiterals.Add((f, Syn.Line(t), TypedValue.FromToken(t)!.Value, t.Text));
            }
        }
        // the normalised-tree proof: undo the swaps in the new text and compare with the old tree, trivia ignored
        if (fileOk && replacements.Count > 0)
        {
            var sb = new StringBuilder(newText.ToString());
            foreach (var (start, len, old) in replacements.OrderByDescending(x => x.start)) sb.Remove(start, len).Insert(start, old);
            var rebuilt = CSharpSyntaxTree.ParseText(sb.ToString(), (CSharpParseOptions)newT.Options);
            if (!SyntaxFactory.AreEquivalent(oldRoot, rebuilt.GetRoot(), topLevel: false))
                r.ReconstructFail.Add(Repo.Short(f));
        }
    }

    private static string Snip(string s)
    {
        s = Regex.Replace(s, @"\s+", " ").Trim().Replace("`", "'");
        return s.Length > 150 ? s[..150] + "…" : s;
    }

    private static List<MemberDeclarationSyntax> MembersIn(SyntaxNode root, TextSpan span) =>
        root.DescendantNodes(span).OfType<MemberDeclarationSyntax>()
            .Where(m => m is FieldDeclarationSyntax or PropertyDeclarationSyntax && span.IntersectsWith(m.Span)).ToList();

    private static ExpressionSyntax Strip(ExpressionSyntax e, out string? cast, out bool negated)
    {
        cast = null;
        negated = false;
        while (true)
        {
            switch (e)
            {
                case ParenthesizedExpressionSyntax p: e = p.Expression; continue;
                case CastExpressionSyntax c: cast ??= c.Type.ToString(); e = c.Expression; continue;
                case PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression } u: negated = !negated; e = u.Operand; continue;
            }
            return e;
        }
    }

    /// <summary>A const / static readonly field turned into expression-bodied properties of the same names (lane B, mbconst move).</summary>
    private static void MemberRewrite(string f, FieldDeclarationSyntax om, List<MemberDeclarationSyntax> newMembers, List<Site> sites,
        List<(int, int, string)> reps, List<string> bad, HashSet<SyntaxToken> skipOld, HashSet<SyntaxToken> skipNew, PairResult r)
    {
        if (!om.Modifiers.Any(SyntaxKind.ConstKeyword) && !om.Modifiers.Any(SyntaxKind.StaticKeyword)) return;
        var props = new List<PropertyDeclarationSyntax>();
        foreach (var v in om.Declaration.Variables)
        {
            var nm = newMembers.OfType<PropertyDeclarationSyntax>().FirstOrDefault(p => p.Identifier.Text == v.Identifier.Text && p.ExpressionBody != null);
            if (nm == null || v.Initializer == null) return;
            props.Add(nm);
        }
        var how0 = om.Modifiers.Any(SyntaxKind.ConstKeyword) ? "const_to_property" : "static_to_property";
        var localSites = new List<Site>();
        var localBad = new List<string>();
        var typeNotes = new List<string>();
        for (var idx = 0; idx < props.Count; idx++)
        {
            var v = om.Declaration.Variables[idx];
            var nm = props[idx];
            var init = v.Initializer!.Value;
            var body = nm.ExpressionBody!.Expression;
            var core = Strip(body, out var cast, out var neg);
            var path = TP(core);
            var typeNote = om.Declaration.Type.ToString() == nm.Type.ToString() ? "" : $" (type {om.Declaration.Type} -> {nm.Type})";
            if (typeNote != "") typeNotes.Add($"{Repo.Short(f)}:{Syn.Line(nm)} {nm.Identifier.Text}:{typeNote}");
            var lit = TypedValue.FromExpression(init);
            var arr = init is InitializerExpressionSyntax ie ? ie.Expressions.Select(TypedValue.FromExpression).ToList() : null;
            if (path != null && (lit != null || arr != null && arr.All(x => x != null)))
            {
                var litTok = init.DescendantTokens().FirstOrDefault(t => t.IsKind(SyntaxKind.NumericLiteralToken) || t.IsKind(SyntaxKind.TrueKeyword) || t.IsKind(SyntaxKind.FalseKeyword));
                var initNeg = init is PrefixUnaryExpressionSyntax;
                if (lit != null && initNeg != neg) { localBad.Add($"{nm.Identifier.Text}: sign differs"); continue; }
                localSites.Add(new Site
                {
                    File = f, Path = path, How = (arr != null ? "array_to_property" : how0) + (cast != null ? $" (cast {cast})" : "") + typeNote,
                    OldLine = Syn.Line(v), NewLine = Syn.Line(nm), OldPos = litTok.SpanStart, NewPos = core.SpanStart,
                    Literal = lit ?? arr![0]!.Value, Array = arr?.Select(x => x!.Value).ToList(),
                    LiteralText = arr != null ? init.ToString() : litTok.Text, OldSnippet = om.ToString(), Cast = cast,
                });
                continue;
            }
            // the same expression (a const chain turned into properties): token-equal initializer and body
            var ia = init.DescendantTokens().ToList();
            var ib = body.DescendantTokens().ToList();
            if (ia.Select(t => t.ValueText).SequenceEqual(ib.Select(t => t.ValueText))) continue;
            // the initializer with literal swaps inside (e.g. "EscortTicks * 0.05f")
            var ops = Lcs.Diff(ia, ib, (x, y) => x.RawKind == y.RawKind && x.ValueText == y.ValueText);
            int i = 0, j = 0, k = 0;
            while (k < ops.Count)
            {
                if (ops[k] == Lcs.Op.Equal) { i++; j++; k++; continue; }
                var del = new List<SyntaxToken>();
                var ins = new List<SyntaxToken>();
                while (k < ops.Count && ops[k] != Lcs.Op.Equal)
                {
                    if (ops[k] == Lcs.Op.Delete) del.Add(ia[i++]); else ins.Add(ib[j++]);
                    k++;
                }
                ClassifyBlock(f, del, ins, -1, body.SyntaxTree.GetRoot(), localSites, new List<(int, int, string)>(), localBad);
            }
        }
        if (localBad.Count > 0) return; // left to the token diff, which reports it
        r.TypeChanges.AddRange(typeNotes);
        foreach (var t in om.DescendantTokens()) skipOld.Add(t);
        foreach (var p in props) foreach (var t in p.DescendantTokens()) skipNew.Add(t);
        foreach (var s in localSites) if (s.How == "inline") s.How = how0 + " (expression)";
        sites.AddRange(localSites);
        var first = props.Min(p => p.SpanStart);
        var last = props.Max(p => p.Span.End);
        reps.Add((first, last - first, om.ToString()));
    }

    /// <summary>
    /// Lane B's manual rewrite of a default parameter that read a moved constant: "T x = D" became "T? xOrDefault = null"
    /// with "var x = xOrDefault ?? D;" in the body. Equivalent: a call without the argument gets D at run time.
    /// </summary>
    private static bool DefaultParamPattern(SyntaxNode oldRoot, SyntaxNode newRoot, List<(List<SyntaxToken> del, List<SyntaxToken> ins)> blocks, out string what)
    {
        what = "";
        var found = new List<string>();
        foreach (var (del, ins) in blocks)
        {
            if (ins.Count == 0) return false;
            var newMethod = ins[0].Parent?.AncestorsAndSelf().OfType<MethodDeclarationSyntax>().FirstOrDefault();
            if (newMethod == null) return false;
            var ok = false;
            foreach (var p in newMethod.ParameterList.Parameters)
            {
                if (!p.Identifier.Text.EndsWith("OrDefault") || p.Type is not NullableTypeSyntax nt || p.Default?.Value.ToString() != "null") continue;
                var x = p.Identifier.Text[..^"OrDefault".Length];
                var decl = newMethod.DescendantNodes().OfType<LocalDeclarationStatementSyntax>()
                    .FirstOrDefault(l => l.Declaration.Variables.Count == 1 && l.Declaration.Variables[0].Identifier.Text == x
                                         && l.Declaration.Variables[0].Initializer?.Value is BinaryExpressionSyntax { RawKind: (int)SyntaxKind.CoalesceExpression } be
                                         && be.Left.ToString() == p.Identifier.Text);
                if (decl == null) continue;
                var d = ((BinaryExpressionSyntax)decl.Declaration.Variables[0].Initializer!.Value).Right.ToString();
                var name = newMethod.Identifier.Text;
                var oldMethod = oldRoot.DescendantNodes().OfType<MethodDeclarationSyntax>().FirstOrDefault(m => m.Identifier.Text == name
                    && m.ParameterList.Parameters.Any(op => op.Identifier.Text == x && op.Default?.Value.ToString() == d && op.Type?.ToString() == nt.ElementType.ToString()));
                if (oldMethod == null) continue;
                if (!ins.All(t => p.Span.Contains(t.Span) || decl.Span.Contains(t.Span))) continue;
                ok = true;
                found.Add($"{name}({x} = {d})");
                break;
            }
            if (!ok) return false;
        }
        what = "default parameter -> nullable + ?? (lane B pattern): " + string.Join(", ", found.Distinct());
        return true;
    }

    private static void ClassifyBlock(string f, List<SyntaxToken> del, List<SyntaxToken> ins, int nextNew, SyntaxNode newRoot, List<Site> sites,
        List<(int, int, string)> reps, List<string> bad)
    {
        // (1) one literal -> one SimTunables chain
        if (del.Count == 1 && del[0].IsKind(SyntaxKind.NumericLiteralToken) && ins.Count > 0)
        {
            var chain = Syn.ChainAt(newRoot, ins[0].SpanStart);
            var path = chain == null ? null : TP(chain);
            if (chain != null && path != null && chain.SpanStart == ins[0].SpanStart && chain.Span.End == ins[^1].Span.End)
            {
                sites.Add(new Site
                {
                    File = f, Path = path, How = "inline", OldLine = Syn.Line(del[0]), NewLine = Syn.Line(ins[0]), OldPos = del[0].SpanStart, NewPos = chain.SpanStart,
                    Literal = TypedValue.FromToken(del[0])!.Value, LiteralText = del[0].Text, OldSnippet = del[0].Parent?.Parent?.ToString() ?? "",
                });
                reps.Add((chain.SpanStart, chain.Span.Length, del[0].Text));
                return;
            }
        }
        // (1b) pass 2 (--signed): a negated literal "-x" -> one SimTunables chain whose key holds -x
        if (del.Count == 2 && del[0].IsKind(SyntaxKind.MinusToken) && del[0].Parent is PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression } negPu
            && del[1].IsKind(SyntaxKind.NumericLiteralToken) && negPu.Operand is LiteralExpressionSyntax opl && opl.Token == del[1] && ins.Count > 0)
        {
            var chain = Syn.ChainAt(newRoot, ins[0].SpanStart);
            var path = chain == null ? null : TP(chain);
            if (chain != null && path != null && chain.SpanStart == ins[0].SpanStart && chain.Span.End == ins[^1].Span.End)
            {
                var text = "-" + del[1].Text;
                sites.Add(new Site
                {
                    File = f, Path = path, How = "inline", OldLine = Syn.Line(del[0]), NewLine = Syn.Line(ins[0]), OldPos = del[0].SpanStart, NewPos = chain.SpanStart,
                    Literal = TypedValue.FromToken(del[1], negate: true)!.Value, LiteralText = text, OldSnippet = negPu.Parent?.ToString() ?? "",
                });
                reps.Add((chain.SpanStart, chain.Span.Length, text));
                return;
            }
        }
        // (2) "const" dropped from a local whose initializer became a SimTunables read (mbconst move, local_const)
        if (del.Count == 1 && ins.Count == 0 && del[0].IsKind(SyntaxKind.ConstKeyword) && del[0].Parent is LocalDeclarationStatementSyntax && nextNew >= 0)
        {
            var local = newRoot.FindToken(nextNew).Parent?.AncestorsAndSelf().OfType<LocalDeclarationStatementSyntax>().FirstOrDefault();
            var init = local?.Declaration.Variables.Count == 1 ? local.Declaration.Variables[0].Initializer?.Value : null;
            if (init is PrefixUnaryExpressionSyntax pu) init = pu.Operand;
            if (init != null && TP(init) != null)
            {
                reps.Add((nextNew, 0, "const "));
                return;
            }
        }
        var d = string.Join(" ", del.Select(t => t.Text));
        var n = string.Join(" ", ins.Select(t => t.Text));
        bad.Add($"-[{Trim(d)}] +[{Trim(n)}]");
    }

    private static string Trim(string s) => s.Length > 60 ? s[..60] + "…" : s;

    // ------------------------------------------------------------------------------------------------ (e) types

    private static void TypeCheck(PairResult r, Compiler.Pair oldC, Compiler.Pair newC)
    {
        foreach (var s in r.Sites)
        {
            var om = oldC.Model(s.File);
            var nm = newC.Model(s.File);
            if (om == null || nm == null) continue;
            var oldNode = om.SyntaxTree.GetRoot().FindToken(s.OldPos).Parent as ExpressionSyntax;
            var newNode = Syn.ChainAt(nm.SyntaxTree.GetRoot(), s.NewPos);
            if (oldNode == null || newNode == null) { r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} node not found"); continue; }
            if (s.How == "param_default_nullable")
            {
                // the old default literal (converted to the parameter's type) vs the new "(x ?? field)"
                var oldLit = om.SyntaxTree.GetRoot().FindToken(s.OldPos).Parent;
                var oldExpr = oldLit?.Parent is PrefixUnaryExpressionSyntax neg0 ? neg0 : oldLit as ExpressionSyntax;
                var chain = Syn.ChainAt(nm.SyntaxTree.GetRoot(), s.NewPos);
                var paren = chain?.Parent?.Parent as ParenthesizedExpressionSyntax;
                if (oldExpr == null || paren == null) { r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} param default: node not found"); continue; }
                var pt = om.GetTypeInfo(oldExpr).ConvertedType;
                var qt = nm.GetTypeInfo(paren).Type;
                if (Disp(pt) != Disp(qt)) r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} param default {s.LiteralText} -> {s.Path}: {Disp(pt)} vs {Disp(qt)}");
                continue;
            }
            if (s.How.StartsWith("inline"))
            {
                var oi = om.GetTypeInfo(oldNode);
                var ni = nm.GetTypeInfo(newNode);
                if (Disp(oi.Type) == Disp(ni.Type) && Disp(ni.ConvertedType) == Disp(oi.ConvertedType) + "?"
                    && (newNode.Parent is ArgumentSyntax || newNode.Parent is PrefixUnaryExpressionSyntax { Parent: ArgumentSyntax })
                    && (nm.GetSymbolInfo(newNode.FirstAncestorOrSelf<ArgumentSyntax>()!.Parent!.Parent!).Symbol as IMethodSymbol)?.Parameters
                        .Any(p => p.HasExplicitDefaultValue && p.ExplicitDefaultValue == null && Disp(p.Type) == Disp(ni.ConvertedType)) == true)
                    // pass 2: the argument of a parameter the nullable-default pattern turned T -> T? (same value; "x ?? field" reads it)
                    r.Rewrites.Add($"{Repo.Short(s.File)}:{s.NewLine} argument {s.LiteralText} -> {s.Path} now converts to {Disp(ni.ConvertedType)} (a T? = null parameter of pass 2): same value");
                else if (Disp(oi.Type) != Disp(ni.Type) || Disp(oi.ConvertedType) != Disp(ni.ConvertedType))
                    r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} {s.LiteralText} -> {s.Path}: {oi.Type}/{oi.ConvertedType} vs {ni.Type}/{ni.ConvertedType}");
                SyntaxNode? o = oldNode.Parent, n = newNode.Parent;
                for (var depth = 0; depth < 8 && o is ExpressionSyntax oe && n is ExpressionSyntax ne && o is not AnonymousFunctionExpressionSyntax; depth++)
                {
                    if (o.RawKind != n.RawKind) { r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} expression shape differs ({o.Kind()} vs {n.Kind()})"); break; }
                    var ot = om.GetTypeInfo(oe);
                    var nt = nm.GetTypeInfo(ne);
                    if (Disp(ot.Type) != Disp(nt.Type) || Disp(ot.ConvertedType) != Disp(nt.ConvertedType))
                    {
                        r.TypeChanges.Add($"{Repo.Short(s.File)}:{s.NewLine} `{Snip(oe.ToString())}`: {ot.Type}/{ot.ConvertedType} vs {nt.Type}/{nt.ConvertedType}");
                        break;
                    }
                    var oc = om.GetConstantValue(oe);
                    if (oc.HasValue && !nm.GetConstantValue(ne).HasValue && oe is BinaryExpressionSyntax)
                        r.FoldingNotes.Add($"{Repo.Short(s.File)}:{s.NewLine} `{Snip(oe.ToString())}` ({ot.Type})");
                    o = o.Parent;
                    n = n.Parent;
                }
            }
        }
    }

    private static bool CastBack(TypedValue def, string cast, TypedValue lit) => cast switch
    {
        "float" => lit.Type == "float" && BitConverter.SingleToInt32Bits((float)def.AsDouble) == BitConverter.SingleToInt32Bits((float)lit.Value),
        "int" => lit.Type == "int" && (int)def.AsDouble == (int)lit.Value,
        "double" => lit.AsDouble.Equals(def.AsDouble),
        _ => false,
    };

    /// <summary>The semantic model of the new file being compared (resolves SimTunables fields reached through a using or a nested name).</summary>
    [ThreadStatic] private static SemanticModel? _newModel;

    private static string? TP(ExpressionSyntax e)
    {
        var p = Syn.TunablePath(e);
        if (p != null || _newModel == null || e.SyntaxTree != _newModel.SyntaxTree) return p;
        if (_newModel.GetSymbolInfo(e).Symbol is not IFieldSymbol f) return null;
        var names = new List<string> { f.Name };
        for (var t = f.ContainingType; t != null; t = t.ContainingType)
        {
            if (t.Name == "SimTunables" && t.ContainingNamespace.ToDisplayString() == "MachineBrigade.Sim.Content") return string.Join('.', Enumerable.Reverse(names));
            names.Add(t.Name);
        }
        return null;
    }

    private static string Disp(ITypeSymbol? t) => t?.ToDisplayString() ?? "-";

    // ------------------------------------------------------------------------------------------------ report

    private static string Report(List<PairResult> results, Registry reg, List<SourceSet> bases, SourceSet head, string? dotnetLog, out bool pass)
    {
        var sb = new StringBuilder();
        var pathToKey = reg.Keys.Values.GroupBy(k => k.Path).ToDictionary(g => g.Key, g => g.First().Key);
        var allSites = results.SelectMany(r => r.Sites).ToList();
        foreach (var s in allSites) if (!pathToKey.ContainsKey(s.Path)) s.How += " (no key reads this field)";

        // (b) defaults vs json vs original literal
        var bFail = new List<string>();
        var bNotes = new List<string>();
        var evidence = new Dictionary<string, string>();
        foreach (var k in reg.Keys.Values.OrderBy(k => k.Key, StringComparer.Ordinal))
        {
            var cmp = reg.CompareJson(k);
            if (cmp != null) bFail.Add($"{k.Key}: {cmp}");
            var sites = allSites.Where(s => s.Path == k.Path).ToList();
            var def = k.Field?.Default;
            if (sites.Count > 0 && (def != null || k.Field?.ArrayDefault != null))
            {
                foreach (var s in sites)
                {
                    if (s.Array != null)
                    {
                        var ad = k.Field!.ArrayDefault;
                        if (ad == null || ad.Count != s.Array.Count || ad.Where((x, i) => !x.SameAs(s.Array[i])).Any())
                            bFail.Add($"{k.Key}: array {s.LiteralText} at {Repo.Short(s.File)}:{s.OldLine} != default {k.Field.InitText}");
                        continue;
                    }
                    if (def == null) { bFail.Add($"{k.Key}: default {k.Field?.InitText} is not a literal"); continue; }
                    if (s.Literal.SameAs(def.Value)) continue;
                    if (s.Cast != null && CastBack(def.Value, s.Cast, s.Literal))
                        bNotes.Add($"{k.Key}: field type {def.Value.Type} (`{k.Field!.InitText}`) vs literal `{s.LiteralText}` ({s.Literal.Type}) at {Repo.Short(s.File)}:{s.OldLine}; the property casts back to {s.Cast}: value identical");
                    else if (s.Literal.AsDouble.Equals(def.Value.AsDouble))
                        bFail.Add($"{k.Key}: type/suffix changed: literal `{s.LiteralText}` ({s.Literal.Type}) at {Repo.Short(s.File)}:{s.OldLine}, default `{k.Field!.InitText}` ({def.Value.Type})");
                    else bFail.Add($"{k.Key}: literal {s.LiteralText} at {Repo.Short(s.File)}:{s.OldLine} != default {k.Field!.InitText}");
                }
                evidence[k.Key] = "site";
            }
            else if (k.Field != null && !results.Any(x => x.NewKeys.Contains(k.Key)))
                evidence[k.Key] = "earlier"; // not created by these pairs: its original was checked when it was (default == json still checked)
            else if (k.Field != null)
            {
                var was = WasLine(k.Field.Doc, bases, k.Field, out var how);
                if (was == "none")
                {
                    // the pair that created the key: a literal of the same value and type deleted from a rewritten hunk there?
                    var pr = results.FirstOrDefault(x => x.NewKeys.Contains(k.Key));
                    var vals = k.Field.ArrayDefault ?? (def != null ? new List<TypedValue> { def.Value } : new List<TypedValue>());
                    var hits = pr == null ? new List<string>() : vals.Select(v => pr.DeletedLiterals.FirstOrDefault(d => d.val.SameAs(v)))
                        .Where(d => d.text != null).Select(d => $"{Repo.Short(d.file)}:{d.line} `{d.text}`").ToList();
                    if (pr != null && hits.Count == vals.Count && vals.Count > 0)
                    {
                        was = "deleted-literal";
                        how = $"in {pr.Name}: {string.Join(", ", hits.Distinct())}";
                    }
                    else if (pr != null)
                    {
                        was = "new-key";
                        how = $"created in {pr.Name}{(pr.Label != null ? " (" + pr.Label + ")" : "")} with no equal literal removed: a new rule or flag, not a moved number";
                    }
                }
                evidence[k.Key] = was;
                if (was == "mismatch") bFail.Add($"{k.Key}: {how}");
                else if (was == "was-line-type") bFail.Add($"{k.Key}: {how}");
                else if (was is "none" or "new-key" or "deleted-literal") bNotes.Add($"{k.Key} [{was}]: {how}");
            }
        }

        // (c) one key, one literal
        var cFail = new List<string>();
        foreach (var g in allSites.GroupBy(s => s.Path))
        {
            var vals = g.Select(s => s.Literal).Distinct().ToList();
            if (vals.Count > 1)
                cFail.Add($"{pathToKey.GetValueOrDefault(g.Key, g.Key)}: {string.Join(", ", vals)} at {string.Join("; ", g.Select(s => Repo.Short(s.File) + ":" + s.OldLine).Take(6))}");
        }
        var shared = allSites.GroupBy(s => s.Literal).Where(g => g.Select(s => s.Path).Distinct().Count() > 1).Count();

        var aFail = results.Sum(r => r.NonLiteral.Count + r.ReconstructFail.Count);
        var dFail = results.Sum(r => r.Errors.Count);
        var dWarn = results.Sum(r => r.NewWarnings.Count(w => w.StartsWith("**")));
        var eFail = results.Sum(r => r.TypeChanges.Count);
        var compiled = results.All(r => r.Compiled);
        pass = aFail == 0 && bFail.Count == 0 && cFail.Count == 0 && dFail == 0 && dWarn == 0 && eFail == 0 && compiled;

        sb.AppendLine("# Equivalence check (balance pack 2, §2.2)");
        sb.AppendLine();
        sb.AppendLine($"Generated by `Tools/export/mbconst check` on {DateTime.Now:yyyy-MM-dd HH:mm}. Static only (no Unity, no tests). Keys in the registry: {reg.Keys.Count}; in tunables.json: {reg.Json.Count}.");
        sb.AppendLine();
        sb.AppendLine("| check | result | detail |");
        sb.AppendLine("|---|---|---|");
        sb.AppendLine($"| (a) only literal → SimTunables.X | {(aFail == 0 ? "PASS" : "FAIL")} | {results.Sum(r => r.HunksLiteralOnly)}/{results.Sum(r => r.HunksTotal)} hunks literal-only; {allSites.Count} swaps; {aFail} other change(s) |");
        sb.AppendLine($"| (b) default == json == original literal | {(bFail.Count == 0 ? "PASS" : "FAIL")} | {reg.Keys.Count} keys; evidence: {Ev(evidence, "site")} by a swap site, {Ev(evidence, "was-line")} by the 'was' line, {Ev(evidence, "deleted-literal")} by an equal literal deleted in a rewritten hunk, {Ev(evidence, "new-key")} new keys (no literal before), {Ev(evidence, "none")} no original found, {Ev(evidence, "earlier")} keys from before these commits (default == json only); {bFail.Count} mismatch(es) |");
        sb.AppendLine($"| (c) no key with two literals | {(cFail.Count == 0 ? "PASS" : "FAIL")} | {cFail.Count} conflict(s); {shared} literal value(s) feed several keys (allowed) |");
        sb.AppendLine($"| (d) compile, no new conversion warnings | {(!compiled ? "SKIPPED" : dFail == 0 && dWarn == 0 ? "PASS" : "FAIL")} | {dFail} error(s); {results.Sum(r => r.NewWarnings.Count)} new warning(s), {dWarn} conversion/constant |");
        sb.AppendLine($"| (e) expression types unchanged | {(!compiled ? "SKIPPED" : eFail == 0 ? "PASS" : "FAIL")} | {eFail} change(s); {results.Sum(r => r.FoldingNotes.Count)} constant fold(s) now at run time (note) |");
        sb.AppendLine();
        sb.AppendLine($"**Overall: {(pass ? "PASS" : "FAIL")}**");
        sb.AppendLine();
        foreach (var r in results)
        {
            sb.AppendLine($"## {r.Name}{(r.Label != null ? " — " + r.Label : "")}");
            sb.AppendLine();
            sb.AppendLine($"- Files changed (SimTunables*.cs left out): {r.FilesChanged}; hunks {r.HunksTotal}, literal-only {r.HunksLiteralOnly}; swaps {r.Sites.Count} " +
                          $"({string.Join(", ", r.Sites.GroupBy(s => s.How.Split(' ')[0]).Select(g => $"{g.Key} {g.Count()}"))}).");
            if (r.Compiled) sb.AppendLine($"- Compile (Roslyn of the .NET SDK, Sim + Game, Unity 6 DLLs): {r.Errors.Count} error(s); warnings {r.OldWarnings} → {r.HeadWarnings}, new {r.NewWarnings.Count}.");
            List("(a) changes that are not a literal swap", r.NonLiteral, sb, 400);
            List("(a) rebuilt tree differs", r.ReconstructFail, sb, 50);
            List("(a) recognised equivalent rewrites (lane B's xOrDefault: pattern-checked; pass 2's nullable default: undone, then the whole file tree-rebuilt)", r.Rewrites, sb, 50);
            List("(d) errors", r.Errors, sb, 40);
            List("(d) new warnings", r.NewWarnings, sb, 60);
            List("(e) type changes", r.TypeChanges, sb, 100);
            List("(e) note: constant folds now done at run time (same IEEE result for one float/double operation)", r.FoldingNotes, sb, 40);
            sb.AppendLine();
        }
        sb.AppendLine("## (b) keys");
        sb.AppendLine();
        List("mismatches", bFail, sb, 400);
        List("keys without a swap site: weaker evidence or new keys", bNotes, sb, 400);
        sb.AppendLine("## (c) conflicts");
        sb.AppendLine();
        List("one key, several literals", cFail, sb, 100);
        if (dotnetLog != null)
        {
            sb.AppendLine("## dotnet build (working tree)");
            sb.AppendLine();
            sb.AppendLine("```");
            sb.AppendLine(dotnetLog.Trim());
            sb.AppendLine("```");
        }
        return sb.ToString();
    }

    private static int Ev(Dictionary<string, string> e, string v) => e.Values.Count(x => x == v || x.StartsWith(v));

    private static void List(string title, List<string> items, StringBuilder sb, int max)
    {
        if (items.Count == 0) return;
        sb.AppendLine($"### {title} ({items.Count})");
        sb.AppendLine();
        foreach (var i in items.Take(max)) sb.AppendLine("- " + i);
        if (items.Count > max) sb.AppendLine($"- … {items.Count - max} more");
        sb.AppendLine();
    }

    private static readonly Regex WasRx = new(@"was (?:Sim|Game)/([\w/.]+\.cs):(\d+)");

    /// <summary>A key with no swap site: check its default against the literal on the 'was file:line' of its doc, in the bases.</summary>
    private static string WasLine(string doc, List<SourceSet> bases, FieldInfo f, out string how)
    {
        var m = WasRx.Match(doc);
        how = "";
        if (!m.Success) { how = $"no 'was file:line' in the doc ({Snip(doc)})"; return "none"; }
        var rel = Repo.Scripts + "/" + m.Value[4..m.Value.LastIndexOf(':')];
        var line = int.Parse(m.Groups[2].Value);
        foreach (var b in bases)
        {
            if (!b.Files.TryGetValue(rel, out var text)) continue;
            var st = SourceText.From(text);
            if (line > st.Lines.Count) continue;
            var tree = CSharpSyntaxTree.ParseText(text, rel.Contains("/Sim/") ? Compiler.SimParse : Compiler.GameParse);
            var span = st.Lines[line - 1].Span;
            var lits = tree.GetRoot().DescendantTokens(span).Where(t => span.Contains(t.Span))
                .Where(t => t.IsKind(SyntaxKind.NumericLiteralToken) || t.IsKind(SyntaxKind.TrueKeyword) || t.IsKind(SyntaxKind.FalseKeyword))
                .Select(t => (tok: t, val: TypedValue.FromToken(t, t.GetPreviousToken().IsKind(SyntaxKind.MinusToken) && t.GetPreviousToken().Parent is PrefixUnaryExpressionSyntax)!.Value)).ToList();
            if (f.ArrayDefault != null)
            {
                var all = f.ArrayDefault.All(d => lits.Any(l => l.val.SameAs(d)));
                how = all ? "" : $"array elements not all on {Repo.Short(rel)}:{line} in {b.Name}";
                if (all) return "was-line";
                continue;
            }
            if (f.Default == null) { how = "default not a literal"; return "none"; }
            if (lits.Any(l => l.val.SameAs(f.Default.Value))) { how = $"{Repo.Short(rel)}:{line} in {b.Name}"; return "was-line"; }
            var sameValue = lits.FirstOrDefault(l => l.val.AsDouble.Equals(f.Default.Value.AsDouble));
            if (sameValue.tok != default)
            {
                // an int literal assigned to a float const (const float X = 4) reads the same value: type check
                how = $"{Repo.Short(rel)}:{line} literal `{sameValue.tok.Text}` ({sameValue.val.Type}) vs default `{f.InitText}` ({f.Default.Value.Type})";
                return DeclaredType(tree, span) == f.Type ? "was-line" : "was-line-type";
            }
        }
        how = $"no literal equal to {f.Default?.ToString() ?? "the array"} on {Repo.Short(rel)}:{line} in any base";
        return "none";
    }

    private static string? DeclaredType(SyntaxTree tree, TextSpan span)
    {
        var node = tree.GetRoot().DescendantNodes(span).OfType<VariableDeclarationSyntax>().FirstOrDefault();
        if (node != null) return node.Type.ToString();
        var prop = tree.GetRoot().DescendantNodes(span).OfType<PropertyDeclarationSyntax>().FirstOrDefault();
        return prop?.Type.ToString();
    }

    // ------------------------------------------------------------------------------------------------ dotnet build

    private static string DotnetBuild()
    {
        var dir = Path.Combine(Path.GetTempPath(), "mbconst_build");
        Directory.CreateDirectory(Path.Combine(dir, "sim"));
        Directory.CreateDirectory(Path.Combine(dir, "game"));
        var scripts = Repo.Abs(Repo.Scripts);
        const string noWarnSim = "$(NoWarn);CS8632;CS1591;CS0067;CS1574;CS1584;CS1580;CS1572;CS1573;CS1587";
        File.WriteAllText(Path.Combine(dir, "sim", "SimCheck.csproj"), $"""
            <Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>netstandard2.1</TargetFramework><LangVersion>9.0</LangVersion>
            <Nullable>disable</Nullable><EnableDefaultCompileItems>false</EnableDefaultCompileItems><AssemblyName>MachineBrigade.Sim</AssemblyName>
            <NoWarn>{noWarnSim}</NoWarn></PropertyGroup><ItemGroup><Compile Include="{scripts}/Sim/**/*.cs" /></ItemGroup></Project>
            """);
        File.WriteAllText(Path.Combine(dir, "game", "GameCheck.csproj"), $"""
            <Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>netstandard2.1</TargetFramework><LangVersion>9.0</LangVersion>
            <Nullable>disable</Nullable><EnableDefaultCompileItems>false</EnableDefaultCompileItems><AssemblyName>MachineBrigade.Game</AssemblyName>
            <DefineConstants>{string.Join(';', Compiler.GameDefines)}</DefineConstants>
            <NoWarn>{noWarnSim};CS0618;CS0649;CS0414;CS0169;CS1701;CS1702</NoWarn></PropertyGroup>
            <ItemGroup><Compile Include="{scripts}/Game/**/*.cs" />
            <Reference Include="MachineBrigade.Sim"><HintPath>../sim/bin/Debug/netstandard2.1/MachineBrigade.Sim.dll</HintPath></Reference></ItemGroup>
            <ItemGroup><UnityDll Include="{Compiler.UnityEditor}/*.dll" />
            <UnityDll Include="{Compiler.ScriptAssemblies}/Unity.*.dll" Exclude="{Compiler.ScriptAssemblies}/*Tests*.dll;{Compiler.ScriptAssemblies}/*Editor*.dll;{Compiler.ScriptAssemblies}/*CodeGen*.dll" />
            <UnityDll Include="{Compiler.ScriptAssemblies}/UnityEngine.*.dll" /><Reference Include="@(UnityDll)" /></ItemGroup></Project>
            """);
        var log = new StringBuilder();
        foreach (var p in new[] { "sim", "game" })
        {
            var psi = new ProcessStartInfo("dotnet", "build -nologo -v q -clp:NoSummary") { WorkingDirectory = Path.Combine(dir, p), RedirectStandardOutput = true, RedirectStandardError = true };
            using var proc = Process.Start(psi)!;
            var o = proc.StandardOutput.ReadToEnd() + proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            var errs = Regex.Matches(o, @"error CS\d+").Count;
            var warns = Regex.Matches(o, @"warning CS\d+").Select(x => x.Value).Distinct().Count();
            log.AppendLine($"{p}: exit {proc.ExitCode}, {errs} error line(s), {warns} distinct warning id(s)");
            foreach (var l in o.Split('\n').Where(l => l.Contains("error CS")).Take(10)) log.AppendLine("  " + l.Trim());
        }
        return log.ToString();
    }
}

/// <summary>Plain LCS diff (O(n·m) memory-light with prefix/suffix trimming); good for hunks and files of a few thousand lines.</summary>
internal static class Lcs
{
    public enum Op { Equal, Delete, Insert }

    public static List<Op> Diff<T>(IReadOnlyList<T> a, IReadOnlyList<T> b, Func<T, T, bool> eq)
    {
        int pre = 0;
        while (pre < a.Count && pre < b.Count && eq(a[pre], b[pre])) pre++;
        int suf = 0;
        while (suf < a.Count - pre && suf < b.Count - pre && eq(a[a.Count - 1 - suf], b[b.Count - 1 - suf])) suf++;
        int n = a.Count - pre - suf, m = b.Count - pre - suf;
        var ops = new List<Op>(a.Count + b.Count);
        for (var i = 0; i < pre; i++) ops.Add(Op.Equal);
        if (n > 0 && m > 0)
        {
            if ((long)n * m > 60_000_000)
            {
                for (var i = 0; i < n; i++) ops.Add(Op.Delete);
                for (var j = 0; j < m; j++) ops.Add(Op.Insert);
            }
            else
            {
                // lengths table with ushort cells when it fits (files of thousands of lines)
                var len = new int[(n + 1) * (m + 1)];
                for (var i = n - 1; i >= 0; i--)
                for (var j = m - 1; j >= 0; j--)
                    len[i * (m + 1) + j] = eq(a[pre + i], b[pre + j]) ? len[(i + 1) * (m + 1) + j + 1] + 1 : Math.Max(len[(i + 1) * (m + 1) + j], len[i * (m + 1) + j + 1]);
                int x = 0, y = 0;
                while (x < n && y < m)
                {
                    if (eq(a[pre + x], b[pre + y])) { ops.Add(Op.Equal); x++; y++; }
                    else if (len[(x + 1) * (m + 1) + y] >= len[x * (m + 1) + y + 1]) { ops.Add(Op.Delete); x++; }
                    else { ops.Add(Op.Insert); y++; }
                }
                for (; x < n; x++) ops.Add(Op.Delete);
                for (; y < m; y++) ops.Add(Op.Insert);
            }
        }
        else
        {
            for (var i = 0; i < n; i++) ops.Add(Op.Delete);
            for (var j = 0; j < m; j++) ops.Add(Op.Insert);
        }
        for (var i = 0; i < suf; i++) ops.Add(Op.Equal);
        return ops;
    }
}

using System.Collections.Concurrent;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>
/// The static call graph of Sim + Game (§3.1): nodes are source members (methods, constructors, properties, fields,
/// events); an edge is a reference (call, read, object creation, operator, method group, override / interface
/// implementation). Conservative: a virtual call reaches every override, a field read reaches its initializer.
/// </summary>
internal sealed class Graph
{
    public sealed class Member
    {
        public ISymbol Symbol = null!;
        public string Id = "";
        public string File = "";
        public SyntaxNode Decl = null!;
        public readonly HashSet<Member> Out = new();
        public readonly HashSet<Member> In = new();
        public bool Reachable;
        public int Depth = -1;
        public string? RootReason;
    }

    public readonly Dictionary<string, Member> Members = new(StringComparer.Ordinal); // by Key(symbol): one name across the Sim and Game compilations
    public readonly Compiler.Pair C;
    public readonly Dictionary<string, List<string>> Overrides = new(StringComparer.Ordinal);

    public Graph(Compiler.Pair c) => C = c;

    public static string IdOf(ISymbol s) => s.ToDisplayString(SymbolDisplayFormat.CSharpErrorMessageFormat);

    /// <summary>A symbol's identity across compilations (Game sees Sim's symbols retargeted, so object identity does not hold).</summary>
    public static string Key(ISymbol s) => s.GetDocumentationCommentId() ?? IdOf(s);

    public Member? Get(ISymbol s) => Members.GetValueOrDefault(Key(Norm(s)));

    public static ISymbol Norm(ISymbol s)
    {
        s = s.OriginalDefinition;
        if (s is IMethodSymbol m)
        {
            if (m.ReducedFrom != null) m = m.ReducedFrom;
            if (m.AssociatedSymbol is IPropertySymbol or IEventSymbol) return m.AssociatedSymbol!.OriginalDefinition;
            if (m.MethodKind == MethodKind.LocalFunction || m.MethodKind == MethodKind.AnonymousFunction)
            {
                var c = m.ContainingSymbol;
                while (c is IMethodSymbol cm && (cm.MethodKind == MethodKind.LocalFunction || cm.MethodKind == MethodKind.AnonymousFunction)) c = cm.ContainingSymbol;
                return Norm(c);
            }
            return m.OriginalDefinition;
        }
        return s;
    }

    /// <summary>The member node that owns a syntax node (the declaration it sits in).</summary>
    public Member? Owner(SyntaxNode n, SemanticModel model)
    {
        for (var a = n; a != null; a = a.Parent)
        {
            ISymbol? s = a switch
            {
                BaseMethodDeclarationSyntax or PropertyDeclarationSyntax or IndexerDeclarationSyntax or EventDeclarationSyntax => model.GetDeclaredSymbol(a),
                VariableDeclaratorSyntax { Parent.Parent: FieldDeclarationSyntax or EventFieldDeclarationSyntax } => model.GetDeclaredSymbol(a),
                EnumMemberDeclarationSyntax => model.GetDeclaredSymbol(a),
                _ => null,
            };
            if (s != null) return Get(s);
            if (a is FieldDeclarationSyntax fd && fd.Declaration.Variables.Count > 0)
                return Get(model.GetDeclaredSymbol(fd.Declaration.Variables[0])!);
        }
        return null;
    }

    public void Build()
    {
        // 1. members
        foreach (var (rel, tree) in C.Trees)
        {
            var model = C.Model(rel)!;
            foreach (var n in tree.GetRoot().DescendantNodes())
            {
                ISymbol? s = n switch
                {
                    BaseMethodDeclarationSyntax or PropertyDeclarationSyntax or IndexerDeclarationSyntax or EventDeclarationSyntax => model.GetDeclaredSymbol(n),
                    VariableDeclaratorSyntax { Parent.Parent: FieldDeclarationSyntax or EventFieldDeclarationSyntax } => model.GetDeclaredSymbol(n),
                    EnumMemberDeclarationSyntax => model.GetDeclaredSymbol(n),
                    _ => null,
                };
                if (s == null) continue;
                s = Norm(s);
                if (Members.ContainsKey(Key(s))) continue; // partial methods: keep the first
                Members[Key(s)] = new Member { Symbol = s, Id = IdOf(s), File = rel, Decl = n };
            }
        }
        // 2. overrides / interface implementations
        foreach (var m in Members.Values)
        {
            if (m.Symbol is IMethodSymbol ms)
            {
                for (var o = ms.OverriddenMethod; o != null; o = o.OverriddenMethod) AddOverride(o, ms);
                foreach (var i in ImplementedInterfaceMembers(ms)) AddOverride(i, ms);
            }
            else if (m.Symbol is IPropertySymbol ps)
            {
                for (var o = ps.OverriddenProperty; o != null; o = o.OverriddenProperty) AddOverride(o, ps);
                foreach (var i in ImplementedInterfaceMembers(ps)) AddOverride(i, ps);
            }
        }
        // 3. edges
        var edges = new ConcurrentBag<(Member from, ISymbol to)>();
        Parallel.ForEach(C.Trees, kv =>
        {
            var model = C.Model(kv.Key)!;
            foreach (var n in kv.Value.GetRoot().DescendantNodes())
            {
                if (n is not (IdentifierNameSyntax or GenericNameSyntax or ObjectCreationExpressionSyntax or ImplicitObjectCreationExpressionSyntax
                    or BinaryExpressionSyntax or ElementAccessExpressionSyntax or ConstructorInitializerSyntax or PrefixUnaryExpressionSyntax
                    or AssignmentExpressionSyntax or ForEachStatementSyntax)) continue;
                SymbolInfo info;
                try { info = n is ForEachStatementSyntax fe ? default : model.GetSymbolInfo(n); }
                catch { continue; }
                var target = info.Symbol ?? info.CandidateSymbols.FirstOrDefault();
                if (target == null) continue;
                if (target is ILocalSymbol or IParameterSymbol or INamespaceSymbol or ILabelSymbol or IRangeVariableSymbol) continue;
                if (target is INamedTypeSymbol) continue;
                var from = Owner(n, model);
                if (from == null) continue;
                edges.Add((from, Norm(target)));
            }
        });
        foreach (var (from, toSym) in edges)
        {
            var to = Key(toSym);
            if (Members.TryGetValue(to, out var t)) Link(from, t);
            if (Overrides.TryGetValue(to, out var impls))
                foreach (var i in impls)
                    if (Members.TryGetValue(i, out var ti)) Link(from, ti);
        }
        // a type's constructors reach its instance field initializers; any member reaches the static ones
        foreach (var m in Members.Values.Where(m => m.Symbol is IFieldSymbol { IsConst: false } || m.Symbol is IPropertySymbol))
        {
            var type = m.Symbol.ContainingType;
            if (m.Decl is not VariableDeclaratorSyntax { Initializer: not null } && m.Decl is not PropertyDeclarationSyntax { Initializer: not null }) continue;
            foreach (var ctor in type.Constructors.Concat(type.StaticConstructors))
                if (Get(ctor) is { } cm) Link(cm, m);
        }
    }

    private static IEnumerable<ISymbol> ImplementedInterfaceMembers(ISymbol s)
    {
        var type = s.ContainingType;
        foreach (var iface in type.AllInterfaces)
            foreach (var im in iface.GetMembers())
            {
                var impl = type.FindImplementationForInterfaceMember(im);
                if (impl != null && SymbolEqualityComparer.Default.Equals(impl.OriginalDefinition, s.OriginalDefinition)) yield return im.OriginalDefinition;
            }
    }

    private void AddOverride(ISymbol baseSym, ISymbol impl)
    {
        var b = Key(baseSym.OriginalDefinition);
        if (!Overrides.TryGetValue(b, out var list)) Overrides[b] = list = new List<string>();
        list.Add(Key(impl.OriginalDefinition));
    }

    private static void Link(Member a, Member b)
    {
        if (a == b) return;
        a.Out.Add(b);
        b.In.Add(a);
    }

    /// <summary>Members the walk never enters (view code: it cannot change the simulation's result); the edges into them are kept in Boundary.</summary>
    public Func<Member, bool> Blocked = _ => false;
    public readonly List<(Member from, Member to)> Boundary = new();

    public void Reach(IEnumerable<(Member m, string why)> roots)
    {
        var q = new Queue<Member>();
        foreach (var (m, why) in roots)
        {
            if (m.Reachable) continue;
            m.Reachable = true;
            m.Depth = 0;
            m.RootReason = why;
            q.Enqueue(m);
        }
        while (q.Count > 0)
        {
            var m = q.Dequeue();
            foreach (var t in m.Out)
            {
                if (t.Reachable) continue;
                if (Blocked(t)) { Boundary.Add((m, t)); continue; }
                t.Reachable = true;
                t.Depth = m.Depth + 1;
                q.Enqueue(t);
            }
        }
    }

    /// <summary>Members reachable from the seeds within a number of calls.</summary>
    public static HashSet<Member> Within(IEnumerable<Member> seeds, int depth)
    {
        var seen = new HashSet<Member>(seeds);
        var frontier = seen.ToList();
        for (var d = 0; d < depth; d++)
        {
            var next = new List<Member>();
            foreach (var m in frontier)
                foreach (var t in m.Out)
                    if (seen.Add(t)) next.Add(t);
            frontier = next;
        }
        return seen;
    }
}

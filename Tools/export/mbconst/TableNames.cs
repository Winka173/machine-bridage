using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>
/// Pack 2 pass 2 (09/10): a readable base name for a literal that sits in a data table: a static field initializer (the
/// gear catalogue, the commanders, the hunt supports) or an array / object initializer inside a method. The name is the
/// table row's id (its first string argument, its <c>Id = "..."</c>, its first enum argument or the field's own name),
/// then the path down to the literal (constructor parameter names, initializer property names, the enum arguments of a
/// helper call such as <c>L(StatId.Damage, x, CommanderReach.Army)</c>, the branch of a conditional) and the element's
/// 1-based index in an array of several: longBarrelTop3, reyesLinesDamageAircraft, lineHealthEndless2. Null when the
/// literal is not in a table (the generic context name is used).
/// </summary>
internal static class TableNames
{
    public static string? Of(LiteralExpressionSyntax lit, SemanticModel? model)
    {
        var field = lit.Ancestors().OfType<FieldDeclarationSyntax>().FirstOrDefault();
        var staticTable = field != null && field.Modifiers.Any(SyntaxKind.StaticKeyword) && !field.Modifiers.Any(SyntaxKind.ConstKeyword)
                          && field.Declaration.Variables.Count == 1 && field.Declaration.Variables[0].Initializer is { } fi && fi.Value.Span.Contains(lit.Span);
        if (!staticTable && !lit.Ancestors().TakeWhile(a => a is not StatementSyntax and not MemberDeclarationSyntax).Any(a => a is InitializerExpressionSyntax))
            return null;

        var parts = new List<string>();      // bottom-up
        SyntaxNode node = lit.Parent is PrefixUnaryExpressionSyntax pu ? pu : lit;
        SyntaxNode? entry = null;
        var entryParts = -1;
        for (var p = node.Parent; p != null; node = p, p = p.Parent)
        {
            if (p is StatementSyntax or GlobalStatementSyntax) break;
            if (p is EqualsValueClauseSyntax { Parent: VariableDeclaratorSyntax }) break;
            if (p is MemberDeclarationSyntax) break;
            switch (p)
            {
                case ArgumentSyntax targ when targ.Parent is TupleExpressionSyntax tup:
                {
                    var ti = tup.Arguments.IndexOf(targ);
                    parts.Add(targ.NameColon?.Name.Identifier.Text ?? TupleElementName(tup, ti) ?? "part" + (ti + 1));
                    break;
                }
                case ArgumentSyntax arg when arg.Parent is BaseArgumentListSyntax list:
                {
                    var call = list.Parent;
                    var idx = list.Arguments.IndexOf(arg);
                    if (call is TupleExpressionSyntax) { parts.Add(arg.NameColon?.Name.Identifier.Text ?? TupleElementName(call, idx) ?? "part" + (idx + 1)); break; }
                    var sym = call != null && model != null ? model.GetSymbolInfo(call).Symbol as IMethodSymbol : null;
                    string pname = arg.NameColon?.Name.Identifier.Text ?? "";
                    var isParams = false;
                    if (pname == "" && sym != null)
                    {
                        var pi = Math.Min(idx, sym.Parameters.Length - 1);
                        if (pi >= 0)
                        {
                            pname = sym.Parameters[pi].Name;
                            isParams = sym.Parameters[pi].IsParams;
                            if (isParams) pname = (idx - pi + 1).ToString();
                        }
                    }
                    var isEntry = call?.Parent is InitializerExpressionSyntax ie && !ie.IsKind(SyntaxKind.ObjectInitializerExpression)
                                  || call?.Parent is EqualsValueClauseSyntax;
                    if (!isEntry && call is InvocationExpressionSyntax or ObjectCreationExpressionSyntax or ImplicitObjectCreationExpressionSyntax)
                    {
                        // a helper call inside a row: its enum arguments describe the value better than its parameter name
                        var desc = list.Arguments.Select(a => a.Expression).OfType<MemberAccessExpressionSyntax>()
                            .Where(m => m.Expression is IdentifierNameSyntax).Select(m => m.Name.Identifier.Text).ToList();
                        var numeric = list.Arguments.Count(a => a.Expression is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.NumericLiteralExpression }
                                                                or PrefixUnaryExpressionSyntax { Operand: LiteralExpressionSyntax });
                        if (desc.Count > 0) parts.Add((numeric > 1 && !isParams ? pname : "") + string.Concat(desc.Select(Syn.Pascal)));
                        else parts.Add(pname);
                    }
                    else parts.Add(pname);
                    break;
                }
                case InitializerExpressionSyntax init when !init.IsKind(SyntaxKind.ObjectInitializerExpression) && node is ExpressionSyntax el:
                {
                    if (staticTable && el is ObjectCreationExpressionSyntax or ImplicitObjectCreationExpressionSyntax or InvocationExpressionSyntax or TupleExpressionSyntax)
                    {
                        entry = el;
                        entryParts = parts.Count;
                    }
                    if (init.Expressions.Count > 1) parts.Add((init.Expressions.IndexOf(el) + 1).ToString());
                    break;
                }
                case AssignmentExpressionSyntax asg when asg.Right == node:
                    parts.Add(LastName(asg.Left));
                    break;
                case ConditionalExpressionSyntax ce:
                {
                    var c = LastName(ce.Condition);
                    if (ce.WhenTrue == node) parts.Add(c);
                    else if (ce.WhenFalse == node) parts.Add("not" + Syn.Pascal(c));
                    break;
                }
                case ObjectCreationExpressionSyntax or ImplicitObjectCreationExpressionSyntax when node is InitializerExpressionSyntax && !staticTable:
                    // a settings object built in a method: its property names are enough
                    goto done;
            }
        }
        done:
        string rowId;
        if (staticTable)
        {
            if (entry != null)
            {
                rowId = RowId(entry) ?? field!.Declaration.Variables[0].Identifier.Text;
                parts = parts.Take(entryParts).ToList();
            }
            else rowId = field!.Declaration.Variables[0].Identifier.Text;
        }
        else if (field != null && field.Declaration.Variables.Count == 1 && field.Declaration.Variables[0].Initializer is { } fi2 && fi2.Value.Span.Contains(lit.Span)
                 && node.Parent is EqualsValueClauseSyntax)
            rowId = field.Declaration.Variables[0].Identifier.Text; // an instance field's own table: its name
        else rowId = "";
        parts.Reverse();
        var sb = new System.Text.StringBuilder(Ident(rowId));
        foreach (var x in parts.Where(x => x != "").Select(x => Syn.Pascal(Ident(x))))
        {
            // an index after a name ending in a digit (Top2, then element 3) reads Top2N3
            if (x.Length > 0 && char.IsDigit(x[0]) && sb.Length > 0 && char.IsDigit(sb[^1])) sb.Append('N');
            sb.Append(x);
        }
        var name = Syn.Camel(sb.ToString());
        if (name == "") return null;
        if (char.IsDigit(name[0])) name = "n" + name;
        return name.Length > 60 ? name[..60] : name;
    }

    /// <summary>The declared name of a tuple element ((int cp, float seconds)[] x = { (2, 25f) } -> "seconds" for index 1).</summary>
    private static string? TupleElementName(SyntaxNode tuple, int idx)
    {
        var decl = tuple.Ancestors().OfType<VariableDeclarationSyntax>().FirstOrDefault();
        var t = decl?.Type;
        while (t is ArrayTypeSyntax at) t = at.ElementType;
        if (t is GenericNameSyntax g && g.TypeArgumentList.Arguments.Count == 1) t = g.TypeArgumentList.Arguments[0];
        if (t is TupleTypeSyntax tt && idx < tt.Elements.Count) return tt.Elements[idx].Identifier.Text is { Length: > 0 } n ? n : null;
        return null;
    }

    /// <summary>A table row's id: Id = "x" in its initializer, else its first string argument, else its first enum argument.</summary>
    private static string? RowId(SyntaxNode entry)
    {
        foreach (var a in entry.DescendantNodes().OfType<AssignmentExpressionSyntax>())
            if (LastName(a.Left) == "Id" && a.Right is LiteralExpressionSyntax { RawKind: (int)SyntaxKind.StringLiteralExpression } s) return s.Token.ValueText;
        var str = entry.DescendantNodes().OfType<LiteralExpressionSyntax>().FirstOrDefault(l => l.IsKind(SyntaxKind.StringLiteralExpression));
        if (str != null) return str.Token.ValueText;
        var args = entry switch
        {
            BaseObjectCreationExpressionSyntax oc => oc.ArgumentList?.Arguments,
            InvocationExpressionSyntax inv => inv.ArgumentList.Arguments,
            _ => null,
        };
        var en = args?.Select(a => a.Expression).OfType<MemberAccessExpressionSyntax>().FirstOrDefault();
        return en?.Name.Identifier.Text;
    }

    private static string Ident(string s)
    {
        var sb = new System.Text.StringBuilder();
        var up = false;
        foreach (var ch in s)
        {
            if (char.IsLetterOrDigit(ch)) { sb.Append(up ? char.ToUpperInvariant(ch) : ch); up = false; }
            else up = sb.Length > 0;
        }
        return sb.ToString();
    }

    private static string LastName(SyntaxNode e) => e switch
    {
        IdentifierNameSyntax id => id.Identifier.Text,
        MemberAccessExpressionSyntax ma => ma.Name.Identifier.Text,
        InvocationExpressionSyntax inv => LastName(inv.Expression),
        ParenthesizedExpressionSyntax pe => LastName(pe.Expression),
        PrefixUnaryExpressionSyntax u => LastName(u.Operand),
        BinaryExpressionSyntax b => LastName(b.Left) is { Length: > 0 } s ? s : LastName(b.Right),
        _ => "",
    };
}

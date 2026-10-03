using System.Globalization;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

namespace MbConst;

/// <summary>A numeric (or bool) value with its C# type, as a literal token gives it.</summary>
internal readonly record struct TypedValue(string Type, object Value)
{
    public static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    public static TypedValue? FromToken(SyntaxToken t, bool negate = false)
    {
        if (t.IsKind(SyntaxKind.TrueKeyword)) return new TypedValue("bool", true);
        if (t.IsKind(SyntaxKind.FalseKeyword)) return new TypedValue("bool", false);
        if (!t.IsKind(SyntaxKind.NumericLiteralToken) || t.Value == null) return null;
        var v = t.Value;
        if (negate)
            v = v switch
            {
                float f => -f, double d => -d, int i => -i, long l => -l, decimal m => -m,
                uint u => -(long)u, ulong ul => (object)(-(decimal)ul), _ => v,
            };
        return new TypedValue(TypeName(v), v);
    }

    /// <summary>The literal of an expression that is a literal or a negated literal (else null).</summary>
    public static TypedValue? FromExpression(ExpressionSyntax? e)
    {
        switch (e)
        {
            case LiteralExpressionSyntax lit: return FromToken(lit.Token);
            case PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryMinusExpression, Operand: LiteralExpressionSyntax l2 }:
                return FromToken(l2.Token, negate: true);
            case PrefixUnaryExpressionSyntax { RawKind: (int)SyntaxKind.UnaryPlusExpression, Operand: LiteralExpressionSyntax l3 }:
                return FromToken(l3.Token);
            case ParenthesizedExpressionSyntax p: return FromExpression(p.Expression);
            case BinaryExpressionSyntax b when FromExpression(b.Left) is { } l && FromExpression(b.Right) is { } r && l.Type == r.Type:
                // a constant expression of literals (2f / 3f), folded the way C# folds it
                return (l.Value, r.Value, b.Kind()) switch
                {
                    (float x, float y, SyntaxKind.DivideExpression) => new TypedValue("float", x / y),
                    (float x, float y, SyntaxKind.MultiplyExpression) => new TypedValue("float", x * y),
                    (float x, float y, SyntaxKind.AddExpression) => new TypedValue("float", x + y),
                    (float x, float y, SyntaxKind.SubtractExpression) => new TypedValue("float", x - y),
                    (double x, double y, SyntaxKind.DivideExpression) => new TypedValue("double", x / y),
                    (double x, double y, SyntaxKind.MultiplyExpression) => new TypedValue("double", x * y),
                    (int x, int y, SyntaxKind.MultiplyExpression) => new TypedValue("int", x * y),
                    (int x, int y, SyntaxKind.AddExpression) => new TypedValue("int", x + y),
                    _ => null,
                };
            default: return null;
        }
    }

    public static string TypeName(object v) => v switch
    {
        float => "float", double => "double", int => "int", long => "long", uint => "uint", ulong => "ulong",
        decimal => "decimal", bool => "bool", short => "short", byte => "byte", _ => v.GetType().Name,
    };

    public double AsDouble => Value switch
    {
        float f => f, double d => d, int i => i, long l => l, uint u => u, ulong ul => ul, decimal m => (double)m,
        bool b => b ? 1 : 0, _ => double.NaN,
    };

    /// <summary>Does a JSON number read as this field's type give exactly this value (SimTunables.Apply's casts)?</summary>
    public bool EqualsJson(double json) => Type switch
    {
        "float" => BitConverter.SingleToInt32Bits((float)json) == BitConverter.SingleToInt32Bits((float)Value),
        "double" => json.Equals((double)Value),
        "int" => json == Math.Round(json) && (int)Math.Round(json) == (int)Value,
        "long" => json == Math.Round(json) && (long)Math.Round(json) == (long)Value,
        "uint" => json == Math.Round(json) && (uint)Math.Round(json) == (uint)Value,
        "bool" => (json != 0) == (bool)Value,
        _ => false,
    };

    public bool SameAs(TypedValue o) => Type == o.Type && Value.Equals(o.Value);

    public override string ToString() => Value switch
    {
        float f => f.ToString("R", Inv) + "f", double d => d.ToString("R", Inv), bool b => b ? "true" : "false",
        IFormattable fm => fm.ToString(null, Inv), _ => Value.ToString() ?? "",
    };

    /// <summary>The value as a JSON number (lane B style: a float or double always carries a decimal point).</summary>
    public string JsonText()
    {
        switch (Value)
        {
            case bool b: return b ? "true" : "false";
            case float f:
            {
                // the shortest decimal that reads back as this float: what the C# literal meant
                var s = f.ToString("R", Inv);
                return s.Contains('.') || s.Contains('E') ? s.Replace("E", "e") : s + ".0";
            }
            case double d:
            {
                var s = d.ToString("R", Inv);
                return s.Contains('.') || s.Contains('E') ? s.Replace("E", "e") : s + ".0";
            }
            case IFormattable fm: return fm.ToString(null, Inv);
            default: return Value.ToString() ?? "0";
        }
    }

    /// <summary>How SimTunables.Apply casts the JSON double into a field of this type (the Entry setter).</summary>
    public string SetterCast(string target) => Type switch
    {
        "float" => $"v => {target} = (float)v",
        "double" => $"v => {target} = v",
        "int" => $"v => {target} = (int)System.Math.Round(v)",
        "long" => $"v => {target} = (long)System.Math.Round(v)",
        "uint" => $"v => {target} = (uint)System.Math.Round(v)",
        _ => throw new NotSupportedException("type " + Type + " has no SimTunables entry"),
    };
}

internal static class Syn
{
    public static int Line(SyntaxNode n) => n.GetLocation().GetLineSpan().StartLinePosition.Line + 1;
    public static int Line(SyntaxToken t) => t.GetLocation().GetLineSpan().StartLinePosition.Line + 1;

    public static string Pascal(string s) => s.Length == 0 ? s : char.ToUpperInvariant(s[0]) + s[1..];
    public static string Camel(string s) => s.Length == 0 ? s : char.ToLowerInvariant(s[0]) + s[1..];

    /// <summary>"weapons.combatSystem.axisRatio" -> "Weapons.CombatSystem.AxisRatio".</summary>
    public static string KeyToPath(string key) => string.Join('.', key.Split('.').Select(Pascal));

    public const string Qualifier = "global::MachineBrigade.Sim.Content.SimTunables.";

    /// <summary>Is this expression a reference into SimTunables (global::...SimTunables.A.B.C or SimTunables.A.B.C)? Returns "A.B.C".</summary>
    public static string? TunablePath(ExpressionSyntax e)
    {
        var text = string.Concat(e.DescendantTokens().Select(t => t.Text));
        var i = text.IndexOf("SimTunables.", StringComparison.Ordinal);
        if (i < 0) return null;
        var prefix = text[..i];
        if (prefix != "" && prefix != "global::MachineBrigade.Sim.Content." && prefix != "MachineBrigade.Sim.Content." && prefix != "Content.") return null;
        var path = text[(i + "SimTunables.".Length)..];
        return path.All(c => char.IsLetterOrDigit(c) || c == '_' || c == '.') ? path : null;
    }

    /// <summary>The outermost member access / qualified name chain that contains this token.</summary>
    public static ExpressionSyntax? ChainAt(SyntaxNode root, int position)
    {
        var tok = root.FindToken(position);
        SyntaxNode? n = tok.Parent;
        ExpressionSyntax? best = null;
        while (n is MemberAccessExpressionSyntax or QualifiedNameSyntax or AliasQualifiedNameSyntax or IdentifierNameSyntax)
        {
            best = (ExpressionSyntax)n;
            n = n.Parent;
        }
        return best;
    }

    /// <summary>Why a literal here must stay a compile-time constant (null: it may become a field read).</summary>
    public static string? ConstantContext(SyntaxNode lit)
    {
        for (var n = lit.Parent; n != null; n = n.Parent)
        {
            switch (n)
            {
                case AttributeArgumentSyntax: return "attribute argument";
                case CaseSwitchLabelSyntax: return "case label";
                case ConstantPatternSyntax or RelationalPatternSyntax: return "pattern";
                case EnumMemberDeclarationSyntax: return "enum member";
                case ParameterSyntax: return "parameter default";
                case AnonymousFunctionExpressionSyntax or LocalFunctionStatementSyntax: return null;
                case StatementSyntax or MemberDeclarationSyntax: return null;
            }
        }
        return null;
    }
}

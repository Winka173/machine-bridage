#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Small JSON reader for the balance and map files. It avoids reflection-based
    /// serialisers, which IL2CPP code stripping can break, and it accepts <c>//</c> line
    /// comments so tuning notes can live next to the numbers.
    /// Values become <see cref="Dictionary{TKey,TValue}"/>, <see cref="List{T}"/>, double,
    /// string, bool or null.
    /// </summary>
    public static class MiniJson
    {
        public static object? Parse(string text)
        {
            var parser = new Parser(text ?? throw new ArgumentNullException(nameof(text)));
            var value = parser.ReadValue();
            parser.SkipWhitespace();
            if (!parser.AtEnd) throw parser.Error("unexpected content after the root value");
            return value;
        }

        private sealed class Parser
        {
            private readonly string _s;
            private int _i;

            public Parser(string s) => _s = s;

            public bool AtEnd => _i >= _s.Length;

            public object? ReadValue()
            {
                SkipWhitespace();
                if (AtEnd) throw Error("unexpected end of input");
                var c = _s[_i];
                switch (c)
                {
                    case '{': return ReadObject();
                    case '[': return ReadArray();
                    case '"': return ReadString();
                    case 't': ExpectWord("true"); return true;
                    case 'f': ExpectWord("false"); return false;
                    case 'n': ExpectWord("null"); return null;
                    default:
                        if (c == '-' || char.IsDigit(c)) return ReadNumber();
                        throw Error($"unexpected character '{c}'");
                }
            }

            private Dictionary<string, object?> ReadObject()
            {
                _i++; // {
                var result = new Dictionary<string, object?>();
                SkipWhitespace();
                if (Peek() == '}') { _i++; return result; }
                while (true)
                {
                    SkipWhitespace();
                    if (Peek() != '"') throw Error("expected a property name");
                    var key = ReadString();
                    SkipWhitespace();
                    if (Peek() != ':') throw Error("expected ':'");
                    _i++;
                    result[key] = ReadValue();
                    SkipWhitespace();
                    var next = Peek();
                    _i++;
                    if (next == ',') continue;
                    if (next == '}') return result;
                    throw Error("expected ',' or '}'");
                }
            }

            private List<object?> ReadArray()
            {
                _i++; // [
                var result = new List<object?>();
                SkipWhitespace();
                if (Peek() == ']') { _i++; return result; }
                while (true)
                {
                    result.Add(ReadValue());
                    SkipWhitespace();
                    var next = Peek();
                    _i++;
                    if (next == ',') continue;
                    if (next == ']') return result;
                    throw Error("expected ',' or ']'");
                }
            }

            private string ReadString()
            {
                _i++; // opening quote
                var sb = new StringBuilder();
                while (true)
                {
                    if (AtEnd) throw Error("unterminated string");
                    var c = _s[_i++];
                    if (c == '"') return sb.ToString();
                    if (c != '\\') { sb.Append(c); continue; }
                    if (AtEnd) throw Error("unterminated escape");
                    var e = _s[_i++];
                    switch (e)
                    {
                        case '"': case '\\': case '/': sb.Append(e); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'n': sb.Append('\n'); break;
                        case 'r': sb.Append('\r'); break;
                        case 't': sb.Append('\t'); break;
                        case 'u':
                            if (_i + 4 > _s.Length) throw Error("truncated \\u escape");
                            sb.Append((char)int.Parse(_s.Substring(_i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture));
                            _i += 4;
                            break;
                        default: throw Error($"unknown escape '\\{e}'");
                    }
                }
            }

            private double ReadNumber()
            {
                var start = _i;
                if (Peek() == '-') _i++;
                while (!AtEnd && (char.IsDigit(_s[_i]) || _s[_i] == '.' || _s[_i] == 'e' || _s[_i] == 'E' || _s[_i] == '+' || _s[_i] == '-'))
                    _i++;
                var token = _s.Substring(start, _i - start);
                if (!double.TryParse(token, NumberStyles.Float, CultureInfo.InvariantCulture, out var value))
                    throw Error($"invalid number '{token}'");
                return value;
            }

            private void ExpectWord(string word)
            {
                if (string.CompareOrdinal(_s, _i, word, 0, word.Length) != 0) throw Error($"expected '{word}'");
                _i += word.Length;
            }

            private char Peek() => AtEnd ? '\0' : _s[_i];

            public void SkipWhitespace()
            {
                while (!AtEnd)
                {
                    var c = _s[_i];
                    if (char.IsWhiteSpace(c)) { _i++; continue; }
                    if (c == '/' && _i + 1 < _s.Length && _s[_i + 1] == '/')
                    {
                        while (!AtEnd && _s[_i] != '\n') _i++;
                        continue;
                    }
                    break;
                }
            }

            public FormatException Error(string message)
            {
                int line = 1, column = 1;
                for (var k = 0; k < _i && k < _s.Length; k++)
                {
                    if (_s[k] == '\n') { line++; column = 1; }
                    else column++;
                }
                return new FormatException($"JSON: {message} at line {line}, column {column}.");
            }
        }
    }
}

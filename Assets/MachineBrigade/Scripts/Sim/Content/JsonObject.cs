#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Typed, error-reporting view over a parsed JSON object. Every failure names the path
    /// (for example <c>vehicles[2].speed</c>) so a typo in a data file is quick to find.
    /// </summary>
    internal readonly struct JsonObject
    {
        private readonly Dictionary<string, object?> _values;

        public JsonObject(object? value, string path)
        {
            _values = value as Dictionary<string, object?> ?? throw new FormatException($"{path}: expected an object.");
            Path = path;
        }

        public string Path { get; }

        public bool Has(string key) => _values.TryGetValue(key, out var v) && v != null;

        public float Float(string key) =>
            _values.TryGetValue(key, out var v) && v is double d ? (float)d : throw Invalid(key, "a number");

        public float Float(string key, float fallback) =>
            !Has(key) ? fallback : _values[key] is double d ? (float)d : throw Invalid(key, "a number");

        public int Int(string key, int fallback)
        {
            if (!Has(key)) return fallback;
            if (_values[key] is double d && Math.Abs(d - Math.Round(d)) < 1e-9) return (int)Math.Round(d);
            throw Invalid(key, "a whole number");
        }

        public string String(string key) =>
            _values.TryGetValue(key, out var v) && v is string s && s.Length > 0 ? s : throw Invalid(key, "a non-empty string");

        public bool Bool(string key, bool fallback) =>
            !Has(key) ? fallback : _values[key] is bool b ? b : throw Invalid(key, "true or false");

        public TEnum Enum<TEnum>(string key, TEnum fallback) where TEnum : struct, System.Enum =>
            Has(key) ? Enum<TEnum>(key) : fallback;

        public TEnum Enum<TEnum>(string key) where TEnum : struct, System.Enum =>
            System.Enum.TryParse<TEnum>(String(key), true, out var e) && System.Enum.IsDefined(typeof(TEnum), e)
                ? e
                : throw Invalid(key, $"one of {string.Join(", ", System.Enum.GetNames(typeof(TEnum)))}");

        public JsonObject Object(string key) =>
            Has(key) ? new JsonObject(_values[key], $"{Path}.{key}") : throw Invalid(key, "an object");

        public IEnumerable<JsonObject> Array(string key)
        {
            if (!Has(key)) yield break;
            if (_values[key] is not List<object?> list) throw Invalid(key, "an array");
            for (var i = 0; i < list.Count; i++) yield return new JsonObject(list[i], $"{Path}.{key}[{i}]");
        }

        public IReadOnlyList<float> FloatArray(string key)
        {
            if (!Has(key) || _values[key] is not List<object?> list) throw Invalid(key, "an array of numbers");
            var result = new List<float>(list.Count);
            foreach (var item in list) result.Add(item is double d ? (float)d : throw Invalid(key, "an array of numbers"));
            return result;
        }

        public IReadOnlyList<string> StringArray(string key)
        {
            if (!Has(key) || _values[key] is not List<object?> list) throw Invalid(key, "an array of strings");
            var result = new List<string>(list.Count);
            foreach (var item in list) result.Add(item is string s ? s : throw Invalid(key, "an array of strings"));
            return result;
        }

        public IEnumerable<string> Keys => _values.Keys;

        private FormatException Invalid(string key, string expected) =>
            new FormatException($"{Path}.{key}: expected {expected}.");
    }
}

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

        /// <summary>The parsed fields themselves (prompt 20's boss templates build entries from them).</summary>
        internal Dictionary<string, object?> Raw => _values;

        public bool Has(string key) => _values.TryGetValue(key, out var v) && v != null;

        /// <summary>The value at <paramref name="key"/> is an array (data that takes one number or several).</summary>
        public bool IsArray(string key) => _values.TryGetValue(key, out var v) && v is List<object?>;

        /// <summary>The value at <paramref name="key"/> is a string (data that takes a word or a number).</summary>
        public bool IsString(string key) => _values.TryGetValue(key, out var v) && v is string;

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

        /// <summary>An array of arrays of numbers (polygons, points as x, z pairs).</summary>
        public IReadOnlyList<IReadOnlyList<float>> FloatArrays(string key)
        {
            if (!Has(key) || _values[key] is not List<object?> list) throw Invalid(key, "an array of arrays of numbers");
            var result = new List<IReadOnlyList<float>>(list.Count);
            foreach (var item in list)
            {
                if (item is not List<object?> inner) throw Invalid(key, "an array of arrays of numbers");
                var row = new List<float>(inner.Count);
                foreach (var v in inner) row.Add(v is double d ? (float)d : throw Invalid(key, "an array of arrays of numbers"));
                result.Add(row);
            }
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

        /// <summary>This object's fields with <paramref name="child"/>'s on top (a def that inherits another's data).</summary>
        internal JsonObject Under(JsonObject child)
        {
            var merged = new Dictionary<string, object?>(_values);
            foreach (var pair in child._values) merged[pair.Key] = pair.Value;
            return new JsonObject(merged, child.Path);
        }

        /// <summary>
        /// Prompt 25 A3: this object with <paramref name="shared"/>'s fields on top (a weapon family's), but for
        /// <paramref name="skip"/>; it keeps its own path, so an error names the weapon.
        /// </summary>
        internal JsonObject Taking(JsonObject shared, params string[] skip)
        {
            var merged = new Dictionary<string, object?>(_values);
            foreach (var pair in shared._values)
                if (System.Array.IndexOf(skip, pair.Key) < 0) merged[pair.Key] = pair.Value;
            return new JsonObject(merged, Path);
        }

        /// <summary>Prompt 25 G: a copy without some fields (a second round leaves its gun's own round links behind).</summary>
        internal JsonObject Without(params string[] keys)
        {
            var copy = new Dictionary<string, object?>(_values);
            foreach (var k in keys) copy.Remove(k);
            return new JsonObject(copy, Path);
        }

        /// <summary>A copy with one field set (a merged def's resolved model).</summary>
        internal JsonObject With(string key, object? value)
        {
            var copy = new Dictionary<string, object?>(_values) { [key] = value };
            return new JsonObject(copy, Path);
        }

        private FormatException Invalid(string key, string expected) =>
            new FormatException($"{Path}.{key}: expected {expected}.");
    }
}

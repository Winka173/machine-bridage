#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Balance pack (lane B): the registry of the data file Resources/Data/tunables.json. Every entry is a static field
    /// of <see cref="SimTunables"/> (domain, owner class, name) whose initial value is the code's old constant; the file
    /// sets them (<see cref="Apply"/>, called by GameContent.LoadCatalog), a key the file leaves out keeps its default.
    /// Values never change during a battle, so the simulation stays deterministic.
    /// </summary>
    public static partial class SimTunables
    {
        /// <summary>One data value: its key (domain.ownerClass.name), unit, and how to read and set the field.</summary>
        private sealed class Entry
        {
            public readonly string Key;
            public readonly string Unit;
            public readonly Func<double>? Get;
            public readonly Action<double>? Set;
            public readonly Func<double[]>? GetArray;
            public readonly Action<double[]>? SetArray;
            public readonly bool Flag;

            public Entry(string key, string unit, Func<double> get, Action<double> set, bool flag = false)
            {
                Key = key;
                Unit = unit;
                Get = get;
                Set = set;
                Flag = flag;
            }

            private Entry(string key, string unit, Func<double[]> get, Action<double[]> set)
            {
                Key = key;
                Unit = unit;
                GetArray = get;
                SetArray = set;
            }

            public static Entry FloatArray(string key, string unit, Func<float[]> get, Action<float[]> set) =>
                new(key, unit, () => Array.ConvertAll(get(), x => (double)x), v => set(Array.ConvertAll(v, x => (float)x)));

            public static Entry IntArray(string key, string unit, Func<int[]> get, Action<int[]> set) =>
                new(key, unit, () => Array.ConvertAll(get(), x => (double)x), v => set(Array.ConvertAll(v, x => (int)Math.Round(x))));
        }

        private static Dictionary<string, Entry>? _byKey;
        private static Dictionary<string, object>? _defaults;

        private static Dictionary<string, Entry> ByKey()
        {
            if (_byKey != null) return _byKey;
            var map = new Dictionary<string, Entry>(StringComparer.Ordinal);
            foreach (var e in Entries) map.Add(e.Key, e);
            foreach (var e in RuleEntries) map.Add(e.Key, e);
            foreach (var e in Pack2Entries()) map.Add(e.Key, e);
            _byKey = map;
            // The fields' values before any file was applied: the code's old constants.
            _defaults = new Dictionary<string, object>(StringComparer.Ordinal);
            foreach (var e in map.Values)
                _defaults[e.Key] = e.GetArray != null ? (object)e.GetArray() : e.Get!();
            return map;
        }

        /// <summary>The keys the last <see cref="Apply"/> did not know, or whose value had the wrong shape (tests read it).</summary>
        public static List<string> Problems { get; } = new();

        /// <summary>Every key, in the registry's order (the export and the tests).</summary>
        public static IEnumerable<string> Keys
        {
            get
            {
                foreach (var e in Entries) yield return e.Key;
                foreach (var e in RuleEntries) yield return e.Key;
                foreach (var e in Pack2Entries()) yield return e.Key;
            }
        }

        /// <summary>Puts every field back to the code's default.</summary>
        public static void Reset()
        {
            var map = ByKey();
            foreach (var e in map.Values)
            {
                var d = _defaults![e.Key];
                if (e.SetArray != null) e.SetArray((double[])((double[])d).Clone());
                else e.Set!((double)d);
            }
        }

        /// <summary>
        /// Sets the fields from the JSONC text of tunables.json (after <see cref="Reset"/>): domain → owner class → name →
        /// a number, an array, true / false, or an object whose "value" is one. Returns how many values were set.
        /// </summary>
        public static int Apply(string json)
        {
            var map = ByKey();
            Reset();
            Problems.Clear();
            if (MiniJson.Parse(json) is not Dictionary<string, object?> root) throw new FormatException("tunables: expected an object.");
            var set = 0;
            foreach (var domainPair in root)
            {
                var domain = domainPair.Key;
                var domainValue = domainPair.Value;
                if (domain == "version") continue;
                if (domainValue is not Dictionary<string, object?> owners)
                {
                    Problems.Add(domain);
                    continue;
                }
                foreach (var ownerPair in owners)
                {
                    var owner = ownerPair.Key;
                    var ownerValue = ownerPair.Value;
                    if (ownerValue is not Dictionary<string, object?> names)
                    {
                        Problems.Add(domain + "." + owner);
                        continue;
                    }
                    foreach (var namePair in names)
                    {
                        var name = namePair.Key;
                        var raw = namePair.Value;
                        var key = domain + "." + owner + "." + name;
                        var value = raw is Dictionary<string, object?> o && o.TryGetValue("value", out var inner) ? inner : raw;
                        if (!map.TryGetValue(key, out var entry) || !TrySet(entry, value))
                        {
                            Problems.Add(key);
                            continue;
                        }
                        set++;
                    }
                }
            }
            return set;
        }

        private static bool TrySet(Entry entry, object? value)
        {
            if (entry.SetArray != null)
            {
                if (value is not List<object?> list) return false;
                var values = new double[list.Count];
                for (var i = 0; i < list.Count; i++)
                {
                    if (list[i] is not double d) return false;
                    values[i] = d;
                }
                entry.SetArray(values);
                return true;
            }
            switch (value)
            {
                case double d:
                    entry.Set!(d);
                    return true;
                case bool b when entry.Flag:
                    entry.Set!(b ? 1.0 : 0.0);
                    return true;
                default:
                    return false;
            }
        }

        /// <summary>
        /// The export (ExportGameDoc): every value now, as (key, unit, text); numbers in the invariant culture, arrays as
        /// "a;b;c", flags as true / false.
        /// </summary>
        public static List<(string key, string unit, string value)> Snapshot()
        {
            var map = ByKey();
            var result = new List<(string, string, string)>();
            foreach (var key in Keys)
            {
                var e = map[key];
                string text;
                if (e.GetArray != null)
                    text = string.Join(";", Array.ConvertAll(e.GetArray(), x => x.ToString("R", CultureInfo.InvariantCulture)));
                else if (e.Flag)
                    text = e.Get!() != 0.0 ? "true" : "false";
                else
                    text = ((float)e.Get!()).ToString("R", CultureInfo.InvariantCulture);
                result.Add((key, e.Unit, text));
            }
            return result;
        }

        /// <summary>The code's default for a key (tests: the shipped file must equal the defaults it replaced).</summary>
        public static string DefaultText(string key)
        {
            ByKey();
            var d = _defaults![key];
            return d is double[] a
                ? string.Join(";", Array.ConvertAll(a, x => x.ToString("R", CultureInfo.InvariantCulture)))
                : ((double)d).ToString("R", CultureInfo.InvariantCulture);
        }

        /// <summary>The value now of a key, as <see cref="DefaultText"/> writes it.</summary>
        public static string ValueText(string key)
        {
            var e = ByKey()[key];
            return e.GetArray != null
                ? string.Join(";", Array.ConvertAll(e.GetArray(), x => x.ToString("R", CultureInfo.InvariantCulture)))
                : e.Get!().ToString("R", CultureInfo.InvariantCulture);
        }
    }
}

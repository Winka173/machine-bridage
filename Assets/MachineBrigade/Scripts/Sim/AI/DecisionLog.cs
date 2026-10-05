#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.AI
{
    /// <summary>Which AI layer made a decision (prompt 28 J.2).</summary>
    public enum AiLayer
    {
        Commander,
        Squad,
        Unit,
    }

    /// <summary>What a log line records (J.4).</summary>
    public enum DecisionKind
    {
        Plan,
        Action,
        State,
        Target,
        Emergency,
        Tactic,
        Hint,

        /// <summary>AI MASTER P0-B: the buying AI's BUY, REJECT, PLAN and RESERVE lines (Part O's PURCHASE_* codes).</summary>
        Purchase,

        /// <summary>AI MASTER P0-D + P1: movement and traffic lines (Part O's TRAFFIC_*, JAM_*, ROUTE_*, SEVERE_UNSTUCK).</summary>
        Traffic,
    }

    /// <summary>One scoring factor: a key the viewer's text table names ("why.ratio") and its points (+ or -).</summary>
    public readonly struct Factor
    {
        public Factor(string key, float points)
        {
            Key = key;
            Points = points;
        }

        public string Key { get; }
        public float Points { get; }

        public override string ToString() => $"{(Points >= 0f ? "+" : "")}{Points:0} {Key}";
    }

    /// <summary>
    /// "VÌ SAO" (J.2): the chosen option and its score, its 3 biggest plus and 2 biggest minus factors, and the runner-up.
    /// Kept for every scored decision; the local viewer draws it.
    /// </summary>
    public sealed class Why
    {
        public AiLayer Layer { get; internal set; }
        public int Team { get; internal set; }

        /// <summary>The squad id, the unit's entity id, or 0 for the commander.</summary>
        public int Subject { get; internal set; }
        public double Time { get; internal set; }
        public string Choice { get; internal set; } = "";
        public float Score { get; internal set; }
        public Factor[] Plus { get; internal set; } = Array.Empty<Factor>();
        public Factor[] Minus { get; internal set; } = Array.Empty<Factor>();
        public string? RunnerUp { get; internal set; }
        public float RunnerUpScore { get; internal set; }

        /// <summary>The squad's state, the unit's target, the commander's plan: the line the viewer heads the record with.</summary>
        public string Context { get; internal set; } = "";

        /// <summary>The events that led to it (the commander's plan).</summary>
        public IReadOnlyList<string> Events { get; internal set; } = Array.Empty<string>();

        public override string ToString() =>
            $"{Choice} {Score:0} ({string.Join("; ", Plus)}; {string.Join("; ", Minus)}){(RunnerUp != null ? $", then {RunnerUp} {RunnerUpScore:0}" : "")}";

        /// <summary>The top 3 plus and top 2 minus of <paramref name="factors"/>.</summary>
        internal static (Factor[] plus, Factor[] minus) Split(List<Factor> factors)
        {
            var plus = new List<Factor>();
            var minus = new List<Factor>();
            foreach (var f in factors)
                if (f.Points > 0f) plus.Add(f);
                else if (f.Points < 0f) minus.Add(f);
            // Stable sorts (by points, then key) so a replay prints the same record.
            plus.Sort((a, b) => b.Points != a.Points ? b.Points.CompareTo(a.Points) : string.CompareOrdinal(a.Key, b.Key));
            minus.Sort((a, b) => a.Points != b.Points ? a.Points.CompareTo(b.Points) : string.CompareOrdinal(a.Key, b.Key));
            if (plus.Count > 3) plus.RemoveRange(3, plus.Count - 3);
            if (minus.Count > 2) minus.RemoveRange(2, minus.Count - 2);
            return (plus.ToArray(), minus.ToArray());
        }
    }

    /// <summary>One replay log line (J.4).</summary>
    public readonly struct DecisionEntry
    {
        public DecisionEntry(double time, int team, AiLayer layer, int subject, DecisionKind kind, string text)
        {
            Time = time;
            Team = team;
            Layer = layer;
            Subject = subject;
            Kind = kind;
            Text = text;
        }

        public double Time { get; }
        public int Team { get; }
        public AiLayer Layer { get; }
        public int Subject { get; }
        public DecisionKind Kind { get; }
        public string Text { get; }

        public override string ToString() => $"{Time,7:0.00} t{Team} {Layer}#{Subject} {Kind}: {Text}";
    }

    /// <summary>
    /// Prompt 28 J.2-J.4: the latest "VÌ SAO" per decision maker, the churn counters (switches a minute per squad, with a
    /// warning flag) and the replay log of the commanders' plans, tactic switches, emergency repositions and actions.
    /// Writing here never feeds back into a decision, so it cannot change a battle; the log keeps the last
    /// <see cref="Capacity"/> lines.
    /// </summary>
    public sealed class DecisionLog
    {
        public const int Capacity = 4000;

        private readonly List<DecisionEntry> _entries = new();
        private int _start;
        private readonly Dictionary<(AiLayer, int, int), Why> _why = new();
        private readonly Dictionary<(int team, int squad), Churn> _churn = new();

        /// <summary>Switches a minute (action, target or state) of one squad above which the viewer warns (J.3).</summary>
        public float WarnPerMinute { get; set; } = 6f;

        /// <summary>The log in time order (oldest kept first).</summary>
        public IEnumerable<DecisionEntry> Entries
        {
            get
            {
                for (var i = 0; i < _entries.Count; i++) yield return _entries[(_start + i) % _entries.Count];
            }
        }

        public int Count => _entries.Count;

        public void Add(DecisionEntry entry)
        {
            if (_entries.Count < Capacity) _entries.Add(entry);
            else
            {
                _entries[_start] = entry;
                _start = (_start + 1) % Capacity;
            }
        }

        public Why? Latest(AiLayer layer, int team, int subject) => _why.TryGetValue((layer, team, subject), out var w) ? w : null;

        internal void Record(Why why) => _why[(why.Layer, why.Team, why.Subject)] = why;

        internal void Forget(AiLayer layer, int team, int subject) => _why.Remove((layer, team, subject));

        /// <summary>Counts one switch of a squad's action, state or target.</summary>
        internal void CountSwitch(int team, int squad, DecisionKind kind, double now)
        {
            if (!_churn.TryGetValue((team, squad), out var c)) _churn[(team, squad)] = c = new Churn();
            c.Add(kind, now);
        }

        /// <summary>A squad's switches in the last minute: actions, states, targets.</summary>
        public (int actions, int states, int targets) Switches(int team, int squad, double now) =>
            _churn.TryGetValue((team, squad), out var c) ? c.LastMinute(now) : (0, 0, 0);

        /// <summary>J.3: the squad switches its action, state or target more often than <see cref="WarnPerMinute"/>.</summary>
        public bool Churning(int team, int squad, double now)
        {
            var (a, s, t) = Switches(team, squad, now);
            return a > WarnPerMinute || s > WarnPerMinute || t > WarnPerMinute;
        }

        /// <summary>Every switch counted so far by kind (the churn metric of O.1, for the measures).</summary>
        public (int actions, int states, int targets) Totals()
        {
            int a = 0, s = 0, t = 0;
            foreach (var c in _churn.Values)
            {
                a += c.TotalActions;
                s += c.TotalStates;
                t += c.TotalTargets;
            }
            return (a, s, t);
        }

        private sealed class Churn
        {
            private readonly Queue<(double at, DecisionKind kind)> _recent = new();
            public int TotalActions, TotalStates, TotalTargets;

            public void Add(DecisionKind kind, double now)
            {
                _recent.Enqueue((now, kind));
                if (kind == DecisionKind.Action) TotalActions++;
                else if (kind == DecisionKind.State) TotalStates++;
                else if (kind == DecisionKind.Target) TotalTargets++;
                while (_recent.Count > 0 && now - _recent.Peek().at > 60.0) _recent.Dequeue();
            }

            public (int, int, int) LastMinute(double now)
            {
                int a = 0, s = 0, t = 0;
                foreach (var (at, kind) in _recent)
                {
                    if (now - at > 60.0) continue;
                    if (kind == DecisionKind.Action) a++;
                    else if (kind == DecisionKind.State) s++;
                    else if (kind == DecisionKind.Target) t++;
                }
                return (a, s, t);
            }
        }
    }
}

using System.Collections.Generic;
using MachineBrigade.Game.Views;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>Fix prompt L5: what a warning ring warns of.</summary>
    internal enum WarningKind
    {
        /// <summary>An enemy's T4 round (a gun from 203 mm, a 400 kg+ bomb, a 300 mm+ rocket).</summary>
        Round,

        /// <summary>An enemy's area support (an airstrike, a barrage, a cruise missile).</summary>
        Support,

        /// <summary>A super weapon: a boss's big attack, a T5 round (406 mm, 800 mm), an Ultimate support. Always shown, on top.</summary>
        Super,
    }

    /// <summary>
    /// Fix prompt L5 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): which warning rings are drawn. Every ring renderer
    /// (<see cref="EscapeWarnings"/>, the support telegraphs of <see cref="StrikeEffects"/>, <see cref="BigAttackZones"/>)
    /// offers its live rings every frame and draws a ring only while it is shown. At most
    /// <see cref="MachineBrigade.Sim.Content.WarningRules.MaxShown"/> (6) at once besides the super weapons, which are always
    /// shown and drawn on top: first those over most of the player's units, then those nearest the view. The rest keep their
    /// minimap mark only (MatchRunner's). The Settings choice: Full (that), Important only (the super weapons and the rings
    /// over the player's units), Off (the super weapons only). Decided at the end of a frame for the next (a new ring waits
    /// one frame; it fades in anyway). View only.
    /// </summary>
    internal sealed class WarningGate
    {
        /// <summary>The Settings choice (MatchSettings.WarningRings): 0 Full, 1 Important only, 2 Off.</summary>
        public int Level { get; set; }

        /// <summary>Rings shown at once at most, the super weapons not counted (data warningRules.maxShown).</summary>
        public int MaxShown { get; set; } = 6;

        /// <summary>The player's side (its units are what a ring threatens).</summary>
        public int PlayerTeam { get; set; }

        private readonly struct Offer
        {
            public Offer(object key, Vector3 at, float radius, WarningKind kind)
            {
                Key = key;
                At = at;
                Radius = radius;
                Kind = kind;
            }

            public object Key { get; }
            public Vector3 At { get; }
            public float Radius { get; }
            public WarningKind Kind { get; }
        }

        private readonly List<Offer> _offers = new();
        private readonly List<(float score, object key)> _ranked = new();
        private readonly HashSet<object> _shown = new();

        /// <summary>A live ring this frame (<paramref name="key"/>: the renderer's own object for it).</summary>
        public void Offer(object key, Vector3 at, float radius, WarningKind kind)
        {
            if (key == null) return;
            _offers.Add(new Offer(key, at, radius, kind));
        }

        /// <summary>Whether the ring <paramref name="key"/> is drawn (a super weapon always is).</summary>
        public bool Shown(object key, WarningKind kind) => kind == WarningKind.Super || (key != null && _shown.Contains(key));

        /// <summary>Rings decided shown now (the super weapons with them).</summary>
        public int ShownCount => _shown.Count;

        /// <summary>The end of a frame: picks the rings drawn next frame from those offered, then forgets the offers.</summary>
        public void Resolve(ViewRegistry views, Vector3 focus)
        {
            _shown.Clear();
            _ranked.Clear();
            foreach (var o in _offers)
            {
                if (o.Kind == WarningKind.Super)
                {
                    _shown.Add(o.Key);
                    continue;
                }
                if (Level >= 2) continue;
                var threat = Threat(views, o.At, o.Radius);
                if (Level == 1 && threat <= 0) continue;
                var near = 1f / (1f + Vector3.Distance(new Vector3(o.At.x, 0f, o.At.z), new Vector3(focus.x, 0f, focus.z)) / 40f);
                _ranked.Add((threat * 10f + near, o.Key));
            }
            _offers.Clear();
            _ranked.Sort((a, b) => b.score.CompareTo(a.score));
            for (var i = 0; i < _ranked.Count && i < Mathf.Max(1, MaxShown); i++) _shown.Add(_ranked[i].key);
        }

        /// <summary>The player's units the ring at <paramref name="at"/> reaches (their hulls inside it).</summary>
        private int Threat(ViewRegistry views, Vector3 at, float radius)
        {
            if (views == null) return 0;
            var n = 0;
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var v = all[i];
                if (v == null || v.Sim == null || !v.Sim.IsAlive || v.Sim.Team != PlayerTeam) continue;
                var dx = v.Sim.Position.X - at.x;
                var dz = v.Sim.Position.Y - at.z;
                var reach = radius + v.Sim.Radius;
                if (dx * dx + dz * dz <= reach * reach) n++;
            }
            return n;
        }
    }
}

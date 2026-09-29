using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Prompt 23 F.2: one direction reinforcements come from, as the minimap draws it.</summary>
    internal struct DirectionMark
    {
        /// <summary>On the ground: x east, y north, unit length.</summary>
        public Vector2 Direction;

        /// <summary>The enemy's (red); otherwise ours, the Meridian Accord's (sky blue).</summary>
        public bool Enemy;

        /// <summary>1 while the warning runs, down to 0 as it ends.</summary>
        public float Alpha;

        /// <summary>Where they come in, when the event system knows (<see cref="HasAt"/>): the minimap's arrow stands there.</summary>
        public Vector2 At;

        public bool HasAt;
    }

    /// <summary>
    /// Prompt 23 F.2: where reinforcements are coming from, for as long as their warning runs. Each direction is an arrow at
    /// the minimap's edge on that side (drawn by <see cref="Minimap"/> from <see cref="Marks"/>) and a small round indicator
    /// at the screen's edge in the same direction, its arrow pointing out towards them: red for the enemy's, sky blue for the
    /// Accord's. Up to <see cref="Max"/> at once; a second warning from nearly the same side (within 20 degrees) keeps the
    /// first one up longer instead of adding another. The indicator sits on the line from the screen's middle in that
    /// direction, as far out as it can without touching the HUD (the minimap, the top strip and the notices, pause, the
    /// rail, the selection, the tray and the dialogue line): it slides in along that line past anything in the way, so it
    /// always points true. Five elements at most, moved with translate (no layout): cheap on a phone.
    /// </summary>
    internal sealed class DirectionArrows
    {
        public const int Max = 4;

        /// <summary>The shortest an arrow stays up, whatever the notice asked (a warning is read, then looked for).</summary>
        public const float MinSeconds = 3f;

        private const float FadeIn = 0.2f, FadeOut = 0.6f, PulseSeconds = 2f;
        private const float SameSide = 0.94f; // cos 20 degrees
        private const float Margin = 8f, Step = 6f, Gap = 6f;

        private struct Arrow
        {
            public Vector2 Direction, At;
            public bool Enemy, HasAt;
            public float From, Until;
        }

        private readonly List<Arrow> _arrows = new();
        private readonly List<DirectionMark> _marks = new();
        private readonly VisualElement[] _indicators = new VisualElement[Max];
        private readonly IconElement[] _icons = new IconElement[Max];
        private readonly bool[] _shown = new bool[Max];
        private readonly List<Rect> _blocked = new();
        private bool _changed;

        public DirectionArrows()
        {
            Layer = Kit.Box("fc-edge-layer");
            for (var i = 0; i < Max; i++)
            {
                var indicator = Kit.Box("fc-edge-arrow");
                var icon = Kit.Icon("arrow", "fc-edge-arrow__icon", 2.4f);
                indicator.Add(icon);
                indicator.style.display = DisplayStyle.None;
                _indicators[i] = indicator;
                _icons[i] = icon;
                Layer.Add(indicator);
            }
        }

        /// <summary>The screen-edge indicators' layer, filling the safe area, under every control.</summary>
        public VisualElement Layer { get; }

        /// <summary>The directions up now, for the minimap.</summary>
        public IReadOnlyList<DirectionMark> Marks => _marks;

        /// <summary>Directions up (the checks).</summary>
        internal int Count => _arrows.Count;

        /// <summary>Indicators on screen (the checks).</summary>
        internal int Showing
        {
            get
            {
                var n = 0;
                for (var i = 0; i < Max; i++)
                    if (_shown[i]) n++;
                return n;
            }
        }

        /// <summary>An indicator (the checks read where it is).</summary>
        internal VisualElement Indicator(int i) => _indicators[i];

        /// <summary>
        /// Reinforcements coming from <paramref name="direction"/> (on the ground, x east, y north: from the player's side
        /// towards them) for <paramref name="seconds"/> (the warning time; at least <see cref="MinSeconds"/>), coming in at
        /// <paramref name="at"/> when known. <paramref name="now"/> is the battle's clock (it stops under the pause).
        /// </summary>
        public void Add(Vector2 direction, float seconds, bool enemy, float now, Vector2? at = null)
        {
            if (direction.sqrMagnitude < 1e-6f) return;
            direction.Normalize();
            var until = now + Mathf.Max(MinSeconds, seconds);
            for (var i = 0; i < _arrows.Count; i++)
            {
                var a = _arrows[i];
                if (a.Enemy != enemy || Vector2.Dot(a.Direction, direction) < SameSide) continue;
                a.Until = Mathf.Max(a.Until, until);
                if (at is { } point && !a.HasAt)
                {
                    a.At = point;
                    a.HasAt = true;
                    _changed = true;
                }
                _arrows[i] = a;
                return;
            }
            if (_arrows.Count >= Max)
            {
                // Full: the one closest to its end makes room.
                var soonest = 0;
                for (var i = 1; i < _arrows.Count; i++)
                    if (_arrows[i].Until < _arrows[soonest].Until) soonest = i;
                _arrows.RemoveAt(soonest);
            }
            _arrows.Add(new Arrow { Direction = direction, Enemy = enemy, From = now, Until = until, At = at ?? default, HasAt = at.HasValue });
            _changed = true;
        }

        public void Clear()
        {
            _changed |= _arrows.Count > 0;
            _arrows.Clear();
        }

        /// <summary>
        /// Every frame: ends the arrows whose warning is over, hands the rest to the minimap and places the indicators clear
        /// of <paramref name="keepOut"/> (the HUD's controls, in panel coordinates), turned as the minimap turns the map.
        /// </summary>
        public void Tick(float now, Minimap minimap, IReadOnlyList<Rect> keepOut)
        {
            for (var i = _arrows.Count - 1; i >= 0; i--)
                if (now >= _arrows[i].Until)
                {
                    _arrows.RemoveAt(i);
                    _changed = true;
                }
            _marks.Clear();
            foreach (var a in _arrows) _marks.Add(new DirectionMark { Direction = a.Direction, Enemy = a.Enemy, Alpha = Alpha(a, now), At = a.At, HasAt = a.HasAt });
            if (minimap != null)
            {
                minimap.Arrows = _marks;
                if (_changed) minimap.ArrowsChanged();
            }
            _changed = false;
            Place(now, minimap, keepOut);
        }

        private static float Alpha(in Arrow a, float now) =>
            Mathf.Clamp01(Mathf.Min((now - a.From) / FadeIn, (a.Until - now) / FadeOut));

        private void Place(float now, Minimap minimap, IReadOnlyList<Rect> keepOut)
        {
            var box = Layer.contentRect;
            var ready = box.width > 40f && box.height > 40f && Layer.panel != null;
            var size = _indicators[0].resolvedStyle.width > 1f ? _indicators[0].resolvedStyle.width : 40f;
            var half = size * 0.5f;
            var count = ready ? Mathf.Min(Max, _arrows.Count) : 0;
            for (var i = 0; i < count; i++)
            {
                var a = _arrows[i];
                // Towards where they come in from the middle of the view when both are known, else the warning's direction;
                // turned as the view is, then the panel's (y down).
                var towards = a.HasAt && minimap != null && minimap.TryViewCentre(out var middle) && (a.At - middle).sqrMagnitude > 1f ? a.At - middle : a.Direction;
                var view = minimap != null ? minimap.ViewDirection(towards) : DefaultView(towards);
                var screen = new Vector2(view.x, -view.y);
                if (screen.sqrMagnitude < 1e-6f) screen = Vector2.up;
                _screen[i] = screen.normalized;
            }
            // Where they go only changes with the HUD and the arrows: worked out again only then.
            var signature = Signature(box, keepOut, count);
            if (signature != _signature)
            {
                _signature = signature;
                _blocked.Clear();
                if (ready && keepOut != null)
                    foreach (var r in keepOut) _blocked.Add(Layer.WorldToLocal(r));
                var frame = new Rect(box.xMin + Margin + half, box.yMin + Margin + half, box.width - 2f * (Margin + half), box.height - 2f * (Margin + half));
                for (var i = 0; i < count; i++)
                {
                    _found[i] = Find(frame, _screen[i], size, out _at[i]);
                    if (_found[i]) _blocked.Add(new Rect(_at[i].x - half, _at[i].y - half, size, size));
                }
            }
            for (var i = 0; i < Max; i++)
            {
                // Nowhere clear (a screen crowded with panels): the minimap's arrow says it alone.
                if (i >= count || !_found[i])
                {
                    Show(i, false);
                    continue;
                }
                var a = _arrows[i];
                var indicator = _indicators[i];
                indicator.style.translate = new Translate(_at[i].x - half, _at[i].y - half);
                // Pointing out towards them wherever it stands; a gentle beat for the first two seconds.
                _icons[i].style.rotate = new Rotate(Mathf.Atan2(_screen[i].y, _screen[i].x) * Mathf.Rad2Deg);
                var age = now - a.From;
                var beat = age < PulseSeconds ? 1f + 0.1f * Mathf.Abs(Mathf.Sin(age * 6f)) : 1f;
                indicator.style.scale = new Scale(new Vector3(beat, beat, 1f));
                indicator.style.opacity = Alpha(a, now);
                indicator.EnableInClassList("fc-edge-arrow--ours", !a.Enemy);
                Show(i, true);
            }
        }

        private readonly Vector2[] _screen = new Vector2[Max], _at = new Vector2[Max];
        private readonly bool[] _found = new bool[Max];
        private int _signature;

        private int Signature(Rect box, IReadOnlyList<Rect> keepOut, int count)
        {
            var h = new System.HashCode();
            h.Add(Mathf.RoundToInt(box.width));
            h.Add(Mathf.RoundToInt(box.height));
            if (keepOut != null)
                foreach (var r in keepOut)
                {
                    h.Add(Mathf.RoundToInt(r.x));
                    h.Add(Mathf.RoundToInt(r.y));
                    h.Add(Mathf.RoundToInt(r.width));
                    h.Add(Mathf.RoundToInt(r.height));
                }
            for (var i = 0; i < count; i++)
            {
                h.Add(Mathf.RoundToInt(_screen[i].x * 500f));
                h.Add(Mathf.RoundToInt(_screen[i].y * 500f));
            }
            h.Add(count);
            return h.ToHashCode();
        }

        /// <summary>
        /// Where an indicator for <paramref name="screen"/> (a panel direction from the middle) goes, clear of the HUD: first
        /// along that line from the edge in to 60 % of the way; then at the edge either side of it, up to 90 degrees off,
        /// nearest first, which keeps it on that side of the screen; then further in along the line; last, on rings further
        /// in all round, nearest in angle first. Its arrow points true wherever it stands.
        /// </summary>
        private bool Find(Rect frame, Vector2 screen, float size, out Vector2 at)
        {
            var centre = frame.center;
            var reach = Reach(frame, screen);
            for (var d = reach; d >= reach * 0.6f; d -= Step)
                if (Clear(at = centre + screen * d, size)) return true;
            for (var off = AngleStep; off <= 90f; off += AngleStep)
                foreach (var sign in Signs)
                {
                    var turned = Rotate(screen, sign * off);
                    var edge = Reach(frame, turned);
                    for (var k = 0; k < 3; k++)
                        if (Clear(at = centre + turned * (edge - k * 12f), size)) return true;
                }
            for (var d = reach * 0.6f; d >= reach * 0.2f; d -= Step)
                if (Clear(at = centre + screen * d, size)) return true;
            for (var inset = 48f; inset <= 168f; inset += 40f)
            {
                var ring = new Rect(frame.xMin + inset, frame.yMin + inset, frame.width - 2f * inset, frame.height - 2f * inset);
                if (ring.width < size || ring.height < size) break;
                for (var off = 0f; off <= 180f; off += AngleStep)
                    foreach (var sign in Signs)
                    {
                        var turned = Rotate(screen, sign * off);
                        if (Clear(at = ring.center + turned * Reach(ring, turned), size)) return true;
                    }
            }
            at = default;
            return false;
        }

        private const float AngleStep = 6f;
        private static readonly float[] Signs = { 1f, -1f };

        /// <summary>How far from the frame's middle a line in <paramref name="d"/> meets the frame.</summary>
        private static float Reach(Rect frame, Vector2 d)
        {
            var tx = Mathf.Abs(d.x) > 1e-4f ? frame.width * 0.5f / Mathf.Abs(d.x) : float.MaxValue;
            var ty = Mathf.Abs(d.y) > 1e-4f ? frame.height * 0.5f / Mathf.Abs(d.y) : float.MaxValue;
            return Mathf.Min(tx, ty);
        }

        private static Vector2 Rotate(Vector2 v, float degrees)
        {
            var r = degrees * Mathf.Deg2Rad;
            float c = Mathf.Cos(r), s = Mathf.Sin(r);
            return new Vector2(v.x * c - v.y * s, v.x * s + v.y * c);
        }

        private bool Clear(Vector2 p, float size)
        {
            var r = new Rect(p.x - size * 0.5f - Gap, p.y - size * 0.5f - Gap, size + 2f * Gap, size + 2f * Gap);
            foreach (var b in _blocked)
                if (b.Overlaps(r)) return false;
            return true;
        }

        private void Show(int i, bool on)
        {
            if (_shown[i] == on) return;
            _shown[i] = on;
            _indicators[i].style.display = on ? DisplayStyle.Flex : DisplayStyle.None;
        }

        /// <summary>The square maps' view (north-west up), when there is no minimap.</summary>
        private static Vector2 DefaultView(Vector2 d)
        {
            const float c = 0.70710678f;
            return new Vector2(d.x * c + d.y * c, -d.x * c + d.y * c);
        }
    }

    /// <summary>
    /// Prompt 23 F.5 and H.9: a small name label over an enemy general's vehicle on the field: the general's short name (the
    /// dialogue's, in capitals) in the enemy speakers' red on the dialogue's dim strip, and while that general's line is on
    /// show a small speaking mark before the name (sound bars that beat), never a speech bubble. A label is hidden where it
    /// would touch the HUD (the dialogue line, the notices, the tray...), under which it lies anyway. A pool of
    /// <see cref="Max"/>, placed by the runner every frame with <see cref="Begin"/>, <see cref="Place"/> and <see cref="End"/>.
    /// </summary>
    internal sealed class GeneralTags
    {
        public const int Max = 4;

        private readonly VisualElement[] _tags = new VisualElement[Max];
        private readonly Label[] _names = new Label[Max];
        private readonly IconElement[] _marks = new IconElement[Max];
        private readonly string[] _shownName = new string[Max];
        private readonly bool[] _shown = new bool[Max];
        private readonly bool[] _speaking = new bool[Max];
        private readonly List<Rect> _blocked = new();
        private int _next;

        public GeneralTags()
        {
            Layer = Kit.Box("fc-general-tags");
            for (var i = 0; i < Max; i++)
            {
                var tag = Kit.Box("fc-general-tag");
                var mark = Kit.Icon("speaking", "fc-general-tag__mark", 2.4f);
                var name = Kit.Text("", "fc-general-tag__name");
                tag.Add(mark);
                tag.Add(name);
                tag.style.display = DisplayStyle.None;
                _tags[i] = tag;
                _names[i] = name;
                _marks[i] = mark;
                Layer.Add(tag);
            }
        }

        /// <summary>The labels' layer, filling the screen under every control.</summary>
        public VisualElement Layer { get; }

        /// <summary>Labels on screen (the checks).</summary>
        internal int Showing
        {
            get
            {
                var n = 0;
                for (var i = 0; i < Max; i++)
                    if (_shown[i]) n++;
                return n;
            }
        }

        /// <summary>A label (the checks).</summary>
        internal VisualElement Tag(int i) => _tags[i];

        internal string NameShown(int i) => _names[i].text;

        internal bool SpeakingShown(int i) => _shown[i] && _speaking[i];

        /// <summary>A new frame of labels: the HUD's controls to keep clear of, in panel coordinates.</summary>
        public void Begin(IReadOnlyList<Rect> keepOut)
        {
            _next = 0;
            _blocked.Clear();
            if (keepOut != null && Layer.panel != null)
                foreach (var r in keepOut) _blocked.Add(Layer.WorldToLocal(r));
        }

        /// <summary>
        /// A label for <paramref name="general"/> standing on <paramref name="panelPoint"/> (above its vehicle's health bar,
        /// panel coordinates); <paramref name="speaking"/>: their line is on show. False when no label is left or it would
        /// touch the HUD.
        /// </summary>
        public bool Place(Vector2 panelPoint, string general, bool speaking, float now)
        {
            if (_next >= Max || string.IsNullOrEmpty(general)) return false;
            var at = Layer.panel != null ? Layer.WorldToLocal(panelPoint) : panelPoint;
            var area = Layer.contentRect;
            if (area.width > 1f && !area.Contains(at)) return false;
            var i = _next;
            var tag = _tags[i];
            var size = tag.layout.width > 1f ? tag.layout.size : new Vector2(120f, 30f);
            var rect = new Rect(at.x - size.x * 0.5f, at.y - size.y, size.x, size.y);
            foreach (var b in _blocked)
                if (b.Overlaps(rect)) return false;
            _next++;
            var name = Kit.Caps(DialogueText.Name(general));
            if (_shownName[i] != name) _names[i].text = _shownName[i] = name;
            tag.style.left = at.x;
            tag.style.top = at.y;
            if (_speaking[i] != speaking)
            {
                _speaking[i] = speaking;
                tag.EnableInClassList("fc-general-tag--speaking", speaking);
            }
            if (speaking) _marks[i].style.opacity = 0.55f + 0.45f * Mathf.Abs(Mathf.Sin(now * 5f));
            if (!_shown[i])
            {
                _shown[i] = true;
                tag.style.display = DisplayStyle.Flex;
            }
            return true;
        }

        /// <summary>Hides the labels this frame did not place.</summary>
        public void End()
        {
            for (var i = _next; i < Max; i++)
            {
                if (!_shown[i]) continue;
                _shown[i] = false;
                _tags[i].style.display = DisplayStyle.None;
            }
        }
    }
}

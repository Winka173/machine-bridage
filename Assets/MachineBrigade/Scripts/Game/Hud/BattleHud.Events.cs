using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 23 F.2, F.3 and F.5 on the battle HUD (DECISIONS 23F), kept apart from BattleHud.cs:
    /// <list type="bullet">
    /// <item>F.2: a notice with a <see cref="HudNotice.Direction"/> (or <see cref="Arrow"/>) puts up an arrow at the minimap's
    /// edge and a small indicator at the screen's edge for as long as the warning runs (<see cref="DirectionArrows"/>).</item>
    /// <item>F.3: a side objective's row on the mission bar with its clock (<see cref="SideObjective"/>,
    /// <see cref="SideObjectiveDone"/>) and a short notice when it ends.</item>
    /// <item>F.5: the name labels over the enemy generals' vehicles (<see cref="GeneralTags"/>), placed by the runner.</item>
    /// </list>
    /// All three keep clear of the HUD's controls: <see cref="KeepOut"/> is the list, fresh every frame.
    /// </summary>
    public sealed partial class BattleHud
    {
        private DirectionArrows _arrows;
        private GeneralTags _generalTags;
        private readonly List<Rect> _keepOut = new();
        private VisualElement _keepTop, _keepUnder, _keepLeft, _keepRail;
        private float? _eventClock;

        /// <summary>F.2: the direction arrows (null in the menu).</summary>
        internal DirectionArrows DirectionArrows => _arrows;

        /// <summary>F.5: the generals' name labels (null in the menu).</summary>
        internal GeneralTags GeneralTags => _generalTags;

        /// <summary>
        /// The battle's clock for warnings and side objectives: Unity's scaled time, which stops under the pause and slows with
        /// a story moment as the simulation does. The checks set it.
        /// </summary>
        internal float EventClock
        {
            get => _eventClock ?? Time.time;
            set => _eventClock = value;
        }

        /// <summary>The HUD's controls the event markers keep clear of this frame (panel coordinates).</summary>
        internal IReadOnlyList<Rect> KeepOut => _keepOut;

        private void BuildEventMarkers()
        {
            // The edge indicators in the safe area, under every control; the name labels under the whole HUD, like the
            // equipment's words.
            _arrows = new DirectionArrows();
            _safe.Insert(0, _arrows.Layer);
            _generalTags = new GeneralTags();
            var hud = _safe.parent;
            hud.Insert(hud.IndexOf(_safe), _generalTags.Layer);
            _keepTop = _safe.Q(className: "fc-hud__top");
            _keepUnder = _safe.Q(className: "fc-hud__under");
            _keepLeft = _safe.Q(className: "fc-hud__left");
            _keepRail = _safe.Q(className: "fc-hud__rail");
            if (Minimap != null) Minimap.Arrows = _arrows.Marks;
            LanguageSwitched += RefreshSideObjective;
        }

        /// <summary>
        /// F.2: reinforcements coming from <paramref name="direction"/> (on the ground, x east, y north: from the player's side
        /// towards them) for <paramref name="seconds"/> (their warning), coming in at <paramref name="at"/> when known: an arrow
        /// on the minimap and at the screen's edge, red for the enemy's, sky blue for the Accord's. Called again for the same
        /// side it keeps that arrow up (the runner reports the event system's arrows a few times a second).
        /// </summary>
        public void Arrow(System.Numerics.Vector2 direction, float seconds, bool enemy = true, System.Numerics.Vector2? at = null) =>
            _arrows?.Add(new Vector2(direction.X, direction.Y), seconds, enemy, EventClock, at is { } p ? new Vector2(p.X, p.Y) : null);

        /// <summary>
        /// F.2: a notice with a <see cref="HudNotice.Direction"/> puts up its arrow at once (an alert's is the enemy's, as 23A
        /// sends bad news; <see cref="NoticeKind.Accord"/>'s is the Accord's), for its seconds (at least
        /// <see cref="DirectionArrows.MinSeconds"/>). Off while the event system's adapter reports the arrows with their full
        /// warning time (<c>MatchRunner.EventHudSource</c>).
        /// </summary>
        internal bool ArrowsFromNotices { get; set; } = true;

        /// <summary>The notice on show and those waiting (the checks).</summary>
        internal string NoticeText => _toastText?.text;

        internal IEnumerable<HudNotice> NoticesWaiting => _toastQueue;

        /// <summary>F.5: a world point on the panel (false behind the camera or before the HUD is on a panel).</summary>
        internal bool WorldToPanel(Vector3 world, Camera camera, out Vector2 point)
        {
            point = default;
            if (camera == null || _root.panel == null) return false;
            var screen = camera.WorldToScreenPoint(world);
            if (screen.z <= 0f) return false;
            point = RuntimePanelUtils.ScreenToPanel(_root.panel, new Vector2(screen.x, Screen.height - screen.y));
            return true;
        }

        /// <summary>A notice arrived: its direction, if it has one, becomes an arrow at once (even while the notice waits its turn).</summary>
        private void NoticeArrow(in HudNotice notice)
        {
            if (ArrowsFromNotices && notice.Direction is { } towards) Arrow(towards, notice.Seconds, notice.Alert && notice.Kind != NoticeKind.Accord);
        }

        /// <summary>Every frame: what to keep clear of, the arrows, the side objective's clock.</summary>
        internal void TickEvents()
        {
            if (_arrows == null) return;
            CollectKeepOut();
            var now = EventClock;
            _arrows.Tick(now, Minimap, _keepOut);
            TickSideObjective(now);
        }

        private void CollectKeepOut()
        {
            _keepOut.Clear();
            // The top strip and the column under it are wide boxes round narrower, centred panels: their panels count, and
            // the notice's place whether one shows or not.
            KeepChildren(_keepTop);
            KeepChildren(_keepUnder);
            if (_toast != null && _toast.panel != null && _toast.worldBound.height >= 1f) _keepOut.Add(_toast.worldBound);
            Keep(_keepLeft);
            Keep(_corner);
            Keep(_keepRail);
            Keep(_command);
            Keep(_deck?.Root);
            Keep(_items?.Root);
            Keep(_hintBar);
            Keep(_targeting);
            Keep(_banner);
            if (_dialogue != null && _dialogue.Root.panel != null)
            {
                // The dialogue line's place is kept whether a line shows or not, two lines high, so nothing jumps when one starts.
                var r = _dialogue.Root.worldBound;
                var font = _dialogue.Label.resolvedStyle.fontSize;
                var high = Mathf.Max(r.height, font * 2.7f + 12f);
                if (r.width > 1f && !float.IsNaN(r.x)) _keepOut.Add(new Rect(r.xMin, r.yMax - high, r.width, high));
            }
        }

        private void KeepChildren(VisualElement e)
        {
            if (e == null || e.resolvedStyle.display == DisplayStyle.None) return;
            foreach (var child in e.Children())
                if (child != _toast) Keep(child);
        }

        private void Keep(VisualElement e)
        {
            if (e == null || e.panel == null) return;
            var style = e.resolvedStyle;
            if (style.display == DisplayStyle.None || style.visibility == Visibility.Hidden || style.opacity < 0.05f) return;
            var r = e.worldBound;
            if (r.width < 1f || r.height < 1f || float.IsNaN(r.x)) return;
            _keepOut.Add(r);
        }

        // ------------------------------------------------------------------------------------------------ F.3

        private string _sideId, _sideText;
        private float _sideUntil;
        private bool _sideTimed;
        private int _sideShown = -1, _sideCount, _sideNeeded;

        /// <summary>The side objective on show (null: none).</summary>
        internal string SideObjectiveId => _sideId;

        /// <summary>F.3: the mission bar's side objective row (null outside a mission).</summary>
        internal VisualElement SideObjectiveRow => _missionBar?.SideRow;

        /// <summary>
        /// F.3: a side objective starts (or, with the same <paramref name="id"/>, is brought up to date): a row on the mission
        /// bar with what to do (<paramref name="text"/>: a text key, or a text), how far along (<paramref name="count"/> of
        /// <paramref name="needed"/>; 0 needed: no count) and a clock of <paramref name="secondsLeft"/> (0 or less: none), and,
        /// when new and <paramref name="announce"/>, a notice. One at a time: a new id takes the row. Between calls the clock
        /// runs on the battle's time; the simulation decides the outcome and says it with <see cref="SideObjectiveDone"/>.
        /// </summary>
        public void SideObjective(string id, string text, float secondsLeft, int count = 0, int needed = 0, bool announce = true)
        {
            if (_missionBar == null || string.IsNullOrEmpty(id)) return;
            var fresh = id != _sideId;
            _sideId = id;
            _sideText = text;
            _sideTimed = secondsLeft > 0f;
            _sideUntil = EventClock + Mathf.Max(0f, secondsLeft);
            _sideCount = count;
            _sideNeeded = needed;
            _sideShown = int.MinValue;
            _safe.EnableInClassList("fc-hud--side-goal", true);
            TickSideObjective(EventClock);
            if (fresh && announce) Toast(Strings.Format("toast.side.new", ("goal", SideText)), kind: NoticeKind.Objective);
        }

        /// <summary>F.3: the side objective <paramref name="id"/> ended (done, or failed at its time-out): its row goes and a short notice says how.</summary>
        public void SideObjectiveDone(string id, bool success, bool announce = true)
        {
            if (_sideId == null || id != _sideId) return;
            var goal = SideText;
            ClearSideObjective();
            if (announce) Toast(Strings.Format(success ? "toast.side.done" : "toast.side.failed", ("goal", goal)), kind: success ? NoticeKind.Done : NoticeKind.Objective);
        }

        private string SideText => string.IsNullOrEmpty(_sideText) ? "" : Strings.Has(_sideText) ? Strings.Get(_sideText) : _sideText;

        private void ClearSideObjective()
        {
            _sideId = null;
            _missionBar?.HideSide();
            _safe?.EnableInClassList("fc-hud--side-goal", false);
        }

        private void TickSideObjective(float now)
        {
            if (_sideId == null || _missionBar == null) return;
            var left = _sideUntil - now;
            // The simulation says the outcome; a clock that ran out without a word goes quietly after a few seconds.
            if (_sideTimed && left < -5f)
            {
                ClearSideObjective();
                return;
            }
            var seconds = _sideTimed ? Mathf.CeilToInt(Mathf.Max(0f, left)) : -1;
            if (seconds == _sideShown) return;
            _sideShown = seconds;
            var clock = seconds < 0 ? "" : $"{seconds / 60}:{seconds % 60:00}";
            var count = _sideNeeded > 0 ? $"{_sideCount}/{_sideNeeded}" : "";
            _missionBar.ShowSide(SideText, count, clock, seconds >= 0 && seconds <= 10);
        }

        private void RefreshSideObjective()
        {
            if (_sideId == null) return;
            _sideShown = int.MinValue;
            TickSideObjective(EventClock);
        }
    }
}

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>An objective as the HUD shows it.</summary>
    public readonly struct PointInfo
    {
        public PointInfo(string id, int owner, float progress, bool contested)
        {
            Id = id;
            Owner = owner;
            Progress = progress;
            Contested = contested;
        }

        public string Id { get; }

        /// <summary>0 = player, 1 = enemy, -1 = neutral.</summary>
        public int Owner { get; }

        /// <summary>-1 (enemy hold) .. +1 (player hold).</summary>
        public float Progress { get; }

        public bool Contested { get; }
    }

    /// <summary>
    /// The score across the top on the kit (Field Command 2.0, G): our side and theirs, each a number
    /// over what it counts and a draining bar, round the objective chips (each ringed by its capture
    /// progress in the capturing side's colour; a tap points the army at it), the clock under them.
    /// </summary>
    internal sealed class ScoreBar
    {
        private readonly Label _ours, _theirs;
        private readonly VisualElement _oursFill, _theirsFill;
        private readonly VisualElement _chips;
        private readonly Label _timer;
        private readonly List<PointChip> _points = new();
        private readonly string _label;
        private string _shownTimer;

        public ScoreBar(string labelKey = "stat.tickets")
        {
            _label = labelKey;
            Root = Kit.Box("fc-score");
            _ours = Side(Root, true, out _oursFill);
            var centre = Kit.Box("fc-score__centre");
            _chips = Kit.Box("fc-score__chips");
            centre.Add(_chips);
            _timer = Kit.Text("", "fc-number-small fc-hud__clock");
            _timer.style.display = DisplayStyle.None;
            centre.Add(_timer);
            Root.Add(centre);
            _theirs = Side(Root, false, out _theirsFill);
        }

        public void SetTimer(float secondsLeft)
        {
            var text = secondsLeft < 0f ? "" : $"{(int)secondsLeft / 60}:{(int)secondsLeft % 60:00}";
            if (text == _shownTimer) return;
            _timer.text = _shownTimer = text;
            _timer.style.display = text.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _timer.EnableInClassList("fc-hud__clock--urgent", secondsLeft >= 0f && secondsLeft < 60f);
        }

        public VisualElement Root { get; }

        /// <summary>An objective chip was tapped (the player points the army at it).</summary>
        public event Action<string> PointPressed;

        private int _shownOurs = -1, _shownTheirs = -1, _shownMax = -1;

        public void SetFocus(string id)
        {
            foreach (var chip in _points) chip.EnableInClassList("fc-point--focus", chip.Id == id);
        }

        public void Update(int ours, int theirs, int max, IReadOnlyList<PointInfo> points)
        {
            if (ours != _shownOurs || theirs != _shownTheirs || max != _shownMax)
            {
                _shownOurs = ours;
                _shownTheirs = theirs;
                _shownMax = max;
                _ours.text = ours.ToString();
                _theirs.text = theirs.ToString();
                _oursFill.style.width = Length.Percent(Mathf.Clamp01(ours / (float)Mathf.Max(1, max)) * 100f);
                _theirsFill.style.width = Length.Percent(Mathf.Clamp01(theirs / (float)Mathf.Max(1, max)) * 100f);
            }
            PointChip.Fill(_chips, _points, points, id => PointPressed?.Invoke(id));
        }

        private Label Side(VisualElement parent, bool ours, out VisualElement fill)
        {
            var box = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-score__side " + (ours ? "fc-score__side--ours" : "fc-score__side--theirs"));
            var number = Kit.Text("0", "fc-number fc-score__number");
            var column = Kit.Box("fc-score__column");
            column.Add(Kit.Caption(Strings.Get(ours ? "hud.us" : "hud.enemy") + " · " + Strings.Get(_label)));
            var track = Kit.Box("fc-score__track");
            fill = Kit.Box("fc-score__fill");
            track.Add(fill);
            column.Add(track);
            if (ours)
            {
                box.Add(number);
                box.Add(column);
            }
            else
            {
                box.Add(column);
                box.Add(number);
            }
            parent.Add(box);
            return number;
        }
    }

    /// <summary>
    /// A capture point's letter inside its progress ring, a full touch target (the ring sits inside
    /// the padding). The ring's colours come from the theme (--point-ours, --point-theirs, --point-track).
    /// </summary>
    internal sealed class PointChip : VisualElement
    {
        private static readonly CustomStyleProperty<Color> OursColour = new("--point-ours");
        private static readonly CustomStyleProperty<Color> TheirsColour = new("--point-theirs");
        private static readonly CustomStyleProperty<Color> TrackColour = new("--point-track");

        private readonly Label _letter;
        private PointInfo _info;
        private Color _ours, _theirs, _track;

        public PointChip()
        {
            AddToClassList("fc-point");
            pickingMode = PickingMode.Position;
            var face = Kit.Box("fc-point__face");
            _letter = Kit.Text("", "fc-number-small fc-point__letter");
            face.Add(_letter);
            Add(face);
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(_ =>
            {
                customStyle.TryGetValue(OursColour, out _ours);
                customStyle.TryGetValue(TheirsColour, out _theirs);
                customStyle.TryGetValue(TrackColour, out _track);
                MarkDirtyRepaint();
            });
        }

        public string Id => _info.Id;

        /// <summary>Keeps a row of chips in step with the points (new chips point the army when tapped).</summary>
        internal static void Fill(VisualElement row, List<PointChip> chips, IReadOnlyList<PointInfo> points, Action<string> pressed)
        {
            while (chips.Count < points.Count)
            {
                var chip = new PointChip();
                chip.AddManipulator(new Tap(() =>
                {
                    if (chip.Id != null) pressed(chip.Id);
                }));
                row.Add(chip);
                chips.Add(chip);
            }
            for (var i = 0; i < points.Count; i++) chips[i].Set(points[i]);
        }

        public void Set(PointInfo info)
        {
            var changed = info.Owner != _info.Owner || Mathf.Abs(info.Progress - _info.Progress) > 0.005f || info.Contested != _info.Contested;
            if (info.Id != _info.Id) _letter.text = Strings.Get("point." + info.Id);
            _info = info;
            EnableInClassList("fc-point--ours", info.Owner == 0);
            EnableInClassList("fc-point--theirs", info.Owner == 1);
            EnableInClassList("fc-point--contested", info.Contested);
            if (changed) MarkDirtyRepaint();
        }

        private void Draw(MeshGenerationContext context)
        {
            var rect = contentRect;
            var centre = rect.center;
            var radius = Mathf.Min(rect.width, rect.height) * 0.5f - 2f;
            var p = context.painter2D;
            p.lineWidth = 3f;
            p.strokeColor = _track;
            p.BeginPath();
            p.Arc(centre, radius, 0f, 360f);
            p.Stroke();

            var amount = Mathf.Abs(_info.Progress);
            if (amount < 0.01f) return;
            p.strokeColor = _info.Progress > 0f ? _ours : _theirs;
            p.lineCap = LineCap.Round;
            p.BeginPath();
            p.Arc(centre, radius, -90f, -90f + 360f * amount);
            p.Stroke();
        }
    }
}

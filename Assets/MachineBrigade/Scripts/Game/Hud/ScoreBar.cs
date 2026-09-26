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
    /// Conquest scoreboard for the top bar: both sides' tickets as draining bars around the
    /// objective chips, each chip ringed by its capture progress in the capturing side's colour.
    /// </summary>
    internal sealed class ScoreBar
    {
        private readonly Label _ours, _theirs;
        private readonly VisualElement _oursFill, _theirsFill;
        private readonly VisualElement _chips;
        private readonly List<PointChip> _points = new();

        public ScoreBar()
        {
            Root = UiKit.Box("score");
            _ours = Side(Root, "ours", out _oursFill);
            _chips = UiKit.Box("chips");
            Root.Add(_chips);
            _theirs = Side(Root, "theirs", out _theirsFill);
        }

        public VisualElement Root { get; }

        public void Update(int ours, int theirs, int max, IReadOnlyList<PointInfo> points)
        {
            _ours.text = ours.ToString();
            _theirs.text = theirs.ToString();
            _oursFill.style.width = Length.Percent(Mathf.Clamp01(ours / (float)Mathf.Max(1, max)) * 100f);
            _theirsFill.style.width = Length.Percent(Mathf.Clamp01(theirs / (float)Mathf.Max(1, max)) * 100f);

            while (_points.Count < points.Count)
            {
                var chip = new PointChip();
                _chips.Add(chip);
                _points.Add(chip);
            }
            for (var i = 0; i < points.Count; i++) _points[i].Set(points[i]);
        }

        private static Label Side(VisualElement parent, string side, out VisualElement fill)
        {
            var box = UiKit.Box("score-side " + side);
            var number = UiKit.Text("0", "score-number");
            var column = UiKit.Box("score-column");
            column.Add(UiKit.Text(Strings.Get("stat.tickets"), "stat-label"));
            var track = UiKit.Box("score-track");
            fill = UiKit.Box("score-fill");
            track.Add(fill);
            column.Add(track);
            if (side == "ours")
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

    /// <summary>A capture point letter inside a progress ring.</summary>
    internal sealed class PointChip : VisualElement
    {
        private readonly Label _letter;
        private PointInfo _info;

        public PointChip()
        {
            AddToClassList("point-chip");
            pickingMode = PickingMode.Ignore;
            _letter = UiKit.Text("", "point-letter");
            Add(_letter);
            generateVisualContent += Draw;
        }

        public void Set(PointInfo info)
        {
            var changed = info.Owner != _info.Owner || Mathf.Abs(info.Progress - _info.Progress) > 0.005f || info.Contested != _info.Contested;
            _info = info;
            _letter.text = Strings.Get("point." + info.Id);
            EnableInClassList("ours", info.Owner == 0);
            EnableInClassList("theirs", info.Owner == 1);
            EnableInClassList("contested", info.Contested);
            if (changed) MarkDirtyRepaint();
        }

        private void Draw(MeshGenerationContext context)
        {
            var rect = contentRect;
            var centre = rect.center;
            var radius = Mathf.Min(rect.width, rect.height) * 0.5f - 2f;
            var p = context.painter2D;
            p.lineWidth = 3f;
            p.strokeColor = new Color(1f, 1f, 1f, 0.12f);
            p.BeginPath();
            p.Arc(centre, radius, 0f, 360f);
            p.Stroke();

            var amount = Mathf.Abs(_info.Progress);
            if (amount < 0.01f) return;
            p.strokeColor = _info.Progress > 0f ? UiKit.Mint : UiKit.Danger;
            p.lineCap = LineCap.Round;
            p.BeginPath();
            p.Arc(centre, radius, -90f, -90f + 360f * amount);
            p.Stroke();
        }
    }
}

using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>The campaign's portraits (Resources/UI/Portraits, drawn by Tools/campaign/portraits.py).</summary>
    internal static class Portraits
    {
        private static readonly Dictionary<string, Texture2D> Cache = new();

        public static Texture2D Get(string id)
        {
            if (string.IsNullOrEmpty(id)) id = "hq";
            if (Cache.TryGetValue(id, out var texture) && texture != null) return texture;
            texture = Resources.Load<Texture2D>("UI/Portraits/" + id) ?? Resources.Load<Texture2D>("UI/Portraits/hq");
            Cache[id] = texture;
            return texture;
        }

        /// <summary>A square portrait element (its size is the stylesheet's).</summary>
        public static VisualElement Element(string id, string classNames)
        {
            var e = UiKit.Box(classNames);
            e.style.backgroundImage = new StyleBackground(Get(id));
            return e;
        }

        public static void Set(VisualElement e, string id) => e.style.backgroundImage = new StyleBackground(Get(id));
    }

    /// <summary>
    /// In-battle radio chatter: a small portrait, the speaker and one line, one after another. A
    /// tap skips to the next; the queue never holds more than a few (old chatter is dropped).
    /// </summary>
    internal sealed class RadioPanel
    {
        private const float Seconds = 5f;
        private const int MaxQueue = 3;

        private readonly VisualElement _portrait;
        private readonly Label _name, _text;
        private readonly Queue<RadioLine> _queue = new();
        private float _until;
        private bool _showing;

        public RadioPanel()
        {
            Root = UiKit.Button("radio-panel", Skip);
            _portrait = Portraits.Element("hq", "radio-portrait");
            Root.Add(_portrait);
            var text = UiKit.Box("radio-text");
            _name = UiKit.Text("", "radio-name");
            _text = UiKit.Text("", "radio-line");
            text.Add(_name);
            text.Add(_text);
            Root.Add(text);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public void Say(RadioLine line)
        {
            while (_queue.Count >= MaxQueue) _queue.Dequeue();
            _queue.Enqueue(line);
            if (!_showing) Next();
        }

        public void Tick()
        {
            if (_showing && Time.unscaledTime >= _until) Next();
        }

        private void Skip()
        {
            if (_showing) Next();
        }

        private void Next()
        {
            if (_queue.Count == 0)
            {
                _showing = false;
                Root.style.display = DisplayStyle.None;
                return;
            }
            var line = _queue.Dequeue();
            Portraits.Set(_portrait, line.Speaker);
            _name.text = Strings.Get("char." + line.Speaker + ".name").ToUpperInvariant();
            _text.text = Strings.Get(line.Key);
            Root.EnableInClassList("enemy", line.Enemy);
            Root.style.display = DisplayStyle.Flex;
            _showing = true;
            _until = Time.unscaledTime + Mathf.Max(Seconds, 1.5f + _text.text.Length * 0.045f);
        }
    }

    /// <summary>
    /// A story card over a page: a kicker, a title, portraits, a few sentences and one or two
    /// actions. The chapter openings, the mission briefings and the epilogue use it.
    /// </summary>
    internal sealed class StoryCard
    {
        private readonly Label _kicker, _title, _speaker, _role, _body, _aside;
        private readonly VisualElement _portrait, _general, _asideBox, _buttons, _chips;
        private Action _primary, _secondary;

        public StoryCard()
        {
            Root = UiKit.Box("story-scrim", PickingMode.Position);
            var card = UiKit.Box("story-card");
            var head = UiKit.Box("story-head");
            _kicker = UiKit.Text("", "story-kicker");
            _title = UiKit.Text("", "story-title");
            head.Add(_kicker);
            head.Add(_title);
            card.Add(head);
            var main = UiKit.Box("story-main");
            _portrait = Portraits.Element("khai", "story-portrait");
            main.Add(_portrait);
            var column = UiKit.Box("story-column");
            _speaker = UiKit.Text("", "story-speaker");
            _role = UiKit.Text("", "story-role");
            _body = UiKit.Text("", "story-body");
            column.Add(_speaker);
            column.Add(_role);
            column.Add(_body);
            _chips = UiKit.Box("story-chips");
            column.Add(_chips);
            main.Add(column);
            card.Add(main);
            _asideBox = UiKit.Box("story-aside");
            _general = Portraits.Element("varga", "story-aside-portrait");
            _asideBox.Add(_general);
            _aside = UiKit.Text("", "story-aside-text");
            _asideBox.Add(_aside);
            card.Add(_asideBox);
            _buttons = UiKit.Box("story-buttons");
            card.Add(_buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <param name="speaker">A portrait id, or null for none.</param>
        /// <param name="aside">An enemy general and a line of theirs under the card, or null.</param>
        public void Show(string kicker, string title, string speaker, string body, IReadOnlyList<string> chips,
            (string general, string line)? aside, (string label, Action act) primary, (string label, Action act)? secondary)
        {
            _kicker.text = kicker.ToUpperInvariant();
            _title.text = title;
            _portrait.style.display = speaker != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (speaker != null) Portraits.Set(_portrait, speaker);
            _speaker.text = speaker != null ? Strings.Get("char." + speaker + ".name").ToUpperInvariant() : "";
            _role.text = speaker != null ? Strings.Get("char." + speaker + ".role") : "";
            _speaker.style.display = _role.style.display = speaker != null ? DisplayStyle.Flex : DisplayStyle.None;
            _body.text = body;
            _chips.Clear();
            if (chips != null)
                foreach (var chip in chips) _chips.Add(UiKit.Text(chip, "story-chip"));
            _asideBox.style.display = aside != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (aside is { } a)
            {
                Portraits.Set(_general, a.general);
                _aside.text = Strings.Get("char." + a.general + ".name").ToUpperInvariant() + ": " + a.line;
            }
            _primary = primary.act;
            _secondary = secondary?.act;
            _buttons.Clear();
            if (secondary is { } back) _buttons.Add(UiKit.WideButton("wide story-back", "retreat", back.label, null, () => Close(_secondary)));
            _buttons.Add(UiKit.WideButton("wide primary story-go", "play", primary.label, null, () => Close(_primary)));
            UiKit.Uppercase(_buttons);
            Root.style.display = DisplayStyle.Flex;
            Root.BringToFront();
        }

        public void Hide() => Root.style.display = DisplayStyle.None;

        private void Close(Action then)
        {
            Hide();
            then?.Invoke();
        }
    }
}

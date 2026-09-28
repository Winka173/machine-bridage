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
            // The battle's one toast style (Field Command 2.0, G): radio chatter, air-raid warnings and elite notices.
            Root = Kit.Tappable(KitPanel.SurfaceClass + " fc-surface--field fc-radio", Skip);
            _portrait = Portraits.Element("hq", "fc-radio__portrait");
            Root.Add(_portrait);
            var text = Kit.Box("fc-radio__text");
            _name = Kit.Text("", "fc-caption fc-radio__name");
            _text = Kit.Text("", "fc-body fc-row-text");
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
            _name.text = Kit.Caps(Strings.Get("char." + line.Speaker + ".name"));
            _text.text = Strings.Get(line.Key);
            Root.EnableInClassList("fc-radio--enemy", line.Enemy);
            Root.style.display = DisplayStyle.Flex;
            _showing = true;
            _until = Time.unscaledTime + Mathf.Max(Seconds, 1.5f + _text.text.Length * 0.045f);
        }
    }

    /// <summary>
    /// A story card over a page (the kit's dialog surface on a scrim): a kicker, a title, the
    /// battlefield's picture, the speaker's portrait and a few sentences, tags, an enemy general's
    /// line, and one or two actions (Back, then the one main button). The chapter openings, the
    /// mission briefings and the epilogue use it.
    /// </summary>
    internal sealed class StoryCard
    {
        private readonly Label _kicker, _title, _speaker, _role, _body, _aside;
        private readonly VisualElement _art, _portrait, _general, _asideBox, _buttons, _chips, _who;
        private Action _primary, _secondary;

        public StoryCard(VisualElement host = null)
        {
            Root = Kit.Box(KitDialog.ScrimClass + " fc-story-scrim", PickingMode.Position);
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-story", PickingMode.Position);
            _art = Kit.Box("fc-story__art");
            card.Add(_art);
            // The text scrolls when it is long or the type is large; the buttons stay under it.
            var column = Kit.Box("fc-story__column");
            var scroll = Kit.Scroll(ScrollViewMode.Vertical, "fc-story__scroll");
            var main = Kit.Box("fc-story__main");
            scroll.Add(main);
            column.Add(scroll);
            _kicker = Kit.Caption("");
            main.Add(_kicker);
            _title = Kit.Text("", "fc-title");
            main.Add(_title);
            _who = Kit.Box("fc-story__who");
            _portrait = Portraits.Element("khai", "fc-portrait");
            _who.Add(_portrait);
            var names = Kit.Box("fc-row-text");
            _speaker = Kit.Text("", "fc-panel-title");
            _role = Kit.Small("");
            names.Add(_speaker);
            names.Add(_role);
            _who.Add(names);
            main.Add(_who);
            _body = Kit.Body("");
            main.Add(_body);
            _chips = Kit.Box("fc-row fc-row--wrap fc-mt-3");
            main.Add(_chips);
            _asideBox = Kit.Box("fc-story__aside");
            _general = Portraits.Element("varga", "fc-portrait fc-portrait--small");
            _asideBox.Add(_general);
            _aside = Kit.Text("", "fc-body-2 fc-row-text");
            _asideBox.Add(_aside);
            main.Add(_asideBox);
            _buttons = Kit.Box("fc-dialog__buttons fc-story__buttons");
            column.Add(_buttons);
            card.Add(column);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <param name="speaker">A portrait id, or null for none.</param>
        /// <param name="aside">An enemy general and a line of theirs under the card, or null.</param>
        /// <param name="map">The battlefield whose picture heads the card, or null.</param>
        public void Show(string kicker, string title, string speaker, string body, IReadOnlyList<string> chips,
            (string general, string line)? aside, (string label, Action act) primary, (string label, Action act)? secondary, string map = null)
        {
            _kicker.text = Kit.Caps(kicker);
            _title.text = Kit.Caps(title);
            var picture = map != null ? MapArt.For(map) : null;
            _art.style.display = picture != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (picture != null) _art.style.backgroundImage = Background.FromTexture2D(picture);
            _who.style.display = speaker != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (speaker != null)
            {
                Portraits.Set(_portrait, speaker);
                _speaker.text = Kit.Caps(Strings.Get("char." + speaker + ".name"));
                _role.text = Strings.Get("char." + speaker + ".role");
            }
            _body.text = body;
            _chips.Clear();
            if (chips != null)
                foreach (var chip in chips)
                {
                    var tag = Kit.Box("fc-tag");
                    tag.Add(Kit.Text(chip, "fc-small"));
                    _chips.Add(tag);
                }
            _asideBox.style.display = aside != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (aside is { } a)
            {
                Portraits.Set(_general, a.general);
                _aside.text = Strings.Get("char." + a.general + ".name") + ": " + a.line;
            }
            _primary = primary.act;
            _secondary = secondary?.act;
            _buttons.Clear();
            if (secondary is { } back) _buttons.Add(new KitButton(ButtonTier.Secondary, back.label, () => Close(_secondary), "retreat"));
            _buttons.Add(new KitButton(ButtonTier.Primary, primary.label, () => Close(_primary), "play"));
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

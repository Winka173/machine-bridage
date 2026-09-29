using System;
using System.Collections.Generic;
using MachineBrigade.Game.Match;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 D.8: the still panels at the end of a chapter or interlude, a comic's page: three or four frames side by
    /// side, each a battlefield's picture with a render in it, the speaker's portrait and a speech box. Next shows them one
    /// after another; Skip closes the page at once; the dossier's timeline plays them again. The pictures are the renders
    /// and battlefield shots the game has, in a comic frame: placeholders until drawn panels come (Docs/ASSET_DEBT.md).
    /// </summary>
    internal sealed class ComicPage
    {
        private readonly VisualElement _host, _panels, _buttons;
        private readonly Label _kicker, _title;
        private readonly List<VisualElement> _frames = new();
        private KitButton _next;
        private int _shown;
        private Action _then;

        public ComicPage(VisualElement host)
        {
            _host = host;
            Root = Kit.Box(KitDialog.ScrimClass + " fc-comic-scrim", PickingMode.Position);
            var card = Kit.Box(KitPanel.SurfaceClass + " fc-comic", PickingMode.Position);
            var head = Kit.Box("fc-comic__head");
            _kicker = Kit.Caption("");
            head.Add(_kicker);
            _title = Kit.Text("", "fc-title");
            head.Add(_title);
            card.Add(head);
            _panels = Kit.Box("fc-comic__panels");
            card.Add(_panels);
            _buttons = Kit.Box("fc-dialog__buttons fc-comic__buttons");
            card.Add(_buttons);
            Root.Add(card);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        public bool Visible => Root.style.display == DisplayStyle.Flex;

        /// <summary>How many panels are showing (the checks read it).</summary>
        public int Shown => _shown;

        /// <summary>Shows a chapter's panels (the first one; Next shows the rest); <paramref name="then"/> runs when the page closes.</summary>
        public bool Show(int chapter, Action then)
        {
            var panels = Narrative.ComicOf(chapter);
            if (panels.Count == 0) return false;
            _then = then;
            _kicker.text = Kit.Caps(Strings.Format("comic.kicker", ("chapter", Campaign.ChapterName(chapter))));
            _title.text = Kit.Caps(Strings.Get($"chapter.{chapter}.title"));
            _panels.Clear();
            _frames.Clear();
            foreach (var panel in panels)
            {
                var frame = Frame(panel);
                _frames.Add(frame);
                _panels.Add(frame);
            }
            _shown = 0;
            _buttons.Clear();
            _buttons.Add(new KitButton(ButtonTier.Secondary, Strings.Get("comic.skip"), Close, "close"));
            _next = new KitButton(ButtonTier.Primary, Strings.Get("comic.next"), Next, "play");
            _buttons.Add(_next);
            Reveal();
            if (Root.parent == null) _host?.Add(Root);
            Root.style.display = DisplayStyle.Flex;
            Root.BringToFront();
            return true;
        }

        /// <summary>The next panel, or the page closes after the last.</summary>
        public void Next()
        {
            if (_shown >= _frames.Count) Close();
            else Reveal();
        }

        private void Reveal()
        {
            _shown++;
            for (var i = 0; i < _frames.Count; i++) _frames[i].EnableInClassList("fc-comic__panel--waiting", i >= _shown);
            _next.Label = Strings.Get(_shown >= _frames.Count ? "comic.done" : "comic.next");
        }

        public void Close()
        {
            Root.style.display = DisplayStyle.None;
            var then = _then;
            _then = null;
            then?.Invoke();
        }

        private static VisualElement Frame(ComicPanel panel)
        {
            var frame = Kit.Box("fc-comic__panel");
            var art = Kit.Box("fc-comic__art");
            foreach (var map in panel.Art.Split('|'))
                if (MapArt.For(map) is { } picture)
                {
                    art.style.backgroundImage = Background.FromTexture2D(picture);
                    break;
                }
            if (panel.Render != null && Resources.Load<Texture2D>(CardArt.Folder + panel.Render) is { } render)
            {
                var figure = Kit.Box("fc-comic__render");
                figure.style.backgroundImage = Background.FromTexture2D(render);
                art.Add(figure);
            }
            art.Add(Portraits.Element(panel.Speaker, "fc-portrait fc-portrait--small fc-comic__portrait"));
            frame.Add(art);
            var bubble = Kit.Box("fc-comic__bubble");
            bubble.Add(Kit.Caption(ShortName(panel.Speaker)));
            bubble.Add(Kit.Text(Strings.Get(panel.Key), "fc-body"));
            frame.Add(bubble);
            return frame;
        }

        /// <summary>A speaker's name as a speech box heads it: the name the story calls them by (NameText), else the last word of it.</summary>
        private static string ShortName(string speaker)
        {
            if (Strings.Has("name." + speaker)) return Strings.Get("name." + speaker);
            var name = Strings.Get($"char.{speaker}.name");
            var space = name.LastIndexOf(' ');
            return space > 0 ? name.Substring(space + 1) : name;
        }
    }
}

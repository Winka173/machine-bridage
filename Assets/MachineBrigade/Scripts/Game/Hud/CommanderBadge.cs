using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 22 F.4: the commander's small face in the HUD's corner, beside pause (the compact HUD's 44 px face in a
    /// full touch target). A tap opens a small card under the corner with the call sign, the strength and the weakness;
    /// a second tap, a tap on the card or eight seconds close it.
    /// </summary>
    internal sealed class CommanderBadge
    {
        private const float OpenSeconds = 8f;
        private float _until;

        public CommanderBadge(CommanderDef commander)
        {
            var sheet = Resources.Load<StyleSheet>("UI/Commanders");
            var name = CommanderText.Name(commander);
            Face = Kit.Tappable("fc-cmdr-badge", Toggle);
            if (sheet != null) Face.styleSheets.Add(sheet);
            Face.tooltip = Strings.Format("cmdr.hud", ("name", name));
            var face = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-cmdr-badge__face");
            face.Add(Portraits.Element(commander.Portrait, "fc-cmdr-badge__portrait"));
            Face.Add(face);

            Card = Kit.Tappable(KitPanel.SurfaceClass + " fc-surface--field fc-cmdr-card", Close);
            if (sheet != null) Card.styleSheets.Add(sheet);
            Card.Add(Kit.Text(Kit.Caps(name), "fc-caption"));
            Card.Add(Kit.Text(CommanderText.Call(commander), "fc-small fc-cmdr-card__call"));
            Card.Add(Line("cmdr.strength", CommanderText.Strength(commander), "fc-cmdr-card__good"));
            Card.Add(Line("cmdr.weakness", CommanderText.Weakness(commander), "fc-cmdr-card__bad"));
            Card.style.display = DisplayStyle.None;
        }

        /// <summary>The face in the corner.</summary>
        public VisualElement Face { get; }

        /// <summary>The card it opens (the HUD places it under the corner).</summary>
        public VisualElement Card { get; }

        public bool Open => Card.style.display == DisplayStyle.Flex;

        private static VisualElement Line(string label, string text, string modifier)
        {
            var row = Kit.Box("fc-cmdr-card__line " + modifier);
            row.Add(Kit.Text(Strings.Format("cmdr.line", ("label", Strings.Get(label)), ("text", text)), "fc-small fc-row-text"));
            return row;
        }

        public void Toggle()
        {
            if (Open) Close();
            else Show();
        }

        public void Show()
        {
            Card.style.display = DisplayStyle.Flex;
            Card.BringToFront();
            _until = Time.unscaledTime + OpenSeconds;
        }

        public void Close() => Card.style.display = DisplayStyle.None;

        public void Tick()
        {
            if (Open && Time.unscaledTime >= _until) Close();
        }
    }
}

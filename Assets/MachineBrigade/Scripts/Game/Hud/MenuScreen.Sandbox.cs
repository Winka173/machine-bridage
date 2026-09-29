using MachineBrigade.Game.Match;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 21 A.3: the Sandbox's way in, with the challenges on the Operations tab. The player version shows
    /// locked, with what opens it, until the last chapter switched on is finished; the internal build is open from
    /// the start. Its page says that nothing in it pays out.
    /// </summary>
    internal sealed partial class MenuScreen
    {
        private VisualElement SandboxCard()
        {
            var line = SandboxSession.Open ? Strings.Get("sandbox.sub") : SandboxText.Format("sandbox.locked", ("chapter", Campaign.LastChapter));
            var card = OpsCard(OpsEntry.Sandbox, null, Strings.Get("sandbox.title"), line, false);
            if (!SandboxSession.Open) card.AddToClassList("fc-ops__card--locked");
            return card;
        }

        private VisualElement SandboxDetail(VisualElement body)
        {
            body.Add(Kit.Caption(Strings.Get("sandbox.title")));
            body.Add(Kit.Text(Strings.Get("sandbox.sub"), "fc-body-2 fc-mb-3"));
            body.Add(Rule("tank", Strings.Get(SandboxSession.Internal ? "sandbox.internal" : "sandbox.player")));
            body.Add(Rule("coin", Strings.Get("sandbox.noRewards")));
            if (!SandboxSession.Open)
            {
                body.Add(Rule("lock", SandboxText.Format("sandbox.locked", ("chapter", Campaign.LastChapter))));
                return null;
            }
            return PlayButton(Match.GameModeKind.Sandbox);
        }

        /// <summary>G.3: the Sandbox's section at the end of the Guide (the combat legend).</summary>
        private void SandboxGuide(VisualElement body)
        {
            var section = Section(body, "sandbox.guide.title");
            section.Add(Kit.Text(Strings.Get("sandbox.guide.body"), "fc-body-2 fc-mb-2"));
        }
    }
}

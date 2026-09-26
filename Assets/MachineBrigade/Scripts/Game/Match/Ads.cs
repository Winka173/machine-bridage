using System;

namespace MachineBrigade.Game.Match
{
    /// <summary>A rewarded video ad network (AdMob, LevelPlay...), or the stand-in below.</summary>
    public interface IRewardedAds
    {
        bool Ready { get; }

        /// <summary>Shows an ad; <paramref name="done"/> gets true only when it was watched to the end.</summary>
        void Show(Action<bool> done);
    }

    /// <summary>
    /// Where the game gets its rewarded ads. Until a real network is wired in (it needs the
    /// publisher's account and app id), a stand-in shows a five-second placeholder screen, so
    /// the whole "double your coins" flow can be played and tested.
    /// </summary>
    public static class Ads
    {
        public static IRewardedAds Rewarded { get; set; } = new PlaceholderAds();
    }

    /// <summary>Stand-in ad: the HUD draws a short countdown screen (see <see cref="Presenter"/>).</summary>
    public sealed class PlaceholderAds : IRewardedAds
    {
        /// <summary>Set by the match: shows the placeholder screen and reports whether it ran to the end.</summary>
        public static Action<Action<bool>> Presenter { get; set; }

        public bool Ready => Presenter != null;

        public void Show(Action<bool> done)
        {
            if (Presenter == null)
            {
                done?.Invoke(false);
                return;
            }
            Presenter(done);
        }
    }
}

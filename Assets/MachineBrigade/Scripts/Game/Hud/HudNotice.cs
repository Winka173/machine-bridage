namespace MachineBrigade.Game.Hud
{
    /// <summary>Prompt 23 F.1: what a notice at the top edge is about; it picks the notice's icon.</summary>
    public enum NoticeKind
    {
        Info,
        Captured,
        Lost,
        AirRaid,
        Air,
        Strike,
        Reinforce,

        /// <summary>Prompt 23 F.4: the Meridian Accord's reinforcements (their sign).</summary>
        Accord,
        Landing,
        Boss,
        Elite,
        Part,
        Weather,
        Crate,
        Objective,
        Area,
        Wave,
        Reward,
        Order,
        Done,
    }

    /// <summary>
    /// Prompt 23 F.1: a notice at the top edge (prompt 11's compact HUD): an icon by kind and one line that hides itself;
    /// several queue. <see cref="Direction"/> is where it comes from on the map (a unit vector in the battle's ground
    /// plane, x east and y north), for the edge and minimap arrows of F.2; null when it has none.
    /// </summary>
    public readonly struct HudNotice
    {
        public HudNotice(NoticeKind kind, string text, bool alert = false, float seconds = 3f, System.Numerics.Vector2? direction = null)
        {
            Kind = kind;
            Text = text;
            Alert = alert;
            Seconds = seconds;
            Direction = direction;
        }

        public NoticeKind Kind { get; }
        public string Text { get; }

        /// <summary>Bad news for the player: the notice's bar and icon are red, and it does not wait its turn.</summary>
        public bool Alert { get; }

        public float Seconds { get; }
        public System.Numerics.Vector2? Direction { get; }

        /// <summary>The icon for a kind of notice.</summary>
        public static string Icon(NoticeKind kind) => kind switch
        {
            NoticeKind.Captured or NoticeKind.Lost or NoticeKind.Objective => "flag",
            NoticeKind.AirRaid => "airstrike",
            NoticeKind.Air => "jet",
            NoticeKind.Strike => "barrage",
            NoticeKind.Reinforce => "reinforce",
            NoticeKind.Accord => "accord",
            NoticeKind.Landing => "anchor",
            NoticeKind.Boss => "skull",
            NoticeKind.Elite => "elite",
            NoticeKind.Part => "crosshair",
            NoticeKind.Weather => "cloud",
            NoticeKind.Crate => "crate",
            NoticeKind.Area => "expand",
            NoticeKind.Wave => "people",
            NoticeKind.Reward => "coin",
            NoticeKind.Order => "command",
            NoticeKind.Done => "check",
            _ => "info",
        };
    }
}

#nullable enable

namespace MachineBrigade.Sim.AI
{
    /// <summary>
    /// Prompt 28 E.1: a tower's targeting mode. The seven of the prompt, and the sheet "Công trình"'s special ones
    /// (C-RAM's rounds, Patriot's largest aircraft and missiles). Default: the data's mode for the tower.
    /// </summary>
    public enum TowerMode
    {
        Default,
        Nearest,
        Strongest,
        Weakest,
        Lead,
        AirFirst,
        Cluster,
        ArtilleryFirst,
        ShieldKey,
        NearestRound,
        BiggestAircraft,
        MissilesFirst,
        None,
    }

    /// <summary>Prompt 28 F.1: the boss behaviour types of the sheet "Kiểu hành vi boss".</summary>
    public enum BossBehaviour
    {
        AntiBlob,
        AntiAir,
        AntiArtillery,
        CoreProtection,
        FlankPunishment,
        AreaDenial,
    }
}

#nullable enable
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER P5 Part N: what a tower is for, from its weapon and role (a tower can be more than one).</summary>
    [System.Flags]
    public enum TowerKind : byte
    {
        None = 0,
        AntiAir = 1,
        AntiTank = 2,
        /// <summary>Indirect fire or a drone hangar: reaches enemy artillery and support.</summary>
        FireSupport = 4,
        /// <summary>Point defence / shield: intercepts rounds (its targeting is the interception system's, kept).</summary>
        Defence = 8,
    }

    /// <summary>One candidate's picture for a tower (built by CombatSystem.P5 from observed state only; the tests build it by hand).</summary>
    public readonly struct TowerTargetFacts
    {
        public TowerTargetFacts(bool flying, bool threatensProtectedZone, bool heavyArmour, bool artilleryOrSupport, bool criticalObjectiveThreat,
            float otherTowersDamage, float targetHp, bool alreadyMine)
        {
            Flying = flying;
            ThreatensProtectedZone = threatensProtectedZone;
            HeavyArmour = heavyArmour;
            ArtilleryOrSupport = artilleryOrSupport;
            CriticalObjectiveThreat = criticalObjectiveThreat;
            OtherTowersDamage = otherTowersDamage;
            TargetHp = targetHp;
            AlreadyMine = alreadyMine;
        }

        public bool Flying { get; }

        /// <summary>An aircraft over / attacking the protected zone (the HQ, a friendly structure it shoots at).</summary>
        public bool ThreatensProtectedZone { get; }
        public bool HeavyArmour { get; }
        public bool ArtilleryOrSupport { get; }

        /// <summary>Within <c>criticalRadius</c> of the HQ or shooting at it.</summary>
        public bool CriticalObjectiveThreat { get; }

        /// <summary>The damage of one cycle of every other friendly tower already on this target.</summary>
        public float OtherTowersDamage { get; }
        public float TargetHp { get; }

        /// <summary>This tower already has it (it finishes what it started: no overkill switch).</summary>
        public bool AlreadyMine { get; }
    }

    /// <summary>
    /// AI MASTER P5 Part N: tower coordination. The tower modes (prompt 28 E, <see cref="TowerMode"/>) stay the base score; these
    /// factors go on top: SAM / AA towers first on aircraft threatening the protected zone, AT towers on heavy armour,
    /// artillery-capable towers and drone hangars on enemy artillery and support, a critical objective threat over any mode,
    /// and no overkill when several towers would shoot one weak unit (the P3 planned-damage board covers AI sides' towers too;
    /// this rule also counts towers that are not on the board's side). Static towers never path. Pure (the tests call it).
    /// </summary>
    public static class TowerCoordination
    {
        public static float Worth(TowerKind kind, in TowerTargetFacts f)
        {
            if (!Tun.Towers.Enabled) return 1f;
            var worth = 1f;
            if ((kind & TowerKind.AntiAir) != 0 && f.Flying && f.ThreatensProtectedZone) worth *= Tun.Towers.AirThreatWorth;
            if ((kind & TowerKind.AntiTank) != 0 && f.HeavyArmour) worth *= Tun.Towers.HeavyWorth;
            if ((kind & TowerKind.FireSupport) != 0 && f.ArtilleryOrSupport) worth *= Tun.Towers.ArtilleryWorth;
            if (f.CriticalObjectiveThreat) worth *= Tun.Towers.CriticalWorth;
            if (Overkill(f)) worth *= Tun.Towers.OverkillFloor;
            return worth;
        }

        /// <summary>Other towers' committed damage already kills it (x <c>overkillShare</c>) and this tower is not on it yet.</summary>
        public static bool Overkill(in TowerTargetFacts f) =>
            !f.AlreadyMine && !f.CriticalObjectiveThreat && f.TargetHp > 0f && f.OtherTowersDamage >= f.TargetHp * Tun.Towers.OverkillShare;
    }
}

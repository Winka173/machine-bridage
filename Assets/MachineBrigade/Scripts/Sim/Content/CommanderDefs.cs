#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Which of a side's units a commander's stat line reaches (prompt 22 F). Bosses and HQs are never reached.</summary>
    public enum CommanderReach
    {
        /// <summary>Every unit the side fields: vehicles, aircraft, ships and towers.</summary>
        Army,
        /// <summary>Everything that moves: ground vehicles, aircraft and ships.</summary>
        Vehicles,
        /// <summary>Ground vehicles (not aircraft, not towers).</summary>
        Ground,
        /// <summary>Planes and helicopters (not drones).</summary>
        Aircraft,
        /// <summary>Drones and launchers whose main round is a drone (FPV, Lancet, the swarm).</summary>
        Drones,
        /// <summary>Drone units only (a UAV, a strike drone, a carrier's and a hangar's drones).</summary>
        DroneUnits,
        Tanks,
        /// <summary>Tanks and heavy vehicles.</summary>
        Armour,
        Heavy,
        /// <summary>Scouts and light vehicles.</summary>
        Light,
        /// <summary>Ground guns that lob over cover (the Artillery branch).</summary>
        Artillery,
        /// <summary>Ground vehicles that fire straight (not the Artillery branch, not a lobbed or drone main round).</summary>
        DirectFire,
        /// <summary>Fixed towers: a base's, a point's, a field tower.</summary>
        Towers,
        Ships,
        /// <summary>Vehicles of <see cref="CommanderRules.CheapAt"/> CP or less.</summary>
        Cheap,
        /// <summary>Vehicles of <see cref="CommanderRules.DearAt"/> CP or more.</summary>
        Dear,
        /// <summary>Units whose main gun does energy damage.</summary>
        Energy,
        /// <summary>Units that carry a shield: a dome, wards or a shield skill.</summary>
        Shielded,
    }

    /// <summary>Which cards a commander's price change reaches.</summary>
    public enum PriceReach
    {
        /// <summary>Every vehicle card (reinforcements).</summary>
        Vehicles,
        /// <summary>Vehicle cards of <see cref="CommanderRules.CheapAt"/> CP or less.</summary>
        Cheap,
        /// <summary>Engineers (a repair aura).</summary>
        Engineers,
        /// <summary>Towers dropped by parachute (a support of the Tower kind: the field tower).</summary>
        AirdropTowers,
    }

    /// <summary>The kind of deck a commander suits, shown on the picker and measured by the balance sweep (F.6).</summary>
    public enum DeckStyle
    {
        Balanced,
        Sustain,
        Air,
        Recon,
        Drones,
        Blitz,
        Fortress,
        Artillery,
        LongGame,
        Points,
        Swarm,
        Heavy,
        Attrition,
        Hoard,
    }

    public enum CommanderFamily
    {
        Combat,
        Economy,
        General,
    }

    /// <summary>One stat line: a strength when positive, a weakness when negative (fractions: 0.05 is 5 %).</summary>
    public readonly struct CommanderLine
    {
        public CommanderLine(StatId stat, float value, CommanderReach reach)
        {
            Stat = stat;
            Value = value;
            Reach = reach;
        }

        public StatId Stat { get; }
        public float Value { get; }
        public CommanderReach Reach { get; }
    }

    /// <summary>A price change: the cards of <see cref="Reach"/> cost <see cref="Scale"/> times their CP.</summary>
    public readonly struct CommanderPrice
    {
        public CommanderPrice(PriceReach reach, float scale)
        {
            Reach = reach;
            Scale = scale;
        }

        public PriceReach Reach { get; }
        public float Scale { get; }
    }

    /// <summary>
    /// Prompt 22 F: a commander (or an enemy general playing by the same rules). One passive strength and one small
    /// weakness, always on for the whole battle: no active skill, no gauge, no levels. The unit lines go through the
    /// loadout's stat caps like equipment (<see cref="CommanderRules.Merge"/>); the side-wide numbers work in the
    /// economy, the abilities, sight and damage. Every number is neutral by default. The Game layer names each one
    /// ("cmdr.&lt;id&gt;.*").
    /// </summary>
    public sealed class CommanderDef
    {
        public string Id { get; internal set; } = "";

        public CommanderFamily Family { get; internal set; }

        /// <summary>The portrait (UI/Portraits/&lt;id&gt;; a missing one is the HQ's placeholder).</summary>
        public string Portrait { get; internal set; } = "hq";

        /// <summary>
        /// Where it opens: a chapter id the story places ("c4": on reaching chapter 4, "c5+": once chapter 5 is done,
        /// "i1": the first interlude). Generals have none.
        /// </summary>
        public string Unlock { get; internal set; } = "c1";

        /// <summary>The kind of deck it suits (the picker's suggestion).</summary>
        public DeckStyle Style { get; internal set; }

        /// <summary>For a general: the campaign's general id (campaign.json "general"); null for the player's commanders.</summary>
        public string? General { get; internal set; }

        public IReadOnlyList<CommanderLine> Lines { get; internal set; } = Array.Empty<CommanderLine>();

        public IReadOnlyList<CommanderPrice> Prices { get; internal set; } = Array.Empty<CommanderPrice>();

        // ---------------------------------------------------------------- side-wide numbers (1 or 0: none)

        /// <summary>CP income multiplier (all of it: the base rate, points and relays).</summary>
        public float Income { get; internal set; } = 1f;

        /// <summary>Multiplier on what held points pay.</summary>
        public float PointIncome { get; internal set; } = 1f;

        /// <summary>Income multiplier in a battle without capture points.</summary>
        public float NoPointsIncome { get; internal set; } = 1f;

        /// <summary>Income multiplier while the side holds <see cref="RichAt"/> CP or more.</summary>
        public float RichIncome { get; internal set; } = 1f;

        public float RichAt { get; internal set; } = 20f;

        /// <summary>Income multiplier for the first <see cref="EarlySeconds"/> of the battle.</summary>
        public float EarlyIncome { get; internal set; } = 1f;

        public float EarlySeconds { get; internal set; } = 90f;

        /// <summary>CP added to the bank cap (30 to 45: 15).</summary>
        public float BankBonus { get; internal set; }

        /// <summary>Supply (the army value kept up before upkeep) multiplier.</summary>
        public float Supply { get; internal set; } = 1f;

        /// <summary>Extra aircraft the side may have up.</summary>
        public int AirCap { get; internal set; }

        /// <summary>A kill's base refund share (0.25 by default; the 45 % cap on every refund holds).</summary>
        public float KillRefund { get; internal set; } = 0.25f;

        /// <summary>False: the side's own losses refund nothing (the Quartermaster set's 10 %).</summary>
        public bool LossRefund { get; internal set; } = true;

        /// <summary>A parachute delivery's time multiplier (0.75: 25 % faster).</summary>
        public float Delivery { get; internal set; } = 1f;

        /// <summary>Repair rate multiplier of the side's engineers and repair bays.</summary>
        public float Repair { get; internal set; } = 1f;

        /// <summary>How fast the side's aircraft rearm (1.15: 15 % faster).</summary>
        public float AirRearm { get; internal set; } = 1f;

        /// <summary>How far the side sees stealthy and hidden enemies (1.25: 25 % farther).</summary>
        public float StealthSight { get; internal set; } = 1f;

        /// <summary>Damage an enemy takes from the side while marked or revealed to it (1.05: 5 % more).</summary>
        public float ExposedTaken { get; internal set; } = 1f;

        /// <summary>Share of the jamming the side's drones shrug off (0.3: jammed 30 % less often).</summary>
        public float JamResist { get; internal set; }

        /// <summary>Damage multiplier of the side's units under half health.</summary>
        public float LowHpDamage { get; internal set; } = 1f;

        public bool IsGeneral => Family == CommanderFamily.General;

        /// <summary>A stat line's value for a def (0: none reaches it); the lines of one stat add up.</summary>
        public float Line(StatId stat, VehicleDef def)
        {
            var sum = 0f;
            foreach (var l in Lines)
                if (l.Stat == stat && CommanderRules.Reaches(l.Reach, def)) sum += l.Value;
            return sum;
        }
    }
}

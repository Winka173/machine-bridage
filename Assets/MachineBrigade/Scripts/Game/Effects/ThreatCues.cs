using System.Collections.Generic;
using MachineBrigade.Game.Audio;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Effects
{
    /// <summary>MVA W1-B (spec part BL): the kinds of threat that carry a cue.</summary>
    internal enum ThreatType
    {
        ArtilleryIncoming,
        HeavyRoundIncoming,
        MissileIncoming,
        TopAttack,
        Bomb,
        BombStick,
        SupportStrike,
        BossSuperweapon,
        SuperheavyStrike,
        Thermobaric,
        MineDetected,
        Emp,
    }

    /// <summary>What a cancelled threat's cue does (spec part AF).</summary>
    internal enum CancelBehavior
    {
        /// <summary>The ring / mark goes the frame the round lands or is gone (diverted, shot down, its shooter dead).</summary>
        EndsWithRound,

        /// <summary>The zone fades out when the attack ends or is called off.</summary>
        FadeOut,

        /// <summary>Not cancellable once started (it lands on its clock).</summary>
        Fixed,

        /// <summary>No cue in the game yet (a W2/W3 gap, listed so it is not forgotten).</summary>
        NotImplemented,
    }

    /// <summary>One row of the cross-system threat cue table (spec parts AF, AG, AN, BL).</summary>
    internal readonly struct ThreatCue
    {
        public ThreatCue(ThreatType type, AudioClass priority, string visualTelegraph, string telegraphShape, string actualDangerShape,
            float minLeadTime, string audioCue, string haptic, CancelBehavior cancel, string impactCue, bool canBeOccludedVisually,
            string source)
        {
            Type = type;
            Priority = priority;
            VisualTelegraph = visualTelegraph;
            TelegraphShape = telegraphShape;
            ActualDangerShape = actualDangerShape;
            MinLeadTime = minLeadTime;
            AudioCue = audioCue;
            OptionalHaptic = haptic;
            Cancel = cancel;
            ImpactCue = impactCue;
            CanBeOccludedVisually = canBeOccludedVisually;
            Source = source;
        }

        public ThreatType Type { get; }
        public AudioClass Priority { get; }
        public string VisualTelegraph { get; }
        public string TelegraphShape { get; }
        public string ActualDangerShape { get; }

        /// <summary>The shortest warning before it lands, s (0: none ahead of the impact itself).</summary>
        public float MinLeadTime { get; }

        public string AudioCue { get; }
        public string OptionalHaptic { get; }
        public CancelBehavior Cancel { get; }
        public string ImpactCue { get; }

        /// <summary>Spec part AG: false = drawn above smoke, decals and debris (critical cues).</summary>
        public bool CanBeOccludedVisually { get; }

        /// <summary>Spec part BL: a P0 / P1 audio cue is never virtualised during its active warning.</summary>
        public bool CanBeVirtualizedAudio => AudioPolicy.For(Priority).CanBeVirtualized;

        /// <summary>Spec part AN: the low graphics preset never removes a danger telegraph (true for every row).</summary>
        public bool KeptOnLowPreset => true;

        /// <summary>Where the cue is drawn / played in the code.</summary>
        public string Source { get; }
    }

    /// <summary>
    /// MVA W1-B (spec parts AE, AF, AG, AN, BL; DECISIONS "Map/visual/audio W1-B (lane B)"): the canonical threat cue table,
    /// one row per threat with its telegraph, the danger it stands for, its lead, audio, cancel and impact cues, as the game
    /// draws and plays them now. Owner rule of play-test 14 (DECISIONS "Play-test 14 (lane A)"): ordinary bombs and artillery
    /// show no ground zone (<see cref="EffectsDirector.Zoneless"/>), their cue is the incoming whistle. Exported to
    /// Docs/mapvisaudio/THREAT_CUES.md by hand from this table; the tests read it.
    /// </summary>
    internal static class ThreatCues
    {
        private static readonly ThreatCue[] Table =
        {
            new(ThreatType.ArtilleryIncoming, AudioClass.P1, "none (owner rule: zoneless howitzer / mortar shells)", "-",
                "blast core + edge (WeaponDef.SplashRadius / WarnRadius)", 1.15f, "warn_whistle (P1), 1.15 s before landing", "-",
                CancelBehavior.Fixed, "blast by tier (TierFx T0-T5)", false, "AudioDirector.Whistle, EffectsDirector.Zoneless"),
            new(ThreatType.HeavyRoundIncoming, AudioClass.P1, "escape ring pair (edge + core), fades in", "circle = blast edge, inner = core",
                "circle = blast edge, inner = core", 2.5f, "warn_whistle (P1); 406 mm+: warn_whistle_big (P0)", "-",
                CancelBehavior.EndsWithRound, "blast by tier", false, "EscapeWarnings (WarningKind.Round), warningRules.floorT4"),
            new(ThreatType.MissileIncoming, AudioClass.P1, "the missile and its motor plume (never culled on Low)", "projectile path",
                "warhead splash at the target", 0.4f, "missile_hiss at the target (P1 when aimed at the player's unit)", "-",
                CancelBehavior.EndsWithRound, "shaped-charge / HE impact", false, "WeaponEffects (missile), AudioDirector.Incoming"),
            new(ThreatType.TopAttack, AudioClass.P1, "climb-then-dive flight + a contracting dive ring on the target (top attack only)",
                "ring closing on the target over the dive", "the target itself (overhead hit)", 0.9f,
                "missile_hiss (P1) at the target", "-", CancelBehavior.EndsWithRound, "overhead shaped-charge impact", false,
                "TopAttackMarks, WeaponDef.Flight = Loft"),
            new(ThreatType.Bomb, AudioClass.P1, "none (owner rule: zoneless bombs); 400 kg+: escape ring", "circle = blast edge (400 kg+)",
                "blast core + edge", 1.15f, "warn_whistle (P1); a boss's / 406 mm-class: warn_whistle_big (P0)", "-",
                CancelBehavior.Fixed, "HE blast by tier", false, "EscapeWarnings, AudioDirector.Whistle"),
            new(ThreatType.BombStick, AudioClass.P1, "STICK_RECT rectangle along the run", "rectangle = the stick's footprint",
                "every bomb's blast along the run", 1.15f, "warn_whistle per stick (P1)", "-", CancelBehavior.EndsWithRound,
                "a chain of HE blasts", false, "EffectsDirector.StickFired, AudioDirector.StickWhistle"),
            new(ThreatType.SupportStrike, AudioClass.P1, "strike zone (airstrike line, barrage / cruise-missile circle)",
                "zone = the support's radius / line", "the support's blast radius inside it", 1.15f,
                "warn_whistle (P1), a second halfway through a long barrage", "-", CancelBehavior.FadeOut, "the support's blasts",
                false, "StrikeEffects (WarningKind.Support), AudioDirector StrikeWarning"),
            new(ThreatType.BossSuperweapon, AudioClass.P0, "big-attack zone, always shown, drawn on top (WarningKind.Super)",
                "zone = the attack's area", "the attack's area", 2.5f, "its own super cue alarm (P0, CriticalWarnings bus) + big whistle",
                "-", CancelBehavior.FadeOut, "T4-T5 blast", false, "BigAttackZones, AudioDirector.SuperCues"),
            new(ThreatType.SuperheavyStrike, AudioClass.P0, "escape ring pair as a super weapon (always shown, on top)",
                "circle = blast edge, inner = core", "circle = blast edge, inner = core", 4f, "warn_whistle_big (P0)", "-",
                CancelBehavior.EndsWithRound, "T5 blast", false, "EscapeWarnings (super), warningRules.floorT5"),
            new(ThreatType.Thermobaric, AudioClass.P1, "as its carrier round (escape ring from T4)", "circle = blast edge",
                "pressure blast (larger edge)", 2.5f, "whistle / hiss as its carrier; blast_thermo bank on impact (P2)", "-",
                CancelBehavior.EndsWithRound, "thermobaric blast (own bank)", false, "EscapeWarnings, AudioDirector.P34 blast_thermo"),
            new(ThreatType.MineDetected, AudioClass.P1, "none yet", "-", "the mine's trigger radius", 0f, "none yet", "-",
                CancelBehavior.NotImplemented, "mine blast", false, "gap: queued for W2"),
            new(ThreatType.Emp, AudioClass.P1, "none yet", "-", "the EMP's radius", 0f, "none yet", "-",
                CancelBehavior.NotImplemented, "-", false, "gap: queued for W2"),
        };

        public static IReadOnlyList<ThreatCue> All => Table;

        public static ThreatCue For(ThreatType type) => Table[(int)type];

        /// <summary>
        /// The threat a fired round is, for its cue: a top attack only for a top-attack weapon (spec part AE: never for ordinary
        /// direct fire), a super-heavy strike from T5, else by projectile.
        /// </summary>
        public static ThreatType Of(WeaponDef round, bool bossBigAttack = false)
        {
            if (bossBigAttack) return ThreatType.BossSuperweapon;
            if (round == null) return ThreatType.ArtilleryIncoming;
            if (round.Tier >= 5) return ThreatType.SuperheavyStrike;
            if (round.TopAttack) return ThreatType.TopAttack;
            if (round.Thermobaric) return ThreatType.Thermobaric;
            return round.Projectile switch
            {
                ProjectileKind.Missile => ThreatType.MissileIncoming,
                ProjectileKind.Bomb => round.LaysStick ? ThreatType.BombStick : ThreatType.Bomb,
                _ => round.WarnSeconds > 0f ? ThreatType.HeavyRoundIncoming : ThreatType.ArtilleryIncoming,
            };
        }
    }
}

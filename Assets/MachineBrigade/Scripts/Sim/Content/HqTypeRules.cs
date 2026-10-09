#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 32 L4: what a side's HQ is (chosen in the base loadout, from HQ level 1; it replaces the old HQ doctrine,
    /// which DECISIONS 23D had already folded into the commanders). Each type has a passive and one skill on the one
    /// HQ button by the CP box (a shared 120 s cooldown).
    /// </summary>
    public enum HqType
    {
        /// <summary>No type: the plain HQ, no skill (a bare HQ, a mode's own camp, a loadout made in code).</summary>
        None,

        /// <summary>Weapons on the HQ (a medium tower's gun, ground or anti-air); skill: a focused barrage of three heavy rounds.</summary>
        Fortress,

        /// <summary>A reaction garrison: a squad stocked every 60 s (two at most) that turns out when enemies enter the base; skill: the alarm.</summary>
        Garrison,

        /// <summary>A point-defence dome over the base and slow tower repairs; skill: an emergency shield dome.</summary>
        Shield,
    }

    /// <summary>Prompt 32 L4: a Fortress HQ's branch: the ground (anti-vehicle) gun or the anti-air one.</summary>
    public enum HqBranch
    {
        Ground,
        Air,
    }

    /// <summary>
    /// Prompt 32 L4: the HQ types' numbers (balance.json "base.hqTypes"). Every scale is by HQ level 1-5 (the last value
    /// holds beyond). See DECISIONS "Prompt 32 L4/L5/L6/L8" and Tools/balance/p32_hq_types.py (the comparison).
    /// </summary>
    public sealed class HqTypeRules
    {
        /// <summary>A loadout (or a save) naming no type takes this one.</summary>
        public HqType Default { get; internal set; } = HqType.Fortress;

        /// <summary>The one skill's cooldown, seconds (every type).</summary>
        public float SkillCooldown { get; internal set; } = 120f;

        /// <summary>The base's region round its HQ (metres): the Shield's dome, the garrison's leash, the AI's threat count.</summary>
        public float Radius { get; internal set; } = 45f;

        // ------------------------------------------------------------------ Fortress

        /// <summary>The HQ def a Fortress HQ stands as, by branch (the plain HQ plus a medium tower's gun).</summary>
        public string FortressGround { get; internal set; } = "headquarters.fortress_ground";
        public string FortressAir { get; internal set; } = "headquarters.fortress_air";

        /// <summary>The Fortress's added gun against a medium tower of the same role, by HQ level (damage and cadence each take the square root).</summary>
        private float[] _fortressScale = { 0.5f, 0.65f, 0.8f, 1f, 1.2f };

        /// <summary>The anti-air branch's own table ("airScale"; none: the ground one's).</summary>
        private float[]? _fortressAirScale;

        /// <summary>The skill's three rounds (an event support: no deck, CP or cooldown of its own), their damage times the level's scale.</summary>
        public string Barrage { get; internal set; } = "hq_barrage";

        // ------------------------------------------------------------------ Garrison

        /// <summary>Seconds to stock one squad, by HQ level, and the most stocked at once.</summary>
        private float[] _garrisonEvery = { global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonEvery1, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonEvery2, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonEvery3, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonEvery4, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonEvery5 };
        public int GarrisonStock { get; internal set; } = 2;

        /// <summary>Seconds the base region must be clear of enemies before the garrison goes back in (and is gone).</summary>
        public float GarrisonClear { get; internal set; } = 30f;

        private readonly List<IReadOnlyList<string>> _squads = new()
        {
            new[] { "light_tank" }, new[] { "armored_car", "scout_jeep" }, new[] { "light_tank", "armored_car" },
            new[] { "main_battle_tank" }, new[] { "main_battle_tank", "scout_jeep" },
        };

        /// <summary>
        /// Play-test 14: the light units the player may have the HQ call (the HQ tab); a squad is then its level's count of that
        /// unit. Empty: the level's mixed squad (the AI's).
        /// </summary>
        private readonly List<string> _callable = new() { "scout_jeep", "armored_car", "light_tank" };

        public IReadOnlyList<string> Callable => _callable;

        /// <summary>The level's squad: the chosen unit as many times as the level's squad has units, or the squad itself.</summary>
        public IReadOnlyList<string> Squad(int level, string? unit)
        {
            var squad = Squad(level);
            if (string.IsNullOrEmpty(unit) || !_callable.Contains(unit!)) return squad;
            var calls = new string[squad.Count];
            for (var i = 0; i < calls.Length; i++) calls[i] = unit!;
            return calls;
        }

        /// <summary>The most baseCP of garrison alive at once, by HQ level.</summary>
        private int[] _garrisonCaps = { global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonCaps1, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonCaps2, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonCaps3, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonCaps4, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.GarrisonCaps5 };

        // ------------------------------------------------------------------ Shield

        /// <summary>The HQ def a Shield HQ stands as (the plain HQ plus a C-RAM's point defence over the base).</summary>
        public string ShieldHq { get; internal set; } = "headquarters.shield";

        /// <summary>The dome's interceptions against a medium C-RAM's, by HQ level (its charges and its reload pace).</summary>
        private float[] _shieldScale = { 0.5f, 0.65f, 0.8f, 1f, 1.2f };

        /// <summary>A medium C-RAM's interceptors (the scale's 1): the Shield HQ holds this many times its level's scale (its def's "aps" the most).</summary>
        public int ShieldCharges { get; internal set; } = 4;

        /// <summary>Seconds a tower in the base must go unhit before it mends, and the share of its full health it mends a second, by HQ level.</summary>
        public float RegenDelay { get; internal set; } = 5f;
        private float[] _regen = { global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Regen1, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Regen2, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Regen3, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Regen4, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Regen5 };

        /// <summary>The emergency dome: how much it absorbs (a share of the HQ's full health) by HQ level, and how long it stands.</summary>
        private float[] _dome = { global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Dome1, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Dome2, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Dome3, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Dome4, global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.Dome5 };
        public float DomeSeconds { get; internal set; } = 10f;

        // ------------------------------------------------------------------ the AI

        /// <summary>The enemy's type by its general's base style (varga, orlov ...), else by difficulty (Easy ... VeryHard).</summary>
        private readonly Dictionary<string, HqType> _ai = new(StringComparer.OrdinalIgnoreCase)
        {
            ["brandt"] = HqType.Fortress, ["kessler"] = HqType.Fortress, ["varga"] = HqType.Garrison,
            ["orlov"] = HqType.Shield, ["aurel"] = HqType.Shield,
            ["Easy"] = HqType.Garrison, ["Normal"] = HqType.Fortress, ["Hard"] = HqType.Shield, ["VeryHard"] = HqType.Fortress,
        };

        /// <summary>The share of aircraft in the deck an AI Fortress faces from which it takes the anti-air branch.</summary>
        public float AiAirShare { get; internal set; } = 0.3f;

        private static float ByLevel(float[] table, int level) => table[Math.Clamp(level, 1, table.Length) - 1];

        public float FortressScale(int level, HqBranch branch = HqBranch.Ground) =>
            ByLevel(branch == HqBranch.Air && _fortressAirScale != null ? _fortressAirScale : _fortressScale, level);
        public float GarrisonEvery(int level) => Math.Max(1f, ByLevel(_garrisonEvery, level));
        public float ShieldScale(int level) => ByLevel(_shieldScale, level);
        public float Regen(int level) => ByLevel(_regen, level);
        public float Dome(int level) => ByLevel(_dome, level);
        public int GarrisonCap(int level) => _garrisonCaps[Math.Clamp(level, 1, _garrisonCaps.Length) - 1];
        public IReadOnlyList<string> Squad(int level) => _squads[Math.Clamp(level, 1, _squads.Count) - 1];

        /// <summary>The HQ def a type stands as (null: the plain HQ).</summary>
        public string? HqDef(HqType type, HqBranch branch) => type switch
        {
            HqType.Fortress => branch == HqBranch.Air ? FortressAir : FortressGround,
            HqType.Shield => ShieldHq,
            _ => null,
        };

        /// <summary>The AI's type: its general's style's, else its difficulty's, else the default.</summary>
        public HqType ForAi(string? style, string? difficulty)
        {
            if (style != null && _ai.TryGetValue(style, out var byStyle)) return byStyle;
            if (difficulty != null && _ai.TryGetValue(difficulty, out var byDifficulty)) return byDifficulty;
            return Default;
        }

        /// <summary>The id a save and the data use ("fortress", "garrison", "shield").</summary>
        public static string Key(HqType type) => type.ToString().ToLowerInvariant();

        public static bool TryParse(string? key, out HqType type) => Enum.TryParse(key ?? "", true, out type) && Enum.IsDefined(typeof(HqType), type);

        private static float[] Floats(JsonObject o, string key, float[] fallback)
        {
            if (!o.Has(key)) return fallback;
            var list = o.FloatArray(key);
            if (list.Count == 0) return fallback;
            var a = new float[list.Count];
            for (var i = 0; i < a.Length; i++) a[i] = Math.Max(0f, list[i]);
            return a;
        }

        internal static HqTypeRules Parse(JsonObject o)
        {
            var r = new HqTypeRules();
            if (o.Has("default") && TryParse(o.String("default"), out var d)) r.Default = d;
            r.SkillCooldown = Math.Max(1f, o.Float("skillCooldown", r.SkillCooldown));
            r.Radius = Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.ParseFloatFloor2, o.Float("radius", r.Radius));
            if (o.Has("fortress"))
            {
                var f = o.Object("fortress");
                r.FortressGround = f.OptionalString("ground") ?? r.FortressGround;
                r.FortressAir = f.OptionalString("air") ?? r.FortressAir;
                r.Barrage = f.OptionalString("barrage") ?? r.Barrage;
                r._fortressScale = Floats(f, "scale", r._fortressScale);
                if (f.Has("airScale")) r._fortressAirScale = Floats(f, "airScale", r._fortressScale);
                r.AiAirShare = Math.Clamp(f.Float("aiAirShare", r.AiAirShare), 0f, 1f);
            }
            if (o.Has("garrison"))
            {
                var g = o.Object("garrison");
                // "every": one number for every level, or one a level.
                if (g.IsArray("every")) r._garrisonEvery = Floats(g, "every", r._garrisonEvery);
                else if (g.Has("every")) r._garrisonEvery = new[] { Math.Max(1f, g.Float("every", 60f)) };
                r.GarrisonStock = Math.Max(1, g.Int("stock", r.GarrisonStock));
                r.GarrisonClear = Math.Max(1f, g.Float("clear", r.GarrisonClear));
                if (g.Has("squads"))
                {
                    r._squads.Clear();
                    foreach (var s in g.Array("squads")) r._squads.Add(s.StringArray("units"));
                    if (r._squads.Count == 0) throw new FormatException("base.hqTypes.garrison.squads: at least one squad.");
                }
                if (g.Has("callable"))
                {
                    r._callable.Clear();
                    r._callable.AddRange(g.StringArray("callable"));
                }
                if (g.Has("caps"))
                {
                    var caps = g.FloatArray("caps");
                    if (caps.Count > 0)
                    {
                        r._garrisonCaps = new int[caps.Count];
                        for (var i = 0; i < caps.Count; i++) r._garrisonCaps[i] = Math.Max(0, (int)MathF.Round(caps[i]));
                    }
                }
            }
            if (o.Has("shield"))
            {
                var s = o.Object("shield");
                r.ShieldHq = s.OptionalString("hq") ?? r.ShieldHq;
                r._shieldScale = Floats(s, "scale", r._shieldScale);
                r.ShieldCharges = Math.Max(1, s.Int("charges", r.ShieldCharges));
                r.RegenDelay = Math.Max(0f, s.Float("regenDelay", r.RegenDelay));
                r._regen = Floats(s, "regen", r._regen);
                r._dome = Floats(s, "dome", r._dome);
                r.DomeSeconds = Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Bases.HqTypeRules.ParseFloatFloor4, s.Float("domeSeconds", r.DomeSeconds));
            }
            if (o.Has("ai"))
            {
                var ai = o.Object("ai");
                foreach (var key in ai.Keys)
                    if (TryParse(ai.String(key), out var t)) r._ai[key] = t;
                    else throw new FormatException($"base.hqTypes.ai.{key}: unknown HQ type '{ai.String(key)}'.");
            }
            return r;
        }
    }
}

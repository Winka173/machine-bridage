using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Hud
{
    /// <summary>Prompt 32 L8: one entry of the ammunition handbook: its title, its paragraphs and an optional table.</summary>
    public sealed class HandbookEntry
    {
        public HandbookEntry(string id, string title)
        {
            Id = id;
            Title = title;
        }

        public string Id { get; }
        public string Title { get; }
        public List<string> Lines { get; } = new();
        public string[] Header { get; set; }
        public List<string[]> Rows { get; } = new();
    }

    /// <summary>
    /// Prompt 32 L8: the ammunition handbook (the Dossier's "Ammunition handbook" tab, the detail page's chips), every
    /// number generated from the data and the rules' constants (<see cref="HandbookFacts"/>, the damage table, second
    /// rounds, armour levels), in the language shown (EN / VI). <c>HandbookP32Tests</c> compares the strings to the data.
    /// </summary>
    public static class AmmoHandbook
    {
        public const string Types = "types", Penetration = "penetration", Top = "mark.top", Thermobaric = "mark.thermobaric",
            Blast = "mark.blast", Guided = "mark.guided", Airburst = "mark.airburst", Alt = "mark.alt", MinRange = "mark.minrange",
            Defences = "defences", Structures = "structures", Walls = "structures.walls";

        public static readonly DamageType[] DamageTypes =
            { DamageType.Kinetic, DamageType.ShapedCharge, DamageType.HighExplosive, DamageType.Fire, DamageType.Fragmentation, DamageType.Energy };

        public static readonly TargetKind[] Kinds = { TargetKind.Ground, TargetKind.Air, TargetKind.Structure };

        /// <summary>A multiplier as the handbook writes it ("×0.6" / "×0,6").</summary>
        public static string Mult(float m) => "×" + Strings.Num(m, "0.##");

        /// <summary>A share as a percentage ("30%").</summary>
        public static string Percent(float share) => Strings.Num(share * 100f, "0") + "%";

        public static string Kind(TargetKind kind) => Strings.Get("hb.kind." + kind);

        public static string TypeName(DamageType type) => Strings.Get("dtype." + type);

        /// <summary>A weapon's name: its real name, else its id.</summary>
        public static string WeaponName(WeaponDef w) => string.IsNullOrEmpty(w.RealName) ? w.Id : w.RealName;

        /// <summary>A card a player fields (bought for CP; no structure, boss or elite): the handbook's examples come from these.</summary>
        private static bool Card(VehicleDef v) => v.CpCost > 0 && !v.Static && !v.Boss && !v.Elite && v.Fort == null;

        /// <summary>The weapons on the cards that pass <paramref name="fits"/>, the most carried first (then by id), at most <paramref name="count"/>.</summary>
        public static List<WeaponDef> Examples(Catalog c, System.Func<WeaponDef, bool> fits, int count = 3)
        {
            var carriers = new Dictionary<string, (WeaponDef w, int n)>();
            foreach (var v in c.Vehicles.Values)
            {
                if (!Card(v)) continue;
                foreach (var m in v.Mounts)
                {
                    var w = m.Weapon;
                    if (w == null || w.Damage <= 0f || !fits(w)) continue;
                    carriers[w.Id] = carriers.TryGetValue(w.Id, out var e) ? (w, e.n + 1) : (w, 1);
                }
            }
            // Two weapon lines of the same real weapon read as one example.
            return carriers.Values.OrderByDescending(e => e.n).ThenBy(e => e.w.Id, System.StringComparer.Ordinal)
                .GroupBy(e => WeaponName(e.w)).Select(g => g.First().w).Take(count).ToList();
        }

        private static string Names(IEnumerable<WeaponDef> ws) => string.Join(", ", ws.Select(WeaponName));

        /// <summary>The handbook's damage on a face: one shot's damage x penetration against that face x the damage type on the ground.</summary>
        public static float ShotOn(Catalog c, WeaponDef w, int armour) => w.Damage * c.Damage.Effective(w, armour, TargetKind.Ground);

        /// <summary>Every entry, in reading order.</summary>
        public static List<HandbookEntry> Build(Catalog c)
        {
            var list = new List<HandbookEntry>();
            var table = c.Damage;

            // 1. The six damage types against ground, air and structures.
            var types = new HandbookEntry(Types, Strings.Get("hb.types.title"))
            {
                Header = new[] { Strings.Get("hb.types.type"), Kind(TargetKind.Ground), Kind(TargetKind.Air), Kind(TargetKind.Structure) },
            };
            foreach (var t in DamageTypes)
            {
                types.Rows.Add(new[] { TypeName(t) }.Concat(Kinds.Select(k => Mult(table.Type(t, k)))).ToArray());
                var best = Kinds.OrderByDescending(k => table.Type(t, k)).First();
                var worst = Kinds.OrderBy(k => table.Type(t, k)).First();
                var examples = Examples(c, w => w.DamageType == t);
                types.Lines.Add(Strings.Format("hb.types.line", ("type", TypeName(t)), ("strong", Kind(best)), ("strongMult", Mult(table.Type(t, best))),
                    ("weak", Kind(worst)), ("weakMult", Mult(table.Type(t, worst))), ("examples", examples.Count > 0 ? Names(examples) : Strings.Get("hb.none"))));
            }
            list.Add(types);

            // 2. Penetration against armour, faces, bosses, a worked example.
            var pen = new HandbookEntry(Penetration, Strings.Get("hb.pen.title")) { Header = new[] { Strings.Get("hb.pen.diff"), Strings.Get("hb.pen.mult") } };
            for (var i = 0; i < DamageTable.PenetrationSteps; i++) pen.Rows.Add(new[] { Strings.Get("hb.pen.step" + i), Mult(table.PenetrationStep(i)) });
            pen.Lines.Add(Strings.Format("hb.pen.faces", ("unit", ArmourLevels.MaxUnit), ("boss", ArmourLevels.Max), ("roofMult", Mult(table.PenetrationStep(1)))));
            if (c.Vehicles.TryGetValue(c.Handbook.ExampleShooter, out var shooter) && shooter.Mounts.Count > 0 &&
                c.Vehicles.TryGetValue(c.Handbook.ExampleTarget, out var target))
            {
                var w = shooter.Mounts[0].Weapon;
                var a = target.Armour;
                pen.Lines.Add(Strings.Format("hb.pen.example", ("weapon", WeaponName(w)), ("shooter", Strings.Unit(shooter.Id)), ("pen", w.Penetration), ("damage", Strings.Num(w.Damage, "0")),
                    ("target", Strings.Unit(target.Id)), ("front", a.Front), ("frontMult", Mult(c.Damage.Effective(w, a.Front, TargetKind.Ground))),
                    ("frontHit", Strings.Num(ShotOn(c, w, a.Front), "0")), ("side", a.Side), ("sideMult", Mult(c.Damage.Effective(w, a.Side, TargetKind.Ground))),
                    ("sideHit", Strings.Num(ShotOn(c, w, a.Side), "0")), ("hp", Strings.Num(target.MaxHp, "0"))));
            }
            list.Add(pen);

            // 3. The special marks.
            var top = new HandbookEntry(Top, Strings.Get("hb.top.title"));
            top.Lines.Add(Strings.Format("hb.top", ("examples", Names(Examples(c, w => w.TopAttack)))));
            list.Add(top);
            var thermo = new HandbookEntry(Thermobaric, Strings.Get("hb.thermo.title"));
            thermo.Lines.Add(Strings.Format("hb.thermo", ("he", Mult(table.Type(DamageType.HighExplosive, TargetKind.Structure))), ("thermo", Mult(table.ThermobaricStructure)),
                ("examples", Names(Examples(c, w => w.Thermobaric)))));
            list.Add(thermo);
            var blast = new HandbookEntry(Blast, Strings.Get("hb.blast.title"));
            var edged = Examples(c, w => w.SplashEdge > w.SplashRadius && w.SplashRadius > 0f, 1);
            if (edged.Count > 0)
                blast.Lines.Add(Strings.Format("hb.blast", ("weapon", WeaponName(edged[0])), ("core", Strings.Num(edged[0].SplashRadius, "0.#")), ("edge", Strings.Num(edged[0].SplashEdge, "0.#")),
                    ("share", Percent(edged[0].EdgeShare))));
            else blast.Lines.Add(Strings.Get("hb.blast.plain"));
            list.Add(blast);
            var guided = new HandbookEntry(Guided, Strings.Get("hb.guided.title"));
            guided.Lines.Add(Strings.Format("hb.guided", ("examples", Names(Examples(c, w => w.Guided || w.GuidedBomb || w.GuidedShell)))));
            list.Add(guided);
            var air = new HandbookEntry(Airburst, Strings.Get("hb.airburst.title"));
            air.Lines.Add(Strings.Format("hb.airburst", ("air", Mult(table.Type(DamageType.Fragmentation, TargetKind.Air))), ("ground", Mult(table.Type(DamageType.Fragmentation, TargetKind.Ground))),
                ("examples", Names(Examples(c, w => w.DamageType == DamageType.Fragmentation && w.CanTarget(true))))));
            list.Add(air);
            var alt = new HandbookEntry(Alt, Strings.Get("hb.alt.title"));
            alt.Lines.Add(Strings.Format("hb.alt", ("hold", Strings.Num(WeaponDef.RoundHoldSeconds, "0.#")), ("min", Strings.Num(WeaponDef.MinSwitchSeconds, "0.#"))));
            var gun = Examples(c, w => w.Rounds.Count > 0, 1);
            if (gun.Count > 0)
            {
                var r = gun[0].Rounds[0];
                alt.Lines.Add(Strings.Format("hb.alt.example", ("gun", WeaponName(gun[0])), ("round", WeaponName(r.Round)), ("seconds", Strings.Num(gun[0].SwitchSeconds(r), "0.#"))));
            }
            list.Add(alt);
            var min = new HandbookEntry(MinRange, Strings.Get("hb.minrange.title"));
            min.Lines.Add(Strings.Format("hb.minrange", ("examples", string.Join(", ", Examples(c, w => w.MinRange > 0f).Select(w => WeaponName(w) + " (" + Strings.Num(w.MinRange, "0") + " m)")))));
            list.Add(min);

            // 4. What stops which rounds (SELF_APS and POINT_DEFENSE never a tank's shell).
            var def = new HandbookEntry(Defences, Strings.Get("hb.def.title"));
            def.Lines.Add(Strings.Format("hb.def.era", ("cap", Percent(HandbookFacts.ReactiveCap))));
            def.Lines.Add(Strings.Get("hb.def.cage"));
            def.Lines.Add(Strings.Get("hb.def.selfaps"));
            var cram = c.Vehicles.TryGetValue("c_ram", out var cr) && cr.Aps != null ? cr.Aps.Shells : 0f;
            var laser = c.Vehicles.TryGetValue("laser_ad_station", out var la) && la.Aps != null ? la.Aps.Shells : 0f;
            def.Lines.Add(Strings.Format("hb.def.pd", ("cram", Percent(cram)), ("laser", Percent(laser))));
            def.Lines.Add(Strings.Get("hb.def.flares"));
            def.Lines.Add(Strings.Get("hb.def.smoke"));
            def.Lines.Add(Strings.Get("hb.def.jam"));
            def.Lines.Add(Strings.Get("hb.def.shield"));
            list.Add(def);

            // 5. What to hit structures with.
            var st = new HandbookEntry(Structures, Strings.Get("hb.struct.title")) { Header = new[] { Strings.Get("hb.types.type"), Kind(TargetKind.Structure) } };
            foreach (var type in DamageTypes.OrderByDescending(x => table.Type(x, TargetKind.Structure)))
                st.Rows.Add(new[] { TypeName(type), Mult(table.Type(type, TargetKind.Structure)) });
            st.Rows.Insert(0, new[] { Strings.Get("hb.struct.thermo"), Mult(table.ThermobaricStructure) });
            st.Lines.Add(Strings.Format("hb.struct", ("he", Mult(table.Type(DamageType.HighExplosive, TargetKind.Structure))), ("thermo", Mult(table.ThermobaricStructure)),
                ("fire", Mult(table.Type(DamageType.Fire, TargetKind.Structure)))));
            st.Lines.Add(Strings.Format("hb.struct.weak", ("kinetic", Mult(table.Type(DamageType.Kinetic, TargetKind.Structure))),
                ("shaped", Mult(table.Type(DamageType.ShapedCharge, TargetKind.Structure))), ("frag", Mult(table.Type(DamageType.Fragmentation, TargetKind.Structure)))));
            list.Add(st);
            var walls = new HandbookEntry(Walls, Strings.Get("hb.walls.title"));
            walls.Lines.Add(Strings.Format("hb.walls", ("mult", Mult(c.Base.WallBreakerMultiplier)),
                ("units", string.Join(", ", c.Base.WallBreakers.Where(c.Vehicles.ContainsKey).Select(Strings.Unit)))));
            list.Add(walls);
            return list;
        }

        /// <summary>
        /// The detail page's chips for a vehicle: (label key, the entry it opens). Top attack, a second round, airburst,
        /// guided, a structure breaker (a weapon at x1.5 or more on structures), a wall breaker.
        /// </summary>
        public static List<(string key, string entry)> Chips(Catalog c, VehicleDef v)
        {
            var chips = new List<(string, string)>();
            var ws = v.Mounts.Select(m => m.Weapon).Where(w => w != null && w.Damage > 0f).ToList();
            if (ws.Any(Armour.StrikesTop)) chips.Add(("hb.chip.top", Top));
            if (ws.Any(w => w.Rounds.Any(r => r.CarriedBy(v)))) chips.Add(("hb.chip.alt", Alt));
            if (ws.Any(w => w.DamageType == DamageType.Fragmentation && w.CanTarget(true))) chips.Add(("hb.chip.airburst", Airburst));
            if (ws.Any(w => w.Guided || w.GuidedBomb || w.GuidedShell)) chips.Add(("hb.chip.guided", Guided));
            if (ws.Any(w => c.Damage.TypeOf(w, TargetKind.Structure) >= 1.5f)) chips.Add(("hb.chip.structure", Structures));
            if (c.Base.WallBreakers.Contains(v.Id)) chips.Add(("hb.chip.wall", Walls));
            return chips;
        }
    }
}

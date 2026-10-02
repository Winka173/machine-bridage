#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// The enemy's elites (prompt 8 H): what an elite costs against its base card, the share of the
    /// enemy's spending that goes on them and how many may be out at once (both by difficulty, from
    /// Easy to Iron), and what beating one pays after the battle. balance.json "elites".
    /// </summary>
    public sealed class EliteRules
    {
        /// <summary>An elite costs its base card's CP times this (and refunds its kill at that price).</summary>
        public float CostScale { get; internal set; } = 1.6f;

        /// <summary>An elite's health against its base card's (the data's elite "hp" is set to it; a test holds them to it).</summary>
        public float HpScale { get; internal set; } = 1.6f;

        /// <summary>Everything an elite fires hits this many times as hard as its base card's gun would.</summary>
        public float DamageScale { get; internal set; } = 1.25f;

        /// <summary>A general's elites: the cards it does not favour get this share of the budget (the favoured ones all of it).</summary>
        public float OtherShare { get; internal set; } = 0.5f;

        /// <summary>At most this many elites a battle pay their bounty (so a long battle's pay stays on the prompt 7 curve).</summary>
        public int BountyCap { get; internal set; } = 4;

        internal Dictionary<string, float> Budget { get; set; } = new();
        internal Dictionary<string, int> Cap { get; set; } = new();

        /// <summary>Coins each elite destroyed pays after the battle.</summary>
        public int Coins { get; internal set; } = 15;

        /// <summary>Chance an elite destroyed drops a blueprint of its base card.</summary>
        public float BlueprintChance { get; internal set; } = 0.08f;

        /// <summary>
        /// An elite's fighting worth against its base card's (health times firepower, its skills
        /// counted in): the target band is 1.8 to 2.2. The campaign's enemy scaling takes the edge the
        /// elite budget adds into account with it.
        /// </summary>
        public float PowerRatio { get; internal set; } = 2f;

        /// <summary>The share of the enemy's vehicle spending that may go on elites at a difficulty (Easy, Normal, Hard, Heroic, Iron).</summary>
        public float BudgetFor(string? difficulty) =>
            difficulty != null && Budget.TryGetValue(difficulty, out var share) ? share : Budget.TryGetValue("Normal", out var normal) ? normal : 0.1f;

        /// <summary>How many elites the enemy may have out at once at a difficulty.</summary>
        public int CapFor(string? difficulty) =>
            difficulty != null && Cap.TryGetValue(difficulty, out var cap) ? cap : Cap.TryGetValue("Normal", out var normal) ? normal : 2;

        /// <summary>
        /// How much stronger per CP an army gets with this share of its spending on elites (elites are
        /// <see cref="PowerRatio"/> as strong for <see cref="CostScale"/> the price).
        /// </summary>
        public float PowerEdge(float share) => MathF.Max(0f, share) * MathF.Max(0f, PowerRatio / MathF.Max(0.1f, CostScale) - 1f);
    }

    /// <summary>
    /// An enemy general (balance.json "generals"): which of the deck's cards the general turns into
    /// elites first (class names, or "Drone" for drone carriers and UAVs), and cards the general always
    /// adds to the deck (Varga's armoured bulldozer).
    /// </summary>
    public sealed class GeneralRules
    {
        public GeneralRules(string id) => Id = Guard.Id(id);

        public string Id { get; }
        public IReadOnlyList<string> ElitePrefer { get; internal set; } = Array.Empty<string>();
        public IReadOnlyList<string> Deck { get; internal set; } = Array.Empty<string>();

        /// <summary>Whether this general favours making an elite of this card.</summary>
        public bool Prefers(VehicleDef def)
        {
            foreach (var p in ElitePrefer)
            {
                if (p == "Drone" && Catalog.FliesDrones(def)) return true;
                if (p == "Air" && def.Flying) return true;
                if (Enum.TryParse<UnitClass>(p, out var c) && def.Class == c) return true;
            }
            return false;
        }
    }

    public sealed partial class Catalog
    {
        /// <summary>The enemy's elite budget, caps and rewards.</summary>
        public EliteRules Elites { get; internal set; } = new();

        /// <summary>The enemy generals, by id (varga, orlov, sen, quaden...).</summary>
        public IReadOnlyDictionary<string, GeneralRules> Generals { get; internal set; } = new Dictionary<string, GeneralRules>();

        /// <summary>Which army branch each class belongs to (balance.json "branches").</summary>
        public IReadOnlyDictionary<UnitClass, ArmyBranch> BranchByClass { get; internal set; } = DefaultBranches();

        /// <summary>A card that fights with drones: a drone carrier, a loitering munition launcher, a UAV.</summary>
        public static bool FliesDrones(VehicleDef def)
        {
            if (def.Drone) return true;
            foreach (var m in def.Mounts)
                if (m.Weapon.Projectile == ProjectileKind.Drone) return true;
            return false;
        }

        private static Dictionary<UnitClass, ArmyBranch> DefaultBranches() => new()
        {
            [UnitClass.Tank] = ArmyBranch.Armor, [UnitClass.Heavy] = ArmyBranch.Armor, [UnitClass.TankHunter] = ArmyBranch.Armor,
            [UnitClass.Light] = ArmyBranch.Light, [UnitClass.Scout] = ArmyBranch.Light, [UnitClass.AntiAir] = ArmyBranch.Light,
            [UnitClass.Support] = ArmyBranch.Light, [UnitClass.Artillery] = ArmyBranch.Artillery,
            [UnitClass.Helicopter] = ArmyBranch.Air, [UnitClass.Plane] = ArmyBranch.Air,
        };

        /// <summary>
        /// A vehicle's equipment branch: an aircraft is Air, the rest by class (balance.json
        /// "branches": the long-range SAM is anti-air and so Light, the FPV carrier a tank hunter and so
        /// Armour); a class the table does not name goes by its gun (a minimum range: Artillery, else
        /// Light); a def may name its own ("branch").
        /// </summary>
        internal static ArmyBranch BranchFor(VehicleDef def, IReadOnlyDictionary<UnitClass, ArmyBranch> byClass, ArmyBranch? own)
        {
            if (own is { } named) return named;
            if (def.Flying) return ArmyBranch.Air;
            if (byClass.TryGetValue(def.Class, out var branch)) return branch;
            return def.Weapon.MinRange > 0f ? ArmyBranch.Artillery : ArmyBranch.Light;
        }

        /// <summary>Prompt 8's vehicle fields (see VehicleDef.Extra.cs).</summary>
        private static void ParseExtras(JsonObject v, VehicleDef def)
        {
            def.MineArmor = Math.Clamp(v.Float("mineArmor", 1f), 0f, 1f);
            // 0 until FinishExtras fills in the elite default (or 1).
            def.DamageScale = v.Has("damageScale") ? Math.Clamp(v.Float("damageScale", 1f), 0.1f, 5f) : 0f;
            def.WeaponDamage = Math.Clamp(v.Float("weaponDamage", 1f), 0.1f, 10f);
            // Prompt 29 S03, S04.
            def.OutgoingDamageMult = Math.Clamp(v.Float("outgoingDamageMult", 1f), 0.1f, 10f);
            def.DropDelay = Math.Clamp(v.Float("dropDelay", Economy.EconomySystem.DeliverySeconds), 0.5f, 30f);
            // Prompt 29 S06, S07.
            def.FlareCharges = Math.Max(0, v.Int("flareCharges", 0));
            def.FlareRecharge = v.Has("flareRecharge") ? Math.Max(1f, v.Float("flareRecharge", 20f)) : null;
            def.ApsCapability = v.Enum("apsCapability", ApsCapability.None);
            def.InterceptionModeData = v.Has("interceptionMode") ? v.Enum<InterceptionMode>("interceptionMode") : null;
            def.Breacher = v.Bool("breacher", false);
            def.MarkedSpread = Math.Clamp(v.Float("markedSpread", 1f), 0.01f, 1f);
            if (v.Has("radioSpawn")) def.RadioSpawn = v.String("radioSpawn");
            if (v.Has("scoot"))
            {
                var s = v.Object("scoot");
                def.Scoot = new ScootDef { Shots = Math.Max(1, s.Int("shots", 3)), Min = s.Float("min", 15f), Max = s.Float("max", 20f) };
            }
            if (v.Has("parts"))
            {
                var parts = new List<BossPartDef>();
                foreach (var p in v.Array("parts"))
                {
                    var part = Wrap(p, () => new BossPartDef(p.String("id"), p.Has("kind") ? p.String("kind") : "part", p.Float("hp")));
                    if (p.Has("node")) part.Node = p.String("node");
                    if (p.Has("wreck")) part.Wreck = p.String("wreck");
                    if (p.Has("at"))
                    {
                        var at = p.FloatArray("at");
                        part.At = new Vector2(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f);
                        part.Height = at.Count > 2 ? at[2] : 0f;
                    }
                    part.Radius = p.Float("radius", 2f);
                    if (p.Has("armour"))
                    {
                        var level = p.Int("armour", 0);
                        part.Armour = level >= 0 && level <= ArmourLevels.Max ? level : throw new FormatException($"{p.Path}.armour: a level 0 to {ArmourLevels.Max}.");
                    }
                    if (p.Has("mounts"))
                    {
                        var mounts = new List<int>();
                        foreach (var m in p.FloatArray("mounts")) mounts.Add((int)m);
                        part.Mounts = mounts;
                    }
                    if (p.Has("skills")) part.Skills = p.StringArray("skills");
                    part.Speed = p.Float("speed", 1f);
                    part.Spread = p.Float("spread", 1f);
                    part.Fail = Math.Clamp(p.Float("fail", 0f), 0f, 1f);
                    if (p.Has("affects"))
                    {
                        var affects = new List<int>();
                        foreach (var m in p.FloatArray("affects")) affects.Add((int)m);
                        part.Affects = affects;
                    }
                    part.BreakDamage = Math.Clamp(p.Float("breakDamage", 0.3f), 0f, 1f);
                    // Prompt 9: what else it drives, how it breaks in the view, its radio line.
                    if (p.Has("stops")) part.Stops = p.StringArray("stops");
                    part.Turn = Math.Clamp(p.Float("turn", 1f), 0.05f, 2f);
                    part.Cadence = Math.Clamp(p.Float("cadence", 1f), 0.2f, 5f);
                    if (p.Has("radio")) part.Radio = p.String("radio");
                    part.Fx = p.Has("fx") ? p.String("fx") : BossPartDef.FxFor(part.Kind);
                    part.Attachment = p.Int("attach", -1);
                    parts.Add(part);
                }
                def.Parts = parts;
            }
            if (v.Has("partLock"))
            {
                var l = v.Object("partLock");
                def.PartLock = Wrap(l, () => new PartLockDef(l.String("kind"), l.Int("count", 1)));
            }
            if (v.Has("burrow"))
            {
                var b = v.Object("burrow");
                def.Burrow = new BurrowDef
                {
                    Surface = b.Float("surface", 20f), Dive = b.Float("dive", 2f), Speed = b.Float("speed", 14f), Warn = b.Float("warn", 2f),
                    Radius = b.Float("radius", 15f), Stun = b.Float("stun", 3f), Damage = b.Float("damage", 300f), Exposed = b.Float("exposed", 6f),
                    ExposedTaken = b.Float("exposedTaken", 1.5f), First = b.Float("first", 12f),
                    // Prompt 20 J.4: a submarine's dives (Typhon): on the sea lanes, a phase's own times, none from its last phase.
                    Sea = b.Bool("sea", false), Under = MathF.Max(0f, b.Float("under", 0f)), StopPhase = b.Int("stopPhase", -1),
                    SurfaceByPhase = b.Has("surfaceByPhase") ? b.FloatArray("surfaceByPhase") : Array.Empty<float>(),
                    UnderByPhase = b.Has("underByPhase") ? b.FloatArray("underByPhase") : Array.Empty<float>(),
                };
            }
            if (v.Has("landing"))
            {
                var l = v.Object("landing");
                var ramp = l.Has("ramp") ? l.FloatArray("ramp") : new[] { 0f, 10f };
                def.Landing = new LandingDef
                {
                    Every = l.Float("every", 40f), Stop = l.Float("stop", 6f), Min = l.Int("min", 3), Max = l.Int("max", 4),
                    Landings = l.Int("landings", 4), First = l.Float("first", 20f),
                    Units = l.Has("units") ? l.StringArray("units") : Array.Empty<string>(),
                    Ramp = new Vector2(ramp.Count > 0 ? ramp[0] : 0f, ramp.Count > 1 ? ramp[1] : 10f),
                };
            }
            if (v.Has("bombard"))
            {
                var b = v.Object("bombard");
                def.Bombard = new BombardDef
                {
                    // Prompt 25 C2: -1 takes the weapon's (below, once the weapons are read).
                    Every = b.Has("every") ? b.Float("every", 20f) : b.Has("weapon") ? -1f : 20f, Warn = b.Float("warn", 3f),
                    Damage = b.Has("damage") ? b.Float("damage", 1400f) : b.Has("weapon") ? -1f : 1400f,
                    Radius = b.Has("radius") ? b.Float("radius", 14f) : b.Has("weapon") ? -1f : 14f,
                    Scatter = b.Float("scatter", 3f), BlindScatter = b.Float("blindScatter", 2.5f), First = b.Float("first", 10f),
                    Spotter = b.Has("spotter") ? b.String("spotter") : null, Weapon = b.Has("weapon") ? b.String("weapon") : null,
                    Warning = b.Has("warning") ? b.String("warning") : null,
                    PierceMax = Math.Max(0, b.Int("pierceMax", 0)), PierceDamage = MathF.Max(0f, b.Float("pierceDamage", 0f)),
                    GlobalTargeting = !string.Equals(b.Has("targeting") ? b.String("targeting") : "Global", "Range", StringComparison.OrdinalIgnoreCase),
                };
            }
            // Prompt 18: its big attack by id, and its own scaling of it.
            if (v.Has("bigAttack")) def.BigAttackId = v.String("bigAttack");
            if (v.Has("bigAttackScale"))
            {
                var s = v.Object("bigAttackScale");
                def.BigAttackScale = new BigAttackScale(MathF.Max(0f, s.Float("damage", 1f)), MathF.Max(0.1f, s.Float("cooldown", 1f)), s.Float("warn", 0f));
            }
            if (v.Has("fireTrail"))
            {
                var f = v.Object("fireTrail");
                def.FireTrail = new FireTrailDef
                {
                    Every = MathF.Max(0.5f, f.Float("every", 4f)), Seconds = MathF.Max(0.5f, f.Float("seconds", 10f)),
                    Radius = MathF.Max(0.5f, f.Float("radius", 3.5f)), Dps = MathF.Max(0f, f.Float("dps", 18f)),
                };
            }
            if (v.Has("guards"))
            {
                var guards = new List<GuardDef>();
                foreach (var g in v.Array("guards"))
                {
                    var at = g.FloatArray("at");
                    guards.Add(Wrap(g, () => new GuardDef(g.String("def"), new Vector2(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f), g.Float("heading", 0f))));
                }
                def.Guards = guards;
            }
            if (v.Has("attach"))
            {
                var list = new List<AttachmentDef>();
                foreach (var a in v.Array("attach"))
                {
                    var at = a.FloatArray("at");
                    list.Add(Wrap(a, () => new AttachmentDef(a.String("model"),
                        new Vector3(at.Count > 0 ? at[0] : 0f, at.Count > 1 ? at[1] : 0f, at.Count > 2 ? at[2] : 0f), a.Float("heading", 0f))));
                }
                def.Attachments = list;
            }
            // Prompt 17 C: domes, deploying, wingmen, relays.
            ParseP17(v, def);
            // Prompt 19: altitude tiers, drop pods, weapon ceilings, a Boss Rush arena.
            ParseP19(v, def);
            ParseP20(v, def);
            // Prompt 22 E: a duel mode, a story-only unit.
            ParseP22(v, def);
            // The tower-branch rework (DECISIONS 19T): tower shields, the loot depot, the radar's air picture, the branch art.
            ParseBranchRework(v, def);
            // Prompt 32 L1: the tower roster's declared branches, noBranch and role tags.
            ParseRoster(v, def);
            // Prompt 25 F2 batch A (DECISIONS 25F2-A): the new units' and structures' mechanisms.
            ParseP25A(v, def);
        }

        /// <summary>
        /// Root-level prompt 8 data, once every vehicle is built: the branches, the elite rules (and
        /// each elite's army cost at the elite price), the generals, and the checks that every part's
        /// mounts and skills and every boss's guards and landing units exist.
        /// </summary>
        private void FinishExtras(JsonObject root, Dictionary<string, ArmyBranch?> ownBranches)
        {
            if (root.Has("branches"))
            {
                var map = new Dictionary<UnitClass, ArmyBranch>();
                var b = root.Object("branches");
                foreach (var key in b.Keys)
                {
                    if (!Enum.TryParse<ArmyBranch>(key, true, out var branch)) throw new FormatException($"balance.branches: unknown branch '{key}'.");
                    foreach (var name in b.StringArray(key))
                        map[Enum.TryParse<UnitClass>(name, true, out var c) ? c : throw new FormatException($"balance.branches.{key}: unknown class '{name}'.")] = branch;
                }
                BranchByClass = map;
            }
            foreach (var def in _vehicles.Values)
                def.Branch = BranchFor(def, BranchByClass, ownBranches.TryGetValue(def.Id, out var own) ? own : null);

            if (root.Has("elites"))
            {
                var e = root.Object("elites");
                var rules = new EliteRules
                {
                    CostScale = e.Float("costScale", 1.6f), Coins = e.Int("coins", 15), BlueprintChance = e.Float("blueprintChance", 0.08f),
                    PowerRatio = e.Float("powerRatio", 2f), HpScale = e.Float("hpScale", 1.6f), DamageScale = e.Float("damageScale", 1.25f),
                    OtherShare = Math.Clamp(e.Float("otherShare", 0.5f), 0f, 1f), BountyCap = Math.Max(0, e.Int("bountyCap", 4)),
                };
                if (e.Has("budget"))
                {
                    var budget = e.Object("budget");
                    foreach (var key in budget.Keys) rules.Budget[key] = budget.Float(key);
                }
                if (e.Has("cap"))
                {
                    var cap = e.Object("cap");
                    foreach (var key in cap.Keys) rules.Cap[key] = cap.Int(key, 2);
                }
                Elites = rules;
            }
            // An elite counts (army value, kill refunds) at its elite price, and hits harder by the elite scale.
            foreach (var v in _vehicles.Values)
            {
                if (v.EliteOf != null && _vehicles.TryGetValue(v.EliteOf, out var original))
                    v.ArmyCost = EliteCost(original);
                if (v.DamageScale <= 0f) v.DamageScale = v.Elite && v.EliteOf != null ? Elites.DamageScale : 1f;
            }

            if (root.Has("generals"))
            {
                var generals = new Dictionary<string, GeneralRules>();
                var g = root.Object("generals");
                foreach (var key in g.Keys)
                {
                    var o = g.Object(key);
                    var general = new GeneralRules(key)
                    {
                        ElitePrefer = o.Has("elites") ? o.StringArray("elites") : Array.Empty<string>(),
                        Deck = o.Has("deck") ? o.StringArray("deck") : Array.Empty<string>(),
                    };
                    foreach (var id in general.Deck)
                        if (!_vehicles.ContainsKey(id)) throw new FormatException($"balance.generals.{key}.deck: unknown vehicle '{id}'.");
                    generals[key] = general;
                }
                Generals = generals;
            }

            foreach (var def in _vehicles.Values)
            {
                foreach (var part in def.Parts)
                {
                    foreach (var m in part.Mounts)
                        if (m < 0 || m >= def.Mounts.Count) throw new FormatException($"{def.Id}.parts.{part.Id}: no weapon mount {m}.");
                    foreach (var m in part.Affects)
                        if (m < 0 || m >= def.Mounts.Count) throw new FormatException($"{def.Id}.parts.{part.Id}: no weapon mount {m} to affect.");
                    foreach (var stop in part.Stops)
                        if (Array.IndexOf(BossPartDef.Mechanisms, stop) < 0) throw new FormatException($"{def.Id}.parts.{part.Id}: unknown mechanism '{stop}'.");
                    if (part.Attachment >= def.Attachments.Count) throw new FormatException($"{def.Id}.parts.{part.Id}: no attached model {part.Attachment}.");
                    foreach (var s in part.Skills)
                    {
                        var found = false;
                        foreach (var k in def.Skills) found |= k.Id == s;
                        if (!found) throw new FormatException($"{def.Id}.parts.{part.Id}: the boss has no skill '{s}'.");
                    }
                }
                if (def.PartLock != null && def.Parts.Count > 0)
                {
                    var n = 0;
                    foreach (var p in def.Parts) if (p.Kind == def.PartLock.Kind) n++;
                    if (n < def.PartLock.Count) throw new FormatException($"{def.Id}.partLock: only {n} parts of kind '{def.PartLock.Kind}'.");
                }
                foreach (var guard in def.Guards)
                    if (!_vehicles.ContainsKey(guard.Def)) throw new FormatException($"{def.Id}.guards: unknown vehicle '{guard.Def}'.");
                // Prompt 25 C2: a crusher that is a weapon (Kronos's bucket wheel) takes its numbers.
                if (def.Crush is { Weapon: { } wheel } crush)
                {
                    if (!_weapons.TryGetValue(wheel, out var w)) throw new FormatException($"{def.Id}.crush.weapon: unknown weapon '{wheel}'.");
                    if (crush.Dps < 0f) crush.Dps = w.Damage / MathF.Max(0.05f, w.Cooldown);
                    if (crush.Reach < 0f) crush.Reach = MathF.Max(0.5f, w.Range);
                }
                if (def.Landing != null)
                    foreach (var id in def.Landing.Units)
                        if (!_vehicles.ContainsKey(id)) throw new FormatException($"{def.Id}.landing.units: unknown vehicle '{id}'.");
                if (def.Bombard is { } bombard)
                {
                    if (bombard.Weapon != null && !_weapons.ContainsKey(bombard.Weapon)) throw new FormatException($"{def.Id}.bombard.weapon: unknown weapon '{bombard.Weapon}'.");
                    // Prompt 25 C2: the gun's own numbers where the bombard gives none.
                    if (bombard.Weapon != null && _weapons.TryGetValue(bombard.Weapon, out var gun))
                    {
                        if (bombard.Damage < 0f) bombard.Damage = gun.Damage;
                        if (bombard.Radius < 0f) bombard.Radius = MathF.Max(1f, gun.SplashRadius);
                        if (bombard.Every < 0f) bombard.Every = MathF.Max(bombard.Warn + 1f, gun.Cooldown);
                    }
                    if (bombard.Warning != null && !_supports.ContainsKey(bombard.Warning)) throw new FormatException($"{def.Id}.bombard.warning: unknown support '{bombard.Warning}'.");
                    if (bombard.Spotter != null && !_vehicles.ContainsKey(bombard.Spotter)) throw new FormatException($"{def.Id}.bombard.spotter: unknown vehicle '{bombard.Spotter}'.");
                }
            }
            // Prompt 20: frames, ranks and variants (the escort caps need the ranks).
            FinishP20(root);
            // Prompt 16 F: every boss's escort table.
            ParseEscorts(root);
            // Prompt 18: the big-attack library and every boss's attack.
            ParseBigAttacks(root);
            // Prompt 19: the tiered bosses' pods and crash.
            CheckTiers();
            // Prompt 22 E: the duels' big attacks.
            FinishP22();
            // Prompt 25 F2 batch A: the ids the new mechanisms name.
            FinishP25A();
        }

        /// <summary>What an elite of this base card costs the enemy (and refunds when destroyed): its CP times the elite scale, rounded.</summary>
        public int EliteCost(VehicleDef original) => Math.Max(1, (int)MathF.Round(original.CpCost * Elites.CostScale));
    }
}

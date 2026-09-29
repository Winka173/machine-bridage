#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Every definition a match can use, resolved and validated up front so the simulation
    /// never meets a dangling id mid-battle.
    /// </summary>
    public sealed partial class Catalog
    {
        private readonly Dictionary<string, WeaponDef> _weapons;
        private readonly Dictionary<string, VehicleDef> _vehicles;
        private readonly Dictionary<string, PropDef> _props;
        private readonly Dictionary<string, SupportDef> _supports;

        public Catalog(int version, DamageTable damage, IEnumerable<WeaponDef> weapons,
            IEnumerable<VehicleDef> vehicles, IEnumerable<PropDef> props, IEnumerable<SupportDef>? supports = null)
        {
            _supports = Index(supports ?? Array.Empty<SupportDef>(), s => s.Id, "support");
            Version = version;
            Damage = damage ?? throw new ArgumentNullException(nameof(damage));
            _weapons = Index(weapons, w => w.Id, "weapon");
            _vehicles = Index(vehicles, v => v.Id, "vehicle");
            _props = Index(props, p => p.Id, "prop");
            foreach (var v in _vehicles.Values)
            {
                v.Branch = BranchFor(v, BranchByClass, null);
                if (v.EliteOf == null || !_vehicles.TryGetValue(v.EliteOf, out var original)) continue;
                // An elite counts (army value, kill refunds) at its elite price (prompt 8 H.4).
                v.ArmyCost = EliteCost(original);
                _elites.TryAdd(v.EliteOf, v.Id);
            }
        }

        private readonly Dictionary<string, string> _elites = new();

        /// <summary>The elite version of a vehicle, if it has one.</summary>
        public string? EliteVariant(string vehicleId) => _elites.TryGetValue(vehicleId, out var elite) ? elite : null;

        /// <summary>Balance version, recorded with results so tuning changes stay traceable.</summary>
        public int Version { get; }

        /// <summary>Multiplies every side's CP income, objective bonuses included (balance.json "economy.income").</summary>
        public float IncomeScale { get; internal set; } = 1f;

        /// <summary>Bases: the HQ, hardpoint budgets, tower rebuilds, roles by mode (balance.json "base").</summary>
        public BaseRules Base { get; internal set; } = new();

        /// <summary>Multiplies every side's supply line, the army kept up at full income ("economy.supply").</summary>
        public float SupplyScale { get; internal set; } = 1f;

        /// <summary>The share of the player's arsenal edge a campaign enemy matches (balance.json economy.enemyScaling).</summary>
        public float EnemyScaling { get; internal set; } = 0.55f;

        internal Dictionary<string, int> ArmyCaps { get; set; } = new();

        internal Dictionary<string, int> VehicleCaps { get; set; } = new();

        /// <summary>The enemy's vehicle ceiling in a mode (balance.json economy.vehicleCap): its entry, else "default", else 32.</summary>
        public int VehicleCapFor(string? mode) =>
            mode != null && VehicleCaps.TryGetValue(mode, out var cap) ? cap : VehicleCaps.TryGetValue("default", out var d) ? d : Economy.TeamEconomy.MaxVehicles;

        /// <summary>The army supply (CP) of a mode that does not set its own: its entry, else "default", else 24.</summary>
        public int ArmyCapFor(string? mode) =>
            mode != null && ArmyCaps.TryGetValue(mode, out var cap) ? cap : ArmyCaps.TryGetValue("default", out var d) ? d : 24;

        public DamageTable Damage { get; }

        public IReadOnlyDictionary<string, WeaponDef> Weapons => _weapons;
        public IReadOnlyDictionary<string, VehicleDef> Vehicles => _vehicles;
        public IReadOnlyDictionary<string, PropDef> Props => _props;
        public IReadOnlyDictionary<string, SupportDef> Supports => _supports;

        public bool TryGetSupport(string id, out SupportDef support) => _supports.TryGetValue(id, out support!);

        /// <summary>Prompt 19: a prop by id, if there is one.</summary>
        public bool TryGetProp(string id, out PropDef prop) => _props.TryGetValue(id, out prop!);

        public VehicleDef Vehicle(string id) =>
            _vehicles.TryGetValue(id, out var def) ? def : throw new KeyNotFoundException($"Unknown vehicle '{id}'.");

        public PropDef Prop(string id) =>
            _props.TryGetValue(id, out var def) ? def : throw new KeyNotFoundException($"Unknown prop '{id}'.");

        private static AuraDef ParseAura(JsonObject o) => new(o.Float("radius"), o.Float("rate"));

        /// <summary>
        /// Prompt 13 C.2: seconds from empty to fully loaded at the holding pattern's full rate when the
        /// data gives none: helicopters and drones 8.5, fighters 11, attack jets 14, bombers 21.
        /// </summary>
        private static float DefaultRearm(VehicleDef def)
        {
            if (!def.Flying) return 0f;
            if (!def.FixedWing || def.Drone) return 8.5f;
            if (def.Interceptor) return 11f;
            return def.Weapon.Projectile == ProjectileKind.Bomb ? 21f : 14f;
        }

        /// <summary>A sensible class for vehicles whose data does not name one.</summary>
        private static UnitClass InferClass(VehicleDef def)
        {
            if (def.Boss) return UnitClass.Boss;
            if (def.Static) return UnitClass.Defense;
            if (def.Flying) return def.FixedWing ? UnitClass.Plane : UnitClass.Helicopter;
            var weapon = def.Weapon;
            if (weapon.MinRange > 0f) return UnitClass.Artillery;
            if (!weapon.CanTarget(false) || weapon.DamageType == DamageType.Fragmentation) return UnitClass.AntiAir;
            if (def.Armor == ArmorClass.Heavy) return def.MaxHp >= 1400f ? UnitClass.Heavy : UnitClass.Tank;
            return def.Speed >= 11f ? UnitClass.Scout : UnitClass.Light;
        }

        /// <summary>Parses <c>balance.json</c>. Throws <see cref="FormatException"/> naming the bad field.</summary>
        public static Catalog FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "balance");

            var damage = root.Has("damageTable") ? ParseDamageTable(root.Object("damageTable")) : DamageTable.Default;

            // Global tuning, one place for the whole roster: "toughness" multiplies every vehicle's
            // health (bosses separately), "firepower" the damage of strikes and of blasts (burning
            // props, vehicles blowing up, mines), "economy" every side's income and supply line.
            float Tune(string section, string key) => root.Has(section) ? root.Object(section).Float(key, 1f) : 1f;
            var vehicleHp = Tune("toughness", "vehicles");
            var bossHp = Tune("toughness", "bosses");
            var strikeDamage = Tune("firepower", "strikes");
            var propBlasts = Tune("firepower", "propBlasts");
            var vehicleBlasts = Tune("firepower", "vehicleBlasts");

            var weapons = new Dictionary<string, WeaponDef>();
            foreach (var w in Inherited(root.Array("weapons"), model: false))
            {
                var def = Wrap(w, () => new WeaponDef(
                    w.String("id"), w.Enum<DamageType>("damageType"), w.Float("damage"), w.Float("cooldown"),
                    w.Float("range"), w.Float("minRange", 0f), w.Float("projectileSpeed"), w.Float("splash", 0f),
                    w.Float("spread", 0f), w.Enum<ExplosionTier>("impactTier"),
                    w.Enum("projectile", ProjectileKind.Shell), w.Int("burst", 1), w.Float("burstInterval", 0.1f),
                    w.Enum("targets", TargetLayers.Ground))
                {
                    Ammo = w.Int("ammo", 0), Reload = w.Float("reload", 0f), ImpactScale = w.Float("impactScale", 1f), Load = w.Int("load", 0),
                    Pierce = w.Bool("pierce", false), Beam = w.Bool("beam", false), Melee = w.Bool("melee", false),
                    InterceptOnly = w.Bool("interceptOnly", false),
                    ProjectileModel = w.Has("projectileModel") ? w.String("projectileModel") : null,
                    ProjectileScale = w.Float("projectileScale", 1f),
                    Charge = w.Float("charge", 0f), FlareResist = Math.Clamp(w.Float("flareResist", 0f), 0f, 1f),
                    Family = w.Has("family") ? w.String("family") : null, Size = w.Float("size", 0f),
                    RealName = w.Has("real") ? w.String("real") : null,
                    Clip = w.Int("clip", 0), ClipReload = w.Float("clipReload", 0f), RoundWeight = w.Float("roundWeight", 0f),
                    // Prompt 15: penetration, the top-attack and thermobaric tags, the round's shape, its impact's look.
                    TopAttack = w.Bool("topAttack", false), Thermobaric = w.Bool("thermobaric", false), PiercingLook = w.Bool("piercing", false),
                    Laid = w.Bool("laid", false),
                });
                if (w.Has("pen"))
                {
                    var pen = w.Int("pen", 0);
                    if (pen < 0 || pen > ArmourLevels.Max) throw new FormatException($"{w.Path}.pen: a penetration level 0 to {ArmourLevels.Max}.");
                    def.Penetration = pen;
                }
                if (w.Has("form")) def.Form = w.Enum<WeaponForm>("form");
                ParseWeaponP17(w, def);
                ParseWeaponP19(w, def);
                if (def.Clip < 0 || def.ClipReload < 0f || (def.Clip > 0 && def.Burst > 1))
                    throw new FormatException($"{w.Path}: a magazine (clip) needs a single-round weapon (burst 1) and a clipReload of 0 or more.");
                if (w.Has("bonuses"))
                {
                    var bonuses = new List<DamageBonus>();
                    foreach (var b in w.Array("bonuses"))
                        bonuses.Add(new DamageBonus
                        {
                            Mult = b.Float("mult", 1f),
                            Class = b.Has("class") ? b.Enum<UnitClass>("class") : null,
                            Armor = b.Has("armor") ? b.Enum<ArmorClass>("armor") : null,
                            StillFor = b.Float("still", 0f),
                            Flank = b.Bool("flank", false),
                        });
                    def.Bonuses = bonuses;
                }
                if (w.Has("cluster"))
                {
                    var c = w.Object("cluster");
                    def.Cluster = new ClusterDef(c.Int("count", 4), c.Float("radius"),
                        new ExplosionDef(c.Float("damage"), c.Float("splash"), 0f, c.Enum("tier", ExplosionTier.Small)))
                    {
                        Penetration = Math.Clamp(c.Int("pen", ClusterDef.DefaultPenetration), 0, ArmourLevels.Max),
                    };
                }
                if (!weapons.TryAdd(def.Id, def)) throw new FormatException($"{w.Path}: duplicate weapon '{def.Id}'.");
            }
            ResolveHeRounds(Inherited(root.Array("weapons"), model: false), weapons);
            ResolveAirRounds(Inherited(root.Array("weapons"), model: false), weapons);

            var skills = new Dictionary<string, SkillDef>();
            if (root.Has("skills"))
                foreach (var k in root.Array("skills"))
                {
                    var skill = Wrap(k, () => new SkillDef(k.String("id"), k.Enum<SkillKind>("kind"),
                        k.Enum("trigger", SkillTrigger.Always), k.Float("threshold", 0f), k.Float("cooldown", 0f),
                        k.Float("duration", 0f), k.Float("amount", 0f), k.Float("radius", 0f), k.Int("count", 0),
                        k.Has("unit") ? k.String("unit") : null, k.Bool("once", false)));
                    if (!skills.TryAdd(skill.Id, skill)) throw new FormatException($"{k.Path}: duplicate skill '{skill.Id}'.");
                }

            var vehicles = new List<VehicleDef>();
            var ownBranches = new Dictionary<string, ArmyBranch?>();
            // Prompt 20 E: bosses built from their frames, the part library, their variants and ranks.
            foreach (var v in BossTemplates.Expand(root, Inherited(root.Array("vehicles"), model: true)))
            {
                var weapon = Weapon(weapons, v, "weapon");
                var secondary = new List<WeaponMount>();
                if (v.Has("secondary"))
                {
                    foreach (var m in v.Array("secondary"))
                        secondary.Add(new WeaponMount(Weapon(weapons, m, "weapon"), m.String("slot"), m.Enum("aim", MountAim.Free))
                        {
                            ProjectileModel = m.Has("model") ? m.String("model") : null,
                            ArcCentre = m.Has("arc") ? m.FloatArray("arc")[0] * MathF.PI / 180f : 0f,
                            ArcHalf = m.Has("arc") && m.FloatArray("arc").Count > 1 ? Math.Clamp(m.FloatArray("arc")[1], 5f, 180f) * MathF.PI / 180f : 0f,
                        });
                }
                vehicles.Add(Wrap(v, () =>
                {
                    // "scale" resizes the drawn model and its hull (length, width) together. The radius
                    // (how far a shot or blast reaches it) stays as given: a bigger-drawn aircraft is
                    // not an easier target, a smaller-drawn tank not a harder one.
                    var scale = v.Float("scale", 1f);
                    var def = new VehicleDef(
                        v.String("id"), v.Enum("armor", v.Bool("flying", false) ? ArmorClass.Air : ArmorClass.Light), v.Float("hp") * (v.Bool("boss", false) ? bossHp : vehicleHp),
                        v.Float("speed"), v.Float("turnRate"), v.Float("turretTurnRate"), v.Float("radius"), v.Int("cp", 0), v.Float("vision"),
                        v.Bool("firesWhileMoving", true), weapon, ParseExplosion(v, "deathExplosion", vehicleBlasts), secondary,
                        v.Bool("flying", false), v.Float("altitude", 0f), v.Float("captureRate", 1f),
                        v.Has("mainSlot") ? v.String("mainSlot") : "main", v.Bool("fixedWing", false), v.Bool("static", false));
                    if (v.Has("model")) def.Model = v.String("model");
                    if (v.Has("mainModel")) def.Mounts[0].ProjectileModel = v.String("mainModel");
                    def.Boss = v.Bool("boss", false);
                    // Prompt 15 A: armour levels ("armour": the front, or [front, side, rear, top]); a fixed defence
                    // that is no boss is a structure unless the data says otherwise; the broad class follows.
                    var structure = v.Bool("structure", def.Static && !def.Boss ? true : v.Has("armor") && v.Enum<ArmorClass>("armor") == ArmorClass.Structure);
                    if (v.Has("armour")) def.SetArmour(Levels(v, "armour", def.Flying || structure), structure);
                    else def.SetArmour(structure ? ArmourLevels.Uniform(2) : def.Armour, structure);
                    def.Card = v.Bool("card", true);
                    def.Elite = v.Bool("elite", false);
                    def.EliteOf = v.Has("eliteOf") ? v.String("eliteOf") : null;
                    def.ArmyCost = def.CpCost;
                    def.Scale = scale;
                    if (v.Has("length")) def.Length = v.Float("length") * scale;
                    if (v.Has("width")) def.Width = v.Float("width") * scale;
                    def.Class = v.Has("class") ? v.Enum<UnitClass>("class") : InferClass(def);
                    if (v.Has("strongVs"))
                    {
                        var list = new List<UnitClass>();
                        foreach (var name in v.StringArray("strongVs")) list.Add((UnitClass)Enum.Parse(typeof(UnitClass), name));
                        def.StrongVs = list;
                    }
                    if (v.Has("skills"))
                    {
                        var list = new List<SkillDef>();
                        foreach (var id in v.StringArray("skills"))
                            list.Add(skills.TryGetValue(id, out var skill) ? skill : throw new FormatException($"{v.Path}.skills: unknown skill '{id}'."));
                        def.Skills = list;
                    }
                    if (v.Has("phases"))
                    {
                        var phases = new List<BossPhaseDef>();
                        foreach (var p in v.Array("phases"))
                        {
                            var phaseSkills = new List<SkillDef>();
                            if (p.Has("skills"))
                                foreach (var id in p.StringArray("skills"))
                                    phaseSkills.Add(skills.TryGetValue(id, out var skill) ? skill : throw new FormatException($"{p.Path}.skills: unknown skill '{id}'."));
                            phases.Add(new BossPhaseDef
                            {
                                At = p.Float("at"), Transform = p.Float("transform", 3f), Heal = p.Float("heal", 0f),
                                Damage = p.Float("damage", 1f), Speed = p.Float("speed", 1f), Armor = p.Float("armor", 1f),
                                Skills = phaseSkills, Model = p.Has("model") ? p.String("model") : null, Radio = p.Has("radio") ? p.String("radio") : null,
                            });
                        }
                        phases.Sort((a, b) => b.At.CompareTo(a.At));
                        def.Phases = phases;
                    }
                    if (v.Has("general")) def.General = v.String("general");
                    if (v.Has("repair")) def.RepairAura = ParseAura(v.Object("repair"));
                    if (v.Has("rearm")) def.RearmAura = ParseAura(v.Object("rearm"));
                    // Prompt 13 F.2: an ammunition carrier: helicopters beside it rearm twice as fast.
                    if (v.Has("airRearm")) def.AirRearm = ParseAura(v.Object("airRearm"));
                    def.Jammer = v.Float("jammer", 0f);
                    if (v.Has("mainAim")) def.AimMain(v.Enum<MountAim>("mainAim"));
                    def.Orbit = v.Bool("orbit", false);
                    def.OrbitRadius = v.Float("orbitRadius", 0f);
                    def.Stealth = v.Bool("stealth", false);
                    def.Interceptor = v.Bool("interceptor", false);
                    def.Vtol = v.Bool("vtol", false);
                    def.AttackHold = def.FixedWing ? v.Float("attackHold", 0f) : 0f;
                    // Prompt 13 C: an aircraft's stores per full load and how long they take to come back.
                    if (v.Has("loads"))
                    {
                        var loads = new Dictionary<string, int>();
                        var o = v.Object("loads");
                        foreach (var key in o.Keys) loads[key] = o.Int(key, 0);
                        def.Loads = loads;
                    }
                    def.RearmTime = v.Float("rearmTime", DefaultRearm(def));
                    def.CombatValue = v.Float("value", 1f);
                    def.Kamikaze = v.Bool("kamikaze", false);
                    def.DroneArmor = v.Float("droneArmor", 1f);
                    def.MineProof = v.Bool("mineProof", false);
                    if (v.Has("fortify")) def.FortifyAura = ParseAura(v.Object("fortify"));
                    if (v.Has("fort"))
                    {
                        var f = v.Object("fort");
                        def.Fort = new FortDef(f.Enum("size", SlotSize.Small), f.Enum("kind", FortKind.Tower))
                        {
                            Tier = f.Int("tier", 1),
                        };
                    }
                    if (v.Has("aps"))
                    {
                        var a = v.Object("aps");
                        // Prompt 20 L.1: a launcher reloaded whole ("reload") needs no one-at-a-time "recharge".
                        var reload = a.Float("reload", 0f);
                        def.Aps = new ApsDef(a.Float("radius"), a.Int("charges", 2), reload > 0f ? a.Float("recharge", reload) : a.Float("recharge"))
                        {
                            Rockets = a.Bool("rockets", false), Shells = a.Float("shells", 0f), Laser = a.Bool("laser", false),
                            Reload = reload, Direct = a.Bool("direct", true), Missiles = a.Bool("missiles", false), Heavy = a.Bool("heavy", false),
                            Burst = Math.Max(0f, a.Float("burst", 0f)),
                        };
                    }
                    if (v.Has("commandAura"))
                    {
                        var c = v.Object("commandAura");
                        def.CommandAura = new CommandAuraDef(c.Float("radius"), c.Float("fireRate"), c.Float("damage", 0f));
                    }
                    if (v.Has("counterBattery"))
                    {
                        var c = v.Object("counterBattery");
                        def.CounterBattery = new CounterBatteryDef(c.Float("range"), c.Float("seconds"), c.Float("bonus", 0f));
                    }
                    def.ForwardDrop = v.Float("forwardDrop", 0f);
                    def.BranchOf = v.Has("branchOf") ? v.String("branchOf") : null;
                    def.MaxPerSide = v.Int("maxPerSide", 0);
                    def.Standoff = v.Bool("standoff", false);
                    def.Obstacle = v.Bool("obstacle", false);
                    def.Untargetable = v.Bool("untargetable", false);
                    def.Passable = v.Bool("passable", false);
                    def.RevealStealth = v.Bool("revealStealth", false);
                    def.Drone = v.Bool("drone", false);
                    if (v.Has("towerRangeAura"))
                    {
                        var a = v.Object("towerRangeAura");
                        def.TowerRangeAura = new AuraDef(a.Float("radius"), a.Float("range"));
                    }
                    if (v.Has("slowAura"))
                    {
                        var a = v.Object("slowAura");
                        def.SlowAura = new AuraDef(a.Float("radius"), a.Float("share"));
                    }
                    if (v.Has("hidden"))
                    {
                        var h = v.Object("hidden");
                        def.Hidden = new HiddenDef(h.Float("rise"), h.Float("cut", 0.6f), h.Float("firstShot", 1f));
                    }
                    if (v.Has("utility"))
                    {
                        var u = v.Object("utility");
                        def.Utility = new UtilityDef
                        {
                            Repair = u.Float("repair", 0f), Rearm = u.Float("rearm", 0f), AirRepair = u.Float("airRepair", 0f),
                            AirRearm = u.Float("airRearm", 1f), AirCap = u.Int("airCap", 0),
                            AirReach = u.Float("airReach", 14f), Supply = u.Int("supply", 0), RevealBase = u.Bool("revealBase", false),
                        };
                    }
                    if (v.Has("mines"))
                    {
                        var m = v.Object("mines");
                        def.Mines = new MineLayerDef(m.Float("interval"), m.Int("max", 6),
                            new ExplosionDef(m.Float("damage") * vehicleBlasts, m.Float("radius"), 0f, m.Enum("tier", ExplosionTier.Large)),
                            m.Float("trigger", 2f)) { Spread = m.Float("spread", 0f) };
                    }
                    ParseExtras(v, def);
                    ParseNaval(v, def);
                    if (v.Has("branch")) ownBranches[def.Id] = v.Enum<ArmyBranch>("branch");
                    return def;
                }));
            }

            var props = new List<PropDef>();
            foreach (var p in root.Array("props"))
            {
                var propScale = p.Float("scale", 1f);
                props.Add(Wrap(p, () => new PropDef(
                    p.String("id"), p.Enum<ArmorClass>("armor"), p.Float("hp"), p.Float("width") * propScale, p.Float("depth") * propScale,
                    p.Bool("blocks", false), ParseExplosion(p, "explosion", propBlasts), p.Has("blocksFire") ? p.Bool("blocksFire", true) : null)
                { Scale = propScale, Crushable = p.Bool("crush", false), Collapse = p.Float("collapse", 0f) }));
                // Prompt 15 A.3: a prop's armour level, the same all round.
                if (p.Has("armour")) props[props.Count - 1].Armour = Levels(p, "armour", allRound: true);
            }

            var supports = new List<SupportDef>();
            if (root.Has("supports"))
            {
                foreach (var s in root.Array("supports"))
                {
                    supports.Add(Wrap(s, () => new SupportDef(
                        s.String("id"), s.Enum<SupportKind>("kind"), s.Int("cp", 0), s.Float("cooldown"), s.Float("delay", 1.5f),
                        s.Float("radius"), s.Int("count", 1), s.Float("duration", 0f), s.Float("damage", 0f) * strikeDamage,
                        s.Enum("damageType", DamageType.HighExplosive), s.Enum("tier", ExplosionTier.Large), s.Float("length", 0f),
                        s.Float("blast", 0f))
                    {
                        Penetration = s.Int("pen", -1),
                        Thermobaric = s.Bool("thermobaric", false),
                        Consumable = s.Bool("consumable", false),
                        EventOnly = s.Bool("event", false),
                        Units = s.Has("units") ? s.StringArray("units") : Array.Empty<string>(),
                        UnitRank = s.Int("unitRank", 0),
                        LineRank = s.Has("rankLine") ? s.Object("rankLine").Int("rank", 0) : 0,
                        LineScale = s.Has("rankLine") ? s.Object("rankLine").Float("scale", 1f) : 1f,
                    }));
                }
            }

            var catalog = new Catalog(root.Int("version", 1), damage, weapons.Values, vehicles, props, supports)
            {
                IncomeScale = Tune("economy", "income"),
                SupplyScale = Tune("economy", "supply"),
                EnemyScaling = Tune("economy", "enemyScaling"),
                ArmyCaps = ReadArmyCaps(root),
                VehicleCaps = ReadCaps(root, "vehicleCap", 32),
                Base = root.Has("base") ? BaseRules.Parse(root.Object("base")) : new BaseRules(),
            };
            catalog.FinishExtras(root, ownBranches);
            catalog.CheckNaval();
            return catalog;
        }

        /// <summary>
        /// Vehicle entries with "inherits" (a tower's rank-7 branch) take the named def's fields,
        /// theirs on top; the parent's model too, unless they name their own. In data order.
        /// </summary>
        private static IEnumerable<JsonObject> Inherited(IEnumerable<JsonObject> entries, bool model)
        {
            var list = new List<JsonObject>(entries);
            var byId = new Dictionary<string, JsonObject>();
            foreach (var v in list)
                if (v.Has("id")) byId[v.String("id")] = v;
            JsonObject Resolve(JsonObject v, int depth)
            {
                if (!v.Has("inherits")) return v;
                if (depth > 4) throw new FormatException($"{v.Path}: inherits too deep");
                var parentId = v.String("inherits");
                if (!byId.TryGetValue(parentId, out var parent)) throw new FormatException($"{v.Path}.inherits: unknown vehicle '{parentId}'");
                var baseDef = Resolve(parent, depth + 1);
                var merged = baseDef.Under(v);
                if (model && !v.Has("model") && !baseDef.Has("model")) merged = merged.With("model", parentId);
                return merged;
            }
            foreach (var v in list) yield return Resolve(v, 0);
        }

        private static Dictionary<string, int> ReadCaps(JsonObject root, string key, int fallback)
        {
            var caps = new Dictionary<string, int>();
            if (!root.Has("economy") || !root.Object("economy").Has(key)) return caps;
            var o = root.Object("economy").Object(key);
            foreach (var k in o.Keys) caps[k] = o.Int(k, fallback);
            return caps;
        }

        private static Dictionary<string, int> ReadArmyCaps(JsonObject root)
        {
            var caps = new Dictionary<string, int>();
            if (!root.Has("economy") || !root.Object("economy").Has("armyCap")) return caps;
            var o = root.Object("economy").Object("armyCap");
            foreach (var key in o.Keys) caps[key] = o.Int(key, 24);
            return caps;
        }

        private static WeaponDef Weapon(Dictionary<string, WeaponDef> weapons, JsonObject owner, string key)
        {
            var id = owner.String(key);
            return weapons.TryGetValue(id, out var weapon)
                ? weapon
                : throw new FormatException($"{owner.Path}.{key}: unknown weapon '{id}'.");
        }

        private static ExplosionDef? ParseExplosion(JsonObject owner, string key, float damageScale = 1f)
        {
            if (!owner.Has(key)) return null;
            var e = owner.Object(key);
            return Wrap(e, () => new ExplosionDef(e.Float("damage") * damageScale, e.Float("radius"), e.Float("delay", 0f),
                e.Enum<ExplosionTier>("tier")));
        }

        /// <summary>
        /// Prompt 15: the damage-type table (a row per type: Ground, Air, Structure), the penetration row
        /// ("penetration": above, level, -1, -2, -3) and the thermobaric tag's structure multiplier.
        /// </summary>
        private static DamageTable ParseDamageTable(JsonObject table)
        {
            var damageTypes = (DamageType[])Enum.GetValues(typeof(DamageType));
            var kinds = (TargetKind[])Enum.GetValues(typeof(TargetKind));
            var values = new float[damageTypes.Length, kinds.Length];
            foreach (var d in damageTypes)
            {
                var row = table.Object(d.ToString());
                foreach (var k in kinds) values[(int)d, (int)k] = row.Float(k.ToString());
            }
            float[]? pen = null;
            if (table.Has("penetration"))
            {
                var list = table.FloatArray("penetration");
                pen = new float[list.Count];
                for (var i = 0; i < list.Count; i++) pen[i] = list[i];
            }
            return Wrap(table, () => new DamageTable(values, pen, table.Float("thermobaric", 2f)));
        }

        /// <summary>
        /// Armour levels from data: one number (the front; with <paramref name="allRound"/> the same all round,
        /// else the side one less and the rear and roof two less) or four [front, side, rear, top].
        /// </summary>
        internal static ArmourLevels Levels(JsonObject o, string key, bool allRound)
        {
            if (o.IsArray(key))
            {
                var a = o.FloatArray(key);
                if (a.Count != 4) throw new FormatException($"{o.Path}.{key}: one level or four [front, side, rear, top].");
                foreach (var x in a)
                    if (x < 0f || x > ArmourLevels.Max || x != MathF.Round(x)) throw new FormatException($"{o.Path}.{key}: whole levels 0 to {ArmourLevels.Max}.");
                return new ArmourLevels((int)a[0], (int)a[1], (int)a[2], (int)a[3]);
            }
            var front = o.Int(key, 0);
            if (front < 0 || front > ArmourLevels.Max) throw new FormatException($"{o.Path}.{key}: a level 0 to {ArmourLevels.Max}.");
            return allRound ? ArmourLevels.Uniform(front) : ArmourLevels.Vehicle(front);
        }

        /// <summary>Re-throws definition validation errors with the JSON path attached.</summary>
        private static T Wrap<T>(JsonObject source, Func<T> create)
        {
            try
            {
                return create();
            }
            catch (ArgumentException e)
            {
                throw new FormatException($"{source.Path}: {e.Message}", e);
            }
        }

        private static Dictionary<string, T> Index<T>(IEnumerable<T> items, Func<T, string> key, string kind)
        {
            var result = new Dictionary<string, T>();
            foreach (var item in items)
                if (!result.TryAdd(key(item), item)) throw new ArgumentException($"Duplicate {kind} '{key(item)}'.");
            return result;
        }
    }
}

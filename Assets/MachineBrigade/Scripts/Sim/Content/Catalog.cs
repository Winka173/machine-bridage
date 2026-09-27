#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Every definition a match can use, resolved and validated up front so the simulation
    /// never meets a dangling id mid-battle.
    /// </summary>
    public sealed class Catalog
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
                if (v.EliteOf == null || !_vehicles.TryGetValue(v.EliteOf, out var original)) continue;
                v.ArmyCost = original.CpCost;
                _elites[v.EliteOf] = v.Id;
            }
        }

        private readonly Dictionary<string, string> _elites = new();

        /// <summary>The elite version of a vehicle, if it has one.</summary>
        public string? EliteVariant(string vehicleId) => _elites.TryGetValue(vehicleId, out var elite) ? elite : null;

        /// <summary>Balance version, recorded with results so tuning changes stay traceable.</summary>
        public int Version { get; }

        /// <summary>Multiplies every side's CP income, objective bonuses included (balance.json "economy.income").</summary>
        public float IncomeScale { get; internal set; } = 1f;

        /// <summary>Multiplies every side's supply line, the army kept up at full income ("economy.supply").</summary>
        public float SupplyScale { get; internal set; } = 1f;

        public DamageTable Damage { get; }

        public IReadOnlyDictionary<string, WeaponDef> Weapons => _weapons;
        public IReadOnlyDictionary<string, VehicleDef> Vehicles => _vehicles;
        public IReadOnlyDictionary<string, PropDef> Props => _props;
        public IReadOnlyDictionary<string, SupportDef> Supports => _supports;

        public bool TryGetSupport(string id, out SupportDef support) => _supports.TryGetValue(id, out support!);

        public VehicleDef Vehicle(string id) =>
            _vehicles.TryGetValue(id, out var def) ? def : throw new KeyNotFoundException($"Unknown vehicle '{id}'.");

        public PropDef Prop(string id) =>
            _props.TryGetValue(id, out var def) ? def : throw new KeyNotFoundException($"Unknown prop '{id}'.");

        private static AuraDef ParseAura(JsonObject o) => new(o.Float("radius"), o.Float("rate"));

        /// <summary>A sensible class for vehicles whose data does not name one.</summary>
        private static UnitClass InferClass(VehicleDef def)
        {
            if (def.Boss) return UnitClass.Boss;
            if (def.Static) return UnitClass.Defense;
            if (def.Flying) return def.FixedWing ? UnitClass.Plane : UnitClass.Helicopter;
            var weapon = def.Weapon;
            if (weapon.MinRange > 0f) return UnitClass.Artillery;
            if (!weapon.CanTarget(false) || weapon.DamageType == DamageType.Flak) return UnitClass.AntiAir;
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
            foreach (var w in root.Array("weapons"))
            {
                var def = Wrap(w, () => new WeaponDef(
                    w.String("id"), w.Enum<DamageType>("damageType"), w.Float("damage"), w.Float("cooldown"),
                    w.Float("range"), w.Float("minRange", 0f), w.Float("projectileSpeed"), w.Float("splash", 0f),
                    w.Float("spread", 0f), w.Enum<ExplosionTier>("impactTier"),
                    w.Enum("projectile", ProjectileKind.Shell), w.Int("burst", 1), w.Float("burstInterval", 0.1f),
                    w.Enum("targets", TargetLayers.Ground))
                {
                    Ammo = w.Int("ammo", 0), Reload = w.Float("reload", 0f), ImpactScale = w.Float("impactScale", 1f),
                });
                if (w.Has("cluster"))
                {
                    var c = w.Object("cluster");
                    def.Cluster = new ClusterDef(c.Int("count", 4), c.Float("radius"),
                        new ExplosionDef(c.Float("damage"), c.Float("splash"), 0f, c.Enum("tier", ExplosionTier.Small)));
                }
                if (!weapons.TryAdd(def.Id, def)) throw new FormatException($"{w.Path}: duplicate weapon '{def.Id}'.");
            }

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
            foreach (var v in root.Array("vehicles"))
            {
                var weapon = Weapon(weapons, v, "weapon");
                var secondary = new List<WeaponMount>();
                if (v.Has("secondary"))
                {
                    foreach (var m in v.Array("secondary"))
                        secondary.Add(new WeaponMount(Weapon(weapons, m, "weapon"), m.String("slot"), m.Enum("aim", MountAim.Free)));
                }
                vehicles.Add(Wrap(v, () =>
                {
                    // "scale" resizes the drawn model and its hull (length, width) together. The radius
                    // (how far a shot or blast reaches it) stays as given: a bigger-drawn aircraft is
                    // not an easier target, a smaller-drawn tank not a harder one.
                    var scale = v.Float("scale", 1f);
                    var def = new VehicleDef(
                        v.String("id"), v.Enum<ArmorClass>("armor"), v.Float("hp") * (v.Bool("boss", false) ? bossHp : vehicleHp),
                        v.Float("speed"), v.Float("turnRate"), v.Float("turretTurnRate"), v.Float("radius"), v.Int("cp", 0), v.Float("vision"),
                        v.Bool("firesWhileMoving", true), weapon, ParseExplosion(v, "deathExplosion", vehicleBlasts), secondary,
                        v.Bool("flying", false), v.Float("altitude", 0f), v.Float("captureRate", 1f),
                        v.Has("mainSlot") ? v.String("mainSlot") : "main", v.Bool("fixedWing", false), v.Bool("static", false));
                    if (v.Has("model")) def.Model = v.String("model");
                    def.Boss = v.Bool("boss", false);
                    def.Elite = v.Bool("elite", false);
                    def.EliteOf = v.Has("eliteOf") ? v.String("eliteOf") : null;
                    def.ArmyCost = def.CpCost;
                    def.Scale = scale;
                    if (v.Has("length")) def.Length = v.Float("length") * scale;
                    if (v.Has("width")) def.Width = v.Float("width") * scale;
                    def.Class = v.Has("class") ? v.Enum<UnitClass>("class") : InferClass(def);
                    if (v.Has("skills"))
                    {
                        var list = new List<SkillDef>();
                        foreach (var id in v.StringArray("skills"))
                            list.Add(skills.TryGetValue(id, out var skill) ? skill : throw new FormatException($"{v.Path}.skills: unknown skill '{id}'."));
                        def.Skills = list;
                    }
                    if (v.Has("repair")) def.RepairAura = ParseAura(v.Object("repair"));
                    if (v.Has("rearm")) def.RearmAura = ParseAura(v.Object("rearm"));
                    def.Jammer = v.Float("jammer", 0f);
                    if (v.Has("aps"))
                    {
                        var a = v.Object("aps");
                        def.Aps = new ApsDef(a.Float("radius"), a.Int("charges", 2), a.Float("recharge"));
                    }
                    if (v.Has("mines"))
                    {
                        var m = v.Object("mines");
                        def.Mines = new MineLayerDef(m.Float("interval"), m.Int("max", 6),
                            new ExplosionDef(m.Float("damage") * vehicleBlasts, m.Float("radius"), 0f, m.Enum("tier", ExplosionTier.Large)),
                            m.Float("trigger", 2f));
                    }
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
                { Scale = propScale, Crushable = p.Bool("crush", false) }));
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
                        Consumable = s.Bool("consumable", false),
                        EventOnly = s.Bool("event", false),
                        Units = s.Has("units") ? s.StringArray("units") : Array.Empty<string>(),
                    }));
                }
            }

            return new Catalog(root.Int("version", 1), damage, weapons.Values, vehicles, props, supports)
            {
                IncomeScale = Tune("economy", "income"),
                SupplyScale = Tune("economy", "supply"),
            };
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

        private static DamageTable ParseDamageTable(JsonObject table)
        {
            var damageTypes = (DamageType[])Enum.GetValues(typeof(DamageType));
            var armorClasses = (ArmorClass[])Enum.GetValues(typeof(ArmorClass));
            var values = new float[damageTypes.Length, armorClasses.Length];
            foreach (var d in damageTypes)
            {
                var row = table.Object(d.ToString());
                foreach (var a in armorClasses) values[(int)d, (int)a] = row.Float(a.ToString());
            }
            return new DamageTable(values);
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

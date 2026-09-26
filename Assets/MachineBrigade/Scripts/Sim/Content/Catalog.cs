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
        }

        /// <summary>Balance version, recorded with results so tuning changes stay traceable.</summary>
        public int Version { get; }

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

        /// <summary>Parses <c>balance.json</c>. Throws <see cref="FormatException"/> naming the bad field.</summary>
        public static Catalog FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "balance");

            var damage = root.Has("damageTable") ? ParseDamageTable(root.Object("damageTable")) : DamageTable.Default;

            var weapons = new Dictionary<string, WeaponDef>();
            foreach (var w in root.Array("weapons"))
            {
                var def = Wrap(w, () => new WeaponDef(
                    w.String("id"), w.Enum<DamageType>("damageType"), w.Float("damage"), w.Float("cooldown"),
                    w.Float("range"), w.Float("minRange", 0f), w.Float("projectileSpeed"), w.Float("splash", 0f),
                    w.Float("spread", 0f), w.Enum<ExplosionTier>("impactTier"),
                    w.Enum("projectile", ProjectileKind.Shell), w.Int("burst", 1), w.Float("burstInterval", 0.1f),
                    w.Enum("targets", TargetLayers.Ground)));
                if (!weapons.TryAdd(def.Id, def)) throw new FormatException($"{w.Path}: duplicate weapon '{def.Id}'.");
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
                vehicles.Add(Wrap(v, () => new VehicleDef(
                    v.String("id"), v.Enum<ArmorClass>("armor"), v.Float("hp"), v.Float("speed"), v.Float("turnRate"),
                    v.Float("turretTurnRate"), v.Float("radius"), v.Int("cp", 0), v.Float("vision"),
                    v.Bool("firesWhileMoving", true), weapon, ParseExplosion(v, "deathExplosion"), secondary,
                    v.Bool("flying", false), v.Float("altitude", 0f), v.Float("captureRate", 1f),
                    v.Has("mainSlot") ? v.String("mainSlot") : "main")));
            }

            var props = new List<PropDef>();
            foreach (var p in root.Array("props"))
            {
                props.Add(Wrap(p, () => new PropDef(
                    p.String("id"), p.Enum<ArmorClass>("armor"), p.Float("hp"), p.Float("width"), p.Float("depth"),
                    p.Bool("blocks", false), ParseExplosion(p, "explosion"))));
            }

            var supports = new List<SupportDef>();
            if (root.Has("supports"))
            {
                foreach (var s in root.Array("supports"))
                {
                    supports.Add(Wrap(s, () => new SupportDef(
                        s.String("id"), s.Enum<SupportKind>("kind"), s.Int("cp", 0), s.Float("cooldown"), s.Float("delay", 1.5f),
                        s.Float("radius"), s.Int("count", 1), s.Float("duration", 0f), s.Float("damage", 0f),
                        s.Enum("damageType", DamageType.HighExplosive), s.Enum("tier", ExplosionTier.Large), s.Float("length", 0f),
                        s.Float("blast", 0f))));
                }
            }

            return new Catalog(root.Int("version", 1), damage, weapons.Values, vehicles, props, supports);
        }

        private static WeaponDef Weapon(Dictionary<string, WeaponDef> weapons, JsonObject owner, string key)
        {
            var id = owner.String(key);
            return weapons.TryGetValue(id, out var weapon)
                ? weapon
                : throw new FormatException($"{owner.Path}.{key}: unknown weapon '{id}'.");
        }

        private static ExplosionDef? ParseExplosion(JsonObject owner, string key)
        {
            if (!owner.Has(key)) return null;
            var e = owner.Object(key);
            return Wrap(e, () => new ExplosionDef(e.Float("damage"), e.Float("radius"), e.Float("delay", 0f),
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

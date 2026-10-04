#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// MB_FINAL F2 (owner's final balance bundle, DECISIONS "MB_FINAL balance F2 (lane B)"): one boss's own reach for one of its
    /// weapons, balance.json "bossWeaponOverrides": { "&lt;boss id&gt;": { "&lt;weapon id&gt;": { "groundMinReach", "minRange",
    /// "maxRange" } } }. A field left out keeps the weapon's own value.
    /// </summary>
    public sealed class BossWeaponOverride
    {
        /// <summary>No shot at a ground target nearer than this, measured to its near face (WeaponDef.GroundMinReach); null: the weapon's.</summary>
        public float? GroundMinReach { get; internal set; }

        /// <summary>
        /// The weapon's minimum range. Only a weapon that already has one (an indirect weapon: artillery, lobbed rockets) takes it
        /// as its MinRange; on a direct-fire weapon it is folded into <see cref="GroundMinReach"/> (the larger of the two), because
        /// MinRange &gt; 0 would make the gun indirect (WeaponDef.Indirect: no line of fire, the artillery role for the AI).
        /// </summary>
        public float? MinRange { get; internal set; }

        /// <summary>The weapon's reach (WeaponDef.Range); a ground reach of its own (GroundRange) is scaled with it. Null: the weapon's.</summary>
        public float? MaxRange { get; internal set; }
    }

    public sealed partial class WeaponDef
    {
        /// <summary>
        /// MB_FINAL F2: a copy of this weapon (every field, the same id, so it looks and sounds the same) with one boss's own
        /// reach: the shared definition is never changed. See <see cref="BossWeaponOverride"/> for the fields.
        /// </summary>
        internal WeaponDef WithReach(BossWeaponOverride o, string path)
        {
            var copy = (WeaponDef)MemberwiseClone();
            if (o.MaxRange is { } max)
            {
                if (GroundRange > 0f) copy.GroundRange = MathF.Min(max, GroundRange * max / Range);
                copy.Range = max;
            }
            if (o.GroundMinReach is { } reach) copy.GroundMinReach = reach;
            if (o.MinRange is { } min)
            {
                if (MinRange > 0f) copy.MinRange = min;
                else copy.GroundMinReach = MathF.Max(copy.GroundMinReach, min);
            }
            if (copy.MinRange >= copy.Range) throw new FormatException($"{path}: minRange {copy.MinRange} must be below the reach {copy.Range}.");
            if (copy.GroundMinReach >= copy.Range) throw new FormatException($"{path}: groundMinReach {copy.GroundMinReach} must be below the reach {copy.Range}.");
            return copy;
        }
    }

    /// <summary>
    /// MB_FINAL F2: the "bossWeaponOverrides" table while the catalog builds the bosses. A boss's row for a weapon is used for every
    /// mount of that weapon on that boss; a variant ("variantOf") with no row of its own for a weapon takes its parent's row (then
    /// the grandparent's), whole: a variant's own row replaces its parent's, it does not merge with it. Bosses only; vehicles and
    /// towers carrying the same weapon keep the shared one.
    /// </summary>
    internal sealed class BossReachTable
    {
        private readonly Dictionary<string, Dictionary<string, BossWeaponOverride>> _rows = new(StringComparer.Ordinal);
        private readonly Dictionary<string, string> _parentOf = new(StringComparer.Ordinal);
        private readonly Dictionary<string, WeaponDef> _made = new(StringComparer.Ordinal);

        public int Count => _rows.Count;

        public static BossReachTable Parse(JsonObject root)
        {
            var table = new BossReachTable();
            if (!root.Has("bossWeaponOverrides")) return table;
            var all = root.Object("bossWeaponOverrides");
            foreach (var bossId in all.Keys)
            {
                var boss = all.Object(bossId);
                var rows = new Dictionary<string, BossWeaponOverride>(StringComparer.Ordinal);
                foreach (var weaponId in boss.Keys)
                {
                    var o = boss.Object(weaponId);
                    foreach (var key in o.Keys)
                        if (key is not ("groundMinReach" or "minRange" or "maxRange"))
                            throw new FormatException($"{o.Path}.{key}: a boss weapon override takes groundMinReach, minRange and maxRange only.");
                    var row = new BossWeaponOverride
                    {
                        GroundMinReach = o.Has("groundMinReach") ? o.Float("groundMinReach") : null,
                        MinRange = o.Has("minRange") ? o.Float("minRange") : null,
                        MaxRange = o.Has("maxRange") ? o.Float("maxRange") : null,
                    };
                    if (row.GroundMinReach < 0f || row.MinRange < 0f || row.MaxRange <= 0f)
                        throw new FormatException($"{o.Path}: groundMinReach and minRange 0 or more, maxRange above 0.");
                    rows[weaponId] = row;
                }
                table._rows[bossId] = rows;
            }
            return table;
        }

        /// <summary>A boss as the catalog meets it (parents come before their variants).</summary>
        public void Enter(string bossId, string? variantOf)
        {
            if (!string.IsNullOrEmpty(variantOf)) _parentOf[bossId] = variantOf!;
        }

        /// <summary>The row this boss uses for a weapon (its own, else its nearest ancestor's), or null.</summary>
        public BossWeaponOverride? Of(string bossId, string weaponId, out string? from)
        {
            var id = bossId;
            for (var depth = 0; depth < 8 && id != null; depth++)
            {
                if (_rows.TryGetValue(id, out var rows) && rows.TryGetValue(weaponId, out var row))
                {
                    from = id;
                    return row;
                }
                id = _parentOf.TryGetValue(id, out var parent) ? parent : null;
            }
            from = null;
            return null;
        }

        /// <summary>The weapon a mount of this boss fires: its own copy where the table has a row, else the weapon given.</summary>
        public WeaponDef Arm(string bossId, WeaponDef weapon)
        {
            var row = Of(bossId, weapon.Id, out var from);
            if (row == null) return weapon;
            var key = bossId + "/" + weapon.Id;
            if (_made.TryGetValue(key, out var made)) return made;
            made = weapon.WithReach(row, $"bossWeaponOverrides.{from}.{weapon.Id} (on {bossId})");
            _made[key] = made;
            return made;
        }

        /// <summary>Same as <see cref="Arm"/> without the shared copy: for a boss's own tuned copy (its "missiles" load).</summary>
        public WeaponDef Apply(string bossId, WeaponDef weapon)
        {
            var row = Of(bossId, weapon.Id, out var from);
            return row == null ? weapon : weapon.WithReach(row, $"bossWeaponOverrides.{from}.{weapon.Id} (on {bossId})");
        }

        /// <summary>Every row names a boss that carries the weapon (a stale row is an error, not a silent no-op).</summary>
        public void Check(IReadOnlyDictionary<string, WeaponDef> weapons, IEnumerable<VehicleDef> vehicles)
        {
            if (_rows.Count == 0) return;
            var bosses = new Dictionary<string, VehicleDef>(StringComparer.Ordinal);
            foreach (var v in vehicles)
                if (v.Boss) bosses[v.Id] = v;
            foreach (var pair in _rows)
            {
                if (!bosses.TryGetValue(pair.Key, out var boss))
                    throw new FormatException($"bossWeaponOverrides.{pair.Key}: no boss of that id.");
                foreach (var weaponId in pair.Value.Keys)
                {
                    if (!weapons.ContainsKey(weaponId))
                        throw new FormatException($"bossWeaponOverrides.{pair.Key}.{weaponId}: unknown weapon.");
                    var carried = false;
                    foreach (var m in boss.Mounts) carried |= m.Weapon.Id == weaponId;
                    if (!carried)
                        throw new FormatException($"bossWeaponOverrides.{pair.Key}.{weaponId}: the boss carries no '{weaponId}' (stale row?).");
                }
            }
        }
    }
}

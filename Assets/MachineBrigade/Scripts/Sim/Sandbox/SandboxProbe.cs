#nullable enable
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>One weapon as the Sandbox's overlays show it (prompt 21 E.1, E.4).</summary>
    public readonly struct SandboxWeapon
    {
        public SandboxWeapon(string id, float range, float minRange, bool air, int ammo, int full, float reloadLeft, float cooldown)
        {
            Id = id;
            Range = range;
            MinRange = minRange;
            Air = air;
            Ammo = ammo;
            Full = full;
            ReloadLeft = reloadLeft;
            Cooldown = cooldown;
        }

        public string Id { get; }
        public float Range { get; }
        public float MinRange { get; }

        /// <summary>It can shoot at aircraft.</summary>
        public bool Air { get; }

        /// <summary>Rounds left (-1 unlimited) of <see cref="Full"/> (0: no magazine).</summary>
        public int Ammo { get; }

        public int Full { get; }
        public float ReloadLeft { get; }
        public float Cooldown { get; }
    }

    /// <summary>
    /// Read-only views of a vehicle's inner state for the Sandbox's overlays (prompt 21 E): its weapons' reach and
    /// magazines exactly as the simulation has them (the overlays match the real data, part 3), its hull capsule,
    /// the route it is following, its resupply state, and a boss's big-attack zones and shield domes. Nothing here
    /// changes the battle.
    /// </summary>
    public static class SandboxProbe
    {
        public static List<SandboxWeapon> Weapons(Vehicle v)
        {
            var list = new List<SandboxWeapon>(v.Arms.Length);
            for (var i = 0; i < v.Arms.Length; i++)
            {
                var w = v.Arms[i];
                var s = v.Weapons[i];
                var full = s.Load > 0 ? s.Load : w.Ammo > 0 ? w.Ammo : 0;
                list.Add(new SandboxWeapon(w.Id, w.Range, w.MinRange, w.CanTarget(true), s.Ammo, full, s.ReloadLeft, s.Cooldown));
            }
            return list;
        }

        /// <summary>The widest reach and the largest dead zone of its weapons (the range rings).</summary>
        public static (float max, float min) Reach(Vehicle v)
        {
            var (max, min) = (0f, 0f);
            for (var i = 0; i < v.Arms.Length; i++)
            {
                if (v.Arms[i].Range > max) max = v.Arms[i].Range;
                if (v.Arms[i].MinRange > min) min = v.Arms[i].MinRange;
            }
            return (max, min);
        }

        /// <summary>Its resupply state's name (fighting, going back to rearm, rearming...).</summary>
        public static string Supply(Vehicle v) => v.HasStores ? v.Supply.ToString() : "";

        /// <summary>Its hull as a capsule (internal overlay E.6): half its length along the heading, and its radius.</summary>
        public static (float half, float radius) Hull(Vehicle v) => (v.Def.HullHalf, v.Def.HullRadius);

        /// <summary>The rest of the route it is following (internal overlay E.6).</summary>
        public static List<Vector2> Route(Vehicle v)
        {
            var list = new List<Vector2>();
            for (var i = v.PathIndex; i < v.Path.Count; i++) list.Add(v.Path[i]);
            return list;
        }

        /// <summary>A big attack's warned zones now (E.5).</summary>
        public static IReadOnlyList<BigZone> BigZones(Vehicle v) =>
            v.BigAttack is { } big && big.Stage != BigStage.Ready ? big.Zones : System.Array.Empty<BigZone>();

        /// <summary>A shield dome's reach while it stands (E.5), else 0.</summary>
        public static float Dome(Vehicle v) => v.DomeUp && v.Def.Dome is { } d ? d.Radius : 0f;

        /// <summary>The vehicles the stuck detector has open episodes for (E.6), by entity id.</summary>
        public static HashSet<int> Stuck(Navigation.StuckWatch? watch)
        {
            var set = new HashSet<int>();
            if (watch == null) return set;
            foreach (var r in watch.Records)
                if (r.EndTime < 0) set.Add(r.VehicleId);
            return set;
        }
    }
}

using System;
using System.Collections.Generic;
using System.Text;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Who beats whom. The simulation earns these through damage types, armour, range and speed
    /// (and <c>CounterTests</c> checks them in real skirmishes); this table is what the cards
    /// and the selection panel tell the player.
    /// </summary>
    public static class Counters
    {
        private static readonly Dictionary<UnitClass, UnitClass[]> Strong = new()
        {
            [UnitClass.Scout] = new[] { UnitClass.Artillery, UnitClass.Support },
            [UnitClass.Light] = new[] { UnitClass.Scout, UnitClass.Artillery, UnitClass.AntiAir, UnitClass.Support },
            [UnitClass.Tank] = new[] { UnitClass.Light, UnitClass.Scout, UnitClass.AntiAir },
            [UnitClass.Heavy] = new[] { UnitClass.Tank, UnitClass.Light, UnitClass.Defense },
            [UnitClass.TankHunter] = new[] { UnitClass.Tank, UnitClass.Heavy, UnitClass.Boss },
            [UnitClass.Artillery] = new[] { UnitClass.Defense, UnitClass.TankHunter, UnitClass.Heavy },
            [UnitClass.AntiAir] = new[] { UnitClass.Helicopter, UnitClass.Plane },
            [UnitClass.Support] = Array.Empty<UnitClass>(),
            [UnitClass.Helicopter] = new[] { UnitClass.Tank, UnitClass.Heavy, UnitClass.Artillery },
            [UnitClass.Plane] = new[] { UnitClass.Helicopter, UnitClass.Heavy, UnitClass.Artillery },
            [UnitClass.Defense] = new[] { UnitClass.Light, UnitClass.Scout, UnitClass.Tank },
            [UnitClass.Boss] = new[] { UnitClass.Light, UnitClass.Tank },
        };

        public static IReadOnlyList<UnitClass> StrongVs(UnitClass unit) =>
            Strong.TryGetValue(unit, out var list) ? list : Array.Empty<UnitClass>();

        /// <summary>What this unit beats: its own list where the data gives one (aircraft differ within a class), else its class's.</summary>
        public static IReadOnlyList<UnitClass> StrongVs(VehicleDef def) => def.StrongVs ?? StrongVs(def.Class);

        /// <summary>The classes that list <paramref name="unit"/> among their prey.</summary>
        public static IReadOnlyList<UnitClass> WeakVs(UnitClass unit)
        {
            var weak = new List<UnitClass>();
            foreach (var (hunter, prey) in Strong)
                if (hunter != UnitClass.Boss && Array.IndexOf(prey, unit) >= 0) weak.Add(hunter);
            // Aircraft also fear the fighters (planes), whatever the class line says.
            if (unit == UnitClass.Plane && !weak.Contains(UnitClass.Plane)) weak.Add(UnitClass.Plane);
            return weak;
        }

        /// <summary>"Strong vs light, scouts · Weak vs tank hunters, helicopters", in the current language.</summary>
        public static string Line(VehicleDef def)
        {
            var text = new StringBuilder();
            var strong = StrongVs(def);
            if (def.Class == UnitClass.Support) text.Append(Strings.Get("counter.support"));
            else if (strong.Count > 0) text.Append(Strings.Format("counter.strong", Join(strong)));
            var weak = WeakVs(def.Class);
            if (weak.Count > 0)
            {
                if (text.Length > 0) text.Append("  ·  ");
                text.Append(Strings.Format("counter.weak", Join(weak)));
            }
            return text.ToString();
        }

        private static string Join(IReadOnlyList<UnitClass> classes)
        {
            var parts = new string[classes.Count];
            for (var i = 0; i < classes.Count; i++) parts[i] = Strings.Get("class." + classes[i]);
            return string.Join(", ", parts);
        }
    }
}

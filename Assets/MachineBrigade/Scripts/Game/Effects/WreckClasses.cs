using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Game.Effects
{
    /// <summary>Prompt 34 L7: how a destroyed vehicle breaks up (and, L6, what its wreck sounds like), by its class.</summary>
    internal enum WreckClass
    {
        /// <summary>Tracked fighting vehicles: the turret is blown off (prompt 9), the hulk burns.</summary>
        Tank,

        /// <summary>Wheeled vehicles: wheels thrown off, the frame rolls over.</summary>
        Wheeled,

        /// <summary>Lorries and ammunition carriers: the cargo goes up in a chain.</summary>
        Truck,

        /// <summary>Guns and launchers: the ammunition inside cooks off.</summary>
        Artillery,

        /// <summary>Fighters and attack jets: a wing breaks off and it spins down trailing smoke, or the fuselage breaks in two.</summary>
        Fighter,

        /// <summary>Helicopters: the tail rotor goes and it spins down; the main rotor flies off.</summary>
        Helicopter,

        /// <summary>Bombers, transports, gunships: an engine burns, a wing goes, a long slanting fall.</summary>
        BigAircraft,

        /// <summary>Ships: list, break in two, sink (ShipSinking).</summary>
        Ship,

        /// <summary>Drones (and parachute drops): a small blast, nothing left.</summary>
        Drone,

        /// <summary>Towers and buildings: their ruin stays (WreckManager).</summary>
        Static,

        /// <summary>Armoured trains: burn where they stop, like a tank.</summary>
        Train,
    }

    /// <summary>Prompt 34 L7 (DECISIONS "Prompt 34 L5/L6/L7"): the class table, wreck lives and how many full wrecks are kept.</summary>
    internal static class WreckClasses
    {
        /// <summary>Ground vehicles that run on wheels, by their id (the defs do not say; the models do, with Part_wheel since L7).</summary>
        private static readonly string[] WheeledWords =
        {
            "car", "jeep", "technical", "wheeled", "apc", "vbied", "buggy", "radar_scout", "radar_support", "patrol", "humvee",
        };

        public static WreckClass Of(VehicleDef def)
        {
            if (def == null) return WreckClass.Tank;
            if (def.Static) return WreckClass.Static;
            if (def.Naval != null) return WreckClass.Ship;
            var id = def.Id ?? "";
            if (def.Frame?.Move == BossMove.Rail || id.Contains("train")) return WreckClass.Train;
            if (def.Flying)
            {
                if (def.Drone || id.Contains("drone") || id.Contains("chute") || id == "drop_pod") return WreckClass.Drone;
                if (!def.FixedWing) return WreckClass.Helicopter;
                return def.Boss || def.Radius >= 4.5f || def.MaxHp > 3000f || def.Class == UnitClass.Support ? WreckClass.BigAircraft : WreckClass.Fighter;
            }
            if (def.Boss) return WreckClass.Tank;
            if (def.Class == UnitClass.Artillery) return WreckClass.Artillery;
            if (def.Class == UnitClass.Support || id.Contains("truck") || id.Contains("ammo") || id.Contains("supply")) return WreckClass.Truck;
            foreach (var word in WheeledWords)
                if (id.Contains(word)) return WreckClass.Wheeled;
            return WreckClass.Tank;
        }

        /// <summary>An aircraft class whose wreck falls (its crash is the Sim's: a fixed point and time).</summary>
        public static bool Falls(WreckClass c) => c is WreckClass.Fighter or WreckClass.Helicopter or WreckClass.BigAircraft;

        /// <summary>Full wrecks near the camera at most (the prompt's ~12; Medium 9, Low 6); the rest are drawn simple and fade.</summary>
        public static int FullCap(GraphicsQuality tier) => tier switch
        {
            GraphicsQuality.Low => 6,
            GraphicsQuality.Medium => 9,
            _ => 12,
        };

        /// <summary>A full wreck counts as near the camera within this of the view's focus (m).</summary>
        public const float NearCamera = 90f;

        /// <summary>A wreck's life, s: 30-45 (by the vehicle's size), a boss's 90; Low graphics a third shorter.</summary>
        public static float Life(VehicleDef def, float random01, GraphicsQuality tier)
        {
            var life = def != null && def.Boss ? 90f : 30f + 15f * random01;
            return tier == GraphicsQuality.Low ? life * 0.67f : life;
        }

        /// <summary>A wreck over the full cap, or far from the camera, lives this long at most (a simple hulk, then a burn mark).</summary>
        public const float SimpleLife = 14f;
    }
}

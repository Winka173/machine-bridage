using System.Collections.Generic;
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
        /// <summary>
        /// The models given separable wheels by Tools/blender/mb_p34_parts.py (WHEELED there: keep the two lists the same).
        /// The defs do not say what runs on wheels; at runtime a model with a Part_wheel node is wheeled whatever its id.
        /// </summary>
        internal static readonly HashSet<string> WheeledModels = new()
        {
            "armored_car", "fpv_carrier", "ground_cruise_missile_vehicle", "heavy_aa", "iron_beam", "long_sam", "recoilless_jeep",
            "rocket_technical", "scout_jeep", "vbied", "wheeled_gun", "zu23_technical",
        };

        /// <summary>Other ground vehicles that run on wheels, by words in their id (elites and variants of the above).</summary>
        private static readonly string[] WheeledWords = { "car", "jeep", "technical", "wheeled", "apc", "vbied", "buggy", "humvee" };

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
            if (WheeledModels.Contains(id) || (def.Model != null && WheeledModels.Contains(def.Model))) return WreckClass.Wheeled;
            foreach (var word in WheeledWords)
                if (id.Contains(word)) return WreckClass.Wheeled;
            return WreckClass.Tank;
        }

        /// <summary>
        /// Play-test 12 ("mỗi loại nên có 2-3 loại random"): how many ways a class breaks up (WreckManager picks one).
        /// </summary>
        public static int Variants(WreckClass c) => c switch
        {
            WreckClass.Tank or WreckClass.Wheeled or WreckClass.Fighter or WreckClass.Helicopter or WreckClass.BigAircraft => 3,
            WreckClass.Truck or WreckClass.Artillery or WreckClass.Train => 2,
            _ => 1,
        };

        /// <summary>
        /// Play-test 12: the way this wreck breaks up, 0 to <see cref="Variants"/> - 1, picked from its entity id (the same
        /// vehicle always breaks the same way; neighbours differ). View only.
        /// </summary>
        public static int Variant(MachineBrigade.Sim.Core.EntityId id, WreckClass c)
        {
            var n = Variants(c);
            if (n <= 1) return 0;
            unchecked
            {
                var h = (uint)id.Value * 2654435761u;
                h ^= h >> 15;
                return (int)(h % (uint)n);
            }
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

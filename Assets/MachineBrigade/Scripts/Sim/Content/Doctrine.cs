#nullable enable
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// A commander's doctrine, chosen before a battle: small army-wide edges that favour a style
    /// of play. Not veterancy: nothing carries over between battles.
    /// </summary>
    public sealed class Doctrine
    {
        private readonly Dictionary<UnitClass, float> _toughness;

        private Doctrine(string id, Dictionary<UnitClass, float> toughness, float speed = 1f, float strikeCooldown = 1f,
            float income = 1f, int armyCap = 0)
        {
            Id = id;
            _toughness = toughness;
            Speed = speed;
            StrikeCooldown = strikeCooldown;
            Income = income;
            ArmyCap = armyCap;
        }

        public string Id { get; }

        /// <summary>Drive speed multiplier for the whole army.</summary>
        public float Speed { get; }

        /// <summary>Fire-support cooldown multiplier.</summary>
        public float StrikeCooldown { get; }

        /// <summary>CP income multiplier.</summary>
        public float Income { get; }

        /// <summary>Extra army cap.</summary>
        public int ArmyCap { get; }

        /// <summary>Health multiplier for a unit of this class.</summary>
        public float Toughness(UnitClass unit) => _toughness.TryGetValue(unit, out var m) ? m : 1f;

        public static readonly Doctrine Armor = new("armor", new Dictionary<UnitClass, float>
        {
            [UnitClass.Tank] = 1.2f, [UnitClass.Heavy] = 1.2f, [UnitClass.TankHunter] = 1.1f,
        });

        public static readonly Doctrine Air = new("air", new Dictionary<UnitClass, float>
        {
            [UnitClass.Helicopter] = 1.2f, [UnitClass.Plane] = 1.2f,
        }, strikeCooldown: 0.85f);

        public static readonly Doctrine Artillery = new("artillery", new Dictionary<UnitClass, float>
        {
            [UnitClass.Artillery] = 1.25f,
        }, strikeCooldown: 0.75f);

        public static readonly Doctrine Blitz = new("blitz", new Dictionary<UnitClass, float>
        {
            [UnitClass.Scout] = 1.15f, [UnitClass.Light] = 1.15f,
        }, speed: 1.15f);

        public static readonly Doctrine Logistics = new("logistics", new Dictionary<UnitClass, float>(), income: 1.2f, armyCap: 4);

        public static readonly IReadOnlyList<Doctrine> All = new[] { Armor, Air, Artillery, Blitz, Logistics };

        public static Doctrine? Get(string? id)
        {
            foreach (var d in All)
                if (d.Id == id) return d;
            return null;
        }
    }
}

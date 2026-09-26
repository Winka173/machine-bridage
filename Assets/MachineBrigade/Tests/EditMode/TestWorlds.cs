using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>Small hand-built catalogs and maps so each test controls every number it relies on.</summary>
    internal static class TestWorlds
    {
        public const float Step = 0.05f;

        public static readonly WeaponDef Gun = new WeaponDef("gun", DamageType.ArmorPiercing, damage: 100f,
            cooldown: 1f, range: 20f, minRange: 0f, projectileSpeed: 100f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Medium);

        public static readonly WeaponDef Shell = new WeaponDef("shell", DamageType.HighExplosive, damage: 50f,
            cooldown: 2f, range: 25f, minRange: 0f, projectileSpeed: 100f, splashRadius: 6f, spread: 0f,
            ExplosionTier.Large);

        public static readonly WeaponDef Howitzer = new WeaponDef("howitzer", DamageType.HighExplosive, damage: 40f,
            cooldown: 3f, range: 50f, minRange: 15f, projectileSpeed: 60f, splashRadius: 4f, spread: 0f,
            ExplosionTier.Large);

        /// <summary>Reaches nothing, so targets built with it never shoot back.</summary>
        public static readonly WeaponDef Stub = new WeaponDef("stub", DamageType.Kinetic, damage: 0f,
            cooldown: 1f, range: 0.5f, minRange: 0f, projectileSpeed: 100f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Small);

        public static Catalog Catalog()
        {
            var dummy = new VehicleDef("dummy", ArmorClass.Heavy, maxHp: 1000f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 1, visionRange: 30f, firesWhileMoving: true, Stub,
                deathExplosion: null);
            var tank = new VehicleDef("tank", ArmorClass.Heavy, maxHp: 300f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 4, visionRange: 30f, firesWhileMoving: true, Gun,
                deathExplosion: null);
            var boomer = new VehicleDef("boomer", ArmorClass.Heavy, maxHp: 50f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 4, visionRange: 30f, firesWhileMoving: true, Gun,
                new ExplosionDef(damage: 10f, radius: 3f, delay: 0.2f, ExplosionTier.Huge));
            var mortar = new VehicleDef("mortar", ArmorClass.Light, maxHp: 200f, speed: 5f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 5, visionRange: 30f, firesWhileMoving: true, Shell,
                deathExplosion: null);

            var arty = new VehicleDef("arty", ArmorClass.Light, maxHp: 200f, speed: 5f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 5, visionRange: 30f, firesWhileMoving: false, Howitzer,
                deathExplosion: null);
            // Harmless and nearly indestructible: a target that survives a whole test.
            var decoy = new VehicleDef("decoy", ArmorClass.Heavy, maxHp: 50000f, speed: 8f, turnRateDegrees: 360f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 1, visionRange: 30f, firesWhileMoving: true, Stub,
                deathExplosion: null);

            var barrel = new PropDef("barrel", ArmorClass.Light, maxHp: 10f, width: 1f, depth: 1f,
                blocksMovement: false, new ExplosionDef(damage: 50f, radius: 4f, delay: 0.1f, ExplosionTier.Large));
            var house = new PropDef("house", ArmorClass.Structure, maxHp: 100f, width: 8f, depth: 8f,
                blocksMovement: true, explosion: null);

            return new Catalog(1, DamageTable.Default, new[] { Gun, Shell, Stub, Howitzer },
                new[] { tank, boomer, mortar, dummy, arty, decoy },
                new[] { barrel, house });
        }

        public static SimWorld World(params PropPlacement[] props) =>
            new SimWorld(Catalog(), new MapDefinition("test", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) },
                props, new List<UnitPlacement>()));

        public static PropPlacement Prop(string def, float x, float y) => new PropPlacement(def, new Vector2(x, y), 0);

        public static void Run(SimWorld world, float seconds)
        {
            var steps = (int)(seconds / Step + 0.5f);
            for (var i = 0; i < steps; i++) world.Step(Step);
        }
    }
}

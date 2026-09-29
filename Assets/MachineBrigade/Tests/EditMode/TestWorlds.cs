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

        public static readonly WeaponDef Gun = new WeaponDef("gun", DamageType.Kinetic, damage: 100f,
            cooldown: 1f, range: 20f, minRange: 0f, projectileSpeed: 100f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Medium) { Penetration = 4, PiercingLook = true };

        public static readonly WeaponDef Shell = new WeaponDef("shell", DamageType.HighExplosive, damage: 50f,
            cooldown: 2f, range: 25f, minRange: 0f, projectileSpeed: 100f, splashRadius: 6f, spread: 0f,
            ExplosionTier.Large);

        public static readonly WeaponDef Howitzer = new WeaponDef("howitzer", DamageType.HighExplosive, damage: 40f,
            cooldown: 3f, range: 50f, minRange: 15f, projectileSpeed: 60f, splashRadius: 4f, spread: 0f,
            ExplosionTier.Large);

        public static readonly WeaponDef RoofGun = new WeaponDef("roofgun", DamageType.Kinetic, damage: 10f,
            cooldown: 0.2f, range: 22f, minRange: 0f, projectileSpeed: 200f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Small, ProjectileKind.Bullet, targets: TargetLayers.All);

        public static readonly WeaponDef Flak = new WeaponDef("flak", DamageType.Fragmentation, damage: 40f,
            cooldown: 0.5f, range: 30f, minRange: 0f, projectileSpeed: 250f, splashRadius: 3f, spread: 0f,
            ExplosionTier.Small, ProjectileKind.Bullet, targets: TargetLayers.All);

        public static readonly WeaponDef Salvo = new WeaponDef("salvo", DamageType.HighExplosive, damage: 20f,
            cooldown: 10f, range: 40f, minRange: 0f, projectileSpeed: 80f, splashRadius: 2f, spread: 0f,
            ExplosionTier.Medium, ProjectileKind.Rocket, burst: 6, burstInterval: 0.2f);

        public static readonly WeaponDef Missile = new WeaponDef("missile", DamageType.ShapedCharge, damage: 100f,
            cooldown: 5f, range: 30f, minRange: 0f, projectileSpeed: 20f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Medium, ProjectileKind.Missile);

        public static readonly WeaponDef Strafe = new WeaponDef("strafe", DamageType.Kinetic, damage: 20f,
            cooldown: 0.3f, range: 25f, minRange: 0f, projectileSpeed: 250f, splashRadius: 0f, spread: 0f,
            ExplosionTier.Small, ProjectileKind.Bullet);

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

            var gunner = new VehicleDef("gunner", ArmorClass.Heavy, maxHp: 900f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 7, visionRange: 30f, firesWhileMoving: true, Gun,
                deathExplosion: null, new[] { new WeaponMount(RoofGun, "mg", MountAim.Free) });
            var heli = new VehicleDef("heli", ArmorClass.Air, maxHp: 300f, speed: 14f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 360f, radius: 1.5f, cpCost: 6, visionRange: 35f, firesWhileMoving: true, Missile,
                deathExplosion: null, flying: true, altitude: 9f, captureRate: 0f);
            var jet = new VehicleDef("jet", ArmorClass.Air, maxHp: 300f, speed: 20f, turnRateDegrees: 90f,
                turretTurnRateDegrees: 360f, radius: 2f, cpCost: 8, visionRange: 45f, firesWhileMoving: true, Strafe,
                deathExplosion: null, flying: true, altitude: 16f, captureRate: 0f, fixedWing: true);
            var aa = new VehicleDef("aa", ArmorClass.Light, maxHp: 300f, speed: 8f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 4, visionRange: 40f, firesWhileMoving: true, Flak,
                deathExplosion: null);
            var launcher = new VehicleDef("launcher", ArmorClass.Light, maxHp: 250f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 7, visionRange: 40f, firesWhileMoving: false, Salvo,
                deathExplosion: null);
            var hunter = new VehicleDef("hunter", ArmorClass.Light, maxHp: 250f, speed: 6f, turnRateDegrees: 180f,
                turretTurnRateDegrees: 720f, radius: 1f, cpCost: 4, visionRange: 40f, firesWhileMoving: true, Missile,
                deathExplosion: null);

            var barrel = new PropDef("barrel", ArmorClass.Light, maxHp: 10f, width: 1f, depth: 1f,
                blocksMovement: false, new ExplosionDef(damage: 50f, radius: 4f, delay: 0.1f, ExplosionTier.Large));
            var house = new PropDef("house", ArmorClass.Structure, maxHp: 100f, width: 8f, depth: 8f,
                blocksMovement: true, explosion: null);

            var supports = new[]
            {
                new SupportDef("barrage", SupportKind.Barrage, cpCost: 5, cooldown: 30f, delay: 1.5f, radius: 6f, count: 6,
                    duration: 1f, damage: 80f, DamageType.HighExplosive, ExplosionTier.Large, blastRadius: 5f),
                new SupportDef("airstrike", SupportKind.Airstrike, cpCost: 8, cooldown: 60f, delay: 2f, radius: 2f, count: 5,
                    duration: 1f, damage: 150f, DamageType.HighExplosive, ExplosionTier.Huge, length: 40f, blastRadius: 5f),
                new SupportDef("smoke", SupportKind.Smoke, cpCost: 2, cooldown: 20f, delay: 0.5f, radius: 10f, count: 1,
                    duration: 10f, damage: 0f, DamageType.HighExplosive, ExplosionTier.Small),
                new SupportDef("repair", SupportKind.Repair, cpCost: 4, cooldown: 30f, delay: 0.5f, radius: 10f, count: 5,
                    duration: 2f, damage: 0.5f, DamageType.HighExplosive, ExplosionTier.Small),
            };

            return new Catalog(1, DamageTable.Default, new[] { Gun, Shell, Stub, Howitzer, RoofGun, Flak, Salvo, Missile, Strafe },
                new[] { tank, boomer, mortar, dummy, arty, decoy, gunner, heli, jet, aa, launcher, hunter },
                new[] { barrel, house }, supports);
        }

        public static SimWorld World(params PropPlacement[] props) =>
            new SimWorld(Catalog(), new MapDefinition("test", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) },
                props, new List<UnitPlacement>()));

        /// <summary>A 100 m map with a single objective of radius 8 at the centre.</summary>
        public static SimWorld ObjectiveWorld() =>
            new SimWorld(Catalog(), new MapDefinition("test", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) },
                new List<PropPlacement>(), new List<UnitPlacement>(),
                new[] { new CapturePointDef("mid", "mid", Vector2.Zero, 8f) }));

        public static PropPlacement Prop(string def, float x, float y) => new PropPlacement(def, new Vector2(x, y), 0);

        public static void Run(SimWorld world, float seconds)
        {
            var steps = (int)(seconds / Step + 0.5f);
            for (var i = 0; i < steps; i++) world.Step(Step);
        }
    }
}

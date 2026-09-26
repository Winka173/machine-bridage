using UnityEngine;
using P = MachineBrigade.Voxel.VoxelPalette;

namespace MachineBrigade.Voxel
{
    /// <summary>A vehicle split into a hull and a turret that rotates on its own.</summary>
    public sealed class VehicleModel
    {
        public VehicleModel(VoxelModel hull, VoxelModel turret, Vector3 turretPivot, Vector3 turretMount, float muzzleHeight)
        {
            Hull = hull;
            Turret = turret;
            TurretPivot = turretPivot;
            TurretMount = turretMount;
            MuzzleHeight = muzzleHeight;
        }

        public VoxelModel Hull { get; }
        public VoxelModel Turret { get; }

        /// <summary>Rotation centre inside the turret model, in voxels.</summary>
        public Vector3 TurretPivot { get; }

        /// <summary>Where that centre sits on the hull, in hull voxels.</summary>
        public Vector3 TurretMount { get; }

        /// <summary>Barrel height above the ground in voxels, for tracers and muzzle flashes.</summary>
        public float MuzzleHeight { get; }

        public Vector3 HullPivot => new Vector3(Hull.SizeX * 0.5f, 0f, Hull.SizeZ * 0.5f);
    }

    /// <summary>
    /// Every model in the game, drawn in code at 0.25 m per voxel. Footprints match the
    /// balance catalog (an 8 m house is 32 voxels wide). Models face +Z.
    /// </summary>
    public static class VoxelShapes
    {
        public const float VoxelSize = 0.25f;

        public static VehicleModel Vehicle(string id) => id switch
        {
            "scout_jeep" => Jeep(),
            "main_battle_tank" => MainBattleTank(),
            "artillery" => Artillery(),
            _ => LightTank(),
        };

        public static VoxelModel Prop(string id) => id switch
        {
            "house_small" => House(32, 32, 12, windowsRows: 1),
            "house_large" => House(48, 40, 20, windowsRows: 2),
            "wall" => Wall(),
            "fuel_tank" => FuelTank(),
            "barrel" => Barrel(),
            "ammo_crate" => Crate(),
            "tree" => Tree(),
            _ => Crate(),
        };

        /// <summary>Low, irregular pile left behind by a destroyed building.</summary>
        public static VoxelModel Rubble(int sizeX, int sizeZ, int seed)
        {
            var m = new VoxelModel(sizeX, 5, sizeZ);
            for (var z = 0; z < sizeZ; z++)
            for (var x = 0; x < sizeX; x++)
            {
                var h = 1 + Hash(x / 3, z / 3, seed) % 4;
                for (var y = 0; y < h; y++) m.Set(x, y, z, Hash(x, z + y, seed) % 3 == 0 ? P.Stone : P.Rubble);
            }
            return m;
        }

        private static VehicleModel LightTank()
        {
            var hull = new VoxelModel(13, 6, 26);
            Tracks(hull, 3, 26);
            hull.Box(2, 1, 1, 11, 5, 25, P.TeamMain);
            hull.Box(2, 4, 22, 11, 5, 25, 0); // sloped glacis
            hull.Box(0, 3, 1, 13, 4, 25, P.TeamDark); // fenders
            hull.Box(4, 5, 2, 9, 6, 7, P.Metal); // engine grille
            hull.Box(2, 3, 25, 4, 4, 26, P.Light);
            hull.Box(9, 3, 25, 11, 4, 26, P.Light);

            var turret = new VoxelModel(7, 4, 20);
            turret.Box(0, 0, 0, 7, 3, 8, P.TeamMain);
            turret.Box(1, 3, 1, 3, 4, 3, P.TeamDark);
            turret.Box(2, 0, 8, 5, 3, 9, P.TeamDark);
            turret.Box(3, 1, 9, 4, 2, 20, P.Metal);
            return new VehicleModel(hull, turret, new Vector3(3.5f, 0f, 4f), new Vector3(6.5f, 5f, 12f), 6.5f);
        }

        private static VehicleModel MainBattleTank()
        {
            var hull = new VoxelModel(16, 7, 34);
            Tracks(hull, 4, 34);
            hull.Box(2, 1, 1, 14, 6, 33, P.TeamMain);
            hull.Box(2, 5, 29, 14, 6, 33, 0);
            hull.Box(2, 4, 31, 14, 5, 33, 0);
            hull.Box(0, 4, 1, 16, 5, 33, P.TeamDark);
            hull.Box(4, 6, 2, 12, 7, 9, P.Metal);
            hull.Box(2, 4, 33, 4, 5, 34, P.Light);
            hull.Box(12, 4, 33, 14, 5, 34, P.Light);

            var turret = new VoxelModel(10, 5, 30);
            turret.Box(0, 0, 0, 10, 4, 11, P.TeamMain);
            turret.Box(1, 0, 11, 9, 3, 12, P.TeamDark);
            turret.Box(0, 3, 0, 10, 4, 3, P.TeamDark); // bustle rack
            turret.Box(6, 4, 3, 8, 5, 5, P.Metal); // commander hatch
            turret.Box(4, 1, 12, 6, 3, 14, P.TeamDark); // mantlet
            turret.Box(4, 2, 14, 5, 3, 30, P.Metal); // barrel
            return new VehicleModel(hull, turret, new Vector3(5f, 0f, 5.5f), new Vector3(8f, 6f, 15f), 8.5f);
        }

        private static VehicleModel Jeep()
        {
            var hull = new VoxelModel(9, 6, 18);
            foreach (var z in new[] { 2, 12 })
            {
                hull.Box(0, 0, z, 2, 3, z + 4, P.Rubber);
                hull.Box(7, 0, z, 9, 3, z + 4, P.Rubber);
            }
            hull.Box(1, 1, 1, 8, 4, 17, P.TeamMain);
            hull.Box(1, 3, 12, 8, 4, 17, P.TeamDark); // bonnet
            hull.Box(1, 4, 10, 8, 6, 11, P.Glass); // windscreen
            hull.Box(1, 4, 1, 2, 5, 9, P.TeamDark);
            hull.Box(7, 4, 1, 8, 5, 9, P.TeamDark);
            hull.Box(2, 2, 17, 3, 3, 18, P.Light);
            hull.Box(6, 2, 17, 7, 3, 18, P.Light);

            var turret = new VoxelModel(3, 4, 8);
            turret.Box(1, 0, 1, 2, 2, 2, P.Metal);
            turret.Box(0, 2, 2, 3, 4, 3, P.TeamDark);
            turret.Box(1, 2, 0, 2, 3, 8, P.Metal);
            return new VehicleModel(hull, turret, new Vector3(1.5f, 0f, 1.5f), new Vector3(4.5f, 4f, 5f), 6.5f);
        }

        private static VehicleModel Artillery()
        {
            var hull = new VoxelModel(14, 6, 28);
            Tracks(hull, 3, 28);
            hull.Box(2, 1, 1, 12, 5, 27, P.TeamMain);
            hull.Box(0, 3, 1, 14, 4, 27, P.TeamDark);
            hull.Box(3, 5, 20, 11, 6, 26, P.Metal);

            var turret = new VoxelModel(10, 7, 32);
            turret.Box(0, 0, 0, 10, 6, 12, P.TeamMain);
            turret.Box(0, 5, 0, 10, 6, 12, P.TeamDark);
            turret.Box(1, 2, 12, 9, 5, 13, P.TeamDark);
            turret.Box(4, 3, 13, 6, 5, 32, P.Metal); // long barrel
            turret.Box(3, 3, 28, 7, 5, 30, P.Metal); // muzzle brake
            return new VehicleModel(hull, turret, new Vector3(5f, 0f, 6f), new Vector3(7f, 5f, 9f), 9f);
        }

        private static void Tracks(VoxelModel hull, int width, int length)
        {
            hull.Box(0, 0, 1, width, 3, length - 1, P.Rubber);
            hull.Box(hull.SizeX - width, 0, 1, hull.SizeX, 3, length - 1, P.Rubber);
            hull.Box(0, 1, 0, width, 2, length, P.Rubber);
            hull.Box(hull.SizeX - width, 1, 0, hull.SizeX, 2, length, P.Rubber);
        }

        private static VoxelModel House(int sx, int sz, int wallHeight, int windowsRows)
        {
            var roofHeight = sx / 4;
            var m = new VoxelModel(sx, wallHeight + roofHeight + 3, sz);
            m.Box(0, 0, 0, sx, wallHeight, sz, P.Wall);
            m.Box(0, 0, 0, sx, 1, sz, P.Stone);

            var rowHeight = wallHeight / windowsRows;
            m.Paint((x, y, z) =>
            {
                var onFace = x == 0 || z == 0 || x == sx - 1 || z == sz - 1;
                if (!onFace) return false;
                var along = x == 0 || x == sx - 1 ? z : x;
                var inRow = (y % rowHeight) >= rowHeight / 2 - 1 && (y % rowHeight) < rowHeight / 2 + 2 && y > 1;
                return inRow && along % 8 >= 3 && along % 8 < 6;
            }, P.Window);
            m.Box(sx / 2 - 2, 1, 0, sx / 2 + 2, 7, 1, P.Door);

            for (var k = 0; k < roofHeight; k++) m.Box(k - 1, wallHeight + k, -1, sx - k + 1, wallHeight + k + 1, sz + 1, P.Roof);
            m.Box(sx / 4, wallHeight, sz * 3 / 4, sx / 4 + 3, wallHeight + roofHeight + 3, sz * 3 / 4 + 3, P.Stone);
            return m;
        }

        private static VoxelModel Wall()
        {
            var m = new VoxelModel(32, 8, 4);
            m.Box(0, 0, 0, 32, 8, 4, P.Stone);
            m.Paint((x, y, z) => (x / 4 + y / 2) % 2 == 0, P.Rubble);
            return m;
        }

        private static VoxelModel FuelTank()
        {
            var m = new VoxelModel(16, 14, 16);
            m.Cylinder(8f, 8f, 7.8f, 0, 11, P.TankWhite);
            m.Cylinder(8f, 8f, 7.9f, 7, 8, P.Stripe);
            m.Ellipsoid(8f, 11f, 8f, 7f, 2.5f, 7f, P.TankWhite);
            m.Box(7, 12, 7, 9, 14, 9, P.Metal);
            return m;
        }

        private static VoxelModel Barrel()
        {
            var m = new VoxelModel(4, 5, 4);
            m.Cylinder(2f, 2f, 2f, 0, 5, P.BarrelRed);
            m.Cylinder(2f, 2f, 2f, 1, 2, P.Metal);
            m.Cylinder(2f, 2f, 2f, 3, 4, P.Metal);
            return m;
        }

        private static VoxelModel Crate()
        {
            var m = new VoxelModel(5, 4, 5);
            m.Box(0, 0, 0, 5, 4, 5, P.Crate);
            m.Paint((x, y, z) => y == 2 && (x == 0 || z == 0 || x == 4 || z == 4), P.Stripe);
            return m;
        }

        private static VoxelModel Tree()
        {
            var m = new VoxelModel(12, 20, 12);
            m.Box(5, 0, 5, 7, 9, 7, P.Wood);
            m.Ellipsoid(6f, 13f, 6f, 6f, 6.5f, 6f, P.Leaf);
            m.Paint((x, y, z) => y > 7 && Hash(x, y + z, 7) % 4 == 0, P.LeafDark);
            return m;
        }

        private static int Hash(int x, int y, int seed)
        {
            unchecked
            {
                var h = x * 374761393 + y * 668265263 + seed * 144269504;
                h = (h ^ (h >> 13)) * 1274126177;
                return (h ^ (h >> 16)) & 0x7fffffff;
            }
        }
    }
}

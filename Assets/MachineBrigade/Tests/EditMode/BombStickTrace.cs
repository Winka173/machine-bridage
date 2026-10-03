using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Movement;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The bomb-run fix, pass 0 (DECISIONS "Ném bom rải thảm"): where every bomb of one drop lands, for every bomb weapon on
    /// every unit that mounts one. No battle is simulated: the test builds an empty field with one bomber and one target
    /// tank at (0, 0), flies the bomber straight at it on heading 0 (north, +z) and calls the game's own drop code directly:
    /// CombatSystem.CanFire (the release moment: StickStraddles, StickNearOwn, reach) and CombatSystem.Launch (the aim
    /// point: BombImpact, the scatter, the fall time). Between bombs it repeats the salvo timer of CombatSystem.Operate and
    /// the run throttle of MovementSystem (0.8 inside 1.1 x its attack reach; the attack-hold ease), nothing else.
    /// Three seeds. One row a bomb, written to the csv named by MB_BOMB_TRACE (Tools/export/export.py bom reads it into
    /// the Bom_vet_tha sheet). Runs only with MB_BOMB_TRACE set.
    /// </summary>
    public class BombStickTrace
    {
        private const float Dt = 0.05f;
        private const BindingFlags Hidden = BindingFlags.NonPublic | BindingFlags.Instance;
        private static readonly int[] Seeds = { 1, 2, 3 };

        private const string Header = "vu_khi_id,don_vi_id,seed,chi_so_bom,tick_tha,vi_tri_tha_x_m,vi_tri_tha_z_m,tick_cham,vi_tri_roi_x_m," +
            "vi_tri_roi_z_m,thoi_gian_roi_s,toc_do_luc_tha_m_s,do_cao_m,huong_bay_deg,duong_tha,dieu_kien_tha,loi_m,ria_m,khoang_tha_s,ghi_chu";

        [Test, Category("Export")]
        public void WriteTheBombDropTrace()
        {
            var path = Environment.GetEnvironmentVariable("MB_BOMB_TRACE");
            if (string.IsNullOrEmpty(path)) Assert.Ignore("bomb trace: set MB_BOMB_TRACE to the output csv path");
            var catalog = GameContent.LoadCatalog();
            var launch = typeof(CombatSystem).GetMethod("Launch", Hidden);
            var canFire = typeof(CombatSystem).GetMethod("CanFire", Hidden);
            var attackReach = typeof(MovementSystem).GetMethod("AttackReach", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(launch, "CombatSystem.Launch (private) not found: the trace calls it by reflection");
            Assert.IsNotNull(canFire, "CombatSystem.CanFire (private) not found: the trace calls it by reflection");

            // Every (bomb weapon, unit mounting it) pair, the units in id order.
            var pairs = new List<(WeaponDef weapon, VehicleDef carrier, int mount)>();
            foreach (var unit in catalog.Vehicles.Values.OrderBy(d => d.Id, StringComparer.Ordinal))
            {
                // A car bomb's charge (family "bomb" too) blows up its own vehicle: not a drop.
                if (unit.Kamikaze) continue;
                for (var m = 0; m < unit.Mounts.Count; m++)
                {
                    var arm = unit.Mounts[m].Weapon;
                    if (!IsBomb(arm)) continue;
                    var seen = false;
                    foreach (var p in pairs)
                        if (p.weapon.Id == arm.Id && p.carrier.Id == unit.Id) seen = true;
                    if (!seen) pairs.Add((arm, unit, m));
                }
            }

            var sb = new StringBuilder();
            sb.Append(Header).Append('\n');
            var bombs = 0;
            foreach (var (weapon, carrier, mount) in pairs)
            {
                foreach (var seed in Seeds)
                {
                    try
                    {
                        bombs += Trace(catalog, launch, canFire, attackReach, weapon, carrier, mount, seed, sb);
                    }
                    catch (Exception ex)
                    {
                        var inner = ex is TargetInvocationException && ex.InnerException != null ? ex.InnerException : ex;
                        sb.Append(weapon.Id).Append(',').Append(carrier.Id).Append(',').Append(seed).Append(",-1,,,,,,,,,,,,ERROR,,,,")
                            .Append(Clean("ERROR " + inner.GetType().Name + ": " + inner.Message)).Append('\n');
                    }
                }
            }
            var dir = Path.GetDirectoryName(Path.GetFullPath(path));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
            Assert.Greater(pairs.Count, 0, "no bomb weapon is mounted on any unit");
            Assert.Greater(bombs, 0, "no bomb was dropped: see the ghi_chu column of " + path);
        }

        /// <summary>A bomb weapon: it fires bombs, or its data family is "bomb" (the bosses' bomb-bay sticks fly as shells).</summary>
        private static bool IsBomb(WeaponDef w) => w.Projectile == ProjectileKind.Bomb || w.Family == "bomb";

        private static int Trace(Catalog catalog, MethodInfo launch, MethodInfo canFire, MethodInfo attackReach, WeaponDef weapon,
            VehicleDef carrier, int mount, int seed, StringBuilder sb)
        {
            var world = new SimWorld(catalog, Field(), seed: seed);
            var target = world.SpawnVehicle("main_battle_tank", 1, Vector2.Zero, 0f);
            var bomber = world.SpawnVehicle(carrier.Id, 0, new Vector2(0f, -40f), 0f);
            var combat = world.Combat;
            var round = CombatSystem.Loaded(bomber, mount);
            var freeFall = CombatSystem.FreeFall(bomber, round);
            var path = freeFall ? "FREE_FALL" : round.Projectile == ProjectileKind.Bomb ? (round.Glides ? "GLIDE" : "GUIDED_OR_GROUND") : "SHELL_PATH";
            var state = bomber.Weapons[mount];
            state.Cooldown = 0f;
            bomber.Heading = 0f;
            bomber.Speed = bomber.Flying ? carrier.Speed : 0f;
            var reach = attackReach != null ? (float)attackReach.Invoke(null, new object[] { bomber, target }) : round.Range;
            var fall = CombatSystem.BombFall(bomber);
            var stick = CombatSystem.StickLength(bomber, round, round.Burst);
            var start = freeFall ? -(bomber.Speed * fall + stick + 60f) : -Math.Clamp(round.Range * 0.6f, 8f, 40f);
            bomber.Position = new Vector2(0f, Math.Max(-180f, start));

            // The run in: straight north at the target until the game's own CanFire lets the stick go.
            var tick = 0;
            var extending = false;
            var condition = freeFall ? "CanFire" : "DIRECT";
            var released = !freeFall;
            while (!released && tick < 2000 && bomber.Position.Y < 5f)
            {
                tick++;
                Fly(bomber, carrier, target, reach, ref extending);
                released = (bool)canFire.Invoke(combat, new object[] { bomber, mount, target });
            }
            if (!released)
            {
                sb.Append(weapon.Id).Append(',').Append(carrier.Id).Append(',').Append(seed).Append(",-1,").Append(tick)
                    .Append(",,,,,,,,,,").Append(path).Append(",NO_RELEASE,,,,")
                    .Append(Clean("CanFire never true on the straight run (passed over the target)")).Append('\n');
                return 0;
            }

            // The salvo as CombatSystem.Operate fires it: the first bomb now, the rest one BurstInterval apart (20 Hz steps).
            var salvo = round.Burst;
            if (state.Load > 0) salvo = Math.Min(salvo, Math.Max(0, state.Ammo));
            var interval = round.Burst > 1 ? round.BurstInterval : 0.15f;
            var written = Drop(world, combat, launch, bomber, mount, target, round, carrier.Id, seed, 0, tick, true, path, condition, interval, sb);
            var left = salvo - 1;
            var timer = interval;
            var next = 1;
            while (left > 0 && tick < 4000)
            {
                tick++;
                Fly(bomber, carrier, target, reach, ref extending);
                timer -= Dt;
                while (left > 0 && timer <= 0f)
                {
                    written += Drop(world, combat, launch, bomber, mount, target, round, carrier.Id, seed, next, tick, false, path, condition, interval, sb);
                    next++;
                    left--;
                    timer += interval;
                }
            }
            return written;
        }

        /// <summary>One bomb through the game's CombatSystem.Launch; its WeaponFired event gives the aim point and the fall time.</summary>
        private static int Drop(SimWorld world, CombatSystem combat, MethodInfo launch, Vehicle bomber, int mount, Vehicle target, WeaponDef round,
            string carrierId, int seed, int index, int tick, bool pull, string path, string condition, float interval, StringBuilder sb)
        {
            world.ClearEvents();
            var from = bomber.Position;
            var speed = bomber.Speed;
            launch.Invoke(combat, new object[] { bomber, mount, target.Position, target.Id, false, 1f, pull, target });
            var count = 0;
            foreach (var e in world.Events)
            {
                if (e.Kind != SimEventKind.WeaponFired || e.Entity != bomber.Id) continue;
                var travel = e.Value;
                var lands = tick + (int)Math.Ceiling(travel / Dt - 1e-4);
                sb.Append(round.Id).Append(',').Append(carrierId).Append(',').Append(seed).Append(',').Append(index).Append(',')
                    .Append(tick).Append(',').Append(F(from.X)).Append(',').Append(F(from.Y)).Append(',').Append(lands).Append(',')
                    .Append(F(e.Target.X)).Append(',').Append(F(e.Target.Y)).Append(',').Append(F(travel)).Append(',')
                    .Append(F(speed)).Append(',').Append(F(bomber.Height)).Append(',').Append(F(bomber.Heading * 180f / MathF.PI)).Append(',')
                    .Append(path).Append(',').Append(condition).Append(',').Append(F(round.SplashRadius)).Append(',').Append(F(round.WarnRadius))
                    .Append(',').Append(F(interval)).Append(',').Append('\n');
                count++;
            }
            world.ClearEvents();
            return count;
        }

        /// <summary>
        /// The bomber's straight run at a target dead ahead, as MovementSystem flies it (the attack-run throttle and the speed
        /// change rate, MovementSystem.cs: the AttackHold ease, 0.8 inside 1.1 x the attack reach, full power once extending).
        /// </summary>
        private static void Fly(Vehicle v, VehicleDef def, Vehicle target, float reach, ref bool extending)
        {
            if (!v.Flying) return;
            var offset = target.Position - v.Position;
            var distance = offset.Length();
            var ahead = Vector2.Dot(SimMath.Forward(v.Heading), offset);
            if (!extending && (distance < MathF.Max(6f, reach * 0.3f) || (ahead < 0f && distance < reach * 0.6f))) extending = true;
            var throttle = 1f;
            if (!extending && def.AttackHold > 0f) throttle = Math.Clamp((distance - target.Radius - reach) / reach + 0.5f, 0.5f, 1f);
            else if (!extending && distance < reach * 1.1f) throttle = 0.8f;
            v.Speed = SimMath.MoveTowards(v.Speed, def.Speed * v.SpeedFactor * throttle, def.Speed * 0.8f * Dt);
            v.Position += SimMath.Forward(v.Heading) * (v.Speed * Dt);
        }

        private static MapDefinition Field() =>
            new MapDefinition("field", 400f,
                new[] { new TeamStart(0, new Vector2(-160f, -160f)), new TeamStart(1, new Vector2(160f, 160f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());

        private static string F(float value) => value.ToString("0.###", CultureInfo.InvariantCulture);

        private static string Clean(string text) => text.Replace(',', ';').Replace('\n', ' ').Replace('\r', ' ');
    }
}

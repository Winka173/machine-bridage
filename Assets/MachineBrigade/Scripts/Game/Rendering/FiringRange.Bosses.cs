using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Play-test 12 (DECISIONS "Play-test 12 (lane B)"): a boss's "In action" clip. The usual five targets in front left most
    /// of a boss's guns silent (an aft turret's arc, a laid main battery, a 60 s main gun), so a boss gets one enemy per gun
    /// mount, each inside that mount's reach and arc, laid out for its domain:
    /// <list type="bullet">
    /// <item>at sea (play-test 13): the ship lies along the beach (bow along the shore line), and the line abreast of ships
    /// stands between it and the shore, parallel to the beach, bows towards it, along its length (every turret bears on the
    /// beam); a sunk ship's replacement comes back once the wreck has gone under;
    /// the main battery and the launch cells, which only the naval system fires at sea, are fired by the range
    /// (SimWorld.PreviewSalvo / PreviewCruise), each turret at a ship of its own;</item>
    /// <item>on the ground: the main gun's target nearest and dead ahead (the hull-aimed launchers fire on it too), the
    /// others fanned in front, an arc's mount at its arc;</item>
    /// <item>on the rail: down both sides of the track, ahead of the middle of the train;</item>
    /// <item>in the air: a spread of ground targets round the spot it works over, as before but one per gun.</item>
    /// </list>
    /// Guns that fire on aircraft only get a helicopter or two. No weapon waits more than <see cref="ShowCadence"/> s
    /// (SimWorld.Hasten), so a slow main gun shows in the clip. View and preview only: a battle is unchanged.
    /// </summary>
    public sealed partial class FiringRange
    {
        /// <summary>The longest any weapon of a boss on show waits for its next round.</summary>
        internal const float ShowCadence = 8f;

        /// <summary>How often the preview fires a flagship's salvo and its cruise missile.</summary>
        private const double SalvoEvery = 9.0, CruiseEvery = 15.0;

        /// <summary>The most enemies a boss gets for its guns, and helicopters for its anti-aircraft guns.</summary>
        internal const int MostBossTargets = 8, MostBossAir = 2;

        /// <summary>A boss on show (not a flying one's framing, which follows its circuit).</summary>
        private bool _bossShow;

        private double _salvoAt = 3.0, _cruiseAt = 7.0;

        /// <summary>The ground the boss's scene covers (shooter and targets), framed whole; null: the usual framing.</summary>
        private Rect? _bossBox;

        /// <summary>Each target slot's heading as it was set up (ships in line abreast face the boss).</summary>
        private readonly List<float> _headings = new();

        private static readonly string[] BossGroundTargets =
            { "main_battle_tank", "light_tank", "heavy_tank", "armored_car", "ifv", "tank_destroyer", "scout_jeep", "main_battle_tank" };

        private static readonly string[] BossShipTargets = { "sea_corvette", "missile_boat", "missile_boat" };

        /// <summary>A naval boss's scene: the ship mid-range, lying along the beach, the line abreast on its port side, shoreward.</summary>
        internal static Vector2 BossSeaStart => Vector2.Zero;

        /// <summary>Play-test 13: a naval boss on show lies parallel to the beach (bow along +x; its port side faces the shore).</summary>
        internal const float BossSeaHeading = MathF.PI * 0.5f;

        /// <summary>A sunk ship of the line comes back this much later than a ground target (its wreck goes under first).</summary>
        private const double ShipReplaceExtra = 3.0;

        /// <summary>How far off its beam the line abreast stands: most of its shortest (not laid) gun's reach, clear of its own beam.</summary>
        internal static float BossSeaOffset(VehicleDef def)
        {
            var reach = float.MaxValue;
            foreach (var m in def.Mounts)
            {
                var w = m.Weapon;
                if (w.Damage <= 0f || w.Laid || !w.CanEngage(false, def)) continue;
                reach = Mathf.Min(reach, w.Range);
            }
            if (reach == float.MaxValue) reach = 60f;
            return Mathf.Clamp(reach * 0.55f, def.Width * 0.5f + 14f, Mathf.Max(def.Width * 0.5f + 14f, 60f));
        }

        /// <summary>Half the longest ship of the line (it lies bows-on, across the shore line).</summary>
        internal static float BossSeaShipHalf(Catalog catalog)
        {
            var half = 8f;
            foreach (var id in BossShipTargets)
                if (catalog.Vehicles.TryGetValue(id, out var ship)) half = Mathf.Max(half, ship.Length * 0.5f);
            return half;
        }

        /// <summary>The far edge of a naval boss's scene: the line abreast, its ships' length, then the shore gap to the beach.</summary>
        internal static float BossSeaFar(Catalog catalog, VehicleDef def) =>
            BossSeaOffset(def) + BossSeaShipHalf(catalog) + 8f + PreviewSettings.ShoreGap;

        /// <summary>The boss's targets, one per gun mount, set up once (see the class notes).</summary>
        private void BossTargets()
        {
            var def = _shooter.Def;
            var guns = new List<int>();
            var airOnly = new List<int>();
            for (var i = 0; i < def.Mounts.Count; i++)
            {
                var w = def.Mounts[i].Weapon;
                if (w.Damage <= 0f) continue;
                if (w.Laid || w.CanEngage(false, def)) guns.Add(i);
                else if (w.CanEngage(true, def)) airOnly.Add(i);
            }
            var spots = new List<(string id, Vector2 at, float heading)>();
            switch (Setting)
            {
                case PreviewSetting.Sea:
                    LineAbreast(def, guns, spots);
                    break;
                case PreviewSetting.Air:
                    for (var k = 0; k < Math.Min(Math.Max(guns.Count, 3), MostBossTargets); k++)
                        spots.Add((Ground(k), _far + AirSpread[k % AirSpread.Length], MathF.PI));
                    break;
                default:
                    FanOut(def, guns, spots, Setting == PreviewSetting.Rail);
                    break;
            }
            // Anti-aircraft-only guns: a helicopter or two, in the reach of the shortest of them.
            if (airOnly.Count > 0)
            {
                var reach = float.MaxValue;
                var least = 0f;
                foreach (var i in airOnly)
                {
                    reach = Mathf.Min(reach, def.Mounts[i].Weapon.Range);
                    least = Mathf.Max(least, def.Mounts[i].Weapon.MinRange);
                }
                var d = Mathf.Clamp(reach * 0.55f, least + 8f, Mathf.Max(least + 8f, 40f));
                d = Mathf.Max(d, def.Radius + 10f);
                var count = Math.Min(MostBossAir, airOnly.Count);
                for (var k = 0; k < count; k++)
                {
                    // Sea: over the line of ships; else up front, either side.
                    var bearing = Setting == PreviewSetting.Sea ? BossSeaHeading - MathF.PI * 0.5f + (k == 0 ? -0.35f : 0.35f)
                        : count == 1 ? 0.3f : (k == 0 ? -0.45f : 0.45f);
                    var at = Setting == PreviewSetting.Air ? _far + new Vector2(k == 0 ? -12f : 12f, -6f) : _start + SimMath.Forward(bearing) * d;
                    spots.Add(("attack_helicopter", Inside(at), MathF.PI));
                }
            }
            foreach (var (id, at, heading) in spots) Target(id, at, heading);
            if (Setting == PreviewSetting.Air) return;
            // The scene framed whole: the boss's hull (lying along x at sea) and every target.
            var along = Setting == PreviewSetting.Sea;
            float halfX = (along ? def.Length : def.Width) * 0.5f, halfY = (along ? def.Width : def.Length) * 0.5f;
            float minX = _start.X - halfX, maxX = _start.X + halfX;
            float minY = _start.Y - halfY, maxY = _start.Y + halfY;
            foreach (var (_, at, _) in spots)
            {
                minX = Mathf.Min(minX, at.X - 3f);
                maxX = Mathf.Max(maxX, at.X + 3f);
                minY = Mathf.Min(minY, at.Y - 3f);
                maxY = Mathf.Max(maxY, at.Y + 3f);
            }
            _bossBox = Rect.MinMaxRect(minX, minY, maxX, maxY);
        }

        /// <summary>The ground targets' offsets round a flying boss's spot (the usual five, then more round them).</summary>
        private static readonly Vector2[] AirSpread =
        {
            new Vector2(-4f, 0f), new Vector2(5f, 3f), new Vector2(0f, 9f), new Vector2(-8.5f, 6f), new Vector2(8.5f, 9f),
            new Vector2(-12f, 13f), new Vector2(12f, 0f), new Vector2(3f, 16f),
        };

        private string Ground(int k)
        {
            var id = BossGroundTargets[k % BossGroundTargets.Length];
            return _world.Catalog.Vehicles.ContainsKey(id) ? id : "main_battle_tank";
        }

        private string Ship(int k)
        {
            var id = BossShipTargets[k % BossShipTargets.Length];
            return _world.Catalog.Vehicles.ContainsKey(id) ? id : ShipTarget;
        }

        /// <summary>
        /// A naval boss's targets (play-test 13): the boss lies along the beach; a line abreast of ships on its port side,
        /// between it and the shore and parallel to the beach (bows towards it), along its length, as far off as most of its
        /// shortest gun's reach; every turret, fore, aft and amidships, bears on the beam.
        /// </summary>
        private void LineAbreast(VehicleDef def, List<int> guns, List<(string id, Vector2 at, float heading)> spots)
        {
            var n = Math.Min(Math.Max(guns.Count, 2), MostBossTargets);
            var off = BossSeaOffset(def);
            // Side by side a beam and a gap apart, the line no longer than the hull (so its ends stay in reach).
            var beam = 0f;
            for (var k = 0; k < n; k++)
                if (_world.Catalog.Vehicles.TryGetValue(Ship(k), out var ship)) beam = Mathf.Max(beam, ship.Width);
            var gap = n > 1 ? Mathf.Clamp(def.Length * 0.9f / (n - 1), beam + 4f, Mathf.Max(beam + 4f, 16f)) : 0f;
            // On the port beam (towards the shore), side by side along the hull, each bow towards the boss; every ship on the
            // water, its far end short of the beach (BossSeaFar left the room).
            var port = SimMath.Forward(BossSeaHeading - MathF.PI * 0.5f);
            var ahead = SimMath.Forward(BossSeaHeading);
            var facing = SimMath.HeadingOf(-port);
            for (var k = 0; k < n; k++)
                spots.Add((Ship(k), Inside(_start + port * off + ahead * ((k - (n - 1) * 0.5f) * gap)), facing));
        }

        /// <summary>
        /// A ground or rail boss's targets: the main gun's nearest and dead ahead (the hull-aimed launchers fire on it too), a
        /// mount with an arc of its own at its arc, the rest fanned in front (a train's down both sides of the track).
        /// </summary>
        private void FanOut(VehicleDef def, List<int> guns, List<(string id, Vector2 at, float heading)> spots, bool rail)
        {
            // A secondary turret or hull mount (not free, no arc, not a broadside) fires only on the main gun's target in
            // the Sim (CombatSystem.SelectSecondaryTarget): it gets none of its own.
            var own = new List<int>();
            foreach (var i in guns)
            {
                var m = def.Mounts[i];
                if (i == 0 || m.Aim is MountAim.Free or MountAim.Left or MountAim.Right || m.ArcHalf > 0f) own.Add(i);
            }
            var count = Math.Min(own.Count, MostBossTargets);
            var free = 0;
            for (var k = 0; k < count; k++)
                if (own[k] != 0 && def.Mounts[own[k]].ArcHalf <= 0f && def.Mounts[own[k]].Aim == MountAim.Free) free++;
            var j = 0;
            for (var k = 0; k < count; k++)
            {
                var i = own[k];
                var mount = def.Mounts[i];
                var w = mount.Weapon;
                var least = Mathf.Max(w.MinRange + 6f, def.Radius + 8f);
                float bearing, d;
                if (i == 0)
                {
                    bearing = 0f;
                    d = Mathf.Clamp(w.Range * 0.45f, least, Mathf.Max(least, 36f));
                }
                else
                {
                    if (mount.ArcHalf > 0f) bearing = mount.ArcCentre;
                    else if (mount.Aim == MountAim.Left) bearing = -MathF.PI * 0.5f;
                    else if (mount.Aim == MountAim.Right) bearing = MathF.PI * 0.5f;
                    else if (rail) bearing = (j % 2 == 0 ? -1f : 1f) * (0.75f + 0.25f * (j / 2));
                    else bearing = free > 1 ? Mathf.Lerp(-0.8f, 0.8f, j / (free - 1f)) : 0.45f;
                    if (mount.ArcHalf <= 0f && mount.Aim == MountAim.Free) j++;
                    d = Mathf.Clamp(w.Range * 0.6f, least, Mathf.Max(least, 60f));
                }
                var at = _start + SimMath.Forward(bearing) * d;
                // Not on top of one already there: on out along its line.
                for (var tries = 0; tries < 4 && Crowded(at, spots); tries++) at += SimMath.Forward(bearing) * 7f;
                at = Inside(at);
                spots.Add((Ground(k), at, SimMath.HeadingOf(_start - at)));
            }
        }

        private static bool Crowded(Vector2 at, List<(string id, Vector2 at, float heading)> spots)
        {
            foreach (var s in spots)
                if (Vector2.Distance(s.at, at) < 7f) return true;
            return false;
        }

        /// <summary>Every step of a boss's clip: no long waits, and a flagship's salvo and cruise missile now and then.</summary>
        private void BossShow()
        {
            if (!_bossShow || !_targetsUp || _shooter == null || !_shooter.IsAlive) return;
            _world.Hasten(_shooter, ShowCadence);
            if (_shooter.HoldFire) return;
            // Play-test 14: the salvo is laid first (the turrets traverse) and fires on a later call once they are on.
            if (_shooter.Def.Salvo != null && (_world.Time >= _salvoAt || _world.SalvoLaying(_shooter)))
            {
                if (!_world.SalvoLaying(_shooter)) _salvoAt = _world.Time + SalvoEvery;
                _world.PreviewSalvo(_shooter);
            }
            if (_shooter.Def.Cruise != null && _world.Time >= _cruiseAt)
            {
                _cruiseAt = _world.Time + CruiseEvery;
                _world.PreviewCruise(_shooter);
            }
        }

        /// <summary>A boss's whole scene: its centre and how far it reaches from there.</summary>
        private bool BossFrame(out Vector3 centre, out float span)
        {
            centre = default;
            span = 0f;
            if (_bossBox is not { } box) return false;
            centre = new Vector3(box.center.x, 1.5f, box.center.y);
            span = Mathf.Max(box.width, box.height) * 0.5f / Zoom + 6f;
            return true;
        }
    }
}

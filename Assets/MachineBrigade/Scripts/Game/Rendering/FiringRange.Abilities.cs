using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Test feedback 11D: in its In action clip a vehicle or fire support with a special ability
    /// shows the ability working, not only its gun. Each scene adds what the ability works on,
    /// with the real simulation doing the work: friendly vehicles to repair, fortify or lead,
    /// enemy "sparring partners" (they move and fire but cannot be destroyed) whose missiles a
    /// jammer scrambles, whose rockets an interceptor burns down, whose gun a counter-battery
    /// radar finds, whose SAMs draw an aircraft's flares, that an EMP silences or a shield dome
    /// soaks up; dragon's teeth for a breacher's blade. A pulse on the ground marks an aura.
    /// Vehicles whose clip already showed their ability (mine layer, car bomb, smoke generator,
    /// drone carriers) and plain gun vehicles keep the plain range. Play-test 13: a mine roller (the demolition-line
    /// vehicle) drives a lane through an enemy minefield, setting the mines off under its roller; a drone killer (the
    /// microwave, the interceptor drones) downs the drones enemy carriers send at its friends; an unarmed transport (the
    /// heavy-lift helicopter, the tanker) flies its run, the tanker with a fighter in tow.
    /// </summary>
    public sealed partial class FiringRange
    {
        internal enum Scene
        {
            None,
            Jammer,
            Interceptor,
            Repair,
            Fortify,
            Command,
            CounterBattery,
            Breach,
            Flares,
            Emp,
            Shield,
            Smoke,
            Recon,
            Resupply,
            Dome,
            Wingman,
            // Test feedback 19P: towers with nothing to shoot show what they do.
            Relay,
            Teeth,
            Minefield,
            Depot,
            Supply,
            // Play-test 13: utility vehicles that do not shoot do their job.
            MineClear,
            AntiDrone,
            Ferry,
        }

        private Scene _scene;
        private bool _staged;

        /// <summary>Friendly vehicles the scene set up (a repair drop's patients too).</summary>
        private readonly List<Vehicle> _friends = new();

        /// <summary>Enemy sparring partners and whom each one shoots at.</summary>
        private readonly List<(Vehicle who, Vehicle at)> _attackers = new();

        /// <summary>Friends knocked back down once they have healed past a share, so a repair keeps showing.</summary>
        private readonly List<(Vehicle who, float above, float hit)> _wounded = new();

        /// <summary>Obstacles for a breacher, and when the last lot went down.</summary>
        private readonly List<Vehicle> _obstacles = new();

        private Vehicle _counterGun;
        private float _pulseAt;
        private double _homeAt = -1;

        internal static Scene SceneFor(VehicleDef def)
        {
            if (def.Relay != null) return Scene.Relay;
            if (def.Obstacle) return Scene.Teeth;
            if (def.Mines is { Spread: > 0f }) return Scene.Minefield;
            if (def.Utility is { Rearm: > 1f }) return Scene.Depot;
            if (def.Utility is { Supply: > 0 }) return Scene.Supply;
            // Prompt 17 C: a shield dome (carrier or generator) takes the enemy's fire on its friends; a wingman pulls SAMs off its leader.
            if (def.Dome != null) return Scene.Dome;
            if (def.Wingman != null) return Scene.Wingman;
            if (def.Jammer > 0f) return Scene.Jammer;
            if (def.Aps != null) return Scene.Interceptor;
            // The ammunition carrier (prompt 13 F.2): launchers beside it reload three times as fast.
            if (def.RearmAura != null && def.RepairAura == null) return Scene.Resupply;
            if (def.RepairAura != null || def.RearmAura != null) return Scene.Repair;
            if (def.FortifyAura != null) return Scene.Fortify;
            if (def.CommandAura != null) return Scene.Command;
            if (def.CounterBattery != null) return Scene.CounterBattery;
            if (def.Breacher) return Scene.Breach;
            if (def.MineProof) return Scene.MineClear;
            if (def.Microwave != null || def.DroneHunt != null) return Scene.AntiDrone;
            foreach (var skill in def.Skills)
            {
                if (def.Flying && skill.Kind == SkillKind.Flares) return Scene.Flares;
                if (skill.Kind == SkillKind.Smoke && skill.Trigger is SkillTrigger.UnderFire or SkillTrigger.EnemyInRange) return Scene.Smoke;
            }
            // A reconnaissance drone: what it sees, its side sees.
            if (def.Flying && def.Drone && def.VisionRange >= 80f) return Scene.Recon;
            // An unarmed aircraft (a transport, a tanker): it flies its run.
            if (def.Flying && !Armed(def)) return Scene.Ferry;
            return Scene.None;
        }

        private static bool Armed(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.Damage > 0f) return true;
            return false;
        }

        private static Scene SceneFor(SupportDef support) => support?.Kind switch
        {
            SupportKind.Emp => Scene.Emp,
            SupportKind.ShieldDome => Scene.Shield,
            _ => Scene.None,
        };

        /// <summary>Once the targets are up: the scene's other vehicles (see the class notes). Then, every step, keeps it going.</summary>
        private void Stage()
        {
            if (_scene == Scene.None || !_targetsUp) return;
            if (!_staged)
            {
                _staged = true;
                SetUp();
            }
            ReplaceAttackers();
            Towers();
            // Sparring partners keep at their marks (an order can lapse when a target is stunned or hidden).
            if (_world.Tick % 20 == 7)
                foreach (var (who, at) in _attackers)
                    if (who.IsAlive && at != null && at.IsAlive && (who.Order.Kind != OrderKind.Attack || who.Order.Target != at.Id))
                        _world.Submit(new Command(CommandType.Attack, who.Team, new[] { who.Id }, default, at.Id));
            // Patients healed most of the way are hit again, so the repair goes on.
            if (_world.Tick % 20 == 13)
                foreach (var (who, above, hit) in _wounded)
                    if (who.IsAlive && who.Hp > who.MaxHp * above) _world.DebugDamage(who, hit);
        }

        private void SetUp()
        {
            var s = _start;
            switch (_scene)
            {
                case Scene.Jammer:
                    // Enemy missiles and a loitering drone go for the jammer's friends: inside its
                    // field they lose their lock and fly wide.
                    var tank = Friend("main_battle_tank", s + new Vector2(-6f, 4f), dummy: true);
                    var ifv = Friend("ifv", s + new Vector2(6f, 3f), dummy: true);
                    Attacker("atgm_tower", new Vector2(-7f, _far.Y + 18f), tank);
                    Attacker("shahed_truck", new Vector2(8f, _far.Y + 20f), ifv);
                    Widen(_far.Y + 24f);
                    break;
                case Scene.Interceptor:
                    // Rockets and a missile at the vehicles it guards: its laser burns them out of the air.
                    var guarded = Friend("main_battle_tank", s + new Vector2(-6f, 5f), dummy: true);
                    var second = Friend("ifv", s + new Vector2(6f, 4f), dummy: true);
                    Attacker("rocket_technical", new Vector2(-8f, _far.Y + 10f), guarded);
                    Attacker("atgm_tower", new Vector2(9f, _far.Y + 8f), second);
                    Widen(_far.Y + 6f);
                    break;
                case Scene.Repair:
                    // Two knocked-about friends beside it: the engineer patches them up (and they fight on).
                    Wounded(Friend("main_battle_tank", s + new Vector2(-5f, 3f)), 0.55f);
                    Wounded(Friend("ifv", s + new Vector2(5f, 2f)), 0.55f);
                    break;
                case Scene.Depot:
                    // Test feedback 19P: the ammunition depot works at home: the range's home is here, and the
                    // launchers beside it (emptied) reload faster than they would anywhere else.
                    _world.SetRally(0, s);
                    goto case Scene.Resupply;
                case Scene.Resupply:
                    // Two rocket launchers beside it, empty to start with, shooting at the targets: they reload
                    // on the spot three times as fast as on their own, and fire again.
                    foreach (var x in new[] { -6f, 6f })
                    {
                        var launcher = Friend("mlrs", s + new Vector2(x, 3f));
                        _world.DebugEmpty(launcher);
                        var aim = _targets.Count > 0 ? _targets[x < 0f ? 0 : Mathf.Min(1, _targets.Count - 1)] : null;
                        if (aim != null) _world.Submit(new Command(CommandType.Attack, 0, new[] { launcher.Id }, default, aim.Id));
                    }
                    break;
                case Scene.Fortify:
                    // A battered friendly guard tower the sapper shores up as it works.
                    Wounded(Friend("guard_tower", s + new Vector2(-7f, 3f)), 0.5f);
                    break;
                case Scene.Command:
                    // A troop of light tanks under its command, firing faster inside its aura.
                    foreach (var x in new[] { -6f, 6f })
                    {
                        var led = Friend("light_tank", s + new Vector2(x, 2f));
                        var aim = _targets.Count > 0 ? _targets[x < 0f ? 0 : Mathf.Min(1, _targets.Count - 1)] : null;
                        if (aim != null) _world.Submit(new Command(CommandType.Attack, 0, new[] { led.Id }, default, aim.Id));
                    }
                    break;
                case Scene.CounterBattery:
                    // An enemy mortar shells the radar's side: the radar finds it (a red ping) and a
                    // friendly mortar answers it.
                    var shelled = Friend("main_battle_tank", s + new Vector2(-5f, 3f), dummy: true);
                    Attacker("mortar_carrier", new Vector2(10f, _far.Y + 16f), shelled);
                    _counterGun = Friend("mortar_carrier", s + new Vector2(7f, -3f));
                    Widen(_far.Y + 12f);
                    break;
                case Scene.Breach:
                    _world.MakeSparring(_shooter);
                    Obstacles();
                    Widen(_far.Y + 10f);
                    break;
                case Scene.Flares:
                    // An enemy air-defence vehicle fires SAMs at the aircraft: its flares pull them off.
                    _world.MakeSparring(_shooter);
                    Attacker("aa_vehicle", _far + new Vector2(7f, 5f), _shooter);
                    break;
                case Scene.Emp:
                    // The targets are real tanks shelling two friends: the EMP silences them for a while.
                    var a = Friend("main_battle_tank", new Vector2(-6f, -16f), dummy: true);
                    var b = Friend("ifv", new Vector2(6f, -16f), dummy: true);
                    Attacker("main_battle_tank", _far + new Vector2(-9f, -2f), a);
                    Attacker("light_tank", _far + new Vector2(10f, -1f), b);
                    break;
                case Scene.Smoke:
                    // An enemy armoured car comes in close and opens up on it: it lays its smoke screen
                    // (a smoke generator when an enemy is near, an IFV's dischargers under fire).
                    _world.MakeSparring(_shooter);
                    Attacker("armored_car", _start + new Vector2(7f, 6f), _shooter);
                    break;
                case Scene.Dome:
                    // Two friends under its dome, and enemy tanks shelling them: the dome takes the hits, ripples, and breaks.
                    var left = Friend("main_battle_tank", s + new Vector2(-5f, 4f));
                    var right = Friend("ifv", s + new Vector2(5f, 3f));
                    _world.MakeSparring(left);
                    _world.MakeSparring(right);
                    _world.MakeSparring(_shooter);
                    // Beyond the dome's edge: fire from inside it is not stopped (a generator's dome is 25 m).
                    var outside = Mathf.Max(_far.Y + 4f, s.Y + (_shooter.Def.Dome?.Radius ?? 0f) + 6f);
                    Attacker("main_battle_tank", new Vector2(-9f, outside), left);
                    Attacker("main_battle_tank", new Vector2(9f, outside + 2f), right);
                    Widen(outside + 6f);
                    break;
                case Scene.Wingman:
                    // A friendly fighter it flies with, and an enemy SAM vehicle firing at the fighter: some missiles turn onto the drone.
                    var leader = Friend("fighter_jet", s + new Vector2(0f, 8f));
                    _world.MakeSparring(leader);
                    _world.MakeSparring(_shooter);
                    Attacker("aa_vehicle", _far + new Vector2(7f, 5f), leader);
                    break;
                case Scene.MineClear:
                    // An enemy minefield across its way: it drives the lane, the mines going off under its roller.
                    LayLane();
                    Widen(_start.Y + LaneRun + 6f);
                    break;
                case Scene.AntiDrone:
                    // Enemy drone carriers send FPVs and Lancets at the friends beside it: it downs them in the air.
                    var near = Friend("main_battle_tank", s + new Vector2(-6f, 4f), dummy: true);
                    var close = Friend("ifv", s + new Vector2(6f, 3f), dummy: true);
                    Attacker("fpv_carrier", s + new Vector2(-10f, DroneStandOff), near);
                    Attacker("swarm_carrier", s + new Vector2(10f, DroneStandOff + 4f), close);
                    Widen(s.Y + DroneStandOff + 10f);
                    break;
                case Scene.Ferry:
                    // A tanker's receiver: a fighter keeps station behind it, as if taking on fuel.
                    if (_shooter.Def.FixedWing)
                    {
                        _receiver = Friend("fighter_jet", _shooter.Position - SimMath.Forward(_shooter.Heading) * ReceiverBehind);
                        _world.MakeSparring(_receiver);
                    }
                    break;
                case Scene.Shield:
                    // Enemy tanks fire on the friends under the dome: the shield takes the hits.
                    foreach (var f in _friends) _world.MakeSparring(f);
                    if (_friends.Count > 0)
                    {
                        Attacker("main_battle_tank", new Vector2(-9f, 24f), _friends[0]);
                        Attacker("main_battle_tank", new Vector2(9f, 26f), _friends[_friends.Count - 1]);
                    }
                    Widen(20f);
                    break;
                default:
                    SetUpTower();
                    break;
            }
        }

        /// <summary>
        /// The scene steers the shooter itself: a breacher drives into a wall and a watchtower
        /// (its blade knocks them down), backs off to its start, and new ones go up. Else the usual targets.
        /// </summary>
        private bool Directs()
        {
            if (_staged && _scene == Scene.MineClear) return ClearLane();
            if (_staged && _scene == Scene.Ferry) return Ferry();
            if (_scene != Scene.Breach || !_staged) return false;
            if (!_shooter.IsAlive || _world.Tick % 20 != 1) return true;
            Vehicle nearest = null;
            var best = float.MaxValue;
            foreach (var o in _obstacles)
            {
                if (!o.IsAlive) continue;
                var d = Vector2.Distance(o.Position, _shooter.Position);
                if (d < best)
                {
                    best = d;
                    nearest = o;
                }
            }
            if (nearest != null)
            {
                if (_shooter.Order.Kind != OrderKind.Move || Vector2.Distance(_shooter.Order.Point, nearest.Position) > 0.5f)
                    _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, nearest.Position));
                return true;
            }
            var home = _start - new Vector2(0f, 2f);
            if (Vector2.Distance(_shooter.Position, home) < 2.5f)
            {
                // A breather at the start before the next row goes up.
                if (_homeAt < 0) _homeAt = _world.Time;
                if (_world.Time - _homeAt < 3.0) return true;
                _homeAt = -1;
                Obstacles();
                return true;
            }
            if (_shooter.Order.Kind != OrderKind.Move || Vector2.Distance(_shooter.Order.Point, home) > 0.5f)
                _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, home));
            return true;
        }

        /// <summary>How far the mine roller drives up its lane, and the mines' spots along it (from its start).</summary>
        private const float LaneRun = 22f;

        private static readonly Vector2[] LaneMines = { new(0.4f, 6f), new(-0.5f, 10.5f), new(0.3f, 15f), new(-0.2f, 19f) };

        /// <summary>How far ahead the drone carriers stand (inside their drones' reach of the friends).</summary>
        private const float DroneStandOff = 48f;

        /// <summary>How far behind a tanker its receiver keeps station (m), and the transports' run (half its length).</summary>
        private const float ReceiverBehind = 12f, FerryHalf = 26f;

        private bool _laneOut;
        private Vehicle _receiver;

        /// <summary>An enemy minefield across the mine roller's lane (the mine layer's own mines), armed in a moment.</summary>
        private void LayLane()
        {
            if (!_world.Catalog.Vehicles.TryGetValue("mine_layer", out var layer) || layer.Mines == null) return;
            foreach (var spot in LaneMines)
                _world.DebugAddMine(1, _start + spot, layer.Mines, 0.6, 60.0);
            _laneOut = true;
        }

        /// <summary>
        /// The mine roller's clip: up the lane over the mines (each goes off under its roller, which takes the blast), back to
        /// its start, a breather, a new minefield, again.
        /// </summary>
        private bool ClearLane()
        {
            if (!_shooter.IsAlive || _world.Tick % 20 != 1) return true;
            var end = _start + new Vector2(0f, LaneRun);
            var home = _start - new Vector2(0f, 2f);
            if (_laneOut)
            {
                if (Vector2.Distance(_shooter.Position, end) < 2.5f) _laneOut = false;
                else if (_shooter.Order.Kind != OrderKind.Move || Vector2.Distance(_shooter.Order.Point, end) > 0.5f)
                    _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, end));
                return true;
            }
            if (Vector2.Distance(_shooter.Position, home) < 2.5f)
            {
                if (_homeAt < 0) _homeAt = _world.Time;
                if (_world.Time - _homeAt < 3.0) return true;
                _homeAt = -1;
                LayLane();
                return true;
            }
            if (_shooter.Order.Kind != OrderKind.Move || Vector2.Distance(_shooter.Order.Point, home) > 0.5f)
                _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, home));
            return true;
        }

        /// <summary>An unarmed aircraft's clip: it flies its run back and forth across the range (a tanker's receiver behind it).</summary>
        private bool Ferry()
        {
            if (!_shooter.IsAlive || _world.Tick % 20 != 1) return true;
            var a = _start + new Vector2(-FerryHalf, 10f);
            var b = _start + new Vector2(FerryHalf, 10f);
            var to = _shooter.Order.Kind == OrderKind.Move ? _shooter.Order.Point : b;
            if (Vector2.Distance(_shooter.Position, to) < 6f) to = Vector2.Distance(to, a) < 1f ? b : a;
            if (_shooter.Order.Kind != OrderKind.Move || Vector2.Distance(_shooter.Order.Point, to) > 0.5f)
                _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, to));
            if (_receiver != null && _receiver.IsAlive)
                _world.Submit(new Command(CommandType.Move, 0, new[] { _receiver.Id },
                    _shooter.Position - SimMath.Forward(_shooter.Heading) * ReceiverBehind));
            return true;
        }

        /// <summary>
        /// Play-test 14 ("ủi sập tường và tháp canh"): what the bulldozer breaks: a HESCO wall across its way, then the
        /// watchtower behind it (its machine gun firing on the dozer, which cannot fall here). Both already battered, so the
        /// clip shows them coming down in a few strokes each.
        /// </summary>
        private void Obstacles()
        {
            _obstacles.Clear();
            var wallAt = new Vector2(0f, _start.Y + 6.5f);
            if (_world.Map.Contains(wallAt))
            {
                var wall = _world.SpawnVehicle("wall_hesco", 1, wallAt, 0f);
                _world.DebugDamage(wall, 0.6f);
                _obstacles.Add(wall);
            }
            var towerAt = new Vector2(3.5f, _start.Y + 13f);
            if (_world.Map.Contains(towerAt))
            {
                var tower = _world.SpawnVehicle("guard_tower.watch", 1, towerAt, SimMath.HeadingOf(_start - towerAt));
                _world.DebugDamage(tower, 0.4f);
                _obstacles.Add(tower);
            }
        }

        /// <summary>Sim events the scene reacts to: a radar's find turns the friendly mortar on the gun it found.</summary>
        private void Watch(in SimEvent e)
        {
            if (e.Kind == SimEventKind.MineLaid && e.Team == 0) _laid.Add((e.Entity, e.Position, _world.Time));
            if (_scene == Scene.CounterBattery && e.Kind == SimEventKind.GunRevealed && _counterGun != null && _counterGun.IsAlive &&
                _counterGun.Order.Target != e.Other)
                _world.Submit(new Command(CommandType.Attack, 0, new[] { _counterGun.Id }, default, e.Other));
        }

        /// <summary>Per frame: an aura's pulse on the ground around the vehicle (a jammer's field, a command aura).</summary>
        private void Pulse()
        {
            if (_shooter == null || !_shooter.IsAlive || Time.unscaledTime < _pulseAt) return;
            Color colour;
            float size;
            if (TowerPulse(_views.TryGet(_shooter.Id, out var tower) ? tower.Position : new Vector3(_shooter.Position.X, 0f, _shooter.Position.Y))) return;
            switch (_scene)
            {
                case Scene.Jammer:
                    colour = new Color(1.3f, 0.55f, 2.6f, 0.9f);
                    size = 26f;
                    break;
                case Scene.Command:
                    colour = new Color(2.6f, 1.9f, 0.5f, 0.85f);
                    size = 22f;
                    break;
                case Scene.Recon:
                    // Every target in its sight gets a spotting ping, the way its side's map shows them.
                    _pulseAt = Time.unscaledTime + 2f;
                    foreach (var t in _targets)
                        if (t.IsAlive && Vector2.Distance(t.Position, _shooter.Position) <= _shooter.Def.VisionRange &&
                            _views.TryGet(t.Id, out var seen))
                            _effects.AbilityRing(new Vector3(seen.Position.x, 0.1f, seen.Position.z), 7f, new Color(2.4f, 0.4f, 0.25f, 0.8f));
                    return;
                default:
                    return;
            }
            _pulseAt = Time.unscaledTime + (_scene == Scene.Jammer ? 1f : 1.5f);
            var at = _views.TryGet(_shooter.Id, out var view) ? view.Position : new Vector3(_shooter.Position.X, 0f, _shooter.Position.Y);
            _effects.AbilityRing(new Vector3(at.x, 0.1f, at.z), size, colour);
        }

        private Vehicle Friend(string id, Vector2 at, bool dummy = false)
        {
            var friend = _world.SpawnVehicle(id, 0, at, 0f);
            if (dummy) _world.MakeDummy(friend);
            _friends.Add(friend);
            return friend;
        }

        /// <summary>An enemy sparring partner: it moves and fires, and it can be knocked out (a new one comes in its place).</summary>
        private Vehicle Attacker(string id, Vector2 at, Vehicle target)
        {
            var enemy = _world.SpawnVehicle(id, 1, at, MathF.PI);
            _world.MakeSparring(enemy);
            _world.MakeMortal(enemy);
            _attackers.Add((enemy, target));
            _posts.Add((id, at, double.NaN));
            if (target != null) _world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, target.Id));
            return enemy;
        }

        /// <summary>Where each attacker came in and when its replacement is due (NaN: none due).</summary>
        private readonly List<(string id, Vector2 at, double due)> _posts = new();

        /// <summary>Test feedback 19P: a knocked-out attacker is replaced a moment later, on the same mark.</summary>
        private void ReplaceAttackers()
        {
            for (var i = 0; i < _attackers.Count; i++)
            {
                var (who, at) = _attackers[i];
                if (who.IsAlive) continue;
                var (id, post, due) = _posts[i];
                if (double.IsNaN(due))
                {
                    _posts[i] = (id, post, _world.Time + ReplaceAfter + 0.5);
                    continue;
                }
                if (_world.Time < due) continue;
                var enemy = _world.SpawnVehicle(id, 1, post, MathF.PI);
                _world.MakeSparring(enemy);
                _world.MakeMortal(enemy);
                if (_silenced.Remove(who.Id)) _silenced.Add(enemy.Id);
                _attackers[i] = (enemy, at);
                _posts[i] = (id, post, double.NaN);
                if (at != null) _world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, at.Id));
            }
        }

        private void Wounded(Vehicle who, float share)
        {
            _world.DebugDamage(who, share);
            _wounded.Add((who, 0.85f, 0.35f));
        }

        /// <summary>The camera takes in the scene out to <paramref name="y"/> (enemy fire from beyond the targets).</summary>
        private void Widen(float y) => _reach = Mathf.Max(_reach, y * 2f);
    }
}

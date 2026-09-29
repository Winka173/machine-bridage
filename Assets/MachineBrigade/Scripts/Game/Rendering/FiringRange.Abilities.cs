using System;
using System.Collections.Generic;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
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
    /// drone carriers) and plain gun vehicles keep the plain range.
    /// </summary>
    public sealed partial class FiringRange
    {
        private enum Scene
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

        private static Scene SceneFor(VehicleDef def)
        {
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
            foreach (var skill in def.Skills)
            {
                if (def.Flying && skill.Kind == SkillKind.Flares) return Scene.Flares;
                if (skill.Kind == SkillKind.Smoke && skill.Trigger is SkillTrigger.UnderFire or SkillTrigger.EnemyInRange) return Scene.Smoke;
            }
            // A reconnaissance drone: what it sees, its side sees.
            if (def.Flying && def.Drone && def.VisionRange >= 80f) return Scene.Recon;
            return Scene.None;
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
                    Attacker("lancet_truck", new Vector2(8f, _far.Y + 20f), ifv);
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
                    Attacker("ifv", _far + new Vector2(10f, -1f), b);
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
                    Attacker("main_battle_tank", new Vector2(-9f, _far.Y + 4f), left);
                    Attacker("main_battle_tank", new Vector2(9f, _far.Y + 6f), right);
                    Widen(_far.Y + 10f);
                    break;
                case Scene.Wingman:
                    // A friendly fighter it flies with, and an enemy SAM vehicle firing at the fighter: some missiles turn onto the drone.
                    var leader = Friend("fighter_jet", s + new Vector2(0f, 8f));
                    _world.MakeSparring(leader);
                    _world.MakeSparring(_shooter);
                    Attacker("aa_vehicle", _far + new Vector2(7f, 5f), leader);
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
            }
        }

        /// <summary>
        /// The scene steers the shooter itself: a breacher drives into a row of dragon's teeth
        /// (its blade flattens them), backs off to its start, and a new row goes up. Else the usual targets.
        /// </summary>
        private bool Directs()
        {
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

        /// <summary>A row of enemy dragon's teeth across the breacher's way, between it and the targets.</summary>
        private void Obstacles()
        {
            _obstacles.Clear();
            foreach (var x in new[] { -3f, 3f })
            {
                var at = new Vector2(x, _start.Y + 5.5f);
                if (_world.Map.Contains(at)) _obstacles.Add(_world.SpawnVehicle("dragons_teeth", 1, at, 0f));
            }
        }

        /// <summary>Sim events the scene reacts to: a radar's find turns the friendly mortar on the gun it found.</summary>
        private void Watch(in SimEvent e)
        {
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

        private void Attacker(string id, Vector2 at, Vehicle target)
        {
            var enemy = _world.SpawnVehicle(id, 1, at, MathF.PI);
            _world.MakeSparring(enemy);
            _attackers.Add((enemy, target));
            if (target != null) _world.Submit(new Command(CommandType.Attack, 1, new[] { enemy.Id }, default, target.Id));
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

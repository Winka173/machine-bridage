using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// The detail page's "In action" tab: a small battle of its own in which the vehicle shoots
    /// at targets that stand still and cannot fire back: the real simulation, the real models and
    /// effects, seen by the preview camera. It runs only while the tab is open, when the lobby
    /// battle is resting, and everything in it lives on the preview camera's layer, so the two
    /// never mix. Test feedback 19P: the unit shown never runs out of ammunition; the enemy can be
    /// knocked out, and a new one comes in for each one lost; aircraft glide in and nobody fires at
    /// anything before it is in the picture.
    /// </summary>
    public sealed partial class FiringRange : IDisposable
    {
        private const float Step = 0.05f;

        /// <summary>How long a knocked-out target burns before its replacement comes in.</summary>
        private const double ReplaceAfter = 2.5;

        private readonly SimWorld _world;
        private readonly ViewRegistry _views;
        private readonly MineViews _mines;
        private readonly EffectsDirector _effects;
        private readonly Transform _root;
        private readonly Camera _camera;
        private readonly int _layer;
        private Vehicle _shooter;
        private readonly string _id;

        /// <summary>A fire support being shown instead of a vehicle: its card id, and when it is called next.</summary>
        private readonly SupportDef _support;
        private double _nextStrike;
        private readonly Vector2 _start;
        private float _goneFor;
        private readonly List<Vehicle> _targets = new();

        /// <summary>Each target's card and spot, and when its replacement is due (NaN: none due).</summary>
        private readonly List<(string id, Vector2 at, double due)> _slots = new();

        /// <summary>Replacements driving up to their spots (they hold their fire and become targets on arrival).</summary>
        private readonly List<(Vehicle who, Vector2 at)> _arriving = new();

        /// <summary>Vehicles a scene keeps quiet for now, whatever is in the picture.</summary>
        private readonly HashSet<EntityId> _silenced = new();

        private float _accumulator;
        private float _layerAt;
        private Vector3 _look;
        private float _reach;

        /// <summary>Development capture: how much closer than usual the camera frames the vehicle (1: as on the detail page).</summary>
        public static float Zoom = 1f;

        /// <summary>The range's events for the sound (its shots and blasts), step by step.</summary>
        public System.Action<IReadOnlyList<Sim.Events.SimEvent>> Sounds;

        /// <summary>Where the camera looks: the range is heard from here.</summary>
        public Vector3 Look => _look;

        /// <summary>Development capture: every simulation event of the range, as it happens (time, event).</summary>
        public static System.Action<float, Sim.Events.SimEvent> Log;

        public FiringRange(Catalog catalog, MaterialLibrary materials, MeshLibrary meshes, ModelLibrary models, Camera camera, int layer,
            string vehicleId)
        {
            _camera = camera;
            _layer = layer;
            _root = new GameObject("Firing Range").transform;
            var flier = catalog.Vehicles.TryGetValue(vehicleId, out var shown) && shown.Flying;
            var strike = shown == null;
            // An aircraft needs room for its circuit (a pylon turn is 40-70 m across), a fire support for its run.
            // Play-test 12: a boss's scene (a target per gun, at its reach) needs the room an aircraft's circuit does.
            var boss = shown != null && shown.Boss;
            var map = new MapDefinition("range", flier || strike || boss ? 220f : 90f,
                new[] { new TeamStart(0, new Vector2(0f, -70f)), new TeamStart(1, new Vector2(0f, 70f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            _world = new SimWorld(catalog, map, seed: 11);
            _world.EnableEconomy(new TeamEconomy(0));
            _world.EnableEconomy(new TeamEconomy(1));
            _views = new ViewRegistry(models, meshes, materials, _root, 0);
            // Play-test 14 (lane L): the preview camera draws real shadows now (UnitPreview); with shadows Off every vehicle
            // gets the soft disc instead, as in a match.
            _views.BlobShadows = Match.MatchSettings.Options.Shadows == Match.ShadowLevel.Off;
            _mines = new MineViews(models, _root, -1);
            // The effects need a battlefield camera for culling and the view's focus; this one only
            // wraps the preview camera, which is put back the way the preview wants it below.
            var rts = new RtsCamera(camera, 90f, Vector3.zero);
            camera.orthographic = false;
            camera.fieldOfView = 36f;
            camera.nearClipPlane = 0.5f;
            camera.farClipPlane = 400f;
            _effects = new EffectsDirector(catalog, materials, meshes, models, rts, _root, EffectBudget.Eco);

            // Prompt 34 L8: every blast and warning of the shown unit gets its ring at its real size.
            _effects.PreviewRings = true;

            _id = vehicleId;
            if (!catalog.Vehicles.TryGetValue(vehicleId, out var def))
            {
                // A fire support: a group of targets in the middle, the support called on them.
                catalog.TryGetSupport(vehicleId, out _support);
                _world.EnableEconomy(new TeamEconomy(0, 999f, income: 50f, bank: 999f));
                _start = new Vector2(0f, -30f);
                _far = new Vector2(0f, 6f);
                _ground = true;
                _air = false;
                _reach = 22f;
                _nextStrike = 1.2;
                // Friendly vehicles by the targets for a repair or reinforcement drop to work on.
                if (_support != null && _support.Kind is SupportKind.Repair or SupportKind.ShieldDome)
                    for (var i = 0; i < 3; i++)
                    {
                        var friend = _world.SpawnVehicle(i == 1 ? "main_battle_tank" : "ifv", 0, new Vector2(-6f + i * 6f, -2f), 0f);
                        _world.DebugDamage(friend, 0.65f);
                        _friends.Add(friend);
                    }
                _scene = SceneFor(_support);
                _stage = PreviewStage.ForRange(materials, _root, PreviewSetting.Ground, PreviewSettings.Biome(), _start.Y, _far.Y, 0f, 0f);
                SetLayer(_root);
                return;
            }
            _scene = SceneFor(def);
            // Prompt 34 L8: the unit in its own setting; a ship stands far enough off for its hull to stay on the water.
            Setting = PreviewSettings.Of(def);
            var distance = TowerScene ? TowerDistance : TargetDistance(def);
            if (Setting == PreviewSetting.Sea) distance = PreviewSettings.SeaDistance(def, distance);
            _start = new Vector2(0f, -distance * 0.5f);
            // Play-test 14 (lane G): a train stands wholly on the range's track, its front a few metres short of the buffer stop
            // (the track ends RailEndBack before the targets' line); wave M2's long trains stood half off its end.
            var train = Setting == PreviewSetting.Rail ? Mathf.Max(def.Length, def.ModelLength) : 0f;
            if (train > 0f) _start = new Vector2(0f, Mathf.Min(_start.Y, distance * 0.5f - RailEndBack - RailStopGap - train * 0.5f));
            // Play-test 12: a naval boss mid-range, the shore well past its bow, its line abreast of targets on its beam.
            _bossShow = def.Boss;
            var seaBoss = def.Boss && Setting == PreviewSetting.Sea;
            if (seaBoss) _start = BossSeaStart;
            // Play-test 13: a naval boss lies along the beach (its line abreast between it and the shore).
            _shooter = _world.SpawnVehicle(vehicleId, 0, _start, seaBoss ? BossSeaHeading : 0f);
            // A tower on show never falls (a relay under fire, a shield generator shelled).
            if (def.Static) _world.MakeSparring(_shooter);
            _ground = HitsGround(def);
            _air = HitsAir(def);
            _far = new Vector2(0f, distance * 0.5f);
            if (seaBoss) _far = new Vector2(0f, _start.Y + BossSeaFar(catalog, def));
            _reach = distance;
            // Lying along the beach, a naval boss reaches towards the shore by half its beam, not half its length.
            _stage = PreviewStage.ForRange(materials, _root, Setting, PreviewSettings.Biome(), _start.Y, _far.Y,
                seaBoss ? def.Width : train > 0f ? train : def.Length, seaBoss ? def.Length : def.Width);
            SetLayer(_root);
        }

        /// <summary>Play-test 14 (lane G): how far before the targets' line the range's track ends (PreviewStage.ForRange's own).</summary>
        internal const float RailEndBack = 8f;

        /// <summary>Play-test 14 (lane G): metres a train on the range stands short of the track's buffer stop.</summary>
        internal const float RailStopGap = 3f;

        /// <summary>Prompt 34 L8: the setting the range stands its unit in (<see cref="PreviewSettings.Of"/>).</summary>
        public PreviewSetting Setting { get; } = PreviewSetting.Ground;

        /// <summary>The ground, sea, track or pad under the range (<see cref="PreviewStage"/>).</summary>
        private readonly PreviewStage _stage;

        /// <summary>Prompt 34 L8: a coastal gun's target, a ship out at sea (it fires on ships only).</summary>
        internal const string ShipTarget = "missile_boat";

        /// <summary>
        /// Far enough for artillery's minimum range, near enough to see the vehicle and its targets in one frame. Play-test 8
        /// A (DECISIONS 22Q): set by the main weapon and the others that reach about as far. Play-test 7's short self-defence
        /// machine guns (18-21 m) had pulled every target in to 12 m, which put the SAM launcher's helicopter right overhead
        /// at the top edge of the picture, where nobody may fire at it (<see cref="HoldUntilFramed"/>): its missiles never flew.
        /// </summary>
        internal static float TargetDistance(VehicleDef def)
        {
            var main = def.Mounts.Count > 0 && def.Mounts[0].Weapon.Damage > 0f ? def.Mounts[0].Weapon.Range : 0f;
            var reach = float.MaxValue;
            var minimum = 0f;
            foreach (var m in def.Mounts)
            {
                if (m.Weapon.Damage <= 0f) continue;
                minimum = Mathf.Max(minimum, m.Weapon.MinRange);
                if (m.Weapon.Range < main * ShortReach) continue;
                reach = Mathf.Min(reach, m.Weapon.Range);
            }
            if (reach == float.MaxValue) reach = 20f;
            var d = Mathf.Clamp(reach * 0.7f, 10f, 42f);
            return Mathf.Max(d, minimum + 6f);
        }

        /// <summary>A secondary weapon reaching less than this share of the main one's range does not set the targets' distance.</summary>
        internal const float ShortReach = 0.6f;

        private static bool HitsGround(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.CanEngage(false, def) && m.Weapon.Damage > 0f) return true;
            return false;
        }

        private static bool HitsAir(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                // Prompt 25 G: a gun with an air-burst round shows it on a helicopter (and its change of rounds).
                if (m.Weapon.CanEngage(true, def) && m.Weapon.Damage > 0f) return true;
            return false;
        }

        private readonly bool _ground, _air;
        private readonly Vector2 _far;

        /// <summary>
        /// A fire support's clip: called on the targets (a line strike flies across them) every
        /// few seconds, its cooldown and price waived; items get a fresh stock.
        /// </summary>
        private void CallSupport()
        {
            if (_support == null || _world.Time < _nextStrike || !_targetsUp) return;
            if (!_world.TryGetEconomy(0, out var economy)) return;
            // A fresh purse each time: no cooldown, no price, a new item.
            var fresh = new TeamEconomy(0, 999f, income: 50f, bank: 999f);
            if (_support.Consumable) fresh.Items[_support.Id] = 9;
            _world.EnableEconomy(fresh);
            // A field tower lands on our side of the targets; remote mines across the runner's road.
            var at = _support.Kind switch
            {
                SupportKind.Tower => new Vector2(-6f, -14f),
                SupportKind.Minefield => new Vector2(0f, -8f),
                _ => _far + new Vector2(0f, 2f),
            };
            var towards = _support.IsLine ? at + new Vector2(1f, 0f) : _support.Kind == SupportKind.Tower ? at + new Vector2(0f, 1f) : default;
            _world.Submit(Command.Strike(0, _support.Id, at, towards));
            // An escort (the sky gunship) stays its whole time: the next one is called as it leaves.
            var gap = _support.Kind == SupportKind.Escort ? _support.Duration + 2.0
                : _support.Kind == SupportKind.Reinforce ? 14.0 : _support.Kind == SupportKind.Smoke ? 10.0 : 7.0;
            _nextStrike = _world.Time + gap + _support.Delay + (_support.Kind == SupportKind.Escort ? 0.0 : _support.Duration * 0.5);
        }
        private bool _targetsUp;

        /// <summary>
        /// The targets are set up a moment after the vehicle, once it is drawn on its spot: a
        /// first shot fired in the first instant would leave from a vehicle not yet seen.
        /// </summary>
        private void PlaceTargets()
        {
            if (_targetsUp || _world.Time < 0.8) return;
            _targetsUp = true;
            // A tower's own scene brings its own enemies; the depot's launchers want the usual targets.
            if (TowerScene && _scene != Scene.Depot) return;
            // Play-test 12: a boss gets an enemy for every gun, in its reach and arc, laid out for its domain.
            if (_bossShow && _shooter != null)
            {
                BossTargets();
                return;
            }
            // Prompt 34 L8: a gun that fires on ships only gets a ship at sea (the range's other targets are on land).
            if (_shooter != null && _shooter.Def.NavalOnly)
            {
                Target(ShipTarget, _far + new Vector2(0f, 4f));
                return;
            }
            if (_ground || _scene == Scene.Depot)
                foreach (var (id, at) in GroundTargets)
                    Target(id, _far + at);
            if (_air) Target("attack_helicopter", _far + new Vector2(_ground ? 10f : 0f, _ground ? -6f : 0f));
            // SEAD wants an air defence to hit.
            if (_support != null && _support.Kind == SupportKind.Sead) Target("aa_vehicle", _far + new Vector2(8f, 4f));
        }

        /// <summary>
        /// Play-test 5 (DECISIONS 20V): the ground targets, one of each armour level from 0 to 4 (a jeep, an armoured car,
        /// a light tank, a battle tank, a heavy tank), so a weapon's effect on each reads side by side. None of them lays
        /// smoke (the IFV's dischargers hid the clip), and none fires back (they are dummies).
        /// </summary>
        internal static readonly (string id, Vector2 at)[] GroundTargets =
        {
            ("main_battle_tank", new Vector2(-4f, 0f)),
            ("light_tank", new Vector2(5f, 3f)),
            ("heavy_tank", new Vector2(0f, 9f)),
            ("armored_car", new Vector2(-8.5f, 6f)),
            ("scout_jeep", new Vector2(8.5f, 9f)),
        };

        /// <summary>Remote mines' clip: an armoured car drives to and fro across the minefield (a new one when a mine gets it).</summary>
        private void RunTheMines()
        {
            if (_support == null || _support.Kind != SupportKind.Minefield || !_targetsUp) return;
            if (_runner == null || !_runner.IsAlive)
            {
                if (_world.Time < _runnerAt) return;
                _runner = _world.SpawnVehicle("armored_car", 1, new Vector2(-24f, -8f), MathF.PI * 0.5f);
                _silenced.Add(_runner.Id);
                _runnerLeg = 1;
            }
            if (_runner.IsMoving || _runner.Order.Kind == Sim.Entities.OrderKind.Move) return;
            _runnerLeg = -_runnerLeg;
            _world.Submit(new Command(CommandType.Move, 1, new[] { _runner.Id }, new Vector2(24f * -_runnerLeg, -8f)));
            _runnerAt = _world.Time + 3.0;
        }

        private Vehicle _runner;
        private int _runnerLeg = 1;
        private double _runnerAt;

        /// <summary>A range target: it stands still and never fires, but it can be knocked out (a new one comes in).</summary>
        private void Target(string id, Vector2 at, float heading = MathF.PI)
        {
            var target = _world.SpawnVehicle(id, 1, at, heading);
            _world.MakeDummy(target);
            _world.MakeMortal(target);
            _targets.Add(target);
            _slots.Add((id, at, double.NaN));
            _headings.Add(heading);
        }

        /// <summary>
        /// Test feedback 19P: a knocked-out target burns for a moment, then a new one comes in: an
        /// aircraft flies onto the spot, a ground vehicle drives up to it from beyond (holding its
        /// fire) and stands as a target once there.
        /// </summary>
        private void KeepTargets()
        {
            for (var i = 0; i < _targets.Count; i++)
            {
                var (id, at, due) = _slots[i];
                if (_targets[i].IsAlive) continue;
                if (double.IsNaN(due))
                {
                    // Play-test 13: a sunk ship's replacement waits until its wreck has gone under (never one inside the other).
                    var afloat = _world.Catalog.Vehicles.TryGetValue(id, out var lost) && lost.Naval != null;
                    _slots[i] = (id, at, _world.Time + ReplaceAfter + (afloat ? ShipReplaceExtra : 0.0));
                    continue;
                }
                if (_world.Time < due) continue;
                var flies = _world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Flying;
                // Play-test 14 (lane J): a ship's replacement waits until the wreck on its spot is under the water (the Sim's
                // wreck, not a guessed time), so the new ship never sits inside the sinking one.
                if (def != null && def.Naval != null && _world.Wrecks.Blocks(at, def.HullBound, true)) continue;
                _slots[i] = (id, at, double.NaN);
                // Play-test 12: a ship of a naval boss's line comes back on its spot too (nothing drives up on the water).
                var heading = i < _headings.Count ? _headings[i] : MathF.PI;
                if (flies || (def != null && def.Naval != null))
                {
                    var target = _world.SpawnVehicle(id, 1, at, heading);
                    _world.MakeDummy(target);
                    _world.MakeMortal(target);
                    _targets[i] = target;
                    continue;
                }
                // Play-test 14 (lane J): the burning wreck still stands on the spot (solid in the Sim): the new one comes to a clear
                // spot beside it, not into the wreck ("tới chính xác vị trí vừa chết, clip vào trong luôn xác").
                var spot = def != null ? ClearSpot(def, at) : at;
                // From beyond the spot, a little off the wreck's line (a boss's targets from out beyond theirs, away from it).
                var from = spot + new Vector2(i % 2 == 0 ? -3f : 3f, 16f);
                if (_bossShow && Vector2.DistanceSquared(at, _start) > 1f) from = spot + Vector2.Normalize(at - _start) * 16f;
                var coming = _world.SpawnVehicle(id, 1, Inside(from), _bossShow ? heading : MathF.PI);
                _silenced.Add(coming.Id);
                _world.Submit(new Command(CommandType.Move, 1, new[] { coming.Id }, spot));
                _arriving.Add((coming, spot));
                _targets[i] = coming;
            }
            for (var i = _arriving.Count - 1; i >= 0; i--)
            {
                var (who, at) = _arriving[i];
                if (!who.IsAlive)
                {
                    _arriving.RemoveAt(i);
                    continue;
                }
                if (Vector2.Distance(who.Position, at) > 1.5f && (who.IsMoving || who.Order.Kind == OrderKind.Move)) continue;
                _world.MakeDummy(who);
                _world.MakeMortal(who);
                _silenced.Remove(who.Id);
                _arriving.RemoveAt(i);
            }
        }

        /// <summary>
        /// Test feedback 19P: nobody fires at what is not yet in the picture (an aircraft still flying
        /// in, a target beyond the edge); the shown unit never runs out of rounds.
        /// </summary>
        private void HoldUntilFramed()
        {
            if (_shooter != null && _shooter.IsAlive) _world.Refill(_shooter);
            var all = _world.Vehicles;
            for (var i = 0; i < all.Count; i++)
            {
                var v = all[i];
                if (!v.IsAlive || v.Dummy || v.Def.Mounts.Count == 0) continue;
                var aimed = v.Order.Kind == OrderKind.Attack ? v.Order.Target : v.Target;
                var hold = _silenced.Contains(v.Id) || (aimed.IsValid && !Framed(aimed));
                if (v.HoldFire != hold) _world.HoldFire(v, hold);
            }
        }

        /// <summary>
        /// Play-test 14 (lane J): where a replacement of <paramref name="def"/> stands: its <paramref name="at"/>, or, while a
        /// wreck (or another hull) is still there, the nearest clear spot beside it (either side across the line of fire, a
        /// hull's length and more apart, then further back), inside the range. Its own spot again once the wreck has gone.
        /// </summary>
        private Vector2 ClearSpot(VehicleDef def, Vector2 at)
        {
            var room = def.HullBound + 0.8f;
            if (Clear(at, room)) return at;
            var along = Vector2.DistanceSquared(at, _start) > 1f ? Vector2.Normalize(at - _start) : new Vector2(0f, 1f);
            var across = new Vector2(along.Y, -along.X);
            var step = def.HullBound * 2f + 1.5f;
            for (var k = 1; k <= 3; k++)
            {
                var right = Inside(at + across * (step * k));
                if (Clear(right, room)) return right;
                var left = Inside(at - across * (step * k));
                if (Clear(left, room)) return left;
                var back = Inside(at + along * (step * k));
                if (Clear(back, room)) return back;
            }
            return at;
        }

        /// <summary>Play-test 14 (lane J): no ground wreck and no other ground hull within <paramref name="room"/> of <paramref name="p"/>.</summary>
        private bool Clear(Vector2 p, float room)
        {
            if (_world.Wrecks.Blocks(p, room, false)) return false;
            var all = _world.Vehicles;
            for (var i = 0; i < all.Count; i++)
            {
                var v = all[i];
                if (!v.IsAlive || v.Flying) continue;
                var reach = room + v.Def.HullBound;
                if (Vector2.DistanceSquared(v.Position, p) < reach * reach) return false;
            }
            return true;
        }

        /// <summary>A point kept a few metres inside the range's edges.</summary>
        private Vector2 Inside(Vector2 p)
        {
            var map = _world.Map;
            var c = map.Centre;
            float x = map.Width * 0.5f - 4f, y = map.Length * 0.5f - 4f;
            return new Vector2(Math.Clamp(p.X, c.X - x, c.X + x), Math.Clamp(p.Y, c.Y - y, c.Y + y));
        }

        /// <summary>Whether a vehicle is drawn in the picture, flown in (a small margin inside the edges).</summary>
        private bool Framed(EntityId id)
        {
            if (!_views.TryGet(id, out var view) || view.Root == null || !view.Arrived) return false;
            var p = _camera.WorldToViewportPoint(view.Position + Vector3.up);
            return p.z > 0f && p.x > 0.03f && p.x < 0.97f && p.y > 0.03f && p.y < 0.97f;
        }

        /// <summary>Per frame: steps the little battle, keeps the vehicle on its targets and the camera on the scene.</summary>
        public void Tick(float dt)
        {
            _accumulator = Mathf.Min(_accumulator + dt, Step * 4f);
            while (_accumulator >= Step)
            {
                _accumulator -= Step;
                PlaceTargets();
                CallSupport();
                RunTheMines();
                KeepTargets();
                Stage();
                if (_shooter != null && !Directs()) Order();
                HoldUntilFramed();
                BossShow();
                _world.Step(Step);
                _views.SnapshotAll();
                foreach (var e in _world.Events)
                    if (e.Kind == Sim.Events.SimEventKind.VehicleSpawned && _world.TryGetVehicle(e.Entity, out var spawned))
                        _views.Add(spawned).GentleArrival = true;
                foreach (var e in _world.Events) Watch(e);
                if (Log != null)
                    foreach (var e in _world.Events)
                        Log((float)_world.Time, e);
                Sounds?.Invoke(_world.Events);
                // Play-test 12: the range's rounds fly on its own Sim's clock (a shared one froze them behind the menu).
                _effects.Clock.Launching(_world.Time - Step);
                _effects.Consume(_world.Events, _views, null);
                _world.ClearEvents();
            }
            // A car bomb (or anything knocked out) comes back for another go.
            _goneFor = _shooter == null || _shooter.IsAlive ? 0f : _goneFor + dt;
            if (_goneFor > 2.5f)
            {
                _goneFor = 0f;
                _shooter = _world.SpawnVehicle(_id, 0, _start, 0f);
            }
            // The range's Sim time as its views draw it (they interpolate the last step by the accumulator).
            _effects.Clock.Advance(_world.Time - Step * (1.0 - _accumulator / Step), false, dt);
            _effects.Tick(_views);
            _stage?.Tick(Time.unscaledTime);
            _mines.Update(_world);
            Pulse();
            Frame(dt);
            _views.Render(_accumulator / Step, _camera.transform.rotation);
            // Rounds leave from the barrels as they have just been drawn.
            _effects.LaunchShots(_views);
            // New effects and views are made on the default layer: move them onto the preview's.
            if (Time.unscaledTime >= _layerAt)
            {
                _layerAt = Time.unscaledTime + 0.3f;
                SetLayer(_root);
            }
        }

        /// <summary>Keeps the vehicle attacking the nearest target it can hit (a car bomb goes round again: it is rebuilt).</summary>
        private void Order()
        {
            if (LayMines()) return;
            // Not before the views are up: the first shot would leave from nowhere.
            if (!_shooter.IsAlive || _world.Tick % 20 != 1 || _world.Time < 0.6) return;
            // Stay on the target being shot at until it goes down (an aircraft circling it would
            // otherwise be sent to whichever target happened to be nearest).
            if (_world.TryGetVehicle(_shooter.Order.Target, out var current) && current.IsAlive && _shooter.Def.Weapon.CanEngage(current.Flying, _shooter.Def)) return;
            Vehicle best = null;
            var bestDistance = float.MaxValue;
            foreach (var t in _targets)
            {
                if (!t.IsAlive || !_shooter.Def.Weapon.CanEngage(t.Flying, _shooter.Def)) continue;
                var d = Vector2.Distance(t.Position, _shooter.Position);
                if (d < bestDistance)
                {
                    best = t;
                    bestDistance = d;
                }
            }
            if (best != null && _shooter.Order.Target != best.Id)
                _world.Submit(new Command(CommandType.Attack, 0, new[] { _shooter.Id }, default, best.Id));
        }

        /// <summary>
        /// From beside and a little behind the vehicle, high enough to see the rounds land. A gunship
        /// circling its target is framed on the whole turn instead, so it flies round inside the picture.
        /// </summary>
        private void Frame(float dt)
        {
            Vector3 centre;
            float span;
            var orbiter = _shooter != null && _shooter.Def.Orbit ? _shooter.Def : _support != null ? EscortOrbiter() : null;
            // Play-test 12: a boss's scene (its hull and a target per gun) framed whole.
            if (orbiter == null && BossFrame(out var whole, out var reach))
            {
                centre = whole;
                span = reach;
            }
            else if (orbiter != null)
            {
                var radius = Mathf.Max(orbiter.OrbitRadius, 14f);
                centre = new Vector3(_far.X, orbiter.Altitude * 0.45f, _far.Y);
                span = (radius + 10f + orbiter.Altitude * 0.25f) / Zoom;
            }
            else
            {
                var from = _shooter != null && _views.TryGet(_shooter.Id, out var view) ? view.Position : new Vector3(0f, 0f, -_reach * 0.5f);
                var to = new Vector3(0f, 0f, _reach * 0.5f);
                if (Zoom > 1f) to = Vector3.Lerp(from, to, 1f / Zoom);
                centre = (from + to) * 0.5f + Vector3.up * 1.5f;
                // A big boss (the drone mothership) is stood back from, so it does not fill the picture.
                var bulk = _shooter != null ? Mathf.Max(0f, _shooter.Def.Radius - 3f) * 1.6f : 0f;
                // Play-test 8 A (DECISIONS 22Q): a long hull (the Leviathan's 86 m) by its length as well, so it all fits.
                if (_shooter != null) bulk = Mathf.Max(bulk, Mathf.Max(0f, _shooter.Def.Length * 0.5f - 10f) * 1.2f);
                span = Mathf.Max(Vector3.Distance(from, to) * 0.5f + (8f + bulk) / Zoom, 14f / Zoom);
                // Play-test 5 (DECISIONS 20V): a fire support is framed with the sky it comes out of, so the jets, the
                // bomber, the transport or the incoming rounds are in the picture as well as the impacts.
                var sky = _support != null ? SupportSky(_support) : 0f;
                centre += Vector3.up * sky * 0.42f;
                span += sky * 0.36f / Zoom;
            }
            _look = _look == Vector3.zero ? centre : Vector3.Lerp(_look, centre, 1f - Mathf.Exp(-dt * 3f));
            var distance = span / Mathf.Tan(_camera.fieldOfView * 0.5f * Mathf.Deg2Rad) * 0.95f;
            _camera.transform.position = _look + new Vector3(0.95f, 0.75f, -0.45f).normalized * distance;
            _camera.transform.LookAt(_look);
        }

        /// <summary>How high what delivers a fire support flies over the targets (StrikeEffects' altitudes), in metres.</summary>
        internal static float SupportSky(SupportDef support) => support.Kind switch
        {
            SupportKind.Airstrike => support.Id == "air_raid" ? 32f : 24f,
            SupportKind.Sead => 24f,
            SupportKind.CruiseMissile => support.Id == "moab" ? 44f : 24f,
            SupportKind.Reinforce or SupportKind.Repair or SupportKind.ShieldDome or SupportKind.Tower => 30f,
            SupportKind.Scan => 22f,
            SupportKind.Barrage or SupportKind.Emp => 20f,
            _ => 14f,
        };

        /// <summary>An escort support's circling aircraft (the sky gunship), framed on its whole turn like a shown gunship.</summary>
        private VehicleDef EscortOrbiter()
        {
            if (_support.Kind != SupportKind.Escort || _support.Units == null) return null;
            foreach (var id in _support.Units)
                if (_world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Orbit) return def;
            return null;
        }

        private void SetLayer(Transform t)
        {
            t.gameObject.layer = _layer;
            foreach (Transform child in t) SetLayer(child);
        }

        public void Dispose()
        {
            _effects.Dispose();
            _views.Dispose();
            _stage?.Dispose();
            if (_root != null) UnityEngine.Object.Destroy(_root.gameObject);
        }
    }
}

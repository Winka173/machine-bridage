using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Test feedback 19P: the In action clips of what does not shoot, or does its work on others.
    /// <list type="bullet">
    /// <item>The CP relay pays its side while enemy fire keeps off it: the clip counts the CP it has paid and
    /// its rate, and an armoured car shoots at it now and then, when it pays nothing for its quiet time
    /// (<see cref="Readout"/>, drawn over the picture by the detail page; a gold pulse while it pays, red while it is
    /// quiet).</item>
    /// <item>Dragon's teeth: a row of them across the enemy's road; enemy vehicles on their way through have to
    /// go round the ends (or, wire, crawl through), under a friendly tank's gun.</item>
    /// <item>A minefield, and the mine layer once it has sown mines: enemy vehicles drive across over the
    /// armed mines, one after another.</item>
    /// <item>The ammunition depot: the range's home is at the depot, and emptied launchers beside it reload
    /// there faster (the ammunition carrier's scene); the logistics station: the army supply it adds.</item>
    /// </list>
    /// The shield generator, the EW tower and the radar have their scenes in FiringRange.Abilities (the dome, the
    /// jammer and the counter-battery radar).
    /// </summary>
    public sealed partial class FiringRange
    {
        /// <summary>How far apart the tower and the enemy's side of its scene are.</summary>
        private const float TowerDistance = 24f;

        private bool TowerScene => _scene is Scene.Relay or Scene.Teeth or Scene.Minefield or Scene.Depot or Scene.Supply;

        /// <summary>
        /// A line of text over the picture (the CP relay's pay, the depot's reload): the detail page shows it
        /// while it is set. Its alert state (the relay under fire) draws it in the warning colour.
        /// </summary>
        public string Readout { get; private set; }

        public bool ReadoutAlert { get; private set; }

        /// <summary>CP the relay has paid since the clip began.</summary>
        private float _paid;

        /// <summary>The armoured car that shoots at the relay now and then.</summary>
        private Vehicle _raider;

        /// <summary>Mines of ours laid in this clip: which, where, and when (they arm a moment later).</summary>
        private readonly List<(EntityId id, Vector2 at, double when)> _laid = new();

        /// <summary>Enemy vehicles driving across the tower's (or the mine layer's) ground, each with where it is headed.</summary>
        private readonly List<(Vehicle who, Vector2 to)> _crossers = new();

        private double _nextCrosser = 3.0;
        private int _crossed;

        private void SetUpTower()
        {
            var s = _start;
            switch (_scene)
            {
                case Scene.Relay:
                    // It raids the relay now and then (Towers keeps it quiet in between).
                    _raider = Attacker("armored_car", new Vector2(8f, _far.Y + 4f), _shooter);
                    _silenced.Add(_raider.Id);
                    break;
                case Scene.Teeth:
                    // The shown block in the middle of a row of them, a friendly tank behind covering the ends.
                    foreach (var x in new[] { -9f, -4.5f, 4.5f, 9f })
                        _world.MakeSparring(Friend(_shooter.Def.Id, s + new Vector2(x, 0f)));
                    var gun = Friend("main_battle_tank", s + new Vector2(-16f, -6f));
                    _world.MakeSparring(gun);
                    Widen(_far.Y + 6f);
                    break;
                case Scene.Minefield:
                case Scene.Supply:
                    break;
            }
        }

        /// <summary>Every step, once the scene is up: the relay's pay and raids, the enemy crossing the ground, the readouts.</summary>
        private void Towers()
        {
            switch (_scene)
            {
                case Scene.Relay:
                    Relay();
                    break;
                case Scene.Teeth:
                    Cross(_far.Y + 6f, 2, new[] { "armored_car", "ifv", "light_tank" }, _start.Y - 14f, false);
                    break;
                case Scene.Minefield:
                    Cross(_far.Y + 6f, 1, new[] { "armored_car", "ifv", "scout_jeep" }, _start.Y - 14f, true);
                    break;
                case Scene.Depot:
                    Readout = _shooter.Def.Utility != null ? Strings.Format("range.depot", _shooter.Def.Utility.Rearm) : null;
                    ReadoutAlert = false;
                    break;
                case Scene.Supply:
                    if (_world.TryGetEconomy(0, out var economy))
                        Readout = Strings.Format("range.supply", economy.Supply, _shooter.Def.Utility?.Supply ?? 0);
                    ReadoutAlert = false;
                    break;
            }
        }

        /// <summary>
        /// The relay's clip: its pay (while nothing has hit it for its quiet time) counted up, and a raid every
        /// 14 s: the armoured car opens up for a couple of seconds, and the pay stops until the quiet time is over.
        /// </summary>
        private void Relay()
        {
            if (_shooter == null || !_world.TryGetEconomy(0, out var economy)) return;
            var relay = _shooter.Def.Relay;
            _paid += economy.Relay * Step;
            var quiet = relay != null ? (float)(relay.Quiet - (_world.Time - _shooter.LastHitAt)) : 0f;
            ReadoutAlert = economy.Relay <= 0f && quiet > 0f;
            Readout = ReadoutAlert ? Strings.Format("range.relay.quiet", Mathf.Ceil(quiet), _paid)
                : Strings.Format("range.relay", economy.Relay, _paid);
            if (_raider == null || !_raider.IsAlive)
            {
                foreach (var (who, _) in _attackers)
                    if (who.IsAlive && who.Def.Id == "armored_car") _raider = who;
                return;
            }
            var phase = _world.Time % 14.0;
            var raiding = phase >= 6.0 && phase < 8.5;
            if (raiding) _silenced.Remove(_raider.Id);
            else _silenced.Add(_raider.Id);
        }

        /// <summary>
        /// Enemy vehicles, <paramref name="count"/> at a time, driving from <paramref name="fromY"/> across to
        /// <paramref name="toY"/> and back, holding their fire: over our armed mines when <paramref name="overMines"/>,
        /// else straight at the tower's row (they must find their way round). A new one comes in a few seconds
        /// after one is knocked out.
        /// </summary>
        private void Cross(float fromY, int count, string[] kinds, float toY, bool overMines)
        {
            for (var i = _crossers.Count - 1; i >= 0; i--)
            {
                var (who, to) = _crossers[i];
                if (!who.IsAlive)
                {
                    _crossers.RemoveAt(i);
                    _nextCrosser = Math.Max(_nextCrosser, _world.Time + 3.0);
                    continue;
                }
                if (Vector2.Distance(who.Position, to) > 3f && (who.IsMoving || who.Order.Kind == OrderKind.Move)) continue;
                // At the far end: back the other way, over another mine.
                var back = new Vector2(Lane(overMines, who.Position.X), to.Y > (fromY + toY) * 0.5f ? toY : fromY);
                _world.Submit(new Command(CommandType.Move, 1, new[] { who.Id }, back));
                _crossers[i] = (who, back);
            }
            if (_crossers.Count >= count || _world.Time < _nextCrosser) return;
            if (overMines && ArmedMine(0f) == null) return;
            var x = overMines ? Lane(true, 0f) : (_crossed % 2 == 0 ? -2f : 2f);
            var kind = kinds[_crossed % kinds.Length];
            _crossed++;
            var enemy = _world.SpawnVehicle(kind, 1, Inside(new Vector2(x, fromY)), MathF.PI);
            _world.MakeMortal(enemy);
            _silenced.Add(enemy.Id);
            var goal = new Vector2(x, toY);
            _world.Submit(new Command(CommandType.Move, 1, new[] { enemy.Id }, goal));
            _crossers.Add((enemy, goal));
            _nextCrosser = _world.Time + 4.0;
        }

        /// <summary>The x of the next crossing: over an armed mine of ours (away from <paramref name="avoid"/>), else the middle.</summary>
        private float Lane(bool overMines, float avoid)
        {
            if (!overMines) return avoid >= 0f ? -2f : 2f;
            var mine = ArmedMine(avoid);
            return mine?.X ?? 0f;
        }

        /// <summary>
        /// An armed mine of ours still in the ground (laid 2.5 s ago or more), the one farthest across from
        /// <paramref name="avoid"/> (and from the mine layer's own lane position), or null.
        /// </summary>
        private Vector2? ArmedMine(float avoid)
        {
            Vector2? best = null;
            var bestScore = float.MinValue;
            foreach (var m in _world.Mines)
            {
                if (!m.IsAlive || m.Team != 0) continue;
                var laid = -1.0;
                foreach (var l in _laid)
                    if (l.id == m.Id) laid = l.when;
                if (laid < 0 || _world.Time - laid < 2.5) continue;
                var score = Mathf.Abs(m.Position.X - avoid);
                if (_shooter != null && !_shooter.Def.Static) score += Mathf.Abs(m.Position.X - _shooter.Position.X) * 0.5f;
                if (score <= bestScore) continue;
                bestScore = score;
                best = m.Position;
            }
            return best;
        }

        /// <summary>
        /// A mine layer shows what it is for: it drives to and fro across the range sowing its mines, and once
        /// one is armed enemy vehicles drive across over them, one after another.
        /// </summary>
        private bool LayMines()
        {
            if (_shooter.Def.Mines == null || _shooter.Def.Static) return false;
            Cross(_far.Y + 8f, 1, new[] { "ifv", "armored_car", "light_tank" }, _start.Y - 12f, true);
            if (!_shooter.IsAlive || _world.Tick % 20 != 1) return true;
            var y = _start.Y + 6f;
            var left = new Vector2(-10f, y);
            var right = new Vector2(10f, y);
            var going = _shooter.Order.Kind == OrderKind.Move ? _shooter.Order.Point : right;
            if (Vector2.Distance(_shooter.Position, going) < 2.5f || _shooter.Order.Kind != OrderKind.Move)
                _world.Submit(new Command(CommandType.Move, 0, new[] { _shooter.Id }, going == right ? left : right));
            return true;
        }

        /// <summary>The relay's pulse on the ground: gold while it pays, red while it is quiet.</summary>
        private bool TowerPulse(Vector3 at)
        {
            if (_scene != Scene.Relay) return false;
            _pulseAt = Time.unscaledTime + 1f;
            _effects.AbilityRing(new Vector3(at.x, 0.1f, at.z), ReadoutAlert ? 9f : 7f,
                ReadoutAlert ? new Color(2.6f, 0.35f, 0.25f, 0.85f) : new Color(2.6f, 1.9f, 0.5f, 0.85f));
            return true;
        }
    }
}

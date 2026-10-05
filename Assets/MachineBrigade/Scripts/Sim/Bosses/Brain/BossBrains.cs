#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Bosses.BossBrain;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// AI MASTER P0-C (spec 48, Part U): the boss brains of a battle. Each step (BossSystem.Step, before the naval system
    /// sails): phase, mission anchor and corridor for every moving boss; every <see cref="Tun.BrainTicks"/> steps its weapon
    /// picture (targets per mount, active-DPS bearing) and, for a ship, its broadside; then the decision log (section 96).
    /// Deterministic: vehicle-list order, no random numbers; the log never feeds back.
    /// </summary>
    public sealed class BossBrains
    {
        private readonly SimWorld _world;
        private readonly List<BossCorridor> _corridors = new();
        private readonly List<MountSample> _mounts = new();
        private readonly List<TargetSample> _targets = new();
        private readonly List<(float d, int id, TargetSample t)> _scratch = new();

        internal BossBrains(SimWorld world) => _world = world;

        /// <summary>Spec 52 / section 110: steps a boss ship's speed went below 0 (never; the lead's tests assert 0).</summary>
        public int NavalReverseEvents { get; internal set; }

        /// <summary>Reverses asked of a boss ship by the ground traffic rules and refused (ships are never in them; for the tests).</summary>
        public int NavalReverseRefused { get; internal set; }

        /// <summary>Friends asked to clear a boss's corridor so far (spec 33).</summary>
        public int CorridorYields { get; internal set; }

        /// <summary>Spec 33: the corridors reserved this step (ground bosses under way): the API for the traffic lane.</summary>
        public IReadOnlyList<BossCorridor> Corridors => _corridors;

        /// <summary>Whether a ground vehicle of <paramref name="team"/> at <paramref name="p"/> (hull <paramref name="radius"/>) stands in a friendly boss's corridor.</summary>
        public bool InCorridor(int team, Vector2 p, float radius, out BossCorridor corridor)
        {
            foreach (var c in _corridors)
            {
                if (c.Team != team || !c.Holds(p, radius)) continue;
                corridor = c;
                return true;
            }
            corridor = default;
            return false;
        }

        /// <summary>A boss joined: its brain (moving bosses only; a fixed boss has nothing to steer).</summary>
        internal void Join(Vehicle v)
        {
            if (!v.Def.Boss || v.Def.Static || v.Brain != null) return;
            v.Brain = new BossBrain(BossMovementController.CraftOf(v.Def));
        }

        internal void Step(double now)
        {
            _corridors.Clear();
            var slow = _world.Tick % Math.Max(1, Tun.BrainTicks) == 0;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Brain is not { } b) continue;
                BossPhaseController.Update(_world, v, b, now);
                BossMissionController.Update(_world, v, b, now);
                BossMovementController.UpdateCorridor(v, b);
                if (b.HasCorridor) _corridors.Add(b.Corridor);
                if (!slow) continue;
                // AI MASTER P2 Part F5 / R5: a broken part took mounts away: the held broadside is dropped so the next
                // sample (working mounts only) is chosen at once, not after the hysteresis (no keeping a useless side).
                if (_world.Components.MountsChanged(v))
                {
                    b.BroadsideHeld = 0f;
                    b.BroadsideEngaged = false;
                    AI.P2Reasons.Unit(_world, v, AI.DecisionKind.State, AI.P2Reasons.BossBroadsideRecompute);
                }
                BossWeaponDirector.NoteTargets(v, b);
                BossWeaponDirector.Samples(v, _mounts);
                BossWeaponDirector.Targets(_world, v, _mounts, _targets, _scratch);
                b.ActiveDpsFraction = NavalBossMovementController.BearingShare(_mounts, v.Position, v.Heading, _targets, out _);
                if (b.Craft == BossCraft.Naval && v.Def.Naval != null) Broadside(v, b);
                else Land(v, b, now);
                Log(v, b, now);
            }
        }

        /// <summary>Spec 56-57: a ship's broadside offset, on its lane only (not running, not holding, not coming about, surfaced).</summary>
        private void Broadside(Vehicle v, BossBrain b)
        {
            if (_world.Map.Sea is not { } sea || b.LookAhead <= 0f || v.Burrow != Vehicle.BurrowState.Surface || v.Escaping || v.SeaHold >= 0 ||
                b.TurnSide != 0 || !NavalBossMovementController.OnLane(v, sea))
            {
                NavalBossMovementController.ResetBroadside(b);
                return;
            }
            var f = sea.Frame(v.Position);
            var half = (_world.Naval.Routes?.Corridor ?? 20f) * 0.5f;
            // The room its own escorts' slots leave either side of the lane's line (their slots are kept beside the lane).
            var roomIn = float.PositiveInfinity;
            var roomOut = float.PositiveInfinity;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || o.Flagship != v.Id || !o.OnStation) continue;
                var gap = MathF.Abs(o.StationAt.Y) - (v.Def.Width + o.Def.Width) * 0.5f - NavalSystem.LateralMargin;
                if (o.StationAt.Y > 0f) roomOut = MathF.Min(roomOut, gap);
                else roomIn = MathF.Min(roomIn, gap);
            }
            var route = new RouteContext(sea.Out, f.Y - v.NavalGoal.Y, half, f.Y - sea.ShoreAt(f.X) - v.Def.Width * 0.5f, b.PlanningRadius, roomIn, roomOut);
            var candidate = _targets.Count == 0 ? 0f
                : NavalBossMovementController.ChooseOffset(_mounts, v.Position, b.RouteHeading, _targets, route, b.BroadsideHeld, out _, out _);
            NavalBossMovementController.UpdateBroadside(b, candidate, v.Heading);
        }

        /// <summary>A land / air boss's hull state for the debug: its route, the mission, or a granted alignment.</summary>
        private static void Land(Vehicle v, BossBrain b, double now)
        {
            b.ActualHeading = v.Heading;
            if (b.MissionLocked) b.HullReason = v.Escaping ? HullReason.Escape : HullReason.Phase;
            else if (now - b.AlignGrantedAt < 0.25) return;
            else b.HullReason = v.HasPath ? HullReason.Route : HullReason.Hold;
            b.DesiredHullHeading = v.HasPath ? SimMath.HeadingOf(v.Path[v.PathIndex] - v.Position) : v.Heading;
        }

        /// <summary>Section 96 into the decision log: the latest "why" every brain tick, a line when the hull's reason changes.</summary>
        private void Log(Vehicle v, BossBrain b, double now)
        {
            var log = _world.AiLog;
            log.Record(new Why
            {
                Layer = AiLayer.Unit,
                Team = v.Team,
                Subject = v.Id.Value,
                Time = now,
                Choice = "boss hull: " + b.HullReason,
                Score = b.ActiveDpsFraction,
                Context = b.DebugLine(),
            });
            if (b.LoggedReason == b.HullReason && b.LoggedBroadside == b.BroadsideEngaged) return;
            b.LoggedReason = b.HullReason;
            b.LoggedBroadside = b.BroadsideEngaged;
            // AI MASTER P5 Part O: the line starts with its registered code (BOSS_HULL_* / NAVAL_*).
            log.Add(new DecisionEntry(now, v.Team, AiLayer.Unit, v.Id.Value, DecisionKind.State,
                $"{ReasonCodes.HullCode(b.HullReason, b.Craft == BossCraft.Naval)} hull={b.HullReason}{(b.BroadsideEngaged ? " (broadside)" : "")}: {b.DebugLine()}"));
        }
    }

    internal sealed partial class BossSystem
    {
        private BossBrains? _brains;

        /// <summary>AI MASTER P0-C: the boss brains (spec 48).</summary>
        internal BossBrains Brains => _brains ??= new BossBrains(_world);
    }
}

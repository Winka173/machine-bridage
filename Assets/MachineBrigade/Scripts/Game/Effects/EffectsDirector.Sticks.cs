using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// The bomb-run fix, pass 3 (DECISIONS "Ném bom rải thảm"): how a stick of bombs looks (view only; the Sim already puts
    /// every bomb on its own point, one release interval after the last). The bay doors open on a bomber with hinged doors
    /// as it runs in and stay open for the stick; each bomb is drawn as its release event comes, falling with a thin trail
    /// (WeaponEffects); the blasts come down one after another along the line (each its own event), the near ones whole, the
    /// far ones of a long stick lighter (<see cref="TierFx.StickDetail"/>, inside the tiers' concurrent budget); one warning
    /// rectangle for the whole stick in place of a ring per bomb (<see cref="StickWarnings"/>), giving up its ground as the
    /// bombs land. Everything on this director's own shot clock (play-test 12).
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private readonly StickRuns _stickRuns = new();
        private StickWarnings _stickWarn;

        /// <summary>The bay doors stay open this long after a stick's last bomb (s).</summary>
        private const float BayHold = 1.2f;

        /// <summary>A bomber's doors start opening this much farther out than its run-in needs (m).</summary>
        private const float BayEarly = 6f;

        /// <summary>Tests: the sticks tracked now and the rectangles drawn.</summary>
        internal StickRuns StickTracker => _stickRuns;

        internal int StickWarningsDrawn => _stickWarn?.Drawn ?? 0;

        private void InitSticks(MaterialLibrary materials, MeshLibrary meshes)
        {
            _stickRuns.Clock = Clock;
            _stickWarn = new StickWarnings(materials, meshes, _root) { Gate = _gate, FadeIn = _catalog.Warnings.FadeIn };
        }

        /// <summary>
        /// A fired event: when its round lays a stick, its bomb goes on its run (a new run for a stick's first bomb), the bay
        /// doors are held open for the rest of the stick, and the stick's rectangle warns (an enemy's STICK_RECT stick, or a
        /// preview's own). True when the rectangle is this round's warning (no escape ring per bomb then).
        /// </summary>
        private bool StickFired(in SimEvent e, VehicleView shooter, ViewRegistry views, float now)
        {
            if (e.Kind != SimEventKind.WeaponFired || e.DefId == null || !_catalog.Weapons.TryGetValue(e.DefId, out var gun)) return false;
            var round = shooter != null && shooter.Sim != null ? FiredRound(e, shooter, gun) : gun;
            if (round.Stick is not { Laid: true } stick) return false;
            var rect = stick.Warn == StickWarn.StickRect;
            var enemy = shooter != null && shooter.Sim != null && shooter.Sim.Team != views.PlayerTeam;
            var preview = PreviewRings && shooter != null && shooter.Sim != null && shooter.Sim.Team == 0;
            var bomb = new Vector3(e.Target.X, 0f, e.Target.Y);
            var way = StickWay(e, shooter, views, stick, bomb);
            var owner = ((long)e.Entity.Value << 8) | (uint)(e.Mount & 0xff);
            var run = _stickRuns.Fired(owner, round, bomb, way, now, Mathf.Max(0.05f, e.Value), rect && (enemy || preview),
                round.Tier >= 5 || preview, out var index);
            if (shooter != null && shooter.Root != null && shooter.HasBayDoors)
            {
                if (index == 0) shooter.LastStickAt = now;
                shooter.OpenBay(Mathf.Max(0, run.Bombs - 1 - index) * stick.Interval + BayHold);
            }
            return rect;
        }

        /// <summary>
        /// The way a new stick runs, from its first bomb: a free-falling bomber's along its heading (its bombs keep its track);
        /// a boss bay's from the first bomb to its aim (the stick is laid round the aim), else away from the boss.
        /// </summary>
        private static Vector3 StickWay(in SimEvent e, VehicleView shooter, ViewRegistry views, StickDef stick, Vector3 bomb)
        {
            if (stick.Drop == StickDrop.Overfly && shooter != null && shooter.Sim != null)
            {
                var heading = SimMath.Forward(shooter.Sim.Heading);
                return new Vector3(heading.X, 0f, heading.Y);
            }
            if (e.Other.IsValid && views.TryGet(e.Other, out var aimed) && aimed != null && aimed.Sim != null)
            {
                var toAim = new Vector3(aimed.Sim.Position.X - bomb.x, 0f, aimed.Sim.Position.Y - bomb.z);
                if (toAim.sqrMagnitude > stick.Spacing * stick.Spacing * 0.25f) return toAim.normalized;
            }
            var away = new Vector3(e.Target.X - e.Position.X, 0f, e.Target.Y - e.Position.Y);
            return away.sqrMagnitude > 1e-4f ? away.normalized : Vector3.forward;
        }

        /// <summary>
        /// A bomb of a stick landed at <paramref name="impact"/>: its section of the warning goes now (the frame its blast is
        /// drawn), and the stick's bomb count for the detail of its blast (0: not a stick's bomb).
        /// </summary>
        private int StickLanded(WeaponDef round, Vector3 impact, float now)
        {
            if (round?.Stick is not { Laid: true } stick) return 0;
            var run = _stickRuns.Landed(round, impact, out var index);
            if (run == null || index < 0) return stick.Bombs;
            run.Due[index] = Mathf.Min(run.Due[index], ShotClock.Map(Clock, now));
            return run.Bombs;
        }

        /// <summary>The detail a stick's bomb at <paramref name="at"/> is drawn at (<paramref name="bombs"/> 0: not a stick's, as before).</summary>
        private TierFx.Detail StickDetailAt(Vector3 at, int bombs)
        {
            var distance = Vector3.Distance(at, _camera.Focus);
            return TierFx.StickDetail(TierFx.DetailAt(distance, _camera.Zoom), bombs, distance);
        }

        /// <summary>The frame's sticks: runs let go, the rectangles, and the bombers' doors as they run in.</summary>
        private void TickSticks(ViewRegistry views, float now)
        {
            _stickRuns.Tick(now);
            _stickWarn?.Tick(_stickRuns.Runs, ShotClock.Map(Clock, now));
            TickBayDoors(views);
        }

        /// <summary>
        /// A bomber with hinged doors running in on its target (in front of it, within its lead, half its stick and the doors'
        /// opening time at its release speed) opens its doors before the first bomb. A boss bay (it lays its stick from a
        /// stand-off, no run in) opens them with its first stick, then before each next one: its target in reach and the
        /// bay's cycle (cooldown and the stick's ripple) nearly round again since the last stick began.
        /// </summary>
        private static void TickBayDoors(ViewRegistry views)
        {
            var all = views.All;
            var now = Time.time;
            for (var i = 0; i < all.Count; i++)
            {
                var v = all[i];
                if (v == null || v.Root == null || v.Sim == null || !v.HasBayDoors || !v.Sim.IsAlive) continue;
                var stick = v.BayStick;
                var target = v.Sim.MountTarget(v.BayMount);
                if (!target.IsValid || !views.TryGet(target, out var aimed) || aimed == null || aimed.Sim == null) continue;
                if (stick.Drop != StickDrop.Overfly)
                {
                    var arm = v.Sim.Arm(v.BayMount);
                    var cycle = arm.Cooldown + Mathf.Max(0, stick.Bombs - 1) * arm.BurstInterval;
                    var near = System.Numerics.Vector2.Distance(aimed.Sim.Position, v.Sim.Position) <= arm.Range * 1.1f;
                    if (near && v.LastStickAt > -50f && now >= v.LastStickAt + cycle - stick.BayOpen - 0.3f) v.OpenBay(0.5f);
                    continue;
                }
                var to = aimed.Sim.Position - v.Sim.Position;
                var ahead = SimMath.Forward(v.Sim.Heading);
                var along = to.X * ahead.X + to.Y * ahead.Y;
                var across = Mathf.Abs(to.X * ahead.Y - to.Y * ahead.X);
                var reach = stick.Lead + stick.Length * 0.5f + stick.ReleaseSpeed * stick.BayOpen + BayEarly;
                if (along > 0f && along < reach && across < Mathf.Max(stick.Width, stick.Length * 0.5f)) v.OpenBay(0.5f);
            }
        }
    }
}

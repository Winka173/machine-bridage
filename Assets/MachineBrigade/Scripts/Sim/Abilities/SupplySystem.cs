#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Abilities
{
    /// <summary>
    /// Prompt 13 C: an aircraft's stores (bombs, missiles, rockets) on the field. They come back one
    /// round at a time wherever it is, with no trip home: at the full rate while it is out of danger
    /// and not attacking (for 3 s at least), at half that while it attacks or is inside enemy
    /// anti-aircraft or fighter reach; faster at a landing pad (twice), over its HQ (half as fast
    /// again) or, for a helicopter, beside an ammunition carrier (twice). Guns never run out.
    /// <para>
    /// With every store empty (a bomber: with less than two thirds of its bombs) an aircraft
    /// finishes what it is doing (the salvo in the air, its attack hold, the pass under way), then
    /// flies to its holding pattern: a circle just behind the nearest friendly ground unit, outside
    /// the reach of every known enemy anti-aircraft gun, missile and fighter, 2-3 s of flight from
    /// the fight and always on the map. It is recomputed as the front moves. There it circles (a
    /// helicopter hovers), guns still firing at anything in reach, until its stores are half back
    /// (a bomber's two thirds) and it has something to attack, then it goes back to its orders. A
    /// landing pad, the HQ or an ammunition carrier is chosen instead when the flight there and the
    /// rearm take less time, or when it needs mending and the time is not much longer.
    /// </para>
    /// </summary>
    /// <summary>The stores' rates, for the unit details (prompt 13 G): <see cref="SupplySystem"/> goes by them.</summary>
    public static class SupplyRules
    {
        /// <summary>The slow rate (attacking, or in danger), against the full one.</summary>
        public const float SlowShare = 0.5f;

        /// <summary>Share of its stores an aircraft goes back to fighting with; a bomber's share of its bombs.</summary>
        public const float ReturnShare = 0.5f, BomberShare = 2f / 3f;

        /// <summary>How much faster than the holding pattern a landing pad, the HQ and an ammunition carrier (helicopters) rearm.</summary>
        public const float PadRate = 2f, HqRate = 1.5f, CarrierRate = 2f;

        /// <summary>Seconds out of danger (and not attacking) before the full rate starts.</summary>
        public const float SafeSeconds = 3f;
    }

    internal sealed class SupplySystem
    {
        /// <summary>The slow rate (attacking, or in danger), against the full one.</summary>
        internal const float SlowShare = SupplyRules.SlowShare;

        /// <summary>Seconds out of danger (and not attacking) before the full rate starts.</summary>
        internal const double SafeSeconds = 3.0;

        /// <summary>Share of its stores an aircraft goes back to fighting with; a bomber's share of its bombs.</summary>
        internal const float ReturnShare = SupplyRules.ReturnShare, BomberShare = SupplyRules.BomberShare;

        /// <summary>Below this share of its stores the commander may send it to rearm early in a lull.</summary>
        internal const float LowShare = 0.2f;

        /// <summary>How much faster than the holding pattern the other sites rearm.</summary>
        internal const float PadRate = SupplyRules.PadRate, HqRate = SupplyRules.HqRate, CarrierRate = SupplyRules.CarrierRate;

        /// <summary>The HQ's basic mending for aircraft over it (a share of health a second; a landing pad's is its module's).</summary>
        internal const float HqHeal = 0.01f;

        /// <summary>How near the HQ and an ammunition carrier count as there.</summary>
        internal const float HqReach = 20f, CarrierReach = 12f;

        /// <summary>Metres kept outside an enemy anti-aircraft weapon's reach.</summary>
        internal const float Margin = 6f;

        /// <summary>The flight to the holding pattern: this many seconds at the aircraft's speed, at most (about).</summary>
        internal const float HoldFlight = 2.6f;

        private readonly SimWorld _world;

        public SupplySystem(SimWorld world) => _world = world;

        public void Step(float dt)
        {
            var now = _world.Time;
            var tick = _world.Tick;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || !v.HasStores) continue;
                // Danger a few times a second (every fifth step, spread over the aircraft).
                if (((v.Id.Value + tick) % 5) == 0)
                {
                    v.InDanger = Exposure(v.Team, v.Position, 0f, true) > 0f;
                    if (v.InDanger) v.DangerAt = now;
                }
                Decide(v, now);
                Rearm(v, dt, now);
            }
        }

        // ------------------------------------------------------------------ going and coming back

        private void Decide(Vehicle v, double now)
        {
            switch (v.Supply)
            {
                case SupplyState.Fighting:
                    if (!MustRearm(v) || !CanBreakOff(v)) return;
                    v.RearmRequested = false;
                    v.SupplyGuard = v.GuardPoint;
                    v.SupplyFrom = v.Position;
                    v.Supply = SupplyState.Leaving;
                    v.SupplySince = now;
                    ChooseSite(v);
                    return;

                case SupplyState.Leaving:
                    // The holding pattern follows the front on the way too.
                    if (v.RearmAt == RearmSite.Holding && ((v.Id.Value + _world.Tick) % 20) == 0) v.HoldPoint = HoldingPoint(v);
                    if (Vector2.Distance(v.Position, v.HoldPoint) <= Arrive(v))
                    {
                        v.Supply = SupplyState.Holding;
                        v.SupplySince = now;
                    }
                    return;

                case SupplyState.Holding:
                    if (ReadyToFight(v))
                    {
                        Return(v);
                        return;
                    }
                    if (v.RearmAt == RearmSite.Holding && ((v.Id.Value + _world.Tick) % 20) == 0) v.HoldPoint = HoldingPoint(v);
                    // A site gone (the pad destroyed, the carrier moved off): back to the holding pattern.
                    if (v.RearmAt != RearmSite.Holding && !SiteStands(v)) ChooseSite(v);
                    return;
            }
        }

        /// <summary>Its stores are spent (a bomber: its bombs under two thirds), or the commander wants it rearmed.</summary>
        internal static bool MustRearm(Vehicle v)
        {
            if (v.StoresEmpty) return true;
            if (Bomber(v) && MainShare(v) < BomberShare) return true;
            return v.RearmRequested && v.StoresShare < 1f;
        }

        /// <summary>
        /// Nothing half done: no salvo still firing, no attack hold, and an aeroplane not in the middle of
        /// its pass (it pulls through first). An aircraft never turns tail mid-attack and vanishes.
        /// </summary>
        internal bool CanBreakOff(Vehicle v)
        {
            if (v.InAttackHold) return false;
            foreach (var w in v.Weapons)
                if (w.BurstLeft > 0) return false;
            if (!v.Def.FixedWing || v.RunExtending) return true;
            if (!_world.TryGetVehicle(v.RunTarget, out var run) || !run.IsAlive) return true;
            // In its run: close to it and heading at it (the pass finishes once it pulls through).
            var to = run.Position - v.Position;
            var ahead = Vector2.Dot(SimMath.Forward(v.Heading), to);
            return !(ahead > 0f && to.Length() < v.Arms[0].Range * 1.4f);
        }

        /// <summary>Back to half its stores (a bomber two thirds of its bombs) with something to attack; or full and nothing to wait for.</summary>
        private bool ReadyToFight(Vehicle v)
        {
            var share = Bomber(v) ? MainShare(v) : v.StoresShare;
            var need = Bomber(v) ? BomberShare : ReturnShare;
            if (share < need) return false;
            if (HasWork(v)) return true;
            // Full with nothing in sight: an aircraft on guard goes back to its post; one sent at the
            // enemy waits here, ready, rather than circle the battlefield for nothing.
            return share >= 0.999f && v.Order.Kind is OrderKind.Idle or OrderKind.Move or OrderKind.Retreat;
        }

        /// <summary>A target for it: its ordered one, or a known enemy it can hit near its orders or its post.</summary>
        private bool HasWork(Vehicle v)
        {
            if (v.Order.Kind == OrderKind.Attack) return _world.TryGetTarget(v.Order.Target, out var t) && t.IsAlive;
            if (v.Order.Kind is OrderKind.Move or OrderKind.Retreat) return true;
            var around = v.Order.Kind == OrderKind.AttackMove ? v.Order.Point : v.SupplyGuard;
            var reach = MathF.Max(v.Def.VisionRange, 50f) + (v.Def.Interceptor ? v.Def.Weapon.Range * 1.4f : 20f);
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Invulnerable || e.Def.Untargetable || !e.IsVisibleTo(v.Team)) continue;
                if (!CanHit(v, e.Flying)) continue;
                if (Vector2.DistanceSquared(e.Position, around) < reach * reach || Vector2.DistanceSquared(e.Position, v.Position) < reach * reach) return true;
            }
            return false;
        }

        private static bool CanHit(Vehicle v, bool flying)
        {
            for (var i = 0; i < v.Arms.Length; i++)
                if (v.Arms[i].Damage > 0f && v.Arms[i].CanTarget(flying) && v.Weapons[i].Ammo != 0) return true;
            return false;
        }

        private void Return(Vehicle v)
        {
            v.Supply = SupplyState.Fighting;
            v.SupplySince = _world.Time;
            v.GuardPoint = v.SupplyGuard;
            v.ResumeRoute = true;
            v.RunTarget = EntityId.None;
            v.RunExtending = false;
            v.ClearPath();
        }

        /// <summary>A bomber: its main weapon drops bombs (it goes in again only with two thirds of them).</summary>
        internal static bool Bomber(Vehicle v) => v.Def.FixedWing && v.Arms[0].Projectile == ProjectileKind.Bomb && v.Weapons[0].Load > 0;

        /// <summary>The main weapon's stores left, 0 to 1.</summary>
        internal static float MainShare(Vehicle v) => v.Weapons[0].Load > 0 ? Math.Max(0, v.Weapons[0].Ammo) / (float)v.Weapons[0].Load : 1f;

        private static float Arrive(Vehicle v) => v.Def.FixedWing ? Orbit(v) + 8f : 4f;

        /// <summary>The circle an aeroplane flies round its holding pattern (as its idle circle round a post).</summary>
        internal static float Orbit(Vehicle v) => v.Def.FixedWing ? MathF.Max(14f, v.Def.Speed / v.Def.TurnRate * 1.6f) : 0f;

        // ------------------------------------------------------------------ where to rearm

        /// <summary>
        /// The holding pattern, or a landing pad, the HQ or (for a helicopter) an ammunition carrier when
        /// the flight there and the rearm are quicker, or it needs mending and they are not much slower.
        /// </summary>
        private void ChooseSite(Vehicle v)
        {
            var hold = HoldingPoint(v);
            var speed = MathF.Max(4f, v.Def.Speed);
            var missing = 1f - v.StoresShare;
            var rearm = MathF.Max(1f, v.Def.RearmTime) * missing;
            float Time(Vector2 at, float rate) => Vector2.Distance(v.Position, at) / speed + rearm / rate;
            var best = (site: RearmSite.Holding, at: hold, time: Time(hold, 1f));
            var healBest = (site: RearmSite.Holding, at: hold, time: float.MaxValue);
            void Offer(RearmSite site, Vector2 at, float rate, bool heals)
            {
                // A site under enemy anti-air rearms only at the slow rate.
                if (Exposure(v.Team, at, 0f, false) > 0f) rate = SlowShare;
                var t = Time(at, rate);
                if (t < best.time) best = (site, at, t);
                if (heals && t < healBest.time) healBest = (site, at, t);
            }
            if (Pad(v.Team, out var pad, out var padRate)) Offer(RearmSite.LandingPad, pad.Position, PadRate * padRate, true);
            if (Hq(v.Team, out var hq)) Offer(RearmSite.Headquarters, hq.Position, HqRate, true);
            if (!v.Def.FixedWing && Carrier(v, out var carrier)) Offer(RearmSite.AmmoCarrier, carrier.Position, CarrierRate, false);
            // Needing both mending and stores: a place that mends when it is not much slower.
            var hurt = v.Hp < v.MaxHp * 0.6f;
            var pick = hurt && healBest.time <= best.time * 1.5f + 5f ? healBest : best;
            v.RearmAt = pick.site;
            v.HoldPoint = pick.at;
            if (v.Supply == SupplyState.Holding && Vector2.Distance(v.Position, v.HoldPoint) > Arrive(v)) v.Supply = SupplyState.Leaving;
        }

        private bool SiteStands(Vehicle v) => v.RearmAt switch
        {
            RearmSite.LandingPad => Pad(v.Team, out _, out _),
            RearmSite.Headquarters => Hq(v.Team, out _),
            RearmSite.AmmoCarrier => Carrier(v, out var c) && Vector2.Distance(c.Position, v.HoldPoint) < CarrierReach,
            _ => true,
        };

        /// <summary>The side's landing pad (a base's airfield module), and how much faster its branch rearms.</summary>
        internal bool Pad(int team, out Vehicle pad, out float rate)
        {
            pad = null!;
            rate = 1f;
            foreach (var m in _world.VehicleList)
            {
                if (!m.IsAlive || m.Team != team || m.Def.Utility is not { AirRepair: > 0f } u) continue;
                pad = m;
                rate = MathF.Max(1f, u.AirRearm);
                return true;
            }
            return false;
        }

        /// <summary>The side's HQ (every base has one: its basic rearm point).</summary>
        internal bool Hq(int team, out Vehicle hq)
        {
            hq = null!;
            foreach (var m in _world.VehicleList)
                if (m.IsAlive && m.Team == team && m.Def.Fort is { Kind: FortKind.Hq })
                {
                    hq = m;
                    return true;
                }
            return false;
        }

        /// <summary>The nearest friendly ammunition carrier within a few seconds' flight (helicopters rearm beside it).</summary>
        internal bool Carrier(Vehicle v, out Vehicle carrier)
        {
            carrier = null!;
            var best = MathF.Max(40f, v.Def.Speed * 5f);
            foreach (var m in _world.VehicleList)
            {
                if (!m.IsAlive || m.Team != v.Team || m.Def.AirRearm == null) continue;
                var d = Vector2.Distance(m.Position, v.Position);
                if (d >= best) continue;
                best = d;
                carrier = m;
            }
            return carrier != null;
        }

        /// <summary>
        /// The holding pattern: straight back from the nearest friendly ground unit (towards home) to the
        /// first spot out of every known enemy anti-aircraft and fighter reach, turning up to 60 degrees
        /// either way if straight back is covered; at most about 2.6 s of flight from the fight, on the
        /// map with room to circle. With every spot covered, the least covered.
        /// </summary>
        internal Vector2 HoldingPoint(Vehicle v)
        {
            // Measured from where it broke off its attack (the fight), never from where it circles now:
            // a pattern worked out from its own position would run away in front of it.
            var from = v.Supply == SupplyState.Fighting ? v.Position : v.SupplyFrom;
            var anchor = from;
            var nearest = 60f;
            foreach (var o in _world.VehicleList)
            {
                if (!o.IsAlive || o.Team != v.Team || o.Flying || o.Def.Static || o.Scripted) continue;
                var d = Vector2.Distance(o.Position, from);
                if (d >= nearest) continue;
                nearest = d;
                anchor = o.Position;
            }
            var home = _world.TryGetRally(v.Team, out var rally) ? rally : anchor;
            var back = home - anchor;
            if (back.LengthSquared() < 25f)
            {
                // At home already: away from the enemy's side.
                back = _world.TryGetRally(1 - Math.Clamp(v.Team, 0, 1), out var theirs) ? home - theirs : -SimMath.Forward(v.Heading);
            }
            back = back.LengthSquared() > 0.01f ? Vector2.Normalize(back) : -SimMath.Forward(v.Heading);
            var orbit = Orbit(v);
            var far = MathF.Max(30f, v.Def.Speed * HoldFlight);
            var edge = orbit + (v.Def.FixedWing ? v.Def.Speed / v.Def.TurnRate * 1.3f + 4f : 6f);
            // At least a second and a half of flight behind a friendly line, two seconds with none (it
            // then measures from where it broke off, over the fight).
            var near = MathF.Min(far, anchor == from ? v.Def.Speed * 2f : MathF.Max(20f, v.Def.Speed * 1.2f));
            var best = ClampInside(anchor + back * near, edge);
            var bestExposure = float.MaxValue;
            for (var d = near; d <= far + 0.1f; d += 8f)
                for (var k = 0; k < 5; k++)
                {
                    // 0, +30, -30, +60, -60 degrees off straight back.
                    var turn = ((k + 1) / 2) * (k % 2 == 1 ? 1f : -1f) * (MathF.PI / 6f);
                    var p = ClampInside(anchor + SimMath.Rotate(back, turn) * d, edge);
                    var exposure = Exposure(v.Team, p, orbit, false) + (k > 0 ? 0.01f * k : 0f);
                    if (exposure < 0.1f) return p;
                    if (exposure >= bestExposure) continue;
                    bestExposure = exposure;
                    best = p;
                }
            return best;
        }

        private Vector2 ClampInside(Vector2 p, float margin)
        {
            var limit = MathF.Max(0f, _world.Map.HalfSize - margin);
            return new Vector2(Math.Clamp(p.X, -limit, limit), Math.Clamp(p.Y, -limit, limit));
        }

        /// <summary>
        /// How far into enemy anti-aircraft and fighter reach a point is (metres summed over the enemies
        /// covering it; 0: out of all of them). <paramref name="real"/>: the real danger (for the rearm
        /// rate); otherwise only what the side knows of (for choosing where to go).
        /// </summary>
        internal float Exposure(int team, Vector2 at, float extra, bool real)
        {
            var total = 0f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == team || e.Team < 0 || e.Stunned) continue;
                if (!real && !e.IsVisibleTo(team)) continue;
                var reach = AirReach(e);
                if (reach <= 0f) continue;
                var gap = Vector2.Distance(e.Position, at) - extra;
                total += MathF.Max(0f, reach + Margin - gap);
            }
            return total;
        }

        /// <summary>How far a vehicle's weapons reach aircraft (anti-aircraft guns and missiles, a fighter's), 0 for none.</summary>
        internal static float AirReach(Vehicle e)
        {
            if (e.Def.Passive) return 0f;
            // Aircraft threaten aircraft only as fighters; a helicopter's or bomber's self-defence does not make a place dangerous.
            if (e.Flying && !e.Def.Interceptor) return 0f;
            var reach = 0f;
            for (var i = 0; i < e.Arms.Length; i++)
            {
                var w = e.Arms[i];
                if (w.Damage <= 0f || !w.CanTarget(true) || e.Weapons[i].Ammo == 0) continue;
                // A machine gun is not anti-air; flak, AA missiles and a fighter's weapons are.
                if (!Combat.CombatSystem.IsAntiAir(w) && !e.Def.Interceptor) continue;
                reach = MathF.Max(reach, w.Range * (e.Def.Interceptor ? 1.2f : 1f));
            }
            return reach;
        }

        // ------------------------------------------------------------------ taking the stores on

        private void Rearm(Vehicle v, float dt, double now)
        {
            var full = true;
            foreach (var w in v.Weapons)
                if (w.Load > 0 && w.Ammo < w.Load) full = false;
            if (full)
            {
                v.RearmRate = 0f;
                return;
            }
            var safe = now - v.DangerAt >= SafeSeconds;
            var attacking = v.Supply == SupplyState.Fighting && (v.Target.IsValid || v.InAttackHold || now - v.LastFiredAt < SafeSeconds);
            var rate = safe && !attacking ? 1f : SlowShare;
            if (rate >= 1f && v.Supply == SupplyState.Holding) rate *= SiteRate(v);
            v.RearmRate = rate;
            var perSecond = rate / MathF.Max(1f, v.Def.RearmTime);
            for (var i = 0; i < v.Weapons.Length; i++)
            {
                var w = v.Weapons[i];
                if (w.Load <= 0) continue;
                if (w.Ammo >= w.Load)
                {
                    w.LoadProgress = 0f;
                    continue;
                }
                // One round at a time: every weapon fills in the same time.
                w.LoadProgress += dt * perSecond * w.Load;
                while (w.LoadProgress >= 1f && w.Ammo < w.Load)
                {
                    w.Ammo = Math.Max(0, w.Ammo) + 1;
                    w.LoadProgress -= 1f;
                }
            }
            // The HQ mends a little (a landing pad's own module mends more, see AbilitySystem.ServeAircraft).
            if (v.RearmAt == RearmSite.Headquarters && v.Supply == SupplyState.Holding && safe && v.Hp < v.MaxHp &&
                Hq(v.Team, out var hq) && Vector2.Distance(hq.Position, v.Position) <= HqReach)
                v.Hp = MathF.Min(v.MaxHp, v.Hp + v.MaxHp * HqHeal * dt);
        }

        /// <summary>The rearm site's speed-up when it is there (1 at the holding pattern).</summary>
        private float SiteRate(Vehicle v)
        {
            switch (v.RearmAt)
            {
                case RearmSite.LandingPad:
                    return Pad(v.Team, out var pad, out var branch) && Vector2.Distance(pad.Position, v.Position) <= pad.Def.Utility!.AirReach + 2f ? PadRate * branch : 1f;
                case RearmSite.Headquarters:
                    return Hq(v.Team, out var hq) && Vector2.Distance(hq.Position, v.Position) <= HqReach ? HqRate : 1f;
                case RearmSite.AmmoCarrier:
                    return Carrier(v, out var c) && Vector2.Distance(c.Position, v.Position) <= CarrierReach ? CarrierRate : 1f;
                default:
                    return 1f;
            }
        }
    }
}

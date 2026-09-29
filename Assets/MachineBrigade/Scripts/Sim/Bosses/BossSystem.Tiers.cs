#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Prompt 19 (DECISIONS 18A): bosses on altitude tiers, drop pods and the crash, all from data any boss can opt into
    /// (balance.json "tiers" and "pods"; prompt 20 reuses them for Daedalus, Icarus Mk.0 and Typhon).
    /// <list type="bullet">
    /// <item>The opening in orbit (untouchable, guns held, its big attack and first pods still come), the way down (a
    /// satellite stays up), then each phase's fixed cycle of high and low steps, never back to orbit. A change takes
    /// its "shift" (longer with manoeuvring thrusters broken) and counts as the lower tier meanwhile. The main engine
    /// broken, it keeps to the low tier.</item>
    /// <item>Drop pods at the tiers the data names: low-tier targets that land their 1-2 vehicles after a warned fall,
    /// or lose them if shot down; at most so many of their vehicles alive, apart from the escort cap.</item>
    /// <item>The last phase with a crash: it falls to a set point, lands as a ground fortress (a ground target for
    /// every weapon, its wrecked model, its sleeping guns awake, cover round it, its ground closed to routes), and at the
    /// hardest difficulties seizes the other side's drones now and then (jammer cover protects them).</item>
    /// </list>
    /// The Sandbox calls (prompt 21) are plain methods: <see cref="ForceTier"/>, <see cref="JumpPhase"/>,
    /// <see cref="TriggerBig"/>, <see cref="SetBigOff"/> (and <see cref="Break"/> for a part). Deterministic: vehicle-list
    /// order, the world's clock and random stream.
    /// </summary>
    internal sealed partial class BossSystem
    {
        private sealed class PodFlight
        {
            public Vehicle Pod = null!;
            public Vehicle Boss = null!;
            public string[] Units = Array.Empty<string>();
        }

        private readonly List<PodFlight> _podFlights = new();
        private readonly List<(Vehicle boss, Vehicle unit)> _podLanded = new();
        private readonly List<(Vehicle boss, Vector2 at, string[] units, float height, PodDef def)> _podOrders = new();
        private readonly List<Vehicle> _hijacked = new();

        /// <summary>Its pods' vehicles alive and still on the way (the cap).</summary>
        public int PodLoad(Vehicle boss)
        {
            var n = 0;
            foreach (var (b, u) in _podLanded)
                if (b == boss && u.IsAlive) n++;
            foreach (var f in _podFlights)
                if (f.Boss == boss && f.Pod.IsAlive) n += f.Units.Length;
            return n;
        }

        /// <summary>Drop pods of this boss in the air now.</summary>
        public int PodsFalling(Vehicle boss)
        {
            var n = 0;
            foreach (var f in _podFlights)
                if (f.Boss == boss && f.Pod.IsAlive) n++;
            return n;
        }

        // ================================================================== joining

        private void JoinTiers(Vehicle v)
        {
            if (v.Def.Tiers is not { } t) return;
            var now = _world.Time;
            if (t.Opening > 0f)
            {
                v.Tier = v.TierFrom = v.TierTo = AltitudeTier.Orbit;
                v.TierNext = now + t.Opening;
                v.Invulnerable = true;
            }
            else
            {
                var first = t.CycleOf(0)[0];
                v.LeftOrbit = true;
                v.Tier = v.TierFrom = v.TierTo = first.Tier;
                v.TierStep = 0;
                v.TierNext = now + first.Seconds;
            }
            v.AltitudeNow = t.HeightOf(v.TierFrom);
            if (v.Def.Pods is { } pods) v.PodNext = now + pods.First;
            v.HijackNext = double.PositiveInfinity;
            Radio(v, t, "appear");
        }

        /// <summary>A tiered boss that opens in orbit gets its escorts as it comes down, not while it is out of reach.</summary>
        private static bool EscortsLater(Vehicle v) => v.Def.Tiers is { Opening: > 0f, EscortsOnDescend: true };

        private void Radio(Vehicle v, TierDef t, string moment)
        {
            if (t.RadioFor(moment) is { } key) _world.Emit(SimEvent.RadioMessage(key, v.Team));
        }

        // ================================================================== the step

        private void StepTiers(double now)
        {
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Def.Tiers is not { } t) continue;
                if (v.Crashed)
                {
                    StepHijack(v, t, now);
                    continue;
                }
                if (v.Crashing)
                {
                    StepCrash(v, t, now);
                    continue;
                }
                if (!v.LeftOrbit)
                {
                    if (now >= v.TierNext) Descend(v, t, now);
                }
                else
                {
                    var phase = PhaseOf(v, t);
                    if (phase > v.TierPhase)
                    {
                        EnterPhase(v, t, phase, now);
                        if (v.Crashing) continue;
                    }
                    if (v.Shifting)
                    {
                        if (now >= v.ShiftEnds) Settle(v);
                    }
                    // Its main engine broken while high: it comes down and stays low.
                    else if (v.ThrustOff && v.TierFrom == AltitudeTier.High) Change(v, t, AltitudeTier.Low, now, Math.Max(0.0, v.TierNext - now));
                    else if (now >= v.TierNext) NextStep(v, t, now);
                }
                Height(v, t, now);
                PodsDue(v, now);
            }
            foreach (var (boss, at, units, height, def) in _podOrders) LaunchPod(boss, at, units, height, def, now);
            _podOrders.Clear();
            StepPods(now);
            Release(now);
        }

        /// <summary>The phase its health puts it in: how many of its marks it has passed.</summary>
        private static int PhaseOf(Vehicle v, TierDef t)
        {
            var share = v.Hp / MathF.Max(1f, v.MaxHp);
            var n = 0;
            foreach (var m in t.Marks)
                if (share <= m) n++;
            return n;
        }

        private void EnterPhase(Vehicle v, TierDef t, int phase, double now)
        {
            v.TierPhase = phase;
            Radio(v, t, "phase" + (phase + 1));
            // Prompt 20 H.2: it stops where it is (the next drop comes at once).
            if (t.HaltPhase >= 0 && phase >= t.HaltPhase)
            {
                v.PhaseSpeed = 0f;
                v.ClearPath();
                v.PodNext = Math.Min(v.PodNext, now);
            }
            if (phase == t.CrashPhase)
            {
                BeginCrash(v, t, now);
                return;
            }
            // The new phase's cycle from its first step (after a change under way settles).
            v.TierStep = -1;
            v.TierNext = now;
        }

        /// <summary>The opening is over: down from orbit to its first step, a satellite left up there; never back.</summary>
        private void Descend(Vehicle v, TierDef t, double now)
        {
            var first = t.CycleOf(0)[0];
            v.LeftOrbit = true;
            v.Invulnerable = false;
            v.HasSatellite = true;
            v.SatelliteAt = v.Position;
            v.TierStep = 0;
            Change(v, t, first.Tier, now, first.Seconds, t.Descend);
            Radio(v, t, "descend");
            _world.Emit(SimEvent.Tiered(v, "descend", (int)first.Tier, t.Descend));
            if (EscortsLater(v)) JoinEscorts(v);
            // A mark passed while out of reach (the Sandbox's jump) counts from here.
            var phase = PhaseOf(v, t);
            if (phase > v.TierPhase) EnterPhase(v, t, phase, now);
        }

        private void NextStep(Vehicle v, TierDef t, double now)
        {
            var cycle = t.CycleOf(v.TierPhase);
            v.TierStep = (v.TierStep + 1) % cycle.Count;
            var step = cycle[v.TierStep];
            var want = v.ThrustOff && step.Tier == AltitudeTier.High ? AltitudeTier.Low : step.Tier;
            if (want == v.TierFrom)
            {
                v.TierNext = now + step.Seconds;
                return;
            }
            Change(v, t, want, now, step.Seconds);
        }

        /// <summary>A change of tier begins: <paramref name="hold"/> s at the new one once there; the lower of the two counts meanwhile.</summary>
        private void Change(Vehicle v, TierDef t, AltitudeTier to, double now, double hold, float seconds = -1f)
        {
            // Each manoeuvring thruster broken makes the change longer (the speed it lost).
            if (seconds < 0f) seconds = t.Shift / MathF.Max(0.4f, v.PartSpeed);
            v.Shifting = true;
            v.TierTo = to;
            v.ShiftStart = now;
            v.ShiftEnds = now + seconds;
            v.Tier = Vehicle.Lower(v.TierFrom, to);
            v.TierNext = v.ShiftEnds + hold;
            if (v.TierFrom != AltitudeTier.Orbit) _world.Emit(SimEvent.Tiered(v, "shift", (int)to, seconds));
        }

        private static void Settle(Vehicle v)
        {
            v.Shifting = false;
            v.TierFrom = v.TierTo;
            v.Tier = v.TierTo;
        }

        /// <summary>The height it is drawn at: its tier's, eased through a change.</summary>
        private static void Height(Vehicle v, TierDef t, double now)
        {
            if (!v.Shifting)
            {
                v.AltitudeNow = t.HeightOf(v.TierFrom);
                return;
            }
            var u = (float)Math.Clamp((now - v.ShiftStart) / Math.Max(0.1, v.ShiftEnds - v.ShiftStart), 0.0, 1.0);
            u = u * u * (3f - 2f * u);
            v.AltitudeNow = t.HeightOf(v.TierFrom) + (t.HeightOf(v.TierTo) - t.HeightOf(v.TierFrom)) * u;
        }

        // ================================================================== drop pods

        private void PodsDue(Vehicle v, double now)
        {
            if (v.Def.Pods is not { } p || v.PodsOff || v.Stunned || now < v.PodNext) return;
            var tier = v.Def.Tiers == null ? AltitudeTier.None : v.Shifting ? AltitudeTier.None : v.TierFrom;
            if (v.Def.Tiers != null && !p.DropsAt(tier)) return;
            v.PodNext = now + p.EveryIn(v.TierPhase) * (v.PodShare < 1f ? 1f / MathF.Max(0.34f, v.PodShare) : 1f);
            var room = p.Max - PodLoad(v);
            if (room <= 0) return;
            // Short of the other side's biggest group, towards the boss (never on top of it); else under the boss.
            var centre = v.Position;
            if (BiggestGroup(v, out var group) > 0)
            {
                var back = v.Position - group;
                var distance = back.Length();
                centre = distance > 0.5f ? group + back / distance * MathF.Min(p.Offset, distance) : group;
            }
            var sent = 0;
            for (var k = 0; k < p.Count && room > 0; k++)
            {
                var seats = Math.Min(room, p.Min + (p.PerPod > p.Min ? _world.Random.Next(p.PerPod - p.Min + 1) : 0));
                var units = new string[seats];
                for (var j = 0; j < seats; j++) units[j] = _world.Economy.ForWave(v.Team, p.Units[(v.PodsSent * 2 + j) % p.Units.Count]);
                v.PodsSent++;
                var at = _world.ClampToMap(centre + RandomIn(_world.Random, p.Spread));
                if (_world.Grid.TryNearestWalkable(at, 8, out var open)) at = open;
                _podOrders.Add((v, at, units, MathF.Max(8f, v.Height), p));
                room -= seats;
                sent++;
            }
            if (sent > 0) _world.Emit(SimEvent.Tiered(v, "pods", (int)v.Tier, sent));
        }

        private void LaunchPod(Vehicle boss, Vector2 at, string[] units, float height, PodDef p, double now)
        {
            var pod = _world.SpawnVehicle(p.Unit, boss.Team, at, boss.Heading);
            pod.IsPod = true;
            pod.Scripted = true;
            pod.Tier = pod.TierFrom = pod.TierTo = AltitudeTier.Low;
            pod.PodLaunched = now;
            pod.PodLands = now + p.Fall;
            pod.PodFrom = height;
            pod.AltitudeNow = height;
            _podFlights.Add(new PodFlight { Pod = pod, Boss = boss, Units = units });
            if (p.Warning != null && _world.Catalog.TryGetSupport(p.Warning, out var warning))
                _world.Emit(SimEvent.StrikeWarning(boss.Team, warning, at, at, p.Fall));
        }

        /// <summary>Pods fall; one that reaches the ground lands its vehicles and is gone (a shot-down one took them with it).</summary>
        private void StepPods(double now)
        {
            for (var i = 0; i < _podFlights.Count; i++)
            {
                var f = _podFlights[i];
                var pod = f.Pod;
                if (!pod.IsAlive)
                {
                    _podFlights.RemoveAt(i--);
                    continue;
                }
                var u = (float)Math.Clamp((now - pod.PodLaunched) / Math.Max(0.1, pod.PodLands - pod.PodLaunched), 0.0, 1.0);
                pod.AltitudeNow = pod.PodFrom + (PodGround - pod.PodFrom) * u;
                if (now < pod.PodLands) continue;
                _podFlights.RemoveAt(i--);
                var forward = SimMath.Forward(pod.Heading);
                var right = new Vector2(forward.Y, -forward.X);
                for (var k = 0; k < f.Units.Length; k++)
                {
                    var spot = pod.Position + right * ((k - (f.Units.Length - 1) * 0.5f) * 5f) + forward * 3f;
                    var unit = _world.SpawnVehicle(f.Units[k], f.Boss.Team, _world.ClampToMap(spot), pod.Heading);
                    _podLanded.Add((f.Boss, unit));
                }
                pod.Hp = 0f;
                _world.Emit(SimEvent.Retired(pod));
                _world.Emit(SimEvent.Exploded(pod.Position, new ExplosionDef(0f, 5f, 0f, ExplosionTier.Large), pod.Id));
                _world.Emit(SimEvent.Landed(f.Boss, pod.Position, f.Units.Length));
            }
            for (var i = _podLanded.Count - 1; i >= 0; i--)
                if (!_podLanded[i].unit.IsAlive) _podLanded.RemoveAt(i);
        }

        /// <summary>A pod's drawn height as it touches down (its model's centre).</summary>
        private const float PodGround = 3f;

        // ================================================================== the crash

        private void BeginCrash(Vehicle v, TierDef t, double now)
        {
            var crash = t.Crash!;
            v.Crashing = true;
            v.Shifting = false;
            v.Tier = v.TierFrom = v.TierTo = AltitudeTier.Low;
            v.CrashStart = now;
            v.CrashAt = now + crash.Fall;
            v.CrashFrom = v.Position;
            v.CrashSpot = CrashSite(crash);
            v.PodFrom = MathF.Max(t.LowHeight, v.AltitudeNow);
            v.ClearPath();
            v.Speed = 0f;
            Radio(v, t, "crash");
            _world.Emit(SimEvent.BossPhase(v, t.Marks.Count + 1, true, "toast.tier.crash"));
            _world.Emit(SimEvent.Tiered(v, "crash", (int)AltitudeTier.None, crash.Fall, v.CrashSpot));
            if (crash.Warning != null && _world.Catalog.TryGetSupport(crash.Warning, out var warning))
                _world.Emit(SimEvent.StrikeWarning(v.Team, warning, v.CrashSpot, v.CrashSpot, crash.Fall));
        }

        /// <summary>Where it comes down: its set point on the map, on the nearest open ground.</summary>
        private Vector2 CrashSite(CrashDef crash)
        {
            var at = _world.ClampToMap(crash.At);
            return _world.Grid.TryNearestWalkable(at, 12, out var open) ? open : at;
        }

        private void StepCrash(Vehicle v, TierDef t, double now)
        {
            var u = (float)Math.Clamp((now - v.CrashStart) / Math.Max(0.1, v.CrashAt - v.CrashStart), 0.0, 1.0);
            var to = v.CrashSpot - v.CrashFrom;
            v.Position = _world.ClampToMap(v.CrashFrom + to * u);
            if (to.LengthSquared() > 1f) v.Heading = SimMath.HeadingOf(to);
            // It falls ever faster, on a long smoking slope.
            v.AltitudeNow = v.PodFrom * (1f - u * u);
            if (now >= v.CrashAt) Land(v, t, now);
        }

        /// <summary>Down: a ground fortress where it fell (its wreck, its guns awake, cover round it, its ground closed to routes).</summary>
        private void Land(Vehicle v, TierDef t, double now)
        {
            var crash = t.Crash!;
            v.Crashing = false;
            v.Crashed = true;
            v.Tier = v.TierFrom = v.TierTo = AltitudeTier.None;
            v.AltitudeNow = 0f;
            v.Position = v.CrashSpot;
            v.Speed = 0f;
            v.ClearPath();
            foreach (var m in crash.Guns)
                if (m < v.MountDormant.Length) v.MountDormant[m] = false;
            if (crash.Form != null) v.Form = crash.Form;
            _world.Emit(SimEvent.BossPhase(v, t.Marks.Count + 1, false, null));
            _world.Emit(SimEvent.Tiered(v, "landed", (int)AltitudeTier.None, 0f, v.Position));
            if (crash.Damage > 0f)
                _world.Damage.Queue(v.Position, new ExplosionDef(crash.Damage, crash.Radius, 0f, ExplosionTier.Ultimate), 0f, v.Team, v, HitKind.Strike, v.Id);
            _world.AnchorCrash(v);
            var forward = SimMath.Forward(v.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            foreach (var d in crash.DebrisAt) _world.AddCover(crash.Debris, _world.ClampToMap(v.Position + right * d.X + forward * d.Y));
            if (t.Hijack != null) v.HijackNext = now + t.Hijack.First;
        }

        // ================================================================== seizing drones (the hardest difficulties)

        private void StepHijack(Vehicle v, TierDef t, double now)
        {
            if (t.Hijack is not { } h || !h.On(_world.BigAttackSettings?.Difficulty)) return;
            if (!v.HijackWarned && now >= v.HijackNext)
            {
                v.HijackWarned = true;
                v.HijackAt = now + h.Warn;
                Radio(v, t, "hijackWarn");
                Radio(v, t, "hijack");
                _world.Emit(SimEvent.Tiered(v, "hijack", 0, h.Warn));
                return;
            }
            if (!v.HijackWarned || now < v.HijackAt) return;
            v.HijackWarned = false;
            v.HijackNext = now + h.Every;
            Seize(v, h, now);
        }

        /// <summary>The other side's drones not under its own jammer cover fight for the boss for a few seconds.</summary>
        private void Seize(Vehicle v, HijackDef h, double now)
        {
            var taken = 0;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || e.Def.Boss || e.IsPod || e.HijackedFrom >= 0 || !IsDrone(e.Def)) continue;
                // A jammer vehicle or EW tower of its own side in reach keeps it.
                if (_world.Abilities.Jammed(e.Position, v.Team)) continue;
                e.HijackedFrom = e.Team;
                e.HijackEnds = now + h.Seconds;
                _world.Defect(e, v.Team);
                _hijacked.Add(e);
                taken++;
            }
            _world.Emit(SimEvent.Tiered(v, "hijack", 1, taken));
        }

        /// <summary>A drone for the seizure: a drone aircraft, or a vehicle that fires drones (FPV and Lancet launchers, a swarm carrier).</summary>
        internal static bool IsDrone(VehicleDef def)
        {
            if (def.Drone) return true;
            foreach (var m in def.Mounts)
                if (m.Weapon.Projectile == ProjectileKind.Drone) return true;
            return false;
        }

        /// <summary>Seized drones go back to their side when the time is up (or the boss is gone).</summary>
        private void Release(double now)
        {
            for (var i = _hijacked.Count - 1; i >= 0; i--)
            {
                var e = _hijacked[i];
                if (!e.IsAlive)
                {
                    _hijacked.RemoveAt(i);
                    continue;
                }
                if (now < e.HijackEnds) continue;
                _world.Defect(e, e.HijackedFrom);
                e.HijackedFrom = -1;
                _hijacked.RemoveAt(i);
            }
        }

        /// <summary>Drones seized now (tests, the HUD).</summary>
        public int Hijacked => _hijacked.Count;

        // ================================================================== the Sandbox's calls (prompt 21) and tests

        /// <summary>A change to <paramref name="tier"/> (low or high) now, the schedule going on from there; false when it cannot (no tiers, in orbit, down).</summary>
        public bool ForceTier(Vehicle v, AltitudeTier tier)
        {
            if (v.Def.Tiers is not { } t || !v.LeftOrbit || v.Crashing || v.Crashed || tier is not (AltitudeTier.Low or AltitudeTier.High)) return false;
            if (v.Shifting) Settle(v);
            if (v.TierFrom == tier) return true;
            var cycle = t.CycleOf(v.TierPhase);
            Change(v, t, tier, _world.Time, cycle[Math.Max(0, v.TierStep) % cycle.Count].Seconds);
            return true;
        }

        /// <summary>
        /// Straight to phase <paramref name="phase"/> (0 first): out of its opening in orbit on the next step, and its
        /// health just under that phase's mark (the phase begins on the next step too).
        /// </summary>
        public void JumpPhase(Vehicle v, int phase)
        {
            if (v.Def.Tiers is not { } t)
            {
                JumpPhaseP20(v, phase);
                return;
            }
            if (!v.LeftOrbit) v.TierNext = _world.Time;
            if (phase <= v.TierPhase || t.Marks.Count == 0) return;
            var mark = t.Marks[Math.Clamp(phase, 1, t.Marks.Count) - 1];
            v.Hp = MathF.Min(v.Hp, mark * v.MaxHp - 1f);
        }

        /// <summary>Its big attack now (it waits a moment if it is busy); switches it on again if it was off.</summary>
        public void TriggerBig(Vehicle v)
        {
            if (v.BigAttack is not { } s) return;
            s.Off = false;
            if (s.Stage == BigStage.Ready) s.Next = _world.Time;
        }

        /// <summary>Its big attack switched off (it waits) or on again.</summary>
        public void SetBigOff(Vehicle v, bool off)
        {
            if (v.BigAttack is { } s) s.Off = off;
        }

        /// <summary>Tiers, pods and seized drones into the battle's fingerprint.</summary>
        private void MixTiers(Action<long> mix)
        {
            foreach (var v in _world.VehicleList)
                if (v.Def.Tiers != null) mix((long)v.Tier * 100_000 + v.TierPhase * 10_000 + (v.Crashed ? 5000 : v.Crashing ? 3000 : 0) + (long)Math.Round(v.TierNext * 10.0) % 1000);
            mix(_podFlights.Count * 64 + _podLanded.Count * 8 + _hijacked.Count);
        }
    }
}

#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Sandbox
{
    /// <summary>
    /// One hit a vehicle took (prompt 21 E.2, F.4): when, who hit whom, what got through of which damage type, the
    /// face struck and the round's penetration multiplier on it (✓ ~ ✕ by <see cref="Matchup.Verdict(float)"/>).
    /// </summary>
    public readonly struct HitReport
    {
        public HitReport(long tick, int attacker, int attackerTeam, int victim, int victimTeam, float dealt, DamageType type, ArmorFace face, float pen,
            Vector2 at, bool victimAlive)
        {
            Tick = tick;
            Attacker = attacker;
            AttackerTeam = attackerTeam;
            Victim = victim;
            VictimTeam = victimTeam;
            Dealt = dealt;
            Type = type;
            Face = face;
            Pen = pen;
            At = at;
            VictimAlive = victimAlive;
        }

        public long Tick { get; }

        /// <summary>The attacker's entity id (0: none, a strike or a burn with no vehicle behind it).</summary>
        public int Attacker { get; }

        public int AttackerTeam { get; }
        public int Victim { get; }
        public int VictimTeam { get; }
        public float Dealt { get; }
        public DamageType Type { get; }
        public ArmorFace Face { get; }
        public float Pen { get; }
        public Vector2 At { get; }
        public bool VictimAlive { get; }

        public MatchVerdict Verdict => Matchup.Verdict(Pen);

        /// <summary>The round got through (fully or partly); ✕ is a bounce.</summary>
        public bool Pierced => Verdict != MatchVerdict.None;
    }

    /// <summary>One unit's numbers in a Sandbox battle (prompt 21 F.4).</summary>
    public sealed class SandboxUnitStats
    {
        public int Id;
        public string Def = "";
        public int Team;

        /// <summary>Damage dealt and taken, by damage type (indexed by <see cref="DamageType"/>).</summary>
        public readonly float[] Dealt = new float[DamageTypes], Taken = new float[DamageTypes];

        public int Pierced, Bounced, PiercedTaken, BouncedTaken, Kills;

        /// <summary>Seconds from its first hit on a target to that target's end, summed over its kills.</summary>
        public double KillSeconds;

        public double Born, Died = -1;

        public float DealtTotal => Sum(Dealt);
        public float TakenTotal => Sum(Taken);

        /// <summary>Mean seconds to bring down what it killed (-1: nothing).</summary>
        public double TimeToKill => Kills > 0 ? KillSeconds / Kills : -1;

        public double Lifetime(double now) => (Died >= 0 ? Died : now) - Born;

        internal static int DamageTypes => Enum.GetValues(typeof(DamageType)).Length;

        private static float Sum(float[] a)
        {
            var s = 0f;
            foreach (var v in a) s += v;
            return s;
        }
    }

    /// <summary>
    /// The Sandbox's measurements (prompt 21 E.2-E.3, F.4): every hit from <see cref="SimWorld.HitLog"/>, each unit's
    /// damage dealt and taken by type, rounds through and bounced, kills and the time to make them, how long it lived,
    /// and a live damage-per-second over the last few seconds (the real DPS of the combat-value measure, prompt 13).
    /// It only listens; the battle runs the same with or without it.
    /// </summary>
    public sealed class SandboxStats
    {
        /// <summary>The live DPS window, seconds.</summary>
        public const double DpsWindow = 5.0;

        /// <summary>Recent hits kept for the floating numbers.</summary>
        public const int RecentHits = 64;

        private readonly Dictionary<int, SandboxUnitStats> _units = new();
        private readonly List<SandboxUnitStats> _order = new();
        private readonly Dictionary<(int attacker, int victim), double> _firstHit = new();
        private readonly Dictionary<int, Queue<(double time, float dealt)>> _window = new();
        private readonly Queue<HitReport> _recent = new();
        private SimWorld? _world;

        public IReadOnlyList<SandboxUnitStats> Units => _order;

        /// <summary>The last <see cref="RecentHits"/> hits, oldest first.</summary>
        public IEnumerable<HitReport> Recent => _recent;

        /// <summary>Every hit so far (a test's view of the overlay's numbers).</summary>
        public int Hits { get; private set; }

        /// <summary>Set once the battle ended: the numbers stop there.</summary>
        public bool Frozen { get; set; }

        public void Attach(SimWorld world)
        {
            _world = world;
            world.HitLog = Record;
            foreach (var v in world.Vehicles) Of(v.Id.Value, v.Def.Id, v.Team, world.Time);
        }

        public SandboxUnitStats? Get(int id) => _units.TryGetValue(id, out var s) ? s : null;

        private SandboxUnitStats Of(int id, string def, int team, double now)
        {
            if (_units.TryGetValue(id, out var s)) return s;
            s = new SandboxUnitStats { Id = id, Def = def, Team = team, Born = now };
            _units[id] = s;
            _order.Add(s);
            return s;
        }

        /// <summary>New arrivals (bought, escorts, a swapped boss) and the ones that went down.</summary>
        public void Step(SimWorld world)
        {
            if (Frozen) return;
            foreach (var v in world.Vehicles) Of(v.Id.Value, v.Def.Id, v.Team, world.Time);
            // Gone without a hit to say so (sent home, sunk, crashed): marked when it is no longer on the field.
            foreach (var s in _order)
                if (s.Died < 0 && (!world.TryGetVehicle(new Core.EntityId(s.Id), out var v) || !v.IsAlive)) s.Died = world.Time;
        }

        private void Record(HitReport hit)
        {
            if (Frozen || _world == null) return;
            Hits++;
            var now = _world.Time;
            _recent.Enqueue(hit);
            while (_recent.Count > RecentHits) _recent.Dequeue();
            var t = (int)hit.Type;
            var victimDef = _world.TryGetVehicle(new Core.EntityId(hit.Victim), out var victim) ? victim.Def.Id : "";
            var target = Of(hit.Victim, victimDef, hit.VictimTeam, now);
            target.Taken[t] += hit.Dealt;
            if (hit.Pierced) target.PiercedTaken++;
            else target.BouncedTaken++;
            if (!hit.VictimAlive && target.Died < 0) target.Died = now;
            if (hit.Attacker <= 0) return;
            var attackerDef = _world.TryGetVehicle(new Core.EntityId(hit.Attacker), out var attacker) ? attacker.Def.Id : "";
            var by = Of(hit.Attacker, attackerDef, hit.AttackerTeam, now);
            by.Dealt[t] += hit.Dealt;
            if (hit.Pierced) by.Pierced++;
            else by.Bounced++;
            var key = (hit.Attacker, hit.Victim);
            if (!_firstHit.ContainsKey(key)) _firstHit[key] = now;
            if (!hit.VictimAlive)
            {
                by.Kills++;
                by.KillSeconds += now - _firstHit[key];
            }
            if (!_window.TryGetValue(hit.Attacker, out var q)) _window[hit.Attacker] = q = new Queue<(double, float)>();
            q.Enqueue((now, hit.Dealt));
        }

        /// <summary>A unit's damage a second over the last <see cref="DpsWindow"/> seconds (the overlay's DPS meter).</summary>
        public float Dps(int id)
        {
            if (_world == null || !_window.TryGetValue(id, out var q)) return 0f;
            var now = _world.Time;
            while (q.Count > 0 && q.Peek().time < now - DpsWindow) q.Dequeue();
            var sum = 0f;
            foreach (var (_, dealt) in q) sum += dealt;
            return (float)(sum / Math.Min(DpsWindow, Math.Max(1.0, now)));
        }

        /// <summary>A side's damage dealt and units lost.</summary>
        public (float dealt, int lost) Side(int team)
        {
            var (dealt, lost) = (0f, 0);
            foreach (var s in _order)
            {
                if (s.Team != team) continue;
                dealt += s.DealtTotal;
                if (s.Died >= 0) lost++;
            }
            return (dealt, lost);
        }
    }
}

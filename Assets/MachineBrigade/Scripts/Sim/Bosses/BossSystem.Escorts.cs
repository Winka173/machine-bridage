#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Escorts for every boss (prompt 16 F), from each boss's table in balance.json "escorts":
    /// <list type="bullet">
    /// <item>A wave comes in with the boss, and another at each phase change (its own phase marks, else
    /// the table's; the Earth Worm's each time it breaks out). Beside it, air-dropped round it after a
    /// warning, in from the map edge behind it, or set down at an offset.</item>
    /// <item>At most <see cref="EscortSettings.Cap"/> alive at once (the mode's, by difficulty; fewer in
    /// Boss Rush, where only part of each wave's guards come, as elites). The helpers of a wave come
    /// first: every wave brings at least one unit that helps the boss.</item>
    /// <item>Guards fight whatever attacks the boss, never past the leash; helpers keep station behind it
    /// (away from the enemy): an engineer mends it, a jammer scrambles guided weapons, anti-air covers it,
    /// a spotter marks targets (the boss's side hits them harder, its guns more tightly).</item>
    /// <item>Destroying one pays its killer's side CP. When the boss falls they fight on under the
    /// commander.</item>
    /// </list>
    /// Only when the world has <see cref="SimWorld.EscortSettings"/> (the modes set them): bare test
    /// battles have none.
    /// </summary>
    internal sealed partial class BossSystem
    {
        /// <summary>Escort orders and helper effects are worked out this often (ticks).</summary>
        private const int EscortTicks = 10;

        private const float EscortSeconds = EscortTicks * 0.05f;

        /// <summary>A boss's escorts and how many of its waves have come.</summary>
        private sealed class EscortGroup
        {
            public EscortGroup(Vehicle boss, EscortDef def)
            {
                Boss = boss;
                Def = def;
            }

            public readonly Vehicle Boss;
            public readonly EscortDef Def;
            public bool Arrived;
            public int Waves;
            public int Surfaced;
            public bool WasUnder;
            public int Slots;
            public readonly List<Escort> Members = new();
        }

        private sealed class Escort
        {
            public Vehicle Unit = null!;
            public EscortRole Role;
            public EscortSlot Slot;
            public int Index;
            public Vector2 Ordered;
            public bool HasOrder;
            public string Base = "";
        }

        private readonly List<EscortGroup> _groups = new();
        private readonly List<(double at, EscortGroup group, EscortUnitDef unit, int index, Vector2 spot)> _drops = new();
        private readonly EntityId[] _one = new EntityId[1];

        /// <summary>A boss joined: it gets its escort group (its first wave comes in on the next step).</summary>
        private void JoinEscorts(Vehicle v)
        {
            if (!v.Def.Boss || !_world.Catalog.Escorts.TryGetValue(v.Def.Id, out var def)) return;
            _groups.Add(new EscortGroup(v, def) { WasUnder = v.Burrowed });
        }

        /// <summary>How many escorts of this boss are alive (the boss bar's count).</summary>
        public int EscortsAlive(EntityId boss)
        {
            foreach (var g in _groups)
                if (g.Boss.Id == boss) return Alive(g);
            return 0;
        }

        private static int Alive(EscortGroup g)
        {
            var n = 0;
            foreach (var m in g.Members)
                if (m.Unit.IsAlive) n++;
            return n;
        }

        private int Pending(EscortGroup g)
        {
            var n = 0;
            foreach (var d in _drops)
                if (d.group == g) n++;
            return n;
        }

        private void StepEscorts(double now)
        {
            if (_groups.Count == 0 && _drops.Count == 0) return;
            var settings = _world.EscortSettings;
            if (settings == null) return;
            // Air drops land.
            for (var i = 0; i < _drops.Count; i++)
            {
                var d = _drops[i];
                if (now < d.at) continue;
                _drops.RemoveAt(i--);
                if (d.group.Boss.IsAlive) Spawn(d.group, d.unit, d.index, d.spot, settings);
            }
            if (_world.Tick % EscortTicks != 0) return;
            for (var i = 0; i < _groups.Count; i++)
            {
                var g = _groups[i];
                if (!g.Boss.IsAlive)
                {
                    // The boss is down: its escorts fight on under the commander.
                    foreach (var m in g.Members)
                    {
                        Paid(g, m);
                        m.Unit.EscortOf = EntityId.None;
                    }
                    _groups.RemoveAt(i--);
                    continue;
                }
                if (!g.Arrived)
                {
                    g.Arrived = true;
                    if (g.Def.Arrive != null) Send(g, g.Def.Arrive, settings, now);
                }
                var changes = PhaseChanges(g);
                while (g.Waves < changes)
                {
                    var wave = g.Def.PhaseWave(g.Waves);
                    g.Waves++;
                    if (wave != null) Send(g, wave, settings, now);
                }
                for (var k = g.Members.Count - 1; k >= 0; k--)
                {
                    var m = g.Members[k];
                    if (m.Unit.IsAlive) continue;
                    Paid(g, m);
                    g.Members.RemoveAt(k);
                }
                Guide(g, now);
            }
        }

        /// <summary>How many phase changes the boss has been through: its own phases (a change counts as it begins), the table's marks, or its breaking out of the ground.</summary>
        private int PhaseChanges(EscortGroup g)
        {
            var boss = g.Boss;
            if (g.Def.On == EscortTrigger.Surface)
            {
                var under = boss.Burrowed || boss.Burrow == Vehicle.BurrowState.Diving;
                if (g.WasUnder && !under) g.Surfaced++;
                g.WasUnder = under;
                return g.Surfaced;
            }
            if (g.Def.Marks.Count == 0 && boss.Def.Phases.Count > 0) return boss.Phase + (boss.Transforming ? 1 : 0);
            var marks = g.Def.Marks.Count > 0 ? g.Def.Marks : _world.Catalog.EscortRules.Marks;
            var share = boss.Hp / MathF.Max(1f, boss.MaxHp);
            var n = 0;
            foreach (var m in marks)
                if (share <= m) n++;
            return n;
        }

        /// <summary>Sends a wave: the helpers first, then the guards (Boss Rush: a share of them), as far as the cap allows.</summary>
        private void Send(EscortGroup g, EscortWaveDef wave, EscortSettings settings, double now)
        {
            var cap = g.Def.Cap > 0 ? Math.Min(g.Def.Cap, settings.Cap) : settings.Cap;
            var room = cap - Alive(g) - Pending(g);
            var guards = 0;
            foreach (var u in wave.Units)
                if (!u.Helper) guards++;
            var guardsSent = (int)MathF.Ceiling(guards * Math.Clamp(settings.Guards, 0f, 1f));
            var sent = 0;
            for (var pass = 0; pass < 2 && room > 0; pass++)
                foreach (var u in wave.Units)
                {
                    if (room <= 0) break;
                    if (u.Helper != (pass == 0)) continue;
                    if (!u.Helper && guardsSent-- <= 0) continue;
                    if (wave.Refill && !Lost(g, wave, u)) continue;
                    Dispatch(g, wave, u, settings, now);
                    room--;
                    sent++;
                }
            if (sent == 0) return;
            if (wave.Halt > 0f) _world.Status.Slow(g.Boss, 0.95f, wave.Halt);
            if (wave.Radio != null) _world.Emit(SimEvent.RadioMessage(wave.Radio, g.Boss.Team));
        }

        /// <summary>A refill wave's unit is sent only if the boss has fewer of it alive than the wave brings.</summary>
        private static bool Lost(EscortGroup g, EscortWaveDef wave, EscortUnitDef unit)
        {
            var wanted = 0;
            foreach (var u in wave.Units)
                if (u.Unit == unit.Unit) wanted++;
            var have = 0;
            foreach (var m in g.Members)
                if (m.Unit.IsAlive && m.Base == unit.Unit) have++;
            return have < wanted;
        }

        private void Dispatch(EscortGroup g, EscortWaveDef wave, EscortUnitDef u, EscortSettings settings, double now)
        {
            var boss = g.Boss;
            var index = g.Slots++;
            var slot = SlotOf(u.Slot, u.Role);
            var spot = u.At is { } at ? Offset(boss, at) : SlotPoint(g, boss, slot, index);
            switch (wave.Drop)
            {
                case EscortDrop.Para:
                {
                    // Its warning ring, the transport and the parachute: the wave's drop support, else the
                    // unit's own ("escort_drop.<unit>", one parachute per vehicle where it lands).
                    var warn = _world.Catalog.EscortRules.DropWarn;
                    spot = _world.ClampToMap(spot);
                    if (_world.Catalog.TryGetSupport(wave.Support ?? "escort_drop." + u.Unit, out var support))
                        _world.Emit(SimEvent.StrikeWarning(boss.Team, support, spot, spot, warn));
                    _drops.Add((now + warn, g, u, index, spot));
                    return;
                }
                case EscortDrop.Edge:
                {
                    // From the map edge behind the boss (away from the enemy): they drive or fly in.
                    var away = -ThreatDirection(boss);
                    spot = EdgePoint(boss.Position, away);
                    break;
                }
            }
            Spawn(g, u, index, spot, settings);
        }

        private void Spawn(EscortGroup g, EscortUnitDef u, int index, Vector2 spot, EscortSettings settings)
        {
            var boss = g.Boss;
            var id = u.Unit;
            // A signature elite always; Boss Rush's guards as elites; otherwise the side's elite budget decides (prompt 8 H).
            if (u.Elite || (settings.EliteGuards && !u.Helper)) id = _world.Catalog.EliteVariant(u.Unit) ?? u.Unit;
            else id = _world.Economy.ForWave(boss.Team, u.Unit);
            var v = _world.SpawnVehicle(id, boss.Team, _world.ClampToMap(spot), boss.Heading);
            v.EscortOf = boss.Id;
            v.EscortRole = u.Role;
            g.Members.Add(new Escort { Unit = v, Role = u.Role, Slot = SlotOf(u.Slot, u.Role), Index = index, Base = u.Unit });
        }

        private static EscortSlot SlotOf(EscortSlot slot, EscortRole role) =>
            slot != EscortSlot.Auto ? slot : role is EscortRole.Guard or EscortRole.Raid ? EscortSlot.Flank : EscortSlot.Rear;

        /// <summary>A point in the boss's frame (X right, Y forward).</summary>
        private static Vector2 Offset(Vehicle boss, Vector2 at)
        {
            var forward = SimMath.Forward(boss.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            return boss.Position + right * at.X + forward * at.Y;
        }

        /// <summary>Where the enemy is from the boss: the nearest enemy it can see within 80 m, else the enemy's rally, else ahead.</summary>
        private Vector2 ThreatDirection(Vehicle boss)
        {
            Vehicle? nearest = null;
            var best = 80f * 80f;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == boss.Team || e.Team < 0 || !e.IsVisibleTo(boss.Team)) continue;
                var d = Vector2.DistanceSquared(e.Position, boss.Position);
                if (d >= best) continue;
                best = d;
                nearest = e;
            }
            var to = nearest != null ? nearest.Position - boss.Position
                : _world.TryGetRally(boss.Team == 0 ? 1 : 0, out var rally) ? rally - boss.Position : SimMath.Forward(boss.Heading);
            return to.LengthSquared() > 0.01f ? Vector2.Normalize(to) : SimMath.Forward(boss.Heading);
        }

        /// <summary>The point where a ray from <paramref name="from"/> along <paramref name="dir"/> meets the map's edge (a little inside).</summary>
        private Vector2 EdgePoint(Vector2 from, Vector2 dir)
        {
            var limit = _world.Map.HalfSize - 4f;
            var t = float.MaxValue;
            if (MathF.Abs(dir.X) > 1e-4f) t = MathF.Min(t, ((dir.X > 0 ? limit : -limit) - from.X) / dir.X);
            if (MathF.Abs(dir.Y) > 1e-4f) t = MathF.Min(t, ((dir.Y > 0 ? limit : -limit) - from.Y) / dir.Y);
            return _world.ClampToMap(from + dir * MathF.Max(0f, t));
        }

        /// <summary>
        /// Its station round the boss: flank guards beside it along its heading (a train's run parallel to
        /// its rails), helpers behind it away from the enemy, a screen between it and the enemy.
        /// </summary>
        private Vector2 SlotPoint(EscortGroup g, Vehicle boss, EscortSlot slot, int index)
        {
            var hull = boss.Def.HullBound;
            var forward = SimMath.Forward(boss.Heading);
            var right = new Vector2(forward.Y, -forward.X);
            var side = index % 2 == 0 ? 1f : -1f;
            var rank = index / 2 % 3;
            switch (slot)
            {
                case EscortSlot.Front:
                    return boss.Position + forward * (hull + 8f + rank * 6f) + right * side * 4f;
                case EscortSlot.Rear:
                case EscortSlot.Screen:
                {
                    var threat = ThreatDirection(boss);
                    var across = new Vector2(threat.Y, -threat.X);
                    var toward = slot == EscortSlot.Screen ? 1f : -1f;
                    return boss.Position + threat * toward * (hull + 8f + rank * 5f) + across * side * (3f + rank * 3f);
                }
                default:
                    return boss.Position + right * side * (hull + 6f + rank * 5f) + forward * (3f - rank * 5f);
            }
        }

        /// <summary>Guards take on what attacks the boss inside the leash and come back past it; helpers keep station and help.</summary>
        private void Guide(EscortGroup g, double now)
        {
            var boss = g.Boss;
            var rules = _world.Catalog.EscortRules;
            var leash = g.Def.Leash > 0f ? g.Def.Leash : rules.Leash;
            foreach (var m in g.Members)
            {
                var v = m.Unit;
                if (!v.IsAlive || v.Def.Static || v.Stunned) continue;
                var home = SlotPoint(g, boss, m.Slot, m.Index);
                var reach = m.Role == EscortRole.Raid ? leash * 1.6f : leash;
                var out_ = Vector2.Distance(v.Position, boss.Position);
                if (m.Role is EscortRole.Guard or EscortRole.Raid)
                {
                    var threat = out_ <= reach ? Threat(boss, v, reach) : null;
                    if (threat != null)
                    {
                        if (v.Order.Kind != OrderKind.Attack || v.Order.Target != threat.Id) Steer(v, CommandType.Attack, threat.Position, threat.Id);
                        m.HasOrder = false;
                        continue;
                    }
                }
                else Help(g, m, now, rules);
                // Back to its station (past the leash it drops what it was chasing).
                var far = Vector2.Distance(v.Position, home) > 6f;
                var moved = !m.HasOrder || Vector2.Distance(m.Ordered, home) > 4f;
                if (out_ > reach || (far && (moved || v.Order.Kind != OrderKind.Move)))
                {
                    Steer(v, CommandType.Move, home, EntityId.None);
                    m.Ordered = home;
                    m.HasOrder = true;
                }
            }
        }

        /// <summary>The enemy a guard should take on: within the leash round the boss (plus its reach), those attacking the boss first.</summary>
        private Vehicle? Threat(Vehicle boss, Vehicle guard, float leash)
        {
            var weapon = guard.Def.Weapon;
            var reach = leash + weapon.Range;
            Vehicle? best = null;
            var bestScore = float.MaxValue;
            foreach (var e in _world.VehicleList)
            {
                if (!e.IsAlive || e.Team == boss.Team || e.Team < 0 || e.Invulnerable || !e.IsVisibleTo(guard.Team) || !weapon.CanTarget(e.Flying)) continue;
                var d = Vector2.Distance(e.Position, boss.Position);
                if (d > reach) continue;
                var attacking = e.Target == boss.Id || e.Order.Target == boss.Id || boss.LastAttacker == e.Id;
                var score = d + Vector2.Distance(e.Position, guard.Position) * 0.5f - (attacking ? 30f : 0f);
                if (score >= bestScore) continue;
                bestScore = score;
                best = e;
            }
            return best;
        }

        /// <summary>A helper's effect: a repairer mends the boss, a spotter marks the enemies it sees near it.</summary>
        private void Help(EscortGroup g, Escort m, double now, EscortRules rules)
        {
            var boss = g.Boss;
            var v = m.Unit;
            switch (m.Role)
            {
                case EscortRole.Repair:
                    if (boss.Transforming || boss.Hp >= boss.MaxHp || boss.Burrowed) return;
                    if (Vector2.Distance(v.Position, boss.Position) > boss.Def.HullBound + rules.RepairReach) return;
                    var amount = MathF.Min(boss.MaxHp - boss.Hp, boss.MaxHp * rules.Repair * EscortSeconds);
                    boss.Hp += amount;
                    _world.Emit(SimEvent.RepairedBy(boss, amount));
                    return;
                case EscortRole.Spot:
                {
                    var marked = 0;
                    var sight = v.Def.Vision;
                    foreach (var e in _world.VehicleList)
                    {
                        if (!e.IsAlive || e.Team == v.Team || e.Team < 0 || !e.IsVisibleTo(v.Team)) continue;
                        if (Vector2.DistanceSquared(e.Position, v.Position) > sight * sight) continue;
                        _world.Status.Mark(e, rules.SpotBonus, EscortSeconds * 2.5f, v.Team, 0f);
                        if (++marked >= 6) break;
                    }
                    return;
                }
            }
        }

        private void Steer(Vehicle v, CommandType type, Vector2 point, EntityId target)
        {
            _one[0] = v.Id;
            _world.Submit(new Command(type, v.Team, _one, _world.ClampToMap(point), target));
        }

        /// <summary>An escort destroyed by the other side pays its killer's side (once).</summary>
        private void Paid(EscortGroup g, Escort m)
        {
            var v = m.Unit;
            if (v.IsAlive || m.Index < 0) return;
            var team = v.LastAttackerTeam;
            m.Index = -1;
            if (team < 0 || team == v.Team || _world.Time - v.LastHitTime > 10.0 || !_world.TryGetEconomy(team, out var economy)) return;
            var rules = _world.Catalog.EscortRules;
            var cp = m.Role is EscortRole.Guard or EscortRole.Raid ? rules.Bounty : rules.HelperBounty;
            if (cp <= 0f) return;
            economy.Cp = MathF.Min(economy.Bank, economy.Cp + cp);
            _world.Emit(SimEvent.BountyPaid(team, "escort", v.Position, cp));
        }

        /// <summary>The escorts into the battle's fingerprint.</summary>
        private void MixEscorts(Action<long> mix)
        {
            foreach (var g in _groups)
            {
                mix(g.Boss.Id.Value * 16 + g.Waves);
                foreach (var m in g.Members)
                    if (m.Unit.IsAlive) mix(m.Unit.Id.Value);
            }
            mix(_drops.Count);
        }
    }
}

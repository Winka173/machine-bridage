#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>What a mission's events ask of the mission (or operation) they run in.</summary>
    public interface IMissionEventHost
    {
        MissionDef Def { get; }

        /// <summary>When the mission began (the events' clock counts from here).</summary>
        double StartedAt { get; }

        float Progress(SimWorld world);

        /// <summary>The mission's boss on the field (invalid when none).</summary>
        EntityId Boss { get; }

        Vector2? PlayerGoal(SimWorld world);
        Vector2? EnemyGoal(SimWorld world);

        /// <summary>D.8: a new plan (a stage to move on to, or a new goal); true when the mission took it.</summary>
        bool ChangePlan(SimWorld world, MissionEventDef e);
    }

    /// <summary>Where an event is.</summary>
    public enum EventPhase
    {
        /// <summary>Its trigger has not held yet.</summary>
        Waiting,

        /// <summary>Announced; it happens at <see cref="EventState.StartAt"/>.</summary>
        Warned,

        /// <summary>Under way (a side objective's clock, a general on the field, the blackout, the weather turning).</summary>
        Running,

        Done,
        Failed,
    }

    /// <summary>
    /// One event of a mission as the battle plays it: its phase, when it was warned and starts, where it comes from (the
    /// minimap's arrows, F.2), a side objective's clock and count (F.3). Read-only for the Game layer.
    /// </summary>
    public sealed class EventState
    {
        internal EventState(MissionEventDef def, int index)
        {
            Def = def;
            Index = index;
        }

        public MissionEventDef Def { get; }
        internal int Index { get; }
        public EventPhase Phase { get; internal set; }

        /// <summary>Times it has started (a repeating event's count).</summary>
        public int Fired { get; internal set; }

        public double WarnedAt { get; internal set; } = -1;
        public double StartAt { get; internal set; } = -1;

        /// <summary>When it first happened (another event's "after" counts from here; -1 before).</summary>
        public double HappenedAt { get; internal set; } = -1;

        /// <summary>A running event's end (a side objective's deadline, the blackout's end; -1: none).</summary>
        public double EndsAt { get; internal set; } = -1;

        /// <summary>Where it comes in or lands (the first group's point for a wave).</summary>
        public Vector2 Where { get; internal set; }

        /// <summary>F.2: each direction it comes from: the spawn point and the way in (enemy waves, the general, a raid).</summary>
        public List<(Vector2 at, Vector2 inward, SpawnBearing bearing)> Arrows { get; } = new();

        /// <summary>Prompt 31 L3: places it marks on the minimap while it is warned and running (a gate, a storm's half, pods' landings).</summary>
        public List<(Vector2 at, float radius)> Marks { get; } = new();

        /// <summary>F.3: a side objective's count: done out of needed.</summary>
        public int Count { get; internal set; }

        public int Needed { get; internal set; }

        /// <summary>The combat value of what it brought (C.3's measure).</summary>
        public float Strength { get; internal set; }

        /// <summary>The vehicles it brought in.</summary>
        internal readonly List<EntityId> Units = new();

        /// <summary>A second group (the besiegers of a rescue, a general's escorts).</summary>
        internal readonly List<EntityId> Others = new();

        internal double ReadyAt = -1;
        internal double NextTry;
        internal int Tries;
        internal string? Variant;
        internal object? Plan;

        /// <summary>Seconds left on its clock (a side objective, the blackout), or -1.</summary>
        public float SecondsLeft(double now) => EndsAt < 0 ? -1f : (float)Math.Max(0.0, EndsAt - now);
    }

    /// <summary>
    /// Prompt 23 A-D: a mission's events. Each waits for its trigger (A.1: a time, the mission's progress, the boss's health,
    /// the vehicles on the field, another event), is announced ahead when it matters (A.4: a notice with its direction, a
    /// line, lead by the C.3 table), then plays: reinforcements from several directions (C), fire support, a general on the
    /// field, side objectives, the economy, logistics, intelligence, a mini boss, a new plan, the weather turning (D).
    /// Deterministic from the battle's seed; <see cref="Log"/> and <see cref="Mix"/> put every event in the battle's
    /// fingerprint, so a checkpoint's replay (the journal of commands on the same seed) brings them back as they were.
    /// </summary>
    public sealed partial class MissionEventSystem
    {
        private readonly IMissionEventHost _host;
        private readonly List<EventState> _states = new();
        private readonly Random _random;
        private readonly List<(long tick, string instance, string moment)> _log = new();
        private readonly List<(string kind, int amount, string? id)> _earned = new();
        private readonly double _origin;
        private bool _joined;

        public MissionEventSystem(SimWorld world, IMissionEventHost host, IReadOnlyList<MissionEventDef> events, EventLevel level)
        {
            _host = host;
            Level = level;
            Rules = host.Def.EventRules;
            _origin = host.StartedAt;
            _random = new Random(unchecked(world.Seed * 7349 + Stable(host.Def.Id) + events.Count * 31));
            for (var i = 0; i < events.Count; i++) _states.Add(new EventState(events[i], i));
            world.EventSystems.Add(this);
            // C.2: the side falling behind gets the mission's allied wave instead of prompt 13's free drop (never both).
            foreach (var e in events)
                if (e.Kind == MissionEventKind.AllyWave)
                {
                    world.Economy.UnderdogStandIn = team => team == MissionMode.PlayerTeam && CallAllies(world);
                    break;
                }
        }

        public EventLevel Level { get; }
        public EventRules Rules { get; }
        public EventDifficulty Difficulty => Rules.Of(Level);
        public IReadOnlyList<EventState> States => _states;

        /// <summary>A.3: every moment of every event (warned, started, done, failed, retreated, over), with its step.</summary>
        public IReadOnlyList<(long tick, string instance, string moment)> Log => _log;

        /// <summary>What the events paid that the battle does not hold (coins, blueprints, intel files), for the result screen.</summary>
        public IReadOnlyList<(string kind, int amount, string? id)> Earned => _earned;

        /// <summary>The battlefield's spawn points (worked out on the first step).</summary>
        public SpawnPoints? Spawns { get; private set; }

        /// <summary>Allied waves sent so far (Very Hard: one a mission).</summary>
        public int AllyWaves { get; private set; }

        private double Now(SimWorld world) => world.Time - _origin;

        public void Tick(SimWorld world, float dt)
        {
            if (world.IsOver) return;
            Spawns ??= SpawnPoints.Build(world, MissionMode.PlayerTeam, MissionMode.EnemyTeam);
            StepDrops(world);
            StepStrikes(world);
            StepRods(world);
            foreach (var s in _states)
            {
                switch (s.Phase)
                {
                    case EventPhase.Waiting:
                        if (!Due(world, s)) break;
                        Begin(world, s);
                        break;
                    case EventPhase.Warned:
                        if (world.Time >= s.StartAt && world.Time >= s.NextTry) Start(world, s);
                        break;
                    case EventPhase.Running:
                        Update(world, s, dt);
                        break;
                    case EventPhase.Done:
                    case EventPhase.Failed:
                        Rearm(world, s);
                        break;
                }
            }
        }

        /// <summary>Whether the trigger holds (every condition it gives), its delay counted from the first step it did.</summary>
        private bool Due(SimWorld world, EventState s)
        {
            if (s.ReadyAt >= 0) return world.Time >= s.ReadyAt;
            var t = s.Def.Trigger;
            if (t.At is { } at && Now(world) < at) return false;
            if (t.Progress is { } p && _host.Progress(world) < p) return false;
            if (t.BossHealth is { } bh && (!world.TryGetVehicle(_host.Boss, out var boss) || !boss.IsAlive || boss.Hp > boss.MaxHp * bh)) return false;
            if (t.EnemyBelow is { } eb && Field(world, MissionMode.EnemyTeam) >= eb) return false;
            if (t.EnemyAbove is { } ea && Field(world, MissionMode.EnemyTeam) <= ea) return false;
            if (t.PlayerBelow is { } pb && Field(world, MissionMode.PlayerTeam) >= pb) return false;
            if (t.PlayerAbove is { } pa && Field(world, MissionMode.PlayerTeam) <= pa) return false;
            if (t.After != null && Find(t.After) is not { HappenedAt: >= 0 }) return false;
            if (t.Outnumbered is { } ratio && Army(world, MissionMode.EnemyTeam) < ratio * MathF.Max(1f, Army(world, MissionMode.PlayerTeam))) return false;
            if (t.Spotted && !Spotted(world)) return false;
            if (t.PropDown != null && !PropDown(world, s)) return false;
            s.ReadyAt = world.Time + t.Delay;
            return world.Time >= s.ReadyAt;
        }

        /// <summary>A repeating event comes again <see cref="EventTrigger.Every"/> after it last started.</summary>
        private static void Rearm(SimWorld world, EventState s)
        {
            var t = s.Def.Trigger;
            if (t.Every <= 0.0 || s.Fired >= t.Times || s.StartAt < 0) return;
            s.Phase = EventPhase.Waiting;
            s.ReadyAt = s.StartAt + t.Every;
        }

        /// <summary>Its trigger held: the event is set up (directions, targets) and warned, or starts now.</summary>
        private void Begin(SimWorld world, EventState s)
        {
            s.Arrows.Clear();
            s.Marks.Clear();
            if (!Prepare(world, s))
            {
                // Nothing to do on this battlefield (no general, no point, no target): it passes.
                s.Phase = EventPhase.Done;
                s.Fired = s.Def.Trigger.Times;
                Record(world, s, "skipped");
                return;
            }
            var lead = Lead(s);
            s.WarnedAt = world.Time;
            s.StartAt = world.Time + lead;
            s.NextTry = s.StartAt;
            s.Tries = 0;
            if (lead > 0.01f)
            {
                s.Phase = EventPhase.Warned;
                Notice(world, s, "warn", lead);
                Line(world, s, "warn");
                Record(world, s, "warn");
                return;
            }
            Start(world, s);
        }

        /// <summary>A.4: seconds of warning: the event's own, else the C.3 table's for a big event, none for a small one.</summary>
        private float Lead(EventState s)
        {
            var table = Difficulty.Warning;
            // Prompt 31 L3: the events that change the battlefield warn 8-12 s ahead at every difficulty.
            if (ChangesGround(s.Def.Kind)) return Math.Clamp(s.Def.Lead ?? table, 8f, 12f);
            if (s.Def.Lead is { } own) return MathF.Max(0f, own);
            return s.Def.Kind switch
            {
                MissionEventKind.EnemyWave or MissionEventKind.GeneralField or MissionEventKind.MiniBoss or MissionEventKind.SupplyRaid
                    or MissionEventKind.Barrage or MissionEventKind.Blackout or MissionEventKind.WeatherShift or MissionEventKind.OrbitalStrike => table,
                MissionEventKind.AirRaid => MathF.Min(table, 6f),
                _ => 0f,
            };
        }

        private void Start(SimWorld world, EventState s)
        {
            var result = Happen(world, s);
            if (result == Outcome.Retry)
            {
                // B.3: every point in its direction has the player's units on it: it waits a little (at most 15 s).
                s.NextTry = world.Time + 3.0;
                s.Tries++;
                if (s.Phase == EventPhase.Waiting) s.Phase = EventPhase.Warned;
                return;
            }
            s.Fired++;
            if (s.HappenedAt < 0) s.HappenedAt = world.Time;
            s.StartAt = world.Time;
            Record(world, s, "start");
            if (result == Outcome.Running)
            {
                s.Phase = EventPhase.Running;
                return;
            }
            s.Phase = EventPhase.Done;
        }

        private enum Outcome
        {
            Done,
            Running,
            Retry,
        }

        private EventState? Find(string instance)
        {
            foreach (var s in _states)
                if (s.Def.Instance == instance) return s;
            return null;
        }

        private void Finish(SimWorld world, EventState s, bool done, string? moment = null)
        {
            s.Phase = done ? EventPhase.Done : EventPhase.Failed;
            moment ??= done ? "done" : "fail";
            Record(world, s, moment);
            if (done && s.Def.Reward is { } reward) Pay(world, s, reward);
        }

        private void Pay(SimWorld world, EventState s, EventReward r)
        {
            if (r.Cp > 0 && world.TryGetEconomy(MissionMode.PlayerTeam, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + r.Cp);
            if (r.Repair > 0f)
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Team == MissionMode.PlayerTeam && !v.Def.Boss && Vector2.Distance(v.Position, s.Where) < 30f)
                    {
                        var amount = world.Gear.Heal(v, v.MaxHp * r.Repair);
                        if (amount > 0f) world.Emit(SimEvent.RepairedBy(v, amount));
                    }
            if (r.Coins > 0) _earned.Add(("coins", r.Coins, s.Def.Instance));
            if (r.Prints > 0) _earned.Add(("prints", r.Prints, s.Def.Instance));
            if (r.Intel != null) _earned.Add(("intel", 1, r.Intel));
        }

        private void Record(SimWorld world, EventState s, string moment) => _log.Add((world.Tick, s.Def.Instance, moment));

        // ------------------------------------------------------------------ notices and lines

        /// <summary>The notice's text key for a moment: the event's own, else "event.&lt;kind&gt;[.&lt;variant&gt;].&lt;moment&gt;".</summary>
        public static string NoticeKey(MissionEventDef e, string moment, string? variant = null) =>
            e.Notices.TryGetValue(moment, out var own) ? own : $"event.{e.KindKey}{(variant != null ? "." + variant : "")}.{moment}";

        /// <summary>A line's key: the event's own, else "radio.&lt;speaker&gt;.ev.&lt;kind&gt;[.&lt;variant&gt;].&lt;moment&gt;".</summary>
        public static string LineKey(MissionEventDef e, string moment, string speaker, string? variant = null) =>
            e.Lines.TryGetValue(moment, out var own) ? own : $"radio.{speaker}.ev.{e.KindKey}{(variant != null ? "." + variant : "")}.{moment}";

        /// <summary>The moments a kind shows a notice at (the text table has a key for each; the checks read them).</summary>
        public static string[] NoticeMoments(MissionEventKind kind) => kind switch
        {
            MissionEventKind.EnemyWave or MissionEventKind.Barrage or MissionEventKind.AirRaid or MissionEventKind.CounterBattery
                or MissionEventKind.MiniBoss or MissionEventKind.WeatherShift or MissionEventKind.OrbitalStrike => new[] { "warn" },
            MissionEventKind.GeneralField => new[] { "warn", "start", "retreat", "done" },
            MissionEventKind.Ceasefire => new[] { "start", "end", "broken", "betrayed" },
            MissionEventKind.SideObjective or MissionEventKind.LootDrop => new[] { "start", "done", "fail" },
            MissionEventKind.SupplyRaid => new[] { "warn", "done", "fail" },
            MissionEventKind.Blackout => new[] { "warn", "start", "end" },
            MissionEventKind.GroundChange or MissionEventKind.OrbitalPods or MissionEventKind.IceCrack => new[] { "warn", "start" },
            MissionEventKind.SandstormTurn or MissionEventKind.CityBlackout => new[] { "warn", "end" },
            MissionEventKind.BetrayalWarning => new[] { "warn" },
            _ => new[] { "start" },
        };

        /// <summary>The moments a kind says a line at (when its speaker has one: a mini boss's start only with a general).</summary>
        public static string[] LineMoments(MissionEventKind kind) => kind switch
        {
            MissionEventKind.EnemyWave or MissionEventKind.Barrage or MissionEventKind.AirRaid or MissionEventKind.CounterBattery
                or MissionEventKind.SupplyRaid or MissionEventKind.WeatherShift or MissionEventKind.OrbitalStrike => new[] { "warn" },
            MissionEventKind.GeneralField => new[] { "warn", "start", "retreat" },
            MissionEventKind.Ceasefire => new[] { "start", "end", "broken", "betrayed" },
            MissionEventKind.MiniBoss => new[] { "warn", "start" },
            MissionEventKind.SideObjective => new[] { "start", "done", "fail" },
            MissionEventKind.Blackout => new[] { "warn", "end" },
            MissionEventKind.GroundChange or MissionEventKind.SandstormTurn or MissionEventKind.CityBlackout or MissionEventKind.BetrayalWarning
                or MissionEventKind.OrbitalPods or MissionEventKind.IceCrack => new[] { "warn" },
            MissionEventKind.LootDrop => Array.Empty<string>(),
            _ => new[] { "start" },
        };

        /// <summary>The moments a kind speaks at (warn, start, done, fail, retreat, end) and who speaks each by default.</summary>
        public static string? DefaultSpeaker(MissionEventDef e, string moment, string? general)
        {
            if (e.Speaker != null) return e.Speaker;
            switch (e.Kind)
            {
                case MissionEventKind.EnemyWave or MissionEventKind.Barrage or MissionEventKind.AirRaid or MissionEventKind.CounterBattery
                    or MissionEventKind.SupplyRaid or MissionEventKind.WeatherShift or MissionEventKind.OrbitalStrike:
                    return moment == "warn" ? "linh" : null;
                case MissionEventKind.Ceasefire:
                    // Kade calls it and answers a broken word; the general keeps it or answers ours being broken.
                    return moment is "start" or "betrayed" ? "khai" : moment is "end" or "broken" ? general : null;
                case MissionEventKind.Blackout:
                    return moment is "warn" or "end" ? "linh" : null;
                case MissionEventKind.GroundChange or MissionEventKind.SandstormTurn or MissionEventKind.CityBlackout or MissionEventKind.BetrayalWarning
                    or MissionEventKind.OrbitalPods or MissionEventKind.IceCrack:
                    return moment == "warn" ? "linh" : null;
                case MissionEventKind.GeneralField:
                    return moment == "warn" ? "linh" : moment is "start" or "retreat" ? general : null;
                case MissionEventKind.MiniBoss:
                    return moment == "warn" ? "linh" : moment == "start" ? general : null;
                case MissionEventKind.AllyAirStrike:
                    return moment == "start" ? "dieuhau" : null;
                case MissionEventKind.IntelReveal or MissionEventKind.NeutralConvoy:
                    return moment == "start" ? "linh" : null;
                case MissionEventKind.AllyWave or MissionEventKind.AllyArtillery or MissionEventKind.PlanChange or MissionEventKind.SupplyDrop:
                    return moment == "start" ? "khai" : null;
                case MissionEventKind.SideObjective:
                    return moment is "start" or "done" or "fail" ? "khai" : null;
                default:
                    return null;
            }
        }

        /// <summary>
        /// F.1: the event's notice for the top-edge queue: its text key, where, the direction it comes from, the seconds to it
        /// (or of it), its priority and kind (the icon), whether it is bad news.
        /// </summary>
        private void Notice(SimWorld world, EventState s, string moment, float seconds, EntityId entity = default)
        {
            var e = s.Def;
            var bad = (Bad(e.Kind) && moment is not ("done" or "end" or "retreat")) || (e.Kind == MissionEventKind.Ceasefire && moment is "broken" or "betrayed");
            var priority = e.Priority ?? (moment == "warn" ? LinePriority.Warning : LinePriority.Event);
            Vector2 dir = default;
            var bearing = -1;
            if (s.Arrows.Count > 0)
            {
                dir = -s.Arrows[0].inward;
                bearing = (int)s.Arrows[0].bearing;
            }
            world.Emit(SimEvent.EventNotice(NoticeKey(e, moment, s.Variant), e.Kind, s.Where, dir, bearing, seconds, priority, bad ? 1 : 0, entity));
        }

        private void Line(SimWorld world, EventState s, string moment, EntityId speaker = default)
        {
            // Prompt 23 E: the event's own general (a general the mission is not tied to: Brandt in chapter 1, Thorne turning in
            // chapter 7, Orlov at Skygate) speaks for the enemy as the mission's does.
            var general = GeneralOf(s.Def);
            var who = DefaultSpeaker(s.Def, moment, general);
            if (who == null) return;
            var priority = s.Def.Priority ?? (moment == "warn" ? LinePriority.Warning : LinePriority.Event);
            var team = who == general || who == General ? MissionMode.EnemyTeam : MissionMode.PlayerTeam;
            world.Emit(SimEvent.RadioMessage(LineKey(s.Def, moment, who, s.Variant), team, priority, speaker));
        }

        private static bool Bad(MissionEventKind kind) => kind is MissionEventKind.EnemyWave or MissionEventKind.Barrage or MissionEventKind.AirRaid
            or MissionEventKind.CounterBattery or MissionEventKind.GeneralField or MissionEventKind.SupplyRaid or MissionEventKind.Blackout
            or MissionEventKind.MiniBoss or MissionEventKind.OrbitalStrike or MissionEventKind.GroundChange or MissionEventKind.SandstormTurn
            or MissionEventKind.CityBlackout or MissionEventKind.BetrayalWarning or MissionEventKind.OrbitalPods or MissionEventKind.IceCrack;

        /// <summary>Prompt 31 L3: the kinds that change the battlefield (8-12 s of warning, a mark on the minimap).</summary>
        public static bool ChangesGround(MissionEventKind kind) => kind is MissionEventKind.GroundChange or MissionEventKind.SandstormTurn
            or MissionEventKind.CityBlackout or MissionEventKind.BetrayalWarning or MissionEventKind.OrbitalPods or MissionEventKind.IceCrack;

        // ------------------------------------------------------------------ the battlefield

        /// <summary>The mission's general (its id), or null.</summary>
        private string? General => _host.Def.General;

        /// <summary>The general an event is about: its own ("general" in its params), else the mission's.</summary>
        private string? GeneralOf(MissionEventDef e) => e.Word("general") ?? General;

        private static int Field(SimWorld world, int team)
        {
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Def.Boss && !v.Scripted) n++;
            return n;
        }

        /// <summary>A side's army by C.3's measure (every vehicle's combat value, its allies' too).</summary>
        private static float Army(SimWorld world, int team)
        {
            var total = 0f;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == team && !v.Def.Static && !v.Scripted) total += Strength(v.Def);
            return total;
        }

        /// <summary>
        /// C.3: a vehicle's strength: its price (an elite's dearer one) times prompt 13's measured combat value per CP. A wave's is
        /// the sum over its vehicles.
        /// </summary>
        public static float Strength(VehicleDef def) => MathF.Max(1f, def.ArmyCost > 0 ? def.ArmyCost : def.CpCost) * MathF.Max(0.1f, def.CombatValue);

        public static float Strength(Catalog catalog, IEnumerable<string> units)
        {
            var total = 0f;
            foreach (var id in units)
                if (catalog.Vehicles.TryGetValue(id, out var def)) total += Strength(def);
            return total;
        }

        /// <summary>The middle of a side's biggest group on the ground (vehicles within 14 m of one another), or null.</summary>
        internal static Vector2? Group(SimWorld world, int team, bool visibleTo = false, int watcher = -1)
        {
            Vector2? best = null;
            var most = 0;
            foreach (var a in world.VehicleList)
            {
                if (!a.IsAlive || a.Team != team || a.Flying || a.Def.Static || a.Scripted) continue;
                if (visibleTo && watcher >= 0 && a.IsVisibleTo(watcher)) continue;
                var n = 0;
                var sum = Vector2.Zero;
                foreach (var b in world.VehicleList)
                    if (b.IsAlive && b.Team == team && !b.Flying && !b.Def.Static && Vector2.DistanceSquared(a.Position, b.Position) < 14f * 14f)
                    {
                        n++;
                        sum += b.Position;
                    }
                if (n <= most) continue;
                most = n;
                best = sum / n;
            }
            return best;
        }

        private static Vector2? Centre(SimWorld world, int team)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != team || v.Flying || v.Def.Static || v.Scripted) continue;
                sum += v.Position;
                n++;
            }
            return n > 0 ? sum / n : null;
        }

        /// <summary>Reinforcement vehicles of a side alive now (C.4's own cap).</summary>
        public static int Reinforcements(SimWorld world, int team)
        {
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == team && v.Reinforcement) n++;
            return n;
        }

        private int Room(SimWorld world, int team) => Room(world, team, team == MissionMode.PlayerTeam ? Rules.AllyCap : Rules.EnemyCap);

        /// <summary>Room under a cap of the event's own (chapter 12's Total Offensive matches the enemy's cap).</summary>
        private int Room(SimWorld world, int team, int cap) => Math.Max(0, cap - Reinforcements(world, team) - Pending(team));

        /// <summary>Whether a vehicle of the player's side would see a spawn at this spot (its allies and scripted trucks aside).</summary>
        private bool Seen(SimWorld world, Vector2 at)
        {
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == MissionMode.PlayerTeam && !v.Scripted && Vector2.DistanceSquared(v.Position, at) < Rules.NearSight * Rules.NearSight)
                    return true;
            return false;
        }

        internal void Mix(Action<long> mix)
        {
            mix(_log.Count);
            foreach (var s in _states)
            {
                mix((long)s.Phase * 1000 + s.Fired);
                mix((long)Math.Round(s.StartAt * 20.0));
                mix(s.Units.Count * 31 + s.Count);
            }
            mix(_drops.Count);
            mix(_strikes.Count);
            mix(_rods.Count);
        }

        /// <summary>A stable hash of a text (string.GetHashCode differs between runs of .NET).</summary>
        internal static int Stable(string text)
        {
            unchecked
            {
                var h = (int)2166136261;
                foreach (var c in text) h = (h ^ c) * 16777619;
                return h;
            }
        }

        /// <summary>Whether a mission's events need the allied commander (Accord waves, a rescued convoy that joins them).</summary>
        public static bool NeedsAllies(MissionDef def)
        {
            static bool Any(IReadOnlyList<MissionEventDef> events)
            {
                foreach (var e in events)
                    if (e.Kind == MissionEventKind.AllyWave || (e.Kind == MissionEventKind.SideObjective && e.Word("type") == "rescue")) return true;
                return false;
            }
            if (Any(def.Events)) return true;
            foreach (var s in def.Stages)
                if (Any(s.Mission.Events)) return true;
            return false;
        }

        // ------------------------------------------------------------------ arrivals

        /// <summary>Vehicles on their way by parachute or drop pod: when they land, whose, where, which event brought them.</summary>
        private readonly List<(double due, string def, int team, Vector2 at, Vector2 inward, int state, bool ally)> _drops = new();

        private int Pending(int team)
        {
            var n = 0;
            foreach (var d in _drops)
                if (d.team == team) n++;
            return n;
        }

        private void StepDrops(SimWorld world)
        {
            for (var i = 0; i < _drops.Count; i++)
            {
                var d = _drops[i];
                if (world.Time < d.due) continue;
                _drops.RemoveAt(i--);
                Arrive(world, _states[d.state], d.def, d.team, d.at, d.inward, d.ally);
            }
        }

        /// <summary>How a group comes in at a spawn point: driving in (an edge, a rail head, the water), by parachute, or by drop pod.</summary>
        private void Deliver(SimWorld world, EventState s, IReadOnlyList<string> units, int team, Vector2 at, Vector2 inward, SpawnKind kind, bool ally,
            bool pods = false, Vector2? from = null)
        {
            var across = new Vector2(-inward.Y, inward.X);
            for (var i = 0; i < units.Count; i++)
            {
                var spot = world.ClampToMap(at + across * ((i % 4) - 1.5f) * 5f - inward * (i / 4) * 6f);
                var def = world.Catalog.Vehicle(units[i]);
                // Aircraft fly in over the edge of an air path or a landing zone, not out of the middle of it.
                if (def.Flying && from is { } edge && kind is SpawnKind.Landing or SpawnKind.Air) spot = world.ClampToMap(edge + across * ((i % 4) - 1.5f) * 6f);
                if (pods && !def.Flying)
                {
                    if (world.Catalog.TryGetSupport("pod_drop", out var pod)) world.Emit(SimEvent.StrikeWarning(team, pod, spot, spot, 6f));
                    _drops.Add((world.Time + 6.0, units[i], team, spot, inward, s.Index, ally));
                }
                else if (!def.Flying && kind is SpawnKind.Landing or SpawnKind.Air or SpawnKind.Drop)
                {
                    world.Emit(SimEvent.DeploymentQueued(team, units[i], spot, inward, EconomySystemDelivery));
                    _drops.Add((world.Time + EconomySystemDelivery, units[i], team, spot, inward, s.Index, ally));
                }
                else Arrive(world, s, units[i], team, spot, inward, ally);
            }
        }

        private const float EconomySystemDelivery = MachineBrigade.Sim.Economy.EconomySystem.DeliverySeconds;

        /// <summary>Seconds a reinforcement pushes on its own before its side's commander takes it over.</summary>
        private const double PushSeconds = 40.0;

        private Vehicle Arrive(SimWorld world, EventState s, string defId, int team, Vector2 at, Vector2 inward, bool ally)
        {
            var v = world.SpawnVehicle(defId, team, at, SimMath.HeadingOf(inward));
            v.Reinforcement = true;
            if (ally) v.Ally = true;
            s.Units.Add(v.Id);
            // A tower (Brandt's line) stands where it lands.
            if (!v.Def.Static)
                Push(world, v, team == MissionMode.PlayerTeam ? _host.PlayerGoal(world) ?? Centre(world, MissionMode.EnemyTeam)
                    : _host.EnemyGoal(world) ?? Centre(world, MissionMode.PlayerTeam));
            return v;
        }

        /// <summary>Sends a newly arrived vehicle into the fight (attack-moving on the goal); its commander leaves it be for a while.</summary>
        private static void Push(SimWorld world, Vehicle v, Vector2? goal)
        {
            if (goal is not { } to) return;
            v.ManualUntil = world.Time + PushSeconds;
            world.Submit(new Command(CommandType.AttackMove, v.Team, new[] { v.Id }, world.ClampToMap(to)));
        }
    }
}

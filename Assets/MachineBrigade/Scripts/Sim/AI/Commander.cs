#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.AI
{
    /// <summary>When an AI general changes its tactic during a battle (prompt 28 K).</summary>
    public enum TacticSwitching
    {
        Never,
        WhenLosing,
        Counter,
    }

    /// <summary>
    /// Prompt 28 K: difficulty changes the quality of the AI, not only numbers: reaction delay, how long it remembers
    /// (confidence decay), how well it spreads before splash, how often it flanks and focuses fire, and when its general
    /// changes tactic. The player's own Auto-buy and Support AI always plays Normal (K.2).
    /// </summary>
    public sealed class AiSkill
    {
        public float ReactionDelay { get; set; } = 0.8f;
        public float DecayScale { get; set; } = 1f;
        public float Spread { get; set; } = 1f;
        public float Flank { get; set; } = 1f;
        public float Focus { get; set; } = 1f;
        public TacticSwitching Switching { get; set; } = TacticSwitching.Never;

        /// <summary>The difficulty's skill, its reaction delay scaled from the catalog's Normal value (params.reactionDelay).</summary>
        public static AiSkill For(AiDifficulty difficulty, AiParams ai)
        {
            var p = ai.Has("params.reactionDelay") ? ai.Param("params.reactionDelay") : new AiParam(0.8f, 0.3f, 1.5f, "", "");
            float normal = p.Value, min = p.Min, max = p.Max;
            return difficulty switch
            {
                AiDifficulty.Easy => new AiSkill { ReactionDelay = max, DecayScale = 1.5f, Spread = 0.5f, Flank = 0.5f, Focus = 0f },
                AiDifficulty.Hard => new AiSkill
                {
                    ReactionDelay = normal - (normal - min) * 0.6f, DecayScale = 0.85f, Flank = 1.3f, Focus = 1.3f,
                    Switching = TacticSwitching.WhenLosing,
                },
                AiDifficulty.VeryHard => new AiSkill
                {
                    ReactionDelay = min, DecayScale = 0.6f, Flank = 1.3f, Focus = 1.3f, Switching = TacticSwitching.Counter,
                },
                _ => new AiSkill { ReactionDelay = normal },
            };
        }
    }

    /// <summary>The commander's strategic intent (B.1): what, where, when, what first, and how the army is split.</summary>
    public struct StrategicIntent
    {
        public Vector2? PrimaryObjective;
        public Vector2 PrimaryEffort;
        public Vector2? SecondaryObjective;

        /// <summary>"attack", "hold", "flank", "breakthrough", "pincer", "wait".</summary>
        public string TacticalIntent;
        public bool AttackWindow;

        /// <summary>Why the window is open or shut (the event or the ratio), for the viewer.</summary>
        public string WindowReason;
    }

    /// <summary>The result of asking for a tactic change (H.6).</summary>
    public enum TacticSwitchResult
    {
        Done,
        Same,
        Cooldown,
        Unknown,

        /// <summary>The mode's profile does not allow the tactic (prompt 28 appendix).</summary>
        NotAllowed,
    }

    /// <summary>
    /// Prompt 28 B: the AI general of one side, about once a second. It decides what, where, when, what first and how the
    /// army is split, and hands each squad a task; the squads (<see cref="SquadLayer"/>) choose how. Plans are held for the
    /// minimum commitment unless an emergency (the main objective lost, a big enemy attack, a boss phase). It also owns
    /// the side's tactic (H): buying shares, switching with a cooldown and a transition, and the general's own switches.
    /// </summary>
    public sealed partial class AiCommander
    {
        private readonly Func<SimWorld, Vector2?> _objective;
        private readonly float[] _spent = new float[8];
        private float _timer;
        private double _planSince = double.NegativeInfinity, _windowSince = double.NegativeInfinity, _fullSince = double.NaN;
        private double _losingSince = double.NaN, _prepStart = double.NaN;
        private int _lastBossPhase = -1;
        private string? _seenEnemyTactic;
        private bool _massing;

        public AiCommander(int team, int enemyTeam, AiSkill skill, string tactic, Func<SimWorld, Vector2?> objective)
        {
            Team = team;
            EnemyTeam = enemyTeam;
            Skill = skill;
            Tactic = tactic;
            _objective = objective;
            Squads = new SquadLayer(this);
            _timer = team == 1 ? 0.5f : 0f;
        }

        public int Team { get; }
        public int EnemyTeam { get; }
        public AiSkill Skill { get; set; }
        public SquadLayer Squads { get; }
        public StrategicIntent Intent;

        /// <summary>The side's tactic id (H.4), as chosen; <see cref="TacticDef.MergedInto"/> is followed when it is read.</summary>
        public string Tactic { get; private set; }

        /// <summary>A defending stance (ConquestAi's Defend): every squad holds.</summary>
        public bool Defending { get; set; }

        public double TacticReadyAt { get; private set; }
        public double TransitionUntil { get; private set; } = double.NegativeInfinity;
        public double LastSwitchAt { get; private set; } = double.NegativeInfinity;
        public bool InTransition { get; private set; }

        /// <summary>H.6 Boss Rush: tactic switches in a break between two bosses are free of the cooldown.</summary>
        public bool FreeSwitch { get; set; }

        /// <summary>H.10: per-squad tactics are open (after chapter 6); otherwise every squad plays the side's.</summary>
        public bool SquadTactics { get; set; }

        public bool WaitingForAir { get; private set; }
        public bool WaitingForArtillery { get; private set; }

        /// <summary>The side's fire stance (H.9); null: the tactic's.</summary>
        public FireStance? Stance { get; set; }

        private SimWorld? _world;

        public TacticDef CurrentTactic => (_world?.Catalog.AiData ?? Empty).Tactic(Tactic);

        private static readonly AiBehaviour Empty = new();

        public TacticDef TacticFor(Squad s) =>
            SquadTactics && s.TacticOverride != null ? (_world?.Catalog.AiData ?? Empty).Tactic(s.TacticOverride) : CurrentTactic;

        public FireStance StanceFor(Squad s) => Stance ?? TacticFor(s).Modules.Stance;

        /// <summary>
        /// Own/enemy strength for an attack: the tactic's (else the parameter), lowered by "use it or lose it" (I.4) only
        /// where the mode's profile has advancePressure and this side does not defend (prompt 28 appendix A, B).
        /// </summary>
        public float AttackThreshold(Squad? s)
        {
            var ai = _world?.Catalog.Ai;
            if (ai == null) return 1.2f;
            var t = (s != null ? TacticFor(s) : CurrentTactic).Modules.AttackThreshold ?? ai.AttackThreshold;
            if (double.IsNaN(_fullSince) || _world == null || !AdvancePressure(_world, Team)) return t;
            var low = ai.Get("economy.useOrLoseThreshold", 0.9f);
            var ramp = MathF.Max(1f, ai.Get("economy.useOrLoseRamp", 30f));
            var k = (float)Math.Clamp((_world.Time - _fullSince) / ramp, 0.0, 1.0);
            return MathF.Min(t, t + (low - t) * k);
        }

        /// <summary>Whether the side's attack threshold falls with a full army and bank: the profile's flag, never for the defender.</summary>
        public static bool AdvancePressure(SimWorld world, int team)
        {
            var p = world.AiProfile;
            return p.AdvancePressure && !p.Defends(team);
        }

        /// <summary>
        /// The tactic the profile lets the side play: the asked one if allowed, else balanced if allowed, else the first
        /// allowed; a profile with none (wave directors, bosses) plays balanced and never switches.
        /// </summary>
        public static string AllowedTactic(SimWorld world, string tactic)
        {
            var p = world.AiProfile;
            if (p.Tactics.Count == 0 || p.HasFlag("noGeneralTactic")) return "balanced";
            if (p.Allows(tactic)) return tactic;
            if (p.Allows("balanced")) return "balanced";
            foreach (var t in p.Tactics)
                if (world.Catalog.AiData.HasTactic(t)) return t;
            return "balanced";
        }

        /// <summary>H.6: asks for a new tactic. Cooldown (unless free), a transition, squads attacking lose their momentum.</summary>
        public TacticSwitchResult RequestTactic(SimWorld world, string tactic, string reason = "player")
        {
            _world = world;
            if (!world.Catalog.AiData.HasTactic(tactic)) return TacticSwitchResult.Unknown;
            if (tactic == Tactic) return TacticSwitchResult.Same;
            if (AllowedTactic(world, tactic) != tactic) return TacticSwitchResult.NotAllowed;
            if (!FreeSwitch && world.Time < TacticReadyAt) return TacticSwitchResult.Cooldown;
            var ai = world.Catalog.Ai;
            world.AiLog.Add(new DecisionEntry(world.Time, Team, AiLayer.Commander, 0, DecisionKind.Tactic, $"{Tactic} -> {tactic} ({reason})"));
            Tactic = tactic;
            LastSwitchAt = world.Time;
            TacticReadyAt = world.Time + ai.TacticCooldown;
            TransitionUntil = world.Time + ai.TacticTransition;
            InTransition = true;
            _prepStart = double.NaN;
            foreach (var s in Squads.Squads)
            {
                // Squads on the attack lose their momentum: they regroup and gather before going on (H.6).
                if (s.Action is SquadAction.Attack or SquadAction.FlankLeft or SquadAction.FlankRight) s.ActionSince = double.NegativeInfinity;
            }
            return TacticSwitchResult.Done;
        }

        /// <summary>H.10: a squad's own tactic, with its own cooldown; null hands it back to the side's.</summary>
        public TacticSwitchResult RequestSquadTactic(SimWorld world, Squad squad, string? tactic)
        {
            if (!SquadTactics) return TacticSwitchResult.Unknown;
            if (tactic != null && !world.Catalog.AiData.HasTactic(tactic)) return TacticSwitchResult.Unknown;
            if (world.Time < squad.OwnTacticReadyAt) return TacticSwitchResult.Cooldown;
            squad.TacticOverride = tactic;
            squad.OwnTacticReadyAt = world.Time + world.Catalog.Ai.TacticCooldown;
            squad.ActionSince = double.NegativeInfinity;
            world.AiLog.Add(new DecisionEntry(world.Time, Team, AiLayer.Squad, squad.Id, DecisionKind.Tactic, tactic ?? "(side's)"));
            return TacticSwitchResult.Done;
        }

        /// <summary>
        /// H.8: whether <paramref name="viewer"/> knows this side's tactic now: one of its recon or UAV vehicles has one of
        /// this side's vehicles in its own sight.
        /// </summary>
        public bool TacticSeenBy(SimWorld world, int viewer)
        {
            foreach (var spotter in world.VehicleList)
            {
                if (!spotter.IsAlive || spotter.Team != viewer) continue;
                var role = world.Catalog.AiData.Units.TryGetValue(spotter.Def.Id, out var r) ? r : null;
                if (role is not ("Recon" or "UAV" or "ScoutHeli")) continue;
                foreach (var v in world.VehicleList)
                    if (v.IsAlive && v.Team == Team && Vector2.Distance(v.Position, spotter.Position) <= spotter.Def.VisionRange) return true;
            }
            return false;
        }

        public void Tick(SimWorld world, float dt, IReadOnlyList<Vehicle> pool, AiCommander? enemy)
        {
            _world = world;
            if (InTransition && world.Time >= TransitionUntil) InTransition = false;
            Squads.Tick(world, dt);
            _timer -= dt;
            if (_timer > 0f) return;
            _timer = 1f;
            var intel = world.Intel.For(Team);
            intel.Decay = world.Catalog.Ai.ConfidenceDecay * Skill.DecayScale;
            world.AiLog.WarnPerMinute = world.Catalog.Ai.Get("world.churnWarn", 6f);
            Squads.Enlist(world, pool);
            UseOrLose(world);
            Plan(world, intel);
            Assign(world, intel);
            UnitsOutsideSquads(world, intel);
            SwitchTactic(world, intel, enemy);
        }

        // ------------------------------------------------------------------------------------------------ planning

        private void Plan(SimWorld world, TeamIntel intel)
        {
            var now = world.Time;
            var ai = world.Catalog.Ai;
            var m = CurrentTactic.Modules;
            var objective = _objective(world);
            // The plan is held for its minimum commitment unless an emergency (B.5).
            var emergency = Emergency(world, intel);
            if (Intent.PrimaryObjective == null || emergency || now - _planSince >= ai.MinCommit ||
                (objective.HasValue && Intent.PrimaryObjective.HasValue && Vector2.Distance(objective.Value, Intent.PrimaryObjective.Value) < 5f))
            {
                if (objective.HasValue != Intent.PrimaryObjective.HasValue ||
                    (objective.HasValue && Vector2.Distance(objective.Value, Intent.PrimaryObjective!.Value) >= 5f))
                {
                    _planSince = now;
                    world.AiLog.Add(new DecisionEntry(now, Team, AiLayer.Commander, 0, DecisionKind.Plan,
                        $"objective {(objective.HasValue ? $"({objective.Value.X:0},{objective.Value.Y:0})" : "the enemy")}{(emergency ? " (emergency)" : "")}"));
                }
                Intent.PrimaryObjective = objective;
            }
            var centre = OwnCentre(world, out var any);
            var target = Intent.PrimaryObjective ?? (EnemyCentre(intel) ?? centre);
            Intent.PrimaryEffort = Vector2.Distance(centre, target) > 1f ? Vector2.Normalize(target - centre) : Vector2.UnitY;
            Intent.SecondaryObjective = m.DropSecondary ? null : ArtilleryCentre(world) ?? ThreatenedPoint(intel);

            // Waiting conditions: air superiority waits for the enemy's aircraft to be gone; firepower for its barrages.
            WaitingForAir = m.WaitAir && (intel.EnemyComposition[(int)ForceGroup.Helicopter] + intel.EnemyComposition[(int)ForceGroup.Plane]) >
                0.05f * MathF.Max(1f, intel.EnemyTotal);
            var prep = Math.Max(m.ArtilleryPrep, (int)ai.ArtilleryPrep);
            if (prep > 0 && ArtilleryCentre(world).HasValue)
            {
                if (double.IsNaN(_prepStart)) _prepStart = now;
                WaitingForArtillery = now - _prepStart < prep * 8.0;
            }
            else WaitingForArtillery = false;

            // ATTACK_WINDOW: own strength over the threshold near the objective, or a WINDOW/OPPORTUNITY there.
            var (own, enemyThere) = intel.StrengthAround(target, 60f);
            own = MathF.Max(own, intel.OwnTotal * MainEffort(world));
            var threshold = AttackThreshold(null);
            string reason;
            var open = false;
            if (enemyThere <= 0f)
            {
                open = true;
                reason = "noEnemyKnown";
            }
            else if (own / enemyThere >= threshold)
            {
                open = true;
                reason = $"ratio {own / enemyThere:0.00} >= {threshold:0.00}";
            }
            else reason = $"ratio {own / enemyThere:0.00} < {threshold:0.00}";
            foreach (var e in intel.Events)
                if (e.Kind is IntelEventKind.Window or IntelEventKind.Opportunity && e.Confidence >= 0.5f && Vector2.Distance(e.Centre, target) < 80f &&
                    now - e.Created >= Skill.ReactionDelay)
                {
                    open = true;
                    reason = e.Reason;
                }
            if (WaitingForAir || WaitingForArtillery || InTransition || Defending) open = false;
            // The window is committed to like a plan: it does not flicker each second.
            if (open != Intent.AttackWindow && (now - _windowSince >= ai.MinCommit || emergency))
            {
                Intent.AttackWindow = open;
                Intent.WindowReason = reason;
                _windowSince = now;
                world.AiLog.Add(new DecisionEntry(now, Team, AiLayer.Commander, 0, DecisionKind.Plan, $"window {(open ? "open" : "shut")}: {reason}"));
            }
            Intent.TacticalIntent = Defending || m.Hold ? "hold" : WaitingForAir || WaitingForArtillery ? "wait" : m.Pincer ? "pincer" :
                m.MainEffort >= 0.7f ? "breakthrough" : m.Flank > 1f ? "flank" : "attack";

            var why = new List<string>();
            foreach (var e in intel.Events)
                if (e.Priority >= 60f) why.Add(e.ToString());
            world.AiLog.Record(new Why
            {
                Layer = AiLayer.Commander, Team = Team, Subject = 0, Time = now, Choice = Intent.TacticalIntent,
                Score = own / MathF.Max(0.01f, enemyThere), Context = $"{Tactic}; window {(Intent.AttackWindow ? "open" : "shut")} ({Intent.WindowReason})",
                Events = why,
            });
        }

        private bool Emergency(SimWorld world, TeamIntel intel)
        {
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Threat && e.Priority >= 90f) return true;
            // A boss of this side, or one it fights, changed phase.
            var phase = -1;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Def.Boss) phase = Math.Max(phase, v.Phase);
            var changed = _lastBossPhase >= 0 && phase != _lastBossPhase;
            _lastBossPhase = phase;
            // The main objective was lost (it is no longer what the objective chooser picks, and the plan is young).
            return changed;
        }

        private float MainEffort(SimWorld world) => CurrentTactic.Modules.MainEffort ?? world.Catalog.Ai.MainEffort;

        /// <summary>B.2: squads to tasks. The main effort's share of the strength goes to the primary objective (nearest first).</summary>
        private void Assign(SimWorld world, TeamIntel intel)
        {
            var squads = Squads.Squads;
            if (squads.Count == 0) return;
            var m = CurrentTactic.Modules;
            var total = 0f;
            foreach (var s in squads) total += s.Strength;
            var share = MainEffort(world);
            var target = Intent.PrimaryObjective;
            var order = new List<Squad>(squads);
            var to = target ?? (EnemyCentre(intel) ?? Vector2.Zero);
            order.Sort((a, b) =>
            {
                var da = Vector2.DistanceSquared(a.Centre, to);
                var db = Vector2.DistanceSquared(b.Centre, to);
                return da != db ? da.CompareTo(db) : a.Id.CompareTo(b.Id);
            });
            var assigned = 0f;
            var pincer = 0;
            var home = world.TryGetRally(Team, out var rally) ? rally : (Vector2?)null;
            foreach (var s in order)
            {
                var primary = assigned < total * share || Intent.SecondaryObjective == null || m.Together;
                SquadTask task;
                if (m.HoldBase && home.HasValue) task = new SquadTask { Kind = TaskKind.Secondary, Objective = home, Hold = true };
                else if (primary)
                {
                    task = new SquadTask { Kind = TaskKind.Primary, Objective = target, Window = Intent.AttackWindow, Hold = Defending || m.Hold };
                    if (m.Pincer && pincer < 3) task.FlankSide = pincer++ % 2 == 0 ? -1 : 1;
                    assigned += s.Strength;
                }
                else task = new SquadTask { Kind = TaskKind.Secondary, Objective = Intent.SecondaryObjective, Hold = true, Window = false };
                s.Task = task;
            }
        }

        // ------------------------------------------------------------------------------------------------ tactics

        private void SwitchTactic(SimWorld world, TeamIntel intel, AiCommander? enemy)
        {
            if (Skill.Switching == TacticSwitching.Never || world.Time < TacticReadyAt) return;
            var data = world.Catalog.AiData;
            // Seen through scouts and UAVs only (H.8).
            if (enemy != null && enemy.TacticSeenBy(world, Team)) _seenEnemyTactic = enemy.Tactic;
            if (Skill.Switching == TacticSwitching.Counter && _seenEnemyTactic != null && data.Tactic(Tactic).CounteredBy.Contains(_seenEnemyTactic))
            {
                if (Counter(data, _seenEnemyTactic) is { } counter) RequestTactic(world, counter, $"counter {_seenEnemyTactic}");
                return;
            }
            // Losing clearly: own strength under 0.6 of the enemy's for 20 s.
            if (intel.EnemyTotal > 0f && intel.OwnTotal < intel.EnemyTotal * 0.6f)
            {
                if (double.IsNaN(_losingSince)) _losingSince = world.Time;
                if (world.Time - _losingSince >= 20.0)
                {
                    var next = _seenEnemyTactic != null ? Counter(data, _seenEnemyTactic) : null;
                    next ??= Tactic == "depth" ? "attrition" : "depth";
                    if (data.HasTactic(next)) RequestTactic(world, next, "losing");
                    _losingSince = double.NaN;
                }
            }
            else _losingSince = double.NaN;
        }

        private string? Counter(AiBehaviour data, string enemyTactic)
        {
            foreach (var t in data.Tactics)
                if (t.MergedInto == null && t.Id != Tactic && t.Counters.Contains(enemyTactic)) return t.Id;
            return null;
        }

        // ------------------------------------------------------------------------------------------------ economy

        /// <summary>I.4: the side is at its vehicle cap with a full bank: the attack threshold falls over the ramp.</summary>
        private void UseOrLose(SimWorld world)
        {
            if (!world.TryGetEconomy(Team, out var economy)) return;
            var full = economy.VehicleCount >= economy.VehicleCap && economy.Cp >= economy.Bank - 1f;
            if (!full) _fullSince = double.NaN;
            else if (double.IsNaN(_fullSince)) _fullSince = world.Time;
        }

        /// <summary>Counts a purchase's CP to its group (H.5: shares by CP spent, not by vehicles).</summary>
        public void Bought(VehicleDef def, float cp)
        {
            if (TeamIntel.GroupOf(def) is { } g) _spent[(int)g] += cp;
        }

        /// <summary>The CP spent per group so far.</summary>
        public IReadOnlyList<float> Spent => _spent;

        /// <summary>
        /// H.5: how much a card helps the tactic's force shares: the group furthest below its (soft) target first; MISMATCH
        /// moves a group's target by up to 15 points; groups the deck lacks give their share to the rest; the tactic's
        /// preferred cards within a group first.
        /// </summary>
        public float BuyScore(SimWorld world, TeamEconomy economy, VehicleDef def)
        {
            if (TeamIntel.GroupOf(def) is not { } g) return 0f;
            var target = Targets(world, economy);
            var spent = 0f;
            foreach (var x in _spent) spent += x;
            var have = spent > 0f ? _spent[(int)g] / spent : 0f;
            var score = (target[(int)g] - have) * 6f;
            foreach (var p in CurrentTactic.Prefer)
                if (p == def.Id) score += 1.5f;
            return score;
        }

        /// <summary>The tactic's CP shares for this deck, moved by MISMATCH events (at most 15 points a group).</summary>
        public float[] Targets(SimWorld world, TeamEconomy economy)
        {
            var target = (float[])CurrentTactic.Cp.Clone();
            var intel = world.Intel.For(Team);
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.Mismatch && e.Need is { } need) target[(int)need] += 0.15f * e.Confidence;
            // The deck's groups only; the missing ones' shares go to the rest in proportion.
            var present = new bool[8];
            foreach (var id in economy.Vehicles)
                if (world.Catalog.Vehicles.TryGetValue(id, out var d) && TeamIntel.GroupOf(d) is { } dg) present[(int)dg] = true;
            var sum = 0f;
            for (var i = 0; i < 8; i++)
            {
                if (!present[i]) target[i] = 0f;
                sum += target[i];
            }
            if (sum > 0f)
                for (var i = 0; i < 8; i++) target[i] /= sum;
            return target;
        }

        /// <summary>All-out assault (cpSaving): with an army out and no fight on its hands, save to 90 % of the bank, then spend it all.</summary>
        public bool SavingUp(SimWorld world, TeamEconomy economy)
        {
            var saving = CurrentTactic.Modules.CpSaving || world.Catalog.Ai.CpSaving >= 0.5f;
            if (!saving) return false;
            // spendPressure (prompt 28 appendix A): never sit at the bank cap; the saving ends at a full bank.
            if (world.AiProfile.SpendPressure && economy.Cp >= economy.Bank - 1f) return false;
            if (_massing && economy.Cp < 6f) _massing = false;
            if (!_massing && economy.Cp >= economy.Bank * 0.9f) _massing = true;
            return !_massing && economy.VehicleCount >= 4;
        }

        /// <summary>
        /// B.4: a support card for the situation: smoke over a squad under artillery or a big attack's threat; SEAD on
        /// known enemy anti-air before an air window (Air superiority, SEAD first). Null when nothing fits.
        /// </summary>
        public (SupportKind kind, Vector2 at)? SupportWanted(SimWorld world)
        {
            var intel = world.Intel.For(Team);
            foreach (var s in Squads.Squads)
                if (s.State == SquadState.Combat && intel.ThreatAt(ThreatKind.Artillery, s.Centre) > s.Strength) return (SupportKind.Smoke, s.Centre);
            var m = CurrentTactic.Modules;
            if (m.SeadCards || m.WaitAir)
            {
                Contact? aa = null;
                foreach (var c in intel.Contacts)
                    if (c.Group == ForceGroup.AntiAir && !c.Displaced && (aa == null || c.Strength > aa.Strength)) aa = c;
                if (aa != null) return (SupportKind.Sead, aa.Position);
            }
            return null;
        }

        // ------------------------------------------------------------------------------------------------ helpers

        private Vector2 OwnCentre(SimWorld world, out bool any)
        {
            Vector2 sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && !v.Def.Static && !v.Flying)
                {
                    sum += v.Position;
                    n++;
                }
            any = n > 0;
            if (n > 0) return sum / n;
            return world.TryGetRally(Team, out var rally) ? rally : Vector2.Zero;
        }

        private static Vector2? EnemyCentre(TeamIntel intel)
        {
            Vector2 sum = Vector2.Zero;
            var w = 0f;
            foreach (var g in intel.EnemyGroups)
                if (!g.Air)
                {
                    sum += g.Centre * g.Strength;
                    w += g.Strength;
                }
            return w > 0f ? sum / w : null;
        }

        private Vector2? ArtilleryCentre(SimWorld world)
        {
            Vector2 sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Team && !v.Def.Static && v.Def.Weapon.MinRange > 0f)
                {
                    sum += v.Position;
                    n++;
                }
            return n > 0 ? sum / n : null;
        }

        private static Vector2? ThreatenedPoint(TeamIntel intel)
        {
            foreach (var e in intel.Events)
                if (e.Kind == IntelEventKind.ObjectivePressure) return e.Centre;
            return null;
        }
    }

    /// <summary>
    /// B.7: a small hint line for the player, from high-priority events (never an order). Key and place; the HUD words
    /// them (text table "aihint.*") and the player can turn them off. At most one hint per key every 20 s.
    /// </summary>
    public sealed class AiHints
    {
        private readonly Dictionary<string, double> _last = new(StringComparer.Ordinal);

        public readonly struct Hint
        {
            public Hint(string key, Vector2 at, double time)
            {
                Key = key;
                At = at;
                Time = time;
            }

            /// <summary>"aihint.bigAttack", "aihint.needAntiAir", "aihint.enemyArtillery", "aihint.stuck", ...</summary>
            public string Key { get; }
            public Vector2 At { get; }
            public double Time { get; }
        }

        /// <summary>The next hint for <paramref name="team"/>, if one is due (call about once a second).</summary>
        public Hint? Next(SimWorld world, int team, SquadLayer? squads = null)
        {
            var intel = world.Intel.For(team);
            IntelEvent? best = null;
            string? key = null;
            foreach (var e in intel.Events)
            {
                if (e.Priority < 60f) continue;
                var k = e.Kind switch
                {
                    IntelEventKind.Threat when e.Reason.StartsWith("big", StringComparison.Ordinal) => "aihint.bigAttack",
                    IntelEventKind.Threat when e.Reason.StartsWith("strike", StringComparison.Ordinal) => "aihint.strike",
                    IntelEventKind.Threat when e.Reason.Contains("aircraft") => "aihint.airInbound",
                    IntelEventKind.Threat => "aihint.overwhelmed",
                    IntelEventKind.Mismatch when e.Need == ForceGroup.AntiAir => "aihint.needAntiAir",
                    IntelEventKind.Mismatch => "aihint.needAntiTank",
                    IntelEventKind.Opportunity when e.Reason.StartsWith("Artillery", StringComparison.Ordinal) => "aihint.enemyArtillery",
                    IntelEventKind.Opportunity => "aihint.opportunity",
                    IntelEventKind.Window => "aihint.window",
                    _ => "aihint.losingPoint",
                };
                if (_last.TryGetValue(k, out var at) && world.Time - at < 20.0) continue;
                if (best == null || e.Priority > best.Priority)
                {
                    best = e;
                    key = k;
                }
            }
            if (squads != null && key == null)
                foreach (var s in squads.Squads)
                    if (s.Progress.Count > 0 && Stuck(s) && !(_last.TryGetValue("aihint.stuck", out var st) && world.Time - st < 20.0))
                    {
                        _last["aihint.stuck"] = world.Time;
                        return new Hint("aihint.stuck", s.Centre, world.Time);
                    }
            if (best == null || key == null) return null;
            _last[key] = world.Time;
            return new Hint(key, best.Centre, world.Time);
        }

        private static bool Stuck(Squad s)
        {
            foreach (var p in s.Progress.Values)
                if (p.rung >= 2) return true;
            return false;
        }
    }
}

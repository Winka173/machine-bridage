#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER section 13: the army's role budget (a unit may fill several).</summary>
    public enum ProcurementRole
    {
        Frontline,
        AntiTank,
        AntiAir,
        Artillery,
        Recon,
        Engineer,
        ElectronicWarfare,
        Drone,
        FastFlank,
        Siege,
        NavalScreen,
        NavalStrike,
        AirCover,
    }

    /// <summary>AI MASTER section 16: a batch of 3-5 cards bought for one purpose, cancelled when the situation changes.</summary>
    public sealed class PurchasePlan
    {
        public PurchasePlan(IReadOnlyList<string> cards, string purpose, float expectedPower, int cpCost, double created, int signature)
        {
            Cards = cards;
            Purpose = purpose;
            ExpectedPower = expectedPower;
            CpCost = cpCost;
            Created = created;
            Signature = signature;
        }

        public IReadOnlyList<string> Cards { get; }
        public string Purpose { get; }
        public float ExpectedPower { get; }
        public int CpCost { get; }
        public double Created { get; }

        /// <summary>The confirmed counter needs it was made for (a change cancels it).</summary>
        public int Signature { get; }

        /// <summary>The next card to buy (cards before it are bought or skipped).</summary>
        public int Next { get; internal set; }

        public bool Done => Next >= Cards.Count;

        public override string ToString() => $"{Purpose}: {string.Join(", ", Cards)} ({CpCost} CP, next {Next})";
    }

    /// <summary>
    /// AI MASTER sections 9-18, 196-198, 208-209 (lane P0-B): the buying AI's director, one per commander. Integrated into the
    /// existing buying score (<see cref="ConquestAi"/>'s TryDeploy, Part A): hard legality and map feasibility first (a card
    /// with no map influence is REJECTED before any scoring), then the master score (role deficit by the tactic's shares,
    /// counter need from observed intel smoothed by an EMA with a confidence and a 4 s confirmation, objective fit, map
    /// influence, time to value, survivability, synergy, cost, tactic; minus redundancy, congestion and long travel) is
    /// added to the legacy score with <c>ai.procurement.blendWeight</c>; purchase plans of 3-5 cards, a bounded CP reserve,
    /// same-match feedback (low realised utilisation lowers a card), counter saturation, soft floors and capability
    /// replacement. Fog-fair (only what the side has seen), deterministic (no dictionary order decides anything).
    /// </summary>
    public sealed class ProcurementDirector
    {
        /// <summary>The enemy composition the director smooths (section 14): what is seen, by kind.</summary>
        public enum Threat
        {
            Air,
            HeavyArmour,
            Light,
            Artillery,
            Drones,
            Naval,
            AntiAir,
            AntiTank,
        }

        private const int Roles = 13;
        private const int Threats = 8;

        private readonly int _team;
        private readonly float[] _ema = new float[Threats];
        private readonly double[] _since = new double[Threats];
        private readonly bool[] _ever = new bool[Threats];
        private readonly float[] _desired = new float[Roles];
        private readonly float[] _have = new float[Roles];
        private readonly float[] _lost = new float[Roles];
        private readonly float[] _answer = new float[Threats];
        private readonly Dictionary<string, (float combat, float firing)> _use = new(StringComparer.Ordinal);
        private readonly List<(EntityId id, VehicleDef def)> _fielded = new();
        private readonly List<(EntityId id, VehicleDef def)> _fieldedNext = new();
        private readonly Dictionary<string, string> _lastReject = new(StringComparer.Ordinal);
        private double _lastObserve = double.NaN;
        private double _lostAt = double.NegativeInfinity;
        private double _reserveSince = double.NaN;
        private float _haveTotal;
        private float _confidence;
        private float _ownTotal;
        private int _ownGround;

        public ProcurementDirector(int team)
        {
            _team = team;
            for (var i = 0; i < Threats; i++) _since[i] = double.NaN;
        }

        /// <summary>The plan being bought, if any (section 16).</summary>
        public PurchasePlan? Plan { get; private set; }

        /// <summary>The targets and objectives the last <see cref="Observe"/> built (fog-fair).</summary>
        public FeasibilityContext? Context { get; private set; }

        /// <summary>Rejections so far (the AI health monitor's noMapInfluencePurchases is purchases, which stay 0).</summary>
        public int Rejections { get; private set; }

        /// <summary>The smoothed enemy share of a threat kind (section 15).</summary>
        public float Share(Threat t) => _ema[(int)t];

        /// <summary>A counter need that has held its threshold and confidence for the confirmation time (section 15).</summary>
        public bool Confirmed(Threat t, double now) =>
            !double.IsNaN(_since[(int)t]) && now - _since[(int)t] >= SimTunables.Ai.Procurement.MismatchConfirmSeconds - 1e-6;

        // ------------------------------------------------------------------------------------------------ observing

        /// <summary>
        /// Once per buying decision: smooth what is seen of the enemy (EMA 0.20, decaying when nothing is in sight), count
        /// the army by role, note losses (capability replacement) and each card's realised use, and build the feasibility
        /// context: the enemies seen, points not held, the mission's goal, the other camp.
        /// </summary>
        public void Observe(SimWorld world, IReadOnlyList<Vehicle> known, Vector2 deployAt, Modes.IObjectiveMode? mode,
            Vector2? goal, Vector2? defendPoint, float[]? desiredByGroup, float[]? legacyMix)
        {
            var now = world.Time;
            var dt = double.IsNaN(_lastObserve) ? 0f : (float)Math.Min(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ObserveNowCap, now - _lastObserve);
            _lastObserve = now;
            var p = SimTunables.Ai.Procurement.IntelEma;

            // Section 14-15: the enemy seen now, by kind, by value.
            var current = new float[Threats];
            var seen = 0f;
            foreach (var e in known)
            {
                if (!e.IsAlive || e.Team == _team) continue;
                var value = e.Def.Boss ? global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ObserveBossTrue : MathF.Max(1f, e.Def.CpCost);
                seen += value;
                var layer = EngagementFeasibility.LayerOf(world, e);
                if (layer == TargetLayer.Air) current[(int)Threat.Air] += value;
                if (layer == TargetLayer.Naval) current[(int)Threat.Naval] += value;
                if (layer == TargetLayer.Ground && e.Def.Armour.Front >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ObserveFrontMin) current[(int)Threat.HeavyArmour] += value;
                if (layer == TargetLayer.Ground && e.Def.Class is UnitClass.Scout or UnitClass.Light) current[(int)Threat.Light] += value;
                if (e.Def.Weapon.MinRange > 0f && !e.Flying) current[(int)Threat.Artillery] += value;
                if (e.Def.Drone || Catalog.FliesDrones(e.Def)) current[(int)Threat.Drones] += value;
                if (EngagementFeasibility.CanHit(e.Def, TargetLayer.Air) && !e.Flying) current[(int)Threat.AntiAir] += value;
                if (KillsArmour(e.Def)) current[(int)Threat.AntiTank] += value;
            }
            _confidence = MathF.Min(1f, seen / MathF.Max(1f, SimTunables.Ai.Procurement.ConfidenceCp));
            for (var t = 0; t < Threats; t++)
            {
                var share = seen > 0f ? current[t] / seen : 0f;
                // Nothing in sight: the picture goes stale and the need decays (section 14).
                _ema[t] = seen > 0f ? _ema[t] + (share - _ema[t]) * p : _ema[t] * (1f - p);
                if (share > 0f) _ever[t] = true;
                var over = _ema[t] >= SimTunables.Ai.Procurement.MismatchShare && _confidence >= SimTunables.Ai.Procurement.MismatchConfidence;
                if (!over) _since[t] = double.NaN;
                else if (double.IsNaN(_since[t])) _since[t] = now;
            }

            // The army by role (deliveries on the way are not yet on the field), and the share of it that answers each threat.
            Array.Clear(_have, 0, Roles);
            Array.Clear(_answer, 0, Threats);
            _haveTotal = 0f;
            _ownTotal = 0f;
            _ownGround = 0;
            _fieldedNext.Clear();
            var roles = new float[Roles];
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != _team || v.Def.Static || v.Scripted || v.IsEscort || v.Garrison) continue;
                _fieldedNext.Add((v.Id, v.Def));
                var value = MathF.Max(1f, v.Def.CpCost);
                _ownTotal += value;
                if (!v.Flying) _ownGround++;
                RolesOf(v.Def, roles);
                var sum = 0f;
                foreach (var r in roles) sum += r;
                if (sum > 0f)
                    for (var r = 0; r < Roles; r++) _have[r] += value * roles[r] / sum;
                _haveTotal += value;
                for (var t = 0; t < Threats; t++)
                    if (Answers(v.Def, (Threat)t)) _answer[t] += value;
                // Section 196: realised use per card while there is a fight in its reach.
                Track(world, v, known, dt);
            }
            // Section 209: what died leaves its roles short (not its card id) for a while.
            var decay = MathF.Max(1f, SimTunables.Ai.Procurement.CapabilitySeconds);
            if (dt > 0f)
                for (var r = 0; r < Roles; r++) _lost[r] *= MathF.Max(0f, 1f - dt / decay);
            foreach (var (id, def) in _fielded)
            {
                var alive = false;
                foreach (var (nid, _) in _fieldedNext)
                    if (nid.Value == id.Value)
                    {
                        alive = true;
                        break;
                    }
                if (alive) continue;
                RolesOf(def, roles);
                var sum = 0f;
                foreach (var r in roles) sum += r;
                var value = MathF.Max(1f, def.CpCost);
                if (sum > 0f)
                    for (var r = 0; r < Roles; r++) _lost[r] += value * roles[r] / sum;
                _lostAt = now;
            }
            _fielded.Clear();
            _fielded.AddRange(_fieldedNext);

            Desired(desiredByGroup, legacyMix);
            Context = EngagementFeasibility.Observed(world, _team, deployAt, known, mode, goal, defendPoint);
        }

        private void Track(SimWorld world, Vehicle v, IReadOnlyList<Vehicle> known, float dt)
        {
            if (dt <= 0f) return;
            var ground = WeaponEnvelope.Of(v.Def, TargetLayer.Ground).MaxRange;
            var air = WeaponEnvelope.Of(v.Def, TargetLayer.Air).MaxRange;
            if (ground <= 0f && air <= 0f) return;
            var fired = world.Time - v.LastFiredAt <= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.TrackTimeMax;
            var inReach = fired;
            for (var i = 0; i < known.Count && !inReach; i++)
            {
                var e = known[i];
                if (!e.IsAlive) continue;
                var reach = (e.Flying ? air : ground) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.TrackScale + e.Radius;
                if (reach > 0f && Vector2.DistanceSquared(e.Position, v.Position) <= reach * reach) inReach = true;
            }
            if (!inReach) return;
            var key = v.Def.EliteOf ?? v.Def.Id;
            _use.TryGetValue(key, out var u);
            _use[key] = (u.combat + dt, u.firing + (fired ? dt : 0f));
        }

        /// <summary>Section 196: 1, or down to <c>feedbackMinModifier</c> for a card that has fought 20 s and fired under 15 % of it.</summary>
        public float FeedbackModifier(string cardId)
        {
            if (!_use.TryGetValue(cardId, out var u) || u.combat < SimTunables.Ai.Procurement.FeedbackCombatSeconds) return 1f;
            var utilization = u.firing / MathF.Max(1e-3f, u.combat);
            var low = SimTunables.Ai.Procurement.FeedbackUtilization;
            if (utilization >= low) return 1f;
            var min = SimTunables.Ai.Procurement.FeedbackMinModifier;
            return min + (1f - min) * Math.Clamp(utilization / MathF.Max(1e-3f, low), 0f, 1f);
        }

        /// <summary>Records realised use directly (tests; a replay of stored stats).</summary>
        internal void RecordUse(string cardId, float combatSeconds, float firingSeconds) => _use[cardId] = (combatSeconds, firingSeconds);

        /// <summary>Section 13: the tactic's shares mapped onto the roles (the layered general's force groups, else the legacy mix, else Balanced).</summary>
        private void Desired(float[]? groups, float[]? mix)
        {
            Array.Clear(_desired, 0, Roles);
            if (groups != null && groups.Length >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.DesiredLengthMin)
            {
                _desired[(int)ProcurementRole.Frontline] = groups[(int)ForceGroup.Armour];
                _desired[(int)ProcurementRole.FastFlank] = groups[(int)ForceGroup.Light] * 0.6f;
                _desired[(int)ProcurementRole.Recon] = groups[(int)ForceGroup.Light] * 0.4f;
                _desired[(int)ProcurementRole.AntiTank] = groups[(int)ForceGroup.AntiTank];
                _desired[(int)ProcurementRole.Artillery] = groups[(int)ForceGroup.Artillery];
                _desired[(int)ProcurementRole.AntiAir] = groups[(int)ForceGroup.AntiAir];
                _desired[(int)ProcurementRole.AirCover] = groups[(int)ForceGroup.Helicopter] + groups[(int)ForceGroup.Plane];
                _desired[(int)ProcurementRole.Engineer] = groups[(int)ForceGroup.Support] * 0.6f;
                _desired[(int)ProcurementRole.ElectronicWarfare] = groups[(int)ForceGroup.Support] * 0.4f;
            }
            else if (mix != null && mix.Length >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.DesiredLengthMin2)
            {
                _desired[(int)ProcurementRole.Frontline] = mix[0] * 2f / 3f;
                _desired[(int)ProcurementRole.AntiTank] = mix[0] / 3f;
                _desired[(int)ProcurementRole.FastFlank] = mix[1] * 2f / 3f;
                _desired[(int)ProcurementRole.Recon] = mix[1] / 3f;
                _desired[(int)ProcurementRole.Artillery] = mix[2];
                _desired[(int)ProcurementRole.AntiAir] = mix[3];
                _desired[(int)ProcurementRole.AirCover] = mix[4];
            }
            else
            {
                // Section 13's Balanced; its "Flexible" 0.10 goes to air cover and drones.
                _desired[(int)ProcurementRole.Frontline] = 0.28f;
                _desired[(int)ProcurementRole.AntiTank] = 0.15f;
                _desired[(int)ProcurementRole.AntiAir] = 0.12f;
                _desired[(int)ProcurementRole.Artillery] = 0.10f;
                _desired[(int)ProcurementRole.Recon] = 0.07f;
                _desired[(int)ProcurementRole.Engineer] = 0.06f;
                _desired[(int)ProcurementRole.FastFlank] = 0.08f;
                _desired[(int)ProcurementRole.ElectronicWarfare] = 0.04f;
                _desired[(int)ProcurementRole.AirCover] = 0.06f;
                _desired[(int)ProcurementRole.Drone] = 0.04f;
            }
        }

        // ------------------------------------------------------------------------------------------------ the hard filter

        /// <summary>
        /// Sections 10-11 and 101: the map filter, before any score. False (and a REJECT line in the decision log when the
        /// verdict changes) when the card cannot be deployed, or cannot reach an objective or an enemy, cannot fire on one from
        /// ground it can reach, and has no strategic utility. Ground units stay eligible from the shore (firing reach) and for
        /// land objectives.
        /// </summary>
        public bool Gate(SimWorld world, VehicleDef def, out InfluenceResult influence)
        {
            var ctx = Context ?? new FeasibilityContext(_team, Vector2.Zero);
            influence = world.Feasibility.Evaluate(def, ctx);
            string? reason = null;
            if (!influence.CanDeploy) reason = "deployment-unreachable";
            else if (!influence.Useful && !IsStrategicUtility(def, influence, world.Time)) reason = "no-map-influence";
            var key = def.Id;
            if (reason == null)
            {
                _lastReject.Remove(key);
                return true;
            }
            Rejections++;
            if (!_lastReject.TryGetValue(key, out var last) || last != reason)
            {
                _lastReject[key] = reason;
                var code = reason == "no-map-influence" ? "PURCHASE_NO_MAP_INFLUENCE" : "PURCHASE_DEPLOYMENT_UNREACHABLE";
                world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Purchase,
                    $"REJECT {def.Id} reason={reason} ({code}; {influence})"));
            }
            return false;
        }

        /// <summary>The cards rejected at the last check, with their reason (the debug view, tests).</summary>
        public string? LastReject(string cardId) => _lastReject.TryGetValue(cardId, out var r) ? r : null;

        /// <summary>
        /// Section 10-11: a unit that pays without fighting where it can drive: repair and rearm, command, recon, jammers,
        /// counter-battery radars, shield domes, and a soft floor's anti-air while the side has none and aircraft have been
        /// seen this battle (section 198). Never when it cannot even reach anything with nothing known (that is no target, not
        /// no influence).
        /// </summary>
        public bool IsStrategicUtility(VehicleDef def, InfluenceResult influence, double now)
        {
            if (!influence.CanDeploy) return false;
            if (def.RepairAura != null || def.RearmAura != null || def.AirRearm != null || def.CommandAura != null ||
                def.Jammer > 0f || def.CounterBattery != null || def.Dome != null || def.ReconPass != null)
                return _ownTotal > 0f;
            // Soft floor: anti-air with none on the field once enemy aircraft have shown.
            return EngagementFeasibility.CanHit(def, TargetLayer.Air) && _ever[(int)Threat.Air] && _answer[(int)Threat.Air] <= 0f;
        }

        // ------------------------------------------------------------------------------------------------ the score

        /// <summary>
        /// Section 12: the master score (inputs 0-1, the spec's weights), minus redundancy, congestion and long travel, times
        /// the same-match feedback. <paramref name="factors"/> gets the named parts for the decision log.
        /// </summary>
        public float Score(SimWorld world, TeamEconomy economy, VehicleDef def, InfluenceResult inf, int copies,
            AiCommander? commander, List<Factor>? factors)
        {
            var w = SimTunables.Ai.Procurement.Weights;
            float W(int i) => w != null && i < w.Length ? w[i] : 0f;
            var now = world.Time;
            var late = Math.Clamp((float)(now - SimTunables.Ai.Procurement.LateGameSeconds) / MathF.Max(1f, SimTunables.Ai.Procurement.LateGameSeconds), 0f, 1f);

            var role = RoleDeficit(def, out var saturated);
            var counter = CounterNeed(def, now);
            var objective = ObjectiveFit(def, inf);
            var influence = inf.NoTargets ? 0.5f : inf.Coverage;
            var timing = TimingFit(def, inf) * (1f + late);
            var survive = SurvivabilityFit(def);
            var synergy = Synergy(def);
            var cost = Math.Clamp(def.CombatValue * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreCombatValueScale, 0f, 1f) * (1f - global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreLateScale * late);
            var tactic = TacticPreference(def, economy, commander);

            var redundancy = copies * SimTunables.Ai.Procurement.RedundancyPerCopy + (saturated ? global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreSaturatedTrue : 0f);
            var congestion = Congestion(world, economy, def);
            var travel = float.IsPositiveInfinity(inf.TravelSeconds) ? 0f
                : Math.Clamp((inf.TravelSeconds - SimTunables.Ai.Procurement.LongTravelSeconds) / MathF.Max(1f, SimTunables.Ai.Procurement.LongTravelSeconds), 0f, 1f)
                  * SimTunables.Ai.Procurement.LongTravelMax;

            var score = W(0) * role + W(1) * counter + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreI) * objective + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreI2) * influence + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreI3) * timing + W(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreI4) * survive +
                        W(6) * synergy + W(7) * cost + W(8) * tactic - redundancy - congestion - travel;
            var feedback = FeedbackModifier(def.EliteOf ?? def.Id);
            if (score > 0f) score *= feedback;
            if (factors != null)
            {
                factors.Add(new Factor("role", W(0) * role * 100f));
                factors.Add(new Factor("counter", W(1) * counter * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreWScale));
                factors.Add(new Factor("objective", W(2) * objective * 100f));
                factors.Add(new Factor("map", W(3) * influence * 100f));
                factors.Add(new Factor("timing", W(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreI3) * timing * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreWScale));
                factors.Add(new Factor("survive", W(5) * survive * 100f));
                factors.Add(new Factor("synergy", W(6) * synergy * 100f));
                factors.Add(new Factor("cost", W(7) * cost * 100f));
                factors.Add(new Factor("tactic", W(8) * tactic * 100f));
                if (redundancy > 0f) factors.Add(new Factor(saturated ? "role-saturated" : "redundancy", -redundancy * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ScoreRedundancyScale));
                if (congestion > 0f) factors.Add(new Factor("congestion", -congestion * 100f));
                if (travel > 0f) factors.Add(new Factor("long-travel", -travel * 100f));
                if (feedback < 1f) factors.Add(new Factor("low-realized-utilization", -(1f - feedback) * 100f));
            }
            return score;
        }

        /// <summary>
        /// What the director adds to the legacy buying score: the master score times <c>ai.procurement.blendWeight</c>
        /// (scaled by difficulty: Easy half), minus the same-match feedback's points.
        /// </summary>
        public float LegacyAdjust(float masterScore, VehicleDef def, AiDifficulty difficulty)
        {
            var scale = difficulty switch { AiDifficulty.Easy => 0.5f, AiDifficulty.Normal => 0.75f, _ => 1f };
            var adjust = masterScore * SimTunables.Ai.Procurement.BlendWeight * scale;
            adjust -= (1f - FeedbackModifier(def.EliteOf ?? def.Id)) * SimTunables.Ai.Procurement.FeedbackPoints;
            return adjust;
        }

        /// <summary>Sections 13, 197, 198, 209: how far the card's roles are below their share (existing coverage counted; losses and soft floors added).</summary>
        public float RoleDeficit(VehicleDef def, out bool saturated)
        {
            var roles = new float[Roles];
            RolesOf(def, roles);
            var sum = 0f;
            foreach (var r in roles) sum += r;
            saturated = false;
            if (sum <= 0f) return 0f;
            var total = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RoleDeficitHaveTotalFloor, _haveTotal);
            var floors = SimTunables.Ai.Procurement.Floors;
            var best = 0f;
            var primary = -1;
            var primaryWeight = 0f;
            for (var r = 0; r < Roles; r++)
            {
                if (roles[r] <= 0f) continue;
                if (roles[r] > primaryWeight)
                {
                    primaryWeight = roles[r];
                    primary = r;
                }
                var have = _have[r] / total;
                var want = _desired[r] + _lost[r] / total;
                // Soft floors (section 198): a little recon, anti-air and anti-tank while the threat can appear.
                var floor = r switch
                {
                    (int)ProcurementRole.Recon => FloorOf(floors, 0, true),
                    (int)ProcurementRole.AntiAir => FloorOf(floors, 1, _ever[(int)Threat.Air] || _ever[(int)Threat.Drones]),
                    (int)ProcurementRole.AntiTank => FloorOf(floors, global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RoleDeficitI, _ever[(int)Threat.HeavyArmour] || _ever[(int)Threat.Naval]),
                    _ => 0f,
                };
                want = MathF.Max(want, floor);
                if (want <= 0f) continue;
                var deficit = Math.Clamp((want - have) / want, 0f, 1f) * (roles[r] / sum);
                best = MathF.Max(best, deficit);
            }
            if (primary >= 0)
            {
                var want = _desired[primary] + _lost[primary] / total;
                saturated = want > 0f ? _have[primary] / total > want * SimTunables.Ai.Procurement.Saturation : _have[primary] > 0f;
            }
            return Math.Clamp(best * 1.0f / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RoleDeficitMaxWeightFloor, MaxWeight(roles, sum)), 0f, 1f);

            static float FloorOf(float[]? f, int i, bool plausible) => plausible && f != null && i < f.Length ? f[i] : 0f;
        }

        private static float MaxWeight(float[] roles, float sum)
        {
            var m = 0f;
            foreach (var r in roles) m = MathF.Max(m, r / sum);
            return m;
        }

        /// <summary>Sections 14, 15, 197: confirmed needs (smoothed share past the threshold with confidence for 4 s), less the army's existing answer.</summary>
        public float CounterNeed(VehicleDef def, double now)
        {
            var own = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.CounterNeedOwnTotalFloor, _ownTotal);
            var best = 0f;
            for (var t = 0; t < Threats; t++)
            {
                if (t == (int)Threat.AntiAir || t == (int)Threat.AntiTank) continue; // threats to us, not counters to buy
                if (!Confirmed((Threat)t, now) || !Answers(def, (Threat)t)) continue;
                var share = _ema[t];
                var answered = _answer[t] / own;
                var need = Math.Clamp((share - answered * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.CounterNeedAnsweredScale) / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.CounterNeedShareFloor, share), 0f, 1f) * _confidence;
                best = MathF.Max(best, need);
            }
            return best;
        }

        private static float ObjectiveFit(VehicleDef def, InfluenceResult inf)
        {
            if (inf.NoTargets) return 0.5f;
            var fit = inf.ObjectiveCoverage;
            if (def.CaptureRate > 0f && !def.Flying && inf.CanReachObjective) fit = MathF.Max(fit, 1f);
            return Math.Clamp(fit, 0f, 1f);
        }

        /// <summary>Section 208: delivery, then travel to where it matters (to its firing region when it fights from range).</summary>
        private static float TimingFit(VehicleDef def, InfluenceResult inf)
        {
            var reference = MathF.Max(1f, SimTunables.Ai.Procurement.TimingRefSeconds);
            var travel = float.IsPositiveInfinity(inf.TravelSeconds) ? reference : inf.TravelSeconds;
            var toValue = def.DropDelay + travel;
            return 1f - Math.Clamp(toValue / reference, 0f, 1f);
        }

        private float SurvivabilityFit(VehicleDef def)
        {
            float s;
            if (def.Flying) s = 1f - _ema[(int)Threat.AntiAir];
            else if (def.Armor == ArmorClass.Heavy) s = 1f - global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.SurvivabilityFitEmaScale * _ema[(int)Threat.AntiTank] - global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.SurvivabilityFitEmaScale2 * _ema[(int)Threat.Artillery];
            else s = 1f - 0.8f * _ema[(int)Threat.AntiTank] - 0.2f * _ema[(int)Threat.Artillery];
            return Math.Clamp(s, 0f, 1f);
        }

        private float Synergy(VehicleDef def)
        {
            if (def.RepairAura != null || def.RearmAura != null || def.AirRearm != null || def.CommandAura != null || def.Dome != null)
                return Math.Clamp(_fielded.Count / global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.SynergyCountDivisor, 0f, 1f);
            // An army with its support (repairs, ammunition, a commander) gets more out of each fighter.
            var support = _have[(int)ProcurementRole.Engineer] + _have[(int)ProcurementRole.ElectronicWarfare];
            return support > 0f ? 0.6f : 0.4f;
        }

        private static float TacticPreference(VehicleDef def, TeamEconomy economy, AiCommander? commander)
        {
            if (commander != null)
                foreach (var p in commander.CurrentTactic.Prefer)
                    if (p == def.Id || p == def.EliteOf) return 1f;
            return economy.Commander is { } c ? Math.Clamp(CommanderRules.Fit(c, def) * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.TacticPreferenceFitScale, 0f, 1f) : 0f;
        }

        /// <summary>Section 17: crowding (ground army against the cap) x footprint x how much the route depends on a choke.</summary>
        private float Congestion(SimWorld world, TeamEconomy economy, VehicleDef def)
        {
            var domain = MapTopology.DomainOf(def);
            if (domain is not (MobilityDomain.Ground or MobilityDomain.Amphibious)) return 0f;
            var density = Math.Clamp(_ownGround / MathF.Max(1f, economy.VehicleCap), 0f, 1f);
            var footprint = Math.Clamp(def.Radius / global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.CongestionRadiusDivisor, 0f, 1f);
            var dependency = ChokeDependency(world, def);
            return density * footprint * dependency * SimTunables.Ai.Procurement.CongestionMax;
        }

        private int _chokeSource = int.MinValue, _chokeTarget = int.MinValue, _chokeGeneration = -1;
        private float _chokeWidth = float.PositiveInfinity;

        /// <summary>1 when the route from the drop zone to the first objective runs through a passage no wider than a choke, falling to 0 at twice that.</summary>
        private float ChokeDependency(SimWorld world, VehicleDef def)
        {
            if (Context == null) return 0f;
            var topo = world.Topology;
            Vector2? to = null;
            foreach (var t in Context.Targets)
                if (t.Objective && t.Layer == TargetLayer.Ground)
                {
                    to = t.Centre;
                    break;
                }
            if (to == null) return 0f;
            var rings = SimTunables.Ai.Topology.NearestRings;
            var source = topo.Ground.NearestPassableCell(Context.DeployAt, rings);
            var target = topo.Ground.NearestPassableCell(to.Value, rings);
            if (source != _chokeSource || target != _chokeTarget || topo.Generation != _chokeGeneration)
            {
                _chokeSource = source;
                _chokeTarget = target;
                _chokeGeneration = topo.Generation;
                _chokeWidth = topo.Bottleneck(source, target);
            }
            if (float.IsPositiveInfinity(_chokeWidth)) return 0f;
            var choke = SimTunables.Ai.Topology.ChokeWidth;
            var spare = _chokeWidth - def.Radius * 2f;
            return Math.Clamp(1f - (spare - choke * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ChokeDependencyChokeScale) / MathF.Max(1f, choke * global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ChokeDependencyChokeScale2), 0f, 1f);
        }

        // ------------------------------------------------------------------------------------------------ plans and reserve

        /// <summary>The confirmed counter needs as bits (a plan made for one set is cancelled when it changes).</summary>
        public int Signature(double now)
        {
            var bits = 0;
            for (var t = 0; t < Threats; t++)
                if (Confirmed((Threat)t, now)) bits |= 1 << t;
            return bits;
        }

        /// <summary>
        /// Section 16: a plan from the scored cards (best first): the best, then the next best of other roles, up to the
        /// difficulty's size (3-5). Its purpose names what it is for.
        /// </summary>
        public PurchasePlan MakePlan(SimWorld world, TeamEconomy economy, IReadOnlyList<(string id, float score)> ranked, AiDifficulty difficulty)
        {
            var size = Math.Clamp(difficulty switch { AiDifficulty.Easy => global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.MakePlanDifficultyValue, AiDifficulty.Normal => global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.MakePlanDifficultyValue2, _ => global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.MakePlanDifficultyValue3 },
                SimTunables.Ai.Procurement.MinPlanCards, Math.Max(SimTunables.Ai.Procurement.MinPlanCards, SimTunables.Ai.Procurement.MaxPlanCards));
            var cards = new List<string>();
            var cp = 0;
            var power = 0f;
            var usedRoles = new bool[Roles];
            var roles = new float[Roles];
            // First pass: different roles; second: the best again where roles ran out.
            for (var pass = 0; pass < global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.MakePlanPassMax && cards.Count < size; pass++)
                foreach (var (id, _) in ranked)
                {
                    if (cards.Count >= size) break;
                    if (!world.Catalog.Vehicles.TryGetValue(id, out var def)) continue;
                    var primary = PrimaryRole(def, roles);
                    if (pass == 0 && (cards.Contains(id) || (primary >= 0 && usedRoles[primary] && cards.Count > 0))) continue;
                    if (pass == 1 && cards.Count > 0 && Count(cards, id) >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.MakePlanCountMin) continue;
                    cards.Add(id);
                    if (primary >= 0) usedRoles[primary] = true;
                    cp += (int)MathF.Round(economy.PriceOf(id, def.CpCost));
                    power += def.Power;
                }
            var purpose = Purpose(world, cards);
            Plan = new PurchasePlan(cards, purpose, power, cp, world.Time, Signature(world.Time));
            world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Purchase, $"PLAN {Plan}"));
            return Plan;

            static int Count(List<string> list, string id)
            {
                var n = 0;
                foreach (var x in list)
                    if (x == id) n++;
                return n;
            }
        }

        private string Purpose(SimWorld world, List<string> cards)
        {
            var now = world.Time;
            if (Confirmed(Threat.Naval, now) || _ema[(int)Threat.Naval] > global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.PurposeEmaMin) return "shore denial";
            if (Confirmed(Threat.Air, now)) return "air defence";
            if (Confirmed(Threat.HeavyArmour, now)) return "anti-armour";
            if (Confirmed(Threat.Artillery, now)) return "counter-battery";
            if (cards.Count > 0 && world.Catalog.Vehicles.TryGetValue(cards[0], out var first) && first.CaptureRate > 0f && Context != null)
                foreach (var t in Context.Targets)
                    if (t.Capture) return "objective capture";
            return "frontline";
        }

        /// <summary>Whether the plan still stands: not expired, the same confirmed needs, every card still feasible.</summary>
        public bool PlanValid(SimWorld world)
        {
            if (Plan == null || Plan.Done) return false;
            var now = world.Time;
            string? why = null;
            if (now - Plan.Created > SimTunables.Ai.Procurement.PlanExpireSeconds) why = "expired";
            else if (Signature(now) != Plan.Signature) why = "intel-changed";
            if (why == null) return true;
            CancelPlan(world, why);
            return false;
        }

        public void CancelPlan(SimWorld world, string why)
        {
            if (Plan == null) return;
            if (!Plan.Done) world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Purchase, $"PLAN cancel {Plan.Purpose} reason={why}"));
            Plan = null;
        }

        /// <summary>Logs a purchase (BUY card score plan factors) and moves the plan on when it was the plan's card.</summary>
        public void Bought(SimWorld world, string id, float score, List<Factor>? factors)
        {
            var plan = Plan;
            if (plan != null && !plan.Done && plan.Cards[plan.Next] == id) plan.Next++;
            _reserveSince = double.NaN;
            var (plus, minus) = factors != null ? Why.Split(factors) : (Array.Empty<Factor>(), Array.Empty<Factor>());
            world.AiLog.Add(new DecisionEntry(world.Time, _team, AiLayer.Commander, 0, DecisionKind.Purchase,
                $"BUY {id} score={score:0.00}{(plan != null ? $" plan={plan.Purpose} {plan.Next}/{plan.Cards.Count}" : "")} ({string.Join("; ", plus)}; {string.Join("; ", minus)})"));
            if (plan != null && plan.Done) Plan = null;
        }

        /// <summary>Skips the plan's next card (illegal now: a cap, a limit) without buying it.</summary>
        public void Skip()
        {
            if (Plan != null && !Plan.Done) Plan.Next++;
            if (Plan != null && Plan.Done) Plan = null;
        }

        /// <summary>
        /// Section 18: keep CP back for an important counter that is almost affordable (a confirmed need the card to buy now
        /// does not answer), never past the bank cap, with a thin army, or longer than <c>reserveMaxSeconds</c>.
        /// </summary>
        public bool Reserve(SimWorld world, TeamEconomy economy, VehicleDef toBuy, VehicleDef? counter, bool thin, bool underFire)
        {
            var now = world.Time;
            if (counter == null || thin || underFire || economy.Cp >= economy.Bank - global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.ReserveBankSub || counter.Id == toBuy.Id) return Release();
            var price = economy.PriceOf(counter.Id, counter.CpCost);
            if (price <= economy.Cp) return Release();
            if (economy.Cp + economy.Income * SimTunables.Ai.Procurement.ReserveHorizonSeconds < price) return Release();
            for (var t = 0; t < Threats; t++)
                if (Confirmed((Threat)t, now) && Answers(counter, (Threat)t) && Answers(toBuy, (Threat)t)) return Release();
            if (double.IsNaN(_reserveSince))
            {
                _reserveSince = now;
                world.AiLog.Add(new DecisionEntry(now, _team, AiLayer.Commander, 0, DecisionKind.Purchase, $"RESERVE {price:0} CP for {counter.Id} reason=counter"));
            }
            return now - _reserveSince < SimTunables.Ai.Procurement.ReserveMaxSeconds;

            bool Release()
            {
                _reserveSince = double.NaN;
                return false;
            }
        }

        /// <summary>Whether a card answers a confirmed need (any threat confirmed now).</summary>
        public bool AnswersConfirmed(VehicleDef def, double now)
        {
            for (var t = 0; t < Threats; t++)
                if (t != (int)Threat.AntiAir && t != (int)Threat.AntiTank && Confirmed((Threat)t, now) && Answers(def, (Threat)t)) return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------ roles

        /// <summary>Section 13: the roles a vehicle fills, weighted (a battle tank is front line and some anti-tank).</summary>
        public static void RolesOf(VehicleDef def, float[] roles)
        {
            Array.Clear(roles, 0, roles.Length);
            void Add(ProcurementRole r, float w) => roles[(int)r] = MathF.Max(roles[(int)r], w);
            var airGun = EngagementFeasibility.CanHit(def, TargetLayer.Air);
            if (def.Flying)
            {
                Add(ProcurementRole.AirCover, 1f);
                if (def.Drone) Add(ProcurementRole.Drone, 1f);
                if (KillsArmour(def)) Add(ProcurementRole.AntiTank, global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfW);
                return;
            }
            switch (def.Class)
            {
                case UnitClass.Tank:
                case UnitClass.Heavy:
                    Add(ProcurementRole.Frontline, 1f);
                    if (KillsArmour(def)) Add(ProcurementRole.AntiTank, global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfW);
                    break;
                case UnitClass.TankHunter:
                    Add(ProcurementRole.AntiTank, 1f);
                    break;
                case UnitClass.Artillery:
                    Add(ProcurementRole.Artillery, 1f);
                    break;
                case UnitClass.AntiAir:
                    Add(ProcurementRole.AntiAir, 1f);
                    break;
                case UnitClass.Scout:
                    Add(ProcurementRole.Recon, 1f);
                    Add(ProcurementRole.FastFlank, 0.5f);
                    break;
                case UnitClass.Light:
                    Add(ProcurementRole.FastFlank, 1f);
                    if (def.VisionRange >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfVisionRangeMin) Add(ProcurementRole.Recon, global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfW);
                    break;
                case UnitClass.Support:
                    if (def.RepairAura != null || def.RearmAura != null || def.AirRearm != null || def.Breacher) Add(ProcurementRole.Engineer, 1f);
                    if (def.Jammer > 0f || def.CounterBattery != null || def.Dome != null || def.CommandAura != null) Add(ProcurementRole.ElectronicWarfare, 1f);
                    if (roles[(int)ProcurementRole.Engineer] <= 0f && roles[(int)ProcurementRole.ElectronicWarfare] <= 0f) Add(ProcurementRole.Engineer, 0.5f);
                    break;
                default:
                    Add(ProcurementRole.Frontline, 0.5f);
                    break;
            }
            if (def.Weapon.MinRange > 0f) Add(ProcurementRole.Artillery, 1f);
            if (airGun && def.Class != UnitClass.AntiAir) Add(ProcurementRole.AntiAir, 0.3f);
            if (def.Breacher) Add(ProcurementRole.Siege, 1f);
            if (Catalog.FliesDrones(def)) Add(ProcurementRole.Drone, 1f);
            // Anything that reaches ships from the shore (a long gun, a missile) screens the coast.
            if (WeaponEnvelope.Of(def, TargetLayer.Naval).MaxRange >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfMaxRangeMin) Add(ProcurementRole.NavalStrike, global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.RolesOfW);
        }

        private static int PrimaryRole(VehicleDef def, float[] roles)
        {
            RolesOf(def, roles);
            var best = -1;
            var w = 0f;
            for (var r = 0; r < roles.Length; r++)
                if (roles[r] > w)
                {
                    w = roles[r];
                    best = r;
                }
            return best;
        }

        /// <summary>Whether a vehicle answers a kind of threat (section 14).</summary>
        public static bool Answers(VehicleDef def, Threat t) => t switch
        {
            Threat.Air => EngagementFeasibility.CanHit(def, TargetLayer.Air),
            Threat.HeavyArmour => KillsArmour(def),
            Threat.Light => EngagementFeasibility.CanHit(def, TargetLayer.Ground) && def.Weapon.MinRange <= 0f,
            Threat.Artillery => def.Flying || def.Speed >= global::MachineBrigade.Sim.Content.SimTunables.Ai.ProcurementDirector.AnswersSpeedMin || def.CounterBattery != null || def.Weapon.MinRange > 0f,
            Threat.Drones => EngagementFeasibility.CanHit(def, TargetLayer.Air) || def.Microwave != null || def.DroneHunt != null,
            Threat.Naval => EngagementFeasibility.CanHit(def, TargetLayer.Naval),
            _ => false,
        };

        private static bool KillsArmour(VehicleDef def)
        {
            foreach (var m in def.Mounts)
                if (m.Weapon.AntiArmour && m.Weapon.CanTarget(false)) return true;
            return false;
        }
    }
}

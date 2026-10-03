#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Modes
{
    /// <summary>Prompt 32 L4: a side's HQ type in the battle (see <see cref="HqTypeRules"/>).</summary>
    public sealed class HqState
    {
        /// <summary>Set up with a base that has an HQ (or a fortress's command HQ); false: no type in play.</summary>
        public bool Ready { get; internal set; }

        public HqType Type { get; internal set; }
        public HqBranch Branch { get; internal set; }

        /// <summary>Play-test 14: the light unit the Garrison calls (null: the level's mixed squad).</summary>
        public string? Unit { get; internal set; }
        public int Level { get; internal set; } = 1;

        /// <summary>Match time the skill is ready again.</summary>
        public double SkillReadyAt { get; internal set; }

        /// <summary>The Garrison's squads stocked (ready to turn out), and when the next one is stocked (infinite: the stock is full).</summary>
        public int Stock { get; internal set; }

        internal double NextStockAt = double.PositiveInfinity;

        /// <summary>The garrison's vehicles in the field (pruned as they fall).</summary>
        internal readonly List<EntityId> Garrison = new();

        /// <summary>Since when the base region has been clear of enemies (NaN: enemies in it).</summary>
        internal double ClearSince = double.NaN;

        /// <summary>The HQ's damage marks given (50 %: a warning only; 25 %: a warning and the free rebuild).</summary>
        public bool Half { get; internal set; }
        public bool Quarter { get; internal set; }

        /// <summary>The Shield's emergency dome: what it can still absorb, and until when it stands.</summary>
        public float DomeHp { get; internal set; }
        public float DomeFull { get; internal set; }
        public double DomeUntil { get; internal set; } = double.NegativeInfinity;

        /// <summary>Enemy CP (base price) inside the base region at the last look, and the dearest intruder (none: invalid).</summary>
        public float Threat { get; internal set; }
        internal EntityId Intruder;
        internal double NextLook;
        internal double LastStep = double.NaN;

        public bool DomeUp(double now) => DomeHp > 0f && now < DomeUntil;

        public float SkillLeft(double now) => (float)Math.Max(0.0, SkillReadyAt - now);
    }

    public sealed partial class BaseSystem
    {
        /// <summary>Seconds between the HQ's looks round its region (threat, garrison leash).</summary>
        private static double LookEvery => global::MachineBrigade.Sim.Content.SimTunables.Bases.BaseSystem.LookEvery;

        /// <summary>
        /// Prompt 32 L4: the sides whose HQ skill the AI uses (when its base is threatened past the mode profile's
        /// <see cref="AiModeProfile.HqSkillThreat"/>). Default: every side but the player's (team 0); the menu's battle sets both.
        /// </summary>
        public Func<int, bool> AutoSkill { get; set; } = team => team != 0;

        /// <summary>The HQ def a loadout's type stands as (the plain HQ where the data has no def for it).</summary>
        private string HqDefOf(BaseLoadout loadout)
        {
            var catalog = _world.Catalog;
            var id = catalog.Base.HqTypes.HqDef(loadout.HqType, loadout.HqBranch);
            return id != null && catalog.Vehicles.ContainsKey(id) ? id : catalog.Base.HqId;
        }

        /// <summary>The HQ type's state as the base is set up: the Fortress gun's and the Shield dome's scale by HQ level.</summary>
        private void SetUpHq(TeamBase b)
        {
            var rules = _world.Catalog.Base.HqTypes;
            var s = b.Hq32;
            s.Ready = true;
            s.Type = b.Loadout.HqType;
            s.Branch = b.Loadout.HqBranch;
            s.Unit = b.Loadout.HqUnit;
            s.Level = Math.Clamp(b.Loadout.HqLevel, 1, 5);
            s.SkillReadyAt = _world.Time;
            s.Stock = 0;
            s.NextStockAt = s.Type == HqType.Garrison ? _world.Time + rules.GarrisonEvery(s.Level) : double.PositiveInfinity;
            if (!b.Hq.IsValid || !_world.TryGetVehicle(b.Hq, out var hq)) return;
            if (s.Type == HqType.Fortress && _world.Catalog.Vehicles.TryGetValue(_world.Catalog.Base.HqId, out var plain))
            {
                // The mounts past the plain HQ's are the type's gun: damage and cadence each the root of the level's scale.
                var k = MathF.Sqrt(rules.FortressScale(s.Level, s.Branch));
                for (var i = plain.Mounts.Count; i < hq.Weapons.Length; i++)
                {
                    hq.Weapons[i].DamageScale = k;
                    hq.Weapons[i].RateScale = k;
                }
            }
            if (s.Type == HqType.Shield && hq.Aps != null)
            {
                var k = rules.ShieldScale(s.Level);
                hq.ApsMax = Math.Clamp((int)MathF.Round(rules.ShieldCharges * k), 1, hq.Aps.Charges);
                hq.ApsCharges = Math.Min(hq.ApsCharges, hq.ApsMax);
                hq.ApsRate = k;
            }
        }

        /// <summary>One step of a base's HQ type: the damage marks, the garrison, the Shield's repairs, the AI's skill.</summary>
        private void StepHq(TeamBase b)
        {
            var s = b.Hq32;
            if (!s.Ready || b.HqFallen) return;
            var now = _world.Time;
            var dt = double.IsNaN(s.LastStep) ? 0f : (float)(now - s.LastStep);
            s.LastStep = now;
            var rules = _world.Catalog.Base.HqTypes;
            Vehicle? hq = b.Hq.IsValid && _world.TryGetVehicle(b.Hq, out var h) && h.IsAlive ? h : null;
            if (hq != null) Marks(b, s, hq);
            if (now >= s.NextLook)
            {
                s.NextLook = now + LookEvery;
                Look(b, s, rules);
                if (s.Type == HqType.Garrison) Garrison(b, s, rules, now);
                if (s.Type != HqType.None && AutoSkill(b.Team) && now >= s.SkillReadyAt && s.Threat > 0f && s.Threat >= _world.AiProfile.HqSkillThreat) AiSkill(b, s);
            }
            if (s.Type == HqType.Shield && dt > 0f) Mend(b, s, rules, now, dt);
            if (s.DomeHp > 0f && now >= s.DomeUntil) s.DomeHp = 0f;
        }

        /// <summary>The HQ's damage marks: at half health a warning (the model's smoke is the view's), at a quarter another (the free rebuild is <see cref="HqRescue"/>).</summary>
        private void Marks(TeamBase b, HqState s, Vehicle hq)
        {
            var share = hq.Hp / MathF.Max(1f, hq.MaxHp);
            var ours = b.Team == 0;
            if (!s.Half && share <= 0.5f)
            {
                s.Half = true;
                _world.Emit(SimEvent.Alert(b.HqPosition, ours ? "alert.hq.half.ours" : "alert.hq.half.theirs", bad: ours));
            }
            if (!s.Quarter && share <= _world.Catalog.Base.HqRescueShare)
            {
                s.Quarter = true;
                _world.Emit(SimEvent.Alert(b.HqPosition, ours ? "alert.hq.quarter.ours" : "alert.hq.quarter.theirs", bad: ours));
            }
        }

        /// <summary>The enemy CP inside the base region and its dearest vehicle (ties by id).</summary>
        private void Look(TeamBase b, HqState s, HqTypeRules rules)
        {
            var r2 = rules.Radius * rules.Radius;
            var threat = 0f;
            Vehicle? best = null;
            foreach (var v in _world.VehicleList)
            {
                if (!v.IsAlive || v.Team == b.Team || v.Team < 0 || v.Def.Static) continue;
                if (Vector2.DistanceSquared(v.Position, b.HqPosition) > r2) continue;
                threat += v.Def.BaseCp;
                if (best == null || v.Def.BaseCp > best.Def.BaseCp || (v.Def.BaseCp == best.Def.BaseCp && v.Id.Value < best.Id.Value)) best = v;
            }
            s.Threat = threat;
            s.Intruder = best?.Id ?? EntityId.None;
        }

        // ------------------------------------------------------------------ Garrison

        private void Garrison(TeamBase b, HqState s, HqTypeRules rules, double now)
        {
            // Stock one squad every interval while the stock is not full.
            if (s.Stock < rules.GarrisonStock && double.IsPositiveInfinity(s.NextStockAt)) s.NextStockAt = now + rules.GarrisonEvery(s.Level);
            if (s.Stock < rules.GarrisonStock && now >= s.NextStockAt)
            {
                s.Stock++;
                s.NextStockAt = s.Stock < rules.GarrisonStock ? now + rules.GarrisonEvery(s.Level) : double.PositiveInfinity;
            }
            s.Garrison.RemoveAll(id => !_world.TryGetVehicle(id, out var g) || !g.IsAlive);
            var intruder = _world.TryGetVehicle(s.Intruder, out var e) && e.IsAlive ? e : null;
            if (intruder != null)
            {
                s.ClearSince = double.NaN;
                // An enemy in the base: a stocked squad turns out (one per look, while the cap has room).
                if (s.Stock > 0 && TurnOut(b, s, rules, intruder.Position)) s.Stock--;
            }
            else if (double.IsNaN(s.ClearSince)) s.ClearSince = now;
            // The garrison keeps to the base: its post is the HQ's side facing the intruder; past the region it is called back.
            var post = intruder != null ? Toward(b.HqPosition, intruder.Position, MathF.Min(rules.Radius * 0.5f, Vector2.Distance(b.HqPosition, intruder.Position))) : b.HqPosition;
            foreach (var id in s.Garrison)
            {
                if (!_world.TryGetVehicle(id, out var g)) continue;
                g.GuardPoint = _world.ClampToMap(post);
                g.PostRadius = rules.Radius;
                if (Vector2.Distance(g.Position, b.HqPosition) > rules.Radius + 5f && g.Order.Kind != OrderKind.Idle)
                {
                    g.SetOrder(Order.Idle);
                    g.ClearPath();
                    _world.PathTo(g, g.GuardPoint);
                }
            }
            // The base clear long enough: the garrison goes back in (no wreck, no kill, nothing paid).
            if (!double.IsNaN(s.ClearSince) && now - s.ClearSince >= rules.GarrisonClear && s.Garrison.Count > 0)
            {
                foreach (var id in s.Garrison)
                    if (_world.TryGetVehicle(id, out var g) && g.IsAlive) g.ExpiresAt = now;
                s.Garrison.Clear();
            }
        }

        /// <summary>A point <paramref name="metres"/> from <paramref name="from"/> towards <paramref name="to"/>.</summary>
        private static Vector2 Toward(Vector2 from, Vector2 to, float metres)
        {
            var d = to - from;
            return d.LengthSquared() > 0.01f ? from + Vector2.Normalize(d) * metres : from;
        }

        /// <summary>The garrison's baseCP alive now.</summary>
        internal float GarrisonCp(HqState s)
        {
            var total = 0f;
            foreach (var id in s.Garrison)
                if (_world.TryGetVehicle(id, out var g) && g.IsAlive) total += g.Def.BaseCp;
            return total;
        }

        /// <summary>
        /// One stocked squad turns out beside the HQ, on the side facing <paramref name="towards"/>, if the garrison's cap
        /// (baseCP alive, by HQ level) and the side's army cap have room; false: it stays in stock.
        /// </summary>
        private bool TurnOut(TeamBase b, HqState s, HqTypeRules rules, Vector2 towards)
        {
            var squad = rules.Squad(s.Level, s.Unit);
            var cost = 0f;
            var ids = new List<VehicleDef>();
            foreach (var id in squad)
                if (_world.Catalog.Vehicles.TryGetValue(id, out var def))
                {
                    ids.Add(def);
                    cost += def.BaseCp;
                }
            if (ids.Count == 0 || GarrisonCp(s) + cost > rules.GarrisonCap(s.Level) + 0.01f) return false;
            if (_world.TryGetEconomy(b.Team, out var economy) && _world.Economy.VehicleCount(b.Team) + ids.Count > economy.VehicleCap) return false;
            var hqRadius = _world.TryGetVehicle(b.Hq, out var hq) ? hq.Def.Radius : 6f;
            var out0 = Toward(b.HqPosition, towards, hqRadius + 6f);
            var dir = towards - b.HqPosition;
            var side = dir.LengthSquared() > 0.01f ? Vector2.Normalize(new Vector2(-dir.Y, dir.X)) : Vector2.UnitX;
            for (var k = 0; k < ids.Count; k++)
            {
                var at = _world.ClampToMap(out0 + side * ((k - (ids.Count - 1) * 0.5f) * 5f));
                var v = _world.SpawnVehicle(ids[k].Id, b.Team, at, SimMath.HeadingOf(dir.LengthSquared() > 0.01f ? dir : Vector2.UnitX));
                v.Garrison = true;
                v.GuardPoint = at;
                v.PostRadius = rules.Radius;
                s.Garrison.Add(v.Id);
            }
            _world.Emit(SimEvent.Alert(b.HqPosition, b.Team == 0 ? "alert.hq.garrison.ours" : "alert.hq.garrison.theirs", bad: b.Team != 0));
            return true;
        }

        // ------------------------------------------------------------------ Shield

        /// <summary>The Shield's repairs: a tower of the base left unhit for the delay mends a share of its health a second.</summary>
        private void Mend(TeamBase b, HqState s, HqTypeRules rules, double now, float dt)
        {
            var rate = rules.Regen(s.Level);
            if (rate <= 0f) return;
            var r2 = rules.Radius * rules.Radius;
            foreach (var slot in b.Slots)
            {
                if (!_world.TryGetVehicle(slot.Structure, out var t) || !t.IsAlive || t.Hp >= t.MaxHp) continue;
                if (now - t.LastHitTime < rules.RegenDelay || Vector2.DistanceSquared(t.Position, b.HqPosition) > r2) continue;
                t.Hp = MathF.Min(t.MaxHp, t.Hp + t.MaxHp * rate * dt);
            }
        }

        /// <summary>The emergency dome covering <paramref name="victim"/> (its side's, standing, round its HQ), or null.</summary>
        internal HqState? SkillDomeOver(Vehicle victim)
        {
            if (_anyDomeUntil <= _world.Time || victim.Flying || !_bases.TryGetValue(victim.Team, out var b)) return null;
            var s = b.Hq32;
            if (!s.DomeUp(_world.Time)) return null;
            var r = _world.Catalog.Base.HqTypes.Radius;
            return Vector2.DistanceSquared(victim.Position, b.HqPosition) <= r * r ? s : null;
        }

        /// <summary>Whether any emergency dome may be up (a quick way out for the damage path).</summary>
        internal bool AnySkillDome => _anyDomeUntil > _world.Time;

        private double _anyDomeUntil = double.NegativeInfinity;

        // ------------------------------------------------------------------ the skill

        /// <summary>
        /// The HQ's one skill (Command.HqSkill), on its shared cooldown: the Fortress's three heavy rounds on Point (the
        /// support cards' rules: on the map, not into the enemy's home zone), the Garrison's alarm (every stocked squad out
        /// now, the caps still holding), the Shield's emergency dome over the base.
        /// </summary>
        public CommandResult UseSkill(Command command)
        {
            if (!_bases.TryGetValue(command.Team, out var b) || !b.Hq32.Ready || b.Hq32.Type == HqType.None || b.HqFallen)
                return CommandResult.Rejected(CommandError.NotAvailable);
            var s = b.Hq32;
            if (_world.Time < s.SkillReadyAt) return CommandResult.Rejected(CommandError.OnCooldown);
            var rules = _world.Catalog.Base.HqTypes;
            switch (s.Type)
            {
                case HqType.Fortress:
                {
                    if (!SimMath.IsFinite(command.Point)) return CommandResult.Rejected(CommandError.InvalidPoint);
                    if (!_world.Map.Contains(command.Point)) return CommandResult.Rejected(CommandError.OutOfBounds);
                    if (_world.InEnemyHome(command.Point, command.Team)) return CommandResult.Rejected(CommandError.InvalidPoint);
                    if (!_world.Catalog.TryGetSupport(rules.Barrage, out var barrage)) return CommandResult.Rejected(CommandError.NotAvailable);
                    _world.Strikes.Launch(barrage, command.Team, command.Point, command.Point);
                    break;
                }
                case HqType.Garrison:
                {
                    var any = false;
                    var towards = _world.TryGetVehicle(s.Intruder, out var e) && e.IsAlive ? e.Position : b.HqPosition + Vector2.UnitX;
                    while (s.Stock > 0 && TurnOut(b, s, rules, towards))
                    {
                        s.Stock--;
                        any = true;
                    }
                    if (!any) return CommandResult.Rejected(s.Stock > 0 ? CommandError.ArmyAtCapacity : CommandError.NotAvailable);
                    s.ClearSince = double.NaN;
                    break;
                }
                case HqType.Shield:
                default:
                {
                    var full = _world.TryGetVehicle(b.Hq, out var hq) && hq.IsAlive ? hq.MaxHp
                        : _world.Catalog.Vehicles.TryGetValue(_world.Catalog.Base.HqId, out var plain) ? plain.MaxHp : 0f;
                    s.DomeFull = s.DomeHp = full * rules.Dome(s.Level);
                    s.DomeUntil = _world.Time + rules.DomeSeconds;
                    _anyDomeUntil = Math.Max(_anyDomeUntil, s.DomeUntil);
                    _world.Emit(SimEvent.Alert(b.HqPosition, b.Team == 0 ? "alert.hq.dome.ours" : "alert.hq.dome.theirs", bad: b.Team != 0));
                    break;
                }
            }
            s.SkillReadyAt = _world.Time + rules.SkillCooldown;
            return CommandResult.Ok;
        }

        /// <summary>The AI's skill when its base is threatened: the barrage on the dearest intruder, else the type's own.</summary>
        private void AiSkill(TeamBase b, HqState s)
        {
            if (s.Type == HqType.Garrison && s.Stock == 0) return;
            var at = _world.TryGetVehicle(s.Intruder, out var e) && e.IsAlive ? e.Position : b.HqPosition;
            if (s.Type == HqType.Fortress && !s.Intruder.IsValid) return;
            UseSkill(Command.HqSkill(b.Team, at));
        }

        /// <summary>The Fortress barrage's damage on a side's strike (its HQ level's scale); 1 for every other support.</summary>
        internal float SkillStrikeScale(int team, string supportId)
        {
            if (!_bases.TryGetValue(team, out var b) || !b.Hq32.Ready) return 1f;
            var rules = _world.Catalog.Base.HqTypes;
            return supportId == rules.Barrage ? rules.FortressScale(b.Hq32.Level, b.Hq32.Branch) : 1f;
        }

        /// <summary>The HQ types' state in the battle's fingerprint (sides in team order).</summary>
        internal void Mix(Action<long> mix)
        {
            for (var team = 0; team <= 2; team++)
            {
                if (!_bases.TryGetValue(team, out var b) || !b.Hq32.Ready) continue;
                var s = b.Hq32;
                mix((long)s.Type * 8 + s.Stock);
                mix((long)Math.Round(s.SkillReadyAt * 10.0));
                mix((long)MathF.Round(s.DomeHp));
                mix(s.Garrison.Count);
            }
        }
    }
}

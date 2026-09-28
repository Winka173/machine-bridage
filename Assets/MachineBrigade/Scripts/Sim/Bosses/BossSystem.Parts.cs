#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim.Bosses
{
    /// <summary>
    /// Boss parts, the general rules (prompts 8 and 9): every boss is a body and parts, each part
    /// with its own health (a share of the body's), where it sits, and the weapon mounts, skills and
    /// mechanisms it drives.
    /// <list type="bullet">
    /// <item>Only a round that strikes a part hurts it: blasts, fire, strikes and pierces land on
    /// the body, so artillery gets no multiplied damage out of a boss.</item>
    /// <item>The body always takes damage; only a lock (<see cref="PartLockDef"/>, the command
    /// airship's engines) shuts it until enough parts of a kind are broken.</item>
    /// <item>A broken part's mounts fall silent, its skills stop once every part that carries them is
    /// broken, its mechanisms stop, its penalties apply, and the body takes 30 % of the part's full
    /// health.</item>
    /// <item>A self-repair (<see cref="SkillKind.Patch"/>) puts one broken part back at half health:
    /// the one with the strongest weapons, each part at most once.</item>
    /// <item>Aim: a shooter goes for the live part most dangerous to it that it can reach (anti-air for
    /// the parts that shoot at aircraft, tank hunters for the toughest), and about two rounds in five
    /// at the body. The player's order (<see cref="CommandType.FocusPart"/>) sends every round of the
    /// side's units in reach at one part until it breaks or the order is cancelled.</item>
    /// </list>
    /// </summary>
    internal sealed partial class BossSystem
    {
        /// <summary>The share of rounds at an unlocked boss that go at its body rather than a part.</summary>
        internal const double BodyShare = 0.4;

        /// <summary>Each side's part order: which boss and which of its parts.</summary>
        private readonly Dictionary<int, (EntityId boss, int part)> _focus = new();

        // ================================================================== aiming

        /// <summary>
        /// Which part of a boss a shooter aims at (-1: the body). The side's part order first; while
        /// the body is locked, the parts that unlock it, nearest first; else the part most dangerous to
        /// it within reach, and two rounds in five the body.
        /// </summary>
        public int ChoosePart(Vehicle shooter, Vehicle boss, WeaponDef weapon)
        {
            if (!boss.HasParts) return -1;
            var parts = boss.Def.Parts;
            var focus = FocusOf(shooter.Team, boss.Id);
            if (focus >= 0 && Reaches(shooter, boss, focus, weapon)) return focus;
            var locked = boss.BodyLocked;
            var best = -1;
            var bestScore = float.MinValue;
            for (var i = 0; i < parts.Count; i++)
            {
                if (boss.PartBroken[i] || !Reaches(shooter, boss, i, weapon)) continue;
                var distance = Vector2.Distance(boss.PartPosition(i), shooter.Position);
                float score;
                if (locked) score = parts[i].Kind == boss.Def.PartLock!.Kind ? 1000f - distance : -500f - distance;
                else score = Danger(shooter, boss, i) - distance * 0.01f;
                if (score <= bestScore) continue;
                bestScore = score;
                best = i;
            }
            if (locked || best < 0) return best;
            // The body stays a main target: two rounds in five go at it.
            return _world.Random.NextDouble() < BodyShare ? -1 : best;
        }

        /// <summary>Whether a round from this weapon can reach part <paramref name="i"/> (a blade or a short gun only the parts it is beside).</summary>
        private static bool Reaches(Vehicle shooter, Vehicle boss, int i, WeaponDef weapon) =>
            !boss.PartBroken[i] && Vector2.Distance(boss.PartPosition(i), shooter.Position) <= weapon.Range + boss.Def.Parts[i].Radius + 1f;

        /// <summary>
        /// How much a shooter wants part <paramref name="i"/>: anti-air the part that fires at aircraft
        /// (it is shielding its own), a tank hunter the toughest part, everyone else the part whose guns
        /// hurt it most; a part with nothing aimed at the shooter still counts a little for its
        /// firepower, and one that drives a mechanism or skill (a drill, a shield) a little more.
        /// </summary>
        private float Danger(Vehicle shooter, Vehicle boss, int i)
        {
            var part = boss.Def.Parts[i];
            if (shooter.Def.Class == UnitClass.TankHunter) return boss.PartHealth(i) / MathF.Max(1f, boss.MaxHp) * 100f;
            var antiAir = shooter.Def.Class == UnitClass.AntiAir || CombatSystem.IsAntiAir(shooter.Weapon);
            var reach = Vector2.Distance(boss.Position, shooter.Position);
            var toShooter = 0f;
            var toAir = 0f;
            var all = 0f;
            foreach (var m in part.Mounts)
            {
                var w = boss.Arms[m];
                if (w.Damage <= 0f) continue;
                var dps = Firepower(w);
                all += dps;
                if (w.CanTarget(true)) toAir += dps;
                if (w.CanTarget(shooter.Flying) && reach <= w.Range + boss.Radius)
                    toShooter += dps * _world.Catalog.Damage.Multiplier(w.DamageType, shooter.Armor);
            }
            var score = (antiAir ? toAir : toShooter) + all * 0.15f;
            if (part.Skills.Count > 0 || part.Stops.Count > 0) score += 8f;
            return score;
        }

        /// <summary>
        /// How heavy a weapon is against ground vehicles, the boss's main enemy: the damage of one of
        /// its rounds against the armour it suits better (a main gun's shell before a rocket's or a
        /// flak burst's, whatever their rate).
        /// </summary>
        private float GroundFirepower(WeaponDef w) =>
            w.CanTarget(false) ? w.Damage * MathF.Max(_world.Catalog.Damage.Multiplier(w.DamageType, ArmorClass.Light),
                _world.Catalog.Damage.Multiplier(w.DamageType, ArmorClass.Heavy)) : 0f;

        /// <summary>A weapon's damage a second on paper (its volley over its cycle).</summary>
        internal static float Firepower(WeaponDef w) =>
            w.Damage * Math.Max(1, w.Burst) / MathF.Max(0.1f, w.Cooldown + (Math.Max(1, w.Burst) - 1) * w.BurstInterval);

        // ================================================================== the part order

        /// <summary>The player's (or any side's) part order: every unit of the side in reach aims at that part.</summary>
        public CommandResult Focus(Command command)
        {
            // Cancelled.
            if (string.IsNullOrEmpty(command.DefId))
            {
                _focus.Remove(command.Team);
                return CommandResult.Ok;
            }
            if (!_world.TryGetVehicle(command.Target, out var boss) || !boss.IsAlive || !boss.HasParts || boss.Team == command.Team)
                return CommandResult.Rejected(CommandError.InvalidTarget);
            var index = boss.Def.PartIndex(command.DefId!);
            if (index < 0 || boss.PartBroken[index]) return CommandResult.Rejected(CommandError.InvalidTarget);
            _focus[command.Team] = (boss.Id, index);
            return CommandResult.Ok;
        }

        /// <summary>The part of <paramref name="boss"/> the side has ordered its units at, or -1.</summary>
        public int FocusOf(int team, EntityId boss)
        {
            if (!_focus.TryGetValue(team, out var f) || f.boss != boss) return -1;
            return _world.TryGetVehicle(boss, out var b) && b.IsAlive && !b.IsPartBroken(f.part) ? f.part : -1;
        }

        /// <summary>The side's part order (the boss and the part), if it has one standing.</summary>
        public bool TryGetFocus(int team, out EntityId boss, out int part)
        {
            boss = EntityId.None;
            part = -1;
            if (!_focus.TryGetValue(team, out var f)) return false;
            part = FocusOf(team, f.boss);
            boss = f.boss;
            return part >= 0;
        }

        /// <summary>The side has ordered its units at a part of this boss (they pick it as their target first).</summary>
        public bool IsFocused(int team, EntityId boss) => FocusOf(team, boss) >= 0;

        /// <summary>The part orders into the battle's fingerprint.</summary>
        internal void Mix(Action<long> mix)
        {
            for (var team = 0; team <= 2; team++)
                if (_focus.TryGetValue(team, out var f) && FocusOf(team, f.boss) >= 0) mix(f.boss.Value * 64 + f.part);
        }

        // ================================================================== damage, breaking, patching

        /// <summary>Takes <paramref name="damage"/> off a part (already through the damage rules); returns what it lost, and breaks it at zero.</summary>
        public float DamagePart(Vehicle boss, int i, float damage, in HitInfo hit)
        {
            if (i < 0 || i >= boss.PartFrac.Length || boss.PartBroken[i] || !(damage > 0f)) return 0f;
            var full = boss.PartFullHealth(i);
            if (!(full > 0f)) return 0f;
            var lost = MathF.Min(boss.PartFrac[i] * full, damage);
            boss.PartFrac[i] -= lost / full;
            if (boss.PartFrac[i] * full <= 0.01f) Break(boss, i, hit);
            return lost;
        }

        /// <summary>A part breaks: its guns fall silent, its skills and mechanisms stop, its penalties apply, and the body takes its share.</summary>
        public void Break(Vehicle boss, int i, in HitInfo hit = default)
        {
            if (boss.PartBroken[i]) return;
            var part = boss.Def.Parts[i];
            boss.PartBroken[i] = true;
            boss.PartFrac[i] = 0f;
            foreach (var m in part.Mounts)
            {
                boss.Weapons[m].Target = EntityId.None;
                boss.Weapons[m].BurstLeft = 0;
            }
            Recompute(boss);
            var at = boss.PartPosition(i);
            _world.Emit(SimEvent.PartLost(boss, i, at, part.Id));
            _world.Emit(SimEvent.Exploded(at, new ExplosionDef(0f, MathF.Max(3f, part.Radius * 1.4f), 0f, ExplosionTier.Huge), boss.Id));
            // The body takes 30 % of the part's full health (none on the airship: its hull has the lock).
            if (part.BreakDamage > 0f && boss.IsAlive)
                _world.Damage.Apply(boss, boss.PartFullHealth(i) * part.BreakDamage, DamageType.HighExplosive,
                    new HitInfo(hit.Attacker, hit.Team, null, at, HitKind.Redirect, false));
        }

        /// <summary>A self-repair has something to do: a broken part not yet patched.</summary>
        public bool CanPatch(Vehicle boss)
        {
            for (var i = 0; i < boss.PartBroken.Length; i++)
                if (boss.PartBroken[i] && !boss.PartPatched[i]) return true;
            return false;
        }

        /// <summary>
        /// A self-repair: the broken part with the strongest weapons (the heaviest rounds against
        /// ground vehicles, the boss's main enemy: a main gun before a flak mount; then one that drives a
        /// skill or a mechanism, then the first) comes back at <paramref name="share"/> of its health,
        /// its guns and skills with it. Each part is patched at most once. Returns the part, or -1.
        /// </summary>
        public int Patch(Vehicle boss, float share)
        {
            var best = -1;
            var bestScore = -1f;
            for (var i = 0; i < boss.PartBroken.Length; i++)
            {
                if (!boss.PartBroken[i] || boss.PartPatched[i]) continue;
                var part = boss.Def.Parts[i];
                var score = 0f;
                foreach (var m in part.Mounts) score += GroundFirepower(boss.Arms[m]);
                if (part.Skills.Count > 0 || part.Stops.Count > 0) score += 0.5f;
                if (score <= bestScore) continue;
                bestScore = score;
                best = i;
            }
            if (best < 0) return -1;
            boss.PartBroken[best] = false;
            boss.PartPatched[best] = true;
            boss.PartFrac[best] = Math.Clamp(share, 0.05f, 1f);
            Recompute(boss);
            _world.Emit(SimEvent.PartBack(boss, best, boss.PartPosition(best), boss.Def.Parts[best].Id));
            return best;
        }

        /// <summary>
        /// Everything the broken parts take away, from scratch: mounts off, skills off (once every part
        /// that carries a skill is broken), mechanisms off, speed, turning, cadence, spread and lost locks.
        /// </summary>
        internal static void Recompute(Vehicle boss)
        {
            var parts = boss.Def.Parts;
            var skills = boss.Def.Skills;
            for (var m = 0; m < boss.MountOff.Length; m++)
            {
                boss.MountOff[m] = false;
                boss.MountSpread[m] = 1f;
                boss.MountFail[m] = 0f;
            }
            for (var k = 0; k < boss.SkillOff.Length; k++)
            {
                var carried = false;
                var standing = false;
                for (var i = 0; i < parts.Count; i++)
                {
                    if (!Contains(parts[i].Skills, skills[k].Id)) continue;
                    carried = true;
                    standing |= !boss.PartBroken[i];
                }
                boss.SkillOff[k] = carried && !standing;
            }
            var speed = 1f;
            var turn = 1f;
            var cadence = 1f;
            boss.BombardOff = boss.SpotterOff = boss.BurrowOff = boss.LandingOff = boss.AuraOff = false;
            for (var i = 0; i < parts.Count; i++)
            {
                if (!boss.PartBroken[i]) continue;
                var part = parts[i];
                foreach (var m in part.Mounts) boss.MountOff[m] = true;
                speed *= part.Speed;
                turn *= part.Turn;
                cadence *= part.Cadence;
                for (var m = 0; m < boss.MountSpread.Length; m++)
                {
                    if (part.Affects.Count > 0 && !Contains(part.Affects, m)) continue;
                    boss.MountSpread[m] *= part.Spread;
                    boss.MountFail[m] = MathF.Min(0.9f, boss.MountFail[m] + part.Fail);
                }
                foreach (var stop in part.Stops)
                    switch (stop)
                    {
                        case "bombard": boss.BombardOff = true; break;
                        case "spotter": boss.SpotterOff = true; break;
                        case "burrow": boss.BurrowOff = true; break;
                        case "landing": boss.LandingOff = true; break;
                        case "aura": boss.AuraOff = true; break;
                    }
            }
            boss.PartSpeed = speed;
            boss.TurnFactor = boss.TurnFactor / boss.PartTurn * turn;
            boss.TurretFactor = boss.TurretFactor / boss.PartTurn * turn;
            boss.PartTurn = turn;
            boss.PartCadence = cadence;
        }

        private static bool Contains(IReadOnlyList<int> list, int x)
        {
            foreach (var y in list)
                if (y == x) return true;
            return false;
        }

        private static bool Contains(IReadOnlyList<string> list, string x)
        {
            foreach (var y in list)
                if (y == x) return true;
            return false;
        }
    }
}

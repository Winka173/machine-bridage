#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Combat
{
    /// <summary>
    /// Prompt 28 E (tower targeting modes, towers sharing a target, the sheet's special rules) and F.2 (a boss's target
    /// weights by its behaviour types), as factors on the existing target score, so the switch margin and the hold until
    /// dead or out of reach (E.3) are the ones every vehicle has.
    /// </summary>
    internal sealed partial class CombatSystem
    {
        /// <summary>A tower's effective mode: the one set on it, else the data's default for its type, else Nearest.</summary>
        internal TowerMode ModeOf(Vehicle tower)
        {
            if (tower.TowerMode != TowerMode.Default) return tower.TowerMode;
            if (!_world.Catalog.AiData.Towers.TryGetValue(tower.Def.Id, out var t)) return TowerMode.Nearest;
            // A tactic's tower mode (base defence: "Lead") where the tower offers it and the player set none.
            if (_world.AiCommanders.TryGetValue(tower.Team, out var c) && c.CurrentTactic.Modules.TowerMode is { } m &&
                Enum.TryParse<TowerMode>(m, out var wanted))
                foreach (var allowed in t.Modes)
                    if (allowed == wanted) return wanted;
            return t.Mode;
        }

        private float TowerWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (!v.Def.Static || v.Def.Boss) return 1f;
            var worth = ModeOf(v) switch
            {
                TowerMode.Nearest or TowerMode.NearestRound or TowerMode.ShieldKey => 1f / (1f + 2f * Vector2.Distance(v.Position, other.Position) / MathF.Max(1f, weapon.Range)),
                TowerMode.Strongest => MathF.Sqrt(MathF.Max(0.5f, TeamIntel.StrengthOf(other))),
                TowerMode.Weakest => 1.6f - other.Hp / MathF.Max(1f, other.MaxHp) + 200f / MathF.Max(50f, other.Hp),
                TowerMode.Lead => Lead(v, other),
                TowerMode.AirFirst or TowerMode.MissilesFirst => other.Flying ? 3f : 1f,
                TowerMode.BiggestAircraft => other.Flying ? 1f + other.MaxHp / 300f : 0.5f,
                TowerMode.Cluster => 1f + 0.5f * Crowd(other, 8f),
                TowerMode.ArtilleryFirst => other.Def.Weapon.MinRange > 0f ? 3f : 1f,
                _ => 1f,
            };
            // The sheet's special rules (E.4).
            switch (v.Def.Id)
            {
                case "atgm_tower":
                case "one_shot_atgm_tower":
                case "recoilless_gun_tower":
                case "at_gun_emplacement":
                    // No missile on a light vehicle while armour is in reach.
                    if (other.Armor == ArmorClass.Light && ArmourInReach(v, weapon)) worth *= 0.05f;
                    break;
                case "guard_tower":
                    if (other.Armor == ArmorClass.Light || other.Def.Class == UnitClass.Scout) worth *= 1.5f;
                    break;
                case "mg_bunker":
                    if (other.Armor == ArmorClass.Light) worth *= 1f + 0.3f * Crowd(other, 8f);
                    break;
                case "rocket_turret":
                    worth *= Crowd(other, 8f) >= 2 ? 2f : 0.6f; // waits for a group of three or more where it can
                    break;
                case "drone_hangar":
                    if (other.Def.Weapon.MinRange > 0f || !other.IsMoving) worth *= 2f;
                    break;
            }
            // E.2: towers close together take the same target when it goes down fast.
            if (other.Hp < other.MaxHp * 0.5f)
                foreach (var f in _world.VehicleList)
                    if (f != v && f.IsAlive && f.Team == v.Team && f.Def.Static && f.Target == other.Id &&
                        Vector2.DistanceSquared(f.Position, v.Position) < 40f * 40f)
                    {
                        worth *= 1.4f;
                        break;
                    }
            return worth;
        }

        /// <summary>"Đầu đoàn": the enemy furthest forward towards this side's camp.</summary>
        private float Lead(Vehicle tower, Vehicle other)
        {
            if (!_world.TryGetRally(tower.Team, out var home)) return 1f;
            return 1f + 60f / MathF.Max(10f, Vector2.Distance(other.Position, home));
        }

        private bool ArmourInReach(Vehicle v, WeaponDef weapon)
        {
            foreach (var e in _world.VehicleList)
                if (e.IsAlive && e.Team != v.Team && e.Team >= 0 && e.Armor == ArmorClass.Heavy && e.IsVisibleTo(v.Team) &&
                    Vector2.DistanceSquared(e.Position, v.Position) <= weapon.Range * weapon.Range) return true;
            return false;
        }

        private int Crowd(Vehicle e, float radius)
        {
            var n = 0;
            foreach (var o in _world.VehicleList)
                if (o != e && o.IsAlive && o.Team == e.Team && o.Flying == e.Flying && Vector2.DistanceSquared(o.Position, e.Position) <= radius * radius) n++;
            return n;
        }

        /// <summary>
        /// F.2: a boss's weights by its behaviour types on top of the score's value, threat, distance and reach: Anti-Blob
        /// the crowd, Anti-Air aircraft, Anti-Artillery guns and still targets, Core Protection whoever attacks it up close,
        /// Flank Punishment whatever is off its front, Area Denial whatever stands still.
        /// </summary>
        private float BossWorth(Vehicle v, Vehicle other, WeaponDef weapon)
        {
            if (!v.Def.Boss) return 1f;
            var kinds = _world.Bosses.Behaviours(v);
            if (kinds.Count == 0) return 1f;
            var worth = other.Target == v.Id ? 1.2f : 1f;
            foreach (var k in kinds)
                worth *= k switch
                {
                    BossBehaviour.AntiBlob => 1f + 0.4f * Crowd(other, 10f),
                    BossBehaviour.AntiAir => other.Flying ? 2.5f : 1f,
                    BossBehaviour.AntiArtillery => other.Def.Weapon.MinRange > 0f ? 3f : other.IsMoving ? 1f : 1.3f,
                    BossBehaviour.CoreProtection => other.Target == v.Id && Vector2.Distance(other.Position, v.Position) < 30f ? 1.8f : 1f,
                    BossBehaviour.FlankPunishment => BossSystem.Behind(v, other) ? 2.2f : 1f,
                    BossBehaviour.AreaDenial => other.IsMoving ? 1f : 1.6f,
                    _ => 1f,
                };
            return worth;
        }

        /// <summary>E.4: a point-defence tower's next round by its mode (key structures and boss missiles first for C-RAM's default).</summary>
        private bool BetterRound(Vehicle v, Projectile p, Projectile best)
        {
            if (!v.Def.Static) return p.TimeLeft < best.TimeLeft;
            var mode = ModeOf(v);
            int Rank(Projectile r)
            {
                if (mode == TowerMode.MissilesFirst) return r.Weapon.Projectile is ProjectileKind.Missile or ProjectileKind.Rocket ? 0 : 1;
                if (mode != TowerMode.ShieldKey) return 0;
                var fromBoss = _world.TryGetVehicle(r.Owner, out var owner) && owner.Def.Boss;
                var atKey = _world.TryGetVehicle(r.Target, out var target) && target.Def.Static;
                return fromBoss || atKey ? 0 : 1;
            }
            var a = Rank(p);
            var b = Rank(best);
            return a != b ? a < b : p.TimeLeft < best.TimeLeft;
        }
    }
}

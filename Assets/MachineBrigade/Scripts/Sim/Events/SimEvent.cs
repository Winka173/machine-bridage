#nullable enable
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Events
{
    public enum SimEventKind
    {
        VehicleSpawned,
        VehicleDestroyed,
        PropDestroyed,
        WeaponFired,
        ProjectileImpact,
        Explosion,
        Damaged,

        /// <summary>A vehicle was bought; it arrives at Position after Value seconds.</summary>
        DeploymentQueued,

        /// <summary>A strike was called: Position (and Target for lines), Value = seconds until impact.</summary>
        StrikeWarning,

        /// <summary>One shell, bomb or missile of a strike landed at Position (Value = blast radius).</summary>
        StrikeImpact,

        /// <summary>A strike aircraft or cruise missile flies from Position to Target over Value seconds.</summary>
        AircraftPass,

        /// <summary>A smoke cloud appeared at Position with radius Value.</summary>
        SmokeDeployed,

        /// <summary>A vehicle was repaired by Value hit points.</summary>
        Repaired,

        /// <summary>An objective changed hands: Team is the new owner (-1 neutral), DefId the point id.</summary>
        PointCaptured,

        /// <summary>A vehicle used a skill: DefId is the skill, Tier carries its kind (see <c>SkillKind</c>), Value its duration.</summary>
        SkillUsed,

        /// <summary>A mine was laid at Position (Entity: the mine).</summary>
        MineLaid,

        /// <summary>A mine went off at Position (an Explosion event follows).</summary>
        MineDetonated,

        /// <summary>A vehicle left the battle without being destroyed (a loaned escort flying home).</summary>
        VehicleRetired,

        /// <summary>A supply crate is parachuting down onto Position, landing in Value seconds.</summary>
        CrateIncoming,

        /// <summary>Team claimed the supply crate at Position.</summary>
        CrateClaimed,

        /// <summary>
        /// An active protection system (Entity) shot down an incoming round (DefId: its weapon) at
        /// Position; Value is -1 for the left launcher, +1 for the right.
        /// </summary>
        Intercepted,

        /// <summary>
        /// A siege stage fell (Value: the stage now under way, 2 or 3; 4 when the fortress falls)
        /// at Position; DefId is the string key announcing what comes next.
        /// </summary>
        StageCleared,

        /// <summary>A fortress event (DefId: its string key, for the announcement) at Position.</summary>
        FortressAlert,
    }

    /// <summary>
    /// Something the presentation should show. Events describe what already happened in the
    /// simulation; effects and sounds consume them and never feed damage back.
    /// </summary>
    public readonly struct SimEvent
    {
        private SimEvent(SimEventKind kind, EntityId entity, Vector2 position, Vector2 target, float value,
            ExplosionTier tier, string? defId, int team, int mount = 0, EntityId other = default, bool airborne = false)
        {
            Airborne = airborne;
            Mount = mount;
            Other = other;
            Kind = kind;
            Entity = entity;
            Position = position;
            Target = target;
            Value = value;
            Tier = tier;
            DefId = defId;
            Team = team;
        }

        public SimEventKind Kind { get; }

        /// <summary>The vehicle or prop concerned (the shooter for WeaponFired, the source for Explosion).</summary>
        public EntityId Entity { get; }

        public Vector2 Position { get; }

        /// <summary>Aim point for WeaponFired.</summary>
        public Vector2 Target { get; }

        /// <summary>Travel time (WeaponFired), radius (impacts, explosions) or damage dealt (Damaged).</summary>
        public float Value { get; }

        public ExplosionTier Tier { get; }

        /// <summary>Vehicle, prop or weapon definition id, for choosing visuals.</summary>
        public string? DefId { get; }

        public int Team { get; }

        /// <summary>The impact or blast happened in the air (flak and missiles hitting aircraft).</summary>
        public bool Airborne { get; }

        /// <summary>Weapon mount index for WeaponFired (0 = main weapon), matching VehicleDef.Mounts.</summary>
        public int Mount { get; }

        /// <summary>Second entity involved: the target of a shot (guided missiles home in on it).</summary>
        public EntityId Other { get; }

        internal static SimEvent Spawned(Vehicle v) =>
            new(SimEventKind.VehicleSpawned, v.Id, v.Position, default, 0f, default, v.Def.Id, v.Team);

        internal static SimEvent Fired(Vehicle shooter, int mount, Vector2 origin, Vector2 aim, float travelTime, EntityId target)
        {
            var weapon = shooter.Def.Mounts[mount].Weapon;
            return new(SimEventKind.WeaponFired, shooter.Id, origin, aim, travelTime, weapon.ImpactTier, weapon.Id,
                shooter.Team, mount, target);
        }

        internal static SimEvent Impact(WeaponDef weapon, Vector2 at, EntityId hit, int team, bool airborne = false) =>
            new(SimEventKind.ProjectileImpact, hit, at, default, weapon.SplashRadius, weapon.ImpactTier, weapon.Id, team,
                airborne: airborne);

        internal static SimEvent Exploded(Vector2 at, ExplosionDef explosion, EntityId source) =>
            new(SimEventKind.Explosion, source, at, default, explosion.Radius, explosion.Tier, null, Teams.Environment);

        internal static SimEvent Damage(IDamageable target, float amount) =>
            new(SimEventKind.Damaged, target.Id, target.Position, default, amount, default, null, target.Team);

        internal static SimEvent VehicleLost(Vehicle v) =>
            new(SimEventKind.VehicleDestroyed, v.Id, v.Position, default, 0f, ExplosionTier.Medium, v.Def.Id, v.Team);

        internal static SimEvent DeploymentQueued(int team, string vehicleId, Vector2 at, float seconds) =>
            new(SimEventKind.DeploymentQueued, EntityId.None, at, default, seconds, default, vehicleId, team);

        internal static SimEvent StrikeWarning(int team, SupportDef support, Vector2 at, Vector2 towards, float seconds) =>
            new(SimEventKind.StrikeWarning, EntityId.None, at, towards, seconds, support.Tier, support.Id, team);

        internal static SimEvent StrikeImpact(int team, SupportDef support, Vector2 at) =>
            new(SimEventKind.StrikeImpact, EntityId.None, at, default, support.BlastRadius, support.Tier, support.Id, team);

        internal static SimEvent AircraftPass(int team, SupportDef support, Vector2 from, Vector2 to, float seconds) =>
            new(SimEventKind.AircraftPass, EntityId.None, from, to, seconds, support.Tier, support.Id, team);

        internal static SimEvent SmokeDeployed(int team, Vector2 at, float radius, float seconds) =>
            new(SimEventKind.SmokeDeployed, EntityId.None, at, new Vector2(seconds, 0f), radius, default, null, team);

        internal static SimEvent RepairedBy(Vehicle v, float amount) =>
            new(SimEventKind.Repaired, v.Id, v.Position, default, amount, default, v.Def.Id, v.Team);

        internal static SimEvent Captured(string pointId, Vector2 at, int owner) =>
            new(SimEventKind.PointCaptured, EntityId.None, at, default, 0f, default, pointId, owner);

        internal static SimEvent SkillUsed(Vehicle v, SkillDef skill) =>
            new(SimEventKind.SkillUsed, v.Id, v.Position, default, skill.Duration, (ExplosionTier)(int)skill.Kind, skill.Id, v.Team,
                airborne: v.Flying);

        /// <summary>Which skill a <see cref="SimEventKind.SkillUsed"/> event carries.</summary>
        public SkillKind Skill => (SkillKind)(int)Tier;

        internal static SimEvent Retired(Vehicle v) =>
            new(SimEventKind.VehicleRetired, v.Id, v.Position, default, 0f, default, v.Def.Id, v.Team, airborne: v.Flying);

        internal static SimEvent CrateIncoming(Crate c, float seconds) =>
            new(SimEventKind.CrateIncoming, c.Id, c.Position, default, seconds, default, null, Teams.Neutral);

        internal static SimEvent Intercept(Vehicle aps, WeaponDef weapon, Vector2 at, bool left) =>
            new(SimEventKind.Intercepted, aps.Id, at, aps.Position, left ? -1f : 1f, ExplosionTier.Small, weapon.Id, aps.Team);

        internal static SimEvent Stage(int stage, Vector2 at, string key) =>
            new(SimEventKind.StageCleared, default, at, default, stage, default, key, 0);

        internal static SimEvent Alert(Vector2 at, string key) =>
            new(SimEventKind.FortressAlert, default, at, default, 0f, default, key, 1);

        internal static SimEvent CrateClaimed(Crate c, int team) =>
            new(SimEventKind.CrateClaimed, c.Id, c.Position, default, 0f, default, null, team);

        internal static SimEvent MineLaid(Mine m) =>
            new(SimEventKind.MineLaid, m.Id, m.Position, default, 0f, default, null, m.Team);

        internal static SimEvent MineDetonated(Mine m) =>
            new(SimEventKind.MineDetonated, m.Id, m.Position, default, m.Def.Blast.Radius, m.Def.Blast.Tier, null, m.Team);

        /// <summary>A tree or fence knocked down by a hull; Target is the way it falls.</summary>
        internal static SimEvent PropCrushed(Prop p, Vector2 direction) =>
            new(SimEventKind.PropDestroyed, p.Id, p.Position, direction, p.Radius, ExplosionTier.Small, p.Def.Id, Teams.Neutral);

        internal static SimEvent PropLost(Prop p) =>
            new(SimEventKind.PropDestroyed, p.Id, p.Position, default, p.Radius, ExplosionTier.Medium, p.Def.Id, Teams.Neutral);
    }
}

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

        /// <summary>A counter-battery radar (Entity) found an enemy gun (Other) that fired: shown to the radar's side for Value seconds.</summary>
        GunRevealed,

        /// <summary>A vehicle changed sides (Team: its new side): drawn again in its new colours.</summary>
        Defected,

        /// <summary>
        /// A multi-phase boss (Entity) reached a phase: Value its number (2 up), Mount 1 as its
        /// transformation begins and 0 when it fights on, DefId its general's radio line (or null).
        /// </summary>
        BossPhase,

        /// <summary>A multi-stage mission moved on: DefId is the new stage's id, Value its number (1 up).</summary>
        StageStarted,

        /// <summary>The play area changed (Position its lower corner, Target its upper; Value 0 for the whole map).</summary>
        AreaChanged,

        /// <summary>A radio message for the player (DefId: its text key).</summary>
        Radio,

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

        /// <summary>
        /// A fire-support round (DefId: the support) is coming down onto Position, landing in Value
        /// seconds, fired from the direction of Target (a unit vector): drawn falling from the sky.
        /// </summary>
        ShellInbound,

        /// <summary>Team knocked down an enemy building worth a bounty (DefId: the building) at Position, paid Value CP.</summary>
        Bounty,

        /// <summary>
        /// A vehicle's equipment went off where the player should see it (DefId: the trait's or
        /// module's key, e.g. "ricochet_shells"): the game shows a short word over the vehicle. At
        /// most one every two seconds per vehicle.
        /// </summary>
        TraitProc,

        /// <summary>A charged weapon (Mount) of Entity began powering up; it fires in Value seconds at Target.</summary>
        WeaponCharging,

        /// <summary>
        /// A fortress's reinforcements are on their way in by its line (DefId "rail" or "runway"):
        /// the train or aircraft gets to Position (the stop) in Value seconds, facing Target (a unit
        /// vector); Team is whose they are. The vehicles aboard come as DeploymentQueued events with
        /// Mount 1 (no parachute) and land when it stops.
        /// </summary>
        Arrival,
        /// <summary>A boss part broke: Entity the boss, Mount the part's index, Position where it was, DefId the part's id.</summary>
        PartBroken,

        /// <summary>A boring boss (Entity): Value 0 it dives, 1 the ground cracks at Position (it breaks out in Target.X seconds), 2 it breaks out at Position.</summary>
        Burrowing,

        /// <summary>A landing craft (Entity) lowers its ramp at Position and lands Value vehicles.</summary>
        TroopsLanding,

        /// <summary>A boss's self-repair put a part back: Entity the boss, Mount the part's index, DefId its id.</summary>
        PartRepaired,

        /// <summary>Prompt 16: a patch of a boss's fire trail lit at Position (Entity the boss): Value its lit seconds, Target.X its radius.</summary>
        FireTrail,
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

        /// <summary>A shot from equipment rather than a mount (a Drone Escort drone): drawn from the main muzzle with its own weapon's look.</summary>
        internal static SimEvent FiredWith(Vehicle shooter, WeaponDef weapon, Vector2 origin, Vector2 aim, float travelTime, EntityId target) =>
            new(SimEventKind.WeaponFired, shooter.Id, origin, aim, travelTime, weapon.ImpactTier, weapon.Id, shooter.Team, 0, target);

        internal static SimEvent Charging(Vehicle shooter, int mount, float seconds, Vector2 aim) =>
            new(SimEventKind.WeaponCharging, shooter.Id, shooter.Position, aim, seconds, default, shooter.Def.Mounts[mount].Weapon.Id,
                shooter.Team, mount);

        internal static SimEvent Proc(Vehicle v, string key) =>
            new(SimEventKind.TraitProc, v.Id, v.Position, default, 0f, default, key, v.Team, airborne: v.Flying);

        internal static SimEvent Impact(WeaponDef weapon, Vector2 at, EntityId hit, int team, bool airborne = false) =>
            new(SimEventKind.ProjectileImpact, hit, at, default, weapon.SplashRadius, weapon.ImpactTier, weapon.Id, team,
                airborne: airborne);

        internal static SimEvent Exploded(Vector2 at, ExplosionDef explosion, EntityId source) =>
            new(SimEventKind.Explosion, source, at, default, explosion.Radius, explosion.Tier, null, Teams.Environment);

        internal static SimEvent Damage(IDamageable target, float amount) =>
            new(SimEventKind.Damaged, target.Id, target.Position, default, amount, default, null, target.Team);

        internal static SimEvent VehicleLost(Vehicle v) =>
            new(SimEventKind.VehicleDestroyed, v.Id, v.Position, default, 0f, ExplosionTier.Medium, v.Def.Id, v.Team);

        /// <summary>A vehicle bought: where it will land (Position), which way it faces in (Target), and in how long (Value).</summary>
        internal static SimEvent DeploymentQueued(int team, string vehicleId, Vector2 at, Vector2 inward, float seconds) =>
            new(SimEventKind.DeploymentQueued, EntityId.None, at, inward, seconds, default, vehicleId, team);

        /// <summary>A delivery that comes by a fortress's line (Mount 1): it gets off at Position when the train or aircraft stops.</summary>
        internal static SimEvent DeploymentRouted(int team, string vehicleId, Vector2 at, Vector2 inward, float seconds) =>
            new(SimEventKind.DeploymentQueued, EntityId.None, at, inward, seconds, default, vehicleId, team, mount: 1);

        /// <summary>Whether a DeploymentQueued event is a delivery by a fortress's line (no parachute).</summary>
        public bool ByLine => Kind == SimEventKind.DeploymentQueued && Mount == 1;

        internal static SimEvent ArrivalInbound(int team, string kind, Vector2 stop, Vector2 facing, float seconds) =>
            new(SimEventKind.Arrival, EntityId.None, stop, facing, seconds, default, kind, team);

        internal static SimEvent StrikeWarning(int team, SupportDef support, Vector2 at, Vector2 towards, float seconds) =>
            new(SimEventKind.StrikeWarning, EntityId.None, at, towards, seconds, support.Tier, support.Id, team);

        internal static SimEvent BountyPaid(int team, string building, Vector2 at, float cp) =>
            new(SimEventKind.Bounty, EntityId.None, at, default, cp, default, building, team);

        internal static SimEvent ShellInbound(int team, SupportDef support, Vector2 at, Vector2 from, float seconds) =>
            new(SimEventKind.ShellInbound, EntityId.None, at, from, seconds, support.Tier, support.Id, team);

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

        /// <summary>A fortress's alarm (its sirens): Team 1 when it is bad news for the player, 0 when good (a gate of the enemy's blown in).</summary>
        internal static SimEvent Alert(Vector2 at, string key, bool bad = true) =>
            new(SimEventKind.FortressAlert, default, at, default, 0f, default, key, bad ? 1 : 0);

        internal static SimEvent CrateClaimed(Crate c, int team) =>
            new(SimEventKind.CrateClaimed, c.Id, c.Position, default, 0f, default, null, team);

        internal static SimEvent Revealed(Vehicle radar, Vehicle gun, float seconds) =>
            new(SimEventKind.GunRevealed, radar.Id, gun.Position, default, seconds, default, gun.Def.Id, radar.Team, other: gun.Id);

        internal static SimEvent PartLost(Vehicle boss, int part, Vector2 at, string id) =>
            new(SimEventKind.PartBroken, boss.Id, at, boss.Position, 0f, ExplosionTier.Huge, id, boss.Team, part);

        internal static SimEvent PartBack(Vehicle boss, int part, Vector2 at, string id) =>
            new(SimEventKind.PartRepaired, boss.Id, at, boss.Position, 0f, ExplosionTier.Small, id, boss.Team, part);

        internal static SimEvent Burrow(Vehicle boss, int stage, Vector2 at, float seconds = 0f) =>
            new(SimEventKind.Burrowing, boss.Id, at, new Vector2(seconds, 0f), stage, ExplosionTier.Ultimate, boss.Def.Id, boss.Team);

        /// <summary>A patch of the Inferno's fire trail lit at Position (prompt 16): Value its lit seconds, Target.X its radius.</summary>
        internal static SimEvent FireTrail(Vehicle boss, Vector2 at, float seconds, float radius) =>
            new(SimEventKind.FireTrail, boss.Id, at, new Vector2(radius, 0f), seconds, ExplosionTier.Medium, boss.Def.Id, boss.Team);

        internal static SimEvent Landed(Vehicle boss, Vector2 at, int count) =>
            new(SimEventKind.TroopsLanding, boss.Id, at, boss.Position, count, ExplosionTier.Large, boss.Def.Id, boss.Team);

        internal static SimEvent BossPhase(Vehicle v, int number, bool begins, string? radio) =>
            new(SimEventKind.BossPhase, v.Id, v.Position, default, number, default, radio, v.Team, mount: begins ? 1 : 0);

        internal static SimEvent Defected(Vehicle v) =>
            new(SimEventKind.Defected, v.Id, v.Position, default, 0f, default, v.Def.Id, v.Team);

        internal static SimEvent AreaChanged(Content.PlayArea? area) =>
            new(SimEventKind.AreaChanged, EntityId.None, area?.Min ?? default, area?.Max ?? default, area.HasValue ? 1f : 0f, default, null, 0);

        internal static SimEvent RadioMessage(string key, int team = 0) =>
            new(SimEventKind.Radio, EntityId.None, default, default, 0f, default, key, team);

        internal static SimEvent StageBegan(string stageId, int number) =>
            new(SimEventKind.StageStarted, EntityId.None, default, default, number, default, stageId, 0);

        internal static SimEvent MineLaid(Mine m) =>
            new(SimEventKind.MineLaid, m.Id, m.Position, default, 0f, default, null, m.Team);

        /// <summary>An engineer cleared a mine (it just goes; no blast).</summary>
        internal static SimEvent MineCleared(Mine m) =>
            new(SimEventKind.MineDetonated, m.Id, m.Position, default, 0f, ExplosionTier.Small, null, m.Team);

        internal static SimEvent MineDetonated(Mine m) =>
            new(SimEventKind.MineDetonated, m.Id, m.Position, default, m.Def.Blast.Radius, m.Def.Blast.Tier, null, m.Team);

        /// <summary>A tree or fence knocked down by a hull; Target is the way it falls.</summary>
        internal static SimEvent PropCrushed(Prop p, Vector2 direction) =>
            new(SimEventKind.PropDestroyed, p.Id, p.Position, direction, p.Radius, ExplosionTier.Small, p.Def.Id, Teams.Neutral);

        internal static SimEvent PropLost(Prop p) =>
            new(SimEventKind.PropDestroyed, p.Id, p.Position, default, p.Radius, ExplosionTier.Medium, p.Def.Id, Teams.Neutral);
    }
}

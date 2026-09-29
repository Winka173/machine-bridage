#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Modes
{
    public sealed class SiegeRules
    {
        /// <summary>
        /// The clock is a time bank (as in Overwatch escort): this much at the start, and each
        /// stage cleared adds its bonus, up to <see cref="MaxBank"/> on the clock at once.
        /// </summary>
        public float StartSeconds { get; set; } = 300f;

        public float[] StageBonus { get; set; } = { 240f, 300f };
        public float MaxBank { get; set; } = 600f;

        /// <summary>
        /// The clock may run over by up to this long while the attackers are fighting at a live
        /// objective, so a strike already in the air can still count.
        /// </summary>
        public float Overtime { get; set; } = 90f;

        /// <summary>Stage 1 objectives: the relay stations of the outer line.</summary>
        public string Relay { get; set; } = "radar_station";

        /// <summary>Stage 2 objectives: the shield generators inside the walls, which keep the HQ shielded.</summary>
        public string Generator { get; set; } = "shield_generator";

        /// <summary>Stage 3: the prop that has to fall.</summary>
        public string Target { get; set; } = "command_hq";

        /// <summary>The HQ is this many times tougher than the building's catalogue health.</summary>
        public float Hardening { get; set; } = 2.5f;

        /// <summary>The relay stations and the shield generators are this many times tougher (Defend's lines hold longer).</summary>
        public float LineHardening { get; set; } = 1f;

        /// <summary>The fortress guardian that rolls out of the keep when stage 3 begins (null: none).</summary>
        public string? Guardian { get; set; } = "mobile_fortress";

        /// <summary>
        /// The stage the attack starts at (the weekly fortress: rings broken in an earlier attack
        /// this week stay broken). Their objectives and guns are gone; the clock has their bonuses.
        /// </summary>
        public int StartStage { get; set; } = 1;

        /// <summary>CP the attacker gets each time a stage falls.</summary>
        public float StageCp { get; set; } = 20f;

        /// <summary>
        /// CP the defender gets when it loses its outer line and its walls: the towers of the lost
        /// line blow up, and the side falls back on the next with something to spend.
        /// </summary>
        public float[] RetreatCp { get; set; } = { 16f, 22f };

        /// <summary>The fortress's own buildings (barracks, stores, offices, workshops): each one knocked down pays the attacker.</summary>
        public HashSet<string> BountyBuildings { get; set; } = new()
        {
            "warehouse", "office_block", "house_large", "house_small", "garage", "container_stack", "container", "townhouse",
            "radar_dome", "fuel_depot", "ammo_dump", "vehicle_hangar", "barn", "apartment", "adobe_house", "adobe_large",
            "cottage", "log_cabin", "shop", "factory", "hangar", "control_tower",
        };

        public SideSetup Attacker { get; set; } = new() { StartCp = 34f, Income = 1.8f, ArmyCap = 40 };
        public SideSetup Defender { get; set; } = new() { StartCp = 20f, Income = 1f };

        /// <summary>
        /// Defend: the fortress is the player's base and the enemy lays siege to it. The map's two
        /// sides trade places (the fortress's guns and garrison become the player's); the player
        /// holds until the attacker's clock runs out.
        /// </summary>
        public bool PlayerDefends { get; set; }

        /// <summary>Endless: no clock; the waves keep coming, bigger and more often elite, until the HQ falls.</summary>
        public bool Endless { get; set; }

        /// <summary>Seconds between the attacker's waves (flown in on top of what it buys); 0: none.</summary>
        public float WaveSeconds { get; set; }

        /// <summary>What the waves are mostly made of: the cheap swarm (empty: the attacker's deck).</summary>
        public IReadOnlyList<string> WaveRoster { get; set; } = Array.Empty<string>();

        /// <summary>The few heavier vehicles a wave brings on top of its swarm (see <see cref="HeavyEvery"/>); empty: none.</summary>
        public IReadOnlyList<string> WaveHeavy { get; set; } = Array.Empty<string>();

        /// <summary>The first wave's size, how much each wave grows, and the most one wave brings.</summary>
        public int WaveStart { get; set; } = 3;

        public float WaveGrowth { get; set; } = 1f;
        public int WaveMax { get; set; } = 12;

        /// <summary>One heavy vehicle in the wave per this many waves so far, up to a quarter of the wave.</summary>
        public int HeavyEvery { get; set; } = 3;

        /// <summary>From this wave on more and more of a wave comes as the elite versions.</summary>
        public int EliteFrom { get; set; } = 6;

        /// <summary>
        /// Prompt 13 H.7-H.8: the waves grow with the defender's base (its towers' rank and equipment, its
        /// HQ level: <see cref="BaseStrength"/>): their size times <see cref="BaseStrength.WaveScale"/>, the
        /// attacker's income times its square root.
        /// </summary>
        public bool ScaleToBase { get; set; }

        /// <summary>
        /// Endless: each wave this share bigger than the last (on top of <see cref="WaveGrowth"/>, which
        /// adds vehicles), so the pressure climbs smoothly (0: only the added vehicles).
        /// </summary>
        public float WaveCompound { get; set; }

        /// <summary>Siege breakers a wave brings from <see cref="BreachFrom"/> on, one more every <see cref="BreachEvery"/> waves (bulldozers, siege guns, long guns that outrange the towers).</summary>
        public IReadOnlyList<string> WaveBreachers { get; set; } = Array.Empty<string>();

        public int BreachFrom { get; set; } = 2;
        public int BreachEvery { get; set; } = 2;

        /// <summary>The waves are drawn against the base they attack: its anti-air, anti-armour and machine-gun towers (prompt 13 H.7).</summary>
        public bool CounterBase { get; set; }

        /// <summary>
        /// Once a match, a player holding far too easily (after 4 minutes, the defenders on the field worth 1.6
        /// times the attackers or more) draws an extra breaching wave instead of anything for itself (H.12).
        /// </summary>
        public bool BreachWave { get; set; }

        /// <summary>Seeds the waves' make-up (drawn one wave ahead, so the preview is the wave that lands).</summary>
        public int WaveSeed { get; set; } = 1;

        /// <summary>
        /// The most attackers alive at once that the waves fill up to (Siege, Defend, Endless): a
        /// wave's vehicles beyond it wait off the map and come in as attackers fall. The tick
        /// budget sets the final number.
        /// </summary>
        public int MaxAlive { get; set; } = 48;

        /// <summary>The attacking side's camp (an Anchor base at the camp outside the walls); null: a bare HQ.</summary>
        public BaseLoadout? AttackerBase { get; set; }

        /// <summary>
        /// What stands in the fortress's hardpoints: the defender's base loadout (the enemy's drawn
        /// for its difficulty in Siege, the player's own in Defend); null: the AI's for Normal.
        /// </summary>
        public BaseLoadout? FortressLoadout { get; set; }

        /// <summary>The fortress's towers by ring (outer line, walls, keep): health and damage times the usual.</summary>
        public float[] LineHealth { get; set; } = { 1f, 1.25f, 1.5f };

        public float[] LineDamage { get; set; } = { 1f, 1.1f, 1.2f };

        /// <summary>The share of the outer line's and the walls' tower hardpoints that are manned (an easier fortress leaves some empty).</summary>
        public float Manning { get; set; } = 1f;

        /// <summary>
        /// Whether the fortress's side can fly destroyed towers back into their hardpoints (null: only
        /// when the fortress is the player's, in Defend; an AI fortress that rebuilt its keep under
        /// fire never fell).
        /// </summary>
        public bool? Rebuild { get; set; }

        /// <summary>
        /// Whether the attack blows in the keep's gate before going for the HQ (null: when the enemy
        /// attacks, in Defend; the player's army in Siege uses the keep's open gate). The walls' gate
        /// always comes first.
        /// </summary>
        public bool? KeepGateFirst { get; set; }

        /// <summary>The gates (blocking until blown in) and the wall segments (toppling into rubble).</summary>
        public string Gate { get; set; } = "fortress_gate";

        public string Wall { get; set; } = "base_wall";

        /// <summary>The fortress's super-gun (null: none), its shell, when it first fires and how often after.</summary>
        public string? SuperGun { get; set; } = "super_gun";

        public string SuperGunShell { get; set; } = "super_gun_shell";
        public float SuperGunFirst { get; set; } = 90f;
        public float SuperGunSeconds { get; set; } = 75f;

        /// <summary>CP the attacker gets for destroying the super-gun (a side objective; Siege pays coins too).</summary>
        public float SuperGunCp { get; set; } = 25f;

        /// <summary>
        /// CP the attacker gets for each of the fortress's landing pads it destroys (prompt 13 F.1: the
        /// defender's aircraft then rearm and mend only at their holding patterns and the HQ).
        /// </summary>
        public float PadCp { get; set; } = 12f;

        /// <summary>
        /// The defender's ground deliveries come in by the fortress's line (a train or an aircraft
        /// onto a runway) while it holds the walls, when the map has one and the defender is the AI.
        /// </summary>
        public bool Arrivals { get; set; } = true;

        /// <summary>Seconds from a train or aircraft being on its way to it stopping, and at least between two stops.</summary>
        public float ArrivalLead { get; set; } = 10f;

        public float ArrivalGap { get; set; } = 16f;

        /// <summary>Night: the fortress sounds its sirens when it spots attackers on its ground (set by the game with the weather).</summary>
        public bool Night { get; set; }
    }

    /// <summary>
    /// Siege (công thành), in three stages, on a fortress that holds 40-50 % of the battlefield.
    /// <list type="number">
    /// <item><description>Break the outer line: destroy its relay stations.</description></item>
    /// <item><description>Get inside the walls (blow in a gate or a wall; the sally ports are the
    /// long way round) and destroy the shield generators. While any stands, a shield dome covers
    /// the keep (its guns and the HQ cannot be hurt), and each one lost browns out the defences.</description></item>
    /// <item><description>Level the command HQ in the keep. Its guardian boss rolls out, and at
    /// 75, 50 and 25 % health the HQ calls a barrage, raises a shield round the keep with elite
    /// reinforcements, and makes a last stand.</description></item>
    /// </list>
    /// Each line lost blows up its towers one after another, adds time and pays the attacker CP,
    /// and pays the defender a retreat reward. The fortress's towers stand in sized hardpoints by
    /// ring from the defender's base loadout, the inner lines' tougher. Its super-gun fires a huge
    /// shell at the attackers on a countdown until it is destroyed (a side objective); its
    /// reinforcements come in by train or onto a runway; at night its sirens sound when it spots
    /// attackers. When the HQ falls, the whole fortress goes up in a chain.
    /// </summary>
    public sealed class SiegeMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly SiegeRules _rules;
        private readonly KillLedger _ledger = new();
        private readonly List<EntityId> _relays = new();
        private readonly List<EntityId> _generators = new();
        private readonly List<EntityId> _targets = new();
        private readonly List<EntityId>[] _defences = { new(), new(), new() };
        private readonly List<EntityId> _fortressProps = new();
        private readonly List<EntityId> _bounty = new();
        private readonly List<(EntityId id, int ring, Vector2 outward)> _gates = new();
        private readonly List<(EntityId id, int ring)> _walls = new();
        private readonly HashSet<EntityId> _gatesDown = new();
        private readonly bool[] _breachTold = new bool[4];

        /// <summary>The fortress buildings still standing that pay a bounty when knocked down (for the attacking AI).</summary>
        public IReadOnlyList<EntityId> BountyTargets => _bounty;

        /// <summary>Buildings the attacker has knocked down (each paid on the spot, and in coins at the end).</summary>
        public int BuildingsRazed { get; private set; }
        private readonly List<(double at, EntityId id, bool prop)> _chain = new();
        private double _wipedSince = -1;
        private double _deadline;
        private double _finishAt = -1;
        private double _glyphUntil = -1;
        private int _hqPhase;
        private FortressDef? _fortress;

        public SiegeMode(SiegeRules? rules = null) => _rules = rules ?? new SiegeRules();

        /// <summary>The rules this siege runs by.</summary>
        public SiegeRules Rules => _rules;

        /// <summary>The side breaking in and the side holding the fortress (the player attacks unless it defends).</summary>
        public int Attacker => _rules.PlayerDefends ? EnemyTeam : PlayerTeam;

        public int Defender => _rules.PlayerDefends ? PlayerTeam : EnemyTeam;

        /// <summary>Waves sent so far (Defend and Endless).</summary>
        public int Wave { get; private set; }

        /// <summary>Seconds until the next wave, or -1 when there are none.</summary>
        public float SecondsToWave(SimWorld world) => _rules.WaveSeconds > 0f ? MathF.Max(0f, (float)(_nextWave - world.Time)) : -1f;

        public bool Endless => _rules.Endless;

        private double _nextWave;

        /// <summary>A key for what just happened, in the words of the side the player is on.</summary>
        private string Key(string what) => (_rules.PlayerDefends ? "base." : "siege.") + what;

        private int Side(int mapTeam) => _rules.PlayerDefends && mapTeam is PlayerTeam or EnemyTeam ? 1 - mapTeam : mapTeam;

        public MatchResult? Result { get; private set; }
        public IReadOnlyList<ObjectiveState> Points => Array.Empty<ObjectiveState>();

        public int Kills => _ledger.Kills(PlayerTeam);
        public int Losses => _ledger.Losses(PlayerTeam);

        /// <summary>The stage under way: 1 outer line, 2 walls, 3 keep (4 once the fortress fell).</summary>
        public int Stage { get; private set; } = 1;

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, (float)(_deadline - world.Time));

        /// <summary>The fortress centre (the HQ), for the defender to rally round.</summary>
        public Vector2? Fortress { get; private set; }

        /// <summary>The map's fortress (its ground, hardpoints, super-gun and line in), or null on an older map.</summary>
        public FortressDef? FortressPlan => _fortress;

        /// <summary>Night (the weather): the sirens sound when the fortress spots attackers on its ground.</summary>
        public bool Night
        {
            get => _rules.Night;
            set => _rules.Night = value;
        }

        // ------------------------------------------------------------------ the shield dome

        /// <summary>The shield dome over the keep is up: a shield generator still stands (stages 1 and 2).</summary>
        public bool DomeUp { get; private set; }

        /// <summary>The dome's centre and radius (the keep's middle, reaching its corners).</summary>
        public Vector2 DomeCentre { get; private set; }

        public float DomeRadius { get; private set; }

        // ------------------------------------------------------------------ the super-gun

        /// <summary>The fortress's super-gun while it stands (None once destroyed, or on a map without one).</summary>
        public EntityId SuperGun { get; private set; }

        /// <summary>The super-gun was destroyed (the side objective done).</summary>
        public bool SuperGunDown { get; private set; }

        private double _superGunFireAt = double.MaxValue;
        private Vector2 _superGunAt;

        /// <summary>Where the super-gun stands (or stood).</summary>
        public Vector2 SuperGunAt => _superGunAt;

        /// <summary>Seconds until the super-gun fires its next shell, or -1 when there is none standing.</summary>
        public float SuperGunCountdown(SimWorld world) =>
            SuperGun.IsValid && _superGunFireAt < double.MaxValue ? MathF.Max(0f, (float)(_superGunFireAt - world.Time)) : -1f;

        /// <summary>Shells the super-gun has fired.</summary>
        public int SuperGunShots { get; private set; }

        // ------------------------------------------------------------------ the line in

        private double _arrivalAt = double.NaN;
        private double _lastArrival = double.MinValue;

        /// <summary>Trains (or aircraft) that have come in so far.</summary>
        public int Arrivals { get; private set; }

        // ------------------------------------------------------------------ waves

        private readonly List<string> _plan = new();
        private readonly List<(string id, int count)> _preview = new();
        private readonly Queue<(int wave, string id)> _reserve = new();
        private readonly List<double> _inbound = new();
        private readonly Dictionary<int, List<string>> _landed = new();
        private Random _waveRandom = new(1);

        /// <summary>
        /// The next wave's make-up (vehicle, how many), in the order it lands: drawn a wave ahead,
        /// so it is exactly the wave that comes. Empty when there are no waves.
        /// </summary>
        public IReadOnlyList<(string id, int count)> NextWave => _preview;

        /// <summary>Vehicles of waves already sent still waiting off the map for room under <see cref="SiegeRules.MaxAlive"/>.</summary>
        public int Held => _reserve.Count;

        /// <summary>What each wave actually brought in (by wave number), for checks.</summary>
        public IReadOnlyDictionary<int, List<string>> Landed => _landed;

        private double _spottedAt = double.MinValue;
        private double _spotCheck;

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Attacker.Build(Attacker));
            world.EnableEconomy(_rules.Defender.Build(Defender));
            // Defend: the camps trade places, so the player's drop zone is inside the fortress.
            if (_rules.PlayerDefends && world.TryGetRally(PlayerTeam, out var outside) && world.TryGetRally(EnemyTeam, out var inside))
            {
                world.SetRally(PlayerTeam, inside);
                world.SetRally(EnemyTeam, outside);
            }
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, Side(unit.Team), unit.Position, unit.Heading);
            _fortress = world.Map.Fortress;
            foreach (var prop in world.Props)
            {
                if (!prop.IsAlive) continue;
                if (prop.Def.Id == _rules.Target)
                {
                    _targets.Add(prop.Id);
                    if (_rules.Hardening > 1f) prop.Harden(_rules.Hardening);
                    Fortress ??= prop.Position;
                }
                else if (prop.Def.Id == _rules.Relay || prop.Def.Id == _rules.Generator)
                {
                    (prop.Def.Id == _rules.Relay ? _relays : _generators).Add(prop.Id);
                    if (_rules.LineHardening > 1f) prop.Harden(_rules.LineHardening);
                }
            }
            Fortress ??= _fortress?.Hq;
            if (Fortress == null && world.TryGetRally(Defender, out var rally)) Fortress = rally;
            var rings = world.Map.SiegeRings;
            ClassifyWorks(world, rings);
            // The fortress's towers in its hardpoints, from the defender's loadout.
            if (_fortress != null && _fortress.Slots.Count > 0 && Fortress is { } hqAt)
            {
                var loadout = _rules.FortressLoadout ?? BaseLoadout.ForAi(world.Catalog, "Normal");
                var role = _rules.PlayerDefends ? BaseRole.Defend : BaseRole.Target;
                var fortressBase = world.Bases.EstablishFortress(Defender, loadout, role, hqAt, _fortress.Slots, _rules.LineHealth, _rules.LineDamage, _rules.Manning);
                var rebuild = _rules.Rebuild ?? _rules.PlayerDefends;
                foreach (var slot in fortressBase.Slots)
                {
                    if (slot.Structure.IsValid) _defences[Math.Clamp(slot.Ring, 1, 3) - 1].Add(slot.Structure);
                    if (slot.Structure.IsValid && world.TryGetVehicle(slot.Structure, out var module) && module.Def.Utility is { AirRepair: > 0f })
                        _pads.Add((slot.Structure, module.Position));
                    if (!rebuild) slot.Lost = true;
                }
            }
            // An older map's fortress: its guns are map units.
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Defender && v.Def.Static && !Listed(v.Id))
                    _defences[RingOf(v.Position, rings) - 1].Add(v.Id);
            foreach (var ring in _defences)
                foreach (var id in ring)
                    // The attacker comes with the fortress plans: every gun is on the map from the start.
                    if (world.TryGetVehicle(id, out var gun)) gun.VisibleToMask |= 1 << Attacker;
            SpawnSuperGun(world);
            // Everything built into the fortress goes up with it at the end.
            if (Fortress is { } centre && rings.Count > 0)
                foreach (var prop in world.Props)
                    if (prop.IsAlive && prop.Def.BlocksMovement && !prop.Def.Indestructible &&
                        (_fortress is { Layered: true } layered ? layered.Contains(prop.Position) : Chebyshev(prop.Position, centre) <= rings[0] + 4f))
                    {
                        _fortressProps.Add(prop.Id);
                        if (_rules.BountyBuildings.Contains(prop.Def.Id)) _bounty.Add(prop.Id);
                    }
            // A map without relays (or generators) starts at the stage it has, with the time those stages would have earned.
            Stage = _relays.Count > 0 ? 1 : _generators.Count > 0 ? 2 : 3;
            // Rings already broken (the weekly fortress): their objectives and guns are gone.
            while (Stage < Math.Min(3, _rules.StartStage))
            {
                foreach (var id in Stage == 1 ? _relays : _generators)
                    if (world.TryGetProp(id, out var fallen)) world.RemoveQuietly(fallen);
                foreach (var id in _defences[Stage - 1])
                    if (world.TryGetVehicle(id, out var gun)) world.RemoveQuietly(gun);
                world.Bases.LoseRing(Defender, Stage);
                // Past the walls: their gates were blown in that attack.
                if (Stage == 2)
                    foreach (var (id, ring, _) in _gates)
                        if (ring == 2 && world.TryGetProp(id, out var gate)) world.RemoveQuietly(gate);
                Stage++;
                if (Stage == 3) SpawnGuardian(world);
            }
            _deadline = _rules.Endless ? double.MaxValue : _rules.StartSeconds;
            _nextWave = _rules.WaveSeconds > 0f ? _rules.WaveSeconds * 0.75f : double.MaxValue;
            for (var skipped = 1; skipped < Stage && skipped <= _rules.StageBonus.Length; skipped++) _deadline += _rules.StageBonus[skipped - 1];
            DomeUp = Stage <= 2 && _generators.Count > 0;
            Shield(world);
            // Prompt 17 B.2: on a long battlefield the attack's reinforcements land further forward once a ring has fallen.
            if (_fortress is { Layered: true } && _fortress.ForwardDrops.Count > 0)
                world.Bases.ForwardZone = team => team == Attacker ? ForwardDrop : null;
            // The attacker's own camp outside the walls (the map's side 0): its HQ and towers. Only
            // when the player attacks (Siege): the waves of Defend come without a camp of their own.
            if (Attacker == PlayerTeam && world.Map.BaseOf(0) != null && world.Catalog.Vehicles.ContainsKey(world.Catalog.Base.HqId))
                world.Bases.Establish(Attacker, _rules.AttackerBase ?? BaseLoadout.HqOnly(), Content.BaseRole.Anchor, siteTeam: 0);
            // The fortress's reinforcements come in by its rail line or runway while it holds its walls.
            if (_rules.Arrivals && !_rules.PlayerDefends && _fortress?.Arrival is { Kind: not ArrivalKind.None })
                world.Economy.Route = team => team == Defender ? NextArrival(world) : null;
            if (_rules.WaveSeconds > 0f)
            {
                _waveRandom = new Random(_rules.WaveSeed * 7919 + 17);
                // Prompt 13 H.7: the waves by the base they face, and drawn against it.
                if (_rules.ScaleToBase)
                {
                    BaseScore = BaseStrength.Score(world, Defender);
                    _waveScale = BaseStrength.WaveScale(BaseScore);
                    if (world.TryGetEconomy(Attacker, out var attacking)) attacking.IncomeScale *= MathF.Sqrt(_waveScale);
                }
                if (_rules.CounterBase) _counterRoster = CounterRoster(world);
                PlanWave(world, 1);
            }
        }

        /// <summary>The defender's base strength the waves were sized by (100: the mid-level mark; 0 when the waves are not scaled).</summary>
        public float BaseScore { get; private set; }

        private float _waveScale = 1f;
        private List<string>? _counterRoster;

        /// <summary>
        /// The swarm drawn against the base (prompt 13 H.7): the towers' worth by what they are good at
        /// (anti-air, anti-armour guns and missiles, machine guns and flame, artillery), and the swarm
        /// weighted away from what they counter: more armour against machine guns, more fast light
        /// vehicles, drones and long guns against anti-armour towers, no aircraft against a sky full of
        /// anti-air, fast raiders against artillery.
        /// </summary>
        private List<string> CounterRoster(SimWorld world)
        {
            float aa = 0f, antiArmour = 0f, guns = 0f, artillery = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Defender || v.Def.Fort is not { Kind: FortKind.Tower } || v.Def.Passive) continue;
                var w = v.Def.Weapon;
                var worth = v.Def.Power;
                if (BaseLoadout.IsAntiAir(world.Catalog, v.Def.Id)) aa += worth;
                if (w.MinRange > 0f) artillery += worth;
                else if (w.AntiArmour || w.Projectile == ProjectileKind.Missile) antiArmour += worth;
                else if (w.DamageType is DamageType.Kinetic or DamageType.Fire || w.Projectile == ProjectileKind.Bullet) guns += worth;
            }
            var total = MathF.Max(1f, aa + antiArmour + guns + artillery);
            var list = new List<string>();
            void Add(string id, float weight)
            {
                if (!world.Catalog.Vehicles.TryGetValue(id, out var def)) return;
                var n = Math.Clamp((int)MathF.Round(weight), 0, 4);
                for (var i = 0; i < n; i++) list.Add(id);
            }
            foreach (var id in _rules.WaveRoster)
            {
                if (!world.Catalog.Vehicles.TryGetValue(id, out var def)) continue;
                var weight = 1f;
                if (def.Armor == ArmorClass.Heavy && !def.Flying) weight += 2f * guns / total - 1f * antiArmour / total;
                if (def.Armor == ArmorClass.Light && def.Speed >= 11f) weight += 2f * antiArmour / total + 1.5f * artillery / total;
                if (def.Weapon.Projectile == ProjectileKind.Drone || def.Weapon.MinRange > 0f) weight += 1.5f * antiArmour / total;
                if (def.Flying) weight -= 2.5f * aa / total;
                Add(id, weight);
            }
            return list.Count > 0 ? list : new List<string>(_rules.WaveRoster);
        }

        private bool Listed(EntityId id)
        {
            foreach (var ring in _defences)
                if (ring.Contains(id)) return true;
            return false;
        }

        /// <summary>
        /// The fortress's gates and wall segments, by the ring they close: the walls' ring or the
        /// keep's (whichever line they stand nearer); and the keep's size, for its shield dome.
        /// </summary>
        private void ClassifyWorks(SimWorld world, IReadOnlyList<float> rings)
        {
            if (Fortress is not { } hq) return;
            var split = rings.Count >= 2 ? (rings[0] + rings[1]) * 0.5f : float.MaxValue;
            Vector2 min = new(float.MaxValue), max = new(float.MinValue);
            foreach (var prop in world.Props)
            {
                if (!prop.IsAlive) continue;
                var gate = prop.Def.Id == _rules.Gate;
                if (!gate && prop.Def.Id != _rules.Wall) continue;
                var ring = _fortress is { Layered: true } f ? Math.Max(2, f.RingOf(prop.Position)) : Chebyshev(prop.Position, hq) >= split ? 2 : 3;
                if (ring == 3)
                {
                    min = Vector2.Min(min, prop.Position);
                    max = Vector2.Max(max, prop.Position);
                }
                if (!gate)
                {
                    _walls.Add((prop.Id, ring));
                    continue;
                }
                // Outward: away from the HQ, square to the wall the gate stands in (on a layered base, the wall's own
                // run: its outer wall crosses the whole map, so the HQ's bearing does not say which wall it is).
                var off = prop.Position - hq;
                var outward = _fortress is { Layered: true }
                    ? prop.Rotation % 180 == 0 ? new Vector2(0f, MathF.Sign(off.Y)) : new Vector2(MathF.Sign(off.X), 0f)
                    : MathF.Abs(off.X) >= MathF.Abs(off.Y) ? new Vector2(MathF.Sign(off.X), 0f) : new Vector2(0f, MathF.Sign(off.Y));
                _gates.Add((prop.Id, ring, outward));
            }
            if (min.X <= max.X)
            {
                DomeCentre = (min + max) * 0.5f;
                DomeRadius = Vector2.Distance(min, max) * 0.5f + 2f;
            }
            else
            {
                DomeCentre = hq;
                DomeRadius = rings.Count >= 2 ? rings[1] + 4f : 30f;
            }
        }

        /// <summary>Which ring a point lies in: 1 outer line, 2 walls, 3 keep.</summary>
        private int RingOf(Vector2 p, IReadOnlyList<float> rings)
        {
            if (_fortress is { Layered: true } layered) return layered.RingOf(p);
            if (Fortress is not { } centre || rings.Count < 2) return 1;
            var d = Chebyshev(p, centre);
            return d > rings[0] ? 1 : d > rings[1] ? 2 : 3;
        }

        private static float Chebyshev(Vector2 a, Vector2 b) => MathF.Max(MathF.Abs(a.X - b.X), MathF.Abs(a.Y - b.Y));

        /// <summary>
        /// Only the current stage's objectives can be hurt; later ones are shielded. The dome keeps
        /// the keep's guns from harm, and silent, while a generator stands.
        /// </summary>
        private void Shield(SimWorld world)
        {
            var glyph = world.Time < _glyphUntil;
            foreach (var id in _relays)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = false;
            foreach (var id in _generators)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = Stage < 2;
            foreach (var id in _targets)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = Stage < 3 || glyph;
            // Under the dome the keep's guns can neither be hurt nor fire out: the fight for the keep comes with stage three.
            foreach (var id in _defences[2])
                if (world.TryGetVehicle(id, out var v))
                {
                    v.Invulnerable = glyph || DomeUp;
                    v.HoldFire = DomeUp;
                }
        }

        private static int Alive(SimWorld world, List<EntityId> props)
        {
            var n = 0;
            foreach (var id in props)
                if (world.TryGetProp(id, out var p) && p.IsAlive) n++;
            return n;
        }

        /// <summary>Share of the whole siege done (0-1): a third per stage.</summary>
        public float Progress(SimWorld world)
        {
            if (Stage >= 4) return 1f;
            float part;
            switch (Stage)
            {
                case 1:
                    part = _relays.Count > 0 ? 1f - Alive(world, _relays) / (float)_relays.Count : 1f;
                    break;
                case 2:
                    part = _generators.Count > 0 ? 1f - Alive(world, _generators) / (float)_generators.Count : 1f;
                    break;
                default:
                    if (_targets.Count == 0)
                    {
                        // No HQ: the fixed defences are the fortress (destroyed ones leave the world's list).
                        int total = 0, standing = 0;
                        foreach (var ring in _defences)
                            foreach (var id in ring)
                            {
                                total++;
                                if (world.TryGetVehicle(id, out var v) && v.IsAlive) standing++;
                            }
                        part = total > 0 ? 1f - standing / (float)total : 0f;
                        break;
                    }
                    float hp = 0f, max = 0f;
                    foreach (var id in _targets)
                        if (world.TryGetProp(id, out var p))
                        {
                            hp += MathF.Max(0f, p.Hp);
                            max += p.MaxHp;
                        }
                    part = max > 0f ? 1f - hp / max : 1f;
                    break;
            }
            return MathF.Min(1f, (Stage - 1 + part) / 3f);
        }

        /// <summary>
        /// What the attacking army should knock down now: the current stage's standing objective
        /// nearest the attacking army (its camp before it has one), so it works along the line
        /// instead of marching back and forth across it.
        /// </summary>
        public EntityId Target(SimWorld world)
        {
            var list = Stage switch { 1 => _relays, 2 => _generators, _ => _targets };
            var from = TryAttackerCentre(world, out var army) ? army : world.TryGetRally(Attacker, out var rally) ? rally : Vector2.Zero;
            var best = EntityId.None;
            var nearest = float.MaxValue;
            foreach (var id in list)
            {
                if (!world.TryGetProp(id, out var p) || !p.IsAlive) continue;
                var d = Vector2.DistanceSquared(p.Position, from);
                if (d >= nearest) continue;
                nearest = d;
                best = id;
            }
            return best;
        }

        // ------------------------------------------------------------------ gates and breaches

        /// <summary>The fortress's gates: each one's prop, the ring it closes (2 walls, 3 keep) and which way is out.</summary>
        public IReadOnlyList<(EntityId id, int ring, Vector2 outward)> Gates => _gates;

        /// <summary>Whether a ring's line has been broken: one of its gates blown in or one of its wall segments down.</summary>
        public bool Breached(SimWorld world, int ring)
        {
            foreach (var (id, r, _) in _gates)
                if (r == ring && (!world.TryGetProp(id, out var g) || !g.IsAlive)) return true;
            foreach (var (id, r) in _walls)
                if (r == ring && (!world.TryGetProp(id, out var w) || !w.IsAlive)) return true;
            return false;
        }

        private bool InsideRing(SimWorld world, Vector2 p, int ring)
        {
            if (_fortress is { Layered: true } layered) return layered.RingOf(p) >= (ring == 2 ? 2 : 3);
            var rings = world.Map.SiegeRings;
            if (Fortress is not { } hq || rings.Count < 2) return true;
            return Chebyshev(p, hq) <= rings[ring == 2 ? 0 : 1];
        }

        /// <summary>
        /// The gate the attack has to blow in first: while the current stage's objective stands
        /// behind a line nobody has broken yet (no gate of it blown, no wall of it down) and the
        /// attacking army is still outside it, the standing gate of that line nearest the army.
        /// </summary>
        public EntityId GateToBreak(SimWorld world)
        {
            if (Stage is < 2 or > 3 || Breached(world, Stage)) return EntityId.None;
            if (Stage == 3 && !(_rules.KeepGateFirst ?? _rules.PlayerDefends)) return EntityId.None;
            var front = TryAttackerCentre(world, out var centre) ? centre : world.TryGetRally(Attacker, out var rally) ? rally : Vector2.Zero;
            if (InsideRing(world, front, Stage)) return EntityId.None;
            var best = EntityId.None;
            var nearest = float.MaxValue;
            foreach (var (id, ring, _) in _gates)
            {
                if (ring != Stage || !world.TryGetProp(id, out var gate) || !gate.IsAlive) continue;
                var d = Vector2.DistanceSquared(gate.Position, front);
                if (d >= nearest) continue;
                nearest = d;
                best = id;
            }
            return best;
        }

        /// <summary>Where the attacking army should go: in front of the gate to blow in, else the current objective.</summary>
        public Vector2? AttackGoal(SimWorld world)
        {
            var gate = GateToBreak(world);
            if (gate.IsValid && world.TryGetProp(gate, out var g))
                foreach (var (id, _, outward) in _gates)
                    if (id == gate) return g.Position + outward * 9f;
            return world.TryGetProp(Target(world), out var objective) ? objective.Position : Fortress;
        }

        /// <summary>What the attacking army should knock down: the gate in its way, else the current objective.</summary>
        public EntityId AttackTarget(SimWorld world)
        {
            var gate = GateToBreak(world);
            return gate.IsValid ? gate : Target(world);
        }

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            RunChain(world);
            if (_finishAt >= 0)
            {
                if (world.Time >= _finishAt) Finish(world, Attacker);
                return;
            }
            if (world.Time >= _nextWave) SendWave(world);
            if (_rules.BreachWave && !BreachSent && _rules.WaveBreachers.Count > 0 && world.Time >= 240.0) SendBreach(world);
            ReleaseWaves(world);
            if (Stage == 1 && Alive(world, _relays) == 0) Advance(world, 2);
            if (Stage == 2 && Alive(world, _generators) == 0) Advance(world, 3);
            if (Stage == 3) KeepEvents(world);
            RunSuperGun(world);
            PayForPads(world);
            WatchWorks(world);
            Watch(world);
            PayBounties(world);
            Brownout(world);
            if (Stage == 3 && (_targets.Count > 0 ? Alive(world, _targets) == 0 : Progress(world) >= 0.999f))
            {
                Fall(world);
                return;
            }
            if (world.Time >= _deadline && !(world.Time < _deadline + _rules.Overtime && Contested(world)))
            {
                Finish(world, Defender);
                return;
            }
            // An attacking player wiped out has lost; an attacking AI always buys more.
            if (_rules.PlayerDefends) return;
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            if (_wipedSince >= 0 && world.Time - _wipedSince > 12.0) Finish(world, EnemyTeam);
        }

        /// <summary>
        /// Every fortress building knocked down pays the attacker on the spot: two to six CP by its
        /// size (a garage, a warehouse), and coins at the end of the battle. Buildings that go up
        /// in the fortress's final collapse pay nothing.
        /// </summary>
        private void PayBounties(SimWorld world)
        {
            for (var i = _bounty.Count - 1; i >= 0; i--)
            {
                if (world.TryGetProp(_bounty[i], out var building) && building.IsAlive) continue;
                _bounty.RemoveAt(i);
                if (building == null) continue;
                var cp = Math.Clamp(MathF.Round(building.Def.MaxHp / 400f), 2f, 6f);
                if (world.TryGetEconomy(Attacker, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + cp);
                BuildingsRazed++;
                world.Emit(SimEvent.BountyPaid(Attacker, building.Def.Id, building.Position, cp));
            }
        }

        /// <summary>Attackers are fighting within 25 m of a live objective (overtime runs while they are).</summary>
        private bool Contested(SimWorld world)
        {
            if (!world.TryGetProp(Target(world), out var objective)) return false;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Attacker && Vector2.Distance(v.Position, objective.Position) < 25f) return true;
            return false;
        }

        private void Advance(SimWorld world, int next)
        {
            var cleared = Stage;
            Stage = next;
            var bonus = _rules.StageBonus.Length >= cleared ? _rules.StageBonus[cleared - 1] : 0f;
            _deadline = Math.Min(_deadline + bonus, world.Time + _rules.MaxBank);
            if (world.TryGetEconomy(Attacker, out var economy)) economy.Cp = MathF.Min(economy.Bank, economy.Cp + _rules.StageCp);
            // The line just taken is lost to the defender: its guns blow up one after another, none
            // is ever flown back in, and the defender falls back on the next with CP to spend.
            Collapse(world, _defences[cleared - 1], 0.25, props: false);
            world.Bases.LoseRing(Defender, cleared);
            var retreat = _rules.RetreatCp.Length >= cleared ? _rules.RetreatCp[cleared - 1] : 0f;
            if (retreat > 0f && world.TryGetEconomy(Defender, out var ours))
            {
                ours.Cp = MathF.Min(ours.Bank, ours.Cp + retreat);
                world.Emit(SimEvent.BountyPaid(Defender, "retreat", Fortress ?? Vector2.Zero, retreat));
            }
            var domeWasUp = DomeUp;
            DomeUp = next <= 2 && Alive(world, _generators) > 0;
            Shield(world);
            if (next == 3) SpawnGuardian(world);
            world.Emit(SimEvent.Stage(next, Fortress ?? Vector2.Zero, Key(next == 2 ? "stage2" : "stage3")));
            if (domeWasUp && !DomeUp) world.Emit(SimEvent.Alert(DomeCentre, Key("dome"), bad: _rules.PlayerDefends));
        }

        /// <summary>The keep's guardian wakes (stage three).</summary>
        private void SpawnGuardian(SimWorld world)
        {
            if (_rules.Guardian == null || Fortress is not { } hq || !world.Catalog.Vehicles.ContainsKey(_rules.Guardian)) return;
            var toward = world.TryGetRally(Attacker, out var rally) ? Vector2.Normalize(rally - hq) : new Vector2(-0.7f, -0.7f);
            world.SpawnVehicle(_rules.Guardian, Defender, RoomFor(world, hq + toward * 12f, world.Catalog.Vehicle(_rules.Guardian)), SimMath.HeadingOf(toward));
        }

        /// <summary>
        /// The open ground nearest <paramref name="at"/> with room all round for a hull this big (the
        /// guardian is 9 m across): it came out in a gap between the HQ, the keep's wall and a tower,
        /// where it could hardly move (prompt 12). Within 24 m; else the point itself.
        /// </summary>
        private static Vector2 RoomFor(SimWorld world, Vector2 at, VehicleDef def)
        {
            var grid = world.Grid;
            var lanes = world.Lanes;
            var room = Math.Max(2, (int)MathF.Ceiling((def.HullRadius - SimWorld.ObstacleClearance) / grid.CellSize) + 1);
            var (cx, cy) = grid.CellOf(at);
            var main = grid.MainRegion;
            for (var ring = 0; ring <= 12; ring++)
            {
                var best = float.MaxValue;
                var spot = at;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue;
                    if (!grid.IsWalkable(x, y) || grid.RegionOf(x, y) != main) continue;
                    var c = grid.CellCenter(x, y);
                    if (lanes.ClearanceAt(c) < room) continue;
                    var d = Vector2.DistanceSquared(c, at);
                    if (d >= best) continue;
                    best = d;
                    spot = c;
                }
                if (best < float.MaxValue) return spot;
            }
            return at;
        }

        /// <summary>
        /// The HQ's last cards, at 75, 50 and 25 % of its health: an artillery barrage on the
        /// attackers, then a six-second shield over the keep while two elites arrive, then a last
        /// stand that has every remaining gun firing faster.
        /// </summary>
        private void KeepEvents(SimWorld world)
        {
            if (!world.TryGetProp(Target(world), out var hq)) return;
            var health = hq.Hp / hq.MaxHp;
            if (_hqPhase == 0 && health < 0.75f)
            {
                _hqPhase = 1;
                if (world.Catalog.TryGetSupport("artillery_barrage", out var barrage) && TryAttackerCentre(world, out var at))
                    world.Strikes.Launch(barrage, Defender, at, at);
                world.Emit(SimEvent.Alert(hq.Position, Key("barrage")));
            }
            else if (_hqPhase == 1 && health < 0.5f)
            {
                _hqPhase = 2;
                _glyphUntil = world.Time + 6.0;
                foreach (var elite in new[] { "elite_mbt", "elite_heavy_tank" })
                    if (world.Catalog.Vehicles.ContainsKey(elite))
                        // (Where it has room: beside the HQ they came down in a pocket and never got out; prompt 12.)
                        world.SpawnVehicle(elite, Defender, RoomFor(world, hq.Position + new Vector2(-8f, -8f), world.Catalog.Vehicle(elite)),
                            SimMath.DegToRad(225f));
                world.Emit(SimEvent.Alert(hq.Position, Key("glyph")));
            }
            else if (_hqPhase == 2 && health < 0.25f)
            {
                _hqPhase = 3;
                world.Emit(SimEvent.Alert(hq.Position, Key("laststand")));
            }
            Shield(world);
        }

        private bool TryAttackerCentre(SimWorld world, out Vector2 centre)
        {
            var sum = Vector2.Zero;
            var n = 0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Attacker || v.Flying || v.Def.Static) continue;
                sum += v.Position;
                n++;
            }
            centre = n > 0 ? sum / n : Vector2.Zero;
            return n > 0;
        }

        /// <summary>
        /// Each generator lost browns out the walls and keep: their guns fire a sixth slower per
        /// generator down; the HQ's last stand has them firing 30 % faster instead.
        /// </summary>
        private void Brownout(SimWorld world)
        {
            var down = _generators.Count - Alive(world, _generators);
            var boost = _hqPhase >= 3 ? 1.3f : MathF.Max(0.5f, 1f - down / 6f);
            for (var ring = 1; ring < 3; ring++)
                foreach (var id in _defences[ring])
                    if (world.TryGetVehicle(id, out var v)) v.FireBoost = boost;
        }

        /// <summary>The HQ is down: the fortress goes up in a chain over four seconds, then the siege is won.</summary>
        private void Fall(SimWorld world)
        {
            Stage = 4;
            DomeUp = false;
            var remaining = new List<EntityId>();
            foreach (var ring in _defences) remaining.AddRange(ring);
            if (SuperGun.IsValid) remaining.Add(SuperGun);
            Collapse(world, remaining, 0.12, props: false);
            Collapse(world, _fortressProps, 0.08, props: true);
            _finishAt = world.Time + 4.5;
            world.Emit(SimEvent.Stage(4, Fortress ?? Vector2.Zero, Key("fallen")));
        }

        // ------------------------------------------------------------------ gates and walls, sirens

        /// <summary>A gate blown in or the first wall of a line down: the fortress's alarm goes (and the news goes out).</summary>
        private void WatchWorks(SimWorld world)
        {
            foreach (var (id, ring, _) in _gates)
            {
                if (_gatesDown.Contains(id) || (world.TryGetProp(id, out var gate) && gate.IsAlive)) continue;
                _gatesDown.Add(id);
                _breachTold[ring] = true;
                world.Emit(SimEvent.Alert(gate?.Position ?? Fortress ?? Vector2.Zero, Key("gate"), bad: _rules.PlayerDefends));
            }
            foreach (var (id, ring) in _walls)
            {
                if (_breachTold[ring] || (world.TryGetProp(id, out var wall) && wall.IsAlive)) continue;
                _breachTold[ring] = true;
                world.Emit(SimEvent.Alert(wall?.Position ?? Fortress ?? Vector2.Zero, Key("breach"), bad: _rules.PlayerDefends));
            }
        }

        /// <summary>At night the fortress's sirens sound when it spots attackers on its ground (at most once a minute).</summary>
        private void Watch(SimWorld world)
        {
            if (!_rules.Night || _fortress == null || world.Time < _spotCheck || world.Time - _spottedAt < 60.0) return;
            _spotCheck = world.Time + 1.0;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Attacker || v.Flying || v.Def.Static || !v.IsVisibleTo(Defender) || !_fortress.Contains(v.Position)) continue;
                _spottedAt = world.Time;
                world.Emit(SimEvent.Alert(v.Position, Key("spotted")));
                return;
            }
        }

        // ------------------------------------------------------------------ the super-gun

        private void SpawnSuperGun(SimWorld world)
        {
            if (_rules.SuperGun == null || _fortress?.SuperGun is not { } at || !world.Catalog.Vehicles.ContainsKey(_rules.SuperGun)) return;
            var gun = world.SpawnVehicle(_rules.SuperGun, Defender, at, _fortress.SuperGunHeading);
            gun.VisibleToMask |= 1 << Attacker;
            SuperGun = gun.Id;
            _superGunAt = gun.Position;
            _superGunFireAt = _rules.SuperGunFirst;
        }

        /// <summary>The fortress's landing pads still to pay for when they fall (prompt 13 F.1).</summary>
        private readonly List<(EntityId id, Vector2 at)> _pads = new();

        /// <summary>A landing pad of the fortress destroyed: the attacker is paid (the defender's aircraft lose their fast rearm).</summary>
        private void PayForPads(SimWorld world)
        {
            for (var i = _pads.Count - 1; i >= 0; i--)
            {
                var (id, at) = _pads[i];
                if (world.TryGetVehicle(id, out var pad) && pad.IsAlive) continue;
                _pads.RemoveAt(i);
                if (_rules.PadCp <= 0f || !world.TryGetEconomy(Attacker, out var economy)) continue;
                economy.Cp = MathF.Min(economy.Bank, economy.Cp + _rules.PadCp);
                world.Emit(SimEvent.BountyPaid(Attacker, "airfield", at, _rules.PadCp));
            }
        }

        /// <summary>
        /// The super-gun fires a huge shell on its countdown at the thickest knot of attackers on the
        /// ground (their camp when they have nobody out); destroyed, it pays the attacker.
        /// </summary>
        private void RunSuperGun(SimWorld world)
        {
            if (!SuperGun.IsValid) return;
            if (!world.TryGetVehicle(SuperGun, out var gun) || !gun.IsAlive)
            {
                SuperGun = EntityId.None;
                SuperGunDown = true;
                _superGunFireAt = double.MaxValue;
                if (_rules.SuperGunCp > 0f && world.TryGetEconomy(Attacker, out var economy))
                {
                    economy.Cp = MathF.Min(economy.Bank, economy.Cp + _rules.SuperGunCp);
                    world.Emit(SimEvent.BountyPaid(Attacker, "super_gun", _superGunAt, _rules.SuperGunCp));
                }
                world.Emit(SimEvent.Alert(_superGunAt, Key("gunDown"), bad: _rules.PlayerDefends));
                return;
            }
            if (world.Time < _superGunFireAt || Stage >= 4) return;
            _superGunFireAt = world.Time + _rules.SuperGunSeconds;
            if (!world.Catalog.TryGetSupport(_rules.SuperGunShell, out var shell)) return;
            var target = SuperGunAim(world);
            if (target == null) return;
            SuperGunShots++;
            world.Strikes.Launch(shell, Defender, target.Value, gun.Position);
            world.Emit(SimEvent.Alert(gun.Position, Key("gunFire"), bad: !_rules.PlayerDefends));
        }

        /// <summary>The attacking ground vehicle with the most attacking value round it (12 m), else their drop zone.</summary>
        private Vector2? SuperGunAim(SimWorld world)
        {
            Vector2? best = null;
            var bestValue = 0f;
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != Attacker || v.Flying || v.Def.Static) continue;
                var value = 0f;
                foreach (var o in world.VehicleList)
                    if (o.IsAlive && o.Team == Attacker && !o.Flying && !o.Def.Static && Vector2.DistanceSquared(o.Position, v.Position) < 144f)
                        value += MathF.Max(1f, o.Def.CpCost);
                if (value <= bestValue) continue;
                bestValue = value;
                best = v.Position;
            }
            if (best != null) return best;
            return world.TryGetRally(Attacker, out var camp) ? camp : null;
        }

        // ------------------------------------------------------------------ the line in

        /// <summary>
        /// When and where the defender's next delivery gets in by the fortress's line: the train
        /// (or aircraft) already on its way if it is not about to stop, else a new one, announced.
        /// Nothing once the walls are lost: the line is in the attackers' hands.
        /// </summary>
        private (double due, Vector2 at, Vector2 along)? NextArrival(SimWorld world)
        {
            if (_fortress?.Arrival is not { } line || Stage >= 3 || line.Path.Count < 2) return null;
            var now = world.Time;
            var along = line.Path[line.Path.Count - 1] - line.Path[line.Path.Count - 2];
            along = along.LengthSquared() > 0.01f ? Vector2.Normalize(along) : Vector2.UnitX;
            if (!double.IsNaN(_arrivalAt) && _arrivalAt - now >= 2.5) return (_arrivalAt, line.Stop, along);
            _arrivalAt = Math.Max(now + _rules.ArrivalLead, _lastArrival + _rules.ArrivalGap);
            _lastArrival = _arrivalAt;
            Arrivals++;
            world.Emit(SimEvent.ArrivalInbound(Defender, line.Kind == ArrivalKind.Rail ? "rail" : "runway", line.Stop, SimMath.Forward(line.Heading),
                (float)(_arrivalAt - now)));
            return (_arrivalAt, line.Stop, along);
        }

        // ------------------------------------------------------------------ waves

        /// <summary>
        /// Draws wave <paramref name="wave"/>: mostly the cheap swarm, growing wave on wave, with a
        /// heavy vehicle for every few waves so far (at most a quarter of it), and from
        /// <see cref="SiegeRules.EliteFrom"/> on more and more of it the elite versions.
        /// </summary>
        private void PlanWave(SimWorld world, int wave)
        {
            _plan.Clear();
            _preview.Clear();
            IReadOnlyList<string> swarm = _counterRoster != null ? _counterRoster : _rules.WaveRoster.Count > 0 ? _rules.WaveRoster
                : world.TryGetEconomy(Attacker, out var own) ? own.Vehicles : Array.Empty<string>();
            if (swarm.Count == 0) return;
            var raw = (_rules.WaveStart + _rules.WaveGrowth * (wave - 1)) * MathF.Pow(1f + _rules.WaveCompound, wave - 1) * _waveScale;
            var count = Math.Min(_rules.WaveMax, (int)MathF.Round(raw));
            var heavies = _rules.WaveHeavy.Count > 0 && _rules.HeavyEvery > 0 ? Math.Min(count / 4, wave / _rules.HeavyEvery) : 0;
            // Siege breakers: bulldozers for the gates and walls, siege guns and long guns that outrange the towers.
            var breakers = _rules.WaveBreachers.Count > 0 && wave >= _rules.BreachFrom ? Math.Min(count / 4, 1 + (wave - _rules.BreachFrom) / Math.Max(1, _rules.BreachEvery)) : 0;
            var offset = _waveRandom.Next(swarm.Count);
            for (var i = 0; i < count - heavies - breakers; i++) _plan.Add(swarm[(offset + i) % swarm.Count]);
            for (var i = 0; i < heavies; i++) _plan.Add(_rules.WaveHeavy[(wave + i) % _rules.WaveHeavy.Count]);
            for (var i = 0; i < breakers; i++) _plan.Add(_rules.WaveBreachers[(wave + i) % _rules.WaveBreachers.Count]);
            var elite = MathF.Min(0.6f, (wave - _rules.EliteFrom + 1) * 0.08f);
            for (var i = 0; i < _plan.Count; i++)
                if (elite > 0f && world.Catalog.EliteVariant(_plan[i]) is { } better && _waveRandom.NextDouble() < elite)
                    _plan[i] = better;
            foreach (var id in _plan)
            {
                var k = _preview.FindIndex(p => p.id == id);
                if (k >= 0) _preview[k] = (id, _preview[k].count + 1);
                else _preview.Add((id, 1));
            }
        }

        /// <summary>
        /// A wave flown in to the attacker's camp on top of what it buys (the one the preview
        /// showed), and the next one drawn. Endless also has the attacker earn a little more after
        /// every wave.
        /// </summary>
        private void SendWave(SimWorld world)
        {
            _nextWave = world.Time + _rules.WaveSeconds;
            if (!world.TryGetRally(Attacker, out var camp) || _plan.Count == 0) return;
            Wave++;
            _landed[Wave] = new List<string>();
            foreach (var id in _plan) _reserve.Enqueue((Wave, id));
            ReleaseWaves(world);
            // Endless: both sides grow each wave, the enemy faster (4 %) than the player (2 %, to +30 %).
            if (_rules.Endless && world.TryGetEconomy(Attacker, out var economy)) economy.IncomeScale *= 1.04f;
            if (_rules.Endless && world.TryGetEconomy(Defender, out var ours) && Wave <= 15) ours.IncomeScale *= (1f + 0.02f * Wave) / (1f + 0.02f * (Wave - 1));
            world.Emit(SimEvent.Alert(camp, Key("wave")));
            PlanWave(world, Wave + 1);
        }

        /// <summary>The extra breaching wave was sent (prompt 13 H.12: a player holding far too easily).</summary>
        public bool BreachSent { get; private set; }

        private void SendBreach(SimWorld world)
        {
            if (!world.TryGetEconomy(Defender, out var ours) || !world.TryGetEconomy(Attacker, out var theirs)) return;
            if (ours.ArmyCp < 14 || ours.ArmyCp < 1.6f * Math.Max(1, theirs.ArmyCp)) return;
            if (!world.TryGetRally(Attacker, out var camp)) return;
            BreachSent = true;
            // Two of every breaker, elite where there is one: a hammer blow at the line.
            foreach (var id in _rules.WaveBreachers)
                for (var k = 0; k < 2; k++) _reserve.Enqueue((Wave, world.Catalog.EliteVariant(id) ?? id));
            ReleaseWaves(world);
            world.Emit(SimEvent.Alert(camp, "assist.breach"));
        }

        /// <summary>Flies in waiting wave vehicles while the attackers alive (and on their way) are under the ceiling.</summary>
        /// <summary>
        /// Prompt 17 B.2: where the attack's reinforcements land on a long battlefield once a ring has fallen (the
        /// fortress's forward drops: before the buffer after stage 1, before the outer wall after stage 2); null before.
        /// </summary>
        public Vector2? ForwardDrop
        {
            get
            {
                if (_fortress is not { Layered: true } f || f.ForwardDrops.Count == 0 || Stage < 2) return null;
                return f.ForwardDrops[Math.Min(Stage - 2, f.ForwardDrops.Count - 1)];
            }
        }

        private void ReleaseWaves(SimWorld world)
        {
            if (_reserve.Count == 0 || !world.TryGetRally(Attacker, out var camp)) return;
            if (ForwardDrop is { } forward) camp = forward;
            for (var i = _inbound.Count - 1; i >= 0; i--)
                if (_inbound[i] <= world.Time) _inbound.RemoveAt(i);
            var alive = _inbound.Count + AttackersAlive(world);
            while (_reserve.Count > 0 && alive < _rules.MaxAlive)
            {
                var (wave, id) = _reserve.Dequeue();
                world.Economy.Airlift(Attacker, id, camp);
                _inbound.Add(world.Time + Economy.EconomySystem.DeliverySeconds + 0.5);
                if (_landed.TryGetValue(wave, out var list)) list.Add(id);
                alive++;
            }
        }

        /// <summary>The attacking side's vehicles in the field (not its fixed defences).</summary>
        public int AttackersAlive(SimWorld world)
        {
            var n = 0;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Attacker && !v.Def.Static && !v.Scripted) n++;
            return n;
        }

        /// <summary>Queues things to blow up one after another, nearest the fortress centre first.</summary>
        private void Collapse(SimWorld world, List<EntityId> ids, double interval, bool props)
        {
            var centre = Fortress ?? Vector2.Zero;
            var order = new List<(float d, EntityId id)>();
            foreach (var id in ids)
            {
                if (props ? world.TryGetProp(id, out var p) && p.IsAlive : world.TryGetVehicle(id, out _))
                {
                    var at = props ? world.TryGetProp(id, out var pp) ? pp.Position : centre
                        : world.TryGetVehicle(id, out var vv) ? vv.Position : centre;
                    order.Add((Vector2.Distance(at, centre), id));
                }
            }
            order.Sort((a, b) => a.d.CompareTo(b.d));
            var start = world.Time + 0.4;
            for (var i = 0; i < order.Count; i++) _chain.Add((start + i * interval, order[i].id, props));
        }

        private void RunChain(SimWorld world)
        {
            for (var i = _chain.Count - 1; i >= 0; i--)
            {
                var (at, id, prop) = _chain[i];
                if (world.Time < at) continue;
                _chain.RemoveAt(i);
                if (prop)
                {
                    if (world.TryGetProp(id, out var p) && p.IsAlive)
                    {
                        p.Invulnerable = false;
                        world.Damage.Apply(p, p.Hp * 10f + 100000f, DamageType.HighExplosive);
                    }
                }
                else if (world.TryGetVehicle(id, out var v) && v.IsAlive)
                {
                    v.Invulnerable = false;
                    world.Damage.Apply(v, v.Hp * 10f + 100000f, DamageType.HighExplosive);
                }
            }
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }

        /// <summary>Device check: the super-gun fires in this many seconds.</summary>
        public void DebugFireSuperGunIn(SimWorld world, float seconds)
        {
            if (SuperGun.IsValid) _superGunFireAt = world.Time + seconds;
        }

        /// <summary>Device check: reinforcements for the fortress, flown in (by its line when it has one).</summary>
        public void DebugReinforce(SimWorld world, params string[] vehicles)
        {
            if (!world.TryGetRally(Defender, out var rally)) return;
            foreach (var id in vehicles) world.Economy.Airlift(Defender, id, rally);
        }
    }

    public sealed partial class BossRushRules
    {
        /// <summary>The bosses, fought one after another.</summary>
        public IReadOnlyList<string> Bosses { get; set; } = new[] { "behemoth", "mega_gunship", "mobile_fortress", "drone_mothership", "silver_bug" };

        /// <summary>
        /// Every kind of boss and its variants (at most three of a kind): the super-heavy tank
        /// (Behemoth, Inferno, Tempest), the gunship (Iron Bird, Spectre), the mobile fortress
        /// (Citadel, Hive, Bastion), the drone mothership, the Silver Bug, and prompt 8's five: the rail
        /// supergun, the Earth Worm, the command airship, the landing hovercraft and the Supreme Commander.
        /// </summary>
        public static readonly IReadOnlyList<string[]> Kinds = new[]
        {
            new[] { "behemoth", "behemoth_inferno", "behemoth_tempest" },
            new[] { "mega_gunship", "sky_fortress" },
            new[] { "mobile_fortress", "fortress_hive", "fortress_bastion" },
            new[] { "drone_mothership" },
            new[] { "silver_bug" },
            new[] { "rail_supergun" },
            new[] { "earth_borer" },
            new[] { "command_airship" },
            new[] { "landing_hovercraft" },
            // Prompt 16: Kessler's Leviathan, on the sea (Boss Rush switches to Lighthouse Bay for it).
            new[] { "leviathan" },
            new[] { "supreme_command" },
            // Prompt 20 H-J: the new main bosses (Kronos on the open-pit mine, Typhon at sea) and the new mini bosses
            // by where they fight (prompt 20 pass 3 reworks the rush round the two ranks).
            new[] { "moloch" },
            new[] { "daedalus" },
            new[] { "kronos" },
            new[] { "typhon" },
            new[] { "behemoth_mk2", "bastion_mk0", "fenrir", "ixion" },
            new[] { "locust", "argus", "icarus_mk0" },
            new[] { "scylla", "caspian" },
        };

        /// <summary>One boss of each kind, in the usual order, the variant drawn by <paramref name="seed"/>.</summary>
        public static IReadOnlyList<string> Roster(int seed) => Roster(seed, null);

        /// <summary>
        /// Prompt 20 C.3: the same with only the bosses <paramref name="allowed"/> keeps (the campaign's
        /// chapters switched on); with every boss allowed it draws exactly as <see cref="Roster(int)"/>.
        /// </summary>
        public static IReadOnlyList<string> Roster(int seed, Func<string, bool>? allowed)
        {
            var random = new System.Random(seed);
            var roster = new List<string>();
            foreach (var kind in KindsWhere(allowed)) roster.Add(kind[random.Next(kind.Length)]);
            return roster;
        }

        /// <summary>The kinds with the variants <paramref name="allowed"/> keeps; a kind left with none is dropped.</summary>
        public static IReadOnlyList<string[]> KindsWhere(Func<string, bool>? allowed)
        {
            if (allowed == null) return Kinds;
            var kinds = new List<string[]>();
            foreach (var kind in Kinds)
            {
                var kept = System.Array.FindAll(kind, id => allowed(id));
                if (kept.Length > 0) kinds.Add(kept.Length == kind.Length ? kind : kept);
            }
            return kinds;
        }

        /// <summary>Every boss Boss Rush may bring (for loading its models ahead).</summary>
        public static IEnumerable<string> Everyone()
        {
            foreach (var kind in Kinds)
                foreach (var id in kind)
                    yield return id;
        }

        /// <summary>
        /// Prompt 16 F: the escorts are the general system's now (balance.json "escorts", the same tables as
        /// in the campaign), smaller here: fewer alive at once, part of each wave's guards, as elites
        /// (<see cref="EscortSettings.For"/>). The mode sets them unless the session already has.
        /// </summary>
        public EscortSettings? EscortSettings { get; set; }

        /// <summary>Seconds between one boss falling and the next arriving.</summary>
        public float Breather { get; set; } = 20f;

        /// <summary>Ten bosses since prompt 8 (was 27 minutes for five); eleven with Leviathan (prompt 16); eighteen with prompt 20's (four main, three mini).</summary>
        public float TimeLimit { get; set; } = 88 * 60f;

        /// <summary>CP handed out when a boss falls.</summary>
        public float Bounty { get; set; } = 15f;

        /// <summary>CP handed out each time the boss drops below 75, 50 and 25 % health (paid during the fight, BTD6 style).</summary>
        public float StepBounty { get; set; }

        /// <summary>CP handed out for each part of the boss broken (prompt 9).</summary>
        public float PartBounty { get; set; } = 2f;

        public SideSetup Player { get; set; } = new() { StartCp = 30f, Income = 1.5f, ArmyCap = 36 };

        /// <summary>Prompt 16: the battlefield a boss that sails is fought on when the rush's own has no sea.</summary>
        public string SeaMap { get; set; } = "lighthousebay";

        /// <summary>The rush's own battlefield (the one chosen), to go back to after a sea boss; null: stay.</summary>
        public string? HomeMap { get; set; }

        /// <summary>Picked up again after a switch of battlefield: the bosses beaten, the seconds used, the army and CP carried over.</summary>
        public BossRushCarry? Resume { get; set; }

        /// <summary>The share of a flagship's fleet that sails with it here (fewer, so the fight stays short).</summary>
        public float FleetShare { get; set; } = 0.5f;
    }

    /// <summary>What Boss Rush carries from one battlefield to the next (prompt 16 D.2): progress, time, army, CP.</summary>
    public sealed partial class BossRushCarry
    {
        /// <summary>The battlefield to go to (a map id, without its version).</summary>
        public string Map { get; set; } = "";

        public int Defeated { get; set; }
        public double TimeUsed { get; set; }
        public float Cp { get; set; }

        /// <summary>The player's vehicles (def, health share), landed again at the drop zone.</summary>
        public List<(string def, float health)> Army { get; } = new();
    }

    /// <summary>
    /// Boss Rush: the campaign's bosses one after another, each with an elite escort, on an open
    /// field. Every boss that falls pays a CP bounty and buys a short breather.
    /// </summary>
    public sealed partial class BossRushMode : IGameMode, IObjectiveMode
    {
        public const int PlayerTeam = 0;
        public const int EnemyTeam = 1;

        private readonly BossRushRules _rules;
        private readonly KillLedger _ledger = new();
        private double _nextBossAt;
        private double _wipedSince = -1;

        public BossRushMode(BossRushRules? rules = null) => _rules = rules ?? new BossRushRules();

        public MatchResult? Result { get; private set; }
        public IReadOnlyList<ObjectiveState> Points => Array.Empty<ObjectiveState>();

        /// <summary>Bosses destroyed so far.</summary>
        public int Defeated { get; private set; }

        public int Total => _rules.Bosses.Count;

        /// <summary>The boss on the field (none during a breather).</summary>
        public EntityId Boss { get; private set; }

        public int Kills => _ledger.Kills(PlayerTeam);
        public int Losses => _ledger.Losses(PlayerTeam);

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)(world.Time + TimeUsed));

        /// <summary>Seconds of the rush played on earlier battlefields (prompt 16's switch).</summary>
        public double TimeUsed { get; private set; }

        /// <summary>The battlefield the rush must go to before its next boss (prompt 16), or null: the session switches and carries on.</summary>
        public BossRushCarry? SwitchTo { get; private set; }

        /// <summary>Sea bosses that got away (no bounty for them).</summary>
        public int Escapes { get; private set; }

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(new SideSetup { StartCp = 0f, Income = 0.01f }.Build(EnemyTeam));
            world.SeaRules.FleetShare = _rules.FleetShare;
            _ledger.Ignore = v => v.Def.Boss || v.Def.Naval != null;
            _nextBossAt = 10.0;
            world.EscortSettings ??= _rules.EscortSettings ?? EscortSettings.For(world.Catalog.EscortRules, "Normal", bossRush: true);
            world.BigAttackSettings ??= BigAttackSettings.For(world.Catalog.BigAttackRules, "Normal");
            if (_rules.Resume is { } resume)
            {
                // Carried over from the last battlefield: the army lands at the drop zone, the bosses and the clock go on.
                Defeated = resume.Defeated;
                TimeUsed = resume.TimeUsed;
                Endless = resume.Endless;
                if (world.TryGetEconomy(PlayerTeam, out var economy)) economy.Cp = MathF.Min(economy.Bank, resume.Cp);
                world.TryGetRally(PlayerTeam, out var rally);
                for (var i = 0; i < resume.Army.Count; i++)
                {
                    var (def, health) = resume.Army[i];
                    if (!world.Catalog.Vehicles.ContainsKey(def)) continue;
                    var angle = i * 2.4f;
                    var v = world.SpawnVehicle(def, PlayerTeam, rally + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (4f + 1.2f * i), SimMath.DegToRad(45f));
                    v.Hp = MathF.Max(1f, v.MaxHp * Math.Clamp(health, 0.05f, 1f));
                }
                _nextBossAt = 6.0;
                HuntSetup(world);
                return;
            }
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            HuntSetup(world);
        }

        /// <summary>Prompt 19: the battlefield a boss is fought on in the rush, or null (any).</summary>
        private static string? ArenaOf(SimWorld world, string id) => world.Catalog.Vehicles.TryGetValue(id, out var def) ? def.Arena : null;

        /// <summary>The battle is on this map (its id is the map's with the mode's suffix: "launchsite_sandbox").</summary>
        private static bool On(SimWorld world, string map) => world.Map.Id == map || world.Map.Id.StartsWith(map + "_", StringComparison.Ordinal);

        /// <summary>The battle is on some boss's own battlefield (to go home from after it).</summary>
        private bool OnAnArena(SimWorld world)
        {
            foreach (var id in _rules.Bosses)
                if (ArenaOf(world, id) is { } arena && On(world, arena)) return true;
            return false;
        }

        /// <summary>A boss that sails (prompt 16) needs a battlefield with a sea.</summary>
        private static bool Sails(SimWorld world, string id) => world.Catalog.Vehicles.TryGetValue(id, out var def) && def.Naval != null;

        /// <summary>What the rush carries to the next battlefield: the bosses beaten, the time used, the army standing, the CP.</summary>
        private BossRushCarry Carry(SimWorld world, string map)
        {
            var carry = new BossRushCarry { Map = map, Defeated = Defeated, TimeUsed = TimeUsed + world.Time, Endless = Endless };
            if (world.TryGetEconomy(PlayerTeam, out var economy)) carry.Cp = economy.Cp;
            carry.Supports.AddRange(_held);
            carry.Paid = PaidBefore;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == PlayerTeam && !v.Def.Static && !v.Scripted && v.Def.CpCost > 0)
                    carry.Army.Add((v.Def.Id, v.Hp / v.MaxHp));
            return carry;
        }

        /// <summary>Health steps of the boss on the field already paid for (75, 50, 25 %).</summary>
        private int _stepsPaid;

        /// <summary>Parts of the boss on the field already paid for (prompt 9: each part pays once, even if it is patched and broken again).</summary>
        private ulong _partsPaid;

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            HuntTick(world);
            if (_rules.StepBounty > 0f && Boss.IsValid && world.TryGetVehicle(Boss, out var hurt) && hurt.IsAlive)
            {
                var steps = Math.Min(3, (int)MathF.Floor((1f - hurt.Hp / hurt.MaxHp) * 4f));
                for (; _stepsPaid < steps; _stepsPaid++)
                    if (world.TryGetEconomy(PlayerTeam, out var paid)) paid.Cp = MathF.Min(paid.Bank, paid.Cp + _rules.StepBounty * _bountyScale);
            }
            if (_rules.PartBounty > 0f && Boss.IsValid && world.TryGetVehicle(Boss, out var parted) && parted.IsAlive)
                for (var i = 0; i < parted.PartCount && i < 64; i++)
                {
                    if (!parted.IsPartBroken(i) || (_partsPaid & (1UL << i)) != 0) continue;
                    _partsPaid |= 1UL << i;
                    if (world.TryGetEconomy(PlayerTeam, out var bounty)) bounty.Cp = MathF.Min(bounty.Bank, bounty.Cp + _rules.PartBounty * _bountyScale);
                }
            if (SwitchTo != null) return;
            var escaped = Boss.IsValid && world.TryGetVehicle(Boss, out var sailed) && sailed.IsAlive && sailed.Escaped;
            if (Boss.IsValid && (escaped || !world.TryGetVehicle(Boss, out var boss) || !boss.IsAlive))
            {
                Boss = EntityId.None;
                var fallen = BossAt(Defeated);
                Defeated++;
                // A ship that got away pays nothing (prompt 16); the rush goes on.
                if (escaped) Escapes++;
                else if (world.TryGetEconomy(PlayerTeam, out var ours)) ours.Cp = MathF.Min(ours.Bank, ours.Cp + _rules.Bounty * _bountyScale);
                // Play-test 6 (DECISIONS 21G): the last boss down, the player may carry on into the endless run.
                if (Defeated >= Total && !Endless)
                {
                    if (!_rules.EndlessOffer)
                    {
                        Finish(world, PlayerTeam);
                        return;
                    }
                    OfferEndless(world);
                }
                _nextBossAt = world.Time + _rules.Breather;
                HuntRest(world, fallen);
            }
            if (EndlessTick(world)) return;
            if (!Boss.IsValid && world.Time >= _nextBossAt && (Defeated < Total || Endless))
            {
                // Prompt 20 N: the rest is over (a support not picked is taken, the checkpoint kept).
                HuntRestOver(world);
                // Prompt 16: a boss that sails is fought at sea; the next one back on the rush's own battlefield.
                // Prompt 19 G.2: a boss with its own battlefield (the Silver Bug's Launch Site) is fought there, as the sea boss at sea.
                var sails = Sails(world, BossAt(Defeated));
                var arena = ArenaOf(world, BossAt(Defeated));
                if (sails && world.Map.Sea == null) SwitchTo = Carry(world, _rules.SeaMap);
                else if (!sails && arena != null && !On(world, arena)) SwitchTo = Carry(world, arena);
                else if (!sails && arena == null && world.Map.Sea != null && _rules.HomeMap != null && _rules.HomeMap != _rules.SeaMap) SwitchTo = Carry(world, _rules.HomeMap);
                else if (!sails && arena == null && _rules.HomeMap != null && !On(world, _rules.HomeMap) && OnAnArena(world)) SwitchTo = Carry(world, _rules.HomeMap);
                else Spawn(world);
                if (SwitchTo != null) return;
            }
            // The endless run is played after the rush was won: however it ends, the rush stays won.
            if (world.Time + TimeUsed >= _rules.TimeLimit && !Endless)
            {
                Finish(world, EnemyTeam);
                return;
            }
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            if (_wipedSince >= 0 && world.Time - _wipedSince > 12.0) Finish(world, Endless ? PlayerTeam : EnemyTeam);
        }

        private void Spawn(SimWorld world)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            var id = BossAt(Defeated);
            var home = world.TryGetRally(PlayerTeam, out var h) ? h : Vector2.Zero;
            var heading = SimMath.HeadingOf(home - rally);
            // Play-test 6 (DECISIONS 21G): a boss that drives a route of this battlefield (a train's line, Kronos's road) starts on it.
            if (world.Catalog.Vehicles.TryGetValue(id, out var routed) && routed.RouteName != null && world.Map.Route(routed.RouteName) is { Count: >= 2 } line)
            {
                rally = line[0];
                heading = SimMath.HeadingOf(line[1] - line[0]);
            }
            // A ship comes in on the far lane, from the end away from the player's camp.
            if (world.Map.Sea is { } sea && Sails(world, id) && sea.Lane("far") is { } far)
            {
                var side = sea.Frame(home).X <= 0f ? 1f : -1f;
                rally = sea.At(side * far.Patrol, far.W);
            }
            HuntRamp(world);
            Boss = world.SpawnVehicle(id, EnemyTeam, rally, heading).Id;
            _stepsPaid = 0;
            _partsPaid = 0;
            // Its escorts come with it from the boss's table (prompt 16 F).
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }
    }
}

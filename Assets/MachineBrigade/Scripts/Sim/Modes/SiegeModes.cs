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

        /// <summary>The fortress guardian that rolls out of the keep when stage 3 begins (null: none).</summary>
        public string? Guardian { get; set; } = "mobile_fortress";

        /// <summary>
        /// The stage the attack starts at (the weekly fortress: rings broken in an earlier attack
        /// this week stay broken). Their objectives and guns are gone; the clock has their bonuses.
        /// </summary>
        public int StartStage { get; set; } = 1;

        /// <summary>CP the attacker gets each time a stage falls.</summary>
        public float StageCp { get; set; } = 20f;

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

        /// <summary>What the waves are made of (empty: the attacker's deck).</summary>
        public IReadOnlyList<string> WaveRoster { get; set; } = Array.Empty<string>();

        /// <summary>The attacking side's camp (an Anchor base at the camp outside the walls); null: a bare HQ.</summary>
        public BaseLoadout? AttackerBase { get; set; }
    }

    /// <summary>
    /// Siege (công thành), in three stages.
    /// <list type="number">
    /// <item><description>Break the outer line: destroy its relay stations.</description></item>
    /// <item><description>Get inside the walls and destroy the shield generators. While any
    /// stands, the HQ is shielded, and each one lost browns out the defences.</description></item>
    /// <item><description>Level the command HQ in the keep. Its guardian boss rolls out, and at
    /// 75, 50 and 25 % health the HQ calls a barrage, raises a shield round the keep with elite
    /// reinforcements, and makes a last stand.</description></item>
    /// </list>
    /// Each stage cleared adds time, pays the attacker CP, and blows up the defences of the ring
    /// just taken, one after another. When the HQ falls, the whole fortress goes up in a chain.
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

        public SiegeMode(SiegeRules? rules = null) => _rules = rules ?? new SiegeRules();

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
            foreach (var prop in world.Props)
            {
                if (!prop.IsAlive) continue;
                if (prop.Def.Id == _rules.Target)
                {
                    _targets.Add(prop.Id);
                    if (_rules.Hardening > 1f) prop.Harden(_rules.Hardening);
                    Fortress ??= prop.Position;
                }
                else if (prop.Def.Id == _rules.Relay) _relays.Add(prop.Id);
                else if (prop.Def.Id == _rules.Generator) _generators.Add(prop.Id);
            }
            if (Fortress == null && world.TryGetRally(Defender, out var rally)) Fortress = rally;
            var rings = world.Map.SiegeRings;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == Defender && v.Def.Static)
                {
                    _defences[RingOf(v.Position, rings) - 1].Add(v.Id);
                    // The attacker comes with the fortress plans: every gun is on the map from the start.
                    v.VisibleToMask |= 1 << Attacker;
                }
            // Everything built into the fortress goes up with it at the end.
            if (Fortress is { } centre && rings.Count > 0)
                foreach (var prop in world.Props)
                    if (prop.IsAlive && prop.Def.BlocksMovement && !prop.Def.Indestructible && Chebyshev(prop.Position, centre) <= rings[0] + 4f)
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
                Stage++;
                if (Stage == 3) SpawnGuardian(world);
            }
            _deadline = _rules.Endless ? double.MaxValue : _rules.StartSeconds;
            _nextWave = _rules.WaveSeconds > 0f ? _rules.WaveSeconds * 0.75f : double.MaxValue;
            for (var skipped = 1; skipped < Stage && skipped <= _rules.StageBonus.Length; skipped++) _deadline += _rules.StageBonus[skipped - 1];
            Shield(world);
            // The attacker's own camp outside the walls (the map's side 0): its HQ and towers.
            if (world.Map.BaseOf(0) != null && world.Catalog.Vehicles.ContainsKey(world.Catalog.Base.HqId))
                world.Bases.Establish(Attacker, _rules.AttackerBase ?? BaseLoadout.HqOnly(), Content.BaseRole.Anchor, siteTeam: 0);
        }

        /// <summary>Which ring a point lies in: 1 outer line, 2 walls, 3 keep.</summary>
        private int RingOf(Vector2 p, IReadOnlyList<float> rings)
        {
            if (Fortress is not { } centre || rings.Count < 2) return 1;
            var d = Chebyshev(p, centre);
            return d > rings[0] ? 1 : d > rings[1] ? 2 : 3;
        }

        private static float Chebyshev(Vector2 a, Vector2 b) => MathF.Max(MathF.Abs(a.X - b.X), MathF.Abs(a.Y - b.Y));

        /// <summary>Only the current stage's objectives can be hurt; later ones are shielded.</summary>
        private void Shield(SimWorld world)
        {
            var glyph = world.Time < _glyphUntil;
            foreach (var id in _relays)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = false;
            foreach (var id in _generators)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = Stage < 2;
            foreach (var id in _targets)
                if (world.TryGetProp(id, out var p)) p.Invulnerable = Stage < 3 || glyph;
            foreach (var id in _defences[2])
                if (world.TryGetVehicle(id, out var v)) v.Invulnerable = glyph;
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

        /// <summary>What the attacking army should knock down now: the current stage's nearest standing objective.</summary>
        public EntityId Target(SimWorld world)
        {
            var list = Stage switch { 1 => _relays, 2 => _generators, _ => _targets };
            var from = world.TryGetRally(Attacker, out var rally) ? rally : Vector2.Zero;
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
            if (Stage == 1 && Alive(world, _relays) == 0) Advance(world, 2);
            if (Stage == 2 && Alive(world, _generators) == 0) Advance(world, 3);
            if (Stage == 3) KeepEvents(world);
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
            // The ring just taken is lost to the defender: its guns blow up one after another.
            Collapse(world, _defences[cleared - 1], 0.25, props: false);
            Shield(world);
            if (next == 3) SpawnGuardian(world);
            world.Emit(SimEvent.Stage(next, Fortress ?? Vector2.Zero, Key(next == 2 ? "stage2" : "stage3")));
        }

        /// <summary>The keep's guardian wakes (stage three).</summary>
        private void SpawnGuardian(SimWorld world)
        {
            if (_rules.Guardian == null || Fortress is not { } hq || !world.Catalog.Vehicles.ContainsKey(_rules.Guardian)) return;
            var toward = world.TryGetRally(Attacker, out var rally) ? Vector2.Normalize(rally - hq) : new Vector2(-0.7f, -0.7f);
            world.SpawnVehicle(_rules.Guardian, Defender, hq + toward * 12f, SimMath.HeadingOf(toward));
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
                        world.SpawnVehicle(elite, Defender, hq.Position + new Vector2(-8f, -8f), SimMath.DegToRad(225f));
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
                if (!v.IsAlive || v.Team != Attacker || v.Flying) continue;
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
            var remaining = new List<EntityId>();
            foreach (var ring in _defences) remaining.AddRange(ring);
            Collapse(world, remaining, 0.12, props: false);
            Collapse(world, _fortressProps, 0.08, props: true);
            _finishAt = world.Time + 4.5;
            world.Emit(SimEvent.Stage(4, Fortress ?? Vector2.Zero, Key("fallen")));
        }

        /// <summary>
        /// A wave flown in to the attacker's camp on top of what it buys: bigger each time, and
        /// from the sixth on more and more of it the elite versions. Endless also has the attacker
        /// earn a little more after every wave.
        /// </summary>
        private void SendWave(SimWorld world)
        {
            _nextWave = world.Time + _rules.WaveSeconds;
            if (!world.TryGetRally(Attacker, out var camp)) return;
            var roster = _rules.WaveRoster.Count > 0 ? _rules.WaveRoster
                : world.TryGetEconomy(Attacker, out var own) ? own.Vehicles : Array.Empty<string>();
            if (roster.Count == 0) return;
            Wave++;
            var count = Math.Min(12, 2 + Wave);
            var elite = MathF.Min(0.6f, (Wave - 5) * 0.08f);
            for (var i = 0; i < count; i++)
            {
                var id = roster[(Wave * 3 + i * 5) % roster.Count];
                if (elite > 0f && world.Catalog.EliteVariant(id) is { } better && world.Random.NextDouble() < elite) id = better;
                world.Economy.Airlift(Attacker, id, camp);
            }
            // Endless: both sides grow each wave, the enemy faster (4 %) than the player (2 %, to +30 %).
            if (_rules.Endless && world.TryGetEconomy(Attacker, out var economy)) economy.IncomeScale *= 1.04f;
            if (_rules.Endless && world.TryGetEconomy(Defender, out var ours) && Wave <= 15) ours.IncomeScale *= (1f + 0.02f * Wave) / (1f + 0.02f * (Wave - 1));
            world.Emit(SimEvent.Alert(camp, Key("wave")));
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
    }

    public sealed class BossRushRules
    {
        /// <summary>The bosses, fought one after another.</summary>
        public IReadOnlyList<string> Bosses { get; set; } = new[] { "behemoth", "mega_gunship", "mobile_fortress", "drone_mothership", "silver_bug" };

        /// <summary>
        /// Every kind of boss and its variants (at most three of a kind): the super-heavy tank
        /// (Behemoth, Inferno, Tempest), the gunship (Iron Bird, Spectre), the mobile fortress
        /// (Citadel, Hive, Bastion), the drone mothership and the Silver Bug.
        /// </summary>
        public static readonly IReadOnlyList<string[]> Kinds = new[]
        {
            new[] { "behemoth", "behemoth_inferno", "behemoth_tempest" },
            new[] { "mega_gunship", "sky_fortress" },
            new[] { "mobile_fortress", "fortress_hive", "fortress_bastion" },
            new[] { "drone_mothership" },
            new[] { "silver_bug" },
        };

        /// <summary>One boss of each kind, in the usual order, the variant drawn by <paramref name="seed"/>.</summary>
        public static IReadOnlyList<string> Roster(int seed)
        {
            var random = new System.Random(seed);
            var roster = new List<string>();
            foreach (var kind in Kinds) roster.Add(kind[random.Next(kind.Length)]);
            return roster;
        }

        /// <summary>Every boss Boss Rush may bring (for loading its models ahead).</summary>
        public static IEnumerable<string> Everyone()
        {
            foreach (var kind in Kinds)
                foreach (var id in kind)
                    yield return id;
        }

        /// <summary>Elite escorts that come with each boss, by boss.</summary>
        public IReadOnlyDictionary<string, string[]> Escorts { get; set; } = new Dictionary<string, string[]>
        {
            ["behemoth"] = new[] { "elite_mbt", "elite_mbt" },
            ["mega_gunship"] = new[] { "elite_attack_helicopter", "elite_attack_helicopter" },
            ["mobile_fortress"] = new[] { "elite_heavy_tank", "elite_aa", "elite_mlrs" },
            ["drone_mothership"] = new[] { "elite_aa", "elite_apc", "elite_tank_destroyer" },
            ["silver_bug"] = new[] { "elite_aa", "elite_attack_helicopter", "elite_heavy_tank" },
            ["behemoth_inferno"] = new[] { "elite_heavy_tank", "elite_heavy_tank" },
            ["behemoth_tempest"] = new[] { "elite_tank_destroyer", "elite_tank_destroyer" },
            ["sky_fortress"] = new[] { "elite_attack_helicopter", "elite_attack_helicopter" },
            ["fortress_hive"] = new[] { "elite_aa", "elite_apc" },
            ["fortress_bastion"] = new[] { "elite_heavy_tank", "elite_mlrs" },
        };

        /// <summary>Seconds between one boss falling and the next arriving.</summary>
        public float Breather { get; set; } = 20f;

        public float TimeLimit { get; set; } = 27 * 60f;

        /// <summary>CP handed out when a boss falls.</summary>
        public float Bounty { get; set; } = 15f;

        /// <summary>CP handed out each time the boss drops below 75, 50 and 25 % health (paid during the fight, BTD6 style).</summary>
        public float StepBounty { get; set; }

        public SideSetup Player { get; set; } = new() { StartCp = 30f, Income = 1.5f, ArmyCap = 36 };
    }

    /// <summary>
    /// Boss Rush: the campaign's bosses one after another, each with an elite escort, on an open
    /// field. Every boss that falls pays a CP bounty and buys a short breather.
    /// </summary>
    public sealed class BossRushMode : IGameMode, IObjectiveMode
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

        public float SecondsLeft(SimWorld world) => MathF.Max(0f, _rules.TimeLimit - (float)world.Time);

        public void Setup(SimWorld world)
        {
            world.EnableEconomy(_rules.Player.Build(PlayerTeam));
            world.EnableEconomy(new SideSetup { StartCp = 0f, Income = 0.01f }.Build(EnemyTeam));
            foreach (var unit in world.Map.Units) world.SpawnVehicle(unit.DefId, unit.Team, unit.Position, unit.Heading);
            _ledger.Ignore = v => v.Def.Boss;
            _nextBossAt = 10.0;
        }

        /// <summary>Health steps of the boss on the field already paid for (75, 50, 25 %).</summary>
        private int _stepsPaid;

        public void Tick(SimWorld world, float dt)
        {
            if (Result != null) return;
            _ledger.Update(world);
            if (_rules.StepBounty > 0f && Boss.IsValid && world.TryGetVehicle(Boss, out var hurt) && hurt.IsAlive)
            {
                var steps = Math.Min(3, (int)MathF.Floor((1f - hurt.Hp / hurt.MaxHp) * 4f));
                for (; _stepsPaid < steps; _stepsPaid++)
                    if (world.TryGetEconomy(PlayerTeam, out var paid)) paid.Cp = MathF.Min(paid.Bank, paid.Cp + _rules.StepBounty);
            }
            if (Boss.IsValid && (!world.TryGetVehicle(Boss, out var boss) || !boss.IsAlive))
            {
                Boss = EntityId.None;
                Defeated++;
                if (world.TryGetEconomy(PlayerTeam, out var ours)) ours.Cp = MathF.Min(ours.Bank, ours.Cp + _rules.Bounty);
                if (Defeated >= Total)
                {
                    Finish(world, PlayerTeam);
                    return;
                }
                _nextBossAt = world.Time + _rules.Breather;
            }
            if (!Boss.IsValid && world.Time >= _nextBossAt && Defeated < Total) Spawn(world);
            if (world.Time >= _rules.TimeLimit)
            {
                Finish(world, EnemyTeam);
                return;
            }
            var wiped = world.TryGetEconomy(PlayerTeam, out var economy) && economy.ArmyCp == 0 && world.Time > 5.0;
            _wipedSince = wiped ? (_wipedSince < 0 ? world.Time : _wipedSince) : -1;
            if (_wipedSince >= 0 && world.Time - _wipedSince > 12.0) Finish(world, EnemyTeam);
        }

        private void Spawn(SimWorld world)
        {
            if (!world.TryGetRally(EnemyTeam, out var rally)) return;
            var id = _rules.Bosses[Defeated];
            var home = world.TryGetRally(PlayerTeam, out var h) ? h : Vector2.Zero;
            var heading = SimMath.HeadingOf(home - rally);
            Boss = world.SpawnVehicle(id, EnemyTeam, rally, heading).Id;
            _stepsPaid = 0;
            if (!_rules.Escorts.TryGetValue(id, out var escorts)) return;
            for (var i = 0; i < escorts.Length; i++)
            {
                var angle = heading + (i - (escorts.Length - 1) * 0.5f) * 0.7f;
                world.SpawnVehicle(escorts[i], EnemyTeam, world.ClampToMap(rally + SimMath.Forward(angle) * 14f), heading);
            }
        }

        private void Finish(SimWorld world, int winner)
        {
            Result = new MatchResult(winner);
            world.IsOver = true;
        }
    }
}

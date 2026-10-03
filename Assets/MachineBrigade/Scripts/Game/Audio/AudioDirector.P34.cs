using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Fix pass L7 (in place of prompt 34 L6's seven steps): the priority a voice is cut by when the 24 effect voices run out,
    /// higher wins: warnings > a boss's or a 406 mm / super weapon's sound > blasts near the view > shots near the view >
    /// far blasts > far shots > small arms (their clusters) > the environment.
    /// </summary>
    internal static class SoundPriority
    {
        /// <summary>The environment (debris, ambience).</summary>
        public const int Ambient = 10;

        /// <summary>Small arms fired over and over, and their clusters.</summary>
        public const int SmallArms = 20;

        /// <summary>A shot far from the view.</summary>
        public const int FarShot = 25;

        /// <summary>A blast (a landing, a wreck) far from the view.</summary>
        public const int FarBlast = 30;

        /// <summary>A shot near the view.</summary>
        public const int NearShot = 40;

        /// <summary>A blast near the view.</summary>
        public const int NearBlast = 50;

        /// <summary>A boss's, a 406 mm's or a super weapon's sound.</summary>
        public const int Boss = 60;

        /// <summary>Gameplay warnings (the whistles of incoming fire; the alarms play on their own source).</summary>
        public const int Warning = 70;

        /// <summary>The old banks' priorities (0-5) on this scale; 7 and up is a warning.</summary>
        public static int Steps(int old) => old >= 7 ? Warning : old switch
        {
            <= 0 => Ambient,
            1 or 2 => SmallArms,
            3 => NearShot,
            _ => NearBlast,
        };

        /// <summary>A sound's priority: by its size, a boss's, a blast or a shot, near the view or not.</summary>
        public static int For(SizeClass size, bool boss, bool blast, bool near)
        {
            if (boss || size >= SizeClass.S406) return Boss;
            if (blast) return near ? NearBlast : FarBlast;
            if (size == SizeClass.S0) return SmallArms;
            return near ? NearShot : FarShot;
        }
    }

    public sealed partial class AudioDirector
    {
        /// <summary>Effect voices at once before the least important is cut (of the pool's 32; the rest wait for warnings and boss sounds).</summary>
        internal const int EffectVoices = 24;

        /// <summary>A source off the screen plays this much quieter (0.6 in prompt 34 L6: part of the lost punch, Docs/audio/diagnosis.md).</summary>
        internal const float OffScreenGain = 0.85f;

        /// <summary>Small arms within this of each other (m) inside <see cref="ClusterWindow"/> (s) count as one firefight.</summary>
        internal const float ClusterRadius = 20f, ClusterWindow = 0.5f;

        /// <summary>From this many small-arms shots in a firefight, it is heard as one cluster sound, not a voice a shot.</summary>
        internal const int ClusterFrom = 3;

        /// <summary>A sound counts as near the view inside this share of the hearing reach.</summary>
        internal const float NearShare = 0.45f;

        /// <summary>The Effects compressor's attack and release (s).</summary>
        internal const float CompressorAttack = 0.03f, CompressorRelease = 0.3f;

        /// <summary>The groups' volumes (Settings, under the master volume).</summary>
        private static float Fx => SoundLibrary.Gain(AudioGroup.Effects);
        private static float Talk => SoundLibrary.Gain(AudioGroup.Dialogue);
        private static float Ui => SoundLibrary.Gain(AudioGroup.UI);

        /// <summary>The library's banks by name (Resources/Audio/sfx/name), from Tools/sfx/build_sfx.py.</summary>
        private readonly Dictionary<string, Bank> _tierBanks = new();

        /// <summary>Banks loaded with their units (the map's group): "naval" (ship horn, engines, wrecks), "rail" (train horn, rails).</summary>
        private readonly HashSet<string> _groups = new();

        private readonly HashSet<string> _bossWeapons = new();
        private readonly HashSet<EntityId> _salvoShips = new();
        /// <summary>Falling aircraft: from when their crash is due (the Sim's fall time on the loss event).</summary>
        private readonly Dictionary<EntityId, float> _crashing = new();
        private readonly List<(float at, Vector2 where, EntityId who)> _smallArms = new();

        /// <summary>Play-test 12: when each shooter's burst segment ends (s), by shooter and weapon.</summary>
        private readonly Dictionary<(EntityId, string), float> _bursts = new();

        /// <summary>Play-test 12: the next time an incoming missile's hiss may be scheduled (one in <see cref="HissGap"/> s).</summary>
        private float _nextHiss;
        private float _clusterUntil = -10f;
        private Vector2 _clusterAt;
        private AudioSource _rails, _engines, _engTracked, _engWheeled, _engHeavy;
        private readonly Dictionary<EntityId, float> _nextHorn = new();

        /// <summary>Fix pass L7: the match-wide cap on metal hits.</summary>
        private readonly MetalCap _metal = new();

        /// <summary>Fix pass L7: every unit seen spawning, by id (a killing round's impact comes after its loss event).</summary>
        private readonly Dictionary<EntityId, VehicleDef> _unitDefs = new();

        /// <summary>The views (from the last <see cref="Tick"/>): what a round struck, its heading and armour.</summary>
        private ViewRegistry _views;

        /// <summary>Fix pass L7: each library clip's RMS envelope (50 Hz), for the Effects compressor.</summary>
        private Dictionary<string, float[]> _envelopes = new();

        /// <summary>The Effects compressor's gain now (1: no reduction).</summary>
        private float _busGain = 1f;

        private EffectsLimiter _limiter;
        private bool _ownsLimiter;
        private int _limiterTries;

        /// <summary>The Effects compressor's gain now (1: none), for the stress check.</summary>
        internal float EffectsGain => _busGain;

        private void AddTierBanks()
        {
            var env = Resources.Load<TextAsset>("Audio/" + SoundLibrary.Folder + "envelopes");
            if (env != null) _envelopes = SoundLibrary.ParseEnvelopes(env.text);
            // The level of each size is in its file (Tools/sfx/build_sfx.py); the banks only set the voices and cooldowns.
            int[] shotVoices = { 4, 4, 4, 3, 2, 2, 2 };
            string[] shots = { "shot_s0", "shot_s1", "shot_s2", "shot_s3", "shot_s4", "shot_s406", "shot_super" };
            for (var i = 0; i < shots.Length; i++)
                TierBank(shots[i], 1f, shotVoices[i], i <= 1 ? 0.06f : 0.05f + 0.01f * i, i == 0 ? SoundPriority.SmallArms : SoundPriority.NearShot,
                    light: i <= 1);
            // Play-test 12: the launches by family, the 57 mm autocannon, the rapid-fire bursts (one a shooter, never cut
            // mid-burst, a small pitch spread so the rhythm stays the gun's) and the incoming missile's hiss.
            foreach (var name in new[] { "launch_atgm", "launch_sam", "launch_s2", "launch_s3", "launch_big", "launch_cruise" })
                TierBank(name, 1f, name is "launch_big" or "launch_cruise" ? 2 : 3, 0.06f, SoundPriority.NearShot);
            TierBank("shot_ac57", 1f, 3, 0.07f, SoundPriority.NearShot, light: true);
            foreach (var burst in SoundLibrary.Bursts)
            {
                TierBank(burst.Bank, 1f, BurstVoices, 0f, burst.Size == SizeClass.S0 ? SoundPriority.SmallArms : SoundPriority.NearShot, light: true);
                if (!_tierBanks.TryGetValue(burst.Bank, out var made)) continue;
                made.NoSteal = true;
                made.PitchSpread = 0.03f;
            }
            TierBank("missile_hiss", 1f, 2, 0.25f, SoundPriority.FarShot, light: true);
            string[] blasts = { "blast_he_s1", "blast_he_s2", "blast_he_s3", "blast_he_s4", "blast_bomb", "blast_he_s406", "blast_super" };
            for (var i = 0; i < blasts.Length; i++)
                TierBank(blasts[i], 1f, i >= 5 ? 2 : i >= 2 ? 3 : 4, 0.04f + 0.01f * i, SoundPriority.NearBlast, delayed: true);
            foreach (var name in new[] { "blast_thermo_s3", "blast_thermo_s4" }) TierBank(name, 1f, 2, 0.1f, SoundPriority.NearBlast, delayed: true);
            foreach (var name in new[] { "blast_heat_s2", "blast_heat_s3" }) TierBank(name, 1f, 3, 0.05f, SoundPriority.NearBlast);
            foreach (var name in new[] { "blast_air_s1", "blast_air_s2", "blast_air_s3" }) TierBank(name, 1f, 3, 0.06f, SoundPriority.FarBlast, light: true);
            foreach (var name in new[] { "hit_ground_light", "hit_concrete_light", "hit_pen_light" }) TierBank(name, 1f, 3, 0.05f, SoundPriority.SmallArms, light: true);
            foreach (var name in new[] { "hit_ground_heavy", "hit_concrete_heavy", "hit_pen_heavy" }) TierBank(name, 1f, 3, 0.05f, SoundPriority.NearShot);
            TierBank("hit_metal_light", 1f, 2, MetalCap.MinGap, SoundPriority.SmallArms, light: true);
            TierBank("hit_metal_heavy", 1f, 2, MetalCap.MinGap, SoundPriority.NearShot);
            TierBank("smallarms_cluster", 1f, 2, 0.35f, SoundPriority.SmallArms, light: true);
            foreach (var kind in new[] { "tank", "wheeled", "truck", "artillery", "aircraft", "heli", "drone" })
                TierBank("wreck_" + kind, 1f, 3, 0.1f, SoundPriority.NearBlast, delayed: true);
            TierBank("crash_fall", 1f, 2, 0.3f, SoundPriority.NearShot);
            TierBank("crash_impact", 1f, 2, 0.1f, SoundPriority.NearBlast, delayed: true);
            TierBank("flare_pop", 1f, 2, 0.15f, SoundPriority.NearShot);
            TierBank("warn_whistle_big", 1f, 2, 0.3f, SoundPriority.Warning);
            foreach (var def in _catalog.Vehicles.Values)
            {
                if (!def.Boss) continue;
                foreach (var mount in def.Mounts) _bossWeapons.Add(mount.Weapon.Id);
            }
            _engTracked = TierLoop("Engines (tracked)", "engine_tracked");
            _engWheeled = TierLoop("Engines (wheeled)", "engine_wheeled");
            _engHeavy = TierLoop("Engines (heavy)", "engine_heavy");
            AttachLimiter();
        }

        /// <summary>A library bank, when its clips are there (built and imported); without them the old banks play.</summary>
        private void TierBank(string name, float volume, int voices, float cooldown, int priority, bool light = false, bool delayed = false)
        {
            var clips = Recorded(SoundLibrary.Folder + name);
            if (clips == null) return;
            _tierBanks[name] = new Bank
            {
                Clips = clips, Volume = volume, MaxVoices = voices, Cooldown = cooldown, Priority = priority, Light = light, Delayed = delayed,
            };
        }

        /// <summary>
        /// Loads a map group's banks the first time one of its units shows up: a map with no ships or trains never loads their
        /// sounds.
        /// </summary>
        private void LoadGroup(string group)
        {
            if (!_groups.Add(group)) return;
            if (group == "naval")
            {
                TierBank("ship_horn", 0.8f, 1, 10f, SoundPriority.NearShot);
                TierBank("wreck_ship", 1f, 2, 0.2f, SoundPriority.Boss, delayed: true);
                _engines = TierLoop("Ship Engines", "ship_engine");
            }
            else if (group == "rail")
            {
                TierBank("train_horn", 0.8f, 1, 8f, SoundPriority.NearShot);
                _rails = TierLoop("Rails", "train_rails");
            }
            foreach (var name in group == "naval" ? new[] { "ship_horn", "wreck_ship" } : new[] { "train_horn" })
                if (_tierBanks.TryGetValue(name, out var bank))
                    foreach (var clip in bank.Clips)
                        Load(clip);
        }

        private AudioSource TierLoop(string name, string folder)
        {
            var clips = Recorded(SoundLibrary.Folder + folder);
            if (clips == null) return null;
            var source = NewSource(name);
            source.clip = clips[0];
            source.loop = true;
            source.volume = 0f;
            Load(source.clip);
            return source;
        }

        private bool Near(Vector2 at) => Vector3.Distance(new Vector3(at.X, 0f, at.Y), Focus) < Reach(0f) * NearShare;

        private int PriorityOf(WeaponDef weapon, Vector2 at, bool blast) =>
            weapon == null ? -1 : SoundPriority.For(SoundLibrary.SizeOf(weapon), _bossWeapons.Contains(weapon.Id), blast, Near(at));

        /// <summary>The bank a shot plays (null: the old categories).</summary>
        internal static string ShotBank(WeaponDef weapon) => SoundLibrary.ShotBank(weapon);

        /// <summary>The blast a round's landing plays on the ground (null: a round without a blast, or the old categories).</summary>
        internal static string ImpactBank(WeaponDef round) => SoundLibrary.BlastBank(round);

        /// <summary>The wreck bank of a class (null: none, the old blast plays).</summary>
        internal static string WreckBank(WreckClass c) => c switch
        {
            WreckClass.Tank or WreckClass.Train => "wreck_tank",
            WreckClass.Wheeled => "wreck_wheeled",
            WreckClass.Truck => "wreck_truck",
            WreckClass.Artillery => "wreck_artillery",
            WreckClass.Fighter or WreckClass.BigAircraft => "wreck_aircraft",
            WreckClass.Helicopter => "wreck_heli",
            WreckClass.Ship => "wreck_ship",
            WreckClass.Drone => "wreck_drone",
            _ => null,
        };

        /// <summary>A small-arms round: the T0-T1 bullets that fire in streams (not flak, not a railgun's slug).</summary>
        internal static bool SmallArms(WeaponDef weapon) =>
            weapon != null && weapon.Tier <= 1 && weapon.Projectile == ProjectileKind.Bullet && weapon.DamageType != DamageType.Fragmentation &&
            !weapon.Beam && weapon.Charge <= 0f;

        /// <summary>Play-test 12: voices a burst bank may hold (one burst each: a firefight of more is the cluster's).</summary>
        internal const int BurstVoices = 3;

        /// <summary>Play-test 12: a shooter's next burst segment may start this early (s; the Sim's events come on its 20 Hz tick).</summary>
        internal const float BurstSlack = 0.02f;

        /// <summary>Play-test 12: an incoming missile's hiss lasts this long (s, the clip) and ends at the landing.</summary>
        internal const float HissLead = 0.5f;

        /// <summary>Play-test 12: one incoming hiss at most in this many seconds (a rocket salvo hisses once; the whistles keep their queue).</summary>
        internal const float HissGap = 0.3f;

        /// <summary>
        /// A shot: its sound by size at its priority, carrying farther the bigger it is; machine guns in a firefight as one
        /// cluster; play-test 12: a rapid-fire gun as its burst (one segment a shooter at the gun's own rate), not a clip a round.
        /// </summary>
        private void Shot(in SimEvent e, WeaponDef weapon)
        {
            var priority = PriorityOf(weapon, e.Position, false);
            if (SmallArms(weapon) && SoundLibrary.SizeOf(weapon) == SizeClass.S0 && Clustered(e.Position, e.Entity)) return;
            var burstName = SoundLibrary.BurstBank(weapon, out var burstPitch, out var segment);
            if (burstName != null && _tierBanks.TryGetValue(burstName, out var burstBank))
            {
                var now = Time.unscaledTime;
                var key = (e.Entity, weapon.Id);
                if (_bursts.TryGetValue(key, out var until) && now < until - BurstSlack) return;
                if (_bursts.Count > 256) _bursts.Clear();
                _bursts[key] = now + segment;
                Play(burstBank, e.Position, 1f, SoundLibrary.Carry(SoundLibrary.SizeOf(weapon)), priority, burstPitch);
                return;
            }
            var name = ShotBank(weapon);
            if (name != null && _tierBanks.TryGetValue(name, out var bank)) Play(bank, e.Position, 1f, SoundLibrary.Carry(SoundLibrary.SizeOf(weapon)), priority);
            else Play(_banks[WeaponSound(weapon)], e.Position, 1f, 0f, priority);
        }

        /// <summary>
        /// Machine guns: when <see cref="ClusterFrom"/> or more shooters fire within <see cref="ClusterRadius"/> of each other
        /// inside <see cref="ClusterWindow"/>, the firefight is one cluster sound played now and then, and their shots take no
        /// voice of their own. Play-test 12: counted by shooter (one machine gun is its own burst, not a firefight). True when
        /// the shot was taken into a cluster.
        /// </summary>
        private bool Clustered(Vector2 at, EntityId who)
        {
            if (!_tierBanks.TryGetValue("smallarms_cluster", out var cluster)) return false;
            var now = Time.unscaledTime;
            var others = 0;
            var centre = at;
            var listed = false;
            for (var i = _smallArms.Count - 1; i >= 0; i--)
            {
                var (when, where, shooter) = _smallArms[i];
                if (now - when > ClusterWindow)
                {
                    _smallArms.RemoveAt(i);
                    continue;
                }
                if (shooter == who)
                {
                    _smallArms[i] = (now, at, who);
                    listed = true;
                    continue;
                }
                if (Vector2.Distance(where, at) > ClusterRadius) continue;
                others++;
                centre += where;
            }
            if (!listed && _smallArms.Count < 64) _smallArms.Add((now, at, who));
            if (others + 1 < ClusterFrom) return false;
            if (now >= _clusterUntil || Vector2.Distance(_clusterAt, at) > ClusterRadius)
            {
                _clusterUntil = now + 0.9f;
                _clusterAt = centre / (others + 1);
                Play(cluster, _clusterAt, 1f, 0f, SoundPriority.SmallArms);
            }
            return true;
        }

        /// <summary>
        /// A round landing. With a blast: by size and round (HE, thermobaric, HEAT, an air burst). Without one (a kinetic
        /// round): by what it struck (<see cref="Surface"/>): metal only on armour it did not pierce, under the match-wide
        /// cap. False: the old categories play it (fire, energy).
        /// </summary>
        private bool Landed(in SimEvent e)
        {
            if (e.DefId == null || !_catalog.Weapons.TryGetValue(e.DefId, out var round)) return false;
            var size = SoundLibrary.SizeOf(round);
            var name = SoundLibrary.BlastBank(round, e.Airborne);
            var blast = name != null;
            if (!blast)
            {
                if (round.DamageType != DamageType.Kinetic) return false;
                var surface = Surface(e, round);
                // Over the cap a glancing round is not heard at all (the run is heard by its first few).
                if (surface == HitSurface.Metal && !_metal.TryTake(Time.unscaledTime)) return true;
                name = SoundLibrary.HitBank(surface, size);
            }
            if (!_tierBanks.TryGetValue(name, out var bank)) return false;
            // The bomb-run fix, pass 3: a stick's blasts each crack at their own point; the one before gives up its tail as the
            // next goes off, so the stick rolls on as one tail (AudioDirector.Sticks).
            var run = blast ? StickRun(round, e.Position) : 0;
            Play(bank, e.Position, 1f, SoundLibrary.Carry(size), PriorityOf(round, e.Position, blast), 1f, run);
            return true;
        }

        /// <summary>
        /// Fix pass L7: what a round without a blast struck, read from the event the view already has (no Sim change): the
        /// struck entity (<see cref="SimEvent.Entity"/>, invalid for the ground) and the hull contact point the Sim puts the
        /// impact on (DamageSystem: a direct round meets the hull on the shooter's side, so the face it struck is the face that
        /// point lies on; a round from above strikes the roof). The target's armour on that face against the round's
        /// penetration decides metal (not pierced) or a heavy impact (pierced), as the Sim's penetration step does (level or
        /// better goes through). Not counted: the shooter's equipment bonus (internal to the Sim) and a boss part's own armour.
        /// </summary>
        private HitSurface Surface(in SimEvent e, WeaponDef round)
        {
            if (!e.Entity.IsValid) return HitSurface.Ground;
            if (_views != null && _views.TryGet(e.Entity, out var view) && view != null && view.Sim != null)
            {
                var v = view.Sim;
                var top = Armour.StrikesTop(round);
                var face = top ? ArmorFace.Top : Armour.FaceFrom(v.Position, v.Heading, e.Position);
                return SoundLibrary.SurfaceOf(true, true, v.Def.Static || v.Def.Armor == ArmorClass.Structure, v.Flying, round.DamageType == DamageType.Kinetic,
                    round.Penetration, v.ArmourOn(face));
            }
            // Gone from the views (the round that killed it): its definition from its spawn, the side armour.
            if (_unitDefs.TryGetValue(e.Entity, out var def))
                return SoundLibrary.SurfaceOf(true, true, def.Static || def.Armor == ArmorClass.Structure, def.Flying && e.Airborne,
                    round.DamageType == DamageType.Kinetic, round.Penetration, def.Armour[Armour.StrikesTop(round) ? ArmorFace.Top : ArmorFace.Side]);
            // Not a unit: a building, a wall, a prop.
            return HitSurface.Concrete;
        }

        /// <summary>A blast event: a falling aircraft hitting the ground, a ship's salvo shell. False: the old categories play it.</summary>
        private bool Exploded(in SimEvent e)
        {
            if (_crashing.TryGetValue(e.Entity, out var due) && Time.unscaledTime >= due && _crashing.Remove(e.Entity) &&
                _tierBanks.TryGetValue("crash_impact", out var crash))
            {
                Play(crash, e.Position, 1f, 40f, SoundPriority.NearBlast);
                return true;
            }
            if (!_salvoShips.Contains(e.Entity) || !_catalog.Vehicles.TryGetValue(ShipDef(e.Entity), out var ship) || ship.Salvo?.Weapon is not { } gun ||
                !_catalog.Weapons.TryGetValue(gun, out var shell)) return false;
            var name = SoundLibrary.BlastBank(shell);
            if (name == null || !_tierBanks.TryGetValue(name, out var bank)) return false;
            Play(bank, e.Position, 1f, SoundLibrary.Carry(SoundLibrary.SizeOf(shell)), SoundPriority.Boss);
            return true;
        }

        private readonly Dictionary<EntityId, string> _shipDefs = new();

        private string ShipDef(EntityId id) => _shipDefs.TryGetValue(id, out var def) ? def : "";

        /// <summary>A vehicle lost: its wreck by its class; an aircraft's fall too, its crash heard when it lands (the Sim's blast).</summary>
        private bool Wrecked(in SimEvent e)
        {
            _salvoShips.Remove(e.Entity);
            _nextHorn.Remove(e.Entity);
            if (e.DefId == null || !_catalog.Vehicles.TryGetValue(e.DefId, out var def)) return false;
            var c = WreckClasses.Of(def);
            if (c == WreckClass.Ship) LoadGroup("naval");
            var name = WreckBank(c);
            if (name == null || !_tierBanks.TryGetValue(name, out var bank)) return false;
            var priority = def.Boss ? SoundPriority.Boss : Near(e.Position) ? SoundPriority.NearBlast : SoundPriority.FarBlast;
            Play(bank, e.Position, 1f, 30f, priority);
            if (WreckClasses.Falls(c))
            {
                // The crash is the Sim's blast at its fixed point and time (VehicleDestroyed's Value: the fall); a death
                // blast of its own before that is not the crash.
                _crashing[e.Entity] = Time.unscaledTime + Mathf.Max(0f, e.Value - 0.3f);
                if (_crashing.Count > 64) _crashing.Clear();
                if (_tierBanks.TryGetValue("crash_fall", out var fall)) Play(fall, e.Position, 0.9f, 0f, priority);
            }
            return true;
        }

        /// <summary>A vehicle arrives: noted for its hits; a ship or a train loads its group and sounds its horn; a salvo ship is noted for its shells.</summary>
        private void Spawned(in SimEvent e)
        {
            if (e.DefId == null || !_catalog.Vehicles.TryGetValue(e.DefId, out var def)) return;
            if (_unitDefs.Count > 4096) _unitDefs.Clear();
            _unitDefs[e.Entity] = def;
            var c = WreckClasses.Of(def);
            if (def.Salvo != null)
            {
                _salvoShips.Add(e.Entity);
                _shipDefs[e.Entity] = def.Id;
            }
            if (c == WreckClass.Ship)
            {
                LoadGroup("naval");
                if (def.Radius >= 4f && _tierBanks.TryGetValue("ship_horn", out var horn)) Play(horn, e.Position, 1f, 40f, SoundPriority.NearShot);
            }
            else if (c == WreckClass.Train)
            {
                LoadGroup("rail");
                if (_tierBanks.TryGetValue("train_horn", out var horn)) Play(horn, e.Position, 1f, 40f, def.Boss ? SoundPriority.Boss : SoundPriority.NearShot);
                _nextHorn[e.Entity] = Time.unscaledTime + 35f + (float)_rng.NextDouble() * 15f;
            }
        }

        /// <summary>Flares out (the skill): the cartridges' pops and the burning flares' hiss.</summary>
        private void Flared(in SimEvent e)
        {
            if (_tierBanks.TryGetValue("flare_pop", out var bank)) Play(bank, e.Position, 1f, 10f, SoundPriority.NearShot);
        }

        /// <summary>
        /// Play-test 12: a missile's or a rocket's hiss in flight, heard where it was aimed just before it lands (its blast
        /// follows by its warhead); one at most in <see cref="HissGap"/> s, so a salvo never crowds out the shells' whistles.
        /// </summary>
        private void Incoming(in SimEvent e, WeaponDef weapon)
        {
            if (weapon == null || e.Jammed || weapon.Projectile is not (ProjectileKind.Missile or ProjectileKind.Rocket)) return;
            if (SoundLibrary.LaunchBank(weapon) == null || e.Value < HissLead + 0.4f) return;
            if (!_tierBanks.TryGetValue("missile_hiss", out var hiss)) return;
            var now = Time.unscaledTime;
            if (now < _nextHiss) return;
            _nextHiss = now + HissGap;
            Schedule(hiss, e.Target, 0.9f, e.Value - HissLead, SoundPriority.FarShot);
        }

        /// <summary>An incoming shell's whistle: the big one for a boss's attack or a 406 mm / super weapon.</summary>
        private void Whistle(Vector2 at, float volume, float delay, bool big)
        {
            if (big && _tierBanks.TryGetValue("warn_whistle_big", out var bank)) Schedule(bank, at, volume, delay, SoundPriority.Warning);
            else Schedule(Sound.Whistle, at, volume, delay);
        }

        /// <summary>Per frame: the engines of the moving units near the view by class, the rails under a train, a ship's engines, a train's horn.</summary>
        private void TickTiers(ViewRegistry views, float now)
        {
            var train = float.MaxValue;
            var ship = float.MaxValue;
            var tracked = float.MaxValue;
            var wheeled = float.MaxValue;
            var heavy = float.MaxValue;
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (view.IsWreck || !view.Sim.IsAlive) continue;
                var c = WreckClasses.Of(view.Def);
                var d = Vector3.Distance(view.Position, Focus);
                if (c == WreckClass.Train && view.Sim.Speed > 0.3f)
                {
                    train = Mathf.Min(train, d);
                    if (_nextHorn.TryGetValue(view.Id, out var due) && now >= due && d < Reach(0f) && _tierBanks.TryGetValue("train_horn", out var horn))
                    {
                        _nextHorn[view.Id] = now + 35f + (float)_rng.NextDouble() * 15f;
                        Play(horn, new Vector2(view.Position.x, view.Position.z), 0.8f, 40f, view.Def.Boss ? SoundPriority.Boss : SoundPriority.NearShot);
                    }
                }
                else if (c == WreckClass.Ship) ship = Mathf.Min(ship, d);
                else if (view.Sim.Speed > 0.5f && !view.Flying)
                {
                    if (c == WreckClass.Tank) tracked = Mathf.Min(tracked, d);
                    else if (c == WreckClass.Wheeled) wheeled = Mathf.Min(wheeled, d);
                    else if (c is WreckClass.Truck or WreckClass.Artillery) heavy = Mathf.Min(heavy, d);
                }
            }
            var reach = Reach(0f);
            float Level(float d, float top) => d < float.MaxValue && !_lobby ? Mathf.Clamp01(1f - d / (reach * 0.6f)) * top * Fx : 0f;
            Steer(_rails, Level(train, 0.5f));
            Steer(_engines, Level(ship, 0.35f));
            Steer(_engTracked, Level(tracked, 0.45f));
            Steer(_engWheeled, Level(wheeled, 0.35f));
            Steer(_engHeavy, Level(heavy, 0.4f));
        }

        private static void Steer(AudioSource loop, float target)
        {
            if (loop == null) return;
            loop.volume = Mathf.MoveTowards(loop.volume, target, Time.unscaledDeltaTime * 0.6f);
            if (loop.volume > 0f && !loop.isPlaying) loop.Play();
            else if (loop.volume <= 0f && loop.isPlaying) loop.Stop();
        }

        // ------------------------------------------------------------------------------------------------ the Effects group

        /// <summary>
        /// The Effects compressor (control rate, each frame): the summed RMS of what the effect voices play now (each voice's
        /// level times its clip's envelope at its play position; a clip without one counts at a fifth of its level) against
        /// <see cref="SoundLibrary.CompressorThreshold"/>, at <see cref="SoundLibrary.CompressorRatio"/>, with a fast attack and
        /// a slow release; the gain goes onto every effect voice. The limiter (<see cref="EffectsLimiter"/>) catches the peaks
        /// it is too slow for.
        /// </summary>
        private void Compress(float dt)
        {
            var sum = 0f;
            foreach (var v in _voices)
            {
                if (v.Bank == null || !v.Source.isPlaying || v.Source.clip == null) continue;
                var rms = 0.2f;
                if (_envelopes.TryGetValue(v.Source.clip.name, out var env) && env.Length > 0)
                {
                    var i = (int)(v.Source.time * SoundLibrary.EnvelopeRate);
                    rms = i < env.Length ? env[i] : 0f;
                }
                var a = v.Level * rms;
                sum += a * a;
            }
            var target = SoundLibrary.CompressorGain(Mathf.Sqrt(sum));
            var time = target < _busGain ? CompressorAttack : CompressorRelease;
            _busGain = Mathf.Lerp(_busGain, target, 1f - Mathf.Exp(-dt / time));
            if (_limiter == null && _limiterTries < 30 && Time.frameCount % 60 == 0) AttachLimiter();
        }

        /// <summary>Puts the output limiter on the listener (once; another director's is shared, not owned).</summary>
        private void AttachLimiter()
        {
            _limiterTries++;
            var cam = View;
            var listener = cam != null ? cam.GetComponent<AudioListener>() : null;
            if (listener == null) listener = UnityEngine.Object.FindAnyObjectByType<AudioListener>();
            if (listener == null) return;
            _limiter = listener.GetComponent<EffectsLimiter>();
            if (_limiter != null) return;
            _limiter = listener.gameObject.AddComponent<EffectsLimiter>();
            _ownsLimiter = true;
        }

        private void DetachLimiter()
        {
            if (_ownsLimiter && _limiter != null) UnityEngine.Object.Destroy(_limiter);
            _limiter = null;
        }
    }
}

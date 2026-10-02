using System.Collections.Generic;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Prompt 34 L6: the prompt's seven priorities, as a number a voice is cut by (higher wins). Between the prompt's
    /// steps there is room for one more (an enemy's T2 gun under our important weapons, over the small arms).
    /// </summary>
    internal static class SoundPriority
    {
        /// <summary>7. The environment (debris, ambience).</summary>
        public const int Ambient = 10;

        /// <summary>6. Small arms fired over and over (and their clusters).</summary>
        public const int SmallArms = 20;

        /// <summary>Between 5 and 6: an enemy's T2 gun, a medium blast.</summary>
        public const int Medium = 25;

        /// <summary>5. Our side's important weapons (T2+ guns, missiles, rockets, drones).</summary>
        public const int Ally = 30;

        /// <summary>4. A T3 round near the view (far: as our important weapons).</summary>
        public const int T3Near = 40;

        /// <summary>3. A T4 round near the view (far: as a T3 near).</summary>
        public const int T4Near = 50;

        /// <summary>2. A T5 round or a boss's.</summary>
        public const int Boss = 60;

        /// <summary>1. Gameplay warnings and super weapons (the whistles of incoming fire; the alarms play on their own source).</summary>
        public const int Warning = 70;

        /// <summary>The old banks' priorities (0-5) on this scale; 7 and up is a warning.</summary>
        public static int Steps(int old) => old >= 7 ? Warning : old switch
        {
            <= 0 => Ambient,
            1 or 2 => SmallArms,
            3 => Ally,
            4 => T3Near,
            _ => T4Near,
        };

        /// <summary>A round's priority: by its tier, a boss's, our side's, near the view or not.</summary>
        public static int For(int tier, bool boss, bool ally, bool near, bool important)
        {
            if (boss || tier >= 5) return Boss;
            if (tier == 4) return near ? T4Near : T3Near;
            if (tier == 3) return near ? T3Near : Ally;
            if (ally && important) return Ally;
            return tier <= 1 ? SmallArms : Medium;
        }
    }

    public sealed partial class AudioDirector
    {
        /// <summary>Effect voices at once before the least important is cut (of the pool's 32; the rest wait for warnings and T5 / boss).</summary>
        internal const int EffectVoices = 24;

        /// <summary>A source off the screen plays this much quieter.</summary>
        internal const float OffScreenGain = 0.6f;

        /// <summary>Small arms within this of each other (m) inside <see cref="ClusterWindow"/> (s) count as one firefight.</summary>
        internal const float ClusterRadius = 20f, ClusterWindow = 0.5f;

        /// <summary>From this many small-arms shots in a firefight, it is heard as one cluster sound, not a voice a shot.</summary>
        internal const int ClusterFrom = 3;

        /// <summary>A round counts as near the view inside this share of the hearing reach.</summary>
        internal const float NearShare = 0.45f;

        /// <summary>The effects' and the dialogue's volumes (Settings, under the master volume).</summary>
        private static float Fx => MatchSettings.EffectsVolume;
        private static float Talk => MatchSettings.DialogueVolume;

        /// <summary>The tiered banks by name (Resources/Audio/p34/name), from Tools/sfx/build_sfx.py.</summary>
        private readonly Dictionary<string, Bank> _tierBanks = new();

        /// <summary>Banks loaded with their units (the map's group): "naval" (ship horn, engines, wrecks), "rail" (train horn, rails).</summary>
        private readonly HashSet<string> _groups = new();

        private readonly HashSet<string> _bossWeapons = new();
        private readonly HashSet<EntityId> _salvoShips = new();
        /// <summary>Falling aircraft: from when their crash is due (the Sim's fall time, L7's crash plan on the loss event).</summary>
        private readonly Dictionary<EntityId, float> _crashing = new();
        private readonly List<(float at, Vector2 where)> _smallArms = new();
        private float _clusterUntil = -10f;
        private Vector2 _clusterAt;
        private AudioSource _rails, _engines;
        private readonly Dictionary<EntityId, float> _nextHorn = new();

        private void AddTierBanks()
        {
            float[] shotVolume = { 0.38f, 0.46f, 0.72f, 0.86f, 0.95f, 1f };
            int[] shotVoices = { 4, 4, 4, 3, 2, 2 };
            for (var t = 0; t <= 5; t++)
                TierBank($"shot_t{t}", shotVolume[t], shotVoices[t], t <= 1 ? 0.06f : 0.05f + 0.01f * t,
                    SoundPriority.For(t, false, false, true, true), light: t <= 1);
            for (var t = 2; t <= 5; t++) TierBank($"launch_t{t}", 0.5f + 0.1f * t, t >= 4 ? 2 : 3, 0.06f, SoundPriority.For(t, false, false, true, true));
            for (var t = 1; t <= 5; t++)
                TierBank($"blast_he_t{t}", 0.5f + 0.1f * t, t >= 4 ? 2 : t >= 3 ? 3 : 4, 0.04f + 0.012f * t, SoundPriority.For(t, false, false, true, true),
                    delayed: true);
            for (var t = 1; t <= 4; t++) TierBank($"blast_ap_t{t}", 0.35f + 0.12f * t, 3, 0.05f, SoundPriority.For(t, false, false, true, true));
            TierBank("blast_heat", 0.7f, 3, 0.05f, SoundPriority.Ally);
            TierBank("blast_thermo_t3", 0.9f, 2, 0.1f, SoundPriority.T3Near, delayed: true);
            TierBank("blast_thermo_t4", 1f, 2, 0.12f, SoundPriority.T4Near, delayed: true);
            TierBank("smallarms_cluster", 0.55f, 2, 0.35f, SoundPriority.SmallArms, light: true);
            foreach (var kind in new[] { "tank", "wheeled", "truck", "artillery", "aircraft", "heli", "drone" })
                TierBank("wreck_" + kind, kind == "drone" ? 0.55f : 0.85f, 3, 0.1f, SoundPriority.T3Near, delayed: true);
            TierBank("crash_fall", 0.6f, 2, 0.3f, SoundPriority.T3Near);
            TierBank("crash_impact", 0.95f, 2, 0.1f, SoundPriority.T4Near, delayed: true);
            foreach (var def in _catalog.Vehicles.Values)
            {
                if (!def.Boss) continue;
                foreach (var mount in def.Mounts) _bossWeapons.Add(mount.Weapon.Id);
            }
        }

        /// <summary>A tiered bank, when its clips are there (built and imported); without them the old banks play.</summary>
        private void TierBank(string name, float volume, int voices, float cooldown, int priority, bool light = false, bool delayed = false)
        {
            var clips = Recorded("p34/" + name);
            if (clips == null) return;
            _tierBanks[name] = new Bank
            {
                Clips = clips, Volume = volume, MaxVoices = voices, Cooldown = cooldown, Priority = priority, Light = light, Delayed = delayed,
            };
        }

        /// <summary>
        /// Loads a map group's banks the first time one of its units shows up (prompt's "load by map group"): a map with no
        /// ships or trains never loads their sounds.
        /// </summary>
        private void LoadGroup(string group)
        {
            if (!_groups.Add(group)) return;
            if (group == "naval")
            {
                TierBank("ship_horn", 0.8f, 1, 10f, SoundPriority.Ally);
                TierBank("wreck_ship", 1f, 2, 0.2f, SoundPriority.T4Near, delayed: true);
                _engines = TierLoop("Ship Engines", "ship_engine");
            }
            else if (group == "rail")
            {
                TierBank("train_horn", 0.8f, 1, 8f, SoundPriority.Ally);
                _rails = TierLoop("Rails", "train_rails");
            }
            foreach (var name in group == "naval" ? new[] { "ship_horn", "wreck_ship" } : new[] { "train_horn" })
                if (_tierBanks.TryGetValue(name, out var bank))
                    foreach (var clip in bank.Clips)
                        Load(clip);
        }

        private AudioSource TierLoop(string name, string folder)
        {
            var clips = Recorded("p34/" + folder);
            if (clips == null) return null;
            var source = NewSource(name);
            source.clip = clips[0];
            source.loop = true;
            source.volume = 0f;
            Load(source.clip);
            return source;
        }

        private bool Near(Vector2 at) => Vector3.Distance(new Vector3(at.X, 0f, at.Y), Focus) < Reach(0f) * NearShare;

        private int PriorityOf(WeaponDef weapon, Vector2 at, int team)
        {
            if (weapon == null) return -1;
            var important = weapon.Tier >= 2 || weapon.Projectile is ProjectileKind.Missile or ProjectileKind.Rocket or ProjectileKind.Drone;
            return SoundPriority.For(weapon.Tier, _bossWeapons.Contains(weapon.Id), team == _playerTeam && _playerTeam >= 0, Near(at), important);
        }

        /// <summary>The tiered bank a shot plays (null: the old categories): guns by tier, rockets and missiles of T2+ by tier.</summary>
        internal static string ShotBank(WeaponDef weapon)
        {
            if (weapon == null || weapon.Tier < 0 || weapon.Beam) return null;
            switch (weapon.Projectile)
            {
                case ProjectileKind.Rocket:
                case ProjectileKind.Missile:
                    return weapon.Tier >= 2 ? $"launch_t{Mathf.Min(5, weapon.Tier)}" : null;
                case ProjectileKind.Bullet when weapon.DamageType == DamageType.Fragmentation:
                case ProjectileKind.Flame:
                case ProjectileKind.Drone:
                case ProjectileKind.Bomb:
                    return null;
                default:
                    return $"shot_t{Mathf.Min(5, weapon.Tier)}";
            }
        }

        /// <summary>The tiered bank a round's landing plays (null: the old categories): by tier and round.</summary>
        internal static string ImpactBank(WeaponDef round)
        {
            if (round == null || round.Tier < 1 || round.Beam) return null;
            if (round.Id.StartsWith("thermobaric") || round.WeaponVariantId == "thermobaric") return $"blast_thermo_t{Mathf.Clamp(round.Tier, 3, 4)}";
            if (round.DamageType == DamageType.ShapedCharge) return "blast_heat";
            if (round.DamageType == DamageType.Kinetic && round.SplashRadius <= 0f) return $"blast_ap_t{Mathf.Clamp(round.Tier, 1, 4)}";
            if (round.DamageType is DamageType.Fire or DamageType.Energy or DamageType.Fragmentation) return null;
            return $"blast_he_t{Mathf.Clamp(round.Tier, 1, 5)}";
        }

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

        /// <summary>A shot: its tiered sound at its priority; small arms in a firefight heard as one cluster.</summary>
        private void Shot(in SimEvent e, WeaponDef weapon)
        {
            var priority = PriorityOf(weapon, e.Position, e.Team);
            if (SmallArms(weapon) && Clustered(e.Position)) return;
            var name = ShotBank(weapon);
            if (name != null && _tierBanks.TryGetValue(name, out var bank)) Play(bank, e.Position, 1f, 0f, priority);
            else Play(_banks[WeaponSound(weapon)], e.Position, 1f, 0f, priority);
        }

        /// <summary>
        /// Small arms: when <see cref="ClusterFrom"/> or more shots come from within <see cref="ClusterRadius"/> inside
        /// <see cref="ClusterWindow"/>, the firefight is one cluster sound (a few guns at once, near and far) played now and then,
        /// and the shots in it take no voice of their own. True when the shot was taken into a cluster.
        /// </summary>
        private bool Clustered(Vector2 at)
        {
            if (!_tierBanks.TryGetValue("smallarms_cluster", out var cluster)) return false;
            var now = Time.unscaledTime;
            var near = 0;
            var centre = at;
            for (var i = _smallArms.Count - 1; i >= 0; i--)
            {
                var (when, where) = _smallArms[i];
                if (now - when > ClusterWindow)
                {
                    _smallArms.RemoveAt(i);
                    continue;
                }
                if (Vector2.Distance(where, at) > ClusterRadius) continue;
                near++;
                centre += where;
            }
            if (_smallArms.Count < 64) _smallArms.Add((now, at));
            if (near + 1 < ClusterFrom) return false;
            if (now >= _clusterUntil || Vector2.Distance(_clusterAt, at) > ClusterRadius)
            {
                _clusterUntil = now + 0.9f;
                _clusterAt = centre / (near + 1);
                Play(cluster, _clusterAt, 1f, 0f, SoundPriority.SmallArms);
            }
            return true;
        }

        /// <summary>A round landing: by tier and round (HE, AP, HEAT, thermobaric). False: the old categories play it.</summary>
        private bool Landed(in SimEvent e)
        {
            if (e.DefId == null || !_catalog.Weapons.TryGetValue(e.DefId, out var round)) return false;
            var name = ImpactBank(round);
            if (name == null || !_tierBanks.TryGetValue(name, out var bank)) return false;
            Play(bank, e.Position, e.Tier >= ExplosionTier.Huge ? 1f : 0.9f, 0f, PriorityOf(round, e.Position, e.Team));
            return true;
        }

        /// <summary>A blast event: a falling aircraft hitting the ground, a ship's salvo shell. False: the old categories play it.</summary>
        private bool Exploded(in SimEvent e)
        {
            if (_crashing.TryGetValue(e.Entity, out var due) && Time.unscaledTime >= due && _crashing.Remove(e.Entity) &&
                _tierBanks.TryGetValue("crash_impact", out var crash))
            {
                Play(crash, e.Position, 1f, 0f, SoundPriority.T4Near);
                return true;
            }
            if (!_salvoShips.Contains(e.Entity) || !_catalog.Vehicles.TryGetValue(ShipDef(e.Entity), out var ship) || ship.Salvo?.Weapon is not { } gun ||
                !_catalog.Weapons.TryGetValue(gun, out var shell)) return false;
            var name = ImpactBank(shell);
            if (name == null || !_tierBanks.TryGetValue(name, out var bank)) return false;
            Play(bank, e.Position, 1f, 0f, SoundPriority.Boss);
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
            var priority = def.Boss ? SoundPriority.Boss : Near(e.Position) ? SoundPriority.T3Near : SoundPriority.Ally;
            Play(bank, e.Position, 1f, 0f, priority);
            if (WreckClasses.Falls(c))
            {
                // The crash is the Sim's blast at its fixed point and time (VehicleDestroyed's Value: the fall, L7); a death
                // blast of its own before that is not the crash.
                _crashing[e.Entity] = Time.unscaledTime + Mathf.Max(0f, e.Value - 0.3f);
                if (_crashing.Count > 64) _crashing.Clear();
                if (_tierBanks.TryGetValue("crash_fall", out var fall)) Play(fall, e.Position, 0.9f, 0f, priority);
            }
            return true;
        }

        /// <summary>A vehicle arrives: a ship or a train loads its group and sounds its horn; a salvo ship is noted for its shells.</summary>
        private void Spawned(in SimEvent e)
        {
            if (e.DefId == null || !_catalog.Vehicles.TryGetValue(e.DefId, out var def)) return;
            var c = WreckClasses.Of(def);
            if (def.Salvo != null)
            {
                _salvoShips.Add(e.Entity);
                _shipDefs[e.Entity] = def.Id;
            }
            if (c == WreckClass.Ship)
            {
                LoadGroup("naval");
                if (def.Radius >= 4f && _tierBanks.TryGetValue("ship_horn", out var horn)) Play(horn, e.Position, 1f, 0f, SoundPriority.Ally);
            }
            else if (c == WreckClass.Train)
            {
                LoadGroup("rail");
                if (_tierBanks.TryGetValue("train_horn", out var horn)) Play(horn, e.Position, 1f, 0f, def.Boss ? SoundPriority.Boss : SoundPriority.Ally);
                _nextHorn[e.Entity] = Time.unscaledTime + 35f + (float)_rng.NextDouble() * 15f;
            }
        }

        /// <summary>Per frame: the rails under a moving train and a ship's engines near the view; a train's horn now and then.</summary>
        private void TickTiers(ViewRegistry views, float now)
        {
            if (_rails == null && _engines == null) return;
            var train = float.MaxValue;
            var ship = float.MaxValue;
            var all = views.All;
            for (var i = 0; i < all.Count; i++)
            {
                var view = all[i];
                if (view.IsWreck || !view.Sim.IsAlive) continue;
                var c = WreckClasses.Of(view.Def);
                if (c == WreckClass.Train && view.Sim.Speed > 0.3f)
                {
                    var d = Vector3.Distance(view.Position, Focus);
                    train = Mathf.Min(train, d);
                    if (_nextHorn.TryGetValue(view.Id, out var due) && now >= due && d < Reach(0f) && _tierBanks.TryGetValue("train_horn", out var horn))
                    {
                        _nextHorn[view.Id] = now + 35f + (float)_rng.NextDouble() * 15f;
                        Play(horn, new Vector2(view.Position.x, view.Position.z), 0.8f, 0f, view.Def.Boss ? SoundPriority.Boss : SoundPriority.Ally);
                    }
                }
                else if (c == WreckClass.Ship) ship = Mathf.Min(ship, Vector3.Distance(view.Position, Focus));
            }
            var reach = Reach(0f);
            Steer(_rails, train < float.MaxValue && !_lobby ? Mathf.Clamp01(1f - train / reach) * 0.5f * Fx : 0f);
            Steer(_engines, ship < float.MaxValue && !_lobby ? Mathf.Clamp01(1f - ship / reach) * 0.35f * Fx : 0f);
        }

        private static void Steer(AudioSource loop, float target)
        {
            if (loop == null) return;
            loop.volume = Mathf.MoveTowards(loop.volume, target, Time.unscaledDeltaTime * 0.6f);
            if (loop.volume > 0f && !loop.isPlaying) loop.Play();
            else if (loop.volume <= 0f && loop.isPlaying) loop.Stop();
        }
    }
}

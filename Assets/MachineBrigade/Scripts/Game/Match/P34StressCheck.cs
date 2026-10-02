using System.Collections.Generic;
using System.Globalization;
using System.Text;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Effects;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 34 L9 (DECISIONS "Prompt 34 L8 / L9"): the offline stress scene. Debug flags
    /// <c>-mb-play -mb-lighthousebay -mb-p34stress</c> (or <c>-mb-p34stress=SECONDS</c>, default 120): the Leviathan at
    /// sea, Jötunn (the Smerch pods) and Roc (the 400 kg bomb stick) for the enemy, and 32 vehicles a side kept up to
    /// strength in the middle of the view. Once a second it samples the live particles (every particle system in the
    /// scene), the busy sound voices (of 32) and the wrecks (hulks and torn-off pieces); at the end it writes the peaks
    /// and means to <c>Docs/balance/p34_stress_counts.json</c> (in the editor; the log in a player) and logs one line.
    /// Counts only: frame times are NEED PROFILE on a device, and nothing here says anything of balance.
    /// Written for the lead to run; not run in the pass that wrote it.
    /// </summary>
    internal sealed class P34StressCheck
    {
        public const string Flag = "-mb-p34stress";

        /// <summary>The bosses of the scene: the Leviathan's 406 mm and 155 mm, Jötunn's Smerch, Roc's bombs.</summary>
        public static readonly string[] Bosses = { "leviathan", "mobile_fortress", "command_airship" };

        /// <summary>Vehicles a side, kept up to strength.</summary>
        public const int PerSide = 32;

        /// <summary>A mix of the roster (tanks, carriers, artillery, rockets, air defence, helicopters).</summary>
        public static readonly string[] Roster =
        {
            "main_battle_tank", "heavy_tank", "ifv", "apc", "artillery", "mlrs", "grad_truck", "aa_vehicle", "tank_destroyer",
            "armored_car", "sam_launcher", "attack_helicopter", "howitzer", "mortar_carrier", "light_tank", "heavy_aa",
        };

        private const float Gap = 7f;
        private const int PerTick = 8;

        private readonly List<string> _roster = new();
        private readonly Vector2 _centre;
        private readonly float _seconds;
        private readonly Dictionary<string, Vehicle> _bosses = new();
        private readonly Dictionary<string, float> _bossDue = new();
        private float _nextAt, _sampleAt, _startAt = -1f;
        private int _next;
        private bool _done;

        private int _samples;
        private long _particleSum, _voiceSum, _wreckSum, _pieceSum;
        private int _particlePeak, _voicePeak, _wreckPeak, _piecePeak, _systemsPeak;

        private P34StressCheck(SimWorld world, Vector3 focus, float seconds)
        {
            foreach (var id in Roster)
                if (world.Catalog.Vehicles.ContainsKey(id)) _roster.Add(id);
            _centre = new Vector2(focus.x, focus.z);
            _seconds = seconds;
        }

        /// <summary>The scene when the flag is set (outside the menu), else null.</summary>
        public static P34StressCheck Create(SimWorld world, Vector3 focus)
        {
            var value = DebugFlags.Value(Flag + "=");
            if (!DebugFlags.Has(Flag) && value == null) return null;
            var seconds = float.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out var s) ? Mathf.Clamp(s, 10f, 1800f) : 120f;
            return new P34StressCheck(world, focus, seconds);
        }

        /// <summary>Keeps the scene going and samples it (call every frame while unpaused).</summary>
        public void Tick(SimWorld world, float now, EffectsDirector effects, AudioDirector audio)
        {
            if (_done) return;
            if (_startAt < 0f) _startAt = now;
            KeepBosses(world, now);
            KeepArmies(world, now);
            if (now >= _sampleAt)
            {
                _sampleAt = now + 1f;
                Sample(effects, audio);
            }
            if (now - _startAt >= _seconds)
            {
                _done = true;
                Write();
            }
        }

        /// <summary>Each boss in, and back 10 s after it is lost (the Leviathan on its sea lane when the map has a sea).</summary>
        private void KeepBosses(SimWorld world, float now)
        {
            foreach (var id in Bosses)
            {
                if (!world.Catalog.Vehicles.TryGetValue(id, out var def)) continue;
                if (_bosses.TryGetValue(id, out var boss) && boss.IsAlive) continue;
                if (boss != null && !_bossDue.ContainsKey(id)) _bossDue[id] = now + 10f;
                if (_bossDue.TryGetValue(id, out var due) && now < due) continue;
                _bossDue.Remove(id);
                var at = _centre + new Vector2(30f, 30f);
                if (def.Naval != null && world.Map.Sea is { } sea)
                {
                    var w = sea.Lanes.Count > 0 ? sea.Lanes[sea.Lanes.Count / 2].W : 0f;
                    at = sea.At(sea.Frame(_centre).X, w);
                }
                else if (def.Flying) at = _centre + new Vector2(45f, 45f);
                _bosses[id] = world.SpawnVehicle(id, 1, at, Mathf.PI * 1.25f);
            }
        }

        /// <summary>Both sides topped up to <see cref="PerSide"/> (the bosses not counted), a few a step.</summary>
        private void KeepArmies(SimWorld world, float now)
        {
            if (now < _nextAt || _roster.Count == 0) return;
            _nextAt = now + 0.5f;
            var across = Vector2.Normalize(new Vector2(1f, 1f));
            var along = new Vector2(across.Y, -across.X);
            for (var team = 0; team <= 1; team++)
            {
                var alive = world.CountAlive(team);
                if (team == 1)
                    foreach (var b in _bosses.Values)
                        if (b != null && b.IsAlive) alive--;
                var missing = PerSide - alive;
                var side = team == 0 ? -1f : 1f;
                for (var i = 0; i < Mathf.Min(missing, PerTick); i++)
                {
                    var slot = _next++;
                    var row = slot % 8 - 3.5f;
                    var rank = (slot / 8) % 4;
                    var at = _centre + across * (side * (16f + rank * Gap)) + along * (row * Gap);
                    var heading = Mathf.Atan2(across.X, across.Y) + (team == 0 ? 0f : Mathf.PI);
                    world.SpawnVehicle(_roster[slot % _roster.Count], team, at, heading);
                }
            }
        }

        private void Sample(EffectsDirector effects, AudioDirector audio)
        {
            var particles = 0;
            var systems = 0;
            foreach (var ps in Object.FindObjectsByType<ParticleSystem>())
            {
                var n = ps.particleCount;
                if (n <= 0) continue;
                particles += n;
                systems++;
            }
            var voices = audio != null ? audio.BusyVoices : 0;
            var wrecks = effects != null ? effects.WreckCount : 0;
            var pieces = effects != null ? effects.WreckPieces : 0;
            _samples++;
            _particleSum += particles;
            _voiceSum += voices;
            _wreckSum += wrecks;
            _pieceSum += pieces;
            _particlePeak = Mathf.Max(_particlePeak, particles);
            _systemsPeak = Mathf.Max(_systemsPeak, systems);
            _voicePeak = Mathf.Max(_voicePeak, voices);
            _wreckPeak = Mathf.Max(_wreckPeak, wrecks);
            _piecePeak = Mathf.Max(_piecePeak, pieces);
        }

        /// <summary>The counts as JSON (peaks and means over the samples).</summary>
        public string Report()
        {
            var n = Mathf.Max(1, _samples);
            var sb = new StringBuilder();
            sb.Append("{\n");
            sb.Append("  \"scene\": \"prompt 34 L9: leviathan + mobile_fortress (Smerch) + command_airship (bombs) + ").Append(PerSide).Append(" a side\",\n");
            sb.Append("  \"seconds\": ").Append(_seconds.ToString("0", CultureInfo.InvariantCulture)).Append(",\n");
            sb.Append("  \"samples\": ").Append(_samples).Append(",\n");
            sb.Append("  \"graphics\": \"").Append(MatchSettings.Graphics).Append("\",\n");
            sb.Append("  \"particles\": { \"peak\": ").Append(_particlePeak).Append(", \"mean\": ").Append((_particleSum / n).ToString(CultureInfo.InvariantCulture))
                .Append(", \"systemsPeak\": ").Append(_systemsPeak).Append(" },\n");
            sb.Append("  \"voices\": { \"peak\": ").Append(_voicePeak).Append(", \"mean\": ").Append(((float)_voiceSum / n).ToString("0.0", CultureInfo.InvariantCulture))
                .Append(", \"of\": 32 },\n");
            sb.Append("  \"wrecks\": { \"peak\": ").Append(_wreckPeak).Append(", \"mean\": ").Append(((float)_wreckSum / n).ToString("0.0", CultureInfo.InvariantCulture)).Append(" },\n");
            sb.Append("  \"wreckPieces\": { \"peak\": ").Append(_piecePeak).Append(", \"mean\": ").Append(((float)_pieceSum / n).ToString("0.0", CultureInfo.InvariantCulture)).Append(" },\n");
            sb.Append("  \"fps\": \"NEED PROFILE (not measured here)\"\n");
            sb.Append("}\n");
            return sb.ToString();
        }

        private void Write()
        {
            var report = Report();
            Debug.Log("[p34stress] " + report.Replace("\n", " "));
#if UNITY_EDITOR
            try
            {
                var path = System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath, "..", "Docs", "balance", "p34_stress_counts.json"));
                System.IO.File.WriteAllText(path, report);
                Debug.Log("[p34stress] written to " + path);
            }
            catch (System.Exception e)
            {
                Debug.LogWarning("[p34stress] could not write the counts: " + e.Message);
            }
#endif
        }
    }
}

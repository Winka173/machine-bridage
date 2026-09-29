using System;
using System.IO;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Navigation;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The stuck detector in the internal build (prompt 12): in the editor and in development
    /// builds (or with the -mb-stuck flag in any build) every battle is watched by the sim's
    /// <see cref="StuckWatch"/>, and when it ends its report (the vehicles that got nowhere for 8 s
    /// or more, why, and every time the safety net stepped in, with the seed, the data's
    /// fingerprint and the player's commands to play it again) is written to
    /// persistentDataPath/stuck/ and summed up in the log. It only watches: the battle is the same
    /// with it or without it.
    /// </summary>
    internal sealed class StuckReporter
    {
        private readonly StuckWatch _watch;
        private readonly string _map;
        private bool _done;

        private StuckReporter(string map, string mode, int seed)
        {
            _map = map;
            _watch = new StuckWatch(map, mode, seed, "game");
        }

        /// <summary>Whether battles are watched: the editor, a development build, or -mb-stuck.</summary>
        public static bool Enabled => Application.isEditor || Debug.isDebugBuild || DebugFlags.Has("-mb-stuck");

        /// <summary>A reporter for a battle about to start, or null when battles are not watched (a release build).</summary>
        public static StuckReporter Create(string map, GameModeKind mode, int seed) => Enabled ? new StuckReporter(map, mode.ToString(), seed) : null;

        /// <summary>After each step of the battle.</summary>
        public void Observe(SimWorld world)
        {
            if (!_done) _watch.Observe(world);
        }

        /// <summary>The battle is over (or left): the report is written once.</summary>
        public void Finish(SimWorld world)
        {
            if (_done || world == null) return;
            _done = true;
            _watch.Finish(world);
            var over = _watch.CountOver(10.0);
            Debug.Log($"[Stuck] {_watch.Mode} on {_map}, seed {_watch.Seed}: {_watch.Records.Count} vehicles stuck 8 s or more, {over} over 10 s, " +
                      $"{_watch.Rescues.Count} safety-net activations");
            if (_watch.Records.Count == 0 && _watch.Rescues.Count == 0) return;
            try
            {
                var dir = Path.Combine(Application.persistentDataPath, "stuck");
                Directory.CreateDirectory(dir);
                var file = Path.Combine(dir, $"{_watch.Mode.ToLowerInvariant()}_{_map}_s{_watch.Seed}_{DateTime.UtcNow:yyyyMMdd_HHmmss}.json");
                File.WriteAllText(file, _watch.ToJson(world, $"app {Application.version}"));
                Debug.Log("[Stuck] report: " + file);
            }
            catch (Exception e)
            {
                Debug.LogWarning("[Stuck] could not write the report: " + e.Message);
            }
        }
    }
}

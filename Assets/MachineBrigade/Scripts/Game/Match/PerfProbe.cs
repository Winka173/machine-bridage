using System;
using System.Diagnostics;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using Debug = UnityEngine.Debug;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Frame-time probe for device testing (debug flag -mb-perf). Every few seconds it logs frame
    /// time percentiles, hitches, garbage collections, draw calls and where the main thread went;
    /// every hitch is logged on its own with the same breakdown, so stutter can be traced from
    /// logcat without attaching the profiler.
    /// </summary>
    internal sealed class PerfProbe : IDisposable
    {
        public enum Section
        {
            Sim,
            Events,
            Effects,
            Views,
            Hud,
            Audio,
            Scenery,
            Count,
        }

        private const float ReportSeconds = 5f;
        private const float HitchSeconds = 0.034f;

        private readonly Stopwatch _watch = new();
        private readonly double[] _section = new double[(int)Section.Count];
        private readonly double[] _sectionTotal = new double[(int)Section.Count];
        private readonly float[] _frames = new float[1024];
        private readonly StringBuilder _text = new();
        /// <summary>Engine markers worth watching: rendering, waiting on the GPU, UI, particles.</summary>
        private static readonly string[] MarkerNames =
        {
            "Gfx.WaitForPresentOnGfxThread", "Gfx.WaitForRenderThread", "Gfx.PresentFrame",
            "RenderPipelineManager.DoRenderLoop_Internal()", "MainLightShadow", "DrawOpaqueObjects", "DrawTransparentObjects",
            "UberPostProcess", "Bloom", "UIElementsUpdatePanels", "UIR.DrawChain", "UIElementsRepaintPanels", "ParticleSystem.Update",
            "ParticleSystem.WaitForUpdateThreads", "Physics.Simulate", "Culling", "PostLateUpdate.FinishFrameRendering",
        };

        private readonly UnityEngine.Profiling.Recorder[] _markers = new UnityEngine.Profiling.Recorder[MarkerNames.Length];
        private readonly double[] _markerTotal = new double[MarkerNames.Length];
        private ProfilerRecorder _drawCalls, _batches, _setPass, _triangles, _gcAlloc, _mainThread;
        private int _frameCount, _hitches, _gcStart, _steps;
        private float _reportAt;
        private long _drawTotal, _allocTotal;

        private PerfProbe()
        {
            _drawCalls = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count");
            _batches = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Batches Count");
            _setPass = ProfilerRecorder.StartNew(ProfilerCategory.Render, "SetPass Calls Count");
            _triangles = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Triangles Count");
            _gcAlloc = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
            _mainThread = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 15);
            _gcStart = GC.CollectionCount(0);
            _reportAt = Time.realtimeSinceStartup + ReportSeconds;
            for (var i = 0; i < MarkerNames.Length; i++)
            {
                _markers[i] = UnityEngine.Profiling.Recorder.Get(MarkerNames[i]);
                if (_markers[i].isValid) _markers[i].enabled = true;
            }
        }

        /// <summary>A probe when -mb-perf is set, otherwise null (every call site uses ?.).</summary>
        public static PerfProbe Create() => DebugFlags.Has("-mb-perf") ? new PerfProbe() : null;

        public void Begin() => _watch.Restart();

        public void End(Section section)
        {
            _section[(int)section] += _watch.Elapsed.TotalMilliseconds;
        }

        public void CountSteps(int steps) => _steps += steps;

        /// <summary>Extra state for each report (the vehicles' detail levels).</summary>
        public Func<string> Detail { get; set; }

        /// <summary>Call once per frame, at the end of LateUpdate.</summary>
        public void EndFrame(int vehicles)
        {
            var dt = Time.unscaledDeltaTime;
            if (_frameCount < _frames.Length) _frames[_frameCount++] = dt;
            var draws = _drawCalls.Valid ? _drawCalls.LastValue : 0;
            var alloc = _gcAlloc.Valid ? _gcAlloc.LastValue : 0;
            _drawTotal += draws;
            _allocTotal += alloc;
            for (var i = 0; i < _section.Length; i++) _sectionTotal[i] += _section[i];
            for (var i = 0; i < _markers.Length; i++)
                if (_markers[i].isValid) _markerTotal[i] += _markers[i].elapsedNanoseconds / 1e6;

            if (dt > HitchSeconds && Time.frameCount > 30)
            {
                _hitches++;
                _text.Clear();
                _text.Append($"[Perf] HITCH {dt * 1000f:0} ms steps={_steps} gc={GC.CollectionCount(0) - _gcStart} alloc={alloc / 1024}KB draws={draws} ");
                AppendSections(_section, 1);
                Debug.Log(_text.ToString());
            }
            Array.Clear(_section, 0, _section.Length);
            _steps = 0;

            if (Time.realtimeSinceStartup < _reportAt || _frameCount == 0) return;
            _reportAt = Time.realtimeSinceStartup + ReportSeconds;
            Array.Sort(_frames, 0, _frameCount);
            var total = 0f;
            for (var i = 0; i < _frameCount; i++) total += _frames[i];
            var p50 = _frames[_frameCount / 2] * 1000f;
            var p95 = _frames[Mathf.Min(_frameCount - 1, (int)(_frameCount * 0.95f))] * 1000f;
            var max = _frames[_frameCount - 1] * 1000f;
            _text.Clear();
            _text.Append($"[Perf] fps={_frameCount / total:0.0} p50={p50:0.0} p95={p95:0.0} max={max:0} hitches={_hitches} " +
                         $"gc={GC.CollectionCount(0) - _gcStart} alloc/frame={_allocTotal / _frameCount / 1024f:0.0}KB " +
                         $"draws={_drawTotal / _frameCount} batches={(_batches.Valid ? _batches.LastValue : 0)} " +
                         $"setpass={(_setPass.Valid ? _setPass.LastValue : 0)} tris={(_triangles.Valid ? _triangles.LastValue / 1000 : 0)}k " +
                         $"main={(_mainThread.Valid ? _mainThread.LastValue / 1e6 : 0):0.0}ms vehicles={vehicles} {Detail?.Invoke()} | ");
            AppendSections(_sectionTotal, _frameCount);
            _text.Append("| ");
            for (var i = 0; i < _markers.Length; i++)
            {
                var ms = _markerTotal[i] / _frameCount;
                if (ms >= 0.2) _text.Append($"{MarkerNames[i]}={ms:0.0} ");
            }
            Array.Clear(_markerTotal, 0, _markerTotal.Length);
            Debug.Log(_text.ToString());
            _frameCount = 0;
            _hitches = 0;
            _drawTotal = 0;
            _allocTotal = 0;
            _gcStart = GC.CollectionCount(0);
            Array.Clear(_sectionTotal, 0, _sectionTotal.Length);
        }

        /// <summary>Logs how many renderers and triangles each part of the scene holds (once, early in a match).</summary>
        public void Census(long instancedTriangles, int instancedBatches)
        {
            var groups = new System.Collections.Generic.Dictionary<string, (int renderers, long triangles)>();
            foreach (var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>())
            {
                if (!renderer.enabled || !renderer.gameObject.activeInHierarchy) continue;
                var filter = renderer.GetComponent<MeshFilter>();
                if (filter == null || filter.sharedMesh == null) continue;
                long triangles = 0;
                for (var i = 0; i < filter.sharedMesh.subMeshCount; i++) triangles += filter.sharedMesh.GetIndexCount(i) / 3;
                var t = renderer.transform;
                while (t.parent != null && t.parent.parent != null) t = t.parent;
                var key = t.name;
                groups.TryGetValue(key, out var g);
                groups[key] = (g.renderers + 1, g.triangles + triangles);
            }
            _text.Clear();
            _text.Append($"[Perf] CENSUS instanced={instancedTriangles / 1000}k tris in {instancedBatches} batches | ");
            foreach (var (name, (renderers, triangles)) in groups)
                _text.Append($"{name}: {renderers} renderers {triangles / 1000}k tris; ");
            Debug.Log(_text.ToString());
        }

        public void Dispose()
        {
            _drawCalls.Dispose();
            _batches.Dispose();
            _setPass.Dispose();
            _triangles.Dispose();
            _gcAlloc.Dispose();
            _mainThread.Dispose();
        }

        private void AppendSections(double[] values, int frames)
        {
            for (var i = 0; i < (int)Section.Count; i++)
                _text.Append($"{(Section)i}={values[i] / frames:0.00} ");
        }
    }
}

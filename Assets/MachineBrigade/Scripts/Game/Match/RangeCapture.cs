using System.Collections;
using System.Collections.Generic;
using System.IO;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Development only: films the detail page's In action range for chosen vehicles, frame by
    /// frame at a fixed game-time step (Time.captureFramerate), so how a shot looks can be judged
    /// on a slow emulator as it would play on a phone. <c>-mb-range=apc+ifv</c> (or <c>all</c>),
    /// <c>-mb-range-secs=8</c>, <c>-mb-range-fps=10</c>, <c>-mb-range-hd</c> for 1280 x 960; the frames
    /// go to <c>persistentDataPath/range/&lt;id&gt;_&lt;n&gt;.jpg</c>, then <c>done.txt</c>.
    /// </summary>
    public sealed class RangeCapture : MonoBehaviour
    {
        private const int Rate = 30;

        public static bool Active { get; private set; }

        private UnitPreview _preview;
        private List<string> _ids;
        private float _seconds = 8f;
        private int _every = 3;

        public static void TryStart(GameObject host, UnitPreview preview, Catalog catalog)
        {
            var list = DebugFlags.Value("-mb-range=");
            if (string.IsNullOrEmpty(list) || Active) return;
            var ids = new List<string>();
            foreach (var id in list.Split('+'))
            {
                if (id == "all") ids.AddRange(catalog.Vehicles.Keys);
                else if (catalog.Vehicles.ContainsKey(id)) ids.Add(id);
            }
            if (ids.Count == 0) return;
            var capture = host.AddComponent<RangeCapture>();
            capture._preview = preview;
            capture._ids = ids;
            if (float.TryParse(DebugFlags.Value("-mb-range-secs="), out var seconds)) capture._seconds = seconds;
            if (int.TryParse(DebugFlags.Value("-mb-range-fps="), out var fps) && fps > 0) capture._every = Mathf.Max(1, Rate / fps);
            if (DebugFlags.Has("-mb-range-hd")) preview.Resize(1280, 960);
            if (float.TryParse(DebugFlags.Value("-mb-range-zoom="), System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out var zoom)) FiringRange.Zoom = Mathf.Max(1f, zoom);
            Active = true;
        }

        private IEnumerator Start()
        {
            // Let the menu and the lobby settle first.
            for (var i = 0; i < 90; i++) yield return null;
            var dir = Path.Combine(Application.persistentDataPath, "range");
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
            Directory.CreateDirectory(dir);
            Time.captureFramerate = Rate;
            var frame = new Texture2D(_preview.Texture.width, _preview.Texture.height, TextureFormat.RGB24, false);
            var endOfFrame = new WaitForEndOfFrame();
            var log = new System.Text.StringBuilder();
            FiringRange.Log = (t, e) =>
            {
                if (e.Kind == Sim.Events.SimEventKind.WeaponFired) log.AppendLine($"{t:0.00} fired mount {e.Mount} {e.DefId}");
            };
            foreach (var id in _ids)
            {
                log.AppendLine("== " + id);
                _preview.ShowRange(id);
                var frames = Mathf.RoundToInt(_seconds * Rate);
                for (var f = 0; f < frames; f++)
                {
                    _preview.Tick(1f / Rate);
                    yield return endOfFrame;
                    if (f % _every != 0) continue;
                    RenderTexture.active = _preview.Texture;
                    frame.ReadPixels(new Rect(0, 0, frame.width, frame.height), 0, 0);
                    frame.Apply(false);
                    RenderTexture.active = null;
                    File.WriteAllBytes(Path.Combine(dir, $"{id}_{f / _every:000}.jpg"), frame.EncodeToJPG(88));
                }
                Debug.Log($"[RangeCapture] {id}");
            }
            Time.captureFramerate = 0;
            FiringRange.Log = null;
            File.WriteAllText(Path.Combine(dir, "events.txt"), log.ToString());
            _preview.Hide();
            File.WriteAllText(Path.Combine(dir, "done.txt"), string.Join(" ", _ids));
            Active = false;
        }
    }
}

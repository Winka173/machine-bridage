using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// A marking painted on the ground with the GroundMark shader: objective circles, strike
    /// telegraphs, selection brackets, move markers and aircraft rings. The quad has a radius
    /// of 1; scale its transform to the radius wanted. Values go through a property block and
    /// are only pushed when they change.
    /// </summary>
    public sealed class GroundMark
    {
        public enum Style
        {
            Objective = 0,
            Strike = 1,
            Selection = 2,
            Move = 3,
            Aircraft = 4,

            /// <summary>Fix prompt L5: a warning ring (a thin edge, a faint fill heavier toward the middle, the time left round the edge).</summary>
            Warning = 5,

            /// <summary>
            /// The bomb-run fix, pass 3: a stick's warning rectangle (STICK_RECT): a thin edge, a faint fill heavier toward its
            /// long middle line and the flight line dashed along it. The quad is scaled to the rectangle (x: half its width, z:
            /// half its length, its local z along the stick).
            /// </summary>
            WarningRect = 6,
        }

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly int AccentId = Shader.PropertyToID("_Accent");
        private static readonly int ParamsId = Shader.PropertyToID("_Params");

        private readonly MeshRenderer _renderer;
        private readonly MaterialPropertyBlock _block = new();
        private readonly float _seed;
        private float _style;
        private Color _color, _accent;
        private float _progress = -1f, _pulse = -1f;

        public GroundMark(string name, Transform parent, MeshLibrary meshes, MaterialLibrary materials, Style style)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = meshes.GroundQuad;
            _renderer = go.AddComponent<MeshRenderer>();
            _renderer.sharedMaterial = materials.GroundMark;
            _renderer.shadowCastingMode = ShadowCastingMode.Off;
            _renderer.receiveShadows = false;
            Transform = go.transform;
            _style = (int)style;
            _seed = Random.value;
        }

        public Transform Transform { get; }

        public bool Visible
        {
            get => _renderer.enabled;
            set
            {
                if (_renderer.enabled != value) _renderer.enabled = value;
            }
        }

        /// <summary>Fix prompt L5: draws it in another style from now on (a pooled mark reused as a warning ring).</summary>
        public void Restyle(Style style)
        {
            if (Mathf.Approximately(_style, (int)style)) return;
            _style = (int)style;
            _progress = -1f;
        }

        /// <summary>
        /// MVA W2-B (spec part Q1): the least boost a danger telegraph gets in this weather (WeatherPresentation.TelegraphBoost,
        /// 1 to 1.3): its colour brighter and its alpha fuller (capped at 1). Set by Rendering.Weather.
        /// </summary>
        public static float TelegraphBoost { get; set; } = 1f;

        private static Color Boost(Color c) => new(c.r * TelegraphBoost, c.g * TelegraphBoost, c.b * TelegraphBoost, Mathf.Min(1f, c.a * TelegraphBoost));

        public void Set(Color color, Color accent, float progress = 0f, float pulse = 0f)
        {
            if (color == _color && accent == _accent && Mathf.Abs(progress - _progress) < 0.002f && Mathf.Abs(pulse - _pulse) < 0.01f) return;
            _color = color;
            _accent = accent;
            _progress = progress;
            _pulse = pulse;
            // MVA W2-B (spec parts Q1, AM): a danger telegraph (warning ring, stick rectangle, strike zone) gets the weather's
            // boost, so fog, snow or a sandstorm never fade it out; the other marks draw as given.
            var style = Mathf.RoundToInt(_style);
            if ((style == (int)Style.Warning || style == (int)Style.WarningRect || style == (int)Style.Strike) && TelegraphBoost > 1f)
            {
                color = Boost(color);
                accent = Boost(accent);
            }
            _block.SetColor(ColorId, color);
            _block.SetColor(AccentId, accent);
            _block.SetVector(ParamsId, new Vector4(_style, progress, pulse, _seed));
            _renderer.SetPropertyBlock(_block);
        }
    }
}

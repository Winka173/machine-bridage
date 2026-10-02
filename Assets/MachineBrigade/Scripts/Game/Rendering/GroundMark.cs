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

        public void Set(Color color, Color accent, float progress = 0f, float pulse = 0f)
        {
            if (color == _color && accent == _accent && Mathf.Abs(progress - _progress) < 0.002f && Mathf.Abs(pulse - _pulse) < 0.01f) return;
            _color = color;
            _accent = accent;
            _progress = progress;
            _pulse = pulse;
            _block.SetColor(ColorId, color);
            _block.SetColor(AccentId, accent);
            _block.SetVector(ParamsId, new Vector4(_style, progress, pulse, _seed));
            _renderer.SetPropertyBlock(_block);
        }
    }
}

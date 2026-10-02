using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Fix prompt L6 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): the smoke and dust a blast leaves after its own recipe is
    /// done, as long as its size band says (<see cref="EffectLife"/>): a low haze for 20-155 mm (play-test 12: 0.5-1 s, 1.5-2.5 s, 3-5 s), a
    /// standing column for 203 mm and up (6-10 s), and a tall one for 406 mm and the super weapons (10-15 s), each
    /// drifting off on the wind and fading out slowly (never blinking out). Added on top of what every blast always drew.
    /// <list type="bullet">
    /// <item>At most <see cref="BigColumns"/> (3) big columns at once: a new one makes the older ones fade faster
    /// (<see cref="FastFade"/>), the oldest giving its slot up.</item>
    /// <item>By distance (TierFx.DetailAt): full near the view; half the puffs in the middle distance; far off no haze and a
    /// thin column.</item>
    /// <item>Pooled: two particle systems (emitted by hand) and a fixed set of column slots; nothing is made in battle.</item>
    /// <item>View only: the Sim's sight never sees it (smoke that blocks sight is the smoke screens').</item>
    /// </list>
    /// </summary>
    internal sealed class ImpactSmoke
    {
        public const int BigColumns = 3;

        /// <summary>Seconds an older column takes to clear once a new one stands (a whole column at most this long).</summary>
        public const float FastFade = 4f;

        /// <summary>Seconds between a column's billows (twice that far off).</summary>
        private const float BillowGap = 0.45f;

        /// <summary>A column keeps billowing up for this share of its life, then hangs and fades.</summary>
        private const float BillowShare = 0.55f;

        private sealed class Column
        {
            public Vector3 At;
            public float Start, End, Next, Size;
            public uint Seed;
            public bool Active, Tall, Thin;
        }

        private readonly ParticleSystem _haze;
        private readonly ParticleSystem _column;
        private readonly Column[] _columns = new Column[BigColumns];
        private readonly ParticleSystem.Particle[] _buffer;
        private uint _seed = 1;

        public ImpactSmoke(Transform parent)
        {
            var root = new GameObject("Impact Smoke").transform;
            root.SetParent(parent, false);
            var fx = FxMaterials.Shared;
            // The low haze: grey-brown, spreading and paling as it drifts, fading in and out softly.
            _haze = Manual(root, "Lingering Haze", fx.Smoke, 900);
            PB.Flipbook(_haze, loop: false, tilt: 22f, from: 0.1f);
            PB.Colors(_haze, PB.Hold(new Color(0.42f, 0.39f, 0.35f), new Color(0.62f, 0.6f, 0.57f), 0.12f, 0.45f, 0.55f));
            PB.Grow(_haze, 0.7f, 2.1f);
            PB.Rise(_haze, 0.15f, 0.55f);
            Drag(_haze, 0.35f);
            // The column: dark billows climbing, paling as they rise and lean off with the wind, a long soft fade.
            _column = Manual(root, "Lingering Column", fx.Smoke, 700);
            PB.Flipbook(_column, loop: false, tilt: 14f, from: 0.08f);
            PB.Colors(_column, PB.Hold(new Color(0.14f, 0.13f, 0.125f), new Color(0.55f, 0.54f, 0.53f), 0.1f, 0.4f, 0.85f));
            PB.Grow(_column, 0.6f, 2.8f);
            var vol = _column.velocityOverLifetime;
            vol.enabled = true;
            vol.space = ParticleSystemSimulationSpace.World;
            // The wind takes it more the higher it gets (the drift grows over each billow's life).
            var lean = AnimationCurve.Linear(0f, 0.4f, 1f, 1.6f);
            vol.x = new ParticleSystem.MinMaxCurve(PB.Wind.x * 1.4f, lean);
            vol.y = new ParticleSystem.MinMaxCurve(0.25f, AnimationCurve.Linear(0f, 1f, 1f, 0.2f));
            vol.z = new ParticleSystem.MinMaxCurve(PB.Wind.z * 1.4f, lean);
            Drag(_column, 0.12f);
            _buffer = new ParticleSystem.Particle[_column.main.maxParticles];
            for (var i = 0; i < _columns.Length; i++) _columns[i] = new Column();
        }

        /// <summary>Big columns standing now (tests).</summary>
        internal int Standing
        {
            get
            {
                var n = 0;
                foreach (var c in _columns)
                    if (c.Active) n++;
                return n;
            }
        }

        /// <summary>
        /// A blast of <paramref name="band"/> at <paramref name="at"/> (its core <paramref name="core"/> m) at
        /// <paramref name="now"/>: the smoke and dust it leaves behind, at <paramref name="detail"/>.
        /// </summary>
        public void Linger(int band, Vector3 at, float core, float now, TierFx.Detail detail)
        {
            if (band <= 0) return; // up to 14.5 mm: its own half-second puff is all
            var life = EffectLife.Of(band);
            var ground = new Vector3(at.x, Mathf.Max(0.3f, at.y), at.z);
            if (band >= 4)
            {
                Raise(band >= 5, ground, Mathf.Max(core, band >= 5 ? 14f : 8f), Random.Range(life.SmokeMin, life.SmokeMax), now,
                    detail == TierFx.Detail.Far);
                return;
            }
            if (detail == TierFx.Detail.Far) return;
            var puffs = detail == TierFx.Detail.Full ? band + 1 : Mathf.Max(1, band / 2);
            var size = Mathf.Clamp(core > 0f ? core * 0.9f : band * 1.2f, 1.2f, 7f);
            for (var k = 0; k < puffs; k++)
            {
                var spot = ground + new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)) * size * 0.4f + Vector3.up * Random.Range(0.2f, 0.8f);
                Emit(_haze, spot, Vector3.up * Random.Range(0.2f, 0.6f), size * Random.Range(0.8f, 1.15f), Random.Range(life.SmokeMin, life.SmokeMax), 0);
            }
        }

        /// <summary>A big column: the newest takes a free slot or the oldest's; the others clear faster now.</summary>
        private void Raise(bool tall, Vector3 at, float core, float seconds, float now, bool thin)
        {
            Column slot = null;
            foreach (var c in _columns)
            {
                if (!c.Active)
                {
                    slot ??= c;
                    continue;
                }
                // An older column clears faster when a new one stands.
                Hurry(c, now);
            }
            if (slot == null)
            {
                slot = _columns[0];
                foreach (var c in _columns)
                    if (c.Start < slot.Start) slot = c;
                Clear(slot, now, 1.2f);
            }
            slot.Active = true;
            slot.At = at;
            slot.Start = now;
            slot.End = now + seconds;
            slot.Next = now + 0.25f;
            slot.Size = Mathf.Clamp(core * (tall ? 0.7f : 0.75f), 5f, tall ? 16f : 10f);
            slot.Tall = tall;
            slot.Thin = thin;
            slot.Seed = _seed++;
            if (_seed == 0) _seed = 1;
        }

        /// <summary>A column told to clear: it billows no more and its smoke has at most <see cref="FastFade"/> s left.</summary>
        private void Hurry(Column c, float now) => Clear(c, now, FastFade);

        private void Clear(Column c, float now, float within)
        {
            if (c.End <= now + within) return;
            c.End = now + within;
            var n = _column.GetParticles(_buffer);
            for (var i = 0; i < n; i++)
            {
                if (_buffer[i].randomSeed != c.Seed || _buffer[i].remainingLifetime <= within) continue;
                // Its age kept, its end brought in: the fade-out plays from where it is.
                var age = _buffer[i].startLifetime - _buffer[i].remainingLifetime;
                _buffer[i].startLifetime = age + within;
                _buffer[i].remainingLifetime = within;
            }
            _column.SetParticles(_buffer, n);
        }

        /// <summary>Every frame: the standing columns billow on, each billow living out the column's time.</summary>
        public void Tick(float now)
        {
            foreach (var c in _columns)
            {
                if (!c.Active) continue;
                if (now >= c.End)
                {
                    c.Active = false;
                    continue;
                }
                var life = c.End - c.Start;
                var billowsUntil = c.Start + life * BillowShare;
                var gap = c.Thin ? BillowGap * 2f : BillowGap;
                var guard = 0;
                while (c.Next <= now && c.Next < billowsUntil && guard++ < 8)
                {
                    var t = Mathf.Clamp01((c.Next - c.Start) / Mathf.Max(0.1f, life * BillowShare));
                    // Low and dark at the root, then climbing (a tall one twice as high).
                    var height = (c.Tall ? 2.4f : 1.5f) + t * (c.Tall ? 9f : 5f);
                    var spot = c.At + new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)) * c.Size * 0.18f + Vector3.up * height * 0.35f;
                    var rise = Vector3.up * Random.Range(c.Tall ? 1.6f : 1f, c.Tall ? 2.6f : 1.7f);
                    var left = Mathf.Max(1.5f, c.End - c.Next);
                    Emit(_column, spot, rise, c.Size * Random.Range(0.85f, 1.15f) * (0.8f + 0.4f * t), left * Random.Range(0.9f, 1f), c.Seed);
                    c.Next += gap * Random.Range(0.8f, 1.2f);
                }
            }
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime, uint seed)
        {
            var emit = new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                rotation = Random.Range(-14f, 14f),
                applyShapeToPosition = false,
            };
            if (seed != 0) emit.randomSeed = seed;
            system.Emit(emit, 1);
        }

        private static ParticleSystem Manual(Transform parent, string name, Material material, int max)
        {
            var ps = PB.Create(parent, name, material);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play(true);
            return ps;
        }

        private static void Drag(ParticleSystem ps, float drag)
        {
            var limit = ps.limitVelocityOverLifetime;
            limit.enabled = true;
            limit.limit = new ParticleSystem.MinMaxCurve(40f);
            limit.drag = new ParticleSystem.MinMaxCurve(drag);
            limit.multiplyDragByParticleSize = false;
            limit.multiplyDragByParticleVelocity = false;
        }
    }
}

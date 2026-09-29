using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Draws one vehicle. It reads the simulation after each fixed step and interpolates between
    /// the last two steps every frame. On top of that it adds life the simulation does not need:
    /// barrel recoil, hull pitch when accelerating or braking, a light bounce on the move, turning
    /// weapon mounts, spinning rotors, and flight (altitude, banking) for aircraft.
    /// </summary>
    public sealed partial class VehicleView
    {
        private const float BarWidth = 2.4f;
        private const float BarHeight = 0.2f;
        private const float RecoilSeconds = 0.35f;
        /// <summary>Aircraft fly in over this long: from behind along their heading, a little above their height.</summary>
        private const float ArriveSeconds = 2.6f;

        private static readonly int TintId = Shader.PropertyToID("_Tint");

        private readonly ModelInstance _model;
        private readonly Transform _body;
        private readonly GroundMark _ring;
        private readonly GroundMark _shadowRing;
        private readonly Transform _bar;
        private readonly Transform _barFill;
        private readonly Transform _barTrail;
        private readonly Vector3[] _recoilRest;
        private readonly float _recoilDistance;
        private readonly Transform[] _mounts;
        private readonly Transform[] _muzzles;
        private readonly float[] _previousMount, _currentMount;
        private readonly float _spawnTime;
        private Vector3 _previousPosition, _currentPosition;
        private float _previousHeading, _currentHeading, _previousTurret, _currentTurret;
        private float _previousSpeed, _currentSpeed;
        private float _recoilTime = -10f;
        private float _pitch, _bank;

        /// <summary>An aeroplane's attack hold eased in and out (0-1), and the height it has climbed breaking away from one (see VehicleDef.AttackHold).</summary>
        private float _hold, _climb, _climbRate;

        /// <summary>Metres an aeroplane climbs as it breaks away from its attack hold (and dives back down coming in again).</summary>
        private const float BreakClimb = 5f;

        /// <summary>
        /// Editor shot tools (AirHoldShots): the step, in seconds, the flight pose animates by each
        /// render, and the clock it reads; negative, the real frame time (the game).
        /// </summary>
        public static float ShotStep = -1f;

        public static float ShotClock;

        private static float FrameStep => ShotStep >= 0f ? ShotStep : Time.deltaTime;
        private static float FrameTime => ShotStep >= 0f ? ShotClock : Time.time;
        private float _bouncePhase;
        private float _spin;
        private float _crashStart = -1f;
        private float _crashHeight;
        private Vector3 _crashDrift;
        private bool _wreck;

        // Parts some models animate from the simulation: the Doomsday Train's missile erector and a
        // guard tower's searchlight. Null on every other model.
        private readonly Transform _erector, _searchlight;
        private readonly Quaternion _erectorRest, _searchlightRest;

        /// <summary>Its side is the player's (its shield is drawn blue, else red-orange).</summary>
        private readonly bool _ours;

        public VehicleView(Vehicle vehicle, ModelLibrary models, MeshLibrary meshes, MaterialLibrary materials,
            Transform parent, int playerTeam)
        {
            Sim = vehicle;
            Def = vehicle.Def;
            Root = new GameObject($"{vehicle.Def.Id} {vehicle.Id}").transform;
            Root.SetParent(parent, false);
            _body = new GameObject("Body").transform;
            _body.SetParent(Root, false);
            // A boss in a later form wears that form's model.
            _model = models.Spawn(vehicle.Form != null && models.Has(vehicle.Form) ? vehicle.Form : vehicle.Def.Model, vehicle.Team, _body, lod: VehicleLod.Enabled);
            // The whole drawn vehicle takes the def's scale (muzzles, turret and wreck included).
            _body.localScale = Vector3.one * vehicle.Def.Scale;
            ModelBounds = Measure(_model.Root.transform, _body);
            if (vehicle.Def.Flying) BuildNavLights(meshes, materials);
            _spawnTime = Time.time;

            _recoilRest = new Vector3[_model.RecoilParts.Count];
            for (var i = 0; i < _recoilRest.Length; i++) _recoilRest[i] = _model.RecoilParts[i].localPosition;
            // Several barrels (Main_cannon, Main_cannon_2...): they fire in turn, each from its own tip.
            _barrelOf = new int[_recoilRest.Length];
            var tips = new List<Transform>();
            for (var i = 0; i < _recoilRest.Length; i++)
            {
                var part = _model.RecoilParts[i];
                // Main_cannon_2 is the second barrel (Main_cannon_2_gilt with it); _L and _R are the left and right.
                var suffix = System.Text.RegularExpressions.Regex.Match(part.name, @"^(?:Main_cannon|Muzzle_brake)_(\d+|L|R)(?![a-z])",
                    System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                var barrel = !suffix.Success ? 0 : suffix.Groups[1].Value.ToUpperInvariant() switch
                {
                    "L" => 0,
                    "R" => 1,
                    var n => int.Parse(n) - 1,
                };
                _barrelOf[i] = barrel;
                while (tips.Count <= barrel) tips.Add(null);
                if (tips[barrel] == null || part.name.StartsWith("Muzzle_brake")) tips[barrel] = part;
            }
            if (tips.Count > 1 && !tips.Contains(null))
            {
                // Where each barrel really is: the middle of its tip's mesh (part origins can all sit on the trunnion).
                _barrelTipOffsets = new Vector3[tips.Count];
                for (var i = 0; i < tips.Count; i++)
                {
                    var filter = tips[i].GetComponentInChildren<MeshFilter>();
                    _barrelTipOffsets[i] = filter != null && filter.sharedMesh != null
                        ? tips[i].InverseTransformPoint(filter.transform.TransformPoint(filter.sharedMesh.bounds.center))
                        : Vector3.zero;
                }
                _barrelTips = tips.ToArray();
                if (!SideBySide()) _barrelTips = null;
            }
            _recoilDistance = Mathf.Clamp(vehicle.Radius * 0.18f, 0.12f, 0.45f);

            var mounts = Def.Mounts;
            _mounts = new Transform[mounts.Count];
            _muzzles = new Transform[mounts.Count];
            _launchers = new List<LaunchPoint>[mounts.Count];
            _nextLauncher = new int[mounts.Count];
            _previousMount = new float[mounts.Count];
            _currentMount = new float[mounts.Count];
            var sameSlot = new Dictionary<string, int>();
            _ownBarrel = new int[mounts.Count];
            var onMainSlot = 0;
            foreach (var m in mounts)
                if (m.Slot == mounts[0].Slot) onMainSlot++;
            for (var i = 0; i < mounts.Count; i++)
            {
                // The k-th mount of a slot in the data is the k-th Mount_/Muzzle_ of it in the model.
                var slot = mounts[i].Slot;
                var k = sameSlot.TryGetValue(slot, out var seen) ? seen : 0;
                sameSlot[slot] = k + 1;
                // Two weapons on the main gun's slot of a twin-barrelled model (the Inferno's two
                // flame projectors): each fires from its own barrel, the k-th, instead of both from
                // the muzzle between them (DECISIONS 12A).
                _ownBarrel[i] = _barrelTips != null && onMainSlot > 1 && slot == mounts[0].Slot ? k % _barrelTips.Length : -1;
                if (_model.MountLists.TryGetValue(slot, out var mountList) && mountList.Count > 1) _mounts[i] = mountList[k % mountList.Count];
                else _model.Mounts.TryGetValue(slot, out _mounts[i]);
                if (_model.MuzzleLists.TryGetValue(slot, out var muzzleList) && muzzleList.Count > 1) _muzzles[i] = muzzleList[k % muzzleList.Count];
                else _model.Muzzles.TryGetValue(slot, out _muzzles[i]);
                // Rockets, missiles and drones leave from the pods and rails on both sides in turn;
                // twin miniguns from both guns. With two mounts of a slot, each has the pods on it.
                var kind = mounts[i].Weapon.Projectile;
                if (_model.Launchers.TryGetValue(slot, out var launchers) &&
                    (kind is ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Drone || slot == "gun"))
                {
                    var own = launchers;
                    if (sameSlot[slot] > 0 && mountList != null && mountList.Count > 1 && _mounts[i] != null)
                    {
                        own = launchers.FindAll(p => p.transform.IsChildOf(_mounts[i]));
                        if (own.Count == 0) own = launchers;
                    }
                    _launchers[i] = own;
                }
            }

            _ring = new GroundMark("Selection", Root, meshes, materials, GroundMark.Style.Selection);
            _ring.Transform.localPosition = new Vector3(0f, 0.07f, 0f);
            _ring.Transform.localScale = Vector3.one * (vehicle.Radius + 0.9f);
            _ring.Set(new Color(0.55f, 1.7f, 1.15f, 1f), Color.white);
            _ring.Visible = false;
            if (vehicle.Def.Flying)
            {
                // Aircraft show where they are over the ground (and whose they are) with a faint ring.
                _shadowRing = new GroundMark("Air Ring", Root, meshes, materials, GroundMark.Style.Aircraft);
                _shadowRing.Transform.localScale = Vector3.one * (vehicle.Radius + 1.2f);
                var colour = (Color)TeamColors.Ui(vehicle.Team == playerTeam ? 0 : 1) * 1.2f;
                colour.a = 0.75f;
                _shadowRing.Set(colour, Color.white);
            }

            _bar = new GameObject("HealthBar").transform;
            _bar.SetParent(Root, false);
            _bar.localPosition = new Vector3(0f, _model.Muzzle.y * vehicle.Def.Scale + 1.9f, 0f);
            var back = CreateMesh("Back", _bar, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(BarWidth + 0.14f, BarHeight + 0.14f, 1f);
            _barTrail = CreateMesh("Trail", _bar, meshes.Quad, materials.BarTrail, false);
            _barTrail.localPosition = new Vector3(0f, 0f, -0.01f);
            _barFill = CreateMesh("Fill", _bar, meshes.Quad,
                vehicle.Team == playerTeam ? materials.BarAlly : vehicle.Team == Teams.Hostile ? materials.BarNeutral : materials.BarEnemy, false);
            _barFill.localPosition = new Vector3(0f, 0f, -0.02f);
            // Prompt 13 C.9: the stores icon for aircraft, helicopters and launchers (it took over the three-shell gauge).
            if (vehicle.HasStores || vehicle.Def.Mounts[0].Weapon.Ammo > 0) BuildStoresMark(meshes, materials);
            BuildRepairMark(meshes, materials);
            _bar.gameObject.SetActive(false);

            foreach (var t in _model.Root.GetComponentsInChildren<Transform>(true))
            {
                if (t.name == "Erector") _erector = t;
                else if (t.name == "Searchlight") _searchlight = t;
                else if (t.name == "Lift") _lift = t;
            }
            if (_lift != null) _liftRest = _lift.localPosition;
            if (_erector != null) _erectorRest = _erector.localRotation;
            if (_searchlight != null) _searchlightRest = _searchlight.localRotation;
            _ours = vehicle.Team == playerTeam;
            AddRotorBlur(materials);
            InitParts(models, meshes, materials);
            // Elite enemies wear a gold health bar.
            if (vehicle.Def.Elite && vehicle.Team != playerTeam) _barFill.GetComponent<MeshRenderer>().sharedMaterial = materials.BarElite;

            Snapshot();
            Snapshot(); // previous == current, so the first frame does not interpolate from the origin
            Render(1f, Quaternion.identity);
        }

        public Vehicle Sim { get; }
        public VehicleDef Def { get; }
        public EntityId Id => Sim.Id;
        public int Team => Sim.Team;
        public string DefId => Def.Id;
        public Transform Root { get; }
        public Transform Turret => _model.Turret;
        public Vector3 Position => Root.position;

        /// <summary>The detail level it is drawn at (<see cref="VehicleLod"/>): 0 full, 1 simplified, 2 impostor.</summary>
        public int Level => Mathf.Max(VehicleLod.Full, _level);

        /// <summary>The model's far detail level; null when it has none (-mb-no-lod).</summary>
        public ModelLod Lod => _model.Lod;

        /// <summary>Its page in the impostor atlas (set by the views when it is made); null without one.</summary>
        public ImpostorPage Impostor { get; internal set; }

        /// <summary>How big it is in metres (length, span or height, whichever is most): what the level is chosen by.</summary>
        public float LodSize => Mathf.Max(ModelBounds.size.x, Mathf.Max(ModelBounds.size.y, ModelBounds.size.z)) * Def.Scale;

        /// <summary>Where its impostor card is centred (on its upright axis, at its middle height).</summary>
        public Vector3 ImpostorCentre => Root.position + Vector3.up * ((Impostor != null ? Impostor.Centre.y : Top * 0.5f) * Def.Scale);

        /// <summary>The impostor's tint: the hull's scorching and the hit flash (as on the meshes), the debug colour.</summary>
        public Color ImpostorTint
        {
            get
            {
                var tint = new Color(_scorch, _scorch * 0.97f, _scorch * 0.95f, 1f - _shownFlash);
                if (!VehicleLod.Colours) return tint;
                var debug = VehicleLod.Tint(VehicleLod.Impostor);
                return new Color(tint.r * debug.r, tint.g * debug.g, tint.b * debug.b, tint.a);
            }
        }

        private int _level = -1;

        /// <summary>
        /// Chooses the detail level for this frame's scale (screen pixels per metre; 0 or less
        /// keeps full detail), honouring -mb-lod=N. A wreck stays on meshes (its turret flies off).
        /// </summary>
        public void UpdateLod(float pixelsPerMetre)
        {
            var deepest = _model.Lod == null || _model.Lod1Renderers.Length == 0 ? VehicleLod.Full
                : Impostor != null && Impostor.Baked && !_wreck ? VehicleLod.Impostor
                : VehicleLod.Simple;
            int level;
            if (VehicleLod.Forced >= 0) level = Mathf.Min(VehicleLod.Forced, deepest);
            else if (pixelsPerMetre <= 0f) level = VehicleLod.Full;
            else level = VehicleLod.Choose(_level, LodSize * pixelsPerMetre, deepest);
            SetLevel(level);
        }

        /// <summary>Shows one detail level: the full model's renderers, the simplified parts, or neither (the views draw the card).</summary>
        public void SetLevel(int level)
        {
            if (level == _level) return;
            var full = level == VehicleLod.Full;
            var simple = level == VehicleLod.Simple;
            foreach (var r in _model.Renderers) r.enabled = full;
            foreach (var r in _model.Lod1Renderers) r.gameObject.SetActive(simple);
            _level = level;
            if (VehicleLod.Colours) ApplyTint();
        }

        /// <summary>Dead: a burning hulk or a falling wreck.</summary>
        public bool IsWreck => _wreck;

        /// <summary>The drawn model's extent in the body's own frame (before the def's scale): span on X, length on Z.</summary>
        public Bounds ModelBounds { get; }

        private static Bounds Measure(Transform model, Transform frame)
        {
            var bounds = new Bounds();
            var first = true;
            foreach (var filter in model.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                var b = filter.sharedMesh.bounds;
                for (var i = 0; i < 8; i++)
                {
                    var corner = b.center + Vector3.Scale(b.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = frame.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    if (first) bounds = new Bounds(p, Vector3.zero);
                    else bounds.Encapsulate(p);
                    first = false;
                }
            }
            return bounds;
        }

        private Transform _navStrobe, _navBeacon;

        /// <summary>
        /// Navigation lights, as on real aircraft: steady red on the left wingtip and green on the
        /// right, a white strobe on the tail that flashes; a helicopter adds a red anti-collision
        /// beacon on top that pulses.
        /// </summary>
        private void BuildNavLights(MeshLibrary meshes, MaterialLibrary materials)
        {
            var b = ModelBounds;
            var size = Mathf.Max(0.12f, b.size.x * 0.018f);
            // The airframe without its rotors and propellers: the lights go on its real wingtips.
            var frame = Airframe(out var tipLeft, out var tipRight);
            if (frame.size.x > 0.5f) size = Mathf.Max(0.12f, frame.size.x * 0.018f);
            // The model's left is -X in the engine (Blender's +X), the nose +Z.
            Transform Light(string name, Material material, Vector3 at)
            {
                var light = CreateMesh(name, _body, meshes.Box, material, false);
                light.localPosition = at;
                light.localScale = Vector3.one * (size / Mathf.Max(0.01f, Def.Scale));
                return light;
            }
            if (frame.size.x > 0.5f)
            {
                Light("Nav_left", materials.NavRed, tipLeft);
                Light("Nav_right", materials.NavGreen, tipRight);
                b = frame;
            }
            else
            {
                Light("Nav_left", materials.NavRed, new Vector3(b.min.x, b.center.y, b.center.z));
                Light("Nav_right", materials.NavGreen, new Vector3(b.max.x, b.center.y, b.center.z));
            }
            _navStrobe = Light("Nav_strobe", materials.NavWhite, new Vector3(b.center.x, b.max.y * 0.8f, b.min.z));
            if (!Def.FixedWing) _navBeacon = Light("Nav_beacon", materials.NavRed, new Vector3(b.center.x, b.max.y, b.center.z));
        }

        /// <summary>
        /// Bounds of the airframe in the body's space, rotors and propellers left out, and the
        /// middle of the outermost part on each side (the wingtips, a helicopter's stub wings).
        /// </summary>
        private Bounds Airframe(out Vector3 left, out Vector3 right)
        {
            left = right = Vector3.zero;
            var bounds = new Bounds();
            var first = true;
            var minX = float.MaxValue;
            var maxX = float.MinValue;
            foreach (var filter in _model.Root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null || OnSpinner(filter.transform)) continue;
                var mb = filter.sharedMesh.bounds;
                var partMin = Vector3.positiveInfinity;
                var partMax = Vector3.negativeInfinity;
                for (var i = 0; i < 8; i++)
                {
                    var corner = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = _body.InverseTransformPoint(filter.transform.TransformPoint(corner));
                    partMin = Vector3.Min(partMin, p);
                    partMax = Vector3.Max(partMax, p);
                    if (first) bounds = new Bounds(p, Vector3.zero);
                    else bounds.Encapsulate(p);
                    first = false;
                }
                var mid = (partMin + partMax) * 0.5f;
                if (partMin.x < minX)
                {
                    minX = partMin.x;
                    left = new Vector3(partMin.x, mid.y, mid.z);
                }
                if (partMax.x > maxX)
                {
                    maxX = partMax.x;
                    right = new Vector3(partMax.x, mid.y, mid.z);
                }
            }
            return bounds;
        }

        private bool OnSpinner(Transform t)
        {
            foreach (var spinner in _model.Spinners)
                if (spinner.Transform != null && t.IsChildOf(spinner.Transform)) return true;
            return false;
        }

        private void AnimateNavLights()
        {
            if (_navStrobe == null) return;
            var phase = Mathf.Repeat(Time.time + Id.Value * 0.37f, 1.2f);
            var on = phase < 0.07f || (phase > 0.16f && phase < 0.22f);
            if (_navStrobe.gameObject.activeSelf != on) _navStrobe.gameObject.SetActive(on);
            if (_navBeacon != null)
            {
                var pulse = Mathf.Repeat(Time.time * 1.1f + Id.Value * 0.21f, 1f) < 0.35f;
                if (_navBeacon.gameObject.activeSelf != pulse) _navBeacon.gameObject.SetActive(pulse);
            }
        }
        public bool Selected { get; set; }
        public bool Flying => Def.Flying;

        /// <summary>The model's body as drawn (with its pitch and bank), for effects that follow it.</summary>
        public Transform Body => _body;

        /// <summary>How far an aircraft is banked into its turn, in degrees.</summary>
        public float Bank => _bank;

        /// <summary>World-space main muzzle, for tracers and flashes.</summary>
        public Vector3 MuzzleWorld => _body.TransformPoint(_model.Muzzle);

        public float MuzzleHeight => _model.Muzzle.y * Def.Scale;

        /// <summary>Roughly how tall the model stands (where a fixed defence smokes and burns from).</summary>
        public float Top => Mathf.Max(1.5f, MuzzleHeight + 0.4f);

        private float _collapseStart = -1f;
        private Vector2 _collapseTilt;
        private float _collapseSink;

        /// <summary>Latest simulated ground speed in m/s.</summary>
        public float Speed => _currentSpeed;

        /// <summary>Next time tread dust may be kicked up; owned by the effects layer.</summary>
        public float DustAt { get; set; }

        /// <summary>Where the last track mark was printed (see EffectsDirector).</summary>
        public Vector3 TrackAt { get; set; }

        /// <summary>When the next wisp of damage smoke or lick of flame is due (see EffectsDirector).</summary>
        public float DamageFxAt { get; set; }

        private float _shownScorch = 1f;
        private float _scorch = 1f;
        private float _shownFlash;

        /// <summary>
        /// Darkens the hull as it takes damage: clean above half health, sooty and scorched as it
        /// nears destruction (the wreck tint is darker still).
        /// </summary>
        public void Scorch(float health)
        {
            if (_wreck) return;
            var shade = health >= 0.5f ? 1f : Mathf.Lerp(0.45f, 1f, health / 0.5f);
            if (Mathf.Abs(shade - _shownScorch) < 0.04f) return;
            _shownScorch = shade;
            _scorch = shade;
            ApplyTint();
        }

        private MaterialPropertyBlock _tintBlock;

        private void ApplyTint()
        {
            _tintBlock ??= new MaterialPropertyBlock();
            var tint = new Color(_scorch, _scorch * 0.97f, _scorch * 0.95f, 1f - _shownFlash);
            _tintBlock.SetColor(TintId, tint);
            foreach (var r in _model.Renderers) r.SetPropertyBlock(_tintBlock);
            if (_model.Lod1Renderers.Length == 0) return;
            if (VehicleLod.Colours)
            {
                var debug = VehicleLod.Tint(VehicleLod.Simple);
                _tintBlock.SetColor(TintId, new Color(tint.r * debug.r, tint.g * debug.g, tint.b * debug.b, tint.a));
            }
            foreach (var r in _model.Lod1Renderers) r.SetPropertyBlock(_tintBlock);
        }

        // Hit feedback: a soft white flash for a hit that takes 2 % or more at once (a shell, a
        // missile, a blast; never the patter of machine guns from every side), at most every 0.6 s;
        // heavy hits rock the hull 1.5 to 4 degrees; the health bar keeps a trail of what was just
        // lost, which catches up after 0.4 s.
        private const float FlashHold = 0.05f;
        private const float FlashFade = 0.1f;
        private const float FlashGap = 0.6f;
        private const float FlashHit = 0.02f;
        private float _hitTime = -10f;
        private float _lastHealth = 1f;
        private float _trail = 1f;
        private float _trailHoldUntil;
        private Vector2 _jolt;
        private float _joltTime = -10f;

        private void NoteHealth(float health)
        {
            var now = Time.time;
            var lost = _lastHealth - health;
            _lastHealth = health;
            if (health >= _trail) _trail = health;
            if (lost <= 0.004f) return;
            _trailHoldUntil = now + 0.4f;
            // Concrete and steel emplacements do not flash; they smoke and burn instead.
            if (lost >= FlashHit && now - _hitTime >= FlashGap && !Def.Static) _hitTime = now;
            if (lost >= 0.03f && !Flying)
            {
                var degrees = Mathf.Clamp(lost * 60f, 1.5f, 4f);
                _jolt = new Vector2(Random.Range(-1f, 1f), Random.Range(-1f, 1f)).normalized * degrees;
                _joltTime = now;
            }
        }

        private void RenderHitFeedback()
        {
            var t = Time.time - _hitTime;
            var flash = t < FlashHold ? 1f : Mathf.Clamp01(1f - (t - FlashHold) / FlashFade);
            // Aircraft take hit after hit from flak; half the flash keeps them from blinking white.
            if (Flying) flash *= 0.5f;
            if (Mathf.Abs(flash - _shownFlash) > 0.02f || (flash == 0f && _shownFlash != 0f))
            {
                _shownFlash = flash;
                ApplyTint();
            }
        }

        /// <summary>The hull's rock after a heavy hit (pitch, roll in degrees), dying away in 0.3 s.</summary>
        private Vector2 Jolt()
        {
            var t = (Time.time - _joltTime) / 0.3f;
            return t is >= 0f and < 1f ? _jolt * ((1f - t) * (1f - t)) : Vector2.zero;
        }

        /// <summary>Current flight height (0 on the ground).</summary>
        public float Altitude { get; private set; }

        /// <summary>
        /// World position of the muzzle of weapon mount <paramref name="index"/>. Models without that
        /// muzzle fall back to a sensible spot: a coaxial gun beside the main gun, roof weapons on top.
        /// </summary>
        private readonly List<LaunchPoint>[] _launchers;
        private readonly int[] _nextLauncher;

        /// <summary>
        /// Where the next round of weapon mount <paramref name="index"/> leaves from (call once a
        /// shot): the next pod or rail of a launcher pair, a random tube of a multi-tube face, the
        /// barrel firing now of a twin gun, else the mount's muzzle.
        /// </summary>
        public Vector3 MuzzleOf(int index)
        {
            if (index < _launchers.Length && _launchers[index] != null)
            {
                var list = _launchers[index];
                var point = list[_nextLauncher[index]++ % list.Count];
                var spread = point.Spread;
                if (spread == Vector2.zero) return Anchored(point.transform, point.transform.position);
                var jitter = new Vector3(Random.Range(-spread.x, spread.x), Random.Range(-spread.y, spread.y), 0f);
                return Anchored(point.transform, point.transform.position + point.transform.parent.TransformVector(jitter));
            }
            var own = index < _ownBarrel.Length ? _ownBarrel[index] : -1;
            if ((index == 0 || own >= 0) && _barrelTips != null && _muzzles.Length > 0 && _muzzles[0] != null)
            {
                // The barrel firing now (or the mount's own barrel): the main muzzle moved across to that barrel's line.
                var centre = _muzzles[0].position;
                var along = DirectionOf(index);
                var offset = BarrelTip(own >= 0 ? own : _barrel) - centre;
                return Anchored(_muzzles[0], centre + offset - along * Vector3.Dot(offset, along));
            }
            // An aircraft's air-to-air missile marked only on the centreline (a hint for the
            // builder, not a rail): it leaves from the wingtip rails instead.
            if (Def.Flying && index > 0 && Def.Mounts[index].Slot == "aam" && _muzzles[index] != null &&
                Mathf.Abs(_body.InverseTransformPoint(_muzzles[index].position).x) < 0.1f && AirframeStore(index, "aam", out var rail))
                return Anchored(_body, rail);
            if (index < _muzzles.Length && _muzzles[index] != null) return Anchored(_muzzles[index], _muzzles[index].position);
            if (index == 0) return Anchored(_body, MuzzleWorld);
            var slot = Def.Mounts[index].Slot;
            if (Def.Flying && AirframeStore(index, slot, out var store)) return Anchored(_body, store);
            var pivot = _mounts[index] != null ? _mounts[index] : _model.Turret != null ? _model.Turret : _body;
            if (slot == "coax") return Anchored(pivot, _body.TransformPoint(_model.Muzzle) + pivot.right * 0.35f - pivot.forward * 0.6f);
            var top = pivot.position + Vector3.up * (pivot == _body ? MuzzleHeight + 0.6f : 0.8f);
            return Anchored(pivot, top + DirectionOf(index) * 0.8f);
        }

        /// <summary>
        /// Tests and tools: the part the last <see cref="MuzzleOf"/> point rides on and that point in
        /// the part's own space, so where the barrel's tip is drawn can be found again later.
        /// </summary>
        internal Transform LastMuzzleNode { get; private set; }
        internal Vector3 LastMuzzleLocal { get; private set; }

        private Vector3 Anchored(Transform node, Vector3 world)
        {
            LastMuzzleNode = node;
            LastMuzzleLocal = node.InverseTransformPoint(world);
            return world;
        }

        /// <summary>
        /// Where an aircraft's store without a muzzle of its own leaves: an air-to-air missile from
        /// the outermost pylon or rail of the wing, left and right in turn; anything else from
        /// the other stores' muzzle (the bomb bay, the pylons).
        /// </summary>
        private bool AirframeStore(int index, string slot, out Vector3 at)
        {
            at = default;
            if (slot == "aam")
            {
                var outer = Vector3.zero;
                var found = false;
                foreach (var list in _model.Launchers.Values)
                    foreach (var point in list)
                    {
                        var local = _body.InverseTransformPoint(point.transform.position);
                        if (!found || Mathf.Abs(local.x) > Mathf.Abs(outer.x)) outer = local;
                        found = true;
                    }
                foreach (var muzzle in _model.Muzzles.Values)
                {
                    var local = _body.InverseTransformPoint(muzzle.position);
                    if (!found || Mathf.Abs(local.x) > Mathf.Abs(outer.x)) outer = local;
                    found = true;
                }
                if (!found || Mathf.Abs(outer.x) < 0.3f) return false;
                // A little further out than the outermost store: the wingtip rail.
                var side = (_nextLauncher[index]++ & 1) == 0 ? 1f : -1f;
                at = _body.TransformPoint(new Vector3(Mathf.Abs(outer.x) * 1.12f * side, outer.y, outer.z));
                return true;
            }
            foreach (var other in new[] { "missile", "rocket", "main", "gun" })
            {
                if (other == slot || !_model.Muzzles.TryGetValue(other, out var muzzle)) continue;
                at = muzzle.position;
                return true;
            }
            return false;
        }

        /// <summary>World-space direction weapon mount <paramref name="index"/> points in.</summary>
        public Vector3 DirectionOf(int index)
        {
            var heading = index < _currentMount.Length ? _currentMount[index] : _currentTurret;
            return Quaternion.Euler(0f, heading, 0f) * Vector3.forward;
        }

        public void Snapshot()
        {
            _previousPosition = _currentPosition;
            _previousHeading = _currentHeading;
            _previousTurret = _currentTurret;
            _previousSpeed = _currentSpeed;
            _currentPosition = new Vector3(Sim.Position.X, 0f, Sim.Position.Y);
            _currentHeading = Sim.Heading * Mathf.Rad2Deg;
            _currentTurret = Sim.TurretHeading * Mathf.Rad2Deg;
            _currentSpeed = Sim.Speed;
            for (var i = 0; i < _currentMount.Length; i++)
            {
                _previousMount[i] = _currentMount[i];
                _currentMount[i] = Sim.MountHeading(i) * Mathf.Rad2Deg;
            }
        }

        private Vector3 _shownPosition, _shownVelocity;
        private float _shownHeading;
        private bool _shown;

        /// <summary>
        /// Irons out collision jitter on the drawn hull. The position follows the interpolated
        /// one through a filter that predicts along the smoothed velocity (steady driving is not
        /// delayed), so a crowd shoving itself a few centimetres back and forth at the
        /// simulation rate no longer shakes; the heading eases the same way. Large jumps
        /// (spawning, teleports) snap straight through.
        /// </summary>
        private void Steady(ref Vector3 position, ref float hull)
        {
            var dt = Time.deltaTime;
            if (!_shown || (position - _shownPosition).sqrMagnitude > 4f || dt <= 0f)
            {
                _shown = true;
                _shownPosition = position;
                _shownVelocity = Vector3.zero;
                _shownHeading = hull;
                return;
            }
            var velocity = (_currentPosition - _previousPosition) * 20f;
            _shownVelocity = Vector3.Lerp(_shownVelocity, velocity, 1f - Mathf.Exp(-dt * 7f));
            var predicted = _shownPosition + _shownVelocity * dt;
            _shownPosition = Vector3.Lerp(predicted, position, 1f - Mathf.Exp(-dt * 11f));
            _shownHeading = Mathf.LerpAngle(_shownHeading, hull, 1f - Mathf.Exp(-dt * 14f));
            position = _shownPosition;
            hull = _shownHeading;
        }

        private float _elevation = float.NaN;

        /// <summary>
        /// Raises the barrel to where its shots go: howitzers and rocket boxes lift to their
        /// firing angle (mortars highest), guns at aircraft follow the aircraft up, tank guns
        /// tilt a few degrees with range. Idle, artillery rests slightly raised. The angle
        /// moves at a gun-laying speed, not in a snap.
        /// </summary>
        private void Elevate(bool snap = false)
        {
            var pivot = _model.Elevation;
            if (pivot == null) return;
            var weapon = Def.Weapon;
            var indirect = weapon.MinRange > 0f || weapon.Projectile == ProjectileKind.Bomb;
            var aiming = Sim.Aiming && Sim.AimDistance > 0f;
            float want;
            if (Def.Flying)
            {
                // A gunship's chin gun looks down at what it shoots.
                want = aiming ? Mathf.Clamp(-Mathf.Atan2(Altitude, Mathf.Max(1f, Sim.AimDistance)) * Mathf.Rad2Deg, -65f, 5f) : -6f;
            }
            else if (aiming && Sim.AimHeight > 0f)
                want = Mathf.Clamp(Mathf.Atan2(Sim.AimHeight - MuzzleHeight, Mathf.Max(1f, Sim.AimDistance)) * Mathf.Rad2Deg, 8f, 78f);
            else if (aiming && (indirect || _model.Barrel == BarrelKind.Mortar))
            {
                // Farther targets want a higher arc, up to the weapon's own ceiling.
                var reach = Mathf.Clamp01(Sim.AimDistance / Mathf.Max(1f, weapon.Range));
                want = _model.Barrel switch
                {
                    BarrelKind.Mortar => Mathf.Lerp(55f, 72f, reach),
                    BarrelKind.Launcher => Mathf.Lerp(28f, 48f, reach),
                    _ => Mathf.Lerp(24f, 50f, reach),
                };
            }
            else if (aiming) want = Mathf.Lerp(0.5f, 4f, Mathf.Clamp01(Sim.AimDistance / Mathf.Max(1f, weapon.Range)));
            else if (_model.Barrel == BarrelKind.Mortar) want = Mathf.Max(_model.RestPitch, 40f);
            else want = indirect ? 10f : weapon.Targets == TargetLayers.Air ? 18f : 0f;
            if (float.IsNaN(_elevation)) _elevation = _model.RestPitch;
            var rate = weapon.Targets == TargetLayers.Air || Sim.AimHeight > 0f ? 150f : indirect ? 32f : 60f;
            _elevation = snap ? want : Mathf.MoveTowards(_elevation, want, rate * Time.deltaTime);
            pivot.localRotation = Quaternion.Euler(-(_elevation - _model.RestPitch), 0f, 0f);
        }

        /// <summary>
        /// A shot is leaving the turret: the barrel is laid where it must point at once (a gun
        /// still swinging up after an aircraft, a mortar still rising), so the round and the
        /// barrel agree. Returns the barrel's angle above level in degrees, or NaN for a model
        /// whose barrel does not elevate.
        /// </summary>
        public float LayForShot()
        {
            if (_model.Elevation == null) return float.NaN;
            Elevate(snap: true);
            return _elevation;
        }

        /// <summary>World-space direction the elevated barrel of mount <paramref name="index"/> points (level for a mount that does not elevate).</summary>
        public Vector3 BarrelDirectionOf(int index)
        {
            var flat = DirectionOf(index);
            if (index != 0 || _model.Elevation == null || float.IsNaN(_elevation)) return flat;
            var pitch = _elevation * Mathf.Deg2Rad;
            return (flat * Mathf.Cos(pitch) + Vector3.up * Mathf.Sin(pitch)).normalized;
        }

        /// <summary>
        /// World-space direction the barrel of mount <paramref name="index"/> points in as drawn this
        /// frame: the part it turns with (its own free mount, the turret or the hull, with the
        /// hull's pitch and rock) and, for the main gun, the barrel's elevation. Muzzle flashes
        /// face this way; <see cref="DirectionOf"/> is the simulation's latest heading, up to a
        /// step ahead of the drawn turret.
        /// </summary>
        public Vector3 DrawnBarrelOf(int index)
        {
            var aim = index < Def.Mounts.Count ? Def.Mounts[index].Aim : MountAim.Turret;
            var node = aim == MountAim.Free && index < _mounts.Length && _mounts[index] != null ? _mounts[index]
                : aim != MountAim.Hull && _model.Turret != null ? _model.Turret : _body;
            var forward = node.forward;
            if (index == 0 && _model.Elevation != null && !float.IsNaN(_elevation))
                forward = Quaternion.AngleAxis(-_elevation, node.right) * forward;
            return forward;
        }

        /// <summary>Starts the barrel kick; called when the simulation reports a main-gun shot.</summary>
        public void Recoil()
        {
            _recoilTime = Time.time;
            // Barrels fire in turn, unless each belongs to its own weapon mount.
            if (_barrelTips != null && _ownBarrel[0] < 0) _barrel = (_barrel + 1) % _barrelTips.Length;
        }

        /// <summary>Barrels that really stand apart (a twin gun), not one barrel modelled in segments.</summary>
        private bool SideBySide()
        {
            var spread = 0f;
            for (var i = 0; i < _barrelTips.Length; i++)
                for (var j = i + 1; j < _barrelTips.Length; j++)
                {
                    var d = _body.InverseTransformPoint(BarrelTip(i)) - _body.InverseTransformPoint(BarrelTip(j));
                    spread = Mathf.Max(spread, new Vector2(d.x, d.y).magnitude * Def.Scale);
                }
            return spread > 0.25f;
        }

        private Vector3[] _barrelTipOffsets;

        private Vector3 BarrelTip(int i) => _barrelTips[i].TransformPoint(_barrelTipOffsets[i]);

        private readonly int[] _barrelOf;
        private Transform[] _barrelTips;
        private int _barrel;

        /// <summary>Per mount: the barrel of a twin-barrelled main gun it fires from alone, or -1 (see the constructor).</summary>
        private readonly int[] _ownBarrel;

        /// <summary>Eases the attack-hold pose in and out, and the climb away from the hold (see VehicleDef.AttackHold).</summary>
        private void HoldPose()
        {
            var dt = FrameStep;
            _hold = Mathf.MoveTowards(_hold, Sim.InAttackHold ? 1f : 0f, dt * 2.5f);
            var climbed = _climb;
            _climb = Mathf.MoveTowards(_climb, Def.AttackHold > 0f && Sim.Breaking ? BreakClimb : 0f, dt * 4f);
            _climbRate = dt > 0f ? (_climb - climbed) / dt : 0f;
        }

        public void Render(float alpha, Quaternion cameraRotation)
        {
            if (_wreck)
            {
                RenderWreck();
                return;
            }

            var hull = Mathf.LerpAngle(_previousHeading, _currentHeading, alpha);
            var position = Vector3.Lerp(_previousPosition, _currentPosition, alpha);
            var acceleration = (_currentSpeed - _previousSpeed) * 20f;
            var ease = 1f - Mathf.Exp(-FrameStep * 6f);
            if (!Flying) Steady(ref position, ref hull);

            if (Flying)
            {
                // Fly in from behind (never out of the ground), then hover with a slow bob, nose
                // down when speeding up and bank into turns.
                var arrive = ShotStep >= 0f ? 1f : Mathf.SmoothStep(0f, 1f, (Time.time - _spawnTime) / ArriveSeconds);
                var above = 1f - arrive;
                if (Def.FixedWing) HoldPose();
                // A jet hanging on its target bobs a little more than one flying level.
                var bob = Mathf.Sin(FrameTime * 1.3f + Id.Value) * 0.25f + Mathf.Sin(FrameTime * 2.3f + Id.Value * 0.7f) * 0.2f * _hold;
                Altitude = Def.Altitude + above * (Def.FixedWing ? 8f : 10f) + bob * arrive + _climb;
                if (above > 0f)
                {
                    // It flies in along its heading from behind, dropping to its height as it comes.
                    var heading = hull * Mathf.Deg2Rad;
                    position -= new Vector3(Mathf.Sin(heading), 0f, Mathf.Cos(heading)) * (above * above * (Def.FixedWing ? 80f : 35f));
                }
                var turn = Mathf.DeltaAngle(_previousHeading, _currentHeading) * 20f;
                if (Def.FixedWing)
                {
                    // Aeroplanes fly level and bank hard into their turns. In an attack hold the nose
                    // dips at the target and a jet slowed right down (a hovering VTOL jet) turns without
                    // banking, rocking a little; breaking away it pitches up into the climb, and comes
                    // back down nose first.
                    var flown = Mathf.Clamp01(_currentSpeed / (Def.Speed * 0.6f));
                    var dip = _hold * Mathf.Clamp(Mathf.Atan2(Def.Altitude - Sim.AimHeight, Mathf.Max(4f, Sim.AimDistance)) * Mathf.Rad2Deg * 0.35f, 0f, 12f);
                    var level = Mathf.Clamp(acceleration * 0.5f, -4f, 4f) * (1f - _hold);
                    _pitch = Mathf.Lerp(_pitch, level + dip - Mathf.Clamp(_climbRate * 2.5f, -12f, 12f), ease);
                    var rock = Mathf.Sin(FrameTime * 1.7f + Id.Value) * 2f * _hold;
                    _bank = Mathf.Lerp(_bank, Mathf.Clamp(-turn * 0.45f, -50f, 50f) * flown + rock, ease);
                }
                else
                {
                    _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(_currentSpeed * 0.9f + acceleration * 1.5f, -8f, 16f), ease);
                    _bank = Mathf.Lerp(_bank, Mathf.Clamp(-turn * 0.12f, -20f, 20f), ease);
                }
                position.y = Altitude;
                _body.localPosition = Vector3.zero;
                _body.localRotation = Quaternion.Euler(_pitch, 0f, _bank);
                AnimateNavLights();
            }
            else
            {
                // Hull pitch follows acceleration (nose dips when braking) and eases back.
                _pitch = Mathf.Lerp(_pitch, Mathf.Clamp(-acceleration * 0.9f, -4f, 4f), ease);
                _bouncePhase += Time.deltaTime * (4f + _currentSpeed * 1.4f);
                var bounce = Mathf.Sin(_bouncePhase) * 0.012f * Mathf.Clamp01(_currentSpeed / 4f);
                _body.localPosition = new Vector3(0f, bounce, 0f);
                var jolt = Jolt();
                _body.localRotation = Quaternion.Euler(_pitch + jolt.x, 0f, jolt.y);
            }
            Root.position = position;
            Root.rotation = Quaternion.Euler(0f, hull, 0f);

            if (_model.Turret != null && !Match.DebugFlags.Has("-mb-no-turret"))
            {
                var turret = Mathf.LerpAngle(_previousTurret, _currentTurret, alpha);
                _model.Turret.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(hull, turret), 0f);
                var t = (Time.time - _recoilTime) / RecoilSeconds;
                var kick = t is >= 0f and < 1f ? (1f - t) * (1f - t) * _recoilDistance : 0f;
                for (var i = 0; i < _recoilRest.Length; i++)
                    _model.RecoilParts[i].localPosition = _recoilRest[i] + Vector3.back * (_barrelTips == null || _barrelOf[i] == _barrel ? kick : 0f);
            }

            // Free weapon mounts turn on their own; their parent may be the turret or the hull (the
            // main one too when it is a free roof gun, as on the command vehicle).
            for (var i = 0; i < _mounts.Length; i++)
            {
                var mount = _mounts[i];
                if (mount == null || Def.Mounts[i].Aim != MountAim.Free) continue;
                var heading = Mathf.LerpAngle(_previousMount[i], _currentMount[i], alpha);
                var parentYaw = mount.parent != null ? mount.parent.eulerAngles.y : 0f;
                mount.localRotation = Quaternion.Euler(0f, Mathf.DeltaAngle(parentYaw, heading), 0f);
            }

            Elevate();
            Spin(1f);
            AnimateParts(cameraRotation);

            _ring.Visible = Selected;
            if (_shadowRing != null)
            {
                // Keep the air ring on the ground under the aircraft, level whatever it is doing.
                _shadowRing.Transform.position = new Vector3(Root.position.x, 0.08f, Root.position.z);
                _shadowRing.Transform.rotation = Quaternion.identity;
            }
            var health = Mathf.Clamp01(Sim.Hp / Sim.MaxHp);
            NoteHealth(health);
            RenderHitFeedback();
            if (Time.time >= _trailHoldUntil && _trail > health) _trail = Mathf.MoveTowards(_trail, health, Time.deltaTime * 2f);
            var repairing = Time.time < _repairUntil;
            // The stores icon is drawn under the bar's transform, so it is worked out before the bar is hidden.
            var stores = _storesMark != null && StoresWanted();
            var showBar = Selected || health < 0.999f || stores || repairing;
            if (_bar.gameObject.activeSelf != showBar) _bar.gameObject.SetActive(showBar);
            if (!showBar) return;
            _bar.rotation = cameraRotation;
            if (_repairMark.gameObject.activeSelf != repairing) _repairMark.gameObject.SetActive(repairing);
            if (repairing) _repairMark.localScale = Vector3.one * (1f + 0.08f * Mathf.Sin(Time.time * 6f));
            RenderStoresMark();
            _barFill.localScale = new Vector3(BarWidth * health, BarHeight, 1f);
            _barFill.localPosition = new Vector3(-BarWidth * (1f - health) * 0.5f, 0f, -0.02f);
            _barTrail.localScale = new Vector3(BarWidth * _trail, BarHeight, 1f);
            _barTrail.localPosition = new Vector3(-BarWidth * (1f - _trail) * 0.5f, 0f, -0.01f);
        }

        private Transform _repairMark;
        private float _repairUntil = -1f;

        /// <summary>Something is repairing this vehicle or defence: the wrench shows over its health bar for a moment.</summary>
        public void ShowRepair() => _repairUntil = Time.time + 1.4f;

        /// <summary>
        /// A green wrench on a dark disc above the health bar: a diagonal handle and a head with an
        /// open jaw, built from quads so it needs no texture.
        /// </summary>
        private void BuildRepairMark(MeshLibrary meshes, MaterialLibrary materials)
        {
            _repairMark = new GameObject("RepairMark").transform;
            _repairMark.SetParent(_bar, false);
            _repairMark.localPosition = new Vector3(0f, 0.72f, 0f);
            var back = CreateMesh("Back", _repairMark, meshes.Quad, materials.BarBack, false);
            back.localScale = new Vector3(0.82f, 0.82f, 1f);
            back.localRotation = Quaternion.Euler(0f, 0f, 45f);
            var handle = CreateMesh("Handle", _repairMark, meshes.Quad, materials.RepairMark, false);
            handle.localScale = new Vector3(0.14f, 0.62f, 1f);
            handle.localRotation = Quaternion.Euler(0f, 0f, -45f);
            handle.localPosition = new Vector3(-0.05f, -0.05f, -0.01f);
            var head = CreateMesh("Head", _repairMark, meshes.Quad, materials.RepairMark, false);
            head.localScale = new Vector3(0.3f, 0.3f, 1f);
            head.localRotation = Quaternion.Euler(0f, 0f, -45f);
            head.localPosition = new Vector3(0.17f, 0.17f, -0.01f);
            var jaw = CreateMesh("Jaw", _repairMark, meshes.Quad, materials.BarBack, false);
            jaw.localScale = new Vector3(0.1f, 0.18f, 1f);
            jaw.localRotation = Quaternion.Euler(0f, 0f, -45f);
            jaw.localPosition = new Vector3(0.23f, 0.23f, -0.02f);
            _repairMark.gameObject.SetActive(false);
        }
        private Transform _lift;
        private Vector3 _liftRest;
        private float _liftDown;

        /// <summary>How far a gun pit's lift sinks (the model is built raised: its gun clears the berm by this).</summary>
        private const float PitDepth = 1.6f;

        private const float LiftSeconds = 0.9f;

        private void AnimateParts(Quaternion cameraRotation)
        {
            // The missile rises on its erector as the launch countdown runs.
            if (_erector != null) _erector.localRotation = _erectorRest * Quaternion.Euler(-90f * Sim.Charge, 0f, 0f);
            AnimatePrompt8Parts();
            // Searchlights sweep back and forth, each tower on its own rhythm.
            if (_searchlight != null)
                _searchlight.localRotation = _searchlightRest * Quaternion.Euler(0f, Mathf.Sin(Time.time * 0.45f + Id.Value) * 75f, 0f);
            // A gun pit sinks into its hole while it hides and comes up in a second when an enemy is close.
            if (_lift != null)
            {
                _liftDown = Mathf.MoveTowards(_liftDown, Sim.Lowered ? 1f : 0f, Time.deltaTime / LiftSeconds);
                _lift.localPosition = _liftRest + Vector3.down * (PitDepth * Mathf.SmoothStep(0f, 1f, _liftDown));
            }

            AnimateShield(cameraRotation);
        }

        /// <summary>Freezes the view as a burnt-out hulk; the simulation entity is gone.</summary>
        public void BecomeWreck()
        {
            if (!Match.DebugFlags.Has("-mb-no-tint"))
            {
                var block = new MaterialPropertyBlock();
                block.SetColor(TintId, new Color(0.16f, 0.14f, 0.13f));
                foreach (var r in _model.Renderers) r.SetPropertyBlock(block);
                foreach (var r in _model.Lod1Renderers) r.SetPropertyBlock(block);
            }
            // A hulk is drawn with meshes: its turret can be thrown off and it sinks away.
            if (_level == VehicleLod.Impostor) SetLevel(VehicleLod.Simple);
            _ring.Visible = false;
            if (_shadowRing != null) _shadowRing.Visible = false;
            _bar.gameObject.SetActive(false);
            Selected = false;
            HideShield();
            _wreck = true;
            if (Flying)
            {
                // Keep some of the momentum it had when it was hit.
                _crashStart = Time.time;
                _crashHeight = Root.position.y;
                _crashDrift = (_currentPosition - _previousPosition) * 20f * 0.8f;
                _crashDrift.y = 0f;
                return;
            }
            if (Def.Static)
            {
                // A fixed defence does not drive off as a hulk: it slumps into a leaning, burnt ruin
                // and stays where it stood.
                _collapseStart = Time.time;
                _collapseTilt = new Vector2(Random.Range(-15f, 15f), Random.Range(-15f, 15f));
                _collapseSink = Top * 0.3f;
                return;
            }
            _body.localRotation = Quaternion.Euler(Random.Range(-3f, 3f), 0f, Random.Range(-4f, 4f));
        }

        /// <summary>True while a shot-down aircraft is still falling.</summary>
        public bool Falling => _crashStart >= 0f && Root.position.y > 0.05f;

        /// <summary>Animates a wreck that is still settling (a shot-down aircraft falling) and keeps its detail level up with the zoom.</summary>
        public void AnimateWreck()
        {
            UpdateLod(VehicleLod.PixelsPerMetre);
            RenderWreck();
        }

        private void RenderWreck()
        {
            if (_collapseStart >= 0f)
            {
                // Slumps over a second and a half: down on one side, leaning, then still.
                var c = Mathf.Clamp01((Time.time - _collapseStart) / 1.5f);
                var e = c * c * (3f - 2f * c);
                _body.localPosition = Vector3.down * (_collapseSink * e);
                _body.localRotation = Quaternion.Euler(_collapseTilt.x * e, 0f, _collapseTilt.y * e);
                return;
            }
            if (!Flying || _crashStart < 0f || Root.position.y <= 0f) return;
            // Out of control: it drifts on with its momentum, spins faster and faster as the tail
            // goes, tips over and drops, the rotor winding down, until it hits the ground.
            var t = Time.time - _crashStart;
            if (Def.FixedWing)
            {
                // An aeroplane dives in nose first, rolling, trailing fire.
                var dive = Mathf.Max(0f, _crashHeight - 0.5f * 11f * t * t);
                var glide = _crashDrift * Mathf.Clamp01(1f - t * 0.35f) * Time.deltaTime;
                var q = Root.position + glide;
                Root.position = new Vector3(q.x, dive, q.z);
                _body.localRotation = Quaternion.Euler(Mathf.Min(40f, t * 30f), 0f, t * 140f);
                Spin(1f);
                return;
            }
            var height = Mathf.Max(0f, _crashHeight - 0.5f * 7f * t * t);
            var drift = _crashDrift * Mathf.Clamp01(1f - t * 0.5f) * Time.deltaTime;
            var p = Root.position + drift;
            Root.position = new Vector3(p.x, height, p.z);
            Root.rotation *= Quaternion.Euler(0f, Mathf.Lerp(150f, 560f, Mathf.Clamp01(t / 1.4f)) * Time.deltaTime, 0f);
            _body.localRotation = Quaternion.Euler(Mathf.Min(28f, t * 24f), 0f, Mathf.Min(40f, t * 34f));
            Spin(Mathf.Clamp01(1f - t * 0.6f));
        }

        /// <summary>
        /// Most a fast spinner (rotor, propeller) turns in one frame. Turned further, a rotor of four
        /// or five blades seems to crawl backwards or strobe (the wagon-wheel effect); below it the
        /// blades read as sweeping round, and the blur disc sells the speed.
        /// </summary>
        private const float MaxSpinPerFrame = 23f;

        private float[] _spinAngles;

        private void Spin(float speed)
        {
            var spinners = _model.Spinners;
            if (spinners.Count == 0) return;
            _spinAngles ??= new float[spinners.Count];
            var dt = Time.deltaTime * speed;
            for (var i = 0; i < spinners.Count; i++)
            {
                var step = spinners[i].DegreesPerSecond * dt;
                if (spinners[i].DegreesPerSecond > 600f) step = Mathf.Min(step, MaxSpinPerFrame);
                _spinAngles[i] = (_spinAngles[i] + step) % 360f;
                spinners[i].Transform.localRotation = spinners[i].Rest * Quaternion.AngleAxis(_spinAngles[i], spinners[i].Axis);
            }
        }

        private static Mesh _blurDisc;

        /// <summary>
        /// A faint disc under each main rotor, the blur of blades turning faster than the eye can
        /// follow; it stays still while the blades sweep through it.
        /// </summary>
        private void AddRotorBlur(MaterialLibrary materials)
        {
            foreach (var spinner in _model.Spinners)
            {
                if (spinner.Axis != Vector3.up || spinner.DegreesPerSecond < 600f || spinner.Transform.parent == null) continue;
                var renderers = spinner.Transform.GetComponentsInChildren<Renderer>();
                if (renderers.Length == 0) continue;
                var bounds = renderers[0].bounds;
                foreach (var r in renderers) bounds.Encapsulate(r.bounds);
                var radius = Mathf.Max(bounds.extents.x, bounds.extents.z) / Mathf.Max(0.01f, Root.lossyScale.x);
                if (radius < 0.5f) continue;
                _blurDisc ??= BlurDisc();
                var disc = CreateMesh("Rotor Blur", spinner.Transform.parent, _blurDisc, materials.SoftSmoke, false);
                disc.localPosition = spinner.Transform.localPosition + Vector3.up * 0.05f;
                disc.localRotation = Quaternion.identity;
                var parentScale = spinner.Transform.parent.lossyScale.x / Mathf.Max(0.01f, Root.lossyScale.x);
                disc.localScale = Vector3.one * (radius * 2.1f / Mathf.Max(0.01f, parentScale));
            }
        }

        /// <summary>A flat quad (XZ plane) tinted a faint smoky grey, for the soft-disc particle shader.</summary>
        private static Mesh BlurDisc()
        {
            var colour = Primitives.Linear(new Color(0.16f, 0.16f, 0.17f, 0.3f));
            var mesh = new Mesh { name = "RotorBlur" };
            mesh.SetVertices(new[] { new Vector3(-0.5f, 0f, -0.5f), new Vector3(0.5f, 0f, -0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(-0.5f, 0f, 0.5f) });
            mesh.SetUVs(0, new[] { new Vector2(0f, 0f), new Vector2(1f, 0f), new Vector2(1f, 1f), new Vector2(0f, 1f) });
            mesh.SetColors(new[] { colour, colour, colour, colour });
            mesh.SetTriangles(new[] { 0, 2, 1, 0, 3, 2 }, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        internal static Transform CreateMesh(string name, Transform parent, Mesh mesh, Material material, bool castShadows)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            renderer.receiveShadows = castShadows;
            return go.transform;
        }
    }
}

using System.Collections.Generic;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Burnt-out hulks: they burn, cook off now and then, smoulder, and after a while sink into
    /// the ground and disappear (sooner when there are more than the budget allows). A vehicle's
    /// death explosion tears pieces off it, bucks the hull and can blow the turret high into the
    /// air trailing fire; big vehicles then cook off in a quick chain of blasts, and some shoot a
    /// fountain of flame out of the turret ring. Shot-down aircraft fall burning and blow up
    /// when they hit the ground. Everything moves on simple kinematics; no physics engine.
    /// <para>Prompt 34 L7 (DECISIONS "Prompt 34 L5/L6/L7"): the breakup by class (<see cref="WreckClasses"/>): a tank's
    /// turret thrown and its hulk burning; a wheeled vehicle's wheels thrown off (Part_wheel, Part_wheelb) and its frame
    /// rolling over; a lorry's cargo going up in a chain along its bed; a gun's ammunition cooking off with a fountain of
    /// flame; a fighter losing a wing (Part_wing) and spiralling down, a helicopter losing its tail rotor and spinning
    /// down as its main rotor flies off, a big aircraft burning at an engine and falling long and slanting with a wing
    /// gone, each on a show path onto the Sim's crash point and time (VehicleView.PlanCrash); a drone a small blast and
    /// gone. Ships list, break and sink (ShipSinking). All view only: no wreck blocks movement or sight in the Sim.
    /// Wrecks live 30-45 s (bosses 90 s; Low graphics a third less); at most ~12 full wrecks near the camera (Medium 9,
    /// Low 6), any more near it and those far from it go sooner, leaving a burn mark.</para>
    /// </summary>
    internal sealed class WreckManager
    {
        // Explode, burn, go: a hulk burns for a good part of its life and is gone after it, so
        // the field shows the current fight rather than a scrapyard of old ones.
        private const float BurnShare = 0.4f;
        private const float SinkSeconds = 3f;
        private const float SinkDepth = 2.2f;
        private const float Gravity = 18f;

        /// <summary>How long a destroyed defence burns before it only smoulders.</summary>
        private const float StaticBurnSeconds = 45f;

        private sealed class Wreck
        {
            public EntityId Id;
            public VehicleView View;
            public WreckClass Class;
            public float Created, Expires, Burn;
            public float SinkStart = -1f;
            public float NextPop;
            public int PopsLeft;
            public int ChainLeft;
            public float NextChain;
            public bool ChainAlong, SlowChain;
            public bool WasFalling;
            public bool Blown;
            public bool Gone;
            public Transform Turret;
            public Vector3 TurretVelocity, TurretSpin;
            public bool TurretFlying;
            public float TurretFlame, TurretSmoke;
            public float JetFrom, JetUntil, JetDebt;
            public float HopVelocity, HopHeight;
            public float FlipStart = -1f, FlipAngle, FlipSide, FlipLift;
            public Quaternion FlipBase;
            public int Fire;
        }

        private readonly List<Wreck> _wrecks = new();
        private readonly List<(Vector3 position, float size)> _crashes = new();
        private readonly List<(Vector3 position, float size)> _marks = new();
        private readonly FireSpots _fires;
        private readonly ChunkThrower _chunks;
        private readonly WreckBreakup _breakup;
        private readonly int _capacity;
        private float _nextTrim;

        /// <summary>The view's focus (EffectsDirector sets it each frame): the full wrecks are counted near it.</summary>
        public Vector3 Focus { get; set; }

        /// <summary>Pieces torn off wrecks still about (tests and the budget log).</summary>
        public int Pieces => _breakup.Count;

        /// <summary>Prompt 34 L9: the wrecks on the field now (the stress scene's count).</summary>
        public int Count => _wrecks.Count;

        public WreckManager(FireSpots fires, ChunkThrower chunks, int capacity, Transform parent = null)
        {
            _fires = fires;
            _chunks = chunks;
            _capacity = capacity;
            _breakup = new WreckBreakup(parent, chunks, fires);
        }

        public void Add(VehicleView view, float now) => Add(view, now, null, 0f);

        /// <summary>
        /// A destroyed vehicle's view becomes a wreck. For a shot-down aircraft, <paramref name="crashAt"/> and
        /// <paramref name="fall"/> are the Sim's crash plan (the loss event's Target and Value): its wreck flies a show path
        /// that lands there and then.
        /// </summary>
        public void Add(VehicleView view, float now, Vector3? crashAt, float fall)
        {
            view.BecomeWreck();
            var cls = WreckClasses.Of(view.Def);
            // A vehicle the defs call tracked but whose model has wheels to lose breaks up as a wheeled one.
            if (cls == WreckClass.Tank && !view.Def.Boss && view.FindPart("Part_wheel") != null) cls = WreckClass.Wheeled;
            var life = WreckClasses.Life(view.Def, Random.value, MatchSettings.Tier);
            var wreck = new Wreck
            {
                Id = view.Id, View = view, Class = cls, Created = now, Expires = now + life, Burn = life * BurnShare,
                NextPop = now + Random.Range(3f, 5f), PopsLeft = Random.Range(1, 3), WasFalling = view.Falling,
            };
            _wrecks.Add(wreck);
            if (cls == WreckClass.Drone)
            {
                // A drone: its small blast, and nothing left of it.
                wreck.Gone = true;
                if (view.Root != null) view.Root.gameObject.SetActive(false);
                return;
            }
            if (view.Def.Static)
            {
                // A tower, bunker or gun: its ruin stays for the rest of the battle. It burns hard
                // from the top and at its foot, its ammunition goes up in a chain, then pops now and
                // then while it burns, and it smoulders on after.
                wreck.Expires = float.MaxValue;
                wreck.ChainLeft = Random.Range(4, 7);
                wreck.NextChain = now + Random.Range(0.3f, 0.5f);
                wreck.PopsLeft = Random.Range(4, 7);
                wreck.NextPop = now + Random.Range(4f, 6f);
                var blaze = Mathf.Clamp(view.Sim.Radius / 1.4f, 1f, 2f);
                // DECISIONS 20Y: a boss's ruin burns as hard but shorter, under its thinner death smoke.
                var boss = view.Def.Boss;
                var burn = boss ? StaticBurnSeconds * 0.45f : StaticBurnSeconds;
                var smoke = boss ? FireSpots.BossSmoke : 1f;
                wreck.Fire = _fires.Ignite(view.Root.position + Vector3.up * view.Top * 0.7f, blaze, burn, now, smoke: smoke);
                _fires.Ignite(view.Root.position + Vector3.up * 0.5f + Random.insideUnitSphere * 0.8f, blaze * 0.7f, burn * 1.6f, now, smoke: smoke);
                return;
            }
            // A shot-down aircraft burns all the way down; a ground hulk burns where it stopped.
            var size = Mathf.Clamp(view.Sim.Radius / 1.6f, 0.75f, 1.6f);
            wreck.Fire = _fires.Ignite(view.Root.position + Vector3.up * 0.9f, size, wreck.Burn * Random.Range(0.85f, 1.15f), now,
                view.Flying ? view.Root : null, smoke: view.Def.Boss ? FireSpots.BossSmoke : 1f);
            if (view.Flying && WreckClasses.Falls(cls)) BreakInTheAir(wreck, now, crashAt, fall);

            // Ruins of fixed defences stay; only vehicle hulks make room for new ones.
            var living = 0;
            foreach (var w in _wrecks)
                if (w.SinkStart < 0f && !w.View.Def.Static) living++;
            if (living <= _capacity) return;
            foreach (var w in _wrecks)
            {
                if (w.SinkStart >= 0f || w.View.Def.Static) continue;
                Sink(w, now);
                break;
            }
        }

        /// <summary>
        /// Prompt 34 L7: a shot-down aircraft breaks up as it starts to fall: a fighter's left wing (Part_wing) goes and it
        /// spirals down; a helicopter's tail rotor goes, its main rotor flies off and it spins down; a big aircraft's wing goes
        /// with an engine burning and it falls long and slanting. The fall is a show path onto the Sim's crash plan.
        /// </summary>
        private void BreakInTheAir(Wreck w, float now, Vector3? crashAt, float fall)
        {
            var view = w.View;
            var root = view.Root;
            var drift = view.Def.FixedWing ? root.forward * Mathf.Max(6f, view.Def.Speed * 0.6f) : Vector3.zero;
            var style = VehicleView.FallStyle.Spin;
            var side = Random.value < 0.5f ? -1f : 1f;
            // Play-test 12: each class breaks up one of two or three ways, by the vehicle's id (WreckClasses.Variant).
            var variant = WreckClasses.Variant(w.Id, w.Class);
            var radius = view.Sim.Radius;
            switch (w.Class)
            {
                case WreckClass.Fighter:
                case WreckClass.BigAircraft:
                {
                    var big = w.Class == WreckClass.BigAircraft;
                    if (variant == 1)
                    {
                        // Its engines on fire, whole: a long burning dive (a fighter nose down, a big one banking over).
                        style = VehicleView.FallStyle.Slant;
                        _fires.Ignite(root.position - root.forward * radius * 0.45f, big ? 1.5f : 1f, Mathf.Max(6f, fall + 4f), now, root);
                        if (big) _fires.Ignite(root.position + root.right * radius * 0.35f, 1.2f, Mathf.Max(6f, fall + 4f), now, root);
                        break;
                    }
                    // The separated wing is the left one: it rolls and banks to that side.
                    side = -1f;
                    // Variant 0: the wing goes, a spiral (a long slant for a big one); 2: it breaks up in the air, the wing and a
                    // shower of burning pieces, and the rest goes down in a flat spin.
                    style = variant == 2 ? VehicleView.FallStyle.Spin : big ? VehicleView.FallStyle.Slant : VehicleView.FallStyle.Spiral;
                    var wing = view.FindPart("Part_wing");
                    if (wing != null)
                        _breakup.Throw(wing, root, drift * 0.7f - root.right * (big ? 2.5f : 4f) + Vector3.up * (big ? 1.5f : 3f),
                            Random.insideUnitSphere * (big ? 120f : 320f), true, 0.3f, 25f, now);
                    if (variant == 2) _chunks?.Wreck(root.position, radius * 0.8f, view.Team, false, now);
                    // A smoke trail off the torn wing root; a big aircraft's engine burning hard on that side.
                    var at = root.position - root.right * radius * (big ? 0.35f : 0.2f);
                    _fires.Ignite(at, big ? 1.4f : 0.8f, Mathf.Max(6f, fall + 4f), now, root);
                    break;
                }
                case WreckClass.Helicopter:
                {
                    var tail = view.FindPart("Tail_rotor");
                    var rotor = view.FindPart("Rotor") ?? view.FindPart("Rotor_front");
                    switch (variant)
                    {
                        case 0:
                            // The tail boom snaps: the tail rotor goes tumbling, the main rotor still turns and it spins down faster and faster.
                            style = VehicleView.FallStyle.Spin;
                            if (tail != null)
                                _breakup.Throw(tail, root, -root.forward * 5f + Vector3.up * 1f + Random.insideUnitSphere, new Vector3(720f, 0f, 90f), true,
                                    0.2f, 20f, now);
                            _fires.Ignite(root.position - root.forward * radius * 0.6f, 0.7f, Mathf.Max(6f, fall + 4f), now, root);
                            break;
                        case 1:
                            // Hit in the engine: nothing comes off; it burns hard under the rotor and goes down in a long burning slant.
                            style = VehicleView.FallStyle.Slant;
                            _fires.Ignite(root.position + Vector3.up * 0.6f, Mathf.Clamp(radius / 1.4f, 1f, 1.8f), Mathf.Max(6f, fall + 4f), now, root);
                            break;
                        default:
                            // Torn apart: the main rotor flies off, the tail with it, a burst of burning pieces; the cabin drops tumbling.
                            style = VehicleView.FallStyle.Spiral;
                            if (tail != null)
                                _breakup.Throw(tail, root, -root.forward * 5f + Vector3.up * 2f + Random.insideUnitSphere, new Vector3(720f, 0f, 90f), false,
                                    0.2f, 20f, now);
                            if (rotor != null)
                                _breakup.Throw(rotor, root, Vector3.up * 7f + Random.insideUnitSphere * 3f, new Vector3(30f, 900f, 20f), false, 0.15f, 20f,
                                    now);
                            _chunks?.Wreck(root.position, radius * 0.7f, view.Team, false, now);
                            break;
                    }
                    break;
                }
            }
            if (crashAt.HasValue && fall > 0f) view.PlanCrash(crashAt.Value, fall, style, side);
        }

        /// <summary>A falling or fallen aircraft wreck: where it is now (its death blast goes off there).</summary>
        public bool TryGetAircraftWreck(EntityId id, out Vector3 position)
        {
            foreach (var w in _wrecks)
            {
                if (w.Id != id || !w.View.Flying || w.Gone) continue;
                position = w.View.Root.position;
                return true;
            }
            position = default;
            return false;
        }

        private void Sink(Wreck w, float now)
        {
            w.SinkStart = now;
            w.JetUntil = 0f;
            // No flames over empty ground once the hulk has gone; a burn mark stays where it lay.
            _fires.Extinguish(w.Fire, now);
            if (!w.Gone && w.View.Root != null && !w.View.Def.Static)
                _marks.Add((w.View.Root.position, Mathf.Max(2.5f, w.View.Sim.Radius * 2.2f)));
        }

        /// <summary>
        /// The death explosion of a freshly destroyed ground vehicle, by its class: pieces of it fly off (some burning, some
        /// in its colours), the hull bucks; a tank's turret is thrown into the air, a wheeled vehicle loses its wheels and rolls
        /// over, a lorry's cargo goes up in a chain, a gun's ammunition cooks off. Once per wreck; aircraft are left to fall.
        /// </summary>
        public void Blow(EntityId id, float now)
        {
            Wreck wreck = null;
            foreach (var w in _wrecks)
                if (w.Id == id) wreck = w;
            if (wreck == null || wreck.Blown || wreck.Gone || wreck.View.Flying) return;
            wreck.Blown = true;
            var view = wreck.View;
            var radius = view.Sim.Radius;
            _chunks?.Wreck(view.Root.position, radius, view.Team, true, now);
            // A hull bucks in the blast; a concrete defence does not.
            wreck.HopVelocity = view.Def.Static ? 0f : Random.Range(3f, 4.5f);

            // Ammunition going up: a quick chain of small pops around the hull after the big blast.
            if (radius >= 1.1f)
            {
                wreck.ChainLeft = radius >= 1.8f ? Random.Range(3, 5) : Random.Range(2, 4);
                wreck.NextChain = now + Random.Range(0.35f, 0.6f);
            }
            if (radius >= 1.8f)
            {
                // ...and in some hulls a roaring jet of flame out of the turret ring.
                if (view.Turret != null && Random.value < 0.55f)
                {
                    wreck.JetFrom = now + Random.Range(0.25f, 0.8f);
                    wreck.JetUntil = wreck.JetFrom + Random.Range(1.4f, 2.6f);
                }
            }
            // Play-test 12: each class breaks up one of two or three ways, by the vehicle's id (WreckClasses.Variant).
            var variant = WreckClasses.Variant(wreck.Id, wreck.Class);
            switch (wreck.Class)
            {
                case WreckClass.Wheeled:
                    // 0: the wheels thrown and the frame over on its side or roof; 1: thrown onto its roof whole, burning;
                    // 2: the wheels blown off, the burning frame bucking high and dropping where it stood.
                    if (variant != 1) ThrowWheels(wreck, now);
                    if (variant == 2)
                    {
                        wreck.HopVelocity = Random.Range(4.5f, 6f);
                        break;
                    }
                    wreck.FlipStart = now + 0.05f;
                    wreck.FlipAngle = variant == 1 ? Random.Range(165f, 180f)
                        : Random.value < 0.55f ? Random.Range(85f, 100f) : Random.Range(160f, 180f);
                    wreck.FlipSide = Random.value < 0.5f ? -1f : 1f;
                    wreck.FlipBase = view.Root.rotation;
                    if (variant == 1) wreck.HopVelocity = Random.Range(5f, 6.5f);
                    break;
                case WreckClass.Truck when variant == 1:
                    // The cab goes up: one hard blast that throws it onto its side, a short chain after.
                    wreck.ChainLeft = Random.Range(2, 4);
                    wreck.NextChain = now + Random.Range(0.4f, 0.7f);
                    wreck.HopVelocity = Random.Range(4.5f, 6f);
                    wreck.FlipStart = now + 0.08f;
                    wreck.FlipAngle = Random.Range(80f, 95f);
                    wreck.FlipSide = Random.value < 0.5f ? -1f : 1f;
                    wreck.FlipBase = view.Root.rotation;
                    _fires.Ignite(view.Root.position + view.Root.forward * radius * 0.5f + Vector3.up * 1f, 0.9f, wreck.Burn * 0.8f, now);
                    break;
                case WreckClass.Truck:
                    // The cargo goes up in a chain along the bed, and the bed burns.
                    wreck.ChainLeft = Random.Range(4, 7);
                    wreck.NextChain = now + Random.Range(0.25f, 0.45f);
                    wreck.ChainAlong = true;
                    _fires.Ignite(view.Root.position - view.Root.forward * radius * 0.5f + Vector3.up * 1f, 0.9f, wreck.Burn * 0.8f, now);
                    break;
                case WreckClass.Artillery:
                    // The ammunition inside cooks off: a long chain, a fountain of flame, pops while it burns; now and then the turret goes.
                    wreck.ChainLeft = Random.Range(6, 10);
                    wreck.NextChain = now + Random.Range(0.3f, 0.6f);
                    wreck.SlowChain = true;
                    wreck.PopsLeft += 3;
                    wreck.JetFrom = now + Random.Range(0.3f, 0.6f);
                    wreck.JetUntil = wreck.JetFrom + Random.Range(2f, 3.5f);
                    // Play-test 12, variant 1: it all goes at once, the turret or launcher thrown high and the hull bucking hard.
                    if (variant == 1)
                    {
                        wreck.ChainLeft = Random.Range(3, 5);
                        wreck.SlowChain = false;
                        wreck.HopVelocity = Random.Range(5f, 6.5f);
                        TossTurret(wreck);
                    }
                    else if (Random.value < 0.5f) TossTurret(wreck);
                    break;
                default:
                    // Play-test 12: 0 the turret thrown high (the old way); 1 the turret stays and the hull burns out with a long
                    // jet of flame from the turret ring (a catastrophic cook-off); 2 the turret knocked off sideways onto the ground.
                    if (variant == 1 && view.Turret != null)
                    {
                        wreck.JetFrom = now + Random.Range(0.2f, 0.5f);
                        wreck.JetUntil = wreck.JetFrom + Random.Range(3f, 4.5f);
                        wreck.ChainLeft += 2;
                        break;
                    }
                    TossTurret(wreck);
                    if (variant == 2 && wreck.TurretFlying && view.Root != null)
                    {
                        var aside = (Random.value < 0.5f ? -1f : 1f) * view.Root.right;
                        wreck.TurretVelocity = aside * Random.Range(3.5f, 5.5f) + Vector3.up * Random.Range(4.5f, 6.5f);
                        wreck.TurretSpin = new Vector3(Random.Range(-90f, 90f), Random.Range(-200f, 200f), Random.Range(-160f, 160f));
                    }
                    break;
            }
        }

        /// <summary>A wheeled vehicle's separable wheels (Part_wheel, Part_wheelb) thrown out sideways, spinning, some burning.</summary>
        private void ThrowWheels(Wreck w, float now)
        {
            var root = w.View.Root;
            foreach (var name in new[] { "Part_wheel", "Part_wheelb" })
            {
                var wheel = w.View.FindPart(name);
                if (wheel == null) continue;
                var outward = root.InverseTransformPoint(wheel.position).x < 0f ? -root.right : root.right;
                _breakup.Throw(wheel, root, outward * Random.Range(4f, 7f) + Vector3.up * Random.Range(5f, 8f) + Random.insideUnitSphere,
                    new Vector3(Random.Range(-200f, 200f), 0f, Random.Range(400f, 700f)), Random.value < 0.5f, 0.4f, w.Expires - now, now);
            }
        }

        /// <summary>Throws the turret of a freshly destroyed vehicle high into the air.</summary>
        private static void TossTurret(Wreck wreck)
        {
            if (wreck.Turret != null || wreck.View.Turret == null || wreck.View.Flying) return;
            wreck.Turret = wreck.View.Turret;
            wreck.Turret.SetParent(wreck.View.Root, true);
            wreck.TurretVelocity = new Vector3(Random.Range(-3.5f, 3.5f), Random.Range(11f, 16f), Random.Range(-3.5f, 3.5f));
            wreck.TurretSpin = Random.insideUnitSphere * 420f;
            wreck.TurretFlying = true;
        }

        /// <summary>
        /// Ammunition cooking off inside a burning hulk: returns one wreck position that is due a
        /// secondary explosion, and whether it is a pop (a small fireball) or only a spray of
        /// sparks: first a quick chain of pops scattered round the hull right after the big
        /// blast (a lorry's along its bed, a gun's slower and longer), then a few while it burns.
        /// Never another big blast on the same spot.
        /// </summary>
        public bool TryCookOff(float now, out Vector3 position, out bool pop)
        {
            foreach (var w in _wrecks)
            {
                if (w.SinkStart >= 0f || w.WasFalling || w.Gone) continue;
                var high = w.View.Def.Static ? w.View.Top * 0.6f : 0.8f;
                if (w.ChainLeft > 0 && now >= w.NextChain)
                {
                    w.ChainLeft--;
                    w.NextChain = now + (w.SlowChain ? Random.Range(0.3f, 0.8f) : Random.Range(0.22f, 0.5f));
                    pop = true;
                    position = w.ChainAlong ? AlongBed(w, high) : Around(w, high, w.View.Sim.Radius * 1.4f);
                    return true;
                }
                if (now - w.Created > (w.View.Def.Static ? StaticBurnSeconds : w.Burn) || w.PopsLeft <= 0 || now < w.NextPop) continue;
                w.PopsLeft--;
                w.NextPop = now + Random.Range(2f, 4f);
                pop = Random.value < 0.5f;
                position = Around(w, w.View.Def.Static ? high : 1.2f, 0.7f);
                return true;
            }
            position = default;
            pop = false;
            return false;
        }

        /// <summary>A falling aircraft that has just hit the ground: where, and how big it was.</summary>
        public bool TryCrash(out Vector3 position, out float size)
        {
            if (_crashes.Count == 0)
            {
                position = default;
                size = 0f;
                return false;
            }
            (position, size) = _crashes[_crashes.Count - 1];
            _crashes.RemoveAt(_crashes.Count - 1);
            return true;
        }

        /// <summary>Prompt 34 L7: a wreck that has gone left a burn mark here, this wide.</summary>
        public bool TryBurnMark(out Vector3 position, out float size)
        {
            if (_marks.Count == 0)
            {
                position = default;
                size = 0f;
                return false;
            }
            (position, size) = _marks[_marks.Count - 1];
            _marks.RemoveAt(_marks.Count - 1);
            return true;
        }

        public void Tick(float now, float dt)
        {
            if (now >= _nextTrim)
            {
                _nextTrim = now + 0.5f;
                Trim(now);
            }
            _breakup.Tick(now, dt);
            for (var i = _wrecks.Count - 1; i >= 0; i--)
            {
                var w = _wrecks[i];
                if (w.Gone || w.View.Root == null)
                {
                    if (w.View.Root != null) Object.Destroy(w.View.Root.gameObject);
                    _wrecks.RemoveAt(i);
                    continue;
                }
                if (w.SinkStart < 0f)
                {
                    w.View.AnimateWreck();
                    if (w.WasFalling && !w.View.Falling)
                    {
                        w.WasFalling = false;
                        _crashes.Add((w.View.Root.position, w.View.Sim.Radius));
                    }
                    if (now >= w.Expires) Sink(w, now);
                    Flip(w, now);
                    Hop(w, dt);
                    if (now >= w.JetFrom && now < w.JetUntil)
                    {
                        // The fountain surges, then gutters out.
                        var t = (now - w.JetFrom) / Mathf.Max(0.1f, w.JetUntil - w.JetFrom);
                        var strength = Mathf.Lerp(1.15f, 0.6f, t) * Mathf.Clamp(w.View.Sim.Radius / 2.2f, 0.8f, 1.4f);
                        _fires.Jet(w.View.Root.position + Vector3.up * 1.6f, strength, ref w.JetDebt, dt);
                    }
                }
                if (w.TurretFlying) FlyTurret(w, now, dt);

                if (w.SinkStart < 0f) continue;
                var k = (now - w.SinkStart) / SinkSeconds;
                if (k >= 1f)
                {
                    Object.Destroy(w.View.Root.gameObject);
                    _wrecks.RemoveAt(i);
                    continue;
                }
                var p = w.View.Root.position;
                w.View.Root.position = new Vector3(p.x, -SinkDepth * k * k, p.z);
            }
        }

        /// <summary>
        /// Prompt 34 L7: at most <see cref="WreckClasses.FullCap"/> full wrecks near the camera: the newest stay full, the
        /// older ones near it go within a few seconds, and wrecks far from the camera live <see cref="WreckClasses.SimpleLife"/>
        /// at most (both leave a burn mark). Bosses and fixed defences are not counted and keep their lives.
        /// </summary>
        private void Trim(float now)
        {
            var cap = WreckClasses.FullCap(MatchSettings.Tier);
            var near = 0;
            for (var i = _wrecks.Count - 1; i >= 0; i--)
            {
                var w = _wrecks[i];
                if (w.SinkStart >= 0f || w.Gone || w.View.Def.Static || w.View.Def.Boss || w.View.Root == null || w.View.Falling) continue;
                var p = w.View.Root.position;
                var far = new Vector2(p.x - Focus.x, p.z - Focus.z).magnitude > WreckClasses.NearCamera;
                if (far)
                {
                    w.Expires = Mathf.Min(w.Expires, w.Created + WreckClasses.SimpleLife);
                    continue;
                }
                // The list runs newest first from the end: those past the cap are the older ones.
                if (++near > cap) w.Expires = Mathf.Min(w.Expires, now + 3f);
            }
        }

        public void Clear()
        {
            foreach (var w in _wrecks)
                if (w.View.Root != null) Object.Destroy(w.View.Root.gameObject);
            _wrecks.Clear();
            _crashes.Clear();
            _marks.Clear();
            _breakup.Clear();
        }

        private static Vector3 Around(Wreck w, float height, float reach) =>
            w.View.Root.position + new Vector3(Random.Range(-reach, reach), height, Random.Range(-reach, reach));

        /// <summary>A point on a lorry's bed: along its back half, a little to either side.</summary>
        private static Vector3 AlongBed(Wreck w, float height)
        {
            var root = w.View.Root;
            var r = w.View.Sim.Radius;
            return root.position - root.forward * Random.Range(-0.1f * r, 0.9f * r) + root.right * Random.Range(-0.35f, 0.35f) * r +
                   Vector3.up * (height + 0.3f);
        }

        /// <summary>A wheeled hulk rolling over onto its side or roof (it rises by what it turns over on).</summary>
        private static void Flip(Wreck w, float now)
        {
            if (w.FlipStart < 0f || now < w.FlipStart) return;
            var k = Mathf.Clamp01((now - w.FlipStart) / 0.9f);
            var e = k * k * (3f - 2f * k);
            var angle = w.FlipAngle * e;
            var rad = angle * Mathf.Deg2Rad;
            w.View.Root.rotation = w.FlipBase * Quaternion.Euler(0f, 0f, w.FlipSide * angle);
            var half = w.View.Sim.Radius * 0.45f;
            w.FlipLift = Mathf.Abs(Mathf.Sin(rad)) * half + (1f - Mathf.Cos(rad)) * 0.5f * w.View.Top * 0.6f;
            if (k >= 1f) w.FlipStart = -1f;
            var p = w.View.Root.position;
            w.View.Root.position = new Vector3(p.x, w.HopHeight + w.FlipLift, p.z);
        }

        /// <summary>The hull thrown up by its death explosion, landing back with a thud.</summary>
        private static void Hop(Wreck w, float dt)
        {
            if (w.HopVelocity == 0f && w.HopHeight == 0f) return;
            w.HopVelocity -= Gravity * dt;
            w.HopHeight += w.HopVelocity * dt;
            if (w.HopHeight <= 0f)
            {
                w.HopHeight = 0f;
                w.HopVelocity = 0f;
            }
            var p = w.View.Root.position;
            w.View.Root.position = new Vector3(p.x, w.HopHeight + w.FlipLift, p.z);
        }

        /// <summary>The blown-off turret tumbles through the air trailing fire and smoke, and comes to rest burning.</summary>
        private void FlyTurret(Wreck w, float now, float dt)
        {
            var turret = w.Turret;
            if (turret == null)
            {
                w.TurretFlying = false;
                return;
            }
            w.TurretVelocity.y -= Gravity * dt;
            var position = turret.position + w.TurretVelocity * dt;
            turret.rotation = Quaternion.Euler(w.TurretSpin * dt) * turret.rotation;
            _chunks?.Trails.Fly(ref w.TurretFlame, ref w.TurretSmoke, position, true, dt);
            const float rest = 0.35f;
            if (position.y <= rest && w.TurretVelocity.y < 0f)
            {
                position.y = rest;
                if (w.TurretVelocity.y < -4f)
                {
                    w.TurretVelocity = new Vector3(w.TurretVelocity.x * 0.4f, -w.TurretVelocity.y * 0.25f, w.TurretVelocity.z * 0.4f);
                    w.TurretSpin *= 0.3f;
                    _chunks?.Trails.Impact(position);
                }
                else
                {
                    w.TurretFlying = false;
                    // Settle upright or upside down, whichever is nearer.
                    var up = Vector3.Dot(turret.up, Vector3.up) >= 0f ? Vector3.up : Vector3.down;
                    turret.rotation = Quaternion.FromToRotation(turret.up, up) * turret.rotation;
                    _chunks?.Trails.Land(position, 0f, true, now);
                    _fires.Ignite(new Vector3(position.x, 0.3f, position.z), 0.55f, Random.Range(8f, 12f), now);
                }
            }
            turret.position = position;
        }
    }
}

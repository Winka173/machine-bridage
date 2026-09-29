using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Entities;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Prompt 13 C.9: the ammunition icon beside the health bar, one set for aircraft, helicopters and
    /// launchers, built from quads like the repair mark (no textures), in flat single colours:
    /// low (a magazine with one bar, coin yellow, under 20 %), empty (an empty magazine, red, blinking
    /// gently), flying out to rearm (a return arrow, secondary grey), rearming (the magazine in our green
    /// with a ring of segments round it that fills with the stores, turning slowly and dim at the slow
    /// rate, brighter at the full one) and full (the ring flashes, then the icon goes). Enemy units show
    /// only empty and flying out. It sits right of the bar, never over it.
    /// </summary>
    public sealed partial class VehicleView
    {
        private enum StoresLook { None, Low, Empty, Leaving, Rearming, Full }

        private const int RingSegments = 12;
        private const float FlashSeconds = 0.6f;

        private Transform _storesMark, _storesRing, _magazine, _magazineBar, _arrow;
        private MeshRenderer _magazineBody, _magazineBack;
        private MeshRenderer[] _ringSegments;
        private Material _storesLow, _storesFull, _storesSlow, _storesMuted, _storesEmpty, _storesSpent, _barBack;
        private StoresLook _storesLook = StoresLook.None;
        private int _storesLit = -1;
        private bool _storesBright;
        private float _flashUntil = -1f, _ringAngle;

        private void BuildStoresMark(MeshLibrary meshes, MaterialLibrary materials)
        {
            _storesLow = materials.StoresLow;
            _storesFull = materials.StoresFull;
            _storesSlow = materials.StoresSlow;
            _storesMuted = materials.StoresMuted;
            _storesEmpty = materials.AmmoEmpty;
            _storesSpent = materials.AmmoSpent;
            _barBack = materials.BarBack;
            _storesMark = new GameObject("StoresMark").transform;
            _storesMark.SetParent(_bar, false);
            _storesMark.localPosition = new Vector3(BarWidth * 0.5f + 0.72f, 0.05f, 0f);
            // The magazine: a frame, its body, and one bar at the bottom for "low".
            _magazine = new GameObject("Magazine").transform;
            _magazine.SetParent(_storesMark, false);
            _magazineBack = CreateMesh("Frame", _magazine, meshes.Quad, materials.BarBack, false).GetComponent<MeshRenderer>();
            _magazineBack.transform.localScale = new Vector3(0.5f, 0.72f, 1f);
            _magazineBody = CreateMesh("Body", _magazine, meshes.Quad, materials.StoresFull, false).GetComponent<MeshRenderer>();
            _magazineBody.transform.localScale = new Vector3(0.3f, 0.52f, 1f);
            _magazineBody.transform.localPosition = new Vector3(0f, 0f, -0.01f);
            _magazineBar = CreateMesh("Bar", _magazine, meshes.Quad, materials.StoresLow, false);
            _magazineBar.localScale = new Vector3(0.3f, 0.12f, 1f);
            _magazineBar.localPosition = new Vector3(0f, -0.2f, -0.02f);
            // The ring round it.
            _storesRing = new GameObject("Ring").transform;
            _storesRing.SetParent(_storesMark, false);
            _ringSegments = new MeshRenderer[RingSegments];
            for (var i = 0; i < RingSegments; i++)
            {
                var angle = i * 360f / RingSegments;
                var segment = CreateMesh("Segment", _storesRing, meshes.Quad, materials.AmmoSpent, false);
                var rad = angle * Mathf.Deg2Rad;
                segment.localPosition = new Vector3(Mathf.Sin(rad) * 0.56f, Mathf.Cos(rad) * 0.56f, -0.01f);
                segment.localRotation = Quaternion.Euler(0f, 0f, -angle);
                segment.localScale = new Vector3(0.2f, 0.09f, 1f);
                _ringSegments[i] = segment.GetComponent<MeshRenderer>();
            }
            // The return arrow: a shaft and a head pointing back (to the left, away from the fight).
            _arrow = new GameObject("Arrow").transform;
            _arrow.SetParent(_storesMark, false);
            var disc = CreateMesh("Back", _arrow, meshes.Quad, materials.BarBack, false);
            disc.localScale = new Vector3(0.74f, 0.74f, 1f);
            disc.localRotation = Quaternion.Euler(0f, 0f, 45f);
            var shaft = CreateMesh("Shaft", _arrow, meshes.Quad, materials.StoresMuted, false);
            shaft.localScale = new Vector3(0.44f, 0.1f, 1f);
            shaft.localPosition = new Vector3(0.05f, 0f, -0.01f);
            foreach (var side in new[] { 1f, -1f })
            {
                var head = CreateMesh("Head", _arrow, meshes.Quad, materials.StoresMuted, false);
                head.localScale = new Vector3(0.26f, 0.1f, 1f);
                head.localRotation = Quaternion.Euler(0f, 0f, 40f * side);
                head.localPosition = new Vector3(-0.12f, 0.08f * side, -0.01f);
            }
            _storesMark.gameObject.SetActive(false);
        }

        /// <summary>What the icon should show now (by the side watching: the enemy's only empty and flying out).</summary>
        private StoresLook StoresState(out float share, out bool bright)
        {
            share = 1f;
            bright = false;
            if (MatchSettings.AmmoIcons == 1 && !Sim.Flying) return StoresLook.None;
            bool empty, leaving, rearming;
            if (Sim.HasStores)
            {
                share = Sim.StoresShare;
                empty = Sim.StoresEmpty;
                leaving = Sim.Supply == SupplyState.Leaving;
                // Rearming: at the holding pattern or a site, or at the full rate in a lull.
                rearming = share < 0.999f && (Sim.Supply == SupplyState.Holding || Sim.RearmRate >= 1f);
                bright = Sim.RearmRate >= 1f;
            }
            else
            {
                var max = Mathf.Max(1, Sim.Def.Mounts[0].Weapon.Ammo);
                var left = Mathf.Max(0, Sim.Ammo(0));
                empty = Sim.OutOfAmmo && Sim.ReloadPaused;
                leaving = false;
                rearming = Sim.OutOfAmmo && !Sim.ReloadPaused;
                share = Sim.OutOfAmmo ? Sim.ReloadProgress : (float)left / max;
                bright = true;
                if (!Sim.OutOfAmmo && left == 1 && max > 1) share = Mathf.Min(share, 0.19f);
            }
            if (leaving) return StoresLook.Leaving;
            if (empty && !rearming) return StoresLook.Empty;
            if (!_ours) return StoresLook.None;
            if (rearming) return StoresLook.Rearming;
            if (share < 0.2f) return StoresLook.Low;
            return StoresLook.None;
        }

        /// <summary>Whether the icon has anything to show this frame (a state, or the full flash).</summary>
        private bool StoresWanted()
        {
            var look = StoresState(out _, out _);
            if (_storesLook == StoresLook.Rearming && look == StoresLook.None && _ours) _flashUntil = Time.time + FlashSeconds;
            if (look == StoresLook.None && _storesLook == StoresLook.Rearming) _storesLook = StoresLook.None;
            return look != StoresLook.None || Time.time < _flashUntil;
        }

        /// <summary>Draws the icon; true while it shows (the health bar shows with it).</summary>
        private bool RenderStoresMark()
        {
            if (_storesMark == null) return false;
            var look = StoresState(out var share, out var bright);
            // Coming off the ring full: a short flash (started by StoresWanted), then nothing.
            var flashing = look == StoresLook.None && Time.time < _flashUntil;
            if (flashing) look = StoresLook.Full;
            var show = look != StoresLook.None;
            if (_storesMark.gameObject.activeSelf != show) _storesMark.gameObject.SetActive(show);
            if (!show)
            {
                _storesLook = look;
                return false;
            }
            if (look != _storesLook)
            {
                _storesLook = look;
                _storesLit = -1;
                _magazine.gameObject.SetActive(look != StoresLook.Leaving);
                _arrow.gameObject.SetActive(look == StoresLook.Leaving);
                _storesRing.gameObject.SetActive(look is StoresLook.Rearming or StoresLook.Full);
                _magazineBar.gameObject.SetActive(look == StoresLook.Low);
                _magazineBody.sharedMaterial = look switch
                {
                    StoresLook.Low => _storesSpent,
                    StoresLook.Empty => _storesSpent,
                    _ => _storesFull,
                };
                _magazineBack.sharedMaterial = look == StoresLook.Empty ? _storesEmpty : _barBack;
            }
            switch (look)
            {
                case StoresLook.Empty:
                    // A gentle blink: the red frame dims every other half second.
                    var on = Mathf.Repeat(Time.time * 1.6f, 1f) < 0.65f;
                    _magazineBack.sharedMaterial = on ? _storesEmpty : _barBack;
                    break;
                case StoresLook.Rearming:
                    var lit = Mathf.Clamp(Mathf.FloorToInt(share * RingSegments + 0.001f), 0, RingSegments);
                    if (lit != _storesLit || bright != _storesBright)
                    {
                        _storesLit = lit;
                        _storesBright = bright;
                        for (var i = 0; i < RingSegments; i++) _ringSegments[i].sharedMaterial = i < lit ? (bright ? _storesFull : _storesSlow) : _storesSpent;
                        _magazineBody.sharedMaterial = bright ? _storesFull : _storesSlow;
                    }
                    // The ring turns: slowly at the slow rate, faster at the full one.
                    _ringAngle = Mathf.Repeat(_ringAngle + Time.deltaTime * (bright ? 90f : 30f), 360f);
                    _storesRing.localRotation = Quaternion.Euler(0f, 0f, -_ringAngle);
                    break;
                case StoresLook.Full:
                    if (_storesLit != RingSegments)
                    {
                        _storesLit = RingSegments;
                        foreach (var s in _ringSegments) s.sharedMaterial = _storesFull;
                    }
                    var left = Mathf.Clamp01((_flashUntil - Time.time) / FlashSeconds);
                    _storesMark.localScale = Vector3.one * (1f + 0.25f * Mathf.Sin(left * Mathf.PI));
                    return true;
            }
            _storesMark.localScale = Vector3.one;
            return true;
        }
    }
}

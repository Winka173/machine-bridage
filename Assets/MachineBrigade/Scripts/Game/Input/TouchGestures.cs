using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.EnhancedTouch;
using ETouch = UnityEngine.InputSystem.EnhancedTouch.Touch;
using TouchPhase = UnityEngine.InputSystem.TouchPhase;

namespace MachineBrigade.Game.Input
{
    public interface IGestureHandler
    {
        void OnTap(Vector2 screen);
        void OnDoubleTap(Vector2 screen);
        void OnPan(Vector2 fromScreen, Vector2 toScreen);
        void OnPinch(float scale, Vector2 centreScreen);
        void OnBoxUpdate(Vector2 startScreen, Vector2 currentScreen);
        void OnBoxEnd(Vector2 startScreen, Vector2 endScreen);
        void OnBoxCancel();
    }

    /// <summary>
    /// Turns raw touches (or the mouse in the editor) into gestures:
    /// tap, double tap, one-finger pan, two-finger pinch and long-press box selection.
    /// A pinch never ends as a tap (T07), and a touch that starts on the HUD never
    /// reaches the battlefield (V2 R16).
    /// </summary>
    public sealed class TouchGestures
    {
        private const float LongPressSeconds = 0.4f;
        private const float DoubleTapSeconds = 0.3f;

        private enum State { Idle, Pending, Pan, Box, Pinch, Blocked }

        private readonly IGestureHandler _handler;
        private readonly Func<Vector2, bool> _isOverUi;
        private readonly List<Vector2> _points = new();
        private readonly float _dragThreshold;
        private State _state;
        private int _previousCount;
        private Vector2 _start, _last, _pinchCentre, _lastTapPosition, _rightDragLast;
        private float _startTime, _pinchDistance, _lastTapTime = -10f;
        private bool _rightDragging;

        /// <summary>When it returns true, a one-finger drag box-selects instead of panning.</summary>
        public Func<bool> BoxMode { get; set; } = () => false;

        public TouchGestures(IGestureHandler handler, Func<Vector2, bool> isOverUi)
        {
            _handler = handler;
            _isOverUi = isOverUi;
            _dragThreshold = 12f * Mathf.Max(1f, Screen.dpi / 160f);
        }

        public void Enable() => EnhancedTouchSupport.Enable();

        public void Disable() => EnhancedTouchSupport.Disable();

        public void Tick(float now)
        {
            Collect();
            var count = _points.Count;
            switch (_state)
            {
                case State.Idle:
                    if (count == 0 || _previousCount != 0) break;
                    _start = _last = _points[0];
                    _startTime = now;
                    if (_isOverUi(_points[0])) _state = State.Blocked;
                    else if (count >= 2) BeginPinch();
                    else _state = State.Pending;
                    break;

                case State.Pending:
                    if (count >= 2) BeginPinch();
                    else if (count == 0)
                    {
                        Tap(_last, now);
                        _state = State.Idle;
                    }
                    else
                    {
                        var p = _points[0];
                        if ((p - _start).magnitude > _dragThreshold)
                        {
                            if (BoxMode())
                            {
                                _state = State.Box;
                                _handler.OnBoxUpdate(_start, p);
                            }
                            else
                            {
                                _state = State.Pan;
                                _handler.OnPan(_last, p);
                            }
                        }
                        else if (now - _startTime >= LongPressSeconds)
                        {
                            _state = State.Box;
                            _handler.OnBoxUpdate(_start, p);
                        }
                        _last = p;
                    }
                    break;

                case State.Pan:
                    if (count >= 2) BeginPinch();
                    else if (count == 0) _state = State.Idle;
                    else
                    {
                        _handler.OnPan(_last, _points[0]);
                        _last = _points[0];
                    }
                    break;

                case State.Box:
                    if (count >= 2)
                    {
                        _handler.OnBoxCancel();
                        BeginPinch();
                    }
                    else if (count == 0)
                    {
                        _handler.OnBoxEnd(_start, _last);
                        _state = State.Idle;
                    }
                    else
                    {
                        _last = _points[0];
                        _handler.OnBoxUpdate(_start, _last);
                    }
                    break;

                case State.Pinch:
                    if (count == 0) _state = State.Idle;
                    else if (count >= 2)
                    {
                        if (_previousCount < 2) BeginPinch(); // a finger came back: restart without a jump
                        var distance = Vector2.Distance(_points[0], _points[1]);
                        var centre = (_points[0] + _points[1]) * 0.5f;
                        if (_pinchDistance > 1f) _handler.OnPinch(distance / _pinchDistance, centre);
                        _handler.OnPan(_pinchCentre, centre);
                        _pinchDistance = distance;
                        _pinchCentre = centre;
                    }
                    // One finger left after a pinch: wait for release instead of panning or tapping.
                    break;

                case State.Blocked:
                    if (count == 0) _state = State.Idle;
                    break;
            }
            _previousCount = count;
            MouseExtras();
        }

        private void BeginPinch()
        {
            _state = State.Pinch;
            _pinchDistance = Vector2.Distance(_points[0], _points[1]);
            _pinchCentre = (_points[0] + _points[1]) * 0.5f;
        }

        private void Tap(Vector2 position, float now)
        {
            if (now - _lastTapTime < DoubleTapSeconds && (position - _lastTapPosition).magnitude < _dragThreshold * 3f)
            {
                _lastTapTime = -10f;
                _handler.OnDoubleTap(position);
                return;
            }
            _lastTapTime = now;
            _lastTapPosition = position;
            _handler.OnTap(position);
        }

        private void Collect()
        {
            _points.Clear();
            foreach (var touch in ETouch.activeTouches)
            {
                var phase = touch.phase;
                if (phase == TouchPhase.Began || phase == TouchPhase.Moved || phase == TouchPhase.Stationary)
                    _points.Add(touch.screenPosition);
            }
            if (_points.Count == 0 && Mouse.current != null && Mouse.current.leftButton.isPressed)
                _points.Add(Mouse.current.position.ReadValue());
        }

        /// <summary>How much one wheel notch zooms (15 %).</summary>
        internal const float WheelStep = 1.15f;

        /// <summary>
        /// The zoom factor for a frame's wheel movement. Play-test 6: the Input System reports a notch as 1 (its
        /// uniform scroll setting, the default) where the old code expected 120, so a notch zoomed 0.1 % and the
        /// owner had to scroll a long way; a notch is now one step either way (at most three a frame).
        /// </summary>
        internal static float WheelZoom(float scroll)
        {
            var notches = Mathf.Abs(scroll) >= 20f ? scroll / 120f : scroll;
            return Mathf.Pow(WheelStep, Mathf.Clamp(notches, -3f, 3f));
        }

        /// <summary>Editor conveniences: wheel zooms, right-drag pans.</summary>
        private void MouseExtras()
        {
            var mouse = Mouse.current;
            if (mouse == null) return;
            var position = mouse.position.ReadValue();
            var scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) > 0.01f && !_isOverUi(position)) _handler.OnPinch(WheelZoom(scroll), position);

            if (mouse.rightButton.isPressed)
            {
                if (_rightDragging) _handler.OnPan(_rightDragLast, position);
                _rightDragLast = position;
                _rightDragging = true;
            }
            else
            {
                _rightDragging = false;
            }
        }
    }
}

using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// A tap that lands. UI Toolkit's <see cref="Clickable"/> only fires if the element still holds
    /// the pointer when it is released, and a scroll view takes the pointer as soon as a finger
    /// drifts a pixel or two, so taps on phones (and presses on a busy frame) were often lost.
    /// This fires on release if the pointer has not travelled more than a finger's slop since it
    /// went down, whoever holds the pointer by then; a real drag (a scroll) cancels it. The
    /// release is watched from the panel's root, so it is seen even when a scroll view has taken
    /// the pointer. While pressed, the element carries the "pressed" class for the pushed-in look.
    /// A hold (prompt 11: a card held shows its full name) is optional: once the finger has stayed
    /// down for <see cref="HoldSeconds"/> the hold callback gets true, and on release false, and the
    /// tap is not fired.
    /// </summary>
    internal sealed class Tap : Manipulator
    {
        /// <summary>How far (panel pixels) a press may travel and still count as a tap.</summary>
        private const float Slop = 18f;

        /// <summary>How long a press must stay down to count as a hold.</summary>
        public const float HoldSeconds = 0.45f;

        /// <summary>Marks a panel root whose release and move events are already watched.</summary>
        private const string RootMark = "tap-root";

        /// <summary>Marks every element that takes a tap, so the UI checks can find the touch targets (UiLayoutTests).</summary>
        public const string TargetClass = "mb-tap";

        private static Tap _pending;
        private static int _pointer = -1;
        private static long _downStamp;
        private static Vector2 _start;

        private readonly Action _action;
        private readonly Action<bool> _hold;
        private IVisualElementScheduledItem _holdTimer;
        private bool _holding;

        public Tap(Action action) => _action = action;

        /// <param name="hold">Called with true when a press is held, and with false when it ends; a held press fires no tap.</param>
        public Tap(Action action, Action<bool> hold)
        {
            _action = action;
            _hold = hold;
        }

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _pending = null;
            _pointer = -1;
        }

        protected override void RegisterCallbacksOnTarget()
        {
            target.AddToClassList(TargetClass);
            target.RegisterCallback<PointerDownEvent>(OnDown);
            target.RegisterCallback<AttachToPanelEvent>(OnAttach);
            target.RegisterCallback<DetachFromPanelEvent>(OnDetach);
            if (target.panel != null) Hook(target.panel.visualTree);
        }

        protected override void UnregisterCallbacksFromTarget()
        {
            target.UnregisterCallback<PointerDownEvent>(OnDown);
            target.UnregisterCallback<AttachToPanelEvent>(OnAttach);
            target.UnregisterCallback<DetachFromPanelEvent>(OnDetach);
            if (_pending == this) Cancel();
        }

        private void OnAttach(AttachToPanelEvent evt) => Hook(evt.destinationPanel?.visualTree);

        private void OnDetach(DetachFromPanelEvent evt)
        {
            if (_pending == this) Cancel();
        }

        private static void Hook(VisualElement root)
        {
            if (root == null || root.ClassListContains(RootMark)) return;
            root.AddToClassList(RootMark);
            root.RegisterCallback<PointerMoveEvent>(OnMove, TrickleDown.TrickleDown);
            root.RegisterCallback<PointerUpEvent>(OnUp, TrickleDown.TrickleDown);
            root.RegisterCallback<PointerCancelEvent>(OnCancel, TrickleDown.TrickleDown);
        }

        private void OnDown(PointerDownEvent evt)
        {
            if (evt.pointerType == UnityEngine.UIElements.PointerType.mouse && evt.button != 0) return;
            // A button inside another: the press bubbles from the inner one first, which keeps it.
            // (Propagation is not stopped, so a scroll view round the button can still start a drag.)
            if (_pending != null && _pointer == evt.pointerId && _downStamp == evt.timestamp) return;
            Cancel();
            _pending = this;
            _pointer = evt.pointerId;
            _downStamp = evt.timestamp;
            _start = evt.position;
            target.AddToClassList("pressed");
            if (_hold == null) return;
            _holdTimer?.Pause();
            _holdTimer = target.schedule.Execute(() =>
            {
                if (_pending != this) return;
                _holding = true;
                _hold(true);
            }).StartingIn((long)(HoldSeconds * 1000f));
        }

        private static void OnMove(PointerMoveEvent evt)
        {
            if (_pending == null || evt.pointerId != _pointer) return;
            if (((Vector2)evt.position - _start).sqrMagnitude > Slop * Slop) Cancel();
        }

        private static void OnUp(PointerUpEvent evt)
        {
            if (_pending == null || evt.pointerId != _pointer) return;
            var tap = _pending;
            var travelled = ((Vector2)evt.position - _start).sqrMagnitude;
            var held = tap._holding;
            Cancel();
            if (held) return;
            if (travelled > Slop * Slop || tap.target == null || tap.target.panel == null || !tap.target.enabledInHierarchy) return;
            tap._action?.Invoke();
        }

        private static void OnCancel(PointerCancelEvent evt)
        {
            if (evt.pointerId == _pointer) Cancel();
        }

        private static void Cancel()
        {
            _pending?.target?.RemoveFromClassList("pressed");
            if (_pending != null)
            {
                _pending._holdTimer?.Pause();
                _pending._holdTimer = null;
                if (_pending._holding)
                {
                    _pending._holding = false;
                    _pending._hold?.Invoke(false);
                }
            }
            _pending = null;
            _pointer = -1;
        }
    }
}

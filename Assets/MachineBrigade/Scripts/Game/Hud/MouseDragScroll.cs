using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Lets a mouse drag a <see cref="ScrollView"/> the way a finger does. UI Toolkit only
    /// drag-scrolls for touch, so in the editor's Game view (and on desktop) the long menu pages
    /// could not be pulled down. A press on a card only turns into a scroll once it moves a few
    /// pixels; taking the pointer then cancels the card's click, so a drag never taps a card.
    /// </summary>
    internal sealed class MouseDragScroll : PointerManipulator
    {
        private const float Threshold = 8f;

        private readonly ScrollView _scroll;
        private bool _down, _dragging;
        private Vector2 _start, _startOffset;
        private int _pointer = -1;

        private MouseDragScroll(ScrollView scroll)
        {
            _scroll = scroll;
            target = scroll;
        }

        public static void Attach(ScrollView scroll) => scroll.AddManipulator(new MouseDragScroll(scroll));

        protected override void RegisterCallbacksOnTarget()
        {
            target.RegisterCallback<PointerDownEvent>(OnDown, TrickleDown.TrickleDown);
            target.RegisterCallback<PointerMoveEvent>(OnMove, TrickleDown.TrickleDown);
            target.RegisterCallback<PointerUpEvent>(OnUp, TrickleDown.TrickleDown);
            target.RegisterCallback<PointerCaptureOutEvent>(OnLost);
        }

        protected override void UnregisterCallbacksFromTarget()
        {
            target.UnregisterCallback<PointerDownEvent>(OnDown, TrickleDown.TrickleDown);
            target.UnregisterCallback<PointerMoveEvent>(OnMove, TrickleDown.TrickleDown);
            target.UnregisterCallback<PointerUpEvent>(OnUp, TrickleDown.TrickleDown);
            target.UnregisterCallback<PointerCaptureOutEvent>(OnLost);
        }

        private void OnDown(PointerDownEvent evt)
        {
            if (evt.pointerType != UnityEngine.UIElements.PointerType.mouse || evt.button != 0) return;
            _down = true;
            _dragging = false;
            _pointer = evt.pointerId;
            _start = evt.position;
            _startOffset = _scroll.scrollOffset;
        }

        private void OnMove(PointerMoveEvent evt)
        {
            if (!_down || evt.pointerId != _pointer) return;
            var delta = (Vector2)evt.position - _start;
            if (!_dragging)
            {
                if (Mathf.Abs(delta.y) < Threshold) return;
                _dragging = true;
                target.CapturePointer(_pointer);
            }
            _scroll.scrollOffset = new Vector2(_startOffset.x, _startOffset.y - delta.y);
            evt.StopPropagation();
        }

        private void OnUp(PointerUpEvent evt)
        {
            if (evt.pointerId != _pointer) return;
            if (_dragging)
            {
                evt.StopPropagation();
                if (target.HasPointerCapture(_pointer)) target.ReleasePointer(_pointer);
            }
            _down = _dragging = false;
        }

        private void OnLost(PointerCaptureOutEvent evt)
        {
            if (_dragging) _down = _dragging = false;
        }
    }
}

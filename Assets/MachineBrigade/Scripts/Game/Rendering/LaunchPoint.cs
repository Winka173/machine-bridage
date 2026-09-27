using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Where one launcher of a weapon slot sits (a rocket pod, a missile rail, a minigun), found
    /// from the model's own meshes (see ModelLibrary.AddLaunchPoints): rounds leave from these in
    /// turn instead of from one muzzle on the centre line. A multi-tube face (a rocket pod, an
    /// MLRS box) has a spread, half its width and height, and each round leaves from a random tube in it.
    /// </summary>
    public sealed class LaunchPoint : MonoBehaviour
    {
        public string Slot;
        public Vector2 Spread;
    }
}

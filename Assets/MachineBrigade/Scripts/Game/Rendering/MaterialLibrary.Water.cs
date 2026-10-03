using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Play-test 13 ("biển nhìn không thực xíu nào"): the water material on the MachineBrigade/Water shader. It keeps the
    /// old Lit water's property names (<c>_BaseColor</c> the deep colour, <c>_Roughness</c>), so themes and maps set it as
    /// before; <c>_ShallowColor</c> is the colour at the shore. Vertex colours carry the depth (r), the open water (g) and a
    /// brightness (b) (see the shader's header); a mesh without colours is deep open sea.
    /// </summary>
    public sealed partial class MaterialLibrary
    {
        /// <summary>The water's shader name.</summary>
        public const string WaterShader = "MachineBrigade/Water";

        private Material NewWater(Color deep)
        {
            var m = new Material(Find(WaterShader)) { name = "Water", enableInstancing = true };
            m.SetColor("_BaseColor", deep);
            m.SetColor("_ShallowColor", ShallowOf(deep, new Color(0.83f, 0.75f, 0.58f)));
            m.SetFloat("_Roughness", 0.08f);
            _owned.Add(m);
            return m;
        }

        /// <summary>
        /// The water's colour over a shallow bottom: the deep colour lightened toward the sand (light reaches the bottom and
        /// comes back) and shifted a little toward turquoise, as clear coastal water looks.
        /// </summary>
        public static Color ShallowOf(Color deep, Color sand)
        {
            var c = Color.Lerp(deep, sand, 0.42f);
            return Color.Lerp(c, new Color(0.3f, 0.72f, 0.68f), 0.18f);
        }
    }
}

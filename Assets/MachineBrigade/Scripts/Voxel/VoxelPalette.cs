using UnityEngine;

namespace MachineBrigade.Voxel
{
    /// <summary>
    /// Shared colour slots. Models store slot numbers, so one model can be meshed in any team's
    /// colours by swapping <see cref="TeamMain"/> and <see cref="TeamDark"/>.
    /// </summary>
    public static class VoxelPalette
    {
        public const byte TeamMain = 1;
        public const byte TeamDark = 2;
        public const byte Metal = 3;
        public const byte Rubber = 4;
        public const byte Glass = 5;
        public const byte Wall = 6;
        public const byte Roof = 7;
        public const byte Window = 8;
        public const byte Wood = 9;
        public const byte Leaf = 10;
        public const byte LeafDark = 11;
        public const byte BarrelRed = 12;
        public const byte Stone = 13;
        public const byte TankWhite = 14;
        public const byte Stripe = 15;
        public const byte Crate = 16;
        public const byte Rubble = 17;
        public const byte Door = 18;
        public const byte Char = 19;
        public const byte Light = 20;

        public static Color32[] Create(Color32 teamMain, Color32 teamDark)
        {
            var p = new Color32[256];
            for (var i = 0; i < p.Length; i++) p[i] = new Color32(255, 0, 255, 255); // unmistakable if a slot is missing
            p[TeamMain] = teamMain;
            p[TeamDark] = teamDark;
            p[Metal] = new Color32(58, 60, 62, 255);
            p[Rubber] = new Color32(32, 32, 34, 255);
            p[Glass] = new Color32(96, 132, 150, 255);
            p[Wall] = new Color32(206, 188, 158, 255);
            p[Roof] = new Color32(140, 66, 48, 255);
            p[Window] = new Color32(40, 54, 70, 255);
            p[Wood] = new Color32(92, 64, 40, 255);
            p[Leaf] = new Color32(70, 118, 48, 255);
            p[LeafDark] = new Color32(48, 90, 36, 255);
            p[BarrelRed] = new Color32(178, 42, 30, 255);
            p[Stone] = new Color32(128, 126, 120, 255);
            p[TankWhite] = new Color32(218, 216, 204, 255);
            p[Stripe] = new Color32(222, 180, 32, 255);
            p[Crate] = new Color32(92, 98, 54, 255);
            p[Rubble] = new Color32(104, 96, 86, 255);
            p[Door] = new Color32(86, 58, 38, 255);
            p[Char] = new Color32(30, 28, 26, 255);
            p[Light] = new Color32(255, 222, 150, 255);
            return p;
        }

        public static Color32[] Neutral { get; } = Create(new Color32(120, 120, 110, 255), new Color32(80, 80, 72, 255));
    }
}

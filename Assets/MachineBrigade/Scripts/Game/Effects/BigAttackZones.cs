using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 18 D.2: every boss's big-attack warning drawn the same way, exactly the sim's zones (BigAttackState):
    /// a circle as a strike ring whose fill sweeps round to the moment it lands, a strip, a line or a sweep as a bright
    /// outline with a countdown ring at its middle, each point of a walking barrage or a missile's landing its own ring
    /// and countdown. Outlines and thin rings only (no fill over the player's units); unlit HDR red so it reads on every
    /// map and weather, Low graphics included. The charging part pulses on the boss. View only.
    /// </summary>
    internal sealed class BigAttackZones
    {
        private const int Marks = 28, Outlines = 8;

        // Fix prompt L5: a thin edge and a faint fill (GroundMark.Style.Warning), brighter than an ordinary round's: a super weapon.
        private static readonly Color Edge = new(2.6f, 0.36f, 0.18f, 1f);
        private static readonly Color Fill = new(2f, 0.4f, 0.16f, 0.7f);
        private static readonly Color Soft = new(1.4f, 1.1f, 0.9f, 0.55f);

        private readonly List<GroundMark> _marks = new();
        private readonly List<LineRenderer> _lines = new();
        private readonly Vector3[] _corners = new Vector3[4];

        public BigAttackZones(MaterialLibrary materials, MeshLibrary meshes, Transform parent)
        {
            var root = new GameObject("Big Attacks").transform;
            root.SetParent(parent, false);
            for (var i = 0; i < Marks; i++)
            {
                var mark = new GroundMark("Big Attack Mark", root, meshes, materials, GroundMark.Style.Warning) { Visible = false };
                _marks.Add(mark);
            }
            for (var i = 0; i < Outlines; i++)
            {
                var go = new GameObject("Big Attack Outline");
                go.transform.SetParent(root, false);
                var line = go.AddComponent<LineRenderer>();
                line.sharedMaterial = materials.StrikeWarning;
                line.useWorldSpace = true;
                line.loop = true;
                line.positionCount = 4;
                line.alignment = LineAlignment.View;
                line.numCornerVertices = 2;
                line.shadowCastingMode = ShadowCastingMode.Off;
                line.receiveShadows = false;
                line.widthMultiplier = 0.45f;
                line.enabled = false;
                _lines.Add(line);
            }
        }

        /// <summary>
        /// Fix prompt L5: the gate the zones are offered to. A boss's big attack is a super weapon's: always shown, drawn on
        /// top (<see cref="SuperHeight"/>), Off in the Settings included; none for a boss of the player's side.
        /// </summary>
        public WarningGate Gate { get; set; }

        /// <summary>A super weapon's rings sit this high, over every other ring.</summary>
        private const float SuperHeight = 0.16f;

        /// <summary>Every frame: the zones of every boss whose big attack is warning or landing.</summary>
        public void Tick(ViewRegistry views, float now)
        {
            var mark = 0;
            var line = 0;
            var all = views.All;
            for (var v = 0; v < all.Count; v++)
            {
                var sim = all[v].Sim;
                if (sim?.BigAttack is not { } big || big.Stage == BigStage.Ready || !sim.IsAlive) continue;
                if (sim.Team == views.PlayerTeam) continue;
                Gate?.Offer(big, new Vector3(sim.Position.X, 0f, sim.Position.Y), sim.Radius, WarningKind.Super);
                var zones = big.Zones;
                for (var z = 0; z < zones.Count; z++)
                {
                    var zone = zones[z];
                    var span = zone.Due - big.WarnStart;
                    var progress = span > 0.05 ? Mathf.Clamp01((float)((big.Now - big.WarnStart) / span)) : 1f;
                    var urgency = Mathf.Clamp01(1f - (float)(zone.Due - big.Now) / 2f);
                    var edge = zone.Harmful ? Edge : Soft;
                    var fill = zone.Harmful ? Fill : Soft;
                    var centre = new Vector3(zone.Centre.X, SuperHeight, zone.Centre.Y);
                    if (!zone.Rect)
                    {
                        if (mark >= _marks.Count) continue;
                        var m = _marks[mark++];
                        m.Transform.position = centre;
                        m.Transform.localScale = Vector3.one * Mathf.Max(1f, zone.Radius) * (1f + 0.04f * Mathf.Sin(now * Mathf.Lerp(6f, 20f, urgency)));
                        m.Set(edge, fill, progress, urgency);
                        m.Visible = true;
                        continue;
                    }
                    if (line < _lines.Count)
                    {
                        var l = _lines[line++];
                        var axis = new Vector3(zone.Axis.X, 0f, zone.Axis.Y);
                        var across = new Vector3(zone.Axis.Y, 0f, -zone.Axis.X);
                        var a = axis * zone.HalfLength;
                        var b = across * Mathf.Max(0.6f, zone.HalfWidth);
                        _corners[0] = centre - a - b;
                        _corners[1] = centre + a - b;
                        _corners[2] = centre + a + b;
                        _corners[3] = centre - a + b;
                        l.SetPositions(_corners);
                        l.widthMultiplier = Mathf.Lerp(0.35f, 0.7f, urgency);
                        l.enabled = true;
                    }
                    // Its countdown ring at the middle.
                    if (mark < _marks.Count)
                    {
                        var m = _marks[mark++];
                        m.Transform.position = centre;
                        m.Transform.localScale = Vector3.one * Mathf.Clamp(zone.HalfWidth, 2.5f, 6f);
                        m.Set(edge, fill, progress, urgency);
                        m.Visible = true;
                    }
                }
            }
            for (var i = mark; i < _marks.Count; i++) _marks[i].Visible = false;
            for (var i = line; i < _lines.Count; i++) _lines[i].enabled = false;
        }
    }
}

// Markings painted on the ground: objective circles, strike telegraphs, selection brackets,
// move markers and the shadow ring under aircraft. Everything is drawn from the quad's UVs as
// signed distances, anti-aliased with screen-space derivatives, so the rings stay crisp and
// round at any zoom (the old ring meshes showed their polygon edges). Per-renderer values come
// from a MaterialPropertyBlock:
//   _Color   main colour (HDR glows through bloom)
//   _Accent  second colour (capture progress, strike fill)
//   _Params  x: style (0 objective, 1 strike, 2 selection, 3 move marker, 4 aircraft ring, 5 warning ring)
//            y: progress 0..1 (capture, time to impact)
//            z: pulse 0..1 (contested point, imminent strike)
//            w: seed (desynchronises animation between marks)
Shader "MachineBrigade/GroundMark"
{
    Properties
    {
        [HDR] _Color ("Color", Color) = (1, 1, 1, 1)
        [HDR] _Accent ("Accent", Color) = (1, 1, 1, 1)
        _Params ("Style, Progress, Pulse, Seed", Vector) = (0, 0, 0, 0)
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent-20" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }

        Pass
        {
            Name "GroundMark"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half4 _Accent;
                float4 _Params;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float fog : TEXCOORD1;
            };

            // Fog from view depth. URP's clip-space fog assumes a perspective camera; with this
            // orthographic one it gave no fog at all on OpenGL ES.
            float OrthoFog(float3 positionWS)
            {
                return ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = input.uv;
                output.fog = OrthoFog(TransformObjectToWorld(input.positionOS.xyz));
                return output;
            }

            // Coverage of a band of half-width w around radius c, anti-aliased by aa.
            half Band(float r, float c, float w, float aa)
            {
                return (half)saturate((w - abs(r - c)) / aa + 0.5);
            }

            // Repeating on/off pattern around the circle: n segments, `fill` of each drawn.
            half Dashes(float turn, float n, float fill, float aaTurn)
            {
                float f = frac(turn * n);
                float w = max(aaTurn * n, 1e-4);
                return (half)(saturate(f / w + 0.5) * saturate((fill - f) / w + 0.5));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 p = input.uv * 2.0 - 1.0;
                float r = length(p);
                float aa = max(fwidth(r), 1e-4) * 1.2;
                // Angle as a fraction of a turn, clockwise from "north".
                float turn = frac(atan2(p.x, p.y) / 6.2831853 + 1.0);
                float aaTurn = aa / max(r * 6.2831853, 1e-3);
                float time = _Time.y + _Params.w * 17.0;
                float style = _Params.x;
                float progress = saturate(_Params.y);
                float pulse = _Params.z;

                half3 colour = _Color.rgb;
                half alpha = 0;

                if (style < 0.5)
                {
                    // Objective: a solid rim in the owner's colour, a slowly turning dashed ring
                    // inside it, the capture progress sweeping round as an arc, a soft tint.
                    half rim = Band(r, 0.955, 0.02, aa);
                    half dashes = Band(r, 0.885, 0.012, aa) * Dashes(turn + time * 0.01, 36.0, 0.55, aaTurn);
                    half arc = Band(r, 0.92, 0.03, aa) * saturate((progress - turn) / aaTurn + 0.5) * step(0.005, progress);
                    half tint = saturate(1.0 - r) * 0.1 + Band(r, 0.8, 0.2, aa) * 0.05;
                    half glow = 1.0 + pulse * (0.6 + 0.4 * sin(time * 8.0));
                    colour = lerp(_Color.rgb * glow, _Accent.rgb * 1.3, arc);
                    alpha = saturate(rim * 0.95 + dashes * 0.7 + arc + tint) * step(r, 1.0);
                }
                else if (style < 1.5)
                {
                    // Strike telegraph: a heavy red ring with turning dashes, crosshair ticks,
                    // and a fill that sweeps round until the moment of impact.
                    half beat = 0.75 + 0.25 * sin(time * lerp(6.0, 22.0, pulse));
                    half rim = Band(r, 0.94, 0.045, aa);
                    half dashes = Band(r, 0.8, 0.025, aa) * Dashes(turn - time * 0.08, 16.0, 0.5, aaTurn);
                    float2 q = abs(p);
                    half crosshair = (half)(saturate((0.018 - min(q.x, q.y)) / aa + 0.5) * step(0.25, r) * step(r, 0.62));
                    half centreDot = Band(r, 0.0, 0.05, aa);
                    half sweep = saturate((progress - turn) / aaTurn + 0.5) * step(r, 0.9) * 0.22;
                    colour = lerp(_Color.rgb, _Accent.rgb, sweep > 0.01 ? 0.35 : 0.0) * beat;
                    alpha = saturate(rim + dashes * 0.85 + crosshair * 0.8 + centreDot + sweep) * step(r, 1.0);
                }
                else if (style > 4.5)
                {
                    // Fix prompt L5: a warning ring: a thin edge on the damage radius and a faint fill (not solid red),
                    // heavier toward the middle; the time left runs round the edge as a thin arc. _Color.a fades it in.
                    half rim = Band(r, 0.975, 0.016, aa);
                    half arc = Band(r, 0.93, 0.012, aa) * saturate((progress - turn) / aaTurn + 0.5) * step(0.005, progress);
                    half fill = (0.07 + 0.11 * saturate(1.0 - r)) * step(r, 0.96);
                    half beat = 1.0 + pulse * 0.25 * sin(time * 14.0);
                    colour = lerp(_Color.rgb, _Accent.rgb, saturate(arc + fill * 2.0)) * beat;
                    alpha = saturate(rim + arc * 0.8 + fill * _Accent.a) * step(r, 1.0);
                }
                else if (style < 2.5)
                {
                    // Selection: four brackets turning slowly round the vehicle.
                    half ring = Band(r, 0.9, 0.05, aa) * Dashes(turn + time * 0.05, 4.0, 0.62, aaTurn);
                    half inner = Band(r, 0.9, 0.012, aa) * 0.35;
                    alpha = saturate(ring + inner);
                }
                else if (style < 3.5)
                {
                    // Move marker: a ring closing in (progress 0 -> 1) with a bright centre.
                    float c = lerp(0.95, 0.3, progress);
                    half ring = Band(r, c, 0.05, aa);
                    half centre = Band(r, 0.0, 0.08, aa);
                    alpha = saturate(ring + centre) * (1.0 - progress * 0.6);
                }
                else
                {
                    // Aircraft: a faint dashed ring on the ground under it, so height reads.
                    half ring = Band(r, 0.9, 0.035, aa) * Dashes(turn + time * 0.15, 12.0, 0.6, aaTurn);
                    half centre = saturate(1.0 - r / 0.45) * 0.18;
                    alpha = saturate(ring * 0.8 + centre);
                }

                alpha *= _Color.a;
                colour = MixFog(colour, input.fog);
                return half4(colour, alpha);
            }
            ENDHLSL
        }
    }
}

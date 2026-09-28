// Flipbook fire and smoke. The sheets (Resources/Textures/Fx) are rendered from Mantaflow fire
// and smoke simulations and channel-packed as linear data:
//   R  heat: how brightly the fire burns there, seen through the smoke in front of it
//   G  light: how lit the smoke is by the sun (0 in shadow, 1 facing it)
//   A  smoke coverage
// Fire is coloured here from heat with a blackbody-like ramp (deep red, orange, yellow-white),
// so one sheet serves a wreck fire, napalm or a thermobaric blast; smoke takes the particle's
// colour, shaded by the baked light. Output is premultiplied alpha (Blend One OneMinusSrcAlpha):
// smoke occludes what is behind it and fire adds light, in one draw. Frames are blended
// (UV2 + AnimBlend streams), so few frames still play smoothly on long-lived puffs.
Shader "MachineBrigade/Flipbook"
{
    Properties
    {
        _MainTex ("Sheet (R heat, G light, A coverage)", 2D) = "black" {}
        _FireDeep ("Fire: cool edge", Color) = (0.55, 0.06, 0.01, 1)
        _FireMid ("Fire: body", Color) = (1, 0.36, 0.05, 1)
        _FireHot ("Fire: hottest core", Color) = (1, 0.86, 0.55, 1)
        _FireIntensity ("Fire intensity (HDR)", Float) = 3
        _HeatScale ("Heat scale", Float) = 1
        _HeatCool ("Heat lost over the particle's life", Float) = 0
        _FireOpacity ("How much fire hides what is behind it", Range(0, 1)) = 0.35
        _SmokeShadow ("Smoke brightness in shadow", Float) = 0.35
        _SmokeLight ("Smoke brightness in light", Float) = 1.15
        _Density ("Smoke density", Float) = 1
        _DepthPull ("Depth pull (m towards the camera)", Float) = 0
        _OntoGround ("Onto ground (1: lies on the ground in depth, under vehicles)", Float) = 0
        _GroundFade ("Fade below the ground over (m, 0 off)", Float) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent"
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
            "PreviewType" = "Plane"
        }

        Pass
        {
            Name "Flipbook"
            Tags { "LightMode" = "UniversalForward" }
            Blend One OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing
            #pragma multi_compile_fog
            // Both variants are always built: the materials are made at run time.
            #pragma multi_compile_local _ _FLIPBOOK_BLEND

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "MbClear.hlsl"
            #include "MbDepth.hlsl"

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                half4 _FireDeep;
                half4 _FireMid;
                half4 _FireHot;
                half _FireIntensity;
                half _HeatScale;
                half _HeatCool;
                half _FireOpacity;
                half _SmokeShadow;
                half _SmokeLight;
                half _Density;
                float _DepthPull;
                float _OntoGround;
                float _GroundFade;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                half4 color : COLOR;
                float4 uv : TEXCOORD0;   // xy: this frame, zw: the next frame
                float4 anim : TEXCOORD1; // x: blend to the next frame, y: age 0..1, z: stable random
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half4 color : COLOR;
                float4 uv : TEXCOORD0;
                float4 data : TEXCOORD1; // x: frame blend, y: age, z: height above the ground, w: fog
                float3 positionWS : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                float height = positionWS.y;
                // The camera is orthographic: sliding a vertex towards it changes only its depth,
                // so big puffs near the ground are not sliced by it (see Particle.shader; along the
                // ray to a perspective camera, MbDepth.hlsl). A fire burning on the ground lies on
                // the ground in depth instead, so a vehicle standing in it is drawn over its flames.
                positionWS = _OntoGround > 0.5 ? MbOntoGround(positionWS, 0.2) : MbDepthPull(positionWS, _DepthPull);
                output.positionCS = TransformWorldToHClip(positionWS);
                output.color = input.color;
                output.uv = float4(TRANSFORM_TEX(input.uv.xy, _MainTex), TRANSFORM_TEX(input.uv.zw, _MainTex));
                // URP's clip-space fog assumes a perspective camera; use view depth (OrthoFog).
                float fog = ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
                output.data = float4(input.anim.x, input.anim.y, height, fog);
                output.positionWS = positionWS;
                return output;
            }

            half3 FireRamp(half heat)
            {
                half3 c = lerp(_FireDeep.rgb, _FireMid.rgb, saturate(heat * 1.8h));
                c = lerp(c, _FireHot.rgb, saturate(heat * 3.3h - 2.3h));
                // Brightness climbs steeply with heat: dim red licks, orange body, a blinding core.
                return c * (heat * (0.3h + heat * 1.2h));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 s = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv.xy);
                #if defined(_FLIPBOOK_BLEND)
                half4 next = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv.zw);
                s = lerp(s, next, (half)input.data.x);
                #endif
                half fade = input.color.a;
                if (_GroundFade > 0.0) fade *= (half)saturate(input.data.z / _GroundFade + 0.5);

                half heat = saturate(s.r * _HeatScale - (half)input.data.y * _HeatCool);
                half coverage = saturate(s.a * _Density) * fade;
                half3 smoke = input.color.rgb * lerp(_SmokeShadow, _SmokeLight, s.g);
                half3 fire = FireRamp(heat) * (_FireIntensity * fade);

                half fogFactor = (half)input.data.w;
                smoke = MixFog(smoke, fogFactor);
                fire = MixFogColor(fire, half3(0, 0, 0), fogFactor);

                half alpha = saturate(coverage + heat * _FireOpacity * fade);
                // Premultiplied: thinning the whole puff over a boss keeps its colours.
                return half4(smoke * coverage + fire, alpha) * MbClearFade(input.positionWS, 0.25h);
            }
            ENDHLSL
        }
    }
}

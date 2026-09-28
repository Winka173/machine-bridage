// A laser beam on a camera-facing line (LineRenderer, alignment View, texture mode Tile). The
// cross-section comes from the line's V: bright along the centre, falling off to the edges by
// _Softness. Energy ripples run along it from the emitter (uv.x is metres along the line),
// scrolled by time. Additive and HDR, so the bloom makes it glow; its alpha is the line's colour
// alpha, which LaserBeams flickers and fades every frame.
Shader "MachineBrigade/Beam"
{
    Properties
    {
        _Intensity ("Intensity (HDR)", Float) = 4
        _Softness ("Edge falloff power", Float) = 1.5
        _Ripple ("Energy ripple along the beam (0 to 1)", Float) = 0.3
        _RippleScale ("Ripples per metre", Float) = 0.35
        _RippleSpeed ("Ripple speed (m/s)", Float) = 60
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent+10"
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
            "PreviewType" = "Plane"
        }

        Pass
        {
            Name "Beam"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha One
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "MbClear.hlsl"
            #include "MbDepth.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half _Intensity;
                half _Softness;
                half _Ripple;
                float _RippleScale;
                float _RippleSpeed;
            CBUFFER_END

            TEXTURE2D(_MbNoise);
            SAMPLER(sampler_MbNoise);

            struct Attributes
            {
                float4 positionOS : POSITION;
                half4 color : COLOR;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half4 color : COLOR;
                float2 uv : TEXCOORD0;
                float fog : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                // Pulled towards the camera (orthographic: only its depth changes), so the beam is
                // never cut by the hull or the ground it burns into (along the ray to a perspective
                // camera, so it stays on its muzzle there too: MbDepth.hlsl).
                positionWS = MbDepthPull(positionWS, 3.0);
                output.positionCS = TransformWorldToHClip(positionWS);
                output.fog = ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
                output.positionWS = positionWS;
                output.color = input.color;
                output.uv = input.uv;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half across = abs(input.uv.y * 2.0 - 1.0);
                half profile = pow(saturate(1.0 - across), max(_Softness, 0.05h));
                float2 p = float2(input.uv.x * _RippleScale - _Time.y * _RippleSpeed * _RippleScale, input.uv.y * 0.3 + 0.37);
                half n = SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, p).r;
                half ripple = 1.0h + (n - 0.5h) * 2.0h * _Ripple;
                half3 colour = input.color.rgb * _Intensity * ripple;
                colour = MixFogColor(colour, half3(0, 0, 0), input.fog);
                // Over a boss the beam keeps half its glow, like the other additive light.
                colour *= MbClearFade(input.positionWS, 0.5h);
                return half4(colour, saturate(input.color.a * profile));
            }
            ENDHLSL
        }
    }
}

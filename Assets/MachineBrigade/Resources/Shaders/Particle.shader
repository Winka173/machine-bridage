// Texture-free particle shader. The shape is computed from UVs: a soft dot, a thin ring for
// shockwaves, a solid square, a noise-eroded fireball puff, or a lit billowing smoke puff. Blend
// factors come from material properties, so one shader serves additive fire and alpha-blended
// smoke. Fire and smoke read the particle's age and a stable random value from TEXCOORD0.zw
// (custom vertex streams set by ParticleBuilder), so every puff has its own shape and it
// evolves over its life.
Shader "MachineBrigade/Particle"
{
    Properties
    {
        _Intensity ("Intensity", Float) = 1
        _Shape ("Shape (0 dot, 1 ring, 2 square, 3 flame, 4 billow)", Float) = 0
        _Softness ("Softness", Float) = 1
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Source Blend", Float) = 5
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Destination Blend", Float) = 1
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
            Name "Particle"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half _Intensity;
                half _Shape;
                half _Softness;
                half _SrcBlend;
                half _DstBlend;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                half4 color : COLOR;
                float4 uv : TEXCOORD0; // xy: quad UV, z: age 0..1, w: stable random 0..1
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half4 color : COLOR;
                float4 uv : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.color = input.color;
                output.uv = input.uv;
                return output;
            }

            float Hash(float2 p)
            {
                p = frac(p * float2(123.34, 456.21));
                p += dot(p, p + 45.32);
                return frac(p.x * p.y);
            }

            float ValueNoise(float2 p)
            {
                float2 i = floor(p);
                float2 f = frac(p);
                float2 u = f * f * (3.0 - 2.0 * f);
                float a = Hash(i);
                float b = Hash(i + float2(1, 0));
                float c = Hash(i + float2(0, 1));
                float d = Hash(i + float2(1, 1));
                return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
            }

            float Fbm(float2 p)
            {
                float sum = 0.0;
                float amplitude = 0.5;
                for (int i = 0; i < 3; i++)
                {
                    sum += ValueNoise(p) * amplitude;
                    p = p * 2.03 + 17.1;
                    amplitude *= 0.5;
                }
                return sum / 0.875;
            }

            half4 Flame(Varyings input)
            {
                float2 p = input.uv.xy * 2.0 - 1.0;
                float r = length(p);
                float age = input.uv.z;
                float seed = input.uv.w * 37.0;
                // The noise scrolls upwards over the puff's life and tears it into tongues.
                float n = Fbm(p * 1.7 + float2(seed, seed * 1.3) - float2(0.0, age * 1.8));
                float edge = r + (n - 0.5) * 1.0;
                float threshold = lerp(0.98, 0.42, age);
                half mask = saturate((threshold - edge) * 4.5);
                // Hot core where the fire is dense and young; cooler, redder edges.
                half heat = saturate((1.0 - r) * 1.3 + (n - 0.5) * 0.8) * (1.0 - age * 0.7);
                half3 colour = input.color.rgb * (0.6 + heat * 0.9);
                colour = lerp(colour, half3(1.0, 0.9, 0.7) * 1.25, heat * heat * heat * 0.45);
                return half4(colour * _Intensity, input.color.a * mask);
            }

            half4 Billow(Varyings input)
            {
                float2 p = input.uv.xy * 2.0 - 1.0;
                float r = length(p);
                float age = input.uv.z;
                float seed = input.uv.w * 29.0;
                float n = Fbm(p * 1.5 + float2(seed * 0.7, seed) + float2(age * 0.4, -age * 0.7));
                float edge = r + (n - 0.5) * 0.8;
                half mask = saturate((0.92 - edge) * 2.6);
                // Light the puff as a lumpy sphere: sun from its direction in view space.
                float3 normal = normalize(float3(p + (n - 0.5) * 0.6, sqrt(saturate(1.0 - r * r)) + 0.35));
                float3 sun = normalize(mul((float3x3)UNITY_MATRIX_V, _MainLightPosition.xyz));
                half lit = saturate(dot(normal, sun) * 0.5 + 0.5);
                half3 colour = input.color.rgb * (0.55 + lit * 0.75 + (n - 0.5) * 0.25);
                return half4(colour * _Intensity, input.color.a * mask);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                if (_Shape > 3.5h) return Billow(input);
                if (_Shape > 2.5h) return Flame(input);

                float r = length(input.uv.xy * 2.0 - 1.0);
                half mask;
                if (_Shape < 0.5h)
                {
                    mask = pow(saturate(1.0 - r), max(_Softness, 0.05h));
                }
                else if (_Shape < 1.5h)
                {
                    mask = saturate(1.0 - abs(r - 0.82) * 7.0) * step(r, 1.0);
                }
                else
                {
                    mask = 1.0h;
                }
                half4 color = input.color;
                color.rgb *= _Intensity;
                color.a *= mask;
                return color;
            }
            ENDHLSL
        }
    }
}

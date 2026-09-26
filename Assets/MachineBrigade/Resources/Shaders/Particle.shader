// Texture-free particle shader. The shape is computed from UVs: a soft dot for fire and
// smoke, a thin ring for shockwaves, or a solid square. Blend factors come from material
// properties, so one shader serves additive fire and alpha-blended smoke.
Shader "MachineBrigade/Particle"
{
    Properties
    {
        _Intensity ("Intensity", Float) = 1
        _Shape ("Shape (0 dot, 1 ring, 2 square)", Float) = 0
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
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half4 color : COLOR;
                float2 uv : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.color = input.color;
                output.uv = input.uv;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float r = length(input.uv * 2.0 - 1.0);
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

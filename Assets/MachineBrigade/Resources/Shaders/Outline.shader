// A bright rim round a mesh (prompt 9: the boss part the player has ordered fire at): the mesh drawn
// again from behind, pushed out along its normals, in a flat HDR colour that glows through bloom.
Shader "MachineBrigade/Outline"
{
    Properties
    {
        [HDR] _Color ("Color", Color) = (2.6, 1.9, 0.45, 1)
        _Width ("Width", Float) = 0.1
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry+10" }

        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "UniversalForward" }
            Cull Front
            ZWrite On

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                float _Width;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                float3 grown = input.positionOS.xyz + normalize(input.normalOS) * _Width;
                output.positionCS = TransformObjectToHClip(grown);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                return _Color;
            }
            ENDHLSL
        }
    }
}

// Far-away vehicles as camera-facing cards cut from the impostor atlas (ImpostorAtlas). Each card
// blends the two baked headings either side of the vehicle's own and is lit like the models (sun,
// shadows, explosion lights, ambient, fog) from the baked albedo and view-space normals, so night,
// storms and blasts light it as they light the rest of the army. The card is pushed towards the
// camera by the vehicle's size, so the ground it stands on never cuts into it (an orthographic
// view does not move it on screen). Drawn instanced: one draw per atlas sheet.
Shader "MachineBrigade/Impostor"
{
    Properties
    {
        _Albedo ("Albedo and Coverage", 2D) = "black" {}
        _Surface ("Normal, Metallic, Glow", 2D) = "black" {}
    }

    SubShader
    {
        Tags { "RenderType" = "TransparentCutout" "RenderPipeline" = "UniversalPipeline" "Queue" = "AlphaTest" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            ZWrite On
            // With MSAA the coverage smooths the card's outline as the meshes' edges are smoothed.
            AlphaToMask On

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_Albedo);
            SAMPLER(sampler_Albedo);
            TEXTURE2D(_Surface);
            SAMPLER(sampler_Surface);

            // The rotation the atlas was baked with (camera to world), for the baked normals.
            float4x4 _MbImpostorViewToWorld;

            UNITY_INSTANCING_BUFFER_START(Props)
                // UV corners of the two headings' cells.
                UNITY_DEFINE_INSTANCED_PROP(float4, _ImpCells)
                // x: blend towards the second heading, y: cell size in UV, z: push towards the camera (m).
                UNITY_DEFINE_INSTANCED_PROP(float4, _ImpShape)
                // rgb: scorch and debug tint, a: 1 - hit flash.
                UNITY_DEFINE_INSTANCED_PROP(float4, _ImpTint)
            UNITY_INSTANCING_BUFFER_END(Props)

            static const half MaxReflected = 1.6h;

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float4 uv : TEXCOORD1;
                half4 fogAndVertexLight : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            // URP's own UniversalFragmentPBR takes the sun's strength and the lights in reach from
            // per-renderer data that instanced draws do not get (the sun came out black), so the
            // card is lit here: the sun with its shadow, every visible light, ambient and reflections.
            half3 Shade(InputData inputData, SurfaceData data)
            {
                BRDFData brdf;
                half alpha = 1.0h;
                InitializeBRDFData(data.albedo, data.metallic, half3(0.0h, 0.0h, 0.0h), data.smoothness, alpha, brdf);
                half3 color = GlobalIllumination(brdf, inputData.bakedGI, data.occlusion, inputData.positionWS, inputData.normalWS, inputData.viewDirectionWS);
                Light sun = GetMainLight(inputData.shadowCoord, inputData.positionWS, inputData.shadowMask);
                sun.distanceAttenuation = 1.0h;
                color += LightingPhysicallyBased(brdf, sun, inputData.normalWS, inputData.viewDirectionWS);
            #if defined(_ADDITIONAL_LIGHTS) || defined(_ADDITIONAL_LIGHTS_VERTEX)
                uint lights = (uint)_AdditionalLightsCount.x;
                for (uint i = 0u; i < lights; i++)
                {
                    Light light = GetAdditionalPerObjectLight((int)i, inputData.positionWS);
                    color += LightingPhysicallyBased(brdf, light, inputData.normalWS, inputData.viewDirectionWS);
                }
            #endif
                return color;
            }

            float OrthoFog(float3 positionWS)
            {
                return ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                float4 cells = UNITY_ACCESS_INSTANCED_PROP(Props, _ImpCells);
                float4 shape = UNITY_ACCESS_INSTANCED_PROP(Props, _ImpShape);
                float3 centre = TransformObjectToWorld(float3(0.0, 0.0, 0.0));
                float size = length(UNITY_MATRIX_M._m00_m10_m20);
                // A card in the camera's plane through the vehicle's middle.
                float3 right = UNITY_MATRIX_V[0].xyz;
                float3 up = UNITY_MATRIX_V[1].xyz;
                float3 positionWS = centre + (right * input.positionOS.x + up * input.positionOS.y) * size;
                float3 positionVS = TransformWorldToView(positionWS);
                positionVS.z += shape.z;
                output.positionCS = TransformWViewToHClip(positionVS);
                output.positionWS = positionWS;
                float2 inCell = (input.positionOS.xy + 0.5) * shape.y;
                output.uv = float4(cells.xy + inCell, cells.zw + inCell);
                output.fogAndVertexLight = half4(OrthoFog(positionWS), 0.0h, 0.0h, 0.0h);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float4 shape = UNITY_ACCESS_INSTANCED_PROP(Props, _ImpShape);
                half4 tint = (half4)UNITY_ACCESS_INSTANCED_PROP(Props, _ImpTint);
                half4 albedo = lerp(SAMPLE_TEXTURE2D(_Albedo, sampler_Albedo, input.uv.xy), SAMPLE_TEXTURE2D(_Albedo, sampler_Albedo, input.uv.zw), (half)shape.x);
                half4 surface = lerp(SAMPLE_TEXTURE2D(_Surface, sampler_Surface, input.uv.xy), SAMPLE_TEXTURE2D(_Surface, sampler_Surface, input.uv.zw), (half)shape.x);
                clip(albedo.a - 0.1h);
                // Coverage sharpened to a pixel-wide ramp round 0.5 (alpha to coverage).
                half edge = saturate((albedo.a - 0.5h) / max(fwidth(albedo.a), 0.0001h) + 0.5h);
                // Stored premultiplied by coverage (so the mip chain does not darken the edges).
                half inverse = 1.0h / max(albedo.a, 0.01h);
                albedo.rgb *= inverse;
                surface *= inverse;
                half2 xy = surface.xy * 2.0h - 1.0h;
                half3 normalVS = half3(xy, sqrt(saturate(1.0h - dot(xy, xy))));
                half3 normalWS = normalize(mul((float3x3)_MbImpostorViewToWorld, (float3)normalVS));

                InputData inputData = (InputData)0;
                inputData.positionWS = input.positionWS;
                inputData.positionCS = input.positionCS;
                inputData.normalWS = normalWS;
                inputData.viewDirectionWS = -GetViewForwardDir();
                inputData.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                inputData.fogCoord = input.fogAndVertexLight.x;
                inputData.vertexLighting = input.fogAndVertexLight.yzw;
                inputData.bakedGI = SampleSH(normalWS);
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                inputData.shadowMask = half4(1, 1, 1, 1);

                SurfaceData data = (SurfaceData)0;
                data.albedo = albedo.rgb * tint.rgb;
                data.metallic = surface.z;
                data.smoothness = 0.5h;
                data.occlusion = 0.95h;
                data.alpha = 1.0h;
                data.normalTS = half3(0, 0, 1);

                half3 color = Shade(inputData, data);
                color = min(color, MaxReflected) + data.albedo * surface.w * 16.0h;
                color = lerp(color, half3(1.25h, 1.2h, 1.1h), (1.0h - tint.a) * 0.3h);
                color = MixFog(color, inputData.fogCoord);
                return half4(color, edge);
            }
            ENDHLSL
        }
    }
}

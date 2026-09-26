// PBR shader for the Blender models. The models carry baked grey lighting (ambient occlusion,
// worn edges, ground grime) in their vertex colours; it multiplies the material colour, exactly
// as in the 3d_astra renderer. Lighting goes through URP's own UniversalFragmentPBR, so the sun,
// its shadows, explosion point lights, ambient and reflections all behave like URP Lit.
// _BaseMap textures the ground (white elsewhere); _Tint darkens wrecks; _Wind sways foliage.
Shader "MachineBrigade/Lit"
{
    Properties
    {
        _BaseColor ("Base Colour", Color) = (1, 1, 1, 1)
        _BaseMap ("Base Map", 2D) = "white" {}
        _Metallic ("Metallic", Range(0, 1)) = 0
        _Roughness ("Roughness", Range(0, 1)) = 0.8
        [HDR] _EmissionColor ("Emission", Color) = (0, 0, 0, 1)
        _Tint ("Tint", Color) = (1, 1, 1, 1)
        _Wind ("Wind Sway", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        TEXTURE2D(_BaseMap);
        SAMPLER(sampler_BaseMap);

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _Metallic;
            half _Roughness;
            half4 _EmissionColor;
            half4 _Tint;
            half _Wind;
        CBUFFER_END

        // Foliage sway: displacement grows with height above the ground. The phase comes from the
        // world position, so merged forests do not sway in lockstep.
        float3 ApplyWind(float3 positionOS)
        {
            if (_Wind <= 0.0) return positionOS;
            float3 world = TransformObjectToWorld(positionOS);
            float phase = _Time.y * 1.7 + world.x * 0.09 + world.z * 0.07;
            float sway = sin(phase) * 0.6 + sin(phase * 2.3) * 0.25;
            float weight = saturate(positionOS.y * 0.25) * positionOS.y * 0.04 * _Wind;
            positionOS.x += sway * weight;
            positionOS.z += cos(phase * 0.8) * weight * 0.6;
            return positionOS;
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            static const half MaxReflected = 1.6h;

            // Specular anti-aliasing (Kaplanyan and Hoffman 2016): where the normal changes quickly
            // across a pixel, widen the highlight so it cannot alias into single-pixel sparkles.
            half SpecularAntiAliasedRoughness(half perceptualRoughness, float3 normalWS)
            {
                float3 du = ddx(normalWS);
                float3 dv = ddy(normalWS);
                float variance = 0.25 * (dot(du, du) + dot(dv, dv));
                float kernel = min(2.0 * variance, 0.2);
                float roughness = perceptualRoughness * perceptualRoughness;
                return (half)sqrt(sqrt(saturate(roughness * roughness + kernel)));
            }

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half4 color : COLOR;
                half4 fogAndVertexLight : TEXCOORD2;
                float2 uv : TEXCOORD3;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            // Fog from view depth. URP's clip-space fog assumes a perspective camera; with this
            // orthographic one it gave no fog at all on OpenGL ES.
            float OrthoFog(float3 positionWS)
            {
                return ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                VertexPositionInputs position = GetVertexPositionInputs(ApplyWind(input.positionOS.xyz));
                output.positionCS = position.positionCS;
                output.positionWS = position.positionWS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.color = input.color;
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                half3 vertexLight = VertexLighting(position.positionWS, output.normalWS);
                output.fogAndVertexLight = half4(OrthoFog(position.positionWS), vertexLight);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 normalWS = NormalizeNormalPerPixel(input.normalWS);

                InputData inputData = (InputData)0;
                inputData.positionWS = input.positionWS;
                inputData.positionCS = input.positionCS;
                inputData.normalWS = normalWS;
                inputData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
                inputData.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                inputData.fogCoord = input.fogAndVertexLight.x;
                inputData.vertexLighting = input.fogAndVertexLight.yzw;
                inputData.bakedGI = SampleSH(normalWS);
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                inputData.shadowMask = half4(1, 1, 1, 1);

                // Baked vertex lighting is grey; its level also dims ambient light in crevices.
                half bakedAo = saturate(dot(input.color.rgb, half3(0.333, 0.333, 0.334)) * 1.25);

                SurfaceData surface = (SurfaceData)0;
                half3 map = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb;
                surface.albedo = _BaseColor.rgb * map * input.color.rgb * _Tint.rgb;
                surface.metallic = _Metallic;
                surface.smoothness = 1.0h - SpecularAntiAliasedRoughness(_Roughness, input.normalWS);
                surface.occlusion = lerp(0.55h, 1.0h, bakedAo);
                surface.alpha = 1.0h;
                surface.normalTS = half3(0, 0, 1);

                // Sun glints on thin, glossy parts (barrels, periscopes) cover a pixel one frame and
                // miss it the next; with HDR values in the tens, bloom blew each one up into a flash
                // over the whole vehicle. Reflected light is capped; emission (lamps, tracers) is
                // added afterwards so it still blooms.
                half4 color = UniversalFragmentPBR(inputData, surface);
                color.rgb = min(color.rgb, MaxReflected) + _EmissionColor.rgb * _Tint.rgb;
                color.rgb = MixFog(color.rgb, inputData.fogCoord);
                return half4(color.rgb, 1.0h);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0

            HLSLPROGRAM
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 ShadowVert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = TransformObjectToWorld(ApplyWind(input.positionOS.xyz));
                float3 normalWS = TransformObjectToWorldNormal(input.normalOS);
            #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 lightDirection = normalize(_LightPosition - positionWS);
            #else
                float3 lightDirection = _LightDirection;
            #endif
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirection));
            #if UNITY_REVERSED_Z
                positionCS.z = min(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #else
                positionCS.z = max(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #endif
                return positionCS;
            }

            half4 ShadowFrag() : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 DepthVert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return TransformObjectToHClip(ApplyWind(input.positionOS.xyz));
            }

            half DepthFrag() : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On

            HLSLPROGRAM
            #pragma vertex NormalsVert
            #pragma fragment NormalsFrag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half3 normalWS : TEXCOORD0;
            };

            Varyings NormalsVert(Attributes input)
            {
                Varyings output;
                UNITY_SETUP_INSTANCE_ID(input);
                output.positionCS = TransformObjectToHClip(ApplyWind(input.positionOS.xyz));
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 NormalsFrag(Varyings input) : SV_Target
            {
                return half4(NormalizeNormalPerPixel(input.normalWS), 0.0h);
            }
            ENDHLSL
        }
    }
}

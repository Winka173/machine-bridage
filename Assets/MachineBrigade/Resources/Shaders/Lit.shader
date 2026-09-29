// PBR shader for the Blender models. The models carry baked grey lighting (ambient occlusion,
// worn edges, ground grime) in their vertex colours; it multiplies the material colour, exactly
// as in the 3d_astra renderer. Lighting goes through URP's own UniversalFragmentPBR, so the sun,
// its shadows, explosion point lights, ambient and reflections all behave like URP Lit.
// _BaseMap textures the ground (white elsewhere); _Tint darkens wrecks, and its alpha below 1
// flashes a vehicle white as it is hit; _Wind sways foliage.
// _VertexSurface marks a vehicle's far detail level (see MaterialLibrary.Lod): one material for
// the whole part, each vertex naming its kit surface by a palette column in its first UV.
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
        _CamoMode ("Camo (0 plain, 1 blotches, 2 stripes, 3 digital)", Float) = 0
        _CamoColorB ("Camo Second", Color) = (0.3, 0.3, 0.3, 1)
        _CamoColorC ("Camo Third", Color) = (0.6, 0.6, 0.6, 1)
        _CamoScale ("Camo Scale", Float) = 0.35
        _VertexSurface ("Vertex Surface (far detail)", Float) = 0
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
            half _CamoMode;
            half4 _CamoColorB;
            half4 _CamoColorC;
            half _CamoScale;
            half _VertexSurface;
        CBUFFER_END

        // Army skins: a pattern computed from the object-space position (the models' UVs are not
        // laid out for painting), projected at a slant so side and top faces both get it. Only
        // the Team materials set a mode; everything else takes the first branch.
        TEXTURE2D(_MbNoise);
        SAMPLER(sampler_MbNoise);

        half3 Camo(float3 p, half3 baseColour)
        {
            if (_CamoMode < 0.5) return baseColour;
            float2 q = (p.xz + p.yy * float2(0.7, 0.45)) * _CamoScale;
            if (_CamoMode < 1.5)
            {
                float a = SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, q * 0.125).r;
                float b = SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, q * 0.22 + 0.37).r;
                half3 c = lerp(baseColour, _CamoColorB.rgb, step(0.56, a));
                return lerp(c, _CamoColorC.rgb, step(0.63, b));
            }
            if (_CamoMode < 2.5)
            {
                float n = SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, q * 0.09).r;
                float stripe = sin((q.x * 1.25 + q.y * 0.4) * 3.2 + n * 7.0);
                return lerp(baseColour, _CamoColorB.rgb, step(0.45, stripe));
            }
            float2 cell = floor(q * 2.2);
            float h = frac(sin(dot(cell, float2(12.9898, 78.233))) * 43758.5453);
            float m = SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, cell * 0.061).r;
            half3 d = lerp(baseColour, _CamoColorB.rgb, step(0.52, m + h * 0.18));
            return lerp(d, _CamoColorC.rgb, step(0.86, h));
        }

        // The far detail level's surfaces (MaterialLibrary.Palette): row 0 holds base colour and
        // metallic, row 1 emission and roughness. A metallic of -1 is the army's paint (the
        // material's colour, camouflage and finish), -2 its glow.
        TEXTURE2D(_MbPalette);
        SAMPLER(sampler_MbPalette);

        void VertexSurface(float column, float3 positionOS, out half3 paint, out half metallic, out half roughness, out half3 emission)
        {
            half4 a = SAMPLE_TEXTURE2D_LOD(_MbPalette, sampler_MbPalette, float2(column, 0.25), 0);
            half4 b = SAMPLE_TEXTURE2D_LOD(_MbPalette, sampler_MbPalette, float2(column, 0.75), 0);
            paint = a.rgb;
            metallic = a.a;
            roughness = b.a;
            emission = b.rgb;
            if (a.a < -1.5h)
            {
                paint = _BaseColor.rgb;
                metallic = 0.0h;
                emission = _EmissionColor.rgb;
            }
            else if (a.a < -0.5h)
            {
                paint = Camo(positionOS, _BaseColor.rgb);
                metallic = _Metallic;
                roughness = _Roughness;
                emission = half3(0.0h, 0.0h, 0.0h);
            }
        }

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
            // Play-test 8 (DECISIONS 22R): burning vehicles light their hull and the ground round them (HeatLights):
            // up to four warm glows, xyz the fire and w 1 / reach^2, with a soft fall-off and a wrapped facing term, no
            // shadows. The count is 0 when nothing burns (and unset: menus), so the loop costs nothing then.
            float4 _MbHeat[4];
            half4 _MbHeatColour[4];
            float _MbHeatCount;
            // The fires' light on a surface (to multiply its albedo) and, close in, the metal's own glow.
            void HeatLight(float3 positionWS, half3 normalWS, out half3 light, out half3 glow)
            {
                light = half3(0.0h, 0.0h, 0.0h);
                glow = half3(0.0h, 0.0h, 0.0h);
                for (int i = 0; i < 4; i++)
                {
                    if ((float)i >= _MbHeatCount) break;
                    float3 d = _MbHeat[i].xyz - positionWS;
                    float d2 = dot(d, d);
                    half q = (half)saturate(1.0 - d2 * _MbHeat[i].w);
                    half q2 = q * q;
                    half facing = saturate(dot(normalWS, (half3)(d * rsqrt(max(d2, 1e-4)))) * 0.6h + 0.4h);
                    light += _MbHeatColour[i].rgb * (q2 * facing);
                    glow += _MbHeatColour[i].rgb * (q2 * q2);
                }
            }

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
                float3 positionOS : TEXCOORD4;
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
                output.positionOS = input.positionOS.xyz;
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

                half3 paint;
                half metallic = _Metallic;
                half roughness = _Roughness;
                half3 emission = _EmissionColor.rgb;
                UNITY_BRANCH
                if (_VertexSurface > 0.5h)
                    VertexSurface(input.uv.x, input.positionOS, paint, metallic, roughness, emission);
                else
                    paint = Camo(input.positionOS, _BaseColor.rgb) * SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv).rgb;

                SurfaceData surface = (SurfaceData)0;
                surface.albedo = paint * input.color.rgb * _Tint.rgb;
                surface.metallic = metallic;
                surface.smoothness = 1.0h - SpecularAntiAliasedRoughness(roughness, input.normalWS);
                surface.occlusion = lerp(0.55h, 1.0h, bakedAo);
                surface.alpha = 1.0h;
                surface.normalTS = half3(0, 0, 1);

                // Sun glints on thin, glossy parts (barrels, periscopes) cover a pixel one frame and
                // miss it the next; with HDR values in the tens, bloom blew each one up into a flash
                // over the whole vehicle. Reflected light is capped; emission (lamps, tracers) is
                // added afterwards so it still blooms.
                half4 color = UniversalFragmentPBR(inputData, surface);
                color.rgb = min(color.rgb, MaxReflected) + emission * _Tint.rgb;
                half3 heat, heatGlow;
                HeatLight(input.positionWS, normalWS, heat, heatGlow);
                color.rgb += heat * surface.albedo + heatGlow * 0.08h;
                // Hit flash: a brief white-hot wash (1 - _Tint.a; 0 unless a view is flashing).
                color.rgb = lerp(color.rgb, half3(1.25h, 1.2h, 1.1h), (1.0h - _Tint.a) * 0.3h);
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

        // Draws a far-detail part into the impostor atlas (ImpostorAtlas): albedo and coverage to
        // the first target; the view-space normal, metallic and glow to the second. Never drawn by
        // the pipeline itself (its light mode is ours).
        Pass
        {
            Name "ImpostorBake"
            Tags { "LightMode" = "MbImpostorBake" }
            ZWrite On
            ZTest LEqual
            Cull Back

            HLSLPROGRAM
            #pragma vertex BakeVert
            #pragma fragment BakeFrag

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half3 normalVS : TEXCOORD0;
                half4 color : COLOR;
                float2 uv : TEXCOORD1;
                float3 positionOS : TEXCOORD2;
            };

            struct Targets
            {
                half4 albedo : SV_Target0;
                half4 surface : SV_Target1;
            };

            Varyings BakeVert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.normalVS = TransformWorldToViewDir(TransformObjectToWorldNormal(input.normalOS));
                output.color = input.color;
                output.uv = input.uv;
                output.positionOS = input.positionOS.xyz;
                return output;
            }

            Targets BakeFrag(Varyings input)
            {
                half3 paint;
                half metallic;
                half roughness;
                half3 emission;
                VertexSurface(input.uv.x, input.positionOS, paint, metallic, roughness, emission);
                half3 albedo = paint * input.color.rgb;
                half3 n = normalize(input.normalVS);
                // Glow as a multiple of the albedo's brightness (the impostor tints it with the albedo).
                half glow = saturate(dot(emission, half3(0.3h, 0.59h, 0.11h)) / max(dot(albedo, half3(0.3h, 0.59h, 0.11h)), 0.02h) / 16.0h);
                Targets output;
                output.albedo = half4(albedo, 1.0h);
                output.surface = half4(n.xy * 0.5h + 0.5h, saturate(metallic), glow);
                return output;
            }
            ENDHLSL
        }
    }
}

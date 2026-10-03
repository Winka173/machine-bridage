// Play-test 13 ("biển nhìn không thực xíu nào"): the sea, rivers and floods. Opaque and texture-light for phones: no
// depth or opaque texture, no screen-space effect; the shore comes from the meshes' data instead.
//   Depth colour: shallow (turquoise, sand showing through) at the shore to deep (the theme's water colour) offshore.
//   Waves: three long swells (analytic slopes) and two scrolling ripple layers (the shared _MbNoise texture) bend the
//          normal, so the sun's highlight breaks into a glitter path and the sky reflection moves.
//   Light: the sun's diffuse and a sharp specular with its shadows (ships and units shade the water), the sky's
//          reflection by Fresnel, the night's point lights (blasts, fires) glinting.
//   Foam:  a swash line on the shore and broken foam bands washing in and out inside it; a few whitecaps offshore.
//   Fog:   the battle's linear fog by view depth (the far sea fades into the horizon haze).
// Inputs per vertex (COLOR): r = depth 0 shallow .. 1 deep, g = open water 0 at the shore .. 1 clear of it. A mesh without
// colours reads white: deep, open sea. With _UseShoreTex the shore distance comes from _ShoreTex instead (the edge sea
// beyond the map: R = 0 on the coast .. 1 at 32 m out), laid over the world rectangle _ShoreRect (x, z min; 1 / size).
// _BaseColor and _Roughness keep the old Lit water's names (the themes and maps set them).
Shader "MachineBrigade/Water"
{
    Properties
    {
        _BaseColor ("Deep Colour", Color) = (0.18, 0.43, 0.47, 1)
        _ShallowColor ("Shallow Colour", Color) = (0.36, 0.66, 0.62, 1)
        _FoamColor ("Foam Colour", Color) = (0.95, 0.97, 0.98, 1)
        _Roughness ("Roughness", Range(0.02, 1)) = 0.08
        _WaveStrength ("Wave Strength", Range(0, 2)) = 1
        _WaveScale ("Wave Scale", Range(0.25, 4)) = 1
        _FoamAmount ("Foam Amount", Range(0, 2)) = 1
        _Calm ("Calm (rivers, floods: 1)", Range(0, 1)) = 0
        _ShoreTex ("Shore Distance", 2D) = "white" {}
        _ShoreRect ("Shore Rect (x min, z min, 1/size x, 1/size z)", Vector) = (0, 0, 0, 0)
        _UseShoreTex ("Use Shore Texture", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            half4 _BaseColor;
            half4 _ShallowColor;
            half4 _FoamColor;
            half _Roughness;
            half _WaveStrength;
            half _WaveScale;
            half _FoamAmount;
            half _Calm;
            float4 _ShoreTex_ST;
            float4 _ShoreRect;
            half _UseShoreTex;
        CBUFFER_END
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
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_MbNoise);
            SAMPLER(sampler_MbNoise);
            TEXTURE2D(_ShoreTex);
            SAMPLER(sampler_ShoreTex);

            // As the Lit shader: reflected light is capped so a glint cannot bloom into a flash.
            static const half MaxReflected = 2.2h;

            struct Attributes
            {
                float4 positionOS : POSITION;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half4 color : COLOR;
                half4 fogAndVertexLight : TEXCOORD1;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            // Fog from view depth (the orthographic battle camera; see the Lit shader).
            float OrthoFog(float3 positionWS)
            {
                return ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                VertexPositionInputs position = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = position.positionCS;
                output.positionWS = position.positionWS;
                output.color = input.color;
                half3 vertexLight = VertexLighting(position.positionWS, half3(0.0h, 1.0h, 0.0h));
                output.fogAndVertexLight = half4(OrthoFog(position.positionWS), vertexLight);
                return output;
            }

            float Noise(float2 p)
            {
                return SAMPLE_TEXTURE2D(_MbNoise, sampler_MbNoise, p * 0.125).r;
            }

            // One ripple layer's slope (d height / d x, d height / d z) from three taps of the noise.
            float2 RippleSlope(float2 p, float scale)
            {
                const float e = 0.35;
                float2 q = p * scale;
                float h = Noise(q);
                return float2(Noise(q + float2(e, 0.0)) - h, Noise(q + float2(0.0, e)) - h) * (scale / e);
            }

            // A long swell (deep-water speed): its slope along its direction, and its height in metres (crest tint, caps).
            float2 Swell(float2 p, float2 dir, float wavelength, float amplitude, float t, inout float height)
            {
                float k = 6.2831853 / wavelength;
                float phase = dot(dir, p) * k - t * sqrt(9.8 * k);
                height += sin(phase) * amplitude;
                return dir * (cos(phase) * amplitude * k);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = input.positionWS;
                float2 p = positionWS.xz / _WaveScale;
                float t = _Time.y;

                // Depth and the shore: from the vertex colour, or the edge sea's shore distance texture.
                half depth = input.color.r;
                half open = input.color.g;
                if (_UseShoreTex > 0.5h)
                {
                    float2 uv = (positionWS.xz - _ShoreRect.xy) * _ShoreRect.zw;
                    half inside = (half)(step(0.0, uv.x) * step(uv.x, 1.0) * step(0.0, uv.y) * step(uv.y, 1.0));
                    half shore = SAMPLE_TEXTURE2D(_ShoreTex, sampler_ShoreTex, saturate(uv)).r;
                    shore = lerp(1.0h, shore, inside);
                    open = min(open, saturate(shore * 5.0h));   // the foam's band: the first ~6 m
                    depth = min(depth, saturate(shore * 1.25h)); // shallow to deep over ~25 m
                }
                half calm = _Calm;

                // Waves: three swells (none on calm water) and two ripple layers drifting across each other.
                float height = 0.0;
                float2 slope = 0.0;
                half swell = (1.0h - calm) * _WaveStrength;
                // Play-test 14 ("sóng chạy từ dưới lên, sóng phải theo gió"): every swell and ripple runs downwind, the
                // smoke's wind (ParticleBuilder.Wind, x 0.9 z 0.6, ~34 degrees off +x): the swells within 25 degrees of it
                // (one had run up the screen, +z), both ripple layers drifting with it (the first had drifted against it).
                slope += Swell(p, float2(0.832, 0.555), 23.0, 0.35, t, height) * swell;
                slope += Swell(p, float2(0.520, 0.854), 13.0, 0.2, t * 1.1, height) * swell;
                slope += Swell(p, float2(0.972, 0.237), 7.5, 0.1, t * 1.2, height) * swell;
                float2 drift = float2(0.9, 0.6) * t;
                half ripple = _WaveStrength * lerp(1.0h, 0.45h, calm);
                slope += RippleSlope(p - drift * 0.35, 0.16) * 0.55 * ripple;
                // This layer is read in swapped axes (z, -x): the wind there is (0.6, -0.9).
                slope += RippleSlope(p.yx * float2(1.0, -1.0) - float2(0.6, -0.9) * t * 0.22, 0.37) * 0.32 * ripple;
                // Calmer and flatter in the shallows (the waves break there; the foam takes over).
                slope *= lerp(0.45, 1.0, open);
                half3 normalWS = normalize(half3(-slope.x, 1.0h, -slope.y));

                // Base colour: shallow to deep, a touch greener on the crests (light through the wave).
                half deepness = smoothstep(0.0h, 1.0h, depth);
                half3 water = lerp(_ShallowColor.rgb, _BaseColor.rgb, deepness);
                water += half3(0.02h, 0.05h, 0.04h) * saturate((half)height * 1.2h + 0.4h) * (1.0h - calm);

                InputData inputData = (InputData)0;
                inputData.positionWS = positionWS;
                inputData.positionCS = input.positionCS;
                inputData.normalWS = normalWS;
                inputData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(positionWS);
                inputData.shadowCoord = TransformWorldToShadowCoord(positionWS);
                inputData.fogCoord = input.fogAndVertexLight.x;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                inputData.shadowMask = half4(1, 1, 1, 1);
                half3 viewDir = inputData.viewDirectionWS;

                Light sun = GetMainLight(inputData.shadowCoord, positionWS, inputData.shadowMask);
                half shadow = sun.shadowAttenuation * sun.distanceAttenuation;
                half3 sunLight = sun.color * shadow;
                half ndl = saturate(dot(normalWS, sun.direction));
                half3 ambient = SampleSH(half3(0.0h, 1.0h, 0.0h));

                // Body colour: lit softly (water scatters light from below); shaded where a hull's shadow falls.
                half3 colour = water * (ambient * 0.9h + sunLight * (0.35h + 0.45h * ndl));

                // Sky reflection by Fresnel (Schlick, F0 0.02), lifted a little: from the battle camera's steep angle the
                // real figure is ~2 % and the water read as paint.
                half3 reflected = reflect(-viewDir, normalWS);
                half fresnel = 0.02h + 0.98h * pow(1.0h - saturate(dot(normalWS, viewDir)), 5.0h);
                fresnel = saturate(fresnel * 2.5h + 0.05h) * lerp(1.0h, 0.6h, calm);
                half3 sky = SampleSH(reflected) * 1.15h;
                colour = lerp(colour, sky, fresnel);

                // The sun's highlight: a sharp lobe (normalised Blinn-Phong) and a glitter of sparkles inside a wider one.
                half rough = max(_Roughness, 0.03h);
                half shininess = clamp(2.0h / (rough * rough) - 2.0h, 8.0h, 900.0h);
                half3 halfDir = normalize(sun.direction + viewDir);
                half ndh = saturate(dot(normalWS, halfDir));
                half spec = pow(ndh, shininess) * (shininess + 8.0h) * 0.0398h; // (n + 8) / (8 pi)
                half wide = pow(ndh, shininess * 0.08h + 4.0h);
                float glitterNoise = Noise(positionWS.xz * 1.7 + float2(t * 0.7, -t * 0.4)) * Noise(positionWS.zx * 2.3 - t * 0.5);
                half glitter = (half)smoothstep(0.5, 0.62, glitterNoise) * wide * 6.0h * (1.0h - calm * 0.7h);
                colour += sunLight * (spec * 0.9h + glitter) * fresnel * 4.0h;

                // Night: blasts and fires glint on the water.
            #if defined(_ADDITIONAL_LIGHTS)
                uint lightCount = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(lightCount)
                    Light light = GetAdditionalLight(lightIndex, positionWS, inputData.shadowMask);
                    half3 lightColour = light.color * light.distanceAttenuation;
                    half3 h = normalize(light.direction + viewDir);
                    half s = pow(saturate(dot(normalWS, h)), shininess * 0.5h) * (shininess * 0.5h + 8.0h) * 0.0398h;
                    colour += lightColour * (water * saturate(dot(normalWS, light.direction)) * 0.5h + s * 0.6h);
                LIGHT_LOOP_END
            #elif defined(_ADDITIONAL_LIGHTS_VERTEX)
                colour += water * input.fogAndVertexLight.yzw * 0.5h;
            #endif

                // Foam: a swash line on the shore, foam bands washing in and out inside it, broken by noise; whitecaps offshore.
                half shoreBand = 1.0h - open;
                float wash = sin(open * 14.0 - t * 1.4 + Noise(positionWS.xz * 0.45) * 5.0) * 0.5 + 0.5;
                float breakup = Noise(positionWS.xz * 0.9 + float2(t * 0.15, t * 0.1));
                half swash = (half)smoothstep(0.82, 0.98, shoreBand);
                half bands = (half)(smoothstep(0.55, 0.85, wash) * smoothstep(0.35, 0.65, breakup)) * shoreBand * shoreBand;
                half caps = (half)smoothstep(0.45, 0.6, height) * (half)smoothstep(0.6, 0.75, breakup) * open * (1.0h - calm) * 0.6h;
                half foam = saturate((swash * 0.85h + bands * 0.8h) * lerp(0.5h, 1.0h, 1.0h - calm) + caps) * _FoamAmount;
                half3 foamLit = _FoamColor.rgb * (ambient + sunLight * (0.55h + 0.45h * ndl));
                colour = lerp(colour, foamLit, saturate(foam));

                colour = min(colour, MaxReflected) * input.color.b; // b: a fade into the backdrop (the menu's turntable)
                colour = MixFog(colour, inputData.fogCoord);
                return half4(colour, 1.0h);
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
                return TransformObjectToHClip(input.positionOS.xyz);
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
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 NormalsVert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return TransformObjectToHClip(input.positionOS.xyz);
            }

            half4 NormalsFrag() : SV_Target
            {
                return half4(0.0h, 1.0h, 0.0h, 0.0h);
            }
            ENDHLSL
        }
    }
}

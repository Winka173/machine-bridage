// Every shield in the game (prompt 11C): the fortress's dome over its keep, the Shield Dome item,
// a boss's or an elite's shield skill round the vehicle, a siege objective not yet in play.
//
// An energy skin of hexagonal tiles (ShieldVisual builds the mesh: the dual of a geodesic sphere,
// one fan of triangles per tile, so a tile's vertices all carry its centre and its own random
// value). It is bright only towards its rim (fresnel) and almost clear in the middle, so what
// stands inside stays plain to see. Hits send a ring of lit tiles out from where they land
// (up to four at once), a failing shield flickers (tiles drop out, the whole skin dips), and it
// dies by shattering: it flares, then its tiles break one by one, shrink and fly off.
//
// Additive, no depth writes, both faces (the far side a little dimmer). Everything that varies
// per tile is worked out per vertex (a tile's seven vertices agree), so the fragment only adds
// the fresnel, the lattice lines and the ground band. Time comes from _Now (set by script),
// so editor shots freeze any moment. _SHIELD_LITE (Low graphics) drops the lattice, ripples and
// shimmer: fresnel rim, ground band, flicker, the whole-skin hit flash and the shatter remain.
Shader "MachineBrigade/Shield"
{
    Properties
    {
        _Color ("Side colour", Color) = (0.25, 0.68, 1, 1)
        _Intensity ("Intensity (HDR)", Float) = 2
        _Now ("Clock (s)", Float) = 0
        _Power ("Power (0 off, 1 up)", Float) = 1
        _Flicker ("Flicker (0 steady, 1 failing)", Float) = 0
        _Collapse ("Collapse (0 standing, 1 gone)", Float) = 0
        _Hit ("Hit flash of the whole skin", Float) = 0
        _Cell ("Tile size (m)", Float) = 4
        _Reach ("Ripple reach (m)", Float) = 10
        _Line ("Lattice line (share of a tile's radius)", Float) = 0.1
        _Ground ("Standing on the ground (domes): cut below it, glowing band where it meets it", Float) = 1
        _Ripple0 ("Ripple 0 (xyz object space, w start)", Vector) = (0, 1, 0, -100)
        _Ripple1 ("Ripple 1", Vector) = (0, 1, 0, -100)
        _Ripple2 ("Ripple 2", Vector) = (0, 1, 0, -100)
        _Ripple3 ("Ripple 3", Vector) = (0, 1, 0, -100)
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Transparent"
            "Queue" = "Transparent+5"
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
        }

        Pass
        {
            Name "Shield"
            Tags { "LightMode" = "UniversalForward" }
            // Premultiplied: bright parts also cover a little of what is behind them, so the side's
            // colour reads true over any ground (additive red over green grass turned yellow).
            Blend One OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            // Materials are made at run time, so the Low variant must not be stripped (not shader_feature).
            #pragma multi_compile_local _ _SHIELD_LITE

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half _Intensity;
                float _Now;
                half _Power;
                half _Flicker;
                half _Collapse;
                half _Hit;
                float _Cell;
                float _Reach;
                half _Line;
                half _Ground;
                float4 _Ripple0;
                float4 _Ripple1;
                float4 _Ripple2;
                float4 _Ripple3;
            CBUFFER_END

            // Seconds a ripple runs.
            #define RIPPLE_LIFE 0.8

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 uv : TEXCOORD0;   // x: 0 at the tile's centre, 1 on its edge; y: the tile's random (0-1)
                float3 cell : TEXCOORD1; // the tile's centre in object space (on the unit sphere)
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                half4 tile : TEXCOORD2;  // x: ripple light, y: shimmer, z: how much of the tile stands, w: its flare
                float2 local : TEXCOORD3; // x: 0 centre to 1 edge of the tile, y: metres above the object's base
                float fog : TEXCOORD4;
            };

            // A hash without trigonometry: sin() of big arguments is unreliable on some phone GPUs.
            float Hash11(float p)
            {
                p = frac(p * 0.1031);
                p *= p + 33.33;
                p *= p + p;
                return frac(p);
            }

            // How lit a tile is by one ripple: a flash where the round struck, then a ring of tiles
            // running out from it, fading as it goes.
            float Ripple(float3 tileWS, float4 ripple)
            {
                float age = _Now - ripple.w;
                float live = step(0.0, age) * step(age, RIPPLE_LIFE);
                float t = saturate(age / RIPPLE_LIFE);
                float d = distance(tileWS, TransformObjectToWorld(ripple.xyz));
                float front = _Reach * (1.0 - (1.0 - t) * (1.0 - t));
                float ring = saturate(1.0 - abs(d - front) / (_Cell * 0.65)) * (1.0 - t);
                float spot = saturate(1.0 - d / (_Cell * 1.3)) * saturate(1.0 - age / 0.35) * 1.5;
                return live * (ring * 1.6 + spot);
            }

            Varyings Vert(Attributes input)
            {
                Varyings output;
                float3 position = input.positionOS.xyz;
                float3 centre = input.cell;
                float seed = input.uv.y;

                // The shatter: each tile breaks at its own moment, flares, shrinks to its centre
                // and flies outwards, dropping a little.
                float breakAt = 0.12 + seed * 0.5;
                float broken = saturate((_Collapse - breakAt) / 0.38);
                position = centre + (position - centre) * (1.0 - broken * 0.8);
                position += centre * (broken * (0.05 + seed * 0.12));
                position.y -= broken * broken * 0.06;

                float3 positionWS = TransformObjectToWorld(position);
                output.positionWS = positionWS;
                output.positionCS = TransformWorldToHClip(positionWS);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                // Fog from view depth (the battle camera is orthographic; see Particle.shader).
                output.fog = ComputeFogFactorZ0ToFar(-TransformWorldToView(positionWS).z);

                // Flicker, stepped fifteen times a second: the whole skin dips on some steps,
                // single tiles drop out, a few spark.
                float tick = floor(_Now * 15.0);
                float dip = step(Hash11(tick * 1.37 + 5.1), _Flicker * 0.5);
                float drop = step(Hash11(tick + seed * 173.0), _Flicker * 0.4);
                float spark = step(1.0 - _Flicker * 0.1, Hash11(tick * 0.71 + seed * 91.0));
                float stands = (1.0 - dip * 0.6) * (1.0 - drop * 0.85) * (1.0 - broken);
                // A breaking tile flares as it goes.
                float flare = step(0.001, broken) * (1.0 - broken) * 1.4 + spark;

                float ripple = 0.0;
                float shimmer = 0.0;
            #ifndef _SHIELD_LITE
                float3 tileWS = TransformObjectToWorld(centre);
                ripple = Ripple(tileWS, _Ripple0) + Ripple(tileWS, _Ripple1) + Ripple(tileWS, _Ripple2) + Ripple(tileWS, _Ripple3);
                // Now and then a tile glows softly and fades: the field is alive.
                float wave = saturate(sin(_Now * 0.9 + seed * 57.0));
                shimmer = wave * wave * wave * wave;
                shimmer *= shimmer * shimmer * 0.9;
            #endif
                output.tile = half4(ripple, shimmer, stands, flare);
                // Metres above the shield's base (where a dome stands on the ground), before the shatter moved it.
                float rest = TransformObjectToWorld(input.positionOS.xyz).y - GetObjectToWorldMatrix()._m13;
                output.local = float2(input.uv.x, rest);
                return output;
            }

            half4 Frag(Varyings input, FRONT_FACE_TYPE face : FRONT_FACE_SEMANTIC) : SV_Target
            {
                float3 normal = normalize(input.normalWS);
                float3 view = GetWorldSpaceNormalizeViewDir(input.positionWS);
                half fresnel = 1.0h - (half)saturate(abs(dot(normal, view)));
                half soft = fresnel * fresnel;
                half rim = soft * soft;
                rim *= rim;
                // The far side, seen through the near one, dimmer.
                half side = IS_FRONT_VFACE(face, 1.0h, 0.5h);

                // Nearly nothing where it faces the camera, bright where it curves away.
                half glow = 0.006h + soft * 0.06h + rim * 0.9h;
                glow += _Hit * (0.04h + soft * 0.3h + rim * 0.8h);
                half lattice = 0.0h;
            #ifndef _SHIELD_LITE
                float edge = input.local.x;
                float aa = max(fwidth(edge), 1e-4);
                lattice = (half)smoothstep(1.0 - _Line - aa, 1.0 - _Line + aa, edge);
                // A soft halo inside the line, so the lattice glows rather than aliases.
                half halo = (half)saturate((edge - (1.0 - _Line * 3.0)) / (_Line * 2.0));
                glow += lattice * (0.06h + soft * 0.35h + rim * 0.6h) + halo * halo * rim * 0.2h;
                glow += input.tile.x * (0.05h + lattice * 2.2h + halo * 0.6h);
                glow += input.tile.y * (0.02h + lattice * 0.25h);
            #endif
                glow *= side * input.tile.z;
                glow += input.tile.w * (0.06h + rim * 0.5h + lattice * 1.2h) * input.tile.z;

                // Where a dome meets the ground: a bright seam, and nothing below it.
                float height = input.local.y;
                half band = (half)exp2(-max(height, 0.0) * 3.0) * 1.3h * input.tile.z;
                glow += band * _Ground;
                glow *= lerp(1.0h, (half)step(0.0, height), _Ground);

                // Going down it flares first; coming up it fades in.
                half flare = _Collapse > 0.0h ? 1.0h + 2.2h * (half)exp2(-_Collapse * 14.0) : 1.0h;
                glow *= _Power * flare;

                half3 colour = _Color.rgb * glow * _Intensity;
                // White-hot only where it is brightest (the rim, a ripple's heart).
                half hot = max(glow - 0.9h, 0.0h);
                colour += hot * hot * 0.2h * _Intensity;
                // How much of what is behind it covers: nothing in the clear middle, some at the rim.
                half cover = saturate(glow * 0.3h);
                // Fog: towards the fog's colour over what it covers, fading the glow out.
                colour = MixFogColor(colour, unity_FogColor.rgb * cover, input.fog);
                return half4(colour, cover);
            }
            ENDHLSL
        }
    }
}

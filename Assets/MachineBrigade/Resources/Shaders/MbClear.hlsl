#ifndef MB_CLEAR_INCLUDED
#define MB_CLEAR_INCLUDED

// A boss is never lost behind the smoke and fire of the strikes on it: smoke and flames between
// the camera and the boss thin out over it (EffectsDirector sets _MbClear each frame). Nothing is
// removed or made smaller: fire keeps half its glow over the boss, smoke a fifth of its cover,
// and everything outside the boss's outline on screen is untouched.

float4 _MbClear; // xyz: the boss's centre in the world; w: its radius on screen (0: no boss)

half MbClearFade(float3 positionWS, half floorValue)
{
    if (_MbClear.w <= 0.0) return 1.0h;
    float3 forward = GetViewForwardDir();
    float3 d = positionWS - _MbClear.xyz;
    // The camera is orthographic: what covers the boss on screen lies near the line of sight
    // through its centre, anywhere nearer the camera than the boss.
    float along = dot(d, forward);
    float r = length(d - along * forward);
    half inside = (half)saturate(1.0 - (r - _MbClear.w) / (_MbClear.w * 0.7));
    half front = (half)saturate(0.5 - along / 4.0);
    return lerp(1.0h, floorValue, inside * front);
}

#endif

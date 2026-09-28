#ifndef MB_DEPTH_INCLUDED
#define MB_DEPTH_INCLUDED

// Moves a particle vertex in depth only, never across the screen (DECISIONS 12A).

// Slides a vertex pull metres towards the camera. The battle camera is orthographic: straight
// along the view. The detail page's range and preview cameras are perspective: along the ray
// to the camera, so the vertex still lands on the same pixel. Sliding along the view axis there
// moved fire and smoke across the screen (a muzzle flash a metre off its barrel, a flame stream
// beside its nozzle), the more the farther from the middle of the view.
float3 MbDepthPull(float3 positionWS, float pull)
{
    if (IsPerspectiveProjection())
    {
        float3 toCamera = GetCameraPositionWS() - positionWS;
        float distance = max(length(toCamera), 1e-3);
        return positionWS + toCamera / distance * min(pull, distance * 0.5);
    }
    return positionWS - GetViewForwardDir() * pull;
}

// Slides a vertex along its view ray onto the ground plane (lift metres up): a fire burning on
// the ground keeps its shape on screen but lies on the ground in depth, so a vehicle standing in
// it (above the ground) is drawn over its flames instead of inside them.
float3 MbOntoGround(float3 positionWS, float lift)
{
    float3 ray = IsPerspectiveProjection() ? normalize(positionWS - GetCameraPositionWS()) : GetViewForwardDir();
    if (ray.y > -0.05) return positionWS;
    return positionWS + ray * ((lift - positionWS.y) / ray.y);
}

#endif

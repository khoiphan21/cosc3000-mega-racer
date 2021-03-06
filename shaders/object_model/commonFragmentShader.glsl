uniform mat4 worldToViewTransform;
uniform mat4 viewSpaceToSmTextureSpace;
uniform sampler2DShadow shadowMapTexture;

uniform vec3 viewSpaceLightPosition;
uniform vec3 sunLightColour;
uniform vec3 globalAmbientLight;

vec3 toSrgb(vec3 color)
{
  return pow(color, vec3(1.0 / 2.2));
}


vec3 computeShading(vec3 materialColour, vec3 viewSpacePosition, vec3 viewSpaceNormal, vec3 viewSpaceLightPos, vec3 lightColour)
{
    // TODO 1.5: Here's where code to compute shading would be placed most conveniently
    vec3 viewSpaceDirToLight = normalize(viewSpaceLightPosition - viewSpacePosition);
    vec3 norm_viewSpaceNormal = normalize(viewSpaceNormal);
    float incomingIntensity = max(0.0, dot(norm_viewSpaceNormal, viewSpaceDirToLight));
    return (vec3(incomingIntensity) * sunLightColour +  + globalAmbientLight) * materialColour;
    // return (vec3(incomingIntensity)) * materialColour;
    // return materialColour;
}
// Input from the vertex shader, will contain the interpolated (i.e., area weighted average) value
// out put for each of the three vertex shaders that
// produced the vertex data for the triangle this fragmet is part of.
in VertexData
{
    float v2f_height;
    vec3 v2f_viewSpacePosition;
    vec3 v2f_viewSpaceNormal;
    vec3 v2f_worldSpacePosition;
};

uniform float terrainHeightScale;
uniform float terrainTextureXyScale;

out vec4 fragmentColor;

void main()
{
    vec3 materialColour = vec3(v2f_height/terrainHeightScale);
    // TODO 1.4: Compute the texture coordinates and sample the texture for the 
    // grass and use as material colour.

    vec3 reflectedLight = computeShading(materialColour, v2f_viewSpacePosition, 
        v2f_viewSpaceNormal, viewSpaceLightPosition, sunLightColour);
    fragmentColor = vec4(toSrgb(reflectedLight), 1.0);
    // fragmentColor = vec4(toSrgb(vec3(v2f_height/terrainHeightScale)), 1.0);

}
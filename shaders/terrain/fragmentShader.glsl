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

uniform sampler2D ourTexture;
uniform sampler2D rockHighTexture;

out vec4 fragmentColor;

void main()
{   
    // TODO 1.4: Compute the texture coordinates and sample the texture for the 
    // grass and use as material colour.
    vec2 textCoord = vec2(v2f_worldSpacePosition.x * terrainTextureXyScale, v2f_worldSpacePosition.y * terrainTextureXyScale);

    float height = v2f_height/terrainHeightScale;
    float ratio = 0.0;

    if ( height > 0.8)
    {
        ratio = height;
    }

    vec4 mixedTexture = mix(
        texture(ourTexture, textCoord),
        texture(rockHighTexture, textCoord),
        ratio
    );
    vec3 materialColour = mixedTexture.xyz;
    // vec3 materialColour = texture(ourTexture, textCoord).xyz;


    vec3 reflectedLight = computeShading(materialColour, v2f_viewSpacePosition, 
        v2f_viewSpaceNormal, viewSpaceLightPosition, sunLightColour);
    fragmentColor = vec4(toSrgb(reflectedLight), 1.0);
    // fragmentColor = vec4(toSrgb(vec3(v2f_height/terrainHeightScale)), 1.0);

}
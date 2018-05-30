// Input from the vertex shader, will contain the interpolated (i.e., area weighted average) value
// out put for each of the three vertex shaders that
// produced the vertex data for the triangle this fragmet is part of.
in VertexData
{
    float v2f_height;
    vec3 v2f_viewSpacePosition;
    vec3 v2f_viewSpaceNormal;
    vec3 v2f_worldSpacePosition;
    vec3 v2f_normalIn;
    vec2 v2f_xyNormScale;
    vec2 v2f_xyOffset;    
};

uniform float terrainHeightScale;
uniform float terrainTextureXyScale;

uniform sampler2D ourTexture;
uniform sampler2D rockHighTexture;
uniform sampler2D slopeTexture;
uniform sampler2D pavingTexture;
uniform sampler2D mapData;

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

    // Now check viewspace normal to see if the texture should be slope instead
    float cosine = dot(v2f_normalIn, 
            vec3(v2f_normalIn.x, 0.0, v2f_normalIn.z)
        );
    if (cosine < 0.6) {
            materialColour = mix(
            texture(ourTexture, textCoord),
            texture(slopeTexture, textCoord),
            0.3 * cosine
        ).xyz;
    }

    // Now pick material color based on map data
    // get normalised texture coordinates first
    vec2 normalized_text_coord = vec2(
        v2f_worldSpacePosition.x * v2f_xyNormScale.x, 
        v2f_worldSpacePosition.y * v2f_xyNormScale.y
    );
    normalized_text_coord = (normalized_text_coord - 
        v2f_xyOffset * v2f_xyNormScale
    );
    float blue_channel = texture(mapData, normalized_text_coord).z;
    if (blue_channel > 0.1) {
        materialColour = mix(
            texture(ourTexture, textCoord),
            texture(pavingTexture, textCoord),
            blue_channel
        ).xyz;
        // materialColour = texture(pavingTexture, textCoord).xyz;
    }
    // vec3 materialColour = texture(ourTexture, textCoord).xyz;


    vec3 reflectedLight = computeShading(materialColour, v2f_viewSpacePosition, 
        v2f_viewSpaceNormal, viewSpaceLightPosition, sunLightColour);
    fragmentColor = vec4(toSrgb(reflectedLight), 1.0);


    // try to output fragment color as the terrain data first
    

    // fragmentColor = vec4(texture(mapData, normalized_text_coord).xyz, 1.0);

}
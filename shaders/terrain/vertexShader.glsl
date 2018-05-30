#version 330
in vec3 positionIn;
in vec3 normalIn;

uniform mat4 modelToClipTransform;
uniform mat4 modelToViewTransform;
uniform mat3 modelToViewNormalTransform;

uniform float terrainHeightScale;
uniform float terrainTextureXyScale;
uniform vec2 xyNormScale;
uniform vec2 xyOffset;


// 'out' variables declared in a vertex shader can be accessed in the subsequent stages.
// For a fragment shader the variable is interpolated (the type of interpolation can be modified, try placing 'flat' in front here and in the fragment shader!).
out VertexData
{
    float v2f_height;
    vec3 v2f_viewSpacePosition;
    vec3 v2f_viewSpaceNormal;
    vec3 v2f_worldSpacePosition;
    vec3 v2f_normalIn;
    vec2 v2f_xyNormScale;
};

void main()
{
    // pass the world-space Z to the fragment shader, as it is used to compute the colour and other things
    v2f_height = positionIn.z;
    v2f_worldSpacePosition = positionIn;
    v2f_viewSpacePosition = (modelToViewTransform * vec4(positionIn, 1.0)).xyz;
    v2f_viewSpaceNormal = modelToViewNormalTransform * normalIn;
    v2f_normalIn = normalIn;
    v2f_xyNormScale = xyNormScale;
    // gl_Position is a buit-in 'out'-variable that gets passed on to the clipping and rasterization stages (hardware fixed function).
    // it must be written by the vertex shader in order to produce any drawn geometry.
    // We transform the position using one matrix multiply from model to clip space. Note the added 1 at the end of the position to make the 3D
    // coordinate homogeneous.
    gl_Position = modelToClipTransform * vec4(positionIn, 1.0);
}
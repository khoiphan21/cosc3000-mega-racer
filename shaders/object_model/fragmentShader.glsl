// Input from the vertex shader, will contain the interpolated (i.e., area-weighted average) vaule out put for each of the three vertex shaders that
// produced the vertex data for the triangle this fragment is part of.
in VertexData
{
    vec3 v2f_viewSpaceNormal;
    vec3 v2f_viewSpacePosition;
    vec2 v2f_texCoord;
};

// Material properties set by OBJModel.
uniform vec3 material_diffuse_color;
uniform float material_alpha;
uniform vec3 material_specular_color;
uniform vec3 material_emissive_color;
uniform float material_specular_exponent;

// Textures set by OBJModel
uniform sampler2D diffuse_texture;
uniform sampler2D opacity_texture;
uniform sampler2D specular_texture;
uniform sampler2D normal_texture;

out vec4 fragmentColor;

void main()
{
    // Manual alpha test (note: alpha test is no longer part of Opengl 3.3).
    if (texture(opacity_texture, v2f_texCoord).r < 0.5)
    {
        discard;
    }

    vec3 materialDiffuse = texture(diffuse_texture, v2f_texCoord).xyz * material_diffuse_color;

    vec3 reflectedLight = computeShading(materialDiffuse, v2f_viewSpacePosition, v2f_viewSpaceNormal, viewSpaceLightPosition, sunLightColour) + material_emissive_color;

    fragmentColor = vec4(toSrgb(reflectedLight), material_alpha);
}
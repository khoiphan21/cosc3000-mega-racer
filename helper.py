from OpenGL.GL import *
import math

import imgui

# we use 'warnings' to remove this warning that ImGui[glfw] gives
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from ObjModel import ObjModel
import lab_utils as lu
from lab_utils import vec3

from mega_racer import World


#
# Classes
#


# ViewParams is used to contain the needed data to represent a 'view' mostly we want to get at the
# projection and world-to-view transform, as these are used in all shaders. Keeping them in one
# object makes it easier to pass around. It is also convenient future-proofing if we want to add more
# views (e.g., for a shadow map).
class ViewParams:
    viewToClipTransform = lu.Mat4()
    worldToViewTransform = lu.Mat4()
    width = 0
    height = 0


#
# Really just a helper class to be able to pass around shared utilities to the different modules
#
class RenderingSystem:
    # The variable renderingSystem.commonFragmentShaderCode contains code that we wish to use in all the fragment shaders,
    # for example code to transform the colour output to srgb. It is also a nice place to put code to compute lighting
    # and other effects that should be the same accross the terrain and racer for example.
    commonFragmentShaderCode = """

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
        return materialColour;
    }
    """
    objModelShader = None

    def __init__(self, world: World):
        self.world = world

    # Helper to set common uniforms, such as those used for global lights that should be implemetned the same way in all shaders.
    # Properly, these should be put into a uniform buffer object and uploaded once and for all, this is infinitely faster and better
    #
    def setCommonUniforms(self, shader, view, modelToWorldTransform):
        # Concatenate the transformations to take vertices directly from model space to clip space
        modelToClipTransform = view.viewToClipTransform * view.worldToViewTransform * modelToWorldTransform
        # Transform to view space from model space (used for the shading)
        modelToViewTransform = view.worldToViewTransform * modelToWorldTransform
        # Transform to view space for normals, need to use the inverse transpose unless only rigid body & uniform scale.
        modelToViewNormalTransform = lu.inverse(lu.transpose(lu.Mat3(modelToViewTransform)))

        # Set the standard transforms, these vary per object and must be set each time an object is drawn (since they have different modelToWorld transforms)
        lu.setUniform(shader, "modelToClipTransform", modelToClipTransform);
        lu.setUniform(shader, "modelToViewTransform", modelToViewTransform);
        lu.setUniform(shader, "modelToViewNormalTransform", modelToViewNormalTransform);

        # These transforms are the same for the current view and could be set once for all the objects
        lu.setUniform(shader, "worldToViewTransform", view.worldToViewTransform);
        lu.setUniform(shader, "viewToClipTransform", view.viewToClipTransform);
        # Lighting parameters as could these
        viewSpaceLightPosition = lu.transformPoint(view.worldToViewTransform, self.world.g_sunPosition);
        lu.setUniform(shader, "viewSpaceLightPosition", viewSpaceLightPosition);
        lu.setUniform(shader, "globalAmbientLight", self.world.g_globalAmbientLight);
        lu.setUniform(shader, "sunLightColour", self.world.g_sunLightColour);

    def drawObjModel(self, model, modelToWorldTransform, view):
        # Bind the shader program such that we can set the uniforms (model.render sets it again)
        glUseProgram(self.objModelShader)

        self.setCommonUniforms(self.objModelShader, view, modelToWorldTransform);

        model.render(self.objModelShader)

        glUseProgram(0)

    def setupObjModelShader(self):
        self.objModelShader = lu.buildShader(["""
                #version 330

                in vec3 positionAttribute;
                in vec3	normalAttribute;
                in vec2	texCoordAttribute;

                uniform mat4 modelToClipTransform;
                uniform mat4 modelToViewTransform;
                uniform mat3 modelToViewNormalTransform;

                // Out variables decalred in a vertex shader can be accessed in the subsequent stages.
                // For a pixel shader the variable is interpolated (the type of interpolation can be modified, try placing 'flat' in front, and also in the fragment shader!).
                out VertexData
                {
	                vec3 v2f_viewSpaceNormal;
	                vec3 v2f_viewSpacePosition;
	                vec2 v2f_texCoord;
                };

                void main() 
                {
	                // gl_Position is a buit in out variable that gets passed on to the clipping and rasterization stages.
                  // it must be written in order to produce any drawn geometry. 
                  // We transform the position using one matrix multiply from model to clip space, note the added 1 at the end of the position.
	                gl_Position = modelToClipTransform * vec4(positionAttribute, 1.0);
	                // We transform the normal to view space using the normal transform (which is the inverse-transpose of the rotation part of the modelToViewTransform)
                  // Just using the rotation is only valid if the matrix contains only rotation and uniform scaling.
	                v2f_viewSpaceNormal = normalize(modelToViewNormalTransform * normalAttribute);
	                v2f_viewSpacePosition = (modelToViewTransform * vec4(positionAttribute, 1.0)).xyz;
	                // The texture coordinate is just passed through
	                v2f_texCoord = texCoordAttribute;
                }
                """], ["#version 330\n", self.commonFragmentShaderCode, """
                // Input from the vertex shader, will contain the interpolated (i.e., area-weighted average) vaule out put for each of the three vertex shaders that 
                // produced the vertex data for the triangle this fragmet is part of.
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
            """], ObjModel.getDefaultAttributeBindings())
        glUseProgram(self.objModelShader)
        ObjModel.setDefaultUniformBindings(self.objModelShader)
        glUseProgram(0)


#
# Functions and procedures
#


def sampleKeyFrames(t, kfs):
    # 1. find correct interval
    if t <= kfs[0][0]:
        return kfs[0][1]

    if t >= kfs[-1][0]:
        return kfs[-1][1]

    for i1 in range(1, len(kfs)):
        if t < kfs[i1][0]:
            i0 = i1 - 1;
            t0 = kfs[i0][0];
            t1 = kfs[i1][0];
            # linear interpolation from one to the other
            return lu.mix(kfs[i0][1], kfs[i1][1], (t - t0) / (t1 - t0));

    # we should not get here, unless the key values are malformed (i.e., not strictly increasing)
    assert False
    # but if we do, we return a value that is obviously no good (rahter than say zero that might pass unnoticed for much longer)
    return None


def update(world: World, g_renderingSystem: RenderingSystem, dt, keyStateMap, mouseDelta):

    if world.g_updateSun:
        world.g_sunAngle += dt * 0.25
        world.g_sunAngle = world.g_sunAngle % (2.0 * math.pi)

    world.g_sunPosition = lu.Mat3(lu.make_rotation_x(world.g_sunAngle)) * world.g_sunStartPosition

    world.g_sunLightColour = sampleKeyFrames(lu.dot(lu.normalize(world.g_sunPosition), vec3(0.0, 0.0, 1.0)), world.g_sunKeyFrames)
    world.g_globalAmbientLight = sampleKeyFrames(lu.dot(lu.normalize(world.g_sunPosition), vec3(0.0, 0.0, 1.0)), world.g_ambientKeyFrames)

    world.racer.update(dt, keyStateMap)

    world.g_viewPosition = world.racer.position - (world.racer.heading * world.g_followCamOffset) + [0, 0, world.g_followCamOffset]
    world.g_viewTarget = world.racer.position + vec3(0, 0, world.g_followCamLookOffset)

    if imgui.tree_node("Camera", imgui.TREE_NODE_DEFAULT_OPEN):
        _, world.g_followCamOffset = imgui.slider_float("FollowCamOffset ", world.g_followCamOffset, 2.0, 100.0)
        _, world.g_followCamLookOffset = imgui.slider_float("FollowCamLookOffset", world.g_followCamLookOffset, 0.0, 100.0)
        imgui.tree_pop()

    if imgui.tree_node("Racer", imgui.TREE_NODE_DEFAULT_OPEN):
        world.racer.drawUi()
        imgui.tree_pop()

    if imgui.tree_node("Terrain", imgui.TREE_NODE_DEFAULT_OPEN):
        world.terrain.drawUi()
        imgui.tree_pop()

    if imgui.tree_node("Lighting", imgui.TREE_NODE_DEFAULT_OPEN):
        _, world.g_globalAmbientLight = lu.imguiX_color_edit3_list("GlobalAmbientLight",
                                                                   world.g_globalAmbientLight)  # , imgui.GuiColorEditFlags_Float);// | ImGuiColorEditFlags_HSV);
        _, world.g_sunLightColour = lu.imguiX_color_edit3_list("SunLightColour",
                                                               world.g_sunLightColour)  # , imgui.GuiColorEditFlags_Float);// | ImGuiColorEditFlags_HSV);
        _, world.g_sunAngle = imgui.slider_float("SunAngle", world.g_sunAngle, 0.0, 2.0 * math.pi)
        _, world.g_updateSun = imgui.checkbox("UpdateSun", world.g_updateSun)
        imgui.tree_pop()


# Called once per frame by the main loop below
def renderFrame(game: World, rendering_system: RenderingSystem, width, height):
    glViewport(0, 0, width, height)
    glClearColor(game.g_backGroundColour[0], game.g_backGroundColour[1], game.g_backGroundColour[2], 1.0)
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    aspectRatio = float(width) / float(height)

    # ViewParams is used to contain the needed data to represent a 'view' mostly we want to get at the
    # projection and world-to-view transform, as these are used in all shaders. Keeping them in one
    # object makes it easier to pass around. It is also convenient future-proofing if we want to add more
    # views (e.g., for a shadow map).
    view = ViewParams()
    # Projection (view to clip space transform)
    view.viewToClipTransform = lu.make_perspective(game.g_fov, aspectRatio, game.g_nearDistance, game.g_farDistance)
    # Transform from world space to view space.
    view.worldToViewTransform = lu.make_lookAt(game.g_viewPosition, game.g_viewTarget, game.g_viewUp)
    view.width = width
    view.height = height

    # Call each part of the scene to render itself
    game.terrain.render(view, rendering_system)
    game.racer.render(view, rendering_system)

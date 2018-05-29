from OpenGL.GL import *
import math

import imgui

# we use 'warnings' to remove this warning that ImGui[glfw] gives
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from utils.ObjModel import ObjModel
from utils import lab_utils as lu
from utils.lab_utils import vec3

from models.world import World


OBJECT_MODEL_VERTEX_SHADER_FILE = 'shaders/object_model/vertexShader.glsl'
OBJECT_MODEL_FRAGMENT_SHADER_FILE = 'shaders/object_model/fragmentShader.glsl'
COMMON_FRAGMENT_SHADER_FILE = 'shaders/object_model/commonFragmentShader.glsl'


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

    objModelShader = None

    def __init__(self, world: World):
        self.world = world

        # The variable renderingSystem.commonFragmentShaderCode contains code that we wish to use in all the fragment shaders,
        # for example code to transform the colour output to srgb. It is also a nice place to put code to compute lighting
        # and other effects that should be the same accross the terrain and racer for example.
        with open(COMMON_FRAGMENT_SHADER_FILE) as file:
            self.commonFragmentShaderCode = ''.join(file.readlines())

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
        lu.setUniform(shader, "modelToClipTransform", modelToClipTransform)
        lu.setUniform(shader, "modelToViewTransform", modelToViewTransform)
        lu.setUniform(shader, "modelToViewNormalTransform", modelToViewNormalTransform)

        # These transforms are the same for the current view and could be set once for all the objects
        lu.setUniform(shader, "worldToViewTransform", view.worldToViewTransform)
        lu.setUniform(shader, "viewToClipTransform", view.viewToClipTransform)
        # Lighting parameters as could these
        viewSpaceLightPosition = lu.transformPoint(view.worldToViewTransform, self.world.sun_position)
        lu.setUniform(shader, "viewSpaceLightPosition", viewSpaceLightPosition)
        lu.setUniform(shader, "globalAmbientLight", self.world.global_ambient_light)
        lu.setUniform(shader, "sunLightColour", self.world.sunlight_color)

    def drawObjModel(self, model, modelToWorldTransform, view):
        # Bind the shader program such that we can set the uniforms (model.render sets it again)
        glUseProgram(self.objModelShader)

        self.setCommonUniforms(self.objModelShader, view, modelToWorldTransform)

        model.render(self.objModelShader)

        glUseProgram(0)

    def setupObjModelShader(self):
        with open(OBJECT_MODEL_VERTEX_SHADER_FILE) as file:
            vertex_shader_code = ''.join(file.readlines())
        with open(OBJECT_MODEL_FRAGMENT_SHADER_FILE) as file:
            fragment_shader_code = ''.join(file.readlines())
        self.objModelShader = lu.buildShader([vertex_shader_code],
                                             ["#version 330\n", self.commonFragmentShaderCode, fragment_shader_code],
                                             ObjModel.getDefaultAttributeBindings())
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
            i0 = i1 - 1
            t0 = kfs[i0][0]
            t1 = kfs[i1][0]
            # linear interpolation from one to the other
            return lu.mix(kfs[i0][1], kfs[i1][1], (t - t0) / (t1 - t0))

    # we should not get here, unless the key values are malformed (i.e., not strictly increasing)
    assert False
    # but if we do, we return a value that is obviously no good (rahter than say zero that might pass unnoticed for much longer)
    return None


def update(world: World, g_renderingSystem: RenderingSystem, dt, keyStateMap, mouseDelta):

    if world.should_update_sun:
        world.sun_angle += dt * 0.25
        world.sun_angle = world.sun_angle % (2.0 * math.pi)

    world.sun_position = lu.Mat3(lu.make_rotation_x(world.sun_angle)) * world.sun_start_position

    world.sunlight_color = sampleKeyFrames(lu.dot(lu.normalize(world.sun_position), vec3(0.0, 0.0, 1.0)), world.sun_keyframes)
    world.global_ambient_light = sampleKeyFrames(lu.dot(lu.normalize(world.sun_position), vec3(0.0, 0.0, 1.0)), world.ambient_keyframes)

    world.racer.update(dt, keyStateMap)

    world.view_position = world.racer.position - \
                          (world.racer.heading * world.follow_cam_offset) + \
                          [0, 0, world.follow_cam_offset]
    world.view_target = world.racer.position + vec3(0, 0, world.follow_cam_look_offset)

    if imgui.tree_node("Camera", imgui.TREE_NODE_DEFAULT_OPEN):
        _, world.follow_cam_offset = imgui.slider_float("FollowCamOffset ", world.follow_cam_offset, 2.0, 100.0)
        _, world.follow_cam_look_offset = imgui.slider_float("FollowCamLookOffset", world.follow_cam_look_offset, 0.0, 100.0)
        imgui.tree_pop()

    if imgui.tree_node("Racer", imgui.TREE_NODE_DEFAULT_OPEN):
        world.racer.draw_ui()
        imgui.tree_pop()

    if imgui.tree_node("Terrain", imgui.TREE_NODE_DEFAULT_OPEN):
        world.terrain.draw_ui()
        imgui.tree_pop()

    if imgui.tree_node("Lighting", imgui.TREE_NODE_DEFAULT_OPEN):
        _, world.global_ambient_light = lu.imguiX_color_edit3_list("GlobalAmbientLight",
                                                                   world.global_ambient_light)  # , imgui.GuiColorEditFlags_Float);// | ImGuiColorEditFlags_HSV);
        _, world.sunlight_color = lu.imguiX_color_edit3_list("SunLightColour",
                                                             world.sunlight_color)  # , imgui.GuiColorEditFlags_Float);// | ImGuiColorEditFlags_HSV);
        _, world.sun_angle = imgui.slider_float("SunAngle", world.sun_angle, 0.0, 2.0 * math.pi)
        _, world.should_update_sun = imgui.checkbox("UpdateSun", world.should_update_sun)
        imgui.tree_pop()


# Called once per frame by the main loop below
def renderFrame(game: World, rendering_system: RenderingSystem, width, height):
    glViewport(0, 0, width, height)
    glClearColor(game.background_color[0], game.background_color[1], game.background_color[2], 1.0)
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    aspectRatio = float(width) / float(height)

    # ViewParams is used to contain the needed data to represent a 'view' mostly we want to get at the
    # projection and world-to-view transform, as these are used in all shaders. Keeping them in one
    # object makes it easier to pass around. It is also convenient future-proofing if we want to add more
    # views (e.g., for a shadow map).
    view = ViewParams()
    # Projection (view to clip space transform)
    view.viewToClipTransform = lu.make_perspective(game.field_of_view, aspectRatio, game.near_distance, game.far_distance)
    # Transform from world space to view space.
    view.worldToViewTransform = lu.make_lookAt(game.view_position, game.view_target, game.view_up)
    view.width = width
    view.height = height

    # Call each part of the scene to render itself
    game.terrain.render(view, rendering_system)
    game.racer.render(view, rendering_system)

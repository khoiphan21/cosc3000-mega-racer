"""Initialise the GLFW windows and world UI"""

from OpenGL.GL import *
import glfw

import sys

import imgui

# we use 'warnings' to remove this warning that ImGui[glfw] gives
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer

from models.terrain import Terrain
from models.racer import Racer
from helper import renderFrame, update, RenderingSystem
from .mappings import GLFW_KEYMAP, GLFW_MOUSE_MAP

from models.world import World


START_WIDTH  = 1280
START_HEIGHT = 720

def setup_glfw():
    """Initialises the GLFW window and world UI"""
    if not glfw.init():
        sys.exit(1)

    # glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, 1)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    # This can be used to turn on multisampling AA for the default render target.
    # glfw.window_hint(glfw.SAMPLES, g_currentMsaaSamples)

    window = glfw.create_window(START_WIDTH, START_HEIGHT, "The Mega-racer world", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    print(
        "--------------------------------------\nOpenGL\n  Vendor: %s\n  Renderer: %s\n  Version: %s\n--------------------------------------\n" % (
            glGetString(GL_VENDOR).decode("utf8"), glGetString(GL_RENDERER).decode("utf8"),
            glGetString(GL_VERSION).decode("utf8")), flush=True)

    # Enable some much-needed hardware functions that are off by default.
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)

    return window


def run_main_logic(game: World, rendering_system: RenderingSystem, window):

    impl = ImGuiGlfwRenderer(window)

    # set the variables from the world object
    game.terrain = Terrain()
    game.terrain.load("data/track_01_128.png", rendering_system)

    game.racer = Racer()
    game.racer.load("data/racer_02.obj", game.terrain, rendering_system)

    currentTime = glfw.get_time()
    prevMouseX, prevMouseY = glfw.get_cursor_pos(window)

    while not glfw.window_should_close(window):
        prevTime = currentTime
        currentTime = glfw.get_time()
        dt = currentTime - prevTime

        keyStateMap = {}
        for name, id in GLFW_KEYMAP.items():
            keyStateMap[name] = glfw.get_key(window, id) == glfw.PRESS

        for name, id in GLFW_MOUSE_MAP.items():
            keyStateMap[name] = glfw.get_mouse_button(window, id) == glfw.PRESS

        imgui.new_frame()
        imgui.set_next_window_size(430.0, 450.0, imgui.FIRST_USE_EVER)
        imgui.begin("Tweak variables");

        mouseX, mouseY = glfw.get_cursor_pos(window)
        g_mousePos = [mouseX, mouseY]
        mouseDelta = [mouseX - prevMouseX, mouseY - prevMouseY]
        prevMouseX, prevMouseY = mouseX, mouseY

        # Udpate 'world logic'
        imIo = imgui.get_io()
        if imIo.want_capture_mouse:
            mouseDelta = [0, 0]
        update(game, rendering_system, dt, keyStateMap, mouseDelta)

        width, height = glfw.get_framebuffer_size(window)

        renderFrame(game, rendering_system, width, height)

        # mgui.show_test_window()

        imgui.end()
        imgui.render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()

    glfw.destroy_window(window)
    glfw.terminate()

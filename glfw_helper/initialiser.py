"""Contain the initialisation code for GLFW and OpenGL"""

from OpenGL.GL import GL_TRUE, GL_VENDOR, GL_RENDERER, \
    GL_VERSION, GL_CULL_FACE, GL_DEPTH_TEST, \
    glGetString, glEnable

import glfw

import sys


START_WIDTH = 1280
START_HEIGHT = 720


def initialise_glfw():
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

    print("{}\nOpenGL\n  Vendor: {}\n  Renderer: {}\n  Version: {}\n{}\n".format(
        ''.center(38, '-'),
        glGetString(GL_VENDOR).decode("utf8"),
        glGetString(GL_RENDERER).decode("utf8"),
        glGetString(GL_VERSION).decode("utf8"),
        ''.center(38, '-')
    ), flush=True)
    # Enable some much-needed hardware functions that are off by default.
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)

    return window

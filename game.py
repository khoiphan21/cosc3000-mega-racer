"""Initialise the GLFW windows and world UI"""

import glfw

import imgui


from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer

from models.terrain import Terrain
from models.racer import Racer
from models.world import World
from helper import renderFrame, update, RenderingSystem
from glfw_helper.mappings import GLFW_KEYMAP, GLFW_MOUSE_MAP
from glfw_helper.initialiser import initialise_glfw


START_WIDTH = 1280
START_HEIGHT = 720


class MegaRacer:
    def __init__(self, world: World):
        self.world = world
        self.rendering_system = None  # Can't set it up first until setup() is called
        self.window = None

    def setup(self):
        """Setup the GLFW library, OpenGL library and the rendering system"""
        self.window = initialise_glfw()
        self.__setup_rendering_system()

    def __setup_rendering_system(self):
        self.rendering_system = RenderingSystem(self.world)
        self.rendering_system.setupObjModelShader()

    def run(self):
        """Run the main game loop logic"""
        # Shorten the variables
        world = self.world
        rendering_system = self.rendering_system
        window = self.window

        impl = ImGuiGlfwRenderer(window)

        # set the variables from the world object
        world.terrain = Terrain()
        world.terrain.load("data/track_01_128.png", rendering_system)

        world.racer = Racer()
        world.racer.load("data/racer_02.obj", world.terrain)

        current_time = glfw.get_time()
        prev_mouse_x, prev_mouse_y = glfw.get_cursor_pos(window)

        while not glfw.window_should_close(window):
            prev_time = current_time
            current_time = glfw.get_time()
            dt = current_time - prev_time

            key_state_map = {}
            for item_name, item_id in GLFW_KEYMAP.items():
                key_state_map[item_name] = glfw.get_key(window, item_id) == glfw.PRESS

            for item_name, item_id in GLFW_MOUSE_MAP.items():
                key_state_map[item_name] = glfw.get_mouse_button(window, item_id) == glfw.PRESS

            imgui.new_frame()
            imgui.set_next_window_size(430.0, 450.0, imgui.FIRST_USE_EVER)
            imgui.begin("Tweak variables")

            mouse_x, mouse_y = glfw.get_cursor_pos(window)
            mouse_delta = [mouse_x - prev_mouse_x, mouse_y - prev_mouse_y]
            prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

            # Update 'world logic'
            im_io = imgui.get_io()
            if im_io.want_capture_mouse:
                mouse_delta = [0, 0]
            update(world, rendering_system, dt, key_state_map, mouse_delta)

            width, height = glfw.get_framebuffer_size(window)

            renderFrame(world, rendering_system, width, height)

            # mgui.show_test_window()

            imgui.end()
            imgui.render()
            # Swap front and back buffers
            glfw.swap_buffers(window)

            # Poll for and process events
            glfw.poll_events()
            impl.process_inputs()

        # This is the end of the game. Do some cleanup
        glfw.destroy_window(window)
        glfw.terminate()

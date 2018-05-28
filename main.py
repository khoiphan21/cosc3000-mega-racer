from models.world import World
from helper import RenderingSystem
from glfw_helper.initialiser import setup_glfw, run_main_logic


world = World()

window = setup_glfw()

rendering_system = RenderingSystem(world)
rendering_system.setupObjModelShader()

#
# Start the main program
#
run_main_logic(world, rendering_system, window)

"""The entry point of the whole project"""

import warnings  # we use 'warnings' to remove this warning that ImGui[glfw] gives

from models.world import World
from game import MegaRacer

warnings.simplefilter(action='ignore', category=FutureWarning)

# Setup the world model used for rendering
world = World()

# Setup and run the game
game = MegaRacer(world)
game.setup()
game.run()

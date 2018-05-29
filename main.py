from models.world import World
from game import MegaRacer

# Setup the world model used for rendering
world = World()

# Setup and run the game
game = MegaRacer(world)
game.setup()
game.run()

import imgui

from utils import lab_utils as lu
from utils.lab_utils import vec3, make_mat4_from_zAxis
from models.terrain import TerrainInfo
from ObjModel import ObjModel


class ViewParams:
    """ViewParams is used to contain the needed data to represent a 'view'.

    Mostly we want to get at the projection and world-to-view transform,
    as these are used in all shaders. Keeping them in one object makes it
    easier to pass around.

    It is also convenient future-proofing if we want to add more views (e.g., for a shadow map).
    """
    viewToClipTransform = lu.Mat4()
    worldToViewTransform = lu.Mat4()
    width = 0
    height = 0


class Racer:
    position = vec3(0, 0, 0)
    velocity = vec3(0, 0, 0)
    heading = vec3(1, 0, 0)
    speed = 0.0

    max_speed_road = 50.0
    max_speed_rough = 15.0
    z_offset = 3.0
    angular_velocity = 2.0

    terrain = None
    model = None

    def render(self, view, rendering_system):
        rendering_system.drawObjModel(self.model,
                                      make_mat4_from_zAxis(self.position,
                                                           self.heading,
                                                           [0.0, 0.0, 1.0]),
                                      view)

    def load(self, model_name, terrain):
        self.terrain = terrain
        self.position = terrain.startLocations[0]
        self.model = ObjModel(model_name)

    def update(self, dt, key_state_map):
        info = self.terrain.getInfoAt(self.position)
        # Select max speed based on material
        max_speed = self.max_speed_road if info.material == TerrainInfo.M_Road else self.max_speed_rough

        target_velocity = vec3(0.0)
        if key_state_map["UP"]:
            target_velocity = self.heading * max_speed
        if key_state_map["DOWN"]:
            target_velocity = self.heading * -max_speed

        # Linearly interpolate towards the target velocity.
        # This means it is tied to the frame rate, which is kind of bad.
        self.velocity = lu.mix(self.velocity, target_velocity, 0.01)

        self.speed = lu.length(self.velocity)

        rotation_matrix = lu.Mat4()
        if key_state_map["LEFT"]:
            rotation_matrix = lu.make_rotation_z(dt * self.angular_velocity)
        if key_state_map["RIGHT"]:
            rotation_matrix = lu.make_rotation_z(dt * -self.angular_velocity)

        self.heading = lu.Mat3(rotation_matrix) * self.heading

        # get height of ground at this point.

        self.position += self.velocity * dt

        self.position[2] = lu.mix(self.position[2], info.height + self.z_offset, 0.1)

    def draw_ui(self):
        imgui.label_text("Speed", "%0.1fm/s" % self.speed)

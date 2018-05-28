from lab_utils import vec3


class World:
    background_color = [0.1, 0.2, 0.1]

    field_of_view = 60.0
    near_distance = 0.2
    far_distance = 2000.0

    view_position = [100.0, 100.0, 100.0]
    view_target = [0.0, 0.0, 0.0]
    view_up = [0.0, 0.0, 1.0]

    follow_cam_offset = 25.0
    follow_cam_look_offset = 10.0

    sun_start_position = [0.0, 0.0, 1000.0]
    sun_position = sun_start_position
    global_ambient_light = vec3(0.045, 0.045, 0.045)
    sunlight_color = [0.9, 0.8, 0.7]

    should_update_sun = True
    sun_angle = 0.0

    terrain = None
    racer = None

    #
    # Key-frames for the sun light and ambient, picked by hand-waving to look ok.
    # Note how most of this is nonsense from a physical point of view and
    # some of the reasoning is basically to compensate for the lack of exposure (or tone-mapping).
    #
    sun_keyframes = [
        [-1.0, vec3(0.0, 0.0, 0.0)],
        # midnight - no direct light, but we'll ramp up the ambient to make things look ok
        # (should _really_ be done using HDR)
        [0.0, vec3(0.0, 0.0, 0.0)],  # we want ull dark past the horizon line (this ixes shadow artiacts also)
        [0.2, vec3(0.9, 0.3, 0.2)],  # Quick sunrise to some reddish color perhaps?
        [1.0, vec3(1.0, 0.9, 0.8)],  # Noon
    ]
    ambient_keyframes = [
        [-1.0, vec3(0.045, 0.045, 0.15)],
        # Night, a somewhat brighter ambient (to compensate or the lack o direct light, totally unphyscal!)
        [0.0, vec3(0.045, 0.045, 0.15)],  # -||-
        [0.2, vec3(0.05, 0.045, 0.01)],  # Quick sunrise to some reddish color perhaps?
        [1.0, vec3(0.045, 0.045, 0.2)],  # Noon
    ]

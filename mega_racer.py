from lab_utils import vec3


class World:
    g_backGroundColour = [0.1, 0.2, 0.1]

    g_fov = 60.0
    g_nearDistance = 0.2
    g_farDistance = 2000.0

    g_viewPosition = [100.0, 100.0, 100.0]
    g_viewTarget = [0.0, 0.0, 0.0]
    g_viewUp = [0.0, 0.0, 1.0]

    g_followCamOffset = 25.0
    g_followCamLookOffset = 10.0

    g_sunStartPosition = [0.0, 0.0, 1000.0]
    g_sunPosition = g_sunStartPosition
    g_globalAmbientLight = vec3(0.045, 0.045, 0.045)
    g_sunLightColour = [0.9, 0.8, 0.7]

    g_updateSun = True
    g_sunAngle = 0.0

    terrain = None
    racer = None

    # g_rendering_system = None

    #
    # Key-frames for the sun light and ambient, picked by hand-waving to look ok. Note how most of this is nonsense from a physical point of view and
    # some of the reasoning is basically to compensate for the lack of exposure (or tone-mapping).
    #
    g_sunKeyFrames = [
        [-1.0, vec3(0.0, 0.0, 0.0)],
        # midnight - no direct light, but we'll ramp up the ambient to make things look ok - should _really_ be done using HDR
        [0.0, vec3(0.0, 0.0, 0.0)],  # we want ull dark past the horizon line (this ixes shadow artiacts also)
        [0.2, vec3(0.9, 0.3, 0.2)],  # Quick sunrise to some reddish color perhaps?
        [1.0, vec3(1.0, 0.9, 0.8)],  # Noon
    ]
    g_ambientKeyFrames = [
        [-1.0, vec3(0.045, 0.045, 0.15)],
        # Night, a somewhat brighter ambient (to compensate or the lack o direct light, totally unphyscal!)
        [0.0, vec3(0.045, 0.045, 0.15)],  # -||-
        [0.2, vec3(0.05, 0.045, 0.01)],  # Quick sunrise to some reddish color perhaps?
        [1.0, vec3(0.045, 0.045, 0.2)],  # Noon
    ]


#
# global variable declarations
#

g_backGroundColour = [0.1, 0.2, 0.1]

g_fov = 60.0
g_nearDistance = 0.2
g_farDistance = 2000.0

g_viewPosition = [100.0, 100.0, 100.0]
g_viewTarget = [0.0, 0.0, 0.0]
g_viewUp = [0.0, 0.0, 1.0]

g_followCamOffset = 25.0
g_followCamLookOffset = 10.0

g_sunStartPosition = [0.0, 0.0, 1000.0]
g_sunPosition = g_sunStartPosition
g_globalAmbientLight = vec3(0.045, 0.045, 0.045)
g_sunLightColour = [0.9, 0.8, 0.7]

g_updateSun = True
g_sunAngle = 0.0

g_terrain = None
g_racer = None

#
# Key-frames for the sun light and ambient, picked by hand-waving to look ok. Note how most of this is nonsense from a physical point of view and
# some of the reasoning is basically to compensate for the lack of exposure (or tone-mapping).
#
g_sunKeyFrames = [
    [-1.0, vec3(0.0, 0.0, 0.0)],
    # midnight - no direct light, but we'll ramp up the ambient to make things look ok - should _really_ be done using HDR
    [0.0, vec3(0.0, 0.0, 0.0)],  # we want ull dark past the horizon line (this ixes shadow artiacts also)
    [0.2, vec3(0.9, 0.3, 0.2)],  # Quick sunrise to some reddish color perhaps?
    [1.0, vec3(1.0, 0.9, 0.8)],  # Noon
]
g_ambientKeyFrames = [
    [-1.0, vec3(0.045, 0.045, 0.15)],
    # Night, a somewhat brighter ambient (to compensate or the lack o direct light, totally unphyscal!)
    [0.0, vec3(0.045, 0.045, 0.15)],  # -||-
    [0.2, vec3(0.05, 0.045, 0.01)],  # Quick sunrise to some reddish color perhaps?
    [1.0, vec3(0.045, 0.045, 0.2)],  # Noon
]

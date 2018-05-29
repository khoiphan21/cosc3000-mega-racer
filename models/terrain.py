import os

import imgui
from OpenGL.GL import *
from PIL import Image

from utils import lab_utils as lu
from utils.lab_utils import vec3, vec2
from utils.ObjModel import ObjModel


TERRAIN_VERTEX_SHADER_PATH = 'shaders/terrain/vertexShader.glsl'
TERRAIN_FRAGMENT_SHADER_PATH = 'shaders/terrain/fragmentShader.glsl'


# returned by getInfoAt to provide easy access to height and material type on the terrain for use
# by the world logic.
class TerrainInfo:
    M_Road = 0
    M_Rough = 1
    height = 0.0
    material = 0


# This class looks after loading & generating the terrain geometry as well as rendering.
# It also provides access to the terrain height and type at different points.
class Terrain:
    xyScale = 8.0
    heightScale = 75.0
    textureXyScale = 0.1

    imageWidth = 0
    imageHeight = 0
    shader = None
    renderWireFrame = False

    # Lists of locations generated from the map texture green channel (see the 'load' method)
    # you can add any other meaning of other values as you see fit.

    # Locations to place racers at (the start-grid if you will)
    startLocations = []
    # Locations where trees might be put down (the demo implementation samples these randomly)
    treeLocations = []
    # Same for rocks
    rockLocations = []

    # Texture unit allocations:
    TU_Grass = 0

    def render(self, view, renderingSystem):
        glUseProgram(self.shader)
        renderingSystem.setCommonUniforms(self.shader, view, lu.Mat4())

        lu.setUniform(self.shader, "terrainHeightScale", self.heightScale)
        lu.setUniform(self.shader, "terrainTextureXyScale", self.textureXyScale)
        xyNormScale = 1.0 / (vec2(self.imageWidth, self.imageHeight) * self.xyScale)
        lu.setUniform(self.shader, "xyNormScale", xyNormScale)
        xyOffset = -(vec2(self.imageWidth, self.imageHeight) + vec2(1.0)) * self.xyScale / 2.0
        lu.setUniform(self.shader, "xyOffset", xyOffset)

        # TODO 1.4: Bind the grass texture to the right texture unit, hint: lu.bindTexture
        texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0 + self.TU_Grass)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        if self.renderWireFrame:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(1.0)
        glBindVertexArray(self.vertexArrayObject)
        glDrawElements(GL_TRIANGLES, len(self.terrainInds), GL_UNSIGNED_INT, None)

        if self.renderWireFrame:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(0)
        glUseProgram(0)

    def load(self, imageName, renderingSystem):
        with Image.open(imageName)  as im:
            self.imageWidth = im.size[0]
            self.imageHeight = im.size[1]
            self.imageData = im.tobytes("raw", "RGBX" if im.mode == 'RGB' else "RGBA", 0, -1)

            xyOffset = -vec2(float(self.imageWidth), float(self.imageHeight)) * self.xyScale / 2.0;

            # Calculate vertex positions
            terrainVerts = []
            for j in range(self.imageHeight):
                for i in range(self.imageWidth):
                    offset = (j * self.imageWidth + i) * 4
                    # copy pixel 4 channels
                    imagePixel = self.imageData[offset:offset + 4];
                    # Normalize the red channel from [0,255] to [0.0, 1.0]
                    red = float(imagePixel[0]) / 255.0;

                    xyPos = vec2(i, j) * self.xyScale + xyOffset;
                    zPos = red * self.heightScale
                    pt = vec3(xyPos[0], xyPos[1], zPos)
                    terrainVerts.append(pt)

                    green = imagePixel[1];
                    if green == 255:
                        self.startLocations.append(pt)
                    if green == 128:
                        self.treeLocations.append(pt)
                    if green == 64:
                        self.rockLocations.append(pt)

            # build vertex normals...
            terrainNormals = [vec3(0.0, 0.0, 1.0)] * self.imageWidth * self.imageHeight;
            for j in range(1, self.imageHeight - 1):
                for i in range(1, self.imageWidth - 1):
                    v = terrainVerts[j * self.imageWidth + i];
                    vxP = terrainVerts[j * self.imageWidth + i - 1];
                    vxN = terrainVerts[j * self.imageWidth + i + 1];
                    dx = vxP - vxN;

                    vyP = terrainVerts[(j - 1) * self.imageWidth + i];
                    vyN = terrainVerts[(j + 1) * self.imageWidth + i];
                    dy = vyP - vyN;

                    nP = lu.normalize(lu.cross(dx, dy));

                    vdxyP = terrainVerts[(j - 1) * self.imageWidth + i - 1];
                    vdxyN = terrainVerts[(j + 1) * self.imageWidth + i + 1];
                    dxy = vdxyP - vdxyN;

                    vdyxP = terrainVerts[(j - 1) * self.imageWidth + i + 1];
                    vdyxN = terrainVerts[(j + 1) * self.imageWidth + i - 1];
                    dyx = vdyxP - vdyxN;

                    nD = lu.normalize(lu.cross(dxy, dyx));

                    terrainNormals[j * self.imageWidth + i] = lu.normalize(nP + nD);

            # join verts with quads that is: 2 triangles @ 3 vertices, with one less in each direction.
            terrainInds = [0] * 2 * 3 * (self.imageWidth - 1) * (self.imageHeight - 1)
            for j in range(0, self.imageHeight - 1):
                for i in range(0, self.imageWidth - 1):
                    # Vertex indices to the four corners of the quad.
                    qInds = [
                        j * self.imageWidth + i,
                        j * self.imageWidth + i + 1,
                        (j + 1) * self.imageWidth + i,
                        (j + 1) * self.imageWidth + i + 1,
                    ]
                    outOffset = 3 * 2 * (j * (self.imageWidth - 1) + i);
                    points = [
                        terrainVerts[qInds[0]],
                        terrainVerts[qInds[1]],
                        terrainVerts[qInds[2]],
                        terrainVerts[qInds[3]],
                    ]
                    # output first triangle:
                    terrainInds[outOffset + 0] = qInds[0];
                    terrainInds[outOffset + 1] = qInds[1];
                    terrainInds[outOffset + 2] = qInds[2];
                    # second triangle
                    terrainInds[outOffset + 3] = qInds[2];
                    terrainInds[outOffset + 4] = qInds[1];
                    terrainInds[outOffset + 5] = qInds[3];

            self.terrainInds = terrainInds

            # This creates a Vertex Array Object (VAO) to store each vertex attribute call.
            # This is so that we only need to configure the Vertex Attribute Pointers
            #   only once, and whenever we want to draw a certain object, we can just
            #   bind the corresponding VAO
            self.vertexArrayObject = glGenVertexArrays(1)

            self.vertexDataBuffer = lu.createAndAddVertexArrayData(self.vertexArrayObject, terrainVerts, 0)
            self.normalDataBuffer = lu.createAndAddVertexArrayData(self.vertexArrayObject, terrainNormals, 1)
            self.indexDataBuffer = lu.createAndAddIndexArray(self.vertexArrayObject, terrainInds)

        # Get the vertexShader and fragmentShader from the files
        with open(TERRAIN_VERTEX_SHADER_PATH) as file:
            vertexShader = ''.join(file.readlines())
        with open(TERRAIN_FRAGMENT_SHADER_PATH) as file:
            fragmentShader = ''.join(file.readlines())

        # Note how we provide lists of source code strings for the two shader stages.
        # This is basically the only standard way to 'include' or 'import' code into more than one shader. The variable renderingSystem.commonFragmentShaderCode
        # contains code that we wish to use in all the fragment shaders, for example code to transform the colour output to srgb.
        # It is also a nice place to put code to compute lighting and other effects that should be the same accross the terrain and racer for example.
        self.shader = lu.buildShader([vertexShader],
                                     ["#version 330\n", renderingSystem.commonFragmentShaderCode, fragmentShader],
                                     {"positionIn": 0, "normalIn": 1})

        # TODO 1.4: Load texture and configure the sampler
        texture_file = 'data/grass2.png'
        base_path, filename = os.path.split(texture_file)
        texture_id = ObjModel.loadTexture(filename, base_path, True)


    # Called by the world to drawt he UI widgets for the terrain.
    def draw_ui(self):
        # height scale is read-only as it is not run-time changable (since we use it to compute normals at load-time)
        imgui.label_text("terrainHeightScale", "%0.2f" % self.heightScale)
        # _,self.heightScale = imgui.slider_float("terrainHeightScale", self.heightScale, 1.0, 100.0)
        _, self.textureXyScale = imgui.slider_float("terrainTextureXyScale", self.textureXyScale, 0.01, 10.0)
        _, self.renderWireFrame = imgui.checkbox("WireFrame", self.renderWireFrame);

    # Retrieves information about the terrain at some x/y world-space position, if you request info from outside
    # the track it just clamps the position to the edge of the track.
    # Returns an instance of the class TerrainInfo.
    # An improvement that would make the movement of the racer smoother is to bi-linearly interpolate the image data.
    # this is something that comes free with OpenGL texture sampling, but here we'd have to implement it ourselves.
    def getInfoAt(self, position):
        # 1. convert x&y to texture scale
        xyOffset = -vec2(self.imageWidth, self.imageHeight) * self.xyScale / 2.0
        imageSpacePos = (vec2(position[0], position[1]) - xyOffset) / self.xyScale;

        x = max(0, min(self.imageWidth - 1, int(imageSpacePos[0])))
        y = max(0, min(self.imageHeight - 1, int(imageSpacePos[1])))
        pixelOffset = (y * self.imageWidth + x) * 4
        # copy pixel 4 channels
        imagePixel = self.imageData[pixelOffset:pixelOffset + 4]

        info = TerrainInfo();
        info.height = float(imagePixel[0]) * self.heightScale / 255.0;
        info.material = TerrainInfo.M_Road if imagePixel[2] == 255 else TerrainInfo.M_Rough
        return info;

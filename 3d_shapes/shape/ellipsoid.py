import ctypes
from OpenGL.GL import *
import glm
from .mesh import Mesh
from util import Shader

class Ellipsoid(Mesh):
    color: glm.vec3 = glm.vec3(0.7, 0.5, 0.7)

    def __init__(self, 
                 shader: Shader, 
                 vertexFile: str, 
                 subd : int = 0,
                 model: glm.mat4 = glm.mat4(1.0)):
        
        floatList: list[float] = []

        with open(vertexFile, 'r') as fin:
            floatList.extend(map(lambda x: float(x), fin.read().split()))

        assert len(floatList) % 9 == 0, \
               'vertexFile should contain 9n floats, ' \
               'each three floats denote a vertex (x, y, z), ' \
               'each three vertices denote a triangular facet'

        vertexList: list[float] = []

        if subd > 0:
            floatList = self.subdivide(subd,floatList)

        for i in range(0, len(floatList), 9):
            v1: glm.vec3 = glm.vec3(floatList[i],     floatList[i + 1], floatList[i + 2])
            v2: glm.vec3 = glm.vec3(floatList[i + 3], floatList[i + 4], floatList[i + 5])
            v3: glm.vec3 = glm.vec3(floatList[i + 6], floatList[i + 7], floatList[i + 8])
            faceNormal: glm.vec3 = glm.normalize(glm.cross(v2 - v1, v3 - v2))

            vertexList.append(v1.x)
            vertexList.append(v1.y)
            vertexList.append(v1.z)
            vertexList.append(faceNormal.x)
            vertexList.append(faceNormal.y)
            vertexList.append(faceNormal.z)
            vertexList.append(self.color.x)
            vertexList.append(self.color.y)
            vertexList.append(self.color.z)

            vertexList.append(v2.x)
            vertexList.append(v2.y)
            vertexList.append(v2.z)
            vertexList.append(faceNormal.x)
            vertexList.append(faceNormal.y)
            vertexList.append(faceNormal.z)
            vertexList.append(self.color.x)
            vertexList.append(self.color.y)
            vertexList.append(self.color.z)

            vertexList.append(v3.x)
            vertexList.append(v3.y)
            vertexList.append(v3.z)
            vertexList.append(faceNormal.x)
            vertexList.append(faceNormal.y)
            vertexList.append(faceNormal.z)
            vertexList.append(self.color.x)
            vertexList.append(self.color.y)
            vertexList.append(self.color.z)

        self.vertices: glm.array = glm.array(glm.float32, *vertexList)

        # Python does not support delegate constructors, 
        # implementing a classmethod called "fromFile" is much more Pythonic.
        # Yet, we invoke Mesh.__init__ for consistency with the C++ version...
        

        # Perform subdivision if requested
        
        
        super().__init__(shader, self.vertices, model)

    def subdivide(self, num_subdivisions: int, floatList: list[float]) -> list[float]:
        vertices = floatList
        # Define ellipsoid scaling factors
        a, b, c = 1.5, 1.0, 0.5  # x, y, z scaling factors
        
        for _ in range(num_subdivisions):
            new_vertices = []
            for i in range(0, len(vertices), 9):
                v1 = glm.vec3(vertices[i], vertices[i+1], vertices[i+2])
                v2 = glm.vec3(vertices[i+3], vertices[i+4], vertices[i+5])
                v3 = glm.vec3(vertices[i+6], vertices[i+7], vertices[i+8])

                # Calculate midpoints
                v12 = (v1 + v2) / 2.0
                v23 = (v2 + v3) / 2.0
                v31 = (v3 + v1) / 2.0

                # Normalize and scale to ellipsoid surface
                v12_norm = glm.normalize(v12)
                v23_norm = glm.normalize(v23)
                v31_norm = glm.normalize(v31)

                # Scale to ellipsoid
                v12 = glm.vec3(v12_norm.x * a, v12_norm.y * b, v12_norm.z * c)
                v23 = glm.vec3(v23_norm.x * a, v23_norm.y * b, v23_norm.z * c)
                v31 = glm.vec3(v31_norm.x * a, v31_norm.y * b, v31_norm.z * c)

                # Add four new triangles
                new_vertices.extend([v1.x, v1.y, v1.z])
                new_vertices.extend([v12.x, v12.y, v12.z])
                new_vertices.extend([v31.x, v31.y, v31.z])
                
                new_vertices.extend([v2.x, v2.y, v2.z])
                new_vertices.extend([v23.x, v23.y, v23.z])
                new_vertices.extend([v12.x, v12.y, v12.z])

                new_vertices.extend([v3.x, v3.y, v3.z])
                new_vertices.extend([v31.x, v31.y, v31.z])
                new_vertices.extend([v23.x, v23.y, v23.z])

                new_vertices.extend([v12.x, v12.y, v12.z])
                new_vertices.extend([v23.x, v23.y, v23.z])
                new_vertices.extend([v31.x, v31.y, v31.z])

            vertices = new_vertices
        return vertices
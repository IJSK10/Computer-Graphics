import ctypes
from OpenGL.GL import *
import glm
from .mesh import Mesh
from util import Shader

class Cube(Mesh):
    color: glm.vec3 = glm.vec3(0.3, 0.8, 0.5) 
    
    def __init__(self, 
                 shader: Shader, 
                 vertexFile: str, 
                 model: glm.mat4 = glm.mat4(1.0)):
        floatList: list[float] = []
        
        with open(vertexFile, 'r') as fin:
            floatList.extend(map(lambda x: float(x), fin.read().split()))
            
        assert len(floatList) % 9 == 0, \
               'vertexFile should contain 9n floats, ' \
               'each three floats denote a vertex (x, y, z), ' \
               'each three vertices denote a triangular facet'
        
        vertexList: list[float] = []
        
        for i in range(0, len(floatList), 9):
            v1: glm.vec3 = glm.vec3(floatList[i],     floatList[i + 1], floatList[i + 2])
            v2: glm.vec3 = glm.vec3(floatList[i + 3], floatList[i + 4], floatList[i + 5])
            v3: glm.vec3 = glm.vec3(floatList[i + 6], floatList[i + 7], floatList[i + 8])
            faceNormal: glm.vec3 = glm.normalize(glm.cross(v2 - v1, v3 - v2))
            
            for v in [v1, v2, v3]:
                vertexList.extend([
                    v.x, v.y, v.z,  # Position
                    faceNormal.x, faceNormal.y, faceNormal.z,  # Normal
                    self.color.x, self.color.y, self.color.z  # Color
                ])
        
        self.vertices: glm.array = glm.array(glm.float32, *vertexList)
        
        super().__init__(shader, self.vertices, model)
import ctypes
from typing import Dict, List, Tuple
from OpenGL.GL import *
import glm
from .mesh import Mesh
from util import Shader

class Smooth(Mesh):
    color: glm.vec3 = glm.vec3(0.1, 0.5, 0.2)
    
    def __init__(self, 
                 shader: Shader, 
                 vertexFile: str, 
                 model: glm.mat4 = glm.mat4(1.0)):
        
        # Read vertices from file
        floatList : list[float]= []
        with open(vertexFile, 'r') as fin:
            floatList.extend(map(lambda x: float(x), fin.read().split()))
        
        # Verify data format
        assert len(floatList) % 9 == 0, \
            'vertexFile should contain 9n floats, ' \
            'each three floats denote a vertex (x, y, z), ' \
            'each three vertices denote a triangular facet'
        
        # Dictionary to collect face normals for each unique vertex
        vertex_normals: Dict[Tuple[float, float, float], List[glm.vec3]] = {}
        
        # First pass: Collect face normals for each unique vertex
        for i in range(0, len(floatList), 9):
            v1 = glm.vec3(floatList[i], floatList[i+1], floatList[i+2])
            v2 = glm.vec3(floatList[i+3], floatList[i+4], floatList[i+5])
            v3 = glm.vec3(floatList[i+6], floatList[i+7], floatList[i+8])
            
            # Calculate face normal
            face_normal = glm.normalize(glm.cross(v2 - v1, v3 - v1))
            
            # Collect face normals for each vertex
            vertex_key1 = (v1.x, v1.y, v1.z)
            vertex_key2 = (v2.x, v2.y, v2.z)
            vertex_key3 = (v3.x, v3.y, v3.z)
            
            vertex_normals.setdefault(vertex_key1, []).append(face_normal)
            vertex_normals.setdefault(vertex_key2, []).append(face_normal)
            vertex_normals.setdefault(vertex_key3, []).append(face_normal)
        
        # Prepare vertex list with smooth normals
        vertexList = []
        
        # Second pass: Calculate smooth vertex normals and create vertex list
        for i in range(0, len(floatList), 9):
            v1 = glm.vec3(floatList[i], floatList[i+1], floatList[i+2])
            v2 = glm.vec3(floatList[i+3], floatList[i+4], floatList[i+5])
            v3 = glm.vec3(floatList[i+6], floatList[i+7], floatList[i+8])
            
            # Compute smooth vertex normals by averaging adjacent face normals
            v1_normal = glm.normalize(sum(vertex_normals[(v1.x, v1.y, v1.z)], glm.vec3(0, 0, 0)))
            v2_normal = glm.normalize(sum(vertex_normals[(v2.x, v2.y, v2.z)], glm.vec3(0, 0, 0)))
            v3_normal = glm.normalize(sum(vertex_normals[(v3.x, v3.y, v3.z)], glm.vec3(0, 0, 0)))
            
            # Add vertices with smooth normals
            for vertex, normal in [(v1, v1_normal), (v2, v2_normal), (v3, v3_normal)]:
                vertexList.extend([
                    vertex.x, vertex.y, vertex.z,  # Position
                    normal.x, normal.y, normal.z,  # Smooth Normal
                    self.color.x, self.color.y, self.color.z  # Color
                ])
        
        self.vertices : glm.array= glm.array(glm.float32, *vertexList)
        super().__init__(shader, self.vertices, model)
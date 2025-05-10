import ctypes
from OpenGL.GL import *
import glm
from .meshwire import MeshWire
from util import Shader
from typing import List

class TetrahedronWire(MeshWire):
    def __init__(self, 
                 shader: Shader, 
                 vertexFile: str, 
                 model: glm.mat4 = glm.mat4(1.0),
                 color: glm.vec3 = glm.vec3(0.31, 0.5, 1.0)):
        """
        Create a wireframe tetrahedron from a vertex file
        
        :param shader: Shader to use for rendering
        :param vertexFile: Path to file containing vertex coordinates
        :param model: Model transformation matrix
        :param color: Color of the wireframe
        """
        # Read vertices from file
        floatList: List[float] = []
        
        with open(vertexFile, 'r') as fin:
            floatList.extend(map(float, fin.read().split()))
        
        # Ensure the file contains vertices
        assert len(floatList) % 3 == 0, \
               'vertexFile should contain 3n floats, ' \
               'each three floats denote a vertex (x, y, z)'
        
        # Create vertices array with full vertex information
        vertices_with_attributes = []
        for i in range(0, len(floatList), 3):
            # Position
            vertices_with_attributes.extend([
                floatList[i], floatList[i+1], floatList[i+2],  # Position
                0, 0, 1,  # Normal (placeholder)
                color.x, color.y, color.z  # Color
            ])
        
        # Convert to glm array
        vertices = glm.array(glm.float32, *vertices_with_attributes)
        
        # Define tetrahedron edges 
        # This assumes vertices are in a specific order
        edges = [
            # Edges connecting vertices
            (0, 1), (0, 2), (0, 3),  # Edges from first vertex
            (1, 2), (1, 3),           # Edges from second vertex
            (2, 3)                 # Remaining edge 
        ]
        
        # Call parent constructor with vertices and edges
        super().__init__(
            shader=shader, 
            vertices=vertices, 
            edges=edges,
            model=model,
            color=color,
            render_mode='wireframe'
        )
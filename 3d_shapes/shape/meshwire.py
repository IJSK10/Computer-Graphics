import copy
import ctypes
from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader
from typing import List, Tuple

class MeshWire(GLShape, Renderable):
    def __init__(self, 
                 shader: Shader, 
                 vertices: glm.array, 
                 edges: List[Tuple[int, int]] = None,
                 model: glm.mat4 = glm.mat4(1.0),
                 render_mode: str = "fill",
                 color: glm.vec3 = glm.vec3(0.2, 0.7, 0.6)):
        """
        Initialize a wireframe mesh with more flexible vertex and edge handling
        
        :param shader: Shader to use for rendering
        :param vertices: glm array of vertices (position, normal, color)
        :param edges: Optional list of edge connections as (start_vertex_index, end_vertex_index)
        :param model: Model transformation matrix
        :param render_mode: Rendering mode (fill, wireframe, point)
        :param color: Default color for wireframe edges
        """
        # Validate vertices input
        assert vertices.element_type == glm.float32, \
               'vertices should be glm.array of dtype glm.float32'
        assert vertices.length % 9 == 0, \
               'Each 9 floats should represent a vertex (pos, normal, color)'
        
        super().__init__(shader, model)
        
        # Extract unique vertices
        unique_vertices = []
        for i in range(0, vertices.length, 9):
            vertex = [
                vertices[i], 
                vertices[i+1], 
                vertices[i+2]
            ]
            if vertex not in unique_vertices:
                unique_vertices.append(vertex)
        
        # Generate edges if not provided
        if edges is None:
            # Default to connecting all unique vertices
            edges = []
            for i in range(len(unique_vertices)):
                for j in range(i+1, len(unique_vertices)):
                    edges.append((i, j))
        
        # Create wireframe vertices
        wireframe_vertices = []
        for edge in edges:
            v1 = unique_vertices[edge[0]]
            v2 = unique_vertices[edge[1]]
            
            # First vertex of the edge
            wireframe_vertices.extend([
                v1[0], v1[1], v1[2],  # Position
                0, 0, 1,  # Normal (placeholder)
                color.x, color.y, color.z  # Color
            ])
            
            # Second vertex of the edge
            wireframe_vertices.extend([
                v2[0], v2[1], v2[2],  # Position
                0, 0, 1,  # Normal (placeholder)
                color.x, color.y, color.z  # Color
            ])
        
        # Convert back to glm array
        self.vertices = glm.array(glm.float32, *wireframe_vertices)
        
        # Set render mode
        self.render_mode = render_mode
        
        # Vertex Array Object and Buffer Object setup
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # Vertex coordinate attribute array
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 
                              9 * glm.sizeof(glm.float32), None)
        
        # Normal vertex attribute array
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 
                              9 * glm.sizeof(glm.float32),
                              ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
        
        # Vertex color attribute array
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 
                              9 * glm.sizeof(glm.float32),
                              ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
        
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,
                     self.vertices.ptr,
                     GL_STATIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
    def render(self, timeElapsedSinceLastFrame: int) -> None:
        """
        Render the wireframe mesh
        
        :param timeElapsedSinceLastFrame: Elapsed time (unused, but kept for interface compatibility)
        :param render_mode: Optional override for rendering mode
        """
        # Use provided render mode or fall back to instance render mode
        
        # Set polygon mode based on render_mode
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        draw_mode = GL_LINES
        
        self.shader.use()
        self.shader.setMat4("model", self.model)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # Draw the wireframe
        glDrawArrays(draw_mode,
                    0,                          # start from index 0 in current VBO
                    self.vertices.length // 9)  # draw these number of vertex attributes
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        # Reset to default fill mode to prevent affecting other rendering
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
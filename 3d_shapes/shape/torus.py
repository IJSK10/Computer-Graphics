import copy
import ctypes
from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader

class Torus(GLShape, Renderable):
    def __init__(self, 
                 shader: Shader, 
                 center: glm.vec3, 
                 major_radius: float,
                 minor_radius: float,
                 color: glm.vec3, 
                 model: glm.mat4 = glm.mat4(1.0)):
        
        super().__init__(shader, model)
        self.center: glm.vec3 = copy.deepcopy(center)
        self.color: glm.vec3 = copy.deepcopy(color)
        self.major_radius: float = major_radius
        self.minor_radius: float = minor_radius
        self.dummy: glm.array = glm.array(glm.float32, 0.0)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Placeholder attribute array "layout (position = 0) in float null"
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,                            
                              1,                            
                              GL_FLOAT,                     
                              GL_FALSE,                     
                              glm.sizeof(glm.float32),      
                              None)                         
        glBufferData(GL_ARRAY_BUFFER,
                     self.dummy.nbytes,
                     self.dummy.ptr,
                     GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
    def render(self, timeElapsedSinceLastFrame: int) -> None:
        self.shader.use()
        self.shader.setMat4('model', self.model)
        self.shader.setVec3('center', self.center)
        self.shader.setFloat('majorRadius', self.major_radius)
        self.shader.setFloat('minorRadius', self.minor_radius)
        self.shader.setVec3('color', self.color)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glPatchParameteri(GL_PATCH_VERTICES, 1)
        glDrawArrays(GL_PATCHES, 0, 1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
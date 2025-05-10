import copy

from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm

from .window import Window
from shape import Line, Mesh, Renderable, Sphere, Tetrahedron, Cube, Octahedron, CubeWire, TetrahedronWire, Icosahedron, Smooth, Cone, Cylinder, Torus, OctahedronWire, Ellipsoid, TetrahedronColor, ConeWire, CylinderWire, SphereWire, TorusWire, EllipsoidWire, IcosahedronWire
from util import Camera, Shader


class App(Window):
    def __init__(self):
        self.windowName: str = 'hw3'
        self.windowWidth: int = 1000
        self.windowHeight: int = 1000
        super().__init__(self.windowWidth, self.windowHeight, self.windowName)
        self.currentmode : str = "test"
        self.subd : int = 0
        self.pressingshift: bool = False
        
        # GLFW boilerplate.
        glfwSetWindowUserPointer(self.window, self)
        glfwSetCursorPosCallback(self.window, self.__cursorPosCallback)
        glfwSetFramebufferSizeCallback(self.window, self.__framebufferSizeCallback)
        glfwSetKeyCallback(self.window, self.__keyCallback)
        glfwSetMouseButtonCallback(self.window, self.__mouseButtonCallback)
        glfwSetScrollCallback(self.window, self.__scrollCallback)

        # Global OpenGL pipeline settings.
        glViewport(0, 0, self.windowWidth, self.windowHeight)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(2.0)
        glPointSize(1.0)
        
        # Only for 3D scenes!
        # Also remember to clear GL_DEPTH_BUFFER_BIT, or OpenGL won't display anything...
        glEnable(GL_DEPTH_TEST)
        
        # Program context.
        
        # Shaders.
        self.lineShader: Shader = \
            Shader(vert='shader/line.vert.glsl', 
                   tesc=None,
                   tese=None,
                   frag='shader/line.frag.glsl')
                   
        self.meshShader: Shader = \
            Shader(vert='shader/mesh.vert.glsl',
                   tesc=None,
                   tese=None,
                   frag='shader/phong.frag.glsl')
                   
        self.sphereShader: Shader = \
            Shader(vert='shader/sphere.vert.glsl',
                   tesc='shader/sphere.tesc.glsl',
                   tese='shader/sphere.tese.glsl',
                   frag='shader/phong.frag.glsl')
        
        self.coneShader: Shader = \
            Shader(vert='shader/sphere.vert.glsl',
                   tesc='shader/cone.tesc.glsl',
                   tese='shader/cone.tese.glsl',
                   frag='shader/phong.frag.glsl')
        
        
        self.cylinderShader: Shader = \
            Shader(vert='shader/sphere.vert.glsl',
                   tesc='shader/cylinder.tesc.glsl',
                   tese='shader/cylinder.tese.glsl',
                   frag='shader/phong.frag.glsl')
        
        self.torusShader: Shader = \
            Shader(vert='shader/sphere.vert.glsl',
                   tesc='shader/torus.tesc.glsl',
                   tese='shader/torus.tese.glsl',
                   frag='shader/phong.frag.glsl')
        

        # Objects to render.
        self.shapes: list[Renderable] = []
        

        self.xyz=Line(
                self.lineShader, 
                glm.array(
                    # dtype
                    glm.float32, 
                    # pos (x y z)   # color (r g b)
                    0.0, 0.0, 0.0,  1.0, 0.0, 0.0,
                    3.0, 0.0, 0.0,  1.0, 0.0, 0.0,
                    0.0, 0.0, 0.0,  0.0, 1.0, 0.0,
                    0.0, 3.0, 0.0,  0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0,  0.0, 0.0, 1.0,
                    0.0, 0.0, 3.0,  0.0, 0.0, 1.0,
                ),
                glm.mat4(1.0)
            )

        # self.shapes.append(
        #     Cube
        # )
        
        # self.shapes.append(
        #     Mesh(
        #         self.meshShader,
        #         glm.array(
        #             # dtype
        #             glm.float32,
        #             # pos (x y z)        # normal (x y z)   # color (r g b)
        #             -0.5,  -0.5,  0.0,   0.0, 0.0, 1.0,     1.0, 0.0, 0.0,
        #              0.5,  -0.5,  0.0,   0.0, 0.0, 1.0,     0.0, 1.0, 0.0,
        #              0.0,   0.5,  0.0,   0.0, 0.0, 1.0,     0.0, 0.0, 1.0,
        #         ),
        #         glm.rotate(
        #             glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0)),
        #             glm.radians(45.0), glm.vec3(0.0, 1.0, 0.0))
        #     )
        # )
    
        
        # Viewing
        self.camera: Camera = Camera(glm.vec3(0.0, 0.0, 10.0))
        self.view: glm.mat4 = glm.mat4(1.0)
        self.projection: glm.mat4 = glm.mat4(1.0)

        self.lightColor: glm.vec3 = glm.vec3(1.0, 1.0, 1.0)
        self.lightPos: glm.vec3 = glm.vec3(10.0, -10.0, 10.0)

        # Frontend GUI
        self.timeElapsedSinceLastFrame: float = 0.0
        self.lastFrameTimeStamp: float = 0.0
        self.mousePressed: bool = False
        self.mousePos: glm.dvec2 = glm.dvec2(0.0, 0.0)
        
        self.debugMousePos: bool = False
        
        # Note lastMouseLeftClickPos is different from lastMouseLeftPressPos.
        # If you press left button (and hold it there) and move the mouse,
        # lastMouseLeftPressPos gets updated to the current mouse position
        # (while lastMouseLeftClickPos, if there is one, remains the original value).
        self.lastMouseLeftClickPos: glm.dvec2 = glm.dvec2(0.0, 0.0)
        self.lastMouseLeftPressPos: glm.dvec2 = glm.dvec2(0.0, 0.0)
        
    def run(self) -> None:
        while not glfwWindowShouldClose(self.window):
            # Per-frame logic
            self.__perFrameTimeLogic(self.window)
            self.__processKeyInput(self.window)

            # Send render commands to OpenGL server
            glClearColor(0.2, 0.3, 0.3, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.__render()

            # Check and call events and swap the buffers
            glfwSwapBuffers(self.window)
            glfwPollEvents()
    
    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)

        app.mousePos.x = xpos;
        app.mousePos.y = app.windowHeight - ypos;
        
        if app.debugMousePos:
            print(f'cursor @ {app.mousePos}')

        if app.mousePressed:
            # Note: Must calculate offset first, then update lastMouseLeftPressPos.
            # Also MUST explivitly use copy here!
            # C++: copy assign is copy; Python: it's reference!
            offset: glm.dvec2 = app.mousePos - app.lastMouseLeftPressPos

            if app.debugMousePos:
                print(f'mouse drag offset {offset}')
            
            app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)
            app.camera.processMouseMovement(offset.x, offset.y)
    
    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)
    
    @staticmethod
    def __keyCallback(window: GLFWwindow, key: int, scancode: int, action: int, mods: int) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if action == GLFW_PRESS:
            if key == GLFW_KEY_1:
                app.currentmode="qn1"
                app.shapes.clear()
            if app.currentmode=="qn1" and key==GLFW_KEY_F1:
                app.shapes.clear()
                app.shapes.append(TetrahedronWire(
                app.meshShader,
                'var/tetrahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, 0.0))
                ))
                app.shapes.append(CubeWire(
                app.meshShader,
                'var/cube.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
                ))
                app.shapes.append(OctahedronWire(
                app.meshShader,
                'var/octahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0))
                ))
            
            if app.currentmode=="qn1" and key==GLFW_KEY_F2:
                app.shapes.clear()
                app.shapes.append(Tetrahedron(
                app.meshShader,
                'var/tetrahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, 0.0))
                ))
                app.shapes.append(Cube(
                app.meshShader,
                'var/cube.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
                ))
                app.shapes.append(Octahedron(
                app.meshShader,
                'var/octahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0))
                ))
            
            if app.currentmode=="qn1" and key==GLFW_KEY_F4:
                app.shapes.clear()
                app.shapes.append(Smooth(
                app.meshShader,
                'var/tetrahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, 0.0))
                ))
                app.shapes.append(Smooth(
                app.meshShader,
                'var/cube.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
                ))
                app.shapes.append(Smooth(
                app.meshShader,
                'var/octahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0))
                ))
            
            if app.currentmode=="qn1" and key==GLFW_KEY_F3:
                app.shapes.clear()
                app.shapes.append(TetrahedronColor(
                app.meshShader,
                'var/tetrahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, 0.0))
                ))
                app.shapes.append(TetrahedronColor(
                app.meshShader,
                'var/cube.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
                ))
                app.shapes.append(TetrahedronColor(
                app.meshShader,
                'var/octahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0))
                ))
            
            if key == GLFW_KEY_2:
                app.currentmode="qn2"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Icosahedron(
                app.meshShader,
                'var/icosahedron.txt',
                app.subd,
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))

            if app.currentmode=="qn2" and key==GLFW_KEY_F1:
                app.currentmode="qn2"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(IcosahedronWire(
                app.meshShader,
                'var/icosahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if app.currentmode=="qn2" and key==GLFW_KEY_F2:
                app.currentmode="qn2"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Icosahedron(
                app.meshShader,
                'var/icosahedron.txt',
                app.subd,
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if app.currentmode=="qn2" and key==GLFW_KEY_F4:
                app.currentmode="qn2"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Smooth(
                app.meshShader,
                'var/icosahedron.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if key == GLFW_KEY_3:
                app.currentmode="qn3"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Ellipsoid(
                app.meshShader,
                'var/ellipsoid.txt',
                app.subd,
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if app.currentmode=="qn3" and key==GLFW_KEY_F1:
                app.currentmode="qn3"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(EllipsoidWire(
                app.meshShader,
                'var/ellipsoid.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if app.currentmode=="qn3" and key==GLFW_KEY_F2:
                app.currentmode="qn3"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Ellipsoid(
                app.meshShader,
                'var/ellipsoid.txt',
                app.subd,
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            
            if app.currentmode=="qn3" and key==GLFW_KEY_F4:
                app.currentmode="qn3"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Smooth(
                app.meshShader,
                'var/ellipsoid.txt',
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                ))
            

            if key == GLFW_KEY_4:
                app.currentmode="qn4"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Cylinder(
                app.cylinderShader,
                glm.vec3(-2.5, 0.0, 0.0),  
                2.0,                       
                1.0,                       
                glm.vec3(1.0, 0.0, 1.0),   
                glm.mat4(1.0)
                ))
                app.shapes.append(
                Sphere(
                    app.sphereShader,
                    glm.vec3(0.0, 0.0, 0.0),   
                    1.0,                       
                    glm.vec3(0.2, 0.5, 0.51),  
                    glm.mat4(1.0)
                ))
                app.shapes.append(
                Cone(
                    app.coneShader,
                    glm.vec3(2.5, 0.0, 0.0),  
                    2.0,                       
                    1.0,                       
                    glm.vec3(0.5, 0.2, 0.2),   
                    glm.mat4(1.0)
                ))
            
            if app.currentmode=="qn4" and key==GLFW_KEY_F1:
                app.currentmode="qn4"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(CylinderWire(
                app.cylinderShader,
                glm.vec3(-2.5, 0.0, 0.0),  
                2.0,                       
                1.0,                       
                glm.vec3(1.0, 0.0, 1.0),   
                glm.mat4(1.0)
                ))
                app.shapes.append(
                SphereWire(
                    app.sphereShader,
                    glm.vec3(0.0, 0.0, 0.0),   
                    1.0,                       
                    glm.vec3(0.2, 0.5, 0.51),  
                    glm.mat4(1.0)
                ))
                app.shapes.append(
                ConeWire(
                    app.coneShader,
                    glm.vec3(2.5, 0.0, 0.0),  
                    2.0,                       
                    1.0,                       
                    glm.vec3(0.5, 0.2, 0.2),   
                    glm.mat4(1.0)
                ))
            
            if app.currentmode=="qn4" and key==GLFW_KEY_F2:
                app.currentmode="qn4"
                app.subd = 0
                app.shapes.clear()
                app.shapes.append(Cylinder(
                app.cylinderShader,
                glm.vec3(-2.5, 0.0, 0.0),  
                2.0,                       
                1.0,                       
                glm.vec3(1.0, 0.0, 1.0),   
                glm.mat4(1.0)
                ))
                app.shapes.append(
                Sphere(
                    app.sphereShader,
                    glm.vec3(0.0, 0.0, 0.0),   
                    1.0,                       
                    glm.vec3(0.2, 0.5, 0.51),  
                    glm.mat4(1.0)
                ))
                app.shapes.append(
                Cone(
                    app.coneShader,
                    glm.vec3(2.5, 0.0, 0.0),  
                    2.0,                       
                    1.0,                       
                    glm.vec3(0.5, 0.2, 0.2),   
                    glm.mat4(1.0)
                ))


            if key == GLFW_KEY_X:
                if app.xyz in app.shapes:
                    app.shapes.remove(app.xyz)
                else:
                    app.shapes.append(app.xyz)

            if key == GLFW_KEY_5:
                app.currentmode="qn5"
                app.subd = 0
                app.shapes.clear()
                app.torusShader.use()
                app.torusShader.setInt('tessLevel', 15)
                app.shapes.append(
                    Torus(
                    app.torusShader,
                    glm.vec3(0.0, 0.0, 0.0),  
                    1.0,                       
                    0.2,                       
                    glm.vec3(0.3, 0.6, 0.4)    
                ))
            
            if app.currentmode=="qn5" and key==GLFW_KEY_F1:
                print("yes")
                app.currentmode="qn5"
                app.subd = 0
                app.shapes.clear()
                app.torusShader.use()
                app.torusShader.setInt('tessLevel', 15)
                app.shapes.append(
                    TorusWire(
                    app.torusShader,
                    glm.vec3(0.0, 0.0, 0.0),  
                    1.0,                       
                    0.2,                       
                    glm.vec3(0.3, 0.6, 0.4)    
                ))
            
            if app.currentmode=="qn5" and key==GLFW_KEY_F2:
                app.currentmode="qn5"
                app.subd = 0
                app.shapes.clear()
                app.torusShader.use()
                app.torusShader.setInt('tessLevel', 15)
                app.shapes.append(
                    Torus(
                    app.torusShader,
                    glm.vec3(0.0, 0.0, 0.0),  
                    1.0,                       
                    0.2,                       
                    glm.vec3(0.3, 0.6, 0.4)    
                ))

            
            if key == GLFW_KEY_EQUAL and app.currentmode=="qn2" and app.pressingshift==True:
                if app.subd<2:
                    app.subd = app.subd+1
                    app.shapes.clear()
                    app.shapes.append(Icosahedron(
                    app.meshShader,
                    'var/icosahedron.txt',
                    app.subd,
                    glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                    ))
            
            if key == GLFW_KEY_EQUAL and app.currentmode=="qn3" and app.pressingshift==True:
                if app.subd<2:
                    app.subd = app.subd+1
                    app.shapes.clear()
                    app.shapes.append(Ellipsoid(
                    app.meshShader,
                    'var/ellipsoid.txt',
                    app.subd,
                    glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                    ))
            
            if key == GLFW_KEY_EQUAL and app.currentmode=="qn5" and app.pressingshift==True:
                if app.subd<2:
                    app.subd = app.subd+1
                    app.shapes.clear()
                    app.torusShader.use()
                    if app.subd==1:
                        app.torusShader.setInt('tessLevel', 30)
                    if app.subd==2:
                        app.torusShader.setInt('tessLevel', 60)
                    app.shapes.append(
                        Torus(
                        app.torusShader,
                        glm.vec3(0.0, 0.0, 0.0),  # center
                        1.0,                       # major radius
                        0.2,                       # minor radius
                        glm.vec3(0.3, 0.6, 0.4)    # different color
                    ))

            
            if key==GLFW_KEY_LEFT_SHIFT or key==GLFW_KEY_RIGHT_SHIFT:
                app.pressingshift=True

        if action == GLFW_RELEASE:
            if key==GLFW_KEY_LEFT_SHIFT or key==GLFW_KEY_RIGHT_SHIFT:
                app.pressingshift=False

            

    
    @staticmethod
    def __mouseButtonCallback(window: GLFWwindow, button: int, action: int, mods: int) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                app.mousePressed = True
                
                # NOTE: MUST explivitly use copy here!
                # C++: copy assign is copy; Python: it's reference!
                app.lastMouseLeftClickPos = copy.deepcopy(app.mousePos)
                app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)
                
                if app.debugMousePos:
                    print(f'mouseLeftPress @ {app.mousePos}')
                
            elif action == GLFW_RELEASE:
                app.mousePressed = False

                if app.debugMousePos:
                    print(f'mouseLeftRelease @ {app.mousePos}')
    
    @staticmethod
    def __scrollCallback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:
        app: App = glfwGetWindowUserPointer(window)
        app.camera.processMouseScroll(yoffset)
    
    @staticmethod
    def __perFrameTimeLogic(window: GLFWwindow) -> None:
        app: App = glfwGetWindowUserPointer(window);

        currentFrame: float = glfwGetTime();
        app.timeElapsedSinceLastFrame = currentFrame - app.lastFrameTimeStamp;
        app.lastFrameTimeStamp = currentFrame;
    
    @staticmethod
    def __processKeyInput(window: GLFWwindow) -> None:
        # Camera control
        app: App = glfwGetWindowUserPointer(window)

        if glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kLeft, app.timeElapsedSinceLastFrame)

        if glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kRight, app.timeElapsedSinceLastFrame)

        if glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kBackWard, app.timeElapsedSinceLastFrame)

        if glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kForward, app.timeElapsedSinceLastFrame)

        if glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kUp, app.timeElapsedSinceLastFrame)

        if glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS:
            app.camera.processKeyboard(Camera.Movement.kDown, app.timeElapsedSinceLastFrame)
    
    def __render(self) -> None:
        t: float = self.timeElapsedSinceLastFrame

        # Update shader uniforms.
        self.view = self.camera.getViewMatrix()
        self.projection = glm.perspective(glm.radians(self.camera.zoom),
                                          self.windowWidth / self.windowHeight,
                                          0.01,
                                          100.0)

        self.lineShader.use()
        self.lineShader.setMat4('view', self.view)
        self.lineShader.setMat4('projection', self.projection)
        
        self.meshShader.use()
        self.meshShader.setMat4('view', self.view)
        self.meshShader.setMat4('projection', self.projection)
        self.meshShader.setVec3('ViewPos', self.camera.position)
        self.meshShader.setVec3('lightPos', self.lightPos)
        self.meshShader.setVec3('lightColor', self.lightColor)

        self.sphereShader.use()
        self.sphereShader.setMat4('view', self.view)
        self.sphereShader.setMat4('projection', self.projection)
        self.sphereShader.setVec3('ViewPos', self.camera.position)
        self.sphereShader.setVec3('lightPos', self.lightPos)
        self.sphereShader.setVec3('lightColor', self.lightColor)


        self.coneShader.use()
        self.coneShader.setMat4('view', self.view)
        self.coneShader.setMat4('projection', self.projection)
        self.coneShader.setVec3('ViewPos', self.camera.position)
        self.coneShader.setVec3('lightPos', self.lightPos)
        self.coneShader.setVec3('lightColor', self.lightColor)

        self.cylinderShader.use()
        self.cylinderShader.setMat4('view', self.view)
        self.cylinderShader.setMat4('projection', self.projection)
        self.cylinderShader.setVec3('ViewPos', self.camera.position)
        self.cylinderShader.setVec3('lightPos', self.lightPos)
        self.cylinderShader.setVec3('lightColor', self.lightColor)

        self.torusShader.use()
        self.torusShader.setMat4('view', self.view)
        self.torusShader.setMat4('projection', self.projection)
        self.torusShader.setVec3('ViewPos', self.camera.position)
        self.torusShader.setVec3('lightPos', self.lightPos)
        self.torusShader.setVec3('lightColor', self.lightColor)

        # Render all shapes.
        for s in self.shapes:
            s.render(t)


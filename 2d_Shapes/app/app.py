import copy

from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm
import math
from .window import Window
from shape import Pixel, Renderable
from util import Shader


class App(Window):
    def __init__(self):
        self.windowName: str = 'hw1'
        self.windowWidth: int = 1000
        self.windowHeight: int = 1000
        super().__init__(self.windowWidth, self.windowHeight, self.windowName)
        
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
        glLineWidth(1.0)
        glPointSize(1.0)
        
        # Program context.
        
        # Shaders.
        self.pixelShader: Shader = \
            Shader(vert='shader/pixel.vert.glsl', 
                   tesc=None,
                   tese=None,
                   frag='shader/pixel.frag.glsl')
                   
        # Shapes.
        self.shapes: list[Renderable] = []
        self.shapes.append(Pixel(self.pixelShader))

        # Frontend GUI
        self.showPreview: bool = False
        
        self.timeElapsedSinceLastFrame: float = 0.0
        self.lastFrameTimeStamp: float = 0.0
        self.mousePressed: bool = False
        self.mousePos: glm.dvec2 = glm.dvec2(0.0, 0.0)
        
        self.debugMousePos: bool = False
        
        self.currPoints = []
        self.currentmode : str = None
        self.pressingShift : bool = False
        self.pointCaptured: bool =False
        self.rightClick : bool = False


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
            glClear(GL_COLOR_BUFFER_BIT)

            self.__render()

            # Check and call events and swap the buffers
            glfwSwapBuffers(self.window)
            glfwPollEvents()
    
    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)

        app.mousePos.x = xpos;
        app.mousePos.y = app.windowHeight - ypos;

        if app.mousePressed:
            # # Note: Must calculate offset first, then update lastMouseLeftPressPos.
            # # Also must invoke copy explicitly. 
            # # C++: copy assign is copy; Python: it's reference!
            # glm::dvec2 offset = app.mousePos - app.lastMouseLeftPressPos;
            app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)
        
        # Display a preview line which moves with the mouse cursor iff.
        # the most-recent mouse click is left click.
        # showPreview is controlled by mouseButtonCallback.
        if app.showPreview:
            pixel: Pixel = app.shapes[0]

            x0 = int(app.lastMouseLeftPressPos.x)
            y0 = int(app.lastMouseLeftPressPos.y)
            x1 = int(app.mousePos.x)
            y1 = int(app.mousePos.y)

            if app.currentmode=='qn1':
                #print("QN no 1")
                pixel.path.clear()
                App.__bresenhamLine(pixel.path, x0, y0, x1, y1);
            
            if app.currentmode ==  'qn2':
                #print('Qn no 2')
                pixel.path.clear()
                App.__drawLine(pixel.path,x0,y0,x1,y1);
            
            if app.currentmode == 'qn3':
                #print('QN no 3')
                pixel.path.clear()
                App.__drawPolygon(app,pixel.path,app.currPoints,x1,y1)
            
            if app.currentmode == 'qn4':
                #print("QN no 4")
                pixel.path.clear()
                if app.pressingShift==True:
                    App.__drawCircle(pixel.path,x0,y0,y0,y1)
                else:
                    App.__drawEllipse(pixel.path,x0,y0,abs(x0-x1),abs(y0-y1))
            
            if app.currentmode == 'qn5':
                print("qn5")

            pixel.dirty = True
    
    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)
    
    @staticmethod
    def __keyCallback(window: GLFWwindow, key: int, scancode: int, action: int, mods: int) -> None:
        app: App=glfwGetWindowUserPointer(window)

        if action == GLFW_PRESS:

            if key == GLFW_KEY_1:
                app.currentmode ='qn1'

            if key == GLFW_KEY_2:
                app.currentmode = 'qn2' 
            
            if key == GLFW_KEY_3:
                app.currentmode = 'qn3'

            if key == GLFW_KEY_4:
                app.currentmode = 'qn4'

            if key == GLFW_KEY_5:
                app.currentmode='qn5'
                with open("etc/config.txt", "r") as file:
                    values = file.readline().split()
                a, b, c, d = map(float, values)

                app.showPreview = True
                pixel: Pixel = app.shapes[0]

                pixel.path.clear()

                if a==0:
                    App.__drawQuadPoly(pixel.path,b,c,d);
                else:
                    App.__drawCubicPoly(pixel.path,a,b,c,d);

                app.showPreview=False
                pixel.dirty=True
            
            if key == GLFW_KEY_F:
                if app.currentmode=='qn3':
                    app.showPreview = True
                    pixel: Pixel = app.shapes[0]
                    pixel.path.clear()

                    App.__fillWithIntPoly(pixel.path,app.currPoints)

                    app.showPreview=False
                    pixel.dirty=True

                
            if key==GLFW_KEY_LEFT_SHIFT:
                print("Pressing shift")
                app.pressingShift = True
        
        if action ==GLFW_RELEASE:

            if key==GLFW_KEY_LEFT_SHIFT:
                print("Released shift")
                app.pressingShift = False



        
    @staticmethod
    def __mouseButtonCallback(window: GLFWwindow, button: int, action: int, mods: int) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                app.mousePressed = True
                app.lastMouseLeftClickPos = copy.deepcopy(app.mousePos)
                app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)
                if app.currentmode == 'qn3':
                    if app.rightClick == True:
                        app.currPoints.clear()
                        app.rightClick=False
                    app.currPoints.append((int(app.lastMouseLeftPressPos.x),int(app.lastMouseLeftPressPos.y)))
                
                if app.debugMousePos:
                    print(f'mouseLeftPress @ {app.mousePos}')

            elif action == GLFW_RELEASE:
                app.mousePressed = False
                app.showPreview = True
                if app.debugMousePos:
                    print(f'mouseLeftRelease @ {app.mousePos}')
        
        elif button == GLFW_MOUSE_BUTTON_RIGHT:
            if action == GLFW_RELEASE:
                lastMouseRightPressPos = copy.deepcopy(app.mousePos)
                app.showPreview = False
                if app.currentmode=='qn3':
                    #print(app.currPoints)
                    if app.rightClick==False:
                        app.currPoints.append((int(lastMouseRightPressPos.x),int(lastMouseRightPressPos.y)))
                app.rightClick=True
    
    @staticmethod
    def __scrollCallback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:
        pass
    
    @staticmethod
    def __perFrameTimeLogic(window: GLFWwindow) -> None:
        app: App = glfwGetWindowUserPointer(window);

        currentFrame: float = glfwGetTime();
        app.timeElapsedSinceLastFrame = currentFrame - app.lastFrameTimeStamp;
        app.lastFrameTimeStamp = currentFrame;
    
    @staticmethod
    def __processKeyInput(window: GLFWwindow) -> None:
        pass
        
    @staticmethod
    def __bresenhamLine(path: list[glm.float32], x0: int, y0: int, x1: int, y1: int) -> None:
        """
        Bresenham line-drawing algorithm for line (x0, y0) -> (x1, y1) in screen space,
        given that its slope m satisfies 0.0 <= m <= 1.0 and that (x0, y0) is the start position.
        All pixels on this line are appended to path 
        (a list of glm.float32s, each five glm.float32s constitute a pixel (x y) (r g b).)
        P.S. Returning a view of path is more Pythonic,
        however, we still modify the argument for consistency with the C++ version...
        """

        if x0>x1:
            x0,x1=x1,x0
            y0,y1=y1,y0
        dx: int = abs(x1 - x0)
        dy: int = abs(y1 - y0)
        p: int = 2 * dy - dx
        twoDy: int = 2 * dy
        twoDyMinusDx: int = 2 * (dy - dx)

        x: int = x0
        y: int = y0

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        while x < x1:
            x += 1

            if p < 0:
                p += twoDy
            else:
                y += 1
                p += twoDyMinusDx

            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    @staticmethod
    def __drawLine(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:
        dx : int = x1-x0
        dy : int = y1-y0
        if dx == 0:
            App.__lV(path, x0, y0, x1, y1);
        elif dy == 0:
            App.__lH(path, x0, y0, x1, y1);
        else:
            m :float =dy/dx
            if 0>m>-1:
                App.__lsztno(path,x0,y0,x1,y1);
            elif 0<m<1:
                App.__bresenhamLine(path,x0,y0,x1,y1);
            elif m>=1:
                App.__lsmto(path,x0,y0,x1,y1);
            elif m<=-1:
                App.__lsltno(path,x0,y0,x1,y1);
            else:
                App.__bresenhamLine(path,x0,y0,x1,y1);
    
    @staticmethod
    def __lV(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:
        if y0>y1:
            y0,y1=y1,y0
        x : int =x0
        y : int =y0
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)


        while y<y1:
            y+=1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)
    
    @staticmethod
    def __lH(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:

        if x0>x1:
            x0,x1=x1,x0
        x : int =x0
        y : int =y0
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)


        while x<x1:
            x+=1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    @staticmethod
    def __lsztno(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:
        if x0>x1:
            x0,x1=x1,x0
            y0,y1=y1,y0
        dx : int = x1-x0
        dy : int = y1-y0
        d : int =dy+dx*(1/2)
        inc_E: int =dy
        inc_NE : int =dy+dx
        x : int =x0
        y : int =y0

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)


        while x<x1:
            x+=1
            
            if d>0:
                d=d+inc_E
            else:
                d=d+inc_NE
                y=y-1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    @staticmethod
    def __lsmto(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:

        if y0>y1:
            x0,x1=x1,x0
            y0,y1=y1,y0
        dx : int = x1-x0
        dy : int = y1-y0
        d : int =dx-dy*(1/2)
        inc_E: int =dx
        inc_NE : int =dx-dy
        x : int =x0
        y : int =y0

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)


        while y<y1:
            y+=1
            
            if d<0:
                d=d+inc_E
            else:
                d=d+inc_NE
                x=x+1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    @staticmethod
    def __lsltno(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:
        if y1>y0:
            x0,x1=x1,x0
            y0,y1=y1,y0
        dx : int = x1-x0
        dy : int = y1-y0
        d : int  = dx+ dy/2
        inc_E: int =dx
        inc_NE : int =dx+dy
        x : int =x0
        y : int =y0

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)


        while y>=y1:
            y=y-1
            if d<0:
                d=d+inc_E
            else:
                d=d+inc_NE
                x=x+1

            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __drawPolygon(app,path:list[glm.float32],pts : list[tuple[int,int]],fx1:int,fx2:int) -> None:
        if pts:
            x0 : int = 0
            y0 : int = 0
            x1 : int = pts[0][0]
            y1 : int = pts[0][1]
            for i in range(1,len(pts)):
                x0,y0=x1,y1
                x1,y1=pts[i]
                App.__drawLine(path, x0, y0, x1, y1)
            App.__drawLine(path,x1,y1,fx1,fx2)
            if app.pressingShift==True:
                App.__drawLine(path,fx1,fx2,pts[0][0],pts[0][1])
        if not pts:
            print("List is empty")

    @staticmethod
    def __drawCircle(path:list[glm.float32],x0:int,y0:int,x1:int,y1:int) -> None:
        r : int = int(math.dist([x0,y0],[x1,y1]))
        cx : int = 0
        cy : int = r
        p : int = 1-r

        App.__circlePlotPoints(path,x0,y0,cx,cy)
        while cx < cy:
            cx+=1
            if p<0 :
                p=p+2*cx+1
            else:
                cy-=1
                p=p+2*(cx-cy)+1
            App.__circlePlotPoints(path,x0,y0,cx,cy)

    @staticmethod
    def __circlePlotPoints (path:list[glm.float32],x1:int,y1:int,cx:int,cy:int) -> None:
        temp=[(1,1),(-1,1),(1,-1),(-1,-1)]
        for i in range(0,len(temp)):
            path.append(x1+temp[i][0]*cx)
            path.append(y1+temp[i][1]*cy)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)
        for i in range(0,len(temp)):
            path.append(x1+temp[i][0]*cy)
            path.append(y1+temp[i][1]*cx)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    @staticmethod
    def __drawEllipse(path:list[glm.float32],xc:int,yc:int,x1:int,y1:int) -> None:
        rx2 : int = x1 * x1
        ry2 : int = y1 * y1
        tworx2 : int = 2* rx2
        twory2 : int = 2* ry2
        p : int = 0
        x : int =0
        y : int = y1
        px : int = 0
        py : int = tworx2 * y
        

        App.__ellipsePlotPoints(path,x,y,xc,yc)

        p = round(ry2 - (rx2* y1) + (0.25 * rx2))
        while px < py:
            x+=1
            px+=twory2
            if p<0 :
                p=p+ry2+px
            else:
                y-=1
                py-=tworx2
                p=p+ry2+px-py
            App.__ellipsePlotPoints(path,x,y,xc,yc)
        p=round(ry2*(x+0.5)*(x+0.5) + rx2*(y-1)*(y-1) - rx2*ry2)
        while y>0:
            y-=1
            py-=tworx2
            if p>0:
                p+=rx2-py
            else:
                x+=1
                px+=twory2
                p+=rx2-py+px
            App.__ellipsePlotPoints(path,x,y,xc,yc)


    @staticmethod
    def __ellipsePlotPoints (path:list[glm.float32],x1:int,y1:int,xc:int,yc:int) -> None:
        temp=[(1,1),(-1,1),(1,-1),(-1,-1)]
        for i in range(0,len(temp)):
            path.append(xc+temp[i][0]*x1)
            path.append(yc+temp[i][1]*y1)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __drawQuadPoly(path: list[glm.float32],a : float, b:float, c: float) -> None:
        tpt: set[int] = {0,1000}
        tpt.add(App.__slopequad(0,a,b))
        tpt.add(App.__slopequad(1,a,b))
        tpt.add(App.__slopequad(-1,a,b))

        pts=list(tpt)
        pts.sort()

        for i in range(0,len(pts)-1):
            h : int = (pts[i+1]+pts[i])/2
            m=2*a*h + b
            print(m)
            if m>1:
                App.__quadmmo(path,pts[i],pts[i+1],a,b,c)
            elif m<-1:
                App.__quadmlno(path,pts[i],pts[i+1],a,b,c)
            elif m>0:
                App.__quadmon(path,pts[i],pts[i+1],a,b,c)
            elif m<0:
                App.__quadlon(path,pts[i],pts[i+1],a,b,c)


    def __slopequad(y: int ,a:float , b: float) -> int :
        x=(y-b)/(2*a)
        return int(x)
    
    def __quadmmo(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float) -> None:        
        print("Slope more than one")
        y : int=a*(x**2)+b*(x)+c
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y+1) - a* ((x+1/2)**2) - b*(x+1/2) -c
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-100)):
            y=y+1
            if p<0:
                p+=1
            else:
                p+=1-2*a*x-2*a-b
                x=x+1
            

            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __quadmlno(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float) -> None:        
        y : int=a*(x**2)+b*(x)+c
        print("slope less than-1")  
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y-1) - a* ((x+1/2)**2) - b*(x+1/2) -c
        while((x< 1000) & (y<2000) & (x<=x1) & (y>0)):
            y=y-1
            if p>0:
                p+=-1
            else:
                p+=-1-2*a*x-2*a-b
                x=x+1
            
            path.append(x)
            path.append(y)
            path.append(1)
            path.append(1)
            path.append(1)
    
    def __quadmon(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float) -> None:      
        y : int=a*(x**2)+b*(x)+c
        print("slope 0 to 1")  
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y+1/2) - a* ((x+1)**2) - b*(x+1) -c
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-1000)):
            x=x+1
            if p>0:
                p+=-3*a-2*a*x-b
            else:
                p+=-3*a-2*a*x-b+1
                y=y+1
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __quadlon(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float) -> None:     
        print("slope o to -1")   
        y : int=a*(x**2)+b*(x)+c
        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y-1/2) - a* ((x+1)**2) - b*(x+1) -c
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-100)):
            x=x+1
            if p<=0:
                p+=-3*a-2*a*x-b
            else:
                p+=-3*a-2*a*x-b-1
                y=y-1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)
    
    def __drawCubicPoly(path: list[glm.float32],a : float, b:float, c: float , d:float) -> None:
        tpt: set[int] = {0,1000}
        tpt.update(App.__slopecubic(0,a,b,c))
        tpt.update(App.__slopecubic(1,a,b,c))
        tpt.update(App.__slopecubic(-1,a,b,c))

        pts=list(tpt)

        pts.sort()

        ptsy=[]
        for i in range(0,len(pts)):
            x=pts[i]
            ptsy.append(int(a*(x**3)+b*(x**2)+c*x+d))
        for i in range(0,len(pts)-1):
            h : int = (pts[i+1]+pts[i])/2
            m=3*a*(h**2)+2*b*h+c
            if m>1:
                App.__cubicmmot(path,pts[i],pts[i+1],a,b,c,d)
            elif m<-1:
                App.__cubicmlot(path,pts[i],pts[i+1],a,b,c,d)
            elif m>0:
                App.__cubicmont(path,pts[i],pts[i+1],a,b,c,d)
            elif m<0:
                App.__cubiclont(path,pts[i],pts[i+1],a,b,c,d)

    def __slopecubic(y: int ,a:float , b: float , c: float) -> set[int] :
        t1=-2*b
        t2=(4*(b**2) - 12*a*(c-y))**(1/2)
        t3=6*a

        x1=(t1+t2)/t3
        x2=(t1-t2)/t3

        s1=set()
        s1.add(int(x1.real))
        s1.add(int(x2.real))

        return s1
    
    def __cubicmmot(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float , d:float) -> None:        
        y : int=a*(x**3)+b*(x**2)+c*x+d

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y+1) - a*((x+1/2)**3) - b*((x+1/2)**2) - c*(x+1/2) - d
        while((x< 1000) & (y<2000) & (x<=x1) ):
            y=y+1
            if p<0:
                p+=1
            else:
                p+=1+a*(-3.25 - 3*((x)**2)-6*x)+b*(-2-2*x)-c
                x=x+1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __cubicmlot(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float , d:float) -> None:        
        y : int=a*(x**3)+b*(x**2)+c*x+d

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y-1) - a*((x+1/2)**3) - b*((x+1/2)**2) - c*(x+1/2) - d
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-100)):
            y=y-1
            if p>0:
                p+=-1
            else:
                p+=-1+a*(-3.25 - 3*((x)**2)-6*x)+b*(-2-2*x)-c
                x=x+1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)
    
    def __cubicmont(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float , d:float) -> None:        
        y : int=a*(x**3)+b*(x**2)+c*x+d

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y+1/2) - a*((x+1)**3) - b* ((x+1)**2) - c*(x+1) -d
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-100)):
            x=x+1
            if p>0:
                p+=a*(-7-3*(x**2)-9*x)+b*(-3-2*x)-c
            else:
                p+=a*(-7-3*(x**2)-9*x)+b*(-3-2*x)-c+1
                y=y+1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)

    def __cubiclont(path: list[glm.float32],x : int, x1 : int, a : float, b:float, c: float , d:float) -> None:        
        y : int=a*(x**3)+b*(x**2)+c*x+d

        path.append(x)
        path.append(y)
        path.append(1.0)
        path.append(1.0)
        path.append(1.0)

        p: int = (y-1/2) - a*((x+1)**3) - b* ((x+1)**2) - c*(x+1) -d
        while((x< 1000) & (y<2000) & (x<=x1) & (y>-100)):
            x=x+1
            if p<0:
                p+=a*(-7-3*(x**2)-9*x)+b*(-3-2*x)-c
            else:
                p+=a*(-7-3*(x**2)-9*x)+b*(-3-2*x)-c-1
                y=y-1
            
            path.append(x)
            path.append(y)
            path.append(1.0)
            path.append(1.0)
            path.append(1.0)
        
    def __render(self) -> None:
        # Update all shader uniforms.
        self.pixelShader.use()
        self.pixelShader.setFloat("windowWidth", self.windowWidth)
        self.pixelShader.setFloat("windowHeight", self.windowHeight)

        # Render all shapes.
        for s in self.shapes:
            s.render()

    def __scan_convert_polygon(path: list[glm.float32], vertices) -> None:
        ymin=min(v[1] for v in vertices)
        ymax=max(v[1] for v in vertices)

        edges=[]
        for i in range(len(vertices)):
            x1,y1=vertices[i]
            x2,y2=vertices[(i+1)%len(vertices)]
            if y1!=y2:
                if y1>y2:
                    x1,x2=x2,x1
                    y1,y2=y2,y1
                m=(x2-x1)/(y2-y1)
                edges.append([y1,y2,x1,m])
        edges.sort(key=lambda e:e[0])

        aet=[]
        y=ymin
        while y<=ymax:
            while edges and edges[0][0] == y:
                aet.append(edges.pop(0))
            
            aet.sort(key=lambda e:e[2])

            for i in range(0,len(aet),2):
                if i+1<len(aet):
                    x_start= int(aet[i][2])
                    x_end=int(aet[i+1][2])
                    for x in range(x_start,x_end+1):
                        path.append(x)
                        path.append(y)
                        path.append(1.0)
                        path.append(0)
                        path.append(0)
            
            aet=[e for e in aet if e[1]!=y]

            for edge in aet:
                edge[2]+=edge[3]
            
            y+=1
    
    def __lineIntersect(x1,y1,x2,y2,x3,y3,x4,y4) -> bool :
        def ccw(ax,ay,bx,by,cx,cy):
            return (cy-ay)*(bx-ax)>(by-ay)*(cx-ax)
        
        return ccw(x1,y1,x3,y3,x4,y4) != ccw(x2,y2,x3,y3,x4,y4) and ccw(x1,y1,x2,y2,x3,y3) != ccw(x1,y1,x2,y2,x4,y4)
        
    def __intersectionPoint(x1,y1,x2,y2,x3,y3,x4,y4):
        det = (x1-x2)*(y3-y4)- (y1-y2)*(x3-x4)
        if det==0:
            return None
        t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/det
        x=x1+ t * (x2-x1)
        y=y1+ t * (y2-y1)

        return (x,y)
    
    def __detectSelfIntersections(vertices):
        intpts=[]
        n=len(vertices)
        for i in range(n):
            for j in range(i+2,n):
                if i==0 and j==n-1:
                    continue
                x1,y1 = vertices[i]
                x2,y2= vertices[(i+1)%n]
                x3,y3 = vertices[j]
                x4,y4 = vertices[(j+1)%n]
                if App.__lineIntersect(x1,y1,x2,y2,x3,y3,x4,y4):
                    point = App.__intersectionPoint(x1,y1,x2,y2,x3,y3,x4,y4)
                    if point:
                        intpts.append(point)
        return intpts
    
    def __fillWithIntPoly(path: list[glm.float32], vertices) -> None:
            n =len(vertices)
            for i in range(0,len(vertices)):
                App.__drawLine(path, vertices[i][0], vertices[i][1], vertices[(i+1)%n][0], vertices[(i+1)%n][1])
            pts=App.__detectSelfIntersections(vertices)
            if pts:
                print("The intersecting points are")
                for pt in pts:
                    print(f" {pt[0]}  {pt[1]}")
                    path.append(pt[0])
                    path.append(pt[1])
                    path.append(1)
                    path.append(0)
                    path.append(0)
            else:
                App.__scan_convert_polygon(path,vertices)


from math import cos, sin
from wireturtle3d import AnimContext, InterpMode, Renderer, Camera, Object, Scene
import wireturtle3d
from wireturtle3d.shapes import Cube, Cuboid
from wireturtle3d.utils import v

wireturtle3d.DEBUG = False
wireturtle3d.DEBUG_SKIP_CLIPPING = False
wireturtle3d.DEBUG_SHOW_FRAME = False


my_scene: Scene = Scene({
    "cube1": Object(
        location=[0.,0.,-5.],
        rotation=[0.,0.,0.], 
        scale=[1.,1.,1.], 
        mesh = Cube(2.)
    ),
    "rect":Object(
        location=[-2.,0.,-7.],
        rotation=[0.,0.,0.], 
        scale=[1.,1.,1.],
        mesh= Cuboid([1.,3.,5.])
    ),
    "my_camera": Camera(
        width=1200,height=900,
        fov=90, zfar=100., znear=0.1,
        location=[0.,0.,0.],
        rotation=[0.,0.,0.],
        scale=[1.,1.,1.]
    )
})

my_renderer: Renderer = Renderer(scene=my_scene, fps=120)

@my_renderer.animation
def my_anim(context: AnimContext):
    r = 2.
    w = 1.
    my_renderer.print(message="Hello World")
    context["cube1"].set(location=[r*cos(w*context.etime), r * (sin(w*context.etime)), -5.]) # Orbit
    context["cube1"].add(rotation=v[10,10*4,10] * context.dt)  # pyright: ignore[reportOperatorIssue]
    context["rect"].set(location=context.interpolate(A=[-2.,0.,-7.],B=[3.,0.,-7.], start = 20, end = 40))
    context["rect"].set(location=context.interpolate(A=[3.,0.,-7.], B=[-5, -3, -7], start=40, end=100))
    context["rect"].set(rotation=context.interpolate(A=(0,0,0), B=(0,90,0), start=20, end=100, mode=InterpMode.LINEAR))
my_renderer.start()
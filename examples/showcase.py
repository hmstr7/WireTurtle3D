from math import cos, sin
from wireturtle3d import AnimContext, InterpMode, Renderer, Camera, Object, Scene
import wireturtle3d
import numpy as np
from wireturtle3d.shapes import Cube, Cuboid
from wireturtle3d.utils import v

wireturtle3d.DEBUG =False
wireturtle3d.DEBUG_SKIP_CLIPPING = False
wireturtle3d.DEBUG_SHOW_FRAME = False


my_scene = Scene({
    "cube1": Object(
        [0.,0.,-5.],
        [0.,0.,0.], 
        [1.,1.,1.], 
        mesh = Cube(2.)
    ),
    "rect":Object(
        [-2.,0.,-7.],
        [0.,0.,0.], 
        [1.,1.,1.],
        mesh= Cuboid(np.array([1.,3.,5.]))
    ),
    "my_camera": Camera(
        1200,900,
        90, 100., 0.1,
        location=[0.,0.,0.],
        rotation=[0.,0.,0.],
        scale=[1.,1.,1.]
    )
})

my_renderer= Renderer(my_scene, 120)

@my_renderer.animation
def my_anim(context: AnimContext):
    r = 2.
    w = 1.
    my_renderer.print("Hello World")
    context["cube1"].set([r*cos(w*context.etime), r * (sin(w*context.etime)), -5.]) # Orbit
    context["cube1"].add(rotation=v[10,10*4,10]*context.dt)  # pyright: ignore[reportOperatorIssue]
    context["rect"].set(location=context.interpolate([-2.,0.,-7.],[3.,0.,-7.], start = 20, end = 40))
    context["rect"].set(location=context.interpolate([3.,0.,-7.], [-5, -3, -7], start=40, end=100))
    context["rect"].set(rotation=context.interpolate((0,0,0),(0,90,0),20,100,None, InterpMode.LINEAR))
my_renderer.start()
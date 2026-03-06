from math import cos, sin
import time
from main import AnimContext, Renderer, Camera, Object, Mesh3D, Scene
import main
import numpy as np

main.DEBUG =False
main.DEBUG_SKIP_CLIPPING = False
main.DEBUG_SHOW_FRAME = False

s = 1./2
cube_mesh = Mesh3D(
    vertices= np.array([
        [-s, -s, -s],
        [ s, -s, -s],
        [ s,  s, -s],
        [-s,  s, -s],
        [-s, -s,  s],
        [ s, -s,  s],
        [ s,  s,  s],
        [-s,  s,  s]
    ]),
    edges=np.array([
        [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
        [4, 5], [5, 6], [6, 7], [7, 4],  # top face
        [0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
    ])
)

my_scene = Scene({
    "cube1": Object(
        [0.,0.,-5.],
        [0.,0.,0.], 
        [2.,2.,2.], 
        mesh = cube_mesh),
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
    context["cube1"].set([r*cos(w*context.etime), r * (sin(w*context.etime)), -5.]) # Orbit
    context["cube1"].add(rotation=[10*context.dt,10*context.dt*2,10*context.dt])

my_renderer.start()
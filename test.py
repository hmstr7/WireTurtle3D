from math import cos, sin
import time
from main import AnimContext, Renderer, Camera, Object, Mesh3D, Scene
import main
import numpy as np

main.DEBUG =False
main.DEBUG_SKIP_CLIPPING = False
main.DEBUG_SHOW_FRAME = True

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

def cone_mesh(radius: float = 1.0, height: float = 2.0, segments: int = 16) -> Mesh3D:
    """
    Generates a cone mesh pointing along +Z axis, base at z=0, tip at z=height.
    """
    vertices = []
    edges = []

    # Tip of the cone
    tip = np.array([0., 0., height])
    vertices.append(tip)

    # Base vertices
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 0.
        vertices.append(np.array([x, y, z]))

    vertices = np.array(vertices)

    # Edges: from tip to base
    for i in range(1, segments + 1):
        edges.append([0, i])

    # Edges: around base
    for i in range(1, segments + 1):
        edges.append([i, 1 if i == segments else i + 1])

    return Mesh3D(vertices=vertices, edges=np.array(edges))

suz_vertices = np.array([
    # === Head ring (front) ===
    [ 0.5,  0.2,  0.7],
    [ 0.0,  0.3,  0.8],
    [-0.5,  0.2,  0.7],
    [-0.6, -0.1,  0.6],
    [-0.3, -0.4,  0.6],
    [ 0.0, -0.5,  0.6],
    [ 0.3, -0.4,  0.6],
    [ 0.6, -0.1,  0.6],

    # === Eye ridge ===
    [ 0.35, -0.05, 0.75],
    [-0.35, -0.05, 0.75],

    # === Ears (right) ===
    [ 0.9,  0.1, 0.5],
    [ 1.0, -0.1, 0.4],
    [ 0.85,-0.3, 0.5],
    [ 0.7, -0.15,0.6],

    # === Ears (left) ===
    [-0.9,  0.1, 0.5],
    [-1.0, -0.1, 0.4],
    [-0.85,-0.3, 0.5],
    [-0.7, -0.15,0.6],

    # === Chin ===
    [ 0.0, -0.7, 0.4],
    [ 0.0, -0.85,0.2],
], dtype=np.float64)

suz_edges = np.array([
    # Head outline loop
    [0,1],[1,2],[2,3],[3,4],
    [4,5],[5,6],[6,7],[7,0],

    # Eye ridge
    [8,9],
    [8,0],[8,6],
    [9,2],[9,4],

    # Right ear
    [7,10],[10,11],[11,12],[12,13],[13,7],

    # Left ear
    [3,14],[14,15],[15,16],[16,17],[17,3],

    # Chin
    [5,18],[18,19]
], dtype=np.int32)

suzanne = Mesh3D(suz_vertices,suz_edges)

def create_sphere_mesh(radius=1.0, lat_steps=8, lon_steps=16):
    vertices = []
    edges = []

    # Generate vertices
    for i in range(lat_steps + 1):
        theta = np.pi * i / lat_steps  # latitude from 0 (top) to pi (bottom)
        z = radius * np.cos(theta)
        r = radius * np.sin(theta)
        for j in range(lon_steps):
            phi = 2 * np.pi * j / lon_steps  # longitude from 0 to 2pi
            x = r * np.cos(phi)
            y = r * np.sin(phi)
            vertices.append([x, y, z])

    vertices = np.array(vertices, dtype=np.float64)

    # Generate edges
    for i in range(lat_steps + 1):
        for j in range(lon_steps):
            idx = i * lon_steps + j
            # longitude edge
            edges.append([idx, i * lon_steps + (j + 1) % lon_steps])
            # latitude edge (skip last latitude row)
            if i < lat_steps:
                edges.append([idx, (i + 1) * lon_steps + j])

    edges = np.array(edges, dtype=np.int32)
    return vertices, edges

sphere=Mesh3D(*create_sphere_mesh())

my_scene = Scene({
    "cube1": Object(np.array([[0.,0.,-5.]]), np.array([[0.,0.,0.]]), np.array([[2.,2.,2.]]), mesh = cube_mesh), # [[np.deg2rad(30),np.deg2rad(45),np.deg2rad(15)]]
    "my_camera": Camera(
        1200,900,
        90, 100., 0.1,
        location=np.array([[0.,0.,0.]]),
        rotation=np.array([[0.,0.,0.]]),
        scale=np.array([[1.,1.,1.]])
    )
})

my_renderer= Renderer(my_scene, 120)

@my_renderer.animation
def my_anim(context: AnimContext):
    r = 2.
    w = 1.
    # context["cube1"].set([r*cos(w*context.etime), r * (sin(w*context.etime)), -5.]) # Orbit
    # context["cube1"].add(rotation=[10*context.dt,10*context.dt*2,10*context.dt])
    print(context.etime)
    print(context.interpolate([-2,-2,-10.], [2,2,-10.],5.,10.))
    context["cube1"].set(location=context.interpolate([-2,-2,-10.], [2,2,-10.],5000.,5050.))
my_renderer.start()
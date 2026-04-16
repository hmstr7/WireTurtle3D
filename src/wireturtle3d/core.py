from enum import Enum
from functools import wraps
from time import perf_counter
from turtle import _Screen
from typing import Annotated, Any, Self, cast, override, Callable
#from warnings import deprecated
import numpy as np
from numpy.typing import NDArray
from numpy import deg2rad, float64, int32, tan

import turtle

from .utils import *

# Settings
DEBUG: Annotated[bool, "Debug messages on/off"] = False
DEBUG_SKIP_CLIPPING: Annotated[bool, "Line clipping step on/off"] = False
DEBUG_SHOW_FRAME = False

RADIANS: Annotated[bool, "All given angles are in radians on/off"] = False

EXPENSIVE_N: Annotated[int, "Number of edges per mesh exceeding which can cause performance issues"] = 100

class InterpMode[Enum]:
    LINEAR: Annotated[int, "Used to interpolate location or scale linearly."] = 0
    LINEAR_ROTATION: Annotated[int, "Used to interpolate rotation linearly. (SLERP)"] = 1

class Mesh3D:
    """A part of an Object that IS renderable. (3D model)"""
    def __init__(self, vertices: NDArray[float64], edges: NDArray[int32]) -> None:
        """
        - vertices: `NDArray(n,3)` - in model-space coordinates
        - edges: `NDArray(n,2)[int]` - pairs of vertices 
        """
        self.vertices: NDArray[float64] = vertices
        self.edges: NDArray[int32] = edges
        self.is_expensive: bool = self.edges.shape[0] >= EXPENSIVE_N

class Object:
    """Generic object class."""
    def __init__(self,
            location: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float], 
            rotation: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float], 
            scale: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] = (1., 1., 1.), 
            mesh: Mesh3D | None = None
        ) -> None:
        """
        - location: `NDArray` | `list` | `tuple` - in world-space coords
        - rotation: `NDArray` | `list` | `tuple` - in degrees, can be swithched to radians with `RADIANS = True`
        - scale: `NDArray` | `list` | `tuple`
        - mesh (opitional): `Mesh3D` - 3D model of this object
        """
        # All transforms are converted to be row vectors; type checks
        # Location
        if isinstance(location, np.ndarray):
            if location.shape == (1,3):
                self.location: NDArray[float64] = location
            else:
                try:
                    self.location: NDArray[float64] = location.reshape((1,3))
                except Exception as e:
                    raise ValueError(f"Invalid argument for location: {str(location)} - {str(e)}")
        elif isinstance(location, list|tuple):
            if len(location) != 3:
                raise ValueError(f"Invalid argument for location: {str(location)}")
            self.location = np.array([location], dtype=float64)
        
        # Rotation
        if isinstance(rotation, np.ndarray):
            if not RADIANS:
                rotation = deg2rad(rotation)
            if rotation.shape == (1,3):
                self.rotation: NDArray[float64] = rotation
            else:
                try:
                    self.rotation: NDArray[float64] = rotation.reshape((1,3))
                except Exception as e:
                    raise ValueError(f"Invalid argument for rotation: {str(rotation)} - {str(e)}")
        elif isinstance(rotation, list|tuple):
            if not RADIANS:
                rotation = [deg2rad(el) for el in rotation]
            if len(rotation) != 3:
                raise ValueError(f"Invalid argument for rotation: {str(rotation)}")
            self.rotation = np.array([rotation], dtype=float64)
        
        # Scale
        if isinstance(scale, np.ndarray):
            if scale.shape == (1,3):
                self.scale: NDArray[float64] = scale
            else:
                try:
                    self.scale: NDArray[float64] = scale.reshape((1,3))
                except Exception as e:
                    raise ValueError(f"Invalid argument for scale: {str(scale)} - {str(e)}")
        elif isinstance(scale, list|tuple):
            if len(scale) != 3:
                raise ValueError(f"Invalid argument for scale: {str(scale)}")
            self.scale = np.array([scale], dtype=float64)
        
        self.mesh: Mesh3D | None = mesh
        self.renderable: bool = True if mesh else False
    
    def set(self, 
            location: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None, 
            rotation: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None, 
            scale: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None
        ) -> None:
        """
        Update object's transforms
        - location (optional): `NDArray(1,3)` | `list` | `tuple` - in world-space coords
        - rotation (optional): `NDArray(1,3)` | `list` | `tuple` - in degrees, can be swithched to radians with `RADIANS = True`
        - scale (optional): `NDArray(1,3)` | `list` | `tuple`
        """

        # Location
        if location is not None:
            if isinstance(location, np.ndarray):
                if location.shape == (1,3):
                    self.location = location
                else:
                    try:
                        self.location = location.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for location: {str(location)} - {str(e)}")
            elif isinstance(location, list|tuple):
                if len(location) != 3:
                    raise ValueError(f"Invalid argument for location: {str(location)}")
                self.location = np.array([location], dtype=float64)
        
        # Rotation
        if rotation is not None:
            if isinstance(rotation, np.ndarray):
                if not RADIANS:
                    rotation = deg2rad(rotation)
                if rotation.shape == (1,3):
                    self.rotation = rotation
                else:
                    try:
                        self.rotation = rotation.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for rotation: {str(rotation)} - {str(e)}")
            elif isinstance(rotation, list|tuple):
                if not RADIANS:
                    rotation = [deg2rad(el) for el in rotation]
                if len(rotation) != 3:
                    raise ValueError(f"Invalid argument for rotation: {str(rotation)}")
                self.rotation = np.array([rotation], dtype=float64)
        
        # Scale
        if scale is not None:
            if isinstance(scale, np.ndarray):
                if scale.shape == (1,3):
                    self.scale = scale
                else:
                    try:
                        self.scale = scale.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for scale: {str(scale)} - {str(e)}")
            elif isinstance(scale, list|tuple):
                if len(scale) != 3:
                    raise ValueError(f"Invalid argument for scale: {str(scale)}")
                self.scale = np.array([scale], dtype=float64)
    def add(self, 
            location: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None, 
            rotation: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None, 
            scale: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float] | None = None
        ) -> None:
        """Adds specified transforms on top of the current ones. For argument information refer to `.set()` method docstring."""
        # Location
        if location is not None:
            if isinstance(location, np.ndarray):
                if location.shape == (1,3):
                    self.location += location
                else:
                    try:
                        self.location += location.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for location: {str(location)} - {str(e)}")
            elif isinstance(location, list|tuple):
                if len(location) != 3:
                    raise ValueError(f"Invalid argument for location: {str(location)}")
                self.location += np.array([location], dtype=float64)
        
        # Rotation
        if rotation is not None:
            if isinstance(rotation, np.ndarray):
                if not RADIANS:
                    rotation = deg2rad(rotation)
                if rotation.shape == (1,3):
                    self.rotation += rotation
                else:
                    try:
                        self.rotation += rotation.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for rotation: {str(rotation)} - {str(e)}")
            elif isinstance(rotation, list|tuple):
                if not RADIANS:
                    rotation = [deg2rad(el) for el in rotation]
                if len(rotation) != 3:
                    raise ValueError(f"Invalid argument for rotation: {str(rotation)}")
                self.rotation += np.array([rotation], dtype=float64)
        
        # Scale
        if scale is not None:
            if isinstance(scale, np.ndarray):
                if scale.shape == (1,3):
                    self.scale += scale
                else:
                    try:
                        self.scale += scale.reshape((1,3))
                    except Exception as e:
                        raise ValueError(f"Invalid argument for scale: {str(scale)} - {str(e)}")
            elif isinstance(scale, list|tuple):
                if len(scale) != 3:
                    raise ValueError(f"Invalid argument for scale: {str(scale)}")
                self.scale += np.array([scale], dtype=float64)

    def model_to_world_space(self) -> NDArray[float64]:
        if self.renderable:
            return make_model_to_world(self.location, self.rotation, self.scale)
        else:
            raise Exception("Object not renderable")

class Camera(Object):
    """Camera object."""
    def __init__(self,
            width:int, 
            height:int, 
            fov:int|float=90, 
            zfar:int|float=100., 
            znear:int|float=0.1, 
        *args, **kwargs) -> None:
        """
        - width : `int` - screen width
        - height: `int` - screen height
        - fov (optional): `int` | `float` - camera's field of view, the default value is 90 (in degrees, can be swithched to radians with `RADIANS = True`)
        - zfar (optional): `int` | `float` - far z plane
        - znear (optional): `int` | `float` - near z plane
        ---
        - location: `NDArray` | `list` | `tuple` - in world-space coords
        - rotation: `NDArray` | `list` | `tuple` - in degrees, can be swithched to radians with `RADIANS = True`
        - scale: `NDArray` | `list` | `tuple`
        """
        super().__init__(*args, **kwargs)
        self.renderable = False  # pyright: ignore[reportUnannotatedClassAttribute]

        self.screen_width: int = width
        self.screen_height: int = height
        self.fov: int|float = fov if RADIANS else deg2rad(fov) # radians
        self.zfar: int | float = zfar
        self.znear: int | float = znear
        
        self.perspective: NDArray[float64] = self.make_perspective()
        self.world_to_camera: NDArray[float64] = self.make_world_to_camera()
  
    @override
    def set(self,
            width:int|None = None, 
            height:int|None = None, 
            fov:int|float|None=90, 
            zfar:int|float|None=100., 
            znear:int|float|None=0.1, 
        *args,**kwargs) -> None:
        """ Update transforms, parameters and matrices

        - width (optional): `int` - screen width
        - height (optional): `int` - screen height
        - fov (optional): `int` | `float` - camera's field of view, the default value is 90 (in degrees, can be swithched to radians with `RADIANS = True`)
        - zfar (optional): `int` | `float` - far z plane
        - znear (optional): `int` | `float` - near z plane
        ---
        - location (optional): `NDArray` | `list` | `tuple` - in world-space coords
        - rotation (optional): `NDArray` | `list` | `tuple` - in degrees, can be swithched to radians with `RADIANS = True`
        """
        if width:
            self.screen_width = width
        if height:
            self.screen_height = height
        if fov:
            self.fov = fov if RADIANS else deg2rad(fov)
        if zfar:
            self.zfar = zfar
        if znear:
            self.znear = znear

        super().set(*args,**kwargs)
        self.perspective = self.make_perspective()
        self.world_to_camera = self.make_world_to_camera()

    def make_world_to_camera(self)-> NDArray[float64]:
        """Makes a 4x4 matrix able to convert a Vector4D to camera-relative coordinates. 

        -> `NDArray(4,4)`
        """

        result: NDArray[float64] = np.eye(4, dtype=float64)
        R_C = rotate(self.rotation)
        result[0:3,0:3] = R_C.T
        result[0:3, 3]= (-R_C.T @ self.location.reshape(3,)) # Because self.location is a row vector, i.e. (1,3) but (3,) is expected. Probably TODO: Clear this mess
        result[-1,-1] = 1.
        return result

    def make_perspective(self) -> NDArray[float64]:
        """Make a 4x4 perspective matrix that accounts for aspect ratio and camera FOV 
        (Basically a normalization step, but NOT the perspective divide yet) 

        -> `NDArray(4,4)`
        """
        result = np.zeros(shape=(4,4), dtype=float64)
        fov, zfar, znear = self.fov, self.zfar, self.znear
        aspect = self.screen_width/self.screen_height
        result[0,0] = 1/(tan(fov/2) * aspect)
        result[1,1] = 1/tan(fov/2)
        result[2,2] = -(zfar + znear)/(zfar - znear)
        result[2,3] = -(2 * zfar * znear)/(zfar - znear)
        result[3,2] = -1
        return result

    #@deprecated("Use Camera.world_to_camera matrix directly (don't forget to .set when needed)")
    def world_to_camera_space(self, vertex: NDArray[float64]) -> NDArray[float64]:
        """Converts world coordinates of a point to camera space coordinates.
        
        - vertex: `NDArray(1,3)`
        
        -> `NDArray(4,)` - with trailing 1
        """
        return self.world_to_camera @ np.hstack([vertex, [[1.0]]]).T

class Scene:
    """A collection of objects to render, must contain at least one `Camera`."""
    def __init__(self, objects: dict[str,Object], camera_name: str|None = None) -> None:
        """
        - objects: `dict[str, Object]` - the scene itself
        """
        self.objects: dict[str, Object] = objects

        self.camera = ...   # pyright: ignore[reportAttributeAccessIssue]
        try:
            if camera_name:
                camera_candidate = self.objects[camera_name]
                if not isinstance(camera_candidate, Camera):
                    raise Exception("Not a Camera")
                self.camera: Camera = camera_candidate
            else:
                for obj in self.objects.values():
                    if isinstance(obj, Camera):
                        self.camera: Camera = obj
                        break
                if not self.camera:
                    raise Exception("No camera found")
        except KeyError:
            raise KeyError(f"No object with name {camera_name}")
    
    def add(self, name: str, object: Object) -> Object:
        """Add an object to the scene after it's creation"""
        if name in self.objects.keys():
            raise Exception(f"Object with name {name} already exists.")
        self.objects[name] = object
        return object

    def remove(self, name: str) -> None:
        if name not in self.objects:
            raise KeyError(f"Object with name {name} not found")
        _ = self.objects.pop(name)
    
    def clear(self) -> None:
        """Deletes all renderable objects from scene"""
        for name, object in self.objects.items():
            if object.renderable:
                _ = self.objects.pop(name)
    
    def clear_all(self) -> None:
        """Clears everything in the scene, INCLUDING `Camera`s

        Warning: a scene cannot be rendered without a `Camera`!
        """
        
    def set_camera(self, camera_name: str) -> None:
        try:
            if camera_name:
                camera_candidate = self.objects[camera_name]
                if not isinstance(camera_candidate, Camera):
                    raise Exception("Not a Camera")
                self.camera = camera_candidate
        except KeyError:
            raise KeyError(f"No object with name {camera_name}")

    @classmethod
    def create_empty(cls)  -> type[Self]:
        """Creates an empty `Scene` with nothing but a `'camera'`.
        """
        return cls(  # pyright: ignore[reportReturnType]
            objects = {
                'camera': Camera(
                    width = 1000,
                    height = 1000,
                    location = [0,0,0],
                    rotation = [0,0,0],
                    scale=[0,0,0]
                ),
            },
            camera_name = 'camera'
        )
        
class Renderer:
    """An object that handles rendering"""
    def __init__(self, scene: Scene, fps:float|int = 60, nworkers:int=10) -> None:
        """
        - scene: Scene - objects to be rendered
        ---
        - fps (optional): int|float - desired refresh rate
        - nworkers (optional) (WIP) - number of turtles to create
        """
        self.scene: Scene = scene
        self.window_width: int = self.scene.camera.screen_width
        self.window_height: int = self.scene.camera.screen_height

        self.window: _Screen = turtle.Screen()
        self.window.setup(self.window_width,self.window_height)
        self.window.tracer(False)

        # For printing data, debug
        self.reserved_turtle= turtle.Turtle(visible=False)
        self.reserved_turtle.penup()
        self.reserved_turtle.teleport(-self.window_width/2+1,self.window_height/2-1)

        # For rendering
        self.workers: list[dict[str,turtle.Turtle|int]] = []
        self.__setup_workers(nworkers)

        if fps <= 0:
            raise ValueError("FPS must be greater than 0")
        self.fps: int|float = fps
        
        self.animstate: AnimState = AnimState()
        self.animcontext = AnimContext(self.scene, self.animstate)

        self.start = self.window.mainloop
    
    def __setup_workers(self, n: int=10) -> None:
        for i in range(n):
            w = turtle.Turtle(visible=False, undobuffersize=0)
            w.speed(0)
            self.workers.append({'worker':w,'busy':0})
    
    def __get_worker(self) -> tuple[int,turtle.Turtle]:
        """Returns a turtle and it's worker id
        
        -> (`int`, `Turtle`)
        """
        # Find free workers
        for wid, worker in enumerate(self.workers):
            if worker['busy'] == 0:
                return wid, cast(turtle.Turtle, worker['worker'])
        
        # Find a worker with minimal business
        wid, min_worker = 0,self.workers[0]
        bmin: int = cast(int,min_worker['busy'])
        for id, worker in enumerate(self.workers):
            if cast(int, worker["busy"]) < bmin:
                wid, min_worker = id, worker
                bmin = cast(int, worker["busy"])
            
        self.workers[wid]['busy'] += 1  # pyright: ignore[reportOperatorIssue]
        return wid, cast(turtle.Turtle, min_worker['worker'])
        
    def __free_worker(self, id: int):
        """Must be called when worker's job is done, decreases worker's business by 1
        
        - id: `int` - worker id to free
        """
        if id<0 or id>len(self.workers):
            raise ValueError(f"No worker with id {str(id)}")
        worker = self.workers[id]
        if cast(int, worker['busy'])==0:
            self._debug("Worker is already free")
            return
        worker['busy'] -= 1  # pyright: ignore[reportOperatorIssue]
    
    def update_scene(self, scene: Scene|None = None) -> None:
        """Replaces the scene or reinitializes the old one (MUST call this if camera was updated)
        
        - scene (optional): `Scene` - new scene to be rendered
        """
        if scene:
            self.scene = scene
        
        self.window_width = self.scene.camera.screen_width
        self.window_height = self.scene.camera.screen_height
        self.window.setup(self.window_width,self.window_height)
        self.window.tracer(False)
        self.workers = []
        self.__setup_workers()

    def _debug(self, *args) -> None:
        if DEBUG:
            print(*args)

    def render(self) -> None:
        """Renders current state of the scene. 
        
        Warning: if you've changed the active camera in scene (with `Scene.set_camera()`) you MUST run `.update_scene()` first!
        """
        
        camera: Camera = self.scene.camera
        camera.set()

        to_render = {k: v for k,v in self.scene.objects.items() if v.renderable}
        for name, obj in to_render.items():
            # Get object's vertices and convert them to homogeneous coordinates
            vertices = cast(Mesh3D,obj.mesh).vertices
            no_vertices = vertices.shape[0]
            edges = cast(Mesh3D,obj.mesh).edges
            vertices_h = np.hstack([vertices, np.ones((no_vertices,1))])

            # MVP
            vertices_clip = camera.perspective @ camera.world_to_camera @ obj.model_to_world_space() @ vertices_h.T # IMPORTANT: From now on shape is (4,N)
            
            lines = [] # Lines to draw

            # Clipping and perspective divide
            if DEBUG_SKIP_CLIPPING:
                self._debug("The renderer will NOT clip vertices")
            for i0, i1 in edges:
                p0 = vertices_clip[:, i0]
                p1 = vertices_clip[:, i1]

                if not DEBUG_SKIP_CLIPPING:
                    self._debug(f"About to clip: {str(i0)}-{str(i1)}")
                    clipped = self._clip_line(p0, p1)
                    self._debug(f"Clipped output: {str(clipped)}")
                else:
                    clipped = p0, p1
                if clipped is None: 
                    continue # Drop the segment if it's outside the screen

                c0, c1 = clipped

                # Perspective divide
                n0 = c0[:3] / c0[3]
                n1 = c1[:3] / c1[3]

                lines.append([n0[:2], n1[:2]])

            lines = np.array(lines)
            
            self._debug(f"Lines: {str(lines)}")

            for line in lines:
                self._debug(f"Drawing line {str(line)}")
                self._draw(line)  # pyright: ignore[reportArgumentType]
            
        self._debug('Render finished')
         
    def _clip_line(self,
            p0: NDArray[np.float64],
            p1: NDArray[np.float64],
            eps: float = 1e-8
        ) -> tuple[NDArray[np.float64], NDArray[np.float64]]|None:
        """
        Clips a line segment.

        - p0,p1: `NDArray[float64](4,)` - in homogeneous clip-space coordinates (after MVP, before perspective divide)

        -> ( `NDArray[float64](4,)`, `NDArray[float64](4,)` ) | `None` - clipped (p0, p1) in clip space, or None if fully outside.
        """
        self._debug(f"Clipping {str(p0)}-{str(p1)}")

        if not ( p0.shape == (4,) and p1.shape == (4,) ):
            raise ValueError("Shape of points must be (4,)")

        d = p1 - p0
        t0, t1 = 0.0, 1.0

        # planes representing: x + w >= 0, -x + w >= 0, y + w >= 0, -y + w >= 0, z + w >= 0, -z + w >= 0
        planes = [
            np.array([ 1.0,  0.0,  0.0,  1.0], dtype=np.float64),
            np.array([-1.0,  0.0,  0.0,  1.0], dtype=np.float64),
            np.array([ 0.0,  1.0,  0.0,  1.0], dtype=np.float64),
            np.array([ 0.0, -1.0,  0.0,  1.0], dtype=np.float64),
            np.array([ 0.0,  0.0,  1.0,  1.0], dtype=np.float64),
            np.array([ 0.0,  0.0, -1.0,  1.0], dtype=np.float64),
        ]

        for plane in planes:
            f0 = plane @ p0
            fd = plane @ d

            self._debug("Testing against plane: ",plane)
            if abs(fd) < eps:
                # segment parallel to plane: if starting point is outside, fully outside
                self._debug(f"Segment parallel to plane: if starting point is outside, fully outside (f0 = {str(f0)})")
                if f0 < 0.0:
                    self._debug("Segment discard")
                    return None
                else:
                    self._debug("Continue")
                    continue

            t = -f0 / fd
            if fd < 0.0:
                # leaving -> update t1
                t1 = min(t1, t)
            else:
                # entering -> update t0
                t0 = max(t0, t)

            if t0 > t1:
                self._debug("t0 > t1 - segment discard")
                return None
        self._debug(f"Clip result: {str((p0 + t0 * d, p0 + t1 * d))}")
        return (p0 + t0 * d, p0 + t1 * d)

    def _draw(self, proj: NDArray[float64]) -> None:
        """Draw a 2D segment
        
        - proj: `NDArray()`
        """
        if not proj.shape[0]==2:
            raise Exception(f"Failed to draw an object: incorrect draw_buffer was passed. {str(proj.shape)}")

        # Convert to turtle coords:
        proj[:,0] *= self.window_width/2
        proj[:,1] *= self.window_height/2
        
        id, t = self.__get_worker()

        t.penup()
        self._debug(f"Start) Goto ({str(proj[0,0])},{str(proj[0,1])}); Pen is {str(t.pen())}")
        t.goto(proj[0,0],proj[0,1])
        t.pendown()
        self._debug(f"End) Goto ({str(proj[1,0])},{str(proj[1,1])}); Pen is {str(t.pen())}")
        t.goto(proj[1,0],proj[1,1])

        self.__free_worker(id)
        
    def clear(self) -> None:
        """Clears screen"""
        for worker in self.workers:
            cast(turtle.Turtle,worker['worker']).clear()
             
    def animation(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.clear()
            self.animstate.tick()
            self.animcontext.update()
            kwargs["context"] = self.animcontext
            func(*args, **kwargs)
            if DEBUG_SHOW_FRAME:
                id, w = self.__get_worker()
                w.penup()
                w.goto(-self.window_width/2+100, self.window_height/2-100)
                w.write(str(self.animstate.frame), font=("Arial",24,"bold"))
                self.__free_worker(id)
            self.render()
            self.window.update()
            self.window.ontimer(wrapper,round(1000/self.fps))
        wrapper()
        return wrapper

    def print(self, message:str) -> None:
        self.reserved_turtle.pendown()
        self.reserved_turtle.clear()
        self.reserved_turtle.write(message)

class AnimState:
    frame: int = 0
    etime: float = perf_counter()
    last_time: float = etime
    dt: float|int = perf_counter() - last_time
    def tick(self):
        self.frame += 1
        self.etime = perf_counter()
        self.dt = perf_counter() - self.last_time
        self.last_time = self.etime

class AnimContext:
    """Shortcut access to Renderer or Scene variables and data"""
    def __init__(self, scene: Scene, state: AnimState) -> None:
        self.scene: Scene = scene
        self.state: AnimState = state
        self.dt: float | int = self.state.dt
        self.etime: float = self.state.etime
        self.frame: int = self.state.frame
        
        interp_buffer: float = 0.
    def update(self) -> None:
        self.__init__(self.scene,self.state)
    def __getitem__(self, key: str) -> Object:
        """Shortcut for renderer.scene.objects[key]"""
        return self.scene.objects[key]
    def get(self) -> None:
        ...
    
    def interpolate(self, 
            A: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float],
            B: NDArray[float64] | list[float|int] | tuple[int|float,int|float,int|float],
            start: float|int, end: float|int,
            t: float | int | None  = None,
            mode: int = InterpMode.LINEAR
        ) -> NDArray[float64]|None:
        start_state: NDArray[float64] = A  # pyright: ignore[reportAssignmentType]
        current_state: NDArray[float64] = start_state   # pyright: ignore[reportAssignmentType]
        end_state: NDArray[float64] = B  # pyright: ignore[reportAssignmentType]
        if not t:
            t = self.frame
        if start>t:
            return None
        if end<t:
            return None



        # Type checks
        if isinstance(A, np.ndarray):
            if A.shape != (1,3):
                try:
                    start_state = A.reshape((1,3))
                except Exception as e:
                    raise ValueError(f"Invalid argument for location: {str(A)} - {str(e)}")
        elif isinstance(A, list|tuple):
            if len(A) != 3:
                raise ValueError(f"Invalid argument for location: {str(A)}")
            start_state = np.array([A], dtype=float64)
        if isinstance(B, np.ndarray):
            if B.shape != (1,3):
                try:
                    end_state = B.reshape((1,3))
                except Exception as e:
                    raise ValueError(f"Invalid argument for location: {str(B)} - {str(e)}")
        elif isinstance(B, list|tuple):
            if len(B) != 3:
                raise ValueError(f"Invalid argument for location: {str(B)}")
            end_state = np.array([B], dtype=float64)
        
        if mode == InterpMode.LINEAR:
            current_state = start_state + (((t-start)*(end_state-start_state))/(end-start))
        elif mode == InterpMode.LINEAR_ROTATION:
            R0: NDArray[float64] = rotate(start_state)
            R1: NDArray[float64] = rotate(end_state)
            R: NDArray[float64] = R0 @ ((R0.T @ R1.T)**t)
            current_state = unrotate(R)
        else:
            raise ValueError("Incorrect mode")
        return current_state
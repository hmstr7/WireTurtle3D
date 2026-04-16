from .core import Mesh3D
from numpy.typing import NDArray
from numpy import float16, float32, float64, int16, int32, int64
import numpy as np

class Cuboid(Mesh3D):
    """A cuboid of arbitrary side sizes."""
    def __init__(self, size: list[float|int] | tuple[float|int,float|int,float|int] | NDArray[float64|float32|float16|int32|int16|int64]) -> None:
        x: float | int = 1.
        y: float | int = 1.
        z: float | int = 1.

        if isinstance(size, np.ndarray):
            try:
                size = size.reshape(-1)
                x,y,z = size/2
            except Exception as e:
                raise ValueError("Incorrect size")
        elif isinstance(size, list|tuple):
            if len(size) != 3:
                raise ValueError("Incorrect size")
            x,y,z = [a/2 for a in size]

        vertices: NDArray[float64]= np.array([
        [-x, -y, -z],
        [ x, -y, -z],
        [ x,  y, -z],
        [-x,  y, -z],
        [-x, -y,  z],
        [ x, -y,  z],
        [ x,  y,  z],
        [-x,  y,  z]
        ], dtype=float64)

        edges: NDArray[int32] = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
        ], dtype=int32)

        super().__init__(vertices, edges)

class Cube(Cuboid):
    """A cube (equal sides)"""
    def __init__(self, size: float | int = 1.) -> None:
        super().__init__(size=[size,size,size])



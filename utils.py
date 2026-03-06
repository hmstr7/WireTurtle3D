
from typing import Any, Callable


from numpy import deg2rad, float64, int32, tan, cos, sin
import numpy as np
from numpy.typing import NDArray
def rotate_roll(theta:float) -> NDArray[float64]:
    """
    - theta: float - in radians
    """
    result = np.zeros((3,3), float64)
    result[0,0] = 1.
    result[1,1] = cos(theta)
    result[1,2] = -sin(theta)
    result[2,1] = sin(theta)
    result[2,2] = cos(theta)
    
    return result

def rotate_pitch(theta:float) -> NDArray[float64]:
    """
    - theta: float - in radians
    """
    # result = np.zeros((3,3), float64)
    # result[0,0] = cos(theta)
    # result[0,2] = sin(theta)
    # result[1,1] = 1.
    # result[0,2] = -sin(theta)
    # result[2,2] = cos(theta)
    result = np.eye(3, dtype=np.float64)
    result[0,0] = cos(theta)
    result[0,2] = sin(theta)
    result[2,0] = -sin(theta)
    result[2,2] = cos(theta)
    return result

def rotate_yaw(theta:float) -> NDArray[float64]:
    """
    - theta: float - in radians
    """
    result = np.zeros((3,3), float64)
    result[0,0] = cos(theta)
    result[0,1] = -sin(theta)
    result[1,0] = sin(theta)
    result[1,1] = cos(theta)
    result[2,2] = 1.
    
    return result

def rotate(rotation: NDArray[float64]) -> NDArray[float64]:
    rotation_matrix = rotate_yaw(rotation[0,2]) @ rotate_pitch(rotation[0,1]) @ rotate_roll(rotation[0,0])
    return rotation_matrix

def make_model_to_world(location: NDArray[float64], rotation: NDArray[float64], scale: NDArray[float64]) -> NDArray[float64]:
    """
    Returns a 4x4 matrix able to convert a homogenuous vector to world space.
    - location: Point3D
    - rotation: Point3D
    - scale: Point3D

    -> NDArray(4,4)[float]
    
    Note: all points must be row vectors (horizontal), in other words NDArray with the shape (1,3)
    """
    # matrix = np.zeros((4,4), float64)
    
    # R_scaled: NDArray[float64] = rotate(rotation) # TODO: Refactor this horrible mess
    # R_scaled[:,0] *= scale[0,0]
    # R_scaled[:,1] *= scale[0,1]
    # R_scaled[:,2] *= scale[0,2]

    # matrix[0:3,0:3] = R_scaled
    # matrix[0:3,3] = location.T.flatten()
    
    R = rotate(rotation)  # 3x3
    # create matrix
    M = np.eye(4, dtype=np.float64)
    # scale first along local axes
    M[0:3,0:3] = R * scale  # relies on broadcasting shape (1,3)
    M[0:3,3] = location.T.flatten()
    return M

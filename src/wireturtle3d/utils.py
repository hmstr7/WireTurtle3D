from numpy import arcsin, atan2, float64, cos, sin
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

    result = np.eye(3, dtype=np.float64)
    result[0,0] = cos(theta)
    result[0,2] = sin(theta)
    result[2,0] = -sin(theta)
    result[2,2] = cos(theta)
    return result

def rotate_yaw(theta:float) -> NDArray[float64]:
    """
    - theta: float - in radians if `RADIANS=True`
    """
    result = np.zeros((3,3), float64)
    result[0,0] = cos(theta)
    result[0,1] = -sin(theta)
    result[1,0] = sin(theta)
    result[1,1] = cos(theta)
    result[2,2] = 1.
    
    return result

def rotate(rotation: NDArray[float64]) -> NDArray[float64]:
    """Makes ZYX rotation matrix for a given set of euler angles.
    - rotation: `NDArray(1,3)` - in radians

    -> `NDArray(3,3)`
    """
    rotation_matrix = rotate_yaw(rotation[0,2]) @ rotate_pitch(rotation[0,1]) @ rotate_roll(rotation[0,0])
    return rotation_matrix

def make_model_to_world(location: NDArray[float64], rotation: NDArray[float64], scale: NDArray[float64]) -> NDArray[float64]:
    """
    Returns a 4x4 matrix able to convert a homogenuous vector to world space.
    - location: `NDArray(1,3)`
    - rotation: `NDArray(1,3)`
    - scale: `NDArray(1,3)`

    -> `NDArray(4,4)`
    
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

def unrotate(rotation_matrix:NDArray[float64]) -> NDArray[float64]:
    """Converts a rotation matrix back to euler angles.
    - rotation_matrix: `NDArray(3,3)`

    -> `NDArray(1,3)` 
    """
    if rotation_matrix.shape != (3,3):
        raise ValueError("Incorrect shape (must be (3,3))")
    x, y, z = atan2(rotation_matrix[2,1], rotation_matrix[2,2]), arcsin(-rotation_matrix[2,0]), atan2(rotation_matrix[1,0],rotation_matrix[0,0])

    return np.array([[x,y,z]], dtype=float64)

class Vec3:
    def __init__(self, x:int|float,y:int|float,z:int|float) -> None:
        self.value: NDArray[float64] = np.array([[x,y,z]],dtype=float64)
    
    @classmethod
    def __class_getitem__(cls, key:tuple[float|int,float|int,float|int]) -> NDArray[float64]:
        if len(key) != 3:
            raise ValueError("This is a 3D vector")
        return np.array([[*key]],dtype=float)
v = Vec3
zero = v[0,0,0] 

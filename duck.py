from typing import Optional, Tuple
import numpy as np
from numpy.typing import NDArray

def clip_line_clipspace(
    p0: NDArray[np.float64],
    p1: NDArray[np.float64],
    eps: float = 1e-9
) -> Optional[Tuple[NDArray[np.float64], NDArray[np.float64]]]:
    """
    Clip a line segment in homogeneous clip space.
    p0,p1: shape (4,), clip-space (x,y,z,w) BEFORE perspective divide.
    Returns clipped (p0,p1) in clip space or None.
    """
    assert p0.shape == (4,) and p1.shape == (4,)

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

        if abs(fd) < eps:
            # segment parallel to plane: if starting point is outside, fully outside
            if f0 < 0.0:
                return None
            else:
                continue

        t = -f0 / fd
        if fd < 0.0:
            # leaving -> update t1
            t1 = min(t1, t)
        else:
            # entering -> update t0
            t0 = max(t0, t)

        if t0 > t1:
            return None

    return (p0 + t0 * d, p0 + t1 * d)
def test_clipper(clipper):
    tests = []

    # 1) fully inside
    p0 = np.array([0.0, 0.0, 0.0, 1.0])
    p1 = np.array([0.4, 0.2, 0.0, 1.0])
    tests.append(("inside", p0, p1))

    # 2) crossing left plane (x from -2 to 0)
    p0 = np.array([-2.0, 0.0, 0.0, 1.0])
    p1 = np.array([ 0.0, 0.0, 0.0, 1.0])
    tests.append(("cross_left", p0, p1))

    # 3) entirely outside (both x >> w)
    p0 = np.array([ 5.0, 0.0, 0.0, 1.0])
    p1 = np.array([ 6.0, 0.0, 0.0, 1.0])
    tests.append(("outside", p0, p1))

    # 4) crossing with different w (simulate perspective popular case)
    # p0 is at w=2, x=3 (outside), p1 at w=1, x=0 (inside) -> should clip
    p0 = np.array([3.0, 0.0, 0.0, 2.0])
    p1 = np.array([0.0, 0.0, 0.0, 1.0])
    tests.append(("cross_diff_w", p0, p1))

    for name, a, b in tests:
        out = clipper(a, b)
        print(f"TEST {name}: in {a} -> {b} =>", "CLIPPED" if out else "REJECTED")
        if out:
            pqa, pqb = out
            print("  ->", pqa, pqb)

# run
test_clipper(clip_line_clipspace)
from smithers.io.stlhandler import STLHandler
import numpy as np


def min_max(stl):
    if isinstance(stl, str):
        stl = STLHandler.read(stl)

    return np.concatenate(
        [
            np.min(stl["points"][:, None], axis=0),
            np.max(stl["points"][:, None], axis=0),
        ],
        axis=0,
    )


def dimension(stl):
    mm = min_max(stl)
    return mm[1] - mm[0]


def diameter(stl):
    dims = dimension(stl)
    # the diameter of the propeller lies on the XZ plane
    return max(dims[0], dims[2])

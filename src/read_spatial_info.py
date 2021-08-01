from smithers.io.stlhandler import STLHandler
from smithers.io.obj import ObjHandler
import numpy as np


class DataWrapper:
    def __init__(self, path):
        extension = path.split(".")[-1]
        if extension == "stl":
            self._points = np.asarray(STLHandler.read(path)["points"])
        elif extension == "obj":
            self._points = np.asarray(ObjHandler.read(path).vertices)
        else:
            raise ValueError(
                "Files of type {} are not supported at the moment".format(
                    extension
                )
            )

    @property
    def points(self):
        return self._points


def min_max(data):
    return np.concatenate(
        [
            np.min(data.points[:, None], axis=0),
            np.max(data.points[:, None], axis=0),
        ],
        axis=0,
    )


def dimension(data):
    mm = min_max(data)
    return mm[1] - mm[0]


def diameter(data):
    dims = dimension(data)
    # the diameter of the propeller lies on the XZ plane
    return max(dims[0], dims[2])


def boundary(data):
    return np.concatenate(
        [
            np.min(data.points, axis=0)[None, :],
            np.max(data.points, axis=0)[None, :],
        ],
        axis=0,
    )


def middle_point(data):
    return np.sum(boundary(data), axis=0) / 2

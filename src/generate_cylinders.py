import numpy as np
from smithers.io.obj import ObjHandler


def compute_cylinder_dimensions(
    scales=None, dimensions=None, propeller_diameter=None
):
    """If `scales` isn't `None` the dimension of the cylinders is given by
    the product of each scaling factor (i.e. the components of the 2D array
    `scales`) with the diameter of the propeller.

    If `dimensions` is not `None` the diameter of the cylinders is given by
    the components of the 2D array `dimensions`.

    Both `dimensions` and `scales` must be 2D array, along the first axis
    changes the index of the cylinder, along the second axis changes the
    dimension of the cylinder along the x,y,z axes (therefore the second axis
    must have three components).

    One and only one of `scales` and `dimensions` must be `None`. The arrays
    can have an arbitrary number of components along the first axis.
    """

    if (scales and dimensions) or (not scales and not dimensions):
        raise ValueError(
            "One of `scales` and `dimensions` must not be `None`."
        )
    if scales and not propeller_diameter:
        raise ValueError("The diameter of the propeller is needed.")

    if dimensions and np.asarray(dimensions).ndim != 2:
        raise ValueError("Expected 2D array, got 1D.")
    if scales and np.asarray(scales).ndim != 2:
        raise ValueError("Expected 2D array, got 1D.")

    if dimensions and np.asarray(dimensions).shape[1] != 3:
        raise ValueError("Wrong number of components along the second axis.")
    if scales and np.asarray(scales).shape[1] != 3:
        raise ValueError("Wrong number of components along the second axis.")

    if scales:
        return np.asarray(scales) * propeller_diameter
    else:
        return np.asarray(dimensions)


def generate_cylinders(
    dimensions,
    base_folder='.'
    paths=["innerCylinder.obj", "middleCylinder.obj", "outerCylinder.obj"],
):
    base_cylinder = ObjHandler.read("res/cylinder.obj")
    base_dimension = ObjHandler.dimension(base_cylinder)

    for expected_dimension, filename in zip(dimensions, paths):
        scale_factors = expected_dimension / base_dimension
        ObjHandler.scale(base_cylinder, scale_factors)
        ObjHandler.write(base_folder + '/' + filename, base_cylinder)

        # after scaling we unscale to reset che changes to the base cylinder
        ObjHandler.scale(base_cylinder, 1 / scale_factors)

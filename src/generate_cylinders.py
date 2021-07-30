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


def generate_cylinders_obj(
    dimensions,
    base_folder=".",
    paths=["innerCylinder.obj", "middleCylinder.obj", "outerCylinder.obj"],
    regions=["innerCylinder", "middleCylinder", "outerCylinder"],
):
    base_cylinder = ObjHandler.read("res/cylinder.obj")
    base_dimension = ObjHandler.dimension(base_cylinder)

    for expected_dimension, filename, region, idx in zip(
        dimensions, paths, regions, range(len(dimensions))
    ):
        scale_factors = expected_dimension / base_dimension
        ObjHandler.scale(base_cylinder, scale_factors)

        base_cylinder.regions.clear()
        base_cylinder.regions_change_indexes.clear()

        if idx != len(dimensions) - 1:
            base_cylinder.regions.append(region)
            base_cylinder.regions_change_indexes.append((0, 0))
        else:
            # the outermost cylinder wants three regions:
            # outerCylinderWall, outerCylinderInlet, outerCylinderOutlet

            # first of all we find the two regions in which Y remains constant
            min_y = np.min(base_cylinder.vertices[:, 1])
            max_y = np.min(base_cylinder.vertices[:, 1])

            poly = np.asarray(base_cylinder.polygons) - 1
            poly_vertices_y = base_cylinder.vertices[poly.flatten()][:, 1]

            def find_plateau_polygons(constant_y):
                return np.all(
                    (poly_vertices_y == constant_y).reshape(-1, poly.shape[1]),
                    axis=1,
                )

            left_bool_idxes = find_plateau_polygons(min_y)
            right_bool_idxes = find_plateau_polygons(max_y)
            walls_bool_idxes = np.logical_not(
                np.logical_or(left_bool_idxes, right_bool_idxes)
            )

            left = poly[left_bool_idxes]
            right = poly[right_bool_idxes]
            walls = poly[walls_bool_idxes]

            base_cylinder.regions.extend(
                map(lambda s: region + s, ["Inlet", "Outlet", "Wall"])
            )
            base_cylinder.regions_change_indexes.append((0, 0))
            base_cylinder.regions_change_indexes.append((left.shape[0], 1))
            base_cylinder.regions_change_indexes.append(
                (left.shape[0] + right.shape[0], 2)
            )

            # as always we increment the result by 1
            base_cylinder.polygons = (
                np.concatenate([left, right, walls], axis=0) + 1
            )

        ObjHandler.write(base_folder + "/" + filename, base_cylinder)

        # after scaling we unscale to reset che changes to the base cylinder
        ObjHandler.scale(base_cylinder, 1 / scale_factors)

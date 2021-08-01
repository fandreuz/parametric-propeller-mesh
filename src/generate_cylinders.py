import numpy as np
from smithers.io.obj import ObjHandler
from .read_spatial_info import middle_point, boundary


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


def compute_cylinder_anchors(
    ydistance_from_innermost, outer_cylinder_y_dimension, propeller
):
    propeller_middle = middle_point(propeller)
    propeller_boundary = boundary(propeller)

    # we return the x and z middle points, and the biggest Y coordinate of the
    # propeller
    outer_anchor = np.array(
        [propeller_middle[0], propeller_boundary[1, 1], propeller_middle[2]]
    )[None, :]

    outer_cylinder_y_min = (
        propeller_boundary[1, 1] - outer_cylinder_y_dimension
    )

    middle_layer = np.repeat(
        np.array([propeller_middle[0], np.nan, propeller_middle[2]])[None, :],
        repeats=len(ydistance_from_innermost),
        axis=0,
    )

    # space_left is the space between the outlet and the tip of the propeller
    # it is updated as soon a cylinder erases the space left
    space_left = outer_cylinder_y_dimension - (
        propeller_boundary[1, 1] - propeller_boundary[0, 1]
    )
    for idx in range(len(ydistance_from_innermost)):
        if idx == 0:
            base = propeller_boundary[0, 1]
        else:
            base = middle_layer[idx - 1, 1]

        middle_layer[idx, 1] = (
            base - ydistance_from_innermost[idx] * space_left
        )
        space_left = middle_layer[idx, 1] - outer_cylinder_y_min

    return np.concatenate([middle_layer, outer_anchor], axis=0)


def generate_cylinders_obj(
    dimensions,
    anchors,
    base_folder=".",
    paths=["innerCylinder.obj", "middleCylinder.obj", "outerCylinder.obj"],
    regions=["innerCylinder", "middleCylinder", "outerCylinder"],
):
    """Generate .obj files which contain cylinder that can be used to
    bound volumes with different mesh resolutions.

    The outermost cylinder contains three regions: `regions[-1]`Inlet,
    `regions[-1]`Outlet, `regions[-1]`Wall, while the other cylinders contain
    a single region named according to the parameter `regions`.

    :param dimensions: A 2D array which represents the dimension of each
        cylinder. A row corresponds to a cylinder, the (3) columns correspond
        to X,Y,Z dimensions. See also :func:`compute_cylinder_dimensions`.
    :type dimensions: np.ndarray
    :param base_folder: The root folder of the OpenFOAM case taken into account,
        OBJ files are saved into `base_folder/`constant/triSurface.
        Defaults to "."
    :type base_folder: str, optional
    :param paths: Names of the cylinders, defaults to
        ["innerCylinder.obj", "middleCylinder.obj", "outerCylinder.obj"]
    :type paths: list, optional
    :param regions: Names of the regions inside of cylinders, specified
        individually for each cylinder. Defaults to
        ["innerCylinder", "middleCylinder", "outerCylinder"]
    :type regions: list, optional
    :return: A 2-tuple which contains the minimum and maximum Y coordinate of
        the outer cylinder.
    :rtype: tuple
    """

    base_cylinder = ObjHandler.read("res/cylinder.obj")
    base_dimension = ObjHandler.dimension(base_cylinder)

    for expected_dimension, filename, region, idx, anchor in zip(
        dimensions, paths, regions, range(len(dimensions)), anchors
    ):
        scale_factors = expected_dimension / base_dimension
        ObjHandler.scale(base_cylinder, scale_factors)

        base_cylinder.regions.clear()
        base_cylinder.regions_change_indexes.clear()

        cylinder_middle = (
            np.max(base_cylinder.vertices, axis=0)
            + np.min(base_cylinder.vertices, axis=0)
        ) / 2

        translation_vector = anchor - cylinder_middle

        if idx != len(dimensions) - 1:
            translation_vector[1] = anchor[1] - np.min(
                base_cylinder.vertices[:, 1]
            )
            ObjHandler.translate(base_cylinder, translation_vector)

            base_cylinder.regions.append(region)
            base_cylinder.regions_change_indexes.append((0, 0))
        else:
            translation_vector[1] = anchor[1] - np.max(
                base_cylinder.vertices[:, 1]
            )
            ObjHandler.translate(base_cylinder, translation_vector)

            # the outermost cylinder wants three regions:
            # outerCylinderWall, outerCylinderInlet, outerCylinderOutlet

            # first of all we find the two regions in which Y remains constant
            min_y = np.min(base_cylinder.vertices[:, 1])
            max_y = np.max(base_cylinder.vertices[:, 1])

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
            base_cylinder.regions_change_indexes.append((right.shape[0], 1))
            base_cylinder.regions_change_indexes.append(
                (left.shape[0] + right.shape[0], 2)
            )

            # as always we increment the result by 1
            base_cylinder.polygons = (
                np.concatenate([right, left, walls], axis=0) + 1
            )

        ObjHandler.write(base_cylinder, base_folder + "/" + filename)

        if idx == len(dimensions) - 1:
            return ObjHandler.boundary(base_cylinder, axis=1)
        else:
            # after scaling we unscale to reset che changes to the base cylinder
            ObjHandler.scale(base_cylinder, 1 / scale_factors)
            ObjHandler.translate(base_cylinder, -translation_vector)

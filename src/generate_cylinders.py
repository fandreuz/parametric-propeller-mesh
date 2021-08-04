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


def compute_cylinder_anchors(
    take_available_y, outer_cylinder_y_dimension, propeller_boundary
):
    """Generate a set of X,Y,Z anchors to be used during the generation of the
    cylinders. X and Z will be used as the center coordinate of the cylinder
    on the corresponding axis. The interpretation of the Y anchor varies with
    the index of the cylinder.

    If the cylinder is the outermost one, the Y anchor is the end of the stem
    of the propeller, which means that the biggest Y coordinate reached by
    the outermost cylinder will match the Y anchor.

    Otherwise, the Y anchor is the starting Y point of the cylinder, i.e. its
    lowest Y coordinate.

    A 1D array of float values is required to specify the Y position of the
    cylinders (except for the outermost one, which is already fixed according
    to what we stated above). Each cylinder, starting from the innermost one,
    "arrives" in a situtation where a fixed amount of space is available.

    For instance, let :math:`O_y` be the lowest Y coordinate reached
    by the outermost cylinder. Note that this value is uniquely determined since
    we already know the y dimension of each cylinder, and we also now the
    biggest Y coordinate reached by the outermost cylinder). Let :math:`x_y` be
    the lowest Y coordinate reached by the propeller tip. When the innermost
    cylinder is inserted, the amount of space available is :math:`O_y - x_y`.
    When we insert the second cylinder, the amount of space available is
    :math:`O_y - I_y`, where :math:`I_y` is the lowest Y coordinate reached
    by the innermost cylinder, and so on.

    The parameter `take_available_y` is needed to specify how much of
    the available space the cylinder has to take at each step. It must be a
    subset of :math:`(0,1)`, since the borders of two cylinders cannot overlap.

    The first item is the amount of available space taken by the innermost
    cylinder, the last is the amount of available space taken by the last
    cylinder which is not the outermost (since the outermost cylinder is already
    fixed).

    For instance, if `take_available_y=[0.1,0.5]` the innermost cylinder will
    take 1/10 of the available space, and the middle cylinder will take 1/2 of
    what's available after the first step (note that the available space changes
    step by step).

    :param take_available_y: The amount of available space on the Y axis that
        each cylinder has to take, must be a subset of (0,1).
    :type take_available_y: list
    :param outer_cylinder_y_dimension: The Y dimension of the outermost
        cylinder.
    :type outer_cylinder_y_dimension: float
    :param propeller_boundary: A 2D array which represents the boundary of the
        propeller (first row minimum, second row maximum, one column for each
        axis).
    :type propeller_boundary: np.ndarray
    :return: A 2D array which contains the X,Y,Z anchors (one row for each
        cylinder).
    :rtype: np.ndarray
    """

    propeller_middle = np.sum(propeller_boundary, axis=0) / 2

    outer_anchor = np.array(
        [propeller_middle[0], propeller_boundary[1, 1], propeller_middle[2]]
    )[None, :]

    outer_cylinder_y_min = (
        propeller_boundary[1, 1] - outer_cylinder_y_dimension
    )

    middle_layer = np.repeat(
        np.array([propeller_middle[0], np.nan, propeller_middle[2]])[None, :],
        repeats=len(take_available_y),
        axis=0,
    )

    # space_left is the space between the outlet and the tip of the propeller
    # it is updated as soon a cylinder erases the space left
    space_left = outer_cylinder_y_dimension - (
        propeller_boundary[1, 1] - propeller_boundary[0, 1]
    )
    for idx in range(len(take_available_y)):
        if idx == 0:
            base = propeller_boundary[0, 1]
        else:
            base = middle_layer[idx - 1, 1]

        # taking only take_available_y[idx] * space_left would be wrong, we need
        # to append this quantity to the last known base
        middle_layer[idx, 1] = base - take_available_y[idx] * space_left
        space_left = middle_layer[idx, 1] - outer_cylinder_y_min

    return np.concatenate([middle_layer, outer_anchor], axis=0)


def generate_cylinders_obj(
    dimensions,
    anchors,
    names,
    base_folder=".",
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

    if dimensions.shape[0] != anchors.shape[0]:
        raise ValueError(
            """You probably supplied a wrong number of values to
            `compute_cylinder_anchors`"""
        )

    base_cylinder = ObjHandler.read("res/cylinder.obj")
    base_dimension = ObjHandler.dimension(base_cylinder)

    for expected_dimension, name, idx, anchor in zip(
        dimensions, names, range(len(dimensions)), anchors
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

            base_cylinder.regions.append(name)
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
                map(lambda s: name + s, ["Inlet", "Outlet", "Wall"])
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

        ObjHandler.write(base_cylinder, base_folder + "/" + name + ".obj")

        if idx == len(dimensions) - 1:
            return ObjHandler.boundary(base_cylinder, axis=1)
        else:
            # after scaling we unscale to reset che changes to the base cylinder
            ObjHandler.scale(base_cylinder, 1 / scale_factors)
            ObjHandler.translate(base_cylinder, -translation_vector)


def adjust_dimensions(cylinder_dimensions, cylinder_anchors):
    # replace np.nan to match the bigges Y coordinate of Z
    nans = np.isnan(cylinder_dimensions[:, 1])
    maxy = cylinder_anchors[-1, 1]
    cylinder_dimensions[nans, 1] = maxy - cylinder_anchors[nans, 1]

    # check that coords are non-decreasing
    shifted = np.concatenate(
        [np.zeros((1, cylinder_dimensions.shape[1])), cylinder_dimensions[:-1]]
    )
    if np.any(cylinder_dimensions < shifted):
        raise ValueError("Invalid dimension of cylinders")

    # verify that the dimension of the last cylinder is high enough to contain
    # all the others
    cylinder_boundaries_maxy = (
        cylinder_anchors[:, 1] + cylinder_dimensions[:, 1]
    )
    cylinder_boundaries_maxy[-1] = cylinder_anchors[-1, 1]

    cylinder_boundaries_miny = cylinder_anchors[:, 1]
    cylinder_boundaries_miny[-1] = (
        cylinder_anchors[-1, 1] - cylinder_dimensions[-1, 1]
    )

    if (
        np.max(cylinder_boundaries_maxy) != cylinder_boundaries_maxy[-1]
        or np.min(cylinder_boundaries_miny) != cylinder_boundaries_miny[-1]
    ):
        raise ValueError(
            "The outer cylinder does not enclose the internal cylinders"
        )

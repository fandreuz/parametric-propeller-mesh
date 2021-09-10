import numpy as np

# refinementRegions in snappyHesMeshDict
refinement_values = [5, 4, 3]

N_of_cylinders = 4

# wrt the propeller diameter
# np.nan means "up to the maximum Y coordinate of outerCylinder"
cylinder_scales = [
    [1.1, np.nan, 1.1],
    [2, np.nan, 2],
    [3, np.nan, 3],
    [5, 9, 5],
]

# ydistance, check generate_cylinders.py::compute_cylinder_anchors
take_available_y = [0.0001, 0.8, 0.9]

outer_cylinder_min_surf_ref = 3
outer_cylinder_max_surf_ref = 4

propeller_min_surf_ref = 9
propeller_max_surf_ref = 10

refinement_regions_mode = 'inside'
refinement_regions_distance = '1.0'
refinement_values = [4, 3, 2, 1]

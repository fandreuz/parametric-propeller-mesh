from smithers.io.stlhandler import STLHandler
from src.read_spatial_info import (
    dimension,
    diameter,
    min_max,
    DataWrapper,
    boundary,
)
from src.generate_cylinders import (
    generate_cylinders_obj,
    compute_cylinder_dimensions,
    compute_cylinder_anchors,
    adjust_dimensions,
)
from src.openfoam_parametrizer import generate_openfoam_configuration_dicts
from pathlib import Path
import sys
from shutil import copyfile
import numpy as np
import params
# we use some parameters from params in the following code
from params import *

"""PARAMETERS
# 1: the path to the OpenFOAM folder (with the subfolders system, constant, etc)
# 2: the path to the propeller.obj

O     x------I
======= Y axis ========>

O    : outlet
I    : inlet
x    : blades
---- : stem

"""

openfoam_folder = sys.argv[1]
openfoam_path = Path(openfoam_folder)

propeller_path = sys.argv[2]

# -------------------------------  CONFIG -------------------------------------

cylinder_names = ["cylinder{}".format(i) for i in range(N_of_cylinders - 1)]
cylinder_names.append("outerCylinder")

if (
    len(take_available_y) != N_of_cylinders - 1
    or len(cylinder_scales) != N_of_cylinders
):
    raise ValueError("Unexpected number of cylinders.")

# -------------------------------  SCRIPT -------------------------------------

# first of all we read the dimension of the propeller
data = DataWrapper(propeller_path)
propeller_dimension = dimension(data)
propeller_boundary = boundary(data)
propeller_diameter = diameter(data)

propeller_newpath = str(
    openfoam_path / "constant" / "triSurface" / "propeller.obj"
)

# we copy the propeller file into the OpenFOAM folder
copyfile(propeller_path, propeller_newpath)

# then we generate the cylinders according to the dimensions specified by the
# user
cylinder_dimensions = compute_cylinder_dimensions(
    scales=cylinder_scales,
    propeller_diameter=propeller_diameter,
)

propeller_middle = np.median(propeller_boundary, axis=0)
# HERE: modifications to propeller_middle

cylinder_anchors = compute_cylinder_anchors(
    take_available_y=take_available_y,
    # the length of the outermost cylinder
    outer_cylinder_y_dimension=cylinder_dimensions[-1, 1],
    propeller_boundary=propeller_boundary,
    propeller_middle=propeller_middle
)
adjust_dimensions(cylinder_dimensions, cylinder_anchors)

miny, maxy = generate_cylinders_obj(
    dimensions=cylinder_dimensions,
    anchors=cylinder_anchors,
    base_folder=str(openfoam_path / "constant" / "triSurface"),
    names=cylinder_names,
)

# we take half of the diameter of the outer cylinder, plus an epsilon
maxx, maxz = cylinder_dimensions[-1][[0, 2]] / 2 + 0.1
minx, minz = (-maxx, -maxz)

# y is the length
yfactor = (0.21 + 0.81) * cylinder_dimensions[-1][1]

location_in_mesh_xz = cylinder_anchors[[0, 1], [0, 2]] + np.median(
    cylinder_dimensions[[0, 1], [0, 2]], axis=0
)
location_in_mesh_y = np.median(cylinder_anchors[[0, 1], 1])

# ------------------------------ CONFIG DICT----------------------------------

# generate the configuration dictionary for the script
opfoam_config_dict = dict(
    destination=openfoam_folder,
    block_mesh_point_x=[minx, maxx, maxx, minx, minx, maxx, maxx, minx],
    block_mesh_point_y=[miny, miny, maxy, maxy, miny, miny, maxy, maxy],
    block_mesh_point_z=[minz, minz, minz, minz, maxz, maxz, maxz, maxz],
    location_in_mesh="{} {} {}".format(
        location_in_mesh_xz[0], location_in_mesh_y, location_in_mesh_xz[1]
    ),
    cylinder_names=cylinder_names
)

# append the values from params
for key in filter(lambda s: not s[0] == '_', dir(params)):
    opfoam_config_dict[key] = getattr(params, key)

# then we run the parameterizer
generate_openfoam_configuration_dicts(**opfoam_config_dict)

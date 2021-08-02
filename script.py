from smithers.io.stlhandler import STLHandler
from src.read_spatial_info import dimension, diameter, min_max, DataWrapper, boundary
from src.generate_cylinders import (
    generate_cylinders_obj,
    compute_cylinder_dimensions,
    compute_cylinder_anchors,
)
from src.openfoam_parametrizer import generate_openfoam_configuration_dicts
from pathlib import Path
import sys
from shutil import copyfile

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

# first of all we read the dimension of the propeller
data = DataWrapper(propeller_path)
propeller_dimension = dimension(data)
propeller_boundary = dimension(data)
propeller_diameter = diameter(data)

propeller_newpath = str(
    openfoam_path / "constant" / "triSurface" / "propeller.obj"
)

copyfile(propeller_path,propeller_newpath)

# then we generate three cylinders
cylinder_dimensions = compute_cylinder_dimensions(
    scales=[
        [1.1, 3, 1.1],
        [2.5, 9, 2.5],
        [5, 12.7, 5],
    ],
    propeller_diameter=propeller_diameter,
)
cylinder_anchors = compute_cylinder_anchors(
    ydistance_from_innermost=[0.1, 0.5],
    # the length of the outermost cylinder
    outer_cylinder_y_dimension=cylinder_dimensions[-1, 1],
    propeller_boundary=propeller_boundary,
)

miny, maxy = generate_cylinders_obj(
    dimensions=cylinder_dimensions,
    anchors=cylinder_anchors,
    base_folder=str(openfoam_path / "constant" / "triSurface"),
)

# we take half of the diameter of the outer cylinder, plus an epsilon
maxx, maxz = cylinder_dimensions[-1][[0, 2]] / 2 + 0.1
minx, minz = (-maxx, -maxz)

# y is the length
yfactor = (0.21 + 0.81) * cylinder_dimensions[-1][1]

# then we generate the parametrized dictionaries
generate_openfoam_configuration_dicts(
    destination=openfoam_folder,
    # OpenFOAM parameters
    decompose_nx=4,
    decompose_ny=4,
    decompose_nz=4,
    minx=minx,
    maxx=maxx,
    miny=miny,
    maxy=maxy,
    minz=minz,
    maxz=maxz,
)

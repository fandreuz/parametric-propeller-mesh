from smithers.io.stlhandler import STLHandler
from src.read_stl_spatial_info import dimension, diameter, min_max
from src.generate_cylinders import (
    generate_cylinders_obj,
    compute_cylinder_dimensions,
)
from src.openfoam_parametrizer import generate_openfoam_configuration_dicts
from pathlib import Path
import sys

openfoam_folder = sys.argv[1]
propeller_path = sys.argv[2]
stl = STLHandler.read(propeller_path)

# first of all we read the dimension of the propeller
propeller_dimension = dimension(stl)
propeller_diameter = diameter(stl)

# then we generate three cylinders
cylinder_dimensions = compute_cylinder_dimensions(
    scales=[
        [1.1, 3, 1.1],
        [2.5, 9, 2.5],
        [5, 12, 5],
    ],
    propeller_diameter=propeller_diameter,
)
generate_cylinders_obj(
    dimensions=cylinder_dimensions,
    base_folder=str(Path(openfoam_folder) / "constant" / "triSurface"),
)

# we take half of the diameter of the outer cylinder, plus an epsilon
maxx,maxz = cylinder_dimensions[-1][[0,2]]/2 + 0.1
minx,minz = (-maxx,-maxz)

# y is the length
yfactor = (0.21 + 0.81) * cylinder_dimensions[-1][1]
miny = - 0.81 / yfactor
maxy = 0.21 / yfactor

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
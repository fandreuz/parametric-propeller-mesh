from pathlib import Path
from operator import itemgetter
from src.steroid_dict import SteroidDict
from string import Template
from .utils import find_balanced


class CaseTemplate(Template):
    delimiter = "@"


parametrized_files = [
    "constant/dynamicMeshDict",
    "system/blockMeshDict",
    "system/createBafflesDict",
    "system/decomposeParDict",
    "system/snappyHexMeshDict",
    "system/surfaceFeaturesDict",
]

geometry_member_template = """    @cylinder_names_noouter
    {
        type        triSurfaceMesh;
        file        "@cylinder_names_noouter.obj";
        regions
        {
            @cylinder_names_noouter
            {
                 name       @cylinder_names_noouter;
            }
        }
    }"""
geometry_fullstring = """@geometry_member
    outerCylinder
    {
        type        triSurfaceMesh;
        file        "outerCylinder.obj";
        regions
        {
            outerCylinderWall
            {
                 name       outerCylinder;
            }
            outerCylinderInlet
            {
                 name       inlet;
            }
            outerCylinderOutlet
            {
                 name       outlet;
            }
        }
    }
    propeller
    {
        type        triSurfaceMesh;
        file        "propeller.obj";
        regions
        {
            propellerStem
            {
                 name       propellerStem;
            }
            propellerTip
            {
                 name       propellerTip;
            }
        }
    }"""

refinement_regions_template = """        @cylinder_names
        {
            mode        @refinement_regions_mode;
            levels      ((@refinement_regions_distance @refinement_values));
        }"""
refinement_regions_fullstring = "@refinement_regions_list"

features_fullstring = """        {
            file        "outerCylinder.eMesh";
            level       2;
        }
        {
            file        "propeller.eMesh";
            level       4;
        }"""

refinement_surfaces_fullstring = """        cylinder0
        {
            level   (0 0);
            cellZone    cylinder0;
            faceZone    cylinder0;
            cellZoneInside  inside;
        }
        outerCylinder
        {
            level   (@outer_cylinder_min_surf_ref @outer_cylinder_max_surf_ref);
            regions
            {
                inlet
                {
                    level   (@outer_cylinder_max_surf_ref @outer_cylinder_max_surf_ref);
                    patchInfo
                    {
                        type        patch;
                    }
                }
                outlet
                {
                    level   (@outer_cylinder_max_surf_ref @outer_cylinder_max_surf_ref);
                    patchInfo
                    {
                        type        patch;
                    }
                }
            }
        }
        propeller
        {
            level   (@propeller_min_surf_ref @propeller_max_surf_ref);
        }"""

location_in_mesh_fullstring = "@location_in_mesh"

block_mesh_dimensions_member_template = "    (@block_mesh_point_x @block_mesh_point_y @block_mesh_point_z)"
block_mesh_dimensions_fullstring = """@block_mesh_dimensions_members"""

dictionary = SteroidDict()
dictionary["cylinder_names_noouter"] = lambda dc: dc["cylinder_names"][:-1]
dictionary.set_computable_template(
    "geometry_member", geometry_member_template, repetable=True
)
dictionary.set_computable_template(
    "refinement_regions_list", refinement_regions_template, repetable=True
)
dictionary.set_computable_template(
    "block_mesh_dimensions_members", block_mesh_dimensions_member_template, repetable=True
)

full_strings = [
    ('geometry', '{', geometry_fullstring),
    ('refinementRegions', '{', refinement_regions_fullstring),
    ('features', '(', features_fullstring),
    ('refinementSurfaces', '{', refinement_surfaces_fullstring),
    ('locationInMesh', '(', location_in_mesh_fullstring),
    ('vertices', '(', block_mesh_dimensions_fullstring),
]

def write_full_strings(s):
    for t in full_strings:
        try:
            bounds = find_balanced(s, t[0], t[1])
        except ValueError:
            continue

        if bounds is not None:
            s = s[:bounds[0]] + t[2] + s[bounds[1]:]
    return s

def write(dc, file, destination):
    s = file.read_text()
    s = write_full_strings(s)

    template = CaseTemplate(s)
    # write the modifications to the file
    content = template.substitute(dc)
    # remove the .tmpl extension
    file = file.with_name(file.name.split(".")[0])
    # write the new file to the destination
    (destination / file.parent.name / file.name).write_text(content)

def generate_openfoam_configuration_dicts(destination, **kwargs):
    if isinstance(destination, str):
        destination = Path(destination)

    dictionary.update(kwargs)

    for path in parametrized_files:
        file = destination / path
        write(dictionary, file, destination)

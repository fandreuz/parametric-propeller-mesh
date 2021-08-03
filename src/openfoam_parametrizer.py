from pathlib import Path
from operator import itemgetter
from src.steroid_dict import SteroidDict
from string import Template


class CaseTemplate(Template):
    delimiter = "@"


parametrized_files = [
    "constant/dynamicMeshDict.tmpl",
    "system/blockMeshDict.tmpl",
    "system/createBafflesDict.tmpl",
    "system/decomposeParDict.tmpl",
    "system/snappyHexMeshDict.tmpl",
    "system/surfaceFeaturesDict.tmpl",
]

searchable_surface_list_string = """    @cylinder_names_noouter
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

refinement_regions_string = """        @cylinder_names_noouter
        {
            mode        inside;
            levels      ((1E15 @refinement_values));
        }"""

default_values = dict(
    decompose_nx=1,
    decompose_ny=4,
    decompose_nz=1,
    minx=-0.3,
    maxx=0.3,
    miny=-0.81,
    maxy=0.21,
    minz=-0.3,
    maxz=0.3,
)

dictionary = SteroidDict(default_values)
dictionary["cylinder_names_noouter"] = lambda dc: dc["cylinder_names"][:-1]
dictionary.set_computable_template(
    "searchable_surface_list", searchable_surface_list_string, repetable=True
)
dictionary.set_computable_template(
    "refinement_regions_list", refinement_regions_string, repetable=True
)


def write(dc, file, destination):
    template = CaseTemplate(file.read_text())
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

    openfoam_folder = Path("res/openfoam_folder")
    for path in parametrized_files:
        file = openfoam_folder / path
        write(dictionary, file, destination)

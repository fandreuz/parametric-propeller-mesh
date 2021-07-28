from string import Template
from pathlib import Path

parametrized_files = [
    "constant/dynamicMeshDict.tmpl",
    "system/blockMeshDict.tmpl",
    "system/createBafflesDict.tmpl",
    "system/decomposeParDict.tmpl",
    "system/snappyHexMeshDict.tmpl",
    "system/surfaceFeaturesDict.tmpl",
]

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


class CaseTemplate(Template):
    delimiter = "@"


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

    # we use default values for those not provided
    dc = default_values.copy()
    dc.update(kwargs)

    openfoam_folder = Path("res/openfoam_folder")
    for path in parametrized_files:
        file = openfoam_folder / path
        write(dc, file, destination)

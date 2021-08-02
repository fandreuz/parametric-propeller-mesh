from src.generate_cylinders import (
    compute_cylinder_dimensions,
    generate_cylinders_obj,
    compute_cylinder_anchors,
)
import numpy as np
import pytest
from smithers.io.obj import ObjHandler

# ------------------------
# test cylinder dimensions
# ------------------------


def test_compute_cylinder_dimensions_scale():
    result = compute_cylinder_dimensions(
        scales=[[1, 2, 1], [2, 2.5, 2], [4, 3, 4]], propeller_diameter=0.5
    )

    expected = np.array([[0.5, 1, 0.5], [1, 1.25, 1], [2, 1.5, 2]])

    np.testing.assert_almost_equal(result, expected, decimal=7)


def test_compute_cylinder_dimensions_dimensions():
    result = compute_cylinder_dimensions(
        dimensions=[[1, 2, 1], [2, 2.5, 2], [4, 3, 4]]
    )

    expected = np.array([[1, 2, 1], [2, 2.5, 2], [4, 3, 4]])

    np.testing.assert_almost_equal(result, expected, decimal=7)


# ---------------------
# test cylinder anchors
# ---------------------


def test_compute_cylinder_anchors():
    prop_boundary = np.array(
        [
            [-0.15, 0, -0.15],
            [0.35, 0.3, 0.35],
        ]
    )

    anchors = compute_cylinder_anchors([0.1, 0.5], 1, prop_boundary)

    expected = np.array(
        [
            [0.1, -0.07, 0.1],
            [0.1, -0.385, 0.1],
            [0.1, 0.3, 0.1],
        ]
    )

    np.testing.assert_allclose(anchors, expected)


# ------------------------
# test cylinder generation
# ------------------------


def test_generate_cylinders():
    anchors = np.array(
        [
            [0.1, -0.07, 0.1],
            [0.1, 0.3, 0.1],
        ]
    )

    generate_cylinders_obj(
        dimensions=np.array([[1, 1, 1], [2, 2, 2]]),
        anchors=anchors,
        paths=["tests/test_datasets/smol.obj", "tests/test_datasets/big.obj"],
    )

    smol = ObjHandler.read("tests/test_datasets/smol.obj")
    big = ObjHandler.read("tests/test_datasets/big.obj")

    np.testing.assert_allclose(ObjHandler.dimension(smol), [1, 1, 1])
    np.testing.assert_allclose(ObjHandler.dimension(big), [2, 2, 2])

    np.testing.assert_allclose(ObjHandler.boundary(smol), [[-0.4, -0.07, -0.4],[0.6, 0.93, 0.6]])
    np.testing.assert_allclose(ObjHandler.boundary(big), [[-0.9, -1.7, -0.9],[1.1, 0.3, 1.1]])


# ------------------------------------------------
# check that the appropriate expections are thrown
# ------------------------------------------------


def test_compute_cylinder_dimensions_both():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(
            scales=[[1, 2, 1], [2, 2.5, 2], [4, 3, 4]],
            dimensions=[[1, 2, 1], [2, 2.5, 2], [4, 3, 4]],
        )


def test_compute_cylinder_dimensions_none():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(propeller_diameter=2)


def test_compute_cylinder_dimensions_wrongdim():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(dimensions=[1, 2, 1])
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[1, 2, 1], propeller_diameter=2)


def test_compute_cylinder_dimensions_wrongdim2():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(dimensions=[[1, 2], [2, 2], [4, 3]])
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(
            scales=[[1, 2], [2, 2], [4, 3]], propeller_diameter=2
        )


def test_compute_cylinder_dimensions_nopropellerdiameter():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[1, 2, 1])

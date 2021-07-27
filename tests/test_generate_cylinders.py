from src.generate_cylinders import compute_cylinder_dimensions
import numpy as np
import pytest

def test_compute_cylinder_dimensions_scale():
    result = compute_cylinder_dimensions(scales=[
        [1,2,1],
        [2,2.5,2],
        [4,3,4]
    ], propeller_diameter=0.5)

    expected = np.array([
        [0.5,1,0.5],
        [1,1.25,1],
        [2,1.5,2]
    ])

    np.testing.assert_almost_equal(result, expected, decimal=7)

def test_compute_cylinder_dimensions_dimensions():
    result = compute_cylinder_dimensions(dimensions=[
        [1,2,1],
        [2,2.5,2],
        [4,3,4]
    ])

    expected = np.array([
        [1,2,1],
        [2,2.5,2],
        [4,3,4]
    ])

    np.testing.assert_almost_equal(result, expected, decimal=7)

# ------------------------------------------------
# check that the appropriate expections are thrown
# ------------------------------------------------

def test_compute_cylinder_dimensions_both():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[
        [1,2,1],
        [2,2.5,2],
        [4,3,4]
    ], dimensions=[
        [1,2,1],
        [2,2.5,2],
        [4,3,4]
    ])

def test_compute_cylinder_dimensions_none():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(propeller_diameter=2)

def test_compute_cylinder_dimensions_wrongdim():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(dimensions=[1,2,1])
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[1,2,1], propeller_diameter=2)

def test_compute_cylinder_dimensions_wrongdim2():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(dimensions=[
        [1,2],
        [2,2],
        [4,3]
    ])
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[
        [1,2],
        [2,2],
        [4,3]
    ], propeller_diameter=2)

def test_compute_cylinder_dimensions_nopropellerdiameter():
    with pytest.raises(ValueError):
        compute_cylinder_dimensions(scales=[1,2,1])


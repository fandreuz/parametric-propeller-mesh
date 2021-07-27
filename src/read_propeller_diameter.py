from smithers.io.stlhandler import STLHandler

def dimension(stl_filename: str):
    x = STLHandler.read(stl_filename)
    return np.max(x['points'], axis=0) - np.min(x['points'], axis=0)

def propeller_diameter(stl_filename: str):
    dims = dimension(stl_filename)
    # the diameter of the propeller lies on the XZ plane
    return max(dims[0], dims[2])

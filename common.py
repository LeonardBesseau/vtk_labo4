from pyproj import Transformer
import numpy as np
import vtkmodules.all as vtk

# https://epsg.org/crs_4326/WGS-84.html
# https://epsg.org/crs_3021/RT90-2-5-gon-V.html
RT90_TO_WGS84 = Transformer.from_crs(3021, 4326)

def convert_RT90_list_toWGS84(RT90_list):
    return np.array([np.asarray(RT90_TO_WGS84.transform(x[1], x[0])) for x in RT90_list])


def convert_to_cartesian(longitude, latitude, elevation):
    transform = vtk.vtkTransform()
    transform.RotateX(latitude)
    transform.RotateY(longitude)
    return transform.TransformPoint((0, 0, elevation))
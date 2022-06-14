import pandas as pd
import vtkmodules.all as vtk
import numpy as np
from common import convert_RT90_toWGS84, convert_to_cartesian, EARTH_RADIUS

GLIDER_PATH_RADIUS = 30
GLIDER_PATH_COLOR_RANGE = (-5, 5)


def get_path(glider_data_file):
    data = pd.read_table(glider_data_file, header=None, skiprows=[0], usecols=[1, 2, 3],
                         delim_whitespace=True, dtype={1: np.int32, 2: np.int32, 3: np.float64})
    # Compute elevation difference
    data[4] = data[3].diff()
    data[4] = data[4].fillna(0)  # clean up Nan
    data[4] = -data[4]

    # Convert coordinates to WGS84
    data[1], data[2] = convert_RT90_toWGS84(data[1], data[2])

    data[5] = data.apply(lambda x: convert_to_cartesian(x[1], x[2], x[3] + EARTH_RADIUS), axis=1)

    return data[4], data[5]


def get_glider(glider_data_file):
    elevations, coordinates = get_path(glider_data_file)

    # generate Path
    points = vtk.vtkPoints()
    elevations_points = vtk.vtkFloatArray()

    for coordinate, elevation in zip(coordinates, elevations):
        points.InsertNextPoint(coordinate)
        elevations_points.InsertNextValue(elevation)

    line = vtk.vtkLineSource()
    line.SetPoints(points)
    line.Update()

    line_data = line.GetOutput()
    line_data.GetPointData().SetScalars(elevations_points)

    tube = vtk.vtkTubeFilter()
    tube.SetRadius(GLIDER_PATH_RADIUS)
    tube.SetInputConnection(line.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    mapper.SetScalarRange(GLIDER_PATH_COLOR_RANGE)

    output = vtk.vtkActor()
    output.SetMapper(mapper)

    return output

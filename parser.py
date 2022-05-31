import numpy as np
import vtkmodules.all as vtk
from pyproj import Transformer
import math

# https://epsg.org/crs_4326/WGS-84.html
# https://epsg.org/crs_3021/RT90-2-5-gon-V.html
RT90_TO_WGS84 = Transformer.from_crs(3021, 4326)

# down_left, down_right, upper_left, upper_right
MAP_LIMITS_RT90 = [(1349602, 7005969), (1371835, 7006362), (1371573, 7022967), (1349340, 7022573)]
ELEVATION_LIMITS_WGS84 = [(60, 10), (65, 15)]
ELEVATION_DATA_DIMENSIONS = (6000, 6000)
EARTH_RADIUS = 6371009

QUAD_INTERPOLATION_MATRIX = np.array([[1, 0, 0, 0], [-1, 1, 0, 0], [-1, 0, 0, 1], [1, -1, 1, -1]])


def convert_RT90_list_toWGS84(RT90_list):
    return [RT90_TO_WGS84.transform(x[1], x[0]) for x in RT90_list]


def convert_to_cartesian(longitude, latitude, elevation):
    transform = vtk.vtkTransform()
    transform.RotateX(latitude)
    transform.RotateY(longitude)
    return transform.TransformPoint((0, 0, elevation))


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def read_elevation(elevation_file):
    data = np.fromfile(elevation_file, dtype=np.int16)

    longitude_coords = np.linspace(ELEVATION_LIMITS_WGS84[0][1], ELEVATION_LIMITS_WGS84[1][1],
                                   ELEVATION_DATA_DIMENSIONS[1])
    latitude_coords = np.linspace(ELEVATION_LIMITS_WGS84[0][0], ELEVATION_LIMITS_WGS84[1][0],
                                  ELEVATION_DATA_DIMENSIONS[0])

    elevation_points = vtk.vtkPoints()
    elevation_value = vtk.vtkIntArray()
    texture_coords = vtk.vtkFloatArray()
    texture_coords.SetNumberOfComponents(2)

    for longitude in range(ELEVATION_DATA_DIMENSIONS[1]):
        if 12.802148375908851 <= longitude_coords[longitude] <= 13.262723166975816:
            for latitude in range(ELEVATION_DATA_DIMENSIONS[0]):
                if 63.13203595611243 <= latitude_coords[latitude] <= 63.29286525347288:
                    elevation = data[latitude + longitude * ELEVATION_DATA_DIMENSIONS[1]]
                    p = convert_to_cartesian(longitude_coords[longitude], latitude_coords[latitude],
                                             EARTH_RADIUS + elevation)
                    elevation_points.InsertNextPoint(p)
                    elevation_value.InsertNextValue(elevation)
                    x = translate(longitude_coords[longitude], 12.802148375908851, 13.262723166975816, 0, 1024)
                    y = translate(latitude_coords[latitude], 63.13203595611243, 63.29286525347288, 0, 768)
                    texture_coords.InsertNextTuple2(x, y)

    a = longitude_coords >= 12.802148375908851
    b = longitude_coords <= 13.262723166975816
    cols = longitude_coords[a & b].size
    c = latitude_coords >= 63.13203595611243
    d = latitude_coords <= 63.29286525347288
    rows = latitude_coords[c & d].size

    limits_wgs84 = convert_RT90_list_toWGS84(MAP_LIMITS_RT90)

    # lower_bound = latitudes >= 63.13203595611243
    # upper_bound = latitudes <= 63.29286525347288
    # left_bound = longitudes >= 12.802148375908851
    # right_bound = longitudes <= 13.262723166975816

    # longitude = limits_wgs84[0][1]
    #
    # for longitude, latitude, elevation in zip(longitudes, latitudes, data):
    #     p = convert_to_cartesian(longitude, latitude, EARTH_RADIUS + elevation)
    #     p1 = polar_to_cartesian(longitude, latitude, EARTH_RADIUS + elevation)
    #     elevation_points.InsertNextPoint(p)
    #     elevation_value.InsertNextValue(elevation)
    #     texture_coords.InsertNextTuple2(longitude, latitude)

    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(rows, cols, 1)
    grid.SetPoints(elevation_points)
    grid.GetPointData().SetScalars(elevation_value)
    grid.GetPointData().SetTCoords(texture_coords)

    return grid

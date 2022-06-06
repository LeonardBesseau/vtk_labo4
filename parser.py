import math
import vtkmodules.all as vtk
import numpy as np

from common import convert_to_cartesian, convert_RT90_list_toWGS84, EARTH_RADIUS

# down_left, down_right, upper_left, upper_right
MAP_LIMITS_RT90 = [(1349602, 7005969), (1371835, 7006362), (1371573, 7022967), (1349340, 7022573)]
MAP_AREA_RT90 = [(1349602, 7005969), (1371835, 7006362), (1371573, 7022967), (1349340, 7022573)]
ELEVATION_LIMITS_WGS84 = [(60, 10), (65, 15)]
ELEVATION_DATA_DIMENSIONS = (6000, 6000)



def compute_quad_values(map_values):
    # Matrix used to compute the interpolation of a quadrilateral
    # https://www.particleincell.com/2012/quad-interpolation/
    quad_interpolation_matrix = np.array([[1, 0, 0, 0], [-1, 1, 0, 0], [-1, 0, 0, 1], [1, -1, 1, -1]])
    alpha = quad_interpolation_matrix.dot(map_values[:, 0])
    beta = quad_interpolation_matrix.dot(map_values[:, 1])
    return alpha, beta


def quadInterpolation(x, y, a, b):
    """
    Compute quad interpolation from physical world to logical world
    https://www.particleincell.com/2012/quad-interpolation/
    """
    # quadratic equation coeffs, aa*mm^2+bb*m+cc=0
    aa = a[3] * b[2] - a[2] * b[3]
    bb = a[3] * b[0] - a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + x * b[3] - y * a[3]
    cc = a[1] * b[0] - a[0] * b[1] + x * b[1] - y * a[1]

    # compute m = (-b+sqrt(b^2-4ac))/(2a)
    det = math.sqrt(bb ** 2 - 4 * aa * cc)
    m = (-bb - det) / (2 * aa)

    # compute l
    l = (x - a[0] - a[2] * m) / (a[1] + a[3] * m)

    return l, m


def generate_clip_function(limits):
    # I could not manage to intersect a quad with the grid, so we do it manually with 4 plane
    clip_function = vtk.vtkImplicitBoolean()
    clip_function.SetOperationTypeToIntersection()

    p0 = np.array([0, 0, 0])
    p1 = np.array(convert_to_cartesian(*limits[0], 1))
    p2 = np.array(convert_to_cartesian(*limits[1], 1))
    p3 = np.array(convert_to_cartesian(*limits[2], 1))
    p4 = np.array(convert_to_cartesian(*limits[3], 1))
    for p in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
        n = -np.cross(p[0] - p0, p[1] - p0)
        plane = vtk.vtkPlane()
        plane.SetNormal(n)
        clip_function.AddFunction(plane)
    return clip_function


def get_mesh(elevation_file):
    data = np.fromfile(elevation_file, dtype=np.int16)

    limits_wgs84 = convert_RT90_list_toWGS84(MAP_LIMITS_RT90)
    # Get quad interpolation matrices based on map limits
    alpha, beta = compute_quad_values(limits_wgs84)

    # Generate position matrix
    longitudes, latitudes = np.meshgrid(
        np.linspace(ELEVATION_LIMITS_WGS84[0][1], ELEVATION_LIMITS_WGS84[1][1], ELEVATION_DATA_DIMENSIONS[1]),
        np.linspace(ELEVATION_LIMITS_WGS84[1][0], ELEVATION_LIMITS_WGS84[0][0], ELEVATION_DATA_DIMENSIONS[0]))
    latitudes, longitudes = latitudes.flatten(), longitudes.flatten()

    # Mask based on maps limits
    lower_bound_mask = latitudes >= limits_wgs84[:, 0].min()
    upper_bound_mask = latitudes <= limits_wgs84[:, 0].max()
    left_bound_mask = longitudes >= limits_wgs84[:, 1].min()
    right_bound_mask = longitudes <= limits_wgs84[:, 1].max()

    rows = latitudes[upper_bound_mask & lower_bound_mask].size // ELEVATION_DATA_DIMENSIONS[0]
    cols = longitudes[left_bound_mask & right_bound_mask].size // ELEVATION_DATA_DIMENSIONS[1]

    # Filter data
    latitudes = latitudes[upper_bound_mask & lower_bound_mask & left_bound_mask & right_bound_mask]
    longitudes = longitudes[upper_bound_mask & lower_bound_mask & left_bound_mask & right_bound_mask]
    elevations = data[upper_bound_mask & lower_bound_mask & left_bound_mask & right_bound_mask]

    elevation_points = vtk.vtkPoints()
    elevation_value = vtk.vtkIntArray()
    texture_points = vtk.vtkFloatArray()
    texture_points.SetNumberOfComponents(2)
    for latitude, longitude, elevation in zip(latitudes, longitudes, elevations):
        p = convert_to_cartesian(latitude, longitude, elevation + EARTH_RADIUS)
        elevation_points.InsertNextPoint(p)
        elevation_value.InsertNextValue(elevation)
        texture_points.InsertNextTuple(quadInterpolation(latitude, longitude, alpha, beta))

    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(cols, rows, 1)
    grid.SetPoints(elevation_points)
    grid.GetPointData().SetScalars(elevation_value)
    grid.GetPointData().SetTCoords(texture_points)

    # Cut the grid to the dimensions of the map
    clipper = vtk.vtkClipDataSet()
    clipper.SetInputData(grid)
    clipper.SetClipFunction(generate_clip_function(limits_wgs84))
    clipper.InsideOutOn()
    clipper.Update()

    return clipper


def get_map(elevation_file, texture_file):
    mesh = get_mesh(elevation_file)
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(mesh.GetOutputPort())
    mapper.ScalarVisibilityOff()

    reader = vtk.vtkJPEGReader()
    reader.SetFileName(texture_file)

    texture = vtk.vtkTexture()
    texture.RepeatOff()
    texture.SetInputConnection(reader.GetOutputPort())

    output = vtk.vtkActor()
    output.SetMapper(mapper)
    output.SetTexture(texture)

    return output

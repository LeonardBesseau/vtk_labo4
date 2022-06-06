import vtkmodules.all as vtk

from glider import get_glider_path
from parser import get_mesh, get_map

TEXTURE_FILE = "files/glider_map.jpg"
ELEVATION_FILE = "files/EarthEnv-DEM90_N60E010.bil"
GLIDER_FILE = "files/vtkgps.txt"

if __name__ == '__main__':
    a = get_glider_path(GLIDER_FILE)
    michel = get_map(ELEVATION_FILE, TEXTURE_FILE)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(michel)
    renderer.SetBackground(1, 1, 1)

    # Adds the renderer to the render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)

    # Adds controls
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    interactor.Initialize()
    render_window.Render()
    interactor.Start()

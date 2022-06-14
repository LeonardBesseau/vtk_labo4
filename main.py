import vtkmodules.all as vtk

from glider import get_glider
from interactor import MouseInteractorStyle
from parser import get_map

TEXTURE_FILE = "files/glider_map.jpg"
ELEVATION_FILE = "files/EarthEnv-DEM90_N60E010.bil"
GLIDER_FILE = "files/vtkgps.txt"

if __name__ == '__main__':
    michel = get_map(ELEVATION_FILE, TEXTURE_FILE)
    glider = get_glider(GLIDER_FILE)
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)

    renderer.AddActor(michel)
    renderer.AddActor(glider)

    # Adds the renderer to the render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 800)

    # Adds controls
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    style = MouseInteractorStyle(michel)
    style.SetDefaultRenderer(renderer)
    style.lateInit()
    interactor.SetInteractorStyle(style)

    interactor.Initialize()
    interactor.Render()

    interactor.Start()

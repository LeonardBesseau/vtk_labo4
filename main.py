import vtkmodules.all as vtk


from parser import read_elevation

TEXTURE_FILE = "files/glider_map.jpg"
ELEVATION_FILE = "files/EarthEnv-DEM90_N60E010.bil"
GLIDER_FILE = "files/vtkgps.txt"

if __name__ == '__main__':
    reader = vtk.vtkJPEGReader()
    reader.SetFileName(TEXTURE_FILE)

    texture = vtk.vtkTexture()
    texture.RepeatOff()
    texture.SetInputConnection(reader.GetOutputPort())

    grid = read_elevation(ELEVATION_FILE)
    grid_mapper = vtk.vtkDataSetMapper()
    grid_mapper.SetInputData(grid)
    michel = vtk.vtkActor()
    michel.SetMapper(grid_mapper)
    michel.SetTexture(texture)

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

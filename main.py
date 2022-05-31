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

    color_table = vtk.vtkColorTransferFunction()
    sea_level = 0
    color_table.AddRGBPoint(sea_level + 0, 0.52, 0.5, 1)
    color_table.AddRGBPoint(sea_level + 494, 0.129, 0.643, 0.318)
    color_table.AddRGBPoint(sea_level + 500, 0.573, 0.765, 0.431)
    color_table.AddRGBPoint(sea_level + 600, 0.573, 0.765, 0.431)
    color_table.AddRGBPoint(sea_level + 800, 0.949, 0.864, 0.808)
    color_table.AddRGBPoint(sea_level + 1200, 1, 1, 1)

    grid = read_elevation(ELEVATION_FILE)
    grid_mapper = vtk.vtkDataSetMapper()
    grid_mapper.SetInputData(grid)
    grid_mapper.SetLookupTable(color_table)
    michel = vtk.vtkActor()
    michel.SetMapper(grid_mapper)
    #michel.SetTexture(texture)

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

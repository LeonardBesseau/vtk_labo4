import numpy as np
import vtkmodules.all as vtk

TUBE_RADIUS = 50
TUBE_COLOR = (0.00, 0.80, 0.80)


# Catch mouse events
class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, map, *args, **kwargs):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event)
        self.map = map

        self.picker = vtk.vtkPointPicker()
        self.picker.PickFromListOn()
        self.picker.AddPickList(map)

        self.sphere = vtk.vtkSphere()

        self.cutter = vtk.vtkCutter()
        self.cutter.SetCutFunction(self.sphere)
        self.cutter.SetInputData(self.map.GetMapper().GetInput())

        self.stripper = vtk.vtkStripper()
        self.stripper.SetInputConnection(self.cutter.GetOutputPort())

        self.tube = vtk.vtkTubeFilter()
        self.tube.SetRadius(TUBE_RADIUS)
        self.tube.SetInputConnection(self.stripper.GetOutputPort())

        self.tube_mapper = vtk.vtkPolyDataMapper()
        self.tube_mapper.ScalarVisibilityOff()
        self.tube_mapper.SetInputConnection(self.tube.GetOutputPort())

        self.tube_actor = vtk.vtkActor()
        self.tube_actor.GetProperty().SetColor(TUBE_COLOR)
        self.tube_actor.SetMapper(self.tube_mapper)

    def lateInit(self):
        self.GetDefaultRenderer().AddActor(self.tube_actor)

    def left_button_press_event(self, obj, event):
        # Get the location of the click (in window coordinates)
        pos = self.GetInteractor().GetEventPosition()

        # Pick from this location.
        self.picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())
        actor = self.picker.GetActor()

        if actor == self.map:
            # Compute radius from position
            radius = np.linalg.norm(self.picker.GetPickPosition())
            self.sphere.SetRadius(radius)

            self.cutter.Update()
            self.GetInteractor().Render()

        # Forward events
        self.OnLeftButtonDown()

import numpy as np
import vtkmodules.all as vtk

# Catch mouse events
from common import EARTH_RADIUS


class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, data):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event)
        self.actor = data

    def left_button_press_event(self, obj, event):
        colors = vtk.vtkNamedColors()

        # Get the location of the click (in window coordinates)
        pos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.05)

        # Pick from this location.
        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())
        actor = picker.GetActor()

        print(picker.GetPointId())
        if actor == self.actor:
            data = actor.GetMapper().GetInput().GetPointData().GetScalars()
            points = vtk.vtkIdList()
            print()
            actor.GetMapper().GetInput().GetCellPoints(picker.GetCellId(), points)
            print("hello")
            a = [data.GetValue(points.GetId(i)) for i in range(points.GetNumberOfIds())]
            print(a)
            sphere = vtk.vtkSphere()
            sphere.SetRadius(EARTH_RADIUS + np.average(a))
            sphere.SetCenter(0, 0, 0)

            cutter = vtk.vtkCutter()
            cutter.SetCutFunction(sphere)

            cutter.SetInputData(actor.GetMapper().GetInput())
            cutter.Update()

            stripper = vtk.vtkStripper()
            stripper.SetInputConnection(cutter.GetOutputPort())

            tube = vtk.vtkTubeFilter()
            tube.SetInputConnection(stripper.GetOutputPort())
            tube.SetRadius(50)

            tube_mapper = vtk.vtkPolyDataMapper()
            tube_mapper.SetInputConnection(tube.GetOutputPort())
            tube_mapper.ScalarVisibilityOff()

            tube_actor = vtk.vtkActor()
            tube_actor.SetMapper(tube_mapper)

            self.GetDefaultRenderer().AddActor(tube_actor)
            self.GetInteractor().Render()

        # Forward events
        self.OnLeftButtonDown()

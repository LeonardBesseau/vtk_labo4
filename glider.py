import pandas as pd
import vtkmodules.all as vtk
import numpy as np


def get_glider_path(glider_data_file):
    data = pd.read_table(glider_data_file, header=None, skiprows=[0], usecols=[1, 2, 3, 4, 5],
                         delim_whitespace=True, dtype={1: np.int32, 2: np.int32, 3: np.float64})
    data[5] = pd.to_datetime((data[4] + "-" + data[5]), format="%m/%d/%y-%H:%M:%S")
    data[5] = data[5].diff().dt.seconds
    print("Hello")

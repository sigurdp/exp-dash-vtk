import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_mesh_state

#import vtkmodules.all as vtk

from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter

from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader

from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid

from vtkmodules.vtkRenderingCore import vtkDataSetMapper


# May have to try vtkXMLMultiBlockDataReader for this
#file_name = "./HeatingCoil.vtm"

file_name = "./TestData/HeatingCoil/HeatingCoil_0_0.vtu"
#file_name = "./TestData/HeatingCoil/HeatingCoil_1_0.vtu"

unstruct_reader = vtkXMLUnstructuredGridReader()
unstruct_reader.SetFileName(file_name)
unstruct_reader.Update()


num_point_arrays = unstruct_reader.GetNumberOfPointArrays()
print(f"\nnum_point_arrays={num_point_arrays}")
for i in range(num_point_arrays):
    print(unstruct_reader.GetPointArrayName(i))

num_cell_arrays = unstruct_reader.GetNumberOfCellArrays()
print(f"\nnum_cell_arrays={num_cell_arrays}")
for i in range(num_cell_arrays):
    print(unstruct_reader.GetCellArrayName(i))

print("\n\n")

my_ugrid: vtkUnstructuredGrid = unstruct_reader.GetOutput()

# print(type(my_ugrid))
# print(my_ugrid)

# print(type(my_ugrid.GetPointData()))
# print(my_ugrid.GetPointData())

scalar_range = my_ugrid.GetScalarRange()
mapper = vtkDataSetMapper()
mapper.SetInputData(my_ugrid)
mapper.SetColorModeToDefault()
mapper.SetScalarRange(scalar_range)
mapper.SetScalarVisibility(True)
#mapper.SetLookupTable(colormap)


# Similar to what's going on inside to_mesh_state()
extractSkinFilter = vtkGeometryFilter()
#extractSkinFilter = vtkOutlineFilter()
#extractSkinFilter.SetInputData(mapper.GetOutput())
extractSkinFilter.SetInputData(my_ugrid)
extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()

# print("--------------------------------------------------")
# print(polydata)
# print("--------------------------------------------------")
print(f"scalar_range={scalar_range}")

mesh_state = to_mesh_state(polydata, "Pressure")

content = dash_vtk.View(
    background=[0.5, 0, 0],
    children=[
        dash_vtk.GeometryRepresentation(
            showCubeAxes=True,
            property={
                "lighting": True,
                "edgeVisibility": True,
                #"color": [0.5, 0.5, 0.1],
                "lineWidth": 5,
                "pointSize": 5,
                "representation": 2,    # 0=points, 1=wireframe, 2=surf
            }, 
            mapper={
                "scalarVisibility" : True,
                'scalarMode': 1,
                "interpolateScalarsBeforeMapping": False
            },
            colorMapPreset="Cool to Warm",
            colorDataRange=[0,280],
            children=[
                dash_vtk.Mesh(state=mesh_state)
            ]),
    ])

# Dash setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "800px"},
    children=[content],
)

if __name__ == "__main__":
    app.run_server(debug=True)

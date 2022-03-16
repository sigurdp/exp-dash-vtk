import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_mesh_state

#import vtkmodules.all as vtk

from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter


# Use VTK to get some data
data_source = vtkRTAnalyticSource()
data_source.Update()  # <= Execute source to produce an output
dataset = data_source.GetOutput()

# Use helper to get a mesh structure that can be passed as-is to a Mesh
# RTData is the name of the field
mesh_state = to_mesh_state(dataset)

# Similar to what's going on inside to_mesh_state()
#extractSkinFilter = vtkGeometryFilter()
extractSkinFilter = vtkOutlineFilter()
extractSkinFilter.SetInputData(dataset)
extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()
mesh_state = to_mesh_state(polydata)

content = dash_vtk.View([
    dash_vtk.GeometryRepresentation([
        dash_vtk.Mesh(state=mesh_state)
        
    ]),
])

# Dash setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "400px"},
    children=[content],
)

if __name__ == "__main__":
    app.run_server(debug=True)

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
#mesh_state = to_mesh_state(dataset)
#print(dataset)

extractSkinFilter = vtkGeometryFilter()
#extractSkinFilter = vtkOutlineFilter()
extractSkinFilter.SetInputData(dataset)
extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()
mesh_state = to_mesh_state(polydata)

# See:
# https://dash.plotly.com/vtk/representations

content = dash_vtk.View(
    background=[0.5, 0, 0],
    children=[
        dash_vtk.GeometryRepresentation(
            showCubeAxes=True,
            property={
                "lighting": True,
                "edgeVisibility": True,
                "color": [0.5, 0.5, 0.1],
                "lineWidth": 5,
                "pointSize": 5,
                "representation": 0,    # 0=points, 1=wireframe, 2=surf
            }, 
            children=[
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

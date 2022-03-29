import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_mesh_state

from vtkmodules.vtkFiltersGeometry import vtkExplicitStructuredGridSurfaceFilter


import numpy as np
import pyvista as pv


import grid_factory


grid = grid_factory.create_explicit_structured_grid(5, 4, 3, 20.0, 10.0, 5.0)

extractSkinFilter = vtkExplicitStructuredGridSurfaceFilter()
extractSkinFilter.SetInputData(grid)
extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()

# grid = grid.cast_to_unstructured_grid()
# polydata = grid.extract_geometry()


skin_mesh_state = to_mesh_state(polydata)

z = 15.0
line_verts = np.array([(5.0, 5.0, z), (15.0, 12.0, z), (25.0, 23.0, z), (70.0, 31.0, z), (65.0, 15.0, z)])
#line_verts = np.array([(-5.0, -1.0, z), (15.0, 12.0, z), (19.0, 23.0, z), (105.0, 38.0, z), (85.0, 25.0, z)])
#line_verts = np.array([(-5.0, -1.0, z), (105.0, 38.0, z)])
vertex_count = len(line_verts)
line_conn = np.array([5, 0, 1, 2, 3, 4])
#line_conn = np.array([4, 0, 1, 2, 3])
#line_conn = np.array([3, 0, 1, 1])
my_polyline = pv.PolyData(line_verts, lines=line_conn);
polyline_mesh_state = to_mesh_state(my_polyline)

intersection = grid.slice_along_line(my_polyline)
print(intersection)
#intersection = grid.slice(normal=(-1.0, 2.3, 0.0), origin=(0.0, 0.0, 0.0), generate_triangles=True)
isect_mesh_state = to_mesh_state(intersection)


content = dash_vtk.View([
    dash_vtk.GeometryRepresentation(
        property={
            "lighting": True,
            "edgeVisibility": True,
            "color": [0.5, 0.5, 0.1],
            "lineWidth": 5,
            "pointSize": 5,
            "representation": 1,    # 0=points, 1=wireframe, 2=surf
        }, 
        children=[
            dash_vtk.Mesh(state=skin_mesh_state)
        ]
    ),
    dash_vtk.GeometryRepresentation(
        property={
            "lighting": False,
            "color": [1.0, 1.0, 0.1],
            "pointSize": 5,
            "representation": 0,    # 0=points, 1=wireframe, 2=surf
        }, 
        children=[
            dash_vtk.Mesh(state=polyline_mesh_state),
        ]
    ),
    dash_vtk.GeometryRepresentation(
        property={
            "lighting": False,
            "color": [1.0, 0.5, 0.1],
            "lineWidth": 5,
        }, 
        children=[
            dash_vtk.Mesh(state=polyline_mesh_state),
        ]
    ),
    dash_vtk.GeometryRepresentation(
        property={
            "lighting": False,
            "edgeVisibility": True,
            "color": [0.3, 0.8, 0.1],
            "lineWidth": 5,
        }, 
        children=[
            dash_vtk.Mesh(state=isect_mesh_state),
        ]
    ),
])

# Dash setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "1000px"},
    children=[content],
)

if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_mesh_state

from vtkmodules.vtkFiltersGeometry import vtkExplicitStructuredGridSurfaceFilter
from vtkmodules.vtkCommonDataModel import vtkPolyPlane
from vtkmodules.vtkCommonDataModel import vtkCellLocator
from vtkmodules.vtkFiltersCore import vtkCutter
from vtkmodules.vtkFiltersCore import vtkImplicitPolyDataDistance 
from vtkmodules.vtkFiltersCore import vtkImplicitPolyDataDistance 
from vtkmodules.vtkCommonCore import vtkIdList 

# Not yet available!
#from vtkmodules.vtkFiltersCore import vtkExtractCellsAlongPolyLine

import numpy as np
import pyvista as pv


import grid_factory


grid = grid_factory.create_explicit_structured_grid(5, 4, 3, 20.0, 10.0, 5.0)

test_cell_blanking = True
if test_cell_blanking:
    cellLocator = vtkCellLocator()
    cellLocator.SetDataSet(grid)
    cellLocator.BuildLocator()
    cellIds = vtkIdList()
    cellLocator.FindCellsAlongLine((6.0, 6.0, 12.0), (67.0, 12.0, 12.0), 0.001, cellIds)
    for i in range(cellIds.GetNumberOfIds()):
        id = cellIds.GetId(i)
        grid.BlankCell(id)



extractSkinFilter = vtkExplicitStructuredGridSurfaceFilter()
extractSkinFilter.SetInputData(grid)
extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()

# grid = grid.cast_to_unstructured_grid()
# polydata = grid.extract_geometry()


skin_mesh_state = to_mesh_state(polydata)

z = 14.0
line_verts = np.array([(-5.0, -1.0, z), (5.0, 5.0, z), (6.0, 5.0, z), (7.0, 4.0, z), (8.0, 9.0, z), (15.0, 12.0, z), (25.0, 23.0, z), (70.0, 31.0, z), (65.0, 15.0, z), (66.0, -2.0, z)])
#line_verts = np.array([(-5.0, -1.0, z), (5.0, 5.0, z), (6.0, 5.0, z), (7.0, 4.0, z), (8.0, 9.0, z), (15.0, 12.0, z), (25.0, 23.0, z), (70.0, 31.0, z), (65.0, 15.0, z)])
#line_verts = np.array([(5.0, 5.0, z), (6.0, 5.0, z), (7.0, 4.0, z), (8.0, 9.0, z), (15.0, 12.0, z), (25.0, 23.0, z), (70.0, 31.0, z), (65.0, 15.0, z)])
#line_verts = np.array([(5.0, 5.0, z), (15.0, 12.0, z), (25.0, 23.0, z), (70.0, 31.0, z), (65.0, 15.0, z)])
#line_verts = np.array([(-5.0, -1.0, z), (15.0, 12.0, z), (19.0, 23.0, z), (105.0, 38.0, z), (85.0, 25.0, z)])
#line_verts = np.array([(-5.0, -1.0, z), (105.0, 38.0, z)])

vertex_count = len(line_verts)
line_conn = np.arange(-1, vertex_count)
line_conn[0] = vertex_count

my_polyline = pv.PolyData(line_verts, lines=line_conn);
polyline_mesh_state = to_mesh_state(my_polyline)


cut_func = vtkPolyPlane()
cut_func.SetPolyLine(my_polyline.GetCell(0))


# poly_verts = line_verts.repeat(2, axis=0)
# poly_verts = poly_verts.reshape(-1, 3)
# num_poly_verts = 2*len(line_verts)
# for i in range(1, num_poly_verts, 2):
#     poly_verts[i][2] = 10.0

# num_polys = int(len(poly_verts)/2 - 1)
# poly_conn = np.zeros(5*num_polys, dtype=int)
# for i in range(0, num_polys):
#     poly_conn[5*i] = 4
#     poly_conn[5*i + 1] = 2*i
#     poly_conn[5*i + 2] = 2*i + 1
#     poly_conn[5*i + 3] = 2*i + 3
#     poly_conn[5*i + 4] = 2*i + 2

# print(poly_verts)
# print(poly_conn)

# cut_poly_data = pv.PolyData(poly_verts, faces=poly_conn);
# cut_func = vtkImplicitPolyDataDistance()
# cut_func.SetInput(cut_poly_data)


alg = vtkCutter()
alg.SetInputDataObject(grid)
alg.SetCutFunction(cut_func)
alg.Update()
intersection = alg.GetOutput()

#intersection = grid.slice_along_line(my_polyline)
#intersection = grid.slice(normal=(-1.0, 2.3, 0.0), origin=(0.0, 0.0, 0.0), generate_triangles=True)

# Does not yet exist in the VTK version
# alg = vtkExtractCellsAlongPolyLine()
# alg.SetInput(0, grid)
# alg.SetInput(1, my_polyline)
# alg.Update()
# intersection = alg.GetOutput()

isect_mesh_state = to_mesh_state(intersection)


content = dash_vtk.View([
    dash_vtk.GeometryRepresentation(
        property={
            "lighting": True,
            "edgeVisibility": True,
            "opacity": 0.5,
            "color": [0.5, 0.5, 0.1],
            "lineWidth": 5,
            "pointSize": 5,
            "representation": 2,    # 0=points, 1=wireframe, 2=surf
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
    # dash_vtk.GeometryRepresentation(
    #     property={
    #         "color": [0.8, 0.2, 0.1],
    #         "edgeVisibility": True,
    #         "representation": 2,    # 0=points, 1=wireframe, 2=surf
    #     }, 
    #     children=[
    #         dash_vtk.Mesh(state=to_mesh_state(cut_poly_data)),
    #     ]
    # ),
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

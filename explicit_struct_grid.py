import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_mesh_state

import numpy as np
import pyvista as pv

from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersGeometry import vtkExplicitStructuredGridSurfaceFilter
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersCore import vtkExplicitStructuredGridCrop



# grid size: ni*nj*nk cells; si, sj, sk steps
ni, nj, nk = 4, 5, 6
si, sj, sk = 20, 10, 1

# create raw coordinate grid
grid_ijk = np.mgrid[:(ni+1)*si:si, :(nj+1)*sj:sj, :(nk+1)*sk:sk]

# repeat array along each Cartesian axis for connectivity
for axis in range(1, 4):
    grid_ijk = grid_ijk.repeat(2, axis=axis)

# slice off unnecessarily doubled edge coordinates
grid_ijk = grid_ijk[:, 1:-1, 1:-1, 1:-1]

# reorder and reshape to VTK order
corners = grid_ijk.transpose().reshape(-1, 3)

dims = np.array([ni, nj, nk]) + 1
grid = pv.ExplicitStructuredGrid(dims, corners)
grid = grid.compute_connectivity()
grid.ComputeFacesConnectivityFlagsArray()

print(grid)
#grid.plot()

polydata = grid.extract_surface()
#polydata = grid.cast_to_unstructured_grid().extract_geometry()
#polydata = grid.cast_to_unstructured_grid().extract_surface()

cropFilter = vtkExplicitStructuredGridCrop()
cropFilter.SetInputData(grid);
cropFilter.SetOutputWholeExtent(0, 1, 0, 2, 0, 3);
cropFilter.Update()
print(cropFilter.GetOutput())


"""
# Note that output of shrink filter is unstruct grid
shrinkFilter = vtkShrinkFilter()
shrinkFilter.SetInputData(grid);
shrinkFilter.SetShrinkFactor(.8);
shrinkFilter.Update()
shrunkenGrid = shrinkFilter.GetOutput()

extractSkinFilter = vtkGeometryFilter()
extractSkinFilter.SetInputData(shrinkFilter.GetOutput())
"""

extractSkinFilter = vtkExplicitStructuredGridSurfaceFilter()
extractSkinFilter.SetInputData(cropFilter.GetOutput())

extractSkinFilter.Update()
polydata = extractSkinFilter.GetOutput()


print(polydata)

#mesh_state = to_mesh_state(grid.cast_to_unstructured_grid())
mesh_state = to_mesh_state(polydata)

content = dash_vtk.View([
    dash_vtk.GeometryRepresentation(
        showCubeAxes=True,
        property={
            "lighting": True,
            "edgeVisibility": True,
            "color": [0.5, 0.5, 0.1],
            "lineWidth": 5,
            "pointSize": 5,
            "representation": 2,    # 0=points, 1=wireframe, 2=surf
        }, 
        children=[
            dash_vtk.Mesh(state=mesh_state)
        ]
    ),
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

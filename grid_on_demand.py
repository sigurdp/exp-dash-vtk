import os
import random

import dash
from dash import html
from dash import dcc

import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

import dash_vtk
from dash_vtk.utils import to_mesh_state, preset_as_options

import vtk

from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersGeometry import vtkExplicitStructuredGridSurfaceFilter
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersCore import vtkExplicitStructuredGridCrop


import numpy as np
import pyvista as pv

random.seed(42)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# 3D Viz
# -----------------------------------------------------------------------------
vtk_view = dash_vtk.View(
    id="vtk-view",
    children=[],
)


# Control UI
# -----------------------------------------------------------------------------
controls = [
    dbc.Card([
        dbc.CardHeader("Grid Size"),
        dbc.CardBody([
            dbc.Row([
                dbc.Label("I count:", width=6),
                dbc.Col(dbc.Input(id="i_size", type="number", min=1, value=1, persistence=True, persistence_type="session"), width=6) 
            ]),
            dbc.Row([
                dbc.Label("J count:", width=6), 
                dbc.Col(dbc.Input(id="j_size", type="number", min=1, value=2, persistence=True, persistence_type="session"), width=6) 
            ]),
            dbc.Row([
                dbc.Label("K count:", width=6), 
                dbc.Col(dbc.Input(id="k_size", type="number", min=1, value=3, persistence=True, persistence_type="session"), width=6) 
            ]),
            dbc.Row([
                dbc.Label("Cell count:", width=6), 
                dbc.Label("", id="cell_count_label", width=6), 
            ]),
            
            dbc.Button("Generate", id="generate_button")
        ])
    ]),
]

# App UI
# -----------------------------------------------------------------------------
app.layout = dbc.Container(
    fluid=True,
    style={"marginTop": "15px", "height": "calc(100vh - 30px)"},
    children=[
        dbc.Row(
            [
                dbc.Col(width=2, children=controls),
                dbc.Col(width=10, children=[html.Div(vtk_view, style={"height": "100%", "width": "100%"})]),
            ],
            style={"height": "100%"},
        ),
    ],
)

# Handle controls
# -----------------------------------------------------------------------------
@app.callback(
    Output("cell_count_label", "children"),
    Input("i_size", "value"),
    Input("j_size", "value"),
    Input("k_size", "value"),
)
def _update_cell_count_label(i_size, j_size, k_size):
    return i_size*j_size*k_size


@app.callback(
    Output("vtk-view", "children"),
    Output("vtk-view", "triggerRender"),
    Output("vtk-view", "triggerResetCamera"),
    State("i_size", "value"),
    State("j_size", "value"),
    State("k_size", "value"),
    Input("generate_button", "n_clicks"),
)
def _generate_grid(i_size, j_size, k_size, _n_clicks):

    print(f"Generating grid: {i_size}x{j_size}x{k_size}")

    ni, nj, nk = i_size, j_size, k_size
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

    print("construction")
    grid = pv.ExplicitStructuredGrid(dims, corners)
    print("compute conn")
    grid = grid.compute_connectivity()
    print("compute conn flags")
    grid.ComputeFacesConnectivityFlagsArray()

    print("extract surf")
    # !!! extract_surface() does not plat nice with ExplicitStructuredGrid
    #polydata = grid.extract_surface()

    extractSkinFilter = vtkExplicitStructuredGridSurfaceFilter()
    extractSkinFilter.SetInputData(grid)

    extractSkinFilter.Update()
    polydata = extractSkinFilter.GetOutput()

    print("to_mesh_state")
    mesh_state = to_mesh_state(polydata)

    print("making payload")
    children = [
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
    ]

    print("done")

    return children, random.random(), random.random()



# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)
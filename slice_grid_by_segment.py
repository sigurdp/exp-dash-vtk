import pyvista as pv
import numpy as np



def create_explicit_structured_grid(ni: int, nj: int, nk: int, si: float, sj: float, sk: float) -> pv.ExplicitStructuredGrid:

    si = float(si)
    sj = float(sj)
    sk = float(sk)

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

    return grid

grid = create_explicit_structured_grid(5, 4, 3, 20.0, 10.0, 5.0)


z = 14.0
line_verts = np.array(
    [
        (-5.0, -1.0, z),
        (5.0, 5.0, z),
        (6.0, 5.0, z),
        (7.0, 4.0, z),
        (8.0, 9.0, z),
        (15.0, 12.0, z),
        (25.0, 23.0, z),
        (70.0, 31.0, z),
        (65.0, 15.0, z),
        (66.0, 3.0, z),
        
    ]
)

slices = []
for vert,vert2 in zip(line_verts[:-1],line_verts[1:]):
    normal = np.cross(vert,vert2)
    minx = min(vert[0],vert2[0])
    maxx = max(vert[0],vert2[0])
    miny = min(vert[1],vert2[1])
    maxy = max(vert[1],vert2[1])
    s = grid.slice(normal=[normal[0],normal[1],0], origin=vert)
    s = s.clip_box([minx,maxx,miny,maxy,-9999,9999], invert=False)
    slices.append(s)

intersect = slices[0].merge(slices[1:])

vertex_count = len(line_verts)
line_conn = np.arange(-1, vertex_count)
line_conn[0] = vertex_count
my_polyline = pv.PolyData(line_verts, lines=line_conn)

plotter = pv.Plotter()
plotter.add_mesh(grid,style="wireframe",color="blue")
plotter.add_mesh(my_polyline,style="points", point_size=10, color="red")
plotter.add_mesh(my_polyline.copy(),style="surface", color="yellow")
plotter.add_mesh(intersect,show_edges=False)
plotter.show()


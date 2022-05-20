"""
**********
Matplotlib
**********

Draw hypergraphs with matplotlib.
"""

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

import xgi

__all__ = [
    "draw",
]


def draw(
        H,
        pos=None,
        cmap=None,
        ax=None,
        edge_lc="black",
        edge_lw=1.5,
        node_fc="white",
        node_ec="black",
        node_lw=1,
        node_size=0.03,
        nodecolors=None,
        nodelabels=None,
        nodelabel_xoffset=0.05
):
    """
    Draw hypergraph or simplicial complex.

    Parameters
    ----
    H : xgi Hypergraph or SimplicialComplex.

    pos : dict (default=None)
        If passed, this dictionary of positions d:(x,y) is used for placing the 0-simplices.
        If None (default), use the `barycenter_spring_layout` to compute the positions.

    cmap : `matplotlib.colors.ListedColormap`, default: `matplotlib.cm.Paired`
        The qualitative colormap used to distinguish edges of different order.
        If a continuous `matplotlib.colors.LinearSegmentedColormap` is given, it is discretized first.

    ax : matplotlib.pyplot.axes (default=None)

    edge_lc : color (default='black')
    Color of the edges (dyadic links and borders of the hyperedges).

    edge_lw :  float (default=1.5)
    Line width of edges of order 1 (dyadic links).

    node_fc : color (default='white')
    Color of the nodes.

    node_ec : color (default='black')
    Color of node borders.

    node_lw : float (default=1.0)
    Line width of the node borders.

    node_size : float (default=0.03)
    Size of the nodes.

    nodecolors : dict (node to color)
    Node colors

    nodelabels : dict (node to label), if True node indices are used
    Node labels

    Examples
    --------
    >>> import xgi
    >>> H=xgi.Hypergraph()
    >>> H.add_edges_from([[1,2,3],[3,4],[4,5,6,7],[7,8,9,10,11]])
    >>> xgi.draw(H, pos=xgi.barycenter_spring_layout(H))

    """
    if pos is None:
        pos = xgi.barycenter_spring_layout(H)

    def CCW_sort(p):
        """
        Sort the input 2D points counterclockwise.
        """
        p = np.array(p)
        mean = np.mean(p, axis=0)
        d = p - mean
        s = np.arctan2(d[:, 0], d[:, 1])
        return p[np.argsort(s), :]

    # Defining colors, one for each dimension
    d_max = H.max_edge_order()
    if cmap is None:
        cmap = cm.Paired
        colors = [cmap(i) for i in range(0, d_max + 1)]
    else:
        if type(cmap) == ListedColormap:
            # The colormap is already discrete
            colors = [cmap(i) for i in range(0, d_max + 1)]
        elif type(cmap) == LinearSegmentedColormap:
            # I need to discretize the given colormap
            color_range = np.linspace(0.1, 0.9, d_max)
            colors = [cmap(i) for i in color_range]

    if ax is None:
        ax = plt.gca()
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    ax.axis("off")

    if type(H) == xgi.classes.hypergraph.Hypergraph:
        # Looping over the hyperedges of different order (reversed) -- nodes will be plotted separately
        for d in reversed(range(1, d_max + 1)):
            if d == 1:
                # Drawing the edges
                for he in H.edges(order=d).members():
                    he = list(he)
                    x_coords = [pos[he[0]][0], pos[he[1]][0]]
                    y_coords = [pos[he[0]][1], pos[he[1]][1]]
                    line = plt.Line2D(x_coords, y_coords, color=edge_lc, lw=edge_lw)
                    ax.add_line(line)

            else:
                # Hyperedges of order d (d=1: links, etc.)
                for he in H.edges(order=d).members():
                    # Filling the polygon
                    coordinates = [[pos[n][0], pos[n][1]] for n in he]
                    # Sorting the points counterclockwise (needed to have the correct filling)
                    sorted_coordinates = CCW_sort(coordinates)
                    obj = plt.Polygon(
                        sorted_coordinates,
                        edgecolor=edge_lc,
                        facecolor=colors[d - 1],
                        alpha=0.4,
                        lw=0.5,
                    )
                    ax.add_patch(obj)
    elif type(H) == xgi.classes.simplicialcomplex.SimplicialComplex:
        # I will only plot the maximal simplices, so I convert the SC to H
        H_ = xgi.from_simplicial_complex_to_hypergraph(H)

        # Looping over the hyperedges of different order (reversed) -- nodes will be plotted separately
        for d in reversed(range(1, d_max + 1)):
            if d == 1:
                # Drawing the edges
                for he in H_.edges(order=d).members():
                    he = list(he)
                    x_coords = [pos[he[0]][0], pos[he[1]][0]]
                    y_coords = [pos[he[0]][1], pos[he[1]][1]]
                    line = plt.Line2D(x_coords, y_coords, color=edge_lc, lw=edge_lw)
                    ax.add_line(line)
            else:
                # Hyperedges of order d (d=1: links, etc.)
                for he in H_.edges(order=d).members():
                    # Filling the polygon
                    coordinates = [[pos[n][0], pos[n][1]] for n in he]
                    # Sorting the points counterclockwise (needed to have the correct filling)
                    sorted_coordinates = CCW_sort(coordinates)
                    obj = plt.Polygon(
                        sorted_coordinates,
                        edgecolor=edge_lc,
                        facecolor=colors[d - 1],
                        alpha=0.4,
                        lw=0.5,
                    )
                    ax.add_patch(obj)
                    # Drawing the all the edges within
                    for i, j in combinations(sorted_coordinates, 2):
                        x_coords = [i[0], j[0]]
                        y_coords = [i[1], j[1]]
                        line = plt.Line2D(x_coords, y_coords, color=edge_lc, lw=edge_lw)
                        ax.add_line(line)
    else:
        raise XGIError("The input must be a xgi.SimplicialComplex or xgi.Hypergraph")

    # Drawing the nodes
    for i in list(H.nodes):
        (x, y) = pos[i]
        nodecolor = node_fc if nodecolors is None else nodecolors[i]
        circ = plt.Circle(
            [x, y],
            radius=node_size,
            lw=node_lw,
            zorder=d_max + 1,
            ec=node_ec,
            fc=nodecolor,
        )
        ax.add_patch(circ)

    # Drawing node labels
    if nodelabels is not None:

        for i in list(H.nodes):
            (x, y) = pos[i]
            s = str(i) if nodelabels==True else str(nodelabels[i])
            ax.text(
                    x + nodelabel_xoffset,
                    y,
                    s)


"""Read from and write to JSON."""
import json

import xgi
from xgi.exception import XGIError

__all__ = ["write_hypergraph_json", "read_hypergraph_json"]


def write_hypergraph_json(H, path):
    """
    A function to write a file in a standardized JSON format.

    Parameters
    ----------
    H: Hypergraph object
        The specified hypergraph object
    path: string
        The path of the file to read from

    """
    # initialize empty data
    data = {}

    # get overall hypergraph attributes, name always gets written (default is an empty string)
    data["hypergraph-data"] = dict()
    data["hypergraph-data"].update(H._hypergraph)

    # get node data
    data["node-data"] = {str(id): H.nodes[id] for id in H.nodes}
    data["edge-data"] = {str(id): H.edges[id] for id in H.edges}

    # hyperedge dict
    data["edge-dict"] = {
        str(id): [str(n) for n in H.edges.members(id)] for id in H.edges
    }

    datastring = json.dumps(data)

    with open(path, "w") as output_file:
        output_file.write(datastring)


def read_hypergraph_json(path, nodetype=None, edgetype=None):
    """
    A function to read a file in a standardized JSON format.

    Parameters
    ----------
    hypergraph_dict: dict
        A dictionary in the hypergraph JSON format
    nodetype: type, optional
        type that the node IDs will be cast to
    edgetype: type, optional
        type that the edge IDs will be cast to

    Returns
    -------
    A Hypergraph object
        The loaded hypergraph

    Raises
    ------
    XGIError
        If the JSON is not in a format that can be loaded.

    """
    with open(path) as file:
        data = json.loads(file.read())

    H = xgi.empty_hypergraph()
    try:
        H._hypergraph.update(data["hypergraph-data"])
    except KeyError:
        raise XGIError("Failed to get hypergraph data attributes.")

    try:
        for id, dd in data["node-data"].items():
            if nodetype is not None:
                try:
                    id = nodetype(id)
                except Exception as e:
                    raise TypeError(
                        f"Failed to convert edge IDs to type {nodetype}."
                    ) from e
            H.add_node(id, **dd)
    except KeyError:
        raise XGIError("Failed to import node attributes.")

    try:
        for id, edge in data["edge-dict"].items():
            if edgetype is not None:
                try:
                    id = edgetype(id)
                except Exception as e:
                    raise TypeError(
                        f"Failed to convert the edge with ID {id} to type {edgetype}."
                    ) from e

            if nodetype is not None:
                try:
                    edge = [nodetype(n) for n in edge]
                except Exception as e:
                    raise TypeError(
                        f"Failed to convert nodes to type {nodetype}."
                    ) from e
            H.add_edge(edge, id)
    except:
        raise XGIError("Failed to import edge dictionary.")

    try:
        xgi.set_edge_attributes(
            H,
            data["edge-data"]
            if edgetype is None
            else {edgetype(e): dd for e, dd in data["edge-data"].items()},
        )
    except KeyError:
        raise XGIError("Failed to import edge attributes.")

    return H

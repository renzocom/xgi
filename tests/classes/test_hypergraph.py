import pytest

import xgi
from xgi.exception import IDNotFound, XGIError


def test_constructor(edgelist5, dict5, incidence5, dataframe5):
    H_list = xgi.Hypergraph(edgelist5)
    H_dict = xgi.Hypergraph(dict5)
    H_mat = xgi.Hypergraph(incidence5)
    H_df = xgi.Hypergraph(dataframe5)

    assert (
        list(H_list.nodes)
        == list(H_dict.nodes)
        == list(H_mat.nodes)
        == list(H_df.nodes)
    )
    assert (
        list(H_list.edges)
        == list(H_dict.edges)
        == list(H_mat.edges)
        == list(H_df.edges)
    )
    assert (
        list(H_list.edges.members(0))
        == list(H_dict.edges.members(0))
        == list(H_mat.edges.members(0))
        == list(H_df.edges.members(0))
    )


def test_hypergraph_attrs():
    H = xgi.Hypergraph()
    assert H._hypergraph == dict()
    with pytest.raises(XGIError):
        name = H["name"]
    H = xgi.Hypergraph(name="test")
    assert H["name"] == "test"


def test_contains(edgelist1):
    el1 = edgelist1
    H = xgi.Hypergraph(el1)
    unique_nodes = {node for edge in el1 for node in edge}
    for node in unique_nodes:
        assert node in H

    assert 0 not in H


def test_string():
    H1 = xgi.Hypergraph()
    assert str(H1) == "Unnamed Hypergraph with 0 nodes and 0 hyperedges"
    H2 = xgi.Hypergraph(name="test")
    assert str(H2) == "Hypergraph named test with 0 nodes and 0 hyperedges"


def test_len(edgelist1, edgelist2):
    el1 = edgelist1
    el2 = edgelist2
    H1 = xgi.Hypergraph(el1)
    H2 = xgi.Hypergraph(el2)
    assert len(H1) == 8
    assert len(H2) == 6


def test_neighbors(edgelist1, edgelist2):
    el1 = edgelist1
    el2 = edgelist2
    H1 = xgi.Hypergraph(el1)
    H2 = xgi.Hypergraph(el2)
    assert H1.neighbors(1) == {2, 3}
    assert H1.neighbors(4) == set()
    assert H1.neighbors(6) == {5, 7, 8}
    assert H2.neighbors(4) == {3, 5, 6}
    assert H2.neighbors(1) == {2}


def test_dual(edgelist1, edgelist2, edgelist4):
    el1 = edgelist1
    el2 = edgelist2
    el4 = edgelist4
    H1 = xgi.Hypergraph(el1)
    H2 = xgi.Hypergraph(el2)
    H3 = xgi.Hypergraph(el4)

    D1 = H1.dual()
    D2 = H2.dual()
    D3 = H3.dual()
    assert (D1.num_nodes, D1.num_edges) == (4, 8)
    assert (D2.num_nodes, D2.num_edges) == (3, 6)
    assert (D3.num_nodes, D3.num_edges) == (3, 5)


def test_max_edge_order(edgelist1, edgelist4, edgelist5):
    H0 = xgi.empty_hypergraph()
    H1 = xgi.empty_hypergraph()
    H1.add_nodes_from(range(5))
    H2 = xgi.Hypergraph(edgelist1)
    H3 = xgi.Hypergraph(edgelist4)
    H4 = xgi.Hypergraph(edgelist5)

    assert H0.max_edge_order() == None
    assert H1.max_edge_order() == 0
    assert H2.max_edge_order() == 2
    assert H3.max_edge_order() == 3
    assert H4.max_edge_order() == 3


def test_add_nodes_from(attr1, attr2, attr3):
    H = xgi.Hypergraph()
    H.add_nodes_from(range(3), **attr1)
    assert H.nodes[0]["color"] == attr1["color"]
    assert H.nodes[1]["color"] == attr1["color"]
    assert H.nodes[2]["color"] == attr1["color"]

    H = xgi.Hypergraph()
    H.add_nodes_from(zip(range(3), [attr1, attr2, attr3]))
    assert H.nodes[0]["color"] == attr1["color"]
    assert H.nodes[1]["color"] == attr2["color"]
    assert H.nodes[2]["color"] == attr3["color"]


def test_is_possible_order(edgelist1):
    H1 = xgi.Hypergraph(edgelist1)

    assert H1.is_possible_order(-1) == False
    assert H1.is_possible_order(0) == False
    assert H1.is_possible_order(1) == True
    assert H1.is_possible_order(2) == True
    assert H1.is_possible_order(3) == False


def test_singleton_edges(edgelist1, edgelist2):
    H1 = xgi.Hypergraph(edgelist1)
    H2 = xgi.Hypergraph(edgelist2)

    assert len(H1.singleton_edges()) == 1
    assert 1 in H1.singleton_edges()
    assert len(H2.singleton_edges()) == 0


def test_remove_singleton_edges(edgelist1, edgelist2):
    H1 = xgi.Hypergraph(edgelist1)
    H2 = xgi.Hypergraph(edgelist2)

    H1.remove_singleton_edges()
    H2.remove_singleton_edges()

    assert H1.singleton_edges() == {}
    assert H2.singleton_edges() == {}


def test_is_uniform(edgelist1, edgelist6, edgelist7):
    H0 = xgi.Hypergraph(edgelist1)
    H1 = xgi.Hypergraph(edgelist6)
    H2 = xgi.Hypergraph(edgelist7)
    H3 = xgi.empty_hypergraph()

    assert H0.is_uniform() == False
    assert H1.is_uniform() == 2
    assert H2.is_uniform() == 2
    assert H3.is_uniform() == False


def test_isolates(edgelist1):
    H = xgi.Hypergraph(edgelist1)
    assert H.isolates(ignore_singletons=False) == set()
    assert H.isolates() == {4}
    H.remove_isolates()
    assert 4 not in H


def test_add_node_attr(edgelist1):
    H = xgi.Hypergraph(edgelist1)
    assert "new_node" not in H
    H.add_node("new_node", color="red")
    assert "new_node" in H
    assert "color" in H.nodes["new_node"]
    assert H.nodes["new_node"]["color"] == "red"


def test_hypergraph_attr(edgelist1):
    H = xgi.Hypergraph(edgelist1)
    with pytest.raises(XGIError):
        H["color"]
    H["color"] = "red"
    assert H["color"] == "red"


def test_members(edgelist1):
    H = xgi.Hypergraph(edgelist1)
    assert H.nodes.memberships(1) == [0]
    assert H.nodes.memberships(2) == [0]
    assert H.nodes.memberships(3) == [0]
    assert H.nodes.memberships(4) == [1]
    assert H.nodes.memberships(6) == [2, 3]
    with pytest.raises(IDNotFound):
        H.nodes.memberships(0)
    with pytest.raises(XGIError):
        H.nodes.memberships(slice(1, 4))


def test_has_edge(edgelist1):
    H = xgi.Hypergraph(edgelist1)
    assert H.has_edge([1, 2, 3])
    assert H.has_edge({1, 2, 3})
    assert H.has_edge({4})
    assert not H.has_edge([4, 5])
    assert not H.has_edge([3])
    assert not H.has_edge([1, 2])


def test_egonet(edgelist3):
    H = xgi.Hypergraph(edgelist3)
    assert H.neighbors(3) == {1, 2, 4}
    assert H.egonet(3) == [[1, 2], [4]]
    assert H.egonet(3, include_self=True) == [[1, 2, 3], [3, 4]]
    with pytest.raises(IDNotFound):
        H.egonet(7)


def test_add_edge():
    for edge in [[1, 2, 3], {1, 2, 3}, iter([1, 2, 3])]:
        H = xgi.Hypergraph()
        H.add_edge(edge)
        assert (1 in H) and (2 in H) and (3 in H)
        assert 0 in H.edges
        assert [1, 2, 3] in H.edges.members()
        assert [1, 2, 3] == H.edges.members(0)
        assert H.edges.members(dtype=dict) == {0: [1, 2, 3]}

    H = xgi.Hypergraph()
    for edge in [[], set(), iter([])]:
        with pytest.raises(XGIError):
            H.add_edge(edge)


def test_add_edge_with_id():
    H = xgi.Hypergraph()
    H.add_edge([1, 2, 3], id="myedge")
    assert (1 in H) and (2 in H) and (3 in H)
    assert "myedge" in H.edges
    assert [1, 2, 3] in H.edges.members()
    assert [1, 2, 3] == H.edges.members("myedge")
    assert H.edges.members(dtype=dict) == {"myedge": [1, 2, 3]}


def test_add_edge_with_attr():
    H = xgi.Hypergraph()
    H.add_edge([1, 2, 3], color="red", place="peru")
    assert (1 in H) and (2 in H) and (3 in H)
    assert 0 in H.edges
    assert [1, 2, 3] in H.edges.members()
    assert [1, 2, 3] == H.edges.members(0)
    assert H.edges.members(dtype=dict) == {0: [1, 2, 3]}
    assert H.edges[0] == {"color": "red", "place": "peru"}


def test_add_node_to_edge():
    H = xgi.Hypergraph()
    H.add_edge(["apple", "banana"], "fruits")
    H.add_node_to_edge("fruits", "pear")
    H.add_node_to_edge("veggies", "lettuce")
    assert H.edges.members(dtype=dict) == {
        "fruits": ["apple", "banana", "pear"],
        "veggies": ["lettuce"],
    }
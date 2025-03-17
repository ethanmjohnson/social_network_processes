def find_petri_net_diameter(file_path):
    import networkx as nx
    import pm4py

    """
    This function finds the diameter of a Petri net using the longest shortest paths.

    Inputs:
    file_path: the file path to the Petri net

    Outputs:
    diameter: the diameter of the Petri net
    """

    # read in the petri net path
    net, im, fm = pm4py.read_pnml(file_path)

    # initialise a directed graph
    G = nx.DiGraph()

    # add the places from the net as nodes to G
    for place in net.places:
        G.add_node(place.name, type="place")

    # add transitions from the net as nodes to G
    for transition in net.transitions:
        label = transition.label if transition.label else transition.name
        G.add_node(transition.name, type="transition", label=label)

    # add the arcs from the net as edges in G
    for arc in net.arcs:
        G.add_edge(arc.source.name, arc.target.name)

    # find the shortest path length between all nodes in G
    lengths = dict(nx.all_pairs_shortest_path_length(G))

    # find the longest shortest path
    diameter = 0
    for source in lengths:
        for target in lengths[source]:
            diameter = max(diameter, lengths[source][target])

    return diameter
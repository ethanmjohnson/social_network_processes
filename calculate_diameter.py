def find_petri_net_diameter(file_path):

    """
    This function finds the diameter of a Petri net using the longest shortest paths.

    Inputs:
    file_path: the file path to the Petri net

    Outputs:
    diameter: the diameter of the Petri net
    """

    import networkx as nx
    import pm4py

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

if __name__ == "__main__":
    from load_config import load_config
    import os
    import argparse

    config = load_config()

    parser = argparse.ArgumentParser(description="Run script on a Petri net.")
    parser.add_argument("--pn", type=str, required=True, choices=["brazil_1.pnml", "brazil_2.pnml", "honduras_coordinated.pnml", "honduras_uncoordinated.pnml", "uae_coordinated.pnml", "uae_uncoordinated.pnml"], help="Petri net filename (relative to project root)")
    args = parser.parse_args()

    # Construct dataset path
    file_path = os.path.join(config["project_root"], "data", args.pn)

    diameter = find_petri_net_diameter(file_path)
    print("Diameter of", args.pn, ": ", diameter)
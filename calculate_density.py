def find_petri_net_density(file_path):
    """
    This function finds the density of a given petri net using the density for a directed graph.

    Inputs:
    file_path: the path to a Petri net

    Outputs:
    density: the density as a float
    """

    import pm4py

    net, im, fm = pm4py.read_pnml(file_path)

    # calculate the total number of nodes
    no_nodes = len(net.transitions) + len(net.places)

    # calculate the number of edges
    no_edges = len(net.arcs)

    # calculate the density using the density of a directed graph
    density = no_edges/(no_nodes*(no_nodes - 1))

    return density, no_nodes

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

    density, no_nodes = find_petri_net_density(file_path)

    print("Number of nodes of", args.pn, ":", no_nodes)
    print("Density of", args.pn, ": ", density)
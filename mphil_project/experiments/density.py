def find_density(net):
    """
    This function finds the density of a given petri net using the density for a directed graph.

    Inputs:
    net: a Petri net

    Outputs:
    density: the density as a float
    """

    # calculate the total number of nodes
    no_nodes = len(net.transitions) + len(net.places)
    print('nodes: ', no_nodes)

    # calculate the number of edges
    no_edges = len(net.arcs)

    # calculate the density using the density of a directed graph
    density = no_edges/(no_nodes*(no_nodes - 1))

    return density

if __name__ == "__main__":
    import pm4py

    # add path to Petri net model for Brazil/UAE/Honduras Petri net
    path = "honduras_coordinated.pnml"

    net, im, fm = pm4py.read_pnml(path)

    # find the density
    density = find_density(net)

    print(density)


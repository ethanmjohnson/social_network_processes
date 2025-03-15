def find_density(net):
    """
    This function finds the density of a given petri net.
    """

    no_nodes = len(net.transitions) + len(net.places)
    print('nodes: ', no_nodes)
    no_edges = len(net.arcs)

    density = no_edges/(no_nodes*(no_nodes - 1))

    return density

if __name__ == "__main__":
    import pm4py
    path = "/Users/ethanjohnson/Desktop/models/honduras_uncoordinated.pnml"

    net, im, fm = pm4py.read_pnml(path)

    density = find_density(net)

    print(density)


import networkx as nx
import pm4py

def find_depth(petri_net):
    G = nx.DiGraph()
    
    # add nodes (places and transitions)
    for place in petri_net.places:
        G.add_node(place.name)
    for transition in petri_net.transitions:
        G.add_node(transition.name)
    
    # add edges (arcs)
    for arc in petri_net.arcs:
        G.add_edge(arc.source.name, arc.target.name)
    
    # find Strongly Connected Components (SCCs)
    sccs = list(nx.strongly_connected_components(G))
    
    # build SCC Collapsed Graph (DAG)
    scc_graph = nx.DiGraph()
    scc_map = {}  # Map each node to its SCC
    
    for i, scc in enumerate(sccs):
        scc_graph.add_node(i)  # each SCC becomes a node
        for node in scc:
            scc_map[node] = i  # track which SCC each node belongs to
    
    # add edges between SCCs
    for u, v in G.edges():
        scc_u = scc_map[u]
        scc_v = scc_map[v]
        if scc_u != scc_v:  # Only add edges between different SCCs
            scc_graph.add_edge(scc_u, scc_v)
    
    # compute longest path in the SCC DAG
    depth = {node: 0 for node in scc_graph.nodes}
    
    for node in nx.topological_sort(scc_graph):  # process SCCs in order
        for successor in scc_graph.successors(node):
            depth[successor] = max(depth[successor], depth[node] + 1)
    
    return max(depth.values())  # maximum depth in the collapsed SCC DAG

if __name__ == "__main__":
    import pm4py
    path = "/Users/ethanjohnson/Desktop/models/brazil_uncoordinated.pnml"

    net, im, fm = pm4py.read_pnml(path)

    density = find_depth(net)

    print(density)
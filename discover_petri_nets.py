def discover_petri_nets(file_path):
    """
    Discovers a Petri net using the inductive miner and saves to a .pnml file in the same folder as the event log is located.

    Inputs:
    file_path: path to an event log 
    """
    import pm4py
    print("loading event log...")
    log = pm4py.read_xes(file_path)
    print("discovering Petri net...")
    net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2, multi_processing=True)

    # add path to output for each Petri net
    print("saving Petri net...")
    split_path = file_path.split(sep='.xes')
    output_path = split_path[0] + ".pnml"
    pm4py.write_pnml(net, im, fm, output_path)
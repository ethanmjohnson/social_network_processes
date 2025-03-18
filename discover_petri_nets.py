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

    return net, im, fm


if __name__ == "__main__":
    from load_config import load_config
    import os
    import argparse
    import pm4py

    config = load_config()

    parser = argparse.ArgumentParser(description="Discover Petri net from event log.")
    parser.add_argument("--log", type=str, required=True, help="Event log filename (relative to project root)")
    args = parser.parse_args()

    # Construct dataset path
    dataset_path = os.path.join(config["project_root"], "data", args.log)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    split_path = args.log.split(sep=".xes")

    output_path = os.path.join(config['project_root'], "data", split_path[0] + ".pnml")

    net, im, fm = discover_petri_nets(dataset_path)

    pm4py.write_pnml(net, im, fm, output_path)

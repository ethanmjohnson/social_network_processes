import pm4py
from free_choice_SPN import generate_P
from pm4py.objects.log.importer.xes import importer as xes_importer
import numpy as np


def get_preceding_places(petri_net, transition):
    """
    Get the preceding places of a given transition in a Petri net.

    Parameters:
    - petri_net: The Petri net object.
    - transition: The transition object.

    Returns:
    - List of preceding places.
    """
    preceding_places = [arc.source for arc in petri_net.arcs if arc.target == transition]
    return preceding_places

def get_output_transitions(petri_net, place):
    """
    Get the output transitions of a given place in a Petri net.

    Parameters:
    - petri_net: The Petri net object.
    - place: The place object.

    Returns:
    - List of output transitions.
    """
    output_transitions = [arc.target for arc in petri_net.arcs if arc.source == place]
    return output_transitions


def get_transition_by_name(transitions, name):
    """
    Get a transition object by its name.
    
    Parameters:
    - transitions: List of Transition objects.
    - name: The name of the transition to find.

    Returns:
    - The transition object if found, else None.
    """
    for transition in transitions:
        if transition.label == name:
            return transition
    return None

def calculate_ks_entropy(pn_file_path, log_file_path):
    net, im, fm = pm4py.read_pnml(pn_file_path)
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(log_file_path, variant=variant, parameters=parameters)

    freq_of_places = {}


    for trace in log:
        for activity in trace:
            name = activity["concept:name"]
            transition = get_transition_by_name(net.transitions, name)
            places = get_preceding_places(net,transition)
            if len(places) == 1:
                place = places[0]
                if place not in freq_of_places:
                    freq_of_places[place] = 1
                else:
                    freq_of_places[place] += 1

    total = sum(freq_of_places.values())

    mu = {k: v / total for k, v in freq_of_places.items()}

    P = generate_P(log, net, im, fm)

    ks = 0
    for place in mu:
        transitions = get_output_transitions(net, place)
        total_sum = 0
        for transition in transitions:
            if P[transition.name] > 0:
                total_sum += -(P[transition.name])*np.log2(P[transition.name])
        total_sum*=mu[place]
        ks+=total_sum
    return ks


if __name__ == "__main__":
    from load_config import load_config
    import os
    import argparse

    config = load_config()

    parser = argparse.ArgumentParser(description="Run script on a Petri net.")
    parser.add_argument("--pn", type=str, required=True, choices=["brazil_1.pnml", "brazil_2.pnml", "honduras_coordinated.pnml", "honduras_uncoordinated.pnml", "uae_coordinated.pnml", "uae_uncoordinated.pnml"], help="Petri net filename (relative to project root)")
    args = parser.parse_args()

    split_pn_path = args.pn.split(sep=".pnml")
    log_name = split_pn_path[0] + ".xes"
    # Construct dataset path
    pn_file_path = os.path.join(config["project_root"], "data", args.pn)
    log_file_path = os.path.join(config["project_root"], "data", log_name)

    ks = calculate_ks_entropy(pn_file_path, log_file_path)
    print("KS of", args.pn, ": ", ks)
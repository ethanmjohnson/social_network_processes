import numpy as np
from pm4py.objects.log.obj import EventLog
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from tqdm import tqdm

def generate_P(log, net, im, fm):

    """
    Generates the dictionary P containing probabilities of transitioning to some transition

    Inputs:
    log: the event log
    net: the Petri net discovered from the event log
    im: the initial marking
    fm: the final marking

    Outputs:
    P: the dictionary containing transition probabilities
    """

    keys = [t.name for t in net.transitions]

    # initialise the frequency dict
    freq = {key: 0 for key in keys}

    for trace in tqdm(log):
        # find fitness of trace to petri net
        trace_log = EventLog()
        trace_log.append(trace)
        fitness = token_replay.apply(trace_log, net, im, fm)

        if fitness[0]['trace_fitness'] == 1.0:
            # if trace is in net, get the activated transitions required to achieve this trace in net
            activated_transitions = fitness[0]['activated_transitions']

            # update frequencies
            for transition in activated_transitions:
                label = transition.name
                freq[label] += 1
    

    places = [p for p in net.places]

    P = freq

    for place in places:
        outgoing_transitions = [arc.target for arc in net.arcs if arc.source == place]
        
        # find number of output transitions per place
        total = 0
        for t in outgoing_transitions:
            total = total + freq[t.name]
        
        if total == 0:
            for t in outgoing_transitions:
                P[t.name] = 0.0
        else:
            # divide freq for place by total for place
            for t in outgoing_transitions:
                P[t.name] = freq[t.name]/total
        
    return P


def find_previous_transitions(net, current_transition, visited_transitions=None, visited_places=None):

    """
    Finds the previous possible non-silent transitions from some starting transition

    Inputs:
    net: a Petri net
    current_transition: the transition to find all previous transitions from

    Outputs:
    transition_list: a list of previous possible transitions
    """
    if visited_transitions is None:
        visited_transitions = set()
    if visited_places is None:
        visited_places = set()

    visited_transitions.add(current_transition)
    
    transition_list = []
    
    while len(transition_list) == 0:
        # find associated places for the current transition
        places = [arc.source for arc in net.arcs if arc.target == current_transition]

        # break while loop if no more previous transitions
        if len(places) == 0 or places[0].name == 'source':
            break

        # handle synchronised transitions (multiple places)
        if len(places) > 1:
            synchronised_transitions = []
            for place in places:
                input_transitions = [arc.source for arc in net.arcs if arc.target == place]

                for t in input_transitions:
                    visited_transitions.add(t)
                visited_places.add(place)

                for t in input_transitions:
                    if t.label is not None:
                        synchronised_transitions.append(t)
                    else:
                        synchronised_transitions.extend(find_previous_transitions(net, t, visited_transitions, visited_places))

            flat_synchronised_transitions = [item for sublist in synchronised_transitions for item in (sublist if isinstance(sublist, list) else [sublist])]

            transition_list.append(flat_synchronised_transitions)
            break

        # explore previous transitions
        found_transition = False
        for place in places:
            if place in visited_places:
                continue  # skip if the place has already been visited
            
            visited_places.add(place)  # mark the place as visited
            
            input_transitions = [arc.source for arc in net.arcs if arc.target == place]
            
            for input_transition in input_transitions:
                if input_transition in visited_transitions:
                    continue  # skip if the transition has already been visited

                visited_transitions.add(input_transition)  # mark the transition as visited

                if input_transition.label is not None:
                    transition_list.append([input_transition])
                    found_transition = True

                if input_transition.label is None:
                    transition_list.extend(find_previous_transitions(net, input_transition, visited_transitions, visited_places))

        # if no transition was found, break the loop
        if not found_transition:
            break
    
    return transition_list

def generate_F(net, log):

    """
    Finds a dictionary of pdfs associated with each transitions in the net

    Inputs:
    net: the Petri net
    log: the event log the Petri net was discovered from

    Outputs:
    F: a dictionary containing pdfs for each key (transition in the Petri net)
    """

    transitions = [t for t in net.transitions if t.label is not None]

    previous_transitions_dict = {t: 0 for t in transitions}

    # generate a dictionary of previous possible transitions
    for t in transitions:
        previous_transitions_dict[t] = find_previous_transitions(net, t)

    
    # initialise time delay dict
    delay_time_dict = {k: 0 for k in previous_transitions_dict.keys()}

    for key in previous_transitions_dict.keys():
        delay_time = []
        for t_list in previous_transitions_dict[key]:
            if len(t_list) == 1: # if only one possible transition, search log and add time delay
                transition = t_list[0]
                
                for trace in log:
                    for i in range(1, len(trace)):
                        curr_event = trace[i]
                        prev_event = trace[i-1]

                        if curr_event['concept:name'] == key.label and prev_event['concept:name'] == transition.label:
                            delay_time.append((curr_event['time:timestamp'] - prev_event['time:timestamp']).total_seconds())

            else: # if multiple possible transitions (synchronised events), search log and add the minimum time delay

                t_list_names = [t.label for t in t_list]
                for trace in log:
                    trace_event_names = {event['concept:name'] for event in trace}
                    timestamp_b = None
                    timestamp_a = None

                    if any(t_list_name in trace_event_names for t_list_name in t_list_names) and key.label in trace_event_names:
                        for event in trace:
                            if event['concept:name'] == key.label:
                                timestamp_b = event['time:timestamp']
                        delay_time_single = np.inf
                        for event in trace:
                            if event['concept:name'] in t_list_names:
                                timestamp_a = event['time:timestamp']
                                delta = (timestamp_b - timestamp_a).total_seconds()

                                if delta < delay_time_single and delta >= 0:
                                    delay_time_single = delta
                        if delay_time_single != np.inf:
                            delay_time.append(delay_time_single)
        
        delay_time_dict[key] = delay_time

    name_keys = [t.name for t in net.transitions]

    label_time_differences = {key: [] for key in name_keys}

    for key in delay_time_dict.keys():
        label_time_differences[key.name] = delay_time_dict[key]

    
    F = {key: 0 for key in name_keys}

    for label in label_time_differences.keys():
        times = label_time_differences[label]
        F[label] = times
    
    return F
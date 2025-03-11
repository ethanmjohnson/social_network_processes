# logic for choosing which transition fires

import random
import numpy as np
import scipy.stats as stats
import random
import pm4py
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from tqdm import tqdm
import pandas as pd
from collections import defaultdict

def choose_transition(transitions, P, F):
    # logic to choose an enabled transition to fire
    # Inputs:
    # transitions - list of enabled transitions
    # P - dictionary of probabilities
    # F - dictionary of pdfs


    # outputs:
    # selected_transition - the chosen transition to fire
    # selected_time - the time delay for this transition to fire

    # find the transition names 

    transition_names = [t.name for t in transitions]

    # create a subset of P containing relevant probabilites

    probabilities = {k: v for k,v in P.items() if k in transition_names}

    keys = list(probabilities.keys())
    weights = list(probabilities.values())

    # select a transition using the probabilities

    selected_key = random.choices(keys, weights=weights, k=1)[0]

    # find full transition object
    for t in transitions:
        if selected_key == t.name:
            selected_transition = t

    # find associated time
    selected_time = F[selected_key]

    return (selected_transition, selected_time())



def best_fitting_distribution(time_differences):
    # given a list of time differences, finds the best fitting distribution to this list
    data_seconds = np.array(time_differences)

    # distributions to test
    numpy_distributions = {
        "exponential": stats.expon,
        "gamma": stats.gamma,
        "lognormal": stats.lognorm,
        "weibull": stats.weibull_min,
        "normal": stats.norm
    }

    best_fit = None
    best_params = None
    best_ks = np.inf


    for dist_name, dist_func in numpy_distributions.items():
        try:
            # fit the distribution to the data
            params = dist_func.fit(data_seconds)


            ks_stat, _ = stats.kstest(data_seconds, dist_func.cdf, args=params)

            # track the best fit (smallest KS statistic)
            if ks_stat < best_ks:
                best_ks = ks_stat
                best_fit = dist_name
                best_params = params
        except Exception as e:
            print(f"Skipping {dist_name}: {e}")

    # return the best fitting distribution and its parameters
    if best_fit == "exponential":
        lambda_value = best_params[0]
        return lambda lambda_value=lambda_value: stats.expon.rvs(scale=lambda_value)
    elif best_fit == "normal":
        loc, scale = best_params
        return lambda loc=loc, scale=scale: stats.norm.rvs(loc=loc, scale=scale)
    elif best_fit == "gamma":
        shape, loc, scale = best_params
        return lambda shape=shape, loc=loc, scale=scale: stats.gamma.rvs(shape, loc=loc, scale=scale)
    elif best_fit == "lognormal":
        shape, loc, scale = best_params
        return lambda shape=shape, loc=loc, scale=scale: stats.lognorm.rvs(shape, loc=loc, scale=scale)
    elif best_fit == "weibull":
        c, loc, scale = best_params
        return lambda c=c, loc=loc, scale=scale: stats.weibull_min.rvs(c, loc=loc, scale=scale)
    else:
        average_time = np.mean(time_differences)
        return lambda average_time=average_time: stats.uniform.rvs(loc=0, scale=2 * average_time)
    
def generate_P(log, net, im, fm):
    # this function generates the matrix P used to choose a transition to fire

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
        
        # divide freq for place by total for place
        for t in outgoing_transitions:
            P[t.name] = freq[t.name]/total

    return P


def find_previous_transitions(net, current_transition, visited_transitions=None, visited_places=None):
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
    # fit distribution to each time difference list
    for label in label_time_differences.keys():
        times = label_time_differences[label]

        # if more than 30, find a distribution
        if len(times) >= 30:
            user_time = best_fitting_distribution(times)
        # otherwise use a uniform dist
        elif len(times) >= 1:
            average_time = np.mean(times)

            user_time = lambda avg_time=average_time: stats.uniform.rvs(loc=0, scale = 2*avg_time)

        else:
            user_time = lambda: stats.uniform.rvs(loc = 0,scale = 0)
        
        F[label] = user_time
    
    return F
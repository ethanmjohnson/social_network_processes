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
        "weibull": stats.weibull_min
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

def generate_F(log, net, im, fm):
    # this function generates the matrix F containing the pdfs associated with each transition in the petri net

    label_keys = [t.label for t in net.transitions]

    # initialise time differences dict
    time_differences = {key: [] for key in label_keys}

    for trace in tqdm(log):
        trace_log = EventLog()
        trace_log.append(trace)
        fitness = token_replay.apply(trace_log, net, im, fm)
        # find fitness, if 1, trace is in net and so all behaviour (including multiple input places per transition) is visible
        if fitness[0]['trace_fitness'] == 1.0:
            for i in range(1, len(trace)):
                prev_event = trace[i-1]
                curr_event = trace[i]
                # find difference in time between events in trace
                delta = (curr_event['time:timestamp'] - prev_event['time:timestamp']).total_seconds()

                time_differences[curr_event['concept:name']].append(delta)

    name_keys = [t.name for t in net.transitions]

    label_time_differences = {key: [] for key in name_keys}

    for t in net.transitions:
        label_time_differences[t.name] = time_differences[t.label]
    
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

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

def choose_transition(transitions, user_distributions):
    # logic to choose an enabled transition to fire
    # Inputs:
    # transitions - list of enabled transitions
    # user_distributions - a dictionary mapping users in the petri net to a pdf

    # outputs:
    # selected_transition - the chosen transition to fire
    # transition_time - the time delay for this transition to fire

    times = []
    # randomly shuffle the transition list so there is a random chance of choosing transitions with equal time
    random.shuffle(transitions)

    # generate a time delay for each user

    for trans in transitions:
        trans_name = trans.label
        func = user_distributions[trans_name]
        result = func()
        times.append(result)

    # find the smallest time

    min_time = np.inf
    for time in times:
        if time < min_time:
            min_time = time

    # find the associated transition with the smallest time

    trans_index = times.index(min_time)

    selected_transition = transitions[trans_index]
    transition_time = times[trans_index]
    return (selected_transition, transition_time)



def initialise_user_times(net: pm4py.objects.petri_net.obj.PetriNet):
    # initialise the dictionary containing the user retweet times
    transition_names = [t.label for t in net.transitions if t.label is not None]
    unique_names = list(set(transition_names))

    times_dict = {}

    for name in unique_names:
        times_dict[name] = []
    return times_dict

def find_user_retweet_times(times_dict: dict, log: EventLog, net, im, fm):

    for j in tqdm(range(len(log))):
        trace = log[j]
        trace_log = EventLog()
        trace_log.append(trace)
        # replay to find if trace is in petri net
        fitness = token_replay.apply(trace_log, net, im, fm)

        if fitness[0]['trace_fitness'] == 1.0:
            # find the difference in times from event log if the trace exists in petri net
            for i in range(1, len(trace)):
                times_dict[trace[i]['concept:name']].append((trace[i]['time:timestamp'] - trace[i-1]['time:timestamp']).total_seconds())
    
    return times_dict

def find_user_retweet_dist(times_dict: dict):
    user_distributions = {}

    for key in times_dict.keys():
        times = times_dict[key]

        if len(times) >= 30:
            user_time = best_fitting_distribution(times)

        elif len(times) > 1:
            average_time = np.mean(times)

            user_time = lambda: stats.uniform.rvs(loc=0, scale = 2*average_time)
        elif len(times) == 1:
            user_time = lambda: stats.uniform.rvs(loc = 0, scale = 2*times[0])
        else:
            user_time = lambda: stats.uniform.rvs(loc = 0,scale = 0)
        
        user_distributions[key] = user_time
    # set silent transitions to a high number so they never fire unless only enabled transition
    # this is why your code is taking 1000000 years in simulation time
    user_distributions[None] = lambda: np.random.uniform(1000000, 1000001)

    return user_distributions




def best_fitting_distribution(time_differences):
    # Convert time data (Timedelta) to hours
    data_seconds = np.array(time_differences)


    # List of distributions available in numpy.random
    numpy_distributions = {
        "exponential": stats.expon,
        "gamma": stats.gamma,
        "lognormal": stats.lognorm,
        "weibull": stats.weibull_min
    }

    best_fit = None
    best_params = None
    best_ks = np.inf

    # Loop over each distribution
    for dist_name, dist_func in numpy_distributions.items():
        try:
            # Fit the distribution to the data
            params = dist_func.fit(data_seconds)

            # Perform the Kolmogorov-Smirnov test
            ks_stat, _ = stats.kstest(data_seconds, dist_func.cdf, args=params)

            # Track the best fit (smallest KS statistic)
            if ks_stat < best_ks:
                best_ks = ks_stat
                best_fit = dist_name
                best_params = params
        except Exception as e:
            print(f"Skipping {dist_name}: {e}")

    # Return the best-fitting distribution and its parameters
    if best_fit == "exponential":
        lambda_value = best_params[0]
        return lambda: stats.expon.rvs(scale=lambda_value)
    elif best_fit == "gamma":
        shape, loc, scale = best_params
        return lambda: stats.gamma.rvs(shape, loc=loc, scale=scale)
    elif best_fit == "lognormal":
        shape, loc, scale = best_params
        return lambda: stats.lognorm.rvs(shape, loc=loc, scale=scale)
    elif best_fit == "weibull":
        c, loc, scale = best_params
        return lambda: stats.weibull_min.rvs(c, loc=loc, scale=scale)
    else:
        average_time = np.mean(time_differences)
        return lambda: stats.uniform.rvs(loc=0, scale=2 * average_time)
    
def generate_probability_matrix(log, net, im, fm):
    # this function generates the matrix P used to choose a transition to fire


    transition_names = [t.label for t in net.transitions if t.label is not None]
    # produce the frequency df
    freq = pd.DataFrame(0, index = transition_names, columns = transition_names)

    for trace in tqdm(log):
        trace_log = EventLog()
        trace_log.append(trace)
        fitness = token_replay.apply(trace_log, net, im, fm)

        if fitness[0]['trace_fitness'] == 1.0:
            for i in range(len(trace)-1):
                freq.at[trace[i]['concept:name'], trace[i+1]['concept:name']] += 1


    row_sums = freq.sum(axis=1)
    P = freq.div(row_sums, axis=0)

    return P

def generate_pdf_matrix(log, net, im, fm):
    # this function generates the matrix F containing the pdfs associated with each transition in the petri net

    transition_names = [t.label for t in net.transitions if t.label is not None]
    
    F = pd.DataFrame(0, index = transition_names, columns = transition_names)

    time_matrix = pd.DataFrame(index = transition_names, columns = transition_names)
    time_matrix = time_matrix.applymap(lambda x: [])

    for j in tqdm(range(len(log))):
        trace = log[j]
        trace_log = EventLog()
        trace_log.append(trace)

        fitness = token_replay.apply(trace_log, net, im, fm)

        if fitness[0]['trace_fitness'] == 1.0:
            for i in range(1, len(trace)):
                time_matrix.at[trace[i-1]['concept:name'], trace[i]['concept:name']].append((trace[i]['time:timestamp'] - trace[i-1]['time:timestamp']).total_seconds())



    for name_row in transition_names:
        for name_col in transition_names:
            times = time_matrix.at[name_row, name_col]

            if len(times) >= 30:
                user_time = best_fitting_distribution(times)

            elif len(times) > 1:
                average_time = np.mean(times)

                user_time = lambda: stats.uniform.rvs(loc=0, scale = 2*average_time)
            elif len(times) == 1:
                user_time = lambda: stats.uniform.rvs(loc = 0, scale = 2*times[0])
            else:
                user_time = lambda: stats.uniform.rvs(loc = 0,scale = 0)
            
            F.at[name_row, name_col] = user_time
    return F


if __name__ == "__main__":
    from pm4py.objects.petri_net.importer import importer as pn_importer
    from pm4py.objects.petri_net.utils import petri_utils
    import random
    from pm4py.objects.log.importer.xes import importer as xes_importer

    # load log and net
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply("/Users/ethanjohnson/Desktop/mphil-project/data/processed/honduras_coordinated_log.xes", variant=variant, parameters=parameters)

    net, im, fm = pn_importer.apply("/Users/ethanjohnson/Desktop/mphil-project/models/honduras_coordinated.pnml")

    # P = generate_probability_matrix(log, net, im, fm)
    # print(P)
    F = generate_pdf_matrix(log, net, im, fm)
    print(F.at['u1611919694', 'u977748062306217984']())
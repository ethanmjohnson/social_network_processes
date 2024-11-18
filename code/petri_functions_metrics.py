# this has all the functions for the metrics used in the paper for petri nets

import os
from analysis import load_log, discover_petri
import numpy as np
from pm4py.objects.log.obj import EventLog, Trace
import pm4py
import networkx as nx
from pm4py.algo.conformance.tokenreplay.algorithm import apply as replay
from mc_functions_metrics import find_user_retweetingTimes


def petri_paths(log):
    # finds the paths in a petri net
    net, im, fm = discover_petri(log)
    rp = replay(log, net, im, fm)


    path_collection = []

    for rps in rp:
        single_path = []
        for transition in rps['activated_transitions']:
            single_path.append(transition.label)
        path_collection.append(single_path)

    return path_collection

def time_between_events_pn(log):
    # finds the interarrival times for a single log for a petri net

    paths = petri_paths(log)
    average_retweet = find_user_retweetingTimes(log)


    import datetime
    log_time_diffs = []

    

    for i in range(len(paths)):
        times = []

        current_time = datetime.datetime.now()
        for j in range(len(paths[i])):
            current_time = current_time + datetime.timedelta(seconds = average_retweet[paths[i][j]])
            times.append(current_time)

        time_diffs = [((times[k+1]-times[k]).total_seconds())/3600 for k in range(len(times)-1)]


        log_time_diffs.append(np.mean(time_diffs))
    return log_time_diffs

def folder_IT_between_pn(folder_path, num):

    import os
    # this finds the interarrival time between events of a folder (petri net representation)

    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    diff_values = []

    for file in logs[:num]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)
        diff_values = diff_values + time_between_events_pn(log)

    return diff_values



def IT_between_log(eventlog: EventLog) -> list:
    # calculates the interarrival times in the event log
    interarrival_times = []
    for trace in eventlog:
        trace_times = []
        for event in trace:
            trace_times.append(event['time:timestamp'])
        trace_interarrival = [((x - trace_times[i - 1]).total_seconds())/3600 for i, x in enumerate(trace_times) if i > 0]

        interarrival_times.append(np.mean(trace_interarrival))

    return interarrival_times


def folder_IT_between_log(folder_path, num):
    # this finds the interarrival time between events of a folder (event log representation)
    average_intertime = []

    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    for file_name in logs[:num]:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            log = load_log(file_path)
            times = IT_between_log(log)
            average_intertime = average_intertime + times
    return average_intertime

def folder_IT_firstlast_log(folder_path, num):
    # interarrival times between first and last events in event log
    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]
    for file_name in logs[:num]:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            log = load_log(file_path)
            trace_duration = []
            for trace in log:
                trace_duration.append(((trace[len(trace)-1]['time:timestamp']-trace[0]['time:timestamp']).total_seconds())/3600)
    return trace_duration

def time_between_firstlast_pn(log):
    import datetime

    paths = petri_paths(log)
    average_retweet = find_user_retweetingTimes(log)
    # this finds the ineterarrival times between the first and last events in the petri net
    log_time_diffs = []

    

    for i in range(len(paths)):
        times = []

        current_time = datetime.datetime.now()
        for j in range(len(paths[i])):
            current_time = current_time + datetime.timedelta(seconds = average_retweet[paths[i][j]])
            times.append(current_time)

        time_diffs = ((times[len(times)-1] - times[0]).total_seconds())/3600

        log_time_diffs.append(time_diffs)
    return log_time_diffs

def folder_IT_firstlast_pn(folder_path, num):
    import os
    # this finds the interarrival times between the first and last events of a petri net given a folder of event logs

    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    diff_values = []

    for file in logs[:num]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)
        diff_values = diff_values + time_between_firstlast_pn(log)

    return diff_values


def density_analysis(eventlog):
    # density for single event log
    log = load_log(eventlog)
    
    tree = pm4py.discover_process_tree_inductive(log)
    bpmn_graph = pm4py.convert_to_bpmn(tree)

    bpmn_model = bpmn_graph.get_graph()

    density = nx.density(bpmn_model)

    return density


def folder_density(folder_path):
    # density for folder of event logs
    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    density_values = []

    for file in logs[:30]:
        file_path = os.path.join(folder_path, file)
        density_values.append(density_analysis(file_path))

    return density_values
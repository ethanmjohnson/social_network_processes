# a module containing functions for use with analysing event logs

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog, Trace
import os
import numpy as np
import pm4py
import random


def load_log(file_path):
    # this function loads an .xes format event log
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(file_path, variant=variant, parameters=parameters)
    return log

def discover_petri(eventlog, visualise = False):
    print('discovering...')
    net, im, fm = pm4py.discover_petri_net_inductive(eventlog)
    if visualise is True:
        print('visualising...')
        pm4py.view_petri_net(net, im, fm)
    return (net, im, fm)


def calculate_interarrival_times(eventlog: EventLog) -> list:
    # calculates the event interarrival times in each trace for all traces
    interarrival_times = []
    for trace in eventlog:
        trace_times = []
        for event in trace:
            trace_times.append(event['time:timestamp'])
        trace_interarrival = [(x - trace_times[i - 1]).total_seconds() for i, x in enumerate(trace_times) if i > 0]
        interarrival_times = [*interarrival_times, *trace_interarrival]
    return interarrival_times


def calculate_interarrival_times_folder(folder_path):
    average_intertime = []
    for file_name in os.listdir(folder_path):
        if not file_name.startswith('.'):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                log = load_log(file_path)
                times = calculate_interarrival_times(log)
                average_intertime.append(np.mean(times))
    return average_intertime

def discover_model(log: EventLog, view_log = False):
    print('discovering...')
    net, im, fm = pm4py.discover_petri_net_inductive(log)

    if view_log:
        print('visualising...')
        pm4py.view_petri_net(net, im, fm, format='png')
    #pm4py.save_vis_petri_net(net, im, fm, "/Users/ethanjohnson/Desktop/mphil-project/figs/higgs_petri_postlog.png")

    return net, im, fm


def filter_log_activity_count(event_count, log):
    # this function removes activities that are seen fewer than the event_count in the log

    eventlist = []

    for trace in log:
        for event in trace:
            eventlist.append(event['concept:name'])

    unique_elements, counts = np.unique(eventlist, return_counts=True)

    combined_counts = list(zip(unique_elements, counts))

    filtered_events = []
    for element in combined_counts:
        if element[1] > event_count:
            filtered_events.append(element[0])

    filtered_log = EventLog()

    for trace in log:
        filtered_trace = Trace()
        i=0
        for event in trace:
            if event['concept:name'] in filtered_events:
                filtered_trace.insert(i, event)
                i+=1
        filtered_log.append(filtered_trace)
    
    extra_filtered_log = pm4py.filter_case_size(filtered_log, 2, 2**50)
    
    return extra_filtered_log


def filter_log_size(log_length, log):
    # this function randomly reduces the number of traces in log down to the size of log_length

    sample = random.sample(list(range(len(log))), log_length)
    new_log = EventLog()
    for number in sample:
        new_log.append(log[number])

    return new_log
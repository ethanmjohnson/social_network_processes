# a module containing functions for use with analysing event logs

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog
import os
import numpy as np


def load_log(file_path):
    # this function loads an .xes format event log
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(file_path, variant=variant, parameters=parameters)
    return log


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
                average_intertime.append(np.sum(times)/len(log))
    return average_intertime
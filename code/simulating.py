from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo_simulation
from pm4py.objects.log.obj import EventLog, Trace, Event
import os
from pm4py.objects.log.util.split_train_test import split


# simulates an event log from a real event log using a montecarlo simulation



def simulating(file, trainsplit):

    print("Reading event log...")

    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(file, variant=variant, parameters=parameters)

    train, test = split(log, trainsplit)

    pm4py.write_xes(train, '/Users/ethanjohnson/Desktop/mphil-project/processed_data/trainset.xes')
    pm4py.write_xes(test, '/Users/ethanjohnson/Desktop/mphil-project/processed_data/testset.xes')


    simulated_log = EventLog()

    print('Discovering... \n')
    net, im, fm = pm4py.discover_petri_net_inductive(train)

    print("Simulating... \n")



    parameters={}
    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_MAX_THREAD_EXECUTION_TIME] = 1000

    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_NUM_SIMULATIONS] = 2000

    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.TIMESTAMP_KEY] = "time:timestamp"

    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.ACTIVITY_KEY] = "concept:name"

    count = 0
    for i in range(8):
        simlog, res = montecarlo_simulation.apply(train, net, im, fm, parameters=parameters)
        count +=1
        print(count)
        for trace in simlog:
            simulated_log.append(trace)


    desired_start_timestamp = test[0][0]["time:timestamp"]
    current_start_timestamp = simulated_log[0][0]["time:timestamp"]

    time_difference = desired_start_timestamp - current_start_timestamp

    for trace in simulated_log:
        for event in trace:
            event["time:timestamp"] += time_difference
    
    return simulated_log



trainsplit = 0.66
file = '/Users/ethanjohnson/Desktop/mphil-project/processed_data/honduras_log.xes'

simulated_log = simulating(file, trainsplit)

print('writing')

pm4py.write_xes(simulated_log, '/Users/ethanjohnson/Desktop/mphil-project/processed_data/simtest.xes')

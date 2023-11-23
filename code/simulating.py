from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py
import pm4py.algo.simulation.montecarlo as monte
from pm4py.objects.log.obj import EventLog, Trace, Event
import os


# simulates an event log from a real event log

#directory = os.path.dirname()

print("Reading event log...")

file = '/Users/ethanjohnson/Library/CloudStorage/Box-Box/MPhil/data/adjusted_event_log.xes'

variant = xes_importer.Variants.ITERPARSE
parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
eventlog = xes_importer.apply(file, variant=variant, parameters=parameters)

simulated_log = EventLog()

print('Discovering... \n')
net, im, fm = pm4py.discover_petri_net_inductive(eventlog)

print("Simulating... \n")

n = int(len(eventlog)/100)



# 

sim_trace = monte.algorithm.apply(eventlog, net, im, fm, parameters={"num_simulations": 10000, "parallelization": True, "max_thread_execution_time": 3600})[0]
simulated_log = pm4py.convert_to_event_log(sim_trace)

print(len(simulated_log))

print("Writing...")

#pm4py.write_xes(simulated_log, '/Users/ethanjohnson/Library/CloudStorage/Box-Box/MPhil/data/simulated_hondurasData.xes')

print("Done")




# priority:
# create bins of events, generate histogram from number of events in each bin.
# increase simulation numbers

# look at first bin for this data (t=0) suspect its because we dont have control over cases when length of trace is 1.

# check average transition time distributions
# try to build time distributions for other transitions in the net
# keep one tweet analysis

# take a uer filter them out of the event log - find time when previous activity occurred, 

# assuem when one user retweets the user in question will also retweet. take difference in times and plot

# send notes to anna and lewis


# 
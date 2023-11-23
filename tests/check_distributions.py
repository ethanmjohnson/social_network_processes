import pm4py
from pm4py import write_xes as xes
from pm4py.objects.log.obj import EventLog, Trace
from datetime import datetime, timedelta
import numpy as np
import pm4py.algo.simulation.montecarlo as monte

# checks the distributions of the simulated event log to see if realistic

# Function to generate timestamps based on an exponential distribution
def generate_timestamps(num_events, lambda_value):
    #timestamps = [timedelta(seconds=np.random.exponential(1/lambda_value)) for _ in range(num_events)]
    timestamps = [timedelta(seconds=np.random.exponential(1/lambda_value)) for _ in range(num_events)]
    return timestamps

# Generate event names and timestamps based on the exponential distribution
event_names = ['Event A', 'Event B', 'Event C']  # Example event names
num_events = 100  # Number of events to generate
lambda_value = 0.1  # Lambda value for exponential distribution

timestamps = generate_timestamps(num_events, lambda_value)

# Create a synthetic event log
log = EventLog()
trace = Trace()

current_time = datetime(2023, 1, 1)
for i in range(num_events):
    current_time += timestamps[i]
    event = {
        'concept:name': np.random.choice(event_names),
        'time:timestamp': current_time
    }
    trace.insert(i, event)
    

log.append(trace)

print(log[0][0])




# Extract timestamps from the event log
timestamps = []
for trace in log:
    for event in trace:
        timestamps.append(event['time:timestamp'])  # Assuming 'time:timestamp' is the timestamp attribute

# Calculate time differences (durations) between consecutive events
durations = []
for i in range(1, len(timestamps)):
    time_diff = timestamps[i] - timestamps[i - 1]
    durations.append(time_diff.total_seconds())

# Calculate statistics or analyze the durations
mean_duration = np.mean(durations)
median_duration = np.median(durations)
std_deviation = np.std(durations)

print(f"Mean Duration: {mean_duration} seconds")
print(f"Median Duration: {median_duration} seconds")
print(f"Standard Deviation: {std_deviation} seconds")

net, im, fm = pm4py.discover_petri_net_inductive(log)


sim_trace = monte.algorithm.apply(log, net, im, fm, parameters={"num_simulations": 1, "max_thread_execution_time": 3600})[0]
simlog = pm4py.convert_to_event_log(sim_trace)

for trace in simlog:
    for event in trace:
        print(event)


timestamps = []
for trace in simlog:
    for event in trace:
        timestamps.append(event['time:timestamp'])  # Assuming 'time:timestamp' is the timestamp attribute

# Calculate time differences (durations) between consecutive events
durations = []
for i in range(1, len(timestamps)):
    time_diff = timestamps[i] - timestamps[i - 1]
    durations.append(time_diff.total_seconds())

mean_duration = np.mean(durations)
median_duration = np.median(durations)
std_deviation = np.std(durations)



print(f"Mean Duration sim: {mean_duration} seconds")
print(f"Median Duration sim: {median_duration} seconds")
print(f"Standard Deviation sim: {std_deviation} seconds")
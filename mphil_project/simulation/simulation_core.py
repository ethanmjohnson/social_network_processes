from pm4py.objects.log.obj import Event, EventLog, Trace
from datetime import datetime, timedelta
from pm4py.objects.petri_net.semantics import enabled_transitions, execute
from simulation_utils import initialise_user_times, find_user_retweet_dist, find_user_retweet_times, choose_transition


def simulate_pn_trace(net, im, fm, log):
    current_marking = im
    trace = Trace()
    current_time = datetime.now()
    times_dict = initialise_user_times(net)
    times_dict = find_user_retweet_times(times_dict, log, net, im, fm)
    user_distributions = find_user_retweet_dist(times_dict)

    while current_marking != fm:
        # get list of currently enabled transitions
        transitions = list(enabled_transitions(net, current_marking))
        # choose a transition to fire
        transition, transition_time = choose_transition(transitions, user_distributions)
        
        current_time = current_time + timedelta(seconds=transition_time)
        # generate event
        event = Event({
                "concept:name": transition.label,
                "time:timestamp": current_time
            })
        # add transition to trace
        trace.append(event)
        # fire transition, update marking
        current_marking = execute(transition, net, current_marking)

    return trace
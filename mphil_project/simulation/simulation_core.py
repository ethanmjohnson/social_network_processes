from pm4py.objects.log.obj import Event, EventLog, Trace
from datetime import datetime, timedelta
from pm4py.objects.petri_net.semantics import enabled_transitions, execute
from simulation_utils import find_user_retweetingTimes, choose_transition


def simulate_pn_trace(net, im, fm, log):
    current_marking = im
    trace = Trace()
    current_time = datetime.now()
    user_distributions = find_user_retweetingTimes(log)

    while current_marking != fm:
        # get list of currently enabled transitions
        transitions = list(enabled_transitions(net, current_marking))
        # choose a transition to fire
        transition, transition_time = choose_transition(transitions, user_distributions)
        
        current_time = current_time + timedelta(hours=transition_time)
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
from pm4py.objects.log.obj import Event, EventLog, Trace
from datetime import datetime, timedelta
from pm4py.objects.petri_net.semantics import enabled_transitions, execute
from simulation_utils import choose_transition, generate_F, generate_P


def simulate_pn_trace(net, im, fm, log, num_sims = 10):
    # this function runs the simulation of a stochastic petri net

    # generate the probability and pdf arrays
    F = generate_F(log, net, im, fm)
    P = generate_P(log, net, im, fm)

    # initialise a simulated event log
    sim_log = EventLog()

    for i in range(num_sims):
        current_marking = im
        trace = Trace()
        current_time = datetime.now()

        # run simulation until final marking has been reached
        while current_marking != fm:
            # get list of currently enabled transitions
            transitions = list(enabled_transitions(net, current_marking))
            # choose a transition to fire
            transition, transition_time = choose_transition(transitions, P, F)
            
            # update current time

            if transition_time > 1e8:
                transition_time = 1e8
            
            if transition_time < 0.0:
                transition_time = 0.0

            current_time = current_time + timedelta(seconds=transition_time)

            if transition.label != None:
                # generate event if the transition is not silent
                event = Event({
                        "concept:name": transition.label,
                        "time:timestamp": current_time
                    })
                # add transition to trace
                trace.append(event)
            # fire transition, update marking
            current_marking = execute(transition, net, current_marking)
        
        sim_log.append(trace)

    return sim_log

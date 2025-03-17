from pm4py.objects.log.obj import Event, EventLog, Trace
from datetime import datetime, timedelta
from pm4py.objects.petri_net.semantics import enabled_transitions, execute
from simulation_utils import choose_transition, generate_F, generate_P


def simulate_pn_trace(net, im, fm, log, num_sims = 10):
    """
    Simulates num_sims traces of a free-choice Stochastic Petri net

    Inputs:
    net: the Petri net
    im: the initial marking of a Petri net
    fm: the final marking of a Petri net
    log: the event log the Petri net was discovered from
    num_sims: (default = 10) the number of traces to simulate from the free-choice Stochastic Petri net

    Outputs:
    sim_log: the simulated event log from the free-choice Stochastic Petri net containing num_sims traces
    """

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

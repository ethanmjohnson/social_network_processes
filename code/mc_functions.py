# this file contains all of the functions for extracting a markov chain from an event log

import numpy as np
import pandas as pd
import networkx as nx

def calc_transition_matrix(log):
    # this function calculates the transition matrix from an event log
    users_long = []
    for trace in log:
        for event in trace:
            users_long.append(event['concept:name'])

    users = np.unique(users_long)

    frequency_matrix = pd.DataFrame(0, index=users, columns=users)

    for trace in log:
        first_event = trace[0]['concept:name']
        for i in range(len(trace)-1):
            current_event = trace[i]['concept:name']
            next_event = trace[i+1]['concept:name']
            frequency_matrix.loc[current_event, next_event] += 1
        # adds the end state to beginning state transition
        frequency_matrix.loc[next_event, first_event] += 1


    transition_matrix = pd.DataFrame(0.0, index = users, columns=users)

    # converts frequency matrix to probability matrix
    for row in range(len(frequency_matrix)):
        row_sum = frequency_matrix.iloc[row].sum()
        for column in range(len(frequency_matrix)):
            transition_matrix.iloc[row, column] = frequency_matrix.iloc[row, column]/row_sum
        
    transition_matrix = transition_matrix.to_numpy()
    
    return (transition_matrix, users)


def find_start_probs(log, users):
        # this function finds the starting probabilities of the markov chain
    start_freq = pd.DataFrame(0, index = users, columns = ['frequency'])

    for trace in log:
        user = trace[0]['concept:name']
        start_freq.loc[user] += 1

    colsum = start_freq.sum()

    start_probs = pd.DataFrame(0, index = users, columns = ['probability'])

    for column in range(len(start_freq)):
            start_probs.iloc[column] = start_freq.iloc[column]/colsum

    return start_probs


def find_mc(transition_matrix, users):
    # this function produces the graph of the markov chain
  
    G = nx.DiGraph()


    for i, state in enumerate(users):
        G.add_node(state)

    
    for i, state_from in enumerate(users):
        for j, state_to in enumerate(users):
            weight = transition_matrix[i][j]
            if weight > 0:  
                G.add_edge(state_from, state_to, weight=weight)
    
    return G



def find_end_states(log):
    # this finds the end states of the markov chain
    end_states = []

    for trace in log:
        length = len(trace)
        user = trace[length-1]['concept:name']
        end_states.append(user)

    end_states = list(set(end_states))

    return end_states

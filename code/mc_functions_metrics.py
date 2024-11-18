# this file contains the functions to find the metrics in the paper for a markov chain

import pm4py
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix
import os
from mc_functions import calc_transition_matrix, find_end_states, find_start_probs, find_mc
from analysis import load_log
import datetime
from scipy.linalg import eig
import networkx as nx


def find_user_retweetingTimes(log):
    # this function finds the retweeting times of users in an event log
    users_long = []
    for trace in log:
        for event in trace:
            users_long.append(event['concept:name'])

    users = np.unique(users_long)

    # find the average time taken for each user to retweet i.e. times between each users retweet and the post


    average_retweet = {}

    df_log = pm4py.convert_to_dataframe(log)
    df = df_log.sort_values(by='time:timestamp')

    for user in users:

        subset_df = df[df['concept:name'] == user]

        times = list(subset_df['time:timestamp'])

        if len(times) >= 2:
            time_differences = [times[i] - times[i - 1] for i in range(1, len(times))]
            average_time = np.mean(time_differences)
            average_time = (average_time.total_seconds())/3600
        else:
            average_time = 0.0


        average_retweet[user] = average_time
    average_retweet[None] = 0.0

    return average_retweet



def find_paths_through_markov_chain(transition_matrix, starting_probs, end_state_names, state_names, threshold=0.01, max_depth=10):
    # this function finds all the paths through the markov chain


    # Number of states
    num_states = transition_matrix.shape[0]
    
    # Ensure that state_names is a list of strings
    assert isinstance(state_names, list), "state_names should be a list"
    assert isinstance(end_state_names, list), "end_state_names should be a list"

    # Check if all end_state_names exist in state_names
    for end_state in end_state_names:
        if end_state not in state_names:
            raise ValueError(f"End state {end_state} not found in state_names")
    
    # Convert transition matrix to a sparse graph if needed
    transition_matrix_sparse = csr_matrix(transition_matrix)
    
    # Create an adjacency list representation of the graph
    graph = defaultdict(list)
    for i in range(num_states):
        for j in range(num_states):
            prob = transition_matrix_sparse[i, j]
            if prob > 0:
                graph[i].append((j, prob))

    # Find the starting states based on non-zero starting probabilities
    start_states = [i for i in range(num_states) if starting_probs[i] > 0]

    # Convert end_state_names to their corresponding indices
    end_states = []
    for name in end_state_names:
        if name in state_names:
            end_states.append(state_names.index(name))
        else:
            print(f"Warning: State name {name} not found in state_names")

    # DFS function to find paths
    def dfs(graph, current_state, path, path_prob, end_states, paths, max_depth):
        # If the current state is in the end_states, store the path and its probability
        if current_state in end_states:
            paths.append((path, path_prob))
            return
        
        # If path length exceeds max_depth, stop further exploration
        if len(path) > max_depth:
            return

        # Explore adjacent states (transitions)
        for next_state, trans_prob in graph[current_state]:
            if trans_prob > threshold:  # Prune low probability transitions
                dfs(graph, next_state, path + [next_state], path_prob * trans_prob, end_states, paths, max_depth)

    # List to store paths
    paths = []

    # Start DFS from each starting state
    for start_state in start_states:
        initial_prob = starting_probs[start_state]
        dfs(graph, start_state, [start_state], initial_prob, end_states, paths, max_depth)

    # Convert paths from indices to state names for output
    named_paths = []
    for path, prob in paths:
        named_paths.append(([state_names[i] for i in path]))

    return named_paths



def time_between_events_mc(paths, average_retweet):
    # this function find the interarrival times of a markov chain
    log_time_diffs = []

    

    for i in range(len(paths)):
        times = []

        current_time = datetime.datetime.now()
        for j in range(len(paths[i])):
            current_time = current_time + datetime.timedelta(seconds = average_retweet[paths[i][j]])
            times.append(current_time)

        time_diffs = [((times[k+1]-times[k]).total_seconds())/3600 for k in range(len(times)-1)]


        log_time_diffs.append(np.mean(time_diffs))
    return log_time_diffs


def IT_between_mc(log):
    # this function finds the time between events of a single event log (markov chain representation)
    average_times = find_user_retweetingTimes(log)

    matrix, users = calc_transition_matrix(log)

    start_probs = find_start_probs(log, users)

    end_states = find_end_states(log)

    paths = find_paths_through_markov_chain(np.array(matrix), np.array(start_probs), end_states, list(users))

    time_diffs = time_between_events_mc(paths, average_times)

    return time_diffs


def folder_IT_between_mc(folder_path, num):
    # this finds the interarrival time between events of a folder (markov chain representation)

    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    diff_values = []

    for file in logs[:num]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)
        diff_values = diff_values + IT_between_mc(log)

    return diff_values


def time_between_firstlast_mc(paths, average_retweet):
    # this finds the interarrival times between the first and last events in the markov chains
    log_time_diffs = []

    

    for i in range(len(paths)):
        times = []

        current_time = datetime.datetime.now()
        for j in range(len(paths[i])):
            current_time = current_time + datetime.timedelta(seconds = average_retweet[paths[i][j]])
            times.append(current_time)

        time_diffs = ((times[len(times)-1] - times[0]).total_seconds())/3600

        log_time_diffs.append(time_diffs)
    return log_time_diffs



def IT_firstlast_mc(log):
    # this finds the interarrival times between first and last events givn an event log (mc representation)
    average_times = find_user_retweetingTimes(log)

    matrix, users = calc_transition_matrix(log)

    start_probs = find_start_probs(log, users)

    end_states = find_end_states(log)

    paths = find_paths_through_markov_chain(np.array(matrix), np.array(start_probs), end_states, list(users))

    time_diffs = time_between_firstlast_mc(paths, average_times)

    return time_diffs

def folder_IT_firstlast_mc(folder_path, num):
    # this finds the interarrival times between the first and last events of a markov chain given a folder of event logs

    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    diff_values = []

    for file in logs[:num]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)
        diff_values = diff_values + IT_firstlast_mc(log)

    return diff_values


def stationary_distribution(transition_matrix):
    # calculates the stationary distribution of a transition matrix
    n = transition_matrix.shape[0]

    eigvals, eigvecs = eig(transition_matrix.T)
  
    stationary = np.real(eigvecs[:, np.isclose(eigvals, 1)])

    stationary_distribution = stationary / stationary.sum()
    return stationary_distribution.flatten()


def kolmogorov_sinai_entropy(transition_matrix):
    # calculates the kolmogorov sinai entropy of a transition matrix
    pi = stationary_distribution(transition_matrix)
    entropy = 0.0
    
    for i in range(len(transition_matrix)):
        for j in range(len(transition_matrix)):
            if transition_matrix[i, j] > 0:
                entropy += pi[i] * transition_matrix[i, j] * np.log(transition_matrix[i, j])
    return -entropy  

def ks_entropy_folder(folder_path):
    # calculates the k-s entropy given a folder of event logs
    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    entropy_values = []

    for file in logs[:30]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)

        P, users = calc_transition_matrix(log)

        entropy_values.append(kolmogorov_sinai_entropy(P))

    return entropy_values

def mc_density(log):
    # this finds the density of a markov chain

    transition_matrix, users = calc_transition_matrix(log)

    G = find_mc(transition_matrix, users)

    density = nx.density(G)

    return density

def density_folder_mc(folder_path):
    # this finds the density of a markov chain from a folder of logs
    logs = [f for f in os.listdir(folder_path) if f.endswith('.xes')]

    density_values = []

    for file in logs[:30]:
        file_path = os.path.join(folder_path, file)
        log = load_log(file_path)
        density_values.append(mc_density(log))

    return density_values
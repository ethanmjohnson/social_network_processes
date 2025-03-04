# logic for choosing which transition fires

import random
import numpy as np
import scipy.stats as stats
import random
import pm4py

def choose_transition(transitions, user_distributions):
    # logic to choose an enabled transition to fire
    # Inputs:
    # transitions - list of enabled transitions
    # user_distributions - a dictionary mapping users in the petri net to a pdf

    # outputs:
    # selected_transition - the chosen transition to fire
    # transition_time - the time delay for this transition to fire

    times = []
    # randomly shuffle the transition list so there is a random chance of choosing transitions with equal time
    random.shuffle(transitions)

    # generate a time delay for each user

    for trans in transitions:
        trans_name = trans.label
        func = user_distributions[trans_name]
        result = func()
        times.append(result)

    # find the smallest time

    min_time = np.inf
    for time in times:
        if time < min_time:
            min_time = time

    # find the associated transition with the smallest time

    trans_index = times.index(min_time)

    selected_transition = transitions[trans_index]
    transition_time = times[trans_index]
    return (selected_transition, transition_time)



def find_user_retweetingTimes(log):
    # this function finds the retweeting times of users in an event log
    users_long = []
    for trace in log:
        for event in trace:
            users_long.append(event['concept:name'])

    users = np.unique(users_long)

    # find the average time taken for each user to retweet i.e. times between each users retweet and the post


    user_distributions = {}

    df_log = pm4py.convert_to_dataframe(log)
    df = df_log.sort_values(by='time:timestamp')

    for user in users:

        subset_df = df[df['concept:name'] == user]

        times = list(subset_df['time:timestamp'])

        time_differences = [times[i] - times[i - 1] for i in range(1, len(times))]

        if len(times) >= 30:
            user_time = best_fitting_distribution(time_differences)
            
        else:
            average_time = np.mean([td.total_seconds() for td in time_differences])  # Convert Timedelta to seconds
            average_time = average_time / 3600 

            user_time = lambda: np.random.uniform(0, 2*average_time)
            

        user_distributions[user] = user_time
    # set silent transitions to a high number so they never fire unless only enabled transition
    # this is why your code is taking 1000000 years in simulation time
    user_distributions[None] = lambda: np.random.uniform(1000000, 1000001)

    return user_distributions




def best_fitting_distribution(time_differences):
    # Convert time data (Timedelta) to hours
    data_hours = np.array([td.total_seconds() / 3600 for td in time_differences])


    # List of distributions available in numpy.random
    numpy_distributions = {
        "exponential": stats.expon,
        "gamma": stats.gamma,
        "lognormal": stats.lognorm,
        "weibull": stats.weibull_min
    }

    best_fit = None
    best_params = None
    best_ks = np.inf

    # Loop over each distribution
    for dist_name, dist_func in numpy_distributions.items():
        try:
            # Fit the distribution to the data
            params = dist_func.fit(data_hours)

            # Perform the Kolmogorov-Smirnov test
            ks_stat, _ = stats.kstest(data_hours, dist_func.cdf, args=params)

            # Track the best fit (smallest KS statistic)
            if ks_stat < best_ks:
                best_ks = ks_stat
                best_fit = dist_name
                best_params = params
        except Exception as e:
            print(f"Skipping {dist_name}: {e}")
    

    # Return the best-fitting distribution and its parameters
    if best_fit == "exponential":
        lambda_value = best_params[0]
        return lambda: np.random.exponential(lambda_value)
    elif best_fit == "normal":
        mean, std = best_params
        return lambda: np.random.normal(mean, std)
    elif best_fit == "gamma":
        shape, loc, scale = best_params
        return lambda: np.random.gamma(shape, scale)
    elif best_fit == "lognormal":
        shape, loc, scale = best_params
        return lambda: np.random.lognormal(shape, scale)
    elif best_fit == "weibull":
        c, loc, scale = best_params
        return lambda: np.random.weibull(c)
    else:
        #time_differences = [time_differences[i] - time_differences[i - 1] for i in range(1, len(time_differences))]
        average_time = np.mean(time_differences)
        average_time = (average_time.total_seconds())/3600
        return lambda: np.random.uniform(0, 2*average_time)
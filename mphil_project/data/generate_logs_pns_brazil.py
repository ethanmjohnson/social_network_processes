def create_brazil_event_logs(data, trim_length, log_length):

    """
    This function converts a jsonlines file to an EventLog for the Brazil datasets. 

    Inputs:
    data: jsonlines file to convert
    trim_length: length to trim each trace to
    log_length: desired length of returned log

    Outputs:
    good_short_log: an event log for the uncoordinated users
    bad_short_log: an event log for the coordinated users
    """

    from pm4py.objects.conversion.log import converter as log_converter
    from pm4py.filtering import filter_case_size
    from pm4py.objects.log.obj import EventLog, Trace

    df = data.loc[:, ['retweeted_status.id_str', 'user.id_str', 'timestamp_ms', 'botscore']]

    df = df.rename(columns = {'retweeted_status.id_str': 'retweet_tweetid', 'user.id_str': 'userid', 'timestamp_ms': 'tweet_time'})

    # convert times to datetime format
    df['tweet_time'] = pd.to_datetime(df['tweet_time'], unit='ms')
    # remove problematic ID characters
    df['userid'] = df['userid'].astype('str')
    df['userid'] = df['userid'].str.replace('[+=]', '', regex=True)
    df['userid'] = ['u' + id for id in df['userid']]
    # convert tweet ID to int
    df['retweet_tweetid'] = df['retweet_tweetid'].astype('Int64')

    # format dataframe
    df.sort_values(by = 'tweet_time', ascending=True, inplace=True)
    df = df[df['retweet_tweetid'].isnull() == False]
    df = df[df['userid'].isnull() == False]

    bad_df = df[df['botscore'] >= 0.9]
    good_df = df[df['botscore'] <= 0.1]


    bad_df = bad_df.loc[:, ['retweet_tweetid', 'userid', 'tweet_time']]
    good_df = good_df.loc[:, ['retweet_tweetid', 'userid', 'tweet_time']]

    cols = ['case:concept:name', 'concept:name', 'time:timestamp']
    bad_df.columns = cols
    good_df.columns = cols

    selected_df = good_df

    idx = selected_df.groupby(['case:concept:name', 'concept:name'])['time:timestamp'].idxmin()
    earliest_events_df = selected_df.loc[idx].reset_index(drop=True)
    earliest_events_df.sort_values(by = 'time:timestamp', ascending=True, inplace=True)

    length_df = earliest_events_df.groupby('case:concept:name').filter(lambda x: len(x) >= 2)


    good_log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # trim each trace of log to length n

    good_trimmed_log = EventLog()

    for trace in good_log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            for i in range(trim_length):
                trimmed_trace.append(trace[i])
            good_trimmed_log.append(trimmed_trace)
        else:
            good_trimmed_log.append(trace)

    # remove traces of length 1
    filtered_log = filter_case_size(good_trimmed_log, 2, 1e6)

    # select the first x traces
    good_short_log = EventLog()

    for i in range(log_length):
        good_short_log.append(filtered_log[i])


    
    selected_df = bad_df

    idx = selected_df.groupby(['case:concept:name', 'concept:name'])['time:timestamp'].idxmin()
    earliest_events_df = selected_df.loc[idx].reset_index(drop=True)
    earliest_events_df.sort_values(by = 'time:timestamp', ascending=True, inplace=True)

    length_df = earliest_events_df.groupby('case:concept:name').filter(lambda x: len(x) >= 2)


    bad_log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # trim each trace of log to length n

    bad_trimmed_log = EventLog()

    for trace in bad_log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            for i in range(trim_length):
                trimmed_trace.append(trace[i])
            bad_trimmed_log.append(trimmed_trace)
        else:
            bad_trimmed_log.append(trace)

    # remove traces of length 1
    filtered_log = filter_case_size(bad_trimmed_log, 2, 1e6)

    # select the first x traces
    bad_short_log = EventLog()

    for i in range(log_length):
        bad_short_log.append(filtered_log[i])

    return good_short_log, bad_short_log



if __name__ == "__main__":

    import pm4py
    import pandas as pd
    import os

    print("collecting files...")
    # add path to the folder containing the 2018 Brazil election data
    folder_path = "brazil_elections-2018"

    dataframes = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            dataframes.append(df)

    data = pd.concat(dataframes, ignore_index=True)

    good_log, bad_log = create_brazil_event_logs(data, 5, 500)

    # add output path for uncoordinated and coordinated logs
    pm4py.write_xes(good_log, "brazil_uncoordinated_log.xes")
    pm4py.write_xes(bad_log, "brazil_coordinated_log.xes")

    print("discovering uncoordinated Petri net...")
    net, im, fm = pm4py.discover_petri_net_inductive(good_log, noise_threshold=0.2, multi_processing=True)

    # add output path to uncoordinated Petri net
    print("saving uncoordinated Petri net...")
    pm4py.write_pnml(net, im, fm, "brazil_uncoordinated.pnml")

    print("discovering coordinated Petri net...")
    net, im, fm = pm4py.discover_petri_net_inductive(bad_log, noise_threshold=0.2, multi_processing=True)

    # add output path to coordinated Petri net
    print("saving coordinated Petri net...")
    pm4py.write_pnml(net, im, fm, "brazil_coordinated.pnml")

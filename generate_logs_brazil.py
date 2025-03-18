def create_brazil_event_logs(project_root, trim_length, log_length):

    """
    This function converts a jsonlines file to an EventLog for the Brazil datasets. 

    Inputs:
    folder_path: path to folder containing brazil_elections-2018 dataset
    trim_length: length to trim each trace to
    log_length: desired length of returned log

    Outputs:
    brazil_1_short_log: an event log for the users with a bot score of >= 0.9
    brazil_2_short_log: an event log for the users with a bot score of <= 0.1
    """
    import pm4py
    from pm4py.objects.conversion.log import converter as log_converter
    from pm4py.filtering import filter_case_size
    from pm4py.objects.log.obj import EventLog, Trace
    import os
    import pandas as pd

    print("collecting files...")

    folder_path = os.path.join(project_root, "data/brazil_elections-2018")

    dataframes = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            dataframes.append(df)

    data = pd.concat(dataframes, ignore_index=True)

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

    # split dataset using botscore - coordinated if botscore is >= 0.9 and uncoordinated if <= 0.1
    brazil_1_df = df[df['botscore'] >= 0.9]
    brazil_2_df = df[df['botscore'] <= 0.1]


    brazil_1_df = brazil_1_df.loc[:, ['retweet_tweetid', 'userid', 'tweet_time']]
    brazil_2_df = brazil_2_df.loc[:, ['retweet_tweetid', 'userid', 'tweet_time']]

    cols = ['case:concept:name', 'concept:name', 'time:timestamp']
    brazil_1_df.columns = cols
    brazil_2_df.columns = cols

    selected_df = brazil_2_df

    idx = selected_df.groupby(['case:concept:name', 'concept:name'])['time:timestamp'].idxmin()
    earliest_events_df = selected_df.loc[idx].reset_index(drop=True)
    earliest_events_df.sort_values(by = 'time:timestamp', ascending=True, inplace=True)

    length_df = earliest_events_df.groupby('case:concept:name').filter(lambda x: len(x) >= 2)


    brazil_2_log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # trim each trace of log to length n

    brazil_2_trimmed_log = EventLog()

    for trace in brazil_2_log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            for i in range(trim_length):
                trimmed_trace.append(trace[i])
            brazil_2_trimmed_log.append(trimmed_trace)
        else:
            brazil_2_trimmed_log.append(trace)

    # remove traces of length 1
    brazil_2_filtered_log = filter_case_size(brazil_2_trimmed_log, 2, 1e6)

    # select the first x traces
    brazil_2_short_log = EventLog()

    for i in range(log_length):
        brazil_2_short_log.append(brazil_2_filtered_log[i])


    
    selected_df = brazil_1_df

    idx = selected_df.groupby(['case:concept:name', 'concept:name'])['time:timestamp'].idxmin()
    earliest_events_df = selected_df.loc[idx].reset_index(drop=True)
    earliest_events_df.sort_values(by = 'time:timestamp', ascending=True, inplace=True)

    length_df = earliest_events_df.groupby('case:concept:name').filter(lambda x: len(x) >= 2)


    brazil_1_log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # trim each trace of log to length n

    brazil_1_trimmed_log = EventLog()

    for trace in brazil_1_log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            trimmed_trace.attributes.update(trace.attributes)
            for i in range(trim_length):
                trimmed_trace.append(trace[i])
            brazil_1_trimmed_log.append(trimmed_trace)
        else:
            brazil_1_trimmed_log.append(trace)

    # remove traces of length 1
    brazil_1_filtered_log = filter_case_size(brazil_1_trimmed_log, 2, 1e6)

    # select the first x traces
    brazil_1_short_log = EventLog()

    for i in range(log_length):
        brazil_1_short_log.append(brazil_1_filtered_log[i])


    pm4py.write_xes(brazil_2_short_log, os.path.join(project_root, "data/brazil_2.xes"))
    pm4py.write_xes(brazil_1_short_log, os.path.join(project_root, "data/brazil_1.xes"))

if __name__ == "__main__":
    from load_config import load_config

    config = load_config()

    project_root = config['project_root']

    create_brazil_event_logs(project_root, 10, 200)


    

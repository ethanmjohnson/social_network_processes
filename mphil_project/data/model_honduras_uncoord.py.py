def create_honduras_uncoord_event_log(data, trim_length, log_length):
    """
    This function converts a jsonlines file to an EventLog. 

    Inputs:
    data: jsonlines file to convert
    trim_length: length to trim each trace to
    log_length: desired length of returned log

    Outputs:
    short_log: an event log
    """
    from pm4py.objects.conversion.log import converter as log_converter
    from pm4py.filtering import filter_case_size
    from pm4py.objects.log.obj import EventLog, Trace

    df = []

    df = data.loc[:, ['tweet_time', 'userid', 'retweet_tweetid']]

    # convert times to datetime format
    df['tweet_time'] = pd.to_datetime(df['tweet_time'])
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

    cols = ['time:timestamp', 'concept:name', 'case:concept:name']
    df.columns = cols

    # filters traces that only contain a single event
    length_df = df.groupby('case:concept:name').filter(lambda x: len(x) >= 2)
    # convert df to log
    log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # trim each trace of log to length n

    trimmed_log = EventLog()

    for trace in log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            for i in range(trim_length):
                trimmed_trace.append(trace[i])
            trimmed_log.append(trimmed_trace)
        else:
            trimmed_log.append(trace)

    # remove traces of length 1
    filtered_log = filter_case_size(trimmed_log, 2, 1e6)

    # select the first x traces
    short_log = EventLog()

    for i in range(log_length):
        short_log.append(filtered_log[i])

    return short_log
 



if __name__ == "__main__":
    import pm4py
    import pandas as pd
    from pathlib import Path
    from pm4py.visualization.petri_net import visualizer as pn_viz

    print("create log...")

    path = Path(__file__).parent.parent.parent / "data/external/honduras-good-anonymized"

    data = pd.read_json(path, lines = True)

    log = create_honduras_uncoord_event_log(data, 30, 100)

    pm4py.write_xes(log, Path(__file__).parent.parent.parent / "data/processed/honduras_uncoordinated_log.xes")

    print("discovering Petri net...")
    net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)


    print("saving Petri net...")
    pm4py.write_pnml(net, im, fm, str(Path(__file__).parent.parent.parent / "models/honduras_uncoordinated.pnml"))

    # visualise pn
    print("visualising...")
    gviz = pn_viz.apply(net, im, fm)

    # save pn image

    pn_viz.save(gviz, Path(__file__).parent.parent.parent / "figures/honduras_uncoordinated.png")




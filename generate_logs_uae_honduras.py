def create_event_log(file_path, trim_length, log_length):
    """
    This function converts a jsonlines file to an EventLog for the Honduras and UAE datasets. This function saves the outputted event log
    to the same folder containing the input data.

    Inputs:
    file_path: the path to a corresponding jsonlines file containing the data from the Honduras or UAE datasets (coordinated or uncoordinated)
    trim_length: length to trim each trace to
    log_length: desired length of returned log


    """
    from pm4py.objects.conversion.log import converter as log_converter
    from pm4py.filtering import filter_case_size
    from pm4py.objects.log.obj import EventLog, Trace
    import pandas as pd

    print("reading in data...")
    data = pd.read_json(file_path, lines = True)

    df = []
    # select relevant columns in data
    df = data.loc[:, ['tweet_time', 'userid', 'retweet_tweetid']]

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

    cols = ['time:timestamp', 'concept:name', 'case:concept:name']
    df.columns = cols


    # convert df to log
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)


    trimmed_log = EventLog()

    for trace in log:
        if len(trace) > trim_length:
            trimmed_trace = Trace()
            trimmed_trace.attributes.update(trace.attributes)
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
    from load_config import load_config
    import os
    import argparse
    import pm4py

    config = load_config()

    parser = argparse.ArgumentParser(description="Run script on a dataset.")
    parser.add_argument("--dataset", type=str, required=True, choices=["uae-good-anonymized", "uae-bad-anonymized", "honduras-good-anonymized", "honduras-bad-anonymized"], help="Dataset filename (relative to project root)")
    args = parser.parse_args()

    # Construct dataset path
    dataset_path = os.path.join(config["project_root"], "data", args.dataset)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    if args.dataset == "honduras-bad-anonymized":
        output_path = os.path.join(config["project_root"], "data/honduras_coordinated.xes")
        log_length = 400
    elif args.dataset == "honduras-good-anonymized":
        output_path = os.path.join(config["project_root"], "data/honduras_uncoordinated.xes")
        log_length = 400
    elif args.dataset == "uae-bad-anonymized":
        output_path = os.path.join(config["project_root"], "data/uae_coordinated.xes")
        log_length = 300
    elif args.dataset == "uae-good-anonymized":
        output_path = os.path.join(config["project_root"], "data/uae_uncoordinated.xes")
        log_length = 300

    log = create_event_log(dataset_path, 10, log_length=log_length)

    pm4py.write_xes(log, output_path)
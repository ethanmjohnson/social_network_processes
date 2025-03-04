# this script takes creates an event log from the honduras coordinated dataset

def create_honduras_coord_event_log(data):

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

    # remove more than one instance per trace

    idx = df.groupby(['case:concept:name', 'concept:name'])['time:timestamp'].idxmin()
    earliest_events_df = df.loc[idx].reset_index(drop=True)
    earliest_events_df.sort_values(by = 'time:timestamp', ascending=True, inplace=True)

    length_df = earliest_events_df.groupby('case:concept:name').filter(lambda x: len(x) >= 2 and len(x) <= 10)

    log = log_converter.apply(length_df, variant=log_converter.Variants.TO_EVENT_LOG)

    # Get the frequency of each trace variant
    variants = case_statistics.get_variant_statistics(log)

    # Sort variants by frequency (descending)
    variants = sorted(variants, key=lambda x: x['count'], reverse=True)

    # Keep only the top x% most frequent variants
    num_variants_to_keep = int(0.5 * len(variants))
    admitted_variants = [var['variant'] for var in variants[:num_variants_to_keep]]

    # Apply the filter
    filtered_log = variants_filter.apply(log, admitted_variants)

    return filtered_log

def remove_single_occurrence_activities(log):
    # Convert the event log to a DataFrame
    df_log = pm4py.convert_to_dataframe(log)
    
    # Count the occurrences of each activity
    activity_counts = df_log['concept:name'].value_counts()

    # Filter the activities that occur more than once
    activities_to_keep = activity_counts[activity_counts > 1].index.tolist()

    # Filter the DataFrame to keep only the activities that occur more than once
    filtered_df = df_log[df_log['concept:name'].isin(activities_to_keep)]

    # Convert the filtered DataFrame back to an event log
    filtered_log = log_converter.apply(filtered_df, variant=log_converter.Variants.TO_EVENT_LOG)
    
    return filtered_log


if __name__ == "__main__":
    import pm4py
    import pandas as pd
    from pm4py.objects.conversion.log import converter as log_converter
    from pathlib import Path
    from pm4py.algo.filtering.log.variants import variants_filter
    from pm4py.statistics.traces.generic.log import case_statistics


    path = Path(__file__).parent.parent.parent / "data/external/honduras-bad-anonymized"

    data = pd.read_json(path, lines = True)

    log = create_honduras_coord_event_log(data)
    filtered_log = remove_single_occurrence_activities(log)

    pm4py.write_xes(filtered_log, Path(__file__).parent.parent.parent / "data/processed/honduras_coordinated_log.xes")






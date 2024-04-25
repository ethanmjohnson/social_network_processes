import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
import numpy as np
import pandas as pd
import datetime
import pm4py.objects.log.util.sorting as sorting
from preprocessing import combine_jsonl
from tqdm import tqdm
import os

# converts the series list to a data frame
def series_to_df(series):
    array = []
    for lst in series:
        for item in lst:
            array.append(item)
    
    return array

# Function to determine retweet_id
def determine_retweet_id(row):
    if row['action'] == 'retweeted':
        return row['og_user_id']
    else:
        return 'Not a retweet'
    
def determine_quote_id(row):
    if row['action'] == 'quoted':
        return row['og_user_id']
    else:
        return 'Not a quote'
    
def determine_reply_id(row):
    if row['action'] == 'reply':
        return row['og_user_id']
    else:
        return 'nan'
    

# finds tweet ids
def collect_tweet_ids(action_ids):
    elements_to_delete = ['Not a retweet', 'Not a quote', 'nan']
    all_id = []
    for id in action_ids:
        temp_id = df[id].unique()
        mask = np.isin(temp_id, elements_to_delete)
        temp_id = temp_id[~mask]
        all_id.append(temp_id)

    all_id = [item for sublist in all_id for item in sublist]
    all_id = np.unique(all_id)
    return all_id
    


# file paths to combine from info ops folder
file_paths = ['/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_1)_negative.jsonl', '/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_1)_positive.jsonl', '/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_2)_negative.jsonl', '/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_2)_positive.jsonl', '/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_3)_negative.jsonl', '/Users/ethanjohnson/Desktop/mphil-project/raw_data/twitter_info_ops/tweets/tweets_China_(July_2019_set_3)_positive.jsonl']
output_file_path = '/Users/ethanjohnson/Desktop/mphil-project/processed_data/combined_china.jsonl'

combine_jsonl(file_paths, output_file_path)

# read combined file in
df_json = pd.read_json(output_file_path, lines=True)

# gets a list of all required data from file
user_ids_lst = df_json['data'].apply(lambda x: [item.get('author_id') for item in x] if isinstance(x, list) else None)
timestamp_lst = df_json['data'].apply(lambda x: [item.get('created_at') for item in x] if isinstance(x, list) else None)
referenced_lst = df_json['data'].apply(lambda x: [item.get('referenced_tweets') for item in x] if isinstance(x, list) else None)

# removes none elements
user_ids_lst.dropna(inplace=True)
timestamp_lst.dropna(inplace=True)
referenced_lst.dropna(inplace=True)


# converts list to df
user_ids = series_to_df(user_ids_lst)
timestamp = series_to_df(timestamp_lst)
reference_id = series_to_df(referenced_lst)

# find when none in reference id index
index_none = [index for index, value in enumerate(reference_id) if value is None]

# remove these indices for all lists
filtered_user_id = [value for index, value in enumerate(user_ids) if index not in index_none]
filtered_timestamp = [value for index, value in enumerate(timestamp) if index not in index_none]
filtered_reference_id = [value for index, value in enumerate(reference_id) if index not in index_none]


# removes cases where multiple events occur at the same time stamp indicating multiple calls to same activity in log
sublist_count = -1
sublist_index = []
for sublist in filtered_reference_id:
    sublist_count+=1
    count = 0
    for item in sublist:
        count+=1
        if count > 1:
            sublist_index.append(sublist_count)

clean_user_id = [value for index, value in enumerate(filtered_user_id) if index not in sublist_index]
clean_timestamp = [value for index, value in enumerate(filtered_timestamp) if index not in sublist_index]
clean_reference_id = [value for index, value in enumerate(filtered_reference_id) if index not in sublist_index]


# extract tweet id and tweet action from reference list
og_tweet_id = [item['id'] for sublist in clean_reference_id for item in sublist]
tweet_action = [item['type'] for sublist in clean_reference_id for item in sublist]

# create a df from these
data = {'user_id' : clean_user_id, 'og_user_id' : og_tweet_id, 'timestamp' : clean_timestamp, 'action' : tweet_action}
df = pd.DataFrame(data)

# process timestamp to correct format
timestamps = df['timestamp']
new_timestamps = [datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ') for t in timestamps]
df['timestamp'] = new_timestamps

# process other columns to str
df['user_id'] = df['user_id'].astype('str')
df['og_user_id'] = df['og_user_id'].astype('str')


# Create new columns based on if rt, qt, or reply
df['retweet_id'] = df.apply(determine_retweet_id, axis=1)
df['quote_id'] = df.apply(determine_quote_id, axis=1)
df['reply_id'] = df.apply(determine_reply_id, axis=1)

df.drop('action', axis=1, inplace=True)
df.drop('og_user_id', axis=1, inplace=True)

# collect tweet ids from action list
action_ids = ['retweet_id', 'quote_id', 'reply_id']
all_id = collect_tweet_ids(action_ids)

# uses specific tweet id to get all actions related to tweet
actions = ['retweet', 'quote', 'reply']
post_log = EventLog()

for id in tqdm(all_id):
    trace = Trace()
    for action in actions:
        action_events = df.loc[df[action+'_id']==id]
        for i in range(len(action_events)):
            event = Event({'concept:name' : 'u' + action_events.iat[i,0] + '_' + action + 's', 'time:timestamp' : action_events.iat[i,1]})

            trace.insert(i, event)
    trace = sorting.sort_timestamp_trace(trace)
    post_log.append(trace)

# remove traces of len 1
post_log = pm4py.convert_to_event_log(post_log)
post_log = pm4py.filter_case_size(post_log, 2, 2**50)

# remove traces with events of same size
filtered_traces = []
for trace in post_log:
    timestamps = set(event['time:timestamp'] for event in trace)
    if len(timestamps) > 1:
        filtered_traces.append(trace)

filtered_log = EventLog()
for trace in filtered_traces:
    filtered_log.append(trace)

# write to save
pm4py.write_xes(filtered_log, os.getcwd() + '/processed_data/infoops_china.xes')
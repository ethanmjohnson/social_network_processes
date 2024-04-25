import pm4py
import os
from preprocessing import process_gov_data
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
import pandas as pd
from tqdm import tqdm

# this code takes a .csv file from the government dataset and converts the data to an event log using each unique post as the case id
def process_gov_data(file_path: str) -> EventLog:

    data = pd.read_csv(file_path)
    # code to convert the government dataset to an event log

    df = []

    # extract relevant columns
    df = data.loc[:, ['tweet_time', 'userid', 'retweet_tweetid']]

    # convert times to datetime format
    df['tweet_time'] = pd.to_datetime(df['tweet_time'])
    # remove problematic ID characters
    df['userid'] = df['userid'].str.replace('[+=]', '', regex=True)
    # convert tweet ID to int
    df['retweet_tweetid'] = df['retweet_tweetid'].astype('Int64')

    # format dataframe
    df.sort_values(by = 'tweet_time', ascending=True, inplace=True)
    df = df[df['retweet_tweetid'].isnull() == False]
    df = df[df['userid'].isnull() == False]


    df = df.loc[df.duplicated(subset='retweet_tweetid', keep=False), :]
    df.reset_index(drop=True, inplace = True)


    rt_id = df['retweet_tweetid'].unique()

    # construct event log using retweet_tweet_id as case ID
    log = EventLog()
    for id in tqdm(rt_id[0:2000]):
        trace = Trace()
        tweet = df[df['retweet_tweetid']==id]
        tweet = tweet.drop_duplicates(subset=['userid'], keep='first')
        for i in range(len(tweet)):
            event = Event({'concept:name' : 'u' + tweet.iat[i,1] + '_retweets', 'time:timestamp' : tweet.iat[i,0]})
            trace.insert(i, event)
        log.append(trace)

    # filter out traces of length 1
    eventlog = pm4py.convert_to_event_log(log)
    eventlog = pm4py.filter_case_size(eventlog, 2, 2**50)
    return eventlog


file_path = os.getcwd() + '/raw_data/government_data/Dec 2019/Saudi Arabia/saudi_arabia_112019_tweets_csv_hashed/saudi_arabia_112019_tweets_csv_hashed_9.csv'

eventlog = process_gov_data(file_path)

pm4py.write_xes(eventlog, os.getcwd() + '/processed_data/government_logs/saudi_log.xes')


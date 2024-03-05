import pandas as pd
from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py
import os

# this code takes a .csv file and converts the data to an event log using each unique post as the case id

def csv_to_eventlog(data):

    df = []

    df = data.loc[:, ['tweet_time', 'userid', 'retweet_tweetid']]

    print(len(df))

    df['tweet_time'] = pd.to_datetime(df['tweet_time'])



    df['retweet_tweetid'] = df['retweet_tweetid'].astype('Int64')

    df.sort_values(by = 'tweet_time', ascending=True, inplace=True)
    df = df[df['retweet_tweetid'].isnull() == False]
    df = df[df['userid'].isnull() == False]


    df = df.loc[df.duplicated(subset='retweet_tweetid', keep=False), :]
    df.reset_index(drop=True, inplace = True)


    rt_id = df['retweet_tweetid'].unique()



    log = EventLog()



    for id in rt_id:
        trace = Trace()
        tweet = df[df['retweet_tweetid']==id]
        tweet = tweet.drop_duplicates(subset=['userid'], keep='first')
        for i in range(len(tweet)):
            event = Event({'concept:name' : tweet.iat[i,1] + '-retweets', 'time:timestamp' : tweet.iat[i,0]})

            trace.insert(i, event)
        log.append(trace)


    eventlog = pm4py.convert_to_event_log(log)
    eventlog = pm4py.filter_case_size(eventlog, 2, 2**50)
    return eventlog

data = pd.read_csv('/Users/ethanjohnson/Desktop/mphil-project/raw_data/Apr 2020/Honduras/honduras_022020_tweets_csv_hashed.csv')

eventlog = csv_to_eventlog(data)
pm4py.write_xes(eventlog, '/Users/ethanjohnson/Desktop/mphil-project/processed_data/honduras_log.xes')

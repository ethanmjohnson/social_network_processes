import pandas as pd
from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from multiprocessing import Process

# converts the csv file to an event log


def getIndexes(dfObj, value):
     
    # Empty list
    listOfPos = []
     
    # isin() method will return a dataframe with
    # boolean values, True at the positions   
    # where element exists
    result = dfObj.isin([value])
     
    # any() method will return
    # a boolean series
    seriesObj = result.any()
 
    # Get list of column names where
    # element exists
    columnNames = list(seriesObj[seriesObj == True].index)
    
    # Iterate over the list of columns and
    # extract the row index where element exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
 
        for row in rows:
            listOfPos.append((row, col))
             
    # This list contains a list tuples with
    # the index of element in the dataframe
    return listOfPos



if __name__ == '__main__':
    # read in csv file
    data = pd.read_csv('/Users/ethanjohnson/Library/CloudStorage/Box-Box/MPhil/raw/anna_data/Apr 2020/Honduras/honduras_022020_tweets_csv_hashed.csv')



    df = []

    # select important colmns from csv
    df = data.loc[:, ['tweet_time', 'userid', 'retweet_tweetid']]

    df['tweet_time'] = pd.to_datetime(df['tweet_time'])



    df['retweet_tweetid'] = df['retweet_tweetid'].astype('Int64')

    df.sort_values(by = 'tweet_time', ascending=True, inplace=True)
    df = df[df['retweet_tweetid'].isnull() == False]
    df = df.loc[df.duplicated(subset='retweet_tweetid', keep=False), :]
    df.reset_index(drop=True, inplace = True)





    uniqueNames = df.drop_duplicates(subset= 'retweet_tweetid', keep = 'first')
    uniqueNames = uniqueNames.loc[:, ['retweet_tweetid']]



    uniqueNames = uniqueNames[uniqueNames['retweet_tweetid'].isnull() == False]
    uniqueNames.reset_index(drop=True, inplace=True)


    # 233977 - length of uniquenames

    log = EventLog()


    for j in range(100000):
        
        trace = Trace()
        i = 0
        ind = getIndexes(df, uniqueNames.at[j, 'retweet_tweetid'])
        for k in range(len(ind)):
            event = Event({'concept:name' : df.userid[ind[k][0]] + '-retweets', 'time:timestamp' : df.tweet_time[ind[k][0]]})
            trace.insert(i, event)
            i=i+1
        log.append(trace)


    eventlog = pm4py.convert_to_event_log(log)
    eventlog = pm4py.filter_case_size(eventlog, 2, 2**50)

    pm4py.write_xes(eventlog, '/Users/ethanjohnson/Library/CloudStorage/Box-Box/MPhil/data/hondurasData.xes')










#print('Visualising... \n')
#parameters = {pn_visualizer.Variants.PERFORMANCE.value.Parameters.FORMAT: "png"}
#gviz = pn_visualizer.apply(net, im, fm, parameters=parameters, variant=pn_visualizer.Variants.PERFORMANCE, log=eventlog)

#pn_visualizer.save(gviz, "/Users/ethanjohnson/Library/CloudStorage/Box-Box/MPhil/figs/inductive_times.png")



######

#simulate using log and petri net i already have
# collect metrics for current and simulated petri net e.g. mean firing time
# generate a histogram of these times




# interarrival time and total events in eventlog

# anna code gets transition times 

from analysis import load_log, calculate_interarrival_times, calculate_interarrival_times_folder
import numpy as np
import os
import matplotlib.pyplot as plt

# load relevant files and folders
china_log = load_log(os.getcwd() + '/processed_data/info_ops_logs/filtered_china_post_centric_difftimestamps.xes')
china_folder_path = os.getcwd() + '/processed_data/info_ops_logs_sim/china'
saudi_log = load_log(os.getcwd() + '/processed_data/government_logs/saudi_log_1048trace.xes')
saudi_folder_path = os.getcwd() + '/processed_data/government_logs_sim/saudi'


# calculate interarrival times
average_intertime_sim_china = calculate_interarrival_times_folder(china_folder_path)
average_intertime_china = np.sum(calculate_interarrival_times(china_log))/len(china_log)

average_intertime_sim_saudi = calculate_interarrival_times_folder(saudi_folder_path)
average_intertime_saudi = np.sum(calculate_interarrival_times(saudi_log))/len(saudi_log)

# plot
plt.hist(average_intertime_sim_china, bins = 30, color = 'skyblue', edgecolor = 'black', label = 'uncoordinated')
plt.axvline(x=average_intertime_china, color = 'darkblue')
plt.hist(average_intertime_sim_saudi, bins=30, color = 'lightgreen', edgecolor = 'black', label = 'coordinated')
plt.axvline(x=average_intertime_saudi, color = 'darkgreen')
plt.xlabel('average interarrival time')
plt.ylabel('frequency')
plt.title('the average interarrival times of simulated logs with the true interarrival time in red')
plt.legend()
plt.show()
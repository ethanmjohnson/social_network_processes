import pm4py
from free_choice_SPN import generate_F
from pm4py.objects.log.importer.xes import importer as xes_importer
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp


def calculate_mean_waiting_times(c_input_file, u_input_file):
    netc, initial_markingc, final_markingc = pm4py.read_pnml(c_input_file + ".pnml")
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    logc = xes_importer.apply(c_input_file + '.xes', variant=variant, parameters=parameters)

    netu, initial_markingu, final_markingu = pm4py.read_pnml(u_input_file + ".pnml")
    logu = xes_importer.apply(u_input_file + ".xes", variant=variant, parameters=parameters)

    Fc = generate_F(netc, logc)
    Fu = generate_F(netu, logu)


    mean_timesc = []
    mean_timesu = []

    for f in Fc:
        sum = 0
        cnt = 0
        for t in Fc[f]:
            sum+=t/1000
            cnt+=1
        if sum > 0:
            avg = sum/cnt
            mean_timesc.append(avg)
    mean_timesc = np.array(mean_timesc)

    for f in Fu:
        sum = 0
        cnt = 0
        for t in Fu[f]:
            sum+=t/1000
            cnt+=1
        if sum > 0:
            avg = sum/cnt
            mean_timesu.append(avg)

    mean_timesu = np.array(mean_timesu)

    return mean_timesc, mean_timesu



if __name__ == "__main__":
    from load_config import load_config
    import os
    import argparse

    config = load_config()

    parser = argparse.ArgumentParser(description="Run script for each country.")
    parser.add_argument("--country", type=str, required=True, choices = ["uae", "brazil", "honduras"], help="Country name (lowercase)")
    args = parser.parse_args()

    if args.country == "brazil":
        c_input_file = os.path.join(config['project_root'], "data", args.country + "_1")
        u_input_file = os.path.join(config['project_root'], "data", args.country + "_2")
    else:
        c_input_file = os.path.join(config['project_root'], "data", args.country + "_coordinated")
        u_input_file = os.path.join(config['project_root'], "data", args.country + "_uncoordinated")




    mean_timesc, mean_timesu = calculate_mean_waiting_times(c_input_file, u_input_file)

    num_bins1=round(max(mean_timesc)*6)
    num_bins2=round(max(mean_timesu)*6)
    # Create histogram bins


    # Plot histograms with transparency
    plt.figure(figsize=(8, 5))
    plt.hist(mean_timesc, bins=num_bins1, alpha=0.3, label='Coordinated behavior', color='blue',  edgecolor='black', density=True)
    plt.hist(mean_timesu, bins=num_bins2, alpha=0.3, label='Uncoordinated behavior', color='red',  edgecolor='black', density=True)

    # Labels and title
    plt.xlabel('Time in seconds')
    plt.ylabel('Density')
    plt.title('User waiting times in ' + args.country + ' model')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xlim(0, 15) 
    plt.ylim(0, 0.5) 

    # Show the plot
    plt.show()

    ks_statistic, p_value = ks_2samp(mean_timesc, mean_timesu)
    print(p_value)

    if args.country == "brazil":
        print("Average wait time in " + args.country + "_1:", np.mean(mean_timesc)*1000)
        print("Average wait time in " + args.country + "_2:", np.mean(mean_timesu)*1000)
    else:
        print("Average wait time in " + args.country + " coordinated:", np.mean(mean_timesc)*1000)
        print("Average wait time in " + args.country + " uncoordinated:", np.mean(mean_timesu)*1000)



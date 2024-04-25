# a module for use when preprocessing a variety of data sources used in this project

import json
import pandas as pd
import glob


def combine_jsonl(file_paths, output_path):
    # this function takes multiple jsonl file paths and combines them into a single jsonl file

    combined_files = []

    # Read data from each file and append it to the combined_data list
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            for line in file:
                combined_files.append(json.loads(line))

    # Write combined data to a new JSON Lines file
    with open(output_path, 'w') as output_file:
        for item in combined_files:
            output_file.write(json.dumps(item) + '\n')


def read_xlsx_folder(path):
    # this function reads a folder of .xlsx files and concatenates them into a single dataframe.
    all_files = glob.glob(path + "/*.xlsx")
    li = []
    for filename in all_files:
        df = pd.read_excel(filename, index_col=None, header=0)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)

    return df

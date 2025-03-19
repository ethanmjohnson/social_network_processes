# Processes in Social Networks: A Framework for Exploring Online User Behavior

This repository contains code for discovering and analyzing free-choice Stochastic Petri nets, as presented in our paper titled "Processes in Social Networks: A Framework for Exploring Online User Behavior".

## Table of Contents

-[Introduction](#introduction)\
-[Project Structure](#project-structure)\
-[Reproducibility](#reproducibility)\
-[Usage](#usage)

## Introduction

This repository provides the implementation and analysis of free-choice Stochastic Petri nets in exploring user behaviors online. It includes tools for:

- **Generating event logs from social network data**
- **Discovery of free-choice Stochastic Petri nets**
- **Analyzing structural measures of free-choice Stochastic Petri nets**

## Project Structure

The project is structured as follows:

```bash

social_network_processes/
│
├── data/                       # Folder containing the event logs and Petri net models discovered 
├── calculate_density.py     # The 'calculate' scripts contain functions for the case studies section
├── calculate_diameter.py
├── calculate_ks_entropy.py
├── calculate_mean_waiting_time.py 
├── config.json                 # Contains the path to the project root. Update this to reflect your current path
├── discover_petri_nets.py      # Used to discover the Petri nets from an event log
├── generate_logs_brazil.py     # Used to generate event logs from the Brazil dataset
├── generate_logs_uae_honduras.py       # Used to generate event logs from the UAE and Honduras datasets
├── free_choice_SPN.py     # Contains functions used to extend a Petri net to a free-choice Stochastic Petri net
│
├── requirements.txt            # List of required Python packages
└── README.md                   # Project description and instructions  

```


## Reproducibility

To obtain the results from our paper, follow these steps.

1. Navigate to the `config.json` file and update the project root entry with the path to the `social_network_processes` folder.
2. Download the UAE and Honduras datasets (https://zenodo.org/records/10650967) and Brazil datasets (https://zenodo.org/records/10669936), save these in the `social_network_processes/data` folder. 
3. Pass the UAE and Honduras datasets through `generate_logs_uae_honduras.py`. For UAE use `trim_length = 10` and `log_length = 300`. For Honduras use `trim_length = 10` and `log_length = 400` (these variables are already set depending on which dataset is passed).
4. Pass the Brazil dataset through `generate_logs_brazil.py`. Use `trim_length = 10` and `log_length = 200` (these variables are already set).
5. Use `discover_petri_nets.py` to discover Petri nets for each of the six event logs generated in steps 2 and 3.
6. Use `calculate_diameter.py` to calculate the diameter of the Petri nets.
7. Use `calculate_density.py` to calculate the density of the Petri nets.
8. Use `calculate_ks_entropy.py` to calculate the KS entropy.
9. Use `calculate_mean_waiting_time.py` to generate a plot comparing the mean waiting time for uncoordinated and coordinated datasets.


## Usage

The dependencies required for running the code in this repository can be installed using

```bash
pip install -r requirements.txt

```

Each script in this repository should be run from the terminal, passing in the required argument. For example, finding the designated arguments for running `calculate_diameter.py` can be found by running

```bash
python calculate_diamter.py --help

```

This shows that the required argument is a Petri net, so we can run the script using

```bash
python calculate_diameter.py --pn honduras_coordianted.pnml
```

Note the path to the Petri net is just the name of the file and not a complete path.
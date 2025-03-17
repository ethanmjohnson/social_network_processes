# Processes in Social Networks: A Framework for Exploring Online User Behavior

This repository contains code for discovering, analyzing and simulating free-choice Stochastic Petri nets, as presented in our paper titled "Processes in Social Networks: A Framework for Exploring Online User Behavior".

## Table of Contents

-[Introduction](#introduction)
-[Project Structure](#project-structure)
-[Reproducibility](#reproducibility)

## Introduction

This repository provides the implementation and analysis of free-choice Stochastic Petri nets in exploring user behaviors online. It includes tools for:

- **Generating event logs from social network data**
- **Discovering and simulation of free-choice Stochastic Petri nets**
- **Analyzing structural measures of free-choice Stochastic Petri nets**

## Project Structure

The project is structured as follows:

```bash

social_network_processes/
│
├── data/                       # Folder containing the event logs and Petri net models discovered 
├── case_studies_metrics.py     # Contains the functions used to complete the case studies section of the paper
├── discover_petri_nets.py      # Used to discover the Petri nets from an event log
├── generate_logs_brazil.py     # Used to generate event logs from the Brazil dataset
├── generate_logs_uae_honduras.py       # Used to generate event logs from the UAE and Honduras datasets
├── simulation_core.py      # Used to simulate traces of a free-choice Stochastic Petri net
├── simulation_utils.py     # Contains functions used in the simulation process
│
├── requirements.txt            # List of required Python packages
└── README.md                   # Project description and instructions  

```


## Reproducibility

To obtain the results from our paper, follow these steps.

1. Download the UAE and Honduras datasets (https://zenodo.org/records/10650967) and Brazil datasets (https://zenodo.org/records/10669936). 
2. Pass the UAE and Honduras datasets through `generate_logs_uae_honduras.py`. For UAE use `trim_length = 10` and `log_length = 300`. For Honduras use `trim_length = 10` and `log_length = 400`.
3. Pass the Brazil dataset through `generate_logs_brazil.py`. Use `trim_length = 10` and `log_length = 200`.
4. Use `discover_petri_nets.py` to discover Petri nets for each of the six event logs generated in steps 2 and 3.
5. Use the functions contained within `case_studies_metrics.py` to find the density and diameter of the Petri nets.
6. Use `simulation_core.py` to generate a free-choice Stochastic Petri net and to simulate traces from this.

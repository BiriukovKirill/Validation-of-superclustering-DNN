import argparse
import json
import os
import pandas as pd
import numpy as np

from validation.histFunctions import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input", "-i", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/csvFiles/csv_form_dumper.csv",
    help="Path to csv data file"
)

parser.add_argument(
    "--output", "-o", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/histograms",
    help="Path to directory to save histograms"
)

parser.add_argument(
    "--config", "-c", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/configs/config.json",
    help="JSON configuration file"
)

parser.add_argument(
    "--efficiency", "-e", default=[0.1, 0.2, 0.5, 0.8],
    help="Identify efficiency cuts in a form of a list"
)

args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)

df_ = pd.read_csv(args.input)

print(args.efficiency, type(args.efficiency), args.efficiency[0])

# If the df doesn't contain 'simToReco_score' column, it's impossible to make the efficiency plots
# Therefore, we just skip the step of transforming the efficiency str into list(float)
if "simToReco_score" not in df_.columns:
    args.efficiency = []

# transform efficiency into floats
if isinstance(args.efficiency, str) and ("simToReco_score" in df_.columns):
    if args.efficiency == "[]":
        args.efficiency = []
    else:
        args.efficiency = [float(num.strip()) for num in args.efficiency.split(',')]

efficiency_dfs = []
for ef in args.efficiency:
    print(ef)
    efficiency_dfs.append(df_[df_['simToReco_score'] < ef])
efficiency_dfs.append(df_)

args.efficiency.append(1)

with open(args.config, "r") as file:
    config = json.load(file)

for i, ef in enumerate(args.efficiency):
    df = efficiency_dfs[i]
    print(len(df))
    os.makedirs(f'{args.output}/efficiency_{efficiencyLabel(ef)}/efficiency', exist_ok=True)
    if len(args.efficiency) > 1:
        makeEfficiencyHist(df, efficiency_dfs[-1], f'{args.output}/efficiency_{efficiencyLabel(ef)}/efficiency')

    print(len(df))
    for data, data_dict in config.items():
        dir_path = f'{args.output}/efficiency_{efficiencyLabel(ef)}/{data}'
        os.makedirs(dir_path, exist_ok=True)
        data_bins = data_dict['data_bins']
        data_opt = data_dict['data_opt']
        data_edges = makeEdges(df, data, data_bins, data_opt)

        for var, bins, opt in zip(data_dict['binning_columns'], data_dict['binning_bins'], data_dict['binning_opt']):
            postfix = ''
            hd_ld_opt = None
            df_orig = None
            if var == 'hd':
                df_orig = df
                var = 'sim_raw_energy'
                df = df[df['sim_barycenter_eta'] > 2.15]
                postfix='_hd'
                hd_ld_opt = 'hd'
            if var == 'ld':
                df_orig = df
                var = 'sim_raw_energy'
                df = df[df['sim_barycenter_eta'] < 2.15]
                postfix = '_ld'
                hd_ld_opt = 'ld'
            
            y_edges = makeEdges(df, var, bins, opt, primary_var=False)

            if data == 'n_scls_per_event':
                if df_orig is None:
                    df_orig = df
                df = df.drop_duplicates(subset=['file', 'event'])
            if data == 'n_scls_per_cp':
                if df_orig is None:
                    df_orig = df
                df = df.drop_duplicates(subset=['file', 'recoToSim_id', 'event'])

            hist, x_edges, y_edges = np.histogram2d(df[data], df[var], [data_edges, y_edges])
            np.savez(f'{args.output}/efficiency_{efficiencyLabel(ef)}/{data}/{var}{postfix}.npz', hist = hist, x_edges = x_edges, y_edges = y_edges)
            
            if df_orig is not None:
                df = df_orig
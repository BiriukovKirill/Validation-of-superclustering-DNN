import argparse
import os
import numpy as np
import json

from validation.plotFunctions import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input", "-i", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/histograms",
    help="A directory with .npz histograms"
)

parser.add_argument(
    "--output", "-o", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/plots",
    help="The folder where to save the plots"
)

parser.add_argument(
    "--config", "-c", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/configs/config.json",
    help="JSON configuration file"
)

parser.add_argument(
    "-pu", default=0,
    help="Value of the pile-up. It's required to put the corresponding value on a canvas"
)

args = parser.parse_args()

with open(args.config, "r") as file:
    config = json.load(file)

for root, dirs, files in os.walk(args.input):

    rel_path = os.path.relpath(root, args.input)
    target_path = os.path.join(args.output, rel_path)

    os.makedirs(target_path, exist_ok=True)
    for file in files:
        hd_ld_opt = None

        src_file = os.path.join(root, file)

        data = src_file.split('/')[-2]
        binning_var = src_file.split('/')[-1].split('.')[0]
        if binning_var.split('_')[-1] == 'hd':
            binning_var = binning_var[:-3]
            hd_ld_opt = 'hd'
        if binning_var.split('_')[-1] == 'ld':
            binning_var = binning_var[:-3]
            hd_ld_opt = 'ld'

        loaded_hist = np.load(src_file)
        
        if data == 'efficiency':
            threshold = src_file.split('/')[-3].split('_')[-1]
            dest_file = os.path.join(target_path, f'{binning_var}_{threshold}.png')
            plotEfficiency(loaded_hist, binning_var, threshold, hd_ld_opt, args.pu, dest_file)
        else:
            #find required attributes in config
            data_dict = config[data]
            var_index = data_dict['binning_columns'].index(binning_var)
            plot_opt = data_dict['plot'][var_index]

            if plot_opt == "unroll":
                dest_file_name = binning_var
                if hd_ld_opt is not None:
                    dest_file_name = dest_file_name + '_' + hd_ld_opt
                dest_file = os.path.join(target_path, f'{dest_file_name}.png')
                makeUnroll(loaded_hist, data, binning_var, hd_ld_opt, args.pu, dest_file)

            if plot_opt == "2d":
                dest_file_name = binning_var
                if hd_ld_opt is not None:
                    dest_file_name = dest_file_name + '_' + hd_ld_opt
                dest_file = os.path.join(target_path, f'{dest_file_name}.png')
                make2D(loaded_hist, data, binning_var, hd_ld_opt, args.pu, dest_file)
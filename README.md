# Validation-of-superclustering-DNN

This is a validation software required to produce a set of validation plots for superclusters produced by a superclustering DNN within TICL framework. One can produce plots for various constraints sim-to-reco association scores. The following plots are available (tested):

- No association:
  - Number of superclusters per event;
  - Energy, transverse momentum, angular distributions of superclusters;
- Associated with sim-to-reco scores:
  - Number of superclusters associated to a given caloparticle within an event;
  - Number of tracksters within a supercluster;
  - Energy, transverse momentum, angular distibutions of superclusters;
  - Energy ratio distributions (reconstructed to corresponding CP energy or regressed reconstructed to corresponding generated energy);
  - Angular response;
  - sim-to-reco score vs reco-to-sim score;
- Efficiency plots for a given sim-to-reco score threshold

## Workflow

We start from TICL dumper files produced within a CMSSW framework (only 15 version works for now). The workflow consists of 3 consecutive steps:

1. Production of flat NTuples.
    At this stage one produces flat NTuples with all required data for histogram building from the TICL dumper files.
2. Making histograms.
    Histograms are made using the flat NTuples produced at the stage 1.
3. Plotting histograms.

## Configuration file

In order to specify what kind of plots must be produced, one has to make a configuration file. This is a json file which contains all information about binning and extra variables a given one has to be binned in. The structure of the file is the following:

{
    "var_1":{
        "data_bins": 10,
        "data_opt": "lin",
        "binning_columns": ["binning_var_1", "binning_var_2"],
        "binning_bins": [5, 5],
        "binning_opt": ["lin", "log"],
        "plot": ["unroll", "2d"]
    }
}

The variable "var_1" is a variable one wants to make a plot of. One has to specify the number of bins for ("data_bins") and the binning option (can be "lin" or "log" representing the linear and the logarithmic scale respectively). "binning_columns" represents a list of variables the first one must be binned in. For each of binning variables one has to specify the number of bins ("binning_bins") and the scale option ("binning_opt") as well as the type of plot one wants to produce ("plot"). For now, there are 2 available plot types present: "unroll" and "2d". "unroll" represents plotting 1D distribution of an initial variable for each bin of a binning variable on a single canvas. "2d" is simply a 2d distribution of an initial variable together with a binning one.

### How can I plot a combined distribution?

A reader may have noticed there is no option to plot a combined distribution. Yet there is a way to do it. One simply has to specify the number of "binning_bins" to be 1 for a "binning_columns" of their own choice and the "plot" to be "unroll". Note that the value for "binning_columns" does not really matter as the is a single bin.

## Running the code

Before one runs the workflow one has to `source bash/set_pythonpath.sh`. The scripts add the python directory into a `PYTHONPATH` environmental variable. It is required in order to successfully import the custom validation modules stored in `python/validation`.

For each stage described in the "workflow" section there is a corresponding python script stored in `python/scripts` and a python module containing all the required functions sroted in `python/validation`.

### NTupler

In order to produce the NTuples one has to run `python3 python/scripts/makeSclsDataFrame.py -i "input_directory_with_TICL_dumper_files" -o "output_file_path" -s "score_option" -nf "max_number_of_files"`. Available options for scores are: best_associated, best_shared_e or no (if no association required). The script saved the NTupler as a csv file.

### Histogrammer

Run `python3 python/scripts/makeHists.py -i "csv_file_path" -o "output_directory_for_histograms" -c "path_to_json_config_file" -e "sim-to-reco_thresholds_comma_separated"`. The output is a directory with .npz files containing numpy histograms with edges.

### Plotter

Run `python3 python/scripts/makePlots.py -i "directory_with_numpy_histograms" -o "directory_with_plots" -c "path_to_json_config_file" -pu "value_of_pile-up"`
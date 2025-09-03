import pandas as pd
import numpy as np

def getBinningFactor(df_array):
    low_q = df_array.quantile(0.01)
    high_q = df_array.quantile(0.99)
    core_range = high_q - low_q

    min_val = np.min(df_array)
    max_val = np.max(df_array)
    full_range = max_val - min_val

    if core_range < 0.:
        raise ValueError('High quantile is lower then low quantile')

    return np.round(core_range/full_range, decimals=0)

def getCI(efficiency, n_events, ci_opt: str):
    from statsmodels.stats.proportion import proportion_confint

    ci_low, ci_high = proportion_confint(np.array(efficiency)*np.array(n_events), n_events, alpha = 0.32, method=ci_opt)

    #ci_high = np.minimum(ci_high, 1.)
    
    ci = []
    ci.append(efficiency - ci_low)
    ci.append(ci_high - efficiency)

    return np.array(ci)

def efficiencyLabel(efficiency):
    ef = str(efficiency)
    try:
        return '_'.join(ef.split('.'))
    except:
        return ef
    
def makeEdges(df, var, nbins, opt, dynamic=False, primary_var=True):
    array = df[var]

    if dynamic:
        binning_factor = getBinningFactor(array)
        nbins = int(nbins*binning_factor)
    
    rebin_vars = {'nTracksters', 'n_scls_per_event', 'n_scls_per_cp', "n_tr_per_scls"}

    min_val = np.min(array)
    max_val = np.max(array)
    if (var in rebin_vars) and primary_var:
        nbins = int(max_val - min_val + 1)
    if opt == 'lin':
        return np.linspace(min_val, max_val, nbins + 1)
    if opt == 'log':
        min_val = {True: min_val, False: 10}[min_val > 10]
        return np.logspace(np.log10(min_val), np.log10(max_val), nbins + 1)
    else:
        raise KeyError('opt value must be either lin or log')

def makeEfficiencyHist(df, df_full, where_to_save):
    binning_vars = ['sim_barycenter_eta', 'sim_barycenter_phi', 'sim_raw_energy', 'hd', 'ld']
    binning_bins = [10, 10, 8, 8, 8]
    binning_opts = ['lin', 'lin', 'log', 'log', 'log']

    for var, bins, opt in zip(binning_vars, binning_bins, binning_opts):
        postfix = ''
        if var == 'hd':
            df_orig = df
            df_full_orig = df_full
            var = 'sim_raw_energy'
            df = df[df['sim_barycenter_eta'] > 2.15]
            df_full = df_full[df_full['sim_barycenter_eta'] > 2.15]
            postfix = '_hd'
        if var == 'ld':
            df_orig = df
            df_full_orig = df_full
            var = 'sim_raw_energy'
            df = df[df['sim_barycenter_eta'] < 2.15]
            df_full = df_full[df_full['sim_barycenter_eta'] < 2.15]
            postfix = '_ld'
        
        edges = makeEdges(df, var, bins, opt, primary_var = False)
        efficiency_per_var = []
        nevents_per_var = []
        for ef_bin in range(len(edges) - 1):
            min_bin = edges[ef_bin]
            max_bin = edges[ef_bin + 1]

            df_ef_per_bin = df[(df[var] > min_bin) & (df[var] < max_bin)]
            df_per_bin = df_full[(df_full[var] > min_bin) & (df_full[var] < max_bin)]

            #ef_counts = df_ef_per_bin.groupby('file').size().reset_index(name='count')['count']
            #full_counts = df_per_bin.groupby('file').size().reset_index(name='count')['count']

            #ratio_per_file = ef_counts/full_counts
            ratio_per_file = len(df_ef_per_bin)/len(df_per_bin)
            if ratio_per_file > 1.:
                print(len(df_ef_per_bin), len(df_per_bin))
                    
            efficiency_per_var.append(ratio_per_file)
            nevents_per_var.append(len(df_per_bin))
        efficiency_per_var = np.array(efficiency_per_var)
        nevents_per_var = np.array(nevents_per_var)

        np.savez(f'{where_to_save}/{var}{postfix}.npz', hist=efficiency_per_var, edges=edges, ci = getCI(efficiency_per_var, nevents_per_var, 'beta'))
        try:
            df = df_orig
            df_full = df_full_orig
        except:
            pass

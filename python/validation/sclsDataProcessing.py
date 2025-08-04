import pandas as pd
import uproot as ur
import awkward as ak
import numpy as np
from typing import List, Dict
import warnings

def testLen(array):
    return len(ak.flatten(array, axis=None))

def fillSeries(df, input_array, name):
    if input_array.ndim != 1:
        input_array = ak.flatten(input_array, axis=None)

    series = pd.Series(np.array(input_array), name=name)
    df[series.name] = series

def fillNan(array):
    return ak.fill_none(ak.pad_none(array, 1, axis=-1), np.nan, axis=-1)

def bestS2RScore(df, root_file):
    s2r_id = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP'].array()
    s2r_s = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP_score'].array()
    s2r_sorting_map = ak.argsort(s2r_s, ascending=True)

    s2r_id = s2r_id[s2r_sorting_map]
    s2r_s = s2r_s[s2r_sorting_map]

    fillSeries(df, fillNan(s2r_id[...,:1]), 'simToReco_id')
    fillSeries(df, fillNan(s2r_s[...,:1]), 'simToReco_score')

    return s2r_id[...,:1], s2r_id[...,1:2]

def bestS2RSharedE(df, root_file):
    s2r_id = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP'].array()
    s2r_e = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP_sharedE'].array()
    s2r_s = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP_score'].array()
    s2r_sorting_map = ak.argsort(s2r_e, ascending=False)

    s2r_id = s2r_id[s2r_sorting_map]
    s2r_s = s2r_s[s2r_sorting_map]

    fillSeries(df, fillNan(s2r_id[...,:1]), 'simToReco_id')
    fillSeries(df, fillNan(s2r_s[...,:1]), 'simToReco_score')

    return s2r_id[...,:1], s2r_id[...,1:2]

def associatedS2R(df, root_file, threshold=0.99):
    s2r_id = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP'].array()
    s2r_s = root_file['ticlDumper/associations/ticlTracksterLinksSuperclusteringDNN_simToReco_CP_score'].array()
    s2r_map = s2r_s < threshold

    s2r_id = s2r_id[s2r_map]
    s2r_s = s2r_s[s2r_map]

    fillSeries(df, fillNan(s2r_id), 'simToReco_id')
    fillSeries(df, fillNan(s2r_s), 'simToReco_score')

    return s2r_id

def fillEventNumber(df, root_file, score):
    if score is None:
        raw_energy = root_file['ticlDumper/ticlTracksterLinksSuperclusteringDNN/raw_energy'].array()
        n_event = ak.Array(np.linspace(1, len(raw_energy), len(raw_energy)))
        n_event = ak.broadcast_arrays(n_event, raw_energy)[0]
    else:
        n_event = ak.Array(np.linspace(1, len(score), len(score)))
        n_event = ak.broadcast_arrays(n_event, fillNan(score))[0]

    fillSeries(df, n_event, 'event')
    print(testLen(n_event))

def fillNSclsPerEvent(df, root_file):
    raw_energy = root_file['ticlDumper/ticlTracksterLinksSuperclusteringDNN/raw_energy'].array()

    n_scls_per_event = ak.num(raw_energy, axis=-1)
    n_scls_broadcasted = ak.broadcast_arrays(n_scls_per_event[:,None], raw_energy)[0]
    n_scls_broadcasted = n_scls_broadcasted[n_scls_broadcasted > 0]

    fillSeries(df, n_scls_broadcasted, 'n_scls_per_event')
    print(testLen(n_scls_broadcasted))

def fillNSclsPerCP(df, root_file, scores):
    raw_energy = root_file['ticlDumper/ticlTracksterLinksSuperclusteringDNN/raw_energy'].array()
    cp_energy = root_file['ticlDumper/simtrackstersCP/raw_energy'].array()

    br_raw_energy = ak.broadcast_arrays(raw_energy[:,None], cp_energy)[0][scores]

    n_scls_per_cp = ak.num(br_raw_energy, axis=-1)

    fillSeries(df, n_scls_per_cp, 'n_scls_per_cp')
    print(testLen(n_scls_per_cp))

def fillNTrPerScls(df, root_file, scores):
    tr_in_scls = root_file['ticlDumper/superclustering/linkedResultTracksters'].array()
    n_tr_in_scls = ak.num(tr_in_scls, axis=2)

    cp_energy = root_file['ticlDumper/simtrackstersCP/raw_energy'].array()
    n_tr_in_scls = ak.broadcast_arrays(n_tr_in_scls[:,None], cp_energy)[0]

    n_tr_in_scls = n_tr_in_scls[scores]
    n_tr_in_scls = fillNan(n_tr_in_scls)

    fillSeries(df, n_tr_in_scls, 'n_tr_per_scls')
    print(testLen(n_tr_in_scls))

def fillSclsRecoArrays(df, root_file, scores):
    reco_branch = 'ticlDumper/ticlTracksterLinksSuperclusteringDNN'

    columns = ['raw_energy', 'regressed_energy', 'raw_pt', 'barycenter_eta', 'barycenter_phi', 'barycenter_x', 'barycenter_y', 'barycenter_z']

    arrays = []
    for col in columns:
        arrays.append(root_file[reco_branch][col].array())
    
    if scores is not None:
        cp_energy = root_file['ticlDumper/simtrackstersCP/raw_energy'].array()

        for i, array in enumerate(arrays):
            arrays[i] = ak.broadcast_arrays(array[:,None], cp_energy)[0][scores]
            arrays[i] = fillNan(arrays[i])

    for col, array in zip(columns, arrays):
        if 'eta' in col:
            array = np.abs(array)
        fillSeries(df, array, f'reco_{col}')
        print(testLen(array))

def fillSclsSimArrays(df, root_file, scores):
    sim_branch = 'ticlDumper/simtrackstersCP'

    columns = ['raw_energy', 'regressed_energy', 'barycenter_eta', 'barycenter_phi', 'barycenter_x', 'barycenter_y', 'barycenter_z']

    arrays = []
    for col in columns:
        arrays.append(root_file[sim_branch][col].array())

    if scores is not None:
        reco_energy = root_file['ticlDumper/ticlTracksterLinksSuperclusteringDNN/raw_energy'].array()

        for i, array in enumerate(arrays):
            arrays[i] = ak.broadcast_arrays(reco_energy[:,None], array)[1][scores]
            arrays[i] = fillNan(arrays[i])

    for col, array in zip(columns, arrays):
        if 'eta' in col:
            array = np.abs(array)
        fillSeries(df, array, f'sim_{col}')
        print(testLen(array))

def fillR2S(df, root_file, scores):
    associations = root_file['ticlDumper/associations']

    r2s_id = associations['ticlTracksterLinksSuperclusteringDNN_recoToSim_CP'].array()
    r2s_score = associations['ticlTracksterLinksSuperclusteringDNN_recoToSim_CP_score'].array()

    matched_r2s_s = []
    matched_r2s_id = []
    for event_id, event in enumerate(scores):
        r2s_s_per_event = []
        r2s_id_per_event = []
        for sim_id, sim in enumerate(event):
            r2s_s_per_sim = []
            r2s_id_per_sim = []
            for reco_id in sim:
                sim_id_in_reco_id_array = np.where(r2s_id[event_id][reco_id] == sim_id)[0][0]
                r2s_s_per_sim.append(r2s_score[event_id][reco_id][sim_id_in_reco_id_array])
                r2s_id_per_sim.append(sim_id)
            r2s_s_per_event.append(r2s_s_per_sim)
            r2s_id_per_event.append(r2s_id_per_sim)
        matched_r2s_s.append(r2s_s_per_event)
        matched_r2s_id.append(r2s_id_per_event)

    matched_r2s_s = ak.Array(matched_r2s_s)
    matched_r2s_id = ak.Array(matched_r2s_id)

    matched_r2s_s = fillNan(matched_r2s_s)
    matched_r2s_id = fillNan(matched_r2s_id)

    fillSeries(df, matched_r2s_s, 'recoToSim_score')
    fillSeries(df, matched_r2s_id, 'recoToSim_id')
    print(testLen(matched_r2s_id))
    print(testLen(matched_r2s_s))

def computeBaryResponse(df):
    vars = ['barycenter_eta', 'barycenter_phi', 'barycenter_x', 'barycenter_y', 'barycenter_z']
    response_vars = [f'sim_{var}' for var in vars] + [f'reco_{var}' for var in vars]
    
    if any(var not in df.columns for var in response_vars):
        warnings.warn(f"Not all the variables from the following list are in the dataframe: {response_vars}")
    
    for var in response_vars:
        if ('sim_' in var) and (('reco_' + var.split('_',1)[-1]) not in df.columns):
            raise Exception(f"No reco pair for {var} in the dataframe")
        if ('reco_' in var) and (('sim_' + var.split('_',1)[-1]) not in df.columns):
            raise Exception(f"No sim pair for {var} in the dataframe")

    for var in response_vars:
        if var not in df.columns:
            response_vars.remove(var)
    
    for var in response_vars:
        if 'sim_' in var:
            delta_var = df['reco_' + var.split('_',1)[-1]] - df[var]
            label = 'delta_' + var.split('_',1)[-1]
            fillSeries(df, delta_var, label)

def computeResponse(df):
    vars = ['raw_energy', 'regressed_energy']
    response_vars = [f'sim_{var}' for var in vars] + [f'reco_{var}' for var in vars]

    if any(var not in df.columns for var in response_vars):
        warnings.warn(f"Not all the variables from the following list are in the dataframe: {response_vars}")

    for var in response_vars:
        if ('sim_' in var) and (('reco_' + var.split('_',1)[-1]) not in df.columns):
            raise Exception(f"No reco pair for {var} in the dataframe")
        if ('reco_' in var) and (('sim_' + var.split('_', 1)[-1]) not in df.columns):
            raise Exception(f"No sim pair for {var} in the dataframe")
        
    for var in response_vars:
        if var not in df.columns:
            response_vars.remove(var)

    for var in response_vars:
        if 'sim_' in var:
            response_var = df['reco_' + var.split('_', 1)[-1]]/df[var]
            label = var.split('_',1)[-1] + '_ratio'
            fillSeries(df, response_var, label)


    

    






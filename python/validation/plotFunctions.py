import sys
sys.path.append("/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/python")

from new_validation.fitting import cruijff, resolutionFunc

import numpy as np
import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
mpl.rcParams['figure.dpi'] = 300
import mplhep as hep
plt.style.use(hep.style.CMS)

var_labels = {
    'raw_energy_ratio': r'$\frac{E_\text{reco}^{raw}}{E_\text{gen}}$',
    'regressed_energy_ratio': r'$\frac{E_\text{reco}^{regressed}}{E_\text{gen}}$',
    'sim_raw_energy': r'$E_\text{gen}$ (GeV)',
    'reco_raw_energy': r'$E_\text{reco}^\text{raw}$',
    'reco_regressed_energy': r'$E_\text{reco}^\text{regressed}$',
    'reco_raw_pt': r'$(p_T)_\text{reco}^\text{raw}$',
    'ld': r'LD (1.6 < $\eta$ < 2.15)',
    'hd': r'HD (2.15 < $\eta$ < 2.9)',
    'nTracksters': '# tracksters',
    'nLC': '# LC in trackster',
    'n_scls_per_cp': '# scls associated to CP',
    'n_scls_per_event': '# scls per event',
    'n_tr_per_scls': '# tracksters in supercluster',
    'delta_theta_pca': r'$\Delta \Theta^\text{PCA}$',
    'em_probability': 'Pr(EM)',
    'simToReco_score': 'score sim-to-reco',
    'recoToSim_score': 'score reco-to-sim',
    'sim_barycenter_eta': r'$\eta_\text{gen}$',
    'sim_barycenter_phi': r'$\phi_\text{gen}$',
    'reco_barycenter_eta': r'$\eta_\text{reco}$',
    'reco_barycenter_phi': r'$\phi_\text{reco}$',
    'delta_barycenter_eta': r'$\Delta \eta$',
    'delta_barycenter_phi': r'$\Delta \phi$',
    'ev_ratio': r'$\frac{EV1}{EV1 + EV2 + EV3}$',
    'simToReco_sharedE': r'$E_{shared}^{sim-to-reco}$ (GeV)',
    'recoToSim_sharedE': r'$E_{shared}^{reco-to-sim}$ (GeV)',
    'simToReco_sharedE_to_sim_raw_energy': r'$\frac{E_{shared}^{sim-to-reco}}{E_{gen}}$',
    'recoToSim_sharedE_to_reco_raw_energy': r'$\frac{E_{shared}^{reco-to-sim}}{E_{reco}^{raw}}$',
    'simToReco_sharedE_second_best_to_sim_raw_energy': r'$\frac{E_{shared}^\text{sim-to-reco second best}}{E_{gen}}$'
}

def NormHist(hist):
    nevents = np.sum(hist, axis=1)
    weights = np.max(nevents)/nevents
    return hist*weights[:, np.newaxis]

def makeIndPlots(data, fit_data, data_var, binning_var, hd_ld_opt, pu, path_to_save):
    hist = data['hist'].T
    x_edges = data['x_edges']
    y_edges = data['y_edges']

    fit_opt_params = fit_data['func_params']

    for i in range(len(hist)):
        fig, ax = plt.subplots()

        #hist_bins = hists[1]
        bin_centers = (x_edges[1:] + x_edges[:-1])/2
        half_bin_widths = (x_edges[1:] - x_edges[:-1])/2
        #bin_centers_ext = np.concatenate([[hist_bins[0] - half_bin_widths[0]], bin_centers ,[hist_bins[-1] + half_bin_widths[-1]]])
        #errors = np.sqrt(hists[0][i])
        #errors_lower = np.concatenate([[hists[0][i][0]], hists[0][i] - errors ,[hists[0][i][-1]]])
        #errors_upper = np.concatenate([[hists[0][i][0]], hists[0][i] + errors ,[hists[0][i][-1]]])
        #ax.fill_between(bin_centers_ext, errors_lower, errors_upper, step='mid', alpha=0.2, color='grey')
        x_fit = np.linspace(x_edges[0], x_edges[-1], 150)
        y_fit = cruijff(x_fit, *fit_opt_params[i])
        x_fit = x_fit[y_fit < 10**6]
        y_fit = y_fit[y_fit < 10**6]

        min_e = y_edges[i]
        max_e = y_edges[i + 1]
        binning_var_label = var_labels[binning_var]
        hist_label = rf'{min_e:.2f} < {binning_var_label} < {max_e:.2f}'
        if hd_ld_opt != '':
            hist_label = hist_label + '\n' + var_labels[hd_ld_opt]
        
        bins_for_step = np.repeat(x_edges, 2)
        hist_for_step = np.concatenate([[0], np.repeat(hist[i], 2), [0]])
        ax.step(bins_for_step, hist_for_step, label=hist_label, where='post', linewidth = 2)
        ax.plot(x_fit, y_fit, linewidth = 2)
        ax.set_xlabel(var_labels[data_var])
        ax.set_ylabel('Events')
        ax.legend()
        hep.cms.text("Preliminary", exp="TICLv5", ax=ax)
        hep.cms.lumitext(f"PU={pu}", ax=ax)

        fig.tight_layout()
        fig.savefig(os.path.join(path_to_save, f'{binning_var}_{min_e:.1f}_{max_e:.1f}.png'))
        plt.close()

def makeUnroll(data, data_var, binning_var, hd_ld_opt, pu, path_to_save):
    hist = data['hist'].T
    x_edges = data['x_edges']
    y_edges = data['y_edges']

    hist = NormHist(hist)
    fig, ax = plt.subplots()
    for i in range(len(hist)):
        min_e = y_edges[i]
        max_e = y_edges[i + 1]
        binning_var_label = var_labels[binning_var]
        hist_label = rf'{min_e:.2f} < {binning_var_label} < {max_e:.2f}'

        x_label = var_labels[data_var]
        if hd_ld_opt != '':
            x_label = x_label + '\n' + var_labels[hd_ld_opt]


        bins_for_step = np.repeat(x_edges, 2)
        hist_for_step = np.concatenate([[0], np.repeat(hist[i], 2), [0]])
        ax.step(bins_for_step, hist_for_step, label=hist_label, where='post', linewidth = 2)
        ax.set_xlabel(x_label)
        ax.set_ybound(0)
        ax.set_ylabel('Events')

        if 'energy_ratio' in data_var:
            ax.axvline(1.0, linestyle='--', c='black')

        if data_var == 'nTracksters':
            ax.set_xticks((x_edges[1:] + x_edges[:-1])/2)
            ax.set_xticklabels(range(int(x_edges[0]), int(x_edges[-1]) + 1))

        ax.legend()
        hep.cms.text("Preliminary", exp="TICLv5", ax=ax)
        hep.cms.lumitext(f"PU={pu}", ax=ax)
        
        fig.tight_layout()
        fig.savefig(path_to_save)
        plt.close()

def make2D(data, data_var, binning_var, hd_ld_opt, pu, path_to_save):
    hist = data['hist'].T
    x_edges = data['x_edges']
    y_edges = data['y_edges']

    #x_centers = (x_edges[1:] + x_edges[:-1])/2
    #y_centers = (y_edges[1:] + y_edges[:-1])/2

    x_widths = np.round((x_edges[1:] - x_edges[:-1])/2, decimals = 4)
    y_widths = np.round((y_edges[1:] - y_edges[:-1])/2, decimals = 4)

    fig, ax = plt.subplots()
    h = ax.pcolormesh(x_edges, y_edges, hist, shading='flat', cmap='viridis', norm=mcolors.LogNorm(vmin=1, vmax=hist.max()))
    plt.colorbar(h, ax= ax, label='Events')
    ax.set_xlabel(var_labels[data_var])
    ax.set_ylabel(var_labels[binning_var])
    if ~np.all(x_widths == x_widths[0]):
        ax.set_xscale('log')
    if ~np.all(y_widths == y_widths[0]):
        ax.set_yscale('log')

    hep.cms.text("Preliminary", exp="TICLv5", ax=ax)
    hep.cms.lumitext(f"PU={pu}", ax=ax)

    fig.tight_layout()
    fig.savefig(path_to_save)
    plt.close()

def plotEfficiency(data, binning_var, threshold, hd_ld_opt, pu, path_to_save):
    hist = data['hist']
    x_edges = data['edges']

    fig, ax = plt.subplots()

    x_label = var_labels[binning_var]
    if hd_ld_opt != '':
        x_label = x_label + '\n' + var_labels[hd_ld_opt]
    
    bin_centers = (x_edges[1:] + x_edges[:-1])/2
    bin_widths = (x_edges[1:] - x_edges[:-1])/2
    ax.axhline(y=1., linestyle='--', linewidth=2)
    ax.errorbar(bin_centers, hist, yerr=data['ci'],  xerr=bin_widths, marker='s', ms=3)
    ax.set_xlabel(x_label)
    ax.set_ybound(0,1.1)
    if threshold == '1':
        ax.set_ylabel(f'Efficiency (threshold = {threshold})')
    else:
        ax.set_ylabel(f'Efficiency (threshold = 0.{threshold})')
    hep.cms.text("Preliminary", exp="TICLv5", ax=ax)
    hep.cms.lumitext(f"PU={pu}", ax=ax)

    fig.tight_layout()
    fig.savefig(path_to_save)
    plt.close()
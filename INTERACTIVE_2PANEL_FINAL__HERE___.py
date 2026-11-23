#import necessary packages
import pandas as pd
import numpy as np
import matplotlib
#creates a popup window for interactivity
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, NullFormatter

#load data
df = pd.read_csv('category_data_final.csv')

#filter for SN-associated objects (No Kilonova) for the Nickel plot
df_SN = df[df['KN'] == 'no'].copy()

#ensure nickel mass is numeric and filter valid entries for top panel -- code breaks otherwise
df_SN_valid = df_SN.copy()
df_SN_valid['nickel mass'] = pd.to_numeric(df_SN_valid['nickel mass'], errors='coerce')
df_SN_valid = df_SN_valid[df_SN_valid['nickel mass'].notna()]

#ensure luminosity is numeric for the bottom panel too 
df['L_1998'] = pd.to_numeric(df['L_1998'], errors='coerce')

#create colour maps for markers 
facecolour_map = {'gold': 'gold', 'silver': 'silver', 'bronze': 'brown'}
edgecolour_map = {
    'Collapsar': 'red', 'S-Merger': 'blue', 'L-Merger': 'green', 
    'L-Weak': 'orange', 'S-Weak': 'purple'
}

#initialise plotting 
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14), sharex=True)
plt.subplots_adjust(hspace=0.1)

scatter_plots = []     #for the interactive cursor
legend_elements = []   #legend list

#plotting ancient hosts
for ax, y_col in [(ax1, 'nickel mass'), (ax2, 'L_1998')]:
    #top panel - only show ancient hosts which are not KNs and have Ni mass
    if ax == ax1:
        ancient_subset = df_SN_valid[df_SN_valid['ancient'] == 'yes'].copy()
    #bottom plot - show all ancient hosts
    else:
        ancient_subset = df[df['ancient'] == 'yes'].copy()

    if not ancient_subset.empty:
        plot_y = pd.to_numeric(ancient_subset[y_col], errors='coerce')
        valid_mask = plot_y.notna()
        
        sc_anc = ax.scatter(
            ancient_subset.loc[valid_mask, 'T_90'], 
            plot_y[valid_mask], 
            color='grey', 
            s=600,        
            alpha=0.5, 
            zorder=0      
        )
        sc_anc.dataset = ancient_subset.loc[valid_mask]
        scatter_plots.append(sc_anc)

#add ancient hosts to legend
legend_elements.append(Line2D([0], [0], marker= 'o' if df['upperlimit'].iloc[0] == 'no' else 'v', color='w', markerfacecolor='grey', 
                              label='Ancient Host', markersize=15, alpha=0.5, linestyle='None'))

#plot progenitors nickel mass + luminosity plot 
for progenitor, color in edgecolour_map.items():
    sub_ni = df_SN_valid[df_SN_valid['progenitor'] == progenitor]
    sub_lum = df[df['progenitor'] == progenitor]

    for subset, ax, col_name in [(sub_ni, ax1, 'nickel mass'), (sub_lum, ax2, 'L_1998')]:
        #exclude 980425 for star marker later
        standard_dots = subset[subset['GRB'] != '980425']
        
        if not standard_dots.empty:
            f_colors = [facecolour_map.get(str(s).strip().lower(), 'white') for s in standard_dots['sample']]
            m_sizes = [250 if str(s).strip().lower() == 'gold' else 150 for s in standard_dots['sample']]
            
            y_values = pd.to_numeric(standard_dots[col_name], errors='coerce')
            valid_idx = y_values.notna()
            
            sc = ax.scatter(
                standard_dots.loc[valid_idx, 'T_90'], 
                y_values[valid_idx], 
                fc=[f_colors[i] for i, val in enumerate(valid_idx) if val], 
                ec=color, 
                s=[m_sizes[i] for i, val in enumerate(valid_idx) if val], 
                linewidth=2, 
                zorder=5
            )
            sc.dataset = standard_dots.loc[valid_idx]
            scatter_plots.append(sc)

    #add progenitor categories to legend
    legend_elements.append(Line2D([0], [0], marker='o' if df['upperlimit'].iloc[0] == 'no' else 'v', color='w', markeredgecolor=color, 
                                  markerfacecolor='white', label=progenitor, markersize=10, 
                                  markeredgewidth=2, linestyle='None'))

#plot GRB 980425 as a star --- keep this in ? 
star_grb = df[df['GRB'] == '980425'].copy()
if not star_grb.empty:
    for ax, col_name in [(ax1, 'nickel mass'), (ax2, 'L_1998')]:
        y_val_raw = star_grb[col_name].values[0]
        y_val = pd.to_numeric(y_val_raw, errors='coerce')
        
        if not np.isnan(y_val):
            sc_star = ax.scatter(
                star_grb['T_90'], y_val, 
                marker='*', s=800, color='brown', edgecolor='red', 
                linewidth=1.5, zorder=10, alpha=1.0
            )
            sc_star.dataset = star_grb
            scatter_plots.append(sc_star)

legend_elements.append(Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
                              markeredgecolor='black', label='GRB 980425', 
                              markersize=18, linestyle='None'))

#ensure limits allow all GRBs to be shown 
ax1.set_ylim(0.001, 2)
ax2.set_ylim(0.001, 5)

#SNe limit 
sn_limit = 0.13
ax2.axhline(y=sn_limit, color='red', linestyle='--', linewidth=2, zorder=1)
ax2.text(x=ax2.get_xlim()[0]*1.2, y=sn_limit*1.1, s='Supernova Limit', 
         color='red', fontweight='bold', fontsize=12)

ax1.set_ylabel(r'Nickel Mass ($M_{\odot}$)', fontsize=20)
ax2.set_ylabel(r'Luminosity Fraction $f_{1998bw}$', fontsize=20)
ax2.set_xlabel(r'$T_{90}$ (s)', fontsize=20)

#formatting axis ticks 
def format_ticks(x, pos):
    return f'{x:g}'

for ax in [ax1, ax2]:
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    #decimals
    ax.xaxis.set_major_formatter(FuncFormatter(format_ticks))
    ax.yaxis.set_major_formatter(FuncFormatter(format_ticks))
    
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    
    ax.tick_params(which='both', direction='in', top=True, right=True, labelsize=14)

ax1.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize=11)

#make plot interactive using @cursor.connect 
cursor = mplcursors.cursor(scatter_plots, hover=True)

@cursor.connect("add")
def on_add(sel):
    data = sel.artist.dataset
    row = data.iloc[sel.index]
    
    label = (f"GRB: {row.get('GRB', 'Unknown')}\n"
             f"Progenitor: {row.get('progenitor', 'N/A')}\n"
             f"z: {row.get('z', 0.0):.2f}\n"
             f"T_90: {row.get('T_90', 0.0):.2f}s\n"
             f"L_98bw: {row.get('L_1998', 0.0):.2f}\n")
    
    sel.annotation.set_text(label)
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9, edgecolor='black')

#also need to display lines between both values for 100316D and 190829A ? 
print("Plot ready. Hover to explore data. Use the popup window to interact.")
plt.show()
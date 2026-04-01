from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime
from pathlib import Path

import sqlite3
import hist

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
hep.style.use('CMS')

#--------------------------------------------------------------------------#
def make_BL_NW_2D_maps(pivot_df: pd.DataFrame, given_chip_name: str, note: str, save_path: Path, timestamp: str):
    """Generates 2D heatmaps for Baseline and Noise Width."""
    fig, axes = plt.subplots(1, 2, dpi=200, figsize=(20, 10))

    # Configuration for the two plots to avoid repeated code
    plot_configs = [
        (axes[0], 'baseline', 'BL', pivot_df['baseline'].values.min(), pivot_df['baseline'].values.max()),
        (axes[1], 'noise_width', 'NW', 0, 16)
    ]

    for ax, col_name, title_prefix, vmin, vmax in plot_configs:
        ax.set_title(f"{given_chip_name}: {title_prefix} (DAC LSB)\n{note}", size=17, loc="right")
        img = ax.imshow(pivot_df[col_name], interpolation='none', vmin=vmin, vmax=vmax)
        ax.set_aspect("equal")
        ax.invert_xaxis()
        ax.invert_yaxis()

        ax.set_xticks(range(16))
        ax.set_xticklabels(range(16), rotation="vertical")
        ax.set_yticks(range(16))
        ax.minorticks_off()

        hep.cms.text(loc=0, ax=ax, fontsize=17, text="ETL ETROC")

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size="5%", pad=0.05)
        fig.colorbar(img, cax=cax, orientation="vertical")

    # Dynamic threshold for text color visibility
    bl_min, bl_max = pivot_df['baseline'].values.min(), pivot_df['baseline'].values.max()
    bl_threshold = 0.55 * (bl_max - bl_min) + bl_min

    # Overlay numeric values on the heatmaps
    for col in range(16):
        for row in range(16):
            bl_value = int(pivot_df['baseline'][col][row])
            nw_value = int(pivot_df['noise_width'][col][row])

            bl_text_color = 'black' if bl_value > bl_threshold else 'white'
            nw_text_color = 'black' if nw_value > 9 else 'white'

            axes[0].text(col, row, bl_value, c=bl_text_color, size=10, rotation=45, fontweight="bold", ha="center", va="center")
            axes[1].text(col, row, nw_value, c=nw_text_color, size=11, rotation=45, fontweight="bold", ha="center", va="center")

    fig.tight_layout()
    fig.savefig(save_path / f'{given_chip_name}_BL_NW_2D_map_{timestamp}.png')
    plt.close(fig) # Properly closes the figure to free memory


#--------------------------------------------------------------------------#
def make_BL_NW_1D_hists(input_df: pd.DataFrame, given_chip_name: str, note: str, save_path: Path, timestamp: str):
    """Generates 1D histograms for Baseline and Noise Width."""
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # 1. Baseline Histogram
    hep.cms.text(loc=0, ax=axes[0], fontsize=17, text="ETL ETROC")
    axes[0].set_title(f"{given_chip_name}: BL (DAC LSB)\n{note}", size=17, loc="right")
    bl_array = input_df['baseline'].to_numpy().flatten()
    bl_hist = hist.Hist(hist.axis.Regular(128, 0, 1024, name='bl', label='BL [DAC]'))
    bl_hist.fill(bl_array)
    bl_hist.plot1d(ax=axes[0], yerr=False, label=f'Mean: {bl_array.mean():.2f}, Std: {bl_array.std():.2f}')
    axes[0].legend()

    # 2. Noise Width Histogram
    hep.cms.text(loc=0, ax=axes[1], fontsize=17, text="ETL ETROC")
    axes[1].set_title(f"{given_chip_name}: NW (DAC LSB)\n{note}", size=17, loc="right")
    nw_hist = hist.Hist(hist.axis.Regular(16, 0, 16, name='nw', label='NW [DAC]'))
    nw_array = input_df['noise_width'].to_numpy().flatten()
    nw_hist.fill(nw_array)
    nw_hist.plot1d(ax=axes[1], yerr=False, label=f'Mean: {nw_array.mean():.2f}, Std: {nw_array.std():.2f}')

    axes[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
    axes[1].xaxis.set_minor_locator(ticker.NullLocator())
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(save_path / f'{given_chip_name}_BL_NW_1D_hist_{timestamp}.png')
    plt.close(fig) # Properly closes the figure to free memory


#--------------------------------------------------------------------------#
def save_baselines(
        input_df: pd.DataFrame,
        hist_dir: str = "../ETROC-History",
        save_notes: str = "",
    ):
    """Saves the baselines for a single chip to SQL and generates plots."""

    save_mother_path = Path(hist_dir)
    save_mother_path.mkdir(exist_ok=True, parents=True)

    outfile = save_mother_path / 'BaselineHistory.sqlite'
    fig_outdir = save_mother_path / 'baseline_figures'
    fig_outdir.mkdir(exist_ok=True, parents=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    chip_name = input_df['chip_name'].unique()[0]

    # Pivot the data for the 2D map
    pivot_df = input_df.pivot(index=['row'], columns=['col'], values=['baseline', 'noise_width'])

    # Safely duplicate for SQL to prevent modifying the user's active DataFrame
    sql_df = input_df.copy()
    sql_df["save_notes"] = save_notes

    with sqlite3.connect(outfile) as sqlconn:
        sql_df.to_sql('baselines', sqlconn, if_exists='append', index=False)

    # Call the plotting functions
    make_BL_NW_2D_maps(pivot_df, chip_name, save_notes, fig_outdir, timestamp)
    make_BL_NW_1D_hists(input_df, chip_name, save_notes, fig_outdir, timestamp)
import os
import re
import cmocean
import numpy as np
import pandas as pd
import xarray as xr
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from typing import Any, Dict, List
from tsdat.config import VariableDefinition, DatasetDefinition
from tsdat.pipeline import IngestPipeline
from tsdat.utils import DSUtil

class MODAQIngestPipeline(IngestPipeline):
    """-------------------------------------------------------------------
    This is an example class that extends the default IngestPipeline in
    order to hook in custom behavior such as creating custom plots.
    If users need to apply custom changes to the dataset, instrument
    corrections, or create custom plots, they should follow this example
    to extend the IngestPipeline class.
    -------------------------------------------------------------------"""
    def customize_raw_datasets(self, raw_dataset_mapping: Dict[str, xr.Dataset]) -> Dict[str, xr.Dataset]:
        """-------------------------------------------------------------------
        Hook to allow for user customizations to one or more raw xarray Datasets
        before they merged and used to create the standardized dataset.  The
        raw_dataset_mapping will contain one entry for each file being used
        as input to the pipeline.  The keys are the standardized raw file name,
        and the values are the datasets.

        This method would typically only be used if the user is combining
        multiple files into a single dataset.  In this case, this method may
        be used to correct coordinates if they don't match for all the files,
        or to change variable (column) names if two files have the same
        name for a variable, but they are two distinct variables.

        This method can also be used to check for unique conditions in the raw
        data that should cause a pipeline failure if they are not met.

        This method is called before the inputs are merged and converted to
        standard format as specified by the config file.

        Args:
            raw_dataset_mapping (Dict[str, xr.Dataset])     The raw datasets to
                                                            customize.

        Returns:
            Dict[str, xr.Dataset]: The customized raw dataset.
        -------------------------------------------------------------------"""
        dod = self.config.dataset_definition
        time_def = dod.get_variable("time")
        """
        for filename, dataset in raw_dataset_mapping.items():
            if "GPS" in filename: 
                old_name = "Timestamp\n"
                new_name = "Timestamp"
                old_name2 = "Fix Time UTC\n"
                new_name2 = "Fix Time UTC"
                raw_dataset_mapping[filename] = dataset.rename_vars({old_name: new_name, old_name2: new_name2})
        """
        # No customization to raw data - return original dataset
        return raw_dataset_mapping
    
    def create_and_persist_plots(self, dataset: xr.Dataset):

        ds = dataset
        
        filename = DSUtil.get_plot_filename(dataset, "Three Phase Voltage", "png")
        with self.storage._tmp.get_temp_filepath(filename) as tmp_path:
            
            # Calculations for contour plots
            date = pd.to_datetime(ds.time.data[0]).strftime('%d-%b-%Y')
            #hi = np.ceil(ds.wind_speed.max().data + 1)
            #lo = np.floor(ds.wind_speed.min().data)
            #levels = np.arange(lo, hi, 1)

            # Colormaps to use
            #wind_cmap = cmocean.cm.deep_r
            #avail_cmap = cmocean.cm.amp_r

            # Create figure and axes objects
            fig, ax = plt.subplots(figsize=(16,8), constrained_layout=True)
            fig.suptitle(f"Three Phase Voltage from {ds.attrs['title']} on {date}")

            ds.MODAQ_Va[:100].plot(ax = ax)
            ds.MODAQ_Vb[:100].plot(ax = ax)
            ds.MODAQ_Vc[:100].plot(ax = ax)

            # Save the figure
            fig.savefig(tmp_path, dpi=100)
            self.storage.save(tmp_path)
            plt.close()

        return


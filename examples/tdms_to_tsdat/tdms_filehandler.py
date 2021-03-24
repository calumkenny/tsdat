import pandas as pd
import xarray as xr
from nptdms import TdmsFile

from tsdat import Config
from tsdat.io import AbstractFileHandler, register_filehandler

@register_filehandler(['.tdms','.done'])
class TdmsFileHandler(AbstractFileHandler):

    def write(ds: xr.Dataset, filename: str, config: Config, **kwargs):
        raise NotImplementedError("Error: this file format should not be used to write to.")

    def read(filename: str, **kwargs) -> xr.Dataset:
        tdms_file = TdmsFile.read(filename)
        for group in tdms_file.groups():
            df = group.as_dataframe()
            for channel in group.channels():
                df.rename({channel.name : channel.name.strip()}, axis = 1, inplace=True) #remove \n and spaces from channel names and assign inplace to columns axis
        return df.to_xarray() 

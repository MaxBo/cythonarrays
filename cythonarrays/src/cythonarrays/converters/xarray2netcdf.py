# -*- coding: utf-8 -*-
import xarray as xr


def xr2netcdf(dataset: xr.Dataset,
              filepath: str,
              mode: str='w',
              engine: str='netcdf4',
              compressed:bool=True,
              complevel:int=2, ):
    """
    save dataset as netcdf-file to filepath using the given compression level

    Parameters
    ----------
    dataset : xarray-dataset
        the xarray-dataset to store
    filepath : str
        the path where the netcdf-file shold be stored
    engine : str (optional, default=netcdf4)
        the engine to use
    compressed : boolen (optional, default=True)
        if False, the data-variables are not compressed
    complevel : int (optional, default=2)
        the compression-level between 1 and 9
        1 is faster, 9 uses a more efficient compression, but is much slower
        2 is in general a good compromise
    """
    encoding = {}
    comp = {}
    if compressed:
        comp['zlib'] = 'True'
        comp['complevel'] = complevel

    for data_var in dataset.data_vars:
        encoding[data_var] = comp
    dataset.to_netcdf(filepath, mode=mode, engine=engine, encoding=encoding)

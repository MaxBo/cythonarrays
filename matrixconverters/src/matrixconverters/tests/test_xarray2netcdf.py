# -*- coding: utf-8 -*-

import os
import pytest
import numpy as np
import xarray as xr
from matrixconverters.xarray2netcdf import xr2netcdf
from h5py.version import hdf5_version


@pytest.fixture(scope='class')
def folder() -> str:
    return os.path.dirname(__file__)


@pytest.fixture(scope='class')
def fp_dataset_with_umlaut(folder: str) -> str:
    fn = os.path.join(folder, 'ÄÖÜß', 'ÄÖÜß.nc4')
    return fn


@pytest.fixture(scope='class')
def fp_dataset_without_umlaut(folder: str) -> str:
    fn = os.path.join(folder, 'dataset_netcdf.nc4')
    return fn

@pytest.fixture(scope='class')
def ds() -> xr.Dataset:
    da = xr.DataArray(np.arange(9).reshape(3, 3))
    zones = xr.DataArray([100, 200, 300])
    names = xr.DataArray(['ÄÄÄ-Town', 'B-Village', 'C-City'])
    ds = xr.Dataset({'matrix': da,
                     'zone_no': zones,
                     'zone_name': names,})
    return ds


class TestSaveReadxr2netcdf:
    def test_01_save_ds(self, ds: xr.Dataset, fp_dataset_without_umlaut: str):
        xr2netcdf(ds, fp_dataset_without_umlaut)
        ds_saved = xr.open_dataset(fp_dataset_without_umlaut)
        np.testing.assert_array_equal(ds_saved.matrix, ds.matrix)
        np.testing.assert_array_equal(ds_saved.zone_no, ds.zone_no)
        np.testing.assert_array_equal(ds_saved.zone_name, ds.zone_name)

    @pytest.mark.xfail(
        (hdf5_version < '1.18'),
        reason='''Hdf5 cannot use filepaths with non-ascii-characters
        - on windows it works locally, but not on appveyor - on linux it failes''')
    def test_02_save_ds_with_umlaut(self, ds: xr.Dataset, fp_dataset_with_umlaut: str):
        xr2netcdf(ds, fp_dataset_with_umlaut)
        ds_saved = xr.open_dataset(fp_dataset_with_umlaut)
        np.testing.assert_array_equal(ds_saved.matrix, ds.matrix)
        np.testing.assert_array_equal(ds_saved.zone_no, ds.zone_no)
        np.testing.assert_array_equal(ds_saved.zone_name, ds.zone_name)

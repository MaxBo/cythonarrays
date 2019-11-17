# -*- coding: utf-8 -*-

import sys
import os
import pytest
import numpy as np
import xarray as xr
from matrixconverters.xarray2netcdf import xr2netcdf


@pytest.fixture(scope='class')
def folder():
    return os.path.dirname(__file__)


@pytest.fixture(scope='class')
def fp_dataset_with_umlaut(folder):
    fn = os.path.join(folder, 'ÄÖÜß', 'ÄÖÜß.nc4')
    return fn


class TestSaveReadxr2netcdf:
    def test_01_save_ds(self, fp_dataset_with_umlaut):
        da = xr.DataArray(np.arange(9).reshape(3, 3))
        zones = xr.DataArray([100, 200, 300])
        names = xr.DataArray(['ÄÄÄ-Town', 'B-Village', 'C-City'])
        ds = xr.Dataset({'matrix': da,
                         'zone_no': zones,
                         'zone_name': names,})
        # if the filepath containes non-ascii chars, you have to use the
        # legacy encoding in windows
        sys._enablelegacywindowsfsencoding()
        xr2netcdf(ds, fp_dataset_with_umlaut)
        ds_saved = xr.open_dataset(fp_dataset_with_umlaut)
        np.testing.assert_array_equal(ds_saved.matrix, da)
        np.testing.assert_array_equal(ds_saved.zone_no, zones)
        np.testing.assert_array_equal(ds_saved.zone_name, names)

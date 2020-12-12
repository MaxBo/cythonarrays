# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
import numpy as np
from matrixconverters.read_ptv import ReadPTVMatrix
from matrixconverters.save_ptv import SavePTV
import xarray as xr


@pytest.fixture(scope='class')
def folder() -> str:
    return os.path.dirname(__file__)


@pytest.fixture(scope='class')
def matrix_fn(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_v_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_out(folder: str) -> str:
    fn = os.path.join(folder, 'matrix.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bk_out(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bk_format.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bi_out(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bi_format.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bk(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bk_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bi(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bi_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bl_out(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bl_format.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bl(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_bl_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_o(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_o_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_o_without_names(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_o_format_without_names.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_o_with_zeros(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_o_format_with_zeros.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_o_with_dashes(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_o_format_with_dashes.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_e(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_e_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_s(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_s_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_or(folder: str) -> str:
    fn = os.path.join(folder, 'matrix_or_format.mtx')
    return fn


class TestReadPTV:
    """Test reading PTV matrices"""
    def test_01_read_v_format(self, matrix_fn: str):
        """Test reading v-Format"""
        ds = ReadPTVMatrix(filename=matrix_fn)
        self.print_matrix(ds)

    def test_02_read_bk_format(self, matrix_fn_bk):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        self.print_matrix(ds)

    def test_02a_read_o_format(self,
                               matrix_fn_o,
                               matrix_fn_or,
                               matrix_fn_o_without_names,
                               matrix_fn_o_with_zeros,
                               matrix_fn_o_with_dashes):
        """Test reading bk-format"""
        zone_no = [100, 200, 300, 400]
        ds = ReadPTVMatrix(filename=matrix_fn_o)
        self.print_matrix(ds)
        np.testing.assert_equal(ds.zone_no.data, zone_no)

        ds = ReadPTVMatrix(filename=matrix_fn_or)
        self.print_matrix(ds)
        np.testing.assert_equal(ds.zone_no.data, zone_no)

        ds = ReadPTVMatrix(filename=matrix_fn_o_without_names)
        self.print_matrix(ds)
        np.testing.assert_equal(ds.zone_no.data, zone_no)

        ds = ReadPTVMatrix(filename=matrix_fn_o_with_zeros)
        self.print_matrix(ds)
        np.testing.assert_equal(ds.zone_no.data, zone_no)
        np.testing.assert_equal((ds.matrix.data != 0).sum(), 2,
                                err_msg='only 2 values should be different to 0')

        ds = ReadPTVMatrix(filename=matrix_fn_o_with_dashes)
        self.print_matrix(ds)
        np.testing.assert_equal(ds.zone_no.data, zone_no)
        np.testing.assert_equal((ds.matrix.data != 0).sum(), 1,
                                err_msg='only 1 values should be different to 0')


    def test_02b_read_e_s_format(self, matrix_fn_e, matrix_fn_s):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_e)
        self.print_matrix(ds)

        ds = ReadPTVMatrix(filename=matrix_fn_s)
        self.print_matrix(ds)

    def test_02c_read_bi_format(self, matrix_fn_bi):
        """Test reading bki-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bi)
        self.print_matrix(ds)

    def print_matrix(self, ds):
        print(ds)
        print('Histogram of travel times')
        print(np.histogram(ds.matrix.data, bins=range(0, 60, 10)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)

    def test_03_save_v_format(self, matrix_fn_bk, matrix_fn_out):
        """Test writing v-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins=range(0, 60, 10)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_out,
                        file_type='VN', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_out)
        print(np.histogram(ds2.matrix.data, bins=range(0, 60, 10)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        np.testing.assert_almost_equal(sum_before, sum_after, decimal=5)

    def test_03b_save_vm_format(self, matrix_fn_bk, matrix_fn_out):
        """Test writing vm-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        sum_before = ds.matrix.data.sum()
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_out,
                        file_type='VM', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_out)
        sum_after = ds2.matrix.data.sum()
        np.testing.assert_almost_equal(sum_before, sum_after, decimal=5)

    def test_05_save_bk_format(self, matrix_fn_bk, matrix_fn_bk_out):
        """Test writing bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins=range(8)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_bk_out,
                        file_type='BK', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_bk_out)
        print(np.histogram(ds2.matrix.data, bins=range(8)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        assert sum_before == sum_after
        #  test if it raises Exception, if zone numbers do not match the matrix
        del ds['zone_name']
        ds['zone_no'] = xr.IndexVariable(('zone_no', ), ds['zone_no'][:3])
        with pytest.raises(AssertionError):
            SavePTV(ds).savePTVMatrix(file_name=matrix_fn_bk_out,
                        file_type='BK', )

    def test_05a_save_bi_format(self, matrix_fn_bi, matrix_fn_bi_out):
        """Test writing bi-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bi)
        print(np.histogram(ds.matrix.data, bins=range(8)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_bi_out, file_type='BI')
        ds2 = ReadPTVMatrix(filename=matrix_fn_bi_out)
        print(np.histogram(ds2.matrix.data, bins=range(8)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        assert sum_before == sum_after

    def test_05b_save_bi_format_zero(self, matrix_fn_bi, matrix_fn_bi_out):
        """Test writing bi-format with zero flag"""
        ds = ReadPTVMatrix(filename=matrix_fn_bi)
        ds.matrix.data[:] = 0
        print(np.histogram(ds.matrix.data, bins=range(8)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_bi_out, file_type='BI')
        ds2 = ReadPTVMatrix(filename=matrix_fn_bi_out)
        print(np.histogram(ds2.matrix.data, bins=range(8)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        assert sum_before == sum_after

    def test_06_save_o_format(self, matrix_fn_bk, matrix_fn_out):
        """Test writing v-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins=range(0, 60, 10)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_out,
                        file_type='O', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_out)
        print(np.histogram(ds2.matrix.data, bins=range(0, 60, 10)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        np.testing.assert_almost_equal(sum_before, sum_after, decimal=5)

    def test_07_save_bl_format(self, matrix_fn_bl, matrix_fn_bl_out):
        """Test writing bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bl)
        print(np.histogram(ds.matrix.data, bins=range(8)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        ds['zone_name'][:] = ['A', 'B', 'C', 'D', 'E']
        ds['zone_names2'][:] = ['ÄÄ', 'ÜÜ', 'Öß€']
        ds = ds.assign_coords(zone_no2=ds['zone_no2'] * 100)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_bl_out,
                        file_type='BK', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_bl_out)
        print(np.histogram(ds2.matrix.data, bins=range(8)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        assert sum_before == sum_after
        np.testing.assert_array_equal(ds.zone_no, ds2.zone_no)
        np.testing.assert_array_equal(ds.zone_no2, ds2.zone_no2)
        np.testing.assert_array_equal(ds.zone_name, ds2.zone_name)
        np.testing.assert_array_equal(ds.zone_names2, ds2.zone_names2)

    def test_08_save_simple_ds(self, matrix_fn_bk_out):
        da = xr.DataArray(np.arange(9).reshape(3, 3))
        zones = xr.DataArray([100, 200, 300])
        names = xr.DataArray(['A-Town', 'B-Village', 'C-City'])
        ds = xr.Dataset({'matrix': da,
                         'zone_no': zones,
                         'zone_name': names,})
        s = SavePTV(ds)
        s.savePTVMatrix(matrix_fn_bk_out)

        ds_saved = ReadPTVMatrix(matrix_fn_bk_out)
        print(ds_saved)
        np.testing.assert_array_equal(ds_saved.matrix, da)
        np.testing.assert_array_equal(ds_saved.zone_no, zones)
        np.testing.assert_array_equal(ds_saved.origins, zones)
        np.testing.assert_array_equal(ds_saved.destinations, zones)
        np.testing.assert_array_equal(ds_saved.zone_name, names)
        np.testing.assert_array_equal(ds_saved.zone_names2, names)

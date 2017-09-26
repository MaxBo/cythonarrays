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


@pytest.fixture(scope='class')
def folder():
    return os.path.dirname(__file__)


@pytest.fixture(scope='class')
def matrix_fn(folder):
    fn = os.path.join(folder, 'matrix_v_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_out(folder):
    fn = os.path.join(folder, 'matrix.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_b_out(folder):
    fn = os.path.join(folder, 'matrix_b_format.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bk_out(folder):
    fn = os.path.join(folder, 'matrix_bk_format.out')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bk(folder):
    fn = os.path.join(folder, 'matrix_bk_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_bl_out(folder):
    fn = os.path.join(folder, 'matrix_bl_format.out')
    return fn

@pytest.fixture(scope='class')
def matrix_fn_bl(folder):
    fn = os.path.join(folder, 'matrix_bl_format.mtx')
    return fn

@pytest.fixture(scope='class')
def matrix_fn_o(folder):
    fn = os.path.join(folder, 'matrix_o_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_e(folder):
    fn = os.path.join(folder, 'matrix_e_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_s(folder):
    fn = os.path.join(folder, 'matrix_s_format.mtx')
    return fn


@pytest.fixture(scope='class')
def matrix_fn_or(folder):
    fn = os.path.join(folder, 'matrix_or_format.mtx')
    return fn


class TestReadPTV:
    """Test reading PTV matrices"""
    def test_01_read_v_format(self, matrix_fn):
        """Test reading v-Format"""
        ds = ReadPTVMatrix(filename=matrix_fn)
        self.print_matrix(ds)

    def test_02_read_bk_format(self, matrix_fn_bk):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        self.print_matrix(ds)

    def test_02a_read_o_format(self, matrix_fn_o, matrix_fn_or):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_o)
        self.print_matrix(ds)

        ds = ReadPTVMatrix(filename=matrix_fn_or)
        self.print_matrix(ds)

    def test_02b_read_e_s_format(self, matrix_fn_e, matrix_fn_s):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_e)
        self.print_matrix(ds)

        ds = ReadPTVMatrix(filename=matrix_fn_s)
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

    def test_03a_depreciated_args(self, matrix_fn_bk, matrix_fn_out):
        """Test depreciated arguments"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_out,
                        Ftype='VN', )


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

    def test_04_save_b_format(self, matrix_fn_bk, matrix_fn_b_out):
        """Test writing uncompressed b-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins=range(8)))
        sum_before = ds.matrix.data.sum()
        print(sum_before)
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_b_out,
                        file_type='B', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_b_out)
        print(np.histogram(ds2.matrix.data, bins=range(8)))
        sum_after = ds2.matrix.data.sum()
        print(sum_after)
        assert sum_before == sum_after

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
        ds['zone_no2'] *= 100
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


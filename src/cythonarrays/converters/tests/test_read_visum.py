# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
import numpy as np
from cythonarrays.converters.read_ptv import ReadPTVMatrix
from cythonarrays.converters.save_ptv import SavePTV


@pytest.fixture(scope='class')
def matrix_fn():
    fn = os.path.join(os.path.dirname(__file__),
                      'example_dataset.h5')
    fn = r'E:\GGR\Kiel\60 Modell\610 Wirtschaftsverkehrsmodell\612 Beispieldaten\Matrizen\2 TT0 (Pkw Pkw).mtx'
    return fn

@pytest.fixture(scope='class')
def matrix_fn_out():
    fn = os.path.join(os.path.dirname(__file__),
                      'example_dataset.h5')
    fn = r'E:\GGR\Kiel\60 Modell\610 Wirtschaftsverkehrsmodell\612 Beispieldaten\Matrizen\IV_out.mtx'
    return fn

@pytest.fixture(scope='class')
def matrix_fn_bk_out():
    fn = os.path.join(os.path.dirname(__file__),
                      'example_dataset.h5')
    fn = r'E:\GGR\Kiel\60 Modell\610 Wirtschaftsverkehrsmodell\612 Beispieldaten\Matrizen\OV_out.NTR'
    return fn

@pytest.fixture(scope='class')
def matrix_fn_bk():
    fn = os.path.join(os.path.dirname(__file__),
                      'example_dataset.h5')
    fn = r'E:\Modell\KS\Matrizen\130503_Kenngr_OV_Nullfall\19_24\OV.NTR'
    return fn

class TestReadPTV:
    """Test reading PTV matrices"""
    def test_01_read_v_format(self, matrix_fn):
        """Test reading v-Format"""
        ds = ReadPTVMatrix(filename=matrix_fn)
        print(ds)

    def test_02_read_bk_format(self, matrix_fn_bk):
        """Test reading bk-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(ds)
        print('Histogram of number of transfers')
        print(np.histogram(ds.matrix.data, bins = range(8)))

    def test_03_save_v_format(self, matrix_fn_bk, matrix_fn_out):
        """Test writing v-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins = range(8)))
        print(ds.matrix.data.sum())
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_out,
                        Ftype='VN', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_out)
        print(np.histogram(ds2.matrix.data, bins = range(8)))
        print(ds2.matrix.data.sum())

    def test_04_save_bk_format(self, matrix_fn_bk, matrix_fn_bk_out):
        """Test writing v-format"""
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(np.histogram(ds.matrix.data, bins = range(8)))
        print(ds.matrix.data.sum())
        s = SavePTV(ds)
        s.savePTVMatrix(file_name=matrix_fn_bk_out,
                        Ftype='BK', )
        ds2 = ReadPTVMatrix(filename=matrix_fn_bk_out)
        print(np.histogram(ds2.matrix.data, bins = range(8)))
        print(ds2.matrix.data.sum())

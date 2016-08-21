# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
import numpy as np
from cythonarrays.converters.read_ptv import ReadPTVMatrix


@pytest.fixture(scope='class')
def matrix_fn():
    fn = os.path.join(os.path.dirname(__file__),
                      'example_dataset.h5')
    fn = r'E:\GGR\Kiel\60 Modell\610 Wirtschaftsverkehrsmodell\612 Beispieldaten\Matrizen\2 TT0 (Pkw Pkw).mtx'
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
        ds = ReadPTVMatrix(filename=matrix_fn)
        print(ds)

    def test_02_read_bk_format(self, matrix_fn_bk):
        ds = ReadPTVMatrix(filename=matrix_fn_bk)
        print(ds)
        print('Histogram of number of transfers')
        print(np.histogram(ds.matrix.data, bins = range(8)))

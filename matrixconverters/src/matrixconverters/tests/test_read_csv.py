# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
import numpy as np
from matrixconverters.read_csv import ReadOFormat
from matrixconverters.save_ptv import SavePTV
from matrixconverters.tests.test_read_visum import folder, matrix_fn


@pytest.fixture(scope='class')
def fn_zones(folder):
    fn = os.path.join(folder, 'zones.csv')
    return fn

@pytest.fixture(scope='class')
def fn_matrix(folder):
    fn = os.path.join(folder, 'matrix.csv')
    return fn



class TestReadCSV:
    """Test reading CSV matrices"""
    def test_01_read_csv(self, fn_zones, fn_matrix):
        """Test reading CSV-Format"""
        ds = ReadOFormat(zonefile=fn_zones,
                         matrixfile=fn_matrix)
        print(ds)
        print(ds.matrix)
        np.testing.assert_allclose(ds.matrix.sum(), 198.1)

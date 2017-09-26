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
from matrixconverters.tests.test_read_visum import folder, matrix_fn


@pytest.fixture(scope='class')
def matrix_cc(folder):
    fn = os.path.join(folder, 'matrix.cc')
    return fn


@pytest.fixture(scope='class')
def matrix_cc_out(folder):
    fn = os.path.join(folder, 'matrix_out.cc')
    return fn


@pytest.fixture(scope='class')
def matrix_cn(folder):
    fn = os.path.join(folder, 'matrix.cn')
    return fn

@pytest.fixture(scope='class')
def matrix_cn_out(folder):
    fn = os.path.join(folder, 'matrix_out.cn')
    return fn


class TestReadPSV:
    """Test reading PSV matrices"""
    def test_01_write_cc(self, matrix_fn, matrix_cc_out):
        """Test writing CC-Format"""
        ds = ReadPTVMatrix(filename=matrix_fn)
        s = SavePTV(ds)
        s.savePSVMatrix(file_name=matrix_cc_out,
                        ftype='CC', )

    def test_02_write_cn(self, matrix_fn, matrix_cn_out):
        """Test writing CC-Format"""
        ds = ReadPTVMatrix(filename=matrix_fn)
        s = SavePTV(ds)
        s.savePSVMatrix(file_name=matrix_cn_out,
                            ftype='CN', )

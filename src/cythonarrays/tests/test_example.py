# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
import numpy as np
from cythonarrays.converters.read_ptv import ReadPTVMatrix
from cythonarrays.tests.example_python import Example, ExampleAgent


@pytest.fixture(scope='class')
def folder():
    return os.path.dirname(__file__)


@pytest.fixture(scope='class')
def file(folder):
    fn = os.path.join(folder, 'example.h5')
    return fn


@pytest.fixture(scope='class')
def example():
    example = Example(n_groups=2, n_zones=4)
    example.define_datasets()
    example.data['groups'] = ['EW', 'AZ']
    example.data['zone_no'] = [100, 200, 300, 400]
    example.data['origins'] = [100, 200, 300, 400]
    example.source_potential_gh[:] = [[100, 0, 50, 100],
                                      [50, 100, 50, 0]]
    return example

class TestExample:
    """Test reading PTV matrices"""
    def test_01_generate_example(self, example, file):
        """Test generating example file"""
        print(example)
        example.save_data('data', file)

    def test_02_example_agent(self, example):
        """Test the example agent"""
        agent = ExampleAgent(0,
                             example.data.ids.data,
                             example.data.ages.data,
                             example.data.names.data,
                             example.n_chars)
        print(agent.i)
        pass



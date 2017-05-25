# -*- coding: utf-8 -*-

import multiprocessing
import xarray as xr
import os
from collections import defaultdict
import numpy as np

from cythonarrays.array_properties import _ArrayProperties
import pyximport; pyximport.install()
from .example_cython import (_Example)

np.seterr(divide='ignore', invalid='ignore')


class Example(_Example, _ArrayProperties):
    """Example job choice model"""

    def __init__(self,
                 n_groups,
                 n_zones,
                 threading=True,
                 init_arrays=True):
        super().__init__()

        self.n_zones = n_zones
        self.n_groups = n_groups
        self.set_n_threads(threading)

        self.define_arrays()
        if init_arrays:
            self.init_arrays()

    def set_n_threads(self, threading=True):
        """Set the number of threads"""
        if threading:
            self.n_threads = min(multiprocessing.cpu_count(), self.n_groups)
        else:
            self.n_threads = 1

    def define_arrays(self):
        """Define the arrays"""
        self.init_array('param_g', 'n_groups', -0.1)
        self.init_array('km_ij', 'n_zones, n_zones')

        self.init_array('persons_gi', 'n_groups, n_zones')
        self.init_array('jobs_j', 'n_zones')
        self.init_array('trips_ij', 'n_zones, n_zones', 0)

        # the following array will not be initialized for testing purposes
        # self.init_array('not_initialized_ij', 'n_zones, n_groups')


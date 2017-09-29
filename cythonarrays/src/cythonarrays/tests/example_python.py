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
    """
    Example job choice model

    Parameters
    ----------
    groups : int
        the number of groups
    origins : int
        the number of zones
    threading: bool, optional(default=True)
        use multiprocessing?
    init_arrays: bool, optional(default=True)
        if true, the arrays are initialized in the beginning

    """
    _coordinates = {'origins': 'zonenumbers_i',
                    'destinations': 'zonenumbers_i',
                    'groups': 'groupnames_g',
                    }

    def __init__(self,
                 groups,
                 origins,
                 threading=True,
                 init_arrays=True):
        super().__init__()

        self.groups = groups
        zones = origins
        self.origins = zones
        self.destinations = zones
        self.set_n_threads(threading)

        self.define_arrays()
        if init_arrays:
            self.init_arrays()

    def set_n_threads(self, threading=True):
        """Set the number of threads"""
        if threading:
            self.n_threads = min(multiprocessing.cpu_count(), self.groups)
        else:
            self.n_threads = 1

    def define_arrays(self):
        """Define the arrays"""
        self.init_array('param_g', 'groups', -0.1)
        self.init_array('km_ij', 'origins, destinations')

        self.init_array('persons_gi', 'groups, origins')
        self.init_array('jobs_j', 'destinations')
        self.init_array('trips_ij', ['origins', 'destinations'], 0)

        self.init_array('zonenumbers_i', 'origins')
        self.init_object_array('groupnames_g', 'groups')
        self.init_object_array('zonenames_i', ['origins'])

        self.init_array('valid_g', 'groups', 1)
        self.init_array('invalid_g', 'groups', 0)

        # the following array will not be initialized for testing purposes
        # self.init_array('not_initialized_ij', 'zones, groups')


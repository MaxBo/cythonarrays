# -*- coding: utf-8 -*-


import numpy as np
np.seterr(divide='ignore', invalid='ignore')

from cythonarrays.array_properties import _ArrayProperties
import pyximport; pyximport.install()
from .simple_cython import (_Simple)



class Simple(_Simple, _ArrayProperties):
    """
    Simple job choice model

    Parameters
    ----------
    groups : int
        the number of groups
    zones : int
        the number of zones
    init_arrays: bool, optional(default=True)
        if true, the arrays are initialized in the beginning

    """
    _coordinates = {'zones': 'zonenumbers_i',
                    'groups': 'groupnames_g',
                    }

    def __init__(self,
                 groups,
                 zones,
                 init_arrays=True):
        super().__init__()

        self.groups = groups
        self.zones = zones

        self.define_arrays()
        if init_arrays:
            self.init_arrays()

    def define_arrays(self):
        """Define the arrays"""
        self.init_array('param_g', 'groups', -0.1)

        self.init_array('persons_gi', 'groups, zones')
        self.init_array('zonenumbers_i', 'zones')
        self.init_object_array('groupnames_g', 'groups')



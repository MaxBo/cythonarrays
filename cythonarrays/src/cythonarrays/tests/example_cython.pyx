# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True

cimport cython
cimport numpy as np
import numpy as np

from cython.parallel import prange, threadid, parallel
from cythonarrays.numpy_types cimport *

from cythonarrays.array_shapes cimport ArrayShapes
from cythonarrays.array_shapes import ArrayShapes
from libc.math cimport exp, log


cdef class _Example(ArrayShapes):
    """
    Cython CDefClass for Example model
    with n_groups and n_zones
    """

    def __cinit__(self, *args, **kwargs):
        """init the file"""
        for cls in self.__class__.__mro__:
            self._search_memview(cls)

    @cython.initializedcheck(False)
    cpdef char calc_model(self) except -1:
        """
        Calc the daily trips for all groups and zones
        """
        cdef char t, r
        cdef long32 g, h
        cdef double tours, linking_trips
        self.reset_array('trips_ij')
        with nogil, parallel(num_threads=self.n_threads):
            t = threadid()
            # loop over calibration groups
            for g in prange(self.n_groups, schedule='guided'):
                with gil:
                    self.logger.info('calculate group {}'.format(g))
                # loop over home zones
                self._calc_p_destination(g)

    @cython.initializedcheck(False)
    cdef double _calc_weight_destination(self, double param,
                                         double minutes, double jobs) nogil:
        """calculate weight for destination"""
        cdef double weight = exp(param * minutes) * jobs
        return weight


    @cython.initializedcheck(False)
    cdef ARRAY_1D_d _calc_p_destination(self,
                                        long32 g) nogil:
        """abc"""
        cdef double param, minutes, persons, jobs, weight, total_weight
        cdef long32 i, j
        cdef ARRAY_1D_d weights_j
        with gil:
            weights_j = np.empty((self.n_zones), 'd')
        param = self._param_g[g]
        for i in range(self.n_zones):
            persons = self._persons_gi[g, i]
            total_weight = 0
            for j in range(self.n_zones):
                jobs = self._jobs_j[j]
                minutes = self._km_ij[i, j]
                weight = self._calc_weight_destination(param, minutes, jobs)
                weights_j[j] = weight
                total_weight += weight
            factor = persons / total_weight
            for j in range(self.n_zones):
                self._trips_ij[i, j] += factor * weights_j[j]
        return weights_j

    def calc_p_destination(self, g):
        return self._calc_p_destination(g)

# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True

cimport cython
import numpy as np

from cython.parallel import prange, threadid, parallel
from cythonarrays.numpy_types cimport *
from cythonarrays.array_shapes cimport ArrayShapes
from libc.math cimport exp


cdef class _Example(ArrayShapes):
    """
    Cython CDefClass for Example model
    with coordinates groups and zones
    """
    @cython.initializedcheck(False)
    cpdef char calc_model(self) except -1:
        """
        Calc the daily trips for all groups and zones
        """
        cdef char t
        cdef long32 g
        self.reset_array('trips_ij')
        with nogil, parallel(num_threads=self.n_threads):
            t = threadid()
            # loop over groups
            for g in prange(self.groups, schedule='guided'):
                with gil:
                    self.logger.info('calculate group {}'.format(g))
                # calc destination choice model for group g
                self._calc_p_destination(g)

    @cython.initializedcheck(False)
    cdef double _calc_weight_destination(self, double param,
                                         double minutes, double jobs) nogil:
        """calculate weight for destination"""
        cdef double weight = exp(param * minutes) * jobs
        return weight

    @cython.initializedcheck(False)
    cdef ARRAY_1D_d _calc_p_destination(self, long32 g) nogil:
        """Calc the destination choice probability for group g"""
        cdef double param, minutes, persons, jobs, weight, total_weight
        cdef long32 i, j
        cdef ARRAY_1D_d weights_j
        with gil:
            weights_j = np.empty((self.destinations), 'd')
        param = self._param_g[g]
        for i in range(self.origins):
            persons = self._persons_gi[g, i]
            total_weight = 0
            for j in range(self.destinations):
                jobs = self._jobs_j[j]
                minutes = self._km_ij[i, j]
                weight = self._calc_weight_destination(param, minutes, jobs)
                weights_j[j] = weight
                total_weight += weight
            factor = persons / total_weight
            for j in range(self.destinations):
                self._trips_ij[i, j] += factor * weights_j[j]
        return weights_j

    def calc_p_destination(self, g):
        """
        Calc the destination choice probability for group g

        Parameters
        ----------
        g : int
            the group number

        Returns
        -------
        weights : np.array
            array with the weights for each zone
        """
        return self._calc_p_destination(g)



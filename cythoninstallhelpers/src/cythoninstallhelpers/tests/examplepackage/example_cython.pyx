# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True

cimport cython
import numpy as np

from cython.parallel import prange, threadid, parallel


cdef class Example:
    """
    Cython CDefClass for Example
    """
    def __init__(self, int i, int j, char n_threads, cython.longlong large_value):
        """
        Create the array with dimensions i and j

        Parameters
        ----------
        i:
            number of rows
        j:
            number of columns
        n_threads:
            number of threads
        large_value:
            a large value
        """
        self.array_ij = np.arange(i*j).astype('d').reshape((i, j))
        self.n_threads = n_threads
        self.large_value = large_value

    cpdef double calc_array(self, double param):
        """
        Calc an array with the given parameter

        Parameters
        ----------
        param:
            a parameter

        Returns
        -------
        :
            the result
        """
        cdef int i, j, t, n_rows, n_cols
        n_rows = self.array_ij.shape[0]
        n_cols = self.array_ij.shape[1]

        self.rowsums = np.zeros((n_rows))
        with nogil, parallel(num_threads=self.n_threads):
            t = threadid()
            # loop over calibration groups
            for i in prange(n_rows, schedule='guided'):
                for j in range(n_cols):
                    self.rowsums[i] += self.array_ij[i, j] * param - self.large_value
        return np.array(self.rowsums).mean()






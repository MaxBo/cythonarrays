# -*- coding: utf-8 -*-

cimport cython
cimport numpy as np

cdef class Example():
    """
    Cython CDefClass for Example class
    """
    cdef public cython.char n_threads
    cdef public cython.longlong large_value
    cdef public cython.double[:, :] array_ij
    cdef public cython.double[:] rowsums

    cpdef double calc_array(self, double param)



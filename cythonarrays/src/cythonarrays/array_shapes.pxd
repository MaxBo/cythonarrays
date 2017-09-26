# -*- coding: utf-8 -*-
cimport numpy as np
cimport cython

from .numpy_types cimport np_floating

cdef class ArrayShapes(object):
    cdef public float NAN_f
    cdef public float INF_f
    cdef public float NINF_f

    cdef public double NAN_d
    cdef public double INF_d
    cdef public double NINF_d

    cdef public char isnan(self, np_floating x) nogil

    cpdef _search_memview(self, cls)
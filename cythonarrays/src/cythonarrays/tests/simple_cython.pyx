# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True


from cythonarrays.numpy_types cimport *
from cythonarrays.array_shapes cimport ArrayShapes



cdef class _Simple(ArrayShapes):
    """
    Cython CDefClass for Example model
    with coordinates groups and zones
    """



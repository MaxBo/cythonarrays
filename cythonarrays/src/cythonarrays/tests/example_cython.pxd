# -*- coding: utf-8 -*-

from cythonarrays.numpy_types cimport *

from cythonarrays.array_shapes cimport ArrayShapes
from cythonarrays.array_shapes import ArrayShapes


cdef class _Example(ArrayShapes):
    """
    Cython CDefClass for Example model
    with n_groups and n_zones
    """
    cdef public long32 n_groups
    cdef public long32 n_zones
    cdef public char n_threads

    # parameter of groups
    cdef public ARRAY_1D_d _param_g

    # distance matrix (km from a to b)
    cdef public ARRAY_2D_d _km_ij

    # persons per group and zone
    cdef public ARRAY_2D_d _persons_gi
    # jobs per zone
    cdef public ARRAY_1D_d _jobs_j

    # resulting trip matrix
    cdef public ARRAY_2D_d _trips_ij

    # not initialized matrix
    cdef public ARRAY_2D_i4 _not_initialized_ij


    cpdef char calc_model(self) except -1
    cdef double _calc_weight_destination(self, double param,
                                         double minutes, double jobs) nogil
    cdef ARRAY_1D_d _calc_p_destination(self, long32 g) nogil



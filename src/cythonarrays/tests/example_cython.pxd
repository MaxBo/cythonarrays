# -*- coding: utf-8 -*-

from cythonarrays.numpy_types cimport *

from cythonarrays.array_shapes cimport ArrayShapes
from cythonarrays.array_shapes import ArrayShapes


cdef class _Example(ArrayShapes):
    """
    BaseClass for Example model
    with n_groups and n_zones
    """
    cdef public long32 n_groups
    cdef public long32 n_zones
    cdef public long32 n_chars
    cdef public char n_threads

    # Sources for each group
    cdef public ARRAY_2D_d _source_potential_gh

    # resulting trips
    cdef public ARRAY_3D_d _trips_gij

    # group attributes
    cdef public ARRAY_1D_i1 _ages
    cdef public ARRAY_1D_i4 _ids


cdef class ExampleAgent:
    """
    Example Agent
    """
    cdef public ARRAY_1D_i4 _ids
    cdef public ARRAY_1D_i1 _ages
    cdef public ARRAY_1D_i4 _names
    cdef public int i
    cdef public int n_chars

    cpdef long32 get_id(self)
    cpdef char set_id(self, long32)
    cpdef char get_age(self)
    cpdef char set_age(self, char)
    cpdef str get_name(self)
    cpdef char set_name(self, str)


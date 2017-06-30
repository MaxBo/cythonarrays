# -*- coding: utf-8 -*-

from cythonarrays.numpy_types cimport *
from cythonarrays.array_shapes cimport ArrayShapes


cdef class _Simple(ArrayShapes):
    """
    Cython CDefClass for Simple model
    with coordinates groups, origins, and destinations
    """
    cdef public long32 groups
    cdef public long32 zones

    # zonenumbers
    cdef public ARRAY_1D_i4 _zonenumbers_i

    # parameter of groups
    cdef public ARRAY_1D_d _param_g

    # persons per group and zone
    cdef public ARRAY_2D_d _persons_gi


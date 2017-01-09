# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True

cimport cython
cimport numpy as np
import numpy as np

from cython.parallel import prange, threadid, parallel
cimport openmp
from cythonarrays.numpy_types cimport *
from cythonarrays.array_properties import _ArrayProperties
from cythonarrays.array_shapes cimport ArrayShapes
from cythonarrays.array_shapes import ArrayShapes


cdef class _Example(ArrayShapes):
    """
    BaseClass for Example model
    with n_groups and n_zones
    """

    def __cinit__(self, *args, **kwargs):
        """init the file"""
        for cls in self.__class__.__mro__:
            self._search_memview(cls)

cdef class ExampleAgent:
    """
    Example Agent
    """
    def __cinit__(self,
                  int i,
                  ARRAY_1D_i4 ids,
                  ARRAY_1D_i1 ages,
                  np.ndarray names,
                  int n_chars):

        self.i = i
        self._ids = ids
        self._ages = ages
        self._names = names.view('i4')
        self.n_chars = n_chars

    cpdef long32 get_id(self):
        return self._ids[self.i]

    cpdef char set_id(self, long32 id):
        self._ids[self.i] = id

    cpdef char get_age(self):
        return self._ages[self.i]

    cpdef char set_age(self, char age):
        self._ages[self.i] = age

    @property
    def age(self):
        return self._ages[self.i]
    @age.setter
    def age(self, char age):
        self._ages[self.i] = age

    cpdef str get_name(self):
        return <str>np.array(self._names[self.i*self.n_chars:
        (self.i+1)*self.n_chars]).view(dtype='U{}'.format(self.n_chars))

    cpdef char set_name(self, str name):
        buf = np.array(self._names[self.i*self.n_chars:
        (self.i+1)*self.n_chars], copy=False).view(dtype='U{}'.format(self.n_chars))
        buf[:]= name

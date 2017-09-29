# -*- coding: utf-8 -*-
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: embedsignature=True


import numpy as np
cimport numpy as np
oldsettings = np.seterr(divide='ignore')

from .numpy_types import typedict
from .numpy_types cimport np_floating, np_numeric
from .array_descriptors import ArrayDescriptor

from .configure_logger import get_logger

cimport cython
cdef extern from "numpy/npy_math.h":
    bint npy_isnan(double x) nogil


cdef class ArrayShapes(object):
    """
    Base Class for a Cython cdef class which helps to handle
    memoryviews better
    """
    dtypes = {}

    def __cinit__(self, *args, **kwargs):
        """init the file"""
        for cls in self.__class__.__mro__:
            self._search_memview(cls)

    def __init__(self, *args, **kwargs):
        """
        inits the Array and creates the constands for NAN and NINF
        """
        # cdef class has to be subclassed in python
        if not hasattr(self, '__module__'):
            msg = "don't instantiate cdef class directly, please subclass in python class"
            raise NotImplementedError(msg)


        # super class has to be called even if the super class of ArrayShapes
        # is only `object'`
        super(ArrayShapes, self).__init__(*args, **kwargs)
        # set NAN-Values
        self.NAN_f = np.NAN #np.float32(0) / np.float32(0)
        self.INF_f = np.float32(1) / np.float32(0)
        self.NINF_f = np.float32(-1) / np.float32(0)

        self.NAN_d = np.NAN #np.float64(0) / np.float64(0)
        self.INF_d = np.float64(1) / np.float64(0)
        self.NINF_d = np.float64(-1) / np.float64(0)

        # create Class logger
        self.logger = get_logger(self)

    cdef public char isnan(self, np_floating x) nogil:
        """check for nan"""
        return npy_isnan(x)

    def isnan_py(self, np_numeric x):
        """python wrapper around isnan()"""
        return bool(self.isnan(float(x)))

    @cython.initializedcheck(False)
    cpdef _search_memview(self, cls):
        """
        Search the memoryviews in the class cls
        and determine their dtype by trial and error

        Parameters
        ----------
        cls : the subclass to check for memorytypes
        """
        for name, attr in cls.__dict__.items():
            if not name.startswith('__'):
                if name.startswith('_'):
                    try:
                        attr = getattr(self, name)
                        ismemview = [cl.__name__.endswith('memoryview')
                                     for cl in attr.__class__.mro()]
                    except AttributeError as err:
                        if str(err) == 'Memoryview is not initialized':
                            ismemview = [True]
                        else:
                            raise
                    if any(ismemview):
                        prop_name = name[1:]
                        self._init_array(prop_name, (0,))

    @cython.initializedcheck(False)
    def _init_array(self, name, shape0=None, default=None):
        """
        Inits the attribute name with an empty array with the specified shape
        the dtype is inferred from the definition of the attribute

        Parameters
        ----------
        name : str
            the name of the array (without leading underscore)
        shape0 : tuple, optional
            the shape of the array that should be initialized
        default : number, optional
            the default value to fill the created array
            if None, an empty array is created
        """
        intern_name = '_%s' % name
        if shape0 is None:
            shape = (0,)
        elif not isinstance(shape0, tuple):
            shape = (int(shape0), )
        else:
            shape = shape0
        ndim = len(shape)
        np_dtype = 'f4'
        arr = np.empty(shape, dtype=np_dtype)
        try:
            setattr(self, intern_name, arr)

        except ValueError as err:
            msg = str(err)
            if msg.startswith('Buffer has wrong number of dimensions'):
                arr = self._change_ndims(msg, shape, np_dtype)
                ndim = arr.ndim
                try:
                    setattr(self, intern_name, arr)
                except ValueError as err:
                    msg = str(err)
                    if msg.startswith('Buffer dtype mismatch'):
                        arr, np_dtype = self._change_dtype(msg, arr.shape,
                                                           default)
                        ndim = arr.ndim
                        setattr(self, intern_name, arr)
                    else:
                        raise

            elif msg.startswith('Buffer dtype mismatch'):
                arr, np_dtype = self._change_dtype(msg, arr.shape, default)
                #print intern_name, arr.dtype, np_dtype, arr.itemsize
                #print msg
                try:
                    setattr(self, intern_name, arr)
                except ValueError as err:
                    print(err)
                    raise err
            else:
                raise
        self.dtypes[name] = ArrayDescriptor(name, np_dtype, ndim)

    def _change_ndims(self, msg, shape, np_dtype):
        """
        according to the error message received the number of dimensions
        is changed and a new array returned
        Parameters
        ----------
        msg : str
            the message raised by the Exeption
        shape : tuple
            the shape of the array to create
        np_dtype : str
            the numpy-dtype of the array to create

        Returns
        -------
        arr : np.array
            the data with the changed datatype
        """
        cndim = int(msg.split("expected ")[1].split(", got")[0])
        shape = tuple([0] * cndim)
        arr = np.empty(shape, dtype=np_dtype)
        return arr

    def _change_dtype(self, msg, shape, default):
        """
        according to the error message received the dtype is changed
        and a new array returned

        Parameters
        ----------
        msg : str
            the message raised by the Exeption
        shape : tuple
            the shape of the array to create
        default : number
            the default value to fill the array

        Returns
        -------
        arr : np.array
            the data with the changed datatype
        np_dtype : str
            the numpy datatype
        """
        cdtype = msg.split("expected '")[1].split("' but got")[0]
        np_dtype = typedict[cdtype]
        arr = np.empty(shape, dtype=np_dtype)
        if default is not None:
            arr.fill(default)
        return arr, np_dtype

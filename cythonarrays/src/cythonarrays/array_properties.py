# -*- coding: utf-8 -*-

import numpy as np
from cythonarrays.configure_logger import get_logger


class _ArrayProperties(object):
    def __init__(self, *args, **kwargs):
        """
        create properties for all arrays
        """
        for descr in self.dtypes.values():
            prop = self._create_prop(descr)
            setattr(self.__class__, descr.name, prop)
            # create Class logger
            self.logger = get_logger(self)

    def _create_prop(self, descr):
        """
        Create the property name that reads and writes
        the internal attribute _name
        """
        intern_name = '_%s' % descr.name

        def fget(self):
            arr = getattr(self, intern_name)
            return np.array(arr, copy=False).view(dtype=descr.dtype_numpy)

        def fset(self, value):
            self.set_array(descr.name, value)

        def fdel(self):
            self.set_array(descr.name, np.empty(tuple([0]*descr.ndim)))

        fdoc = str(descr)
        prop = property(fget, fset, fdel, fdoc)
        return prop

    def init_array(self, name, shape=None, default=None):
        """
        Inits the attribute name with an empty array with the specified shape
        and fill with the default value

        Parameters
        ----------
        name : str
            the name of the attribute
        shape : tuple, optional
            the shape of the dtype. If not given,
            the dtype stored in self.dtypes is used.
            if None, an array of shape [0] * ndim is initialized
        default : number, optional
            the default value. If not given,
            the default value stored in self.dtypes is used.
            if None, an empty array is initialized
        """
        descr = self.dtypes[name]
        if shape is not None:
            descr.shape = shape
        if default is not None:
            descr.default = default
        if descr.shape is not None:
            self.check_ndims(descr)
            target_shape = descr.get_shape(self)
            arr = np.empty(target_shape, dtype=descr.dtype)
            if descr.default is not None:
                arr.fill(descr.default)
        else:
            arr = np.empty([0] * descr.ndim, dtype=descr.dtype)
        self.set_array(name, arr)

    def set_array(self, name, value, shape=None):
        """
        Sets the attribute name to the value and casts to the correct dtype
        if necessary

        Parameters
        ----------
        name : str
            the name of the attribute to set
        value : Array-like
            the value to assign to the memoryview
        shape : tuple (optional)
            a tuple of ints or str to validate the shape of the array provided

        Examples
        --------
          >>> arr = XArray([5, 7, 5, 8], dtype='u1')
          >>> shape = ('n_agents', )
          >>> model.n_agents
          4
          >>> model.set_array('age', arr, shape)
          >>> model.n_agents = 5
          >>> model.set_array('age', arr, shape)
          Exception...
          >>> shape = (4, )
          >>> model.set_array('age', arr, shape)
        """
        intern_name = '_%s' % name
        descr = self.dtypes[name]
        if shape is not None:
            descr.shape = shape
            self.check_ndims(descr)
        arr2 = descr.validate_array(value, self)
        arr = arr2
        setattr(self, intern_name, arr)

    def reset_array(self, name):
        """Reset array to default value"""
        descr = self.dtypes[name]
        default = descr.default
        getattr(self, name).fill(default)

    def check_ndims(self, descr):
        if len(descr.shape) != descr.ndim:
            msg = '{ndim} Dimensions required, shape {s} has {n} dimensions'
            raise ValueError(msg.format(ndim=descr.ndim,
                                        s=descr.shape, n=len(descr.shape)))

    def init_arrays(self):
        for name in self.dtypes:
            self.init_array(name)

# -*- coding: utf-8 -*-

from typing import Tuple, Union, Iterable
import numpy as np
from numpy.testing import assert_array_equal


class ArrayDescriptor(object):
    """
    describes an array used as an instance attribute of a cython class
    """
    def __init__(self,
                 name: str,
                 dtype: str,
                 ndim: int,
                 shape: Tuple[Union[int, str]]=None,
                 dtype_numpy: str=None,
                 default=None):
        """
        Parameters
        ----------
        name :
            the name of the array
        dtype : str
            the numpy-dtype of the array for internal storage
        ndim : int
            the number of dimensions of the array
        shape :
            the shape of the array
        dtype_numpy :
            the numpy-dtype of the array that should be returned
        default : number
            the default value
        """
        self.name = name
        self.dtype = dtype
        self.ndim = ndim
        self.shape = shape
        self._dtype_numpy = dtype_numpy
        self.default = default

    def __repr__(self):
        txt = 'array {0.name} of dtype {0.dtype}, ndim {0.ndim}'
        if self.shape is not None:
            txt += ' and shape {0.shape}'
        return txt.format(self)

    @staticmethod
    def to_dim(arr, ndim: int) -> np.ndarray:
        """
        Casts the array to ndim dimensions

        Parameters
        ----------
        ndim :
            if self.ndim > ndim and the shape of the first axis <> 0:
            raise ValueError

        Returns
        -------
        :
            array of ndim dimensions
        """

        dim_diff = ndim - arr.ndim
        if dim_diff > 0:
            return arr.__getitem__((np.newaxis, ) * dim_diff)
        elif dim_diff < 0:
            dim_diff *= -1
            if arr.shape[:dim_diff] == tuple([1] * dim_diff):
                new_shape = arr.shape[dim_diff:]
                return arr.reshape(new_shape)
            else:
                msg = f'cannot reshape shape {arr.shape} to {ndim} dimensions'
                raise ValueError(msg)
        else:
            return arr

    def validate_array(
        self,
        arr: np.ndarray,
        instance=None) -> np.ndarray:
        """
        checks if the ndim (and the shape, if specified) match
        and casts the array to the dtype specified

        Parameters
        ----------
        arr:
            the array to test
        instance: ArrayShapes
            the CDefClass-instance holding the information on the allowed shapes

        Returns
        -------
        :
            the validated array casted to the target dimension and dtype
        """
        # cast arr to numpy array
        if not isinstance(arr, np.ndarray):
                arr = np.array(arr)
        msg = f'{self.name}: ndim target: {self.ndim}, actual: {arr.ndim}'
        # if ndim does not match
        try:
            assert self.ndim == arr.ndim, msg
        except AssertionError as err:
            # try to add additional dimensions
            try:
                arr = self.to_dim(arr, self.ndim)
            except ValueError:
                raise err
        if self.shape is not None:
            shape = self.get_shape(instance)
            msg = f'{self.name}: shape target: {shape}, actual: {arr.shape}'
            assert_array_equal(arr.shape, shape, msg)

        # convert bool array to i1 with view instead of astype
        if issubclass(arr.dtype.type, np.bool_):
            new_type = np.dtype(self.dtype).type
            if issubclass(new_type, np.int8):
                return arr.view(dtype='i1')
            elif issubclass(new_type, np.uint8):
                return arr.view(dtype='u1')

        return arr.astype(self.dtype, copy=False)

    def get_shape(self,
                  instance=None) -> Tuple[int]:
        """
        get the shape of the array defined by the ArrayDescriptor
        using the information from the ArrayShape-instance

        Parameters
        ----------
        instance: ArrayShapes
            the CDefClass-instance holding the information on the allowed shapes

        Returns
        -------
        :
            a tuple with the shape
        """
        shape = []
        for d in range(self.ndim):
            if isinstance(self.shape[d], str):
                v = getattr(instance, self.shape[d])
            else:
                v = self.shape[d]
            shape.append(v)
        return shape

    @property
    def dtype_numpy(self) -> str:
        """return the numpy dtype"""
        if self._dtype_numpy is None:
            return self.dtype
        else:
            return self._dtype_numpy

    @property
    def shape(self) -> Tuple[Union[str, int]]:
        """the shape of the array described, with numbers or strings

        Parameters
        ----------
        value: Union[int, str, bytes, Tuple[Union[int, str]]]
            the setter can receive the shape provided as a number, a string
            (comma separated for several dimensions) or a tuple/list of strings or ints
        """
        return self._shape

    @shape.setter
    def shape(self, value: Union[int, str, bytes, Tuple[Union[int, str]]]):
        """
        convert the shape to a tuple

        Parameters
        ----------
        value:
            the shape provided as a number, a string
            (comma separated for several dimensions) or a tuple/list of strings or ints
        """
        if isinstance(value, (np.int, np.long)):
            value = (value, )
        elif isinstance(value, (str, bytes)):
            splitted = value.split(',')
            value = []
            for s in splitted:
                # strip whitespace
                st = s.strip()
                try:
                    value.append(int(st))
                except ValueError:
                    value.append(st)
        self._shape = value

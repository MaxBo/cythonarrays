Purpose of Cythonarrays
=======================

Cython is a great tool to write Code at C-Speed.

Numpy is a great tool to work with arrays.

xarray is a great package to work with a set of arrays with named dimensions.

The purpose of the cythonarrays package is to make writing cdef-Classes in cython easyer, safer and more convenient by linking to numpy and xarray.

It consists of the following components:

cythoninstallhelpers
--------------------

this package provides some help for compiling cython classes that use numpy and openmp. Frequently used code can be imported in the setup.py the .pyxbld files.
It includes:

* build_config.py : ensure that numpy and openmp is correctly linked in the cython file by using a .pyxbld-file 
												 
* make_cython_extensions.py : use make_extensions(list_of_extention_module_names) in the setup.py to define ext_modules

* get_version.py : import the version number from a _version.py file with

cythonarrays
------------
this package provides base classes for cdef-Cython-Classes.

You create a cyton cdef-class with memoryviews and subclass this class in a python-class.
The python class converts the memoryviews into numpy arrays. In addition, it wraps the arrays into an `xarray <http://xarray.pydata.org>`_-class. If you set arrays with numpy-arrays, they are validated in terms of shape and dtype. cdef-methods on the cython-class can manipulate the data at c-speed.


How to work with Cythonarrays CDef-Classes
==========================================


link numpy and openmp sources
-----------------------------
In order to use Cython with numpy, the numpy sources have to be linked to the Cython code.

One way is to use for each Cython module 4 files:

* mymodule_cython.pyx : The actual Cython code

* mymodule_cython.pxd : The header files with the definition of all Classes and its attributes and methods

* mymodule_cython.pyxbld : the compiler directives

* mymodule.py : a python module, that imports the cython code and wraps it to normal python modules

the .pyxbld file will import helpers from cythoninstallhelpers::

  from cythoninstallhelpers.build_config import (extra_compile_args,
                                                 extra_link_args,
                                                 make_ext,)

      
This tells the compiler to use the platform specific openmp-libraries and to include the numpy dirs.

Cython cdef classes
-------------------

Cython cdef classes are extension types for cython.

All methods and class attributes, that should be used with C-Speed have to by defined.
This can be done in the declaration .pxd file::

  cdef class MyCythonClass(object):
      """A Cython class"""
      cdef unsigned long i, j
      cdef public float U
      cdef readonly double result
      
      cpdef double calc_result(self, float U)
      cdef calc_p(self, unsigned long i, unsigned long j) nogil
      
Class attributes defined as **public** are also readable and writable from Python.

Class attributes defined as **readonly** are readable from Python but not writable.

Class attributes defined without a **public** or **writable** flag are only accessible from within a cdef-Cython function.

Methods defined as cdef are only accessible from other class methods.

Methods defined as cpdef are also usable as python classes.

If the method is defined as **nogil**, then they can be used within a parallel calculation at C-speed.

This method does not need the "Global Interpreter Lock" (GIL). So a method can only be **nogil**, 
if no python attributes or methods are used within the function and only other **nogil** functions are called.

A cpdef method cannot be **nogil** at the same time. 

A **nogil** function cannot return nothing, so specify at least a return type like char.


memoryviews and numpy arrays
----------------------------
A comfortable way to work with numpy arrays in cdef classes is the following:

* the cdef class holds an memoryview on the data as an attribute
  the memoryview can be accessed in C-Speed from within cython functions

* from python the data is accessible as a normal numpy array

To facilitate this, the Cython module array_shapes.pyx and the Python moduls array_types have been written.

Let your Cython class inherit from ArrayShapes.
     from cythonarrays.array_shapes cimport ArrayShapes
     from cythonarrays.array_shapes import ArrayShapes
import the numpy array types::

     from cythonarrays.numpy_types cimport *

specify all arrays that you need in the mymodule_cython.pxd-file with a leading underscore::

  cdef class _Example(ArrayShapes):
      cdef public ARRAY_2D_f _myfloatarr
      cdef public ARRAY_3D_i4 _myintarr
      cdef public ARRAY_1D_d _mydoublevector
      
      cdef public int n_rows, n_blocks, n_cols
      

In the mymodule_cython.pyx-file, add a __cinit__ method::

  cdef class _MyCythonClass(ArrayShapes):
    def __cinit__(self, *args, **kwargs):
        """init the file"""
        for cls in self.__class__.__mro__:
            self.search_memview(cls)
 
the method search_memview(cls) searches all memoryviews in the class and the base class.

  
Create a wrapper Python class in a python module mymodule.py, that inherits from _MyCythonClass and from the Python-Class _ArrayProperties::

  import pyximport
  pyximport.install()
  from mymodule_cython import _MyCythonClass
  from cythonarrays.array_properties import _ArrayProperties
  
  class MyClass(_MyCythonClass, _ArrayProperties):
      def __init__(self, n_rows, n_cols, n_blocks, *args, **kwargs):
          super(MyCythonClass, self).__init__(*args, **kwargs)
          self.n_rows = n_rows
          self.n_cols = n_cols
          self.n_blocks = n_blocks
      
This creates automatically properties for a comfortable access to the array::

  >>> myinstance = MyClass(n_rows=4, n_cols=5, n_blocks=6)

The array can be initialised by::

  >>> shape = ('n_blocks', 'n_rows', 'n_cols')
  >>> myinstance.init_array('myintarr', shape, default=-1) 
  >>> shape = (6, )
  >>> myinstance.init_array('mydoublevector', shape) 
  
  or with some data::
  
  >>> arr = np.random.random((4, 5)).astype('f8')
  >>> shape = ('n_rows', 'n_cols')
  >>> myinstance.set_array('myfloatarr', arr, shape)

In this case, the dtype is automatically casted to the target type of the class attribute (in this case: f4).
And the shape is checked. If the shape does not match, an error is raised.
The Data is accessible form Python via::

  >>> intarr = myinstance.myintarr
  >>> intarr.dtype
  int32
  >>> intarr.shape
  (6, 4, 5)
  >>> intarr[2, 2:4, 1]
  array([-1, -1])
  >>> intarr[0] *= 2
  
and from within a cython function::

  cdef class _MyCythonClass(_ArrayShapes):
    cpdef sum_mult_by_block(self):
       cdef int block, row, col
       cdef double res
       for block in range(self.n_blocks):
           res = 0
           for row in range(self.n_rows):
               for col in range(self.n_cols):
                   res += self._myintarr[block, row, col] * self._myfloatarr[row, col]
           self._mydoublevector[block] = res
           
  >>> myinstance.sum_mult_by_block()
  >>> myinstance._mydoublevector
  array([-40., -20., -20., -20., -20., -20.])
  

You can define an Array within a cdef function::

  cdef class _MyCythonClass(_ArrayShapes):
    cpdef sum_mult_by_block(self):
       cdef int block, row, col
       cdef ARRAY_1D_d vec = self._mydoublevector
       cdef double res
       for block in range(self.n_blocks):
           res = 0
           for row in range(self.n_rows):
               for col in range(self.n_cols):
                   res += self._myintarr[block, row, col] * self._myfloatarr[row, col]
           vec[block] = res
           
but don't do that in a subfunction, that is called many times, because assigning memory to the variable *vec* a costly operation.


Link Cythonarrays-Class to xarray-Dataset
=================================

You can create an `xarray-Dataset <http://xarray.pydata.org/en/stable/>`_ which infers the dimensions, coordinates, and data variables from the cdef-class.

  >>> example = Example()
  >>> example.create_ds()
  >>> print(example.ds)
  <xarray.Dataset>
  Dimensions:             (destinations: 3, dim_0: 0, dim_1: 0, groups: 2, origins: 3)
  Coordinates:
    * destinations        (destinations) int32 100 200 300
    * groups              (groups) object 'Female' 'Male'
    * origins             (origins) int32 100 200 300
  Dimensions without coordinates: dim_0, dim_1
  Data variables:
      param_g             (groups) float64 -0.2 -0.1
      trips_ij            (origins, destinations) float64 29.02 31.86 39.12 ...
      groupnames_g        (groups) object 'Female' 'Male'
      not_initialized_ij  (dim_0, dim_1) int32 
      persons_gi          (groups, origins) float64 100.0 0.0 200.0 0.0 250.0 50.0
      zonenumbers_i       (origins) int32 100 200 300
      jobs_j              (destinations) float64 100.0 200.0 300.0
      km_ij               (origins, destinations) float64 1.0 4.0 5.0 2.0 1.0 ...

xarray-Dataset is linked to cython class
----------------------------------------

The Data variables of the xarray-Dataset share the same memory with the attributes of the cdef-Cython-Class.
So when a cdef function modifies a value  in example._trips_ij

  >>> self._trips_ij[1, 2] = 99
  
then the value is changed directly in the xarray-Dataset

  >>> print(self.ds.trips_ij.values[1, 2])
  99.0





  

Validation of Data in cythonarrays
==================================

The pxd-file example_cython.pxd imports shortcuts for memoryviews and the base class ArrayShapes::

  from cythonarrays.numpy_types cimport *
  from cythonarrays.array_shapes cimport ArrayShapes

Then it defines the cdef-class _Example, that inherits from ArrayShapes.

It will have the coordinates groups, origins, and destinations.

Paralell loops will use n_threads.

It defines different memoryviews of 1 and 2 dimensions and dtypes i4 (4-byte integer) und d (double).

These memoryviews start with a leading underscore. 

In the Python-Class these arrays will be exposed later without the leading underscore as numpy arrays.

The suffix *g* and *i* in *_persons_gi* help later to use the right variables (self._persons_gi[g, i] = ...)

The cdef class will define a method *calc_model* which can be called from python and cython that returns -1 if an exeption occurs

The cdef class defines two methods *_calc_weight_destination* and *_calc_weight_destination* which can be called only from cython.

Nogil means that these methods can be called in parallel threads where the global intepreter lock (gil) has been released::

  cdef class _Example(ArrayShapes):
      """
      Cython CDefClass for Example model
      with coordinates groups, origins, and destinations
      """
      cdef public long32 groups
      cdef public long32 origins
      cdef public long32 destinations
      cdef public char n_threads


      cdef public ARRAY_1D_i4 _zonenumbers_i

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

The cython-module example_cython.pyx implements these methods. 

It uses the __cinit__-method to search for all memoryviews defined in its .pxd-file and expose all of them, which start with a leading underscore, as numpy arrays::

  cdef class _Example(ArrayShapes):
      @cython.initializedcheck(False)
      cpdef char calc_model(self) except -1:
          """
          Calc the daily trips for all groups and zones
          """
          cdef char t
          cdef long32 g
          self.reset_array('trips_ij')
          with nogil, parallel(num_threads=self.n_threads):
              t = threadid()
              # loop over groups
              for g in prange(self.groups, schedule='guided'):
                  with gil:
                      self.logger.info('calculate group {}'.format(g))
                  # calc destination choice
                  self._calc_p_destination(g)
	  
Now the cython and cpdef methods are implemented. 

In the example, it uses parallel threads to calculate the model for different groups. 

Within the parallel sessions, pure python-methods like a logging function can be called by temporarily using the gil (global interpreter lock).

The ArrayShape-class defines a logger which is bound to the cdef-class.

To reset the memoryview to its default values, the self.reset_array('trips_ij') is used.::

  import numpy as np
  from cythonarrays.tests.example_python import Example

    km_ij = np.array([[1, 4, 5],
                      [2, 1, 7],
                      [5, 7, 2]])
    jobs = np.array([100, 200, 300])
    params_groups = np.array([-0.2, -0.1])
    persons_gi = np.array([[100, 0, 200],
                           [0, 250, 50]])


    groups, zones = persons_gi.shape
    example = Example(groups, zones)
    example.set_array('km_ij', km_ij)
    example.set_array('jobs_j', jobs)
    example.set_array('param_g', params_groups)
    example.set_array('persons_gi', persons_gi)
    return example

	
	
	
    tempfile_h5 = tempfile.mktemp(suffix='h5')


class Test01_ExampleCDefClass:
    """Test the Example CDefClass"""
    def test_01_test_init_array(self, persons_gi):
        """Test the Example CDefClass creation"""
        groups, zones = persons_gi.shape
        example = Example(groups, zones)

        # set correct shape
        values = np.arange(zones)
        example.set_array('jobs_j', np.arange((zones)))
        np.testing.assert_array_equal(example.jobs_j, values)
        np.testing.assert_array_equal(example._jobs_j, values)

        # init the array with a default value
        example.init_array('jobs_j', default=0)
        np.testing.assert_array_equal(example.jobs_j, np.zeros(zones))

        # init the array with the other default value
        example.init_array('jobs_j', default=2)
        np.testing.assert_array_equal(example.jobs_j, np.full(zones, 2))

        # new default value will be stored
        example.reset_array('jobs_j')
        np.testing.assert_array_equal(example.jobs_j, np.full(zones, 2))

        # set new shape, keep old default value
        example.init_array('jobs_j', shape='groups')
        np.testing.assert_array_equal(example.jobs_j, np.full(groups, 2))

    def test_02_test_shape(self, persons_gi):
        """
        Test if the shapes of array are controlled correctly
        """
        groups, zones = persons_gi.shape
        example = Example(groups, zones)

        # jobs_j should have the shape (zones)

        # correct shape
        arr = np.ones((zones))
        example.jobs_j = arr

        # try to set values with the wrong shape
        arr = np.ones((groups))
        message = """
Arrays are not equal
jobs_j: shape soll: [3], ist: (2,)
(mismatch 100.0%)
 x: array([2])
 y: array([3])
        """
        with pytest.raises(AssertionError,
                           message=message):
            example.jobs_j = arr

        # change zones and try again
        example.destinations = groups
        # now the array fits to the shape defined
        example.jobs_j = arr

    def test_03_test_dimensions(self, persons_gi):
        """Test the dimensions"""
        groups, zones = persons_gi.shape
        example = Example(groups, zones)

        # try to set shape with the wrong number of dimensions
        msg = "builtins.ValueError: 1 Dimensions required, shape ['groups', 'zones'] has 2 dimensions"
        with pytest.raises(ValueError,
                           message=msg):
            example.init_array('jobs_j', shape='groups, zones')

        # access a non-initialized array
        target = np.empty((0, 0))
        actual = example.not_initialized_ij
        np.testing.assert_array_equal(actual, target)

        # set arbitrary values to non-initialized 2D-Array
        a = np.array([2, 3, 4])
        # with less dimensions than required ...
        example.not_initialized_ij = a
        b = example.not_initialized_ij
        # another dimension is added
        assert b.ndim == 2
        assert b.shape == (1, 3)

        # change value in cython-memoryview
        example._not_initialized_ij[0, 1] = 99
        target = np.array([[2, 99, 4]])
        # the value will be changed in the numpy-view of the array
        np.testing.assert_array_equal(example.not_initialized_ij, target)
        # as this is a view on the input-data, it will be changed there, too
        np.testing.assert_array_equal(a[1], 99)

        # the right number of dimensions should be fine
        c = np.array([[0, 1],
                      [2, 3]])
        example.not_initialized_ij = c
        d = example.not_initialized_ij
        np.testing.assert_array_equal(c, d)

        # too many dimensions will raise an error
        e = np.array([[[0, 1],
                       [2, 3]],
                      [[4, 5],
                       [6, 7]]])
        with pytest.raises(AssertionError,
                           message="not_initialized_ij: ndim soll: 2, ist: 3"):
            example.not_initialized_ij = e

        # when the dimensions can be reduced to the target dimensions,
        # it should be fine
        f = np.array([[[0, 1],
                       [2, 3]]])
        example.not_initialized_ij = f
        g = example.not_initialized_ij
        np.testing.assert_array_equal(g, f[0])

        # change value in cython-memoryview
        example._not_initialized_ij[1, 1] = 88
        target = np.array([[0, 1],
                           [2, 88]])
        # the value will be changed in the numpy-view of the array
        np.testing.assert_array_equal(example.not_initialized_ij, target)
        # as this is a view on the input-data, it will be changed there, too
        np.testing.assert_array_equal(f[0, 1, 1], 88)

    def test_04_test_dtype(self, persons_gi):
        """Test the dimensions"""
        groups, zones = persons_gi.shape
        example = Example(groups, zones)

        # dtype of jobs_j: f8
        # dtype of not_initialized_ij: i4
        # dtype of n_threads: char

        # test if n_threads is really a signed char
        example.n_threads = 127
        assert example.n_threads == 127

        with pytest.raises(OverflowError,
                           message='value too large to convert to char'):
            example.n_threads = 128

        # test if jobs_j is really an array of double precision
        arr_i4 = np.array([2, 3, 4], dtype='i4')
        example.jobs_j = arr_i4
        assert example.jobs_j.dtype == np.dtype('f8')
        # because the array set to jobs_j is of different dtype,
        # it had to be converted to double. So no view is used,
        # but a copy of the data
        arr_i4[1] = -1
        # the data in jobs_j stays untouched
        assert example.jobs_j[1] == 3

        # test if not_initialized_ij is really an array of 32bit integer
        arr_i4 = np.array([[2, 3, 4], [5, 6, 7]], dtype='i4')
        example.not_initialized_ij = arr_i4
        assert example.not_initialized_ij.dtype == np.dtype('i4')
        # because the array set to not_initialized_ij is of the same dtype,
        # a view on the data could have been used
        arr_i4[1, 2] = -1
        # the data in not_initialized_ij changes
        assert example.not_initialized_ij[1, 2] == -1

    def test_10_test_model(self, example):
        """Test the Example CDefClass model"""
        res = example.calc_model()
        print(example.trips_ij)
        total_trips_target = example.persons_gi.sum()
        total_trips_actual = example.trips_ij.sum()
        np.testing.assert_almost_equal(total_trips_target, total_trips_actual)

    def test_11_dataset(self, example):
        """Test the creation of an xarrays Dataset linked to the Cythonclass"""
        example.zonenumbers_i = np.array([100, 200, 300])
        example.groupnames_g = np.array(['Female', 'Male'], dtype='O')
        example.create_ds()
        print(example.ds)

    def test_20_save_and_read_ds(self, example, tempfile_h5):
        """Test that saving and re-reading the data works"""
        example.zonenumbers_i = np.array([100, 200, 300])
        example.groupnames_g = np.array(['Female', 'Male'], dtype='O')
        example.create_ds()
        example.save_dataset_to_netcdf(tempfile_h5)

        # read the data into new class
        new_example = Example.from_netcdf(tempfile_h5)
        # assert that the data match
        np.testing.assert_array_equal(example.jobs_j, new_example.jobs_j)
        np.testing.assert_array_equal(example.groupnames_g,
                                      new_example.groupnames_g)

        # assert, that the array are correctly linked to the Dataset
        new_example.calc_model()
        old_value = new_example.ds.trips_ij.sum()
        # calculate the model with 77 persons more
        new_example.persons_gi[1, 0] += 77
        new_example.calc_model()
        new_value = new_example.ds.trips_ij.sum()
        np.testing.assert_allclose(old_value + 77, new_value)

        print(new_example.ds)

if __name__ == '__main__':
    pytest.main()

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





  
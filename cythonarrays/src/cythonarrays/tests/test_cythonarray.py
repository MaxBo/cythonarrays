# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import numpy as np
import pytest

from cythonarrays.tests.example_python import Example


@pytest.fixture(scope='class')
def km_ij(request):
    """
    travel times
    """
    array = np.array([[1, 4, 5],
                      [2, 1, 7],
                      [5, 7, 2]])
    return array


@pytest.fixture(scope='class')
def jobs(request):
    """
    jobs
    """
    jobs = np.array([100, 200, 300])
    return jobs


@pytest.fixture(scope='class')
def params_groups(request):
    """
    different values for saving categories
    """
    return np.array([-0.2, -0.1])


@pytest.fixture(scope='class')
def persons_gi(request):
    """
    different values for home zone
    """
    arr = np.array([[100, 0, 200],
                    [0, 250, 50]])
    return arr


@pytest.fixture(scope='class')
def example(km_ij, jobs, params_groups, persons_gi):
    """
    different values for home zone
    """
    n_groups, n_zones = persons_gi.shape
    example = Example(n_groups, n_zones)
    example.set_array('km_ij', km_ij)
    example.set_array('jobs_j', jobs)
    example.set_array('param_g', params_groups)
    example.set_array('persons_gi', persons_gi)
    return example


class Test01_ExampleCDefClass:
    """Test the Example CDefClass"""
    def test_01_test_init_array(self, persons_gi):
        """Test the Example CDefClass creation"""
        n_groups, n_zones = persons_gi.shape
        example = Example(n_groups, n_zones)

        # set correct shape
        values = np.arange(n_zones)
        example.set_array('jobs_j', np.arange((n_zones)))
        np.testing.assert_array_equal(example.jobs_j, values)
        np.testing.assert_array_equal(example._jobs_j, values)

        # init the array with a default value
        example.init_array('jobs_j', default=0)
        np.testing.assert_array_equal(example.jobs_j, np.zeros(n_zones))

        # init the array with the other default value
        example.init_array('jobs_j', default=2)
        np.testing.assert_array_equal(example.jobs_j, np.full(n_zones, 2))

        # new default value will be stored
        example.reset_array('jobs_j')
        np.testing.assert_array_equal(example.jobs_j, np.full(n_zones, 2))

        # set new shape, keep old default value
        example.init_array('jobs_j', shape='n_groups')
        np.testing.assert_array_equal(example.jobs_j, np.full(n_groups, 2))

    def test_02_test_shape(self, persons_gi):
        """
        Test if the shapes of array are controlled correctly
        """
        n_groups, n_zones = persons_gi.shape
        example = Example(n_groups, n_zones)

        # jobs_j should have the shape (n_zones)

        # correct shape
        arr = np.ones((n_zones))
        example.jobs_j = arr

        # try to set values with the wrong shape
        arr = np.ones((n_groups))
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

        # change n_zones and try again
        example.n_zones = n_groups
        # now the array fits to the shape defined
        example.jobs_j = arr

    def test_03_test_dimensions(self, persons_gi):
        """Test the dimensions"""
        n_groups, n_zones = persons_gi.shape
        example = Example(n_groups, n_zones)

        # try to set shape with the wrong number of dimensions
        with pytest.raises(ValueError,
                           message="builtins.ValueError: 1 Dimensions required, shape ['n_groups', 'n_zones'] has 2 dimensions"):
            example.init_array('jobs_j', shape='n_groups, n_zones')

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
        n_groups, n_zones = persons_gi.shape
        example = Example(n_groups, n_zones)

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

        # test if not_initialized_ij is really an array of double precision
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


if __name__ == '__main__':
    pytest.main()
# -*- coding: utf-8 -*-

import multiprocessing
import xarray as xr
import os

from cythonarrays.array_properties import _ArrayProperties
from cythonarrays.converters.xarray2netcdf import xr2netcdf
import pyximport; pyximport.install()
from cythonarrays.tests.example_cython import (_Example, ExampleAgent)


class Example(_Example, _ArrayProperties):
    """Example python class inheriting from cython"""

    def __init__(self,
                 n_groups,
                 n_zones,
                 n_chars=2,
                 threading=True):
        super().__init__()

        self.n_zones = n_zones
        self.n_groups = n_groups
        self.n_chars = n_chars
        self.set_n_threads(threading)

        self.define_arrays()
        self.init_arrays()

    def set_n_threads(self, threading=True):
        """Set the number of threads"""
        if threading:
            self.n_threads = min(multiprocessing.cpu_count(), self.n_groups)
        else:
            self.n_threads = 1

    @classmethod
    def read_from_netcdf(cls, file):
        """Read an Example Model
        from a set of netcdf-Filename located in folder"""
        # create instance of self
        self = cls(n_groups=0, n_zones=0)
        # add datasets
        self.read_data(file)

        # set the dimensions
        dims = self.data.dims
        self.n_zones = dims['zone_no']
        self.n_groups = dims['groups']
        self.set_n_threads()

        # resize the arrays to the right dimensions
        self.init_arrays()
        self.set_arrays_from_dataset()
        return self

    def set_arrays_from_dataset(self):
        """Sets the arrays with values from the dataset"""
        ds = self.data
        # params
        self.groups = ds.groups.data
        self.zone_no = ds.zone_no.data
        self.results = self.define_results()

    def define_arrays(self):
        """Define the arrays"""
        self.init_array('source_potential_gh', 'n_groups, n_zones')
        self.init_array('trips_gij', 'n_groups, n_zones, n_zones')
        self.init_array('ages', 'n_groups')
        self.init_array('ids', 'n_groups')

    def define_datasets(self):
        """Define the datasets"""
        self.data = self.define_params()
        self.results = self.define_results()

    def define_params(self):
        """Define the params"""
        ds = xr.Dataset()
        ds['source_potential'] = (('groups', 'origins'),
                                  self.source_potential_gh)
        ds['ids'] = (('groups'), self.ids)
        ds['names'] = (('groups'), ['AA', 'BB'])
        ds['ages'] = (('groups'), self.ages)

        return ds

    def define_results(self):
        """Define the results"""
        ds = xr.Dataset()
        # resulting arrays
        #ds['groups'] = self.groups_g
        #ds['origins'] = self.zone_no_h
        #ds['destinations'] = self.zone_no_h
        #ds['zone_no'] = self.zone_no_h
        ds['trips_gij'] = (('groups', 'origins', 'destinations'),
                           self.trips_gij)
        return ds

    def save_data(self, dataset_name, fn):
        """Save Dataset to netcdf-file"""
        ds = getattr(self, dataset_name)
        self.logger.info('write {}'.format(fn))
        dirname = os.path.dirname(fn)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        xr2netcdf(ds, fn)
        ds.close()

    def read_data(self, dataset_name, fn):
        """read single dataset from """
        self.logger.info('read {}'.format(fn))
        ds = xr.open_dataset(fn)
        setattr(self, dataset_name, ds)

#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import xarray as xr


class ReadOFormat(xr.Dataset):
    """reads Matrix from a file
    """
    _target_cols_zones = ['zone_no', 'zone_name']
    _target_cols_matrix = ['origins', 'destinations', 'values']

    def __init__(self,
                 zonefile,
                 matrixfile,
                 cols_zones=None,
                 cols_matrix=None,
                ):
        """
        Parameters
        ----------
        zonefile : str
            the filepath to the file with zone names
        matrixfile : str
            the filepath to the file with the matrix values
        cols_zones : list-like, optional
        cols_matrix : list-like, optional
        """
        super().__init__()
        self.read_zones_csv(zonefile, cols_zones)
        self.read_matrix_csv(matrixfile, cols_matrix)

    def read_matrix_csv(self, filename, cols_matrix):
        """
        Reads a matrix from a csv-file and stores it in self['matrix']

        Parameters
        ----------
        filename : str
            the filepath of the input file
        cols_matrix : list-like
            the columns to use
        """
        target_cols = self._target_cols_matrix
        data_cols = cols_matrix
        pkey = target_cols[:2]

        da = self.read_file_to_da(data_cols, filename, target_cols, pkey)
        self['matrix'] = da['values']
        m = self['matrix']
        m.data[np.isnan(m.data)] = 0

    def read_zones_csv(self, filename, cols_zones):
        """
        Reads a matrix from a csv-file and stores it as coordinates


        Parameters
        ----------
        filename : str
            the filepath of the input file
        cols_matrix : list-like
            the columns to use [column_with_zone_no, column_with_zone_name]
        """
        target_cols = self._target_cols_zones
        data_cols = cols_zones
        pkey = target_cols[0]
        col_name = target_cols[1]

        da = self.read_file_to_da(data_cols, filename, target_cols, pkey)
        dims = self._target_cols_zones[:1] + self._target_cols_matrix[:2]
        # set as origins and destinations
        for dim in dims:
            renamed_da = da.rename({pkey: dim})
            self[dim] = renamed_da[dim]
            name_dim = 'name_{}'.format(dim)
            self.coords[name_dim] = xr.IndexVariable(dims=[dim],
                                                     data=renamed_da[col_name])

    def read_file_to_da(self, data_cols, filename, target_cols, pkey):
        """
        reads a file into a DataArray

        Parameters
        ----------
        data_cols : list-like
        filename : str
        target_cols : list_like
        pkey : str

        Returns
        -------
        da : xarray.DataArray
        """
        df = pd.read_csv(filename, usecols=data_cols)
        if not data_cols:
            # take the first columns of the table
            data_cols = df.columns.values[:len(target_cols)]

        # rename the columns to the target names
        msg = 'wrong number of columns specified'
        assert len(data_cols) == len(target_cols), msg
        rename_cols = dict(zip(data_cols,
                               target_cols))
        df.rename(columns=rename_cols, inplace=True)

        da = df.set_index(pkey).sort_index().to_xarray()
        return da

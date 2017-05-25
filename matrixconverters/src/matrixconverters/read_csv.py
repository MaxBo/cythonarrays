#!/usr/bin/python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
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
        super(ReadOFormat, self).__init__()
        self.read_zones_csv(zonefile, cols_zones)
        self.read_matrix_csv(matrixfile, cols_matrix)

    def read_matrix_csv(self, filename, cols_matrix):
        """
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



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-z', '--zonefile', dest='zonefile', required=True)
    parser.add_argument('-m', '--matrixfile', dest='matrixfile', required=True)
    parser.add_argument('--cols_zones', dest='cols_zones', nargs='*')
    parser.add_argument('--cols_matrix', dest='cols_matrix', nargs='*')

    options = parser.parse_args()
    ds = ReadOFormat(options.zonefile,
                     options.matrixfile,
                     options.cols_zones,
                     options.cols_matrix)
    print(ds)

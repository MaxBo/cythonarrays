# -*- coding: utf-8 -*-

import zlib
from collections import deque
import numpy as np
import xarray as xr
from typing import TextIO, BinaryIO, IO, Iterable, Tuple, List


class ReadPTVMatrix(xr.Dataset):
    """reads PTV-Matrix from file
    the matrix-type is determined by the header
    reades $V, $O, $E, and the binary types $BI, $BK and $B
    """
    __slots__ = ()

    def __init__(self, filename: str):
        """
        read a PTV-Matrix and return it as an xarray-dataset

        Parameters
        ----------
        filename: str
            path to file on disk
        """
        super().__init__()
        self.attrs['fn'] = filename
        self.attrs['ZeitVon'] = 0
        self.attrs['ZeitBis'] = 0
        self.attrs['Faktor'] = 1
        self.attrs['VMAktKennung'] = 0
        self.attrs['AnzBezeichnerlisten'] = 1
        self.attrs['roundproc'] = 1

        with self._openfile(mode='rb') as f:
            line = f.readline().strip()

            errmsg = 'Matrix type not recognised form Header {}'.format(line)

        if line.startswith(b'$') and len(line) > 1:
            # text format
            matrix_type = chr(line[1])
            if line.startswith(b"$"):
                read_methods = {
                    'V': self.readPTVMatrixV,
                    'O': self.readPTVMatrixO,
                    'E': self.readPTVMatrixE,
                    'S': self.readPTVMatrixE,
                }
                read = read_methods.get(matrix_type)
                if not read:
                    raise ValueError(errmsg)
                read()
            else:
                raise ValueError(errmsg)
        else:
            # assume it is the binary format
            self.readPTVMatrixB()

    def readPTVMatrixO(self):
        """read a file in O-Format"""
        with self._openfile(mode="r") as f:
            rows = self.read_header(f)
        loc = self.matrix.loc
        for row in rows:
            r = row.split()
            fr = int(r[0])
            to = int(r[1])
            value = self.float_nan(r[2])
            loc[fr, to] = value

    def readPTVMatrixE(self):
        """read a file in E-Format"""
        with self._openfile(mode="r") as f:
            rows = self.read_header(f)
        loc = self.matrix.loc
        for row in rows:
            cols = row.lstrip('-').split()
            fr = int(cols[0])
            for i in range(1, len(cols), 2):
                to = int(cols[i])
                value = float(cols[i + 1])
                loc[fr, to] = value

    def read_header(self, f: TextIO) -> deque:
        """
        read the header

        Parameters
        ----------
        f : file-obj

        Returns
        -------
        rows: deque
        """
        line = f.readline()
        MatrixTyp = line.split("$")[-1].split(";")[0]
        if "M" in MatrixTyp:
            self.attrs['VMAktKennung'] = self.read_value(f)

        if "N" not in MatrixTyp:
            ZeitVon, ZeitBis, Faktor = self.read_values(f, 3)
            self.attrs['ZeitVon'] = ZeitVon
            self.attrs['ZeitBis'] = ZeitBis
            self.attrs['Faktor'] = Faktor

        rows, line = self.read_values_in_o_format_to_list(f)
        self.read_names_o_format(f, line, rows)
        return rows

    def _openfile(self, mode: str = 'r', encoding: str = 'latin1') -> IO:
        """
        open the file with the according open method

        Parameters
        ----------
        mode : str, optional(default='r')
            read, write or append
        encoding : str, optional(default='latin1')

        Returns
        -------
        open file-handler
        """
        if mode.endswith('b'):
            encoding = None
        return open(self.attrs['fn'], mode=mode, encoding=encoding)

    def readPTVMatrixV(self):
        """read a file in V-Format"""
        with self._openfile() as f:
            line = f.readline()
            MatrixTyp = line.split("$")[-1].split(";")[0]
            if not MatrixTyp.startswith("V"):
                print("Keine Matrix im V-Format!")
                raise TypeError
            if "M" in MatrixTyp:
                self.attrs['VMAktKennung'] = self.read_value(f)

            if "N" not in MatrixTyp:
                ZeitVon, ZeitBis, Faktor = self.read_values(f, 3)
                self.attrs['ZeitVon'] = ZeitVon
                self.attrs['ZeitBis'] = ZeitBis
                self.attrs['Faktor'] = Faktor

            n_zones = self.read_value(f)
            self.create_zones(n_zones)
            self.read_values_to_array(f, self.zone_no)

            self.create_matrix(n_zones)
            self.read_values_to_array(f, self.matrix)
            self.create_zone_names(n_zones)
            self.read_names(f, self.zone_name)

    def create_zone_names(self,
                          n_zones: int,
                          name: str = 'zone_name',
                          dim: str = 'zone_no'):
        coord = getattr(self, dim).data
        self[name] = xr.DataArray(
            np.empty((n_zones, ), dtype='O'),
            coords=(coord, ),
            dims=(dim,),
            name=name,)

    def create_matrix(self,
                      n_zones: int,
                      n_cols: int = None,
                      dtype: str = 'f8'):
        n_cols = n_cols or n_zones
        origins = self.zone_no
        destinations = getattr(self, 'zone_no2', origins)
        self['matrix'] = xr.DataArray(
            np.zeros((n_zones, n_cols), dtype=dtype),
            coords=(origins, destinations),
            dims=('origins', 'destinations'),
            name='matrix',)

    def create_zones(self,
                     n_zones: int,
                     name: str = 'zone_no',
                     dim: str = 'zones'):
        self.coords[name] = xr.DataArray(np.arange(n_zones, dtype='i4'),
                                         dims=(dim,),)

    def read_names(self, f: TextIO, arr: xr.DataArray):
        """Read the zone names"""
        line = f.readline()
        while line.startswith("*") or line == "\n":
            line = f.readline()
        if line:
            if line.upper().startswith('$NAMES'):

                line = f.readline().strip()
                while line:
                    row = line.split(' "')
                    zone_no = int(row[0])
                    name = row[1].strip('"')
                    arr.loc[zone_no] = name
                    line = f.readline().strip()

    def read_names_o_format(self,
                            f: TextIO,
                            line: str,
                            rows: Iterable[str]):
        """Read the zone names"""
        names = deque()
        while line.startswith("*") or line == "\n":
            line = f.readline()
        if line:
            if line.upper().startswith('$NAMES'):

                line = f.readline().strip()
                while line:
                    row = line.split(' "')
                    zone_no = int(row[0])
                    name = row[1].strip('"')
                    names.append((zone_no, name))
                    line = f.readline().strip()
        if names:
            n_zones = len(names)
            self.create_zones(n_zones)
            for i, (zone_no, name) in enumerate(names):
                self.zone_no.data[i] = zone_no
            self.create_zone_names(n_zones)
            for i, (zone_no, name) in enumerate(names):
                self.zone_name.loc[zone_no] = name
        else:
            # get zone_no from unique zones in the data
            zones = []
            for row in rows:
                r = row.split()
                zones.extend(r[:2])
            zone_no = np.unique(np.array(zones, dtype=int))
            n_zones = len(zone_no)
            self.create_zones(n_zones)
            self.zone_no[:] = zone_no
        self.create_matrix(n_zones)

    def readPTVMatrixB(self):
        """
        Read a binary PTV Matrix
        """
        with self._openfile(mode="rb") as f:
            f.seek(0, 0)
            idlength = self.read_i2(f)
            idvalue = f.read(idlength)
            compression_type = chr(idvalue[2])
            header = self.read_i2(f)
            headervalue = f.read(header)
            transportvalue = self.read_i4(f)
            starttime = self.read_f4(f)
            endtime = self.read_f4(f)
            factor = self.read_f4(f)
            n_zones = self.read_i4(f)
            data_type = self.read_i2(f)
            roundproc = self.read_u1(f)
            if roundproc > 1:
                raise IOError("Flag of round procedure doesn't exist.")

            self.attrs['ZeitVon'] = starttime
            self.attrs['ZeitBis'] = endtime
            self.attrs['Faktor'] = factor
            self.attrs['roundproc'] = roundproc
            self.attrs['VMAktKennung'] = transportvalue
            self.attrs['AnzBezeichnerlisten'] = 1

            self.create_zones(n_zones)

            data_types = {2: 'i2', 3: 'i4', 4: 'f4', 5: 'f8'}
            dtype = data_types.get(data_type, 'f8')

            if compression_type == 'I':
                n_cols = n_zones
                self.create_matrix(n_zones, dtype=dtype)

                self.zone_no.data[:] = np.frombuffer(
                    f.read(n_zones * 4), dtype="i4")
            else:
                # BK or BL
                n_cols = self.read_i4(f)
                if compression_type == 'L':
                    dim = 'destinations'
                else:
                    dim = 'zones'
                self.create_zones(n_cols, name='zone_no2', dim=dim)

                self.zone_no.data[:] = np.frombuffer(
                    f.read(n_zones * 4), dtype="i4")
                self.zone_no2.data[:] = np.frombuffer(
                    f.read(n_cols * 4), dtype="i4")
                self.create_matrix(n_zones, n_cols=n_cols, dtype=dtype)

                # read zone names for rows
                self.create_zone_names(n_zones)
                for i in range(n_zones):
                    self.zone_name.data[i] = self.read_utf16(f)

                # read zone names for columns
                self.create_zone_names(n_cols, name='zone_names2',
                                       dim='zone_no2')
                for i in range(n_cols):
                    self.zone_names2.data[i] = self.read_utf16(f)

            # all null values=
            allnull = self.read_u1(f)
            if allnull > 1:
                raise IOError("Flag of allnull not correctly set.")

            # read the results
            rowsums = np.empty((n_zones), dtype='f8')
            colsums = np.empty((n_cols), dtype='f8')
            if not allnull:
                self.attrs['diagsum'] = self.read_f8(f)
                for i in range(n_zones):
                    len_chunk = self.read_i4(f)
                    unpacked = zlib.decompress(f.read(len_chunk))
                    self.matrix[i] = np.frombuffer(unpacked, dtype=dtype)
                    if compression_type < 'L':
                        # for this format row and colsums are
                        # written at each line
                        rowsums[i] = self.read_f8(f)
                        colsums[i] = self.read_f8(f)

                if compression_type >= 'L':
                    # for this format the row and colsums are written
                    # as a vector each
                    rowsums[:] = np.frombuffer(f.read(8*n_zones), dtype="f8")
                    colsums[:] = np.frombuffer(f.read(8*n_cols), dtype="f8")
            # all null
            else:
                self.attrs['diagsum'] = 0
                self.matrix[:] = 0
                rowsums[:] = 0
                colsums[:] = 0

        # check row and colsums and diagonal
        np.testing.assert_allclose(self.matrix.sum(axis=1), rowsums)
        np.testing.assert_allclose(self.matrix.sum(axis=0), colsums)
        np.testing.assert_allclose(np.diag(self.matrix).sum(),
                                   self.attrs['diagsum'])

    def read_utf16(self, f: BinaryIO) -> str:
        """read utf16( encoded string from file at current position"""
        n_chars = self.read_i4(f)
        return f.read(n_chars * 2).decode('utf16')

    @staticmethod
    def read_f4(f: BinaryIO) -> float:
        """read float from file at current position"""
        return np.frombuffer(f.read(4), dtype="f4")[0]

    @staticmethod
    def read_f8(f: BinaryIO) -> float:
        """read double from file at current position"""
        return np.frombuffer(f.read(8), dtype="f8")[0]

    @staticmethod
    def read_u1(f: BinaryIO) -> int:
        """read byte from file at current position"""
        return np.frombuffer(f.read(1), dtype="u1")[0]

    @staticmethod
    def read_i2(f: BinaryIO) -> int:
        """read short integer from file at current position"""
        return np.frombuffer(f.read(2), dtype="i2")[0]

    @staticmethod
    def read_i4(f: BinaryIO) -> int:
        """read integer from file at current position"""
        return np.frombuffer(f.read(4), dtype="i4")[0]

    def read_value(self, f: TextIO) -> int:
        """read a single value from the file as integer"""
        line = f.readline().strip()
        while not line or line.startswith("*"):
            line = f.readline()
        value = int(line)
        return value

    def read_values_to_array(self,
                             f: TextIO,
                             arr: xr.DataArray,
                             sep: str = ' '):
        """read values from the file into a DataArray"""
        flat_arr = arr.data.ravel()
        n_total = len(flat_arr)
        pos_from = 0
        while pos_from < n_total:
            line = f.readline()
            while line.startswith("*"):
                line = f.readline()
            row = np.fromstring(line, sep=sep, dtype=arr.dtype)
            pos_to = pos_from + len(row)
            flat_arr[pos_from:pos_to] = row
            pos_from = pos_to

    def read_values_in_o_format_to_list(self, f: TextIO) -> Tuple[deque, str]:
        """read values to a list"""
        rows = deque()
        for line in f:
            row = line.strip()
            if not row or row.startswith("*"):
                continue
            if row.startswith('$'):
                return rows, row
            rows.append(row)
        return rows, row

    def read_values(self, f: TextIO, n_values: int) -> List[float]:
        values = []
        found = 0
        while found < n_values:
            line = f.readline()
            while line.startswith("*"):
                line = f.readline()
            values += map(lambda x: self.float_nan(x), line.strip().split())
            found = len(values)
        return values

    @staticmethod
    def float_nan(x: str) -> float:
        """convert str to float, handling '-' as 0.0"""
        try:
            return float(x)
        except ValueError as err:
            if x == '-':
                return 0.0
            raise err


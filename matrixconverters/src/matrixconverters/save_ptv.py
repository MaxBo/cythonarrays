# -*- coding: utf-8 -*-

import zlib
import numpy as np
import xarray as xr
from typing import BinaryIO


def write_line(f, text, length):
    f.write(text.ljust(length) + b"\r\n")


class SavePTV(object):

    def __init__(self, ds: xr.Dataset):
        """
        Parameters
        ----------
        ds: xarray-Dataset
            the dataset that should be saved
        """
        self.ds = ds

    @staticmethod
    def write_u1(f: BinaryIO, val: int):
        """write 1-byte number to file"""
        f.write(np.array(val, dtype="u1").tobytes())

    @staticmethod
    def write_i2(f: BinaryIO, val: int):
        """write short number to file"""
        f.write(np.array(val, dtype="i2").tobytes())

    @staticmethod
    def write_i4(f: BinaryIO, val: int):
        """write int number to file"""
        f.write(np.array(val, dtype="i4").tobytes())

    @staticmethod
    def write_f4(f: BinaryIO, val: float):
        """write float to file"""
        f.write(np.array(val, dtype="f4").tobytes())

    @staticmethod
    def write_f8(f: BinaryIO, val: float):
        """write double to file"""
        f.write(np.array(val, dtype="f8").tobytes())

    def write_utf16(self, f: BinaryIO, val: xr.DataArray):
        """write string as utf16 encoded string to file"""
        unencoded_str = val.data.tolist()
        self.write_i4(f, len(unencoded_str))
        utf16_str = unencoded_str.encode('UTF-16LE')
        f.write(utf16_str)

    def savePTVMatrix(self,
                      file_name: str,
                      file_type: str = 'BK',
                      version: float = 0.11,
                      ):
        """
        save array im PTV-Format

        Parameters
        ----------
        file_name : string
            output file_name
        file_type : str
            Type of PTV-File Format
        version : str
            version number
        """

        if file_type.startswith("B"):
            self._write_format_b(file_name, file_type=file_type)
        elif file_type.startswith("V"):
            self._write_format_v(file_name, file_type)
        elif file_type.startswith("O"):
            self._write_format_o(file_name, file_type)

    def _write_format_v(self, fn: str, file_type: str):
        dtypes = {'float32': "Y4", 'float64': "Y5",
                  'int32': "Y3", 'int16': "Y2"}
        outformat = {'float32': "%0.3f", 'float64': "%0.6f",
                     'int32': "%d", 'int16': "%d"}
        with open(fn, "w") as f:
            ZeitVon = getattr(self.ds.attrs, 'ZeitVon', 0)
            ZeitBis = getattr(self.ds.attrs, 'ZeitBis', 24)
            Faktor = getattr(self.ds.attrs, 'Faktor', 1)
            VMAktKennung = getattr(self.ds.attrs, 'VMAktKennung', 0)
            dtype = self.ds.matrix.dtype
            f.write("$%s, %s\n" % (file_type, dtypes[str(dtype)]))
            if "M" in file_type:
                f.write("* Verkehrsmittelkennung:\n %d \n" % VMAktKennung)
            if "N" not in file_type:
                f.write("* Zeitintervall:\n {v} {b} \n".format(
                    v=ZeitVon,
                    b=ZeitBis))
                f.write("* Faktor:\n %d \n" % Faktor)
            zone_no = self.ds.zone_no.data
            n_zones = len(zone_no)
            f.write("* Anzahl Bezirke:\n %d\n" % n_zones)
            f.write("* Bezirksnummern\n")
            for i in range(0, n_zones, 10):
                f.write("\t".join(map(lambda x:
                                      str(x),
                                      zone_no[i: i + 10])) + "\n")
            f.write("* Matrixwerte\n")
            values = self.ds.matrix.data
            fmt = outformat[str(dtype)]
            for i in range(n_zones):
                no = zone_no[i]
                f.write("* %s \n" % no)
                for j in range(0, n_zones, 10):
                    values[i, j: j + 10].tofile(f, sep=' ', format=fmt)
                    f.write('\n')

            if 'zone_name' in self.ds:
                zone_name = self.ds.zone_name.data
                fmt = '{no} "{name}"\n'
                for i in range(n_zones):
                    f.write(fmt.format(no=zone_no[i], name=zone_name[i]))

    def _write_format_o(self, fn: str, file_type: str):
        dtypes = {'float32': "Y4", 'float64': "Y5",
                  'int32': "Y3", 'int16': "Y2"}

        with open(fn, "w") as f:
            ZeitVon = self.ds.attrs.get('ZeitVon', 0)
            ZeitBis = self.ds.attrs.get('ZeitBis', 24)
            Faktor = self.ds.attrs.get('Faktor', 1)
            VMAktKennung = self.ds.attrs.get('VMAktKennung', 0)
            dtype = self.ds.matrix.dtype
            f.write("$%s, %s\n" % (file_type, dtypes[str(dtype)]))
            if "M" in file_type:
                f.write("* Verkehrsmittelkennung:\n %d \n" % VMAktKennung)
            if "N" not in file_type:
                f.write("* Zeitintervall:\n {v} {b} \n".format(
                    v=ZeitVon,
                    b=ZeitBis))
                f.write("* Faktor:\n %d \n" % Faktor)
            df = self.ds.matrix.to_dataframe().iloc[:, 0]
            df_larger_0 = df[df > 0]
            f.write("* Matrixwerte\n")
            df_larger_0.to_csv(f, sep=' ', header=False)

            zone_no = self.ds.zone_no.data
            n_zones = self.ds.dims['zone_no']

            if 'zone_name' in self.ds:
                f.write('* Netzobjektnamen\n')
                f.write('$NAMES\n')
                zone_name = self.ds.zone_name.data
                fmt = '{no} "{name}"\n'
                for i in range(n_zones):
                    f.write(fmt.format(no=zone_no[i], name=zone_name[i]))

    def _write_format_b(self, fn: str, file_type: str = 'K'):
        m = self.ds.matrix.data
        with open(fn, "wb") as f:

            n_zones = m.shape[0]
            n_cols = m.shape[1]

            idlength = 3
            self.write_i2(f, idlength)
            is_square = n_zones == n_cols
            if is_square:
                if file_type == 'BI':
                    idvalue = b'$BI'
                else:
                    idvalue = b'$BK'
            else:
                idvalue = b'$BL'
            compression_type = chr(idvalue[2])
            f.write(idvalue)

            vartype = 5

            datatypes = {'f': 4, 'd': 5, 'l': 3, 'h': 2, }
            typecodes = {'f': 'f4', 'd': 'f8', 'l': 'i4', 'h': 'i2', }
            datatype = datatypes.get(m.dtype.char, 5)
            typecode = typecodes.get(m.dtype.char, 'f8')

            header_lines = ['']
            ZeitVon = self.ds.attrs.get('ZeitVon', 0)
            ZeitBis = self.ds.attrs.get('ZeitBis', 24)
            Faktor = self.ds.attrs.get('Faktor', 1)
            VMAktKennung = self.ds.attrs.get('VMAktKennung', 0)
            roundproc = self.ds.attrs.get('roundproc', 0)

            # write header
            header_lines.append("Muuli matrix in packed binary format.")
            header_lines.append("Zones: {} ".format(n_zones))
            header_lines.append("VarType: {} ".format(vartype))
            header_lines.append("Total sum: {:.6f} ".format(m.sum()))

            diagsum = np.diag(m).sum()
            header_lines.append("Diagonal sum: {:6f} ".format(diagsum))
            header_lines.append("Transport mode: {} ".format(VMAktKennung))
            header_lines.append("from: {:.2f} ".format(ZeitVon))
            header_lines.append("to: {:.2f} ".format(ZeitBis))
            header_lines.append("Factor: {:6f} ".format(Faktor))
            header_lines.append("")

            header = '\r\n'.join(header_lines).encode('utf8')
            header_length = len(header)
            self.write_i2(f, header_length)
            f.write(header)

            # write additional infos
            self.write_i4(f, VMAktKennung)
            self.write_f4(f, ZeitVon)
            self.write_f4(f, ZeitBis)
            self.write_f4(f, Faktor)
            self.write_i4(f, n_zones)
            self.write_i2(f, datatype)
            self.write_u1(f, roundproc)

            # columns
            if compression_type != 'I':
                self.write_i4(f, n_cols)
            # zone numbers for rows ...
            zone_no = self.ds.zone_no
            assert len(zone_no) == n_zones,\
                   'zone_no with length {d} does not match matrix with {n} rows'\
                .format(d=len(zone_no), n=n_zones)
            f.write(np.array(zone_no.data).astype("i4").tobytes())
            # ... and columns (not for $BI)
            if compression_type != 'I':
                zone_cols = getattr(self.ds, 'zone_no2', zone_no)
                assert len(zone_cols) == n_cols,\
                    'zone_cols with length {d} does not match matrix with {n} columns'\
                    .format(d=len(zone_cols), n=n_cols)
                f.write(np.array(zone_cols.data).astype("i4").tobytes())

                # zone_names (not for $BI):
                zone_names = getattr(self.ds, 'zone_name', None)
                if zone_names is None:
                    zone_names = [xr.DataArray('') for i in range(n_zones)]
                assert len(zone_names) == n_zones,\
                    'zone_names with length {d} does not match matrix with {n} rows'\
                    .format(d=len(zone_names), n=n_zones)
                # for rows
                for zone_name in zone_names:
                    self.write_utf16(f, zone_name)
                # for columns
                zone_names2 = getattr(self.ds, 'zone_names2', None)
                if zone_names2 is None:
                    if is_square:
                        zone_names2 = zone_names
                    else:
                        zone_names2 = [xr.DataArray('') for i in range(n_cols)]
                assert len(zone_names2) == n_cols,\
                    'zone_names2 with length {d} does not match matrix with {n} columns'\
                    .format(d=len(zone_names2), n=n_cols)
                for zone_name in zone_names2:
                    self.write_utf16(f, zone_name)

            allnull = int(not np.any(m))
            self.write_u1(f, allnull)
            self.write_f8(f, diagsum)
            if not allnull:
                data = m.astype(typecode)
                rowsums = data.sum(1).astype('f8')
                colsums = data.sum(0).astype('f8')
                for i in range(n_zones):
                    row = data[i]
                    compressed = zlib.compress(row.tobytes())
                    self.write_i4(f, len(compressed))
                    f.write(compressed)
                    if compression_type != 'L':
                        self.write_f8(f, rowsums[i])
                        self.write_f8(f, colsums[i])
                if not is_square:
                    # for $BL-format, the row and colsums are written as vector
                    f.write(rowsums.tobytes())
                    f.write(colsums.tobytes())

    def savePSVMatrix(self,
                      file_name: str,
                      ftype: str = "CC",
                      max_width: int = 1000):
        """
        exports array in PSV-Format
        """
        m = self.ds.matrix.data
        if not m.ndim == 2:
            raise ValueError('matrix has to have 2 dimensions')
        rows, cols = m.shape
        zones = self.ds.get('zone_no1', range(1, rows + 1))

        with open(file_name, "w") as f:
            Za = max(rows, cols)
            Zi = min(rows, cols)
            f.write("%s; Za %s; Zi %s;\n" % (ftype, Za, Zi))
            if ftype == "CC":
                for i in range(rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if m[i].any():
                        # addiere 1, um Zellennummer 0 zu vermeiden
                        row = str(zones[i])
                        for j in range(cols):
                            if len("%s %s %s" % (row, zones[j],
                                                 m[i, j])) >= max_width:
                                row += "\n"
                                f.write(row)
                                row = str(zones[i])
                            if m[i, j] != 0:
                                row += " %s %s " % (zones[j], m[i, j])
                        row += "\n"
                        f.write(row)

            elif ftype == "CN":
                for i in range(rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if m[i].any():
                        row = str(zones[i])
                        for j in range(cols):
                            if len("%s %s" % (row, m[i, j])) >= max_width:
                                row += "\n"
                                f.write(row)
                                row = str(zones[i])
                            row += " " + str(m[i, j])
                        row += "\n"
                        f.write(row)
            else:
                raise TypeError("Kann Typ %s nicht schreiben" % ftype)

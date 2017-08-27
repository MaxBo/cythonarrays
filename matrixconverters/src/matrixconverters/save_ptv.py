# -*- coding: utf-8 -*-
# Name:        saveArray
# Purpose:
#
# Author:      Max Bohnet
#
# Created:     21/09/2011
# Copyright:   (c) Max Bohnet 2011


import gzip
import zlib
import numpy as np
import xarray as xr


def writeFormattedLine(f, text, length):
    f.write(text.ljust(length) + b"\r\n")


class SavePTV(object):

    def __init__(self, ds):
        """"""
        self.ds = ds

    @staticmethod
    def write_u1(f, val):
        """write 1-byte number to file"""
        f.write(np.array(val, dtype="u1").tostring())

    @staticmethod
    def write_i2(f, val):
        """write short number to file"""
        f.write(np.array(val, dtype="i2").tostring())

    @staticmethod
    def write_i4(f, val):
        """write int number to file"""
        f.write(np.array(val, dtype="i4").tostring())

    @staticmethod
    def write_f4(f, val):
        """write float to file"""
        f.write(np.array(val, dtype="f4").tostring())

    @staticmethod
    def write_f8(f, val):
        """write double to file"""
        f.write(np.array(val, dtype="f8").tostring())

    def write_utf16(self, f, val):
        """write string as utf16 encoded string to file"""
        unencoded_str = val.data.tolist()
        self.write_i4(f, len(unencoded_str))
        utf16_str = unencoded_str.encode('UTF-16LE')
        f.write(utf16_str)


    def savePTVMatrix(self, file_name, Ftype='BK', version=0.11,
                      zipped=False):
        """
        save array im PTV-Format

        Parameters
        ----------
        file_name : string
            output file_name
        FType : {'B', 'V'}
            Type of PTV-File Format
            either als binary file ("B")
            or as V-Format ("V")
            or as O-Format ("O")
        version : srting
            version number
        zipped : bool
            To save Disc Space and increase speed,
            the file can be saved in a gzip-packed format (zipped = True)
        """
        if zipped:
            OpenFile = gzip.open
            fn = file_name + ".gzip"
        else:
            OpenFile = open
            fn = file_name

        if Ftype.startswith("BK"):
            self.write_format_bk(OpenFile, fn, version)
        elif Ftype.startswith("B"):
            self.write_format_b(OpenFile, fn, version)
        elif Ftype.startswith("V"):
            self.write_format_v(OpenFile, fn, Ftype)
        elif Ftype.startswith("O"):
            self.write_format_o(OpenFile, fn, Ftype)

    def write_format_v(self, OpenFile, fn, Ftype):
        dtypes = {'float32': "Y4", 'float64': "Y5",
                  'int32': "Y3", 'int16': "Y2"}
        outformat = {'float32': "%0.3f", 'float64': "%0.6f",
                     'int32': "%d", 'int16': "%d"}
        with OpenFile(fn, "w") as f:
            anz_bez_listen = getattr(self.ds.attrs, 'AnzBezeichnerlisten', 1)
            ZeitVon = getattr(self.ds.attrs, 'ZeitVon', 0)
            ZeitBis = getattr(self.ds.attrs, 'ZeitBis', 24)
            Faktor = getattr(self.ds.attrs, 'Faktor', 1)
            VMAktKennung = getattr(self.ds.attrs, 'VMAktKennung', 0)
            dtype = self.ds.matrix.dtype
            f.write("$%s, %s\n" % (Ftype, dtypes[str(dtype)]))
            if "M" in Ftype:
                f.write("* Verkehrsmittelkennung:\n %d \n" % VMAktKennung)
            if "N" not in Ftype:
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

    def write_format_o(self, OpenFile, fn, Ftype):
        dtypes = {'float32': "Y4", 'float64': "Y5",
                  'int32': "Y3", 'int16': "Y2"}
        outformat = {'float32': "%0.3f", 'float64': "%0.6f",
                     'int32': "%d", 'int16': "%d"}
        with OpenFile(fn, "w") as f:
            anz_bez_listen = getattr(self.ds.attrs, 'AnzBezeichnerlisten', 1)
            ZeitVon = getattr(self.ds.attrs, 'ZeitVon', 0)
            ZeitBis = getattr(self.ds.attrs, 'ZeitBis', 24)
            Faktor = getattr(self.ds.attrs, 'Faktor', 1)
            VMAktKennung = getattr(self.ds.attrs, 'VMAktKennung', 0)
            dtype = self.ds.matrix.dtype
            f.write("$%s, %s\n" % (Ftype, dtypes[str(dtype)]))
            if "M" in Ftype:
                f.write("* Verkehrsmittelkennung:\n %d \n" % VMAktKennung)
            if "N" not in Ftype:
                f.write("* Zeitintervall:\n {v} {b} \n".format(
                    v=ZeitVon,
                    b=ZeitBis))
                f.write("* Faktor:\n %d \n" % Faktor)
            df = self.ds.matrix.to_dataframe().ix[:, 0]
            df_larger_0 =  df[df > 0]
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

    def write_format_b(self, OpenFile, fn, version):
        m = self.ds.matrix.data
        with OpenFile(fn, "wb") as f:
            anz_bez_listen = getattr(self.ds.attrs, 'AnzBezeichnerlisten', 1)
            ZeitVon = getattr(self.ds.attrs, 'ZeitVon', 0)
            ZeitBis = getattr(self.ds.attrs, 'ZeitBis', 24)
            Faktor = getattr(self.ds.attrs, 'Faktor', 1)
            VMAktKennung = getattr(self.ds.attrs, 'VMAktKennung', 0)
            writeFormattedLine(f, b"PTVSYSTEM   MUULI       VMatrixComp1", 44)
            writeFormattedLine(f, b"VMatversionsnummer: %0.2f" % version, 28)
            writeFormattedLine(f, b"Anzahl Dimensionen: %d" % m.ndim, 28)
            writeFormattedLine(f, b"Seitenlaengen der Matrix:", 30)
            text = b""
            for n in range(m.ndim):
                text += (b"%d" % m.shape[n]).ljust(8)
            writeFormattedLine(f, text, 48)
            writeFormattedLine(f, b"% -30s%d" % (b"Anzahl Bezeichnerlisten:",
                                                 anz_bez_listen),
                               38)
            writeFormattedLine(f, b"% -20s%02d:00   %02d:00" % (
                b"Zeitbereich:",
                ZeitVon,
                ZeitBis,
                ),
                               36)
            writeFormattedLine(f, b"% -20s%s" % (b"RandomRound:", b"Nein"), 28)
            writeFormattedLine(f, b"% -24s%0.2f" % (b"Faktor:",
                                                    Faktor), 28)
            for i in range(20):
                writeFormattedLine(f, b" ", 80)
            f.write(np.array(6682, dtype="i2").tostring())  # header
            f.write(b" " * 80)
            f.write(np.array(11, dtype="i2").tostring())  # header
            f.write(np.array(m.ndim, dtype="i2").tostring())  # Dimensions
            # Zeilen je Dimension
            f.write(np.array(m.shape[-2], dtype="i4").tostring())
            f.write(np.array(2080, dtype="i4").tostring())  # header
            # Spalten
            f.write(np.array(m.shape[-1], dtype="i4").tostring())
            f.write(np.array(2080, dtype="i4").tostring())  # ???
            if m.ndim == 3:
                # Bloecke
                f.write(np.array(m.shape[0], dtype="i4").tostring())
                f.write(np.array(2080, dtype="i4").tostring())  # ???

            if m.dtype.char == 'f':
                # 3 Datentyp float
                f.write(np.array(3, dtype="i2").tostring())
                typecode = '<f4'
            elif m.dtype.char == 'd':
                # 4 Datentyp double
                f.write(np.array(4, dtype="i2").tostring())
                typecode = '<f8'
            else:
                # z.B. integer oder unsigned integer:
                # 3 Datentyp float
                # ToDo: Prüfen!!!
                f.write(np.array(3, dtype="i2").tostring())
                typecode = '<f8'
            # AnzBezeichnerlisten, was immer das auch ist ???
            f.write(np.array(anz_bez_listen, dtype="i2").tostring())
            f.write(np.array(ZeitVon, dtype="f4").tostring())  # ZeitVon
            f.write(np.array(ZeitBis, dtype="f4").tostring())  # ZeitBis
            # VMAktKennung
            f.write(np.array(VMAktKennung, dtype="i4").tostring())
            # Unbekannt U als float
            f.write(np.array(Faktor, dtype="<f4").tostring())
            # zones
            f.write(np.array(self.ds.zone_no.data).astype("i4").tostring())
            f.write(m.astype(typecode).flatten().tostring())  # Matrix

    def write_format_bk(self, OpenFile, fn, version):
        m = self.ds.matrix.data
        with OpenFile(fn, "wb") as f:

            n_zones = m.shape[0]
            n_cols = m.shape[1]

            idlength = 3
            self.write_i2(f, idlength)
            is_square = n_zones == n_cols
            if is_square:
                idvalue = b'$BK'
            else:
                idvalue = b'$BL'
            compression_type = chr(idvalue[2])
            f.write(idvalue)

            vartype = 5

            datatypes = {'f': 4, 'd': 5, 'l': 3, 'h': 2,}
            typecodes = {'f': 'f4', 'd': 'f8', 'l': 'i4', 'h': 'i2',}
            datatype = datatypes.get(m.dtype.char, 5)
            typecode = typecodes.get(m.dtype.char, 'f8')

            header_lines = ['']
            anz_bez_listen = getattr(self.ds.attrs, 'AnzBezeichnerlisten', 1)
            ZeitVon = getattr(self.ds.attrs, 'ZeitVon', 0)
            ZeitBis = getattr(self.ds.attrs, 'ZeitBis', 24)
            Faktor = getattr(self.ds.attrs, 'Faktor', 1)
            VMAktKennung = getattr(self.ds.attrs, 'VMAktKennung', 0)
            roundproc = getattr(self.ds.attrs, 'roundproc', 0)

            # write header
            header_lines.append("Muuli matrix in packed binary format.")
            header_lines.append("Zones: {}".format(n_zones))
            header_lines.append("VarType: {}".format(vartype))
            header_lines.append("Total sum: {}".format(m.sum()))

            diagsum = np.diag(m).sum()
            header_lines.append("Diagonal sume: {}".format(diagsum))
            header_lines.append("Transport mode: {}".format(VMAktKennung))
            header_lines.append("from: {}".format(ZeitVon))
            header_lines.append("to: {}".format(ZeitBis))
            header_lines.append("Factor: {}".format(Faktor))
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
            self.write_i4(f, n_cols)
            # zone numbers for rows and columns
            zone_no = self.ds.zone_no
            f.write(np.array(zone_no.data).astype("i4").tostring())
            zone_cols = getattr(self.ds, 'zone_no2', zone_no)
            f.write(np.array(zone_cols.data).astype("i4").tostring())

            # zone_names:
            zone_names = getattr(self.ds, 'zone_name', None)
            if zone_names is None:
                zone_names = (xr.DataArray('') for i in range(n_zones))
            # for rows
            for zone_name in zone_names:
                self.write_utf16(f, zone_name)
            # for columns
            zone_names2 = getattr(self.ds, 'zone_names2', None)
            if zone_names2 is None:
                if is_square:
                    zone_names2 = zone_names
                else:
                    zone_names2 = (xr.DataArray('') for i in range(n_cols))
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
                    #if compression_type == 'L':
                        #f.write(row.tostring())
                    #else:
                    compressed = zlib.compress(row.tostring())
                    self.write_i4(f, len(compressed))
                    f.write(compressed)
                    if compression_type != 'L':
                        self.write_f8(f, rowsums[i])
                        self.write_f8(f, colsums[i])
                if not is_square:
                    # for $BL-format, the row and colsums are written as vector
                    f.write(rowsums.tostring())
                    f.write(colsums.tostring())


    def savePSVMatrix(self, fileName, ftype="CC", maxWidth=1000):
        """ exports array in PSV-Format
        """
        m = self.ds.matrix.data
        if not m.ndim == 2:
            raise ValueError('matrix has to have 2 dimensions')
        rows, cols = m.shape
        if not hasattr(self, 'zones'):
            self.zones = range(1, rows + 1)
        f = open(fileName, "w")
        try:
            Za = max(rows, cols)
            Zi = min(rows, cols)
            f.write("%s; Za %s; Zi %s;\n" % (ftype, Za, Zi))
            if ftype == "CC":
                for i in range(rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if m[i].any():
                        # addiere 1, um Zellennummer 0 zu vermeiden
                        row = str(m.zones[i])
                        for j in range(cols):
                            if len("%s %s %s" % (row, m.zones[j],
                                                 m[i, j])) >= maxWidth:
                                row += "\n"
                                f.write(row)
                                row = str(m.zones[i])
                            if m[i, j] != 0:
                                row += " %s %s " % (m.zones[j], m[i, j])
                        row += "\n"
                        f.write(row)

            elif ftype == "CN":
                for i in range(rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if m[i].any():
                        row = str(m.zones[i])
                        for j in range(cols):
                            if len("%s %s" % (row, m[i, j])) >= maxWidth:
                                row += "\n"
                                f.write(row)
                                row = str(m.zones[i])
                            row += " " + str(m[i, j])
                        row += "\n"
                        f.write(row)
            else:
                raise TypeError("Kann Typ %s nicht schreiben" % ftype)
        finally:
            f.close()

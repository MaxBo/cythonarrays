#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import gzip
import zlib
import io
from argparse import ArgumentParser
from collections import deque
import numpy as np
import xarray as xr


class ReadPTVMatrix(xr.Dataset):
    """reads PTV-Matrix from file
    the matrix-type is determined by the header
    reades $M, $V, $O, $E, and the binary types $BI and $B

    Arguments:
        FileName: path to file on disk
        header: length ot the header
        zipped: true, if file is zipped
    """
    def __init__(self, filename, header=2048, zipped=False):
        super(ReadPTVMatrix, self).__init__()
        self.attrs['fn'] = filename
        self.attrs['ZeitVon'] = 0
        self.attrs['ZeitBis'] = 0
        self.attrs['Faktor'] = 1
        self.attrs['VMAktKennung'] = 0
        self.attrs['AnzBezeichnerlisten'] = 1

        self.set_open_method(filename, zipped)
        with self.openfile(mode='rb') as f:
            line = f.readline().strip()

        if line.startswith(b"$M"):
            self.readPTVMatrixM()
        elif line.startswith(b"$V"):
            self.readPTVMatrixV()
        elif line.startswith(b"$O"):
            self.readPTVMatrixO()
        elif line.startswith(b"$E"):
            self.readPTVMatrixE()
        elif line.startswith(b"$S"):
            self.readPTVMatrixE()
        elif line.strip(bytes([3, 0])).startswith(b"$BI"):
            self.readPTVMatrixBI()
        elif line.strip(bytes([3, 0])).startswith(b"$BK"):
            self.readPTVMatrixBK()
        elif line.strip(bytes([3, 0])).startswith(b"$B"):
            self.readPTVMatrixB()

        else:
            self.readPTVMatrixB(header)

        del self.attrs['open']

    def readPTVMatrixO(self):
        with self.openfile(mode="r") as f:
            rows = self.read_header(f)
        loc = self.matrix.loc
        for row in rows:
            r = row.split()
            fr = int(r[0])
            to = int(r[1])
            value = float(r[2])
            loc[fr, to] = value

    def readPTVMatrixE(self):
        with self.openfile(mode="r") as f:
            rows = self.read_header(f)
        loc = self.matrix.loc
        for row in rows:
            cols = row.lstrip('-').split()
            fr = int(cols[0])
            for i in range(1, len(cols), 2):
                to = int(cols[i])
                value = float(cols[i + 1])
                loc[fr, to] = value

    def read_header(self, f):
        line = f.readline()
        MatrixTyp = line.split("$")[-1].split(";")[0]
        if "M" in MatrixTyp:
            self.attrs['VMAktKennung'] = self.readWert(f)

        if "N" not in MatrixTyp:
            ZeitVon, ZeitBis, Faktor = self.readWerte(f, 3)
            self.attrs['ZeitVon'] = ZeitVon
            self.attrs['ZeitBis'] = ZeitBis
            self.attrs['Faktor'] = Faktor

        rows, line = self.read_values_in_o_format_to_list(f)
        self.read_names_o_format(f, line)
        return rows

    def set_open_method(self, filename, zipped):
        """set the open-method"""
        if filename.endswith(".gzip") or zipped:
            self.attrs['open'] = gzip.open
        elif sys.version_info[0] > 2:
            self.attrs['open'] = open
        else:
            self.attrs['open'] = io.open

    def openfile(self, mode='r', encoding='latin1'):
        open_method = self.attrs['open']
        if mode.endswith('b'):
            encoding = None
        return open_method(self.attrs['fn'], mode=mode, encoding=encoding)

    def readPTVMatrixV(self):
        with self.openfile() as f:
            line = f.readline()
            MatrixTyp = line.split("$")[-1].split(";")[0]
            if not MatrixTyp.startswith("V"):
                print("Keine Matrix im V-Format!")
                raise TypeError
            if "M" in MatrixTyp:
                self.attrs['VMAktKennung'] = self.readWert(f)

            if "N" not in MatrixTyp:
                ZeitVon, ZeitBis, Faktor = self.readWerte(f, 3)
                self.attrs['ZeitVon'] = ZeitVon
                self.attrs['ZeitBis'] = ZeitBis
                self.attrs['Faktor'] = Faktor

            n_zones = self.readWert(f)
            self.create_zones(n_zones)
            self.read_values_to_array(f, self.zone_no)

            self.create_matrix(n_zones)
            self.read_values_to_array(f, self.matrix)
            self.create_zone_names(n_zones)
            self.read_names(f, self.zone_name)

    def create_zone_names(self, n_zones, name='zone_name'):
        self[name] = xr.DataArray(
            np.empty((n_zones, ), dtype='O'),
            coords=(self.zone_no.data, ),
            dims=('zone_no',),
            name=name,)

    def create_matrix(self, n_zones, dtype='f8'):
        self['matrix'] = xr.DataArray(
            np.empty((n_zones, n_zones), dtype=dtype),
            coords=(self.zone_no, self.zone_no),
            dims=('origins', 'destinations'),
            name='matrix',)

    def create_zones(self, n_zones, name='zone_no'):
        self.coords[name] = xr.DataArray(np.empty((n_zones, ), dtype='i4'),
                                         dims=('zones',),)

    def read_names(self, f, arr):
        """Read the zone names"""
        line = f.readline()
        while line.startswith("*") or line == "\n":
            line = f.readline()
        if line:
            if line.upper().startswith('$NAMES'):

                line = f.readline().strip()
                while line:
                    l = line.split(' "')
                    zone_no = int(l[0])
                    name = l[1].strip('"')
                    arr.loc[zone_no] = name
                    line = f.readline().strip()

    def read_names_o_format(self, f, line):
        """Read the zone names"""
        names = deque()
        while line.startswith("*") or line == "\n":
            line = f.readline()
        if line:
            if line.upper().startswith('$NAMES'):

                line = f.readline().strip()
                while line:
                    l = line.split(' "')
                    zone_no = int(l[0])
                    name = l[1].strip('"')
                    names.append((zone_no, name))
                    line = f.readline().strip()
        n_zones = len(names)
        self.create_zones(n_zones)
        for i, (zone_no, name) in enumerate(names):
            self.zone_no.data[i] = zone_no
        self.create_zone_names(n_zones)
        for i, (zone_no, name) in enumerate(names):
            self.zone_name.loc[zone_no] = name
        self.create_matrix(n_zones)

    def readPTVMatrixBK(self):
        """
        Die Länge des Headers stehen in Byte 5/6
        Zuerst wird mit Hilfe dieses offsets die Anzahl der Zellen ausgelesen
        und eine leere Matrix gebildet
        dann werden Verkehrsmittelkennung gelesen.
        Dann folgen die Zellennummern
        Schlieslich wird für jede Zeile der Matrix zuerst
        die Länge der gepakten Daten dieser Zeile (lenChunk) gelesen
        und dann die Daten mit zlib.decompress entpackt
        und mit np.fromstring in ein Zeilen-array verwandelt,
        Damit wird die Matrix zeilenweise "gefüllt"
        Zwischen den Zeilen befinden sich jeweils 16 byte,
        deren Sinn unklar ist (ggf. eine Prüfsumme?)
        Diese werden ignoriert.
        """
        with self.openfile(mode="rb") as f:
            f.seek(5, 0)
            header = np.fromstring(f.read(2), dtype="i2")[0]
            f.seek(header, 0)
            f.seek(23 - 16, 1)
            self.attrs['VMAktKennung'] = np.fromstring(f.read(2),
                                                       dtype="i2")[0]
            f.seek(14, 1)
            n_zones = np.fromstring(f.read(4), dtype="i4")[0]
            self.create_zones(n_zones)

            data_type = np.fromstring(f.read(2), dtype="i2")[0]
            f.seek(1, 1)
            if data_type == 4:
                dtype = '<f4'
            elif data_type == 5:
                dtype = '<f8'
            self.create_matrix(n_zones, dtype=dtype)

            n_zones2 = np.fromstring(f.read(4), dtype="i4")[0]
            self.zone_no.data[:] = np.fromstring(
                f.read(n_zones * 4), dtype="i4")
            self.create_zones(n_zones2, name='zone_no2')
            self.zone_no2.data[:] = np.fromstring(
                f.read(n_zones * 4), dtype="i4")
            self.create_zone_names(n_zones)
            for i in range(n_zones):
                Zeichen = np.fromstring(f.read(4), dtype="i4")[0]
                self.zone_name.data[i] = f.read(Zeichen * 2).decode('utf16')

            self.create_zone_names(n_zones, name='zone_names2')
            for i in range(n_zones2):
                Zeichen = np.fromstring(f.read(4), dtype="i4")[0]
                self.zone_names2.data[i] = f.read(Zeichen * 2).decode('utf16')
            f.seek(1, 1)
            self.attrs['Unbek1'] = np.fromstring(f.read(8), dtype="f8")[0]
            for i in range(n_zones):
                lenChunk = np.fromstring(f.read(4), dtype="i4")[0]
                unpacked = zlib.decompress(f.read(lenChunk))
                self.matrix[i] = np.fromstring(unpacked, dtype=dtype)
                f.seek(16, 1)

    def readPTVMatrixBI(self):
        """
        Die Länge des Headers stehen in Byte 5/6
        Zuerst wird mit Hilfe dieses offsets die Anzahl der Zellen ausgelesen
        und eine leere Matrix gebildet
        dann werden Verkehrsmittelkennung gelesen.
        Dann folgen die Zellennummern
        Schlieslich wird für jede Zeile der Matrix
        zuerst die Länge der gepakten Daten dieser Zeile (lenChunk) gelesen
        und dann die Daten mit zlib.decompress entpackt
        und mit np.fromstring in ein Zeilen-array verwandelt,
        Damit wird die Matrix zeilenweise "gefüllt"
        Zwischen den Zeilen befinden sich jeweils 16 byte,
        deren Sinn unklar ist (ggf. eine Prüfsumme?)
        Diese werden ignoriert.
        """
        with self.openfile("rb") as f:
            f.seek(5, 0)
            header = np.fromstring(f.read(2), dtype="i2")[0]
            f.seek(header, 0)
            f.seek(23 - 16, 1)
            self.attrs['VMAktKennung'] = np.fromstring(
                f.read(2), dtype="i2")[0]
            f.seek(14, 1)
            n_zones = np.fromstring(f.read(4), dtype="i4")[0]
            data_type = np.fromstring(f.read(2), dtype="i2")[0]
            if data_type == 4:
                dtype = '<f4'
            elif data_type == 5:
                dtype = '<f8'
            self.create_zones(n_zones)
            self.create_matrix(n_zones, dtype=dtype)
            f.seek(1, 1)
            self.zone_no.data[:] = np.fromstring(
                f.read(4 * n_zones), dtype="i4")[0]
            f.seek(9, 1)
            m = self.matrix.data

            for i in range(n_zones):
                lenChunk = np.fromstring(f.read(4), dtype="i4")[0]
                unpacked = zlib.decompress(f.read(lenChunk))
                m[i] = np.fromstring(unpacked, dtype=dtype)
                m.seek(16, 1)

    def readPTVMatrixB(self, header=2048):
        with self.openfile(mode="rb") as f:
            f.seek(header)
            f.seek(2, 1)
            Dimensions = np.fromstring(f.read(2), dtype="i2")[0]
            MatrixZeilen = np.fromstring(f.read(4), dtype="i4")[0]
            f.seek(4, 1)
            MatrixSpalten = np.fromstring(f.read(4), dtype="i4")[0]
            f.seek(4, 1)
            if Dimensions == 3:
                MatrixBlock = np.fromstring(f[header + 20:header + 24],
                                            dtype="i4")[0]
                f.seek(4, 1)
                shape = (MatrixBlock, MatrixZeilen, MatrixSpalten)
            elif Dimensions == 2:
                MatrixBlock = 1
                shape = (MatrixZeilen, MatrixSpalten)
            else:
                msg = 'only 2d or 3d dimensions allowed, found %s dimensions'
                raise ValueError(msg % Dimensions)
            data_type = np.fromstring(f.read(2), dtype="i2")
            if data_type == 3:
                data_length = 4
                dtype = '<f4'
            elif data_type == 4:
                data_length = 8
                dtype = '<f8'
            AnzBezeichnerlisten = np.fromstring(f.read(2),
                                                dtype="i2")
            AnzFelder = MatrixZeilen * MatrixSpalten * MatrixBlock

            n_zones = max(MatrixZeilen, MatrixSpalten)
            self.create_zones(n_zones)
            self.attrs['ZeitVon'] = int(np.fromstring(f.read(4), dtype="f4"))
            self.attrs['ZeitBis'] = int(np.fromstring(f.read(4), dtype="f4"))
            self.attrs['VMAktKennung'] = int(
                np.fromstring(f.read(4), dtype="i4"))
            self.attrs['Faktor'] = int(np.fromstring(f.read(4), dtype="f4"))
            if AnzBezeichnerlisten > 0:
                self.zone_no.data[:] = np.fromstring(
                    f.read(4 * n_zones), dtype='i4')
            self.create_matrix(n_zones, dtype=dtype)
            arr = np.fromstring(f.read(AnzFelder * data_length), dtype=dtype)
            self.matrix.data[:] = arr.reshape(shape)

    def readWert(self, f):
        line = f.readline()
        while line.startswith("*") or line == "\n":
            line = f.readline()
        Wert = int(line.strip())
        return Wert

    def read_values_to_array(self, f, arr, sep=' '):
        """read values to a numpy array at pos x"""
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

    def read_values_in_o_format_to_list(self, f):
        """read values to a numpy array at pos x"""
        rows = deque()
        for line in f:
            if line.startswith("*") or line == '\n':
                continue
            if line.startswith('$'):
                return rows, line
            row = line.strip()
            rows.append(row)
        return rows, line

    def readWerte(self, f, AnzWerte):
        Werte = []
        WerteGefunden = 0
        while WerteGefunden < AnzWerte:
            line = f.readline()
            while line.startswith("*"):
                line = f.readline()
            Werte += map(lambda x: float(x), line.strip().split())
            WerteGefunden = len(Werte)
        return Werte

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', dest='fn')
    options = parser.parse_args()
    ds = ReadPTVMatrix(options.fn)

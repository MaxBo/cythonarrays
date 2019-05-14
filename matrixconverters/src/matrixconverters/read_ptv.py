import sys
import io
import gzip
import zlib
from collections import deque
import numpy as np
import xarray as xr


class ReadPTVMatrix(xr.Dataset):
    """reads PTV-Matrix from file
    the matrix-type is determined by the header
    reades $M, $V, $O, $E, and the binary types $BI, $BK and $B
    """

    def __init__(self, filename, header=2048, zipped=False):
        """
        read a PTV-Matrix and return it as an xarray-dataset

        Parameters
        ----------
        filename: str
            path to file on disk
        header: int, optional (default=2048)
            length ot the header of a binary file
        zipped: bool, optional (default=False)
            true, if file is zipped
        """
        super().__init__()
        self.attrs['fn'] = filename
        self.attrs['ZeitVon'] = 0
        self.attrs['ZeitBis'] = 0
        self.attrs['Faktor'] = 1
        self.attrs['VMAktKennung'] = 0
        self.attrs['AnzBezeichnerlisten'] = 1

        self._set_open_method(filename, zipped)
        with self._openfile(mode='rb') as f:
            line = f.readline().strip()

            errmsg = 'Matrix type not recognised form Header {}'.format(line)

        if line.startswith(bytes([3, 0])) and \
           line.startswith(b'$B', 2) and len(line) >= 4:
            # binary format
            if chr(line[4]) in 'IKL':
                self.readPTVMatrixBKI()
            else:
                self.readPTVMatrixB(header=header)
        elif line.startswith(b'$') and len(line) > 1:
            # text format
            matrix_type = chr(line[1])
            if line.startswith(b"$"):
                read_methods = {
                    #'M': self.readPTVMatrixM,
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
            self.readPTVMatrixB(header=header)

        del self.attrs['open']

    def readPTVMatrixO(self):
        """read a file in O-Format"""
        with self._openfile(mode="r") as f:
            rows = self.read_header(f)
        loc = self.matrix.loc
        for row in rows:
            r = row.split()
            fr = int(r[0])
            to = int(r[1])
            value = float(r[2])
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

    def read_header(self, f):
        """
        read the header

        Parameters
        ----------
        f : file-obj

        Returns
        -------
        rows: list
        """
        line = f.readline()
        MatrixTyp = line.split("$")[-1].split(";")[0]
        if "M" in MatrixTyp:
            self.attrs['VMAktKennung'] = self.readWert(f)

        if "N" not in MatrixTyp:
            ZeitVon, ZeitBis, Faktor = self.read_values(f, 3)
            self.attrs['ZeitVon'] = ZeitVon
            self.attrs['ZeitBis'] = ZeitBis
            self.attrs['Faktor'] = Faktor

        rows, line = self.read_values_in_o_format_to_list(f)
        self.read_names_o_format(f, line)
        return rows

    def _set_open_method(self, filename, zipped):
        """
        set the file-open-method

        Parameters
        ----------
        filename : str

        zipped : bool
        """
        if filename.endswith(".gzip") or zipped:
            self.attrs['open'] = gzip.open
        elif sys.version_info[0] > 2:
            self.attrs['open'] = open
        else:
            self.attrs['open'] = io.open

    def _openfile(self, mode='r', encoding='latin1'):
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
        open_method = self.attrs['open']
        if mode.endswith('b'):
            encoding = None
        return open_method(self.attrs['fn'], mode=mode, encoding=encoding)

    def readPTVMatrixV(self):
        """read a file in V-Format"""
        with self._openfile() as f:
            line = f.readline()
            MatrixTyp = line.split("$")[-1].split(";")[0]
            if not MatrixTyp.startswith("V"):
                print("Keine Matrix im V-Format!")
                raise TypeError
            if "M" in MatrixTyp:
                self.attrs['VMAktKennung'] = self.readWert(f)

            if "N" not in MatrixTyp:
                ZeitVon, ZeitBis, Faktor = self.read_values(f, 3)
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

    def create_zone_names(self, n_zones, name='zone_name', dim='zone_no'):
        coord = getattr(self, dim).data
        self[name] = xr.DataArray(
            np.empty((n_zones, ), dtype='O'),
            coords=(coord, ),
            dims=(dim,),
            name=name,)

    def create_matrix(self, n_zones, n_cols=None, dtype='f8'):
        n_cols = n_cols or n_zones
        origins = self.zone_no
        destinations = getattr(self, 'zone_no2', origins)
        self['matrix'] = xr.DataArray(
            np.empty((n_zones, n_cols), dtype=dtype),
            coords=(origins, destinations),
            dims=('origins', 'destinations'),
            name='matrix',)

    def create_zones(self, n_zones, name='zone_no', dim = 'zones'):
        self.coords[name] = xr.DataArray(np.arange(n_zones, dtype='i4'),
                                         dims=(dim,),)

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

    def readPTVMatrixBKI(self):
        """
        Die Länge des Headers stehen in Byte 5/6
        Zuerst wird mit Hilfe dieses offsets die Anzahl der Zellen ausgelesen
        und eine leere Matrix gebildet
        dann werden Verkehrsmittelkennung gelesen.
        Dann folgen die Zellennummern
        Schlieslich wird für jede Zeile der Matrix zuerst
        die Länge der gepakten Daten dieser Zeile (lenChunk) gelesen
        und dann die Daten mit zlib.decompress entpackt
        und mit np.frombuffer in ein Zeilen-array verwandelt,
        Damit wird die Matrix zeilenweise "gefüllt"
        Zwischen den Zeilen befinden sich jeweils 16 byte,
        deren Sinn unklar ist (ggf. eine Prüfsumme?)
        Diese werden ignoriert.
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

            data_types = {2: 'i2', 3: 'i4', 4: 'f4', 5: 'f8',}
            dtype = data_types.get(data_type, 'f8')


            if compression_type == 'I':
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
                self.create_matrix(n_zones, n_cols=n_cols, dtype=dtype)

                self.zone_no.data[:] = np.frombuffer(
                    f.read(n_zones * 4), dtype="i4")
                self.zone_no2.data[:] = np.frombuffer(
                    f.read(n_cols * 4), dtype="i4")

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
                raise IOError("Flag of allnull doesn't exist.")

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
                    #else:
                        #self.matrix[i] = np.frombuffer(f.read(n_cols*8),
                                                       #dtype='f8')
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

    def read_utf16(self, f):
        """read utf16( encoded string from file at current position"""
        n_chars = self.read_i4(f)
        return f.read(n_chars * 2).decode('utf16')

    @staticmethod
    def read_f4(f):
        """read float from file at current position"""
        return np.frombuffer(f.read(4), dtype="f4")[0]

    @staticmethod
    def read_f8(f):
        """read double from file at current position"""
        return np.frombuffer(f.read(8), dtype="f8")[0]

    @staticmethod
    def read_u1(f):
        """read byte from file at current position"""
        return np.frombuffer(f.read(1), dtype="u1")[0]

    @staticmethod
    def read_i2(f):
        """read short integer from file at current position"""
        return np.frombuffer(f.read(2), dtype="i2")[0]

    @staticmethod
    def read_i4(f):
        """read integer from file at current position"""
        return np.frombuffer(f.read(4), dtype="i4")[0]

    def readPTVMatrixB(self, header=2048):
        """read non-compressed binary format"""
        with self._openfile(mode="rb") as f:
            f.seek(header)
            f.seek(2, 1)
            Dimensions = np.frombuffer(f.read(2), dtype="i2")[0]
            MatrixZeilen = np.frombuffer(f.read(4), dtype="i4")[0]
            f.seek(4, 1)
            MatrixSpalten = np.frombuffer(f.read(4), dtype="i4")[0]
            f.seek(4, 1)
            if Dimensions == 3:
                MatrixBlock = np.frombuffer(f[header + 20:header + 24],
                                            dtype="i4")[0]
                f.seek(4, 1)
                shape = (MatrixBlock, MatrixZeilen, MatrixSpalten)
            elif Dimensions == 2:
                MatrixBlock = 1
                shape = (MatrixZeilen, MatrixSpalten)
            else:
                msg = 'only 2d or 3d dimensions allowed, found %s dimensions'
                raise ValueError(msg % Dimensions)
            data_type = np.frombuffer(f.read(2), dtype="i2")
            if data_type == 3:
                data_length = 4
                dtype = '<f4'
            elif data_type == 4:
                data_length = 8
                dtype = '<f8'
            else:
                data_length = 8
                dtype = '<f8'
            AnzBezeichnerlisten = np.frombuffer(f.read(2),
                                                dtype="i2")
            AnzFelder = MatrixZeilen * MatrixSpalten * MatrixBlock

            n_zones = max(MatrixZeilen, MatrixSpalten)
            self.create_zones(n_zones)
            self.attrs['ZeitVon'] = int(np.frombuffer(f.read(4), dtype="f4"))
            self.attrs['ZeitBis'] = int(np.frombuffer(f.read(4), dtype="f4"))
            self.attrs['VMAktKennung'] = int(
                np.frombuffer(f.read(4), dtype="i4"))
            self.attrs['Faktor'] = int(np.frombuffer(f.read(4), dtype="f4"))
            if AnzBezeichnerlisten > 0:
                self.zone_no.data[:] = np.frombuffer(
                    f.read(4 * n_zones), dtype='i4')
            self.create_matrix(n_zones, dtype=dtype)
            arr = np.frombuffer(f.read(AnzFelder * data_length), dtype=dtype)
            self.matrix.data[:] = arr.reshape(shape)

    def readWert(self, f):
        """read a single value from the file"""
        line = f.readline().strip()
        while not line or line.startswith("*"):
            line = f.readline()
        Wert = int(line)
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
            row = line.strip()
            if not row or row.startswith("*"):
                continue
            if row.startswith('$'):
                return rows, row
            rows.append(row)
        return rows, row

    def read_values(self, f, n_values):
        values = []
        found = 0
        while found < n_values:
            line = f.readline()
            while line.startswith("*"):
                line = f.readline()
            values += map(lambda x: float(x), line.strip().split())
            found = len(values)
        return values

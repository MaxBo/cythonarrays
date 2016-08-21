#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import gzip
import zlib



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
        self.attrs['fn']= filename
        if filename.endswith(".gzip") or zipped:
            self.attrs['open'] = gzip.open
        else:
            self.attrs['open'] = open
        with self.openfile(mode='rb') as f:
            Z = f.readline().strip()

        if Z.startswith(b"$M"):
            self.readPTVMatrixM()
        elif Z.startswith(b"$V"):
            self.readPTVMatrixV()
        elif Z.startswith(b"$O"):
            self.readPTVMatrixO()
        elif Z.startswith(b"$E"):
            self.readPTVMatrixE()
        elif Z.strip(bytes([3, 0])).startswith(b"$BI"):
            self.readPTVMatrixBI()
        elif Z.strip(bytes([3, 0])).startswith(b"$BK"):
            self.readPTVMatrixBK()
        elif Z.strip(bytes([3, 0])).startswith(b"$B"):
            self.readPTVMatrixB()

        # hier kommen noch mehr Matrix-Formate
        #
        #
        else:
            self.readPTVMatrixB(openFile, fileName, header)
        #self = super(ReadPTVMatrix, cls).__new__(cls, data=array)
        #for attr in ['ZeitVon', 'ZeitBis', 'Faktor', 'VMAktKennung', 'Unbek1',
                     #'Unbek2', 'AnzBezeichnerlisten', 'u2', 'u3']:
            #if hasattr(array, attr):
                #setattr(self, attr, getattr(array, attr))
        #self.zones = zones

    def readPTVMatrixO(self):
        with self.open(self.filename) as f:
            Z = f.readline()
            MatrixTyp = Z.split("$")[-1].split(";")[0]
            if not MatrixTyp.startswith("O"):
                print("Keine Matrix im O-Format!")
                raise TypeError

            if "M" in MatrixTyp:
                VMAktKennung = readWert(f)

            if not "N" in MatrixTyp:
                ZeitVon, ZeitBis, Faktor = readWerte(f, 3)

            if "00" in MatrixTyp:
                AnzBezirke = readWert(f)
                MatrixObj = readWerte2Matrix(f, AnzBezirke)
                ZellenNr = []
                Zellen = Zones(range(AnzBezirke))

            else:
                MatrixObj, Zellen = readWerte2Dict(f)
            try:
                MatrixObj.VMAktKennung = VMAktKennung
            except:
                pass
            try:
                (MatrixObj.ZeitVon,
                 MatrixObj.ZeitBis,
                 MatrixObj.Faktor) = ZeitVon, ZeitBis, Faktor
            except:
                pass
        return MatrixObj, Zellen

    def openfile(self, mode='r'):
        return self.attrs['open'](self.attrs['fn'], mode=mode)

    def readPTVMatrixM(self):
        with self.open(self.filename) as f:
            Z = f.readline()
            if not Z.strip().startswith("$M"):
                print("Keine Matrix im M-Format!")
                raise TypeError
            VMAktKennung = readWert(f)
            AnzBezirke = readWert(f)
            ZellenNr = readWerte(f, AnzBezirke)
            MatrixObj = readWerte2Matrix(f, AnzBezirke)
            Zellen = Zones(ZellenNr)
            MatrixObj.zones = Zellen
            MatrixObj.VMAktKennung = VMAktKennung
        return MatrixObj, Zellen

    def readPTVMatrixV(self):
        with self.openfile() as f:
            Z = f.readline()
            MatrixTyp = Z.split("$")[-1].split(";")[0]
            if not MatrixTyp.startswith("V"):
                print("Keine Matrix im V-Format!")
                raise TypeError
            if "M" in MatrixTyp:
                self.attrs['VMAktKennung'] = self.readWert(f)

            if not "N" in MatrixTyp:
                ZeitVon, ZeitBis, Faktor = self.readWerte(f, 3)
                self.attrs['ZeitVon'] = ZeitVon
                self.attrs['ZeitBis'] = ZeitBis
                self.attrs['Faktor'] = Faktor

            n_zones = self.readWert(f)
            self.create_zones(n_zones)
            pos = 0
            self.read_values_to_array(f, self.zone_no)

            self.create_matrix(n_zones)
            self.read_values_to_array(f, self.matrix)
            self.create_zone_names(n_zones)
            self.read_names(f, self.zone_names)

    def create_zone_names(self, n_zones, name='zone_names'):
        self[name] = xr.DataArray(
            np.empty((n_zones, ), dtype='O'),
            coords=(self.zone_no.data, ),
            dims=('zone',),
            name=name,)

    def create_matrix(self, n_zones, dtype='f8'):
        self['matrix'] = xr.DataArray(
            np.empty((n_zones, n_zones), dtype=dtype),
            coords=(self.zone_no, self.zone_no),
            dims=('origin', 'destination'),
            name='matrix',)

    def create_zones(self, n_zones):
        self['zone_no'] = xr.DataArray(np.empty((n_zones, ), dtype='i4'),
                                       name='zone_no',
                                       dims=('zones',),)

    def read_names(self, f, arr):
        """Read the zone names"""
        Z = f.readline()
        while Z.startswith("*") or Z == "\n":
            Z = f.readline()
        if Z:
            if Z.upper().startswith('$NAMES'):

                line = f.readline().strip()
                while line:
                    l = line.split(' "')
                    zone_no = int(l[0])
                    name = l[1].strip('"')
                    arr.loc[zone_no] = name
                    line = f.readline().strip()

    def readPTVMatrixE(self):
        f = openFile(fileName)
        Z = f.readline()
        MatrixTyp = Z.split("$")[-1].split(";")[0]
        if not MatrixTyp.startswith("E"):
            print("Keine Matrix im E-Format!")
            raise TypeError
        if "M" in MatrixTyp:
            VMAktKennung = readWert(f)

        if not "N" in MatrixTyp:
            ZeitVon, ZeitBis, Faktor = readWerte(f, 3)

        MatrixObj, Zellen = readEWerte2DictE(f)
        try:
            MatrixObj.VMAktKennung = VMAktKennung
        except:
            pass
        try:
            (MatrixObj.ZeitVon,
             MatrixObj.ZeitBis,
             MatrixObj.Faktor) = ZeitVon, ZeitBis, Faktor
        except:
            (MatrixObj.ZeitVon,
             MatrixObj.ZeitBis,
             MatrixObj.Faktor) = 0., 0., 1.
        MatrixObj.Unbek1 = 0.
        return MatrixObj, Zellen

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
        with self.openfile(mode="rb") as file:
            f = file.read()
        header = np.fromstring(f[5:7], dtype="i2")[0] + 23
        n_zones = np.fromstring(f[header:header + 4], dtype="i4")[0]
        self.create_zones(n_zones)

        data_type = np.fromstring(f[header + 4:header + 6], dtype="i2")[0]
        if data_type == 4:
            data_length = 4
            dtype = '<f4'
        elif data_type == 5:
            data_length = 8
            dtype = '<f8'
        self.create_matrix(n_zones, dtype=dtype)

        self.attrs['VMAktKennung'] = np.fromstring(f[header - 16:header - 14],
                                                   dtype="i2")[0]
        self.attrs['Unbek1'] = f[header + 6]
        AnzZellen2 = np.fromstring(f[header + 7:header + 11], dtype="i4")[0]
        idx = header + 11 + n_zones * 4
        self.zone_no.data[:] = np.fromstring(f[header + 11:idx], dtype="i4")
        ZellenList2 = np.fromstring(f[idx:header + 11 + n_zones * 4 * 2],
                                       dtype="i4")
        startpos = header + 11 + n_zones * 4 * 2
        self.create_zone_names(n_zones)
        for i in range(n_zones):
            Zeichen = np.fromstring(f[startpos:startpos + 4], dtype="i4")[0]
            endpos = startpos + 4 + Zeichen * 2
            self.zone_names.data[i] = f[startpos + 4:endpos].decode('utf16')
            startpos += (4 + Zeichen * 2)
        self.create_zone_names(n_zones, name='zone_names2')
        for i in range(AnzZellen2):
            Zeichen = np.fromstring(f[startpos:startpos + 4], dtype="i4")[0]
            endpos = startpos + 4 + Zeichen * 2
            self.zone_names2.data[i] =f[startpos + 4:endpos].decode('utf16')
            startpos += (4 + Zeichen * 2)
        startpos += 1
        self.attrs['Unbek1'] = np.fromstring(f[startpos:startpos + 8],
                                             dtype="f8")[0]
        startpos += 8
        for i in range(n_zones):
            lenChunk = np.fromstring(f[startpos:startpos + 4], dtype="i4")[0]
            startpos += 4
            unpacked = zlib.decompress(f[startpos:startpos + lenChunk])
            self.matrix[i] = np.fromstring(unpacked, dtype=dtype)
            startpos += lenChunk + 16

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
        f = openFile(fileName, "rb").read()
        header = np.fromstring(f[5:7], dtype="i2")[0] + 23
        n_zones = np.fromstring(f[header:header + 4], dtype="i4")[0]
        data_type = np.fromstring(f[header + 4:header + 6], dtype="i2")[0]
        if data_type == 4:
            data_length = 4
            dtype = '<f4'
        elif data_type == 5:
            data_length = 8
            dtype = '<f8'
        MatrixObj = XArray.zeros((AnzZellen, AnzZellen), dtype=dtype)
        MatrixObj.VMAktKennung = np.fromstring(f[header - 16:header - 14],
                                                  dtype="i2")[0]
        MatrixObj.Unbek1 = np.fromstring(f[header + 6], dtype="i1")[0]
        ZellenList = np.fromstring(f[header + 7:header + 7 + AnzZellen * 4],
                                      dtype="i4")
        startpos = header + 16 + AnzZellen * 4
        MatrixObj.Unbek2 = np.fromstring(f[startpos - 8:startpos],
                                            dtype="f8")[0]
        for i in range(n_zones):
            lenChunk = np.fromstring(f[startpos:startpos + 4], dtype="i4")[0]
            startpos += 4
            unpacked = zlib.decompress(f[startpos:startpos + lenChunk])
            MatrixObj[i] = np.fromstring(unpacked, dtype=dtype)
            startpos += lenChunk + 16
        Zellen = Zones(ZellenList)
        MatrixObj.zones = Zellen
        return MatrixObj, Zellen

    def readPTVMatrixB(self, header=2048):
        f = openFile(fileName, "rb").read()
        Dimensions = np.fromstring(f[header + 2:header + 4], dtype="i2")[0]
        MatrixZeilen = np.fromstring(f[header + 4:header + 8], dtype="i4")[0]
        MatrixSpalten = np.fromstring(f[header + 12:header + 16],
                                         dtype="i4")[0]
        if Dimensions == 3:
            MatrixBlock = np.fromstring(f[header + 20:header + 24],
                                           dtype="i4")[0]
            header += 8
            shape = (MatrixBlock, MatrixZeilen, MatrixSpalten)
        elif Dimensions == 2:
            MatrixBlock = 1
            shape = (MatrixZeilen, MatrixSpalten)
        else:
            msg = 'only 2d or 3d dimensions allowed, found %s dimensions'
            raise ValueError(msg % Dimensions)
        data_type = np.fromstring(f[header + 20:header + 22], dtype="i2")
        if data_type == 3:
            data_length = 4
            dtype = '<f4'
        elif data_type == 4:
            data_length = 8
            dtype = '<f8'
        AnzBezeichnerlisten = np.fromstring(f[header + 22:header + 24],
                                               dtype="i2")
        AnzFelder = MatrixZeilen * MatrixSpalten * MatrixBlock
##        AnzZellen = MatrixSpalten
        AnzZellen = max(MatrixZeilen, MatrixSpalten)
        StartPosMatrix = header + AnzBezeichnerlisten * (AnzZellen * 4) + 40
        EndPosMatrix = StartPosMatrix + AnzFelder * data_length
        MatrixObj = XArray.fromstring(f[StartPosMatrix:EndPosMatrix],
                                      dtype=dtype).reshape(shape)
        if AnzBezeichnerlisten > 0:
            StartPosZellenNr = StartPosMatrix - AnzZellen * 4
            ZellenList = np.fromstring(f[StartPosZellenNr:StartPosMatrix],
                                          dtype="i4")
            Zellen = Zones(ZellenList)
            MatrixObj.zones = Zellen
        MatrixObj.Faktor = np.fromstring(f[StartPosZellenNr - 4:
                                              StartPosZellenNr],
                                            dtype="f4")[0]
        MatrixObj.VMAktKennung = np.fromstring(f[StartPosZellenNr - 8:
                                                    StartPosZellenNr - 4],
                                                  dtype="i4")[0]
        MatrixObj.ZeitVon = int(np.fromstring(f[StartPosZellenNr - 16:
                                                   StartPosZellenNr - 12],
                                                 dtype="f4"))
        MatrixObj.ZeitBis = int(np.fromstring(f[StartPosZellenNr - 12:
                                                   StartPosZellenNr - 8],
                                                 dtype="f4"))
        return MatrixObj, Zellen


    def readWert(self, f):
        Z = f.readline()
        while Z.startswith("*") or Z == "\n":
            Z = f.readline()
        Wert = int(Z.strip())
        return Wert

    def read_values_to_array(self, f, arr, sep=' '):
        """read values to a numpy array at pos x"""
        flat_arr = arr.data.ravel()
        n_total = len(flat_arr)
        pos_from = 0
        while pos_from < n_total:
            Z = f.readline()
            while Z.startswith("*"):
                Z = f.readline()
            row = np.fromstring(Z, sep=sep, dtype=arr.dtype)
            pos_to = pos_from + len(row)
            flat_arr[pos_from:pos_to] = row
            pos_from = pos_to


    def readWerte(self, f, AnzWerte):
        Werte = []
        WerteGefunden = 0
        while WerteGefunden < AnzWerte:
            Z = f.readline()
            while Z.startswith("*"):
                Z = f.readline()
            Werte += map(lambda x: float(x), Z.strip().split())
            WerteGefunden = len(Werte)
        return Werte


    def readWerte2Matrix(self, f, AnzBezirke):
        Matrix = []
        ZellwerteGefunden = 0
        AnzFelder = AnzBezirke ** 2
        while ZellwerteGefunden < AnzFelder:
            Z = f.readline()
            while Z.startswith("*"):
                Z = f.readline()
            Matrix += map(lambda x: float(x), Z.strip().split())
            ZellwerteGefunden = len(Matrix)
        MatrixObj = XArray(Matrix).reshape(AnzBezirke, -1)
        return MatrixObj


def readWerte2Dict(f):
    Werte = {}
    ZellenNr = []
    Z = f.readline()
    while Z != "":
        while Z.startswith("*"):
            Z = f.readline()
        VonNachWert = Z.strip().split()
        Von = int(VonNachWert[0])
        Nach = int(VonNachWert[1])
        Wert = float(VonNachWert[2])
        Werte[(Von, Nach)] = Wert
        Z = f.readline()
    ZellenNr = np.unique(np.array(Werte.keys()))
    AnzBezirke = len(ZellenNr)
    MatrixObj = XArray(np.zeros((AnzBezirke, AnzBezirke)))
    for VonNach, Wert in Werte.items():
        VonIndex, NachIndex = ZellenNr.searchsorted(VonNach)
        MatrixObj[VonIndex, NachIndex] = Wert
    Zellen = Zones(ZellenNr)
    return MatrixObj, Zellen


def readEWerte2DictE(f):
    Werte = {}
    ZellenNr = []
    Z = f.readline()
    while Z != "":
        while Z.startswith("*"):
            Z = f.readline()
        VonNachWerte = Z.strip().split()
        Von = -int(VonNachWerte[0])
        for i in range(1, len(VonNachWerte), 2):
            Nach = int(VonNachWerte[i])
            Wert = float(VonNachWerte[i + 1])
            Werte[(Von, Nach)] = Wert
        Z = f.readline()
    ZellenNr = np.unique(np.array(Werte.keys()))
    AnzBezirke = len(ZellenNr)
    MatrixObj = XArray.zeros((AnzBezirke, AnzBezirke))
    for VonNach, Wert in Werte.items():
        VonIndex, NachIndex = ZellenNr.searchsorted(VonNach)
        MatrixObj[VonIndex, NachIndex] = Wert
    Zellen = Zones(ZellenNr)
    return MatrixObj, Zellen

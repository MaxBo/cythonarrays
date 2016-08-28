# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Name:        saveArray
# Purpose:
#
# Author:      Max Bohnet
#
# Created:     21/09/2011
# Copyright:   (c) Max Bohnet 2011
#------------------------------------------------------------------------------

__version__ = 1.0

import os
import gzip
import time
import numpy as np

def writeFormattedLine(f, text, length):
    f.write(text.ljust(length) + b"\r\n")


class SavePTV(object):

    def __init__(self, ds):
        """"""
        self.ds = ds


    def save2db(self, tableName, connection='hlocalhost',
                overwrite=True, missings=[99999, np.inf, -np.inf],
                saveFlattened=False, debug=False):
        """
        saves 2D-array into postgresql database table
        with 3 columns: q (from row), z (to column), value

        Parameters
        ----------
        tableName : string
            Name of the table to be created in the db
        conn : connection object
            an open connection to a postgresql Database.
            If conn is None, than a new connection is opened
            with the following parameters:
        overwrite : bool
            if true, than a table is overwritten if it already exists.
            This is the default.
        missing : bool
            if value in the list of missing values,
            than now row will be written
        saveFlattened : bool
            if True, than the array is flattened before beeing saved
        debug : bool
            print debug messages if true
        """

        #ToDo:
        #- save several arrays of the same shape
        # into same dbtable with one value column per array

        t0 = time.time()

        if saveFlattened:
            array = self.flatten()
        else:
            array = self

        if isinstance(self, np.ndarray):
            from StringIO import StringIO
            if isinstance(connection, psycopg2._psycopg.connection):
                conn = connection
                keepConnOpen = True
            else:
                keepConnOpen = False
                fileConfig()
                pool = get_connection_pool(connection)
                conn = pool.getconn()
            try:
                cur = conn.cursor()
                if array.ndim == 2:
                    primaryKeys = 'q integer, z integer'
                elif array.ndim == 1:
                    primaryKeys = 'z integer'
                sql = """create or replace function build_foo_table()
                returns void as $$;
                         CREATE TABLE %(tn)s (%(pk)s, value double precision);
                        $$ language sql;

                         create or replace function truncate_foo_table()
                         returns void as $$;
                         TRUNCATE %(tn)s;
                         ALTER TABLE %(tn)s DROP CONSTRAINT %(tn)s_pkey;
                        $$ language sql;

                        create or replace function foo_table_exists()
                        returns int as $$
                         select count(table_name)::int
                         from information_schema.tables
                         where table_name = '%(tn)s'
                         and table_schema = '%(schema)s';
                        $$ language sql;

                        select case when foo_table_exists()=0
                        then build_foo_table()
                        else truncate_foo_table() end;

                        drop function build_foo_table();
                        drop function truncate_foo_table();
                        drop function foo_table_exists();


                """ % {'tn': tableName, 'schema': 'h', 'pk': primaryKeys}

                cur.execute(sql)
                if debug:
                    t1 = time.time()
                    print('initTables: %0.2f' % (t1 - t0))
                    t0 = t1
                has_zones = hasattr(self, 'zones')
                if has_zones:
                    zoneids_z = self.zones.ids
                    zoneids_q = self.zones.ids
                else:
                    zoneids_z = dict(zip(xrange(array.shape[-1]),
                                         xrange(array.shape[-1])))
                    if array.ndim == 2:
                        zoneids_q = dict(zip(xrange(array.shape[0]),
                                             xrange(array.shape[0])))
                pos = 0
                buf = StringIO()
                if array.ndim == 2:
                    for i in range(array.rows):
                        row = '\n'.join(['%d\t%d\t%s' % (zoneids_q[i],
                                                         zoneids_z[j],
                                                         array[i, j])
                                         for j in range(array.cols)
                                         if array[i, j] not in missings])
                        if row:
                            buf.write(row + '\n')

                        if not (i + 1) % 1000:
                            buf.seek(pos)
                            cur.copy_from(buf, tableName)
                            pos = buf.pos
                            conn.commit()
                            print(i + 1, zoneids_q[i], pos)

                elif array.ndim == 1:
                    row = '\n'.join(['%d\t%s' % (zoneids_z[j], array[j])
                                     for j in range(array.cols)
                                     if array[j] not in missings])
                    if row:
                        buf.write(row + '\n')

                buf.seek(pos)
                if debug:
                    t1 = time.time()
                    print('Built buffer: %0.2f' % (t1 - t0))
                    t0 = t1
                cur.copy_from(buf, tableName)
                if debug:
                    t1 = time.time()
                    print('executed sql: %0.2f' % (t1 - t0))
                    t0 = t1
                    if array.ndim == 2:
                        print(i + 1, zoneids_q[i], pos)
                conn.commit()
                if debug:
                    t1 = time.time()
                    print('Commit: %0.2f' % (t1 - t0))
                    t0 = t1

                buf.close()
                sql = 'ALTER TABLE %(tn)s ADD PRIMARY KEY (%(pk)s);'
                sql = sql % {'tn': tableName,
                             'pk': primaryKeys.replace(' integer', '')}
                cur.execute(sql)
                if debug:
                    t1 = time.time()
                    print('executed add index: %0.2f' % (t1 - t0))
                    t0 = t1
                conn.commit()
                if debug:
                    t1 = time.time()
                    print('Commit add index: %0.2f' % (t1 - t0))
                    t0 = t1

            finally:
                if not keepConnOpen:
                    conn.close()

    def savePTVMatrix(self, file_name, Ftype, version=0.11,
                      AnzBezeichnerlisten=1, zipped=False):
        """
        save array im PTV-Format

        Parameters
        ----------
        file_name : string
            output file_name
        FType : {'B', 'V'}
            Type of PTV-File Format
            either als binary file ("B")
            or as V-Format ("V").
        version : srting
            version number
        AnzBezeichnerlisten : integer
            Number of lists containing zone attributes (numbers, names)
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

        if Ftype.startswith("B"):
            self.write_format_b(OpenFile, fn, version)
        elif Ftype.startswith("V"):
            self.write_format_v(OpenFile, fn, Ftype)

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
            if not "N" in Ftype:
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

            if 'zone_names' in self.ds:
                zone_names = self.ds.zone_names.data
                fmt = '{no} "{name}"\n'
                for i in range(n_zones):
                    f.write(fmt.format(no=zone_no[i], name=zone_names[i]))

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
                typecode = '<f4'
            # AnzBezeichnerlisten, was immer das auch ist ???
            f.write(np.array(anz_bez_listen, dtype="i2").tostring())
            f.write(np.array(ZeitVon, dtype="f4").tostring())  # ZeitVon
            f.write(np.array(ZeitBis, dtype="f4").tostring())  # ZeitBis
            # VMAktKennung
            f.write(np.array(VMAktKennung, dtype="i4").tostring())
            # Unbekannt U als float
            f.write(np.array(Faktor, dtype="<f4").tostring())
            f.write(np.array(self.ds.zone_no.data).astype("i4").tostring())  # zones
            f.write(m.astype(typecode).flatten().tostring())  # Matrix

    def savePSVMatrix(self, fileName, type="CC", maxWidth=1000):
        """ exports array in PSV-Format
        """
        if not hasattr(self, 'zones'):
            self.zones = range(1, self.rows + 1)
        f = open(fileName, "w")
        try:
            Za = max(self.rows, self.cols)
            Zi = min(self.rows, self.cols)
            f.write("%s; Za %s; Zi %s;\n" % (type, Za, Zi))
            if type == "CC":
                for i in range(self.rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if self[i].any():
                        # addiere 1, um Zellennummer 0 zu vermeiden
                        row = str(self.zones[i])
                        for j in range(self.cols):
                            if len("%s %s %s" % (row, self.zones[j],
                                                 self[i, j])) >= maxWidth:
                                row += "\n"
                                f.write(row)
                                row = str(self.zones[i])
                            if self[i, j] != 0:
                                row += " %s %s " % (self.zones[j], self[i, j])
                        row += "\n"
                        f.write(row)

            elif type == "CN":
                for i in range(self.rows):
                    # teste, ob Zeile nicht nur aus Nullen besteht
                    if self[i].any():
                        row = str(self.zones[i])
                        for j in range(self.cols):
                            if len("%s %s" % (row, self[i, j])) >= maxWidth:
                                row += "\n"
                                f.write(row)
                                row = str(self.zones[i])
                            row += " " + str(self[i, j])
                        row += "\n"
                        f.write(row)
            else:
                raise(TypeError, "Kann Typ %s nicht schreiben" % type)
        finally:
            f.close()




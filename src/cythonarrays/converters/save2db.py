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
import cPickle
import time
import numpy
import psycopg2
from simcommon.matrixio.zones import Zones
from simcommon.matrixio.helpers.database import fileConfig, get_connection_pool

def writeFormattedLine(f, text, length):
    f.write(text.ljust(length) + "\r\n")


class XArraySave(object):

    def save(self, fileName, overwrite=True):
        """
        saves array into a gzipped-file with fileName in a binary format
        open with the load function of this module
        """
        if overwrite or not os.path.exists(fileName):
            f = gzip.open(fileName, 'wb', compresslevel=2)
            cPickle.dump(self.__array__(), f, 1)
            f.close()
        else:
            print "file", fileName, "already exists"
            raise IOError

    def save2db(self, tableName, connection='hlocalhost',
                overwrite=True, missings=[99999, numpy.inf, -numpy.inf],
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

        if isinstance(self, numpy.ndarray):
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
                    print 'initTables: %0.2f' % (t1 - t0)
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
                            print i + 1, zoneids_q[i], pos

                elif array.ndim == 1:
                    row = '\n'.join(['%d\t%s' % (zoneids_z[j], array[j])
                                     for j in range(array.cols)
                                     if array[j] not in missings])
                    if row:
                        buf.write(row + '\n')

                buf.seek(pos)
                if debug:
                    t1 = time.time()
                    print 'Built buffer: %0.2f' % (t1 - t0)
                    t0 = t1
                cur.copy_from(buf, tableName)
                if debug:
                    t1 = time.time()
                    print 'executed sql: %0.2f' % (t1 - t0)
                    t0 = t1
                    if array.ndim == 2:
                        print i + 1, zoneids_q[i], pos
                conn.commit()
                if debug:
                    t1 = time.time()
                    print 'Commit: %0.2f' % (t1 - t0)
                    t0 = t1

                buf.close()
                sql = 'ALTER TABLE %(tn)s ADD PRIMARY KEY (%(pk)s);'
                sql = sql % {'tn': tableName,
                             'pk': primaryKeys.replace(' integer', '')}
                cur.execute(sql)
                if debug:
                    t1 = time.time()
                    print 'executed add index: %0.2f' % (t1 - t0)
                    t0 = t1
                conn.commit()
                if debug:
                    t1 = time.time()
                    print 'Commit add index: %0.2f' % (t1 - t0)
                    t0 = t1

            finally:
                if not keepConnOpen:
                    conn.close()

    def savePTVMatrix(self, FileName, Ftype, zones=None, version=0.11,
                      Faktor=1, AnzBezeichnerlisten=1, zipped=False):
        """
        save array im PTV-Format

        Parameters
        ----------
        FileName : string
            output FileName
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
            fn = FileName + ".gzip"
        else:
            OpenFile = open
            fn = FileName

        if zones is None:
            if hasattr(self, 'zones'):
                zones = self.zones
            else:
                zones = Zones(xrange(self.shape[-1]))
        elif not isinstance(zones, Zones):
            zones = Zones(zones)

        if not hasattr(self, "ZeitVon"):
            self.ZeitVon = 0.
        if not hasattr(self, "ZeitBis"):
            self.ZeitBis = 24.
        if not hasattr(self, "Faktor"):
            self.Faktor = 1.
        if not hasattr(self, "VMAktKennung"):
            self.VMAktKennung = 0

        if Ftype == "B":
            f = OpenFile(fn, "wb")
            writeFormattedLine(f, "PTVSYSTEM   MUULI       VMatrixComp1", 44)
            writeFormattedLine(f, "VMatversionsnummer: %0.2f" % version, 28)
            writeFormattedLine(f, "Anzahl Dimensionen: %d" % self.ndim, 28)
            writeFormattedLine(f, "Seitenlaengen der Matrix:", 30)
            text = ""
            for n in range(self.ndim):
                text += ("%d" % self.shape[n]).ljust(8)
            writeFormattedLine(f, text, 48)
            writeFormattedLine(f, "% -30s%d" % ("Anzahl Bezeichnerlisten:",
                                                AnzBezeichnerlisten),
                               38)
            writeFormattedLine(f, "% -20s%02d:00   %02d:00" % ("Zeitbereich:",
                                                               self.ZeitVon,
                                                               self.ZeitBis),
                               36)
            writeFormattedLine(f, "% -20s%s" % ("RandomRound:", "Nein"), 28)
            writeFormattedLine(f, "% -24s%0.2f" % ("Faktor:", Faktor), 28)
            for i in range(20):
                writeFormattedLine(f, " ", 80)
            f.write(numpy.array(6682, dtype="i2").tostring())  # header
            f.write(" " * 80)
            f.write(numpy.array(11, dtype="i2").tostring())  # header
            f.write(numpy.array(self.ndim, dtype="i2").tostring())  # Dimensions
            # Zeilen je Dimension
            f.write(numpy.array(self.shape[-2], dtype="i4").tostring())
            f.write(numpy.array(2080, dtype="i4").tostring())  # header
            # Spalten
            f.write(numpy.array(self.shape[-1], dtype="i4").tostring())
            f.write(numpy.array(2080, dtype="i4").tostring())  # ???
            if self.ndim == 3:
                # Bloecke
                f.write(numpy.array(self.shape[0], dtype="i4").tostring())
                f.write(numpy.array(2080, dtype="i4").tostring())  # ???

            if self.dtype.char == 'f':
                # 3 Datentyp float
                f.write(numpy.array(3, dtype="i2").tostring())
                typecode = '<f4'
            elif self.dtype.char == 'd':
                # 4 Datentyp double
                f.write(numpy.array(4, dtype="i2").tostring())
                typecode = '<f8'
            else:
                # z.B. integer oder unsigned integer:
                # 3 Datentyp float
                # ToDo: Prüfen!!!
                f.write(numpy.array(3, dtype="i2").tostring())
                typecode = '<f4'
            # AnzBezeichnerlisten, was immer das auch ist ???
            f.write(numpy.array(1, dtype="i2").tostring())
            f.write(numpy.array(self.ZeitVon, dtype="f4").tostring())  # ZeitVon
            f.write(numpy.array(self.ZeitBis, dtype="f4").tostring())  # ZeitBis
            # VMAktKennung
            f.write(numpy.array(self.VMAktKennung, dtype="i4").tostring())
            # Unbekannt U als float
            f.write(numpy.array(self.Faktor, dtype="<f4").tostring())
            f.write(numpy.array(zones.values).astype("i4").tostring())  # zones
            f.write(self.astype(typecode).flatten().tostring())  # Matrix

            f.close()
        elif Ftype.startswith("V"):
            dtypes = {'float32': "Y4", 'float64': "Y5",
                      'int32': "Y3", 'int16': "Y2"}
            outformat = {'float32': "%0.3f", 'float64': "%0.6f",
                         'int32': "%d", 'int16': "%d"}
            f = OpenFile(fn, "w")
            f.write("$%s, %s\n" % (Ftype, dtypes[str(self.dtype)]))
            if "M" in Ftype:
                f.write("* Verkehrsmittelkennung:\n %d \n" % self.VMAktKennung)
            if not "N" in Ftype:
                f.write("* Zeitintervall:\n %s %s \n" % (self.ZeitVon,
                                                         self.ZeitBis))
                f.write("* Faktor:\n %d \n" % Faktor)
            f.write("*Anzahl Bezirke:\n %d\n" % self.shape[0])
            f.write("* Bezirksnummern\n")
            for i in range(0, zones.count, 10):
                f.write("\t".join(map(lambda x:
                                      str(x),
                                      zones.values[i: i + 10])) + "\n")
            f.write("* Matrixwerte\n")
            for i in range(zones.count):
                Bezirksnummer = zones.values[i]
                f.write("* %s \n" % Bezirksnummer)
                for j in range(0, zones.count, 10):
                    f.write("\t".join(map(lambda x:
                                          outformat[str(self.dtype)] % x,
                                          self[i, j: j + 10])) + "\n")
            f.close()

        elif Ftype.startswith("BK"):
            raise NotImplementedError('Binary Format still to be implemented')

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
                            if self[i, j] <> 0:
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
                raise TypeError, "Kann Typ %s nicht schreiben" % type
        finally:
            f.close()




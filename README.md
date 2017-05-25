# cythonarrays
Python Package to facilitate cython cdef-classes that expose memoryviews as numpy arrays

it consists of three packages

cythoninstallhelpers:
a package that provides functions that are used in the setup.py of cythonarrays
therefore, it has to be installed first

cythonarrays: 
provides a Base-Class for cython CDef-Classes, that allow to define arrays
as attributes which can be used in cython code as fast memoryviews and at the same time
be accessed from python as numpy-arrays
In addition, the dimensions and shapes of data assigned to the arrays is checked automatically.
If you try to set data with wrong dimensions or shapes, an error is thrown.
Data is automatically converted to the right dtype.

matrixconverters:
tools to read and write matrices in the format or PTV VISUM



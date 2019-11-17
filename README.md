
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://travis-ci.org/MaxBo/cythonarrays.svg?branch=master)](https://travis-ci.org/MaxBo/cythonarrays)
[![Build status](https://ci.appveyor.com/api/projects/status/q0lek1t5tl5lcq29?svg=true)](https://ci.appveyor.com/project/MaxBo/cythonarrays)
[![codecov](https://codecov.io/gh/MaxBo/cythonarrays/branch/master/graph/badge.svg)](https://codecov.io/gh/MaxBo/cythonarrays)

# cythonarrays
Python Packages to facilitate cython cdef-classes that expose memoryviews as numpy arrays.

It consists of three packages:

**cythoninstallhelpers**:
[![PyPI version](https://badge.fury.io/py/cythoninstallhelpers.svg)](https://badge.fury.io/py/cythoninstallhelpers)
[![Anaconda-Server Badge](https://anaconda.org/maxbo/cythoninstallhelpers/badges/version.svg)](https://anaconda.org/maxbo/cythoninstallhelpers)

a package that provides functions that are used in the setup.py of cythonarrays
therefore, it has to be installed first

**cythonarrays**:
[![PyPI version](https://badge.fury.io/py/cythonarrays.svg)](https://badge.fury.io/py/cythonarrays)
[![Anaconda-Server Badge](https://anaconda.org/maxbo/cythonarrays/badges/version.svg)](https://anaconda.org/maxbo/cythonarrays)

provides a Base-Class for cython CDef-Classes, that allow to define arrays
as attributes which can be used in cython code as fast memoryviews and at the same time
be accessed from python as numpy-arrays
In addition, the dimensions and shapes of data assigned to the arrays is checked automatically.
If you try to set data with wrong dimensions or shapes, an error is thrown.
Data is automatically converted to the right dtype.


**matrixconverters**:
[![PyPI version](https://badge.fury.io/py/matrixconverters.svg)](https://badge.fury.io/py/matrixconverters)
[![Anaconda-Server Badge](https://anaconda.org/maxbo/matrixconverters/badges/version.svg)](https://anaconda.org/maxbo/matrixconverters)

tools to read and write matrices in the format or PTV VISUM

[Documentation](https://maxbo.github.io/cythonarrays/)

# Installation
You can use pip to install the packages (and the requirements like numpy).

```
pip install cythoninstallhelpers
pip install cythonarrays
pip install matrixconverters
```
Another way to handle dependencies is to use [conda](https://conda.io/miniconda.html).

There conda packages for python 3.5-3.8 for windows and linux are generated in the channel *MaxBo* in [Anaconda Cloud](https://anaconda.org/MaxBo).
```
conda create -n myenv python=3.6
activate myenv

conda config --add channels conda-forge
conda config --add channels MaxBo

conda install cythonarrays
conda install matrixconverters
```

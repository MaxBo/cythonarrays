
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) 
[![Build Status](https://travis-ci.org/MaxBo/cythonarrays.svg?branch=master)](https://travis-ci.org/MaxBo/cythonarrays) 
[![Build status](https://ci.appveyor.com/api/projects/status/q0lek1t5tl5lcq29?svg=true)](https://ci.appveyor.com/project/MaxBo/cythonarrays)

# cythonarrays
Python Packages to facilitate cython cdef-classes that expose memoryviews as numpy arrays.

It consists of three packages:

**cythoninstallhelpers**:
a package that provides functions that are used in the setup.py of cythonarrays
therefore, it has to be installed first

**cythonarrays**: 
provides a Base-Class for cython CDef-Classes, that allow to define arrays
as attributes which can be used in cython code as fast memoryviews and at the same time
be accessed from python as numpy-arrays
In addition, the dimensions and shapes of data assigned to the arrays is checked automatically.
If you try to set data with wrong dimensions or shapes, an error is thrown.
Data is automatically converted to the right dtype.

**matrixconverters**:
tools to read and write matrices in the format or PTV VISUM

[Documentation](https://maxbo.github.io/cythonarrays/)

# Installation

The easiest way to handle dependencies is to use [conda](https://conda.io/miniconda.html).

There conda packages for python 3.5 and 3.6 for windown and linux are generated in the channel *MaxBo* in [Anaconda Cloud](https://anaconda.org/MaxBo).
```
conda create -n myenv python=3.6
activate myenv

conda config --add channels conda-forge
conda config --add channels MaxBo

conda install cythonarrays
conda install matrixconverters
```
Without conda, you can use pip to install the packages, if you have the requirements like numpy installed.

```
pip install cythoninstallhelpers
pip install cythonarrays
pip install matrixconverters
```

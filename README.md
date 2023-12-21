
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![Build Status Linux](https://github.com/MaxBo/cythonarrays/actions/workflows/linux-conda.yml/badge.svg)](https://github.com/MaxBo/cythonarrays/actions/workflows/linux-conda.yml)
[![Build Status Windows](https://github.com/MaxBo/cythonarrays/actions/workflows/windows-conda.yml/badge.svg)](https://github.com/MaxBo/cythonarrays/actions/workflows/windows-conda.yml)
[![codecov](https://codecov.io/gh/MaxBo/cythonarrays/branch/master/graph/badge.svg)](https://codecov.io/gh/MaxBo/cythonarrays)

# cythonarrays
Python Packages to facilitate cython cdef-classes that expose memoryviews as numpy arrays.

##cythonarrays:
[![PyPI version](https://badge.fury.io/py/cythonarrays.svg)](https://badge.fury.io/py/cythonarrays)
[![Anaconda-Server Badge](https://anaconda.org/maxbo/cythonarrays/badges/version.svg)](https://anaconda.org/maxbo/cythonarrays)

provides a Base-Class for cython CDef-Classes, that allow to define arrays
as attributes which can be used in cython code as fast memoryviews and at the same time
be accessed from python as numpy-arrays
In addition, the dimensions and shapes of data assigned to the arrays is checked automatically.
If you try to set data with wrong dimensions or shapes, an error is thrown.
Data is automatically converted to the right dtype.


[Documentation](https://maxbo.github.io/cythonarrays/)

# Installation
You can use pip to install the packages (and the requirements like numpy).

```
pip install cythonarrays
```

Another way to handle dependencies is to use [conda](https://conda.io/miniconda.html).

There conda packages for python 3.8-3.12 for windows and linux are generated
in the channel *MaxBo* in [Anaconda Cloud](https://anaconda.org/MaxBo).

```
conda create -n myenv python=3.12
conda activate myenv

conda config --add channels conda-forge
conda config --add channels MaxBo

conda install cythonarrays
```

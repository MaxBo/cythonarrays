# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:33:08 2016

@author: MaxBohnet
"""

from setuptools import setup, find_packages
from cythoninstallhelpers.get_version import get_version
from cythoninstallhelpers.make_cython_extensions import make_extensions


ext_modnames = []

package_name = "matrixconverters"
version = get_version(package_name, __file__)

setup(
    name=package_name,
    version=version,
    description="package to read and write PTV-Visum Matrix Formats",
    url='https://maxbo.github.io/cythonarrays/',
    author='Max Bohnet',
    author_email='bohnet@ggr-planung.de',
    classifiers=[
        # How mature is this project? Common values are
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Cython',

    ],
    keywords='Visum PTV Matrix numpy xarray',

    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    package_data={'': ['*.pxd', '*.mtx', '*.csv']},
    include_package_data=True,
    zip_safe=False,
    data_files=[
        ],

    tests_require=['pytest', ],

    install_requires=[
        'xarray',
        'netCDF4',
        'cythoninstallhelpers',
    ],
    ext_modules=make_extensions(ext_modnames),
)
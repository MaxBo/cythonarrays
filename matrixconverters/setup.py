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
    description="functions to read and write PTV Matrix Formats",

    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    package_data={'': ['*.pxd']},
    include_package_data=True,
    zip_safe=False,
    data_files=[
        ],

    extras_require=dict(
        extra=[],
        docs=[
            'z3c.recipe.sphinxdoc',
            'sphinxcontrib-requirements'
        ],
        test=[]
    ),
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],

    install_requires=[
        'numpy>1.12',
        'pandas',
        'xarray',
    ],
    ext_modules=make_extensions(ext_modnames),
)
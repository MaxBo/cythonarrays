# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:33:08 2016

@author: MaxBohnet
"""

from setuptools import setup, find_packages
from cythoninstallhelpers.get_version import get_version
from cythoninstallhelpers.make_cython_extensions import make_extensions


ext_modnames = ['cythonarrays.array_shapes',
                ]

package_name = "cythonarrays"
version = get_version(package_name, __file__)

setup(
    name=package_name,
    version=version,
    description="helper functions for cythonarrays",

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
        'cythoninstallhelpers>=1.1',
        'cython',
        'numpy',
    ],
    ext_modules=make_extensions(ext_modnames),
)
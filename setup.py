# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:33:08 2016

@author: MaxBohnet
"""

from setuptools import setup, find_packages
from cythoninstallhelpers.make_cython_extensions import make_extensions


ext_modnames = ['cythonarrays.array_shapes',
                ]

setup(
    name="cythonarrays",
    version="1.1",
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

    install_requires=[
        'cythoninstallhelpers'
    ],
    ext_modules=make_extensions(ext_modnames),
)
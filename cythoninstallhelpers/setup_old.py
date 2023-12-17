# -*- coding: utf-8 -*-

from setuptools import setup, find_namespace_packages


setup(
    packages=find_namespace_packages('src', exclude=['ez_setup']),

    package_dir={'': 'src'},
    package_data={'': ['*.pxd', '*.pyx', '*.pyxbld'],},
    include_package_data=True,
)


# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version_dict = dict()
exec(open(os.path.join(os.path.dirname(__file__),
                       'src',
                       "cythoninstallhelpers",
                       '_version.py')).read(),
     version_dict)

setup(
    name="cythoninstallhelpers",
    version=version_dict['__version__'],
    description="helper for cython installation",
    classifiers=[
      "Programming Language :: Python",
      "Environment :: Plugins",
      "Intended Audience :: System Administrators",
      "License :: Other/Proprietary License",
      "Natural Language :: English",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
                ],
    keywords='cython',
    download_url='',
    license='other',
    packages=find_packages('src', exclude=['ez_setup']),

    package_dir={'': 'src'},
    package_data={'': ['*.pxd']},
    include_package_data=True,
    zip_safe=False,
    data_files=[],
    install_requires=[
        'setuptools',
        'cython',
        ],
)


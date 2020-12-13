# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""
from setuptools.dist import Distribution
from setuptools.command.build_ext import build_ext
import importlib.util
import shutil
from distutils.extension import Extension
import numpy as np
import sys
import os
import pytest
import tempfile
import gc
from cythoninstallhelpers.make_cython_extensions import make_extensions


@pytest.fixture(scope='class')
def packagename() -> str:
    # return the package name for the test-class
    packagename = 'cythoninstallhelpers.tests.examplepackage'
    yield packagename

@pytest.fixture(scope='class')
def extension_name(packagename) -> str:
    return f'{packagename}.example_cython'

@pytest.fixture(scope='class')
def tmpdir(extension_name) -> str:
    """return a temp folder"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestMakeExtensions:
    """Test making cython extensions"""

    def test_01_make_extension(self,
                               packagename: str,
                               extension_name: str,
                               tmpdir: str):
        """Test the creation of an extension"""
        source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # make the extension module
        extension_modules = make_extensions([extension_name],
                                            source_dir=source_dir)
        # test, if the extension module build in the fixture has the right name
        extension = extension_modules[0]
        assert extension.name == extension_name
        # and the according C-file
        assert extension.sources[0].split(os.sep)[-1] == 'example_cython.c'

        # Create a distribution named examplepackage, including the extension modules
        dist = Distribution(dict(ext_modules=extension_modules))#
        dist.metadata.name = 'cythoninstallhelpers.tests.examplepackage'
        dist.packages = ['cythoninstallhelpers.tests.examplepackage']
        #  change the working directory to the test file's directory
        # to ensure the test runs from whereever it is called
        os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        package_dir = '.'
        dist.package_dir = {'': package_dir,}
        cmd = build_ext(dist)
        cmd.finalize_options()
        cmd.build_lib = tmpdir
        cmd.build_temp = tmpdir
        cmd.run()

        # move the created pyd/so-file to the source folder
        # otherwise the temp folder cannot be deleted
        ext_path = cmd.get_ext_fullpath(extension.name)
        ext_fn = cmd.get_ext_filename(extension.name)
        dest_fn = os.path.join(source_dir, ext_fn)
        if os.path.exists(dest_fn):
            os.remove(dest_fn)
        shutil.move(ext_path, dest_fn)

        # import the module from the file
        spec = importlib.util.spec_from_file_location(extension.name, dest_fn)
        example_cython = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(example_cython)
        print('Import successful')

        # run a Cdef-function built with Openmp
        # and check if the results are as expected
        ex = example_cython.Example(2, 3, 4, 5)
        ret = ex.calc_array(22.2)
        np.testing.assert_almost_equal(ex.rowsums, [51.6, 251.4])
        assert ret == 151.5
        print('Calculation successful')

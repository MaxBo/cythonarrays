# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""
from setuptools.dist import Distribution
from setuptools.command.build_ext import build_ext
import importlib.util
import numpy as np
import os
from cythoninstallhelpers.make_cython_extensions import make_extensions


class TestMakeExtensions:
    """Test making cython extensions"""

    def test_01_make_extension(self, tmpdir: str):
        """Test the creation of an extension"""
        source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        dest_fn = tmpdir.strpath
        packagename = 'cythoninstallhelpers.tests.examplepackage'
        extension_name = f'{packagename}.example_cython'
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
        dist.metadata.name = packagename
        dist.packages = [packagename]
        #  change the working directory to the test file's directory
        # to ensure the test runs from whereever it is called
        os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        package_dir = '.'
        dist.package_dir = {'': package_dir,}
        cmd = build_ext(dist)
        cmd.finalize_options()
        cmd.build_lib = dest_fn
        cmd.build_temp = dest_fn
        cmd.run()

        ext_fn = cmd.get_ext_filename(extension.name)
        file_location = os.path.join(dest_fn, ext_fn)
        # import the module from the file
        spec = importlib.util.spec_from_file_location(extension.name, file_location)
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

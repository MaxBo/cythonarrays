# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

from setuptools.dist import Distribution
from setuptools.command.develop import develop
import subprocess
from distutils.extension import Extension
import numpy as np
import sys
import os
import pytest
from cythoninstallhelpers.make_cython_extensions import make_extensions


@pytest.fixture(scope='class')
def packagename() -> str:
    # return the package name for the test-class
    packagename = 'examplepackage'
    yield packagename
    # clean up by uninstalling the package after the tests
    print(f'Uninstall {packagename}')
    executable = os.path.join(sys.exec_prefix, 'python')
    subprocess.call([executable, '-m', 'pip', 'uninstall', '-y', packagename])


@pytest.fixture(scope='class')
def extension_name(packagename) -> str:
    return f'{packagename}.example_cython'


class TestMakeExtensions:
    """Test making cython extensions"""

    def test_01_make_extension(self,
                               packagename: str,
                               extension_name: str):
        """Test the creation of an extension"""
        source_dir = os.path.join(os.path.dirname(__file__), 'src')
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
        dist.metadata.name = 'examplepackage'
        dist.packages = ['examplepackage']
        #  change the working directory to the test file's directory
        # to ensure the test runs from whereever it is called
        os.chdir(os.path.dirname(__file__))
        package_dir = os.path.join('src')
        dist.package_dir = {'': package_dir,}
        dist.script_name = os.path.join(os.path.dirname(__file__), 'setup.py')
        dist.script_args = ['develop', '--user']

        # install the examplepackage distribution with python setup.py develop
        cmd = develop(dist)
        cmd.finalize_options()
        cmd.run()
        # add the egg_path to sys.path
        if not cmd.egg_path in sys.path:
            sys.path.append(cmd.egg_path)
        import examplepackage.example_cython
        print('Import successful')

    def test_02_run_extension(self):
        """Test if the extension can be imported and does what it should do"""
        # import the Test-Class from the extension-module
        from examplepackage.example_cython import Example
        print('2nd Import successful')

        # run a Cdef-function built with Openmp
        # and check if the results are as expected
        ex = Example(2, 3, 4, 5)
        ret = ex.calc_array(22.2)
        np.testing.assert_almost_equal(ex.rowsums, [51.6, 251.4])
        assert ret == 151.5
        print('Calculation successful')

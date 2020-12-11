# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

from setuptools.dist import Distribution
from setuptools.command.build_ext import build_ext
import numpy as np
import sys
import gc
import os
import shutil
from cythoninstallhelpers.make_cython_extensions import make_extensions


class TestMakeExtensions:
    """Test making cython extensions"""
    def remove_compiled_module(self):
        """check if the compiled module is already installed and delete it otherwise"""
        try:
            import cythoninstallhelpers.tests.example_cython as mod
            path = mod.__file__
            mod_name = mod.__name__
            if mod_name in sys.modules:
                del sys.modules[mod_name]
            del mod
            gc.collect()
            try:
                os.remove(path)
            except PermissionError:
                trash = move_file(path)
                shutil.rmtree(trash, ignore_errors=True)
        except (ImportError):
            pass

    def test_01_make_extension(self):
        """Test the creation of an extension"""
        self.remove_compiled_module()

        source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        extension_name = 'cythoninstallhelpers.tests.example_cython'
        extension_modules = make_extensions([extension_name],
                                     source_dir=source_dir)
        extension = extension_modules[0]
        assert extension.name == extension_name
        assert extension.sources[0].split(os.sep)[-1] == 'example_cython.c'
        dist = Distribution(dict(ext_modules=extension_modules))
        dist.script_name = 'install'
        cmd = build_ext(dist)
        cmd.run_command('install')

    def test_02_run_extension(self):
        """Test if the extension can be imported and does what it should do"""
        from cythoninstallhelpers.tests.example_cython import Example
        ex = Example(2, 3, 4, 5)
        ret = ex.calc_array(22.2)
        np.testing.assert_almost_equal(ex.rowsums, [51.6, 251.4])
        assert ret == 151.5
        self.remove_compiled_module()

def move_file(path):
    trash = os.path.join(os.path.dirname(path), 'trash')
    os.makedirs(trash, exist_ok=True)
    dest_path = os.path.join(trash, os.path.basename(path))
    try:
        os.remove(dest_path)
    except PermissionError:
        pass
    if os.path.exists(path):
        os.rename(path, dest_path)
    return trash

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

import pytest
import os
from cythoninstallhelpers.get_version import get_version


class TestVersion:
    """Test reading the version"""
    @classmethod
    def setup_class(cls):
        """dummy directories"""
        cls.installdir = os.path.dirname(os.path.dirname(__file__))
        cls.setuppy = os.path.join(cls.installdir, 'setup.py')

    def test_01_read_correct_version(self):
        """Test reading a correct version file"""

        version = get_version(package_name='tests',
                              setupfilepath=self.setuppy,
                              package_dir='',
                              versionfile='_version.py')

        assert version == '0.7.1a'

    def test_02_read_still_ok_version(self):
        """Test reading a version file that works"""

        version = get_version(package_name='tests',
                              setupfilepath=self.setuppy,
                              package_dir='',
                              versionfile='_version2.py')

        assert version == '0.8.1'

    def test_03_read_incorrect_version(self):
        """Test reading a broken correct version file"""
        version_file = '_version_broken.py'
        version_path = os.path.join(self.installdir, 'tests', version_file)
        msg = "Unable to find version string in {:s}.".format(version_path,)

        with pytest.raises(RuntimeError,) as excinfo:
            version = get_version(package_name='tests',
                                  setupfilepath=self.setuppy,
                                  package_dir='',
                                  versionfile=version_file)
        assert excinfo.value.args[0] == msg

    def test_04_read_nonexistent_version(self):
        """Test reading a non existent version file"""
        version_file = '_version_nonexistant.py'
        version_path = os.path.join(self.installdir, 'tests', version_file)
        msg = 'Version file {} not found'.format(version_path)

        with pytest.raises(IOError) as excinfo:
            version = get_version(package_name='tests',
                                  setupfilepath=self.setuppy,
                                  package_dir='',
                                  versionfile=version_file)

        assert excinfo.value.args[0] == msg

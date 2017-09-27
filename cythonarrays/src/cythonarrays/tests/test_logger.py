# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 21:00:21 2016

@author: MaxBohnet
"""

from cythonarrays.configure_logger import (SimLogger,
                                           get_module_logger,
                                           get_logger)
import tempfile
import shutil
import os
import glob


class Test01_Logger:
    """Test the the SimLogger"""
    @classmethod
    def setup_class(cls):
        cls.LOG_FOLDER = tempfile.mkdtemp(prefix='Log_')
        print(cls.LOG_FOLDER)
        cls.scenario = 'TestScenario'
        sim_logger = SimLogger()
        print(sim_logger.packages)
        sim_logger.add_packages(['cythonarrays',
                                 'cythoninstallhelpers',
                                 'numpy'])
        sim_logger.configure(LOG_FOLDER=cls.LOG_FOLDER,
                             scenario=cls.scenario)
        print(sim_logger.packages)

    @classmethod
    def teardown_class(cls):
        try:
            shutil.rmtree(cls.LOG_FOLDER)
        except PermissionError:
            pass

    def test_02_log_something(self):
        """log something to the logger"""
        logger = get_logger(self)
        logger.info('Info in test_02')
        logger.debug('Debug in test_02')
        logger.warn('Warn in test_02')
        logfiles = glob.glob(os.path.join(self.LOG_FOLDER,
                                          '{}*.log'.format(self.scenario)))
        assert logfiles
        print(logfiles)
        for logfile in logfiles:
            with open(logfile) as f:
                for line in f:
                    print(line.strip())



    def test_03_module_logger(self):
        """Test the module logger"""
        module_logger = get_module_logger(self.__module__)
        module_logger.info('Info in Module {}'.format(self.__module__))


if __name__ == '__main__':
    pytest.main()
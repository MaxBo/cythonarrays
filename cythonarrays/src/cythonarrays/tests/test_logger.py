# -*- coding: utf-8 -*-

from cythonarrays.configure_logger import (SimLogger,
                                           get_module_logger,
                                           get_logger)
import os
import glob
from .module_with_logging import function_with_logging
from .example_python import _Example


class Test01_Logger:
    """Test the the SimLogger"""
    def test_01_log_something(self, tmpdir: str):
        """log something to the logger"""
        print(tmpdir)
        scenario = 'TestScenario_without_Packages'
        sim_logger = SimLogger()
        sim_logger.configure(LOG_FOLDER=tmpdir, scenario=scenario)
        print(sim_logger.packages)

        function_with_logging('Log something in function_with_logging without package')

        logger = get_logger(self)
        logger.info('Info in test_01')
        logger.debug('Debug in test_01')
        logger.warning('Warn in test_01')

        logger = get_logger(_Example)
        logger.warn('Logging for the cython module')

        instance = 'A String'
        logger = get_logger(instance)
        logger.info('Logging for an str-instance form builtins without module')

        print(sim_logger.packages)

        logfiles = glob.glob(os.path.join(tmpdir, f'{scenario}*.log'))
        assert logfiles
        print(logfiles)
        for logfile in logfiles:
            with open(logfile) as f:
                for line in f:
                    print(line.strip())

    def test_03_module_logger(self, tmpdir):
        """Test the module logger"""
        module_logger = get_module_logger(self.__module__)
        module_logger.info('Info in Module {}'.format(self.__module__))

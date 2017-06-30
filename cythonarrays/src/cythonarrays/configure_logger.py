import logging
import datetime
import os
import inspect


class SimLogger(object):
    """
    Singleton Class for the logging
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimLogger, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """ init the sim-logger"""
        if not hasattr(self, 'packages'):
            self.packages = set()
        if not hasattr(self, 'filehandler_initialized'):
            self.filehandler_initialized = False
        # add at least a console handler
        if not hasattr(self, 'ch'):
            self.add_console_handler()

    def add_package(self, package):
        """add single package to the list of logged packages"""
        if package not in self.packages:
            self.packages.add(package)
            self.create_logger_for_package(package)

    def add_packages(self, packages):
        """add list of packages to the list of logged packages"""
        for package in packages:
            self.add_package(package)

    def configure(self,
                  LOG_FOLDER,
                  scenario,
                  mode='a'):
        """
        configures the file handlers for the logger

        Parameters
        ----------
        LOG_FOLDER : str
            the path to the log-folder
        scenario : str
            the name of the scenario used in the log file
        mode : str, optional(Default: 'a')
            a: append
            w: recreate logfile
        """

        iso_date = datetime.date.today().isoformat()
        # define the file where to log
        LOGGING_FILE = os.path.join(LOG_FOLDER,
                                    '{sc}_{date}.log'.format(sc=scenario,
                                                             date=iso_date))
        LOGGING_FILE_DEBUG = os.path.join(LOG_FOLDER,
                                          '{sc}_{date}_debug.log'.format(
                                              sc=scenario,
                                              date=iso_date))

        # create file handler which logs only info messages
        self.fh = logging.FileHandler(LOGGING_FILE, mode=mode)
        self.fh.setLevel(logging.INFO)

        # create file handler which logs even debug messages
        self.fh_debug = logging.FileHandler(LOGGING_FILE_DEBUG, mode=mode)
        self.fh_debug.setLevel(logging.DEBUG)

        # create file formatter and add it to the handlers
        self.fh_debug.setFormatter(self.get_debug_formatter())
        self.fh.setFormatter(self.get_info_formatter())
        self.filehandler_initialized = True

        # configure the file handlers to all given packages
        for package in self.packages:
            self.create_logger_for_package(package)

    def add_console_handler(self):
        # create console handler with a higher log level
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(self.get_info_formatter())

    def get_debug_formatter(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return formatter

    def get_info_formatter(self):
        msg = '%(asctime)s.%(msecs).03d-%(levelname)s->%(message)s'
        formatter_info = logging.Formatter(fmt=msg, datefmt='%H:%M:%S')
        return formatter_info

    def create_logger_for_package(self, package):
        # create a logger for the package
        logger = logging.getLogger(package)
        logger.setLevel(logging.DEBUG)

        # remove existing handlers
        del logger.handlers[:]
        logger.addHandler(self.ch)

        if self.filehandler_initialized:
            # add the handlers to the logger
            logger.addHandler(self.fh)
            logger.addHandler(self.fh_debug)

    @staticmethod
    def get_caller_name(skip=2):
        """
        Get a name of a caller in the format module.class.method

        `skip` specifies how many levels of stack to skip while getting caller
        name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

        An empty string is returned if skipped levels exceed stack height
        """
        stack = inspect.stack()
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]

        name = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(techtonik): consider using __main__
        if module:
            name.append(module.__name__)
        # detect classname
        if 'self' in parentframe.f_locals:
            # I don't know any way to detect call from the object method
            # XXX: there seems to be no way to detect static method call
            #   - it will be just a function call
            name.append(parentframe.f_locals['self'].__class__.__name__)
        codename = parentframe.f_code.co_name
        # top level usually
        if codename != '<module>' and codename != '__init__':
            name.append(codename)  # function or a method
        del parentframe
        return ".".join(name)

    def get(self, instance):
        """
        returns a logger for the current package

        Parameters
        ----------
        instance : object
            the instance to inspect
        """
        if hasattr(instance, '__module__'):
            package = instance.__module__.split('.')[0]
        else:
            package = None
        if package in self.packages:
            caller_name = '.'.join([instance.__module__,
                                    instance.__class__.__name__])
        else:
            caller_name = self.get_caller_name(skip=3)
            print('''logging uses inspect-module, may be slow.
            Consider import from fully qualified namespace package
            (from namespace.{package} import xyz
            instead of from {package} import xyz)'''.format(package=package))

        logger = logging.getLogger(caller_name)
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())
        return logger


def get_module_logger(module_name):
    """create Module logger named after the module"""
    module_logger = logging.getLogger(module_name)
    # Add a NullHandler for the case if no logging is configured by the
    # Application
    module_logger.addHandler(logging.NullHandler())
    return module_logger


def get_logger(instance):
    """
    for the instance, get the package,
    add the package to the list of loggers,
    and return the logger for the instance

    Parameter
    ---------
    instance : object

    Returns
    -------
    logger : logger-instace

    """
    sim_logger = SimLogger()
    if hasattr(instance, '__module__'):
        sim_logger.add_package(instance.__module__.split('.')[0])
    return sim_logger.get(instance)

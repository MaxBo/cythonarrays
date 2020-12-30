from cythoninstallhelpers.configure_logger import get_logger


def function_with_logging(msg: str):
    """a function that logs something"""
    logger = get_logger(function_with_logging)
    logger.info(msg)
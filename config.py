import coloredlogs
import logging
import verboselogs

ADMINS = ("213247101314924545", "399388398990786561", "276519987244695552")
PREFIX = "{"


def getLogger():
    verboselogs.install()
    logger = logging.getLogger("PyBot")
    coloredlogs.install(level="INFO", logger=logger, fmt="[%(levelname)s] %(asctime)s: %(message)s", datefmt="[%m-%d-%Y %I:%M:%S]")
    return logger

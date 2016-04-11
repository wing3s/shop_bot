import os
import sys
import time
import ConfigParser
import logging
import logging.handlers

from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = "Wen-Hao Lee"
__email__ = "wing3s@gmail.com"
__copyright__ = "Copyright 2014, Numnum"

base_path = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read(os.path.join(base_path, 'config.ini'))


def get_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    script_name = os.path.splitext(os.path.basename(file_name))[0]
    log_path = os.path.join(base_path, 'log')

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    fileHandler = logging.handlers.TimedRotatingFileHandler(
        "%s/%s.log" % (log_path, script_name),
        when='midnight',
        backupCount=14)
    fileHandler.suffix = "%Y-%m-%d"
    fileFormatter = logging.Formatter(
        '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
    fileHandler.setFormatter(fileFormatter)
    fileHandler.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleFormatter = logging.Formatter("%(levelname)s - %(message)s")
    consoleHandler.setFormatter(consoleFormatter)
    consoleHandler.setLevel(logging.WARNING)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    return logger


def get_session(env):
    assert env in ['dev', 'stage', 'prod']

    db_url = (
        "mysql://{username}:{psswd}@{host}/{database}?charset=utf8"
        .format(
            host=config.get(env, 'host'),
            username=config.get(env, 'username'),
            psswd=config.get(env, 'psswd'),
            database=config.get(env, 'database')))
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def timeit(logger=None):
    def real_timeit(method):
        @wraps(method)
        def wrap(*args, **kwargs):
            ts = time.time()
            result = method(*args, **kwargs)
            te = time.time()
            msg = (
                "%r (%r, %r) Spent %2.2f sec"
                % (method.__name__, args, kwargs, te-ts))
            if logger:
                logger.info(msg)
            return result
        return wrap
    return real_timeit
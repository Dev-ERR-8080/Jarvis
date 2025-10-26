# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOGFILE = os.path.join(os.path.dirname(__file__), "..", "jarvis.log")
logger = logging.getLogger("jarvis")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    fh = RotatingFileHandler(LOGFILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

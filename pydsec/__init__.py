import logging

from .pydsec import Trend

__all__ = [Trend]

logging.getLogger(__name__).addHandler(logging.NullHandler())

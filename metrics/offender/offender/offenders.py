import logging

from . import utilities

logger = logging.getLogger(__name__)


def get_offenders(project):
    return utilities.CSV.read(f'offender/data/{project}.csv')

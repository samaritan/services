import logging

from . import utilities

logger = logging.getLogger(__name__)


def get_offenders(project):
    offenders = utilities.CSV.read(f'offender/data/{project.repository}.csv')
    for index, _ in enumerate(offenders):
        aliases = offenders[index]['aliases']
        offenders[index]['aliases'] = aliases.split(',') if aliases else None
    return offenders

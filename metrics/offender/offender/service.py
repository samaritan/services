import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc

from .schemas import OffenderSchema
from .offenders import get_offenders

logger = logging.getLogger(__name__)


class OffenderService:
    name = 'offender'

    config = Config()

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        offenders = get_offenders(project)

        return OffenderSchema(many=True).dump(offenders).data

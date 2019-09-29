import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc

from .schemas import OffenderSchema
from .offenders import get_offenders

logger = logging.getLogger(__name__)


class OffenderService:
    name = 'offender'

    config = Config()

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        offenders = get_offenders(project)

        return OffenderSchema(many=True).dump(offenders)

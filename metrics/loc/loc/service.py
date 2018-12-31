import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .sourcecode import SourceCode
from .schemas import LocSchema

logger = logging.getLogger(__name__)


class LocService:
    name = 'loc'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)
        path = self.repository_rpc.get_path(project)
        sourcecode = SourceCode(path, processes)
        locs = sourcecode.get_loc()
        return LocSchema(many=True).dump(locs).data

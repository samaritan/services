import logging

from eventlet.greenpool import GreenPool
from lizard import get_all_source_files, get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Nesting
from .schemas import NestingSchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions(['nd']))  # pylint: disable=invalid-name


def _get_nestings(path, file_):
    nestings = list()

    path = file_.replace(f'{path}/', '')
    for function in analyzer(file_).function_list:
        nesting = function.max_nesting_depth
        nestings.append(Nesting(function.long_name, path, nesting))

    return nestings


class NestingService:
    name = 'nesting'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)
        path = self.repository_rpc.get_path(project)

        pool = GreenPool()
        arguments = ((path, f) for f in get_all_source_files([path], [], None))
        nestings = list()
        for item in pool.starmap(_get_nestings, arguments):
            nestings.extend(item)
        return NestingSchema(many=True).dump(nestings)

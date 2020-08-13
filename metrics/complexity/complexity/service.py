import logging

from eventlet.greenpool import GreenPool
from lizard import get_all_source_files, get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Complexity
from .schemas import ComplexitySchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions([]))  # pylint: disable=invalid-name


def _get_complexities(path, file_):
    complexities = list()

    path = file_.replace(f'{path}/', '')
    for function in analyzer(file_).function_list:
        complexity = function.cyclomatic_complexity
        complexities.append(Complexity(function.long_name, path, complexity))

    return complexities


class ComplexityService:
    name = 'complexity'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)
        path = self.repository_rpc.get_path(project)

        pool = GreenPool()
        arguments = ((path, f) for f in get_all_source_files([path], [], None))
        complexities = list()
        for item in pool.starmap(_get_complexities, arguments):
            complexities.extend(item)
        return ComplexitySchema(many=True).dump(complexities)

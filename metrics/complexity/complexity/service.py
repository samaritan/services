import logging

from eventlet.greenpool import GreenPool
from lizard import get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Complexity
from .schemas import ChangesSchema, ComplexitySchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions([]))  # pylint: disable=invalid-name


def _get_complexities(project, path, change, repository_rpc):
    complexities = list()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(path, content):
            complexity = function.cyclomatic_complexity
            complexity = Complexity(function.long_name, path, complexity)
            complexities.append(complexity)

    return complexities


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


class ComplexityService:
    name = 'complexity'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path=None, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, sha, path)
        changes = ChangesSchema(many=True).load(changes)
        changes = ((p, cc) for c in changes for p, cc in c.changes.items())

        pool = GreenPool()
        arguments = ((project, p, c, self.repository_rpc) for p, c in changes)
        complexities = list()
        for item in pool.starmap(_get_complexities, arguments):
            complexities.extend(item)
        return ComplexitySchema(many=True).dump(complexities)

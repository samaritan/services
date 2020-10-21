import logging

from lizard import get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import ChangesSchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions([]))  # pylint: disable=invalid-name


def _get_complexities(project, path, change, repository_rpc):
    complexities = dict()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(path, content):
            if function.long_name in complexities:
                logger.warning(
                    'Duplicate function %s in %s with complexity %f and %f',
                    function.long_name, path, complexities[function.long_name],
                    function.cyclomatic_complexity
                )
            complexities[function.long_name] = function.cyclomatic_complexity

    return complexities


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


class ComplexityService:
    name = 'complexity'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, sha, path)
        changes = ChangesSchema(many=True).load(changes)
        change = changes[0].changes[path]

        complexities = _get_complexities(
            project, path, change, self.repository_rpc
        )
        return complexities if complexities else None

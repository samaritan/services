import logging

from lizard import get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import ChangesSchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions(['nd']))  # pylint: disable=invalid-name


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


def _get_nestings(project, path, change, repository_rpc):
    nestings = dict()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(path, content):
            if function.long_name in nestings:
                logger.warning(
                    'Duplicate function %s in %s with nesting %f and %f',
                    function.long_name, path, nestings[function.long_name],
                    function.cyclomatic_complexity
                )
            nestings[function.long_name] = function.max_nesting_depth

    return nestings


class NestingService:
    name = 'nesting'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, sha, path)
        changes = ChangesSchema(many=True).load(changes)
        change = changes[0].changes[path]

        nestings = _get_nestings(project, path, change, self.repository_rpc)
        return nestings if nestings else None

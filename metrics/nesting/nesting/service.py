import logging

from eventlet.greenpool import GreenPool
from lizard import get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Nesting
from .schemas import ChangesSchema, NestingSchema

logger = logging.getLogger(__name__)
analyzer = FileAnalyzer(get_extensions(['nd']))  # pylint: disable=invalid-name


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


def _get_nestings(project, path, change, repository_rpc):
    nestings = list()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(path, content):
            nesting = function.max_nesting_depth
            nestings.append(Nesting(function.long_name, path, nesting))

    return nestings


class NestingService:
    name = 'nesting'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, sha)
        changes = ChangesSchema(many=True).load(changes)
        changes = ((p, cc) for c in changes for p, cc in c.changes.items())

        pool = GreenPool()
        arguments = ((project, p, c, self.repository_rpc) for p, c in changes)
        nestings = list()
        for item in pool.starmap(_get_nestings, arguments):
            nestings.extend(item)
        return NestingSchema(many=True).dump(nestings)

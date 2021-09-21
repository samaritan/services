import logging

from lizard import get_extensions, FileAnalyzer
from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import ChangeSchema

METRIC = 'complexity'
analyzer = FileAnalyzer(get_extensions([]))  # pylint: disable=invalid-name
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


def _get_complexities(project, change, repository_rpc):
    complexities = dict()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(change.path, content):
            if function.long_name in complexities:
                _warn(change.path, function, complexities)
            complexities[function.long_name] = function.cyclomatic_complexity

    return complexities


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


def _warn(path, function, complexities):
    msg = '%s in %s repeated with complexity %f and %f'
    name = function.long_name
    ncm, ocm = function.cyclomatic_complexity, complexities[name]
    logger.warning(msg, name, path, ocm, ncm)


class ComplexityService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        change = self.repository_rpc.get_change(project, sha, path)
        change = ChangeSchema().load(change)

        complexities = _get_complexities(project, change, self.repository_rpc)
        return complexities if complexities else None

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')

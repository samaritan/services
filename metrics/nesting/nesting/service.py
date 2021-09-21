import logging

from kombu.messaging import Exchange, Queue
from lizard import get_extensions, FileAnalyzer
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import ChangeSchema

METRIC = 'nesting'
analyzer = FileAnalyzer(get_extensions(['nd']))  # pylint: disable=invalid-name
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


def _get_functions(path, content):
    return analyzer.analyze_source_code(path, content).function_list


def _get_nestings(project, path, change, repository_rpc):
    nestings = dict()

    content = repository_rpc.get_content(project, change.oids.after)
    if content is not None:
        for function in _get_functions(path, content):
            logger.debug(function.long_name)
            if function.long_name in nestings:
                _warn(change.path, function, nestings)
            nestings[function.long_name] = function.max_nesting_depth

    return nestings


def _warn(path, function, nestings):
    msg = '%s in %s repeated with nesting %f and %f'
    name = function.long_name
    nne, one = function.max_nesting_depth, nestings[name]
    logger.warning(msg, name, path, one, nne)


class NestingService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)
        logger.debug('%s %s', sha, path)

        change = self.repository_rpc.get_change(project, sha, path)
        change = ChangeSchema().load(change)

        nestings = _get_nestings(project, path, change, self.repository_rpc)
        return nestings if nestings else None

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        logger.debug(payload['measure'])
        self.publish(payload, routing_key='measure')

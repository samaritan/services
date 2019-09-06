import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc

from . import utilities
from .parsers import get_parser
from .schemas import FunctionSchema

logger = logging.getLogger(__name__)


class ParserService:
    name = 'parser'

    inferer = utilities.LanguageInferer()
    config = Config()

    @rpc
    def is_supported(self, language):
        return language in self.config['LANGUAGES']

    @rpc
    def get_functions(self, name, contents):
        language = self.inferer.infer(name)
        if language is None:
            logger.debug('%s is in an unsupported language', name)
            return None
        parser = get_parser(language)
        functions = parser.get_functions(name, contents)
        return FunctionSchema(many=True).dump(functions)

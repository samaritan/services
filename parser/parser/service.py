import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc

from . import utilities
from .languages import get_languages
from .parsers import get_parser
from .schemas import FunctionSchema

logger = logging.getLogger(__name__)


class ParserService:
    name = 'parser'

    languages = get_languages()
    inferer = utilities.LanguageInferer()
    config = Config()

    @rpc
    def is_supported(self, language):
        return language in self.languages

    @rpc
    def is_parsable(self, name):
        language = self.inferer.infer(name)
        return language is not None

    @rpc
    def get_functions(self, name, contents):
        functions = None

        language = self.inferer.infer(name)
        if language is None:
            logger.debug('%s is in an unsupported language', name)
        else:
            parser = get_parser(language)
            functions = parser.get_functions(name, contents)
            if functions is not None:
                functions = FunctionSchema(many=True).dump(functions)

        return functions

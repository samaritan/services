import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc

from . import utilities
from .languages import get_languages
from .parsers import get_parser
from .schemas import CommentSchema, FunctionSchema

logger = logging.getLogger(__name__)


class ParserService:
    name = 'parser'

    languages = get_languages()
    inferer = utilities.LanguageInferer(languages)
    config = Config()

    @rpc
    def is_supported(self, language):
        return language in self.languages

    @rpc
    def is_parsable(self, name):
        language = self.inferer.infer(name)
        return language is not None

    @rpc
    def get_comments(self, name, contents):
        comments = None

        language = self.inferer.infer(name)
        if language is None:
            logger.debug('%s is in an unsupported language', name)
        else:
            parser = get_parser(language)
            comments = parser.get_comments(name, contents)
            if comments is not None:
                comments = CommentSchema(many=True).dump(comments)

        return comments

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

    @rpc
    def get_language(self, name):
        return self.inferer.infer(name)

    @rpc
    def get_functions_with_properties(self, name, contents):
        functions = None
        function_list = []

        language = self.inferer.infer(name)
        if language is None:
            logger.debug('%s is an unsupported language', name)
        else:
            parser = get_parser(language)
            functions = parser.get_functions_with_properties(name, contents)

            if functions is not None and functions != {}:
                for key in functions.keys():
                    function_list.append(
                        FunctionSchema(many=False)
                        .dump(functions[key])
                    )

                functions = function_list

        return functions

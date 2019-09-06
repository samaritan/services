from .cparser import CParser
from ..exceptions import NoParser

PARSERS = {'c/c++': CParser}


def get_parser(language):
    language = language.lower()
    if language not in PARSERS:
        raise NoParser(f'No parser to parse files written in {language}')
    return PARSERS[language]()

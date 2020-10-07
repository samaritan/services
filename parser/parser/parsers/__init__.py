from .cparser import CParser
from ..exceptions import NoParser

PARSERS = {'C': CParser, 'C++': CParser}


def get_parser(language):
    if language not in PARSERS:
        raise NoParser(f'No parser to parse files written in {language}')
    return PARSERS[language]()

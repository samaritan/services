from .srcmlparser import SrcMLParser
from ..exceptions import NoParser

PARSERS = {'C': SrcMLParser, 'C++': SrcMLParser, 'Java': SrcMLParser}


def get_parser(language):
    if language not in PARSERS:
        raise NoParser(f'No parser to parse files written in {language}')
    return PARSERS[language](language)

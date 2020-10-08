import logging
import subprocess

from xml.etree import ElementTree

from ..models import Function

logger = logging.getLogger(__name__)

SRC_NS = 'http://www.srcML.org/srcML/src'
POS_NS = 'http://www.srcML.org/srcML/position'
NS = {'src': SRC_NS, 'pos': POS_NS}


def _get_declarations(srcml):
    for function in srcml.findall('src:function_decl', NS):
        name = _get_name(function)
        begin, _ = _get_linerange(function)
        # TODO: Use `end` from `src:function_decl` after Issue #20 is resolved
        parameter_list = function.find('src:parameter_list', NS)
        _, end = _get_linerange(parameter_list)
        yield Function(name=name, lines=(begin, end))


def _get_definitions(srcml):
    for function in srcml.findall('src:function', NS):
        name = _get_name(function)
        begin, end = _get_linerange(function)
        # TODO: Use `end` from `src:function` after Issue #20 is resolved
        block = function.find('src:block', NS)
        block_content = block.find('src:block_content', NS)
        if block_content.attrib:
            _, end = _get_linerange(block_content)
            end += 1
        yield Function(name=name, lines=(begin, end))


def _get_name(element):
    name = element.find('src:name', NS)
    return ''.join(name.itertext()) if name is not None else None


def _get_linerange(element):
    position = element.attrib[f'{{{POS_NS}}}start']
    begin, _ = (int(i) for i in position.split(':'))
    position = element.attrib[f'{{{POS_NS}}}end']
    end, _ = (int(i) for i in position.split(':'))
    return begin, end


def _get_srcml(contents, language):
    try:
        args = ['srcml', '--position', '--language', language, '-']
        process = subprocess.run(
            args, input=contents, check=True, text=True, capture_output=True
        )
        return process.stdout
    except subprocess.CalledProcessError as error:
        logger.exception(error)
    return None


class SrcMLParser:
    def __init__(self, language):
        self._language = language

    def get_functions(self, name, contents):
        functions = None

        srcml = _get_srcml(contents, self._language)
        if srcml is None:
            logger.error('SrcML failed to parse %s', name)
        else:
            functions = list()
            srcml = ElementTree.fromstring(srcml)
            functions.extend(_get_declarations(srcml))
            functions.extend(_get_definitions(srcml))

        return functions

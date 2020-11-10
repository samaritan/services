import logging
import subprocess

from xml.etree import ElementTree

from ..enumerations import CommentType
from ..models import Comment, Function, Position, Span

logger = logging.getLogger(__name__)

COMMENT_TYPE = {'line': CommentType.LINE, 'block': CommentType.BLOCK}
SRC_NS = 'http://www.srcML.org/srcML/src'
POS_NS = 'http://www.srcML.org/srcML/position'
NS = {'src': SRC_NS, 'pos': POS_NS}


def _create_position(line, column):
    return Position(line=line, column=column)


def _get_comments(srcml):
    for comment in srcml.iter(f'{{{SRC_NS}}}comment'):
        begin, end = _get_span(comment)
        type_ = COMMENT_TYPE[comment.get('type')]
        begin, end = _create_position(*begin), _create_position(*end)
        yield Comment(type=type_, span=Span(begin=begin, end=end))


def _get_declarations(srcml):
    for function in srcml.iter(f'{{{SRC_NS}}}function_decl'):
        name = _get_name(function)
        (begin, _), (end, _) = _get_span(function)
        # TODO: Use `end` from `src:function_decl` after Issue #20 is resolved
        parameter_list = function.find('src:parameter_list', NS)
        if parameter_list is not None:
            _, (end, _) = _get_span(parameter_list)
        begin, end = _create_position(begin, None), _create_position(end, None)
        yield Function(name=name, span=Span(begin=begin, end=end))


def _get_definitions(srcml):
    for function in srcml.iter(f'{{{SRC_NS}}}function'):
        name = _get_name(function)
        (begin, _), (end, _) = _get_span(function)
        # TODO: Use `end` from `src:function` after Issue #20 is resolved
        block = function.find('.//src:block', NS)
        if block is not None:
            block_content = block.find('src:block_content', NS)
            if block_content.attrib:
                _, (end, _) = _get_span(block_content)
                end += 1
        begin, end = _create_position(begin, None), _create_position(end, None)
        yield Function(name=name, span=Span(begin=begin, end=end))


def _get_name(element):
    name = element.find('src:name', NS)
    if name is not None:
        name = ''.join(i.strip() for i in name.itertext())
    return name


def _get_span(element):
    position = element.attrib[f'{{{POS_NS}}}start']
    begin = (int(i) for i in position.split(':'))
    position = element.attrib[f'{{{POS_NS}}}end']
    end = (int(i) for i in position.split(':'))
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

    def get_comments(self, name, contents):
        comments = None

        srcml = _get_srcml(contents, self._language)
        if srcml is None:
            logger.error('SrcML failed to parse %s', name)
        else:
            srcml = ElementTree.fromstring(srcml)
            comments = list(_get_comments(srcml))

        return comments

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

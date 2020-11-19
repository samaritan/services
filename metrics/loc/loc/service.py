import enum
import logging
import re

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Loc
from .schemas import ChangeSchema, CommentSchema, FunctionSchema, LocSchema

logger = logging.getLogger(__name__)
NEWLINE_RE = re.compile(r'\r\n?|\n')


class Flag(enum.IntFlag):
    COMMENT = 2
    BLANK = 1
    NONE = 0


def _get_lines(content):
    lines = NEWLINE_RE.split(content)
    return lines[:-1] if lines[-1] == '' else lines  # Handle newline at EOF


def _get_flags(lines, comments):
    flags = [Flag.BLANK if not l else Flag.NONE for l in lines]
    for comment in comments:
        begin, end = comment.span.begin, comment.span.end
        if begin.line == end.line:
            line = lines[begin.line - 1]
            # Line on which the comment exists must not have anything else
            if not line.replace(line[begin.column - 1:end.column], '').strip():
                flags[begin.line - 1] |= Flag.COMMENT
        else:
            line = lines[begin.line - 1]
            # Line on which a comment begins must not have anything else
            if not line.replace(line[begin.column - 1:], '').strip():
                flags[begin.line - 1] |= Flag.COMMENT
            for index in range(begin.line, end.line - 1):
                flags[index] |= Flag.COMMENT
            line = lines[end.line - 1]
            # Line on which a comment ends must not have anything else
            if not line.replace(line[:end.column], '').strip():
                flags[end.line - 1] |= Flag.COMMENT
    return flags


def _get_functionloc(function, flags):
    loc, bloc, cloc = 0, 0, 0
    begin, end = function.span.begin, function.span.end
    for index in range(begin.line - 1, end.line):
        loc += 1
        bloc += 1 if flags[index] == Flag.BLANK else 0
        cloc += 1 if Flag.COMMENT in flags[index] else 0
    sloc = loc - (bloc + cloc)
    return LocSchema().dump(Loc(bloc=bloc, cloc=cloc, sloc=sloc))


def _get_functionsloc(functions, flags):
    loc = dict()
    for function in functions:
        if function.signature in loc:
            logger.warning('Duplicate function `%s`', function.signature)
        loc[function.signature] = _get_functionloc(function, flags)
    return loc


def _get_fileloc(lines, flags):
    bloc, cloc = 0, 0
    for flag in flags:
        bloc += 1 if flag == Flag.BLANK else 0
        cloc += 1 if Flag.COMMENT in flag else 0
    sloc = len(lines) - (bloc + cloc)
    return LocSchema().dump(Loc(bloc=bloc, cloc=cloc, sloc=sloc))


class LocService:
    name = 'loc'

    config = Config()
    parser_rpc = RpcProxy('parser')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug('%s %s %s', project, sha, path)

        granularity = options.get('granularity', 'file')
        if granularity not in {'file', 'function'}:
            granularity = 'file'

        change = self.repository_rpc.get_change(project, sha, path)
        change = ChangeSchema().load(change)

        content = self.repository_rpc.get_content(project, change.oids.after)
        if content is not None:
            lines = _get_lines(content)
            comments = self._get_comments(path, content)
            if comments is not None:
                flags = _get_flags(lines, comments)
                if granularity == 'file':
                    return _get_fileloc(lines, flags)

                functions = self._get_functions(path, content)
                return _get_functionsloc(functions, flags)
        return None

    def _get_comments(self, path, content):
        comments = self.parser_rpc.get_comments(path, content)
        if comments is not None:
            return CommentSchema(many=True).load(comments)
        return None

    def _get_functions(self, path, content):
        functions = self.parser_rpc.get_functions(path, content)
        if functions is not None:
            return FunctionSchema(many=True).load(functions)
        return None

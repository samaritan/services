import logging

import clang.cindex

from ..models import Function

logger = logging.getLogger(__name__)


def _filename_filter(functions, name):
    def _filter(item):
        return item.extent.start.file.name == name and                        \
               item.extent.end.file.name == name
    return filter(_filter, functions)


def _kind_filter(functions):
    kinds = {
        clang.cindex.CursorKind.FUNCTION_DECL,
        clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL
    }
    def _filter(item):
        return item.kind in kinds
    return filter(_filter, functions)


class CParser:
    def get_functions(self, name, contents):
        functions = None
        try:
            functions = list(self._get_functions(name, contents))
        except clang.cindex.TranslationUnitLoadError:
            logger.error('libclang failed to parse %s', name)
        return functions

    def _get_functions(self, name, contents):
        index = clang.cindex.Index.create()
        tunit = index.parse(name, unsaved_files=[(name, contents),])
        cursor = tunit.cursor
        functions = _kind_filter(cursor.get_children())
        for function in _filename_filter(functions, name):
            name = function.spelling
            begin, end = function.extent.start.line, function.extent.end.line
            yield Function(name=name, lines=(begin, end))

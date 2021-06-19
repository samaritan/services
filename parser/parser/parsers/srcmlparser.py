import logging
import re
import subprocess

from xml.etree import ElementTree

from ..enumerations import CommentType
from ..models import Comment, Function, Position, Span, \
     AcyclicalPath, GlobalVariableWrite, FunctionProperties
from ..constants import _get_constants_from_language

logger = logging.getLogger(__name__)

COMMENT_TYPE = {'line': CommentType.LINE, 'block': CommentType.BLOCK}
NEWLINE_RE = re.compile(r'\r\n?|\n')
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
        signature = _get_signature(function)
        (begin, _), (end, _) = _get_span(function)
        # TODO: Use `end` from `src:function_decl` after Issue #20 is resolved
        parameter_list = function.find('src:parameter_list', NS)
        if parameter_list is not None:
            _, (end, _) = _get_span(parameter_list)
        begin, end = _create_position(begin, None), _create_position(end, None)
        yield Function(signature=signature, span=Span(begin=begin, end=end))

def _parse_enum(element):
    enum_names = []

    if element.tag == f'{{{SRC_NS}}}enum':

        enum_block = element.find(f'{{{SRC_NS}}}block')
        enum_decls = (enum_block.findall(f'{{{SRC_NS}}}decl')
        if enum_block is not None else [])

        for decl in enum_decls:
            decl_name = _get_name_from_nested_name(
                decl.find(f'{{{SRC_NS}}}name'))

            decl_name_txt = (
                decl_name.text
                if decl_name is not None and decl_name.text is not None
                else '')

            if decl_name_txt != '':
                enum_names.append(decl_name_txt)

    return list(set(enum_names))

def _get_definitions(srcml, nlines):
    for function in srcml.iter(f'{{{SRC_NS}}}function'):
        signature = _get_signature(function)
        (begin, _), (end, _) = _get_span(function)
        # TODO: Use `end` from `src:function` after Issue #20 is resolved
        block = function.find('.//src:block', NS)
        if block is not None:
            block_content = block.find('src:block_content', NS)
            if block_content.attrib:
                _, (end, _) = _get_span(block_content)
                end += 1
        end = min(end, nlines)  # TODO: Revisit after Issue #20 is resolved
        begin, end = _create_position(begin, None), _create_position(end, None)
        yield Function(signature=signature, span=Span(begin=begin, end=end))

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

def _get_signature(element):
    def _join(values, delimiter=' '):
        return delimiter.join(i.strip() for i in values if i.strip())

    components = list()
    type_ = element.find('src:type', NS)

    if type_ is not None:
        components.append(_join(type_.itertext()))
        components.append(' ')

    components.append(_get_name(element))
    parameters = element.find('src:parameter_list', NS)
    if parameters:
        components.append('(')
        parameters = list(parameters.iterfind('src:parameter', NS))
        for index, parameter in enumerate(parameters):
            components.append(_join(parameter.itertext()))
            if index < len(parameters) - 1:
                components.append(', ')
        components.append(')')

    return ''.join(components) if components else None

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

def _get_name_from_nested_name(name):
    curr, prev = name, None
    while curr is not None:
        prev, curr = curr, curr.find(f'{{{SRC_NS}}}name')
    return prev

def _get_full_name_text_from_name(name):
    name_txt = ''

    if name is not None:
        if name.text is not None:
            name_txt = name.text
        else:
            name_txt = ''.join(n_txt for n_txt in name.itertext())

    return name_txt

def _get_throws_expression_names(element):
    exception_names = []

    if element.tag == f'{{{SRC_NS}}}throws':
        args = element.findall(f'{{{SRC_NS}}}argument')
        for arg in args:
            expr = arg.find(f'{{{SRC_NS}}}expr')
            expr_name = (expr.find(f'{{{SRC_NS}}}name')
            if expr is not None else None)

            name_txt = _get_full_name_text_from_name(expr_name)

            if name_txt != '':
                exception_names.append(name_txt)

    return exception_names

def _get_param_data(function):
    parameter_list = function.find(f'{{{SRC_NS}}}parameter_list')
    parameters = parameter_list.findall(f'{{{SRC_NS}}}parameter')

    parameter_declarations = []
    parameters_passed_by_reference = []

    for param in parameters:
        decl = param.find(f'{{{SRC_NS}}}decl')

        decl_name = (decl.find(f'{{{SRC_NS}}}name')
        if decl is not None else None)

        decl_name_txt = (decl_name.text
        if decl_name is not None and decl_name.text else '')

        decl_type = (decl.find(f'{{{SRC_NS}}}type')
        if decl is not None else None)

        decl_type_name = (decl_type.find(f'{{{SRC_NS}}}name')
        if decl_type is not None else None)

        decl_type_name_txt = (
            decl_type_name.text
            if decl_type_name is not None and decl_type_name.text
            else '')

        decl_type_modifier = (decl_type.find(f'{{{SRC_NS}}}modifier')
        if decl_type is not None
        else None)

        decl_type_modifier_txt = (decl_type_modifier.text
        if decl_type_modifier is not None and decl_type_modifier.text
        else '')

        if decl_type_modifier_txt in {'*', '&'}:
            parameters_passed_by_reference.append(
                {
                    'type': decl_type_name_txt,
                    'modifier': decl_type_modifier_txt,
                    'name': decl_name_txt})

        if decl_name_txt != '':
            parameter_declarations.append(
                {
                    'type': decl_type_name_txt,
                    'modifier': decl_type_modifier_txt,
                    'name': decl_name_txt})

    return {
        'parameters' : parameter_declarations,
        'parameters_passed_by_reference': parameters_passed_by_reference}

def _parse_function_call(element):
    call_data = {}

    if element.tag == f'{{{SRC_NS}}}call':
        call_name = element.find(f'{{{SRC_NS}}}name')
        call_name_txt = _get_full_name_text_from_name(call_name)

        if call_name_txt not in list(call_data) and call_name_txt != '':
            call_data[call_name_txt] ={
                'cumulative_args': []
            }

        if call_name_txt != '':
            call_arg_list = element.find(f'{{{SRC_NS}}}argument_list')

            call_args = (call_arg_list.findall(f'{{{SRC_NS}}}argument')
            if call_arg_list is not None
            else [])

            for arg in call_args:
                arg_expr = arg.find(f'{{{SRC_NS}}}expr')
                arg_expr_name = (arg_expr.find(f'{{{SRC_NS}}}name')
                if arg_expr is not None
                else None)

                arg_expr_name_txt = (arg_expr_name.text
                if arg_expr_name is not None and arg_expr_name.text is not None
                else '')

                if arg_expr_name_txt != '':
                    call_data[call_name_txt]['cumulative_args'] = [
                        *call_data[call_name_txt]['cumulative_args'],
                        arg_expr_name_txt]

    for key in list(call_data):
        call_data[key]['cumulative_args'] = list(
            set(call_data[key]['cumulative_args']))

    if call_data != {}:
        return call_data

    return None

def _parse_declaration(
    element,
    parent_struct_name = '',
    parent_struct_type = '',
    belongs_to_file = ''):
    if element.tag in {
        f'{{{SRC_NS}}}decl_stmt',
        f'{{{SRC_NS}}}control',
        f'{{{SRC_NS}}}struct'
    }:
        decls = []

        if element.tag == f'{{{SRC_NS}}}control':
            control_init = element.find(f'{{{SRC_NS}}}init')
            control_init_decls = control_init.findall(f'{{{SRC_NS}}}decl')
            decls = [*decls, *control_init_decls]

        if element.tag == f'{{{SRC_NS}}}struct':
            struct_decls = element.findall(f'{{{SRC_NS}}}decl')

            decls = [*decls, *struct_decls]

        decls = [*decls, *element.findall(f'{{{SRC_NS}}}decl')]

        for decl in decls:
            decl_type = (decl.find(f'{{{SRC_NS}}}type')
            if decl is not None else None)

            decl_names = (decl.findall(f'{{{SRC_NS}}}name')
            if decl is not None else None)

            type_specifier = (decl_type.find(f'{{{SRC_NS}}}specifier')
            if decl_type is not None
            else None)

            type_specifier_txt = (type_specifier.text
            if type_specifier is not None and
            type_specifier.text is not None
            else '')

            type_name = (decl_type.find(f'{{{SRC_NS}}}name')
            if decl_type is not None else None)

            type_name_txt = (type_name.text
            if type_name is not None and type_name.text is not None
            else '')

            index_tag = None
            index_str = ''

            if type_name_txt == '' and type_name is not None:
                i_type_name = type_name.find(f'{{{SRC_NS}}}name')

                type_name_txt = (i_type_name.text
                if i_type_name is not None and
                i_type_name.text is not None
                else '')

                type_name_index = type_name.find(f'{{{SRC_NS}}}index')
                index_tag = type_name_index

                if type_name_index is not None:
                    index_str = ''.join(
                        i_str for i_str in type_name_index.itertext())

            type_modifier = (decl_type.find(f'{{{SRC_NS}}}modifier')
            if decl_type is not None
            else None)

            type_modifier_txt = (type_modifier.text
            if type_modifier is not None and type_modifier.text is not None
            else '')

            decl_pos = tuple(_get_span(decl)[0])
            decl_pos_row = int(decl_pos[0])

            if type_name != '':
                for name in decl_names:
                    child_name = _get_name_from_nested_name(name)
                    child_name_txt = (child_name.text
                    if child_name is not None and child_name.text is not None
                    else '')

                    if child_name_txt != '':
                        return {
                            'specifier': type_specifier_txt,
                            'type': type_name_txt,
                            'modifier': type_modifier_txt,
                            'name': child_name_txt,
                            'index_tag': index_tag,
                            'index_str': index_str,
                            'signature': re.sub('/s+', ' ', ' '.join(
                                [
                                    type_specifier_txt,
                                    type_name_txt,
                                    type_modifier_txt,
                                    child_name_txt]).rstrip()),
                            'pos_row': decl_pos_row,
                            'file_name': belongs_to_file,
                            'parent_structure_name': parent_struct_name,
                            'parent_structure_type': parent_struct_type,
                        }


    return None

class FunctionCollector:
    def __init__(self, language):
        self.language = language
        (self.RESERVED_FUNCTIONS,
        self.RESERVED_STREAMS,
        self.RESERVED_KEYWORDS) = _get_constants_from_language(language)


class SrcMLParser:
    def __init__(self, language):
        self._language = language
        (self.RESERVED_FUNCTIONS,
        self.RESERVED_STREAMS,
        self.RESERVED_KEYWORDS) = _get_constants_from_language(language)

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

        lines = NEWLINE_RE.split(contents)
        nlines = len(lines[:-1] if lines[-1] == '' else lines)
        srcml = _get_srcml(contents, self._language)
        if srcml is None:
            logger.error('SrcML failed to parse %s', name)
        else:
            functions = list()
            srcml = ElementTree.fromstring(srcml)
            functions.extend(_get_declarations(srcml))
            functions.extend(_get_definitions(srcml, nlines))

        return functions

    def _parse_el_for_global_variable_write(
        self,
        element,
        function_declaration_list,
        pointer_declarations,
        variable_writes):
        decl_names = [d['name'] for d in [
            *function_declaration_list,
            *pointer_declarations]]

        expr_str = ''

        fan_out_var_candidates = []

        expr_children = [child for child in element.iter()]
        expr_str = ''.join([child for child in element.itertext()])

        expr_names = element.findall(f'{{{SRC_NS}}}name')
        operators = element.findall(f'{{{SRC_NS}}}operator')

        incr_decr_op = next(
            (op for op in operators
            if op is not None and
            op.text is not None and
            op.text in {'++', '--'}),
            None)

        incr_decr_op_txt = (incr_decr_op.text
        if incr_decr_op is not None and incr_decr_op.text is not None
        else '')

        incr_decr_op_pos = (-1, -1)

        if incr_decr_op is not None:
            incr_decr_op_pos = tuple(_get_span(incr_decr_op)[0])

        incr_decr_op_row = int(incr_decr_op_pos[0])
        incr_decr_op_col = int(incr_decr_op_pos[1])

        equals_ops = [op for op in operators
        if op is not None
        and op.text is not None
        and op.text in {
            '=',
            '+=',
            '-=',
            '*=',
            '\\='
        }]

        last_equals_op_txt = ''
        last_equals_op_pos = first_equals_op_pos = (-1, -1)
        if len(equals_ops) > 0:
            last_equals_op_txt = (equals_ops[-1].text
            if equals_ops[-1].text is not None else '')

            last_equals_op_pos = tuple(_get_span(equals_ops[-1])[0])
            first_equals_op_pos = tuple(_get_span(equals_ops[0])[0])

        last_equals_op_row = int(last_equals_op_pos[0])
        last_equals_op_col = int(last_equals_op_pos[1])

        first_equals_op_col = int(first_equals_op_pos[1])

        if last_equals_op_txt != '' or incr_decr_op_txt != '':
            if len(expr_names) > 0:
                first_expr_name = expr_names[0]
                first_expr_name_txt = ''

                for name in expr_names:
                    name_pos = tuple(_get_span(name)[0])
                    name_pos_row = int(name_pos[0])
                    name_pos_col = int(name_pos[1])

                    expr_sub_names = name.findall(f'{{{SRC_NS}}}name')

                    expr_sub_name = (_get_name_from_nested_name(
                        expr_sub_names[0])
                    if len(expr_sub_names) > 1
                    else name)

                    expr_sub_name_pos = (-1, -1)

                    if expr_sub_name is not None:
                        expr_sub_name_pos = tuple(_get_span(expr_sub_name)[0])

                    expr_sub_name_pos_row = int(expr_sub_name_pos[0])
                    expr_sub_name_pos_col = int(expr_sub_name_pos[1])

                    expr_index = name.find(f'{{{SRC_NS}}}index')
                    expr_index_pos = (-1 ,-1)

                    if expr_index is not None:
                        expr_index_pos = tuple(_get_span(expr_index)[0])

                    expr_index_pos_row = int(expr_index_pos[0])
                    expr_index_pos_col = int(expr_index_pos[1])

                    first_expr_name_txt = (expr_sub_name.text
                    if expr_sub_name is not None
                    and expr_sub_name.text is not None
                    else ''.join(child_txt
                    for child_txt in first_expr_name.itertext()))

                    name_signature = ''.join(child_txt
                    for child_txt in name.itertext())

                    name_op = name.findall(f'{{{SRC_NS}}}operator')

                    access_op = next(
                        (op for op in name_op
                        if op is not None and op.text is not None
                        and (op.text == '->' or op.text == '.')), None)

                    access_op_pos = (-1, -1)

                    if access_op is not None:
                        access_op_pos = tuple(
                            _get_span(access_op)[0])

                    access_op_pos_row = int(access_op_pos[0])
                    access_op_pos_col = int(access_op_pos[1])

                    members_accessed = []
                    expr_mod_statements = []
                    indices = []

                    index_accessed_str = ''

                    if (access_op is not None
                        and access_op_pos_row == expr_sub_name_pos_row
                        and access_op_pos_col > expr_sub_name_pos_col
                        and (
                            access_op_pos_col < first_equals_op_col or
                            incr_decr_op_col != -1)
                        ):

                        member_accessed_str = ''

                        for child in expr_children:
                            child_pos = (-1, -1)

                            if child_pos is not None:
                                child_pos = tuple(_get_span(child)[0])

                            child_pos_row = int(child_pos[0])
                            child_pos_col = int(child_pos[1])

                            child_txt = (''.join(child.itertext())
                            if child.text is None else child.text)

                            if (
                                child_pos_row == access_op_pos_row and
                                child_pos_col > access_op_pos_col and
                                (
                                    child_pos_col < first_equals_op_col or
                                    incr_decr_op_col != -1)):

                                if (child_txt != '' and
                                expr_index_pos_col > access_op_pos_col and
                                expr_index_pos_row == access_op_pos_row):
                                    index_accessed_str += child_txt
                                else:
                                    member_accessed_str += child_txt
                            elif (
                                child_pos_col < first_equals_op_col and
                                expr_index_pos_col < first_equals_op_col and
                                expr_index_pos_col != -1 and
                                child_txt != '' and
                                expr_index_pos_row == access_op_pos_row):
                                index_accessed_str += child_txt

                        if index_accessed_str != '':
                            indices.append(index_accessed_str)

                        if member_accessed_str != '':
                            members_accessed.append(member_accessed_str)

                    elif access_op is None and expr_index is None:
                        expr_mod_statements.append(expr_str)

                    if (first_expr_name_txt != 'this' and
                    first_expr_name_txt not in decl_names):
                        fan_out_var_candidates.append({
                        'name': first_expr_name_txt,
                        'signature': name_signature,
                        'row_pos': name_pos_row,
                        'col_pos': name_pos_col,
                        'members_accessed': members_accessed,
                        'indices' : indices,
                        'expr_mod_statements': expr_mod_statements
                        })

            for cand in fan_out_var_candidates:
                if ((
                        last_equals_op_txt != '' and
                        last_equals_op_col > cand['col_pos'] and
                        last_equals_op_row == cand['row_pos']
                    ) or (
                        incr_decr_op_txt and
                        incr_decr_op_row == cand['row_pos']
                    )):
                    if cand['name'] not in variable_writes.keys():
                        variable_writes[cand['name']] = GlobalVariableWrite(
                            expressions = cand['expr_mod_statements'],
                            members_modified = cand['members_accessed'],
                            indices_modified = cand['indices']
                        )
                    else:
                        object.__setattr__(
                            variable_writes[cand['name']],
                            'expressions',
                            [
                            *variable_writes[cand['name']].expressions,
                            *cand['expr_mod_statements']
                            ])

                        object.__setattr__(
                            variable_writes[cand['name']],
                            'members_modified',
                            [
                            *variable_writes[cand['name']].members_modified,
                            *cand['members_accessed']
                            ])

                        object.__setattr__(
                            variable_writes[cand['name']],
                            'indices_modified',
                            [
                            *variable_writes[cand['name']].indices_modified,
                            *cand['indices']
                            ])

    def _parse_el_for_global_variable_read(
        self,
        expr,
        calls,
        function_declarations,
        params,
        local_function_names,
        enums,
        read_variable_names,
        throws_exception_names,
        parent_declarations):
        declaration_names = [d['name'] for d in function_declarations]

        parent_declaration_var_names= [d['name']
        for d in parent_declarations if d is not None]

        param_names = [p['name'] for p in params]

        call_arg_names = []

        for key in calls.keys():
            call_arg_names = [*call_arg_names, *calls[key]['cumulative_args']]

        expr_names = expr.findall(f'{{{SRC_NS}}}name')

        ops = (expr.findall(f'{{{SRC_NS}}}operator')
        if expr is not None else None)

        last_op = next(
            (op for op in list(reversed(ops))
            if op is not None and
            op.text is not None and
            op.text in {'=','+=','-=','*=','\\='}), None)

        incr_decr_op = next((
            op for op in ops if op is not None and
            op.text is not None and
            op.text in {'++', '--'}), None)

        incr_decr_op_pos = (-1, -1)
        if incr_decr_op is not None:
            incr_decr_op_pos = tuple(_get_span(incr_decr_op)[0])

        incr_decr_op_col = int(incr_decr_op_pos[1])

        equal_op_pos = (-1, -1)

        if last_op is not None:
            equal_op_pos = tuple(_get_span(last_op)[0])

        equal_op_pos_col = int(equal_op_pos[1])

        for arg in call_arg_names:
            if(
                not isinstance(arg, (int, float, bytes)) and
                arg != '' and
                arg is not None and
                arg not in self.RESERVED_KEYWORDS and
                arg not in self.RESERVED_STREAMS and
                not re.match(r'^null$', arg, flags=re.IGNORECASE) and
                arg not in declaration_names and
                arg not in param_names and
            (
                (
                    arg not in list(calls) and
                    arg not in self.RESERVED_FUNCTIONS and
                    arg not in local_function_names and
                    arg not in enums and
                    arg not in throws_exception_names
                )
            or
                arg in parent_declaration_var_names
            or
                arg in param_names
            )
            ):
                read_variable_names.append(arg)

        for name in expr_names:
            name_txt = _get_full_name_text_from_name(name)
            name_pos = (-1, -1)

            if name is not None:
                name_pos = tuple(_get_span(name)[0])

            name_pos_col = int(name_pos[1])

            name_accessed_txt = re.split(r'\-\>|\[|\.', name_txt, 1)[0]

            if(
                name_pos_col >= equal_op_pos_col and
                equal_op_pos_col <= incr_decr_op_col and
                name_accessed_txt != '' and
                name_accessed_txt is not None and
                name_accessed_txt not in self.RESERVED_KEYWORDS and
                name_accessed_txt not in self.RESERVED_STREAMS and
                not re.match(
                    r'^null$',
                    name_accessed_txt,
                    flags=re.IGNORECASE) and
                name_accessed_txt not in declaration_names and
                (
                    (
                        name_accessed_txt not in list(calls) and
                        name_accessed_txt not in self.RESERVED_FUNCTIONS and
                        name_accessed_txt not in local_function_names and
                        name_accessed_txt not in enums and
                        name_accessed_txt not in throws_exception_names
                    )
                or
                    name_accessed_txt in parent_declaration_var_names
                or
                    name_accessed_txt in param_names
                )
            ):
                read_variable_names.append(name_txt)

        read_variable_names = list(set([*read_variable_names]))

    def _compile_acyclical_paths_tree(self, root):
        root_paths = []

        root_block = root.find(f'{{{SRC_NS}}}block')
        root_block_content = (
            root_block.find(f'{{{SRC_NS}}}block_content')
            if root_block is not None
            else root_block if root_block is not None
            else root)

        for child in list(root_block_content):
            if child.tag == f'{{{SRC_NS}}}if_stmt':
                root_paths = [
                    *root_paths,
                    *self._compile_acyclical_paths_tree(child)]

            elif child.tag in {
                f'{{{SRC_NS}}}if',
                f'{{{SRC_NS}}}else'
            }:
                if_type = (child.attrib['type']
                if 'type' in child.attrib.keys() else '')

                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    if_type = if_type,
                    children = self._compile_acyclical_paths_tree(child)))
            elif child.tag in {
                f'{{{SRC_NS}}}for',
                f'{{{SRC_NS}}}while',
                f'{{{SRC_NS}}}do'
            }:
                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    if_type = None,
                    children = self._compile_acyclical_paths_tree(child)))
            elif child.tag == f'{{{SRC_NS}}}switch':
                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    children = self._compile_acyclical_paths_tree(child)))
            elif child.tag in {
                f'{{{SRC_NS}}}case',
                f'{{{SRC_NS}}}default'
            }:
                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    children = self._compile_acyclical_paths_tree(child)))
            elif child.tag == f'{{{SRC_NS}}}ternary':
                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    children = self._compile_acyclical_paths_tree(child)))
            elif child.tag == f'{{{SRC_NS}}}then':
                root_paths.append(AcyclicalPath(
                    type = child.tag,
                    children = []))

        return root_paths

    def get_function_properties(
        self,
        function_element,
        function_dict,
        all_local_call_names,
        parent_struct_name,
        parent_struct_type,
        parent_declarations,
        file_name,
        enums,
        local_function_names
        ):

        if function_element.tag in {
            f'{{{SRC_NS}}}function',
            f'{{{SRC_NS}}}constructor'
        }:
            func_sig =_get_signature(function_element)
            func_name = _get_name(function_element)
            func_span = _get_span(function_element)
            block = function_element.find(f'{{{SRC_NS}}}block')

            has_return_value = False

            acyc_paths = self._compile_acyclical_paths_tree(function_element)

            throws_exception_names = []
            declarations = []
            pointer_decls = []

            calls = {}

            global_variable_writes = {}
            global_variable_reads = []

            if block is not None:
                param_data = _get_param_data(function_element)

                for func_child in function_element.iter():
                    decl = _parse_declaration(
                        func_child,
                        parent_struct_name=parent_struct_name,
                        parent_struct_type=parent_struct_type,
                        belongs_to_file=file_name)

                    call = _parse_function_call(func_child)
                    throws = _get_throws_expression_names(func_child)

                    if throws != []:
                        throws_exception_names = [
                            *throws_exception_names,
                            *throws]

                    if decl is not None:
                        if decl['modifier'] == '*':
                            pointer_decls.append(decl)
                        else:
                            declarations.append(decl)

                    if call is not None:
                        calls = {**calls, **call}
                        all_local_call_names = [
                            *all_local_call_names,
                            *call.keys()]

                    if f'{{{SRC_NS}}}return' and has_return_value is False:
                        return_expr = func_child.find(f'{{{SRC_NS}}}expr')
                        if return_expr is not None:
                            has_return_value = True

                    if func_child.tag in {
                        f'{{{SRC_NS}}}expr',
                        f'{{{SRC_NS}}}decl_stmt',
                    }:
                        self._parse_el_for_global_variable_write(
                            element = func_child,
                            function_declaration_list = declarations,
                            pointer_declarations = pointer_decls,
                            variable_writes = global_variable_writes,
                        )

                        self._parse_el_for_global_variable_read(
                            expr = func_child,
                            calls = calls,
                            function_declarations = declarations,
                            params = param_data['parameters'],
                            local_function_names = local_function_names,
                            enums = enums,
                            read_variable_names = global_variable_reads,
                            throws_exception_names = throws_exception_names,
                            parent_declarations = parent_declarations
                            )

                global_variable_reads = list(set(global_variable_reads))

                if func_sig not in function_dict.keys():
                    local_function_names.append(func_name)
                    function_dict[func_sig] = FunctionProperties(
                        signature = func_sig,
                        span = func_span,
                        function_name = func_name,
                        calls = calls,
                        callers = [],
                        acyclical_paths_tree = acyc_paths,
                        has_return = has_return_value,
                        parent_structure_name = parent_struct_name,
                        parent_structure_type = parent_struct_type,
                        global_variable_writes = global_variable_writes,
                        global_variable_reads = list(
                            set(global_variable_reads))
                    )

        return function_dict

    def get_functions_with_metric_properties(
        self,
        root_element,
        parent_struct_name,
        parent_struct_type,
        parent_declarations,
        file_name,
        enums,
        all_local_call_names
        ):
        parent_name_txt = parent_struct_name
        local_declarations = parent_declarations

        function_dict = {}

        class_els = root_element.findall(rf'{{{SRC_NS}}}class')
        struct_els = root_element.findall(rf'{{{SRC_NS}}}struct')
        namespace_els = root_element.findall(rf'{{{SRC_NS}}}namespace')
        unit_els = root_element.findall(rf'{{{SRC_NS}}}unit')
        function_els = root_element.findall(rf'{{{SRC_NS}}}function')
        block_els = root_element.findall(rf'{{{SRC_NS}}}block')
        block_content_els = root_element.findall(rf'{{{SRC_NS}}}block_content')

        #Sorts by row position
        root_els = sorted([
            *class_els,
            *struct_els,
            *namespace_els,
            *unit_els,
            *function_els,
            *block_els,
            *block_content_els
        ], key = lambda el: tuple(_get_span(el)[0])[0])

        for child in root_els:
            if child.tag in {
                f'{{{SRC_NS}}}class',
                f'{{{SRC_NS}}}struct',
                f'{{{SRC_NS}}}namespace',
                f'{{{SRC_NS}}}unit'
            }:
                parent_name = child.find(f'{{{SRC_NS}}}name')
                new_parent_struct_type = re.sub(r'{.+}', '', child.tag)

                new_parent_name_txt = (
                    parent_struct_name +
                    _get_full_name_text_from_name(parent_name))

                class_declarations = [
                    _parse_declaration(
                        element = decl,
                        parent_struct_name = new_parent_name_txt,
                        parent_struct_type = new_parent_struct_type,
                        belongs_to_file = file_name)
                        for decl in child.findall(f'{{{SRC_NS}}}decl_stmt')]

                class_enums = [
                    _parse_enum(el)
                    for el in child.findall(f'{{{SRC_NS}}}enum')
                ]

                local_declarations = [
                    *parent_declarations,
                    *class_declarations]

                enums = [*enums, *class_enums]

                function_dict = {**function_dict,
                **self.get_functions_with_metric_properties(
                root_element = child,
                all_local_call_names = all_local_call_names,
                parent_struct_name = new_parent_name_txt,
                parent_struct_type = new_parent_struct_type,
                parent_declarations = local_declarations,
                file_name = file_name,
                enums = enums)}

            if child.tag in {
                f'{{{SRC_NS}}}block',
                f'{{{SRC_NS}}}block_content'
            }:
                function_dict = {**function_dict,
                **self.get_functions_with_metric_properties(
                root_element = child,
                all_local_call_names = all_local_call_names,
                parent_struct_name = parent_name_txt,
                parent_struct_type = parent_struct_type,
                parent_declarations = local_declarations,
                file_name = file_name,
                enums = enums)}

            if child.tag in {
                f'{{{SRC_NS}}}function',
                f'{{{SRC_NS}}}constructor'
            }:
                updated_function_dict = self.get_function_properties(
                    function_element = child,
                    function_dict = function_dict,
                    all_local_call_names = all_local_call_names,
                    parent_struct_name = parent_name_txt,
                    parent_struct_type = parent_struct_type,
                    parent_declarations = parent_declarations,
                    file_name = file_name,
                    local_function_names=[
                        f.function_name
                        for f in function_dict.values()],
                    enums = enums)

                function_dict = {**function_dict, **updated_function_dict}

        return function_dict

    def get_functions_with_properties(self, file_name, contents):
        srcml = _get_srcml(contents, self._language)

        if srcml is None:
            return None

        root = ElementTree.fromstring(srcml)

        root_declarations = [
            _parse_declaration(
                element = decl,
                parent_struct_name=file_name,
                parent_struct_type='file',
                belongs_to_file='file_name')
            for decl in root.findall(f'{{{SRC_NS}}}decl_stmt')]

        root_enums = [
            _parse_enum(el)
            for el in root.findall(f'{{{SRC_NS}}}enum')
        ]

        func_dict = self.get_functions_with_metric_properties(
            root_element = root,
            parent_struct_name = file_name,
            parent_struct_type= 'file',
            parent_declarations=root_declarations,
            all_local_call_names=[],
            enums = root_enums,
            file_name = file_name
            )

        return func_dict

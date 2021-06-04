import logging
import re
import subprocess

from xml.etree import ElementTree

from ..enumerations import CommentType
from ..models import Comment, Function, Position, Span
from ..constants import C_LIB_FUNCTIONS, C_LIB_STREAMS, C_RESERVED_KEYWORDS

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

    if re.search(rf"{{{SRC_NS}}}enum", element.tag):

        enum_block = element.find(rf"{{{SRC_NS}}}block")
        enum_decls = enum_block.findall(rf"{{{SRC_NS}}}decl") if enum_block is not None else []

        for decl in enum_decls:

            decl_name = _get_name_from_nested_name(
                decl.find(rf"{{{SRC_NS}}}name")
                )

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
        print(error)

    return None

def _get_name_from_nested_name(name):
    if name is not None and name.text is not None:
        return name
    else:
        next_elname = name.find(rf"{{{SRC_NS}}}name")
        if next_elname is None:
            return next_elname

        return _get_name_from_nested_name(next_elname)

def _get_full_name_text_from_name(name):
    name_txt = ''

    if name is not None:
        if name.text is not None:
            name_txt = name.text
        else:
            for n_txt in name.itertext():
                name_txt += n_txt

    return name_txt

def _get_throws_expression_names(statement):
    exception_names = []

    if re.search(rf"{{{SRC_NS}}}throws", statement.tag):
        args = statement.findall(rf"{{{SRC_NS}}}argument")
        for arg in args:
            expr = arg.find(rf"{{{SRC_NS}}}expr")
            expr_name = expr.find(rf"{{{SRC_NS}}}name") if expr is not None else None

            name_txt = _get_full_name_text_from_name(expr_name)

            if name_txt != '':
                exception_names.append(name_txt)

    return exception_names

def _get_param_data(function):
    parameter_list = function.find(rf"{{{SRC_NS}}}parameter_list")
    parameters = parameter_list.findall(rf"{{{SRC_NS}}}parameter")

    parameter_declarations = []
    parameters_passed_by_reference = []

    for param in parameters:
        decl = param.find(rf"{{{SRC_NS}}}decl")
        decl_name = decl.find(rf"{{{SRC_NS}}}name") if decl is not None else None
        decl_name_txt = decl_name.text if decl_name is not None and decl_name.text else ""

        decl_type = decl.find(rf"{{{SRC_NS}}}type") if decl is not None else None
        decl_type_name = decl_type.find(rf"{{{SRC_NS}}}name") if decl_type is not None else None
        decl_type_name_txt = (
            decl_type_name.text
            if decl_type_name is not None and decl_type_name.text
            else "")

        decl_type_modifier = (decl_type.find(rf"{{{SRC_NS}}}modifier")
        if decl_type is not None
        else None)

        decl_type_modifier_txt = (decl_type_modifier.text
        if decl_type_modifier is not None and decl_type_modifier.text
        else "")

        if re.search(r"\*|\&", decl_type_modifier_txt):
            parameters_passed_by_reference.append(
                {
                    "type": decl_type_name_txt,
                    "modifier": decl_type_modifier_txt,
                    "name": decl_name_txt})

        if decl_name_txt != "":
            parameter_declarations.append(
                {
                    "type": decl_type_name_txt,
                    "modifier": decl_type_modifier_txt,
                    "name": decl_name_txt})

    return {
        "parameters" : parameter_declarations,
        "parameters_passed_by_reference": parameters_passed_by_reference}

def _parse_function_call(element):
    call_data = {}

    if re.search(rf"{{{SRC_NS}}}call", str(element)):
        call_name = element.find(rf"{{{SRC_NS}}}name")
        call_name_txt = _get_full_name_text_from_name(call_name)


        if call_name_txt not in list(call_data) and call_name_txt != "":
            call_data[call_name_txt] ={
                "cumulative_args": []
            }

        if call_name_txt != "":
            call_arg_list = element.find(rf"{{{SRC_NS}}}argument_list")

            call_args = (call_arg_list.findall(rf"{{{SRC_NS}}}argument")
            if call_arg_list is not None
            else [])

            for arg in call_args:
                arg_expr = arg.find(rf"{{{SRC_NS}}}expr")
                arg_expr_name = (arg_expr.find(rf"{{{SRC_NS}}}name")
                if arg_expr is not None
                else None)

                arg_expr_name_txt = (arg_expr_name.text
                if arg_expr_name is not None and arg_expr_name.text is not None
                else "")

                if arg_expr_name_txt != "":
                    call_data[call_name_txt]["cumulative_args"] = [
                        *call_data[call_name_txt]["cumulative_args"],
                        arg_expr_name_txt]

    for key in list(call_data):
        call_data[key]["cumulative_args"] = list(set(call_data[key]["cumulative_args"]))

    if call_data != {}:
        return call_data

    return None

def _parse_macro_call(element, language):
    macro_calls = {}
    if re.search(rf"{{{SRC_NS}}}macro", element.tag):
        macro_arg_list = element.find(rf"{{{SRC_NS}}}argument_list")
        macro_args = (macro_arg_list.findall(rf"{{{SRC_NS}}}argument")
        if macro_arg_list is not None
        else None)

        if macro_args is not None:
            for arg in macro_args:
                arg_text = arg.text if arg is not None and arg.text is not None else ""

                if arg_text != "":
                    srcml = _get_srcml(arg_text, language)
                    rootet = ElementTree.fromstring(srcml)

                    if re.search(r"{(.)+}", arg_text, flags=re.MULTILINE|re.DOTALL):
                        for child in rootet.iter():
                            call = _parse_function_call(child)

                            if call is not None:
                                macro_calls = {**macro_calls, **call}

    if macro_calls != {}:
        return macro_calls

    return None

def _parse_declaration(
    element,
    parent_struct_name = '',
    parent_struct_type = '',
    belongs_to_file = ''):
    if re.search(rf"{{{SRC_NS}}}decl_stmt|control|struct", element.tag):
        decls = []

        if re.search(rf"{{{SRC_NS}}}control", element.tag):
            control_init = element.find(rf"{{{SRC_NS}}}init")
            control_init_decls = control_init.findall(rf"{{{SRC_NS}}}decl")
            decls = [*decls, *control_init_decls]

        if re.search(rf"{{{SRC_NS}}}struct", element.tag):
            struct_decls = element.findall(rf"{{{SRC_NS}}}decl")

            decls = [*decls, *struct_decls]

        decls = [*decls, *element.findall(rf"{{{SRC_NS}}}decl")]

        for decl in decls:
            decl_type = decl.find(rf"{{{SRC_NS}}}type") if decl is not None else None

            decl_names = decl.findall(rf"{{{SRC_NS}}}name") if decl is not None else None

            type_specifier = (decl_type.find(rf"{{{SRC_NS}}}specifier")
            if decl_type is not None
            else None)

            type_specifier_txt = (type_specifier.text
            if type_specifier is not None and type_specifier.text is not None
            else "")

            type_name = decl_type.find(rf"{{{SRC_NS}}}name") if decl_type is not None else None
            type_name_txt = (type_name.text
            if type_name is not None and type_name.text is not None
            else "")

            index_tag = None
            index_str = ""

            if type_name_txt == "" and type_name is not None:
                i_type_name = type_name.find(rf"{{{SRC_NS}}}name")

                type_name_txt = (i_type_name.text
                if i_type_name is not None and i_type_name.text is not None
                else "")

                type_name_index = type_name.find(rf"{{{SRC_NS}}}index")
                index_tag = type_name_index

                if type_name_index is not None:
                    for i_str in type_name_index.itertext():
                        index_str += i_str

            type_modifier = (decl_type.find(rf"{{{SRC_NS}}}modifier")
            if decl_type is not None
            else None)

            type_modifier_txt = (type_modifier.text
            if type_modifier is not None and type_modifier.text is not None
            else "")

            decl_pos = (decl.attrib[rf"{{{POS_NS}}}start"].split(':')
            if rf"{{{POS_NS}}}start" in decl.attrib.keys()
            else [-1, -1])

            decl_pos_row = int(decl_pos[0])


            if type_name != "":
                for name in decl_names:
                    child_name = _get_name_from_nested_name(name)
                    child_name_txt = (child_name.text
                    if child_name is not None and child_name.text is not None
                    else '')

                    if child_name_txt != '':
                        return {
                            "specifier": type_specifier_txt,
                            "type": type_name_txt,
                            "modifier": type_modifier_txt,
                            "name": child_name_txt,
                            "index_tag": index_tag,
                            "index_str": index_str,
                            "signature": re.sub("/s+", " ", " ".join(
                                [
                                    type_specifier_txt,
                                    type_name_txt,
                                    type_modifier_txt,
                                    child_name_txt]).rstrip()),
                            "pos_row": decl_pos_row,
                            "file_name": belongs_to_file,
                            "parent_structure_name": parent_struct_name,
                            "parent_structure_type": parent_struct_type,
                        }


    return None

def _parse_el_for_global_variable_write(
    element,
    function_declaration_list,
    parameters_passed_by_reference,
    pointer_declarations,
    calls,
    variable_writes,
    parent_declarations):

    decl_names = [d["name"] for d in [*function_declaration_list, *pointer_declarations]]

    expr_str = ""

    fan_out_var_candidates = []

    expr_children = [child for child in element.iter()]
    expr_str = ''.join([child for child in element.itertext()])

    expr_names = element.findall(rf"{{{SRC_NS}}}name")
    operators = element.findall(rf"{{{SRC_NS}}}operator")

    incr_decr_op = next(
        (op for op in operators
        if op is not None and op.text is not None and re.fullmatch(r"^\+\+|\-\-$", op.text)),
        None)

    incr_decr_op_txt = (incr_decr_op.text
    if incr_decr_op is not None and incr_decr_op.text is not None
    else '')

    incr_decr_op_pos = (incr_decr_op.attrib[rf"{{{POS_NS}}}start"].split(':')
    if incr_decr_op is not None and rf"{{{POS_NS}}}start" in incr_decr_op.attrib.keys()
    else [-1, -1])

    incr_decr_op_row = int(incr_decr_op_pos[0])
    incr_decr_op_col = int(incr_decr_op_pos[1])

    equals_ops = [op for op in operators
    if op is not None
    and op.text is not None
    and re.fullmatch(r"^\=|\+\=|\-\=|\*\=|\\\=$", op.text)]

    if len(equals_ops) == 0:
        equals_ops = [None]

    last_equals_op_txt = (equals_ops[-1].text
    if equals_ops[-1] is not None and equals_ops[-1].text is not None
    else '')

    last_equals_op_pos = (equals_ops[-1].attrib[rf"{{{POS_NS}}}start"].split(':')
    if equals_ops[-1] is not None and rf"{{{POS_NS}}}start" in equals_ops[-1].attrib.keys()
    else [-1, -1])

    last_equals_op_row = int(last_equals_op_pos[0])
    last_equals_op_col = int(last_equals_op_pos[1])

    first_equals_op_pos = (equals_ops[0].attrib[rf"{{{POS_NS}}}start"].split(':')
    if equals_ops[0] is not None
    and rf"{{{POS_NS}}}start" in equals_ops[0].attrib.keys()
    else [-1, -1])

    first_equals_op_col = int(first_equals_op_pos[1])

    if last_equals_op_txt != '' or incr_decr_op_txt != '':
        if len(expr_names) > 0:
            first_expr_name = expr_names[0]
            first_expr_name_txt = ''

            for name in expr_names:
                name_pos = name.attrib[rf"{{{POS_NS}}}start"].split(':')
                name_pos_row = int(name_pos[0])
                name_pos_col = int(name_pos[1])

                expr_sub_names = name.findall(rf"{{{SRC_NS}}}name")

                expr_sub_name = (_get_name_from_nested_name(expr_sub_names[0])
                if len(expr_sub_names) > 1
                else name)

                expr_sub_name_pos =( expr_sub_name.attrib[rf"{{{POS_NS}}}start"].split(':')
                if expr_sub_name is not None
                and rf"{{{POS_NS}}}start" in expr_sub_name.attrib.keys()
                else [-1, -1])

                expr_sub_name_pos_row = int(expr_sub_name_pos[0])
                expr_sub_name_pos_col = int(expr_sub_name_pos[1])

                expr_index = name.find(rf"{{{SRC_NS}}}index")

                expr_index_pos = (expr_index.attrib[rf"{{{POS_NS}}}start"].split(':')
                if expr_index is not None and rf"{{{POS_NS}}}start" in expr_index.keys()
                else [-1, -1])

                expr_index_pos_row = int(expr_index_pos[0])
                expr_index_pos_col = int(expr_index_pos[1])

                first_expr_name_txt = (expr_sub_name.text
                if expr_sub_name is not None
                and expr_sub_name.text is not None
                else ''.join([child_txt for child_txt in first_expr_name.itertext()]))

                name_signature = ''.join([child_txt for child_txt in name.itertext()])

                name_op = name.findall(rf"{{{SRC_NS}}}operator")

                member_access_op = next(
                    (op for op in name_op
                    if op is not None and op.text is not None
                    and (op.text == '->' or op.text == '.')), None)

                member_access_op_pos = (member_access_op.attrib[rf"{{{POS_NS}}}start"].split(':')
                if member_access_op is not None
                and rf"{{{POS_NS}}}start" in member_access_op.attrib.keys()
                else [-1, -1])

                member_access_op_pos_row = int(member_access_op_pos[0])
                member_access_op_pos_col = int(member_access_op_pos[1])

                members_accessed = []
                expr_mod_statements = []
                indices = []

                index_accessed_str = ''

                if (member_access_op is not None
                    and member_access_op_pos_row == expr_sub_name_pos_row
                    and member_access_op_pos_col > expr_sub_name_pos_col
                    and (member_access_op_pos_col < first_equals_op_col or incr_decr_op_col != -1)
                    ):

                    member_accessed_str = ''

                    for child in expr_children:
                        child_pos = (child.attrib[rf"{{{POS_NS}}}start"].split(':')
                        if rf"{{{POS_NS}}}start" in child.attrib.keys()
                        else [-1, -1])

                        child_pos_row = int(child_pos[0])
                        child_pos_col = int(child_pos[1])

                        child_txt = ''.join(child.itertext()) if child.text is None else child.text

                        if (
                            child_pos_row == member_access_op_pos_row and
                            child_pos_col > member_access_op_pos_col and
                            (child_pos_col < first_equals_op_col or incr_decr_op_col != -1)):

                            if child_txt != '':
                                if (
                                    expr_index_pos_col > member_access_op_pos_col and
                                    expr_index_pos_row == member_access_op_pos_row):
                                    index_accessed_str += child_txt
                                else:
                                    member_accessed_str += child_txt
                        elif (
                            child_pos_col < first_equals_op_col and
                            expr_index_pos_col < first_equals_op_col and
                            expr_index_pos_col != -1):
                            if child_txt != '':
                                if expr_index_pos_row == member_access_op_pos_row:
                                    index_accessed_str += child_txt

                    if index_accessed_str != '':
                        indices.append(index_accessed_str)

                    if member_accessed_str != '':
                        members_accessed.append(member_accessed_str)

                elif member_access_op is None and expr_index is None:
                    expr_mod_statements.append(expr_str)

                if first_expr_name_txt != "this" and first_expr_name_txt not in decl_names:
                    fan_out_var_candidates.append({
                    "name": first_expr_name_txt,
                    "signature": name_signature,
                    "row_pos": name_pos_row,
                    "col_pos": name_pos_col,
                    "members_accessed": members_accessed,
                    "indices" : indices,
                    "expr_mod_statements": expr_mod_statements
                    })

        for cand in fan_out_var_candidates:
            if (
                last_equals_op_txt != '' and
                last_equals_op_col > cand["col_pos"] and
                last_equals_op_row == cand["row_pos"]):
                if cand["name"] not in variable_writes.keys():
                    variable_writes[cand["name"]] = {
                        'expressions': cand["expr_mod_statements"],
                        'members_modified': cand["members_accessed"],
                        'indices_modified': cand["indices"]
                    }
                else:
                    variable_writes[cand["name"]]['expressions'] = [
                        *variable_writes[cand["name"]]['expressions'],
                        *cand["expr_mod_statements"]]

                    variable_writes[cand["name"]]['members_modified'] = [
                        *variable_writes[cand["name"]]['members_modified'],
                        *cand["members_accessed"]]

                    variable_writes[cand["name"]]['indices_modified'] = [
                        *variable_writes[cand["name"]]['indices_modified'],
                        *cand["indices"]]

            elif incr_decr_op_txt and incr_decr_op_row == cand["row_pos"]:
                if cand["name"] not in variable_writes.keys():
                    variable_writes[cand["name"]] = {
                        'expressions': cand["expr_mod_statements"],
                        'members_modified': cand["members_accessed"],
                        'indices_modified': cand["indices"]
                    }
                else:
                    variable_writes[cand["name"]]['expressions'] = [
                        *variable_writes[cand["name"]]['expressions'],
                        *cand["expr_mod_statements"]]

                    variable_writes[cand["name"]]['members_modified'] = [
                        *variable_writes[cand["name"]]['members_modified'],
                        *cand["members_accessed"]]

                    variable_writes[cand["name"]]['indices_modified'] = [
                        *variable_writes[cand["name"]]['indices_modified'],
                        *cand["indices"]]

def _parse_el_for_global_variable_read(
    expr,
    calls,
    function_declarations,
    pointer_declarations,
    params,
    local_function_names,
    enums,
    read_variable_names,
    function_throws_exception_names,
    parent_declarations):
    declaration_names = [d["name"] for d in function_declarations]
    parent_declaration_var_names= [d["name"] for d in parent_declarations if d is not None]
    param_names = [p["name"] for p in params]

    call_arg_names = []

    for key in calls.keys():
        call_arg_names = [*call_arg_names, *calls[key]["cumulative_args"]]

    expr_names = expr.findall(rf"{{{SRC_NS}}}name")

    ops = expr.findall(rf"{{{SRC_NS}}}operator") if expr is not None else None

    last_op = next(
        (op for op in list(reversed(ops))
        if op is not None and
        op.text is not None and
        re.fullmatch(r"^\=|\+\=|\-\=|\*\=|\\\=$", op.text)), None)

    incr_decr_op = next((
        op for op in ops if op is not None and
        op.text is not None and
        re.fullmatch(r"^\+\+|\-\-$", op.text)), None)

    incr_decr_op_pos = (incr_decr_op.attrib[rf"{{{POS_NS}}}start"].split(':')
    if incr_decr_op is not None and
    rf"{{{POS_NS}}}start" in incr_decr_op.attrib.keys()
    else [-1, -1])

    incr_decr_op_col = int(incr_decr_op_pos[1])

    equal_op_pos = (
        last_op.attrib[rf'{{{POS_NS}}}start'].split(':')
        if last_op is not None and
        rf'{{{POS_NS}}}start' in last_op.attrib.keys()
        else [-1, -1])

    equal_op_pos_col = int(equal_op_pos[1])

    for arg in call_arg_names:
        if(
            not isinstance(arg, (int, float, bytes)) and
            arg != "" and
            arg is not None and
            arg not in C_RESERVED_KEYWORDS and
            arg not in C_LIB_STREAMS and
            not re.match(r"^null$", arg, flags=re.IGNORECASE) and
            arg not in declaration_names and
            arg not in param_names and
        (

            (
                arg not in list(calls) and
                arg not in C_LIB_FUNCTIONS and
                arg not in local_function_names and
                arg not in enums and
                arg not in function_throws_exception_names
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

        name_pos = (
            name.attrib[rf'{{{POS_NS}}}start'].split(':')
            if rf'{{{POS_NS}}}start' in name.attrib.keys()
            else [-1, -1])

        name_pos_col = int(name_pos[1])

        name_member_access_txt = re.split(r"\-\>|\[|\.", name_txt, 1)[0]

        if(
            name_pos_col >= equal_op_pos_col and
            equal_op_pos_col <= incr_decr_op_col and
            name_member_access_txt != "" and
            name_member_access_txt is not None and
            name_member_access_txt not in C_RESERVED_KEYWORDS and
            name_member_access_txt not in C_LIB_STREAMS and
            not re.match(r"^null$", name_member_access_txt, flags=re.IGNORECASE) and
            name_member_access_txt not in declaration_names and
            (
                (
                    name_member_access_txt not in list(calls) and
                    name_member_access_txt not in C_LIB_FUNCTIONS and
                    name_member_access_txt not in local_function_names and
                    name_member_access_txt not in enums and
                    name_member_access_txt not in function_throws_exception_names
                )
            or
                name_member_access_txt in parent_declaration_var_names
            or
                name_member_access_txt in param_names
            )
        ):
            read_variable_names.append(name_txt)

    read_variable_names = list(set([*read_variable_names]))

def _compile_acyclical_paths_tree(root):
    root_paths = []

    root_block = root.find(rf"{{{SRC_NS}}}block")
    root_block_content = (
        root_block.find(rf"{{{SRC_NS}}}block_content")
        if root_block is not None
        else root_block if root_block is not None
        else root)

    for child in list(root_block_content):
        if re.search(rf'{{{SRC_NS}}}if_stmt', child.tag):
            root_paths = [
                *root_paths,
                *_compile_acyclical_paths_tree(child)]

        elif re.search (rf'{{{SRC_NS}}}if|else', child.tag):
            if_type = child.attrib["type"] if "type" in child.attrib.keys() else ""

            root_paths.append({
                "type": child.tag,
                "if_type": if_type,
                "children": _compile_acyclical_paths_tree(child)
            })
        elif re.search(rf'{{{SRC_NS}}}for|while|do', child.tag):
            root_paths.append({
                "type": child.tag,
                "children": _compile_acyclical_paths_tree(child)
            })
        elif re.search(rf"{{{SRC_NS}}}switch", child.tag):
            root_paths.append({
                "type": child.tag,
                "children": _compile_acyclical_paths_tree(child)
            })
        elif re.search(rf'{{{SRC_NS}}}case|default', child.tag):
            root_paths.append({
                "type": child.tag,
                "children": _compile_acyclical_paths_tree(child)
            })
        elif re.search(rf"{{{SRC_NS}}}ternary", child.tag):
            root_paths.append({
                "type": child.tag,
                "children": _compile_acyclical_paths_tree(child)
            })
        elif re.search(rf"{{{SRC_NS}}}then", child.tag):
            root_paths.append({
                "type": child.tag,
                "children": []
            })

    return root_paths

def get_function_global_var_ops_and_paths(
    function_element,
    function_dict,
    all_local_call_names,
    parent_struct_name,
    parent_struct_type,
    parent_declarations,
    file_name,
    enums,
    local_function_names,
    language):

    if re.search(rf"{{{SRC_NS}}}function|constructor", function_element.tag):
        func_sig =_get_signature(function_element)
        func_name = _get_name(function_element)
        block = function_element.find(rf"{{{SRC_NS}}}block")

        has_return_value = False

        acyc_paths = _compile_acyclical_paths_tree(function_element)

        throws_exception_names = []
        declarations = []
        pointer_decls = []

        calls = {}
        macro_calls = {}

        global_variable_writes = {}
        global_variable_reads = []

        if block is not None:
            param_data = _get_param_data(function_element)
            param_count = len(param_data["parameters"])

            for func_child in function_element.iter():
                decl = _parse_declaration(
                    func_child,
                    parent_struct_name=parent_struct_name,
                    parent_struct_type=parent_struct_type,
                    belongs_to_file=file_name)

                call = _parse_function_call(func_child)
                macros = _parse_macro_call(func_child, language)
                throws = _get_throws_expression_names(func_child)

                if throws != []:
                    throws_exception_names = [*throws_exception_names, *throws]

                if decl is not None:
                    if decl["modifier"] == "*":
                        pointer_decls.append(decl)
                    else:
                        declarations.append(decl)

                if call is not None:
                    calls = {**calls, **call}
                    all_local_call_names = [*all_local_call_names, *call.keys()]

                if macros is not None:
                    macro_calls = {**macro_calls, **macros}

                if re.search(rf'{{{SRC_NS}}}return', func_child.tag) and has_return_value is False:
                    return_expr = func_child.find(rf"{{{SRC_NS}}}expr")
                    if return_expr is not None:
                        has_return_value = True

                if re.search(rf"{{{SRC_NS}}}expr|decl_stmt", func_child.tag):
                    _parse_el_for_global_variable_write(
                        element = func_child,
                        function_declaration_list = declarations,
                        parameters_passed_by_reference = param_data[
                            "parameters_passed_by_reference"],
                        pointer_declarations = pointer_decls,
                        calls = calls,
                        variable_writes = global_variable_writes,
                        parent_declarations = parent_declarations
                    )

                    _parse_el_for_global_variable_read(
                        expr = func_child,
                        calls = calls,
                        function_declarations = declarations,
                        pointer_declarations = pointer_decls,
                        params = param_data["parameters"],
                        local_function_names = local_function_names,
                        enums = enums,
                        read_variable_names = global_variable_reads,
                        function_throws_exception_names = throws_exception_names,
                        parent_declarations = parent_declarations
                        )

            global_variable_reads = list(set(global_variable_reads))

            if func_sig not in function_dict.keys():
                local_function_names.append(func_name)
                function_dict[func_sig] = {
                    "signature": func_sig,
                    "function_name": func_name,
                    "param_count": param_count,
                    "calls": calls,
                    "functions_called_by": [],
                    "acyclical_paths_tree": acyc_paths,
                    "has_return": has_return_value,
                    "parent_structure_name": parent_struct_name,
                    "parent_structure_type": parent_struct_type,
                    "file_name": file_name,
                    "global_variable_writes": global_variable_writes,
                    "global_variable_reads": list(set(global_variable_reads))
                }

    return function_dict

def get_functions_with_metric_properties(
    root_element,
    parent_struct_name,
    parent_struct_type,
    parent_declarations,
    file_name,
    local_function_names,
    enums,
    all_local_call_names,
    language
    ):
    parent_name_txt = parent_struct_name
    local_declarations = parent_declarations

    function_dict = {}
    for child in list(root_element):
        if re.search(rf"{{{SRC_NS}}}class|struct|namespace|unit", child.tag):
            parent_name = child.find(rf"{{{SRC_NS}}}name")
            new_parent_struct_type = re.sub(r"{.+}", "", child.tag)
            new_parent_name_txt = parent_struct_name + _get_full_name_text_from_name(parent_name)

            class_declarations = [
                _parse_declaration(
                    element = decl,
                    parent_struct_name = new_parent_name_txt,
                    parent_struct_type = new_parent_struct_type,
                    belongs_to_file = file_name)
                    for decl in child.findall(rf"{{{SRC_NS}}}decl_stmt")]

            class_enums = [
                _parse_enum(el)
                for el in child.findall(rf'{{{SRC_NS}}}enum')
            ]

            local_declarations = [*parent_declarations, *class_declarations]
            enums = [*enums, *class_enums]

            function_dict = {**function_dict,
            **get_functions_with_metric_properties(
            root_element = child,
            all_local_call_names = all_local_call_names,
            parent_struct_name = new_parent_name_txt,
            parent_struct_type = new_parent_struct_type,
            parent_declarations = local_declarations,
            file_name = file_name,
            local_function_names=[f["function_name"] for f in function_dict.values()],
            enums = enums,
            language = language)}

        if re.search(rf"{{{SRC_NS}}}block|block_content", child.tag):
            function_dict = {**function_dict,
            **get_functions_with_metric_properties(
            root_element = child,
            all_local_call_names = all_local_call_names,
            parent_struct_name = parent_name_txt,
            parent_struct_type = parent_struct_type,
            parent_declarations = local_declarations,
            file_name = file_name,
            local_function_names=[f["function_name"] for f in function_dict.values()],
            enums = enums,
            language = language)}

        if re.search(rf"{{{SRC_NS}}}function|constructor", child.tag):
            updated_function_dict = get_function_global_var_ops_and_paths(
                function_element = child,
                function_dict = function_dict,
                all_local_call_names = all_local_call_names,
                parent_struct_name = parent_name_txt,
                parent_struct_type = parent_struct_type,
                parent_declarations = parent_declarations,
                file_name = file_name,
                local_function_names=[f["function_name"] for f in function_dict.values()],
                enums = enums,
                language = language)

            function_dict = {**function_dict, **updated_function_dict}

    return function_dict

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

    def get_functions_with_properties(self, file_name, contents):
        srcml = _get_srcml(contents, self._language)

        if srcml is None:
            logger.debug('Srcml parser is none')
            return "None"
        else:
            logger.debug('Successfully retrieved srcml parser')

        root = ElementTree.fromstring(srcml)

        root_declarations = [
            _parse_declaration(
                element = decl,
                parent_struct_name=file_name,
                parent_struct_type='file',
                belongs_to_file='file_name')
            for decl in root.findall(rf'{{{SRC_NS}}}decl_stmt')]

        root_enums = [
            _parse_enum(el)
            for el in root.findall(rf'{{{SRC_NS}}}enum')
        ]

        func_dict = get_functions_with_metric_properties(
            root_element = root,
            parent_struct_name = file_name,
            parent_struct_type= 'file',
            parent_declarations=root_declarations,
            all_local_call_names=[],
            local_function_names=[],
            language=self._language,
            enums = root_enums,
            file_name = file_name)

        return func_dict

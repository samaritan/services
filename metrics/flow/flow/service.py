import logging
import operator

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Flow
from .schemas import FlowSchema, ChangeSchema

import re

logger = logging.getLogger(__name__)
METRICS = ['CountInput', 'CountOutput', 'CountPath']
SRC_NS = 'http://www.srcML.org/srcML/src'


def _count_fan_in(global_variable_reads):
    return len(global_variable_reads)

def _count_fan_out(variable_writes):
    fan_out = 0

    for key in list(variable_writes):
        if len(variable_writes[key]['expressions']) > 0:
            fan_out += 1

        members_modded = list(
            set(
                [m for m in variable_writes[key]['members_modified'] if m.rstrip() != '']))

        indicies_modded = list(
            set(
                [i for i in variable_writes[key]['indices_modified'] if i.rstrip() != '']))

        fan_out += len(members_modded) + len(indicies_modded)

    return fan_out

def _count_npath_from_acyc_paths(acyc_paths, depth = 0):
    npath = 0
    pos = 0

    while pos < len(acyc_paths):
        path = acyc_paths[pos]

        if isinstance(path, dict):
            next_path = acyc_paths[pos + 1] if pos + 1 < len(acyc_paths) else {}
            next_path_type = next_path["type"] if "type" in next_path.keys() else ""

            previous_path = acyc_paths[pos - 1] if pos - 1 > 0 else {}
            previous_path_type = previous_path["type"] if "type" in previous_path.keys() else ""

            p_children = path["children"] if "children" in path.keys() else []
            p_type = path["type"] if "type" in path.keys() else ""

            npath_child = _count_npath_from_acyc_paths(acyc_paths = p_children, depth = depth + 1)

            if re.fullmatch(rf"{{{SRC_NS}}}if", p_type):# == "if_stmt":
                p_if_type = path["if_type"] if "if_type" in path.keys() else ""
                next_if_type = next_path["if_type"] if "if_type" in next_path.keys() else ""

                if p_if_type != 'elseif':
                    if (next_if_type == 'elseif' or
                        re.fullmatch(rf'{{{SRC_NS}}}else', next_path_type)):
                            npath += 1 + npath_child
                    elif re.fullmatch(rf'{{{SRC_NS}}}if|switch|loop', previous_path_type):
                        if npath_child == 0:
                            npath = npath + 2 if npath == 0 else npath * 2
                        else:
                            npath = (
                                npath + (2 * npath_child)
                                if npath == 0
                                else npath * 2 * npath_child)
                    else:
                        npath = npath + 2 * npath_child if npath_child > 0 else npath + 2
                else:
                    npath += 1 + npath_child

            elif re.fullmatch(rf"{{{SRC_NS}}}(for|while|do)", p_type):
                if re.fullmatch(
                    r'^if|elseif|else|loop|switch$',
                    previous_path_type):
                    npath = npath * (1 + npath_child) if npath_child > 0 else npath * 2
                else:
                    npath = npath + 1 + npath_child if npath_child > 0 else npath + 2

            elif re.fullmatch(rf"{{{SRC_NS}}}else", p_type):
                npath += 1 + npath_child
            elif re.fullmatch(rf"{{{SRC_NS}}}switch", p_type):
                npath += 1 + npath_child
            elif re.fullmatch(rf"{{{SRC_NS}}}case", p_type):
                npath += 1 + npath_child
            elif re.fullmatch(rf"{{{SRC_NS}}}default", p_type):
                npath += npath_child
        pos += 1

    if npath == 0 and depth == 0:
        npath = 1

    return npath

class FlowService:
    name = 'flow'

    config = Config()
    parser_rpc = RpcProxy('parser')
    repo_rpc = RpcProxy('repository')

    @rpc
    def metrics_from_contents(self, file_name, contents):
        functions = self.parser_rpc.get_functions_with_properties(file_name, contents)

        ninput = 0
        noutput = 0
        npath = 0

        if functions is not None:
            for function in functions:
                func_ninput = 0
                func_noutput = 0
                func_npath = 0

                func_npath = _count_npath_from_acyc_paths(
                    function["acyclical_paths_tree"],
                    depth = 0
                )

                func_ninput = (
                    func_ninput +
                    _count_fan_in(function["global_variable_reads"]) +
                    len(function["functions_called_by"])
                )

                func_noutput += _count_fan_out(
                    function["global_variable_writes"]
                )

                logger.debug(function["file_name"])
                logger.debug(function["signature"])
                logger.debug(" fanin: " + str(func_ninput))
                logger.debug("fanout: " + str(func_noutput))
                logger.debug(" npath: " + str(func_npath))
                logger.debug('-'*30)

                func_noutput += 1 if function["has_return"] else 0

                ninput += func_ninput
                noutput += func_noutput
                npath += func_npath

        return {
            'ninput': ninput,
            'noutput': noutput,
            'npath': npath
        }

    @rpc
    def collect(self, project, sha, **options):
        flow_metrics = []
        changes = self.repo_rpc.get_changes(project = project, sha = sha)

        logger.debug("Displaying contents")
        for change in changes:
            file_name = change["path"].split('/')[-1]
            oids = change["oids"]
            oid_after = oids["after"]
            contents = self.repo_rpc.get_content(project, oid_after)

            metrics = self.metrics_from_contents(
                file_name = file_name,
                contents = contents
            )

            change_obj = ChangeSchema(many = False).dump({
                            'path': change["path"],
                            'type': change["type"],
                            'oids': oids
                        })

            flow_metrics.append({
                'change': change_obj,
                **metrics
            })

        if len(flow_metrics) > 0:
            return FlowSchema(many=True).dump(flow_metrics)

        return None

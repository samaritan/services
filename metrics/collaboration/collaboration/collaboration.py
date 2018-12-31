import itertools
import logging

import graph_tool

from graph_tool.centrality import betweenness

from .library import pathwhitelister
from .models import Collaboration

logger = logging.getLogger(__name__)


def _aggregate_centrality(centralities):
    _centralities = list()
    for (file, centrality) in centralities.items():
        _centralities.append(Collaboration(
            path=file,
            collaboration=max(centrality) if centrality else 0.0
        ))
    return _centralities


def _get_edge_centrality(graph):
    _, centrality = betweenness(graph, norm=False)
    return centrality


def _get_whitelister(**options):
    names, extensions = None, None

    whitelist = options.get('whitelist', None)
    if whitelist is not None:
        names = whitelist.get('names', None)
        extensions = whitelist.get('extensions', None)
    return pathwhitelister.PathWhitelister(names, extensions)


def _transform(graph, centralities):
    _centralities = dict()

    for edge in graph.edges():
        centrality = centralities[edge]
        for file in graph.ep.files[edge]:
            if file not in _centralities:
                _centralities[file] = list()
            _centralities[file].append(centrality)

    return _centralities


def get_collaboration(changes, processes, **options):
    graph_tool.openmp_set_num_threads(processes)
    whitelister = _get_whitelister(**options)

    collaboration = None

    files = dict()
    for change in changes:
        for _change in change.changes:
            if whitelister.is_valid(_change.path):
                if _change.path not in files:
                    files[_change.path] = set()
                files[_change.path].add(change.commit.author)

    graph = graph_tool.Graph(directed=False)

    graph.vp.label = graph.new_vertex_property('object')
    graph.ep.files = graph.new_edge_property('object')

    nodes, edges = dict(), dict()
    for (file, developers) in files.items():
        for (src, dst) in itertools.combinations(developers, 2):
            snode = nodes.get(src, None)
            if snode is None:
                snode = graph.add_vertex()
                nodes[src] = snode

            dnode = nodes.get(dst, None)
            if dnode is None:
                dnode = graph.add_vertex()
                nodes[dst] = dnode

            edge = edges.get(
                (snode, dnode), edges.get((dnode, snode), None)
            )
            if edge is None:
                edge = graph.add_edge(snode, dnode)
                edges[(snode, dnode)] = edge
                graph.ep.files[edge] = {file}
            else:
                graph.ep.files[edge].add(file)

    logger.debug('# Nodes: %s', graph.num_vertices())
    logger.debug('# Edges: %s', graph.num_edges())

    centrality = _get_edge_centrality(graph)
    collaboration = _aggregate_centrality(_transform(graph, centrality))

    return collaboration

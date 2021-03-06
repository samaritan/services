import logging
import os

import graph_tool
from graph_tool.centrality import betweenness

from .library import pathwhitelister

logger = logging.getLogger(__name__)


def _get_vertex_centrality(graph):
    centrality, _ = betweenness(graph, weight=graph.ep.weight, norm=False)
    return centrality


def _prune_graph(graph, options):
    logger.debug('Prune graph')

    whitelist = options.get('whitelist', None)
    if whitelist is None:
        return graph

    names = whitelist.get('names', None)
    extensions = whitelist.get('extensions', None)
    whitelister = pathwhitelister.PathWhitelister(names, extensions)

    include = graph.new_vertex_property('bool')
    for vertex in graph.vertices():
        include[vertex] = True
        if graph.vp.bipartite[vertex]:
            include[vertex] = whitelister.is_valid(graph.vp.label[vertex])

    graph.set_vertex_filter(include)
    graph.purge_vertices()
    graph.clear_filters()

    return graph


def get_contribution(changes, **options):
    graph_tool.openmp_set_num_threads(os.cpu_count())

    contribution = None

    graph = graph_tool.Graph(directed=False)

    graph.vp.label = graph.new_vertex_property('object')
    graph.vp.bipartite = graph.new_vertex_property('bool')
    graph.ep.weight = graph.new_edge_property('int')

    nodes, edges = dict(), dict()
    for (commit, _changes) in changes:
        developer = nodes.get(commit.author, None)
        if developer is None:
            developer = graph.add_vertex()
            nodes[commit.author] = developer

            graph.vp.bipartite[developer] = False
            graph.vp.label[developer] = commit.author

        for change in _changes:
            path = nodes.get(change.path, None)
            if path is None:
                path = graph.add_vertex()
                nodes[change.path] = path

                graph.vp.bipartite[path] = True
                graph.vp.label[path] = change.path

            edge = edges.get((developer, path), None)
            if edge is None:
                edge = graph.add_edge(developer, path)
                edges[(developer, path)] = edge
                graph.ep.weight[edge] = 1
            else:
                graph.ep.weight[edge] += 1
    nodes.clear()
    edges.clear()

    logger.debug('# Nodes: %s', graph.num_vertices())
    logger.debug('# Edges: %s', graph.num_edges())
    _prune_graph(graph, options)
    logger.debug('# Nodes: %s', graph.num_vertices())
    logger.debug('# Edges: %s', graph.num_edges())

    centrality = _get_vertex_centrality(graph)

    # Filter developer vertices from the graph
    graph.set_vertex_filter(graph.vp.bipartite)
    contribution = {graph.vp.label[v]: centrality[v] for v in graph.vertices()}
    graph.clear_filters()

    return contribution

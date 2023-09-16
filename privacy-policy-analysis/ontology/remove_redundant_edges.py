#!/usr/bin/env python3

import sys
import networkx as nx

graph = nx.read_gml(sys.argv[1])
to_remove = set()

for u, v in graph.edges():
    for path in nx.all_simple_paths(graph, u, v):
        if tuple(path) != (u, v):
            break
    else:
        continue

    print("Redundant edge:", u, "->", v)
    to_remove.add((u, v))

for u, v in to_remove:
    graph.remove_edge(u, v)

nx.write_gml(graph, sys.argv[1])

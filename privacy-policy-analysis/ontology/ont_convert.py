#!/usr/bin/env python3

import argparse
import os

import networkx as nx

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')
args = parser.parse_args()

_, input_ext = os.path.splitext(args.input)
_, output_ext = os.path.splitext(args.output)

if input_ext == '.pickle':
    ont = nx.read_gpickle(args.input)
elif input_ext == '.gml':
    ont = nx.read_gml(args.input)

for _, attr in ont.nodes(data=True):
    attr.clear()

for _, _, attr in ont.edges(data=True):
    attr.clear()

if output_ext == '.pickle':
    nx.write_gpickle(ont, args.output, 2)
elif output_ext == '.gml':
    nx.write_gml(ont, args.output)

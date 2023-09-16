#!/usr/bin/env python3

from collections import defaultdict
import logging
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import networkx as nx
import yaml

ont_root = Path(sys.argv[1])
tree = ET.parse(ont_root / 'synonyms.xml')
root = tree.getroot()

ont_entity = nx.read_gml(ont_root / "entity_ontology.gml")
ont_data = nx.read_gml(ont_root / "data_ontology.gml")

entity_map = defaultdict(set)
domain_map = defaultdict(set)
data_map = defaultdict(set)

for node in root:
    if node.tag != 'node':
        raise RuntimeError("Unknown tag: %s" % node.tag)

    term = node.get('term')
    is_entity = term in ont_entity
    is_data = term in ont_data

    if is_entity and is_data:
        logging.warning(f"{term} is both an entity and a data type!")

    if not is_entity and not is_data:
        logging.warning(f"{term} does not exist in the ontology!")

    for child in node:
        synonym = child.get('term')

        if synonym == term:
            continue

        if is_entity:
            if synonym and ' ' not in synonym and '.' in synonym:
                domain_map[term].add(synonym)
            else:
                entity_map[term].add(synonym)

        if is_data:
            data_map[term].add(synonym)

for k, v in entity_map.items():
    for term in v:
        if term in entity_map:
            logging.error(f"{term} is both a node and a synonym in entity_map")

for k, v in data_map.items():
    for term in v:
        if term in data_map:
            logging.error(f"{term} is both a node and a synonym in data_map")

with open(ont_root / 'domains.yml', 'w') as fout:
    yaml.safe_dump({k: sorted(v) for k, v in domain_map.items()}, fout)

with open(ont_root / 'entity_synonyms.yml', 'w') as fout:
    yaml.safe_dump({k: sorted(v) for k, v in entity_map.items()}, fout)

with open(ont_root / 'data_synonyms.yml', 'w') as fout:
    yaml.safe_dump({k: sorted(v) for k, v in data_map.items()}, fout)

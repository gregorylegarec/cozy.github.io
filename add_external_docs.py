"""
Adds table of contents of each external documentation to the
References menu
"""

import yaml
import json
import os
import sys
import re
import os.path as osp
from collections import OrderedDict

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


leadingHash = re.compile('#+\s+')

def read_toc(directory):
    toc_path = osp.join('src', directory, 'toc.yml')
    if not osp.exists(toc_path):
        return
    else:
        def make_paths_absolute(tree):
            for t in tree:
                for k in t.iterkeys():
                    if isinstance(t[k], str):
                        t[k] = re.sub('^.', directory, t[k])
                    else:
                        make_paths_absolute(t[k])
        with open(toc_path) as f:
            toc = ordered_load(f)
            make_paths_absolute(toc)
            return toc

def find_entry(tree, name):
    return [p for p in tree if p.get(name)][0][name]

def main():
    with open('./mkdocs.yml') as f:
        data = ordered_load(f, yaml.SafeLoader)

    with open('OUTSIDE_DOCS') as f:
        outside_docs_conf = [l.strip().split(' ') for l in f.readlines()]


    outside_docs_conf = [
        {'name': c[0], 'repo': c[1], 'subdir': c[2]}
        for c in outside_docs_conf
    ]
    outside_doc_names = [c['name'] for c in outside_docs_conf] 

    develop = find_entry(data['pages'], 'Develop')
    references = find_entry(develop, 'References')

    del references[:]

    for dir in outside_doc_names:
        abs = osp.join('./src', dir)
        toc = read_toc(dir)
        if toc:
            references.append({ dir: toc })

    data['extra'] = {"outside_docs": outside_docs_conf}
    with open('mkdocs.yml', 'w+') as f:
        ordered_dump(data, f, indent=2, default_flow_style=False, Dumper=yaml.SafeDumper)

main()

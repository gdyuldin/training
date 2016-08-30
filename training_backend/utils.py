import yaml
import os

import dpath.util


def patch_config(data):
    for key, val in dpath.util.search(data, '**', yielded=True, separator='_'):
        dpath.util.set(data,
                       key,
                       os.environ.get(key.upper(), val),
                       separator='_')


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f)
    patch_config(data)
    return data
